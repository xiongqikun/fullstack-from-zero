"""Console output, prompts, colours and CJK-aware text helpers.

Nothing here knows about lessons or state.  One ``Console`` object is created
per run and handed around; tests create one with string streams and a scripted
reader.
"""

import contextlib
import io
import re
import sys
import unicodedata
import warnings

from .errors import Cancelled, UsageProblem
from .normalize import normalize

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
OK_MARK = "✅"
BAD_MARK = "❌"
WARN_MARK = "⚠️"

TEXT = {
    "cancelled": "已取消，没有记录任何东西。需要时重新运行同一条命令就行。",
    "no_prompt": "现在是不提问模式（COURSE_NONINTERACTIVE=1），这一步需要你输入内容。",
    "yes_no": "（输入 y 表示是，直接回车表示否）",
    "tutor_box_head": "发给导师（从这一行开始复制）",
    "tutor_box_tail": "到这一行结束",
}

_ANSI = {
    "ok": "\033[32m",
    "bad": "\033[31m",
    "warn": "\033[33m",
    "dim": "\033[2m",
    "bold": "\033[1m",
}
_RESET = "\033[0m"


def wants_color(stream, env):
    """Colour only on a terminal, and never when NO_COLOR is set.

    NO_COLOR follows https://no-color.org: present and not empty switches
    colour off, whatever its value.  ``TERM=dumb`` also switches it off.
    """
    if env.get("NO_COLOR"):
        return False
    if env.get("TERM") == "dumb":
        return False
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False


def _is_tty(stream):
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False


class Console:
    """Where the tool writes and how it asks.

    ``can_prompt`` is False in non-interactive mode (COURSE_NONINTERACTIVE=1):
    the tool then never waits for input.  ``is_tty`` says whether a person is
    sitting at the keyboard; optional questions (a confidence rating, a
    confirmation) are asked only then.
    """

    def __init__(self, out=None, err=None, reader=None, color=False,
                 can_prompt=True, is_tty=None, stdin=None):
        self._out = out if out is not None else sys.stdout
        self._err = err if err is not None else sys.stderr
        self._stdin = stdin
        self._reader = reader
        self.color = bool(color)
        self.can_prompt = bool(can_prompt)
        if is_tty is None:
            is_tty = _is_tty(stdin if stdin is not None else sys.stdin)
        self.is_tty = bool(is_tty)

    @classmethod
    def from_env(cls, env):
        """The console of a real run: standard streams, settings from ``env``."""
        for stream in (sys.stdout, sys.stderr, sys.stdin):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, io.UnsupportedOperation):
                pass
        can_prompt = env.get("COURSE_NONINTERACTIVE", "") in ("", "0")
        return cls(out=sys.stdout, err=sys.stderr, stdin=sys.stdin,
                   color=wants_color(sys.stdout, env), can_prompt=can_prompt)

    # -- output -------------------------------------------------------------
    def out(self, text=""):
        """Write ``text`` and a newline to standard output."""
        self._out.write(str(text) + "\n")

    def err(self, text=""):
        """Write ``text`` and a newline to standard error."""
        self._err.write(str(text) + "\n")

    def flush(self):
        for stream in (self._out, self._err):
            try:
                stream.flush()
            except (AttributeError, ValueError, OSError):
                pass

    def paint(self, text, kind):
        """Wrap ``text`` in a colour (ok, bad, warn, dim, bold) when allowed."""
        if not self.color or kind not in _ANSI:
            return text
        return _ANSI[kind] + text + _RESET

    # -- input --------------------------------------------------------------
    @property
    def may_ask_optional(self):
        """True when optional questions are welcome (a person at a terminal)."""
        return self.can_prompt and self.is_tty

    def read(self, prompt):
        """Show ``prompt`` and return one line typed by the learner.

        Raises ``Cancelled`` on end-of-file or Ctrl+C, and ``UsageProblem`` in
        non-interactive mode.  Never returns the trailing newline.
        """
        if not self.can_prompt:
            raise UsageProblem(TEXT["no_prompt"])
        try:
            if self._reader is not None:
                line = self._reader(prompt)
                if line is None:
                    raise EOFError()
            else:
                self._out.write(prompt)
                self._out.flush()
                stdin = self._stdin if self._stdin is not None else sys.stdin
                line = stdin.readline()
                if line == "":
                    raise EOFError()
        except (EOFError, KeyboardInterrupt):
            self._out.write("\n")
            raise Cancelled()
        return line.rstrip("\r\n")

    def confirm(self, prompt):
        """Ask a yes/no question; only an explicit yes returns True."""
        answer = normalize(self.read(prompt + " " + TEXT["yes_no"] + " "))
        return answer in ("y", "yes", "是", "是的", "好", "好的")


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def display_width(text):
    """Number of terminal cells ``text`` occupies (CJK characters count 2)."""
    width = 0
    for ch in text:
        if unicodedata.combining(ch) or ch in ("️", "‍"):
            continue
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def pad(text, width):
    """Pad ``text`` with spaces on the right up to ``width`` cells."""
    return text + " " * max(0, width - display_width(text))


