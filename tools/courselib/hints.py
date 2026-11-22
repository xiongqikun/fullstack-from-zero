"""The four hint levels of a station (plan I3, I4).

A lesson gives every station exactly four hints, from vague to complete:
方向 → 位置 → 相似例子 → 答案与解释.  ``hint`` reveals the next level each
time it is called and logs it.  Level 4 is the full answer: after it the
station counts as 带扶手完成 and a cold redo is due 3 to 7 days later.
"""

from . import progress
from .errors import ToolTrouble

LEVEL_NAMES = ("方向", "位置", "相似例子", "答案与解释")

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "no_hints": "这一站（{station}）的提示还没有写好，或者不是四条。",
    "head": "提示 {level}/4（{name}）· {heading}",
    "more": "还不够的话，再运行一次同样的命令，看下一级（第 {next} 级：{name}）。",
    "try_first": "先照这条提示自己再试一次，试完运行：python3 tools/course.py check {station}",
    "last": "这是最后一级，已经是完整的答案和解释。照着做完后运行：python3 tools/course.py check {station}",
    "confirm": (
        "第 4 级是完整答案。看了以后这一站会记为「带扶手完成」，"
        "{after} 之后还要不看提示重做一次。现在看吗？"
    ),
    "declined": "好，先不看答案。前三级提示随时可以重看：python3 tools/course.py hint {station} --again",
    "assisted": (
        "这一站现在记为「带扶手完成」。这很正常：看答案也是学习的一种方式。\n"
        "请在 {after} 到 {before} 之间，不看提示把这一站重做一遍"
        "（到时候 status 会提醒你）。重做通过后就记为「通过」。"
    ),
    "all_seen": "四级提示都已经看过了，下面重新显示第 4 级。",
    "again_head": "已经看过的提示 · {heading}",
    "again_none": "这一站还没有看过任何提示。运行 python3 tools/course.py hint {station} 看第 1 级。",
    "level_line": "第 {level} 级（{name}）",
}


def hints_for(lesson, station_id):
    """The four hint strings of a station; raises ``ToolTrouble`` when unusable."""
    hints = lesson.hints.get(station_id)
    if (not isinstance(hints, (list, tuple)) or len(hints) != 4
            or not all(isinstance(text, str) and text.strip() for text in hints)):
        raise ToolTrouble(TEXT["no_hints"].format(station=station_id),
                          where=lesson.rel + "/lesson.py")
    return [text.strip() for text in hints]


def redo_window(now):
    """``(after, before)`` dates of the cold redo if level 4 is shown now."""
    import datetime
    return (now.date() + datetime.timedelta(days=progress.REDO_EARLIEST_DAYS),
            now.date() + datetime.timedelta(days=progress.REDO_LATEST_DAYS))


def next_level(state, station_id):
    """The level the next call would reveal (1 to 4)."""
    record = progress.record_of(state, station_id)
    return min(progress.hint_level(record) + 1, progress.MAX_HINT)


def needs_confirmation(state, station_id):
    """True when the next call reveals the answer for the first time and it matters."""
    record = progress.record_of(state, station_id)
    return (progress.hint_level(record) == progress.MAX_HINT - 1
            and record.get("status") != progress.PASSED)
