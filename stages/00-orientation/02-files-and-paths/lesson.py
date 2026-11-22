"""Lesson 0.2: files, paths and a home for code (plan section 4, task T2).

Three stations:

- 0.2a paths: walk a fixed "town" in the start scenario (worked example),
  then a seeded maze (scenario 0.2a) where only the relative path with ``..``
  leads to the right file (ask check).
- 0.2b reading errors and asking for help: the error-reading questions, then
  ``man ls`` to find a seeded option and apply it in scenario 0.2b (quiz + ask).
- 0.2c a home for code: ``~/Developer`` exists, the learner reads ``doctor``
  and ``~/Developer/fullstack-from-zero`` leads to the workspace: either the moved
  folder itself or, for a learner who keeps the folder where it is (a free
  decision asked with ``ctx.choose``, stored as
  ``decisions.workspace_location``), the entrance link the tutor makes.

Standard library only, Python 3.9 syntax; imports nothing from the tool.
"""

import os
import posixpath
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "0.2",
    "slug": "02-files-and-paths",
    "title": "文件、路径和代码的家",
    "stage": 0,
    "prerequisites": ["0.1"],
    "stations": [
        {
            "id": "0.2a",
            "title": "路径：在文件夹之间走来走去",
            "minutes": 35,
            "new_concept": "路径是文件的地址：绝对路径从最顶上写起，相对路径从你现在站的地方写起",
            "new_commands": ["cd", "cd ..", "cd ~"],
        },
        {
            "id": "0.2b",
            "title": "读懂报错，查说明书",
            "minutes": 30,
            "new_concept": "报错和说明书都是程序写给你看的话：按报错三问读报错，用 man 查用法",
            "new_commands": ["man", "ls -F"],
        },
        {
            "id": "0.2c",
            "title": "给代码安个家",
            "minutes": 40,
            "new_concept": "代码放在不被云同步的固定文件夹里，这台 Mac 上是 ~/Developer",
            "new_commands": ["mkdir", "mkdir -p", "python3 tools/course.py doctor"],
        },
    ],
    "rules": ["WS-01", "WS-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9", "less": "668"},
    },
    "unverified_steps": [
        "0.2a：按 Tab 键补全文件夹名（构建环境没有交互式终端，无法实测；标〔建课时无法验证〕）",
        "0.2b：在 man 显示的说明书里翻页、按 / 搜索、按 n 找下一个、按 q 退出（只对照了本机的 man less 和 man man；标〔对照文档，界面可能不同〕）",
        "0.2b：从菜单栏的输入法菜单切到英文（对照 Apple 的 Mac 使用手册；标〔对照文档，界面可能不同〕）；用 Caps Lock 切换的设置放在文末「想多了解」，同样标注",
        "0.2c：导师复制学习工作区时，Claude 桌面应用请学习者批准导师要运行的命令（2026-11-20 对照 code.claude.com/docs/en/permissions：Manual 模式下运行 Bash 命令和改文件都要批准；docs/tutor/playbook.md §10 第 3 步；标〔对照文档，界面可能不同〕）",
        "0.2c：搬家以后在新位置重新打开 Claude 桌面应用（Code 标签页里开新会话，用输入框下面一行的项目文件夹按钮选 ~/Developer/fullstack-from-zero；2026-11-20 对照 code.claude.com/docs/en/desktop 和 README.md 的卡片「搬家后怎么找回导师」；标〔对照文档，界面可能不同〕）",
    ],
}

