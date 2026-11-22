"""Shared helpers for the tests of tools/course.py.

Every test works in a throw-away sandbox under the temporary folder ($TMPDIR):
a fake workspace, a fake home directory and (inside it) the playground.  The
real home directory, the real Git configuration and the real workspace are
never touched.

Run the suite from the workspace root:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/tests
"""

import sys

sys.dont_write_bytecode = True

import atexit
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

TESTS = Path(__file__).resolve().parent
TOOLS = TESTS.parent
REPO = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from courselib import cli, syllabus
from courselib.app import App
from courselib.ui import Console

EXAMPLE = REPO / "docs" / "authoring" / "example-lesson"
EXAMPLE_STAGE = "99-example"
EXAMPLE_FOLDER = "01-notes-repo"
NOW = "2026-11-19T10:00:00"
LEARNER = ["-c", "commit.gpgsign=false", "-c", "user.name=Learner",
           "-c", "user.email=learner@example.com"]


def _remove_bytecode():
    """Leave no __pycache__ behind in the tools folder, whatever started the tests."""
    for folder in list(TOOLS.rglob("__pycache__")):
        shutil.rmtree(str(folder), ignore_errors=True)


atexit.register(_remove_bytecode)


class Result:
    """Exit code and captured output of one run of the tool."""

    def __init__(self, code, out, err=""):
        self.code = code
        self.out = out
        self.err = err

    @property
    def text(self):
        return self.out + self.err

    def __repr__(self):
        return f"<Result code={self.code}>\n--- out\n{self.out}\n--- err\n{self.err}"


RULE_CARD = """### {rule} 示例规则 {rule}

- **约束力**：{level}（适用范围：所有项目）
- **规则类型**：{kind}
- **规则**：一句话说清这条规则。
- **谁说的**：示例出处 第 1 版 https://example.com/{rule}
- **核对日期**：2026-11-19；**复核周期**：12 个月
- **谁来管**：评审人；**不遵守的后果**：别人看不懂你的改动。
- **为什么**：不这样做会出事。
- **正例**：`正例`
- **反例**：`反例`
- **怎么检查**：人工检查：看一遍
- **例外**：无
- **旧教程提醒**：无
- **学于**：{lesson}
"""

#: A concrete 规则类型 for each family that plan section 4 gives in brackets.
FAMILY_TYPE = {"惯例": "惯例·平台与工具"}


LESSON_TEMPLATE = '''"""A generated test lesson."""

META = {{
    "id": "{id}",
    "slug": "{folder}",
    "title": "{title}",
    "stage": {stage},
    "prerequisites": [],
    "stations": [
{stations}
    ],
    "rules": {rules!r},
    "verified": {{"date": "2026-11-19", "tools": {{"git": "2.54.0"}}}},
    "unverified_steps": [],
}}

TERMS = [{{"term": "术语 {id}", "en": "term", "plain": "一句大白话", "first": "{id}a"}}]


def _flag_check(ctx):
    """Passes when the test has created <playground>/flags/<station>.ok."""
    flag = ctx.playground / "flags" / (ctx.station + ".ok")
    if ctx.is_file(flag):
        ctx.ok("找到了完成标记")
    else:
        ctx.fail("还没有完成标记", where="练习场的 flags 文件夹", saw="没有 " + flag.name)


checks = {{{check_map}}}

HINTS = {{
{hints}
}}

REVIEW = [
    {{"id": "{id}-r1", "type": "recall", "tier": "fluent", "q": "问题 {id}？", "a": "答案 {id}。"}},
    {{"id": "{id}-r2", "type": "which", "tier": "fluent", "station": "{id}a",
      "q": "选哪个？", "options": ["甲", "乙", "丙"], "answer": "B"}},
]


def build_start(sc):
    sc.write("hello.txt", "你好")
    sc.fact("lesson", "{id}")


SCENARIOS = {{"start": build_start}}

EXAM = []
{extra}
'''


