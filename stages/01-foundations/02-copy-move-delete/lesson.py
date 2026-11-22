"""Lesson 1.2: 终端：复制、移动、删除 (plan section 4, task T2).

Station a: cp, cp -R, mv; the learner creates ~/Developer/my-site (state S1).
Station b: rm, rm -r, rmdir (rm -i only in 想多了解); wildcards and quotes; rule TERM-02.

Standard library only, Python 3.9 syntax.  The reference is
docs/authoring/tool-api.md.
"""

META = {
    "id": "1.2",
    "slug": "02-copy-move-delete",
    "title": "终端：复制、移动、删除",
    "stage": 1,
    "prerequisites": ["1.1"],
    "stations": [
        {
            "id": "1.2a",
            "title": "复制和移动",
            "minutes": 30,
            "new_concept": "复制留下原件，移动（包括改名）不留原件；目标是已有的文件夹时，东西会被放进它里面",
            "new_commands": ["cp", "cp -R", "mv"],
        },
        {
            "id": "1.2b",
            "title": "删除和安全",
            "minutes": 40,
            "new_concept": "rm 的删除立刻生效、不经过废纸篓，所以删之前先看清要删什么（连隐藏文件一起看）",
            "new_commands": ["rm", "rm -r", "rmdir"],
        },
    ],
    "rules": ["TERM-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9"},
    },
    "unverified_steps": [
        "在 Finder 里删除文件会进废纸篓、可以从废纸篓放回原处（对照 Apple 支持文档，建课环境没有图形界面）",
    ],
}

TERMS = [
    {"term": "复制", "en": "copy", "plain": "做一份一模一样的，原件还在原处", "first": "1.2a"},
    {"term": "移动", "en": "move", "plain": "把东西换个地方或换个名字，原处就没有了；改名也是移动", "first": "1.2a"},
    {"term": "递归", "en": "recursive", "plain": "连同里面的文件夹、文件夹里的文件，一层一层全算上", "first": "1.2a"},
    {"term": "废纸篓", "en": "Trash", "plain": "在 Finder 里删掉的东西先去的地方，还能放回原处", "first": "1.2b"},
    {"term": "通配符", "en": "wildcard", "plain": "在名字里代替“任意几个字符”的符号，最常用的是 *", "first": "1.2b"},
    {"term": "引号", "en": "quotes", "plain": "把带空格的名字括起来，让终端把它当成一个整体", "first": "1.2b"},
]


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """The practice folder for the worked steps of both stations.

    The names are fixed because the lesson text uses them word for word.
    The learner's own site does not exist yet (state S0): station a creates
    it in the real ~/Developer, which no builder may touch.
    """
    sc.write("notes.txt", """
        周一：买菜
        周二：学终端
        周三：给网站起个名字
    """)
    sc.write("recipes/noodles.txt", """
        西红柿鸡蛋面
        先炒鸡蛋，再下面条。
    """)
    sc.write("recipes/dumplings.txt", """
        白菜猪肉饺子
        馅里少放盐。
    """)
    sc.todo("练习用的文件在这里：" + sc.show())


JUNK_WORDS = ["cache", "temp", "partial", "session", "upload", "preview", "thumb", "draft"]


def build_downloads(sc):
    """Station b: a downloads folder with junk to delete and keepers to keep.

    Shared by the station scenario and the ``do`` review item.  Everything a
    check needs is recorded as a fact; the names change with the seed.
    """
    base = "downloads"
    tmp_files = sorted(w + ".tmp" for w in sc.sample(JUNK_WORDS, sc.randint(3, 5)))
    for name in tmp_files:
        sc.write(base + "/" + name, "临时文件，可以删。")
    spaced = "report copy.txt"
    sc.write(base + "/" + spaced, "报告的一份多余副本。")
    empty_dir = "old-" + sc.word()
    sc.mkdir(base + "/" + empty_dir)
    full_dir = "installer-" + sc.word()
    sc.write(base + "/" + full_dir + "/setup.pkg", "安装包（替身）")
    sc.write(base + "/" + full_dir + "/readme.txt", "安装说明")

    sc.write(base + "/report.txt", "这是要交的报告，不能删。")
    sc.write(base + "/todo.txt", "待办：整理下载文件夹。")
    sc.write(base + "/tmp-plan.txt", "名字里有 tmp，但它不是 .tmp 结尾，要留着。")
    sc.write(base + "/photos/trip-1.jpg", "（照片的替身）")
    sc.write(base + "/photos/trip-2.jpg", "（照片的替身）")

    sc.fact("folder", base)
    sc.fact("tmp_files", tmp_files)
    sc.fact("tmp_count", len(tmp_files))
    sc.fact("spaced", spaced)
    sc.fact("empty_dir", empty_dir)
    sc.fact("full_dir", full_dir)
    sc.fact("keep_files", ["report.txt", "todo.txt", "tmp-plan.txt",
                           "photos/trip-1.jpg", "photos/trip-2.jpg"])
    where = sc.show(base)
    sc.todo("要清理的文件夹：" + where)
    sc.todo("先进去：cd " + where)
    sc.todo("要删的：所有以 .tmp 结尾的文件；report copy.txt；空文件夹 "
            + empty_dir + "；文件夹 " + full_dir + "（连同里面的东西）")
    sc.todo("其他的都要留下。删之前先数一数有几个 .tmp 文件，检查时会问你。")


