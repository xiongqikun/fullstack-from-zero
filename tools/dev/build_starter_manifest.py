#!/usr/bin/env python3
"""The manifest of the original starter files (plan G11a).

For builders and the tutor; learners never run this.  Standard library only,
Python 3.9 or newer.

    python3 tools/dev/build_starter_manifest.py --check     # do disk and manifest agree?
    python3 tools/dev/build_starter_manifest.py --write     # builders: record what is on disk now
    python3 tools/dev/build_starter_manifest.py --restore starter/my-site/index.html

``tools/courselib/starter_manifest.json`` holds the original content and the
sha256 of every file under ``starter/``: text files as text, anything that is
not UTF-8 text as base64.  Scenarios, the state ladder and exams build from
these originals (``courselib.scenario.copy_starter``), so a learner who edits
``starter/my-site/index.html`` in the editor changes nothing they practise on.

- ``--write`` regenerates the manifest from disk.  Only builders run it, after
  they changed starter material on purpose.
- ``--check`` compares disk and manifest; exit code 1 names the files that
  differ, are missing or are not in the manifest yet (0 when they agree).
  A changed ``learner_edits`` file is named on its own line and never makes
  the exit code 1 (the builders' guard is the test that calls ``compare``).
- ``--restore PATH ...`` is the tutor's repair: the present file is first
  copied to ``PATH.changed`` (``PATH.changed-2`` ... when that exists), then
  the original is written back.  Nothing is ever deleted.  ``PATH`` is read
  from the workspace root (``starter/my-site/index.html``) or is absolute.
  A ``learner_edits`` file is refused without ``--force``: it holds the
  learner's exercise.  The tutor restores only the files ``doctor`` names.

``starter/hello-fx/convert.py`` is the file lesson 0.1c tells the learner to
edit; it is recorded like every other file and listed under ``learner_edits``,
so ``doctor`` never reports it and ``--check`` names it apart, without
counting it.
"""

import argparse
import base64
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
MANIFEST = WORKSPACE / "tools" / "courselib" / "starter_manifest.json"
STARTER = "starter"
SCHEMA = 1

#: Files a lesson tells the learner to edit in place (plan G11a rule 1).
LEARNER_EDITS = ("starter/hello-fx/convert.py",)
#: Never recorded: the system makes them, not the course.
NOISE_NAMES = (".DS_Store", "__pycache__")
NOISE_SUFFIXES = (".pyc",)

NOTE = ("starter/ 下每个文件的原样（文本原样保存，其他内容用 base64）和 sha256。"
        "练习场景、网站状态和考试都从这里取原样，不读工作区里可能被改过的那一份。"
        "由 tools/dev/build_starter_manifest.py --write 生成，不要手改。")

TEXT = {
    "written": "清单写好了：{path}（{n} 个文件）。",
    "same": "starter/ 和清单一致（{n} 个文件）。",
    "differ": "starter/ 和清单对不上：",
    "changed": "  改动过：{path}",
    "missing": "  不见了：{path}",
    "added": "  清单里没有：{path}",
    "kept": "  （导师恢复时留下的副本，不算问题：{path}）",
    "learner_edit": "  课文让学习者自己改的文件，改过不算问题：{path}",
    "differ_next": ("是被不小心改了：运行 --restore <路径> 恢复原样（只恢复 doctor 点名的文件）。"
                    "--write 只给建课的人用：故意改了 starter/ 以后，用它更新清单。"),
    "learner_only": "starter/ 和清单一致（{n} 个文件）；只有课文让学习者自己改的文件改过了，不算问题。",
    "learner_refused": ("拒绝：{path} 是课文让学习者自己改的文件，里面是学习者的练习。"
                        "真要恢复原样，再加上 --force（改过的那一份照样会留成 .changed）。"),
    "no_manifest": "读不出清单 {path}（{reason}）。",
    "unknown": "清单里没有这个文件：{path}。能恢复的只有清单里的文件（--check 会列出它们和磁盘的差别）。",
    "outside": "拒绝：{path} 不在 {starter} 里面。",
    "is_folder": "拒绝：{path} 现在是一个文件夹，不是文件。先请人看一眼里面是什么，再处理。",
    "nothing_to_do": "{path} 和原样一样，不用恢复。",
    "restored": "{path} 恢复成原样了。",
    "restored_kept": "{path} 恢复成原样了；改动过的那一份留在 {copy}，没有删除。",
    "bad_entry": "清单里 {path} 这一项坏了（{reason}）。",
}


