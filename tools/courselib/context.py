"""The check context: the one object a lesson's check function receives.

A check function looks at the learner's work through ``ctx`` (files, Git, the
facts of a built scenario, the learner's gates), may ask questions through it
(``ask`` and ``quiz`` have a right answer; ``choose`` is a free decision), and
reports through ``ctx.ok`` / ``ctx.fail`` / ``ctx.note``.  It never prints and
never writes.

Every helper that looks at something is safe to call on anything: a missing
file reads as "", a folder that is not a repository has no commits.  A broken
environment (no ``git``, a timeout) raises ``ToolTrouble``, which the runner
turns into 检查器出问题.

The full reference with examples is docs/authoring/tool-api.md.
"""

import collections
import copy
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .errors import Cancelled, CheckStop, ToolTrouble, UsageProblem
from .gitread import GitReader, GitRepo, RunResult
from .normalize import (
    choice_letter,
    index_to_letter,
    letter_to_index,
    matches,
    normalize,
    option_text_index,
    parse_int,
)
from .progress import gate_status
from .scenario import MARKER, lesson_scenario_info
from .syllabus import GATES
from .ui import one_line, visible

MAX_READ = 2 * 1024 * 1024
MAX_WALK = 2000
QUIZ_TRIES = 3

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "file_ok": "有这个文件：{label}",
    "file_missing_saw": "没有找到这个文件",
    "file_missing": "这个文件要存在（名字和位置都要对）",
    "file_is_dir_saw": "这个名字现在是一个文件夹",
    "file_is_dir": "这里需要的是文件，不是文件夹",
    "dir_ok": "有这个文件夹：{label}",
    "dir_missing_saw": "没有找到这个文件夹",
    "dir_missing": "这个文件夹要存在（名字和位置都要对）",
    "dir_is_file_saw": "这个名字现在是一个文件",
    "dir_is_file": "这里需要的是文件夹，不是文件",
    "gone_ok": "已经不在了：{label}",
    "gone_saw": "它还在",
    "gone_missing": "它不应该再留在这个位置",
    "repo_ok": "是一个 Git 仓库：{label}",
    "repo_no_saw": "这个文件夹还不是 Git 仓库",
    "repo_no": "要先把这个文件夹变成 Git 仓库",
    "repo_nested_saw": "这个文件夹自己不是仓库，它被包在另一个仓库里面（那个仓库的顶层是 {top}）",
    "repo_nested": "仓库要建在这个文件夹里，而不是它的上层文件夹里",
    "repo_damaged": "{label} 里有 .git，但 Git 认不出它，这个仓库可能损坏了。",
    "repo_damaged_recovery": (
        "先不要运行 git init。如果这是练习场里的仓库，可以重新搭一份练习场景；"
        "如果是你自己的仓库，把这一段发给导师。"
    ),
    "scenario_where": "练习场 {path}",
    "scenario_missing_saw": "还没有搭好这个练习场景",
    "scenario_missing": "先运行：python3 tools/course.py scenario {id}",
    "scenario_broken_saw": "这个练习场景没有搭完整",
    "scenario_broken": "重新搭一次：python3 tools/course.py scenario {id}",
    "ask_question": "问：{prompt}",
    "ask_prompt": "你的回答：",
    "ask_ok": "答对了：{q}",
    "ask_where": "问答题：{q}",
    "ask_saw": "你的回答是「{answer}」",
    "ask_saw_empty": "你没有输入内容",
    "ask_empty": "这一题要填一个回答（直接回车不算）。",
    "ask_empty_scripted": "--answer 给的回答是空的。问答题要写上回答，例如 --answer 3",
    "ask_missing": "这个回答和实际情况对不上。回到题目说的地方再看一次，然后重新运行检查",
    # No retest promise: an extra practice sitting has none (exam prints what comes next).
    "ask_missing_final": "这个回答和实际情况对不上，这一题记为还没达标。",
    "quiz_prompt": "你的选择（输入一个字母）：",
    "quiz_retry": "请输入 {first} 到 {last} 之间的一个字母。",
    "quiz_ok": "选对了：{q}",
    "quiz_where": "选择题：{q}",
    "quiz_saw": "你选的是 {letter}（{option}）",
    "quiz_saw_bad": "你的输入「{answer}」不是 {first} 到 {last} 之间的字母",
    "quiz_missing": "这一题还没选对。再想一想，重新运行检查",
    "quiz_missing_final": "这一题没有选对，记为还没达标。",
    "choose_ok": "你的决定：{label}",
    "choose_scripted_bad": (
        "--answer 给的「{answer}」不是 {first} 到 {last} 之间的字母，也不是哪个选项的原文。"
        "这一题要选一个选项，例如 --answer {first}"
    ),
    "unknown_gate": "检查函数问的关卡 {gate} 不存在",
    "need_answer": (
        "这个检查要回答问题，但现在是不提问模式（COURSE_NONINTERACTIVE=1）。"
        "用 --answer 按提问顺序给出回答，例如：--answer 3 --answer B"
    ),
    "bad_scenario_key": "检查函数用了这一课没有定义的场景：{key}",
    "no_scenario_key": "检查函数调用 ctx.scenario() 时没有说是哪个场景",
}


