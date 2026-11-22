#!/usr/bin/env python3
"""Create a simulation home that mimics a typical learner's Mac (plan G8).

For builders and testers only; learners never run this.  Standard library
only, Python 3.9 or newer.

    python3 tools/dev/make_sim_home.py "$TMPDIR/sim-1"            # home + copy of the workspace
    python3 tools/dev/make_sim_home.py "$TMPDIR/sim-1" --no-copy  # home only
    python3 tools/dev/make_sim_home.py "$TMPDIR/sim-1" --no-identity
    python3 tools/dev/make_sim_home.py "$TMPDIR/sim-1" --stay     # the learner who stayed

What it creates under the target folder ``<sim>``:

    <sim>/home/.gitconfig          typical global Git settings of a beginner
                                   (fake identity, signing on, gpg missing,
                                   gpg.ssh.program and gpg.ssh.allowedSignersFile
                                   present and empty, tag.forceSignAnnotated=false)
    <sim>/home/.gitignore_global   the eight patterns of plan G7
    <sim>/home/Developer/          the learner's code folder
    <sim>/home/Developer/fullstack-from-zero   a copy of this workspace (unless --no-copy),
                                   without the learner's journal/, notes/,
                                   learner/ and PROGRESS.md (unless
                                   --with-learner-files); the course's own
                                   README.md files there and the skeleton of
                                   notes/my-rules.md (headings only) are copied

With ``--stay`` the copy is the one of a learner who kept the course where it
was (lesson 0.2c, decision ``workspace_location`` = ``stay-in-sync``):

    <sim>/home/Desktop/Code/fullstack-from-zero   the copy of the workspace
    <sim>/home/Developer/fullstack-from-zero      the entrance: a symbolic link to it
    .../learner/state.json                {"decisions": {"workspace_location":
                                          "stay-in-sync"}} unless the copy has one

The simulation cannot mark the Desktop as synced by iCloud, so ``doctor``
reports the folder as not synced there.

Then it prints the shell lines to use (``export HOME=...`` and so on).  It
never runs ``git config --global`` and never touches the real home: the files
are written directly into the target, and the target must be a new or empty
folder inside the system temporary directory ($TMPDIR or /tmp).
"""

import argparse
import json
import os
import shlex
import shutil
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

#: The fake identity (plan G8).  Tests assert that these never appear in
#: anything the course tool prints or stores.
FAKE_NAME = "Learner"
FAKE_EMAIL = "learner@example.com"
FAKE_SIGNING_KEY = "FAKEKEY0000"

#: A typical ~/.gitignore_global (plan G7), in this order.
GLOBAL_IGNORE = (".DS_Store", "._*", ".Spotlight-V100", ".Trashes", ".idea/",
                 "*.swp", "*.swo", "*.log")

#: Not copied into the simulation's workspace (at any depth).
SKIP = ("__pycache__", "*.pyc", ".DS_Store", ".ruff_cache", ".pytest_cache")

#: Top-level folders and files of the workspace that belong to the learner or
#: hold the learner's state (plan G11).  A simulation starts without them, so
#: no agent ever reads or carries around the learner's own notes; pass
#: --with-learner-files to copy them anyway.
LEARNER_OWNED = ("journal", "notes", "learner", "PROGRESS.md")
#: What the course itself ships inside those folders (COMMON section 4): the
#: README.md of each, and the skeleton of notes/my-rules.md (title,
#: instructions and headings; the learner's own lines are left out).
COURSE_SKELETONS = ("journal/README.md", "notes/README.md", "learner/README.md")
RULES_NOTES = "notes/my-rules.md"

TEXT = {
    "not_temp": "拒绝：目标文件夹 {target} 不在系统临时目录（{roots}）里。模拟家目录只能建在临时目录下。",
    "is_root": "拒绝：目标不能是临时目录本身，请给一个新的子文件夹，例如 {example}。",
    "not_empty": "拒绝：目标文件夹 {target} 已经存在而且不是空的。换一个新名字，或者先自己删掉它。",
    "not_folder": "拒绝：{target} 已经存在，而且不是文件夹。",
    "inside_workspace": "拒绝：目标文件夹在学习工作区里面（{workspace}），复制会无限套娃。",
    "no_workspace": "拒绝：找不到要复制的学习工作区 {workspace}。",
    "stay_needs_copy": "拒绝：--stay 要复制学习工作区，不能和 --no-copy 一起用。",
    "done": "模拟家目录建好了：{home}",
    "copied": "学习工作区副本：{copy}",
    "entrance": "入口（符号链接）：{entrance} -> {copy}",
    "use": "在模拟用的 shell 里执行下面几行（只影响那个 shell）：",
    "note": ("提醒：这里的 git 会把 commit.gpgsign=true 当真，所以普通的 git commit 会失败，"
             "模拟的就是签名打开、没装 gpg 的常见情况。要提交请在命令里加 -c commit.gpgsign=false，并在报告里写明。"),
}


