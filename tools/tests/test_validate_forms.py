"""``validate``: the one wording of the recurring parts of lesson.md (V1-V12).

Most tests call ``validate.check_lesson_forms`` on a generated lesson text that
follows every fixed form, change one thing and look for exactly the finding
that change must cause.  The last tests run the whole command in a sandbox
(lesson.py texts, rule cards, the checks across lessons) and read the three
real lessons 0.2, 1.6 and 1.12.
"""

import json
import re
import unittest

import helpers

from courselib import rulecards, validate

RULE_TITLES = {"GIT-01": "一个项目一个仓库", "GIT-02": "提交前确认身份设置",
               "PM-01": "每个任务有明确的完成标准", "PM-02": "固定周期复盘",
               "REMOTE-01": "重要仓库在别处有第二份", "REMOTE-02": "推送前先查密钥",
               "PUB-01": "公开仓库三件套", "DOC-01": "每个项目有 README",
               "DOC-02": "README 回答五个问题", "PM-03": "每个阶段结束做一次复盘"}

CARD = """### {rule} {title}

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：一句话。
- **谁说的**：示例出处 https://example.com/{rule}
- **核对日期**：2026-11-19；**复核周期**：12 个月
- **谁来管**：评审人；**不遵守的后果**：一句话。
- **为什么**：两三句。
- **正例**：`正例`
- **反例**：`反例`
- **怎么检查**：人工检查：看一遍
- **例外**：无
- **旧教程提醒**：无
- **学于**：{lesson}
"""


def cards_for(lesson_id, rules):
    text = "\n".join(CARD.format(rule=r, title=RULE_TITLES[r], lesson=lesson_id) for r in rules)
    return rulecards.parse_cards(text)


def station(lesson_id, letter, number, last, minutes, mark=False, mid=None):
    sid = lesson_id + letter
    target = f"从 {lesson_id} 的收尾继续" if last else f"从 {lesson_id}{chr(ord(letter) + 1)} 继续"
    lines = [f"## 第 {number} 站：示例（约 {minutes} 分钟）", "", "### 概念", "",
             "一个新概念。", "", "### 跟我做", "", "```zsh", "pwd", "```", ""]
    if mark:
        lines += ["打开设置页面〔对照文档，界面可能不同〕。", "",
                  validate.G6_LINE, ""]
    lines += ["### 补全", "", "填空。", "", "### 自己做", "", "目标：做一件事。", ""]
    if mid:
        lines += [f"> **中途存档点**：备份做完，到这里可以安全停下。下次可以对导师说“做小关卡 {mid}”。", "",
                  "### 考试时段", "", "按工具说的做。", ""]
    lines += [validate.HINT_LINE.format(station=sid), validate.CHECK_LINE.format(station=sid), "",
              "> **想多了解（可跳过）：一个细节**", "> 可以不读。", "",
              validate.SAVE_LINE.format(station=sid, target=target), ""]
    return lines


def good_text(lesson_id="1.6", letters="abc", rules=("GIT-01", "GIT-02"), minutes=25,
              closing=5, mark=True, mid=None, end=None):
    """A lesson.md that follows every fixed form (V1-V12 find nothing)."""
    total = minutes * len(letters) + closing
    lines = [f"# {lesson_id} 示例课", "",
             f"> **用时** {len(letters)} 站，约 {total} 分钟 ｜ **前置** 无", "",
             "## 先想一想", "", "一个问题。", ""]
    for number, letter in enumerate(letters, 1):
        lines += station(lesson_id, letter, number, number == len(letters), minutes,
                         mark=mark and number == 1, mid=mid if number == len(letters) else None)
    if rules:
        lines += ["## 本课行规", "", "| " + " | ".join(validate.SUMMARY_COLUMNS) + " |",
                  "|---|---|---|---|---|---|"]
        for rule in rules:
            lines.append(f"| {rule} | {RULE_TITLES[rule]} | 必须（适用范围：本课程）；推荐（适用范围：所有项目） "
                         "| 惯例·平台与工具 | 示例出处 | 2026-11-19 |")
        lines += ["", validate.SUMMARY_SENTENCE, ""]
    lines += [f"## 收尾（约 {closing} 分钟）", "",
              "1. " + validate.CLOSING_CHECK.format(lesson=lesson_id)]
    number = 2
    if rules:
        lines.append(f"{number}. " + validate._notes_line(list(rules), cards_for(lesson_id, rules)))
        number += 1
    lines.append(f"{number}. " + validate.CLOSING_JOURNAL)
    number += 1
    key = helpers.syllabus.lesson_key
    if key(lesson_id) > key("1.12"):
        lines.append(f"{number}. " + validate.CLOSING_BACKUP)
    elif lesson_id == "1.12":
        lines += [f"{number}. 备份：把今天的记录提交并推送，这一组命令以后每次都做：", "",
                  "```bash", "git status", "git add .", 'git commit -m "docs: 记日志"', "git push",
                  "```"]
    lines += ["", end or validate.CLOSING_END.format(lesson="1.7"), "",
              "## 想多了解", "", "下面的都可以跳过。", ""]
    return "\n".join(lines)


