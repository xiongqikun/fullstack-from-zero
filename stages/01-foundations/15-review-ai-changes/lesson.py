"""Lesson 1.15 验收 AI 的改动 (plan section 4).

Station a: let the tutor change ~/Developer/my-site in 干活 mode, then review
           the uncommitted change (git status, git diff --stat, git diff, the
           page) and decide: commit it yourself or throw it away.
Station b: (worked example: fx-tool; exercise: ai-change/my-site with
           ai-change/ai-report.txt; both built by scenario 1.15a, so that the
           station needs no second setup) spot the three planted problems in an
           "AI change" (an unrelated file modified, a key-like file added, a
           wrong commit type) and clean up with commands taught in 1.2, 1.8 and
           1.10; the commit message of an AI change is yours to write: right
           type, AI named in a trailer.  Scenario 1.15-ai-change builds the
           same exercise on its own for review item 1.15-d1 (not named
           1.15b, so that `scenario 1.15b` does not build a copy the station
           check never looks at).
Station c: the project instruction file CLAUDE.md (AGENTS.md only as an
           optional box).

Rules: AI-01 and AI-02 (both station b).  Gate: gate-1.
Free decisions (accept or reject, who wrote CLAUDE.md) use ctx.choose.
Standard library only; must import on Python 3.9.
"""

import datetime
import json
import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.15",
    "slug": "15-review-ai-changes",
    "title": "验收 AI 的改动",
    "stage": 1,
    "prerequisites": ["1.14"],
    "stations": [
        {
            "id": "1.15a",
            "title": "让 AI 干活，你来验收",
            "minutes": 40,
            "new_concept": "AI 交来的改动是一份待验收的提案：看过改动清单再决定收下还是退回",
            "new_commands": ["git diff --stat"],
        },
        {
            "id": "1.15b",
            "title": "找茬：一次 AI 改动里的三处问题",
            "minutes": 40,
            "new_concept": ("以改动本身为准，不以 AI 的说明为准：多改的文件、多出的文件、写错的提交说明"
                            "都由你核对，提交说明由你来写"),
            "new_commands": [],
        },
        {
            "id": "1.15c",
            "title": "给 AI 立规矩",
            "minutes": 40,
            "new_concept": "项目说明文件：把给 AI 的规矩写进仓库里的 CLAUDE.md，在这个项目里开工时它先读",
            "new_commands": [],
        },
    ],
    "rules": ["AI-01", "AI-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9"},
    },
    "unverified_steps": [
        "1.15a：在 Claude 桌面应用里切换到干活模式，请导师改 ~/Developer/my-site（导师的回答和改法每次不同）",
        "1.15a：open index.html 在浏览器里看网页（建课环境不能打开浏览器）",
        "1.15c：用 code CLAUDE.md 在 VS Code 里编辑文件（图形界面）",
        "1.15c（想多了解）：在 Claude 桌面应用里把 my-site 选作项目文件夹，让新会话读到 CLAUDE.md",
    ],
}

TERMS = [
    {"term": "验收", "en": "acceptance review",
     "plain": "按清单核对别人交来的改动，再决定收下还是退回", "first": "1.15a"},
    {"term": "改动统计", "en": "diffstat",
     "plain": "git diff --stat 打印的那几行：哪些文件改了、各改了多少行", "first": "1.15a"},
    {"term": "范围外的改动", "en": "out-of-scope change",
     "plain": "没让改却被改了的地方，常常藏在别的文件里", "first": "1.15b"},
    {"term": "项目说明文件", "en": "project instruction file (CLAUDE.md, AGENTS.md)",
     "plain": "放在仓库根目录、写给 AI 看的项目规矩，在这个项目里开工时 AI 先读它", "first": "1.15c"},
    {"term": "尾注", "en": "trailer",
     "plain": "提交说明末尾“名字: 内容”格式的行，第 1.10 课说的脚注里的一种，比如写明 AI 参与了这次提交",
     "first": "1.15b"},
]

# Conventional Commits 1.0.0: a type, an optional scope in parentheses (any
# noun; lesson 1.10 accepts any text without spaces or parentheses, also
# Chinese), an optional !, then ": " and the description.
CC_SUBJECT = re.compile(r"^([a-z]+)(\([^()\s]+\))?!?: \S")
CC_PREFIX = re.compile(r"^([A-Za-z]+)(\([^()\s]+\))?!?$")
ATTRIBUTION_KEYS = ("Co-authored-by", "Assisted-by", "Generated-by")
PAGE_FILES = ("index.html", "style.css")

# A commit cannot be rewritten with what the learner knows (commit --amend is
# stage 2, plan section 4); in the real my-site the way out is one more commit
# of a change the learner really wants, not a meaningless edit.
REDO_NOTE = ("已经做好的提交改不了（改写提交的命令要到阶段 2 才学），它就留在历史里。"
             "办法：{what}，用正确的写法再提交一次；检查看的是{which}。")
REDO_PAGE = dict(what="给网页再做一处你真想要的小改动（比如把页脚那句话改得更顺），验收后",
                 which="这一课里最新一次改了网页的提交")
REDO_RULES = dict(what="给 CLAUDE.md 再加一条你想要的规矩，或者把一条改得更具体",
                  which="最新一次改 CLAUDE.md 的提交")
RESET_NOTE = ("已经进了提交的东西，用学过的命令改不回那次提交。重搭一份练习再做最省事："
              "python3 tools/course.py scenario {key} --reset")
LOST_NOTE = "那一节是 AI 写的、还没提交过，退回以后用学过的命令找不回来。"


def _commit_type(subject):
    m = CC_SUBJECT.match(subject or "")
    return m.group(1) if m else None


