"""Station records and sessions: the rules that change learner/state.json.

All functions here work on the plain state dict (see ``store``) and on a
``now`` passed in by the caller; none of them touches the disk.

Station status (plan I5):

- ``open``      not passed yet
- ``passed``    the check passed without the learner having seen hint level 4,
                or a cold redo passed later
- ``assisted``  带扶手完成: hint level 4 (the full answer) was shown.  A cold redo
                is due 3 to 7 days later; passing the check again in or after
                that window, on a day without hints, turns it into ``passed``.

A station counts as done for progress once its check has passed at least once
(``first_pass`` is set), whatever the status.
"""

import datetime
import math
import re
from fractions import Fraction

from .app import parse_stamp, stamp

OPEN = "open"
PASSED = "passed"
ASSISTED = "assisted"

REDO_EARLIEST_DAYS = 3
REDO_LATEST_DAYS = 7
SESSION_GAP_MINUTES = 45
MAX_HINT = 4


def new_record():
    return {"status": OPEN, "attempts": 0, "first_pass": None, "last_pass": None,
            "last_attempt": None, "highest_hint": 0, "last_hint": None,
            "confidence": None}


def record_of(state, station_id, create=False):
    """The record of ``station_id``; a fresh one when there is none yet."""
    stations = state.setdefault("stations", {})
    record = stations.get(station_id)
    if not isinstance(record, dict):
        record = new_record()
        if create:
            stations[station_id] = record
    else:
        for key, value in new_record().items():
            record.setdefault(key, value)
    return record


def is_done(record):
    """Has the check of this station passed at least once?"""
    return bool(record and record.get("first_pass"))


def hint_level(record):
    return int((record or {}).get("highest_hint") or 0)


def redo_of(record):
    redo = (record or {}).get("redo")
    return redo if isinstance(redo, dict) else None


def redo_is_due(record, today):
    """Is a cold redo of this station due on ``today`` (a date)?"""
    redo = redo_of(record)
    if not redo or redo.get("done"):
        return False
    after = parse_stamp(redo.get("after"))
    return bool(after and today >= after.date())


def record_check(state, station_id, passed, now, confidence=None):
    """Count one check attempt.  Returns a dict of what changed.

    Keys of the returned dict (all bool): ``first_pass``, ``assisted`` (the
    station is 带扶手完成 after this attempt), ``redo_done`` (this pass was
    the cold redo), ``redo_pending`` (a redo is scheduled and not done).
    """
    record = record_of(state, station_id, create=True)
    record["attempts"] = int(record.get("attempts") or 0) + 1
    record["last_attempt"] = stamp(now)
    if confidence is not None:
        record["confidence"] = confidence
    changed = {"first_pass": False, "assisted": False, "redo_done": False,
               "redo_pending": False}
    if not passed:
        changed["assisted"] = record.get("status") == ASSISTED
        return changed
    if not record.get("first_pass"):
        record["first_pass"] = stamp(now)
        changed["first_pass"] = True
    record["last_pass"] = stamp(now)
    redo = redo_of(record)
    if redo and not redo.get("done"):
        last_hint = parse_stamp(record.get("last_hint"))
        cold = last_hint is None or last_hint.date() < now.date()
        if redo_is_due(record, now.date()) and cold:
            redo["done"] = now.date().isoformat()
            record["status"] = PASSED
            changed["redo_done"] = True
        else:
            record["status"] = ASSISTED
            changed["assisted"] = True
            changed["redo_pending"] = True
    elif record.get("status") != ASSISTED or (redo and redo.get("done")):
        record["status"] = PASSED
    else:
        changed["assisted"] = True
    return changed


def record_hint(state, station_id, now):
    """Reveal the next hint level.  Returns ``(level, scheduled_redo)``.

    ``level`` is 1 to 4 (4 again when every level was already shown).
    ``scheduled_redo`` is True when this call marked the station 带扶手完成
    and scheduled the cold redo.
    """
    record = record_of(state, station_id, create=True)
    level = min(hint_level(record) + 1, MAX_HINT)
    record["highest_hint"] = max(hint_level(record), level)
    record["last_hint"] = stamp(now)
    scheduled = False
    if level == MAX_HINT and record.get("status") != PASSED and not redo_of(record):
        record["status"] = ASSISTED
        record["redo"] = {
            "after": (now.date() + datetime.timedelta(days=REDO_EARLIEST_DAYS)).isoformat(),
            "before": (now.date() + datetime.timedelta(days=REDO_LATEST_DAYS)).isoformat(),
            "done": None,
        }
        scheduled = True
    return level, scheduled


