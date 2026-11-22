"""Lesson 1.10 提交规范 (plan section 4): one commit, one thing; Conventional Commits.

Stations
    1.10a  一次提交只做一件事      COMMIT-02   check: artifact (scenario 1.10a)
    1.10b  写好提交说明            COMMIT-01   check: artifact (~/Developer/my-site) + 5 quiz items (找茬)

Scenarios
    start   the learner's site in state S5 (copy) and a small practice repository
            ``cafe`` whose history has one commit mixing three unrelated changes,
            plus three pending, unrelated changes for the worked steps
    1.10a   the independent exercise of station a: a seeded repository with two
            unrelated pending changes (one modified file, one new file)

Exam (gate-b)
    1.10-x1 split pending work into conventional commits and discard an accidental edit
    1.10-x2 find the commit that made a given change and name the one fault of its message
            (a second faulty message on the same file keeps the message from giving it away)

Standard library only; must import on Python 3.9.  Reference: docs/authoring/tool-api.md.
"""

import re
import unicodedata

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.10",
    "slug": "10-commit-conventions",
    "title": "提交规范",
    "stage": 1,
    "prerequisites": ["1.9"],
    "stations": [
        {
            "id": "1.10a",
            "title": "一次提交只做一件事",
            "minutes": 40,
            "new_concept": "一次提交只装一件完整的事（原子提交）",
            "new_commands": ["git show --stat"],
        },
        {
            "id": "1.10b",
            "title": "写好提交说明",
            "minutes": 40,
            "new_concept": "提交说明的第一行按约定式提交写成「类型(范围): 描述」",
            "new_commands": ["git commit -m … -m …"],
        },
    ],
    "rules": ["COMMIT-01", "COMMIT-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9"},
    },
    "unverified_steps": [
        "1.10b 跟我做第 2 步：在 dquote> 提示符下按 Ctrl+C 回到平常的提示符（建课环境没有终端设备；"
        "只核实了少打一个引号时交互式 zsh 会显示 dquote>，以及之后什么都没有提交）",
        "1.10b 自己做：在 VS Code 里改 my-site 的 index.html 和 style.css 并按 ⌘S 保存（编辑器操作沿用 1.4 课，"
        "对照 VS Code 文档；建课环境里没法点，模拟里用脚本改文件代替）；忘了 -m 时 Git 打开 1.6 课设好的 "
        "VS Code 标签页 COMMIT_EDITMSG，什么都不写就关掉会取消提交（沿用 1.6 课对照 GitHub Docs 的说法；"
        "“说明是空的就取消”在模拟环境里用一个不改文件的编辑器实测过）",
    ],
}

TERMS = [
    {"term": "原子提交", "en": "atomic commit",
     "plain": "一次提交只装一件完整的事，可以单独看懂、单独撤回", "first": "1.10a"},
    {"term": "约定式提交", "en": "Conventional Commits",
     "plain": "一份公开的提交说明写法规范，第一行写成「类型: 描述」", "first": "1.10b"},
    {"term": "类型", "en": "type",
     "plain": "提交说明开头的英文小词，说明这次是新功能、修复还是文档", "first": "1.10b"},
    {"term": "范围", "en": "scope",
     "plain": "类型后面圆括号里的词，说明改的是项目的哪一块", "first": "1.10b"},
    {"term": "正文", "en": "body",
     "plain": "提交说明第一行之后、空一行再写的详细说明，讲为什么这样改", "first": "1.10b"},
    {"term": "破坏性变更", "en": "breaking change",
     "plain": "会让别人原来的用法失效的改动，要在提交说明里特别标出来", "first": "1.10b"},
    {"term": "脚注", "en": "footer",
     "plain": "提交说明正文后面几行固定格式的附加信息，例如写明谁参与了这次改动", "first": "1.10b"},
]

# ---------------------------------------------------------------------------
# The commit-subject rule used by the checks (COMMIT-01)
# ---------------------------------------------------------------------------
# Conventional Commits 1.0.0 defines only feat and fix and allows other types.
# This course accepts the type list of @commitlint/config-conventional
# (checked 2026-11-19), in lower case, as that tool's default configuration does.
TYPES = ("build", "chore", "ci", "docs", "feat", "fix", "perf", "refactor",
         "revert", "style", "test")
_PREFIX = re.compile(r"^([A-Za-z]+)(\(([^()\s]+)\))?(!)?$")


