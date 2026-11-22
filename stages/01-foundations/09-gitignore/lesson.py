"""Lesson 1.9 Git：什么不该进仓库 (plan section 4).

Station a: the "不拍名单" .gitignore (patterns, git status --ignored,
git check-ignore -v, the learner's global ignore file, the official
templates); the exercise is the learner's own ~/Developer/my-site, which ends
in ladder state S5 (.gitignore with drafts/, *.tmp, .env; a new heading colour
and .gitignore in two commits, 「换了一个标题颜色」 and 「添加 .gitignore」;
five commits when the learner followed the lessons exactly).
Station b: a file that is already tracked is not affected by the list
(git ls-files, git rm --cached, git rm -r --cached); a committed secret stays
in history, so it is revoked first.  The exercise is the scenario 1.9b.

Scenarios: "start" (S4 copy of the site plus the commit of lesson 1.7b),
"1.9-demo" (the worked examples of both stations: hello-fx for station a,
weather for station b), "1.9b" (exercise of station b, seeded names).
Standard library only, Python 3.9 syntax.
"""

import re
import shlex

META = {
    "id": "1.9",
    "slug": "09-gitignore",
    "title": "Git：什么不该进仓库",
    "stage": 1,
    "prerequisites": ["1.8"],
    "stations": [
        {
            "id": "1.9a",
            "title": "给 Git 一份不拍名单",
            "minutes": 40,
            "new_concept": "仓库只放源文件：能重新生成的、私密的、太大的，写进 .gitignore 挡在外面",
            "new_commands": ["git status --ignored", "git check-ignore -v"],
        },
        {
            "id": "1.9b",
            "title": "已经进了仓库怎么办",
            "minutes": 40,
            "new_concept": "名单管不到已经跟踪的文件，历史里的东西也删不掉",
            "new_commands": ["git ls-files", "git rm --cached", "git rm -r --cached"],
        },
    ],
    "rules": ["REPO-01", "REPO-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9"},
    },
    "unverified_steps": [
        "1.9a：用 VS Code 打开 .gitignore、输入规则、按 ⌘S 保存，以及“标签上的圆点表示没保存”（code 命令在模拟环境里不能打开窗口；"
        "只验证了保存后的文件内容和 Git 的反应；“文件不存在时新建并标为已编辑”对照 VS Code 文档 Command Line Interface，圆点的说法对照 Basic editing，2026-11-20）",
        "1.9b：到发密钥的网站作废、更换密钥（各网站界面不同，只按 GitHub Docs 和 OWASP 的说法写了顺序）",
        "本课行规：GitHub 推送保护的行为（只对照了 GitHub Docs「About push protection」，2026-11-20 核对，没有真的推送）",
    ],
}

TERMS = [
    {"term": ".gitignore", "en": ".gitignore",
     "plain": "给 Git 的“不拍名单”：写在里面的文件，Git 不再提醒你提交；也叫忽略文件", "first": "1.9a"},
    {"term": "全局忽略文件", "en": "global ignore file (core.excludesFile)",
     "plain": "只在这台电脑上起作用、管所有仓库的不拍名单", "first": "1.9a"},
    {"term": "源文件", "en": "source file",
     "plain": "你亲手写的、别人要重建这个项目必须拿到的文件", "first": "1.9a"},
    {"term": "密钥", "en": "secret",
     "plain": "拿到就能冒充你“开门”的一串字符，比如密码、令牌、接口密钥", "first": "1.9a"},
    {"term": "接口密钥", "en": "API key",
     "plain": "网站发给你、让你的程序去用它的接口（网站留给别的程序取数据、办事的入口）时出示的密钥", "first": "1.9a"},
    {"term": "令牌", "en": "token",
     "plain": "一种通行证：程序拿着它就能代表你去用某个网站的服务；它代替密码，可以单独作废", "first": "1.9a"},
    {"term": "取消跟踪", "en": "untrack (git rm --cached)",
     "plain": "让 Git 不再管某个文件，但文件本身还留在你的电脑上", "first": "1.9b"},
    {"term": "作废密钥", "en": "revoke / rotate a secret",
     "plain": "到发密钥的网站让旧的失效，必要时换一个新的", "first": "1.9b"},
    {"term": "公开仓库", "en": "public repository",
     "plain": "谁都能看的仓库", "first": "1.9b"},
    {"term": "推送保护", "en": "push protection",
     "plain": "GitHub 在你往公开仓库推送时检查有没有认得出的密钥，有就先拦下来；你自己可以选择放行", "first": "1.9b"},
]


