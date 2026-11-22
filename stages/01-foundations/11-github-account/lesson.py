"""Lesson 1.11: GitHub account, security and identity.

Station a: sign up and two-factor authentication (web steps, checked against
GitHub Docs on 2026-11-19).  Station b: install gh with Homebrew and log in
(gh auth login is interactive and needs an account and the network, so the
check never runs gh and never reads a token).  Station c: the identity inside a
commit is public; choose the commit e-mail and the signing method, and prove
it with one new commit in a practice copy of the site.

Standard library only, Python 3.9 syntax.  See docs/authoring/tool-api.md.
"""

import re
import unicodedata
from pathlib import Path

META = {
    "id": "1.11",
    "slug": "11-github-account",
    "title": "GitHub：账号、安全与身份",
    "stage": 1,
    "prerequisites": ["1.10"],
    "stations": [
        {"id": "1.11a", "title": "注册和双重验证", "minutes": 35,
         "new_concept": "双重验证：登录时除了密码，还要一样只在你手里的东西",
         "new_commands": []},
        {"id": "1.11b", "title": "让电脑认识 GitHub", "minutes": 35,
         "new_concept": "电脑用令牌代替密码，替你在 GitHub 上办事",
         "new_commands": ["which", "brew install", "gh --version", "gh auth login", "gh auth status"]},
        {"id": "1.11c", "title": "提交邮箱隐私和签名的选择", "minutes": 35,
         "new_concept": "提交里写着作者的名字和邮箱，推送到公开仓库后谁都看得到",
         "new_commands": ["git log --format", "git log -1"]},
    ],
    "rules": ["ACC-01", "ACC-02"],
    "verified": {"date": "2026-11-20",
                 "tools": {"macos": "27.2.1", "zsh": "5.9", "git": "2.54.0",
                           "brew": "7.0.10", "gh": "2.105.0", "python3": "3.14.9"}},
    "unverified_steps": [
        "1.11a 在 github.com/signup 注册账号；已经用短信开了双重验证的，添加验证器 App 并设为 Preferred 2FA method（对照 GitHub Docs：Creating an account on GitHub、Changing your two-factor authentication method）",
        "1.11a 用验证器 App 开启双重验证、下载恢复码（对照 GitHub Docs：Configuring two-factor authentication）；故意把数字最后一位改错再填时页面上的提示原文无法验证",
        "1.11a 把恢复码存进 Mac 自带的 Passwords App 的 Notes 栏（对照 Apple 支持文档：See your website or app passwords and related info on Mac）",
        "1.11a 想多了解：退出后用验证器 App 的六位数字重新登录（对照 GitHub Docs）",
        "1.11b brew install gh 的输出，包括结尾的 Caveats 几行（建课时不能在本机装软件；格式对照 Homebrew 7.0.10 的源码 install.rb、messages.rb、caveats.rb）",
        "1.11b 装好以后 which gh 和 gh --version 的输出（建课时没装 gh；路径按 Homebrew 在 Apple 芯片上的默认位置 /opt/homebrew，版本行格式取自 gh 2.105.0 源码）",
        "1.11b gh auth login 的问题和回答（需要账号和网络；问题原文取自 gh 2.105.0 源码和 GitHub Docs）",
        "1.11b gh auth status 的输出（需要账号；格式取自 gh 2.105.0 源码）",
        "1.11c 跟我做第 2 步：在 quote> 提示符下按 Ctrl+C 回到平常的提示符（同 1.10b，建课环境没有终端设备；"
        "只核实了少打右边的单引号时交互式 zsh 会显示 quote>）",
        "1.11c 在 GitHub 的 Emails 设置页打开邮箱隐私、复制 noreply 地址；用自己邮箱时去掉 Block command line pushes 的勾（对照 GitHub Docs）",
        "1.11c 推送被 GH007 拦下时的那一行 remote: error（GitHub 文档没有原文；建课时不能推送）",
        "1.11c 想多了解：在 Emails 页 Add email address 添加第 1.6 课的邮箱（对照 GitHub Docs：Adding an email address to your GitHub account）",
        "1.11 想多了解：SSH 签名里 ssh-keygen 的三句提问（建课时没有终端可以交互，只能用 -f 和 -N 运行；结尾几行已实测）",
        "1.11 想多了解：在 GitHub 上添加 Signing Key（对照 GitHub Docs：Adding a new SSH key to your GitHub account）",
    ],
}

