"""Lesson 1.1: 终端：新建与查看 (plan section 4, task T2).

Station a: mkdir, touch, ls -l, ls -a; the new concept is the option.
Station b: cat, less, head; the new concept is the text file.
Rule: TERM-01.  Gate: gate-a.

Standard library only, Python 3.9 syntax, no side effects at import time.
API reference: docs/authoring/tool-api.md.
"""

import math

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.1",
    "slug": "01-create-and-view",
    "title": "终端：新建与查看",
    "stage": 1,
    "prerequisites": ["0.4"],
    "stations": [
        {
            "id": "1.1a",
            "title": "新建",
            "minutes": 35,
            "new_concept": "选项：命令后面加一个短横线和字母，改变命令的做法",
            # mkdir belongs to 0.2 (COMMON.md section 10); this station reuses it.
            "new_commands": ["touch", "ls -l", "ls -a"],
        },
        {
            "id": "1.1b",
            "title": "查看",
            "minutes": 35,
            "new_concept": "文本文件：由文字组成、能直接显示在终端里的文件",
            "new_commands": ["cat", "less", "head", "head -n"],
        },
    ],
    "rules": ["TERM-01"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9", "less": "668"},
    },
    "unverified_steps": [
        "1.1b：less 里按空格翻页、按 q 退出，less 底部显示的文件名、冒号和 (END)，"
        "以及按 v 会用 vi 打开文件（EDITOR 没有设置时），是对照 less 668 的手册写的；"
        "建课环境没有终端窗口，less 的界面没有实际跑过",
        "1.1b：cat 一个图片文件时屏幕上的乱码长什么样，取决于终端程序，建课时无法验证",
    ],
}

TERMS = [
    {"term": "选项", "en": "option",
     "plain": "跟在命令后面、以短横线开头的开关，用来改变命令的做法，比如 ls -l 里的 -l",
     "first": "1.1a"},
    {"term": "隐藏文件", "en": "hidden file",
     "plain": "名字以点开头的文件或文件夹，ls 默认不列出来，加 -a 才看得见",
     "first": "1.1a"},
    {"term": "字节", "en": "byte",
     "plain": "计算机里算文件大小的基本单位，一个英文字母占 1 字节；ls -l 里日期前面的数字就是字节数",
     "first": "1.1a"},
    {"term": "文本文件", "en": "text file",
     "plain": "里面只有文字的文件，可以直接在终端里显示；图片、压缩包这类文件不是",
     "first": "1.1b"},
]


# ---------------------------------------------------------------------------
# Practice material
# ---------------------------------------------------------------------------
# A 4x4 blue PNG.  The bytes were chosen so that printing the file with cat
# sends no escape (0x1b), shift-in/out (0x0e/0x0f), bell (0x07) or XOFF (0x13)
# to the terminal.  It does contain CR, LF, BS and FF (so the output spans a
# few lines) and three bytes in the C1 range (0x89, 0x93, 0x82); a UTF-8
# terminal shows those as invalid characters and does not act on them.  The
# learner sees gibberish, but the terminal is not left in a strange state.
CHART_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x04\x00\x00\x00\x04"
    b"\x08\x02\x00\x00\x00&\x93\t)\x00\x00\x00\x10IDATx\xdac\xd0\xca\xbf\x01"
    b"G\x0c\xc4q\x00M\x12\x17\x11\xcd\xb4K\xd2\x00\x00\x00\x00IEND\xaeB`\x82"
)

HISTORY_DAYS = 120          # data lines in history/usd-cny.txt
MONTH_DAYS = [31, 31, 30, 31, 30, 31]   # July ... December 2026


def _history_text():
    """Deterministic: the lesson text quotes its first lines verbatim."""
    lines = ["# 美元兑人民币，每天一行：日期，1 美元可换的人民币。数字是为练习编的，不是真实汇率。"]
    month, day = 7, 1
    for n in range(HISTORY_DAYS):
        value = 7.10 + 0.04 * math.sin(n / 9.0) + 0.01 * math.cos(n / 2.0)
        lines.append("2026-{:02d}-{:02d}  {:.4f}".format(month, day, value))
        day += 1
        if day > MONTH_DAYS[month - 7]:
            month, day = month + 1, 1
    return "\n".join(lines) + "\n"