TERMS = [
    {"term": "路径", "en": "path", "plain": "文件在电脑里的地址", "first": "0.2a"},
    {"term": "绝对路径", "en": "absolute path",
     "plain": "从最顶上（/ 或 ~）写起的完整地址，在哪里用都指同一个地方", "first": "0.2a"},
    {"term": "相对路径", "en": "relative path",
     "plain": "从你现在所在的文件夹写起的地址，换个出发点就指向别处", "first": "0.2a"},
    {"term": "主文件夹", "en": "home folder",
     "plain": "你这个用户在电脑上的“家”，写作 ~", "first": "0.2a"},
    {"term": "上一级文件夹", "en": "parent folder",
     "plain": "装着当前文件夹的那个文件夹，写作 ..", "first": "0.2a"},
    {"term": "Tab 补全", "en": "tab completion",
     "plain": "名字打一半按 Tab 键，终端替你补完整", "first": "0.2a"},
    {"term": "说明书", "en": "manual page (man page)",
     "plain": "命令自带的使用说明，用 man 命令打开", "first": "0.2b"},
    {"term": "全角字符", "en": "full-width character",
     "plain": "中文输入法打出来的、占一个汉字宽的字母、数字、标点和空格；写在命令名、选项、分隔的空格和 ~ / - 这类符号里，命令就不认", "first": "0.2b"},
    {"term": "半角字符", "en": "half-width character",
     "plain": "英文输入状态下打出来的普通字母、数字、标点和空格；命令名、选项、分隔的空格和 ~ / - 这类符号只认它们", "first": "0.2b"},
    {"term": "云同步文件夹", "en": "cloud-synced folder",
     "plain": "里面的文件会被自动上传到云端、再同步到别的设备的文件夹", "first": "0.2c"},
    {"term": "短横线命名", "en": "kebab-case",
     "plain": "名字全用小写英文，单词之间用短横线 - 连接，例如 my-site", "first": "0.2c"},
]


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """The worked example of station a: a small fixed "town" (same for everyone).

    Fixed names, so that the outputs pasted in the lesson match exactly.
    """
    sc.write("town/north/library/map.txt", "图书馆的平面图\n")
    sc.write("town/north/library/reading-room/today.txt", "今天的阅览室开到晚上九点。\n")
    sc.write("town/south/market/price-list.txt", "苹果 5 元一斤\n")
    sc.write("town/south/station/timetable.txt", "8:00 第一班车\n")
    sc.todo("一个小镇模样的文件夹：" + sc.show("town"))


THINGS = ["lantern", "compass", "ticket", "letter", "badge", "coin", "ribbon", "whistle"]


def build_maze(sc):
    """Station a exercise: only the route with ``..`` reaches the target file.

    maze/<w1>/<w2>            start point
    maze/<w1>/<w3>/<w4>/T     target  (start + ../<w3>/<w4>)
    maze/<w1>/<w2>/<w3>/<w4>/A  decoy: the ``..`` was skipped
    maze/<w3>/<w4>/B          decoy: went up two levels
    """
    w1, w2, w3, w4, f1, f2 = sc.words(6)
    target, skip, up2, filler = sc.sample(THINGS, 4)
    target, skip, up2, filler = (target + ".txt", skip + ".txt", up2 + ".txt", filler + ".txt")
    sc.write(f"maze/{w1}/{w3}/{w4}/{target}", "找到了。\n")
    sc.write(f"maze/{w1}/{w2}/{w3}/{w4}/{skip}", "这里不是要找的地方。\n")
    sc.write(f"maze/{w3}/{w4}/{up2}", "这里也不是。\n")
    sc.write(f"maze/{f1}/{f2}/{filler}", "随便逛逛。\n")
    sc.mkdir(f"maze/{w1}/{f1}")
    sc.mkdir(f"maze/{w1}/{w2}/{f2}")
    start = f"maze/{w1}/{w2}"
    route = f"../{w3}/{w4}"
    sc.fact("start", start)
    sc.fact("route", route)
    sc.fact("target", target)
    sc.fact("target_rel", f"maze/{w1}/{w3}/{w4}/{target}")
    sc.fact("decoy_skip", skip)
    sc.fact("decoy_up2", up2)
    sc.todo("进入起点：cd " + sc.show(start))
    sc.todo("从起点出发要走的相对路径：" + route)
    sc.todo("走到以后看看那里有什么文件，再回到课文的「自己做」，写出这个文件的完整地址。")


SORT_TASKS = {
    # "Sort by descending" stays on one line of man ls down to 35 columns
    # ("time modified" wraps below about 45, and less then finds nothing).
    "t": {"desc": "按修改时间排序，最近改过的排在最前面", "keyword": "Sort by descending"},
    "S": {"desc": "按文件大小排序，最大的排在最前面", "keyword": "Sort by size"},
    "r": {"desc": "把排列的顺序倒过来", "keyword": "Reverse"},
}


