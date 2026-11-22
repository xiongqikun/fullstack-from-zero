"""Lesson 1.8 Git：后悔药 (undo changes that are not committed yet).

Station a: ``git restore <file>`` throws away working-tree changes; Git keeps
no copy of them, so this cannot be undone.  Station b: ``git restore
--staged <file>`` takes a change back off the staging area without touching
the file, and a three-row table of which command fits which situation.

Amending commits and recovering lost work are deferred to stage 2.
Standard library only; importable on Python 3.9.  API: docs/authoring/tool-api.md.
"""

META = {
    "id": "1.8",
    "slug": "08-undo-uncommitted",
    "title": "Git：后悔药",
    "stage": 1,
    "prerequisites": ["1.7"],
    "stations": [
        {
            "id": "1.8a",
            "title": "丢掉工作区里的修改",
            "minutes": 40,
            "new_concept": "git restore 用暂存区里的版本盖掉工作区的文件（没 git add 过，就是上次提交的版本），没存过的改动就此消失",
            "new_commands": ["git restore"],
        },
        {
            "id": "1.8b",
            "title": "从暂存区拿下来，以及哪种情况用哪个",
            "minutes": 40,
            "new_concept": "取消暂存只把改动从打包台拿下来，文件本身不动",
            "new_commands": ["git restore --staged"],
        },
    ],
    "rules": ["GIT-04"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9"},
    },
    "unverified_steps": [],
}

TERMS = [
    {"term": "丢弃修改", "en": "discard changes",
     "plain": "让文件回到存档里的样子，中间改的内容不要了", "first": "1.8a"},
    {"term": "会丢数据的命令", "en": "destructive command",
     "plain": "执行以后，有些内容就再也找不回来的命令", "first": "1.8a"},
    {"term": "跟踪", "en": "track",
     "plain": "Git 管着这个文件：你 git add 过它，暂存区或存档里有它的版本", "first": "1.8a"},
    {"term": "取消暂存", "en": "unstage",
     "plain": "把改动从暂存区拿下来，文件本身的内容不变", "first": "1.8b"},
]


# ---------------------------------------------------------------------------
# Shared helpers for the checks
# ---------------------------------------------------------------------------
def _same(a, b):
    """Compare two texts, ignoring only trailing line breaks."""
    if a is None or b is None:
        return a is None and b is None
    return a.rstrip("\n") == b.rstrip("\n")


def _index_text(repo, name):
    """The content of ``name`` in the staging area, or None."""
    result = repo.query("show", ":" + name)
    if not result.ok:
        return None
    return result.out


def _look(ctx, repo, name):
    """Everything a check needs to know about one file."""
    path = repo.path / name
    exists = ctx.is_file(path)
    return {
        "name": name,
        "exists": exists,
        "work": ctx.read(path) if exists else None,
        "head": repo.file_at("HEAD", name),
        "index": _index_text(repo, name),
        "code": repo.status().code(name),
    }


GONE_NOTE = "{name} 在上次提交里有版本：git status 括号里写着怎么把它找回来。"


def _want_committed(ctx, f, junk=None, staged_note=None, gone_note=None):
    """The file must be exactly as in the last commit, nothing staged.
    ``staged_note`` is added when the change sits in the staging area (station
    1.8a, before the learner has been taught how to take it back);
    ``gone_note`` when the file was deleted (stations and review only: the
    exam graders give no such pointer)."""
    name = f["name"]
    if not f["exists"]:
        ctx.fail(name + " 这个文件不见了", where="练习仓库的工作区", saw="找不到 " + name)
        if gone_note:
            ctx.note(gone_note.format(name=name))
        return False
    if f["code"][:1] not in ("", " "):
        ctx.fail(name + " 的改动还在暂存区里", where="git status",
                 saw=name + " 列在 Changes to be committed 下面")
        if staged_note:
            ctx.note(staged_note)
        return False
    if not _same(f["work"], f["head"]):
        saw = "里面还有那行手滑打的字" if junk and junk in (f["work"] or "") else "内容和上次提交时不同"
        return ctx.fail(name + " 还没回到上次提交时的样子", where=name + " 的内容", saw=saw)
    if f["work"] != f["head"]:
        # Lenient: only the line breaks at the very end differ (a hand fix);
        # git status still lists the file, so the message says so.
        ctx.ok(name + " 的内容和上次提交时一样")
        ctx.note(name + " 只是文件末尾的换行和上次提交时不同，git status 还会把它列成 modified；"
                 "用 git restore " + name + " 会连这一点也还原。")
        return True
    return ctx.ok(name + " 回到了上次提交时的样子")


