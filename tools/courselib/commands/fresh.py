"""``fresh``: compare installed tool versions with the course baseline (plan I4).

Read-only and offline.  For every tool in ``tools/courselib/baseline.json``
it runs the tool's own version command (with a timeout, as an argument list,
never through a shell) and classifies the result:

- 一致        same version numbers as the baseline
- 小版本变了  same major version, something after it differs
- 大版本变了  the major version differs; for a tool whose major number is 0
              (uv, Ruff) the first two numbers count as the major version,
              because 0.x tools make breaking changes in the minor number
- 没装        the command is not on PATH
- 还没安装（第 1.11 课会装）  the command is not on PATH, the entry names the
              lesson that installs it (``"installed_in": "1.11"``) and that
              lesson is not done yet (some station of it has not passed):
              not a problem, nothing to check
- 看不懂版本  the command ran but printed nothing the pattern recognises

Then it lists the lessons whose ``META["verified"]["tools"]`` name a tool
that is not 一致, and ends with one sentence on what to do.  A missing tool
or an unreadable version is a line of the report, never an error.  Only an
unreadable baseline file is a 检查器出问题 (exit code 2).

``fresh`` writes nothing.  It reads ``learner/state.json`` directly and only
for reading (never through ``app.store``; a damaged or missing file counts as
"nothing passed") to know whether the lesson named by ``installed_in`` is
done.  A test may replace the module attributes ``BASELINE`` (path of the
baseline file) and ``RUN_TIMEOUT``.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

from .. import cmdkit
from ..errors import EXIT_OK, ToolTrouble
from ..store import reason as os_reason
from ..syllabus import TOOL_NAMES, lesson_entry, lesson_key
from ..ui import display_width, pad

BASELINE = Path(__file__).resolve().parent.parent / "baseline.json"
RUN_TIMEOUT = 15

SAME = "same"
MINOR = "minor"
MAJOR = "major"
MISSING = "missing"
LATER = "later"
UNKNOWN = "unknown"

SUMMARY = "检查课程内容有没有过时（对比工具版本，只看不改）"

DESCRIPTION = """\
把这台电脑上装的工具版本，和课程核对时用的版本（tools/courselib/baseline.json）比一比，
列出哪些工具变了、哪些课可能受影响。只看不改，不联网。

