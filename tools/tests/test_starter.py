"""Practice material of plan I6: starter/hello-fx and starter/my-site."""

import html.parser
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import helpers

STARTER = helpers.REPO / "starter"
EXPECTED_LINE = "100 美元 ≈ 710.00 人民币（按 1 美元 = 7.10 人民币计算）"


def run_convert(python):
    """Run a copy of convert.py (so no __pycache__ can appear in the workspace)."""
    folder = tempfile.mkdtemp(prefix="course-starter-")
    try:
        shutil.copy(str(STARTER / "hello-fx" / "convert.py"), folder)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", LANG="C.UTF-8")
        return subprocess.run([python, "convert.py"], cwd=folder, env=env,
                              capture_output=True, timeout=60, check=False)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


class HelloFxTest(unittest.TestCase):
    def test_prints_exactly_one_line(self):
        for python in filter(None, [sys.executable, helpers.find_python39()]):
            with self.subTest(python=python):
                done = run_convert(python)
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(done.stdout.decode("utf-8"), EXPECTED_LINE + "\n")
                self.assertEqual(done.stderr, b"")

    def test_small_standard_library_only_constants_on_top(self):
        text = (STARTER / "hello-fx" / "convert.py").read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertLessEqual(len(lines), 20)
        self.assertNotIn("import", text)
        self.assertIn("示例数字", text)
        constants = [i for i, line in enumerate(lines) if line.startswith(("AMOUNT_USD", "USD_TO_CNY"))]
        first_def = next(i for i, line in enumerate(lines) if line.startswith("def "))
        self.assertEqual(len(constants), 2)
        self.assertTrue(all(i < first_def for i in constants))

    def test_rates_file_is_labelled_example_data(self):
        lines = (STARTER / "hello-fx" / "rates.txt").read_text(encoding="utf-8").splitlines()
        self.assertTrue(8 <= len(lines) <= 14, len(lines))
        self.assertTrue(lines[0].startswith("#") and "示例" in lines[0] and "不是真实汇率" in lines[0])
        rows = [line.split() for line in lines if line and not line.startswith("#")]
        self.assertGreaterEqual(len(rows), 6)
        self.assertTrue(all(len(row) == 3 and row[0].isupper() and len(row[0]) == 3 for row in rows))
        self.assertIn(["CNY", "人民币", "7.10"], rows)
        for row in rows:
            float(row[2])


class _Collector(html.parser.HTMLParser):
    VOID = {"meta", "link", "br", "img", "input", "hr"}

    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.tags = []
        self.attrs = {}
        self.stack = []
        self.text = {}
        self.decl = ""
        self.errors = []

    def handle_decl(self, decl):
        self.decl = decl

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.setdefault(tag, []).append(dict(attrs))
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}>")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack:
            self.text.setdefault(self.stack[-1], []).append(data.strip())


class MySiteTest(unittest.TestCase):
    def test_index_html(self):
        text = (STARTER / "my-site" / "index.html").read_text(encoding="utf-8")
        self.assertTrue(20 <= len(text.splitlines()) <= 32)
        page = _Collector()
        page.feed(text)
        page.close()
        self.assertEqual(page.errors, [])
        self.assertEqual(page.stack, [])
        self.assertEqual(page.decl.lower(), "doctype html")
        self.assertEqual(page.attrs["html"][0].get("lang"), "zh-CN")
        self.assertEqual(page.attrs["meta"][0].get("charset"), "utf-8")
        self.assertEqual(page.tags.count("h1"), 1)
        self.assertIn("____", "".join(page.text["h1"]))
        self.assertEqual(page.tags.count("p"), 1)
        self.assertEqual(page.tags.count("ul"), 1)
        self.assertEqual(page.tags.count("li"), 3)
        self.assertEqual(page.tags.count("a"), 1)
        self.assertTrue(page.attrs["a"][0]["href"].startswith("https://"))
        self.assertIn({"rel": "stylesheet", "href": "style.css"}, page.attrs["link"])
        self.assertTrue(page.text.get("title"))

    def test_style_css(self):
        text = (STARTER / "my-site" / "style.css").read_text(encoding="utf-8")
        self.assertTrue(8 <= len(text.splitlines()) <= 16)
        self.assertEqual(text.count("{"), text.count("}"))
        self.assertIn("body", text)

    def test_text_files_are_utf8_with_lf_and_a_final_newline(self):
        for path in sorted(STARTER.rglob("*")):
            if path.is_file():
                with self.subTest(path=path.name):
                    data = path.read_bytes()
                    data.decode("utf-8")
                    self.assertNotIn(b"\r\n", data)
                    self.assertTrue(data.endswith(b"\n") and not data.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
