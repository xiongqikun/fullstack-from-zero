"""Leitner boxes for review items (plan I4, ``review``).

Five boxes with growing intervals: 2 days, 1 week, 3 weeks, 2 months,
6 months.  An item enters box 1 when the station it belongs to is first
passed.  Each answer moves it:

- ``right``  (记得, or a correct choice, or a passed ``do`` check): one box
  up, due again after the interval of the new box.  Right in the last box:
  the item is **retired** (``retired`` holds the date, ``due`` becomes None)
  and is never scheduled again.
- ``fuzzy``  (模糊): the box is kept, due again after the interval of that box.
- ``wrong``  (忘了, a wrong choice, a ``do`` task given up): back to box 1,
  due again **the next day**.

Only items with tier ``fluent`` are scheduled.  The functions work on the
plain state dict; ``today`` is a ``datetime.date``.  Records written by hand
or by an older tool are read leniently: an unreadable box counts as box 1.

Record of one item in ``state["review"]``::

    {"box": 1, "due": "2026-11-21",
     "history": [{"date": "...", "result": "right|fuzzy|wrong", "box": 2}],
     "retired": "2027-09-01",                   # only once retired
     "pending": {"since": "...", "folder": "review/1.6-r3", "tries": 0}}
                                                # only while a do task is out

The session logic on top of this (what is served, in which order, the return
routine, cold redos) lives in ``courselib.review``.
"""

import datetime

INTERVAL_DAYS = (2, 7, 21, 60, 180)
BOXES = len(INTERVAL_DAYS)
MISS_DAYS = 1
MAX_HISTORY = 50
SCHEDULED_TIER = "fluent"

RIGHT = "right"
FUZZY = "fuzzy"
WRONG = "wrong"
RESULTS = (RIGHT, FUZZY, WRONG)


def interval(box):
    """Days until an item in ``box`` (1 to 5) is due again."""
    return INTERVAL_DAYS[max(1, min(int(box), BOXES)) - 1]


def box_of(record):
    """The box of a record, 1 to 5; anything unreadable counts as box 1."""
    try:
        box = int((record or {}).get("box") or 1)
    except (TypeError, ValueError, AttributeError):
        return 1
    return max(1, min(box, BOXES))


def is_retired(record):
    return isinstance(record, dict) and bool(record.get("retired"))


def is_enrolled(state, item_id):
    return isinstance(state.get("review", {}).get(item_id), dict)


def enroll(state, item_id, today):
    """Put a new item into box 1.  Returns its record (unchanged if it exists)."""
    review = state.setdefault("review", {})
    if isinstance(review.get(item_id), dict):
        return review[item_id]
    record = {"box": 1, "due": (today + datetime.timedelta(days=interval(1))).isoformat(),
              "history": []}
    review[item_id] = record
    return record


def due_date(record):
    """The due date of a record as a ``date``; None when it is unreadable or retired."""
    if is_retired(record):
        return None
    try:
        return datetime.date.fromisoformat(str(record.get("due"))[:10])
    except (ValueError, AttributeError):
        return None


def due_items(state, today):
    """Ids of the items due on or before ``today``, most overdue first."""
    found = []
    for item_id, record in state.get("review", {}).items():
        if not isinstance(record, dict):
            continue
        due = due_date(record)
        if due is not None and due <= today:
            found.append((due, item_id))
    return [item_id for due, item_id in sorted(found)]


def next_due(state, today):
    """The earliest due date after ``today``; None when nothing is scheduled."""
    later = []
    for record in state.get("review", {}).values():
        due = due_date(record) if isinstance(record, dict) else None
        if due is not None and due > today:
            later.append(due)
    return min(later) if later else None


def answer(state, item_id, result, today):
    """Record one answer (``right``, ``fuzzy`` or ``wrong``) and reschedule.

    Returns the record.  ``record["retired"]`` is set when a right answer in
    the last box retired the item.
    """
    if result not in RESULTS:
        raise ValueError(f"result must be one of {RESULTS}, got {result!r}")
    record = enroll(state, item_id, today)
    box = box_of(record)
    entry = {"date": today.isoformat(), "result": result}
    if result == RIGHT and box >= BOXES:
        record["box"] = BOXES
        record["due"] = None
        record["retired"] = today.isoformat()
        entry["retired"] = True
    else:
        if result == RIGHT:
            box += 1
            days = interval(box)
        elif result == FUZZY:
            days = interval(box)
        else:
            box = 1
            days = MISS_DAYS
        record["box"] = box
        record["due"] = (today + datetime.timedelta(days=days)).isoformat()
        record.pop("retired", None)
    entry["box"] = record["box"]
    history = record.get("history")
    if not isinstance(history, list):
        history = record["history"] = []
    history.append(entry)
    del history[:-MAX_HISTORY]
    return record


def grade(state, item_id, correct, today):
    """Right or wrong (see ``answer``).  Returns the record."""
    return answer(state, item_id, RIGHT if correct else WRONG, today)


def last_result(record):
    """``right`` / ``fuzzy`` / ``wrong`` of the latest answer, or None."""
    history = (record or {}).get("history")
    if isinstance(history, list):
        for entry in reversed(history):
            if isinstance(entry, dict) and entry.get("result") in RESULTS:
                return entry["result"]
    return None


def box_counts(state):
    """How many scheduled (not retired) items sit in each box: ``[n1, ..., n5]``."""
    counts = [0] * BOXES
    for record in state.get("review", {}).values():
        if isinstance(record, dict) and not is_retired(record):
            counts[box_of(record) - 1] += 1
    return counts


def retired_count(state):
    return sum(1 for record in state.get("review", {}).values() if is_retired(record))


def item_station(lesson, item):
    """The station an item belongs to (its ``station`` key, else the last station)."""
    station = item.get("station")
    ids = lesson.station_ids
    if station in ids:
        return station
    return ids[-1] if ids else ""


def enroll_station_items(state, lesson, station_id, today):
    """Enrol the fluent items of ``station_id``; returns the newly enrolled ids."""
    added = []
    for item in lesson.review:
        item_id = item.get("id")
        if (not isinstance(item_id, str) or item.get("tier") != SCHEDULED_TIER
                or item_station(lesson, item) != station_id or is_enrolled(state, item_id)):
            continue
        enroll(state, item_id, today)
        added.append(item_id)
    return added