EUR_DAYS = 100              # data lines in history/eur-cny.txt (the 补全 file of 1.1b)


def _eur_text():
    """A second long file, so the 补全 of 1.1b does not preview the 自己做 file."""
    lines = ["# 欧元兑人民币，每天一行：日期，1 欧元可换的人民币。数字是为练习编的，不是真实汇率。"]
    month, day = 7, 1
    for n in range(EUR_DAYS):
        value = 7.75 + 0.05 * math.cos(n / 11.0) + 0.01 * math.sin(n / 3.0)
        lines.append("2026-{:02d}-{:02d}  {:.4f}".format(month, day, value))
        day += 1
        if day > MONTH_DAYS[month - 7]:
            month, day = month + 1, 1
    return "\n".join(lines) + "\n"


NOTE_LINE = "这是一条练习用的便签。\n"                 # 34 bytes in UTF-8
HIDDEN_NAMES = [".draft", ".backup-notes", ".old-plan", ".todo"]

TOPICS = [
    "每周固定三个晚上学习", "先把终端命令练熟", "每次学习结束写一句日志",
    "遇到报错先读三问", "看不懂的命令先查手册", "练习只在练习场里做",
    "每课结束复习一次", "提问时写清楚做了什么", "累了就存档收工",
    "周末复盘这一周", "复习题到期就做", "把规范用自己的话写下来",
]


def _build_inbox(sc):
    """inbox/: visible notes plus hidden ones; a hidden one is the largest."""
    visible = sc.randint(2, 3)
    hidden = sc.randint(1, 2)
    names = [w + ".txt" for w in sc.words(visible)]
    sizes = sc.sample(range(1, 6), visible)               # in lines of NOTE_LINE
    for name, lines in zip(names, sizes):
        sc.write("inbox/" + name, NOTE_LINE * lines, exact=True)
    biggest = max(sizes)
    hidden_names = sc.sample(HIDDEN_NAMES, hidden)
    for number, name in enumerate(hidden_names):
        lines = biggest + 2 + number * 2 if number == 0 else sc.randint(1, biggest)
        sc.write("inbox/" + name, NOTE_LINE * lines, exact=True)
    sc.fact("inbox_count", visible + hidden)


def _build_archive(sc):
    """archive/meeting-notes.txt: line 2 and the last line carry the answers."""
    people = sc.randint(3, 12)
    room = sc.randint(13, 40)
    items = sc.randint(80, 110)
    lines = ["# 学习小组会议记录（练习用，内容是编的）", "参会人数：{} 人".format(people)]
    for number in range(1, items + 1):
        lines.append("第 {} 项：{}".format(number, sc.pick(TOPICS)))
    lines.append("下次会议地点：{} 号会议室".format(room))
    sc.write("archive/meeting-notes.txt", "\n".join(lines) + "\n", exact=True)
    sc.fact("people", people)
    sc.fact("room", room)
    sc.fact("items", items)


def build_start(sc):
    """The state just before lesson 1.1: a practice folder to look at.

    The website (state S0) does not exist yet, so nothing of it is built.
    """
    sc.copy_in("starter/hello-fx", "hello-fx")
    sc.write("history/usd-cny.txt", _history_text(), exact=True)
    sc.write("history/eur-cny.txt", _eur_text(), exact=True)
    sc.write_bytes("history/chart.png", CHART_PNG)
    _build_inbox(sc)
    _build_archive(sc)
    sc.todo("hello-fx：阶段 0 用过的小程序和它的数据文件 rates.txt")
    sc.todo("history、inbox、archive：这一课要看的文件和文件夹")


def build_drill(sc):
    """For the review item 1.1-d1: an empty folder and two seeded names."""
    folder = sc.fact("folder", sc.word() + "-box")
    name = sc.fact("file", sc.word() + ".txt")
    sc.todo("在这里新建文件夹 {}，并在它里面放一个空文件 {}".format(folder, name))


