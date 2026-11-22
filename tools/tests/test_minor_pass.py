"""The last small pass on the tool, 2026-11-20 (writer ``tools-minor``).

One class per item M1-M8: the seven minor findings of the confirming review
and the explain-back minutes of plan G5a.  Each class has at least one
assertion that fails on the code before this pass.
"""

import re
import subprocess
import sys
import unittest

import helpers
from test_integration import Case

from courselib import progress, status, syllabus, validate
from courselib.normalize import COMPARISON_WORDS, matches, parse_int


# ---------------------------------------------------------------------------
# M1 parse_int: a bound is not a number
# ---------------------------------------------------------------------------
class ComparisonWordsTest(unittest.TestCase):
    def test_every_comparison_word_before_the_number_gives_none(self):
        before = [word for word in COMPARISON_WORDS if word not in ("以上", "以下", "以内", "以外")]
        for word in before:
            for text in (word + "3行", word + " 3 个", word + "三个"):
                self.assertIsNone(parse_int(text), text)

    def test_every_comparison_word_after_the_number_gives_none(self):
        for word in COMPARISON_WORDS:
            for text in ("3 行" + word, "3个" + word, "三个" + word):
                self.assertIsNone(parse_int(text), text)

    def test_the_findings_examples(self):
        for text in ("不超过5个", "不到 3 个", "最多 3 行", "至少 3 行", "3 行以上", "少于3行",
                     "5个以内", "至少有 3 个", "大于等于 3", "3 个或以上", "3 个文件以上",
                     "最多也就 3 行", "不多于 5 个", "不少于 5 个"):
            self.assertIsNone(parse_int(text), text)
            self.assertFalse(matches(text, [3, 5]), text)

    def test_the_word_list_is_the_decided_one(self):
        self.assertEqual(set(COMPARISON_WORDS), {
            "少于", "小于", "低于", "不到", "不足", "不超过", "不多于", "不少于", "至多", "最多",
            "至少", "最少", "超过", "多于", "大于", "高于", "以上", "以下", "以内", "以外"})
        self.assertNotIn("左右", COMPARISON_WORDS)

    def test_about_and_hedges_keep_the_number(self):
        for text, value in {"3 个左右": 3, "差不多 3 个": 3, "大概 3 个": 3, "三个左右": 3,
                            "除了 . 和 .. 以外有 5 个": 5, "一共 5 个": 5}.items():
            self.assertEqual(parse_int(text), value, text)

    def test_a_filler_or_a_bracket_does_not_hide_the_bound(self):
        # Checker of the last pass: 了 / 得 / 只 after the word, or the word
        # alone in brackets, still give a bound.
        for text in ("超过了 3 个", "至少得 3 个", "最多只有 3 个", "最少也有 3 个",
                     "至少得有 3 个", "3（以上）", "3 个（至少）", "3 (以下)", "（至少）3 个"):
            self.assertIsNone(parse_int(text), text)
            self.assertFalse(matches(text, 3), text)

    def test_after_an_ordinal_the_word_bounds_nothing(self):
        for text, value in {"第 3 行最多": 3, "第三条最多": 3, "第 3 个文件最大": 3,
                            "第 3 行以下": 3, "3 个（最多的那组）": 3, "最多的是 3 个": 3}.items():
            self.assertEqual(parse_int(text), value, text)
        # Without 第 the tool cannot tell a label or 'the following' from a
        # bound; documented in tool-api.md section 8.
        for text in ("3 号最多", "3 行以下是空行"):
            self.assertIsNone(parse_int(text), text)


# ---------------------------------------------------------------------------
# M2 parse_int: a bracket or spaces do not hide a negation
# ---------------------------------------------------------------------------
class NegationGapTest(unittest.TestCase):
    def test_bracket_or_spaces_between_negation_and_number(self):
        for text in ("不是（3）", "没有（3 个）", "不 是 5", "不太是 5", "不是 (3)", "不是　5",
                     "不一定是 5", "没有 （ 3 个 ）"):
            self.assertIsNone(parse_int(text), text)

    def test_remarks_keep_the_number(self):
        for text, value in {"3（不确定）": 3, "5 个，不算 . 和 ..": 5, "（3 个）": 3,
                            "应该是 3 个吧，不太确定": 3, "4 行（第一行是标题）": 4}.items():
            self.assertEqual(parse_int(text), value, text)


