"""Lesson 0.4 像管项目一样管学习 (plan section 4).

Station a: the definition of done, applied to the board (PROGRESS.md) and to
           a fictional learner's board in the playground.
Station b: a fixed weekly rhythm with a review slot, the return routine and
           the learner's own 累了协议, written into learner/profile.md.
Station c: an interim backup (a dated zip archive in ~/Documents), then the
           cold gate exam gate-0 as its own sitting behind a mid-station save
           point; check 0.4c needs the backup and a graded gate-0 sitting.

Standard library only, Python 3.9 syntax.  Reference: docs/authoring/tool-api.md.
"""

import datetime
import re
import zipfile

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "0.4",
    "slug": "04-manage-your-learning",
    "title": "像管项目一样管学习",
    "stage": 0,
    "prerequisites": ["0.3"],
    "stations": [
        {
            "id": "0.4a",
            "title": "任务、看板和完成的定义",
            "minutes": 30,
            "new_concept": "完成的定义：一件事做到哪几样看得见的结果才算完成",
            "new_commands": [
                "python3 tools/course.py status --write",
            ],
        },
        {
            "id": "0.4b",
            "title": "每周计划和复盘",
            "minutes": 30,
            "new_concept": "迭代：按固定的周期计划、去做、回头看，再调整",
            "new_commands": ["python3 tools/course.py review"],
        },
        {
            "id": "0.4c",
            "title": "安全网和小关卡",
            "minutes": 25,
            "new_concept": "备份：放在别处的第二份，并且确认过它是好的",
            "new_commands": [
                "zip -r -q",
                "zip -T",
                "python3 tools/course.py exam gate-0",
                "python3 tools/course.py exam gate-0 --grade",
                "python3 tools/course.py exam gate-0 --explain pass",
            ],
        },
    ],
    "rules": ["PM-01", "PM-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"macos": "27.2.1", "zsh": "5.9", "python3": "3.14.9", "zip": "3.0"},
    },
    "unverified_steps": [
        "0.4a：用 code PROGRESS.md 在 VS Code 里打开看板文件（图形界面，对照 VS Code 文档）",
        "0.4b：在 VS Code 里编辑 learner/profile.md，没保存的文件标签页上有一个圆点，按 ⌘S 保存（图形界面，对照 VS Code 文档）",
        "0.4b：导师听到“我回来了，带我走回归流程”后的回归流程（导师行为，按 docs/tutor/playbook.md §12，建课时无法验证）",
        "0.4b：导师听到“直接告诉我答案”后先问一句“是累了，还是卡住了？”（导师行为，按 docs/tutor/playbook.md §15，建课时无法验证）",
        "0.4c：第一次往「文稿」（Documents）文件夹里写文件时，macOS 可能弹窗询问权限（建课时无法验证）",
        "0.4c：导师按 gates/gate-0/rubric.md 问讲解题（导师行为，按 docs/tutor/playbook.md §4，建课时无法验证）",
    ],
    # Station 0.4c's minutes are the backup work and its check (plan G5a).
    # The cold exam gate-0 is its own sitting behind the mid-station save
    # point: one task per lesson 0.1-0.4 (about 19-23 minutes, printed by
    # exam) plus about 10 minutes for the explain-back part.  check 0.4c
    # needs a graded gate-0 sitting (plan section 4 puts the gate in 0.4c).
}

TERMS = [
    {"term": "任务", "en": "task",
     "plain": "小到一次能做完、做完能看出区别的一件事；在这门课里一站就是一个任务", "first": "0.4a"},
    {"term": "看板", "en": "Kanban board",
     "plain": "把每件事放进「待办、进行中、完成」几栏的一张表，一眼看出做到哪了", "first": "0.4a"},
    {"term": "完成的定义", "en": "Definition of Done, DoD",
     "plain": "事先写好的几条看得见的标准，全部满足才算完成", "first": "0.4a"},
    {"term": "在制品限制", "en": "WIP limit (work in progress)",
     "plain": "同时开着、还没做完的事最多几件；这门课是一次只开一课", "first": "0.4a"},
    {"term": "带扶手完成", "en": "finished with help",
     "plain": "看过提示的第 4 级（完整答案）以后才通过的一站；三到七天后要不看提示再做一遍", "first": "0.4b"},
    {"term": "迭代", "en": "iteration",
     "plain": "按固定周期重复的一轮：计划、去做、回头看、调整", "first": "0.4b"},
    {"term": "复盘", "en": "retrospective",
     "plain": "一轮结束后回头看：哪里顺、哪里卡、下一轮改一件什么", "first": "0.4b"},
    {"term": "备份", "en": "backup",
     "plain": "放在别处的第二份，原来那份坏了或丢了还能找回来", "first": "0.4c"},
    {"term": "压缩包", "en": "zip archive",
     "plain": "把一个文件夹连同里面的所有文件装进一个 .zip 文件", "first": "0.4c"},
    {"term": "关卡", "en": "gate",
     "plain": "学完几课后一次不给提示的小考，题目每次随机生成", "first": "0.4c"},
    {"term": "讲解题", "en": "explain-back question",
     "plain": "要你用自己的话讲清“为什么这样做，而不是那样做”的题，由导师问", "first": "0.4c"},
]