class CheckContext:
    """What a check function can see and say.  See the module docstring."""

    def __init__(self, app, lesson=None, station_id=None, answers=None,
                 scenario=None, state=None):
        self._app = app
        self._console = app.console
        self._lesson = lesson
        self._answers = list(answers or [])
        self._bound = scenario
        self._state = state if state is not None else {}
        self._reader = None
        self.station = station_id
        self.lesson_id = lesson.id if lesson is not None else ""
        self.now = app.now
        self.workspace = app.root
        self.home = app.home
        self.playground = app.playground
        self.my_site = app.my_site
        self.python = sys.executable
        self.last_answer = ""
        # collected results
        self.oks = []
        self.fails = []
        self.notes = []
        self.asked = []
        self.decisions = {}
        self.interactive = False
        self.answers_used = 0
        #: True when a wrong answer cannot be retried in this sitting (an exam
        #: task): ``ask`` and ``quiz`` then end their fail with 「…这一题记为
        #: 还没达标。」 instead of 「…重新运行检查」.  Set by the command, read here.
        self.final = False
        #: True when the check stopped because a scenario it needs is not
        #: built (completely): the result is 还没达标 but not an attempt.
        self.not_ready = False
        self._typed_live = False

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def ok(self, text):
        """Record one thing the learner got right (shown under 已经做到)."""
        self.oks.append(one_line(text))
        return True

    def fail(self, missing, where="", saw=""):
        """Record one thing that is not there yet.

        ``where`` says where the tool looked, ``saw`` what it found there and
        ``missing`` what is still needed.  Never put the solution in any of
        them: say what is missing, not which command produces it.
        """
        self.fails.append({"where": one_line(where), "saw": one_line(saw),
                           "missing": one_line(missing)})
        return False

    def note(self, text):
        """Add a neutral remark for the learner (it does not affect the outcome)."""
        self.notes.append(one_line(text))

    def expect(self, condition, ok, missing, where="", saw=""):
        """``ok(ok)`` when ``condition`` is true, else ``fail(missing, where, saw)``.

        Returns the truth value of ``condition``, so it can guard what follows.
        """
        if condition:
            return self.ok(ok)
        return self.fail(missing, where=where, saw=saw)

    @property
    def failed(self):
        """True when at least one ``fail`` has been recorded so far."""
        return bool(self.fails)

    def stop(self):
        """End the check here.  Whatever was recorded so far decides the outcome."""
        raise CheckStop()

    # ------------------------------------------------------------------
    # Paths and files (read-only)
    # ------------------------------------------------------------------
    def path(self, target):
        """An absolute Path.  "~/x" is relative to HOME, "x/y" to the workspace."""
        if isinstance(target, Path):
            return target if target.is_absolute() else self.workspace / target
        text = str(target)
        if text == "~" or text.startswith("~/"):
            return self._app.expand(text)
        path = Path(text)
        return path if path.is_absolute() else self.workspace / path

    def show(self, target, entrance=True):
        """The path as the learner should read it, with ``~`` for the home folder.

        The learning workspace and everything in it are shown through
        ``~/Developer/fullstack-from-zero`` whenever that path leads to it (the moved
        folder, or the entrance of a learner who stayed).  ``entrance=False``
        shows the real place, for a message about where the folder really is
        (for example a workspace still in a synced folder).
        """
        return self._app.show(self.path(target), entrance=entrance)

    def exists(self, target):
        return self.path(target).exists()

    def is_file(self, target):
        return self.path(target).is_file()

    def is_dir(self, target):
        return self.path(target).is_dir()

    def read_bytes(self, target, limit=MAX_READ):
        """The first ``limit`` bytes of a file; b"" when it cannot be read."""
        path = self.path(target)
        if not path.is_file():
            return b""
        try:
            with open(str(path), "rb") as handle:
                return handle.read(limit)
        except OSError:
            return b""

    def read(self, target, default=""):
        """The text of a file (UTF-8); ``default`` when it is missing or unreadable."""
        path = self.path(target)
        if not path.is_file():
            return default
        data = self.read_bytes(path)
        return data.decode("utf-8", "replace").lstrip("﻿")

    def lines(self, target):
        """The lines of a text file without their line ends; [] when missing."""
        return self.read(target).splitlines()

    def listdir(self, target, hidden=True):
        """Sorted names inside a folder; [] when it is missing.

        ``hidden=False`` leaves out names that start with a dot.
        """
        path = self.path(target)
        if not path.is_dir():
            return []
        try:
            names = sorted(os.listdir(str(path)))
        except OSError:
            return []
        return names if hidden else [name for name in names if not name.startswith(".")]

    def walk(self, target, everything=False):
        """Relative paths of all files below a folder, sorted ("a/b.txt").

        ``.git`` folders, ``.DS_Store`` and the tool's marker file are left
        out unless ``everything`` is true.  At most 2000 files are returned.
        """
        base = self.path(target)
        found = []
        if not base.is_dir():
            return found
        for folder, dirs, files in os.walk(str(base)):
            if not everything:
                dirs[:] = [d for d in dirs if d != ".git"]
            dirs.sort()
            for name in sorted(files):
                if not everything and name in (".DS_Store", MARKER):
                    continue
                full = Path(folder) / name
                found.append(full.relative_to(base).as_posix())
                if len(found) >= MAX_WALK:
                    return found
        return found

    def size(self, target):
        """Size of a file in bytes; None when it is not a file."""
        path = self.path(target)
        try:
            return path.stat().st_size if path.is_file() else None
        except OSError:
            return None

    def mtime(self, target):
        """When a file or folder was last modified (a datetime); None when missing."""
        try:
            return datetime.datetime.fromtimestamp(self.path(target).stat().st_mtime)
        except OSError:
            return None

    # -- worded expectations --------------------------------------------------
    def expect_file(self, target, label=None):
        """Record ok when the file exists, a worded fail otherwise.  Returns a bool."""
        path = self.path(target)
        label = label or self.show(path)
        if path.is_file():
            return self.ok(TEXT["file_ok"].format(label=label))
        if path.is_dir():
            return self.fail(TEXT["file_is_dir"], where=label, saw=TEXT["file_is_dir_saw"])
        return self.fail(TEXT["file_missing"], where=label, saw=TEXT["file_missing_saw"])

    def expect_dir(self, target, label=None):
        """Record ok when the folder exists, a worded fail otherwise.  Returns a bool."""
        path = self.path(target)
        label = label or self.show(path)
        if path.is_dir():
            return self.ok(TEXT["dir_ok"].format(label=label))
        if path.exists():
            return self.fail(TEXT["dir_is_file"], where=label, saw=TEXT["dir_is_file_saw"])
        return self.fail(TEXT["dir_missing"], where=label, saw=TEXT["dir_missing_saw"])

    def expect_missing(self, target, label=None):
        """Record ok when nothing is at this path any more.  Returns a bool."""
        path = self.path(target)
        label = label or self.show(path)
        if not path.exists() and not path.is_symlink():
            return self.ok(TEXT["gone_ok"].format(label=label))
        return self.fail(TEXT["gone_missing"], where=label, saw=TEXT["gone_saw"])

    def need_file(self, target, label=None):
        """Like ``expect_file`` but ends the check when the file is missing."""
        if not self.expect_file(target, label):
            self.stop()
        return self.path(target)

    def need_dir(self, target, label=None):
        """Like ``expect_dir`` but ends the check when the folder is missing."""
        if not self.expect_dir(target, label):
            self.stop()
        return self.path(target)

    def need_repo(self, target, label=None, praise=False):
        """Return the ``GitRepo`` at ``target``; end the check when it is not one.

        ``praise=True`` records 「是一个 Git 仓库：<label>」 under 已经做到; use
        it only where the learner made the repository in this very station or
        task (git init is part of what it asks).  A repository that a
        scenario, an exam task or an earlier lesson made is not praised.
        """
        path = self.path(target)
        label = label or self.show(path)
        if not path.is_dir():
            self.expect_dir(path, label)
            self.stop()
        repo = self.git(path)
        if repo.is_repo:
            if praise:
                self.ok(TEXT["repo_ok"].format(label=label))
            return repo
        if os.path.lexists(str(path / ".git")):
            # A .git that Git does not recognise: telling the learner "not a
            # repository yet" would lead to a git init over a damaged one.
            raise ToolTrouble(TEXT["repo_damaged"].format(label=label),
                              recovery=TEXT["repo_damaged_recovery"])
        if repo.inside_repo:
            self.fail(TEXT["repo_nested"], where=label,
                      saw=TEXT["repo_nested_saw"].format(top=self._app.show(repo.toplevel)))
        else:
            self.fail(TEXT["repo_no"], where=label, saw=TEXT["repo_no_saw"])
        self.stop()

    # ------------------------------------------------------------------
    # Git (read-only) and other programs
    # ------------------------------------------------------------------
    def _git_reader(self):
        if self._reader is None:
            self._reader = GitReader(self._app.child_env())
        return self._reader

    def git(self, target):
        """A read-only ``GitRepo`` view of the folder ``target``."""
        return GitRepo(self.path(target), self._git_reader())

    def git_global(self, key):
        """A value of the learner's global Git configuration; None when unset.

        Never put the value of user.name or user.email into a message.
        """
        return self._git_reader().global_config(key)

    def git_global_bool(self, key):
        """A global Git setting read as True/False; None when unset."""
        return self._git_reader().global_bool(key)

    def git_global_state(self, key):
        """A boolean global Git setting as "true", "false", "unset" or "invalid".

        "invalid" is a value Git cannot read as true or false (a typo such
        as ``commit.gpgsign=fasle``).  A global configuration file that Git
        cannot read at all raises (检查器出问题).
        """
        return self._git_reader().global_state(key)

    def git_global_all(self, key):
        """Every value of a multi-valued global Git setting, in order; [] when unset.

        Like ``git_global``: never put the values of user.name or user.email
        into a message.
        """
        return self._git_reader().global_all(key)

    def git_version(self):
        """The installed Git version, e.g. (2, 54, 0)."""
        return self._git_reader().version()

    def which(self, program):
        """Full path of ``program`` on the learner's PATH; None when not installed."""
        return shutil.which(program, path=self._app.env.get("PATH"))

    def env(self, name, default=""):
        """The value of an environment variable of the learner's shell."""
        return self._app.env.get(name, default)

    def run(self, argv, cwd=None, timeout=10, stdin_text=None):
        """Run a read-only command and return a ``RunResult``.

        ``argv`` is a list (no shell).  ``result.ok`` is False when the program
        is missing (``result.missing``), ran too long (``result.timed_out``)
        or ended with a non-zero code (``result.code``).  Use it to run the
        learner's own program or a read-only tool; use ``ctx.git`` for Git.

        ``timeout`` is clamped to 1-60 seconds.  A mistake in the check itself
        raises ``ValueError`` (which the learner sees as 检查器出问题): a
        string instead of a list, an empty list, or ``git`` as the program.
        """
        if isinstance(argv, str) or not argv:
            raise ValueError("ctx.run needs a list such as ['python3', 'convert.py']")
        if os.path.basename(str(argv[0])) == "git":
            raise ValueError("ctx.run must not run git: use ctx.git(path) (read-only)")
        try:
            timeout = min(60.0, max(1.0, float(timeout)))
        except (TypeError, ValueError):
            timeout = 10.0
        env = self._app.child_env()
        env.update({"PAGER": "cat", "GIT_PAGER": "cat", "PYTHONDONTWRITEBYTECODE": "1",
                    "GIT_OPTIONAL_LOCKS": "0"})
        try:
            done = subprocess.run(
                [str(item) for item in argv],
                cwd=str(self.path(cwd)) if cwd is not None else str(self.workspace),
                env=env, capture_output=True, timeout=timeout, check=False,
                input=stdin_text.encode("utf-8") if stdin_text is not None else None,
                stdin=subprocess.DEVNULL if stdin_text is None else None)
        except subprocess.TimeoutExpired as exc:
            return RunResult(-1, _decode(exc.stdout), _decode(exc.stderr), timed_out=True)
        except (OSError, ValueError) as exc:
            return RunResult(127, "", str(exc), missing=True)
        return RunResult(done.returncode, _decode(done.stdout), _decode(done.stderr))

    # ------------------------------------------------------------------
    # Scenarios
    # ------------------------------------------------------------------
    def scenario(self, key=None, required=True):
        """Info about a built scenario: ``.path``, ``.seed``, ``.facts``, ``.exists``.

        In a station check pass the scenario key ("start", "1.6b").  In the
        check of a ``do`` review item and in an exam grading function call it
        without arguments: it returns the scenario built for that task.

        When the scenario has not been built the check ends with a worded
        "not yet" that tells the learner the command to build it.  With
        ``required=False`` the info is returned instead (``.exists`` False).
        """
        bound = self._bound
        if bound is not None and (key is None or key == bound.key):
            return bound
        if self._lesson is None:
            raise ToolTrouble(TEXT["no_scenario_key"])
        if key is None:
            if self.station and self.station in self._lesson.scenarios:
                key = self.station
            else:
                raise ToolTrouble(TEXT["no_scenario_key"])
        if key not in self._lesson.scenarios:
            raise ToolTrouble(TEXT["bad_scenario_key"].format(key=key))
        info = lesson_scenario_info(self._app, self._lesson, key)
        if info.exists or not required:
            return info
        scenario_id = self._lesson.scenario_id(key)
        self.not_ready = True
        where = TEXT["scenario_where"].format(path=self._app.show(info.path))
        if info.started or info.path.exists():
            self.fail(TEXT["scenario_broken"].format(id=scenario_id), where=where,
                      saw=TEXT["scenario_broken_saw"])
        else:
            self.fail(TEXT["scenario_missing"].format(id=scenario_id), where=where,
                      saw=TEXT["scenario_missing_saw"])
        self.stop()

    # ------------------------------------------------------------------
    # Questions
    # ------------------------------------------------------------------
    def normalize(self, text, case=True):
        """Trim, convert full-width to half-width, lower-case (see normalize.py)."""
        return normalize(text, case=case)

    def parse_int(self, text):
        """Read a whole number from free text ("３ 个" -> 3); None when there is none."""
        return parse_int(text)

    def visible(self, text):
        """``text`` with invisible characters named, for ``saw=`` evidence.

        U+3000 -> 〔全角空格〕, a tab -> 〔Tab〕, U+00A0 -> 〔不换行空格〕,
        each ASCII space at the end of a line -> ·.
        """
        return visible(text)

    def _take(self, question_lines, prompt):
        self.interactive = True
        if not self._answers and not self._console.can_prompt:
            raise UsageProblem(TEXT["need_answer"])
        for line in question_lines:
            self._console.out(line)
        if self._answers:
            answer = self._answers.pop(0)
            self.answers_used += 1
            self._typed_live = False
            self._console.out(prompt + str(answer))
            return str(answer)
        self._typed_live = True
        return self._console.read(prompt)

    def ask(self, prompt, expected):
        """Ask a question whose answer the learner gets by doing the task.

        ``expected`` is a string, an int, a compiled regular expression, a
        function ``f(normalised_answer) -> bool`` or a list of those (any may
        match); see ``normalize.matches``.  Compute it from the learner's real
        files or from ``ctx.scenario(...).facts``; never hard-code something a
        learner could copy from the lesson text.

        Records ok or a worded fail (the expected answer is never shown) and
        returns True or False.  The typed answer is kept in ``ctx.last_answer``.
        """
        question = one_line(prompt, limit=60)
        lines = ["", TEXT["ask_question"].format(prompt=str(prompt).strip())]
        answer = ""
        for attempt in range(QUIZ_TRIES):
            answer = self._take(lines if attempt == 0 else [], TEXT["ask_prompt"])
            if normalize(answer) or not self._typed_live:
                break
            self._console.out(TEXT["ask_empty"])
        if not normalize(answer):
            # Nothing typed (Enter pressed): not an answer, so not an attempt.
            if self._typed_live:
                raise Cancelled()
            raise UsageProblem(TEXT["ask_empty_scripted"])
        self.last_answer = normalize(answer, case=False)
        good = matches(answer, expected)
        self.asked.append({"kind": "ask", "prompt": question,
                           "answer": self.last_answer, "correct": good})
        if good:
            return self.ok(TEXT["ask_ok"].format(q=question))
        saw = (TEXT["ask_saw"].format(answer=self.last_answer) if self.last_answer
               else TEXT["ask_saw_empty"])
        missing = TEXT["ask_missing_final"] if self.final else TEXT["ask_missing"]
        return self.fail(missing, where=TEXT["ask_where"].format(q=question), saw=saw)

    def quiz(self, question, options, answer, explain="", feedback=None):
        """Ask one multiple-choice question; returns True when answered correctly.

        ``options`` is a list of 2 to 6 strings shown as A, B, C ...;
        ``answer`` is the letter of the correct one ("B").  ``explain`` is
        shown after a correct answer.  ``feedback`` maps the letter of a wrong
        option to a sentence shown when the learner picks it: say why that
        option is wrong without naming the right one.
        """
        if not isinstance(options, (list, tuple)):
            raise ValueError("quiz options must be a list of 2 to 6 non-empty strings")  # noqa: TRY004
        options = list(options)
        correct = letter_to_index(answer)
        if not 2 <= len(options) <= 6 or not all(isinstance(o, str) and o.strip() for o in options):
            raise ValueError("quiz options must be a list of 2 to 6 non-empty strings")
        if correct is None or correct >= len(options):
            raise ValueError(f"quiz answer must be the letter of one option, got {answer!r}")
        feedback = {str(k).strip().upper(): v for k, v in (feedback or {}).items()}
        short = one_line(question, limit=60)
        first, last = "A", index_to_letter(len(options) - 1)
        lines = ["", TEXT["ask_question"].format(prompt=str(question).strip())]
        lines += [f"  {index_to_letter(i)}. {option}" for i, option in enumerate(options)]
        chosen = None
        typed = ""
        for attempt in range(QUIZ_TRIES):
            typed = self._take(lines if attempt == 0 else [], TEXT["quiz_prompt"])
            chosen = _read_choice(typed, options)
            if chosen is not None or not self._typed_live:
                break
            self._console.out(TEXT["quiz_retry"].format(first=first, last=last))
        self.last_answer = normalize(typed, case=False)
        good = chosen == correct
        self.asked.append({"kind": "quiz", "prompt": short, "correct": good,
                           "answer": index_to_letter(chosen) if chosen is not None
                           else self.last_answer})
        if good:
            self.ok(TEXT["quiz_ok"].format(q=short))
            if explain:
                self.note(explain)
            return True
        if chosen is None:
            saw = TEXT["quiz_saw_bad"].format(answer=self.last_answer, first=first, last=last)
        else:
            saw = TEXT["quiz_saw"].format(letter=index_to_letter(chosen),
                                          option=one_line(options[chosen], limit=40))
        missing = TEXT["quiz_missing_final"] if self.final else TEXT["quiz_missing"]
        if chosen is not None and feedback.get(index_to_letter(chosen)):
            reason = one_line(feedback[index_to_letter(chosen)])
            if reason and reason[-1] not in "。！？!?.；;":
                reason += "。"
            missing = reason + missing
        return self.fail(missing, where=TEXT["quiz_where"].format(q=short), saw=saw)

    def choose(self, question, options, key=None, explain="", feedback=None):
        """Let the learner make a free choice; there is no right or wrong answer.

        ``options`` is a list of 2 to 6 labels (strings), or of
        ``(value, label)`` pairs when the stored value should differ from what
        the learner reads.  The options are shown as A, B, C ... and read like
        a quiz answer (``b``, ``Ｂ``, ``选 B`` or the exact text of an option).

        Records 「你的决定：<label>」 under 已经做到 (never 答对了 or a fail),
        and, when ``key`` is given, the value as ``decisions[key]`` (saved
        like ``ctx.decide`` when this check passes).  ``explain`` is shown as
        a note after any choice; ``feedback`` maps a letter to a note shown
        when that option is chosen.  Returns the chosen value (the label for
        plain strings).

        An answer that names no option is asked again at the terminal (three
        times, then the check is cancelled); from ``--answer`` it is a usage
        error.  A malformed question raises (检查器出问题).
        """
        pairs = _choice_pairs(options)
        labels = [label for _value, label in pairs]
        if key is not None and (not isinstance(key, str) or not key.strip()):
            raise ValueError("choose key must be a non-empty string such as 'workspace_location'")
        feedback = {str(k).strip().upper(): v for k, v in (feedback or {}).items()}
        first, last = "A", index_to_letter(len(pairs) - 1)
        lines = ["", TEXT["ask_question"].format(prompt=str(question).strip())]
        lines += [f"  {index_to_letter(i)}. {label}" for i, label in enumerate(labels)]
        chosen = None
        typed = ""
        for attempt in range(QUIZ_TRIES):
            typed = self._take(lines if attempt == 0 else [], TEXT["quiz_prompt"])
            chosen = _read_choice(typed, labels)
            if chosen is not None:
                break
            if not self._typed_live:
                raise UsageProblem(TEXT["choose_scripted_bad"].format(
                    answer=one_line(typed, limit=30), first=first, last=last))
            if attempt + 1 < QUIZ_TRIES:
                self._console.out(TEXT["quiz_retry"].format(first=first, last=last))
        if chosen is None:
            # Three answers that name no option: not a decision, not an attempt.
            raise Cancelled()
        value, label = pairs[chosen]
        letter = index_to_letter(chosen)
        self.last_answer = normalize(typed, case=False)
        self.asked.append({"kind": "choose", "prompt": one_line(question, limit=60),
                           "answer": letter, "choice": one_line(label, limit=60)})
        if key is not None:
            self.decisions[key.strip()] = value
        self.ok(TEXT["choose_ok"].format(label=one_line(label, limit=60)))
        if feedback.get(letter):
            self.note(feedback[letter])
        if explain:
            self.note(explain)
        return value

    # ------------------------------------------------------------------
    # Learner state (read-only) and decisions
    # ------------------------------------------------------------------
    @property
    def state(self):
        """A copy of learner/state.json as a dict (changes to it are ignored)."""
        return copy.deepcopy(self._state)

    def passed(self, station_id):
        """True when the learner has passed the check of ``station_id``."""
        record = self._state.get("stations", {}).get(station_id) or {}
        return bool(record.get("first_pass"))

    def decision(self, key, default=None):
        """A decision recorded earlier (``decisions`` in the state file)."""
        return self._state.get("decisions", {}).get(key, default)

    def decide(self, key, value):
        """Record a decision of the learner; it is saved when this check passes."""
        self.decisions[str(key)] = value

    # ------------------------------------------------------------------
    # Gates (read-only)
    # ------------------------------------------------------------------
    def _gate_status(self, gate_id):
        catalog = self._app.catalog()
        gate = str(gate_id)
        if gate not in catalog.gate_ids():
            raise ToolTrouble(TEXT["unknown_gate"].format(gate=gate))
        return catalog, gate_status(catalog, self._state, gate)

    def gate_done(self, gate_id):
        """True when the gate is passed (the rule of ``exam``, COMMON.md section 1).

        Every lesson the gate covers has a passed task, and the explain-back
        questions are recorded as passed (``exam <gate> --explain pass``).
        """
        return self._gate_status(gate_id)[1].done

    def gate_result(self, gate_id):
        """A read-only ``GateResult`` of one gate, so a check can say what is missing.

        Fields: ``gate``, ``title``, ``attempts``, ``passed``, ``open``,
        ``open_titles``, ``done``, ``in_progress``, ``tasks``,
        ``practical_done``, ``explain``, ``explain_date``, ``lessons``,
        ``open_lessons``, ``open_lesson_titles``, ``next_count``,
        ``next_minutes`` (see ``GateResult``).
        """
        catalog, summary = self._gate_status(gate_id)
        gate = summary.gate
        primary, _secondary, _unusable = catalog.gate_pool(gate)
        titles = {t["id"]: str(t.get("title", "")) for _l, t in primary}

        def lesson_title(lesson_id):
            lesson = catalog.lesson(lesson_id)
            return lesson.title if lesson is not None else ""

        return GateResult(
            gate=gate, title=GATES.get(gate, {}).get("title", ""),
            attempts=summary.attempts, passed=tuple(summary.passed),
            open=tuple(summary.open),
            open_titles=tuple(titles.get(task_id, "") for task_id in summary.open),
            done=summary.done, in_progress=summary.in_progress, tasks=summary.tasks,
            practical_done=summary.practical_done, explain=summary.explain,
            explain_date=summary.explain_date, lessons=tuple(summary.lessons),
            open_lessons=tuple(summary.open_lessons),
            open_lesson_titles=tuple(lesson_title(l) for l in summary.open_lessons),
            next_count=summary.next_count, next_minutes=summary.next_minutes)