# ---------------------------------------------------------------------------
# M3 validate: a named release next to Chinese text says since when
# ---------------------------------------------------------------------------
class NamedReleaseTest(unittest.TestCase):
    def test_without_spaces_next_to_chinese(self):
        for text in ("从 macOS Catalina起默认是 zsh", "从macOS Catalina起默认是 zsh", "从Python 3起",
                     "从 macOS Catalina 起", "Big Sur以后", "macOS 15起"):
            self.assertTrue(validate._since_when(text), text)

    def test_a_count_is_not_a_release(self):
        for text in ("Git 2 种写法", "Git 2种写法", "Python 3 个版本", "Git 两种写法", "CatalinaX"):
            self.assertFalse(validate._since_when(text), text)

    def test_through_the_box_check(self):
        text = ("# 课\n\n> **旧教程提醒**：旧教程用 bash；从macOS Catalina起默认是 zsh。\n\n"
                "> **旧教程提醒**：Git 2 种写法都能用。\n")
        report = validate.Report("x")
        validate._check_old_tutorial_boxes(report, validate.Doc(text))
        found = [item.message for item in report.warnings]
        self.assertEqual(len(found), 1, found)
        self.assertIn("Git 2 种写法", found[0])


# ---------------------------------------------------------------------------
# M4 validate: optional material in a heading
# ---------------------------------------------------------------------------
class OptionalHeadingTest(unittest.TestCase):
    def test_reported(self):
        for title in ("可选的进阶", "这一段可选", "进阶，可选", "进阶, 可选", "补充（可以跳过的部分）",
                      "再练一次（可选）", "选做：再练一次", "选读的材料", "这部分选做"):
            self.assertTrue(validate._OPTIONAL_IN_HEADING.search(title), title)

    def test_through_the_heading_check(self):
        text = ("# 课\n\n### 可选的进阶\n\n### 这一段可选\n\n### 进阶，可选\n\n"
                "### 补充（可以跳过的部分）\n\n### 自己做（可选的两种做法都行）\n")
        report = validate.Report("x")
        validate._check_optional_labels(report, validate.Doc(text))
        found = [item.message for item in report.warnings]
        self.assertEqual(len(found), 4, found)
        self.assertFalse(any("自己做" in message for message in found), found)

    def test_a_word_inside_a_sentence_is_fine(self):
        for title in ("自己做（可选的两种做法都行）", "自己做：两种做法可选其一", "补全"):
            self.assertFalse(validate._OPTIONAL_IN_HEADING.search(title), title)


# ---------------------------------------------------------------------------
# M5 gate_full_plan: the six-lesson limit is stated
# ---------------------------------------------------------------------------
class FullPlanLimitTest(unittest.TestCase):
    def test_no_gate_has_more_lessons_than_a_sitting_holds(self):
        for gate, entry in syllabus.GATES.items():
            self.assertLessEqual(len(entry["lessons"]), progress.GATE_MAX_TASKS, gate)

    def test_the_limit_is_documented(self):
        doc = " ".join(progress.gate_full_plan.__doc__.split())
        self.assertIn("never come up in extra practice", doc)
        api = (helpers.REPO / "docs" / "authoring" / "tool-api.md").read_text(encoding="utf-8")
        self.assertIn("no gate may have more than six lessons", api)


# ---------------------------------------------------------------------------
# M6 status: landing and stage lines follow the lesson of the first line
# ---------------------------------------------------------------------------
PLACES = {  # gate: (lessons in the sandbox, the lesson the gate follows, stage title)
    "gate-0": (("0.3", "0.4", "1.1"), "0.4"),
    "gate-a": (("1.4", "1.5", "1.6"), "1.5"),
    "gate-b": (("1.9", "1.10", "1.11"), "1.10"),
    "gate-1": (("1.15", "1.16"), "1.16"),
}