def meta_for(lesson_id="1.6", letters="abc", rules=("GIT-01", "GIT-02"), minutes=25,
             unverified=("1.6a 设置页面",)):
    return {"id": lesson_id, "rules": list(rules), "unverified_steps": list(unverified),
            "stations": [{"id": lesson_id + letter, "minutes": minutes} for letter in letters]}


def forms(text, lesson_id="1.6", letters="abc", rules=("GIT-01", "GIT-02"), meta=None,
          cards=None):
    """The findings of ``check_lesson_forms`` as "CODE message" strings."""
    report = validate.Report(None)
    meta = meta or meta_for(lesson_id, letters, rules)
    ids = [s["id"] for s in meta["stations"]]
    validate.check_lesson_forms(report, validate.Doc(text), lesson_id, ids, meta,
                                cards if cards is not None else cards_for(lesson_id, rules))
    for finding in report.findings:
        assert finding.level == validate.WARNING, finding
    return [f"{f.code} {f.message}" for f in report.findings]


class FormsTestCase(unittest.TestCase):
    def assertOne(self, found, *parts):
        hits = [f for f in found if all(p in f for p in parts)]
        self.assertTrue(hits, f"no finding with {parts} in {found}")
        return hits[0]

    def assertNone(self, found, *parts):
        hits = [f for f in found if all(p in f for p in parts)]
        self.assertEqual(hits, [], found)


class GoodTextTest(FormsTestCase):
    def test_the_generated_lessons_follow_every_form(self):
        cases = [
            ("1.6", "abc", ("GIT-01", "GIT-02"), {}),
            ("1.3", "ab", (), {"end": validate.CLOSING_END.format(lesson="1.4")}),
            ("1.5", "ab", ("DOC-01", "DOC-02"), {"end": validate.CLOSING_END_GATE.format(gate="gate-a")}),
            ("1.12", "abc", ("REMOTE-01", "REMOTE-02"),
             {"closing": 10, "end": validate.CLOSING_END.format(lesson="1.13")}),
            ("1.13", "abc", ("PUB-01",), {"closing": 10, "end": validate.CLOSING_END.format(lesson="1.14")}),
            ("0.4", "abc", ("PM-01", "PM-02"), {"mid": "gate-0", "end": validate.CLOSING_END.format(lesson="1.1")}),
            ("1.16", "abc", ("PM-03",), {"closing": 10, "mid": "gate-1",
                                         "end": "阶段 1 到这里结束。下次可以对导师说“准备阶段 2”。"}),
        ]
        for lesson_id, letters, rules, options in cases:
            with self.subTest(lesson=lesson_id):
                text = good_text(lesson_id, letters, rules, **options)
                meta = meta_for(lesson_id, letters, rules, unverified=["一步"])
                self.assertEqual(forms(text, lesson_id, letters, rules, meta=meta), [])


