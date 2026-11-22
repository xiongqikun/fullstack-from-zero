"""The check context: read-only helpers, worded expectations, ask and quiz."""

import io
import sys
import unittest

import helpers
from courselib import scenario
from courselib.context import CheckContext
from courselib.errors import Cancelled, CheckStop, ToolTrouble, UsageProblem
from courselib.ui import Console


class ContextTestCase(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def ctx(self, inputs=None, answers=None, can_prompt=True, lesson=None, station=None,
            bound=None, state=None):
        """A context whose console reads ``inputs`` and records what it printed."""
        self.out = io.StringIO()
        feed = list(inputs or [])

        def reader(prompt):
            self.out.write(prompt)
            if not feed:
                raise EOFError()
            item = feed.pop(0)
            if item is KeyboardInterrupt:
                raise KeyboardInterrupt()
            return item

        console = Console(out=self.out, err=self.out, reader=reader, can_prompt=can_prompt,
                          is_tty=True)
        app = helpers.App(self.box.root, env=self.box.environment(), console=console)
        return CheckContext(app, lesson=lesson, station_id=station, answers=answers,
                            scenario=bound, state=state)


class FilesTest(ContextTestCase):
    def test_paths(self):
        ctx = self.ctx()
        self.assertEqual(ctx.path("~/Developer/my-site"), self.box.home / "Developer" / "my-site")
        self.assertEqual(ctx.path("~"), self.box.home)
        self.assertEqual(ctx.path("notes/my-rules.md"), self.box.root / "notes" / "my-rules.md")
        self.assertEqual(ctx.path(self.box.home), self.box.home)
        self.assertEqual(ctx.show(self.box.home / "Developer"), "~/Developer")
        self.assertEqual(ctx.show("~/x"), "~/x")
        self.assertEqual(ctx.my_site, self.box.home / "Developer" / "my-site")
        self.assertEqual(ctx.playground, self.box.playground)
        self.assertEqual(ctx.workspace, self.box.root)
        self.assertEqual(ctx.now.isoformat(), helpers.NOW)

    def test_reading_never_raises(self):
        ctx = self.ctx()
        folder = self.box.home / "data"
        folder.mkdir()
        (folder / "a.txt").write_text("第一行\r\n第二行\n", encoding="utf-8")
        (folder / "bom.txt").write_bytes(b"\xef\xbb\xbfhello")
        (folder / "gbk.txt").write_bytes("你好".encode("gbk"))
        (folder / ".hidden").write_text("")
        (folder / "sub").mkdir()
        (folder / "sub" / "b.txt").write_text("b")
        (folder / "sub" / ".git").mkdir()
        (folder / "sub" / ".git" / "config").write_text("x")
        (folder / ".DS_Store").write_text("x")
        self.assertEqual(ctx.read(folder / "a.txt"), "第一行\r\n第二行\n")
        self.assertEqual(ctx.lines(folder / "a.txt"), ["第一行", "第二行"])
        self.assertEqual(ctx.read(folder / "bom.txt"), "hello")
        self.assertIn("�", ctx.read(folder / "gbk.txt"))
        self.assertEqual(ctx.read_bytes(folder / "gbk.txt"), "你好".encode("gbk"))
        self.assertEqual(ctx.read(folder / "missing.txt"), "")
        self.assertEqual(ctx.read(folder / "missing.txt", default=None), None)
        self.assertEqual(ctx.read(folder), "")
        self.assertEqual(ctx.lines(folder / "missing.txt"), [])
        self.assertEqual(ctx.read_bytes(folder / "missing.txt"), b"")
        self.assertEqual(ctx.listdir(folder),
                         [".DS_Store", ".hidden", "a.txt", "bom.txt", "gbk.txt", "sub"])
        self.assertEqual(ctx.listdir(folder, hidden=False), ["a.txt", "bom.txt", "gbk.txt", "sub"])
        self.assertEqual(ctx.listdir(folder / "missing"), [])
        self.assertEqual(ctx.walk(folder), [".hidden", "a.txt", "bom.txt", "gbk.txt", "sub/b.txt"])
        self.assertIn("sub/.git/config", ctx.walk(folder, everything=True))
        self.assertEqual(ctx.walk(folder / "missing"), [])
        self.assertEqual(ctx.size(folder / "sub" / "b.txt"), 1)
        self.assertIsNone(ctx.size(folder))
        self.assertIsNone(ctx.mtime(folder / "missing"))
        self.assertIsNotNone(ctx.mtime(folder / "a.txt"))
        self.assertTrue(ctx.exists(folder) and ctx.is_dir(folder) and not ctx.is_file(folder))
        self.assertTrue(ctx.is_file(folder / "a.txt"))

    def test_expectations_record_worded_results(self):
        ctx = self.ctx()
        folder = self.box.home / "site"
        folder.mkdir()
        (folder / "index.html").write_text("x")
        self.assertTrue(ctx.expect_file(folder / "index.html", "网页文件"))
        self.assertTrue(ctx.expect_dir(folder))
        self.assertTrue(ctx.expect_missing(folder / "old.txt"))
        self.assertFalse(ctx.failed)
        self.assertFalse(ctx.expect_file(folder / "style.css"))
        self.assertFalse(ctx.expect_file(folder, "应该是文件的东西"))
        self.assertFalse(ctx.expect_dir(folder / "index.html"))
        self.assertFalse(ctx.expect_dir(folder / "assets"))
        self.assertFalse(ctx.expect_missing(folder / "index.html"))
        self.assertTrue(ctx.failed)
        self.assertEqual(ctx.oks[0], "有这个文件：网页文件")
        self.assertEqual(len(ctx.oks), 3)
        self.assertEqual(len(ctx.fails), 5)
        for fail in ctx.fails:
            self.assertTrue(fail["where"] and fail["saw"] and fail["missing"], fail)
        self.assertEqual(ctx.fails[0]["where"], "~/site/style.css")
        self.assertEqual(ctx.fails[1]["where"], "应该是文件的东西")

    def test_need_helpers_stop_the_check(self):
        ctx = self.ctx()
        folder = self.box.home / "site"
        folder.mkdir()
        self.assertEqual(ctx.need_dir(folder), folder)
        with self.assertRaises(CheckStop):
            ctx.need_file(folder / "index.html")
        with self.assertRaises(CheckStop):
            ctx.need_dir(folder / "assets")
        self.assertEqual(len(ctx.fails), 2)
        with self.assertRaises(CheckStop):
            ctx.stop()

    def test_one_line_messages(self):
        ctx = self.ctx()
        ctx.ok("第一行\n  第二行")
        ctx.fail("缺\n这个", where="这\n里", saw="看到\n了")
        ctx.fail("只有一句")
        ctx.note("备注\n一条")
        self.assertEqual(ctx.oks, ["第一行 第二行"])
        self.assertEqual(ctx.fails[0], {"where": "这 里", "saw": "看到 了", "missing": "缺 这个"})
        self.assertEqual(ctx.fails[1], {"where": "", "saw": "", "missing": "只有一句"})
        self.assertEqual(ctx.notes, ["备注 一条"])

    def test_expect_records_ok_or_fail_and_returns_the_condition(self):
        ctx = self.ctx()
        self.assertTrue(ctx.expect(1 + 1 == 2, "算对了", "没算对"))
        self.assertFalse(ctx.expect("", "有内容", "还是空的", where="文件", saw="0 字节"))
        self.assertEqual(ctx.oks, ["算对了"])
        self.assertEqual(ctx.fails, [{"where": "文件", "saw": "0 字节", "missing": "还是空的"}])
        self.assertTrue(ctx.failed)


class GitAndProgramsTest(ContextTestCase):
    def test_need_repo(self):
        ctx = self.ctx()
        base = self.box.home / "Developer"
        (base / "plain").mkdir()
        with self.assertRaises(CheckStop):
            ctx.need_repo(base / "missing", "不存在的文件夹")
        with self.assertRaises(CheckStop):
            ctx.need_repo(base / "plain")
        self.box.git(base, "init", "-q", "-b", "main", "outer")
        (base / "outer" / "inner").mkdir()
        with self.assertRaises(CheckStop):
            ctx.need_repo(base / "outer" / "inner", "里面的文件夹")
        repo = ctx.need_repo(base / "outer", "外面的仓库")
        self.assertTrue(repo.is_repo)
        # only praise=True records the line (2026-11-20, tools-r5 T3)
        self.assertEqual(ctx.oks, [])
        ctx.need_repo(base / "outer", "外面的仓库", praise=True)
        self.assertEqual(ctx.oks, ["是一个 Git 仓库：外面的仓库"])
        self.assertEqual([fail["where"] for fail in ctx.fails],
                         ["不存在的文件夹", "~/Developer/plain", "里面的文件夹"])
        self.assertIn("另一个仓库", ctx.fails[2]["saw"])
        self.assertIn("~/Developer/outer", ctx.fails[2]["saw"])

    def test_global_git_configuration_and_programs(self):
        self.box.write_gitconfig("[user]\n\tname = Somebody\n[commit]\n\tgpgsign = true\n")
        ctx = self.ctx()
        self.assertEqual(ctx.git_global("user.name"), "Somebody")
        self.assertIsNone(ctx.git_global("user.email"))
        self.assertIs(ctx.git_global_bool("commit.gpgsign"), True)
        self.assertGreaterEqual(ctx.git_version()[0], 2)
        self.assertTrue(ctx.which("git"))
        self.assertIsNone(ctx.which("surely-no-such-program-here"))
        self.assertEqual(ctx.env("HOME"), str(self.box.home))
        self.assertEqual(ctx.env("EDITOR", "vi"), "vi")

    def test_run_reports_instead_of_raising(self):
        ctx = self.ctx()
        script = self.box.root / "hello.py"
        script.write_text("import sys\nprint('你好 ' + sys.stdin.read().strip())\n", encoding="utf-8")
        good = ctx.run([ctx.python, "hello.py"], stdin_text="世界")
        self.assertTrue(good.ok)
        self.assertEqual(good.out, "你好 世界\n")
        self.assertEqual(good.lines, ["你好 世界"])
        bad = ctx.run([ctx.python, "-c", "import sys; sys.stderr.write('oops'); sys.exit(3)"])
        self.assertEqual((bad.ok, bad.code, bad.err), (False, 3, "oops"))
        missing = ctx.run(["surely-no-such-program-here"])
        self.assertTrue(missing.missing and not missing.ok)
        slow = ctx.run([ctx.python, "-c", "import time; time.sleep(20)"], timeout=0.5)
        self.assertTrue(slow.timed_out and not slow.ok)
        elsewhere = ctx.run([ctx.python, "-c", "import os; print(os.getcwd())"], cwd="~")
        self.assertEqual(elsewhere.out.strip(), str(self.box.home))
        with self.assertRaises(ValueError):
            ctx.run("echo not-a-list")
        self.assertEqual([p.name for p in self.box.root.glob("**/__pycache__")], [])


class AskTest(ContextTestCase):
    def test_right_answer_typed_at_the_prompt(self):
        ctx = self.ctx(inputs=["  ＭＡＩＮ "])
        self.assertTrue(ctx.ask("现在在哪个分支上？", "main"))
        self.assertEqual(ctx.oks, ["答对了：现在在哪个分支上？"])
        self.assertEqual(ctx.last_answer, "MAIN")
        self.assertTrue(ctx.interactive)
        shown = self.out.getvalue()
        self.assertIn("问：现在在哪个分支上？", shown)
        self.assertIn("你的回答：", shown)

    def test_wrong_answer_never_reveals_the_expected_one(self):
        ctx = self.ctx(inputs=["master"])
        self.assertFalse(ctx.ask("现在在哪个分支上？", "main-secret"))
        fail = ctx.fails[0]
        self.assertEqual(fail["saw"], "你的回答是「master」")
        self.assertNotIn("main-secret", str(fail) + self.out.getvalue())
        self.assertEqual(ctx.asked[0]["correct"], False)

    def test_empty_answer_is_asked_again_not_graded(self):
        # Regression (tester novice-abuse): an empty Enter used to be graded
        # wrong and counted as an attempt.
        ctx = self.ctx(inputs=["", "3"])
        self.assertTrue(ctx.ask("几个？", 3))
        self.assertIn("这一题要填一个回答", self.out.getvalue())
        self.assertEqual(ctx.fails, [])

    def test_only_empty_answers_cancel(self):
        ctx = self.ctx(inputs=["", " ", "　"])
        with self.assertRaises(Cancelled):
            ctx.ask("几个？", 3)
        self.assertEqual(ctx.fails, [])

    def test_empty_scripted_answer_is_a_usage_error(self):
        ctx = self.ctx(answers=[""])
        with self.assertRaises(UsageProblem):
            ctx.ask("几个？", 3)

    def test_expected_can_be_computed_and_lenient(self):
        ctx = self.ctx(inputs=["三个", "q", "ABC1234"])
        self.assertTrue(ctx.ask("有几个文件？", 3))
        self.assertTrue(ctx.ask("怎么退出？", ["q", "quit"]))
        self.assertTrue(ctx.ask("短编号？", lambda s: "abc1234def".startswith(s) and len(s) >= 7))

    def test_answers_from_the_command_line_come_first(self):
        ctx = self.ctx(inputs=["typed"], answers=["given"])
        self.assertTrue(ctx.ask("一？", "given"))
        self.assertTrue(ctx.ask("二？", "typed"))
        self.assertEqual(ctx.answers_used, 1)
        self.assertIn("你的回答：given", self.out.getvalue())

    def test_no_prompt_mode_without_an_answer_is_a_usage_problem(self):
        ctx = self.ctx(can_prompt=False)
        with self.assertRaises(UsageProblem) as caught:
            ctx.ask("一？", "x")
        self.assertIn("--answer", caught.exception.message)
        self.assertEqual(self.out.getvalue(), "")
        self.assertEqual(ctx.oks + ctx.fails, [])

    def test_no_prompt_mode_with_answers_works(self):
        ctx = self.ctx(can_prompt=False, answers=["x"])
        self.assertTrue(ctx.ask("一？", "x"))

    def test_end_of_input_and_ctrl_c_cancel(self):
        with self.assertRaises(Cancelled):
            self.ctx(inputs=[]).ask("一？", "x")
        with self.assertRaises(Cancelled):
            self.ctx(inputs=[KeyboardInterrupt]).ask("一？", "x")

    def test_normalize_helpers_are_available(self):
        ctx = self.ctx()
        self.assertEqual(ctx.normalize(" Ａb "), "ab")
        self.assertEqual(ctx.normalize(" Ａb ", case=False), "Ab")
        self.assertEqual(ctx.parse_int("３ 个"), 3)


class QuizTest(ContextTestCase):
    OPTIONS = ["甲方案", "乙方案", "丙方案"]

    def test_right_letter_in_any_spelling(self):
        for typed in ("b", "B", "Ｂ", "选 b", "乙方案"):
            ctx = self.ctx(inputs=[typed])
            self.assertTrue(ctx.quiz("选哪个？", self.OPTIONS, "B", explain="因为乙最好。"), typed)
            self.assertEqual(ctx.oks, ["选对了：选哪个？"])
            self.assertEqual(ctx.notes, ["因为乙最好。"])
            self.assertEqual(ctx.asked[0]["answer"], "B")
        shown = self.out.getvalue()
        for line in ("问：选哪个？", "  A. 甲方案", "  B. 乙方案", "  C. 丙方案"):
            self.assertIn(line, shown)

    def test_wrong_letter_gets_targeted_feedback_but_not_the_answer(self):
        ctx = self.ctx(inputs=["a"])
        self.assertFalse(ctx.quiz("选哪个？", self.OPTIONS, "B", explain="因为乙最好。",
                                  feedback={"a": "甲太贵", "C": "丙太慢。"}))
        fail = ctx.fails[0]
        self.assertEqual(fail["saw"], "你选的是 A（甲方案）")
        self.assertTrue(fail["missing"].startswith("甲太贵。"))
        self.assertEqual(ctx.notes, [])
        self.assertNotIn("因为乙最好", str(fail))

    def test_unreadable_input_is_asked_again_at_most_three_times(self):
        ctx = self.ctx(inputs=["x", "9", "c"])
        self.assertFalse(ctx.quiz("选哪个？", self.OPTIONS, "B"))
        self.assertEqual(self.out.getvalue().count("请输入 A 到 C 之间的一个字母"), 2)
        self.assertEqual(ctx.fails[0]["saw"], "你选的是 C（丙方案）")
        ctx = self.ctx(inputs=["x", "y", "z", "b"])
        self.assertFalse(ctx.quiz("选哪个？", self.OPTIONS, "B"))
        self.assertIn("不是 A 到 C 之间的字母", ctx.fails[0]["saw"])

    def test_given_answers_are_not_retried(self):
        ctx = self.ctx(inputs=["b"], answers=["zzz"])
        self.assertFalse(ctx.quiz("选哪个？", self.OPTIONS, "B"))
        self.assertTrue(ctx.quiz("再选？", self.OPTIONS, "B"))

    def test_badly_written_questions_are_the_lessons_fault(self):
        ctx = self.ctx(inputs=["a"] * 5)
        for options, answer in ((["只有一个"], "A"), (self.OPTIONS, "D"), (self.OPTIONS, 1),
                                (["甲", ""], "A"), ("甲乙", "A")):
            with self.assertRaises(ValueError, msg=(options, answer)):
                ctx.quiz("题目", options, answer)


class ScenarioAndStateTest(ContextTestCase):
    def setUp(self):
        ContextTestCase.setUp(self)
        self.box.add_syllabus_lesson("1.6", extra='SCENARIOS["1.6b"] = build_start\n')
        self.lesson = self.box.app().catalog().lesson("1.6")

    def test_missing_scenario_ends_the_check_with_the_command_to_build_it(self):
        ctx = self.ctx(lesson=self.lesson, station="1.6a")
        with self.assertRaises(CheckStop):
            ctx.scenario("start")
        fail = ctx.fails[0]
        self.assertEqual(fail["where"], "练习场 ~/Developer/playground/1.6-start")
        self.assertIn("python3 tools/course.py scenario 1.6-start", fail["missing"])
        self.assertFalse(ctx.scenario("start", required=False).exists)

    def test_built_scenario_gives_path_seed_and_facts(self):
        self.box.build_scenario("1.6", seed=77)
        ctx = self.ctx(lesson=self.lesson, station="1.6a")
        info = ctx.scenario("start")
        self.assertEqual(info.path, self.box.playground / "1.6-start")
        self.assertEqual((info.seed, info.facts), (77, {"lesson": "1.6"}))

    def test_station_scenario_is_the_default(self):
        self.box.build_scenario("1.6b", seed=3)
        ctx = self.ctx(lesson=self.lesson, station="1.6b")
        self.assertEqual(ctx.scenario().path, self.box.playground / "1.6b")
        with self.assertRaises(ToolTrouble):
            self.ctx(lesson=self.lesson, station="1.6a").scenario()
        with self.assertRaises(ToolTrouble):
            self.ctx(lesson=self.lesson, station="1.6a").scenario("1.6z")

    def test_half_built_scenario_asks_for_a_plain_rebuild(self):
        target = self.box.playground / "1.6-start"
        target.mkdir(parents=True)
        (target / ".playground").write_text('{"complete": false}')
        ctx = self.ctx(lesson=self.lesson, station="1.6a")
        with self.assertRaises(CheckStop):
            ctx.scenario("start")
        # the plain command rebuilds a half-built scenario, so no --reset
        self.assertIn("python3 tools/course.py scenario 1.6-start", ctx.fails[0]["missing"])
        self.assertNotIn("--reset", ctx.fails[0]["missing"])
        self.assertTrue(ctx.not_ready)

    def test_bound_scenario_wins_for_review_and_exam(self):
        app = self.box.app()
        bound = scenario.build(app, self.lesson.scenarios["start"], "review/1.6-r9",
                               key="start", lesson_id="1.6", seed=8)
        ctx = self.ctx(lesson=self.lesson, bound=bound)
        self.assertIs(ctx.scenario(), bound)
        self.assertIs(ctx.scenario("start"), bound)
        self.assertEqual(ctx.scenario().path, self.box.playground / "review" / "1.6-r9")

    def test_state_is_a_copy_and_decisions_are_collected(self):
        state = {"stations": {"1.6a": {"first_pass": "2026-11-19T09:00:00"}},
                 "decisions": {"commit_signing": "off"}}
        ctx = self.ctx(state=state)
        self.assertTrue(ctx.passed("1.6a"))
        self.assertFalse(ctx.passed("1.6b"))
        self.assertEqual(ctx.decision("commit_signing"), "off")
        self.assertEqual(ctx.decision("missing", "默认"), "默认")
        ctx.state["decisions"]["commit_signing"] = "changed"
        self.assertEqual(state["decisions"]["commit_signing"], "off")
        ctx.decide("workspace_location", "~/Developer/fullstack-from-zero")
        self.assertEqual(ctx.decisions, {"workspace_location": "~/Developer/fullstack-from-zero"})

    def test_python_is_the_running_interpreter(self):
        self.assertEqual(self.ctx().python, sys.executable)


if __name__ == "__main__":
    unittest.main()
