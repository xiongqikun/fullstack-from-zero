"""Rule cards (plan I2) and the two label axes of plan G3."""

import datetime
import unittest

import helpers
from courselib import rulecards

TODAY = datetime.date(2026, 11, 19)

GOOD = """# 本课行规

### GIT-03 提交前先看改了什么

- **约束力**：必须（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：提交前先运行 git diff --staged。
- **谁说的**：Pro Git 第 2 版 2.2 节 https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库
- **核对日期**：2026-11-19；**复核周期**：12 个月
- **谁来管**：评审人；**不遵守的后果**：把不想要的改动带进历史。
- **为什么**：提交以后再拆开很麻烦。
- **正例**：

      git diff --staged
      git commit -m "docs: 改标题"

- **反例**：不看就提交。
- **怎么检查**：复习题 1.7-r2
- **例外**：无
- **旧教程提醒**：无
- **学于**：1.7

## 别的章节
这里不属于任何卡片。
"""


def card_text(**changes):
    """GOOD with some field lines replaced (value None drops the line)."""
    lines = []
    for line in GOOD.splitlines():
        for name, value in changes.items():
            if line.startswith(f"- **{name}**："):
                line = None if value is None else f"- **{name}**：{value}"
                break
        if line is not None:
            lines.append(line)
    return "\n".join(lines) + "\n"


def problems(text, lesson="1.7"):
    cards = rulecards.parse_cards(text)
    return rulecards.check_card(cards[0], lesson, TODAY)


class ParseTest(unittest.TestCase):
    def test_fields_and_second_labels(self):
        cards = rulecards.parse_cards(GOOD)
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual((card.id, card.title, card.line), ("GIT-03", "提交前先看改了什么", 3))
        self.assertEqual(set(card.fields), set(rulecards.ALL_FIELDS))
        self.assertEqual(card.get("核对日期"), "2026-11-19")
        self.assertEqual(card.get("复核周期"), "12 个月")
        self.assertEqual(card.get("谁来管"), "评审人")
        self.assertEqual(card.get("不遵守的后果"), "把不想要的改动带进历史。")
        self.assertIn('git commit -m "docs: 改标题"', card.get("正例"))
        self.assertEqual(card.get("学于"), "1.7")
        self.assertNotIn("别的章节", card.get("学于"))
        self.assertEqual((card.level, card.scopes, card.kind), ("必须", ["所有项目"], "惯例·平台与工具"))

    def test_two_cards_and_text_between(self):
        second = GOOD.replace("GIT-03 提交前先看改了什么", "GIT-04 动手前先看状态")
        cards = rulecards.parse_cards(GOOD + "\n" + second)
        self.assertEqual([card.id for card in cards], ["GIT-03", "GIT-04"])
        self.assertTrue(all(len(card.fields) == 15 for card in cards))

    def test_type_label_drops_a_remark(self):
        self.assertEqual(rulecards.type_label("惯例·事实标准（EditorConfig）"), "惯例·事实标准")
        self.assertEqual(rulecards.type_label(" 行业要求 (平台强制) "), "行业要求")

    def test_scopes(self):
        card = rulecards.parse_cards(card_text(约束力="推荐（适用范围：本机、所有项目）；团队里是必须"))[0]
        self.assertEqual((card.level, card.scopes), ("推荐", ["本机", "所有项目"]))