def build_sorting(sc):
    """Station b exercise: four files; each way of sorting puts another one first."""
    names = sorted(name + ".txt" for name in sc.words(4))
    newest, largest = sc.sample([names[1], names[2]], 2)
    task = sc.pick(sorted(SORT_TASKS))
    hours_ago = {names[0]: 30, names[1]: 20, names[2]: 10, names[3]: 40}
    hours_ago[newest] = 1
    for index, name in enumerate(names):
        lines = 40 if name == largest else index + 2
        sc.write(name, "".join(f"第 {n} 行\n" for n in range(1, lines + 1)), exact=True)
        sc.set_mtime(name, sc.ago(hours=hours_ago[name]))
    first = {"t": newest, "S": largest, "r": names[-1]}[task]
    sc.fact("task", task)
    sc.fact("desc", SORT_TASKS[task]["desc"])
    sc.fact("keyword", SORT_TASKS[task]["keyword"])
    sc.fact("first", first)
    sc.fact("plain_first", names[0])
    sc.todo("这个文件夹里有 4 个文件：" + sc.show("."))
    sc.todo("任务：用 man ls 查出哪个选项能让 ls「" + SORT_TASKS[task]["desc"] + "」。")
    sc.todo("说明书是英文的，搜这个关键词能找到它：" + SORT_TASKS[task]["keyword"])
    sc.todo("查到以后，在这个文件夹里用这个选项运行 ls，记下排在最前面的文件名。")


SCENARIOS = {"start": build_start, "0.2a": build_maze, "0.2b": build_sorting}


# ---------------------------------------------------------------------------
# helpers shared by checks
# ---------------------------------------------------------------------------
ICLOUD_ATTRIBUTE = "com.apple.file-provider-domain-id"
XATTR = "/usr/bin/xattr"


def _strip_txt(name):
    return name[:-4] if name.endswith(".txt") else name


def _last_part(typed):
    """The file name in a typed name or address, without .txt ("~/…/ticket.txt" -> "ticket")."""
    return _strip_txt(posixpath.basename(_bare_address(typed)))


def _path_forms(ctx, path):
    """Every way a learner may legitimately write this absolute path, normalised."""
    forms = set()
    for candidate in (str(path), os.path.realpath(str(path)), ctx.show(path)):
        forms.add(posixpath.normpath(ctx.normalize(candidate).rstrip("/")))
    return forms


COMMAND_IN_FRONT = re.compile(r"^(?:cd|ls)\s+")


def _bare_address(typed):
    """The typed address without a ``cd`` / ``ls`` in front and without a trailing /."""
    return COMMAND_IN_FRONT.sub("", typed.strip()).rstrip("/")


def _same_path(ctx, path):
    """An ``expected`` function: the typed answer names ``path``.

    ``..`` and ``.`` inside the answer are walked first, so "start + route"
    (``~/…/wren/../north/violet/ticket.txt``) counts as the same address; a
    ``cd`` or ``ls`` typed in front of the address is left aside.
    """
    forms = _path_forms(ctx, path)

    def expected(typed):
        typed = _bare_address(typed)
        return bool(typed) and posixpath.normpath(typed) in forms
    return expected