def _subject_problem(subject):
    """None for a Conventional Commits subject, else (missing, saw) naming the real cause."""
    text = subject or ""
    if CC_SUBJECT.match(text):
        return None
    saw = "现在是「%s」" % _short(text)
    half, full = text.find(":"), text.find("：")
    if full != -1 and (half == -1 or full < half):
        if re.match(r"^[A-Za-z]+", text):
            return ("类型后面的冒号要用半角的 :（英文冒号），后面再空一格", saw)
        return ("提交说明开头还缺类型前缀", saw)
    if half == -1:
        return ("提交说明开头还缺类型前缀", saw)
    prefix, rest = text[:half], text[half + 1:]
    match = CC_PREFIX.match(prefix)
    if not match:
        if CC_PREFIX.match(prefix.rstrip()):
            return ("冒号要紧跟在类型后面，中间不空格", saw)
        if re.match(r"^[A-Za-z]+\s*[（(]", prefix):
            if "（" in prefix or "）" in prefix:
                return ("范围的圆括号要用半角的 ( )", saw)
            if "()" in prefix:
                return ("范围的圆括号里还没写字（不写范围，就连括号一起去掉）", saw)
            return ("范围写在类型后面的一对圆括号里，里面不能有空格，也不能再套括号", saw)
        return ("提交说明开头还缺类型前缀", saw)
    if match.group(1) != match.group(1).lower():
        return ("类型要用小写英文字母", saw)
    if not rest.strip():
        return ("冒号后面还缺一句描述", saw)
    if not rest.startswith(" "):
        return ("类型后面的冒号之后要空一格", saw)
    return ("冒号后面只空一格，再写描述", saw)


def _short(text, limit=30):
    text = (text or "").replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"


# ---------------------------------------------------------------------------
# Practice material
# ---------------------------------------------------------------------------
STUDY_SECTION = """
    <h2>我在学什么</h2>
    <ul>
      <li>终端：新建、复制、查找文件</li>
      <li>Git：提交、看改动、撤销</li>
      <li>GitHub：备份和发布网页</li>
    </ul>
"""

# Station b and the exam: a requested section plus planted problems.
TOOLS_SECTIONS = {
    "我常用的工具": ["终端（Terminal）", "VS Code", "Git 和 GitHub"],
    "我最近读的资料": ["Pro Git 第 2 章", "MDN 的 HTML 入门", "Conventional Commits 1.0.0"],
    "我下个月的目标": ["学会写一个小程序", "每周复习三次", "给网页加一张照片"],
}
SECRET_FILES = {
    "config.local.json": '{{\n  "weather_api_key": "wk-live-{key}"\n}}\n',
    "api-key.txt": "WEATHER_API_KEY=wk-live-{key}\n",
    "secrets.js": 'const WEATHER_API_KEY = "wk-live-{key}";\n',
}
WRONG_TYPES = ["fix", "docs"]

STYLE_EDITS = [
    ("  line-height: 1.7;\n", "  line-height: 2.2;\n"),
    ("  max-width: 40rem;\n", "  max-width: 60rem;\n"),
    ("  font-family: system-ui, sans-serif;\n", "  font-family: serif;\n"),
]

# Every rule sentence printed in lesson.md (the draft's lines, the fix, and the
# examples of 1.15c 自己做): copying them does not count as writing your own.
SAMPLE_RULES = [
    "只改我点名的文件；想顺手改别的，先列出来问我。",
    "不新建文件，除非我同意。",
    "改完不要提交，等我看完 git diff 自己提交。",
    "改完直接提交并推送，不用等我看。",
    "改 style.css 之前，先告诉我要改哪一条",
    "网页上不要出现我的真名、电话和住址",
    "每次只做一件事，做完用三句话告诉我改了什么",
]

DRAFT_CLAUDE_MD = """
    # my-site：给 AI 的项目说明

    这是一个只有一页的个人网页，我用它学做软件。仓库是公开的。

    ## 规矩

    - 只改我点名的文件；想顺手改别的，先列出来问我。
    - 不新建文件，除非我同意。
    - 改完直接提交并推送，不用等我看。
"""


REPORT = """
    AI 的交付说明
    =============

    任务：在首页的列表下面加一节「{title}」。

    我做了什么：在 index.html 里加了一个小标题和三条列表。其他文件没有动。

    建议的提交说明：{wrong}: 在首页加上{title}
"""


def _section_html(title, items):
    lines = ["", "    <h2>%s</h2>" % title, "    <ul>"]
    lines += ["      <li>%s</li>" % item for item in items]
    lines += ["    </ul>"]
    return "\n".join(lines) + "\n"


def _insert_after_list(html, block):
    """Insert ``block`` after the first </ul> of the page."""
    marker = "    </ul>\n"
    at = html.find(marker)
    if at < 0:
        raise RuntimeError("index.html has no </ul> line")
    at += len(marker)
    return html[:at] + block + html[at:]


def _read(sc, rel):
    return sc.path(rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """State S7: the learner's site, public remote, page online."""
    sc.site_before()
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))


B_FOLDER = "ai-change"
B_KEYS = ("site", "base", "base_commits", "title", "unrelated", "secret", "wrong_type", "touched")


def build_a(sc):
    """Everything stations a and b practise on, built once.

    my-site: an S7 copy with one clean, uncommitted change made 'by the tutor'
    (station a, worked example).  fx-tool: a small converter repository with an
    AI change that hides an out-of-scope edit and a stray new file (station b,
    worked example).  ai-change/: an S7 copy with an AI change hiding three
    problems plus the AI's report (station b, exercise; its facts carry the
    prefix "b_").  Station b thus starts without a second scenario.
    """
    b = _plant_b(sc, B_FOLDER)
    for key in B_KEYS:
        sc.fact("b_" + key, b[key])
    sc.site_before()          # after _plant_b: these facts describe station a's copy
    rel = sc.facts["site"]
    html = _read(sc, rel + "/index.html")
    sc.write(rel + "/index.html", _insert_after_list(html, STUDY_SECTION), exact=True)
    sc.fact("heading", "我在学什么")
    _build_fx_demo(sc)
    sc.todo("网站副本：" + sc.show(rel) + "（导师刚改完，还没提交；第 1 站用）")
    sc.todo("练习仓库：" + sc.show("fx-tool") + "（AI 刚改完，还没提交；第 2 站用）")
    sc.todo("AI 的另一次改动：" + sc.show(B_FOLDER) + "（网站副本和 AI 的交付说明；第 2 站「自己做」用）")