# ---------------------------------------------------------------------------
# Shared builder: a fictional learner's board with one false "完成"
# ---------------------------------------------------------------------------
NAMES = ["阿青", "小周", "阿木", "小禾", "阿远", "小舟", "阿北", "小林"]

COURSES = {
    "photo": ("一门摄影网课",
              ["认识相机", "拿稳相机", "对焦", "曝光", "光圈", "快门", "构图", "用光", "修图"],
              "课后小测"),
    "guitar": ("一门吉他自学课",
               ["认识吉他", "调音", "按弦", "C 和弦", "G 和弦", "扫弦", "节奏", "换和弦", "弹唱"],
               "练习录音打分"),
    "english": ("一门英语口语课",
                ["自我介绍", "问路", "点餐", "购物", "打电话", "看病", "订酒店", "面试", "闲聊"],
                "跟读打分"),
}

DOD_ITEMS = ("{quiz}通过：「{quiz}记录」里有这一课的「通过」",
             "要点写进笔记：「要点笔记」里有这一课",
             "写了日志：「日志」里有一行写到这一课")


def _day(sc, days):
    moment = sc.ago(days=days)
    return "{:02d}-{:02d}".format(moment.month, moment.day)


def _build_board(sc, rel, course_key):
    """Write a fictional learner's board to ``rel`` and record the facts.

    Three lessons sit in 完成; exactly one of them misses one item of the
    definition of done (seeded).  Another one failed its quiz once before it
    passed, so "还没通过" alone is not the answer.
    """
    who = sc.pick(NAMES)
    course, topics, quiz = COURSES[course_key]
    first = sc.randint(3, 5)
    numbers = [first + offset for offset in range(6)]       # done x3, doing, todo x2
    done, doing, todo = numbers[:3], numbers[3], numbers[4:]
    false = sc.pick(done)
    missing = sc.randint(1, 3)
    retried = sc.pick([n for n in done if n != false])
    title = {n: topics[n - first] for n in numbers}

    quiz_lines, note_lines, log_lines = [], [], []
    age = 20
    for n in done:
        age -= sc.randint(2, 3)
        day = _day(sc, age)
        if n == retried:
            quiz_lines.append(f"{_day(sc, age + 1)}  第 {n} 课  还没通过")
        if n == false and missing == 1:
            quiz_lines.append(f"{day}  第 {n} 课  还没通过")
        else:
            quiz_lines.append(f"{day}  第 {n} 课  通过")
        if not (n == false and missing == 2):
            note_lines.append(f"第 {n} 课 {title[n]}：" + sc.pick(
                ["先看清楚，再动手。", "慢一点反而快。", "每次只改一个地方。", "记下自己常犯的错。"]))
        if not (n == false and missing == 3):
            log_lines.append(f"{day}  学了第 {n} 课「{title[n]}」，" + sc.pick(
                ["有点难，但做完了。", "比想象的顺。", "中间卡了一会儿。"]))
    today = _day(sc, 1)
    log_lines.append(f"{today}  开始第 {doing} 课「{title[doing]}」，还没做完。")
    quiz_lines.append(f"{today}  第 {doing} 课  还没通过")

    dod = [item.format(quiz=quiz) for item in DOD_ITEMS]
    text = "\n".join(
        [f"{who}的学习看板（{who}在学{course}）", "",
         "完成的定义（每一课三条都满足，才算完成）：",
         f"  1. {dod[0]}", f"  2. {dod[1]}", f"  3. {dod[2]}", "",
         "【待办】"] + [f"  第 {n} 课 {title[n]}" for n in todo] +
        ["【进行中】", f"  第 {doing} 课 {title[doing]}",
         "【完成】"] + [f"  第 {n} 课 {title[n]}" for n in done] +
        ["", f"---- {quiz}记录 ----"] + quiz_lines +
        ["", "---- 要点笔记 ----"] + note_lines +
        ["", "---- 日志 ----"] + log_lines) + "\n"
    sc.write(rel, text, exact=True)
    sc.fact("who", who)
    sc.fact("board", rel)
    sc.fact("false_lesson", false)
    sc.fact("false_topic", title[false])
    sc.fact("other_topics", [title[n] for n in numbers if n != false])
    sc.fact("missing_item", missing)
    sc.fact("doing", doing)
    sc.fact("next_todo", todo[0])


PROFILE_SAMPLE = """
    # {who}的学习档案（示例，不是你的）

    ## 每周学习时间

    - 周二 20:30-21:15 学一站
    - 周四 20:30-21:15 学一站
    - 周六 09:00-10:00 学两站
    - 周日 21:00-21:15 复盘：先 review，再 status --write 刷新看板，然后回答每周复盘的三个问题

    ## 累了协议

    1. 有点累、还想学：换轻的，做 10 分钟复习，不开新的一站。
    2. 很累：存档收工，写一句日志就停。
    3. 卡住了又很累：看示范，或者直接要答案，过几天不看提示再重做一遍。
"""


