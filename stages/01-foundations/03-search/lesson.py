"""Lesson 1.3: 终端：查找 (grep for content, find for file names).

Station a: grep with -n, -i and -r; "no output" means nothing matched.
Station b: find . -name with the pattern in quotes; revisit TERM-01 by
reading one command part by part.

Both station checks are ask checks: the answers exist only in the seeded
practice folders of the ``start`` scenario.  Standard library only; must
import on Python 3.9.  Reference: docs/authoring/tool-api.md.
"""

import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.3",
    "slug": "03-search",
    "title": "终端：查找",
    "stage": 1,
    "prerequisites": ["1.2"],
    "stations": [
        {
            "id": "1.3a",
            "title": "找内容",
            "minutes": 35,
            "new_concept": "grep 在文件内容里逐行找一串字，只把含有它的行打印出来",
            "new_commands": ["grep", "grep -n", "grep -i", "grep -r"],
        },
        {
            "id": "1.3b",
            "title": "找文件",
            "minutes": 35,
            "new_concept": "find 从一个起点往下按名字找文件，名字里带 * 时要加引号",
            "new_commands": ["find . -name"],
        },
    ],
    "rules": [],
    "verified": {
        "date": "2026-11-20",
        "tools": {"macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9", "grep": "2.6.0"},
    },
    "unverified_steps": [
        "1.3a 第 7 步：grep 后面没有文件名（忘了写，或者中间混进了全角空格）时，它会停下来等键盘输入，要按 Ctrl+C。"
        "等输入的行为已用管道实测（全角空格的情况也测了）；建课环境没有真正的终端，按 Ctrl+C 这一下没法实测。",
        "1.3b 第 4 步的提醒：引号没配对时提示符变成 dquote>（已用 zsh -i 实测），按 Ctrl+C 回到正常提示符；"
        "建课环境没有真正的终端，按 Ctrl+C 这一下没法实测。",
    ],
}

TERMS = [
    {"term": "匹配", "en": "match",
     "plain": "一行里含有你要找的那串字，就叫这一行匹配上了", "first": "1.3a"},
    {"term": "区分大小写", "en": "case-sensitive",
     "plain": "把大写字母和小写字母当成不同的字，EUR 和 eur 对不上", "first": "1.3a"},
    {"term": "注释", "en": "comment",
     "plain": "写给人看的说明文字，程序不照着它做事；本课的文件里它以 # 开头", "first": "1.3a"},
    {"term": "模式", "en": "pattern",
     "plain": "描述“名字长什么样”的写法，比如 *.css 表示所有以 .css 结尾的名字", "first": "1.3b"},
]


# ---------------------------------------------------------------------------
# Seeded material
# ---------------------------------------------------------------------------
# Customer code names in the order files.  None is a substring of another,
# and none occurs in starter/my-site, so a search from the scenario root finds
# exactly one line (the marker .playground is base64 since marker version 2).
CUSTOMERS = [
    "heron", "cedar", "maple", "otter", "willow", "falcon", "juniper", "badger",
    "lotus", "walnut", "pebble", "thistle", "marten", "sorrel", "quince", "osprey",
]
GOODS = [("苹果", "箱"), ("大米", "袋"), ("鸡蛋", "盒"), ("牛奶", "箱"), ("面粉", "袋"),
         ("茶叶", "罐"), ("酱油", "瓶"), ("香皂", "块"), ("毛巾", "条"), ("纸巾", "包")]

# The order files of station a.  The target line always lands in one of the
# nested files, so it can only be found by searching into sub-folders.
# Listed oldest first, so the order numbers grow with the months.
ORDER_FILES = ["old/2025/2025-12.txt", "old/2026-08.txt", "old/2026-09.txt",
               "2026-10.txt", "2026-11.txt"]
NESTED_ORDER_FILES = ORDER_FILES[:3]