class SavePointTest(FormsTestCase):
    """V1: the save-point line after every station."""

    def test_missing_line(self):
        text = good_text().replace(validate.SAVE_LINE.format(station="1.6b", target="从 1.6c 继续"), "")
        found = forms(text)
        self.assertOne(found, "I1", "第 2 站（1.6b", "末尾没有存档点", "下次可以对导师说“从 1.6c 继续”")

    def test_wrong_target_after_the_last_station(self):
        good = validate.SAVE_LINE.format(station="1.6c", target="从 1.6 的收尾继续")
        found = forms(good_text().replace(good, good.replace("从 1.6 的收尾继续", "从 1.7 开始")))
        self.assertOne(found, "I1", "说的话应该是“从 1.6 的收尾继续”，现在是“从 1.7 开始”")

    def test_ascii_quotes_and_missing_word(self):
        good = validate.SAVE_LINE.format(station="1.6a", target="从 1.6b 继续")
        bad = '> **存档点 1.6a**：到这里可以安全停下。下次对导师说"从 1.6b 继续"。'
        message = self.assertOne(forms(good_text().replace(good, bad)), "I1", "存档点写法不对")
        self.assertIn("英文的直引号", message)
        self.assertIn("少了「可以」", message)
        self.assertIn(good, message)

    def test_extra_text(self):
        good = validate.SAVE_LINE.format(station="1.6a", target="从 1.6b 继续")
        message = self.assertOne(forms(good_text().replace(good, good + "你的网站有了后悔药。")),
                                 "I1", "存档点写法不对")
        self.assertIn("句子后面多了「你的网站有了后悔药。」", message)
        bad = good.replace("下次可以", "你的网站有了后悔药。下次可以")
        self.assertIn("中间多了", self.assertOne(forms(good_text().replace(good, bad)), "存档点写法不对"))

    def test_mid_station_save_point_before_a_gate(self):
        text = good_text("0.4", rules=("PM-01", "PM-02"), mid="gate-0",
                         end=validate.CLOSING_END.format(lesson="1.1"))
        meta = meta_for("0.4", rules=("PM-01", "PM-02"))
        self.assertEqual(forms(text, "0.4", rules=("PM-01", "PM-02"), meta=meta), [])
        bad = text.replace("“做小关卡 gate-0”", '"从 0.4c 的小关卡继续"')
        message = self.assertOne(forms(bad, "0.4", rules=("PM-01", "PM-02"), meta=meta),
                                 "I1", "中途存档点写法不对")
        self.assertIn("说的话应该是“做小关卡 gate-0”", message)

    def test_save_point_lines_in_pasted_output_are_not_read(self):
        text = good_text().replace("```zsh\npwd\n```", "```text\n  存档点 1.6a：到这里可以安全停下。\n```", 1)
        self.assertEqual(forms(text), [])


class StationPartsTest(FormsTestCase):
    """V3: 概念, 跟我做, 补全, 自己做, and the last two lines of 自己做."""

    def test_missing_part(self):
        text = good_text().replace("### 补全", "### 练一练", 1)
        self.assertOne(forms(text), "I1", "第 1 站（1.6a）缺少「### 补全」")

    def test_wrong_order(self):
        text = good_text().replace("### 概念", "### 先放这里", 1).replace(
            "### 补全", "### 补全\n\n### 概念", 1)
        self.assertOne(forms(text), "I1", "几部分顺序是「跟我做、补全、概念、自己做」")

    def test_hint_and_check_in_another_form(self):
        old = validate.CHECK_LINE.format(station="1.6b")
        text = good_text().replace(old, "- 检查：`python3 tools/course.py check 1.6b`")
        message = self.assertOne(forms(text), "I1", "第 2 站（1.6b）的「自己做」要以这两行结尾")
        self.assertIn("- 检查：`python3 tools/course.py check 1.6b`", message)

    def test_a_box_after_the_check_line(self):
        old = validate.CHECK_LINE.format(station="1.6a")
        text = good_text().replace(old, old + "\n\n> **困在 vi 里了怎么办**：按 Esc。")
        self.assertOne(forms(text), "I1", "第 1 站（1.6a）的「自己做」要以这两行结尾", "困在 vi 里")

    def test_part_after_own_work_needs_a_mid_save_point(self):
        old = validate.HINT_LINE.format(station="1.6c")
        text = good_text().replace(old, "### 考试时段\n\n考试。\n\n" + old)
        self.assertOne(forms(text), "I1", "第 3 站（1.6c）在「自己做」后面还有「### 考试时段」")