def _decode(data):
    if not data:
        return ""
    return data[:MAX_READ].decode("utf-8", "replace")


def _read_choice(typed, labels):
    """The index of the option ``typed`` names (a letter or its text), or None.

    The text is compared with dots folded (``normalize.fold_dots``), so
    「惯例.事实标准」 names 「惯例·事实标准」.
    """
    chosen = choice_letter(typed, len(labels))
    if chosen is None:
        chosen = option_text_index(typed, labels)
    return chosen


def _choice_pairs(options):
    """``[(value, label)]`` for the options of ``ctx.choose``; raises when malformed."""
    problem = "choose options must be a list of 2 to 6 labels or (value, label) pairs"
    if not isinstance(options, (list, tuple)) or not 2 <= len(options) <= 6:
        raise ValueError(problem)
    pairs = []
    for option in options:
        if isinstance(option, str):
            value, label = option, option
        elif isinstance(option, (list, tuple)) and len(option) == 2:
            value, label = option
        else:
            raise ValueError(problem)
        if not isinstance(label, str) or not label.strip():
            raise ValueError(problem)
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            raise ValueError("choose values must be strings, numbers, True/False or None")
        pairs.append((value, label))
    if len({normalize(label) for _value, label in pairs}) != len(pairs):
        raise ValueError("choose options must have different labels")
    return pairs


