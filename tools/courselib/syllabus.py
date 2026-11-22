"""The fixed syllabus of batch 1 (plan section 4), as data.

``validate`` compares every lesson module with this table: folder, station
ids, rule ids and the gate its exam tasks belong to.  ``status`` uses the gates
as landing points.  Lessons that are not in the table (later stages, test
fixtures) only get the general checks.

Changing this file changes the contract of the course: do it only together
with the plan.
"""

# The vocabulary of the norm labels (plan G3) lives in ``rulecards``.

# Names allowed as keys of META["verified"]["tools"].  ``fresh`` compares the
# installed version of each tool with tools/courselib/baseline.json.
TOOL_NAMES = {
    "macos": "macOS（系统版本）",
    "zsh": "zsh（终端里的命令解释器）",
    "python3": "python3",
    "git": "git",
    "code": "VS Code（code 命令）",
    "brew": "Homebrew（brew 命令）",
    "gh": "GitHub CLI（gh 命令）",
    "node": "Node.js",
    "npm": "npm",
    "uv": "uv",
    "ruff": "ruff",
    "sqlite3": "sqlite3",
    "docker": "Docker",
    "less": "less（分页器）",
    "vi": "vi（Git 默认的编辑器）",
    "man": "man（手册命令）",
    "grep": "grep（查找文字的命令）",
    "zip": "zip（打包压缩的命令）",
    "claude-desktop": "Claude 桌面应用",
    "chrome": "Chrome 浏览器",
}

STAGES = {
    0: {"folder": "00-orientation", "title": "起步"},
    1: {"folder": "01-foundations", "title": "工程师的基本功"},
}


def _lesson(lesson_id, folder, title, stations, rules, gate):
    stage = int(lesson_id.split(".")[0])
    return {
        "id": lesson_id,
        "stage": stage,
        "stage_folder": STAGES[stage]["folder"],
        "folder": folder,
        "title": title,
        "stations": [lesson_id + letter for letter in stations],
        # rule id -> what plan section 4 says in brackets after the id:
        # "kind" is the family of the 规则类型 (惯例, 惯例·事实标准, 行业要求 ...;
        # see rulecards.FAMILIES), "level" a 约束力 where the plan names one.
        # Where the audit of the cards (2026-11-19, COMMON section 7) accepted
        # a label that differs from the plan's hint, the accepted label is
        # here: WS-02 规范·组织, DOC-02 规范·本课程约定, REPO-01 惯例·事实标准,
        # HELP-01 惯例·平台与工具, AI-01 规范·组织.
        "rules": dict(rules),
        "gate": gate,
    }


# (id, folder, title, station letters, {rule id: {"kind": family, "level": ...}}, gate)
LESSONS = [
    _lesson("0.1", "01-first-steps", "第一次动手", "abc",
            {"META-01": {"kind": "规范·本课程约定"}}, "gate-0"),
    _lesson("0.2", "02-files-and-paths", "文件、路径和代码的家", "abc",
            {"WS-01": {"kind": "惯例"}, "WS-02": {"kind": "规范·组织"}}, "gate-0"),
    _lesson("0.3", "03-how-software-is-made", "软件是怎么做出来的，规范从哪来", "abc",
            {"META-02": {"kind": "规范·本课程约定"}}, "gate-0"),
    _lesson("0.4", "04-manage-your-learning", "像管项目一样管学习", "abc",
            {"PM-01": {"kind": "惯例"}, "PM-02": {"kind": "惯例"}}, "gate-0"),
    _lesson("1.1", "01-create-and-view", "终端：新建与查看", "ab",
            {"TERM-01": {"kind": "规范·本课程约定"}}, "gate-a"),
    _lesson("1.2", "02-copy-move-delete", "终端：复制、移动、删除", "ab",
            {"TERM-02": {"kind": "规范·本课程约定"}}, "gate-a"),
    _lesson("1.3", "03-search", "终端：查找", "ab",
            {}, "gate-a"),
    _lesson("1.4", "04-editor", "编辑器 VS Code", "abc",
            {"ED-01": {"kind": "惯例"}, "ED-02": {"kind": "惯例·事实标准"}}, "gate-a"),
    _lesson("1.5", "05-markdown-readme", "Markdown 与 README", "ab",
            {"DOC-01": {"kind": "惯例"}, "DOC-02": {"kind": "规范·本课程约定"}}, "gate-a"),
    _lesson("1.6", "06-first-commit", "Git：第一次提交", "abc",
            {"GIT-01": {"kind": "惯例"}, "GIT-02": {"kind": "惯例·平台与工具"}}, "gate-b"),
    _lesson("1.7", "07-read-diff", "Git：看懂改了什么", "ab",
            {"GIT-03": {"kind": "惯例"}}, "gate-b"),
    _lesson("1.8", "08-undo-uncommitted", "Git：后悔药", "ab",
            {"GIT-04": {"kind": "规范·本课程约定"}}, "gate-b"),
    _lesson("1.9", "09-gitignore", "Git：什么不该进仓库", "ab",
            {"REPO-01": {"kind": "惯例·事实标准"}, "REPO-02": {"kind": "惯例"}}, "gate-b"),
    _lesson("1.10", "10-commit-conventions", "提交规范", "ab",
            {"COMMIT-01": {"kind": "惯例·事实标准"}, "COMMIT-02": {"kind": "惯例"}}, "gate-b"),
    _lesson("1.11", "11-github-account", "GitHub：账号、安全与身份", "abc",
            {"ACC-01": {"kind": "行业要求"}, "ACC-02": {"level": "推荐"}}, "gate-1"),
    _lesson("1.12", "12-push-and-backup", "第一次推送和云端备份", "abc",
            {"REMOTE-01": {"kind": "惯例"}, "REMOTE-02": {"kind": "行业要求"}}, "gate-1"),
    _lesson("1.13", "13-publish-site", "把你的网页放到网上", "abc",
            {"PUB-01": {"kind": "惯例"}}, "gate-1"),
    _lesson("1.14", "14-errors-help-fresh", "排错、求助与“与时俱进”", "abc",
            {"HELP-01": {"kind": "惯例·平台与工具"}, "FRESH-01": {"kind": "规范·本课程约定"}}, "gate-1"),
    _lesson("1.15", "15-review-ai-changes", "验收 AI 的改动", "abc",
            {"AI-01": {"kind": "规范·组织"}, "AI-02": {"kind": "惯例"}}, "gate-1"),
    _lesson("1.16", "16-stage-project-and-gate", "阶段作品与验收", "abc",
            {"PM-03": {"kind": "惯例"}}, "gate-1"),
]

