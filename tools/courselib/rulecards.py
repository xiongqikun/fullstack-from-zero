"""Rule cards in a lesson's ``rules.md`` (plan I2) and the labels of plan G3.

A card starts with a level-3 heading that carries the rule id and the rule's
name, and ends at the next heading of level 1 to 3.  Its body is a list of
thirteen bold-labelled fields; two lines carry a second label after a
full-width semicolon::

    ### GIT-03 提交前先看改了什么

    - **约束力**：必须（适用范围：所有项目）
    - **规则类型**：惯例·平台与工具
    - **规则**：提交前先用 git diff --staged 看一遍要提交的改动。
    - **谁说的**：Pro Git 第 2 版 2.2 节 https://git-scm.com/book/zh/v2/…
    - **核对日期**：2026-11-19；**复核周期**：12 个月
    - **谁来管**：评审人；**不遵守的后果**：把不想要的改动带进历史。
    - **为什么**：……
    - **正例**：……
    - **反例**：……
    - **怎么检查**：……
    - **例外**：无
    - **旧教程提醒**：无
    - **学于**：1.7

A field's value runs until the next bold label, so 正例 and 反例 may hold an
indented code block over several lines.

The two axes of plan G3 are kept apart: **约束力** (必须 / 推荐 / 参考, with a
scope in brackets) says how strongly the rule applies here; **规则类型** (one
label, see ``TYPES``) says who wrote it.  ``check_card`` turns a parsed card
into a list of problems; ``validate`` reports them.
"""

import datetime
import re

RULE_ID = re.compile(r"^[A-Z][A-Z0-9]{1,7}-\d{2}$")

#: The thirteen fields of plan I2, in the order a card lists them.
FIELDS = ("约束力", "规则类型", "规则", "谁说的", "核对日期", "谁来管", "为什么",
          "正例", "反例", "怎么检查", "例外", "旧教程提醒", "学于")
#: Second labels on the lines of 核对日期 and 谁来管; also mandatory.
SUBFIELDS = ("复核周期", "不遵守的后果")
ALL_FIELDS = FIELDS + SUBFIELDS

#: 约束力 (plan G3): the level, then the scope in brackets.
LEVELS = ("必须", "推荐", "参考")
SCOPES = ("本课程", "本机", "所在团队", "所有项目")

#: 规则类型 (plan G3).  个人偏好 exists as a word but is never the type of a card;
#: 规范·本课程约定 is how the course writes 规范·团队约定 for its own choices;
#: 岗位期望 is the separate label for what employers expect (instead of 行业要求).
TYPES = ("标准", "行业要求", "岗位期望", "惯例·事实标准", "惯例·平台与工具",
         "规范·组织", "规范·团队约定", "规范·本课程约定")
NOT_A_RULE = "个人偏好"
#: Types whose 谁说的 may name this course or team instead of a public web page.
LOCAL_TYPES = ("规范·团队约定", "规范·本课程约定")

#: The families that plan section 4 gives in brackets after a rule id, and the
#: types each family allows.  A family that is a full type allows only itself.
FAMILIES = {
    "惯例": ("惯例·事实标准", "惯例·平台与工具"),
    "规范": ("规范·组织", "规范·团队约定", "规范·本课程约定"),
}

_HEADING = re.compile(r"^###[ \t]+([A-Z][A-Z0-9]*-\d+)(?:[ \t]+(.*))?$", re.MULTILINE)
_ANY_HEADING = re.compile(r"^#{1,3}[ \t]+\S", re.MULTILINE)
_FIELD = re.compile(r"\*\*({})\*\*[ \t]*[：:]".format("|".join(ALL_FIELDS)))
_PLAIN_FIELD = re.compile(r"^[ \t]*[-*][ \t]+({})[ \t]*[：:]".format("|".join(FIELDS)),
                          re.MULTILINE)
_TRAILING = (re.compile(r"\s*[｜|；;，,]\s*$"), re.compile(r"\n[ \t]*[-*][ \t]*$"))
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_URL = re.compile(r"https?://\S+")
_SCOPE = re.compile(r"[（(]\s*适用范围\s*[：:]\s*([^）)]*)[）)]")
_DOTS = ("・", "•", "‧", "∙", "⋅", "．", ".", "-", "—", " ")
_VAGUE = ("todo", "tbd", "fixme", "xxx", "待补", "待定", "待查", "待核实", "？？", "??", "……", "...")

