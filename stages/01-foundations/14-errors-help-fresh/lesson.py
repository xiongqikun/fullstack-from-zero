"""Lesson 1.14: 排错、求助与“与时俱进”.

Stations:
  1.14a  排错实验室: five small broken situations in one scenario folder,
         one check that looks at four of them and asks one question.
         The plan row (section 4) names eight situations; three of them
         (not a repository, an ignored path, stuck in vi) are review items
         instead, so that the station fits its calculated 40 minutes (G5a).
  1.14b  怎么求助: a minimal reproduction and a five-part question file.
  1.14c  判断一份资料是否过时: a quiz on three short tutorial snippets.

Standard library only, Python 3.9 syntax.  Reference: docs/authoring/tool-api.md.
"""

import re
import textwrap

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.14",
    "slug": "14-errors-help-fresh",
    "title": "排错、求助与“与时俱进”",
    "stage": 1,
    "prerequisites": ["1.13"],
    "stations": [
        {
            "id": "1.14a",
            "title": "排错实验室",
            "minutes": 40,
            "new_concept": "报错是线索：先自己用报错三问把报错对上原因",
            "new_commands": [],
        },
        {
            "id": "1.14b",
            "title": "怎么求助",
            "minutes": 40,
            "new_concept": "最小可复现示例和五段式提问",
            "new_commands": ["git <命令> -h", "sw_vers -productVersion"],
        },
        {
            "id": "1.14c",
            "title": "判断一份资料是否过时",
            "minutes": 35,
            "new_concept": "资料三查：日期、版本、官方现在怎么说",
            "new_commands": ["python3 tools/course.py fresh"],
        },
    ],
    "rules": ["HELP-01", "FRESH-01"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9",
                  "gh": "2.105.0", "vi": "9.1"},
    },
    "unverified_steps": [
        "1.14a 情况 5：在 dquote> 提示符下按 Ctrl+C 回到普通提示符（建课环境没有真终端，只验证了 dquote> 会出现）",
        "1.14b 用 VS Code 打开练习场景文件夹、编辑并保存 question.md（图形界面）",
        "1.14c 补全：git-scm.com 文档页顶上的 Latest version 菜单（网页内容在 2026-11-20 核对过，界面可能不同）",
        "1.14c 想多了解：Git、VS Code、GitHub 的发布说明页在浏览器里的样子（网址和内容在 2026-11-20 核对过，界面可能不同）",
    ],
}

TERMS = [
    {"term": "续行提示符", "en": "continuation prompt",
     "plain": "一行命令还没输完整时，终端显示的等待提示，比如 dquote>", "first": "1.14a"},
    {"term": "最小可复现示例", "en": "minimal reproducible example",
     "plain": "去掉一切无关的东西以后，还能让同一个问题再出现一次的最少步骤", "first": "1.14b"},
    {"term": "发布说明", "en": "release notes",
     "plain": "软件每出一个新版本，官方写的“这次改了什么”", "first": "1.14c"},
    {"term": "基线", "en": "baseline",
     "plain": "课程记下的、核对课文时各个工具的版本表", "first": "1.14c"},
    {"term": "弃用", "en": "deprecated",
     "plain": "官方说这个做法以后会去掉，现在还能用，但不该再新学它", "first": "1.14c"},
    {"term": "知识截止日期", "en": "knowledge cutoff",
     "plain": "AI 学习的资料截止到哪一天；那以后的变化它不知道，只能去查", "first": "1.14c"},
]


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
NOTES_TOPICS = ["买一盏台灯", "周五交周报", "约牙医复诊", "给网页换配色", "整理书架", "报名游泳课"]


def build_start(sc):
    """The state just before 1.14: the website copy in state S7 (after 1.13)."""
    sc.site_before()
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))


def build_lab(sc):
    """Station 1.14a: five small broken situations, one folder each."""
    # 1. wrong folder: the file sits one level further down.
    word1 = sc.word()
    sc.write("1-wrong-folder/docs/notes.txt", f"""
        会议记录
        下次讨论：{word1}
    """)
    sc.fact("s1_text", f"会议记录\n下次讨论：{word1}\n")

    # 2. misspelt command: a folder that should become a repository.
    sc.write("2-typo/diary/day-1.txt", "今天开始写日记。")

    # 3. nothing staged: a tracked file was changed but not added.
    sc.git_init("3-nothing-staged/notes")
    sc.write("3-nothing-staged/notes/plan.md", """
        # 本周计划

        - 复习第 1.13 课
    """)
    sc.git_commit("3-nothing-staged/notes", "docs: 本周计划", date=sc.ago(days=1))
    task = "- " + sc.pick(NOTES_TOPICS)
    sc.append("3-nothing-staged/notes/plan.md", task + "\n")
    sc.fact("s3_line", task)
    sc.fact("s3_commits", 1)

    # 4. full-width character: a hidden file that ls -a would show.
    hidden = ".memo-" + sc.word()
    sc.write("4-full-width/" + hidden, "这是一个隐藏文件。")
    sc.write("4-full-width/readme.txt", "这个文件夹里还有一个隐藏文件。")
    sc.fact("s4_hidden", hidden)

    # 5. unclosed quote: a file name with a space, to be renamed.
    word5 = sc.word()
    sc.write("5-quote/my notes.txt", f"这份笔记的暗号是 {word5}。")
    sc.fact("s5_text", f"这份笔记的暗号是 {word5}。\n")

    sc.todo("五个坏掉的情况在这里，一个文件夹一个：" + sc.show("."))


