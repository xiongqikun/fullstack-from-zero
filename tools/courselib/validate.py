"""The builders' validator (plan I4 ``validate``).

For every lesson it checks:

- the interface of plan I3 (the names a lesson module must define and their
  shapes, exactly as docs/authoring/tool-api.md describes them);
- the budgets of plan G5 as revised by G5a (2 or 3 stations; ``minutes`` an
  integer from 15 to 40, a warning above 30 because the number must be the
  calculated one of G5a and movable material belongs in a 「想多了解（可跳
  过）」 box; one new concept and at most five new commands per station, one
  check per station, at most two rule cards per lesson);
- that the minutes in the station headings of lesson.md (「## 第 N 站：……（约
  X 分钟）」) agree with META (a warning; headings without minutes are fine);
- that no option of a quiz, a choice or a choice review item is a word the
  review session reads as a command (``q`` ends the session, ``s`` skips): a
  learner who types that option's text would end or skip instead (a warning);
- the rule cards of plan I2: all thirteen fields, the two label axes of plan
  G3 (约束力 with a scope; exactly one 规则类型), a source and a check date;
- the syllabus of plan section 4 (folder, station ids, rule ids, gate) for the
  lessons listed there;
- four hints and one check for every station;
- the one wording of the recurring parts of lesson.md (``check_lesson_forms``,
  all warnings): save points, the four parts of a station and the hint and
  check lines, the closing section and its last line, the G6 line and marks,
  sentences to the tutor, quotation marks, course-folder paths and names,
  labels of optional material, the rule summary against the cards, since-when
  in old-tutorial boxes, ``git config`` without a subcommand, the header's
  minutes; the same for the texts of lesson.py where they apply;
- across lessons: rule, term, command and item claimed twice, one English
  gloss under two terms, and the decided owners of terms and commands;
- that the module compiles on Python 3.9 (with a real 3.9 interpreter when the
  machine has one, because newer interpreters accept syntax that 3.9 rejects).

A finding is an *error* (the lesson is rejected) or a *warning* (worth a look).
Lessons outside the syllabus (later stages, the worked example) only get the
general checks.
"""

import ast
import datetime
import inspect
import re
import subprocess
import sys
import tempfile

from . import rulecards, scenario
from .catalog import FOLDER_PREFIX, LESSON_ID
from .errors import CourseError
from .normalize import letter_to_index, normalize
from .syllabus import GATES, LESSONS, TOOL_NAMES, lesson_entry, lesson_key

ERROR = "error"
WARNING = "warning"

MIN_STATIONS, MAX_STATIONS = 2, 3
#: Plan G5a: accepted 15-40, a warning above 30; G5's 20-25 stays the target.
MIN_MINUTES, MAX_MINUTES = 15, 40
WARN_MINUTES = 30
TARGET_MINUTES = (20, 25)
#: Context methods whose second argument is a list of options the learner
#: picks from by letter or by text (checked against the review commands).
CHOICE_METHODS = ("quiz", "choose")
_STATION_HEADING = re.compile(
    r"^##\s*第\s*([0-9一二三四五六七八九]+)\s*站\s*[：:](.*)$")
_HEADING_BRACKET = re.compile(r"[（(]([^（）()]*)[）)]\s*$")
_HEADING_MINUTES = re.compile(r"约\s*(\d+)\s*分钟")
_CN_SMALL = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
MAX_COMMANDS = 5
MAX_RULES = 2
MIN_GATE_TASKS = 4

META_KEYS = ("id", "slug", "title", "stage", "prerequisites", "stations", "rules",
             "verified", "unverified_steps")
STATION_KEYS = ("id", "title", "minutes", "new_concept", "new_commands")
REVIEW_TYPES = ("recall", "predict", "which", "fault", "do")
CHOICE_TYPES = ("predict", "which", "fault")
TIERS = ("fluent", "lookup", "aware")
_GATE = re.compile(r"^gate-[a-z0-9]+$")
_VERSION = re.compile(r"^\d+(\.\d+)*([a-z0-9.+-]*)$")
_PLACEHOLDER = re.compile(r"\{([a-z_][a-z0-9_]*)\}")

#: Where a Python 3.9 usually lives on macOS (the system one from Apple's developer tools).
OLD_PYTHONS = (
    "/Library/Developer/CommandLineTools/usr/bin/python3",
    "/Applications/Xcode.app/Contents/Developer/usr/bin/python3",
    "/usr/bin/python3",
)
_PROBE = "import sys; print('%d.%d' % sys.version_info[:2])"
_COMPILE = (
    "import sys\n"
    "for path in sys.argv[1:]:\n"
    "    try:\n"
    "        compile(open(path, encoding='utf-8').read(), path, 'exec')\n"
    "        print('OK')\n"
    "    except SyntaxError as exc:\n"
    "        print('BAD %s %s' % (exc.lineno, exc.msg))\n"
    "    except Exception as exc:\n"
    "        print('BAD 0 %s' % type(exc).__name__)\n"
)


class Finding:
    def __init__(self, level, code, message):
        self.level = level
        self.code = code
        self.message = message

    def __repr__(self):
        return f"<{self.level} [{self.code}] {self.message}>"


class Report:
    """The findings about one lesson."""

    def __init__(self, lesson):
        self.lesson = lesson
        self.findings = []

    def error(self, code, message):
        self.findings.append(Finding(ERROR, code, message))

    def warn(self, code, message):
        self.findings.append(Finding(WARNING, code, message))

    @property
    def errors(self):
        return [f for f in self.findings if f.level == ERROR]

    @property
    def warnings(self):
        return [f for f in self.findings if f.level == WARNING]

    @property
    def ok(self):
        return not self.errors


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _takes_one(function):
    """Can ``function`` be called with exactly one positional argument?"""
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError):
        return True
    try:
        signature.bind(object())
    except TypeError:
        return False
    return True


def _date(text):
    try:
        return datetime.date.fromisoformat(text) if isinstance(text, str) and len(text) == 10 else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# One lesson
# ---------------------------------------------------------------------------
def validate_lesson(lesson, today, complete=False):
    """Check one loaded ``Lesson``; returns a ``Report``."""
    report = Report(lesson)
    if lesson.error and not lesson.namespace:
        report.error("I3", f"课程模块用不了：{lesson.error}")
        return report
    names = lesson.namespace
    _check_names(report, names)
    meta = names.get("META")
    station_ids = []
    if isinstance(meta, dict):
        station_ids = _check_meta(report, lesson, meta, today, complete)
    if lesson.error:
        report.error("I3", f"课程模块用不了：{lesson.error}")
    lesson_id = meta.get("id") if isinstance(meta, dict) and isinstance(meta.get("id"), str) else ""
    _check_terms(report, names.get("TERMS"), station_ids)
    _check_checks(report, names, station_ids)
    _check_hints(report, names.get("HINTS"), station_ids)
    scenario_keys = _check_scenarios(report, names.get("SCENARIOS"), lesson_id)
    review_ids = _check_review(report, names.get("REVIEW"), lesson_id, station_ids,
                               scenario_keys, meta if isinstance(meta, dict) else {})
    _check_exam(report, names.get("EXAM"), lesson_id, review_ids)
    _check_choice_options(report, lesson, names)
    if isinstance(meta, dict):
        _check_rule_cards(report, lesson, meta, today)
        _check_syllabus(report, lesson, meta, names)
    _check_text(report, lesson, station_ids, complete)
    return report


def _check_names(report, names):
    wanted = (("META", dict, "字典"), ("TERMS", list, "列表"), ("HINTS", dict, "字典"),
              ("REVIEW", list, "列表"), ("SCENARIOS", dict, "字典"), ("EXAM", list, "列表"))
    for name, kind, word in wanted:
        if name not in names:
            report.error("I3", f"缺少 {name}（要定义成{word}）")
        elif not isinstance(names[name], kind):
            report.error("I3", f"{name} 应该是{word}，现在是 {type(names[name]).__name__}")
    has_lower, has_upper = "checks" in names, "CHECKS" in names
    if has_lower and has_upper:
        report.error("I3", "checks 和 CHECKS 只能定义一个（请用小写的 checks）")
    elif not has_lower and not has_upper:
        report.error("I3", "缺少 checks（站点编号到检查函数的字典）")
    else:
        value = names.get("checks", names.get("CHECKS"))
        if not isinstance(value, dict):
            report.error("I3", f"checks 应该是字典，现在是 {type(value).__name__}")


