"""The starter manifest (plan G11a): tools/courselib/starter_manifest.json and
tools/dev/build_starter_manifest.py (--write, --check, --restore).

Every test that writes works on a throw-away copy under $TMPDIR; the real
workspace is only read.
"""

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import helpers

from courselib import scenario

_SPEC = importlib.util.spec_from_file_location(
    "build_starter_manifest", str(helpers.TOOLS / "dev" / "build_starter_manifest.py"))
BUILDER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(BUILDER)

MANIFEST = helpers.TOOLS / "courselib" / "starter_manifest.json"


class ManifestTodayTest(unittest.TestCase):
    def test_the_manifest_matches_the_starter_folder_today(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(sorted(data["files"]), BUILDER.disk_files(helpers.REPO))
        self.assertEqual(BUILDER.compare(helpers.REPO, data), ([], [], [], []))
        self.assertEqual(scenario.starter_differences(helpers.REPO), [])
        # --write would not change a byte
        self.assertEqual(MANIFEST.read_text(encoding="utf-8"),
                         BUILDER.manifest_text(BUILDER.build(helpers.REPO)))

    def test_every_entry_holds_the_original_and_its_checksum(self):
        data = scenario.load_starter_manifest()
        self.assertEqual(data["schema"], 1)
        self.assertEqual(data["learner_edits"], ["starter/hello-fx/convert.py"])
        for path in data["files"]:
            original = scenario.starter_originals(path, data)[""]
            self.assertEqual(original, (helpers.REPO / path).read_bytes(), path)
        self.assertIn("text", data["files"]["starter/my-site/index.html"])

    def test_check_on_the_real_workspace_exits_0(self):
        lines = []
        code = BUILDER.main(["--check"], out=lines.append)
        self.assertEqual(code, 0, lines)
        self.assertIn("starter/ 和清单一致", lines[0])


class ManifestToolTest(unittest.TestCase):
    def setUp(self):
        self.base = Path(os.path.realpath(tempfile.mkdtemp(prefix="starter-manifest-")))
        self.addCleanup(shutil.rmtree, str(self.base), True)
        self.ws = self.base / "ws"
        shutil.copytree(str(helpers.REPO / "starter"), str(self.ws / "starter"))
        (self.ws / "starter" / "my-site" / "logo.bin").write_bytes(b"\x89PNG\r\n\x1a\n\xff\x00")
        (self.ws / "starter" / "my-site" / ".DS_Store").write_bytes(b"\x00\x01")
        (self.ws / "starter" / "hello-fx" / "__pycache__").mkdir()
        (self.ws / "starter" / "hello-fx" / "__pycache__" / "x.pyc").write_bytes(b"\x00")
        self.manifest = self.base / "manifest.json"
        self.lines = []

    def run_tool(self, *argv):
        self.lines = []
        return BUILDER.main(list(argv), workspace=self.ws, manifest=self.manifest,
                            out=self.lines.append)

    def test_write_records_text_as_text_and_other_bytes_as_base64(self):
        self.assertEqual(self.run_tool("--write"), 0)
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(sorted(data["files"]), [
            "starter/hello-fx/convert.py", "starter/hello-fx/rates.txt",
            "starter/my-site/index.html", "starter/my-site/logo.bin", "starter/my-site/style.css"])
        self.assertIn("text", data["files"]["starter/my-site/index.html"])
        self.assertIn("base64", data["files"]["starter/my-site/logo.bin"])
        self.assertNotIn("text", data["files"]["starter/my-site/logo.bin"])
        self.assertEqual(scenario.starter_originals("starter/my-site/logo.bin", data)[""],
                         b"\x89PNG\r\n\x1a\n\xff\x00")
        self.assertEqual(self.run_tool("--check"), 0)

    def test_check_names_changed_missing_and_new_files(self):
        self.run_tool("--write")
        (self.ws / "starter" / "my-site" / "index.html").write_text("改了\n", encoding="utf-8")
        (self.ws / "starter" / "hello-fx" / "rates.txt").unlink()
        (self.ws / "starter" / "my-site" / "notes.txt").write_text("新的\n", encoding="utf-8")
        self.assertEqual(self.run_tool("--check"), 1)
        text = "\n".join(self.lines)
        self.assertIn("改动过：starter/my-site/index.html", text)
        self.assertIn("不见了：starter/hello-fx/rates.txt", text)
        self.assertIn("清单里没有：starter/my-site/notes.txt", text)
        self.assertNotIn(".DS_Store", text)
        self.assertNotIn("__pycache__", text)

    def test_restore_keeps_the_present_file_and_writes_the_original(self):
        self.run_tool("--write")
        page = self.ws / "starter" / "my-site" / "index.html"
        original = page.read_bytes()
        page.write_text("学习者改过的版本\n", encoding="utf-8")
        self.assertEqual(self.run_tool("--restore", "starter/my-site/index.html"), 0)
        self.assertEqual(page.read_bytes(), original)
        kept = self.ws / "starter" / "my-site" / "index.html.changed"
        self.assertEqual(kept.read_text(encoding="utf-8"), "学习者改过的版本\n")
        self.assertIn("没有删除", self.lines[0])
        # a second repair never overwrites the first copy
        page.write_text("又改了一次\n", encoding="utf-8")
        self.run_tool("--restore", str(page))
        self.assertEqual(kept.read_text(encoding="utf-8"), "学习者改过的版本\n")
        self.assertEqual((self.ws / "starter" / "my-site" / "index.html.changed-2")
                         .read_text(encoding="utf-8"), "又改了一次\n")
        # the kept copies do not make --check fail
        self.assertEqual(self.run_tool("--check"), 0, self.lines)
        self.assertIn("导师恢复时留下的副本", "\n".join(self.lines))

    def test_restore_of_an_unchanged_or_a_missing_file(self):
        self.run_tool("--write")
        self.assertEqual(self.run_tool("--restore", "starter/hello-fx/rates.txt"), 0)
        self.assertIn("不用恢复", self.lines[0])
        rates = self.ws / "starter" / "hello-fx" / "rates.txt"
        original = rates.read_bytes()
        rates.unlink()
        self.assertEqual(self.run_tool("--restore", "starter/hello-fx/rates.txt"), 0)
        self.assertEqual(rates.read_bytes(), original)
        self.assertFalse((self.ws / "starter" / "hello-fx" / "rates.txt.changed").exists())

    def test_restore_refuses_what_it_does_not_know(self):
        self.run_tool("--write")
        for typed in ("starter/my-site/notes.txt", "README.md", "../outside.txt"):
            err = io.StringIO()
            real = sys.stderr
            sys.stderr = err
            try:
                self.assertEqual(self.run_tool("--restore", typed), 2, typed)
            finally:
                sys.stderr = real
            self.assertTrue(err.getvalue().strip(), typed)
        self.assertFalse((self.base / "outside.txt").exists())

    def test_the_script_runs_on_python_39(self):
        python = helpers.find_python39()
        if python is None:
            self.skipTest("no Python 3.9 on this machine")
        done = subprocess.run([python, str(helpers.TOOLS / "dev" / "build_starter_manifest.py"),
                               "--check"], capture_output=True, check=False, timeout=60,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()
