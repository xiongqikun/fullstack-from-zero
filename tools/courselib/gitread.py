"""Read-only Git access for checks.

Rules (plan I4): the tool reads Git state only through machine-readable
commands (``status --porcelain=v1 -z``, ``rev-parse``, ``for-each-ref``,
``log --format=...``), every command has a timeout, and a repository that is
being checked is never modified.  ``GIT_OPTIONAL_LOCKS=0`` keeps even
``git status`` from refreshing the index on disk; ``diff.autoRefreshIndex``
is switched off for porcelain ``git diff``; and ``GitRepo.query`` runs every
command against a temporary copy of the index, because porcelain commands
such as ``git diff`` and ``git describe --dirty`` would otherwise rewrite
``.git/index`` after a stat-only change.

A folder that is not a repository is a normal answer (``repo.is_repo`` is
False and every query returns an empty value).  A missing ``git`` program, a
timeout or an unexpected failure is a problem of the environment and raises
``ToolTrouble``, which the check runner reports as 检查器出问题: the learner is
never told "not yet" because the tool could not look.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .errors import ToolTrouble

TEXT = {
    "no_git": "这台电脑上找不到 git 命令。",
    "no_git_recovery": "在终端里运行 git --version 看看；如果提示要安装开发者工具，按提示安装后再试。",
    "timeout": "git 命令超过 {seconds} 秒没有结束。",
    "failed": "git 命令意外失败（退出码 {code}）。",
    "forbidden": "检查函数想运行一条可能改动仓库的 git 命令（git {name}），工具拒绝执行。",
    "index_copy": "检查前复制 Git 暂存区文件失败。",
    "config_unreadable": "Git 读不了你的全局设置文件（~/.gitconfig），里面可能有一行写坏了。",
    "config_unreadable_recovery": "先不要改这个文件。运行 python3 tools/course.py doctor，把结果发给导师。",
}

#: Environment variables that would point git at another repository.
DROP_ENV = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_COMMON_DIR",
    "GIT_PREFIX",
)

#: Subcommands that ``GitRepo.query`` accepts: none of them changes anything.
#: ``grep`` is not among them: its ``-O``/``--open-files-in-pager`` option runs
#: an arbitrary program.
READ_ONLY = frozenset((
    "rev-parse", "rev-list", "log", "show", "status", "for-each-ref",
    "ls-files", "ls-tree", "cat-file", "diff", "diff-tree", "diff-index",
    "diff-files", "check-ignore", "check-attr", "merge-base", "describe",
    "shortlog", "count-objects", "name-rev", "show-ref", "blame",
))

#: Option prefixes ``GitRepo.query`` refuses whatever the subcommand: they
#: write a file or run another program.
FORBIDDEN_OPTIONS = ("--output", "--open-files-in-pager", "--ext-diff", "--exec")

DEFAULT_TIMEOUT = 10.0
_LOG_FORMAT = "%H%x1f%h%x1f%P%x1f%an%x1f%ae%x1f%aI%x1f%cI%x1f%s%x1f%b%x1e"


class RunResult:
    """What a finished command printed and how it ended."""

    def __init__(self, code, out, err, timed_out=False, missing=False):
        self.code = code
        self.out = out
        self.err = err
        self.timed_out = timed_out
        self.missing = missing

    @property
    def ok(self):
        return self.code == 0 and not self.timed_out and not self.missing

    @property
    def lines(self):
        return [line for line in self.out.splitlines() if line.strip()]

    def __repr__(self):
        return f"<RunResult code={self.code!r} out={self.out[:60]!r}>"


class Commit:
    """One commit as read from ``git log``."""

    def __init__(self, fields):
        (self.hash, self.short, parents, self.author_name, self.author_email,
         self.date, self.commit_date, self.subject, body) = fields
        self.parents = parents.split()
        self.body = body.strip("\n")
        self.message = self.subject + ("\n\n" + self.body if self.body else "")

    def __repr__(self):
        return f"<Commit {self.short} {self.subject!r}>"


class StatusEntry:
    """One line of ``git status --porcelain=v1``: two letters and a path."""

    def __init__(self, x, y, path, original=None):
        self.x = x
        self.y = y
        self.code = x + y
        self.path = path
        self.original = original

    def __repr__(self):
        return f"<StatusEntry {self.code!r} {self.path}>"


class Status:
    """The working tree and index of a repository at one moment."""

    def __init__(self, entries):
        self.entries = list(entries)

    @property
    def clean(self):
        """Nothing staged, nothing modified, nothing untracked."""
        return not self.entries

    @property
    def staged(self):
        """Paths with a change in the index (暂存区)."""
        return [e.path for e in self.entries if e.x not in " ?!"]

    @property
    def unstaged(self):
        """Tracked paths changed in the working tree but not staged."""
        return [e.path for e in self.entries if e.y not in " ?!"]

    @property
    def untracked(self):
        return [e.path for e in self.entries if e.code == "??"]

    def code(self, path):
        """The two status letters of ``path`` ("" when it has no entry)."""
        for entry in self.entries:
            if entry.path == path:
                return entry.code
        return ""

    def __repr__(self):
        return "<Status %s>" % ("clean" if self.clean else [e.code + " " + e.path for e in self.entries])


def parse_status(raw):
    """Parse the output of ``git status --porcelain=v1 -z``."""
    entries = []
    parts = raw.split("\0")
    index = 0
    while index < len(parts):
        item = parts[index]
        index += 1
        if len(item) < 4 or item[2] != " ":
            continue
        x, y, path = item[0], item[1], item[3:]
        original = None
        if (x in "RC" or y in "RC") and index < len(parts):
            original = parts[index]
            index += 1
        entries.append(StatusEntry(x, y, path, original))
    return entries


def reader_env(env):
    """The environment for read-only git commands."""
    child = dict(env)
    for name in DROP_ENV:
        child.pop(name, None)
    child.update({
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
        "PAGER": "cat",
        "LC_ALL": "C",
        "GIT_NO_LAZY_FETCH": "1",
    })
    return child


class GitReader:
    """Runs read-only git commands with a timeout."""

    BASE = ("--no-pager", "-c", "core.quotePath=false", "-c", "color.ui=never",
            "-c", "diff.autoRefreshIndex=false")

    def __init__(self, env, timeout=DEFAULT_TIMEOUT):
        self.env = reader_env(env)
        self.timeout = timeout
        self._program = None

    def program(self):
        if self._program is None:
            found = shutil.which("git", path=self.env.get("PATH"))
            if not found:
                raise ToolTrouble(TEXT["no_git"], recovery=TEXT["no_git_recovery"])
            self._program = found
        return self._program

    def run(self, cwd, *args, **options):
        """Run ``git <args>`` in ``cwd`` and return a ``RunResult``.

        The keyword option ``index`` names another index file to use
        (``GIT_INDEX_FILE``).
        """
        command = [self.program()] + list(self.BASE) + [str(a) for a in args]
        env = self.env
        if options.get("index"):
            env = dict(env)
            env["GIT_INDEX_FILE"] = str(options["index"])
        try:
            done = subprocess.run(
                command, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                capture_output=True, timeout=self.timeout, check=False)
        except subprocess.TimeoutExpired:
            raise ToolTrouble(TEXT["timeout"].format(seconds=int(self.timeout)),
                              detail="git " + " ".join(str(a) for a in args))
        except OSError as exc:
            raise ToolTrouble(TEXT["failed"].format(code="?"), detail=repr(exc))
        return RunResult(done.returncode,
                         done.stdout.decode("utf-8", "replace"),
                         done.stderr.decode("utf-8", "replace"))

    def global_config(self, key):
        """A value of the learner's global Git configuration, or None."""
        result = self.run(_safe_cwd(), "config", "--global", "--get", key)
        if result.code == 0:
            return result.out.rstrip("\n")
        return None

    def global_bool(self, key):
        """A global setting read as true/false; None when it is not set."""
        result = self.run(_safe_cwd(), "config", "--global", "--type=bool", "--get", key)
        if result.code != 0:
            return None
        return result.out.strip() == "true"

    def global_state(self, key):
        """A boolean global setting as "true", "false", "unset" or "invalid".

        "invalid" is a value Git cannot read as a boolean (a typo such as
        ``fasle``).  A configuration file that Git cannot read at all (a
        broken line) raises ``ToolTrouble``: the tool could not look.
        """
        result = self.run(_safe_cwd(), "config", "--global", "--type=bool", "--get", key)
        if result.code == 0:
            value = result.out.strip()
            return value if value in ("true", "false") else "invalid"
        if result.code == 1:
            return "unset"
        if "bad boolean" in result.err or "bad numeric" in result.err:
            return "invalid"
        raise ToolTrouble(TEXT["config_unreadable"], detail=result.err.strip(),
                          recovery=TEXT["config_unreadable_recovery"])

    def global_all(self, key):
        """Every value of a (multi-valued) global setting, in file order; [] when unset."""
        result = self.run(_safe_cwd(), "config", "--global", "-z", "--get-all", key)
        if result.code == 0:
            return result.out.split("\0")[:-1]
        if result.code == 1:
            return []
        raise ToolTrouble(TEXT["config_unreadable"], detail=result.err.strip(),
                          recovery=TEXT["config_unreadable_recovery"])

    def version(self):
        """The installed Git version as a tuple of ints, e.g. (2, 54, 0)."""
        result = self.run(_safe_cwd(), "version")
        numbers = []
        for word in result.out.split():
            if word[:1].isdigit():
                for piece in word.split("."):
                    if piece.isdigit():
                        numbers.append(int(piece))
                    else:
                        break
                break
        return tuple(numbers)