def _check_meta(report, lesson, meta, today, complete):
    """Check META; returns the list of station ids (possibly empty)."""
    for key in META_KEYS:
        if key not in meta:
            report.error("I3", f"META 缺少 {key!r}")
    lesson_id = meta.get("id")
    id_ok = isinstance(lesson_id, str) and bool(LESSON_ID.match(lesson_id))
    if "id" in meta and not id_ok:
        report.error("I3", f"META['id'] 要写成 \"1.6\" 这样的字符串，现在是 {lesson_id!r}")
    stage_part = int(lesson_id.split(".")[0]) if id_ok else None
    number_part = int(lesson_id.split(".")[1]) if id_ok else None

    # folders (plan section 2 and G12)
    folder, stage_folder = lesson.folder.name, lesson.folder.parent.name
    folder_match = FOLDER_PREFIX.match(folder)
    stage_match = FOLDER_PREFIX.match(stage_folder)
    if not folder_match or not re.match(r"^\d{2}(-[a-z0-9]+)+$", folder):
        report.error("G12", f"课程文件夹名要写成 06-first-commit 这样（两位数字加小写英文短横线），现在是 {folder}")
    elif id_ok and int(folder_match.group(1)) != number_part:
        report.error("G12", f"课程文件夹 {folder} 的序号和 META['id']={lesson_id} 对不上")
    if not stage_match or not re.match(r"^\d{2}(-[a-z0-9]+)+$", stage_folder):
        report.error("G12", f"阶段文件夹名要写成 01-foundations 这样，现在是 {stage_folder}")
    elif id_ok and int(stage_match.group(1)) != stage_part:
        report.error("G12", f"阶段文件夹 {stage_folder} 和 META['id']={lesson_id} 的阶段号对不上")
    if "slug" in meta and meta.get("slug") != folder:
        report.error("I3", "META['slug'] 要和课程文件夹名完全一样（{}），现在是 {!r}".format(folder, meta.get("slug")))
    if "title" in meta and not _text(meta.get("title")):
        report.error("I3", "META['title'] 不能为空")
    if "stage" in meta:
        if not _is_int(meta.get("stage")):
            report.error("I3", "META['stage'] 要是整数，现在是 {!r}".format(meta.get("stage")))
        elif id_ok and meta["stage"] != stage_part:
            report.error("I3", "META['stage']={!r} 和 META['id']={} 对不上".format(meta["stage"], lesson_id))

    # prerequisites
    prerequisites = meta.get("prerequisites")
    if "prerequisites" in meta:
        if not isinstance(prerequisites, list):
            report.error("I3", "META['prerequisites'] 要是课程编号的列表（没有就写 []）")
        else:
            for item in prerequisites:
                if not isinstance(item, str) or not LESSON_ID.match(item):
                    report.error("I3", f"前置课程编号写法不对：{item!r}")
                elif id_ok and lesson_key(item) >= lesson_key(lesson_id):
                    report.error("I3", f"前置课程 {item} 必须排在本课 {lesson_id} 之前")

    # stations (plan G5)
    station_ids = []
    stations = meta.get("stations")
    if "stations" in meta:
        if not isinstance(stations, list) or not all(isinstance(s, dict) for s in stations):
            report.error("I3", "META['stations'] 要是字典组成的列表")
            stations = []
        if stations and not MIN_STATIONS <= len(stations) <= MAX_STATIONS:
            report.error("G5", f"一课要有 2 或 3 站，现在是 {len(stations)} 站")
        elif not stations and isinstance(meta.get("stations"), list):
            report.error("G5", "一课要有 2 或 3 站，现在一站也没有")
        seen_commands = {}
        for index, station in enumerate(stations):
            expected = "{}{}".format(lesson_id, "abcdefgh"[index]) if id_ok and index < 8 else None
            station_id = station.get("id")
            label = station_id if isinstance(station_id, str) else f"第 {index + 1} 站"
            for key in STATION_KEYS:
                if key not in station:
                    report.error("I3", f"{label} 缺少 {key!r}")
            if isinstance(station_id, str):
                station_ids.append(station_id)
            if expected and station_id != expected:
                report.error("I3", f"第 {index + 1} 站的 id 应该是 {expected}，现在是 {station_id!r}")
            if "title" in station and not _text(station.get("title")):
                report.error("I3", f"{label} 的 title 不能为空")
            minutes = station.get("minutes")
            if "minutes" in station:
                if not _is_int(minutes):
                    report.error("G5", f"{label} 的 minutes 要是整数")
                elif minutes > MAX_MINUTES:
                    report.error("G5", f"{label} 标了 {minutes} 分钟；一站最多 {MAX_MINUTES} 分钟"
                                       "（计划 G5a）。这一站要减内容：挪进「想多了解（可跳过）」框、"
                                       "挪到已经讲这个主题的后面一课，或者删掉")
                elif minutes < MIN_MINUTES:
                    report.error("G5", f"{label} 标了 {minutes} 分钟；"
                                       f"一站要在 {MIN_MINUTES} 到 {MAX_MINUTES} 分钟之间（计划 G5a）")
                elif minutes > WARN_MINUTES:
                    report.warn("G5", f"{label} 标了 {minutes} 分钟，超过 {WARN_MINUTES} 分钟"
                                      f"（目标是 {TARGET_MINUTES[0]} 到 {TARGET_MINUTES[1]} 分钟）。"
                                      "这个数必须是按计划 G5a 的算法算出来的用时；"
                                      "能挪走的内容放进「想多了解（可跳过）」框")
            concept = station.get("new_concept")
            if "new_concept" in station and not _text(concept):
                report.error("G5", f"{label} 的 new_concept 要是一个字符串：一站只引入一个新概念")
            commands = station.get("new_commands")
            if "new_commands" in station:
                if not isinstance(commands, list) or not all(_text(c) for c in commands):
                    report.error("I3", f"{label} 的 new_commands 要是字符串列表（没有就写 []）")
                else:
                    if len(commands) > MAX_COMMANDS:
                        report.error("G5", f"{label} 引入了 {len(commands)} 条新命令，"
                                           f"一站最多 {MAX_COMMANDS} 条")
                    for command in commands:
                        if command in seen_commands:
                            report.error("G5", f"命令 {command!r} 在 {seen_commands[command]} 和 {label} 都算成了新命令")
                        seen_commands[command] = label

    # rules (plan G5: at most two new rule cards)
    rules = meta.get("rules")
    if "rules" in meta:
        if not isinstance(rules, list) or not all(isinstance(r, str) for r in rules):
            report.error("I3", "META['rules'] 要是规则编号的列表（没有就写 []）")
        else:
            if len(rules) > MAX_RULES:
                report.error("G5", f"一课最多 {MAX_RULES} 张新规则卡，现在列了 {len(rules)} 张")
            if len(set(rules)) != len(rules):
                report.error("I3", "META['rules'] 里有重复的编号")
            for rule in rules:
                if not rulecards.RULE_ID.match(rule):
                    report.error("I3", f"规则编号要写成 GIT-03 这样，现在是 {rule!r}")

    # verified (plan G4)
    verified = meta.get("verified")
    if "verified" in meta:
        if not isinstance(verified, dict):
            report.error("G4", "META['verified'] 要是字典：{'date': 'YYYY-MM-DD', 'tools': {...}}")
        else:
            when = _date(verified.get("date"))
            if when is None:
                report.error("G4", "META['verified']['date'] 要写成 YYYY-MM-DD，现在是 {!r}".format(verified.get("date")))
            elif when > today:
                report.error("G4", "核实日期 {} 在今天之后".format(verified["date"]))
            tools = verified.get("tools")
            if not isinstance(tools, dict):
                report.error("G4", "META['verified']['tools'] 要是字典（工具名到版本号，没有就写 {}）")
            else:
                for name, version in tools.items():
                    if not isinstance(name, str) or not isinstance(version, str):
                        report.error("G4", f"verified.tools 的工具名和版本号都要是字符串：{({name: version})!r}")
                        continue
                    if name not in TOOL_NAMES:
                        report.warn("G4", f"verified.tools 里的工具名 {name!r} 不在约定的名单里，fresh 命令认不出它")
                    if not _VERSION.match(version):
                        report.warn("G4", f"verified.tools[{name!r}] 的版本号 {version!r} 看起来不像版本号")
    unverified = meta.get("unverified_steps")
    if "unverified_steps" in meta and (
            not isinstance(unverified, list) or not all(_text(s) for s in unverified)):
        report.error("G6", "META['unverified_steps'] 要是字符串列表（没有就写 []）")
    return station_ids


def _check_terms(report, terms, station_ids):
    if not isinstance(terms, list):
        return
    seen = set()
    for index, term in enumerate(terms):
        label = f"TERMS 第 {index + 1} 项"
        if not isinstance(term, dict):
            report.error("I3", f"{label} 要是字典")
            continue
        for key in ("term", "en", "plain", "first"):
            if key not in term:
                report.error("I3", f"{label} 缺少 {key!r}")
            elif not isinstance(term[key], str):
                report.error("I3", f"{label} 的 {key!r} 要是字符串")
        if isinstance(term.get("term"), str):
            label = "术语「{}」".format(term["term"])
            if not term["term"].strip():
                report.error("I3", f"TERMS 第 {index + 1} 项的 term 不能为空")
            if term["term"] in seen:
                report.error("I3", f"{label} 在 TERMS 里出现了两次")
            seen.add(term["term"])
        if isinstance(term.get("plain"), str) and not term["plain"].strip():
            report.error("I3", f"{label} 的 plain（大白话解释）不能为空")
        if isinstance(term.get("en"), str) and not term["en"].strip():
            report.warn("I3", f"{label} 没有写英文原词（en）")
        if isinstance(term.get("first"), str) and station_ids and term["first"] not in station_ids:
            report.error("I3", "{} 的 first={!r} 不是本课的站点编号".format(label, term["first"]))


def _check_checks(report, names, station_ids):
    checks = names.get("checks", names.get("CHECKS"))
    if not isinstance(checks, dict):
        return
    for station_id in station_ids:
        if station_id not in checks:
            report.error("I4", f"{station_id} 没有检查函数：每一站都要有一个检查")
    for key, function in checks.items():
        if station_ids and key not in station_ids:
            report.error("I4", f"checks 里的 {key!r} 不是本课的站点编号")
        if not callable(function):
            report.error("I3", f"checks[{key!r}] 不是函数")
        elif not _takes_one(function):
            report.error("I3", f"checks[{key!r}] 要能用一个参数调用：def check(ctx)")


def _check_hints(report, hints, station_ids):
    if not isinstance(hints, dict):
        return
    for station_id in station_ids:
        if station_id not in hints:
            report.error("I4", f"{station_id} 没有提示：每一站都要有四级提示")
    for key, levels in hints.items():
        if station_ids and key not in station_ids:
            report.error("I4", f"HINTS 里的 {key!r} 不是本课的站点编号")
        if not isinstance(levels, (list, tuple)) or len(levels) != 4:
            count = len(levels) if isinstance(levels, (list, tuple)) else 0
            report.error("I4", f"HINTS[{key!r}] 要正好四条（方向、位置、相似例子、答案与解释），现在是 {count} 条")
        elif not all(_text(level) for level in levels):
            report.error("I4", f"HINTS[{key!r}] 的四条提示都要是非空字符串")
        elif len({level.strip() for level in levels}) != 4:
            report.error("I4", f"HINTS[{key!r}] 的四条提示里有重复的内容")


def _check_scenarios(report, scenarios, lesson_id):
    """Check SCENARIOS; returns the set of usable keys."""
    if not isinstance(scenarios, dict):
        return set()
    if "start" not in scenarios:
        report.error("I3", "SCENARIOS 里必须有 'start'：学这一课之前的起点状态")
    pattern = re.compile(rf"^{re.escape(lesson_id)}[a-z]?(-[a-z0-9]+)*$") if lesson_id else None
    keys = set()
    for key, builder in scenarios.items():
        if not isinstance(key, str):
            report.error("I3", f"SCENARIOS 的键要是字符串：{key!r}")
            continue
        keys.add(key)
        if key != "start":
            reserved = lesson_id and key in (lesson_id, lesson_id + "-start")
            if reserved or (pattern is not None and not pattern.match(key)):
                report.error("I3", f"场景名 {key!r} 不合规：除了 'start'，要以本课的站点编号开头，"
                                   f"例如 {lesson_id}a 或 {lesson_id}a-broken")
        if not callable(builder):
            report.error("I3", f"SCENARIOS[{key!r}] 不是函数")
        elif not _takes_one(builder):
            report.error("I3", f"SCENARIOS[{key!r}] 要能用一个参数调用：def build(sc)")
    return keys


def _check_choice(report, label, item):
    options = item.get("options")
    if not isinstance(options, list) or not 2 <= len(options) <= 6 or not all(_text(o) for o in options):
        report.error("I3", f"{label} 的 options 要是 2 到 6 个非空字符串")
        return
    if len({o.strip() for o in options}) != len(options):
        report.error("I3", f"{label} 的 options 里有重复的选项")
    index = letter_to_index(item.get("answer"))
    if index is None or index >= len(options):
        report.error("I3", "{} 的 answer 要是正确选项的字母（A 到 {}），现在是 {!r}".format(label, "ABCDEF"[len(options) - 1], item.get("answer")))
    if "a" in item:
        report.error("I3", f"{label} 是选择题，不要再写 a；解释请写在 explain 里")