def build_start(sc):
    """Just before 0.4: a fictional learner's study folder in the playground.

    The learner's own files (learner/profile.md, notes/, journal/) live in the
    workspace and are never written by a builder.  This folder is what the
    lesson practises on: the board for 0.4a, a sample profile in 0.4b, a
    folder to back up for practice in 0.4c.

    The third todo line contains "cd " on purpose and names no path: the tool
    then leaves out its own 「进入练习场景：cd …」 step (stations a and b are
    done from the workspace) and prints only its way back to the workspace.
    """
    folder = "study-" + sc.word()
    _build_board(sc, folder + "/board.txt", "photo")
    sc.write(folder + "/profile.md", PROFILE_SAMPLE.format(who=sc.facts["who"]))
    sc.write(folder + "/notes.txt", """
        这个文件夹是练习用的示例：一位虚构的同学的学习记录。
        改坏了没关系，可以用 --reset 重新搭一份。
    """)
    sc.fact("folder", folder)
    sc.fact("files", ["board.txt", "profile.md", "notes.txt"])
    sc.fact("target", ".")
    sc.todo("{}的学习文件夹：{}".format(sc.facts["who"], sc.show(folder)))
    sc.todo("看板在：" + sc.show(folder + "/board.txt"))
    sc.todo("第 1、2 站不用 cd 进这个文件夹，留在学习工作区照课文做就行")


# ---------------------------------------------------------------------------
# Station a: judging "done" by evidence
# ---------------------------------------------------------------------------
def _need_progress(ctx):
    if ctx.is_file("PROGRESS.md"):
        ctx.ok("学习工作区里有看板文件 PROGRESS.md")
    else:
        ctx.fail("看板文件 PROGRESS.md 还没有生成", where="学习工作区的最上层文件夹",
                 saw="没有 PROGRESS.md")


def _number_answer(ctx, number, words=(), others=()):
    """An expected-function for ctx.ask: the answer names ``number``.

    The number is read with ctx.parse_int (7, ７, 七, 第七课, 缺第二条).  An
    answer that gives both answers at once (「第5课，缺第2条」) is read by
    its first part.  An answer without a number counts when it names one of
    ``words`` (the lesson's topic, or the item's key word) and none of
    ``others``.
    """
    def match(typed):
        value = ctx.parse_int(typed)
        if value is None:
            head = re.split(r"[,，;；。]", typed, maxsplit=1)[0]
            if head != typed:
                value = ctx.parse_int(head)
        if value is not None:
            return value == number
        if any(word and word.lower() in typed for word in others):
            return False
        return any(word and word.lower() in typed for word in words)
    return match


ITEM_WORDS = {1: ("小测", "打分", "通过"), 2: ("笔记",), 3: ("日志",)}


def _judge_board(ctx, info):
    """Ask what only reading the board yields (shared by 0.4a and the exam)."""
    who = info.facts["who"]
    false = info.facts["false_lesson"]
    topic = info.facts.get("false_topic", "")
    other_topics = info.facts.get("other_topics", [])
    if not ctx.ask(f"{who}的「完成」栏里有一课其实还没完成。是第几课？（填课号）",
                   expected=_number_answer(ctx, false, (topic,), other_topics)):
        ctx.stop()
    missing = info.facts["missing_item"]
    other_words = [word for item, words in ITEM_WORDS.items() if item != missing for word in words]
    ctx.ask("那一课缺的是完成的定义里的第几条？（填 1、2 或 3）",
            expected=_number_answer(ctx, missing, ITEM_WORDS[missing], other_words))


def check_a(ctx):
    _need_progress(ctx)
    if ctx.failed:
        ctx.stop()
    info = ctx.scenario("start")
    if not ctx.is_file(info.path / info.facts["board"]):
        ctx.fail("练习用的看板文件不见了", where=ctx.show(info.path / info.facts["board"]),
                 saw="没有这个文件（重搭一份：python3 tools/course.py scenario 0.4 --reset）")
        ctx.stop()
    _judge_board(ctx, info)
    if ctx.failed:
        ctx.stop()
    who = info.facts["who"]
    ctx.quiz(
        f"{who}打算今天开始第 {info.facts['next_todo']} 课。按「一次只开一课」和完成的定义，"
        "今天先做哪件事最合适？",
        [f"直接开始第 {info.facts['next_todo']} 课，学新的更有劲",
         f"先把「完成」栏里那一课缺的补上，再把第 {info.facts['doing']} 课做完",
         f"把第 {info.facts['doing']} 课挪回「待办」，腾出位置开始新的一课"],
        "B",
        explain="先完成，再开始：没做完的事越多，越难知道自己到底会了什么。",
        feedback={
            "A": "这样「进行中」就同时开着两课，还留着一个假的「完成」。",
            "C": "挪回待办只是换了个地方放，做了一半的东西还在那里。",
        },
    )


# ---------------------------------------------------------------------------
# Station b: the profile (schedule with a review slot, 累了协议)
# ---------------------------------------------------------------------------
# A heading as CommonMark reads it: 1-6 '#' followed by a space or a tab
# (or nothing).  「##每周学习时间」 is not a heading; it is reported apart.
HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?[ \t]*$")
NEAR_HEADING = re.compile(r"^\s{0,3}#{1,6}[^# \t]")
DAY = re.compile(r"(周|星期|礼拜)[一二三四五六日天1-7]|每天|天天|工作日|周末|"
                 r"\b(mon|tue|wed|thu|fri|sat|sun)[a-z]*\b")
