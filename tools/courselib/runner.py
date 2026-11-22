"""The guarded check runner and the three outcomes (plan I4).

``run_check`` calls one check function and always comes back with exactly one
of three outcomes:

- ``passed``   通过 (exit code 0)
- ``not_yet``  还没达标 (exit code 1): where the tool looked, what it saw, what
               is still missing; never the solution
- ``problem``  检查器出问题 (exit code 2): the check function raised, returned
               without a conclusion, or the environment is broken.  The
               learner is told it is not their fault.

A traceback is never printed.  It is kept in the result (``problem["detail"]``)
so that it reaches learner/last-result.json for the tutor, with every home
folder (HOME and the login account's home, each as given and as resolved
through links) written as ``~`` (``App.scrub``).  The block the learner copies
to the tutor is scrubbed the same way.

The same runner serves station checks, the checks of ``do`` review items and
exam grading functions.
"""

import io
import traceback

from .catalog import describe_exception
from .context import CheckContext
from .errors import (
    EXIT_NOT_YET,
    EXIT_OK,
    EXIT_PROBLEM,
    Cancelled,
    CheckStop,
    ToolTrouble,
    UsageProblem,
)
from .ui import BAD_MARK, OK_MARK, WARN_MARK, captured, tutor_box

PASSED = "passed"
NOT_YET = "not_yet"
PROBLEM = "problem"

EXIT_CODES = {PASSED: EXIT_OK, NOT_YET: EXIT_NOT_YET, PROBLEM: EXIT_PROBLEM}

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    PASSED: "通过",
    NOT_YET: "还没达标",
    PROBLEM: "检查器出问题",
    "done_head": "已经做到：",
    "missing_head": "还差 {n} 处：",
    "where": "看了哪里：",
    "saw": "看到了什么：",
    "missing": "还缺什么：",
    "notes_head": "补充：",
    "not_your_fault": "这不是你的错。把下面这段原样发给导师：",
    "box_place": "位置：{place}",
    "box_problem": "问题：{summary}",
    "box_where": "出处：{where}",
    "box_time": "时间：{time}",
    "box_detail": "详情：learner/last-result.json",
    "recovery": "可以先这样处理：{recovery}",
    "check_raised": "检查函数出错了：{what}",
    "no_conclusion": "检查函数运行完了，但没有给出任何结论（既没有 ok 也没有 fail）",
    "not_callable": "这一站的检查不是一个可以调用的函数",
    "extra_answers": "多给了 {n} 个 --answer，没有用上。",
}


class CheckResult:
    """The outcome of one check run."""

    def __init__(self, outcome, oks=(), fails=(), notes=(), asked=(), decisions=None,
                 interactive=False, problem=None, printed="", answers_used=0,
                 counted=True):
        self.outcome = outcome
        self.oks = list(oks)
        self.fails = list(fails)
        self.notes = list(notes)
        self.asked = list(asked)
        self.decisions = dict(decisions or {})
        self.interactive = bool(interactive)
        self.problem = problem
        self.printed = printed
        #: how many of the answers given on the command line this check consumed
        self.answers_used = int(answers_used)
        #: False when the check could not start (a scenario it needs is not
        #: built yet): the outcome is 还没达标, but it is not an attempt.
        self.counted = bool(counted)

    @property
    def passed(self):
        return self.outcome == PASSED

    @property
    def exit_code(self):
        return EXIT_CODES[self.outcome]

    def to_dict(self):
        """A JSON-ready dict (for learner/last-result.json and the log)."""
        data = {
            "outcome": self.outcome,
            "outcome_text": TEXT[self.outcome],
            "exit_code": self.exit_code,
            "ok": self.oks,
            "missing": self.fails,
            "notes": self.notes,
            "asked": self.asked,
            "interactive": self.interactive,
            "counted": self.counted,
        }
        if self.problem:
            data["problem"] = self.problem
        if self.printed:
            data["printed_by_check"] = self.printed
        return data


def make_problem(app, exc, source=""):
    """Turn an exception into the ``problem`` dict of a result."""
    if isinstance(exc, ToolTrouble):
        return {"summary": app.scrub(exc.summary), "where": app.scrub(exc.where),
                "detail": app.scrub(exc.detail), "recovery": exc.recovery}
    filename = str(source) if source else ""
    line = 0
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == filename:
            line = frame.lineno or 0
    where = ""
    if filename:
        where = app.rel(filename) + (f" 第 {line} 行" if line else "")
    detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    summary = TEXT["check_raised"].format(what=describe_exception(exc, filename))
    return {"summary": app.scrub(summary), "where": where, "detail": app.scrub(detail),
            "recovery": ""}