def temp_roots():
    """Folders under which a simulation may be created (resolved)."""
    roots = []
    for candidate in (tempfile.gettempdir(), os.environ.get("TMPDIR", ""), "/tmp"):
        if candidate:
            real = Path(os.path.realpath(candidate))
            if real.is_dir() and real not in roots:
                roots.append(real)
    return roots


class Refusal(Exception):
    """The target is not acceptable; the message says why."""


def check_target(target, workspace=None, copy=True):
    """The resolved target folder, or Refusal."""
    real = Path(os.path.realpath(os.path.expanduser(str(target))))
    roots = temp_roots()
    if real in roots:
        raise Refusal(TEXT["is_root"].format(example=str(roots[0] / "sim-1")))
    if not any(root in real.parents for root in roots):
        raise Refusal(TEXT["not_temp"].format(
            target=real, roots="、".join(str(root) for root in roots)))
    if real.exists() and not real.is_dir():
        raise Refusal(TEXT["not_folder"].format(target=real))
    if real.is_dir() and any(real.iterdir()):
        raise Refusal(TEXT["not_empty"].format(target=real))
    if copy:
        source = Path(os.path.realpath(str(workspace or WORKSPACE)))
        if not source.is_dir():
            raise Refusal(TEXT["no_workspace"].format(workspace=source))
        if real == source or source in real.parents:
            raise Refusal(TEXT["inside_workspace"].format(workspace=source))
    return real


def gitconfig_text(identity=True, signing=True, excludes="~/.gitignore_global"):
    """The text of the simulated ~/.gitconfig (the typical settings of plan G7).

    With ``signing`` it also carries the two keys of ``[gpg "ssh"]`` that a
    broken setup can have with empty values, written the way ``git config``
    writes an empty value (``key = `` with a trailing space), and
    ``tag.forceSignAnnotated = false``.
    """
    lines = []
    if identity or signing:
        lines.append("[user]")
        if identity:
            lines.append("\tname = " + FAKE_NAME)
            lines.append("\temail = " + FAKE_EMAIL)
        if signing:
            lines.append("\tsigningkey = " + FAKE_SIGNING_KEY)
    if signing:
        lines += ["[commit]", "\tgpgsign = true",
                  "[gpg]", "\tformat = openpgp", "\tprogram = gpg",
                  '[gpg "ssh"]', "\tprogram = ", "\tallowedSignersFile = ",
                  "[tag]", "\tforceSignAnnotated = false"]
    if excludes:
        lines += ["[core]", "\texcludesfile = " + excludes]
    return "\n".join(lines) + "\n"


def write_home(home, identity=True, signing=True):
    """Write .gitconfig and .gitignore_global into ``home`` (created if needed)."""
    home = Path(home)
    (home / "Developer").mkdir(parents=True, exist_ok=True)
    (home / ".gitconfig").write_text(gitconfig_text(identity=identity, signing=signing),
                                     encoding="utf-8")
    (home / ".gitignore_global").write_text("\n".join(GLOBAL_IGNORE) + "\n", encoding="utf-8")
    return home


def _ignore(source_root, learner_files):
    skip_anywhere = shutil.ignore_patterns(*SKIP)
    top = os.path.realpath(str(source_root))

    def ignore(folder, names):
        skipped = set(skip_anywhere(folder, names))
        if not learner_files and os.path.realpath(folder) == top:
            skipped.update(name for name in names if name in LEARNER_OWNED)
        return skipped

    return ignore


#: Where ``--stay`` puts the copy: a course folder on the Desktop that was never moved.
STAY_PLACE = ("Desktop", "Code", "fullstack-from-zero")


