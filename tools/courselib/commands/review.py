"""``review``: spaced review of what the learner already passed (plan I4).

``review``            one session: due cold redos first, then due items
                      (at most 8 things, about 10 minutes), or the return
                      routine after a break of more than 10 days.
``review --grade``    grade the ``do`` task handed out earlier, with its check.
``review --give-up``  give that ``do`` task up (counts as 忘了, back tomorrow).

What is served and when is decided by ``courselib.review`` (plan, order,
return routine) and ``courselib.schedule`` (Leitner boxes).  This module only
asks, shows and records.  Every answer is saved at once (atomically, through
the store), so stopping with q, Ctrl+C or end-of-file loses nothing.

Answers come from the terminal or, in order, from ``--answer`` (needed with
COURSE_NONINTERACTIVE=1).  Prompts that only pause ("press Enter to see the
answer") are shown only to a person typing live; they never consume an
``--answer``.  Each graded question consumes exactly one.
"""

import hashlib
import random

from .. import cmdkit, progress, review, runner, schedule
from ..errors import (
    EXIT_NOT_YET,
    EXIT_OK,
    EXIT_PROBLEM,
    Cancelled,
    Refused,
    ToolTrouble,
    UsageProblem,
)
from ..normalize import (
    choice_letter,
    index_to_letter,
    letter_to_index,
    normalize,
    option_text_index,
    parse_int,
)
from ..ui import BAD_MARK, OK_MARK, WARN_MARK, indent, one_line

