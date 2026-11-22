"""Argument parsing, plug-in discovery and top-level error handling.

``main`` is the single entry point.  It builds the ``App``, discovers the
command plug-ins in ``courselib/commands``, parses the arguments and runs the
chosen command.  Whatever happens, it returns an exit code of plan I4 and
never lets a traceback reach the learner:

- 0 ok, 1 not yet / refused / cancelled, 2 checker problem, 64 usage error.

A plug-in that fails to import does not take the other commands down: its name
stays in the list and reports the failure when it is called.
"""

import importlib
import pkgutil
import sys
import traceback

from . import API_VERSION, __version__, cmdkit
from .app import App
from .catalog import LESSON_ID, describe_exception
from .errors import (
    EXIT_NOT_YET,
    EXIT_OK,
    EXIT_PROBLEM,
    EXIT_USAGE,
    Cancelled,
    Refused,
    ToolTrouble,
    UsageProblem,
)
from .normalize import to_halfwidth
from .runner import render_problem
from .ui import TEXT as UI_TEXT
from .ui import Console, visible

#: Order of the commands in the help; others follow alphabetically.
PREFERRED = ("status", "check", "hint", "scenario", "review", "exam", "journal",
             "doctor", "fresh", "validate")

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "usage": "用法：{prog} <命令> [参数]",
    "intro": "不带命令运行，会显示你现在学到哪了、下一步做什么。",
    "commands": "命令：",
    "more": "每个命令的详细用法：{prog} <命令> -h",
    "version": "course.py {version}（课程模块接口第 {api} 版，Python {python}）",
    "version_help": "显示工具的版本",
    "usage_error": "用法不对：{message}",
    "stopped": "已停止。需要时重新运行同一条命令就行。",
    "plugin_failed_summary": "（加载失败）",
    "plugin_failed": "命令 {name} 的代码加载失败，暂时用不了。其他命令不受影响。",
    "plugin_bad": "命令模块 courselib/commands/{name}.py 没有提供 register 和 run 两个函数。",
    "crash": "工具自己出错了：{what}",
    "heading_tool": "course.py {command}",
    "fullwidth": "命令里混进了全角字符（中文输入法打出来的空格或符号）：{shown}。",
    "fullwidth_chars": "混进来的是：{chars}。",
    "fullwidth_fix": "切回英文输入法，把这一段重新打一遍。",
}

#: Spaces that a Chinese input method (or a copy from a web page) produces.
#: The shell does not split a command line there, so "check　1.14a" reaches
#: the tool as one word.
FOREIGN_SPACES = {"　": "全角空格", " ": "不换行空格", " ": "全角空格",
                  " ": "全角空格", " ": "窄空格", " ": "不换行空格"}
#: Look-alikes of "-" that an input method types (「－」, 「——」, 「–」).
FOREIGN_DASHES = "－—–−"
#: Options whose value is the learner's own free text (answers, journal lines):
#: anything is allowed there.
FREE_TEXT_OPTIONS = ("--answer", "--done", "--stuck", "--next", "--unclear", "--slow")