def subject_problem(subject):
    """Return None when ``subject`` follows the course's reading of
    Conventional Commits 1.0.0, otherwise one short Chinese sentence that
    names the fault (never the corrected subject)."""
    text = (subject or "").strip()
    if not text:
        return "第一行是空的"
    half = text.find(":")
    full = text.find("：")
    if full != -1 and (half == -1 or full < half):
        return "类型后面的冒号是全角的「：」（中文输入法打出来的）"
    if half == -1:
        return "第一行里找不到类型后面的冒号"
    prefix, rest = text[:half], text[half + 1:]
    if not prefix:
        return "冒号前面还没有类型"
    match = _PREFIX.match(prefix)
    if not match:
        if " " in prefix or "　" in prefix:
            return "冒号前面只能是类型（可以带圆括号里的范围），中间不能有空格"
        if "（" in prefix or "）" in prefix:
            return "范围的圆括号是全角的"
        return "冒号前面应该只有一个英文类型（可以带圆括号里的范围）"
    kind = match.group(1)
    if kind.lower() not in TYPES:
        return "类型「{}」不在本课程认可的类型清单里".format(kind[:12])
    if kind != kind.lower():
        return "类型「{}」要全用小写字母".format(kind)
    if rest == "":
        return "冒号后面还没有描述"
    if rest.startswith("　"):
        return "冒号后面的空格是全角的"
    if not rest.startswith(" "):
        return "冒号后面少了一个空格"
    if rest.startswith("  "):
        return "冒号后面的空格多了：本课程要求只空一个"
    if not rest.strip():
        return "冒号后面还没有描述"
    return None


def _width(text):
    """Display width: a CJK or full-width character counts as two, the way
    Pro Git (zh) turns Git's 50 characters into about 25 汉字."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _visible(ctx, text, limit=30):
    """The subject as the learner should see it in 「看到了什么」.

    ctx.visible names full-width spaces, tabs and non-breaking spaces; the
    tool still prints a run of ASCII spaces as one space, so a doubled space
    is marked with one · per space here."""
    text = re.sub(r" {2,}", lambda m: "·" * len(m.group(0)), (text or "")[:limit])
    return ctx.visible(text)


def _saw(ctx, subject):
    shown = _visible(ctx, subject)
    if "·" in shown:
        return "现在是「{}」（一个 · 是一个空格）".format(shown)
    return "现在是「{}」".format(shown)


def _subject_notes(ctx, subject):
    """Neutral remarks that do not decide the outcome."""
    width = _width(subject)
    if width > 50:
        ctx.note("「{}…」折合约 {} 个字符宽（一个汉字算两个）。Git 手册建议第一行不超过 50 个字符，"
                 "《Pro Git》第 2 版中文版折算成约 25 个汉字：这是建议，不是要求。".format(subject[:10], width))
    if subject.endswith(".") or subject.endswith("。"):
        ctx.note("第一行末尾一般不加句号（常用的检查工具 commitlint 会拦英文句点）。")


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
CAFE_PAGE = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head><meta charset="utf-8"><title>湖边咖啡</title></head>
    <body>
      <h1>{title}</h1>
      <p>菜单见 menu.txt，营业时间和地址见 about.txt。</p>
    </body>
    </html>
"""
CAFE_README = """
    # 湖边咖啡的网页

    - index.html：首页
    - menu.txt：菜单
    - about.txt：营业时间和地址
"""


def build_start(sc):
    """The learner's site just before 1.10 (S5) and the worked-example repository.

    ``cafe`` is fixed (not seeded) so that the commands of 「跟我做」 can be
    typed exactly as printed; only hashes and dates differ.
    """
    sc.site_before()
    repo = "cafe"
    sc.git_init(repo)
    sc.write(repo + "/index.html", CAFE_PAGE.format(title="湖边咖啡"))
    sc.write(repo + "/menu.txt", """
        今日菜单
        美式咖啡 18 元
        拿铁 22 元
    """)
    sc.write(repo + "/about.txt", """
        关于湖边咖啡
        营业时间：每天 8:00-20:00
        地址：湖边路 12 号
    """)
    sc.git_commit(repo, "添加小店网页", date=sc.ago(days=3))
    # One commit that mixes three unrelated changes.
    sc.write(repo + "/index.html", CAFE_PAGE.format(title="湖边咖啡馆"))
    sc.write(repo + "/menu.txt", """
        今日菜单
        美式咖啡 18 元
        拿铁 24 元
    """)
    sc.write(repo + "/about.txt", """
        关于湖边咖啡
        营业时间：每天 7:30-20:00
        地址：湖边路 12 号
    """)
    sc.git_commit(repo, "更新", date=sc.ago(days=2))
    # Three pending, unrelated changes for the worked steps of both stations.
    sc.append(repo + "/menu.txt", "桂花拿铁 26 元\n")
    sc.write(repo + "/about.txt", """
        关于湖边咖啡
        营业时间：每天 7:30-20:00
        地址：湖边路 21 号
    """)
    sc.write(repo + "/README.md", CAFE_README)
    sc.fact("cafe", repo)
    sc.fact("cafe_commits", 2)
    sc.todo("网站的副本在这里（练习用，不是你真正的网站；第 2 站的提交做在你自己的 ~/Developer/my-site 里）："
            + sc.show(sc.facts["site"]))
    sc.todo("小店的练习仓库在这里：" + sc.show(repo))


