#!/usr/bin/env python3
"""Export the course as a folder that can be published (a public repository).

For builders only; learners never run this.  Standard library only, Python
3.9 or newer.

    python3 tools/dev/export_public.py ~/Developer/fullstack-from-zero   # export, then check the export
    python3 tools/dev/export_public.py --check                           # check the workspace, write nothing

The learning workspace holds two things: the course (lessons, tools,
handbook, design documents) and one learner's own records (questionnaire,
progress, journal, rule notes).  The course can be published; the records
stay in the learner's private repository (lesson 1.12).  This script copies
only the course:

- left out: everything ``.gitignore`` keeps out of a repository (``IGNORED``
  mirrors it, and a test keeps the two in step), ``.git/`` and ``.claude/``,
  the private research in ``docs/research/local-only/``, and the learner's
  records: every file in ``learner/`` and ``journal/`` except their
  ``README.md``, everything in ``notes/`` (the export rebuilds
  ``notes/my-rules.md`` as the empty skeleton with ``build_reference.py
  --notes``), and the generated progress table ``PROGRESS.md``.
- files under ``starter/`` are written from the originals kept in
  ``tools/courselib/starter_manifest.json`` (plan G11a), so a lesson's edit
  in the workspace (lesson 0.1 changes ``starter/hello-fx/convert.py``) never
  reaches the public copy.
- then every text file of the export is checked; ``--check`` checks the
  workspace itself, with the same exclusions.  A finding is printed as
  ``file:line  rule`` without repeating the matched text, and the exit code
  is 1.  The rules: the account name (except in a copyright line or in the
  repository address, where it is the author's public GitHub name) and the home folder of this computer;
  e-mail addresses other than documented placeholders; strings shaped like
  real keys or tokens; and every term in
  ``docs/research/local-only/public-denylist.txt`` (one term per line, ``#``
  starts a comment).  That list is private by construction: it lives in the
  one folder that is never exported, so the names it guards are never
  published, not even inside this check.

Exit codes: 0 clean; 1 findings; 2 usage problem (for example the target
folder exists and is not empty, or lies inside the workspace).
"""

import sys

sys.dont_write_bytecode = True

import argparse
import base64
import getpass
import hashlib
import json
import os
import re
import shutil
import subprocess
from fnmatch import fnmatch
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
PROG = "python3 tools/dev/export_public.py"
DENYLIST = "docs/research/local-only/public-denylist.txt"

#: The patterns of .gitignore, in the same order (tests/test_export_public.py compares them).
IGNORED = (
    ".DS_Store",
    "._*",
    "__pycache__/",
    "*.pyc",
    ".ruff_cache/",
    "learner/last-result.json",
    "learner/.*.tmp",
    "docs/research/local-only/",
    ".claude/settings.local.json",
    ".claude/.cc-writes/",
    ".env",
)
#: Folders that never belong to the published course.
NEVER = (".git/", ".claude/")

#: The learner's own records stay in the private learning repository; only these files go out.
RECORD_FOLDERS = {"learner": {"README.md"}, "journal": {"README.md"}, "notes": set()}
#: Single files at the root that belong to the learner (tool-written state, plan G11).
RECORD_FILES = {"PROGRESS.md"}
NOTES = "notes/my-rules.md"
STARTER_MANIFEST = "tools/courselib/starter_manifest.json"

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_EMAIL = re.compile(
    r"(@(example\.(com|org|net|invalid)|[\w.-]+\.example|computer\.local|anthropic\.com"
    r"|users\.noreply\.github\.com)|^git@github\.com)$",
    re.IGNORECASE,
)
#: Things shaped like an address that are file names, e.g. the Homebrew API page postgresql@18.json.
NOT_AN_ADDRESS = re.compile(r"\.(json|md|txt|py|js|ts|html|css|toml|ya?ml|lock|sh|plist|png|jpe?g|svg)$",
                            re.IGNORECASE)