def _synced_folder(ctx, folder):
    """The folder (or ancestor) that a sync provider manages, or None.

    The same test as ``doctor``: under ~/Library/Mobile Documents, or carrying
    the file-provider attribute.  Raises when it cannot look, so the learner
    sees 检查器出问题 and never a false 还没达标.
    """
    root = Path(os.path.realpath(str(folder)))
    mobile = Path(os.path.realpath(str(ctx.home / "Library" / "Mobile Documents")))
    if root == mobile or mobile in root.parents:
        return root
    trouble = False
    for candidate in [root] + list(root.parents):
        result = ctx.run([XATTR, str(candidate)], timeout=5)
        if result.missing or result.timed_out:
            raise RuntimeError("xattr unavailable: cannot tell whether the folder is synced")
        if not result.ok:
            trouble = True
            continue
        if ICLOUD_ATTRIBUTE in [line.strip() for line in result.out.splitlines()]:
            return candidate
    if trouble:
        raise RuntimeError("xattr failed on an ancestor: cannot tell whether the folder is synced")
    return None


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def check_a(ctx):
    """Ask: the file name at the end of the route, then its absolute path."""
    info = ctx.scenario("0.2a")
    facts = info.facts
    target = facts["target"]
    # A learner who already writes the whole address (as the lesson asks)
    # names the file too: its last part counts; question 2 checks the rest.
    right = ctx.ask("按相对路径走到的那个文件夹里，那个文件叫什么名字？（先写名字，完整地址下一题再问）",
                    expected=lambda typed: _last_part(typed) == _strip_txt(target))
    if not right:
        typed = _last_part(ctx.normalize(ctx.last_answer))
        if typed == _strip_txt(facts["decoy_skip"]):
            ctx.note("这个文件在起点的里面。相对路径开头的 .. 是让你先往上走一层，再往下走。")
        elif typed == _strip_txt(facts["decoy_up2"]):
            ctx.note("这个文件离起点太远了：路径里只有一个 ..，只往上走一层。")
        elif posixpath.normpath(_bare_address(ctx.normalize(ctx.last_answer)) or ".") in \
                _path_forms(ctx, (info.path / facts["target_rel"]).parent):
            ctx.note("这是那个文件所在文件夹的地址。这一题要的是文件名：在那个文件夹里运行 ls 看到的名字。")
        else:
            ctx.note("先 cd 到起点，用 pwd 确认站对了地方，再照着相对路径走，最后 ls。")
        ctx.stop()
    target_path = info.path / facts["target_rel"]
    right = ctx.ask("从主文件夹 ~ 写起，这个文件的完整地址是什么？（以 ~/ 开头）",
                    expected=_same_path(ctx, target_path))
    if not right:
        typed = posixpath.normpath(_bare_address(ctx.normalize(ctx.last_answer)) or ".")
        if not (typed.startswith("~") or typed.startswith("/")):
            ctx.note("这个地址不是从 ~ 写起的：从起点或当前文件夹写起的地址，换个地方就不对了。")
        elif typed in _path_forms(ctx, target_path.parent):
            ctx.note("这是那个文件所在文件夹的地址：最后还要加上 / 和文件名。")
        elif typed + ".txt" in _path_forms(ctx, target_path):
            ctx.note("文件名要写全，包括后面的 .txt。")
        else:
            ctx.note("在那个文件夹里运行 pwd，把它的输出和你写的地址一段一段地比。"
                     "写好以后可以用 ls 加上这个地址试一试。")


ERROR_QUIZ = {
    "question": ("终端里出现了这一行：\n\n    ls: Downlaods: No such file or directory\n\n"
                 "按报错三问的第一问：是谁在报错？"),
    "options": ["zsh，终端里接你命令的那个程序", "ls 命令", "Downlaods 这个文件夹"],
    "answer": "B",
    "explain": "冒号前面的第一个词就是报错的程序。这里是 ls：它没找到叫 Downlaods 的东西。",
    "feedback": {
        "A": "zsh 自己报错时，这一行会以 zsh: 开头。",
        "C": "Downlaods 是被找的对象，它根本不存在，没法报错。",
    },
}


def _option_is_right(ctx, task):
    """Accept "-t", "t", "ls -t"; upper and lower case are different options."""
    def bare(text):
        text = text.strip()
        if text.lower().startswith("ls "):
            text = text[3:].strip()
        return text[1:] if text.startswith("-") else text

    def expected(typed):
        raw = ctx.last_answer
        if ctx.normalize(raw) != typed:      # the typed text is not available: compare without case
            raw = typed
            return bare(raw).lower() == task.lower()
        return bare(raw) == task
    return expected


def check_b(ctx):
    """Quiz on reading an error, then the option found with man and its effect."""
    info = ctx.scenario("0.2b")
    facts = info.facts
    task = facts["task"]
    ctx.quiz(ERROR_QUIZ["question"], ERROR_QUIZ["options"], ERROR_QUIZ["answer"],
             explain=ERROR_QUIZ["explain"], feedback=ERROR_QUIZ["feedback"])
    if ctx.failed:
        ctx.stop()
    right = ctx.ask("你在 man ls 里查到的是哪个选项？（像 -F 这样写）",
                    expected=_option_is_right(ctx, task))
    if not right and ctx.last_answer.strip().lstrip("-").lower().endswith(task.lower()):
        ctx.note("选项字母的大小写要和说明书里写的一样：大写和小写是两个不同的选项。")
    if ctx.failed:
        ctx.note("任务和关键词写在 scenario 0.2b 打印的那几行里；忘了就再运行一次那条命令。")
        ctx.stop()
    first = facts["first"]
    right = ctx.ask("在 0.2b 文件夹里用这个选项运行 ls，排在最前面的是哪个文件？",
                    expected=[first, _strip_txt(first)])
    if not right:
        typed = _strip_txt(ctx.normalize(ctx.last_answer))
        if typed == _strip_txt(facts["plain_first"]):
            ctx.note("这是不加任何选项时排在最前面的文件。运行 ls 时要把选项也写上，中间隔一个空格。")
        else:
            ctx.note("先 cd 到 0.2b 文件夹（scenario 0.2b 打印的位置），再运行 ls 加上那个选项。")


