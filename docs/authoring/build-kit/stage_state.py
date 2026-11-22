#!/usr/bin/env python3
"""Stage the state of a simulated learner for the tutor tests.

For builders and testers of the course only (docs/authoring/tutor-tests.md,
"How to run a test", step 1).  Learners never run this.  Standard library
only, Python 3.9 or newer.

Every change of learner/state.json and learner/log.jsonl is made by the
course tool's own code, imported from the tools/ folder of the simulated
workspace and run in-process: the real ``check``, ``hint``, ``status``,
``exam``, ``journal`` commands and the review session class.  Only the
*verdict* of a check or exam task is chosen here (the guarded runner
``courselib.runner.run_check`` is replaced for the stations and tasks named in
the spec); recording, scheduling, sessions and the log are the tool's.
learner/profile.md is plain text written from templates/profile-template.md.

Commands
--------

    python3 stage_state.py apply <spec.json | ->       stage the steps of a spec
    python3 stage_state.py show [--on YYYY-MM-DD]      summary of the staged state
    python3 stage_state.py peek --now <date> -- <tool arguments>
                                                       run course.py, then restore learner/, journal/, PROGRESS.md
    python3 stage_state.py --self-test                 build a simulation home, stage, check with status, remove it

``apply``, ``show`` and ``peek`` must run with HOME pointing at a simulation
home (made by tools/dev/make_sim_home.py under the system temporary folder)
and with the working directory inside that simulation's workspace copy; they
refuse otherwise.  The full usage, with one example per kind of state, is
printed by ``python3 stage_state.py --help-spec``.
"""

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import contextlib  # noqa: E402
import datetime  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve()
#: The workspace this file ships in (docs/authoring/build-kit/stage_state.py);
#: ``--self-test --workspace <dir>`` names another one.
OWN_WORKSPACE = HERE.parents[3]

STRICTNESS = ("严格", "适中", "宽松")

SPEC_HELP = r"""
SPEC FORMAT (apply)

A spec is JSON: either a list of steps, or an object
  {"start_time": "19:30", "minutes_per_command": 4, "steps": [ ... ]}.
Steps run in the order given and must go forward in time (a step dated
before the previous one is refused).  A date is "YYYY-MM-DD" (the day's
first command runs at start_time, default 19:30, and each tool command
moves the clock on by minutes_per_command, default 4) or
"YYYY-MM-DDTHH:MM" for an exact time.  Unknown keys are refused.

Steps ("do": ...):

  profile    learner/profile.md from templates/profile-template.md
             {"do": "profile", "strictness": "适中", "hours": 6,
              "product": "汇率看板",            # adds 「课程产品：汇率看板」 (lesson 0.3a)
              "schedule": "default",            # adds 「## 每周学习时间」 (lesson 0.4); or a list of lines
              "tired": "default",               # adds 「## 累了协议」 (lesson 0.4); or a list of lines; omit = no section
              "weekly": "<free text>",          # replaces the answer under 「## 每周时间与固定时段」
              "answers": {"英文阅读": "能直接读"},  # replaces the answer under any template heading
              "replace": false}                 # true: overwrite an existing profile.md
             strictness is one of 严格 / 适中 / 宽松 (default 适中).

  pass       stations passed, in course order, through the real `check`
             {"do": "pass", "from": "0.1a", "to": "1.6a",
              "date": "2026-11-24"                       # all on one day, or
              "dates": ["2026-11-02", "2026-11-05"],     # spread evenly, last station on the last date, or
              "start": "2026-11-02", "end": "2026-11-24", "days": 10,   # evenly spaced study days
              "hints": {"1.3b": 2, "1.5a": 4},           # hint levels seen before that station passed
              "lesson_checks": true,                     # run `check <lesson>` when a lesson's last station passes (default true)
              "no_lesson_check": ["1.3"],                # ...except these lessons
              "decisions": {"0.2c": {"workspace_location": "stay-in-sync"}},
              "reviews": "daily"}                        # one review session (all 记得) on each study day
                                                         # of this step that has items due, before its passes
             "from"/"to" may be a lesson id ("1.6" = its first / last station);
             "stations": [...] instead of from/to names them one by one.
             Stations already passed are skipped.  Decisions the real checks
             record are recorded too: 0.1c hello_fx_amount (AMOUNT_USD of the
             workspace's starter/hello-fx/convert.py), 0.2c workspace_location
             "not-synced" (kept when one is recorded already, e.g. by --stay),
             0.3a course_product (the 课程产品 line of learner/profile.md, else
             汇率看板), 1.6a commit_signing "off", 1.11b commit_email "noreply"
             and commit_signing "off"; "decisions" overrides or adds.
             Hint level 4 makes the station 带扶手完成 with a cold redo in 3-7 days.

  hint       hint levels seen on a station (not passed), through `hint <station> --yes`
             {"do": "hint", "station": "1.8a", "level": 2, "date": "2026-11-20"}

  check      one check with a chosen verdict, through the real `check`
             {"do": "check", "target": "1.6b", "result": "fail", "times": 2, "date": "..."}
             result "pass" or "fail".  A fail first runs the real check on the
             untouched folders and keeps its 还没达标 when it gives one;
             otherwise it is a 还没达标 without detail lines.  target may be a
             lesson id: the whole-lesson check (its open stations get the result).
             A pass of an 带扶手完成 station inside its redo window, on a day
             without hints, is the cold redo (status turns to passed).
             result "problem" (a station only) makes the check end in
             检查器出问题 with the text you give; the tool prints its box and
             stores it in learner/last-result.json; it is not an attempt:
             {"do": "check", "target": "1.6b", "result": "problem", "date": "...",
              "problem": {"summary": "检查函数出错了：…", "where": "stages/…/lesson.py 第 12 行",
                          "detail": "Traceback …"}}

  session    a study day with no other activity: the real `status`
             {"do": "session", "date": "2026-11-24"}   or  "dates": [...]

  review     one review session served by the tool's own plan; every item
             served gets the same answer
             {"do": "review", "date": "2026-11-20", "answer": "right"}   # right / fuzzy / wrong

  due        exactly N review items due on a date (what `status` on that date counts)
             {"do": "due", "count": 3, "on": "2026-11-26", "review_day": "2026-11-24"}
             review_day (default: the last study day before "on") gets as many
             review sessions as it takes to answer every item due by then:
             N of them so that they fall due on "on" (or the day before),
             the rest so that they fall due later.  Items that fall due
             between review_day and "on" cannot be changed and count towards
             N; when they are more than N the step fails and says so (pass
             those stations at least two days before review_day).  The step
             checks the count with the tool's own review.due_count.  It is
             exact when "on" is 1 to 6 days after review_day; across a long
             break (7 days or more) leave the backlog as it is instead.

  exam-start draw a gate sitting: the real `exam <gate>` (builds the task
             folders in ~/Developer/playground/exam-<gate>/)
             {"do": "exam-start", "gate": "gate-b", "date": "...", "seed": 7}   # seed optional
  exam-grade grade the open sitting: the real `exam <gate> --grade`
             {"do": "exam-grade", "gate": "gate-b", "date": "...", "fail": ["1.8"]}
             "fail" lists lesson ids or task ids; every other task passes.
  explain    the explain-back verdict: the real `exam <gate> --explain pass|again`
             {"do": "explain", "gate": "gate-b", "result": "pass", "date": "..."}
  gate       exam-start + exam-grade (+ explain) on one date
             {"do": "gate", "gate": "gate-0", "date": "...", "fail": [], "explain": "pass"}
             "explain": "pass" / "again" / null (default null: no record).

  decision   set one decision (no tool command records decisions alone; the
             tool's store saves it and logs the change as a state patch)
             {"do": "decision", "key": "workspace_location", "value": "stay-in-sync"}

  journal    an entry through the real `journal --done ... --stuck ... --next ...`
             {"do": "journal", "date": "2026-10-28", "done": "做完了 1.3b",
              "stuck": "", "next": "auto", "unclear": "", "slow": ""}
             "next": "auto" (or omitted) = the sentence the tool proposes
             (status.next_step), as when the learner presses Enter.

  git-global change the SIMULATION's ~/.gitconfig (git config --file $HOME/.gitconfig;
             refused unless HOME is under the temporary folder)
             {"do": "git-global", "set": {"commit.gpgsign": "false"}, "unset": ["gpg.ssh.program"]}

  tool       any other tool command, unchanged, at a date
             {"do": "tool", "args": ["scenario", "1.8"], "date": "...", "expect": [0]}

Notes
  - learner/last-result.json holds the result of the last command staged;
    a forced verdict has empty 'ok' / 'missing' lists.  Finish with a real
    command ({"do": "tool", "args": ["doctor"]}) if the situation's tutor
    will read that file.
  - Passing 1.6a records commit_signing "off" but does not change the
    simulation's ~/.gitconfig (it still has commit.gpgsign = true, and
    doctor then says signing is on and gpg missing).  Add
    {"do": "git-global", "set": {"commit.gpgsign": "false"}} after 1.6a for
    a learner who did what lesson 1.6 says.
  - Files outside learner/ and journal/ (starter/, a .git, notes/my-rules.md)
    are not this helper's business: change them in the simulation directly.
"""