SUMMARY = "做到期的复习题（每次最多 8 道，约 10 分钟）"
DESCRIPTION = """复习你已经学过的内容。每一站第一次通过检查后，它的复习题会排进复习计划：
隔 2 天、1 周、3 周、2 个月、6 个月各出现一次。答对了，间隔变长；
答「模糊」，间隔不变；忘了，明天再来一次。在最长的间隔后还答对，这道题就毕业了。

一次最多做 8 道，大约 10 分钟。之前看过完整答案（带扶手完成）的站，
3 到 7 天后会排在最前面，提醒你不看提示重做一遍。
隔了 10 天以上再回来，只先做 4 道容易的题，其余的不急。

每道题都可以输入 s 跳过、q 结束；做完一道记一道，中途停下不会丢。

例子：
  python3 tools/course.py review              做今天到期的复习
  python3 tools/course.py review --grade      动手题做完以后，检查并记录结果
  python3 tools/course.py review --give-up    动手题做不出来：记为「忘了」，明天再来"""

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "answer_help": "提前给出回答；有几道题就写几次，按出题的顺序（回忆题写 1 记得、2 模糊、3 忘了）",
    "grade_help": "检查已经搭好练习场的动手题，并记录结果",
    "give_up_help": "放弃正在做的动手题：记为「忘了」，明天重新出现",
    "both_flags": "--grade 和 --give-up 不能一起用：要么检查动手题，要么放弃它。",
    "need_answer": (
        "现在是不提问模式（COURSE_NONINTERACTIVE=1），这道题需要一个回答。"
        "请用 --answer 按出题的顺序给出。"
    ),
    "head": "复习 · {date}",
    "nothing": "现在没有到期的复习题。",
    "nothing_next": "下一次有题到期：{date}。",
    "nothing_ever": "还没有排进复习计划的题。每一站第一次通过检查后，它的复习题会自动排进来。",
    "enrolled": "补排了 {n} 道复习题（它们是在你通过那一站之后才加进课程的），{date} 起出现。",
    "intro": "今天到期：{what}。这次做 {n} 道，大约 {minutes} 分钟。",
    "intro_due": "{n} 道复习题",
    "intro_redo": "{n} 站要重做",
    "intro_keys": "每道题都可以输入 s 跳过、q 结束；做完一道记一道，中途停下不会丢。",
    "backlog": "还有 {n} 条，不急，下次再说。",
    "return_line": "距离上次学习已经 {days} 天。这次只做 {n} 道容易的题，先找回手感。",
    "return_nothing": "距离上次学习已经 {days} 天。",
    "return_no_easy": "这次先不做题：到期的都是动手题，等找回手感再做。",
    "return_tutor": "想把落下的内容理一理，可以对导师说“我回来了，带我走回归流程”。",
    "pending": "还有一道动手题没交：{item}（练习场在 {path}）。做完运行 python3 tools/course.py review --grade；做不出来运行 python3 tools/course.py review --give-up。",
    "orphans_missing": "{mark} 有 {n} 道复习题找不到对应的课程或题目了（{ids}），这次跳过；记录还留着。把这句发给导师。",
    "orphans_broken": "{mark} 有 {n} 道复习题所在的课程模块加载失败（{ids}），这次跳过。把这句发给导师。",
    "item_head": "第 {n}/{total} 题 · {kind} · {source}",
    "kind_recall": "回忆",
    "kind_predict": "预测",
    "kind_which": "选择",
    "kind_fault": "找错",
    "kind_do": "动手",
    "kind_redo": "重做",
    "source": "{lesson} {title}",
    "recall_think": "先在心里（或纸上）答一遍。想好了按回车看参考答案（s 跳过，q 结束）：",
    "recall_answer": "参考答案：",
    "recall_grade": "你答得怎么样？1 记得，2 模糊，3 忘了（s 跳过，q 结束）：",
    "recall_retry": "请输入 1、2 或 3，也可以写「记得」「模糊」「忘了」。",
    "choice_prompt": "输入选项的字母（s 跳过，q 结束）：",
    "choice_retry": "请输入 {first} 到 {last} 中的一个字母。",
    "right": "答对了。",
    "wrong": "不对。正确答案是 {letter}：{option}",
    "explain": "解释：{text}",
    "unreadable": "看不懂回答「{answer}」，这道题先跳过，下次还会出现。",
    "skipped": "跳过了，这道题还在到期的列表里。",
    "next_right": "下次复习：{date}（隔 {days} 天）。",
    "next_fuzzy": "间隔不变，{date} 再来一次。",
    "next_wrong": "没关系，复习就是为了找出忘了的地方。明天（{date}）再来一次。",
    "retired": "在最长的间隔之后你还记得：这道题毕业了，以后不再出现。",
    "broken_item": "{mark} 这道题的写法有问题（{what}），先跳过，不算错。把题号 {id} 发给导师。",
    "broken_options": "选项或答案不对",
    "broken_answer": "缺少参考答案",
    "redo_body": (
        "你之前看过这一站的完整答案，它记为「带扶手完成」。"
        "现在不看提示，把课文 {path} 里第 {number} 站的「自己做」重新做一遍。"
    ),
    "redo_late": "建议的时间是 {after} 到 {before}。过了也没关系，现在做一样算数。",
    "redo_scenario": "需要重新搭这一站的练习场，可以运行：python3 tools/course.py scenario {id} --reset",
    "redo_how": "做完运行：python3 tools/course.py check {station}（通过后这一站改记为「通过」）",
    "redo_later": "重做不在这里计时，复习完再做就行。",
    "redo_next": "记下了就按回车，接着做复习题（q 结束）：",
    "do_start": "回车搭练习场，开始做（s 跳过，q 结束）：",
    "do_ready": "练习场搭好了：{path}",
    "do_todo": "做完运行：python3 tools/course.py review --grade",
    "do_give_up": "做不出来也没关系：运行 python3 tools/course.py review --give-up，这道题明天再来。",
    "do_unavailable": "{mark} 动手题暂时做不了：搭练习场的功能还没准备好。这道题先跳过，不算错。",
    "do_refused": "动手题的练习场搭不了，这道题先跳过，不算错：",
    "do_trouble": "动手题的练习场没搭起来。这道题先跳过，不算错。",
    "do_no_builder": "{mark} 这道动手题要的练习场（{key}）在课程里找不到。先跳过，不算错。把题号 {id} 发给导师。",
    "time_up": "已经大约 {minutes} 分钟了，今天的复习到这里。",
    "quit": "好，这次复习到这里。",
    "stopped": "复习停在这里。",
    "left_over": "剩下的 {n} 条下次再说。",
    "summary": "这次复习：{parts}。",
    "summary_none": "这次复习没有记录任何回答。",
    "part_right": "记得 {n} 道",
    "part_fuzzy": "模糊 {n} 道",
    "part_wrong": "忘了 {n} 道",
    "part_skip": "跳过 {n} 道",
    "part_retired": "其中 {n} 道毕业",
    "after_do": "动手题已经搭好，做完运行 python3 tools/course.py review --grade。",
    "after_redo": "别忘了重做：{stations}。做完各自运行 check。",
    "unused_answers": "多给了 {n} 个 --answer，没有用上。",
    # --grade / --give-up
    "no_pending": "现在没有等着检查的动手题。做今天的复习：python3 tools/course.py review",
    "grade_head": "动手题 {id} · {source}",
    "grade_gone": "这道动手题的练习场不见了（{path}）。这次不算，下次复习会重新搭一份。",
    "grade_right": "这道动手题记为「记得」。下次复习：{date}（隔 {days} 天）。",
    "grade_fuzzy": "试了不止一次才做对，记为「模糊」：间隔不变，{date} 再来一次。",
    "grade_retired": "这道动手题毕业了，以后不再出现。",
    "grade_not_yet": "改好后再运行 python3 tools/course.py review --grade；做不出来运行 python3 tools/course.py review --give-up。",
    "grade_problem": "这次检查不算，这道题还等着你交。",
    "gave_up": "动手题 {id} 记为「忘了」，明天（{date}）重新出现，到时会搭一份新的练习场。",
    "gave_up_folder": "旧的练习场留在 {path}，不需要了可以不管它，下次会被替换。",
}

