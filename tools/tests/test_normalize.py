"""Normalisation of learner answers: trim, full-width to half-width, case."""

import re
import unittest

import helpers  # noqa: F401  (sets up sys.path)
from courselib import normalize as n


class NormalizeTest(unittest.TestCase):
    def test_trims_and_collapses_spaces(self):
        self.assertEqual(n.normalize("  git   status \n"), "git status")

    def test_full_width_becomes_half_width(self):
        self.assertEqual(n.normalize("ｇｉｔ　ｓｔａｔｕｓ"), "git status")
        self.assertEqual(n.normalize("１２３"), "123")
        self.assertEqual(n.normalize("ｄｏｃｓ：说明"), "docs:说明")

    def test_case_is_folded_unless_asked(self):
        self.assertEqual(n.normalize("README.md"), "readme.md")
        self.assertEqual(n.normalize("README.md", case=False), "README.md")

    def test_one_pair_of_wrapping_quotes_is_removed(self):
        for wrapped in ('"main"', "'main'", "`main`", "“main”", "「main」"):
            self.assertEqual(n.normalize(wrapped), "main", wrapped)
        self.assertEqual(n.normalize('"main"', quotes=False), '"main"')
        self.assertEqual(n.normalize('say "hi" now'), 'say "hi" now')

    def test_trailing_chinese_full_stop_is_dropped(self):
        self.assertEqual(n.normalize("main。"), "main")
        self.assertEqual(n.normalize(".."), "..")

    def test_empty_and_non_string_input(self):
        self.assertEqual(n.normalize(""), "")
        self.assertEqual(n.normalize(42), "42")


class ParseIntTest(unittest.TestCase):
    def test_plain_and_full_width_digits(self):
        self.assertEqual(n.parse_int("3"), 3)
        self.assertEqual(n.parse_int(" ３ "), 3)
        self.assertEqual(n.parse_int("-2"), -2)

    def test_number_with_measure_word(self):
        self.assertEqual(n.parse_int("3个"), 3)
        self.assertEqual(n.parse_int("3 个文件"), 3)
        self.assertEqual(n.parse_int("一共 12 行"), 12)

    def test_chinese_numerals(self):
        cases = {"三": 3, "两个": 2, "十": 10, "十二": 12, "二十": 20, "四十五": 45, "零": 0,
                 "三个文件": 3}
        for text, value in cases.items():
            self.assertEqual(n.parse_int(text), value, text)

    def test_no_number_or_ambiguous(self):
        for text in ("", "很多", "3 或 4", "3.5", "1.6a", "一个也没有", "没有"):
            self.assertIsNone(n.parse_int(text), text)


class ChoiceTest(unittest.TestCase):
    def test_accepted_spellings(self):
        for text in ("b", "B", "Ｂ", " b ", "B.", "(b)", "选 B", "选B", "答案是 b", "b项"):
            self.assertEqual(n.choice_letter(text, 3), 1, text)

    def test_out_of_range_or_not_a_letter(self):
        for text in ("d", "", "bb", "2", "乙"):
            self.assertIsNone(n.choice_letter(text, 3), text)

    def test_letter_index_round_trip(self):
        self.assertEqual(n.letter_to_index("A"), 0)
        self.assertEqual(n.letter_to_index("c"), 2)
        self.assertIsNone(n.letter_to_index(1))
        self.assertIsNone(n.letter_to_index("AB"))
        self.assertEqual(n.index_to_letter(3), "D")


class MatchesTest(unittest.TestCase):
    def test_string_is_compared_after_normalisation(self):
        self.assertTrue(n.matches(" ＭＡＩＮ ", "main"))
        self.assertTrue(n.matches("“index.html”", "index.html"))
        self.assertFalse(n.matches("master", "main"))

    def test_int_expects_exactly_that_number(self):
        self.assertTrue(n.matches("３ 个", 3))
        self.assertTrue(n.matches("三", 3))
        self.assertFalse(n.matches("4", 3))
        self.assertFalse(n.matches("", 3))

    def test_any_of_a_list(self):
        self.assertTrue(n.matches("q", ["q", "按 q"]))
        self.assertTrue(n.matches("2", (2, "两个")))
        self.assertFalse(n.matches("x", ["q", "quit"]))

    def test_regular_expression_must_match_whole_answer(self):
        pattern = re.compile(r"[0-9a-f]{7}")
        self.assertTrue(n.matches("A1B2C3D", pattern))
        self.assertFalse(n.matches("a1b2c3d4", pattern))

    def test_function_gets_the_normalised_answer(self):
        seen = []
        self.assertTrue(n.matches("  Ｈello ", lambda s: seen.append(s) or s == "hello"))
        self.assertEqual(seen, ["hello"])

    def test_unsupported_expected_values_raise(self):
        with self.assertRaises(TypeError):
            n.matches("yes", True)
        with self.assertRaises(TypeError):
            n.matches("1.5", 1.5)


if __name__ == "__main__":
    unittest.main()