class StageError(Exception):
    """A step could not be staged; the message says why and what to do."""


# ---------------------------------------------------------------------------
# Safety: simulation homes only
# ---------------------------------------------------------------------------
def temp_roots():
    roots = []
    for candidate in (tempfile.gettempdir(), os.environ.get("TMPDIR", ""), "/tmp"):
        if candidate:
            real = os.path.realpath(candidate).rstrip("/")
            if real and real not in roots:
                roots.append(real)
    return roots


def under_temp(path):
    real = os.path.realpath(str(path)).rstrip("/")
    return any(real.startswith(root + "/") for root in temp_roots())


def find_root(start):
    """The workspace copy that holds ``start``: the folder with tools/course.py."""
    here = Path(os.path.realpath(str(start)))
    for folder in [here] + list(here.parents):
        if (folder / "tools" / "course.py").is_file() and (folder / "tools" / "courselib").is_dir():
            return folder
    return None


def guarded_root():
    """Check HOME and the working directory; return the workspace root."""
    home = os.environ.get("HOME", "")
    if not home or not under_temp(home):
        raise StageError("拒绝：HOME（{}）不在系统临时目录里。先用 tools/dev/make_sim_home.py 建一个"
                         "模拟家目录，再 export HOME=<sim>/home。".format(home or "未设置"))
    root = find_root(os.getcwd())
    if root is None:
        raise StageError("拒绝：当前目录不在一份学习工作区里（找不到 tools/course.py）。"
                         "先 cd 到模拟家目录里的 Developer/fullstack-from-zero。")
    if not under_temp(root):
        raise StageError("拒绝：工作区 {} 不在系统临时目录里；只给模拟家目录里的副本造状态。".format(root))
    if os.path.realpath(str(root)) == os.path.realpath(str(OWN_WORKSPACE)):
        raise StageError("拒绝：这是真正的学习工作区。")
    return root


def clean_environment():
    """Keep Git and the tool away from anything outside the simulation."""
    for key in ("XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "COURSE_PLAYGROUND", "COURSE_DEBUG",
                "COURSE_NOW"):
        os.environ.pop(key, None)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["NO_COLOR"] = "1"


