"""``check``: run the check of one station or of a whole lesson (plan I4).

One station (``check 1.6a``): optionally ask for a 1-5 confidence rating,
run the check under guard, print exactly one of the three outcomes, log the
attempt with the highest hint level used, and store the result in
learner/last-result.json for the tutor.

A whole lesson (``check 1.6``): stations that already passed are listed as
passed and are not run again (a later station may legitimately have changed
the practice state an earlier one looked at); stations that are still open
are checked now.  ``--again`` re-runs every station.

After an outcome the learner is told where to pick up next time, in the
canonical sentences the lessons and the tutor quote (tool-api.md section
6.8): 「下次可以对导师说“从 1.6b 继续”。」 after a station,
「下次可以对导师说“从 1.6 的收尾继续”。」 after the last one, and after the
whole-lesson check what ``status.next_step(..., after=lesson)`` answers: the
gate that is due
(``syllabus.GATES[gate]["after"]`` is this lesson and the gate is not done:
「…“做小关卡 gate-b”。」, or 「…“请问我 gate-b 的讲解题”。」 when only the
explain-back is missing), the next lesson (「…“从 1.7 开始”。」), or the end of
the stage (「…“准备阶段 2”。」), plus one line for every gate still open after
its lessons.  A passed whole-lesson check is remembered in
``state["lesson_checks"][lesson]`` (the time it first passed), so that
``status`` and ``journal`` know the closing steps were reached.
"""

import copy
import re

from .. import cmdkit, progress, runner, schedule
from .. import status as next_steps
from ..app import parse_stamp
from ..errors import EXIT_NOT_YET, EXIT_OK, EXIT_PROBLEM
from ..normalize import parse_int
from ..syllabus import lesson_key
from ..ui import OK_MARK

#: The closing steps include the backup routine from this lesson on (COMMON.md section 3).
BACKUP_FROM = "1.12"
_RULE_HEADING = re.compile(r"^###\s+([A-Z]+-\d{2})\s+(.*)$")

