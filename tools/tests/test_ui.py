"""Console helpers: colours, prompts, CJK-aware padding."""

import io
import unittest

import helpers  # noqa: F401 - puts tools/ on sys.path

from courselib import ui
from courselib.errors import Cancelled, UsageProblem


class Tty(io.StringIO):
    def isatty(self):
        return True


class ColourTest(unittest.TestCase):
    def test_colour_only_on_a_terminal_and_without_no_color(self):
        self.assertTrue(ui.wants_color(Tty(), {}))
        self.assertFalse(ui.wants_color(io.StringIO(), {}))
        self.assertFalse(ui.wants_color(Tty(), {"NO_COLOR": "1"}))
        self.assertFalse(ui.wants_color(Tty(), {"NO_COLOR": "anything"}))
        self.assertTrue(ui.wants_color(Tty(), {"NO_COLOR": ""}))
        self.assertFalse(ui.wants_color(Tty(), {"TERM": "dumb"}))

    def test_paint(self):
        plain = ui.Console(out=io.StringIO(), color=False)
        self.assertEqual(plain.paint("通过", "ok"), "通过")
        coloured = ui.Console(out=io.StringIO(), color=True)
        self.assertEqual(coloured.paint("通过", "ok"), "\033[32m通过\033[0m")
        self.assertEqual(coloured.paint("x", "unknown"), "x")


class ReadTest(unittest.TestCase):
    def console(self, text, can_prompt=True):
        out = io.StringIO()
        return ui.Console(out=out, err=out, stdin=io.StringIO(text), can_prompt=can_prompt,
                          is_tty=False), out

    def test_reads_one_line_without_its_end(self):
        console, out = self.console("你好\r\n下一行\n")
        self.assertEqual(console.read("问："), "你好")
        self.assertEqual(console.read("问："), "下一行")
        self.assertEqual(out.getvalue(), "问：问：")

    def test_end_of_file_cancels(self):
        console, out = self.console("")
        with self.assertRaises(Cancelled):
            console.read("问：")
        self.assertTrue(out.getvalue().endswith("\n"))

    def test_ctrl_c_cancels(self):
        def reader(prompt):
            raise KeyboardInterrupt()
        console = ui.Console(out=io.StringIO(), reader=reader)
        with self.assertRaises(Cancelled):
            console.read("问：")

    def test_no_prompt_mode_never_waits(self):
        console, _ = self.console("y\n", can_prompt=False)
        with self.assertRaises(UsageProblem):
            console.read("问：")
        self.assertFalse(console.may_ask_optional)

    def test_confirm_needs_an_explicit_yes(self):
        for typed, expected in (("y", True), ("Ｙ", True), ("是", True), ("好的", True),
                                ("", False), ("n", False), ("不", False)):
            console, _ = self.console(typed + "\n")
            self.assertEqual(console.confirm("看吗？"), expected, typed)

    def test_optional_questions_only_for_a_person_at_a_terminal(self):
        self.assertTrue(ui.Console(out=io.StringIO(), is_tty=True).may_ask_optional)
        self.assertFalse(ui.Console(out=io.StringIO(), is_tty=False).may_ask_optional)
        self.assertFalse(ui.Console(out=io.StringIO(), is_tty=True,
                                    can_prompt=False).may_ask_optional)


class TextTest(unittest.TestCase):
    def test_display_width_counts_cjk_as_two(self):
        self.assertEqual(ui.display_width("abc"), 3)
        self.assertEqual(ui.display_width("通过"), 4)
        self.assertEqual(ui.display_width("１.６"), 5)
        self.assertEqual(ui.pad("通过", 6), "通过  ")
        self.assertEqual(ui.pad("toolong", 3), "toolong")

    def test_one_line_indent_bullets_and_tutor_box(self):
        self.assertEqual(ui.one_line(" a \n b\t c "), "a b c")
        self.assertEqual(ui.one_line("一二三四五", limit=4), "一二三…")
        self.assertEqual(ui.indent("a\n\nb", 2), "  a\n\n  b")
        self.assertEqual(ui.bullets(["一", "二\n续"]), "    - 一\n    - 二\n      续")
        box = ui.tutor_box(["问题：x"])
        self.assertIn("发给导师", box)
        self.assertIn("│ 问题：x", box)


if __name__ == "__main__":
    unittest.main()