ENTRANCE_SENTENCE = "我先不搬，帮我在 ~/Developer 建一个入口"
MOVE_SENTENCE = "帮我把课程安置到 ~/Developer"
README_CARD = "README.md 里的卡片「搬家后怎么找回导师」"


def _entrance_kind(ctx, workspace):
    """What is at ``~/Developer/fullstack-from-zero``, seen from this workspace.

    The same five kinds as the tool's ``App.entrance_kind`` (lesson modules
    import nothing from the tool): ``"workspace"`` (the moved folder),
    ``"link"`` (the entrance), ``"missing"``, ``"broken"`` (a link that leads
    nowhere or elsewhere) and ``"other"`` (a real folder that is not this
    workspace).
    """
    path = str(ctx.home / "Developer" / "fullstack-from-zero")
    if os.path.exists(path) and os.path.realpath(path) == str(workspace):
        return "link" if os.path.islink(path) else "workspace"
    if os.path.islink(path):
        return "broken"
    if os.path.lexists(path):
        return "other"
    return "missing"


def _doctor_group(ctx, synced, kind):
    """The letter of the doctor group that holds the workspace line right now.

    Mirrors ``doctor``: a synced workspace is always 需要处理; a workspace
    outside synced folders is 没问题, unless ``~/Developer/fullstack-from-zero`` does
    not lead to it although the learner has a ``workspace_location`` decision
    or has passed lesson 0.2 (then doctor names the missing entrance).
    """
    if synced is not None:
        return "B"
    done = all(ctx.passed(station) for station in ("0.2a", "0.2b", "0.2c"))
    if kind in ("missing", "broken") and (ctx.decision("workspace_location") is not None or done):
        return "B"
    return "A"


def _link_target(ctx, link):
    """Where a symbolic link points, as the learner reads it."""
    target = os.readlink(str(link))
    if not os.path.isabs(target):
        target = os.path.normpath(os.path.join(os.path.dirname(str(link)), target))
    return ctx.show(Path(target), entrance=False)


def _expect_entrance(ctx, kind):
    """``~/Developer/fullstack-from-zero`` must lead to the workspace (COMMON section 6)."""
    entrance = ctx.home / "Developer" / "fullstack-from-zero"
    if kind in ("workspace", "link"):
        ctx.ok("~/Developer/fullstack-from-zero 通到这个学习工作区，以后课文里的 cd ~/Developer/fullstack-from-zero 走得通")
        return True
    if kind == "missing":
        ctx.fail("~/Developer/fullstack-from-zero 这个入口还没有建", where="~/Developer",
                 saw="里面没有 fullstack-from-zero")
    elif kind == "broken":
        ctx.fail("~/Developer/fullstack-from-zero 是一个入口，但它没有通到这个学习工作区",
                 where="~/Developer/fullstack-from-zero",
                 saw="它指向 " + _link_target(ctx, entrance))
    else:
        ctx.fail("~/Developer/fullstack-from-zero 是另一个文件夹，不是通往这个学习工作区的入口",
                 where="~/Developer/fullstack-from-zero", saw="它不是这个学习工作区，也不是入口")
    ctx.note("对导师说“" + ENTRANCE_SENTENCE + "”，导师弄好以后再运行这个检查。")
    return False