# Station a, independent exercise: two unrelated pending changes.
TRIPS = [
    {"place": "杭州", "packing": ["雨伞", "充电宝", "身份证"], "extra": "防晒霜",
     "route": ["第一天：西湖边走一圈", "第二天：灵隐寺", "第三天：回家"]},
    {"place": "成都", "packing": ["薄外套", "充电宝", "身份证"], "extra": "常用药",
     "route": ["第一天：宽窄巷子", "第二天：熊猫基地", "第三天：回家"]},
    {"place": "青岛", "packing": ["泳衣", "充电宝", "身份证"], "extra": "拖鞋",
     "route": ["第一天：栈桥", "第二天：崂山", "第三天：回家"]},
]


def build_1_10a(sc):
    """A trip-planning repository with two unrelated, uncommitted changes:
    one tracked file modified (packing list), one new file (route)."""
    trip = sc.pick(TRIPS)
    repo = "trip-" + sc.word()
    sc.git_init(repo)
    sc.write(repo + "/packing.txt", "要带的东西\n" + "\n".join(trip["packing"]) + "\n", exact=True)
    sc.write(repo + "/budget.txt", "预算\n车票 300 元\n住宿 600 元\n", exact=True)
    sc.git_commit(repo, "开始计划去{}".format(trip["place"]), date=sc.ago(days=2))
    sc.write(repo + "/notes.txt", "出发前一天检查天气。\n", exact=True)
    sc.git_commit(repo, "加一条备忘", date=sc.ago(days=1))
    sc.append(repo + "/packing.txt", trip["extra"] + "\n")
    sc.write(repo + "/route.txt", "路线\n" + "\n".join(trip["route"]) + "\n", exact=True)
    sc.fact("repo", repo)
    sc.fact("commits", 2)
    sc.fact("extra", trip["extra"])
    sc.fact("route_line", trip["route"][0])
    sc.todo("进入练习仓库：cd " + sc.show(repo))
    sc.todo("里面有两处还没提交的改动，它们是两件不相干的事。")


SCENARIOS = {
    "start": build_start,
    "1.10a": build_1_10a,
}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _two_separate_commits(ctx, key="1.10a"):
    """Shared by the station check of 1.10a and the do review item."""
    info = ctx.scenario(key)
    name = info.facts["repo"]
    repo = ctx.need_repo(info.path / name, "练习仓库 " + name)
    before = info.facts["commits"]
    extra, route_line = info.facts["extra"], info.facts["route_line"]

    packing_now = repo.file_at("HEAD", "packing.txt") or ""
    packing_disk = ctx.read(repo.path / "packing.txt")
    route_now = repo.file_at("HEAD", "route.txt")
    route_disk = ctx.read(repo.path / "route.txt")

    lost = []
    if extra not in packing_now and extra not in packing_disk:
        lost.append("packing.txt 里新加的那一行")
    if route_now is None and route_line not in route_disk:
        lost.append("route.txt")
    if lost:
        ctx.fail("有一处原来的改动不见了，没法再分开提交",
                 where="工作区和最新提交", saw="找不到 " + "、".join(lost))
        ctx.note("重搭一份练习再做：python3 tools/course.py scenario 1.10a --reset 。"
                 "重搭以后仓库的名字会变，照新打印的 cd 那一行进去。")
        ctx.stop()

    count = repo.commit_count()
    new = count - before
    if new <= 0:
        ctx.fail("还没有新的提交", where="练习仓库的提交历史",
                 saw="还是开始时的 {} 个提交".format(count))
        ctx.stop()

    mixed = None
    touched = {"packing.txt": 0, "route.txt": 0}
    for commit in repo.commits(limit=new):
        paths = {path for _letter, path in repo.changed_files(commit.hash)}
        both = {"packing.txt", "route.txt"} <= paths
        if both and mixed is None:
            mixed = commit
        for path in touched:
            if path in paths:
                touched[path] += 1
    if mixed is not None:
        ctx.fail("两件不相干的改动进了同一个提交",
                 where="你新做的提交",
                 saw="提交「{}」同时改了 packing.txt 和 route.txt".format(_visible(ctx, mixed.subject, 20)))
        ctx.note("进了历史的提交，用学过的命令拆不开，也不用拆：重搭一份练习再做，"
                 "python3 tools/course.py scenario 1.10a --reset 。"
                 "重搭以后仓库的名字会变，照新打印的 cd 那一行进去。")
    committed_packing = extra in packing_now
    committed_route = route_now is not None and route_line in route_now
    if committed_packing and committed_route:
        if mixed is None:
            ctx.ok("两处改动分别进了不同的提交")
    else:
        waiting = [n for n, done in (("packing.txt", committed_packing),
                                     ("route.txt", committed_route)) if not done]
        ctx.fail("还有一处改动没有提交", where="最新的提交里的文件",
                 saw="里面还没有 " + "、".join(waiting) + " 的改动")
    if not ctx.failed:
        status = repo.status()
        if status.clean:
            ctx.ok("工作区是干净的，没有落下的改动")
        else:
            ctx.note("工作区里还有别的改动：{}。这一站不要求处理它们；如果它们是另一件事，就另开一个提交。"
                     .format("、".join(e.path for e in status.entries[:3])))
    return repo


