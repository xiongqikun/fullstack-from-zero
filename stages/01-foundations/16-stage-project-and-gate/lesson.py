"""Lesson 1.16: 阶段作品与验收 (plan section 4, task T2).

Three stations:

- 1.16a 整理作品: an artifact check on the learner's *real* folders
  (``~/Developer/my-site`` and the workspace itself, both repositories with a
  remote since lessons 1.12-1.13) plus one ask about the site's history.
- 1.16b 阶段验收: the debugging task of gate-1 in the station scenario
  ``1.16b`` (an ignored file that was committed earlier) with one ask, the two
  written explain-back answers in ``notes/gate-1-explain.md``, and gate-1
  itself, read with ``ctx.gate_result`` / ``ctx.gate_done`` (every lesson
  1.11-1.16 has a passed task and the explain-back is recorded as pass).
- 1.16c 复盘和下一段: the retrospective file ``notes/stage-1-retro.md``
  (made from ``templates/retro.md``) and one ask whose answer is the study
  time ``status`` prints.

Standard library only; importable on Python 3.9.  Reference:
docs/authoring/tool-api.md.
"""

import posixpath
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.16",
    "slug": "16-stage-project-and-gate",
    "title": "阶段作品与验收",
    "stage": 1,
    "prerequisites": ["1.15"],
    "stations": [
        {"id": "1.16a", "title": "整理作品", "minutes": 40,
         "new_concept": "阶段的完成标准：作品别人看得到、看得懂、拿得回来",
         "new_commands": []},
        {"id": "1.16b", "title": "阶段验收", "minutes": 40,
         "new_concept": "冷考：不看提示、换个情境、讲得出为什么"
                        "（阶段验收 gate-1 的实操题和讲解题是单独的一段时间，不算在这一站里）",
         "new_commands": []},
        {"id": "1.16c", "title": "复盘和下一段", "minutes": 40,
         "new_concept": "阶段复盘：用证据回看整整一个阶段，定下一步要改的一件事",
         "new_commands": []},
    ],
    "rules": ["PM-03"],
    "verified": {"date": "2026-11-20",
                 "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9",
                           "python3": "3.14.9"}},
    "unverified_steps": [
        "1.16a：用 VS Code 打开并编辑 README.md（code README.md）〔对照文档，界面可能不同〕",
        "1.16a：git push 推送到 GitHub 时屏幕上的远程地址和进度行〔建课时无法验证〕"
        "（模拟里推送到本地的替身仓库）",
        "1.16b：用 VS Code 新建 notes/gate-1-explain.md 并粘贴骨架〔对照文档，界面可能不同〕",
        "1.16b：讲解题：对导师说“请问我 gate-1 的讲解题”，或者在不以 fullstack-from-zero 为项目文件夹的新对话里"
        "用 gates/gate-1/examiner-prompt.md 请考官评〔建课时无法验证〕",
        "1.16c：用 VS Code 打开 ROADMAP.md 和 notes/stage-1-retro.md〔对照文档，界面可能不同〕",
    ],
}

TERMS = [
    {"term": "作品集", "en": "portfolio",
     "plain": "能拿给别人看、证明你做得出来的一组作品", "first": "1.16a"},
    {"term": "冷考", "en": "cold test",
     "plain": "过了几天、不看提示、换一个没见过的情境再做一次，看你是不是真的会了", "first": "1.16b"},
    {"term": "考官", "en": "examiner",
     "plain": "只按评分标准和你的证据判过没过、不教你的那一方（这里是导师，或者一个新开的 Claude 对话）",
     "first": "1.16b"},
    {"term": "补考", "en": "retest",
     "plain": "只重考还没通过的那几课，并且换另一套题面", "first": "1.16b"},
    {"term": "回顾会", "en": "Sprint Retrospective",
     "plain": "Scrum 里每个冲刺结束时，团队一起复盘、定改进的固定会议", "first": "1.16c"},
]

# ---------------------------------------------------------------------------
# Shared data and small helpers
# ---------------------------------------------------------------------------
# Every rule id of stages 0 and 1 except PM-03, which this lesson teaches
# (plan section 4; tools/courselib/syllabus.py has the same list).
STAGE_RULES = [
    "META-01", "WS-01", "WS-02", "META-02", "PM-01", "PM-02",
    "TERM-01", "TERM-02", "ED-01", "ED-02", "DOC-01", "DOC-02",
    "GIT-01", "GIT-02", "GIT-03", "GIT-04", "REPO-01", "REPO-02",
    "COMMIT-01", "COMMIT-02", "ACC-01", "ACC-02", "REMOTE-01", "REMOTE-02",
    "PUB-01", "HELP-01", "FRESH-01", "AI-01", "AI-02",
]
PREFIXES = "meta|ws|pm|term|ed|doc|git|repo|commit|acc|remote|pub|help|fresh|ai"
RULE_ID = re.compile(r"(?<![a-z])(" + PREFIXES + r")[-_‐-―－]?(\d{2})(?!\d)")
LIST_MARK = re.compile(r"^(?:[-*+>]\s*|\d+[.)、．]\s*)+")
# Conventional Commits 1.0.0: type, optional (scope), optional !, colon, ONE space.
# Item 15 of the spec: implementors MUST NOT treat the units as case-sensitive,
# so "Fix:" is accepted (with a note that the spec's examples are lower case).
# A full-width colon is not the spec's colon and is not accepted.
CONVENTIONAL = re.compile(r"^[A-Za-z]+(\([^()\s]+\))?!?: \S")
FIX_TYPE = re.compile(r"^fix(\([^()\s]+\))?!?: \S", re.IGNORECASE)
LOWER_TYPE = re.compile(r"^[a-z]+[(!:]")


def _case_note(ctx, subjects):
    if any(CONVENTIONAL.match(s) and not LOWER_TYPE.match(s) for s in subjects):
        ctx.note("约定式提交规范不分大小写，所以大写的类型也算对；不过规范里的例子都写小写（feat、fix、docs），照着写小写最稳妥。")


# Files that the tool and the tutor rewrite all the time (plan G11): they may
# be modified when a check runs, so they never count as "not committed".
TOOL_OWNED = ("learner/", "PROGRESS.md")
NOTES_RULES = "notes/my-rules.md"
EXPLAIN = "notes/gate-1-explain.md"
RETRO = "notes/stage-1-retro.md"
JOURNAL_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
URL = re.compile(r"https?://[^\s<>()\[\]「」]+")
DIGIT = re.compile(r"\d")
# Hours written in Chinese numerals: 「二十五个小时」「两小时」, or an answer that
# is only a number (「八」「约三十」「二十五到三十」).  A numeral inside other
# words (「一周看情况」「周二」) is not a number of hours.
CN_NUM = "零〇一二两三四五六七八九十百千"
CN_HOURS = re.compile(r"[" + CN_NUM + r"]+\s*个?\s*半?\s*(?:小时|钟头)")
CN_ONLY = re.compile(r"^[约大概差不多左右至到～~\-、，,\s个小时钟头。.（）()" + CN_NUM + r"]+$")
LICENCE_FILES = ("LICENSE", "LICENSE.md", "LICENSE.txt")
NOT_A_NAME = ("the", "copyright", "license", "licence", "version")