def check_c(ctx):
    """~/Developer exists; the learner read doctor; ~/Developer/fullstack-from-zero leads here."""
    developer = ctx.need_dir("~/Developer", "主文件夹里的 Developer 文件夹")
    if _synced_folder(ctx, developer) is not None:
        ctx.fail("~/Developer 自己在同步盘里，代码放进去也会被同步",
                 where=ctx.show(developer), saw="它被云同步管着")
        ctx.stop()
    workspace = Path(os.path.realpath(str(ctx.workspace)))
    here = ctx.show(workspace, entrance=False)
    kind = _entrance_kind(ctx, workspace)
    new_copy = ctx.home / "Developer" / "fullstack-from-zero"
    if kind == "other" and (new_copy / "tools" / "course.py").is_file():
        ctx.fail("~/Developer/fullstack-from-zero 已经有一份课程，这次检查用的却是 " + here + " 那一份",
                 where=here, saw="检查是在旧的那一份里运行的")
        ctx.note("在新位置重新打开 Claude（" + README_CARD + "），在那里的终端里再运行这个检查。")
        ctx.stop()
    synced = _synced_folder(ctx, workspace)
    group = _doctor_group(ctx, synced, kind)
    ctx.quiz("现在运行一次 python3 tools/course.py doctor，找到「学习工作区的位置」那一行。它在哪一组？",
             ["没问题", "需要处理", "仅提示"], group,
             explain="每一组的标题都在那一组的最上面一行。",
             feedback={letter: ("从「学习工作区的位置」那一行往上找，遇到的第一个组标题就是它所在的组。"
                                "报告会跟着你的电脑变：看这一次运行的结果。")
                       for letter in "ABC" if letter != group})
    if ctx.failed:
        ctx.stop()
    if synced is None:
        if _expect_entrance(ctx, kind):
            ctx.ok("学习工作区在 " + here + "，不在同步盘里")
            ctx.decide("workspace_location", "not-synced")
        return
    if ctx.decision("workspace_location") == "stay-in-sync":
        ctx.ok("你在第 0.2 课决定先把学习工作区留在原处，这个决定已经记下")
        _expect_entrance(ctx, kind)
        return
    choice = ctx.choose(
        "学习工作区还在同步盘里（" + here + "）。你怎么决定？",
        [("move", "请导师帮我搬到 ~/Developer（还没搬）"),
         ("stay-in-sync", "先留在原处，我知道风险")],
        key="workspace_location",
        feedback={"B": ("第 1.12 课把学习工作区变成仓库之前，会再问你一次。"
                        "以后想搬，随时对导师说“" + MOVE_SENTENCE + "”。")})
    if choice == "move":
        ctx.fail("学习工作区还没有搬到 ~/Developer/fullstack-from-zero", where=here, saw="它还在同步盘里")
        ctx.note("对导师说“" + MOVE_SENTENCE + "”。搬好以后在新位置重新打开 Claude（"
                 + README_CARD + "），在那里运行这个检查。")
        ctx.stop()
    _expect_entrance(ctx, kind)


