"""Lesson 1.6: Git, the first commit (plan section 4, row 1.6).

Stations:
  1.6a  why version control, one-time settings, the signing blocker
  1.6b  first commits in a practice folder (init, status, add, commit, log)
  1.6c  the learner's own site becomes a repository (state S4)

Standard library only, Python 3.9 syntax.  Reference: docs/authoring/tool-api.md.
"""

import os

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.6",
    "slug": "06-first-commit",
    "title": "Git：第一次提交",
    "stage": 1,
    "prerequisites": ["1.5"],
    "stations": [
        {
            "id": "1.6a",
            "title": "为什么要版本管理，一次性设置",
            "minutes": 40,
            "new_concept": "Git 的设置分全局和单个仓库，全局设置一次管所有仓库",
            "new_commands": ["git --version", "git config get", "git config set",
                             "git commit -m", "git log --oneline"],
        },
        {
            "id": "1.6b",
            "title": "第一次提交",
            "minutes": 40,
            "new_concept": "改动先放进暂存区，再拍成提交",
            "new_commands": ["git init", "git status", "git add"],
        },
        {
            "id": "1.6c",
            "title": "给 my-site 建仓库",
            "minutes": 40,
            "new_concept": "一个项目一个仓库，建在项目的根目录",
            "new_commands": [],
        },
    ],
    "rules": ["GIT-01", "GIT-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9",
                  "code": "1.145.2", "vi": "9.1"},
    },
    "unverified_steps": [
        "1.6a：在 vi 里按 Esc、输入 :q!、按回车退出（建课环境没有真终端；按键对照建课时那台电脑上 Vim 9.1 自带的帮助 /usr/share/vim/vim91/doc/editing.txt 里的 :q[uit]!）",
        "1.6a：引号没配对时 zsh 显示 dquote> 等待，按 Ctrl+C 退出（没有真终端；非交互运行只得到 unmatched \"，提示符对照 zsh 手册 PS2 的默认值 %_> ）",
        "1.6a：core.editor 设成 code --wait 以后，Git 打开 VS Code 标签页、关掉标签页后才继续；忘了 -m 时打开的是 COMMIT_EDITMSG，不写说明就关掉会取消提交（对照 code --help 和 GitHub Docs「Associating text editors with Git」，2026-11-20 打开过；“说明是空的就取消”这一半在模拟环境里用一个不改文件的编辑器实测过）",
        "1.6b、1.6c：在 VS Code 里改 monday.txt、README.md 并保存，没保存时标签页上有圆点（1.4 学过的操作；圆点对照 VS Code Docs「Basic editing」；建课时用写文件代替，命令输出已实测）",
    ],
}

TERMS = [
    {"term": "版本管理", "en": "version control",
     "plain": "把文件夹每一次像样的状态都存下来，随时能看、能比、能退回；《Pro Git》中文版叫版本控制",
     "first": "1.6a"},
    {"term": "Git", "en": "Git",
     "plain": "这门课用的版本管理工具；通常随 Mac 的命令行开发者工具一起装上，还没有的话，第一次在终端敲 git 时 macOS 会请你安装（README「怎么拿到这门课」讲了）", "first": "1.6a"},
    {"term": "仓库", "en": "repository",
     "plain": "被 Git 管着的文件夹，隐藏的 .git 文件夹里存着全部快照", "first": "1.6a"},
    {"term": "提交", "en": "commit",
     "plain": "拍一次快照并写一句说明", "first": "1.6a"},
    {"term": "提交说明", "en": "commit message",
     "plain": "写在每个提交上的那句话，说清这次改了什么；git commit -m 后面引号里的就是",
     "first": "1.6a"},
    {"term": "HEAD", "en": "HEAD",
     "plain": "Git 用来标“你现在在哪”的记号，平时指向当前分支最新的那个提交", "first": "1.6a"},
    {"term": "全局设置", "en": "global configuration",
     "plain": "写在 ~/.gitconfig 里、对这台电脑上所有仓库都起作用的 Git 设置", "first": "1.6a"},
    {"term": "提交签名", "en": "commit signing",
     "plain": "给提交盖一个只有你能盖的章，让别人能核对这个提交确实是你做的", "first": "1.6a"},
    {"term": "参数", "en": "argument",
     "plain": "命令名后面跟着的每一个词，选项和对象都算；git config set 后面的设置名和值就是两个参数",
     "first": "1.6a"},
    {"term": "分支", "en": "branch",
     "plain": "一条历史线的名字；新仓库自带一条，这门课里叫 main", "first": "1.6a"},
    {"term": "工作区", "en": "working tree",
     "plain": "一个仓库里你正在改的那些文件，就是你在文件夹里看到的样子（不是学习工作区）",
     "first": "1.6b"},
    {"term": "暂存区", "en": "staging area",
     "plain": "准备拍进下一张快照的改动", "first": "1.6b"},
    {"term": "未跟踪", "en": "untracked",
     "plain": "在文件夹里，但 Git 还从来没有收过它的文件", "first": "1.6b"},
    {"term": "本地历史", "en": "commit history",
     "plain": "已经拍下的快照，一张接一张，存在你自己的电脑上", "first": "1.6b"},
]


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
DISHES = ["番茄炒蛋", "青椒土豆丝", "麻婆豆腐", "清炒时蔬", "红烧茄子", "酸辣汤", "葱油拌面", "蛋炒饭"]


