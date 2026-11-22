"""Lesson 1.4: the editor VS Code (plan section 4).

Station a: open the project folder with ``code .``, edit and save index.html,
look at it in the browser with ``open index.html``.
Station b: finding things by name: the Command Palette (functions), Quick
Open (files), search across files (text), and the integrated terminal opened
from the palette.
Station c: text encoding and line endings as one idea, written down as an
``.editorconfig`` for my-site.

The clicks in VS Code cannot be checked, so the checks look at what the
clicks leave behind: the learner's ``~/Developer/my-site/index.html`` (station
a), an answer that only a search across the practice folder gives (station
b), and ``~/Developer/my-site/.editorconfig`` (station c).  Standard library
only, Python 3.9 syntax; every helper comes through ``ctx`` and ``sc``
(docs/authoring/tool-api.md).
"""

import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.4",
    "slug": "04-editor",
    "title": "编辑器 VS Code",
    "stage": 1,
    "prerequisites": ["1.3"],
    "stations": [
        {
            "id": "1.4a",
            "title": "打开文件夹、编辑、保存、在浏览器里看效果",
            "minutes": 40,
            "new_concept": "编辑器打开的是整个项目文件夹，改完要保存，文件才真的变了",
            "new_commands": ["code .", "open"],
        },
        {
            "id": "1.4b",
            "title": "命令面板、快速打开、搜索和内置终端",
            "minutes": 30,
            "new_concept": "按名字找：命令面板找功能，快速打开找文件，跨文件搜索找文字",
            "new_commands": [],
        },
        {
            "id": "1.4c",
            "title": "编码、换行和 .editorconfig",
            "minutes": 40,
            "new_concept": "文本文件的格式（字符编码和换行符）要写成项目里的约定：.editorconfig",
            "new_commands": [],
        },
    ],
    "rules": ["ED-01", "ED-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"code": "1.145.2", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9"},
    },
    "unverified_steps": [
        "1.4a：菜单 Code > Quit Visual Studio Code 退出 VS Code；code index.html 只打开一个文件时资源管理器显示 NO FOLDER OPENED"
        "（可能先弹出 Do you want to allow untrusted files in this window?；VS Code 恢复了上次的文件夹时用 File > Close Folder）；⇧⌘E",
        "1.4a：在终端里运行 code . 后 VS Code 打开文件夹的窗口（受限模式横幅、资源管理器 MY-SITE）；全角的 。 让 VS Code 打开一个叫 。 的文件",
        "1.4a：受限模式横幅里信任文件夹（Manage，再在 Workspace Trust 页面上点 Trust）",
        "1.4a：编辑器标签页上的圆点；⌘S 保存后圆点消失",
        "1.4a：open index.html 在默认浏览器里打开网页，⌘R 刷新后看到改动（找不到文件时的报错已实测）",
        "1.4b、1.4c：练习文件夹打开时的受限模式横幅，照第 1 站的办法信任（受限模式里不能开终端）",
        "1.4b：⇧⌘P 命令面板、Terminal: Create New Terminal、⌃⇧` 和 ⌃`；内置终端从打开的文件夹开始（pwd、cat 的输出已实测）",
        "1.4b：⌘P 快速打开按文件名找到 plan.md，右边灰字显示所在的文件夹",
        "1.4b：⇧⌘F 搜“汇率”列出两个文件（等价的 grep -rn 已实测）",
        "1.4c：⌘P 打开 GBK 文件显示乱码；状态栏里 old-pc.txt 显示 CRLF、today.md 显示 LF；"
        "⇧⌘F 搜“汇率”只列出 today.md（等价的 grep 已实测）",
        "1.4c：在资源管理器里新建文件 .editorconfig；打开它时右下角推荐 EditorConfig 扩展的提示",
        "想多了解：File > Auto Save 开关",
        "想多了解：安装 EditorConfig 扩展（⇧⌘X 或命令面板里的 View: Show Extensions、Trust Publisher & Install；"
        "命令名和快捷键在 1.145.2 安装包里核对过）",
    ],
}

TERMS = [
    {"term": "受限模式", "en": "Restricted Mode",
     "plain": "VS Code 打开一个还没被你信任的文件夹时的安全模式：能看能改，但不自动运行里面的东西",
     "first": "1.4a"},
    {"term": "资源管理器", "en": "Explorer",
     "plain": "VS Code 左边那一栏，列出打开的文件夹里所有的文件", "first": "1.4a"},
    {"term": "自动保存", "en": "Auto Save",
     "plain": "停手一秒左右，编辑器就替你把改动写进文件", "first": "1.4a"},
    {"term": "标签", "en": "tag",
     "plain": "网页文件里尖括号括起来的记号，比如 <h1>，告诉浏览器中间的字是什么；"
              "不是 VS Code 顶上的标签页（tab）", "first": "1.4a"},
    {"term": "命令面板", "en": "Command Palette",
     "plain": "按 ⇧⌘P 弹出的输入框，输入功能的名字就能用这个功能", "first": "1.4b"},
    {"term": "快速打开", "en": "Quick Open",
     "plain": "按 ⌘P 弹出的输入框，输入文件名的几个字母就能打开文件", "first": "1.4b"},
    {"term": "跨文件搜索", "en": "search across files",
     "plain": "按 ⇧⌘F，在打开的文件夹的所有文件里找一串字", "first": "1.4b"},
    {"term": "内置终端", "en": "integrated terminal",
     "plain": "VS Code 窗口下方的终端，和你平时用的是同一个 zsh", "first": "1.4b"},
    {"term": "字符编码", "en": "character encoding",
     "plain": "把文字存成字节的一套对照表；读和写用的不是同一套，就出乱码", "first": "1.4c"},
    {"term": "换行符", "en": "line ending",
     "plain": "文件里表示“这一行结束了”的看不见的字符；Mac 用 LF，Windows 常用 CRLF",
     "first": "1.4c"},
    {"term": "缩进", "en": "indentation",
     "plain": "一行开头空出来的那一段，用来表示这一行在上一层里面", "first": "1.4c"},
    {"term": "扩展", "en": "extension",
     "plain": "给 VS Code 加功能的附加程序，要另外安装（不是第 1.5 课的扩展名）", "first": "1.4c"},
    {"term": "EditorConfig", "en": "EditorConfig",
     "plain": "一份写在项目里的 .editorconfig 文件，告诉各种编辑器这个项目的文本统一用什么格式",
     "first": "1.4c"},
]