def make_sim_home(target, workspace=None, copy=True, identity=True, signing=True,
                  learner_files=False, stay=False):
    """Create the simulation under ``target``; returns a dict of paths.

    Keys: ``sim``, ``home``, ``developer``, ``workspace`` (the real folder of
    the copy, or None) and ``entrance`` (``~/Developer/fullstack-from-zero`` when it
    is a link, that is with ``stay``; else None).
    """
    if stay and not copy:
        raise Refusal(TEXT["stay_needs_copy"])
    real = check_target(target, workspace=workspace, copy=copy)
    real.mkdir(parents=True, exist_ok=True)
    home = write_home(real / "home", identity=identity, signing=signing)
    info = {"sim": str(real), "home": str(home), "developer": str(home / "Developer"),
            "workspace": None, "entrance": None}
    if copy:
        source = Path(os.path.realpath(str(workspace or WORKSPACE)))
        entrance = home / "Developer" / "fullstack-from-zero"
        destination = home.joinpath(*STAY_PLACE) if stay else entrance
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(source), str(destination), symlinks=True,
                        ignore=_ignore(source, learner_files))
        if not learner_files:
            copy_skeletons(source, destination)
        info["workspace"] = str(destination)
        if stay:
            entrance.symlink_to(destination, target_is_directory=True)
            info["entrance"] = str(entrance)
            state = destination / "learner" / "state.json"
            if not state.exists():
                state.parent.mkdir(parents=True, exist_ok=True)
                state.write_text(json.dumps(
                    {"schema": 1, "stations": {}, "review": {}, "exams": {}, "sessions": [],
                     "decisions": {"workspace_location": "stay-in-sync"}},
                    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return info


def rules_notes_skeleton(text):
    """notes/my-rules.md without the learner's own lines.

    Everything before the first 「## 」 heading (the title and the
    instructions the course wrote) and every heading line are kept; under
    each rule heading an empty line is left where the learner writes.
    """
    lines = text.splitlines()
    first = next((i for i, line in enumerate(lines) if line.startswith("## ")), len(lines))
    kept = lines[:first]
    for line in lines[first:]:
        if line.startswith("#"):
            if kept and kept[-1] != "":
                kept.append("")
            kept += [line, ""]
    return "\n".join(kept).rstrip("\n") + "\n"


def copy_skeletons(source, destination):
    """Put the course-supplied files of the learner's folders into the copy."""
    source, destination = Path(source), Path(destination)
    for rel in COURSE_SKELETONS:
        origin = source / rel
        if origin.is_file() and not origin.is_symlink():
            (destination / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(origin), str(destination / rel))
    origin = source / RULES_NOTES
    if origin.is_file() and not origin.is_symlink():
        (destination / RULES_NOTES).parent.mkdir(parents=True, exist_ok=True)
        text = origin.read_text(encoding="utf-8", errors="replace")
        (destination / RULES_NOTES).write_text(rules_notes_skeleton(text), encoding="utf-8")


def export_lines(info):
    """Shell lines that switch a shell into the simulation."""
    lines = [
        "export SIM=" + shlex.quote(info["sim"]),
        "export HOME=" + shlex.quote(info["home"]),
        "unset XDG_CONFIG_HOME GIT_CONFIG_GLOBAL",
    ]
    if info.get("entrance"):
        # The path every lesson writes: cd ~/Developer/fullstack-from-zero
        lines.append("cd " + shlex.quote(info["entrance"]))
    elif info.get("workspace"):
        lines.append("cd " + shlex.quote(info["workspace"]))
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 tools/dev/make_sim_home.py",
        description="Create a simulation home that mimics a typical learner's Mac (plan G8).")
    parser.add_argument("target", help="a new or empty folder inside $TMPDIR or /tmp")
    parser.add_argument("--no-copy", action="store_true",
                        help="do not copy the workspace to <home>/Developer/fullstack-from-zero")
    parser.add_argument("--workspace", default=None,
                        help="workspace to copy (default: the one this script belongs to)")
    parser.add_argument("--no-identity", action="store_true",
                        help="leave user.name and user.email out of .gitconfig")
    parser.add_argument("--no-signing", action="store_true",
                        help="leave the signing settings out of .gitconfig")
    parser.add_argument("--with-learner-files", action="store_true",
                        help="also copy journal/, notes/, learner/ and PROGRESS.md "
                             "(left out by default)")
    parser.add_argument("--stay", action="store_true",
                        help="copy to <home>/Desktop/Code/fullstack-from-zero and make "
                             "<home>/Developer/fullstack-from-zero an entrance (a symbolic link) to it, "
                             "with the decision workspace_location = stay-in-sync")
    parser.add_argument("--json", action="store_true", help="print the paths as JSON only")
    args = parser.parse_args(argv)
    try:
        info = make_sim_home(args.target, workspace=args.workspace, copy=not args.no_copy,
                             identity=not args.no_identity, signing=not args.no_signing,
                             learner_files=args.with_learner_files, stay=args.stay)
    except Refusal as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2
    if args.json:
        sys.stdout.write(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
        return 0
    out = sys.stdout.write
    out(TEXT["done"].format(home=info["home"]) + "\n")
    if info["workspace"]:
        out(TEXT["copied"].format(copy=info["workspace"]) + "\n")
    if info.get("entrance"):
        out(TEXT["entrance"].format(entrance=info["entrance"], copy=info["workspace"]) + "\n")
    out("\n" + TEXT["use"] + "\n\n")
    for line in export_lines(info):
        out("    " + line + "\n")
    out("\n" + TEXT["note"] + "\n")
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main())