# ---------------------------------------------------------------------------
# Every user-visible string of this module (problems found on a card).
# ---------------------------------------------------------------------------
TEXT = {
    "no_title": "标题里没有规则名（要写成：### {id} 一句话规则名）",
    "bad_id": "编号写法不对，要像 GIT-03：大写字母、短横线、两位数字",
    "missing": "缺少「{name}」。这一行要写成：{example}",
    "plain_labels": "字段名没有加粗：要写成 - **约束力**：……（两个星号包住字段名）",
    "placeholder": "「{name}」还是占位内容：「{value}」",
    "level": "约束力要以 {levels} 之一开头，现在是「{value}」",
    "scope_missing": "约束力后面要用括号写明适用范围，例如：必须（适用范围：所有项目）",
    "scope_bad": "适用范围要是 {scopes} 中的一个或几个（用顿号隔开），现在是「{value}」",
    "type_preference": "个人偏好不是规则，不能做规则卡的规则类型；真是个人偏好，就在课文里直说，不写成卡片",
    "type_bad": "规则类型要正好是这几个之一：{types}；现在是「{value}」",
    "type_dot": "规则类型里的间隔号要用「·」（U+00B7），现在是「{value}」",
    "source_url": "谁说的要写名称、版本或日期和网址；这张卡的类型是{kind}，但没有找到网址",
    "date_bad": "核对日期要写成 YYYY-MM-DD，现在是「{value}」",
    "date_future": "核对日期 {date} 在今天之后",
    "learned_bad": "学于要写引入这条规则的课程编号 {lesson}，现在是「{value}」",
    "clause_scope": ("约束力里的每一个「必须 / 推荐 / 参考」后面都要紧跟括号写明适用范围，"
                     "例如「必须（适用范围：本课程）；推荐（适用范围：所有项目）」；"
                     "「{word}」后面没有。现在是「{value}」"),
}

#: How each field's line looks, for the "missing" message.
EXAMPLES = {
    "约束力": "- **约束力**：必须（适用范围：所有项目）",
    "规则类型": "- **规则类型**：惯例·平台与工具",
    "规则": "- **规则**：（可以照着做的一句话）",
    "谁说的": "- **谁说的**：名称 + 版本或日期 + 网址",
    "核对日期": "- **核对日期**：2026-11-19；**复核周期**：12 个月",
    "复核周期": "- **核对日期**：2026-11-19；**复核周期**：12 个月（或写触发条件）",
    "谁来管": "- **谁来管**：工具；**不遵守的后果**：（一句话）",
    "不遵守的后果": "- **谁来管**：工具；**不遵守的后果**：（一句话）",
    "为什么": "- **为什么**：（两三句，讲后果）",
    "正例": "- **正例**：（可照抄）",
    "反例": "- **反例**：……",
    "怎么检查": "- **怎么检查**：（自检命令或复习题编号；或者“人工检查：……”）",
    "例外": "- **例外**：无",
    "旧教程提醒": "- **旧教程提醒**：无",
    "学于": "- **学于**：1.7",
}


class Card:
    """One rule card: its id, title, labelled fields and heading line number."""

    def __init__(self, rule_id, title, fields, line, plain_labels=False):
        self.id = rule_id
        self.title = title
        self.fields = fields
        self.line = line
        #: True when the body has field names without the bold marks.
        self.plain_labels = plain_labels

    def get(self, name):
        return self.fields.get(name, "")

    @property
    def level(self):
        """必须 / 推荐 / 参考, or "" when the 约束力 line does not start with one."""
        text = self.get("约束力")
        for level in LEVELS:
            if text.startswith(level):
                return level
        return ""

    @property
    def scopes(self):
        """The scopes named in the brackets of 约束力 (may be empty)."""
        match = _SCOPE.search(self.get("约束力"))
        if not match:
            return []
        return [part.strip() for part in re.split(r"[、/／，,]", match.group(1)) if part.strip()]

    @property
    def kind(self):
        """The 规则类型 label with any bracketed remark removed."""
        return type_label(self.get("规则类型"))

    def __repr__(self):
        return f"<Card {self.id} {sorted(self.fields)}>"


def type_label(text):
    """The label part of a 规则类型 value: "惯例·事实标准（EditorConfig）" -> "惯例·事实标准"."""
    text = (text or "").strip()
    for bracket in ("（", "("):
        if bracket in text:
            text = text.split(bracket, 1)[0]
    return text.strip()


def _same_dots(text):
    for dot in _DOTS:
        text = text.replace(dot, "·")
    return text


def _clean(value):
    value = value.strip()
    changed = True
    while changed:
        changed = False
        for pattern in _TRAILING:
            shorter = pattern.sub("", value).rstrip()
            if shorter != value:
                value = shorter
                changed = True
    return value.strip().strip("*").strip()


def parse_cards(text):
    """Return the cards found in the text of a ``rules.md`` file, in order."""
    cards = []
    for match in _HEADING.finditer(text):
        following = _ANY_HEADING.search(text, match.end())
        end = following.start() if following else len(text)
        body = text[match.end():end]
        fields = {}
        marks = list(_FIELD.finditer(body))
        for index, mark in enumerate(marks):
            stop = marks[index + 1].start() if index + 1 < len(marks) else len(body)
            name = mark.group(1)
            if name not in fields:
                fields[name] = _clean(body[mark.end():stop])
        plain = not marks and bool(_PLAIN_FIELD.search(body))
        line = text.count("\n", 0, match.start()) + 1
        cards.append(Card(match.group(1), (match.group(2) or "").strip(), fields, line, plain))
    return cards


