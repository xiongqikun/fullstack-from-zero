"""The pass on the tool after the lesson round, 2026-11-20 (writer ``tools-r5``).

One class per item that changes behaviour (T1-T5, T7, T8 are tested here or
in the module's own test file).  Each class has at least one assertion that
fails on the code before this pass.
"""

import datetime
import importlib.util
import json
import types
import unittest
from unittest import mock

import envstubs
import helpers
import test_doctor
import test_validate_forms as vf
from test_context import ContextTestCase

from courselib import syllabus, validate
from courselib.commands import doctor
from courselib.errors import CheckStop
from courselib.normalize import OPTION_DOTS, fold_dots, option_text_index

PASSED = {"first_pass": "2026-11-20T10:00:00", "status": "passed"}
OPEN = {"attempts": 1, "status": "open"}


# ---------------------------------------------------------------------------
# T1 doctor: a .git in the workspace once the learner reached lesson 1.12
# ---------------------------------------------------------------------------
@unittest.skipUnless(envstubs.REAL_GIT, "git is not installed")
class WorkspaceGitLineTest(unittest.TestCase):
    """The line 「学习工作区：最外层有一个 .git …」 only before lesson 1.12 is reached."""

    setUp = test_doctor.DoctorTest.setUp
    home = test_doctor.DoctorTest.home
    doctor = test_doctor.DoctorTest.doctor
    groups = test_doctor.DoctorTest.groups
    state = test_doctor.DoctorTest.state

    def workspace_lines(self):
        return [t for t in self.groups(self.doctor())["todo"] if t.startswith("学习工作区：")]

    @staticmethod
    def stations(*lessons, extra=None):
        found = {}
        for lesson in lessons:
            for station in syllabus.lesson_entry(lesson)["stations"]:
                found[station] = dict(PASSED)
        found.update(extra or {})
        return {"stations": found}

    def test_no_git_folder_no_line(self):
        self.home()
        self.state(self.stations("1.10"))
        self.assertEqual(self.workspace_lines(), [])

    def test_git_folder_with_nothing_passed_is_named_as_today(self):
        self.home()
        (self.box.root / ".git").mkdir()
        lines = self.workspace_lines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith("→ 对导师说“急救：学习工作区里多了 .git”"), lines)

    def test_lesson_1_11_partly_passed_still_names_it(self):
        self.home()
        (self.box.root / ".git").mkdir()
        earlier = [entry["id"] for entry in syllabus.LESSONS
                   if syllabus.lesson_key(entry["id"]) <= (1, 10)]
        self.state(self.stations(*earlier, extra={"1.11a": dict(PASSED), "1.11b": dict(PASSED),
                                                  "1.11c": dict(OPEN), "1.12a": dict(OPEN)}))
        self.assertEqual(len(self.workspace_lines()), 1)

    def test_every_station_of_1_11_passed_hides_it(self):
        # the tester of lesson 1.12: station 1 started again after git init
        self.home()
        (self.box.root / ".git").mkdir()
        earlier = [entry["id"] for entry in syllabus.LESSONS
                   if syllabus.lesson_key(entry["id"]) <= (1, 11)]
        self.state(self.stations(*earlier, extra={"1.12a": dict(OPEN)}))
        self.assertEqual(self.workspace_lines(), [])
        result = self.doctor()
        self.assertNotIn("最外层有一个 .git", result.out)

    def test_1_12a_passed_hides_it_as_before(self):
        self.home()
        (self.box.root / ".git").mkdir()
        self.state({"stations": {"1.12a": dict(PASSED)}})
        self.assertEqual(self.workspace_lines(), [])

    def test_a_station_of_a_later_lesson_hides_it(self):
        self.home()
        (self.box.root / ".git").mkdir()
        self.state({"stations": {"1.13b": dict(PASSED)}})
        self.assertEqual(self.workspace_lines(), [])
        # an open station of a later lesson, or a key that is no station, does not
        self.state({"stations": {"1.13b": dict(OPEN), "x.ya": dict(PASSED), "2.1": dict(PASSED)}})
        self.assertEqual(len(self.workspace_lines()), 1)

    def test_unknown_stations_of_1_11_behave_as_before(self):
        self.home()
        (self.box.root / ".git").mkdir()
        self.state(self.stations("1.11"))
        with mock.patch.object(doctor.syllabus, "lesson_entry", lambda lesson_id: None):
            self.assertEqual(len(self.workspace_lines()), 1)
        self.state({"stations": "damaged"})
        self.assertEqual(len(self.workspace_lines()), 1)
        (self.box.root / "learner" / "state.json").write_text("{ damaged", encoding="utf-8")
        self.assertEqual(len(self.workspace_lines()), 1)