# ---------------------------------------------------------------------------
# Helpers shared by checks, review items and exam graders
# ---------------------------------------------------------------------------
_VERBOSE = re.compile(r"^(?P<source>.*):(?P<line>\d+):(?P<pattern>.*)\t(?P<path>.*)$")
_FULL_WIDTH = "＊／．！＃　"
LESSON_17_COLOR = "#c2410c"   # the colour lesson 1.7b commits (states.LESSON_COLOR)
STARTER_COLOR_LINE = "color: #0b5cad;"


def _ignore_rule(repo, path):
    """``(source, line, pattern)`` of the rule that ignores ``path``, or None.

    None when no rule matches, or when the last matching rule is a negation
    (a pattern starting with "!" means "do NOT ignore").
    """
    result = repo.query("check-ignore", "-v", "--", str(path))
    if result.code == 1:
        return None
    if result.code != 0:
        raise RuntimeError("git check-ignore failed: " + (result.err or "")[-200:])
    for line in result.lines:
        match = _VERBOSE.match(line)
        if match:
            pattern = match.group("pattern")
            if pattern.startswith("!"):
                return None
            return match.group("source"), int(match.group("line")), pattern
    return None


def _source_words(source):
    if source.endswith(".gitignore_global") or source.startswith("/"):
        return "全局忽略文件（只在这台电脑上有效）"
    if source.startswith(".git/"):
        return ".git 里面的个人忽略文件"
    return source


def _expect_ignored_here(ctx, repo, path, label, tracked_extra=""):
    """The path is ignored by the repository's own top-level .gitignore.

    ``tracked_extra`` is appended to the message when the path is already
    tracked (a way out the learner can follow at this point of the lesson).
    """
    if repo.is_tracked(path):
        return ctx.fail(label + "已经被 Git 跟踪，名单管不到它" + tracked_extra,
                        where="git check-ignore -v " + path, saw="它已经进过暂存区或提交")
    rule = _ignore_rule(repo, path)
    if rule is None:
        return ctx.fail(label + "还没有被忽略", where="git check-ignore -v " + path,
                        saw="没有任何规则挡住它")
    source = rule[0]
    if source != ".gitignore":
        return ctx.fail(label + "要由仓库自己的 .gitignore 挡住", where="git check-ignore -v " + path,
                        saw="挡住它的是" + _source_words(source))
    return ctx.ok(label + "被 .gitignore 挡住了")


def _misnamed_list(ctx, folder):
    """A list file with a near-miss name, for a clearer message."""
    for name in ("gitignore", ".gitignore.txt", "gitignore.txt", ".gitIgnore", ".Gitignore"):
        if ctx.is_file(folder / name):
            return name
    return None


def _full_width_line(text):
    """The first pattern line that holds a full-width symbol, or None.

    Blank lines and comment lines (first non-blank character a half-width
    "#") are skipped: Git ignores them, and the lesson teaches Chinese
    comments, which may well end in "！" or hold a full-width space.  A line
    that starts with the full-width "＃" is not a comment to Git and is
    still reported.
    """
    for line in text.splitlines():
        bare = line.lstrip(" \t")
        if not bare or bare.startswith("#"):
            continue
        if any(char in line for char in _FULL_WIDTH):
            # Only half-width blanks are trimmed: a full-width space at the
            # end is exactly what the learner has to see (ctx.visible).
            return line.strip(" \t")
    return None


def _full_width_names(line):
    """「＊」、全角空格 ... for the full-width symbols found in ``line``."""
    names = []
    for char in _FULL_WIDTH:
        if char in line:
            names.append("全角空格" if char == "\u3000" else "全角的「{}」".format(char))
    return "、".join(names)


def _why_no_list(ctx, repo, probes):
    """What the learner did instead of writing the top-level .gitignore.

    A near-miss name, a .gitignore one folder too deep, or a rule for one of
    ``probes`` (paths the list must hold) in another file, such as the global
    ignore file; otherwise the usual cause, a file that was never saved.
    """
    other = _misnamed_list(ctx, repo.path)
    if other:
        return "有一个叫 {} 的文件，名字不对".format(other)
    nested = [rel for rel in ctx.walk(repo.path) if rel.endswith("/.gitignore")]
    if nested:
        return "{} 里有一个 .gitignore；名单要放在最外层的文件夹里".format(nested[0][:-len(".gitignore")])
    for probe in probes:
        rule = _ignore_rule(repo, probe)
        if rule is not None and rule[0] != ".gitignore":
            return "没有这个文件；挡住 {} 的规则写进了{}".format(probe, _source_words(rule[0]))
    return "没有这个文件（在 VS Code 里写好以后，按 ⌘S 保存了吗？）"