KIND_KEYS = {"recall": "kind_recall", "predict": "kind_predict", "which": "kind_which",
             "fault": "kind_fault", "do": "kind_do"}

_RIGHT_WORDS = ("1", "记得", "记住了", "记得住", "会", "对", "答对了", "y", "yes", "right")
_FUZZY_WORDS = ("2", "模糊", "有点模糊", "半对", "一半", "不太确定", "maybe")
_WRONG_WORDS = ("3", "忘了", "忘记了", "不记得", "不会", "错", "答错了", "n", "no", "wrong")
_SKIP_WORDS = ("s", "skip", "跳过")
_QUIT_WORDS = ("q", "quit", "exit", "退出", "结束", "不做了")
#: What the session reads as a command at any question (after ``normalize``):
#: word -> what it does.  ``validate`` warns when an option's whole text is
#: one of these, because typing the option would end or skip instead.
RESERVED_WORDS = {word: "skip" for word in _SKIP_WORDS}
RESERVED_WORDS.update({word: "quit" for word in _QUIT_WORDS})

# outcomes of serving one thing
RIGHT, FUZZY, WRONG = schedule.RIGHT, schedule.FUZZY, schedule.WRONG
SKIP = "skip"
QUIT = "quit"
HANDED_OUT = "handed_out"     # a do task was built and is now with the learner
SHOWN = "shown"               # a redo task was shown
NOT_SERVED = "not_served"     # broken item or unavailable scenario: no grade


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "review", SUMMARY, description=DESCRIPTION)
    parser.add_argument("--answer", action="append", default=[], metavar="<回答>",
                        help=TEXT["answer_help"])
    parser.add_argument("--grade", action="store_true", help=TEXT["grade_help"])
    parser.add_argument("--give-up", action="store_true", dest="give_up",
                        help=TEXT["give_up_help"])


def run(args):
    app = args.app
    if args.grade and args.give_up:
        raise UsageProblem(TEXT["both_flags"])
    answers = Answers(app.console, [str(answer) for answer in args.answer])
    if args.grade:
        return _grade(app, answers)
    if args.give_up:
        return _give_up(app)
    return Session(app, answers).run()


# ---------------------------------------------------------------------------
# Answers: from --answer first, then from the terminal
# ---------------------------------------------------------------------------
class Answers:
    def __init__(self, console, given):
        self.console = console
        self.queue = list(given)

    @property
    def live(self):
        """True when the next answer would be typed by a person right now."""
        return not self.queue and self.console.can_prompt

    def take(self, prompt):
        """One graded answer: ``(text, scripted)``."""
        if self.queue:
            value = self.queue.pop(0)
            self.console.out(prompt + value)
            return value, True
        if not self.console.can_prompt:
            raise UsageProblem(TEXT["need_answer"])
        return self.console.read(prompt), False

    def pause(self, prompt):
        """A pause for a person at the keyboard; "" when answers are scripted."""
        if not self.live:
            return ""
        return self.console.read(prompt)


