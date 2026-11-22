"""Regression tests for the issues the three T1 testers reported.

Each test names the issue it pins down.  Most work through the command line
(``Sandbox.run``) in a throw-away workspace under $TMPDIR; none touches the
real home, the real Git configuration or the real workspace.
"""

import contextlib
import io
import json
import os
import shutil
import stat
import time
import unittest
from pathlib import Path

import helpers
from courselib import gitwrite, normalize, scenario
from courselib.context import CheckContext
from courselib.errors import ToolTrouble
from courselib.gitread import READ_ONLY, GitReader, GitRepo, reader_env
from courselib.store import Store, reason

EXAMPLE_START = "99.1-start"


def example_box(test):
    box = helpers.Sandbox(test, example=True)
    return box


def commit_readme(box, info):
    repo = info.path / info.facts["repo"]
    (repo / "README.md").write_text("# 我的笔记\n", encoding="utf-8")
    box.git(repo, "add", "README.md")
    box.git(repo, "commit", "-q", "-m", "docs: 添加说明")
    return repo


# ---------------------------------------------------------------------------
# safety-contract: read-only Git really is read-only
# ---------------------------------------------------------------------------
class ReadOnlyGitTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.repo_path = self.box.base / "work" / "proj"
        self.repo_path.mkdir(parents=True)
        self.box.git(self.repo_path, "init", "-q", "-b", "main")
        (self.repo_path / "a.txt").write_text("a\n", encoding="utf-8")
        self.box.git(self.repo_path, "add", "-A")
        self.box.git(self.repo_path, "commit", "-q", "-m", "docs: 第一次")
        self.repo = GitRepo(self.repo_path, GitReader(self.box.environment()))

    def test_stat_only_change_leaves_the_index_alone(self):
        # Porcelain diff and describe --dirty used to rewrite .git/index
        # after a stat-only change (touch without editing).
        index = self.repo_path / ".git" / "index"
        time.sleep(1.1)
        os.utime(str(self.repo_path / "a.txt"))
        before = (index.read_bytes(), index.stat().st_mtime_ns)
        repo = self.repo
        repo.status()
        repo.is_clean()
        repo.commits()
        repo.tracked()
        repo.ignored()
        repo.changed_files()
        for args in (("diff",), ("diff", "--stat"), ("diff", "HEAD"), ("diff", "--quiet"),
                     ("diff", "--name-only"), ("describe", "--dirty", "--always"),
                     ("status",), ("log", "--stat")):
            result = repo.query(*args)
            self.assertIn(result.code, (0, 1), (args, result.err))
        self.assertEqual((index.read_bytes(), index.stat().st_mtime_ns), before)

    def test_grep_and_program_running_options_are_refused(self):
        self.assertNotIn("grep", READ_ONLY)
        for args in (("grep", "-Orm", "a"), ("diff", "--ext-diff"),
                     ("log", "--output=x.txt"), ("show", "--open-files-in-pager=rm")):
            with self.assertRaises(ToolTrouble, msg=args):
                self.repo.query(*args)
        self.assertTrue((self.repo_path / "a.txt").exists())

    def test_is_clean_is_false_for_a_folder_that_is_not_a_repository(self):
        plain = self.box.base / "plain"
        plain.mkdir()
        self.assertFalse(GitRepo(plain, GitReader(self.box.environment())).is_clean())
        self.assertFalse(GitRepo(self.box.base / "missing",
                                 GitReader(self.box.environment())).is_clean())
        self.assertTrue(self.repo.is_clean())

    def test_reader_environment(self):
        env = reader_env({"PATH": "/usr/bin", "GIT_DIR": "/elsewhere", "LC_ALL": "de_DE"})
        self.assertEqual(env["LC_ALL"], "C")
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["GIT_NO_LAZY_FETCH"], "1")
        self.assertNotIn("GIT_DIR", env)