# ---------------------------------------------------------------------------
# Shared reading helpers (pure functions, no file access of their own)
# ---------------------------------------------------------------------------
STARTER_HEADING = "你好，我是____"
STARTER_PARAGRAPH = "这是我的第一个网页。我正在从零开始学习做软件。"
STARTER_TITLE = "我的第一个网页"

TAG_RE = re.compile(r"<[^>]*>")
FULL_WIDTH_NAMES = {
    "　": "全角空格", "＝": "全角的 ＝", "［": "全角的 ［", "］": "全角的 ］",
    "【": "全角的 【", "】": "全角的 】",
    "｛": "全角的 ｛", "｝": "全角的 ｝", "，": "全角的逗号 ，", "、": "顿号 、",
    "＊": "全角的 ＊", "．": "全角的 ．", "。": "句号 。", "＃": "全角的 ＃", "；": "全角的 ；",
    "：": "全角的冒号 ：",
}
FULL_WIDTH = "".join(FULL_WIDTH_NAMES)

SAVE_NOTE = "如果编辑器里已经写了内容：看标签页上的文件名旁边有没有圆点，有圆点就是还没保存（⌘S）。"


def _strip_tags(text):
    return re.sub(r"\s+", " ", TAG_RE.sub("", text)).strip()


def _nospace(text):
    """Text without any whitespace: 「和 Git」 and 「和Git」 compare equal."""
    return re.sub(r"\s+", "", text)


def _short(text, limit=24):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit] + "…"