def _expect_gitignore_file(ctx, repo, where_label, probes=()):
    """The top-level .gitignore exists, has no full-width symbols and is committed."""
    path = repo.path / ".gitignore"
    if not ctx.is_file(path):
        ctx.fail("顶层文件夹里还没有 .gitignore", where=where_label, saw=_why_no_list(ctx, repo, probes))
        return False
    text = ctx.read(path)
    odd = _full_width_line(text)
    if odd:
        ctx.fail(".gitignore 里有全角符号，Git 不认", where=".gitignore 的这一行",
                 saw="「{}」：这一行里有{}".format(ctx.visible(odd[:40]), _full_width_names(odd)))
    if repo.file_at("HEAD", ".gitignore") is None:
        ctx.fail(".gitignore 还没有进入提交", where="最新的提交", saw="里面没有 .gitignore")
    else:
        ctx.ok(".gitignore 已经提交")
    return True


def _root_commit(repo):
    result = repo.query("rev-list", "--max-parents=0", "HEAD")
    if not result.ok or not result.lines:
        raise RuntimeError("cannot read the first commit")
    return result.lines[-1].strip()


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """State before the lesson: a copy of the site in S4, plus the commit
    lesson 1.7b makes in the learner's own site (the ladder has no state at
    the end of 1.7, so S4 alone would have one commit fewer than the
    learner's site)."""
    sc.site_before()
    site = sc.facts["site"]
    css = sc.path(site + "/style.css").read_text(encoding="utf-8")
    sc.write(site + "/style.css", css.replace(STARTER_COLOR_LINE, "color: " + LESSON_17_COLOR + ";"),
             exact=True)
    sc.git_commit(site, "改了标题的颜色", add="style.css", date=sc.ago(days=1))
    sc.fact("site_commits", sc.facts["site_commits"] + 1)
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))
    sc.todo("这只是副本，给重建和测试用。本课的练习做在你自己的 ~/Developer/my-site 里。")


def build_demo(sc):
    """Worked example of station a: a small Python project with clutter."""
    sc.copy_in("starter/hello-fx", "hello-fx")
    sc.git_init("hello-fx")
    sc.git_commit("hello-fx", "第一版换算程序", date=sc.ago(days=1))
    sc.write("hello-fx/notes.md", """
        # 笔记

        - 想加一个美元换欧元的功能
    """)
    sc.write("hello-fx/.env", "FX_API_KEY=demo-4f9a2c-not-a-real-key")
    sc.write("hello-fx/secret-token.txt", "tok_demo_8d31e7_not_a_real_token")
    sc.write_bytes("hello-fx/__pycache__/convert.cpython-314.pyc", b"\xa7\r\r\n\x00\x00\x00\x00demo")
    sc.write("hello-fx/rates.txt.bak", "这是编辑器留下的旧备份")
    sc.write_bytes("hello-fx/.DS_Store", b"\x00\x00\x00\x01Bud1demo")
    _build_leak(sc)
    sc.fact("repo", "hello-fx")
    sc.fact("leak_repo", "weather")
    sc.todo("练习项目在这里：" + sc.show("hello-fx"))
    sc.todo("先进去：cd " + sc.show("hello-fx"))
    sc.todo("旁边的 weather 是第 2 站才用的仓库，现在先不用管它。")


LEAK_ENV = "WEATHER_API_KEY=demo-7c2e-not-a-real-key\n"


def _build_leak(sc):
    """Worked example of station b (built together with station a's):
    .env was committed in the second commit; an uncommitted .gitignore
    already lists it."""
    sc.write("weather/index.html", """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><title>今天的天气</title></head>
        <body><h1>今天的天气</h1></body>
        </html>
    """)
    sc.git_init("weather")
    sc.git_commit("weather", "第一版天气页", date=sc.ago(days=2))
    sc.write("weather/.env", LEAK_ENV, exact=True)
    sc.git_commit("weather", "加上天气接口的配置", date=sc.ago(days=1))
    sc.write("weather/.gitignore", "# 密钥，永远不进仓库\n.env\n", exact=True)


SECRET_NAMES = ["api-key.txt", "upload-token.txt", "secret-key.txt"]
CACHE_NAMES = ["thumbs", "cache", "resized"]


def build_b(sc):
    """Exercise of station b: a secret file and a generated folder are tracked."""
    repo = "album-" + sc.word()
    secret = sc.pick(SECRET_NAMES)
    folder = sc.pick(CACHE_NAMES)
    sc.write(repo + "/index.html", """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><title>我的相册</title></head>
        <body><h1>我的相册</h1></body>
        </html>
    """)
    sc.git_init(repo)
    sc.git_commit(repo, "第一版相册页", date=sc.ago(days=3))
    files = []
    for name in sc.sample(["sea", "hill", "cat", "tea", "bridge"], 2):
        rel = "{}/{}-small.jpg".format(folder, name)
        sc.write_bytes(repo + "/" + rel, b"\xff\xd8\xff\xe0demo-" + name.encode() + b"\xff\xd9")
        files.append(rel)
    sc.write(repo + "/" + secret, "demo-{}-not-a-real-key".format(sc.randint(100000, 999999)))
    leak = sc.git_commit(repo, "加上缩略图和上传接口", date=sc.ago(days=2))
    sc.fact("repo", repo)
    sc.fact("secret", secret)
    sc.fact("folder", folder)
    sc.fact("folder_files", files)
    sc.fact("leak", leak)
    sc.todo("练习仓库在这里：" + sc.show(repo))
    sc.todo("先进去：cd " + sc.show(repo))


