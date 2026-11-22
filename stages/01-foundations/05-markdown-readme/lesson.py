"""Lesson 1.5: Markdown and README (plan section 4, row 1.5).

Station a: Markdown syntax (headings, lists, emphasis, inline code, fenced
code blocks, links) and the preview.  The independent exercise is a small
cheat sheet ``commands.md`` in the start scenario; the check scans it with a
small CommonMark-shaped scanner below.

Station b: the README as the front door of a project.  The worked example is
a README for the hello-fx copy in the playground; the independent exercise is
the learner's real ``~/Developer/my-site/README.md`` (state S3).

Standard library only, Python 3.9 syntax.  Reference: docs/authoring/tool-api.md.
"""

import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.5",
    "slug": "05-markdown-readme",
    "title": "Markdown 与 README",
    "stage": 1,
    "prerequisites": ["1.4"],
    "stations": [
        {
            "id": "1.5a",
            "title": "Markdown 语法",
            "minutes": 35,
            "new_concept": "Markdown 用几个普通符号标出文字的结构，预览把它显示成排好版的样子",
            "new_commands": [],
        },
        {
            "id": "1.5b",
            "title": "README 是项目的门面",
            "minutes": 30,
            "new_concept": "README 是放在项目根目录、回答陌生人最先想问的几个问题的说明书",
            "new_commands": [],
        },
    ],
    "rules": ["DOC-01", "DOC-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9", "code": "1.145.2"},
    },
    "unverified_steps": [
        "1.5a：code . 打开 1.5-start 后窗口上方出现受限模式的横幅，照第 1.4 课第 1 站的办法信任这个文件夹；然后在 VS Code 左边的 Explorer 里点开 weekend.md、写入、⌘S 保存，标签页上的圆点消失（按 VS Code 官方文档写成）",
        "1.5a：中文输入法下按反引号键打出的字符，以及括号、#、空格变成全角（不同输入法设置不同）",
        "1.5a：用 ⇧⌘V 和 ⌘K V 打开 Markdown 预览，以及预览里看到的样子（按 VS Code 官方文档 Markdown 一页和 CommonMark 0.31.2 规范写成）",
        "1.5a：故意把「# 周末计划」写成「#周末计划」后，预览里显示成普通文字（按 CommonMark 0.31.2 ATX 标题一节写成，没有在屏幕上看到）",
        "1.5b：在 hello-fx 的 VS Code 窗口里点开用 touch 建好的 README.md，写入、保存并预览（按 VS Code 官方文档写成）",
        "1.5b：在 my-site 的 VS Code 窗口里点开 README.md 写自己的说明（按 VS Code 官方文档写成）",
    ],
}

TERMS = [
    {"term": "Markdown", "en": "Markdown",
     "plain": "一种用 #、-、` 这类普通符号标出标题、列表、代码的纯文本写法", "first": "1.5a"},
    {"term": "扩展名", "en": "file extension",
     "plain": "文件名最后一个点后面的那几个字母，表示文件是哪一种，比如 .md 是 Markdown", "first": "1.5a"},
    {"term": "预览", "en": "preview",
     "plain": "编辑器把 Markdown 显示成排好版的样子，只是看，不改文件", "first": "1.5a"},
    {"term": "标题", "en": "heading",
     "plain": "以 # 开头的一行，# 的个数是级别：一个 # 是一级标题", "first": "1.5a"},
    {"term": "行内代码", "en": "inline code",
     "plain": "一句话里用一对反引号 ` 包起来的命令或文件名", "first": "1.5a"},
    {"term": "代码块", "en": "fenced code block",
     "plain": "上下各一行三个反引号 ``` 围起来的几行，原样显示，常用来放命令", "first": "1.5a"},
    {"term": "README", "en": "README",
     "plain": "项目的门面和说明书：放在项目最外层文件夹，告诉别人这是什么、怎么用", "first": "1.5b"},
    {"term": "根目录", "en": "root directory",
     "plain": "一个项目最外层的那个文件夹，比如 my-site 本身", "first": "1.5b"},
]