def _word(typed):
    """``skip`` / ``quit`` / None for what the learner typed."""
    text = normalize(typed)
    if text in _SKIP_WORDS:
        return SKIP
    if text in _QUIT_WORDS:
        return QUIT
    return None


def self_grade(typed):
    """``right`` / ``fuzzy`` / ``wrong`` / ``skip`` / ``quit`` or None (unreadable)."""
    text = normalize(typed)
    special = _word(text)
    if special:
        return special
    number = parse_int(text)
    if text in _RIGHT_WORDS or number == 1:
        return RIGHT
    if text in _FUZZY_WORDS or number == 2:
        return FUZZY
    if text in _WRONG_WORDS or number == 3:
        return WRONG
    return None


def _shuffled_order(item_id, count, today, shuffle):
    """Display order of the options (indices into the original list)."""
    order = list(range(count))
    if shuffle:
        digest = hashlib.sha256(f"{item_id}|{today.isoformat()}".encode())
        random.Random(int(digest.hexdigest()[:12], 16)).shuffle(order)
    return order


def _valid_choice(item):
    options = item.get("options")
    if not isinstance(options, (list, tuple)) or not 2 <= len(options) <= 6:
        return False
    if not all(isinstance(option, str) and option.strip() for option in options):
        return False
    index = letter_to_index(item.get("answer"))
    return index is not None and index < len(options)