SCENARIOS = {
    "start": build_start,
    "1.1-drill": build_drill,
}


# ---------------------------------------------------------------------------
# Helpers for checks
# ---------------------------------------------------------------------------
def _squash(name):
    """A name with case, spaces and punctuation removed, for near misses."""
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _entry(ctx, parent, name, kind, label):
    """Look for ``name`` (exact spelling) in ``parent``.

    kind is "dir" or "file".  Records ok or fail and returns True when the
    entry is there with the right spelling and the right kind.
    """
    names = ctx.listdir(parent)
    where = ctx.show(parent)
    if name in names:
        path = parent / name
        if kind == "dir" and not ctx.is_dir(path):
            return ctx.fail("{} 要是一个文件夹".format(name), where=where,
                            saw="{} 现在是一个文件".format(name))
        if kind == "file" and not ctx.is_file(path):
            return ctx.fail("{} 要是一个文件".format(name), where=where,
                            saw="{} 现在是一个文件夹".format(name))
        return ctx.ok(label + "建好了")
    for other in names:
        if other.lower() == name.lower():
            return ctx.fail(label + "名字的大小写不对", where=where,
                            saw="现在叫「{}」".format(other))
    for other in names:
        if _squash(other) == _squash(name) or _squash(other) == _squash(name.rsplit(".", 1)[0]):
            return ctx.fail(label + "名字还差一点", where=where,
                            saw="有一个叫「{}」的，逐个字符对一下".format(other))
    return ctx.fail(label + "还没有建", where=where, saw="这里没有叫 {} 的东西".format(name))


def _misplaced(ctx, base, name, expected_parent):
    """Note where ``name`` turned up instead, without saying how to fix it.

    The workspace comes first among the other places: every check sends the
    learner there, so it is the likeliest wrong folder.
    """
    workspace = ctx.workspace
    inside = (base, base / "trip", base / "trip" / "photos", base / "memo")
    outside = (workspace, workspace / "notes", ctx.home)
    for candidate in inside + outside:
        if candidate == expected_parent:
            continue
        if name in ctx.listdir(candidate):
            text = "{} 出现在了 {} 里。建之前先用 pwd 看看自己在哪个文件夹。".format(
                name, ctx.show(candidate))
            if candidate in outside:
                text += STRAY_NOTE
            ctx.note(text)
            return


STRAY_NOTE = "建错地方的那个先留着不碍事，第 1.2 课学了删除再清掉它。"


def _stray_memo(ctx):
    """The 跟我做 folder memo is not checked; note it when it landed in the workspace."""
    if ctx.is_dir(ctx.workspace / "memo"):
        ctx.note("学习工作区里有一个 memo 文件夹。如果它是做「跟我做」时建错了地方："
                 "先留着不碍事，第 1.2 课学了删除再清掉它；「跟我做」不检查，不用重做。")


RESET_NOTE = ("现在可以从头来：回到学习工作区运行 python3 tools/course.py scenario 1.1 --reset"
              " 重搭练习场景，再做一遍第 1 站的「自己做」。")


def _undo_note(ctx, parent, name, kind):
    """A mistake the learner cannot undo yet (rename and delete come in 1.2).

    Two cases: a name that differs only in case (on a Mac, mkdir with the
    right case then says File exists; touch says nothing and the name keeps
    its old case), and the right name made as the wrong kind (a file where a
    folder belongs, or the other way round).
    """
    names = ctx.listdir(parent)
    if name in names:
        path = parent / name
        wrong_kind = not ctx.is_dir(path) if kind == "dir" else not ctx.is_file(path)
        if wrong_kind:
            ctx.note("文件夹和文件不能同名，这个名字已经被占了。删除和改名要到第 1.2 课才学。" + RESET_NOTE)
    elif any(other.lower() == name.lower() for other in names):
        if kind == "dir":
            again = "再用 mkdir 建一次会提示 File exists（已经存在）。"
        else:
            again = "再用 touch 建一次不会报错，但名字还是原来的大小写。"
        ctx.note("Mac 的文件名不分大小写，" + again + "改名要到第 1.2 课才学。" + RESET_NOTE)


