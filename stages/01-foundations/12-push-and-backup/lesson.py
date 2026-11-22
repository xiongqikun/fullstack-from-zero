"""Lesson 1.12: 第一次推送和云端备份 (plan section 4).

Station a: the workspace itself becomes a repository (first commit, after a
           search for secrets), plus a practice folder in the playground
           brought into a repository.  A learner who stayed in a synced
           folder in lesson 0.2 is asked once more (decision
           ``workspace_location``).
Station b: the workspace is pushed to a private GitHub repository (gh), plus
           a practice push to a local stand-in remote with a pre-flight check.
Station c: the backup is verified by cloning it, plus a practice restore from
           a stand-in remote.

Checks never use the network.  The GitHub part of station b is checked
through what Git records locally (a remote named origin, an upstream); the
private visibility on GitHub cannot be seen offline and is only noted.
"""

import os
import re
from pathlib import Path

META = {
    "id": "1.12",
    "slug": "12-push-and-backup",
    "title": "第一次推送和云端备份",
    "stage": 1,
    "prerequisites": ["1.11"],
    "stations": [
        {"id": "1.12a", "title": "学习仓库入库", "minutes": 40,
         "new_concept": "一个早就有很多文件的文件夹，收进仓库之前先看清：哪些被挡在外面、要收的是哪些、内容里有没有密钥",
         "new_commands": ["git add .", "git grep --untracked"]},
        {"id": "1.12b", "title": "推送到私有仓库", "minutes": 40,
         "new_concept": "远程仓库：放在别处的另一份仓库，要你推送才会更新",
         "new_commands": ["gh repo create", "git remote -v", "git push"]},
        {"id": "1.12c", "title": "验证备份真的能用", "minutes": 40,
         "new_concept": "没恢复过的备份只是愿望：克隆一份出来，和原来的比一比",
         "new_commands": ["git clone", "diff -r -q", "rm -rf"]},
    ],
    "rules": ["REMOTE-01", "REMOTE-02"],
    "verified": {"date": "2026-11-20",
                 "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9",
                           "gh": "2.105.0"}},
    "unverified_steps": [
        "1.12b：gh repo create my-fullstack-learning --private --source=. --remote=origin --push 的执行和屏幕输出"
        "（需要 GitHub 账号和网络；按 gh 官方手册和源代码核对，2026-11-20）",
        "1.12b（「想多了解」框「推送被 GH007 拦下」）：推送被拦下时的 remote: error: GH007 那一行（需要 GitHub 账号；"
        "GitHub Docs 只写了机制，原话来自用户的报告）；在 Emails 页去掉 Block command line pushes that expose my email "
        "的勾（对照 GitHub Docs 和第 1.11 课）；两种办法共用的 git push --set-upstream origin main 在本地实测",
        "1.12b：git remote -v 里 GitHub 地址的样子（本地用代替 GitHub 的仓库实测，地址按 gh 源代码的格式改写）",
        "1.12b（「想多了解」框）：gh repo view --json visibility 的输出（需要账号和网络；按 gh 官方手册核对）",
        "1.12c：从 GitHub 克隆私有仓库时的认证和进度输出（需要网络；本地用代替 GitHub 的仓库实测其余部分）",
        "1.12c：Git 没有用 gh 当凭据助手时终端问 Username for 'https://github.com': 的情形（需要网络和账号；"
        "提示的格式取自本机 git 2.54.0 的 git-remote-https，2026-11-20）",
    ],
}

TERMS = [
    {"term": "远程仓库", "en": "remote", "plain": "放在别处的另一份仓库，要你推送或拉取才会同步",
     "first": "1.12b"},
    {"term": "推送", "en": "push", "plain": "把本机仓库里新的提交传到远程仓库", "first": "1.12b"},
    {"term": "私有仓库", "en": "private repository", "plain": "只有你和你邀请的人能看到的 GitHub 仓库",
     "first": "1.12b"},
    {"term": "上游", "en": "upstream", "plain": "本地分支默认推送到的那个远程分支，例如 origin/main",
     "first": "1.12b"},
    {"term": "克隆", "en": "clone", "plain": "从远程仓库完整复制一份仓库到本机，连同全部历史",
     "first": "1.12c"},
    {"term": "恢复测试", "en": "restore test", "plain": "真的从备份里取一份出来，确认它是完整、能用的",
     "first": "1.12c"},
]

TYPES = r"(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
SCOPE = r"(\([^()\s]+\))?!?"
# Conventional Commits 1.0.0, item 15: the units are not case-sensitive.  So a
# type in any letter case is the format; lesson 1.10's course rule (COMMIT-01)
# asks for lowercase, which is only noted.
CONVENTIONAL = re.compile(r"^" + TYPES + SCOPE + r": \S", re.I)
LOWERCASE_TYPE = re.compile(r"^" + TYPES + SCOPE + r": \S")
WIDE_COLON = re.compile(r"^" + TYPES + SCOPE + r"\s*\uff1a", re.I)
NO_SPACE = re.compile(r"^" + TYPES + SCOPE + r":\S", re.I)
COLON_NOTE = "类型后面的冒号是中文全角的“：”。要用英文半角的 :，后面再跟一个空格。"
SPACE_NOTE = "类型后面的冒号用对了，冒号后面还要有一个空格（约定式提交规范第 1 条）。"
CASE_NOTE = ("按第 1.10 课的约定（COMMIT-01），类型用小写字母，比如 docs。约定式提交规范本身不分大小写，"
             "所以这一次算对；以后的提交写小写。")


