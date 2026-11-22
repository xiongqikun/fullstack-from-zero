#!/usr/bin/env python3
"""Generate the shared reference documents from the lessons (plan T3).

For builders only; learners never run this.  Standard library only, Python
3.9 or newer.

    python3 tools/dev/build_reference.py            # write every generated part
    python3 tools/dev/build_reference.py --check    # write nothing; exit 1 when a part is out of date
    python3 tools/dev/build_reference.py --notes    # create notes/my-rules.md (only while it is a skeleton)

What it reads: every ``stages/*/*/rules.md`` (the rule cards, plan I2), and
every lesson module, loaded the way the course tool loads them
(``courselib.catalog``): ``META`` (titles, stations, minutes, rule ids) and
``TERMS``.  ``handbook/catalogue-refs.json`` gives the last column of the
rules table in STANDARDS.md.

What it writes:

- Files with a marker line ``MARKER``: everything above the marker is written
  by people and kept byte for byte; everything below it is replaced on every
  run.  ``handbook/01-…md`` to ``handbook/14-…md`` (the cards of one rule
  family each, copied byte for byte from rules.md), ``handbook/README.md``
  (the index) and ``GLOSSARY.md`` (every TERMS entry).  A missing file is
  created with the hand-written part kept in ``INITIAL``; a file that exists
  without the marker is never touched (reported, exit code 2).
- Regions between ``BEGIN`` and ``END`` in the middle of a file: the rules
  table in section 3 of ``STANDARDS.md`` and the lesson table of each stage
  page ``stages/<stage>/README.md`` (with the hours of the stage, computed by
  plan G5a).  Everything outside the regions is kept.
- ``--notes`` only: ``notes/my-rules.md`` (learner-owned, plan G11).  It is
  written when it does not exist or is still a skeleton (no line of the
  learner under any heading); otherwise it is never changed and the headings
  that differ from the cards are only reported.

Every file is written to a temporary name in the same folder and renamed, and
only when its content changes, so the same input always gives the same
output and a second run changes nothing.  ``--check`` writes nothing; it
exits 1 and names each file whose generated part is out of date (0 when all
are current).  The report printed after the files says plainly what could not
be read and which cards or terms need their lesson's owner; the generator
never edits a lesson.
"""

import sys

sys.dont_write_bytecode = True

import argparse
import json
import math
import os
import re
import tempfile
import unicodedata
from fractions import Fraction
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
TOOLS = WORKSPACE / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from courselib import progress, rulecards, syllabus
from courselib.catalog import load_catalog
from courselib.status import EXPLAIN_MINUTES

PROG = "python3 tools/dev/build_reference.py"
MARKER = "<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->"
BEGIN = "<!-- 生成开始：python3 tools/dev/build_reference.py，请不要手改这一段 -->"
END = "<!-- 生成结束 -->"

STANDARDS = "STANDARDS.md"
GLOSSARY = "GLOSSARY.md"
HANDBOOK = "handbook"
HANDBOOK_INDEX = "handbook/README.md"
HOW_TO_READ = "handbook/00-how-to-read-a-rule.md"
CATALOGUE_REFS = "handbook/catalogue-refs.json"
NOTES = "notes/my-rules.md"

#: Minutes of a lesson's closing steps when its lesson.md has no closing heading
#: (the old fixed rule of COMMON section 1: 5, from 1.12 on 10; since ruling 2 of
#: 2026-11-20 every heading carries the number calculated by plan G5a).
CLOSING_MINUTES = 5
CLOSING_MINUTES_LATE = 10
CLOSING_LATE_FROM = (1, 12)
#: Plan G5a: plus 15 % for reviews, rounded to the half hour.
REVIEW_SHARE = Fraction(15, 100)

#: (file, families, title, the three sentences above the marker).  The
#: chapters of the handbook, in order; a family is the part of a rule id
#: before the dash.
CHAPTERS = (
    ("01-workspace-and-naming.md", ("WS",), "学习工作区和命名",
     ("这一类规则管两件事：代码放在哪里，文件和文件夹叫什么名字。"
     "代码放进网盘同步的文件夹，同步程序会一个文件一个文件地搬动 Git 的仓库，可能弄丢或弄坏里面的内容。"
     "名字里有空格、大写字母或中文，敲命令时容易出错，到了区分大小写的服务器上还可能找不到。")),
    ("02-terminal-safety.md", ("TERM",), "终端安全",
     ("终端照字面执行你敲的每一个字，不会问你“确定吗”。"
     "这一类规则让你在运行看不懂的命令之前先停下来弄懂，在删除之前先看清要删什么。"
     "终端里删掉的东西不进废纸篓，这两步各花几秒钟，挡住的是找不回来的损失。")),
    ("03-editor.md", ("ED",), "编辑器",
     ("编辑器的很多功能以打开的文件夹为单位，只打开一个文件，搜索、内置终端和项目里的设置都会落空。"
     "文字存进文件时要选一种编码和一种换行写法，写的人和读的人选得不一样，就会出乱码，Git 也会把没改的行算成改动。"
     "这一类规则让你打开整个项目，并用 `.editorconfig` 把格式写下来，换一个人、换一个编辑器也照样存。")),
    ("04-documents.md", ("DOC",), "文档",
     ("打开一个陌生项目的人，第一件事是找说明。"
     "没有 `README.md`，别人看不出这是什么、怎么用，六个月后的你也一样。"
     "这一类规则规定说明放在哪里、回答哪几个问题。")),
    ("05-git.md", ("GIT",), "Git",
     ("Git 只记你交给它的东西，也只按你的设置写下作者。"
     "这一类规则防的是几件提交以后才发现的事：仓库建错了地方，提交里写进了你不想公开的名字和邮箱，"
     "提交了没看过的改动，或者一条命令丢掉了还没提交的修改。"
     "这些事大多没有人会拦你，Git 执行时也不提醒，所以要在动手之前看一眼。")),
    ("06-commits.md", ("COMMIT",), "提交",
     ("提交是你以后查找、比较、撤回改动的单位。"
     "一次提交装了几件不相干的事，说明就写不清，撤回时还会把好的改动一起撤掉。"
     "这一类规则规定一次提交装什么、第一行说明怎么写，让人和工具都读得懂历史。")),
    ("07-repository-hygiene.md", ("REPO",), "什么不该进仓库",
     ("仓库会被复制、推送、公开，历史里的每一个版本都留着。"
     "密钥、密码、令牌只要进过一次提交，就要当它已经泄露。"
     "这一类规则让你在第一次提交之前就把这类文件挡在门外，并从官方模板起步写 `.gitignore`。")),
    ("08-accounts-and-identity.md", ("ACC",), "账号和身份",
     ("你的 GitHub 账号保管着你的代码，也代表你的名字。"
     "只有密码时，密码泄露就等于账号丢了；提交里写着的邮箱，推送到公开仓库以后谁都能看到。"
     "这一类规则保护账号的登录，也保护你的邮箱不被公开。")),
    ("09-remotes-and-backup.md", ("REMOTE",), "远程仓库和备份",
     ("只在一台电脑上的仓库，电脑坏了就全没了。"
     "备份也可能不完整，只有真的恢复一次，才知道它能用。"
     "这一类规则让你在别处留一份完整的仓库，并在推送之前先查有没有密钥和别人的个人信息。")),
    ("10-publishing.md", ("PUB",), "公开发布",
     ("公开仓库的读者是陌生人。"
     "没有说明，他不知道这是什么；没有许可证，他不知道能不能用；没有 `.gitignore`，草稿和杂物会跟着一起公开。"
     "这一类规则列出公开之前根目录里要有的三样东西。")),
    ("11-help-and-staying-current.md", ("HELP", "FRESH"), "求助和与时俱进",
     ("帮你的人看不到你的电脑，只能靠你给的目标、步骤、报错原文和版本来重现问题。"
     "工具一直在变，教程、问答和 AI 的回答里有不少是旧版本的做法。"
     "这一类规则让你把问题问清楚，并在照着一份资料动手之前，先查它的日期和版本。")),
    ("12-working-with-ai.md", ("AI",), "和 AI 一起干活",
     ("AI 交来的说明是它自己的总结，会漏，也会说错；Git 记下的改动清单才是事实。"
     "提交是你签字的那一步，签了字，出了问题算你的。"
     "这一类规则让你先看改动再接受，并在提交里如实写明 AI 参与过。")),
    ("13-managing-work.md", ("PM",), "管理工作",
     ("没有事先写好的标准，人很容易在“差不多了”的时候宣布完成。"
     "只往前做、从不回头看，同样的问题会一直留在原地。"
     "这一类规则让每件事有看得见的完成标准，并按固定的周期、在每个阶段结束时复盘。")),
    ("14-about-rules.md", ("META",), "关于规则本身",
     ("这一类规则管的是你怎样对待报错和规矩本身。"
     "看到报错，先问三件事：谁在报错，关键词是什么，我刚才敲了什么。"
     "遇到一条规矩，先问谁说的、多强制、哪年的版本，这样你分得清哪些必须做，哪些只是一篇旧博客里的话。")),
)

