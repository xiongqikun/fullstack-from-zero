"""The state store: atomic writes, a log that can rebuild the state, corrupt files."""

import json
import os
import unittest

import helpers
from courselib import store as store_module
from courselib.errors import StateTrouble, ToolTrouble


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.app = self.box.app()
        self.store = self.app.store
        self.folder = self.box.root / "learner"

    def test_missing_state_is_created(self):
        self.assertFalse(self.folder.exists())
        state = self.store.load()
        self.assertEqual(state, store_module.empty_state())
        on_disk = json.loads((self.folder / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk["schema"], 1)
        self.assertEqual(self.box.events("state-created")[0]["replayed_events"], 0)

    def test_save_is_atomic_and_leaves_no_temporary_file(self):
        state = self.store.load()
        state["decisions"]["commit_signing"] = "off"
        self.store.save(state, events=[{"type": "demo"}])
        self.assertEqual(sorted(os.listdir(str(self.folder))), ["log.jsonl", "state.json"])
        self.assertEqual(self.box.state()["decisions"], {"commit_signing": "off"})

    def test_failed_write_keeps_the_old_file(self):
        state = self.store.load()
        state["decisions"]["a"] = 1
        self.store.save(state)
        before = (self.folder / "state.json").read_bytes()
        real_replace = os.replace

        def broken_replace(source, target):
            raise OSError("disk full")

        os.replace = broken_replace
        try:
            state["decisions"]["a"] = 2
            with self.assertRaises(ToolTrouble):
                self.store.save(state)
        finally:
            os.replace = real_replace
        self.assertEqual((self.folder / "state.json").read_bytes(), before)
        self.assertEqual([name for name in os.listdir(str(self.folder)) if name.endswith(".tmp")], [])

    def test_every_event_has_a_timestamp_and_one_line(self):
        self.store.load()
        self.store.log("note", text="第一行\n第二行")
        lines = (self.folder / "log.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertTrue(all(json.loads(line)["ts"] == helpers.NOW for line in lines))
        self.assertEqual(json.loads(lines[-1])["text"], "第一行\n第二行")

    def test_log_is_append_only(self):
        self.store.load()
        self.store.log("one")
        first = (self.folder / "log.jsonl").read_text(encoding="utf-8")
        self.store.log("two")
        second = (self.folder / "log.jsonl").read_text(encoding="utf-8")
        self.assertTrue(second.startswith(first))

    def test_append_after_a_truncated_line_starts_a_new_line(self):
        self.store.load()
        with open(str(self.folder / "log.jsonl"), "a", encoding="utf-8") as handle:
            handle.write('{"ts": "x", "type": "half')
        self.store.log("after")
        events = list(self.store.events(count_bad=True))
        self.assertIsNone(events[-2])
        self.assertEqual(events[-1]["type"], "after")

    def test_corrupt_state_is_reported_and_never_overwritten(self):
        self.folder.mkdir()
        garbage = '{"schema": 1, "stations": {'
        (self.folder / "state.json").write_text(garbage, encoding="utf-8")
        with self.assertRaises(StateTrouble) as caught:
            self.store.load()
        self.assertIn("state.json", caught.exception.summary)
        self.assertIn("state.json.bad", caught.exception.recovery)
        self.assertEqual((self.folder / "state.json").read_text(encoding="utf-8"), garbage)

    def test_wrong_shapes_are_corrupt_too(self):
        self.folder.mkdir()
        for bad in ("[]", '{"stations": []}', '{"stations": {"1.6a": 3}}', '{"schema": "1"}',
                    '{"sessions": {}}', '{"sessions": [1]}'):
            (self.folder / "state.json").write_text(bad, encoding="utf-8")
            with self.assertRaises(StateTrouble, msg=bad):
                self.store.load()
            self.assertEqual((self.folder / "state.json").read_text(encoding="utf-8"), bad)

    def test_state_from_a_newer_tool_is_refused(self):
        self.folder.mkdir()
        (self.folder / "state.json").write_text('{"schema": 2}', encoding="utf-8")
        with self.assertRaises(StateTrouble) as caught:
            self.store.load()
        self.assertIn("更新", caught.exception.summary)

    def test_save_refuses_to_replace_a_corrupt_file(self):
        self.folder.mkdir()
        (self.folder / "state.json").write_text("not json", encoding="utf-8")
        with self.assertRaises(StateTrouble):
            self.store.save(store_module.empty_state())
        self.assertEqual((self.folder / "state.json").read_text(encoding="utf-8"), "not json")

    def test_unknown_keys_survive_a_round_trip(self):
        state = self.store.load()
        state["future_feature"] = {"x": 1}
        state["stations"]["1.6a"] = {"status": "open", "extra": True}
        self.store.save(state)
        again = self.box.app().store.load()
        self.assertEqual(again["future_feature"], {"x": 1})
        self.assertTrue(again["stations"]["1.6a"]["extra"])

    def test_state_is_rebuilt_from_the_log_after_the_recovery_instruction(self):
        state = self.store.load()
        state["stations"]["1.6a"] = {"status": "passed", "attempts": 2}
        state["sessions"].append({"date": "2026-11-19", "minutes": 10})
        self.store.save(state, events=[{"type": "check", "station": "1.6a"}])
        state["stations"]["1.6a"]["attempts"] = 3
        state["stations"]["1.6b"] = {"status": "open", "attempts": 1}
        state["sessions"][0]["minutes"] = 25
        state["sessions"].append({"date": "2026-11-20", "minutes": 5})
        state["review"]["1.6-r1"] = {"box": 2, "due": "2026-11-26", "history": []}
        state["decisions"]["commit_signing"] = "off"
        self.store.save(state)
        del state["decisions"]["commit_signing"]
        state["decisions"]["workspace_location"] = "~/Developer/fullstack-from-zero"
        self.store.save(state)
        expected = self.box.state()

        # what the recovery instruction says: rename the file, run again
        os.rename(str(self.folder / "state.json"), str(self.folder / "state.json.bad"))
        rebuilt = self.box.app().store.load()
        self.assertEqual(rebuilt, expected)
        self.assertGreater(self.box.events("state-created")[-1]["replayed_events"], 0)

    def test_rebuild_skips_unreadable_log_lines(self):
        state = self.store.load()
        state["decisions"]["k"] = "v"
        self.store.save(state)
        with open(str(self.folder / "log.jsonl"), "a", encoding="utf-8") as handle:
            handle.write("this is not json\n[1, 2]\n")
        os.remove(str(self.folder / "state.json"))
        rebuilt = self.box.app().store.load()
        self.assertEqual(rebuilt["decisions"], {"k": "v"})
        self.assertEqual(self.box.events("state-created")[-1]["unreadable_lines"], 2)

    def test_home_directory_never_reaches_the_files(self):
        state = self.store.load()
        secret = str(self.box.home / "Developer" / "my-site")
        state["decisions"]["where"] = secret
        self.store.save(state, events=[{"type": "note", "path": secret}])
        self.store.write_result({"detail": "Traceback in " + secret})
        for name in ("state.json", "log.jsonl", "last-result.json"):
            text = (self.folder / name).read_text(encoding="utf-8")
            self.assertNotIn(str(self.box.home), text, name)
            self.assertIn("~/Developer/my-site", text, name)

    def test_last_result_round_trip(self):
        self.assertIsNone(self.store.read_result())
        self.store.write_result({"target": "1.6a", "outcome": "passed"})
        result = self.store.read_result()
        self.assertEqual(result["target"], "1.6a")
        self.assertEqual(result["ts"], helpers.NOW)

    def test_unwritable_folder_is_a_tool_problem_not_a_crash(self):
        (self.box.root / "learner").write_text("a file where the folder should be")
        with self.assertRaises(ToolTrouble):
            self.store.load()


class PatchTest(unittest.TestCase):
    def test_diff_then_apply_reproduces_the_new_state(self):
        old = store_module.empty_state()
        old["stations"] = {"a": {"x": 1}, "b": {"x": 2}}
        old["sessions"] = [{"d": 1}, {"d": 2}, {"d": 3}]
        old["gone"] = True
        new = store_module.empty_state()
        new["stations"] = {"a": {"x": 9}, "c": {"x": 3}}
        new["sessions"] = [{"d": 1}, {"d": 20}]
        new["added"] = [1, 2]
        ops = store_module.diff_state(old, new)
        json.dumps(ops)
        rebuilt = json.loads(json.dumps(old))
        store_module.apply_ops(rebuilt, ops)
        self.assertEqual(rebuilt, new)

    def test_no_difference_no_operations(self):
        state = store_module.empty_state()
        self.assertEqual(store_module.diff_state(state, json.loads(json.dumps(state))), [])

    def test_malformed_operations_are_ignored(self):
        state = store_module.empty_state()
        applied = store_module.apply_ops(state, [
            None, {"path": []}, {"path": ["a", "b", "c"], "value": 1},
            {"path": [3], "value": 1}, {"path": ["sessions", 5], "value": {}},
            {"path": ["stations", True], "value": {}}, {"path": ["stations", "x"]},
        ])
        self.assertEqual(applied, 0)
        self.assertEqual(state, store_module.empty_state())
        self.assertEqual(store_module.apply_ops(state, "nonsense"), 0)


if __name__ == "__main__":
    unittest.main()