def _format_notes(ctx, subject):
    """Notes for a first line that is not, or not quite, in the course's form."""
    if WIDE_COLON.match(subject):
        ctx.note(COLON_NOTE)
    elif NO_SPACE.match(subject):
        ctx.note(SPACE_NOTE)
    elif CONVENTIONAL.match(subject) and not LOWERCASE_TYPE.match(subject):
        ctx.note(CASE_NOTE)


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
RECIPES = {
    "soup.md": "# 番茄蛋汤\n\n- 番茄两个\n- 鸡蛋两个\n",
    "noodles.md": "# 葱油拌面\n\n- 面条一把\n- 小葱一把\n",
    "rice.md": "# 蛋炒饭\n\n- 隔夜米饭一碗\n- 鸡蛋一个\n",
    "salad.md": "# 拍黄瓜\n\n- 黄瓜两根\n- 蒜三瓣\n",
    "dumplings.md": "# 白菜猪肉饺子\n\n- 白菜半棵\n- 猪肉馅三百克\n",
}
SKIPPED = {"drafts/idea.md": "# 还没想好的菜\n", "shopping.tmp": "周六要买：酱油、醋\n"}


def build_1_12a(sc):
    """A folder that is not yet a repository, with a .gitignore already in place."""
    folder = "recipes-" + sc.word()
    chosen = sorted(sc.sample(sorted(RECIPES), sc.randint(2, 4)))
    sc.write(folder + "/README.md", """
        # 家常菜谱

        我自己记的菜谱，一道菜一个文件。
    """)
    sc.write(folder + "/.gitignore", """
        # 还没写完的草稿
        drafts/
        # 临时记的东西
        *.tmp
    """)
    for name in chosen:
        sc.write(folder + "/" + name, RECIPES[name])
    for name, text in SKIPPED.items():
        sc.write(folder + "/" + name, text)
    keep = sorted(["README.md", ".gitignore"] + chosen)
    sc.fact("folder", folder)
    sc.fact("keep", keep)
    sc.fact("skip", sorted(SKIPPED))
    sc.todo("菜谱文件夹在这里（还不是仓库）：" + sc.show(folder))
    sc.todo("进到菜谱文件夹本身再做（不是上一层的 " + sc.id + "）：cd " + sc.show(folder))


TRIP_LINES = ["- 第三天：去博物馆", "- 第三天：坐船游湖", "- 第三天：爬山看日出", "- 第三天：逛老街吃小吃"]
PACKING = ["充电器", "雨伞", "身份证", "常用药", "转换插头"]


def _fake_token(sc, prefix):
    alphabet = "abcdef0123456789"
    return prefix + "".join(sc.pick(alphabet) for _ in range(32))


def _repo_with_standin(sc, name, subjects):
    """A repository ``name`` whose main is pushed to ``remote/<name>.git``, upstream set."""
    remote = "remote/" + name + ".git"
    sc.git_init(name)
    sc.write(name + "/README.md", "# " + name + "\n\n这是一个练习仓库。\n")
    sc.write(name + "/plan.md", "# 行程\n\n- 第一天：到达，休息\n")
    sc.git_commit(name, subjects[0], date=sc.ago(days=3))
    sc.append(name + "/plan.md", "- 第二天：市区步行\n")
    sc.git_commit(name, subjects[1], date=sc.ago(days=2))
    sc.git_init(remote, bare=True)
    sc.git(name, "remote", "add", "origin", str(sc.path(remote)))
    sc.git(name, "push", "-q", "-u", "origin", "main")
    return remote


def build_1_12b(sc):
    """A repository already pushed once; new work waits, and a token was pasted into plan.md."""
    name = "trip-" + sc.word()
    remote = _repo_with_standin(sc, name, ["docs: 写下行程的第一天", "docs: 补上第二天的安排"])
    line = sc.pick(TRIP_LINES)
    token = _fake_token(sc, "TOKEN=")
    sc.append(name + "/plan.md", line + "\n临时记一下，用完删：" + token + "\n")
    items = sc.sample(PACKING, 3)
    sc.write(name + "/packing.md", "# 要带的东西\n\n" + "".join("- " + item + "\n" for item in items))
    sc.fact("repo", name)
    sc.fact("remote", remote)
    sc.fact("commits", 2)
    sc.fact("line", line)
    sc.fact("token", token)
    sc.todo("练习仓库在这里：" + sc.show(name))
    sc.todo("它的远程仓库（代替 GitHub）在这里：" + sc.show(remote))
    sc.todo("进到练习仓库本身再做（不是上一层的 " + sc.id + "）：cd " + sc.show(name))