#: The hand-written part of a generated file that does not exist yet (the
#: marker follows it).  Once the file exists, its own text above the marker
#: is kept and this is no longer used.
INITIAL = {
    HANDBOOK_INDEX: (
        "# 规范手册\n\n"
        "阶段 0 和阶段 1 的 30 条规则，按类别分成 14 章。第一次来，先读"
        "[怎么读一张规则卡片](00-how-to-read-a-rule.md)。\n\n"
        "卡片的原文在每一课文件夹的 `rules.md` 里。这里的章节是工具照抄生成的：卡片改了，"
        "手册跟着重新生成；两边对不上时，以 `rules.md` 为准。\n\n"
        "每条规则用你自己的话写在 `notes/my-rules.md` 里，那个文件是你的。\n"),
    GLOSSARY: (
        "# 术语表\n\n"
        "这里收着阶段 0 和阶段 1 每一课第一次讲到的术语，按上课顺序排。"
        "每个词有一句大白话，和它第一次出现的那一站；想看完整的讲法，回到那一课去读。\n\n"
        "表后面有一张按英文字母排的索引：看到一个英文词，可以从那里查到中文。\n\n"
        "下面的表是工具从每一课的术语清单生成的。同一个词在两课都出现时，只留第一次出现的那一条。"
        "要改一个词，改它所在的那一课。\n"),
}
for _file, _families, _title, _intro in CHAPTERS:
    INITIAL[HANDBOOK + "/" + _file] = f"# {_title}\n\n{_intro}\n"

#: The region a file may hold, by file: STANDARDS.md has the rules table,
#: each stage page the lesson table of its stage.
STAGE_PAGE = re.compile(r"^stages/(\d{2})-[^/]+/README\.md$")

# The card heading and the end of a card, exactly as courselib.rulecards
# reads them (tests compare the two).
_HEADING = re.compile(r"^###[ \t]+([A-Z][A-Z0-9]*-\d+)(?:[ \t]+(.*))?$", re.MULTILINE)
_ANY_HEADING = re.compile(r"^#{1,3}[ \t]+\S", re.MULTILINE)
_BINDING_PAIR = re.compile(
    r"(必须|推荐|参考)[ \t]*[（(][ \t]*适用范围[ \t]*[：:][ \t]*([^）)]*)[）)]")
_TAGLIKE = re.compile(r"<(?=[A-Za-z/!])")

# ---------------------------------------------------------------------------
# Every line the generator prints.
# ---------------------------------------------------------------------------
TEXT = {
    "written": "写好了：{path}",
    "created": "新建了：{path}",
    "current": "已是最新：{path}",
    "stale": "过时了（重新运行 {prog} 会改它）：{path}",
    "all_current": "生成的部分都是最新的（{n} 个文件）。",
    "some_stale": "{n} 个文件的生成部分过时了。",
    "refused": "没有动这个文件：{path}。{why}",
    "no_marker": "文件里没有分隔行「{marker}」，不知道哪一段是手写的",
    "two_markers": "文件里有 {n} 行分隔行，只能有一行",
    "region_unclosed": "第 {line} 行的「生成开始」后面没有「生成结束」",
    "region_nested": "第 {line} 行的「生成开始」在另一段生成区里面",
    "region_stray_end": "第 {line} 行的「生成结束」前面没有「生成开始」",
    "region_none": "文件里没有「生成开始 / 生成结束」这一对标记",
    "region_unknown": "这个文件里的生成区不知道该放什么",
    "unreadable": "读不了：{path}（{reason}）",
    "write_failed": "写不进去：{path}（{reason}）",
    "stage_hours": "阶段 {stage}：约 {hours} 小时（站 {stations} 分钟 + 收尾 {closing} 分钟 + 关卡 {gates} 分钟，"
                   "共 {total} 分钟；加 15% 复习约 {with_review} 分钟，按半小时取整）",
    "report_head": "要告诉负责人的事（工具没有改任何一课）：",
    "report_none": "没有要报告的问题。",
    "notes_created": "notes/my-rules.md 还没有，按卡片新建了。",
    "notes_rewritten": "notes/my-rules.md 还只是小标题的骨架，按现在的卡片重写了。",
    "notes_same": "notes/my-rules.md 还只是骨架，和卡片一致，没有改。",
    "notes_kept": "notes/my-rules.md 里已经有学习者写的内容，没有改它。",
    "notes_heading_ok": "notes/my-rules.md 的小标题和卡片一致。",
    "notes_stale": "notes/my-rules.md 还只是骨架，但小标题和卡片不一致：运行 {prog} --notes 会按卡片重写它。",
    "notes_missing_file": "notes/my-rules.md 还没有：运行 {prog} --notes 会新建它。",
}