BY_ID = {entry["id"]: entry for entry in LESSONS}

# Gates (plan I7, COMMON.md section 1).  ``after`` is the lesson whose
# completion reaches the gate: these are the landing points that ``status``
# counts down to.  ``lessons`` are the lessons the gate covers (one task per
# lesson in a sitting; no gate borrows tasks of another gate, so gate-1 covers
# 1.11 to 1.16, whose tasks also use the skills of the earlier lessons).
GATES = {
    "gate-0": {"title": "起步小关卡", "after": "0.4",
               "lessons": ["0.1", "0.2", "0.3", "0.4"]},
    "gate-a": {"title": "终端与文档关卡", "after": "1.5",
               "lessons": ["1.1", "1.2", "1.3", "1.4", "1.5"]},
    "gate-b": {"title": "本地 Git 关卡", "after": "1.10",
               "lessons": ["1.6", "1.7", "1.8", "1.9", "1.10"]},
    "gate-1": {"title": "阶段 1 验收", "after": "1.16",
               "lessons": [entry["id"] for entry in LESSONS if entry["gate"] == "gate-1"]},
}

#: How a sentence names a gate (COMMON.md section 3): 「小关卡 gate-0 / gate-a /
#: gate-b」 and 「阶段验收 gate-1」.
GATE_KIND_SMALL = "小关卡"
GATE_KIND_STAGE = "阶段验收"
GATE_KIND_OTHER = "关卡"


def gate_kind(gate):
    """「阶段验收」 for gate-1, gate-2 ...; 「小关卡」 for the other gates of the syllabus."""
    if gate not in GATES:
        return GATE_KIND_OTHER
    number = gate[len("gate-"):] if gate.startswith("gate-") else ""
    if number.isdigit() and int(number) >= 1:
        return GATE_KIND_STAGE
    return GATE_KIND_SMALL


def gate_name(gate):
    """The gate as a sentence names it: 「小关卡 gate-b」, 「阶段验收 gate-1」 (else the id)."""
    if gate not in GATES:
        return gate
    return f"{gate_kind(gate)} {gate}"


def _says_kind(gate, title):
    kind = gate_kind(gate)
    return kind in title or (kind == GATE_KIND_STAGE and "验收" in title)


def gate_label(gate):
    """The gate with its title: 「小关卡 gate-b「本地 Git 关卡」」, 「gate-1「阶段 1 验收」」.

    The kind word is left out when the title already says it (起步小关卡,
    阶段 1 验收); a gate outside the syllabus is just its id.
    """
    title = GATES.get(gate, {}).get("title", "")
    if not title:
        return gate
    if _says_kind(gate, title):
        return f"{gate}「{title}」"
    return f"{gate_name(gate)}「{title}」"


def gate_titled(gate):
    """The title alone, with the kind when it does not say it: 「小关卡「终端与文档关卡」」."""
    title = GATES.get(gate, {}).get("title", "")
    if not title:
        return gate_kind(gate)
    return title if _says_kind(gate, title) else f"{gate_kind(gate)}「{title}」"


def lesson_entry(lesson_id):
    """The syllabus row of ``lesson_id``, or None for lessons outside it."""
    return BY_ID.get(lesson_id)


def landing_points():
    """Lesson ids that end at a landing point, mapped to the gate reached."""
    return {gate["after"]: gate_id for gate_id, gate in GATES.items()}


def lesson_key(lesson_id):
    """Sort key for lesson ids: "1.10" comes after "1.9"."""
    parts = str(lesson_id).split(".")
    try:
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return (10 ** 6, 10 ** 6)


def station_key(station_id):
    """Sort key for station ids: "1.10a" comes after "1.9c"."""
    text = str(station_id)
    return lesson_key(text[:-1]) + (text[-1:],)