def _check_review(report, review, lesson_id, station_ids, scenario_keys, meta):
    """Check REVIEW; returns the set of item ids."""
    ids = set()
    if not isinstance(review, list):
        return ids
    id_pattern = re.compile(rf"^{re.escape(lesson_id)}-[a-z0-9]+(-[a-z0-9]+)*$") if lesson_id else None
    fluent = 0
    for index, item in enumerate(review):
        label = f"REVIEW 第 {index + 1} 项"
        if not isinstance(item, dict):
            report.error("I3", f"{label} 要是字典")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or (id_pattern is not None and not id_pattern.match(item_id)):
            report.error("I3", "{} 的 id 要以课程编号加短横线开头，例如 {}-r1，现在是 {!r}".format(label, lesson_id or "1.6", item_id))
        else:
            label = f"复习题 {item_id}"
            if item_id in ids:
                report.error("I3", f"{label} 的 id 重复了")
            ids.add(item_id)
        kind = item.get("type")
        if kind not in REVIEW_TYPES:
            report.error("I3", "{} 的 type 要是 {} 之一，现在是 {!r}".format(label, " / ".join(REVIEW_TYPES), kind))
        tier = item.get("tier")
        if tier not in TIERS:
            report.error("I3", "{} 的 tier 要是 {} 之一，现在是 {!r}".format(label, " / ".join(TIERS), tier))
        elif tier == "fluent":
            fluent += 1
        if not _text(item.get("q")):
            report.error("I3", f"{label} 缺少题目 q")
        if kind == "recall":
            if not _text(item.get("a")):
                report.error("I3", f"{label} 是 recall 题，要有参考答案 a")
            if "options" in item or "answer" in item:
                report.error("I3", f"{label} 是 recall 题，不要写 options 和 answer")
        elif kind in CHOICE_TYPES:
            _check_choice(report, label, item)
        elif kind == "do":
            if item.get("scenario") not in scenario_keys:
                report.error("I3", "{} 是 do 题，scenario 要是本课 SCENARIOS 里的一个键，现在是 {!r}".format(label, item.get("scenario")))
            if not callable(item.get("check")):
                report.error("I3", f"{label} 是 do 题，要有检查函数 check")
            elif not _takes_one(item["check"]):
                report.error("I3", f"{label} 的 check 要能用一个参数调用：def check(ctx)")
        if "station" in item and station_ids and item["station"] not in station_ids:
            report.error("I3", "{} 的 station={!r} 不是本课的站点编号".format(label, item["station"]))
        if "rule" in item:
            rules = meta.get("rules") if isinstance(meta.get("rules"), list) else []
            if not isinstance(item["rule"], str) or not rulecards.RULE_ID.match(item["rule"]):
                report.error("I3", "{} 的 rule 要是规则编号，现在是 {!r}".format(label, item["rule"]))
            elif item["rule"] not in rules:
                report.warn("I3", "{} 指向的规则 {} 不是本课引入的规则".format(label, item["rule"]))
        if "explain" in item and not isinstance(item["explain"], str):
            report.error("I3", f"{label} 的 explain 要是字符串")
        if "shuffle" in item and not isinstance(item["shuffle"], bool):
            report.error("I3", f"{label} 的 shuffle 要是 True 或 False")
    if not review:
        report.warn("I3", "REVIEW 是空的：这一课没有任何复习题")
    elif not fluent:
        report.warn("I3", "REVIEW 里没有 tier 为 fluent 的题：这一课不会进入间隔复习")
    return ids


def _check_exam(report, exam, lesson_id, review_ids):
    if not isinstance(exam, list):
        return
    id_pattern = re.compile(rf"^{re.escape(lesson_id)}-[a-z0-9]+(-[a-z0-9]+)*$") if lesson_id else None
    seen = set()
    for index, task in enumerate(exam):
        label = f"EXAM 第 {index + 1} 项"
        if not isinstance(task, dict):
            report.error("I3", f"{label} 要是字典")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or (id_pattern is not None and not id_pattern.match(task_id)):
            report.error("I3", "{} 的 id 要以课程编号加短横线开头，例如 {}-x1，现在是 {!r}".format(label, lesson_id or "1.6", task_id))
        else:
            label = f"考题 {task_id}"
            if task_id in seen or task_id in review_ids:
                report.error("I3", f"{label} 的 id 和别的考题或复习题重复了")
            seen.add(task_id)
        gate = task.get("gate")
        if not isinstance(gate, str) or not _GATE.match(gate):
            report.error("I3", f"{label} 的 gate 要写成 gate-b 这样，现在是 {gate!r}")
        if not _text(task.get("title")):
            report.error("I3", f"{label} 缺少 title（成绩表里显示的短名字）")
        minutes = task.get("minutes")
        if not _is_int(minutes) or not 1 <= minutes <= 15:
            report.error("I3", f"{label} 的 minutes 要是 1 到 15 之间的整数，现在是 {minutes!r}")
        for key, usage in (("build", "def build(sc)"), ("grade", "def grade(ctx)")):
            if not callable(task.get(key)):
                report.error("I3", f"{label} 缺少函数 {key}")
            elif not _takes_one(task[key]):
                report.error("I3", f"{label} 的 {key} 要能用一个参数调用：{usage}")
        text = task.get("task")
        if not isinstance(text, dict) or set(text) != {"A", "B"} or not all(_text(v) for v in text.values()):
            report.error("I3", f"{label} 的 task 要是 {{'A': 题面, 'B': 题面}}：两套平行的题面")
        elif text["A"].strip() == text["B"].strip():
            report.error("I3", f"{label} 的 A、B 两套题面一模一样；平行题要表面不同、考的东西相同")


def _check_rule_cards(report, lesson, meta, today):
    rules = [r for r in meta.get("rules", []) if isinstance(r, str)] \
        if isinstance(meta.get("rules"), list) else []
    path = lesson.rules_path
    if not path.is_file():
        if rules:
            report.error("I2", "META['rules'] 列了 {}，但课程文件夹里没有 rules.md".format("、".join(rules)))
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.error("I2", f"rules.md 读不出来（{type(exc).__name__}）")
        return
    cards = rulecards.parse_cards(text)
    by_id = {}
    for card in cards:
        if card.id in by_id:
            report.error("I2", f"rules.md 里 {card.id} 有两张卡")
        by_id[card.id] = card
    if len(cards) > MAX_RULES:
        report.error("G5", f"rules.md 里有 {len(cards)} 张规则卡，一课最多 {MAX_RULES} 张")
    for rule in rules:
        if rule not in by_id:
            report.error("I2", f"rules.md 里没有 {rule} 的卡片（标题要写成：### {rule} 规则名）")
    lesson_id = meta.get("id") if isinstance(meta.get("id"), str) else ""
    for card in cards:
        label = f"规则卡 {card.id}（rules.md 第 {card.line} 行）"
        if card.id not in rules:
            report.error("I2", f"{label} 没有列在 META['rules'] 里")
        for problem in rulecards.check_card(card, lesson_id, today):
            report.error("I2", f"{label}：{problem}")
        for problem in rulecards.binding_problems(card):
            report.warn("I2", f"{label}：{problem}")
        old = card.get("旧教程提醒")
        if old and not old.startswith("无") and not _since_when(old):
            report.warn("G4", f"{label}的旧教程提醒没写从什么时候起：要写上年份、版本号或日期，"
                              f"例如「（自 Git 2.23 起）」。现在是「{_short(old, 60)}」")
    for number, line in enumerate(text.splitlines(), 1):
        for problem in _path_problems(line, lesson_id):
            report.warn("G10", f"rules.md 的第 {number} 行{problem}")


