"""Worked example of a lesson module (plan I3), for lesson authors.

This is NOT a lesson of the course.  It is an invented two-station lesson that
uses every part of the lesson-facing API once:

- an artifact check, an ask check and a quiz check
- four-level hints
- three kinds of review item (recall, which, do)
- a ``start`` scenario with seeded, randomised content
- one exam task in two parallel forms

To try it, copy this folder into a workspace as

    stages/99-example/01-notes-repo/

(the folder names matter: ``validate`` compares them with META) and run

    python3 tools/course.py validate 99.1 --build
    python3 tools/course.py scenario 99.1
    python3 tools/course.py check 99.1a

A lesson module is plain Python, standard library only, and must run on
Python 3.9.  It imports nothing from the tool: every helper arrives through
the context objects ``ctx`` (checks, grading) and ``sc`` (scenario builders).
All text a learner can see is plain Chinese.  The reference is
docs/authoring/tool-api.md.
"""

# ---------------------------------------------------------------------------
# META and TERMS: data only
# ---------------------------------------------------------------------------
META = {
    "id": "99.1",
    "slug": "01-notes-repo",              # exactly the name of the lesson folder
    "title": "示例课：给练习仓库加一份说明",
    "stage": 99,
    "prerequisites": [],
    "stations": [
        {
            "id": "99.1a",
            "title": "提交是什么",
            "minutes": 15,
            "new_concept": "提交是给项目拍的一张带说明的快照",
            "new_commands": ["git log --oneline"],
        },
        {
            "id": "99.1b",
            "title": "加一份说明并提交",
            "minutes": 20,
            "new_concept": "改动要先放进暂存区，再提交",
            "new_commands": ["git add", "git commit -m"],
        },
    ],
    "rules": ["EX-01"],                   # each needs a card in rules.md
    "verified": {"date": "2026-11-19", "tools": {"git": "2.54.0", "python3": "3.14.9"}},
    "unverified_steps": [],
}

TERMS = [
    {"term": "提交", "en": "commit", "plain": "给项目当前的样子拍一张带说明的快照", "first": "99.1a"},
    {"term": "暂存区", "en": "staging area", "plain": "提交之前，放“这一次要拍进快照的改动”的地方",
     "first": "99.1b"},
]


# ---------------------------------------------------------------------------
# SCENARIOS: builders create practice states under the playground
# ---------------------------------------------------------------------------
SUBJECTS = [
    "docs: 记下周一的想法",
    "docs: 补充读书笔记",
    "docs: 整理待办清单",
    "docs: 记录一次排错",
    "docs: 写下本周计划",
]


def build_start(sc):
    """The state just before this lesson: a small notes repository.

    Names and the number of commits depend on ``sc.seed``, so two learners
    (or two attempts) get different answers.  Whatever a check needs to know
    later is recorded with ``sc.fact``.
    """
    repo = "notes-" + sc.word()                  # e.g. notes-cedar
    count = sc.randint(2, 4)
    subjects = sc.sample(SUBJECTS, count)
    sc.git_init(repo)                            # always a sub-folder, never "."
    for number, subject in enumerate(subjects, 1):
        sc.write(f"{repo}/day-{number}.txt", f"""
            第 {number} 天的笔记
            今天学了一点 Git。
        """)
        sc.git_commit(repo, subject, date=sc.ago(days=count - number + 1))
    sc.fact("repo", repo)
    sc.fact("commits", count)
    where = sc.show(repo)                        # ~/Developer/playground/99.1-start/notes-cedar
    sc.todo(f"练习仓库在这里：{where}")
    sc.todo(f"先进去看一看：cd {where}，然后运行 git log --oneline")


SCENARIOS = {
    "start": build_start,
}