def build_start(sc):
    """State just before 1.6: a copy of the site in state S3 (no repository yet)."""
    sc.site_before()
    sc.todo("网站的副本在这里（练习用，不是你真正的网站）：" + sc.show(sc.facts["site"]))


def build_1_6a(sc):
    """A repository with one staged file, so the learner only has to press the shutter."""
    sc.git_init("first-try")
    sc.write("first-try/hello.txt", """
        你好，Git。
        这是我拍的第一张快照。
    """)
    sc.git("first-try", "add", "hello.txt")
    sc.fact("repo", "first-try")
    sc.todo("试拍用的仓库在这里，要拍的东西已经备好了：" + sc.show("first-try"))
    sc.todo("进去：cd " + sc.show("first-try"))


def build_1_6b(sc):
    """Two plain folders: diary (worked example) and shop-<word> (the exercise)."""
    sc.write("diary/monday.txt", """
        周一：开始学 Git。
    """)
    sc.write("diary/todo.txt", """
        - 买菜
        - 交电费
    """)
    shop = "shop-" + sc.word()
    dishes = sc.sample(DISHES, 3)
    sc.write(shop + "/menu.txt", "今日菜单\n" + "".join("- " + d + "\n" for d in dishes), exact=True)
    sc.write(shop + "/draft.txt", """
        草稿：下周想加的菜，还没定，先不要让 Git 收进去。
    """)
    sc.fact("diary", "diary")
    sc.fact("shop", shop)
    sc.fact("keep", "menu.txt")
    sc.fact("skip", "draft.txt")
    sc.todo("日记文件夹 diary：" + sc.show("diary"))
    sc.todo("小店菜单文件夹：" + sc.show(shop))


SCENARIOS = {
    "start": build_start,
    "1.6a": build_1_6a,
    "1.6b": build_1_6b,
}


# ---------------------------------------------------------------------------
# Shared helpers for checks
# ---------------------------------------------------------------------------
WIDE = "“”‘’＂　"
EXAMPLE_NAMES = ("小林", "你愿意公开的名字")
EXAMPLE_EMAILS = ("xiaolin@example.com", "xiaolin.code@example.com", "你愿意公开的邮箱")


def _expand(ctx, value):
    value = (value or "").strip()
    if value.startswith("~/"):
        return str(ctx.home / value[2:])
    return value


def _config_sane(ctx):
    """Stop the check when a true/false setting holds a value Git cannot read.

    A misspelt core.quotepath breaks every git command, and a misspelt
    commit.gpgsign breaks every commit; neither is the checker's problem.
    """
    bad = False
    for key in ("commit.gpgsign", "core.quotepath"):
        if ctx.git_global_state(key) != "invalid":
            continue
        bad = True
        raw = ctx.git_global(key) or ""
        if key == "core.quotepath":
            missing = "core.quotepath 的值写错了：修好之前每条 git 命令都会失败"
        else:
            missing = "commit.gpgsign 的值写错了：修好之前每次提交都会失败"
        ctx.fail(missing, where="全局 Git 设置里的 " + key,
                 saw="值是「" + ctx.visible(raw[:20]) + "」，既不是 true 也不是 false")
        ctx.note("重新敲一次正确的命令就会盖掉错的值：git config set --global " + key
                 + " false（false 拼作 f-a-l-s-e）。")
    if bad:
        ctx.stop()


def _identity_example_note(ctx, name, email):
    if (name or "").strip() in EXAMPLE_NAMES or (email or "").strip().lower() in EXAMPLE_EMAILS:
        ctx.note("你的名字或邮箱和课文里的示例一模一样。如果是照抄的，换成你自己的（这里不显示内容）。")


def _identity_wide(name, email):
    """The identity keys that hold Chinese quotes or a full-width space (never their values)."""
    return [key for key, value in (("user.name", name), ("user.email", email))
            if any(ch in (value or "") for ch in WIDE)]