checks = {"0.2a": check_a, "0.2b": check_b, "0.2c": check_c}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "0.2a": [
        "相对路径是从起点算的。路径开头的 .. 是“先往上走一层”。先站到起点，再一段一段地走。",
        ("运行 python3 tools/course.py scenario 0.2a，它会再打印一次起点和相对路径。"
         "先 cd 到起点，用 pwd 确认；再 cd 加上那个相对路径；然后 ls。"),
        ("跟我做里的例子：站在 town/north 里运行 ls ../south，看到的是 south 里面的东西，"
         "也就是先回到 town，再进 south。south 的完整地址是 ~/Developer/playground/0.2-start/town/south。"),
        ("答案：cd 到起点，运行 cd 加上 scenario 给的相对路径（照抄，开头的 .. 不能少），再运行 ls，"
         "看到的那个文件名就是第一题的答案。第二题：在那里运行 pwd，把输出开头的 /Users/你的用户名 换成 ~，"
         "后面再加上 / 和文件名。\n"
         "解释：.. 把你带到起点的上一层，所以终点不在起点里面。pwd 打印的永远是绝对路径，"
         "用 ~ 代替主文件夹的那一段，写出来的地址在哪里用都一样。"),
    ],
    "0.2b": [
        "第一题看冒号前面的第一个词。后两题：说明书里每个选项都在行首，以短横线开头。",
        ("运行 man ls，按 / 键，输入 scenario 0.2b 给的英文关键词，按回车。"
         "关键词所在那一段的最左边，就是选项。看完按 q 退出。"),
        "跟我做里的例子：想让文件夹名后面带一个 /，搜 slash，找到 -F，然后运行 ls -F。",
        ("答案：第一题选 B，冒号前面是 ls。第二题：关键词 Sort by descending 对应 -t，"
         "Sort by size 对应 -S（大写的 S），Reverse 对应 -r。第三题：cd 到 0.2b 文件夹，"
         "运行 ls 加一个空格再加这个选项，看排在最前面的名字。\n"
         "解释：报错的格式是“程序: 对象: 出了什么问题”。说明书按选项字母排列，"
         "每个选项后面是一句英文说明；大写和小写是两个不同的选项。"),
    ],
    "0.2c": [
        ("这一站的检查看三件事：~/Developer 在不在；你会不会读 doctor 的分组；"
         "以后每一课开头的 cd ~/Developer/fullstack-from-zero 走不走得通。"),
        ("先运行 mkdir -p ~/Developer，再运行 python3 tools/course.py doctor，"
         "在报告里找「学习工作区的位置」那一行，从它往上找组标题。"
         "然后照「自己做」的 A 或 B 选一条路，对导师说那里写的那句话，导师做完再运行检查。"),
        "相似的例子：「~/Developer 文件夹：有。」这一行出现在「✅ 没问题」下面，它就属于第一组。",
        ("答案：运行 mkdir -p ~/Developer。第一题：重新运行 doctor，「学习工作区的位置」那一行上面最近的组标题是哪个就选哪个"
         "（在同步盘里的一定在「需要处理」）。学习工作区在同步盘里时：想搬，对导师说“帮我把课程安置到 ~/Developer”，"
         "搬好后在新位置重新打开 Claude（README.md 的卡片「搬家后怎么找回导师」），在那里运行检查；"
         "想先留着，对导师说“我先不搬，帮我在 ~/Developer 建一个入口”，建好以后运行检查，第二题选「先留在原处」。"
         "不在同步盘里、但不在 ~/Developer 的，也请导师建这个入口。\n"
         "解释：-p 让 mkdir 在文件夹已经存在时什么也不做、也不报错。"
         "同步盘会一个文件一个文件地改动和搬走代码，所以代码要放在不同步的 ~/Developer；"
         "后面每一课都写 cd ~/Developer/fullstack-from-zero，所以那里要么是学习工作区本身，要么是通向它的入口。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "0.2-paths", "type": "recall", "tier": "fluent", "station": "0.2a",
     "q": "在终端的路径里，~ 和 .. 各代表什么？",
     "a": "~ 是你的主文件夹（家）；.. 是上一级文件夹，也就是装着当前文件夹的那一个。"},
    {"id": "0.2-look-up", "type": "which", "tier": "lookup", "station": "0.2a",
     "q": "你站在 ~/Developer/playground 里，想看看 ~/Developer 里有什么，但不想离开现在的文件夹。用哪条？",
     "options": ["ls ..", "cd ..", "ls ."], "answer": "A",
     "explain": "ls 加路径只是看一眼，不会挪动你；cd 会把你带走；. 是当前文件夹本身。"},
    {"id": "0.2-full-width", "type": "fault", "tier": "fluent", "station": "0.2b",
     "q": "终端回了这一行，最可能是哪里出了问题？\n\n    zsh: command not found: cd　..",
     "options": ["这台电脑没有 cd 这个命令", "cd 和 .. 中间是一个全角空格", ".. 写错了，应该写成 ../"],
     "answer": "B",
     "explain": "zsh 把“cd　..”整个当成了一个命令名，说明中间那个空格不是普通空格。切到英文输入法重打一遍。"},
    {"id": "0.2-man-keys", "type": "recall", "tier": "lookup", "station": "0.2b",
     "q": "用 man 打开了一份说明书。怎么在里面找一个英文词？看完怎么退出？",
     "a": "按 / 再输入那个词，回车；按 n 找下一处。按 q 退出。"},
    {"id": "0.2-code-home", "type": "which", "tier": "fluent", "station": "0.2c", "rule": "WS-01",
     "q": "假设你的 Mac 打开了 iCloud 的“桌面与文稿”同步。新的代码项目 my-app 放在哪里最合适？",
     "options": ["~/Developer/my-app", "~/Desktop/my-app", "~/Documents/my-app"],
     "answer": "A", "shuffle": True,
     "explain": "桌面和文稿会被 iCloud 一个文件一个文件地同步，Git 官方 FAQ 说这会弄坏仓库。备份交给远程仓库。"},
    {"id": "0.2-naming", "type": "fault", "tier": "fluent", "station": "0.2c", "rule": "WS-02",
     "q": "按本课程的命名规则（WS-02），下面哪一个名字不合格？",
     "options": ["Study Notes", "study-notes", "README.md"], "answer": "A",
     "explain": "名字用小写英文、单词之间用短横线，不要空格和大写。README.md 是约定俗成的大写名字，属于例外。"},
]