def _plant_problems(sc, rel, title, items, unrelated, secret, key):
    """Requested section in index.html + one unrelated edit + one key-like file."""
    html = _read(sc, rel + "/index.html")
    sc.write(rel + "/index.html", _insert_after_list(html, _section_html(title, items)), exact=True)
    if unrelated == "style.css":
        before = _read(sc, rel + "/style.css")
        old, new = sc.pick(STYLE_EDITS)
    else:
        before = _read(sc, rel + "/README.md")
        old, new = "还在学习中，会一点一点改。", "已经完成，不再更新。"
    after = before.replace(old, new, 1)
    if after == before:
        raise RuntimeError("the unrelated edit did not apply to " + unrelated)
    sc.write(rel + "/" + unrelated, after, exact=True)
    sc.write(rel + "/" + secret, SECRET_FILES[secret].format(key=key), exact=True)


def _plant_b(sc, base="."):
    """S7 copy under ``base`` with an AI change hiding three problems, plus the
    AI's report next to it.  Returns the facts of the exercise (not recorded)."""
    sc.site_before(base=base)
    rel = sc.facts["site"]
    head = sc.git(rel, "rev-parse", "HEAD").strip()
    title = sc.pick(sorted(TOOLS_SECTIONS))
    unrelated = sc.pick(["style.css", "README.md"])
    secret = sc.pick(sorted(SECRET_FILES))
    wrong = sc.pick(WRONG_TYPES)
    key = "%08x%08x" % (sc.randint(0, 0xFFFFFFFF), sc.randint(0, 0xFFFFFFFF))
    _plant_problems(sc, rel, title, TOOLS_SECTIONS[title], unrelated, secret, key)
    report = "ai-report.txt" if base == "." else base + "/ai-report.txt"
    sc.write(report, REPORT.format(title=title, wrong=wrong))
    return {"site": rel, "base": head, "base_commits": sc.facts["site_commits"],
            "title": title, "unrelated": unrelated, "secret": secret,
            "wrong_type": wrong, "touched": 3, "report": report}


def build_b(sc):
    """Review item 1.15-d1: the exercise of station b on its own."""
    b = _plant_b(sc)
    for key in B_KEYS:
        sc.fact(key, b[key])
    sc.todo("AI 的交付说明：" + sc.show(b["report"]))
    sc.todo("网站副本：" + sc.show(b["site"]) + "（AI 刚改完，还没提交）")


def _build_fx_demo(sc):
    """The worked example of station b: a small converter repository."""
    sc.copy_in("starter/hello-fx", "fx-tool")
    sc.git_init("fx-tool")
    sc.git_commit("fx-tool", "第一版换算程序", date=sc.ago(days=2))
    code = _read(sc, "fx-tool/convert.py")
    line = '    print(f"{AMOUNT_USD} 美元 ≈ {amount_cny:.2f} 人民币（按 1 美元 = {USD_TO_CNY:.2f} 人民币计算）")\n'
    if line not in code:
        raise RuntimeError("starter/hello-fx/convert.py changed")
    code = code.replace(line, line + '    print("提醒：这是示例汇率，不是真实汇率")\n', 1)
    sc.write("fx-tool/convert.py", code, exact=True)
    rates = _read(sc, "fx-tool/rates.txt")
    sc.write("fx-tool/rates.txt", rates.replace("CNY  人民币    7.10", "CNY  人民币    7.30", 1), exact=True)
    sc.write("fx-tool/ai-scratch.txt", """
        草稿：我先试了两种写法，留着备用。
        print("注意：示例汇率")
    """)
    sc.fact("repo", "fx-tool")


def build_c(sc):
    """S7 copy with an AI-drafted, uncommitted CLAUDE.md (one bad rule)."""
    sc.site_before()
    rel = sc.facts["site"]
    sc.write(rel + "/CLAUDE.md", DRAFT_CLAUDE_MD)
    sc.todo("网站副本：" + sc.show(rel) + "（AI 起草的 CLAUDE.md 还没提交）")


SCENARIOS = {
    "start": build_start,
    "1.15a": build_a,
    "1.15-ai-change": build_b,
    "1.15c": build_c,
}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _local(text):
    """An ISO date-time (with or without offset) as a naive local datetime, or None."""
    try:
        moment = datetime.datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None
    if moment.tzinfo is not None:
        moment = moment.astimezone().replace(tzinfo=None)
    return moment


def _first_sign_of_lesson(ctx):
    """The earliest moment that shows lesson 1.15 had begun, or None.

    Candidates: the first build of scenario 1.15a in learner/log.jsonl (a
    --reset later does not move it), the build time of the copy there now,
    and the first pass of any 1.15 station.  The worked example of station a
    builds 1.15a before the 自己做, so this comes before the learner's commit.
    """
    found = []
    log = ctx.read(ctx.workspace / "learner" / "log.jsonl", default="")
    for line in log.splitlines():
        if '"scenario-built"' not in line or '"1.15a"' not in line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("type") == "scenario-built" \
                and event.get("scenario") == "1.15a":
            found.append(_local(event.get("ts") or ""))
    info = ctx.scenario("1.15a", required=False)
    if info.exists:
        found.append(_local(info.built or ""))
    for station, record in (ctx.state.get("stations") or {}).items():
        if station.startswith("1.15") and isinstance(record, dict):
            found.append(_local(record.get("first_pass") or ""))
    found = [moment for moment in found if moment is not None]
    return min(found) if found else None


def _lesson_start(ctx):
    """When this lesson began at the earliest, or None when nothing tells.

    The newest first pass of a station outside 1.15 that came before the
    first sign of this lesson (the learner finished the previous work then);
    a station of an earlier lesson passed later (one the learner had skipped)
    does not move it.  Without such a pass (a new or rebuilt state file) the
    first sign of this lesson itself.  Never a guess such as "a week ago":
    that would reach back to commits of earlier lessons.
    """
    begun = _first_sign_of_lesson(ctx)
    newest = None
    for station, record in (ctx.state.get("stations") or {}).items():
        if station.startswith("1.15") or not isinstance(record, dict):
            continue
        moment = _local(record.get("first_pass") or "")
        if moment is None or (begun is not None and moment > begun):
            continue
        if newest is None or moment > newest:
            newest = moment
    return newest if newest is not None else begun