ALBUM_SUBJECTS = [
    "docs: 写下相册的说明",
    "docs: 记下第一批照片的地点",
    "docs: 补上第二批照片的日期",
    "docs: 整理照片的分类",
    "docs: 记下要冲印的照片",
    "docs: 改正一张照片的说明",
    "docs: 列出要给家人看的照片",
    "docs: 补上照片里的人名",
]


def _build_standin_only(sc, name, count):
    """Only a bare stand-in remote remains: the original folder is gone.

    The subjects are a sample of ALBUM_SUBJECTS kept in list order, so the
    earliest one differs between builds and the ask of 1.12c cannot be
    answered from memory.
    """
    remote = "remote/" + name + ".git"
    work = "gone/" + name
    picked = sorted(sc.sample(range(len(ALBUM_SUBJECTS)), count))
    subjects = [ALBUM_SUBJECTS[index] for index in picked]
    sc.git_init(work)
    for number, subject in enumerate(subjects, 1):
        sc.write(work + "/notes-" + str(number) + ".md", "# 第 " + str(number) + " 批\n")
        sc.git_commit(work, subject, date=sc.ago(days=count - number + 1))
    sc.git_init(remote, bare=True)
    sc.git(work, "remote", "add", "origin", str(sc.path(remote)))
    sc.git(work, "push", "-q", "origin", "main")
    sc.remove("gone")
    sc.fact("name", name)
    sc.fact("remote", remote)
    sc.fact("commits", count)
    sc.fact("first_subject", subjects[0])
    sc.fact("subjects", subjects)
    return remote


def build_1_12c(sc):
    name = "album-" + sc.word()
    remote = _build_standin_only(sc, name, sc.randint(3, 5))
    sc.todo("原来的 " + name + " 文件夹已经没了，只剩远程仓库（代替 GitHub）：" + sc.show(remote))
    sc.todo("要把它恢复到：" + sc.show(name))


def build_start(sc):
    """Just before 1.12: the site in state S6.  The lesson itself works on the workspace."""
    sc.site_before()
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))
    sc.todo("这一课需要：第 1.11 课装好并登录的 gh；学习工作区还不是仓库。")
    sc.todo("这一课主要在学习工作区里做，练习场只放练习用的副本。")


SCENARIOS = {
    "start": build_start,
    "1.12a": build_1_12a,
    "1.12b": build_1_12b,
    "1.12c": build_1_12c,
}


# ---------------------------------------------------------------------------
# shared check helpers
# ---------------------------------------------------------------------------
def _root_commit(repo):
    result = repo.query("rev-list", "--max-parents=0", "HEAD")
    if not result.ok or not result.lines:
        return None
    return repo.commit(result.lines[-1].strip())


OUTER_SENTENCE = "急救：外层有一个建错地方的仓库"


def _outer_repo_note(ctx, folder):
    """A folder that is not a repository itself but sits inside one: say how to get help."""
    view = ctx.git(folder)
    if view.exists and not view.is_repo and view.inside_repo:
        ctx.note("外层那个仓库多半是在错的文件夹里运行 git init 留下的。不要自己删它（删掉 .git 撤不回来）："
                 "对导师说“" + OUTER_SENTENCE + "”。")


def _workspace(ctx):
    _outer_repo_note(ctx, ctx.workspace)
    return ctx.need_repo(ctx.workspace, "学习工作区 fullstack-from-zero")


def _ignored_by_course(path):
    """Paths the workspace's own .gitignore keeps out (the course's own lines)."""
    name = path.rsplit("/", 1)[-1]
    return (path == "learner/last-result.json"
            or path.startswith("docs/research/local-only/")
            or (path.startswith("learner/") and "/" not in path[len("learner/"):]
                and name.startswith(".") and name.endswith(".tmp")))


def _workspace_committed(ctx):
    ws = _workspace(ctx)
    if not ws.has_commits:
        ctx.fail("学习仓库里还没有提交", where="学习仓库的提交历史", saw="git log 里是空的")
        return ws
    leaked = [p for p in ws.tracked() if _ignored_by_course(p)]
    if leaked:
        ctx.fail("有被 .gitignore 挡在外面的文件进了学习仓库", where="学习仓库里被跟踪的文件",
                 saw="、".join(leaked[:3]))
    else:
        ctx.ok("学习工作区已经是仓库，有了第一次提交，忽略规则挡住的文件没有进去")
    root = _root_commit(ws)
    if root is not None:
        if not CONVENTIONAL.match(root.subject):
            ctx.note("第一次提交的说明没有用约定式提交的格式。不用改，以后的提交按 1.10 课写就好。")
        _format_notes(ctx, root.subject)
        if not re.search(r"claude|ai", root.body or "", re.I):
            ctx.note("第一次提交的正文没写明课程材料由 AI 生成。不用改，以后导入新课程材料时记得写上。")
    return ws


