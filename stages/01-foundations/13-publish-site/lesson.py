"""Lesson 1.13: 把你的网页放到网上 (plan section 4, task T2).

Stations
  1.13a  公开仓库和许可证        LICENSE + README section, committed (PUB-01)
  1.13b  用 GitHub Pages 上线    public repository, Pages, address in README
  1.13c  改一处、推送、看网页更新  the delivery loop: change, diff, commit, push, reload

The station checks look at the learner's real site, ~/Developer/my-site
(state S6 before the lesson, S7 after it; plan I6).  They never use the
network: "online" is judged from the local repository (a GitHub remote named
origin, the remote-tracking branch origin/main equal to HEAD) and from an ask
check whose expected address is computed from the learner's own remote URL.

Standard library only; must import on Python 3.9.
"""

import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.13",
    "slug": "13-publish-site",
    "title": "把你的网页放到网上",
    "stage": 1,
    "prerequisites": ["1.12"],
    "stations": [
        {
            "id": "1.13a",
            "title": "公开仓库和许可证",
            "minutes": 40,
            "new_concept": "许可证写明别人可以怎样使用你的作品；没有许可证就是保留所有权利",
            "new_commands": [],
        },
        {
            "id": "1.13b",
            "title": "用 GitHub Pages 上线",
            "minutes": 40,
            "new_concept": "上线：让一台一直开着的电脑把你仓库里的网页发给任何来访的人",
            "new_commands": ["gh repo create --public", "gh browse --settings"],
        },
        {
            "id": "1.13c",
            "title": "改一处、推送、看网页更新",
            "minutes": 35,
            "new_concept": "交付循环：改动、看改动清单、提交、推送、确认上线，一圈接一圈",
            "new_commands": [],
        },
    ],
    "rules": ["PUB-01"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "gh": "2.105.0", "macos": "27.2.1", "zsh": "5.9",
                  "python3": "3.14.9"},
    },
    "unverified_steps": [
        "1.13a 在浏览器里打开 choosealicense.com 的 MIT 页，复制许可证全文（对照 choosealicense.com，2026-11-20）",
        "1.13a 在 VS Code 里点开 LICENSE、粘贴、按 ⌘S 保存（对照文档；文件内容本身在模拟环境里实测）",
        "1.13b gh repo create my-site --public --source=. --remote=origin --push 和没登录时它的提示（需要账号和网络；对照 GitHub CLI 手册 gh repo create）",
        "1.13b git remote -v 里 push 那一行的地址（模拟环境推到本地的替身远程仓库）",
        "1.13b gh browse --settings 打开仓库设置页，Pages → Build and deployment → Source: Deploy from a branch → main、/ (root) → Save（对照 GitHub CLI 手册 gh browse 和 GitHub Docs 'Configuring a publishing source'）",
        "1.13b 等待发布（GitHub Docs：最长约 10 分钟）、Visit site、用手机打开网页；没发布好时看到的 404 页面",
        "1.13c git push 推到 GitHub 的 To 那一行地址（模拟环境推到本地的替身远程仓库，输出的其余部分实测）",
        "1.13c 推送后按 ⌘R 刷新网页看到变化",
        "想多了解：Render 的免费静态网站（对照 render.com/docs/static-sites）",
    ],
}

TERMS = [
    {"term": "许可证", "en": "license",
     "plain": "写明别人可以怎样使用你作品的一份声明，通常放在仓库根目录的 LICENSE 文件里",
     "first": "1.13a"},
    {"term": "版权", "en": "copyright",
     "plain": "作者对自己作品天然拥有的权利；没有许可证时，别人不能复制、修改、分发",
     "first": "1.13a"},
    {"term": "MIT 许可证", "en": "MIT License",
     "plain": "一种有名字的宽松许可证，全文只有一页：别人几乎可以随意使用，只要保留你的版权声明，你也不承担责任",
     "first": "1.13a"},
    {"term": "上线", "en": "deploy",
     "plain": "把作品放到一台一直开着的电脑上，让别人通过网址访问；也叫部署",
     "first": "1.13b"},
    {"term": "静态网站", "en": "static site",
     "plain": "只有现成的网页文件、不需要在服务器上运行程序的网站，比如 my-site",
     "first": "1.13b"},
    {"term": "GitHub Pages", "en": "GitHub Pages",
     "plain": "GitHub 提供的免费网页托管：把仓库里的网页文件发布成一个网址",
     "first": "1.13b"},
    {"term": "交付循环", "en": "delivery loop",
     "plain": "改动、看改动清单、提交、推送、确认上线，这一圈反复做；以后的阶段会让机器替你做其中几步",
     "first": "1.13c"},
]