def _page_commits(repo, since):
    """Commits made since ``since`` that changed the page, newest first."""
    found = []
    for commit in repo.commits(limit=30):
        moment = _local(commit.date)
        if moment is None:
            continue
        if moment < since:
            break
        if any(path in PAGE_FILES for _letter, path in repo.changed_files(commit.hash)):
            found.append(commit)
    return found


def _accepted_commit(repo, since):
    """Newest commit made since ``since`` that changed the page, or None."""
    found = _page_commits(repo, since)
    return found[0] if found else None


def check_a(ctx):
    """Real ~/Developer/my-site: the tutor's change was reviewed and decided."""
    repo = ctx.need_repo(ctx.my_site, "你的网站文件夹 my-site")
    status = repo.status()
    if not status.clean:
        names = "、".join(e.path for e in status.entries[:3])
        ctx.fail("还有改动没有处理完：要的提交，不要的退回",
                 where="my-site 的 git status", saw="还有改动：" + _short(names, 40))
        ctx.stop()
    since = _lesson_start(ctx)
    if since is None:
        # No record says when this lesson began: the worked example's scenario
        # is the anchor, so ask for it (ends the check; not counted as a try).
        ctx.note("检查要靠第 1 站「跟我做」搭的练习场景 1.15a，才知道这一课从什么时候开始。")
        ctx.scenario("1.15a")
        raise RuntimeError("scenario 1.15a exists but has no build time")
    choice = ctx.choose("这次验收你最后怎么决定的？",
                        [("accept", "收下了：我自己提交了（全部或一部分）"),
                         ("reject", "退回了：我用 git restore 丢掉了改动")])
    commit = _accepted_commit(repo, since)
    if choice == "accept":
        if commit is None:
            ctx.fail("没找到你收下改动的那次提交",
                     where="my-site 里开始这一课以后的提交", saw="没有改过网页的新提交")
            ctx.stop()
        ctx.ok("找到了收下的那次提交：" + _short(commit.subject))
        problem = _subject_problem(commit.subject)
        if problem:
            ctx.fail(problem[0], where="那次提交的第一行", saw=problem[1])
            ctx.note(REDO_NOTE.format(**REDO_PAGE))
            ctx.stop()
        ctx.ok("提交说明是约定式提交的格式")
        ctx.ask("那次提交「%s」一共改了几个文件？（git commit 打印的第二行写着；"
                "也可以用 git log --stat -1 再看一次）" % _short(commit.subject, 24),
                expected=len(repo.changed_files(commit.hash)))
        if not any(_trailers(repo, c.hash) for c in _page_commits(repo, since)):
            # Taught in station b; here a reminder, not a redo (a commit cannot be
            # rewritten in stage 1, and a later commit of your own needs no trailer).
            ctx.note("这次改动是导师做的，按行规 AI-02，提交说明里该有一行写明 AI 参与的尾注"
                     "（第二个 -m 写的 Co-Authored-By: Claude <noreply@anthropic.com>）。"
                     "这次没写，它就留在历史里；第 2 站细讲，以后 AI 参与的提交记得加。")
        return
    if commit is not None:
        ctx.fail("你选的是退回，可 my-site 里有一次这一课里改了网页的提交",
                 where="my-site 里开始这一课以后的提交",
                 saw="「%s」" % _short(commit.subject))
        ctx.note("如果你其实收下了改动（哪怕只收下一部分），再检查一次，选“收下了”。")
        ctx.stop()
    # git restore rewrites the file, so a real rejection leaves a fresh mtime.
    touched = [name for name in PAGE_FILES
               if (ctx.mtime(ctx.my_site / name) or datetime.datetime.min) > since]
    if not touched:
        ctx.fail("没看到退回的痕迹：网页文件在这一课里还没被改过", where="my-site 里的 index.html 和 style.css",
                 saw="开始这一课以后没有改动过")
        ctx.note("先做完「自己做」的第 1 到 4 步：请导师改，你来验收，再决定收下还是退回。")
        ctx.stop()
    ctx.ok("改动已经退回，my-site 是干净的")
    ctx.note("退回也是一种验收结果。想再试，就把要求写得更具体，或者请导师只改你点名的那一处。")


def _intro_commit(repo, base, marker, path):
    """The oldest commit after ``base`` whose ``path`` contains ``marker``, or None."""
    for sha in repo.query("rev-list", "--reverse", base + "..HEAD").lines:
        if marker in (repo.file_at(sha, path) or ""):
            return repo.commit(sha)
    return None