def reread_hint(state, station_id, now):
    """Note that already revealed hints were shown again (keeps a redo honest)."""
    record = record_of(state, station_id, create=True)
    record["last_hint"] = stamp(now)


# ---------------------------------------------------------------------------
# Gates (plan I7, COMMON.md section 1)
# ---------------------------------------------------------------------------
# The rule:
#
# - A gate covers the lessons whose exam tasks name it (``"gate": "gate-b"``)
#   and that have at least one usable task.  gate-1 covers 1.11 to 1.16 and
#   borrows nothing from gate-a or gate-b.
# - One sitting holds one task for each of those lessons, in lesson order, at
#   most ``GATE_MAX_TASKS``.
# - A lesson is passed ("covered") once one of its tasks has been passed.  The
#   practical part is passed when every lesson of the gate is.
# - A sitting after an unsuccessful one holds only the lessons not passed yet;
#   a task that was not passed comes back in its other form.
# - The gate is passed (``done``) when the practical part is passed and the
#   explain-back questions are recorded as passed:
#   ``state["explain"][gate] == {"result": "pass", "date": "YYYY-MM-DD"}``.
#
# Tasks of a gate are given to these functions as a *pool*: a list, in
# learning order, of ``(lesson_id, task_id)`` pairs, or of plain task ids
# (the lesson is then read from the id: ``"1.6-x1"`` belongs to 1.6).

GATE_PASS = "pass"
GATE_FAIL = "fail"
#: A sitting has at most this many tasks (one per lesson of the gate).
GATE_MAX_TASKS = 6
#: The two verdicts of the explain-back questions (``exam <gate> --explain``).
EXPLAIN_PASS = "pass"
EXPLAIN_AGAIN = "again"
EXPLAIN_RESULTS = (EXPLAIN_PASS, EXPLAIN_AGAIN)
#: Minutes counted for a task whose ``minutes`` is missing or not usable.
DEFAULT_TASK_MINUTES = 5

_TASK_LESSON = re.compile(r"^(\d{1,2}\.\d{1,2})-")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def task_minutes(task):
    """The ``minutes`` of an exam task (a dict), or ``DEFAULT_TASK_MINUTES``."""
    minutes = task.get("minutes") if isinstance(task, dict) else None
    if isinstance(minutes, int) and not isinstance(minutes, bool) and minutes > 0:
        return minutes
    return DEFAULT_TASK_MINUTES


def _pairs(pool):
    """``[(lesson_id, task_id)]`` of a pool, without repeated task ids."""
    pairs, seen = [], set()
    for item in pool or ():
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            lesson_id, task_id = str(item[0]), str(item[1])
        else:
            task_id = str(item)
            match = _TASK_LESSON.match(task_id)
            lesson_id = match.group(1) if match else task_id
        if task_id not in seen:
            seen.add(task_id)
            pairs.append((lesson_id, task_id))
    return pairs


def _results(results):
    return results if isinstance(results, dict) else {}


def task_passed(record):
    """Has this task (its record in ``state["exams"][gate]``) ever been passed?"""
    if not isinstance(record, dict):
        return False
    if record.get("result") == GATE_PASS:
        return True
    history = record.get("history")
    return isinstance(history, list) and any(
        isinstance(entry, dict) and entry.get("result") == GATE_PASS for entry in history)


def gate_lessons(pool):
    """The lesson ids of a pool, in learning order."""
    lessons = []
    for lesson_id, _task_id in _pairs(pool):
        if lesson_id not in lessons:
            lessons.append(lesson_id)
    return lessons