SECRET_SHAPES = (
    ("GitHub 令牌的形状", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}")),
    ("Stripe 密钥的形状", re.compile(r"\b[sr]k_(live|test)_[A-Za-z0-9]{20,}")),
    ("AWS 访问密钥的形状", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("私钥文件的开头", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("模型服务密钥的形状", re.compile(r"\bsk-(ant-|proj-)?[A-Za-z0-9_-]{32,}")),
)


def _matches(rel, pattern):
    """True when the posix path ``rel`` is caught by one .gitignore-style ``pattern``."""
    if pattern.endswith("/"):
        folder = pattern.rstrip("/")
        if "/" in folder:
            return rel.startswith(folder + "/")
        return any(fnmatch(part, folder) for part in rel.split("/")[:-1])
    if "/" in pattern:
        return fnmatch(rel, pattern)
    return fnmatch(rel.rsplit("/", 1)[-1], pattern)


def is_course_file(rel):
    """True when the file ``rel`` belongs to the published course (see the module docstring)."""
    if any(_matches(rel, p) for p in IGNORED + NEVER):
        return False
    top, _, rest = rel.partition("/")
    if top in RECORD_FOLDERS and rest:
        return rest in RECORD_FOLDERS[top]
    return rel not in RECORD_FILES


def course_files(root):
    """Every course file under ``root``, as sorted posix paths relative to it."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath).relative_to(root).as_posix()
        base = "" if base == "." else base + "/"
        dirnames[:] = sorted(d for d in dirnames
                             if not any(_matches(base + d + "/x", p) for p in IGNORED + NEVER if p.endswith("/")))
        found.extend(base + name for name in filenames if is_course_file(base + name))
    return sorted(found)


def load_denylist(root):
    path = Path(root) / DENYLIST
    if not path.is_file():
        return None
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        term = line.split("#", 1)[0].strip()
        if term:
            terms.append(term)
    return terms


def privacy_rules(denylist, user=None, home=None):
    """(name, pattern) pairs; a name never repeats the text it guards."""
    rules = []
    user = getpass.getuser() if user is None else user
    if user and len(user) >= 3:
        # The account name may also be the author's public GitHub user name.  It is allowed in the
        # three places that name the author on purpose: a copyright line ("Copyright (c) 2026 name",
        # "Copyright 2026 name", "© 2026 name") and the repository address ("github.com/name/").
        public = (r"(?<!github\.com/)(?<!Copyright \(c\) \d{4} )(?<!Copyright \d{4} )(?<!© \d{4} )")
        rules.append(("这台电脑的账户名",
                      re.compile(public + r"(?<![A-Za-z0-9])" + re.escape(user) + r"(?![A-Za-z0-9])", re.IGNORECASE)))
    home = str(Path.home()) if home is None else home
    if home and home != "/":
        rules.append(("这台电脑的主文件夹路径", re.compile(re.escape(home))))
    for number, term in enumerate(denylist or [], 1):
        # A term that starts or ends with a letter or digit matches only as a whole word,
        # so a private name such as "Pine" does not fire on "pineapple".
        pattern = re.escape(term)
        if term[0].isalnum():
            pattern = r"(?<![A-Za-z0-9])" + pattern
        if term[-1].isalnum():
            pattern += r"(?![A-Za-z0-9])"
        rules.append((f"{DENYLIST} 第 {number} 个词", re.compile(pattern, re.IGNORECASE)))
    return rules


def scan(root, files, rules):
    """Findings as (relative path, line number, rule name) tuples, in file order."""
    findings = []
    for rel in files:
        try:
            text = (Path(root) / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for name, pattern in rules + list(SECRET_SHAPES):
                if pattern.search(line):
                    findings.append((rel, number, name))
            for address in EMAIL.findall(line):
                if not ALLOWED_EMAIL.search(address) and not NOT_AN_ADDRESS.search(address):
                    findings.append((rel, number, "不是占位用的邮箱地址"))
    return findings


def restore_starter(target):
    """Write every file of the starter manifest from its original; the number written, or None."""
    try:
        data = json.loads((target / STARTER_MANIFEST).read_text(encoding="utf-8"))
        written = 0
        for rel, entry in data["files"].items():
            if "text" in entry:
                original = entry["text"].encode("utf-8")
            else:
                original = base64.b64decode(entry["base64"].encode("ascii"), validate=True)
            if hashlib.sha256(original).hexdigest() != entry["sha256"]:
                return None
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(original)
            written += 1
        return written
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def export(source, target, out):
    """Copy the course files of ``source`` into the new folder ``target``; None on a usage problem."""
    target = Path(os.path.realpath(os.path.expanduser(str(target))))
    if target == source or source in target.parents:
        out("导出的文件夹不能在学习工作区里面。")
        return None
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        out(f"{target} 已经存在，而且不是空文件夹。换一个新名字，或者先把它移走。")
        return None
    files = course_files(source)
    for rel in files:
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, dest)
    restored = restore_starter(target)
    if restored is None:
        out(f"文件导出了，但 {STARTER_MANIFEST} 读不了或和原样对不上，没法把 starter/ 换回原样。")
        return None
    for folder in RECORD_FOLDERS:
        (target / folder).mkdir(exist_ok=True)
    built = subprocess.run([sys.executable, str(target / "tools" / "dev" / "build_reference.py"), "--notes"],
                           cwd=str(target), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if built.returncode != 0 or not (target / NOTES).is_file():
        out(f"文件导出了，但没能新建空的 {NOTES}：")
        out(built.stderr.strip() or f"build_reference.py 的退出码是 {built.returncode}")
        return None
    out(f"导出了 {len(files)} 个文件到 {target}，另按规则卡新建了空的 {NOTES}。")
    return target


def report(source, checked, out):
    """Check ``checked`` with the denylist of ``source``; returns the exit code."""
    denylist = load_denylist(source)
    if denylist is None:
        out(f"提醒：没有 {DENYLIST}，这次只查了账户名、主文件夹、邮箱和密钥的形状。")
    files = course_files(checked)
    findings = scan(checked, files, privacy_rules(denylist))
    if not findings:
        out(f"查了 {len(files)} 个文件，没有发现不该公开的内容。")
        return 0
    for rel, number, name in findings:
        out(f"{rel}:{number}  {name}")
    out(f"共 {len(findings)} 处。公开之前先处理，处理完再运行一次。")
    return 1


def main(argv=None, out=None):
    parser = argparse.ArgumentParser(
        prog=PROG, description="Export the course files that can be published, then check them (builders only).")
    parser.add_argument("target", nargs="?", help="a new, empty folder outside the workspace")
    parser.add_argument("--check", action="store_true", help="check the workspace itself; write nothing")
    parser.add_argument("--root", default=None,
                        help="workspace to read (default: the one this script belongs to)")
    args = parser.parse_args(argv)
    if out is None:
        def out(line):
            sys.stdout.write(line + "\n")
    source = Path(os.path.realpath(args.root)) if args.root else WORKSPACE
    if args.check == bool(args.target):
        out(f"用法：{PROG} <新文件夹>，或者 {PROG} --check")
        return 2
    if args.check:
        return report(source, source, out)
    target = export(source, args.target, out)
    if target is None:
        return 2
    return report(source, target, out)


if __name__ == "__main__":
    sys.exit(main())