IDENTITY_FIX = ("在英文输入法下重新敲一次设置命令，新的值会盖掉旧的："
                "git config set --global user.name \"你的名字\"（邮箱是 user.email，写法一样）。")


def _subject_quote_note(ctx, repo):
    """A commit message typed with an input method's quotes keeps them: say so once."""
    for commit in repo.commits(limit=100):
        subject = (commit.subject or "").strip()
        if subject[:1] in "“‘＂" or subject[-1:] in "”’＂":
            ctx.note("有一条提交说明两头带着中文引号（「" + ctx.visible(subject[:20])
                     + "」）：中文输入法打出的引号不算引号，原样成了说明的一部分。"
                     "拍下的这一条先不用管；以后 -m 后面用英文半角引号 \"。")
            return


def _signing_state(ctx):
    """Return (works, decision, saw) for the learner's global signing setup."""
    if ctx.git_global_state("commit.gpgsign") != "true":
        return True, "off", "commit.gpgsign 不是 true"
    fmt = (ctx.git_global("gpg.format") or "openpgp").strip().lower()
    if fmt == "ssh":
        programs = ctx.git_global_all("gpg.ssh.program")
        program = programs[-1] if programs else "ssh-keygen"
        key = ctx.git_global("user.signingkey") or ""
        key_ok = key.startswith("key::") or key.startswith("ssh-") or (
            key != "" and os.path.isfile(_expand(ctx, key)))
        if program.strip() and ctx.which(_expand(ctx, program)) and key_ok:
            return True, "ssh", "SSH 签名已经配好"
        return False, None, "签名方式是 ssh，但签名程序或钥匙文件找不到"
    if fmt == "x509":
        program = ctx.git_global("gpg.x509.program") or "gpgsm"
        if ctx.which(_expand(ctx, program)):
            return True, "x509", "x509 签名程序找得到"
        return False, None, "签名方式是 x509，找不到签名程序 " + program
    program = ctx.git_global("gpg.openpgp.program") or ctx.git_global("gpg.program") or "gpg"
    if program.strip() and ctx.which(_expand(ctx, program)):
        return True, "gpg", "签名程序 " + program + " 找得到"
    return False, None, "commit.gpgsign 是 true，找不到签名程序 " + (program or "gpg")


def _fail_signing(ctx, saw):
    ctx.fail("提交签名还开着，但签名程序用不了：以后每次提交都会失败",
             where="全局 Git 设置里的 commit.gpgsign", saw=saw)


