"""Spaced review: the scheduler, the session, the return routine, cold redos (plan I4).

Every test runs in a throw-away sandbox (see helpers.py) with a simulated
clock (COURSE_NOW), so dates are exact.
"""

import datetime
import json
import unittest

import helpers
from courselib import review, schedule, store
from courselib.commands import review as review_command

D = datetime.date

# A lesson 1.6 (stations 1.6a 1.6b 1.6c) with one review item of every type.
# The generated template already has 1.6-r1 (recall, last station 1.6c) and
# 1.6-r2 (which, station 1.6a).
EXTRA = '''

def _do_check(ctx):
    info = ctx.scenario()
    if ctx.is_file(info.path / "done.txt"):
        ctx.ok("找到了 done.txt")
    else:
        ctx.fail("还没有 done.txt", where=ctx.show(info.path), saw="没有这个文件")


def build_task(sc):
    sc.write("task.txt", "在这里新建 done.txt")
    sc.fact("word", sc.word())
    sc.todo("在练习场里新建一个 done.txt")


SCENARIOS["task"] = build_task

REVIEW += [
    {"id": "1.6-p1", "type": "predict", "tier": "fluent", "station": "1.6a",
     "q": "会输出什么？", "options": ["一", "二"], "answer": "A", "explain": "因为是一。"},
    {"id": "1.6-f1", "type": "fault", "tier": "fluent", "station": "1.6b",
     "q": "哪里错了？", "options": ["甲", "乙", "丙"], "answer": "C"},
    {"id": "1.6-d1", "type": "do", "tier": "fluent", "station": "1.6b",
     "q": "动手：在练习场里新建 done.txt。", "scenario": "task", "check": _do_check},
    {"id": "1.6-l1", "type": "recall", "tier": "lookup", "station": "1.6a",
     "q": "这个不排进复习。", "a": "对。"},
]
'''

FIRST_DAY = "2026-11-19T10:00:00"


def with_recall_items(test, count):
    """A sandbox whose lesson 1.6 has ``count`` extra recall items 1.6-m0 ..."""
    items = "\n".join(
        f'    {{"id": "1.6-m{n}", "type": "recall", "tier": "fluent", "q": "第 {n} 题？", '
        f'"a": "答 {n}。"}},' for n in range(count))
    box = helpers.Sandbox(test)
    box.add_syllabus_lesson("1.6", extra=EXTRA + "\nREVIEW += [\n" + items + "\n]\n")
    return box