def gate_open_lessons(pool, results):
    """Lesson ids of the pool none of whose tasks has been passed yet."""
    results = _results(results)
    passed = {lesson_id for lesson_id, task_id in _pairs(pool)
              if task_passed(results.get(task_id))}
    return [lesson_id for lesson_id in gate_lessons(pool) if lesson_id not in passed]


def gate_practical_done(pool, results):
    """True when every lesson of the pool has a passed task (never for an empty pool)."""
    return bool(_pairs(pool)) and not gate_open_lessons(pool, results)


def gate_open_ids(primary_ids, secondary_ids=(), results=None):
    """Task ids tried without a pass, in the lessons not passed yet.

    These are the tasks to practise; each comes back in its other form in the
    next sitting.  A lesson none of whose tasks was tried yet has no entry
    here (see ``gate_open_lessons``).  ``secondary_ids`` is accepted for
    compatibility and ignored: a gate no longer borrows tasks of other gates.
    """
    results = _results(results)
    still_open = set(gate_open_lessons(primary_ids, results))
    return [task_id for lesson_id, task_id in _pairs(primary_ids)
            if lesson_id in still_open and isinstance(results.get(task_id), dict)]


def explain_record(explain):
    """``(result, date)`` of a stored explain-back verdict; ``(None, None)`` when none.

    ``explain`` is ``state["explain"][gate]``; anything malformed counts as none.
    """
    if not isinstance(explain, dict) or explain.get("result") not in EXPLAIN_RESULTS:
        return None, None
    date = explain.get("date")
    return explain["result"], (date if isinstance(date, str) and _ISO_DATE.match(date) else None)


def explain_of(state, gate):
    """``state["explain"][gate]`` (or None), read without changing ``state``."""
    explain = state.get("explain") if isinstance(state, dict) else None
    return explain.get(gate) if isinstance(explain, dict) else None


def record_explain(state, gate, result, today):
    """Store the explain-back verdict of ``gate`` (``"pass"`` or ``"again"``) for ``today``."""
    if result not in EXPLAIN_RESULTS:
        raise ValueError("explain result must be 'pass' or 'again'")
    explain = state.get("explain")
    if not isinstance(explain, dict):
        explain = {}
        state["explain"] = explain
    explain[str(gate)] = {"result": result, "date": today.isoformat()}
    return explain[str(gate)]


def gate_done(primary_ids, secondary_ids=(), results=None, explain=None):
    """True when the gate is passed: practical part passed and explain-back ``pass``.

    ``explain`` is ``state["explain"][gate]``; without it a gate is never done.
    ``secondary_ids`` is accepted for compatibility and ignored.
    """
    return (gate_practical_done(primary_ids, results)
            and explain_record(explain)[0] == EXPLAIN_PASS)


def _last_tried(pairs, results):
    """The task of ``pairs`` tried last (by date, then attempt), or None."""
    tried = []
    for position, (_lesson_id, task_id) in enumerate(pairs):
        record = results.get(task_id)
        if isinstance(record, dict):
            try:
                attempt = int(record.get("attempt") or 0)
            except (TypeError, ValueError):
                attempt = 0
            tried.append((str(record.get("date") or ""), attempt, position, task_id))
    return max(tried)[3] if tried else None


def gate_sitting_plan(pool, results):
    """What the next sitting holds, lesson by lesson: ``[(lesson_id, [task ids])]``.

    For every lesson not passed yet (all of them before the first sitting), in
    learning order and at most ``GATE_MAX_TASKS`` lessons: the task tried last
    there when there is one (it comes back in its other form), else every task
    of that lesson (one of them is drawn at random).  Empty when the practical
    part is passed.
    """
    results = _results(results)
    pairs = _pairs(pool)
    plan = []
    for lesson_id in gate_open_lessons(pairs, results)[:GATE_MAX_TASKS]:
        mine = [pair for pair in pairs if pair[0] == lesson_id]
        again = _last_tried(mine, results)
        plan.append((lesson_id, [again] if again else [task_id for _l, task_id in mine]))
    return plan