BIG_FILES = ["index.html", "style.css", "about.html", "contact.html", "README.md",
             "notes/day-1.md", "notes/day-2.md", "notes/day-3.md", "images/logo.txt",
             "data/prices.csv", "data/hours.csv", "todo.md"]

QUESTION_SKELETON = """
    # 提问：……（用一句话写清楚问题）

    ## 目标
    （我想做成什么）

    ## 我做了什么
    （从一个空文件夹开始，每一步命令原样写出来）

    ## 我期望什么
    （我以为会发生什么）

    ## 实际看到什么
    （报错原文，原样粘贴，不改写、不截图）

    ## 版本
    （和问题有关的程序的版本，加上 macOS 版本）
"""

# Station 1.14b: the goal and the expectation are written in advance, so the
# learner spends the station on the reproduction, the error and the versions.
STATION_SKELETON = """
    # 提问：……（用一句话写清楚问题）

    ## 目标
    在一个还没有任何提交的新仓库里，把一个已经 git add 过的文件从暂存区拿出来。

    ## 我做了什么
    （从一个空文件夹开始，每一步命令原样写出来）

    ## 我期望什么
    这个文件离开暂存区，回到“未跟踪”（git status 里出现在 Untracked files 下面）。

    ## 实际看到什么
    （报错原文，原样粘贴，不改写、不截图）

    ## 版本
    （和问题有关的程序的版本，加上 macOS 版本）
"""


def _build_big_project(sc, folder):
    """A brand-new repository: many files, all staged, no commit yet."""
    sc.git_init(folder)
    for name in BIG_FILES:
        sc.write(f"{folder}/{name}", f"{name} 的内容")
    sc.git(folder, "add", "-A")


def build_help(sc):
    """Station 1.14b: a big project with a puzzling error, and a question skeleton."""
    _build_big_project(sc, "big-project")
    sc.write("question.md", STATION_SKELETON)
    sc.todo("一个刚建好、还没有提交的大项目：" + sc.show("big-project"))
    sc.todo("提问的骨架：" + sc.show("question.md"))


SCENARIOS = {
    "start": build_start,
    "1.14a": build_lab,
    "1.14b": build_help,
}


# ---------------------------------------------------------------------------
# Station 1.14a: the five situations
# ---------------------------------------------------------------------------
def _lab_artifacts(ctx, info):
    """Situations 1, 2, 3 and 5 leave something to look at; returns how many are done."""
    root = info.path
    done = 0

    # 1. wrong folder
    backup = root / "1-wrong-folder/docs/notes-backup.txt"
    if not ctx.is_file(backup):
        elsewhere = [p for p in ("1-wrong-folder/notes-backup.txt", "notes-backup.txt")
                     if ctx.is_file(root / p)]
        ctx.fail("情况 1：docs 里还没有 notes-backup.txt",
                 where=ctx.show(root / "1-wrong-folder/docs"),
                 saw=("notes-backup.txt 在别的文件夹里：" + ctx.show(root / elsewhere[0])) if elsewhere
                 else "、".join(ctx.listdir(root / "1-wrong-folder/docs", hidden=False)) or "文件夹是空的")
    elif ctx.read(backup) != info.facts["s1_text"]:
        ctx.fail("情况 1：备份的内容要和 notes.txt 一模一样",
                 where=ctx.show(backup), saw="内容和原文件不同")
    else:
        ctx.ok("情况 1：notes.txt 已经在正确的位置备份好了")
        done += 1

    # 2. misspelt command
    diary = ctx.git(root / "2-typo/diary")
    if diary.is_repo:
        ctx.ok("情况 2：diary 已经是一个仓库")
        done += 1
    elif diary.inside_repo:
        ctx.fail("情况 2：仓库建在了上一层，不在 diary 里",
                 where=ctx.show(root / "2-typo/diary"),
                 saw="所在的仓库是 " + ctx.show(diary.toplevel))
    else:
        ctx.fail("情况 2：diary 还不是仓库", where=ctx.show(root / "2-typo/diary"),
                 saw="里面没有 .git")

    # 3. nothing staged
    notes = ctx.git(root / "3-nothing-staged/notes")
    plan = notes.file_at("HEAD", "plan.md") or ""
    if notes.commit_count() <= info.facts["s3_commits"]:
        ctx.fail("情况 3：还没有新的提交", where="3-nothing-staged/notes 的提交历史",
                 saw=f"还是 {notes.commit_count()} 个提交")
        if "plan.md" in notes.status().staged and ctx.git_global_state("commit.gpgsign") == "true":
            ctx.note("情况 3：plan.md 已经在暂存区里，提交却没有成功。如果 git commit 报的是 gpg "
                     "或 sign（签名）的错，对导师说“急救：提交签名”。")
    elif info.facts["s3_line"] not in plan:
        ctx.fail("情况 3：新提交里没有 plan.md 的那处改动",
                 where="最新提交里的 plan.md", saw="新加的那一行不在里面")
    elif not notes.is_clean():
        ctx.fail("情况 3：还有没提交的改动", where="3-nothing-staged/notes 的 git status",
                 saw="不是 nothing to commit")
    else:
        ctx.ok("情况 3：plan.md 的改动已经提交")
        done += 1

    # 5. unclosed quote
    old = root / "5-quote/my notes.txt"
    new = root / "5-quote/my-notes.txt"
    if not ctx.is_file(new):
        ctx.fail("情况 5：还没有叫 my-notes.txt 的文件", where=ctx.show(root / "5-quote"),
                 saw="、".join(ctx.listdir(root / "5-quote", hidden=False)) or "文件夹是空的")
    elif ctx.read(new) != info.facts["s5_text"]:
        ctx.fail("情况 5：my-notes.txt 的内容不是原来那份笔记", where=ctx.show(new),
                 saw="内容变了")
    elif ctx.exists(old):
        ctx.fail("情况 5：旧名字的文件还在，要改名而不是复制", where=ctx.show(root / "5-quote"),
                 saw="my notes.txt 还在")
    else:
        ctx.ok("情况 5：文件已经改成了不带空格的名字")
        done += 1
    return done