SUMMARY = "检查一站或一课的练习"
DESCRIPTION = """检查你的练习做到了没有。结果只会是三种之一：

  通过          做到了。
  还没达标      还差一点：会告诉你看了哪里、看到了什么、还缺什么，但不给答案。
  检查器出问题  工具自己出了问题，不是你的错：把屏幕上那一段发给导师。

例子：
  python3 tools/course.py check 1.6a     检查 1.6 课的第 1 站
  python3 tools/course.py check 1.6      全课检查：还没通过的站现在检查，已通过的不重复"""

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "target_help": "站点编号（例如 1.6a）或课程编号（例如 1.6）",
    "answer_help": "提前给出问答题或选择题的回答；有几道题就写几次，按提问的顺序",
    "confidence_help": "检查前你有多大把握已经做对（1 完全没底，5 很有把握）",
    "again_help": "全课检查时，把已经通过的站也重新检查一遍",
    "confidence_prompt": (
        "检查之前先估一下：这一站你有多大把握已经做对？"
        "输入 1 到 5（1 完全没底，5 很有把握），不想估就直接回车："
    ),
    "save_point": "存档点 {station}：到这里可以安全停下。",
    "next_station": "下一站：{next}「{title}」。下次可以对导师说“从 {next} 继续”。",
    "lesson_wrapup": "{lesson} 课的 {n} 站都通过了。收尾先做全课检查：python3 tools/course.py check {lesson}",
    "lesson_wrapup_resume": "下次可以对导师说“从 {lesson} 的收尾继续”。",
    "lesson_remaining": "{lesson} 课还没通过的站：{stations}",
    "resume_station": "下次可以对导师说“从 {station} 继续”。",
    "redo_done": "这次是不看提示的重做，通过了。这一站从「带扶手完成」改记为「通过」。",
    "assisted": (
        "这一站记为「带扶手完成」（你看过完整答案）。"
        "请在 {after} 到 {before} 之间不看提示重做一遍，再运行这条检查命令。"
    ),
    "enrolled": "有 {n} 道复习题排进了复习计划，{date} 起可以做：python3 tools/course.py review",
    "retry": "先自己再试一次。卡住了可以要一条提示：python3 tools/course.py hint {station}",
    "retry_hinted": (
        "先照提示再试一次。还不够，可以看下一级提示："
        "python3 tools/course.py hint {station}（已经看过 {level}/4 级）"
    ),
    "retry_all_hints": "四级提示你都看过了。照第 4 级的答案一步一步对一遍；还是不行，把上面这段结果发给导师。",
    "already_passed": "这一站之前已经通过（{date}），进度不受这次结果影响。",
    "problem_note": "你的进度没有受影响，这次也不算一次尝试。",
    "lesson_head": "全课检查 · {lesson} {title}",
    "station_done": "{mark} {station} {title}：已通过（{date}）",
    "station_assisted": (
        "{mark} {station} {title}：带扶手完成（{date}），"
        "还要在 {after} 到 {before} 之间不看提示重做一遍"
    ),
    "lesson_passed": "全课 {lesson}：{n} 站都已通过",
    "lesson_redo": (
        "其中 {stations} 是带扶手完成的（看过完整答案）。到了上面的日期，不看提示重做一遍，"
        "再运行：python3 tools/course.py check <站点编号>"
    ),
    "lesson_not_yet": "全课 {lesson}：还有 {n} 站没通过（{stations}）",
    "lesson_problem": "全课 {lesson}：有 {n} 站的检查器出了问题（{stations}）",
    "wrapup_head": "收尾还有两件小事：",
    "wrapup_head_backup": "收尾还有三件小事：",
    # A lesson without a new rule has no notes step (COMMON.md section 3).
    "wrapup_head_one": "收尾还有一件小事：",
    "wrapup_rules": "行规笔记：运行 code notes/my-rules.md，在小标题{rules}下面用自己的话写一两句，再配一个你自己的例子",
    "wrapup_rules_two": "行规笔记：运行 code notes/my-rules.md，在小标题{rules}下面各用自己的话写一两句，再配一个你自己的例子",
    "wrapup_journal": "一句话日志：python3 tools/course.py journal",
    "wrapup_backup": "备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做",
    "next_lesson": "下一课：{lesson}「{title}」。下次可以对导师说“从 {lesson} 开始”。",
    "next_lesson_path": "课文在 {path}",
    "next_gate": (
        "下一步是{label}：{n} 道实操题，预计 {minutes} 分钟，讲解题另需约 {explain} 分钟。"
        "开始考试：python3 tools/course.py exam {gate}"
    ),
    "next_gate_resume": "下次可以对导师说“做小关卡 {gate}”。",
    "next_explain_resume": "下次可以对导师说“请问我 {gate} 的讲解题”。",
    "stage_end": "已有的课程都学完了。下次可以对导师说“准备阶段 {stage}”。",
    "unused_answers": "多给了 {n} 个 --answer，没有用上。",
    "confidence_unclear": "没看懂这个把握程度（要输入 1 到 5 的数字），这次不记。",
    "not_counted": "练习场景还没准备好，这次不算一次尝试。",
}


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "check", SUMMARY, description=DESCRIPTION)
    parser.add_argument("target", metavar="<站或课>", help=TEXT["target_help"])
    parser.add_argument("--answer", action="append", default=[], metavar="<回答>",
                        help=TEXT["answer_help"])
    parser.add_argument("--confidence", type=int, choices=[1, 2, 3, 4, 5], metavar="<1-5>",
                        help=TEXT["confidence_help"])
    parser.add_argument("--again", action="store_true", help=TEXT["again_help"])


def run(args):
    app = args.app
    lesson, station = cmdkit.find_target(app, args.target)
    state = app.store.load()
    # Find out now whether the result could be stored: an outcome followed by
    # 检查器出问题 would be two outcomes (plan I4).
    app.store.ensure_writable()
    progress.touch_session(state, app.now)
    answers = [str(answer) for answer in args.answer]
    if station is None:
        return _check_lesson(app, state, lesson, answers, again=args.again)
    confidence = _confidence(app, state, station["id"], args.confidence)
    return _check_station(app, state, lesson, station, answers, confidence).exit_code