class ClosingTest(FormsTestCase):
    """V2: the closing section."""

    def test_heading_without_about(self):
        text = good_text().replace("## 收尾（约 5 分钟）", "## 收尾（5 分钟）")
        self.assertOne(forms(text), "I1", "收尾标题要写成「## 收尾（约 5 分钟）」")

    def test_wrong_lesson_in_the_check(self):
        text = good_text().replace("course.py check 1.6`", "course.py check 1.5`")
        self.assertOne(forms(text), "I1", "收尾第 1 步写法不对", "检查的应该是 1.6，现在是 1.5")

    def test_notes_step_names_every_rule_with_its_title(self):
        text = good_text().replace("「GIT-02 提交前确认身份设置」", "")
        message = self.assertOne(forms(text), "I1", "收尾第 2 步写法不对", "没有写到 GIT-02")
        self.assertIn("「GIT-01 一个项目一个仓库」「GIT-02 提交前确认身份设置」下面各用自己的话", message)

    def test_no_notes_step_without_rules(self):
        text = good_text("1.3", "ab", (), end=validate.CLOSING_END.format(lesson="1.4")).replace(
            "2. " + validate.CLOSING_JOURNAL,
            "2. 打开 `notes/my-rules.md` 复习 TERM-01\n3. " + validate.CLOSING_JOURNAL)
        found = forms(text, "1.3", "ab", ())
        self.assertOne(found, "I1", "本课没有新规则，收尾不要「行规笔记」这一步")
        self.assertNone(found, "顺序不对")

    def test_order(self):
        text = good_text()
        notes = "2. " + validate._notes_line(["GIT-01", "GIT-02"], cards_for("1.6", ("GIT-01", "GIT-02")))
        journal = "3. " + validate.CLOSING_JOURNAL
        text = text.replace(notes, "@@").replace(journal, notes.replace("2.", "3.", 1)).replace(
            "@@", journal.replace("3.", "2.", 1))
        self.assertOne(forms(text), "I1", "收尾的步骤顺序不对")

    def test_backup_step_from_lesson_1_12_on(self):
        options = {"closing": 10, "end": validate.CLOSING_END.format(lesson="1.14")}
        text = good_text("1.13", rules=("PUB-01",), **options).replace(
            "4. " + validate.CLOSING_BACKUP, "")
        self.assertOne(forms(text, "1.13", rules=("PUB-01",)), "I1", "收尾里没有「备份」这一步")
        defining = good_text("1.12", rules=("REMOTE-01", "REMOTE-02"), closing=10,
                             end=validate.CLOSING_END.format(lesson="1.13")).replace("git push\n", "")
        self.assertOne(forms(defining, "1.12", rules=("REMOTE-01", "REMOTE-02")),
                       "I1", "备份这一步要写出那一组命令，最后要有 git push")

    def test_last_line(self):
        found = forms(good_text().replace(validate.CLOSING_END.format(lesson="1.7"),
                                          "下一课是 1.7，对导师说“开始上课”。"))
        self.assertOne(found, "I1", "收尾的最后一行要是「都做完，这一课就完成了。下次可以对导师说“从 1.7 开始”。」")
        gate = good_text("1.10", "ab", (), end=validate.CLOSING_END.format(lesson="1.11"))
        self.assertOne(forms(gate, "1.10", "ab", ()), "I1", "下次可以对导师说“做小关卡 gate-b”")
        stage = good_text("1.16", rules=("PM-03",), closing=10,
                          end=validate.CLOSING_END.format(lesson="2.1"))
        self.assertOne(forms(stage, "1.16", rules=("PM-03",)), "I1", "准备阶段 2")

    def test_closing_end_from_the_syllabus(self):
        entry = helpers.syllabus.lesson_entry
        self.assertEqual(validate._closing_end("0.4", entry("0.4"))[0], "lesson")
        self.assertEqual(validate._closing_end("1.5", entry("1.5"))[0], "gate")
        self.assertEqual(validate._closing_end("1.10", entry("1.10"))[0], "gate")
        self.assertEqual(validate._closing_end("1.16", entry("1.16")),
                         ("stage", "下次可以对导师说“准备阶段 2”。"))
        self.assertIsNone(validate._closing_end("99.1", None))


class MarksTest(FormsTestCase):
    """V4: the marks of plan G6 and the line that follows them."""

    def test_line_missing(self):
        text = good_text().replace(validate.G6_LINE + "\n", "", 1)
        self.assertOne(forms(text), "G6", "却没有这一行")

    def test_line_twice_before_the_mark_and_in_a_quote(self):
        text = good_text().replace("## 先想一想", validate.G6_LINE + "\n\n## 先想一想")
        self.assertOne(forms(text), "G6", "现在出现了 2 次")
        text = good_text().replace(validate.G6_LINE, "> " + validate.G6_LINE.replace("“课文对不上”", '"课文对不上"'))
        message = self.assertOne(forms(text), "G6", "不放在引用框（>）里")
        self.assertIn("一字不差", message)

    def test_mark_in_backticks_and_in_code(self):
        text = good_text().replace("页面〔对照文档，界面可能不同〕", "页面`〔对照文档，界面可能不同〕`")
        self.assertOne(forms(text), "G6", "写在了反引号里")
        text = good_text().replace("```zsh\npwd\n```", "```zsh\npwd 〔建课时无法验证〕\n```", 1)
        self.assertOne(forms(text), "G6", "写在了代码块里")

    def test_unverified_steps_agree_with_the_marks(self):
        self.assertOne(forms(good_text(), meta=meta_for(unverified=())), "G6", "unverified_steps'] 却是空的")
        text = good_text(mark=False)
        self.assertOne(forms(text), "G6", "课文里却没有标记")
        self.assertEqual(forms(text, meta=meta_for(unverified=())), [])