# ---------------------------------------------------------------------------
# checks: one function per station
# ---------------------------------------------------------------------------
def check_a(ctx):
    """Concept station: an auto-graded quiz.  Every question must be right."""
    ctx.quiz(
        "下面哪一句最接近“提交”的意思？",
        [
            "把文件上传到网上",
            "给项目当前的样子拍一张带说明的快照",
            "把文件复制一份改个名字",
        ],
        "B",
        explain="提交只发生在你自己的电脑上；传到网上是另一步，后面的课才学。",
        feedback={
            "A": "提交不需要联网，它只在你自己的电脑上发生。",
            "C": "复制改名留不下“为什么改”的说明，也没法一条命令回到过去。",
        },
    )
    ctx.quiz(
        "git log --oneline 的每一行代表什么？",
        ["一个文件", "一次提交", "一个文件夹"],
        "B",
    )


def _readme_is_committed(ctx):
    """Artifact part shared by the station check and the ``do`` review item.

    It finds the practice state through ``ctx.scenario``: in a station check
    that is the learner's ``start`` scenario; in a review it is the fresh copy
    the tool built for the review item.  Never build paths by hand.
    """
    sc = ctx.scenario("start")
    name = sc.facts["repo"]
    repo = ctx.need_repo(sc.path / name, f"练习仓库 {name}")

    readme = repo.path / "README.md"
    if ctx.expect_file(readme, "练习仓库里的 README.md"):
        first = (ctx.lines(readme) or [""])[0]
        if first.startswith("# ") and first[2:].strip():
            ctx.ok("README.md 的第一行是一级标题")
        else:
            ctx.fail("第一行要是一个一级标题",
                     where="README.md 的第一行", saw=f"第一行现在是「{first[:30]}」")

    before = sc.facts["commits"]
    now = repo.commit_count()
    if now > before:
        ctx.ok(f"提交历史比开始时多了 {now - before} 个提交")
    else:
        ctx.fail("还没有新的提交",
                 where="练习仓库的提交历史", saw=f"和开始时一样，还是 {now} 个提交")

    status = repo.status()
    if not status.clean:
        ctx.fail("还有改动没有进入提交",
                 where="练习仓库现在的状态", saw=f"有 {len(status.entries)} 个文件的改动还没提交")
    elif now > before:
        # Only an achievement once there is work: an untouched practice
        # repository is clean too, and "已经做到" must not praise nothing.
        ctx.ok("没有落下还没提交的改动")
    return sc


def check_b(ctx):
    """Hands-on station: inspect the work (artifact), then ask one question."""
    sc = _readme_is_committed(ctx)
    if ctx.failed:
        ctx.stop()          # do not ask before the work is there
    # The answer can only be read off the learner's own screen, and it differs
    # from seed to seed: it is computed from the facts of the scenario.
    ctx.ask("运行 git log --oneline 数一数：在你动手之前，这个仓库里已经有几个提交？",
            expected=sc.facts["commits"])
    ctx.note("数的时候别忘了去掉你自己刚做的那一个。")


checks = {
    "99.1a": check_a,
    "99.1b": check_b,
}


