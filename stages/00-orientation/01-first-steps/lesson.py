"""Lesson 0.1 第一次动手 (plan section 4).

Stations:
  0.1a  the three things of a study session; intake questionnaire -> learner/profile.md
  0.1b  the terminal: pwd, ls, clear, Ctrl+C
  0.1c  run and change a small program (starter/hello-fx/convert.py)
  收尾   the first journal entry (python3 tools/course.py journal)

The learner edits the workspace's own starter/hello-fx/convert.py (as the
plan row and the stage README say; plan G11a: no later batch rewrites it).
The pristine text of that file is kept here (ORIGINAL_CONVERT), so that the
``start`` scenario can always write an untouched copy into the playground for
comparison, even after the learner has changed or broken the workspace file.
Nothing in this module ever writes to the workspace.

Decision key (tool-api section 6.7): ``hello_fx_amount`` remembers the
amount of the last passed check of 0.1c, so that the cold redo after hint
level 4 asks for a different amount instead of passing on the old edit.

Standard library only, Python 3.9 syntax, no side effects at import time.
"""

import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "0.1",
    "slug": "01-first-steps",
    "title": "第一次动手",
    "stage": 0,
    "prerequisites": [],
    "stations": [
        {
            "id": "0.1a",
            "title": "认识学习界面和导师",
            "minutes": 40,
            "new_concept": "一次学习的三件套：课文、终端、导师",
            "new_commands": [
                "python3 tools/course.py",
                "python3 tools/course.py check",
                "python3 tools/course.py hint",
            ],
        },
        {
            "id": "0.1b",
            "title": "终端三条命令",
            "minutes": 25,
            "new_concept": "终端是一问一答：敲一行命令、按回车，它回一段结果",
            "new_commands": ["pwd", "ls", "clear"],
        },
        {
            "id": "0.1c",
            "title": "运行并改动一个小程序",
            "minutes": 25,
            "new_concept": "程序是一份交给解释器去执行的文本文件",
            "new_commands": [
                "python3 <文件>",
                "code",
                "python3 tools/course.py scenario",
                "python3 tools/course.py journal",
            ],
        },
    ],
    "rules": ["META-01"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9", "code": "1.145.2"},
    },
    "unverified_steps": [
        "0.1a：说“开始上课”以后，导师在 Claude 桌面应用里替学习者打开课文和终端面板（建课时无法操作桌面应用）",
        "0.1a：自己打开终端面板和文件面板：会话最上面的小图标（鼠标停上去显示 Terminal、Files），没有按钮的从 ⋮ 菜单选，"
        "或按 Ctrl+`；要 Claude 桌面应用 v1.2581.0 或更新，版本不够从菜单 Claude > Check for Updates… 更新"
        "（对照 code.claude.com/docs/en/desktop，2026-11-20）",
        "0.1a：导师的状态行和入学问卷由导师完成，建课时无法模拟真实导师",
        "0.1b：按 Ctrl+C 让 dquote> 停下（建课环境没有真正的终端，dquote> 本身已实测）",
        "0.1b：clear 清屏后的样子（clear 发出的指令里包括清除回滚内容，已实测；终端面板怎么显示无法验证）",
        "0.1c：用 code 命令打开 VS Code、信任提示（按钮 Open / Open in Restricted Mode）、Cmd+S 保存、标签页上的圆点、"
        "Cmd+Z 撤销，对照 code.visualstudio.com 的文档和 VS Code 源代码里的对话框文字",
        "0.1c：按 ↑ 键翻出上一条命令（建课环境没有真正的终端）",
    ],
}

TERMS = [
    {"term": "课文", "en": "lesson text",
     "plain": "这门课每一课的文字说明，告诉你一步步做什么", "first": "0.1a"},
    {"term": "导师", "en": "tutor",
     "plain": "按这个工作区的规则当教练的 Claude：给提示，不替你做练习", "first": "0.1a"},
    {"term": "学习工作区", "en": "workspace",
     "plain": "fullstack-from-zero 这个文件夹：课文、工具和你的笔记都在里面", "first": "0.1a"},
    {"term": "终端", "en": "terminal",
     "plain": "用打字而不是点鼠标来指挥电脑的窗口", "first": "0.1a"},
    {"term": "命令", "en": "command",
     "plain": "在终端里敲的一行指令", "first": "0.1a"},
    {"term": "项目文件夹", "en": "project folder",
     "plain": "Claude 桌面应用里一次会话干活的那个文件夹；上课时选 fullstack-from-zero", "first": "0.1a"},
    {"term": "存档点", "en": "save point",
     "plain": "每一站的结尾，到这里可以放心停下，下次从下一站接着学", "first": "0.1a"},
    {"term": "状态行", "en": "status line",
     "plain": "导师每一条回复的第一行，以【教练模式】开头，说明导师读了学习工作区里的规则", "first": "0.1a"},
    {"term": "行规", "en": "lesson rules",
     "plain": "这一课定下、以后一直要守的规矩；每条有编号，完整卡片在本课的 rules.md 里", "first": "0.1a"},
    {"term": "落脚点", "en": "landing point",
     "plain": "学完一段、可以停下回头看的地方，通常是一个关卡；运行 python3 tools/course.py 会告诉你离它还有几站", "first": "0.1a"},
    {"term": "提示符", "en": "prompt",
     "plain": "终端每行开头那段字，以 % 结尾，表示“请讲”", "first": "0.1b"},
    {"term": "报错", "en": "error message",
     "plain": "程序告诉你它没办成、卡在哪里的那段话", "first": "0.1b"},
    {"term": "shell", "en": "shell",
     "plain": "在终端里接你命令、照着执行的程序，中文有时叫命令解释器；你的 Mac 上它叫 zsh", "first": "0.1b"},
    {"term": "程序", "en": "program",
     "plain": "一份写着一步步指令、交给电脑去执行的文本文件", "first": "0.1c"},
    {"term": "解释器", "en": "interpreter",
     "plain": "读程序文件、照着一行行执行的那个软件，比如 python3", "first": "0.1c"},
    {"term": "编辑器", "en": "editor",
     "plain": "写代码和文档用的软件，本课程用的编辑器是 VS Code", "first": "0.1c"},
    {"term": "工作区信任", "en": "Workspace Trust",
     "plain": "VS Code 打开来路不明的文件前先问一句的提示；这里的“工作区”是 VS Code 自己的说法，不是学习工作区", "first": "0.1c"},
    {"term": "标签页", "en": "tab",
     "plain": "VS Code 顶上每个打开的文件占的一个小格子", "first": "0.1c"},
    {"term": "练习场", "en": "playground",
     "plain": "工具专门放练习材料的文件夹（~/Developer/playground），弄坏了也不要紧", "first": "0.1c"},
]


