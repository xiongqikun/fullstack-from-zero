"""Scenario building: the builder context, the marker, and the safety rules."""

import base64
import datetime
import json
import os
import shutil
import subprocess
import sys
import types
import unittest
from unittest import mock

import helpers

from courselib import scenario
from courselib.errors import Refused, ToolTrouble
from courselib.gitread import GitReader, GitRepo


def simple(sc):
    sc.write("hello.txt", "你好")
    sc.fact("n", 3)
    sc.todo("打开   hello.txt\n看一看")


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.app = self.box.app()

    def build(self, builder=simple, folder="demo", **options):
        options.setdefault("seed", 5)
        return scenario.build(self.app, builder, folder, **options)

    # -- the normal case ------------------------------------------------------
    def test_build_writes_the_state_and_the_marker(self):
        info = self.build(scenario_id="1.6b", key="1.6b", lesson_id="1.6")
        target = self.box.playground / "demo"
        self.assertEqual(info.path, target)
        self.assertTrue(info.exists)
        self.assertEqual((target / "hello.txt").read_text(encoding="utf-8"), "你好\n")
        stored = json.loads((target / ".playground").read_text(encoding="utf-8"))
        self.assertEqual(next(iter(stored)), "note")
        self.assertEqual(stored["note"], "学习工具的记号文件，请不要改动或删除，也不用打开。")
        self.assertEqual(stored["marker"], 2)
        self.assertNotIn("facts", stored)
        marker = scenario.read_marker(target)
        self.assertEqual(marker["scenario"], "1.6b")
        self.assertEqual(marker["lesson"], "1.6")
        self.assertEqual(marker["seed"], 5)
        self.assertEqual(marker["built"], helpers.NOW)
        self.assertTrue(marker["complete"])
        self.assertEqual(marker["facts"], {"n": 3})
        self.assertEqual(info.facts, {"n": 3})
        self.assertEqual(info.todo, ["打开 hello.txt 看一看"])
        self.assertEqual((info.id, info.key, info.lesson, info.seed, info.form),
                         ("1.6b", "1.6b", "1.6", 5, None))
        built = self.box.events("scenario-built")
        self.assertEqual((built[0]["scenario"], built[0]["seed"]), ("1.6b", 5))

    def test_same_seed_same_state_different_seed_different_state(self):
        def builder(sc):
            sc.fact("words", sc.words(3))
            sc.fact("number", sc.randint(1, 10 ** 6))
            sc.fact("pick", sc.pick(["a", "b", "c", "d", "e", "f", "g", "h"]))
            sc.fact("sample", sc.sample(range(100), 5))
            sc.fact("word", sc.word())

        first = self.build(builder, "one", seed=42).facts
        again = self.build(builder, "two", seed=42).facts
        other = self.build(builder, "three", seed=43).facts
        self.assertEqual(first, again)
        self.assertNotEqual(first, other)
        self.assertEqual(len(set(first["words"])), 3)

    def test_a_seed_is_chosen_when_none_is_given(self):
        info = scenario.build(self.app, simple, "auto")
        self.assertIsInstance(info.seed, int)
        self.assertGreater(info.seed, 0)

    def test_missing_scenario_reads_as_not_built(self):
        info = scenario.read_info(self.box.playground / "nothing")
        self.assertFalse(info.exists)
        self.assertFalse(info.started)
        self.assertEqual(info.facts, {})

    def test_form_is_passed_to_the_builder(self):
        def builder(sc):
            sc.fact("form", sc.form)

        self.assertEqual(self.build(builder, "exam/a", form="A").facts, {"form": "A"})
        self.assertEqual(self.build(builder, "exam/b", form="B").form, "B")

    # -- refusing to overwrite and to delete ----------------------------------
    def test_refuses_a_folder_that_is_not_empty(self):
        self.build()
        with self.assertRaises(Refused) as caught:
            self.build()
        self.assertIn("--reset", caught.exception.message)
        self.assertNotIn(str(self.box.home), caught.exception.message)

    def test_the_refusal_names_the_full_rebuild_command_for_a_lesson_scenario(self):
        self.build(scenario_id="1.6b", folder="1.6b")
        with self.assertRaises(Refused) as caught:
            self.build(scenario_id="1.6b", folder="1.6b")
        self.assertIn("python3 tools/course.py scenario 1.6b --reset", caught.exception.message)
        # an exam folder is always rebuilt by the exam command: no scenario command there
        self.build(scenario_id="exam-gate-b/1.6-x1", folder="exam-gate-b/1.6-x1")
        with self.assertRaises(Refused) as caught:
            self.build(scenario_id="exam-gate-b/1.6-x1", folder="exam-gate-b/1.6-x1")
        self.assertNotIn("course.py scenario", caught.exception.message)

    def test_reset_rebuilds_a_folder_the_tool_built(self):
        self.build()
        target = self.box.playground / "demo"
        (target / "learner-work.txt").write_text("mine")
        info = self.build(reset=True, seed=6)
        self.assertEqual(info.seed, 6)
        self.assertFalse((target / "learner-work.txt").exists())
        self.assertTrue((target / "hello.txt").exists())

    def test_reset_refuses_a_folder_without_the_marker(self):
        target = self.box.playground / "demo"
        target.mkdir(parents=True)
        (target / "precious.txt").write_text("do not delete")
        with self.assertRaises(Refused) as caught:
            self.build(reset=True)
        self.assertIn(".playground", caught.exception.message)
        self.assertEqual((target / "precious.txt").read_text(), "do not delete")

    def test_an_empty_folder_is_simply_used(self):
        (self.box.playground / "demo").mkdir(parents=True)
        self.assertTrue(self.build().exists)

    def test_refuses_a_file_in_the_way(self):
        self.box.playground.mkdir(parents=True)
        (self.box.playground / "demo").write_text("a file")
        for reset in (False, True):
            with self.assertRaises(Refused):
                self.build(reset=reset)
        self.assertEqual((self.box.playground / "demo").read_text(), "a file")

    def test_refuses_anything_outside_the_playground(self):
        outside = self.box.home / "Documents"
        outside.mkdir()
        (outside / "thesis.txt").write_text("important")
        (outside / ".playground").write_text("{}")
        for folder in ("../Documents", "../../Documents", str(outside), "", ".", "a/../.."):
            with self.assertRaises(Refused, msg=folder):
                self.build(folder=folder, reset=True)
        with self.assertRaises(Refused):
            scenario.remove_built(self.app, outside)
        with self.assertRaises(Refused):
            scenario.remove_built(self.app, self.box.playground)
        self.assertEqual((outside / "thesis.txt").read_text(), "important")

    def test_refuses_a_link_that_leads_out_of_the_playground(self):
        outside = self.box.home / "Documents"
        outside.mkdir()
        (outside / "thesis.txt").write_text("important")
        (outside / ".playground").write_text("{}")
        self.box.playground.mkdir(parents=True)
        os.symlink(str(outside), str(self.box.playground / "demo"))
        with self.assertRaises(Refused):
            self.build(reset=True)
        with self.assertRaises(Refused):
            scenario.remove_built(self.app, self.box.playground / "demo")
        self.assertEqual((outside / "thesis.txt").read_text(), "important")

    def test_refuses_an_unsafe_playground_location(self):
        for unsafe in (self.box.home, self.box.home.parent, "/", self.box.root,
                       self.box.root.parent, "~"):
            env = self.box.environment(COURSE_PLAYGROUND=str(unsafe))
            app = helpers.App(self.box.root, env=env, console=self.app.console)
            with self.assertRaises(Refused, msg=str(unsafe)):
                scenario.build(app, simple, "demo", seed=1)

    def test_playground_location_follows_the_environment(self):
        elsewhere = self.box.base / "elsewhere"
        env = self.box.environment(COURSE_PLAYGROUND=str(elsewhere))
        app = helpers.App(self.box.root, env=env, console=self.app.console)
        info = scenario.build(app, simple, "demo", seed=1)
        self.assertEqual(info.path, elsewhere / "demo")
        self.assertFalse(self.box.playground.exists())

    # -- builders that go wrong -----------------------------------------------
    def test_a_failing_builder_is_a_tool_problem_and_can_be_reset(self):
        def broken(sc):
            sc.write("half.txt", "half")
            raise KeyError("oops")

        with self.assertRaises(ToolTrouble) as caught:
            self.build(broken)
        self.assertIn("KeyError", caught.exception.summary)
        self.assertNotIn(str(self.box.home), caught.exception.detail)
        info = scenario.read_info(self.box.playground / "demo")
        self.assertTrue(info.started)
        self.assertFalse(info.exists)
        self.assertTrue(self.build(reset=True).exists)

    def test_a_builder_that_exits_is_contained(self):
        def exits(sc):
            sys.exit(1)

        with self.assertRaises(ToolTrouble):
            self.build(exits)

    def test_a_builder_cannot_write_outside_its_folder(self):
        for bad in ("../escape.txt", "/tmp/escape.txt", "a/../../escape.txt"):
            def builder(sc, bad=bad):
                sc.write(bad, "x")

            with self.assertRaises(ToolTrouble, msg=bad):
                self.build(builder, "esc-" + str(abs(hash(bad))))
        self.assertFalse((self.box.playground / "escape.txt").exists())

    def test_facts_must_fit_into_json(self):
        def builder(sc):
            sc.fact("when", datetime.datetime.now())

        with self.assertRaises(ToolTrouble):
            self.build(builder)

    def test_builder_output_is_not_printed(self):
        def noisy(sc):
            print("debug noise")
            sc.write("a.txt", "a")

        self.build(noisy)
        self.assertEqual(self.app.test_output.getvalue(), "")


class ContextHelpersTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.app = self.box.app()

    def build(self, builder, folder="demo"):
        return scenario.build(self.app, builder, folder, seed=9)

    def test_file_helpers(self):
        (self.box.root / "material" / "site").mkdir(parents=True)
        (self.box.root / "material" / "site" / "index.html").write_text("<p>hi</p>\n")
        (self.box.root / "material" / "site" / "__pycache__").mkdir()
        (self.box.root / "material" / "one.txt").write_text("one\n")

        def builder(sc):
            sc.mkdir("empty/inner")
            sc.write("indented.txt", """
                第一行
                  缩进的第二行
            """)
            sc.write("exact.txt", "  keep \r\n as is", exact=True)
            sc.write("blank.txt", "")
            sc.write("run.sh", "#!/bin/sh\necho hi\n", executable=True)
            sc.write_bytes("gbk.txt", "你好".encode("gbk"))
            sc.append("log.txt", "a\n")
            sc.append("log.txt", "b\n")
            sc.touch("deep/er/touched.txt")
            sc.copy_in("material/site", "my-site")
            sc.copy_in("material/one.txt", "copies/one.txt")
            sc.write("gone.txt", "x")
            sc.remove("gone.txt")
            sc.remove("never-existed.txt")
            sc.write("old-name.txt", "x")
            sc.move("old-name.txt", "moved/new-name.txt")
            sc.set_mtime("log.txt", sc.ago(days=3))
            sc.fact("shown", sc.show("my-site"))
            sc.fact("root", str(sc.path()) == str(sc.root))

        info = self.build(builder)
        root = info.path
        self.assertTrue((root / "empty" / "inner").is_dir())
        self.assertEqual((root / "indented.txt").read_text(encoding="utf-8"), "第一行\n  缩进的第二行\n")
        self.assertEqual((root / "exact.txt").read_bytes(), b"  keep \r\n as is")
        self.assertEqual((root / "blank.txt").read_bytes(), b"")
        self.assertTrue(os.access(str(root / "run.sh"), os.X_OK))
        self.assertEqual((root / "gbk.txt").read_bytes(), "你好".encode("gbk"))
        self.assertEqual((root / "log.txt").read_text(), "a\nb\n")
        self.assertTrue((root / "deep" / "er" / "touched.txt").is_file())
        self.assertEqual(sorted(os.listdir(str(root / "my-site"))), ["index.html"])
        self.assertEqual((root / "copies" / "one.txt").read_text(), "one\n")
        self.assertFalse((root / "gone.txt").exists())
        self.assertTrue((root / "moved" / "new-name.txt").is_file())
        age = datetime.datetime(2026, 11, 19, 10) - datetime.datetime.fromtimestamp(
            (root / "log.txt").stat().st_mtime)
        self.assertEqual(age.days, 3)
        self.assertEqual(info.facts["shown"], "~/Developer/playground/demo/my-site")
        self.assertTrue(info.facts["root"])

    def test_copy_in_only_reads_from_the_workspace(self):
        for source in ("../home/secret", "/etc/hosts", "starter/missing"):
            def builder(sc, source=source):
                sc.copy_in(source, "x")

            with self.assertRaises(ToolTrouble, msg=source):
                self.build(builder, "copy-" + str(abs(hash(source))))

    def test_git_commits_use_the_practice_identity_and_ignore_global_settings(self):
        # the common bad case of plan G7: signing switched on without a signing program,
        # and a global ignore file that would swallow *.log
        self.box.write_gitconfig(
            "[user]\n\tname = Real Person\n\temail = real@example.com\n\tsigningkey = FAKEKEY0000\n"
            "[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = gpg-that-does-not-exist\n"
            "[core]\n\texcludesfile = {}\n[init]\n\tdefaultBranch = trunk\n".format(
                self.box.home / ".gitignore_global"))
        (self.box.home / ".gitignore_global").write_text("*.log\n.DS_Store\n")

        def builder(sc):
            sc.git_init("repo")
            sc.write("repo/app.log", "kept even though it is ignored globally")
            sc.write("repo/readme.txt", "hi")
            first = sc.git_commit("repo", "docs: 第一次")
            sc.write("repo/two.txt", "2")
            sc.write("repo/three.txt", "3")
            second = sc.git_commit("repo", "feat: 只加一个", add=["two.txt"],
                                   author=("同事小林", "lin@example.invalid"),
                                   date="2026-11-01T09:30:00")
            sc.git_commit("repo", "chore: 空提交", add=None, allow_empty=True)
            sc.fact("first", first)
            sc.fact("second", second)
            sc.fact("log", sc.git("repo", "log", "--format=%s"))
            sc.fact("failed", sc.git("repo", "show", "no-such-ref", check=False).code)

        info = self.build(builder)
        repo = GitRepo(info.path / "repo", GitReader(self.box.environment()))
        commits = repo.commits()
        self.assertEqual([c.subject for c in commits], ["chore: 空提交", "feat: 只加一个", "docs: 第一次"])
        self.assertEqual((commits[2].author_name, commits[2].author_email),
                         ("练习场", "playground@example.invalid"))
        self.assertEqual(commits[1].author_name, "同事小林")
        self.assertTrue(commits[1].date.startswith("2026-11-01T09:30:00"))
        self.assertTrue(commits[2].date.startswith("2026-11-19T10:00:00"))
        self.assertEqual(repo.branch, "main")
        self.assertEqual(repo.tracked(), ["app.log", "readme.txt", "two.txt"])
        self.assertEqual(repo.status().untracked, ["three.txt"])
        self.assertEqual(info.facts["first"], commits[2].hash)
        self.assertEqual(info.facts["second"], commits[1].hash)
        self.assertEqual(info.facts["log"].split("\n")[0], "chore: 空提交")
        self.assertNotEqual(info.facts["failed"], 0)
        # nothing leaked into the repository's own configuration or the global one
        self.assertIsNone(repo.config("user.name", scope="local"))
        self.assertIsNone(repo.config("commit.gpgsign", scope="local"))
        self.assertEqual(repo.config("user.name"), "Real Person")
        self.assertIn("gpgsign = true", (self.box.home / ".gitconfig").read_text())

    def test_default_commit_dates_keep_their_order(self):
        def builder(sc):
            sc.git_init("repo")
            for number in range(3):
                sc.write(f"repo/{number}.txt", str(number))
                sc.git_commit("repo", f"c{number}")

        info = self.build(builder)
        repo = GitRepo(info.path / "repo", GitReader(self.box.environment()))
        dates = [c.date[:19] for c in repo.commits()]
        self.assertEqual(dates, ["2026-11-19T10:02:00", "2026-11-19T10:01:00", "2026-11-19T10:00:00"])

    def test_bare_repository_and_push_to_a_local_remote(self):
        def builder(sc):
            sc.git_init("remotes/my-site.git", bare=True)
            sc.git_init("my-site")
            sc.write("my-site/index.html", "<h1>hi</h1>")
            sc.git_commit("my-site", "feat: 首页")
            sc.git("my-site", "remote", "add", "origin", str(sc.path("remotes/my-site.git")))
            sc.git("my-site", "push", "-u", "origin", "main")

        info = self.build(builder)
        reader = GitReader(self.box.environment())
        self.assertEqual(GitRepo(info.path / "remotes" / "my-site.git", reader).commit_count("main"), 1)
        self.assertEqual(GitRepo(info.path / "my-site", reader).upstream(), "origin/main")

    def test_builders_cannot_reach_the_network(self):
        def builder(sc):
            sc.git_init("repo")
            sc.git("repo", "fetch", "https://example.invalid/x.git")

        with self.assertRaises(ToolTrouble) as caught:
            self.build(builder)
        # Git's own refusal, not a failed name lookup: the protocol allow-list
        # is what keeps builders offline (mutation M8 of the safety tester).
        self.assertIn("transport 'https' not allowed", caught.exception.detail)

    def test_the_scenario_folder_itself_cannot_be_the_repository(self):
        for root in (".", ""):
            def builder(sc, root=root):
                sc.git_init(root)

            with self.assertRaises(ToolTrouble, msg=repr(root)):
                self.build(builder, "root-" + str(len(root)))

    def test_state_ladder_is_delegated_to_the_states_module(self):
        calls = []

        def build_state(name, base, workspace=None, now=None):
            calls.append((name, base, workspace, now))
            (base / "my-site").mkdir()
            return base / "my-site"

        fake = types.ModuleType("courselib.states")
        fake.build_state = build_state
        sys.modules["courselib.states"] = fake
        import courselib
        had = getattr(courselib, "states", None)
        courselib.states = fake
        try:
            def builder(sc):
                sc.fact("site", str(sc.state("S4").relative_to(sc.root)))

            info = self.build(builder)
        finally:
            del sys.modules["courselib.states"]
            if had is None:
                del courselib.states
            else:
                courselib.states = had
        self.assertEqual(info.facts["site"], "my-site")
        name, base, workspace, now = calls[0]
        self.assertEqual((name, base, workspace), ("S4", info.path, self.box.root))
        self.assertEqual(now, self.app.now)

    def test_fill_text(self):
        info = self.build(lambda sc: (sc.fact("repo", "site-cedar"), sc.fact("n", 3)))
        text = scenario.fill_text(self.app, "去 {dir}/{repo}，改 {n} 处；{unknown} 和 {} 不动", info)
        self.assertEqual(
            text, "去 ~/Developer/playground/demo/site-cedar，改 3 处；{unknown} 和 {} 不动")


