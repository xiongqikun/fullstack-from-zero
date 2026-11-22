"""Lesson discovery and safe loading.

Every ``stages/<stage>/<lesson>/lesson.py`` is loaded on its own: the source is
compiled and executed in a fresh module object, with standard output silenced.
Whatever goes wrong in one lesson module (a syntax error, an exception at
import time, even ``sys.exit()``) is recorded on that lesson and never stops
the others from loading.  Nothing is written to disk: no ``__pycache__``.

Lesson modules import nothing from the tool.  They receive every helper through
the context objects (``ctx`` for checks, ``sc`` for scenario builders).
"""

import contextlib
import io
import re
import traceback
import types
from pathlib import Path

from .syllabus import GATES, LESSONS, lesson_key

LESSON_ID = re.compile(r"^\d{1,2}\.\d{1,2}$")
STATION_ID = re.compile(r"^(\d{1,2}\.\d{1,2})([a-z])$")
FOLDER_PREFIX = re.compile(r"^(\d{2})-(.+)$")

TEXT = {
    "read_failed": "读不了这个文件（{reason}）",
    "load_failed": "加载时出错：{what}",
    "syntax": "第 {line} 行有语法错误：{message}",
    "raised": "{kind}: {message}{where}",
    "raised_where": "（第 {line} 行）",
    "exited": "代码调用了退出（{kind}），课程模块里不能这样做",
    "no_meta": "没有定义 META，或者 META 不是字典",
    "bad_id": "META['id'] 应该是 \"1.6\" 这样的字符串，现在是 {value!r}",
    "bad_stations": "META['stations'] 应该是字典组成的列表，每项有字符串 id",
    "duplicate": "课程编号 {id} 和 {other} 重复",
}


class Lesson:
    """One lesson folder and (when it loaded) the names its module defines."""

    def __init__(self, path, root):
        self.path = Path(path)
        self.folder = self.path.parent
        self.root = Path(root)
        try:
            self.rel = self.folder.relative_to(self.root).as_posix()
        except ValueError:
            self.rel = str(self.folder)
        self.namespace = {}
        self.error = ""
        self.error_detail = ""
        self.id = _guess_id(self.folder)
        self.title = ""
        self.stage = _guess_stage(self.folder)
        self.stations = []

    # -- status -------------------------------------------------------------
    @property
    def ok(self):
        """True when the module loaded and is usable at run time."""
        return not self.error

    @property
    def text_path(self):
        return self.folder / "lesson.md"

    @property
    def rules_path(self):
        return self.folder / "rules.md"

    # -- typed access to the module's names ---------------------------------
    def _get(self, name, kind, default):
        value = self.namespace.get(name)
        return value if isinstance(value, kind) else default

    @property
    def meta(self):
        return self._get("META", dict, {})

    @property
    def terms(self):
        return [item for item in self._get("TERMS", list, []) if isinstance(item, dict)]

    @property
    def checks(self):
        """Station id -> check function (``checks``; ``CHECKS`` is accepted too)."""
        value = self.namespace.get("checks")
        if not isinstance(value, dict):
            value = self.namespace.get("CHECKS")
        return value if isinstance(value, dict) else {}

    @property
    def hints(self):
        return self._get("HINTS", dict, {})

    @property
    def review(self):
        return [item for item in self._get("REVIEW", list, []) if isinstance(item, dict)]

    @property
    def scenarios(self):
        return self._get("SCENARIOS", dict, {})

    @property
    def exam(self):
        return [item for item in self._get("EXAM", list, []) if isinstance(item, dict)]

    @property
    def rules(self):
        """Rule ids this lesson introduces (META["rules"])."""
        rules = self.meta.get("rules")
        if not isinstance(rules, list):
            return []
        return [rule for rule in rules if isinstance(rule, str)]

    @property
    def station_ids(self):
        return [station["id"] for station in self.stations]

    def station(self, station_id):
        """The META entry of ``station_id``, or None."""
        for station in self.stations:
            if station["id"] == station_id:
                return station
        return None

    def station_number(self, station_id):
        """1 for the first station of the lesson, 2 for the second ..."""
        ids = self.station_ids
        return ids.index(station_id) + 1 if station_id in ids else 0

    def scenario_id(self, key):
        """The id a learner types for scenario ``key`` of this lesson."""
        return f"{self.id}-start" if key == "start" else str(key)

    def __repr__(self):
        return "<Lesson {} {}>".format(self.id or "?", self.rel)


def _guess_stage(folder):
    match = FOLDER_PREFIX.match(folder.parent.name)
    return int(match.group(1)) if match else None