SCENARIOS = {
    "start": build_start,
    "1.9-demo": build_demo,
    "1.9b": build_b,
}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _draft_note(ctx, drafts):
    """The note the question asks about: a visible file first, then any file."""
    notes = ctx.walk(drafts) if ctx.is_dir(drafts) else []
    visible = [rel for rel in notes if not rel.split("/")[-1].startswith(".")]
    chosen = (visible or notes or [None])[0]
    return None if chosen is None else "drafts/" + chosen


def _commits_touching(repo, path, since=None):
    """Hashes of the commits that changed ``path`` (after ``since`` when given)."""
    args = ["log", "--format=%H"]
    if since:
        args.append(since + "..HEAD")
    result = repo.query(*(args + ["--", path]))
    if not result.ok:
        raise RuntimeError("git log failed: " + (result.err or "")[-200:])
    return [line.strip() for line in result.lines if line.strip()]


def _gitignore_commit(repo):
    """The commit that first added .gitignore, or None."""
    added = repo.query("log", "--format=%H", "--diff-filter=A", "--", ".gitignore")
    if not added.ok or not added.lines:
        return None
    return added.lines[-1].strip()


def _check_colour_commits(ctx, site):
    """A new heading colour is committed, in a commit of its own."""
    first_css = site.file_at(_root_commit(site), "style.css")
    head_css = site.file_at("HEAD", "style.css")
    if head_css is None or first_css is None:
        ctx.fail("最新的提交里没有 style.css", where="最新的提交", saw="找不到 style.css")
        return
    if head_css == first_css:
        ctx.fail("标题的新颜色还没有进入提交", where="最新提交里的 style.css",
                 saw="和第一版网页时一样")
        return
    if LESSON_17_COLOR in head_css.lower():
        ctx.fail("标题的新颜色还没有进入提交", where="最新提交里的 style.css",
                 saw="标题的颜色还是第 1.7 课的 " + LESSON_17_COLOR)
        return
    ctx.ok("标题换了新颜色，已经提交")
    added = _gitignore_commit(site)
    if added is None:
        return   # reported by _expect_gitignore_file
    touched = [name for _letter, name in site.changed_files(added)]
    if "style.css" in touched and not _commits_touching(site, "style.css", since=added):
        ctx.fail("新颜色和 .gitignore 要各有一个提交。不用撤销刚才的提交："
                 "把标题再换一个颜色，保存，单独提交一次",
                 where="git log --stat", saw="添加 .gitignore 的那个提交里也改了 style.css")
    else:
        ctx.ok("新颜色和 .gitignore 各在自己的提交里")


def check_a(ctx):
    """The learner's own site: .gitignore with drafts/, *.tmp, .env; S5."""
    site = ctx.need_repo(ctx.my_site, "你的网站文件夹 my-site")
    if not _expect_gitignore_file(ctx, site, "~/Developer/my-site 里",
                                  probes=("drafts/colors.md", ".env", "notes.tmp")):
        ctx.stop()

    drafts = site.path / "drafts"
    first_note = _draft_note(ctx, drafts)
    if first_note is None:
        ctx.fail("my-site 里还没有放了笔记的 drafts 文件夹", where=ctx.show(drafts),
                 saw="文件夹不存在或是空的")
    else:
        _expect_ignored_here(ctx, site, first_note, "drafts 里的笔记",
                             tracked_extra="。怎么让 Git 放手一个已经跟踪的文件，第 2 站会教："
                                           "先做完第 2 站的“跟我做”，再回来做这里")
    _expect_ignored_here(ctx, site, ".env", ".env 文件")
    _expect_ignored_here(ctx, site, "notes.tmp", "随便一个 .tmp 文件")

    tracked = site.tracked()
    leaked = [path for path in tracked if path.startswith("drafts/") or path == ".env"
              or path.endswith(".tmp")]
    if leaked and leaked != [first_note]:
        ctx.fail("有不该进仓库的文件已经被跟踪", where="仓库里被跟踪的文件",
                 saw="、".join(leaked[:3]))

    _check_colour_commits(ctx, site)
    status = site.status()
    if not status.clean:
        names = "、".join(entry.path for entry in status.entries[:3])
        ctx.fail("还有改动没有处理", where="my-site 里的 git status", saw="还列着：" + names)
    if ctx.failed:
        ctx.stop()
    ctx.ok("git status 是干净的，草稿留在了仓库外面")
    if _commits_touching(site, "drafts"):
        # The learner committed drafts/ before the list and then untracked it
        # (the way out hint 4 gives): true, but the old commits keep it.
        ctx.note("drafts 里的笔记还留在以前的提交里；里面没有私密内容就不要紧（第 2 站讲为什么）")

    rule = _ignore_rule(site, first_note)
    ctx.ask("在 my-site 里运行 git check-ignore -v {}：挡住它的规则写在 .gitignore 的第几行？"
            .format(shlex.quote(first_note)), expected=rule[1])