def _confidence(app, state, station_id, given):
    """The 1-5 rating: from the flag, or asked once before the first attempt."""
    if given is not None:
        return given
    record = progress.record_of(state, station_id)
    if (not app.console.may_ask_optional or progress.is_done(record)
            or int(record.get("attempts") or 0) > 0):
        return None
    typed = app.console.read(TEXT["confidence_prompt"])
    rating = parse_int(typed)
    if rating is not None and 1 <= rating <= 5:
        return rating
    if typed.strip():
        app.console.out(TEXT["confidence_unclear"])
    return None


def _heading(station):
    return ("{} {}".format(station["id"], station.get("title", ""))).strip()


def _day(text):
    moment = parse_stamp(text) if text else None
    return moment.date().isoformat() if moment else ""


def _check_station(app, state, lesson, station, answers, confidence, in_lesson=False):
    """Run one station check, print the outcome, update and save the state."""
    out = app.console.out
    station_id = station["id"]
    before = copy.deepcopy(progress.record_of(state, station_id))
    result = runner.run_check(app, lesson.checks.get(station_id), lesson=lesson,
                              station_id=station_id, answers=answers, state=state,
                              warn_unused=not in_lesson)
    out("")
    for line in runner.render_result(app, result, _heading(station), place=station_id):
        out(line)
    event = {"type": "check", "station": station_id, "outcome": result.outcome,
             "hint_level": progress.hint_level(before), "confidence": confidence,
             "interactive": result.interactive}
    if result.outcome == runner.PROBLEM:
        out("")
        out("  " + TEXT["problem_note"])
        app.store.save(state, events=[event])
        _write_result(app, lesson, station, result, before, confidence)
        return result
    if not result.counted:
        event["counted"] = False
        out("")
        out("  " + TEXT["not_counted"])
        app.store.save(state, events=[event])
        _write_result(app, lesson, station, result, before, confidence)
        return result
    changed = progress.record_check(state, station_id, result.passed, app.now, confidence)
    record = progress.record_of(state, station_id)
    enrolled = []
    if result.passed:
        if result.decisions:
            state.setdefault("decisions", {}).update(result.decisions)
        if changed["first_pass"]:
            enrolled = schedule.enroll_station_items(state, lesson, station_id, app.today)
    event.update({"attempt": record["attempts"], "status": record["status"],
                  "first_pass": changed["first_pass"], "redo_done": changed["redo_done"]})
    app.store.save(state, events=[event])
    _write_result(app, lesson, station, result, record, confidence)
    advice = _advice(app, state, lesson, station, result, changed, enrolled, before, in_lesson)
    if advice:
        out("")
        for line in advice:
            out("  " + line)
    return result


def _advice(app, state, lesson, station, result, changed, enrolled, before, in_lesson):
    """What the learner should know or do after this outcome."""
    station_id = station["id"]
    record = progress.record_of(state, station_id)
    lines = []
    if not result.passed:
        if progress.is_done(before):
            lines.append(TEXT["already_passed"].format(date=_day(before.get("first_pass"))))
        level = progress.hint_level(record)
        if level >= progress.MAX_HINT:
            lines.append(TEXT["retry_all_hints"])
        elif level > 0:
            lines.append(TEXT["retry_hinted"].format(station=station_id, level=level))
        else:
            lines.append(TEXT["retry"].format(station=station_id))
        return lines
    redo = progress.redo_of(record)
    if changed["redo_done"]:
        lines.append(TEXT["redo_done"])
    elif changed["assisted"] and redo:
        lines.append(TEXT["assisted"].format(after=redo.get("after"), before=redo.get("before")))
    if enrolled:
        due = schedule.due_date(state["review"][enrolled[0]])
        lines.append(TEXT["enrolled"].format(n=len(enrolled), date=due.isoformat() if due else ""))
    if in_lesson:
        return lines
    lines.append(TEXT["save_point"].format(station=station_id))
    open_ids = [sid for sid in lesson.station_ids
                if not progress.is_done(progress.record_of(state, sid))]
    ids = lesson.station_ids
    position = ids.index(station_id)
    if position + 1 < len(ids) and ids[position + 1] in open_ids:
        following = lesson.station(ids[position + 1])
        lines.append(TEXT["next_station"].format(next=following["id"],
                                                 title=following.get("title", "")))
    elif open_ids:
        lines.append(TEXT["lesson_remaining"].format(lesson=lesson.id,
                                                     stations=" ".join(open_ids)))
        lines.append(TEXT["resume_station"].format(station=open_ids[0]))
    else:
        # Every station of this lesson has passed: the one answer of
        # status.next_step says what comes next (normally this lesson's
        # closing steps; for a lesson finished long ago, wherever the
        # learner really is).
        step = next_steps.next_step(app, state, reviews=False, after=lesson)
        lines += step_lines(step)
    return lines