def _guess_id(folder):
    stage = _guess_stage(folder)
    match = FOLDER_PREFIX.match(folder.name)
    if stage is None or not match:
        return ""
    return f"{stage}.{int(match.group(1))}"


def _line_in(exc, filename):
    """The last line of ``filename`` in the traceback of ``exc``, or 0."""
    line = 0
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == filename:
            line = frame.lineno or 0
    return line


def describe_exception(exc, filename=""):
    """A short description of ``exc`` (type, message, line); never a traceback."""
    if isinstance(exc, SyntaxError):
        return TEXT["syntax"].format(line=exc.lineno or "?", message=exc.msg)
    if isinstance(exc, (SystemExit, GeneratorExit)):
        return TEXT["exited"].format(kind=type(exc).__name__)
    line = _line_in(exc, filename) if filename else 0
    where = TEXT["raised_where"].format(line=line) if line else ""
    message = " ".join(str(exc).split())
    if len(message) > 200:
        message = message[:199] + "…"
    return TEXT["raised"].format(kind=type(exc).__name__, message=message, where=where)


def load_lesson(path, root):
    """Load one lesson module.  Never raises (except for Ctrl+C)."""
    lesson = Lesson(path, root)
    filename = str(lesson.path)
    try:
        source = lesson.path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        lesson.error = TEXT["read_failed"].format(reason=type(exc).__name__)
        lesson.error_detail = repr(exc)
        return lesson
    name = "course_lesson_" + re.sub(r"[^0-9a-zA-Z]+", "_", lesson.rel)
    module = types.ModuleType(name)
    module.__file__ = filename
    sink = io.StringIO()
    try:
        code = compile(source, filename, "exec")
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            exec(code, module.__dict__)  # noqa: S102 - this is how a lesson module is loaded
    except KeyboardInterrupt:
        raise
    except BaseException as exc:  # noqa: BLE001 - a lesson module must never take the tool down
        lesson.error = TEXT["load_failed"].format(what=describe_exception(exc, filename))
        lesson.error_detail = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__))
        return lesson
    lesson.namespace = module.__dict__
    _read_identity(lesson)
    return lesson


def _read_identity(lesson):
    """Copy id, title, stage and stations out of META; flag unusable modules."""
    meta = lesson.namespace.get("META")
    if not isinstance(meta, dict):
        lesson.error = TEXT["no_meta"]
        return
    lesson_id = meta.get("id")
    if not isinstance(lesson_id, str) or not LESSON_ID.match(lesson_id):
        lesson.error = TEXT["bad_id"].format(value=lesson_id)
        return
    stations = meta.get("stations")
    if (not isinstance(stations, list) or not stations or not all(
            isinstance(s, dict) and isinstance(s.get("id"), str) for s in stations)):
        lesson.id = lesson_id
        lesson.error = TEXT["bad_stations"]
        return
    lesson.id = lesson_id
    lesson.title = meta.get("title") if isinstance(meta.get("title"), str) else ""
    if isinstance(meta.get("stage"), int) and not isinstance(meta.get("stage"), bool):
        lesson.stage = meta["stage"]
    else:
        lesson.stage = int(lesson_id.split(".")[0])
    lesson.stations = stations