EXTRA_DAY = re.compile(r"(周|星期|礼拜)[一二三四五六日天1-7]((\s*[、，,和/]\s*[一二三四五六日天1-7])+)")
CLOCK = re.compile(r"\d{1,2}\s*[:点]\s*\d{0,2}|[零一二三四五六七八九十]{1,3}\s*点|\d{1,2}\s*(am|pm)")
PLACEHOLDER = re.compile(r"_{2,}|＿{2,}|<!--|^[>\-*+\d.、)）\s]*$")
REVIEW_WORDS = ("复盘", "回顾", "review")
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.、)）]|[（(]\d+[)）]|[一二三四五六七八九十]+、)\s*")
# Between the situation and what to do: a colon, an arrow, a comma, a dash,
# a space, or the words 就 / 的话 / 时 between two parts.
# The separator row under a Markdown table's header: | --- | :---: |
TABLE_RULE = re.compile(r"^\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?$")
TWO_PARTS = re.compile(r"\S\s*(?:[：:→,，;；]|->|=>|—+|－|\s|就|的话|时候?)\s*\S")


def _title(text):
    """A heading's text without bold marks or a number in front (「1. 」「一、」)."""
    title = (text or "").replace("**", "").replace("__", "").strip()
    return re.sub(r"^(?:\d+[.、)）]|[一二三四五六七八九十]+、)\s*", "", title)


def _sections(text):
    """{heading text: [content lines]} for every Markdown heading."""
    result, current = {}, None
    for raw in text.splitlines():
        match = HEADING.match(raw)
        if match:
            current = _title(match.group(1))
            result.setdefault(current, [])
        elif current is not None:
            result[current].append(raw)
    return result


def _content(ctx, lines):
    """Lines the learner really wrote: no blanks, no placeholders, no quotes.

    In a Markdown table the header row (the row right above a |---| row)
    and the separator row itself are not entries.
    """
    kept = []
    cleaned = [ctx.normalize(raw, case=False) for raw in lines]
    for index, line in enumerate(cleaned):
        if not line or line.startswith(">") or PLACEHOLDER.search(line):
            continue
        if TABLE_RULE.match(line):
            continue
        following = cleaned[index + 1] if index + 1 < len(cleaned) else ""
        if "|" in line and TABLE_RULE.match(following):
            continue
        kept.append(line)
    return kept


def _sittings(line):
    low = line.lower()
    if "每天" in low or "天天" in low:
        return 7
    count = 0
    if "工作日" in low:
        count += 5
    if "周末" in low:
        count += 2
    for match in DAY.finditer(low):
        if match.group(0) not in ("每天", "天天", "工作日", "周末"):
            count += 1
    for match in EXTRA_DAY.finditer(low):
        count += len(re.findall(r"[一二三四五六日天1-7]", match.group(2)))
    return count


def _candidates(sections, exact, words):
    """Matching sections: the exact heading first, then the others, last one first.

    The 0.1 questionnaire's heading is 「每周时间与固定时段」, which contains
    none of the words; a heading the learner wrote such as 「学习时间」 still
    counts, and the exact one the lesson asks for wins.
    """
    found = [(h, lines) for h, lines in sections.items() if any(word in h for word in words)]
    first = [item for item in found if item[0] == exact]
    rest = [item for item in reversed(found) if item[0] != exact]
    return first + rest


def _is_review(row):
    return any(word in row.lower() for word in REVIEW_WORDS)


def _judge_schedule(ctx, where, heading, lines):
    """Results for one schedule section: a list of ('ok'|'note'|'fail', ...) tuples."""
    out = []
    shown = where + " 的「" + heading + "」"
    rows = _content(ctx, lines)
    timed = [row for row in rows if _sittings(row) and CLOCK.search(row.lower())]
    if not timed:
        out.append(("fail", "「每周学习时间」下面还没有写明星期几、几点", shown,
                    "写了 {} 行，没有一行同时有星期和钟点".format(len(rows))))
        return out
    study = [row for row in timed if not _is_review(row)]
    review = [row for row in timed if _is_review(row)]
    if not study:
        out.append(("fail", "时间表里除了复盘，还没有写明星期和钟点的学习时段", shown,
                    "有星期和钟点的行只有复盘（{} 行）".format(len(timed))))
        return out
    total = sum(_sittings(row) for row in timed)
    out.append(("ok", "时间表写明了星期和钟点：每周约 {} 次".format(total)))
    if total < 3:
        out.append(("note", "课程建议每周至少三次，十分钟的复习也算一次。少于三次也可以，这是你的选择。"))
    if review:
        out.append(("ok", "时间表里有固定的复盘时段"))
    else:
        out.append(("fail", "时间表里还没有固定的复盘时段", shown,
                    "写了星期和钟点的 {} 行里都没有「复盘」两个字".format(len(timed))))
    return out


def _two_parts(row):
    return bool(TWO_PARTS.search(LIST_MARK.sub("", row, count=1).strip()))


def _judge_tired(ctx, where, heading, lines):
    rows = _content(ctx, lines)
    shown = where + " 的「" + heading + "」"
    if len(rows) < 3:
        return [("fail", "累了协议还要再写 {} 条（一共三条）".format(3 - len(rows)), shown,
                 "现在有 {} 条".format(len(rows)))]
    whole = [row for row in rows if _two_parts(row)]
    if len(whole) >= 3:
        return [("ok", "累了协议写了 {} 条，每条都有情况和做法".format(len(rows))
                 if len(whole) == len(rows) else
                 "累了协议里有 {} 条写清了情况和做法".format(len(whole)))]
    single = [row for row in rows if not _two_parts(row)]
    return [("fail", "累了协议每条要写成「什么情况：怎么办」两部分", shown,
             "写了 {} 条，看得出两部分的有 {} 条；比如「{}」只有一部分".format(
                 len(rows), len(whole), ctx.visible(single[0][:20])))]


