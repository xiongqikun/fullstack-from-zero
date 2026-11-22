"""The ``exam`` command (plan I4, I7; COMMON.md section 1): cold practical tasks per gate.

Generated lessons carry small EXAM tasks: the builder makes a folder with a
seeded name and a seeded word; the task is to write that word into
``answer.txt``.  The learner's side is simulated by reading the facts from
the marker, exactly as a person would read the task text.

The rule under test: one sitting holds one task for each lesson of the gate;
a lesson is covered once one of its tasks is passed; a sitting after an
unsuccessful one holds only the lessons not covered yet (the task that was
not passed, in its other form); the gate is passed when every lesson is
covered and the explain-back verdict is recorded as pass.
"""

import json
import os
import random
import shutil
import unittest

import helpers

from courselib import progress, runner, scenario, syllabus
from courselib.commands import exam

EXAM_CODE = '''
def build_x(sc):
    folder = "box-" + sc.word()
    sc.write(folder + "/todo.txt", "待办")
    sc.fact("folder", folder)
    if sc.form == "A":
        sc.fact("word", sc.pick(["alpha", "bravo", "charlie", "delta"]) + "-" + str(sc.randint(1, 999)))
    else:
        sc.fact("word", "b-" + sc.word() + "-" + str(sc.randint(1, 999)))


def grade_x(ctx):
    info = ctx.scenario()
    target = info.path / info.facts["folder"] / "answer.txt"
    ctx.expect(ctx.read(target).strip() == info.facts["word"], "answer.txt 写对了",
               "answer.txt 还没有写对", where=ctx.show(target), saw="内容和题目要求的不一样")


def grade_raises(ctx):
    raise RuntimeError("grader is broken")


def _task(number, grade=grade_x, gate="{gate}"):
    return {{
        "id": "{id}-x" + str(number),
        "gate": gate,
        "title": "{id} 的第 " + str(number) + " 道考题",
        "minutes": 2 + number,
        "build": build_x,
        "task": {{
            "A": "进入 {{dir}}/{{folder}}，新建 answer.txt，里面只写一行：{{word}}",
            "B": "在文件夹 {{dir}}/{{folder}} 里建一个 answer.txt，内容是 {{word}}，不要写别的。",
        }},
        "grade": grade,
    }}


EXAM = [{tasks}]
'''

GATE_B = ("1.6", "1.7", "1.8", "1.9", "1.10")


def exam_code(lesson_id, count, raising=(), gate=None):
    gate = gate or syllabus.lesson_entry(lesson_id)["gate"]
    tasks = ", ".join(
        "_task({n}{extra})".format(n=n, extra=", grade=grade_raises" if n in raising else "")
        for n in range(1, count + 1))
    return EXAM_CODE.format(id=lesson_id, gate=gate, tasks=tasks)