# ---------------------------------------------------------------------------
# safety-contract: builder Git stays inside its own repository
# ---------------------------------------------------------------------------
class BuilderGitTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.env = self.box.environment()

    def test_commit_does_not_walk_up_into_an_enclosing_repository(self):
        outer = self.box.base / "outer" / "Developer"
        outer.mkdir(parents=True)
        self.box.git(outer, "init", "-q", "-b", "main")
        (outer / "diary.txt").write_text("私人日记\n", encoding="utf-8")
        notes = outer / "playground" / "x" / "notes"
        notes.mkdir(parents=True)
        (notes / "a.txt").write_text("a\n", encoding="utf-8")
        with self.assertRaises(ToolTrouble):
            gitwrite.git_commit(notes, "docs: 测试", self.env)
        log = self.box.git(outer, "log", "--oneline", "--all", check=False)
        self.assertEqual(log.strip(), "")

    def test_scenario_git_is_fenced_in(self):
        outer = self.box.home / "Developer"
        self.box.git(outer, "init", "-q", "-b", "main")   # a stray git init
        (outer / "diary.txt").write_text("私人日记\n", encoding="utf-8")
        app = self.box.app()
        seen = {}

        def builder(sc):
            sc.mkdir("notes")
            sc.write("notes/a.txt", "a")
            seen["ceiling"] = sc._env()["GIT_CEILING_DIRECTORIES"]
            for bad in (("-C", "/"), ("--git-dir=/x", "log"), ("-c", "a.b=c", "log")):
                try:
                    sc.git("notes", *bad)
                except ToolTrouble:
                    seen.setdefault("refused", []).append(bad[0])
            sc.git_commit("notes", "docs: 不该成功")

        with self.assertRaises(ToolTrouble):
            scenario.build(app, builder, "fenced")
        self.assertEqual(seen["refused"], ["-C", "--git-dir=/x", "-c"])
        self.assertEqual(seen["ceiling"],
                         os.path.realpath(str(self.box.playground / "fenced")))
        self.assertEqual(self.box.git(outer, "log", "--oneline", "--all", check=False).strip(), "")

    def test_builder_commits_skip_hooks(self):
        # --no-verify (mutation M20): a failing hook never stops a builder.
        repo = self.box.base / "hooked"
        gitwrite.git_init(repo, self.env)
        hook = repo / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        os.chmod(str(hook), os.stat(str(hook)).st_mode | stat.S_IXUSR)
        (repo / "a.txt").write_text("a\n", encoding="utf-8")
        self.assertTrue(gitwrite.git_commit(repo, "docs: 有钩子也能提交", self.env))


# ---------------------------------------------------------------------------
# safety-contract: where the playground may lie
# ---------------------------------------------------------------------------
class PlaygroundLocationTest(unittest.TestCase):
    def test_not_inside_the_workspace_or_the_learners_site(self):
        box = example_box(self)
        site = box.home / "Developer" / "my-site"
        for place in (box.root / "stages", box.root, site, site / "practice"):
            with self.subTest(place=place):
                result = box.run("scenario", "99.1", COURSE_PLAYGROUND=str(place))
                self.assertEqual(result.code, 1, result)
                self.assertIn("练习场的位置不安全", result.out)
                self.assertFalse((place / EXAMPLE_START).exists())

    def test_a_link_inside_the_playground_is_called_a_link(self):
        box = example_box(self)
        outside = box.base / "outside"
        outside.mkdir()
        (outside / "mine.txt").write_text("别动", encoding="utf-8")
        box.playground.mkdir(parents=True)
        os.symlink(str(outside), str(box.playground / EXAMPLE_START))
        result = box.run("scenario", "99.1", "--reset")
        self.assertEqual(result.code, 1, result)
        self.assertIn("这个位置是一个链接", result.out)
        self.assertNotIn("不在练习场里面", result.out)
        self.assertTrue((outside / "mine.txt").exists())