def _trip_built(ctx, base):
    """Station 1.1a, part 1: trip/, trip/photos/, trip/day-1.txt."""
    trip = base / "trip"
    if not _entry(ctx, base, "trip", "dir", "文件夹 trip "):
        _undo_note(ctx, base, "trip", "dir")
        _misplaced(ctx, base, "trip", base)
        return
    if not _entry(ctx, trip, "photos", "dir", "trip 里的文件夹 photos "):
        _undo_note(ctx, trip, "photos", "dir")
        _misplaced(ctx, base, "photos", trip)
    if _entry(ctx, trip, "day-1.txt", "file", "trip 里的文件 day-1.txt "):
        if ctx.size(trip / "day-1.txt"):
            ctx.note("day-1.txt 里面已经有内容了。题目要的是空文件，这不影响通过。")
    else:
        _undo_note(ctx, trip, "day-1.txt", "file")
        if "day" in ctx.listdir(trip):
            text = ("trip 里有一个叫 day 的东西。名字里的空格会把一个名字拆成两个，"
                    "题目要的名字中间是短横线 -。")
            # touch trip/day 1.txt also makes 1.txt where the learner stood.
            for folder in (base, trip):
                if "1.txt" in ctx.listdir(folder):
                    text += "拆出来的另一半是 {} 里的 1.txt：它先留着不碍事，第 1.2 课学了删除再清掉它。".format(
                        ctx.show(folder))
                    break
            ctx.note(text)
        _misplaced(ctx, base, "day-1.txt", trip)


def _inbox_questions(ctx, base):
    """Station 1.1a, part 2: two answers that only ls -l and ls -a give."""
    inbox = base / "inbox"
    if not ctx.is_dir(inbox):
        ctx.fail("练习场景里的 inbox 文件夹不见了", where=ctx.show(base),
                 saw="没有 inbox。运行 python3 tools/course.py scenario 1.1 --reset 重搭一份")
        ctx.stop()
    # Finder writes a hidden .DS_Store into a folder as soon as it shows it.
    # The learner sees it in ls -la, so an answer that counts it is right too.
    every = ctx.listdir(inbox)
    names = [n for n in every if n != ".DS_Store"]
    visible = [n for n in names if not n.startswith(".")]
    counts = sorted({len(names), len(every)})
    if not ctx.ask("inbox 里一共有几个文件？隐藏文件也算，. 和 .. 不算。", expected=counts):
        typed = ctx.parse_int(ctx.last_answer or "")
        if typed == len(visible):
            ctx.note("你数的和不加 -a 时看到的一样多。名字以点开头的文件，默认不会列出来。")
        elif typed in [count + 2 for count in counts]:
            ctx.note("你可能把 . 和 .. 也数进去了。它们代表“这个文件夹”和“上一层”，不是文件。")
    sizes = {n: ctx.size(inbox / n) for n in every if ctx.is_file(inbox / n)}
    largest = sorted({max(sizes[n] for n in names if n in sizes), max(sizes.values())})
    largest_visible = max([sizes[n] for n in visible if n in sizes] or [-1])
    if not ctx.ask("inbox 里最大的那个文件（隐藏的也算）有多少字节？只填数字。", expected=largest):
        typed = ctx.parse_int(ctx.last_answer or "")
        if typed == largest_visible:
            ctx.note("这是不算隐藏文件时最大的那个。隐藏文件也要比一比。")
        elif typed is not None and typed not in sizes.values():
            ctx.note("inbox 里没有哪个文件是这个大小。只看文件那几行，"
                     "不看 total 那一行，也不看 . 和 .. 那两行。")
    if ".DS_Store" in every:
        ctx.note("inbox 里的 .DS_Store 是 Finder（访达）自己记显示方式的隐藏文件，算不算它都可以。")


def check_a(ctx):
    info = ctx.scenario("start")
    base = info.path
    _stray_memo(ctx)
    _trip_built(ctx, base)
    if ctx.failed:
        ctx.stop()
    _inbox_questions(ctx, base)