class Problem(Exception):
    """Something this script cannot do; the message says why."""


def is_noise(name):
    return name in NOISE_NAMES or name.endswith(NOISE_SUFFIXES)


def is_kept_copy(name):
    """A ``.changed`` copy left by ``--restore``."""
    head, _dot, tail = name.rpartition(".changed")
    return bool(head) and (tail == "" or (tail.startswith("-") and tail[1:].isdigit()))


def disk_files(workspace):
    """Sorted workspace-relative POSIX paths of every file under starter/."""
    root = Path(workspace) / STARTER
    found = []
    for folder, names, files in os.walk(str(root)):
        names[:] = sorted(n for n in names if not is_noise(n))
        for name in sorted(files):
            if is_noise(name):
                continue
            full = Path(folder) / name
            found.append(full.relative_to(Path(workspace)).as_posix())
    return sorted(found)


def entry_for(data):
    """A manifest entry for ``data`` (bytes)."""
    entry = {"sha256": hashlib.sha256(data).hexdigest()}
    try:
        entry["text"] = data.decode("utf-8")
    except UnicodeDecodeError:
        entry["base64"] = base64.b64encode(data).decode("ascii")
    return entry


def original_bytes(path, entry):
    try:
        if "text" in entry:
            data = entry["text"].encode("utf-8")
        else:
            data = base64.b64decode(entry["base64"].encode("ascii"), validate=True)
    except (KeyError, AttributeError, ValueError) as exc:
        raise Problem(TEXT["bad_entry"].format(path=path, reason=type(exc).__name__))
    if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
        raise Problem(TEXT["bad_entry"].format(path=path, reason="sha256"))
    return data


def build(workspace):
    """The manifest dict for what is on disk now."""
    files = {}
    for path in disk_files(workspace):
        files[path] = entry_for((Path(workspace) / path).read_bytes())
    return {"schema": SCHEMA, "note": NOTE,
            "learner_edits": [p for p in LEARNER_EDITS if p in files],
            "files": files}


