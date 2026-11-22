"""Integration of the two batches of 2026-11-19 (writer ``tools-integrate``).

What crosses the files of the five writers: the gate rule and the
explain-back record as ``check``, ``status``, ``journal``, ``exam`` and
PROGRESS.md show them through a whole gate; the gate names of COMMON.md
section 3 in every command; the closing steps ``check`` lists; the entrance
seen from a check (``ctx.show(..., entrance=False)``); ``validate
--complete`` under the one-task-per-lesson rule.
"""

import json
import os
import unittest

import helpers
from test_entrance import Layout

from courselib import status as next_steps
from courselib import syllabus
from courselib.commands import check as check_command
from courselib.context import CheckContext

EXAM_TASKS = '''
def _xbuild(sc):
    sc.write("a.txt", "a")


def _xgrade(ctx):
    if ctx.is_file(ctx.scenario().path / "done.ok"):
        ctx.ok("做完了")
    else:
        ctx.fail("还没做完", where="考题文件夹", saw="没有 done.ok")


def _xtask(number, gate):
    return {{"id": "{id}-x" + str(number), "gate": gate, "title": "{id} 题 " + str(number),
             "minutes": {minutes}, "build": _xbuild, "grade": _xgrade,
             "task": {{"A": "做 A", "B": "做 B"}}}}


EXAM = [{tasks}]
'''


def exam_extra(lesson_id, count=1, minutes=4):
    gate = syllabus.lesson_entry(lesson_id)["gate"]
    tasks = ", ".join(f"_xtask({n}, {gate!r})" for n in range(1, count + 1))
    return EXAM_TASKS.format(id=lesson_id, tasks=tasks, minutes=minutes)