def _meaningful(text):
    """Count letters, digits and CJK characters (no spaces, no punctuation)."""
    return sum(1 for ch in str(text) if ch.isalnum())


def _squash(text):
    """Text reduced to its letters and digits, lower case: for copy detection."""
    return "".join(ch for ch in str(text).lower() if ch.isalnum())


def _id_of(match):
    return match.group(1).upper() + "-" + match.group(2)


def _has_number(text):
    """A number of hours written with digits or Chinese numerals (三十、八)."""
    text = text.strip()
    if DIGIT.search(text) or CN_HOURS.search(text):
        return True
    return bool(CN_ONLY.match(text)) and any(ch in CN_NUM for ch in text)


def _ask_hash(ctx, prompt, full):
    """Ask for the first 7 characters of the commit ``full``.  A wrong answer
    shorter than 7 characters also gets a note that 7 are needed (true for
    every short answer, and it does not tell whether the start was right)."""
    if ctx.ask(prompt, expected=lambda typed: len(typed) >= 7 and full.startswith(typed)):
        return True
    typed = "".join(str(ctx.last_answer or "").split())
    if len(typed) < 7:
        ctx.note("编号要输入前 7 位，你输入的只有 {} 位。".format(len(typed)))
    return False


def _rule_texts(ctx, lines):
    """{rule id: the learner's words for it} from the lines of my-rules.md.

    The file has one heading per rule (「### GIT-03 提交前先看改了什么」,
    COMMON.md section 4).  The learner's words are the non-empty lines below
    a rule's heading up to the next heading; the heading's own title never
    counts.  A heading may carry a number or marks in front.  A line written
    anywhere else that starts with a rule id (after a list mark) counts for
    that rule too.
    """
    found = {}
    current = None
    for raw in lines:
        line = ctx.normalize(raw)
        if not line:
            continue
        if line.startswith("#"):
            match = RULE_ID.search(line)
            current = _id_of(match) if match else None
            continue
        body = LIST_MARK.sub("", line)
        match = RULE_ID.match(body)
        if match:
            rule, words = _id_of(match), body[match.end():]
        elif current:
            rule, words = current, line
        else:
            continue
        found[rule] = (found.get(rule, "") + " " + words).strip()
    return found


def _card_texts(ctx):
    """{rule id: [squashed title, squashed rule sentence]} from the course's cards."""
    cards = {}
    current = None
    for rel in ctx.walk("stages"):
        if not rel.endswith("rules.md"):
            continue
        for line in ctx.lines("stages/" + rel):
            head = re.match(r"^###\s+([A-Z]+-\d{2})\s+(.*)$", line.strip())
            if head:
                current = head.group(1)
                cards.setdefault(current, []).append(_squash(head.group(2)))
                continue
            body = re.match(r"^-\s*\*\*规则\*\*[：:](.*)$", line.strip())
            if body and current:
                cards[current].append(_squash(body.group(1)))
    return cards


def _not_committed(status):
    """Entries of a status that are the learner's to commit."""
    return [entry.path for entry in status.entries
            if not any(entry.path == owned or entry.path.startswith(owned)
                       for owned in TOOL_OWNED)]


def _check_pushed(ctx, repo, label):
    """Fails unless every commit of the current branch is on the remote."""
    own = label + (" 的" if label[-1:].isascii() else "的")
    branch = repo.branch or "main"
    upstream = repo.upstream()
    if upstream is not None:
        counts = repo.ahead_behind() or (0, 0)
        if counts[0]:
            ctx.fail("有提交还没有推送", where=own + " git status",
                     saw="比 {} 多 {} 个提交".format(upstream, counts[0]))
            return False
        ctx.ok(own + "提交都已经推送")
        if counts[1]:
            ctx.note("{} 上有 {} 个提交你本地还没有，以后的课会讲怎么拉下来。".format(
                upstream, counts[1]))
        return True
    if not repo.remotes():
        ctx.fail("还没有远程仓库", where=own + "远程设置", saw="git remote -v 是空的")
        return False
    remote_head = repo.ref("origin/" + branch)
    if remote_head is None:
        ctx.fail("这个分支还没有推送过", where=own + "远程分支",
                 saw="找不到 origin/" + branch)
        return False
    if remote_head != repo.head:
        ctx.fail("最新的提交还没有推送", where=own + " origin/" + branch,
                 saw="远程的最新提交和本地的不一样")
        return False
    ctx.ok(own + "提交都已经推送")
    return True


# ---------------------------------------------------------------------------
# Station a: the stage's work is in a deliverable state
# ---------------------------------------------------------------------------
def _licence_name(text):
    """The first word of a licence file's first line ("MIT" for "MIT License")."""
    first = next((line for line in text.splitlines() if line.strip()), "")
    words = re.findall(r"[A-Za-z][A-Za-z0-9.\-]*", first)
    if words and words[0].lower() not in NOT_A_NAME:
        return words[0]
    return None


def _check_site(ctx):
    site = ctx.need_dir("~/Developer/my-site", "你的网站文件夹 my-site")
    repo = ctx.need_repo(site, "my-site")
    readme = site / "README.md"
    if not ctx.expect_file(readme, "my-site 里的 README.md"):
        return repo
    text = ctx.read(readme)
    lower = text.lower()
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    ctx.expect(first.startswith("# ") and len(first) > 2, "README 第一行是一级标题",
               "README 的第一行要是一级标题", where="README.md 的第一行",
               saw="现在是「{}」".format(ctx.visible(first[:20])))
    if "____" in text:
        ctx.fail("README 里还有没填的空", where="README.md", saw="里面有 ____")
    urls = [url for url in URL.findall(text) if "github.io" in url]
    if not urls:
        ctx.fail("README 里还没有网页的网址", where="README.md",
                 saw="没找到 github.io 的网址")
    elif all("你的用户名" in url for url in urls):
        ctx.fail("网址还是占位的写法", where="README.md 里的网址", saw="里面写着“你的用户名”")
    else:
        ctx.ok("README 写了网页的网址")
    tracked = repo.tracked()
    licence = [name for name in LICENCE_FILES if name in tracked]
    ctx.expect(bool(licence), "LICENSE 文件已经在仓库里", "仓库里还没有 LICENSE 文件",
               where="my-site 里被 Git 管着的文件（git ls-files）", saw="没有 LICENSE")
    name = _licence_name(ctx.read(site / licence[0])) if licence else None
    if name:
        named = name.lower() in lower
        saw = "没有出现 LICENSE 第一行写的那个许可证名字"
    else:
        named = "LICENSE" in text
        saw = "没有提到 LICENSE 这个文件"
    if named:
        ctx.ok("README 写明了用的是什么许可证")
    else:
        ctx.fail("README 还没写明用的是什么许可证", where="README.md", saw=saw)
    top = [path for path in tracked if "/" not in path and path != "README.md"]
    unnamed = [path for path in top
               if path.lower() not in lower and path.lower().lstrip(".") not in lower]
    if unnamed:
        ctx.fail("README 还没提到仓库里的这些文件", where="README.md，对照 git ls-files 列出的最上层文件",
                 saw="没提到：" + "、".join(unnamed))
    elif top:
        ctx.ok("仓库最上层的每个文件，README 里都提到了")
    page = ctx.read(site / "index.html")
    if "____" in page:
        ctx.fail("网页大标题里的空还没填", where="my-site/index.html", saw="还有 ____")
    left = _not_committed(repo.status())
    if left:
        ctx.fail("还有改动没有提交", where="my-site 的 git status",
                 saw="、".join(left[:3]) + (" 等" if len(left) > 3 else ""))
    else:
        ctx.ok("my-site 没有落下没提交的改动")
        _check_pushed(ctx, repo, "my-site")
    bad = [c.subject for c in repo.commits(limit=5) if not CONVENTIONAL.match(c.subject)]
    if bad:
        ctx.note("最近 5 个提交里有 {} 个不是约定式提交的写法。旧提交不用改，以后的提交照 1.10 课写。".format(len(bad)))
    return repo


