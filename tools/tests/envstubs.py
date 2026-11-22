"""Fake programs and simulation homes for the tests of ``doctor`` and ``fresh``.

``FakeBin`` is a folder of tiny shell scripts that stand in for the
learner's programs (``sw_vers``, ``python3``, ``code`` ...).  The tests put
only this folder on PATH, so what the doctor "finds" is exactly what the test
installed.  ``git`` is a script that runs the real git, because the doctor
reads real Git configuration from the simulation home.

``make_sim_home`` is the builders' script from ``tools/dev``; its Git
settings are the ones of plan G8 (fake identity, signing on, no gpg).
"""

import importlib.util
import os
import shutil
import stat
from pathlib import Path

import helpers

_SPEC = importlib.util.spec_from_file_location(
    "make_sim_home", str(helpers.TOOLS / "dev" / "make_sim_home.py"))
make_sim_home = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(make_sim_home)

#: The fake identity values that must never be printed or stored.
SECRETS = (make_sim_home.FAKE_NAME, make_sim_home.FAKE_EMAIL, make_sim_home.FAKE_SIGNING_KEY)

#: Reference versions the course was verified with on 2026-11-19 (plan G7).
VERSIONS = {
    "sw_vers": "27.2.1",
    "zsh": "zsh 5.9 (arm64-apple-darwin26.0)",
    "python3": "Python 3.14.9",
    "code": "1.145.2\nc4453f8ea430795f941c1b2ff6c9321135a74a02\narm64",
    "uv": "uv 0.13.5 (Homebrew 2026-10-22 aarch64-apple-darwin)",
    "ruff": "ruff 0.17.2",
    "node": "v26.12.0",
    "npm": "11.20.0",
    "brew": "Homebrew 7.0.10\nHomebrew/homebrew-core (git revision 1; last commit 2026-11-19)",
}

REAL_GIT = shutil.which("git", path=os.environ.get("PATH", "/usr/bin:/bin")) or ""


def _quote(text):
    return "'" + str(text).replace("'", "'\"'\"'") + "'"


class FakeBin:
    """A folder of stub programs."""

    def __init__(self, folder):
        self.path = Path(folder)
        self.path.mkdir(parents=True, exist_ok=True)

    def script(self, name, body):
        target = self.path / name
        target.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return target

    def prints(self, name, text, code=0, stderr=False):
        """A program that prints ``text`` (whatever its arguments) and exits ``code``."""
        redirect = " >&2" if stderr else ""
        return self.script(name, f"printf '%s\\n' {_quote(text)}{redirect}\nexit {code}")

    def real_git(self):
        if not REAL_GIT:
            raise RuntimeError("no git on this machine")
        return self.script("git", f'exec {_quote(REAL_GIT)} "$@"')

    def remove(self, name):
        target = self.path / name
        if target.exists():
            target.unlink()

    def learner_machine(self, skip=(), **override):
        """Every program of plan G7 with its version; ``gpg`` and ``gh`` absent."""
        self.real_git()
        for name, text in VERSIONS.items():
            if name in skip:
                continue
            self.prints(name, override.get(name, text))
        return self

    def __str__(self):
        return str(self.path)


def xattr_stub(folder, flagged=(), fail=False):
    """A stand-in for /usr/bin/xattr.

    Folders listed in ``flagged`` carry the iCloud file-provider attribute;
    ``-p <name> <folder>`` prints an iCloud Drive domain for them.  With
    ``fail`` every call exits 1 with an error message.
    """
    bin_dir = FakeBin(folder)
    flags = bin_dir.path / "xattr-flagged.txt"
    flags.write_text("".join(str(f) + "\n" for f in flagged), encoding="utf-8")
    if fail:
        return bin_dir.script("xattr", "echo 'xattr: [Errno 1] Operation not permitted' >&2\nexit 1")
    grep = shutil.which("grep", path="/usr/bin:/bin") or "/usr/bin/grep"
    body = """\
if [ "$1" = "-p" ]; then
  if {grep} -Fxq -- "$3" {flags}; then
    echo "com.apple.CloudDocs.iCloudDriveFileProvider/0A1B2C3D-0000-0000-0000-000000000000"
    exit 0
  fi
  echo "xattr: $3: No such xattr: $2" >&2
  exit 1
fi
if {grep} -Fxq -- "$1" {flags}; then
  echo "com.apple.file-provider-domain-id"
  echo "com.apple.fileprovider.detached#B"
fi
exit 0""".format(grep=_quote(grep), flags=_quote(flags))
    return bin_dir.script("xattr", body)