# ---------------------------------------------------------------------------
# One review session
# ---------------------------------------------------------------------------
class Session:
    def __init__(self, app, answers):
        self.app = app
        self.out = app.console.out
        self.answers = answers
        self.state = None
        self.plan = None
        self.counts = {RIGHT: 0, FUZZY: 0, WRONG: 0, SKIP: 0, "retired": 0}
        self.handed_out = False
        self.redo_shown = []

    def run(self):
        app = self.app
        catalog = app.catalog()
        today = app.today
        self.state = state = app.store.load()
        away = progress.days_away(state, today)
        progress.touch_session(state, app.now)
        enrolled = review.sync_enrolment(state, catalog, today)
        self.plan = plan = review.make_plan(state, catalog, today, away)
        app.store.save(state, events=[{
            "type": "review-session", "return_routine": plan.return_routine,
            "days_away": away, "due": plan.due_total, "redo_due": plan.redo_total,
            "planned": [task["id"] for task in plan.redo] + [entry.id for entry in plan.items],
            "enrolled": enrolled, "orphans": plan.orphans.all()}])

        out = self.out
        out(TEXT["head"].format(date=today.isoformat()))
        out("")
        if plan.return_routine:
            if plan.items:
                out("  " + TEXT["return_line"].format(days=away, n=len(plan.items)))
            else:
                out("  " + TEXT["return_nothing"].format(days=away))
        self._notes(enrolled)
        if plan.size == 0:
            return self._nothing()
        if not plan.return_routine:
            what = []
            if plan.due_total:
                what.append(TEXT["intro_due"].format(n=plan.due_total))
            if plan.redo_total:
                what.append(TEXT["intro_redo"].format(n=plan.redo_total))
            out("  " + TEXT["intro"].format(what="、".join(what), n=plan.size,
                                            minutes=max(1, round(plan.minutes))))
        if plan.backlog:
            out("  " + TEXT["backlog"].format(n=plan.backlog))
        out("  " + TEXT["intro_keys"])

        served = 0
        stop = None
        start = review.clock()
        things = [("redo", task) for task in plan.redo] + [("item", entry) for entry in plan.items]
        try:
            for number, (kind, thing) in enumerate(things, 1):
                if served and review.clock() - start >= review.SESSION_MINUTES * 60:
                    stop = "time"
                    break
                out("")
                if kind == "redo":
                    outcome = self._serve_redo(thing, number, len(things))
                else:
                    outcome = self._serve_item(thing, number, len(things))
                served += 1
                if outcome == QUIT:
                    stop = "quit"
                    break
        except (Cancelled, KeyboardInterrupt):
            out("")
            out("  " + TEXT["stopped"])
            self._finish(served, len(things), "cancelled")
            return EXIT_NOT_YET
        out("")
        if stop == "time":
            out("  " + TEXT["time_up"].format(minutes=review.SESSION_MINUTES))
        elif stop == "quit":
            out("  " + TEXT["quit"])
        self._finish(served if stop != "quit" else served - 1, len(things), stop)
        return EXIT_OK

    # -- notes before the first item ------------------------------------------
    def _notes(self, enrolled):
        app = self.app
        out = self.out
        plan = self.plan
        if enrolled:
            due = schedule.due_date(self.state["review"][enrolled[0]])
            out("  " + TEXT["enrolled"].format(n=len(enrolled),
                                               date=due.isoformat() if due else ""))
        for entry in plan.pending:
            folder = entry.record["pending"].get("folder") or ("review/" + entry.id)
            out("  " + TEXT["pending"].format(item=entry.id,
                                              path=app.show(app.playground / folder)))
        if plan.orphans.missing or plan.orphans.unscheduled:
            ids = plan.orphans.missing + plan.orphans.unscheduled
            out("  " + TEXT["orphans_missing"].format(mark=WARN_MARK, n=len(ids),
                                                      ids="、".join(ids)))
        if plan.orphans.broken:
            out("  " + TEXT["orphans_broken"].format(mark=WARN_MARK, n=len(plan.orphans.broken),
                                                     ids="、".join(plan.orphans.broken)))

    def _nothing(self):
        out = self.out
        plan = self.plan
        today = self.app.today
        if plan.return_routine and plan.backlog:
            out("  " + TEXT["return_no_easy"])
            out("  " + TEXT["backlog"].format(n=plan.backlog))
        else:
            upcoming = review.next_due(self.state, self.app.catalog(), today)
            if upcoming is not None:
                out("  " + TEXT["nothing"] + TEXT["nothing_next"].format(date=upcoming.isoformat()))
            elif plan.pending:
                out("  " + TEXT["nothing"])
            else:
                out("  " + TEXT["nothing_ever"])
        if plan.return_routine:
            out("  " + TEXT["return_tutor"])
        self._unused()
        return EXIT_OK

    # -- serving ----------------------------------------------------------------
    def _source(self, lesson):
        return TEXT["source"].format(lesson=lesson.id, title=lesson.title)

    def _serve_redo(self, task, number, total):
        out = self.out
        lesson, station = task["lesson"], task["station"]
        station_id = task["id"]
        out(TEXT["item_head"].format(n=number, total=total, kind=TEXT["kind_redo"],
                                     source="{} {}".format(station_id, station.get("title", ""))))
        out("  " + TEXT["redo_body"].format(path=lesson.rel + "/lesson.md",
                                            number=lesson.station_number(station_id)))
        if task["before"] and task["before"] < self.app.today.isoformat():
            out("  " + TEXT["redo_late"].format(after=task["after"], before=task["before"]))
        if station_id in lesson.scenarios:
            out("  " + TEXT["redo_scenario"].format(id=lesson.scenario_id(station_id)))
        out("  " + TEXT["redo_how"].format(station=station_id))
        out("  " + TEXT["redo_later"])
        self.redo_shown.append(station_id)
        self.app.store.log("review-redo-shown", station=station_id)
        if number < total and _word(self.answers.pause("  " + TEXT["redo_next"])) == QUIT:
            return QUIT
        return SHOWN

    def _serve_item(self, entry, number, total):
        kind = TEXT[KIND_KEYS[entry.type]]
        self.out(TEXT["item_head"].format(n=number, total=total, kind=kind,
                                          source=self._source(entry.lesson)))
        if entry.type == "recall":
            outcome = self._recall(entry)
        elif entry.type == "do":
            outcome = self._do(entry)
        else:
            outcome = self._choice(entry)
        if outcome in (RIGHT, FUZZY, WRONG):
            self._record(entry, outcome)
        elif outcome == SKIP:
            self.counts[SKIP] += 1
            self.out("  " + TEXT["skipped"])
            self.app.store.log("review", item=entry.id, item_type=entry.type, result=SKIP)
        return outcome

    def _broken(self, entry, what):
        self.out("  " + TEXT["broken_item"].format(mark=WARN_MARK, what=what, id=entry.id))
        self.app.store.log("review-broken-item", item=entry.id, problem=what)
        return NOT_SERVED

    def _question(self, entry):
        self.out(indent(str(entry.item.get("q", "")).strip(), 2))

    def _recall(self, entry):
        out = self.out
        model = entry.item.get("a")
        if not isinstance(model, str) or not model.strip():
            return self._broken(entry, TEXT["broken_answer"])
        self._question(entry)
        word = _word(self.answers.pause("  " + TEXT["recall_think"]))
        if word:
            return word
        out("  " + TEXT["recall_answer"])
        out(indent(model.strip(), 4))
        if isinstance(entry.item.get("explain"), str) and entry.item["explain"].strip():
            out("  " + TEXT["explain"].format(text=entry.item["explain"].strip()))
        for _attempt in range(3):
            typed, scripted = self.answers.take("  " + TEXT["recall_grade"])
            result = self_grade(typed)
            if result is not None:
                return result
            if scripted:
                break
            out("  " + TEXT["recall_retry"])
        out("  " + TEXT["unreadable"].format(answer=one_line(typed, 30)))
        self.app.store.log("review", item=entry.id, item_type=entry.type, result="unreadable")
        return NOT_SERVED

    def _choice(self, entry):
        out = self.out
        item = entry.item
        if not _valid_choice(item):
            return self._broken(entry, TEXT["broken_options"])
        options = [str(option) for option in item["options"]]
        correct = letter_to_index(item["answer"])
        order = _shuffled_order(entry.id, len(options), self.app.today,
                                item.get("shuffle") is True)
        self._question(entry)
        for shown, original in enumerate(order):
            out(f"    {index_to_letter(shown)}. {options[original]}")
        first, last = "A", index_to_letter(len(options) - 1)
        chosen = None
        typed = ""
        for _attempt in range(3):
            typed, scripted = self.answers.take("  " + TEXT["choice_prompt"])
            word = _word(typed)
            if word:
                return word
            shown = choice_letter(typed, len(options))
            if shown is None:
                # the text of an option, dots folded (「惯例.事实标准」)
                shown = option_text_index(typed, [options[original] for original in order])
            if shown is not None:
                chosen = order[shown]
                break
            if scripted:
                break
            out("  " + TEXT["choice_retry"].format(first=first, last=last))
        if chosen is None:
            out("  " + TEXT["unreadable"].format(answer=one_line(typed, 30)))
            self.app.store.log("review", item=entry.id, item_type=entry.type, result="unreadable")
            return NOT_SERVED
        if chosen == correct:
            out("  " + self.app.console.paint(OK_MARK + " " + TEXT["right"], "ok"))
            result = RIGHT
        else:
            letter = index_to_letter(order.index(correct))
            out("  " + self.app.console.paint(
                BAD_MARK + " " + TEXT["wrong"].format(letter=letter, option=options[correct]),
                "bad"))
            result = WRONG
        if isinstance(item.get("explain"), str) and item["explain"].strip():
            out("  " + TEXT["explain"].format(text=item["explain"].strip()))
        return result

    def _do(self, entry):
        app = self.app
        out = self.out
        self._question(entry)
        word = _word(self.answers.pause("  " + TEXT["do_start"]))
        if word:
            return word
        info = build_do_scenario(app, entry, out)
        if info is None:
            return NOT_SERVED
        folder = "review/" + entry.id
        entry.record["pending"] = {"since": app.stamp(), "folder": folder, "tries": 0}
        app.store.save(self.state, events=[{"type": "review", "item": entry.id,
                                            "item_type": "do", "result": HANDED_OUT,
                                            "folder": folder}])
        out("  " + TEXT["do_ready"].format(path=app.show(info.path)))
        for line in info.todo:
            out(indent(line, 2))
        out("  " + TEXT["do_todo"])
        out("  " + TEXT["do_give_up"])
        self.handed_out = True
        return HANDED_OUT

    def _record(self, entry, result):
        app = self.app
        today = app.today
        record = schedule.answer(self.state, entry.id, result, today)
        retired = schedule.is_retired(record)
        self.counts[result] += 1
        if retired:
            self.counts["retired"] += 1
        app.store.save(self.state, events=[{
            "type": "review", "item": entry.id, "item_type": entry.type, "result": result,
            "box": record["box"], "due": record["due"], "retired": retired,
            "return_routine": self.plan.return_routine}])
        self.out("  " + schedule_line(record, result, today))

    # -- the end --------------------------------------------------------------
    def _finish(self, served, planned, stop):
        out = self.out
        counts = self.counts
        parts = []
        for key, text in ((RIGHT, "part_right"), (FUZZY, "part_fuzzy"),
                          (WRONG, "part_wrong"), (SKIP, "part_skip")):
            if counts[key]:
                parts.append(TEXT[text].format(n=counts[key]))
        if counts["retired"]:
            parts.append(TEXT["part_retired"].format(n=counts["retired"]))
        if parts:
            out("  " + TEXT["summary"].format(parts="，".join(parts)))
        elif not self.handed_out and not self.redo_shown:
            out("  " + TEXT["summary_none"])
        if stop in ("time", "quit", "cancelled"):
            left = max(0, planned - served) + self.plan.backlog
            if left:
                out("  " + TEXT["left_over"].format(n=left))
        if self.handed_out:
            out("  " + TEXT["after_do"])
        if self.redo_shown:
            out("  " + TEXT["after_redo"].format(stations="、".join(self.redo_shown)))
        if self.plan.return_routine:
            out("  " + TEXT["return_tutor"])
        self.app.store.log("review-end", stopped=stop or "", served=served,
                           results={key: value for key, value in counts.items() if value})
        self._unused()

    def _unused(self):
        if self.answers.queue:
            self.out("")
            self.out("  " + TEXT["unused_answers"].format(n=len(self.answers.queue)))