def _check_editor(ctx):
    values = ctx.git_global_all("core.editor")
    if len(values) > 1:
        ctx.fail("core.editor 有好几个值，Git 不知道用哪一个",
                 where="全局 Git 设置里的 core.editor",
                 saw="~/.gitconfig 里有 " + str(len(values)) + " 行 editor")
        ctx.note("把它们合成一个，用这一行（--all 的意思是把所有旧值都换成这一个）："
                 "git config set --global --all core.editor \"code --wait\"")
        return
    editor = (values[0] if values else "").strip()
    words = editor.split()
    first = os.path.basename(words[0]) if words else ""
    shown = "现在是「" + ctx.visible(editor[:30]) + "」"
    if not editor:
        ctx.fail("Git 要你写长说明时还会打开 vi", where="全局 Git 设置里的 core.editor",
                 saw="还没设置")
    elif any(ch in editor for ch in WIDE):
        ctx.fail("编辑器设置里有中文引号或全角空格，Git 启动不了它",
                 where="全局 Git 设置里的 core.editor", saw=shown)
        ctx.note("值两边的双引号要用英文半角 \"，在英文输入法下敲。")
    elif first in ("vi", "vim"):
        ctx.fail("Git 的编辑器还是 vi", where="全局 Git 设置里的 core.editor", saw=shown)
    elif first == "code" and not ("--wait" in words or "-w" in words):
        ctx.fail("编辑器设置里少了让 Git 等你写完的那个选项",
                 where="全局 Git 设置里的 core.editor", saw=shown)
    elif first == "code" and not ctx.which(_expand(ctx, words[0])):
        ctx.fail("Git 要启动 code，可终端里找不到 code 命令",
                 where="全局 Git 设置里的 core.editor", saw=shown + "，找不到 code")
    elif first == "code":
        ctx.ok("Git 要你写长说明时会打开 VS Code，并等你写完")
        if "-w" in words:
            ctx.note("-w 是 --wait 的简写，效果一样。")
    elif not ctx.which(_expand(ctx, words[0])):
        ctx.fail("Git 找不到这个编辑器程序", where="全局 Git 设置里的 core.editor",
                 saw=shown + "，找不到这个程序")
    else:
        ctx.ok("Git 的编辑器换成了 vi 以外的程序")
        ctx.note("课文用的是 VS Code（code --wait）。你选了「" + editor[:20] + "」，也可以。")


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def check_a(ctx):
    """One-time settings, the backup, and a first commit that works."""
    _config_sane(ctx)
    name = ctx.git_global("user.name")
    email = ctx.git_global("user.email")
    ctx.expect(bool(name) and bool(email), "Git 知道你是谁：user.name 和 user.email 都已设置",
               "Git 的身份还没设置完整", where="全局 Git 设置里的 user.name 和 user.email",
               saw="user.name " + ("已设置" if name else "还没设置") + "，user.email "
               + ("已设置" if email else "还没设置"))
    wide = _identity_wide(name, email)
    if wide:
        ctx.fail("Git 的身份里混进了中文引号或全角空格，它们会原样写进每个提交",
                 where="全局 Git 设置里的 " + " 和 ".join(wide),
                 saw=" 和 ".join(wide) + " 里有 “ ” ‘ ’ 或全角空格（这里不显示内容）")
        ctx.note(IDENTITY_FIX)
    _identity_example_note(ctx, name, email)

    backups = [n for n in ctx.listdir("~") if n.startswith(".gitconfig") and n != ".gitconfig"
               and ctx.is_file("~/" + n) and (ctx.size("~/" + n) or 0) > 0]
    if backups:
        ctx.ok("改设置之前留了备份：~/" + backups[0])
    else:
        ctx.fail("还没有给 ~/.gitconfig 留一份备份", where="你的主文件夹 ~",
                 saw="没有名字以 .gitconfig 开头的备份文件")

    works, decision, saw = _signing_state(ctx)
    if works:
        ctx.ok("提交签名不会再挡住提交")
    else:
        _fail_signing(ctx, saw)

    _check_editor(ctx)
    branch = (ctx.git_global("init.defaultBranch") or "").strip()
    if branch and branch != "main":
        ctx.note("你的全局设置里，新仓库的第一个分支名是「" + ctx.visible(branch[:20])
                 + "」，这门课后面写的都是 main。想换成 main："
                 "git config set --global init.defaultBranch main")

    info = ctx.scenario("1.6a")
    repo = ctx.need_repo(info.path / info.facts["repo"], "试拍用的仓库 first-try")
    ctx.expect(repo.has_commits, "试拍成功了：first-try 里有了第一个提交",
               "试拍用的仓库里还没有提交", where=info.path.name + "/first-try 的历史",
               saw="一个提交也没有")
    if repo.has_commits:
        _subject_quote_note(ctx, repo)

    if decision and not ctx.failed:
        ctx.decide("commit_signing", decision)
        if decision == "off":
            ctx.note("你的决定记下了：提交签名先关着，第 1.11 课再回来选。")


def _wrapped_note(ctx, info, folder):
    """A git init one level too high: say exactly how to start over."""
    probe = ctx.git(info.path / folder)
    if not probe.exists or probe.is_repo or not probe.inside_repo:
        return
    top = os.path.realpath(str(probe.toplevel or ""))
    base = os.path.realpath(str(info.path))
    inside_scenario = top == base or top.startswith(base + os.sep)
    if inside_scenario and info.path == ctx.playground / "1.6b":
        ctx.note("多出来的那个仓库在练习场里，不用自己删。重搭一份再做："
                 "python3 tools/course.py scenario 1.6b --reset（diary 也会重搭，shop- 后面的词会变），"
                 "这一次先 cd 进 shop- 开头的文件夹，pwd 确认以后再 git init。")
    elif inside_scenario:
        ctx.note("多出来的那个仓库在这道题的文件夹里。这一题可以运行 "
                 "python3 tools/course.py review --give-up，明天重做。")
    else:
        ctx.note("多出来的那个仓库建在这个练习场景的外面，先什么都不要删，"
                 "对导师说“急救：git init 建错了地方”，并把这一段发过去。")


