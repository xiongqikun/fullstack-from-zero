"""``status``: where the learner is and what comes next (plan I4)."""

from .. import cmdkit, progress, status
from ..errors import EXIT_OK, ToolTrouble

SUMMARY = "现在学到哪了，下一步做什么"
DESCRIPTION = """显示你现在学到哪一站、下一步做什么（以及下次对导师说哪一句）、
离下一个落脚点还有几站、累计学了多久、有没有到期的复习，以及距离上次学习过了几天。

不带任何命令运行 python3 tools/course.py，效果和 status 一样。"""

TEXT = {
    "write_help": "同时重新生成学习工作区最外层的 PROGRESS.md",
    "unsaved": "⚠️ 这次学习时间没能记下：{problem}把这一行发给导师。",
}


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "status", SUMMARY, description=DESCRIPTION)
    parser.add_argument("--write", action="store_true", help=TEXT["write_help"])


def run(args):
    app = args.app
    state = app.store.load()
    progress.touch_session(state, app.now)
    unsaved = None
    try:
        app.store.save(state)
    except ToolTrouble as exc:
        # status only shows progress: a learner/ folder that cannot be written
        # must not hide it.  The problem is named in one line at the end.
        unsaved = exc
    facts = status.compute(app, state, app.catalog())
    app.console.out(status.render_text(facts, reminder=getattr(args, "bare", False)))
    if unsaved is not None:
        app.console.out("")
        app.console.out(app.console.paint(TEXT["unsaved"].format(problem=unsaved.summary), "warn"))
    if args.write:
        path = status.write_progress(app, facts)
        app.store.log("progress-written", file=app.rel(path))
        app.console.out("")
        app.console.out(status.TEXT["written"].format(name=app.rel(path)))
    return EXIT_OK