def _untracked_b(ctx):
    """Shared by the station check of 1.9b and the review item 1.9-d1."""
    info = ctx.scenario("1.9b")
    name = info.facts["repo"]
    repo = ctx.need_repo(info.path / name, "练习仓库 " + name)
    secret = info.facts["secret"]
    folder = info.facts["folder"]
    files = info.facts["folder_files"]

    lost = []
    if not ctx.is_file(repo.path / secret):
        lost.append(secret)
        ctx.fail("密钥文件本身也被删掉了", where=ctx.show(repo.path / secret),
                 saw="电脑上已经没有这个文件；要的是 Git 放手、文件留着")
    missing = [rel for rel in files if not ctx.is_file(repo.path / rel)]
    if missing:
        lost.append(folder)
        ctx.fail("缩略图文件夹里的文件也被删掉了", where=ctx.show(repo.path / folder),
                 saw="少了 " + "、".join(missing))
    if lost:
        way_back = ("找回的办法：还没提交的话，在练习仓库里先运行 git restore --staged {0}，"
                    "再运行 git restore {0}。".format(" ".join(lost)))
        if ctx.station == "1.9b":
            way_back += ("已经提交了，就回到学习工作区重搭一份练习场景，从头再做："
                         "python3 tools/course.py scenario 1.9b --reset")
        ctx.note(way_back)

    tracked = repo.tracked()
    still = [rel for rel in files if rel in tracked]
    started = (secret not in tracked or len(still) < len(files)
               or ctx.is_file(repo.path / ".gitignore") or not repo.is_clean())
    if not started:
        # Nothing changed yet: say what kind of thing is missing, not its name
        # (finding the two is goal 1 of the exercise).
        ctx.fail("还有一个放密钥的文件和一个缩略图文件夹被 Git 跟踪着", where="git ls-files",
                 saw="两样都还在 Git 跟踪的文件里")
        ctx.fail("顶层文件夹里还没有 .gitignore", where="练习仓库的顶层文件夹", saw="没有这个文件")
        return info
    if secret in tracked:
        ctx.fail("Git 还在跟踪 " + secret, where="git ls-files", saw=secret + " 还在列表里")
    if still:
        ctx.fail("Git 还在跟踪 {}/ 里的文件".format(folder), where="git ls-files",
                 saw=still[0] + " 还在列表里")
    if secret not in tracked and not still:
        ctx.ok("Git 已经不再跟踪这两样东西")

    if _expect_gitignore_file(ctx, repo, "练习仓库的顶层文件夹", probes=[secret] + files):
        if ctx.is_file(repo.path / secret) and secret not in tracked:
            _expect_ignored_here(ctx, repo, secret, secret + " ")
        if files and ctx.is_file(repo.path / files[0]) and files[0] not in tracked:
            _expect_ignored_here(ctx, repo, files[0], folder + "/ 里的文件")

    in_head = [path for path in [secret] + files if repo.file_at("HEAD", path) is not None]
    if in_head:
        ctx.fail("最新的提交里还有它们", where="最新的提交", saw=in_head[0] + " 还在快照里")
    status = repo.status()
    if not status.clean:
        # Untracked entries that are the secret or the generated folder must
        # stay out: "commit your changes" would put them back in.
        def _keep_out(path):
            bare = path.rstrip("/")
            return bare == secret or bare == folder or bare.startswith(folder + "/")
        outside = [entry.path for entry in status.entries
                   if entry.code == "??" and _keep_out(entry.path)]
        other = [entry.path for entry in status.entries if entry.path not in outside]
        if outside:
            ctx.fail("还有没被名单挡住的文件：先把它们写进 .gitignore，别把它们提交进去",
                     where="git status 的 Untracked files", saw="还列着：" + "、".join(outside[:3]))
        if other:
            ctx.fail("还有改动没有提交", where="git status", saw="还列着：" + "、".join(other[:3]))
    elif not ctx.failed:
        ctx.ok("改动已经提交，git status 是干净的")
    return info