def _lost_note(key):
    """The way to start over in a station: the exact rebuild command."""
    return "这些内容已经找不回来了。重搭一份练习再做：python3 tools/course.py scenario " + key + " --reset"


LOST_NOTE = _lost_note("1.8b")
EXAM_LOST_NOTE = "没提交过的内容丢了就找不回来。"
# In a review the tool itself prints how to give up and get a fresh copy.
REVIEW_LOST_NOTE = "这些内容已经找不回来了。"
COMMIT_NOTE = "提交以后再撤销是阶段 2 的内容。"


def _note_once(ctx, noted, text):
    """Add a note only once per check run (``noted`` is a set owned by the caller)."""
    if noted is None or text not in noted:
        ctx.note(text)
        if noted is not None:
            noted.add(text)


def _want_unstaged_kept(ctx, f, new_text, noted=None, lost=LOST_NOTE):
    """The change is still in the file, but no longer staged."""
    name = f["name"]
    if not f["exists"]:
        return ctx.fail(name + " 这个文件不见了", where="练习仓库的工作区", saw="找不到 " + name)
    if _same(f["work"], f["head"]):
        ctx.fail(name + " 里写的内容不见了，这些内容本来要留着", where=name + " 的内容",
                 saw="文件回到了上次提交时的样子")
        _note_once(ctx, noted, lost)
        return False
    if f["code"][:1] not in ("", " "):
        return ctx.fail(name + " 在暂存区里还有改动，下次提交会把它带上", where="git status",
                        saw=name + " 列在 Changes to be committed 下面")
    if not _same(f["work"], new_text):
        return ctx.fail(name + " 的内容和开始时不一样了", where=name + " 的内容",
                        saw="写的那几行被改动过")
    return ctx.ok(name + " 不在暂存区了，写的内容还在文件里")


def _want_staged_kept(ctx, f, new_text, praise=True, noted=None, lost=LOST_NOTE):
    """The change stays exactly where it was: in the file and staged."""
    name = f["name"]
    if not f["exists"]:
        return ctx.fail(name + " 这个文件不见了", where="练习仓库的工作区", saw="找不到 " + name)
    if _same(f["work"], f["head"]):
        ctx.fail(name + " 的改动不见了，它本来要原样留着", where=name + " 的内容",
                 saw="文件回到了上次提交时的样子")
        _note_once(ctx, noted, lost)
        return False
    if not _same(f["index"], new_text):
        return ctx.fail(name + " 的改动不在暂存区了，下次提交带不上它", where="git status",
                        saw=name + " 列在 Changes not staged for commit 下面")
    if not _same(f["work"], new_text):
        return ctx.fail(name + " 的内容和开始时不一样了", where=name + " 的内容",
                        saw="文件被改动过")
    if praise:
        ctx.ok(name + " 的改动原样留在暂存区里")
    return True


def _no_new_commit(ctx, repo, before, again=None):
    """No commit may be added.  ``again`` says how to start over (stations and
    review); exam graders pass None, because exam prints what comes next."""
    now = repo.commit_count()
    if now > before:
        ctx.fail("这次练习不需要提交，仓库里多了提交", where="git log --oneline",
                 saw="现在有 %d 个提交，开始时是 %d 个" % (now, before))
        ctx.note(COMMIT_NOTE + (again or ""))
        return False
    return True


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
JUNK = [
    "jjjjjjjjjjjjjjjj（手滑多打的）",
    "asdfasdfasdf 这一行是不小心按出来的",
    "；；；；；；；；；；；",
    "kkkkkkkk 测试测试测试",
]

CAFE = {
    "menu.txt": {"base": "美式咖啡 15 元\n拿铁 18 元\n",
                 "good": "桂花拿铁 20 元（新品）"},
    "hours.txt": {"base": "周一到周五 8:00-20:00\n周末 9:00-18:00\n",
                  "good": "节假日照常营业"},
}