def _check_b_work(ctx, key, station=False):
    info = ctx.scenario(key)
    if station:
        if "b_site" not in info.facts:
            # Built by an older version of this lesson, before station b's
            # exercise moved into scenario 1.15a: nothing of the learner's is lost.
            ctx.fail("练习场景 1.15a 是旧版本搭的，里面没有第 2 站「自己做」的网站副本",
                     where=ctx.show(info.path), saw="没有 " + B_FOLDER + " 文件夹的记录")
            ctx.note("重搭一份再做：python3 tools/course.py scenario 1.15a --reset")
            ctx.stop()
        facts = dict((k, info.facts["b_" + k]) for k in B_KEYS)
    else:
        facts = info.facts
    repo = ctx.need_repo(info.path / facts["site"], "网站副本 my-site")
    secret = facts["secret"]
    unrelated = facts["unrelated"]
    base = facts["base"]
    original = repo.file_at(base, unrelated)
    if original is None:
        raise RuntimeError("scenario base lacks " + unrelated)
    on_disk = ctx.read(repo.path / unrelated, default=None)
    commits = repo.commit_count()
    # Before any attempt, do not name what the learner is meant to find.
    started = (commits > facts["base_commits"] or not ctx.exists(repo.path / secret)
               or on_disk == original
               or facts["title"] not in ctx.read(repo.path / "index.html"))
    redo = False

    # 1. the key-like file: gone and never committed
    if repo.query("log", "--all", "--format=%h", "--", secret).lines:
        ctx.fail("像密钥的那个文件进了提交历史", where="仓库的提交历史",
                 saw="有提交里带着 " + secret)
        redo = True
    elif ctx.exists(repo.path / secret):
        if started:
            ctx.fail("像密钥的那个文件还在文件夹里", where=ctx.show(repo.path), saw="还有 " + secret)
        else:
            ctx.fail("AI 多出来的新文件还没处理", where="网站副本的 git status",
                     saw="还有 Git 没跟踪过的新文件")
    else:
        ctx.ok("像密钥的文件已经清掉，也没有进过提交")

    # 2. the unrelated file: back to what it was before the AI change
    if repo.file_at("HEAD", unrelated) != original:
        ctx.fail("范围外的改动被提交了", where="最新提交里的 " + unrelated,
                 saw="和 AI 动手之前不一样")
        redo = True
    elif on_disk != original:
        if started:
            ctx.fail("有一个文件还留着范围外的改动", where="工作区里的 " + unrelated,
                     saw="和 AI 动手之前不一样")
        else:
            ctx.fail("还有范围外的改动没有退回", where="网站副本里改过的文件",
                     saw="有文件和 AI 动手之前不一样")
    else:
        ctx.ok("范围外的改动已经退回")

    # 3. the requested section: the commit that added it has the right type and the trailer
    intro = _intro_commit(repo, base, facts["title"], "index.html")
    # The section exists only as the AI's uncommitted edit: restored with the
    # out-of-scope file, it cannot be got back with what the learner knows.
    lost = intro is None and facts["title"] not in ctx.read(repo.path / "index.html")
    if commits <= facts["base_commits"] and lost:
        ctx.fail("index.html 里已经没有任务要的那一节了（可能和别的文件一起被 git restore 退回了）",
                 where="工作区里的 index.html", saw="找不到那个小标题")
    elif commits <= facts["base_commits"]:
        ctx.fail("任务要的那一节还没有提交", where="仓库的提交历史", saw="没有新的提交")
    elif intro is None or facts["title"] not in (repo.file_at("HEAD", "index.html") or ""):
        ctx.fail("任务要的那一节不在最新的提交里", where="最新提交里的 index.html",
                 saw="找不到那个小标题")
    else:
        ctx.ok("任务要的那一节已经提交")
        where = "加这一节的那次提交的第一行"
        problem = _subject_problem(intro.subject)
        kind = _commit_type(intro.subject)
        if problem:
            ctx.fail(problem[0], where=where, saw=problem[1])
            redo = True
        elif kind == facts["wrong_type"]:
            ctx.fail("提交类型还是 AI 提议的那个，和这次改动对不上", where=where, saw="类型是 " + kind)
            redo = True
        elif kind != "feat":
            ctx.fail("提交类型和这次改动对不上", where=where, saw="类型是 " + kind)
            redo = True
        else:
            ctx.ok("提交类型选对了")
        if _trailers(repo, intro.hash):
            ctx.ok("那次提交如实写明了 AI 参与")
        else:
            _trailer_fail(ctx, intro, "这一节是 AI 写的，那次提交没有写明",
                          "加这一节的那次提交的说明末尾")
            redo = True

    # 4. nothing left over (only praised once the learner has committed)
    status = repo.status()
    if not status.clean:
        ctx.fail("还有改动没有处理", where="git status",
                 saw="还有 %d 个文件没处理" % len(status.entries))
    elif commits > facts["base_commits"]:
        ctx.ok("没有落下的改动")
    if redo and station:
        ctx.note(RESET_NOTE.format(key=key))
    elif redo:
        ctx.note("已经进了提交的东西，用学过的命令改不回那次提交："
                 "运行 python3 tools/course.py review --give-up，下次会重新搭一份。")
    elif lost and station:
        ctx.note(LOST_NOTE + "重搭一份练习再做：python3 tools/course.py scenario %s --reset" % key)
    elif lost:
        ctx.note(LOST_NOTE + "运行 python3 tools/course.py review --give-up，下次会重新搭一份。")
    return facts


def check_b(ctx):
    _check_b_work(ctx, "1.15a", station=True)


def check_b_review(ctx):
    _check_b_work(ctx, "1.15-ai-change")


def _rule_lines(text):
    rules = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|\d+、\s*)(\S.*)$", line)
        if m:
            rules.append(m.group(1).strip())
    return rules


# List marks an input method types instead of the half-width "- ".
WIDE_BULLETS = "－—–•·・＊＋"