def gate_full_plan(pool, results=None, drawn=()):
    """A full sitting (``exam <gate> --all``): ``[(lesson_id, [task ids])]``.

    Every lesson of the pool, passed or not, in learning order and at most
    ``GATE_MAX_TASKS`` lessons; for each lesson the tasks never drawn yet
    (neither in ``drawn``, the task ids drawn in earlier sittings, nor in
    ``results``), else all its tasks.  One task per lesson is drawn from them.
    When a gate has more lessons than ``GATE_MAX_TASKS``, the lessons not
    passed yet are taken first, so no lesson is left out of every sitting.

    Limit: once every lesson of such a gate is passed, the first
    ``GATE_MAX_TASKS`` lessons are taken every time, so the later ones never
    come up in extra practice (``--all``).  No gate has more than six lessons
    (gate-0 4, gate-a 5, gate-b 5, gate-1 6); a gate with more needs a
    rotation here first.
    """
    results = _results(results)
    seen = {str(task_id) for task_id in drawn or ()} | set(results)
    pairs = _pairs(pool)
    lessons = gate_lessons(pairs)
    if len(lessons) > GATE_MAX_TASKS:
        still_open = gate_open_lessons(pairs, results)
        chosen = (still_open + [lesson for lesson in lessons if lesson not in still_open])
        chosen = set(chosen[:GATE_MAX_TASKS])
        lessons = [lesson for lesson in lessons if lesson in chosen]
    plan = []
    for lesson_id in lessons:
        mine = [task_id for lesson, task_id in pairs if lesson == lesson_id]
        fresh = [task_id for task_id in mine if task_id not in seen]
        plan.append((lesson_id, fresh or mine))
    return plan