TRIP = {
    "plan.txt": {"base": "第一天：到达，住下\n第二天：爬山\n",
                 "good": "第三天：去湖边走走", "draft": "第四天：（还没想好）"},
    "budget.txt": {"base": "住宿：600 元\n交通：300 元\n",
                   "good": "门票：120 元", "draft": "吃饭：（待定，还要再算）"},
    "packing.txt": {"base": "雨伞\n充电器\n",
                    "good": "身份证", "draft": "（还没列完）"},
}


GARDEN = {
    "seeds.txt": {"base": "番茄\n黄瓜\n", "good": "辣椒",
                  "draft": "（还想种点什么，没想好）"},
    "water.txt": {"base": "早上浇一次\n", "good": "夏天傍晚再浇一次",
                  "draft": "下雨天：（待定）"},
    "tools.txt": {"base": "小铲子\n手套\n", "good": "喷壶",
                  "draft": "（还没数完）"},
}


def build_start(sc):
    """The state just before 1.8: a copy of the learner's site in S4."""
    sc.site_before()
    sc.todo("进入网站副本：cd " + sc.show(sc.facts["site"]))
    sc.todo("这是练习用的副本，你真正的 my-site 不受影响。")


def build_a(sc):
    """Two tracked files, both changed, nothing staged: one change is wanted,
    the other is junk.  The learner must look before throwing one away."""
    repo = "cafe-" + sc.word()
    sc.git_init(repo)
    for name, parts in CAFE.items():
        sc.write(repo + "/" + name, parts["base"], exact=True)
    sc.git_commit(repo, "菜单和营业时间", date=sc.ago(days=1))
    junk_file, keep_file = sc.sample(sorted(CAFE), 2)
    junk = sc.pick(JUNK)
    # The junk file loses its first line and gets a line of garbage.
    rest = CAFE[junk_file]["base"].split("\n", 1)[1]
    sc.write(repo + "/" + junk_file, junk + "\n" + rest, exact=True)
    keep_text = CAFE[keep_file]["base"] + CAFE[keep_file]["good"] + "\n"
    sc.write(repo + "/" + keep_file, keep_text, exact=True)
    sc.fact("repo", repo)
    sc.fact("junk_file", junk_file)
    sc.fact("keep_file", keep_file)
    sc.fact("junk", junk)
    sc.fact("keep_text", keep_text)
    sc.fact("commits", 1)
    sc.todo("进入练习仓库：cd " + sc.show(repo))
    sc.todo("里面两个文件都改过，都还没 git add。一个改动是你想要的，另一个是手滑弄乱的。")
    sc.todo("目标：先看清楚两处改动，只丢掉弄乱的那一个；想要的那个原样留着。不要提交。")


def _build_three(sc, repo, files, message):
    """Three tracked files: one with an unwanted, unstaged change (discard),
    one staged but not ready (unstage, keep the text), one staged and ready
    (leave as it is)."""
    sc.git_init(repo)
    for name, parts in files.items():
        sc.write(repo + "/" + name, parts["base"], exact=True)
    sc.git_commit(repo, message, date=sc.ago(days=2))
    discard, unstage, keep = sc.sample(sorted(files), 3)
    junk = sc.pick(JUNK)
    sc.write(repo + "/" + discard, files[discard]["base"] + junk + "\n", exact=True)
    unstage_text = files[unstage]["base"] + files[unstage]["draft"] + "\n"
    sc.write(repo + "/" + unstage, unstage_text, exact=True)
    keep_text = files[keep]["base"] + files[keep]["good"] + "\n"
    sc.write(repo + "/" + keep, keep_text, exact=True)
    sc.git(repo, "add", unstage, keep)
    return discard, unstage, keep, junk, unstage_text, keep_text


def _tell_three(sc, repo, discard, unstage, keep, junk, unstage_text, keep_text):
    sc.fact("repo", repo)
    sc.fact("discard", discard)
    sc.fact("unstage", unstage)
    sc.fact("keep", keep)
    sc.fact("junk", junk)
    sc.fact("unstage_text", unstage_text)
    sc.fact("keep_text", keep_text)
    sc.fact("commits", 1)
    sc.todo("进入练习仓库：cd " + sc.show(repo))
    sc.todo(discard + "：多了一行手滑打的字，还没 git add。这处改动不要了。")
    sc.todo(unstage + "：已经 git add 了，但还没写完。这次先不提交它，写的内容要留在文件里。")
    sc.todo(keep + "：已经 git add 了，改得没问题。下次提交要带上它，保持原样。")
    sc.todo("做完以后不要提交。")