def _check_syllabus(report, lesson, meta, names):
    entry = lesson_entry(meta.get("id")) if isinstance(meta.get("id"), str) else None
    if entry is None:
        return
    if lesson.folder.name != entry["folder"] or lesson.folder.parent.name != entry["stage_folder"]:
        report.error("§4", "大纲规定 {} 课的位置是 stages/{}/{}，现在在 {}".format(entry["id"], entry["stage_folder"], entry["folder"], lesson.rel))
    stations = [s.get("id") for s in meta.get("stations", []) if isinstance(s, dict)] \
        if isinstance(meta.get("stations"), list) else []
    if stations and stations != entry["stations"]:
        report.error("§4", "大纲规定 {} 课的站点是 {}，现在是 {}".format(entry["id"], " ".join(entry["stations"]), " ".join(str(s) for s in stations)))
    rules = meta.get("rules")
    if isinstance(rules, list) and {r for r in rules if isinstance(r, str)} != set(entry["rules"]):
        wanted = "、".join(sorted(entry["rules"])) or "（没有新规则）"
        report.error("§4", "大纲规定 {} 课的新规则是 {}，META['rules'] 现在是 {}".format(entry["id"], wanted, "、".join(str(r) for r in rules) or "（空）"))
    if _text(meta.get("title")) and meta["title"].strip() != entry["title"]:
        report.warn("§4", "课程标题和大纲不一样：大纲是「{}」，META 是「{}」".format(entry["title"], meta["title"]))
    exam = names.get("EXAM")
    for task in exam if isinstance(exam, list) else []:
        if isinstance(task, dict) and isinstance(task.get("gate"), str) and task["gate"] != entry["gate"]:
            report.error("§4", "考题 {} 的 gate 应该是 {}（大纲规定 {} 课归这个关卡），现在是 {}".format(task.get("id"), entry["gate"], entry["id"], task["gate"]))
    if lesson.rules_path.is_file():
        try:
            cards = rulecards.parse_cards(lesson.rules_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            cards = []
        for card in cards:
            expected = entry["rules"].get(card.id, {})
            family, kind = expected.get("kind"), card.kind
            if family and kind in rulecards.TYPES and not rulecards.family_allows(family, kind):
                report.warn("§4", f"规则卡 {card.id} 的规则类型是「{kind}」，大纲在括号里写的是「{family}」。"
                                  "如果按出处判断确实不是这一类，保留你的判断，并在报告里说明")
            level = card.level
            if expected.get("level") and level and level != expected["level"]:
                report.warn("§4", "规则卡 {} 的约束力是「{}」，大纲里写的是「{}」".format(
                    card.id, level, expected["level"]))


def _check_text(report, lesson, station_ids, complete):
    lesson_id = lesson.meta.get("id") if isinstance(lesson.meta.get("id"), str) else ""
    _check_module_texts(report, lesson, lesson_id)
    path = lesson.text_path
    if not path.is_file():
        if complete:
            report.error("I1", "没有课文 lesson.md")
        else:
            report.warn("I1", "还没有课文 lesson.md")
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.error("I1", f"lesson.md 读不出来（{type(exc).__name__}）")
        return
    first = text.lstrip().splitlines()[0] if text.strip() else ""
    if lesson_id and not first.startswith(f"# {lesson_id} "):
        report.warn("I1", f"lesson.md 的第一行应该是「# {lesson_id} 课程标题」")
    doc = Doc(text)
    if not doc.station_headings():
        # Without station headings the station-by-station forms cannot be
        # read; fall back to "does the text mention it at all".
        for station_id in station_ids:
            if f"存档点 {station_id}" not in text:
                report.warn("I1", f"lesson.md 里没有「存档点 {station_id}」")
            if f"check {station_id}" not in text:
                report.warn("I1", f"lesson.md 里没有出现检查命令 check {station_id}")
            if f"hint {station_id}" not in text:
                report.warn("I1", f"lesson.md 里没有出现提示命令 hint {station_id}")
    _check_heading_minutes(report, lesson, text)
    check_lesson_forms(report, doc, lesson_id, station_ids, lesson.meta,
                       _cards_of(lesson))


def _check_heading_minutes(report, lesson, text):
    """Warn when 「## 第 N 站：……（约 X 分钟）」 disagrees with META (plan G5a)."""
    stations = lesson.meta.get("stations")
    if not isinstance(stations, list):
        return
    for number, line in enumerate(text.splitlines(), 1):
        heading = _STATION_HEADING.match(line.strip())
        if not heading:
            continue
        digits = heading.group(1)
        position = int(digits) if digits.isdigit() else _CN_SMALL.get(digits, 0)
        bracket = _HEADING_BRACKET.search(heading.group(2))
        stated = _HEADING_MINUTES.search(bracket.group(1)) if bracket else None
        if not stated or not 1 <= position <= len(stations):
            continue
        station = stations[position - 1]
        if not isinstance(station, dict) or not _is_int(station.get("minutes")):
            continue
        if int(stated.group(1)) != station["minutes"]:
            report.warn("G5", "lesson.md 第 {} 行写的是第 {} 站约 {} 分钟，META 里 {} 是 {} 分钟："
                              "两处要写同一个按计划 G5a 算出来的数".format(
                                  number, position, stated.group(1),
                                  station.get("id", f"第 {position} 站"), station["minutes"]))


# ---------------------------------------------------------------------------
# The fixed forms of lesson.md (the one wording of the recurring parts:
# plan I1, I2, G2, G4, G5a, G6, G10).  Every finding here is a warning, names
# the line, quotes what it found and says what the form should be.  When the
# text is ambiguous the checks stay silent.
# ---------------------------------------------------------------------------
#: Gates that sit inside a station instead of after a lesson (plan I7):
#: their lesson's closing line names the next lesson, not the gate.
GATES_INSIDE = {"gate-0": "0.4c", "gate-1": "1.16b"}
#: The four parts of a station (plan I1), in this order.
PARTS = ("概念", "跟我做", "补全", "自己做")
MARKS = ("〔对照文档，界面可能不同〕", "〔建课时无法验证〕")
G6_LINE = "和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。"
SAVE_LINE = "> **存档点 {station}**：到这里可以安全停下。下次可以对导师说“{target}”。"
MID_LINE = "> **中途存档点**：<做完了什么>，到这里可以安全停下。下次可以对导师说“做小关卡 {gate}”。"
HINT_LINE = "- 提示：`python3 tools/course.py hint {station}`（每运行一次多给一级）"
CHECK_LINE = "- 检查（先回到学习工作区）：`python3 tools/course.py check {station}`"
CLOSING_HEADING = "## 收尾（约 {minutes} 分钟）"
CLOSING_CHECK = "全课检查（在学习工作区里运行）：`python3 tools/course.py check {lesson}`"
CLOSING_NOTES = ("行规笔记：运行 `code notes/my-rules.md`，在小标题{headings}下面{each}用自己的话"
                 "写一两句，再配一个你自己的例子，写完按 ⌘S 保存。")
CLOSING_JOURNAL = "一句话日志：`python3 tools/course.py journal`"
CLOSING_BACKUP = "备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。"
#: The lesson that defines the backup step; it and every later lesson have one.
BACKUP_FROM = "1.12"
CLOSING_END = "都做完，这一课就完成了。下次可以对导师说“从 {lesson} 开始”。"
CLOSING_END_GATE = ("都做完，这一课就完成了。下一步是小关卡 {gate}：它是单独的一段时间，"
                    "开考时工具会打印题数和预计用时。下次可以对导师说“做小关卡 {gate}”。")
CLOSING_END_STAGE = "下次可以对导师说“准备阶段 {stage}”。"
SUMMARY_COLUMNS = ("编号", "规则", "约束力", "规则类型", "谁说的", "核对日期")
SUMMARY_SENTENCE = "完整卡片在本课文件夹的 `rules.md`。"
OPTIONAL_LABEL = "想多了解（可跳过）"
OPTIONAL_WORDS = ("选做", "选读", "可选", "可以跳过")
#: One of OPTIONAL_WORDS used as a label in a heading: 「### 选做：……」「### ……（可选）」,
#: at the end (「这一段可选」), after a comma (「进阶，可选」), or before 的 + the
#: material (「可选的进阶」「补充（可以跳过的部分）」); not a word inside a sentence
#: (「自己做（可选的两种做法都行）」).
_OPTIONAL_IN_HEADING = re.compile(
    r"(?:^|[（(【\[\s·—\-，,、])(?:选做|选读|可选|可以跳过)"
    r"(?:$|[）)】\]：:，,\s]|练习|题|部分|内容|阅读|材料)"
    r"|(?:选做|选读|可选|可以跳过)\s*[）)】\]]?\s*$"
    r"|(?:选做|选读|可选|可以跳过)的(?:进阶|部分|内容|阅读|材料|练习|题)")
#: From this lesson on, a bare 工作区 is Git's working tree (plan section 5a).
WORKING_TREE_FROM = "1.6"
#: From this lesson on the 学习工作区 is a Git repository (学习仓库).
REPO_FROM = "1.12"
#: The sentences a learner says to the tutor (fixed wording of the course).
TUTOR_SENTENCES = (
    r"开始上课", r"从 \d+\.\d+[a-z] 继续", r"从 \d+\.\d+ 的收尾继续", r"从 \d+\.\d+ 开始",
    r"做小关卡 gate-[a-z0-9]+", r"请问我 gate-[a-z0-9]+ 的讲解题", r"急救：\S.*", r"干活：\S.*",
    r"回到上课", r"课文对不上", r"我们来做入学问卷", r"帮我把课程安置到 ~/Developer",
    r"我先不搬，帮我在 ~/Developer 建一个入口", r"我回来了，带我走回归流程",
    r"请解释这条命令的每一部分，先不要运行", r"准备阶段 \d+",
)
_TUTOR_FORMS = [re.compile(pattern) for pattern in TUTOR_SENTENCES]
#: A quoted sentence with one of these words is about going on or getting help.
_RESUME_WORDS = ("继续", "开始", "收尾", "急救", "干活", "关卡", "讲解", "讲给", "上课", "对不上",
                 "阶段", "回来", "回归")
#: Only the learner speaking counts: 「对导师说」「跟导师说」「向导师说」「和导师说」,
#: also 「导师改完以后，对它说……」; not the tutor's own words (「导师说……」「导师会对你说……」).
_TUTOR_SAY = re.compile(r"(?:(?:对|跟|向|和)导师|导师[^。！？\n“”\"「」]{0,12}?(?:对|跟|向|和)[它他她])"
                        r"[^。！？\n“”\"「」]{0,8}?说[：:]?\s*"
                        r"(?:“([^”\n]+)”|\"([^\"\n]+)\"|「([^」\n]+)」)")
#: Terms and commands whose owner lesson the course decided (the term and
#: command ledger of 2026-11-19): only the owner lists them as first or new.
TERM_OWNERS = {"路径": "0.2", "递归": "1.2", "令牌": "1.9", "提交签名": "1.6", "分支": "1.6",
               "讲解题": "0.4"}
COMMAND_OWNERS = {
    "python3 tools/course.py scenario": "0.1",
    "git --version": "1.6",
    "git commit -m … -m …": "1.10",
    "mkdir": "0.2",
    "git config get": "1.6",
    "git diff <文件名>": "1.7",
    "git log -1": "1.11",
    "python3 tools/course.py exam gate-…": "0.4",
    "python3 tools/course.py exam gate-… --grade": "0.4",
}
GIT_CONFIG_SUBCOMMANDS = ("set", "get", "unset", "list", "edit", "rename-section",
                          "remove-section", "get-color", "get-colorbool")

_FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*([A-Za-z0-9_+.-]*)")
_HEADING_LINE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t#]*$")
_CJK = re.compile(r"[㐀-鿿]")
_INLINE_CODE = re.compile(r"(`+)(.+?)\1")
_USERS_PATH = re.compile(r"/Users/([^/\s`'\"）)，。、]*)")
_YEAR_OR_VERSION = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)|\d+\.\d+|\bv\d+|第\s*\d+\s*版")
#: A named release also says since when: 「从 macOS Catalina 起」「Python 3 以后」,
#: also without spaces next to Chinese (「从macOS Catalina起」「从Python 3起」:
#: \b does not match between a Chinese character and a Latin letter, so the
#: edges are lookarounds).  A digit followed by a measure word is a count,
#: not a version: 「Git 2 种写法」.
_NAMED_RELEASE = re.compile(
    r"(?<![A-Za-z])(?:Mojave|Catalina|Big Sur|Monterey|Ventura|Sonoma|Sequoia|Tahoe)(?![A-Za-z])"
    r"|(?<![A-Za-z])(?:macOS|OS X|iOS|Python|Git|Node(?:\.js)?|Xcode|zsh|bash|Ruby|Java)\s*\d+"
    r"(?!\d)(?!\s*[个条种次行站课题项份步类处位张件块段句篇道组遍])")
_LESSON_REF = re.compile(r"第\s*\d+\.\d+\s*课|\d+\.\d+[a-z]?\s*课|\d+\.\d+[a-z](?![a-z0-9])")
_CHECKED = re.compile(r"\d{4}-\d{2}-\d{2}\s*核对|核对(?:日期)?[：:\s]*\d{4}-\d{2}-\d{2}")
_GIT_CONFIG = re.compile(r"git config(?:[ \t]+(\S+))?")
_HEADER = re.compile(r"\*\*用时\*\*\s*(\d+)\s*站\s*[，,]\s*约\s*(\d+)\s*分钟")
_CLOSING = re.compile(r"^##[ \t]+收尾")
_CLOSING_EXACT = re.compile(r"^## 收尾（约 (\d+) 分钟）$")
_STEP = re.compile(r"^(\d+)[.、]\s*(.*)$")
_LEVEL_WORD = re.compile(r"必须|推荐|参考")


def _short(text, width=70):
    text = text.strip()
    return text if len(text) <= width else text[:width - 1] + "…"


def _squash(text):
    """``text`` without white space and punctuation, for comparing table cells."""
    import unicodedata
    return "".join(ch for ch in text if not ch.isspace()
                   and unicodedata.category(ch)[0] not in "PSZ")


class Doc:
    """A lesson.md split into lines, with fenced code blocks and headings known."""

    def __init__(self, text):
        self.lines = text.splitlines()
        count = len(self.lines)
        self.code = [False] * count
        self.lang = [""] * count
        #: Number of the fenced block a line belongs to (-1 outside code).
        self.block = [-1] * count
        self.headings = []
        fence, lang, blocks = "", "", 0
        for index, line in enumerate(self.lines):
            match = _FENCE.match(line)
            if fence:
                self.code[index] = True
                self.lang[index] = lang
                self.block[index] = blocks
                stripped = line.strip()
                if stripped and set(stripped) == {fence[0]} and len(stripped) >= len(fence):
                    fence = ""
                continue
            if match:
                fence, lang = match.group(1), match.group(2).lower()
                blocks += 1
                self.code[index] = True
                self.lang[index] = lang
                self.block[index] = blocks
                continue
            heading = _HEADING_LINE.match(line)
            if heading:
                self.headings.append((index, len(heading.group(1)), heading.group(2).strip()))

    def section_end(self, index, level):
        """Index after the section whose heading is at ``index``."""
        for other, other_level, _title in self.headings:
            if other > index and other_level <= level:
                return other
        return len(self.lines)

    def station_headings(self):
        """``[(position, heading index, end index)]`` for 「## 第 N 站：……」."""
        found = []
        for index, level, _title in self.headings:
            if level != 2:
                continue
            match = _STATION_HEADING.match(self.lines[index].strip())
            if not match:
                continue
            digits = match.group(1)
            position = int(digits) if digits.isdigit() else _CN_SMALL.get(digits, 0)
            found.append((position, index, self.section_end(index, 2)))
        return found

    def section(self, test):
        """``(start, end)`` of the first level-2 section whose title passes ``test``."""
        for index, level, title in self.headings:
            if level == 2 and test(title):
                return index, self.section_end(index, 2)
        return None

    def quote_block(self, index):
        """``(first, last)`` of the blockquote that contains line ``index``."""
        first = last = index
        while first > 0 and not self.code[first - 1] and self.lines[first - 1].lstrip().startswith(">"):
            first -= 1
        while (last + 1 < len(self.lines) and not self.code[last + 1]
               and self.lines[last + 1].lstrip().startswith(">")):
            last += 1
        return first, last

    def quoted(self, index):
        return not self.code[index] and self.lines[index].lstrip().startswith(">")


def _where(index):
    return f"lesson.md 的第 {index + 1} 行"


def _label_of_quote(line):
    """The bold label at the start of a blockquote line plus a bracket after it."""
    match = re.match(r"^\s*>\s*(?:[-*]\s+)?\*\*([^*]+)\*\*\s*([（(][^）)]*[）)])?", line)
    if not match:
        return ""
    return match.group(1).strip() + (match.group(2) or "")