class TutorSentenceTest(FormsTestCase):
    """V5: sentences to the tutor and straight quotes around Chinese."""

    def test_forms_that_are_not_fixed_sentences(self):
        for sentence, advice in (("从本课行规继续", "固定的说法"), ("从 1.10 收尾继续", "收尾继续"),
                                 ("从收尾继续", "的收尾继续"), ("急救", "急救：<一句话说现象>"),
                                 ("继续下一阶段", "准备阶段 2"), ("讲给导师听", "讲解题"),
                                 ("回到上课，我来验收 1.15a", "回到上课")):
            with self.subTest(sentence=sentence):
                text = good_text().replace("一个新概念。", f"卡住了就对导师说“{sentence}”。", 1)
                self.assertOne(forms(text), "G2", f"对导师说“{sentence}”", advice)

    def test_fixed_sentences_and_other_quotes_stay_silent(self):
        for sentence in ("从 1.6b 继续", "急救：code 命令找不到", "开始上课", "准备阶段 2",
                         "请问我 gate-0 的讲解题", "我回来了，带我走回归流程"):
            with self.subTest(sentence=sentence):
                text = good_text().replace("一个新概念。", f"对导师说“{sentence}”。", 1)
                self.assertEqual(forms(text), [])
        text = good_text().replace("一个新概念。", "Git 说“用 git add 开始跟踪”。", 1)
        self.assertEqual(forms(text), [])

    def test_straight_quotes_around_chinese(self):
        text = good_text().replace("一个新概念。", '这叫"快照"，`git commit -m "第一次"` 不算。', 1)
        found = forms(text)
        self.assertOne(found, "G2", '英文直引号', '"快照"')
        self.assertEqual(len([f for f in found if "直引号" in f]), 1)
        quiet = good_text().replace("一个新概念。", '`"x"` 和 "`a`" 文件夹 "README"', 1)
        self.assertEqual(forms(quiet), [])


class CourseFolderTest(FormsTestCase):
    """V6: the names and paths of the course folder."""

    def test_paths(self):
        text = good_text().replace("一个新概念。", "cd ~/Desktop/Code/fullstack-from-zero，再看 /Users/laowang/a。", 1)
        found = forms(text)
        self.assertOne(found, "G10", "Desktop/Code/fullstack-from-zero")
        self.assertOne(found, "G10", "/Users/laowang")
        old = good_text().replace("一个新概念。", "cd ~/Developer/" + "Engineering，或者读《Software Engineering at Google》。", 1)
        self.assertOne(forms(old), "G10", "旧的文件夹名")
        quiet = good_text().replace("一个新概念。", "pwd 显示 /Users/你的用户名/Developer 和 /Users/…/x", 1)
        self.assertEqual(forms(quiet), [])
        lesson_02 = good_text("0.2", rules=(), end=validate.CLOSING_END.format(lesson="0.3")).replace(
            "一个新概念。", "旧位置 ~/Desktop/Code/fullstack-from-zero", 1)
        self.assertEqual(forms(lesson_02, "0.2", rules=(), meta=meta_for("0.2", rules=())), [])

    def test_names(self):
        text = good_text().replace("一个新概念。", "回到课程文件夹。做完回到工作区检查。", 1)
        found = forms(text)
        self.assertOne(found, "G10", "「课程文件夹」")
        self.assertOne(found, "G10", "「回到工作区」")
        early = good_text("1.3", "ab", (), end=validate.CLOSING_END.format(lesson="1.4")).replace(
            "一个新概念。", "做完回到工作区检查。工作区（working tree）。", 1)
        self.assertEqual(forms(early, "1.3", "ab", ()), [])
        git_sense = good_text().replace("一个新概念。", "改动还在工作区里，学习工作区 ~/Developer/fullstack-from-zero。", 1)
        self.assertEqual(forms(git_sense), [])


class OptionalLabelTest(FormsTestCase):
    """V7: optional material carries one label."""

    def test_other_labels(self):
        for label in ("> **选做：用 SSH 签名**", "> **想多了解（可以跳过）**", "> **想多了解**（选读）",
                      "> **旧教程提醒**（选读，可以跳过）：……", "### 选读：更多"):
            with self.subTest(label=label):
                text = good_text().replace("一个新概念。", "一个新概念。\n\n" + label + "\n", 1)
                self.assertOne(forms(text), "I1", "想多了解（可跳过）")

    def test_the_fixed_label_is_fine(self):
        text = good_text().replace("一个新概念。", "一个新概念。\n\n> **想多了解（可跳过）：细节**\n> 内容\n", 1)
        self.assertEqual(forms(text), [])