class GitRepo:
    """Read-only view of the folder ``path`` as a Git repository.

    ``is_repo`` is True only when ``path`` itself is the top folder of a
    repository (or a bare repository).  A folder that merely sits inside some
    other repository has ``is_repo`` False, ``inside_repo`` True and
    ``toplevel`` pointing at that other repository: the usual sign of a
    ``git init`` in the wrong place.
    """

    def __init__(self, path, reader):
        self.path = Path(path)
        self._reader = reader
        self._probe = None

    # -- plumbing -----------------------------------------------------------
    def _run(self, *args):
        return self._reader.run(self.path, *args)

    def _must(self, *args):
        result = self._run(*args)
        if result.code != 0:
            raise ToolTrouble(
                TEXT["failed"].format(code=result.code),
                detail="git {}\n{}".format(" ".join(str(a) for a in args), result.err.strip()))
        return result

    def refresh(self):
        """Forget what was read so far (the learner may have changed things)."""
        self._probe = None

    def _probe_once(self):
        if self._probe is not None:
            return self._probe
        probe = {"inside": False, "toplevel": None, "bare": False, "root": False}
        if self.path.is_dir():
            inside = self._run("rev-parse", "--is-inside-work-tree")
            if inside.code == 0 and inside.out.strip() == "true":
                top = self._must("rev-parse", "--show-toplevel").out.rstrip("\n")
                probe["inside"] = True
                probe["toplevel"] = Path(top)
                probe["root"] = _same_folder(top, self.path)
            elif inside.code == 0:
                bare = self._run("rev-parse", "--is-bare-repository")
                git_dir = self._run("rev-parse", "--git-dir")
                if (bare.code == 0 and bare.out.strip() == "true"
                        and git_dir.code == 0 and git_dir.out.strip() == "."):
                    probe["bare"] = True
                    probe["root"] = True
            elif "not a git repository" not in inside.err:
                raise ToolTrouble(TEXT["failed"].format(code=inside.code),
                                  detail="git rev-parse --is-inside-work-tree\n" + inside.err.strip())
        self._probe = probe
        return probe

    # -- what kind of folder is this ------------------------------------------
    @property
    def exists(self):
        """The folder exists."""
        return self.path.is_dir()

    @property
    def is_repo(self):
        """``path`` itself is the top of a repository (or a bare repository)."""
        return self._probe_once()["root"]

    @property
    def inside_repo(self):
        """``path`` is somewhere inside a working tree (its own or a parent's)."""
        return self._probe_once()["inside"]

    @property
    def toplevel(self):
        """Top folder of the repository that contains ``path``, or None."""
        return self._probe_once()["toplevel"]

    @property
    def is_bare(self):
        return self._probe_once()["bare"]

    # -- history ------------------------------------------------------------
    @property
    def head(self):
        """Full hash of the current commit; None before the first commit."""
        return self.ref("HEAD")

    @property
    def has_commits(self):
        return self.head is not None

    @property
    def branch(self):
        """Name of the current branch; None when HEAD is detached."""
        if not self.is_repo:
            return None
        result = self._run("symbolic-ref", "--short", "-q", "HEAD")
        return result.out.strip() or None if result.code == 0 else None

    def ref(self, name):
        """Full hash that ``name`` (a branch, tag, HEAD~1 ...) points at, or None."""
        if not self.is_repo:
            return None
        result = self._run("rev-parse", "--verify", "-q", f"{name}^{{commit}}")
        return result.out.strip() or None if result.code == 0 else None

    def commit_count(self, ref="HEAD"):
        """Number of commits reachable from ``ref`` (0 before the first commit)."""
        if self.ref(ref) is None:
            return 0
        return int(self._must("rev-list", "--count", ref).out.strip() or 0)

    def commits(self, limit=100, ref="HEAD"):
        """The newest ``limit`` commits reachable from ``ref``, newest first."""
        if self.ref(ref) is None:
            return []
        raw = self._must("log", "--format=" + _LOG_FORMAT, "-n", str(int(limit)), ref).out
        commits = []
        for record in raw.split("\x1e"):
            record = record.lstrip("\n")
            if not record:
                continue
            fields = record.split("\x1f")
            if len(fields) == 9:
                commits.append(Commit(fields))
        return commits

    def commit(self, ref="HEAD"):
        """The commit ``ref`` points at, or None."""
        found = self.commits(limit=1, ref=ref)
        return found[0] if found else None

    def changed_files(self, ref="HEAD"):
        """``[(letter, path)]`` changed by commit ``ref`` (A added, M modified, D deleted)."""
        if self.ref(ref) is None:
            return []
        raw = self._must("diff-tree", "--no-commit-id", "--name-status", "-r",
                         "--root", "-z", ref).out
        parts = [part for part in raw.split("\0") if part != ""]
        return [(parts[i][:1], parts[i + 1]) for i in range(0, len(parts) - 1, 2)]

    def file_at(self, ref, path):
        """Text of ``path`` as stored in commit ``ref``; None when it is not there."""
        if self.ref(ref) is None:
            return None
        result = self._run("cat-file", "blob", f"{ref}:{path}")
        return result.out if result.code == 0 else None

    # -- working tree and index ---------------------------------------------
    def status(self):
        """Staged, unstaged and untracked paths (a ``Status``)."""
        if not self.is_repo or self.is_bare:
            return Status([])
        raw = self._must("status", "--porcelain=v1", "-z", "--untracked-files=all").out
        return Status(parse_status(raw))

    def is_clean(self):
        """Nothing staged, modified or untracked.  False for a folder that is
        not a repository (or a bare one), so ``ctx.expect(repo.is_clean(), ...)``
        never passes on the wrong folder."""
        if not self.is_repo or self.is_bare:
            return False
        return self.status().clean

    def tracked(self):
        """Paths Git keeps track of (the index), sorted."""
        if not self.is_repo or self.is_bare:
            return []
        raw = self._must("ls-files", "-z").out
        return sorted(part for part in raw.split("\0") if part)

    def is_tracked(self, path):
        return str(path) in self.tracked()

    def is_ignored(self, path):
        """Would Git ignore the untracked ``path`` (relative to the repository)?"""
        if not self.is_repo or self.is_bare:
            return False
        result = self._run("check-ignore", "-q", "--", str(path))
        if result.code in (0, 1):
            return result.code == 0
        raise ToolTrouble(TEXT["failed"].format(code=result.code),
                          detail="git check-ignore\n" + result.err.strip())

    def ignored(self):
        """Untracked paths that are ignored, as ``git status --ignored`` lists them."""
        if not self.is_repo or self.is_bare:
            return []
        raw = self._must("status", "--porcelain=v1", "-z", "--ignored",
                         "--untracked-files=all").out
        return [entry.path for entry in parse_status(raw) if entry.code == "!!"]

    # -- configuration, branches, remotes -----------------------------------
    def config(self, key, scope=None):
        """A configuration value seen from this repository, or None.

        ``scope`` None gives the value Git would use here (local, then global,
        then system); "local" or "global" restricts the lookup.
        """
        if not self.is_repo:
            return None
        args = ["config"]
        if scope in ("local", "global"):
            args.append("--" + scope)
        result = self._run(*(args + ["--get", key]))
        return result.out.rstrip("\n") if result.code == 0 else None

    def config_bool(self, key, scope=None):
        """Like ``config`` but read as true/false; None when the key is not set."""
        if not self.is_repo:
            return None
        args = ["config", "--type=bool"]
        if scope in ("local", "global"):
            args.append("--" + scope)
        result = self._run(*(args + ["--get", key]))
        if result.code != 0:
            return None
        return result.out.strip() == "true"

    def branches(self):
        """Names of the local branches."""
        if not self.is_repo:
            return []
        return self._must("for-each-ref", "--format=%(refname:short)", "refs/heads").lines

    def tags(self):
        if not self.is_repo:
            return []
        return self._must("for-each-ref", "--format=%(refname:short)", "refs/tags").lines

    def remotes(self):
        """``{name: url}`` of the configured remotes."""
        if not self.is_repo:
            return {}
        result = self._run("config", "-z", "--get-regexp", r"^remote\..*\.url$")
        remotes = {}
        if result.code != 0:
            return remotes
        for item in result.out.split("\0"):
            if "\n" not in item:
                continue
            key, value = item.split("\n", 1)
            remotes[key[len("remote."):-len(".url")]] = value
        return remotes

    def upstream(self):
        """The branch this one pushes to, e.g. "origin/main"; None when unset."""
        if not self.is_repo or self.head is None:
            return None
        result = self._run("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
        return result.out.strip() or None if result.code == 0 else None

    def ahead_behind(self):
        """``(ahead, behind)`` against the upstream branch; None without one."""
        if self.upstream() is None:
            return None
        counts = self._must("rev-list", "--left-right", "--count", "HEAD...@{u}").out.split()
        return (int(counts[0]), int(counts[1])) if len(counts) == 2 else None

    # -- escape hatch -------------------------------------------------------
    def query(self, *args):
        """Run another read-only git command here and return its ``RunResult``.

        Only subcommands that cannot change anything are accepted (see
        ``READ_ONLY``); options that write a file or run a program
        (``--output``, ``--ext-diff`` ...) are refused.  The command runs
        against a temporary copy of the index, so even porcelain commands that
        like to refresh it (``diff``, ``describe --dirty``) leave the
        repository exactly as it was.
        """
        if not args or str(args[0]) not in READ_ONLY:
            raise ToolTrouble(TEXT["forbidden"].format(name=args[0] if args else ""))
        for arg in args[1:]:
            text = str(arg)
            for option in FORBIDDEN_OPTIONS:
                if text.startswith(option):
                    raise ToolTrouble(TEXT["forbidden"].format(name=f"{args[0]} {option}"))
        if not self.exists:
            return RunResult(128, "", "no such folder", missing=True)
        index = self._index_file()
        if index is None:
            return self._run(*args)
        folder = tempfile.mkdtemp(prefix="course-index-")
        try:
            copy = os.path.join(folder, "index")
            try:
                shutil.copyfile(str(index), copy)
            except OSError as exc:
                raise ToolTrouble(TEXT["index_copy"], detail=repr(exc))
            return self._reader.run(self.path, *args, index=copy)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def _index_file(self):
        """The index file of this repository, or None when there is none."""
        if not self.inside_repo and not self.is_repo:
            return None
        result = self._run("rev-parse", "--git-path", "index")
        if result.code != 0 or not result.out.strip():
            return None
        path = Path(result.out.strip())
        if not path.is_absolute():
            path = self.path / path
        return path if path.is_file() else None

    def __repr__(self):
        return f"<GitRepo {self.path}>"


def _safe_cwd():
    """The current folder, or "/" when it was deleted under our feet."""
    try:
        return os.getcwd()
    except OSError:
        return "/"


def _same_folder(a, b):
    try:
        return os.path.samefile(str(a), str(b))
    except OSError:
        return False