class LandingFollowsHereTest(Case):
    def body(self, write=False):
        result = self.box.run("status", "--write") if write else self.box.run("status")
        lines = []
        for line in result.out.splitlines()[2:]:
            if not line.strip():
                break
            lines.append(line.strip())
        return lines

    def check_lines(self, lines, lesson, gate):
        label = syllabus.gate_label(gate)
        stage = syllabus.lesson_entry(lesson)["stage"]
        text = "\n".join(lines)
        self.assertNotIn("还有 0 站", text)
        for before, after in zip(lines, lines[1:]):
            self.assertNotEqual(before, after)
        landing = [line for line in lines if "落脚点" in line]
        stage_lines = [line for line in lines if line.startswith("阶段 ")]
        self.assertEqual(len(landing), 1, lines)
        self.assertEqual(len(stage_lines), 1, lines)
        self.assertTrue(stage_lines[0].startswith(f"阶段 {stage} "), lines)
        self.assertTrue(stage_lines[0].endswith("（100%）") or stage != 0, lines)
        self.assertIn(label, landing[0])
        return landing[0]

    def progress_agrees(self):
        printed = self.body(write=True)
        md = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8").split("## 现在在哪\n\n")[1]
        mine = [line[2:] for line in md.split("\n\n")[0].splitlines()]
        self.assertEqual(printed, mine)

    def walk(self, gate):
        lessons, last = PLACES[gate]
        self.gate = gate
        for lesson in lessons:
            gated = lesson in syllabus.GATES[gate]["lessons"]
            self.lesson(lesson, tasks=1 if gated else 0)
        for lesson in lessons:
            if lesson == last:
                break
            self.pass_lesson(lesson)
        for station in syllabus.lesson_entry(last)["stations"]:
            self.box.flag(station)
            self.assertEqual(self.box.run("check", station).code, 0)
        title = syllabus.lesson_entry(last)["title"]
        label = syllabus.gate_label(gate)

        # 1. the closing steps are open
        lines = self.body()
        self.assertEqual(lines[0], f"你在：{last} {title} · 收尾")
        landing = self.check_lines(lines, last, gate)
        self.assertEqual(landing, "下一个落脚点是{}{}（学完 {}）：站都通过了，还差 {} 课的收尾".format(
            " " if label[:1].isascii() else "", label, last, last))
        self.progress_agrees()

        # 2. the gate is due, nothing tried
        self.assertEqual(self.box.run("check", last).code, 0)
        lines = self.body()
        self.assertEqual(lines[0], f"你在：{label}（学完 {last} 课以后）")
        self.assertEqual(self.check_lines(lines, last, gate), "落脚点到了：" + label)
        self.progress_agrees()

        # 2b. a sitting is open
        self.box.run("exam", gate)
        lines = self.body()
        self.assertEqual(self.check_lines(lines, last, gate), "落脚点到了：" + label)
        self.solve(*[f"{lesson}-x1" for lesson in syllabus.GATES[gate]["lessons"]])
        self.assertEqual(self.box.run("exam", gate, "--grade").code, 0)

        # 3. practical part passed, explain-back open
        lines = self.body()
        self.assertEqual(lines[0], f"你在：{label}（学完 {last} 课以后）")
        self.assertIn("还差讲解题（约 10 分钟）：请导师问你讲解题，", lines[1])
        self.assertEqual(self.check_lines(lines, last, gate), "落脚点到了：" + label)
        self.progress_agrees()

        # 4. everything passed: every line follows the next lesson
        self.assertEqual(self.box.run("exam", gate, "--explain", "pass").code, 0)
        lines = self.body()
        self.assertNotIn("落脚点到了", "\n".join(lines))
        self.assertNotIn("还有 0 站", "\n".join(lines))
        self.progress_agrees()
        return lines

    def test_end_of_stage_0(self):
        lines = self.walk("gate-0")
        self.assertTrue(lines[0].startswith("你在：1.1 "), lines)
        self.assertTrue(any(line.startswith("阶段 1 ") for line in lines), lines)

    def test_after_lesson_1_5(self):
        lines = self.walk("gate-a")
        self.assertTrue(lines[0].startswith("你在：1.6 "), lines)

    def test_after_lesson_1_10(self):
        lines = self.walk("gate-b")
        self.assertTrue(lines[0].startswith("你在：1.11 "), lines)

    def test_after_lesson_1_16_the_last_lesson(self):
        lines = self.walk("gate-1")
        self.assertTrue(lines[0].startswith("已有的课程的站都通过了"), lines)
        self.assertIn("准备阶段 2", lines[1])

    def test_the_all_done_line_is_documented_as_after_the_last_gate(self):
        # Checker of the last pass: tool-api.md 6.8 said the all-done line
        # follows the last station, which is no longer true.
        doc = (helpers.REPO / "docs" / "authoring" / "tool-api.md").read_text(encoding="utf-8")
        self.assertNotIn("When every station has passed, the first line is", doc)
        self.assertIn("once the gate after the last lesson, gate-1, is passed), the first line is "
                      "「已有的课程的站都通过了（52/52 站）。」", doc)

    def test_a_lesson_in_the_middle_is_unchanged(self):
        self.lesson("1.6")
        self.lesson("1.7")
        self.lesson("1.10")
        for station in syllabus.lesson_entry("1.6")["stations"]:
            self.box.flag(station)
            self.box.run("check", station)
        lines = self.body()
        self.assertEqual(lines[0], "你在：1.6 Git：第一次提交 · 收尾")
        self.assertIn("下一个落脚点是小关卡 gate-b「本地 Git 关卡」（学完 1.10），还有 4 站", lines)