def _hidden_matches(hidden):
    bare = hidden.lstrip(".").lower()

    def check(answer):
        return answer.strip().lstrip(".").lower() == bare
    return check


def check_a(ctx):
    info = ctx.scenario("1.14a")
    # Ask the question only once at least one situation shows real work.
    if _lab_artifacts(ctx, info) == 0:
        ctx.note("情况 1、2、3、5 里至少有一个通过以后，检查才会问情况 4 的小问题。")
        ctx.stop()
    if not ctx.ask("情况 4：4-full-width 里那个隐藏文件叫什么名字？",
                   expected=_hidden_matches(info.facts["s4_hidden"])):
        ctx.note("情况 4：隐藏文件的名字以点开头，要用能显示隐藏文件的那个选项，"
                 "而且减号要是英文输入法敲出来的。")


# ---------------------------------------------------------------------------
# Station 1.14b: minimal reproduction and the five-part question
# ---------------------------------------------------------------------------
SECTIONS = [("目标", "目标"), ("做了什么", "我做了什么"), ("期望", "我期望什么"),
            ("实际", "实际看到什么"), ("版本", "版本")]
QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def _skeleton_text(skeleton):
    return textwrap.dedent(skeleton).strip()


# The skeletons' own bracketed hints; a bracketed line the learner wrote is content.
PLACEHOLDERS = {line.strip() for line in _skeleton_text(QUESTION_SKELETON).splitlines()
                if line.strip().startswith("（") and line.strip().endswith("）")}


HEADING = re.compile(r"^(#{1,6})\s")
FENCE = re.compile(r"^(`{3,}|~{3,})")


def _sections(text):
    """Map each of the five keywords to the text under its heading.

    Markdown is read as Markdown, so that any correct form of the question
    passes:
    - inside a fenced block (``` or ~~~) nothing is a heading: a comment line
      such as 「# 从一个空文件夹开始」 in a ```zsh block is content;
    - a heading is # to ###### followed by a space (「#注释」 is content);
    - a level-2 or deeper heading that contains a keyword starts that section,
      so 「## 1. 我做了什么」 and 「### 我做了什么」 count;
    - a level-2 heading without a keyword ends the current section; a deeper
      one (「### 在终端里依次敲」) or a level-1 line keeps it, because it is a
      sub-heading of the section it stands in.
    A key that has no heading at all is missing from the result.
    """
    found = {}
    current = None
    fence = None
    for raw in text.splitlines():
        line = raw.strip()
        opener = FENCE.match(line)
        if fence is not None:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence) \
                    and not line[len(opener.group(1)):].strip():
                fence = None               # the closing fence
            elif current is not None and line:
                found[current].append(line)
            continue
        if opener:
            fence = opener.group(1)        # an opening fence; its info string is not content
            continue
        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            key = next((k for k, _label in SECTIONS if k in line), None) if level >= 2 else None
            if key is not None:
                current = key
                found.setdefault(key, [])
            elif level == 2:
                current = None
            continue
        if current is None or not line:
            continue
        if line in PLACEHOLDERS:
            continue                       # a placeholder of the skeleton
        found[current].append(line)
    return {key: "\n".join(value) for key, value in found.items()}


def _restore_fails(line):
    """A git restore line that needs HEAD: --staged / -S (also -SW, -WS), or --source / -s."""
    match = re.search(r"\bgit\s+restore\b(.*)", line)
    if not match:
        return False
    rest = " " + match.group(1)
    return re.search(r"\s(--sta\w*|--source\b|-[A-Za-z]*[Ss]\S*)", rest) is not None


def _log_fails(line):
    return re.search(r"\bgit\s+log\b", line) is not None


