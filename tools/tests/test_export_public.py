"""tools/dev/export_public.py: which files go into the public copy, and the privacy check.

Every test that writes works under $TMPDIR; the real workspace is only read.
"""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import helpers

_SPEC = importlib.util.spec_from_file_location(
    "export_public", str(helpers.TOOLS / "dev" / "export_public.py"))
EXPORT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(EXPORT)

WORKSPACE = helpers.TOOLS.parent
# Built from pieces so that this file itself never trips the check it tests.
TERM = "Zebra" + "corn-7781"
USER = "zzquiet" + "user"
HOME = "/Users/" + USER
ADDRESS = "someone" + "@" + "realmail.test"


def run(*argv):
    lines = []
    code = EXPORT.main(list(argv), out=lines.append)
    return code, lines


class IgnoredMirrorsGitignore(unittest.TestCase):
    def test_same_patterns_in_the_same_order(self):
        text = (WORKSPACE / ".gitignore").read_text(encoding="utf-8")
        patterns = tuple(line.strip() for line in text.splitlines()
                         if line.strip() and not line.lstrip().startswith("#"))
        self.assertEqual(patterns, EXPORT.IGNORED)


class WhichFiles(unittest.TestCase):
    def test_course_files_go_out(self):
        for rel in ("README.md", "stages/00-orientation/01-first-steps/lesson.md", "tools/course.py",
                    "learner/README.md", "journal/README.md", ".gitignore", "docs/research/README.md"):
            self.assertTrue(EXPORT.is_course_file(rel), rel)

    def test_records_and_ignored_files_stay(self):
        for rel in ("learner/profile.md", "learner/state.json", "learner/log.jsonl",
                    "learner/misconceptions.md", "learner/last-result.json", "journal/2026-11-20.md",
                    "notes/my-rules.md", "notes/gate-1-explain.md", "notes/stage-1-retro.md", "PROGRESS.md",
                    "docs/research/local-only/public-denylist.txt",
                    "tools/courselib/__pycache__/app.cpython-314.pyc", ".DS_Store", "stages/.DS_Store",
                    "._lesson.md", ".claude/settings.json", ".git/config", ".env"):
            self.assertFalse(EXPORT.is_course_file(rel), rel)