TERMS = [
    {"term": "GitHub", "en": "GitHub",
     "plain": "存放 Git 仓库的网站：给仓库在别处留一份，也能把作品给别人看", "first": "1.11a"},
    {"term": "双重验证", "en": "two-factor authentication, 2FA",
     "plain": "登录时除了密码，还要一样只在你手里的东西，比如手机上的六位数字", "first": "1.11a"},
    {"term": "验证器 App", "en": "authenticator app / TOTP app",
     "plain": "每 30 秒生成一个新的六位数字的手机或电脑程序（TOTP：按时间变化的一次性密码）",
     "first": "1.11a"},
    {"term": "恢复码", "en": "recovery codes",
     "plain": "手机丢了时用来登录的一组一次性备用码", "first": "1.11a"},
    {"term": "密码管理器", "en": "password manager",
     "plain": "专门替你记住密码、加密保存的程序；Mac 自带的一个叫 Passwords（密码）", "first": "1.11a"},
    {"term": "源代码", "en": "source code",
     "plain": "写成一个程序的原文，程序员看的是它", "first": "1.11b"},
    {"term": "包管理器", "en": "package manager",
     "plain": "替你下载、安装、升级命令行程序的程序；Homebrew 是其中一个", "first": "1.11b"},
    {"term": "PATH", "en": "PATH",
     "plain": "终端找命令时按顺序翻的一串文件夹；全大写，和第 0.2 课的路径不是一回事：PATH 是一串路径",
     "first": "1.11b"},
    {"term": "协议", "en": "protocol",
     "plain": "两个程序之间说好的连接方式；这门课里 Git 连 GitHub 用 HTTPS（网址开头的 https）", "first": "1.11b"},
    {"term": "隐私邮箱地址", "en": "noreply email address",
     "plain": "GitHub 给你的一个不收信的邮箱地址，专门写进提交里，不暴露真实邮箱", "first": "1.11c"},
]


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """The site just before 1.11 (state S6), as a practice copy."""
    sc.site_before()
    sc.todo("网站的练习副本在这里：" + sc.show(sc.facts["site"]))


PEOPLE = ["xiaolin", "aqing", "xiaozhou", "amu", "xiaohe", "ayuan"]
PRIVATE_DOMAINS = ["example.com", "example.net", "example.org"]
NOREPLY_RE = re.compile(r"^(\d+\+)?[a-z0-9](?:[a-z0-9-]*[a-z0-9])?@users\.noreply\.github\.com$",
                        re.IGNORECASE)


def _is_noreply(address):
    return bool(NOREPLY_RE.match((address or "").strip()))


def build_x1(sc):
    """A small repository whose history mixes noreply and personal e-mails.

    Form A: exactly one commit carries a personal address (name it).
    Form B: several commits; count the ones that use a noreply address.
    """
    repo = "site-" + sc.word()
    people = sc.sample(PEOPLE, 2)
    noreply = [(p, "{}+{}@users.noreply.github.com".format(sc.randint(1000000, 99999999), p))
               for p in people]
    personal = (people[0], "{}.{}@{}".format(people[0], sc.word(), sc.pick(PRIVATE_DOMAINS)))
    sc.git_init(repo)
    if sc.form == "A":
        total = sc.randint(4, 6)
        leak = sc.randint(2, total - 1)        # neither the oldest nor the newest commit
        plan = [personal if n == leak else sc.pick(noreply) for n in range(1, total + 1)]
    else:
        total = sc.randint(5, 7)
        plan = [sc.pick(noreply + [personal]) for _ in range(total)]
        if all(not _is_noreply(email) for _, email in plan):
            plan[0] = noreply[0]
        if all(_is_noreply(email) for _, email in plan):
            plan[-1] = personal
    for number, author in enumerate(plan, 1):
        sc.write("{}/page-{}.html".format(repo, number), "<p>第 {} 页</p>".format(number))
        sc.git_commit(repo, "feat: 添加第 {} 页".format(number), author=author,
                      date=sc.ago(days=total - number + 1))
    sc.fact("repo", repo)
    sc.fact("commits", total)
    sc.fact("noreply", len([1 for _, email in plan if _is_noreply(email)]))