def _optional_box(doc, index):
    return doc.quoted(index) and _label_of_quote(doc.lines[index]).startswith(OPTIONAL_LABEL)


def check_lesson_forms(report, doc, lesson_id, station_ids, meta, cards):
    """The checks of the recurring parts of lesson.md (all warnings)."""
    stations = meta.get("stations") if isinstance(meta.get("stations"), list) else []
    rules = [r for r in meta.get("rules", []) if isinstance(r, str)] \
        if isinstance(meta.get("rules"), list) else []
    entry = lesson_entry(lesson_id) if lesson_id else None
    seen = set()
    _check_header(report, doc, stations)
    _check_stations(report, doc, lesson_id, station_ids, entry, seen)
    _check_closing(report, doc, lesson_id, rules, cards, entry)
    _check_marks(report, doc, meta, seen)
    _check_tutor_sentences_md(report, doc, seen)
    _check_ascii_quotes(report, doc, seen)
    _check_course_folder_md(report, doc, lesson_id)
    _check_optional_labels(report, doc)
    _check_rule_summary(report, doc, rules, cards)
    _check_old_tutorial_boxes(report, doc)
    _check_git_config_md(report, doc)


# -- V12 the header line ------------------------------------------------------
def _check_header(report, doc, stations):
    closing = doc.section(lambda title: title.startswith("收尾"))
    closing_minutes = None
    if closing:
        # 「## 收尾（5 分钟）」 still says 5 minutes; its missing 约 is V2's finding.
        match = re.search(r"(\d+)\s*分钟", doc.lines[closing[0]])
        closing_minutes = int(match.group(1)) if match else None
    for index, line in enumerate(doc.lines[:15]):
        if "**用时**" not in line:
            continue
        match = _HEADER.search(line)
        if not match:
            report.warn("G5", f"{_where(index)}的用时写法要是「**用时** N 站，约 X 分钟」，现在是「{_short(line)}」")
            return
        count, total = int(match.group(1)), int(match.group(2))
        minutes = [s.get("minutes") for s in stations if isinstance(s, dict)]
        if count != len(stations):
            report.warn("G5", f"{_where(index)}写的是 {count} 站，META 里有 {len(stations)} 站")
        if closing_minutes is not None and minutes and all(_is_int(m) for m in minutes):
            wanted = sum(minutes) + closing_minutes
            if total != wanted:
                report.warn("G5", "{}写的是约 {} 分钟；各站加收尾是 {} 分钟（{} + 收尾 {}）："
                                  "开头的总时间要写这个和".format(
                                      _where(index), total, wanted,
                                      " + ".join(str(m) for m in minutes), closing_minutes))
        return
    report.warn("G5", "lesson.md 开头没有用时这一行：要写「> **用时** N 站，约 X 分钟 ｜ ……」，"
                      "X 是各站分钟数加收尾的分钟数")


# -- V1 save points and V3 the parts of a station -----------------------------
def _resume_problems(line, prefix, target):
    """What differs between a save-point line and the fixed form."""
    problems = []
    if '"' in line:
        problems.append("引号用了英文的直引号 \"，要用中文的 “ ”")
    said = re.search(r"说[：:]?\s*[“\"「]([^”\"」]*)[”\"」]", line)
    if not line.startswith(prefix):
        problems.append(f"开头要是「{prefix}」")
    if not said:
        problems.append(f"没有写下次对导师说什么（要说“{target}”）")
        return problems
    if said.group(1).strip() != target:
        problems.append(f"说的话应该是“{target}”，现在是“{said.group(1).strip()}”")
    before = line[len(prefix):said.start()] if line.startswith(prefix) else ""
    if line.startswith(prefix) and before != "下次可以对导师":
        extra = before.replace("下次可以对导师", "").replace("下次对导师", "")
        if extra.strip():
            problems.append(f"中间多了「{_short(extra, 40)}」")
        elif before == "下次对导师":
            problems.append("少了「可以」：要写「下次可以对导师说」")
    tail = line[said.end():]
    if tail != "。":
        extra = tail.removeprefix("。")
        if extra.strip():
            problems.append(f"句子后面多了「{_short(extra, 40)}」：这一行只写规定的那句话")
    return problems


def _check_save_line(report, doc, index, station, target):
    line = doc.lines[index].rstrip()
    expected = SAVE_LINE.format(station=station, target=target)
    if line == expected:
        return
    prefix = f"> **存档点 {station}**：到这里可以安全停下。"
    problems = _resume_problems(line, prefix, target) or ["写法和规定的不一样"]
    report.warn("I1", "{}的存档点写法不对（{}）：现在是「{}」；要写成「{}」".format(
        _where(index), "；".join(problems), _short(line, 90), expected))


def _check_mid_line(report, doc, index, gate):
    line = doc.lines[index].rstrip()
    match = re.match(r"^> \*\*中途存档点\*\*：(.+?)，到这里可以安全停下。"
                     r"下次可以对导师说“做小关卡 (gate-[a-z0-9]+)”。$", line)
    if match and (not gate or match.group(2) == gate):
        return
    target = f"做小关卡 {gate}" if gate else "做小关卡 <关卡>"
    prefix = "> **中途存档点**："
    problems = []
    if '"' in line:
        problems.append("引号用了英文的直引号 \"，要用中文的 “ ”")
    said = re.search(r"说[：:]?\s*[“\"「]([^”\"」]*)[”\"」]", line)
    if said and said.group(1).strip() != target:
        problems.append(f"说的话应该是“{target}”，现在是“{said.group(1).strip()}”")
    if "，到这里可以安全停下。" not in line or "下次可以对导师说" not in line or not line.startswith(prefix):
        problems.append("固定的部分不全")
    report.warn("I1", "{}的中途存档点写法不对（{}）：现在是「{}」；要写成「{}」".format(
        _where(index), "；".join(problems or ["写法和规定的不一样"]), _short(line, 90),
        MID_LINE.format(gate=gate or "<关卡>")))


def _check_stations(report, doc, lesson_id, station_ids, entry, seen):
    headings = doc.station_headings()
    if not headings or not station_ids:
        return
    gate = entry["gate"] if entry else ""
    for position, start, end in headings:
        if not 1 <= position <= len(station_ids):
            continue
        station = station_ids[position - 1]
        last = position == len(station_ids)
        target = f"从 {lesson_id} 的收尾继续" if last else f"从 {station_ids[position]} 继续"
        save_lines = [i for i in range(start, end) if not doc.code[i]
                      and doc.lines[i].lstrip().startswith("> **存档点")]
        mid_lines = [i for i in range(start, end) if not doc.code[i]
                     and doc.lines[i].lstrip().startswith("> **中途存档点")]
        for index in mid_lines:
            seen.add(index)
            _check_mid_line(report, doc, index, gate)
        own = [i for i in save_lines if re.match(rf"^\s*> \*\*存档点 {re.escape(station)}\*\*", doc.lines[i])]
        for index in save_lines:
            seen.add(index)
        if own:
            _check_save_line(report, doc, own[-1], station, target)
        elif save_lines:
            report.warn("I1", f"{_where(save_lines[-1])}的存档点写的不是这一站的编号（第 {position} 站是 {station}）：现在是「{_short(doc.lines[save_lines[-1]], 90)}」；要写成「{SAVE_LINE.format(station=station, target=target)}」")
        else:
            report.warn("I1", f"第 {position} 站（{station}，{_where(start)}起）的末尾没有存档点。要写成「{SAVE_LINE.format(station=station, target=target)}」")
        _check_parts(report, doc, position, station, start, end,
                     save_lines[-1] if save_lines else None, bool(mid_lines))


def _check_parts(report, doc, position, station, start, end, save_index, has_mid):
    label = f"第 {position} 站（{station}）"
    parts = []
    after_own = []
    for index, level, title in doc.headings:
        if not start < index < end or level != 3:
            continue
        word = next((p for p in PARTS if title.startswith(p)), None)
        if word:
            parts.append((word, index))
        elif parts and parts[-1][0] == "自己做":
            after_own.append((index, title))
    names = [word for word, _index in parts]
    missing = [p for p in PARTS if p not in names]
    if missing:
        report.warn("I1", "{}缺少「{}」：每一站按「概念、跟我做、补全、自己做」四部分写，"
                          "每部分一个三级标题，例如「### {}」（这一站从{}开始）".format(
                              label, "」「".join("### " + p for p in missing), missing[0], _where(start)))
    present = [p for p in PARTS if p in names]
    first_seen = []
    for name in names:
        if name not in first_seen:
            first_seen.append(name)
    if first_seen != present:
        report.warn("I1", "{}的几部分顺序是「{}」，要按「概念、跟我做、补全、自己做」".format(
            label, "、".join(first_seen)))
    if after_own and not has_mid:
        index, title = after_own[0]
        report.warn("I1", "{}在「自己做」后面还有「### {}」（{}）：「自己做」是一站的最后一部分；"
                          "关卡这样单独的一段，前面先放一行中途存档点「{}」".format(
                              label, title, _where(index), MID_LINE.format(gate="<关卡>")))
    own = [index for word, index in parts if word == "自己做"]
    if not own:
        return
    stop = save_index if save_index is not None and save_index > own[-1] else end
    content = [i for i in range(own[-1] + 1, stop) if doc.lines[i].strip()]
    while content and doc.quoted(content[-1]):
        first, _last = doc.quote_block(content[-1])
        if not _optional_box(doc, first):
            break
        content = [i for i in content if i < first]
    hint, check = HINT_LINE.format(station=station), CHECK_LINE.format(station=station)
    tail = [doc.lines[i].strip() for i in content[-2:]]
    if tail == [hint, check]:
        return
    shown = "、".join(f"{_where(i)}「{_short(doc.lines[i], 60)}」" for i in content[-2:]) or "（空）"
    report.warn("I1", f"{label}的「自己做」要以这两行结尾：「{hint}」「{check}」（中间和后面不放别的内容；"
                      f"「想多了解（可跳过）」框可以放在它们后面）。现在最后两行是 {shown}")


# -- V2 the closing section ---------------------------------------------------
def _closing_end(lesson_id, entry):
    """``(kind, expected line)`` for the last line of 收尾, or None outside the syllabus."""
    if entry is None:
        return None
    for gate_id, gate in GATES.items():
        if gate.get("after") == lesson_id and gate_id not in GATES_INSIDE:
            return "gate", CLOSING_END_GATE.format(gate=gate_id)
    ids = [row["id"] for row in LESSONS]
    position = ids.index(lesson_id) if lesson_id in ids else -1
    if 0 <= position < len(ids) - 1:
        return "lesson", CLOSING_END.format(lesson=ids[position + 1])
    return "stage", CLOSING_END_STAGE.format(stage=entry["stage"] + 1)


def _notes_line(rules, cards):
    titles = {card.id: card.title for card in cards}
    headings = "".join("「{} {}」".format(rule, titles.get(rule, "……")) for rule in rules)
    return CLOSING_NOTES.format(headings=headings, each="各" if len(rules) > 1 else "")


def _step_kind(text):
    """The kind of a closing step from ``text``: check, notes, backup, journal or ""."""
    if "全课检查" in text or re.search(r"course\.py check \d", text):
        return "check"
    if "my-rules.md" in text or text.startswith("行规笔记"):
        return "notes"
    if "备份" in text or "推送" in text or "git push" in text:
        return "backup"
    if "course.py journal" in text or "日志" in text:
        return "journal"
    return ""