def schedule_line(record, result, today):
    """One sentence on what happens next to an item after ``result``."""
    if schedule.is_retired(record):
        return TEXT["retired"]
    due = schedule.due_date(record)
    days = (due - today).days if due else 0
    date = due.isoformat() if due else ""
    if result == RIGHT:
        return TEXT["next_right"].format(date=date, days=days)
    if result == FUZZY:
        return TEXT["next_fuzzy"].format(date=date)
    return TEXT["next_wrong"].format(date=date)


# ---------------------------------------------------------------------------
# do items: building the practice copy, grading, giving up
# ---------------------------------------------------------------------------
def build_do_scenario(app, entry, out):
    """Build a fresh copy of the item's scenario under ``review/<id>``.

    Uses the scenario builder interface of the core
    (``courselib.scenario.build``).  Returns the ``ScenarioInfo``, or None
    after telling the learner politely why it could not be built; a ``do``
    item that cannot be built is skipped, never counted as wrong.
    """
    try:
        from .. import scenario as scenario_lib
        build = scenario_lib.build
    except (ImportError, AttributeError) as exc:
        out("  " + TEXT["do_unavailable"].format(mark=WARN_MARK))
        app.store.log("review-do-unavailable", item=entry.id, detail=repr(exc))
        return None
    key = entry.item.get("scenario")
    builder = entry.lesson.scenarios.get(key) if isinstance(key, str) else None
    if not callable(builder):
        out("  " + TEXT["do_no_builder"].format(mark=WARN_MARK, key=key, id=entry.id))
        app.store.log("review-do-unavailable", item=entry.id, detail="no scenario " + repr(key))
        return None
    try:
        return build(app, builder, "review/" + entry.id, key=key, lesson_id=entry.lesson.id,
                     reset=True)
    except Refused as exc:
        out("  " + TEXT["do_refused"])
        out(indent(exc.message, 4))
        app.store.log("review-do-unavailable", item=entry.id, detail="refused")
        return None
    except (Cancelled, KeyboardInterrupt):
        raise
    except Exception as exc:  # noqa: BLE001 - a broken builder must not end the session
        problem = runner.make_problem(app, exc) if not isinstance(exc, ToolTrouble) else {
            "summary": exc.summary, "where": exc.where, "detail": exc.detail,
            "recovery": exc.recovery}
        out("  " + TEXT["do_trouble"])
        for line in runner.render_problem(app, entry.id, problem, place="review " + entry.id):
            out(indent(line, 2))
        app.store.log("review-do-unavailable", item=entry.id, detail=problem.get("summary", ""))
        return None