# ---------------------------------------------------------------------------
# novice-abuse: a half-built scenario
# ---------------------------------------------------------------------------
class HalfBuiltScenarioTest(unittest.TestCase):
    def setUp(self):
        self.box = example_box(self)
        self.folder = self.box.playground / EXAMPLE_START

    def half_build(self):
        self.folder.mkdir(parents=True)
        (self.folder / ".playground").write_text(json.dumps(
            {"tool": "course.py", "scenario": EXAMPLE_START, "complete": False}),
            encoding="utf-8")
        (self.folder / "notes-left-over").mkdir()

    def test_plain_rerun_rebuilds_without_reset(self):
        self.half_build()
        result = self.box.run("scenario", "99.1", "--seed", "4")
        self.assertEqual(result.code, 0, result)
        info = scenario.read_info(self.folder)
        self.assertTrue(info.exists)
        self.assertFalse((self.folder / "notes-left-over").exists())

    def test_a_check_on_it_is_not_an_attempt(self):
        self.half_build()
        result = self.box.run("check", "99.1b", "--answer", "3", noninteractive=True)
        self.assertEqual(result.code, 1, result)
        self.assertIn("没有搭完整", result.out)
        self.assertIn("python3 tools/course.py scenario 99.1-start", result.out)
        self.assertIn("这次不算一次尝试", result.out)
        record = self.box.state()["stations"].get("99.1b", {})
        self.assertEqual(int(record.get("attempts") or 0), 0)
        self.assertFalse(self.box.last_result()["counted"])

    def test_a_missing_scenario_is_not_an_attempt_either(self):
        result = self.box.run("check", "99.1b", "--answer", "3", noninteractive=True)
        self.assertEqual(result.code, 1, result)
        self.assertIn("这次不算一次尝试", result.out)
        self.assertEqual(int(self.box.state()["stations"].get("99.1b", {})
                             .get("attempts") or 0), 0)

    def test_ctrl_c_during_the_build_says_what_to_run(self):
        source = self.box.root / "stages" / helpers.EXAMPLE_STAGE / helpers.EXAMPLE_FOLDER
        lesson = source / "lesson.py"
        text = lesson.read_text(encoding="utf-8")
        text = text.replace('    sc.fact("repo", repo)\n    sc.fact("commits", count)\n',
                            '    raise KeyboardInterrupt()\n', 1)
        lesson.write_text(text, encoding="utf-8")
        result = self.box.run("scenario", "99.1")
        self.assertEqual(result.code, 1, result)
        self.assertIn("搭建被打断了", result.out)
        self.assertIn("python3 tools/course.py scenario 99.1-start", result.out)
        self.assertFalse(scenario.read_info(self.folder).exists)