def _check_notes(ctx):
    if not ctx.expect_file(NOTES_RULES, "notes/my-rules.md"):
        return
    words = _rule_texts(ctx, ctx.lines(NOTES_RULES))
    missing = [rule for rule in STAGE_RULES if _meaningful(words.get(rule, "")) < 5]
    if missing:
        ctx.fail("还没找到你为这些行规写的话，或者写得太短（不到 5 个字）",
                 where="notes/my-rules.md 里每条行规小标题下面的几行",
                 saw="还缺 {} 条：{}".format(len(missing), "、".join(missing)))
    else:
        ctx.ok("阶段 0 和阶段 1 的 {} 条行规都写了自己的话".format(len(STAGE_RULES)))
    cards = _card_texts(ctx)
    copied = [rule for rule in STAGE_RULES
              if rule in words and _squash(words[rule]) in cards.get(rule, [])]
    if copied:
        ctx.fail("这几条和规则卡上的字一模一样，要换成你自己的话",
                 where="notes/my-rules.md", saw="、".join(copied))


def _check_workspace(ctx):
    repo = ctx.need_repo(ctx.workspace, "学习工作区 fullstack-from-zero")
    _check_notes(ctx)
    entries = [name for name in ctx.listdir("journal") if JOURNAL_NAME.match(name)]
    tracked = [name for name in entries if repo.is_tracked("journal/" + name)]
    if not entries:
        ctx.fail("还没有学习日志", where="journal 文件夹", saw="没有 年-月-日.md 这样的文件")
    elif not tracked:
        ctx.fail("学习日志还没有提交", where="journal 文件夹", saw="日志文件不在仓库里")
    else:
        ctx.ok("学习日志已经在仓库里（{} 天）".format(len(tracked)))
    left = _not_committed(repo.status())
    if left:
        ctx.fail("学习工作区还有改动没有提交", where="fullstack-from-zero 的 git status",
                 saw="、".join(left[:3]) + (" 等" if len(left) > 3 else ""))
    else:
        ctx.ok("学习工作区没有落下没提交的改动")
        _check_pushed(ctx, repo, "学习工作区")
    return repo


def check_a(ctx):
    site_repo = _check_site(ctx)
    _check_workspace(ctx)
    if ctx.failed:
        ctx.stop()
    head = site_repo.head or ""
    _ask_hash(ctx, "my-site 最新一个提交的编号是什么？（提交时 [main 后面那 7 位；"
                   "或者在 my-site 里运行 git log --oneline，看第一行开头）输入前 7 位。",
              head)
    ctx.note("learner/ 下的文件和 PROGRESS.md 由工具随时更新，这一站不看它们。")


# ---------------------------------------------------------------------------
# Station b: the gate (debugging task, explain-back answers, gate-1)
# ---------------------------------------------------------------------------
TMP_NAMES = ["draft.tmp", "scratch.tmp", "todo.tmp", "ideas.tmp"]
SNEAKY = ["docs: 补充怎么查看网页", "docs: 更新 README 里的说明", "docs: 改一下 README 的措辞"]
LINK_COLOURS = ["#1d4ed8", "#0f766e", "#7c3aed"]


def build_1_16b(sc):
    """S7 copy, then: a commit that force-added a .tmp file, a later commit,
    and an uncommitted change to the .tmp file.  ``*.tmp`` is in .gitignore."""
    sc.site_before()
    site = sc.facts["site"]
    tmp = sc.pick(TMP_NAMES)
    sc.write(site + "/" + tmp, "临时记一下：\n- 下周把列表再改改\n")
    sc.append(site + "/README.md", "\n打开以后，可以把浏览器窗口拉窄，看看手机上的样子。\n")
    culprit = sc.git_commit(site, sc.pick(SNEAKY), add=["README.md", tmp], force=True)
    sc.append(site + "/style.css", "\na {\n  color: %s;\n}\n" % sc.pick(LINK_COLOURS))
    sc.git_commit(site, "feat: 给链接换一个颜色")
    sc.append(site + "/" + tmp, "- 又想到一件事\n")
    sc.fact("tmp", tmp)
    sc.fact("culprit", culprit)
    sc.fact("commits", sc.facts["site_commits"] + 2)
    sc.todo("网站副本在这里：" + sc.show(site))
    sc.todo("现象：git status 总说 " + tmp + " 被修改了，可 .gitignore 里明明写着 *.tmp。")


def _tracked_tmp_fixed(ctx, station=False):
    """Shared by the station check (``station=True``) and the do review item."""
    info = ctx.scenario("1.16b")
    repo = ctx.need_repo(info.path / info.facts["site"], "网站副本 my-site")
    tmp = info.facts["tmp"]
    if repo.is_tracked(tmp):
        ctx.fail(tmp + " 还被 Git 管着", where="副本里被 Git 管着的文件", saw=tmp + " 在里面")
    else:
        ctx.ok(tmp + " 已经不归 Git 管了")
        # Only worth saying once the learner has acted: untouched, it is there too.
        ctx.expect(ctx.is_file(repo.path / tmp), tmp + " 还留在电脑上",
                   "这个文件要留在电脑上，只是不再交给 Git", where=ctx.show(repo.path / tmp),
                   saw="文件不见了")
    ctx.expect(repo.file_at("HEAD", tmp) is None, "最新的提交里已经没有它",
               "最新的提交里还有这个文件", where="副本的最新提交", saw="里面还有 " + tmp)
    before = info.facts["commits"]
    if repo.commit_count() > before:
        last = repo.commit()
        if CONVENTIONAL.match(last.subject):
            ctx.ok("新提交的说明符合约定式提交")
            _case_note(ctx, [last.subject])
        else:
            ctx.fail("新提交的说明不符合约定式提交", where="最新提交的第一行",
                     saw="「{}」".format(ctx.visible(last.subject[:30])))
            if "：" in last.subject:
                ctx.note("类型后面的冒号要用英文的半角冒号 :，中文输入法打出来的全角冒号 ： 不算。")
            if station:
                ctx.note("已经提交了的说明，现在还改不了（阶段 2 会教）。重搭一份副本再做一次："
                         "python3 tools/course.py scenario 1.16b --reset（文件名和要找的提交都会换）。")
    else:
        ctx.fail("还没有新的提交来记下这次修复", where="副本的提交历史",
                 saw="还是 {} 个提交".format(before))
    status = repo.status()
    ctx.expect(status.clean, "git status 是干净的", "还有改动没处理",
               where="副本的 git status", saw="有 {} 处改动".format(len(status.entries)))
    return info