class MarkerPrivacyTest(unittest.TestCase):
    """P1: a learner's own grep (or cat .playground) never meets an expected answer."""

    FACTS = types.MappingProxyType({"word": "lotus", "file": "orders/old/2025-12.txt", "line": 3,
             "dish": "番茄炒蛋", "code": "1059 大米", "names": ["heron-plan.md", "Cedar"],
             "nested": {"folder": "spring", "count": 12345}})

    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.app = self.box.app()

    def build(self):
        facts = self.FACTS

        def builder(sc):
            for key, value in facts.items():
                sc.fact(key, value)
            sc.todo("要找的客户代号：" + facts["word"])
            sc.todo("订单文件夹 " + sc.show("orders"))

        return scenario.build(self.app, builder, "secretive", seed=3)

    def leaves(self, value):
        if isinstance(value, (dict, types.MappingProxyType)):
            for item in value.values():
                yield from self.leaves(item)
        elif isinstance(value, list):
            for item in value:
                yield from self.leaves(item)
        else:
            yield str(value)

    def test_no_fact_and_no_fragment_of_one_is_in_the_marker(self):
        info = self.build()
        data = (info.path / ".playground").read_bytes()
        folded = data.lower()
        texts = [t for t in self.leaves(self.FACTS) if len(t) >= 4]
        self.assertGreaterEqual(len(texts), 6)
        for text in texts + ["要找的客户代号：lotus"]:
            encoded = text.lower().encode("utf-8")
            self.assertNotIn(encoded, folded, text)
            for start in range(len(text) - 3):
                piece = text[start:start + 4].lower().encode("utf-8")
                self.assertNotIn(piece, folded, (text, piece))
        # the facts and the todo lines are all still there for the checks
        self.assertEqual(info.facts, dict(self.FACTS))
        self.assertEqual(info.todo[0], "要找的客户代号：lotus")

    def test_a_grep_in_the_scenario_folder_finds_nothing_in_the_marker(self):
        info = self.build()
        (info.path / "orders").mkdir()
        (info.path / "orders" / "a.txt").write_text("LOTUS 一箱\n", encoding="utf-8")
        done = subprocess.run(["grep", "-rin", "lotus", "."], cwd=str(info.path),
                              capture_output=True, check=False)
        lines = done.stdout.decode("utf-8").splitlines()
        self.assertEqual(lines, ["./orders/a.txt:1:LOTUS 一箱"])

    def test_the_marker_says_what_it_is_and_that_it_is_not_a_secret(self):
        info = self.build()
        stored = json.loads((info.path / ".playground").read_text(encoding="utf-8"))
        self.assertEqual(next(iter(stored)), "note")
        self.assertEqual(stored["marker"], scenario.MARKER_VERSION)
        self.assertEqual(stored["marker"], 2)
        self.assertNotIn("facts", stored)
        self.assertNotIn("todo", stored)
        # base64 of UTF-8 JSON: anyone can read it back, it is not a secret
        raw = base64.b64decode(stored["data"])
        if stored.get("mask"):
            raw = bytes(b ^ stored["mask"] for b in raw)
        self.assertEqual(json.loads(raw.decode("utf-8"))["facts"], dict(self.FACTS))

    def test_version_1_markers_are_still_read(self):
        folder = self.box.playground / "old"
        folder.mkdir(parents=True)
        (folder / ".playground").write_text(json.dumps({
            "tool": "course.py", "marker": 1, "scenario": "old", "seed": 4, "complete": True,
            "facts": {"repo": "notes-cedar"}, "todo": ["练习仓库：notes-cedar"]},
            ensure_ascii=False), encoding="utf-8")
        info = scenario.read_info(folder)
        self.assertTrue(info.exists)
        self.assertEqual(info.facts, {"repo": "notes-cedar"})
        self.assertEqual(info.todo, ["练习仓库：notes-cedar"])

    def test_a_masked_payload_is_read_back(self):
        raw = json.dumps({"facts": {"a": "lotus"}, "todo": ["x"]}).encode("utf-8")
        data = base64.b64encode(bytes(b ^ 7 for b in raw)).decode("ascii")
        marker = scenario.decode_marker({"complete": True, "data": data, "mask": 7})
        self.assertEqual((marker["facts"], marker["todo"]), ({"a": "lotus"}, ["x"]))

    def test_encode_payload_avoids_fragments_and_round_trips(self):
        facts = {"w": "abcd", "x": "QUJD", "y": "eyJm"}       # "eyJm" starts plain base64 of '{"f'
        data, mask = scenario.encode_payload(facts, ["eyJmYWN0cyI6"])
        self.assertNotIn("eyjm", data.lower())
        self.assertNotIn("abcd", data.lower())
        decoded = scenario.decode_marker({"data": data, "mask": mask})
        self.assertEqual(decoded["facts"], facts)

    def test_a_damaged_payload_is_never_a_finished_build(self):
        folder = self.box.playground / "damaged"
        folder.mkdir(parents=True)
        (folder / ".playground").write_text(json.dumps(
            {"note": "x", "marker": 2, "complete": True, "data": "%%% not base64"}),
            encoding="utf-8")
        info = scenario.read_info(folder)
        self.assertFalse(info.exists)
        self.assertTrue(info.started_complete)       # never rebuilt without --reset
        self.assertEqual(info.facts, {})


