"""E2: one answer to "what comes next" (``status.next_step``) and its three users.

``check`` (after a station and after the whole-lesson check), ``status`` (the
line 「下一步：……」) and ``journal`` (the default of 下次从哪开始) must say the
same canonical sentence of COMMON section 2.
"""

import json
import unittest

import helpers

from courselib import status as next_steps

EXAM_TASKS = '''
def _xbuild(sc):
    sc.write("a.txt", "a")


def _xgrade(ctx):
    ctx.ok("好")


def _xtask(number, gate):
    return {{"id": "{id}-x" + str(number), "gate": gate, "title": "{id} 题 " + str(number),
             "minutes": {minutes}, "build": _xbuild, "grade": _xgrade,
             "task": {{"A": "做 A", "B": "做 B"}}}}


EXAM = [{tasks}]
'''


def exam_extra(lesson_id, count, minutes=4):
    gate = helpers.syllabus.lesson_entry(lesson_id)["gate"]
    tasks = ", ".join(f"_xtask({n}, {gate!r})" for n in range(1, count + 1))
    return EXAM_TASKS.format(id=lesson_id, tasks=tasks, minutes=minutes)


class NextStepCase(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def lesson(self, lesson_id, tasks=0, minutes=4):
        extra = exam_extra(lesson_id, tasks, minutes) if tasks else ""
        self.box.add_syllabus_lesson(lesson_id, extra=extra)

    def pass_station(self, station):
        self.box.flag(station)
        result = self.box.run("check", station)
        self.assertEqual(result.code, 0, result)
        return result

    def pass_lesson(self, lesson_id, whole=True):
        for station in helpers.syllabus.lesson_entry(lesson_id)["stations"]:
            self.pass_station(station)
        if whole:
            result = self.box.run("check", lesson_id)
            self.assertEqual(result.code, 0, result)
            return result
        return None

    def edit_state(self, **sections):
        path = self.box.root / "learner" / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state.update(sections)
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def step(self, **kwargs):
        app = self.box.app()
        return next_steps.next_step(app, app.store.load(), **kwargs)


class NextStepFunctionTest(NextStepCase):
    def test_nothing_done_yet_starts_the_course(self):
        self.lesson("1.6")
        step = self.step()
        self.assertEqual((step.kind, step.say, step.station), (next_steps.LESSON, "开始上课", "1.6a"))

    def test_an_open_station_of_a_begun_lesson(self):
        self.lesson("1.6")
        self.pass_station("1.6a")
        step = self.step()
        self.assertEqual((step.kind, step.say), (next_steps.STATION, "从 1.6b 继续"))
        # A failed attempt at the open station keeps the same sentence.
        self.box.run("check", "1.6b")
        self.assertEqual(self.step().say, "从 1.6b 继续")

    def test_closing_steps_after_the_last_station(self):
        self.lesson("1.6")
        self.lesson("1.7")
        self.pass_lesson("1.6", whole=False)
        step = self.step()
        self.assertEqual((step.kind, step.say, step.count),
                         (next_steps.WRAPUP, "从 1.6 的收尾继续", 3))
        self.assertIn("python3 tools/course.py check 1.6", step.text)

    def test_the_whole_lesson_check_is_remembered(self):
        self.lesson("1.6")
        self.lesson("1.7")
        self.pass_lesson("1.6")
        app = self.box.app()
        self.assertTrue(next_steps.lesson_checked(app.store.load(), "1.6"))
        self.assertEqual(self.step().say, "从 1.7 开始")
        # The first pass is kept; a later run of the whole-lesson check does not move it.
        first = app.store.load()["lesson_checks"]["1.6"]
        self.box.run("check", "1.6", now="2026-11-20T10:00:00")
        self.assertEqual(self.box.app().store.load()["lesson_checks"]["1.6"], first)

    def test_an_unchecked_lesson_no_longer_matters_once_the_next_one_is_begun(self):
        # Learners who finished a lesson before the tool remembered whole-lesson
        # checks: once they work in the next lesson, they are not sent back.
        self.lesson("1.6")
        self.lesson("1.7")
        self.pass_lesson("1.6", whole=False)
        self.pass_station("1.7a")
        self.assertEqual(self.step().say, "从 1.7b 继续")

    def test_reviews_due_come_first_and_name_the_step_after_them(self):
        self.lesson("1.6")
        self.pass_station("1.6a")
        app = self.box.app(now="2026-11-21T10:00:00")
        state = app.store.load()
        step = next_steps.next_step(app, state)
        self.assertEqual(step.kind, next_steps.REVIEW)
        self.assertEqual(step.count, 1)
        self.assertEqual(step.say, "从 1.6b 继续")
        self.assertEqual(step.then.kind, next_steps.STATION)
        self.assertEqual(next_steps.next_step(app, state, reviews=False).kind, next_steps.STATION)

    def test_a_due_gate_then_its_explain_back_then_the_next_lesson(self):
        self.lesson("1.10", tasks=1, minutes=7)
        self.lesson("1.11")
        self.pass_lesson("1.10")
        gate = self.step()
        self.assertEqual((gate.kind, gate.say, gate.count, gate.minutes),
                         (next_steps.GATE, "做小关卡 gate-b", 1, 7))
        self.edit_state(exams={"gate-b": {"1.10-x1": {"result": "pass", "date": "2026-11-20"}}})
        explain = self.step()
        self.assertEqual((explain.kind, explain.say), (next_steps.EXPLAIN, "请问我 gate-b 的讲解题"))
        self.assertIn("exam gate-b --explain pass", explain.text)
        self.edit_state(explain={"gate-b": {"result": "again", "date": "2026-11-21"}})
        self.assertIn("。上一次的讲解题在 2026-11-21 记为“再来一次”", self.step().text)
        self.edit_state(explain={"gate-b": {"result": "pass", "date": "2026-11-22"}})
        after = self.step()
        self.assertEqual((after.kind, after.say, after.gates), (next_steps.LESSON, "从 1.11 开始", []))

    def test_a_gate_never_blocks_the_next_lesson(self):
        self.lesson("1.10", tasks=1)
        self.lesson("1.11")
        self.pass_lesson("1.10")
        self.pass_station("1.11a")
        step = self.step()
        self.assertEqual((step.kind, step.say), (next_steps.STATION, "从 1.11b 继续"))
        self.assertEqual([gate.say for gate in step.gates], ["做小关卡 gate-b"])
        self.assertIn("它不挡下一课", step.gates[0].note)

    def test_end_of_the_stage_names_the_real_next_stage(self):
        self.lesson("0.4")
        self.pass_lesson("0.4")
        step = self.step()
        self.assertEqual((step.kind, step.say), (next_steps.STAGE_END, "准备阶段 1"))

    def test_no_lessons(self):
        self.assertEqual(self.step().kind, next_steps.NOTHING)

    def test_after_a_lesson_finished_out_of_order(self):
        # check 1.10 while 1.6 is still open: the answer is about 1.10.
        self.lesson("1.6")
        self.lesson("1.10", tasks=1)
        self.lesson("1.11")
        self.pass_lesson("1.10", whole=False)
        app = self.box.app()
        state = app.store.load()
        lesson = app.catalog().lesson("1.10")
        self.assertEqual(next_steps.next_step(app, state, after=lesson).say, "从 1.10 的收尾继续")
        self.assertEqual(next_steps.next_step(app, state).say, "从 1.6 开始")


class NextStepUsersTest(NextStepCase):
    def test_check_after_the_whole_lesson_with_an_explain_back_due(self):
        self.lesson("1.10", tasks=1)
        self.lesson("1.11")
        self.pass_lesson("1.10")
        self.edit_state(exams={"gate-b": {"1.10-x1": {"result": "pass", "date": "2026-11-20"}}})
        result = self.box.run("check", "1.10")
        self.assertIn("关卡 gate-b「本地 Git 关卡」的实操题都通过了，还差讲解题", result.out)
        self.assertIn("下次可以对导师说“请问我 gate-b 的讲解题”。", result.out)
        self.assertNotIn("下一课", result.out)

    def test_check_names_an_open_gate_next_to_the_next_lesson(self):
        self.lesson("1.5", tasks=1)
        self.lesson("1.6")
        self.lesson("1.7")
        self.pass_lesson("1.5")
        result = self.pass_lesson("1.6")
        self.assertIn("下一课：1.7「Git：看懂改了什么」。下次可以对导师说“从 1.7 开始”。", result.out)
        self.assertIn("关卡 gate-a「终端与文档关卡」还没有通过，它不挡下一课。"
                      "准备好了就对导师说“做小关卡 gate-a”。", result.out)

    def test_check_at_the_end_of_the_last_lesson(self):
        self.lesson("1.7")
        result = self.pass_lesson("1.7")
        self.assertIn("已有的课程都学完了。下次可以对导师说“准备阶段 2”。", result.out)

    def test_status_shows_the_open_gate_line(self):
        self.lesson("1.5", tasks=1)
        self.lesson("1.6")
        self.pass_lesson("1.5")
        self.pass_station("1.6a")
        out = self.box.run("status").out
        self.assertIn("下一步：打开 stages/01-foundations/06-first-commit/lesson.md，从「第 2 站」接着做；"
                      "做完运行 python3 tools/course.py check 1.6b。下次可以对导师说“从 1.6b 继续”。", out)
        self.assertIn("  小关卡 gate-a「终端与文档关卡」还没有通过，它不挡下一课。", out)

    def test_status_with_a_gate_due(self):
        self.lesson("1.5", tasks=2, minutes=5)
        self.lesson("1.6")
        self.pass_lesson("1.5")
        out = self.box.run("status").out
        self.assertIn("下一步：小关卡 gate-a「终端与文档关卡」：1 道实操题，预计 5 分钟，"
                      "讲解题另需约 10 分钟。开始考试：python3 tools/course.py exam gate-a。下次可以对导师说“做小关卡 gate-a”。", out)

    def test_status_with_reviews_due(self):
        self.lesson("1.6")
        self.pass_station("1.6a")
        out = self.box.run("status", now="2026-11-21T10:00:00").out
        self.assertIn("下一步：先做 1 条到期的复习：python3 tools/course.py review；然后打开 ", out)
        self.assertIn("下次可以对导师说“从 1.6b 继续”。", out)


if __name__ == "__main__":
    unittest.main()