# ---------------------------------------------------------------------------
# The pristine starter program (kept here so it can always be restored)
# ---------------------------------------------------------------------------
ORIGINAL_CONVERT = '''"""汇率换算小程序：把一笔美元换算成人民币，打印一行结果。

运行方式：python3 starter/hello-fx/convert.py
"""

# 可以改的数都放在最上面。
AMOUNT_USD = 100  # 要换算的金额，单位是美元
USD_TO_CNY = 7.10  # 1 美元换多少人民币。这是一个示例数字，不是真实汇率


def main():
    amount_cny = AMOUNT_USD * USD_TO_CNY
    print(f"{AMOUNT_USD} 美元 ≈ {amount_cny:.2f} 人民币（按 1 美元 = {USD_TO_CNY:.2f} 人民币计算）")


if __name__ == "__main__":
    main()
'''

ORIGINAL_RATES = '''# 示例数据：1 美元可以换多少其他货币。数字是为练习编的，不是真实汇率。
# 每行三列，用空格隔开：货币代码  中文名称  1 美元可换的数量
CNY  人民币    7.10
EUR  欧元      0.92
JPY  日元      150.00
GBP  英镑      0.79
HKD  港币      7.80
KRW  韩元      1350.00
SGD  新加坡元  1.34
AUD  澳元      1.52
'''

AMOUNT_LINE = re.compile(r"^\s*AMOUNT_USD\s*=\s*(.*?)\s*(#.*)?$")
RATE_LINE = re.compile(r"^\s*USD_TO_CNY\s*=\s*(.*?)\s*(#.*)?$")
# Half-width digits only: full-width digits look like a number but Python rejects them.
NUMBER = re.compile(r"^[+-]?([0-9][0-9_]*)(\.[0-9]+)?$")


def _cut(text, limit=70):
    """Shorten a message for one line without silently dropping its end."""
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _original_amount():
    for line in ORIGINAL_CONVERT.splitlines():
        found = AMOUNT_LINE.match(line)
        if found:
            return float(found.group(1))
    raise ValueError("ORIGINAL_CONVERT has no AMOUNT_USD line")


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """An untouched copy of starter/hello-fx, written from the text kept here.

    The learner changes the workspace copy in station c; this copy is the
    original to compare with (or to copy back from) if that file got broken.
    """
    sc.write("hello-fx/convert.py", ORIGINAL_CONVERT, exact=True)
    sc.write("hello-fx/rates.txt", ORIGINAL_RATES, exact=True)
    sc.fact("folder", "hello-fx")
    sc.todo("一份没改过的汇率换算小程序：" + sc.show("hello-fx/convert.py"))
    sc.todo("用 VS Code 打开它：code " + sc.show("hello-fx/convert.py"))


SCENARIOS = {"start": build_start}


# ---------------------------------------------------------------------------
# Station 0.1a: learner/profile.md written from the intake questionnaire
# ---------------------------------------------------------------------------
# (key the heading must start with, the heading as templates/profile-template.md
# writes it; COMMON.md section 4 fixes these eight headings)
PROFILE_ITEMS = [
    ("学习目的", "学习目的"),
    ("每周时间", "每周时间与固定时段"),
    ("一次能坐多久", "一次能坐多久"),
    ("英文阅读", "英文阅读"),
    ("github", "GitHub"),
    ("想做的作品", "想做的作品"),
    ("导师严格度", "导师严格度"),
    ("以前用过终端", "以前用过终端吗"),
]

PLACEHOLDER = re.compile(r"^[\s\-*_.。…?？()（）\[\]【】<>＜＞:：]*(待填|待定|todo|tbd|在这里写|填在这里)?[\s\-*_.。…?？()（）\[\]【】<>＜＞:：]*$",
                         re.IGNORECASE)

# A number in front of a heading: "1. ", "1、", "1)", "(1)", "（一）", "一、", "Q1 ", "第1题".
# Chinese numerals count only with a separator after them, so that "一次能坐多久"
# keeps its first character.
NUMBERING = re.compile(
    r"^(?:[(（]\s*(?:\d+|[一二三四五六七八九十]+)\s*[)）]"
    r"|(?:q\s*)?\d+\s*[.、．:：)）]?"
    r"|[一二三四五六七八九十]+\s*[、.．:：)）]"
    r"|第\s*(?:\d+|[一二三四五六七八九十]+)\s*[题项问]\s*[.、．:：]?)\s*")
BOLD_LINE = re.compile(r"^\s{0,3}(\*\*|__)(.+?)\1\s*[:：]?\s*$")