def _record(ctx, results):
    for item in results:
        if item[0] == "ok":
            ctx.ok(item[1])
        elif item[0] == "note":
            ctx.note(item[1])
        else:
            ctx.fail(item[1], where=item[2], saw=item[3])


def _section(ctx, text, sections, exact, words, judge, label):
    """Grade the best matching section, or say why none was found."""
    where = "learner/profile.md"
    candidates = _candidates(sections, exact, words)
    if not candidates:
        lines = [line.strip() for line in text.splitlines() if any(word in line for word in words)]
        wide = [line for line in lines if line.startswith("＃")]
        near = [line for line in lines if NEAR_HEADING.match(line)]
        if wide:
            ctx.fail("标题前的 # 要用半角（切换到英文输入法再敲）", where=where,
                     saw="「{}」开头是全角的 ＃".format(ctx.visible(wide[0][:20])))
        elif near:
            ctx.fail("标题行的 ## 后面要空一个半角空格，不然它不算标题", where=where,
                     saw="「{}」".format(ctx.visible(near[0][:20])))
        else:
            saw = "没有找到含「{}」的标题".format(label)
            if label == "学习时间" and any("每周时间" in h for h in sections):
                saw += "（「每周时间与固定时段」是第 0.1 课问卷的一节，不算）"
            ctx.fail("profile.md 里还没有「{}」这一节".format(exact), where=where, saw=saw)
        return
    judged = [judge(ctx, where, heading, lines) for heading, lines in candidates]
    for results in judged:
        if not any(item[0] == "fail" for item in results):
            _record(ctx, results)
            return
    _record(ctx, judged[0])


def _check_profile(ctx):
    """The schedule and the 累了协议 in learner/profile.md."""
    where = "learner/profile.md"
    if not ctx.is_file(where):
        ctx.fail("还没有你的学习档案 learner/profile.md", where="学习工作区的 learner 文件夹",
                 saw="没有 profile.md")
        return
    text = ctx.read(where)
    sections = _sections(text)
    _section(ctx, text, sections, "每周学习时间", ("每周学习时间", "学习时间", "时间表"),
             _judge_schedule, "学习时间")
    _section(ctx, text, sections, "累了协议", ("累了",), _judge_tired, "累了")


def check_b(ctx):
    _check_profile(ctx)


# ---------------------------------------------------------------------------
# Station c: the interim backup and the gate result
# ---------------------------------------------------------------------------
DATE_IN_NAME = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
MARKER = "tools/course.py"          # every copy of the workspace holds it


def _zip_names(path):
    """Entry names of a zip file, or None when it is not a readable zip.

    Anything that keeps the archive from being read counts as damaged:
    a truncated file, a password (RuntimeError), a compression method Python
    does not know (NotImplementedError), a file the learner cannot read
    (OSError).  Only archives the lesson asked for are ever opened.
    """
    try:
        with zipfile.ZipFile(str(path)) as archive:
            names = archive.namelist()
            broken = archive.testzip()
    except Exception:
        return None
    if broken is not None:
        return None
    return names


def _name_date(name):
    """The first real date (YYYY-MM-DD) in a file name, or None."""
    for match in DATE_IN_NAME.finditer(name):
        try:
            return datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            continue
    return None


