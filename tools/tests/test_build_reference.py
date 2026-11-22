"""tools/dev/build_reference.py: the handbook, the glossary, the rules table of
STANDARDS.md, the lesson tables of the stage pages and notes/my-rules.md.

Every test that writes works on a throw-away copy under $TMPDIR (a snapshot of
the real lessons, or a small made-up workspace); the real workspace is only
read.
"""

import datetime
import importlib.util
import os
import shutil
import tempfile
import textwrap
import types
import unittest
from pathlib import Path

import helpers

from courselib import rulecards, syllabus

_SPEC = importlib.util.spec_from_file_location(
    "build_reference", str(helpers.TOOLS / "dev" / "build_reference.py"))
BUILDER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(BUILDER)

_SIM = importlib.util.spec_from_file_location(
    "make_sim_home_for_reference", str(helpers.TOOLS / "dev" / "make_sim_home.py"))
SIM = importlib.util.module_from_spec(_SIM)
_SIM.loader.exec_module(SIM)

TODAY = datetime.date(2026, 11, 20)
COPIED = ("stages", "STANDARDS.md", "GLOSSARY.md", "handbook", "notes/my-rules.md")


def run(root, *args):
    lines = []
    code = BUILDER.main(["--root", str(root)] + list(args), out=lines.append)
    return code, lines


def snapshot(base):
    """A copy of the parts of the real workspace the generator reads and writes."""
    root = base / "ws"
    root.mkdir()
    for rel in COPIED:
        source = helpers.REPO / rel
        if source.is_dir():
            shutil.copytree(str(source), str(root / rel),
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        elif source.is_file():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(root / rel))
    return root


def tree(root):
    """{relative path: bytes} of every file under ``root``."""
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(Path(root).rglob("*")) if p.is_file()}


LESSON = '''\
META = {{
    "id": "{id}", "slug": "{slug}", "title": "{title}", "stage": {stage},
    "prerequisites": [],
    "stations": [
        {{"id": "{id}a", "title": "第一站", "minutes": {a}, "new_concept": "x", "new_commands": []}},
        {{"id": "{id}b", "title": "第二站", "minutes": {b}, "new_concept": "y", "new_commands": []}},
    ],
    "rules": {rules!r},
    "verified": {{"date": "2026-11-19", "tools": {{}}}},
    "unverified_steps": [],
}}
TERMS = {terms!r}
'''

CARD = textwrap.dedent('''\
    ### {id} {title}

    - **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
    - **规则类型**：{kind}
    - **规则**：照着做的一句话。
    - **谁说的**：本课程约定（2026-11-19 定）https://example.com/rule
    - **核对日期**：2026-11-19；**复核周期**：12 个月
    - **谁来管**：导师；**不遵守的后果**：会出错。
    - **为什么**：两三句理由。
    - **正例**：

          ls -l   # 一段缩进的代码

    - **反例**：不看就做。
    - **怎么检查**：人工检查：看一眼。
    - **例外**：无
    - **旧教程提醒**：无
    - **学于**：{lesson}
    ''')


class FakeWorkspace:
    """A small workspace with lessons 0.1 and 0.2 (folders as in the syllabus)."""

    def __init__(self, base):
        self.root = base / "fake"
        (self.root / "stages" / "00-orientation").mkdir(parents=True)
        (self.root / "handbook").mkdir()

    def lesson(self, number, slug, title, rules=(), cards=None, terms=(), minutes=(20, 25),
               closing=5, rules_text=None):
        lesson_id = f"0.{number}"
        folder = self.root / "stages" / "00-orientation" / slug
        folder.mkdir()
        (folder / "lesson.py").write_text(LESSON.format(
            id=lesson_id, slug=slug, title=title, stage=0, a=minutes[0], b=minutes[1],
            rules=list(rules), terms=list(terms)), encoding="utf-8")
        (folder / "lesson.md").write_text(f"# {lesson_id} {title}\n\n## 收尾（约 {closing} 分钟）\n", encoding="utf-8")
        if rules_text is None:
            rules_text = "".join(CARD.format(id=rule_id, title=card_title, kind=kind, lesson=lesson_id)
                                 + "\n" for rule_id, card_title, kind in (cards or []))
        (folder / "rules.md").write_text(rules_text, encoding="utf-8")
        return folder

    def standard(self):
        (self.root / "STANDARDS.md").write_text(
            "# 规范地图\n\n## 3. 表\n\n手写的说明。\n\n" + BUILDER.BEGIN + "\n旧表\n" + BUILDER.END
            + "\n\n表后面的手写文字。\n", encoding="utf-8")

    def stage_page(self):
        (self.root / "stages" / "00-orientation" / "README.md").write_text(
            "# 阶段 0\n\n## 课表\n\n" + BUILDER.BEGIN + "\n" + BUILDER.END + "\n\n后面的手写文字。\n",
            encoding="utf-8")