SCENARIOS = {
    "start": build_start,
    "1.2b": build_downloads,
}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
SITE_FILES = ("index.html", "style.css")


def check_a(ctx):
    """The learner's own site folder exists as a copy of the starter (state S1)."""
    starter = ctx.workspace / "starter" / "my-site"
    starter_missing = [name for name in SITE_FILES if not ctx.is_file(starter / name)]
    if starter_missing:
        ctx.fail("起步网页要复制出去，原件得留在学习工作区里",
                 where="学习工作区里的 starter/my-site",
                 saw="找不到 " + "、".join(starter_missing))
    else:
        ctx.ok("学习工作区里的 starter/my-site 原样还在")

    site = ctx.my_site
    developer = ctx.home / "Developer"
    if not ctx.is_dir(site):
        stray = [name for name in SITE_FILES if ctx.is_file(developer / name)]
        if stray:
            ctx.fail("index.html 和 style.css 要装在 my-site 文件夹里",
                     where="~/Developer",
                     saw="它们直接落在了 ~/Developer 里，没有 my-site 这一层")
        for other in (ctx.home / "my-site", ctx.workspace / "my-site"):
            if ctx.is_dir(other):
                ctx.note("在 " + ctx.show(other.parent) + " 里找到了一个 my-site 文件夹，位置不对：要的是 ~/Developer/my-site。")
        ctx.expect_dir(site, "你的网站文件夹 ~/Developer/my-site")
        ctx.stop()

    # The Mac's disk ignores case, so is_dir also finds My-Site: compare the real name.
    spelled = [name for name in ctx.listdir(developer) if name.lower() == "my-site"]
    if spelled and "my-site" not in spelled:
        ctx.fail("文件夹名要一字不差地是 my-site：全是小写字母，中间是短横线（WS-02）",
                 where="~/Developer", saw="文件夹名是 " + spelled[0])
    else:
        ctx.ok("~/Developer/my-site 文件夹已经有了")
    stray =[name for name in SITE_FILES if ctx.is_file(developer / name)]
    if stray:
        ctx.note("~/Developer 里还散落着 " + "、".join(stray)
                 + "，可能是之前多复制出来的。不要的话，用 mv 把它们一个一个挪进 ~/Developer/playground。")
    files = ctx.walk(site)
    nested = [path for path in files if path.split("/")[-1] in SITE_FILES and "/" in path]
    if nested:
        ctx.fail("my-site 里面要直接是网页文件，不能再套一层文件夹",
                 where=ctx.show(site),
                 saw="在更深一层找到了 " + nested[0])
    for name in SITE_FILES:
        if name in files:
            ctx.ok("my-site 里有 " + name)
        elif not nested:
            ctx.fail("my-site 里还缺 " + name, where=ctx.show(site), saw="没有这个文件")
    extra = [path for path in files if path not in SITE_FILES and path not in nested]
    if extra:
        ctx.fail("my-site 里只该有网站的两个文件",
                 where=ctx.show(site), saw="还多了 " + "、".join(extra[:3]))
    if ctx.failed:
        return
    if not starter_missing:
        same = all(ctx.read_bytes(site / name) == ctx.read_bytes(starter / name)
                   for name in SITE_FILES)
        if same:
            ctx.ok("两个文件和起步网页里的一模一样")
        else:
            ctx.note("my-site 里的文件和 starter 里的不完全一样。如果是你有意改的，没关系。")