def load_courselib(root):
    tools = str(root / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import courselib  # noqa: F401
    from courselib import app, cli, progress, review, runner, schedule, status, store, ui
    from courselib.commands import journal as journal_cmd
    from courselib.commands import review as review_cmd
    loaded = Path(courselib.__file__).resolve().parent
    if os.path.realpath(str(loaded)) != os.path.realpath(str(root / "tools" / "courselib")):
        raise StageError("拒绝：导入的 courselib 不是这份工作区里的（{}）。".format(loaded))
    return {"app": app, "cli": cli, "progress": progress, "review": review, "runner": runner,
            "schedule": schedule, "status": status, "store": store, "ui": ui,
            "journal_cmd": journal_cmd,
            "review_cmd": review_cmd}


# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------
_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?$")


def parse_date(text, what="日期"):
    match = _DATE.match(str(text or "").strip())
    if not match:
        raise StageError("{} 看不懂：{!r}（写成 2026-11-24 或 2026-11-24T19:30）".format(what, text))
    year, month, day, hour, minute = match.groups()
    try:
        if hour is None:
            return datetime.date(int(year), int(month), int(day)), None
        return (datetime.date(int(year), int(month), int(day)),
                datetime.time(int(hour), int(minute)))
    except ValueError:
        raise StageError("{} 不存在：{!r}".format(what, text))


class Clock:
    """The simulated wall clock: forward only."""

    def __init__(self, start_time="19:30", step_minutes=4, last=None):
        _d, start = parse_date("2000-01-01T" + start_time, "start_time")
        self.start = start
        self.step = datetime.timedelta(minutes=float(step_minutes))
        self.now = last

    def at(self, text):
        day, clock_time = parse_date(text)
        if clock_time is not None:
            moment = datetime.datetime.combine(day, clock_time)
        elif self.now is not None and self.now.date() == day:
            moment = self.now
        else:
            moment = datetime.datetime.combine(day, self.start)
        if self.now is not None and moment < self.now:
            raise StageError("时间倒退了：{} 早于上一步的 {}。步骤要按时间先后排。".format(
                moment.strftime("%Y-%m-%d %H:%M"), self.now.strftime("%Y-%m-%d %H:%M")))
        self.now = moment
        return moment

    def tick(self):
        late = datetime.datetime.combine(self.now.date(), datetime.time(23, 0))
        step = self.step if self.now + self.step <= late else datetime.timedelta(seconds=10)
        nxt = self.now + step
        if nxt.date() != self.now.date():
            nxt = datetime.datetime.combine(self.now.date(), datetime.time(23, 59, 59))
        self.now = nxt


# ---------------------------------------------------------------------------
# The stager
# ---------------------------------------------------------------------------
STEP_KEYS = {
    "profile": {"strictness", "hours", "product", "schedule", "tired", "weekly", "answers",
                "replace"},
    "pass": {"from", "to", "stations", "date", "dates", "start", "end", "days", "hints",
             "lesson_checks", "no_lesson_check", "decisions", "reviews"},
    "hint": {"station", "level", "date"},
    "check": {"target", "result", "times", "date", "decisions", "problem"},
    "session": {"date", "dates"},
    "review": {"date", "answer"},
    "due": {"count", "on", "review_day"},
    "exam-start": {"gate", "date", "seed"},
    "exam-grade": {"gate", "date", "fail"},
    "explain": {"gate", "result", "date"},
    "gate": {"gate", "date", "fail", "explain", "seed"},
    "decision": {"key", "value", "date"},
    "journal": {"date", "done", "stuck", "next", "unclear", "slow"},
    "tool": {"args", "date", "expect"},
    "git-global": {"set", "unset"},
}


class Stager:
    def __init__(self, root, verbose=False, start_time="19:30", step_minutes=4):
        self.root = Path(root)
        self.verbose = verbose
        self.lib = load_courselib(self.root)
        self.catalog = self._app(datetime.datetime(2000, 1, 1)).catalog()
        self.clock = Clock(start_time, step_minutes)
        self.clock.now = self._last_activity()

    # -- plumbing -------------------------------------------------------------
    def _console(self, sink):
        return self.lib["ui"].Console(out=sink, err=sink, can_prompt=False, is_tty=False,
                                      color=False)

    def _env(self, now):
        env = dict(os.environ)
        env["COURSE_NONINTERACTIVE"] = "1"
        env["COURSE_NOW"] = now.strftime("%Y-%m-%dT%H:%M:%S")
        return env

    def _app(self, now, sink=None):
        sink = sink if sink is not None else io.StringIO()
        return self.lib["app"].App(self.root, env=self._env(now), console=self._console(sink),
                                   now=now)

    def state(self):
        """The current state, read through the tool's store; never writes.

        Without learner/state.json this is the tool's empty state: the first
        tool command creates the file (and logs it) at its own time.
        """
        if not (self.root / "learner" / "state.json").exists():
            return self.lib["store"].empty_state()
        return self._app(self.clock.now or datetime.datetime(2000, 1, 1)).store.load()

    def _last_activity(self):
        path = self.root / "learner" / "state.json"
        if not path.exists():
            return None
        parse = self.lib["app"].parse_stamp
        moments = []
        for session in self.state().get("sessions", []):
            if isinstance(session, dict):
                moment = parse(session.get("last") or "")
                if moment is not None:
                    moments.append(moment)
        return max(moments) + datetime.timedelta(minutes=1) if moments else None

    def say(self, text):
        print(text, flush=True)

    @contextlib.contextmanager
    def forced(self, verdicts, decisions=None):
        """Replace the guarded runner for the ids in ``verdicts`` ("pass" / "fail")."""
        runner = self.lib["runner"]
        original = runner.run_check
        decisions = decisions or {}

        def fake(app, function, lesson=None, station_id=None, answers=None, scenario=None,
                 state=None, warn_unused=True, final=False):
            key = station_id or (getattr(scenario, "key", None) if scenario is not None else None)
            want = verdicts.get(key)
            if want is None:
                return original(app, function, lesson=lesson, station_id=station_id,
                                answers=answers, scenario=scenario, state=state,
                                warn_unused=warn_unused, final=final)
            if want == "pass":
                return runner.CheckResult(runner.PASSED, decisions=decisions.get(key))
            if isinstance(want, dict):
                problem = {"summary": str(want.get("summary", "")), "where": str(want.get("where", "")),
                           "detail": str(want.get("detail", "")), "recovery": str(want.get("recovery", ""))}
                return runner.CheckResult(runner.PROBLEM, problem=problem)
            try:
                real = original(app, function, lesson=lesson, station_id=station_id, answers=[],
                                scenario=scenario, state=state, warn_unused=False, final=final)
            except Exception:  # noqa: BLE001 - a question in non-interactive mode, a stop
                real = None
            if real is not None and real.outcome == runner.NOT_YET and real.counted:
                return real
            return runner.CheckResult(runner.NOT_YET)

        runner.run_check = fake
        try:
            yield
        finally:
            runner.run_check = original

    def tool(self, args, expect=(0,), verdicts=None, decisions=None):
        """Run one tool command in-process at the clock's time; return (code, output)."""
        sink = io.StringIO()
        now = self.clock.now
        app_console = self._console(sink)
        with self.forced(verdicts or {}, decisions):
            code = self.lib["cli"].main([str(a) for a in args], root=str(self.root),
                                        env=self._env(now), console=app_console, now=now)
        output = sink.getvalue()
        forced = ""
        if verdicts:
            forced = "  [判定：" + ", ".join("{}={}".format(k, v) for k, v in verdicts.items()) + "]"
        self.say("  {}  course.py {}  -> {}{}".format(now.strftime("%Y-%m-%d %H:%M"),
                                                      " ".join(str(a) for a in args), code, forced))
        if self.verbose:
            for line in output.rstrip().splitlines():
                self.say("      | " + line)
        self.clock.tick()
        if expect is not None and code not in expect:
            raise StageError("course.py {} 的退出码是 {}，预期 {}。它的输出：\n{}".format(
                " ".join(str(a) for a in args), code, list(expect), output))
        return code, output

    # -- catalogue helpers ------------------------------------------------------
    def all_stations(self):
        return [sid for lesson in self.catalog.lessons for sid in lesson.station_ids]

    def lesson_of(self, station_id):
        lesson, station = self.catalog.station(station_id)
        if lesson is None:
            raise StageError("没有这一站：{}".format(station_id))
        return lesson

    def _endpoint(self, text, first):
        text = str(text)
        lesson = self.catalog.lesson(text)
        if lesson is not None and lesson.station_ids:
            return lesson.station_ids[0] if first else lesson.station_ids[-1]
        self.lesson_of(text)
        return text

    def station_list(self, step):
        every = self.all_stations()
        if "stations" in step:
            ids = [str(s) for s in step["stations"]]
            for sid in ids:
                self.lesson_of(sid)
            return ids
        if "from" not in step or "to" not in step:
            raise StageError("pass 要写 from 和 to（或者 stations）")
        first = self._endpoint(step["from"], True)
        last = self._endpoint(step["to"], False)
        i, j = every.index(first), every.index(last)
        if j < i:
            raise StageError("pass 的 from 在 to 之后：{} … {}".format(first, last))
        return every[i:j + 1]

    # -- state helpers --------------------------------------------------------
    def record(self, state, station_id):
        return self.lib["progress"].record_of(state, station_id)

    def passed(self, state, station_id):
        return self.lib["progress"].is_done(self.record(state, station_id))

    # -- steps ----------------------------------------------------------------
    def run_steps(self, steps):
        for number, step in enumerate(steps, 1):
            if not isinstance(step, dict) or "do" not in step:
                raise StageError("第 {} 步不是 {{\"do\": ...}} 这样的对象".format(number))
            kind = step["do"]
            if kind not in STEP_KEYS:
                raise StageError("第 {} 步：不认识的 do：{!r}（可用：{}）".format(
                    number, kind, "、".join(sorted(STEP_KEYS))))
            extra = set(step) - STEP_KEYS[kind] - {"do", "note"}
            if extra:
                raise StageError("第 {} 步（{}）：不认识的键 {}".format(number, kind, sorted(extra)))
            self.say("步骤 {}：{}".format(number, kind))
            getattr(self, "step_" + kind.replace("-", "_"))(step)

    def _date_of(self, step, key="date", required=True):
        if step.get(key):
            return self.clock.at(step[key])
        if required:
            raise StageError("{} 这一步要写 {}".format(step["do"], key))
        return None

    # profile ...................................................................
    def step_profile(self, step):
        path = self.root / "learner" / "profile.md"
        if path.exists() and not step.get("replace"):
            raise StageError("learner/profile.md 已经有了；要覆盖就加 \"replace\": true")
        template = self.root / "templates" / "profile-template.md"
        headings = [line[3:].strip() for line in template.read_text(encoding="utf-8").splitlines()
                    if line.startswith("## ")]
        if len(headings) != 8:
            raise StageError("templates/profile-template.md 里不是八个小标题：{}".format(headings))
        strictness = step.get("strictness", "适中")
        if strictness not in STRICTNESS:
            raise StageError("strictness 只能是 严格 / 适中 / 宽松，不是 {!r}".format(strictness))
        hours = step.get("hours", 6)
        defaults = {
            "学习目的": "（模拟回答）按问卷的顺序：1. 自己动手写并上线；2. 看得懂并管得住 AI；3. 求职",
            "每周时间与固定时段": "（模拟回答）每周大约 {} 小时，分三次学".format(hours),
            "一次能坐多久": "（模拟回答）大约 45 分钟",
            "英文阅读": "（模拟回答）借助翻译能读",
            "GitHub": "（模拟回答）还没有账号",
            "想做的作品": "汇率看板",
            "导师严格度": strictness,
            "以前用过终端吗": "（模拟回答）没用过",
        }
        answers = dict(defaults)
        if step.get("weekly"):
            answers["每周时间与固定时段"] = str(step["weekly"])
        for key, value in (step.get("answers") or {}).items():
            if key not in headings:
                raise StageError("answers 里的 {!r} 不是模板的小标题（{}）".format(key, "、".join(headings)))
            answers[key] = str(value)
        lines = ["# 学习档案", ""]
        for heading in headings:
            lines += ["## " + heading, "", answers.get(heading, "不知道")]
            if heading == "想做的作品" and step.get("product"):
                lines += ["", "课程产品：" + str(step["product"])]
            lines.append("")
        schedule = step.get("schedule")
        if schedule:
            if schedule == "default":
                schedule = ["- 周一 20:00-20:45 学一站", "- 周三 20:00-20:45 学一站",
                            "- 周六 10:00-11:00 学两站",
                            "- 周日 20:00-20:15 复盘：先 review，再回答每周复盘的三个问题"]
            lines += ["## 每周学习时间", ""] + [str(x) for x in schedule] + [""]
        tired = step.get("tired")
        if tired:
            if tired == "default":
                tired = ["1. 有点累、还想学：换轻的，做 10 分钟复习，不开新的一站。",
                         "2. 很累：存档收工，写一句日志就停。",
                         "3. 卡住了又很累：看示范，或者直接要答案，过几天不看提示再重做一遍。"]
            lines += ["## 累了协议", ""] + [str(x) for x in tired] + [""]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
        self.say("  写好 learner/profile.md（导师严格度：{}）".format(strictness))

    # pass ......................................................................
    def _dates_for(self, step, count):
        if step.get("date"):
            return [step["date"]] * count
        if step.get("dates"):
            dates = [str(d) for d in step["dates"]]
        elif step.get("start") and step.get("end"):
            start, _t = parse_date(step["start"])
            end, _t = parse_date(step["end"])
            span = (end - start).days
            if span < 0:
                raise StageError("start 在 end 之后")
            days = int(step.get("days") or min(count, span + 1))
            days = max(1, min(days, span + 1, count))
            if days == 1:
                dates = [end.isoformat()]
            else:
                dates = [(start + datetime.timedelta(days=round(i * span / (days - 1)))).isoformat()
                         for i in range(days)]
        else:
            raise StageError("pass 要写 date、dates 或 start+end")
        k = len(dates)
        return [dates[j * k // count] for j in range(count)]

    def default_decisions(self, station_id):
        state = self.state()
        decided = state.get("decisions") or {}
        if station_id == "0.1c":
            text = (self.root / "starter" / "hello-fx" / "convert.py").read_text(encoding="utf-8")
            found = re.search(r"^AMOUNT_USD\s*=\s*([0-9_]+(?:\.[0-9]+)?)", text, re.M)
            return {"hello_fx_amount": float(found.group(1).replace("_", ""))} if found else {}
        if station_id == "0.2c":
            return {} if decided.get("workspace_location") else {"workspace_location": "not-synced"}
        if station_id == "0.3a":
            product = "汇率看板"
            profile = self.root / "learner" / "profile.md"
            if profile.exists():
                found = re.search(r"^课程产品\s*[：:]\s*(.+?)\s*$", profile.read_text(encoding="utf-8"), re.M)
                if found:
                    product = found.group(1)[:60]
            return {"course_product": product}
        if station_id == "1.6a":
            return {"commit_signing": "off"}
        if station_id == "1.11b":
            return {"commit_email": "noreply", "commit_signing": "off"}
        return {}

    def _hint_to(self, station_id, level):
        level = int(level)
        if not 0 <= level <= 4:
            raise StageError("提示级别只能是 0 到 4：{}".format(level))
        seen = self.lib["progress"].hint_level(self.record(self.state(), station_id))
        for _ in range(seen, level):
            self.tool(["hint", station_id, "--yes"])

    def _check_station(self, station_id, result, extra_decisions=None):
        decisions = {}
        if result == "pass":
            decisions = self.default_decisions(station_id)
            decisions.update(extra_decisions or {})
        expect = (0,) if result == "pass" else (1,)
        self.tool(["check", station_id], expect=expect, verdicts={station_id: result},
                  decisions={station_id: decisions})

    def _lesson_check_if_due(self, lesson, enabled, skip):
        state = self.state()
        if not enabled or lesson.id in skip:
            return
        if not all(self.passed(state, sid) for sid in lesson.station_ids):
            return
        if self.lib["status"].lesson_checked(state, lesson.id):
            return
        self.tool(["check", lesson.id])

    def step_pass(self, step):
        ids = self.station_list(step)
        state = self.state()
        todo = [sid for sid in ids if not self.passed(state, sid)]
        skipped = [sid for sid in ids if sid not in todo]
        if skipped:
            self.say("  已经通过、跳过：{}".format(" ".join(skipped)))
        if not todo:
            return
        dates = self._dates_for(step, len(todo))
        hints = {str(k): v for k, v in (step.get("hints") or {}).items()}
        for sid in hints:
            if sid not in todo:
                raise StageError("hints 里的 {} 不在这次要通过的站里".format(sid))
        decisions = {str(k): v for k, v in (step.get("decisions") or {}).items()}
        enabled = step.get("lesson_checks", True)
        skip = {str(x) for x in step.get("no_lesson_check") or ()}
        reviews = step.get("reviews")
        if reviews not in (None, False, "daily"):
            raise StageError("pass 的 reviews 只能是 \"daily\"（或者不写）")
        reviewed = set()
        for sid, day in zip(todo, dates):
            self.clock.at(day)
            if reviews and self.clock.now.date() not in reviewed:
                reviewed.add(self.clock.now.date())
                if self.lib["review"].due_count(self.state(), self.catalog, self.clock.now.date()):
                    self._session(lambda state, entry: self.lib["schedule"].RIGHT)
            if sid in hints:
                self._hint_to(sid, hints[sid])
            self._check_station(sid, "pass", decisions.get(sid))
            lesson = self.lesson_of(sid)
            if sid == lesson.station_ids[-1]:
                self._lesson_check_if_due(lesson, enabled, skip)

    # hint / check / session ...................................................
    def step_hint(self, step):
        self._date_of(step)
        self._hint_to(str(step["station"]), step.get("level", 1))

    def step_check(self, step):
        self._date_of(step)
        target = str(step["target"])
        result = step.get("result", "pass")
        if result not in ("pass", "fail", "problem"):
            raise StageError("check 的 result 只能是 pass、fail 或 problem")
        times = int(step.get("times", 1))
        if result == "problem":
            problem = step.get("problem")
            if not isinstance(problem, dict) or not str(problem.get("summary") or "").strip():
                raise StageError("result problem 要写 \"problem\": {\"summary\": ..., \"where\": ...}")
            self.lesson_of(target)
            for _ in range(times):
                self.tool(["check", target], expect=(2,), verdicts={target: problem})
            return
        lesson = self.catalog.lesson(target)
        if lesson is not None:
            state = self.state()
            verdicts = {sid: result for sid in lesson.station_ids if not self.passed(state, sid)}
            decisions = {sid: self.default_decisions(sid) for sid in verdicts} if result == "pass" else {}
            for _ in range(times):
                self.tool(["check", target], expect=(0, 1), verdicts=verdicts, decisions=decisions)
            return
        self.lesson_of(target)
        for _ in range(times):
            self._check_station(target, result, step.get("decisions"))

    def step_session(self, step):
        dates = step.get("dates") or ([step["date"]] if step.get("date") else [])
        if not dates:
            raise StageError("session 要写 date 或 dates")
        for day in dates:
            self.clock.at(day)
            self.tool(["status"])

    # reviews ..................................................................
    def _session(self, decide):
        """One review session on the clock's date, every served item answered by ``decide``."""
        review_cmd = self.lib["review_cmd"]
        stager = self

        class StagedSession(review_cmd.Session):
            served = 0

            def _serve_item(self, entry, number, total):
                result = decide(self.state, entry)
                self._record(entry, result)
                StagedSession.served += 1
                return result

        sink = io.StringIO()
        now = self.clock.now
        app = self._app(now, sink)
        session = StagedSession(app, review_cmd.Answers(app.console, []))
        code = session.run()
        app.console.flush()
        self.say("  {}  review（逐题判定）  -> {}，答了 {} 道".format(
            now.strftime("%Y-%m-%d %H:%M"), code, StagedSession.served))
        if stager.verbose:
            for line in sink.getvalue().rstrip().splitlines():
                self.say("      | " + line)
        self.clock.tick()
        return StagedSession.served

    def step_review(self, step):
        self._date_of(step)
        answer = step.get("answer", "right")
        schedule = self.lib["schedule"]
        if answer not in schedule.RESULTS:
            raise StageError("review 的 answer 只能是 right / fuzzy / wrong")
        self._session(lambda state, entry: answer)

    def _due_view(self, today):
        review = self.lib["review"]
        state = self.state()
        entries, _orphans = review.classify(state, self.catalog, today)
        return state, [e for e in entries if not e.pending]

    def step_due(self, step):
        review = self.lib["review"]
        schedule = self.lib["schedule"]
        progress = self.lib["progress"]
        count = int(step["count"])
        target, _t = parse_date(step["on"], "on")
        state = self.state()
        if step.get("review_day"):
            day, _t = parse_date(step["review_day"], "review_day")
        else:
            earlier = [d for d in progress.session_dates(state) if d < target]
            if not earlier:
                raise StageError("due：{} 以前没有学习日；先用 session 或 pass 造一个，或者写 review_day"
                                 .format(target))
            day = earlier[-1]
        if day >= target:
            raise StageError("due：review_day 要早于 on")
        self.clock.at(day.isoformat())
        away = progress.days_away(state, day)
        comeback = away is not None and away > review.LONG_BREAK_DAYS
        _state, servable = self._due_view(day)
        fixed = [e for e in servable if day < e.due <= target]
        if comeback:
            fixed += [e for e in servable if e.due <= day and e.type == "do"]
        to_answer = [e for e in servable if e.due <= day and not (comeback and e.type == "do")]
        need = count - len(fixed)
        if need < 0:
            raise StageError(
                "due：{} 道题在复习日 {} 之后、{} 当天或之前才到期（{}），复习日改不了它们，比要的 {} 道多。"
                "它们来自复习日前两天内才通过的站，或者来自更早的复习（答对后隔 7 天、21 天再到期）。"
                "把那些站提前通过、少做几次 daily 复习、换一个 review_day，或者把 count 改大。".format(
                    len(fixed), day, target, "、".join(e.id for e in fixed), count))
        if need > len(to_answer):
            raise StageError("due：到 {} 为止只有 {} 道题可以安排，凑不出 {} 道。多通过几站再试。".format(
                day, len(fixed) + len(to_answer), count))
        gap = (target - day).days
        assigned = {"due": 0}

        def new_due(box, result):
            if result == schedule.RIGHT:
                return None if box >= schedule.BOXES else schedule.interval(box + 1)
            if result == schedule.FUZZY:
                return schedule.interval(box)
            return schedule.MISS_DAYS

        def decide(state, entry):
            box = schedule.box_of(entry.record)
            if assigned["due"] < need:
                assigned["due"] += 1
                for result in (schedule.RIGHT, schedule.FUZZY):
                    if new_due(box, result) == gap:
                        return result
                return schedule.WRONG
            for result in (schedule.RIGHT, schedule.FUZZY):
                days = new_due(box, result)
                if days is None or days > gap:
                    return result
            return schedule.RIGHT

        for _round in range(40):
            _state, servable = self._due_view(day)
            left = [e for e in servable if e.due <= day and not (comeback and e.type == "do")]
            if not left:
                break
            if self._session(decide) == 0:
                break
        state = self.state()
        got = review.due_count(state, self.catalog, target)
        if got != count:
            raise StageError("due：{} 那天到期的是 {} 道，不是 {} 道（复习日 {}）。复习日和 on 隔了 {} 天；"
                             "隔 7 天以上时，答对的题也会在 on 之前再到期，这一步就做不准。"
                             "长时间没学的情况别用 due，让积压的题保持原样。".format(
                                 target, got, count, day, gap))
        self.say("  {} 到期的复习题：{} 道（{}）".format(
            target, got, "、".join(e.id for e in review.due_entries(state, self.catalog, target))))

    # gates .......................................................................
    def _open_tasks(self, gate):
        attempt = (self.state().get("exam_attempts") or {}).get(gate)
        tasks = attempt.get("tasks") if isinstance(attempt, dict) else None
        return [t for t in (tasks or []) if isinstance(t, dict)
                and t.get("result") not in ("pass", "fail")]

    def step_exam_start(self, step):
        self._date_of(step)
        self._exam_start(str(step["gate"]), step.get("seed"))

    def _exam_start(self, gate, seed=None):
        if self._open_tasks(gate):
            raise StageError("{} 已经有一场没批改完的考试；先 exam-grade，或者用 tool 跑 exam {} --new"
                             .format(gate, gate))
        args = ["exam", gate] + (["--seed", str(int(seed))] if seed is not None else [])
        self.tool(args)
        tasks = self._open_tasks(gate)
        if not tasks:
            raise StageError("exam {} 没有出题（也许实操题已经都通过了）".format(gate))
        self.say("  抽到：{}".format("、".join("{}（{}）".format(t["id"], t.get("form")) for t in tasks)))

    def step_exam_grade(self, step):
        self._date_of(step)
        self._exam_grade(str(step["gate"]), step.get("fail"))

    def _exam_grade(self, gate, fail=None):
        tasks = self._open_tasks(gate)
        if not tasks:
            raise StageError("{} 没有等着批改的考试；先 exam-start".format(gate))
        fail = {str(x) for x in fail or ()}
        known = {t["id"] for t in tasks} | {t.get("lesson") for t in tasks}
        unknown = fail - known
        if unknown:
            raise StageError("fail 里的 {} 不在这一场考试里（这一场：{}）".format(
                sorted(unknown), "、".join(t["id"] for t in tasks)))
        verdicts = {t["id"]: ("fail" if (t["id"] in fail or t.get("lesson") in fail) else "pass")
                    for t in tasks}
        expect = (1,) if "fail" in verdicts.values() else (0,)
        self.tool(["exam", gate, "--grade"], expect=expect, verdicts=verdicts)

    def step_explain(self, step):
        self._date_of(step)
        self._explain(str(step["gate"]), step.get("result", "pass"))

    def _explain(self, gate, result):
        if result not in ("pass", "again"):
            raise StageError("explain 的 result 只能是 pass 或 again")
        self.tool(["exam", gate, "--explain", result])

    def step_gate(self, step):
        self._date_of(step)
        gate = str(step["gate"])
        self._exam_start(gate, step.get("seed"))
        self._exam_grade(gate, step.get("fail"))
        if step.get("explain"):
            self._explain(gate, step["explain"])

    # decision / journal / tool ............................................
    def step_decision(self, step):
        if step.get("date"):
            self.clock.at(step["date"])
        if self.clock.now is None:
            raise StageError("decision 是第一个带时间的步骤时要写 date")
        now = self.clock.now
        app = self._app(now)
        state = app.store.load()
        state.setdefault("decisions", {})[str(step["key"])] = step["value"]
        app.store.save(state)
        self.say("  决定 {} = {!r}（通过工具的 store 保存）".format(step["key"], step["value"]))

    def step_journal(self, step):
        self._date_of(step)
        if not str(step.get("done") or "").strip():
            raise StageError("journal 要写 done")
        args = ["journal", "--done", str(step["done"])]
        nxt = step.get("next", "auto")
        if nxt == "auto":
            now = self.clock.now
            app = self._app(now)
            nxt = self.lib["journal_cmd"]._next_default(app, app.store.load())
        for key, flag in (("stuck", "--stuck"), ("unclear", "--unclear"), ("slow", "--slow")):
            if step.get(key):
                args += [flag, str(step[key])]
        if nxt:
            args += ["--next", str(nxt)]
        self.tool(args)

    def step_git_global(self, step):
        path = Path(os.environ["HOME"]) / ".gitconfig"
        if not under_temp(path):
            raise StageError("拒绝：{} 不在临时目录里".format(path))
        commands = [["--unset", str(key)] for key in step.get("unset") or ()]
        commands += [[str(key), str(value)] for key, value in (step.get("set") or {}).items()]
        if not commands:
            raise StageError("git-global 要写 set 或 unset")
        for extra in commands:
            done = subprocess.run(["git", "config", "--file", str(path)] + extra,
                                  capture_output=True, text=True)
            if done.returncode not in (0, 5):
                raise StageError("git config {} 失败：{}".format(" ".join(extra), done.stderr.strip()))
            self.say("  模拟家目录的 ~/.gitconfig：{}".format(" ".join(extra)))

    def step_tool(self, step):
        self._date_of(step)
        args = step.get("args")
        if not isinstance(args, list) or not args:
            raise StageError("tool 要写 args，例如 [\"doctor\"]")
        expect = tuple(step.get("expect") or (0,))
        self.tool(args, expect=expect)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
def ranges(ids, order):
    """Compress station ids into "0.1a–1.6a" runs along ``order``."""
    position = {sid: n for n, sid in enumerate(order)}
    ids = sorted(ids, key=lambda s: position.get(s, 10 ** 6))
    runs, start, prev = [], None, None
    for sid in ids:
        if start is None:
            start = prev = sid
        elif position.get(sid) == position.get(prev, -5) + 1:
            prev = sid
        else:
            runs.append((start, prev))
            start = prev = sid
    if start is not None:
        runs.append((start, prev))
    return ", ".join(a if a == b else "{}–{}".format(a, b) for a, b in runs) or "（无）"


def show(stager, on=None):
    lib = stager.lib
    progress, review = lib["progress"], lib["review"]
    state = stager.state()
    order = stager.all_stations()
    stations = state.get("stations") or {}
    passed = [sid for sid in order if progress.is_done(stations.get(sid))]
    print("工作区：{}".format(stager.root))
    print("通过的站（{}/{}）：{}".format(len(passed), len(order), ranges(passed, order)))
    for sid in order:
        record = stations.get(sid)
        if not isinstance(record, dict):
            continue
        notes = []
        if record.get("status") == progress.ASSISTED:
            redo = progress.redo_of(record) or {}
            notes.append("带扶手完成，重做 {}～{}{}".format(redo.get("after"), redo.get("before"),
                                                     "（已做）" if redo.get("done") else ""))
        if progress.hint_level(record):
            notes.append("提示到第 {} 级".format(progress.hint_level(record)))
        if not progress.is_done(record):
            notes.append("未通过，检查 {} 次".format(record.get("attempts") or 0))
        if notes:
            print("  {}：{}".format(sid, "；".join(notes)))
    checks = state.get("lesson_checks") or {}
    print("全课检查过的课：{}".format("、".join(sorted(checks, key=lambda x: [int(p) for p in x.split(".")])) or "（无）"))
    dates = [d.isoformat() for d in progress.session_dates(state)]
    print("学习日（{} 天）：{}".format(len(dates), "、".join(dates[-12:]) + (" …" if len(dates) > 12 else "") if dates else "（无）"))
    day = on or (progress.session_dates(state)[-1] if dates else datetime.date.today())
    due = review.due_entries(state, stager.catalog, day)
    print("{} 到期的复习题：{} 道{}".format(day, len(due), "（" + "、".join(e.id for e in due) + "）" if due else ""))
    redo = review.redo_tasks(state, stager.catalog, day)
    if redo:
        print("{} 到期的重做：{}".format(day, "、".join(t["id"] for t in redo)))
    for gate in stager.catalog.gate_ids() if callable(getattr(stager.catalog, "gate_ids", None)) else ():
        summary = progress.gate_status(stager.catalog, state, gate)
        if not summary.attempts and not summary.explain:
            continue
        print("{}：{} 场；{}实操题{}；讲解题 {}".format(
            gate, summary.attempts, "有一场没批改（{} 题）；".format(summary.next_count) if summary.in_progress else "",
            "都通过了" if summary.practical_done else "未通过的课 " + "、".join(summary.open_lessons),
            "{}（{}）".format(summary.explain, summary.explain_date) if summary.explain else "没有记录"))
    print("决定：{}".format(json.dumps(state.get("decisions") or {}, ensure_ascii=False)))
    profile = stager.root / "learner" / "profile.md"
    if profile.exists():
        text = profile.read_text(encoding="utf-8")
        found = re.search(r"^## 导师严格度\s*\n+(.+)$", text, re.M)
        extra = [name for name in ("课程产品", "## 每周学习时间", "## 累了协议") if name in text]
        print("学习档案：有（导师严格度 {}{}）".format(found.group(1).strip() if found else "?",
                                              "；" + "、".join(extra) if extra else ""))
    else:
        print("学习档案：没有")
    journal = sorted(p.name for p in (stager.root / "journal").glob("20*.md"))
    print("日志文件：{}".format("、".join(journal) or "（无）"))


# ---------------------------------------------------------------------------
# peek: run the real tool, then put learner/, journal/ and PROGRESS.md back
# ---------------------------------------------------------------------------
KEEP_PATHS = ("learner", "journal", "PROGRESS.md")


def snapshot(root):
    """Copy learner/, journal/, PROGRESS.md and the simulation's ~/.gitconfig aside."""
    backup = Path(tempfile.mkdtemp(prefix="stage-state-backup-"))
    for name in KEEP_PATHS:
        source = root / name
        if source.is_dir():
            shutil.copytree(str(source), str(backup / name), symlinks=True)
        elif source.exists():
            shutil.copy2(str(source), str(backup / name))
    gitconfig = Path(os.environ["HOME"]) / ".gitconfig"
    if gitconfig.is_file():
        shutil.copy2(str(gitconfig), str(backup / "home.gitconfig"))
    return backup


def restore(root, backup):
    """Put back what ``snapshot`` saved (and remove what did not exist then)."""
    for name in KEEP_PATHS:
        target = root / name
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(str(target))
        elif target.exists() or target.is_symlink():
            target.unlink()
        saved = backup / name
        if saved.is_dir():
            shutil.copytree(str(saved), str(target), symlinks=True)
        elif saved.exists():
            shutil.copy2(str(saved), str(target))
    saved = backup / "home.gitconfig"
    gitconfig = Path(os.environ["HOME"]) / ".gitconfig"
    if saved.is_file() and under_temp(gitconfig):
        shutil.copy2(str(saved), str(gitconfig))


def peek(root, now, tool_args, keep=False, interactive=False):
    playground = Path(os.environ["HOME"]) / "Developer" / "playground"
    before = sorted(p.name for p in playground.iterdir()) if playground.is_dir() else []
    backup = snapshot(root)
    try:
        env = dict(os.environ)
        env["COURSE_NOW"] = now
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        if not interactive:
            env["COURSE_NONINTERACTIVE"] = "1"
        completed = subprocess.run([sys.executable, "-B", str(root / "tools" / "course.py")]
                                   + list(tool_args), cwd=str(root), env=env)
        code = completed.returncode
    finally:
        if not keep:
            restore(root, backup)
        shutil.rmtree(str(backup), ignore_errors=True)
    after = sorted(p.name for p in playground.iterdir()) if playground.is_dir() else []
    print("", file=sys.stderr)
    print("[peek] 退出码 {}；{}".format(code, "保留了这次运行的改动" if keep else
                                     "learner/、journal/、PROGRESS.md 已恢复原样"), file=sys.stderr)
    new = [name for name in after if name not in before]
    if new:
        print("[peek] 注意：练习场里多了 {}（peek 不恢复练习场）".format("、".join(new)), file=sys.stderr)
    return code


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
SELF_TEST_SPEC = {
    "steps": [
        {"do": "profile", "strictness": "严格", "hours": 5, "product": "汇率看板",
         "schedule": "default", "tired": "default"},
        {"do": "pass", "from": "0.1a", "to": "0.4c", "start": "2026-11-02", "end": "2026-11-12",
         "hints": {"0.3b": 2}},
        {"do": "gate", "gate": "gate-0", "date": "2026-11-12", "explain": "pass"},
        {"do": "pass", "from": "1.1a", "to": "1.2a", "dates": ["2026-11-14", "2026-11-16"]},
        {"do": "journal", "date": "2026-11-16", "done": "做完了 1.2a", "stuck": "路径里的空格"},
        {"do": "session", "date": "2026-11-18"},
        {"do": "due", "count": 2, "on": "2026-11-20"},
    ]
}
SELF_TEST_EXPECT = (
    "先做 2 条到期的复习",
    "从 1.2b 继续",
    "你在：1.2",
)


def self_test(workspace=None):
    global OWN_WORKSPACE
    if workspace:
        OWN_WORKSPACE = Path(workspace).resolve()
    make = OWN_WORKSPACE / "tools" / "dev" / "make_sim_home.py"
    if not make.is_file():
        print("自测失败：找不到 {}".format(make))
        return 1
    sim = Path(tempfile.mkdtemp(prefix="stage-state-selftest-"))
    if not under_temp(sim):
        print("自测失败：{} 不在临时目录里".format(sim))
        return 1
    problems = []
    try:
        base_env = dict(os.environ)
        for key in ("XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "COURSE_PLAYGROUND", "COURSE_NOW"):
            base_env.pop(key, None)
        base_env["PYTHONDONTWRITEBYTECODE"] = "1"
        made = subprocess.run([sys.executable, "-B", str(make), str(sim / "s"), "--json",
                               "--workspace", str(OWN_WORKSPACE)],
                              env=base_env, capture_output=True, text=True)
        if made.returncode != 0:
            raise StageError("make_sim_home.py 失败：" + made.stderr)
        info = json.loads(made.stdout[made.stdout.index("{"):])
        home, workspace = info["home"], info["workspace"]
        env = dict(base_env, HOME=home)
        spec = sim / "spec.json"
        spec.write_text(json.dumps(SELF_TEST_SPEC, ensure_ascii=False, indent=1), encoding="utf-8")
        print("自测：模拟家目录 {}".format(sim))
        applied = subprocess.run([sys.executable, "-B", str(HERE), "apply", str(spec)], cwd=workspace,
                                 env=env, capture_output=True, text=True)
        print(applied.stdout.rstrip())
        if applied.returncode != 0:
            raise StageError("apply 失败：\n" + applied.stdout + applied.stderr)
        looked = subprocess.run([sys.executable, "-B", str(HERE), "peek", "--now", "2026-11-20T19:00",
                                 "--", "status"], cwd=workspace, env=env, capture_output=True,
                                text=True)
        print(looked.stdout.rstrip())
        if looked.returncode != 0:
            problems.append("status 的退出码是 {}".format(looked.returncode))
        for text in SELF_TEST_EXPECT:
            if text not in looked.stdout:
                problems.append("status 的输出里没有「{}」".format(text))
        state = json.loads((Path(workspace) / "learner" / "state.json").read_text(encoding="utf-8"))
        dates = sorted({s["date"] for s in state["sessions"]})
        if "2026-11-20" in dates:
            problems.append("peek 没有恢复 state.json（11-20 成了学习日）")
        if dates[-1] != "2026-11-18":
            problems.append("最后一个学习日是 {}，不是 2026-11-18".format(dates[-1]))
        if state.get("explain", {}).get("gate-0", {}).get("result") != "pass":
            problems.append("gate-0 的讲解题没有记为 pass")
        if state["stations"].get("0.3b", {}).get("highest_hint") != 2:
            problems.append("0.3b 的提示级别不是 2")
        shown = subprocess.run([sys.executable, "-B", str(HERE), "show", "--on", "2026-11-20"],
                               cwd=workspace, env=env, capture_output=True, text=True)
        print(shown.stdout.rstrip())
        if shown.returncode != 0:
            problems.append("show 失败：" + shown.stderr)
        stray = [str(p) for p in OWN_WORKSPACE.rglob("__pycache__")]
        if stray:
            problems.append("学习工作区里出现了 __pycache__：{}".format(stray))
    except (StageError, ValueError, KeyError, OSError) as exc:
        problems.append(str(exc))
    finally:
        if under_temp(sim):
            shutil.rmtree(str(sim), ignore_errors=True)
    if os.path.exists(str(sim)):
        problems.append("模拟家目录没删掉：{}".format(sim))
    if problems:
        print("自测失败：")
        for problem in problems:
            print("  - " + problem)
        return 1
    print("自测通过（模拟家目录已删除）。")
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def read_spec(source):
    text = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    try:
        spec = json.loads(text)
    except ValueError as exc:
        raise StageError("spec 不是合法的 JSON：{}".format(exc))
    if isinstance(spec, list):
        spec = {"steps": spec}
    if not isinstance(spec, dict) or not isinstance(spec.get("steps"), list):
        raise StageError("spec 要么是步骤的列表，要么是带 steps 的对象")
    extra = set(spec) - {"steps", "start_time", "minutes_per_command"}
    if extra:
        raise StageError("spec 里不认识的键：{}".format(sorted(extra)))
    return spec


def main(argv=None):
    parser = argparse.ArgumentParser(prog="stage_state.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--self-test", action="store_true", help="build a simulation home, stage, check, remove it")
    parser.add_argument("--workspace", help="with --self-test: the workspace to copy (default: the one this file is in)")
    parser.add_argument("--help-spec", action="store_true", help="print the spec format")
    sub = parser.add_subparsers(dest="command")
    p_apply = sub.add_parser("apply", help="stage the steps of a JSON spec (a file or - for stdin)")
    p_apply.add_argument("spec")
    p_apply.add_argument("--verbose", action="store_true", help="also print every tool output")
    p_show = sub.add_parser("show", help="summary of the staged state")
    p_show.add_argument("--on", help="date for the review count (default: last study day)")
    p_peek = sub.add_parser("peek", help="run course.py with COURSE_NOW, then restore the learner files")
    p_peek.add_argument("--now", required=True, help="COURSE_NOW, e.g. 2026-11-26 or 2026-11-26T19:30")
    p_peek.add_argument("--keep", action="store_true", help="keep what the command changed")
    p_peek.add_argument("--interactive", action="store_true", help="do not set COURSE_NONINTERACTIVE=1")
    p_peek.add_argument("tool_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.help_spec:
        print(SPEC_HELP.strip("\n"))
        return 0
    if args.self_test:
        return self_test(args.workspace)
    if not args.command:
        parser.print_help()
        return 2
    try:
        root = guarded_root()
        clean_environment()
        if args.command == "peek":
            tool_args = list(args.tool_args)
            if tool_args[:1] == ["--"]:
                tool_args = tool_args[1:]
            if not tool_args:
                raise StageError("peek 后面要写工具的参数，例如 peek --now 2026-11-26 -- status")
            parse_date(args.now, "--now")
            return peek(root, args.now, tool_args, keep=args.keep, interactive=args.interactive)
        if args.command == "show":
            stager = Stager(root)
            on = parse_date(args.on, "--on")[0] if args.on else None
            show(stager, on)
            return 0
        spec = read_spec(args.spec)
        backup = snapshot(root)
        try:
            stager = Stager(root, verbose=args.verbose,
                            start_time=spec.get("start_time", "19:30"),
                            step_minutes=spec.get("minutes_per_command", 4))
            stager.run_steps(spec["steps"])
        except BaseException as exc:
            restore(root, backup)
            if not isinstance(exc, StageError):
                import traceback
                traceback.print_exc()
            print("stage_state.py：" + (str(exc) if isinstance(exc, StageError) else repr(exc)),
                  file=sys.stderr)
            print("stage_state.py：失败，learner/、journal/、PROGRESS.md 和模拟家目录的 ~/.gitconfig "
                  "已恢复到 apply 之前（练习场里新搭的考题文件夹不会删）。", file=sys.stderr)
            return 2
        finally:
            shutil.rmtree(str(backup), ignore_errors=True)
        print("")
        show(stager)
        return 0
    except StageError as exc:
        print("stage_state.py：" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