def grade_x1(ctx):
    info = ctx.scenario()
    repo = ctx.need_repo(info.path / info.facts["repo"], "考试仓库")
    commits = repo.commits(limit=50)
    built = info.facts["commits"]
    leaks = [c for c in commits if not _is_noreply(c.author_email)]
    noreply_now = len(commits) - len(leaks)
    noreply_built = info.facts.get("noreply", noreply_now)    # older builds lack the fact
    # The task says 「不要改动这个仓库」: a changed history is the learner's doing,
    # so it is graded 还没达标 (never 检查器出问题); the retest builds a new repository.
    if len(commits) != built:
        saw = "搭好时有 {} 个提交，现在是 {} 个".format(built, len(commits))
    elif noreply_now != noreply_built or (info.form == "A" and len(leaks) != 1):
        saw = "提交个数没变，但作者邮箱和搭好时不一样"
    else:
        saw = ""
    if saw:
        ctx.fail("考试仓库被改动过了：这道题要在搭好时的提交历史上作答",
                 where="考试仓库的提交历史", saw=saw)
        ctx.stop()
    if info.form == "A":
        target = leaks[0].hash
        ctx.ask("哪一个提交的作者邮箱会暴露私人邮箱？写出它的编号（前 7 位）：",
                expected=lambda typed: len(typed) >= 7 and target.startswith(typed))
    else:
        ctx.ask("这个仓库里有几个提交的作者邮箱是 GitHub 的隐私地址（noreply）？",
                expected=noreply_now)


SCENARIOS = {"start": build_start}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def check_a(ctx):
    """Concept plus self-report: TOTP as the primary method, the recovery codes."""
    ctx.quiz(
        "GitHub 现在推荐把哪一种当作双重验证的主要方式？",
        ["手机短信里的验证码", "验证器 App 生成的六位数字", "邮箱里收到的验证码"],
        "B",
        explain="GitHub 文档推荐验证器 App 作主要方式；短信排在后面，邮箱验证码不算双重验证。",
        feedback={
            "A": "短信可能被截获，有的地区还收不到；GitHub 文档把它排在后面。",
            "C": "GitHub 文档写明，邮箱验证不算双重验证：拿到你邮箱的人可以重设密码。",
        },
    )
    ctx.ask("打开你存好的恢复码，数一数：一共有几个？", expected=16)
    ctx.quiz(
        "你的恢复码现在存在哪里？",
        ["还在“下载”文件夹里", "密码管理器里，或者打印出来放在手机以外的地方",
         "~/Developer 下面的一个文件夹里"],
        "B",
        feedback={
            "A": "“下载”文件夹谁都能翻到。照「自己做」把它存进密码管理器，再删掉下载的那份。",
            "C": "~/Developer 下的文件夹会变成仓库，恢复码这类东西永远不进仓库。换个地方存。",
        },
    )


def _cellar_version(resolved):
    match = re.search(r"/Cellar/gh/([0-9][^/]*)/", resolved)
    if not match:
        return None
    return re.sub(r"_\d+$", "", match.group(1))


def _first_version(text):
    numbers = re.search(r"\d+(?:\.\d+)+", text or "")
    return numbers.group(0) if numbers else None


def _ask_where_and_version(ctx, program, found, version):
    """Two answers read off the learner's own screen: `which <program>` and its version."""
    accepted = {found.lower(), ctx.show(found).lower()}
    ctx.ask("which {} 输出的是哪一行？照抄下来：".format(program),
            expected=lambda typed: typed.strip().lower() in accepted)
    label = "Homebrew" if program == "brew" else program
    question = "{} 是哪个版本？写出 {} --version 第一行里的版本号：".format(label, program)
    if version:
        ctx.ask(question, expected=lambda typed: _first_version(typed) == version)
    else:
        ctx.note("检查器读不出这台电脑上 {} 的版本号，只看你写的像不像一个版本号。".format(label))
        ctx.ask(question, expected=re.compile(r".*\d+\.\d+\.\d+.*"))


