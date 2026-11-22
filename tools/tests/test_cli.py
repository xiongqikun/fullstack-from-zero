"""The entry point: argument parsing, plug-in discovery, exit codes, real processes."""

import os
import select
import shutil
import signal
import subprocess
import sys
import time
import unittest

import helpers

from courselib import cli

COMMANDS = ("status", "check", "hint", "scenario", "review", "exam", "journal", "doctor",
            "fresh", "validate")


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6")

    def test_every_command_is_discovered_and_follows_the_protocol(self):
        found = dict(cli.discover_commands())
        for name in COMMANDS:
            self.assertIn(name, found)
            module = found[name]
            self.assertTrue(callable(module.register) and callable(module.run), name)
        self.assertEqual([name for name, _ in cli.discover_commands()][:len(COMMANDS)],
                         list(COMMANDS))

    def test_help_is_chinese_and_lists_the_commands(self):
        result = self.box.run("-h")
        self.assertEqual(result.code, 0)
        self.assertIn("用法：python3 tools/course.py <命令> [参数]", result.out)
        for name in COMMANDS:
            self.assertIn("\n  " + name, result.out)
        for name in COMMANDS:
            with self.subTest(command=name):
                sub = self.box.run(name, "-h")
                self.assertEqual(sub.code, 0, sub)
                self.assertIn("用法：", sub.out)
                self.assertNotIn("usage:", sub.out)
                self.assertNotIn("show this help", sub.out)

    def test_unknown_words_are_called_option_or_argument(self):
        # E4: lessons call a word that starts with a hyphen 选项 (from 0.2 on).
        self.box.add_syllabus_lesson("1.6")
        for argv, line in ((["status", "--wirte"], "用法不对：不认识的选项：--wirte"),
                           (["status", "-x"], "用法不对：不认识的选项：-x"),
                           (["status", "now"], "用法不对：不认识的参数：now"),
                           (["status", "--wirte", "now"],
                            "用法不对：不认识的选项：--wirte；不认识的参数：now"),
                           (["check", "1.6a", "b"], "用法不对：不认识的参数：b")):
            with self.subTest(argv=argv):
                result = self.box.run(*argv)
                self.assertEqual(result.code, 64, result)
                self.assertEqual(result.err.splitlines()[0], line)

    def test_version(self):
        result = self.box.run("--version")
        self.assertEqual(result.code, 0)
        self.assertIn("课程模块接口第 1 版", result.out)

    def test_usage_errors_exit_64_in_chinese(self):
        for argv, words in ((["nonsense"], "没有 nonsense 这个命令"),
                            (["check"], "缺少必须的参数"),
                            (["check", "1.6a", "--bogus"], "不认识的选项：--bogus"),
                            (["check", "1.6a", "--confidence", "9"], "选项 --confidence 不能是 9"),
                            (["check", "1.6a", "--confidence", "x"], "选项 --confidence 要是一个整数"),
                            (["check", "1.6a", "--confidence"], "选项 --confidence 后面要跟一个值")):
            with self.subTest(argv=argv):
                result = self.box.run(*argv)
                self.assertEqual(result.code, 64, result)
                self.assertIn("用法不对：", result.err)
                self.assertIn(words, result.err)
                self.assertNotIn("Traceback", result.text)

    def test_an_unreadable_course_now_is_a_usage_error(self):
        result = self.box.run("status", COURSE_NOW="next tuesday")
        self.assertEqual(result.code, 64)
        self.assertIn("COURSE_NOW", result.err)

    def test_unfinished_commands_say_so_and_exit_2(self):
        found = dict(cli.discover_commands())
        stubs = [name for name in ("scenario", "review", "exam", "doctor", "fresh")
                 if "not_built" in getattr(found[name], "TEXT", {})]
        for name in stubs:
            with self.subTest(command=name):
                result = self.box.run(name)
                self.assertEqual(result.code, 2)
                self.assertIn("这个命令还在建设中", result.out)


