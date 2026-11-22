"""Practice states: the scenario builder context and safe building.

A scenario is a folder under the playground that the tool fills with a known
state (files, a Git repository with commits ...).  Lesson modules describe
scenarios as builder functions ``def build(sc): ...``; ``sc`` is a
``ScenarioContext``.  The functions here run a builder safely:

- a scenario folder is always inside the playground, never elsewhere;
- a folder that is not empty is not touched without ``reset``;
- ``reset`` deletes a folder only when it carries the marker file
  ``.playground`` that the tool itself wrote;
- the marker records the seed and the facts the builder noted, so that a check
  can later compute the expected answer.  The facts and the todo lines are
  stored base64-encoded (marker version 2), so that a learner's own search
  (``grep -rin <word> .``) or a ``cat .playground`` never shows an expected
  answer.  This guards against accidents and casual reading; it is not a
  secret: anyone can decode it.  Version 1 markers (plain JSON facts) are
  still read.
- material under ``starter/`` is always copied from the original recorded in
  ``starter_manifest.json`` (plan G11a), never from the learner's copy in the
  workspace, which a beginner may have edited.
"""

import base64
import datetime
import hashlib
import io
import json
import os
import random
import re
import shutil
import textwrap
import traceback
from pathlib import Path, PurePosixPath

from . import gitwrite
from .catalog import describe_exception
from .errors import Cancelled, Refused, ToolTrouble
from .store import atomic_write_text
from .store import reason as os_reason
from .ui import captured

MARKER = ".playground"
MARKER_VERSION = 2
#: Marker versions this tool can read.
MARKER_VERSIONS = (1, 2)
#: The first key of every marker: what the file is, for a learner who opens it.
MARKER_NOTE = "学习工具的记号文件，请不要改动或删除，也不用打开。"
#: Fragments of a fact this long or longer never appear in the marker's text.
FACT_FRAGMENT = 4

#: Original content of every file under ``starter/`` (plan G11a).  Written by
#: ``tools/dev/build_starter_manifest.py --write``; a test may point it elsewhere.
STARTER_MANIFEST = Path(__file__).resolve().parent / "starter_manifest.json"
STARTER_FOLDER = "starter"

TEXT = {
    "unsafe_playground": (
        "练习场的位置不安全：{path}。练习场不能是整个磁盘、你的主文件夹，"
        "不能和学习工作区或 ~/Developer/my-site 互相包含。"
        "请检查环境变量 COURSE_PLAYGROUND。"
    ),
    "outside": "这个位置不在练习场里面，工具不会动它：{path}",
    "not_a_folder": "练习场里这个位置已经有一个同名的文件，不是文件夹：{path}\n把它改个名字或移走，再运行一次。",
    "not_empty": (
        "这个文件夹里已经有东西了：{path}\n"
        "工具不会覆盖它。想重新搭一份，在命令后面加上 --reset"
        "（会删除这个文件夹里现有的全部内容，再重新搭建）。"
    ),
    "not_empty_command": (
        "这个文件夹里已经有东西了：{path}\n"
        "工具不会覆盖它。想重新搭一份（会删除这个文件夹里现有的全部内容，再重新搭建）："
        "python3 tools/course.py scenario {id} --reset"
    ),
    "not_empty_foreign": (
        "这个位置已经有一个文件夹了，而且不是工具搭的（里面没有 .playground 标记文件）：{path}\n"
        "工具不会覆盖它，也不会删除它。如果里面的东西不要了，请你自己把它改名或移走，再运行一次。"
    ),
    "no_marker": (
        "这个文件夹不是工具搭的（里面没有 .playground 标记文件）：{path}\n"
        "工具不会删除它。如果里面的东西确实不要了，请你自己把它改名或移走，再运行一次。"
    ),
    "is_link": "这个位置是一个链接，不是真正的文件夹，工具不会动它：{path}",
    "delete_failed": "删除旧的练习文件夹失败（{reason}）：{path}",
    "builder_failed": "搭建练习场的代码出错了：{what}",
    "mkdir_failed": "建不了练习场景的文件夹（{reason}）：{path}",
    "mkdir_failed_recovery": "看看 ~/Developer 是不是一个可以写入的文件夹，然后再运行一次；还是不行，把这一段发给导师。",
    "bad_path": "搭建练习场的代码想写到场景文件夹外面：{path}",
    "bad_source": "搭建练习场的代码想从工作区外面复制东西：{path}",
    "missing_source": "搭建练习场需要的文件在工作区里找不到：{path}",
    "no_states": "搭建这个练习场需要 tools/courselib/states.py，但它还没有建好。",
    "bad_fact": "搭建练习场的代码记录了一个存不进 JSON 的值：{key}",
    "repo_at_root": "搭建练习场的代码想把场景文件夹本身建成仓库。仓库要建在场景里面的一个子文件夹里。",
    "git_global_option": "搭建练习场的代码给 sc.git 传了全局选项 {option}；第一个参数要是 git 的子命令（例如 log、add）。",
    "starter_unknown": "搭建练习场的代码要复制 {path}，但起始文件的原样清单里没有它。",
    "starter_unknown_detail": "Add the file under starter/ and run python3 tools/dev/build_starter_manifest.py --write.",
    "no_manifest": "起始文件的原样清单 tools/courselib/starter_manifest.json 读不出来了（{reason}）。",
    "bad_manifest_entry": "起始文件的原样清单里 {path} 这一项坏了。",
    "manifest_recovery": "这不是你的错。把这一段发给导师。",
}