def _names(names, limit=4):
    """"a、b、c" or "a、b、c、d 等 6 个" for a fail message."""
    text = "、".join(names[:limit])
    if len(names) > limit:
        text += " 等 " + str(len(names)) + " 个"
    return text


def _in_review(ctx, path):
    """True when the folder is a review copy under playground/review.

    ctx.station is the item's station ("1.2b") in a review too, so the folder
    is what tells a review copy from the station's own scenario.
    """
    try:
        path.resolve().relative_to((ctx.playground / "review").resolve())
    except ValueError:
        return False
    return True


def _downloads_cleaned(ctx):
    """Station b and the ``do`` review item: junk gone, keepers kept."""
    info = ctx.scenario("1.2b")
    facts = info.facts
    base = info.path / facts["folder"]
    if _in_review(ctx, info.path):
        again = "python3 tools/course.py review --give-up，下次会换一份"
    else:
        again = "先 cd ~/Developer/fullstack-from-zero，再运行 python3 tools/course.py scenario 1.2b --reset"
    rebuild = "删掉的找不回来。重搭一份再练：" + again
    if not ctx.is_dir(base):
        ctx.fail("downloads 文件夹本身要留着，只清理里面的东西",
                 where=ctx.show(info.path), saw="downloads 整个不见了")
        ctx.note(rebuild)
        ctx.stop()

    junk = list(facts["tmp_files"]) + [facts["spaced"], facts["empty_dir"], facts["full_dir"]]
    left = [name for name in junk if ctx.exists(base / name)]
    lost = [name for name in facts["keep_files"] if not ctx.is_file(base / name)]
    if lost:
        ctx.fail("不该删的也被删了", where=ctx.show(base), saw="不见了：" + _names(lost))
        ctx.note(rebuild)
    elif len(left) < len(junk):
        # Only praise what the learner did: an untouched folder keeps everything too.
        ctx.ok("该留下的文件一个不少")

    if left:
        ctx.fail("还有该删的没删", where=ctx.show(base), saw="还在：" + _names(left))
    else:
        ctx.ok("该删的都删掉了")
    if ctx.failed:
        ctx.stop()
    if not ctx.ask("删之前你用 ls 看到的：以 .tmp 结尾的文件一共有几个？", expected=facts["tmp_count"]):
        ctx.note("文件已经删了，只能往上翻终端，找删之前那次 ls 的结果。找不到就重搭一份（"
                 + again + "），重搭以后个数可能会变，删之前先数清楚。")


def check_b(ctx):
    _downloads_cleaned(ctx)