def _pending_info(app, entry):
    from .. import scenario as scenario_lib
    folder = entry.record["pending"].get("folder") or ("review/" + entry.id)
    path = scenario_lib.scenario_folder(app, folder)
    return path, scenario_lib.read_info(path)


def _grade(app, answers):
    """``review --grade``: run the check of each handed-out ``do`` item."""
    out = app.console.out
    catalog = app.catalog()
    state = app.store.load()
    progress.touch_session(state, app.now)
    pending = review.pending_entries(state, catalog, app.today)
    if not pending:
        app.store.save(state)
        out(TEXT["no_pending"])
        return EXIT_OK
    worst = EXIT_OK
    for entry in pending:
        out("")
        heading = TEXT["grade_head"].format(id=entry.id, source=review_source(entry))
        try:
            path, info = _pending_info(app, entry)
        except (ImportError, AttributeError):
            out(heading)
            out("  " + TEXT["do_unavailable"].format(mark=WARN_MARK))
            worst = max(worst, EXIT_PROBLEM)
            continue
        if not info.exists:
            out(heading)
            out("  " + TEXT["grade_gone"].format(path=app.show(path)))
            entry.record.pop("pending", None)
            app.store.save(state, events=[{"type": "review", "item": entry.id, "item_type": "do",
                                           "result": "folder_gone"}])
            continue
        result = runner.run_check(app, entry.item.get("check"), lesson=entry.lesson,
                                  station_id=entry.station, answers=answers.queue,
                                  scenario=info, state=state, warn_unused=False)
        del answers.queue[:result.answers_used]
        for line in runner.render_result(app, result, heading, place="review " + entry.id):
            out(line)
        pending_record = entry.record["pending"]
        event = {"type": "review", "item": entry.id, "item_type": "do", "outcome": result.outcome}
        out("")
        if result.outcome == runner.PROBLEM:
            out("  " + TEXT["grade_problem"])
            worst = max(worst, EXIT_PROBLEM)
        elif result.passed:
            outcome = RIGHT if int(pending_record.get("tries") or 0) == 0 else FUZZY
            entry.record.pop("pending", None)
            record = schedule.answer(state, entry.id, outcome, app.today)
            event.update({"result": outcome, "box": record["box"], "due": record["due"],
                          "retired": schedule.is_retired(record)})
            out("  " + grade_line(record, outcome, app.today))
        else:
            pending_record["tries"] = int(pending_record.get("tries") or 0) + 1
            event["tries"] = pending_record["tries"]
            out("  " + TEXT["grade_not_yet"])
            worst = max(worst, EXIT_NOT_YET)
        app.store.save(state, events=[event])
        data = {"target": entry.id, "kind": "review", "lesson": entry.lesson.id,
                "title": str(entry.item.get("q", ""))[:60]}
        data.update(result.to_dict())
        app.store.write_result(data)
    if answers.queue:
        out("")
        out("  " + TEXT["unused_answers"].format(n=len(answers.queue)))
    return worst