def _question_ok(ctx, root, mini, error, failing, failing_text, skeleton=QUESTION_SKELETON):
    """Shared by station 1.14b and exam task 1.14-x2.

    Both errors depend on one condition only: a repository with no commit yet
    (HEAD points at nothing).  So the reproduction is judged by that condition
    and by its size; a reproduction with no file at all is the smallest one.
    `failing` tells whether a line of 我做了什么 is the command that fails;
    `failing_text` names what the check looks for, for the feedback.
    """
    # The minimal reproduction
    mini_path = root / mini
    if not ctx.is_dir(mini_path):
        ctx.fail("还没有做最小复现的文件夹 " + mini, where=ctx.show(root),
                 saw="没有这个文件夹")
    else:
        repo = ctx.git(mini_path)
        files = ctx.walk(mini_path)
        if not repo.is_repo:
            ctx.fail(mini + " 还不是仓库，原来的问题是在仓库里出现的",
                     where=ctx.show(mini_path), saw="里面没有 .git")
        elif repo.has_commits:
            ctx.fail(mini + " 和出问题的项目不是同一种状态",
                     where=ctx.show(mini_path) + " 的提交历史",
                     saw=f"已经有 {repo.commit_count()} 个提交，出问题的项目一个也没有")
        elif len(files) > 3:
            ctx.fail(mini + " 里的文件太多，还不够“最小”",
                     where=ctx.show(mini_path), saw=f"有 {len(files)} 个文件")
        else:
            ctx.ok(f"{mini} 是一个很小的复现：{len(files)} 个文件，还没有提交")

    # The question
    qpath = root / "question.md"
    text = ctx.read(qpath)
    if not text.strip():
        ctx.fail("question.md 不见了或者是空的", where=ctx.show(qpath), saw="没有内容")
        return
    if text.strip() == _skeleton_text(skeleton):
        ctx.fail("question.md 还是刚搭好时的样子", where=ctx.show(qpath), saw="一个字都没变")
        ctx.note("如果你已经在 VS Code 里写了，先按 ⌘S 保存，再检查。")
        return
    title = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if not title.startswith("#") or "……" in title:
        ctx.fail("第一行的标题还没写成一句具体的话", where="question.md 的第一行",
                 saw=f"现在是「{ctx.visible(title[:30])}」")
    sections = _sections(text)
    missing = [(key, label) for key, label in SECTIONS if key not in sections]
    empty = [label for key, label in SECTIONS if key in sections and not sections[key].strip()]
    if missing:
        ctx.fail("没找到这几段：" + "、".join(label for _key, label in missing)
                 + "。小标题请保留骨架里的写法，例如「## " + missing[0][1] + "」",
                 where="question.md 里以 ## 开头的小标题",
                 saw="没有一个小标题里有“" + "”“".join(key for key, _label in missing) + "”")
        if sum(1 for line in text.splitlines() if FENCE.match(line.strip())) % 2:
            ctx.note("question.md 里有一个代码块（``` 开头的那一行）没有收尾，它后面的小标题都被当成了代码。"
                     "在代码块的最后一行下面再加一行 ```。")
    if empty:
        ctx.fail("这几段还空着：" + "、".join(empty), where="question.md",
                 saw="小标题下面只有骨架里的括号说明，或者什么也没有")
    if not missing and not empty:
        ctx.ok("五段都写了内容")
    actual = sections.get("实际", "").translate(QUOTES)
    if actual and error not in actual:
        ctx.fail("“实际看到什么”里没有一字不差的报错原文", where="question.md 的“实际看到什么”",
                 saw="没有找到和终端里一模一样的那一行报错")
    elif actual:
        ctx.ok("报错原文原样贴进来了")
    if missing or empty or (actual and error not in actual):
        # The check reads the file on disk: text typed after the last save is not there yet.
        ctx.note("如果你在 VS Code 里改过以后还没保存，先按 ⌘S 保存，再检查。")
    done = sections.get("做了什么", "")
    if done:
        lines = done.splitlines()
        has_init = any(re.search(r"\bgit\s+init\b", line) for line in lines)
        has_failing = any(failing(line) for line in lines)
        if not has_init:
            ctx.fail("“我做了什么”里少了把文件夹变成仓库的那条命令",
                     where="question.md 的“我做了什么”", saw="没有找到含 git init 的一行")
        if not has_failing:
            ctx.fail("“我做了什么”里少了让报错出现的那条命令",
                     where="question.md 的“我做了什么”", saw="没有找到" + failing_text + "的一行")
        if has_init and has_failing:
            ctx.ok("“我做了什么”从建仓库写到了出错的那条命令")
    versions = sections.get("版本", "")
    if versions:
        git = ctx.git_version()
        git_text = ".".join(str(part) for part in git[:2]) if git else ""
        mac = ctx.run(["sw_vers", "-productVersion"])
        mac_text = ".".join(mac.out.strip().split(".")[:2]) if mac.ok and mac.out.strip() else ""
        absent = []
        if git_text and git_text not in versions:
            absent.append("Git")
        if mac_text and mac_text not in versions:
            absent.append("macOS")
        if absent:
            ctx.fail("“版本”里还缺你电脑上真实的 " + "、".join(absent) + " 版本号",
                     where="question.md 的“版本”", saw="没有找到和这台电脑一致的版本号")
        else:
            ctx.ok("版本号和这台电脑上的一致")
    home = str(ctx.home)
    if home and home in text:
        ctx.fail("里面有带你用户名的完整路径，公开提问前要换成 ~", where="question.md",
                 saw="出现了 /Users/ 开头、带着用户名的路径")


RESTORE_TEXT = " git restore 加 --staged（或 -S）"
LOG_TEXT = " git log "


def check_b(ctx):
    info = ctx.scenario("1.14b")
    _question_ok(ctx, info.path, "mini", "fatal: could not resolve 'HEAD'",
                 _restore_fails, RESTORE_TEXT, skeleton=STATION_SKELETON)