# The two explain-back questions, as printed in the skeleton of lesson.md and
# in gates/gate-1/rubric.md and examiner-prompt.md (问法 A).
EXPLAIN_QUESTIONS = [
    "为什么密码、令牌这类文件要在提交之前就用 .gitignore 挡住，而不是提交以后再删掉？",
    "为什么学习仓库要推送到 GitHub、并且试着克隆回来，而不是只靠 iCloud 同步来备份？",
]
EXPLAIN_HEAD = re.compile(r"^#{2,}\s*(?:\S+\s+)?问题\s*([12一二])")


def _explain_answers(ctx):
    # No label: the learner sees the full path (~/Developer/fullstack-from-zero/notes/...),
    # so a file written in the wrong folder is easy to spot.
    if not ctx.expect_file(EXPLAIN):
        return
    sections, current = {}, None
    for line in ctx.lines(EXPLAIN):
        head = EXPLAIN_HEAD.match(ctx.normalize(line))
        if head:
            current = {"一": "1", "二": "2"}.get(head.group(1), head.group(1))
            sections[current] = ""
        elif line.startswith("#"):
            current = None
        elif current and not any(_squash(q) in _squash(line) for q in EXPLAIN_QUESTIONS):
            sections[current] += line.replace("（你的回答）", "")
    short = [n for n in ("1", "2") if _meaningful(sections.get(n, "")) < 30]
    if short:
        ctx.fail("讲解题的回答还太短，或者还没写", where=EXPLAIN,
                 saw="「## 问题 " + "」「## 问题 ".join(short) + "」下面不到 30 个字")
    else:
        ctx.ok("每一道讲解题下面都写了自己的回答")
    repo = ctx.git(ctx.workspace)
    if repo.is_repo:
        if not repo.is_tracked(EXPLAIN) or repo.status().code(EXPLAIN):
            ctx.fail("讲解题的回答还没有提交", where="fullstack-from-zero 的 git status",
                     saw=EXPLAIN + " 还有没提交的改动")
        else:
            ctx.ok("讲解题的回答已经提交")


def _gate_1(ctx):
    """gate-1 as the tool counts it (tool-api.md section 6.7)."""
    gate = ctx.gate_result("gate-1")
    extra = "gate-1 还有一场加练没批改：python3 tools/course.py exam gate-1 --grade。它不会让通过的课退回去。"
    if ctx.gate_done("gate-1"):
        ctx.ok("阶段验收 gate-1 通过了（讲解题 {}）".format(gate.explain_date or "已记下"))
        if gate.in_progress:
            ctx.note(extra)
    elif gate.attempts == 0:
        ctx.fail("还没有考 gate-1 的实操题", where="学习记录里的关卡成绩",
                 saw="没有 gate-1 的记录：python3 tools/course.py exam gate-1")
    elif not gate.practical_done:
        if gate.in_progress:
            ctx.fail("gate-1 这一场考试还没有批改完", where="gate-1 最近一场",
                     saw="还有题没批改：python3 tools/course.py exam gate-1 --grade")
        else:
            ctx.fail("还有课的实操题没通过，练好以后补考", where="gate-1 的成绩",
                     saw="还没有一题通过的课：" + "、".join("第 " + lesson + " 课" for lesson in gate.open_lessons))
    else:
        if gate.explain == "again":
            ctx.fail("讲解题还要再讲一次：准备好了再对导师说“请问我 gate-1 的讲解题”", where="gate-1 的讲解题",
                     saw="讲解题上次记的是“再来一次”")
        else:
            ctx.fail("讲解题还没记为通过", where="gate-1 的讲解题",
                     saw="还没有记录：讲完以后用 python3 tools/course.py exam gate-1 --explain pass 记下")
        if gate.in_progress:
            ctx.note(extra)


def check_b(ctx):
    info = _tracked_tmp_fixed(ctx, station=True)
    if not ctx.failed:
        culprit = info.facts["culprit"]
        _ask_hash(ctx, "排错题：看副本的提交历史，是哪一个提交把那个 .tmp 文件带进仓库的？输入编号的前 7 位。",
                  culprit)
    _explain_answers(ctx)
    _gate_1(ctx)


# ---------------------------------------------------------------------------
# Station c: the retrospective
# ---------------------------------------------------------------------------
# Keywords of the six headings of templates/retro.md (COMMON.md section 4).
RETRO_SECTIONS = [
    ("做得好", "「做得好的」"),
    ("要改", "「要改的」"),
    ("下一步", "「下一步」"),
    ("用时", "「用时」"),
    ("每周", "「下一阶段的每周计划」"),
    ("反馈", "「给课程的反馈」"),
]
# The template's own words: they are not the learner's content.
TEMPLATE_WORDS = [
    "计划：", "实际：", "每周学习几小时：", "固定在哪几天、几点：",
    "这个阶段哪一处最难懂？", "哪一处最慢、最想改？", "（写一句）",
]
USAGE_NOTE = "写完把这一段删掉"
DECIMAL = re.compile(r"\d+(?:\.\d+)?")


def _retro_lines(ctx):
    """[(section key or None, stripped line)] of the retrospective, without the
    template's usage note."""
    rows, current = [], None
    for line in ctx.lines(RETRO):
        stripped = line.strip()
        if USAGE_NOTE in stripped:
            continue
        if stripped.startswith("#"):
            current = None
            if stripped.startswith("##"):
                current = next((key for key, _label in RETRO_SECTIONS if key in stripped), None)
                rows.append((current, None))
            continue
        rows.append((current, stripped))
    return rows


def _retro_sections(rows):
    sections = {}
    for key, line in rows:
        if key is None:
            continue
        sections.setdefault(key, "")
        if line:
            for word in TEMPLATE_WORDS:
                line = line.replace(word, " ")
            sections[key] += " " + line
    return sections


def _hours_problem(rows):
    """None when the 用时 section names the planned and the actual hours, else
    the text for saw=."""
    lines = [LIST_MARK.sub("", line) for key, line in rows if key == "用时" and line]
    planned = _after_word(lines, "计划", "实际")
    actual = _after_word(lines, "实际", "计划")
    figures = _figures(" ".join(lines))
    if planned or actual:
        if not actual:
            # 「计划 25～30，用了 24 小时」: no 实际, but two figures are there.
            if figures >= 2:
                return None
            return "写了计划，没有找到写着「实际」的小时数（写成「- 实际：24 小时」这样最清楚）"
        if not any(_has_number(text) for text in actual):
            return "「实际」后面没有找到数字（写 30 或 三十 都行）"
        if planned and not any(_has_number(text) for text in planned):
            return "「计划」后面没有找到数字"
        if not planned and figures < 2:
            # 「- 实际：21 小时」 alone: the planned figure is missing.
            return "写了实际，没有找到写着「计划」的小时数（照「- 实际：…小时」的样子，再写一行「- 计划：…小时」）"
        return None
    if figures < 2:
        return "这一节里找不到两个数字（计划一个，实际一个）"
    return None


