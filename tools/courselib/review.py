"""What a review session serves, and in which order (plan I4 ``review``).

Pure functions on the state dict and the lesson catalog; nothing here reads
or writes files.  The command ``courselib/commands/review.py`` asks and
records; ``status`` uses ``due_count`` and ``next_due``.

Rules (they are explained to lesson authors in
docs/authoring/tool-api.md, section 16):

- Only items with tier ``fluent`` are scheduled.  An item enters box 1 when
  the station it belongs to first passes (``schedule.enroll_station_items``,
  called by ``check``); ``sync_enrolment`` catches up items that were added
  to a lesson after its station had already passed.
- The Leitner moves are in ``courselib.schedule``.
- A normal session first serves due **cold redos** (stations that hint level
  4 marked 带扶手完成, 3 to 7 days later; at most ``MAX_REDO``), then due items:
  *which* items is decided oldest due first (at most ``MAX_ITEMS`` things in
  all, about ``SESSION_MINUTES`` minutes by estimate); *in which order* mixes
  the item types (two items of one type follow each other only when nothing
  else is left).  A ``do`` item is served
  last and only one at a time (``MAX_DO``); while one is out (``pending``) no
  other is started.
- The **return routine**: when the study day before today lies more than
  ``LONG_BREAK_DAYS`` days back, a session serves at most ``RETURN_ITEMS``
  easy items, easiest first (lowest boxes among the items last answered
  right, then items never answered, then fuzzy, then missed) and no redo or
  ``do`` task; the rest is only counted.
- Records whose lesson module or item has disappeared, whose lesson is broken,
  or whose item is no longer ``fluent`` are kept in the state but never served
  and never counted as due.  A record with an unreadable due date counts as
  due today (answering it writes a clean record).
"""

import re
import time

from . import progress, schedule

#: Seconds since some fixed point; the session uses it for its 10-minute cap.
#: Tests replace it to simulate a slow learner (COURSE_NOW stands still).
clock = time.monotonic

MAX_ITEMS = 8
MAX_REDO = 2
MAX_DO = 1
RETURN_ITEMS = 4
SESSION_MINUTES = 10
LONG_BREAK_DAYS = 10
#: Rough minutes per item type, for planning a session of about 10 minutes.
ESTIMATE = {"recall": 1.0, "predict": 1.0, "which": 1.0, "fault": 1.0, "do": 3.0}
CHOICE_TYPES = ("predict", "which", "fault")
TYPES = ("recall",) + CHOICE_TYPES + ("do",)

_LESSON_PREFIX = re.compile(r"^(\d+\.\d+)-")


def lesson_id_of(item_id):
    """``"1.6-r3"`` -> ``"1.6"``; "" when the id has no lesson prefix."""
    match = _LESSON_PREFIX.match(str(item_id))
    return match.group(1) if match else ""


class Entry:
    """One scheduled item as a session sees it."""

    def __init__(self, item_id, record, lesson, item, today):
        self.id = item_id
        self.record = record
        self.lesson = lesson
        self.item = item
        self.type = item.get("type")
        due = schedule.due_date(record)
        #: an unreadable due date counts as due today
        self.due = due if due is not None else today
        self.box = schedule.box_of(record)
        self.last = schedule.last_result(record)

    @property
    def pending(self):
        return isinstance(self.record.get("pending"), dict)

    @property
    def station(self):
        return schedule.item_station(self.lesson, self.item)

    def __repr__(self):
        return f"<Entry {self.id} {self.type} box={self.box} due={self.due}>"


class Orphans:
    """Records that cannot be served: their lesson or item is gone or unusable."""

    def __init__(self):
        self.missing = []        # no lesson module or no such item any more
        self.broken = []         # the lesson module failed to load
        self.unscheduled = []    # the item exists but is no longer fluent

    def __bool__(self):
        return bool(self.missing or self.broken or self.unscheduled)

    def all(self):
        return self.missing + self.broken + self.unscheduled


def classify(state, catalog, today):
    """``(entries, orphans)`` for every record that is not retired."""
    entries = []
    orphans = Orphans()
    for item_id in sorted(state.get("review", {})):
        record = state["review"][item_id]
        if not isinstance(record, dict) or schedule.is_retired(record):
            continue
        lesson, item = catalog.review_item(item_id)
        if lesson is None or not isinstance(item, dict):
            lesson_id = lesson_id_of(item_id)
            if lesson_id and catalog.broken_for(lesson_id) is not None:
                orphans.broken.append(item_id)
            else:
                orphans.missing.append(item_id)
            continue
        if item.get("tier") != schedule.SCHEDULED_TIER or item.get("type") not in TYPES:
            orphans.unscheduled.append(item_id)
            continue
        entries.append(Entry(item_id, record, lesson, item, today))
    return entries, orphans


def _due_order(entry):
    return (entry.due, entry.id)


def due_entries(state, catalog, today):
    """Servable items due on or before ``today`` (not out as a pending ``do``)."""
    entries, _orphans = classify(state, catalog, today)
    due = [entry for entry in entries if entry.due <= today and not entry.pending]
    return sorted(due, key=_due_order)


