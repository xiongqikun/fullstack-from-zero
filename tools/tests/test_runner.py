"""The guarded check runner: exactly three outcomes, never a traceback."""

import sys
import unittest

import helpers
from courselib import runner
from courselib.errors import Cancelled, ToolTrouble, UsageProblem


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def run_check(self, function, **options):
        self.app = self.box.app(inputs=options.pop("inputs", None),
                                noninteractive=options.pop("noninteractive", False))
        return runner.run_check(self.app, function, **options)

    def render(self, result, heading="1.6a 示例站"):
        return "\n".join(runner.render_result(self.app, result, heading, place="1.6a"))

    # -- the three outcomes ---------------------------------------------------
    def test_passed(self):
        def check(ctx):
            ctx.ok("做到了第一件事")
            ctx.note("顺便一提")

        result = self.run_check(check)
        self.assertEqual((result.outcome, result.exit_code, result.passed), ("passed", 0, True))
        text = self.render(result)
        self.assertTrue(text.startswith("✅ 通过 · 1.6a 示例站"))
        self.assertIn("已经做到：\n    - 做到了第一件事", text)
        self.assertIn("补充：\n    - 顺便一提", text)

    def test_not_yet_says_where_what_and_missing(self):
        def check(ctx):
            ctx.ok("文件夹在")
            ctx.fail("还缺一次提交", where="练习仓库的提交历史", saw="0 个提交")
            ctx.fail("只写了缺什么")

        result = self.run_check(check)
        self.assertEqual((result.outcome, result.exit_code, result.passed), ("not_yet", 1, False))
        text = self.render(result)
        self.assertTrue(text.startswith("❌ 还没达标 · 1.6a 示例站"))
        self.assertIn("还差 2 处：", text)
        self.assertIn("    1. 看了哪里：练习仓库的提交历史\n"
                      "       看到了什么：0 个提交\n"
                      "       还缺什么：还缺一次提交", text)
        self.assertIn("    2. 还缺什么：只写了缺什么", text)

    def test_one_failure_outweighs_any_number_of_successes(self):
        def check(ctx):
            ctx.ok("a")
            ctx.ok("b")
            ctx.fail("c")

        self.assertEqual(self.run_check(check).outcome, "not_yet")

    def test_a_raising_check_is_a_checker_problem_without_traceback(self):
        def check(ctx):
            ctx.ok("这一条不算数")
            return {}["missing-key"]

        result = self.run_check(check)
        self.assertEqual((result.outcome, result.exit_code), ("problem", 2))
        text = self.render(result)
        self.assertTrue(text.startswith("⚠️ 检查器出问题 · 1.6a 示例站"))
        self.assertIn("这不是你的错", text)
        self.assertIn("发给导师", text)
        self.assertIn("KeyError", text)
        self.assertIn("位置：1.6a", text)
        self.assertIn("时间：2026-11-19 10:00", text)
        self.assertNotIn("Traceback", text)
        self.assertNotIn("test_runner.py", text.replace("出处：", ""))
        self.assertIn("Traceback", result.problem["detail"])
        self.assertNotIn(str(self.box.home), result.problem["detail"])
        self.assertIn("learner/last-result.json", text)

    def test_other_ways_a_check_can_break(self):
        def exits(ctx):
            sys.exit(0)

        def silent(ctx):
            pass

        def needs_two(ctx, other):
            ctx.ok("x")

        def environment(ctx):
            raise ToolTrouble("找不到 git 命令。", recovery="先安装开发者工具。")

        def recursion(ctx):
            return recursion(ctx)

        for function in (exits, silent, needs_two, environment, recursion, None, "not callable"):
            result = self.run_check(function)
            self.assertEqual((result.outcome, result.exit_code), ("problem", 2), function)
            self.assertNotIn("Traceback", self.render(result))
        result = self.run_check(environment)
        self.assertIn("找不到 git 命令", self.render(result))
        self.assertIn("先安装开发者工具", self.render(result))
        self.assertIn("没有给出任何结论", self.run_check(silent).problem["summary"])

    def test_problem_names_the_line_in_the_lesson_file(self):
        folder = self.box.add_syllabus_lesson(
            "1.1", extra="\ndef boom(ctx):\n    raise ValueError('lesson bug')\n\nchecks['1.1a'] = boom\n")
        app = self.box.app()
        lesson = app.catalog().lesson("1.1")
        result = runner.run_check(app, lesson.checks["1.1a"], lesson=lesson, station_id="1.1a")
        self.assertEqual(result.outcome, "problem")
        line = (folder / "lesson.py").read_text(encoding="utf-8").splitlines().index(
            "    raise ValueError('lesson bug')") + 1
        self.assertEqual(result.problem["where"],
                         f"stages/01-foundations/01-create-and-view/lesson.py 第 {line} 行")
        self.assertIn("ValueError: lesson bug", result.problem["summary"])

    # -- control flow ---------------------------------------------------------
    def test_stop_ends_the_check_early(self):
        def check(ctx):
            ctx.fail("先决条件不满足")
            ctx.stop()
            ctx.ok("到不了这里")

        result = self.run_check(check)
        self.assertEqual(result.outcome, "not_yet")
        self.assertEqual(result.oks, [])

    def test_stop_after_only_successes_is_a_pass(self):
        def check(ctx):
            ctx.ok("够了")
            ctx.stop()

        self.assertEqual(self.run_check(check).outcome, "passed")

    def test_cancel_and_usage_problems_pass_through(self):
        def asks(ctx):
            ctx.ask("问题？", "x")

        with self.assertRaises(Cancelled):
            self.run_check(asks, inputs=[])
        with self.assertRaises(UsageProblem):
            self.run_check(asks, noninteractive=True)

        def interrupted(ctx):
            raise KeyboardInterrupt()

        with self.assertRaises(Cancelled):
            self.run_check(interrupted)

    # -- details --------------------------------------------------------------
    def test_prints_of_a_check_are_captured_not_shown(self):
        def check(ctx):
            print("debug: " + str(ctx.home))
            ctx.ok("好")

        result = self.run_check(check)
        self.assertEqual(self.app.test_output.getvalue(), "")
        self.assertEqual(result.printed, "debug: ~\n")
        self.assertEqual(result.to_dict()["printed_by_check"], "debug: ~\n")

    def test_answers_are_counted_and_leftovers_mentioned(self):
        def check(ctx):
            ctx.ask("一？", "a")

        answers = ["a", "b", "c"]
        result = self.run_check(check, answers=answers, noninteractive=True)
        self.assertEqual((result.outcome, result.answers_used), ("passed", 1))
        self.assertEqual(answers, ["a", "b", "c"])
        self.assertIn("多给了 2 个 --answer", result.notes[-1])
        quiet = self.run_check(check, answers=answers, noninteractive=True, warn_unused=False)
        self.assertEqual(quiet.notes, [])
        self.assertTrue(result.interactive)

    def test_result_as_data(self):
        def check(ctx):
            ctx.ok("好")
            ctx.fail("缺", where="哪里", saw="什么")
            ctx.decide("k", "v")

        data = self.run_check(check).to_dict()
        self.assertEqual(data["outcome"], "not_yet")
        self.assertEqual(data["outcome_text"], "还没达标")
        self.assertEqual(data["exit_code"], 1)
        self.assertEqual(data["ok"], ["好"])
        self.assertEqual(data["missing"], [{"where": "哪里", "saw": "什么", "missing": "缺"}])
        self.assertNotIn("problem", data)

    def test_colour_only_when_the_console_allows_it(self):
        def check(ctx):
            ctx.ok("好")

        result = self.run_check(check)
        self.assertNotIn("\033[", self.render(result))
        self.app.console.color = True
        self.assertIn("\033[32m", self.render(result))


if __name__ == "__main__":
    unittest.main()