def check_b(ctx):
    _untracked_b(ctx)
    if ctx.failed:
        ctx.stop()
    ctx.quiz(
        "这个仓库的历史里还留着那个密钥。如果它是真的，而且仓库已经推送到网上，第一步做什么？",
        [
            "git rm --cached 已经做过了，现在已经安全",
            "把网上的仓库改成私有，别人就看不到了",
            "到发这个密钥的网站，把它作废并换一个新的",
        ],
        "C",
        explain="不再跟踪只管以后的快照；之前的提交里还有它，拿到过历史的人都能看到。",
        feedback={
            "A": "git rm --cached 之后，前面的提交里还留着这个密钥。",
            "B": "改成私有之前，别人可能已经复制走了；密钥本身还能用。",
        },
    )


checks = {"1.9a": check_a, "1.9b": check_b}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.9a": [
        "一共四件事：建 drafts 草稿、给标题换新颜色、写 .gitignore、分两次提交。检查结果里“还缺什么”说的是哪一件？",
        "名单要写在 ~/Developer/my-site/.gitignore 这个文件里（名字以点开头，和 index.html 放在一起），"
        "不是 ~/.gitignore_global。写完在 my-site 里运行 git status --ignored，看 drafts/ 是不是出现在 Ignored files 下面。"
        "提交时一次只 git add 一个文件，两次提交就不会混在一起。",
        "相似的例子：练习项目 hello-fx 里，你写了 secret-token.txt（一个名字）、__pycache__/（一个文件夹）、"
        "*.bak（一类文件）这几行。这次要挡住的是另外三样东西，写法一样。",
        "答案：在 my-site 里运行 mkdir drafts，再 touch drafts/colors.md（一个空文件就够）；"
        "运行 code . 打开整个 my-site，把 style.css 里 h1 下面的 color: #c2410c; 改成新颜色（比如 color: #2a7f62;），保存；"
        "在资源管理器里新建 .gitignore，写三行：drafts/、*.tmp、.env，保存。然后 git add style.css，"
        "git commit -m \"换了一个标题颜色\"；再 git add .gitignore，git commit -m \"添加 .gitignore\"；最后 git status 应该是干净的。"
        "解释：drafts/ 末尾的斜杠表示“这个文件夹”，*.tmp 表示所有以 .tmp 结尾的文件，.env 是一个名字。"
        "最后的问答：git check-ignore -v drafts/colors.md 输出里第一个冒号后面的数字就是行号。"
        "两种常见情况：新颜色和 .gitignore 已经进了同一个提交，不用撤销，把颜色再改一次单独提交；"
        "drafts 已经被提交过（检查说“已经被 Git 跟踪”），先写好 .gitignore，再运行 git rm -r --cached drafts，"
        "然后提交（第 2 站会讲为什么）。",
    ],
    "1.9b": [
        "要做到三件事：Git 不再跟踪那两样东西、它们还留在电脑上、以后也进不来。先弄清楚是哪两样。",
        "运行 git ls-files 看 Git 在跟踪哪些文件；一个是密钥文件，一个是能重新生成的缩略图文件夹。"
        "第 2 站“跟我做”里让 Git 放手 .env 的那条命令就是要用的，文件夹要多加一个选项。",
        "相似的例子：仓库里已经提交过一个 build/ 文件夹，要让 Git 放手它：先把 build/ 写进 .gitignore，"
        "再 git rm -r --cached build，git status 会显示一串 deleted，然后提交。",
        "答案（名字以你的练习仓库为准）：把密钥文件名和“文件夹名/”各写一行到 .gitignore；"
        "运行 git rm --cached 密钥文件名，再运行 git rm -r --cached 文件夹名；git add .gitignore；"
        "git commit -m \"不再跟踪密钥和缩略图\"。用 ls 确认文件还在。"
        "解释：--cached 只从暂存区拿掉，工作区的文件不动；文件夹要加 -r。"
        "最后的选择题选“到发这个密钥的网站，把它作废并换一个新的”：历史里还留着它，只有作废才让它开不了门。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.9-r1", "type": "recall", "tier": "fluent", "station": "1.9a",
     "q": "一个仓库里该放什么？说出三类不该放进去的东西，各举一个例子。",
     "a": "放亲手写的、重建项目必须有的源文件。不放：能重新生成的（__pycache__/ 缓存）、"
          "私密的（.env 里的密钥、密码、令牌）、太大的（视频、大数据文件）。"},
    {"id": "1.9-w1", "type": "which", "tier": "lookup", "station": "1.9a",
     "q": "notes.tmp 没有出现在 git status 里。想知道是哪个文件的哪一行规则挡住了它，用哪条命令？",
     "options": ["git check-ignore -v notes.tmp", "git status --ignored", "git ls-files"],
     "answer": "A", "shuffle": True,
     "explain": "git check-ignore -v 会打印规则所在的文件、行号和规则本身；git status --ignored 只列出被忽略的文件，不说是哪条规则。"},
    {"id": "1.9-f1", "type": "fault", "tier": "lookup", "station": "1.9a", "rule": "REPO-02",
     "q": ".gitignore 里写了下面这一行，可 notes.tmp 还是出现在 git status 的 Untracked files 里。问题在哪？\n\n    ＊.tmp",
     "options": ["星号是全角的＊，Git 只认半角的 *", ".gitignore 要先提交才会生效", ".tmp 前面要加一个斜杠"],
     "answer": "A", "shuffle": True,
     "explain": "规则保存以后马上生效，不用先提交；这一行的星号是中文输入法打出来的全角符号。"},
    {"id": "1.9-p1", "type": "predict", "tier": "fluent", "station": "1.9b",
     "q": "config.env 早就提交过。你把 config.env 写进 .gitignore，然后又改了 config.env 里的一行。git status 会怎样显示它？",
     "options": ["不显示：它已经在名单里了", "显示 modified: config.env", "显示 Untracked files: config.env"],
     "answer": "B",
     "explain": "名单只管还没被跟踪的文件。已经跟踪的文件一改，Git 照样提醒；要先 git rm --cached 让 Git 放手。"},
    {"id": "1.9-r2", "type": "recall", "tier": "fluent", "station": "1.9b", "rule": "REPO-01",
     "q": "你发现一个真的密钥被提交进了仓库，而且已经推送到网上。第一步做什么？为什么 git rm --cached 不够？",
     "a": "第一步：到发这个密钥的网站把它作废，换一个新的。git rm --cached 只是以后不再跟踪，"
          "之前的提交里还留着它，拿到过历史的人都能看到。",
     "explain": "这是行规 REPO-01：密钥、密码、令牌永不入库；进去了就当它已经泄露。"},
    {"id": "1.9-d1", "type": "do", "tier": "lookup", "station": "1.9b",
     "q": "练习仓库里，Git 还在跟踪一个密钥文件和一个能重新生成的缩略图文件夹。让 Git 不再跟踪它们、以后也不再提醒，"
          "文件本身留在电脑上，并把这次改动提交。",
     "scenario": "1.9b", "check": _untracked_b},
]