def _check_closing(report, doc, lesson_id, rules, cards, entry):
    found = doc.section(lambda title: title.startswith("收尾"))
    if not found:
        if lesson_id:
            report.warn("I1", f"lesson.md 里没有收尾这一节：要写「{CLOSING_HEADING.format(minutes=5)}」，下面是全课检查、行规笔记、"
                              "一句话日志这几步")
        return
    start, end = found
    heading = doc.lines[start].strip()
    if not _CLOSING_EXACT.match(heading):
        minutes = _HEADING_MINUTES.search(heading) or re.search(r"(\d+)\s*分钟", heading)
        report.warn("I1", "{}的收尾标题要写成「{}」，现在是「{}」".format(
            _where(start), CLOSING_HEADING.format(minutes=minutes.group(1) if minutes else "N"), heading))
    steps, open_step = [], False
    for index in range(start + 1, end):
        line = doc.lines[index]
        match = None if doc.code[index] else _STEP.match(line)
        if match:
            steps.append([index, match.group(2).strip(), match.group(2).strip()])
            open_step = True
        elif open_step and (doc.code[index] or line.startswith((" ", "\t")) or not line.strip()):
            # Indented lines, blank lines and code blocks belong to the step above.
            steps[-1][2] += "\n" + line
        else:
            open_step = False
    for step in steps:
        # The first line decides; the continuation (indented text, code blocks
        # such as pasted git status output) only when the first line names
        # nothing.
        step.append(_step_kind(step[1]) or _step_kind(step[2]))
    wanted = [("check", "全课检查", CLOSING_CHECK.format(lesson=lesson_id))]
    if rules:
        wanted.append(("notes", "行规笔记", _notes_line(rules, cards)))
    wanted.append(("journal", "一句话日志", CLOSING_JOURNAL))
    backup = lesson_id and lesson_key(lesson_id) >= lesson_key(BACKUP_FROM)
    if backup:
        wanted.append(("backup", "备份", CLOSING_BACKUP if lesson_id != BACKUP_FROM else ""))
    kinds = [step[3] for step in steps]
    if not rules and "notes" in kinds:
        step = steps[kinds.index("notes")]
        report.warn("I1", f"{_where(step[0])}：本课没有新规则，收尾不要「行规笔记」这一步（现在是「{_short(step[1], 50)}」）")
        steps = [s for s in steps if s[3] != "notes"]
        kinds = [step[3] for step in steps]
    order_ok = True
    for number, (kind, name, expected) in enumerate(wanted, 1):
        if kind not in kinds:
            report.warn("I1", "收尾里没有「{}」这一步（{}起）。第 {} 步要写成「{}. {}」".format(
                name, _where(start), number, number,
                expected or "（第 1.12 课在这里写出备份要用的那一组命令，最后是 git push）"))
            order_ok = False
            continue
        position = kinds.index(kind)
        step = steps[position]
        if position != number - 1:
            order_ok = False
        if kind == "backup" and not expected:
            if "git push" not in step[2] and "git push" not in step[1]:
                report.warn("I1", f"{_where(step[0])}的备份这一步要写出那一组命令，最后要有 git push")
            continue
        if step[1] != expected:
            extra = ""
            if kind == "check":
                other = re.search(r"check (\d+\.\d+[a-z]?)", step[1] + step[2])
                if other and other.group(1) != lesson_id:
                    extra = f"；检查的应该是 {lesson_id}，现在是 {other.group(1)}"
            if kind == "notes":
                missing = [r for r in rules if r not in step[1] + step[2]]
                if missing:
                    extra = "；没有写到 {}".format("、".join(missing))
            report.warn("I1", f"{_where(step[0])}的收尾第 {position + 1} 步写法不对{extra}：现在是「{_short(step[1], 80)}」；要写成「{number}. {expected}」")
    if not order_ok and all(kind in kinds for kind, _n, _e in wanted):
        report.warn("I1", "收尾的步骤顺序不对（{}起）：从第 1 步开始，依次是{}；本课自己的步骤编号接在后面".format(
            _where(start), "、".join(name for _k, name, _e in wanted)))
    _check_closing_end(report, doc, start, end, lesson_id, entry)


def _check_closing_end(report, doc, start, end, lesson_id, entry):
    target = _closing_end(lesson_id, entry)
    if target is None:
        return
    kind, expected = target
    lines = [i for i in range(start + 1, end) if doc.lines[i].strip() and not doc.code[i]]
    if not lines:
        return
    index = lines[-1]
    line = doc.lines[index].strip()
    if (kind == "stage" and line.endswith(expected)) or line == expected:
        return
    shown = expected if kind != "stage" else "都做完，这一课就完成了。" + expected
    report.warn("I1", f"收尾的最后一行要是「{shown}」；现在最后一行（{_where(index)}）是「{_short(line, 80)}」")


# -- V4 the marks of plan G6 ---------------------------------------------------
def _check_marks(report, doc, meta, seen):
    marks = []
    for index, line in enumerate(doc.lines):
        for mark in MARKS:
            if mark not in line:
                continue
            marks.append(index)
            if doc.code[index]:
                report.warn("G6", f"{_where(index)}的标记 {mark} 写在了代码块里：标记写在正文里，紧跟着那一步")
            elif any(mark in span.group(2) for span in _INLINE_CODE.finditer(line)):
                report.warn("G6", f"{_where(index)}的标记 {mark} 写在了反引号里：标记不放进 `…`，直接写在正文里")
    lines = [i for i, line in enumerate(doc.lines)
             if "课文对不上" in line and "和你看到的不一样" in line]
    seen.update(lines)
    unverified = meta.get("unverified_steps")
    unverified = unverified if isinstance(unverified, list) else []
    if not marks:
        if lines:
            report.warn("G6", f"{_where(lines[0])}有「{G6_LINE}」这一行，课文里却没有〔对照文档，界面可能不同〕或〔建课时无法验证〕"
                              "标记：给那一步加上标记，或者删掉这一行")
        if unverified:
            report.warn("G6", f"META['unverified_steps'] 列了 {len(unverified)} 步，课文里却没有标记："
                              "给这些步骤加上〔…〕标记，或者从列表里删掉")
        return
    first = marks[0]
    if not unverified:
        report.warn("G6", f"课文里有 {len(marks)} 处〔…〕标记（第一处在{_where(first)}），META['unverified_steps'] 却是空的："
                          "把这些步骤列进去")
    if not lines:
        report.warn("G6", f"课文里有 {len(marks)} 处〔…〕标记，却没有这一行：「{G6_LINE}」。把它单独一行放在第一处标记"
                          f"（{_where(first)}）那一步的后面，不放在引用框（>）里")
        return
    if len(lines) > 1:
        report.warn("G6", "「{}」这一行每课只出现一次，现在出现了 {} 次（第 {} 行）：只留第一处标记后面的那一行".format(
            G6_LINE, len(lines), "、".join(str(i + 1) for i in lines)))
    after = [i for i in lines if i >= first]
    index = after[0] if after else lines[0]
    problems = []
    if index < first:
        problems.append(f"要放在第一处标记（{_where(first)}）的后面")
    if doc.quoted(index):
        problems.append("不放在引用框（>）里")
    if doc.lines[index].strip().lstrip(">").strip() != G6_LINE:
        problems.append("写法要和规定的一字不差")
    if problems:
        report.warn("G6", "{}的「课文对不上」这一行：{}。现在是「{}」；要写成「{}」".format(
            _where(index), "，".join(problems), _short(doc.lines[index], 80), G6_LINE))


# -- V5 sentences to the tutor and quotation marks ----------------------------
def _tutor_sentence_problem(sentence):
    """Advice when ``sentence`` is about going on or help but not a fixed form."""
    sentence = sentence.strip()
    if any(form.fullmatch(sentence) for form in _TUTOR_FORMS):
        return ""
    if not any(word in sentence for word in _RESUME_WORDS):
        return ""
    if "急救" in sentence:
        return "求助要说“急救：<一句话说现象>”"
    if "干活" in sentence:
        return "要说“干活：<要做的事>”"
    if "收尾" in sentence:
        return "最后一站之后说“从 <课号> 的收尾继续”，例如“从 1.6 的收尾继续”"
    if "讲解" in sentence or "讲给" in sentence:
        return "要说“请问我 <关卡> 的讲解题”，例如“请问我 gate-0 的讲解题”"
    if "关卡" in sentence:
        return "要说“做小关卡 <关卡>”，例如“做小关卡 gate-a”"
    if "阶段" in sentence:
        return "要说“准备阶段 2”"
    if "上课" in sentence:
        return "回到课上只说“回到上课”，要做什么另说一句"
    return ("固定的说法是“从 1.6b 继续”“从 1.6 的收尾继续”“从 1.7 开始”“做小关卡 gate-a”"
            "“急救：……”这几种")


def _tutor_matches(text):
    for match in _TUTOR_SAY.finditer(text):
        sentence = next(group for group in match.groups() if group is not None)
        problem = _tutor_sentence_problem(sentence)
        if problem:
            yield sentence, problem


def _check_tutor_sentences_md(report, doc, seen):
    for index, line in enumerate(doc.lines):
        for sentence, problem in _tutor_matches(line):
            if index in seen and doc.lines[index].lstrip().startswith(("> **存档点", "> **中途存档点")):
                continue
            seen.add(index)
            report.warn("G2", f"{_where(index)}叫学习者对导师说“{sentence}”：这不是课程的固定说法。{problem}")


def _check_ascii_quotes(report, doc, seen):
    for index, line in enumerate(doc.lines):
        if doc.code[index] or index in seen or line.lstrip().startswith("|-") \
                or re.match(r"^\s*\|?\s*:?-{3,}", line):
            continue
        text = _INLINE_CODE.sub("x", line)
        if text.count('"') < 2 or text.count('"') % 2:
            continue
        pairs = re.findall(r'"([^"]*)"', text)
        chinese = [p for p in pairs if _CJK.search(p)]
        if chinese:
            report.warn("G2", '{}用英文直引号 " " 括住了中文「{}」：课文里的中文引号用全角的 “ ”'.format(
                _where(index), _short('"' + chinese[0] + '"', 40)))


# -- V6 the course folder ------------------------------------------------------
#: The course folder before it was renamed on 2026-11-21, as a path part (~/Developer/Engineering,
#: …/Engineering/…).  Book titles such as "Software Engineering" are not paths and are not caught.
_OLD_FOLDER = re.compile(r"/Engineering(?![A-Za-z])")

def _path_problems(line, lesson_id):
    problems = []
    if "Desktop/Code/fullstack-from-zero" in line and lesson_id != "0.2":
        problems.append("写了 Desktop/Code/fullstack-from-zero：只有第 0.2 课提这个旧位置，"
                        "别的课一律写 ~/Developer/fullstack-from-zero")
    if _OLD_FOLDER.search(line):
        problems.append("写了旧的文件夹名 Engineering（2026-11-21 改名）：课程文件夹现在叫 fullstack-from-zero，"
                        "一律写 ~/Developer/fullstack-from-zero")
    for match in _USERS_PATH.finditer(line):
        user = match.group(1)
        if not user or _CJK.search(user) or user.startswith(("…", ".", "<", "$", "{")) or user in ("Shared", "Guest"):
            continue
        problems.append(f"写了 /Users/{user}：主文件夹写成 ~，要写出用户名时写「你的用户名」")
    if "/private/tmp/" in line:
        problems.append("写了 /private/tmp/ 下面的路径：这是建课时的临时文件夹，课文里不出现")
    return problems


