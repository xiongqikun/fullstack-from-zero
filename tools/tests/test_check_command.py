"""The ``check`` command: outcomes, exit codes, state, log and last-result."""

import json
import unittest

import helpers

BOOM = '''
def boom(ctx):
    ctx.ok("这一条不算数")
    raise RuntimeError("lesson bug " + str(ctx.home))

checks["1.6b"] = boom
'''

ASKING = '''
def asking(ctx):
    ctx.quiz("选哪个？", ["甲", "乙"], "B")
    if ctx.ask("几个？", 3):
        ctx.decide("commit_signing", "off")

checks["1.6c"] = asking
'''


class CheckStationTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=BOOM + ASKING)
        self.box.add_syllabus_lesson("1.7")

    def test_not_yet_then_passed(self):
        first = self.box.run("check", "1.6a")
        self.assertEqual(first.code, 1)
        self.assertIn("❌ 还没达标 · 1.6a 第 a 站", first.out)
        self.assertIn("看了哪里：练习场的 flags 文件夹", first.out)
        self.assertIn("看到了什么：没有 1.6a.ok", first.out)
        self.assertIn("还缺什么：还没有完成标记", first.out)
        self.assertIn("python3 tools/course.py hint 1.6a", first.out)
        record = self.box.state()["stations"]["1.6a"]
        self.assertEqual((record["status"], record["attempts"], record["first_pass"]),
                         ("open", 1, None))

        self.box.flag("1.6a")
        second = self.box.run("check", "1.6a", now="2026-11-19T10:20:00")
        self.assertEqual(second.code, 0)
        self.assertIn("✅ 通过 · 1.6a 第 a 站", second.out)
        self.assertIn("存档点 1.6a：到这里可以安全停下。", second.out)
        self.assertIn("下一站：1.6b", second.out)
        record = self.box.state()["stations"]["1.6a"]
        self.assertEqual((record["status"], record["attempts"]), ("passed", 2))
        self.assertEqual(record["first_pass"], "2026-11-19T10:20:00")
        self.assertEqual(record["highest_hint"], 0)

    def test_every_attempt_is_logged_with_outcome_and_hint_level(self):
        self.box.run("check", "1.6a")
        self.box.run("hint", "1.6a")
        self.box.run("hint", "1.6a")
        self.box.flag("1.6a")
        self.box.run("check", "1.6a", "--confidence", "2")
        events = self.box.events("check")
        self.assertEqual([(e["station"], e["outcome"], e["hint_level"], e["attempt"])
                          for e in events],
                         [("1.6a", "not_yet", 0, 1), ("1.6a", "passed", 2, 2)])
        self.assertEqual(events[1]["confidence"], 2)
        self.assertTrue(all(e["ts"] == helpers.NOW for e in events))

    def test_last_result_is_written_for_the_tutor(self):
        self.box.run("check", "1.6a")
        result = self.box.last_result()
        self.assertEqual((result["target"], result["kind"], result["lesson"]),
                         ("1.6a", "station", "1.6"))
        self.assertEqual((result["outcome"], result["outcome_text"], result["exit_code"]),
                         ("not_yet", "还没达标", 1))
        self.assertEqual(result["missing"][0]["saw"], "没有 1.6a.ok")
        self.assertEqual((result["attempts"], result["status"], result["highest_hint"]),
                         (1, "open", 0))

    def test_raising_check_is_a_checker_problem_exit_2_no_traceback(self):
        result = self.box.run("check", "1.6b")
        self.assertEqual(result.code, 2)
        self.assertIn("⚠️ 检查器出问题 · 1.6b", result.out)
        self.assertIn("这不是你的错", result.out)
        self.assertIn("RuntimeError", result.out)
        self.assertIn("stages/01-foundations/06-first-commit/lesson.py 第", result.out)
        self.assertIn("你的进度没有受影响", result.out)
        self.assertNotIn("Traceback", result.text)
        self.assertNotIn('File "', result.text)
        self.assertNotIn(str(self.box.home), result.text)
        self.assertEqual(result.err, "")
        # not counted as an attempt of the learner
        self.assertNotIn("1.6b", self.box.state()["stations"])
        stored = self.box.last_result()
        self.assertEqual(stored["outcome"], "problem")
        self.assertIn("Traceback", stored["problem"]["detail"])
        self.assertNotIn(str(self.box.home), json.dumps(stored, ensure_ascii=False))
        self.assertEqual(self.box.events("check")[-1]["outcome"], "problem")

    def test_station_without_a_check_function_is_a_checker_problem(self):
        self.box.add_syllabus_lesson("1.8", extra='del checks["1.8a"]\n')
        result = self.box.run("check", "1.8a")
        self.assertEqual(result.code, 2)
        self.assertIn("检查器出问题", result.out)

    def test_questions_answered_at_the_terminal(self):
        result = self.box.run("check", "1.6c", inputs=["b", "３ 个"], tty=False)
        self.assertEqual(result.code, 0)
        self.assertIn("问：选哪个？", result.out)
        self.assertIn("  B. 乙", result.out)
        self.assertEqual(self.box.state()["decisions"], {"commit_signing": "off"})
        self.assertTrue(self.box.events("check")[-1]["interactive"])

    def test_questions_answered_with_answer_flags(self):
        result = self.box.run("check", "1.6c", "--answer", "A", "--answer", "3",
                              noninteractive=True)
        self.assertEqual(result.code, 1)
        self.assertIn("你选的是 A（甲）", result.out)
        self.assertEqual(self.box.state()["decisions"], {})
        result = self.box.run("check", "1.6c", "--answer", "b", "--answer", "三",
                              noninteractive=True)
        self.assertEqual(result.code, 0)

    def test_missing_answers_in_no_prompt_mode_is_a_usage_error(self):
        result = self.box.run("check", "1.6c", noninteractive=True)
        self.assertEqual(result.code, 64)
        self.assertIn("--answer", result.err)
        self.assertEqual(self.box.events("check"), [])

    def test_end_of_input_and_ctrl_c_are_polite_and_exit_1(self):
        for inputs in ([], ["b"], [KeyboardInterrupt], ["b", KeyboardInterrupt]):
            result = self.box.run("check", "1.6c", inputs=inputs)
            self.assertEqual(result.code, 1, inputs)
            self.assertIn("已取消", result.out)
            self.assertNotIn("Traceback", result.text)
        self.assertEqual(self.box.events("check"), [])
        self.assertNotIn("1.6c", self.box.state()["stations"])

    def test_confidence_is_asked_once_at_a_terminal(self):
        first = self.box.run("check", "1.6a", inputs=["4"], tty=True)
        self.assertIn("有多大把握", first.out)
        self.assertEqual(self.box.state()["stations"]["1.6a"]["confidence"], 4)
        second = self.box.run("check", "1.6a", inputs=[], tty=True)
        self.assertNotIn("有多大把握", second.out)
        self.assertEqual(second.code, 1)

    def test_confidence_enter_skips_and_nonsense_is_ignored(self):
        self.box.run("check", "1.6a", inputs=[""], tty=True)
        self.assertIsNone(self.box.state()["stations"]["1.6a"]["confidence"])
        self.box.run("check", "1.7a", inputs=["9"], tty=True)
        self.assertIsNone(self.box.state()["stations"]["1.7a"]["confidence"])

    def test_confidence_is_not_asked_without_a_terminal_or_in_no_prompt_mode(self):
        piped = self.box.run("check", "1.6a", inputs=[], tty=False)
        self.assertNotIn("有多大把握", piped.out)
        self.assertEqual(piped.code, 1)
        silent = self.box.run("check", "1.7a", noninteractive=True)
        self.assertNotIn("有多大把握", silent.out)

    def test_failing_again_after_a_pass_keeps_the_pass(self):
        self.box.flag("1.6a")
        self.box.run("check", "1.6a")
        (self.box.playground / "flags" / "1.6a.ok").unlink()
        again = self.box.run("check", "1.6a", now="2026-11-20T09:00:00")
        self.assertEqual(again.code, 1)
        self.assertIn("之前已经通过（2026-11-19），进度不受这次结果影响", again.out)
        record = self.box.state()["stations"]["1.6a"]
        self.assertEqual((record["status"], record["first_pass"]), ("passed", helpers.NOW))

    def test_first_pass_enrols_the_fluent_review_items_of_that_station(self):
        self.box.flag("1.6a")
        result = self.box.run("check", "1.6a")
        self.assertIn("有 1 道复习题排进了复习计划，2026-11-21 起可以做", result.out)
        self.assertEqual(self.box.state()["review"],
                         {"1.6-r2": {"box": 1, "due": "2026-11-21", "history": []}})
        self.box.run("check", "1.6a")
        self.assertEqual(sorted(self.box.state()["review"]), ["1.6-r2"])

    def test_typed_ids_are_normalised(self):
        self.box.flag("1.6a")
        for typed in ("1.6A", "１.６ａ", " 1.6a "):
            self.assertEqual(self.box.run("check", typed).code, 0, typed)

    def test_unknown_targets_are_usage_errors(self):
        cases = {"1.6z": "1.6a 1.6b 1.6c", "9.9": "没有 9.9 这一课", "9.9a": "没有 9.9 这一课",
                 "abc": "看不懂"}
        for target, expected in cases.items():
            result = self.box.run("check", target)
            self.assertEqual(result.code, 64, target)
            self.assertIn(expected, result.err)
            self.assertEqual(result.out, "")
        self.assertEqual(self.box.run("check").code, 64)
        self.assertEqual(self.box.run("check", "1.6a", "--confidence", "7").code, 64)
        self.assertEqual(self.box.run("check", "1.6a", "--nope").code, 64)

    def test_broken_lesson_is_a_checker_problem(self):
        self.box.add_lesson("META = {\n", "01-foundations", "09-gitignore")
        result = self.box.run("check", "1.9a")
        self.assertEqual(result.code, 2)
        self.assertIn("检查器出问题", result.out)
        self.assertIn("1.9 课的课程模块加载失败", result.out)
        self.assertNotIn("Traceback", result.text)
        self.assertEqual(self.box.run("check", "1.6a").code, 1)

    def test_corrupt_state_is_reported_with_a_recovery_instruction(self):
        folder = self.box.root / "learner"
        folder.mkdir()
        (folder / "state.json").write_text("{{{ not json", encoding="utf-8")
        result = self.box.run("check", "1.6a")
        self.assertEqual(result.code, 2)
        self.assertIn("检查器出问题", result.out)
        self.assertIn("这不是你的错", result.out)
        self.assertIn("state.json.bad", result.out)
        self.assertNotIn("Traceback", result.text)
        self.assertEqual((folder / "state.json").read_text(encoding="utf-8"), "{{{ not json")

    def test_missing_state_is_created_on_first_use(self):
        self.assertFalse((self.box.root / "learner").exists())
        self.assertEqual(self.box.run("check", "1.6a").code, 1)
        self.assertTrue((self.box.root / "learner" / "state.json").is_file())

    def test_a_check_counts_as_study_time(self):
        self.box.run("check", "1.6a", now="2026-11-19T10:00:00")
        self.box.run("check", "1.6a", now="2026-11-19T10:30:00")
        self.box.run("check", "1.6a", now="2026-11-19T14:00:00")
        sessions = self.box.state()["sessions"]
        self.assertEqual([(s["date"], s["minutes"]) for s in sessions],
                         [("2026-11-19", 30), ("2026-11-19", 0)])


class CheckLessonTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=ASKING)
        self.box.add_syllabus_lesson("1.7")

    def test_open_stations_are_checked_and_passed_ones_are_listed(self):
        self.box.flag("1.6a")
        self.box.run("check", "1.6a")
        (self.box.playground / "flags" / "1.6a.ok").unlink()
        self.box.flag("1.6b")
        result = self.box.run("check", "1.6", "--answer", "B", "--answer", "4",
                              noninteractive=True, now="2026-11-19T11:00:00")
        self.assertEqual(result.code, 1)
        self.assertIn("全课检查 · 1.6", result.out)
        self.assertIn("✅ 1.6a 第 a 站：已通过（2026-11-19）", result.out)
        self.assertIn("✅ 通过 · 1.6b", result.out)
        self.assertIn("❌ 还没达标 · 1.6c", result.out)
        self.assertIn("❌ 还没达标 · 全课 1.6：还有 1 站没通过（1.6c）", result.out)
        self.assertNotIn("存档点", result.out)
        stored = self.box.last_result()
        self.assertEqual((stored["target"], stored["kind"], stored["outcome"]),
                         ("1.6", "lesson", "not_yet"))
        self.assertEqual([item["outcome"] for item in stored["stations"]],
                         ["passed_earlier", "passed", "not_yet"])
        self.assertIn("1.6c", stored["details"])

        done = self.box.run("check", "1.6", "--answer", "B", "--answer", "3",
                            noninteractive=True, now="2026-11-19T11:05:00")
        self.assertEqual(done.code, 0)
        self.assertIn("✅ 通过 · 全课 1.6：3 站都已通过", done.out)
        self.assertIn("在小标题「GIT-01 示例规则 GIT-01」「GIT-02 示例规则 GIT-02」下面各用自己的话写一两句", done.out)
        self.assertIn("python3 tools/course.py journal", done.out)
        self.assertIn("下一课：1.7", done.out)
        self.assertEqual(self.box.events("lesson-check")[-1]["outcome"], "passed")

    def test_an_assisted_station_is_listed_with_its_redo_window(self):
        for _ in range(4):
            self.box.run("hint", "1.7a", noninteractive=True)       # level 4: the full answer
        for station in ("1.7a", "1.7b"):
            self.box.flag(station)
        self.box.run("check", "1.7a", now="2026-11-19T11:00:00")
        self.assertEqual(self.box.state()["stations"]["1.7a"]["status"], "assisted")
        result = self.box.run("check", "1.7", now="2026-11-19T11:10:00")
        self.assertEqual(result.code, 0)
        self.assertIn("✅ 1.7a 第 a 站：带扶手完成（2026-11-19），"
                      "还要在 2026-11-22 到 2026-11-26 之间不看提示重做一遍", result.out)
        self.assertNotIn("1.7a 第 a 站：已通过", result.out)
        self.assertIn("✅ 通过 · 全课 1.7：2 站都已通过", result.out)
        self.assertIn("其中 1.7a 是带扶手完成的", result.out)
        # After the cold redo it is listed as plainly passed again.
        self.box.run("check", "1.7a", now="2026-11-23T09:00:00")
        later = self.box.run("check", "1.7", now="2026-11-23T09:05:00")
        self.assertIn("✅ 1.7a 第 a 站：已通过（2026-11-19）", later.out)
        self.assertNotIn("带扶手完成", later.out)

    def test_again_runs_passed_stations_once_more(self):
        for station in ("1.7a", "1.7b"):
            self.box.flag(station)
        self.assertEqual(self.box.run("check", "1.7").code, 0)
        (self.box.playground / "flags" / "1.7a.ok").unlink()
        self.assertEqual(self.box.run("check", "1.7").code, 0)
        again = self.box.run("check", "1.7", "--again")
        self.assertEqual(again.code, 1)
        self.assertIn("还有 1 站没通过（1.7a）", again.out)
        self.assertEqual(self.box.state()["stations"]["1.7a"]["status"], "passed")

    def test_a_checker_problem_in_one_station_gives_exit_2(self):
        self.box.add_syllabus_lesson("1.8", extra="checks['1.8b'] = lambda ctx: 1 / 0\n")
        self.box.flag("1.8a")
        result = self.box.run("check", "1.8")
        self.assertEqual(result.code, 2)
        self.assertIn("✅ 通过 · 1.8a", result.out)
        self.assertIn("⚠️ 检查器出问题 · 1.8b", result.out)
        self.assertIn("全课 1.8：有 1 站的检查器出了问题（1.8b）", result.out)
        self.assertNotIn("Traceback", result.text)

    def test_lesson_without_rules_and_last_lesson(self):
        self.box.add_syllabus_lesson("1.3")
        for station in ("1.3a", "1.3b", "1.7a", "1.7b"):
            self.box.flag(station)
        no_rules = self.box.run("check", "1.3")
        self.assertIn("收尾还有一件小事：", no_rules.out)
        self.assertNotIn("notes/", no_rules.out)
        last = self.box.run("check", "1.7")
        self.assertEqual(last.code, 0)
        self.assertNotIn("下一课", last.out)

    def test_unused_answers_are_mentioned_once(self):
        for station in ("1.7a", "1.7b"):
            self.box.flag(station)
        result = self.box.run("check", "1.7", "--answer", "x", noninteractive=True)
        self.assertEqual(result.out.count("多给了 1 个 --answer"), 1)


if __name__ == "__main__":
    unittest.main()
