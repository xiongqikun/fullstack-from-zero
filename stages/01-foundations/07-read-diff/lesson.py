"""Lesson 1.7 Git：看懂改了什么 (plan section 4, task T2).

Station a: git diff / git diff --staged on uncommitted work.
Station b: changes stored in history: git log --stat, git show; the pager.

Both exercises are ask checks on seeded scenarios in which a colleague
changed two things (1.7a: a number and a removed line, uncommitted; 1.7b:
a removed line and a changed price in one commit); every expected answer
comes from ``sc.fact``.
Standard library only, Python 3.9 syntax.  API: docs/authoring/tool-api.md.
"""

import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "1.7",
    "slug": "07-read-diff",
    "title": "Git：看懂改了什么",
    "stage": 1,
    "prerequisites": ["1.6"],
    "stations": [
        {
            "id": "1.7a",
            "title": "还没提交的改动：git diff 和 git diff --staged",
            "minutes": 40,
            "new_concept": "差异（diff）：一行一行列出两个地方之间删了什么、加了什么",
            "new_commands": ["git diff", "git diff --staged"],
        },
        {
            "id": "1.7b",
            "title": "历史里的改动：git log --stat 和 git show",
            "minutes": 40,
            "new_concept": "每个提交的改动都随时能调出来看",
            "new_commands": ["git log --stat", "git show"],
        },
    ],
    "rules": ["GIT-03"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9",
                  "less": "668"},
    },
    "unverified_steps": [
        "1.7a 在 VS Code 里改 style.css 并保存（图形界面，对照 1.4 课和 VS Code 官方文档）",
        "1.7b 输出超过一屏时 Git 用 less 分页显示：底部的冒号、(END)、空格翻页、q 退出"
        "（建课环境没有终端窗口，对照 git-config 手册 core.pager 一节和 less 668 手册）",
    ],
}

TERMS = [
    {"term": "差异", "en": "diff",
     "plain": "两个版本之间的对照清单：哪些行删掉了，哪些行加上了", "first": "1.7a"},
    {"term": "改动块", "en": "hunk",
     "plain": "diff 里以 @@ 开头的一段，是文件里挨在一起的一处改动", "first": "1.7a"},
    {"term": "占位写法", "en": "placeholder",
     "plain": "命令说明里用尖括号括起来的一段，比如 <file>：真敲的时候换成具体的名字，尖括号不敲", "first": "1.7a"},
    {"term": "分页器", "en": "pager",
     "plain": "输出太长时，Git 交给它一屏一屏地显示的程序，这台电脑上是 less", "first": "1.7b"},
]


# ---------------------------------------------------------------------------
# Helpers for answers (the learner's text arrives normalised: lower case,
# half-width, trimmed)
# ---------------------------------------------------------------------------
NUMBER = re.compile(r"\d+(?:\.\d+)?")
# a Chinese numeral (十三, 二十六, 七点零八) counts only when 元/块, a non-Chinese
# character or the end follows it, so 一样 / 一行 are words, not numbers
CN_NUMBER = re.compile(r"[零〇一二两三四五六七八九十百千]+(?:点[零〇一二三四五六七八九]+)?"
                       r"(?=$|[元块角\s\W\da-z])")
CN_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
             "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNITS = {"十": 10, "百": 100, "千": 1000}


def _cn_value(text):
    """Value of a plainly written Chinese numeral (十三 13, 七点零八 7.08); None otherwise."""
    whole, _dot, frac = text.partition("点")
    total, digit, last = 0, None, None
    for ch in whole:
        if ch in CN_DIGITS:
            if digit is not None and digit != 0:
                return None                       # 三四: two digits in a row
            digit = CN_DIGITS[ch]
        else:
            unit = CN_UNITS[ch]
            if last is not None and unit >= last:
                return None
            total += (1 if digit is None else digit) * unit
            digit, last = None, unit
    if digit is not None:
        total += digit
    if not whole:
        return None
    if frac:
        return float(str(total) + "." + "".join(str(CN_DIGITS[c]) for c in frac))
    return total


def _numbers(text):
    """(start, end, value) of every number in ``text``: digits and Chinese numerals."""
    found = [(m.start(), m.end(), float(m.group())) for m in NUMBER.finditer(text)]
    for m in CN_NUMBER.finditer(text):
        value = _cn_value(m.group())
        if value is not None:
            found.append((m.start(), m.end(), float(value)))
    return sorted(found)


def _number_positions(text, value):
    """Start offsets of the numbers in ``text`` equal to ``value`` (7.1 equals 7.10, 十三 equals 13)."""
    return [start for start, _end, v in _numbers(text) if abs(v - float(value)) < 1e-9]