def check_a(ctx):
    _two_separate_commits(ctx, "1.10a")


FIND_FAULT_OPTIONS = [
    "没有类型前缀",
    "冒号是全角的",
    "冒号后面少了空格",
    "类型不在本课程认可的清单里",
    "一条说明里有两件事",
]
# The five messages of the 找茬 exercise, in the order of lesson.md, with the
# letter of their one fault in FIND_FAULT_OPTIONS and, for every wrong letter,
# one true sentence that says why that option does not fit (never the answer).
FIND_FAULT = [
    ("docs： 补充 README 里的查看方法", "B", {
        "A": "冒号前面已经有类型 docs 了。",
        "C": "冒号后面有空格，毛病在冒号本身。",
        "D": "docs 在本课程认可的清单里。",
        "E": "描述只说了一件事。"}),
    ("修正首页标题的错别字", "A", {
        "B": "这一条里根本没有冒号。",
        "C": "这一条里根本没有冒号，谈不上冒号后面的空格。",
        "D": "这一条里找不到任何类型，谈不上类型对不对。",
        "E": "描述只说了一件事。"}),
    ("feat: 加上联系方式，顺便把背景改成浅灰色", "E", {
        "A": "冒号前面已经有类型 feat 了。",
        "B": "这里的冒号是英文半角的。",
        "C": "冒号后面有一个空格。",
        "D": "feat 在本课程认可的清单里。"}),
    ("fix:修正页脚链接的地址", "C", {
        "A": "冒号前面已经有类型 fix 了。",
        "B": "这里的冒号是英文半角的。",
        "D": "fix 在本课程认可的清单里。",
        "E": "描述只说了一件事。"}),
    ("update: 调整列表的内容", "D", {
        "A": "冒号前面有一个英文词，问题在这个词本身。",
        "B": "这里的冒号是英文半角的。",
        "C": "冒号后面有一个空格。",
        "E": "描述只说了一件事。"}),
]


# The subjects of 你的网站 made in lessons 1.6 to 1.9 (COMMON section 6, the state
# ladder): written before the rule, so they are not the learner's fault here.
BEFORE_RULE = ("第一版网页", "在 README 里写上用 Git 记录改动", "改了标题的颜色",
               "换了一个标题颜色", "添加 .gitignore")


def _type_of(subject):
    """The lower-case type of a subject that passed subject_problem."""
    return _PREFIX.match(subject.strip().split(":", 1)[0]).group(1).lower()


RECOVER_NOTE = ("写错的旧提交不用改，也不用撤回：再做一处改进，这次写对再提交。"
                "检查看的是：最新的提交合格，并且最近三个提交里有两个合格。")
LABELS = ("最新提交", "倒数第二个提交", "倒数第三个提交")