def _page_findings(ctx, page_path, label, starter_heading=True, starter_paragraph=True):
    """Look at an edited copy of the starter page.

    Records ok / fail through ctx and returns (heading_text, paragraphs).
    ``starter_heading`` / ``starter_paragraph``: whether this task requires
    the starter's heading / paragraph to be gone.
    """
    raw = ctx.read_bytes(page_path)
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        ctx.fail("文件不是用 UTF-8 存的，网页里会出现乱码", where=label,
                 saw="有按 UTF-8 读不懂的字节")
        ctx.stop()
    text = ctx.read(page_path)
    lower = text.lower()

    if "{\\rtf" in text[:40]:
        ctx.fail("文件被存成了带格式的文档（富文本，RTF），不再是纯文本的网页", where=label,
                 saw="开头是 {\\rtf")
        ctx.stop()

    if "＜" in text or "＞" in text:
        ctx.fail("有尖括号是全角的，网页只认半角的尖括号", where=label,
                 saw="找到了全角的 ＜ 或 ＞")

    # The skeleton of the page must still be there.
    needed = [
        ("<!doctype html>", "<!DOCTYPE html>"),
        ("<html", "<html"),
        ("<head>", "<head>"),
        ('<meta charset="utf-8">', '<meta charset="utf-8">'),
        ("<title>", "<title>"),
        ("</title>", "</title>"),
        ("</head>", "</head>"),
        ("<body>", "<body>"),
        ("</body>", "</body>"),
        ("</html>", "</html>"),
    ]
    missing = [shown for probe, shown in needed if probe not in lower]
    if missing:
        ctx.fail("网页的骨架缺了一块：只改标签中间的文字，标签本身要留着",
                 where=label, saw="找不到 " + "、".join(missing[:3]))
    elif STARTER_HEADING not in text or STARTER_PARAGRAPH not in text:
        # Praise the intact skeleton only once the learner has edited something.
        ctx.ok("改过以后，网页的骨架都还在（<head>、<title>、<body> 和开头的 <!DOCTYPE html>）")
    if "style.css" not in lower:
        ctx.fail("网页和样式文件的连接断了", where=label, saw="找不到 style.css")

    # The heading (<h1>, called 大标题 in the lesson; <title> is the 网页标题).
    opens = len(re.findall(r"<h1[\s>]", lower))
    closes = lower.count("</h1>")
    headings = re.findall(r"<h1[^>]*>(.*?)</h1>", text, flags=re.S | re.I)
    heading = None
    if opens != 1 or closes != 1 or len(headings) != 1:
        ctx.fail("大标题那一行的标签不完整：要有一个 <h1> 和一个 </h1>", where=label + " 的大标题",
                 saw="<h1> 有 {} 个，</h1> 有 {} 个".format(opens, closes))
    else:
        heading = _strip_tags(headings[0])
        if starter_heading:
            rest = heading.replace("_", "").replace("＿", "")
            rest = rest.replace("你好，我是", "").replace("你好,我是", "").strip(" ：:，,")
            if "__" in heading or "＿" in heading:
                if rest:
                    ctx.fail("名字写上了，下划线 ____ 还要删掉", where=label + " 的大标题",
                             saw="现在是「{}」".format(_short(heading)))
                else:
                    ctx.fail("大标题里的空还没有填", where=label + " 的大标题",
                             saw="现在是「{}」".format(_short(heading)))
            elif not rest:
                ctx.fail("大标题里还没有名字", where=label + " 的大标题",
                         saw="现在是「{}」".format(_short(heading) or "空的"))
            else:
                ctx.ok("大标题改好了：「{}」".format(_short(heading)))

    # The paragraph(s).
    p_opens = len(re.findall(r"<p[\s>]", lower))
    p_closes = lower.count("</p>")
    paragraphs = [_strip_tags(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", text, flags=re.S | re.I)]
    if p_opens != p_closes:
        ctx.fail("段落的标签不成对：每个 <p> 后面都要有一个 </p>", where=label + " 的段落",
                 saw="<p> 有 {} 个，</p> 有 {} 个".format(p_opens, p_closes))
    elif not any(paragraphs):
        ctx.fail("找不到那一段话", where=label, saw="没有写着字的 <p>…</p>")
    elif starter_paragraph:
        if STARTER_PARAGRAPH in _strip_tags(text):
            ctx.fail("那一段话还是起步网页里的原话", where=label + " 的段落",
                     saw="还是「{}」".format(_short(STARTER_PARAGRAPH)))
        else:
            ctx.ok("那一段话换成了新的：「{}」".format(_short([p for p in paragraphs if p][0])))

    # The list and the link should survive the edit.
    if "<ul>" not in lower or "</ul>" not in lower or "<li>" not in lower:
        ctx.fail("下面的列表被删掉或弄坏了", where=label, saw="找不到完整的 <ul>…</ul>")
    if b"\r\n" in raw:
        ctx.note("这个文件里有 Windows 式的换行（CRLF）。第 3 站会讲为什么统一用 LF。")
    return heading, paragraphs


# ---------------------------------------------------------------------------
# A small EditorConfig reader (spec 0.17.2: sections, key = value, globs)
# ---------------------------------------------------------------------------
KNOWN_VALUES = {
    "charset": {"latin1", "utf-8", "utf-8-bom", "utf-16be", "utf-16le", "unset"},
    "end_of_line": {"lf", "cr", "crlf", "unset"},
    "insert_final_newline": {"true", "false", "unset"},
    "trim_trailing_whitespace": {"true", "false", "unset"},
    "indent_style": {"tab", "space", "unset"},
    "root": {"true", "false"},
}
# A section header that is only one of these words ([html]) matches a file named exactly
# that, not the files with that extension: a likely slip after [*.md].
BARE_EXTENSIONS = {"html", "htm", "css", "md", "py", "txt"}


def _glob_regex(glob):
    """EditorConfig glob -> compiled regex, or None if it cannot be read."""
    out = []
    depth = 0
    i = 0
    while i < len(glob):
        ch = glob[i]
        if ch == "\\" and i + 1 < len(glob):
            out.append(re.escape(glob[i + 1]))
            i += 2
            continue
        if ch == "*":
            if glob[i:i + 2] == "**":
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
        elif ch == "?":
            out.append("[^/]")
        elif ch == "[":
            end = glob.find("]", i + 1)
            if end == -1:
                out.append(re.escape(ch))
            else:
                body = glob[i + 1:end]
                if body.startswith("!"):
                    body = "^" + re.escape(body[1:])
                else:
                    body = re.escape(body)
                out.append("[" + body + "]")
                i = end
        elif ch == "{":
            depth += 1
            out.append("(?:")
        elif ch == "," and depth > 0:
            out.append("|")
        elif ch == "}" and depth > 0:
            depth -= 1
            out.append(")")
        else:
            out.append(re.escape(ch))
        i += 1
    if depth != 0:
        return None
    try:
        return re.compile("(?:" + "".join(out) + r")\Z")
    except re.error:
        return None


def _glob_matches(glob, rel_path):
    glob = glob.strip()
    if glob.startswith("/"):
        glob = glob[1:]
        target = rel_path
    elif "/" in glob:
        target = rel_path
    else:
        target = rel_path.rsplit("/", 1)[-1]
    regex = _glob_regex(glob)
    return bool(regex and regex.match(target))


def _parse_editorconfig(text):
    """Return (preamble, sections, problems).

    preamble: {key: (value, lineno)}; sections: [(glob, {key: (value, lineno)}, lineno)];
    problems: [(lineno, kind, line)] with kind in fullwidth / no-equals / bad-section.
    """
    preamble = {}
    sections = []
    problems = []
    current = preamble
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped[0] in "#;":
            continue
        if any(ch in stripped for ch in FULL_WIDTH):
            problems.append((number, "fullwidth", stripped))
            continue
        if stripped.startswith("["):
            if not stripped.endswith("]") or len(stripped) < 3:
                problems.append((number, "bad-section", stripped))
                continue
            current = {}
            sections.append((stripped[1:-1], current, number))
            continue
        if "=" not in stripped:
            problems.append((number, "no-equals", stripped))
            continue
        key, value = stripped.split("=", 1)
        current[key.strip().lower()] = (value.strip(), number)
    return preamble, sections, problems


def _effective(sections, rel_path):
    """Properties that apply to rel_path: later sections win."""
    props = {}
    for glob, pairs, _number in sections:
        if _glob_matches(glob, rel_path):
            for key, (value, number) in pairs.items():
                props[key] = (value, number)
    return props


def _editorconfig_findings(ctx, folder, label, requirements):
    """Grade the .editorconfig in ``folder``.

    requirements: list of (paths, key, value, wording) meaning that for every
    path in ``paths`` the effective ``key`` must equal ``value``.
    Returns True when the file was there and could be read.
    """
    names = ctx.listdir(folder)
    if ".editorconfig" not in names:
        near = [n for n in names if "editorconfig" in n.lower().replace(" ", "")]
        if near and near[0][:1] in "。．":
            ctx.fail("文件名开头的点是全角的，要用半角的 .（切回英文输入法再打）", where=label,
                     saw="找到的是「{}」".format(ctx.visible(near[0])))
        elif near:
            ctx.fail("文件名要一字不差：开头一个点，全是小写，后面不加 .txt 之类的结尾", where=label,
                     saw="找到的是「{}」".format(ctx.visible(near[0])))
        else:
            ctx.fail(".editorconfig 还没有建", where=label, saw="这个文件夹里没有 .editorconfig")
        return False
    path = folder / ".editorconfig"
    if not ctx.is_file(path):
        ctx.fail(".editorconfig 要是一个文件", where=label, saw="它现在是一个文件夹")
        return False
    raw = ctx.read_bytes(path)
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        ctx.fail(".editorconfig 本身也要用 UTF-8 存", where=label + "/.editorconfig",
                 saw="有按 UTF-8 读不懂的字节")
        return False
    text = ctx.read(path)
    if not text.strip():
        ctx.fail(".editorconfig 是空的", where=label + "/.editorconfig", saw="里面一个字也没有")
        return True
    ctx.ok("文件 .editorconfig 在，名字也对")

    preamble, sections, problems = _parse_editorconfig(text)
    for number, kind, line in problems[:3]:
        where = label + "/.editorconfig 第 {} 行".format(number)
        if kind == "fullwidth":
            found = [FULL_WIDTH_NAMES[ch] for ch in FULL_WIDTH if ch in line]
            ctx.fail("这一行里有全角符号，EditorConfig 只认半角", where=where,
                     saw="「{}」里有{}".format(_short(line), "、".join(found)))
        elif kind == "bad-section":
            ctx.fail("方括号那一行没有写完整", where=where, saw="「{}」".format(_short(line)))
        else:
            ctx.fail("这一行既不是 [文件范围]，也不是 名字 = 值", where=where,
                     saw="「{}」".format(_short(line)))

    root_in_section = [n for _g, pairs, _n in sections for k, (_v, n) in pairs.items() if k == "root"]
    if "root" in preamble and preamble["root"][0].lower() == "true":
        ctx.ok("开头写明了 root = true")
    elif "root" in preamble:
        ctx.fail("root 的值不对", where=label + "/.editorconfig 第 {} 行".format(preamble["root"][1]),
                 saw="root = " + preamble["root"][0])
    elif root_in_section:
        ctx.fail("root = true 要写在第一个 [ ] 之前", where=label + "/.editorconfig",
                 saw="它在第 {} 行，已经进了某一块的里面".format(root_in_section[0]))
    elif any("root" in line.lower() for _n, _k, line in problems[:3]):
        # The root line is there but unreadable; that line has been reported above.
        pass
    else:
        ctx.fail("开头还没有说明这是项目最外层的 .editorconfig", where=label + "/.editorconfig",
                 saw="第一块 [ ] 之前没有 root")

    if problems:
        # Lines the reader cannot use would make every later finding noise.
        return True
    for glob, _pairs, number in sections:
        if re.search(r"\{[^}]*(, | ,)", glob):
            ctx.note("第 {} 行的花括号里，逗号旁边有空格：EditorConfig 会把空格也当成文件名的一部分。".format(
                number))
        bare = glob.strip().lower()
        ext = bare[1:] if bare.startswith(".") else bare
        if ext in BARE_EXTENSIONS:
            ctx.note("第 {0} 行写的是 [{1}]：它只管名字就叫 {1} 的文件，要管所有 .{2} 文件，写 [*.{2}]。".format(
                number, glob.strip(), ext))
    if not sections:
        ctx.fail("还没有任何一块 [文件范围]", where=label + "/.editorconfig",
                 saw="没有以 [ 开头的行")
        return True

    for paths, key, value, wording in requirements:
        lacking = []
        wrong = None
        for rel in paths:
            props = _effective(sections, rel)
            got = props.get(key)
            if got is None:
                lacking.append(rel)
            elif got[0].lower() != value:
                lacking.append(rel)
                if wrong is None:
                    wrong = (got[0], got[1])
        if not lacking:
            ctx.ok(wording)
            continue
        if wrong is not None:
            allowed = KNOWN_VALUES.get(key)
            if allowed is not None and wrong[0].lower() not in allowed:
                saw = "{} = {}，规范里没有这个写法，编辑器会忽略它".format(key, wrong[0])
            else:
                saw = "{} = {}".format(key, wrong[0])
            ctx.fail("还没做到：" + wording,
                     where=label + "/.editorconfig 第 {} 行".format(wrong[1]), saw=saw)
        else:
            ctx.fail("还没做到：" + wording, where=label + "/.editorconfig",
                     saw="对 {} 生效的设置里没有 {}".format("、".join(lacking), key))
    return True


SITE_REQUIREMENTS = [
    (["index.html", "style.css", "README.md"], "charset", "utf-8", "所有文件都用 UTF-8"),
    (["index.html", "style.css", "README.md"], "end_of_line", "lf", "所有文件的换行都用 LF"),
    (["index.html", "style.css", "README.md"], "insert_final_newline", "true",
     "所有文件的最后都留一个换行"),
    (["index.html", "style.css"], "indent_style", "space", "html 和 css 文件用空格缩进"),
    (["index.html", "style.css"], "indent_size", "2", "html 和 css 文件每层缩进 2 格"),
]


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """State S1: a copy of the learner's site just before this lesson."""
    sc.site_before()
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))