# words that say which side of a change a number is on ("从 7.27 改成 7.05", "现价 13 元（原价 12 元）")
OLD_MARKERS = ("原来", "原本", "原价", "原", "本来", "之前", "以前", "改前", "旧价", "旧", "从", "old", "was")
NEW_MARKERS = ("现在", "现价", "现", "如今", "改成", "改为", "变成", "成了", "涨到", "降到", "调到",
               "之后", "改后", "后来", "新价", "新", "now", "->", "→")


def _side(text, pos):
    """"old", "new" or None: the marker word nearest before the number at ``pos``.

    Only the text after the previous number counts, so the marker of one
    number is never read as the marker of the next ("现价12原价13").
    """
    start = max(0, pos - 6)
    for _s, end, _v in _numbers(text):
        if start < end <= pos:
            start = end
    window = text[start:pos]
    best, side = -1, None
    for words, name in ((OLD_MARKERS, "old"), (NEW_MARKERS, "new")):
        for word in words:
            at = window.rfind(word)
            if at >= 0 and at + len(word) > best:
                best, side = at + len(word), name
    return side


def _in_brackets(text, pos):
    """The number at ``pos`` stands inside brackets that open after an earlier number."""
    opened = text.rfind("(", 0, pos)
    if opened < 0 or text.find(")", opened, pos) >= 0:
        return False
    return any(end <= opened for _s, end, _v in _numbers(text))


def _value_answer(value, other, role):
    """Answer gives ``value`` (role "old" or "new") of a change from one number to another.

    Accepted: ``value`` alone (unless a marker word right before it puts it on
    the other side: 原价 13 for the new price); or both numbers when the answer
    says which is which: the nearest marker word before ``value`` (原来 / 原价 /
    从 for the old one, 现在 / 现价 / 改成 / 涨到 / → for the new one), or such a
    marker before the other number (13 元，原价 12 元); or the other number
    standing in brackets after ``value`` as an aside (13 元（12 元）); or else
    the order old before new, which is how a diff reads (从 X 改成 Y).
    Numbers may be written in digits or Chinese numerals (十三元).
    """
    opposite = "new" if role == "old" else "old"

    def test(typed):
        mine = _number_positions(typed, value)
        if not mine:
            return False
        theirs = _number_positions(typed, other)
        side = _side(typed, mine[0])
        if not theirs:
            return side != opposite
        if side == role:
            return True
        if side == opposite:
            return False
        side_other = _side(typed, theirs[0])
        if side_other == opposite:                       # "28 元（原来 4 元）"
            return True
        if side_other == role:
            return False
        mine_aside, theirs_aside = _in_brackets(typed, mine[0]), _in_brackets(typed, theirs[0])
        if theirs_aside != mine_aside:                   # "13 元（12 元）"
            return theirs_aside
        old_at, new_at = (mine[0], theirs[0]) if role == "old" else (theirs[0], mine[0])
        return old_at < new_at
    return test


def _only(value, other):
    """Answer contains ``value`` and not ``other`` (for targeted notes)."""
    def test(typed):
        return bool(_number_positions(typed, value)) and not _number_positions(typed, other)
    return test


def _file_pattern(name):
    """A file name inside free text: glued to Chinese, in brackets, with a/ b/ ./ or
    a folder in front, with or without its extension; never part of a longer name."""
    stem, ext = name.lower().rsplit(".", 1)
    return re.compile(r"(?<![a-z0-9_.\-])" + re.escape(stem) + r"(?:\." + re.escape(ext) + r")?"
                      r"(?![a-z0-9_\-]|\.[a-z0-9])")


def _is_file(name, others):
    """Answer names file ``name`` and no other file of the repository."""
    right = _file_pattern(name)
    wrong = [_file_pattern(o) for o in others]

    def test(typed):
        if not right.search(typed):
            return False
        return not any(w.search(typed) for w in wrong)
    return test


def _names_one(right, wrong_ones):
    """Answer contains the text ``right`` and none of ``wrong_ones``."""
    return _names_any([right], wrong_ones)


def _short_forms(word, other_side):
    """``word`` and its Chinese beginnings of two or more characters (宫保 for 宫保鸡丁)
    that appear in no word of ``other_side``; codes like krw keep only their full form."""
    word = word.lower()
    forms = [word]
    if not word.isascii():
        forms += [word[:k] for k in range(2, len(word))
                  if not any(word[:k] in o.lower() for o in other_side)]
    return forms


def _mentions(typed, words, other_side):
    """The answer names one of ``words``, in full or by a beginning no word of ``other_side`` shares."""
    return any(f in typed for w in words for f in _short_forms(w, other_side))


def _names_any(rights, wrong_ones):
    """Answer names one of ``rights`` (in full or by an unambiguous beginning) and none of ``wrong_ones``."""
    def test(typed):
        if not _mentions(typed, rights, wrong_ones):
            return False
        return not _mentions(typed, wrong_ones, rights)
    return test


def _names_both(rights, wrong_ones):
    """Answer names one of ``rights`` and also one of ``wrong_ones`` (for a targeted note)."""
    def test(typed):
        return _mentions(typed, rights, wrong_ones) and _mentions(typed, wrong_ones, rights)
    return test