def _shop_done(ctx):
    """Shared by the station check and the do review item."""
    _config_sane(ctx)
    info = ctx.scenario()
    shop = info.facts["shop"]
    keep = info.facts["keep"]
    skip = info.facts["skip"]
    _wrapped_note(ctx, info, shop)
    repo = ctx.need_repo(info.path / shop, "小店菜单文件夹 " + shop, praise=True)
    if not repo.has_commits:
        ctx.fail("仓库建好了，但还没有任何提交", where=shop + " 的历史", saw="一个提交也没有")
        ctx.stop()
    if repo.is_tracked(skip):
        ctx.fail(skip + " 被收进了仓库，它应该留在外面", where="仓库里被跟踪的文件",
                 saw=skip + " 在里面")
        if info.path == ctx.playground / "1.6b":
            ctx.note("已经拍进历史的东西，这一课还不教怎么拿出来。重搭一份再做："
                     "python3 tools/course.py scenario 1.6b --reset（diary 也会重搭，"
                     "shop- 后面的词会变），这一次按名字 git add。")
        else:
            ctx.note("已经拍进历史的东西，这一课还不教怎么拿出来。这一题可以运行 "
                     "python3 tools/course.py review --give-up，明天重做。")
    else:
        ctx.ok(skip + " 没有被收进仓库")
    if repo.file_at("HEAD", keep) is None:
        ctx.fail(keep + " 还没有进入提交", where="最新的提交", saw="里面没有 " + keep)
        ctx.stop()
    ctx.ok(keep + " 已经提交了")
    _subject_quote_note(ctx, repo)
    status = repo.status()
    leftover = status.staged + status.unstaged
    others = [p for p in status.untracked if p != skip]
    if leftover:
        ctx.fail("还有改动没有拍进提交", where="git status",
                 saw="、".join(leftover[:3]) + " 有没提交的改动")
    elif others:
        ctx.fail("文件夹里多了 Git 没收的文件", where="git status 的 Untracked files",
                 saw="、".join(others[:3]))
    elif not repo.is_tracked(skip):
        ctx.ok("git status 里只剩 " + skip + " 没被收")
    return repo


def check_b(ctx):
    _shop_done(ctx)


SITE_OUTER_NOTE = ("外层那个仓库多半是一次放错地方的 git init。先什么都不要删，也不要再运行 git init，"
                   "对导师说“急救：my-site 已经在一个仓库里了”，并把这一段发过去。")


def check_c(ctx):
    _config_sane(ctx)
    site = ctx.my_site
    probe = ctx.git(site)
    if probe.exists and probe.inside_repo and not probe.is_repo:
        ctx.note(SITE_OUTER_NOTE)
    repo = ctx.need_repo(site, "你的网站文件夹 ~/Developer/my-site", praise=True)
    outer = ctx.git(site.parent)
    if outer.exists and outer.inside_repo:
        ctx.fail("my-site 的仓库外面还套着一个仓库：一个项目应该只有一个仓库",
                 where="~/Developer/my-site 的上层文件夹",
                 saw="外层仓库的顶层是 " + ctx.show(outer.toplevel or site.parent))
        ctx.note(SITE_OUTER_NOTE)
    if not repo.has_commits:
        ctx.fail("仓库建好了，但还没有提交", where="my-site 的历史", saw="一个提交也没有")
        ctx.stop()
    names = ["index.html", "README.md"]
    for optional in ("style.css", ".editorconfig"):
        if ctx.is_file(site / optional):
            names.append(optional)
    missing = [n for n in names if not repo.is_tracked(n)]
    if missing:
        ctx.fail("网站的文件还没有全部收进仓库", where="my-site 里被跟踪的文件",
                 saw="、".join(missing) + " 不在里面")
    else:
        ctx.ok("、".join(names) + " 都在仓库里了")
    commits = repo.commits(limit=100)
    readme = False
    if len(commits) < 2:
        ctx.fail("自己做的那一次提交还没有：仓库里只有第一个提交", where="my-site 的历史",
                 saw="只有 " + str(len(commits)) + " 个提交")
    else:
        later = [c for c in commits if c.parents]
        readme = any(any(n == "README.md" for _l, n in repo.changed_files(c.hash)) for c in later)
        ctx.expect(readme, "第一个提交之后，README.md 又改过并提交了",
                   "README.md 改过以后还没有提交", where="第一个提交之后的那些提交",
                   saw="里面都没有动过 README.md")
    status = repo.status()
    if status.clean:
        if readme:
            ctx.ok("my-site 现在是干净的：所有改动都拍进了提交")
        else:
            ctx.note("如果你已经改过 README.md：git status 却是干净的，多半是还没保存。"
                     "VS Code 标签页上有圆点 ● 就是没存，按 ⌘S。")
    else:
        shown = [e.path for e in status.entries][:3]
        ctx.fail("my-site 里还有没处理的改动", where="git status", saw="、".join(shown))
        if status.untracked:
            ctx.note("没被收的文件如果是网站的一部分，就按名字 git add 再提交；"
                     "不是的话先别删，问导师（第 1.9 课讲怎么让 Git 不管它）。")
    _subject_quote_note(ctx, repo)
    works, _decision, saw = _signing_state(ctx)
    if not works:
        _fail_signing(ctx, saw)
    name = ctx.git_global("user.name")
    email = ctx.git_global("user.email")
    if not (name and email):
        ctx.fail("Git 的身份设置不完整：以后的提交会写进一个 Git 自己拼出来的身份",
                 where="全局 Git 设置里的 user.name 和 user.email",
                 saw="user.name " + ("已设置" if name else "还没设置") + "，user.email "
                 + ("已设置" if email else "还没设置"))
        ctx.note("设法和第 1 站一样：git config set --global user.name \"你的名字\"（邮箱是 user.email）。")
    elif _identity_wide(name, email):
        ctx.note("你的 " + " 和 ".join(_identity_wide(name, email))
                 + " 里有中文引号或全角空格（这里不显示内容），以后的提交会原样写上它们。" + IDENTITY_FIX)
    _identity_example_note(ctx, name, email)
    if repo.branch and repo.branch != "main":
        ctx.note("你的分支名是「" + repo.branch + "」，课程后面写的是 main。拿不准就问导师。")