# The backup tree of station b.  Innermost folder names are unique, so "which
# folder" has exactly one right answer.  Each exam form uses another tree, another
# kind of target file and another extension (tool-api 15.4 rule 1).
BACKUP_FOLDERS = ["2024", "2025", "2025/spring", "2025/autumn", "misc", "misc/old", "school"]
TARGET_FOLDERS = ["2025/spring", "2025/autumn", "misc/old", "school", "2024"]
EXAM_TREES = {
    "A": (["photos", "photos/2023", "photos/2024", "work", "work/reports", "work/old-2022", "music"],
          ["photos/2023", "photos/2024", "work/reports", "work/old-2022", "music"], "-plan.md"),
    "B": (["home", "home/bills", "home/recipes", "study", "study/lectures", "study/exams", "travel"],
          ["home/bills", "home/recipes", "study/lectures", "study/exams", "travel"], "-ideas.txt"),
}
EXAM_EXTS = {"A": ["xlsx", "png"], "B": ["docx", "mov"]}
PLAN_WORDS = ["garden", "kitchen", "piano", "camping", "moving", "wedding", "reading", "budget"]
DECOYS = ["photo-01.jpg", "photo-02.jpg", "notes.txt", "list.txt", "scan.pdf", "draft.md",
          "song.mp3", "todo.txt"]
CSV_NAMES = ["expenses.csv", "contacts.csv", "scores.csv", "books.csv", "trips.csv",
             "grades.csv", "bills.csv"]
EXT_STEMS = ["expenses", "contacts", "scores", "books", "trips", "grades", "menus"]


def _order_line(sc, number, customer):
    good, unit = sc.pick(GOODS)
    return "{}  {:<4}{:>3} {}   客户 {}".format(number, good, sc.randint(1, 9), unit, customer)


def _build_orders(sc, folder, files, nested, title):
    """Order files under ``folder``; one line (and only one) names the target.

    Records only the fact ``word`` (lower case, as the learner is told it).
    Where the line is, is not recorded: the checks find the line in the files
    themselves (see ``_hits``), so an answer matches what the learner's own
    ``grep`` shows even if a file was edited.
    """
    target_file = sc.pick(nested)
    names = sc.sample(CUSTOMERS, 7)
    word, others = names[0], names[1:]
    target_line = sc.randint(3, 7)
    number = 1000 + sc.randint(1, 80)
    for rel in files:
        month = rel.rsplit("/", 1)[-1][:-4]
        lines = ["# {} {}（练习用的假数据）".format(month, title),
                 "# 编号  商品  数量    客户代号"]
        count = 8 if rel == target_file else sc.randint(5, 8)
        for line_no in range(3, count + 1):
            number += 1
            hit = rel == target_file and line_no == target_line
            lines.append(_order_line(sc, number, word.capitalize() if hit else sc.pick(others)))
        sc.write(folder + "/" + rel, "\n".join(lines) + "\n", exact=True)
    sc.fact("word", word)


def _build_backup(sc, folder, tree, targets, suffix, ext_names, ext):
    """A backup tree with one ``<word><suffix>`` file and a few files ending in ``ext``.

    Records ``plan_file`` (the name the learner is told) and ``ext``.  The
    folder of the file and the count are not recorded (see ``_build_orders``):
    the checks look them up in the tree.
    """
    for rel in tree:
        sc.mkdir(folder + "/" + rel)
    sc.write(folder + "/README.txt", "这是一份旧电脑上的备份，文件是练习用的假数据。")
    for rel in tree:
        for name in sc.sample(DECOYS, 2):
            sc.write("{}/{}/{}".format(folder, rel, name), "练习用的假文件：" + name)
    target_rel = sc.pick(targets)
    plan = sc.pick(PLAN_WORDS) + suffix
    sc.write("{}/{}/{}".format(folder, target_rel, plan), """
        # 计划

        练习用的假文件。
    """)
    count = sc.randint(2, 5)
    places = [sc.pick(tree) for _ in range(count)]
    for name, rel in zip(sc.sample(ext_names, count), places):
        sc.write("{}/{}/{}".format(folder, rel, name), "日期,内容\n2025-01-01,练习用的假数据\n",
                 exact=True)
    sc.fact("plan_file", plan)
    sc.fact("ext", ext)