# ---------------------------------------------------------------------------
# HINTS: exactly four per station: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "99.1a": [
        "回想课文里的类比：提交像什么？它留下了哪两样东西？",
        "重读第 1 站“概念”一节的第二段，注意“快照”和“说明”这两个词。",
        "游戏存档是相似的例子：存档记下那一刻的全部进度，而且可以给存档起名字。",
        ("第一题选 B：提交是带说明的快照，只发生在你自己的电脑上。"
         "第二题选 B：git log --oneline 一行就是一次提交，左边是编号，右边是说明。"),
    ],
    "99.1b": [
        "一共三件事：写文件、把它放进暂存区、提交。检查结果里“还缺什么”会告诉你差哪一件。",
        "先确认你在练习仓库里面：运行 pwd，路径要以 notes- 开头的文件夹结尾。再运行 git status 看文件是什么状态。",
        "相似的例子：要提交一个叫 todo.txt 的新文件，先 git add todo.txt，再 git commit -m \"docs: 添加待办\"。",
        ("答案：在练习仓库里新建 README.md，第一行写“# 我的笔记”，保存；"
         "运行 git add README.md，再运行 git commit -m \"docs: 添加说明\"。"
         "解释：git add 把改动放进暂存区，git commit 把暂存区里的内容拍成快照。"
         "最后的问答题：git log --oneline 的行数减 1，就是你动手之前的提交数。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW: spaced-review items.  Only tier "fluent" is scheduled.
# ---------------------------------------------------------------------------
REVIEW = [
    {
        "id": "99.1-r1",
        "type": "recall",                 # self-graded after the answer is revealed
        "tier": "fluent",
        "station": "99.1b",
        "q": "提交之前，改动要先放到哪里？说出为什么要有这一步。",
        "a": "先放进暂存区（git add）。这样可以挑出这一次提交要包含的改动，而不是把手头所有改动一起提交。",
    },
    {
        "id": "99.1-r2",
        "type": "which",                  # auto-graded multiple choice
        "tier": "fluent",
        "station": "99.1a",
        "q": "只想看每个提交一行的简短历史，用哪条命令？",
        "options": ["git status", "git log --oneline", "git add ."],
        "answer": "B",
        "explain": "git status 看的是现在的状态，git log 看的是历史。",
    },
    {
        "id": "99.1-r3",
        "type": "do",                     # builds a scenario, graded by its check
        "tier": "lookup",
        "station": "99.1b",
        "rule": "EX-01",
        "q": "在练习仓库里新建 README.md（第一行是一级标题）并提交。",
        "scenario": "start",
        "check": _readme_is_committed,
    },
]


# ---------------------------------------------------------------------------
# EXAM: cold tasks for a gate, each in two parallel forms
# ---------------------------------------------------------------------------
PAGE = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head><meta charset="utf-8"><title>练习页</title></head>
    <body><h1>旧标题</h1></body>
    </html>
"""


def build_x1(sc):
    """One repository; form A adds a file, form B edits one.  Same skill."""
    repo = "site-" + sc.word()
    sc.git_init(repo)
    sc.write(repo + "/index.html", PAGE)
    sc.git_commit(repo, "feat: 添加首页")
    sc.fact("repo", repo)
    sc.fact("commits", 1)
    if sc.form == "A":
        sc.fact("file", sc.pick(["about.txt", "links.txt", "contact.txt"]))
    else:
        sc.fact("title", sc.pick(["我的第一个网页", "学习笔记", "周末计划"]))


def grade_x1(ctx):
    sc = ctx.scenario()                   # the task that was built for this exam
    name = sc.facts["repo"]
    repo = ctx.need_repo(sc.path / name, f"考试仓库 {name}")
    if sc.form == "A":
        if repo.file_at("HEAD", sc.facts["file"]) is not None:
            ctx.ok("新文件已经在最新的提交里")
        else:
            ctx.fail("要求的新文件还没有进入提交",
                     where="最新提交里的文件", saw="没有找到题目要求的那个文件名")
    else:
        page = repo.file_at("HEAD", "index.html") or ""
        if sc.facts["title"] in page:
            ctx.ok("新标题已经在最新的提交里")
        else:
            ctx.fail("改过的标题还没有进入提交",
                     where="最新提交里的 index.html", saw="里面没有题目要求的标题文字")
    if repo.commit_count() > sc.facts["commits"]:
        ctx.ok("有新的提交")
    else:
        ctx.fail("还没有新的提交", where="考试仓库的提交历史", saw="提交数没有增加")
    # ctx.expect is the one-line form of "if ...: ctx.ok(...) else: ctx.fail(...)".
    ctx.expect(repo.is_clean(), "没有落下还没提交的改动",
               "还有改动没有进入提交", where="考试仓库现在的状态", saw="有没提交的改动")


EXAM = [
    {
        "id": "99.1-x1",
        "gate": "gate-example",           # real lessons use the gate of plan section 4
        "title": "做一处改动并提交",
        "minutes": 5,
        "build": build_x1,
        "task": {
            "A": "仓库在 {dir}/{repo}。在里面新建文件 {file}，写一行字，然后提交。",
            "B": "仓库在 {dir}/{repo}。把 index.html 里的标题改成“{title}”，然后提交。",
        },
        "grade": grade_x1,
    },
]