# ---------------------------------------------------------------------------
# M7 build_starter_manifest.py -h warns about --write
# ---------------------------------------------------------------------------
class ManifestHelpTest(unittest.TestCase):
    def test_write_help_says_builders_only(self):
        script = helpers.REPO / "tools" / "dev" / "build_starter_manifest.py"
        done = subprocess.run([sys.executable, str(script), "-h"], capture_output=True, check=False,
                              env={"PYTHONDONTWRITEBYTECODE": "1", "COLUMNS": "200",
                                   "PATH": "/usr/bin:/bin"}, timeout=60)
        out = " ".join(done.stdout.decode("utf-8").split())
        self.assertEqual(done.returncode, 0)
        self.assertIn("(builders only; never run it in the learner's workspace)", out)


# ---------------------------------------------------------------------------
# M8 the explain-back takes about 10 minutes; no count of questions
# ---------------------------------------------------------------------------
class ExplainMinutesTest(Case):
    gate = "gate-0"

    def test_the_constant(self):
        self.assertEqual(status.EXPLAIN_MINUTES, 10)
        from courselib.commands import exam
        self.assertEqual(exam.EXPLAIN_MINUTES, 10)

    def test_no_sentence_counts_the_questions(self):
        pattern = re.compile(r"[两二三2-3]\s*[道个]\s*(?:讲解题|问题|“为什么)")
        for path in sorted((helpers.REPO / "tools" / "courselib").rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(pattern.search(text), path.name)
            self.assertNotIn("约 5 分钟", text, path.name)

    def test_check_status_and_exam(self):
        for lesson in ("0.3", "0.4"):
            self.lesson(lesson, tasks=1)
        self.lesson("1.1")
        self.pass_lesson("0.3")
        for station in syllabus.lesson_entry("0.4")["stations"]:
            self.box.flag(station)
            self.box.run("check", station)
        done = self.box.run("check", "0.4").out
        self.assertIn("下一步是 gate-0「起步小关卡」：2 道实操题，预计 8 分钟，讲解题另需约 10 分钟。"
                      "开始考试：python3 tools/course.py exam gate-0", done)
        head = self.box.run("exam", "gate-0").out
        self.assertIn("一共 2 题，每课一题，预计 8 分钟（每题的预计分钟数加起来）。", head)
        self.assertIn("实操题都通过以后还有讲解题，约 10 分钟：导师问你几个问题，请你讲出“为什么这样做”。", head)
        self.solve("0.3-x1", "0.4-x1")
        self.box.run("exam", "gate-0", "--grade")
        sentence = ("gate-0「起步小关卡」的实操题都通过了，还差讲解题（约 10 分钟）：请导师问你讲解题，"
                    "评完用 python3 tools/course.py exam gate-0 --explain pass 记下（要再来一次就写 again）。")
        self.assertIn("下一步：" + sentence, self.box.run("status").out)
        practice = self.box.run("exam", "gate-0", "--all").out
        self.assertIn("讲解题还差一次，约 10 分钟：对导师说“请问我 gate-0 的讲解题”。", practice)


class HundredsTest(unittest.TestCase):
    """Chinese numerals with 百 / 千: read properly or not at all (orchestrator, 2026-11-20)."""

    def test_hundreds_and_thousands_are_read(self):
        from courselib.normalize import parse_int
        for text, value in (("一百二十", 120), ("一百二十个", 120), ("一百零五", 105), ("三百", 300),
                            ("两千", 2000), ("一千零二十", 1020), ("一千二百行", 1200), ("共一百行", 100),
                            ("九十九", 99), ("十", 10), ("十二", 12), ("二十", 20), ("零", 0), ("两个", 2)):
            self.assertEqual(parse_int(text), value, text)

    def test_never_a_wrong_number(self):
        from courselib.normalize import parse_int
        for text in ("一百二", "三四个", "零五", "二零", "十十", "一百十二", "一百零", "三万", "两亿", "百"):
            self.assertIsNone(parse_int(text), text)

    def test_words_stay_words(self):
        from courselib.normalize import parse_int
        self.assertEqual(parse_int("3 个，万一不对再说"), 3)
        self.assertEqual(parse_int("一共 3 个"), 3)
        self.assertIsNone(parse_int("千万别删"))


if __name__ == "__main__":
    unittest.main()