def _check_backup(ctx):
    documents = ctx.path("~/Documents")
    shown = ctx.show(documents)
    if not ctx.is_dir(documents):
        ctx.fail("没有找到「文稿」文件夹", where=shown, saw="这个文件夹不存在")
        return
    zips = [name for name in ctx.listdir(documents, hidden=False) if name.lower().endswith(".zip")]
    if not zips:
        ctx.fail("「文稿」里还没有 .zip 备份文件", where=shown, saw="没有以 .zip 结尾的文件")
        return
    # Only the learner's workspace backups are opened; other archives in
    # ~/Documents are private and are never read.  The lesson's name is
    # fullstack-from-zero-… (engineering-… before the course was renamed); a learner who stayed may have a real folder with
    # another name, reached through the entrance ~/Developer/fullstack-from-zero.
    stems = {"fullstack-from-zero", "engineering", ctx.workspace.name.lower()}
    ours = [name for name in zips if any(stem in name.lower() for stem in stems)]
    if not ours:
        ctx.fail("「文稿」里还没有名字里带 fullstack-from-zero 的备份", where=shown,
                 saw="有 {} 个别的 .zip 文件，名字里都没有 fullstack-from-zero".format(len(zips)))
        return
    good, damaged, other = [], [], []
    for name in ours:
        entries = _zip_names(documents / name)
        if entries is None:
            damaged.append(name)
        elif any(entry == MARKER or entry.endswith("/" + MARKER) for entry in entries):
            good.append((name, entries))
        else:
            other.append(name)
    if not good:
        if damaged:
            ctx.fail("找到的 zip 文件打不开，可能没写完或者坏了", where=shown, saw="、".join(damaged[:3]))
        else:
            ctx.fail("找到了 zip 文件，但里面没有学习工作区的内容", where=shown,
                     saw="、".join(other[:3]) + " 里都没有 " + MARKER)
        return
    dated = [(name, entries, _name_date(name)) for name, entries in good if _name_date(name)]
    if not dated:
        ctx.fail("备份文件名里还没有日期", where=shown,
                 saw="「{}」里没有 年-月-日 这样的日期".format(good[0][0]))
        return
    # The date in the name must be the day the archive was made (its file
    # date), so a block copied weeks later with an old date is caught.
    right = []
    for name, entries, day in dated:
        made = ctx.mtime(documents / name)
        if made is None or abs((made.date() - day).days) <= 1:
            right.append((name, entries))
    if not right:
        name, _entries, day = sorted(dated)[-1]
        made = ctx.mtime(documents / name)
        ctx.fail("备份文件名里的日期要写做备份那天的", where=ctx.show(documents / name),
                 saw="文件名写的是 {}，这个文件是 {} 做的".format(day.isoformat(), made.date().isoformat()))
        return
    name, entries = sorted(right)[-1]
    ctx.ok("「文稿」里有带日期的备份：" + name)
    tops = {stem + "/" for stem in stems}
    if any(entry.lower().startswith(top) for entry in entries for top in tops):
        ctx.ok("备份里是整个学习工作区文件夹，解开就是原来的样子")
    elif any("/" + top in "/" + entry.lower() for entry in entries for top in tops):
        # Made with a full path (zip … ~/Developer/fullstack-from-zero): the folder is
        # there, under the folders above it.
        ctx.note("备份里的学习工作区外面还套着一串上层文件夹（打包时写了完整路径）；能用，"
                 "解开时会多出这几层。下次站在 ~/Developer 里只写 fullstack-from-zero，就没有这几层了。")
    else:
        ctx.note("备份里的文件没有装在一个 fullstack-from-zero 文件夹里；能用，但解开时会散在当前位置。")


def _check_gate(ctx):
    gate = ctx.gate_result("gate-0")
    graded = bool(gate.passed) or bool(gate.open)
    if graded:
        done = len(gate.lessons) - len(gate.open_lessons)
        ctx.ok("小关卡 gate-0 批改过了：实操题 {}/{} 课有题通过".format(done, len(gate.lessons)))
    elif gate.in_progress:
        ctx.fail("小关卡 gate-0 这一场还没有批改", where="学习记录里 gate-0 的成绩",
                 saw="开考了，还没有批改过：python3 tools/course.py exam gate-0 --grade")
    else:
        ctx.fail("小关卡 gate-0 还没有成绩", where="学习记录里 gate-0 的成绩",
                 saw="还没有开考过 gate-0")


def check_c(ctx):
    _check_backup(ctx)
    _check_gate(ctx)


checks = {"0.4a": check_a, "0.4b": check_b, "0.4c": check_c}