# ---------------------------------------------------------------------------
# helpers shared by the checks
# ---------------------------------------------------------------------------
LICENSE_NAMES = ("LICENSE", "LICENSE.txt", "LICENSE.md")
PLACEHOLDERS = ("[year]", "[fullname]")
# "Copyright (c) 2026 阿木", also "(C)", "©", a year range and extra spaces; not "[2026] [阿木]".
COPYRIGHT_FILLED = re.compile(
    r"^\s*Copyright\s*(?:\([cC]\)|©)?\s*\d{4}(?:\s*[-–,]\s*\d{4})?\s+[^\s\[]", re.MULTILINE)
NOREPLY = re.compile(r"@users\.noreply\.github\.com$", re.IGNORECASE)
CONVENTIONAL = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?!?: \S")
GITHUB_URL = re.compile(
    r"^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
    r"([A-Za-z0-9-]+)/([A-Za-z0-9._-]+?)(?:\.git)?/?$")


def _site(ctx):
    return ctx.need_repo(ctx.my_site, "你的网站文件夹 my-site")


def _at(label, text):
    """Join a label and a Chinese phrase: one space only after Latin letters (plan G2)."""
    return label + (" " if label[-1:].isascii() else "") + text


def _license_name(ctx, folder):
    """The exact name of the licence file in ``folder``, or None."""
    names = ctx.listdir(folder)
    for name in LICENSE_NAMES:
        if name in names:
            return name
    return None


def _look_like_license(ctx, folder):
    """Names that look like a licence file but are spelt differently."""
    return [name for name in ctx.listdir(folder)
            if name.lower().startswith(("licen", "copying")) or name.startswith("许可")]


def _check_license(ctx, repo, label="my-site"):
    """LICENSE present, filled in, committed.  Returns the file name or None."""
    name = _license_name(ctx, repo.path)
    if name is None:
        odd = _look_like_license(ctx, repo.path)
        case_only = [n for n in odd if n.lower() in [x.lower() for x in LICENSE_NAMES]]
        if case_only:
            wrong = case_only[0]
            base, dot, ext = wrong.partition(".")
            right = base.upper() + dot + ext
            if repo.is_tracked(wrong):
                ctx.fail("许可证文件名的大小写不对。Mac 上只改大小写，Git 看不出来，"
                         "要在这个文件夹里用 git mv " + wrong + " " + right + " 改名，再提交",
                         where=_at(label, "文件夹的第一层"), saw="文件叫 " + wrong + "，已经提交过")
            else:
                ctx.fail("许可证文件名的大小写不对：要全部大写",
                         where=_at(label, "文件夹的第一层"), saw="文件叫 " + wrong)
        elif odd:
            move = "git mv" if repo.is_tracked(odd[0]) else "mv"
            shown = "'" + odd[0] + "'" if re.search(r"[^\w.-]", odd[0], re.ASCII) else odd[0]
            ctx.fail("许可证文件的名字和课文的写法不一样：在这个文件夹里用 " + move + " " + shown
                     + " LICENSE 改名" + ("，再提交" if move == "git mv" else ""),
                     where=_at(label, "文件夹的第一层"), saw="有 " + odd[0] + "，没有拼成 LICENSE 的文件")
        else:
            ctx.fail("还没有许可证文件", where=_at(label, "文件夹的第一层"), saw="没有 LICENSE")
        return None
    text = ctx.read(repo.path / name)
    if len(text.strip()) < 100:
        ctx.fail("许可证文件里几乎没有内容（在 VS Code 里保存了吗？）", where=label + "/" + name,
                 saw="只有 {} 个字符".format(len(text.strip())))
        return name
    left = [mark for mark in PLACEHOLDERS if mark in text]
    if left:
        ctx.fail("许可证里还有没替换的占位符", where=label + "/" + name + " 的版权那一行",
                 saw="还有 " + "、".join(left))
    elif text.lstrip().startswith("MIT License") and not COPYRIGHT_FILLED.search(text):
        lines = [line.strip() for line in text.splitlines() if line.strip().lower().startswith("copyright")]
        ctx.fail("版权那一行没有写成「Copyright (c) 年份 名字」的样子",
                 where=label + "/" + name + " 的版权那一行",
                 saw=("现在是「" + ctx.visible(lines[0][:60]) + "」") if lines else "没有以 Copyright 开头的一行")
    else:
        ctx.ok(name + " 里的占位符都已经换成了年份和名字")
    if repo.file_at("HEAD", name) is None:
        other = [path for path in repo.tracked() if path.lower() == name.lower() and path != name]
        if other:
            ctx.fail("Git 里记的许可证文件名大小写不对。Mac 上只改大小写，Git 看不出来，"
                     "要在这个文件夹里运行 git mv " + other[0] + " " + name + "，再提交",
                     where=_at(label, "里被跟踪的文件"), saw="Git 记的名字是 " + other[0])
        else:
            ctx.fail(name + " 还没有进入提交", where=_at(label, "的最新提交"), saw="里面没有 " + name)
    else:
        ctx.ok(name + " 已经提交")
    return name