def term(name, english, plain, first):
    return {"term": name, "en": english, "plain": plain, "first": first}


class TodayTest(unittest.TestCase):
    """The real lessons as they are now, in a snapshot under $TMPDIR."""

    @classmethod
    def setUpClass(cls):
        cls.base = Path(os.path.realpath(tempfile.mkdtemp(prefix="build-reference-")))
        cls.root = snapshot(cls.base)
        cls.code, cls.lines = run(cls.root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(str(cls.base), True)

    def test_write_then_check_is_current_and_a_second_run_changes_nothing(self):
        self.assertEqual(self.code, 0, self.lines)
        before = tree(self.root)
        code, lines = run(self.root, "--check")
        self.assertEqual(code, 0, lines)
        self.assertTrue(any("生成的部分都是最新的" in line for line in lines), lines)
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        self.assertFalse([line for line in lines if line.startswith(("写好了", "新建了"))], lines)
        self.assertEqual(tree(self.root), before)

    def test_every_rule_of_plan_section_4_is_in_the_handbook_exactly_once(self):
        expected = [rule for entry in syllabus.LESSONS for rule in entry["rules"]]
        self.assertEqual(len(expected), 30)
        headings = []
        for chapter in BUILDER.CHAPTERS:
            text = (self.root / "handbook" / chapter[0]).read_text(encoding="utf-8")
            headings += [card.id for card in rulecards.parse_cards(text)]
        present = [rule for rule in expected if rule in headings]
        for rule in present:
            self.assertEqual(headings.count(rule), 1, rule)
        missing = sorted(set(expected) - set(headings))
        for rule in missing:
            # only a rule whose card is missing may be absent, and the report says so
            self.assertTrue(any(rule in line and "没有卡片" in line for line in self.lines), (rule, self.lines))

    def test_cards_are_copied_byte_for_byte(self):
        chapters = "".join((self.root / "handbook" / chapter[0]).read_text(encoding="utf-8")
                           for chapter in BUILDER.CHAPTERS)
        for rules in sorted(self.root.glob("stages/*/*/rules.md")):
            blocks, _stray = BUILDER.card_blocks(rules.read_text(encoding="utf-8"))
            for rule_id, _title, _heading, raw in blocks:
                if BUILDER.chapter_of(rule_id.split("-")[0]):
                    self.assertIn(raw, chapters, rule_id)

    def test_card_blocks_find_the_same_cards_as_the_course_tool(self):
        for rules in sorted(helpers.REPO.glob("stages/*/*/rules.md")):
            text = rules.read_text(encoding="utf-8")
            blocks, _stray = BUILDER.card_blocks(text)
            self.assertEqual([(b[0], b[1]) for b in blocks],
                             [(c.id, c.title) for c in rulecards.parse_cards(text)], rules)

    def test_every_generated_file_has_one_marker_or_its_regions(self):
        for chapter in BUILDER.CHAPTERS:
            text = (self.root / "handbook" / chapter[0]).read_text(encoding="utf-8")
            self.assertEqual(text.count(BUILDER.MARKER), 1, chapter[0])
            self.assertTrue(text.startswith("# "), chapter[0])
        for rel in ("handbook/README.md", "GLOSSARY.md"):
            self.assertEqual((self.root / rel).read_text(encoding="utf-8").count(BUILDER.MARKER), 1)
        for rel in ("STANDARDS.md", "stages/00-orientation/README.md", "stages/01-foundations/README.md"):
            text = (self.root / rel).read_text(encoding="utf-8")
            self.assertEqual(len(BUILDER.regions(text)), 1, rel)

    def test_text_outside_the_regions_is_kept(self):
        for rel in ("STANDARDS.md", "stages/00-orientation/README.md", "stages/01-foundations/README.md"):
            old = (helpers.REPO / rel).read_text(encoding="utf-8").split("\n")
            new = (self.root / rel).read_text(encoding="utf-8").split("\n")
            (b_old, e_old), = BUILDER.regions("\n".join(old))
            (b_new, e_new), = BUILDER.regions("\n".join(new))
            self.assertEqual(old[:b_old + 1], new[:b_new + 1], rel)
            self.assertEqual(old[e_old:], new[e_new:], rel)

    def test_the_rules_table_has_thirty_rows_with_the_catalogue_column(self):
        text = (self.root / "STANDARDS.md").read_text(encoding="utf-8")
        (begin, end), = BUILDER.regions(text)
        rows = text.split("\n")[begin + 1:end]
        self.assertEqual(rows[0], "| 编号 | 标题 | 规则类型 | 约束力 | 哪一课 | 目录里的出处 |")
        ids = [row.split(" | ")[0].lstrip("| ") for row in rows[2:]]
        cards = [c for c in ids if c]
        self.assertEqual(len(cards), len(set(cards)))
        self.assertLessEqual(len(cards), 30)

    def test_stage_pages_give_the_hours_and_what_they_contain(self):
        for stage, folder in ((0, "00-orientation"), (1, "01-foundations")):
            text = (self.root / "stages" / folder / "README.md").read_text(encoding="utf-8")
            self.assertIn(f"阶段 {stage} 一共约 ", text)
            self.assertIn("再加 15% 留给复习", text)
            self.assertIn("讲解题", text)
        self.assertTrue(any(line.startswith("阶段 0：约 ") for line in self.lines), self.lines)
        self.assertTrue(any(line.startswith("阶段 1：约 ") for line in self.lines), self.lines)

    def test_the_notes_skeleton_is_a_fixed_point_of_the_sim_home_skeleton(self):
        model, _targets, extras = BUILDER.build(self.root, TODAY)
        notes = extras["notes"]
        self.assertEqual(SIM.rules_notes_skeleton(notes), notes)
        self.assertTrue(BUILDER.is_skeleton(notes))
        self.assertIn("这个文件是你的，课程不会覆盖它", notes)
        headings = [line for line in notes.splitlines() if line.startswith("### ")]
        cards = [card.heading for card in model.cards]
        self.assertEqual(headings, [h for h in cards if h in headings])
        self.assertEqual(len(headings), len(set(headings)))

    def test_nothing_but_the_generated_files_is_written(self):
        before = tree(self.root)
        code, _lines = run(self.root)
        self.assertEqual(code, 0)
        self.assertEqual(sorted(tree(self.root)), sorted(before))
        self.assertFalse(list(self.root.rglob("*.tmp")))
        self.assertFalse(list(self.root.rglob("__pycache__")))


class ToolTest(unittest.TestCase):
    """Behaviour on a small made-up workspace."""

    def setUp(self):
        self.base = Path(os.path.realpath(tempfile.mkdtemp(prefix="build-reference-")))
        self.addCleanup(shutil.rmtree, str(self.base), True)
        self.ws = FakeWorkspace(self.base)
        self.root = self.ws.root

    def two_lessons(self, terms_one=(), terms_two=()):
        self.ws.lesson(1, "01-first-steps", "第一次动手", rules=["META-01"],
                       cards=[("META-01", "报错三问", "规范·本课程约定")], terms=terms_one)
        self.ws.lesson(2, "02-files-and-paths", "文件、路径和代码的家", rules=["WS-01", "WS-02"],
                       cards=[("WS-01", "代码不放网盘同步目录", "惯例·平台与工具"),
                              ("WS-02", "命名用小写英文加短横线", "规范·组织")],
                       terms=terms_two, minutes=(30, 35))
        self.ws.standard()
        self.ws.stage_page()

    def test_chapters_are_created_with_their_hand_written_part(self):
        self.two_lessons()
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        text = (self.root / "handbook" / "01-workspace-and-naming.md").read_text(encoding="utf-8")
        hand, generated = text.split(BUILDER.MARKER)
        self.assertTrue(hand.startswith("# 学习工作区和命名\n\n"))
        self.assertIn("### WS-01 代码不放网盘同步目录", generated)
        self.assertLess(generated.index("WS-01"), generated.index("WS-02"))
        self.assertIn("../stages/00-orientation/02-files-and-paths/rules.md", generated)
        self.assertTrue(any("新建了：handbook/01-workspace-and-naming.md" == line for line in lines))

    def test_the_hand_written_part_is_kept_and_the_generated_part_replaced(self):
        self.two_lessons()
        run(self.root)
        path = self.root / "handbook" / "14-about-rules.md"
        text = path.read_text(encoding="utf-8")
        hand, _generated = text.split(BUILDER.MARKER)
        new_hand = hand.replace("关于规则本身", "关于规则本身（改过）") + "多写的一段。\n\n"
        path.write_text(new_hand + BUILDER.MARKER + "\n\n手改了生成的部分\n", encoding="utf-8")
        code, lines = run(self.root, "--check")
        self.assertEqual(code, 1, lines)
        self.assertIn("过时了（重新运行 python3 tools/dev/build_reference.py 会改它）：handbook/14-about-rules.md",
                      lines)
        self.assertEqual(path.read_text(encoding="utf-8"),
                         new_hand + BUILDER.MARKER + "\n\n手改了生成的部分\n")
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(new_hand + BUILDER.MARKER + "\n\n## 这一类的卡片（1 张）"))
        self.assertNotIn("手改了生成的部分", text)

    def test_a_file_without_the_marker_is_refused_and_left_alone(self):
        self.two_lessons()
        path = self.root / "GLOSSARY.md"
        path.write_text("# 术语表\n\n有人手写的，没有分隔行。\n", encoding="utf-8")
        code, lines = run(self.root)
        self.assertEqual(code, 2, lines)
        self.assertEqual(path.read_text(encoding="utf-8"), "# 术语表\n\n有人手写的，没有分隔行。\n")
        self.assertTrue(any(line.startswith("没有动这个文件：GLOSSARY.md") for line in lines), lines)
        # the other files are still written
        self.assertTrue((self.root / "handbook" / "README.md").exists())

    def test_regions_are_filled_and_the_text_around_them_kept(self):
        self.two_lessons()
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        text = (self.root / "STANDARDS.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# 规范地图\n\n## 3. 表\n\n手写的说明。\n\n" + BUILDER.BEGIN + "\n| 编号 |"))
        self.assertTrue(text.endswith(BUILDER.END + "\n\n表后面的手写文字。\n"))
        self.assertNotIn("旧表", text)
        self.assertIn("| WS-02 | 命名用小写英文加短横线 | 规范·组织 | 必须（本课程）；推荐（所有项目） | 0.2 | — |", text)
        page = (self.root / "stages" / "00-orientation" / "README.md").read_text(encoding="utf-8")
        self.assertIn("| 0.2 | 文件、路径和代码的家 | a 第一站（30 分钟）；b 第二站（35 分钟） | 65 |", page)
        self.assertTrue(page.endswith(BUILDER.END + "\n\n后面的手写文字。\n"))

    def test_an_unclosed_region_is_refused(self):
        self.two_lessons()
        path = self.root / "STANDARDS.md"
        path.write_text("# 规范地图\n\n" + BUILDER.BEGIN + "\n旧表\n", encoding="utf-8")
        code, lines = run(self.root)
        self.assertEqual(code, 2, lines)
        self.assertEqual(path.read_text(encoding="utf-8"), "# 规范地图\n\n" + BUILDER.BEGIN + "\n旧表\n")
        self.assertTrue(any("后面没有「生成结束」" in line for line in lines), lines)

    def test_catalogue_refs_fill_the_last_column_and_gaps_are_reported(self):
        self.two_lessons()
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        self.assertTrue(any("没有 handbook/catalogue-refs.json" in line for line in lines), lines)
        (self.root / "handbook" / "catalogue-refs.json").write_text(
            '{"WS-01": ["B09"], "WS-02": ["C09", "E08"]}\n', encoding="utf-8")
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        text = (self.root / "STANDARDS.md").read_text(encoding="utf-8")
        self.assertIn("| 0.2 | B09 |", text)
        self.assertIn("| 0.2 | C09、E08 |", text)
        self.assertIn("| 报错三问 | 规范·本课程约定 | 必须（本课程）；推荐（所有项目） | 0.1 | — |", text)
        self.assertTrue(any("catalogue-refs.json 里没有 META-01" in line for line in lines), lines)

    def test_glossary_keeps_the_first_occurrence_and_reports_conflicts(self):
        self.two_lessons(
            terms_one=[term("路径", "path", "文件在电脑里的地址，一层层的", "0.1a"),
                       term("终端", "terminal", "用打字而不是点鼠标来指挥电脑的窗口", "0.1b")],
            terms_two=[term("路径", "path", "文件在电脑里的地址", "0.2a"),
                       term("命令", "instruction", "在终端里敲的一行指令", "0.2a"),
                       term("PATH", "PATH", "找命令的一串文件夹", "0.2b")])
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        text = (self.root / "GLOSSARY.md").read_text(encoding="utf-8")
        generated = text.split(BUILDER.MARKER)[1]
        self.assertEqual(generated.count("| 路径 | path |"), 1)
        self.assertIn("| 路径 | path | 文件在电脑里的地址，一层层的 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |",
                      generated)
        self.assertIn("## 英文索引", generated)
        index = generated.split("## 英文索引")[1]
        self.assertLess(index.index("| instruction |"), index.index("| path |"))
        self.assertLess(index.index("| path |"), index.index("| terminal |"))
        report = "\n".join(lines)
        self.assertIn("术语「路径」在第 0.1 课（0.1a）和第 0.2 课（0.2a）都列了", report)
        self.assertIn("大白话不一样", report)
        self.assertIn("「命令」（command）", report)
        self.assertNotIn("英文「path」对应几个", report)   # PATH is not path

    def test_card_problems_and_labels_are_reported_not_fixed(self):
        bad = CARD.format(id="WS-02", title="命名", kind="规范·团队约定", lesson="0.2").replace(
            "- **为什么**：两三句理由。\n", "")
        folder = self.ws.lesson(2, "02-files-and-paths", "文件、路径和代码的家", rules=["WS-01", "WS-02"],
                                rules_text=bad)
        self.ws.standard()
        before = (folder / "rules.md").read_text(encoding="utf-8")
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        self.assertEqual((folder / "rules.md").read_text(encoding="utf-8"), before)
        report = "\n".join(lines)
        self.assertIn("WS-02（stages/00-orientation/02-files-and-paths/rules.md）：缺少「为什么」", report)
        self.assertIn("WS-02 的规则类型是「规范·团队约定」", report)
        self.assertIn("第 0.2 课：META[\"rules\"] 里有 WS-01，但 rules.md 里没有它的卡片", report)
        self.assertIn("META-01（第 0.1 课）没有卡片", report)
        chapter = (self.root / "handbook" / "01-workspace-and-naming.md").read_text(encoding="utf-8")
        self.assertIn(BUILDER.card_blocks(bad)[0][0][3], chapter)

    def test_a_broken_lesson_module_is_reported_and_the_rest_still_built(self):
        self.two_lessons()
        broken = self.root / "stages" / "00-orientation" / "01-first-steps" / "lesson.py"
        broken.write_text("META = {\n", encoding="utf-8")
        code, lines = run(self.root)
        self.assertEqual(code, 0, lines)
        self.assertTrue(any("读不了第 0.1 课的 lesson.py" in line for line in lines), lines)
        self.assertIn("### WS-01", (self.root / "handbook" / "01-workspace-and-naming.md").read_text(encoding="utf-8"))
        page = (self.root / "stages" / "00-orientation" / "README.md").read_text(encoding="utf-8")
        self.assertIn("有的课读不出站的分钟数，这个数偏小。", page)

    def test_check_writes_nothing(self):
        self.two_lessons()
        before = tree(self.root)
        code, lines = run(self.root, "--check")
        self.assertEqual(code, 1, lines)
        self.assertEqual(tree(self.root), before)
        self.assertTrue(any(line == "过时了（重新运行 python3 tools/dev/build_reference.py 会改它）：GLOSSARY.md"
                            for line in lines), lines)

    def test_notes_are_created_once_and_never_changed_after_the_learner_wrote(self):
        self.two_lessons()
        notes = self.root / "notes" / "my-rules.md"
        code, lines = run(self.root)
        self.assertFalse(notes.exists())
        self.assertTrue(any("notes/my-rules.md 还没有" in line for line in lines), lines)
        code, lines = run(self.root, "--notes")
        self.assertEqual(code, 0, lines)
        self.assertIn("notes/my-rules.md 还没有，按卡片新建了。", lines)
        text = notes.read_text(encoding="utf-8")
        self.assertIn("## 0.1 第一次动手\n\n### META-01 报错三问\n\n## 0.2 文件、路径和代码的家\n\n"
                      "### WS-01 代码不放网盘同步目录\n\n### WS-02 命名用小写英文加短横线\n", text)
        self.assertEqual(text.count("\n\n\n"), 0)
        code, lines = run(self.root, "--notes")
        self.assertIn("notes/my-rules.md 还只是骨架，和卡片一致，没有改。", lines)
        # a skeleton with an old heading is rewritten
        notes.write_text(text.replace("WS-02 命名用小写英文加短横线", "WS-02 旧标题") + "\n\n", encoding="utf-8")
        code, lines = run(self.root, "--check")
        self.assertEqual(code, 1, lines)
        code, lines = run(self.root, "--notes")
        self.assertIn("notes/my-rules.md 还只是小标题的骨架，按现在的卡片重写了。", lines)
        self.assertEqual(notes.read_text(encoding="utf-8"), text)
        # once the learner wrote a line, nothing changes; headings are only reported
        written = text.replace("### WS-01 代码不放网盘同步目录\n",
                               "### WS-01 代码不放网盘同步目录\n\n代码放 ~/Developer，网盘只放文档。\n")
        written = written.replace("WS-02 命名用小写英文加短横线", "WS-02 我改过的标题")
        notes.write_text(written, encoding="utf-8")
        for args in ((), ("--notes",), ("--check",)):
            code, lines = run(self.root, *args)
            self.assertEqual(notes.read_text(encoding="utf-8"), written, args)
            self.assertIn("notes/my-rules.md 里已经有学习者写的内容，没有改它。", lines)
            self.assertTrue(any("少了小标题「### WS-02 命名用小写英文加短横线」" in line for line in lines), lines)

    def test_closing_minutes_are_the_number_in_the_closing_heading(self):
        # tools-r5 T8: the heading is the lesson's number (validate checks the
        # header against it); a heading that differs from the fixed rule is
        # used and no longer reported.
        self.ws.lesson(1, "01-first-steps", "第一次动手", closing=15)
        self.ws.lesson(2, "02-files-and-paths", "文件、路径和代码的家", closing=5)
        _code, lines = run(self.root)
        self.assertFalse([line for line in lines if "收尾标题写约" in line], lines)
        info = BUILDER.stage_hours(BUILDER.read_model(self.root), 0)
        self.assertEqual(info["closing"], 20)
        self.assertIn("加上 2 课的收尾 20 分钟（第 0.1 课 15 分钟，其余每课 5 分钟）",
                      BUILDER.hours_sentence(info))

    def test_no_other_lessons_means_no_fixed_rule_in_the_sentence(self):
        # Ruling 2 of 2026-11-20: every closing is calculated, so no lesson
        # may be left for 「其余」; the sentence then names only the lessons.
        self.ws.lesson(1, "01-first-steps", "第一次动手", closing=10)
        self.ws.lesson(2, "02-files-and-paths", "文件、路径和代码的家", closing=15)
        _code, _lines = run(self.root)
        info = BUILDER.stage_hours(BUILDER.read_model(self.root), 0)
        sentence = BUILDER.hours_sentence(info)
        self.assertIn("加上 2 课的收尾 25 分钟（第 0.1 课 10 分钟、第 0.2 课 15 分钟）", sentence)
        self.assertNotIn("其余", sentence)

    def test_the_fixed_rule_is_stated_only_for_the_lessons_that_follow_it(self):
        # The rest are only early lessons: 「从第 1.12 课起 10 分钟」 would be untrue.
        lessons = [types.SimpleNamespace(id="1.3", closing=5), types.SimpleNamespace(id="1.4", closing=15),
                   types.SimpleNamespace(id="1.12", closing=25)]
        info = {"stage": 1, "hours": "1", "station_count": 6, "stations": 0, "lessons": lessons,
                "closing": 45, "gates": [], "total": 45, "with_review": 52, "complete": True}
        sentence = BUILDER.hours_sentence(info)
        self.assertIn("（第 1.4 课 15 分钟、第 1.12 课 25 分钟，其余每课 5 分钟）", sentence)
        self.assertNotIn("从第 1.12 课起", sentence)

    def test_a_missing_closing_heading_is_reported_and_the_fixed_rule_used(self):
        folder = self.ws.lesson(1, "01-first-steps", "第一次动手")
        (folder / "lesson.md").write_text("# 0.1 第一次动手\n\n没有收尾。\n", encoding="utf-8")
        _code, lines = run(self.root)
        self.assertTrue(any("第 0.1 课的 lesson.md 里没找到「## 收尾（约 N 分钟）」；小时数按 5 分钟算。" in line
                            for line in lines), lines)
        info = BUILDER.stage_hours(BUILDER.read_model(self.root), 0)
        self.assertEqual(info["closing"], 5)


