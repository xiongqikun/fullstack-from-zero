"""The ``validate`` command: plan I3 interface, G5 budgets, I2 rule cards, section 4."""

import json
import unittest

import helpers


class ValidateTestCase(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def validate(self, *args):
        result = self.box.run("validate", "--json", *args, noninteractive=True)
        data = json.loads(result.out)
        return result.code, data

    def findings(self, data, lesson_id):
        for lesson in data["lessons"]:
            if lesson["id"] == lesson_id:
                return ([f["code"] + " " + f["message"] for f in lesson["errors"]],
                        [f["code"] + " " + f["message"] for f in lesson["warnings"]])
        raise AssertionError(f"no report for {lesson_id}: {data}")

    def errors(self, lesson_id="1.6", *args):
        code, data = self.validate(*args)
        return code, self.findings(data, lesson_id)[0]

    def edit(self, lesson_id, old, new, name="lesson.py"):
        entry = helpers.syllabus.lesson_entry(lesson_id)
        path = self.box.root / "stages" / entry["stage_folder"] / entry["folder"] / name
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def assertFinding(self, errors, *parts):
        for error in errors:
            if all(part in error for part in parts):
                return
        self.fail(f"no finding with {parts} in {errors}")


class GoodLessonsTest(ValidateTestCase):
    def test_a_valid_syllabus_lesson_passes(self):
        self.box.add_syllabus_lesson("1.6")
        code, data = self.validate()
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ok"])
        self.assertEqual(self.findings(data, "1.6")[0], [])

    def test_human_readable_output(self):
        self.box.add_syllabus_lesson("1.7")
        result = self.box.run("validate", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("课程自检 · 1 课", result.out)
        self.assertIn("✅ 1.7 Git：看懂改了什么（stages/01-foundations/07-read-diff）", result.out)
        self.assertIn("合计：1 课，1 课通过，0 课没通过；错误 0 条", result.out)

    def test_the_worked_example_passes_with_trial_builds(self):
        self.box.add_example()
        result = self.box.run("validate", "--build", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("✅ 99.1 示例课", result.out)
        self.assertIn("错误 0 条", result.out)
        self.assertFalse(self.box.playground.exists(), "trial builds must not touch the playground")
        self.assertFalse((self.box.root / "learner").exists(), "validate keeps no learner state")

    def test_selecting_lessons_by_id_or_folder(self):
        self.box.add_syllabus_lesson("1.6")
        folder = self.box.add_syllabus_lesson("1.7")
        code, data = self.validate("1.7")
        self.assertEqual([lesson["id"] for lesson in data["lessons"]], ["1.7"])
        code, data = self.validate(str(folder))
        self.assertEqual([lesson["id"] for lesson in data["lessons"]], ["1.7"])
        result = self.box.run("validate", "9.9", noninteractive=True)
        self.assertEqual(result.code, 64)

    def test_no_lessons(self):
        result = self.box.run("validate", noninteractive=True)
        self.assertEqual(result.code, 1)
        self.assertIn("没有找到任何课程模块", result.out)


class BudgetTest(ValidateTestCase):
    """Plan G5: a lesson module that breaks a budget is rejected."""

    def setUp(self):
        ValidateTestCase.setUp(self)
        self.box.add_syllabus_lesson("1.6")

    def test_station_minutes(self):
        self.edit("1.6", '"minutes": 20', '"minutes": 41')
        code, errors = self.errors()
        self.assertEqual(code, 1)
        self.assertFinding(errors, "G5", "1.6a", "41 分钟")

    def test_station_minutes_boundaries(self):
        # Plan G5a: 15 and 40 are allowed, 14 and 41 are not (mutation M11).
        for minutes, allowed in ((14, False), (15, True), (20, True), (40, True), (41, False)):
            with self.subTest(minutes=minutes):
                self.box = helpers.Sandbox(self)
                self.box.add_syllabus_lesson("1.6", minutes=minutes)
                _code, errors = self.errors()
                found = [e for e in errors if e.startswith("G5") and "分钟" in e]
                self.assertEqual(bool(found), not allowed, errors)

    def test_too_many_new_commands(self):
        self.edit("1.6", '"new_commands": ["cmd-1.6a"]',
                  '"new_commands": ["a", "b", "c", "d", "e", "f"]')
        code, errors = self.errors()
        self.assertEqual(code, 1)
        self.assertFinding(errors, "G5", "6 条新命令")

    def test_a_command_counted_twice(self):
        self.edit("1.6", '"new_commands": ["cmd-1.6b"]', '"new_commands": ["cmd-1.6a"]')
        self.assertFinding(self.errors()[1], "G5", "cmd-1.6a")

    def test_new_concept_must_be_one_string(self):
        self.edit("1.6", '"new_concept": "概念 1.6a"', '"new_concept": ["概念一", "概念二"]')
        self.assertFinding(self.errors()[1], "G5", "new_concept")

    def test_too_many_stations(self):
        box = self.box
        source = helpers.lesson_source("1.7", "07-read-diff", title="Git：看懂改了什么",
                                       letters="abcd", rules=["GIT-03"])
        box.add_lesson(source, "01-foundations", "07-read-diff",
                       rules_text=helpers.RULE_CARD.format(rule="GIT-03", lesson="1.7",
                                                           level="必须", kind="惯例·平台与工具"))
        code, errors = self.errors("1.7")
        self.assertEqual(code, 1)
        self.assertFinding(errors, "G5", "4 站")

    def test_one_station_is_too_few(self):
        source = helpers.lesson_source("99.1", "01-one", letters="a")
        self.box.add_lesson(source, "99-extra", "01-one")
        self.assertFinding(self.errors("99.1")[1], "G5", "1 站")

    def test_too_many_rule_cards(self):
        source = helpers.lesson_source("99.1", "01-rules", rules=["EX-01", "EX-02", "EX-03"])
        cards = "\n".join(helpers.RULE_CARD.format(rule=r, lesson="99.1", level="推荐",
                                                   kind="规范·本课程约定")
                          for r in ("EX-01", "EX-02", "EX-03"))
        self.box.add_lesson(source, "99-extra", "01-rules", rules_text=cards)
        errors = self.errors("99.1")[1]
        self.assertFinding(errors, "G5", "最多 2 张新规则卡")
        self.assertFinding(errors, "G5", "rules.md 里有 3 张规则卡")

    def test_every_station_needs_a_check_and_four_hints(self):
        self.edit("1.6", '"1.6c": _flag_check', '"1.6x": _flag_check')
        self.edit("1.6", '"1.6b": ["方向 1.6b", "位置 1.6b", "相似例子 1.6b", "答案与解释 1.6b"]',
                  '"1.6b": ["方向 1.6b", "位置 1.6b", "答案与解释 1.6b"]')
        errors = self.errors()[1]
        self.assertFinding(errors, "I4", "1.6c 没有检查函数")
        self.assertFinding(errors, "I4", "1.6x")
        self.assertFinding(errors, "I4", "HINTS['1.6b']", "3 条")


class InterfaceTest(ValidateTestCase):
    """Plan I3: names and shapes."""

    def test_missing_names_and_bad_shapes(self):
        source = helpers.lesson_source("1.6", "06-first-commit", title="Git：第一次提交",
                                       letters="abc", rules=["GIT-01", "GIT-02"])
        source = source.replace("EXAM = []", "EXAM = {}").replace("SCENARIOS = ", "_SCENARIOS = ")
        self.box.add_lesson(source, "01-foundations", "06-first-commit")
        errors = self.errors()[1]
        self.assertFinding(errors, "I3", "缺少 SCENARIOS")
        self.assertFinding(errors, "I3", "EXAM 应该是列表")
        self.assertFinding(errors, "I2", "没有 rules.md")

    def test_review_items(self):
        self.box.add_syllabus_lesson("1.6", extra='''
REVIEW.append({"id": "1.6-r3", "type": "which", "tier": "fluent", "q": "？",
               "options": ["甲"], "answer": "C"})
REVIEW.append({"id": "1.6-r4", "type": "do", "tier": "often", "q": "做", "scenario": "nope"})
REVIEW.append({"id": "x-1", "type": "guess", "tier": "aware", "q": "？"})
''')
        errors = self.errors()[1]
        self.assertFinding(errors, "1.6-r3", "options")
        self.assertFinding(errors, "1.6-r4", "tier")
        self.assertFinding(errors, "1.6-r4", "scenario")
        self.assertFinding(errors, "1.6-r4", "检查函数 check")
        self.assertFinding(errors, "x-1")
        self.assertFinding(errors, "type")

    def test_exam_tasks(self):
        self.box.add_syllabus_lesson("1.6", extra='''
def _build(sc):
    sc.fact("repo", "r")

EXAM.append({"id": "1.6-x1", "gate": "gate-a", "title": "题", "minutes": 5, "build": _build,
             "task": {"A": "在 {dir}/{repo} 里做", "B": "在 {dir}/{repo} 里做"},
             "grade": lambda ctx: None})
EXAM.append({"id": "1.6-x2", "gate": "gate-b", "title": "题", "minutes": 30,
             "task": {"A": "甲"}, "grade": None})
''')
        errors = self.errors()[1]
        self.assertFinding(errors, "§4", "1.6-x1", "gate-b")
        self.assertFinding(errors, "1.6-x1", "一模一样")
        self.assertFinding(errors, "1.6-x2", "minutes")
        self.assertFinding(errors, "1.6-x2", "build")
        self.assertFinding(errors, "1.6-x2", "grade")
        self.assertFinding(errors, "1.6-x2", "两套平行的题面")

    def test_trial_build_finds_broken_builders_and_unknown_placeholders(self):
        self.box.add_syllabus_lesson("1.6", extra='''
def _broken(sc):
    raise RuntimeError("builder bug")

def _build(sc):
    sc.fact("repo", "r")

SCENARIOS["1.6b"] = _broken
EXAM.append({"id": "1.6-x1", "gate": "gate-b", "title": "题", "minutes": 5, "build": _build,
             "task": {"A": "在 {dir}/{repo} 里做", "B": "去 {dir}/{folder} 里做"},
             "grade": lambda ctx: None})
''')
        code, errors = self.errors("1.6", "--build")
        self.assertEqual(code, 1)
        self.assertFinding(errors, "BUILD", "场景 1.6b 搭建失败", "builder bug")
        self.assertFinding(errors, "BUILD", "1.6-x1", "B 卷", "{folder}")
        self.assertFalse(self.box.playground.exists())

    def test_python_39_syntax(self):
        self.box.add_syllabus_lesson("1.6", extra='''
def _newer(value):
    match value:
        case 1:
            return "one"
''')
        self.assertFinding(self.errors()[1], "I3", "3.9")

    def test_a_module_that_raises_at_import(self):
        self.box.add_syllabus_lesson("1.6", extra='raise ValueError("oops")\n')
        self.box.add_syllabus_lesson("1.7")
        code, data = self.validate()
        self.assertEqual(code, 1)
        self.assertFinding(self.findings(data, "1.6")[0], "I3", "ValueError")
        self.assertEqual(self.findings(data, "1.7")[0], [])

    def test_meta_fields(self):
        self.box.add_syllabus_lesson("1.6")
        self.edit("1.6", '"slug": "06-first-commit"', '"slug": "first-commit"')
        self.edit("1.6", '"date": "2026-11-19"', '"date": "2027-01-01"')
        self.edit("1.6", '"prerequisites": []', '"prerequisites": ["1.7"]')
        errors = self.errors()[1]
        self.assertFinding(errors, "slug")
        self.assertFinding(errors, "G4", "今天之后")
        self.assertFinding(errors, "前置课程 1.7")


class RuleCardTest(ValidateTestCase):
    """Plan I2 and G3 through validate."""

    def setUp(self):
        ValidateTestCase.setUp(self)
        self.box.add_syllabus_lesson("1.10")

    def test_missing_card(self):
        self.edit("1.10", "### COMMIT-02", "### COMMIT-09", name="rules.md")
        errors = self.errors("1.10")[1]
        self.assertFinding(errors, "I2", "没有 COMMIT-02 的卡片")
        self.assertFinding(errors, "I2", "COMMIT-09", "没有列在 META['rules'] 里")

    def test_card_problems_are_errors_with_the_line(self):
        self.edit("1.10", "；**复核周期**：12 个月", "", name="rules.md")
        self.edit("1.10", "- **规则类型**：惯例·事实标准", "- **规则类型**：个人偏好", name="rules.md")
        code, errors = self.errors("1.10")
        self.assertEqual(code, 1)
        self.assertFinding(errors, "I2", "规则卡 COMMIT-01（rules.md 第 1 行）", "个人偏好")
        self.assertFinding(errors, "I2", "规则卡 COMMIT-01", "缺少「复核周期」")

    def test_old_format_is_rejected(self):
        entry = helpers.syllabus.lesson_entry("1.10")
        path = self.box.root / "stages" / entry["stage_folder"] / entry["folder"] / "rules.md"
        path.write_text(
            "### COMMIT-01 提交信息遵循约定式提交\n"
            "- **级别**：必须 ｜ **类型**：惯例 ｜ **出处**：https://www.conventionalcommits.org"
            " ｜ **核实**：2026-11-19\n\n"
            "### COMMIT-02 一次提交一件事\n"
            "- **级别**：推荐 ｜ **类型**：惯例 ｜ **出处**：https://git-scm.com ｜ **核实**：2026-11-19\n",
            encoding="utf-8")
        errors = self.errors("1.10")[1]
        self.assertFinding(errors, "COMMIT-01", "缺少「约束力」")
        self.assertFinding(errors, "COMMIT-02", "缺少「谁来管」")

    def test_family_of_plan_section_4_is_a_warning(self):
        self.edit("1.10", "- **规则类型**：惯例·事实标准", "- **规则类型**：规范·组织", name="rules.md")
        code, data = self.validate("1.10")
        errors, warnings = self.findings(data, "1.10")
        self.assertEqual(code, 0, errors)
        self.assertFinding(warnings, "§4", "COMMIT-01", "规范·组织", "惯例·事实标准")

    def test_level_named_by_the_plan(self):
        self.box.add_syllabus_lesson("1.11")
        self.edit("1.11", "- **约束力**：推荐（适用范围：所有项目）",
                  "- **约束力**：必须（适用范围：所有项目）", name="rules.md")
        warnings = self.findings(self.validate("1.11")[1], "1.11")[1]
        self.assertFinding(warnings, "ACC-02", "推荐")


class CompleteTest(ValidateTestCase):
    def test_complete_wants_every_lesson_of_the_syllabus(self):
        self.box.add_syllabus_lesson("0.1")
        code, data = self.validate("--complete")
        self.assertEqual(code, 1)
        general = [f["message"] for f in data["general"]]
        self.assertTrue(any("1.16" in message for message in general), general)
        self.assertTrue(any("gate-b" in message for message in general), general)
        self.assertFinding(self.findings(data, "0.1")[0], "I1", "lesson.md")


if __name__ == "__main__":
    unittest.main()