def build_b(sc):
    """Station 1.8b: a trip plan with three files and three outcomes."""
    repo = "trip-" + sc.word()
    parts = _build_three(sc, repo, TRIP, "旅行计划初稿")
    _tell_three(sc, repo, *parts)


def build_review(sc):
    """The review copy for 1.8-d1: the same skill on a different surface
    (a small garden notebook, other file names)."""
    repo = "garden-" + sc.word()
    parts = _build_three(sc, repo, GARDEN, "菜园记录")
    _tell_three(sc, repo, *parts)


SCENARIOS = {
    "start": build_start,
    "1.8a": build_a,
    "1.8b": build_b,
    "1.8-review": build_review,
}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _check_a_core(ctx):
    info = ctx.scenario("1.8a")
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "练习仓库 " + facts["repo"])
    again = "重搭一份练习再做：python3 tools/course.py scenario 1.8a --reset"
    if not _no_new_commit(ctx, repo, facts["commits"], again):
        ctx.stop()
    junk = _look(ctx, repo, facts["junk_file"])
    keep = _look(ctx, repo, facts["keep_file"])
    # Untouched: say so without naming the junk file (telling them apart is the task).
    junk_start = facts["junk"] + "\n" + CAFE[facts["junk_file"]]["base"].split("\n", 1)[1]
    if (_same(junk["work"], junk_start) and _same(keep["work"], facts["keep_text"])
            and junk["code"] == " M" and keep["code"] == " M"):
        ctx.fail("两处改动都还在，弄乱的那一个还没丢掉", where="练习仓库的两个文件",
                 saw="两个文件都还是开始时改过的样子")
        ctx.stop()
    junk_done = _want_committed(
        ctx, junk, facts["junk"],
        staged_note=("把改动拿出暂存区是第 2 站的内容（git status 的括号里写着命令）。"
                     "也可以重搭一份再做：python3 tools/course.py scenario 1.8a --reset"),
        gone_note=GONE_NOTE)
    name = keep["name"]
    if not keep["exists"]:
        ctx.fail(name + " 这个文件不见了", where="练习仓库的工作区", saw="找不到 " + name)
        ctx.note("里面那处没 git add 过的改动跟着没了，找不回来。" + again)
    elif _same(keep["work"], keep["head"]):
        ctx.fail(name + " 里你想要的那处改动不见了", where=name + " 的内容",
                 saw="文件回到了上次提交时的样子")
        ctx.note("没提交过的改动丢了就找不回来。" + again)
    elif not _same(keep["work"], facts["keep_text"]):
        ctx.fail(name + " 的内容和开始时不一样了", where=name + " 的内容", saw="想要的那处改动被改过")
    elif junk_done:
        ctx.ok(name + " 里想要的改动还在")


def check_a(ctx):
    _check_a_core(ctx)


def _check_b_core(ctx, key="1.8b", lost=LOST_NOTE, again=None):
    """Shared by the station check (key 1.8b) and the review item (key 1.8-review)."""
    info = ctx.scenario(key)
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "练习仓库 " + facts["repo"])
    if not _no_new_commit(ctx, repo, facts["commits"], again):
        ctx.stop()
    noted = set()
    d = _look(ctx, repo, facts["discard"])
    u = _look(ctx, repo, facts["unstage"])
    k = _look(ctx, repo, facts["keep"])
    d_ok = _want_committed(ctx, d, facts["junk"], gone_note=GONE_NOTE)
    u_ok = _want_unstaged_kept(ctx, u, facts["unstage_text"], noted=noted, lost=lost)
    # Only praise the untouched file once the learner has done something.
    _want_staged_kept(ctx, k, facts["keep_text"], praise=bool(d_ok or u_ok), noted=noted, lost=lost)


def check_b(ctx):
    _check_b_core(ctx, "1.8b",
                  again="重搭一份练习再做：python3 tools/course.py scenario 1.8b --reset")


def check_review(ctx):
    _check_b_core(ctx, "1.8-review", lost=REVIEW_LOST_NOTE)