def lesson_source(lesson_id, folder, title="测试课", letters="ab", rules=(), extra="",
                  minutes=20):
    """Source text of a small valid lesson module."""
    stage = int(lesson_id.split(".")[0])
    stations = []
    hints = []
    checks = []
    for letter in letters:
        station = lesson_id + letter
        stations.append(
            f'        {{"id": "{station}", "title": "第 {letter} 站", "minutes": {minutes}, '
            f'"new_concept": "概念 {station}", "new_commands": ["cmd-{station}"]}},')
        hints.append(
            f'    "{station}": ["方向 {station}", "位置 {station}", "相似例子 {station}", "答案与解释 {station}"],')
        checks.append(f'"{station}": _flag_check')
    return LESSON_TEMPLATE.format(
        id=lesson_id, folder=folder, title=title, stage=stage,
        stations="\n".join(stations), rules=list(rules), check_map=", ".join(checks),
        hints="\n".join(hints), extra=extra)


class Sandbox:
    """A fake workspace with its own home, playground and clock."""

    def __init__(self, test, example=False):
        self.base = Path(tempfile.mkdtemp(prefix="course-test-"))
        test.addCleanup(shutil.rmtree, str(self.base), True)
        # macOS: the temp folder is reached through a link (/tmp -> /private/tmp)
        self.base = Path(os.path.realpath(str(self.base)))
        self.root = self.base / "workspace"
        self.home = self.base / "home"
        self.playground = self.home / "Developer" / "playground"
        (self.root / "stages").mkdir(parents=True)
        (self.home / "Developer").mkdir(parents=True)
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.home),
            "TMPDIR": tempfile.gettempdir(),
            "LANG": "C.UTF-8",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "COURSE_NOW": NOW,
        }
        self._tools_installed = False
        if example:
            self.add_example()

    # -- lessons ------------------------------------------------------------
    def add_lesson(self, source, stage_folder, folder, rules_text=None, text=None):
        target = self.root / "stages" / stage_folder / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / "lesson.py").write_text(source, encoding="utf-8")
        if rules_text is not None:
            (target / "rules.md").write_text(rules_text, encoding="utf-8")
        if text is not None:
            (target / "lesson.md").write_text(text, encoding="utf-8")
        return target

    def add_example(self):
        target = self.root / "stages" / EXAMPLE_STAGE / EXAMPLE_FOLDER
        shutil.copytree(str(EXAMPLE), str(target))
        return target

    def add_syllabus_lesson(self, lesson_id, extra="", minutes=20):
        """A valid generated lesson for an id of plan section 4 (folder, stations, rules)."""
        entry = syllabus.lesson_entry(lesson_id)
        letters = "".join(station[-1] for station in entry["stations"])
        source = lesson_source(lesson_id, entry["folder"], title=entry["title"],
                               letters=letters, rules=sorted(entry["rules"]), extra=extra,
                               minutes=minutes)
        cards = "\n".join(
            RULE_CARD.format(rule=rule, lesson=lesson_id,
                             level=labels.get("level", "必须"),
                             kind=FAMILY_TYPE.get(labels.get("kind", "惯例"),
                                                  labels.get("kind", "惯例")))
            for rule, labels in sorted(entry["rules"].items()))
        return self.add_lesson(source, entry["stage_folder"], entry["folder"],
                               rules_text=cards if entry["rules"] else None)

    def flag(self, station_id):
        """Make the generated check of ``station_id`` pass."""
        folder = self.playground / "flags"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (station_id + ".ok")).write_text("ok\n", encoding="utf-8")

    # -- running the tool in this process -------------------------------------
    def environment(self, now=None, noninteractive=False, **extra):
        env = dict(self.env)
        if now:
            env["COURSE_NOW"] = now
        if noninteractive:
            env["COURSE_NONINTERACTIVE"] = "1"
        env.update(extra)
        return env

    def run(self, *argv, inputs=None, tty=False, noninteractive=False, now=None, **extra):
        """Run ``course.py <argv>`` in this process; returns a ``Result``.

        ``inputs`` is what the learner types at prompts, in order; when it runs
        out the next prompt gets end-of-file.  Put ``KeyboardInterrupt`` in the
        list to press Ctrl+C at that prompt.
        """
        out, err = io.StringIO(), io.StringIO()
        feed = list(inputs or [])

        def reader(prompt):
            out.write(prompt)
            if not feed:
                raise EOFError()
            item = feed.pop(0)
            if item is KeyboardInterrupt:
                raise KeyboardInterrupt()
            out.write(str(item) + "\n")
            return str(item)

        console = Console(out=out, err=err, reader=reader, color=False,
                          can_prompt=not noninteractive, is_tty=tty)
        code = cli.main([str(arg) for arg in argv], root=self.root,
                        env=self.environment(now, noninteractive, **extra), console=console)
        return Result(code, out.getvalue(), err.getvalue())

    def app(self, now=None, inputs=None, noninteractive=True):
        """An ``App`` on this sandbox for tests of the library itself."""
        out = io.StringIO()
        feed = list(inputs or [])

        def reader(prompt):
            out.write(prompt)
            if not feed:
                raise EOFError()
            return str(feed.pop(0))

        console = Console(out=out, err=out, reader=reader, color=False,
                          can_prompt=not noninteractive or bool(inputs), is_tty=False)
        app = App(self.root, env=self.environment(now), console=console)
        app.test_output = out
        return app

    # -- running the tool as a separate process -------------------------------
    def install_tools(self):
        """Copy course.py and courselib into the fake workspace (for subprocess runs)."""
        if not self._tools_installed:
            shutil.copytree(str(TOOLS), str(self.root / "tools"),
                            ignore=shutil.ignore_patterns("__pycache__", "tests", "*.pyc"))
            self._tools_installed = True
        return self.root / "tools" / "course.py"

    def run_process(self, *argv, stdin_text="", python=None, cwd=None, now=None,
                    noninteractive=False, **extra):
        """Run ``python3 tools/course.py <argv>`` as a child process."""
        script = self.install_tools()
        done = subprocess.run(
            [python or sys.executable, str(script)] + [str(arg) for arg in argv],
            input=stdin_text.encode("utf-8"), capture_output=True, check=False,
            cwd=str(cwd or self.base), env=self.environment(now, noninteractive, **extra),
            timeout=120)
        return Result(done.returncode, done.stdout.decode("utf-8", "replace"),
                      done.stderr.decode("utf-8", "replace"))

    # -- looking at what the tool wrote ---------------------------------------
    def state(self):
        return json.loads((self.root / "learner" / "state.json").read_text(encoding="utf-8"))

    def events(self, kind=None):
        path = self.root / "learner" / "log.jsonl"
        if not path.exists():
            return []
        events = []
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict):
                events.append(event)
        return [e for e in events if kind is None or e.get("type") == kind]

    def last_result(self):
        return json.loads((self.root / "learner" / "last-result.json").read_text(encoding="utf-8"))

    # -- acting as the learner ------------------------------------------------
    def git(self, repo, *args, check=True):
        """Run git in ``repo`` the way the learner would (own identity, no signing)."""
        done = subprocess.run(["git"] + LEARNER + [str(arg) for arg in args], cwd=str(repo),
                              env=self.environment(), capture_output=True, check=False,
                              timeout=60)
        if check and done.returncode != 0:
            raise AssertionError("git {} failed: {}".format(
                " ".join(str(a) for a in args), done.stderr.decode("utf-8", "replace")))
        return done.stdout.decode("utf-8", "replace")

    def write_gitconfig(self, text):
        (self.home / ".gitconfig").write_text(text, encoding="utf-8")

    def build_scenario(self, text, seed=1, reset=False):
        """Build a lesson scenario through the library (the command is a plug-in)."""
        from courselib import scenario
        app = self.app()
        lesson, key, _ = app.catalog().scenario(text)
        return scenario.build_lesson_scenario(app, lesson, key, seed=seed, reset=reset)


def find_python39():
    """A Python 3.9 interpreter for compatibility tests, or None."""
    if sys.version_info[:2] == (3, 9):
        return sys.executable
    for candidate in ("/Library/Developer/CommandLineTools/usr/bin/python3",
                      "/Applications/Xcode.app/Contents/Developer/usr/bin/python3",
                      "/usr/bin/python3"):
        try:
            done = subprocess.run([candidate, "-c", "import sys; print(sys.version_info[:2])"],
                                  capture_output=True, check=False, timeout=20)
        except (OSError, subprocess.SubprocessError):
            continue
        if done.returncode == 0 and done.stdout.strip() == b"(3, 9)":
            return candidate
    return None