# ---------------------------------------------------------------------------
# HINTS: 方向 → 位置 → 相似例子 → 答案与解释
# ---------------------------------------------------------------------------
HINTS = {
    "0.4a": [
        "完成的定义有三条，三条都满足才算完成。把「完成」栏里的每一课拿出来，三条逐一对一遍，不要只看它放在哪一栏。",
        "看板文件下面有三段记录：小测（或打分）记录、要点笔记、日志。对每一课，在三段里各找一次这一课的课号。"
        "注意：一课可能先「还没通过」后来又「通过」，那算通过。",
        "相似的例子：完成的定义是「作业写完、签了字、交给了老师」。小明的作业写完也签了字，但还在书包里，"
        "那它就没完成，缺的是第 3 条。",
        "答案：每个人的看板是随机生成的，所以这里给的是一步一步的做法。"
        "第一步，抄下「完成」栏的三个课号。第二步，在「记录」那一段里找每个课号的最后一行：只有「还没通过」的那一课缺第 1 条。"
        "第三步，在「要点笔记」里找三个课号：缺了的那一课缺第 2 条。第四步，在「日志」里找：缺了的那一课缺第 3 条。"
        "第二到第四步里只有一处对不上：那一课的课号是第一题的答案，对不上的那一段对应的条目编号是第二题的答案。"
        "第三题选 B：先把那一课补齐，再做完进行中的课，最后才开新的。"
        "解释：完成的定义让「做完了」变成可以核对的事实；一次只开一课，是为了先把手上的做完。"
        "如果检查说还没有看板，先运行 python3 tools/course.py status --write。",
    ],
    "0.4b": [
        "检查要在 learner/profile.md 里找到两节：一节写每周哪天几点学，其中有一行是复盘；一节写累了怎么办，至少三条，每条两部分。",
        "用 code learner/profile.md 打开你的档案，翻到最后。每一节用一行以 ## 开头、## 后面空一格的标题起头，"
        "例如「## 每周学习时间」和「## 累了协议」。第 0.1 课问卷里的「每周时间与固定时段」留着不动。写完一定要按 ⌘S 保存，再运行检查。",
        "相似的例子：练习场里那位同学的 profile.md。示范里写的是「- 周二 20:30-21:15 学一站」这种一行一个时段，"
        "最后一行是「- 周日 21:00-21:15 复盘：……」；累了协议每条是「很累：存档收工」这样，冒号前是情况，后面是做法。",
        "答案：在 learner/profile.md 末尾加上——\n"
        "## 每周学习时间\n- 周一 20:00-20:45 学一站\n- 周三 20:00-20:45 学一站\n"
        "- 周六 10:00-11:00 学两站\n- 周日 20:00-20:15 复盘\n\n"
        "## 累了协议\n1. 有点累：换轻的，只做复习。\n2. 很累：存档收工，写一句日志。\n"
        "3. 卡住又累：看示范，或者要答案，过几天重做。\n"
        "（日子和钟点换成你真能做到的。）按 ⌘S 保存后运行 python3 tools/course.py check 0.4b。"
        "解释：时段写死，才能按时开始，也才能在复盘时看出计划和实际差多少；累了协议是你清醒时替累的自己做的决定。",
    ],
    "0.4c": [
        "这一站的检查看两样东西：「文稿」里带日期的学习工作区备份，和 gate-0 有没有批改过一场。先看检查结果里「还缺什么」是哪一样。"
        "备份的做法和「跟我做」的练习一样：站在上一层，打包，再确认。",
        "位置：打包时站在 ~/Developer（学习工作区 fullstack-from-zero 的上一层）；要装进去的文件夹叫 fullstack-from-zero；"
        "压缩包放在「文稿」里，名字是 fullstack-from-zero-年-月-日.zip。gate-0 的成绩：先运行 python3 tools/course.py exam gate-0 开考，"
        "做完题回到学习工作区运行 python3 tools/course.py exam gate-0 --grade 批改。",
        "相似的例子：练习时你站在 ~/Developer/playground/0.4-start 里运行 zip -r -q study-年-月-日.zip study-…，"
        "压缩包就落在当前文件夹。把压缩包的名字前面加上一个文件夹的路径，比如 ~/Desktop/study-年-月-日.zip，"
        "它就会落到那个文件夹里；zip -T 后面也写同一个完整路径。",
        "答案（年-月-日换成今天的日期，比如 2026-11-20）：\n"
        "cd ~/Developer\nzip -r -q ~/Documents/fullstack-from-zero-年-月-日.zip fullstack-from-zero\n"
        "zip -T ~/Documents/fullstack-from-zero-年-月-日.zip\ncd ~/Developer/fullstack-from-zero\n"
        "然后 python3 tools/course.py exam gate-0，做完题目后 python3 tools/course.py exam gate-0 --grade，"
        "最后 python3 tools/course.py check 0.4c。"
        "解释：备份要在别处，而且要确认能打开；站在上一层打包，压缩包里才是一个完整的 fullstack-from-zero 文件夹。",
    ],
}


# ---------------------------------------------------------------------------
# Backups: the exam task (gate-0) and the review item
# ---------------------------------------------------------------------------
FOLDER_KINDS = {
    "A": ("recipes", ["noodles.txt", "dumplings.txt", "soup.txt"], "菜谱"),
    "B": ("photos", ["trip-list.txt", "camera-notes.txt", "albums.txt"], "相册清单"),
}


def _build_backup(sc, form):
    kind, files, label = FOLDER_KINDS[form]
    folder = kind + "-" + sc.word()
    for name in files:
        sc.write(folder + "/" + name, "{}：{}\n第 {} 页\n".format(label, name, sc.randint(1, 99)),
                 exact=True)
    sc.fact("folder", folder)
    sc.fact("files", files)
    if form == "B":
        sc.mkdir("backup")
        sc.fact("target", "backup")
    else:
        sc.fact("target", ".")


def _dates_ok(ctx, name):
    today = ctx.now.date()
    for match in DATE_IN_NAME.finditer(name):
        try:
            day = datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            continue
        if 0 <= (today - day).days <= 1:
            return True
    return False


def _grade_backup(ctx, info, strict_name):
    folder = info.facts["folder"]
    source = info.path / folder
    target = info.path / info.facts["target"]
    for name in info.facts["files"]:
        if not ctx.is_file(source / name):
            ctx.fail("原来的文件夹被改动了：备份不能动原件", where=ctx.show(source),
                     saw="少了 " + name)
            return
    zips = [name for name in ctx.listdir(target, hidden=False) if name.lower().endswith(".zip")]
    if not zips:
        ctx.fail("还没有 zip 备份文件", where=ctx.show(target), saw="没有以 .zip 结尾的文件")
        return
    best = None
    for name in sorted(zips):
        entries = _zip_names(target / name)
        if entries is None:
            continue
        stripped = {entry[len(folder) + 1:] if entry.startswith(folder + "/") else entry
                    for entry in entries}
        if all(item in stripped for item in info.facts["files"]):
            best = (name, entries)
    if best is None:
        ctx.fail("zip 文件里没有那个文件夹的全部文件，或者打不开", where=ctx.show(target),
                 saw="、".join(zips[:3]))
        return
    name, entries = best
    ctx.ok("备份 {} 里有那个文件夹的全部文件".format(name))
    if _dates_ok(ctx, name):
        ctx.ok("文件名里带着今天的日期")
    else:
        ctx.fail("备份文件名里还没有今天的日期", where=ctx.show(target / name),
                 saw="文件名是「{}」".format(name))
    if strict_name and not re.match(r"^[a-z0-9-]+\.zip$", name):
        ctx.fail("文件名要只用小写英文、数字和短横线", where=ctx.show(target / name),
                 saw="文件名是「{}」".format(name))