# ---------------------------------------------------------------------------
# novice-abuse: empty answers, ids, command names, confidence
# ---------------------------------------------------------------------------
class TypingTest(unittest.TestCase):
    def setUp(self):
        self.box = example_box(self)

    def test_empty_enter_at_an_ask_question_is_not_graded(self):
        info = self.box.build_scenario("99.1", seed=7)
        commit_readme(self.box, info)
        commits = info.facts["commits"]
        result = self.box.run("check", "99.1b", inputs=["", str(commits)])
        self.assertEqual(result.code, 0, result)
        self.assertIn("这一题要填一个回答", result.out)
        self.assertEqual(self.box.state()["stations"]["99.1b"]["attempts"], 1)

    def test_enter_three_times_cancels_without_an_attempt(self):
        info = self.box.build_scenario("99.1", seed=7)
        commit_readme(self.box, info)
        result = self.box.run("check", "99.1b", inputs=["", "", ""])
        self.assertEqual(result.code, 1, result)
        self.assertIn("已取消", result.out)
        self.assertNotIn("还没达标", result.out)
        record = self.box.state()["stations"].get("99.1b", {})
        self.assertEqual(int(record.get("attempts") or 0), 0)

    def test_chinese_full_stop_in_an_id(self):
        for typed in ("99。1a", "99，1a", "９９。１Ａ", "99,1a"):
            with self.subTest(typed=typed):
                result = self.box.run("hint", typed, "--yes")
                self.assertEqual(result.code, 0, result)
                self.assertIn("99.1a", result.out)

    def test_command_names_are_folded(self):
        for typed in ("Status", "ＳＴＡＴＵＳ", "ｓｔａｔｕｓ"):
            with self.subTest(typed=typed):
                self.assertEqual(self.box.run(typed).code, 0)

    def test_a_space_inside_a_station_id(self):
        result = self.box.run("hint", "99.1", "a")
        self.assertEqual(result.code, 64, result)
        self.assertIn("python3 tools/course.py hint 99.1a", result.err)

    def test_unknown_argument_points_to_the_commands_own_help(self):
        result = self.box.run("check", "99.1a", "extra")
        self.assertEqual(result.code, 64, result)
        self.assertIn("python3 tools/course.py check -h", result.err)

    def test_an_unreadable_confidence_is_said_out_loud(self):
        result = self.box.run("check", "99.1a", inputs=["很有把握", "B", "B"], tty=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("没看懂这个把握程度", result.out)

    def test_parse_int_and_zero(self):
        self.assertIsNone(normalize.parse_int("不是3"))
        self.assertIsNone(normalize.parse_int("没有 3 个"))
        self.assertEqual(normalize.parse_int("３ 个"), 3)
        for answer in ("没有", "无", "零", "0", "0 个", "一个也没有"):
            self.assertTrue(normalize.matches(answer, 0), answer)
        self.assertFalse(normalize.matches("没有", 1))
        self.assertFalse(normalize.matches("不是3", 3))


# ---------------------------------------------------------------------------
# novice-abuse: learner/ that cannot be written
# ---------------------------------------------------------------------------
@unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores permissions")
class UnwritableStateTest(unittest.TestCase):
    def setUp(self):
        self.box = example_box(self)
        self.assertEqual(self.box.run("status").code, 0)
        self.learner = self.box.root / "learner"
        self.addCleanup(self.unlock)

    def unlock(self):
        for path in (self.learner, self.learner / "state.json"):
            if path.exists():
                os.chmod(str(path), 0o755 if path.is_dir() else 0o644)

    def test_check_gives_exactly_one_outcome(self):
        log = (self.learner / "log.jsonl").read_bytes()
        state = (self.learner / "state.json").read_bytes()
        os.chmod(str(self.learner), 0o555)
        result = self.box.run("check", "99.1a", "--answer", "B", "--answer", "B",
                              noninteractive=True)
        self.assertEqual(result.code, 2, result)
        self.assertIn("检查器出问题", result.out)
        self.assertNotIn("通过", result.out.replace("检查器出问题", ""))
        self.unlock()
        self.assertEqual((self.learner / "log.jsonl").read_bytes(), log)
        self.assertEqual((self.learner / "state.json").read_bytes(), state)

    def test_status_still_shows_progress(self):
        os.chmod(str(self.learner), 0o555)
        result = self.box.run("status")
        self.assertEqual(result.code, 0, result)
        self.assertIn("学习进度", result.out)
        self.assertIn("这次学习时间没能记下", result.out)

    def test_a_read_only_state_file_is_not_replaced(self):
        path = self.learner / "state.json"
        before = path.read_bytes()
        os.chmod(str(path), 0o444)
        result = self.box.run("status")
        self.assertEqual(result.code, 0, result)
        self.assertIn("只读", result.out)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o444)

    def test_save_writes_the_state_before_the_log(self):
        store = Store(self.learner, app=self.box.app())
        state = store.load()
        log = (self.learner / "log.jsonl").read_bytes()
        os.chmod(str(self.learner / "state.json"), 0o444)
        state["decisions"]["x"] = 1
        with self.assertRaises(ToolTrouble):
            store.save(state, events=[{"type": "check"}])
        self.assertEqual((self.learner / "log.jsonl").read_bytes(), log)


# ---------------------------------------------------------------------------
# novice-abuse: Chinese reasons and recovery steps
# ---------------------------------------------------------------------------
class WordingTest(unittest.TestCase):
    def test_reasons_are_chinese(self):
        for exc in (FileExistsError(), NotADirectoryError(), IsADirectoryError(),
                    PermissionError(), FileNotFoundError(), OSError(28, "No space")):
            text = reason(exc)
            self.assertNotIn("Error", text)
            self.assertTrue(text)

    def test_journal_as_a_file(self):
        box = helpers.Sandbox(self)
        (box.root / "journal").write_text("我的文件", encoding="utf-8")
        result = box.run("journal", "--done", "读了课文", noninteractive=True)
        self.assertEqual(result.code, 2, result)
        self.assertNotIn("Error", result.out)
        self.assertEqual((box.root / "journal").read_text(encoding="utf-8"), "我的文件")

    def test_corrupt_state_recovery_gives_the_command(self):
        box = helpers.Sandbox(self)
        (box.root / "learner").mkdir()
        (box.root / "learner" / "state.json").write_text("{bad", encoding="utf-8")
        result = box.run("status")
        self.assertEqual(result.code, 2, result)
        self.assertIn("mv learner/state.json learner/state.json.bad", result.out)

    def test_untouched_example_does_not_praise_a_clean_repository(self):
        box = example_box(self)
        box.build_scenario("99.1", seed=3)
        result = box.run("check", "99.1b", "--answer", "3", noninteractive=True)
        self.assertEqual(result.code, 1, result)
        self.assertNotIn("没有落下还没提交的改动", result.out)

    def test_exam_list_and_heading_for_a_gate_without_a_title(self):
        box = example_box(self)
        listing = box.run("exam")
        self.assertEqual(listing.code, 0, listing)
        self.assertNotIn("gate-examplegate-example", listing.out)
        box.run("exam", "gate-example", "--seed", "3")
        graded = box.run("exam", "gate-example", "--grade", noninteractive=True)
        self.assertIn("批改 · gate-example · 第 1 场", graded.out)