#: Neutral lower-case words for randomised folder and file names.
WORDS = (
    "amber", "birch", "cedar", "coral", "delta", "dune", "ember", "fjord",
    "flint", "grove", "harbor", "heron", "iris", "jade", "kelp", "lotus",
    "lumen", "maple", "meadow", "north", "olive", "pearl", "pine", "quartz",
    "reed", "river", "sage", "slate", "tide", "tulip", "umber", "violet",
    "willow", "wren", "yarrow", "zephyr",
)

_SKIP_ON_COPY = shutil.ignore_patterns("__pycache__", ".DS_Store", ".git", "*.pyc")


class ScenarioInfo:
    """What is known about a built (or missing) scenario folder.

    ``exists`` is True only for a folder that the tool finished building.
    """

    def __init__(self, path, marker=None):
        marker = marker if isinstance(marker, dict) else {}
        self.path = Path(path)
        self.started = bool(marker)
        self.exists = bool(marker.get("complete")) and self.path.is_dir()
        #: the marker says the build finished (an unreadable marker counts as
        #: finished, so an unknown folder is never rebuilt without --reset)
        self.started_complete = bool(marker) and (bool(marker.get("complete"))
                                                  or bool(marker.get("unreadable")))
        self.id = str(marker.get("scenario", ""))
        self.key = str(marker.get("key", ""))
        self.lesson = str(marker.get("lesson", ""))
        self.seed = marker.get("seed")
        self.form = marker.get("form")
        self.built = marker.get("built")
        facts = marker.get("facts")
        self.facts = facts if isinstance(facts, dict) else {}
        todo = marker.get("todo")
        self.todo = [str(line) for line in todo] if isinstance(todo, list) else []

    def __repr__(self):
        return f"<ScenarioInfo {self.id or self.path.name} exists={self.exists}>"


def read_marker(path):
    """The marker of the scenario folder ``path`` as a dict, or None when absent.

    Facts and todo lines are decoded (marker version 2) or read as they are
    (version 1), so the result always has plain ``facts`` and ``todo``.  A
    marker that cannot be read gives ``{"complete": False, "unreadable": True}``.
    """
    marker_path = Path(path) / MARKER
    if not marker_path.is_file() or marker_path.is_symlink():
        return None
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"complete": False, "unreadable": True}
    if not isinstance(marker, dict):
        return {"complete": False, "unreadable": True}
    return decode_marker(marker)