class ProcessTest(unittest.TestCase):
    """``python3 tools/course.py`` as the learner runs it: a separate process."""

    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6")

    def bytecode(self):
        return [str(p) for p in self.box.base.rglob("__pycache__")]

    def test_runs_from_any_folder_and_after_the_workspace_moved(self):
        result = self.box.run_process(cwd=self.box.home)
        self.assertEqual(result.code, 0, result)
        self.assertIn("你在：1.6", result.out)
        self.assertIn("收工前   → python3 tools/course.py journal", result.out)
        self.box.install_tools()
        moved = self.box.base / "moved-workspace"
        shutil.move(str(self.box.root), str(moved))
        done = subprocess.run([sys.executable, str(moved / "tools" / "course.py"), "status"],
                              cwd="/", env=self.box.environment(), capture_output=True,
                              timeout=60, check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("你在：1.6", done.stdout.decode("utf-8"))
        self.assertTrue((moved / "learner" / "state.json").is_file())
        self.assertEqual(self.bytecode(), [])

    def test_python_39(self):
        python = helpers.find_python39()
        if python is None:
            self.skipTest("no Python 3.9 on this machine")
        status = self.box.run_process("status", python=python)
        self.assertEqual(status.code, 0, status)
        self.assertIn("你在：1.6", status.out)
        self.box.flag("1.6a")
        check = self.box.run_process("check", "1.6a", python=python)
        self.assertEqual(check.code, 0, check)
        self.assertIn("✅ 通过", check.out)
        journal = self.box.run_process("journal", "--done", "测试", python=python,
                                       noninteractive=True)
        self.assertEqual(journal.code, 0, journal)
        self.assertEqual(self.bytecode(), [])

    def test_end_of_input_is_polite(self):
        result = self.box.run_process("journal", stdin_text="")
        self.assertEqual(result.code, 1, result)
        self.assertIn("已取消", result.out)
        self.assertNotIn("Traceback", result.text)

    def test_typed_input_is_read(self):
        result = self.box.run_process("journal", stdin_text="读完第一站\n\n\n\n\n")
        self.assertEqual(result.code, 0, result)
        self.assertIn("已记到 journal/2026-11-19.md。", result.out)

    def test_ctrl_c_at_a_prompt_is_polite(self):
        script = self.box.install_tools()
        child = subprocess.Popen([sys.executable, str(script), "journal"],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, env=self.box.environment(),
                                 cwd=str(self.box.base))
        try:
            seen = b""
            deadline = time.time() + 30
            while "做了什么".encode() not in seen and time.time() < deadline:
                ready, _, _ = select.select([child.stdout], [], [], 1)
                if ready:
                    seen += os.read(child.stdout.fileno(), 4096)
            self.assertIn("做了什么".encode(), seen)
            child.send_signal(signal.SIGINT)
            out, err = child.communicate(timeout=30)
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate()
        text = (seen + out).decode("utf-8") + err.decode("utf-8")
        self.assertEqual(child.returncode, 1, text)
        self.assertIn("已取消", text)
        self.assertNotIn("Traceback", text)

    def test_colour_only_on_a_terminal(self):
        result = self.box.run_process("check", "1.6a")
        self.assertNotIn("\033[", result.out)


class PluginIsolationTest(unittest.TestCase):
    """A broken plug-in does not take the other commands down."""

    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6")
        script = self.box.install_tools()
        self.commands = script.parent / "courselib" / "commands"

    def test_a_plugin_that_raises_at_import(self):
        (self.commands / "zz_broken.py").write_text("raise RuntimeError('plug-in bug')\n",
                                                    encoding="utf-8")
        status = self.box.run_process("status")
        self.assertEqual(status.code, 0, status)
        listing = self.box.run_process("-h")
        self.assertIn("zz_broken", listing.out)
        self.assertIn("加载失败", listing.out)
        broken = self.box.run_process("zz_broken", "whatever")
        self.assertEqual(broken.code, 2, broken)
        self.assertIn("检查器出问题", broken.out)
        self.assertIn("命令 zz_broken 的代码加载失败", broken.out)
        self.assertNotIn("Traceback", broken.text)

    def test_a_plugin_without_the_two_functions(self):
        (self.commands / "zz_empty.py").write_text("SUMMARY = 'x'\n", encoding="utf-8")
        self.assertEqual(self.box.run_process("status").code, 0)
        result = self.box.run_process("zz_empty")
        self.assertEqual(result.code, 2)
        self.assertIn("没有提供 register 和 run", result.out)

    def test_a_plugin_whose_run_raises(self):
        (self.commands / "zz_crash.py").write_text(
            "from .. import cmdkit\n"
            "def register(subparsers):\n"
            "    cmdkit.add_command(subparsers, 'zz_crash', '会出错的命令')\n"
            "def run(args):\n"
            "    raise KeyError('secret ' + str(args.app.home))\n", encoding="utf-8")
        result = self.box.run_process("zz_crash")
        self.assertEqual(result.code, 2)
        self.assertIn("检查器出问题", result.out)
        self.assertIn("这不是你的错", result.out)
        self.assertNotIn("Traceback", result.text)
        self.assertNotIn(str(self.box.home), result.text)
        debug = self.box.run_process("zz_crash", COURSE_DEBUG="1")
        self.assertIn("Traceback", debug.err)


if __name__ == "__main__":
    unittest.main()
