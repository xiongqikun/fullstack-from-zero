"""The ``status`` command and PROGRESS.md."""

import unittest

import helpers


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def lessons(self, *ids):
        for lesson_id in ids:
            self.box.add_syllabus_lesson(lesson_id)

    def pass_station(self, station, now=helpers.NOW):
        self.box.flag(station)
        result = self.box.run("check", station, now=now)
        self.assertEqual(result.code, 0, result)

    # -- shape of the output --------------------------------------------------
    def test_no_command_is_status_plus_a_three_line_reminder(self):
        self.lessons("1.6")
        bare = self.box.run()
        explicit = self.box.run("status")
        self.assertEqual((bare.code, explicit.code), (0, 0))
        self.assertTrue(bare.out.startswith("学习进度 · 2026-11-19\n"))
        self.assertTrue(bare.out.startswith(explicit.out.rstrip("\n")))
        reminder = bare.out[len(explicit.out.rstrip("\n")):].strip("\n").split("\n")
        self.assertEqual(reminder, [
            "  做完一站 → python3 tools/course.py check 1.6a",
            "  卡住了   → python3 tools/course.py hint 1.6a",
            "  收工前   → python3 tools/course.py journal",
        ])
        self.assertNotIn("收工前", explicit.out)

    def test_empty_workspace(self):
        result = self.box.run()
        self.assertEqual(result.code, 0)
        self.assertIn("还没有找到课程", result.out)
        self.assertIn("check <站>", result.out)

    def test_position_and_next_step(self):
        self.lessons("1.6", "1.7")
        start = self.box.run("status")
        self.assertIn("你在：1.6 Git：第一次提交 · 第 1 站「第 a 站」（1.6a）", start.out)
        self.assertIn("下一步：打开 stages/01-foundations/06-first-commit/lesson.md，从头开始", start.out)
        # Nothing done anywhere yet: the sentence that starts the course.
        self.assertIn("下次可以对导师说“开始上课”。", start.out)
        self.assertIn("python3 tools/course.py check 1.6a", start.out)

        self.pass_station("1.6a")
        middle = self.box.run("status")
        self.assertIn("第 2 站「第 b 站」（1.6b）", middle.out)
        self.assertIn("从「第 2 站」接着做", middle.out)

        self.assertIn("下次可以对导师说“从 1.6b 继续”。", middle.out)

        self.box.run("check", "1.6b")
        self.box.run("check", "1.6b")
        retry = self.box.run("status")
        self.assertIn("1.6b 检查过 2 次，还没通过", retry.out)

        for _ in range(4):
            self.box.run("hint", "1.6b", noninteractive=True)
        seen = self.box.run("status")
        self.assertIn("1.6b 你看过完整答案，还没运行检查", seen.out)

    def test_all_done(self):
        self.lessons("1.7")
        self.pass_station("1.7a")
        self.pass_station("1.7b")
        wrapup = self.box.run()
        # The last lesson's closing steps: the first line follows the next step
        # like everywhere else (M6, second pass of 2026-11-20).
        self.assertIn("你在：1.7 Git：看懂改了什么 · 收尾", wrapup.out)
        self.assertIn("下一个落脚点是阶段 1 结束（学完 1.7）：站都通过了，还差 1.7 课的收尾", wrapup.out)
        self.assertIn("下一步：1.7 课的 2 站都通过了。收尾先做全课检查：python3 tools/course.py check 1.7。"
                      "下次可以对导师说“从 1.7 的收尾继续”。", wrapup.out)
        self.assertEqual(self.box.run("check", "1.7").code, 0)
        result = self.box.run()
        self.assertIn("已有的课程的站都通过了（2/2 站）。", result.out)
        # The real number of the next stage, the sentence of lesson 1.16 (E2).
        self.assertIn("下一步：已有的课程都学完了。下一阶段的课还要准备。下次可以对导师说“准备阶段 2”。",
                      result.out)
        self.assertNotIn("继续下一阶段", result.out)
        self.assertIn("check <站>", result.out)

    # -- the individual lines -------------------------------------------------
    def test_stations_left_to_the_next_landing_point(self):
        self.lessons("1.4", "1.5", "1.6", "1.10")
        first = self.box.run("status")
        # Lesson 1.4 has three stations (plan section 4, changed 2026-11-19).
        self.assertIn("下一个落脚点是小关卡 gate-a「终端与文档关卡」（学完 1.5），还有 5 站", first.out)
        self.assertIn("阶段 1 工程师的基本功：已完成 0/10 站（0%）", first.out)
        for station in ("1.4a", "1.4b", "1.4c", "1.5a"):
            self.pass_station(station)
        self.assertIn("（学完 1.5），还有 1 站", self.box.run("status").out)
        self.pass_station("1.5b")
        # At 1.5's closing steps the landing line still follows 1.5 (M6, second pass).
        closing = self.box.run("status")
        self.assertIn("下一个落脚点是小关卡 gate-a「终端与文档关卡」（学完 1.5）：站都通过了，还差 1.5 课的收尾",
                      closing.out)
        self.assertEqual(self.box.run("check", "1.5").code, 0)
        after = self.box.run("status")
        self.assertIn("下一个落脚点是小关卡 gate-b「本地 Git 关卡」（学完 1.10），还有 5 站", after.out)
        self.assertIn("已完成 5/10 站（50%）", after.out)

    def test_end_of_stage_is_a_landing_point_for_lessons_outside_the_syllabus(self):
        self.box.add_example()
        result = self.box.run("status")
        self.assertIn("下一个落脚点是阶段 99 结束（学完 99.1），还有 2 站", result.out)

    def test_hours_logged(self):
        self.lessons("1.6")
        first = self.box.run("status", now="2026-11-19T10:00:00")
        self.assertIn("累计学习：今天是第一次记录", first.out)
        self.box.run("check", "1.6a", now="2026-11-19T10:40:00")
        self.box.run("check", "1.6a", now="2026-11-20T09:00:00")
        result = self.box.run("status", now="2026-11-20T09:35:00")
        self.assertIn("累计学习：约 1.2 小时（2 次）", result.out)

    def test_review_items_due(self):
        self.lessons("1.6")
        self.pass_station("1.6a", now="2026-11-19T10:00:00")
        early = self.box.run("status", now="2026-11-20T10:00:00")
        self.assertIn("到期的复习：0 条（下一次：2026-11-21）", early.out)
        due = self.box.run("status", now="2026-11-21T10:00:00")
        self.assertIn("到期的复习：1 条 → python3 tools/course.py review", due.out)

    def test_days_since_the_last_session_and_the_return_routine(self):
        self.lessons("1.6")
        first = self.box.run("status", now="2026-11-19T10:00:00")
        self.assertNotIn("距离上次学习", first.out)
        next_day = self.box.run("status", now="2026-11-20T10:00:00")
        self.assertIn("距离上次学习：1 天", next_day.out)
        self.assertNotIn("回归流程", next_day.out)
        ten = self.box.run("status", now="2026-11-30T10:00:00")
        self.assertIn("距离上次学习：10 天", ten.out)
        self.assertNotIn("回归流程", ten.out)
        back = self.box.run("status", now="2026-12-11T10:00:00")
        self.assertIn("距离上次学习：11 天", back.out)
        self.assertIn("回归流程", back.out)
        same_day = self.box.run("status", now="2026-12-11T18:00:00")
        self.assertIn("距离上次学习：11 天", same_day.out)
        self.assertIn("回归流程", same_day.out)

    def test_notice_at_seventy_percent_of_the_stage(self):
        self.lessons("1.6", "1.7")
        for station in ("1.6a", "1.6b", "1.6c"):
            self.pass_station(station)
        self.assertNotIn("70%", self.box.run("status").out)
        self.pass_station("1.7a")
        notice = self.box.run("status")
        self.assertIn("阶段 1 已完成 70% 以上（4/5 站）", notice.out)
        self.assertIn("下一阶段的课程需要提前准备", notice.out)
        self.pass_station("1.7b")
        self.assertNotIn("70%", self.box.run("status").out)

    def test_no_seventy_percent_notice_when_the_next_stage_is_already_there(self):
        # E3: stage 1 exists while the learner is in stage 0, so nothing needs
        # preparing and the notice would be untrue.
        self.lessons("0.1", "0.2", "1.6")
        for station in ("0.1a", "0.1b", "0.1c", "0.2a", "0.2b"):
            self.pass_station(station)
        out = self.box.run("status").out
        self.assertIn("阶段 0 起步：已完成 5/6 站（83%）", out)
        self.assertNotIn("70%", out)
        self.assertNotIn("需要提前准备", out)

    def test_cold_redo_due(self):
        self.lessons("1.6")
        for _ in range(4):
            self.box.run("hint", "1.6a", noninteractive=True)
        self.pass_station("1.6a")
        self.assertNotIn("到期的重做", self.box.run("status", now="2026-11-21T10:00:00").out)
        due = self.box.run("status", now="2026-11-22T10:00:00")
        self.assertIn("到期的重做：1.6a", due.out)
        self.box.run("check", "1.6a", now="2026-11-22T10:05:00")
        self.assertNotIn("到期的重做", self.box.run("status", now="2026-11-22T10:06:00").out)

    def test_broken_lessons_are_mentioned_and_do_not_stop_the_report(self):
        self.lessons("1.6")
        self.box.add_lesson("META = {\n", "01-foundations", "07-read-diff")
        result = self.box.run("status")
        self.assertEqual(result.code, 0)
        self.assertIn("你在：1.6", result.out)
        self.assertIn("有 1 课加载失败，暂时用不了：1.7", result.out)

    def test_corrupt_state(self):
        self.lessons("1.6")
        (self.box.root / "learner").mkdir()
        (self.box.root / "learner" / "state.json").write_text("][")
        for argv in ([], ["status"], ["status", "--write"]):
            result = self.box.run(*argv)
            self.assertEqual(result.code, 2, argv)
            self.assertIn("检查器出问题", result.out)
            self.assertIn("state.json.bad", result.out)
            self.assertNotIn("Traceback", result.text)
        self.assertEqual((self.box.root / "learner" / "state.json").read_text(), "][")
        self.assertFalse((self.box.root / "PROGRESS.md").exists())

    # -- PROGRESS.md ----------------------------------------------------------
    def test_write_regenerates_progress_md(self):
        self.lessons("1.6", "1.7")
        self.assertFalse((self.box.root / "PROGRESS.md").exists())
        self.box.run("status")
        self.assertFalse((self.box.root / "PROGRESS.md").exists())
        self.pass_station("1.6a")
        self.box.run("check", "1.6b")
        for _ in range(4):
            self.box.run("hint", "1.6c", noninteractive=True)
        self.pass_station("1.6c")
        result = self.box.run("status", "--write", now="2026-11-19T12:30:00")
        self.assertEqual(result.code, 0)
        self.assertIn("已更新 PROGRESS.md。", result.out)
        text = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# 学习进度\n"))
        self.assertIn("status --write` 生成", text)
        self.assertIn("生成时间：2026-11-19 12:30", text)
        self.assertIn("## 阶段 1 工程师的基本功（2/5 站）", text)
        self.assertIn("| 1.6 Git：第一次提交 | 1.6a 第 a 站 | 通过 | 2026-11-19 | 1 | 0 |", text)
        self.assertIn("| 1.6 Git：第一次提交 | 1.6b 第 b 站 | 试过，还没通过 |  | 1 | 0 |", text)
        self.assertIn("| 1.6 Git：第一次提交 | 1.6c 第 c 站 | 带扶手完成 | 2026-11-19 | 1 | 4 |", text)
        self.assertIn("| 1.7 Git：看懂改了什么 | 1.7a 第 a 站 | 还没开始 |  | 0 | 0 |", text)
        self.assertIn("- 你在：1.6", text)
        self.assertIn("## 复习", text)
        self.assertNotIn(str(self.box.home), text)

        (self.box.root / "PROGRESS.md").write_text("手改的内容\n", encoding="utf-8")
        self.box.run("status", "--write", now="2026-11-19T12:40:00")
        again = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertNotIn("手改的内容", again)
        self.assertIn("生成时间：2026-11-19 12:40", again)
        self.assertEqual(self.box.events("progress-written")[-1]["file"], "PROGRESS.md")

    def test_progress_md_lists_exam_results_when_there_are_some(self):
        self.lessons("1.6")
        self.box.add_syllabus_lesson("1.7", extra=EXAM_1_7)
        self.box.run("status")
        app = self.box.app()
        state = app.store.load()
        state["exams"] = {"gate-b": {
            "1.7-x1": {"form": "A", "result": "fail", "date": "2026-11-19"},
        }}
        app.store.save(state)
        self.box.run("status", "--write")
        text = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("## 关卡", text)
        # Every gate, in order, in the words of the exam listing (one rule).
        self.assertIn("- gate-b 小关卡「本地 Git 关卡」（1.7 课）：实操题通过了 0/1 课；"
                      "下一场 1 题，预计 4 分钟", text)
        self.assertIn("- gate-0 起步小关卡（0.1 到 0.4 课）：考题还没写好", text)
        self.assertLess(text.index("- gate-b"), text.index("- gate-1"))

    def test_progress_md_shows_a_gate_waiting_for_its_explain_back(self):
        self.box.add_syllabus_lesson("1.7", extra=EXAM_1_7)
        self.box.run("status")
        app = self.box.app()
        state = app.store.load()
        state["exams"] = {"gate-b": {"1.7-x1": {"form": "A", "result": "pass", "date": "2026-11-19"}}}
        app.store.save(state)
        self.box.run("status", "--write")
        text = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("- gate-b 小关卡「本地 Git 关卡」（1.7 课）：实操题都通过了，还差讲解题", text)
        state = app.store.load()
        state["explain"] = {"gate-b": {"result": "pass", "date": "2026-11-20"}}
        app.store.save(state)
        self.box.run("status", "--write")
        text = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("- gate-b 小关卡「本地 Git 关卡」（1.7 课）：通过了（讲解题 2026-11-20）", text)


EXAM_1_7 = '''
def _xbuild(sc):
    sc.write("a.txt", "a")


def _xgrade(ctx):
    ctx.ok("好")


EXAM = [{"id": "1.7-x1", "gate": "gate-b", "title": "看改动", "minutes": 4, "build": _xbuild,
         "grade": _xgrade, "task": {"A": "做 A", "B": "做 B"}}]
'''

if __name__ == "__main__":
    unittest.main()