class _BrokenCommand:
    """Stands in for a plug-in that could not be loaded."""

    def __init__(self, name, summary, detail):
        self.name = name
        self.summary = summary
        self.detail = detail

    def register(self, subparsers):
        import argparse
        parser = cmdkit.add_command(subparsers, self.name, TEXT["plugin_failed_summary"])
        parser.add_argument("rest", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

    def run(self, args):
        raise ToolTrouble(self.summary, detail=self.detail,
                          where=f"tools/courselib/commands/{self.name}.py")


def discover_commands():
    """Import every module of ``courselib.commands``; returns ``[(name, module)]``."""
    from . import commands as package
    names = sorted(info.name for info in pkgutil.iter_modules(package.__path__)
                   if not info.name.startswith("_"))
    ordered = [n for n in PREFERRED if n in names] + [n for n in names if n not in PREFERRED]
    found = []
    for name in ordered:
        try:
            module = importlib.import_module(f"{package.__name__}.{name}")
        except KeyboardInterrupt:
            raise
        except BaseException as exc:  # noqa: BLE001 - one broken plug-in must not stop the rest
            detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            module = _BrokenCommand(name, TEXT["plugin_failed"].format(name=name), detail)
        if not callable(getattr(module, "register", None)) or not callable(getattr(module, "run", None)):
            module = _BrokenCommand(name, TEXT["plugin_bad"].format(name=name), "")
        found.append((name, module))
    return found


class _TopParser(cmdkit.ZhParser):
    """The top-level parser; its help is a plain list of commands."""

    command_parsers = None

    def format_help(self):
        lines = [TEXT["usage"].format(prog=self.prog), "", TEXT["intro"], "", TEXT["commands"]]
        parsers = self.command_parsers or {}
        width = max([len(name) for name in parsers] or [0]) + 2
        for name, parser in parsers.items():
            lines.append("  {}{}".format(name.ljust(width), getattr(parser, "summary", "")))
        lines += ["", TEXT["more"].format(prog=self.prog), ""]
        return "\n".join(lines)


def build_parser(commands):
    """The parser with one sub-parser per command; returns ``(parser, handlers)``."""
    parser = _TopParser(prog=cmdkit.PROG)
    parser.add_argument("-V", "--version", action="store_true", help=TEXT["version_help"])
    subparsers = parser.add_subparsers(dest="command", metavar="<命令>",
                                       parser_class=cmdkit.ZhParser)
    handlers = {}
    for name, module in commands:
        before = set(subparsers.choices)
        try:
            module.register(subparsers)
        except KeyboardInterrupt:
            raise
        except BaseException as exc:  # noqa: BLE001 - one broken plug-in must not stop the rest
            detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            module = _BrokenCommand(name, TEXT["plugin_failed"].format(name=name), detail)
            if name not in subparsers.choices:
                module.register(subparsers)
        added = set(subparsers.choices) - before
        if name not in subparsers.choices:
            module = _BrokenCommand(name, TEXT["plugin_bad"].format(name=name), "")
            module.register(subparsers)
            added = {name}
        for added_name in added | {name}:
            handlers[added_name] = module
    parser.command_parsers = {name: subparsers.choices[name] for name, _ in commands
                                  if name in subparsers.choices}
    return parser, handlers


def _crash_problem(app, exc):
    """The ``problem`` dict for an exception nobody expected."""
    frames = traceback.extract_tb(exc.__traceback__)
    where = ""
    if frames:
        last = frames[-1]
        where = f"{app.rel(last.filename)} 第 {last.lineno or 0} 行"
    return {"summary": TEXT["crash"].format(what=describe_exception(exc)),
            "where": app.scrub(where), "detail": "", "recovery": ""}


def main(argv=None, root=None, env=None, console=None, now=None):
    """Run the tool and return its exit code.

    ``root`` is the workspace root (the parent of the ``tools`` folder);
    ``env``, ``console`` and ``now`` exist so tests can inject them.
    """
    if argv is None:
        argv = sys.argv[1:]
    if root is None:
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent.parent
    fallback = console if console is not None else Console()
    try:
        app = App(root, env=env, console=console, now=now)
    except UsageProblem as exc:
        fallback.err(TEXT["usage_error"].format(message=exc.message))
        return EXIT_USAGE
    console = app.console
    command = ""
    try:
        argv = _trim_options([str(arg) for arg in argv])
        _refuse_glued_tokens(argv)
        parser, handlers = build_parser(discover_commands())
        argv = _fold_command(list(argv), handlers)
        try:
            args, extras = parser.parse_known_args(argv)
            if extras:
                _unknown_arguments(args, extras)
        except UsageProblem:
            _refuse_foreign_characters(argv)
            raise
        if getattr(args, "version", False):
            console.out(TEXT["version"].format(
                version=__version__, api=API_VERSION,
                python=".".join(str(part) for part in sys.version_info[:3])))
            return EXIT_OK
        args.bare = args.command is None
        if args.bare:
            args = parser.parse_args(["status"])
            args.bare = True
        command = args.command
        args.app = app
        code = handlers[command].run(args)
        return int(code) if code is not None else EXIT_OK
    except cmdkit.HelpRequested as exc:
        console.out(exc.text.rstrip("\n"))
        return EXIT_OK
    except UsageProblem as exc:
        console.err(TEXT["usage_error"].format(message=exc.message))
        if exc.suggestion:
            console.err(exc.suggestion)
        return EXIT_USAGE
    except Refused as exc:
        console.out(exc.message)
        return EXIT_NOT_YET
    except Cancelled:
        console.out(UI_TEXT["cancelled"])
        return EXIT_NOT_YET
    except KeyboardInterrupt:
        console.out("")
        console.out(TEXT["stopped"])
        return EXIT_NOT_YET
    except BrokenPipeError:
        return EXIT_OK
    except ToolTrouble as exc:
        problem = {"summary": exc.summary, "where": exc.where, "detail": "",
                   "recovery": exc.recovery}
        _report_problem(app, command, problem, exc)
        return EXIT_PROBLEM
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_PROBLEM
    except Exception as exc:  # noqa: BLE001 - last line of defence: never a traceback
        _report_problem(app, command, _crash_problem(app, exc), exc)
        return EXIT_PROBLEM
    finally:
        console.flush()


def _trim_options(argv):
    """Drop a stray space around an option: ``"--again "`` is ``--again``.

    The values of free-text options (``--answer`` …) are the learner's words
    and stay as typed.
    """
    trimmed, skip = [], False
    for token in argv:
        if skip:
            trimmed.append(token)
            skip = False
            continue
        bare = token.strip(" \t" + "".join(FOREIGN_SPACES))
        if bare != token and (bare[:2] == "--" or (bare[:1] == "-" and bare[1:2].isalpha())):
            token = bare
        trimmed.append(token)
        skip = token in FREE_TEXT_OPTIONS
    return trimmed


def _fold_command(argv, handlers):
    """Accept "Check" or full-width "ｃｈｅｃｋ" for the command name "check"."""
    if argv and not str(argv[0]).startswith("-"):
        folded = to_halfwidth(str(argv[0])).strip().lower()
        if folded in handlers:
            argv[0] = folded
    return argv


def _foreign_characters(token):
    """The full-width and look-alike characters in one command-line word, in order."""
    found = []
    for ch in token:
        if (ch in FOREIGN_SPACES or ch in FOREIGN_DASHES or 0xFF01 <= ord(ch) <= 0xFF5E) \
                and ch not in found:
            found.append(ch)
    return found


def _checked_tokens(argv):
    """The words of ``argv`` that are not the learner's free text."""
    tokens = []
    skip = False
    for token in argv:
        if skip:
            skip = False
            continue
        if token in FREE_TEXT_OPTIONS:
            skip = True
            continue
        if any(token.startswith(option + "=") for option in FREE_TEXT_OPTIONS):
            continue
        tokens.append(token)
    return tokens


def _foreign_problem(token):
    chars = _foreign_characters(token)
    shown = visible(token)
    for ch, name in FOREIGN_SPACES.items():
        shown = shown.replace(ch, "〔" + name + "〕")
    message = TEXT["fullwidth"].format(shown=shown)
    others = [ch for ch in chars if ch not in FOREIGN_SPACES]
    if others:
        message += TEXT["fullwidth_chars"].format(chars="、".join(others[:6]))
    return UsageProblem(message + TEXT["fullwidth_fix"])


def _refuse_glued_tokens(argv):
    """Refuse a word that a full-width space glued together, or a full-width option.

    ``check　1.14a`` (U+3000 between the words) reaches the tool as one word,
    and ``——answer`` is not an option at all; both would end in a usage
    error that names a command or an argument the learner never typed.  A
    full-width space at the very start or end of a word is harmless (ids are
    normalised) and passes.
    """
    for token in _checked_tokens(argv):
        inner = token.strip("".join(FOREIGN_SPACES) + " ")
        if any(ch in FOREIGN_SPACES for ch in inner) or (inner[:1] and inner[0] in FOREIGN_DASHES):
            raise _foreign_problem(token)


def _refuse_foreign_characters(argv):
    """After a usage error: blame full-width characters when there are any."""
    for token in _checked_tokens(argv):
        if _foreign_characters(token):
            raise _foreign_problem(token)


def _unknown_arguments(args, extras):
    """Raise the usage error for arguments the command does not take."""
    command = getattr(args, "command", None)
    prog = cmdkit.PROG + (" " + command if command else "")
    # visible(): a stray space or tab in what was typed shows as · or 〔Tab〕.
    message = cmdkit.unknown_words([visible(extra) for extra in extras])
    target = getattr(args, "target", None) or getattr(args, "station", None)
    if (target and len(extras) == 1 and len(extras[0]) == 1 and extras[0].isalpha()
            and LESSON_ID.match(cmdkit.clean_id(target))):
        # "hint 1.6 a": a space typed inside a station id
        joined = cmdkit.clean_id(target) + extras[0].lower()
        raise UsageProblem(message, suggestion=cmdkit.TEXT["joined_id"].format(
            prog=prog, joined=joined))
    raise UsageProblem(message, suggestion=cmdkit.TEXT["see_help"].format(prog=prog))


def _report_problem(app, command, problem, exc):
    heading = TEXT["heading_tool"].format(command=command) if command else "course.py"
    for line in render_problem(app, heading, problem):
        app.console.out(line)
    if app.debug:
        app.console.err("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        detail = getattr(exc, "detail", "")
        if detail:
            app.console.err(str(detail))