def _folder_name_problems(text, lesson_id):
    problems = []
    if "课程文件夹" in text:
        problems.append("用了「课程文件夹」：课程所在的文件夹叫「学习工作区」")
    if "练习文件夹" in text and "fullstack-from-zero" in text:
        problems.append("用了「练习文件夹」指课程文件夹：课程所在的文件夹叫「学习工作区」")
    if lesson_id and lesson_key(lesson_id) >= lesson_key(WORKING_TREE_FROM):
        # From 1.12 on the 学习工作区 is a repository (学习仓库), and 「~/Developer/
        # fullstack-from-zero 的工作区是干净的」 uses 工作区 in Git's own sense.
        git_sense = (lesson_key(lesson_id) >= lesson_key(REPO_FROM)
                     and re.search(r"git|仓库|提交|暂存|干净|改动", text, re.IGNORECASE))
        bare = (re.search(r"回到工作区", text)
                or not git_sense and re.search(r"(?<!学习)工作区[\s`（(：:]*~/Developer/fullstack-from-zero", text)
                or not git_sense and re.search(r"~/Developer/fullstack-from-zero[`）)\s]*(?:这个|的)?(?<!学习)工作区", text))
        if bare:
            problems.append(f"「{_short(bare.group(0), 30)}」里的「工作区」指的是课程文件夹：从第 1.6 课起「工作区」是 Git 的词，"
                            "课程文件夹要写「学习工作区」")
    return problems


def _check_course_folder_md(report, doc, lesson_id):
    for index, line in enumerate(doc.lines):
        problems = _path_problems(line, lesson_id)
        if not doc.code[index]:
            problems += _folder_name_problems(line, lesson_id)
        for problem in problems:
            report.warn("G10", f"{_where(index)}{problem}")


# -- V7 optional material ------------------------------------------------------
def _check_optional_labels(report, doc):
    for index, line in enumerate(doc.lines):
        if doc.code[index]:
            continue
        if doc.quoted(index) and (index == 0 or not doc.quoted(index - 1)):
            label = _label_of_quote(line)
            if not label:
                continue
            if label.startswith("想多了解") and not label.startswith(OPTIONAL_LABEL) or any(word in label for word in OPTIONAL_WORDS):
                bad = label
            else:
                continue
            report.warn("I1", f"{_where(index)}的可跳过材料标成了「{_short(bad, 40)}」：框的标签只用「> **想多了解（可跳过）：<小标题>**」"
                              "（不用选做、选读、可选、可以跳过）")
    for index, level, title in doc.headings:
        if level == 2 and title == "想多了解":
            continue
        if "想多了解" in title or _OPTIONAL_IN_HEADING.search(title):
            report.warn("I1", f"{_where(index)}的标题「{_short(title, 40)}」：可跳过的材料放进「> **想多了解（可跳过）：<小标题>**」框，"
                              "或者放进最后一节「## 想多了解」")


# -- V8 the rule summary -------------------------------------------------------
def _cells(line):
    """The cells of a Markdown table row (pipes inside `code` do not split)."""
    cells, current, in_code = [], "", False
    text = line.strip()
    text = text.removeprefix("|")
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    for char in text:
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code:
            cells.append(current.strip())
            current = ""
        else:
            current += char
    cells.append(current.strip())
    return cells


def _check_rule_summary(report, doc, rules, cards):
    if not rules:
        return
    found = doc.section(lambda title: title.startswith("本课行规"))
    if not found:
        report.warn("I2", "lesson.md 里没有「## 本课行规」这一节：要有一张表「| {} |」，"
                          "表下面写「{}」".format(" | ".join(SUMMARY_COLUMNS), SUMMARY_SENTENCE))
        return
    start, end = found
    rows = [i for i in range(start + 1, end) if not doc.code[i] and doc.lines[i].lstrip().startswith("|")]
    if not any(SUMMARY_SENTENCE == doc.lines[i].strip() for i in range(start + 1, end)):
        variant = [i for i in range(start + 1, end) if "完整" in doc.lines[i] and "卡片" in doc.lines[i]]
        report.warn("I2", "本课行规这一节（{}起）要有单独一行「{}」{}".format(
            _where(start), SUMMARY_SENTENCE,
            f"，现在是{_where(variant[0])}「{_short(doc.lines[variant[0]], 60)}」" if variant else ""))
    if not rows:
        report.warn("I2", "本课行规这一节（{}起）没有表格：要写成「| {} |」这样一张表，"
                          "每条规则一行，约束力和规则类型照抄 rules.md 的卡片".format(
                              _where(start), " | ".join(SUMMARY_COLUMNS)))
        return
    header = _cells(doc.lines[rows[0]])
    if tuple(header) != SUMMARY_COLUMNS:
        report.warn("I2", "{}的表头要是「| {} |」，现在是「| {} |」".format(
            _where(rows[0]), " | ".join(SUMMARY_COLUMNS), " | ".join(header)))
    columns = {name: header.index(name) for name in ("约束力", "规则类型") if name in header}
    by_id = {card.id: card for card in cards}
    listed = {}
    for index in rows[1:]:
        cells = _cells(doc.lines[index])
        rule = re.sub(r"[*`\s]", "", cells[0]) if cells else ""
        if rule in rules:
            listed[rule] = (index, cells)
    for rule in rules:
        if rule not in listed:
            report.warn("I2", f"本课行规的表里没有 {rule} 这一行（{_where(start)}起）")
            continue
        index, cells = listed[rule]
        card = by_id.get(rule)
        if card is None:
            continue
        for name, column in sorted(columns.items()):
            cell = cells[column] if column < len(cells) else ""
            value = card.get(name)
            if value and _squash(cell) != _squash(value):
                report.warn("I2", f"{_where(index)}：{rule} 的「{name}」和 rules.md 的卡片不一样。表里是「{_short(cell, 60)}」，卡片上是「{_short(value, 60)}」："
                                  "照抄卡片")


# -- V9 old-tutorial boxes -----------------------------------------------------
def _since_when(text):
    """Does an old-tutorial text say since when (a year, a version, a date)?

    A check date (「2026-11-19 核对」) says when the builder looked, not since
    when the new way holds, so it does not count.
    """
    text = _CHECKED.sub("", _LESSON_REF.sub("", text))
    return bool(_YEAR_OR_VERSION.search(text) or _NAMED_RELEASE.search(text))


def _check_old_tutorial_boxes(report, doc):
    for index, line in enumerate(doc.lines):
        if doc.code[index] or "**旧教程提醒**" not in line or not doc.quoted(index):
            continue
        _first, last = doc.quote_block(index)
        stop = last
        if re.match(r"^\s*>\s*[-*]\s", line):
            for other in range(index + 1, last + 1):
                if re.match(r"^\s*>\s*[-*]\s", doc.lines[other]):
                    stop = other - 1
                    break
        box = "\n".join(doc.lines[index:stop + 1])
        if not _since_when(box):
            report.warn("G4", f"{_where(index)}的旧教程提醒没写从什么时候起：要写上年份、版本号或日期，"
                              f"例如「（自 Git 2.23 起）」「（2020 年起）」。现在是「{_short(line, 60)}」")


# -- V10 the old form of git config ---------------------------------------------
def _old_git_config(text):
    """The first ``git config`` call in ``text`` that has no subcommand, or ""."""
    for match in _GIT_CONFIG.finditer(text):
        token = match.group(1)
        if not token or token in GIT_CONFIG_SUBCOMMANDS or token in ("-h", "--help"):
            continue
        if token.startswith(("-", "_", "<")) or re.match(r"^[A-Za-z][\w-]*\.[\w.-]+", token):
            return text[match.start():match.end()]
    return ""


def _git_config_advice():
    return ("这门课统一用带子命令的写法：git config set --global <名字> <值>、git config get <名字>、"
            "git config unset --global <名字>、git config list（Git 手册把不带子命令的写法列为过时的写法，"
            "只有第 1.6 课的旧教程提醒里提一次）")


def _check_git_config_md(report, doc):
    exempt = set()
    for index, line in enumerate(doc.lines):
        if "**旧教程提醒**" in line and doc.quoted(index):
            first, last = doc.quote_block(index)
            exempt.update(range(first, last + 1))
    # Git's own identity message quotes the old form: that output stays as it is.
    identity = {doc.block[i] for i, line in enumerate(doc.lines)
                if doc.code[i] and "Please tell me who you are" in line}
    for index, line in enumerate(doc.lines):
        if index in exempt:
            continue
        if doc.code[index]:
            found = "" if doc.block[index] in identity else _old_git_config(line)
        else:
            found = next((f for f in (_old_git_config(s.group(2)) for s in _INLINE_CODE.finditer(line))
                          if f), "")
        if found:
            report.warn("G4", f"{_where(index)}用了 git config 的旧写法「{found}」：{_git_config_advice()}")