# Station b: a folder of study notes, one month per sub-folder.  Two files
# mention 汇率 (the follow-along search); three files with seeded names are
# added, and exactly one of them holds the line 暗号：… (the own exercise).
STUDY = "study"
STUDY_MONTHS = ["2026-09", "2026-10", "2026-11"]
STUDY_FILES = {
    "README.md": "# 学习笔记\n\n每个月一个文件夹。\n",
    "2026-09/terminal.md": "# 终端\n\n学了 pwd、ls、cd。\n顺手查了一次美元兑人民币的汇率。\n",
    "2026-09/files.md": "# 文件\n\n学了 cp、mv、rm。删除前先看清要删什么。\n",
    "2026-10/plan.md": "# 这个月的计划\n\n1. 学会用编辑器打开整个文件夹\n2. 给网站写一份 README\n",
    "2026-10/search.md": "# 查找\n\n用 grep 找文件里的字，用 find 找文件。\n",
    "2026-11/website.md": "# 网站\n\n想在网页上放一个汇率换算的小工具。\n",
}
STUDY_SECRET = "# 随手记\n\n暗号：先保存，再刷新。\n"
STUDY_DECOY = "# 随手记\n\n今天的练习做完了。\n"


def build_1_4b(sc):
    """Study notes in three month folders; one seeded file holds the line 暗号：…"""
    for rel, text in STUDY_FILES.items():
        sc.write_bytes(STUDY + "/" + rel, text.encode("utf-8"))
    words = sc.words(3)
    months = sc.sample(STUDY_MONTHS, 3)
    secret = sc.randint(0, 2)
    names = []
    for index, (word, month) in enumerate(zip(words, months)):
        name = word + ".md"
        names.append(name)
        text = STUDY_SECRET if index == secret else STUDY_DECOY
        sc.write_bytes(STUDY + "/" + month + "/" + name, text.encode("utf-8"))
    sc.fact("folder", STUDY)
    sc.fact("secret_file", names[secret])
    sc.fact("secret_dir", months[secret])
    sc.fact("other_files", [n for i, n in enumerate(names) if i != secret])
    sc.todo("学习笔记在这里：" + sc.show(STUDY))
    sc.todo("用编辑器打开它：cd " + sc.show(STUDY) + "，然后 code .")