def build_start(sc):
    """The state just before 1.3: the site copy (S1) plus two practice folders."""
    sc.site_before()
    _build_orders(sc, "orders", ORDER_FILES, NESTED_ORDER_FILES, "的订单")
    _build_backup(sc, "backup", BACKUP_FOLDERS, TARGET_FOLDERS, "-plan.md", CSV_NAMES, "csv")
    sc.todo("第 1 站要用：订单文件夹 " + sc.show("orders"))
    sc.todo("  要找的客户代号：{}（文件里的大小写可能和这里不一样）".format(sc.facts["word"]))
    sc.todo("第 2 站要用：备份文件夹 " + sc.show("backup"))
    sc.todo("  要找的文件：" + sc.facts["plan_file"])


SCENARIOS = {"start": build_start}


# ---------------------------------------------------------------------------
# Answer matching
# ---------------------------------------------------------------------------
_TOKEN = re.compile(r"[a-z0-9_./~-]+")
# A pasted grep -n line: "orders/old/2025/2025-12.txt:3:1059 大米 ...".
_GREP_LINE = re.compile(r"^[^\s:]+:(\d+):")


def _paths(typed):
    """Path-like tokens of a normalised answer, each as a list of components.

    "orders/old/2026-09.txt:4:1042 苹果" gives [["orders", "old", "2026-09.txt"], ["4"], ["1042"]].
    """
    found = []
    for token in _TOKEN.findall(typed.replace("\\", "/")):
        parts = [p for p in token.split("/") if p not in ("", ".", "..", "~")]
        if parts:
            found.append(parts)
    return found


def _names_in(rels):
    """Every file and folder name on the given paths, files also without .txt."""
    names = set()
    for rel in rels:
        for part in rel.lower().split("/"):
            names.add(part)
            if part.endswith(".txt"):
                names.add(part[:-4])
    return names


def _without_names(text, names):
    """Drop path-like tokens that name a file or folder, so their digits are not read as numbers.

    "2026-08.txt 第 3 行" and "old/2026-08.txt:3" both leave the 3.  A short
    run of digits is never dropped: a line number is never a file name here.
    """
    def drop(found):
        token = found.group(0)
        parts = [p for p in token.split("/") if p not in ("", ".", "..", "~")]
        if token.isdigit() and len(token) <= 2:
            return token
        if "/" in token.strip("./") or (parts and parts[-1] in names):
            return " "
        return token
    return _TOKEN.sub(drop, text)


def _read_number(ctx, typed, grep_line=False, names=()):
    """The one number in an answer, or None.

    With ``grep_line`` a whole pasted grep -n line counts as its line number.
    ``names`` are file and folder names whose digits do not count.
    """
    text = ctx.normalize(typed)
    if grep_line:
        pasted = _GREP_LINE.match(text)
        if pasted:
            return int(pasted.group(1))
    if names:
        text = _without_names(text, names)
    return ctx.parse_int(text)


def _number_matcher(ctx, wanted, grep_line=False, names=()):
    wanted = set(wanted)

    def match(typed):
        return _read_number(ctx, typed, grep_line, names) in wanted
    return match


def _file_names(rels):
    """The base names of the given files, lower case, each also without .txt."""
    names = set()
    for rel in rels:
        base = rel.rsplit("/", 1)[-1].lower()
        names.add(base)
        if base.endswith(".txt"):
            names.add(base[:-4])
    return names


def _named_files(typed, every):
    """The file names of ``every`` that an answer names, alone or at the end of a path."""
    return {parts[-1] for parts in _paths(typed)} & every


def _file_matcher(rels, every_rels):
    """Right when the answer names one of the files and no other file of the folder.

    "2026-08.txt", "old/2026-08", "orders/old/2026-08.txt:7:1026 ..." pass;
    "2026-08.txt 或 2026-09.txt" does not (the same as for the folder question).
    """
    right = _file_names(rels)
    wrong = _file_names(every_rels) - right

    def match(typed):
        named = _named_files(typed, right | wrong)
        return bool(named & right) and not named & wrong
    return match