NOT_HOURS = re.compile(r"(?:阶段|第)\s*\d+(?:\.\d+)?[a-z]?")
SESSIONS = re.compile(r"\d+\s*次")
RANGE = re.compile(r"\d+(?:\.\d+)?\s*[～~\-–—到至]\s*\d+(?:\.\d+)?"
                   r"|[" + CN_NUM + r"]+\s*[～~\-–—到至]\s*[" + CN_NUM + r"]+")


def _figures(text):
    """How many hour figures a text gives: a range (25～30) is one figure, and
    the number of a stage or a lesson (阶段 1、第 1.16 课) or of sessions
    (status's 「（20 次）」) is none."""
    text = RANGE.sub(" 0 ", NOT_HOURS.sub(" ", SESSIONS.sub(" ", text)))
    return len(DECIMAL.findall(text)) + len(CN_HOURS.findall(text))


def _after_word(lines, word, other):
    """The text after ``word`` on every line that has it, up to ``other``
    when ``other`` comes later on the same line (「计划 25～30 小时，实际 24 小时」)."""
    found = []
    for line in lines:
        start = line.find(word)
        if start < 0:
            continue
        text = line[start + len(word):]
        stop = text.find(other)
        if stop >= 0:
            text = text[:stop]
        found.append(text.lstrip("：: "))
    return found


def _weekly_hours(rows):
    """Some line of the weekly plan names a number (of hours)."""
    for key, line in rows:
        if key != "每周" or not line:
            continue
        for word in TEMPLATE_WORDS:
            line = line.replace(word, " ")
        if _has_number(LIST_MARK.sub("", line.strip())):
            return True
    return False


BRACKETED = re.compile(r"[（(][^（）()]*[）)]")
BEFORE_HOURS = re.compile(r"(\d+(?:\.\d+)?)\s*个?\s*小时")


def _hours_match(ctx, total_hours):
    def match(typed):
        # 「约 21.1 小时（19 次）」 pasted from status: a remark in brackets is
        # left aside, and with two numbers the one before 小时 is the answer.
        typed = BRACKETED.sub(" ", typed)
        numbers = DECIMAL.findall(typed)
        if len(numbers) > 1:
            numbers = BEFORE_HOURS.findall(typed)
        if len(numbers) == 1:
            value = float(numbers[0])
        elif not numbers:
            value = ctx.parse_int(typed)
            if value is None:
                return False
        else:
            return False
        # status may have counted a few more minutes since the learner looked.
        return abs(value - total_hours) <= 1.0
    return match


def check_c(ctx):
    if not ctx.expect_file(RETRO):
        ctx.stop()
    rows = _retro_lines(ctx)
    sections = _retro_sections(rows)
    for key, label in RETRO_SECTIONS:
        content = sections.get(key)
        if content is None:
            ctx.fail("复盘里还缺一节" + label, where=RETRO, saw="找不到这个小标题")
        elif _meaningful(content) < 4:
            ctx.fail(label + "下面还没写内容", where=RETRO, saw="这一节是空的，或者只有骨架里原来的字")
    if "用时" in sections:
        problem = _hours_problem(rows)
        if problem:
            ctx.fail("「用时」要写出计划和实际的小时数", where=RETRO + " 的「用时」", saw=problem)
    if "每周" in sections and not _weekly_hours(rows):
        ctx.fail("每周计划要写出每周几小时", where=RETRO + " 的每周计划",
                 saw="这一节里没有找到数字（写 8 或 八 都行）")
    if not ctx.failed:
        ctx.ok("复盘的六节都写了内容")
    repo = ctx.git(ctx.workspace)
    if repo.is_repo:
        if not repo.is_tracked(RETRO) or repo.status().code(RETRO):
            ctx.fail("复盘文件还没有提交", where="fullstack-from-zero 的 git status",
                     saw=RETRO + " 还有没提交的改动")
        else:
            ctx.ok("复盘文件已经提交")
    if ctx.failed:
        ctx.stop()
    minutes = 0
    for session in ctx.state.get("sessions") or []:
        if isinstance(session, dict) and isinstance(session.get("minutes"), int):
            minutes += max(0, session["minutes"])
    ctx.ask("运行 python3 tools/course.py status，看「累计学习」那一行：一共约多少小时？（填数字）",
            expected=_hours_match(ctx, minutes / 60.0))
    words = _rule_texts(ctx, ctx.lines(NOTES_RULES))
    if _meaningful(words.get("PM-03", "")) < 5:
        ctx.note("收尾时别忘了在 notes/my-rules.md 的小标题「PM-03 每个阶段结束做一次复盘」下面写你自己的话。")