# ---------------------------------------------------------------------------
# Reading the lessons
# ---------------------------------------------------------------------------
class Card:
    """One card: its id, heading line, raw text and parsed fields."""

    def __init__(self, rule_id, title, heading, raw, parsed, lesson, rel):
        self.id = rule_id
        self.title = title
        self.heading = heading
        self.raw = raw
        self.parsed = parsed
        self.lesson = lesson
        self.rel = rel

    @property
    def family(self):
        return self.id.split("-", 1)[0]

    @property
    def number(self):
        try:
            return int(self.id.split("-", 1)[1])
        except (IndexError, ValueError):
            return 0

    @property
    def kind(self):
        return rulecards.type_label(self.parsed.get("规则类型"))


class LessonInfo:
    """What the generator needs of one lesson, whether its module loaded or not."""

    def __init__(self, lesson_id, title, folder_rel, stage, stations, rules, terms, ok, error):
        self.id = lesson_id
        self.title = title
        self.rel = folder_rel
        self.stage = stage
        self.stations = stations
        self.rules = rules
        self.terms = terms
        self.ok = ok
        self.error = error
        #: minutes of the closing steps from 「## 收尾（约 N 分钟）」; None when missing
        self.closing = None


class Model:
    """Everything read from the workspace, plus the report lines."""

    def __init__(self, root):
        self.root = Path(root)
        self.report = []
        self.lessons = []
        self.cards = []
        self.catalog = None

    def note(self, text):
        if text not in self.report:
            self.report.append(text)


def card_blocks(text):
    """``[(id, title, heading line, raw text)]`` of the cards in a rules.md text.

    A card runs from its heading to the next heading of level 1-3 (as in
    ``courselib.rulecards``); trailing blank lines are left out, every other
    byte is kept.  Also returns the non-blank text that follows the first card
    and belongs to no card (a ``## …`` section after the cards, say).
    """
    blocks, stray = [], []
    matches = list(_HEADING.finditer(text))
    for match in matches:
        following = _ANY_HEADING.search(text, match.end())
        end = following.start() if following else len(text)
        raw = re.sub(r"[ \t\r\n]+\Z", "", text[match.start():end]) + "\n"
        heading = text[match.start():match.end()]
        blocks.append((match.group(1), (match.group(2) or "").strip(), heading.rstrip(), raw))
        if following and not _HEADING.match(text, following.start()):
            nxt = _HEADING.search(text, following.start())
            stop = nxt.start() if nxt else len(text)
            extra = text[following.start():stop].strip()
            if extra:
                stray.append(extra.splitlines()[0])
    return blocks, stray


_CLOSING = re.compile(r"^##[ \t]*收尾[ \t]*[（(]约[ \t]*(\d+)[ \t]*分钟[）)]", re.MULTILINE)


def check_closing(model, lesson):
    """The minutes of 「## 收尾（约 N 分钟）」 in the lesson's lesson.md, or None.

    The heading is the lesson's own number (``validate`` checks the header
    against it).  Only a missing heading is reported; the hours then use
    the fixed rule of COMMON section 1 (``closing_minutes``).
    """
    if not lesson.id:
        return
    path = lesson.folder / "lesson.md"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        model.note(TEXT["unreadable"].format(path=lesson.rel + "/lesson.md", reason="lesson.md"))
        return
    found = _CLOSING.findall(text)
    if not found:
        want = closing_minutes(lesson.id)
        model.note(f"第 {lesson.id} 课的 lesson.md 里没找到「## 收尾（约 N 分钟）」；小时数按 {want} 分钟算。")
        return None
    return int(found[0])


def read_model(root):
    """Load the lessons and their cards; never raises for a broken lesson."""
    model = Model(root)
    catalog = load_catalog(root)
    model.catalog = catalog
    for broken in catalog.broken:
        model.note("读不了第 {} 课的 lesson.py（{}）：{}。这一课的标题、站和术语按缺失处理。".format(
            broken.id or broken.rel, broken.rel + "/lesson.py", broken.error))
    for lesson in catalog.all:
        entry = syllabus.lesson_entry(lesson.id) or {}
        title = lesson.title if lesson.ok and lesson.title else entry.get("title", "")
        stations = []
        if lesson.ok:
            for station in lesson.stations:
                minutes = station.get("minutes")
                if not isinstance(minutes, int) or isinstance(minutes, bool):
                    model.note("第 {} 课：站 {} 的 minutes 不是整数（{!r}），算小时数时缺了它。".format(
                        lesson.id, station.get("id"), minutes))
                    minutes = None
                stations.append({"id": station.get("id"), "title": str(station.get("title") or ""),
                                 "minutes": minutes})
        rules = list(lesson.rules) if lesson.ok else list(entry.get("rules", {}))
        terms = []
        if lesson.ok:
            raw_terms = lesson.namespace.get("TERMS")
            if raw_terms is not None and not isinstance(raw_terms, list):
                model.note(f"第 {lesson.id} 课：TERMS 不是列表，术语表里没有这一课的词。")
            for position, item in enumerate(lesson.terms):
                if not all(isinstance(item.get(key), str) and item.get(key).strip()
                           for key in ("term", "en", "plain", "first")):
                    model.note(f"第 {lesson.id} 课：TERMS 第 {position + 1} 项缺少 term / en / plain / first 之一，没有收进术语表：{item!r}")
                    continue
                terms.append({key: item[key].strip() for key in ("term", "en", "plain", "first")})
        info = LessonInfo(lesson.id, title, lesson.rel, lesson.stage, stations, rules, terms,
                          lesson.ok, lesson.error)
        model.lessons.append(info)
        info.closing = check_closing(model, lesson)
        rules_path = lesson.folder / "rules.md"
        if not rules_path.exists():
            if rules:
                model.note("第 {} 课没有 rules.md，它的规则 {} 没有卡片。".format(lesson.id, "、".join(rules)))
            continue
        try:
            text = rules_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            model.note(TEXT["unreadable"].format(path=lesson.rel + "/rules.md", reason=type(exc).__name__))
            continue
        if "\r" in text:
            model.note(f"{lesson.rel}/rules.md 里有 Windows 换行（CR），卡片照原样抄进了手册。")
        parsed = {card.id: card for card in rulecards.parse_cards(text)}
        blocks, stray = card_blocks(text)
        for extra in stray:
            model.note(f"{lesson.rel}/rules.md 里卡片后面还有不属于任何卡片的内容，没有收进手册：「{extra[:60]}」")
        for rule_id, title, heading, raw in blocks:
            card = parsed.get(rule_id)
            fields = card.fields if card is not None else {}
            model.cards.append(Card(rule_id, title, heading, raw, fields, info, lesson.rel + "/rules.md"))
        ids = [block[0] for block in blocks]
        for rule_id in rules:
            if rule_id not in ids:
                model.note(f"第 {lesson.id} 课：META[\"rules\"] 里有 {rule_id}，但 rules.md 里没有它的卡片。")
        for rule_id in ids:
            if rule_id not in rules:
                model.note(f"第 {lesson.id} 课：rules.md 里有 {rule_id} 的卡片，但 META[\"rules\"] 里没有它。")
    return model