def write_state(box, review_records=None, stations=None, sessions=None):
    """Write learner/state.json directly (for dates far apart)."""
    state = store.empty_state()
    state["review"] = review_records or {}
    state["stations"] = stations or {}
    state["sessions"] = sessions or []
    folder = box.root / "learner"
    folder.mkdir(exist_ok=True)
    (folder / "state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def session_on(day):
    return {"date": day, "start": day + "T09:00:00", "last": day + "T09:30:00", "minutes": 30}


def rec(box_number, due, history=None):
    return {"box": box_number, "due": due, "history": history or []}


def right(day, box_number):
    return {"date": day, "result": "right", "box": box_number}


def wrong(day):
    return {"date": day, "result": "wrong", "box": 1}


class SchedulerTest(unittest.TestCase):
    """Every box transition of the Leitner schedule (courselib.schedule)."""

    def test_right_answers_climb_every_box_and_then_retire(self):
        state = store.empty_state()
        day = D(2026, 11, 19)
        record = schedule.enroll(state, "x", day)
        self.assertEqual((record["box"], record["due"]), (1, "2026-11-21"))
        for box_after, days in ((2, 7), (3, 21), (4, 60), (5, 180)):
            day = schedule.due_date(record)
            record = schedule.answer(state, "x", schedule.RIGHT, day)
            self.assertEqual(record["box"], box_after)
            self.assertEqual(schedule.due_date(record), day + datetime.timedelta(days=days))
            self.assertFalse(schedule.is_retired(record))
        day = schedule.due_date(record)
        record = schedule.answer(state, "x", schedule.RIGHT, day)
        self.assertTrue(schedule.is_retired(record))
        self.assertIsNone(record["due"])
        self.assertEqual(record["history"][-1], {"date": day.isoformat(), "result": "right",
                                                 "retired": True, "box": 5})
        self.assertEqual(schedule.due_items(state, day + datetime.timedelta(days=4000)), [])
        self.assertIsNone(schedule.next_due(state, day))
        self.assertEqual(schedule.box_counts(state), [0, 0, 0, 0, 0])
        self.assertEqual(schedule.retired_count(state), 1)
        # enrolling again (a station passed once more) does not bring it back
        self.assertTrue(schedule.is_retired(schedule.enroll(state, "x", day)))

    def test_fuzzy_keeps_the_box_in_every_box(self):
        for box_number, days in zip(range(1, 6), schedule.INTERVAL_DAYS):
            state = store.empty_state()
            state["review"]["x"] = rec(box_number, "2026-11-19")
            record = schedule.answer(state, "x", schedule.FUZZY, D(2026, 11, 19))
            self.assertEqual(record["box"], box_number)
            self.assertEqual(schedule.due_date(record), D(2026, 11, 19) + datetime.timedelta(days=days))

    def test_a_miss_in_any_box_goes_back_to_box_1_due_the_next_day(self):
        for box_number in range(1, 6):
            state = store.empty_state()
            state["review"]["x"] = rec(box_number, "2026-11-19")
            record = schedule.answer(state, "x", schedule.WRONG, D(2026, 11, 19))
            self.assertEqual((record["box"], record["due"]), (1, "2026-11-20"))
        # and from box 1 it climbs again with the normal intervals
        record = schedule.answer(state, "x", schedule.RIGHT, D(2026, 11, 20))
        self.assertEqual((record["box"], record["due"]), (2, "2026-11-27"))

    def test_unreadable_records_are_read_leniently(self):
        state = store.empty_state()
        state["review"]["x"] = {"box": "abc", "due": "soon", "history": "junk"}
        self.assertEqual(schedule.box_of(state["review"]["x"]), 1)
        record = schedule.answer(state, "x", schedule.RIGHT, D(2026, 11, 19))
        self.assertEqual((record["box"], record["due"]), (2, "2026-11-26"))
        self.assertEqual(record["history"], [{"date": "2026-11-19", "result": "right", "box": 2}])
        with self.assertRaises(ValueError):
            schedule.answer(state, "x", "maybe", D(2026, 11, 19))


class PlanTest(unittest.TestCase):
    """What a session serves (courselib.review), without running the command."""

    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=EXTRA)
        self.catalog = self.box.app().catalog()

    def many(self, count):
        return with_recall_items(self, count).app().catalog()

    def test_at_most_8_oldest_due_first(self):
        catalog = self.many(12)
        state = store.empty_state()
        for n in range(12):
            state["review"][f"1.6-m{n}"] = rec(1, f"2026-11-{1 + n:02d}")
        plan = review.make_plan(state, catalog, D(2026, 11, 19))
        self.assertEqual(plan.due_total, 12)
        self.assertEqual([entry.id for entry in plan.items],
                         [f"1.6-m{n}" for n in range(8)])
        self.assertEqual(plan.backlog, 4)
        self.assertFalse(plan.return_routine)

    def test_types_are_mixed_and_the_do_item_comes_last(self):
        catalog = self.many(4)
        state = store.empty_state()
        due = {"1.6-m0": "2026-11-01", "1.6-m1": "2026-11-02", "1.6-m2": "2026-11-03",
               "1.6-d1": "2026-11-04", "1.6-r2": "2026-11-05", "1.6-p1": "2026-11-06",
               "1.6-m3": "2026-11-07"}
        for item_id, day in due.items():
            state["review"][item_id] = rec(1, day)
        plan = review.make_plan(state, catalog, D(2026, 11, 19))
        ids = [entry.id for entry in plan.items]
        self.assertEqual(ids, ["1.6-m0", "1.6-r2", "1.6-m1", "1.6-p1", "1.6-m2", "1.6-m3",
                               "1.6-d1"])
        types = [entry.type for entry in plan.items[:4]]
        self.assertTrue(all(a != b for a, b in zip(types, types[1:])))

    def test_no_new_do_item_while_one_is_out(self):
        state = store.empty_state()
        state["review"]["1.6-d1"] = rec(1, "2026-11-10")
        state["review"]["1.6-d1"]["pending"] = {"since": "2026-11-18T10:00:00",
                                                "folder": "review/1.6-d1", "tries": 0}
        state["review"]["1.6-r1"] = rec(1, "2026-11-10")
        plan = review.make_plan(state, self.catalog, D(2026, 11, 19))
        self.assertEqual([entry.id for entry in plan.items], ["1.6-r1"])
        self.assertEqual([entry.id for entry in plan.pending], ["1.6-d1"])
        self.assertEqual(review.due_count(state, self.catalog, D(2026, 11, 19)), 1)

    def test_lookup_items_are_never_served(self):
        state = store.empty_state()
        state["review"]["1.6-l1"] = rec(1, "2026-11-10")
        plan = review.make_plan(state, self.catalog, D(2026, 11, 19))
        self.assertEqual(plan.items, [])
        self.assertEqual(plan.orphans.unscheduled, ["1.6-l1"])

    def test_return_routine_picks_four_easy_items(self):
        state = store.empty_state()
        # last answered right, in boxes 3, 1, 2; never answered; last answered wrong
        state["review"] = {
            "1.6-r1": rec(3, "2026-11-01", [right("2026-10-01", 3)]),
            "1.6-r2": rec(1, "2026-11-02", [right("2026-10-01", 1)]),
            "1.6-p1": rec(2, "2026-11-03", [right("2026-10-01", 2)]),
            "1.6-f1": rec(1, "2026-11-04"),
            "1.6-d1": rec(1, "2026-11-05", [right("2026-10-01", 1)]),
        }
        plan = review.make_plan(state, self.catalog, D(2026, 11, 19), days_away=18)
        self.assertTrue(plan.return_routine)
        self.assertEqual(sorted(entry.id for entry in plan.items),
                         ["1.6-f1", "1.6-p1", "1.6-r1", "1.6-r2"])
        self.assertNotIn("1.6-d1", [entry.id for entry in plan.items])
        self.assertEqual(plan.backlog, 1)
        state["review"]["1.6-f1"]["history"] = [wrong("2026-10-01")]
        state["review"]["1.6-r1"]["history"] = [wrong("2026-10-01")]
        plan = review.make_plan(state, self.catalog, D(2026, 11, 19), days_away=18)
        # easiest first: right in box 1, right in box 2, then the two missed ones
        self.assertEqual([entry.id for entry in plan.items],
                         ["1.6-r2", "1.6-p1", "1.6-f1", "1.6-r1"])

    def test_ten_days_away_is_not_yet_a_return(self):
        state = store.empty_state()
        state["review"]["1.6-r1"] = rec(1, "2026-11-10")
        self.assertFalse(review.make_plan(state, self.catalog, D(2026, 11, 19), 10).return_routine)
        self.assertTrue(review.make_plan(state, self.catalog, D(2026, 11, 19), 11).return_routine)