# An inline link, also with a title: [LICENSE](LICENSE "许可证") or [LICENSE](<LICENSE> '许可证').
MD_LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")


def _readme_links_license(ctx, text, name, label="my-site/README.md"):
    """A Markdown link whose target ends in the licence file name, same letter case."""
    ends = [target.rstrip("/").rsplit("/", 1)[-1] for target in MD_LINK.findall(text)]
    if name in ends:
        return ctx.ok("README.md 里有指向 " + name + " 的链接")
    near = [end for end in ends if end.lower() == name.lower()]
    if near:
        return ctx.fail("README.md 里链接的文件名大小写和 " + name + " 不一样", where=label,
                        saw="链接写的是 " + near[0])
    return ctx.fail("README.md 里还没有指向 " + name + " 的链接", where=label,
                    saw="没有找到链接到 " + name + " 的 Markdown 链接")


def _subject_ok(ctx, subject, what, strict=True):
    """Conventional Commits subject.  ``strict=False`` only notes a miss: an
    existing commit message cannot be changed before stage 2 (no amend yet)."""
    if CONVENTIONAL.match(subject or ""):
        ctx.ok(what + "的说明符合约定式提交")
    elif strict:
        ctx.fail(what + "的说明开头缺类型前缀", where=what + "的第一行",
                 saw="现在是「{}」".format((subject or "")[:30]))
    else:
        ctx.note("{}的说明是「{}」，开头没有类型前缀。已经提交的说明先不用改，下一次提交记得按约定式提交写。".format(
            what, (subject or "")[:30]))


def _expect_clean(ctx, repo, label="my-site"):
    status = repo.status()
    if status.clean:
        return True
    ctx.fail("还有改动没有提交", where=_at(label, "里的 git status"),
             saw="有 {} 个文件是新加的或改过的，还没提交".format(len(status.entries)))
    return False


def _parse_github(url):
    match = GITHUB_URL.match((url or "").strip())
    if not match:
        return None
    return match.group(1), match.group(2)


def _github_origin(ctx, repo):
    """(owner, name) of the GitHub remote ``origin``; records a fail otherwise."""
    remotes = repo.remotes()
    url = remotes.get("origin")
    if not url:
        saw = "没有任何远程仓库" if not remotes else "只有 " + "、".join(sorted(remotes))
        ctx.fail("还没有叫 origin 的远程仓库", where="my-site 的远程仓库列表", saw=saw)
        return None
    parsed = _parse_github(url)
    if parsed is None:
        ctx.fail("origin 指向的不是 GitHub 上的一个仓库", where="origin 的地址",
                 saw=url[:60])
        return None
    ctx.ok("my-site 有远程仓库 origin，在 GitHub 上")
    return parsed


def _expect_pushed(ctx, repo):
    """HEAD equals the remote-tracking branch origin/<branch> (the last push)."""
    branch = repo.branch or "main"
    remote_head = repo.ref("refs/remotes/origin/" + branch)
    if remote_head is None:
        ctx.fail("还没有把 " + branch + " 推送到 origin", where="本地记下的远程分支 origin/" + branch,
                 saw="一次推送都没有记录")
        return False
    if remote_head == repo.head:
        ctx.ok("所有提交都已经推送，和 origin/" + branch + " 一致")
        return True
    ahead = repo.query("rev-list", "--count", "origin/" + branch + "..HEAD").out.strip()
    ctx.fail("还有提交没有推送", where="git status 的第二行",
             saw="本地比 origin/{} 多 {} 个提交".format(branch, ahead or "几"))
    return False