class StarterOriginalsTest(unittest.TestCase):
    """P2: builders copy starter material from the manifest, never the learner's copy."""

    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.app = self.box.app()
        # the learner's workspace copy of starter/, edited in the editor
        shutil.copytree(str(helpers.REPO / "starter"), str(self.box.root / "starter"))
        page = self.box.root / "starter" / "my-site" / "index.html"
        page.write_text("<h1>我把原件改坏了</h1>\n", encoding="utf-8")
        (self.box.root / "starter" / "my-site" / "notes.txt").write_text("新加的\n")
        (self.box.root / "starter" / "hello-fx" / "rates.txt").unlink()

    def original(self, rel):
        return (helpers.REPO / rel).read_bytes()

    def test_copy_in_a_folder_uses_the_originals(self):
        def builder(sc):
            sc.copy_in("starter/my-site", "site")
            sc.copy_in("starter/hello-fx", "fx")

        info = scenario.build(self.app, builder, "originals", seed=1)
        self.assertEqual(sorted(os.listdir(str(info.path / "site"))), ["index.html", "style.css"])
        self.assertEqual((info.path / "site" / "index.html").read_bytes(),
                         self.original("starter/my-site/index.html"))
        self.assertEqual((info.path / "fx" / "rates.txt").read_bytes(),
                         self.original("starter/hello-fx/rates.txt"))

    def test_copy_in_one_file_uses_the_original(self):
        info = scenario.build(self.app, lambda sc: sc.copy_in("starter/my-site/index.html",
                                                              "copy/page.html"), "one", seed=1)
        self.assertEqual((info.path / "copy" / "page.html").read_bytes(),
                         self.original("starter/my-site/index.html"))

    def test_a_starter_path_the_manifest_does_not_know_is_a_builder_mistake(self):
        for source in ("starter/my-site/notes.txt", "starter/nothing", "starter/my-sit"):
            with self.assertRaises(ToolTrouble, msg=source) as caught:
                scenario.build(self.app, lambda sc, s=source: sc.copy_in(s, "x"),
                               "bad-" + str(abs(hash(source))), seed=1)
            self.assertIn("原样清单里没有它", caught.exception.summary)

    def test_works_without_any_starter_folder_in_the_workspace(self):
        shutil.rmtree(str(self.box.root / "starter"))
        info = scenario.build(self.app, lambda sc: sc.copy_in("starter/hello-fx", "fx"),
                              "bare", seed=1)
        self.assertEqual(sorted(os.listdir(str(info.path / "fx"))), ["convert.py", "rates.txt"])

    def test_a_broken_manifest_is_a_checker_problem(self):
        broken = self.box.base / "broken.json"
        broken.write_text("{", encoding="utf-8")
        with mock.patch.object(scenario, "STARTER_MANIFEST", broken), \
                self.assertRaises(ToolTrouble) as caught:
            scenario.build(self.app, lambda sc: sc.copy_in("starter/hello-fx", "fx"),
                           "broken", seed=1)
        self.assertIn("原样清单", caught.exception.summary)

    def test_an_entry_whose_checksum_does_not_match_is_refused(self):
        data = scenario.load_starter_manifest()
        data["files"]["starter/my-site/style.css"]["text"] += "/* changed */"
        with self.assertRaises(ToolTrouble):
            scenario.starter_originals("starter/my-site", data)

    def test_differences_name_changed_and_missing_but_never_convert_py(self):
        convert = self.box.root / "starter" / "hello-fx" / "convert.py"
        convert.write_text(convert.read_text(encoding="utf-8").replace("100", "250"),
                           encoding="utf-8")
        found = scenario.starter_differences(self.box.root)
        self.assertEqual(found, [("starter/hello-fx/rates.txt", "missing"),
                                 ("starter/my-site/index.html", "changed")])
        self.assertEqual(scenario.starter_differences(helpers.REPO), [])


class LessonScenarioTest(unittest.TestCase):
    def test_lesson_scenarios_live_in_folders_named_after_their_id(self):
        box = helpers.Sandbox(self)
        box.add_syllabus_lesson("1.6", extra='SCENARIOS["1.6b"] = build_start\n')
        app = box.app()
        lesson = app.catalog().lesson("1.6")
        start = scenario.build_lesson_scenario(app, lesson, "start", seed=1)
        station = scenario.build_lesson_scenario(app, lesson, "1.6b", seed=2)
        self.assertEqual(start.path, box.playground / "1.6-start")
        self.assertEqual(station.path, box.playground / "1.6b")
        self.assertEqual((start.id, start.key, start.lesson), ("1.6-start", "start", "1.6"))
        again = scenario.lesson_scenario_info(app, lesson, "1.6b")
        self.assertEqual((again.seed, again.facts), (2, {"lesson": "1.6"}))


if __name__ == "__main__":
    unittest.main()