# ---------------------------------------------------------------------------
# EXAM (gate-0)
# ---------------------------------------------------------------------------
def build_x1(sc):
    """Walk a relative route that starts with .., then write the file's full address.

    Both forms test the same two skills (follow ``..``; write an address from ~).
    A: one level up, one down.  B: one level up, two down.  Each has a decoy for
    the learner who skips the ``..``.
    """
    top, a, b, c, d = sc.words(5)
    target, decoy = sc.sample(THINGS, 2)
    target, decoy = target + ".txt", decoy + ".txt"
    if sc.form == "A":
        route, dest, wrong = f"../{c}", f"{top}/{a}/{c}", f"{top}/{a}/{b}/{c}"
    else:
        route, dest, wrong = f"../{c}/{d}", f"{top}/{a}/{c}/{d}", f"{top}/{a}/{b}/{c}/{d}"
    sc.write(f"{dest}/{target}", "就是这里。\n")
    sc.write(f"{wrong}/{decoy}", "不是这里。\n")
    sc.mkdir(f"{top}/{d}/{b}")
    sc.fact("start", f"{top}/{a}/{b}")
    sc.fact("route", route)
    sc.fact("target_rel", f"{dest}/{target}")


def grade_x1(ctx):
    info = ctx.scenario()
    ctx.ask("那个文件的完整地址是什么？（以 ~/ 开头，最后是文件名）",
            expected=_same_path(ctx, info.path / info.facts["target_rel"]))


SPOKEN = ["Fx Dashboard", "Study Plan", "Price Tracker", "Rate Notes", "Weekly Review", "Travel Budget"]


def build_x2(sc):
    """Create nested folders with one command, named by WS-02."""
    spoken = sc.pick(SPOKEN)
    kebab = spoken.lower().replace(" ", "-")
    base = "work-" + sc.word()
    inner = "notes/week-1" if sc.form == "A" else "drafts"
    sc.mkdir(base)
    sc.fact("base", base)
    sc.fact("spoken", spoken)
    sc.fact("kebab", kebab)
    sc.fact("inner", inner)


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    parent = info.path / facts["base"]
    names = ctx.listdir(parent, hidden=False)
    if facts["kebab"] not in names:
        def squash(name):            # "Weekly Review", "weekly_review", "WeeklyReview" -> "weeklyreview"
            return re.sub(r"[\s_\-]+", "", name.lower())
        odd = [name for name in names if squash(name) == squash(facts["kebab"])]
        if odd:
            ctx.fail("文件夹的名字还不符合命名规则", where=ctx.show(parent),
                     saw="现在叫「" + odd[0] + "」")
        else:
            ctx.fail("外层文件夹还没有建出来", where=ctx.show(parent),
                     saw="里面没有按题目要求命名的文件夹")
        ctx.stop()
    ctx.ok("外层文件夹的名字符合命名规则")
    folder = parent / facts["kebab"]
    for part in facts["inner"].split("/"):
        if part not in ctx.listdir(folder, hidden=False):
            ctx.fail("里面那几层文件夹还没有全部建出来", where=ctx.show(folder),
                     saw="缺少「" + part + "」")
            ctx.stop()
        folder = folder / part
    ctx.ok("每一层文件夹都在")


EXAM = [
    {
        "id": "0.2-x1",
        "gate": "gate-0",
        "title": "按相对路径找到文件，写出完整地址",
        "minutes": 5,
        "build": build_x1,
        "task": {
            "A": "从 {dir}/{start} 出发，按相对路径 {route} 走到一个文件夹，那里有一个文件。写出这个文件的完整地址：以 ~/ 开头，最后是文件名。",
            "B": "起点是 {dir}/{start}。照着相对路径 {route} 走，终点文件夹里只有一个文件。答出它的完整地址，从 ~/ 写起，包括文件名。",
        },
        "grade": grade_x1,
    },
    {
        "id": "0.2-x2",
        "gate": "gate-0",
        "title": "一条命令建好多层文件夹",
        "minutes": 4,
        "build": build_x2,
        "task": {
            "A": "在 {dir}/{base} 里建一个项目文件夹，项目叫「{spoken}」，名字按本课程的命名规则写；它里面还要有 {inner} 这两层。三层都要用一条命令建出来。",
            "B": "在 {dir}/{base} 里，用一条命令建出两层文件夹：外层是项目「{spoken}」，名字按本课程的命名规则写；里面一层叫 {inner}。这条命令再运行一次也不能报错。",
        },
        "grade": grade_x2,
    },
]