def step_lines(step):
    """The lines check prints for a ``status.NextStep`` (each one paragraph line)."""
    kind = step.kind
    if kind == next_steps.WRAPUP:
        lines = [TEXT["lesson_wrapup"].format(lesson=step.lesson, n=step.count),
                 TEXT["lesson_wrapup_resume"].format(lesson=step.lesson)]
    elif kind == next_steps.STATION:
        lines = [TEXT["next_station"].format(next=step.station, title=step.title)]
    elif kind == next_steps.LESSON:
        lines = [TEXT["next_lesson"].format(lesson=step.lesson, title=step.title),
                 TEXT["next_lesson_path"].format(path=step.path)]
    elif kind == next_steps.GATE and step.get("sitting"):
        # A sitting of this gate is open: grade it (status says the same).
        lines = [step.text + "。", TEXT["next_gate_resume"].format(gate=step.gate)]
    elif kind == next_steps.GATE:
        label = step.get("label") or step.gate
        lines = [TEXT["next_gate"].format(gate=step.gate, n=step.count, minutes=step.minutes,
                                          label=(" " if label[:1].isascii() else "") + label,
                                          explain=next_steps.EXPLAIN_MINUTES),
                 TEXT["next_gate_resume"].format(gate=step.gate)]
    elif kind == next_steps.EXPLAIN:
        lines = [step.text + "。", TEXT["next_explain_resume"].format(gate=step.gate)]
    elif kind == next_steps.STAGE_END:
        lines = [TEXT["stage_end"].format(stage=step.stage)]
    else:
        lines = []
    return lines + [gate.note for gate in step.gates]


def _write_result(app, lesson, station, result, record, confidence):
    data = {"target": station["id"], "kind": "station", "lesson": lesson.id,
            "title": station.get("title", "")}
    data.update(result.to_dict())
    data.update({"attempts": int(record.get("attempts") or 0),
                 "status": record.get("status"),
                 "highest_hint": progress.hint_level(record),
                 "confidence": confidence})
    app.store.write_result(data)


def _check_lesson(app, state, lesson, answers, again=False):
    """Check every open station of a lesson and print a summary."""
    out = app.console.out
    out(TEXT["lesson_head"].format(lesson=lesson.id, title=lesson.title))
    summary = []
    details = {}
    listing = False
    for station in lesson.stations:
        station_id = station["id"]
        record = progress.record_of(state, station_id)
        if progress.is_done(record) and not again:
            if not listing:
                out("")
            listing = True
            redo = progress.redo_of(record)
            if record.get("status") == progress.ASSISTED and redo and not redo.get("done"):
                out("  " + TEXT["station_assisted"].format(
                    mark=OK_MARK, station=station_id, title=station.get("title", ""),
                    date=_day(record.get("first_pass")),
                    after=redo.get("after"), before=redo.get("before")))
            else:
                out("  " + TEXT["station_done"].format(
                    mark=OK_MARK, station=station_id, title=station.get("title", ""),
                    date=_day(record.get("first_pass"))))
            summary.append({"station": station_id, "outcome": "passed_earlier"})
            continue
        listing = False
        result = _check_station(app, state, lesson, station, answers, None, in_lesson=True)
        del answers[:result.answers_used]
        summary.append({"station": station_id, "outcome": result.outcome})
        details[station_id] = result.to_dict()
    problems = [item["station"] for item in summary if item["outcome"] == runner.PROBLEM]
    not_yet = [item["station"] for item in summary if item["outcome"] == runner.NOT_YET]
    out("")
    if problems:
        outcome, code = runner.PROBLEM, EXIT_PROBLEM
        out(runner.headline(app.console, outcome, TEXT["lesson_problem"].format(
            lesson=lesson.id, n=len(problems), stations=" ".join(problems))))
    elif not_yet:
        outcome, code = runner.NOT_YET, EXIT_NOT_YET
        out(runner.headline(app.console, outcome, TEXT["lesson_not_yet"].format(
            lesson=lesson.id, n=len(not_yet), stations=" ".join(not_yet))))
    else:
        outcome, code = runner.PASSED, EXIT_OK
        out(runner.headline(app.console, outcome, TEXT["lesson_passed"].format(
            lesson=lesson.id, n=len(lesson.stations))))
        assisted = [sid for sid in lesson.station_ids if _redo_pending(state, sid)]
        if assisted:
            out("  " + TEXT["lesson_redo"].format(stations="、".join(assisted)))
        out("")
        for line in wrapup_lines(lesson):
            out("  " + line)
        if not next_steps.lesson_checked(state, lesson.id):
            next_steps.record_lesson_check(state, lesson.id, app.stamp())
            app.store.save(state)
        for line in what_comes_next(app, state, lesson):
            out("")
            out("  " + line)
    if answers:
        out("")
        out("  " + TEXT["unused_answers"].format(n=len(answers)))
    app.store.log("lesson-check", lesson=lesson.id, outcome=outcome, stations=summary)
    app.store.write_result({"target": lesson.id, "kind": "lesson", "title": lesson.title,
                            "outcome": outcome, "outcome_text": runner.TEXT[outcome],
                            "exit_code": code, "stations": summary, "details": details})
    return code