def first_date(text):
    """The first YYYY-MM-DD in ``text``, or ""."""
    found = _DATE.search(text or "")
    return found.group(0) if found else ""


def _is_vague(value):
    lowered = value.lower().strip("（）() ")
    if len(lowered) < 1:
        return True
    return any(word in lowered for word in _VAGUE) and len(lowered) <= 12


def family_allows(family, kind):
    """Does the bracket of plan section 4 (``family``) allow the type ``kind``?"""
    return kind in FAMILIES.get(family, (family,))


def check_card(card, lesson_id, today):
    """Problems of one card as a list of Chinese sentences (empty when it is fine).

    ``lesson_id`` is the id of the lesson whose rules.md holds the card;
    ``today`` is a ``datetime.date``.
    """
    problems = []
    if not RULE_ID.match(card.id):
        problems.append(TEXT["bad_id"])
    if not card.title:
        problems.append(TEXT["no_title"].format(id=card.id))
    if card.plain_labels:
        problems.append(TEXT["plain_labels"])
        return problems
    for name in ALL_FIELDS:
        value = card.get(name)
        if not value:
            problems.append(TEXT["missing"].format(name=name, example=EXAMPLES[name]))
        elif name not in ("例外", "旧教程提醒") and _is_vague(value):
            problems.append(TEXT["placeholder"].format(name=name, value=value))

    binding = card.get("约束力")
    if binding:
        if not card.level:
            problems.append(TEXT["level"].format(levels=" / ".join(LEVELS), value=binding))
        if not _SCOPE.search(binding):
            problems.append(TEXT["scope_missing"])
        else:
            bad = [scope for scope in card.scopes if scope not in SCOPES] or (
                [] if card.scopes else [""])
            if bad:
                problems.append(TEXT["scope_bad"].format(scopes=" / ".join(SCOPES),
                                                         value="、".join(card.scopes)))

    kind = card.kind
    if card.get("规则类型"):
        if kind == NOT_A_RULE:
            problems.append(TEXT["type_preference"])
        elif kind not in TYPES:
            if _same_dots(kind) in TYPES:
                problems.append(TEXT["type_dot"].format(value=kind))
            else:
                problems.append(TEXT["type_bad"].format(types=" / ".join(TYPES), value=kind))

    source = card.get("谁说的")
    if source and kind in TYPES and kind not in LOCAL_TYPES and not _URL.search(source):
        problems.append(TEXT["source_url"].format(kind=kind))

    checked = card.get("核对日期")
    if checked:
        when = _to_date(first_date(checked))
        if when is None or not checked.startswith(first_date(checked)):
            problems.append(TEXT["date_bad"].format(value=checked))
        elif when > today:
            problems.append(TEXT["date_future"].format(date=when.isoformat()))

    learned = card.get("学于")
    if learned and lesson_id and not re.match(re.escape(lesson_id) + r"(?![0-9])",
                                              learned.strip()):
        problems.append(TEXT["learned_bad"].format(lesson=lesson_id, value=learned))
    return problems


def _outside_brackets(text):
    """``text`` with every bracketed part replaced by spaces (same length)."""
    out, depth = [], 0
    for char in text:
        if char in "（(":
            depth += 1
            out.append(" ")
        elif char in "）)" and depth:
            depth -= 1
            out.append(" ")
        else:
            out.append(" " if depth else char)
    return "".join(out)


def binding_problems(card):
    """Wording problems of 约束力 that ``check_card`` lets through (warnings).

    Every level word (必须 / 推荐 / 参考) outside brackets must be followed
    directly by its scope 「（适用范围：……）」, so 「必须（适用范围：本课程）；推荐（适用范围：
    所有项目）」 is fine and 「推荐（适用范围：所有项目），本课程里按必须对待」 is not; every
    scope bracket names only scopes of ``SCOPES``.
    """
    text = card.get("约束力")
    if not text or not card.level or not _SCOPE.search(text):
        return []
    problems = []
    plain = _outside_brackets(text)
    for match in re.finditer("|".join(LEVELS), plain):
        rest = text[match.end():].lstrip()
        if not _SCOPE.match(rest):
            problems.append(TEXT["clause_scope"].format(word=match.group(0), value=text))
            break
    for match in list(_SCOPE.finditer(text))[1:]:
        parts = [p.strip() for p in re.split(r"[、/／，,]", match.group(1)) if p.strip()]
        bad = [p for p in parts if p not in SCOPES]
        if bad:
            problems.append(TEXT["scope_bad"].format(scopes=" / ".join(SCOPES), value="、".join(parts)))
    return problems


def _to_date(text):
    try:
        return datetime.date.fromisoformat(text) if len(text) == 10 else None
    except ValueError:
        return None
