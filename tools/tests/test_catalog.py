"""Lesson discovery: order, isolation of broken modules, no files written."""

import os
import unittest

import helpers

from courselib.catalog import load_catalog, syllabus_gate_lessons


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)

    def catalog(self):
        return load_catalog(self.box.root)

    def test_empty_workspace_has_no_lessons(self):
        catalog = self.catalog()
        self.assertEqual(catalog.lessons, [])
        self.assertEqual(catalog.broken, [])

    def test_lessons_come_in_learning_order(self):
        for lesson_id in ("1.10", "1.9", "0.2", "1.1"):
            self.box.add_syllabus_lesson(lesson_id)
        catalog = self.catalog()
        self.assertEqual([lesson.id for lesson in catalog.lessons], ["0.2", "1.1", "1.9", "1.10"])
        self.assertEqual(catalog.stages(), [0, 1])
        stations = [station["id"] for _, station in catalog.stations()]
        self.assertEqual(stations[:3], ["0.2a", "0.2b", "0.2c"])
        self.assertEqual(stations[-2:], ["1.10a", "1.10b"])

    def test_lookups(self):
        self.box.add_syllabus_lesson("1.6")
        catalog = self.catalog()
        lesson, station = catalog.station("1.6b")
        self.assertEqual((lesson.id, station["id"]), ("1.6", "1.6b"))
        self.assertEqual(lesson.station_number("1.6c"), 3)
        self.assertEqual(catalog.station("1.6z"), (None, None))
        self.assertIsNone(catalog.lesson("1.7"))
        self.assertEqual(lesson.rel, "stages/01-foundations/06-first-commit")

    def test_scenario_ids(self):
        self.box.add_syllabus_lesson("1.6", extra='SCENARIOS["1.6b"] = build_start\n')
        catalog = self.catalog()
        self.assertEqual(sorted(catalog.scenario_ids()), ["1.6-start", "1.6b"])
        for text in ("1.6", "1.6-start"):
            lesson, key, builder = catalog.scenario(text)
            self.assertEqual((lesson.id, key), ("1.6", "start"))
            self.assertTrue(callable(builder))
        self.assertEqual(catalog.scenario("1.6b")[1], "1.6b")
        self.assertIsNone(catalog.scenario("start"))
        self.assertIsNone(catalog.scenario("1.7"))

    def test_a_broken_module_does_not_break_the_others(self):
        self.box.add_syllabus_lesson("1.1")
        self.box.add_lesson("META = {\n", "01-foundations", "02-copy-move-delete")
        self.box.add_lesson("raise RuntimeError('boom at import')\n",
                            "01-foundations", "03-search")
        self.box.add_lesson("import sys\nsys.exit(3)\n", "01-foundations", "04-editor")
        self.box.add_lesson("META = 'not a dict'\n", "01-foundations", "05-markdown-readme")
        self.box.add_lesson("import no_such_module_anywhere\n",
                            "01-foundations", "06-first-commit")
        self.box.add_syllabus_lesson("1.7")
        catalog = self.catalog()
        self.assertEqual([lesson.id for lesson in catalog.lessons], ["1.1", "1.7"])
        broken = dict((lesson.id, lesson.error) for lesson in catalog.broken)
        self.assertEqual(sorted(broken), ["1.2", "1.3", "1.4", "1.5", "1.6"])
        self.assertIn("语法错误", broken["1.2"])
        self.assertIn("RuntimeError", broken["1.3"])
        self.assertIn("boom at import", broken["1.3"])
        self.assertIn("第 1 行", broken["1.3"])
        self.assertIn("退出", broken["1.4"])
        self.assertIn("META", broken["1.5"])
        self.assertIn("no_such_module_anywhere", broken["1.6"])
        self.assertEqual(catalog.broken_for("1.3a").id, "1.3")
        self.assertIsNone(catalog.broken_for("1.1a"))

    def test_bad_meta_shapes_make_a_lesson_unusable(self):
        self.box.add_lesson("META = {'id': 16, 'stations': []}\n", "01-foundations", "01-a")
        self.box.add_lesson("META = {'id': '1.2', 'stations': 'ab'}\n", "01-foundations", "02-b")
        self.box.add_lesson("META = {'id': '1.3', 'stations': [{'id': 7}]}\n",
                            "01-foundations", "03-c")
        catalog = self.catalog()
        self.assertEqual(catalog.lessons, [])
        self.assertEqual(len(catalog.broken), 3)

    def test_duplicate_ids_are_flagged(self):
        self.box.add_syllabus_lesson("1.1")
        source = helpers.lesson_source("1.1", "09-copy")
        self.box.add_lesson(source, "01-foundations", "09-copy")
        catalog = self.catalog()
        self.assertEqual(len(catalog.lessons), 1)
        self.assertEqual(len(catalog.broken), 1)
        self.assertIn("重复", catalog.broken[0].error)

    def test_loading_prints_nothing_and_writes_nothing(self):
        folder = self.box.add_lesson(
            "print('noise at import')\n" + helpers.lesson_source("1.1", "01-create-and-view"),
            "01-foundations", "01-create-and-view")
        before = sorted(os.listdir(str(folder)))
        app = self.box.app()
        self.assertEqual([lesson.id for lesson in app.catalog().lessons], ["1.1"])
        self.assertEqual(app.test_output.getvalue(), "")
        self.assertEqual(sorted(os.listdir(str(folder))), before)

    def test_checks_may_be_spelled_in_capitals(self):
        source = helpers.lesson_source("1.1", "01-create-and-view").replace("\nchecks = ", "\nCHECKS = ")
        self.box.add_lesson(source, "01-foundations", "01-create-and-view")
        lesson = self.catalog().lesson("1.1")
        self.assertEqual(sorted(lesson.checks), ["1.1a", "1.1b"])

    def test_accessors_tolerate_wrong_types(self):
        source = helpers.lesson_source("1.1", "01-create-and-view") + (
            "\nHINTS = None\nREVIEW = 'x'\nSCENARIOS = []\nEXAM = {}\nTERMS = [1, {'term': 't'}]\n")
        self.box.add_lesson(source, "01-foundations", "01-create-and-view")
        lesson = self.catalog().lesson("1.1")
        self.assertEqual(lesson.hints, {})
        self.assertEqual(lesson.review, [])
        self.assertEqual(lesson.scenarios, {})
        self.assertEqual(lesson.exam, [])
        self.assertEqual(lesson.terms, [{"term": "t"}])