# ---------------------------------------------------------------------------
# T2 validate: a closing step is classified from its first line
# ---------------------------------------------------------------------------
class ClosingStepKindTest(vf.FormsTestCase):
    RULES = ("REMOTE-01", "REMOTE-02")

    def text(self, step):
        text = vf.good_text("1.12", rules=self.RULES, closing=10,
                            end=validate.CLOSING_END.format(lesson="1.13"))
        start = text.index("4. 备份：")
        stop = text.index("```\n", text.index("git push", start)) + 4
        return text[:start] + step + text[stop:]

    def found(self, step):
        return vf.forms(self.text(step), "1.12", rules=self.RULES)

    def test_backup_step_with_git_status_output_naming_my_rules(self):
        step = ("4. 备份：把今天的笔记和日志推到云端。\n\n"
                "   ```text\n   Changes not staged for commit:\n"
                "   \tmodified:   notes/my-rules.md\n   ```\n\n"
                "   ```zsh\n   git add .\n   git commit -m \"docs: 记日志\"\n   git push\n   ```\n")
        found = self.found(step)
        self.assertNone(found, "收尾里没有「备份」这一步")
        self.assertNone(found, "顺序不对")

    def test_notes_step_whose_continuation_mentions_backup_stays_notes(self):
        text = vf.good_text("1.6", rules=("GIT-01", "GIT-02"))
        notes = "2. " + validate._notes_line(["GIT-01", "GIT-02"],
                                              vf.cards_for("1.6", ("GIT-01", "GIT-02")))
        text = text.replace(notes, notes + "\n\n   写完以后第 1.12 课会教你备份和推送。")
        found = vf.forms(text)
        self.assertNone(found, "收尾里没有「行规笔记」这一步")
        self.assertNone(found, "顺序不对")

    def test_a_first_line_that_names_nothing_is_read_with_its_continuation(self):
        step = ("4. 最后做这一组命令：\n\n"
                "   ```zsh\n   git add .\n   git commit -m \"docs: 记日志\"\n   git push\n   ```\n")
        found = self.found(step)
        self.assertNone(found, "收尾里没有「备份」这一步")
        self.assertNone(found, "备份这一步要写出那一组命令")


# ---------------------------------------------------------------------------
# T3 need_repo praises only with praise=True
# ---------------------------------------------------------------------------
class NeedRepoPraiseTest(ContextTestCase):
    def test_a_repository_is_not_praised_unless_asked(self):
        base = self.box.home / "Developer"
        self.box.git(base, "init", "-q", "-b", "main", "exam")
        ctx = self.ctx()
        self.assertTrue(ctx.need_repo(base / "exam", "考试仓库").is_repo)
        self.assertEqual(ctx.oks, [])
        ctx.need_repo(base / "exam", "考试仓库", praise=True)
        self.assertEqual(ctx.oks, ["是一个 Git 仓库：考试仓库"])

    def test_failures_are_unchanged(self):
        base = self.box.home / "Developer"
        (base / "plain").mkdir()
        ctx = self.ctx()
        with self.assertRaises(CheckStop):
            ctx.need_repo(base / "plain", "练习仓库", praise=True)
        self.assertEqual(ctx.oks, [])
        self.assertEqual(ctx.fails[0]["where"], "练习仓库")


# ---------------------------------------------------------------------------
# T4 grep and zip are tool names a lesson may record
# ---------------------------------------------------------------------------
class ToolNamesTest(unittest.TestCase):
    def meta_findings(self, tools):
        meta = {"id": "1.3", "title": "终端：查找", "stage": 1, "minutes": 20,
                "verified": {"date": "2026-11-20", "tools": tools}}
        lesson = types.SimpleNamespace(
            folder=helpers.REPO / "stages" / "01-foundations" / "03-search")
        report = validate.Report(None)
        validate._check_meta(report, lesson, meta, datetime.date(2026, 11, 20), False)
        return [f.message for f in report.findings if f.code == "G4"]

    def test_grep_and_zip_are_accepted(self):
        self.assertEqual(syllabus.TOOL_NAMES["grep"], "grep（查找文字的命令）")
        self.assertEqual(syllabus.TOOL_NAMES["zip"], "zip（打包压缩的命令）")
        found = self.meta_findings({"macos": "27.2.1", "grep": "2.6.0", "zip": "3.0"})
        self.assertEqual([m for m in found if "名单" in m], [])
        self.assertTrue(any("名单" in m for m in self.meta_findings({"grepp": "2.6.0"})))

    def test_they_stay_out_of_the_baseline(self):
        baseline = json.loads((helpers.TOOLS / "courselib" / "baseline.json").read_text(encoding="utf-8"))
        tools = baseline.get("tools", baseline)
        self.assertNotIn("grep", tools)
        self.assertNotIn("zip", tools)