checks = {"1.16a": check_a, "1.16b": check_b, "1.16c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "1.16a": [
        "这一站只看两个真文件夹：my-site 和学习工作区。检查结果的“还缺什么”说的是哪一个？先只管那一个。",
        "说 README 的，打开 ~/Developer/my-site/README.md，对照第 1 站「概念」里的交付清单，"
        "再用 git ls-files 看仓库里有哪些文件；说行规的，看 notes/my-rules.md 里检查列出的那几个小标题下面；"
        "说“没提交”“没推送”的，在那个文件夹里运行 git status。",
        "相似的例子：一个菜谱仓库里有 recipes.md、photos.md 和 LICENSE，README 的「里面有什么」只写了 recipes.md。"
        "看得懂的 README 要把另外两个也列上，一个文件一行，写它是干什么的；"
        "然后照 1.7、1.6、1.12 课的老步骤：看改动、提交、推送，最后 git status 要说 up to date。",
        "答案：在 my-site 的 README.md 里，「里面有什么」那一节补上缺的文件（例如「- .gitignore：告诉 Git 哪些文件不收进仓库」"
        "「- LICENSE：许可证全文」），README 里有真实的 github.io 网址和写明 MIT、指向 LICENSE 的许可证一节；"
        "保存后 git diff、git add README.md、git commit -m \"docs: README 里列全仓库里的文件\"、git push、git status。"
        "notes/my-rules.md 里，检查列出的每个编号，在它的小标题下面写一两句自己的话；"
        "然后在学习工作区按第 1.12 课收尾的那一组命令提交并推送。"
        "最后的问答：抄提交时 [main 后面那 7 位，或者在 my-site 里运行 git log --oneline，抄第一行开头的 7 位。"
        "解释：阶段完成的标准是作品别人看得到（已推送）、看得懂（README 和仓库对得上）、拿得回来（远程有一份）。",
    ],
    "1.16b": [
        "这一站的检查看三样：排错题的副本、notes/gate-1-explain.md、gate-1 的成绩。先看“还缺什么”说的是哪一样。",
        "排错题：在副本里运行 git status 和 git log --stat，看那个 .tmp 文件是从哪个提交开始出现的。"
        "想一想 1.9 课：“不拍名单”对已经拍进去的东西有没有用？",
        "相似的例子：.env 已经被提交过，后来才写进 .gitignore。这时要让 Git 不再管它、但文件留在电脑上，"
        "用的是 1.9 课第 2 站的那条命令，再提交一次。",
        "答案：在副本里运行 git rm --cached，后面接 git status 里列出的那个文件名，例如 git rm --cached todo.tmp；"
        "再 git commit -m \"chore: 不再跟踪临时文件\"，git status 就干净了；"
        "git log --stat 里最早（最下面）那个列出这个文件、把它加进来的提交，就是问答题要的编号（前 7 位）；"
        "你自己刚做的那个修复提交也会列出它，在最上面，不是它。"
        "解释：.gitignore 只挡还没被 Git 管的文件，已经提交过的要先用 --cached 从仓库里拿掉，文件本身留着。"
        "讲解题写进 notes/gate-1-explain.md，每题一两句、至少 30 个字，写完提交；gate-1 按课文的考试时段做：开考、批改、讲解题，"
        "讲解题的结果用 python3 tools/course.py exam gate-1 --explain pass 记下。",
    ],
    "1.16c": [
        "复盘看的是证据，不是感觉。检查结果说缺哪一节，就先补那一节。",
        "六个小标题照 templates/retro.md 的骨架写；“用时”的计划数字来自 ROADMAP.md，"
        "实际数字来自 python3 tools/course.py status 的「累计学习」一行。",
        "相似的例子：“要改的：每次都在 1.9 课卡住 → 下一步：每周一先做 5 分钟复习题。” 一个问题配一个能做的动作。",
        "答案：notes/stage-1-retro.md 里六节各写至少一句："
        "做得好的、要改的、下一步、用时（计划：ROADMAP.md 里阶段 1 学完时的累计小时；实际：status 显示的小时数）、"
        "下一阶段的每周计划（每周几小时、哪几天）、给课程的两条反馈；保存后在学习工作区里 "
        "git add notes/stage-1-retro.md、git commit -m \"docs: 阶段 1 复盘\"。"
        "问答题填 status 显示的小时数。解释：复盘的产出是下一段的一个具体改动，所以“下一步”必须写成能做的事。",
    ],
}


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
def build_start(sc):
    """The state just before this lesson: the site in state S7."""
    sc.site_before()
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))
    sc.todo("它的“GitHub”是同一个文件夹里的替身仓库：" + sc.show(sc.facts["site_remote"]))


SCENARIOS = {"start": build_start, "1.16b": build_1_16b}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.16-ahead", "type": "predict", "tier": "fluent", "station": "1.16a",
     "q": "在仓库里运行 git status，第二行是：\n\n    Your branch is ahead of 'origin/main' by 1 commit.\n\n这说明什么？",
     "options": ["本地有 1 个提交还没推送到远程", "远程有 1 个新提交，你本地还没有",
                 "有 1 个文件改了还没提交"],
     "answer": "A", "shuffle": True,
     "explain": "ahead 是“领先”：本地比远程多一个提交，推送以后才会变成 up to date。改了没提交的文件列在下面的 Changes 里。"},
    {"id": "1.16-ignored-tracked", "type": "fault", "tier": "fluent", "station": "1.16b",
     "q": ".gitignore 里写着 *.tmp，可是 git status 还是说：\n\n    modified:   todo.tmp\n\n最可能是哪里出了问题？",
     "options": ["todo.tmp 以前已经被提交过，忽略规则管不到它", ".gitignore 里的 *.tmp 写法不对",
                 "todo.tmp 太大了，Git 不肯忽略"],
     "answer": "A", "shuffle": True,
     "explain": "忽略规则只挡还没被 Git 管的文件；已经提交过的，要先 git rm --cached 从仓库里拿掉。*.tmp 的写法本身没问题。"},
    {"id": "1.16-retro", "type": "recall", "tier": "fluent", "station": "1.16c", "rule": "PM-03",
     "q": "一个阶段结束时的复盘回答哪三个问题？为什么“下一步”一定要写成具体能做的事？",
     "a": "做得好的、要改的、下一步。复盘是为了让下一段做得更好；只写感想不会改变做法，下一步写成一件能做、能检查的事才会真的发生。"},
    {"id": "1.16-gate-fail", "type": "recall", "tier": "lookup", "station": "1.16b",
     "q": "关卡的实操题没通过，接下来会怎样？",
     "a": "工具列出练习清单（哪一课、哪道题）。练好以后再运行 exam，只补考还没通过的课，没通过的题换另一套题面。"},
    {"id": "1.16-untrack", "type": "do", "tier": "lookup", "station": "1.16b",
     "q": "网站副本里有一个 .tmp 文件，虽然 .gitignore 里写了 *.tmp，它还是被 Git 管着。让 Git 不再管它（文件留在电脑上），用一个符合约定式提交的提交记下来，最后 git status 要是干净的。",
     "scenario": "1.16b", "check": _tracked_tmp_fixed},
]


# ---------------------------------------------------------------------------
# EXAM (gate-1): whole-stage tasks
# ---------------------------------------------------------------------------
X1_SETUP = {
    "A": {"prefix": "shop-", "keep": ["index.html", "style.css"],
          "secret": [".env", "secrets.env"], "junk": ["drafts", "cache"]},
    "B": {"prefix": "notes-", "keep": ["README.md", "week-1.md"],
          "secret": ["token.txt", "api-key.txt"], "junk": ["backup", "scratch"]},
}
X1_CONTENT = {
    "index.html": "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head><meta charset=\"utf-8\"><title>小店</title>"
                  "<link rel=\"stylesheet\" href=\"style.css\"></head>\n<body><h1>小店开张了</h1></body>\n</html>\n",
    "style.css": "h1 {\n  color: #b45309;\n}\n",
    "README.md": "# 学习笔记\n\n每周一个文件，记下学了什么。\n",
    "week-1.md": "# 第 1 周\n\n- 学会了 git status\n",
}