def _exercise_a(ctx):
    info = ctx.scenario("1.12a")
    facts = info.facts
    target = info.path / facts["folder"]
    view = ctx.git(target)
    if view.exists and not view.is_repo and view.inside_repo:
        top = view.toplevel
        if top is not None and Path(top).resolve() == info.path.resolve():
            ctx.note("多半是在上一层的 " + info.id + " 里运行了 git init。重搭一份：python3 tools/course.py "
                     "scenario 1.12a --reset，再照它给的 cd 命令进到菜谱文件夹本身。")
        else:
            _outer_repo_note(ctx, target)
    repo = ctx.need_repo(target, "菜谱文件夹 " + facts["folder"], praise=True)
    if not repo.has_commits:
        ctx.fail("菜谱仓库里还没有提交", where="菜谱仓库的提交历史", saw="git log 里是空的")
        ctx.stop()
    root = _root_commit(repo)
    bad_root = False
    missing = [f for f in facts["keep"] if repo.file_at(root.hash, f) is None]
    if missing:
        bad_root = True
        ctx.fail("第一次提交里还少了该收进去的文件", where="菜谱仓库的第一次提交",
                 saw="缺 " + "、".join(missing))
    else:
        ctx.ok("该收的文件都在第一次提交里")
    leaked = [f for f in facts["skip"] if repo.is_tracked(f)]
    if leaked:
        ctx.fail(".gitignore 写明不收的文件进了仓库", where="菜谱仓库里被跟踪的文件",
                 saw="、".join(leaked))
    if CONVENTIONAL.match(root.subject):
        ctx.ok("第一次提交的说明用了约定式提交的格式")
    else:
        bad_root = True
        ctx.fail("第一次提交的说明要用约定式提交的格式", where="第一次提交的第一行",
                 saw="现在是「" + ctx.visible(root.subject[:30]) + "」")
    _format_notes(ctx, root.subject)
    if bad_root:
        ctx.note("第一次提交已经拍下，这一课还没学怎么改它。重搭一份再做：python3 tools/course.py scenario 1.12a --reset")
    if not repo.is_clean():
        ctx.fail("菜谱文件夹里还有没处理的改动", where="菜谱仓库的 git status",
                 saw="不是 nothing to commit, working tree clean")
    return facts


def _nested_repo(ctx, target):
    """A folder one level inside ``target`` that holds a ``.git`` (a clone made inside it)."""
    view = ctx.git(target)
    if not ctx.is_dir(target) or view.is_repo or view.inside_repo:
        return None
    for name in sorted(ctx.listdir(target)):
        if ctx.exists(target / name / ".git"):
            return name
    return None


def _restored(ctx, key):
    """The practice restore: shared by station c, the do item and the exam."""
    info = ctx.scenario(key)
    facts = info.facts
    bare = ctx.git(info.path / facts["remote"])
    if not bare.is_bare or bare.ref("main") is None:
        raise RuntimeError("stand-in remote of the scenario is missing or empty")
    target = info.path / facts["name"]
    inner = _nested_repo(ctx, target)
    if inner is not None:
        ctx.fail("恢复出来的仓库要正好是这个文件夹本身", where=ctx.show(target),
                 saw="它自己不是仓库，仓库在它里面一层：" + inner)
        if key is not None:
            ctx.note("多出来的这一层不要在里面再改。重搭一份再做：python3 tools/course.py scenario "
                     + key + " --reset")
        ctx.stop()
    repo = ctx.need_repo(target, "恢复出来的 " + facts["name"], praise=True)
    if repo.is_bare:
        ctx.fail("恢复出来的要是一个能看到文件的普通仓库", where=ctx.show(target),
                 saw="这是远程仓库那种只有历史、看不到文件的格式")
        if key is not None:
            ctx.note("重搭一份再做：python3 tools/course.py scenario " + key + " --reset")
        ctx.stop()
    url = repo.remotes().get("origin")
    same_remote = False
    if url:
        try:
            same_remote = Path(url).resolve() == (info.path / facts["remote"]).resolve()
        except (OSError, ValueError):
            same_remote = False
    ctx.expect(same_remote, "它的 origin 指向那个远程仓库",
               "这个仓库不是从那个远程仓库克隆来的", where="恢复出来的仓库的 git remote -v",
               saw=("origin 是「" + (url or "没有") + "」")[:60])
    if ctx.expect(repo.head is not None and repo.head == bare.ref("main"),
                  "最新提交和远程仓库里的一样", "恢复出来的历史和远程仓库里的不一样",
                  where="两边的 git log --oneline",
                  saw="最新提交的编号对不上" if repo.head else "这里一个提交也没有"):
        ctx.expect(repo.is_clean(), "恢复出来的文件和最新提交一模一样",
                   "恢复出来的文件夹里有改动", where="恢复出来的仓库的 git status", saw="不是干净的")
    elif key is not None and repo.head is not None:
        ctx.note("恢复出来以后又提交过的，这一课还没学怎么退回去。重搭一份再做：python3 tools/course.py scenario "
                 + key + " --reset")
    return facts


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
ICLOUD_ATTRIBUTE = "com.apple.file-provider-domain-id"
XATTR = "/usr/bin/xattr"
MOVE_SENTENCE = "帮我把课程安置到 ~/Developer"
README_CARD = "README.md 里的卡片「搬家后怎么找回导师」"