# ---------------------------------------------------------------------------
# Checks of the cards (reported, never fixed)
# ---------------------------------------------------------------------------
def expected_rules():
    """``{rule id: (lesson id, plan hint)}`` of plan section 4 (``courselib.syllabus``)."""
    expected = {}
    for entry in syllabus.LESSONS:
        for rule_id, hint in entry["rules"].items():
            expected[rule_id] = (entry["id"], hint)
    return expected


def chapter_of(family):
    for chapter in CHAPTERS:
        if family in chapter[1]:
            return chapter
    return None


def chosen_cards(model, today):
    """The one card per rule id that goes into the handbook, sorted by chapter and id.

    Reports duplicates, missing ids, unknown families, card problems and labels
    that differ from the accepted ones.
    """
    expected = expected_rules()
    by_id = {}
    for card in model.cards:
        by_id.setdefault(card.id, []).append(card)
    chosen = {}
    for rule_id, cards in by_id.items():
        owner = expected.get(rule_id, (None, None))[0]
        pick = next((card for card in cards if card.lesson.id == owner), cards[0])
        chosen[rule_id] = pick
        if len(cards) > 1:
            model.note("{} 有 {} 张卡片（{}）；手册只收了 {} 里的那一张。".format(
                rule_id, len(cards), "、".join(card.rel for card in cards), pick.rel))
        if owner and pick.lesson.id != owner:
            model.note(f"{rule_id} 的卡片在第 {pick.lesson.id} 课，建课计划第 4 节把它排在第 {owner} 课。")
        if chapter_of(pick.family) is None:
            model.note(f"{rule_id} 的类别 {pick.family} 不属于手册的任何一章，没有收进手册。")
    for rule_id, (owner, _hint) in expected.items():
        if rule_id not in chosen:
            model.note(f"{rule_id}（第 {owner} 课）没有卡片，手册、规范地图和行规笔记里都缺它。")
    for rule_id, card in chosen.items():
        if rule_id not in expected:
            model.note(f"{rule_id} 不在建课计划第 4 节的 30 个编号里（卡片在 {card.rel}）。")
    for card in chosen.values():
        if not card.parsed:
            model.note(f"{card.id}（{card.rel}）读不出字段，手册照原样收了它，表里的约束力和规则类型写成「—」。")
            continue
        parsed = rulecards.Card(card.id, card.title, card.parsed, 0)
        problems = rulecards.check_card(parsed, card.lesson.id, today) + rulecards.binding_problems(parsed)
        for problem in problems:
            model.note(f"{card.id}（{card.rel}）：{problem}")
        hint = expected.get(card.id, (None, {}))[1] or {}
        family = hint.get("kind")
        if family and card.kind and not rulecards.family_allows(family, card.kind):
            model.note(f"{card.id} 的规则类型是「{card.kind}」，建课计划第 4 节和 courselib/syllabus.py（含 COMMON 第 7 节认可的标签）"
                       f"写的是「{family}」。")
        if not binding_pairs(card):
            model.note(f"{card.id} 的约束力里找不到「必须 / 推荐 / 参考（适用范围：……）」，表里写成「—」。")
    return sorted((card for card in chosen.values() if chapter_of(card.family) is not None),
                  key=lambda card: (CHAPTERS.index(chapter_of(card.family)),
                                    chapter_of(card.family)[1].index(card.family), card.number, card.id))


def binding_pairs(card):
    """``[(level, scope)]`` of the card's 约束力, in the card's order."""
    return [(match.group(1), match.group(2).strip())
            for match in _BINDING_PAIR.finditer(card.parsed.get("约束力", ""))]


def binding_short(card):
    """约束力 the way the tables write it: 「必须（本课程）；推荐（所有项目）」."""
    pairs = binding_pairs(card)
    if not pairs:
        return "—"
    return "；".join(f"{level}（{scope}）" for level, scope in pairs)


# ---------------------------------------------------------------------------
# Small Markdown helpers
# ---------------------------------------------------------------------------
def cell(text):
    """Text for a table cell: one line, pipes escaped, nothing read as an HTML tag."""
    text = " ".join(str(text).split())
    text = text.replace("|", "\\|")
    return _TAGLIKE.sub("&lt;", text)


def anchor(heading):
    """The anchor GitHub and VS Code give a heading: lower case, punctuation dropped, spaces to -."""
    out = []
    for char in heading.strip().lower():
        if char == " ":
            out.append("-")
        elif char in "-_" or unicodedata.category(char)[0] in "LMN":
            out.append(char)
    return "".join(out)


def card_link(card, base):
    chapter = chapter_of(card.family)
    if chapter is None:
        return ""
    return "{}{}#{}".format(base, chapter[0], anchor(f"{card.id} {card.title}"))


def lesson_link(lesson, base):
    return f"{base}{lesson.rel}/lesson.md"