class Catalog:
    """All lessons of a workspace, in syllabus order."""

    def __init__(self, root, lessons):
        self.root = Path(root)
        seen = {}
        for lesson in lessons:
            if lesson.ok and lesson.id in seen:
                lesson.error = TEXT["duplicate"].format(id=lesson.id, other=seen[lesson.id].rel)
            elif lesson.ok:
                seen[lesson.id] = lesson
        self.all = sorted(lessons, key=lambda item: (lesson_key(item.id), item.rel))
        self.lessons = [lesson for lesson in self.all if lesson.ok]
        self.broken = [lesson for lesson in self.all if not lesson.ok]

    # -- lookups ------------------------------------------------------------
    def lesson(self, lesson_id, include_broken=False):
        for lesson in (self.all if include_broken else self.lessons):
            if lesson.id == lesson_id:
                return lesson
        return None

    def station(self, station_id):
        """``(lesson, station dict)`` for a station id, or ``(None, None)``."""
        for lesson in self.lessons:
            station = lesson.station(station_id)
            if station is not None:
                return lesson, station
        return None, None

    def stations(self):
        """Every ``(lesson, station dict)`` in learning order."""
        return [(lesson, station) for lesson in self.lessons for station in lesson.stations]

    def stages(self):
        """Stage numbers that have at least one usable lesson, ascending."""
        return sorted({lesson.stage for lesson in self.lessons})

    def lessons_in_stage(self, stage):
        return [lesson for lesson in self.lessons if lesson.stage == stage]

    def broken_for(self, text):
        """A broken lesson that ``text`` (a lesson or station id) points into."""
        match = STATION_ID.match(text)
        lesson_id = match.group(1) if match else text
        for lesson in self.broken:
            if lesson.id == lesson_id:
                return lesson
        return None

    # -- scenarios, review items, exam tasks --------------------------------
    def scenario_ids(self):
        ids = []
        for lesson in self.lessons:
            for key in lesson.scenarios:
                ids.append(lesson.scenario_id(key))
        return ids

    def scenario(self, text):
        """``(lesson, key, builder)`` for what a learner typed, or None.

        ``1.6`` and ``1.6-start`` both mean the ``start`` scenario of 1.6.
        """
        for lesson in self.lessons:
            scenarios = lesson.scenarios
            if text in (lesson.id, lesson.id + "-start") and "start" in scenarios:
                return lesson, "start", scenarios["start"]
        for lesson in self.lessons:
            scenarios = lesson.scenarios
            if text != "start" and text in scenarios:
                return lesson, text, scenarios[text]
        return None

    def review_items(self):
        """Every ``(lesson, item)`` of every REVIEW list."""
        return [(lesson, item) for lesson in self.lessons for item in lesson.review]

    def review_item(self, item_id):
        for lesson, item in self.review_items():
            if item.get("id") == item_id:
                return lesson, item
        return None, None

    def exam_tasks(self, gate=None):
        """Every ``(lesson, task)`` of every EXAM list, optionally for one gate."""
        pairs = [(lesson, task) for lesson in self.lessons for task in lesson.exam]
        if gate is None:
            return pairs
        return [(lesson, task) for lesson, task in pairs if task.get("gate") == gate]

    # -- gates --------------------------------------------------------------
    def gate_ids(self):
        """The gates of the syllabus, then any other gate a task names."""
        gates = list(GATES)
        for _lesson, task in self.exam_tasks():
            gate = task.get("gate")
            if isinstance(gate, str) and gate not in gates:
                gates.append(gate)
        return gates

    def gate_pool(self, gate):
        """``(primary, secondary, unusable_ids)`` for ``gate``.

        ``primary``: usable tasks whose ``gate`` is this gate, as ``(lesson,
        task)`` in learning order; their lessons are the lessons the gate
        covers (gate-1: 1.11 to 1.16).  ``secondary`` is always empty: a gate
        no longer borrows tasks of other gates (COMMON.md section 1; the
        tuple keeps its three parts for older callers).  ``unusable_ids``:
        tasks of this gate that lack something (``usable_exam_task``).  The
        rule of a sitting is in ``courselib.progress``.
        """
        primary, unusable, seen = [], [], set()
        for lesson, task in self.exam_tasks(gate):
            task_id = task.get("id")
            if not usable_exam_task(task) or task_id in seen:
                unusable.append(str(task_id))
                continue
            seen.add(task_id)
            primary.append((lesson, task))
        return primary, [], unusable

    def gate_lesson_ids(self, gate):
        """The lessons ``gate`` covers, in learning order.

        The lessons of its usable tasks; when it has none yet, the lessons the
        syllabus assigns to it (``LESSONS[...]["gate"]``), else its range in
        ``syllabus.GATES``.
        """
        primary, _secondary, _unusable = self.gate_pool(gate)
        ids = []
        for lesson, _task in primary:
            if lesson.id not in ids:
                ids.append(lesson.id)
        return ids or syllabus_gate_lessons(gate)


def syllabus_gate_lessons(gate):
    """The lesson ids the syllabus assigns to ``gate`` (its ``gate`` field), in order."""
    ids = [entry["id"] for entry in LESSONS if entry.get("gate") == gate]
    return ids or list(GATES.get(gate, {}).get("lessons", []))


EXAM_FORMS = ("A", "B")


def usable_exam_task(task):
    """True when an exam task has everything the ``exam`` command needs."""
    text = task.get("task")
    return bool(isinstance(task.get("id"), str) and task.get("id")
                and callable(task.get("build")) and callable(task.get("grade"))
                and isinstance(text, dict)
                and all(isinstance(text.get(form), str) and text[form].strip()
                        for form in EXAM_FORMS))


def find_lesson_files(root):
    """Every ``stages/*/*/lesson.py`` under ``root``, sorted."""
    return sorted(Path(root).glob("stages/*/*/lesson.py"))


def load_catalog(root):
    """Discover and load every lesson of the workspace at ``root``."""
    return Catalog(root, [load_lesson(path, root) for path in find_lesson_files(root)])