def _file_note(rels, every_rels, typed):
    """What may be wrong with a file answer, true for every wrong answer, never naming the right one."""
    right = _file_names(rels)
    top = _file_names(rel for rel in every_rels if "/" not in rel)
    named = _named_files(typed, _file_names(every_rels))
    if named & right and named - right:
        return ("你写了不止一个文件。只写一个：grep 输出里那一行第一个冒号前面的路径，"
                "最后一个 / 后面那一段就是文件名。")
    if named & top:
        return ("检查看的是 orders 里每一层子文件夹的文件。只搜最上面一层，"
                "或者没管大小写，都会漏掉那一行。")
    return ("把 grep 输出里那一行第一个冒号前面的路径照抄下来："
            "最后一个 / 后面那一段就是文件名。")


def _folder_names(typed, filename):
    """The folder each path-like token of an answer ends in.

    "./2025/spring/x-plan.md" gives ["spring"]; "autumn（在 2025 里面）" gives
    ["autumn", "2025"]; the file name alone gives nothing.
    """
    filename = filename.lower()
    names = []
    for parts in _paths(typed):
        if parts[-1] == filename:
            parts = parts[:-1]
        if parts:
            names.append(parts[-1])
    return names


def _folder_kinds(rels, filename, top):
    """Split the folder names of a tree: (right, around, elsewhere).

    right: the innermost folder of every file called filename; around: the
    folders it lies in, and the top folder itself; elsewhere: every other
    folder of the tree.
    """
    filename = filename.lower()
    right, around, every = set(), {top.lower()}, set()
    for rel in rels:
        parts = rel.lower().split("/")
        every.update(parts[:-1])
        if parts[-1] == filename and len(parts) > 1:
            right.add(parts[-2])
            around.update(parts[:-2])
    around -= right
    return right, around, every - right - around


def _folder_matcher(kinds, filename):
    """Right when the answer names the innermost folder and no folder elsewhere in the tree.

    "autumn", "2025/autumn/", "./2025/autumn/x-plan.md", "2025 下面的 autumn",
    "autumn（在 2025 里面）" pass; "2025" (a folder around it), "spring"
    and "spring 或 autumn" do not.
    """
    right, _around, elsewhere = kinds

    def match(typed):
        named = set(_folder_names(typed, filename))
        return bool(named & right) and not named & elsewhere
    return match


def _folder_note(kinds, filename, typed):
    """What was wrong with a folder answer, true for every wrong answer, never naming the right one."""
    right, around, elsewhere = kinds
    named = list(dict.fromkeys(_folder_names(typed, filename)))
    wrong = [n for n in named if n in elsewhere]
    if wrong:
        return ("你写的 {} 不是 {} 所在的那一层，也不是它外面的哪一层。"
                "只写 find 输出里文件名前面紧挨着的那一段。".format("、".join(wrong), filename))
    outer = [n for n in named if n in around]
    if outer:
        return ("你写的 {} 是 {} 外面的一层。要写的是最里面那一层："
                "find 输出里，文件名前面紧挨着的那一段。".format("、".join(outer), filename))
    return ("回答里没有这份备份里哪个文件夹的名字。检查看的是 {} 所在的那一层文件夹："
            "find 输出里，文件名前面紧挨着的那一段。".format(filename))


# ---------------------------------------------------------------------------
# Looking things up in the practice folders (read-only)
# ---------------------------------------------------------------------------
def _hits(ctx, folder, word):
    """(path inside folder, line number) of every line that contains word, any case."""
    word = word.lower()
    found = []
    for rel in ctx.walk(folder):
        for number, line in enumerate(ctx.lines(folder / rel), 1):
            if word in line.lower():
                found.append((rel, number))
    return found


def _folders_of(ctx, folder, filename):
    """Innermost folder names of every file called filename below folder."""
    return {rel.rsplit("/", 2)[-2] for rel in ctx.walk(folder)
            if "/" in rel and rel.rsplit("/", 1)[-1] == filename}