class SessionTest(unittest.TestCase):
    """The ``review`` command across simulated dates."""

    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=EXTRA)

    def run_review(self, *answers, now, **options):
        argv = ["review"]
        for answer in answers:
            argv += ["--answer", answer]
        return self.box.run(*argv, now=now, noninteractive=True, **options)

    def pass_station(self, station, now=FIRST_DAY):
        self.box.flag(station)
        result = self.box.run("check", station, now=now, noninteractive=True)
        self.assertEqual(result.code, 0, result)

    def record(self, item_id):
        return self.box.state()["review"][item_id]

    def test_nothing_scheduled_yet(self):
        result = self.run_review(now=FIRST_DAY)
        self.assertEqual(result.code, 0, result)
        self.assertIn("还没有排进复习计划的题", result.out)

    def test_items_enter_when_their_station_first_passes_and_come_due(self):
        self.pass_station("1.6a")
        self.assertEqual(sorted(self.box.state()["review"]), ["1.6-p1", "1.6-r2"])
        early = self.run_review(now="2026-11-20T10:00:00")
        self.assertEqual(early.code, 0, early)
        self.assertIn("现在没有到期的复习题。下一次有题到期：2026-11-21。", early.out)
        due = self.run_review("A", "B", now="2026-11-21T10:00:00")
        self.assertEqual(due.code, 0, due)
        self.assertIn("今天到期：2 道复习题。这次做 2 道", due.out)
        self.assertIn("答对了。", due.out)
        self.assertIn("解释：因为是一。", due.out)
        self.assertIn("下次复习：2026-11-28（隔 7 天）。", due.out)
        self.assertEqual(self.record("1.6-p1")["box"], 2)
        self.assertEqual(self.record("1.6-r2")["box"], 2)
        self.assertNotIn("Traceback", due.text)

    def test_a_recall_item_through_every_box_to_retirement(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-21")},
                    sessions=[session_on("2026-11-19")])
        day = D(2026, 11, 21)
        for box_after in (2, 3, 4, 5):
            result = self.run_review("1", now=day.isoformat() + "T09:00:00")
            self.assertEqual(result.code, 0, result)
            self.assertIn("参考答案：", result.out)
            record = self.record("1.6-r1")
            self.assertEqual(record["box"], box_after)
            day = D.fromisoformat(record["due"])
        result = self.run_review("记得", now=day.isoformat() + "T09:00:00")
        self.assertIn("这道题毕业了，以后不再出现", result.out)
        self.assertIn("其中 1 道毕业", result.out)
        self.assertTrue(schedule.is_retired(self.record("1.6-r1")))
        later = self.run_review(now="2030-01-01T09:00:00")
        self.assertIn("还没有排进复习计划的题", later.out)
        status = self.box.run("status", now="2030-01-01T09:00:00")
        self.assertIn("到期的复习：0 条", status.out)

    def test_fuzzy_and_forgotten(self):
        write_state(self.box, {"1.6-r1": rec(3, "2026-11-19"), "1.6-r2": rec(4, "2026-11-18")},
                    sessions=[session_on("2026-11-18")])
        result = self.run_review("C", "2", now=FIRST_DAY)       # r2 is older: served first
        self.assertEqual(result.code, 0, result)
        self.assertIn("不对。正确答案是 B：乙", result.out)
        self.assertIn("明天（2026-11-20）再来一次", result.out)
        self.assertIn("间隔不变，2026-12-10 再来一次", result.out)
        self.assertEqual((self.record("1.6-r2")["box"], self.record("1.6-r2")["due"]),
                         (1, "2026-11-20"))
        self.assertEqual((self.record("1.6-r1")["box"], self.record("1.6-r1")["due"]),
                         (3, "2026-12-10"))
        self.assertIn("这次复习：模糊 1 道，忘了 1 道。", result.out)
        events = self.box.events("review")
        self.assertEqual([(e["item"], e["result"]) for e in events],
                         [("1.6-r2", "wrong"), ("1.6-r1", "fuzzy")])

    def test_the_cap_of_8_and_the_backlog_line(self):
        box = with_recall_items(self, 11)
        write_state(box, {f"1.6-m{n}": rec(1, f"2026-11-{1 + n:02d}") for n in range(11)},
                    sessions=[session_on("2026-11-18")])
        result = box.run("review", *(["--answer", "1"] * 8), now=FIRST_DAY, noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("这次做 8 道", result.out)
        self.assertIn("还有 3 条，不急，下次再说。", result.out)
        self.assertIn("第 8/8 题", result.out)
        self.assertNotIn("第 9/", result.out)
        state = box.state()["review"]
        self.assertEqual(sorted(i for i, r in state.items() if r["box"] == 2),
                         [f"1.6-m{n}" for n in range(8)])
        status = box.run("status", now=FIRST_DAY)
        self.assertIn("到期的复习：3 条", status.out)

    def test_skip_keeps_the_item_due_and_q_ends_the_session(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-18"), "1.6-r2": rec(1, "2026-11-19")},
                    sessions=[session_on("2026-11-18")])
        result = self.run_review("s", "q", now=FIRST_DAY)
        self.assertEqual(result.code, 0, result)
        self.assertIn("跳过了，这道题还在到期的列表里。", result.out)
        self.assertIn("好，这次复习到这里。", result.out)
        self.assertEqual(self.record("1.6-r1"), rec(1, "2026-11-18"))
        self.assertEqual(self.record("1.6-r2"), rec(1, "2026-11-19"))

    def test_choice_answers_in_other_spellings_and_unreadable_ones(self):
        write_state(self.box, {"1.6-r2": rec(1, "2026-11-18"), "1.6-p1": rec(1, "2026-11-19")},
                    sessions=[session_on("2026-11-18")])
        result = self.run_review("选 Ｂ", "完全不知道", now=FIRST_DAY)
        self.assertEqual(result.code, 0, result)
        self.assertEqual(self.record("1.6-r2")["box"], 2)
        self.assertIn("看不懂回答「完全不知道」，这道题先跳过", result.out)
        self.assertEqual(self.record("1.6-p1"), rec(1, "2026-11-19"))
        again = self.run_review("一", now="2026-11-19T11:00:00")      # the text of option A
        self.assertEqual(self.record("1.6-p1")["box"], 2, again)

    def test_shuffled_options_are_graded_by_content(self):
        order = review_command._shuffled_order("1.6-x", 4, D(2026, 11, 19), True)
        self.assertEqual(sorted(order), [0, 1, 2, 3])
        self.assertEqual(order, review_command._shuffled_order("1.6-x", 4, D(2026, 11, 19), True))
        self.assertEqual(review_command._shuffled_order("1.6-x", 4, D(2026, 11, 19), False),
                         [0, 1, 2, 3])

    def test_noninteractive_without_enough_answers_is_a_usage_error_and_keeps_progress(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-18"), "1.6-r2": rec(1, "2026-11-19")},
                    sessions=[session_on("2026-11-18")])
        result = self.run_review("1", now=FIRST_DAY)
        self.assertEqual(result.code, 64, result)
        self.assertIn("--answer", result.err)
        self.assertEqual(self.record("1.6-r1")["box"], 2)
        self.assertEqual(self.record("1.6-r2")["box"], 1)

    def test_extra_answers_are_mentioned(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-18")}, sessions=[session_on("2026-11-18")])
        result = self.run_review("1", "2", now=FIRST_DAY)
        self.assertIn("多给了 1 个 --answer，没有用上。", result.out)

    def test_end_of_file_and_ctrl_c_stop_politely_and_keep_what_was_answered(self):
        for stop in (None, KeyboardInterrupt):
            with self.subTest(stop=stop):
                write_state(self.box, {"1.6-r1": rec(1, "2026-11-18"),
                                       "1.6-r2": rec(1, "2026-11-19")},
                            sessions=[session_on("2026-11-18")])
                inputs = ["", "1"] + ([stop] if stop else [])
                result = self.box.run("review", inputs=inputs, tty=True, now=FIRST_DAY)
                self.assertEqual(result.code, 1, result)
                self.assertIn("复习停在这里。", result.out)
                # no "everything answered was recorded" line followed by a
                # "nothing was recorded" line (tester novice-abuse)
                self.assertNotIn("已经做完的题都记下了", result.out)
                self.assertNotIn("没有记录任何回答", result.out)
                self.assertIn("剩下的 1 条下次再说。", result.out)
                self.assertNotIn("Traceback", result.text)
                self.assertEqual(self.record("1.6-r1")["box"], 2)
                self.assertEqual(self.record("1.6-r2")["box"], 1)

    def test_live_recall_waits_for_enter_and_rereads_an_unclear_grade(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-18")}, sessions=[session_on("2026-11-18")])
        result = self.box.run("review", inputs=["", "嗯", "模糊"], tty=True, now=FIRST_DAY)
        self.assertEqual(result.code, 0, result)
        self.assertIn("想好了按回车看参考答案", result.out)
        self.assertIn("请输入 1、2 或 3", result.out)
        self.assertEqual(self.record("1.6-r1")["history"][-1]["result"], "fuzzy")

    def test_the_session_stops_after_about_ten_minutes(self):
        box = with_recall_items(self, 6)
        write_state(box, {f"1.6-m{n}": rec(1, f"2026-11-{1 + n:02d}") for n in range(6)},
                    sessions=[session_on("2026-11-18")])
        ticks = iter(range(0, 100000, 250))           # each look at the clock: 250 s later
        original = review.clock
        review.clock = lambda: next(ticks)
        self.addCleanup(setattr, review, "clock", original)
        result = box.run("review", *(["--answer", "1"] * 6), now=FIRST_DAY, noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("已经大约 10 分钟了，今天的复习到这里。", result.out)
        answered = [i for i, r in box.state()["review"].items() if r["box"] == 2]
        # 0 s, 250 s, 500 s: three items started within 10 minutes; at 750 s it stops
        self.assertEqual(len(answered), 3)
        self.assertIn("剩下的 3 条下次再说。", result.out)


class ReturnRoutineTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=EXTRA)

    def test_after_more_than_ten_days(self):
        write_state(self.box, {
            "1.6-r1": rec(3, "2026-11-01", [right("2026-10-11", 3)]),
            "1.6-r2": rec(1, "2026-11-02", [right("2026-10-31", 1)]),
            "1.6-p1": rec(2, "2026-11-03", [right("2026-10-27", 2)]),
            "1.6-f1": rec(1, "2026-11-04", [wrong("2026-11-03")]),
            "1.6-d1": rec(1, "2026-11-05", [right("2026-11-03", 1)]),
        }, stations={"1.6a": {"status": "assisted", "attempts": 1, "first_pass": "2026-11-01T10:00:00",
                              "highest_hint": 4, "last_hint": "2026-11-01T09:00:00",
                              "redo": {"after": "2026-11-04", "before": "2026-11-08", "done": None}}},
            sessions=[session_on("2026-11-01")])
        result = self.box.run("review", "--answer", "1", "--answer", "B", "--answer", "A",
                              "--answer", "1", now=FIRST_DAY, noninteractive=True)
        self.assertEqual(result.code, 0, result)
        lines = result.out.splitlines()
        self.assertEqual(lines[2].strip(),
                         "距离上次学习已经 18 天。这次只做 4 道容易的题，先找回手感。")
        self.assertIn("还有 2 条，不急，下次再说。", result.out)   # 1 do item + 1 redo
        self.assertNotIn("重做", result.out)
        self.assertNotIn("1.6-d1", result.out)
        self.assertNotIn("第 5/", result.out)
        self.assertIn("带我走回归流程", result.out)
        session = self.box.events("review-session")[-1]
        self.assertTrue(session["return_routine"])
        self.assertEqual(sorted(session["planned"]), ["1.6-f1", "1.6-p1", "1.6-r1", "1.6-r2"])

    def test_the_day_after_is_a_normal_session(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-01")},
                    sessions=[session_on("2026-11-01"), session_on("2026-11-19")])
        result = self.box.run("review", "--answer", "1", now="2026-11-20T10:00:00",
                              noninteractive=True)
        self.assertNotIn("距离上次学习", result.out)
        self.assertIn("今天到期：1 道复习题", result.out)


class ColdRedoTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=EXTRA)

    def test_hint_level_4_schedules_a_redo_served_first_3_days_later(self):
        for _level in range(4):
            self.assertEqual(self.box.run("hint", "1.6a", noninteractive=True).code, 0)
        self.box.flag("1.6a")
        self.box.run("check", "1.6a", noninteractive=True)
        record = self.box.state()["stations"]["1.6a"]
        self.assertEqual((record["status"], record["redo"]["after"]), ("assisted", "2026-11-22"))
        early = self.box.run("review", "--answer", "A", "--answer", "B",
                             now="2026-11-21T10:00:00", noninteractive=True)
        self.assertIn("这次复习：记得 2 道。", early.out)
        self.assertNotIn("重做", early.out)
        due = self.box.run("review", now="2026-11-22T10:00:00", noninteractive=True)
        self.assertEqual(due.code, 0, due)
        self.assertIn("今天到期：1 站要重做", due.out)
        self.assertIn("第 1/1 题 · 重做 · 1.6a", due.out)
        self.assertIn("python3 tools/course.py check 1.6a", due.out)
        self.assertIn("别忘了重做：1.6a", due.out)
        redo_pass = self.box.run("check", "1.6a", now="2026-11-22T11:00:00", noninteractive=True)
        self.assertIn("这次是不看提示的重做，通过了", redo_pass.out)
        after = self.box.run("review", now="2026-11-23T10:00:00", noninteractive=True)
        self.assertNotIn("重做", after.out)

    def test_redo_comes_before_due_items(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-01")},
                    stations={"1.6b": {"status": "assisted", "first_pass": "2026-11-12T10:00:00",
                                       "highest_hint": 4, "redo": {"after": "2026-11-15",
                                                                   "before": "2026-11-17",
                                                                   "done": None}}},
                    sessions=[session_on("2026-11-18")])
        result = self.box.run("review", "--answer", "1", now=FIRST_DAY, noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertLess(result.out.index("重做 · 1.6b"), result.out.index("回忆 · 1.6"))
        self.assertIn("建议的时间是 2026-11-15 到 2026-11-17。过了也没关系", result.out)
        self.assertIn("今天到期：1 道复习题、1 站要重做。这次做 2 道", result.out)


    def test_a_live_learner_presses_enter_after_the_redo(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-01")},
                    stations={"1.6b": {"status": "assisted", "first_pass": "2026-11-12T10:00:00",
                                       "highest_hint": 4, "redo": {"after": "2026-11-15",
                                                                   "before": "2026-11-19",
                                                                   "done": None}}},
                    sessions=[session_on("2026-11-18")])
        result = self.box.run("review", inputs=["", "", "1"], tty=True, now=FIRST_DAY)
        self.assertEqual(result.code, 0, result)
        self.assertIn("记下了就按回车，接着做复习题", result.out)
        self.assertNotIn("建议的时间是", result.out)          # still inside the window
        self.assertEqual(self.box.state()["review"]["1.6-r1"]["box"], 2)
        alone = self.box.run("review", tty=True, now="2026-11-19T11:00:00")   # no pause at the end
        self.assertEqual(alone.code, 0, alone)
        self.assertIn("第 1/1 题 · 重做 · 1.6b", alone.out)
        self.assertNotIn("记下了就按回车", alone.out)


class DoItemTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=EXTRA)
        write_state(self.box, {"1.6-d1": rec(2, "2026-11-19")}, sessions=[session_on("2026-11-18")])
        self.folder = self.box.playground / "review" / "1.6-d1"

    def serve(self, now=FIRST_DAY):
        result = self.box.run("review", now=now, noninteractive=True)
        self.assertEqual(result.code, 0, result)
        return result

    def record(self):
        return self.box.state()["review"]["1.6-d1"]

    def test_built_handed_out_graded_on_the_first_try(self):
        result = self.serve()
        self.assertIn("练习场搭好了：~/Developer/playground/review/1.6-d1", result.out)
        self.assertIn("在练习场里新建一个 done.txt", result.out)
        self.assertIn("review --grade", result.out)
        self.assertTrue((self.folder / "task.txt").is_file())
        self.assertEqual(self.record()["pending"]["folder"], "review/1.6-d1")
        self.assertEqual(self.box.run("status").out.count("到期的复习：0 条"), 1)
        again = self.serve(now="2026-11-19T11:00:00")
        self.assertIn("还有一道动手题没交：1.6-d1", again.out)
        (self.folder / "done.txt").write_text("好了\n", encoding="utf-8")
        graded = self.box.run("review", "--grade", now="2026-11-19T12:00:00", noninteractive=True)
        self.assertEqual(graded.code, 0, graded)
        self.assertIn("通过", graded.out)
        self.assertIn("记为「记得」。下次复习：2026-12-10（隔 21 天）", graded.out)
        record = self.record()
        self.assertNotIn("pending", record)
        self.assertEqual(record["box"], 3)
        self.assertEqual(self.box.last_result()["target"], "1.6-d1")
        nothing = self.box.run("review", "--grade", noninteractive=True)
        self.assertIn("现在没有等着检查的动手题", nothing.out)

    def test_not_yet_then_right_counts_as_fuzzy(self):
        self.serve()
        early = self.box.run("review", "--grade", noninteractive=True)
        self.assertEqual(early.code, 1, early)
        self.assertIn("还没达标", early.out)
        self.assertIn("改好后再运行", early.out)
        self.assertEqual(self.record()["pending"]["tries"], 1)
        (self.folder / "done.txt").write_text("好了\n", encoding="utf-8")
        graded = self.box.run("review", "--grade", noninteractive=True)
        self.assertEqual(graded.code, 0, graded)
        self.assertIn("记为「模糊」", graded.out)
        self.assertEqual(self.record()["box"], 2)

    def test_give_up_counts_as_forgotten(self):
        self.serve()
        result = self.box.run("review", "--give-up", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("记为「忘了」，明天（2026-11-20）重新出现", result.out)
        record = self.record()
        self.assertEqual((record["box"], record["due"]), (1, "2026-11-20"))
        self.assertNotIn("pending", record)
        tomorrow = self.serve(now="2026-11-20T10:00:00")      # rebuilt over the old copy
        self.assertIn("练习场搭好了", tomorrow.out)
        self.assertFalse((self.folder / "done.txt").exists())

    def test_a_vanished_practice_folder_is_not_counted(self):
        self.serve()
        import shutil
        shutil.rmtree(str(self.folder))
        result = self.box.run("review", "--grade", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("练习场不见了", result.out)
        self.assertEqual(self.record(), rec(2, "2026-11-19"))

    def test_grade_and_give_up_together_is_a_usage_error(self):
        result = self.box.run("review", "--grade", "--give-up", noninteractive=True)
        self.assertEqual(result.code, 64)
        self.assertIn("不能一起用", result.err)

    def test_scenario_builder_unavailable_degrades_politely(self):
        from courselib import scenario
        original = scenario.build
        del scenario.build
        self.addCleanup(setattr, scenario, "build", original)
        result = self.serve()
        self.assertIn("动手题暂时做不了：搭练习场的功能还没准备好。这道题先跳过，不算错。", result.out)
        self.assertEqual(self.record(), rec(2, "2026-11-19"))
        self.assertNotIn("Traceback", result.text)

    def test_a_broken_builder_is_a_checker_problem_not_a_miss(self):
        box = helpers.Sandbox(self)
        box.add_syllabus_lesson("1.6", extra=EXTRA + '''
def build_broken(sc):
    raise RuntimeError("boom")

SCENARIOS["task"] = build_broken
''')
        write_state(box, {"1.6-d1": rec(2, "2026-11-19")}, sessions=[session_on("2026-11-18")])
        result = box.run("review", now=FIRST_DAY, noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("动手题的练习场没搭起来", result.out)
        self.assertIn("这不是你的错", result.out)
        self.assertNotIn("Traceback", result.text)
        self.assertEqual(box.state()["review"]["1.6-d1"], rec(2, "2026-11-19"))

    def test_a_folder_without_marker_is_refused_not_deleted(self):
        self.folder.mkdir(parents=True)
        (self.folder / "mine.txt").write_text("别删我\n", encoding="utf-8")
        result = self.serve()
        self.assertIn("动手题的练习场搭不了", result.out)
        self.assertTrue((self.folder / "mine.txt").is_file())
        self.assertNotIn("pending", self.record())


class RobustnessTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=EXTRA)

    def test_corrupt_state_file_is_a_checker_problem_with_a_recovery(self):
        folder = self.box.root / "learner"
        folder.mkdir()
        (folder / "state.json").write_text("{not json", encoding="utf-8")
        for argv in (["review"], ["review", "--grade"], ["review", "--give-up"]):
            result = self.box.run(*argv, noninteractive=True)
            self.assertEqual(result.code, 2, result)
            self.assertIn("检查器出问题", result.out)
            self.assertIn("state.json.bad", result.out)
            self.assertNotIn("Traceback", result.text)
        self.assertEqual((folder / "state.json").read_text(encoding="utf-8"), "{not json")

    def test_damaged_review_records_are_served_and_repaired(self):
        write_state(self.box, {"1.6-r1": {"box": "abc", "due": "soon", "history": "junk"},
                               "1.6-r2": {"box": None}},
                    sessions=[session_on("2026-11-18")])
        status = self.box.run("status")
        self.assertEqual(status.code, 0, status)
        self.assertIn("到期的复习：2 条", status.out)
        result = self.box.run("review", "--answer", "1", "--answer", "B", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertEqual(self.box.state()["review"]["1.6-r1"],
                         {"box": 2, "due": "2026-11-26",
                          "history": [{"date": "2026-11-19", "result": "right", "box": 2}]})
        self.assertEqual(self.box.state()["review"]["1.6-r2"]["box"], 2)

    def test_items_whose_lesson_disappeared_or_broke_are_skipped_and_not_counted(self):
        self.box.add_lesson("this is not python (\n", "01-foundations", "07-read-diff")
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-18"),
                               "3.9-r1": rec(1, "2026-11-01"),      # lesson gone
                               "1.6-gone": rec(1, "2026-11-01"),    # item removed from 1.6
                               "1.7-r1": rec(1, "2026-11-01")},     # lesson 1.7 is broken
                    sessions=[session_on("2026-11-18")])
        status = self.box.run("status")
        self.assertIn("到期的复习：1 条", status.out)
        result = self.box.run("review", "--answer", "1", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("有 2 道复习题找不到对应的课程或题目了（1.6-gone、3.9-r1）", result.out)
        self.assertIn("有 1 道复习题所在的课程模块加载失败（1.7-r1）", result.out)
        self.assertIn("这次做 1 道", result.out)
        state = self.box.state()["review"]
        self.assertEqual(state["3.9-r1"], rec(1, "2026-11-01"))       # kept untouched
        self.assertEqual(state["1.6-r1"]["box"], 2)

    def test_items_added_after_the_station_passed_are_enrolled_by_review(self):
        write_state(self.box, {}, stations={"1.6a": {"status": "passed",
                                                     "first_pass": "2026-11-10T10:00:00"}},
                    sessions=[session_on("2026-11-18")])
        result = self.box.run("review", noninteractive=True)
        self.assertIn("补排了 2 道复习题", result.out)
        self.assertEqual(sorted(self.box.state()["review"]), ["1.6-p1", "1.6-r2"])
        self.assertEqual(self.box.state()["review"]["1.6-p1"]["due"], "2026-11-21")

    def test_a_malformed_choice_item_is_skipped_not_graded(self):
        box = helpers.Sandbox(self)
        box.add_syllabus_lesson("1.6", extra='''
REVIEW += [{"id": "1.6-bad", "type": "which", "tier": "fluent", "q": "坏题",
            "options": ["只有一个"], "answer": "B"}]
''')
        write_state(box, {"1.6-bad": rec(1, "2026-11-18")}, sessions=[session_on("2026-11-18")])
        result = box.run("review", noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("这道题的写法有问题（选项或答案不对）", result.out)
        self.assertEqual(box.state()["review"]["1.6-bad"], rec(1, "2026-11-18"))

    def test_state_writes_are_atomic_and_logged(self):
        write_state(self.box, {"1.6-r1": rec(1, "2026-11-18")}, sessions=[session_on("2026-11-18")])
        self.box.run("review", "--answer", "1", noninteractive=True)
        leftovers = [p.name for p in (self.box.root / "learner").iterdir() if p.name.endswith(".tmp")]
        self.assertEqual(leftovers, [])
        kinds = [event["type"] for event in self.box.events()]
        for kind in ("review-session", "review", "state", "review-end"):
            self.assertIn(kind, kinds)

    def test_status_hook(self):
        catalog = self.box.app().catalog()
        state = store.empty_state()
        state["review"] = {"1.6-r1": rec(1, "2026-11-18"), "9.9-r1": rec(1, "2026-11-18"),
                           "1.6-r2": {"box": 5, "due": None, "retired": "2026-11-01"},
                           "1.6-p1": rec(1, "2026-11-25")}
        self.assertEqual(review.due_count(state, catalog, D(2026, 11, 19)), 1)
        self.assertEqual(review.next_due(state, catalog, D(2026, 11, 19)), D(2026, 11, 25))


class Python39Test(unittest.TestCase):
    def test_a_session_runs_on_python_3_9(self):
        python = helpers.find_python39()
        if python is None:
            self.skipTest("no Python 3.9 on this machine")
        box = helpers.Sandbox(self)
        box.add_syllabus_lesson("1.6", extra=EXTRA)
        write_state(box, {"1.6-r1": rec(1, "2026-11-18"), "1.6-d1": rec(1, "2026-11-18")},
                    sessions=[session_on("2026-11-18")])
        result = box.run_process("review", "--answer", "1", python=python, noninteractive=True)
        self.assertEqual(result.code, 0, result)
        self.assertIn("练习场搭好了", result.out)
        (box.playground / "review" / "1.6-d1" / "done.txt").write_text("x\n", encoding="utf-8")
        graded = box.run_process("review", "--grade", python=python, noninteractive=True)
        self.assertEqual(graded.code, 0, graded)
        self.assertEqual(box.state()["review"]["1.6-d1"]["box"], 2)


if __name__ == "__main__":
    unittest.main()