def table(head, rows):
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def course_order(model, cards):
    """``cards`` in learning order: by lesson, then as they stand in its rules.md."""
    order = {lesson.id: index for index, lesson in enumerate(model.lessons)}
    position = {id(card): index for index, card in enumerate(model.cards)}
    return sorted(cards, key=lambda card: (order.get(card.lesson.id, len(order)),
                                           position.get(id(card), 0)))


# ---------------------------------------------------------------------------
# The generated parts
# ---------------------------------------------------------------------------
def chapter_text(cards, chapter, model):
    mine = [card for card in cards if card.family in chapter[1]]
    if not mine:
        model.note(f"手册第 {chapter[0][:2]} 章（{chapter[0]}）里一张卡片也没有。")
        return "## 这一类的卡片\n\n还没有卡片。\n"
    parts = [f"## 这一类的卡片（{len(mine)} 张）\n"]
    for card in mine:
        parts.append("\n" + card.raw)
        parts.append(f"\n> 原文在第 {card.lesson.id} 课「{card.lesson.title}」的 [`rules.md`](../{card.rel})。\n")
    return "".join(parts)


def index_text(cards, model):
    chapters = []
    for file_name, families, title, _intro in CHAPTERS:
        ids = [card.id for card in cards if card.family in families]
        chapters.append([f"[{cell(title)}]({file_name})", cell("、".join(families)),
                         cell("、".join(ids) or "—")])
    rows = []
    for card in course_order(model, cards):
        rows.append([card.id, cell(card.title), cell(binding_short(card)), cell(card.kind or "—"),
                     "[{}]({})".format(card.lesson.id, lesson_link(card.lesson, "../")),
                     "[卡片]({})".format(card_link(card, ""))])
    return ("## 各章\n\n" + table(["章", "类别", "规则"], chapters)
            + f"\n## 全部规则（按上课顺序）\n\n一共 {len(cards)} 条。\n\n"
            + table(["编号", "标题", "约束力", "规则类型", "哪一课", "链接"], rows))


def standards_table(cards, model, refs):
    rows = []
    for card in course_order(model, cards):
        if refs is None:
            where = "—"
        elif card.id not in refs:
            where = "—"
            model.note(f"{CATALOGUE_REFS} 里没有 {card.id}，规范地图第 3 节的「目录里的出处」写成「—」。")
        else:
            value = refs[card.id]
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                model.note(f"{CATALOGUE_REFS} 里 {card.id} 的值不是编号列表（{value!r}），写成「—」。")
                value = []
            where = "、".join(value) or "—"
        rows.append([card.id, cell(card.title), cell(card.kind or "—"), cell(binding_short(card)),
                     card.lesson.id, cell(where)])
    return table(["编号", "标题", "规则类型", "约束力", "哪一课", "目录里的出处"], rows)


def read_refs(model):
    path = model.root / CATALOGUE_REFS
    if not path.exists():
        model.note(f"没有 {CATALOGUE_REFS}：规范地图第 3 节「目录里的出处」一栏全部写成「—」。")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        model.note(f"读不了 {CATALOGUE_REFS}（{type(exc).__name__}）：「目录里的出处」一栏全部写成「—」。")
        return None
    if not isinstance(data, dict):
        model.note(f"{CATALOGUE_REFS} 不是 {{编号: [目录条目]}} 的格式：「目录里的出处」一栏全部写成「—」。")
        return None
    known = {rule_id for rule_id in expected_rules()}
    for rule_id in data:
        if rule_id not in known:
            model.note(f"{CATALOGUE_REFS} 里的 {rule_id} 不是建课计划第 4 节的编号，没有用到。")
    return data


def closing_minutes(lesson_id):
    """The fixed rule of COMMON section 1, used only when a lesson has no closing heading."""
    return CLOSING_MINUTES_LATE if syllabus.lesson_key(lesson_id) >= CLOSING_LATE_FROM else CLOSING_MINUTES


def lesson_closing(lesson):
    """The closing minutes of ``lesson``: its heading's number, else the fixed rule."""
    closing = getattr(lesson, "closing", None)
    return closing if closing is not None else closing_minutes(lesson.id)


def stage_gates(stage):
    """The gates whose landing lesson is in ``stage``, in syllabus order."""
    return [gate for gate, data in syllabus.GATES.items()
            if syllabus.lesson_key(data["after"])[0] == stage]


def format_hours(half_hours):
    whole, half = divmod(half_hours, 2)
    return f"{whole}.5" if half else str(whole)


def stage_hours(model, stage):
    """The hours of a stage by plan G5a and COMMON section 1, as a dict.

    Station minutes, plus the closing steps of each lesson, plus for each gate
    the minutes of one sitting (``exam`` prints them: the tasks of one sitting
    of an empty state) and ``EXPLAIN_MINUTES`` for its explain-back part; plus
    15 % for reviews; rounded to the nearest half hour (a tie rounds up).
    """
    lessons = [lesson for lesson in model.lessons if lesson.stage == stage]
    stations = sum(s["minutes"] or 0 for lesson in lessons for s in lesson.stations)
    count = sum(len(lesson.stations) for lesson in lessons)
    complete = all(lesson.ok and all(s["minutes"] is not None for s in lesson.stations)
                   for lesson in lessons)
    closing = sum(lesson_closing(lesson) for lesson in lessons)
    gates = []
    for gate in stage_gates(stage):
        summary = progress.gate_status(model.catalog, {}, gate)
        if not summary.tasks:
            model.note(f"{gate} 还没有能用的考题，阶段 {stage} 的小时数里它的实操题按 0 分钟算。")
        gates.append((gate, summary.next_minutes, summary.next_count))
    gate_minutes = sum(minutes + EXPLAIN_MINUTES for _gate, minutes, _count in gates)
    total = stations + closing + gate_minutes
    with_review = Fraction(total) * (1 + REVIEW_SHARE)
    half_hours = math.floor(with_review / 30 + Fraction(1, 2))
    return {"stage": stage, "lessons": lessons, "stations": stations, "station_count": count,
            "closing": closing, "gates": gates, "gate_minutes": gate_minutes, "total": total,
            "with_review": math.floor(with_review + Fraction(1, 2)), "half_hours": half_hours,
            "hours": format_hours(half_hours), "complete": complete}


def spaced(left, word, right):
    """``left + word + right`` with one space only where Chinese meets a Latin letter or digit (plan G2)."""
    def latin(char):
        return char.isascii() and char.isalnum()

    out = left
    for piece in (word, right):
        if out and piece and latin(out[-1]) != latin(piece[0]):
            out += " "
        out += piece
    return out