def manifest_text(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def load(manifest):
    try:
        data = json.loads(Path(manifest).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Problem(TEXT["no_manifest"].format(path=manifest, reason=type(exc).__name__))
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise Problem(TEXT["no_manifest"].format(path=manifest, reason="no files"))
    return data


def compare(workspace, data):
    """``(changed, missing, added, kept)``: lists of workspace-relative paths."""
    on_disk = set(disk_files(workspace))
    changed, missing = [], []
    for path, entry in sorted(data["files"].items()):
        full = Path(workspace) / path
        if path not in on_disk or full.is_symlink() or not full.is_file():
            missing.append(path)
        elif hashlib.sha256(full.read_bytes()).hexdigest() != entry.get("sha256"):
            changed.append(path)
    extra = sorted(on_disk - set(data["files"]))
    kept = [p for p in extra if is_kept_copy(p)]
    added = [p for p in extra if not is_kept_copy(p)]
    return changed, missing, added, kept


def write(workspace, manifest):
    data = build(workspace)
    Path(manifest).write_text(manifest_text(data), encoding="utf-8")
    return data


def check(workspace, manifest, out):
    """Compare disk and manifest.  A changed ``learner_edits`` file is named
    on its own line and does not count: the lesson asked for that change."""
    data = load(manifest)
    changed, missing, added, kept = compare(workspace, data)
    edits = set(data.get("learner_edits") or ())
    edited = [path for path in changed if path in edits]
    changed = [path for path in changed if path not in edits]
    if not (changed or missing or added):
        out(TEXT["learner_only" if edited else "same"].format(n=len(data["files"])))
        for path in edited:
            out(TEXT["learner_edit"].format(path=path))
        for path in kept:
            out(TEXT["kept"].format(path=path))
        return 0
    out(TEXT["differ"])
    for key, paths in (("changed", changed), ("missing", missing), ("added", added),
                       ("learner_edit", edited), ("kept", kept)):
        for path in paths:
            out(TEXT[key].format(path=path))
    out(TEXT["differ_next"])
    return 1


def _relative(workspace, typed):
    """The workspace-relative POSIX path of ``typed``.

    A relative path is read from the workspace root (``starter/my-site/index.html``);
    an absolute one must lie inside the workspace's starter folder.
    """
    root = Path(os.path.realpath(str(workspace)))
    candidate = Path(typed)
    if not candidate.is_absolute():
        candidate = root / candidate
    full = Path(os.path.realpath(str(candidate.parent))) / candidate.name
    starter = root / STARTER
    if starter not in full.parents:
        raise Problem(TEXT["outside"].format(path=typed, starter=starter))
    return full.relative_to(root).as_posix()


def _free_copy_name(path):
    copy = Path(str(path) + ".changed")
    number = 2
    while copy.exists() or copy.is_symlink():
        copy = Path(str(path) + ".changed-" + str(number))
        number += 1
    return copy


def restore(workspace, manifest, typed, out, force=False):
    data = load(manifest)
    rel = _relative(workspace, typed)
    if rel not in data["files"]:
        raise Problem(TEXT["unknown"].format(path=rel))
    if rel in (data.get("learner_edits") or ()) and not force:
        raise Problem(TEXT["learner_refused"].format(path=rel))
    original = original_bytes(rel, data["files"][rel])
    full = Path(workspace) / rel
    kept = None
    if full.is_dir() and not full.is_symlink():
        raise Problem(TEXT["is_folder"].format(path=rel))
    if full.is_symlink() or full.exists():
        if full.is_file() and not full.is_symlink() and full.read_bytes() == original:
            out(TEXT["nothing_to_do"].format(path=rel))
            return 0
        # First a copy of the present file, so the learner's version is kept.
        kept = _free_copy_name(full)
        shutil.copy2(str(full), str(kept), follow_symlinks=False)
        if full.is_symlink():
            os.unlink(str(full))        # the link itself is kept in the copy
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(str(full), "wb") as handle:
        handle.write(original)
    if kept is not None:
        out(TEXT["restored_kept"].format(path=rel, copy=Path(kept).relative_to(
            Path(workspace)).as_posix()))
    else:
        out(TEXT["restored"].format(path=rel))
    return 0


def main(argv=None, workspace=None, manifest=None, out=None):
    parser = argparse.ArgumentParser(
        prog="python3 tools/dev/build_starter_manifest.py",
        description="The manifest of the original starter files (plan G11a).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true",
                       help="regenerate tools/courselib/starter_manifest.json from starter/ "
                            "(builders only; never run it in the learner's workspace)")
    group.add_argument("--check", action="store_true",
                       help="compare starter/ with the manifest; exit 1 when they differ")
    group.add_argument("--restore", nargs="+", metavar="PATH",
                       help="keep the present file as PATH.changed, then write the original back")
    parser.add_argument("--force", action="store_true",
                        help="with --restore: also restore a file the learner edits in a lesson")
    args = parser.parse_args(argv)
    workspace = Path(workspace or WORKSPACE)
    manifest = Path(manifest or MANIFEST)
    out = out or (lambda line: sys.stdout.write(line + "\n"))
    try:
        if args.write:
            data = write(workspace, manifest)
            out(TEXT["written"].format(path=manifest, n=len(data["files"])))
            return 0
        if args.check:
            return check(workspace, manifest, out)
        code = 0
        for typed in args.restore:
            code = max(code, restore(workspace, manifest, typed, out, force=args.force))
        return code
    except Problem as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main())