def check_b(ctx):
    info = ctx.scenario("start")
    notes = info.path / "archive" / "meeting-notes.txt"
    if not ctx.is_file(notes):
        ctx.fail("练习场景里的 archive/meeting-notes.txt 不见了", where=ctx.show(info.path / "archive"),
                 saw="没有这个文件。运行 python3 tools/course.py scenario 1.1 --reset 重搭一份")
        ctx.stop()
    facts = info.facts
    if not ctx.ask("archive/meeting-notes.txt 的第 2 行写着参会人数。是几个人？", expected=facts["people"]):
        typed = ctx.parse_int(ctx.last_answer or "")
        if typed == 2:
            ctx.note("2 是行号。题目问的是第 2 行里写的那个人数。")
        elif typed == facts["room"]:
            ctx.note("这个数在文件的最后一行。人数写在开头的第 2 行。")
    if not ctx.ask("这个文件的最后一行写着下次会议在几号会议室？", expected=facts["room"]):
        typed = ctx.parse_int(ctx.last_answer or "")
        if typed == facts["items"]:
            ctx.note("这是最后一个“第几项”的编号。最后一行在它下面，还要再往下看一行。")
        elif typed == facts["people"]:
            ctx.note("这个数在文件开头的第 2 行。题目问的是最后一行。")