# ---------------------------------------------------------------------------
# EXAM (gate-b)
# ---------------------------------------------------------------------------
X1_JUNK = {
    "A": [(".env", "API_KEY=demo-{n}-not-real", "密钥文件"), ("token.txt", "tok_demo_{n}", "令牌文件")],
    "B": [("secrets.env", "PASSWORD=demo-{n}-not-real", "密码文件"), ("api-key.txt", "demo-{n}", "密钥文件")],
}
X1_CACHE = {"A": "build", "B": "tmp-output"}


def build_x1(sc):
    """Untracked clutter that must be kept out before anything is committed."""
    repo = "shop-" + sc.word()
    secret, body, noun = sc.pick(X1_JUNK[sc.form])
    cache = X1_CACHE[sc.form]
    sc.write(repo + "/index.html", "<h1>小店</h1>")
    sc.git_init(repo)
    sc.git_commit(repo, "第一版小店首页", date=sc.ago(days=1))
    sc.write(repo + "/" + secret, body.format(n=sc.randint(1000, 9999)))
    sc.write(repo + "/" + cache + "/page.html", "<h1>自动生成的页面</h1>")
    keep = sc.pick(["menu.txt", "prices.txt", "about.txt"])
    sc.write(repo + "/" + keep, "今天的内容")
    sc.fact("repo", repo)
    sc.fact("secret", secret)
    sc.fact("secret_kind", noun)
    sc.fact("cache", cache)
    sc.fact("keep", keep)