def hours_sentence(info):
    gates = info["gates"]
    names = [syllabus.gate_name(gate) for gate, _m, _c in gates]
    if len(gates) == 1:
        gate_part = f"{names[0]} 一场的实操题约 {gates[0][1]} 分钟、讲解题约 {EXPLAIN_MINUTES} 分钟"
    elif gates:
        gate_part = "{} 一场的实操题分别约 {} 分钟、讲解题各约 {} 分钟".format(
            spaced("、".join(names[:-1]), "和", names[-1]), "、".join(str(m) for _g, m, _c in gates),
            EXPLAIN_MINUTES)
    else:
        gate_part = ""
    # A lesson whose closing heading names another number is named first; the
    # fixed rule is stated only for the lessons that follow it (ruling 2 of
    # 2026-11-20: closings are calculated, so there may be none).
    rest = [lesson for lesson in info["lessons"] if lesson_closing(lesson) == closing_minutes(lesson.id)]
    late = sum(1 for lesson in rest
               if syllabus.lesson_key(lesson.id) >= CLOSING_LATE_FROM)
    if late == len(rest):
        each = f"每课 {CLOSING_MINUTES_LATE} 分钟"
    elif late:
        each = f"每课 {CLOSING_MINUTES} 分钟，从第 {CLOSING_LATE_FROM[0]}.{CLOSING_LATE_FROM[1]} 课起 {CLOSING_MINUTES_LATE} 分钟"
    else:
        each = f"每课 {CLOSING_MINUTES} 分钟"
    other = [(lesson.id, lesson_closing(lesson)) for lesson in info["lessons"]
             if lesson_closing(lesson) != closing_minutes(lesson.id)]
    if other:
        named = "、".join(f"第 {lesson_id} 课 {minutes} 分钟" for lesson_id, minutes in other)
        each = named + "，其余" + each if rest else named
    sentence = ("阶段 {stage} 一共约 {hours} 小时。这个数是这样算的：{n} 站一共 {stations} 分钟，"
                "加上 {lessons} 课的收尾 {closing} 分钟（{each}）").format(
        stage=info["stage"], hours=info["hours"], n=info["station_count"], stations=info["stations"],
        lessons=len(info["lessons"]), closing=info["closing"], each=each)
    if gate_part:
        sentence += "、" + gate_part
    sentence += ("，合计 {total} 分钟；再加 15% 留给复习，约 {review} 分钟，四舍五入到半小时。"
                 "关卡的分钟是工具在开考前估的数；开考时按抽到的题重算，会差几分钟。").format(
        total=info["total"], review=info["with_review"])
    if not info["complete"]:
        sentence += "有的课读不出站的分钟数，这个数偏小。"
    return sentence


def stage_table(model, stage, cards):
    info = stage_hours(model, stage)
    by_id = {card.id: card for card in cards}
    rows = []
    for lesson in info["lessons"]:
        stations = "；".join("{} {}（{} 分钟）".format(s["id"][-1:], s["title"],
                                                   s["minutes"] if s["minutes"] is not None else "？")
                            for s in lesson.stations) or "（读不出）"
        minutes = sum(s["minutes"] or 0 for s in lesson.stations)
        rules = []
        for rule_id in lesson.rules:
            card = by_id.get(rule_id)
            rules.append("[{}]({})".format(rule_id, card_link(card, "../../handbook/")) if card else rule_id)
        rows.append([lesson.id, cell(lesson.title), cell(stations), str(minutes) if lesson.stations else "？",
                     "、".join(rules) or "无",
                     "[lesson.md]({})".format(lesson.rel.split("/", 2)[-1] + "/lesson.md")])
    text = table(["课", "标题", "各站", "站的分钟", "本课行规", "课文"], rows)
    return text + "\n" + hours_sentence(info) + "\n", info


def glossary_text(model):
    """The table of every TERMS entry (first occurrence wins) and the English index."""
    entries, seen = [], {}
    for lesson in model.lessons:
        station_ids = [s["id"] for s in lesson.stations]
        ordered = []
        for position, term in enumerate(lesson.terms):
            if term["first"] in station_ids:
                key = station_ids.index(term["first"])
            else:
                key = len(station_ids)
                model.note("第 {} 课的术语「{}」：first 是 {}，不是这一课的站。".format(
                    lesson.id, term["term"], term["first"]))
            ordered.append((key, position, term))
        for _key, _position, term in sorted(ordered, key=lambda item: (item[0], item[1])):
            name = term["term"]
            if name in seen:
                first_lesson, first = seen[name]
                differs = [label for key, label in (("en", "英文"), ("plain", "大白话"))
                           if first[key] != term[key]]
                model.note("术语「{}」在第 {} 课（{}）和第 {} 课（{}）都列了，术语表只留第一次出现的那一条{}。".format(
                    name, first_lesson.id, first["first"], lesson.id, term["first"],
                    "；两处的" + "和".join(differs) + "不一样" if differs else ""))
                continue
            seen[name] = (lesson, term)
            entries.append((lesson, term))
    by_en = {}
    for lesson, term in entries:
        by_en.setdefault(term["en"], []).append((lesson, term))
    for group in by_en.values():
        if len(group) > 1:
            model.note("英文「{}」对应几个不同的中文术语：{}。".format(
                group[0][1]["en"], "、".join("{}（{}）".format(t["term"], t["first"]) for _l, t in group)))
    register_report(entries, model)
    rows = [[cell(term["term"]), cell(term["en"]), cell(term["plain"]),
             "[{}]({})".format(term["first"], lesson_link(lesson, ""))] for lesson, term in entries]

    def sort_key(item):
        english = item[1]["en"].casefold()
        stripped = english.lstrip("._-·`' ")
        return (stripped or english, item[1]["term"])

    index = [[cell(term["en"]), cell(term["term"]), term["first"]]
             for lesson, term in sorted(entries, key=sort_key)]
    return (f"## 术语（按上课顺序）\n\n一共 {len(entries)} 个。\n\n"
            + table(["术语", "English", "大白话", "第一次出现"], rows)
            + "\n## 英文索引\n\n按英文字母排；开头的点（比如 `.gitignore` 的点）不算。\n\n"
            + table(["English", "术语", "第一次出现"], index))


#: Plan section 5a, the register: (term, English, plain wording).
REGISTER = (
    ("终端", "terminal", "用打字而不是点鼠标来指挥电脑的窗口"),
    ("命令", "command", "在终端里敲的一行指令"),
    ("路径", "path", "文件在电脑里的地址"),
    ("仓库", "repository", "被 Git 管着的文件夹"),
    ("提交", "commit", "拍一次快照并写一句说明"),
    ("暂存区", "staging area", "准备拍进下一张快照的改动"),
    ("远程仓库", "remote", "放在别处的另一份仓库"),
    (".gitignore", ".gitignore", "给 Git 的“不拍名单”"),
    ("README", "README", "项目的门面和说明书"),
)