def _count_ext(ctx, folder, ext):
    return sum(1 for rel in ctx.walk(folder) if rel.rsplit("/", 1)[-1].endswith("." + ext))


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _rebuild_hint(info):
    return "python3 tools/course.py scenario {} --reset".format(
        info.key if info.key != "start" else info.lesson)


def _note_rebuild(ctx, info, folder):
    """Before need_dir stops the check: say how to get a lost practice folder back."""
    if not ctx.is_dir(info.path / folder):
        ctx.note("练习场景里的文件夹 {} 不见了。可以重搭一份：{}"
                 "（重搭后要找的词和文件名会换）".format(folder, _rebuild_hint(info)))


def _changed(ctx, info, missing, where):
    """The practice files no longer hold what the question is about: say so and stop."""
    ctx.fail(missing, where=where, saw="练习文件被改动过")
    ctx.note("可以重搭一份再做：{}（重搭后要找的词和文件名会换）".format(_rebuild_hint(info)))
    ctx.stop()


def _find_word(ctx):
    """Shared by check 1.3a and the do item 1.3-d1."""
    info = ctx.scenario("start")
    _note_rebuild(ctx, info, "orders")
    orders = ctx.need_dir(info.path / "orders", "订单文件夹 orders")
    word = info.facts["word"]
    hits = _hits(ctx, orders, word)
    if not hits:
        _changed(ctx, info, "orders 里已经没有写着 {} 的行".format(word), "订单文件夹 orders")
    hit_rels = [rel for rel, _ in hits]
    every = list(ctx.walk(orders))
    if not ctx.ask("orders 里写着客户代号 {} 的那一行，在哪个文件里？写出文件名".format(word),
                   _file_matcher(hit_rels, every)):
        ctx.note(_file_note(hit_rels, every, ctx.normalize(ctx.last_answer or "")))
    names = _names_in(ctx.walk(orders)) | {"orders"}
    if not ctx.ask("那一行是这个文件的第几行？",
                   _number_matcher(ctx, [n for _, n in hits], grep_line=True, names=names)):
        if _read_number(ctx, ctx.last_answer or "", grep_line=True, names=names) is None:
            ctx.note("这一题只填一个数：grep -n 输出里，第一个冒号和第二个冒号中间的那个数。")
        else:
            ctx.note("行号从文件的第一行算起，开头的注释行也算。让 grep 替你数，别自己数。")


def check_a(ctx):
    """Ask check: file and line of the one order line that names the customer."""
    _find_word(ctx)


def check_b(ctx):
    """Ask check: where the plan file is, how many .csv files; one TERM-01 quiz."""
    info = ctx.scenario("start")
    _note_rebuild(ctx, info, "backup")
    backup = ctx.need_dir(info.path / "backup", "备份文件夹 backup")
    plan, ext = info.facts["plan_file"], info.facts["ext"]
    folders = _folders_of(ctx, backup, plan)
    if not folders:
        _changed(ctx, info, "backup 里已经没有 {} 这个文件".format(plan), "备份文件夹 backup")
    kinds = _folder_kinds(ctx.walk(backup), plan, "backup")
    if not ctx.ask("{} 所在的那一层文件夹叫什么？只写这一层的名字"
                   "（find 输出里，文件名前面紧挨着的那一段）".format(plan),
                   _folder_matcher(kinds, plan)):
        ctx.note(_folder_note(kinds, plan, ctx.normalize(ctx.last_answer or "")))
    if not ctx.ask("backup 里（所有子文件夹都算）一共有几个 .{} 文件？".format(ext),
                   _number_matcher(ctx, [_count_ext(ctx, backup, ext)])):
        ctx.note("检查数的是 backup 里每一层子文件夹的 .{} 文件。只在一层里用 ls 看会漏掉。"
                 "模式没加引号时，终端可能说 no matches found，也可能不报错、只找到一部分："
                 "看看模式有没有加引号、引号是不是半角的 \"。".format(ext))
    ctx.quiz("有人发给你这条命令：find ~/Developer -name \"*.md\"\n"
             "  其中 ~/Developer 这一块是什么意思？",
             ["从哪个文件夹开始往下找", "要找的文件叫什么名字", "一个选项，决定怎么找"],
             "A",
             explain="find 后面第一块是起点；-name 是选项；引号里的 *.md 是名字的模式。",
             feedback={"B": "要找的名字写在 -name 后面，这一块在 -name 前面。",
                       "C": "选项以短横线开头，这一块没有短横线。"})