def grade_x1(ctx):
    info = ctx.scenario()
    repo = ctx.need_repo(info.path / info.facts["repo"], "考试仓库")
    secret, cache, keep = info.facts["secret"], info.facts["cache"], info.facts["keep"]
    if not _expect_gitignore_file(ctx, repo, "考试仓库的顶层文件夹",
                                  probes=(secret, cache + "/page.html")):
        ctx.stop()
    tracked = repo.tracked()
    ctx.expect(secret not in tracked, secret + " 没有进入仓库",
               "不该进仓库的文件被跟踪了", where="仓库里被跟踪的文件", saw=secret + " 在里面")
    ctx.expect(not any(path.startswith(cache + "/") for path in tracked), cache + "/ 没有进入仓库",
               "自动生成的文件夹被跟踪了", where="仓库里被跟踪的文件", saw=cache + "/ 在里面")
    if not ctx.is_file(repo.path / secret):
        ctx.fail("那个文件被删掉了", where=ctx.show(repo.path / secret), saw="电脑上没有它了")
    elif secret not in tracked:
        _expect_ignored_here(ctx, repo, secret, secret + " ")
    if ctx.is_file(repo.path / cache / "page.html") and cache + "/page.html" not in tracked:
        _expect_ignored_here(ctx, repo, cache + "/page.html", cache + "/ 里的文件")
    ctx.expect(repo.file_at("HEAD", keep) is not None, keep + " 已经提交",
               "该提交的文件还没有提交", where="最新的提交", saw="里面没有 " + keep)
    ctx.expect(repo.is_clean(), "git status 是干净的", "还有改动没有处理",
               where="git status", saw="不是干净的")


def build_x2(sc):
    """A file or folder that is already tracked must be untracked and ignored."""
    repo = "notes-" + sc.word()
    sc.write(repo + "/README.md", "# 笔记")
    sc.git_init(repo)
    sc.git_commit(repo, "第一版笔记", date=sc.ago(days=2))
    if sc.form == "A":
        target = sc.pick(["config.env", "password.txt", "db-secret.txt"])
        sc.write(repo + "/" + target, "SECRET=demo-{}".format(sc.randint(1000, 9999)))
        probe = target
        kind = "文件"
    else:
        target = sc.pick(["cache", "generated", "exports"])
        sc.write(repo + "/" + target + "/report.csv", "日期,金额\n2026-11-18,12\n")
        probe = target + "/report.csv"
        kind = "文件夹"
    sc.git_commit(repo, "加上" + target, date=sc.ago(days=1))
    sc.fact("repo", repo)
    sc.fact("target", target)
    sc.fact("probe", probe)
    sc.fact("kind", kind)


def grade_x2(ctx):
    info = ctx.scenario()
    repo = ctx.need_repo(info.path / info.facts["repo"], "考试仓库")
    target, probe = info.facts["target"], info.facts["probe"]
    if not ctx.is_file(repo.path / probe):
        ctx.fail("它在电脑上被删掉了", where=ctx.show(repo.path / probe), saw="文件不在了；要的是只让 Git 放手")
    tracked = repo.tracked()
    ctx.expect(not any(path == target or path.startswith(target + "/") for path in tracked),
               "Git 已经不再跟踪 " + target, "Git 还在跟踪它", where="git ls-files", saw=target + " 还在列表里")
    if (_expect_gitignore_file(ctx, repo, "考试仓库的顶层文件夹", probes=(probe,))
            and ctx.is_file(repo.path / probe)):
        _expect_ignored_here(ctx, repo, probe, target + " ")
    done = ctx.expect(repo.file_at("HEAD", probe) is None, "最新的提交里已经没有它",
                      "这次改动还没有提交", where="最新的提交", saw=probe + " 还在快照里")
    if not repo.is_clean():
        ctx.fail("还有改动没有处理", where="git status", saw="不是干净的")
    elif done:
        ctx.ok("git status 是干净的")


EXAM = [
    {
        "id": "1.9-x1",
        "gate": "gate-b",
        "title": "把不该进仓库的东西挡在外面",
        "minutes": 6,
        "build": build_x1,
        "task": {
            "A": "仓库 {dir}/{repo} 里多了三样东西：{secret}、{cache} 文件夹和 {keep}。"
                 "只有 {keep} 该进仓库。另外两样留在电脑上，但让 Git 以后都不再提醒它们；把该提交的提交，做完 git status 要是干净的。",
            "B": "进入 {dir}/{repo}：{secret} 是{secret_kind}，{cache}/ 是程序自动生成的。"
                 "把 {keep} 和你写的忽略规则提交进去，另外两样永远不进仓库，也不要删掉它们。"
                 "做完 git status 要是干净的。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.9-x2",
        "gate": "gate-b",
        "title": "让 Git 放手一个已经提交的东西",
        "minutes": 6,
        "build": build_x2,
        "task": {
            "A": "仓库 {dir}/{repo} 的历史里提交过一个{kind} {target}，它不该在仓库里。"
                 "让 Git 不再跟踪它，以后也不再提醒它，但它要留在电脑上；把改动提交，git status 要是干净的。",
            "B": "{dir}/{repo} 里的 {target}（一个{kind}）已经被提交了，可它是能随时重新生成的。"
                 "让它从下一个提交开始离开仓库、留在你的电脑上，并保证以后不会再被提交。"
                 "做完 git status 要是干净的。",
        },
        "grade": grade_x2,
    },
]