class Case(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def lesson(self, lesson_id, tasks=0, minutes=4):
        self.box.add_syllabus_lesson(lesson_id, extra=exam_extra(lesson_id, tasks, minutes)
                                     if tasks else "")

    def pass_lesson(self, lesson_id):
        for station in syllabus.lesson_entry(lesson_id)["stations"]:
            self.box.flag(station)
            self.assertEqual(self.box.run("check", station).code, 0)
        result = self.box.run("check", lesson_id)
        self.assertEqual(result.code, 0, result)
        return result

    def solve(self, *task_ids):
        """Make the generated graders of these exam tasks pass."""
        for task_id in task_ids:
            folder = self.box.playground / ("exam-" + self.gate) / task_id
            if folder.is_dir():  # a lesson with two tasks has one of them drawn
                (folder / "done.ok").write_text("ok", encoding="utf-8")

    def status_next(self):
        out = self.box.run("status").out
        return [line.strip() for line in out.splitlines()
                if line.strip().startswith("下一步") or "它不挡下一课" in line]

    def journal_default(self):
        app = self.box.app()
        return next_steps.next_step(app, app.store.load(), reviews=False).say


class WholeGateTest(Case):
    """gate-b through every state, seen by check, status, journal, exam and PROGRESS.md."""

    gate = "gate-b"

    def setUp(self):
        super().setUp()
        self.lesson("1.9", tasks=1)
        self.lesson("1.10", tasks=1)
        self.lesson("1.11")

    def test_a_whole_gate(self):
        # 1. not started: the whole-lesson check of 1.10 names the gate
        done = self.pass_lesson("1.10")
        # gate-b covers the lessons that have its tasks (1.9 and 1.10), passed or not
        self.assertIn("下一步是小关卡 gate-b「本地 Git 关卡」：2 道实操题，预计 8 分钟，"
                      "讲解题另需约 10 分钟。开始考试：python3 tools/course.py exam gate-b", done.out)
        self.assertIn("下次可以对导师说“做小关卡 gate-b”。", done.out)
        self.pass_lesson("1.9")
        status = self.status_next()
        self.assertIn("小关卡 gate-b「本地 Git 关卡」", status[0])
        self.assertTrue(status[0].endswith("下次可以对导师说“做小关卡 gate-b”。"), status)
        self.assertEqual(self.journal_default(), "做小关卡 gate-b")
        listing = self.box.run("exam").out
        self.assertIn("gate-b  小关卡「本地 Git 关卡」（1.9 到 1.10 课）：还没考过；一场 2 题，预计 8 分钟",
                      listing)

        # 2. a sitting with one failed task
        start = self.box.run("exam", "gate-b", "--seed", "3")
        self.assertIn("关卡考试 · 小关卡 gate-b「本地 Git 关卡」 · 第 1 场", start.out)
        self.assertIn("一共 2 题，每课一题，预计 8 分钟（每题的预计分钟数加起来）。", start.out)
        self.assertIn("第 1 场还没批改完（2 题）", self.box.run("exam").out)
        # An open sitting is named with --grade (review finding L2).
        self.assertIn("小关卡 gate-b「本地 Git 关卡」第 1 场考试还没批改完（2 题）：做完以后批改："
                      "python3 tools/course.py exam gate-b --grade", self.status_next()[0])
        self.solve("1.9-x1")
        graded = self.box.run("exam", "gate-b", "--grade")
        self.assertEqual(graded.code, 1, graded)
        self.assertIn("练好以后补考：python3 tools/course.py exam gate-b。补考只考还没通过的 1 课，"
                      "每课一题，没通过的题换另一套题面。", graded.out)
        self.assertIn("实操题通过了 1/2 课；下一场 1 题，预计 4 分钟", self.box.run("exam").out)
        self.assertIn("小关卡 gate-b「本地 Git 关卡」：1 道实操题，预计 4 分钟", self.status_next()[0])
        early = self.box.run("exam", "gate-b", "--explain", "pass")
        self.assertIn("实操题还有 1 课没通过：1.10。补考：python3 tools/course.py exam gate-b", early.out)
        self.box.run("exam", "gate-b", "--explain", "again")  # take the early pass back

        # 3. the retest: only 1.10, in form B
        retest = self.box.run("exam", "gate-b", "--seed", "4")
        self.assertIn("第 2 场 · 补考：只考还没通过的课", retest.out)
        self.assertIn("一共 1 题", retest.out)
        self.assertEqual(self.box.state()["exam_attempts"]["gate-b"]["tasks"][0]["form"], "B")
        self.solve("1.10-x1")
        graded = self.box.run("exam", "gate-b", "--grade")
        self.assertEqual(graded.code, 0, graded)

        # 4. practical part passed, explain-back not recorded as pass
        need = ("实操题都通过了。还差讲解题：对导师说“请问我 gate-b 的讲解题”。导师判断以后，用这条命令记下结果："
                "python3 tools/course.py exam gate-b --explain pass（要再来一次就写 again）")
        self.assertIn(need, graded.out)
        self.assertIn(need, self.box.run("exam", "gate-b").out)
        self.assertIn("实操题都通过了，还差讲解题", self.box.run("exam").out)
        status = self.status_next()
        self.assertIn("小关卡 gate-b「本地 Git 关卡」的实操题都通过了，还差讲解题（约 10 分钟）", status[0])
        self.assertTrue(status[0].endswith("下次可以对导师说“请问我 gate-b 的讲解题”。"), status)
        self.assertEqual(self.journal_default(), "请问我 gate-b 的讲解题")
        again = self.box.run("check", "1.10", "--again")
        self.assertIn("下次可以对导师说“请问我 gate-b 的讲解题”。", again.out)
        # The recorded "again" of step 2 is named with its date.
        self.assertIn("上一次的讲解题在 2026-11-19 记为“再来一次”", status[0])

        # 5. again, then pass
        said = self.box.run("exam", "gate-b", "--explain", "again")
        self.assertIn("讲解题记为“再来一次”：准备好了再对导师说“请问我 gate-b 的讲解题”。", said.out)
        self.assertEqual(self.journal_default(), "请问我 gate-b 的讲解题")
        passed = self.box.run("exam", "gate-b", "--explain", "pass")
        self.assertIn("小关卡 gate-b 通过了：实操题每课都有一题通过，讲解题也记为通过（2026-11-19）。",
                      passed.out)
        self.assertIn("通过了（讲解题 2026-11-19）", self.box.run("exam").out)
        status = self.status_next()
        self.assertTrue(status[0].endswith("下次可以对导师说“从 1.11 开始”。"), status)
        self.assertFalse(any("它不挡下一课" in line for line in status), status)
        self.assertEqual(self.journal_default(), "从 1.11 开始")
        self.box.run("status", "--write")
        progress_md = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("- gate-b 小关卡「本地 Git 关卡」（1.9 到 1.10 课）：通过了（讲解题 2026-11-19）",
                      progress_md)


class GateInLessonCheckTest(Case):
    """ctx.gate_done / ctx.gate_result in a real lesson check through every state."""

    gate = "gate-1"

    CHECK = '''

def check_gate(ctx):
    gate = ctx.gate_result("gate-1")
    if gate.in_progress:
        ctx.fail("这一场考试还没有批改完", where="gate-1", saw="还没批改")
    elif gate.attempts == 0:
        ctx.fail("还没有考 gate-1 的实操题", where="gate-1", saw="没有记录")
    elif not gate.practical_done:
        ctx.fail("还有课的实操题没通过", where="gate-1", saw="还没通过：" + "、".join(gate.open_lesson_titles))
    elif not ctx.gate_done("gate-1"):
        ctx.fail("讲解题还没记为通过", where="gate-1 的讲解题", saw=str(gate.explain))
    else:
        ctx.ok("阶段验收 gate-1 通过了（讲解题 " + gate.explain_date + "）")


checks["1.16b"] = check_gate
'''

    def setUp(self):
        super().setUp()
        self.lesson("1.15", tasks=1)
        self.box.add_syllabus_lesson("1.16", extra=exam_extra("1.16", 1) + self.CHECK)

    def check(self):
        return self.box.run("check", "1.16b")

    def test_every_state_of_the_gate(self):
        self.assertIn("没有记录", self.check().out)
        self.box.run("exam", "gate-1", "--seed", "1")
        self.assertIn("还没批改", self.check().out)
        self.solve("1.15-x1")
        self.box.run("exam", "gate-1", "--grade")
        self.assertIn("还没通过：阶段作品与验收", self.check().out)
        self.box.run("exam", "gate-1", "--seed", "2")
        self.solve("1.16-x1")
        self.box.run("exam", "gate-1", "--grade")
        self.assertIn("看到了什么：None", self.check().out)
        self.box.run("exam", "gate-1", "--explain", "again")
        self.assertIn("看到了什么：again", self.check().out)
        self.box.run("exam", "gate-1", "--explain", "pass")
        result = self.check()
        self.assertEqual(result.code, 0, result)
        self.assertIn("阶段验收 gate-1 通过了（讲解题 2026-11-19）", result.out)


class WordingTest(Case):
    def test_gate_names_follow_common_section_3(self):
        self.assertEqual(syllabus.gate_name("gate-a"), "小关卡 gate-a")
        self.assertEqual(syllabus.gate_name("gate-1"), "阶段验收 gate-1")
        self.assertEqual(syllabus.gate_label("gate-b"), "小关卡 gate-b「本地 Git 关卡」")
        self.assertEqual(syllabus.gate_label("gate-0"), "gate-0「起步小关卡」")
        self.assertEqual(syllabus.gate_label("gate-1"), "gate-1「阶段 1 验收」")
        self.assertEqual(syllabus.gate_label("gate-x"), "gate-x")
        # gate-1 covers 1.11-1.16 only (no borrowing)
        self.assertEqual(syllabus.GATES["gate-1"]["lessons"],
                         ["1.11", "1.12", "1.13", "1.14", "1.15", "1.16"])

    def test_a_gate_whose_title_says_its_kind_reads_with_a_space_after_chinese(self):
        self.lesson("0.4", tasks=1)
        self.lesson("1.1")
        done = self.pass_lesson("0.4")
        self.assertIn("下一步是 gate-0「起步小关卡」：1 道实操题", done.out)

    def test_status_puts_a_space_between_then_and_a_lesson_id(self):
        self.lesson("1.6")
        self.lesson("1.7")
        for station in ("1.6a", "1.6b", "1.6c"):
            self.box.flag(station)
            self.box.run("check", station)
        out = self.box.run("status", now="2026-11-25T10:00:00").out
        self.assertIn("python3 tools/course.py review；然后 1.6 课的 3 站都通过了。", out)

    def test_wrapup_steps(self):
        lesson = type("L", (), {})()
        lesson.id, lesson.rules = "1.6", ["GIT-01"]
        lesson.rules_path = self.box.root / "nothing.md"
        lines = check_command.wrapup_lines(lesson)
        self.assertEqual(lines[0], "收尾还有两件小事：")
        self.assertIn("在小标题「GIT-01」下面用自己的话写一两句", lines[1])
        self.assertNotIn("各用", lines[1])
        lesson.id, lesson.rules = "1.13", ["PUB-01", "PUB-02"]
        lines = check_command.wrapup_lines(lesson)
        self.assertEqual(lines[0], "收尾还有三件小事：")
        self.assertIn("各用自己的话", lines[1])
        self.assertEqual(lines[3], "  3. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做")
        # A lesson without a new rule drops the notes step (COMMON section 3).
        lesson.rules = []
        lines = check_command.wrapup_lines(lesson)
        self.assertEqual(lines[0], "收尾还有两件小事：")
        self.assertEqual(lines[1], "  1. 一句话日志：python3 tools/course.py journal")
        self.assertNotIn("notes/", "".join(lines))
        lesson.id = "1.3"
        self.assertEqual(check_command.wrapup_lines(lesson),
                         ["收尾还有一件小事：", "  1. 一句话日志：python3 tools/course.py journal"])

    def test_wrapup_names_the_rule_titles_from_rules_md(self):
        self.lesson("1.12")
        self.lesson("1.13")
        for station in syllabus.lesson_entry("1.12")["stations"]:
            self.box.flag(station)
            self.box.run("check", station)
        out = self.box.run("check", "1.12").out
        self.assertIn("在小标题「REMOTE-01 示例规则 REMOTE-01」「REMOTE-02 示例规则 REMOTE-02」下面各用", out)
        self.assertIn("3. 备份：", out)


class ExplainDuringPracticeTest(Case):
    """An extra practice sitting (--all) after the practical part never hides the explain-back."""

    gate = "gate-b"

    def test_practice_sitting_open(self):
        self.lesson("1.10", tasks=2)
        self.lesson("1.11")
        self.pass_lesson("1.10")
        self.box.run("exam", "gate-b", "--seed", "1")
        self.solve("1.10-x1", "1.10-x2")
        self.box.run("exam", "gate-b", "--grade")
        self.box.run("exam", "gate-b", "--all", "--seed", "2")
        app = self.box.app()
        step = next_steps.next_step(app, app.store.load(), reviews=False)
        self.assertEqual((step.kind, step.say), (next_steps.EXPLAIN, "请问我 gate-b 的讲解题"))


class ShowRealPlaceTest(unittest.TestCase):
    def test_ctx_show_can_name_the_real_place(self):
        layout = Layout(self)
        layout.entrance.symlink_to(layout.real)
        ctx = CheckContext(layout.app())
        self.assertEqual(ctx.show(ctx.workspace), "~/Developer/fullstack-from-zero")
        self.assertEqual(ctx.show(ctx.workspace, entrance=False), "~/Desktop/Code/fullstack-from-zero")
        self.assertEqual(ctx.show("notes", entrance=False), "~/Desktop/Code/fullstack-from-zero/notes")


class CompleteValidationTest(Case):
    def test_every_lesson_of_a_gate_needs_a_task(self):
        for lesson_id in ("1.6", "1.7", "1.8", "1.9"):
            self.lesson(lesson_id, tasks=1)
        self.lesson("1.10")
        result = self.box.run("validate", "--complete", "--json")
        findings = json.loads(result.out)
        texts = [f.get("message", "") for f in _all_findings(findings)]
        self.assertTrue(any("1.10 课还没有关卡 gate-b 的考题" in t for t in texts), texts[:20])
        self.assertFalse(any("1.9 课还没有关卡 gate-b 的考题" in t for t in texts))


def _all_findings(data):
    """Every finding dict in the JSON of ``validate --json`` (whatever its nesting)."""
    found = []
    if isinstance(data, dict):
        if "message" in data and ("code" in data or "level" in data):
            found.append(data)
        for value in data.values():
            found += _all_findings(value)
    elif isinstance(data, list):
        for value in data:
            found += _all_findings(value)
    return found


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
