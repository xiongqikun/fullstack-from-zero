"""The per-run ``App`` object: workspace paths, the clock and the environment.

One ``App`` is created by ``cli.main`` and attached to the parsed arguments as
``args.app``.  There is no module-level state anywhere in the package: a test
creates as many ``App`` objects as it likes, each with its own root, clock and
environment.

Environment variables honoured (plan I4):

- ``HOME``                  the learner's home directory
- ``COURSE_PLAYGROUND``     where practice states are built
                            (default ``~/Developer/playground``)
- ``COURSE_NOW``            an ISO date or date-time used as "now"
- ``COURSE_NONINTERACTIVE`` ``1``: never prompt, read answers from ``--answer``
- ``NO_COLOR``              no ANSI colours
- ``COURSE_DEBUG``          ``1``: builders get a traceback on standard error

Paths are shown as the learner reads them (``App.show``): with ``~`` for the
home folder, and the workspace through ``~/Developer/fullstack-from-zero`` whenever
that path leads to it (the real folder of a learner who moved the course, or
the entrance, a symbolic link, of a learner who kept it where it was:
decision ``workspace_location`` = ``stay-in-sync`` of lesson 0.2c).
"""

import datetime
import os
import re
from pathlib import Path

from .errors import UsageProblem
from .ui import Console

#: The folder name of the learning workspace under ``~/Developer`` (plan G7,
#: COMMON section 6): every lesson writes ``cd ~/Developer/fullstack-from-zero``.
ENTRANCE_NAME = "fullstack-from-zero"

TEXT = {
    "bad_now": "环境变量 COURSE_NOW 的值看不懂：{value}。要写成 2026-11-19 或 2026-11-19T10:30:00 这样。",
}

_NOW_PATTERN = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})"
    r"(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?)?"
    r"(?:[Zz]|[+-]\d{2}:?\d{2})?$"
)


def parse_now(text):
    """Parse COURSE_NOW.  A date alone means midnight; an offset is ignored.

    The tool works in the learner's wall-clock time and never converts
    between time zones.
    """
    match = _NOW_PATTERN.match(str(text).strip())
    if not match:
        raise UsageProblem(TEXT["bad_now"].format(value=text))
    year, month, day, hour, minute, second = match.groups()
    try:
        return datetime.datetime(int(year), int(month), int(day),
                                 int(hour or 0), int(minute or 0), int(second or 0))
    except ValueError:
        raise UsageProblem(TEXT["bad_now"].format(value=text))


def account_home():
    """Home folder of the login account from the user database, or "".

    Inside a simulation home ``HOME`` points elsewhere, but Python's own
    files (and so tracebacks) still live under this folder.
    """
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_dir or ""
    except (ImportError, KeyError, OSError, AttributeError):
        return ""


def _spellings(folders):
    """Each usable folder as given and resolved, without a trailing slash."""
    found = []
    for folder in folders:
        folder = str(folder or "").rstrip("/")
        if not folder:
            continue
        for spelling in (folder, os.path.realpath(folder).rstrip("/")):
            if spelling and spelling not in found:
                found.append(spelling)
    return found


def _tilde(text, homes):
    """``text`` with a leading home folder written as ``~``, or None."""
    for home in homes:
        if text == home:
            return "~"
        if text.startswith(home + "/"):
            return "~/" + text[len(home) + 1:]
    return None


def stamp(moment):
    """A date-time as the tool stores it: ``2026-11-19T10:30:00``."""
    return moment.replace(microsecond=0).isoformat()


def parse_stamp(text):
    """Inverse of ``stamp``; also accepts a bare date.  None when unreadable."""
    try:
        return parse_now(text)
    except (UsageProblem, TypeError):
        return None