checks = {
    "1.8a": check_a,
    "1.8b": check_b,
}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.8a": [
        "两个文件都改过，只有一个要丢。先弄清楚哪个是弄乱的，再动手；动手只动那一个。",
        ("先进入练习仓库：scenario 1.8a 打印的「进入练习仓库」那一行，照着敲那条 cd。"
         "然后运行 git status 看哪两个文件改了，再运行 git diff，看每个文件改了什么："
         "以 + 开头的是现在多出来的，以 - 开头的是存档里原来有的。"),
        ("相似的例子：跟我做里 index.html 被 style.css 的内容盖掉了，你先看了 git status 和 git diff，"
         "再用一条命令让它回到了上次提交的样子。这次也是一样的步骤，只是要点名弄乱的那个文件。"),
        ("答案：照 GIT-04 先看：git status，再 git diff。diff 里出现一串乱打的字、原来的一行也没了的那个文件，就是弄乱的。"
         "然后运行 git restore，后面空一格写那个文件的名字（比如要丢的是 notes.txt，就敲 git restore notes.txt；换成你看出来的那个文件名），另一个文件不要动。"
         "最后再 git status 看一眼。\n"
         "解释：git restore 只管你点名的文件，用暂存区里的版本（没 git add 过改动时就是上次提交的版本）把它盖掉；没点名的文件不受影响。"
         "如果两个都丢了，运行 python3 tools/course.py scenario 1.8a --reset 重搭一份再做。"),
    ],
    "1.8b": [
        "三个文件，三种结局：一个连内容一起丢掉；一个从暂存区拿下来，但写的内容留着；一个原样不动。",
        ("先进入练习仓库：scenario 1.8b 打印的「进入练习仓库」那一行。运行 git status，看每个文件列在哪一段下面。"
         "每一段下面的括号里，Git 已经写了那一段能用的命令。再对照 scenario 1.8b 打印的三行说明。"),
        ("相似的例子：跟我做里 index.html 已经 git add 了，你先把它从暂存区拿下来，文件内容一点没变；"
         "要连内容一起丢掉，还要再多一步。这次三个文件各走其中的一段路。"),
        ("答案：先 git status 看清三个文件各在哪一段。"
         "对“还没写完”的那个文件运行 git restore --staged，后面空一格写它的文件名；"
         "对“手滑打错、还没 git add”的那个，照 GIT-04 先用 git diff 加它的文件名看清会丢什么，"
         "再运行 git restore 加它的文件名；“改得没问题”的那个不要动。最后再 git status 看一眼。\n"
         "解释：--staged 只把改动从暂存区拿下来，不碰文件；拿下来以后再运行不带 --staged 的 git restore，"
         "才会用暂存区（这时是上次提交）的版本盖掉文件，改动就没了。"
         "做错了运行 python3 tools/course.py scenario 1.8b --reset 重搭一份。"),
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "1.8-r1", "type": "recall", "tier": "fluent", "station": "1.8a", "rule": "GIT-04",
     "q": "改坏了一个文件，还没 git add。想让它回到上一次提交时的样子，用哪条命令？这样做有什么风险？",
     "a": "git restore 文件名（换成那个文件的名字）。风险：这个文件里没提交的改动会直接丢掉，Git 找不回来。",
     "explain": "动手之前先 git status、再 git diff 看一眼会丢掉什么，这是 GIT-04 的要求。"},
    {"id": "1.8-r2", "type": "which", "tier": "fluent", "station": "1.8b",
     "q": "你已经 git add 了 notes.txt，但这次不想提交它，里面写的内容要留着。用哪条命令？",
     "options": ["git restore notes.txt", "git restore --staged notes.txt", "rm notes.txt"],
     "answer": "B",
     "explain": ("--staged 只把它从暂存区拿下来，文件不动。不带 --staged 的 git restore 用暂存区的版本盖工作区，"
                 "这里什么也不会变；rm 会把文件本身删掉。")},
    {"id": "1.8-r3", "type": "predict", "tier": "lookup", "station": "1.8b",
     "q": "a.txt 改过，并且已经 git add。运行 git restore --staged a.txt 之后，git status 会把 a.txt 列在哪一段下面？",
     "options": ["Changes to be committed", "Changes not staged for commit", "哪里都不列：工作区是干净的"],
     "answer": "B",
     "explain": "改动从暂存区拿下来了，但文件里的内容还在，所以是“改了、还没放进暂存区”。"},
    {"id": "1.8-r4", "type": "fault", "tier": "fluent", "station": "1.8b", "rule": "GIT-04",
     "q": "小周只想丢掉 style.css 里还没提交的改动。他什么也没看，直接在仓库根目录敲了：\n\n    git restore .\n\n问题出在哪里？",
     "options": ["点代表当前文件夹：所有没 git add 的改动都会丢",
                 "git restore 后面不能跟一个点：它只认文件名，会报错",
                 "要先用 git add 把 style.css 放进暂存区，git restore 才能用"],
     "answer": "A",
     "explain": ("点是“当前文件夹”，git restore . 会把这个文件夹里所有还没 git add 的改动都盖掉，找不回来。"
                 "应该先 git status、git diff，再只点名 style.css。")},
    {"id": "1.8-r5", "type": "predict", "tier": "lookup", "station": "1.8a",
     "q": "new.txt 是刚用 touch 新建的，从来没有 git add 过。运行 git restore new.txt 会怎样？",
     "options": ["new.txt 被删掉", "报错：error: pathspec 'new.txt' did not match any file(s) known to git",
                 "什么也不显示，new.txt 变成空文件"],
     "answer": "B",
     "explain": "Git 只认识它跟踪的文件，也就是 add 过、存过版本的文件。new.txt 从没 add 过，存档里没有它的版本，git restore 无从恢复，就报这个错。"},
    {"id": "1.8-d1", "type": "do", "tier": "fluent", "station": "1.8b", "rule": "GIT-04",
     "q": ("练习仓库里有三个改过的文件，搭好以后屏幕上会说明每个文件的情况："
           "一个的改动不要了，一个要从暂存区拿下来但内容留着，一个保持原样。按说明处理好，不要提交。"),
     "scenario": "1.8-review", "check": check_review},
]