def _site_progress(repo):
    """"staged", "committed" or None: how far the colour change of 1.7 got in ``repo``."""
    if "style.css" in repo.status().staged:
        return "staged"
    names = [path for _letter, path in repo.changed_files("HEAD")]
    if repo.commit_count() >= 2 and "style.css" in names:
        return "committed"
    return None


def _my_site_note(ctx, station):
    """A neutral remark about the learner's own my-site, or about the copy that
    ``scenario 1.7`` built for a learner whose my-site is broken (never a fail)."""
    sites = []
    own = ctx.git(ctx.my_site)
    if own.is_repo:
        sites.append(("你自己的 my-site ", own))
    start = ctx.scenario("start", required=False)
    if start.exists and start.facts.get("site"):
        copy = ctx.git(start.path / start.facts["site"])
        if copy.is_repo:
            sites.append(("练习场里的网站副本", copy))
    if not sites:
        return
    for name, repo in sites:
        progress = _site_progress(repo)
        if progress == "staged":
            ctx.note(name + "里，style.css 的改动在暂存区，第 2 站开头会把它提交。")
            return
        if progress == "committed":
            ctx.note(name + "里已经有改 style.css 的那次提交了。")
            return
    names = "和".join(name for name, _repo in sites)
    if station == "1.7a":
        ctx.note(names + "里还没看到放进暂存区的 style.css；第 2 站开头要用到它。")
    else:
        ctx.note(names + "里还看不到改颜色的那次提交，回到第 2 站「跟我做」第 1 步。")


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
COLLEAGUES = [("同事小林", "lin@example.invalid"), ("同事阿青", "qing@example.invalid")]

CONVERT_PY = '''\
"""汇率换算小程序：把一笔美元换算成人民币，打印一行结果。"""

AMOUNT_USD = 100  # 要换算的金额，单位是美元
USD_TO_CNY = {rate}  # 1 美元换多少人民币（练习用的数字）


def main():
    amount_cny = AMOUNT_USD * USD_TO_CNY
    print(f"{{AMOUNT_USD}} 美元 ≈ {{amount_cny:.2f}} 人民币")


if __name__ == "__main__":
    main()
'''

RATES = [
    ("EUR", "欧元", "0.92"),
    ("JPY", "日元", "150.00"),
    ("GBP", "英镑", "0.79"),
    ("HKD", "港币", "7.80"),
    ("KRW", "韩元", "1350.00"),
    ("SGD", "新加坡元", "1.34"),
    ("AUD", "澳元", "1.52"),
]

# everyday names a learner may write for a currency besides the ones in rates.txt
CURRENCY_ALIASES = {
    "JPY": ["日币", "日圆", "日本"],
    "GBP": ["英国"],
    "HKD": ["港元", "香港"],
    "KRW": ["韩币", "韩圆", "韩国"],
    "SGD": ["新币", "新加坡"],
}


def _currency_words(code, name):
    return [code, name] + CURRENCY_ALIASES.get(code, [])


RATE_VALUES = ["7.05", "7.08", "7.12", "7.15", "7.18", "7.21", "7.24", "7.27"]


def _rates_text(rows):
    lines = ["# 1 美元可以换多少其他货币。数字是练习用的，不是真实汇率。"]
    for code, name, value in rows:
        lines.append(f"{code}  {name}  {value}")
    return "\n".join(lines) + "\n"


def build_start(sc):
    """The state just before 1.7: a copy of the learner's site in state S4."""
    sc.site_before()
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))
    sc.todo("你自己的 ~/Developer/my-site 坏了或者还不是仓库时，就用这份副本做本课的「跟我做」。")
    sc.todo("先进去：cd " + sc.show(sc.facts["site"]))


def build_1_7a(sc):
    """A colleague's exchange-rate program with two uncommitted changes.

    One file's change is staged and the other's is not (seeded), so each of
    the two diff commands is needed for one of the questions.
    """
    repo = "fx-" + sc.word()
    author = sc.pick(COLLEAGUES)
    old, new = sc.sample(RATE_VALUES, 2)
    removed = sc.pick(RATES[1:-1])            # never the first or last line
    sc.git_init(repo)
    sc.write(repo + "/convert.py", CONVERT_PY.format(rate=old), exact=True)
    sc.git_commit(repo, "添加汇率换算小程序", author=author, date=sc.ago(days=3))
    sc.write(repo + "/rates.txt", _rates_text(RATES), exact=True)
    sc.git_commit(repo, "添加各种货币的汇率表", author=author, date=sc.ago(days=2))
    # the colleague's unfinished work
    sc.write(repo + "/convert.py", CONVERT_PY.format(rate=new), exact=True)
    sc.write(repo + "/rates.txt", _rates_text([r for r in RATES if r != removed]), exact=True)
    staged = sc.pick(["convert.py", "rates.txt"])
    sc.git(repo, "add", staged)
    sc.fact("repo", repo)
    sc.fact("staged", staged)
    sc.fact("unstaged", "rates.txt" if staged == "convert.py" else "convert.py")
    sc.fact("old_rate", old)
    sc.fact("new_rate", new)
    sc.fact("removed_code", removed[0])
    sc.fact("removed_name", removed[1])
    sc.fact("codes", [r[0] for r in RATES])
    sc.fact("names", [r[1] for r in RATES])
    sc.todo("同事的汇率小程序在这里：" + sc.show(repo))
    sc.todo(author[0][2:] + "改了两个文件，还没提交，其中一个已经 git add 过了。")
    sc.todo("先进去：cd " + sc.show(repo))