def grade_line(record, outcome, today):
    if schedule.is_retired(record):
        return TEXT["grade_retired"]
    due = schedule.due_date(record)
    days = (due - today).days if due else 0
    if outcome == RIGHT:
        return TEXT["grade_right"].format(date=due.isoformat() if due else "", days=days)
    return TEXT["grade_fuzzy"].format(date=due.isoformat() if due else "")


def _give_up(app):
    """``review --give-up``: the handed-out ``do`` item counts as 忘了."""
    out = app.console.out
    state = app.store.load()
    progress.touch_session(state, app.now)
    pending = review.pending_entries(state, app.catalog(), app.today)
    if not pending:
        app.store.save(state)
        out(TEXT["no_pending"])
        return EXIT_OK
    events = []
    for entry in pending:
        folder = entry.record["pending"].get("folder") or ("review/" + entry.id)
        entry.record.pop("pending", None)
        record = schedule.answer(state, entry.id, WRONG, app.today)
        events.append({"type": "review", "item": entry.id, "item_type": "do", "result": WRONG,
                       "gave_up": True, "box": record["box"], "due": record["due"]})
        out(TEXT["gave_up"].format(id=entry.id, date=record["due"]))
        out("  " + TEXT["gave_up_folder"].format(path=app.show(app.playground / folder)))
    app.store.save(state, events=events)
    return EXIT_OK


def review_source(entry):
    return TEXT["source"].format(lesson=entry.lesson.id, title=entry.lesson.title)