def _pages_re(owner, name):
    return re.compile(r"(?:https?://)?" + re.escape(owner.lower()) + r"\.github\.io/"
                      + re.escape(name.lower()) + r"(?:/(?:index\.html)?)?", re.IGNORECASE)


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def check_a(ctx):
    """LICENSE, README with a licence section, .gitignore: all committed (PUB-01)."""
    repo = _site(ctx)
    name = _check_license(ctx, repo)

    readme = repo.path / "README.md"
    if ctx.expect_file(readme, "my-site 里的 README.md"):
        text = ctx.read(readme)
        if re.search(r"licen[sc]e|许可", text, re.IGNORECASE):
            ctx.ok("README.md 里提到了许可证")
            if name is not None:
                _readme_links_license(ctx, text, name)
        else:
            ctx.fail("README.md 里还没有写许可证", where="my-site/README.md",
                     saw="没有提到许可证，也没有提到 LICENSE")
    if repo.is_tracked(".gitignore"):
        ctx.ok(".gitignore 在仓库里")
    else:
        ctx.fail("仓库里没有 .gitignore", where="my-site 里被跟踪的文件", saw="没有 .gitignore")

    if name is not None and repo.file_at("HEAD", name) is not None:
        # ":(icase)" also finds the first commit of a file that was later renamed only in letter case
        added = repo.query("log", "--format=%H", "--diff-filter=A", "--", ":(icase)" + name).lines
        if added:
            first = added[-1].strip()
            commit = repo.commit(first)
            _subject_ok(ctx, commit.subject if commit else "", "加入许可证的那次提交", strict=False)
            together = [path for _, path in repo.changed_files(first)]
            readme_head = repo.file_at("HEAD", "README.md") or ""
            if "README.md" not in together and MD_LINK.search(readme_head) and re.search(
                    re.escape(name), readme_head):
                ctx.note("LICENSE 和 README 里的许可证一节分在了不同的提交里。它们是同一件事，"
                         "下次同一件事放进一个提交（第 1.10 课）。已经提交的不用改。")
            email = (commit.author_email if commit else "") or ""
            if email and not NOREPLY.search(email.strip()):
                if ctx.decision("commit_email") == "own":
                    ctx.note("加入许可证的那次提交，作者邮箱是你自己的邮箱（第 1.11 课你选的）。"
                             "第 2 站公开以后，谁都能在提交历史里看到它。")
                else:
                    ctx.note("加入许可证的那次提交，作者邮箱不是 GitHub 的隐私地址"
                             "（…@users.noreply.github.com）。第 2 站公开以后，谁都能在提交历史里看到它。"
                             "不想公开，先别往下做，对导师说“急救：公开前发现旧提交里有我的真实邮箱”。")
    if _expect_clean(ctx, repo) and name is not None and repo.file_at("HEAD", name) is not None:
        ctx.ok("没有落下还没提交的改动")


def check_b(ctx):
    """A public GitHub remote, everything pushed, the Pages address in the README."""
    repo = _site(ctx)
    parsed = _github_origin(ctx, repo)
    if parsed is None:
        ctx.stop()
    owner, name = parsed
    if name.lower() != "my-site":
        ctx.note("你的 GitHub 仓库叫 {}，不是课文里的 my-site；网址里的仓库名要跟着换。".format(name))
    pages = _pages_re(owner, name)

    text = ctx.read(repo.path / "README.md")
    if pages.search(text):
        ctx.ok("README.md 里写着网页地址")
    else:
        other = re.search(r"\S*github\.io\S*", text)
        repo_page = re.search(r"https?://github\.com/" + re.escape(owner) + "/" + re.escape(name),
                              text, re.IGNORECASE)
        if repo_page and not other:
            ctx.fail("README.md 里写的是仓库页面的地址，不是发布出来的网页地址",
                     where="my-site/README.md", saw="写的是 " + repo_page.group(0)[:50])
        elif other:
            ctx.fail("README.md 里的网页地址和你的仓库对不上", where="my-site/README.md",
                     saw="写的是 " + other.group(0)[:50])
        else:
            ctx.fail("README.md 里还没有网页地址", where="my-site/README.md",
                     saw="没有找到 github.io 的地址")
    _expect_clean(ctx, repo)
    _expect_pushed(ctx, repo)
    if ctx.failed:
        ctx.stop()

    def right(typed):
        return pages.fullmatch(typed.replace(" ", "")) is not None

    ctx.note("检查器不联网，看不到 GitHub 上的 Pages 设置，也看不到仓库是不是公开的。"
             "网页到底上线没有，只能靠你在手机上亲眼确认。")
    if not ctx.ask("你用手机打开的网页，地址是什么？照着 Pages 设置页上的网址输入：", right):
        typed = ctx.last_answer.replace(" ", "")
        if re.search(r"github\.com/", typed):
            ctx.note("你输入的像是源代码仓库的地址（github.com/…）。要的是发布出来的网页地址："
                     "https://用户名.github.io/仓库名/。")
        elif re.search(r"\.github\.io/?$", typed):
            ctx.note("你输入的地址少了仓库名那一段。项目网页的地址是 https://用户名.github.io/仓库名/；"
                     "手机地址栏常常只显示前半段，照 Pages 设置页上的网址输入。")
        ctx.stop()
    ctx.quiz(
        "你用手机打开这个网址时，看到的是哪一种？",
        [
            "我自己的网页：大标题就是我在 index.html 里写的那一句",
            "一个写着 404 的页面，说找不到网页",
            "手机打不开这个网址，或者一直在转圈",
        ],
        "A",
        explain="网页已经上线了。网址里的用户名都是小写，结尾的 / 可写可不写。",
        feedback={
            "B": "404 说明 GitHub 还没有发布这个网站：回到第 2 站「打开 Pages」那一步，对一遍设置"
                 "（Deploy from a branch、main、/ (root)，最后点 Save），再等几分钟。",
            "C": "可能是网址输错了，也可能是手机所在的网络打不开 github.io。先在电脑浏览器里打开同一个网址；"
                 "电脑上也打不开，对导师说“急救：Pages 用不了”。",
        },
    )