例子：
  python3 tools/course.py fresh"""

TEXT = {
    "title": "版本核对 · {date}",
    "intro": "课程里的命令是在 {date} 用下面这些版本核对的。只看不改，不联网。",
    "col_tool": "工具",
    "col_baseline": "课程核对时",
    "col_installed": "这台电脑",
    "col_result": "结论",
    "same": "一致",
    "minor": "小版本变了",
    "major": "大版本变了",
    "missing": "没装",
    "later": "还没安装（第 {lesson} 课会装）",
    "unknown": "看不懂版本",
    "newer": "（比课程新）",
    "older": "（比课程旧）",
    "none": "-",
    "why_missing": "{tool}：在 PATH 里找不到 {command} 命令。",
    "why_unknown": "{tool}：运行 {command} 得到的是「{output}」，从里面看不出版本号。",
    "why_failed": "{tool}：运行 {command} 失败（{reason}）。",
    "why_timeout": "超过 {seconds} 秒没有结束",
    "why_exit": "退出码 {code}",
    "why_nothing": "什么也没输出",
    "details_head": "说明：",
    "lessons_head": "可能受影响的课（核对它们时用到了上面变了的工具）：",
    "lessons_none": "可能受影响的课：没有。",
    "lesson_line": "{id} {title}：{tools}",
    "lesson_tool": "{tool}（{result}）",
    "uncovered_head": "课程模块里提到、但基线里没有记录版本的工具（fresh 不比较它们）：",
    "uncovered_line": "{tool}：{lessons}",
    "next_affected": "下一步：把这段发给导师，说“帮我核实受影响的课”。",
    "next_changed": "下一步：有工具的版本变了，但现有的课都没有用到它们，可以照常学。想确认的话，把这段发给导师。",
    "next_clean": "下一步：所有工具都和课程核对时一样，不用做什么。",
    "next_clean_later": "下一步：装了的工具都和课程核对时一样，不用做什么。还没安装的，到了上面写的那一课会带你装。",
    "bad_baseline": "版本基线文件 {name} 读不了。",
    "bad_baseline_recovery": "这不是你的错。把这段发给导师，说“急救：fresh 的基线文件坏了”。",
}


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "fresh", SUMMARY, description=DESCRIPTION)
    return parser


def run(args):
    app = args.app
    baseline = load_baseline(BASELINE)
    done = lesson_done_reader(app)
    results = [probe(app, name, entry, lesson_done=done)
               for name, entry in baseline["tools"].items()]
    lessons, uncovered = affected_lessons(app, results)
    for line in render(app, baseline, results, lessons, uncovered):
        app.console.out(line)
    return EXIT_OK


# ---------------------------------------------------------------------------
# The baseline file
# ---------------------------------------------------------------------------
def load_baseline(path):
    """The parsed baseline; ToolTrouble when it is missing or malformed."""
    name = "tools/courselib/baseline.json"
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        tools = data["tools"]
        if not isinstance(tools, dict) or not tools:
            raise ValueError("'tools' must be a non-empty object")
        for key, entry in tools.items():
            command = entry["command"]
            if not (isinstance(command, list) and command
                    and all(isinstance(word, str) for word in command)):
                raise ValueError(f"tools.{key}.command must be a list of strings")
            if not isinstance(entry["version"], str) or parse_version(entry["version"]) is None:
                raise ValueError(f"tools.{key}.version is not a version")
            re.compile(entry.get("pattern") or r"(\d+(?:\.\d+)+)")
            later = entry.get("installed_in")
            if later is not None and not (isinstance(later, str)
                                          and re.match(r"^\d+\.\d+$", later)):
                raise ValueError(f"tools.{key}.installed_in must be a lesson id such as 1.11")
        str(data["verified_on"])
    except (OSError, ValueError, KeyError, TypeError, AttributeError, re.error) as exc:
        raise ToolTrouble(TEXT["bad_baseline"].format(name=name),
                          detail=f"{type(exc).__name__}: {exc}",
                          recovery=TEXT["bad_baseline_recovery"], where=name)
    return data


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------
def parse_version(text):
    """``"2.54.0"`` -> ``(2, 54, 0)``; None when ``text`` holds no number."""
    match = re.search(r"\d+(?:\.\d+)*", str(text or ""))
    if not match:
        return None
    return tuple(int(part) for part in match.group(0).split("."))


def major_part(numbers):
    """The part of a version that marks breaking changes."""
    return tuple(numbers[:2]) if numbers and numbers[0] == 0 else tuple(numbers[:1])


def _padded(numbers, size=3):
    return tuple(numbers) + (0,) * max(0, size - len(numbers))


def classify(baseline, installed):
    """SAME, MINOR or MAJOR for two version tuples (``5.9`` equals ``5.9.0``)."""
    size = max(len(baseline), len(installed), 3)
    if _padded(baseline, size) == _padded(installed, size):
        return SAME
    if _padded(major_part(baseline), 2) != _padded(major_part(installed), 2):
        return MAJOR
    return MINOR


class ToolResult:
    """What ``probe`` found out about one tool."""

    def __init__(self, name, label, baseline, status, installed="", why=""):
        self.name = name
        self.label = label
        self.baseline = baseline
        self.status = status
        self.installed = installed
        self.why = why
        self.direction = ""

    lesson = ""

    @property
    def drifted(self):
        """True for a result worth a look (a tool still to be installed is not)."""
        return self.status not in (SAME, LATER)

    def result_text(self):
        return TEXT[self.status].format(lesson=self.lesson) + self.direction

    def __repr__(self):
        return f"<ToolResult {self.name} {self.status} {self.installed!r}>"


def probe(app, name, entry, lesson_done=None):
    """Run the version command of one tool and classify the answer.

    ``lesson_done(lesson_id) -> bool`` tells whether a lesson is done; a
    tool that is not installed and whose ``installed_in`` lesson is not done
    is LATER.  Without it every lesson counts as not done.
    """
    label = entry.get("label") or TOOL_NAMES.get(name, name)
    baseline = entry["version"]
    command = list(entry["command"])
    shown = " ".join(command)
    program = shutil.which(command[0], path=app.env.get("PATH", ""))
    if not program:
        later = entry.get("installed_in")
        if later and not (lesson_done or (lambda _lesson: False))(later):
            result = ToolResult(name, label, baseline, LATER)
            result.lesson = later
            return result
        return ToolResult(name, label, baseline, MISSING,
                          why=TEXT["why_missing"].format(tool=label, command=command[0]))
    env = app.child_env()
    env["LC_ALL"] = "C"
    try:
        done = subprocess.run([program] + command[1:], env=env, cwd="/",
                              stdin=subprocess.DEVNULL, capture_output=True,
                              timeout=RUN_TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        return ToolResult(name, label, baseline, UNKNOWN, why=TEXT["why_failed"].format(
            tool=label, command=shown, reason=TEXT["why_timeout"].format(seconds=RUN_TIMEOUT)))
    except OSError as exc:
        return ToolResult(name, label, baseline, UNKNOWN, why=TEXT["why_failed"].format(
            tool=label, command=shown, reason=os_reason(exc)))
    out = done.stdout.decode("utf-8", "replace")
    err = done.stderr.decode("utf-8", "replace")
    pattern = re.compile(entry.get("pattern") or r"(\d+(?:\.\d+)+)", re.MULTILINE)
    found = None
    for text in (out, err):
        match = pattern.search(text)
        if match:
            found = match.group(1) if match.groups() else match.group(0)
            break
    numbers = parse_version(found) if found else None
    if numbers is None:
        if done.returncode != 0 and not out.strip():
            reason = TEXT["why_exit"].format(code=done.returncode)
            return ToolResult(name, label, baseline, UNKNOWN, why=TEXT["why_failed"].format(
                tool=label, command=shown, reason=reason))
        output = _first_line(out) or _first_line(err)
        why = (TEXT["why_unknown"].format(tool=label, command=shown, output=app.scrub(output))
               if output else TEXT["why_failed"].format(tool=label, command=shown,
                                                        reason=TEXT["why_nothing"]))
        return ToolResult(name, label, baseline, UNKNOWN, why=why)
    version = ".".join(str(n) for n in numbers)
    base_numbers = parse_version(baseline)
    result = ToolResult(name, label, baseline, classify(base_numbers, numbers), installed=version)
    if result.drifted:
        result.direction = (TEXT["newer"] if _padded(numbers, 4) > _padded(base_numbers, 4)
                            else TEXT["older"])
    return result


def _first_line(text, limit=60):
    for line in str(text or "").splitlines():
        line = line.strip()
        if line:
            return line if len(line) <= limit else line[: limit - 1] + "…"
    return ""


# ---------------------------------------------------------------------------
# Lessons
# ---------------------------------------------------------------------------
def lesson_done_reader(app):
    """``lesson_done(lesson_id) -> bool``: every station of the lesson has passed.

    ``learner/state.json`` is read once, directly and read-only; a missing or
    damaged file counts as nothing passed.  The stations come from the
    syllabus, else from the lesson catalogue.
    """
    stations = {}
    try:
        with open(str(app.root / "learner" / "state.json"), "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict) and isinstance(data.get("stations"), dict):
            stations = data["stations"]
    except (OSError, ValueError):
        stations = {}

    def lesson_done(lesson_id):
        entry = lesson_entry(lesson_id)
        ids = list(entry["stations"]) if entry else []
        if not ids:
            lesson = app.catalog().lesson(lesson_id)
            ids = list(lesson.station_ids) if lesson is not None else []
        return bool(ids) and all(
            isinstance(stations.get(sid), dict) and bool(stations[sid].get("first_pass"))
            for sid in ids)
    return lesson_done


def lesson_tools(lesson):
    """The tool names of ``META["verified"]["tools"]`` (empty when malformed)."""
    verified = lesson.meta.get("verified")
    if not isinstance(verified, dict):
        return []
    tools = verified.get("tools")
    if not isinstance(tools, dict):
        return []
    return [name for name in tools if isinstance(name, str)]


def affected_lessons(app, results):
    """``([(lesson, [ToolResult])], {tool name: [lesson id]})``.

    The second value lists tools that lessons name but the baseline does not
    cover.
    """
    by_name = {result.name: result for result in results}
    affected = []
    uncovered = {}
    for lesson in sorted(app.catalog().lessons, key=lambda item: lesson_key(item.id)):
        drifted = []
        for name in lesson_tools(lesson):
            result = by_name.get(name)
            if result is None:
                uncovered.setdefault(name, []).append(lesson.id)
            elif result.drifted:
                drifted.append(result)
        if drifted:
            affected.append((lesson, drifted))
    return affected, uncovered


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def render(app, baseline, results, lessons, uncovered):
    date = str(baseline.get("verified_on", ""))
    lines = [TEXT["title"].format(date=app.today.isoformat()),
             TEXT["intro"].format(date=date), ""]
    header = [TEXT["col_tool"], TEXT["col_baseline"], TEXT["col_installed"], TEXT["col_result"]]
    rows = [[r.label, r.baseline, r.installed or TEXT["none"], r.result_text()] for r in results]
    widths = [max(_width(row[i]) for row in [header] + rows) + 2 for i in range(3)]
    for row in [header] + rows:
        lines.append("  " + "".join(pad(cell, widths[i]) for i, cell in enumerate(row[:3]))
                     + row[3])
    reasons = [r.why for r in results if r.why]
    if reasons:
        lines += ["", TEXT["details_head"]]
        lines += ["  - " + why for why in reasons]
    lines.append("")
    if lessons:
        lines.append(TEXT["lessons_head"])
        for lesson, tools in lessons:
            names = "、".join(
                TEXT["lesson_tool"].format(tool=r.label,
                                           result=TEXT[r.status].format(lesson=r.lesson))
                for r in tools)
            title = lesson.meta.get("title") or lesson.title or ""
            lines.append("  - " + TEXT["lesson_line"].format(id=lesson.id, title=title, tools=names))
    else:
        lines.append(TEXT["lessons_none"])
    if uncovered:
        lines += ["", TEXT["uncovered_head"]]
        for name in sorted(uncovered):
            lines.append("  - " + TEXT["uncovered_line"].format(
                tool=TOOL_NAMES.get(name, name), lessons="、".join(uncovered[name])))
    lines.append("")
    if lessons:
        lines.append(TEXT["next_affected"])
    elif any(r.drifted for r in results):
        lines.append(TEXT["next_changed"])
    elif any(r.status == LATER for r in results):
        lines.append(TEXT["next_clean_later"])
    else:
        lines.append(TEXT["next_clean"])
    return lines


def _width(text):
    return display_width(text)