def gate_minutes(minutes, cap=GATE_MAX_TASKS):
    """Expected minutes of a sitting.

    ``minutes`` is a list with one entry per lesson of the sitting: the
    minutes of the task that will be set (an int), or the minutes of the
    tasks one of which is drawn (a list of ints: their mean counts).  The
    first ``cap`` entries count; the sum is rounded up.  (A flat list longer
    than ``cap`` is read the old way: ``cap`` times the mean, rounded up.)
    """
    entries = list(minutes)
    if all(not isinstance(entry, (list, tuple)) for entry in entries):
        values = [int(entry) for entry in entries]
        if len(values) <= cap:
            return sum(values)
        return -(-sum(values) * cap // len(values))
    total = Fraction(0)
    for entry in entries[:cap]:
        values = [int(m) for m in entry] if isinstance(entry, (list, tuple)) else [int(entry)]
        if values:
            total += Fraction(sum(values), len(values))
    return math.ceil(total)


class GateSummary(dict):
    """A summary of one gate: a dict whose keys can also be read as attributes."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


def gate_summary(primary_ids, secondary_ids=(), results=None, attempt=None, explain=None,
                 minutes=None):
    """A plain summary of one gate for checks, ``check`` and ``status``.

    ``primary_ids`` is the pool (see above), ``results`` ``state["exams"][gate]``,
    ``attempt`` ``state["exam_attempts"][gate]``, ``explain``
    ``state["explain"][gate]``, ``minutes`` ``{task id: minutes}`` (missing
    ones count ``DEFAULT_TASK_MINUTES``).  ``secondary_ids`` is ignored.

    Keys (also attributes): ``attempts`` (sittings started), ``passed`` (task
    ids passed), ``open`` (``gate_open_ids``), ``lessons`` (lesson ids of the
    gate), ``open_lessons`` (not passed yet), ``practical_done``, ``explain``
    (``"pass"``, ``"again"`` or None), ``explain_date``, ``done``
    (``practical_done`` and ``explain == "pass"``), ``in_progress`` (a sitting
    has tasks not graded yet), ``next_count`` and ``next_minutes`` (the next
    sitting: the ungraded tasks of the open one, else the plan of
    ``gate_sitting_plan``; 0 and 0 when the practical part is passed and no
    sitting is open: an open extra practice sitting keeps its own numbers),
    ``sitting_kind`` (the ``kind`` of the open sitting: ``"full"``,
    ``"retest"``, ``"again"`` or ``"practice"``; None when none is open).
    """
    results = _results(results)
    attempt = attempt if isinstance(attempt, dict) else {}
    minutes = minutes if isinstance(minutes, dict) else {}
    pairs = _pairs(primary_ids)
    passed = [task_id for _lesson_id, task_id in pairs if task_passed(results.get(task_id))]
    tasks = [t for t in (attempt.get("tasks") if isinstance(attempt.get("tasks"), list) else [])
             if isinstance(t, dict)]
    pending = [t for t in tasks if t.get("result") not in (GATE_PASS, GATE_FAIL)]
    try:
        attempts = max(0, int(attempt.get("attempt") or 0))
    except (TypeError, ValueError):
        attempts = 0
    practical = gate_practical_done(pairs, results)
    verdict, date = explain_record(explain)

    def minutes_of(task_id):
        value = minutes.get(task_id)
        return task_minutes({"minutes": value})

    if pending:
        next_count = len(pending)
        next_minutes = sum(task_minutes(t) for t in pending)
    else:
        plan = gate_sitting_plan(pairs, results)
        next_count = len(plan)
        next_minutes = gate_minutes([[minutes_of(t) for t in ids] for _l, ids in plan])
    return GateSummary(
        attempts=attempts, passed=passed, open=gate_open_ids(pairs, (), results),
        lessons=gate_lessons(pairs), open_lessons=gate_open_lessons(pairs, results),
        practical_done=practical, explain=verdict, explain_date=date,
        done=practical and verdict == EXPLAIN_PASS, in_progress=bool(pending),
        next_count=next_count, next_minutes=next_minutes,
        sitting_kind=(str(attempt.get("kind") or "full") if pending else None))


def gate_status(catalog, state, gate):
    """``gate_summary`` of ``gate`` read from a catalogue and a state dict.

    The one call for commands (``check``, ``status``, ``journal``): the pool
    comes from ``catalog.gate_pool(gate)``, the records from ``state``.  The
    summary also has ``gate`` and ``tasks`` (how many usable tasks the gate has).
    """
    state = state if isinstance(state, dict) else {}
    primary, _secondary, _unusable = catalog.gate_pool(gate)
    pool = [(lesson.id, task["id"]) for lesson, task in primary]
    minutes = {task["id"]: task_minutes(task) for _lesson, task in primary}

    def section(name):
        value = state.get(name)
        value = value.get(gate) if isinstance(value, dict) else None
        return value if isinstance(value, dict) else None

    summary = gate_summary(pool, (), section("exams"), section("exam_attempts"),
                           section("explain"), minutes)
    summary["gate"] = gate
    summary["tasks"] = len(pool)
    return summary


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------
def touch_session(state, now):
    """Count this moment as study activity.  Returns the current session.

    Commands that are part of studying call this.  Activity less than 45
    minutes after the previous one extends the current session; anything later
    starts a new one.  ``minutes`` is the time between the first and the last
    command of a sitting, so it is a lower bound of the time really spent.
    """
    sessions = state.setdefault("sessions", [])
    current = sessions[-1] if sessions and isinstance(sessions[-1], dict) else None
    if current is not None:
        last = parse_stamp(current.get("last"))
        start = parse_stamp(current.get("start"))
        gap = datetime.timedelta(minutes=SESSION_GAP_MINUTES)
        if last is not None and start is not None and last <= now <= last + gap:
            current["last"] = stamp(now)
            current["minutes"] = int((now - start).total_seconds() // 60)
            return current
    current = {"date": now.date().isoformat(), "start": stamp(now), "last": stamp(now),
               "minutes": 0}
    sessions.append(current)
    return current


def total_minutes(state):
    total = 0
    for session in state.get("sessions", []):
        if isinstance(session, dict) and isinstance(session.get("minutes"), int):
            total += max(0, session["minutes"])
    return total


def session_dates(state):
    """The distinct dates with a session, ascending."""
    dates = set()
    for session in state.get("sessions", []):
        moment = parse_stamp(session.get("date")) if isinstance(session, dict) else None
        if moment is not None:
            dates.add(moment.date())
    return sorted(dates)


def days_away(state, today):
    """Days between the study day before ``today`` and ``today``; None if none."""
    earlier = [day for day in session_dates(state) if day < today]
    if not earlier:
        return None
    return (today - earlier[-1]).days