def check_c(ctx):
    """One more visible change went round the whole loop."""
    repo = _site(ctx)
    parsed = _github_origin(ctx, repo)
    if parsed is None:
        ctx.stop()
    owner, name = parsed
    page = ctx.read(repo.path / "index.html")
    link = re.compile(r"href\s*=\s*[\"'](https?)://github\.com/" + re.escape(owner) + "/"
                      + re.escape(name) + r"(\.git)?/?[\"']", re.IGNORECASE)
    found = link.search(page)
    if found:
        ctx.ok("网页里有指向源代码仓库的链接")
        if found.group(1).lower() == "http" or found.group(2):
            ctx.note("浏览器地址栏里仓库页面的写法是 https:// 开头、末尾不带 .git；"
                     "以后写仓库链接照那样写。")
    else:
        other = re.search(r"href\s*=\s*[\"'](https?://github\.com[^\"']*)", page, re.IGNORECASE)
        if other:
            ctx.fail("网页里的仓库链接没有指向你的 my-site 仓库", where="my-site/index.html",
                     saw="链接写的是 " + other.group(1)[:50])
        else:
            ctx.fail("网页里还没有指向源代码仓库的链接", where="my-site/index.html",
                     saw="没有找到以 https://github.com/ 开头的链接")
    committed = repo.file_at("HEAD", "index.html") or ""
    if link.search(page) and not link.search(committed):
        ctx.fail("加了链接的 index.html 还没有提交", where="my-site 的最新提交",
                 saw="提交里的 index.html 还没有这个链接")
    head = repo.commit()
    if head is not None:
        _subject_ok(ctx, head.subject, "最新一次提交", strict=False)
    _expect_clean(ctx, repo)
    _expect_pushed(ctx, repo)
    if ctx.failed:
        ctx.stop()
    ctx.quiz(
        "这一课反复走的交付循环，正确的顺序是哪一个？",
        [
            "改文件 → 看改动清单 → 提交 → 推送 → 刷新网页确认",
            "改文件 → 推送 → 提交 → 刷新网页确认",
            "改文件 → 保存 → 刷新网上的网页确认",
        ],
        "A",
        explain="推送只送走已经提交的快照；网上的网页只会在推送之后、GitHub 发布完以后才变。",
        feedback={
            "B": "先推送再提交，推送时还没有新的快照，网上什么都不会变。",
            "C": "保存只改了你电脑上的文件，网上的网页来自 GitHub 上的仓库。",
        },
    )


checks = {"1.13a": check_a, "1.13b": check_b, "1.13c": check_c}

# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.13a": [
        "这一站要做到三件事：my-site 里有填好的许可证文件；README.md 最后有一节说明用的是什么许可证；"
        "这两处改动按约定式提交拍成一个快照。检查结果里“还缺什么”说的是哪一件？",
        "先 cd ~/Developer/my-site，再运行 git status：LICENSE 和 README.md 是 Untracked、modified 还是已经干净了？"
        "如果说占位符没替换，用 head -n 3 LICENSE 看第三行。",
        "相似的例子：给一个叫 notes 的仓库补一节“联系方式”，就是在 README.md 末尾加\n"
        "    ## 联系方式\n    在 GitHub 上搜用户名 octo-learner 就能找到我。\n"
        "保存，然后 git add README.md，git commit -m \"docs: 补充联系方式\"。",
        "答案：先把 LICENSE 填好：在 VS Code 里打开 my-site 的 LICENSE，粘贴 choosealicense.com 上 MIT 许可证的全文，"
        "第三行写成 Copyright (c) 2026 你的笔名（方括号删掉），按 ⌘S 保存；用 ls 确认文件名是全部大写的 LICENSE。"
        "再打开 README.md，在最后加一节：\n"
        "    ## 许可证\n\n    本项目使用 MIT 许可证，全文见 [LICENSE](LICENSE)。\n"
        "保存。然后在终端里：\n"
        "    cd ~/Developer/my-site\n    git diff\n    git add LICENSE README.md\n"
        "    git commit -m \"docs: 添加 MIT 许可证\"\n    git status\n"
        "    git log -1 --format='%h %an <%ae>'\n"
        "解释：LICENSE 和 README 里的那一节是同一件事（给作品加许可证），所以放进一个提交；"
        "[LICENSE](LICENSE) 是相对链接，在 GitHub 上点它就会打开同一个仓库里的 LICENSE；"
        "最后一条命令（第 1.11 课学过）让你看到这次提交的作者名字和邮箱，它们会和网页一起公开。",
    ],
    "1.13b": [
        "这一站要做到：GitHub 上有公开的 my-site 仓库，Pages 已经打开，所有提交都推上去了，README.md 里写着网页地址，"
        "手机能打开网页。检查器最后会问你在手机上打开的网址和看到的样子。检查结果里“还缺什么”说的是哪一件？",
        "在 my-site 里运行 git remote -v 看有没有 origin；运行 git status 看第二行是不是 up to date with 'origin/main'。"
        "网址的样子是 https://你的用户名.github.io/my-site/，用户名就在 git remote -v 那个地址里 github.com/ 后面。",
        "相似的例子：如果用户名是 octo-learner、仓库叫 notes，网址就是 https://octo-learner.github.io/notes/ ，"
        "源代码仓库的地址是 https://github.com/octo-learner/notes 。两个地址里的用户名是同一个。",
        "答案：分两半。第一半是公开仓库和 Pages：GitHub 上还没有 my-site 的，先 cd ~/Developer/my-site，"
        "pwd 确认最后一段是 my-site，运行 gh repo create my-site --public --source=. --remote=origin --push；"
        "然后运行 gh browse --settings，"
        "左边栏点 Pages；Build and deployment 下面的 Source 选 Deploy from a branch，分支选 main，文件夹选 / (root)，点 Save；"
        "最长等大约 10 分钟，刷新设置页，出现 Visit site 就是发布好了。"
        "第二半：在 VS Code 里给 README.md 最后加一节\n    ## 网页地址\n    https://你的用户名.github.io/my-site/\n"
        "（换成你自己的用户名，全部小写），按 ⌘S 保存，然后在终端里\n"
        "    cd ~/Developer/my-site\n    git add README.md\n    git commit -m \"docs: 在 README 里写上网页地址\"\n    git push\n"
        "最后用手机打开这个网址，看到自己的网页，再运行检查；问网址时输入同一个地址。"
        "解释：Pages 把仓库 my-site 发布在“用户名.github.io/仓库名”下面，只发布推送到 GitHub 的提交；"
        "检查器不联网，看不到 Pages 有没有打开，所以要你亲眼确认。",
    ],
    "1.13c": [
        "这一站要让一处看得见的改动走完整个循环：改、看改动清单、提交、推送、刷新。"
        "检查结果里“还缺什么”停在了哪一步？",
        "运行 git status：如果说 modified，是还没提交；如果说 ahead of 'origin/main'，是还没推送。"
        "链接要写在 index.html 的页脚 <footer> 里，地址是 https://github.com/你的用户名/my-site 。",
        "相似的例子：页脚里已经有一个链接 <a href=\"https://developer.mozilla.org/zh-CN/\">MDN</a>，"
        "新链接的写法和它一样，只是 href 里的地址和两个尖括号中间的字不同。",
        "答案：在 index.html 的 <footer> 里，MDN 那个链接的 </a> 后面接着写\n"
        "    ，<a href=\"https://github.com/你的用户名/my-site\">这个网页的源代码</a>\n"
        "（换成你的用户名），按 ⌘S 保存；然后\n"
        "    cd ~/Developer/my-site\n    git diff\n    git add index.html\n"
        "    git commit -m \"feat: 在页脚加上源代码的链接\"\n    git push\n"
        "等一两分钟刷新网页。解释：推送送走的是提交过的快照，GitHub Pages 在推送之后重新发布；"
        "最后一题选 A。",
    ],
}

# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.13-no-license", "type": "recall", "tier": "fluent", "station": "1.13a",
     "rule": "PUB-01",
     "q": "一个 GitHub 上的公开仓库没有许可证文件。别人可以拿里面的代码做什么，不可以做什么？",
     "a": "可以在 GitHub 上看和 fork（这是 GitHub 服务条款允许的）。不可以复制、修改、分发：没有许可证就是作者保留所有权利。",
     "explain": "想让别人合法地复用，就要加许可证；选哪一个由你决定。"},
    {"id": "1.13-push-unstaged", "type": "predict", "tier": "fluent", "station": "1.13c",
     "q": "你改了 index.html 并保存，但没有 git add，也没有 git commit，就运行了 git push。会发生什么？",
     "options": ["打印 Everything up-to-date，网上的网页不变",
                 "把改动推送上去，网页一会儿就更新",
                 "报错：要先 git add"],
     "answer": "A", "shuffle": True,
     "explain": "推送只送已经提交的快照。没有新提交，Git 就说一切都是最新的，这一句不是报错，但也什么都没送走。"},
    {"id": "1.13-loop", "type": "recall", "tier": "fluent", "station": "1.13c",
     "q": "改网页上的一句话，从改文件到在网上看到变化，按顺序是哪五步？",
     "a": "改文件并保存 → git diff 看改动清单 → git add 和 git commit（按约定式提交写说明）→ git push → 等一会儿刷新网页确认。",
     "explain": "这一圈就是交付循环。以后的阶段会让机器替你检查和发布，但顺序不变。"},
    {"id": "1.13-pages-url", "type": "which", "tier": "lookup", "station": "1.13b",
     "q": "用户名是 octo-learner，仓库叫 notes，用 GitHub Pages 发布后的网页地址是哪一个？",
     "options": ["https://octo-learner.github.io/notes/",
                 "https://github.com/octo-learner/notes",
                 "https://notes.github.io/octo-learner/"],
     "answer": "A",
     "explain": "B 是源代码仓库的页面，不是发布出来的网页；项目网站的地址是“用户名.github.io/仓库名”。"},
    {"id": "1.13-pages-public", "type": "which", "tier": "aware", "station": "1.13b",
     "q": "用免费的 GitHub 账号，想用 GitHub Pages 发布一个仓库里的网页，仓库要是什么样的？",
     "options": ["公开仓库", "私有仓库", "公开或私有都可以"],
     "answer": "A",
     "explain": "GitHub 文档：账号用的是 GitHub Free 时，仓库必须是公开的。而且发布出来的网页对整个互联网公开。"},
    {"id": "1.13-three-files", "type": "fault", "tier": "lookup", "station": "1.13a",
     "rule": "PUB-01",
     "q": "一个马上要公开的仓库，根目录里有这些文件。按“公开仓库三件套”，缺了什么？\n\n    README.md\n    .gitignore\n    index.html\n    style.css",
     "options": ["缺 LICENSE", "缺 CHANGELOG.md", "什么也不缺"],
     "answer": "A",
     "explain": "三件套是 README.md、LICENSE、.gitignore。CHANGELOG.md 有用，但不在这三件里。"},
]

# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """The site just before this lesson: state S6 (no remote yet)."""
    sc.site_before()
    where = sc.show(sc.facts["site"])
    sc.todo("网站在这一课开始前的样子（{} 个提交，还没有远程仓库）：{}".format(
        sc.facts["site_commits"], where))
    sc.todo("你自己的 ~/Developer/my-site 好好的，就不用这个副本。"
            "要用它重建，对导师说“急救：my-site 的状态不对”。")


SCENARIOS = {"start": build_start}

# ---------------------------------------------------------------------------
# EXAM (gate-1)
# ---------------------------------------------------------------------------
MIT_TEMPLATE = """\
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

EXAM_OWNERS = ("小林", "阿青", "小周", "阿木", "小禾", "阿远", "小舟", "阿北")
PAGE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
</head>
<body>
  <h1>{title}</h1>
  <ul>
    <li>{item}</li>
  </ul>
</body>
</html>
"""
README_X1 = """\
# {repo}

一个只有一页的小网站。

## 怎么查看

在终端里进入这个文件夹，运行 open index.html。
"""
README_X1_B = """\
# {repo}

{title}的活动页面，只有一页。

## 页面上有什么

活动时间和联系方式。

## 本地预览

进入这个文件夹，运行 open index.html。
"""
TITLES = ("周末读书会", "社区菜园", "跑步小组", "旧物交换", "摄影角")
ITEMS = ("每周六上午见面", "新人随时欢迎", "活动免费", "下雨也照常")
# Both forms test the same skill (licence from the official text, filled in, named in the README,
# one Conventional commit); only the surface differs: folder and file names, page, README, wording.
X1_SURFACE = {
    "A": {"prefix": "site-", "template": "licenses/MIT.txt", "readme": README_X1,
          "ignore": "*.tmp\n.env\n"},
    "B": {"prefix": "club-", "template": "official/mit-license.txt", "readme": README_X1_B,
          "ignore": "drafts/\n.env\n"},
}


def build_x1(sc):
    """A site repository about to go public: README and .gitignore present, no licence yet."""
    surface = X1_SURFACE[sc.form]
    repo = surface["prefix"] + sc.word()
    owner = sc.pick(EXAM_OWNERS)
    year = sc.now.year
    title = sc.pick(TITLES)
    sc.git_init(repo)
    sc.write(repo + "/index.html", PAGE.format(title=title, item=sc.pick(ITEMS)), exact=True)
    sc.write(repo + "/README.md", surface["readme"].format(repo=repo, title=title), exact=True)
    sc.write(repo + "/.gitignore", surface["ignore"], exact=True)
    sc.git_commit(repo, "feat: 第一版网页")
    sc.write(surface["template"], MIT_TEMPLATE, exact=True)
    sc.fact("template", surface["template"])
    sc.fact("repo", repo)
    sc.fact("owner", owner)
    sc.fact("year", year)
    sc.fact("commits", 1)


def grade_x1(ctx):
    info = ctx.scenario()
    repo = ctx.need_repo(info.path / info.facts["repo"], "考试仓库")
    name = _check_license(ctx, repo, label="考试仓库")
    if name is not None:
        stored = repo.file_at("HEAD", name) or ""
        if info.facts["owner"] in stored and str(info.facts["year"]) in stored:
            ctx.ok("提交里的许可证写着题目要求的年份和版权人")
        else:
            ctx.fail("提交里的许可证没有写上题目要求的年份和版权人",
                     where="最新提交里的 " + name, saw="版权那一行和题目对不上")
    readme = repo.file_at("HEAD", "README.md") or ""
    ctx.expect(re.search(r"licen[sc]e|许可|MIT", readme, re.IGNORECASE) is not None,
               "README.md 里写了用的是什么许可证", "README.md 里还没有写许可证",
               where="最新提交里的 README.md", saw="没有提到许可证")
    if repo.commit_count() > info.facts["commits"]:
        head = repo.commit()
        _subject_ok(ctx, head.subject if head else "", "最新一次提交")
    else:
        ctx.fail("还没有新的提交", where="考试仓库的提交历史", saw="提交数没有增加")
    _expect_clean(ctx, repo, label="考试仓库")