class Scan(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="export-scan-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def findings(self, text, denylist=(), user=USER, home=HOME):
        (self.root / "a.md").write_text(text, encoding="utf-8")
        rules = EXPORT.privacy_rules(list(denylist), user=user, home=home)
        return EXPORT.scan(self.root, ["a.md"], rules)

    def test_placeholders_pass(self):
        text = ("you@example.com li.lei@example.com noreply@anthropic.com jane@computer.local\n"
                "git@github.com:octo-learner/my-site.git playground@example.invalid\n"
                "12345678+octo-learner@users.noreply.github.com FAKE_KEY_FOR_DEMO_0000\n"
                "https://formulae.brew.sh/api/formula/postgresql@18.json\n")
        self.assertEqual(self.findings(text), [])

    def test_each_rule_fires_and_never_repeats_the_text(self):
        text = ("Work on " + TERM + " today\n"
                "see " + HOME + "/Desktop\n"
                "mail " + ADDRESS + "\n"
                "API_KEY = 'sk_live_" + "A1b2C3d4E5f6G7h8I9j0K1l2" + "'\n")
        found = self.findings(text, denylist=[TERM])
        lines = {line for _, line, _ in found}
        self.assertEqual(lines, {1, 2, 3, 4})
        for _, _, name in found:
            self.assertNotIn(TERM, name)
            self.assertNotIn(USER, name)

    def test_the_account_name_may_name_the_author(self):
        text = ("Copyright (c) 2026 " + USER + "\n"
                "Copyright 2026 " + USER + "\n"
                "© 2026 " + USER + " · https://github.com/" + USER + "/fullstack-from-zero\n")
        self.assertEqual(self.findings(text), [])
        self.assertEqual(len(self.findings("written by " + USER + "\n")), 1)

    def test_short_account_names_are_not_guarded(self):
        self.assertEqual(self.findings("ab is here\n", user="ab", home="/"), [])


class ExportEndToEnd(unittest.TestCase):
    """One export of a copy of the real course, with a learner's records added."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="export-e2e-"))
        cls.source = cls.tmp / "fullstack-from-zero"
        for rel in EXPORT.course_files(WORKSPACE):
            dest = cls.source / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(WORKSPACE / rel, dest)
        (cls.source / "learner" / "profile.md").write_text("# 学习档案\n", encoding="utf-8")
        (cls.source / "journal" / "2026-11-20.md").write_text("今天学了 0.1。\n", encoding="utf-8")
        (cls.source / "notes").mkdir(exist_ok=True)
        (cls.source / "notes" / "my-rules.md").write_text("# 我的行规笔记\n\n我自己写的话。\n", encoding="utf-8")
        (cls.source / "notes" / "stage-1-retro.md").write_text("我的复盘。\n", encoding="utf-8")
        (cls.source / "PROGRESS.md").write_text("# 学习进度\n", encoding="utf-8")
        convert = cls.source / "starter" / "hello-fx" / "convert.py"
        convert.write_text(convert.read_text(encoding="utf-8").replace("7.10", "7.20"), encoding="utf-8")
        local = cls.source / "docs" / "research" / "local-only"
        local.mkdir(parents=True, exist_ok=True)
        (local / "public-denylist.txt").write_text("# private terms\n" + TERM + "\n", encoding="utf-8")
        (local / "private-notes.md").write_text(TERM + "\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def export(self, name):
        target = self.tmp / name
        with mock.patch.object(EXPORT.getpass, "getuser", return_value=USER), \
                mock.patch.object(EXPORT.Path, "home", return_value=Path(HOME)):
            code, lines = run("--root", str(self.source), str(target))
        return code, lines, target

    def test_clean_export_leaves_records_and_private_research_behind(self):
        code, lines, target = self.export("clean")
        self.assertEqual(code, 0, "\n".join(lines))
        self.assertFalse((target / "learner" / "profile.md").exists())
        self.assertFalse((target / "journal" / "2026-11-20.md").exists())
        self.assertFalse((target / "docs" / "research" / "local-only").exists())
        self.assertTrue((target / "learner" / "README.md").is_file())
        notes = (target / "notes" / "my-rules.md").read_text(encoding="utf-8")
        self.assertNotIn("我自己写的话", notes)
        self.assertIn("## 0.1", notes)
        self.assertFalse((target / "notes" / "stage-1-retro.md").exists())
        self.assertFalse((target / "PROGRESS.md").exists())

    def test_starter_files_go_out_as_the_originals(self):
        code, lines, target = self.export("starter")
        self.assertEqual(code, 0, "\n".join(lines))
        manifest = json.loads((WORKSPACE / EXPORT.STARTER_MANIFEST).read_text(encoding="utf-8"))
        for rel, entry in manifest["files"].items():
            if "text" in entry:
                self.assertEqual((target / rel).read_text(encoding="utf-8"), entry["text"], rel)
        self.assertNotIn("7.20", (target / "starter" / "hello-fx" / "convert.py").read_text(encoding="utf-8"))

    def test_a_denylisted_term_in_a_course_file_is_reported(self):
        page = self.source / "docs" / "authoring" / "README.md"
        original = page.read_text(encoding="utf-8")
        self.addCleanup(page.write_text, original, encoding="utf-8")
        page.write_text(original + "\n" + TERM + "\n", encoding="utf-8")
        code, lines, _ = self.export("dirty")
        self.assertEqual(code, 1)
        self.assertTrue(any(line.startswith("docs/authoring/README.md:") for line in lines), lines)
        self.assertFalse(any(TERM in line for line in lines))

    def test_target_inside_the_workspace_or_not_empty_is_refused(self):
        code, lines = run("--root", str(self.source), str(self.source / "out"))
        self.assertEqual(code, 2)
        busy = self.tmp / "busy"
        busy.mkdir()
        (busy / "x.txt").write_text("x", encoding="utf-8")
        code, lines = run("--root", str(self.source), str(busy))
        self.assertEqual(code, 2)

    def test_check_or_target_but_not_both(self):
        self.assertEqual(run("--root", str(self.source))[0], 2)
        self.assertEqual(run("--root", str(self.source), "--check", str(self.tmp / "x"))[0], 2)


if __name__ == "__main__":
    unittest.main()