def decode_marker(marker):
    """A marker dict with its payload decoded into plain ``facts`` and ``todo``."""
    marker = dict(marker)
    if "data" not in marker:            # version 1: facts and todo in plain JSON
        return marker
    try:
        raw = base64.b64decode(str(marker.pop("data")).encode("ascii"), validate=True)
        mask = int(marker.pop("mask", 0) or 0)
        if mask:
            raw = bytes(byte ^ mask for byte in raw)
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("payload is not an object")
    except (ValueError, TypeError, UnicodeDecodeError):
        # The tool's own marker, damaged: never rebuilt without --reset, never
        # used as a finished build.
        marker.update({"complete": False, "unreadable": True, "facts": {}, "todo": []})
        return marker
    marker["facts"] = payload.get("facts", {})
    marker["todo"] = payload.get("todo", [])
    return marker


def encode_payload(facts, todo):
    """``(data, mask)``: facts and todo as base64 of UTF-8 JSON.

    No fragment of ``FACT_FRAGMENT`` or more characters of any fact value or
    todo line appears in ``data``, compared without regard to case (the way
    ``grep -i`` would look).  Plain base64 almost always passes; when it does
    not, the bytes are XOR-ed with a one-byte ``mask`` that is stored next to
    the data.  Against accidents, not a secret.
    """
    raw = json.dumps({"facts": facts, "todo": todo}, ensure_ascii=False,
                     separators=(",", ":")).encode("utf-8")
    fragments = _fragments([facts, todo])
    data = ""
    for mask in range(256):
        body = bytes(byte ^ mask for byte in raw) if mask else raw
        data = base64.b64encode(body).decode("ascii")
        folded = data.lower()
        if not any(fragment in folded for fragment in fragments):
            return data, mask
    return base64.b64encode(raw).decode("ascii"), 0


def _fragments(value, found=None):
    """Lower-case pieces (``FACT_FRAGMENT`` characters) of every string in ``value``.

    Only pieces made of base64 characters can ever occur in base64 text.
    """
    found = set() if found is None else found
    if isinstance(value, dict):
        for item in value.values():
            _fragments(item, found)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _fragments(item, found)
    elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
        text = str(value).lower()
        for start in range(len(text) - FACT_FRAGMENT + 1):
            piece = text[start:start + FACT_FRAGMENT]
            if all(ch.isascii() and (ch.isalnum() or ch in "+/=") for ch in piece):
                found.add(piece)
    return found


def read_info(path):
    """Read the marker of the scenario folder ``path``."""
    path = Path(path)
    return ScenarioInfo(path, read_marker(path))


def _real(path):
    return Path(os.path.realpath(str(path)))


def _is_inside(child, parent):
    child, parent = _real(child), _real(parent)
    return child != parent and parent in child.parents


def check_playground(app):
    """Raise ``Refused`` when the playground location could endanger other files."""
    playground = _real(app.playground)
    home = _real(app.home)
    root = _real(app.root)
    site = _real(app.my_site)
    unsafe = (
        playground == Path(playground.anchor)
        or playground == home or playground in home.parents
        # the workspace: neither around it nor inside it (a nested repository)
        or playground == root or playground in root.parents or root in playground.parents
        # the learner's own site (plan G15): neither around it nor inside it
        or playground == site or playground in site.parents or site in playground.parents
    )
    if unsafe:
        raise Refused(TEXT["unsafe_playground"].format(path=app.show(app.playground)))
    return playground


def scenario_folder(app, name):
    """The folder of scenario ``name`` (a relative path) inside the playground."""
    relative = PurePosixPath(str(name))
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise Refused(TEXT["outside"].format(path=name))
    target = app.playground.joinpath(*relative.parts)
    if target.is_symlink():
        # Checked first: a link inside the playground "is outside" only
        # because of where it points, and that message would confuse.
        raise Refused(TEXT["is_link"].format(path=app.show(target)))
    if not _is_inside(target, app.playground):
        raise Refused(TEXT["outside"].format(path=app.show(target)))
    return target