def check_b(ctx):
    """gh is on PATH; where brew is and its version (a transfer of 跟我做 to another
    program); login by self-report."""
    found = ctx.which("gh")
    if not found:
        ctx.fail("电脑还找不到 gh 这个命令", where="PATH 里的各个文件夹",
                 saw="没有叫 gh 的程序")
        ctx.stop()
    ctx.ok("电脑能找到 gh 这个命令")
    brew = ctx.which("brew")
    if brew:
        result = ctx.run([brew, "--version"], timeout=30)
        line = result.lines[0] if result.ok and result.lines else ""
        version = _first_version(line) if line.startswith("Homebrew") else None
        _ask_where_and_version(ctx, "brew", brew, version)
    else:
        # gh came from somewhere else; ask the same two things about gh itself.
        ctx.note("这台电脑上找不到 brew，前两题改问 gh。")
        _ask_where_and_version(ctx, "gh", found, _cellar_version(str(Path(found).resolve())))
    ctx.quiz(
        "运行 gh auth status，Git operations protocol 后面写的是什么？",
        ["https", "ssh", "没有这一行，屏幕上说还没登录（not logged into any GitHub hosts）"],
        "A",
        explain="登录时选 HTTPS，以后 git push 走 HTTPS，由 gh 存好的令牌来证明身份。",
        feedback={
            "B": "这一课登录时要选 HTTPS。重新运行 gh auth login，从头按顺序回答一遍"
                 "（已经登录过也照样可以重来），问协议的那一题选 HTTPS。",
            "C": "说明登录还没完成。回到「跟我做」里登录的那一步，按顺序回答每个问题。",
        },
    )


def _expand(path_text, ctx):
    text = (path_text or "").strip()
    if text.startswith("~/"):
        return ctx.home / text[2:]
    return Path(text)


# The two commits that the lesson's 跟我做 steps make: (subject, file added).
# The 自己做 commit must be a different, later one.
GUIDED_COMMITS = (("docs: 添加 thanks.txt", "thanks.txt"), ("docs: 试一次签名", "signed.txt"))
CONVENTIONAL_RE = re.compile(r"^[a-z]+(\([^()\s]+\))?!?: \S", re.IGNORECASE)


def _is_guided(repo, commit):
    """True when ``commit`` is one of the commits the lesson text walks the learner through."""
    for subject, added in GUIDED_COMMITS:
        if commit.subject.strip() == subject and repo.changed_files(commit.hash) == [("A", added)]:
            return True
    return False


def _site_commit_part(ctx):
    """Artifact part of 1.11c: the learner's own new commit, made with the current identity."""
    info = ctx.scenario("start")
    name = info.facts["site"]
    folder = info.path / name
    repo = ctx.need_repo(folder, "网站的练习副本 " + name)
    before = info.facts["site_commits"]
    now = repo.commit_count()
    last = repo.commit()
    if now <= before:
        ctx.fail("练习副本里还没有你自己做的新提交",
                 where=ctx.show(folder) + " 的提交历史",
                 saw="还是搭好时的 {} 个提交".format(now))
        return repo
    if _is_guided(repo, last):
        ctx.fail("最新的提交还是课文「跟我做」里的那一个",
                 where=ctx.show(folder) + " 的最新提交",
                 saw="说明是「{}」".format(last.subject.strip()[:30]))
        return repo
    ctx.ok("练习副本里有一个你自己做的新提交")
    if CONVENTIONAL_RE.match(last.subject.strip()):
        ctx.ok("新提交的说明照约定式提交的格式写了")
    else:
        ctx.fail("新提交的说明还不是约定式提交的格式", where="最新提交的第一行",
                 saw="现在是「{}」".format(last.subject.strip()[:30]))
    status = repo.status()
    if not status.clean:
        ctx.note("练习副本里还有 {} 个文件的改动没有提交（git status 能看到）；"
                 "这一站只看你的新提交，它们不影响结果。".format(len(status.entries)))
    effective = repo.config("user.email")
    if effective is None:
        ctx.fail("Git 里还没有设置提交邮箱", where="全局 Git 设置 user.email", saw="没有设置")
    elif (last.author_email or "").lower() != effective.strip().lower():
        ctx.fail("最新提交的作者邮箱和你现在的邮箱设置不一样",
                 where="最新提交的作者邮箱（这里不显示内容）",
                 saw="这个提交是在改设置之前做的，或者用了别的邮箱")
    else:
        ctx.ok("最新提交的作者邮箱就是你现在设置的邮箱（这里不显示内容）")
    return repo


def _looks_like_mistyped_noreply(address):
    """A noreply address copied wrongly: full-width characters, spaces or quotes mixed in."""
    folded = unicodedata.normalize("NFKC", address or "").lower()
    return "noreply" in folded and not _is_noreply(address)