class App:
    """Everything a command needs to know about this run."""

    def __init__(self, root, env=None, console=None, now=None):
        self.root = Path(root)
        self.env = dict(os.environ if env is None else env)
        home = self.env.get("HOME") or str(Path.home())
        self.home = Path(home)
        if now is None:
            if self.env.get("COURSE_NOW"):
                now = parse_now(self.env["COURSE_NOW"])
            else:
                now = datetime.datetime.now()
        self.now = now.replace(microsecond=0, tzinfo=None)
        self.console = console if console is not None else Console.from_env(self.env)
        self.debug = self.env.get("COURSE_DEBUG", "") not in ("", "0")
        self.playground = self._playground()
        self.my_site = self.home / "Developer" / "my-site"
        self._catalog = None
        self._store = None
        self._home_spellings = None
        self._scrub_pattern = None
        self._entrance = None

    # -- paths --------------------------------------------------------------
    def _playground(self):
        raw = self.env.get("COURSE_PLAYGROUND", "").strip()
        if not raw:
            return self.home / "Developer" / "playground"
        return self.expand(raw)

    def expand(self, text):
        """Turn ``~/x`` (relative to HOME) or a relative path into an absolute Path."""
        text = str(text)
        if text == "~":
            return self.home
        if text.startswith("~/"):
            return self.home / text[2:]
        path = Path(text)
        if not path.is_absolute():
            path = Path(os.getcwd()) / path
        return path

    def home_spellings(self):
        """HOME as given and as resolved through links (``/tmp`` -> ``/private/tmp``)."""
        if self._home_spellings is None:
            self._home_spellings = _spellings([str(self.home)])
        return list(self._home_spellings)

    @property
    def entrance_path(self):
        """``~/Developer/fullstack-from-zero``: the one path every lesson writes for the workspace."""
        return self.home / "Developer" / ENTRANCE_NAME

    def entrance(self):
        """``~/Developer/fullstack-from-zero`` when it leads to this workspace, else None.

        It leads there when it is the workspace folder itself (a learner who
        moved the course) or a symbolic link to it (the entrance of a learner
        who kept the folder where it was, decision ``stay-in-sync`` of lesson
        0.2c).  A broken link, a link elsewhere and a different real folder
        (a half-finished move) do not lead there.  Looked at once per run.
        """
        if self._entrance is None:
            self._entrance = False
            path = self.entrance_path
            try:
                if os.path.exists(str(path)) and os.path.samefile(str(path), str(self.root)):
                    self._entrance = path
            except OSError:
                self._entrance = False
        return self._entrance or None

    def entrance_is_link(self):
        """True when the entrance leads to the workspace through a symbolic link."""
        return self.entrance() is not None and os.path.islink(str(self.entrance_path))

    def entrance_kind(self):
        """What is at ``~/Developer/fullstack-from-zero``, seen from this workspace.

        ``"workspace"``  the workspace folder itself (the learner moved it);
        ``"link"``       a symbolic link that leads to the workspace (the entrance);
        ``"missing"``    nothing at all;
        ``"broken"``     a symbolic link that leads nowhere or somewhere else;
        ``"other"``      a real folder or file that is not the workspace (for
                         example a half-finished move).
        """
        path = str(self.entrance_path)
        if self.entrance() is not None:
            return "link" if os.path.islink(path) else "workspace"
        if os.path.islink(path):
            return "broken"
        if os.path.lexists(path):
            return "other"
        return "missing"

    def _through_entrance(self, text):
        """``text`` (an absolute path in the workspace) spelled through the entrance, or None."""
        entrance = self.entrance()
        if entrance is None or not os.path.isabs(text):
            return None
        for root in _spellings([str(self.root)]):
            if text == root or text.startswith(root + "/"):
                return str(entrance) + text[len(root):]
        real = os.path.realpath(text)
        real_root = os.path.realpath(str(self.root))
        if real == real_root or real.startswith(real_root.rstrip("/") + "/"):
            return str(entrance) + real[len(real_root):]
        return None

    def show(self, path, entrance=True):
        """A path as the learner should read it: ``~/Developer/my-site``.

        The path is compared with HOME as given and as resolved, and, when
        neither matches, resolved itself: a home reached through a link (a
        simulation home under ``/tmp``) still prints as ``~``.

        The workspace and every path inside it are shown through
        ``~/Developer/fullstack-from-zero`` whenever that path leads to the workspace
        (``entrance()``), also when the tool was started from the real
        folder, so that the screen agrees with the lessons' ``cd
        ~/Developer/fullstack-from-zero``.  ``entrance=False`` shows the real place
        (``doctor`` says where the folder really is).
        """
        text = str(path)
        if entrance:
            text = self._through_entrance(text) or text
        homes = self.home_spellings()
        shown = _tilde(text, homes)
        if shown is not None:
            return shown
        if os.path.isabs(text):
            real = os.path.realpath(text)
            if real != text:
                shown = _tilde(real, homes)
                if shown is not None:
                    return shown
        return text

    def rel(self, path):
        """A workspace path as the learner should read it: ``stages/.../lesson.md``."""
        try:
            return Path(path).relative_to(self.root).as_posix()
        except ValueError:
            return self.show(path)

    def scrub(self, text):
        """Replace every home folder in ``text`` by ``~`` (for stored reports).

        Replaced: HOME and the home of the login account (they differ inside
        a simulation home), each as given and as resolved through links.  So
        a traceback never carries the user name, whichever spelling Python
        used for a file name.
        """
        if self._scrub_pattern is None:
            spellings = _spellings([str(self.home), account_home()])
            spellings.sort(key=len, reverse=True)
            if spellings:
                self._scrub_pattern = re.compile(
                    r"(?<![\w.\-])(?:" + "|".join(re.escape(s) for s in spellings)
                    + r")(?![\w.\-])")
            else:
                self._scrub_pattern = False
        if not self._scrub_pattern:
            return str(text)
        return self._scrub_pattern.sub("~", str(text))

    # -- collaborators ------------------------------------------------------
    @property
    def store(self):
        """The state store under ``learner/`` (created on first use)."""
        if self._store is None:
            from .store import Store
            self._store = Store(self.root / "learner", app=self)
        return self._store

    def catalog(self):
        """All lessons under ``stages/`` (loaded once per run)."""
        if self._catalog is None:
            from .catalog import load_catalog
            self._catalog = load_catalog(self.root)
        return self._catalog

    def child_env(self):
        """A copy of the environment for subprocesses."""
        return dict(self.env)

    # -- time ---------------------------------------------------------------
    @property
    def today(self):
        return self.now.date()

    def stamp(self):
        return stamp(self.now)