class RuleSummaryTest(FormsTestCase):
    """V8: the table of 本课行规 against the cards."""

    def test_cells_must_be_copied_from_the_card(self):
        text = good_text().replace("| GIT-02 | 提交前确认身份设置 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） ",
                                   "| GIT-02 | 提交前确认身份设置 | 必须（所有项目） ")
        message = self.assertOne(forms(text), "I2", "GIT-02 的「约束力」和 rules.md 的卡片不一样")
        self.assertIn("表里是「必须（所有项目）」", message)
        self.assertIn("卡片上是「必须（适用范围：本课程）；推荐（适用范围：所有项目）」", message)

    def test_white_space_and_punctuation_do_not_count(self):
        text = good_text().replace("必须（适用范围：本课程）；推荐（适用范围：所有项目） | 惯例·平台与工具",
                                   "必须(适用范围: 本课程); 推荐(适用范围:所有项目) | 惯例・平台与工具")
        self.assertEqual(forms(text), [])

    def test_table_header_sentence_and_rows(self):
        text = good_text().replace("| 编号 | 规则 |", "| 编号 | 行规 |").replace(
            validate.SUMMARY_SENTENCE, "完整卡片在 [rules.md](rules.md)。")
        found = forms(text)
        self.assertOne(found, "I2", "表头要是")
        self.assertOne(found, "I2", "完整卡片在 [rules.md](rules.md)。")
        no_table = re.sub(r"\n\|.*", "", good_text())
        self.assertOne(forms(no_table), "I2", "没有表格")
        missing_row = re.sub(r"\n\| GIT-01 .*", "", good_text())
        self.assertOne(forms(missing_row), "I2", "没有 GIT-01 这一行")


class OldTutorialTest(FormsTestCase):
    """V9: every 旧教程提醒 says since when."""

    def test_box_without_since_when(self):
        box = "> **旧教程提醒**：以前写 A；现在写 B（GitHub Docs，2026-11-19 核对，见第 1.12 课）。"
        text = good_text().replace("一个新概念。", "一个新概念。\n\n" + box + "\n", 1)
        self.assertOne(forms(text), "G4", "旧教程提醒没写从什么时候起")
        for since in ("（自 Git 2.23 起）", "（2020 年起）", "（自 2021-08-13 起）"):
            with self.subTest(since=since):
                quiet = good_text().replace("一个新概念。", "一个新概念。\n\n" + box.replace("。", since + "。") + "\n", 1)
                self.assertEqual(forms(quiet), [])


class GitConfigTest(FormsTestCase):
    """V10: git config without a subcommand."""

    def test_old_forms(self):
        for command in ("git config --global user.name 小林", "git config --get user.email",
                        "git config --global --unset gpg.ssh.program", "git config user.name"):
            with self.subTest(command=command):
                text = good_text().replace("```zsh\npwd\n```", f"```zsh\n{command}\n```", 1)
                self.assertOne(forms(text), "G4", "git config 的旧写法")
                inline = good_text().replace("一个新概念。", f"运行 `{command}`。", 1)
                self.assertOne(forms(inline), "G4", "git config 的旧写法")

    def test_new_forms_old_tutorial_box_and_git_output(self):
        for command in ("git config set --global user.name 小林", "git config get user.email",
                        "git config unset --global gpg.ssh.program", "git config list", "git config -h"):
            with self.subTest(command=command):
                text = good_text().replace("```zsh\npwd\n```", f"```zsh\n{command}\n```", 1)
                self.assertEqual(forms(text), [])
        box = ("> **旧教程提醒**：以前写 `git config --global user.name …`；"
               "现在写 `git config set --global user.name …`（自 Git 2.46 起）。")
        self.assertEqual(forms(good_text().replace("一个新概念。", "一个新概念。\n\n" + box + "\n", 1)), [])
        output = ("```text\n*** Please tell me who you are.\n\nRun\n\n"
                  '  git config --global user.email "you@example.com"\n```')
        self.assertEqual(forms(good_text().replace("```zsh\npwd\n```", output, 1)), [])


class HeaderTest(FormsTestCase):
    """V12: 「**用时** N 站，约 X 分钟」."""

    def test_sum_of_stations_and_closing(self):
        text = good_text().replace("约 80 分钟", "约 75 分钟")
        self.assertOne(forms(text), "G5", "写的是约 75 分钟；各站加收尾是 80 分钟（25 + 25 + 25 + 收尾 5）")
        text = good_text().replace("3 站，", "2 站，")
        self.assertOne(forms(text), "G5", "写的是 2 站，META 里有 3 站")
        text = good_text().replace("> **用时** 3 站，约 80 分钟", "> **用时** 三站，八十分钟")
        self.assertOne(forms(text), "G5", "用时写法要是")

    def test_closing_heading_without_about_still_counts(self):
        text = good_text().replace("## 收尾（约 5 分钟）", "## 收尾（5 分钟）").replace("约 80 分钟", "约 75 分钟")
        self.assertOne(forms(text), "G5", "各站加收尾是 80 分钟")

    def test_extra_words_after_the_sum_are_fine(self):
        text = good_text().replace("约 80 分钟", "约 80 分钟（搬家再加约 10 分钟）")
        self.assertEqual(forms(text), [])