# ---------------------------------------------------------------------------
# Station 1.14c: three snippets, current or outdated
# ---------------------------------------------------------------------------
def check_c(ctx):
    # Each snippet can only be judged by doing one of the three checks on this
    # machine; none of them repeats the 补全 or a 旧教程提醒 box.
    ctx.quiz(
        "资料一（2021 年的一篇教程，写给 Linux：另一种操作系统，服务器上最常见）："
        "“想知道 ls 有哪些选项，运行 ls --help。”在终端里试一下。它对你的电脑怎么样？",
        ["照做就行：ls --help 会列出 ls 的全部选项",
         "对不上：这台 Mac 上的 ls 说不认识这个选项，只打印了一行用法",
         "对不上：ls 说 command not found，这台电脑上没有 ls"],
        "B",
        explain="线索是“它说的是哪个系统”：教程写给 Linux，Mac 自带的 ls 是另一个版本，不认 --help，要看 man ls。",
        feedback={"A": "先真的运行一次 ls --help，读第一行写的是什么。",
                  "C": "ls 你从第 0.1 课就在用。再运行一次 ls --help，看冒号后面的关键词。"},
    )
    ctx.quiz(
        "资料二（2014 年的教程）：“git log --oneline 让每个提交只占一行：前面是编号，后面是说明。”"
        "进一个仓库试一下（比如网站副本 1.14-start/my-site）。它现在怎么样？",
        ["过时了：2014 年太久了，Git 的命令早就改过",
         "还对：我运行了，每个提交一行，编号在前、说明在后",
         "对不上：现在 git log --oneline 每个提交会显示作者和日期"],
        "B",
        explain="旧不等于错。日期只是提醒你去查，在自己电脑上试一下就能确定。",
        feedback={"A": "年份只是提醒你去查。真的运行一次再下结论。",
                  "C": "再运行一次 git log --oneline，看每一行里到底有什么。"},
    )
    ctx.quiz(
        "资料三（一个 AI 助手今天的回答）：“Git 目前最新的版本是 2.45，比这更新的还没有发布。”"
        "它现在怎么样？",
        ["还对：AI 是今天回答的，说的就是现在的情况",
         "看不出来：只有等 Git 官网通知才知道",
         "过时了：你电脑上的 git --version 已经比它说的“最新版”还新"],
        "C",
        explain="线索是“版本”：AI 有知识截止日期，今天回答不等于知道今天的事。git --version 或 fresh 一比就知道。",
        feedback={"A": "回答的日期新，不等于它知道的事情新。运行 git --version 看看。",
                  "B": "不用等通知：你自己的电脑上就有一个可以比的版本号。"},
    )