checks = {"1.6a": check_a, "1.6b": check_b, "1.6c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.6a": [
        "这一站要留下三样东西：一份 ~/.gitconfig 的备份，几条全局设置，一次成功的试拍。检查结果的“还缺什么”说的是哪一样？",
        "写设置都是同一个形状：git config set --global <设置名> <值>（尖括号连同里面的字换成真的内容）。自己做的设置名在「自己做」那张表的第一列。想看某一项现在是什么，用 git config get <设置名>。",
        "相似的例子：跟我做里关掉签名，敲的是 git config set --global commit.gpgsign false。值里有空格时，整个值要用英文半角双引号括起来。",
        ("答案：先 cp ~/.gitconfig ~/.gitconfig.backup-2026-11-20（日期换成今天）留备份；"
         "git config get user.name 和 git config get user.email 如果什么都不打印，"
         "就用 git config set --global user.name \"你的名字\" 和 git config set --global user.email \"你的邮箱\" 设上；"
         "git config set --global commit.gpgsign false；cd 进练习场的 first-try，运行 git commit -m \"第一次试拍\"；"
         "然后 git config set --global core.editor \"code --wait\"，再用 git config get core.editor 读一次。"
         "解释：--global 表示写进 ~/.gitconfig、对所有仓库起作用；"
         "code 后面的 --wait 让 Git 等你关掉 VS Code 的标签页再继续；"
         "签名关掉以后，提交不再去找不存在的 gpg。"),
    ],
    "1.6b": [
        "一共三件事：把文件夹变成仓库，只把该收的文件放进暂存区，提交。检查结果的“还缺什么”说的是哪一件？",
        "先确认你站在对的文件夹里：pwd 的最后一段要是 shop- 开头的那个文件夹。再运行 git status，看每个文件在哪一段：Untracked files 还是 Changes to be committed。",
        "相似的例子：跟我做里的 diary 文件夹，只 git add 了 monday.txt，todo.txt 一直留在 Untracked files 里。",
        ("答案：cd 进 shop- 开头的文件夹，pwd 确认最后一段对，git init；git add menu.txt；git commit -m \"添加今日菜单\"；"
         "git status 确认只剩 draft.txt 是未跟踪的。"
         "解释：git add 只点名 menu.txt，draft.txt 就一直留在外面；"
         "用 git add . 会把 draft.txt 一起放进暂存区，这正是要避免的事故。"
         "已经把 draft.txt 拍进去了：运行 python3 tools/course.py scenario 1.6b --reset 重搭一份"
         "（shop- 后面的词会变），再按名字做一遍。"),
    ],
    "1.6c": [
        "这一站至少要两个提交：第一版网页，和你自己改 README.md 的那一次（多拍过快照的也算对）。检查结果的“还缺什么”说的是哪一个？",
        "在 ~/Developer/my-site 里运行 git status 和 git log --oneline：前者告诉你还有什么没拍进去，后者告诉你已经拍了几张。改了 README.md，git status 里却没有 modified: README.md？多半是没保存：VS Code 标签页上有圆点 ● 就是没存，按 ⌘S。提交时出现 error: pathspec？看看 -m 后面的引号是不是英文半角的 \"。",
        "相似的例子：第 2 站 diary 里的第二次提交，就是“改一个已经提交过的文件，再 git add、git commit 一次”。",
        ("答案：cd ~/Developer/my-site；ls -a；git status 看到 not a git repository；git init；"
         "git add .editorconfig index.html style.css README.md（ls -a 里还有别的网站文件就一起写上）；"
         "git commit -m \"第一版网页\"；然后在 README.md 里加一句“这个网站现在用 Git 记录每一次改动。”并按 ⌘S 保存；"
         "git add README.md；git commit -m \"在 README 里写上用 Git 记录改动\"；"
         "最后 git status 要显示 nothing to commit, working tree clean。"
         "解释：仓库建在 my-site 这一层（项目根目录），一个项目一个仓库；每改完一件事就拍一张快照。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {
        "id": "1.6-r1", "type": "recall", "tier": "fluent", "station": "1.6b",
        "q": "在 Git 里，git add 和 git commit 各做什么？为什么提交之前要多 git add 这一步？",
        "a": "git add 把改动放进暂存区；git commit 把暂存区里的东西拍成一张快照。多这一步，是为了挑出这一次要拍的改动，不把手头所有东西一股脑拍进去。",
    },
    {
        "id": "1.6-r2", "type": "predict", "tier": "fluent", "station": "1.6b",
        "q": "你在一个仓库里新建了 notes.txt，还没有 git add。运行 git status，它会出现在哪一段下面？",
        "options": ["Untracked files", "Changes to be committed", "Changes not staged for commit"],
        "answer": "A",
        "explain": "Git 从来没收过的新文件叫“未跟踪”。Changes not staged for commit 是 Git 已经收过、后来又改了但还没 git add 的文件。",
    },
    {
        "id": "1.6-r3", "type": "fault", "tier": "fluent", "station": "1.6c", "rule": "GIT-01",
        "q": "有人想把 ~/Developer 下面的 my-site 和 playground 一起管起来，于是这样做了。哪里不对？\n\n    cd ~/Developer\n    git init",
        "options": ["仓库建得太高了，应该进 my-site 再建",
                    "应该先 git add，再 git init",
                    "应该进 playground 里再 git init"],
        "answer": "A",
        "explain": "仓库建在哪一层，就管那一层下面的所有东西：在 ~/Developer 建，每个项目都会变成这个大仓库里的一个文件夹。一个项目一个仓库，建在项目自己的文件夹里；git init 本来就是第一步；playground 是练习场，不是要管的项目。",
    },
    {
        "id": "1.6-r4", "type": "which", "tier": "lookup", "station": "1.6a", "rule": "GIT-02",
        "q": "在一台 Mac 上，user.name 和 user.email 都没设置就运行 git commit，结果会怎样？",
        "options": ["Git 拒绝提交，什么也不记",
                    "提交成功，Git 用你登录这台 Mac 的全名和“用户名@电脑名.local”拼一个身份写进提交",
                    "提交成功，作者一栏留空"],
        "answer": "B",
        "explain": "建课当天在 Git 2.54 上实测：提交照样成功，只多一段英文提醒。拼出来的身份会写进提交，公开以后谁都看得到，所以提交前先确认身份。",
    },
    {
        "id": "1.6-r5", "type": "recall", "tier": "lookup", "station": "1.6a",
        "q": "终端里突然进了 vi（屏幕上是一个文件，最下面一行有文件名，打字没反应或乱跳）。怎么不保存直接出来？",
        "a": "按 Esc，输入 :q!（冒号、q、感叹号，都是英文半角），按回车。如果是 git commit 打开的，退出后提交会被取消。",
    },
    {
        "id": "1.6-d1", "type": "do", "tier": "fluent", "station": "1.6b",
        "q": "练习场里有一个 shop- 开头的文件夹，还不是仓库。把它变成仓库，只提交 menu.txt；draft.txt 留在仓库外面。",
        "scenario": "1.6b", "check": _shop_done,
    },
]


# ---------------------------------------------------------------------------
# EXAM (gate-b)
# ---------------------------------------------------------------------------
X1_FILES = {
    "A": {"keep": ["plan.txt", "goals.txt", "reading.txt"], "skip": ["scratch.txt", "temp-notes.txt"]},
    "B": {"keep": ["index.html", "about.html"], "skip": ["mockup-old.html", "ideas.txt"]},
}


def build_x1(sc):
    """A plain folder: some files belong in the first commit, one does not."""
    folder = ("notes-" if sc.form == "A" else "page-") + sc.word()
    skip = sc.pick(X1_FILES[sc.form]["skip"])
    if sc.form == "A":
        keep = [sc.pick(X1_FILES["A"]["keep"])]
        sc.write(folder + "/" + keep[0], "这周的计划：每天学 30 分钟。")
    else:
        keep = list(X1_FILES["B"]["keep"])
        sc.write(folder + "/index.html", "<h1>首页</h1>")
        sc.write(folder + "/about.html", "<h1>关于我</h1>")
    sc.write(folder + "/" + skip, "还没想好，先别收进去。")
    sc.fact("folder", folder)
    sc.fact("keep", keep)
    sc.fact("keep_text", "、".join(keep))
    sc.fact("skip", skip)


def grade_x1(ctx):
    _config_sane(ctx)
    info = ctx.scenario()
    folder = info.facts["folder"]
    repo = ctx.need_repo(info.path / folder, "考试文件夹 " + folder, praise=True)
    if not repo.has_commits:
        ctx.fail("还没有任何提交", where=folder + " 的历史", saw="一个提交也没有")
        ctx.stop()
    for name in info.facts["keep"]:
        ctx.expect(repo.file_at("HEAD", name) is not None, name + " 已经提交",
                   "要求提交的文件还没有进入提交", where="最新的提交", saw="里面没有 " + name)
    skip = info.facts["skip"]
    ctx.expect(not repo.is_tracked(skip), skip + " 留在了仓库外面",
               "不该提交的文件被收进了仓库", where="仓库里被跟踪的文件", saw=skip + " 在里面")
    status = repo.status()
    others = [p for p in status.untracked if p != skip]
    if status.staged or status.unstaged:
        ctx.fail("还有改动没有拍进提交", where="git status", saw="有已暂存或已修改的文件")
    elif info.form == "B" and others:
        ctx.fail("git status 里除了 " + skip + " 还有没被收的文件", where="git status 的 Untracked files",
                 saw="、".join(others[:3]))
    elif not ctx.failed:
        ctx.ok("没有落下没提交的改动")


TODO_ITEMS = ["复习 git status", "整理书桌", "给植物浇水", "读完第二章", "备份照片"]
NEW_FILES = ["shopping.txt", "ideas.txt", "contacts.txt"]


def build_x2(sc):
    """A repository with one commit; the learner records one more change."""
    repo = "log-" + sc.word()
    sc.git_init(repo)
    sc.write(repo + "/todo.txt", "- 学 Git\n", exact=True)
    sc.git_commit(repo, "添加待办清单")
    sc.fact("repo", repo)
    sc.fact("commits", 1)
    if sc.form == "A":
        sc.fact("item", sc.pick(TODO_ITEMS))
    else:
        sc.fact("newfile", sc.pick(NEW_FILES))


def grade_x2(ctx):
    _config_sane(ctx)
    info = ctx.scenario()
    name = info.facts["repo"]
    repo = ctx.need_repo(info.path / name, "考试仓库 " + name)
    if repo.commit_count() > info.facts["commits"]:
        ctx.ok("有了新的提交")
    else:
        ctx.fail("还没有新的提交", where=name + " 的历史", saw="还是只有 1 个提交")
        ctx.stop()
    if info.form == "A":
        text = repo.file_at("HEAD", "todo.txt") or ""
        ctx.expect(info.facts["item"] in text, "新的待办已经在最新的提交里",
                   "最新提交里的 todo.txt 还没有题目要求的那一条", where="最新提交里的 todo.txt",
                   saw="没有找到要求加的那一条")
    else:
        new = info.facts["newfile"]
        text = repo.file_at("HEAD", new)
        if text is None:
            ctx.fail("新文件还没有进入提交", where="最新的提交", saw="里面没有 " + new)
        else:
            ctx.expect(text.strip() != "", new + " 已经在最新的提交里，里面有字",
                       "提交里的 " + new + " 是空的", where="最新提交里的 " + new,
                       saw="一个字也没有")
    status = repo.status()
    if status.staged or status.unstaged:
        ctx.fail("还有改动没有拍进提交", where="git status",
                 saw="、".join((status.staged + status.unstaged)[:3]) + " 有没提交的改动")
    elif status.untracked:
        ctx.fail("git status 还不是干净的：文件夹里有 Git 没收的文件", where="git status 的 Untracked files",
                 saw="、".join(status.untracked[:3]))
    else:
        ctx.ok("git status 是干净的：没有落下没提交的改动")


EXAM = [
    {
        "id": "1.6-x1", "gate": "gate-b", "title": "给文件夹建仓库，只提交该提交的文件", "minutes": 5,
        "build": build_x1,
        "task": {
            "A": "先 cd 进 {dir}/{folder}：这个文件夹还不是仓库。把它变成仓库，并提交 {keep_text}；{skip} 不能进仓库。",
            "B": "先 cd 进 {dir}/{folder}，把这个文件夹建成 Git 仓库。提交里要有 {keep_text} 这两个文件，{skip} 留在仓库外面。做完以后，git status 里只剩 {skip} 没被收。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.6-x2", "gate": "gate-b", "title": "做一处改动并再提交一次", "minutes": 4,
        "build": build_x2,
        "task": {
            "A": "先 cd 进 {dir}/{repo}：这个仓库里已经有 1 个提交。在 todo.txt 里加一行「- {item}」，然后把这处改动提交。做完以后 git status 要是干净的。",
            "B": "先 cd 进 {dir}/{repo}：这个仓库里已经有 1 个提交。新建文件 {newfile}，在里面写一行字，然后提交它。做完以后 git status 要是干净的。",
        },
        "grade": grade_x2,
    },
]