def _same_text(left, right):
    return re.sub(r"[\s\"“”「」]", "", left) == re.sub(r"[\s\"“”「」]", "", right)


def register_report(entries, model):
    """Report where the glossary differs from the register of plan section 5a."""
    for term, english, plain in REGISTER:
        hits = [(lesson, t) for lesson, t in entries
                if t["term"] == term or t["en"] == english]
        if not hits:
            model.note(f"登记表（计划 5a）里的「{term}」（{english}）不在任何一课的 TERMS 里。")
            continue
        for lesson, t in hits:
            problems = []
            if t["term"] != term:
                problems.append("术语写成「{}」".format(t["term"]))
            if t["en"] != english:
                problems.append("英文写成「{}」".format(t["en"]))
            squeezed = re.sub(r"[\s\"“”「」]", "", t["plain"])
            if not squeezed.startswith(re.sub(r"[\s\"“”「」]", "", plain)):
                problems.append("大白话是「{}」".format(t["plain"]))
            if problems:
                model.note("和登记表（计划 5a）不一致：「{}」（{}）登记的大白话是「{}」；第 {} 课（{}）{}。".format(
                    term, english, plain, lesson.id, t["first"], "，".join(problems)))


# ---------------------------------------------------------------------------
# notes/my-rules.md
# ---------------------------------------------------------------------------
NOTES_HEAD = (
    "# 我的行规笔记\n\n"
    "每学完一课，在这一课每条行规的小标题下面，用自己的话写一两句，再配一个你自己的例子。\n\n"
    "小标题不要改：第 1.16 课的检查按小标题找你写的话。完整的卡片在 `handbook/` 里。\n\n"
    "这个文件是你的，课程不会覆盖它。\n"
)