checks = {"1.3a": check_a, "1.3b": check_b}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.3a": [
        "这是“按内容找”还是“按名字找”？你知道那一行里写着什么，不知道它在哪个文件。"
        "再想想：那一行可能藏在子文件夹里，大小写也可能和你拿到的不一样。",
        "先进入练习场景：cd ~/Developer/playground/1.3-start，对着 orders 文件夹搜。"
        "要用到的三个选项都在第 1 站：第 2 步、第 4 步、第 6 步。"
        "忘了要找的代号，就回学习工作区再运行一次 python3 tools/course.py scenario 1.3。",
        "相似的例子：在学习工作区里，找 starter/my-site 文件夹里所有写着 TITLE 的行，"
        "不管大小写，带行号：grep -rin TITLE starter/my-site。"
        "输出 starter/my-site/index.html:6:  <title>我的第一个网页</title>，"
        "意思是 index.html 的第 6 行，文件里写的是小写的 title。",
        "答案：cd ~/Developer/playground/1.3-start，然后 grep -rin 代号 orders（把“代号”换成场景给你的那个词）。"
        "输出只有一行，第一个冒号前面是文件路径，第一个冒号和第二个冒号中间的那个数就是行号。"
        "解释：-r 钻进 old 这样的子文件夹，-i 让 Heron 和 heron 算同一个词，-n 打印行号。"
        "少了 -r 会报 orders 是个文件夹；少了 -i 会什么都不打印。",
    ],
    "1.3b": [
        "这是“按名字找”，还是“按内容找”？按名字找的那条命令，要你先说清从哪里开始找。",
        "起点是 backup 文件夹（cd ~/Developer/playground/1.3-start/backup 之后，起点就是 .）。"
        "名字里有 * 的时候，回看第 2 站第 4 步。",
        "相似的例子：在学习工作区的 starter 里（cd ~/Developer/fullstack-from-zero/starter），"
        "find . -name \"*.html\" 只打印一行 ./my-site/index.html："
        "说明 starter 里一共有 1 个 .html 文件，它所在的那一层文件夹叫 my-site。",
        "答案：cd ~/Developer/playground/1.3-start/backup，然后 find . -name \"场景给你的文件名\"，"
        "输出路径里文件名前面紧挨着的那一段就是文件夹；再运行 find . -name \"*.csv\"，数一数打印了几行。"
        "最后一题选 A：find 后面第一块是起点。"
        "解释：不加引号时，zsh 会先拿 *.csv 去当前文件夹里展开，这里一个也没有，就报 no matches found，"
        "find 根本没机会运行。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.3-r1", "type": "predict", "tier": "fluent", "station": "1.3a",
     "q": "文件 rates.txt 里只有大写的 EUR。运行 grep eur rates.txt，会看到什么？",
     "options": ["什么也不打印，提示符直接回来", "报错：No such file or directory",
                 "打印 EUR 那一行"],
     "answer": "A",
     "explain": "grep 默认区分大小写，eur 和 EUR 对不上。没有输出就是“没找到”，不是出错；要不管大小写，加 -i。"},
    {"id": "1.3-r2", "type": "which", "tier": "fluent", "station": "1.3a",
     "q": "想在 notes 文件夹和它的所有子文件夹里，找出写着 TODO 的行，并且显示行号。用哪条命令？",
     "options": ["grep -rn TODO notes", "grep -n TODO notes", "grep -n TODO"],
     "answer": "A", "shuffle": True,
     "explain": "-r 钻进子文件夹，-n 显示行号，最后的 notes 是在哪里找。"
                "少了 -r，grep 会报 notes: Is a directory；grep -n TODO 没写在哪里找，"
                "会停下来等你从键盘输入。"},
    {"id": "1.3-r3", "type": "fault", "tier": "fluent", "station": "1.3b",
     "q": "运行下面这条命令，终端回了一句 zsh: no matches found: *.txt。问题出在哪？\n\n"
          "    find . -name *.txt",
     "options": ["*.txt 没加引号，zsh 先拿它去当前文件夹里展开，没展开出东西就报错了",
                 "find 不认识 *，要把文件名写全",
                 "这个文件夹和它的子文件夹里都没有 .txt 文件"],
     "answer": "A",
     "explain": "报错的是 zsh，不是 find。写成 find . -name \"*.txt\"，* 才能原样交给 find，"
                "由 find 去每一层子文件夹里比对。"},
    {"id": "1.3-r4", "type": "recall", "tier": "fluent", "station": "1.3b",
     "q": "grep 和 find 都是“找”。它们各找什么？各举一个什么时候用的例子。",
     "a": "grep 找文件里面的内容：知道写着什么、不知道在哪个文件、哪一行时用，比如 grep -rn 人民币 .。"
          "find 按名字找文件：知道叫什么、不知道放在哪时用，比如 find . -name \"*.css\"。"},
    {"id": "1.3-r5", "type": "which", "tier": "lookup", "station": "1.3a",
     "q": "拆开这条命令：grep -rin \"usd\" starter。其中 -rin 是什么？",
     "options": ["-r、-i、-n 三个选项合在一起写", "一个名叫 rin 的选项", "要找的那个词"],
     "answer": "A",
     "explain": "几个单字母选项可以合写在一个短横线后面，-rin 等于 -r -i -n。要找的词是 \"usd\"，最后的 starter 是在哪里找。"},
    # Kept as lookup on purpose (tool-api 16.2: lookup items are never served,
    # the tutor and later stages read them; 16.6: many do items are better as
    # lookup).  Its check is the station check, whose rebuild advice names the
    # station's scenario, not a review copy, so it is not made fluent.
    {"id": "1.3-d1", "type": "do", "tier": "lookup", "station": "1.3a",
     "q": "练习场景的 orders 文件夹里，有一行写着一个客户代号（大小写可能不一样）。找出它在哪个文件的第几行。",
     "scenario": "start", "check": _find_word},
]