def indent(text, spaces=2):
    """Indent every non-empty line of ``text``."""
    prefix = " " * spaces
    return "\n".join((prefix + line) if line.strip() else line
                     for line in str(text).split("\n"))


def bullets(items, spaces=4, mark="- "):
    """Format ``items`` as an indented bullet list; continuation lines align."""
    lines = []
    prefix = " " * spaces
    for item in items:
        parts = str(item).split("\n")
        lines.append(prefix + mark + parts[0])
        for extra in parts[1:]:
            lines.append(prefix + " " * len(mark) + extra)
    return "\n".join(lines)


def tutor_box(lines):
    """A block the learner can copy to the tutor in one piece."""
    body = ["  │ " + line for line in lines]
    return "\n".join(["  ┌ " + TEXT["tutor_box_head"]] + body
                     + ["  └ " + TEXT["tutor_box_tail"]])


#: The white space that ``one_line`` collapses: ASCII spaces, tabs and line
#: breaks only.  The ideographic space (U+3000) and the non-breaking space
#: (U+00A0) are kept, because evidence may quote them.
_ASCII_SPACE = re.compile("[ \t\r\n\f\v]+")
_ASCII_SPACE_CHARS = " \t\r\n\f\v"


def one_line(text, limit=0):
    """Collapse runs of ASCII spaces, tabs and line breaks into single spaces.

    Other white space, such as the ideographic space U+3000 typed by a
    Chinese input method, is kept as it is: a message that quotes the
    learner's text must show exactly what was there (use ``visible`` to make
    it readable).
    """
    flat = _ASCII_SPACE.sub(" ", str(text)).strip(_ASCII_SPACE_CHARS)
    if limit and len(flat) > limit:
        flat = flat[: limit - 1] + "…"
    return flat


#: Characters that ``visible`` names, because a reader cannot see them.
VISIBLE_NAMES = {
    "　": "〔全角空格〕",
    "\t": "〔Tab〕",
    " ": "〔不换行空格〕",
}
TRAILING_SPACE_MARK = "·"


def visible(text):
    """Make invisible characters visible, for evidence lines that quote text.

    The ideographic space U+3000 becomes 〔全角空格〕, a tab 〔Tab〕, a
    non-breaking space 〔不换行空格〕, and every ASCII space at the end of a
    line becomes one ·.  Everything else is kept as it is.
    """
    lines = []
    for line in str(text).split("\n"):
        ending = ""
        if line.endswith("\r"):
            line, ending = line[:-1], "\r"
        body = line.rstrip(" ")
        trailing = len(line) - len(body)
        lines.append("".join(VISIBLE_NAMES.get(ch, ch) for ch in body)
                     + TRAILING_SPACE_MARK * trailing + ending)
    return "\n".join(lines)


@contextlib.contextmanager
def captured(sink):
    """Run lesson code with everything it prints kept in ``sink``.

    Standard output, standard error and Python warnings all go to ``sink``
    (a ``StringIO``), so nothing a check or builder prints reaches the
    learner's terminal unfiltered.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                yield sink
        finally:
            for item in caught:
                sink.write(f"{item.category.__name__}: {item.message}\n")