GATE_TASKS = '''
def _b(sc):
    sc.write("a.txt", "a")


def _g(ctx):
    ctx.ok("好")


def _t(n, gate="{gate}", text=True):
    task = {{"id": "{id}-x" + str(n), "gate": gate, "title": "t", "build": _b, "grade": _g}}
    if text:
        task["task"] = {{"A": "做 A", "B": "做 B"}}
    return task


EXAM = [{tasks}]
'''


class GatePoolTest(unittest.TestCase):
    """G1: a gate covers the lessons of its own tasks and borrows nothing."""

    def setUp(self):
        self.box = helpers.Sandbox(self)

    def add(self, lesson_id, tasks):
        gate = helpers.syllabus.lesson_entry(lesson_id)["gate"]
        self.box.add_syllabus_lesson(lesson_id, extra=GATE_TASKS.format(
            id=lesson_id, gate=gate, tasks=tasks))

    def test_pool_lessons_and_unusable_tasks(self):
        self.add("1.6", "_t(1), _t(2), _t(3, text=False)")
        self.add("1.11", "_t(1), _t(2, gate='gate-b')")
        catalog = load_catalog(self.box.root)
        primary, secondary, unusable = catalog.gate_pool("gate-1")
        self.assertEqual([t["id"] for _l, t in primary], ["1.11-x1"])
        self.assertEqual((secondary, unusable), ([], []))
        primary_b, _s, unusable_b = catalog.gate_pool("gate-b")
        self.assertEqual([t["id"] for _l, t in primary_b], ["1.6-x1", "1.6-x2", "1.11-x2"])
        self.assertEqual(unusable_b, ["1.6-x3"])
        self.assertEqual(catalog.gate_lesson_ids("gate-1"), ["1.11"])
        self.assertEqual(catalog.gate_lesson_ids("gate-b"), ["1.6", "1.11"])
        # a gate without tasks yet: the lessons the syllabus assigns to it
        self.assertEqual(catalog.gate_lesson_ids("gate-0"), ["0.1", "0.2", "0.3", "0.4"])
        self.assertEqual(syllabus_gate_lessons("gate-1"),
                         ["1.11", "1.12", "1.13", "1.14", "1.15", "1.16"])
        self.assertEqual(syllabus_gate_lessons("gate-z"), [])
        self.assertEqual(catalog.gate_ids(), ["gate-0", "gate-a", "gate-b", "gate-1"])


if __name__ == "__main__":
    unittest.main()
