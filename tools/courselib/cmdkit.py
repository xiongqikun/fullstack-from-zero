"""Helpers for command plug-ins (``courselib/commands/<name>.py``).

A plug-in module exposes two functions::

    def register(subparsers):   # add the command's parser
    def run(args) -> int:       # do the work; args.app is the App of this run

``add_command`` creates a parser whose help, usage line and error messages are
Chinese.  ``clean_id`` and ``find_target`` turn what a learner typed into a
lesson or station.  See docs/authoring/command-plugins.md.
"""

import argparse
import re

from .catalog import LESSON_ID, STATION_ID
from .errors import ToolTrouble, UsageProblem
from .normalize import normalize

PROG = "python3 tools/course.py"

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "usage_prefix": "用法：",
    "arguments": "参数",
    "options": "选项",
    "help_help": "显示这份说明",
    "see_help": "看这个命令的说明：{prog} -h",
    "joined_id": "编号中间不要有空格。你是不是想写：{prog} {joined}",
    "err_required": "缺少必须的参数：{what}",
    # A word that starts with "-" is a 选项 (option), as the lessons call it
    # from 0.2 on; every other word after the command is a 参数 (argument).
    "err_unknown": "不认识的参数：{what}",
    "err_unknown_option": "不认识的选项：{what}",
    "err_unknown_both": "不认识的选项：{options}；不认识的参数：{words}",
    "err_expected_one": "{kind} {name} 后面要跟一个值",
    "err_choice": "{kind} {name} 不能是 {value}（可以用的值：{choices}）",
    "err_int": "{kind} {name} 要是一个整数，现在是 {value}",
    "kind_option": "选项",
    "kind_argument": "参数",
    "err_command": "没有 {value} 这个命令。可以用的命令：{choices}",
    "err_other": "命令的写法有问题（{message}）",
    "bad_target": "看不懂「{text}」。站点编号像 1.6a，课程编号像 1.6。",
    "unknown_station": "没有 {station} 这一站。{lesson} 课的站点是：{stations}",
    "unknown_lesson": "没有 {lesson} 这一课。运行 python3 tools/course.py status 看看你现在在哪一课。",
    "need_station": "这里要写站点编号（像 1.6a），不是课程编号。{lesson} 课的站点是：{stations}",
    "broken_lesson": "{lesson} 课的课程模块加载失败，暂时用不了。",
}

_ERROR_PATTERNS = (
    (re.compile(r"^the following arguments are required: (.+)$"),
     lambda m: TEXT["err_required"].format(what=m.group(1))),
    (re.compile(r"^unrecognized arguments: (.+)$"),
     lambda m: unknown_words(m.group(1).split(" "))),
    (re.compile(r"^argument (.+?): expected one argument$"),
     lambda m: TEXT["err_expected_one"].format(kind=word_kind(m.group(1)), name=m.group(1))),
    (re.compile(r"^argument <命令>: invalid choice: '?(.+?)'? \(choose from (.+)\)$"),
     lambda m: TEXT["err_command"].format(value=m.group(1), choices=_plain(m.group(2)))),
    (re.compile(r"^argument (.+?): invalid choice: '?(.+?)'? \(choose from (.+)\)$"),
     lambda m: TEXT["err_choice"].format(kind=word_kind(m.group(1)), name=m.group(1),
                                         value=m.group(2), choices=_plain(m.group(3)))),
    (re.compile(r"^argument (.+?): invalid int value: '?(.+?)'?$"),
     lambda m: TEXT["err_int"].format(kind=word_kind(m.group(1)), name=m.group(1),
                                      value=m.group(2))),
)


def word_kind(word):
    """选项 for a word that starts with a hyphen (``--write``, ``-h``), else 参数."""
    return TEXT["kind_option"] if str(word).startswith("-") else TEXT["kind_argument"]


def unknown_words(words):
    """The sentence for words a command does not take.

    ``--wirte`` -> 「不认识的选项：--wirte」; ``1.6`` -> 「不认识的参数：1.6」;
    both kinds -> 「不认识的选项：--wirte；不认识的参数：1.6」.
    """
    words = [word for word in words if word != ""]
    options = [word for word in words if word.startswith("-")]
    others = [word for word in words if not word.startswith("-")]
    if options and others:
        return TEXT["err_unknown_both"].format(options=" ".join(options), words=" ".join(others))
    if options:
        return TEXT["err_unknown_option"].format(what=" ".join(options))
    return TEXT["err_unknown"].format(what=" ".join(others))


def _plain(choices):
    return "、".join(part.strip().strip("'") for part in choices.split(","))


def translate_error(message):
    """A Chinese sentence for an argparse error message."""
    for pattern, render in _ERROR_PATTERNS:
        match = pattern.match(message)
        if match:
            return render(match)
    return TEXT["err_other"].format(message=message)