# ---------------------------------------------------------------------------
# EXAM (gate-a)
# ---------------------------------------------------------------------------
DIARY_FILES = ["week-2/extra/friday.txt", "week-2/thursday.txt", "week-2/wednesday.txt",
               "tuesday.txt", "monday.txt"]


def build_x1(sc):
    """A: an order tree, where is the one line naming the word.  B: a diary tree, how many lines name it."""
    folder = ("orders-" if sc.form == "A" else "diary-") + sc.word()
    if sc.form == "A":
        _build_orders(sc, folder, DIARY_FILES, DIARY_FILES[:3], "的订单")
    else:
        names = sc.sample(CUSTOMERS, 6)
        word, others = names[0], names[1:]
        sizes = [sc.randint(4, 6) for _ in DIARY_FILES]
        slots = [(f, n) for f, size in enumerate(sizes) for n in range(size)]
        hits = sc.randint(3, 5)
        chosen = set(sc.sample(slots, hits))
        shouted = min(chosen)          # at least one hit is upper case, so -i matters
        for f, rel in enumerate(DIARY_FILES):
            lines = ["# {}（练习用的假数据）".format(rel.rsplit("/", 1)[-1][:-4])]
            for n in range(sizes[f]):
                if (f, n) == shouted:
                    who = word.upper()
                elif (f, n) in chosen:
                    who = sc.pick([word, word.capitalize()])
                else:
                    who = sc.pick(others)
                lines.append("今天和 {} 一起买了{}。".format(who, sc.pick(GOODS)[0]))
            sc.write(folder + "/" + rel, "\n".join(lines) + "\n", exact=True)
        sc.fact("word", word)
    sc.fact("folder", folder)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    folder = ctx.need_dir(info.path / facts["folder"], "考试文件夹 " + facts["folder"])
    hits = _hits(ctx, folder, facts["word"])
    if not hits:
        raise RuntimeError("1.3-x1: no line names the word any more")
    if info.form == "A":
        ctx.ask("写着 {} 的那一行在哪个文件里？写出文件名".format(facts["word"]),
                _file_matcher([rel for rel, _ in hits], list(ctx.walk(folder))))
        names = _names_in(ctx.walk(folder)) | {facts["folder"].lower()}
        ctx.ask("它是那个文件的第几行？",
                _number_matcher(ctx, [n for _, n in hits], grep_line=True, names=names))
    else:
        ctx.ask("写着 {} 的行一共有几行？（不分大小写，所有子文件夹都算）".format(facts["word"]),
                _number_matcher(ctx, [len(hits)]))