def run_check(app, function, lesson=None, station_id=None, answers=None,
              scenario=None, state=None, warn_unused=True, final=False):
    """Run ``function(ctx)`` under guard and return a ``CheckResult``.

    ``answers`` is a list of answers given on the command line (used before
    the learner is asked; the list itself is not changed, see
    ``result.answers_used``); ``scenario`` is a ``ScenarioInfo`` to bind for
    ``do`` items and exam tasks; ``state`` is the loaded state dict;
    ``warn_unused=False`` drops the remark about answers that were not needed;
    ``final=True`` sets ``ctx.final`` (an exam task: a wrong answer is final
    for this attempt, so ``ask`` and ``quiz`` do not suggest running it again).

    Only two things escape: ``Cancelled`` (the learner left a prompt) and
    ``UsageProblem`` (an answer was needed in non-interactive mode).
    """
    ctx = CheckContext(app, lesson=lesson, station_id=station_id, answers=answers,
                       scenario=scenario, state=state)
    ctx.final = bool(final)
    source = lesson.path if lesson is not None else ""
    problem = None
    sink = io.StringIO()
    try:
        if not callable(function):
            raise ToolTrouble(TEXT["not_callable"])
        with captured(sink):
            function(ctx)
    except CheckStop:
        pass
    except (Cancelled, UsageProblem):
        raise
    except KeyboardInterrupt:
        raise Cancelled()
    except BaseException as exc:  # noqa: BLE001 - whatever lesson code raises, even SystemExit
        problem = make_problem(app, exc, source)
        if not problem.get("where") and lesson is not None:
            problem["where"] = app.rel(lesson.path)
    notes = list(ctx.notes)
    if problem is None and not ctx.fails and not ctx.oks:
        problem = {"summary": TEXT["no_conclusion"],
                   "where": app.rel(lesson.path) if lesson is not None else "",
                   "detail": "", "recovery": ""}
    if ctx._answers and warn_unused:
        notes.append(TEXT["extra_answers"].format(n=len(ctx._answers)))
    if problem is not None:
        outcome = PROBLEM
    elif ctx.fails:
        outcome = NOT_YET
    else:
        outcome = PASSED
    return CheckResult(outcome, oks=ctx.oks, fails=ctx.fails, notes=notes, asked=ctx.asked,
                       decisions=ctx.decisions, interactive=ctx.interactive,
                       problem=problem, printed=app.scrub(sink.getvalue())[:4000],
                       answers_used=ctx.answers_used,
                       counted=not (outcome == NOT_YET and ctx.not_ready))


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def headline(console, outcome, heading):
    """The first line of an outcome: mark, outcome word, what was checked."""
    mark, kind = {PASSED: (OK_MARK, "ok"), NOT_YET: (BAD_MARK, "bad"),
                  PROBLEM: (WARN_MARK, "warn")}[outcome]
    text = f"{mark} {TEXT[outcome]}"
    if heading:
        text += " · " + heading
    return console.paint(text, kind)


def render_problem(app, heading, problem, place=""):
    """Lines for 检查器出问题: a block the learner can copy to the tutor."""
    lines = [headline(app.console, PROBLEM, heading), "",
             "  " + TEXT["not_your_fault"], ""]
    box = []
    if place:
        box.append(TEXT["box_place"].format(place=place))
    box.append(TEXT["box_problem"].format(summary=problem.get("summary", "")))
    if problem.get("where"):
        box.append(TEXT["box_where"].format(where=problem["where"]))
    box.append(TEXT["box_time"].format(time=app.now.strftime("%Y-%m-%d %H:%M")))
    if problem.get("detail"):
        box.append(TEXT["box_detail"])
    lines.append(tutor_box([app.scrub(line) for line in box]))
    if problem.get("recovery"):
        lines += ["", "  " + app.scrub(TEXT["recovery"].format(recovery=problem["recovery"]))]
    return lines


def render_result(app, result, heading, place=""):
    """Lines that show ``result`` to the learner (no trailing advice)."""
    if result.outcome == PROBLEM:
        return render_problem(app, heading, result.problem or {}, place=place)
    lines = [headline(app.console, result.outcome, heading)]
    if result.oks:
        lines += ["", "  " + TEXT["done_head"]]
        lines += ["    - " + text for text in result.oks]
    if result.fails:
        lines += ["", "  " + TEXT["missing_head"].format(n=len(result.fails))]
        for number, fail in enumerate(result.fails, 1):
            rows = []
            if fail.get("where"):
                rows.append(TEXT["where"] + fail["where"])
            if fail.get("saw"):
                rows.append(TEXT["saw"] + fail["saw"])
            rows.append(TEXT["missing"] + fail.get("missing", ""))
            lines.append(f"    {number}. {rows[0]}")
            lines += ["       " + row for row in rows[1:]]
    if result.notes:
        lines += ["", "  " + TEXT["notes_head"]]
        lines += ["    - " + text for text in result.notes]
    return lines