def _bullet_problem(text):
    """(missing, saw) for a line that looks like a rule but is not a list item, or None."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _rule_lines(line):
            continue
        if stripped[0] in WIDE_BULLETS:
            return ("列表开头要用半角的 - 再空一格（中文输入法打出来的符号不算）",
                    "有一行以「%s」开头：%s" % (stripped[0], _short(stripped, 20)))
        if re.match(r"^-[^\s-]", stripped):
            return ("列表开头的 - 后面要空一格", "有一行是「%s」" % _short(stripped, 20))
    return None

def _norm_rule(ctx, text):
    return ctx.normalize(text).rstrip("。.；;")


def _commits_touching(repo, path):
    """Hashes of the commits on HEAD that changed ``path``, newest first."""
    return repo.query("log", "--format=%H", "--", path).lines


def _trailers(repo, commit):
    found = []
    for key in ATTRIBUTION_KEYS:
        result = repo.query("log", "-1", "--format=%(trailers:key=" + key + ",valueonly)", commit)
        found += [line for line in result.lines if line.strip()]
    return found


def _trailer_fail(ctx, commit, missing, where):
    """Record a missing attribution trailer, naming the real cause when it is visible."""
    text = commit.message or ""
    for line in text.splitlines()[1:]:
        low = line.strip().lower()
        for key in ATTRIBUTION_KEYS:
            if not low.startswith(key.lower()):
                continue
            rest = line.strip()[len(key):]
            if rest.startswith(":") and text.splitlines()[-1].strip() != line.strip():
                ctx.fail("尾注要在说明的最后一段：用第二个 -m 单独写它", where=where,
                         saw="写了 %s，但后面还有别的内容" % key)
                return
            if not rest.startswith(":"):
                ctx.fail("尾注要写成「名字: 内容」：名字后面紧跟半角冒号 :，再空一格", where=where,
                         saw="有一行是「%s」" % _short(line.strip(), 30))
                return
    if len(text.strip().splitlines()) == 1 and any(k.lower() in text.lower() for k in ATTRIBUTION_KEYS):
        ctx.fail("尾注要和第一行分开：用第二个 -m 单独写它", where=where,
                 saw="尾注写在了第一行里")
        return
    ctx.fail(missing, where=where, saw="没有找到写明参与者的尾注")


def check_c(ctx):
    """Real ~/Developer/my-site: CLAUDE.md with three own rules, committed honestly."""
    repo = ctx.need_repo(ctx.my_site, "你的网站文件夹 my-site")
    if not ctx.expect_file(repo.path / "CLAUDE.md", "my-site 根目录里的 CLAUDE.md"):
        ctx.stop()
    committed = repo.file_at("HEAD", "CLAUDE.md")
    if committed is None:
        ctx.fail("CLAUDE.md 还没有提交", where="my-site 的最新提交", saw="里面没有 CLAUDE.md")
        ctx.stop()
    ctx.ok("CLAUDE.md 已经提交")
    code = repo.status().code("CLAUDE.md")
    if code:
        ctx.fail("CLAUDE.md 提交以后又改过，还没提交", where="git status", saw="CLAUDE.md 是 " + code.strip())

    rules = _rule_lines(committed)
    samples = set(_norm_rule(ctx, s) for s in SAMPLE_RULES)
    own = [r for r in rules if _norm_rule(ctx, r) not in samples]
    copied = len(rules) - len(own)
    if len(own) >= 3:
        ctx.ok("里面有 %d 条你自己写的规矩" % len(own))
    else:
        bullet = _bullet_problem(committed)
        if copied:
            ctx.fail("要有三条你自己写的规矩", where="已提交的 CLAUDE.md 里的列表",
                     saw="%d 条是自己写的，%d 条和课文例子一字不差" % (len(own), copied))
        elif not bullet:
            ctx.fail("要有三条规矩，每条写成列表的一行", where="已提交的 CLAUDE.md 里的列表",
                     saw="找到 %d 条" % len(rules))
        if bullet:
            ctx.fail(bullet[0], where="已提交的 CLAUDE.md", saw=bullet[1])
        ctx.note("改好以后保存，再 git add CLAUDE.md 和 git commit 一次：检查看的是提交进去的那一份。")

    # The newest commit that touched CLAUDE.md is graded, so a learner who got
    # the message wrong recovers with one more commit (no amend in stage 1).
    touching = _commits_touching(repo, "CLAUDE.md")
    if not touching:
        raise RuntimeError("CLAUDE.md is in HEAD but no commit touching it was found")
    commit = repo.commit(touching[0])
    where = "最新一次改 CLAUDE.md 的提交的第一行"
    problem = _subject_problem(commit.subject)
    kind = _commit_type(commit.subject)
    if problem:
        ctx.fail(problem[0], where=where, saw=problem[1])
    elif kind not in ("docs", "chore"):
        ctx.fail("提交 CLAUDE.md 的类型和改动对不上", where=where, saw="类型是 " + kind)
    else:
        ctx.ok("提交 CLAUDE.md 的说明格式对")
    if ctx.failed:
        if problem or kind not in ("docs", "chore"):
            ctx.note(REDO_NOTE.format(**REDO_RULES))
        ctx.stop()

    author = ctx.choose("这份 CLAUDE.md 是谁写的？",
                        [("self", "全是我自己写的"),
                         ("ai", "AI 起草过或帮我改过措辞")])
    if author == "ai":
        if any(_trailers(repo, sha) for sha in touching):
            ctx.ok("提交里如实写明了 AI 参与")
        else:
            _trailer_fail(ctx, commit, "AI 参与了，但提交里没有写明", "改 CLAUDE.md 的提交的说明末尾")
            ctx.note("在 CLAUDE.md 里再改一小处，提交时用第二个 -m 写上尾注；"
                     "检查会看所有改过 CLAUDE.md 的提交。")
    else:
        ctx.ok("自己写的，提交说明里不用写 AI")


checks = {"1.15a": check_a, "1.15b": check_b, "1.15c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.15a": [
        "检查看两件事：my-site 现在是不是干净的；你选了收下的话，那次提交在不在、写法对不对。检查结果的“还缺什么”说的是哪一件？",
        "进到 ~/Developer/my-site，先运行 git status。还有改动，就回到第 1 站的五个问题，一项一项答完再决定。",
        "相似的例子是练习场 1.15a 里的 my-site：git status、git diff --stat、git diff 一步一步看，五个问题都答完才决定；在你自己的网站上再加一步 open index.html，收下就是 git add 加 git commit -m。",
        ("答案：在 my-site 里运行 git status、git diff --stat、git diff，再 open index.html 看页面，对照五个问题。"
         "都没问题就 git add 你验收过、确认要的文件（这次通常只有 index.html），"
         "再 git commit -m \"feat: 在页脚写明网页由我和 AI 一起维护\" -m \"Co-Authored-By: Claude <noreply@anthropic.com>\""
         "（第一个引号里换成你这次改动的内容；第二个 -m 写明 AI 参与，第 2 站细讲）；"
         "有问题就 git restore <文件名> 退回；只要一部分，就只 add 要的那个文件，其余的 restore。"
         "检查问的文件数，是你那次 git commit 打印的第二行里的数字（忘了就运行 git log --stat -1 看最后一行）。"
         "解释：AI 的改动在你提交之前只是一份提案，提交这一步由你亲手做，等于在验收单上签字。"),
    ],
    "1.15b": [
        "AI 的交付说明会漏也会错，以改动本身为准。三类问题各找一个：改了不该改的、多出了不该有的、说明写错的。提交说明由你来写。",
        "进入 ~/Developer/playground/1.15a/ai-change/my-site，运行 git status：看“Changes not staged”下面有几个文件，“Untracked files”下面有没有新文件。再用 cat ../ai-report.txt 看 AI 建议的提交说明。",
        "相似的例子是“跟我做”里的 fx-tool：git diff 看出 rates.txt 被顺手改了，用 git restore 退回；ai-scratch.txt 是新文件，restore 管不了它，看清内容后用 rm 删掉；提交时第二个 -m 写上尾注。",
        ("答案：先 git restore 那个不该改的文件（style.css 或 README.md，看 git diff --stat）；"
         "再 cat 看一眼那个像密钥的新文件，确认不要了就用 rm 删掉；"
         "然后 git add index.html，git commit -m \"feat: 在首页加上我常用的工具\" -m \"Co-Authored-By: Claude <noreply@anthropic.com>\""
         "（第一个引号里的标题换成 ai-report.txt 里任务说的那一节，类型和尾注要一次写对，提交以后改不了；类型是 feat，因为加了新内容，不是修 bug 也不是文档；"
         "这一节是 AI 写的，所以加尾注）。最后 git status 应该是干净的。"
         "解释：AI 说“其他文件没有动”，git status 说动了三个。永远以 git 看到的为准。"),
    ],
    "1.15c": [
        "检查看三件事：my-site 根目录有 CLAUDE.md 且已提交；里面至少三条你自己写的规矩；提交说明的写法。如果 AI 参与了起草，提交说明里要写明。",
        "规矩写成列表，一条一行，以半角的“- ”开头（减号后面空一格）。写完保存，git add CLAUDE.md，再提交。提交前用 git status 确认只提交了这一个文件。",
        "“跟我做”里练习场那份 CLAUDE.md 是 AI 起草的：先改掉不该有的那一条，再 git add，最后用 docs 类型提交，并按第 2 站的办法加尾注。",
        ("答案：在 ~/Developer/my-site 里运行 code CLAUDE.md，写一个标题，再写三条你在前两站最在意的事，各占一行、以“- ”开头，"
         "用你自己的话写，保存；git add CLAUDE.md；自己写的就 git commit -m \"docs: 添加给 AI 的项目说明\"；"
         "如果请 AI 起草或改过措辞，再加 -m \"Co-Authored-By: Claude <noreply@anthropic.com>\"，检查时选“AI 起草过或帮我改过措辞”。"
         "解释：CLAUDE.md 是在这个项目里开工时 AI 先读的规矩；写成具体、能核对的话，AI 才容易照做。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.15-r1", "type": "recall", "tier": "fluent", "station": "1.15a", "rule": "AI-01",
     "q": "AI 说“改好了”。在你提交之前，按顺序要看哪几样？",
     "a": "git status（动了哪些文件，有没有新文件）→ git diff --stat（改了多少）→ git diff（逐行读）→ 亲眼看效果（打开网页或运行程序）。都没问题才自己提交。",
     "explain": "这是 AI-01：AI 的改动先看 diff 再接受。"},
    {"id": "1.15-p1", "type": "predict", "tier": "fluent", "station": "1.15b",
     "q": "AI 新建了一个文件 notes.txt，它从来没有被提交过。你运行 git restore notes.txt，会怎样？",
     "options": ["notes.txt 被删掉", "报错：pathspec 'notes.txt' did not match any file(s) known to git",
                 "notes.txt 的内容被清空"],
     "answer": "B",
     "explain": "git restore 只能把文件恢复成 Git 记录过的样子；Git 从没记录过的新文件，它不认识。新文件要先看清内容，再决定用 rm 删掉。"},
    {"id": "1.15-f1", "type": "fault", "tier": "lookup", "station": "1.15b", "rule": "AI-01",
     "q": "AI 在网页上加了一节新内容，交来这条提交说明。哪里不对？\n\n    fix: 在首页加上我常用的工具",
     "options": ["类型不对：加了新内容是 feat", "冒号后面不该有空格", "说明不能用中文"],
     "answer": "A",
     "explain": "fix 是修好一个错误。这次是加了新东西，用 feat。冒号后面正好一个空格，说明可以用中文。"},
    {"id": "1.15-w1", "type": "which", "tier": "fluent", "station": "1.15c",
     "q": "想让 Claude Code 在某个项目里每次开工都先读到你定的几条规矩，规矩写在哪里最合适？",
     "options": ["项目根目录的 CLAUDE.md，并提交进仓库", "每次开新对话时在聊天里说一遍",
                 "~/.gitignore_global"],
     "answer": "A", "shuffle": True,
     "explain": "聊天里说的话会话一结束就没了；CLAUDE.md 在仓库里，在这个项目里开工时会读（项目文件夹要选这个项目）。Claude 把它当背景信息，不保证百分之百照做，所以 diff 还是要看。"},
    {"id": "1.15-t1", "type": "recall", "tier": "lookup", "station": "1.15b", "rule": "AI-02",
     "q": "一次提交有 AI 参与。提交说明里怎么写明？写在哪里？",
     "a": "在说明的最后一段写一行尾注，比如 Co-Authored-By: Claude <noreply@anthropic.com>。用 git commit -m \"标题\" -m \"Co-Authored-By: …\"，第二个 -m 会自动空一行。",
     "explain": "这是 AI-02。不同项目可能要求 Assisted-by: 或 Generated-by:，以项目自己的规定为准。"},
    {"id": "1.15-d1", "type": "do", "tier": "fluent", "station": "1.15b", "rule": "AI-01",
     "q": "练习场里有一次 AI 做的、还没提交的改动和它的交付说明。只把任务要的部分按正确的类型提交，并用尾注写明 AI 参与；其余的退回或清掉，做完以后 git status 是干净的。",
     "scenario": "1.15-ai-change", "check": check_b_review},
]


# ---------------------------------------------------------------------------
# EXAM (gate-1)
# ---------------------------------------------------------------------------
NOTES_BASE = {
    "todo.md": "# 本周待办\n\n- 复习 Git 的四个区域\n- 给网页换一个标题颜色\n",
    "README.md": "# study-notes\n\n我的学习笔记。每周更新一次。\n",
}
NOTES_TASKS = ["- 读完 Pro Git 第 2 章", "- 写一页本周复盘", "- 练习三次 git diff"]
NOTES_SECRETS = ["token.txt", "access-key.txt"]


def build_x1(sc):
    """Form A: a web page repo; form B: a notes repo.  Same skill: accept only the asked part."""
    prefix = ["page", "site", "home"] if sc.form == "A" else ["notes", "study", "log"]
    repo = sc.pick(prefix) + "-" + sc.word()
    key = "%08x%08x" % (sc.randint(0, 0xFFFFFFFF), sc.randint(0, 0xFFFFFFFF))
    sc.git_init(repo)
    if sc.form == "A":
        sc.copy_in("starter/my-site", repo + "/web")
        for name in ("index.html", "style.css"):
            sc.move(repo + "/web/" + name, repo + "/" + name)
        sc.remove(repo + "/web")
        sc.write(repo + "/README.md", "# %s\n\n一页的个人网页。\n\n## 现在做到哪了\n\n还在学习中，会一点一点改。\n" % repo)
        sc.git_commit(repo, "feat: 第一版网页", date=sc.ago(days=3))
        base = sc.git(repo, "rev-parse", "HEAD").strip()
        title = sc.pick(sorted(TOOLS_SECTIONS))
        unrelated = sc.pick(["style.css", "README.md"])
        secret = sc.pick(sorted(SECRET_FILES))
        _plant_problems(sc, repo, title, TOOLS_SECTIONS[title], unrelated, secret, key)
        sc.fact("request", "在首页的列表下面加一节「%s」" % title)
        sc.fact("marker", title)
        sc.fact("target", "index.html")
    else:
        for name, text in NOTES_BASE.items():
            sc.write(repo + "/" + name, text, exact=True)
        sc.git_commit(repo, "docs: 第一版笔记", date=sc.ago(days=3))
        base = sc.git(repo, "rev-parse", "HEAD").strip()
        task = sc.pick(NOTES_TASKS)
        unrelated = "README.md"
        secret = sc.pick(NOTES_SECRETS)
        sc.append(repo + "/todo.md", task + "\n")
        sc.write(repo + "/README.md", "# study-notes\n\n我的学习笔记。不再更新。\n", exact=True)
        sc.write(repo + "/" + secret, "TOKEN=tk-live-%s\n" % key, exact=True)
        sc.fact("request", "在 todo.md 的待办列表末尾加一条「%s」" % task[2:])
        sc.fact("marker", task)
        sc.fact("target", "todo.md")
    sc.fact("repo", repo)
    sc.fact("base", base)
    sc.fact("unrelated", unrelated)
    sc.fact("secret", secret)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库")
    secret = facts["secret"]
    original = repo.file_at(facts["base"], facts["unrelated"])
    if original is None:
        raise RuntimeError("exam base lacks the unrelated file")
    on_disk = ctx.read(repo.path / facts["unrelated"], default=None)
    # Before any attempt, do not name what the candidate is meant to find.
    started = (repo.ref("HEAD") != facts["base"] or not ctx.exists(repo.path / secret)
               or on_disk == original)
    if repo.query("log", "--all", "--format=%h", "--", secret).lines:
        ctx.fail("不该有的新文件进了提交历史", where="仓库的提交历史", saw="有提交带着 " + secret)
    elif ctx.exists(repo.path / secret):
        if started:
            ctx.fail("不该有的新文件还在文件夹里", where=ctx.show(repo.path), saw="还有 " + secret)
        else:
            ctx.fail("多出来的新文件还没处理", where="仓库的 git status", saw="还有 Git 没跟踪过的新文件")
    else:
        ctx.ok("不该有的新文件已经清掉")
    if repo.file_at("HEAD", facts["unrelated"]) != original or on_disk != original:
        ctx.fail("任务以外的改动还在", where=facts["unrelated"] if started else "仓库里改过的文件",
                 saw="和改动之前不一样")
    else:
        ctx.ok("任务以外的改动已经退回")
    committed = repo.file_at("HEAD", facts["target"]) or ""
    intro = _intro_commit(repo, facts["base"], facts["marker"], facts["target"])
    if repo.ref("HEAD") == facts["base"]:
        ctx.fail("任务要的改动还没有提交", where="仓库的提交历史", saw="没有新的提交")
    elif intro is None or facts["marker"] not in committed:
        ctx.fail("任务要的改动不在最新的提交里", where="最新提交里的 " + facts["target"],
                 saw="找不到任务要加的内容")
    else:
        ctx.ok("任务要的改动已经提交")
        # Form A adds a page section (feat, as station b teaches).  Form B adds a
        # line to a notes file: feat (new content), docs or chore are all defensible.
        allowed = ("feat",) if info.form == "A" else ("feat", "docs", "chore")
        problem = _subject_problem(intro.subject)
        kind = _commit_type(intro.subject)
        if problem:
            ctx.fail(problem[0], where="加这处改动的那次提交的第一行", saw=problem[1])
        elif kind not in allowed:
            ctx.fail("提交类型和这次改动对不上", where="加这处改动的那次提交的第一行", saw="类型是 " + kind)
        else:
            ctx.ok("提交说明的类型对")
    ctx.expect(repo.is_clean(), "git status 是干净的", "还有改动没有处理",
               where="git status", saw="不是干净的")


EXAM = [
    {
        "id": "1.15-x1",
        "gate": "gate-1",
        "title": "验收一次 AI 改动，只收下任务要的部分",
        "minutes": 10,
        "build": build_x1,
        "task": {
            "A": ("仓库 {dir}/{repo} 里有一次 AI 做的、还没提交的改动。交给 AI 的任务是：{request}。"
                  "验收它：只把任务要的部分提交（提交说明用约定式提交），其余的改动退回、多出来的文件清掉。"
                  "做完以后 git status 要是干净的。"),
            "B": ("进入 {dir}/{repo}。AI 刚按这个要求改完，还没提交：{request}。"
                  "AI 还动了别的东西。把不属于任务的都处理掉，只提交任务本身，提交说明写成约定式提交；"
                  "最后 git status 是干净的。"),
        },
        "grade": grade_x1,
    },
]