# ---------------------------------------------------------------------------
# T5 an option's text typed with another dot
# ---------------------------------------------------------------------------
_SPEC = importlib.util.spec_from_file_location(
    "lesson_0_3_for_r5", str(helpers.REPO / "stages" / "00-orientation"
                             / "03-how-software-is-made" / "lesson.py"))
LESSON_0_3 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(LESSON_0_3)


class OptionDotsTest(ContextTestCase):
    def options(self):
        # the third question of check 0.3c: answer 惯例·事实标准, 行业要求 dropped
        return LESSON_0_3._label_options("惯例·事实标准", "行业要求")

    def test_the_text_typed_with_a_full_stop_names_the_option(self):
        options = self.options()
        right = "ABCDEF"[options.index("惯例·事实标准")]
        for typed in ("惯例.事实标准", "惯例。事实标准", "惯例．事实标准", "惯例・事实标准",
                      "惯例•事实标准", "惯例‧事实标准", "惯例∙事实标准", "惯例·事实标准",
                      "「惯例.事实标准」"):
            ctx = self.ctx(inputs=[typed])
            self.assertTrue(ctx.quiz("这句话的规则类型是哪一种？", options, right), typed)
            self.assertEqual(ctx.asked[0]["answer"], right)

    def test_the_tester_case_is_no_longer_called_a_bad_letter(self):
        options = self.options()
        right = "ABCDEF"[options.index("惯例·事实标准")]
        ctx = self.ctx(answers=["惯例.事实标准"])
        self.assertTrue(ctx.quiz("这句话的规则类型是哪一种？", options, right))
        self.assertEqual(ctx.fails, [])

    def test_letters_and_numbers_mean_what_they_meant(self):
        options = self.options()
        for typed, index in (("b", 1), ("B.", 1), ("Ｂ。", 1), ("c．", 2)):
            ctx = self.ctx(inputs=[typed])
            ctx.quiz("题目", options, "A")
            self.assertEqual(ctx.asked[0]["answer"], "ABCDEF"[index], typed)
        self.assertIsNone(option_text_index("7.20", ["7·20 分", "720"]))
        self.assertEqual(option_text_index("7.20", ["7·20", "720"]), 0)
        self.assertEqual(fold_dots("7.20"), "7.20")

    def test_an_answer_that_names_two_options_after_folding_names_none(self):
        options = ["惯例·事实标准", "惯例.事实标准", "个人偏好"]
        self.assertIsNone(option_text_index("惯例。事实标准", options))
        ctx = self.ctx(inputs=["惯例。事实标准", "x", "y"])
        self.assertFalse(ctx.quiz("题目", options, "A"))
        self.assertIn("不是 A 到 C 之间的字母", ctx.fails[0]["saw"])

    def test_the_folded_characters(self):
        self.assertEqual(set(OPTION_DOTS), set(".。．·・•‧∙"))
        self.assertEqual(fold_dots("a·b・c•d‧e∙f。g．h"), "a.b.c.d.e.f.g.h")

    def test_review_choice_items_read_option_text_the_same_way(self):
        from courselib.commands import review as review_command
        self.assertIs(review_command.option_text_index, option_text_index)
        self.assertEqual(option_text_index("规范.组织", ["标准", "规范·组织"]), 1)


# ---------------------------------------------------------------------------
# T7 the station counts quoted in tool-api.md
# ---------------------------------------------------------------------------
class StationCountsTest(unittest.TestCase):
    def test_the_syllabus_has_40_stations_in_stage_1_and_52_in_all(self):
        counts = {}
        for entry in syllabus.LESSONS:
            counts[entry["stage"]] = counts.get(entry["stage"], 0) + len(entry["stations"])
        self.assertEqual(counts, {0: 12, 1: 40})

    def test_tool_api_quotes_them(self):
        text = (helpers.REPO / "docs" / "authoring" / "tool-api.md").read_text(encoding="utf-8")
        for stale in ("51/51 站", "0/39 站", "/39 站", "/51 站"):
            self.assertFalse(stale in text, stale)


if __name__ == "__main__":
    unittest.main()
