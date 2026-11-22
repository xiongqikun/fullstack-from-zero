"""``scenario``: build a practice state under the playground (plan I4).

``scenario <id> [--reset]`` builds the scenario ``<id>`` of a lesson in
``<playground>/<id>`` and prints where it is and what to do next, including
the exact ``cd`` command.  The playground is ``COURSE_PLAYGROUND`` or
``~/Developer/playground``.

Safety (all enforced by ``courselib.scenario``; this command adds none of its
own deletions):

- nothing is written outside the playground (links are resolved first, so a
  link or ``..`` cannot lead out of it);
- a folder that already holds something is never overwritten without
  ``--reset``;
- ``--reset`` deletes a folder only when it carries the tool's marker file
  ``.playground`` and lies inside the playground.

A scenario that is already built completely is not rebuilt: the command shows
where it is again (exit 0).  ``--reset`` builds it afresh.  A build that never
finished (Ctrl+C, a failing builder: the marker says ``complete: false``) is
rebuilt by the plain command, without ``--reset``.
"""

import shlex

from .. import cmdkit, progress
from .. import scenario as scenarios
from ..catalog import STATION_ID
from ..errors import EXIT_NOT_YET, EXIT_OK, UsageProblem

SUMMARY = "搭一个练习场景（在练习场里，随便改、改坏了可以重来）"
DESCRIPTION = """在练习场里搭一个练习用的文件夹，然后告诉你它在哪、接下来做什么。
练习场默认在 ~/Developer/playground，里面的东西都可以随便改，改坏了可以重搭。

例子：
  python3 tools/course.py scenario 1.6            搭 1.6 课开始前的状态
  python3 tools/course.py scenario 1.6b           搭 1.6b 这一站专用的练习场景
  python3 tools/course.py scenario 1.6 --reset    删掉旧的那份，重新搭一份
  python3 tools/course.py scenario                列出所有可以搭的练习场景

安全规则：工具只在练习场里面动手；已经有东西的文件夹，不加 --reset 不会覆盖；
--reset 只删除工具自己搭的文件夹（里面有 .playground 标记文件的）。"""

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "target_help": "练习场景的编号，例如 1.6（这一课开始前的状态）或 1.6b",
    "reset_help": "删掉工具以前搭的那一份，重新搭（只删有 .playground 标记的文件夹）",
    "seed_help": "给测试用：固定随机数，让每次搭出来的内容一样",
    "list_head": "可以搭的练习场景（{n} 个）：",
    "list_line": "  {id:<14}{lesson} {title}",
    "list_usage": "搭一个：python3 tools/course.py scenario <编号>，例如 python3 tools/course.py scenario {example}",
    "list_none": "现在还没有任何课程提供练习场景。",
    "unknown": "没有「{text}」这个练习场景。",
    "unknown_lesson": "{lesson} 课的练习场景有：{ids}",
    "unknown_all": "不带参数运行 python3 tools/course.py scenario 可以看到全部练习场景。",
    "built": "练习场景 {id} 搭好了。",
    "rebuilt": "练习场景 {id} 已经删掉旧的、重新搭好了。",
    "already": "练习场景 {id} 之前已经搭好了（{built}），这次没有动它。",
    "already_reset": "想从头再来一份（会删掉你在里面做过的改动）：{command}",
    "where": "位置：{path}",
    "todo_head": "这里有什么：",
    "next_head": "接下来：",
    "step_cd": "进入练习场景：cd {path}",
    "step_check": "做完以后回到学习工作区，再运行检查：cd {workspace}，然后 python3 tools/course.py check {station}",
    "step_back": "回到学习工作区：cd {workspace}",
    "step_lesson": "接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd {workspace}",
    "safe": "练习场里的东西随便改，练习场外面的文件不会受影响。",
    "safe_reset": "改乱了可以重搭一份：{command}",
    "reset_command": "python3 tools/course.py scenario {id} --reset",
    "interrupted": (
        "搭建被打断了，练习场景 {id} 没有搭完整，先别在里面做练习。"
        "重新搭一份：python3 tools/course.py scenario {id}"
    ),
}


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "scenario", SUMMARY, description=DESCRIPTION)
    parser.add_argument("target", nargs="?", metavar="<场景>", help=TEXT["target_help"])
    parser.add_argument("--reset", action="store_true", help=TEXT["reset_help"])
    parser.add_argument("--seed", type=int, metavar="<数字>", help=cmdkit.argparse.SUPPRESS)
    return parser