def build_x2(sc):
    """A backup tree: which folder holds the named file, and how many files end in the extension.

    Both forms ask the same two things; the tree, the kind of target file and
    the extension differ between the forms.
    """
    folder = "backup-" + sc.word()
    tree, targets, suffix = EXAM_TREES[sc.form or "A"]
    ext = sc.pick(EXAM_EXTS[sc.form or "A"])
    _build_backup(sc, folder, tree, targets, suffix,
                  ["{}.{}".format(stem, ext) for stem in EXT_STEMS], ext)
    sc.fact("folder", folder)


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    folder = ctx.need_dir(info.path / facts["folder"], "考试文件夹 " + facts["folder"])
    folders = _folders_of(ctx, folder, facts["plan_file"])
    if not folders:
        raise RuntimeError("1.3-x2: the named file is gone")
    kinds = _folder_kinds(ctx.walk(folder), facts["plan_file"], facts["folder"])
    ctx.ask("{} 所在的那一层文件夹叫什么？只写这一层的名字，不写它上面几层".format(facts["plan_file"]),
            _folder_matcher(kinds, facts["plan_file"]))
    ctx.ask("一共有几个名字以 .{} 结尾的文件？".format(facts["ext"]),
            _number_matcher(ctx, [_count_ext(ctx, folder, facts["ext"])]))


EXAM = [
    {
        "id": "1.3-x1",
        "gate": "gate-a",
        "title": "按内容找到一行字",
        "minutes": 5,
        "build": build_x1,
        "task": {
            "A": "先 cd 进 {dir}/{folder}。这个文件夹里有好几层子文件夹，其中只有一行写着 {word}"
                 "（大小写可能不同）。找出它在哪个文件、第几行。做完回到学习工作区批改，批改时会问你，照你找到的回答。",
            "B": "先 cd 进 {dir}/{folder}。在这个文件夹和它的所有子文件夹里，数一数写着 {word} 的行"
                 "一共有几行（大写、小写、大小写混着写都算）。做完回到学习工作区批改，批改时会问你，照你找到的回答。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.3-x2",
        "gate": "gate-a",
        "title": "按名字找到文件",
        "minutes": 6,
        "build": build_x2,
        "task": {
            "A": "先 cd 进 {dir}/{folder}。它是一份旧电脑的备份，文件散在好几层子文件夹里。"
                 "找出叫 {plan_file} 的文件所在的那一层文件夹叫什么，"
                 "再数一数（所有子文件夹都算）有几个名字以 .{ext} 结尾的文件。做完回到学习工作区批改，批改时会问你，照你找到的回答。",
            "B": "先 cd 进 {dir}/{folder}。里面是从旧电脑上拷下来的一堆文件，分在好几层子文件夹里。"
                 "先找出叫 {plan_file} 的文件所在的那一层文件夹叫什么，再数一数这些子文件夹里"
                 "一共有几个名字以 .{ext} 结尾的文件。做完回到学习工作区批改，批改时会问你，照你找到的回答。",
        },
        "grade": grade_x2,
    },
]