def check_b(ctx):
    """Passes when the newest subject of my-site follows the rule and at least
    two of the latest three do (the subjects of 1.6-1.9 do not, so this needs
    two new commits).  A learner who wrote one subject wrongly recovers without
    amend (stage 2): one more correct commit.  The number of commits is not
    checked: the learner's own site may have more than the course's five."""
    repo = ctx.need_repo(ctx.my_site, "你的网站文件夹 my-site")
    site = ctx.show(ctx.my_site)
    recent = repo.commits(limit=3)
    if not recent:
        ctx.fail("my-site 里还没有任何提交", where=site + " 的提交历史", saw="git log 是空的")
        ctx.stop()
    verdicts = [(label, commit, subject_problem(commit.subject))
                for label, commit in zip(LABELS, recent)]
    good = [(label, commit) for label, commit, problem in verdicts if problem is None]
    label, newest, problem = verdicts[0]
    subject_failed = False
    if not good and newest.subject.strip() in BEFORE_RULE:
        # Nothing new yet: the newest is a commit of 1.6-1.9, made before the rule.
        ctx.fail("还没有按约定式提交写的新提交", where=site + " 的提交历史",
                 saw="最新一个是「{}」（学这条规矩之前的，不用改）".format(_visible(ctx, newest.subject)))
        ctx.note("做两处改进，各提交一次，第一行按约定式提交写。"
                 "检查看的是：最新的提交合格，并且最近三个提交里有两个合格。")
        if repo.status().clean:
            ctx.note("如果你改过文件、提交时 Git 却说 nothing to commit，多半是文件还没保存："
                     "VS Code 标签页上有圆点，按 ⌘S 保存再提交。")
        else:
            ctx.note("my-site 里有改了还没提交的文件，git status 能看到它们：先 git add，再 git commit。")
        ctx.stop()
    if problem is not None:
        ctx.fail(problem, where="{} {}的第一行".format(site, label), saw=_saw(ctx, newest.subject))
        subject_failed = True
    elif len(good) < 2:
        # The newest is right; the most recent wrong one among the other two.
        label2, commit2, problem2 = next(v for v in verdicts[1:] if v[2] is not None)
        ctx.fail("最近三个提交里只有一个合格，要两个。这一条：{}".format(problem2),
                 where="{} {}的第一行".format(site, label2), saw=_saw(ctx, commit2.subject))
        subject_failed = True
    if subject_failed:
        ctx.note(RECOVER_NOTE)
        if repo.status().clean:
            ctx.note("如果你改过文件、提交时 Git 却说 nothing to commit，多半是文件还没保存："
                     "VS Code 标签页上有圆点，按 ⌘S 保存再提交。")
        else:
            ctx.note("my-site 里有改了还没提交的文件，git status 能看到它们：先 git add，再 git commit。")
    if ctx.failed:
        ctx.stop()
    for label, commit in good[:2]:
        ctx.ok("{}的第一行符合约定式提交：「{}」".format(label, _visible(ctx, commit.subject)))
        _subject_notes(ctx, commit.subject)
        paths = {path for _letter, path in repo.changed_files(commit.hash)}
        if _type_of(commit.subject) == "style" and paths & {"index.html", "style.css"}:
            ctx.note("style 指代码排版（空格、缩进），不是 CSS 样式；改了网页看起来的样子，本课程用 feat。")
        if {"index.html", "style.css"} <= paths:
            ctx.note("提交「{}」同时改了 index.html 和 style.css。如果那是两件事，下次分成两个提交。"
                     .format(_visible(ctx, commit.subject, 20)))
    status = repo.status()
    if not status.clean:
        ctx.note("my-site 里还有没提交的改动。属于另一件事的，另开一个提交。")
    for number, (message, answer, feedback) in enumerate(FIND_FAULT, 1):
        ctx.quiz("找茬第 {} 条的毛病是什么？\n\n    {}\n".format(number, message),
                 FIND_FAULT_OPTIONS, answer, feedback=feedback)


checks = {
    "1.10a": check_a,
    "1.10b": check_b,
}

# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.10a": [
        "两件不相干的事，要拍成两张快照。每次只往暂存区放一件事的文件，然后马上提交。",
        "先在练习仓库里运行 git status：它列出了两个文件，一个是 modified，一个在 Untracked files 下面。"
        "每个文件属于一件事。",
        "跟我做里的小店仓库就是这样做的：先 git add menu.txt 再 git commit，"
        "然后才 git add about.txt 再 git commit。中间用 git status 看一眼还剩什么。",
        "答案：先进入练习仓库（场景文件夹里面以 trip- 开头的那个文件夹，"
        "scenario 1.10a 打印的 cd 那一行就是），运行 git add packing.txt，再 git commit -m \"行李清单加一样东西\"；"
        "然后 git add route.txt，再 git commit -m \"写下路线\"。说明的文字可以不同。"
        "解释：每次只放一个文件进暂存区，提交就只装那一件事。"
        "以后想单独查看或撤回其中一件，不会牵连另一件。"
        "已经把两件事提交在一起了：回到学习工作区运行 python3 tools/course.py scenario 1.10a --reset，"
        "照新打印的 cd 那一行进去，重做一遍。",
    ],
    "1.10b": [
        "两处改进各提交一次；每次提交说明的第一行先写一个类型，再写冒号、空格和描述。",
        "提交说明的第一行要写成「类型: 描述」或「类型(范围): 描述」。"
        "对照课文第 2 站的类型清单，再看冒号是不是英文半角、后面有没有正好一个空格。"
        "在 ~/Developer/my-site 里运行 git log --oneline 看自己的提交。"
        "改了文件却提交不了，先看 VS Code 标签页上有没有圆点：有就是还没保存。",
        "相似的例子：给小店仓库加 README 时用的是 git commit -m \"docs: 添加小店的说明\"。"
        "网页上看得见的新变化（加一条内容、调大字号），本课程用 feat；改正一处错误用 fix；"
        "style 指的是代码排版（空格、缩进），不是 CSS 样式。"
        "写错了一条也不用改它：再做一处改进，这次写对。",
        "答案：先 cd ~/Developer/my-site。在 VS Code 里给 index.html 的列表加一行并保存，"
        "然后 git add index.html，git commit -m \"feat: 在首页加一条学习计划\"；"
        "再把 style.css 里 h1 的字号调大并保存，git add style.css，"
        "git commit -m \"feat: 调大标题的字号\"。最后 cd ~/Developer/fullstack-from-zero 再运行检查。"
        "找茬五条依次是：B 冒号是全角的、A 没有类型前缀、E 一条说明里有两件事、C 冒号后面少了空格、"
        "D 类型不在本课程认可的清单里。"
        "解释：类型告诉别人这次改动是哪一类，两件事分两个提交，冒号用英文半角并且后面跟一个空格。",
    ],
}

# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
def _review_split(ctx):
    _two_separate_commits(ctx, "1.10a")


REVIEW = [
    {"id": "1.10-r1", "type": "recall", "tier": "fluent", "station": "1.10a", "rule": "COMMIT-02",
     "q": "为什么一次提交只做一件事？说出一个具体的好处。",
     "a": "出了问题时能单独找到、看懂、撤回那一件事，不会牵连别的改动；说明也写得清楚。"},
    {"id": "1.10-f1", "type": "fault", "tier": "fluent", "station": "1.10b", "rule": "COMMIT-01",
     "q": "这条提交说明哪里不符合约定式提交？\n\n    docs： 补充安装说明",
     "options": ["冒号是全角的，要用英文半角", "类型要大写：Docs", "描述不能写中文"],
     "answer": "A", "shuffle": True,
     "explain": "冒号要用英文半角「:」，后面跟一个空格；描述用中文没问题，类型用小写。"},
    {"id": "1.10-w1", "type": "which", "tier": "fluent", "station": "1.10b", "rule": "COMMIT-01",
     "q": "给项目的 README.md 补了一段说明，提交说明的类型用哪个？",
     "options": ["feat", "fix", "docs"], "answer": "C",
     "explain": "只改文档用 docs。feat 是给用户加了新功能，fix 是修好一个错误。"},
    {"id": "1.10-w2", "type": "which", "tier": "lookup", "station": "1.10b", "rule": "COMMIT-01",
     "q": "Git 手册对「提交说明第一行不超过 50 个字符」是怎么说的？",
     "options": ["强制要求，超过就提交失败", "不是必须，但这是个好主意", "手册里没有提过"],
     "answer": "B",
     "explain": "git-commit 手册的 DISCUSSION 一节说：虽然不是必须的，但第一行最好不超过 50 个字符。"},
    {"id": "1.10-r2", "type": "recall", "tier": "lookup", "station": "1.10b", "rule": "COMMIT-01",
     "q": "约定式提交 1.0.0 规范本身定义了哪两个类型？docs、style 这些常用类型是从哪来的？",
     "a": "规范只定义了 feat 和 fix，并允许用别的类型。docs、style、refactor、test、chore 等来自 "
          "commitlint 这类工具的常用配置。"},
    {"id": "1.10-d1", "type": "do", "tier": "lookup", "station": "1.10a", "rule": "COMMIT-02",
     "q": "练习仓库里有两处不相干的、还没提交的改动。把它们分成两个提交，每个提交只装一件事。",
     "scenario": "1.10a", "check": _review_split},
]

# ---------------------------------------------------------------------------
# EXAM (gate-b)
# ---------------------------------------------------------------------------
# A hash in an answer: 7 to 40 hex characters standing alone, so that
# 「编号是 55b1138」 or a pasted `git log --oneline` row count, as in 1.7-x2.
HASH_WORD = re.compile(r"(?<![0-9a-z])[0-9a-f]{7,40}(?![0-9a-z])")
JUNK = ["asdfasdf", "测试测试 123", "<p>这一行是不小心粘进来的</p>", "zzzzzz"]
SHOP_ITEMS = ["抹茶拿铁 25 元", "热可可 20 元", "柠檬茶 16 元"]