def build_x1(sc):
    """A folder that is not a repository yet, with a secret and a junk folder."""
    setup = X1_SETUP[sc.form]
    folder = setup["prefix"] + sc.word()
    secret = sc.pick(setup["secret"])
    junk = sc.pick(setup["junk"])
    for name in setup["keep"]:
        sc.write(folder + "/" + name, X1_CONTENT[name], exact=True)
    sc.write(folder + "/" + secret, "KEY=%d\n" % sc.randint(100000, 999999), exact=True)
    sc.write(folder + "/" + junk + "/old-" + sc.word() + ".md", "旧的草稿，不要了\n", exact=True)
    sc.fact("folder", folder)
    sc.fact("secret", secret)
    sc.fact("junk", junk)
    sc.fact("keep", setup["keep"])


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["folder"], "考试文件夹 " + facts["folder"], praise=True)
    count = repo.commit_count()
    ctx.expect(count >= 2, "有至少两个提交", "提交不到两个", where="仓库的提交历史",
               saw="现在有 {} 个提交".format(count))
    bad = [c.subject for c in repo.commits() if not CONVENTIONAL.match(c.subject)]
    if count and bad:
        ctx.fail("有提交说明不符合约定式提交", where="git log --oneline",
                 saw="例如「{}」".format(ctx.visible(bad[0][:30])))
        if any("：" in subject for subject in bad):
            ctx.note("类型后面的冒号要用英文的半角冒号 :，中文输入法打出来的全角冒号 ： 不算。")
    elif count:
        ctx.ok("每条提交说明都符合约定式提交")
        _case_note(ctx, [c.subject for c in repo.commits()])
    for name in facts["keep"]:
        ctx.expect(repo.is_tracked(name), name + " 已经提交", "该提交的文件还没进仓库",
                   where="仓库里的文件", saw="没有 " + name)
    ctx.expect(repo.is_tracked(".gitignore"), ".gitignore 已经提交", ".gitignore 还没有进入提交",
               where="仓库里的文件", saw="没有 .gitignore")
    secret, junk = facts["secret"], facts["junk"]
    ever = repo.query("log", "--format=%H", "--", secret).lines
    if ever:
        ctx.fail("这个文件曾经被提交过，历史里还留着它", where="git log -- " + secret,
                 saw="有 {} 个提交动过它".format(len(ever)))
    else:
        ctx.expect(repo.is_ignored(secret), secret + " 被忽略规则挡住了",
                   secret + " 还没被任何忽略规则挡住", where="git status --ignored", saw=secret)
    junk_tracked = [path for path in repo.tracked() if path.startswith(junk + "/")]
    junk_ever = repo.query("log", "--format=%H", "--", junk).lines
    if junk_tracked or junk_ever:
        ctx.fail(junk + "/ 里的东西进过仓库", where="仓库的历史", saw=junk + "/ 出现在提交里")
    else:
        names = [p for p in ctx.walk(info.path / facts["folder"] / junk)]
        sample = junk + "/" + (names[0] if names else "x.md")
        ctx.expect(repo.is_ignored(sample), junk + "/ 被忽略规则挡住了",
                   junk + "/ 还没被忽略规则挡住", where="git status --ignored", saw=junk + "/")
    ctx.expect(repo.is_clean(), "git status 是干净的", "还有改动没处理",
               where="git status", saw="不是干净的")


# Exam task 1.16-x2: find the commit that broke the page, fix it, commit the fix.
#
# Form A: a small site whose stylesheet link breaks.  Form B: a reading-notes
# site with another layout (css/ and posts/ folders) whose "about" link breaks.
# In both forms the breaking commit sits at a seeded place (1-3 commits before
# the newest one), and at least one harmless commit also touches index.html,
# so "the commit that changed index.html" or "the second-newest commit" is
# never the answer by itself.  The grader looks at the outcome: every local
# link of index.html in the newest commit must lead to a file of that commit.
# Subjects follow lesson 1.10: a change to what a page shows (text, colours,
# a new page) is feat; only README changes are docs.  The culprit's subject is
# misleading only in that it never mentions the link it breaks.
X2_FORMS = {
    "A": {"prefix": "site-", "titles": ["小站", "我的小站"],
          "css": "style.css", "break": "css",
          "bad": ["styles.css", "css/style.css", "style.ccs"],
          "intros": ["欢迎来我的小站。", "这里记着我学做网页的过程。", "每周更新一点。"],
          "culprits": ["feat: 调整首页的排版", "refactor: 整理首页的代码", "feat: 首页标题改几个字"]},
    "B": {"prefix": "notes-", "titles": ["我的读书笔记", "读书笔记"],
          "css": "css/main.css", "break": "about",
          "bad": ["abuot.html", "about.htm", "pages/about.html"],
          "intros": ["每读完一本书，记几句。", "这里放我的读书笔记。", "慢慢读，慢慢记。"],
          "culprits": ["feat: 首页加一个导航", "refactor: 整理首页的链接", "feat: 首页改几个字"]},
}
X2_COLOURS = ["#0b5cad", "#b45309", "#0f766e", "#7c3aed"]


def _x2_page(page):
    extra = "".join("  <p>%s</p>\n" % text for text in page["extra"])
    links = "".join("  <p><a href=\"%s\">%s</a></p>\n" % (href, text) for href, text in page["links"])
    return ("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <title>%s</title>\n  <link rel=\"stylesheet\" href=\"%s\">\n</head>\n<body>\n"
            "  <h1>%s</h1>\n  <p>%s</p>\n%s%s</body>\n</html>\n"
            % (page["title"], page["css"], page["title"], page["intro"], extra, links))


def _x2_simple(title, body):
    return ("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head><meta charset=\"utf-8\"><title>%s</title></head>\n"
            "<body><h1>%s</h1><p>%s</p></body>\n</html>\n" % (title, title, body))


def _x2_fillers(sc, cfg, page, repo, post):
    """Harmless commits as (subject, change, touches index.html)."""
    css = cfg["css"]

    def colour():
        sc.write(repo + "/" + css, "body {\n  max-width: 40rem;\n  margin: 2rem auto;\n}\n\nh1 {\n  color: %s;\n}\n"
                 % sc.pick(X2_COLOURS[1:]), exact=True)

    def readme():
        sc.write(repo + "/README.md", "# %s\n\n用浏览器打开 index.html 就能看。\n" % page["title"], exact=True)

    def intro():
        page["intro"] = [t for t in cfg["intros"] if t != page["intro"]][0]

    def extra(text):
        def change():
            page["extra"].append(text)
        return change

    if sc.form == "A":
        def about():
            sc.write(repo + "/about.html", _x2_simple("关于我", "我在学做网页，也喜欢爬山。"), exact=True)
        items = [("docs: 添加 README", readme, False),
                 ("feat: 标题换个颜色", colour, False),
                 ("feat: 补充“关于我”", about, False),
                 ("feat: 改一下首页的介绍", intro, True),
                 ("feat: 首页加一句联系方式", extra("有问题可以给我留言。"), True)]
    else:
        def more():
            sc.append(repo + "/" + post, "<p>第二遍读的时候，又看懂了一点。</p>\n")
        items = [("docs: 添加 README", readme, False),
                 ("feat: 标题换一种颜色", colour, False),
                 ("feat: 笔记里补一段", more, False),
                 ("feat: 首页换一句介绍", intro, True),
                 ("feat: 首页加上更新日期", extra("最近更新：每周日。"), True)]
    return items