checks = {
    "1.2a": check_a,
    "1.2b": check_b,
}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.2a": [
        "这一站要的是复制，不是移动：原件留在学习工作区，~/Developer 里多出一份。复制的是整个文件夹，想想要加哪个选项。",
        ("先回到学习工作区：cd ~/Developer/fullstack-from-zero，用 ls starter 确认 my-site 在那里。"
         "命令的格式是：命令、选项、从哪里、到哪里；“到哪里”写完整的 ~/Developer/my-site。"
         "检查结果里的“看到了什么”会告诉你现在差在哪。"),
        ("相似的例子：把练习场里的 recipes 文件夹复制成 recipes-copy，"
         "用的是 cp -R recipes recipes-copy。注意来源末尾不要加斜杠。"),
        ("答案：在学习工作区里运行 cp -R starter/my-site ~/Developer/my-site，"
         "再用 ls ~/Developer/my-site 确认里面直接是 index.html 和 style.css。\n"
         "解释：cp 复制，-R 表示连同文件夹里的东西一起复制；目标 ~/Developer/my-site 还不存在，"
         "所以复制出来的文件夹就叫这个名字。\n"
         "如果之前弄错了：多套了一层或多了别的东西，就把弄错的那份整个挪进练习场"
         "（mv ~/Developer/my-site ~/Developer/playground/my-site-wrong），再运行上面的命令；"
         "两个文件直接落在了 ~/Developer 里，就运行 mkdir ~/Developer/my-site，"
         "再运行 mv ~/Developer/index.html ~/Developer/my-site 和 mv ~/Developer/style.css ~/Developer/my-site 把它们装进去；"
         "原件被移走了，就在学习工作区里运行 cp -R ~/Developer/my-site starter/my-site 放回一份；"
         "文件夹名的大小写不对（比如 My-Site），就运行 mv ~/Developer/My-Site ~/Developer/my-site 改过来。"),
    ],
    "1.2b": [
        ("四类东西要删：.tmp 文件、带空格名字的文件、空文件夹、装着东西的文件夹。"
         "每一类的删法不一样：有的要加引号，有的要加选项，有的要换一条命令。先看清楚，再删。"),
        ("先 cd 进 downloads，用 ls 看全部，再用 ls *.tmp 看通配符会选中哪些，数一数。"
         "名字里有空格的，要用引号把整个名字括起来。"),
        ("相似的例子：课文里删 my list.txt 用的是 rm \"my list.txt\"；"
         "删空文件夹 empty-box，先 ls -a empty-box 看过只有 . 和 ..，再 rmdir empty-box；"
         "删装着东西的 recipes-copy，先 ls -a recipes-copy 看过，再 rm -r recipes-copy。"),
        ("答案：在 downloads 里先 ls 看全部，然后每删一样都先用 ls 看同样的名字：\n"
         "ls *.tmp（数清个数），再 rm *.tmp；\n"
         "ls \"report copy.txt\"，再 rm \"report copy.txt\"；\n"
         "ls -a 加空文件夹的名字（只列出 . 和 .. 就是空的），再 rmdir 加这个名字；\n"
         "ls -a 加 installer 开头的文件夹名字，再 rm -r 加这个名字；最后 ls 看一遍。\n"
         "解释：通配符 *.tmp 只选中以 .tmp 结尾的名字，所以 tmp-plan.txt 不受影响；"
         "不加引号，rm 会把 report 和 copy.txt 当成两个文件；rmdir 只删空文件夹；"
         "rm -r 连同里面的东西一起删。检查问的个数，就是删之前 ls *.tmp 列出的文件个数。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {
        "id": "1.2-r1", "type": "recall", "tier": "fluent", "station": "1.2b", "rule": "TERM-02",
        "q": "在终端里用 rm 删掉的文件，能从废纸篓里找回来吗？可能还想要回来的东西，该怎么删？",
        "a": ("不能。rm 立刻删除，不经过废纸篓。删之前先用 ls 加同样的名字看清要删什么。"
              "可能还想要回来的东西，在 Finder 里删，它会进废纸篓。"),
    },
    {
        "id": "1.2-r2", "type": "which", "tier": "fluent", "station": "1.2a",
        "q": "想把文件 draft.txt 改名为 final.txt，用哪条命令？",
        "options": ["cp draft.txt final.txt", "mv draft.txt final.txt", "rename draft.txt final.txt"],
        "answer": "B",
        "explain": "改名就是原地移动，用 mv。cp 会留下原来的 draft.txt，多出一份；Mac 自带的终端里没有 rename 命令。",
    },
    {
        "id": "1.2-r3", "type": "which", "tier": "fluent", "station": "1.2a",
        "q": "要把文件夹 photos 连同里面所有文件复制一份，叫 photos-backup，用哪条命令？",
        "options": ["cp photos photos-backup", "cp -R photos photos-backup", "mv photos photos-backup"],
        "answer": "B",
        "explain": "复制文件夹要加 -R；不加会报 is a directory (not copied)。mv 是搬走，原来的 photos 就没了。",
    },
    {
        "id": "1.2-r4", "type": "fault", "tier": "fluent", "station": "1.2b", "rule": "TERM-02",
        "q": "下面这条命令想删掉文件 old copy.txt，哪里不对？\n\n    rm old copy.txt",
        "options": [
            "名字里有空格，要加引号",
            "删文件要用 rmdir，不用 rm",
            "要加 -r，rm 才能删 .txt 文件",
        ],
        "answer": "A", "shuffle": True,
        "explain": ("正确的写法是 rm \"old copy.txt\"。不加引号，rm 会把它当成 old 和 copy.txt 两个文件，"
                    "碰巧有叫 copy.txt 的文件就会被删掉。rmdir 只删空文件夹；-r 是删文件夹用的。"),
    },
    {
        "id": "1.2-r5", "type": "predict", "tier": "lookup", "station": "1.2a",
        "q": "文件夹 site 已经存在。运行 cp -R starter site 之后会怎样？",
        "options": [
            "site 里面多出一个 starter 文件夹",
            "site 被换成 starter 的内容，原来的东西没了",
            "报错：site 已经存在",
        ],
        "answer": "A",
        "explain": "目标是已有的文件夹时，cp 和 mv 都会把东西放进它里面。这也是同一条复制命令运行两次会多套一层的原因。",
    },
    {
        "id": "1.2-d1", "type": "do", "tier": "lookup", "station": "1.2b", "rule": "TERM-02",
        "q": ("练习场里有一个 downloads 文件夹。按说明删掉该删的：所有 .tmp 文件、名字带空格的那个副本、"
              "一个空文件夹和一个装着东西的文件夹。其他的一个都不能少。删之前先数清 .tmp 文件的个数，交作业时会问。"),
        "scenario": "1.2b", "check": _downloads_cleaned,
    },
]