def build_x1(sc):
    """Three pending changes: two real, unrelated ones and one accidental edit."""
    junk = sc.pick(JUNK)
    if sc.form == "A":
        repo = "shop-" + sc.word()
        sc.git_init(repo)
        sc.write(repo + "/index.html", "<h1>小店</h1>\n<p>欢迎光临。</p>\n", exact=True)
        sc.write(repo + "/menu.txt", "菜单\n美式咖啡 18 元\n", exact=True)
        sc.write(repo + "/about.txt", "关于小店\n营业时问：每天 9:00-18:00\n", exact=True)
        sc.git_commit(repo, "feat: 小店首页", date=sc.ago(days=1))
        item = sc.pick(SHOP_ITEMS)
        sc.append(repo + "/menu.txt", item + "\n")
        sc.write(repo + "/about.txt", "关于小店\n营业时间：每天 9:00-18:00\n", exact=True)
        sc.append(repo + "/index.html", junk + "\n")
        real = {"menu.txt": item, "about.txt": "营业时间"}
        junk_file, original = "index.html", "<h1>小店</h1>\n<p>欢迎光临。</p>\n"
    else:
        repo = "notes-" + sc.word()
        sc.git_init(repo)
        sc.write(repo + "/plan.txt", "本周计划\n读完第一章\n", exact=True)
        sc.write(repo + "/links.txt", "常用网址\nhttps://git-scm.com/book/zh/v2\n", exact=True)
        sc.git_commit(repo, "docs: 开始记笔记", date=sc.ago(days=1))
        task = sc.pick(["做完第一章的练习", "复习上周的笔记", "整理书签"])
        sc.append(repo + "/plan.txt", task + "\n")
        sc.write(repo + "/reading.txt", "读书清单\n《Pro Git》\n", exact=True)
        sc.append(repo + "/links.txt", junk + "\n")
        real = {"plan.txt": task, "reading.txt": "读书清单"}
        junk_file, original = "links.txt", "常用网址\nhttps://git-scm.com/book/zh/v2\n"
    sc.fact("repo", repo)
    sc.fact("commits", 1)
    sc.fact("real", real)
    sc.fact("junk_file", junk_file)
    sc.fact("original", original)
    sc.fact("junk", junk)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库")
    real = facts["real"]
    new = repo.commit_count() - facts["commits"]
    if new <= 0:
        ctx.fail("还没有新的提交", where="考试仓库的提交历史", saw="提交数没有增加")
        ctx.stop()
    for path, marker in sorted(real.items()):
        stored = repo.file_at("HEAD", path) or ""
        ctx.expect(marker in stored, path + " 的改动已经提交",
                   "有一处该提交的改动还没进入提交", where="最新的提交", saw=path + " 里没有这处改动")
    junk_file, junk = facts["junk_file"], facts["junk"]
    on_disk = ctx.read(repo.path / junk_file)
    commits = repo.commits(limit=new)
    # The accidental line must not reach history at all: also not in a commit
    # that a later commit cleaned up again.
    with_junk = [c for c in commits if junk in (repo.file_at(c.hash, junk_file) or "")]
    if with_junk:
        ctx.fail("不小心加的内容进了提交（以后再删掉，那个提交里也还在）",
                 where="你新做的提交里的 " + junk_file,
                 saw="提交「{}」里有那一行".format(_visible(ctx, with_junk[-1].subject, 20)))
    else:
        ctx.ok("不小心加的那一行没有进入任何新提交")
    ctx.expect(junk not in on_disk, "不小心加的那一行已经去掉",
               "工作区里还留着不小心加的内容", where="工作区的 " + junk_file, saw="那一行还在")
    for commit in commits:
        paths = {path for _letter, path in repo.changed_files(commit.hash)}
        if set(real) <= paths:
            ctx.fail("两件不相干的改动进了同一个提交", where="你新做的提交",
                     saw="「{}」同时改了两处".format(_visible(ctx, commit.subject, 20)))
        elif junk_file in paths and paths & set(real):
            ctx.fail("不小心改的文件和一处真正的改动进了同一个提交", where="你新做的提交",
                     saw="「{}」同时改了 {} 和 {}".format(_visible(ctx, commit.subject, 20), junk_file,
                                                      "、".join(sorted(paths & set(real)))))
        problem = subject_problem(commit.subject)
        if problem is not None:
            ctx.fail(problem, where="提交「{}」的第一行".format(_visible(ctx, commit.subject, 20)),
                     saw="不符合约定式提交")
    if not ctx.failed:
        ctx.ok("新提交的说明都符合约定式提交")
    ctx.expect(repo.is_clean(), "git status 是干净的", "还有改动没有处理",
               where="git status", saw="不是 nothing to commit")


# x2: find the commit that made a change, name the fault of its message.
# Two commits in the history have a faulty first line, each with a different
# fault, and both change the same file: only the change itself tells which
# one is meant (the message alone does not give the target away).
X2_LETTERS = ("A", "B", "C", "D")
X2_FAULT_OPTIONS = ["没有类型前缀", "冒号是全角的", "冒号后面少了空格", "类型不在本课程认可的清单里",
                    "这条说明没有毛病"]
_X2_WRONG_TYPE = {"fix": "change", "feat": "add", "docs": "update"}


def _x2_subject(letter, kind, desc):
    """A first line with exactly the one fault ``letter`` of X2_FAULT_OPTIONS."""
    if letter == "A":
        return desc
    if letter == "B":
        return kind + "\uff1a " + desc          # full-width colon, then a space
    if letter == "C":
        return kind + ":" + desc
    return _X2_WRONG_TYPE[kind] + ": " + desc


