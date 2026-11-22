"""Journal entries: ``journal/YYYY-MM-DD.md`` (plan I4).

The journal folder belongs to the learner.  The tool only ever appends to a
day's file; it never rewrites or truncates what is already there.
"""

import os

from .errors import ToolTrouble
from .store import reason as os_reason
from .ui import one_line

#: (key, label, required-in-prompt) in the order they are asked and written.
FIELDS = (
    ("done", "做了什么"),
    ("stuck", "卡在哪"),
    ("next", "下次从哪开始"),
    ("unclear", "哪里看不懂"),
    ("slow", "哪里太慢"),
)
CORE = ("done", "stuck", "next")
OPTIONAL = ("unclear", "slow")

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "file_title": "# 学习日志 {date}",
    "entry_title": "## {time}",
    "none": "（无）",
    "cannot_write": "写不了日志文件 {path}（{reason}）。",
    "cannot_write_recovery": "看看学习工作区里的 journal 是不是一个文件夹、有没有写入权限，然后再运行一次。",
}


def entry_text(values, now):
    """The Markdown of one entry.  ``values`` maps field keys to one-line texts."""
    lines = [TEXT["entry_title"].format(time=now.strftime("%H:%M")), ""]
    for key, label in FIELDS:
        text = one_line(values.get(key) or "")
        if key in OPTIONAL and not text:
            continue
        lines.append("- {}：{}".format(label, text or TEXT["none"]))
    return "\n".join(lines) + "\n"


def journal_path(app):
    return app.root / "journal" / (app.today.isoformat() + ".md")


def append_entry(app, values):
    """Append one entry to today's journal file and return the file's path."""
    path = journal_path(app)
    entry = entry_text(values, app.now)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 0:
            with open(str(path), "rb") as handle:
                handle.seek(-1, os.SEEK_END)
                ends_with_newline = handle.read(1) == b"\n"
            prefix = "\n" if ends_with_newline else "\n\n"
        else:
            prefix = TEXT["file_title"].format(date=app.today.isoformat()) + "\n\n"
        with open(str(path), "a", encoding="utf-8", newline="\n") as handle:
            handle.write(prefix + entry)
    except OSError as exc:
        raise ToolTrouble(
            TEXT["cannot_write"].format(path=app.rel(path), reason=os_reason(exc)),
            detail=repr(exc), recovery=TEXT["cannot_write_recovery"])
    return path