checks = {"1.14a": check_a, "1.14b": check_b, "1.14c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.14a": [
        "每个情况都先把报错读完，再答报错三问：谁在报错、关键词是什么、我刚才敲了什么。"
        "检查结果里“情况几”没过，就只回到那个文件夹。",
        "先运行 pwd 和 ls，确认自己在哪个文件夹、旁边有什么。几句英文的意思：\n"
        "情况 3 的 no changes added to commit：暂存区里什么也没有，这次没拍下任何东西；\n"
        "情况 4 的 No such file or directory：ls 把 －a 当成了文件名去找，看看这个减号和你平常敲的是不是同一个；\n"
        "情况 5 的 dquote>：命令里有一个双引号没配上对，第 1 站概念里那张表写了怎么出来。",
        "相似的例子（不是这五个里的）：mkdir \"new folder 回车后出现 dquote>，按 Ctrl+C 退出，"
        "改成 mkdir new-folder；git　init（中间是一个全角空格）报 zsh: command not found: git　init，"
        "切回英文输入法重敲；改了 README.md 直接 git commit，输出里有 no changes added to commit，"
        "先 git add README.md 再提交。",
        "答案（每行一个情况，后面是原因）：\n"
        "1：cd docs，再 cp notes.txt notes-backup.txt。原因：notes.txt 在下一层的 docs 里，cp 只在当前文件夹里找。\n"
        "2：在 diary 里运行 git init。原因：gti 是 git 拼错了，zsh 找不到叫 gti 的命令。\n"
        "3：git add plan.md，再 git commit -m \"docs: 更新计划\"，最后 git status 看是不是干净的。"
        "原因：提交只拍暂存区里的东西，改过的文件要先 git add。\n"
        "4：用英文输入法敲 ls -a，以点开头的那个名字就是答案。原因：－ 是全角的减号，"
        "ls 不把它当选项，当成了一个叫 －a 的文件去找。\n"
        "5：按 Ctrl+C 退出 dquote>，再运行 mv \"my notes.txt\" my-notes.txt。"
        "原因：第一个双引号没有配对，zsh 以为命令还没敲完，在等你补上另一个引号。",
    ],
    "1.14b": [
        "这一站不要求你修好问题，要求你把问题问清楚：先做一个最小复现，再把 question.md 写完并保存。",
        "最小复现在 1.14b 文件夹里新建 mini：从空文件夹开始，只做让报错出现必需的事，"
        "再敲大项目里出错的那条命令。HEAD 指“最新的提交”，想想大项目里有没有提交。"
        "版本用 sw_vers -productVersion 和 git --version 查。",
        "相似的例子见课文第 2 站“跟我做”：全角减号的问题，在空文件夹 mini-example 里一条 ls 命令就复现了，"
        "五段里每段一两行。",
        "答案：cd ~/Developer/playground/1.14b，mkdir mini，cd mini，git init，touch a.txt，git add a.txt，"
        "git restore --staged a.txt，看到 fatal: could not resolve 'HEAD'。"
        "（不建 a.txt、直接 git restore --staged a.txt 也会出同一个报错，也算对；-S 和 --staged 是同一个选项。）"
        "然后在 VS Code 里改 question.md：标题写一句话，比如“新仓库里 git restore --staged 报 could not resolve 'HEAD'”；"
        "“我做了什么”按顺序写这些命令；“实际看到什么”原样贴报错那一行；"
        "“版本”贴 git --version 和 sw_vers -productVersion 的输出；路径写成 ~ 开头；最后 ⌘S 保存。"
        "原因：新仓库还没有任何提交，HEAD 指向一个还不存在的提交；git restore --staged 要拿 HEAD 里的样子"
        "来恢复暂存区，所以找不到 HEAD。别人照着你的步骤在自己电脑上就能看到同一个报错，才帮得上你。",
    ],
    "1.14c": [
        "每段资料都用三查：它是哪年的、它说的是哪个版本或哪个系统、你电脑上的工具或官方文档现在怎么说。"
        "这一站每段都要动手查一下。",
        "资料一：在终端里运行 ls --help，读第一行。资料二：在网站副本里运行 git log --oneline。"
        "资料三：运行 git --version，和它说的“最新版”比。",
        "相似的例子：一份 2018 年的资料说“Mac 的终端默认用 bash”（bash：另一种 shell，旧版 macOS 默认用它）。三查：日期 2018 年；"
        "版本：它没写是哪个 macOS；你电脑上的提示符以 % 结尾，第 0.1 课讲过，"
        "自 macOS 10.15 起默认的 shell 是 zsh。结论：过时了。",
        "答案：资料一选 B（Mac 自带的 ls 不认 --help 这个选项，要看 man ls）；"
        "资料二选 B（git log --oneline 至今还是每个提交一行）；"
        "资料三选 C（你电脑上 git --version 的版本比它说的 2.45 新；建课时核对的是 2.54）。"
        "解释：日期只是提醒你去查，结论要靠版本对比，和你电脑上的工具、官方文档现在怎么说。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.14-three-questions", "type": "recall", "tier": "fluent", "station": "1.14a",
     "q": "终端里出现 zsh: command not found: gti。按报错三问，各用一句话回答。",
     "a": "谁在报错：zsh，终端里接你命令、照着执行的那个程序（shell）。"
          "关键词：command not found，找不到这个命令。"
          "我刚才敲了：gti，是 git 拼错了，改成 git 再敲一遍。"},
    {"id": "1.14-dquote", "type": "which", "tier": "fluent", "station": "1.14a",
     "q": "敲完命令按回车，提示符变成了 dquote>，再按回车也没反应。最稳妥的办法是什么？",
     "options": ["按 Ctrl+C，回到平常的提示符，再把命令改对重敲",
                 "关掉终端窗口重新打开",
                 "在 dquote> 后面把整条命令再敲一遍"],
     "answer": "A", "shuffle": True,
     "explain": "dquote> 表示有一个双引号没配对。Ctrl+C 放弃这一行；在 dquote> 后面接着敲，只会把新敲的字也算进引号里。"},
    {"id": "1.14-leave-vi", "type": "which", "tier": "fluent", "station": "1.14a",
     "q": "不小心进了 vi，还按乱了几个键。想不保存、直接退出，怎么按？",
     "options": ["按 Esc，再输入 :q! 然后回车", "只按一下 q 键", "按 Ctrl+C"],
     "answer": "A", "shuffle": True,
     "explain": "q 是退出 less 的键，在 vi 里没用；Ctrl+C 退不出 vi。Esc 先回到命令状态，:q! 表示不保存强制退出。"},
    {"id": "1.14-not-a-repo", "type": "which", "tier": "fluent", "station": "1.14a",
     "q": "在一个文件夹里运行 git log --oneline，看到 fatal: not a git repository "
          "(or any of the parent directories): .git。ls 一看，里面有一个 shop-lumen 文件夹。下一步做什么？",
     "options": ["cd shop-lumen，再运行 git log --oneline",
                 "就在这里运行 git init，把这里变成仓库",
                 "Git 坏了，重新安装 Git"],
     "answer": "A", "shuffle": True,
     "explain": "报错说这里和上面几层都不是仓库，真正的仓库多半在下一层。在这里 git init 只会建一个新的空仓库，看不到原来的提交。"},
    {"id": "1.14-ignored", "type": "which", "tier": "fluent", "station": "1.14a",
     "q": "git add drafts/first-post.md 报 The following paths are ignored by one of your .gitignore files。"
          "想知道是哪一个忽略文件的哪一行挡住了它，用哪条命令？",
     "options": ["git check-ignore -v drafts/first-post.md",
                 "git add -f drafts/first-post.md",
                 "git status --ignored"],
     "answer": "A", "shuffle": True,
     "explain": "check-ignore -v 会打印挡住它的那个文件、行号和那条规则（第 1.9 课）。-f 是硬塞进去，不告诉你原因；"
                "status --ignored 只列出被忽略的文件，不说是哪一行。"},
    {"id": "1.14-question-parts", "type": "recall", "tier": "fluent", "station": "1.14b", "rule": "HELP-01",
     "q": "向别人求助时，一个问题要写哪五段？",
     "a": "目标；我做了什么（从空文件夹开始的每条命令）；我期望什么；实际看到什么（报错原文）；版本。"},
    {"id": "1.14-who-decides", "type": "which", "tier": "fluent", "station": "1.14c", "rule": "FRESH-01",
     "q": "网上一份教程和你电脑上的结果对不上。判断谁过时，最后说了算的是什么？",
     "options": ["教程写的日期越新越对",
                 "你电脑上装的工具自己的说法（-h、man、提示信息）和它的官方文档现在怎么写",
                 "点赞和收藏多的那一篇"],
     "answer": "B",
     "explain": "日期只提醒你去查；点赞多不等于对。你电脑上的工具和官方文档才是现在的样子。"},
]


