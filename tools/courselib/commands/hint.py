"""``hint``: reveal the next hint level of a station (plan I4).

Levels 1 to 4 are 方向, 位置, 相似例子, 答案与解释.  Every reveal is logged.
Level 4 marks the station 带扶手完成 and schedules a cold redo 3 to 7 days
later; a learner at a terminal is asked to confirm before seeing it.
"""

from .. import cmdkit, hints, progress
from ..errors import EXIT_OK
from ..ui import indent

SUMMARY = "卡住时要一条提示（一共四级）"
DESCRIPTION = """每运行一次，多看一级提示，一共四级：

  第 1 级  方向          往哪个方向想
  第 2 级  位置          问题出在哪一步、哪个地方
  第 3 级  相似例子      一个长得像、但不是答案的例子
  第 4 级  答案与解释    完整答案

看了第 4 级，这一站会记为「带扶手完成」，3 到 7 天后要不看提示重做一遍。
这不是惩罚：自己做出来一次，才算真的会了。

例子：
  python3 tools/course.py hint 1.6b            看下一级提示
  python3 tools/course.py hint 1.6b --again    重看已经看过的提示"""

TEXT = dict(hints.TEXT)
TEXT.update({
    "station_help": "站点编号，例如 1.6b",
    "again_help": "重新显示已经看过的提示，不看新的一级",
    "yes_help": "看第 4 级（完整答案）之前不再问一遍",
})


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "hint", SUMMARY, description=DESCRIPTION)
    parser.add_argument("station", metavar="<站>", help=TEXT["station_help"])
    parser.add_argument("--again", action="store_true", help=TEXT["again_help"])
    parser.add_argument("--yes", action="store_true", help=TEXT["yes_help"])


def run(args):
    app = args.app
    out = app.console.out
    lesson, station = cmdkit.find_target(app, args.station, want="station")
    station_id = station["id"]
    texts = hints.hints_for(lesson, station_id)
    heading = ("{} {}".format(station_id, station.get("title", ""))).strip()
    state = app.store.load()
    progress.touch_session(state, app.now)
    seen = progress.hint_level(progress.record_of(state, station_id))

    if args.again:
        if seen == 0:
            out(TEXT["again_none"].format(station=station_id))
            app.store.save(state)
            return EXIT_OK
        out(TEXT["again_head"].format(heading=heading))
        for level in range(1, seen + 1):
            out("")
            out("  " + TEXT["level_line"].format(level=level, name=hints.LEVEL_NAMES[level - 1]))
            out(indent(texts[level - 1], 4))
        progress.reread_hint(state, station_id, app.now)
        app.store.save(state, events=[{"type": "hint-again", "station": station_id,
                                       "levels": seen}])
        return EXIT_OK

    if (hints.needs_confirmation(state, station_id) and app.console.may_ask_optional
            and not args.yes):
        after, _before = hints.redo_window(app.now)
        if not app.console.confirm(TEXT["confirm"].format(after=after.isoformat())):
            out(TEXT["declined"].format(station=station_id))
            app.store.save(state)
            return EXIT_OK

    level, scheduled = progress.record_hint(state, station_id, app.now)
    record = progress.record_of(state, station_id)
    app.store.save(state, events=[{"type": "hint", "station": station_id, "level": level,
                                   "repeat": seen >= progress.MAX_HINT,
                                   "scheduled_redo": scheduled,
                                   "status": record.get("status")}])
    if seen >= progress.MAX_HINT:
        out(TEXT["all_seen"])
        out("")
    out(TEXT["head"].format(level=level, name=hints.LEVEL_NAMES[level - 1], heading=heading))
    out("")
    out(indent(texts[level - 1], 2))
    out("")
    if level < progress.MAX_HINT:
        out("  " + TEXT["try_first"].format(station=station_id))
        out("  " + TEXT["more"].format(next=level + 1, name=hints.LEVEL_NAMES[level]))
    else:
        out("  " + TEXT["last"].format(station=station_id))
    if scheduled:
        redo = progress.redo_of(record) or {}
        out("")
        out(indent(TEXT["assisted"].format(after=redo.get("after"), before=redo.get("before")), 2))
    return EXIT_OK
