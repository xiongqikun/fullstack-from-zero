"""E5: the syllabus table (plan section 4, COMMON section 7)."""

import unittest

import helpers  # noqa: F401 - puts tools/ on sys.path

from courselib import rulecards, syllabus


class SyllabusTest(unittest.TestCase):
    def test_lesson_1_4_has_three_stations(self):
        self.assertEqual(syllabus.lesson_entry("1.4")["stations"], ["1.4a", "1.4b", "1.4c"])
        stage_1 = [entry for entry in syllabus.LESSONS if entry["stage"] == 1]
        self.assertEqual(sum(len(entry["stations"]) for entry in stage_1), 40)

    def test_the_labels_accepted_after_the_audit_give_no_warning(self):
        accepted = {"WS-02": "规范·组织", "DOC-02": "规范·本课程约定", "REPO-01": "惯例·事实标准",
                    "HELP-01": "惯例·平台与工具", "AI-01": "规范·组织"}
        families = {rule: labels.get("kind") for entry in syllabus.LESSONS
                    for rule, labels in entry["rules"].items()}
        for rule, label in accepted.items():
            with self.subTest(rule=rule):
                self.assertIn(label, rulecards.TYPES)
                # the comparison validate makes for its [§4] warning
                self.assertTrue(rulecards.family_allows(families[rule], label))
        # REPO-01 is no longer listed as 行业要求, nor WS-02 / DOC-02 as plain 惯例
        self.assertFalse(rulecards.family_allows(families["REPO-01"], "行业要求"))
        self.assertFalse(rulecards.family_allows(families["WS-02"], "惯例·平台与工具"))
        self.assertFalse(rulecards.family_allows(families["DOC-02"], "惯例·平台与工具"))


if __name__ == "__main__":
    unittest.main()