def build_x2(sc):
    """Five commits; one in the middle made the asked-for change under a faulty
    message, and a later commit to the same file has a different fault."""
    letter = sc.pick(X2_LETTERS)
    decoy = sc.pick([l for l in X2_LETTERS if l != letter])
    if sc.form == "A":
        repo = "menu-" + sc.word()
        item, old, new = sc.pick([("拿铁", "22", "24"), ("美式咖啡", "18", "20"), ("摩卡", "26", "28")])
        lines = ["今日菜单", "拿铁 22 元", "美式咖啡 18 元", "摩卡 26 元"]
        sc.git_init(repo)
        sc.write(repo + "/menu.txt", "\n".join(lines) + "\n", exact=True)
        sc.write(repo + "/about.txt", "关于小店\n营业时间：每天 9:00-18:00\n", exact=True)
        sc.git_commit(repo, "feat: 添加菜单", date=sc.ago(days=5))
        lines.append("热可可 20 元")
        sc.write(repo + "/menu.txt", "\n".join(lines) + "\n", exact=True)
        sc.git_commit(repo, "feat(menu): 加上热可可", date=sc.ago(days=4))
        changed = ["{} {} 元".format(item, new) if l == "{} {} 元".format(item, old) else l for l in lines]
        sc.write(repo + "/menu.txt", "\n".join(changed) + "\n", exact=True)
        target = sc.git_commit(repo, _x2_subject(letter, "fix", "调整价格"), date=sc.ago(days=3))
        sc.write(repo + "/about.txt", "关于小店\n营业时间：每天 8:30-18:00\n", exact=True)
        sc.git_commit(repo, "fix(about): 改正开门时间", date=sc.ago(days=2))
        changed.append("柠檬茶 16 元")
        sc.write(repo + "/menu.txt", "\n".join(changed) + "\n", exact=True)
        sc.git_commit(repo, _x2_subject(decoy, "feat", "加上柠檬茶"), date=sc.ago(days=1))
        sc.fact("what", "{}从 {} 元改成 {} 元".format(item, old, new))
    else:
        repo = "plan-" + sc.word()
        gone = sc.pick(["周三去图书馆", "周四练习打字", "周五整理书桌"])
        lines = ["这周的安排", "周一复习 Git", "周二读一章书", "周三去图书馆", "周四练习打字", "周五整理书桌"]
        sc.git_init(repo)
        sc.write(repo + "/week.txt", "\n".join(lines) + "\n", exact=True)
        sc.write(repo + "/README.md", "# 学习计划\n", exact=True)
        sc.git_commit(repo, "docs: 写下这周的安排", date=sc.ago(days=5))
        sc.write(repo + "/README.md", "# 学习计划\n\n每周一更新。\n", exact=True)
        sc.git_commit(repo, "docs: 说明多久更新一次", date=sc.ago(days=4))
        kept = [l for l in lines if l != gone]
        sc.write(repo + "/week.txt", "\n".join(kept) + "\n", exact=True)
        target = sc.git_commit(repo, _x2_subject(letter, "docs", "删掉一项安排"), date=sc.ago(days=3))
        kept.append("周六休息")
        sc.write(repo + "/week.txt", "\n".join(kept) + "\n", exact=True)
        sc.git_commit(repo, _x2_subject(decoy, "docs", "周六休息"), date=sc.ago(days=2))
        sc.write(repo + "/README.md", "# 学习计划\n\n每周一更新，周日复盘。\n", exact=True)
        sc.git_commit(repo, "docs: 加上周日复盘", date=sc.ago(days=1))
        sc.fact("what", "删掉了「{}」这一项".format(gone))
    sc.fact("repo", repo)
    sc.fact("target", target)
    sc.fact("letter", letter)


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库")
    target = facts["target"]
    if repo.commit(target) is None:
        raise RuntimeError("the exam repository lost the target commit")
    ctx.ask("做出这处改动（{}）的提交，编号的前 7 位是什么？".format(facts["what"]),
            expected=lambda typed: bool(HASH_WORD.findall(typed))
            and all(target.startswith(w) for w in HASH_WORD.findall(typed)))
    ctx.quiz("这个提交的说明（第一行）有什么毛病？", X2_FAULT_OPTIONS, facts["letter"])


EXAM = [
    {
        "id": "1.10-x1",
        "gate": "gate-b",
        "title": "把混在一起的改动整理成规范的提交",
        "minutes": 10,
        "build": build_x1,
        "task": {
            "A": "仓库 {dir}/{repo} 里有三处还没提交的改动。其中一处是不小心粘进去的内容，要丢掉；"
                 "另外两处是两件不相干的事，各提交一次，提交说明用约定式提交。做完以后 git status 要是干净的。",
            "B": "进入 {dir}/{repo}：先弄清楚每个文件改了什么。不小心加进去的那一行要去掉，不能进历史；"
                 "其余两处改动分成两个提交，第一行都按约定式提交来写。最后工作区要是干净的。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.10-x2",
        "gate": "gate-b",
        "title": "在历史里找到一处改动并挑出说明的毛病",
        "minutes": 6,
        "build": build_x2,
        "task": {
            "A": "仓库 {dir}/{repo} 有 5 个提交。找出把{what}的那个提交，记下它编号的前 7 位，"
                 "再看它的提交说明符不符合约定式提交。评分时会问你这两件事。",
            "B": "看一看 {dir}/{repo} 的历史：在哪个提交里{what}？记下那个提交编号的前 7 位，"
                 "并判断它的第一行有什么毛病。评分时要回答这两个问题。",
        },
        "grade": grade_x2,
    },
]