class HelpRequested(Exception):
    """Raised by ``-h``; carries the help text.  ``cli.main`` prints it and exits 0."""

    def __init__(self, text):
        Exception.__init__(self, text)
        self.text = text


class _HelpAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS,
                 help=None):
        argparse.Action.__init__(self, option_strings=option_strings, dest=dest,
                                 default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        raise HelpRequested(parser.format_help())


class ZhFormatter(argparse.RawDescriptionHelpFormatter):
    """Help layout that works with Chinese text: each option on its own line."""

    def __init__(self, prog, **kwargs):
        kwargs.setdefault("max_help_position", 4)
        kwargs.setdefault("width", 100)
        argparse.RawDescriptionHelpFormatter.__init__(self, prog, **kwargs)

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = TEXT["usage_prefix"]
        return argparse.RawDescriptionHelpFormatter.add_usage(self, usage, actions, groups, prefix)

    def format_help(self):
        text = argparse.RawDescriptionHelpFormatter.format_help(self)
        for title in (TEXT["arguments"], TEXT["options"]):
            text = text.replace(title + ":", title + "：")
        return text


class ZhParser(argparse.ArgumentParser):
    """An argument parser that speaks Chinese and never exits by itself.

    A usage error raises ``UsageProblem`` (exit code 64, plan I4) and ``-h``
    raises ``HelpRequested``; ``cli.main`` handles both.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("add_help", False)
        kwargs.setdefault("formatter_class", ZhFormatter)
        kwargs.setdefault("allow_abbrev", False)
        self.summary = kwargs.pop("summary", "")
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self._positionals.title = TEXT["arguments"]
        self._optionals.title = TEXT["options"]
        self.add_argument("-h", "--help", action=_HelpAction, help=TEXT["help_help"])

    def error(self, message):
        raise UsageProblem(translate_error(message),
                           suggestion=TEXT["see_help"].format(prog=self.prog))


def add_command(subparsers, name, summary, description="", epilog=""):
    """Add the parser of command ``name`` and return it.

    ``summary`` is the one line shown in the list of commands; ``description``
    and ``epilog`` appear in ``<command> -h`` exactly as written.
    """
    return subparsers.add_parser(name, help=summary, summary=summary,
                                 description=description or summary, epilog=epilog or None)


# ---------------------------------------------------------------------------
# Lesson and station ids typed by a learner
# ---------------------------------------------------------------------------
#: What a Chinese input method types instead of "." inside an id.
_ID_DOTS = {"。": ".", "｡": ".", "，": ".", ",": ".", "、": "."}


#: Punctuation an input method leaves after an id: 「check 1.1a，」「check 1.1a。」.
_ID_TRAILING = "。｡，,、．.；;：:！!？? \t\u3000"


def clean_id(text):
    """Normalise a typed id: "１.６Ａ " -> "1.6a", "1。6a" -> "1.6a", "1.1a，" -> "1.1a"."""
    raw = str(text).strip().rstrip(_ID_TRAILING)
    raw = "".join(_ID_DOTS.get(ch, ch) for ch in raw)
    return normalize(raw).replace(" ", "")


def find_target(app, text, want="any"):
    """Resolve what the learner typed to ``(lesson, station_or_None)``.

    ``want`` is "any" (a lesson or a station), "station" or "lesson".
    Raises ``UsageProblem`` for something that does not exist and
    ``ToolTrouble`` when the lesson module is broken.
    """
    target = clean_id(text)
    catalog = app.catalog()
    station_match = STATION_ID.match(target)
    if station_match and want != "lesson":
        lesson, station = catalog.station(target)
        if lesson is not None:
            return lesson, station
        lesson_id = station_match.group(1)
        _raise_if_broken(catalog, lesson_id)
        lesson = catalog.lesson(lesson_id)
        if lesson is None:
            raise UsageProblem(TEXT["unknown_lesson"].format(lesson=lesson_id))
        raise UsageProblem(TEXT["unknown_station"].format(
            station=target, lesson=lesson_id, stations=" ".join(lesson.station_ids)))
    if LESSON_ID.match(target):
        _raise_if_broken(catalog, target)
        lesson = catalog.lesson(target)
        if lesson is None:
            raise UsageProblem(TEXT["unknown_lesson"].format(lesson=target))
        if want == "station":
            raise UsageProblem(TEXT["need_station"].format(
                lesson=target, stations=" ".join(lesson.station_ids)))
        return lesson, None
    raise UsageProblem(TEXT["bad_target"].format(text=str(text).strip()))


def _raise_if_broken(catalog, lesson_id):
    broken = catalog.broken_for(lesson_id)
    if broken is not None:
        raise ToolTrouble(TEXT["broken_lesson"].format(lesson=lesson_id),
                          detail=broken.error + "\n" + broken.error_detail,
                          where=broken.rel + "/lesson.py")