# ---------------------------------------------------------------------------
# EXAM (gate-b)
# ---------------------------------------------------------------------------
SHOP = {
    "prices.txt": {"base": "苹果 6 元一斤\n香蕉 4 元一斤\n", "good": "橙子 5 元一斤",
                   "draft": "西瓜：（价钱还没定）"},
    "notice.txt": {"base": "本店营业到晚上九点\n", "good": "周日休息",
                   "draft": "国庆节安排：（还没想好）"},
    "staff.txt": {"base": "早班：小林\n晚班：阿青\n", "good": "周末：小周",
                  "draft": "替班：（待定）"},
}


def build_x1(sc):
    """Form A: discard one unstaged junk change, unstage one draft (keep its text).
    Form B: one staged junk change must go entirely, one staged good change stays."""
    repo = "shop-" + sc.word()
    sc.git_init(repo)
    for name, parts in SHOP.items():
        sc.write(repo + "/" + name, parts["base"], exact=True)
    sc.git_commit(repo, "小店的第一版说明", date=sc.ago(days=3))
    first, second = sc.sample(sorted(SHOP), 2)
    junk = sc.pick(JUNK)
    junk_text = SHOP[first]["base"] + junk + "\n"
    sc.write(repo + "/" + first, junk_text, exact=True)
    if sc.form == "A":
        other_text = SHOP[second]["base"] + SHOP[second]["draft"] + "\n"
        sc.write(repo + "/" + second, other_text, exact=True)
        sc.git(repo, "add", second)
    else:
        other_text = SHOP[second]["base"] + SHOP[second]["good"] + "\n"
        sc.write(repo + "/" + second, other_text, exact=True)
        sc.git(repo, "add", first, second)
    sc.fact("repo", repo)
    sc.fact("bad", first)
    sc.fact("other", second)
    sc.fact("junk", junk)
    sc.fact("other_text", other_text)
    sc.fact("commits", 1)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库 " + facts["repo"])
    if not _no_new_commit(ctx, repo, facts["commits"]):
        ctx.stop()
    bad = _look(ctx, repo, facts["bad"])
    other = _look(ctx, repo, facts["other"])
    bad_ok = _want_committed(ctx, bad, facts["junk"])
    if info.form == "A":
        _want_unstaged_kept(ctx, other, facts["other_text"], lost=EXAM_LOST_NOTE)
    else:
        _want_staged_kept(ctx, other, facts["other_text"], praise=bool(bad_ok), lost=EXAM_LOST_NOTE)