NOTES_MD = "# 今天的笔记\n\n今天查了美元兑人民币的汇率。\n"
NOTES_GBK = "旧电脑上记的：汇率表放在桌面上。\n"


def build_1_4c(sc):
    """Two small notes: one saved as UTF-8 with LF, one saved as GBK with CRLF by an old Windows PC."""
    sc.write_bytes("notes/today.md", NOTES_MD.encode("utf-8"))
    sc.write_bytes("notes/old-pc.txt", NOTES_GBK.replace("\n", "\r\n").encode("gbk"))
    sc.fact("folder", "notes")
    sc.fact("word", "汇率")
    sc.todo("两份笔记在这里：" + sc.show("notes"))
    sc.todo("用编辑器打开它：cd " + sc.show("notes") + "，然后 code .")


SCENARIOS = {
    "start": build_start,
    "1.4b": build_1_4b,
    "1.4-notes": build_1_4c,
}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _starter_note(ctx):
    """Read-only: mention an edited starter page (practice copies come from the manifest)."""
    original = ctx.read("starter/my-site/index.html")
    if original and (STARTER_HEADING not in original or STARTER_PARAGRAPH not in original):
        ctx.note("学习工作区里的 starter/my-site/index.html 被改过了。它是课程的原件；"
                 "练习场和考试用的是工具另存的原样，不受影响。你这份最好也恢复原样："
                 "对导师说“急救：starter 被改动了”。")


def check_a(ctx):
    """Artifact check on the learner's own ~/Developer/my-site/index.html."""
    _starter_note(ctx)
    site = ctx.need_dir("~/Developer/my-site", "你的网站文件夹 ~/Developer/my-site")
    page = ctx.need_file(site / "index.html", "~/Developer/my-site/index.html")
    label = ctx.show(page)
    text_before = ctx.read(page)
    _page_findings(ctx, page, label)
    if ctx.failed:
        ctx.note(SAVE_NOTE)
    if ctx.failed and STARTER_HEADING in text_before and STARTER_PARAGRAPH in text_before:
        info = ctx.scenario("start", required=False)
        if info.exists and info.facts.get("site"):
            copy = ctx.read(info.path / info.facts["site"] / "index.html")
            if copy and STARTER_HEADING not in copy:
                ctx.note("练习场里的副本改过了。这一站要改的是 ~/Developer/my-site 里的 index.html。")


def _tokens(typed):
    """Lower-case name-like pieces of an answer: 「2026-10/Heron.md」 -> 2026-10, heron.md, heron."""
    pieces = set()
    for token in re.findall(r"[a-z0-9_.\-]+", typed.lower()):
        token = token.strip(".")
        if token:
            pieces.add(token)
            if token.endswith(".md"):
                pieces.add(token[:-3])
    return pieces