checks = {"1.1a": check_a, "1.1b": check_b}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.1a": [
        "一共两件事：先建出 trip、photos、day-1.txt 这三样，再用 ls 加选项把 inbox 看清楚。"
        "检查结果里的“还缺什么”说的是哪一件？",
        "建之前先运行 pwd，确认你在 ~/Developer/playground/1.1-start 里。"
        "文件夹用第 1 站“建一个文件夹”那一步的命令，空文件用“建一个空文件”那一步的命令。"
        "inbox 的两个问题，用“看隐藏文件”和“看详细信息”两步里的命令。"
        "命令名和选项之间要有一个空格，短横线要在英文输入法下打。",
        "相似的例子：要在 garden 文件夹里建文件夹 seeds 和空文件 plan.txt，"
        "依次运行 mkdir garden、mkdir garden/seeds、touch garden/plan.txt。"
        "要看 garden 里所有文件的大小，连隐藏的一起，运行 ls -la garden。",
        "答案：在 1.1-start 里依次运行 mkdir trip、mkdir trip/photos、touch trip/day-1.txt，"
        "再运行 ls -la inbox。除了 total 那一行和 . 、.. 两行，剩下几行就是几个文件；"
        "每行日期前面的那个数字是大小（字节），挑最大的那个。"
        "解释：mkdir 建文件夹，touch 建空文件；-a 让 ls 连名字以点开头的隐藏文件一起列出，"
        "-l 让它每个文件一行、带上大小和日期，两个选项可以合写成 -la。",
    ],
    "1.1b": [
        "两个问题都要先看文件内容：一个在开头，一个在最后。想一想哪条命令只看开头，哪条命令能一页一页翻到底。",
        "先确认在 ~/Developer/playground/1.1-start 里，文件是 archive/meeting-notes.txt。"
        "第 1 个问题用第 2 站“只看开头”那一步的命令；第 2 个问题用“一页一页地看”那一步的命令，翻到出现 (END) 为止。",
        "相似的例子：想看 history/usd-cny.txt 的前 4 行，运行 head -n 4 history/usd-cny.txt；"
        "想看它的最后一行，运行 less history/usd-cny.txt，一直按空格，直到底部出现 (END)，看完按 q 退出。",
        "答案：运行 head -n 2 archive/meeting-notes.txt，第 2 行就是参会人数；"
        "再运行 less archive/meeting-notes.txt，按空格翻到底（出现 (END)），最后一行写着会议室号码，按 q 退出。"
        "解释：head 只显示开头几行，-n 后面的数字说显示几行；less 一页一页地显示，适合长文件。"
        "用 cat 一次全部倒出来再往上找也能答对，但长文件用 less 更方便。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
def _drill_done(ctx):
    """The do item 1.1-d1: a seeded folder with a seeded empty file in it."""
    info = ctx.scenario("1.1-drill")
    folder = info.facts["folder"]
    name = info.facts["file"]
    if _entry(ctx, info.path, folder, "dir", "文件夹 {} ".format(folder)):
        _entry(ctx, info.path / folder, name, "file", "{} 里的文件 {} ".format(folder, name))


REVIEW = [
    {"id": "1.1-r1", "type": "which", "tier": "fluent", "station": "1.1a",
     "q": "在 Mac 的终端里，想把一个文件夹里的东西连同隐藏文件一起列出来，用哪条命令？",
     "options": ["ls -a", "ls -l", "ls --all"],
     "answer": "A", "shuffle": True,
     "explain": "-a 是 all 的意思，会列出名字以点开头的文件。-l 只是多显示详细信息；"
                "--all 是 Linux 上的写法，Mac 的 ls 不认识，会报 unrecognized option。"},
    {"id": "1.1-r2", "type": "recall", "tier": "fluent", "station": "1.1a",
     "q": "什么样的文件是“隐藏文件”？ls -l 输出的每一行里，靠右边的三样信息分别是什么？",
     "a": "名字以点开头的文件或文件夹，比如 .draft；ls 默认不列出它们，要加 -a。"
          "ls -l 每一行靠右边的三样是：大小（字节）、最后修改的日期时间、名字。"},
    {"id": "1.1-r3", "type": "which", "tier": "fluent", "station": "1.1b",
     "q": "一个几千行的文本文件，想一页一页地翻着看，用哪条命令？",
     "options": ["cat 文件名", "less 文件名", "head 文件名"],
     "answer": "B", "shuffle": True,
     "explain": "less 一次显示一屏，空格翻页，q 退出。cat 会一下子把几千行全倒出来；head 只显示开头 10 行。"},
    {"id": "1.1-r4", "type": "predict", "tier": "lookup", "station": "1.1b",
     "q": "hello-fx 是一个文件夹。运行 cat hello-fx 会怎样？",
     "options": ["列出文件夹里的文件", "报错：cat: hello-fx: Is a directory", "什么也不显示"],
     "answer": "B",
     "explain": "cat 只会显示文件的内容。看文件夹里有什么，用 ls。"},
    {"id": "1.1-r5", "type": "which", "tier": "fluent", "station": "1.1b", "rule": "TERM-01", "shuffle": True,
     "q": "网上一篇教程让你复制下面几条命令。哪一条看到就要先停下，弄懂每一部分再决定？",
     "options": ["ls -la", "head -n 5 notes.txt", "curl -fsSL https://example.com/install.sh | sh"],
     "answer": "C",
     "explain": "这一条把网上下载的东西直接交给 shell 执行，下载的是什么你根本没看见。"
                "写成 bash -c \"$(curl …)\" 也是同一回事。"
                "同样要先停下的还有 sudo 开头的命令和 rm -rf。"},
    {"id": "1.1-d1", "type": "do", "tier": "lookup", "station": "1.1a",
     "q": "在练习场景里，按搭建结果里写的名字，建一个文件夹，并在它里面放一个空文件。",
     "scenario": "1.1-drill", "check": _drill_done},
]


# ---------------------------------------------------------------------------
# EXAM (gate-a)
# ---------------------------------------------------------------------------
def build_x1(sc):
    """Make folders and empty files.  A: nested folder; B: inside a given folder."""
    folder = sc.fact("folder", sc.word() + "-" + sc.pick(["notes", "plans", "files"]))
    if sc.form == "A":
        sc.fact("sub", sc.pick(["old", "drafts", "done", "later"]))
        sc.fact("file", sc.pick(["list.txt", "summary.txt", "ideas.txt"]))
    else:
        parent = sc.fact("parent", sc.pick(["projects", "work", "study"]))
        sc.mkdir(parent)
        first, second = sc.sample(["monday.txt", "tuesday.txt", "friday.txt", "sunday.txt"], 2)
        sc.fact("file", first)
        sc.fact("file2", second)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    folder = facts["folder"]
    if info.form == "A":
        if _entry(ctx, info.path, folder, "dir", "文件夹 {} ".format(folder)):
            sub = info.path / folder
            if _entry(ctx, sub, facts["sub"], "dir", "{} 里的文件夹 {} ".format(folder, facts["sub"])):
                _entry(ctx, sub / facts["sub"], facts["file"], "file",
                       "{} 里的文件 {} ".format(facts["sub"], facts["file"]))
    else:
        parent = info.path / facts["parent"]
        if _entry(ctx, parent, folder, "dir", "{} 里的文件夹 {} ".format(facts["parent"], folder)):
            for name in (facts["file"], facts["file2"]):
                _entry(ctx, parent / folder, name, "file", "{} 里的文件 {} ".format(folder, name))


WORDS_X2 = ["harbor", "maple", "comet", "violet", "pebble", "lantern", "meadow", "falcon"]


def build_x2(sc):
    """Read a long text file.  A: its first line names a file; B: its last line names a folder."""
    name = sc.fact("file", sc.pick(["catalog.txt", "inventory.txt", "records.txt"]))
    answer = sc.pick(WORDS_X2)
    filler = ["第 {} 条记录：{}".format(n, sc.pick(TOPICS)) for n in range(1, sc.randint(180, 220))]
    if sc.form == "A":
        lines = [answer] + filler
    else:
        lines = filler + [answer]
    sc.write(name, "\n".join(lines) + "\n", exact=True)
    sc.fact("answer", answer)


def grade_x2(ctx):
    """Never names the expected word in a failure: finding it is the task."""
    info = ctx.scenario()
    answer = info.facts["answer"]
    source = info.facts["file"]
    if info.form == "A":
        wanted, kind, what = answer + ".txt", "file", "按第 1 行的单词命名的空文件"
    else:
        wanted, kind, what = answer, "dir", "按最后一行的单词命名的文件夹"
    names = [n for n in ctx.listdir(info.path) if n not in (source, ".DS_Store", ".playground")]
    where = ctx.show(info.path)
    made = "、".join(names[:5]) if names else "什么也没有"
    if wanted in names:
        right_kind = ctx.is_file(info.path / wanted) if kind == "file" else ctx.is_dir(info.path / wanted)
        if right_kind:
            ctx.ok(what + "建好了")
        else:
            ctx.fail(what + "：名字对了，但种类不对", where=where,
                     saw="题目要的是" + ("文件" if kind == "file" else "文件夹") + "，你建的是另一种")
        return
    for other in names:
        if _squash(other) == _squash(wanted) or _squash(other) == _squash(answer):
            ctx.fail(what + "：名字还差一点", where=where,
                     saw="有一个叫「{}」的，和题目要求逐个字符对一下".format(other))
            return
    ctx.fail("还没有" + what, where=where, saw="新建的东西：" + made)


EXAM = [
    {
        "id": "1.1-x1",
        "gate": "gate-a",
        "title": "新建文件夹和空文件",
        "minutes": 4,
        "build": build_x1,
        "task": {
            "A": "在 {dir} 里新建文件夹 {folder}，在 {folder} 里再建一个文件夹 {sub}，"
                 "然后在 {sub} 里放一个空文件 {file}。",
            "B": "{dir} 里已经有一个文件夹 {parent}。在 {parent} 里新建文件夹 {folder}，"
                 "并在 {folder} 里放两个空文件：{file} 和 {file2}。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.1-x2",
        "gate": "gate-a",
        "title": "从长文件里读出信息",
        "minutes": 5,
        "build": build_x2,
        "task": {
            "A": "{dir}/{file} 有大约两百行。它的第 1 行只有一个英文单词。"
                 "在 {dir} 里新建一个空文件，名字是这个单词加上 .txt。",
            "B": "{dir}/{file} 有大约两百行。它的最后一行只有一个英文单词。"
                 "在 {dir} 里新建一个文件夹，名字就是这个单词。",
        },
        "grade": grade_x2,
    },
]