DRAFTS = ["draft-notes.txt", "scratch.txt", "todo-tmp.txt", "ideas.txt"]


def build_x2(sc):
    """A new file was staged by mistake.  Form A: only that file.  Form B: a
    tracked file is staged too and must stay staged."""
    repo = "blog-" + sc.word()
    sc.git_init(repo)
    sc.write(repo + "/index.html", "<h1>我的小博客</h1>\n<p>第一篇文章</p>\n", exact=True)
    sc.git_commit(repo, "博客首页", date=sc.ago(days=2))
    new = sc.pick(DRAFTS)
    new_text = "随手记的草稿，不打算放进仓库\n" + sc.word() + "\n"
    sc.write(repo + "/" + new, new_text, exact=True)
    sc.git(repo, "add", new)
    page_text = "<h1>我的小博客</h1>\n<p>第一篇文章</p>\n<p>第二篇文章</p>\n"
    if sc.form == "B":
        sc.write(repo + "/index.html", page_text, exact=True)
        sc.git(repo, "add", "index.html")
    sc.fact("repo", repo)
    sc.fact("new", new)
    sc.fact("new_text", new_text)
    sc.fact("page_text", page_text)
    sc.fact("commits", 1)


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库 " + facts["repo"])
    if not _no_new_commit(ctx, repo, facts["commits"]):
        ctx.stop()
    new = facts["new"]
    path = repo.path / new
    done = False
    if not ctx.is_file(path):
        ctx.fail(new + " 这个文件不见了，它本来要留在文件夹里", where="考试仓库的文件夹", saw="找不到 " + new)
    elif not _same(ctx.read(path), facts["new_text"]):
        ctx.fail(new + " 的内容和开始时不一样了", where=new + " 的内容", saw="文件被改动过")
    elif _index_text(repo, new) is not None:
        # The staging area still has an entry for the new file, so git status
        # lists it as "new file:" under Changes to be committed.  A file that is
        # out of the staging area passes whether it shows as untracked or is
        # also ignored by a .gitignore: the task's goal is met either way.
        ctx.fail(new + " 还在暂存区里，下次提交会把它带上", where="git status",
                 saw=new + " 列在 Changes to be committed 下面")
    else:
        done = ctx.ok(new + " 不在暂存区了，文件还在")
    if info.form == "B":
        page = _look(ctx, repo, "index.html")
        _want_staged_kept(ctx, page, facts["page_text"], praise=done, lost=EXAM_LOST_NOTE)
        others = [p for p in repo.status().staged if p not in ("index.html", new)]
        if others:
            ctx.fail("下次提交只要 index.html 的改动，暂存区里还有别的", where="git status",
                     saw="Changes to be committed 下面还有：" + "、".join(others))


EXAM = [
    {
        "id": "1.8-x1",
        "gate": "gate-b",
        "title": "撤销还没提交的改动",
        "minutes": 6,
        "build": build_x1,
        "task": {
            "A": ("先 cd 进 {dir}/{repo}。{bad} 里多了一行手滑打的字，这处改动不要了；"
                  "{other} 已经放进了暂存区，但还没写完，这次不提交它，写的内容要留在文件里。"
                  "处理好这两个文件，不要提交。"),
            "B": ("先 cd 进 {dir}/{repo}。{bad} 和 {other} 都已经放进了暂存区。"
                  "{bad} 里那行字是手滑打的：让它彻底回到上次提交时的样子；"
                  "{other} 的改动保持原样，下次提交要带上。不要提交。"),
        },
        "grade": grade_x1,
    },
    {
        "id": "1.8-x2",
        "gate": "gate-b",
        "title": "把误放进暂存区的新文件拿出来",
        "minutes": 4,
        "build": build_x2,
        "task": {
            "A": ("先 cd 进 {dir}/{repo}。新文件 {new} 被误放进了暂存区。"
                  "让它不再进入下次提交，但文件本身要留在文件夹里。不要提交。"),
            "B": ("先 cd 进 {dir}/{repo}。暂存区里现在有两处改动：新文件 {new} 和 index.html 的改动。"
                  "下次提交只要 index.html 的改动；{new} 留在文件夹里，但不进入下次提交。不要提交。"),
        },
        "grade": grade_x2,
    },
]