def check_b(ctx):
    """Ask check: which file of the 1.4b study notes holds the line 暗号：…"""
    info = ctx.scenario("1.4b")
    secret = info.facts["secret_file"]
    stem = secret[:-3]
    known = {n[:-3] for n in info.facts.get("other_files", [])}
    known.update(rel.rsplit("/", 1)[-1][:-3].lower() for rel in STUDY_FILES)

    def right(typed):
        pieces = _tokens(typed)
        return stem in pieces and not (pieces & known)

    if not ctx.ask("学习笔记里有一行以“暗号：”开头。它写在哪个文件里？写出文件名。", expected=right):
        typed = ctx.last_answer or ""
        pieces = _tokens(typed)
        if "暗号" in typed or "保存" in typed:
            ctx.note("题目问的是那一行在哪个文件里，要写文件名，不是那一行写了什么。")
        elif pieces & set(STUDY_MONTHS) and not (pieces & (known | {stem})):
            ctx.note("你写的像是月份文件夹的名字；题目问的是文件名（以 .md 结尾的那个）。")
        elif stem in pieces:
            ctx.note("回答里不止一个文件名；只写那一个文件的名字。")


def check_c(ctx):
    """Artifact check on ~/Developer/my-site/.editorconfig."""
    site = ctx.need_dir("~/Developer/my-site", "你的网站文件夹 ~/Developer/my-site")
    if ".editorconfig" not in ctx.listdir(site):
        for other in ("~/Developer/.editorconfig", "~/.editorconfig"):
            if ctx.is_file(other):
                ctx.fail(".editorconfig 建错了地方", where=ctx.show(site),
                         saw="它在 {}，不在网站文件夹里".format(other))
                ctx.stop()
    readable = _editorconfig_findings(ctx, site, ctx.show(site), SITE_REQUIREMENTS)
    if ctx.failed and readable:
        ctx.note(SAVE_NOTE)
    if not ctx.failed:
        extensions = [n.lower() for n in ctx.listdir("~/.vscode/extensions")]
        if not any(n.startswith("editorconfig.editorconfig-") for n in extensions):
            ctx.note("VS Code 里还没装 EditorConfig 扩展：这个文件现在只对认识它的工具起作用。")