def notes_text(model, cards):
    """The skeleton: a title, three lines, a heading per lesson and per rule.

    Each heading is followed by one empty line, the form that
    ``tools/dev/make_sim_home.py`` (``rules_notes_skeleton``) copies into a
    simulation home, so the skeleton is a fixed point of that function.
    """
    by_lesson = {}
    for card in cards:
        by_lesson.setdefault(card.lesson.id, []).append(card)
    lines = [NOTES_HEAD.rstrip("\n"), ""]
    for lesson in model.lessons:
        mine = by_lesson.get(lesson.id)
        if not mine:
            continue
        lines += [f"## {lesson.id} {lesson.title}", ""]
        order = [card.id for card in model.cards if card.lesson.id == lesson.id]
        for card in sorted(mine, key=lambda c: order.index(c.id) if c.id in order else 99):
            lines += [card.heading, ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def is_skeleton(text):
    """True when no line below the first 「## 」 heading is anything but a heading or blank."""
    lines = text.splitlines()
    first = next((i for i, line in enumerate(lines) if line.startswith("## ")), len(lines))
    return all(not line.strip() or line.lstrip().startswith("#") for line in lines[first:])


def heading_lines(text):
    return [line.rstrip() for line in text.splitlines() if line.startswith("#")]


def notes_differences(text, expected):
    """Plain sentences on the headings of ``text`` that differ from ``expected``."""
    have, want = heading_lines(text), heading_lines(expected)
    out = []
    missing = [line for line in want if line not in have]
    extra = [line for line in have if line not in want and line.startswith("##")]
    for line in missing:
        out.append(f"notes/my-rules.md 里少了小标题「{line}」")
    for line in extra:
        out.append(f"notes/my-rules.md 里的小标题「{line}」在现在的卡片里没有（可能是卡片的标题改了）")
    if not missing and not extra and [l for l in have if l in want] != want:
        out.append("notes/my-rules.md 的小标题顺序和课的顺序不一样")
    return out


# ---------------------------------------------------------------------------
# Splicing generated text into files
# ---------------------------------------------------------------------------
class Refusal(Exception):
    """A file cannot be updated safely; the message says why."""


def splice_marker(old, generated, initial):
    """The new text of a marker file (``old`` is None when it does not exist)."""
    if old is None:
        return initial.rstrip("\n") + "\n\n" + MARKER + "\n\n" + generated
    lines = old.split("\n")
    hits = [i for i, line in enumerate(lines) if line.strip() == MARKER]
    if not hits:
        raise Refusal(TEXT["no_marker"].format(marker=MARKER))
    if len(hits) > 1:
        raise Refusal(TEXT["two_markers"].format(n=len(hits)))
    head = "\n".join(lines[:hits[0] + 1])
    return head + "\n\n" + generated


def regions(text):
    """``[(begin line index, end line index)]`` of the regions in ``text``."""
    lines = text.split("\n")
    found, start = [], None
    for index, line in enumerate(lines):
        if line.strip() == BEGIN:
            if start is not None:
                raise Refusal(TEXT["region_nested"].format(line=index + 1))
            start = index
        elif line.strip() == END:
            if start is None:
                raise Refusal(TEXT["region_stray_end"].format(line=index + 1))
            found.append((start, index))
            start = None
    if start is not None:
        raise Refusal(TEXT["region_unclosed"].format(line=start + 1))
    return found


def splice_regions(old, generated):
    """Replace the inside of every region of ``old`` with ``generated``."""
    spans = regions(old)
    if not spans:
        raise Refusal(TEXT["region_none"])
    lines = old.split("\n")
    body = generated.rstrip("\n").split("\n")
    out, position = [], 0
    for begin, end in spans:
        out += lines[position:begin + 1] + body
        position = end
    out += lines[position:]
    return "\n".join(out)


def write_atomic(path, text):
    """Write ``text`` to ``path`` through a temporary file in the same folder."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = None
    if path.exists():
        mode = path.stat().st_mode & 0o777
    handle, temp = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        if mode is None:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
        os.chmod(temp, mode)
        os.replace(temp, str(path))
    except BaseException:
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# The plan of one run
# ---------------------------------------------------------------------------
def build(root, today):
    """``(model, targets, extras)``.

    ``targets`` is a list of ``(relative path, new text or None, refusal or
    "", created)``; ``extras`` holds the stage hours and the notes text.
    """
    model = read_model(root)
    cards = chosen_cards(model, today)
    root = Path(root)
    targets = []

    def marker_target(rel, generated):
        path = root / rel
        try:
            old = path.read_text(encoding="utf-8") if path.exists() else None
        except (OSError, UnicodeDecodeError) as exc:
            targets.append((rel, None, TEXT["unreadable"].format(path=rel, reason=type(exc).__name__), False))
            return
        try:
            targets.append((rel, splice_marker(old, generated, INITIAL[rel]), "", old is None))
        except Refusal as exc:
            targets.append((rel, None, str(exc), False))

    for file_name, _families, _title, _intro in CHAPTERS:
        rel = HANDBOOK + "/" + file_name
        marker_target(rel, chapter_text(cards, chapter_of(_families[0]), model))
    marker_target(HANDBOOK_INDEX, index_text(cards, model))
    marker_target(GLOSSARY, glossary_text(model))
    if not (root / HOW_TO_READ).exists():
        model.note(f"{HOW_TO_READ} 不存在：它是手写的，工具不生成它，但手册的索引链接到它。")
    count = {}
    for card in cards:
        count[card.id] = count.get(card.id, 0) + 1
    for rule_id in expected_rules():
        if count.get(rule_id, 0) != 1:
            model.note(f"{rule_id} 在手册里出现了 {count.get(rule_id, 0)} 次（应该正好 1 次）。")

    refs = read_refs(model)
    region_files = [STANDARDS] + sorted(
        p.relative_to(root).as_posix() for p in root.glob("stages/*/README.md"))
    hours = {}
    for rel in region_files:
        path = root / rel
        if not path.exists():
            if rel == STANDARDS:
                targets.append((rel, None, TEXT["unreadable"].format(path=rel, reason="不存在"), False))
            continue
        try:
            old = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            targets.append((rel, None, TEXT["unreadable"].format(path=rel, reason=type(exc).__name__), False))
            continue
        match = STAGE_PAGE.match(rel)
        if rel == STANDARDS:
            generated = standards_table(cards, model, refs)
        elif match and int(match.group(1)) in syllabus.STAGES:
            generated, info = stage_table(model, int(match.group(1)), cards)
            hours[info["stage"]] = info
        else:
            if BEGIN in old:
                targets.append((rel, None, TEXT["region_unknown"], False))
            continue
        try:
            targets.append((rel, splice_regions(old, generated), "", False))
        except Refusal as exc:
            targets.append((rel, None, str(exc), False))
    for stage in syllabus.STAGES:
        if stage not in hours:
            hours[stage] = stage_hours(model, stage)
            model.note("stages/{}/README.md 里没有生成区，阶段 {} 的课表没有写进去。".format(
                syllabus.STAGES[stage]["folder"], stage))
    return model, targets, {"hours": hours, "notes": notes_text(model, cards)}


def notes_status(root, expected):
    """``(kind, lines)``: kind is missing / skeleton-same / skeleton-stale / learner."""
    path = Path(root) / NOTES
    if not path.exists():
        return "missing", []
    text = path.read_text(encoding="utf-8")
    if is_skeleton(text):
        return ("skeleton-same" if text == expected else "skeleton-stale"), notes_differences(text, expected)
    return "learner", notes_differences(text, expected)


def run(root, mode, out):
    import datetime

    today = datetime.date.today()
    model, targets, extras = build(root, today)
    root = Path(root)
    code = 0
    stale = []
    for rel, text, refusal, created in targets:
        if refusal:
            out(TEXT["refused"].format(path=rel, why=refusal))
            code = 2
            continue
        path = root / rel
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old == text:
            if mode == "write":
                out(TEXT["current"].format(path=rel))
            continue
        if mode == "check":
            stale.append(rel)
            out(TEXT["stale"].format(path=rel, prog=PROG))
            continue
        if mode == "write":
            try:
                write_atomic(path, text)
            except OSError as exc:
                out(TEXT["write_failed"].format(path=rel, reason=type(exc).__name__))
                code = 2
                continue
            out(TEXT["created" if created else "written"].format(path=rel))

    notes_kind, notes_lines = notes_status(root, extras["notes"])
    if mode == "notes":
        if notes_kind in ("missing", "skeleton-stale"):
            write_atomic(root / NOTES, extras["notes"])
            out(TEXT["notes_created" if notes_kind == "missing" else "notes_rewritten"])
        elif notes_kind == "skeleton-same":
            out(TEXT["notes_same"])
        else:
            out(TEXT["notes_kept"])
            for line in notes_lines:
                out("  " + line)
            if not notes_lines:
                out("  " + TEXT["notes_heading_ok"])
    else:
        if notes_kind == "missing":
            out(TEXT["notes_missing_file"].format(prog=PROG))
        elif notes_kind == "skeleton-stale":
            out(TEXT["notes_stale"].format(prog=PROG))
            if mode == "check":
                stale.append(NOTES)
        elif notes_kind == "learner" and notes_lines:
            out(TEXT["notes_kept"])
            for line in notes_lines:
                out("  " + line)

    if mode == "check" and code == 0:
        if stale:
            out(TEXT["some_stale"].format(n=len(stale)))
            code = 1
        else:
            out(TEXT["all_current"].format(n=len(targets)))
    for stage in sorted(extras["hours"]):
        info = extras["hours"][stage]
        out(TEXT["stage_hours"].format(stage=stage, hours=info["hours"], stations=info["stations"],
                                       closing=info["closing"], gates=info["gate_minutes"],
                                       total=info["total"], with_review=info["with_review"]))
    out("")
    if model.report:
        out(TEXT["report_head"])
        for line in model.report:
            out("- " + line)
    else:
        out(TEXT["report_none"])
    return code


def main(argv=None, out=None):
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Generate the handbook, the glossary, the rules table of STANDARDS.md and the "
                    "lesson tables of the stage pages from the lessons (builders only).")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true",
                       help="write nothing; exit 1 and name each file whose generated part is out of date")
    group.add_argument("--notes", action="store_true",
                       help="create notes/my-rules.md, or rewrite it while it is still a skeleton; "
                            "a file the learner has written in is never changed")
    parser.add_argument("--root", default=None,
                        help="workspace to read and write (default: the one this script belongs to)")
    args = parser.parse_args(argv)
    if out is None:
        def out(line):
            sys.stdout.write(line + "\n")
    mode = "check" if args.check else ("notes" if args.notes else "write")
    root = Path(os.path.realpath(args.root)) if args.root else WORKSPACE
    return run(root, mode, out)


if __name__ == "__main__":
    sys.exit(main())