def _backup_review_check(ctx):
    info = ctx.scenario("start")
    _grade_backup(ctx, info, strict_name=False)


def build_x1(sc):
    _build_backup(sc, sc.form)


def grade_x1(ctx):
    info = ctx.scenario()
    _grade_backup(ctx, info, strict_name=True)


def build_x2(sc):
    _build_board(sc, "board.txt", "guitar" if sc.form == "A" else "english")


def grade_x2(ctx):
    info = ctx.scenario()
    if not ctx.is_file(info.path / "board.txt"):
        ctx.fail("看板文件不见了", where=ctx.show(info.path), saw="没有 board.txt")
        ctx.stop()
    _judge_board(ctx, info)


SCENARIOS = {"start": build_start}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "0.4-done", "type": "recall", "tier": "fluent", "station": "0.4a", "rule": "PM-01",
     "q": "「完成的定义」是什么意思？这门课里，一课满足哪几条才算完成？",
     "a": "事先写好、看得见的几条标准，全部满足才算完成。这门课一课的完成的定义就是它收尾里的几步："
          "全课检查通过；在 notes/my-rules.md 里每条新行规的小标题下面用自己的话写一两句，再配一个例子；写一句日志。"
          "没有新行规的课没有第二条；从第 1.12 课起再加一条：备份。"},
    {"id": "0.4-wip", "type": "which", "tier": "fluent", "station": "0.4a",
     "q": "看板上「进行中」还有一课没做完，你很想开始新的一课。按「一次只开一课」，该怎么做？",
     "options": ["先把进行中的那一课做完，再开始新的",
                 "两课一起开着，哪课有劲做哪课",
                 "把没做完的那课挪回「待办」，再开始新的"],
     "answer": "A", "shuffle": True,
     "explain": "限制同时进行的事，是为了先把手上的做完；挪回待办只是换个地方放半成品。"},
    {"id": "0.4-fixed", "type": "fault", "tier": "fluent", "station": "0.4b", "rule": "PM-02",
     "q": "下面这份每周计划，最大的问题是什么？\n\n    - 有空就学\n    - 周末看情况多学一点\n    - 学完一阶段再总结",
     "options": ["没有固定的日子和钟点，也没有固定的复盘时段",
                 "一周学得太少，至少要每天学",
                 "总结应该放在每天睡前"],
     "answer": "A", "shuffle": True,
     "explain": "迭代靠固定周期：哪天几点学、哪天几点复盘都写死，才能按时开始，也才能比较计划和实际。"},
    {"id": "0.4-return", "type": "recall", "tier": "lookup", "station": "0.4b",
     "q": "隔了两个多星期没学，回来第一次坐下，先做什么？",
     "a": "运行 python3 tools/course.py status 看停在哪；对导师说“我回来了，带我走回归流程”。"
          "不用一口气补完积压的复习，先做一点轻松的，再重新排这一周。"},
    {"id": "0.4-backup", "type": "recall", "tier": "fluent", "station": "0.4c",
     "q": "什么才算备份？为什么一个会自动同步的网盘文件夹本身不算备份？",
     "a": "备份是放在别处的第二份，并且确认过它能打开。同步会把删除和改坏也一起同步过去，"
          "所以要有一份独立的、带日期的副本。"},
    {"id": "0.4-zip", "type": "do", "tier": "lookup", "station": "0.4c",
     "q": "练习场里有一位同学的学习文件夹（study- 开头）。在它旁边（同一层）给它做一个文件名带今天日期的 zip 备份，并确认它没有损坏。",
     "scenario": "start", "check": _backup_review_check},
]


# ---------------------------------------------------------------------------
# EXAM (gate-0)
# ---------------------------------------------------------------------------
EXAM = [
    {
        "id": "0.4-x1",
        "gate": "gate-0",
        "title": "给一个文件夹做带日期的备份",
        "minutes": 6,
        "build": build_x1,
        "task": {
            "A": "在 {dir} 里有一个文件夹 {folder}。给它做一个 zip 备份，放在 {dir} 里；"
                 "文件名只用小写英文、数字和短横线，并且带上今天的日期（年-月-日）。原来的文件夹不要动。"
                 "做完确认这个备份没有损坏。",
            "B": "把 {dir}/{folder} 这个文件夹打包成一个 zip 文件，放进 {dir}/{target} 里。"
                 "文件名里要有今天的日期（年-月-日），并且只用小写英文、数字和短横线。"
                 "原件保持原样，并确认压缩包是完好的。",
        },
        "grade": grade_x1,
    },
    {
        "id": "0.4-x2",
        "gate": "gate-0",
        "title": "按完成的定义核对一张看板",
        "minutes": 6,
        "build": build_x2,
        "task": {
            "A": "{dir}/board.txt 是{who}学吉他的看板。按看板顶上写的完成的定义，核对「完成」栏里的每一课。"
                 "批改时会问你：哪一课其实没完成，缺的是第几条。",
            "B": "{who}在学英语口语，看板是 {dir}/board.txt。用文件里写明的三条完成标准，"
                 "找出被错放进「完成」的那一课和它缺的那一条；批改时要回答这两件事。",
        },
        "grade": grade_x2,
    },
]