def _email_decision(ctx):
    """The learner says which kind of address is set; the answer is read off the real setting."""
    address = ctx.git_global("user.email")
    if address and "你的用户名" in address:
        ctx.fail("提交邮箱还是课文第 6 步的例子：到 Emails 设置页复制你自己的隐私地址，照第 6 步再设置一次，"
                 "改好以后再做一个新提交",
                 where="全局 Git 设置 user.email（这里不显示内容）",
                 saw="里面还留着例子里的“你的用户名”")
        ctx.stop()
    if _looks_like_mistyped_noreply(address):
        ctx.fail("提交邮箱像是隐私地址，但没有抄对：照第 6 步重新复制、再设置一次，改好以后再做一个新提交",
                 where="全局 Git 设置 user.email（这里不显示内容）",
                 saw="里面有 noreply，整体却不像 Emails 设置页给出的隐私地址（可能混进了全角字符、空格或引号）")
        ctx.stop()
    noreply = _is_noreply(address)
    if noreply and address.strip().startswith("12345678+"):
        ctx.note("你的隐私地址开头的编号是 12345678，和课文例子一样。如果是照抄的例子，"
                 "换成 Emails 设置页上你自己的那串数字，再做一个新提交。")
    right = ctx.quiz(
        "你现在的全局提交邮箱（git config get user.email 显示的那个）是哪一种？",
        ["GitHub 给的隐私地址（…@users.noreply.github.com）", "我自己的邮箱"],
        "A" if noreply else "B",
        feedback={
            "A": "检查器看到的地址不是 …@users.noreply.github.com 这种样子（这里不显示内容）。"
                 "想用隐私地址，照第 6 步把它复制过来再设置一次。",
            "B": "检查器看到全局设置里已经是隐私地址了。想用自己的邮箱，照第 6 步改回去。",
        },
    )
    if right:
        if not noreply:
            ctx.note("你决定继续用自己的邮箱，它会跟着每个提交公开。如果它是你 GitHub 账号里的邮箱，"
                     "回到 Emails 页把 Block command line pushes that expose my email 的勾去掉，"
                     "不然第 1.12 课的推送会被 GitHub 拦下（GH007）。")
        ctx.decide("commit_email", "noreply" if noreply else "own")


def _signing_decision(ctx, repo):
    """The learner says whether signing is on; the answer is read off the real setting."""
    state = ctx.git_global_state("commit.gpgsign")
    if state == "invalid":
        ctx.fail("commit.gpgsign 的值写错了：修好之前每次提交都会失败",
                 where="全局 Git 设置 commit.gpgsign", saw="值既不是 true 也不是 false")
        ctx.stop()
    signing = state == "true"
    right = ctx.quiz(
        "你现在的提交签名是哪一种？",
        ["先不签名（自动签名关着）", "用 SSH 签名（照本课最后「想多了解」里那一节配好了）"],
        "B" if signing else "A",
        feedback={
            "A": "检查器看到自动签名还开着（commit.gpgsign 是 true）。"
                 "想先不签名，运行 git config set --global commit.gpgsign false。",
            "B": "检查器看到自动签名是关着的。想用 SSH 签名，照本课最后「想多了解」里签名那一节做完。",
        },
    )
    if not right:
        return
    if not signing:
        ctx.ok("自动签名是关着的，和你说的一致")
        ctx.decide("commit_signing", "off")
        return
    fmt = (ctx.git_global("gpg.format") or "").strip().lower()
    key = ctx.git_global("user.signingkey")
    programs = ctx.git_global_all("gpg.ssh.program")
    problems = []
    if fmt != "ssh":
        problems.append(("签名格式还不是 SSH", "全局 Git 设置 gpg.format",
                         "现在是「{}」".format(fmt or "没有设置")))
    if not key or not _expand(key, ctx).is_file():
        problems.append(("签名用的公钥文件找不到", "全局 Git 设置 user.signingkey",
                         "没有设置，或者指向的文件不存在"))
    if programs and not programs[-1].strip():          # Git uses the last value
        problems.append(("签名程序的设置是空的，签名会失败", "全局 Git 设置 gpg.ssh.program",
                         "这一项存在，但值是空的"))
    for missing, where, saw in problems:
        ctx.fail(missing, where=where, saw=saw)
    if problems:
        return
    ctx.ok("SSH 签名的设置都齐了")
    raw = repo.query("cat-file", "-p", "HEAD")
    if raw.ok and "-----BEGIN SSH SIGNATURE-----" in raw.out:
        ctx.ok("最新提交上有 SSH 签名")
    else:
        ctx.fail("最新提交上没有签名", where="练习副本的最新提交",
                 saw="里面没有 SSH 签名，多半是在打开签名之前做的")
    ctx.decide("commit_signing", "ssh")