class HelperTest(unittest.TestCase):
    def test_anchor_follows_the_github_rule(self):
        self.assertEqual(BUILDER.anchor("GIT-03 提交前先看改了什么"), "git-03-提交前先看改了什么")
        self.assertEqual(BUILDER.anchor("META-01 报错三问：谁在报错，关键词是什么，我刚才敲了什么"),
                         "meta-01-报错三问谁在报错关键词是什么我刚才敲了什么")
        self.assertEqual(BUILDER.anchor("REPO-02 .gitignore 从官方模板起步"), "repo-02-gitignore-从官方模板起步")
        self.assertEqual(BUILDER.anchor("ED-02 文本统一 UTF-8 和 LF，用 .editorconfig 说明"),
                         "ed-02-文本统一-utf-8-和-lf用-editorconfig-说明")

    def test_cells_stay_on_one_line_and_never_become_html(self):
        self.assertEqual(BUILDER.cell("比如 <h1>，a | b\n下一行"), "比如 &lt;h1>，a \\| b 下一行")
        self.assertEqual(BUILDER.cell("1 < 2"), "1 < 2")

    def test_binding_is_shortened_pair_by_pair(self):
        card = BUILDER.Card("X-01", "t", "### X-01 t", "", {
            "约束力": "推荐（适用范围：所有项目）；必须（适用范围：本课程，每课的完成的定义）。说明文字"}, None, "")
        self.assertEqual(BUILDER.binding_short(card), "推荐（所有项目）；必须（本课程，每课的完成的定义）")
        card.parsed = {"约束力": "看情况"}
        self.assertEqual(BUILDER.binding_short(card), "—")

    def test_hours_round_to_the_nearest_half_hour(self):
        self.assertEqual(BUILDER.format_hours(15), "7.5")
        self.assertEqual(BUILDER.format_hours(52), "26")

    def test_spaces_only_between_chinese_and_latin(self):
        self.assertEqual(BUILDER.spaced("小关卡 gate-a", "和", "阶段验收 gate-1"), "小关卡 gate-a 和阶段验收 gate-1")
        self.assertEqual(BUILDER.spaced("gate-x", "和", "gate-y"), "gate-x 和 gate-y")

    def test_splice_regions_keeps_everything_outside(self):
        text = "a\n" + BUILDER.BEGIN + "\nold\n" + BUILDER.END + "\nb\n"
        self.assertEqual(BUILDER.splice_regions(text, "new\n"),
                         "a\n" + BUILDER.BEGIN + "\nnew\n" + BUILDER.END + "\nb\n")
        with self.assertRaises(BUILDER.Refusal):
            BUILDER.splice_regions("a\n" + BUILDER.END + "\n", "x")
        with self.assertRaises(BUILDER.Refusal):
            BUILDER.splice_regions(BUILDER.BEGIN + "\n" + BUILDER.BEGIN + "\n" + BUILDER.END + "\n", "x")

    def test_write_atomic_leaves_no_temporary_file(self):
        base = Path(os.path.realpath(tempfile.mkdtemp(prefix="build-reference-")))
        self.addCleanup(shutil.rmtree, str(base), True)
        target = base / "sub" / "file.md"
        BUILDER.write_atomic(target, "一\n")
        BUILDER.write_atomic(target, "二\n")
        self.assertEqual(target.read_text(encoding="utf-8"), "二\n")
        self.assertEqual([p.name for p in target.parent.iterdir()], ["file.md"])


if __name__ == "__main__":
    unittest.main()