def remove_built(app, target):
    """Delete a folder the tool built earlier.  Returns True when it was deleted.

    Refuses (``Refused``) anything outside the playground, a link, a plain
    file and any folder without the marker ``.playground``.  An empty folder
    is left in place: there is nothing to delete.
    """
    check_playground(app)
    target = Path(target)
    if target.is_symlink():
        raise Refused(TEXT["is_link"].format(path=app.show(target)))
    if not _is_inside(target, app.playground):
        raise Refused(TEXT["outside"].format(path=app.show(target)))
    if not target.exists():
        return False
    if not target.is_dir():
        raise Refused(TEXT["not_a_folder"].format(path=app.show(target)))
    if not any(target.iterdir()):
        return False
    marker = target / MARKER
    if not marker.is_file() or marker.is_symlink():
        raise Refused(TEXT["no_marker"].format(path=app.show(target)))
    try:
        shutil.rmtree(str(target))
    except OSError as exc:
        raise ToolTrouble(TEXT["delete_failed"].format(reason=os_reason(exc),
                                                       path=app.show(target)),
                          detail=repr(exc))
    return True


class ScenarioContext:
    """The object a scenario builder receives (``sc``).

    Every path a builder passes is relative to the scenario folder ``sc.root``
    and may not leave it.  See docs/authoring/tool-api.md for the full list.
    """

    def __init__(self, app, root, seed, scenario_id="", key="", lesson_id="", form=None):
        self._app = app
        self.root = Path(root)
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.id = scenario_id
        self.key = key
        self.lesson_id = lesson_id
        self.form = form
        self.now = app.now
        self.workspace = app.root
        self.facts = {}
        self._todo = []
        self._commits = 0

    # -- paths --------------------------------------------------------------
    def path(self, rel="."):
        """Absolute path of ``rel`` inside the scenario folder."""
        relative = PurePosixPath(str(rel).replace(os.sep, "/"))
        if relative.is_absolute() or ".." in relative.parts:
            raise ToolTrouble(TEXT["bad_path"].format(path=rel))
        return self.root.joinpath(*relative.parts) if relative.parts else self.root

    def show(self, rel="."):
        """The path as the learner should read it (``~/Developer/playground/...``)."""
        return self._app.show(self.path(rel))

    # -- files --------------------------------------------------------------
    def mkdir(self, rel):
        """Create the folder ``rel`` (and its parents).  Returns its path."""
        target = self.path(rel)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def write(self, rel, text, exact=False, executable=False):
        """Write a UTF-8 text file with LF line ends.  Returns its path.

        Unless ``exact`` is true the text is dedented, one leading line break
        is dropped and the file ends with exactly one line break, so a
        triple-quoted string can be indented like the code around it.
        """
        target = self.path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        content = str(text)
        if not exact:
            content = textwrap.dedent(content)
            content = content.removeprefix("\n")
            content = content.rstrip("\n") + "\n" if content.strip("\n") else ""
        with open(str(target), "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        if executable:
            os.chmod(str(target), 0o755)
        return target

    def write_bytes(self, rel, data):
        """Write raw bytes (another encoding, CRLF line ends, a binary file)."""
        target = self.path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(str(target), "wb") as handle:
            handle.write(bytes(data))
        return target

    def append(self, rel, text):
        """Append ``text`` to a file exactly as given (the file is created if needed)."""
        target = self.path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(str(target), "a", encoding="utf-8", newline="") as handle:
            handle.write(str(text))
        return target

    def touch(self, rel):
        """Create an empty file (like the ``touch`` command)."""
        target = self.path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
        return target

    def copy_in(self, source, rel):
        """Copy a file or folder from the workspace (e.g. "starter/my-site").

        Anything under ``starter/`` comes from the original recorded in the
        starter manifest (plan G11a), never from the workspace copy, which the
        learner may have changed; a path under ``starter/`` that the manifest
        does not know is a builder mistake.
        """
        relative = PurePosixPath(str(source).replace(os.sep, "/"))
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ToolTrouble(TEXT["bad_source"].format(path=source))
        target = self.path(rel)
        if relative.parts[0] == STARTER_FOLDER:
            return copy_starter(relative.as_posix(), target)
        origin = self.workspace.joinpath(*relative.parts)
        if origin.is_dir():
            shutil.copytree(str(origin), str(target), ignore=_SKIP_ON_COPY, dirs_exist_ok=True)
        elif origin.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(str(origin), str(target))
        else:
            raise ToolTrouble(TEXT["missing_source"].format(path=source))
        return target

    def remove(self, rel):
        """Delete a file or folder inside the scenario (missing is fine)."""
        target = self.path(rel)
        if target == self.root:
            raise ToolTrouble(TEXT["bad_path"].format(path=rel))
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(str(target))
        elif target.exists() or target.is_symlink():
            target.unlink()

    def move(self, source, dest):
        """Rename or move ``source`` to ``dest`` inside the scenario."""
        target = self.path(dest)
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(str(self.path(source)), str(target))
        return target

    def set_mtime(self, rel, when):
        """Set the modification time of a file (``when`` is a datetime)."""
        seconds = when.timestamp()
        os.utime(str(self.path(rel)), (seconds, seconds))

    # -- git ----------------------------------------------------------------
    def git_init(self, rel, branch=gitwrite.DEFAULT_BRANCH, bare=False):
        """Create a Git repository in the sub-folder ``rel``.  Returns its path.

        The scenario folder itself cannot be the repository: the marker file
        ``.playground`` would show up in the learner's ``git status``.
        """
        target = self.path(rel)
        if target == self.root:
            raise ToolTrouble(TEXT["repo_at_root"])
        return gitwrite.git_init(target, self._env(), branch=branch, bare=bare)

    def git_commit(self, rel, message, add="all", date=None, author=None,
                   allow_empty=False, force=False):
        """Stage and commit in the repository ``rel``.  Returns the full hash.

        The commit is made by 练习场 <playground@example.invalid> with signing
        off.  ``date`` defaults to the build time plus one minute per commit,
        so commits made in one build keep their order.
        """
        if date is None:
            date = self.now + datetime.timedelta(minutes=self._commits)
        self._commits += 1
        return gitwrite.git_commit(self.path(rel), message, self._env(), add=add,
                                   date=date, author=author, allow_empty=allow_empty,
                                   force=force)

    def git(self, rel, *args, **options):
        """Run any git command in ``rel`` as the builder.  Returns its output text.

        Keyword options: ``date`` and ``author`` as in ``git_commit``;
        ``check=False`` returns the ``RunResult`` instead of raising on failure.
        """
        check = options.pop("check", True)
        if args and str(args[0]).startswith("-"):
            # -C, -c, --git-dir, --work-tree ... would lead out of the scenario.
            raise ToolTrouble(TEXT["git_global_option"].format(option=args[0]))
        result = gitwrite.run_git(self.path(rel), args, self._env(),
                                  date=options.pop("date", None),
                                  author=options.pop("author", None), check=check)
        if options:
            raise TypeError("unknown options: {}".format(", ".join(sorted(options))))
        return result.out if check else result

    def _env(self):
        """The environment for builder Git: Git never looks above ``sc.root``."""
        env = self._app.child_env()
        env["GIT_CEILING_DIRECTORIES"] = os.path.realpath(str(self.root))
        return env

    # -- randomness ---------------------------------------------------------
    def pick(self, options):
        """One item of ``options``, chosen by the seed."""
        return self.rng.choice(list(options))

    def sample(self, options, count):
        """``count`` different items of ``options``, chosen by the seed."""
        return self.rng.sample(list(options), count)

    def randint(self, low, high):
        """A whole number from ``low`` to ``high`` inclusive, chosen by the seed."""
        return self.rng.randint(low, high)

    def word(self):
        """A neutral lower-case word for a folder or file name."""
        return self.rng.choice(WORDS)

    def words(self, count):
        """``count`` different neutral words."""
        return self.rng.sample(WORDS, count)

    # -- time ---------------------------------------------------------------
    def ago(self, days=0, hours=0, minutes=0):
        """A moment before the build time (for commit dates and file times)."""
        return self.now - datetime.timedelta(days=days, hours=hours, minutes=minutes)

    # -- talking to the check and to the learner ------------------------------
    def fact(self, key, value):
        """Record a fact for later checks (stored in the marker).  Returns ``value``."""
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            raise ToolTrouble(TEXT["bad_fact"].format(key=key))
        self.facts[str(key)] = value
        return value

    def todo(self, text):
        """A line the learner sees after the scenario is built (what to do)."""
        self._todo.append(" ".join(str(text).split()))

    # -- the state ladder ---------------------------------------------------
    def state(self, name, base="."):
        """Build ladder state ``name`` ("S0" ... "S7") under ``base``.

        Returns the path of the ``my-site`` folder inside ``base``.  The work
        is done by ``courselib.states.build_state`` (plan I6).
        """
        try:
            from . import states
        except ImportError:
            raise ToolTrouble(TEXT["no_states"])
        target = self.mkdir(base)
        built = _call_with_known(states.build_state, name, target, {
            "workspace": self.workspace, "now": self.now, "seed": self.seed,
            "env": self._env(),
        })
        return Path(built) if built else target / "my-site"

    def site_before(self, lesson_id=None, base="."):
        """Build the copy of the learner's site as it is just before a lesson.

        ``lesson_id`` defaults to the lesson this scenario belongs to: in the
        ``start`` scenario of 1.7 this builds state S4 (reached at the end of
        1.6).  Returns the path of the ``my-site`` folder and records the facts
        ``site`` (its path inside the scenario, e.g. "my-site"),
        ``site_state`` ("S4"), ``site_commits`` (int), ``site_owner`` (the pen
        name in the heading, or None before S2) and, from S7 on,
        ``site_remote`` (the stand-in for GitHub, inside the scenario).
        """
        try:
            from . import states
        except ImportError:
            raise ToolTrouble(TEXT["no_states"])
        name = states.state_before(lesson_id or self.lesson_id)
        target = self.mkdir(base)
        built = states.build(name, target, workspace=self.workspace, now=self.now,
                             seed=self.seed, env=self._env())

        def inside(path):
            return Path(path).relative_to(self.root).as_posix() or "."

        self.fact("site", inside(built.site))
        self.fact("site_state", name)
        self.fact("site_commits", built.facts.get("commits", 0))
        self.fact("site_owner", built.facts.get("owner"))
        if built.facts.get("remote"):
            self.fact("site_remote", inside(target / built.facts["remote"]))
        return built.site


# ---------------------------------------------------------------------------
# The starter manifest (plan G11a)
# ---------------------------------------------------------------------------
def load_starter_manifest(path=None):
    """The starter manifest as a dict; ``ToolTrouble`` when it cannot be read.

    Shape: ``{"schema": 1, "note": ..., "learner_edits": [paths],
    "files": {"starter/<path>": {"sha256": hex, "text": str} or
    {"sha256": hex, "base64": str}}}``.
    """
    path = Path(path) if path is not None else STARTER_MANIFEST
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        reason = os_reason(exc) if isinstance(exc, OSError) else "内容不是有效的 JSON"
        raise ToolTrouble(TEXT["no_manifest"].format(reason=reason), detail=repr(exc),
                          recovery=TEXT["manifest_recovery"])
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise ToolTrouble(TEXT["no_manifest"].format(reason="缺少 files"),
                          recovery=TEXT["manifest_recovery"])
    return data


def starter_bytes(path, entry):
    """The original bytes of one manifest entry, checked against its sha256."""
    try:
        if "text" in entry:
            data = str(entry["text"]).encode("utf-8")
        else:
            data = base64.b64decode(str(entry["base64"]).encode("ascii"), validate=True)
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("sha256 does not match")
    except (KeyError, TypeError, ValueError) as exc:
        raise ToolTrouble(TEXT["bad_manifest_entry"].format(path=path), detail=repr(exc),
                          recovery=TEXT["manifest_recovery"])
    return data


def starter_originals(source, manifest=None):
    """``{relative path: bytes}`` of the original files at or below ``source``.

    ``source`` is a workspace path such as ``"starter/my-site"`` or
    ``"starter/my-site/index.html"``.  For a single file the key is ``""``.
    Raises ``ToolTrouble`` when the manifest knows nothing there.
    """
    data = manifest if manifest is not None else load_starter_manifest()
    wanted = PurePosixPath(str(source).replace(os.sep, "/")).as_posix().rstrip("/")
    found = {}
    for path, entry in data["files"].items():
        if path == wanted:
            found[""] = starter_bytes(path, entry)
        elif path.startswith(wanted + "/"):
            found[path[len(wanted) + 1:]] = starter_bytes(path, entry)
    if not found:
        raise ToolTrouble(TEXT["starter_unknown"].format(path=source),
                          detail=TEXT["starter_unknown_detail"])
    return found


def copy_starter(source, target, manifest=None):
    """Write the original of ``source`` (a file or folder under starter/) to ``target``."""
    target = Path(target)
    originals = starter_originals(source, manifest)
    for rel, data in sorted(originals.items()):
        destination = target.joinpath(*rel.split("/")) if rel else target
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(str(destination), "wb") as handle:
            handle.write(data)
    return target


#: Names in starter/ that are never the learner's change (the system makes them).
STARTER_NOISE = ("__pycache__", ".DS_Store")


def starter_differences(workspace, manifest=None):
    """Files under ``<workspace>/starter`` that differ from the manifest.

    A list of ``(path, kind)`` in path order, ``kind`` being ``"changed"``
    (the content differs) or ``"missing"`` (the file is gone or is not a
    plain file).  Files the manifest lists under ``learner_edits`` (the file a
    lesson tells the learner to edit) are never reported; files the learner
    added are not reported either: nothing is built from them.
    """
    data = manifest if manifest is not None else load_starter_manifest()
    skip = set(data.get("learner_edits") or [])
    root = Path(workspace)
    found = []
    for path, entry in sorted(data["files"].items()):
        if path in skip:
            continue
        disk = root.joinpath(*path.split("/"))
        if disk.is_symlink() or not disk.is_file():
            found.append((path, "missing"))
            continue
        try:
            digest = hashlib.sha256(disk.read_bytes()).hexdigest()
        except OSError:
            found.append((path, "missing"))
            continue
        if digest != entry.get("sha256"):
            found.append((path, "changed"))
    return found


def _call_with_known(function, name, base, optional):
    """Call ``function(name, base, **kw)`` with the keyword arguments it accepts."""
    import inspect
    try:
        parameters = inspect.signature(function).parameters
    except (TypeError, ValueError):
        return function(name, base)
    if any(p.kind == p.VAR_KEYWORD for p in parameters.values()):
        return function(name, base, **optional)
    accepted = {key: value for key, value in optional.items() if key in parameters}
    return function(name, base, **accepted)


def _write_marker(target, data):
    """Write the marker: the note first, facts and todo encoded (version 2)."""
    stored = {"note": MARKER_NOTE}
    for key, value in data.items():
        if key not in ("facts", "todo", "note"):
            stored[key] = value
    payload, mask = encode_payload(data.get("facts") or {}, data.get("todo") or [])
    stored["data"] = payload
    if mask:
        stored["mask"] = mask
    text = json.dumps(stored, ensure_ascii=False, indent=2) + "\n"
    atomic_write_text(str(Path(target) / MARKER), text)


def build(app, builder, folder, scenario_id="", key="", lesson_id="", seed=None,
          form=None, reset=False, log=True, typed=None):
    """Build a practice state in ``<playground>/<folder>`` and return its info.

    ``typed`` is the id as the learner typed it (``1.3`` for ``1.3-start``);
    a refusal names the ``--reset`` command with it.

    ``builder`` is a function taking one ``ScenarioContext``.  Raises
    ``Refused`` when the folder holds something and ``reset`` is false, or
    when ``reset`` would delete a folder the tool did not build, and
    ``ToolTrouble`` when the builder itself fails.
    """
    check_playground(app)
    target = scenario_folder(app, folder)
    if target.is_symlink():
        raise Refused(TEXT["is_link"].format(path=app.show(target)))
    if target.exists():
        if not target.is_dir():
            raise Refused(TEXT["not_a_folder"].format(path=app.show(target)))
        if any(target.iterdir()):
            marker = target / MARKER
            if not marker.is_file() or marker.is_symlink():
                key = "no_marker" if reset else "not_empty_foreign"
                raise Refused(TEXT[key].format(path=app.show(target)))
            # A build the tool started but never finished (Ctrl+C, a failing
            # builder) belongs to the tool: it is rebuilt without --reset.
            if not reset and read_info(target).started_complete:
                if scenario_id and not str(scenario_id).startswith("exam-"):
                    raise Refused(TEXT["not_empty_command"].format(
                        path=app.show(target), id=typed or scenario_id))
                raise Refused(TEXT["not_empty"].format(path=app.show(target)))
            remove_built(app, target)
    if seed is None:
        seed = random.SystemRandom().randrange(1, 1000000)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ToolTrouble(TEXT["mkdir_failed"].format(reason=os_reason(exc),
                                                      path=app.show(target)),
                          detail=repr(exc), recovery=TEXT["mkdir_failed_recovery"])
    marker = {
        "tool": "course.py", "marker": MARKER_VERSION,
        "scenario": scenario_id or str(folder), "key": key, "lesson": lesson_id,
        "seed": int(seed), "form": form, "built": app.stamp(),
        "complete": False, "facts": {}, "todo": [],
    }
    _write_marker(target, marker)
    sc = ScenarioContext(app, target, seed, scenario_id=marker["scenario"], key=key,
                         lesson_id=lesson_id, form=form)
    sink = io.StringIO()
    try:
        with captured(sink):
            builder(sc)
    except (Cancelled, KeyboardInterrupt):
        raise
    except ToolTrouble as exc:
        if not exc.where:
            exc.where = marker["scenario"]
        raise
    except BaseException as exc:  # noqa: BLE001 - whatever a builder raises, even SystemExit
        filename = getattr(getattr(builder, "__code__", None), "co_filename", "")
        raise ToolTrouble(
            TEXT["builder_failed"].format(what=describe_exception(exc, filename)),
            detail=app.scrub("".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__))),
            where=app.rel(filename) if filename else marker["scenario"])
    marker.update({"complete": True, "facts": sc.facts, "todo": sc._todo})
    _write_marker(target, marker)
    if log:
        app.store.log("scenario-built", scenario=marker["scenario"], lesson=lesson_id,
                      seed=int(seed), form=form, folder=str(folder), reset=bool(reset))
    return read_info(target)


_PLACEHOLDER = re.compile(r"\{([a-z_][a-z0-9_]*)\}")


def fill_text(app, text, info):
    """Fill ``{dir}`` and ``{fact name}`` placeholders of a task text.

    ``{dir}`` becomes the scenario folder as the learner should read it; any
    other ``{name}`` becomes the fact of that name.  Unknown placeholders and
    other braces are left as they are.
    """
    values = {str(key): value for key, value in info.facts.items()}
    values["dir"] = app.show(info.path)

    def replace(match):
        name = match.group(1)
        return str(values[name]) if name in values else match.group(0)

    return _PLACEHOLDER.sub(replace, str(text))


def build_lesson_scenario(app, lesson, key, seed=None, reset=False, folder=None, typed=None):
    """Build scenario ``key`` of ``lesson`` in its standard folder."""
    scenario_id = lesson.scenario_id(key)
    return build(app, lesson.scenarios[key], folder or scenario_id,
                 scenario_id=scenario_id, key=key, lesson_id=lesson.id,
                 seed=seed, reset=reset, typed=typed)


def lesson_scenario_info(app, lesson, key):
    """Info about scenario ``key`` of ``lesson`` in its standard folder."""
    return read_info(scenario_folder(app, lesson.scenario_id(key)))