def check_c(ctx):
    repo = _site_commit_part(ctx)
    if ctx.failed:
        ctx.stop()
    _email_decision(ctx)
    _signing_decision(ctx, repo)


checks = {"1.11a": check_a, "1.11b": check_b, "1.11c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.11a": [
        "三道题分别问：GitHub 推荐的主要方式、你手里的恢复码有几个、你把它们存在了哪里。后两道只有亲手做过才答得出。",
        "恢复码在开启双重验证时下载的那个文件里，或者在你存进密码管理器、打印出来的那一份里。"
        "找不到了：在 GitHub 的 Settings → Password and authentication 页面，Recovery codes 旁边点 View。",
        "相似的例子：银行给你一张刮刮卡，上面印着一组一次性密码，每个用一次就作废。"
        "GitHub 的恢复码也是一组，一行一个，数行数就行。",
        "答案：第一题选 B，验证器 App 是 GitHub 推荐的主要方式。第二题是 16 个。"
        "第三题选 B：存进密码管理器（比如 Mac 自带的 Passwords App），或者打印出来放在手机以外的地方，"
        "然后删掉“下载”文件夹里的那份。"
        "解释：短信可能被截获，邮箱验证码不算双重验证；恢复码平时不用，是手机丢了时最可靠的备用钥匙。",
    ],
    "1.11b": [
        "这一站要的是三件事：电脑找得到 gh、你说得出终端用的是哪个位置的 brew 和它的版本、gh 已经登录。"
        "检查结果里“还缺什么”说的是哪一件？",
        "先运行 which gh。如果它说 gh not found，回到「跟我做」里安装的那一步。"
        "然后用「跟我做」里查 gh 的那两条命令的问法去查 brew；最后运行 gh auth status，答案都在输出里。",
        "相似的例子：查 git 在哪里、什么版本，就运行 which git 和 git --version。brew 也是一样的问法。",
        "答案：which brew 输出 /opt/homebrew/bin/brew；版本号是 brew --version 第一行 Homebrew 后面的数字"
        "（课程核对时是 7.0.10，你的可能更新）；"
        "gh auth status 里 Git operations protocol 后面应该是 https，所以最后一题选 A。"
        "还没登录就先运行 gh auth login，依次选 GitHub.com、Login with a web browser、HTTPS、Yes。"
        "解释：brew 自己和它装的 gh 都在 /opt/homebrew/bin，这个文件夹早就在 PATH 里，所以敲 brew、gh 都找得到。",
    ],
    "1.11c": [
        "检查看四样：练习副本里有没有一个你自己做的、不是课文「跟我做」里的新提交；"
        "它的说明是不是约定式提交的格式；它的作者邮箱是不是你现在的设置；你说的邮箱和签名是不是和设置一致。",
        "先在练习副本里运行 git log -1 --format='%h %s %ae'（%s 是提交说明的第一行），看最新提交的说明和作者邮箱。"
        "说明是 docs: 添加 thanks.txt 或 docs: 试一次签名，说明你还没做自己的那个提交；"
        "邮箱不是你刚设好的那个，说明这个提交是改设置之前做的。两种情况都再做一个新提交。",
        "相似的例子：换了新手机号以后，只有以后发出的短信显示新号码，以前发过的还是旧号码。"
        "Git 的提交邮箱也是这样，改了设置要再提交一次才看得到。",
        "答案：在练习副本里改一个文件或新建一个文件（不要用 thanks.txt 和 signed.txt），"
        "git add 它，再 git commit -m \"docs: 在 README 里加一句致谢\" 这样照约定式提交写说明。"
        "运行检查时，第一题按 git config get user.email 显示的地址是不是 …@users.noreply.github.com 来选；"
        "第二题：没做本课最后「想多了解」里的 SSH 签名就选 A，做了就选 B，而且这个新提交要在打开签名之后做。"
        "解释：作者邮箱和签名都是提交那一刻写进去的，所以要在设置改好之后再提交一次。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.11-r1", "type": "recall", "tier": "fluent", "station": "1.11a", "rule": "ACC-01",
     "q": "GitHub 开启双重验证后会给你一组恢复码。它们该存在哪里？为什么？",
     "a": "存进密码管理器（比如 Mac 自带的 Passwords App）或打印出来，放在手机以外的地方，"
          "不放进任何仓库文件夹。手机丢了时靠它登录，每个只能用一次；GitHub 客服不能替你恢复登录，"
          "剩下的只有一个要额外证明、要等几个工作日的人工审核。"},
    {"id": "1.11-r2", "type": "which", "tier": "fluent", "station": "1.11a", "rule": "ACC-01",
     "q": "给 GitHub 账号开双重验证，GitHub 推荐用哪一种作为主要方式？",
     "options": ["手机短信验证码", "验证器 App（TOTP）", "邮箱里收到的验证码"],
     "answer": "B",
     "explain": "GitHub 推荐验证器 App 作主要方式；短信有被截获的风险；邮箱验证码不算双重验证。"},
    {"id": "1.11-r3", "type": "fault", "tier": "fluent", "station": "1.11b",
     "q": "一篇教程说：第一次 git push 到 GitHub 时，终端问 Password，就输入你的 GitHub 账号密码。哪里不对？",
     "options": ["GitHub 自 2021 年 8 月起不再接受账号密码做 Git 操作",
                 "没有不对，GitHub 账号密码在终端里照样能用",
                 "要先在网页上关掉双重验证，账号密码才能在终端里用"],
     "answer": "A",
     "explain": "账号密码只用来在网页上登录。命令行里由 gh auth login 存好的令牌证明身份；关掉双重验证既没用也不安全。"},
    {"id": "1.11-r4", "type": "which", "tier": "lookup", "station": "1.11b",
     "q": "想知道这台电脑上的 gh 登录的是哪个账号、Git 操作走哪种协议（HTTPS 还是 SSH），运行哪条命令？",
     "options": ["gh auth login", "gh auth status", "which gh"],
     "answer": "B",
     "explain": "gh auth status 只看不改；gh auth login 会重新登录；which gh 只告诉你程序在哪个文件夹。"},
    {"id": "1.11-r5", "type": "predict", "tier": "fluent", "station": "1.11c", "rule": "ACC-02",
     "q": "你用 git config set --global user.email 把提交邮箱改成了 GitHub 的隐私地址。以前做过的提交里，作者邮箱会怎样？",
     "options": ["全部自动换成新地址", "不变，只有以后的新提交用新地址", "全部变成空的"],
     "answer": "B",
     "explain": "作者邮箱是提交那一刻写进去的，改设置只影响以后的提交。公开以前的历史前，要先检查里面的旧邮箱。"},
    {"id": "1.11-r6", "type": "recall", "tier": "lookup", "station": "1.11c",
     "q": "（第 1.11 课「想多了解」）在这台电脑上改用 SSH 给提交签名，全局 Git 设置要改哪几项？",
     "a": "gpg.format 设成 ssh；user.signingkey 设成公钥文件 ~/.ssh/id_ed25519.pub；commit.gpgsign 设成 true；"
          "如果全局设置里有一项空的 gpg.ssh.program，要删掉它（git config unset --global gpg.ssh.program）。"
          "然后在 GitHub 上把同一把公钥添加为 Signing Key。"},
]


# ---------------------------------------------------------------------------
# EXAM (gate-1)
# ---------------------------------------------------------------------------
EXAM = [
    {
        "id": "1.11-x1",
        "gate": "gate-1",
        "title": "从提交历史里找出暴露的邮箱",
        "minutes": 4,
        "build": build_x1,
        "task": {
            "A": "仓库 {dir}/{repo} 准备公开。它的 {commits} 个提交里，有一个的作者邮箱是私人邮箱，"
                 "其余用的都是 GitHub 的隐私地址。找出那一个提交；评分时会问你它的编号（前 7 位）。不要改动这个仓库。",
            "B": "进入 {dir}/{repo}，查看全部 {commits} 个提交的作者邮箱。"
                 "评分时会问你：其中有几个用的是 GitHub 的隐私地址（noreply）。不要改动这个仓库。",
        },
        "grade": grade_x1,
    },
]