def wrapup_lines(lesson):
    """The closing steps left after a passed whole-lesson check (COMMON.md section 3).

    The notes on the lesson's rules (each rule id with its title from
    rules.md when the card is there; a lesson without a new rule has no
    notes step), the journal, and from lesson 1.12 on the backup of lesson
    1.12.
    """
    rules = lesson.rules
    steps = []
    if rules:
        titles = _rule_titles(lesson)
        named = "".join("「{}」".format(" ".join(filter(None, (rule, titles.get(rule, "")))))
                        for rule in rules)
        steps.append(TEXT["wrapup_rules_two" if len(rules) > 1 else "wrapup_rules"].format(rules=named))
    steps.append(TEXT["wrapup_journal"])
    if lesson_key(lesson.id) >= lesson_key(BACKUP_FROM) and lesson_key(lesson.id)[0] < 10 ** 6:
        steps.append(TEXT["wrapup_backup"])
    head = {1: TEXT["wrapup_head_one"], 2: TEXT["wrapup_head"]}.get(len(steps), TEXT["wrapup_head_backup"])
    return [head] + [f"  {number}. {text}" for number, text in enumerate(steps, 1)]


def _rule_titles(lesson):
    """``{rule id: title}`` from the headings 「### GIT-01 …」 of the lesson's rules.md."""
    try:
        text = lesson.rules_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, AttributeError):
        return {}
    titles = {}
    for line in text.splitlines():
        match = _RULE_HEADING.match(line)
        if match:
            titles.setdefault(match.group(1), match.group(2).strip())
    return titles


def _redo_pending(state, station_id):
    """Is this station 带扶手完成 with its cold redo still to do?"""
    record = progress.record_of(state, station_id)
    redo = progress.redo_of(record)
    return bool(record.get("status") == progress.ASSISTED and redo and not redo.get("done"))


def what_comes_next(app, state, lesson):
    """The paragraphs after a passed whole-lesson check of ``lesson``.

    The answer is ``status.next_step`` (reviews left out): a due gate
    (「…“做小关卡 gate-b”。」), the explain-back of a gate whose practical part
    is passed (「…“请问我 gate-b 的讲解题”。」), the next lesson (「…“从 1.7
    开始”。」), wherever the learner really is, or the end of the stage
    (「…“准备阶段 2”。」).  A gate that is still open after its lessons adds
    one line; it never blocks the next lesson.  Each returned string is
    printed as its own paragraph (lines inside it joined with a two-space
    indent).
    """
    step = next_steps.next_step(app, state, reviews=False, after=lesson)
    lines = step_lines(step)
    if not lines:
        return []
    main = [line for line in lines if line not in [gate.note for gate in step.gates]]
    notes = [gate.note for gate in step.gates]
    paragraphs = ["\n  ".join(main)] if main else []
    return paragraphs + notes
