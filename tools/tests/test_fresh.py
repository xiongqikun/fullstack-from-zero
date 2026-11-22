"""The ``fresh`` command: installed versions against tools/courselib/baseline.json.

PATH holds only stub programs (tests/envstubs.py), so every version the
command sees is the one the test installed.  No network, no real tools.
"""

import json
import re
import unittest
from unittest import mock

import envstubs
import helpers

from courselib import syllabus
from courselib.commands import fresh

#: What ``gh --version`` prints (format of the release notes of GitHub CLI 2.105.0).
GH_PRINTS = "gh version 2.105.0 (2026-11-17)\nhttps://github.com/cli/cli/releases/tag/v2.105.0"

BASELINE = json.loads((helpers.TOOLS / "courselib" / "baseline.json").read_text(encoding="utf-8"))


class BaselineFileTest(unittest.TestCase):
    def test_the_versions_verified_today(self):
        self.assertEqual(BASELINE["verified_on"], "2026-11-19")
        versions = {name: entry["version"] for name, entry in BASELINE["tools"].items()}
        self.assertEqual(versions, {
            "macos": "27.2.1", "zsh": "5.9", "git": "2.54.0", "python3": "3.14.9",
            "code": "1.145.2", "uv": "0.13.5", "ruff": "0.17.2", "node": "26.12.0",
            "npm": "11.20.0", "brew": "7.0.10", "gh": "2.105.0"})
        # gh is not installed on the reference Mac (plan G7): lesson 1.11 installs
        # it, and its version was read from the official release page (E6).
        gh = BASELINE["tools"]["gh"]
        self.assertEqual(gh["installed_in"], "1.11")
        self.assertIn("https://github.com/cli/cli/releases/latest", gh["note"])
        self.assertIn("2026-11-19", gh["note"])

    def test_names_and_patterns(self):
        for name, entry in BASELINE["tools"].items():
            with self.subTest(tool=name):
                self.assertIn(name, syllabus.TOOL_NAMES)
                self.assertIsInstance(entry["command"], list)
                pattern = re.compile(entry["pattern"], re.MULTILINE)
                # the pattern recognises what the reference Mac printed (plan G7)
                printed = dict(envstubs.VERSIONS, git="git version 2.54.0 (Apple Git-157)")
                printed.setdefault("gh", GH_PRINTS)
                stub = printed["sw_vers" if name == "macos" else name]
                match = pattern.search(stub)
                self.assertIsNotNone(match, stub)
                self.assertEqual(match.group(1), entry["version"])
        fresh.load_baseline(fresh.BASELINE)


class ClassifyTest(unittest.TestCase):
    def test_classes(self):
        cases = [
            ("2.54.0", "2.54.0", fresh.SAME),
            ("5.9", "5.9.0", fresh.SAME),
            ("2.54.0", "2.56.1", fresh.MINOR),
            ("2.54.0", "2.53.0", fresh.MINOR),
            ("1.145.2", "1.147.0", fresh.MINOR),
            ("27.2.1", "27.3", fresh.MINOR),
            ("2.54.0", "3.0.0", fresh.MAJOR),
            ("26.12.0", "27.0.0", fresh.MAJOR),
            ("0.13.5", "0.13.9", fresh.MINOR),
            ("0.13.5", "0.14.0", fresh.MAJOR),
            ("0.17.2", "1.0.0", fresh.MAJOR),
        ]
        for base, found, expected in cases:
            with self.subTest(base=base, found=found):
                self.assertEqual(fresh.classify(fresh.parse_version(base),
                                                fresh.parse_version(found)), expected)

    def test_parse_version(self):
        self.assertEqual(fresh.parse_version("v26.12.0"), (26, 12, 0))
        self.assertEqual(fresh.parse_version("7"), (7,))
        self.assertIsNone(fresh.parse_version("no digits here"))
        self.assertIsNone(fresh.parse_version(""))


class FreshCommandTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.bin = envstubs.FakeBin(self.box.base / "bin")

    def install(self, skip=(), **override):
        for name, text in envstubs.VERSIONS.items():
            if name in skip:
                continue
            self.bin.prints(name, override.get(name, text))
        self.bin.prints("git", override.get("git", "git version 2.54.0 (Apple Git-157)"))

    def lesson(self, lesson_id, tools):
        entry = syllabus.lesson_entry(lesson_id)
        letters = "".join(station[-1] for station in entry["stations"])
        source = helpers.lesson_source(lesson_id, entry["folder"], title=entry["title"],
                                       letters=letters)
        old = '"tools": {"git": "2.54.0"}'
        self.assertIn(old, source)
        source = source.replace(old, '"tools": ' + json.dumps(tools))
        self.box.add_lesson(source, entry["stage_folder"], entry["folder"])

    def fresh(self, **env):
        values = {"PATH": str(self.bin)}
        values.update(env)
        result = self.box.run("fresh", **values)
        self.assertNotIn("Traceback", result.text)
        return result

    def row(self, result, label):
        for line in result.out.splitlines():
            if line.startswith("  " + label + " "):
                return " ".join(line.split())
        self.fail(f"no row for {label!r} in\n{result.out}")

    # -- everything as verified -------------------------------------------------
    def test_all_versions_as_verified(self):
        self.install()
        self.lesson("1.6", {"git": "2.54.0", "python3": "3.14.9"})
        result = self.fresh()
        self.assertEqual(result.code, 0, result)
        self.assertTrue(result.out.startswith("版本核对 · 2026-11-19\n"))
        self.assertIn("用下面这些版本核对的", result.out)
        self.assertEqual(self.row(result, "Git"), "Git 2.54.0 2.54.0 一致")
        self.assertEqual(self.row(result, "zsh"), "zsh 5.9 5.9 一致")
        self.assertEqual(self.row(result, "VS Code（code 命令）"), "VS Code（code 命令） 1.145.2 1.145.2 一致")
        self.assertEqual(self.row(result, "uv"), "uv 0.13.5 0.13.5 一致")
        self.assertIn("可能受影响的课：没有。", result.out)
        # gh is not there before lesson 1.11: not a problem, no 说明 line.
        self.assertEqual(self.row(result, "GitHub CLI（gh 命令）"),
                         "GitHub CLI（gh 命令） 2.105.0 - 还没安装（第 1.11 课会装）")
        self.assertNotIn("说明：", result.out)
        self.assertTrue(result.out.rstrip().endswith(
            "下一步：装了的工具都和课程核对时一样，不用做什么。还没安装的，到了上面写的那一课会带你装。"))

    def test_everything_installed_and_as_verified(self):
        self.install()
        self.bin.prints("gh", GH_PRINTS)
        result = self.fresh()
        self.assertEqual(self.row(result, "GitHub CLI（gh 命令）"),
                         "GitHub CLI（gh 命令） 2.105.0 2.105.0 一致")
        self.assertTrue(result.out.rstrip().endswith("下一步：所有工具都和课程核对时一样，不用做什么。"))

    def pass_lesson_1_11(self, stations=("1.11a", "1.11b", "1.11c")):
        (self.box.root / "learner").mkdir(exist_ok=True)
        state = {"schema": 1, "stations": {
            station: {"status": "passed", "attempts": 1, "first_pass": "2026-11-20T10:00:00"}
            for station in stations}}
        (self.box.root / "learner" / "state.json").write_text(json.dumps(state), encoding="utf-8")

    def test_a_tool_still_missing_after_the_lesson_that_installs_it(self):
        self.install()
        self.lesson("1.12", {"gh": "2.105.0"})
        self.pass_lesson_1_11(stations=("1.11a", "1.11b"))
        self.assertIn("还没安装（第 1.11 课会装）", self.fresh().out)
        self.pass_lesson_1_11()
        result = self.fresh()
        self.assertEqual(self.row(result, "GitHub CLI（gh 命令）"), "GitHub CLI（gh 命令） 2.105.0 - 没装")
        self.assertIn("GitHub CLI（gh 命令）：在 PATH 里找不到 gh 命令。", result.out)
        self.assertIn("  - 1.12 第一次推送和云端备份：GitHub CLI（gh 命令）（没装）", result.out)
        self.assertTrue(result.out.rstrip().endswith("下一步：把这段发给导师，说“帮我核实受影响的课”。"))

    def test_a_bad_installed_in_is_a_broken_baseline(self):
        entry = dict(BASELINE["tools"]["gh"], installed_in="第 1.11 课")
        broken = self.box.base / "baseline.json"
        broken.write_text(json.dumps(dict(BASELINE, tools={"gh": entry})), encoding="utf-8")
        with mock.patch.object(fresh, "BASELINE", broken):
            self.assertEqual(self.fresh().code, 2)

    # -- each kind of drift -------------------------------------------------------
    def test_every_class_of_drift(self):
        self.install(skip=("ruff",), python3="Python 3.14.10", node="v27.0.0",
                     uv="uv 0.14.0 (Homebrew 2026-12-01 aarch64-apple-darwin)",
                     git="git version 2.53.0", code="garbage output", npm="12.2.3")
        self.bin.prints("brew", "", code=1)
        result = self.fresh()
        self.assertEqual(result.code, 0, result)
        self.assertEqual(self.row(result, "Python（第一个 python3）"),
                         "Python（第一个 python3） 3.14.9 3.14.10 小版本变了（比课程新）")
        self.assertEqual(self.row(result, "Git"), "Git 2.54.0 2.53.0 小版本变了（比课程旧）")
        self.assertEqual(self.row(result, "Node.js"), "Node.js 26.12.0 27.0.0 大版本变了（比课程新）")
        self.assertEqual(self.row(result, "npm"), "npm 11.20.0 12.2.3 大版本变了（比课程新）")
        self.assertEqual(self.row(result, "uv"), "uv 0.13.5 0.14.0 大版本变了（比课程新）")
        self.assertEqual(self.row(result, "Ruff"), "Ruff 0.17.2 - 没装")
        self.assertEqual(self.row(result, "VS Code（code 命令）"), "VS Code（code 命令） 1.145.2 - 看不懂版本")
        self.assertEqual(self.row(result, "Homebrew"), "Homebrew 7.0.10 - 看不懂版本")
        self.assertEqual(self.row(result, "macOS"), "macOS 27.2.1 27.2.1 一致")
        self.assertIn("Ruff：在 PATH 里找不到 ruff 命令。", result.out)
        self.assertIn("VS Code（code 命令）：运行 code --version 得到的是「garbage output」，从里面看不出版本号。",
                      result.out)
        self.assertIn("Homebrew：运行 brew --version 失败（退出码 1）。", result.out)

    def test_affected_lessons_are_listed(self):
        self.install(python3="Python 3.15.2", ruff="ruff 0.18.0")
        self.lesson("1.6", {"git": "2.54.0", "python3": "3.14.9"})
        self.lesson("1.7", {"git": "2.54.0", "zsh": "5.9"})
        self.lesson("1.11", {"gh": "2.105.0", "ruff": "0.17.2"})
        result = self.fresh()
        self.assertIn("可能受影响的课（核对它们时用到了上面变了的工具）：", result.out)
        self.assertIn("  - 1.6 Git：第一次提交：Python（第一个 python3）（小版本变了）", result.out)
        self.assertIn("  - 1.11 GitHub：账号、安全与身份：Ruff（大版本变了）", result.out)
        self.assertNotIn("  - 1.7 ", result.out)
        self.assertNotIn("  - 1.11 GitHub：账号、安全与身份：GitHub CLI", result.out)
        self.assertTrue(result.out.rstrip().endswith("下一步：把这段发给导师，说“帮我核实受影响的课”。"))

    def test_a_missing_tool_affects_its_lessons(self):
        self.install(skip=("node", "npm"))
        self.lesson("1.6", {"git": "2.54.0", "node": "26.12.0"})
        result = self.fresh()
        self.assertEqual(result.code, 0)
        self.assertIn("  - 1.6 Git：第一次提交：Node.js（没装）", result.out)

    def test_drift_that_no_lesson_uses(self):
        self.install(brew="Homebrew 7.0.15")
        self.lesson("1.6", {"git": "2.54.0"})
        result = self.fresh()
        self.assertIn("可能受影响的课：没有。", result.out)
        self.assertIn("现有的课都没有用到它们，可以照常学", result.out)

    def test_nothing_on_path(self):
        result = self.fresh(PATH=str(self.box.base / "empty"))
        self.assertEqual(result.code, 0, result)
        later = [name for name, entry in BASELINE["tools"].items() if entry.get("installed_in")]
        self.assertEqual(later, ["gh"])
        self.assertEqual(result.out.count("没装"), len(BASELINE["tools"]) - len(later))
        self.assertEqual(result.out.count("还没安装（第 1.11 课会装）"), 1)

    def test_version_on_standard_error_and_a_hanging_tool(self):
        self.install()
        self.bin.prints("zsh", "zsh 5.9 (x86_64-apple-darwin)", stderr=True)
        self.bin.script("node", "/bin/sleep 10")
        with mock.patch.object(fresh, "RUN_TIMEOUT", 2):
            result = self.fresh()
        self.assertEqual(self.row(result, "zsh"), "zsh 5.9 5.9 一致")
        self.assertEqual(self.row(result, "Node.js"), "Node.js 26.12.0 - 看不懂版本")
        self.assertIn("Node.js：运行 node --version 失败（超过 2 秒没有结束）。", result.out)

    def test_read_only(self):
        self.install()
        (self.box.root / "learner").mkdir()
        (self.box.root / "learner" / "state.json").write_text("{broken", encoding="utf-8")
        result = self.fresh()
        self.assertEqual(result.code, 0, result)
        self.assertEqual(sorted(p.name for p in (self.box.root / "learner").iterdir()),
                         ["state.json"])
        # A damaged state counts as "nothing passed" and is left as it was.
        self.assertIn("还没安装（第 1.11 课会装）", result.out)
        self.assertEqual((self.box.root / "learner" / "state.json").read_text(encoding="utf-8"),
                         "{broken")

    # -- the baseline file itself -------------------------------------------------
    def test_unreadable_baseline_is_a_checker_problem(self):
        self.install()
        for text in ("{not json", '{"verified_on": "2026-11-19", "tools": {}}',
                     '{"verified_on": "2026-11-19", "tools": {"git": {"command": "git", "version": "2"}}}',
                     '{"verified_on": "2026-11-19", "tools": {"git": {"command": ["git"], "version": "x"}}}'):
            with self.subTest(text=text):
                broken = self.box.base / "baseline.json"
                broken.write_text(text, encoding="utf-8")
                with mock.patch.object(fresh, "BASELINE", broken):
                    result = self.fresh()
                self.assertEqual(result.code, 2, result)
                self.assertIn("检查器出问题", result.text)
                self.assertIn("baseline.json", result.text)
                # a first-aid sentence in the fixed form “急救：……”
                self.assertIn("说“急救：fresh 的基线文件坏了”", result.text)
        with mock.patch.object(fresh, "BASELINE", self.box.base / "missing.json"):
            self.assertEqual(self.fresh().code, 2)

    def test_python_39_process(self):
        python = helpers.find_python39()
        if python is None:
            self.skipTest("no Python 3.9 on this machine")
        self.install(node="v27.1.0")
        self.lesson("1.6", {"git": "2.54.0", "node": "26.12.0"})
        result = self.box.run_process("fresh", python=python, PATH=str(self.bin))
        self.assertEqual(result.code, 0, result)
        self.assertIn("大版本变了", result.out)
        self.assertIn("1.6 Git：第一次提交：Node.js（大版本变了）", result.out)


if __name__ == "__main__":
    unittest.main()