def _synced_folder(ctx, folder):
    """The folder (or ancestor) that a sync provider manages, or None.

    The same test as ``doctor`` and lesson 0.2: under ~/Library/Mobile
    Documents, or carrying the file-provider attribute.  Raises when it
    cannot look, so the learner sees 检查器出问题 and never a false 还没达标.
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


def _ask_location_again(ctx):
    """Lesson 0.2 promised to ask once more before the workspace becomes a repository.

    Only a learner who decided to stay (``workspace_location`` is
    ``stay-in-sync``) and whose workspace really is in a synced folder is
    asked; the answer is stored again with ``ctx.choose``.
    """
    if ctx.decision("workspace_location") != "stay-in-sync":
        return
    workspace = Path(os.path.realpath(str(ctx.workspace)))
    if _synced_folder(ctx, workspace) is None:
        return
    here = ctx.show(workspace, entrance=False)
    choice = ctx.choose(
        "学习工作区还在同步盘里（" + here + "）。第 0.2 课你选了先留在原处，现在再决定一次：",
        [("stay-in-sync", "留在原处，我知道风险：推到 GitHub 的那一份是我的备份"),
         ("move", "我要搬到 ~/Developer")],
        key="workspace_location",
        feedback={"A": "以后想搬，随时对导师说“" + MOVE_SENTENCE + "”。"})
    if choice == "move":
        ctx.fail("学习工作区还没有搬到 ~/Developer/fullstack-from-zero", where=here, saw="它还在同步盘里")
        ctx.note("对导师说“" + MOVE_SENTENCE + "”，仓库会跟着一起搬过去。搬好以后在新位置重新打开 Claude（"
                 + README_CARD + "），在那里再运行这个检查。")


def check_a(ctx):
    _workspace_committed(ctx)
    _exercise_a(ctx)
    if ctx.failed:
        ctx.stop()
    _ask_location_again(ctx)


def _secret_in_local_history(repo, token):
    """True when a commit of the local repository (pushed or not) holds ``token``."""
    history = repo.query("log", "-p", "--all", "--format=%H")
    if not history.ok:
        raise RuntimeError("cannot read the practice repository: " + history.err)
    return token in history.out


def _exercise_b(ctx, key):
    info = ctx.scenario(key)
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "练习仓库 " + facts["repo"])
    bare = ctx.git(info.path / facts["remote"])
    if not bare.is_bare or bare.ref("main") is None:
        raise RuntimeError("stand-in remote of the scenario is missing or empty")
    token = facts["token"]
    history = bare.query("log", "-p", "--all", "--format=%H")
    if not history.ok:
        raise RuntimeError("cannot read the stand-in remote: " + history.err)
    if token in history.out:
        ctx.fail("那串像密钥的内容已经推到了远程仓库", where="远程仓库的历史",
                 saw="有一个提交里带着它")
        ctx.note("真实情况下，这时第一件事是去作废这把密钥。练习可以重搭：python3 tools/course.py scenario "
                 + key + " --reset")
        ctx.stop()
    if _secret_in_local_history(repo, token):
        ctx.fail("那串像密钥的内容已经在你本地的一个提交里了，先不要推送", where="练习仓库的提交历史",
                 saw="有一个还没推送的提交里带着它")
        ctx.note("一推送它就离开了这台电脑。这一课还没学怎么改提交，重搭一份再做：python3 tools/course.py scenario "
                 + key + " --reset")
        ctx.stop()
    if repo.commit_count() <= facts["commits"]:
        ctx.fail("还没有新的提交", where="练习仓库的提交历史",
                 saw="和开始时一样，还是 " + str(facts["commits"]) + " 个提交")
        ctx.stop()
    if bare.ref("main") != repo.head:
        ctx.fail("新的提交还没有推到远程仓库", where="练习仓库的 git status 第二行",
                 saw="本地和远程的最新提交不一样")
        ctx.stop()
    ctx.ok("新的提交已经推到远程仓库，密钥没有跟着出去")
    plan = bare.file_at("main", "plan.md") or ""
    ctx.expect(facts["line"] in plan, "新加的那一行行程推上去了",
               "plan.md 里新加的那一行行程没有推上去", where="远程仓库里的 plan.md",
               saw="找不到新加的那一行")
    ctx.expect(bare.file_at("main", "packing.md") is not None, "packing.md 推上去了",
               "新文件 packing.md 还没有推上去", where="远程仓库里的文件", saw="没有 packing.md")
    status = repo.status()
    if not status.clean:
        if token in ctx.read(repo.path / "plan.md"):
            ctx.fail("plan.md 里那串像密钥的内容还在，只是没提交", where="练习仓库的 plan.md",
                     saw="git status 里 plan.md 还是已修改")
        else:
            ctx.fail("练习仓库里还有没处理的改动", where="练习仓库的 git status", saw="不是干净的")
    return facts


def check_b(ctx):
    ws = _workspace(ctx)
    remotes = ws.remotes()
    if "origin" in remotes:
        ctx.ok("学习仓库有了名叫 origin 的远程仓库")
        if "github.com" not in remotes["origin"]:
            ctx.note("origin 的地址不在 github.com 上。课文要的是你在 GitHub 上的私有仓库。")
    else:
        ctx.fail("学习仓库还没有名叫 origin 的远程仓库", where="学习仓库的 git remote -v",
                 saw=("现在有：" + "、".join(sorted(remotes))) if remotes else "一个远程仓库也没有")
    if ws.has_commits and ws.upstream():
        ctx.ok("当前分支有了上游 " + ws.upstream() + "，以后直接 git push 就行")
    elif ws.has_commits:
        ctx.fail("学习仓库的当前分支还没有上游，git push 不知道往哪推", where="学习仓库的 git status 第二行",
                 saw="没有 Your branch is up to date with 这一句")
    else:
        ctx.fail("学习仓库里还没有提交", where="学习仓库的提交历史", saw="git log 里是空的")
    _exercise_b(ctx, "1.12b")
    if not ctx.failed:
        ctx.note("检查器不联网，看不到 GitHub 上的仓库是不是私有的：命令里写了 --private 就是私有。"
                 "想亲眼确认，见第 2 站的框「旧教程和亲眼确认私有」。")


def check_c(ctx):
    ws = _workspace(ctx)
    if not ws.has_commits:
        ctx.fail("学习仓库里还没有提交", where="学习仓库的提交历史", saw="git log 里是空的")
    elif ws.upstream() is None:
        ctx.fail("学习仓库的当前分支还没有上游，备份不知道放在哪", where="学习仓库的 git status 第二行",
                 saw="没有 Your branch is up to date with 这一句")
    else:
        ahead, _behind = ws.ahead_behind() or (0, 0)
        if ahead:
            ctx.fail("学习仓库还有提交没有推送，备份不是最新的", where="学习仓库的 git status 第二行",
                     saw="比 " + ws.upstream() + " 多 " + str(ahead) + " 个提交")
        else:
            ctx.ok("学习仓库的提交都推送了，远程那一份和本地一样新")
            ctx.note("检查器不联网：它比的是你上一次推送时记下的 " + ws.upstream() + "。")
    if ctx.exists(ctx.playground / "restore-test"):
        ctx.note(ctx.show(ctx.playground / "restore-test") + " 还在。比较完就可以删掉，见课文第 3 站最后一步。")
    facts = _restored(ctx, "1.12c")
    if ctx.failed:
        ctx.stop()
    desc = facts["first_subject"].split(": ", 1)[-1]
    right = ctx.ask("在恢复出来的仓库里看提交历史：最早的那个提交，说明写的是什么？",
                    expected=lambda typed: desc in typed)
    if not right:
        others = [s.split(": ", 1)[-1] for s in facts.get("subjects", [])[1:]]
        typed = ctx.last_answer or ""
        if any(other in typed for other in others):
            ctx.note("你答的是另一个提交的说明。git log 从最新的往下排：最上面是最新的，最早的在最下面。")


checks = {"1.12a": check_a, "1.12b": check_b, "1.12c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.12a": [
        "这一站有两件事：学习工作区本身的第一次提交（跟我做），和菜谱文件夹的第一次提交（自己做）。"
        "检查结果里“还缺什么”说的是哪一个？",
        "菜谱文件夹：照 scenario 给的 cd 命令进到菜谱文件夹本身（不是上一层的 1.12a），运行 git status --ignored，"
        "看清哪些会被收进去、哪些被挡在外面。学习仓库里如果有 .gitignore 挡住的文件进了仓库，"
        "用 1.9 课的 git rm --cached <文件> 再提交。",
        "相似的例子：跟我做里给学习工作区做的第一次提交。先 git init，读 git status --ignored，git add .，"
        "再 git commit -m \"chore: 导入课程材料\"。冒号用英文半角，后面一个空格。",
        "答案：cd ~/Developer/playground/1.12a/recipes-…（按 scenario 给出的位置，进到菜谱文件夹本身），"
        "运行 git init、git status --ignored，确认 drafts/ 和 shopping.tmp 在 Ignored files 里，"
        "再运行 git add . 和 git commit -m \"docs: 导入家常菜谱\"，最后 git status 应该是干净的。"
        "如果 git init 建在了上一层的 1.12a 里，先 python3 tools/course.py scenario 1.12a --reset 重搭。"
        "解释：读过状态、.gitignore 也已经在位，git add . 才是放心的。",
    ],
    "1.12b": [
        "这一站有两件事：学习仓库推到 GitHub（跟我做），和练习仓库安全地推到它的远程仓库（自己做）。"
        "看检查结果说的是哪一件。",
        "练习仓库：照 scenario 给的 cd 命令进到 trip-… 里面。提交之前先做两步检查：git status 看有哪些改动和新文件；"
        "git grep --untracked 连新文件一起搜像密钥的词。这个仓库里没有 notes journal learner，"
        "-- 和后面的文件夹名不要写。搜到的那一行先去掉、保存、再搜一遍，然后提交和推送。",
        "相似的例子：第 1 站第 5 步的搜索。在别的仓库里它写成 git grep --untracked -n -i -E "
        "\"password|token|secret|key|密码|密钥|令牌\"（去掉了 -- 和后面的文件夹名，搜整个仓库），逐行读搜到的内容。",
        "答案：cd 进练习仓库，运行 git grep --untracked -n -i token，会搜到 plan.md 里“临时记一下”那一行；"
        "运行 code .，点开 plan.md，删掉这一行（保留新加的行程），按 ⌘S 保存；再运行一次 git grep --untracked "
        "-n -i token，什么也不打印才对；git add plan.md packing.md；git commit -m \"docs: 补上第三天和要带的东西\"；"
        "git push；git status 要说 up to date with 'origin/main'。"
        "解释：git status 只告诉你哪个文件改了，不告诉你改的内容里有没有密钥；一旦推送，删掉也收不回来。",
    ],
    "1.12c": [
        "这一站有两件事：学习仓库的备份是最新的（都推送了），和练习场里把一个项目从远程仓库恢复出来。",
        "练习：恢复就是克隆。先 cd 到 scenario 给出的练习场景文件夹，再对那个远程仓库运行 git clone；"
        "然后进入恢复出来的文件夹，用 git log --oneline 看历史。",
        "相似的例子：跟我做里把学习仓库的备份克隆到 ~/Developer/playground/restore-test，"
        "再用 git log --oneline -1 比较两边最新的提交。",
        "答案：cd ~/Developer/playground/1.12c，运行 git clone remote/album-….git（按 scenario 给出的名字），"
        "会得到 album-… 文件夹；cd 进去运行 git log --oneline，最下面一行就是最早的提交，问答题答它的说明。"
        "学习仓库还有没推送的提交，就回到学习工作区运行 git push。"
        "解释：克隆会把远程仓库的全部历史复制下来，这正是“从备份恢复”。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
def _review_restore(ctx):
    _restored(ctx, "1.12c")


REVIEW = [
    {"id": "1.12-remote", "type": "recall", "tier": "fluent", "station": "1.12b",
     "q": "远程仓库是什么？你在本机提交以后，远程仓库会自己更新吗？",
     "a": "远程仓库是放在别处（比如 GitHub）的另一份仓库。它不会自己更新：要运行 git push，把新提交推上去。",
     "rule": "REMOTE-01"},
    {"id": "1.12-push", "type": "which", "tier": "fluent", "station": "1.12b",
     "q": "学习仓库第一次推送已经做完了。今天学完、提交以后，要把新提交传到 GitHub，用哪条命令？",
     "options": ["git push", "git commit", "git clone", "gh repo create"],
     "answer": "A", "shuffle": True,
     "explain": "git commit 只在本机拍快照；gh repo create 只在第一次建远程仓库时用；git clone 是从远程复制一份下来。"},
    {"id": "1.12-ahead", "type": "predict", "tier": "fluent", "station": "1.12b",
     "q": "git status 的第二行写着：\n\n    Your branch is ahead of 'origin/main' by 1 commit.\n\n这说明什么？",
     "options": ["本机有 1 个提交还没推送到远程", "远程有 1 个提交本机还没有", "有 1 个文件还没提交"],
     "answer": "A", "shuffle": True,
     "explain": "ahead 是“领先”：本机比上次记下的 origin/main 多 1 个提交，运行 git push 才会传上去。"},
    {"id": "1.12-preflight", "type": "which", "tier": "fluent", "station": "1.12b",
     "q": "推送之前，想在仓库里搜一搜有没有像 token 这样的内容，连今天新建、还没跟踪的文件也要搜到。用哪条命令？",
     "options": ["git grep --untracked -n -i token", "git grep -n -i token", "git status"],
     "answer": "A", "rule": "REMOTE-02", "shuffle": True,
     "explain": "不加 --untracked 的 git grep 只搜已经被 Git 跟踪的文件，今天新建的文件会漏掉；"
                "git status 只说哪个文件改了，不看内容。"},
    {"id": "1.12-restore", "type": "recall", "tier": "lookup", "station": "1.12c",
     "q": "为什么说“没恢复过的备份只是愿望”？怎么验证 GitHub 上的那一份真的能用？",
     "a": "备份可能不完整、过期或者根本取不出来，只有真取一次才知道。验证：git clone 到练习场，"
          "比较两边 git log --oneline -1 的最新提交，再用 diff -r -q -x .git 比较文件，看完删掉副本。",
     "rule": "REMOTE-01"},
    {"id": "1.12-restore-do", "type": "do", "tier": "lookup", "station": "1.12c",
     "q": "一个项目原来的文件夹没了，只剩远程仓库。把它恢复到练习场里指定的位置。",
     "scenario": "1.12c", "check": _review_restore, "rule": "REMOTE-01"},
]


# ---------------------------------------------------------------------------
# EXAM (gate-1)
# ---------------------------------------------------------------------------
def build_x1(sc):
    """Push new work without letting a secret leave the machine.

    A: a token pasted into a tracked file.  B: a new untracked file holding a password.
    """
    name = sc.pick(["trip", "travel", "holiday", "tour"]) + "-" + sc.word()
    remote = _repo_with_standin(sc, name, ["docs: 开个头", "docs: 补充第二天"])
    line = sc.pick(TRIP_LINES)
    sc.fact("repo", name)
    sc.fact("remote", remote)
    sc.fact("commits", 2)
    sc.fact("line", line)
    if sc.form == "A":
        token = _fake_token(sc, "api_key = ")
        sc.append(name + "/plan.md", line + "\n" + token + "\n")
        sc.fact("token", token)
        sc.fact("secret_file", "")
    else:
        secret = sc.pick(["login.txt", "account.txt", "mail-password.txt"])
        password = _fake_token(sc, "password: ")
        sc.append(name + "/plan.md", line + "\n")
        sc.write(name + "/" + secret, password + "\n")
        sc.fact("token", password)
        sc.fact("secret_file", secret)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库 " + facts["repo"])
    bare = ctx.git(info.path / facts["remote"])
    if not bare.is_bare or bare.ref("main") is None:
        raise RuntimeError("stand-in remote of the exam task is missing")
    history = bare.query("log", "-p", "--all", "--format=%H")
    if not history.ok:
        raise RuntimeError("cannot read the stand-in remote: " + history.err)
    if facts["token"] in history.out:
        ctx.fail("密码或密钥已经推到了远程仓库", where="远程仓库的历史", saw="有一个提交里带着它")
        ctx.stop()
    if _secret_in_local_history(repo, facts["token"]):
        ctx.fail("密码或密钥在本地的一个提交里，一推送就会离开这台电脑", where="考试仓库的提交历史",
                 saw="有一个还没推送的提交里带着它")
        ctx.stop()
    if not ctx.expect(repo.commit_count() > facts["commits"], "有新的提交", "还没有新的提交",
                      where="考试仓库的提交历史", saw="提交数没有增加"):
        ctx.stop()
    ctx.expect(bare.ref("main") is not None and bare.ref("main") == repo.head,
               "新的提交已经推到远程仓库", "新的提交还没有推到远程仓库",
               where="git status 的第二行", saw="本地和远程的最新提交不一样")
    ctx.expect(facts["line"] in (bare.file_at("main", "plan.md") or ""),
               "plan.md 里新加的那一行推上去了", "plan.md 里新加的那一行没有推上去",
               where="远程仓库里的 plan.md", saw="找不到新加的那一行")
    if facts["secret_file"]:
        ctx.expect(not repo.is_tracked(facts["secret_file"]), "装着密码的文件没有进仓库",
                   "装着密码的文件进了仓库", where="考试仓库里被跟踪的文件", saw=facts["secret_file"])
    status = repo.status()
    if status.clean:
        ctx.ok("工作区是干净的")
    else:
        only_secret = facts["secret_file"] and status.untracked == [facts["secret_file"]] \
            and not status.staged and not status.unstaged
        if only_secret:
            ctx.ok("只剩那个不该进仓库的文件留在本机")
        else:
            ctx.fail("还有没处理的改动", where="考试仓库的 git status", saw="不是干净的")


def build_x2(sc):
    """Restore a project from its stand-in remote; only the target folder name differs by form."""
    base = sc.pick(["album", "journal", "recipes", "poems"]) + "-" + sc.word()
    remote = _build_standin_only(sc, base, sc.randint(2, 5))
    target = base if sc.form == "A" else "restored-" + sc.word()
    sc.fact("name", target)
    sc.fact("source", base)
    sc.fact("remote", remote)


def grade_x2(ctx):
    _restored(ctx, None)


EXAM = [
    {"id": "1.12-x1", "gate": "gate-1", "title": "推送前检查，再推送", "minutes": 8,
     "build": build_x1,
     "task": {
         "A": "仓库 {dir}/{repo} 已经推送过一次，远程仓库是 {dir}/{remote}（代替 GitHub）。"
              "把 plan.md 里新写的内容提交并推送上去，但任何像密钥的东西都不能离开这台电脑。"
              "做完以后 git status 要说和 origin/main 一样新。",
         "B": "进入 {dir}/{repo}：把 plan.md 的新改动提交并推送到它的远程仓库 {dir}/{remote}。"
              "文件夹里还有别的新文件；任何像密码、密钥的东西都不能被推送出去。推送以后本地和远程要一样新。",
     },
     "grade": grade_x1},
    {"id": "1.12-x2", "gate": "gate-1", "title": "从远程仓库恢复一个项目", "minutes": 5,
     "build": build_x2,
     "task": {
         "A": "项目 {source} 原来的文件夹没了，只剩远程仓库 {dir}/{remote}。把它恢复成 {dir}/{name}，"
              "恢复出来的历史要和远程仓库的一样。",
         "B": "只剩远程仓库 {dir}/{remote} 了。从它恢复一份完整的项目，放在 {dir}/{name}"
              "（注意文件夹名和远程仓库的名字不一样），并确认最新提交和远程的一样。",
     },
     "grade": grade_x2},
]
