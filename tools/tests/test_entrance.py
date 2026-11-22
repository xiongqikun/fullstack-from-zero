"""E1: the entrance ``~/Developer/fullstack-from-zero`` (COMMON section 6).

A learner who keeps the course folder where it is gets a symbolic link
``~/Developer/fullstack-from-zero`` that leads to it.  The tool shows the workspace
(and every path inside it) through that path whenever it leads there, also
when the tool was started from the real folder; in every other case it shows
the real path with ``~``.  Real symbolic links, no mocks.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import envstubs
import helpers

from courselib.app import App

SIM = envstubs.make_sim_home


class Layout:
    """A home with the course folder at ~/Desktop/Code/fullstack-from-zero (a folder that was never moved)."""

    def __init__(self, test):
        self.base = Path(os.path.realpath(tempfile.mkdtemp(prefix="course-entrance-")))
        test.addCleanup(__import__("shutil").rmtree, str(self.base), True)
        self.home = self.base / "home"
        self.real = self.home / "Desktop" / "Code" / "fullstack-from-zero"
        (self.real / "stages").mkdir(parents=True)
        (self.home / "Developer").mkdir(parents=True)
        self.entrance = self.home / "Developer" / "fullstack-from-zero"

    def app(self, root=None, home=None):
        return App(root or self.real, env={"HOME": str(home or self.home), "PATH": "/usr/bin:/bin"})


class AppShowTest(unittest.TestCase):
    def setUp(self):
        self.layout = Layout(self)

    def test_through_the_entrance(self):
        self.layout.entrance.symlink_to(self.layout.real)
        app = self.layout.app()
        self.assertEqual(app.entrance_kind(), "link")
        self.assertEqual(app.show(app.root), "~/Developer/fullstack-from-zero")
        self.assertEqual(app.show(app.root / "stages" / "x.md"), "~/Developer/fullstack-from-zero/stages/x.md")
        # the same paths spelled through the link, or with HOME reached through a link
        self.assertEqual(app.show(self.layout.entrance / "notes"), "~/Developer/fullstack-from-zero/notes")
        # the real place on request (doctor says where the folder is)
        self.assertEqual(app.show(app.root, entrance=False), "~/Desktop/Code/fullstack-from-zero")
        # paths outside the workspace are not touched
        self.assertEqual(app.show(self.layout.home / "Desktop" / "Code"), "~/Desktop/Code")
        self.assertEqual(app.show(self.layout.home / "Desktop" / "Code" / "fullstack-from-zero-old"),
                         "~/Desktop/Code/fullstack-from-zero-old")

    def test_started_through_the_link_or_with_an_unresolved_home(self):
        self.layout.entrance.symlink_to(self.layout.real)
        app = self.layout.app(root=self.layout.entrance)
        self.assertEqual(app.show(app.root / "tools"), "~/Developer/fullstack-from-zero/tools")
        # macOS: /tmp is a link to /private/tmp; a home spelled through it still works
        spelled = Path("/tmp") / self.layout.base.relative_to("/private/tmp") / "home" \
            if str(self.layout.base).startswith("/private/tmp/") else self.layout.home
        app = self.layout.app(home=spelled)
        self.assertEqual(app.show(self.layout.real), "~/Developer/fullstack-from-zero")

    def test_no_entrance_shows_the_real_place(self):
        app = self.layout.app()
        self.assertEqual(app.entrance_kind(), "missing")
        self.assertEqual(app.show(app.root), "~/Desktop/Code/fullstack-from-zero")

    def test_a_broken_link(self):
        self.layout.entrance.symlink_to(self.layout.base / "nowhere")
        app = self.layout.app()
        self.assertEqual(app.entrance_kind(), "broken")
        self.assertEqual(app.show(app.root), "~/Desktop/Code/fullstack-from-zero")

    def test_a_link_to_another_folder(self):
        other = self.layout.base / "other"
        other.mkdir()
        self.layout.entrance.symlink_to(other)
        app = self.layout.app()
        self.assertEqual(app.entrance_kind(), "broken")
        self.assertEqual(app.show(app.root / "stages"), "~/Desktop/Code/fullstack-from-zero/stages")

    def test_a_half_finished_move(self):
        (self.layout.entrance / "stages").mkdir(parents=True)      # a real, different folder
        app = self.layout.app()
        self.assertEqual(app.entrance_kind(), "other")
        self.assertEqual(app.show(app.root), "~/Desktop/Code/fullstack-from-zero")

    def test_a_learner_who_moved(self):
        moved = self.layout.entrance
        (moved / "stages").mkdir(parents=True)
        app = self.layout.app(root=moved)
        self.assertEqual(app.entrance_kind(), "workspace")
        self.assertEqual(app.show(moved / "stages"), "~/Developer/fullstack-from-zero/stages")


class EntranceCommandsTest(unittest.TestCase):
    """The commands that print the workspace path, in a sandbox with a real link."""

    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6", extra=(
            "\ndef _build(sc):\n    sc.write('a.txt', 'a')\n\n\n"
            "SCENARIOS = {'1.6a': _build}\n"))

    def test_scenario_prints_cd_through_the_entrance(self):
        before = self.box.run("scenario", "1.6a")
        self.assertEqual(before.code, 0, before)
        self.assertIn("cd " + str(self.box.root), before.out)        # no entrance: real path
        (self.box.home / "Developer" / "fullstack-from-zero").symlink_to(self.box.root)
        self.box.run("scenario", "1.6a", "--reset")
        after = self.box.run("scenario", "1.6a")
        self.assertIn("cd ~/Developer/fullstack-from-zero", after.out)
        self.assertNotIn(str(self.box.root), after.out)


class SimHomeStayTest(unittest.TestCase):
    """``make_sim_home.py --stay``: the layout of a learner who stayed, end to end."""

    def setUp(self):
        self.target = Path(tempfile.mkdtemp(prefix="sim-stay-")) / "sim"
        self.addCleanup(__import__("shutil").rmtree, str(self.target.parent), True)
        # a small workspace: the tool and one lesson
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6")
        self.box.install_tools()

    def test_layout_and_what_the_tool_shows(self):
        info = SIM.make_sim_home(self.target, workspace=self.box.root, stay=True)
        home = Path(info["home"])
        entrance = home / "Developer" / "fullstack-from-zero"
        self.assertEqual(info["entrance"], str(entrance))
        self.assertTrue(entrance.is_symlink())
        self.assertEqual(Path(info["workspace"]), home / "Desktop" / "Code" / "fullstack-from-zero")
        self.assertEqual(os.path.realpath(str(entrance)), os.path.realpath(info["workspace"]))
        state = json.loads((Path(info["workspace"]) / "learner" / "state.json").read_text())
        self.assertEqual(state["decisions"], {"workspace_location": "stay-in-sync"})
        self.assertEqual(SIM.export_lines(info)[-1], "cd " + str(entrance))
        env = {"HOME": str(home), "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
               "PYTHONDONTWRITEBYTECODE": "1", "COURSE_NOW": helpers.NOW,
               "COURSE_NONINTERACTIVE": "1", "GIT_CONFIG_NOSYSTEM": "1"}
        done = subprocess.run([sys.executable, "tools/course.py", "doctor"], cwd=str(entrance),
                              env=env, capture_output=True, check=False, timeout=120)
        out = done.stdout.decode("utf-8")
        self.assertEqual(done.returncode, 0, out + done.stderr.decode("utf-8"))
        line = next(text for text in out.splitlines() if "学习工作区的位置：" in text)
        self.assertIn("学习工作区的位置：~/Desktop/Code/fullstack-from-zero，", line)
        self.assertIn("~/Developer/fullstack-from-zero 是通往它的入口", line)

    def test_stay_needs_a_copy(self):
        with self.assertRaises(SIM.Refusal):
            SIM.make_sim_home(self.target, workspace=self.box.root, copy=False, stay=True)


if __name__ == "__main__":
    unittest.main()
