"""The status report: where the learner is and what comes next (plan I4).

``compute`` turns the state and the lesson catalog into a plain dict of facts;
``render_text`` and ``render_markdown`` only format that dict.  Nothing here
writes to disk except ``write_progress``.
"""

from . import progress, review, schedule
from .app import parse_stamp
from .errors import ToolTrouble
from .store import atomic_write_text
from .store import reason as os_reason
from .syllabus import GATES, STAGES, gate_label, gate_titled, landing_points, lesson_key
from .ui import WARN_MARK

SEVENTY = 0.7
LONG_BREAK_DAYS = 10
#: Minutes the explain-back part of a gate takes (COMMON.md section 1, plan
#: G5a): the tutor's questions (two explain-back questions; at gate-0, gate-a
#: and gate-b also a debugging question) and the verdict are four exchanges
#: at 2 minutes, plus the command that records the verdict, rounded up to a
#: multiple of 5.  No sentence of the tool says how many questions there are.
EXPLAIN_MINUTES = 10

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "title": "学习进度 · {date}",
    "no_lessons": (
        "还没有找到课程（stages/ 下面没有可用的 lesson.py）。\n"
        "  如果你刚拿到这个学习工作区，把这句话发给导师。"
    ),
    "here": "你在：{lesson} {title} · 第 {n} 站「{station_title}」（{station}）",
    # When the next step is a lesson's closing steps or the gate after it.
    "here_wrapup": "你在：{lesson} {title} · 收尾",
    "here_gate": "你在：{label}（学完 {lesson} 课以后）",
    "next": "下一步：{text}。下次可以对导师说“{say}”。",
    "next_review": "下一步：{text}；然后{space}{then}。下次可以对导师说“{say}”。",
    "next_plain": "下一步：{text}。",
    "all_done": "已有的课程的站都通过了（{done}/{total} 站）。",
    "landing": "下一个落脚点是{space}{label}（学完 {lesson}），还有 {left} 站",
    # No station left before the landing point (the first line is that lesson).
    "landing_wrapup": "下一个落脚点是{space}{label}（学完 {lesson}）：站都通过了，还差 {lesson} 课的收尾",
    "landing_reached": "落脚点到了：{label}",
    "landing_stations_done": "下一个落脚点是{space}{label}（学完 {lesson}）：站都通过了",
    "landing_stage": "阶段 {stage} 结束",
    "stage": "阶段 {stage}{title}：已完成 {done}/{total} 站（{percent}%）",
    "hours": "累计学习：约 {hours} 小时（{count} 次）",
    "hours_none": "累计学习：今天是第一次记录",
    "hours_note": "（按每次学习第一条和最后一条命令之间的时间算，实际会更多）",
    "review_due": "到期的复习：{n} 条 → python3 tools/course.py review",
    "review_none": "到期的复习：0 条{next}",
    "review_next": "（下一次：{date}）",
    "redo_due": "到期的重做：{stations}（之前带扶手完成，现在不看提示重做一遍，再运行 check）",
    "away": "距离上次学习：{days} 天",
    "away_long": (
        "距离上次学习：{days} 天。隔得有点久，建议先走一遍回归流程："
        "对导师说“我回来了，带我走回归流程”。"
    ),
    # Shown only while the next stage has no lessons in stages/ yet (once
    # they exist, nothing needs preparing and the line would be untrue).
    "seventy": (
        "阶段 {stage} 已完成 70% 以上（{done}/{total} 站）。"
        "把这条告诉导师：下一阶段的课程需要提前准备。"
    ),
    "broken": "{mark} 有 {n} 课加载失败，暂时用不了：{which}。把这条发给导师（导师运行 validate 看详情）。",
    "reminder": (
        "  做完一站 → python3 tools/course.py check {station}",
        "  卡住了   → python3 tools/course.py hint {station}",
        "  收工前   → python3 tools/course.py journal",
    ),
    "station_placeholder": "<站>",
    "written": "已更新 {name}。",
    "cannot_write": "写不了 PROGRESS.md（{reason}）。",
    # PROGRESS.md
    "md_title": "# 学习进度",
    "md_generated": (
        "> 这个文件由 `python3 tools/course.py status --write` 生成，每次生成都会整份覆盖。"
        "不要手改；想记东西请写到 `notes/` 或 `journal/`。\n"
        "> 生成时间：{when}"
    ),
    "md_now": "## 现在在哪",
    "md_stage": "## 阶段 {stage}{title}（{done}/{total} 站）",
    "md_table_head": "| 课 | 站 | 状态 | 首次通过 | 检查次数 | 看过的最高提示 |",
    "md_table_rule": "|---|---|---|---|---|---|",
    "md_review": "## 复习",
    "md_review_line": "- 已排入复习的题目：{total} 条；现在到期：{due} 条",
    "md_review_boxes": "- 各盒数量（间隔 2 天 / 1 周 / 3 周 / 2 个月 / 6 个月）：{boxes}",
    "md_exams": "## 关卡",
    "md_exam_line": "- {gate} {title}（{range}）：{summary}",
    "md_range": "{first} 到 {last} 课",
    "md_range_one": "{first} 课",
    # Where a gate stands, in a few words (``exam`` listing and PROGRESS.md).
    "gate_none": "考题还没写好",
    "gate_new": "还没考过；一场 {n} 题，预计 {minutes} 分钟",
    "gate_partly": "实操题通过了 {covered}/{total} 课；下一场 {n} 题，预计 {minutes} 分钟",
    "gate_open": "第 {n} 场还没批改完（{pending} 题）",
    "gate_practical": "实操题都通过了，还差讲解题",
    "gate_done": "通过了（讲解题 {date}）",
    "gate_done_undated": "通过了",
    # An extra practice sitting (--all after the practical part) still open.
    "gate_practice_open": "；第 {n} 场加练还没批改完（{pending} 题）",
    "st_passed": "通过",
    "st_assisted": "带扶手完成",
    "st_assisted_unchecked": "看过答案，还没检查",
    "st_tried": "试过，还没通过",
    "st_open": "还没开始",
}