checks = {
    "1.4a": check_a,
    "1.4b": check_b,
    "1.4c": check_c,
}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.4a": [
        ("检查只看一个文件：~/Developer/my-site/index.html。"
         "先读检查结果里的“还缺什么”：缺的是大标题、那段话、保存，还是标签被改坏了？"),
        ("先确认你改的是对的文件夹：在终端里 cd ~/Developer/my-site，再运行 code .，"
         "左边资源管理器的最上面应该写着 MY-SITE。改完看标签页：文件名旁边有圆点，就按 ⌘S。"),
        ("跟我做里你改的是练习场副本的 <title>：只改 <title> 和 </title> 中间的字，两边的标签不动。"
         "这次是同样的动作，换成 <h1>…</h1> 和 <p>…</p> 中间的字。"),
        ("答案：在 ~/Developer/my-site 里运行 code .，在资源管理器里单击 index.html。"
         "把 <h1>你好，我是____</h1> 改成 <h1>你好，我是阿青</h1>（“阿青”换成你的笔名，下划线一起删掉）；"
         "把 <p> 和 </p> 中间那句原话换成你自己的一句话，例如 <p>我在从零学做网站，这一页会越来越丰富。</p>；"
         "按 ⌘S，标签页上的圆点消失；在终端里 open index.html，看浏览器里的大标题和那段话。\n"
         "解释：尖括号里的是标签（tag），告诉浏览器“这是大标题”“这是一段话”；你只换标签中间的文字。"
         "编辑器里改了不等于文件改了，保存以后检查和浏览器才看得到。"),
    ],
    "1.4b": [
        ("这一站的检查只问一件事：哪个文件里有一行以“暗号：”开头。"
         "想在一个文件夹的所有文件里找一串字，三种“按名字找”里该用哪一种？"),
        ("先用 VS Code 打开整个 study 文件夹（cd ~/Developer/playground/1.4b/study，再 code .），"
         "再想想第 2 站那张表里，哪一种是“在所有文件里找文字”。"),
        ("跟我做里你用 ⇧⌘F 搜过“汇率”：结果按文件分组，每组第一行是文件名，右边的灰字是它所在的文件夹。"
         "也可以在内置终端里用第 1.3 课的 grep -rn 汇率 .，每行第一个冒号前面就是文件的路径。"),
        ("答案：在 study 文件夹里按 ⇧⌘F 搜 暗号，或者在内置终端里运行 grep -rn 暗号 .。"
         "结果里只有一个文件；回答它的文件名。比如结果显示 2026-10/xxx.md，就回答 xxx.md"
         "（文件夹的名字可写可不写）。\n"
         "解释：跨文件搜索在打开的文件夹的所有文件里找字，不用一个个打开；"
         "它找的是你打开的那个文件夹，所以要先打开整个 study 文件夹（ED-01）。"),
    ],
    "1.4c": [
        ("检查只看 ~/Developer/my-site/.editorconfig 这一个文件：名字对不对，每一行是不是"
         "“[文件范围]”或“名字 = 值”，以及对 index.html、style.css 和这个文件夹里所有文件生效的是哪些设置。"),
        ("对照跟我做里给 notes 文件夹写的那份：开头 root = true，[*] 下面三行管所有文件。"
         "缩进照补全的样子写在最后：管 html 的一块，管 css 的一块。"),
        ("相似的例子：想让 .txt 文件用制表符（tab）缩进、每层 4 格，就在最后加一块 [*.txt]，"
         "下面写 indent_style = tab 和 indent_size = 4。要管两种文件，就各写一块。"),
        ("答案：在 my-site 里新建 .editorconfig，写入下面这些行并保存：\n"
         "root = true\n\n[*]\ncharset = utf-8\nend_of_line = lf\ninsert_final_newline = true\n\n"
         "[*.html]\nindent_style = space\nindent_size = 2\n\n"
         "[*.css]\nindent_style = space\nindent_size = 2\n"
         "解释：root = true 说明这是最外层，编辑器不用再往上找；[*] 那一块对所有文件生效："
         "UTF-8、LF、最后留一个换行；[*.html] 和 [*.css] 两块只对网页文件和样式文件生效："
         "用空格缩进，每层 2 格，和起步网页现在的写法一致。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {
        "id": "1.4-r1", "type": "recall", "tier": "fluent", "station": "1.4a", "rule": "ED-01",
        "q": "在终端里，怎样用 VS Code 打开你现在所在的整个文件夹？为什么要打开文件夹，而不是只打开一个文件？",
        "a": ("code .（点代表当前文件夹）。打开了文件夹，左边能看到项目里的所有文件，"
              "跨文件搜索、内置终端都以这个文件夹为准；只开一个文件，这些都用不上。"),
    },
    {
        "id": "1.4-p1", "type": "predict", "tier": "fluent", "station": "1.4a",
        "q": ("你在 VS Code 里改了 index.html 的大标题，标签页上的文件名旁边有一个实心圆点。"
              "这时在浏览器里刷新这个网页，会看到什么？"),
        "options": ["新的大标题", "还是旧的大标题", "浏览器报错，打不开网页"],
        "answer": "B",
        "explain": "圆点表示改动还没保存，文件里还是旧内容；浏览器读的是文件。按 ⌘S 保存后再刷新。",
    },
    {
        "id": "1.4-w1", "type": "which", "tier": "fluent", "station": "1.4b",
        "q": "在 VS Code 里，想按名字找到任意一个功能（比如“新建终端”），按哪组快捷键？",
        "options": ["⇧⌘P", "⌘P", "⇧⌘F", "⌃`"],
        "answer": "A", "shuffle": True,
        "explain": "⇧⌘P 是命令面板，按功能名字找；⌘P 按文件名找文件；⇧⌘F 在所有文件里找文字；⌃` 收起或打开终端面板。",
    },
    {
        "id": "1.4-f1", "type": "fault", "tier": "fluent", "station": "1.4c", "rule": "ED-02",
        "q": ("下面这份 .editorconfig 里有一处写法规范里没有，编辑器会悄悄忽略它。是哪一处？\n\n"
              "    root = true\n\n    [*]\n    charset = utf8\n    end_of_line = lf\n"
              "    insert_final_newline = true"),
        "options": ["charset 的值要写成 utf-8，中间有短横线", "root = true 要写在最后",
                    "end_of_line 的值要大写成 LF"],
        "answer": "A",
        "explain": "EditorConfig 规范 0.17.2 里 charset 可选的值是 latin1、utf-8、utf-8-bom、utf-16be、utf-16le；"
                   "值不分大小写，root 写在最前面。",
    },
    {
        "id": "1.4-r2", "type": "recall", "tier": "aware", "station": "1.4c", "rule": "ED-02",
        "q": "VS Code 自己会读 .editorconfig 吗？没有装任何扩展时，这个文件有什么用？",
        "a": ("不会。要装 EditorConfig 扩展（EditorConfig.EditorConfig）。没装时，"
              "它仍然写明了项目的约定，自带 EditorConfig 支持的编辑器和工具会照着做，同事也能读到。"),
    },
]


# ---------------------------------------------------------------------------
# EXAM (gate-a)
# ---------------------------------------------------------------------------
HEADINGS = ["欢迎来到我的小站", "这是我的学习记录", "一个慢慢长大的网页", "我在这里练手"]
SENTENCES = ["今天我学会了用编辑器改网页。", "这一页每周都会更新一点。",
             "我正在练习终端、编辑器和 Git。", "这里记下我学做软件的过程。"]
# Sentence-final marks a learner may add or drop; a difference in these alone gets its own remark.
END_MARKS = "。.！!？?"


def build_x1(sc):
    site = "site-" + sc.word()
    sc.copy_in("starter/my-site", site)
    sc.fact("site", site)
    sc.fact("heading", sc.pick(HEADINGS))
    sc.fact("sentence", sc.pick(SENTENCES))