def run(args):
    app = args.app
    if not args.target:
        return _list(app)
    lesson, key = _resolve(app, args.target)
    typed = cmdkit.clean_id(args.target)
    state = app.store.load()
    progress.touch_session(state, app.now)
    scenarios.check_playground(app)
    folder = scenarios.scenario_folder(app, lesson.scenario_id(key))
    existing = scenarios.read_info(folder)
    if (not args.reset and existing.exists and existing.id == lesson.scenario_id(key)
            and not folder.is_symlink()):
        app.store.save(state)
        _report(app, lesson, key, existing, TEXT["already"].format(
            id=existing.id, built=_day(existing.built)), again=True, typed=typed)
        return EXIT_OK
    was_there = folder.exists()
    try:
        info = scenarios.build_lesson_scenario(app, lesson, key, seed=args.seed,
                                               reset=args.reset, typed=typed)
    except KeyboardInterrupt:
        app.console.out("")
        app.console.out(TEXT["interrupted"].format(id=lesson.scenario_id(key)))
        return EXIT_NOT_YET
    app.store.save(state)
    headline = TEXT["rebuilt" if (args.reset and was_there) else "built"].format(id=info.id)
    _report(app, lesson, key, info, headline, typed=typed)
    return EXIT_OK


def _resolve(app, text):
    """``(lesson, key)`` for what the learner typed, or a worded usage error."""
    typed = cmdkit.clean_id(text)
    catalog = app.catalog()
    found = catalog.scenario(typed)
    if found is not None:
        lesson, key, _builder = found
        return lesson, key
    # A lesson module that failed to load is the tool's problem, not a typo.
    lesson_part = typed.split("-")[0]
    match = STATION_ID.match(lesson_part)
    lesson_id = match.group(1) if match else lesson_part
    cmdkit._raise_if_broken(catalog, lesson_id)
    lesson = catalog.lesson(lesson_id)
    message = TEXT["unknown"].format(text=str(text).strip())
    if lesson is not None and lesson.scenarios:
        ids = " ".join(lesson.scenario_id(k) for k in lesson.scenarios)
        raise UsageProblem(message, suggestion=TEXT["unknown_lesson"].format(
            lesson=lesson.id, ids=ids))
    raise UsageProblem(message, suggestion=TEXT["unknown_all"])


def _list(app):
    out = app.console.out
    catalog = app.catalog()
    rows = []
    for lesson in catalog.lessons:
        for key in lesson.scenarios:
            rows.append((lesson.scenario_id(key), lesson))
    if not rows:
        out(TEXT["list_none"])
        return EXIT_OK
    out(TEXT["list_head"].format(n=len(rows)))
    for scenario_id, lesson in rows:
        out(TEXT["list_line"].format(id=scenario_id, lesson=lesson.id, title=lesson.title))
    out("")
    out(TEXT["list_usage"].format(example=rows[0][1].id))
    return EXIT_OK


def _day(stamp):
    text = str(stamp or "")
    return text[:16].replace("T", " ") if text else "时间不详"


def shell_path(app, path):
    """A path the learner can paste after ``cd``: ``~`` kept, the rest quoted if needed."""
    shown = app.show(path)
    if shown == "~":
        return shown
    if shown.startswith("~/"):
        rest = shown[2:]
        return "~/" + (rest if shlex.quote(rest) == rest else shlex.quote(rest))
    return shlex.quote(shown)


def _station_for(lesson, key):
    """The station whose check goes with scenario ``key`` (None if unclear).

    ``start`` is the state before the whole lesson: which station looks at it
    is the lesson's business (the first station may be a quiz), so no station
    is named and the learner is sent back to the lesson text.
    """
    if key == "start":
        return None
    head = str(key).split("-")[0]
    return head if head in lesson.station_ids else None


def reset_command(typed):
    """The full command that rebuilds the scenario the learner typed as ``typed``."""
    return TEXT["reset_command"].format(id=typed)


def _report(app, lesson, key, info, headline, again=False, typed=None):
    out = app.console.out
    out(app.console.paint(headline, "ok"))
    out(TEXT["where"].format(path=app.show(info.path)))
    if info.todo:
        out("")
        out(TEXT["todo_head"])
        for line in info.todo:
            out("  " + line)
    out("")
    out(TEXT["next_head"])
    # A todo line that already gives a cd (usually one folder deeper) wins:
    # two different cd commands on one screen confuse a beginner.
    steps = []
    if not any("cd " in str(line) for line in (info.todo or [])):
        steps.append(TEXT["step_cd"].format(path=shell_path(app, info.path)))
    station = _station_for(lesson, key)
    workspace = shell_path(app, app.root)
    if station:
        steps.append(TEXT["step_check"].format(workspace=workspace, station=station))
    elif key == "start":
        steps.append(TEXT["step_lesson"].format(workspace=workspace))
    else:
        steps.append(TEXT["step_back"].format(workspace=workspace))
    for number, step in enumerate(steps, 1):
        out(f"  {number}. {step}")
    out("")
    command = reset_command(typed or info.id)
    if again:
        out(TEXT["already_reset"].format(command=command))
    else:
        out(TEXT["safe"])
        out(TEXT["safe_reset"].format(command=command))