# ---------------------------------------------------------------------------
# What comes next: one answer for every command (check, status, journal)
# ---------------------------------------------------------------------------
#: Kinds of ``NextStep``, in the order they are considered.
REVIEW = "review"        # review items are due (only with ``reviews=True``)
STATION = "station"      # the open station of a lesson already begun
LESSON = "lesson"        # the next lesson, not begun yet
WRAPUP = "wrapup"        # every station passed, the whole-lesson check not yet
GATE = "gate"            # the practical part of a gate is due
EXPLAIN = "explain"      # practical part passed, explain-back not recorded as pass
STAGE_END = "stage_end"  # nothing left in the workspace: prepare the next stage
NOTHING = "nothing"      # no usable lessons at all

#: ``state["lesson_checks"][lesson_id]``: when the whole-lesson check passed.
LESSON_CHECKS = "lesson_checks"

NEXT_TEXT = {
    "say_start": "开始上课",
    "say_station": "从 {station} 继续",
    "say_wrapup": "从 {lesson} 的收尾继续",
    "say_lesson": "从 {lesson} 开始",
    "say_gate": "做小关卡 {gate}",
    "say_explain": "请问我 {gate} 的讲解题",
    "say_stage": "准备阶段 {stage}",
    "review": "先做 {n} 条到期的复习：python3 tools/course.py review",
    "station": "打开 {path}，从「第 {n} 站」接着做；做完运行 python3 tools/course.py check {station}",
    "retry": "{station} 检查过 {attempts} 次，还没通过。接着改，再运行 python3 tools/course.py check {station}",
    "verify": "{station} 你看过完整答案，还没运行检查。照着做完后运行 python3 tools/course.py check {station}",
    "lesson": "打开 {path}，从头开始；做完第 1 站运行 python3 tools/course.py check {station}",
    "wrapup": "{lesson} 课的 {n} 站都通过了。收尾先做全课检查：python3 tools/course.py check {lesson}",
    "gate": ("{label}：{n} 道实操题，预计 {minutes} 分钟，讲解题另需约 {explain} 分钟。"
             "开始考试：python3 tools/course.py exam {gate}"),
    "explain": ("{label}的实操题都通过了，还差讲解题（约 {explain} 分钟）：请导师问你讲解题，"
                "评完用 python3 tools/course.py exam {gate} --explain pass 记下（要再来一次就写 again）"),
    "explain_again": "。上一次的讲解题在 {date} 记为“再来一次”",
    "stage_end": "已有的课程都学完了。下一阶段的课还要准备",
    "nothing": "还没有找到课程",
    "open_gate": "{label}还没有通过，它不挡下一课。准备好了就对导师说“{say}”。",
    # A sitting started and not graded yet (not an extra practice sitting).
    "sitting": ("{label}第 {n} 场考试还没批改完（{pending} 题）：做完以后批改："
                "python3 tools/course.py exam {gate} --grade；想放弃这一场重新出题："
                "python3 tools/course.py exam {gate} --new"),
    "open_sitting": ("{label}第 {n} 场考试还没批改完（{pending} 题），它不挡下一课。"
                     "做完以后批改：python3 tools/course.py exam {gate} --grade"),
    "open_explain": ("{label}的实操题都通过了，讲解题还没记为通过，它不挡下一课。"
                     "准备好了就对导师说“{say}”。"),
}