class CardBindingTest(unittest.TestCase):
    """V8 on the card: every level word has a scope."""

    def card(self, binding):
        text = CARD.format(rule="GIT-01", title="一", lesson="1.6").replace(
            "必须（适用范围：本课程）；推荐（适用范围：所有项目）", binding)
        return rulecards.parse_cards(text)[0]

    def test_every_level_word_has_a_scope(self):
        self.assertEqual(rulecards.binding_problems(self.card("必须（适用范围：本课程）；推荐（适用范围：所有项目）")), [])
        self.assertEqual(rulecards.binding_problems(self.card("推荐（适用范围：本课程、所有项目）")), [])
        found = rulecards.binding_problems(self.card("推荐（适用范围：所有项目），本课程里按必须对待"))
        self.assertEqual(len(found), 1, found)
        self.assertIn("「必须」后面没有", found[0])
        found = rulecards.binding_problems(self.card("必须（适用范围：本课程）；推荐（适用范围：别的地方）"))
        self.assertIn("别的地方", found[0])

    def test_cards_the_strict_check_already_rejects_are_left_to_it(self):
        self.assertEqual(rulecards.binding_problems(self.card("一定要做")), [])
        self.assertEqual(rulecards.binding_problems(self.card("必须")), [])


# ---------------------------------------------------------------------------
# The whole command in a sandbox
# ---------------------------------------------------------------------------
MODULE_TEXTS = '''
HINTS["1.6a"][2] = "相似的例子：git config --global commit.gpgsign false。"
def _say(ctx):
    ctx.ok("做完了，下次对导师说“从本课行规继续”。")
    ctx.note("回到课程文件夹 ~/Desktop/Code/fullstack-from-zero 再试。")
checks["1.6b"] = _say
'''


class CommandTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def run_json(self, *args):
        result = self.box.run("validate", "--json", *args, noninteractive=True)
        return result.code, json.loads(result.out)

    def warnings(self, data, lesson_id):
        for lesson in data["lessons"]:
            if lesson["id"] == lesson_id:
                return [f["code"] + " " + f["message"] for f in lesson["warnings"]]
        raise AssertionError(data)

    def test_lesson_py_texts_and_hints(self):
        source = helpers.lesson_source("1.6", "06-first-commit", title="Git：第一次提交", letters="abc",
                                       rules=["GIT-01", "GIT-02"])
        source = source.replace('    "1.6a": ["方向 1.6a", "位置 1.6a", "相似例子 1.6a",',
                                '    "1.6a": ["方向 1.6a", "位置 1.6a", "相似：git config --global a.b c",')
        self.assertIn("git config --global a.b c", source)
        cards = "\n".join(helpers.RULE_CARD.format(rule=r, lesson="1.6", level="必须", kind="惯例·平台与工具")
                          for r in ("GIT-01", "GIT-02"))
        self.box.add_lesson(source + MODULE_TEXTS, "01-foundations", "06-first-commit", rules_text=cards)
        code, data = self.run_json()
        self.assertEqual(code, 0)
        found = "\n".join(self.warnings(data, "1.6"))
        self.assertIn("HINTS['1.6a'] 的第 3 级提示（lesson.py 的第", found)
        self.assertIn("叫学习者对导师说“从本课行规继续”", found)
        self.assertIn("「课程文件夹」", found)
        self.assertIn("lesson.py 的第", found)
        self.assertIn("Desktop/Code/fullstack-from-zero", found)

    def test_card_warnings(self):
        source = helpers.lesson_source("1.7", "07-read-diff", title="Git：看懂改了什么", rules=["GIT-03"])
        card = helpers.RULE_CARD.format(rule="GIT-03", lesson="1.7", level="推荐", kind="惯例·平台与工具")
        card = card.replace("推荐（适用范围：所有项目）", "推荐（适用范围：所有项目），本课程里按必须对待").replace(
            "- **旧教程提醒**：无", "- **旧教程提醒**：以前写 A，现在写 B。")
        self.box.add_lesson(source, "01-foundations", "07-read-diff", rules_text=card)
        code, data = self.run_json()
        self.assertEqual(code, 0)
        found = "\n".join(self.warnings(data, "1.7"))
        self.assertIn("I2 规则卡 GIT-03（rules.md 第 1 行）：约束力里的每一个", found)
        self.assertIn("G4 规则卡 GIT-03（rules.md 第 1 行）的旧教程提醒没写从什么时候起", found)

    def add(self, lesson_id, letters, terms="", commands=None):
        entry = helpers.syllabus.lesson_entry(lesson_id)
        source = helpers.lesson_source(lesson_id, entry["folder"], title=entry["title"], letters=letters,
                                       rules=sorted(entry["rules"]))
        source = re.sub(r"(?m)^TERMS = .*$", lambda _m: "TERMS = " + (terms or "[]"), source)
        for station_id, command in (commands or {}).items():
            source = source.replace(f'"new_commands": ["cmd-{station_id}"]', f'"new_commands": [{command!r}]')
        cards = "\n".join(helpers.RULE_CARD.format(rule=r, lesson=lesson_id, level="必须",
                                                   kind="惯例·平台与工具") for r in sorted(entry["rules"]))
        self.box.add_lesson(source, entry["stage_folder"], entry["folder"],
                            rules_text=cards if entry["rules"] else None)

    def test_owners_and_english_glosses(self):
        self.add("1.3", "ab", terms='[{"term": "模式", "en": "pattern", "plain": "名字的样子", "first": "1.3b"},'
                                    ' {"term": "递归", "en": "recursive", "plain": "一层层", "first": "1.3a"}]',
                 commands={"1.3a": "git --version"})
        self.add("1.9", "ab", terms='[{"term": "匹配模式", "en": "pattern", "plain": "x", "first": "1.9a"},'
                                    ' {"term": "PATH", "en": "PATH", "plain": "y", "first": "1.9b"},'
                                    ' {"term": "路径", "en": "path", "plain": "z", "first": "1.9b"}]',
                 commands={"1.9a": "git commit -m ... -m ..."})
        self.add("1.10", "ab", commands={"1.10b": "git commit -m … -m …"})
        _code, data = self.run_json()
        general = [f["message"] for f in data["general"]]
        joined = "\n".join(general)
        self.assertIn("英文原词 'pattern' 下面有 2 个不同的术语：1.3 课的「模式」、1.9 课的「匹配模式」", joined)
        self.assertNotIn("'path'", joined)
        self.assertNotIn("'PATH'", joined)
        self.assertIn("术语「递归」 归 1.2 课（课程约定的归属），1.3 课的 TERMS 不要把它算成第一次出现", joined)
        self.assertIn("命令 'git --version' 归 1.6 课", joined)
        self.assertIn("命令 'git commit -m ... -m ...' 归 1.10 课（课程约定的归属），1.9 课的 new_commands", joined)

    def test_owner_first_then_another_lesson(self):
        self.add("1.6", "abc", commands={"1.6a": "git --version"})
        self.add("1.14", "abc", commands={"1.14b": "git --version"})
        self.add("1.16", "abc", commands={"1.16b": "python3 tools/course.py exam gate-1"})
        self.add("0.4", "abc", commands={"0.4c": "python3 tools/course.py exam gate-0"})
        _code, data = self.run_json()
        joined = "\n".join(f["message"] for f in data["general"])
        self.assertIn("命令 'git --version' 在 1.6 和 1.14 两课里都算成了新命令；按约定它归 1.6 课："
                      "1.14 课的 new_commands 去掉这一项", joined)
        self.assertIn("在 0.4 和 1.16 两课里都算成了新命令（不同关卡的 exam 算同一条命令）；按约定它归 0.4 课", joined)

    def test_the_owner_alone_is_silent(self):
        self.add("1.10", "ab", commands={"1.10b": "git commit -m … -m …"})
        self.add("1.2", "ab", terms='[{"term": "递归", "en": "recursive", "plain": "一层层", "first": "1.2a"}]')
        _code, data = self.run_json()
        self.assertEqual([f for f in data["general"] if f["code"] == "X"], [])


class RealLessonsTest(unittest.TestCase):
    """The three lessons named in the task, as they are today: no crash, only warnings."""

    def test_lessons_0_2_1_6_1_12(self):
        from pathlib import Path

        from courselib.catalog import load_lesson
        for lesson_id, folder in (("0.2", "00-orientation/02-files-and-paths"),
                                  ("1.6", "01-foundations/06-first-commit"),
                                  ("1.12", "01-foundations/12-push-and-backup")):
            with self.subTest(lesson=lesson_id):
                path = helpers.REPO / "stages" / folder / "lesson.py"
                if not path.is_file():
                    self.skipTest(f"{path} is missing")
                lesson = load_lesson(Path(path), helpers.REPO)
                report = validate.Report(lesson)
                validate._check_text(report, lesson, [s["id"] for s in lesson.meta["stations"]], False)
                for finding in report.findings:
                    self.assertEqual(finding.level, validate.WARNING, finding)
                    self.assertTrue(finding.message.strip())


if __name__ == "__main__":
    unittest.main()