def pending_entries(state, catalog, today):
    """``do`` items that were handed out and wait for ``review --grade``."""
    entries, _orphans = classify(state, catalog, today)
    return [entry for entry in entries if entry.pending]


def due_count(state, catalog, today):
    """How many review items are due today: the number ``status`` shows."""
    return len(due_entries(state, catalog, today))


def next_due(state, catalog, today):
    """The earliest due date after ``today`` of a servable item, or None."""
    entries, _orphans = classify(state, catalog, today)
    later = [entry.due for entry in entries if entry.due > today and not entry.pending]
    return min(later) if later else None


def sync_enrolment(state, catalog, today):
    """Enrol fluent items of stations that already passed but were never enrolled.

    This happens when an author adds review items to a lesson after the
    learner passed its station.  Returns the ids enrolled now.
    """
    added = []
    for lesson in catalog.lessons:
        for station_id in lesson.station_ids:
            if progress.is_done(progress.record_of(state, station_id)):
                added += schedule.enroll_station_items(state, lesson, station_id, today)
    return added


def redo_tasks(state, catalog, today):
    """Cold redos due today, earliest first: dicts with lesson, station, after, before."""
    tasks = []
    for station_id, record in sorted(state.get("stations", {}).items()):
        if not isinstance(record, dict) or not progress.redo_is_due(record, today):
            continue
        lesson, station = catalog.station(station_id)
        if lesson is None:
            continue
        redo = progress.redo_of(record) or {}
        tasks.append({"lesson": lesson, "station": station, "id": station_id,
                      "after": str(redo.get("after") or ""),
                      "before": str(redo.get("before") or "")})
    tasks.sort(key=lambda task: (task["after"], task["id"]))
    return tasks


def mix_types(entries, key=None):
    """Keep the given priority order but avoid two items of one type in a row.

    ``key`` is the priority (default: oldest due first).  Greedy: take the
    first remaining item whose type differs from the one just placed; when
    only that type is left, take the first of it.
    """
    left = sorted(entries, key=key or _due_order)
    ordered = []
    while left:
        previous = ordered[-1].type if ordered else None
        pick = next((entry for entry in left if entry.type != previous), left[0])
        left.remove(pick)
        ordered.append(pick)
    return ordered


def _easy_order(entry):
    """Easiest first: last answered right (lowest box first), then never answered."""
    rank = {schedule.RIGHT: 0, None: 1, schedule.FUZZY: 2, schedule.WRONG: 3}[entry.last]
    return (rank, entry.box, entry.due, entry.id)


def pick_easy(entries, count=RETURN_ITEMS):
    """The ``count`` easiest items for the return routine (never a ``do`` item)."""
    candidates = [entry for entry in entries if entry.type != "do"]
    return mix_types(sorted(candidates, key=_easy_order)[:count], key=_easy_order)


class Plan:
    """What one session serves."""

    def __init__(self):
        self.return_routine = False
        self.days_away = None
        self.redo = []           # redo task dicts, served first
        self.items = []          # Entry objects, in serving order
        self.due_total = 0       # items due today
        self.redo_total = 0      # redos due today
        self.backlog = 0         # due things not served this time
        self.pending = []        # do items still out
        self.orphans = Orphans()
        self.minutes = 0.0       # estimate

    @property
    def size(self):
        return len(self.redo) + len(self.items)


def make_plan(state, catalog, today, days_away=None):
    """Choose what to serve.  ``days_away``: see ``progress.days_away``."""
    plan = Plan()
    plan.days_away = days_away
    entries, plan.orphans = classify(state, catalog, today)
    plan.pending = [entry for entry in entries if entry.pending]
    due = sorted((entry for entry in entries if entry.due <= today and not entry.pending),
                 key=_due_order)
    redo = redo_tasks(state, catalog, today)
    plan.due_total = len(due)
    plan.redo_total = len(redo)
    if days_away is not None and days_away > LONG_BREAK_DAYS:
        plan.return_routine = True
        plan.items = pick_easy(due, RETURN_ITEMS)
    else:
        plan.redo = redo[:MAX_REDO]
        room = MAX_ITEMS - len(plan.redo)
        do_allowed = MAX_DO if not plan.pending else 0
        quick = []
        hands_on = []
        minutes = 0.0
        # which items: oldest due first; in which order: mixed, do last
        for entry in due:
            if len(quick) + len(hands_on) >= room:
                break
            cost = ESTIMATE.get(entry.type, 1.0)
            if minutes + cost > SESSION_MINUTES:
                continue
            if entry.type == "do":
                if len(hands_on) >= do_allowed:
                    continue
                hands_on.append(entry)
            else:
                quick.append(entry)
            minutes += cost
        plan.items = mix_types(quick) + hands_on
        plan.minutes = minutes
    if plan.return_routine:
        plan.minutes = sum(ESTIMATE.get(entry.type, 1.0) for entry in plan.items)
    plan.backlog = (plan.due_total - len(plan.items)) + (plan.redo_total - len(plan.redo))
    return plan


def type_counts(entries):
    """``{type: n}`` of a list of entries."""
    counts = {}
    for entry in entries:
        counts[entry.type] = counts.get(entry.type, 0) + 1
    return counts