# ---------------------------------------------------------------------------
# EXAM (gate-a)
# ---------------------------------------------------------------------------
X1_FILES = ["budget.txt", "contacts.txt", "menu.txt"]
X1_BOXES = ["backup", "archive", "copies"]
X1_RENAMES = [("draft.txt", "final.txt"), ("notes-old.txt", "notes-2026.txt"), ("todo.txt", "done.txt")]
X1_SOURCES = ["recipes", "letters", "songs"]
X1_LOOSE = ["index.txt", "readme.txt", "list.txt"]


def build_x1(sc):
    """Copy and move: form A works on files, form B on a folder."""
    if sc.form == "A":
        name = sc.pick(X1_FILES)
        box = sc.pick(X1_BOXES)
        old, new = sc.pick(X1_RENAMES)
        sc.write(name, "要复制的文件：" + name)
        sc.mkdir(box)
        sc.write(old, "要改名的文件：" + old)
        sc.fact("file", name)
        sc.fact("box", box)
        sc.fact("old", old)
        sc.fact("new", new)
    else:
        src = sc.pick(X1_SOURCES)
        copy = src + sc.pick(["-backup", "-copy", "-2026"])
        loose = sc.pick(X1_LOOSE)
        sc.write(src + "/one.txt", "第一份")
        sc.write(src + "/two.txt", "第二份")
        sc.write(loose, "要移进新文件夹的文件")
        sc.fact("src", src)
        sc.fact("copy", copy)
        sc.fact("loose", loose)


def grade_x1(ctx):
    info = ctx.scenario()
    root = info.path
    facts = info.facts
    if info.form == "A":
        ctx.expect(ctx.is_file(root / facts["box"] / facts["file"]),
                   "文件夹 " + facts["box"] + " 里有 " + facts["file"] + " 了",
                   "文件夹里还没有那个文件的副本", where=facts["box"], saw="里面没有 " + facts["file"])
        if not ctx.is_file(root / facts["file"]):
            ctx.fail("原件不见了：题目要的是复制", where=ctx.show(root), saw="没有 " + facts["file"])
        elif ctx.is_file(root / facts["box"] / facts["file"]):
            ctx.ok("原件还在原处")
        ctx.expect(ctx.is_file(root / facts["new"]), "新名字的文件有了",
                   "还没有新名字的文件", where=ctx.show(root), saw="没有 " + facts["new"])
        ctx.expect(not ctx.exists(root / facts["old"]), "旧名字已经没有了",
                   "旧名字的文件还在：改名后旧名字不该留下", where=ctx.show(root), saw=facts["old"] + " 还在")
    else:
        src = root / facts["src"]
        copy = root / facts["copy"]
        if ctx.is_file(copy):
            ctx.fail("新名字要是一个文件夹", where=ctx.show(root),
                     saw=facts["copy"] + " 现在是一个文件，不是文件夹")
        if not (ctx.is_file(src / "one.txt") and ctx.is_file(src / "two.txt")):
            ctx.fail("原来的文件夹不完整了：题目要的是复制", where=facts["src"], saw="少了文件")
        elif ctx.is_dir(copy):
            ctx.ok("原来的文件夹原样还在")
        if ctx.is_dir(copy):
            ctx.ok("新文件夹有了")
        elif not ctx.exists(copy):
            ctx.fail("还没有题目要求的新文件夹", where=ctx.show(root), saw="没有 " + facts["copy"])
        if ctx.is_dir(copy):
            ctx.expect(ctx.is_file(copy / "one.txt") and ctx.is_file(copy / "two.txt"),
                       "新文件夹里有原来的两个文件", "新文件夹里还缺原来的文件",
                       where=facts["copy"], saw="one.txt 或 two.txt 不在里面")
            ctx.expect(ctx.is_file(copy / facts["loose"]), "新文件夹里有那个文件",
                       "新文件夹里还没有那个文件", where=facts["copy"], saw="没有 " + facts["loose"])
        if ctx.exists(root / facts["loose"]):
            ctx.fail("外面还留着那个文件：题目要的是移动", where=ctx.show(root), saw=facts["loose"] + " 还在")
        elif ctx.is_file(copy / facts["loose"]):
            ctx.ok("外面已经没有那个文件了")