#: What ``ctx.gate_result(gate)`` returns: a read-only summary of one gate.
#: ``attempts`` (int) sittings started; ``passed`` (task ids passed);
#: ``open`` / ``open_titles`` (tasks tried without a pass in lessons not
#: passed yet: what to practise; each comes back in its other form);
#: ``done`` (the gate is passed: ``practical_done`` and ``explain == "pass"``,
#: the same as ``ctx.gate_done``); ``in_progress`` (a sitting has tasks not
#: graded yet); ``tasks`` (usable tasks of the gate); ``practical_done``
#: (every lesson of the gate has a passed task); ``explain`` ("pass",
#: "again" or None) and ``explain_date`` (ISO date or None): the recorded
#: verdict of the explain-back questions; ``lessons`` (lesson ids the gate
#: covers); ``open_lessons`` / ``open_lesson_titles`` (lessons without a
#: passed task yet); ``next_count`` / ``next_minutes`` (tasks and expected
#: minutes of the next sitting; 0 when the practical part is passed).
#: Every sequence is a tuple in learning order.
GateResult = collections.namedtuple(
    "GateResult",
    "gate title attempts passed open open_titles done in_progress tasks"
    " practical_done explain explain_date lessons open_lessons open_lesson_titles"
    " next_count next_minutes")
