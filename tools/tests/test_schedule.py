"""Leitner boxes for review items, across simulated dates (plan I4 ``review``)."""

import datetime
import unittest

import helpers
from courselib import schedule, store

D = datetime.date


class LeitnerTest(unittest.TestCase):
    def test_intervals_are_2_days_1_week_3_weeks_2_months_6_months(self):
        self.assertEqual(schedule.INTERVAL_DAYS, (2, 7, 21, 60, 180))
        self.assertEqual([schedule.interval(box) for box in range(7)],
                         [2, 2, 7, 21, 60, 180, 180])

    def test_an_item_climbs_one_box_per_right_answer_and_retires_after_the_last(self):
        state = store.empty_state()
        today = D(2026, 11, 19)
        record = schedule.enroll(state, "1.6-r1", today)
        self.assertEqual((record["box"], record["due"]), (1, "2026-11-21"))
        expected = [(2, 7), (3, 21), (4, 60), (5, 180)]
        for box, days in expected:
            today = schedule.due_date(record)
            self.assertEqual(schedule.due_items(state, today), ["1.6-r1"])
            self.assertEqual(schedule.due_items(state, today - datetime.timedelta(days=1)), [])
            record = schedule.grade(state, "1.6-r1", True, today)
            self.assertEqual(record["box"], box)
            self.assertEqual(schedule.due_date(record), today + datetime.timedelta(days=days))
        # right in the last box: retired, never due again (review task brief)
        today = schedule.due_date(record)
        record = schedule.grade(state, "1.6-r1", True, today)
        self.assertEqual((record["box"], record["due"], record["retired"]),
                         (5, None, today.isoformat()))
        self.assertEqual(schedule.due_items(state, today + datetime.timedelta(days=999)), [])
        self.assertEqual([entry["result"] for entry in record["history"]], ["right"] * 5)

    def test_a_wrong_answer_goes_back_to_box_1_due_the_next_day(self):
        state = store.empty_state()
        schedule.enroll(state, "x", D(2026, 11, 19))
        schedule.grade(state, "x", True, D(2026, 11, 21))
        schedule.grade(state, "x", True, D(2026, 11, 28))
        record = schedule.grade(state, "x", False, D(2026, 12, 19))
        self.assertEqual((record["box"], record["due"]), (1, "2026-12-20"))   # due the next day
        self.assertEqual(record["history"][-1], {"date": "2026-12-19", "result": "wrong", "box": 1})

    def test_due_items_most_overdue_first_and_next_due(self):
        state = store.empty_state()
        schedule.enroll(state, "late", D(2026, 11, 1))
        schedule.enroll(state, "later", D(2026, 11, 10))
        schedule.enroll(state, "future", D(2026, 11, 19))
        self.assertEqual(schedule.due_items(state, D(2026, 11, 19)), ["late", "later"])
        self.assertEqual(schedule.next_due(state, D(2026, 11, 19)), D(2026, 11, 21))
        self.assertEqual(schedule.box_counts(state), [3, 0, 0, 0, 0])

    def test_enrolling_twice_keeps_the_record(self):
        state = store.empty_state()
        schedule.enroll(state, "x", D(2026, 11, 19))
        schedule.grade(state, "x", True, D(2026, 11, 21))
        record = schedule.enroll(state, "x", D(2026, 12, 1))
        self.assertEqual(record["box"], 2)

    def test_unreadable_records_are_skipped(self):
        state = store.empty_state()
        state["review"] = {"a": {"box": 1, "due": "soon"}, "b": "junk",
                           "c": {"box": 9, "due": "2026-11-01"}}
        self.assertEqual(schedule.due_items(state, D(2026, 11, 19)), ["c"])
        self.assertEqual(schedule.box_counts(state), [1, 0, 0, 0, 1])

    def test_history_is_bounded(self):
        state = store.empty_state()
        for day in range(80):
            schedule.grade(state, "x", day % 2 == 0, D(2026, 1, 1) + datetime.timedelta(days=day))
        self.assertEqual(len(state["review"]["x"]["history"]), schedule.MAX_HISTORY)


class EnrolmentThroughCheckTest(unittest.TestCase):
    """Fluent items enter box 1 when their station first passes; they come due by date."""

    def test_items_come_due_with_the_clock(self):
        box = helpers.Sandbox(self)
        box.add_syllabus_lesson("1.6")
        box.flag("1.6a")
        self.assertEqual(box.run("check", "1.6a", now="2026-11-19T10:00:00").code, 0)
        review = box.state()["review"]
        self.assertEqual(sorted(review), ["1.6-r2"])          # only the fluent item of 1.6a
        self.assertIn("到期的复习：0 条", box.run("status", now="2026-11-19T11:00:00").out)
        self.assertIn("到期的复习：0 条（下一次：2026-11-21）",
                      box.run("status", now="2026-11-20T09:00:00").out)
        self.assertIn("到期的复习：1 条", box.run("status", now="2026-11-21T09:00:00").out)


if __name__ == "__main__":
    unittest.main()