class ExamTestBase(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.playground = self.box.base / "pg"
        self.box.env["COURSE_PLAYGROUND"] = str(self.playground)

    def lessons(self, counts, raising=None):
        for lesson_id, count in counts.items():
            self.box.add_syllabus_lesson(
                lesson_id, extra=exam_code(lesson_id, count, (raising or {}).get(lesson_id, ())))

    def exam(self, *argv, **extra):
        return self.box.run("exam", *argv, **extra)

    def attempt(self, gate="gate-b"):
        return self.box.state()["exam_attempts"][gate]

    def folder(self, entry):
        return self.playground / entry["folder"]

    def marker(self, entry):
        return scenario.read_marker(self.folder(entry))

    def solve(self, entry, wrong=False):
        facts = self.marker(entry)["facts"]
        target = self.folder(entry) / facts["folder"] / "answer.txt"
        target.write_text(("wrong" if wrong else facts["word"]) + "\n", encoding="utf-8")


class NoTasksTest(ExamTestBase):
    def test_zero_tasks_is_polite(self):
        self.lessons({"1.6": 0, "1.7": 0})
        result = self.exam("gate-b")
        self.assertEqual(result.code, 0, result)
        self.assertIn("小关卡 gate-b「本地 Git 关卡」的考题还没有写好", result.out)
        self.assertIn("1.6 到 1.10 课", result.out)
        self.assertIn("这不是你的问题", result.out)
        self.assertFalse(self.playground.exists())
        self.assertNotIn("gate-b", self.box.state().get("exam_attempts", {}))
        graded = self.exam("gate-b", "--grade")
        self.assertEqual(graded.code, 1, graded)
        self.assertIn("还没有开始考试", graded.out)

    def test_a_gate_without_any_lesson_yet(self):
        result = self.exam("gate-0")
        self.assertEqual(result.code, 0, result)
        self.assertIn("考题还没有写好", result.out)
        self.assertIn("0.1 到 0.4 课", result.out)

    def test_unknown_gate_and_listing(self):
        self.lessons({"1.6": 2})
        unknown = self.exam("gate-z")
        self.assertEqual(unknown.code, 64)
        self.assertIn("gate-0、gate-a、gate-b、gate-1", unknown.err)
        listing = self.exam()
        self.assertEqual(listing.code, 0, listing)
        # one lesson with tasks: one task per sitting; the estimate is the mean of 3 and 4
        self.assertIn("小关卡「本地 Git 关卡」（1.6 课）：还没考过；一场 1 题，预计 4 分钟", listing.out)
        self.assertIn("起步小关卡（0.1 到 0.4 课）：考题还没写好", listing.out)
        self.assertIn("阶段 1 验收（1.11 到 1.16 课）：考题还没写好", listing.out)
        self.assertEqual(self.exam("GATE-B").code, 0)     # typed ids are normalised

    def test_grade_explain_and_new_cannot_be_combined(self):
        self.lessons({"1.6": 1})
        self.assertEqual(self.exam("gate-b", "--grade", "--new").code, 64)
        self.assertEqual(self.exam("gate-b", "--grade", "--explain", "pass").code, 64)
        self.assertEqual(self.exam("gate-b", "--explain", "pass", "--all").code, 64)
        wrong = self.exam("gate-b", "--explain", "fail")
        self.assertEqual(wrong.code, 64, wrong)
        self.assertIn("pass、again", wrong.err)

    def test_help_explains_the_options(self):
        result = self.exam("--help")
        self.assertEqual(result.code, 0, result)
        self.assertIn("--explain", result.out)
        self.assertIn("记下讲解题的结果", result.out)
        self.assertIn("每课一题", result.out)
        self.assertIn("用它加练", result.out)


class OneTaskTest(ExamTestBase):
    def test_one_task_fail_then_retest_on_the_other_form(self):
        self.lessons({"1.6": 1})
        first = self.exam("gate-b")
        self.assertEqual(first.code, 0, first)
        self.assertIn("1.7、1.8、1.9、1.10 课还没有考题，这一场先考已经写好的 1 题", first.out)
        self.assertIn("关卡考试 · 小关卡 gate-b「本地 Git 关卡」 · 第 1 场", first.out)
        self.assertIn("一共 1 题，每课一题，预计 3 分钟", first.out)
        self.assertIn("讲解题，约 10 分钟", first.out)
        self.assertIn("第 1 题 · 1.6 的第 1 道考题", first.out)
        self.assertNotIn("hint", first.out)
        self.assertNotIn("提示：", first.out)
        attempt = self.attempt()
        entry = attempt["tasks"][0]
        self.assertEqual((attempt["attempt"], attempt["kind"]), (1, "full"))
        self.assertEqual((entry["id"], entry["form"], entry["result"]), ("1.6-x1", "A", None))
        marker = self.marker(entry)
        self.assertEqual((marker["seed"], marker["form"], marker["key"]), (entry["seed"], "A", "1.6-x1"))
        facts = marker["facts"]
        # the task text is filled with the real folder and the seeded word
        self.assertIn("进入 {}/{}，新建 answer.txt，里面只写一行：{}".format(
            self.folder(entry), facts["folder"], facts["word"]), first.out)
        # form A already says which folder to enter: no second, different cd line
        self.assertNotIn("cd " + str(self.folder(entry)), first.out)
        self.assertIn("这道题的文件夹：" + str(self.folder(entry)), first.out)
        self.assertIn("python3 tools/course.py exam gate-b --grade", first.out)

        self.solve(entry, wrong=True)
        graded = self.exam("gate-b", "--grade")
        self.assertEqual(graded.code, 1, graded)
        self.assertIn("还没达标", graded.out)
        self.assertIn("通过 0/1 题", graded.out)
        self.assertIn("1.6 课「Git：第一次提交」：1.6 的第 1 道考题", graded.out)
        self.assertIn("补考只考还没通过的 1 课，每课一题，没通过的题换另一套题面", graded.out)
        record = self.box.state()["exams"]["gate-b"]["1.6-x1"]
        self.assertEqual((record["form"], record["result"], record["date"]), ("A", "fail", "2026-11-19"))
        self.assertEqual(record["seed"], entry["seed"])
        # a graded attempt is closed: grading again changes nothing
        self.solve(entry)
        again = self.exam("gate-b", "--grade")
        self.assertEqual(again.code, 0, again)
        self.assertIn("已经批改过了", again.out)
        self.assertIn("还没通过的课可以补考", again.out)
        self.assertEqual(self.box.state()["exams"]["gate-b"]["1.6-x1"]["result"], "fail")

        retest = self.exam("gate-b", now="2026-11-21T10:00:00")
        self.assertEqual(retest.code, 0, retest)
        self.assertIn("补考：只考还没通过的课", retest.out)
        attempt = self.attempt()
        entry2 = attempt["tasks"][0]
        self.assertEqual((attempt["attempt"], attempt["kind"], entry2["form"]), (2, "retest", "B"))
        self.assertNotEqual(entry2["seed"], entry["seed"])
        marker2 = self.marker(entry2)
        self.assertEqual((marker2["form"], marker2["seed"]), ("B", entry2["seed"]))
        self.assertIn("不要写别的", retest.out)                      # form B text
        # form B names no folder to enter: the tool gives the cd of the task folder
        self.assertIn("先进入这道题的文件夹：cd " + str(self.folder(entry2)), retest.out)
        self.assertFalse((self.folder(entry2) / facts["folder"] / "answer.txt").exists())
        self.solve(entry2)
        passed = self.exam("gate-b", "--grade", now="2026-11-21T10:30:00")
        self.assertEqual(passed.code, 0, passed)
        self.assertIn("实操题都通过了。还差讲解题：对导师说“请问我 gate-b 的讲解题”。", passed.out)
        self.assertIn("python3 tools/course.py exam gate-b --explain pass（要再来一次就写 again）",
                      passed.out)
        record = self.box.state()["exams"]["gate-b"]["1.6-x1"]
        self.assertEqual((record["form"], record["result"], record["date"], record["attempt"]),
                         ("B", "pass", "2026-11-21", 2))
        self.assertEqual([h["result"] for h in record["history"]], ["fail", "pass"])
        last = self.box.last_result()
        self.assertEqual((last["kind"], last["target"]), ("exam", "gate-b"))
        self.assertEqual((last["practical_done"], last["gate_done"], last["explain"]),
                         (True, False, None))

        # the practical part is passed: exam says so and names the one way to practise more
        done = self.exam("gate-b", now="2026-11-22T10:00:00")
        self.assertEqual(done.code, 0, done)
        self.assertIn("实操题都通过了。还差讲解题", done.out)
        self.assertIn("没抽到的题算加练，不做也不影响通过", done.out)
        self.assertIn("python3 tools/course.py exam gate-b --all", done.out)
        self.assertEqual(self.attempt()["attempt"], 2)             # no new sitting
        listing = self.exam(now="2026-11-22T10:00:00")
        self.assertIn("实操题都通过了，还差讲解题", listing.out)

        practice = self.exam("gate-b", "--all", now="2026-11-22T10:00:00")
        self.assertEqual(practice.code, 0, practice)
        self.assertEqual(self.attempt()["tasks"][0]["form"], "A")      # alternates back
        self.assertEqual(self.attempt()["kind"], "practice")
        self.assertIn("加练：实操题你已经通过了", practice.out)
        self.solve(self.attempt()["tasks"][0], wrong=True)
        graded = self.exam("gate-b", "--grade", now="2026-11-22T10:20:00")
        self.assertEqual(graded.code, 1, graded)
        self.assertIn("这是加练：通过的课不会退回去。", graded.out)
        self.assertIn("实操题都通过了。还差讲解题", graded.out)
        self.assertTrue(progress.gate_status(self.box.app().catalog(), self.box.state(),
                                             "gate-b").practical_done)

    def test_reopening_an_open_attempt_keeps_the_work(self):
        self.lessons({"1.6": 1})
        self.exam("gate-b")
        entry = self.attempt()["tasks"][0]
        self.solve(entry)
        reopened = self.exam("gate-b")
        self.assertEqual(reopened.code, 0, reopened)
        self.assertIn("还有题没批改", reopened.out)
        self.assertEqual(self.attempt()["tasks"][0]["seed"], entry["seed"])
        self.assertTrue((self.folder(entry) / self.marker(entry)["facts"]["folder"] / "answer.txt").is_file())
        self.assertEqual(len(self.box.events("exam-started")), 1)
        listing = self.exam()
        self.assertIn("第 1 场还没批改完（1 题）", listing.out)
        new = self.exam("gate-b", "--new")
        self.assertEqual(new.code, 0, new)
        entry2 = self.attempt()["tasks"][0]
        self.assertEqual((self.attempt()["attempt"], entry2["form"]), (2, "B"))
        self.assertNotEqual(entry2["seed"], entry["seed"])

    def test_a_missing_task_folder_is_not_yet(self):
        self.lessons({"1.6": 1})
        self.exam("gate-b")
        entry = self.attempt()["tasks"][0]
        shutil.rmtree(str(self.folder(entry)))
        graded = self.exam("gate-b", "--grade")
        self.assertEqual(graded.code, 1, graded)
        self.assertIn("考题要在工具搭好的文件夹里完成", graded.out)

    def test_refuses_to_replace_a_folder_the_tool_did_not_build(self):
        self.lessons({"1.6": 1})
        mine = self.playground / "exam-gate-b" / "1.6-x1"
        mine.mkdir(parents=True)
        (mine / "keep.txt").write_text("别动", encoding="utf-8")
        result = self.exam("gate-b")
        self.assertEqual(result.code, 1, result)
        self.assertIn(".playground", result.out)
        self.assertEqual(os.listdir(str(mine)), ["keep.txt"])
        self.assertNotIn("gate-b", self.box.state().get("exam_attempts", {}))


class SittingRuleTest(ExamTestBase):
    """G1: one task per lesson, retests only the lessons not covered yet."""

    def test_a_sitting_holds_one_task_per_lesson_and_a_retest_only_what_is_open(self):
        self.lessons({lesson_id: 2 for lesson_id in GATE_B})
        result = self.exam("gate-b")
        self.assertEqual(result.code, 0, result)
        attempt = self.attempt()
        tasks = attempt["tasks"]
        # five lessons: five tasks, not six; one of each lesson, in lesson order
        self.assertEqual([t["lesson"] for t in tasks], list(GATE_B))
        self.assertEqual({t["form"] for t in tasks}, {"A"})
        self.assertEqual(len({t["seed"] for t in tasks}), 5)
        minutes = sum(t["minutes"] for t in tasks)
        self.assertEqual(minutes, sum(2 + int(t["id"][-1]) for t in tasks))
        self.assertIn(f"一共 5 题，每课一题，预计 {minutes} 分钟", result.out)
        self.assertNotIn("还没有考题", result.out)
        for number in range(1, 6):
            self.assertIn(f"第 {number} 题", result.out)
        for entry in tasks[:3]:
            self.solve(entry)
        self.solve(tasks[3], wrong=True)                 # 1.9 wrong, 1.10 left empty
        graded = self.exam("gate-b", "--grade")
        self.assertEqual(graded.code, 1, graded)
        self.assertIn("通过 3/5 题", graded.out)
        self.assertIn("补考只考还没通过的 2 课", graded.out)
        listing = self.exam()
        self.assertIn("实操题通过了 3/5 课；下一场 2 题", listing.out)

        retest = self.exam("gate-b")
        self.assertEqual(retest.code, 0, retest)
        attempt2 = self.attempt()
        again = {t["lesson"]: t for t in attempt2["tasks"]}
        self.assertEqual(sorted(again), ["1.10", "1.9"])
        # the same tasks come back, in their other form
        self.assertEqual(again["1.9"]["id"], tasks[3]["id"])
        self.assertEqual(again["1.10"]["id"], tasks[4]["id"])
        self.assertEqual({t["form"] for t in attempt2["tasks"]}, {"B"})
        self.assertEqual(attempt2["kind"], "retest")
        retest_minutes = again["1.9"]["minutes"] + again["1.10"]["minutes"]
        self.assertIn(f"一共 2 题，每课一题，预计 {retest_minutes} 分钟", retest.out)
        for entry in attempt2["tasks"]:
            self.solve(entry)
        passed = self.exam("gate-b", "--grade")
        self.assertEqual(passed.code, 0, passed)
        self.assertIn("这一场的题全部通过了。", passed.out)
        self.assertIn("实操题都通过了。还差讲解题", passed.out)
        state = self.box.state()
        # five tasks were never drawn: they are extra practice, not a condition
        self.assertEqual(len(state["exams"]["gate-b"]), 5)

    def test_practice_prefers_tasks_never_drawn(self):
        self.lessons({"1.6": 2, "1.7": 2})
        self.exam("gate-b", "--seed", "5")
        first = {t["lesson"]: t["id"] for t in self.attempt()["tasks"]}
        for entry in self.attempt()["tasks"]:
            self.solve(entry)
        self.exam("gate-b", "--grade")
        self.exam("gate-b", "--all", "--seed", "6")
        second = {t["lesson"]: t["id"] for t in self.attempt()["tasks"]}
        self.assertEqual(sorted(second), ["1.6", "1.7"])
        self.assertTrue(all(second[k] != first[k] for k in second), (first, second))
        self.assertEqual(self.attempt()["kind"], "practice")

    def test_gate_1_borrows_nothing_from_gate_a_or_gate_b(self):
        self.lessons({"1.6": 3, "1.11": 2})
        result = self.exam("gate-1")
        self.assertEqual(result.code, 0, result)
        self.assertEqual([t["lesson"] for t in self.attempt("gate-1")["tasks"]], ["1.11"])
        self.assertIn("关卡考试 · gate-1「阶段 1 验收」", result.out)
        primary, secondary, unusable = self.box.app().catalog().gate_pool("gate-1")
        self.assertEqual([t["id"] for _l, t in primary], ["1.11-x1", "1.11-x2"])
        self.assertEqual((secondary, unusable), ([], []))

    def test_a_lesson_that_was_not_built_comes_in_the_next_sitting(self):
        self.lessons({"1.6": 1})
        broken = exam_code("1.7", 1).replace(
            'sc.write(folder + "/todo.txt", "待办")', 'raise ValueError("builder is broken")')
        self.box.add_syllabus_lesson("1.7", extra=broken)
        self.exam("gate-b")
        self.solve(self.attempt()["tasks"][0])
        graded = self.exam("gate-b", "--grade")
        self.assertEqual(graded.code, 0, graded)
        self.assertIn("还有 1 课这一场没考到：1.7。接着考：python3 tools/course.py exam gate-b",
                      graded.out)
        self.assertNotIn("还差讲解题", graded.out)

    def test_draw_and_full_plan(self):
        rng = random.Random(1)
        self.assertEqual(exam.draw([("1.6", ["a"]), ("1.7", []), ("1.8", ["b", "c"])], rng)[0], "a")
        self.assertEqual(len(exam.draw([("1.6", ["a"]), ("1.7", []), ("1.8", ["b", "c"])], rng)), 2)
        pool = [("1.6", "1.6-x1"), ("1.6", "1.6-x2"), ("1.7", "1.7-x1")]
        self.assertEqual(progress.gate_full_plan(pool, {"1.6-x1": {"result": "pass"}}),
                         [("1.6", ["1.6-x2"]), ("1.7", ["1.7-x1"])])
        self.assertEqual(progress.gate_full_plan(pool, {}, drawn=["1.6-x1", "1.6-x2"]),
                         [("1.6", ["1.6-x1", "1.6-x2"]), ("1.7", ["1.7-x1"])])
        many = [(f"1.{n}", f"1.{n}-x1") for n in range(1, 9)]
        self.assertEqual(len(progress.gate_full_plan(many)), progress.GATE_MAX_TASKS)

    def test_names_of_gates(self):
        self.assertEqual(exam.gate_name("gate-0"), "小关卡 gate-0")
        self.assertEqual(exam.gate_name("gate-a"), "小关卡 gate-a")
        self.assertEqual(exam.gate_name("gate-b"), "小关卡 gate-b")
        self.assertEqual(exam.gate_name("gate-1"), "阶段验收 gate-1")
        self.assertEqual(exam.gate_name("gate-example"), "gate-example")
        self.assertEqual(exam.RESULT_OF[runner.PASSED], "pass")
        self.assertEqual(exam.RESULT_OF[runner.NOT_YET], "fail")


class ExplainTest(ExamTestBase):
    """G2: exam <gate> --explain pass|again."""

    def test_refused_before_a_graded_sitting(self):
        self.lessons({"1.6": 1})
        result = self.exam("gate-b", "--explain", "pass")
        self.assertEqual(result.code, 1, result)
        self.assertIn("gate-b 还没有批改过一场考试，现在还不能记讲解题的结果", result.out)
        self.assertNotIn("explain", self.box.state())
        self.exam("gate-b")                                   # a sitting, not graded yet
        still = self.exam("gate-b", "--explain", "again")
        self.assertEqual(still.code, 1, still)
        self.assertNotIn("explain", self.box.state())

    def test_pass_after_the_practical_part_passes_the_gate(self):
        self.lessons({"1.6": 1})
        self.exam("gate-b")
        self.solve(self.attempt()["tasks"][0])
        self.exam("gate-b", "--grade")
        again = self.exam("gate-b", "--explain", "again", now="2026-11-24T10:00:00")
        self.assertEqual(again.code, 0, again)
        self.assertIn("讲解题记为“再来一次”：准备好了再对导师说“请问我 gate-b 的讲解题”。", again.out)
        self.assertEqual(self.box.state()["explain"]["gate-b"],
                         {"result": "again", "date": "2026-11-24"})
        self.assertIn("还差讲解题", self.exam("gate-b").out)
        passed = self.exam("gate-b", "--explain", "pass", now="2026-11-25T10:00:00")
        self.assertEqual(passed.code, 0, passed)
        self.assertIn("讲解题的结果记下了：通过（2026-11-25）。", passed.out)
        self.assertIn("小关卡 gate-b 通过了：实操题每课都有一题通过，讲解题也记为通过（2026-11-25）。",
                      passed.out)
        self.assertEqual(self.box.state()["explain"]["gate-b"],
                         {"result": "pass", "date": "2026-11-25"})
        self.assertEqual([e["result"] for e in self.box.events("exam-explain")], ["again", "pass"])
        done = self.exam("gate-b", now="2026-11-26T10:00:00")
        self.assertIn("小关卡 gate-b 通过了", done.out)
        self.assertIn("exam gate-b --all", done.out)
        self.assertNotIn("还差讲解题", done.out)
        listing = self.exam(now="2026-11-26T10:00:00")
        self.assertIn("通过了（讲解题 2026-11-25）", listing.out)

    def test_accepted_while_the_practical_part_is_still_open(self):
        self.lessons({"1.6": 1, "1.7": 1})
        self.exam("gate-b")
        tasks = self.attempt()["tasks"]
        self.solve(tasks[0])
        self.solve(tasks[1], wrong=True)
        self.exam("gate-b", "--grade")
        result = self.exam("gate-b", "--explain", "pass")
        self.assertEqual(result.code, 0, result)
        self.assertIn("讲解题的结果记下了：通过（2026-11-19）。", result.out)
        self.assertIn("实操题还有 1 课没通过：1.7。补考：python3 tools/course.py exam gate-b", result.out)
        summary = progress.gate_status(self.box.app().catalog(), self.box.state(), "gate-b")
        self.assertEqual((summary.practical_done, summary.explain, summary.done),
                         (False, "pass", False))


class ManyTasksTest(ExamTestBase):
    def test_a_grading_function_that_raises_is_a_checker_problem(self):
        self.lessons({"1.6": 1, "1.7": 1}, raising={"1.7": (1,)})
        self.exam("gate-b")
        for entry in self.attempt()["tasks"]:
            self.solve(entry)
        graded = self.exam("gate-b", "--grade")
        self.assertEqual(graded.code, 2, graded)
        self.assertIn("检查器出问题", graded.out)
        self.assertIn("这不是你的错", graded.out)
        self.assertNotIn("Traceback", graded.text)
        self.assertIn("通过 1/2 题，1 题检查器出问题", graded.out)
        state = self.box.state()
        self.assertEqual(state["exams"]["gate-b"]["1.6-x1"]["result"], "pass")
        self.assertNotIn("1.7-x1", state["exams"]["gate-b"])     # a broken grader is not a result
        tasks = {t["id"]: t["result"] for t in state["exam_attempts"]["gate-b"]["tasks"]}
        self.assertEqual(tasks, {"1.6-x1": "pass", "1.7-x1": "problem"})
        self.assertIn("RuntimeError", json.dumps(self.box.last_result()["details"]["1.7-x1"]))
        # the tutor fixes the lesson; grading again regrades only the broken task
        lesson = self.box.root / "stages" / "01-foundations" / "07-read-diff" / "lesson.py"
        source = lesson.read_text(encoding="utf-8")
        lesson.write_text(source.replace("grade=grade_raises", "grade=grade_x"), encoding="utf-8")
        regrade = self.exam("gate-b", "--grade")
        self.assertEqual(regrade.code, 0, regrade)
        self.assertIn("只重批上次检查器出问题的 1 题", regrade.out)
        self.assertEqual(self.box.state()["exams"]["gate-b"]["1.7-x1"]["result"], "pass")
        self.assertEqual(len(self.box.events("exam-task")), 3)

    def test_a_builder_that_fails_drops_only_its_task(self):
        self.lessons({"1.6": 1})
        broken = exam_code("1.7", 1).replace(
            'sc.write(folder + "/todo.txt", "待办")', 'raise ValueError("builder is broken")')
        self.box.add_syllabus_lesson("1.7", extra=broken)
        result = self.exam("gate-b")
        self.assertEqual(result.code, 2, result)
        self.assertIn("搭建失败", result.out)
        self.assertNotIn("Traceback", result.text)
        self.assertEqual([t["id"] for t in self.attempt()["tasks"]], ["1.6-x1"])


PLACES_CODE = '''
def build_place(sc):
    sc.git_init("repo-" + sc.word())
    sc.fact("repo", sorted(p.name for p in sc.root.iterdir() if p.name.startswith("repo-"))[0])
    sc.todo("考题仓库在里面一层")


def build_cd_todo(sc):
    sc.mkdir("inner")
    sc.fact("repo", "inner")
    sc.todo("先进去：cd " + sc.show("inner"))


def grade_final(ctx):
    # an exam answer is final: the grader sees ctx.final set before it runs
    ctx.expect(getattr(ctx, "final", None) is True, "final 已经打开", "final 没有打开",
               where="ctx.final", saw=repr(getattr(ctx, "final", None)))


def grade_broken(ctx):
    raise RuntimeError("broken grader")


def _t(build, a, b, grade=grade_final):
    return {{"id": "{lesson}-x1", "gate": "gate-b", "title": "第 {number} 道",
            "minutes": 2, "build": build, "task": {{"A": a, "B": b}}, "grade": grade}}


ALL = [
    _t(build_place, "先 cd 进 {{dir}}/{{repo}}，在那里 git init。", "进入 {{dir}}/{{repo}} 以后做。"),
    _t(build_place, "仓库 {{dir}}/{{repo}} 里做一个提交。", "仓库 {{dir}}/{{repo}} 里再做一个提交。"),
    _t(build_cd_todo, "照上面那一行进去，新建一个文件。", "进去以后新建一个文件。"),
    _t(build_place, "随便做点什么。", "随便做点别的。", grade=grade_broken),
]
EXAM = [ALL[{number} - 1]]
'''


class TaskPlacesTest(ExamTestBase):
    """P4: the exam never adds a cd line that contradicts the task, and grading is final."""

    def setUp(self):
        ExamTestBase.setUp(self)
        for number, lesson_id in enumerate(("1.6", "1.7", "1.8", "1.9"), 1):
            self.box.add_syllabus_lesson(
                lesson_id, extra=PLACES_CODE.format(lesson=lesson_id, number=number))

    def blocks(self, out):
        """{task number: [lines]} of the printed task list."""
        found, current = {}, None
        for line in out.splitlines():
            if line.startswith("第 ") and " 题 · " in line:
                current = int(line.split()[1])
                found[current] = []
            elif current and line.startswith("  "):
                found[current].append(line.strip())
            elif not line.strip():
                current = None
        return found

    def test_the_tool_adds_its_cd_line_only_when_the_task_gives_none(self):
        result = self.exam("gate-b", "--seed", "4")
        self.assertIn(result.code, (0, 2), result)
        blocks = self.blocks(result.out)
        cd = [n for n, lines in blocks.items() if any("cd " in l for l in lines)]
        tool_cd = {n: [l for l in lines if l.startswith("先进入这道题的文件夹：cd ")]
                   for n, lines in blocks.items()}
        # task 1 (form A says "先 cd 进 ..."): no second, different cd line
        self.assertEqual(tool_cd[1], [])
        self.assertIn(1, cd)
        # task 2 says nothing about where to stand: the tool's line, worded for beginners
        self.assertEqual(len(tool_cd[2]), 1)
        self.assertIn("题目里说的文件夹如果在它里面，再 cd 进那一层", tool_cd[2][0])
        # task 3: the todo line gives the cd and is shown under the task text
        self.assertTrue(any(l.startswith("先进去：cd ") for l in blocks[3]))
        self.assertEqual(tool_cd[3], [])
        self.assertTrue(all(any(l.startswith("这道题的文件夹：") for l in lines)
                            for lines in blocks.values()))
        self.assertNotIn("进入：cd", result.out)

    def test_a_task_that_says_jin_ru_and_its_folder_gets_no_tool_cd_line(self):
        self.assertTrue(exam.gives_cd("进入 ~/x/1.9-x1/shop：做完", [], "~/x/1.9-x1"))
        self.assertFalse(exam.gives_cd("仓库 ~/x/1.9-x1/shop 里", [], "~/x/1.9-x1"))
        self.assertTrue(exam.gives_cd("先 cd 进去", ["x"]))
        self.assertTrue(exam.gives_cd("x", ["进去：cd ~/a"]))
        self.assertFalse(exam.gives_cd("", []))

    def test_grading_sets_final_and_names_the_full_regrade_command(self):
        self.exam("gate-b", "--seed", "4")
        graded = self.exam("gate-b", "--grade")
        self.assertEqual(graded.code, 2, graded)          # task 4's grader is broken
        self.assertEqual(graded.out.count("✅ 通过"), 3, graded.out)
        self.assertIn("修好以后再运行 python3 tools/course.py exam gate-b --grade，只会重批这几题",
                      graded.out)
        self.assertFalse(hasattr(exam, "final_grader"))  # final=True goes through run_check


class ProcessTest(ExamTestBase):
    def test_exam_as_a_child_process_on_python_39(self):
        python = helpers.find_python39()
        if python is None:
            self.skipTest("no Python 3.9 on this machine")
        self.lessons({"1.6": 1})
        started = self.box.run_process("exam", "gate-b", python=python)
        self.assertEqual(started.code, 0, started)
        self.assertIn("第 1 题", started.out)
        self.solve(self.attempt()["tasks"][0])
        graded = self.box.run_process("exam", "gate-b", "--grade", python=python)
        self.assertEqual(graded.code, 0, graded)
        self.assertIn("通过 1/1 题", graded.out)
        explained = self.box.run_process("exam", "gate-b", "--explain", "pass", python=python)
        self.assertEqual(explained.code, 0, explained)
        self.assertIn("讲解题的结果记下了", explained.out)


if __name__ == "__main__":
    unittest.main()
