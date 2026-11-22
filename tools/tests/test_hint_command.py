"""The ``hint`` command: four levels, logging, 带扶手完成 and the cold redo."""

import unittest

import helpers


class HintTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6")

    def record(self, station="1.6a"):
        return self.box.state()["stations"][station]

    def test_each_call_reveals_the_next_level_and_logs_it(self):
        names = ["方向", "位置", "相似例子", "答案与解释"]
        for level in range(1, 5):
            result = self.box.run("hint", "1.6a", noninteractive=True,
                                  now=f"2026-11-19T10:0{level}:00")
            self.assertEqual(result.code, 0)
            self.assertIn(f"提示 {level}/4（{names[level - 1]}）· 1.6a 第 a 站", result.out)
            self.assertIn(f"{names[level - 1]} 1.6a", result.out)
            for other in range(1, 5):
                if other != level:
                    self.assertNotIn(f"{names[other - 1]} 1.6a", result.out)
            self.assertEqual(self.record()["highest_hint"], level)
        events = self.box.events("hint")
        self.assertEqual([(e["station"], e["level"]) for e in events],
                         [("1.6a", 1), ("1.6a", 2), ("1.6a", 3), ("1.6a", 4)])
        self.assertEqual([e["ts"][-5:] for e in events], ["01:00", "02:00", "03:00", "04:00"])
        self.assertEqual([e["scheduled_redo"] for e in events], [False, False, False, True])

    def test_early_levels_point_to_the_next_level_and_to_check(self):
        result = self.box.run("hint", "1.6a", noninteractive=True)
        self.assertIn("python3 tools/course.py check 1.6a", result.out)
        self.assertIn("看下一级（第 2 级：位置）", result.out)
        self.assertEqual(self.record()["status"], "open")
        self.assertNotIn("redo", self.record())

    def test_level_four_marks_assisted_and_schedules_a_redo_in_3_to_7_days(self):
        for _ in range(3):
            self.box.run("hint", "1.6a", noninteractive=True)
        self.assertEqual(self.record()["status"], "open")
        result = self.box.run("hint", "1.6a", noninteractive=True)
        self.assertIn("这是最后一级", result.out)
        self.assertIn("带扶手完成", result.out)
        self.assertIn("2026-11-22 到 2026-11-26 之间", result.out)
        record = self.record()
        self.assertEqual(record["status"], "assisted")
        self.assertEqual(record["redo"], {"after": "2026-11-22", "before": "2026-11-26", "done": None})
        self.assertEqual(record["last_hint"], helpers.NOW)
        self.assertEqual(self.box.events("hint")[-1]["status"], "assisted")

    def test_asking_again_after_level_four_repeats_it_without_a_new_redo(self):
        for _ in range(4):
            self.box.run("hint", "1.6a", noninteractive=True)
        again = self.box.run("hint", "1.6a", noninteractive=True, now="2026-11-20T08:00:00")
        self.assertIn("四级提示都已经看过了", again.out)
        self.assertIn("提示 4/4", again.out)
        self.assertEqual(self.record()["redo"]["after"], "2026-11-22")
        self.assertTrue(self.box.events("hint")[-1]["repeat"])

    def test_confirmation_before_the_answer_at_a_terminal(self):
        for _ in range(3):
            self.box.run("hint", "1.6a", inputs=[], tty=True)
        declined = self.box.run("hint", "1.6a", inputs=[""], tty=True)
        self.assertEqual(declined.code, 0)
        self.assertIn("第 4 级是完整答案", declined.out)
        self.assertIn("2026-11-22 之后", declined.out)
        self.assertIn("先不看答案", declined.out)
        self.assertNotIn("答案与解释 1.6a", declined.out)
        self.assertEqual((self.record()["highest_hint"], self.record()["status"]), (3, "open"))
        accepted = self.box.run("hint", "1.6a", inputs=["ｙ"], tty=True)
        self.assertIn("答案与解释 1.6a", accepted.out)
        self.assertEqual(self.record()["status"], "assisted")

    def test_yes_flag_skips_the_confirmation(self):
        for _ in range(3):
            self.box.run("hint", "1.6a", noninteractive=True)
        result = self.box.run("hint", "1.6a", "--yes", inputs=[], tty=True)
        self.assertNotIn("现在看吗", result.out)
        self.assertIn("答案与解释 1.6a", result.out)

    def test_leaving_the_confirmation_is_polite(self):
        for _ in range(3):
            self.box.run("hint", "1.6a", noninteractive=True)
        for inputs in ([], [KeyboardInterrupt]):
            result = self.box.run("hint", "1.6a", inputs=inputs, tty=True)
            self.assertEqual(result.code, 1)
            self.assertIn("已取消", result.out)
            self.assertNotIn("Traceback", result.text)
        self.assertEqual(self.record()["highest_hint"], 3)

    def test_again_shows_what_was_already_seen_and_nothing_new(self):
        nothing = self.box.run("hint", "1.6a", "--again", noninteractive=True)
        self.assertIn("还没有看过任何提示", nothing.out)
        self.box.run("hint", "1.6a", noninteractive=True)
        self.box.run("hint", "1.6a", noninteractive=True)
        again = self.box.run("hint", "1.6a", "--again", noninteractive=True)
        self.assertIn("方向 1.6a", again.out)
        self.assertIn("位置 1.6a", again.out)
        self.assertNotIn("相似例子 1.6a", again.out)
        self.assertEqual(self.record()["highest_hint"], 2)
        self.assertEqual(self.box.events("hint-again")[0]["levels"], 2)

    def test_pass_after_the_answer_stays_assisted_until_the_cold_redo(self):
        for _ in range(4):
            self.box.run("hint", "1.6a", noninteractive=True)
        self.box.flag("1.6a")
        same_day = self.box.run("check", "1.6a", now="2026-11-19T11:00:00")
        self.assertEqual(same_day.code, 0)
        self.assertIn("带扶手完成", same_day.out)
        self.assertIn("2026-11-22 到 2026-11-26 之间", same_day.out)
        self.assertEqual(self.record()["status"], "assisted")
        self.assertEqual(self.record()["first_pass"], "2026-11-19T11:00:00")

        too_early = self.box.run("check", "1.6a", now="2026-11-21T09:00:00")
        self.assertEqual(too_early.code, 0)
        self.assertEqual(self.record()["status"], "assisted")

        redo = self.box.run("check", "1.6a", now="2026-11-23T09:00:00")
        self.assertEqual(redo.code, 0)
        self.assertIn("不看提示的重做，通过了", redo.out)
        record = self.record()
        self.assertEqual((record["status"], record["redo"]["done"]), ("passed", "2026-11-23"))
        self.assertTrue(self.box.events("check")[-1]["redo_done"])

    def test_a_redo_on_a_day_with_hints_does_not_count(self):
        for _ in range(4):
            self.box.run("hint", "1.6a", noninteractive=True)
        self.box.flag("1.6a")
        self.box.run("hint", "1.6a", "--again", noninteractive=True, now="2026-11-23T08:00:00")
        self.box.run("check", "1.6a", now="2026-11-23T09:00:00")
        self.assertEqual(self.record()["status"], "assisted")
        self.box.run("check", "1.6a", now="2026-11-24T09:00:00")
        self.assertEqual(self.record()["status"], "passed")

    def test_reading_the_answer_after_a_clean_pass_changes_nothing(self):
        self.box.flag("1.6a")
        self.box.run("check", "1.6a")
        for _ in range(4):
            result = self.box.run("hint", "1.6a", inputs=[], tty=True)
            self.assertEqual(result.code, 0)
            self.assertNotIn("现在看吗", result.out)
        record = self.record()
        self.assertEqual((record["status"], record["highest_hint"]), ("passed", 4))
        self.assertNotIn("redo", record)

    def test_failed_check_after_hints_points_to_the_next_level(self):
        self.box.run("hint", "1.6a", noninteractive=True)
        result = self.box.run("check", "1.6a")
        self.assertIn("已经看过 1/4 级", result.out)
        for _ in range(3):
            self.box.run("hint", "1.6a", noninteractive=True)
        result = self.box.run("check", "1.6a")
        self.assertIn("四级提示你都看过了", result.out)

    def test_hints_are_per_station(self):
        self.box.run("hint", "1.6a", noninteractive=True)
        result = self.box.run("hint", "1.6b", noninteractive=True)
        self.assertIn("提示 1/4（方向）· 1.6b", result.out)

    def test_usage_errors(self):
        for argv in (["hint"], ["hint", "1.6"], ["hint", "1.6z"], ["hint", "what"]):
            result = self.box.run(*argv, noninteractive=True)
            self.assertEqual(result.code, 64, argv)
        self.assertIn("站点编号", self.box.run("hint", "1.6").err)

    def test_unusable_hints_are_a_checker_problem(self):
        self.box.add_syllabus_lesson("1.7", extra='HINTS["1.7a"] = ["只有", "三条", "提示"]\n')
        result = self.box.run("hint", "1.7a", noninteractive=True)
        self.assertEqual(result.code, 2)
        self.assertIn("检查器出问题", result.out)
        self.assertIn("这不是你的错", result.out)
        self.assertNotIn("Traceback", result.text)

    def test_multi_line_hints_keep_their_lines(self):
        self.box.add_syllabus_lesson(
            "1.8", extra='HINTS["1.8a"][0] = "第一行\\n    git status\\n第三行"\n')
        result = self.box.run("hint", "1.8a", noninteractive=True)
        self.assertIn("  第一行\n      git status\n  第三行", result.out)


if __name__ == "__main__":
    unittest.main()