class CheckTest(unittest.TestCase):
    def test_a_complete_card_has_no_problems(self):
        self.assertEqual(problems(GOOD), [])

    def test_example_lesson_card_is_complete(self):
        text = (helpers.EXAMPLE / "rules.md").read_text(encoding="utf-8")
        cards = rulecards.parse_cards(text)
        self.assertEqual([card.id for card in cards], ["EX-01"])
        self.assertEqual(rulecards.check_card(cards[0], "99.1", TODAY), [])

    def test_every_field_is_mandatory(self):
        for name in rulecards.FIELDS:
            with self.subTest(field=name):
                found = problems(card_text(**{name: None}))
                self.assertTrue(any(f"缺少「{name}」" in p for p in found), found)

    def test_second_labels_are_mandatory(self):
        found = problems(card_text(核对日期="2026-11-19", 谁来管="评审人"))
        self.assertTrue(any("缺少「复核周期」" in p for p in found), found)
        self.assertTrue(any("缺少「不遵守的后果」" in p for p in found), found)

    def test_old_four_label_format_is_rejected(self):
        old = ("### GIT-03 提交前先看改了什么\n"
               "- **级别**：必须 ｜ **类型**：惯例 ｜ **出处**：Pro Git（https://git-scm.com）"
               "｜ **核实**：2026-11-19\n- **规则**：……\n- **学于**：1.7\n")
        found = problems(old)
        self.assertTrue(any("缺少「约束力」" in p for p in found))
        self.assertTrue(any("缺少「规则类型」" in p for p in found))

    def test_labels_without_bold_marks(self):
        plain = GOOD.replace("**", "")
        found = problems(plain)
        self.assertEqual(len(found), 1)
        self.assertIn("没有加粗", found[0])

    def test_binding_level_and_scope(self):
        self.assertTrue(any("约束力要以" in p for p in problems(card_text(约束力="强制（适用范围：所有项目）"))))
        self.assertTrue(any("适用范围" in p for p in problems(card_text(约束力="必须"))))
        found = problems(card_text(约束力="必须（适用范围：你的 GitHub 账号）"))
        self.assertTrue(any("适用范围要是" in p for p in found), found)
        self.assertEqual(problems(card_text(约束力="参考（适用范围：本课程）")), [])

    def test_rule_type_is_exactly_one_label(self):
        for kind in rulecards.TYPES:
            with self.subTest(kind=kind):
                text = card_text(规则类型=kind)
                found = [p for p in problems(text) if "规则类型" in p]
                self.assertEqual(found, [])
        self.assertEqual(problems(card_text(规则类型="惯例·事实标准（EditorConfig）")), [])
        for bad in ("惯例", "规范", "课程约定", "标准、行业要求", "惯例·事实标准 / 惯例·平台与工具"):
            with self.subTest(bad=bad):
                self.assertTrue(any("规则类型要正好是" in p for p in problems(card_text(规则类型=bad))))
        self.assertTrue(any("个人偏好不是规则" in p for p in problems(card_text(规则类型="个人偏好"))))
        self.assertTrue(any("间隔号" in p for p in problems(card_text(规则类型="惯例・平台与工具"))))

    def test_source_needs_a_url_unless_the_course_or_team_decided_it(self):
        no_url = "Pro Git 第 2 版 2.2 节"
        self.assertTrue(any("网址" in p for p in problems(card_text(谁说的=no_url))))
        local = card_text(谁说的="本课程约定（2026-11-19）", 规则类型="规范·本课程约定")
        self.assertEqual(problems(local), [])
        self.assertTrue(any("占位" in p for p in problems(card_text(谁说的="待补"))))

    def test_check_date(self):
        self.assertTrue(any("YYYY-MM-DD" in p for p in problems(card_text(核对日期="11 月 19 日；**复核周期**：12 个月"))))
        self.assertTrue(any("YYYY-MM-DD" in p for p in problems(card_text(核对日期="2026-13-40；**复核周期**：12 个月"))))
        self.assertTrue(any("今天之后" in p for p in problems(card_text(核对日期="2027-01-01；**复核周期**：12 个月"))))

    def test_learned_in_names_this_lesson(self):
        self.assertEqual(problems(GOOD, lesson="1.7"), [])
        self.assertEqual(problems(card_text(学于="1.7b"), lesson="1.7"), [])
        self.assertTrue(any("学于" in p for p in problems(GOOD, lesson="1.1")))
        self.assertTrue(any("学于" in p for p in problems(card_text(学于="1.70"), lesson="1.7")))

    def test_heading_needs_a_title_and_a_good_id(self):
        found = problems(GOOD.replace("### GIT-03 提交前先看改了什么", "### GIT-3"))
        self.assertTrue(any("编号写法不对" in p for p in found))
        self.assertTrue(any("没有规则名" in p for p in found))

    def test_families_of_plan_section_4(self):
        self.assertTrue(rulecards.family_allows("惯例", "惯例·事实标准"))
        self.assertTrue(rulecards.family_allows("惯例", "惯例·平台与工具"))
        self.assertFalse(rulecards.family_allows("惯例", "规范·组织"))
        self.assertTrue(rulecards.family_allows("行业要求", "行业要求"))
        self.assertFalse(rulecards.family_allows("惯例·事实标准", "惯例·平台与工具"))
        self.assertTrue(rulecards.family_allows("规范·本课程约定", "规范·本课程约定"))


if __name__ == "__main__":
    unittest.main()