def build_x2(sc):
    """A site repository with a local stand-in remote, already pushed once."""
    repo = "page-" + sc.word()
    title, new_title = sc.sample(TITLES, 2)
    item, new_item = sc.sample(ITEMS, 2)
    sc.git_init(repo)
    sc.write(repo + "/index.html", PAGE.format(title=title, item=item), exact=True)
    sc.git_commit(repo, "feat: 第一版网页")
    sc.git_init("remote/" + repo + ".git", bare=True)
    sc.git(repo, "remote", "add", "origin", str(sc.path("remote/" + repo + ".git")))
    sc.git(repo, "push", "-q", "-u", "origin", "main")
    sc.fact("repo", repo)
    sc.fact("remote", "remote/" + repo + ".git")
    sc.fact("text", new_title if sc.form == "A" else new_item)
    sc.fact("old", title)


def grade_x2(ctx):
    info = ctx.scenario()
    repo = ctx.need_repo(info.path / info.facts["repo"], "考试仓库")
    remote = ctx.git(info.path / info.facts["remote"])
    if not remote.is_bare:
        raise RuntimeError("the stand-in remote of 1.13-x2 is missing")
    text = info.facts["text"]
    local = repo.file_at("HEAD", "index.html") or ""
    online = remote.file_at("main", "index.html") or ""
    replaced = False
    if info.form == "A":
        done = re.search(r"<h1[^>]*>\s*" + re.escape(text) + r"\s*</h1>", local) is not None
        what = "大标题"
    else:
        done = re.search(r"<li[^>]*>\s*" + re.escape(text) + r"\s*</li>", local) is not None
        # The page was built with one item: "加一项" leaves two.
        replaced = done and len(re.findall(r"<li[\s>]", local)) < 2
        done = done and not replaced
        what = "列表里的新一项"
    if done:
        ctx.ok(what + "已经改好并提交")
    elif replaced:
        ctx.fail("列表里原来的那一项不见了：题目要的是加一项，不是把原来的换掉",
                 where="最新提交里的 index.html", saw="列表里只有一项")
    else:
        ctx.fail(what + "还没有出现在最新的提交里", where="最新提交里的 index.html",
                 saw="没有找到题目要求的文字")
    if repo.commit_count() > 1:
        head = repo.commit()
        _subject_ok(ctx, head.subject if head else "", "最新一次提交")
    if done and online == local:
        ctx.ok("改动已经推送到 origin")
    elif done:
        ctx.fail("改动还没有推送到 origin", where="远程仓库里的 index.html", saw="还是推送之前的样子")
    _expect_clean(ctx, repo, label="考试仓库")


EXAM = [
    {
        "id": "1.13-x1",
        "gate": "gate-1",
        "title": "公开之前补齐三件套",
        "minutes": 8,
        "build": build_x1,
        "task": {
            "A": "仓库 {dir}/{repo} 马上要公开，但还没有许可证。用 {dir}/{template} 给它加上 MIT 许可证："
                 "年份写 {year}，版权人写「{owner}」；在 README.md 里写一句用的是什么许可证。"
                 "按约定式提交的格式提交，做完以后 git status 要是干净的。",
            "B": "{dir}/{repo} 是一个活动页面的仓库，下周公开。公开仓库该有的三样东西里，它还差一样：许可证。"
                 "MIT 许可证的原文在 {dir}/{template}。版权行里的年份是 {year}，版权人是「{owner}」；README.md 里也要让读者知道"
                 "用的是什么许可证。改完按约定式提交的格式提交，git status 要是干净的。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.13-x2",
        "gate": "gate-1",
        "title": "改一处并推送到远程",
        "minutes": 6,
        "build": build_x2,
        "task": {
            "A": "仓库 {dir}/{repo} 已经连着一个远程仓库 origin。把网页的大标题从「{old}」改成「{text}」，"
                 "按约定式提交的格式提交，再推送到 origin。做完以后 git status 要显示和 origin/main 一致。",
            "B": "仓库 {dir}/{repo} 已经连着一个远程仓库 origin。在网页的列表里加一项「{text}」，"
                 "按约定式提交的格式提交，再推送到 origin。做完以后 git status 要显示和 origin/main 一致。",
        },
        "grade": grade_x2,
    },
]