def _heading_key(ctx, title):
    """The heading text as compared with the keys: normalised, without bold
    marks and without a number in front."""
    text = ctx.normalize(title).strip("*_ ").strip()
    text = NUMBERING.sub("", text, count=1)
    return text.strip("*_ ").replace(" ", "")


def _is_item(key):
    return any(key.startswith(prefix) for prefix, _label in PROFILE_ITEMS)


def _profile_sections(ctx, text):
    """List of (heading text, content lines).

    Headings are Markdown headings of any level, and lines written wholly in
    bold that name one of the eight items (the bold form only for the items,
    so that a bold answer line never counts as a heading).
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    sections = []
    for line in text.splitlines():
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", line)
        bold = None if heading else BOLD_LINE.match(line)
        if heading:
            sections.append((heading.group(1), []))
        elif bold and _is_item(_heading_key(ctx, bold.group(2))):
            sections.append((bold.group(2), []))
        elif sections:
            sections[-1][1].append(line)
    return sections


def _near_headings(text):
    """Lines that look meant as headings but are not: '##每周' or a full-width '＃'."""
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("＃"):
            found.append("第 {} 行的 ＃ 是中文输入法打出来的，要换成英文的 #".format(number))
        elif re.match(r"^#{1,6}[^#\s]", stripped):
            found.append("第 {} 行的 # 后面少了一个空格".format(number))
    return found


def _has_content(lines):
    for line in lines:
        if not PLACEHOLDER.match(line.strip()):
            return True
    return False


def check_a(ctx):
    """artifact: learner/profile.md has the eight items, each filled in.

    The answers are the learner's; nothing about them is judged.
    """
    where = "学习工作区的 learner/profile.md"
    if not ctx.is_file("learner/profile.md"):
        ctx.fail("入学问卷还没有写进 learner/profile.md", where=where, saw="还没有这个文件")
        ctx.stop()
    text = ctx.read("learner/profile.md")
    sections = _profile_sections(ctx, text)
    near = _near_headings(text)
    if not sections:
        if near:
            saw = near[0] + ("（还有 {} 行也是这样）".format(len(near) - 1) if len(near) > 1 else "")
        else:
            saw = "文件里有 {} 行字，但没有一个小标题".format(len(text.splitlines()))
        ctx.fail("问卷里还没有小标题（像 templates/profile-template.md 里那样，以 ## 加一个空格开头的行）",
                 where=where, saw=saw)
        ctx.stop()
    missing, empty, filled = [], [], []
    for key, label in PROFILE_ITEMS:
        found = [lines for title, lines in sections
                 if _heading_key(ctx, title).startswith(key)]
        if not found:
            missing.append(label)
        elif any(_has_content(lines) for lines in found):
            filled.append(label)
        else:
            empty.append(label)
    if missing:
        # Headings that are not one of the eight (the profile's own title "学习档案" aside).
        others = [title.strip() for title, _lines in sections
                  if title.strip() and not _is_item(_heading_key(ctx, title))
                  and _heading_key(ctx, title) != "学习档案"]
        if near:
            saw = near[0]
        elif others:
            saw = "对不上的小标题：" + _cut("、".join(others), 40)
        else:
            saw = "八个小标题里只找到 {} 个".format(len(PROFILE_ITEMS) - len(missing))
        ctx.fail("还缺以这几个字开头的小标题：" + "、".join("「## " + label + "」" for label in missing),
                 where=where, saw=saw)
    if empty:
        ctx.fail("这几项下面还空着：" + "、".join(empty), where=where,
                 saw="小标题在，下一行起没有回答（回答写在小标题下面，不写在标题那一行）")
    if filled:
        ctx.ok("问卷里已经填好 {} 项（一共 8 项）".format(len(filled)))
    if not ctx.failed:
        ctx.note("检查只看每一项填没填，不评判你的回答。以后想改，对导师说一声。")


# ---------------------------------------------------------------------------
# Station 0.1b: two questions whose answers only the learner's screen shows
# ---------------------------------------------------------------------------
FOLDER_WORD = re.compile(r"\s*(这个)?(文件夹|目录|文件)$")


def _bare(typed):
    """The answer without a trailing 文件夹 / 目录 / 文件 and without quotes or brackets around it."""
    typed = typed.strip().strip("「」『』“”\"'`<>《》 ")
    return FOLDER_WORD.sub("", typed).strip().strip("「」『』“”\"'`<>《》 ")


def _same_folder(one, other):
    try:
        return one.exists() and one.resolve() == other.resolve()
    except OSError:
        return False


def _workspace_spellings(ctx):
    """(parent, name) pairs of the paths that pwd can print for the workspace.

    The real folder (where the course was unpacked, before 0.2, or the moved
    ~/Developer/fullstack-from-zero), and the entrance ~/Developer/fullstack-from-zero of a
    learner who stayed: after `cd ~/Developer/fullstack-from-zero`, zsh's pwd prints
    that path, so its parent Developer is the answer on the learner's screen.
    """
    workspace = ctx.workspace
    pairs = [(ctx.normalize(workspace.parent.name), ctx.normalize(workspace.name))]
    entrance = ctx.home / "Developer" / "fullstack-from-zero"
    if _same_folder(entrance, workspace):
        pair = (ctx.normalize(entrance.parent.name), ctx.normalize(entrance.name))
        if pair not in pairs:
            pairs.append(pair)
    return pairs


def _parent_answer(ctx):
    pairs = _workspace_spellings(ctx)
    parents = [parent for parent, _name in pairs]

    def matches(typed):
        typed = _bare(typed)
        parts = [part for part in typed.split("/") if part]
        if not parts:
            return False
        if len(parts) == 1:                        # Desktop, /Desktop/, Desktop文件夹, Developer
            return parts[0] in parents
        if (parts[-2], parts[-1]) in pairs:
            return True                            # a pasted path from pwd: …/Desktop/fullstack-from-zero
        return parts[-1] in parents                # the parent's own path: ~/Desktop

    return matches


def check_b(ctx):
    """ask: the parent folder of the workspace (from pwd) and a file name (from ls).

    The cold redo after hint level 4 (which printed style.css) asks for the
    .html file of the same folder instead, so that it needs ls again.
    """
    site = "starter/my-site"
    ending = ".html" if _redo_due(ctx, "0.1b") else ".css"
    names = ctx.listdir(site, hidden=False)
    found = [name for name in names if name.lower().endswith(ending)]
    if not found:
        # The starter is the course's own material: if it is gone, the check cannot work.
        raise RuntimeError("starter/my-site has no " + ending + " file: the starter material is missing")
    ctx.ask("第一题：在学习工作区运行 pwd。它打印的路径最后一段是 "
            + ctx.workspace.name + "，紧挨在它前面的那一段文件夹名是什么？",
            _parent_answer(ctx))
    accepted = set()
    for name in found:
        accepted.add(name.lower())
        accepted.add(name.lower()[:-len(ending)])
    ctx.ask("第二题：用 ls 看 starter/my-site 这个文件夹。里面名字以 " + ending + " 结尾的那个文件叫什么？",
            lambda typed: _bare(typed).lower() in accepted)


# ---------------------------------------------------------------------------
# Station 0.1c: the amount constant changed, the program still runs
# ---------------------------------------------------------------------------
def _error_line(text):
    """The line number Python complains about, and its last message line."""
    numbers = re.findall(r'File ".*?", line (\d+)', text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    last = lines[-1] if lines else ""
    return (int(numbers[-1]) if numbers else None), last


COMMENT_WORDS = ("要换算", "金额", "单位是")   # words of the original comment after AMOUNT_USD


def _first_changed_line(lines):
    """The first line (1-based) that differs from ORIGINAL_CONVERT, the two
    lines the lesson lets the learner change (AMOUNT_USD, USD_TO_CNY) aside.
    Trailing spaces do not count. None when nothing else differs."""
    original = ORIGINAL_CONVERT.splitlines()
    lines = list(lines)
    for index in range(max(len(original), len(lines))):
        mine = lines[index].rstrip() if index < len(lines) else None
        theirs = original[index].rstrip() if index < len(original) else None
        if mine is not None and theirs is not None:
            for name in ("AMOUNT_USD", "USD_TO_CNY"):
                if mine.lstrip().startswith(name) and theirs.startswith(name):
                    break
            else:
                if mine != theirs:
                    return index + 1
            continue
        if (mine or "").strip() or (theirs or "").strip():
            return index + 1
    return None


def _leading_blanks(ctx, line):
    """saw= text for a line that starts with white space, which no screen shows."""
    stripped = line.lstrip()
    blanks = line[:len(line) - len(stripped)]
    spaces, tabs = blanks.count(" "), blanks.count("\t")
    parts = (["{} 个空格".format(spaces)] if spaces else []) + (["{} 个 Tab".format(tabs)] if tabs else [])
    return "开头先有 {}，才是「{}」".format("、".join(parts) or "看不见的空白字符",
                                         _cut(ctx.visible(stripped.rstrip()), 24))


def _amount_changed(ctx, program, label, show, earlier=None, rate_edited=False):
    """Shared by the station check and the do item.

    ``program`` is the path of a convert.py; ``show`` how the learner reads it.
    ``earlier``: an amount the cold redo must not reuse (None: no such rule).
    ``rate_edited``: the lesson asked the learner to change USD_TO_CNY too
    (station c's 跟我做), so the notes about that line say so.
    Both number lines are read before the program runs, so that a mistake on
    them is named on its own line (`7,20` or `"7.20"` only fails later, at
    the print line); when the program still fails, the note names the first
    line that differs from ORIGINAL_CONVERT, not the line Python points at.
    Returns (new amount as float, the program's output line) or stops.
    """
    if not ctx.is_file(program):
        ctx.fail(label + " 不见了", where=show, saw="这个位置没有文件")
        ctx.stop()
    recovery = ("想要原版对照：python3 tools/course.py scenario 0.1，"
                "课文第 3 站的「改乱了怎么办」有详细步骤。")
    # 1. The AMOUNT_USD line itself: the line the learner was asked to change.
    amount_no, amount_src, rate_no = None, None, None
    for number, line in enumerate(ctx.lines(program), 1):
        start = ctx.normalize(line, case=False).lstrip()
        if amount_no is None and start.startswith("AMOUNT_USD"):
            amount_no, amount_src = number, line
        elif rate_no is None and start.startswith("USD_TO_CNY"):
            rate_no = number
    if amount_no is None:
        ctx.fail("找不到写着 AMOUNT_USD = 的那一行", where=show, saw="这一行被删掉或改了名字")
        ctx.note(recovery)
        ctx.stop()
    where_amount = "{} 第 {} 行（AMOUNT_USD 那一行）".format(show, amount_no)
    found = AMOUNT_LINE.match(amount_src)
    if not found:
        ctx.fail("这一行要写成：AMOUNT_USD、等号 =、一个数（英文输入法下敲）", where=where_amount,
                 saw=_cut(amount_src.strip(), 40))
        ctx.note(recovery)
        ctx.stop()
    amount_text = found.group(1)
    first = amount_text.split()[0] if amount_text.split() else ""
    rest = amount_text[len(first):].strip()
    if "　" in amount_src:
        ctx.fail("这一行里有一个全角空格（中文输入法打出来的），Python 不认它", where=where_amount,
                 saw=ctx.visible(amount_src.rstrip())[:40])
        ctx.note(recovery)
        ctx.stop()
    if amount_src[:1].isspace():
        ctx.fail("这一行前面多了空格（或 Tab），Python 要求它顶格写", where=where_amount,
                 saw=_leading_blanks(ctx, amount_src))
        ctx.note(recovery)
        ctx.stop()
    if "＃" in amount_text:
        ctx.fail("数字后面那个 ＃ 是中文输入法打出来的，要换成英文的 #", where=where_amount,
                 saw="等号后面是「{}」".format(_cut(amount_text, 24)))
        ctx.note(recovery)
        ctx.stop()
    if NUMBER.match(first) and rest and any(word in rest for word in COMMENT_WORDS):
        # The words of the comment are still there, but its # is gone.
        ctx.fail("数字后面的说明文字前面要有 #，这个 # 不能删", where=where_amount,
                 saw="等号后面是「{}」".format(_cut(amount_text, 24)))
        ctx.note(recovery)
        ctx.stop()
    if not NUMBER.match(amount_text):
        ctx.fail("等号后面只写一个数字（英文输入法下敲），不加引号、逗号或单位", where=where_amount,
                 saw="等号后面是「{}」".format(_cut(amount_text, 24)))
        ctx.note(recovery)
        ctx.stop()
    # 1b. The USD_TO_CNY line: changed in 跟我做 (station c), untouched in the do item.
    rate_hint = ("「跟我做」里只该把 7.10 换成 7.20，别的字符都不动。" if rate_edited
                 else "这一行不用改，照原版写回去。")
    if rate_no is None:
        ctx.fail("找不到写着 USD_TO_CNY = 的那一行（汇率）", where=show,
                 saw="这一行被删掉或改了名字")
        ctx.note(recovery)
        ctx.stop()
    rate_src = ctx.lines(program)[rate_no - 1]
    where_rate = "{} 第 {} 行（USD_TO_CNY 那一行）".format(show, rate_no)
    rate_found = RATE_LINE.match(rate_src)
    rate_text = rate_found.group(1) if rate_found else ""
    if "　" in rate_src:
        ctx.fail("这一行里有一个全角空格（中文输入法打出来的），Python 不认它", where=where_rate,
                 saw=ctx.visible(rate_src.rstrip())[:40])
        ctx.note(rate_hint)
        ctx.stop()
    if rate_src[:1].isspace():
        ctx.fail("这一行前面多了空格（或 Tab），Python 要求它顶格写", where=where_rate,
                 saw=_leading_blanks(ctx, rate_src))
        ctx.note(rate_hint)
        ctx.stop()
    if "＃" in rate_src:
        ctx.fail("数字后面那个 ＃ 是中文输入法打出来的，要换成英文的 #", where=where_rate,
                 saw=_cut(rate_src.strip(), 40))
        ctx.note(rate_hint)
        ctx.stop()
    if not rate_found or not NUMBER.match(rate_text):
        ctx.fail("汇率这一行要写成：USD_TO_CNY、等号 =、一个数字（英文输入法下敲，不加引号、逗号或单位）；"
                 "说明文字只能写在 # 后面", where=where_rate,
                 saw=_cut(rate_src.strip(), 40))
        ctx.note(rate_hint)
        ctx.stop()
    # 2. Does the program still run?
    result = ctx.run([ctx.python, str(ctx.path(program))], timeout=20)
    if result.missing or result.timed_out:
        raise RuntimeError("could not run the learner's program: " + repr(result.code))
    if result.code != 0:
        number, last = _error_line(result.err)
        changed = _first_changed_line(ctx.lines(program))
        if number is not None:
            ctx.fail("程序运行时报错了，Python 指出的是第 {} 行".format(number),
                     where="python3 运行 " + show + " 的结果", saw=_cut(last))
        else:
            ctx.fail("程序运行时报错了", where="python3 运行 " + show + " 的结果",
                     saw=_cut(last) or "没有输出")
        if changed is not None:
            ctx.note("和原版比，第 {} 行被改动过，先对照原版看这一行。{}".format(
                changed, "这一站只该改 AMOUNT_USD 和 USD_TO_CNY 两行等号后面的数。" if rate_edited
                else "这里只该改 AMOUNT_USD 那一行等号后面的数。"))
        ctx.note(recovery)
        ctx.stop()
    lines = result.lines
    prints_one_line = len(lines) == 1 and "美元" in lines[0] and "人民币" in lines[0]
    if not prints_one_line:
        ctx.fail("程序应该正好打印一行换算结果", where="python3 运行 " + show + " 的输出",
                 saw="打印了 {} 行".format(len(lines)))
    # 3. Changed, and to a sensible amount?
    amount = float(amount_text.replace("_", ""))
    if amount <= 0:
        ctx.fail("金额要是一个大于 0 的数", where=where_amount, saw="AMOUNT_USD = " + amount_text)
        ctx.stop()
    if amount == _original_amount():
        ctx.fail("金额还是原来的数（改了没保存的话，这里也看不到）",
                 where=where_amount,
                 saw="AMOUNT_USD = " + amount_text)
        ctx.stop()
    if earlier is not None and amount == earlier:
        ctx.fail("重做这一站时，金额要换一个和上次通过时不一样的数",
                 where=where_amount,
                 saw="AMOUNT_USD = {}，和上次通过时一样".format(amount_text))
        ctx.stop()
    # Praise only once the learner's own change is there (tool-api 19.12).
    ctx.ok("金额改成了 " + amount_text)
    if prints_one_line:
        ctx.ok("改过以后程序照样能运行，打印了一行换算结果")
    return amount, (lines[0] if lines else "")


def _cny_answer(output_line):
    """A matcher for the yuan amount printed after ≈, or None if it cannot be read."""
    found = re.search(r"≈\s*([+-]?[0-9][0-9,]*(?:\.[0-9]+)?)\s*人民币", output_line)
    if not found:
        return None
    expected = float(found.group(1).replace(",", ""))

    def matches(typed):
        numbers = re.findall(r"-?\d[\d,]*(?:\.\d+)?", typed)
        values = []
        for number in numbers:
            try:
                values.append(float(number.replace(",", "")))
            except ValueError:
                pass
        return any(abs(value - expected) < 0.006 for value in values)

    return matches


AMOUNT_KEY = "hello_fx_amount"


def _redo_due(ctx, station_id):
    """Is the cold redo after hint level 4 of this station due today?"""
    record = (ctx.state.get("stations") or {}).get(station_id)
    redo = record.get("redo") if isinstance(record, dict) else None
    if not isinstance(redo, dict) or redo.get("done") or not redo.get("after"):
        return False
    return ctx.now.date().isoformat() >= str(redo["after"])


def check_c(ctx):
    """artifact + ask: the workspace's convert.py, changed and still running.

    The cold redo (due 3-7 days after hint level 4) must use another amount
    than the one of the last passed check, or it would pass on the old edit.
    """
    program = "starter/hello-fx/convert.py"
    earlier = None
    if _redo_due(ctx, "0.1c"):
        try:
            earlier = float(ctx.decision(AMOUNT_KEY))
        except (TypeError, ValueError):
            earlier = None
    amount, line = _amount_changed(ctx, program, "starter/hello-fx/convert.py",
                                   "starter/hello-fx/convert.py", earlier=earlier, rate_edited=True)
    if ctx.failed:
        ctx.stop()
    ctx.decide(AMOUNT_KEY, amount)
    matcher = _cny_answer(line)
    if matcher is None:
        ctx.fail("程序打印的那一行里找不到「≈ 金额 人民币」", where="python3 运行 " + program + " 的输出",
                 saw=_cut(line))
        ctx.note("这一站只该改 AMOUNT_USD 和 USD_TO_CNY 两行等号后面的数，打印那一行不要动。"
                 "想要原版对照：python3 tools/course.py scenario 0.1")
        ctx.stop()
    ctx.ask("改完以后运行程序：它打印的那一行里，≈ 后面的人民币金额是多少？", matcher)


def _do_amount(ctx):
    info = ctx.scenario("start")
    program = info.path / info.facts["folder"] / "convert.py"
    _amount_changed(ctx, program, "练习场景里的 convert.py", ctx.show(program))


checks = {"0.1a": check_a, "0.1b": check_b, "0.1c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "0.1a": [
        "这一站要的是一份填好的入学问卷 learner/profile.md。先看检查结果里「还缺什么」说的是哪一项。",
        "对导师说“我们来做入学问卷”，导师会一题一题问你，再把回答写进 learner/profile.md。"
        "已经做过、只是哪一项空着或标题不对，告诉导师是哪一项，请它照 templates/profile-template.md 的小标题改好。"
        "导师没反应：学完第 3 站以后，运行 code learner/profile.md（没有这个文件，VS Code 会新建一个），"
        "再用 code templates/profile-template.md 打开模板，把它里面以 ## 开头的八行小标题照抄进去，在每个小标题下面写一行回答，按 ⌘S 保存。",
        "相似的例子：第一次去医院填初诊表，每一栏都要有字；填“不知道”“没有”也算填了，空着才不算。"
        "栏目名也要和表上印的一样，别人才找得到。",
        "答案：learner/profile.md 里要有八个小标题，各以这几个字开头：## 学习目的、## 每周时间与固定时段、"
        "## 一次能坐多久、## 英文阅读、## GitHub、## 想做的作品、## 导师严格度、## 以前用过终端吗；"
        "每个小标题下面至少写一行你的回答。"
        "导师不在的话，学完第 3 站以后用 code learner/profile.md 自己写，小标题照抄 templates/profile-template.md"
        "（用 code templates/profile-template.md 打开它）。\n"
        "解释：课程按这些回答安排节奏、英文注释的多少和导师的严格程度；检查只看填没填，不评判你答得对不对。",
    ],
    "0.1b": [
        "两道题的答案都在你自己的屏幕上：一道来自 pwd，一道来自 ls。先在终端里运行，再回答。",
        "第一题：运行 pwd，看它打印的那一行的最后两段。第二题：ls 后面空一格，再写一个文件夹名，就能看那个文件夹里有什么。",
        "相似的例子：想看 starter/hello-fx 里有什么，就运行 ls starter/hello-fx，屏幕上会列出 convert.py 和 rates.txt。",
        "答案：在学习工作区运行 pwd，打印出的路径以 /fullstack-from-zero 结尾，紧挨在它前面的那一段就是第一题的答案"
        "（以你屏幕上的为准，比如 Developer 或 Desktop）。再运行 ls starter/my-site，它列出两个文件，"
        "以 .css 结尾的是 style.css。\n"
        "解释：pwd 告诉你现在在哪个文件夹；ls 列出一个文件夹里有什么，后面跟一个文件夹名，就看那个文件夹。",
    ],
    "0.1c": [
        "检查看三件事：金额改了没有，文件存了没有，程序还能不能运行。先看检查结果里「还缺什么」说的是哪一件。",
        "用 code starter/hello-fx/convert.py 打开文件，找到写着 AMOUNT_USD 的那一行。"
        "改完按 ⌘S 保存；标签页上文件名旁边的圆点消失，才算存好。",
        "相似的例子：「跟我做」里你把汇率那一行 USD_TO_CNY = 7.10 改成了 7.20，保存后再运行，结果就跟着变了。"
        "要换算的金额在它上面一行，写法一样：名字、等号、数，# 后面是给人看的说明。",
        "答案：把 AMOUNT_USD = 100 里的 100 换成另一个大于 0 的数，比如 AMOUNT_USD = 250，"
        "只改数字（英文输入法下敲，不加引号、逗号或单位），等号和 # 后面的说明都不动；"
        "按 ⌘S 保存；在学习工作区运行 python3 starter/hello-fx/convert.py，屏幕上出现"
        "“250 美元 ≈ 1800.00 人民币……”（汇率还是 7.10 的话是 1775.00）；"
        "检查问的人民币金额，照抄你屏幕上这一行里 ≈ 后面的数。"
        "过几天工具请你不看提示重做这一站时，金额要换一个和这次不一样的数。\n"
        "解释：程序就是一份文本文件，python3 读它、照着执行；文件里的数一改，执行出来的结果就跟着变。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "0.1-r1", "type": "recall", "tier": "fluent", "station": "0.1c", "rule": "META-01",
     "q": "终端里出现一段报错。在求助之前，先问自己哪三个问题？",
     "a": "谁在报错（哪个程序）？关键词是什么？我刚才敲了什么？",
     "explain": "这是本课程的约定 META-01。三个答案说得出来，多数报错自己就能看懂。"},
    {"id": "0.1-r2", "type": "which", "tier": "fluent", "station": "0.1b",
     "q": "想知道终端现在在哪个文件夹里，用哪条命令？",
     "options": ["pwd", "ls", "clear"], "answer": "A", "shuffle": True,
     "explain": "pwd 打印当前所在的文件夹（print working directory）；ls 列出文件夹里有什么；clear 只是清屏。"},
    {"id": "0.1-r3", "type": "which", "tier": "fluent", "station": "0.1b",
     "q": "终端里一条命令停不下来，或者提示符变成了 dquote> 不知道怎么回去。按什么键？",
     "options": ["Ctrl+C", "回车（Enter）", "⌘S"], "answer": "A", "shuffle": True,
     "explain": "Ctrl+C 让终端里正在进行的事停下，回到提示符。回车只会接着等你输入；⌘S 是编辑器里的保存。"},
    {"id": "0.1-r4", "type": "fault", "tier": "fluent", "station": "0.1c", "rule": "META-01",
     "q": "运行下面这条命令，python3 回答 [Errno 2] No such file or directory。最可能是哪里出了问题？\n\n"
          "    python3 starter/hello-fx/convrt.py",
     "options": ["文件名打错了，这个位置没有这个文件", "电脑上没有装 Python", "程序里的汇率数字写错了"],
     "answer": "A", "shuffle": True,
     "explain": "报错的是 python3，它已经在运行，所以 Python 装着；它连文件都没打开，更没读到里面的数字。"
                "关键词 No such file or directory 说的是“没有这个文件或文件夹”：对照一下文件名，少了一个 e。"},
    {"id": "0.1-p1", "type": "predict", "tier": "lookup", "station": "0.1b",
     "q": "在终端里把 pwd 多敲了一个 d，敲成 pwdd，按回车。会看到什么？",
     "options": ["zsh: command not found: pwdd", "照样打印当前所在的文件夹", "什么也不显示"],
     "answer": "A",
     "explain": "终端不会猜你的意思。zsh 找不到叫 pwdd 的命令，就直说 command not found（找不到这个命令）。"},
    {"id": "0.1-d1", "type": "do", "tier": "lookup", "station": "0.1c",
     "q": "练习场景里有一份汇率换算小程序 convert.py。把它要换算的美元金额改成另一个大于 0 的数，保存，再运行一次，看结果变没变。",
     "scenario": "start", "check": _do_amount},
]


# ---------------------------------------------------------------------------
# EXAM (gate-0)
# ---------------------------------------------------------------------------
KM_PROGRAM = '''"""把公里换算成英里，打印一行结果。"""

KM = {start}  # 要换算的距离，单位是公里
KM_TO_MILE = 0.621371  # 1 公里约等于多少英里


def main():
    miles = KM * KM_TO_MILE
    print(f"{{KM}} 公里 ≈ {{miles:.2f}} 英里")


if __name__ == "__main__":
    main()
'''

PRICE_PROGRAM = '''"""算一件商品打折后的价格，打印一行结果。"""

DISCOUNT = 0.85  # 打几折：0.85 就是八五折
PRICE = {start}  # 原价，单位是元


def main():
    final = PRICE * DISCOUNT
    print(f"原价 {{PRICE}} 元，打折后 {{final:.2f}} 元")


if __name__ == "__main__":
    main()
'''


def build_x1(sc):
    folder = "tool-" + sc.word()
    if sc.form == "A":
        start = sc.randint(3, 9)
        target = sc.randint(12, 60)
        name = sc.pick(["km_to_mile.py", "distance.py", "run_length.py"])
        sc.write(folder + "/" + name, KM_PROGRAM.format(start=start), exact=True)
        sc.fact("const", "KM")
    else:
        start = sc.pick([60, 80, 120, 150])
        target = sc.pick([90, 200, 260, 340, 480])
        name = sc.pick(["price.py", "discount.py", "sale.py"])
        sc.write(folder + "/" + name, PRICE_PROGRAM.format(start=start), exact=True)
        sc.fact("const", "PRICE")
    sc.fact("folder", folder)
    sc.fact("file", name)
    sc.fact("start", start)
    sc.fact("target", target)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    program = info.path / facts["folder"] / facts["file"]
    show = ctx.show(program)
    if not ctx.is_file(program):
        ctx.fail("考试用的程序文件不见了", where=show, saw="这个位置没有文件")
        ctx.stop()
    pattern = re.compile(r"^\s*" + facts["const"] + r"\s*=\s*(.*?)\s*(#.*)?$")
    value = None
    for line in ctx.lines(program):
        found = pattern.match(line)
        if found:
            value = found.group(1)
    if value is None or not NUMBER.match(value):
        ctx.fail("要改的那个数找不到了，或者等号后面不是一个数", where=show,
                 saw="那一行现在是「{}」".format(_cut(value or "没有这一行", 24)))
        ctx.stop()
    if float(value.replace("_", "")) != float(facts["target"]):
        ctx.fail("那个数还不是题目要求的值", where=show, saw="现在是 " + value)
        ctx.stop()
    ctx.ok("题目要求的数改好了")
    result = ctx.run([ctx.python, str(program)], timeout=20)
    if result.missing or result.timed_out:
        raise RuntimeError("could not run the exam program")
    if result.code != 0 or len(result.lines) != 1:
        number, last = _error_line(result.err)
        ctx.fail("程序不能正常运行了" + ("（Python 指出第 {} 行）".format(number) if number else ""),
                 where="python3 运行 " + show, saw=_cut(last or "没有输出"))
        ctx.stop()
    ctx.ok("程序能运行，打印了一行结果")
    numbers = re.findall(r"\d+\.\d\d", result.lines[0])
    if not numbers:
        # The learner changed the print line (e.g. removed the f of the f-string):
        # learner work, so it is graded, never 检查器出问题.
        ctx.fail("程序打印的那一行里找不到算出来的数（带两位小数的）",
                 where="python3 运行 " + show + " 的输出", saw=_cut(result.lines[0]))
        ctx.stop()
    expected = float(numbers[-1])
    ctx.ask("程序打印的结果里，算出来的那个数（带两位小数的）是多少？",
            lambda typed: any(abs(float(n.replace(",", "")) - expected) < 0.006
                              for n in re.findall(r"\d[\d,]*(?:\.\d+)?", typed)))


# Both forms of 0.1-x2 test what 0.1 taught: read a one-line error with the
# 报错三问, find the mistyped part, fix the command and run the program.
# Form A: the command name is mistyped (zsh answers, as with pwdd in 0.1b).
# Form B: the file name is mistyped (python3 answers, as with convrt.py in 0.1c).
WEEK_PROGRAM = '''"""打印这一周学了几站。"""

DONE = {done}
print(f"这一周学了 {{DONE}} 站")
'''

COUNT_PROGRAM = '''"""打印今天要复习的题数。"""

DUE = {due}
print(f"今天要复习 {{DUE}} 道题")
'''


def build_x2(sc):
    folder = "errors-" + sc.word()
    if sc.form == "A":
        name = sc.pick(["week.py", "weekly.py", "summary.py"])
        typo_cmd = sc.pick(["pyhton3", "pyton3", "pythn3"])
        count = sc.randint(3, 9)
        sc.write(folder + "/" + name, WEEK_PROGRAM.format(done=count), exact=True)
        sc.fact("file", name)
        sc.fact("cmd", typo_cmd)
    else:
        real = sc.pick(["review_count.py", "due_today.py", "count_items.py"])
        typo = {"review_count.py": "reveiw_count.py", "due_today.py": "due_todya.py",
                "count_items.py": "count_iterns.py"}[real]
        count = sc.randint(11, 48)
        sc.write(folder + "/" + real, COUNT_PROGRAM.format(due=count), exact=True)
        sc.fact("file", real)
        sc.fact("typo", typo)
    sc.fact("count", count)
    sc.fact("folder", folder)


WHO_OPTIONS = ["zsh（终端里接命令的 shell）", "python3", "VS Code"]
WHO_FEEDBACK = {
    "A": {"B": "python3 报错时开头是 python3:；这段报错的开头不是它。",
          "C": "这一题从头到尾没有用到编辑器。"},
    "B": {"A": "zsh 报错时开头是 zsh:；这段报错的开头不是它。",
          "C": "这一题从头到尾没有用到编辑器。"},
}


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    form = info.form if info.form in ("A", "B") else "B"
    right = "A" if form == "A" else "B"
    ctx.quiz("按题目给的命令运行时，报错的是哪个程序？", WHO_OPTIONS, right,
             feedback=WHO_FEEDBACK[form])
    what = "站数" if form == "A" else "题数"
    ctx.ask("改对命令、让程序跑起来以后，它打印的{}是多少？".format(what), facts["count"])


EXAM = [
    {
        "id": "0.1-x1",
        "gate": "gate-0",
        "title": "改一个数，再运行程序",
        "minutes": 6,
        "build": build_x1,
        "task": {
            "A": "{dir}/{folder} 里有一个小程序 {file}。把里面的 {const} 改成 {target}，保存，然后运行它。"
                 "评分时会问你它打印出的英里数。",
            "B": "打开 {dir}/{folder}/{file}：让它按原价 {target} 元来算，保存，再运行一次。"
                 "评分时会问你它算出的打折后价格。",
        },
        "grade": grade_x1,
    },
    {
        "id": "0.1-x2",
        "gate": "gate-0",
        "title": "读懂一段报错",
        "minutes": 5,
        "build": build_x2,
        "task": {
            "A": "有人让你运行 {cmd} {dir}/{folder}/{file}，结果报错了。用报错三问读懂它，"
                 "改对命令，让程序真正跑起来。评分时会问你是哪个程序在报错，以及程序打印的站数。",
            "B": "有人让你运行 python3 {dir}/{folder}/{typo}，结果报错了。用报错三问读懂它，"
                 "改对命令，让程序真正跑起来。评分时会问你是哪个程序在报错，以及程序打印的题数。",
        },
        "grade": grade_x2,
    },
]