class NextStep(dict):
    """What comes next for the learner: a dict whose keys are also attributes.

    Keys: ``kind`` (one of the constants above), ``text`` (the plain
    sentence, without a final full stop), ``say`` (the sentence to say to
    the tutor, COMMON section 2, without quotation marks), ``lesson``,
    ``station``, ``gate`` (ids or None), ``title``, ``path`` (lesson.md
    relative to the workspace, or ""), ``count`` and ``minutes`` (a gate's
    next sitting), ``then`` (for ``review``: the step after the reviews),
    ``gates`` (``[NextStep]``: gates still open after their lessons, kind
    ``gate`` or ``explain``, each with ``note``, the one line to show).
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


def _step(kind, text, say, **fields):
    step = NextStep(kind=kind, text=text, say=say, lesson=None, station=None, gate=None,
                    title="", path="", count=0, minutes=0, then=None, gates=[])
    step.update(fields)
    return step


def gate_view(catalog, state, gate):
    """A gate's state for the next-step answer (``progress.gate_status``).

    Fields: ``tasks`` (usable tasks), ``practical_done``, ``explain``
    (``"pass"``, ``"again"`` or None), ``explain_date``, ``done``,
    ``in_progress``, ``next_count``, ``next_minutes``, ``attempts`` and
    ``sitting_kind``.
    """
    summary = progress.gate_status(catalog, state, gate)
    return {key: summary[key] for key in ("tasks", "practical_done", "explain", "explain_date",
                                          "done", "in_progress", "next_count", "next_minutes",
                                          "attempts", "sitting_kind")}


def _gate_step(catalog, state, gate, view=None):
    """The ``gate`` or ``explain`` step of an open gate, or None when it is done."""
    view = view or gate_view(catalog, state, gate)
    if view["done"] or not view["tasks"]:
        return None
    title = GATES.get(gate, {}).get("title", gate)
    label = gate_label(gate)
    if view["practical_done"]:
        # Only the explain-back is missing (an extra practice sitting that
        # may be open meanwhile never takes a passed lesson back).
        say = NEXT_TEXT["say_explain"].format(gate=gate)
        text = NEXT_TEXT["explain"].format(gate=gate, label=label, explain=EXPLAIN_MINUTES)
        if view["explain"] == "again" and view["explain_date"]:
            text += NEXT_TEXT["explain_again"].format(date=view["explain_date"])
        return _step(EXPLAIN, text, say, gate=gate, title=title, label=label,
                     note=NEXT_TEXT["open_explain"].format(label=label, say=say))
    say = NEXT_TEXT["say_gate"].format(gate=gate)
    if view["in_progress"]:
        # A sitting is open: say so, with --grade (CLAUDE.md treats it as an exam).
        fields = {"gate": gate, "label": label, "n": view["attempts"], "pending": view["next_count"]}
        return _step(GATE, NEXT_TEXT["sitting"].format(**fields), say, gate=gate, title=title,
                     label=label, count=view["next_count"], minutes=view["next_minutes"],
                     sitting=view["attempts"],
                     note=NEXT_TEXT["open_sitting"].format(**fields))
    return _step(GATE, NEXT_TEXT["gate"].format(gate=gate, label=label, n=view["next_count"],
                                               minutes=view["next_minutes"],
                                               explain=EXPLAIN_MINUTES),
                 say, gate=gate, title=title, label=label, count=view["next_count"],
                 minutes=view["next_minutes"],
                 note=NEXT_TEXT["open_gate"].format(label=label, say=say))


def lesson_checked(state, lesson_id, app=None):
    """Has the whole-lesson check of ``lesson_id`` passed?

    Read from ``state["lesson_checks"]``.  A state written before that key
    existed (2026-11-19) has none: with ``app`` the passed ``lesson-check``
    events of learner/log.jsonl count too.
    """
    checks = state.get(LESSON_CHECKS) if isinstance(state, dict) else None
    if isinstance(checks, dict) and checks.get(lesson_id):
        return True
    return app is not None and lesson_id in logged_lesson_checks(app)


def logged_lesson_checks(app):
    """``{lesson id: stamp}`` of the passed whole-lesson checks in learner/log.jsonl."""
    store = getattr(app, "store", None)
    events = getattr(store, "events", None)
    if events is None:
        return {}
    found = {}
    try:
        for event in events():
            if (event.get("type") == "lesson-check" and event.get("outcome") == "passed"
                    and isinstance(event.get("lesson"), str)):
                found.setdefault(event["lesson"], event.get("ts") or True)
    except ToolTrouble:
        return {}
    return found


def record_lesson_check(state, lesson_id, stamp):
    """Remember that the whole-lesson check of ``lesson_id`` passed at ``stamp``."""
    checks = state.get(LESSON_CHECKS)
    if not isinstance(checks, dict):
        checks = {}
        state[LESSON_CHECKS] = checks
    checks.setdefault(lesson_id, stamp)
    return checks


def _active(state, station_id):
    record = progress.record_of(state, station_id)
    return progress.is_done(record) or int(record.get("attempts") or 0) > 0 \
        or progress.hint_level(record) > 0


def next_step(app, state, catalog=None, reviews=True, after=None):
    """The one answer to "what comes next" for any state of the learner.

    Considered in this order:

    1. review items due today (only with ``reviews=True``; the step after
       them is in ``then``);
    2. the lesson before the current one: its stations all passed but its
       whole-lesson check not (``WRAPUP``: 「从 1.6 的收尾继续」), as long as
       the current lesson has not been begun;
    3. the gate that sits after that lesson (``GATE``: 「做小关卡 gate-a」, or
       ``EXPLAIN`` when the practical part is passed and the explain-back is
       not recorded as pass: 「请问我 gate-a 的讲解题」), as long as the
       current lesson has not been begun;
    4. the current lesson (the first with a station not passed): its first
       open station when it was begun (``STATION``: 「从 1.6b 继续」), else
       the lesson itself (``LESSON``: 「从 1.7 开始」; before anything at all
       has been done: 「开始上课」);
    5. nothing left: ``STAGE_END`` (「准备阶段 2」, the stage after the last
       one in the workspace).

    ``after`` (a lesson) answers from the point of view of a learner who has
    just finished that lesson (``check`` after its last station or its
    whole-lesson check): it is taken as the lesson before the current one,
    and the current one is the first lesson after it with a station not
    passed, also when an earlier lesson still has one.

    A gate never blocks the next lesson: gates whose lessons are all passed
    and that are still open are listed in ``gates`` (each with its ``note``
    line) whatever the main step is.
    """
    catalog = catalog or app.catalog()
    lessons = list(catalog.lessons)
    if not lessons:
        return _step(NOTHING, NEXT_TEXT["nothing"], "")
    def finished(lesson):
        return all(progress.is_done(progress.record_of(state, sid)) for sid in lesson.station_ids)

    current, previous = None, None
    just_finished = after is not None and after in lessons
    if just_finished:
        previous = after
        current = next((lesson for lesson in lessons[lessons.index(after) + 1:]
                        if not finished(lesson)), None)
    else:
        for lesson in lessons:
            if not finished(lesson):
                current = lesson
                break
            previous = lesson
    begun = current is not None and any(_active(state, sid) for sid in current.station_ids)
    anything = any(_active(state, sid) for lesson in lessons for sid in lesson.station_ids)

    open_gates = []
    gate_after = {gate["after"]: gate_id for gate_id, gate in GATES.items()}
    limit = lesson_key(current.id) if current is not None else None
    for lesson in lessons:
        if limit is not None and lesson_key(lesson.id) >= limit:
            break
        gate_id = gate_after.get(lesson.id)
        if gate_id and finished(lesson):
            step = _gate_step(catalog, state, gate_id)
            if step is not None:
                open_gates.append(step)

    main = None
    if previous is not None and (just_finished or not begun):
        if previous.station_ids and not lesson_checked(state, previous.id, app):
            # The gate after this lesson comes after its closing steps.
            open_gates = [g for g in open_gates if g.gate != gate_after.get(previous.id)]
            main = _step(WRAPUP, NEXT_TEXT["wrapup"].format(lesson=previous.id,
                                                            n=len(previous.station_ids)),
                         NEXT_TEXT["say_wrapup"].format(lesson=previous.id),
                         lesson=previous.id, title=previous.title,
                         path=previous.rel + "/lesson.md", count=len(previous.station_ids))
        elif gate_after.get(previous.id):
            gate_step = next((g for g in open_gates if g.gate == gate_after[previous.id]), None)
            if gate_step is not None:
                main = gate_step
                open_gates = [g for g in open_gates if g is not gate_step]
    if main is None and current is not None:
        path = current.rel + "/lesson.md"
        if begun:
            station_id = next(sid for sid in current.station_ids
                              if not progress.is_done(progress.record_of(state, sid)))
            station = current.station(station_id)
            record = progress.record_of(state, station_id)
            fields = {"station": station_id, "title": str(station.get("title", "")),
                          "n": current.station_number(station_id), "path": path,
                          "attempts": int(record.get("attempts") or 0)}
            if record.get("status") == progress.ASSISTED:
                text = NEXT_TEXT["verify"].format(**fields)
            elif fields["attempts"] > 0:
                text = NEXT_TEXT["retry"].format(**fields)
            else:
                text = NEXT_TEXT["station"].format(**fields)
            main = _step(STATION, text, NEXT_TEXT["say_station"].format(station=station_id),
                         lesson=current.id, station=station_id, title=fields["title"], path=path)
        else:
            first = current.station_ids[0] if current.station_ids else ""
            say = (NEXT_TEXT["say_lesson"].format(lesson=current.id) if anything
                   else NEXT_TEXT["say_start"])
            main = _step(LESSON, NEXT_TEXT["lesson"].format(lesson=current.id,
                                                            title=current.title,
                                                            path=path, station=first),
                         say, lesson=current.id, station=first or None,
                         title=current.title, path=path)
    if main is None:
        stage = max(lesson.stage for lesson in lessons if lesson.stage is not None) \
            if any(lesson.stage is not None for lesson in lessons) else 0
        main = _step(STAGE_END, NEXT_TEXT["stage_end"],
                     NEXT_TEXT["say_stage"].format(stage=stage + 1), stage=stage + 1)
    main["gates"] = open_gates
    if reviews:
        due = review.due_count(state, catalog, app.today)
        if due:
            return _step(REVIEW, NEXT_TEXT["review"].format(n=due), main.say, then=main,
                         gates=open_gates, count=due)
    return main


def _stage_title(stage):
    entry = STAGES.get(stage)
    return " " + entry["title"] if entry else ""


def station_label(record):
    """The status of a station in words."""
    if record.get("status") == progress.ASSISTED:
        return TEXT["st_assisted"] if progress.is_done(record) else TEXT["st_assisted_unchecked"]
    if progress.is_done(record):
        return TEXT["st_passed"]
    if int(record.get("attempts") or 0) > 0:
        return TEXT["st_tried"]
    return TEXT["st_open"]


def compute(app, state, catalog):
    """Collect every fact the status report shows."""
    today = app.today
    rows = []
    for lesson, station in catalog.stations():
        record = progress.record_of(state, station["id"])
        rows.append({"lesson": lesson, "station": station, "record": record,
                     "done": progress.is_done(record)})
    total = len(rows)
    done = sum(1 for row in rows if row["done"])
    current = next((row for row in rows if not row["done"]), None)

    stages = []
    for stage in catalog.stages():
        stage_rows = [row for row in rows if row["lesson"].stage == stage]
        stage_done = sum(1 for row in stage_rows if row["done"])
        stages.append({"stage": stage, "title": _stage_title(stage), "rows": stage_rows,
                       "done": stage_done, "total": len(stage_rows),
                       "percent": int(100 * stage_done / len(stage_rows)) if stage_rows else 0})

    facts = {
        "today": today, "now": app.now, "total": total, "done": done,
        "rows": rows, "stages": stages, "current": None, "landing": None,
        "stage": None, "seventy": False,
        "minutes": progress.total_minutes(state),
        "session_count": len(state.get("sessions", [])),
        "days_away": progress.days_away(state, today),
        "review_due": review.due_count(state, catalog, today),
        "review_next": review.next_due(state, catalog, today),
        "review_total": len(state.get("review", {})),
        "review_boxes": schedule.box_counts(state),
        "redo_due": [row["station"]["id"] for row in rows
                     if progress.redo_is_due(row["record"], today)],
        "broken": [(lesson.id or lesson.rel, lesson.error) for lesson in catalog.broken],
        "exams": state.get("exams", {}),
        "gates": _gates(catalog, state),
    }
    facts["next"] = next_step(app, state, catalog)
    # The first line follows the next step; the landing and stage lines follow
    # the same lesson: at a lesson's closing steps or the gate after it, that
    # lesson, else the lesson of the first open station.
    lesson = _here_lesson(catalog, facts["next"])
    if current is not None:
        station = current["station"]
        record = current["record"]
        facts["current"] = {
            "lesson_id": current["lesson"].id, "lesson_title": current["lesson"].title,
            "path": current["lesson"].rel + "/lesson.md",
            "station_id": station["id"], "station_title": str(station.get("title", "")),
            "number": current["lesson"].station_number(station["id"]),
            "attempts": int(record.get("attempts") or 0),
            "answer_seen": record.get("status") == progress.ASSISTED,
        }
        lesson = lesson or current["lesson"]
    if lesson is None:
        return facts
    facts["stage"] = next((item for item in stages if item["stage"] == lesson.stage), None)
    if facts["stage"] and facts["stage"]["total"]:
        ratio = facts["stage"]["done"] / float(facts["stage"]["total"])
        next_stage_ready = any(item.stage is not None and item.stage > lesson.stage
                               for item in catalog.lessons)
        facts["seventy"] = SEVENTY <= ratio < 1.0 and not next_stage_ready
    facts["landing"] = _landing(catalog, rows, lesson)
    return facts


def _main_step(step):
    """The step itself, or for due reviews the step after them."""
    if step is not None and step.kind == REVIEW and step.then is not None:
        return step.then
    return step


def _here_lesson(catalog, step):
    """The lesson whose closing steps, or the gate after which, is the next step; else None."""
    main = _main_step(step)
    if main is None:
        return None
    if main.kind == WRAPUP:
        lesson_id = main.lesson
    elif main.kind in (GATE, EXPLAIN) and main.gate in GATES:
        lesson_id = GATES[main.gate]["after"]
    else:
        return None
    return next((lesson for lesson in catalog.lessons if lesson.id == lesson_id), None)


def _range(lesson_ids):
    if not lesson_ids:
        return ""
    if len(lesson_ids) == 1:
        return TEXT["md_range_one"].format(first=lesson_ids[0])
    return TEXT["md_range"].format(first=lesson_ids[0], last=lesson_ids[-1])


def _gates(catalog, state):
    """``progress.gate_status`` of every gate the catalogue knows, plus its lesson range."""
    gates = []
    for gate in catalog.gate_ids():
        summary = progress.gate_status(catalog, state, gate)
        summary["range"] = _range(catalog.gate_lesson_ids(gate))
        gates.append(summary)
    return gates


def gate_state_words(summary):
    """Where one gate stands, in a few words (``exam`` listing, PROGRESS.md).

    ``summary`` is a ``progress.gate_status`` result.
    """
    if not summary.tasks:
        return TEXT["gate_none"]
    # An open sitting after the practical part is extra practice: the gate
    # stands where it stood, the sitting is added at the end.
    practice = ""
    if summary.in_progress and summary.practical_done:
        practice = TEXT["gate_practice_open"].format(n=summary.attempts,
                                                     pending=summary.next_count)
    if summary.done:
        if summary.explain_date:
            return TEXT["gate_done"].format(date=summary.explain_date) + practice
        return TEXT["gate_done_undated"] + practice
    if summary.practical_done:
        return TEXT["gate_practical"] + practice
    if summary.in_progress:
        return TEXT["gate_open"].format(n=summary.attempts, pending=summary.next_count)
    if not (summary.attempts or summary.passed or summary.open):
        return TEXT["gate_new"].format(n=summary.next_count, minutes=summary.next_minutes)
    covered = len(summary.lessons) - len(summary.open_lessons)
    return TEXT["gate_partly"].format(covered=covered, total=len(summary.lessons),
                                      n=summary.next_count, minutes=summary.next_minutes)


def _landing(catalog, rows, lesson):
    """The next landing point at or after ``lesson`` and the stations left to it."""
    gates = landing_points()
    candidates = {}
    for stage in catalog.stages():
        in_stage = catalog.lessons_in_stage(stage)
        if in_stage:
            candidates[in_stage[-1].id] = TEXT["landing_stage"].format(stage=stage)
    known = {item.id for item in catalog.lessons}
    for lesson_id, gate_id in gates.items():
        if lesson_id in known:
            candidates[lesson_id] = gate_label(gate_id)
    here = lesson_key(lesson.id)
    ahead = sorted((lesson_key(lesson_id), lesson_id) for lesson_id in candidates
                   if lesson_key(lesson_id) >= here)
    if not ahead:
        return None
    target_key, target = ahead[0]
    left = sum(1 for row in rows
               if not row["done"] and lesson_key(row["lesson"].id) <= target_key)
    return {"lesson_id": target, "label": candidates[target], "left": left}


def _lines(facts):
    """The body lines shared by the terminal report and PROGRESS.md."""
    lines = []
    current = facts["current"]
    if facts["total"] == 0:
        return [TEXT["no_lessons"]]
    step = facts.get("next")
    main = _main_step(step)
    if main and main.kind == WRAPUP:
        lines.append(TEXT["here_wrapup"].format(lesson=main.lesson, title=main.title))
    elif main and main.kind in (GATE, EXPLAIN) and main.gate in GATES:
        lines.append(TEXT["here_gate"].format(label=main.label,
                                              lesson=GATES[main.gate]["after"]))
    elif current is None:
        lines.append(TEXT["all_done"].format(done=facts["done"], total=facts["total"]))
    else:
        lines.append(TEXT["here"].format(
            lesson=current["lesson_id"], title=current["lesson_title"], n=current["number"],
            station_title=current["station_title"], station=current["station_id"]))
    lines += next_lines(facts.get("next"))
    landing = facts["landing"]
    if landing:
        lines.append(_landing_line(landing, main))
    stage = facts["stage"]
    if stage:
        lines.append(TEXT["stage"].format(stage=stage["stage"], title=stage["title"],
                                          done=stage["done"], total=stage["total"],
                                          percent=stage["percent"]))
    if facts["session_count"] > 1 or facts["minutes"] > 0:
        lines.append(TEXT["hours"].format(hours="%.1f" % (facts["minutes"] / 60.0),
                                          count=facts["session_count"])
                     + TEXT["hours_note"])
    else:
        lines.append(TEXT["hours_none"])
    if facts["review_due"]:
        lines.append(TEXT["review_due"].format(n=facts["review_due"]))
    else:
        upcoming = ""
        if facts["review_next"] is not None:
            upcoming = TEXT["review_next"].format(date=facts["review_next"].isoformat())
        lines.append(TEXT["review_none"].format(next=upcoming))
    if facts["redo_due"]:
        lines.append(TEXT["redo_due"].format(stations="、".join(facts["redo_due"])))
    away = facts["days_away"]
    if away is not None:
        key = "away_long" if away > LONG_BREAK_DAYS else "away"
        lines.append(TEXT[key].format(days=away))
    if facts["seventy"] and facts["stage"]:
        stage = facts["stage"]
        lines.append(TEXT["seventy"].format(stage=stage["stage"], done=stage["done"],
                                            total=stage["total"]))
    if facts["broken"]:
        which = "、".join(name for name, error in facts["broken"])
        lines.append(TEXT["broken"].format(mark=WARN_MARK, n=len(facts["broken"]), which=which))
    return lines


def _landing_line(landing, main):
    """The landing line; never 「还有 0 站」."""
    fields = {"label": landing["label"], "lesson": landing["lesson_id"], "left": landing["left"],
              "space": " " if landing["label"][:1].isascii() else ""}
    if landing["left"]:
        return TEXT["landing"].format(**fields)
    kind = main.kind if main else None
    if kind == WRAPUP and main.lesson == landing["lesson_id"]:
        return TEXT["landing_wrapup"].format(**fields)
    if kind in (GATE, EXPLAIN):
        return TEXT["landing_reached"].format(**fields)
    return TEXT["landing_stations_done"].format(**fields)


def next_lines(step):
    """The 「下一步：……」 line of a ``NextStep`` and one line per open gate."""
    if not step or step.kind == NOTHING:
        return []
    if step.kind == REVIEW and step.then is not None:
        then = step.then.text
        lines = [TEXT["next_review"].format(text=step.text, then=then, say=step.say,
                                            space=" " if then[:1].isascii() else "")]
    elif step.say:
        lines = [TEXT["next"].format(text=step.text, say=step.say)]
    else:
        lines = [TEXT["next_plain"].format(text=step.text)]
    lines += [gate.note for gate in step.gates]
    return lines


def render_text(facts, reminder=False):
    """The report for the terminal."""
    out = [TEXT["title"].format(date=facts["today"].isoformat()), ""]
    out += ["  " + line for line in _lines(facts)]
    if reminder:
        station = facts["current"]["station_id"] if facts["current"] else TEXT["station_placeholder"]
        out.append("")
        out += [line.format(station=station) for line in TEXT["reminder"]]
    return "\n".join(out)


def _day(text):
    moment = parse_stamp(text) if text else None
    return moment.date().isoformat() if moment else ""


def render_markdown(facts):
    """The content of PROGRESS.md."""
    out = [TEXT["md_title"], "",
           TEXT["md_generated"].format(when=facts["now"].strftime("%Y-%m-%d %H:%M")), "",
           TEXT["md_now"], ""]
    out += ["- " + line.replace("\n  ", " ") for line in _lines(facts)]
    for stage in facts["stages"]:
        out += ["", TEXT["md_stage"].format(stage=stage["stage"], title=stage["title"],
                                            done=stage["done"], total=stage["total"]), "",
                TEXT["md_table_head"], TEXT["md_table_rule"]]
        for row in stage["rows"]:
            lesson, station, record = row["lesson"], row["station"], row["record"]
            cells = [
                f"{lesson.id} {_cell(lesson.title)}",
                "{} {}".format(station["id"], _cell(str(station.get("title", "")))),
                station_label(record),
                _day(record.get("first_pass")),
                str(int(record.get("attempts") or 0)),
                str(progress.hint_level(record)),
            ]
            out.append("| " + " | ".join(cells) + " |")
    out += ["", TEXT["md_review"], "",
            TEXT["md_review_line"].format(total=facts["review_total"], due=facts["review_due"]),
            TEXT["md_review_boxes"].format(
                boxes=" / ".join(str(count) for count in facts["review_boxes"]))]
    if facts.get("gates"):
        out += ["", TEXT["md_exams"], ""]
        for gate in facts["gates"]:
            out.append(TEXT["md_exam_line"].format(
                gate=gate["gate"], title=gate_titled(gate["gate"]), range=gate["range"] or "-",
                summary=gate_state_words(gate)))
    return "\n".join(out) + "\n"


def _cell(text):
    """Text that is safe inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def write_progress(app, facts):
    """Regenerate PROGRESS.md in the workspace root (atomic)."""
    path = app.root / "PROGRESS.md"
    try:
        atomic_write_text(path, render_markdown(facts))
    except OSError as exc:
        raise ToolTrouble(TEXT["cannot_write"].format(reason=os_reason(exc)),
                          detail=repr(exc))
    return path