# ---------------------------------------------------------------------------
# A small Markdown scanner (enough for beginners' files; CommonMark-shaped)
# ---------------------------------------------------------------------------
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
HEADING_NOSPACE = re.compile(r"^ {0,3}#{1,6}[^#\s]")
HEADING_IDEOSPACE = re.compile("^ {0,3}#{1,6}　")      # 全角空格 after #
FULLWIDTH_HASH = re.compile(r"^\s*＃")
LIST_ITEM = re.compile(r"^ {0,3}(?:[-*+]|\d{1,9}[.)])[ \t]+\S")
LIST_NOSPACE = re.compile(r"^ {0,3}(?:-(?![-\s])|\+(?![+\s])|\d{1,9}[.)](?=[^\d\s]))\S")
LIST_IDEOSPACE = re.compile("^ {0,3}(?:[-*+]|\\d{1,9}[.)])　")   # 全角空格 after -
LIST_CHINESE = re.compile(r"^\s*(?:[·•●▪]|\d{1,2}、)\s*\S")
# CommonMark 0.31.2 section 6.1: a code span begins with a backtick string and
# ends with a backtick string of equal length (`cd`, ``cd``, ``a ` b``).
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)[^\n]*?[^`\s][^\n]*?(?<!`)\1(?!`)")
BAD_INLINE_CODE = re.compile(r"[·｀][A-Za-z0-9 ._~/\-]+[·｀]")
# CommonMark 0.31.2 section 6.3: inside the parentheses the destination and the
# optional title may be surrounded by spaces or tabs; between "]" and "(" no
# space is allowed (that case is in BAD_LINK).
LINK = re.compile(
    r"\[[^\]\n]+\]\([ \t]*(<[^>\n]*>|[^)\s]+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?[ \t]*\)")
# A destination that looks like a real address or a file: a web address, a
# path, an anchor, or a file name with a dot.  The lesson's own placeholder
# 「[显示的文字](网址)」 is none of these.
REAL_TARGET = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|/|\./|\.\./|#|~)|[./]")
# A web address written without https:// (「[MDN](developer.mozilla.org)」):
# the preview treats it as a file next to the document, so the click fails.
WEB_NO_SCHEME = re.compile(
    r"^(?:www\.[^/\s]+|(?:[A-Za-z0-9-]+\.)+(?:com|org|net|cn|io|dev|edu|gov|app|info|me|co|ai"
    r"|site|top|xyz|uk|de|jp))(?::\d+)?(?:[/?#]\S*)?$", re.IGNORECASE)
AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
BARE_URL = re.compile(r"https?://\S+")
BAD_LINK = re.compile(
    r"【[^】\n]+】\s*[（(]|\[[^\]\n]+\]\s*（|\[[^\]\n]+\]\s+\(|\([^)\n]+\)\[https?://|\[[^\]\n]+\]【")
BOLD = re.compile(r"\*\*[^*\n]+?\*\*|__[^_\n]+?__")
# Look-alike fences, including an opening line with two backticks followed by
# a language name (``zsh).
BAD_FENCE = re.compile(r"^\s*(?:·{3,}|｀{3,}|‘{3,}|'{3,}|`{1,2}\s*$|``[A-Za-z][\w+-]*\s*$)")
# A mistyped opening line that is not a fence at all: one or two backticks,
# maybe a space, then a language name (`zsh, `` zsh, ``zsh).  Used only to name
# that line when a code block below it is left open.
NEAR_FENCE = re.compile(r"^\s*`{1,2}[ \t]*[A-Za-z][\w+-]*\s*$")
# CommonMark 0.31.2 section 4.3: a line of = (level 1) or - (level 2) under a
# paragraph makes that paragraph a heading.  Under a list item, a quote or a
# thematic break it does not (a - line there is a thematic break), nor under a
# lazy continuation line of a list item or quote, nor under indented code
# (a first line indented four or more spaces).
SETEXT_H1 = re.compile(r"^ {0,3}=+\s*$")
SETEXT_H2 = re.compile(r"^ {0,3}-+\s*$")
ANY_BREAK = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")   # thematic break
NOT_PARAGRAPH = re.compile(r"^ {0,3}(?:>|(?:[-*+]|\d{1,9}[.)])(?:[ \t]|$)|([-*_])(?:[ \t]*\1){2,}[ \t]*$|=+\s*$)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def scan(text):
    """Return a dict describing the Markdown structure of ``text``.

    Fenced code blocks are recognised first (CommonMark 0.31.2, section 4.5:
    an opening fence of at least three backticks or tildes, indented at most
    three spaces, closed by a fence of the same character that is at least as
    long).  Everything else is only looked at outside code blocks.
    """
    info = {
        "h1": [], "h2": [], "deeper": [], "nospace": [], "fullwidth_hash": [],
        "ideo_heading": [], "items": [], "bad_items": [], "ideo_items": [],
        "chinese_items": [],
        "inline_code": 0, "bad_inline_code": [], "links": 0, "autolinks": 0,
        "bare_urls": 0, "bad_links": [], "bold": 0, "targets": [],
        "placeholder_links": [], "schemeless": [], "stray_backticks": [],
        "fences": 0, "fences_without_lang": 0, "unclosed_fence": None,
        "bad_fences": [], "near_fences": [], "email": False, "first_line": "",
        "body": [],
    }
    lines = text.split("\n")
    fence = None            # (char, length, line number) while inside a block
    previous = ""
    para_start = ""         # first line of the current block, "" after a break
    for number, raw in enumerate(lines, 1):
        line = raw.rstrip("\r")
        if fence is not None:
            stripped = line.strip()
            if (len(line) - len(line.lstrip(" ")) <= 3 and stripped
                    and set(stripped) == {fence[0]} and len(stripped) >= fence[1]):
                info["fences"] += 1
                fence = None
            continue
        opened = FENCE_OPEN.match(line)
        if opened and not (opened.group(1)[0] == "`" and "`" in opened.group(2)):
            fence = (opened.group(1)[0], len(opened.group(1)), number)
            if not opened.group(2).strip():
                info["fences_without_lang"] += 1
            previous = para_start = ""
            continue
        if not info["first_line"] and line.strip():
            info["first_line"] = line.strip()
        if EMAIL.search(line):
            info["email"] = True
        if BAD_FENCE.match(line):
            info["bad_fences"].append(number)
        if NEAR_FENCE.match(line):
            info["near_fences"].append(number)
        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            title = (heading.group(2) or "").rstrip("#").strip()
            key = "h1" if level == 1 else ("h2" if level == 2 else "deeper")
            info[key].append(title)
            previous = para_start = ""
            continue
        if HEADING_IDEOSPACE.match(line):
            info["ideo_heading"].append(line.strip())
        elif HEADING_NOSPACE.match(line):
            info["nospace"].append(line.strip())
        elif FULLWIDTH_HASH.match(line):
            info["fullwidth_hash"].append(line.strip())
        setext = None
        if (previous.strip() and not NOT_PARAGRAPH.match(previous) and para_start
                and not NOT_PARAGRAPH.match(para_start)
                and len(para_start) - len(para_start.lstrip(" ")) <= 3):
            setext = "h1" if SETEXT_H1.match(line) else ("h2" if SETEXT_H2.match(line) else None)
        if setext:
            info[setext].append(previous.strip())
            previous = para_start = ""
            continue
        if not line.strip():
            para_start = ""
        elif (not previous.strip() or NOT_PARAGRAPH.match(line)
                or ANY_BREAK.match(previous)):
            para_start = line           # a new block starts on this line
        if LIST_ITEM.match(line):
            info["items"].append(line.strip())
        elif LIST_IDEOSPACE.match(line):
            info["ideo_items"].append(line.strip())
        elif LIST_NOSPACE.match(line):
            info["bad_items"].append(line.strip())
        elif LIST_CHINESE.match(line):
            info["chinese_items"].append(line.strip())
        info["inline_code"] += len(INLINE_CODE.findall(line))
        info["bad_inline_code"] += BAD_INLINE_CODE.findall(line)
        no_code = INLINE_CODE.sub("", line)
        if "`" in no_code and not BAD_FENCE.match(line):
            info["stray_backticks"].append(line.strip())
        for link in LINK.finditer(no_code):
            target = link.group(1).strip("<>").strip()
            if WEB_NO_SCHEME.match(target):
                info["schemeless"].append(target)
            elif REAL_TARGET.search(target):
                info["links"] += 1
                info["targets"].append(target)
            else:
                info["placeholder_links"].append(link.group(0))
        for link in AUTOLINK.finditer(no_code):
            info["autolinks"] += 1
            info["targets"].append(link.group(1))
        info["bad_links"] += BAD_LINK.findall(no_code)
        info["bold"] += len(BOLD.findall(no_code))
        without_links = AUTOLINK.sub("", LINK.sub("", no_code))
        info["bare_urls"] += len(BARE_URL.findall(without_links))
        if line.strip() and not heading:
            info["body"].append(line.strip())
        previous = line
    if fence is not None:
        info["unclosed_fence"] = fence[2]
    return info


def _outside_fences(text):
    """(line number, line) for every line outside fenced code blocks."""
    fence = None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip("\r")
        if fence is not None:
            stripped = line.strip()
            if (len(line) - len(line.lstrip(" ")) <= 3 and stripped
                    and set(stripped) == {fence[0]} and len(stripped) >= fence[1]):
                fence = None
            continue
        opened = FENCE_OPEN.match(line)
        if opened and not (opened.group(1)[0] == "`" and "`" in opened.group(2)):
            fence = (opened.group(1)[0], len(opened.group(1)))
            continue
        yield number, line


# Commands of lessons 0.1-1.4: a cheat sheet names at least three of them.
KNOWN_COMMANDS = ("pwd", "ls", "cd", "clear", "python3", "code", "man", "mkdir",
                  "touch", "cat", "less", "head", "tail", "cp", "mv", "rm", "rmdir",
                  "grep", "find", "open", "zip", "echo", "which")
COMMAND_WORD = re.compile(r"(?<![A-Za-z0-9_.])(" + "|".join(KNOWN_COMMANDS)
                          + r")(?![A-Za-z0-9_])")


def known_commands(text):
    """The taught command names a file mentions, in order of first appearance."""
    seen = []
    for name in COMMAND_WORD.findall(text):
        if name not in seen:
            seen.append(name)
    return seen


# What is left of a template or a blank to fill in.  The template's own
# placeholders are the bracketed 「（在这里写……）」 lines and its usage paragraph
# 「写完把这一段删掉」; ordinary prose such as 「我会在这里写下……」 is not one.
# Underscores count only outside quotes, inline code and links (a README may
# quote the page's old heading 「你好，我是____」), and a line of underscores
# alone is a thematic break, not a blank.  A section headed TODO is ordinary
# README content.
PLACEHOLDER_TEXT = re.compile(
    r"[（(]\s*在这里写|写完把这一段删掉|<[^>\n]*(?:写|填)[^>\n]*>|待填写|【[^】\n]*填[^】\n]*】")
QUOTED = re.compile(r"「[^」\n]*」|『[^』\n]*』|“[^”\n]*”|\"[^\"\n]*\"|‘[^’\n]*’")
EMPHASIS_UNDERSCORES = re.compile(r"_{2,3}[^_\s](?:[^_\n]*[^_\s])?_{2,3}")
BLANK = re.compile(r"_{3,}")
THEMATIC_BREAK = re.compile(r"^ {0,3}(?:_[ \t]*){3,}$")


def placeholder_line(text):
    """(line number, line) of the first unfilled placeholder, or None."""
    for number, line in _outside_fences(text):
        if PLACEHOLDER_TEXT.search(line):
            return number, line
        if THEMATIC_BREAK.match(line):
            continue
        rest = AUTOLINK.sub("", LINK.sub("", QUOTED.sub("", INLINE_CODE.sub("", line))))
        rest = BARE_URL.sub("", EMPHASIS_UNDERSCORES.sub("", rest))
        if BLANK.search(rest):
            return number, line
    return None


def _short(text, size=24):
    text = text.strip()
    return text if len(text) <= size else text[:size] + "…"


def _check_headings(ctx, info, where, sections_needed):
    """One level-1 heading and at least ``sections_needed`` level-2 headings."""
    if info["ideo_heading"]:
        ctx.fail("有一行 # 后面是全角空格，要换成半角空格（英文输入法下按空格键）",
                 where=where, saw="「" + _short(info["ideo_heading"][0]) + "」")
    if info["fullwidth_hash"]:
        ctx.fail("有一行用的是全角的＃，Markdown 只认半角的 #", where=where,
                 saw="「" + _short(info["fullwidth_hash"][0]) + "」")
    if info["nospace"]:
        ctx.fail("有一行 # 后面没有空格，预览里它只是普通文字，不是标题", where=where,
                 saw="「" + _short(info["nospace"][0]) + "」")
    count = len(info["h1"])
    if count == 1:
        ctx.ok("有一个一级标题：「" + _short(info["h1"][0]) + "」")
    elif count == 0:
        near_h1 = [line for line in info["ideo_heading"] + info["nospace"]
                   if re.match(r"#(?!#)", line)] + info["fullwidth_hash"]
        if not near_h1:          # a broken "#标题" line was already reported above
            ctx.fail("还没有一级标题（以一个 # 加空格开头的一行）", where=where, saw="没有找到")
    else:
        ctx.fail("本课程约定一个文件只有一个一级标题，其余的用二级标题", where=where,
                 saw="有 " + str(count) + " 个一级标题")
    sections = len(info["h2"])
    if sections >= sections_needed:
        ctx.ok("有 " + str(sections) + " 个二级标题，分出了小节")
    else:
        saw = "现在有 " + str(sections) + " 个二级标题"
        if info["deeper"] and sections < sections_needed:
            saw += "，另有 " + str(len(info["deeper"])) + " 个更小的标题"
        if sections_needed == 1:
            ctx.fail("还没有二级标题（以 ## 加空格开头的一行，用来分小节）", where=where, saw=saw)
        else:
            ctx.fail("二级标题（小节）还不够 " + str(sections_needed) + " 个", where=where, saw=saw)


def _list_problem(info):
    """(missing, saw) for lines that look like a list but are not one, or None."""
    if info["ideo_items"]:
        return ("有像列表的行，但 - 后面是全角空格，要换成半角空格",
                "「" + _short(info["ideo_items"][0]) + "」")
    if info["bad_items"]:
        return ("有像列表的行，但列表符号后面少了一个空格",
                "「" + _short(info["bad_items"][0]) + "」")
    if info["chinese_items"]:
        return ("有像列表的行，但用的是中文的序号或圆点，Markdown 不认",
                "「" + _short(info["chinese_items"][0]) + "」")
    return None


SAVE_NOTE = "检查读的是存好的文件。预览里有、检查却说没有：先按 ⌘S 保存，再检查一次。"
SCHEME_NOTE = "网址要从 https:// 开始写，不然点了会去找一个同名的文件。"


def _missing_scheme(ctx, folder, found):
    """Link targets that look like a web address without https:// and are not
    a file or folder next to the document."""
    return [target for target in found["schemeless"]
            if not ctx.exists(folder / target.split("#")[0].split("?")[0])]


def _unclosed_first(ctx, info, where):
    """An unclosed fence hides everything after it: report only that, then stop."""
    if info["unclosed_fence"]:
        _check_fences(ctx, info, where)
        ctx.note(SAVE_NOTE)
        ctx.stop()


def _check_fences(ctx, info, where):
    """Fenced code blocks: none left open, no look-alike fence characters."""
    if info["unclosed_fence"]:
        ctx.fail("有一个代码块只有开头那行三个反引号，没有收尾的那一行", where=where,
                 saw="第 " + str(info["unclosed_fence"]) + " 行开始的代码块一直没有结束")
        ctx.note("代码块没收尾时，它后面的所有内容都被当成代码，后面的标题、列表和链接也就看不见了。")
        before = [n for n in info["bad_fences"] + info["near_fences"]
                  if n < info["unclosed_fence"]]
        if before:
            ctx.note("第 " + str(max(before)) + " 行像是代码块开头的那一行，但不是三个半角反引号 ```。"
                     "它要是开头，先改好它，第 " + str(info["unclosed_fence"]) + " 行就成了收尾的那一行。")
        return False
    if info["bad_fences"]:
        ctx.fail("有一行像是代码块的边，但用的不是三个半角反引号 ```", where=where,
                 saw="第 " + str(info["bad_fences"][0]) + " 行")
        return False
    return True


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """State just before 1.5: a copy of the site in state S2, plus hello-fx."""
    sc.site_before()                         # my-site in state S2
    sc.copy_in("starter/hello-fx", "hello-fx")
    sc.fact("practice", "hello-fx")
    sc.todo("网站的副本（这一课用不到它，别在里面写 README；第 2 站的 README 写在你自己的 ~/Developer/my-site 里）："
            + sc.show(sc.facts["site"]))
    sc.todo("第 2 站要写说明的小程序在这里：" + sc.show("hello-fx"))


FOLDERS = {
    "A": {"prefix": "recipes-",
          "files": {"tomato-egg.txt": "西红柿炒蛋\n\n1. 鸡蛋打散\n2. 西红柿切块\n3. 先炒蛋，再炒西红柿\n",
                    "noodles.txt": "葱油拌面\n\n1. 面煮熟\n2. 葱切段，用油慢慢炸香\n3. 浇在面上拌匀\n",
                    "shopping-list.txt": "要买的东西：鸡蛋、西红柿、葱、面条\n"}},
    "B": {"prefix": "trip-",
          "files": {"day-1.txt": "第一天：上午到，下午逛老城区。\n",
                    "day-2.txt": "第二天：爬山，晚上回城。\n",
                    "budget.txt": "交通 300 元\n住宿 400 元\n吃饭 200 元\n"}},
}


def _build_folder(sc, form):
    plan = FOLDERS[form]
    folder = plan["prefix"] + sc.word()
    names = sorted(plan["files"])
    for name in names:
        sc.write(folder + "/" + name, plan["files"][name], exact=True)
    sc.fact("folder", folder)
    sc.fact("files", names)
    sc.fact("file_list", "、".join(names))
    return folder


def build_folder_review(sc):
    """A small folder without a README (do review item)."""
    folder = _build_folder(sc, sc.pick(["A", "B"]))
    sc.todo("要写说明的文件夹在这里：" + sc.show(folder))


SCENARIOS = {
    "start": build_start,
    "1.5b-folder": build_folder_review,
}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
PRACTICE_FILE = "commands.md"


def _find_strays(ctx, info, name):
    """Places a beginner might have saved the practice file by mistake."""
    places = [info.path / "my-site", info.path / "hello-fx", ctx.playground,
              ctx.home / "Developer", ctx.home, ctx.my_site, ctx.workspace]
    found = [ctx.show(place / name) for place in places if ctx.is_file(place / name)]
    near = [entry for entry in ctx.listdir(info.path)
            if entry != name and entry.lower().startswith(name.split(".")[0])]
    return found, near


# The body lines of the worked example weekend.md (lesson.md, station 1 step 3).
WEEKEND_TITLE = "周末计划"
WEEKEND_BODY = (
    "这个周末**最要紧**的是学一站课程。",
    "- 买菜",
    "- 用 `cd` 进入练习场",
    "- 查资料去 [MDN](https://developer.mozilla.org/zh-CN/)",
)


def _weekend_copy(ctx, info, found):
    """What shows that commands.md is the follow-along file, or "".

    Only the file as a whole counts: its level-1 heading is 周末计划, or half
    or more of its body lines are lines of weekend.md.  A link to weekend.md
    or one borrowed line is ordinary work.
    """
    if [title for title in found["h1"] if title == WEEKEND_TITLE]:
        return "一级标题是「" + WEEKEND_TITLE + "」"
    weekend = set(WEEKEND_BODY)
    mine = info.path / "weekend.md"
    if ctx.is_file(mine):
        theirs = scan(ctx.read(mine))
        if WEEKEND_TITLE in theirs["h1"]:     # still the follow-along file
            weekend.update(theirs["body"])
    body = found["body"]
    same = [line for line in body if line in weekend]
    if len(same) >= 2 and len(same) * 2 >= len(body):
        return str(len(same)) + " 行正文和 weekend.md 一样（一共 " + str(len(body)) + " 行）"
    return ""


def check_a(ctx):
    info = ctx.scenario("start")
    target = info.path / PRACTICE_FILE
    where = ctx.show(target)
    if not ctx.is_file(target):
        found, near = _find_strays(ctx, info, PRACTICE_FILE)
        if near:
            ctx.fail("练习文件的名字不对", where=ctx.show(info.path),
                     saw="这里有「" + near[0] + "」，名字要正好是 " + PRACTICE_FILE)
        elif found:
            ctx.fail("练习文件放错了文件夹", where=ctx.show(info.path),
                     saw="这里没有，但在 " + found[0] + " 找到了一个")
        else:
            ctx.fail("还没有找到练习文件 " + PRACTICE_FILE, where=ctx.show(info.path),
                     saw="这个文件夹里没有它")
        ctx.stop()
    names = ctx.listdir(info.path)
    if PRACTICE_FILE not in names:
        actual = [n for n in names if n.lower() == PRACTICE_FILE]
        ctx.note("文件名最好全用小写：现在是「" + (actual[0] if actual else "?") + "」。")
    text = ctx.read(target)
    if not text.strip():
        ctx.fail("文件是空的。写完以后要保存（⌘S），标签页上的圆点消失才算存好", where=where,
                 saw="0 个字")
        ctx.stop()
    found = scan(text)
    copied = _weekend_copy(ctx, info, found)
    if copied:
        ctx.fail("这还是「跟我做」里的周末计划，自己做要换成终端命令小抄", where=where,
                 saw=copied)
    _unclosed_first(ctx, found, where)
    _check_headings(ctx, found, where, 1)
    list_problem = _list_problem(found)
    if len(found["items"]) >= 3:
        ctx.ok("有一个列表，共 " + str(len(found["items"])) + " 项")
    elif list_problem:
        ctx.fail(list_problem[0], where=where, saw=list_problem[1])
    else:
        ctx.fail("列表还不够 3 项", where=where,
                 saw="找到 " + str(len(found["items"])) + " 项")
    commands = known_commands(text)
    if len(commands) >= 3:
        ctx.ok("小抄里写到了 " + str(len(commands)) + " 条学过的命令")
    else:
        ctx.fail("小抄里能认出来的学过的终端命令还不到 3 条（检查认得的是前几课学过的命令名）",
                 where=where,
                 saw=("找到 " + str(len(commands)) + " 条：" + "、".join(commands))
                 if commands else "一条也没认出来")
    if found["inline_code"]:
        ctx.ok("用反引号标出了行内代码")
    elif found["bad_inline_code"]:
        ctx.fail("有命令两边用的不是半角反引号 `，可能是输入法打出了别的字符", where=where,
                 saw="「" + _short(found["bad_inline_code"][0]) + "」")
    elif found["stray_backticks"]:
        ctx.fail("有反引号，但没有配成一对：命令前后的反引号要一样多", where=where,
                 saw="「" + _short(found["stray_backticks"][0]) + "」")
    else:
        ctx.fail("还没有行内代码（一句话里用一对反引号包起来的命令）", where=where, saw="没有找到")
    if _check_fences(ctx, found, where):
        if found["fences"]:
            ctx.ok("有 " + str(found["fences"]) + " 个代码块，开头和收尾都齐了")
            if found["fences_without_lang"]:
                ctx.note("代码块开头那一行的符号后面可以写上是哪种代码，比如 ```zsh：读的人一眼就知道这几行要在终端里敲。")
        else:
            ctx.fail("还没有代码块（上下各一行三个反引号）", where=where, saw="没有找到")
    web_no_scheme = _missing_scheme(ctx, info.path, found)
    if found["links"] or len(web_no_scheme) < len(found["schemeless"]):
        ctx.ok("有一个可以点的链接")
        if web_no_scheme:
            ctx.note(SCHEME_NOTE + "现在是「" + _short(web_no_scheme[0]) + "」。")
    elif web_no_scheme:
        ctx.fail("有一个链接，但圆括号里的网址没有从 https:// 开始写，点了会去找一个同名的文件",
                 where=where, saw="「" + _short(web_no_scheme[0]) + "」")
    elif found["placeholder_links"]:
        ctx.fail("有一个链接，但圆括号里看不出是网址或文件路径", where=where,
                 saw="「" + _short(found["placeholder_links"][0]) + "」")
    elif found["bad_links"]:
        ctx.fail("有一个像链接的写法，但括号是全角的或者中间多了空格", where=where,
                 saw="「" + _short(found["bad_links"][0]) + "」")
    elif found["bare_urls"] or found["autolinks"]:
        ctx.fail("有网址，但还不是「[显示的文字](网址)」这种带文字的链接", where=where,
                 saw="只有网址，没有方括号里的显示文字")
    else:
        ctx.fail("还没有链接", where=where, saw="没有找到")
    if ctx.failed:
        ctx.note(SAVE_NOTE)


README_NAME = "README.md"
HELLO_FX_MARKS = ("convert.py", "rates.txt", "换算一笔钱")


def _template_lines(ctx):
    """Body lines of the course's README template, if that file exists."""
    lines = []
    for line in ctx.lines("templates/readme-template.md"):
        stripped = line.strip()
        if stripped.startswith("#") or len(stripped) < 6:
            continue
        stripped = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", stripped)
        if len(stripped) >= 6:
            lines.append(stripped)
    return set(lines)


def _starts_with_h1(text):
    """The first non-empty line is a level-1 heading (# Title, or Title over ===)."""
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        return False
    heading = HEADING.match(lines[0])
    if heading and len(heading.group(1)) == 1:
        return True
    return len(lines) > 1 and bool(SETEXT_H1.match(lines[1]))


def _readme_name_problem(ctx, folder):
    """Return a fail text when the README exists under a wrong name."""
    names = ctx.listdir(folder)
    if README_NAME in names:
        return None, None
    for name in names:
        low = name.lower()
        if low == "readme.md":
            return "文件名要写成大写的 README.md，这是约定俗成的写法", name
        if low.startswith("readme"):
            return "README 的文件名要一字不差地写成 README.md", name
    return None, None


def check_b(ctx):
    site = ctx.path(ctx.my_site)
    if not ctx.is_dir(site):            # silent when present: 1.5 did not build it
        ctx.fail("还没有找到你的网站文件夹 my-site", where=ctx.show(site), saw="这个文件夹不存在")
        ctx.stop()
    readme = site / README_NAME
    where = ctx.show(readme)
    problem, wrong = _readme_name_problem(ctx, site)
    if problem:
        ctx.fail(problem, where=ctx.show(site), saw="现在叫「" + wrong + "」")
        ctx.stop()
    if not ctx.is_file(readme):
        start = ctx.scenario("start", required=False)
        copy = None
        if start.exists:
            candidate = start.path / start.facts.get("site", "my-site") / README_NAME
            if ctx.is_file(candidate):
                copy = ctx.show(candidate)
        if copy:
            ctx.fail("README.md 写在了练习场的副本里，要写在你自己的 ~/Developer/my-site 里",
                     where=ctx.show(site), saw="这里没有，副本 " + copy + " 里有")
        else:
            ctx.fail("my-site 里还没有 README.md", where=ctx.show(site), saw="没有这个文件")
        ctx.stop()
    text = ctx.read(readme)
    if not text.strip():
        ctx.fail("README.md 是空的。写完要保存（⌘S）", where=where, saw="0 个字")
        ctx.stop()
    marks = [mark for mark in HELLO_FX_MARKS if mark in text]
    if marks:
        ctx.fail("这里写的像是 hello-fx 的说明，my-site 要写它自己", where=where,
                 saw="里面提到了「" + marks[0] + "」")
    holder = placeholder_line(text)
    if holder:
        ctx.fail("还有模板里的提示或留空的横线，没换成 my-site 自己的话", where=where,
                 saw="第 " + str(holder[0]) + " 行「" + _short(holder[1], 30) + "」")
    found = scan(text)
    _unclosed_first(ctx, found, where)
    template = _template_lines(ctx)
    if template and found["body"]:
        same = [line for line in found["body"]
                if re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", line) in template]
        if len(same) * 2 >= len(found["body"]):
            ctx.fail("正文大半和模板一模一样，要换成 my-site 自己的话", where=where,
                     saw=str(len(same)) + " 行和 templates/readme-template.md 相同")
    _check_headings(ctx, found, where, 3)
    list_problem = _list_problem(found)
    if found["items"]:
        ctx.ok("有一个列表")
    elif list_problem:
        ctx.fail(list_problem[0], where=where, saw=list_problem[1])
    else:
        ctx.fail("还没有列表", where=where, saw="没有找到以「- 」开头的行")
    fences_ok = _check_fences(ctx, found, where)
    web_no_scheme = _missing_scheme(ctx, site, found)
    has_link = (found["links"] or found["autolinks"] or found["bare_urls"]
                or len(web_no_scheme) < len(found["schemeless"]))
    if fences_ok and (found["fences"] or has_link):
        ctx.ok("有代码块或链接，读者可以照着做或点过去")
        if web_no_scheme:
            ctx.note(SCHEME_NOTE + "现在是「" + _short(web_no_scheme[0]) + "」。")
    elif fences_ok:
        if web_no_scheme:
            ctx.fail("有一个链接，但圆括号里的网址没有从 https:// 开始写，点了会去找一个同名的文件；"
                     "也还没有代码块", where=where, saw="「" + _short(web_no_scheme[0]) + "」")
        elif found["placeholder_links"]:
            ctx.fail("有一个链接，但圆括号里看不出是网址或文件路径；也还没有代码块", where=where,
                     saw="「" + _short(found["placeholder_links"][0]) + "」")
        elif found["bad_links"]:
            ctx.fail("有一个像链接的写法，但括号是全角的或者中间多了空格", where=where,
                     saw="「" + _short(found["bad_links"][0]) + "」")
        else:
            ctx.fail("还没有代码块，也没有链接", where=where, saw="两样都没找到")
    if "index.html" in text:
        ctx.ok("说明里提到了 index.html")
    else:
        ctx.fail("还没说文件夹里有什么：至少要提到 index.html", where=where,
                 saw="没有出现 index.html")
    if found["email"]:
        ctx.note("README 里有一个邮箱地址。1.13 课这个文件会公开，不想公开就换成笔名或删掉。")
    if not _starts_with_h1(text):
        ctx.note("小提示：一级标题通常写在第一行（检查 Markdown 写法的常用工具 markdownlint 有一条规则 MD041 就这样要求）。")
    if ctx.failed:
        ctx.note(SAVE_NOTE)


checks = {"1.5a": check_a, "1.5b": check_b}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.5a": [
        "检查结果里「还缺什么」点出的是哪一种元素？把它和课文第 1 站「跟我做」里的 weekend.md 对照着看：同一种元素在那里是怎么写的。",
        ("文件要在 ~/Developer/playground/1.5-start 里，名字正好是 commands.md。用 VS Code 打开它，按 ⇧⌘V 看预览：预览里不像标题、列表、代码或链接的地方，就是还要改的地方。"
         "检查读的是存好的文件：预览里明明有、检查却说没有，先按 ⌘S 保存（标签页上的圆点要消失）再检查。"),
        ("相似的例子（内容换成了买菜）：\n"
         "# 买菜清单\n\n## 要买的\n\n- 鸡蛋\n- 葱\n- 面条\n\n## 记账\n\n"
         "用 `cat` 看账本：\n\n```zsh\ncat money.txt\n```\n\n"
         "[菜价参考](https://example.com)"),
        ("答案（一种写法）：\n"
         "# 我的终端命令小抄\n\n## 看位置和文件\n\n"
         "- `pwd`：显示我现在在哪个文件夹\n- `ls -a`：列出文件，包括隐藏的\n- `cat`：把文件内容打印出来\n\n"
         "## 一个完整的例子\n\n```zsh\ncd ~/Developer/my-site\nls -l\n```\n\n"
         "[MDN 命令行入门](https://developer.mozilla.org/zh-CN/docs/Learn_web_development/Getting_started/Environment_setup/Command_line)\n\n"
         "解释：一个 # 加空格是一级标题，两个 # 是小节；「- 」开头是列表；一对反引号是行内代码；"
         "上下两行 ``` 围起来是代码块；[文字](网址) 是链接。符号都要用半角，# 和 - 后面都要有空格。"),
    ],
    "1.5b": [
        "README 要回答陌生人最先想问的几个问题：这是什么、怎么看到效果、里面有什么、现在做到哪了。检查结果里缺的是哪一块？",
        ("文件是 ~/Developer/my-site/README.md（大写 README，小写 .md），不是练习场里的副本。用 VS Code 打开 my-site 文件夹（在 my-site 里运行 code .），在左边的文件列表里能看到它。"
         "检查读的是存好的文件：写完先按 ⌘S 保存（标签页上的圆点要消失）再检查。"),
        "相似的例子：第 2 站「跟我做」给 hello-fx 写的 README。它的结构可以照搬，内容要换成 my-site 自己的：它是一个网页，看效果的方法和运行 Python 程序不一样。",
        ("答案（一种写法，把笔名换成你自己的）：\n"
         "# my-site\n\n阿青的个人网页：只有一页，是我学做软件的第一个作品。\n\n"
         "## 怎么查看\n\n在终端里进入这个文件夹，运行：\n\n```zsh\nopen index.html\n```\n\n"
         "## 里面有什么\n\n- `index.html`：网页的内容\n- `style.css`：网页的样式\n"
         "- `.editorconfig`：告诉编辑器用 UTF-8 和 LF（第 1.4 课写的）\n\n"
         "## 现在做到哪了\n\n还在学习中。下一步：学会用 Git 记录每一次改动。\n\n"
         "## 作者和许可\n\n作者：阿青。许可证第 1.13 课再加。\n\n"
         "解释：一个一级标题说明是什么；每个 ## 小节回答一个问题；列表列出文件；"
         "代码块放读者可以照着敲的命令。第五个问题的许可证部分第 1.13 课补上。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
def _folder_readme(ctx, info):
    """Shared by the do item and exam task x1: a README for a small folder."""
    folder = info.path / info.facts["folder"]
    where = ctx.show(folder / README_NAME)
    if not ctx.is_dir(folder):          # silent when present: the tool built it
        ctx.fail("要写说明的文件夹不见了", where=ctx.show(folder), saw="这个文件夹不存在")
        ctx.stop()
    problem, wrong = _readme_name_problem(ctx, folder)
    if problem:
        ctx.fail(problem, where=ctx.show(folder), saw="现在叫「" + wrong + "」")
        ctx.stop()
    if not ctx.is_file(folder / README_NAME):
        if ctx.is_file(info.path / README_NAME):
            ctx.fail("README.md 放在了上一层，要放进 " + info.facts["folder"] + " 里面",
                     where=ctx.show(folder), saw="这里没有，" + ctx.show(info.path / README_NAME) + " 有")
        else:
            ctx.fail("文件夹里还没有 README.md", where=ctx.show(folder), saw="没有这个文件")
        ctx.stop()
    text = ctx.read(folder / README_NAME)
    if not text.strip():
        ctx.fail("README.md 是空的，写完要保存", where=where, saw="0 个字")
        ctx.stop()
    found = scan(text)
    _unclosed_first(ctx, found, where)
    _check_headings(ctx, found, where, 2)
    list_problem = _list_problem(found)
    if found["items"]:
        ctx.ok("有一个列表")
    elif list_problem:
        ctx.fail(list_problem[0], where=where, saw=list_problem[1])
    else:
        ctx.fail("还没有列表", where=where, saw="没有找到以「- 」开头的行")
    missing = [name for name in info.facts["files"] if name not in text]
    ctx.expect(not missing, "说明里提到了每一个文件", "还有文件没在说明里提到", where=where,
               saw="少了 " + str(len(missing)) + " 个" if missing else "")
    _check_fences(ctx, found, where)


def _do_folder_readme(ctx):
    _folder_readme(ctx, ctx.scenario("1.5b-folder"))


REVIEW = [
    {"id": "1.5-heading-space", "type": "predict", "tier": "fluent", "station": "1.5a",
     "q": "Markdown 文件里有这样一行，预览里会显示成什么？\n\n    #我的笔记",
     "options": ["一个一级标题「我的笔记」", "一行普通文字「#我的笔记」", "什么都不显示"],
     "answer": "B",
     "explain": "# 后面必须有一个空格才是标题（CommonMark 规范的规定）。没有空格，它就是普通文字。"},
    {"id": "1.5-link", "type": "which", "tier": "fluent", "station": "1.5a",
     "q": "在 Markdown 里写一个显示为「MDN」、点了去 https://developer.mozilla.org 的链接，哪种写法对？",
     "options": ["[MDN](https://developer.mozilla.org)",
                 "(MDN)[https://developer.mozilla.org]",
                 "【MDN】（https://developer.mozilla.org）"],
     "answer": "A", "shuffle": True,
     "explain": "方括号里放显示的文字，紧跟着圆括号里放网址，中间没有空格，括号都是半角的。"},
    {"id": "1.5-fence", "type": "recall", "tier": "fluent", "station": "1.5a",
     "q": "想在 Markdown 里放几行命令，让它们原样显示成代码，怎么写？最容易漏掉哪一步？",
     "a": "上面一行写三个反引号 ```（可以接语言名，比如 ```zsh），中间放命令，下面再写一行 ```。最容易漏掉收尾的那一行：漏了，后面所有内容都会变成代码。"},
    {"id": "1.5-readme-questions", "type": "recall", "tier": "fluent", "station": "1.5b",
     "rule": "DOC-02",
     "q": "一个项目的 README 应该回答哪几个问题？说出四个以上。",
     "a": "这是什么；怎么用或怎么看到效果；文件夹里有什么；现在的状态和下一步打算；作者是谁、用什么许可证。",
     "explain": "GitHub 的文档列的是：项目做什么、为什么有用、怎么开始、去哪求助、谁在维护。"},
    {"id": "1.5-readme-place", "type": "which", "tier": "lookup", "station": "1.5b",
     "rule": "DOC-01",
     "q": "一个项目的 README.md 通常放在哪里，GitHub 才会在项目首页直接显示它？",
     "options": ["项目最外层的文件夹（根目录）", "随便哪个子文件夹", "电脑的桌面上"],
     "answer": "A",
     "explain": "GitHub 先找 .github（放 GitHub 专用设置的隐藏文件夹），再找根目录，最后找 docs（放文档的子文件夹）；惯例是放在根目录。"},
    {"id": "1.5-do-readme", "type": "do", "tier": "lookup", "station": "1.5b",
     "q": "练习场里有一个还没有说明的小文件夹。给它写一个 README.md：一个一级标题，至少两个小节，用列表说出里面每个文件是什么。",
     "scenario": "1.5b-folder", "check": _do_folder_readme},
]


# ---------------------------------------------------------------------------
# EXAM (gate-a)
# ---------------------------------------------------------------------------
def build_x1(sc):
    _build_folder(sc, sc.form)      # the task text names the folder and the cd


def grade_x1(ctx):
    _folder_readme(ctx, ctx.scenario())


TITLES = ["学习笔记", "读书摘抄", "做饭心得", "跑步记录", "旅行清单"]
ITEMS = ["早上", "中午", "晚上", "周一", "周三", "周五", "第一章", "第二章", "第三章"]


def build_x2(sc):
    """A Markdown file with three seeded faults (form A and B differ)."""
    name = "notes-" + sc.word() + ".md"
    title = sc.pick(TITLES)
    items = sc.sample(ITEMS, 3)
    section = sc.pick(["要点", "记录", "备忘"])
    command = sc.pick(["ls -a", "pwd", "cat notes.txt"])
    sc.fact("file", name)
    sc.fact("title", title)
    sc.fact("items", items)
    sc.fact("section", section)
    sc.fact("command", command)
    if sc.form == "A":
        url = "https://developer.mozilla.org/zh-CN/"
        text = ("#" + title + "\n\n## " + section + "\n\n"
                + "".join("-" + item + "\n" for item in items)
                + "\n## 参考\n\n【MDN 文档】（" + url + "）\n")
        sc.fact("url", url)
    else:
        sc.fact("url", "")
        text = ("# " + title + "\n\n## " + section + "\n\n"
                + "".join("- " + item + "\n" for item in items)
                + "\n## 常用命令\n\n这次用到的命令是 ｀" + command + "｀。\n\n"
                + "```zsh\n" + command + "\n\n"
                + "# 下一步\n\n继续练习。\n")
    sc.write(name, text, exact=True)


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    target = info.path / facts["file"]
    where = ctx.show(target)
    if not ctx.is_file(target):
        ctx.fail("题目里的文件不见了", where=ctx.show(info.path), saw="没有找到 " + facts["file"])
        ctx.stop()
    text = ctx.read(target)
    found = scan(text)
    lost = [word for word in [facts["title"], facts["section"]] + list(facts["items"])
            if word not in text]
    if lost:        # silent when nothing was lost: an untouched file keeps its text too
        ctx.fail("有原来的文字被删掉了", where=where, saw="少了 " + str(len(lost)) + " 处")
    title_ok = facts["title"] in "".join(found["h1"]) and len(found["h1"]) == 1
    if not title_ok:
        ctx.fail("一级标题还不对：要有、而且只有一个", where=where,
                 saw="一级标题有 " + str(len(found["h1"])) + " 个")
    elif info.form == "A":      # only form A starts with a broken title: praise only real work
        ctx.ok("标题「" + facts["title"] + "」显示成了一级标题")
    if info.form == "A":
        good = [item for item in facts["items"] if any(item in line for line in found["items"])]
        ctx.expect(len(good) == len(facts["items"]), "列表的每一项都显示成了列表",
                   "还有列表项不是真正的列表", where=where,
                   saw=str(len(good)) + " / " + str(len(facts["items"])) + " 项是列表")
        wanted = facts["url"].rstrip("/")
        clickable = [t for t in found["targets"] if t.strip("<>").rstrip("/") == wanted]
        ctx.expect(bool(clickable), "链接写对了，预览里能点",
                   "链接还没有写成能点的样子", where=where,
                   saw="没有找到指向原来那个网址、预览里能点的链接")
    else:
        if _check_fences(ctx, found, where):
            ctx.ok("代码块有头有尾")
        heads = found["h2"] + found["deeper"]
        ctx.expect(any("下一步" in head for head in heads), "「下一步」成了小节标题",
                   "「下一步」还不是小节标题", where=where, saw="它现在不是二级标题")
        ctx.expect(found["inline_code"] >= 1 and not found["bad_inline_code"],
                   "命令显示成了行内代码", "句子里的命令还没有显示成代码", where=where,
                   saw="两边的符号不是半角反引号")


EXAM = [
    {
        "id": "1.5-x1",
        "gate": "gate-a",
        "title": "给一个文件夹写 README",
        "minutes": 8,
        "build": build_x1,
        "task": {
            "A": ("先 cd 进 {dir}/{folder}：这个文件夹里有几份菜谱（{file_list}），但没有任何说明。"
                  "就在这个文件夹里写一个 README.md：只有一个一级标题，至少两个小节，其中一个小节用列表说出每个文件是什么。"),
            "B": ("先 cd 进 {dir}/{folder}：这是一次旅行的计划，里面的文件是 {file_list}。"
                  "就在这个文件夹里面（不是外面那一层）加一份说明书 README.md，让别人一眼看懂：只有一个一级标题，至少两个二级标题，用列表介绍每一个文件。"),
        },
        "grade": grade_x1,
    },
    {
        "id": "1.5-x2",
        "gate": "gate-a",
        "title": "修好一份显示不对的 Markdown",
        "minutes": 7,
        "build": build_x2,
        "task": {
            "A": ("{dir}/{file} 在预览里有三处不对：标题没有显示成标题，列表没有显示成列表，链接点不了。"
                  "改好这三处，原来的文字不要删。"),
            "B": ("{dir}/{file} 在预览里有三处不对：从某一行开始，后面全变成了代码的样子；"
                  "「下一步」本该是一个小节标题；句子里的命令没有显示成代码。改好这三处，原来的文字不要删。"),
        },
        "grade": grade_x2,
    },
]