def build_x2(sc):
    cfg = X2_FORMS[sc.form]
    repo = cfg["prefix"] + sc.word()
    post = "posts/" + sc.word() + ".html"
    page = {"title": cfg["titles"][0], "intro": sc.pick(cfg["intros"]), "extra": [],
            "css": cfg["css"], "links": [("about.html", "关于我")]}
    sc.git_init(repo)
    sc.write(repo + "/about.html", _x2_simple("关于我", "我在学做网页。"), exact=True)
    sc.write(repo + "/" + cfg["css"], "body {\n  max-width: 40rem;\n  margin: 2rem auto;\n}\n\nh1 {\n  color: %s;\n}\n"
             % X2_COLOURS[0], exact=True)
    if sc.form == "B":
        sc.write(repo + "/" + post, _x2_simple("第一篇笔记", "这本书讲的是怎么慢慢读书。"), exact=True)
        page["links"].append((post, "第一篇笔记"))
    before = sc.randint(0, 2)
    after = sc.randint(1, 3)
    fillers = sc.sample(_x2_fillers(sc, cfg, page, repo, post), before + after)
    if not any(touches for _s, _c, touches in fillers):
        decoys = [item for item in _x2_fillers(sc, cfg, page, repo, post) if item[2]]
        fillers[sc.randint(0, len(fillers) - 1)] = sc.pick(decoys)
    total = 1 + before + 1 + after
    day = total + 1

    def commit(subject):
        nonlocal day
        day -= 1
        return sc.git_commit(repo, subject, date=sc.ago(days=day))

    sc.write(repo + "/index.html", _x2_page(page), exact=True)
    commit("feat: 首页、样式和“关于我”" if sc.form == "A" else "feat: 首页、样式和第一篇笔记")
    for subject, change, _touches in fillers[:before]:
        change()
        sc.write(repo + "/index.html", _x2_page(page), exact=True)
        commit(subject)
    bad = sc.pick(cfg["bad"])
    page["title"] = cfg["titles"][1]
    if cfg["break"] == "css":
        page["css"] = bad
    else:
        page["links"][0] = (bad, "关于我")
    sc.write(repo + "/index.html", _x2_page(page), exact=True)
    culprit = commit(sc.pick(cfg["culprits"]))
    for subject, change, _touches in fillers[before:]:
        change()
        sc.write(repo + "/index.html", _x2_page(page), exact=True)
        commit(subject)
    sc.fact("repo", repo)
    sc.fact("culprit", culprit)
    sc.fact("commits", total)
    sc.fact("bad", bad)
    sc.fact("sheets", 1)
    sc.fact("anchors", len(page["links"]))


class _Links(HTMLParser):
    """The hrefs of stylesheet <link> tags and of <a> tags in one page."""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.sheets, self.anchors = [], []

    def handle_starttag(self, tag, attrs):
        values = {name.lower(): (value or "") for name, value in attrs}
        if "href" not in values:
            return
        if tag == "link" and "stylesheet" in values.get("rel", "").lower().split():
            self.sheets.append(values["href"])
        elif tag == "a":
            self.anchors.append(values["href"])


def _local_path(href):
    """The repository path a relative link points to; None for other links
    (another site, mailto:, #top); "" for a local link that leaves the site."""
    href = href.strip()
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    path = posixpath.normpath(unquote(parts.path))
    if path.startswith("/") or path == ".." or path.startswith("../"):
        return ""
    return path


def _page_links(repo, ref="HEAD"):
    """(local stylesheet paths, local anchor paths, broken count) of index.html."""
    parser = _Links()
    parser.feed(repo.file_at(ref, "index.html") or "")
    parser.close()
    sheets = [p for p in (_local_path(h) for h in parser.sheets) if p is not None]
    anchors = [p for p in (_local_path(h) for h in parser.anchors) if p is not None]
    broken = sum(1 for p in sheets + anchors if not p or repo.file_at(ref, p) is None)
    return sheets, anchors, broken


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库 " + facts["repo"])
    sheets, anchors, broken = _page_links(repo)
    if broken:
        ctx.fail("最新提交里的网页还是坏的", where="最新提交里的 index.html",
                 saw="有 {} 个链接指向的文件在这个提交里找不到".format(broken))
    elif len(sheets) < facts["sheets"] or len(anchors) < facts["anchors"]:
        ctx.fail("最新提交里的网页少了链接", where="最新提交里的 index.html",
                 saw="原来的链接有的不见了，要修好它，而不是删掉它")
    else:
        ctx.ok("最新提交里的网页已经修好")
    if repo.commit_count() > facts["commits"]:
        last = repo.commit()
        ctx.expect(bool(FIX_TYPE.match(last.subject)), "修复用了表示修复问题的提交类型",
                   "记下修复的提交说明，类型不对或格式不对", where="最新提交的第一行",
                   saw="「{}」".format(last.subject[:30]))
        _case_note(ctx, [last.subject])
        ctx.expect(repo.is_clean(), "git status 是干净的", "还有改动没处理",
                   where="git status", saw="不是干净的")
    else:
        ctx.fail("还没有新的提交记下这次修复", where="仓库的提交历史",
                 saw="还是 {} 个提交".format(facts["commits"]))
        if not repo.is_clean():
            ctx.fail("还有改动没处理", where="git status", saw="不是干净的")
    if ctx.failed:
        ctx.stop()
    culprit = facts["culprit"]
    _ask_hash(ctx, "是哪一个提交弄出了这个问题？输入编号的前 7 位。", culprit)


EXAM = [
    {
        "id": "1.16-x1",
        "gate": "gate-1",
        "title": "按说明把一个文件夹建成规范的仓库（复习 1.6、1.9、1.10 课）",
        "minutes": 15,
        "build": build_x1,
        "task": {
            "A": ("文件夹 {dir}/{folder} 是一个还没有版本管理的小网页。把它变成 Git 仓库并提交，要求："
                  "{secret} 和 {junk}/ 文件夹永远不能进仓库；至少两个提交，每个提交只做一件事；"
                  "每条提交说明都符合约定式提交；做完以后 git status 是干净的。"),
            "B": ("{dir}/{folder} 是一份学习笔记，还没有版本管理。要求：在这个文件夹里建仓库；"
                  "{secret} 里是令牌，{junk}/ 是不要的旧东西，它们都不能被 Git 收进去；"
                  "其余文件分成至少两个提交，提交说明都符合约定式提交；最后 git status 是干净的。"),
        },
        "grade": grade_x1,
    },
    {
        "id": "1.16-x2",
        "gate": "gate-1",
        "title": "从历史里找出弄坏网页的提交并修好（复习 1.7、1.10 课）",
        "minutes": 12,
        "build": build_x2,
        "task": {
            "A": ("仓库 {dir}/{repo} 里的网页本来有样式（有颜色、有边距），现在打开只剩白底黑字。"
                  "查出是哪一个提交把它弄坏的，把网页修好（文件和链接怎么改都行，网页能正常显示就算修好），再用一个提交记下这次修复："
                  "说明符合约定式提交，类型用表示“修复问题”的那一种。做完以后 git status 是干净的。"
                  "批改时会问你：弄坏网页的是哪一个提交（编号的前 7 位）。"),
            "B": ("{dir}/{repo} 是一个读书笔记网站。首页上“关于我”那个链接以前点得开，现在点了说找不到文件。"
                  "查出是哪一个提交改坏的，修好它（改链接或改文件名都行，点得开就算修好），再提交一次：说明符合约定式提交，"
                  "类型用表示“修复问题”的那一种；最后 git status 是干净的。"
                  "批改时会问你：改坏链接的是哪一个提交（编号的前 7 位）。"),
        },
        "grade": grade_x2,
    },
]