# ---------------------------------------------------------------------------
# safety-contract: what a check prints and runs
# ---------------------------------------------------------------------------
class CheckContainmentTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def test_stderr_and_warnings_of_a_check_are_captured(self):
        extra = '''
import sys as _sys
import warnings as _warnings


def _noisy(ctx):
    _sys.stderr.write("Traceback (most recent call last): fake\\n")
    _warnings.warn("deprecated thing")
    print("plain print")
    ctx.ok("好了")


checks["1.6a"] = _noisy
'''
        self.box.add_syllabus_lesson("1.6", extra=extra)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            result = self.box.run("check", "1.6a")
        self.assertEqual(result.code, 0, result)
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn("Traceback", result.text)
        printed = self.box.last_result()["printed_by_check"]
        self.assertIn("deprecated thing", printed)
        self.assertIn("plain print", printed)

    def test_ctx_run_guards(self):
        app = self.box.app()
        ctx = CheckContext(app)
        with self.assertRaises(ValueError):
            ctx.run(["git", "status"])
        with self.assertRaises(ValueError):
            ctx.run(["/usr/bin/git", "status"])
        python = helpers.sys.executable
        result = ctx.run([python, "-c", "import os; print(os.environ['GIT_OPTIONAL_LOCKS'])"],
                         timeout=None)
        self.assertTrue(result.ok, result.err)
        self.assertEqual(result.out.strip(), "0")
        slow = ctx.run([python, "-c", "import time; time.sleep(5)"], timeout=0.01)
        self.assertTrue(slow.timed_out)   # clamped to 1 second, not 0.01

    def test_a_damaged_repository_is_not_called_missing(self):
        box = example_box(self)
        info = box.build_scenario("99.1", seed=2)
        head = info.path / info.facts["repo"] / ".git" / "HEAD"
        head.rename(head.with_name("HEAD.bak"))
        result = box.run("check", "99.1b", "--answer", "3", noninteractive=True)
        self.assertEqual(result.code, 2, result)
        self.assertIn("可能损坏了", result.out)
        self.assertNotIn("变成 Git 仓库", result.out)


# ---------------------------------------------------------------------------
# hygiene: simulation homes leave the learner's own files out
# ---------------------------------------------------------------------------
class SimHomeCopyTest(unittest.TestCase):
    def test_learner_files_are_not_copied(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "make_sim_home", str(helpers.TOOLS / "dev" / "make_sim_home.py"))
        sim = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sim)
        box = helpers.Sandbox(self)
        for name in ("journal", "notes", "learner"):
            (box.root / name).mkdir()
            (box.root / name / "mine.md").write_text("私人", encoding="utf-8")
        (box.root / "PROGRESS.md").write_text("x", encoding="utf-8")
        (box.root / "stages" / "notes").mkdir()      # deeper "notes" is course content
        info = sim.make_sim_home(box.base / "sim", workspace=box.root)
        copy = Path(info["workspace"])
        for name in ("journal", "notes", "learner", "PROGRESS.md"):
            self.assertFalse((copy / name).exists(), name)
        self.assertTrue((copy / "stages" / "notes").is_dir())
        shutil.rmtree(str(box.base / "sim"))
        info = sim.make_sim_home(box.base / "sim", workspace=box.root, learner_files=True)
        self.assertTrue((Path(info["workspace"]) / "journal" / "mine.md").exists())


if __name__ == "__main__":
    unittest.main()