# ---------------------------------------------------------------------------
# EXAM (gate-1)
# ---------------------------------------------------------------------------
X1_RULES = ["*.tmp", ".env", "*.bak", "*.zip", "node_modules/"]

# Exam task 1.14-x1 tests lesson 1.14's own skill (reading an error with the
# three questions of META-01, station 1.14a) on top of lesson 1.9's skill
# (finding the rule that blocks a file).  The learner writes the three answers
# into answers.md next to the repository, so the grader can read them.
X1_LABELS = [("who", "谁在报错", r"谁"), ("keyword", "关键词", r"关键"),
             ("typed", "我刚才敲了什么", r"我刚|我敲|敲了")]
X1_SKELETON = "# 报错三问\n\n谁在报错：\n关键词：\n我刚才敲了什么：\n"
COLON = re.compile(r"[:：]")
LEAD = "#-*> 0123456789.、）)"


def _x1_label(line):
    """The key whose label starts this line (after list marks or a number), or None."""
    head = line.lstrip(LEAD).strip()
    for key, _label, stem in X1_LABELS:
        if re.match(stem, head):
            return key
    return None


def _x1_answers(text):
    """Map who / keyword / typed to what the learner wrote after each label.

    The answer may stand on the label's line after the colon, or on the next
    non-empty line when the label line ends with the colon.  A label that is
    not in the file at all is missing from the result.
    """
    lines = [line.strip() for line in text.splitlines()]
    found = {}
    for index, line in enumerate(lines):
        key = _x1_label(line)
        if key is None or key in found:
            continue
        parts = COLON.split(line, maxsplit=1)
        answer = parts[1].strip() if len(parts) == 2 else ""
        if not answer:
            for later in lines[index + 1:]:
                if not later:
                    continue
                if _x1_label(later) is None and not later.startswith("#"):
                    answer = later
                break
        found[key] = answer
    return found


def _x1_saw(answer):
    return "现在是「" + answer[:40] + "」" if answer else "这一行冒号后面还是空的"


def _grade_x1_answers(ctx, info):
    path = info.path / "answers.md"
    text = ctx.read(path)
    if not text.strip() or text.strip() == X1_SKELETON.strip():
        ctx.fail("报错三问还没有写", where=ctx.show(path),
                 saw="还是刚出题时的样子" if text.strip() else "文件不见了或者是空的")
        return
    answers = _x1_answers(text)
    missing = [label for key, label, _stem in X1_LABELS if key not in answers]
    if missing:
        ctx.fail("answers.md 里少了这几行：" + "、".join(missing) + "。请保留出题时写好的开头",
                 where=ctx.show(path), saw="没有以「" + missing[0] + "：」开头的一行")
    who = answers.get("who")
    if who is not None:
        ctx.expect(re.search(r"git", who, re.IGNORECASE) is not None,
                   "“谁在报错”答对了", "“谁在报错”没有对上真正报错的那个程序",
                   where="answers.md 的“谁在报错”", saw=ctx.visible(_x1_saw(who)))
    keyword = answers.get("keyword")
    if keyword is not None:
        lowered = keyword.lower()
        ctx.expect("ignored" in lowered or ".gitignore" in lowered,
                   "关键词是从报错里原样抄来的",
                   "“关键词”里没有报错原文里的那个英文关键词",
                   where="answers.md 的“关键词”", saw=ctx.visible(_x1_saw(keyword)))
    typed = answers.get("typed")
    if typed is not None:
        ctx.expect(re.search(r"\bgit\s+add\b", typed) is not None,
                   "“我刚才敲了什么”写的是出错的那条命令",
                   "“我刚才敲了什么”里没有让报错出现的那条命令",
                   where="answers.md 的“我刚才敲了什么”", saw=ctx.visible(_x1_saw(typed)))