# -- lesson.py: texts the learner reads ---------------------------------------
def _module_strings(tree):
    """``(line, text)`` of the string constants of a module, without docstrings."""
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                docstrings.add(id(body[0].value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            yield node.lineno, node.value


def _hint_strings(tree):
    """``(station, level, line, text)`` of the literal hints in ``HINTS = {...}``."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "HINTS" for t in node.targets):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            station = key.value if isinstance(key, ast.Constant) else "?"
            if not isinstance(value, (ast.List, ast.Tuple)):
                continue
            for level, element in enumerate(value.elts, 1):
                parts = [n.value for n in ast.walk(element)
                         if isinstance(n, ast.Constant) and isinstance(n.value, str)]
                if parts:
                    yield station, level, element.lineno, "".join(parts)


def _check_module_texts(report, lesson, lesson_id):
    """Sentences to the tutor, paths and names in lesson.py (V5, V6, V10)."""
    try:
        source = lesson.path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
        return
    for number, line in enumerate(source.splitlines(), 1):
        for problem in _path_problems(line, lesson_id):
            report.warn("G10", f"lesson.py 的第 {number} 行{problem}")
    for number, text in _module_strings(tree):
        for sentence, problem in _tutor_matches(text):
            report.warn("G2", f"lesson.py 的第 {number} 行叫学习者对导师说“{sentence}”：这不是课程的固定说法。{problem}")
        for problem in _folder_name_problems(text, lesson_id):
            report.warn("G10", f"lesson.py 的第 {number} 行{problem}")
    for station, level, number, text in _hint_strings(tree):
        found = _old_git_config(text)
        if found:
            report.warn("G4", f"HINTS[{station!r}] 的第 {level} 级提示（lesson.py 的第 {number} 行）用了 git config 的旧写法"
                              f"「{found}」：{_git_config_advice()}")


def _cards_of(lesson):
    try:
        return rulecards.parse_cards(lesson.rules_path.read_text(encoding="utf-8")) \
            if lesson.rules_path.is_file() else []
    except (OSError, UnicodeDecodeError):
        return []


def _reserved_words():
    """Review-session commands (``q``, ``s`` ...) -> what they do, in Chinese."""
    from .commands.review import RESERVED_WORDS
    effects = {"quit": "结束这次复习", "skip": "跳过这一题"}
    return {word: effects.get(kind, kind) for word, kind in RESERVED_WORDS.items()}


def _check_reserved_option(report, label, letter, option, reserved):
    word = normalize(option) if isinstance(option, str) else ""
    if word in reserved:
        report.warn("I3", f"{label} 的选项 {letter} 只有「{option.strip()}」：复习时输入 {word} "
                          f"会{reserved[word]}，学习者照着选项原文输入就答不了这一题。"
                          f"把选项写完整，例如「按 {word}」")


def _check_choice_options(report, lesson, names):
    """Options of REVIEW choice items and of literal ctx.quiz / ctx.choose calls."""
    reserved = _reserved_words()
    review = names.get("REVIEW")
    for item in review if isinstance(review, list) else []:
        if not isinstance(item, dict) or item.get("type") not in CHOICE_TYPES:
            continue
        options = item.get("options")
        label = "复习题 {}".format(item.get("id"))
        for index, option in enumerate(options if isinstance(options, list) else []):
            _check_reserved_option(report, label, "ABCDEF"[index] if index < 6 else "?",
                                   option, reserved)
    try:
        tree = ast.parse(lesson.path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
        return
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in CHOICE_METHODS):
            continue
        options = node.args[1] if len(node.args) > 1 else None
        for keyword in node.keywords:
            if keyword.arg == "options":
                options = keyword.value
        if not isinstance(options, (ast.List, ast.Tuple)):
            continue
        label = f"第 {node.lineno} 行的 ctx.{node.func.attr}"
        for index, element in enumerate(options.elts):
            if isinstance(element, (ast.Tuple, ast.List)) and len(element.elts) == 2:
                element = element.elts[1]
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                _check_reserved_option(report, label, "ABCDEF"[index] if index < 6 else "?",
                                       element.value, reserved)


# ---------------------------------------------------------------------------
# Trial builds
# ---------------------------------------------------------------------------
def trial_build(app, lesson, report):
    """Run every scenario builder and exam builder once in a throw-away playground."""
    import io

    from .app import App
    from .ui import Console
    with tempfile.TemporaryDirectory(prefix="course-validate-") as folder:
        env = dict(app.env)
        env["COURSE_PLAYGROUND"] = folder + "/playground"
        quiet = Console(out=io.StringIO(), err=io.StringIO(), can_prompt=False, is_tty=False)
        shadow = App(app.root, env=env, console=quiet, now=app.now)
        for key, builder in sorted(lesson.scenarios.items(), key=lambda pair: str(pair[0])):
            if not callable(builder):
                continue
            try:
                scenario.build(shadow, builder, f"s-{key}", scenario_id=lesson.scenario_id(key),
                               key=str(key), lesson_id=lesson.id, seed=20261119, log=False)
            except CourseError as exc:
                report.error("BUILD", f"场景 {key} 搭建失败：{_brief(exc)}")
        for task in lesson.exam:
            if not callable(task.get("build")) or not isinstance(task.get("task"), dict):
                continue
            for form in ("A", "B"):
                name = "x-{}-{}".format(task.get("id"), form)
                try:
                    info = scenario.build(shadow, task["build"], name, scenario_id=name,
                                          lesson_id=lesson.id, seed=20261119, form=form, log=False)
                except CourseError as exc:
                    report.error("BUILD", "考题 {} 的 {} 卷搭建失败：{}".format(task.get("id"), form, _brief(exc)))
                    continue
                text = task["task"].get(form)
                for name_in_text in _PLACEHOLDER.findall(text if isinstance(text, str) else ""):
                    if name_in_text != "dir" and name_in_text not in info.facts:
                        report.error("BUILD", "考题 {} 的 {} 卷题面用了 {{{}}}，但搭建函数没有用 sc.fact 记录它".format(task.get("id"), form, name_in_text))


def _brief(exc):
    summary = getattr(exc, "summary", None) or getattr(exc, "message", None) or str(exc)
    detail = getattr(exc, "detail", "") or ""
    last = detail.strip().splitlines()[-1] if detail.strip() else ""
    return summary + (f"（{last}）" if last and last not in summary else "")


# ---------------------------------------------------------------------------
# Python 3.9
# ---------------------------------------------------------------------------
def find_python39(env):
    """Path of a Python 3.9 interpreter on this machine, or "" when there is none."""
    if sys.version_info[:2] == (3, 9):
        return sys.executable
    child = dict(env)
    child["PYTHONDONTWRITEBYTECODE"] = "1"
    for candidate in OLD_PYTHONS:
        try:
            done = subprocess.run([candidate, "-c", _PROBE], capture_output=True, env=child,
                                  timeout=10, check=False, stdin=subprocess.DEVNULL)
        except (OSError, subprocess.SubprocessError):
            continue
        if done.returncode == 0 and done.stdout.decode("ascii", "replace").strip() == "3.9":
            return candidate
    return ""


def check_python39(app, reports):
    """Compile every lesson module as Python 3.9; returns general findings."""
    general = []
    paths = []
    for report in reports:
        path = report.lesson.path
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            ast.parse(source, filename=str(path), feature_version=(3, 9))
        except SyntaxError as exc:
            report.error("I3", f"课程模块用了 Python 3.9 不认识的写法：第 {exc.lineno} 行 {exc.msg}")
            continue
        paths.append((report, path))
    if sys.version_info[:2] == (3, 9) or not paths:
        return general
    python = find_python39(app.env)
    if not python:
        general.append(Finding(WARNING, "I3", "这台电脑上没有找到 Python 3.9，"
                                              "只做了一部分 3.9 兼容性检查"))
        return general
    child = app.child_env()
    child["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        done = subprocess.run([python, "-c", _COMPILE] + [str(path) for _, path in paths],
                              capture_output=True, env=child, timeout=60, check=False,
                              stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as exc:
        general.append(Finding(WARNING, "I3", f"Python 3.9 兼容性检查没有跑成（{type(exc).__name__}）"))
        return general
    lines = done.stdout.decode("utf-8", "replace").splitlines()
    if len(lines) != len(paths):
        general.append(Finding(WARNING, "I3", "Python 3.9 兼容性检查的输出不完整，结果不可靠"))
        return general
    for (report, _), line in zip(paths, lines):
        if line.startswith("BAD "):
            _, number, message = (line.split(" ", 2) + ["", ""])[:3]
            report.error("I3", f"课程模块在 Python 3.9 上编译不过：第 {number} 行 {message}"
                               "（课程模块必须能在 3.9 上运行）")
    return general


# ---------------------------------------------------------------------------
# The whole workspace
# ---------------------------------------------------------------------------
def validate_all(app, lessons, complete=False, build=False):
    """Validate ``lessons``; returns ``(reports, general_findings)``."""
    today = app.today
    reports = [validate_lesson(lesson, today, complete=complete) for lesson in lessons]
    general = check_python39(app, reports)
    if build:
        for report in reports:
            if report.lesson.namespace:
                trial_build(app, report.lesson, report)
    general += _cross_checks(reports, complete)
    return reports, general


def _command_key(command):
    """``command`` as compared across lessons: one ellipsis, one space, any gate."""
    key = " ".join(command.replace("...", "…").split())
    return re.sub(r"\bgate-[a-z0-9]+\b", "gate-…", key)


def _cross_checks(reports, complete):
    findings = []
    owners = {"lesson": {}, "rule": {}, "term": {}, "command": {}, "item": {}}

    def claim(kind, key, lesson_id, level, message):
        first = owners[kind].setdefault(key, lesson_id)
        if first != lesson_id:
            findings.append(Finding(level, "X", message % (key, first, lesson_id)))

    def owned(kind, key, shown, lesson_id, owner, message, what):
        """Like ``claim``, but the owner lesson is known (TERM_OWNERS / COMMAND_OWNERS)."""
        first = owners[kind].setdefault(key, lesson_id)
        if lesson_id == owner:
            return
        if first != lesson_id:
            findings.append(Finding(WARNING, "X", (message % (shown, first, lesson_id))
                                    + f"；按约定它归 {owner} 课：{lesson_id} 课的 {what}去掉这一项，课文里留一句简短的解释"))
        else:
            findings.append(Finding(WARNING, "X", "{} 归 {} 课（课程约定的归属），{} 课的 {}不要把它算成{}".format(
                shown if kind == "term" else f"命令 {shown!r}", owner, lesson_id, what,
                "第一次出现" if kind == "term" else "新命令")))

    present = set()
    glosses = {}
    for report in reports:
        lesson = report.lesson
        meta = lesson.meta
        lesson_id = meta.get("id") if isinstance(meta.get("id"), str) else lesson.rel
        present.add(lesson_id)
        claim("lesson", lesson_id, lesson.rel, ERROR, "课程编号 %s 被两个文件夹同时使用：%s 和 %s")
        for rule in lesson.rules:
            claim("rule", rule, lesson_id, ERROR, "规则 %s 在 %s 和 %s 两课里都算成了新规则")
        for term in lesson.terms:
            if isinstance(term.get("term"), str):
                name = term["term"]
                if name in TERM_OWNERS:
                    owned("term", name, f"术语「{name}」", lesson_id, TERM_OWNERS[name],
                          "%s在 %s 和 %s 两课里都算成了第一次出现", "TERMS ")
                else:
                    claim("term", name, lesson_id, WARNING, "术语「%s」在 %s 和 %s 两课里都算成了第一次出现")
                gloss = term.get("en")
                if isinstance(gloss, str) and gloss.strip():
                    glosses.setdefault(gloss.strip(), []).append((lesson_id, name))
        for station in meta.get("stations", []) if isinstance(meta.get("stations"), list) else []:
            commands = station.get("new_commands") if isinstance(station, dict) else None
            for command in commands if isinstance(commands, list) else []:
                if isinstance(command, str):
                    key = _command_key(command)
                    if key in COMMAND_OWNERS:
                        same = "（不同关卡的 exam 算同一条命令）" if "gate-…" in key else ""
                        owned("command", key, command, lesson_id, COMMAND_OWNERS[key],
                              "命令 %r 在 %s 和 %s 两课里都算成了新命令" + same, "new_commands ")
                    else:
                        claim("command", key, lesson_id, WARNING, "命令 %r 在 %s 和 %s 两课里都算成了新命令")
        for item in lesson.review + lesson.exam:
            if isinstance(item.get("id"), str):
                claim("item", item["id"], lesson_id, ERROR, "题目编号 %s 在 %s 和 %s 两课里重复了")
    for gloss, uses in glosses.items():
        names = []
        for lesson_id, name in uses:
            if name not in [n for _l, n in names]:
                names.append((lesson_id, name))
        if len(names) > 1:
            findings.append(Finding(WARNING, "X", "英文原词 {!r} 下面有 {} 个不同的术语：{}。同一个英文词只用一个"
                                                  "中文术语：后面的课沿用最早那一课的叫法".format(
                                                      gloss, len(names),
                                                      "、".join(f"{l} 课的「{n}」" for l, n in names))))
    if complete:
        for entry in LESSONS:
            if entry["id"] not in present:
                findings.append(Finding(ERROR, "§4", "大纲里的 {} 课（stages/{}/{}）还没有".format(entry["id"], entry["stage_folder"], entry["folder"])))
        for report in reports:
            prerequisites = report.lesson.meta.get("prerequisites")
            for item in prerequisites if isinstance(prerequisites, list) else []:
                if isinstance(item, str) and item not in present:
                    findings.append(Finding(ERROR, "I3", f"{report.lesson.id} 课的前置课程 {item} 不存在"))
        for gate_id, gate in sorted(GATES.items()):
            # A sitting holds one task per lesson the gate covers (COMMON.md
            # section 1): every one of those lessons needs a task of this gate.
            tasks = [(report.lesson.id, task) for report in reports for task in report.lesson.exam
                     if task.get("gate") == gate_id]
            count = len(tasks)
            if count < MIN_GATE_TASKS:
                findings.append(Finding(ERROR, "I7", f"关卡 {gate_id} 只有 {count} 道考题，"
                                                     f"至少要 {MIN_GATE_TASKS} 道"))
            covered = {lesson_id for lesson_id, _task in tasks}
            for lesson_id in gate["lessons"]:
                if lesson_id in present and lesson_id not in covered:
                    findings.append(Finding(ERROR, "I7", f"{lesson_id} 课还没有关卡 {gate_id} 的考题："
                                                         "一场考试每课出一题，每一课至少要有一道"))
    return findings