def grade_x1(ctx):
    info = ctx.scenario()
    folder = ctx.need_dir(info.path / info.facts["site"], "考试网站文件夹")
    page = ctx.need_file(folder / "index.html", "考试网站的 index.html")
    label = "考试网站的 index.html"
    if info.form == "A":
        heading, _p = _page_findings(ctx, page, label, starter_heading=False,
                                     starter_paragraph=False)
        if heading is None:
            return
        got, want = _nospace(heading), _nospace(info.facts["heading"])
        saw = "现在是「{}」".format(_short(heading))
        if got != want and got.rstrip(END_MARKS) == want.rstrip(END_MARKS):
            saw += "，和题目要求只差句末的标点"
        done = ctx.expect(got == want,
                          "大标题已经换成题目要求的文字",
                          "大标题还不是题目要求的那句话", where=label + " 的 <h1>",
                          saw=saw)
        if done:
            ctx.expect(STARTER_PARAGRAPH in _strip_tags(ctx.read(page)), "其他内容保持原样",
                       "题目只让改大标题，但那一段话也变了", where=label + " 的 <p>",
                       saw="不再是原来那句话")
    else:
        _h, paragraphs = _page_findings(ctx, page, label, starter_heading=False,
                                        starter_paragraph=False)
        wanted = info.facts["sentence"]
        current = [p for p in paragraphs if p]
        if not current:
            # _page_findings has already reported the missing paragraph.
            return
        # Whitespace is ignored when comparing: 「和Git」 counts like 「和 Git」.
        want = _nospace(wanted)
        flat = [_nospace(p) for p in current]
        if not any(want in p for p in flat):
            saw = "现在那一段是「{}」".format(_short(current[0]))
            if flat[0].rstrip(END_MARKS) == want.rstrip(END_MARKS):
                saw += "，和题目要求只差句末的标点"
            ctx.fail("段落里还没有题目要求的那句话", where=label + " 的 <p>", saw=saw)
            return
        page_text = _nospace(_strip_tags(ctx.read(page)))
        # Either half of the starter paragraph left in a <p> means it was not replaced.
        left = [half + "。" for half in STARTER_PARAGRAPH.rstrip("。").split("。")
                if any(_nospace(half) in p for p in flat)]
        if left:
            ctx.fail("原来那句话还在：题目要的是换成，不是加在后面", where=label + " 的 <p>",
                     saw="段落里还能找到原来的「{}」".format(_short(left[0])))
            return
        ctx.ok("那一段话已经换成题目要求的句子")
        ctx.expect(_nospace(STARTER_HEADING) in page_text, "其他内容保持原样",
                   "题目只让改那一段话，但大标题也变了", where=label + " 的 <h1>",
                   saw="不再是原来的大标题")


def build_x2(sc):
    if sc.form == "A":
        folder = "site-" + sc.word()
        sc.copy_in("starter/my-site", folder)
    else:
        folder = "fx-" + sc.word()
        sc.copy_in("starter/hello-fx", folder)
        sc.write(folder + "/notes.md", "# 换算小程序的笔记\n")
    sc.fact("folder", folder)


X2_REQUIREMENTS = {
    "A": [
        (["index.html", "style.css", "README.md"], "charset", "utf-8", "所有文件都用 UTF-8"),
        (["index.html", "style.css", "README.md"], "end_of_line", "lf", "所有文件的换行都用 LF"),
        (["index.html", "style.css", "README.md"], "insert_final_newline", "true",
         "所有文件的最后都留一个换行"),
        (["index.html", "style.css"], "indent_style", "space", "html 和 css 文件用空格缩进"),
        (["index.html", "style.css"], "indent_size", "2", "html 和 css 文件每层缩进 2 格"),
    ],
    "B": [
        (["convert.py", "rates.txt", "notes.md"], "charset", "utf-8", "所有文件都用 UTF-8"),
        (["convert.py", "rates.txt", "notes.md"], "end_of_line", "lf", "所有文件的换行都用 LF"),
        (["convert.py", "rates.txt", "notes.md"], "insert_final_newline", "true",
         "所有文件的最后都留一个换行"),
        (["convert.py"], "indent_style", "space", "Python 文件用空格缩进"),
        (["convert.py"], "indent_size", "4", "Python 文件每层缩进 4 格"),
    ],
}


def grade_x2(ctx):
    info = ctx.scenario()
    folder = ctx.need_dir(info.path / info.facts["folder"], "考试文件夹")
    _editorconfig_findings(ctx, folder, "考试文件夹 " + info.facts["folder"],
                           X2_REQUIREMENTS[info.form])


EXAM = [
    {
        "id": "1.4-x1",
        "gate": "gate-a",
        "title": "用编辑器改网页里的文字",
        "minutes": 6,
        "build": build_x1,
        "task": {
            "A": ("{dir}/{site} 是一个小网页。先 cd 进 {dir}/{site}，用 VS Code 打开这个文件夹，"
                  "把网页的大标题（<h1> 里的字）改成「{heading}」，保存。其他内容不要动。"),
            "B": ("{dir}/{site} 是一个小网页。先 cd 进 {dir}/{site}，用编辑器打开整个文件夹，"
                  "把网页里那一段话（<p> 里的字）换成「{sentence}」，保存。网页的其他部分保持原样。"),
        },
        "grade": grade_x1,
    },
    {
        "id": "1.4-x2",
        "gate": "gate-a",
        "title": "给项目写一份 .editorconfig",
        "minutes": 8,
        "build": build_x2,
        "task": {
            "A": ("先 cd 进 {dir}/{folder}。给这个网站文件夹写一份 .editorconfig：它是最外层的一份；"
                  "所有文件用 UTF-8、换行用 LF、文件最后留一个换行；html 和 css 文件用空格缩进，每层 2 格。"),
            "B": ("{dir}/{folder} 是一个小程序的文件夹。先 cd 进 {dir}/{folder}，给它写一份 .editorconfig："
                  "它是最外层的一份；所有文件统一 UTF-8 和 LF，文件末尾留一个换行；"
                  "Python 文件（.py）用空格缩进，每层 4 格。"),
        },
        "grade": grade_x2,
    },
]