X2_EXTS = ["tmp", "bak", "old"]
X2_SPACED = [("photo copy.jpg", "photo.jpg"), ("notes copy.txt", "notes.txt"), ("plan copy.md", "plan.md")]


def build_x2(sc):
    """Delete safely: form A with a wildcard, form B with quotes and rmdir."""
    keep = ["report.txt", "pictures/cat.jpg"]
    sc.write("report.txt", "要留下的报告")
    sc.write("pictures/cat.jpg", "（照片的替身）")
    junk_dir = sc.pick(["cache", "build", "logs"]) + "-" + sc.word()
    sc.write(junk_dir + "/a.dat", "垃圾")
    sc.write(junk_dir + "/b.dat", "垃圾")
    junk = [junk_dir]
    if sc.form == "A":
        ext = sc.pick(X2_EXTS)
        for word in sc.words(sc.randint(3, 4)):
            name = word + "." + ext
            sc.write(name, "可以删")
            junk.append(name)
        lookalike = ext + "-list.txt"
        sc.write(lookalike, "名字里有扩展名的字样，但要留着")
        keep.append(lookalike)
        sc.fact("ext", ext)
    else:
        spaced, original = sc.pick(X2_SPACED)
        sc.write(spaced, "多余的副本")
        sc.write(original, "原件，要留着")
        keep.append(original)
        empty_dir = "empty-" + sc.word()
        sc.mkdir(empty_dir)
        junk += [spaced, empty_dir]
        sc.fact("spaced", spaced)
        sc.fact("empty_dir", empty_dir)
    sc.fact("junk_dir", junk_dir)
    sc.fact("junk", junk)
    sc.fact("keep", keep)


def grade_x2(ctx):
    info = ctx.scenario()
    root = info.path
    lost = [name for name in info.facts["keep"] if not ctx.is_file(root / name)]
    left = [name for name in info.facts["junk"] if ctx.exists(root / name)]
    if lost:
        ctx.fail("不该删的也被删了", where=ctx.show(root), saw="不见了：" + "、".join(lost[:3]))
    elif len(left) < len(info.facts["junk"]):
        ctx.ok("该留下的都还在")
    ctx.expect(not left, "该删的都删掉了", "还有该删的没删", where=ctx.show(root),
               saw="还在：" + "、".join(left[:4]))


EXAM = [
    {
        "id": "1.2-x1",
        "gate": "gate-a",
        "title": "复制、改名和移动",
        "minutes": 5,
        "build": build_x1,
        "task": {
            "A": "在 {dir} 里：把文件 {file} 复制一份放进文件夹 {box}（原件留在原处），再把文件 {old} 改名为 {new}。",
            "B": "在 {dir} 里：把文件夹 {src} 连同里面的东西复制一份，新文件夹叫 {copy}；再把文件 {loose} 移进 {copy} 里。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.2-x2",
        "gate": "gate-a",
        "title": "只删该删的",
        "minutes": 6,
        "build": build_x2,
        "task": {
            "A": "在 {dir} 里：删掉所有以 .{ext} 结尾的文件，再删掉文件夹 {junk_dir}（连同里面的东西）。其他的一个都不能少。",
            "B": "在 {dir} 里：删掉文件「{spaced}」、空文件夹 {empty_dir} 和文件夹 {junk_dir}（连同里面的东西）。其他的一个都不能少。",
        },
        "grade": grade_x2,
    },
]