MENU = [("番茄炒蛋", 18), ("宫保鸡丁", 26), ("麻婆豆腐", 16), ("鱼香肉丝", 24),
        ("青椒土豆丝", 12), ("红烧茄子", 15)]
DRINKS = [("柠檬茶", 8), ("豆浆", 4), ("绿豆汤", 6), ("酸梅汤", 7), ("奶茶", 12), ("美式咖啡", 15)]
VAGUE = ["小改动", "更新一下", "改了点东西", "整理一下"]

PAGE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
  <h1>{title}</h1>
  <p>{line}</p>
</body>
</html>
"""


def _list_text(header, rows):
    return header + "\n" + "".join(f"{name}  {price} 元\n" for name, price in rows)


def build_1_7b(sc):
    """A small shop site with a long history by two colleagues.

    One commit with a vague message changed two things in one file: it
    removed one item and changed another item's price (the exercise asks
    three questions about it: the file, the removed item, the new price).  The history is
    long enough (14 commits) that ``git log --stat`` fills more than a screen.
    """
    repo = "shop-" + sc.word()
    target = sc.pick(["menu.txt", "drinks.txt"])
    subject = sc.pick(VAGUE)
    sc.git_init(repo)
    menu, drinks = list(MENU[:4]), list(DRINKS[:4])
    lin, qing = COLLEAGUES
    day = [14]

    def commit(message, who):
        sc.git_commit(repo, message, author=who, date=sc.ago(days=day[0], hours=sc.randint(1, 9)))
        day[0] -= 1

    sc.write(repo + "/index.html", PAGE.format(title="街角小馆", line="家常菜，现点现做。"), exact=True)
    commit("第一版小店网页", lin)
    sc.write(repo + "/menu.txt", _list_text("# 菜单", menu), exact=True)
    commit("加上菜单", lin)
    sc.write(repo + "/drinks.txt", _list_text("# 饮品", drinks), exact=True)
    commit("加上饮品", qing)
    sc.write(repo + "/hours.txt", "营业时间：每天 10:00 到 20:00\n", exact=True)
    commit("写上营业时间", qing)
    menu += MENU[4:]
    sc.write(repo + "/menu.txt", _list_text("# 菜单", menu), exact=True)
    commit("菜单加两道菜", lin)
    drinks += DRINKS[4:]
    sc.write(repo + "/drinks.txt", _list_text("# 饮品", drinks), exact=True)
    commit("饮品加两样", qing)
    sc.write(repo + "/index.html", PAGE.format(title="街角小馆", line="家常菜，现点现做。地址：梧桐路 8 号。"),
             exact=True)
    commit("首页写上地址", lin)
    sc.write(repo + "/hours.txt", "营业时间：每天 10:00 到 21:00\n", exact=True)
    commit("营业时间改到晚上九点", qing)

    # the commit the exercise is about
    rows = list(menu if target == "menu.txt" else drinks)
    # two middle rows with at least one unchanged row between them, so the
    # removed line and the changed price never sit next to each other
    first, second = sc.pick([(1, 3), (1, 4), (2, 4), (3, 1), (4, 1), (4, 2)])
    removed, changed = rows[first], rows[second]
    used = set(price for _name, price in rows)
    new_price = sc.pick([p for p in range(9, 40) if p not in used])
    rows = [(n, new_price if n == changed[0] else p) for n, p in rows if n != removed[0]]
    header = "# 菜单" if target == "menu.txt" else "# 饮品"
    sc.write(repo + "/" + target, _list_text(header, rows), exact=True)
    commit(subject, sc.pick(COLLEAGUES))
    full = sc.git(repo, "rev-parse", "HEAD").strip()

    sc.write(repo + "/index.html", PAGE.format(title="街角小馆 · 家常菜", line="家常菜，现点现做。地址：梧桐路 8 号。"),
             exact=True)
    commit("首页标题加上家常菜", lin)
    sc.write(repo + "/hours.txt", "营业时间：每天 10:00 到 21:00，周一休息\n", exact=True)
    commit("营业时间写上周一休息", qing)
    sc.write(repo + "/phone.txt", "订座电话：010-0000-0000（练习用的号码）\n", exact=True)
    commit("加上订座电话", lin)
    sc.write(repo + "/index.html", PAGE.format(title="街角小馆 · 家常菜",
                                               line="家常菜，现点现做。地址：梧桐路 8 号，订座见 phone.txt。"),
             exact=True)
    commit("首页提到订座电话", qing)
    sc.write(repo + "/hours.txt", "营业时间：每天 10:00 到 21:00，周一休息，节假日照常营业\n", exact=True)
    commit("营业时间写上节假日", lin)

    sc.fact("repo", repo)
    sc.fact("subject", subject)
    sc.fact("commit", full)
    sc.fact("file", target)
    sc.fact("files", ["index.html", "menu.txt", "drinks.txt", "hours.txt", "phone.txt"])
    sc.fact("removed", removed[0])
    sc.fact("changed", changed[0])
    sc.fact("old_price", changed[1])
    sc.fact("new_price", new_price)
    sc.fact("items", [n for n, _p in MENU + DRINKS])
    sc.fact("commits", 14)
    sc.todo("小店网站的仓库在这里：" + sc.show(repo))
    sc.todo("两位同事已经在里面提交了 14 次。")
    sc.todo("「自己做」要找的那个提交，说明写的是「" + subject + "」。")
    sc.todo("先进去：cd " + sc.show(repo))


SCENARIOS = {"start": build_start, "1.7a": build_1_7a, "1.7b": build_1_7b}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _in_review(ctx, path):
    """``path`` is a copy that ``review`` built under playground/review (the do item)."""
    try:
        path.resolve().relative_to((ctx.playground / "review").resolve())
    except ValueError:
        return False
    return True


def _read_uncommitted(ctx, key):
    """Shared by check 1.7a and the do item 1.7-d1: two questions on the 1.7a copy."""
    info = ctx.scenario(key)
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "同事的汇率小程序 " + facts["repo"])
    status = repo.status()
    if status.staged != [facts["staged"]] or status.unstaged != [facts["unstaged"]] or status.untracked:
        if _in_review(ctx, info.path):
            again = "运行 python3 tools/course.py review --give-up，下次会换一份"
        else:
            again = "先运行 python3 tools/course.py scenario 1.7a --reset 重搭一份"
        ctx.fail("仓库和搭好时不一样了。" + again,
                 where="练习仓库的 git status",
                 saw=f"暂存区里：{len(status.staged)} 个文件；没暂存的：{len(status.unstaged)} 个文件")
        ctx.stop()
    ctx.ok("练习仓库还是搭好时的样子：两个文件改了，一个进了暂存区")
    if not ctx.ask("convert.py 里有一个数被改了。改之前它是多少？",
                   _value_answer(facts["old_rate"], facts["new_rate"], "old")):
        if _only(facts["new_rate"], facts["old_rate"])(ctx.normalize(ctx.last_answer)):
            ctx.note("你写的是文件里现在的数。题目问的是改之前的那个：在差异里它是哪种符号开头的行？")
        elif not _numbers(ctx.normalize(ctx.last_answer)):
            ctx.note("这一题要写一个数：convert.py 的差异里，减号行和加号行各有一个。")
    rows = list(zip(facts["codes"], facts.get("names") or [r[1] for r in RATES]))
    removed = [r for r in rows if r[0] == facts["removed_code"]][0]
    others = [w for r in rows if r != removed for w in _currency_words(*r)]
    rights = _currency_words(*removed)
    if not ctx.ask("rates.txt 里删掉了一行。删掉的是哪种货币？照 rates.txt 里写的，写出三个字母代码或者中文名。",
                   _names_any(rights, others)):
        if _names_both(rights, others)(ctx.normalize(ctx.last_answer)):
            ctx.note("你的回答里不止一种货币，检查分不清你说的是哪一种。只写被删掉的那一种。")


def check_a(ctx):
    _read_uncommitted(ctx, "1.7a")
    _my_site_note(ctx, "1.7a")


def _read_history(ctx, key):
    """Shared by check 1.7b: three questions on the shop history."""
    info = ctx.scenario(key)
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "小店网站的仓库 " + facts["repo"])
    if repo.commit(facts["commit"]) is None:
        ctx.fail("找不到搭好时的那段历史了。先运行 python3 tools/course.py scenario 1.7b --reset 重搭一份",
                 where="练习仓库的 git log", saw="历史和搭好时不一样")
        ctx.stop()
    ctx.ok("练习仓库的历史还在")
    subject = facts["subject"]
    ctx.ask(f"提交说明是「{subject}」的那个提交，改的是哪个文件？写出文件名。",
            _is_file(facts["file"], [f for f in facts["files"] if f != facts["file"]]))
    wrong = [n for n in facts["items"] if n != facts["removed"]]
    if not ctx.ask("在这个提交里，有一样东西被整行删掉了。它叫什么？", _names_one(facts["removed"], wrong)):
        typed = ctx.normalize(ctx.last_answer)
        if _names_both([facts["removed"]], wrong)(typed):
            ctx.note("你的回答里不止一样东西的名字，检查分不清你说的是哪一样。只写被整行删掉的那一样。")
        elif _mentions(typed, [facts["changed"]], [facts["removed"]]):
            ctx.note("你写的那一样在这个提交之后还在文件里。整行删掉的那一行只有减号，没有同名的加号行。")
    if not ctx.ask("在这个提交里，还有一样东西的价格变了。它现在卖多少元？",
                   _value_answer(facts["new_price"], facts["old_price"], "new")):
        if _only(facts["old_price"], facts["new_price"])(ctx.normalize(ctx.last_answer)):
            ctx.note("你写的是改之前的价格。现在的价格在哪种符号开头的行里？")


def check_b(ctx):
    _read_history(ctx, "1.7b")
    _my_site_note(ctx, "1.7b")


checks = {"1.7a": check_a, "1.7b": check_b}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "1.7a": [
        "两道题都能从两条命令的输出里读出来：一条看还没放进暂存区的改动，一条看已经放进暂存区的改动。"
        "回想 Git 图：这两条命令各比较哪两个区域？两个文件的改动不在同一个区域里。",
        "先 cd 进同事的仓库（路径在 scenario 1.7a 的输出里），分别运行 git diff 和 git diff --staged。"
        "每条命令的输出以 diff --git a/文件名 开头，先认出是哪个文件，再找以 - 开头的行。",
        "相似的例子：你在 my-site 里把颜色从 #0b5cad 改成 #c2410c 并 git add 之后，"
        "git diff 什么也不显示，git diff --staged 里 -  color: #0b5cad; 是改之前，+  color: #c2410c; 是改之后。",
        "答案：在练习仓库里运行 git diff 和 git diff --staged，其中一条列出 convert.py 的改动，另一条列出 rates.txt 的。"
        "在 convert.py 那一段里找 -USD_TO_CNY = … 这一行，减号后面的数就是改之前的值（加号行是改之后的）；"
        "在 rates.txt 那一段里，只有减号、没有对应加号的那一行就是被删掉的货币，写它的代码或中文名。"
        "解释：git diff 比较工作区和暂存区，git diff --staged 比较暂存区和最新的提交，"
        "所以一处改动 git add 之后，就从第一条命令的输出挪到了第二条命令的输出里。",
    ],
    "1.7b": [
        "先找到那个提交，再打开它看。提交说明写得很含糊，光看说明猜不出改了什么，只能看它的改动。",
        "在小店仓库里运行 git log --oneline，找到说明是搭练习场景时屏幕上给出的那句话（「这里有什么」第三行）的一行，记下左边的编号；"
        "然后运行 git show 加这个编号。输出太长时按空格往下翻，按 q 退出。",
        "相似的例子：你在 my-site 里运行 git show 加“改了标题的颜色”那个提交的编号，"
        "看到 diff --git a/style.css b/style.css，说明改的是 style.css；"
        "-  color: #0b5cad; 是删掉的旧行，+  color: #c2410c; 是加上的新行。",
        "答案：运行 git log --oneline 找到那个提交的编号，再运行 git show <编号>。"
        "diff --git a/… b/… 这一行里的文件名是第 1 题的答案；只有减号、没有对应加号的那一行是被删掉的东西；"
        "同一个名字一行带减号、一行带加号，加号那行里的价格就是现在的价格。"
        "解释：git show 把一个提交和它的上一个提交对照，列出这一次删了哪些行、加了哪些行；"
        "改一个数时，Git 会把整行当成先删后加。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
def _do_uncommitted(ctx):
    _read_uncommitted(ctx, "1.7a")


REVIEW = [
    {"id": "1.7-p1", "type": "predict", "tier": "fluent", "station": "1.7a",
     "q": "你改了 index.html，并且已经 git add 了它。现在运行 git diff（不带 --staged），会看到什么？",
     "options": ["index.html 的改动", "什么也不显示，直接回到提示符", "报错：没有改动可以比较"],
     "answer": "B",
     "explain": "git diff 只比较工作区和暂存区；改动已经进了暂存区，两边一样，所以没有输出。"
                "要看已经放进暂存区的改动，用 git diff --staged。"},
    {"id": "1.7-w1", "type": "which", "tier": "fluent", "station": "1.7b",
     "q": "git log --oneline 里有一个提交，说明只写了“小改动”。想看它到底改了哪些行，用哪条命令？",
     "options": ["git show <它的编号>", "git diff", "git status"],
     "answer": "A",
     "explain": "git show 把一个提交和它的上一个提交对照着列出来。git diff 和 git status 只看还没提交的东西。"},
    {"id": "1.7-w2", "type": "which", "tier": "fluent", "station": "1.7b",
     "q": "运行 git log 以后，终端最下面一行只剩一个冒号 :，敲字也不像平常那样出现。想回到命令提示符，按什么？",
     "options": ["按 q", "按回车", "按 Ctrl+C"],
     "answer": "A",
     "explain": "这是分页器 less 在等你翻页：空格往下翻一屏，q 退出。回车只往下挪一行；"
                "Ctrl+C 在 less 里退不出来。"},
    {"id": "1.7-r1", "type": "recall", "tier": "fluent", "station": "1.7b", "rule": "GIT-03",
     "q": "按行规 GIT-03，每次 git commit 之前要先做哪一步？为什么？",
     "a": "先 git status 看有哪些文件，再 git diff --staged 把这次要提交的改动逐行看一遍。"
          "因为提交的是暂存区里的东西，不看就可能把误删、调试用的内容一起存进历史，事后要翻历史才找得到。"},
    {"id": "1.7-r2", "type": "recall", "tier": "lookup", "station": "1.7a",
     "q": "diff 里有一行 @@ -8,5 +8,5 @@，它是什么意思？",
     "a": "这是一个改动块的开头：改之前从第 8 行起显示 5 行，改之后也从第 8 行起显示 5 行。"
          "下面以空格开头的行没变，- 开头的行是删掉的，+ 开头的行是加上的。"},
    {"id": "1.7-d1", "type": "do", "tier": "fluent", "station": "1.7a",
     "q": "同事改了两个文件还没提交，其中一个已经 git add 过。用 Git 看清楚这两处改动，然后回答两个问题。",
     "scenario": "1.7a", "check": _do_uncommitted},
]


# ---------------------------------------------------------------------------
# EXAM (gate-b)
# ---------------------------------------------------------------------------
CLUB_MEMBERS = ["阿木", "小禾", "阿远", "小舟", "阿北", "小周"]
TITLES = ["周末读书会", "城南跑步群", "楼下羽毛球队", "午休摄影小组"]
PRICES = [("门票", 30), ("茶水", 10), ("场地费", 20), ("资料费", 15)]
SCHEDULE = ["周六 09:00 集合", "周六 09:30 出发", "周六 11:30 午饭", "周六 14:00 分享", "周六 16:00 散场"]


def build_x1(sc):
    """Two uncommitted changes in two files: one wanted, one an accidental deletion."""
    repo = "club-" + sc.word()
    sc.git_init(repo)
    if sc.form == "A":
        sc.write(repo + "/index.html", PAGE.format(title="活动小组", line="欢迎加入。"), exact=True)
        members = sc.sample(CLUB_MEMBERS, 5)
        sc.write(repo + "/members.txt", "# 成员\n" + "".join(m + "\n" for m in members), exact=True)
        sc.git_commit(repo, "第一版小组网页")
        title = sc.pick(TITLES)
        lost = sc.pick(members[1:-1])
        sc.write(repo + "/index.html", PAGE.format(title=title, line="欢迎加入。"), exact=True)
        sc.write(repo + "/members.txt", "# 成员\n" + "".join(m + "\n" for m in members if m != lost),
                 exact=True)
        sc.fact("wanted_file", "index.html")
        sc.fact("wanted_text", title)
        sc.fact("lost_file", "members.txt")
        sc.fact("lost_text", lost)
        sc.fact("title", title)
    else:
        rows = sc.sample(PRICES, 3)
        sc.write(repo + "/prices.txt", "# 费用\n" + "".join(f"{n}  {p} 元\n" for n, p in rows), exact=True)
        sc.write(repo + "/schedule.txt", "# 日程\n" + "".join(s + "\n" for s in SCHEDULE), exact=True)
        sc.git_commit(repo, "写上费用和日程")
        item, old = rows[0]
        new = old + sc.pick([5, 10, 15])
        lost = sc.pick(SCHEDULE[1:-1])
        sc.write(repo + "/prices.txt", "# 费用\n" + "".join(
            f"{n}  {new if n == item else p} 元\n" for n, p in rows), exact=True)
        sc.write(repo + "/schedule.txt", "# 日程\n" + "".join(s + "\n" for s in SCHEDULE if s != lost),
                 exact=True)
        sc.fact("wanted_file", "prices.txt")
        sc.fact("wanted_text", f"{item}  {new} 元")
        sc.fact("lost_file", "schedule.txt")
        sc.fact("lost_text", lost)
        sc.fact("item", item)
        sc.fact("price", new)
    sc.fact("repo", repo)
    sc.fact("commits", 1)


def grade_x1(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库 " + facts["repo"])
    if repo.commit_count() > facts["commits"]:
        ctx.ok("有新的提交")
    else:
        ctx.fail("还没有新的提交", where="考试仓库的提交历史", saw=f"还是 {repo.commit_count()} 个提交")
        ctx.stop()
    wanted = repo.file_at("HEAD", facts["wanted_file"]) or ""
    ctx.expect(facts["wanted_text"] in wanted, "要提交的那处改动已经在最新的提交里",
               "题目要求提交的那处改动要进最新的提交", where="最新提交里的文件",
               saw="没有找到题目说的新内容")
    kept = repo.file_at("HEAD", facts["lost_file"]) or ""
    ctx.expect(facts["lost_text"] in kept, "被误删的那一行没有跟着进提交",
               "被误删的那一行要留在最新的提交里：最新的提交只能带上题目要提交的那处改动",
               where="最新提交里的文件", saw="有一行内容在提交里不见了")


def build_x2(sc):
    """A history in which one commit removed (A) or added (B) a given line.

    Every commit after the first has the same message, so the only way to
    find the right one is to look at the changes (git show / git log --stat).
    """
    repo = "plan-" + sc.word()
    sc.git_init(repo)
    lines = ["买菜", "洗衣服", "去银行", "给花浇水", "交电费", "取快递", "修自行车"]
    todo = sc.sample(lines, 5)
    current = todo[:3]
    sc.write(repo + "/todo.txt", "".join(t + "\n" for t in current), exact=True)
    sc.git_commit(repo, "写下这周要做的事", date=sc.ago(days=6))
    target_at = sc.randint(1, 3)
    full = ""
    if sc.form == "A":
        gone = current[1]
        for step in range(1, 5):
            if step == target_at:
                current = [t for t in current if t != gone]
                message = "更新清单"
            else:
                current = current + [todo[3 + (step % 2)] + f"（第 {step} 次补充）"]
                message = "更新清单"
            sc.write(repo + "/todo.txt", "".join(t + "\n" for t in current), exact=True)
            sc.git_commit(repo, message, date=sc.ago(days=6 - step))
            if step == target_at:
                full = sc.git(repo, "rev-parse", "HEAD").strip()
        sc.fact("line", gone)
    else:
        new = todo[3]
        for step in range(1, 5):
            if step == target_at:
                current = current + [new]
                message = "更新清单"
            else:
                current = current + [todo[4] + f"（第 {step} 次补充）"]
                message = "更新清单"
            sc.write(repo + "/todo.txt", "".join(t + "\n" for t in current), exact=True)
            sc.git_commit(repo, message, date=sc.ago(days=6 - step))
            if step == target_at:
                full = sc.git(repo, "rev-parse", "HEAD").strip()
        sc.fact("line", new)
    sc.fact("repo", repo)
    sc.fact("file", "todo.txt")
    sc.fact("commit", full)


HASH_WORD = re.compile(r"(?<![0-9a-z])[0-9a-f]{7,40}(?![0-9a-z])")


def grade_x2(ctx):
    info = ctx.scenario()
    facts = info.facts
    repo = ctx.need_repo(info.path / facts["repo"], "考试仓库 " + facts["repo"])
    if repo.commit(facts["commit"]) is None:
        raise RuntimeError("the commit recorded by the builder is missing")
    full = facts["commit"]

    def right_hash(typed):
        # every hex word of 7 to 40 characters counts, wherever it stands: "7ff39e6",
        # "commit 7ff39e66…" (git show / git log), "7ff39e6 更新清单" (git log --oneline),
        # "编号是7ff39e6"; one that is not a prefix of the target names another commit
        words = HASH_WORD.findall(typed)
        return bool(words) and all(full.startswith(w) for w in words)

    ctx.ask("那个提交的编号是什么？写前 7 位就够。", right_hash)


EXAM = [
    {
        "id": "1.7-x1",
        "gate": "gate-b",
        "title": "先看清改动，只提交该提交的",
        "minutes": 6,
        "build": build_x1,
        "task": {
            "A": "仓库 {dir}/{repo} 里有两处还没提交的改动：一处是把网页标题改成「{title}」，这是要提交的；"
                 "另一处是不小心删掉了一行，那处改动不能进提交。只把标题这处改动提交上去。",
            "B": "进入 {dir}/{repo}：{item}的价格已经改成 {price} 元，这处改动要提交；"
                 "还有一个文件被误删了一行，那处改动不能提交。做完以后，最新的提交里只能有改价格这一处。",
        },
        "grade": grade_x1,
    },
    {
        "id": "1.7-x2",
        "gate": "gate-b",
        "title": "在历史里找到某一行改动的那个提交",
        "minutes": 5,
        "build": build_x2,
        "task": {
            "A": "仓库 {dir}/{repo} 的历史里，有一个提交把 {file} 里写着「{line}」的那一行删掉了。"
                 "找到这个提交，运行评分时回答它的编号（前 7 位）。",
            "B": "仓库 {dir}/{repo} 的历史里，有一个提交往 {file} 里加上了「{line}」这一行。"
                 "找到这个提交，运行评分时回答它的编号（前 7 位）。",
        },
        "grade": grade_x2,
    },
]
