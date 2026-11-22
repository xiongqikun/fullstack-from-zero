"""The ``scenario`` command (plan I4): building practice states safely.

Every test runs in a throw-away sandbox under $TMPDIR with COURSE_PLAYGROUND
pointing into it.  What is checked here is the command as the learner meets
it: the output, the exit codes and, above all, the safety rules.
"""

import os
import shutil
import subprocess
import unittest

import helpers
from test_states import make_hostile_home, plain_commit_fails

from courselib import scenario
from courselib.gitread import GitReader, GitRepo

STATION_SCENARIOS = '''
def build_broken(sc):
    sc.write("notes/a.txt", "一")
    sc.fact("kind", "broken")


SCENARIOS["1.6b-broken"] = build_broken
SCENARIOS["../escape"] = build_broken
SCENARIOS["hop/inner"] = build_broken


def build_outside(sc):
    sc.write("../../outside.txt", "不该出现")


SCENARIOS["1.6c"] = build_outside
'''

SITE_START = '''
def build_site(sc):
    site = sc.site_before()
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))


SCENARIOS["start"] = build_site
'''


class ScenarioCommandTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        shutil.copytree(str(helpers.REPO / "starter"), str(self.box.root / "starter"))
        self.box.add_syllabus_lesson("1.6", extra=STATION_SCENARIOS)
        self.box.add_syllabus_lesson("1.7", extra=SITE_START)
        self.playground = self.box.base / "pg"
        self.box.env["COURSE_PLAYGROUND"] = str(self.playground)
        self.outside = self.box.base / "outside"
        self.outside.mkdir()

    def run_tool(self, *argv, **extra):
        return self.box.run("scenario", *argv, **extra)

    def marker(self, folder):
        return scenario.read_marker(folder)

    # -- the normal case --------------------------------------------------------
    def test_builds_and_says_where_and_what_next(self):
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 0, result)
        folder = self.playground / "1.6-start"
        self.assertEqual((folder / "hello.txt").read_text(encoding="utf-8"), "你好\n")
        self.assertTrue(self.marker(folder)["complete"])
        self.assertIn("练习场景 1.6-start 搭好了", result.out)
        self.assertIn("位置：" + str(folder), result.out)
        self.assertIn("cd " + str(folder), result.out)
        # A start scenario names no station: which station looks at the start
        # state is the lesson's business, so the learner is sent to the text.
        self.assertIn("接着按课文往下做", result.out)
        self.assertNotIn("course.py check", result.out)
        self.assertIn("cd " + str(self.box.root), result.out)
        self.assertNotIn("Traceback", result.text)
        self.assertEqual(self.box.events("scenario-built")[0]["scenario"], "1.6-start")
        self.assertTrue(self.box.state()["sessions"])        # counted as study time

    def test_start_and_station_ids(self):
        self.assertEqual(self.run_tool("1.6-start").code, 0)
        result = self.run_tool("1.6B-BROKEN")                  # typed ids are normalised
        self.assertEqual(result.code, 0, result)
        self.assertTrue((self.playground / "1.6b-broken" / "notes" / "a.txt").is_file())
        self.assertIn("check 1.6b", result.out)

    def test_a_todo_line_with_its_own_cd_replaces_the_tools_cd_step(self):
        self.box.add_syllabus_lesson("1.8", extra=(
            "\ndef build_deep(sc):\n"
            "    sc.write('notes/a.txt', '一')\n"
            "    sc.todo('先进入练习仓库：cd ' + sc.show('notes'))\n"
            "\n\nSCENARIOS['start'] = build_deep\n"))
        result = self.run_tool("1.8")
        self.assertEqual(result.code, 0, result)
        folder = self.playground / "1.8-start"
        self.assertIn("cd " + str(folder / "notes"), result.out)
        self.assertNotIn("进入练习场景：cd", result.out)       # one cd line, not two
        self.assertIn("接着按课文往下做", result.out)

    def test_cd_line_is_quoted_when_the_path_has_a_space(self):
        self.box.env["COURSE_PLAYGROUND"] = str(self.box.base / "my practice")
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 0, result)
        self.assertIn("cd '{}'".format(self.box.base / "my practice" / "1.6-start"), result.out)

    def test_cd_line_keeps_the_home_shortcut(self):
        del self.box.env["COURSE_PLAYGROUND"]
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 0, result)
        self.assertIn("cd ~/Developer/playground/1.6-start\n", result.out)

    def test_the_rebuild_command_is_printed_in_full_with_the_id_typed(self):
        # G4: no half sentence 「改乱了就加 --reset」; the whole command, ready to copy.
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 0, result)
        self.assertIn("练习场里的东西随便改，练习场外面的文件不会受影响。\n"
                      "改乱了可以重搭一份：python3 tools/course.py scenario 1.6 --reset\n", result.out)
        self.assertNotIn("就加 --reset", result.out)
        station = self.run_tool("1.6B-BROKEN")
        self.assertIn("改乱了可以重搭一份：python3 tools/course.py scenario 1.6b-broken --reset",
                      station.out)
        typed_start = self.run_tool("1.6-start", "--reset")
        self.assertIn("改乱了可以重搭一份：python3 tools/course.py scenario 1.6-start --reset",
                      typed_start.out)
        again = self.run_tool("1.6")
        self.assertEqual(again.code, 0, again)
        self.assertIn("想从头再来一份（会删掉你在里面做过的改动）："
                      "python3 tools/course.py scenario 1.6 --reset", again.out)
        self.assertNotIn("在命令后面加上", again.out)

    def test_listing_and_unknown_ids(self):
        listing = self.run_tool()
        self.assertEqual(listing.code, 0)
        self.assertIn("1.6-start", listing.out)
        self.assertIn("1.6b-broken", listing.out)
        unknown = self.run_tool("1.6z")
        self.assertEqual(unknown.code, 64)
        self.assertIn("没有「1.6z」这个练习场景", unknown.err)
        self.assertIn("1.6-start", unknown.err)
        self.assertEqual(self.run_tool("9.9").code, 64)
        self.assertFalse(self.playground.exists())

    def test_a_broken_lesson_is_a_tool_problem(self):
        self.box.add_lesson("META = {\n", "01-foundations", "08-undo-uncommitted")
        result = self.run_tool("1.8")
        self.assertEqual(result.code, 2, result)
        self.assertIn("检查器出问题", result.out)
        self.assertNotIn("Traceback", result.text)

    # -- not overwriting ----------------------------------------------------------
    def test_second_run_without_reset_keeps_the_learners_work(self):
        self.run_tool("1.6")
        work = self.playground / "1.6-start" / "mine.txt"
        work.write_text("我的改动", encoding="utf-8")
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 0, result)
        self.assertIn("之前已经搭好了", result.out)
        self.assertIn("--reset", result.out)
        self.assertTrue(work.is_file())
        self.assertEqual(len(self.box.events("scenario-built")), 1)

    def test_reset_rebuilds_a_folder_the_tool_built(self):
        self.run_tool("1.6", "--seed", "1")
        work = self.playground / "1.6-start" / "mine.txt"
        work.write_text("我的改动", encoding="utf-8")
        result = self.run_tool("1.6", "--reset", "--seed", "2")
        self.assertEqual(result.code, 0, result)
        self.assertIn("重新搭好了", result.out)
        self.assertFalse(work.exists())
        self.assertEqual(self.marker(self.playground / "1.6-start")["seed"], 2)

    def test_refuses_a_non_empty_folder_without_reset(self):
        folder = self.playground / "1.6-start"
        folder.mkdir(parents=True)
        (folder / "keep.txt").write_text("别动", encoding="utf-8")
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 1, result)
        self.assertIn("已经有一个文件夹了，而且不是工具搭的", result.out)
        # a folder without the marker is never offered a --reset that would
        # then be refused (tester novice-abuse)
        self.assertNotIn("--reset", result.out)
        self.assertEqual(os.listdir(str(folder)), ["keep.txt"])

    def test_reset_refuses_a_folder_without_the_marker(self):
        folder = self.playground / "1.6-start"
        folder.mkdir(parents=True)
        (folder / "keep.txt").write_text("别动", encoding="utf-8")
        result = self.run_tool("1.6", "--reset")
        self.assertEqual(result.code, 1, result)
        self.assertIn(".playground", result.out)
        self.assertEqual((folder / "keep.txt").read_text(encoding="utf-8"), "别动")

    def test_reset_refuses_a_half_marker_left_as_a_link(self):
        folder = self.playground / "1.6-start"
        folder.mkdir(parents=True)
        real_marker = self.outside / "marker"
        real_marker.write_text("{}", encoding="utf-8")
        os.symlink(str(real_marker), str(folder / ".playground"))
        (folder / "keep.txt").write_text("别动", encoding="utf-8")
        self.assertEqual(self.run_tool("1.6", "--reset").code, 1)
        self.assertTrue((folder / "keep.txt").is_file())
        self.assertTrue(real_marker.is_file())

    # -- never outside the playground ---------------------------------------------
    def test_reset_refuses_a_link_that_leads_outside_even_with_a_marker(self):
        victim = self.outside / "victim"
        victim.mkdir()
        (victim / ".playground").write_text('{"complete": true}', encoding="utf-8")
        (victim / "precious.txt").write_text("不能删", encoding="utf-8")
        self.playground.mkdir(parents=True)
        os.symlink(str(victim), str(self.playground / "1.6-start"))
        for argv in (("1.6",), ("1.6", "--reset")):
            result = self.run_tool(*argv)
            self.assertEqual(result.code, 1, result)
            self.assertTrue((victim / "precious.txt").is_file())
            self.assertTrue((victim / ".playground").is_file())
        self.assertTrue("不在练习场里面" in result.out or "链接" in result.out, result.out)

    def test_refuses_an_intermediate_link_out_of_the_playground(self):
        self.playground.mkdir(parents=True)
        os.symlink(str(self.outside), str(self.playground / "hop"))
        result = self.run_tool("hop/inner")
        self.assertEqual(result.code, 1, result)
        self.assertIn("不在练习场里面", result.out)
        self.assertEqual(os.listdir(str(self.outside)), [])

    def test_refuses_dot_dot_in_a_scenario_id(self):
        result = self.run_tool("../escape")
        self.assertEqual(result.code, 1, result)
        self.assertIn("不在练习场里面", result.out)
        self.assertFalse((self.box.base / "escape").exists())

    def test_refuses_a_playground_that_climbs_out_with_dot_dot(self):
        self.box.env["COURSE_PLAYGROUND"] = str(self.box.home / "Developer" / "playground" / ".." / "..")
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 1, result)
        self.assertIn("练习场的位置不安全", result.out)
        self.assertFalse((self.box.home / "1.6-start").exists())

    def test_refuses_a_playground_that_is_a_link_to_the_home_folder(self):
        os.symlink(str(self.box.home), str(self.box.base / "sneaky"))
        self.box.env["COURSE_PLAYGROUND"] = str(self.box.base / "sneaky")
        result = self.run_tool("1.6")
        self.assertEqual(result.code, 1, result)
        self.assertIn("练习场的位置不安全", result.out)
        self.assertFalse((self.box.home / "1.6-start").exists())

    def test_a_builder_cannot_write_outside_its_folder(self):
        result = self.run_tool("1.6c")
        self.assertEqual(result.code, 2, result)
        self.assertIn("检查器出问题", result.out)
        self.assertFalse((self.box.base / "outside.txt").exists())
        self.assertFalse((self.playground / "outside.txt").exists())
        self.assertNotIn("Traceback", result.text)
        # the half-built folder carries the marker, so --reset may rebuild it
        self.assertFalse(self.marker(self.playground / "1.6c")["complete"])

    # -- Git on a machine where plain "git commit" fails ---------------------------
    def test_site_copy_builds_in_a_home_where_plain_commit_fails(self):
        home, env = make_hostile_home(self.box.base / "sim")
        self.assertTrue(plain_commit_fails(env, self.box.base / "sim" / "probe"))
        self.box.env.update({"HOME": str(home), "PATH": env["PATH"]})
        self.box.env.pop("GIT_CONFIG_NOSYSTEM", None)
        before = (home / ".gitconfig").read_bytes()
        result = self.run_tool("1.7")
        self.assertEqual(result.code, 0, result)
        site = self.playground / "1.7-start" / "my-site"
        repo = GitRepo(site, GitReader(dict(self.box.env)))
        self.assertTrue(repo.is_repo)
        self.assertEqual(repo.commit_count(), 2)
        self.assertTrue(repo.is_clean())
        self.assertIn("网站的副本在这里：" + str(site), result.out)
        facts = self.marker(self.playground / "1.7-start")["facts"]
        self.assertEqual((facts["site_state"], facts["site_commits"]), ("S4", 2))
        self.assertEqual((home / ".gitconfig").read_bytes(), before)
        self.assertFalse((home / "Developer" / "my-site").exists())

    def test_runs_as_a_child_process_on_python_39(self):
        python = helpers.find_python39()
        if python is None:
            self.skipTest("no Python 3.9 on this machine")
        result = self.box.run_process("scenario", "1.7", python=python)
        self.assertEqual(result.code, 0, result)
        site = self.playground / "1.7-start" / "my-site"
        log = subprocess.run(["git", "log", "--oneline"], cwd=str(site), capture_output=True,
                             env=self.box.environment(), check=True).stdout
        self.assertEqual(len(log.splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