def build_x1(sc):
    """A repository where one file is blocked by one line of .gitignore."""
    repo = sc.word() + "-notes"
    word = sc.word()
    if sc.form == "A":
        rule, target = "drafts/", f"drafts/{word}.md"
    else:
        rule, target = "report*", f"report-{word}.md"
    others = sc.sample(X1_RULES, 3)
    at = sc.randint(0, 3)
    rules = others[:at] + [rule] + others[at:]
    sc.git_init(repo)
    sc.write(repo + "/.gitignore", "\n".join(rules) + "\n", exact=True)
    sc.fact("ignore_text", "\n".join(rules) + "\n")
    sc.write(repo + "/README.md", "# 笔记\n")
    sc.git_commit(repo, "docs: 添加说明和忽略规则")
    sc.write(f"{repo}/{target}", "# 本周总结\n\n这份要提交。")
    sc.fact("repo", repo)
    sc.fact("file", target)
    sc.fact("rule", rule)
    sc.fact("others", others)
    sc.fact("commits", 1)
    sc.write("answers.md", X1_SKELETON, exact=True)


def grade_x1(ctx):
    info = ctx.scenario()
    _grade_x1_answers(ctx, info)            # lesson 1.14's own skill: the three questions
    repo = ctx.git(info.path / info.facts["repo"])
    if not repo.is_repo:                  # the builder made it a repository; no praise for that
        ctx.fail("考试仓库不是 Git 仓库了", where=ctx.show(repo.path), saw="里面没有 .git")
        ctx.stop()
    target = info.facts["file"]
    ignore_path = repo.path / ".gitignore"
    ignore = [line.strip() for line in ctx.lines(ignore_path)]
    if repo.file_at("HEAD", target) is None:
        # Nothing is praised before the work is there (tool-api 19.12).
        ctx.fail("要求的文件还没有进入提交", where="最新提交", saw="里面没有 " + target)
        if info.facts["rule"] in ignore:
            ctx.fail("挡住它的那条规则还在 .gitignore 里", where=".gitignore", saw="那一行还在")
        ctx.stop()
    ctx.ok("那个文件已经进入提交")
    ctx.expect(info.facts["rule"] not in ignore, "挡住它的那条规则已经改掉了",
               "挡住它的那条规则还在 .gitignore 里", where=".gitignore", saw="那一行还在")
    kept = [rule for rule in info.facts["others"] if rule in ignore]
    ctx.expect(len(kept) == len(info.facts["others"]), "别的忽略规则都还在",
               "别的忽略规则也被删掉了", where=".gitignore",
               saw=f"原来 {len(info.facts['others'])} 条，现在剩 {len(kept)} 条")
    committed = repo.file_at("HEAD", ".gitignore")
    if not ctx.is_file(ignore_path):
        pass                              # the missing rules were reported above; nothing to praise
    elif committed is None or committed != ctx.read(ignore_path):
        ctx.fail(".gitignore 的改动还没有提交", where="最新提交里的 .gitignore", saw="和文件夹里的不一样")
    elif committed != info.facts["ignore_text"]:
        ctx.ok("改过的 .gitignore 也提交了")
    ctx.expect(repo.is_clean(), "没有落下的改动", "还有改动没有处理",
               where="git status", saw="不是干净的")


def build_x2(sc):
    """A puzzling error in a big new project; the learner writes the question."""
    folder = sc.word() + "-site"
    _build_big_project(sc, folder)
    if sc.form == "A":
        sc.fact("command", "git restore --staged index.html")
    else:
        sc.fact("command", "git log")
    sc.fact("project", folder)
    sc.write("question.md", QUESTION_SKELETON)


def grade_x2(ctx):
    info = ctx.scenario()
    if info.form == "A":
        _question_ok(ctx, info.path, "mini", "fatal: could not resolve 'HEAD'",
                     _restore_fails, RESTORE_TEXT)
    else:
        _question_ok(ctx, info.path, "mini", "does not have any commits yet",
                     _log_fails, LOG_TEXT)


EXAM = [
    {
        "id": "1.14-x1",
        "gate": "gate-1",
        "title": "读懂 git add 的报错，查出挡住文件的规则",
        "minutes": 8,
        "build": build_x1,
        "task": {
            "A": "仓库 {dir}/{repo} 里的 {file} 要提交，可是 git add 不收它。先在仓库里运行 git add {file}，"
                 "按报错三问把三行答案写进 {dir}/answers.md（关键词从报错里原样抄英文）。"
                 "再查出是哪条规则挡住了它，去掉这条规则（别的规则保留），把这个文件和改过的 .gitignore 都提交。"
                 "做完 git status 要是干净的。",
            "B": "进入 {dir}/{repo}：{file} 是要交的周报，用 git add 加它的名字，Git 却报错。"
                 "{dir}/answers.md 里有报错三问的三行开头，照着报错把每行写完，关键词照抄报错里的英文。"
                 "然后找出原因并改掉那一条规则，其他忽略规则不动；最后周报和 .gitignore 的改动都要在提交里，工作区干净。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.14-x2",
        "gate": "gate-1",
        "title": "为一个报错写出能复现的提问",
        "minutes": 10,
        "build": build_x2,
        "task": {
            "A": "在 {dir}/{project} 里运行 {command} 会报错。不用修好它：在 {dir} 下建一个叫 mini 的最小复现"
                 "（文件越少越好），再把 {dir}/question.md 的五段写完整，报错原样粘贴，写上真实版本号。",
            "B": "{dir}/{project} 是一个刚建好的项目，在里面运行 {command} 会报错。请为它写一个别人能照着复现的提问："
                 "复现放在 {dir}/mini，提问写在 {dir}/question.md，五段都要有，报错一字不改，版本号要真实。",
        },
        "grade": grade_x2,
    },
]
