"""Runtime changes after the lesson blind tests (items R1-R11 of 2026-11-19).

R1 validate: the minutes of plan G5a, heading minutes, reserved review words.
R2 ctx.choose.  R3 ctx.gate_done / ctx.gate_result.  R4 global Git settings.
R5 parse_int.  R6 one_line and visible.  R7 app.show through links.
R8 home folders scrubbed.  R9 full-width characters on the command line.
R10 resume sentences.  R11 ctx.final.
"""

import datetime
import io
import json
import os
import unittest
from unittest import mock

import helpers

from courselib import progress, runner, ui
from courselib.app import App
from courselib.context import CheckContext
from courselib.errors import Cancelled, ToolTrouble, UsageProblem
from courselib.normalize import parse_int
from courselib.ui import Console

U3000 = "　"
NBSP = " "


def _console(inputs=None, can_prompt=True):
    out = io.StringIO()
    feed = list(inputs or [])

    def reader(prompt):
        out.write(prompt)
        if not feed:
            raise EOFError()
        return feed.pop(0)

    return Console(out=out, err=out, reader=reader, can_prompt=can_prompt, is_tty=True), out


class ContextCase(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def ctx(self, inputs=None, answers=None, can_prompt=True, state=None, env=None):
        console, self.out = _console(inputs, can_prompt)
        app = App(self.box.root, env=env or self.box.environment(), console=console)
        return CheckContext(app, answers=answers, state=state)


# ---------------------------------------------------------------------------
# R1 validate
# ---------------------------------------------------------------------------
class ValidateCase(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def findings(self, lesson_id="1.6"):
        result = self.box.run("validate", "--json", noninteractive=True)
        data = json.loads(result.out)
        for lesson in data["lessons"]:
            if lesson["id"] == lesson_id:
                return (result.code,
                        [f["code"] + " " + f["message"] for f in lesson["errors"]],
                        [f["code"] + " " + f["message"] for f in lesson["warnings"]])
        raise AssertionError(data)

    def folder(self, lesson_id="1.6"):
        entry = helpers.syllabus.lesson_entry(lesson_id)
        return self.box.root / "stages" / entry["stage_folder"] / entry["folder"]


class MinutesBudgetTest(ValidateCase):
    def test_31_minutes_is_a_warning_not_an_error(self):
        # Before plan G5a anything above 25 was an error.
        self.box.add_syllabus_lesson("1.6", minutes=31)
        code, errors, warnings = self.findings()
        self.assertEqual(code, 0, errors)
        self.assertEqual([e for e in errors if e.startswith("G5")], [])
        found = [w for w in warnings if w.startswith("G5") and "1.6a" in w]
        self.assertTrue(found, warnings)
        self.assertIn("31 分钟", found[0])
        self.assertIn("G5a", found[0])
        self.assertIn("「想多了解（可跳过）」", found[0])

    def test_30_and_15_minutes_pass_quietly(self):
        for minutes in (15, 30):
            with self.subTest(minutes=minutes):
                self.box = helpers.Sandbox(self)
                self.box.add_syllabus_lesson("1.6", minutes=minutes)
                code, _errors, warnings = self.findings()
                self.assertEqual(code, 0)
                self.assertEqual([w for w in warnings if "分钟" in w], [])

    def test_above_40_is_an_error_that_says_what_to_do(self):
        self.box.add_syllabus_lesson("1.6", minutes=45)
        code, errors, _warnings = self.findings()
        self.assertEqual(code, 1)
        found = [e for e in errors if e.startswith("G5") and "45 分钟" in e]
        self.assertTrue(found, errors)
        self.assertIn("「想多了解（可跳过）」", found[0])

    def test_not_an_integer(self):
        self.box.add_syllabus_lesson("1.6")
        path = self.folder() / "lesson.py"
        path.write_text(path.read_text(encoding="utf-8").replace('"minutes": 20', '"minutes": 25.5', 1),
                        encoding="utf-8")
        _code, errors, _warnings = self.findings()
        self.assertTrue([e for e in errors if "minutes 要是整数" in e], errors)


class HeadingMinutesTest(ValidateCase):
    def write_text(self, body):
        (self.folder() / "lesson.md").write_text("# 1.6 Git：第一次提交\n\n" + body, encoding="utf-8")

    def heading_warnings(self):
        return [w for w in self.findings()[2] if "lesson.md 第" in w]

    def test_heading_that_disagrees_with_meta_is_a_warning(self):
        self.box.add_syllabus_lesson("1.6", minutes=25)
        self.write_text("## 第 1 站：为什么（约 30 分钟）\n\n## 第二站：第一次提交（约 25 分钟）\n\n"
                        "## 第 3 站：建仓库(约 20 分钟)\n")
        found = self.heading_warnings()
        self.assertEqual(len(found), 2, found)
        self.assertIn("第 3 行写的是第 1 站约 30 分钟，META 里 1.6a 是 25 分钟", found[0])
        self.assertIn("第 3 站约 20 分钟", found[1])

    def test_headings_without_minutes_or_that_agree_are_fine(self):
        self.box.add_syllabus_lesson("1.6", minutes=25)
        self.write_text("## 第 1 站：为什么\n\n## 第 2 站：提交（约 25 分钟，搬家再加约 10 分钟）\n\n"
                        "## 第 9 站：不存在（约 5 分钟）\n## 收尾（5 分钟）\n")
        self.assertEqual(self.heading_warnings(), [])


RESERVED = '''
def _quizzing(ctx):
    ctx.quiz("分页器里按哪个键退出？", ["s", "按 q", "Esc"], "B")

checks["1.6c"] = _quizzing
REVIEW.append({"id": "1.6-w9", "type": "which", "tier": "fluent", "q": "退出 less 按什么？",
               "options": ["q", "Ctrl+Z", "Esc"], "answer": "A"})
REVIEW.append({"id": "1.6-w8", "type": "which", "tier": "fluent", "q": "哪个？",
               "options": ["按 q", "按 s", "Ｑ"], "answer": "A"})
'''


class ReservedWordsTest(ValidateCase):
    def test_options_that_are_review_commands_are_warned(self):
        self.box.add_syllabus_lesson("1.6", extra=RESERVED)
        code, _errors, warnings = self.findings()
        self.assertEqual(code, 0)
        found = [w for w in warnings if w.startswith("I3") and "复习时输入" in w]
        self.assertEqual(len(found), 3, found)
        joined = "\n".join(found)
        self.assertIn("复习题 1.6-w9 的选项 A 只有「q」：复习时输入 q 会结束这次复习", joined)
        self.assertIn("复习题 1.6-w8 的选项 C 只有「Ｑ」", joined)
        self.assertIn("ctx.quiz 的选项 A 只有「s」：复习时输入 s 会跳过这一题", joined)
        self.assertNotIn("按 q」：", joined)

    def test_the_reserved_words_are_the_review_commands(self):
        from courselib.commands import review
        self.assertEqual(review.RESERVED_WORDS["q"], "quit")
        self.assertEqual(review.RESERVED_WORDS["s"], "skip")
        for word in review.RESERVED_WORDS:
            self.assertIsNotNone(review._word(word), word)


# ---------------------------------------------------------------------------
# R2 ctx.choose
# ---------------------------------------------------------------------------
class ChooseTest(ContextCase):
    OPTIONS = (("move", "请导师帮我搬到 ~/Developer（还没搬）"), ("stay-in-sync", "先留在原处，我知道风险"))

    def test_a_choice_is_recorded_neutrally_and_returned(self):
        ctx = self.ctx(answers=["B"])
        value = ctx.choose("你的决定？", self.OPTIONS, key="workspace_location",
                           explain="以后想搬，随时对导师说。")
        self.assertEqual(value, "stay-in-sync")
        self.assertEqual(ctx.decisions, {"workspace_location": "stay-in-sync"})
        self.assertEqual(ctx.oks, ["你的决定：先留在原处，我知道风险"])
        self.assertEqual(ctx.fails, [])
        self.assertEqual(ctx.notes, ["以后想搬，随时对导师说。"])
        self.assertEqual(ctx.asked, [{"kind": "choose", "prompt": "你的决定？", "answer": "B",
                                      "choice": "先留在原处，我知道风险"}])
        self.assertIn("  A. 请导师帮我搬到 ~/Developer（还没搬）", self.out.getvalue())

    def test_plain_labels_any_spelling_and_feedback(self):
        for typed in ("a", "Ａ", "选 A", "接受", "「接受」"):
            with self.subTest(typed=typed):
                ctx = self.ctx(inputs=[typed])
                value = ctx.choose("接受这次改动吗？", ["接受", "不接受"],
                                   feedback={"a": "接受以后记得提交。"})
                self.assertEqual(value, "接受")
                self.assertEqual(ctx.notes, ["接受以后记得提交。"])
                self.assertEqual(ctx.decisions, {})
                self.assertNotIn("答对了", " ".join(ctx.oks))

    def test_unreadable_answer_is_asked_again_then_cancelled(self):
        ctx = self.ctx(inputs=["x", "b"])
        self.assertEqual(ctx.choose("选一个", ["甲", "乙"]), "乙")
        self.assertIn("请输入 A 到 B 之间的一个字母。", self.out.getvalue())
        ctx = self.ctx(inputs=["x", "", "随便"])
        with self.assertRaises(Cancelled):
            ctx.choose("选一个", ["甲", "乙"])
        self.assertEqual((ctx.oks, ctx.fails, ctx.decisions), ([], [], {}))

    def test_scripted_answers_work_like_ask_and_quiz(self):
        ctx = self.ctx(answers=["甲"], can_prompt=False)
        self.assertEqual(ctx.choose("选一个", ["甲", "乙"]), "甲")
        with self.assertRaises(UsageProblem) as caught:
            self.ctx(answers=["c"], can_prompt=False).choose("选一个", ["甲", "乙"])
        self.assertIn("--answer 给的「c」不是 A 到 B 之间的字母", caught.exception.message)
        with self.assertRaises(UsageProblem):
            self.ctx(can_prompt=False).choose("选一个", ["甲", "乙"])

    def test_malformed_questions_are_the_lessons_fault(self):
        ctx = self.ctx(answers=["A"])
        for options in (["只有一个"], ["甲", "甲"], ["甲", ""], "甲乙", [("a", "甲", "x"), "乙"],
                        [(["list"], "甲"), "乙"]):
            with self.subTest(options=options), self.assertRaises(ValueError):
                ctx.choose("选", options)
        with self.assertRaises(ValueError):
            ctx.choose("选", ["甲", "乙"], key="")

    def test_through_the_check_command_the_decision_is_saved(self):
        extra = '''
def _deciding(ctx):
    choice = ctx.choose("课程文件夹放哪？", [("move", "搬走"), ("stay-in-sync", "留在原处")],
                        key="workspace_location")
    if choice == "move":
        ctx.fail("搬好以后在新位置再运行这个检查", where="课程文件夹", saw="还在原处")

checks["1.6c"] = _deciding
'''
        self.box.add_syllabus_lesson("1.6", extra=extra)
        stay = self.box.run("check", "1.6c", "--answer", "B", noninteractive=True)
        self.assertEqual(stay.code, 0, stay)
        self.assertIn("你的决定：留在原处", stay.out)
        for word in ("答对了", "选对了", "还没选对"):
            self.assertNotIn(word, stay.out)
        self.assertEqual(self.box.state()["decisions"]["workspace_location"], "stay-in-sync")
        stored = self.box.last_result()
        self.assertEqual(stored["asked"][0]["kind"], "choose")
        self.assertNotIn("correct", stored["asked"][0])


# ---------------------------------------------------------------------------
# R3 gates
# ---------------------------------------------------------------------------
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


def exam_extra(lesson_id, count, gate=None, minutes=3):
    gate = gate or helpers.syllabus.lesson_entry(lesson_id)["gate"]
    tasks = ", ".join(f"_xtask({n}, {gate!r})" for n in range(1, count + 1))
    return EXAM_TASKS.format(id=lesson_id, tasks=tasks, minutes=minutes)


class GateTest(ContextCase):
    """R3 under the gate rule of COMMON.md section 1 (G1, G3)."""

    def setUp(self):
        ContextCase.setUp(self)
        self.box.add_syllabus_lesson("1.6", extra=exam_extra("1.6", 2))
        self.box.add_syllabus_lesson("1.7", extra=exam_extra("1.7", 1, minutes=6))

    def state(self, gate_results, attempt=None, explain=None):
        state = {"exams": {"gate-b": gate_results}}
        if attempt is not None:
            state["exam_attempts"] = {"gate-b": attempt}
        if explain is not None:
            state["explain"] = {"gate-b": explain}
        return state

    @staticmethod
    def passed():
        return {"result": "pass", "date": "2026-11-25"}

    def test_nothing_tried_is_not_done(self):
        ctx = self.ctx(state={})
        self.assertFalse(ctx.gate_done("gate-b"))
        result = ctx.gate_result("gate-b")
        self.assertEqual((result.attempts, result.passed, result.open, result.done, result.tasks),
                         (0, (), (), False, 3))
        self.assertEqual(result.open_titles, ())
        self.assertEqual((result.gate, result.title), ("gate-b", "本地 Git 关卡"))
        self.assertEqual((result.practical_done, result.explain, result.explain_date),
                         (False, None, None))
        self.assertEqual((result.lessons, result.open_lessons), (("1.6", "1.7"), ("1.6", "1.7")))
        self.assertEqual(result.open_lesson_titles, ("Git：第一次提交", "Git：看懂改了什么"))
        # the next sitting: one task per lesson; 1.6 draws one of two 3-minute tasks
        self.assertEqual((result.next_count, result.next_minutes), (2, 9))

    def test_one_passed_task_per_lesson_and_explain_pass_is_done(self):
        practical = {"1.6-x2": {"result": "pass"}, "1.7-x1": {"result": "pass"}}
        ctx = self.ctx(state=self.state(practical))
        result = ctx.gate_result("gate-b")
        self.assertTrue(result.practical_done)
        self.assertFalse(result.done)                 # the explain-back is still missing
        self.assertFalse(ctx.gate_done("gate-b"))
        self.assertEqual((result.next_count, result.next_minutes), (0, 0))
        again = self.ctx(state=self.state(practical, explain={"result": "again",
                                                                "date": "2026-11-24"}))
        self.assertFalse(again.gate_done("gate-b"))
        self.assertEqual(again.gate_result("gate-b").explain, "again")
        done = self.ctx(state=self.state(practical, explain=self.passed()))
        self.assertTrue(done.gate_done("gate-b"))
        result = done.gate_result("gate-b")
        self.assertEqual((result.done, result.explain, result.explain_date),
                         (True, "pass", "2026-11-25"))
        with self.assertRaises(AttributeError):
            result.done = False

    def test_a_failed_task_is_open_until_its_lesson_has_a_pass(self):
        results = {"1.6-x1": {"result": "pass"}, "1.7-x1": {"result": "fail", "title": "x"}}
        ctx = self.ctx(state=self.state(results, {"attempt": 2, "tasks": [
            {"id": "1.7-x1", "result": None, "minutes": 6}]}, explain=self.passed()))
        self.assertFalse(ctx.gate_done("gate-b"))
        result = ctx.gate_result("gate-b")
        self.assertEqual((result.attempts, result.passed, result.open, result.in_progress),
                         (2, ("1.6-x1",), ("1.7-x1",), True))
        self.assertEqual(result.open_titles, ("1.7 题 1",))
        self.assertEqual(result.open_lessons, ("1.7",))
        self.assertEqual((result.next_count, result.next_minutes), (1, 6))

    def test_untried_tasks_of_a_covered_lesson_are_extra_practice(self):
        # Fails without G1: the old rule wanted 1.6-x2 too.
        partly = {"1.6-x1": {"result": "pass"}, "1.7-x1": {"result": "pass"}}
        self.assertTrue(self.ctx(state=self.state(partly, explain=self.passed())).gate_done("gate-b"))
        # a later fail of a covered lesson does not take it back
        later = dict(partly, **{"1.6-x2": {"result": "fail"}})
        self.assertTrue(self.ctx(state=self.state(later, explain=self.passed())).gate_done("gate-b"))

    def test_same_rule_as_progress_and_the_exam_command(self):
        cases = [{}, {"1.6-x1": {"result": "pass"}},
                 {"1.6-x1": {"result": "fail"}, "1.7-x1": {"result": "pass"}},
                 {"1.6-x1": {"result": "fail", "history": [{"result": "pass"}]},
                  "1.7-x1": {"result": "pass"}}]
        catalog = self.box.app().catalog()
        for case in cases:
            for explain in (None, self.passed()):
                with self.subTest(case=case, explain=explain):
                    state = self.state(case, explain=explain)
                    ctx = self.ctx(state=state)
                    self.assertEqual(ctx.gate_done("gate-b"),
                                     progress.gate_status(catalog, state, "gate-b").done)
                    pool = [("1.6", "1.6-x1"), ("1.6", "1.6-x2"), ("1.7", "1.7-x1")]
                    self.assertEqual(ctx.gate_done("gate-b"),
                                     progress.gate_done(pool, (), case, explain))

    def test_gate_1_borrows_nothing(self):
        # gate-1 covers its own lessons only; 1.6/1.7 belong to gate-b.
        ctx = self.ctx(state={"exams": {"gate-1": {"1.6-x1": {"result": "pass"}}},
                              "explain": {"gate-1": self.passed()}})
        result = ctx.gate_result("gate-1")
        self.assertEqual((result.tasks, result.open, result.done, result.practical_done),
                         (0, (), False, False))
        self.assertEqual(result.lessons, ())

    def test_unknown_gate_is_the_lessons_fault(self):
        with self.assertRaises(ToolTrouble):
            self.ctx(state={}).gate_done("gate-z")

    def test_pure_functions(self):
        pool = ["1.6-x1", "1.6-x2", "1.7-x1"]
        self.assertEqual(progress.gate_lessons(pool), ["1.6", "1.7"])
        self.assertEqual(progress.gate_open_lessons(pool, {"1.6-x2": {"result": "pass"}}), ["1.7"])
        self.assertEqual(progress.gate_open_ids(pool, ["x"], {"1.7-x1": {"result": "fail"},
                                                              "1.6-x1": {"result": "fail"},
                                                              "1.6-x2": {"result": "pass"}}),
                         ["1.7-x1"])
        self.assertFalse(progress.gate_done([], [], {}))
        self.assertFalse(progress.gate_practical_done([], {}))
        self.assertEqual(progress.gate_sitting_plan(pool, {}),
                         [("1.6", ["1.6-x1", "1.6-x2"]), ("1.7", ["1.7-x1"])])
        self.assertEqual(progress.gate_sitting_plan(pool, {"1.6-x2": {"result": "fail"}}),
                         [("1.6", ["1.6-x2"]), ("1.7", ["1.7-x1"])])
        self.assertEqual(progress.gate_minutes([3, 3]), 6)
        self.assertEqual(progress.gate_minutes([5] * 8), 30)
        self.assertEqual(progress.gate_minutes([4, 5, 5, 5, 5, 5, 5]), 30)
        self.assertEqual(progress.gate_minutes([], 0), 0)
        self.assertEqual(progress.gate_minutes([[3, 4], 6]), 10)     # 3.5 + 6 rounded up
        self.assertEqual(progress.explain_record({"result": "pass", "date": "2026-11-25"}),
                         ("pass", "2026-11-25"))
        self.assertEqual(progress.explain_record({"result": "pass", "date": "today"}),
                         ("pass", None))
        self.assertEqual(progress.explain_record({"result": "fail"}), (None, None))
        self.assertEqual(progress.explain_record("pass"), (None, None))
        state = {"explain": "broken"}
        progress.record_explain(state, "gate-0", "again", datetime.date(2026, 11, 24))
        self.assertEqual(state["explain"], {"gate-0": {"result": "again", "date": "2026-11-24"}})
        with self.assertRaises(ValueError):
            progress.record_explain(state, "gate-0", "fail", datetime.date(2026, 11, 24))
        summary = progress.gate_summary(pool, (), {"1.6-x1": {"result": "pass"}})
        self.assertEqual(summary.next_count, 1)
        self.assertEqual(summary["practical_done"], summary.practical_done)
        with self.assertRaises(AttributeError):
            summary.no_such_field   # noqa: B018 - the attribute access is the test


class GlobalGitTest(ContextCase):
    def test_states_of_a_boolean_setting(self):
        self.box.write_gitconfig("[commit]\n\tgpgsign = fasle\n[a]\n\tyes = true\n\tno = false\n"
                                 "\tempty =\n\tbare\n")
        ctx = self.ctx()
        self.assertEqual(ctx.git_global_state("commit.gpgsign"), "invalid")
        self.assertIsNone(ctx.git_global_bool("commit.gpgsign"))     # unchanged meaning
        self.assertEqual(ctx.git_global_state("a.yes"), "true")
        self.assertEqual(ctx.git_global_state("a.no"), "false")
        self.assertEqual(ctx.git_global_state("a.empty"), "false")
        self.assertEqual(ctx.git_global_state("a.bare"), "true")
        self.assertEqual(ctx.git_global_state("a.missing"), "unset")

    def test_every_value_of_a_multi_valued_key(self):
        self.box.write_gitconfig("[x]\n\tv = 1\n\tv = zwei drei\n\tv =\n[gpg \"ssh\"]\n\tprogram =\n")
        ctx = self.ctx()
        self.assertEqual(ctx.git_global_all("x.v"), ["1", "zwei drei", ""])
        self.assertEqual(ctx.git_global_all("gpg.ssh.program"), [""])
        self.assertEqual(ctx.git_global_all("x.none"), [])
        self.assertEqual(ctx.git_global("x.v"), "")                    # unchanged: the last one

    def test_a_broken_file_means_the_tool_could_not_look(self):
        self.box.write_gitconfig("[broken\n")
        ctx = self.ctx()
        for method in (ctx.git_global_state, ctx.git_global_all):
            with self.subTest(method=method.__name__), self.assertRaises(ToolTrouble) as caught:
                method("commit.gpgsign")
            self.assertIn("~/.gitconfig", caught.exception.summary)


# ---------------------------------------------------------------------------
# R5 parse_int
# ---------------------------------------------------------------------------
class ParseIntWhereBeginnersPutItTest(unittest.TestCase):
    def test_numbers_inside_ordinary_answers(self):
        cases = {"第二条": 2, "第四课": 4, "一共三个": 3, "共 12 行": 12, "大概五个": 5,
                 "3 个": 3, "三": 3, "３": 3, "１２ 个": 12, "第 2 站": 2, "十分钟": 10,
                 "3 个，就是三个": 3, "有两条": 2}
        for text, value in cases.items():
            self.assertEqual(parse_int(text), value, text)

    def test_still_none(self):
        for text in ("一共", "一起", "统一", "很多", "", "3 或 4", "第二条，共 3 行", "三四个",
                     "1.1", "3.5", "1.6a", "不是三个", "没有"):
            self.assertIsNone(parse_int(text), text)

    def test_the_old_wrong_answer_is_gone(self):
        self.assertNotEqual(parse_int("一共三个"), 1)


# ---------------------------------------------------------------------------
# R6 one_line and visible
# ---------------------------------------------------------------------------
class VisibleTest(ContextCase):
    def test_one_line_collapses_only_ascii_white_space(self):
        self.assertEqual(ui.one_line(" a \n\t b  c "), "a b c")
        self.assertEqual(ui.one_line("标题" + U3000 + U3000 + "x"), "标题" + U3000 + U3000 + "x")
        self.assertEqual(ui.one_line("a" + NBSP + "b"), "a" + NBSP + "b")

    def test_visible_names_invisible_characters(self):
        self.assertEqual(ui.visible("你好" + U3000 + "世界"), "你好〔全角空格〕世界")
        self.assertEqual(ui.visible("a\tb" + NBSP + "c"), "a〔Tab〕b〔不换行空格〕c")
        self.assertEqual(ui.visible("末尾  "), "末尾··")
        self.assertEqual(ui.visible("一 \n二  \r\n三"), "一·\n二··\r\n三")
        self.assertEqual(ui.visible("  前面的空格不变"), "  前面的空格不变")
        self.assertEqual(self.ctx().visible("x" + U3000), "x〔全角空格〕")

    def test_evidence_keeps_the_ideographic_space(self):
        ctx = self.ctx()
        ctx.fail("标题里多了一个全角空格", where="index.html 的标题",
                 saw="「你好" + U3000 + "我是」")
        ctx.fail("同上", saw=ctx.visible("你好" + U3000 + "我是"))
        result = runner.CheckResult(runner.NOT_YET, fails=ctx.fails)
        text = "\n".join(runner.render_result(ctx._app, result, "1.10b"))
        self.assertIn("「你好" + U3000 + "我是」", text)
        self.assertIn("你好〔全角空格〕我是", text)


# ---------------------------------------------------------------------------
# R7 app.show, R8 scrub
# ---------------------------------------------------------------------------
class LinkedHomeTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.link = self.box.base / "home-link"
        os.symlink(str(self.box.home), str(self.link))

    def app(self, home):
        console, _out = _console()
        return App(self.box.root, env=self.box.environment(HOME=str(home)), console=console)

    def test_show_compares_resolved_paths(self):
        through_link = self.app(self.link)
        self.assertEqual(through_link.show(self.box.home / "Developer" / "x"), "~/Developer/x")
        self.assertEqual(through_link.show(self.link / "Developer"), "~/Developer")
        self.assertEqual(through_link.show(self.box.home), "~")
        direct = self.app(self.box.home)
        self.assertEqual(direct.show(self.link / "Developer"), "~/Developer")
        self.assertEqual(direct.show(self.box.base / "elsewhere"), str(self.box.base / "elsewhere"))
        self.assertEqual(direct.show(str(self.box.home) + "-other/x"), str(self.box.home) + "-other/x")

    def test_scrub_replaces_every_spelling_and_the_account_home(self):
        account = self.box.base / "Users" / "someone"
        with mock.patch("courselib.app.account_home", return_value=str(account)):
            app = self.app(self.link)
            text = (f"File \"{self.box.home}/a.py\" and {self.link}/b and {account}/tools/python3 "
                    f"but not {account}x/c")
            scrubbed = app.scrub(text)
        self.assertEqual(scrubbed, f"File \"~/a.py\" and ~/b and ~/tools/python3 but not {account}x/c")

    def test_a_checker_problem_never_stores_or_prints_a_home(self):
        account = self.box.base / "Users" / "someone"
        extra = f'''
def _boom(ctx):
    import os
    raise RuntimeError(os.path.realpath(str(ctx.home)) + " " + {str(account)!r} + "/lib/x.py")

checks["1.6b"] = _boom
'''
        self.box.add_syllabus_lesson("1.6", extra=extra)
        with mock.patch("courselib.app.account_home", return_value=str(account)):
            result = self.box.run("check", "1.6b", HOME=str(self.link))
        self.assertEqual(result.code, 2, result)
        stored = (self.box.root / "learner" / "last-result.json").read_text(encoding="utf-8")
        for secret in (str(self.box.home), str(self.link), str(account)):
            self.assertNotIn(secret, stored)
            self.assertNotIn(secret, result.text)
        self.assertIn("~/lib/x.py", stored)
        self.assertIn("RuntimeError: ~ ~/lib/x.py", result.out)


# ---------------------------------------------------------------------------
# R9 full-width characters on the command line
# ---------------------------------------------------------------------------
class FullWidthCommandLineTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6")

    def assertFullWidth(self, result, shown):
        self.assertEqual(result.code, 64, result)
        self.assertIn("用法不对：命令里混进了全角字符（中文输入法打出来的空格或符号）：" + shown + "。",
                      result.err)
        self.assertIn("切回英文输入法，把这一段重新打一遍。", result.err)
        self.assertNotIn("没有 check", result.err)

    def test_a_full_width_space_between_command_and_station(self):
        self.assertFullWidth(self.box.run("check" + U3000 + "1.6a"), "check〔全角空格〕1.6a")
        self.assertFullWidth(self.box.run("check", "1.6a" + NBSP + "--again"),
                             "1.6a〔不换行空格〕--again")
        self.assertFullWidth(self.box.run("check", "1.6a", "--answer" + U3000 + "3"),
                             "--answer〔全角空格〕3")

    def test_full_width_option_names(self):
        result = self.box.run("check", "1.6a", "--ａｇａｉｎ")
        self.assertFullWidth(result, "--ａｇａｉｎ")
        self.assertIn("混进来的是：ａ、ｇ、ｉ、ｎ。", result.err)
        self.assertFullWidth(self.box.run("check", "1.6a", "——again"), "——again")

    def test_what_already_worked_still_works(self):
        self.box.flag("1.6a")
        for argv in (("check", "１.６ａ"), ("check", "1.6a" + U3000), ("ｃｈｅｃｋ", "1.6a")):
            with self.subTest(argv=argv):
                self.assertEqual(self.box.run(*argv).code, 0)

    def test_free_text_may_hold_any_space(self):
        extra = '''
def _asking(ctx):
    ctx.ask("几个？", 3)

checks["1.6c"] = _asking
'''
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=extra)
        result = self.box.run("check", "1.6c", "--answer", "三" + U3000 + "个", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        result = self.box.run("check", "1.6c", "--answer=３" + U3000 + "个", noninteractive=True)
        self.assertEqual(result.code, 0, result)


# ---------------------------------------------------------------------------
# R10 resume sentences
# ---------------------------------------------------------------------------
class ResumeSentenceTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def pass_all(self, lesson_id):
        for station in helpers.syllabus.lesson_entry(lesson_id)["stations"]:
            self.box.flag(station)

    def set_exams(self, gate, records):
        path = self.box.root / "learner" / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state.setdefault("exams", {})[gate] = records
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def test_after_the_last_station(self):
        self.box.add_syllabus_lesson("1.7")
        self.box.flag("1.7b")
        middle = self.box.run("check", "1.7b")
        self.assertIn("1.7 课还没通过的站：1.7a", middle.out)
        self.assertIn("下次可以对导师说“从 1.7a 继续”。", middle.out)
        self.box.flag("1.7a")
        last = self.box.run("check", "1.7a")
        self.assertIn("1.7 课的 2 站都通过了。收尾先做全课检查：python3 tools/course.py check 1.7",
                      last.out)
        self.assertIn("下次可以对导师说“从 1.7 的收尾继续”。", last.out)

    def test_after_the_whole_lesson_the_next_lesson(self):
        self.box.add_syllabus_lesson("1.7")
        self.box.add_syllabus_lesson("1.8")
        self.pass_all("1.7")
        result = self.box.run("check", "1.7")
        self.assertEqual(result.code, 0)
        self.assertIn("  下一课：1.8「Git：后悔药」。下次可以对导师说“从 1.8 开始”。\n"
                      "  课文在 stages/01-foundations/08-undo-uncommitted/lesson.md", result.out)

    def set_explain(self, gate, verdict):
        path = self.box.root / "learner" / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state.setdefault("explain", {})[gate] = {"result": verdict, "date": "2026-11-25"}
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def test_a_due_gate_comes_before_the_next_lesson(self):
        # The rule of COMMON.md section 1: one task per lesson (1.6 draws one of
        # its two 4-minute tasks, 1.10 has one of 7 minutes).
        self.box.add_syllabus_lesson("1.6", extra=exam_extra("1.6", 2, minutes=4))
        self.box.add_syllabus_lesson("1.10", extra=exam_extra("1.10", 1, minutes=7))
        self.box.add_syllabus_lesson("1.11")
        self.pass_all("1.10")
        result = self.box.run("check", "1.10")
        self.assertEqual(result.code, 0)
        self.assertIn("下一步是小关卡 gate-b「本地 Git 关卡」：2 道实操题，预计 11 分钟，讲解题另需约 10 分钟。"
                      "开始考试：python3 tools/course.py exam gate-b", result.out)
        self.assertIn("下次可以对导师说“做小关卡 gate-b”。", result.out)
        self.assertNotIn("下一课", result.out)
        # A retest: only the lesson not covered yet, with the task that failed.
        self.set_exams("gate-b", {"1.6-x1": {"result": "fail"}, "1.10-x1": {"result": "pass"}})
        retest = self.box.run("check", "1.10")
        self.assertIn("gate-b「本地 Git 关卡」：1 道实操题，预计 4 分钟，", retest.out)
        # Every lesson covered (1.6-x2 never drawn): no practical task is left.
        self.set_exams("gate-b", {"1.6-x1": {"result": "pass"}, "1.10-x1": {"result": "pass"}})
        practical = self.box.run("check", "1.10")
        self.assertNotIn("道实操题", practical.out)
        # Passed, explain-back included: the next lesson.
        self.set_explain("gate-b", "pass")
        done = self.box.run("check", "1.10")
        self.assertNotIn("关卡", done.out)
        self.assertIn("下一课：1.11「GitHub：账号、安全与身份」。下次可以对导师说“从 1.11 开始”。", done.out)

    def test_an_open_attempt_counts_its_pending_tasks(self):
        self.box.add_syllabus_lesson("1.5", extra=exam_extra("1.5", 3, minutes=5))
        self.pass_all("1.5")
        self.box.run("check", "1.5a")
        path = self.box.root / "learner" / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["exam_attempts"] = {"gate-a": {"attempt": 1, "tasks": [
            {"id": "1.5-x1", "minutes": 5, "result": "pass"},
            {"id": "1.5-x2", "minutes": 6, "result": None},
            {"id": "1.5-x3", "minutes": 5, "result": "problem"}]}}
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        result = self.box.run("check", "1.5")
        # An open sitting is named as such, with --grade (review finding L2).
        self.assertIn("小关卡 gate-a「终端与文档关卡」第 1 场考试还没批改完（2 题）：做完以后批改："
                      "python3 tools/course.py exam gate-a --grade", result.out)

    def test_a_gate_without_tasks_is_skipped(self):
        self.box.add_syllabus_lesson("1.10")
        self.box.add_syllabus_lesson("1.11")
        self.pass_all("1.10")
        result = self.box.run("check", "1.10")
        self.assertNotIn("关卡", result.out)
        self.assertIn("下一课：1.11", result.out)


# ---------------------------------------------------------------------------
# R11 ctx.final
# ---------------------------------------------------------------------------
class FinalTest(ContextCase):
    def test_default_endings_are_unchanged(self):
        ctx = self.ctx(answers=["4", "A"])
        self.assertFalse(ctx.final)
        ctx.ask("几个？", 3)
        ctx.quiz("哪个？", ["甲", "乙"], "B")
        self.assertTrue(ctx.fails[0]["missing"].endswith("然后重新运行检查"))
        self.assertTrue(ctx.fails[1]["missing"].endswith("再想一想，重新运行检查"))

    def test_final_endings(self):
        ctx = self.ctx(answers=["4", "A"])
        ctx.final = True
        ctx.ask("几个？", 3)
        ctx.quiz("哪个？", ["甲", "乙"], "B", feedback={"A": "甲不对"})
        self.assertEqual(ctx.fails[0]["missing"],
                         "这个回答和实际情况对不上，这一题记为还没达标。")
        self.assertEqual(ctx.fails[1]["missing"],
                         "甲不对。这一题没有选对，记为还没达标。")
        for fail in ctx.fails:
            self.assertNotIn("重新运行检查", fail["missing"])

    def test_run_check_sets_it(self):
        seen = []
        app = self.box.app()
        runner.run_check(app, lambda ctx: seen.append(ctx.final) or ctx.ok("好"), final=True)
        runner.run_check(app, lambda ctx: seen.append(ctx.final) or ctx.ok("好"))
        self.assertEqual(seen, [True, False])


if __name__ == "__main__":
    unittest.main()
