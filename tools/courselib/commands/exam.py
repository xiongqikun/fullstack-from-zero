"""``exam``: the cold practical of one gate, and its explain-back verdict (plan I4, I7).

``exam <gate>`` builds the tasks of one sitting (场) with randomised names and
prints them, with no hints.  ``exam <gate> --grade`` grades every task through
the same guarded runner as ``check`` (``runner.run_check(..., final=True)``)
and records the result per task.  ``exam <gate> --explain pass|again`` records
the tutor's verdict on the explain-back questions (讲解题).

The rule of a gate (COMMON.md section 1; the functions are in
``courselib.progress``, the pool in ``Catalog.gate_pool``):

- A gate covers the lessons whose ``EXAM`` tasks name it (``"gate": "gate-b"``)
  and that have at least one usable task.  gate-1 covers 1.11 to 1.16; no
  gate borrows tasks of another gate.
- One sitting holds one task for each of those lessons, in lesson order, at
  most ``progress.GATE_MAX_TASKS``; for a lesson with two tasks one is drawn.
- A lesson is covered once one of its tasks has been passed.  The practical
  part is passed when every lesson of the gate is covered.
- A sitting after an unsuccessful one (补考) holds only the lessons not
  covered yet: the task that was not passed comes back in its other form.
- The gate is passed when the practical part is passed and the explain-back
  verdict ``state["explain"][gate]`` is ``{"result": "pass", "date": ...}``.
- Tasks never drawn are extra practice.  ``--all`` starts a full sitting
  (one task per lesson, preferring tasks never drawn) at any time; after the
  practical part is passed that is the one way to practise more, and its
  results never take a passed lesson back.

One sitting is an *attempt*, kept in ``state["exam_attempts"][gate]``::

    {"attempt": 2, "kind": "full" | "retest" | "again" | "practice",
     "started": "...",
     "tasks": [{"id": "1.6-x1", "lesson": "1.6", "form": "B", "seed": 41237,
                "minutes": 5, "folder": "exam-gate-b/1.6-x1",
                "result": None | "pass" | "fail" | "problem",
                "graded": None | "..."}],
     "forms": {"1.6-x1": "B"}}

- Forms alternate per task across sittings: the first time A, then B, then A.
- Every task is built with a fresh seed, stored with the attempt, in its own
  folder ``<playground>/exam-<gate>/<task id>`` (rebuilt with the safety rules
  of ``courselib.scenario``: only folders carrying the ``.playground`` marker
  are ever deleted).
- Running ``exam <gate>`` again while a sitting is open shows the same tasks
  again; it never rebuilds them (that would destroy the learner's work).
  ``--new`` gives up the open sitting and starts a new one.
- The task list shows the filled task text, the builder's todo lines, the
  task folder and a ``cd`` line for it.  The ``cd`` line is left out when the
  text or a todo line already contains ``cd `` or says 「进入 <a folder inside
  the task folder>」 (the rule of the scenario command, tool-api 15.1).
- ``--grade`` grades the tasks of the open sitting that have no result yet,
  or whose grading broke (检查器出问题).  A task graded pass or fail is not
  graded again: an exam is cold, a fail is answered by the next sitting.

Results per task go to ``state["exams"][gate][task_id]`` (plan I5: form,
result, date; plus seed, attempt, title, lesson and history).  Only pass and
fail are recorded there; a grading problem is not the learner's result.
"""

import random

from .. import cmdkit, progress, runner, syllabus
from .. import scenario as scenarios
from ..catalog import syllabus_gate_lessons, usable_exam_task
from ..errors import (
    EXIT_NOT_YET,
    EXIT_OK,
    EXIT_PROBLEM,
    Refused,
    ToolTrouble,
    UsageProblem,
)
from ..normalize import normalize
from ..status import EXPLAIN_MINUTES as STATUS_EXPLAIN_MINUTES
from ..status import TEXT as STATUS_TEXT
from ..status import gate_state_words
from ..ui import display_width, pad

#: At most this many tasks in one sitting (one per lesson of the gate).
MAX_TASKS = progress.GATE_MAX_TASKS
FORMS = ("A", "B")
#: Minutes the explain-back questions take (COMMON.md section 1).
EXPLAIN_MINUTES = STATUS_EXPLAIN_MINUTES

PASS = progress.GATE_PASS
FAIL = progress.GATE_FAIL
PROBLEM = "problem"
RESULT_OF = {runner.PASSED: PASS, runner.NOT_YET: FAIL, runner.PROBLEM: PROBLEM}

SUMMARY = "关卡考试：不带提示的实操题，和讲解题的结果"
DESCRIPTION = """关卡考试：每课一道不带提示的实操题，检验你能不能不看课文、不要提示，自己把事情做出来。

  python3 tools/course.py exam gate-b                   开始一场考试（搭好考题并显示题目）
  python3 tools/course.py exam gate-b --grade           做完以后批改
  python3 tools/course.py exam gate-b --explain pass    记下讲解题的结果（要再来一次就写 again）
  python3 tools/course.py exam                          看看有哪些关卡、各自考到哪一步

一场考试里，这个关卡的每一课各出一题。每一课有一题通过，实操题就算过了；
没通过的课，准备好以后再运行 exam 补考：只考这些课，没通过的题换另一套题面。
实操题都通过以后，对导师说“请问我 <关卡> 的讲解题”；导师判断以后用 --explain 记下结果。
实操题和讲解题都通过，这个关卡就通过了。"""

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "gate_help": "关卡编号：gate-0、gate-a、gate-b 或 gate-1",
    "grade_help": "批改这一场考试，记下每道题的结果",
    "new_help": "放弃还没批改的这一场，重新出一场（会换题面、重新搭文件夹）",
    "all_help": "完整考一场：每课一题，已经通过的课也算在内，优先出你还没做过的题（实操题都通过以后，用它加练）",
    "explain_help": "记下讲解题的结果：导师判断通过写 pass，要再来一次写 again",
    "answer_help": "提前给出批改时要回答的问题，按提问顺序",
    "seed_help": "给测试用：固定出题的随机数",
    "grade_and_more": "--grade 不能和 --new、--all、--explain 一起用。",
    "explain_and_more": "--explain 不能和 --new、--all 一起用。",
    # names
    "kind_small": syllabus.GATE_KIND_SMALL,
    "kind_stage": syllabus.GATE_KIND_STAGE,
    "kind_other": syllabus.GATE_KIND_OTHER,
    # listing
    "list_head": "关卡（{n} 个）：",
    "list_line": "  {gate}  {title}（{range}）：{state}",
    # The state words are shared with PROGRESS.md (``status.gate_state_words``).
    "list_none": STATUS_TEXT["gate_none"],
    "list_new": STATUS_TEXT["gate_new"],
    "list_partly": STATUS_TEXT["gate_partly"],
    "list_open": STATUS_TEXT["gate_open"],
    "list_practical": STATUS_TEXT["gate_practical"],
    "list_done": STATUS_TEXT["gate_done"],
    "list_done_undated": STATUS_TEXT["gate_done_undated"],
    "list_usage": "开始一个关卡的考试：python3 tools/course.py exam <关卡>，例如 python3 tools/course.py exam {example}",
    "range": "{first} 到 {last} 课",
    "range_one": "{first} 课",
    "unknown_gate": "没有「{text}」这个关卡。",
    "known_gates": "可以用的关卡：{gates}",
    # no tasks
    "no_tasks": "{name}「{title}」的考题还没有写好：{lessons}的课程里还没有一道考题。",
    "no_tasks_next": "这不是你的问题，也不影响你继续往下学。考题写好以后再运行这条命令就行。",
    # starting
    "head": "关卡考试 · {label}",
    "head_attempt": "第 {n} 场",
    "head_retest": "第 {n} 场 · 补考：只考还没通过的课，每课一题，没通过的题换成另一套题面",
    "head_again": "第 {n} 场 · 完整的一场：每课一题，已经通过的课也再考一次",
    "head_practice": "第 {n} 场 · 加练：实操题你已经通过了，这一场的结果不会让通过的课退回去",
    "count": "一共 {n} 题，每课一题，预计 {minutes} 分钟（每题的预计分钟数加起来）。",
    "count_explain": "实操题都通过以后还有讲解题，约 {minutes} 分钟：导师问你几个问题，请你讲出“为什么这样做”。",
    # The head of an extra practice sitting, practical part passed, explain-back not yet.
    "count_explain_due": "讲解题还差一次，约 {minutes} 分钟：对导师说“请问我 {gate} 的讲解题”。",
    "too_few": "这个关卡的考题还没写全：{lessons} 课还没有考题，这一场先考已经写好的 {n} 题。",
    "rules_head": "考试规则：",
    "rule_1": "这是不带提示的实操：考试期间没有提示，先别问导师或 AI。",
    "rule_2": "每道题都在练习场里自己的文件夹里做，改坏了也没关系，不会影响你自己的文件。",
    "rule_3": "做不出来的题空着就行。批改以后会告诉你该练什么，准备好再补考。",
    "task_head": "第 {number} 题 · {title}（约 {minutes} 分钟）",
    "task_folder": "这道题的文件夹：{path}",
    "task_cd": "先进入这道题的文件夹：cd {path}。题目里说的文件夹如果在它里面，再 cd 进那一层。",
    "task_graded": "第 {number} 题 · {title}：已批改（{result}）",
    "task_missing": "这道题的文件夹不见了或者不完整：{path}。要整场重来：python3 tools/course.py exam {gate} --new",
    "task_gone": "第 {number} 题（{id}）：课程里已经找不到这道题了，批改时会跳过它。",
    "finish_head": "做完以后（或者做不下去了），回到学习工作区批改：",
    "finish_cd": "cd {workspace}",
    "finish_grade": "python3 tools/course.py exam {gate} --grade",
    "open_again": "这一场考试还有题没批改，上面是同一批题目，你已经做的改动都还在。想放弃这一场重新出题：python3 tools/course.py exam {gate} --new",
    "skipped_bad": "有 {n} 道考题写得不完整，这次没有用上（导师可以运行 python3 tools/course.py validate 查看）：{ids}",
    "build_failed_head": "第 {number} 题（{id}）搭建失败，这一场先不考它。",
    "all_build_failed": "这一场的考题一道都没能搭好。",
    # the state of the gate
    "gate_passed": "{name} 通过了：实操题每课都有一题通过，讲解题也记为通过（{date}）。",
    "gate_passed_undated": "{name} 通过了：实操题每课都有一题通过，讲解题也记为通过。",
    "explain_needed": (
        "实操题都通过了。还差讲解题：对导师说“请问我 {gate} 的讲解题”。"
        "导师判断以后，用这条命令记下结果：python3 tools/course.py exam {gate} --explain pass"
        "（要再来一次就写 again）"
    ),
    "extra_practice": (
        "没抽到的题算加练，不做也不影响通过。想加练一场（每课一题，优先出你还没做过的题，"
        "结果不会让通过的课退回去）：python3 tools/course.py exam {gate} --all"
    ),
    "lessons_left": "还有 {n} 课这一场没考到：{lessons}。接着考：python3 tools/course.py exam {gate}",
    # grading
    "no_attempt": "{gate} 还没有开始考试，没有可以批改的题。先运行：python3 tools/course.py exam {gate}",
    "closed": "{gate} 第 {n} 场考试已经批改过了：{summary}。",
    "closed_next": "还没通过的课可以补考（每课一题，没通过的题换另一套题面）：python3 tools/course.py exam {gate}",
    "closed_done": "这一场全部通过了。",
    "grade_head": "批改 · {label} · 第 {n} 场",
    "grade_task": "第 {number} 题 {title}",
    "missing_where": "考题文件夹 {path}",
    "missing_saw": "文件夹不在了，或者不是工具搭的那一份",
    "missing_missing": "考题要在工具搭好的文件夹里完成",
    "gone_summary": "课程里已经找不到这道考题：{id}",
    "summary_line": "通过 {passed}/{total} 题",
    "summary_problem": "，{n} 题检查器出问题",
    "result_pass": "通过",
    "result_fail": "还没达标",
    "result_problem": "检查器出问题",
    "result_none": "还没批改",
    "result_head": "这一场的结果：{summary}",
    "passed_all": "这一场的题全部通过了。",
    "practice_head": "接下来练什么：",
    "practice_line": "{lesson} 课「{lesson_title}」：{title}",
    "practice_only": "这是加练：通过的课不会退回去。",
    "retest": "练好以后补考：python3 tools/course.py exam {gate}。补考只考还没通过的 {n} 课，每课一题，没通过的题换另一套题面。",
    "problem_note": "有 {n} 题的检查器出了问题，这不是你的错：把上面的框发给导师。修好以后再运行 python3 tools/course.py exam {gate} --grade，只会重批这几题。",
    "regrade_only": "这次只重批上次检查器出问题的 {n} 题。",
    "unused_answers": "多给了 {n} 个 --answer，没有用上。",
    # explain-back
    "explain_too_early": (
        "{gate} 还没有批改过一场考试，现在还不能记讲解题的结果。"
        "先考实操题：python3 tools/course.py exam {gate}，做完批改：python3 tools/course.py exam {gate} --grade"
    ),
    "explain_pass": "讲解题的结果记下了：通过（{date}）。",
    "explain_again": "讲解题记为“再来一次”：准备好了再对导师说“请问我 {gate} 的讲解题”。",
    "explain_withdrawn": "之前记的是“通过”（{date}），现在改成了“再来一次”：{name} 现在还没通过。",
    "explain_kept": "讲解题的“通过”先记着：等实操题每课都有一题通过，{name} 就通过了。",
    "explain_practical_left": "实操题还有 {n} 课没通过：{lessons}。补考：python3 tools/course.py exam {gate}",
}


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "exam", SUMMARY, description=DESCRIPTION)
    parser.add_argument("gate", nargs="?", metavar="<关卡>", help=TEXT["gate_help"])
    parser.add_argument("--grade", action="store_true", help=TEXT["grade_help"])
    parser.add_argument("--new", action="store_true", help=TEXT["new_help"])
    parser.add_argument("--all", action="store_true", help=TEXT["all_help"])
    parser.add_argument("--explain", type=_explain_word, choices=progress.EXPLAIN_RESULTS,
                        metavar="<pass 或 again>",
                        help=TEXT["explain_help"])
    parser.add_argument("--answer", action="append", default=[], metavar="<回答>",
                        help=TEXT["answer_help"])
    parser.add_argument("--seed", type=int, metavar="<数字>", help=cmdkit.argparse.SUPPRESS)
    return parser


def _explain_word(text):
    """--explain PASS, ｐａｓｓ or "pass　" mean pass (the gate id is folded the same way)."""
    return normalize(text)


def run(args):
    app = args.app
    if not args.gate:
        return _list(app)
    gate = _gate(app, args.gate)
    explain = getattr(args, "explain", None)
    if args.grade and (args.new or args.all or explain):
        raise UsageProblem(TEXT["grade_and_more"])
    if explain and (args.new or args.all):
        raise UsageProblem(TEXT["explain_and_more"])
    state = app.store.load()
    progress.touch_session(state, app.now)
    if explain:
        return _explain(app, state, gate, explain)
    if args.grade:
        return _grade(app, state, gate, [str(a) for a in args.answer])
    return _start(app, state, gate, new=args.new, everything=args.all, seed=args.seed)


# ---------------------------------------------------------------------------
# Gates, their names and their tasks
# ---------------------------------------------------------------------------
def _gate(app, text):
    gate = cmdkit.clean_id(text)
    if gate in app.catalog().gate_ids():
        return gate
    raise UsageProblem(TEXT["unknown_gate"].format(text=str(text).strip()),
                       suggestion=TEXT["known_gates"].format(gates="、".join(syllabus.GATES)))


def _title(gate):
    return syllabus.GATES.get(gate, {}).get("title", "")


def kind_of(gate):
    """「阶段验收」 for gate-1, gate-2 ...; 「小关卡」 for the other gates of the syllabus."""
    return syllabus.gate_kind(gate)


def gate_name(gate):
    """The gate as a sentence names it: 「小关卡 gate-b」, 「阶段验收 gate-1」."""
    return syllabus.gate_name(gate)


def _label(gate):
    """The gate in a heading: 「小关卡 gate-b「本地 Git 关卡」」, 「gate-1「阶段 1 验收」」."""
    return syllabus.gate_label(gate)


def _titled(gate):
    """The title in the listing: 「起步小关卡」, 「小关卡「终端与文档关卡」」, 「关卡」."""
    return syllabus.gate_titled(gate)


def _range_of(lesson_ids):
    if not lesson_ids:
        return ""
    if len(lesson_ids) == 1:
        return TEXT["range_one"].format(first=lesson_ids[0])
    return TEXT["range"].format(first=lesson_ids[0], last=lesson_ids[-1])


def _pool(app, gate):
    """``(primary, pool, unusable)``: the gate's tasks as ``(lesson, task)`` and as ids."""
    primary, _secondary, unusable = app.catalog().gate_pool(gate)
    return primary, [(lesson.id, task["id"]) for lesson, task in primary], unusable


def _find_task(app, task_id):
    for lesson, task in app.catalog().exam_tasks():
        if task.get("id") == task_id and usable_exam_task(task):
            return lesson, task
    return None, None


def _status(app, state, gate):
    return progress.gate_status(app.catalog(), state, gate)


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------
def _list(app):
    out = app.console.out
    catalog = app.catalog()
    state = app.store.load()
    gates = catalog.gate_ids()
    out(TEXT["list_head"].format(n=len(gates)))
    width = max([display_width(gate) for gate in gates] or [0])
    for gate in gates:
        summary = progress.gate_status(catalog, state, gate)
        out(TEXT["list_line"].format(
            gate=pad(gate, width), title=_titled(gate),
            range=_range_of(catalog.gate_lesson_ids(gate)) or "-",
            state=_state_words(summary)))
    out("")
    out(TEXT["list_usage"].format(example=gates[0] if gates else "gate-0"))
    return EXIT_OK


def _state_words(summary):
    """Where one gate stands, in a few words for the listing (``status.gate_state_words``)."""
    return gate_state_words(summary)


# ---------------------------------------------------------------------------
# What the state of a gate means for the learner
# ---------------------------------------------------------------------------
def _passed_lines(gate, summary):
    """The lines for a gate whose practical part is passed."""
    if summary.done:
        if summary.explain_date:
            return [TEXT["gate_passed"].format(name=gate_name(gate), date=summary.explain_date)]
        return [TEXT["gate_passed_undated"].format(name=gate_name(gate))]
    return [TEXT["explain_needed"].format(gate=gate)]


def _lesson_list(lesson_ids):
    return "、".join(lesson_ids)


# ---------------------------------------------------------------------------
# Starting a sitting
# ---------------------------------------------------------------------------
def _attempts(state):
    attempts = state.get("exam_attempts")
    if not isinstance(attempts, dict):
        attempts = {}
        state["exam_attempts"] = attempts
    return attempts


def _results(state, gate):
    exams = state.setdefault("exams", {})
    results = exams.get(gate)
    if not isinstance(results, dict):
        results = {}
        exams[gate] = results
    return results


def _graded(results):
    """True when at least one task of the gate has a recorded pass or fail."""
    return any(isinstance(r, dict) and r.get("result") in (PASS, FAIL)
               for r in (results or {}).values())


def _is_open(attempt):
    tasks = attempt.get("tasks") if isinstance(attempt, dict) else None
    if not isinstance(tasks, list) or not tasks:
        return False
    return any(isinstance(t, dict) and t.get("result") not in (PASS, FAIL) for t in tasks)


def _next_form(attempt, results, task_id):
    """The form a task is shown in next: the other one than last time."""
    forms = attempt.get("forms") if isinstance(attempt, dict) else None
    last = forms.get(task_id) if isinstance(forms, dict) else None
    if last not in FORMS:
        record = results.get(task_id)
        last = record.get("form") if isinstance(record, dict) else None
    if last not in FORMS:
        return FORMS[0]
    return FORMS[1] if last == FORMS[0] else FORMS[0]


def draw(plan, rng):
    """One task id per lesson of ``plan`` (``[(lesson_id, [task ids])]``), in its order."""
    return [ids[0] if len(ids) == 1 else rng.choice(ids) for _lesson_id, ids in plan if ids]


def _start(app, state, gate, new=False, everything=False, seed=None):
    out = app.console.out
    attempts = _attempts(state)
    previous = attempts.get(gate) if isinstance(attempts.get(gate), dict) else {}
    if _is_open(previous) and not new:
        app.store.save(state)
        _show(app, state, gate, previous, reopened=True)
        return EXIT_OK

    primary, pool, unusable = _pool(app, gate)
    if not primary:
        app.store.save(state)
        out(TEXT["no_tasks"].format(name=gate_name(gate), title=_title(gate) or gate,
                                    lessons=_range_of(syllabus_gate_lessons(gate)) or gate))
        out(TEXT["no_tasks_next"])
        app.store.log("exam-no-tasks", gate=gate)
        return EXIT_OK

    results = _results(state, gate)
    summary = _status(app, state, gate)
    if summary.practical_done and not everything:
        app.store.save(state)
        for line in _passed_lines(gate, summary):
            out(line)
        out("")
        out(TEXT["extra_practice"].format(gate=gate))
        return EXIT_OK

    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    if everything:
        kind = "practice" if summary.practical_done else ("again" if _graded(results) else "full")
        forms_before = previous.get("forms") if isinstance(previous.get("forms"), dict) else {}
        plan = progress.gate_full_plan(pool, results, drawn=forms_before)
    else:
        kind = "retest" if _graded(results) else "full"
        plan = progress.gate_sitting_plan(pool, results)
    chosen_ids = draw(plan, rng)
    by_id = {task["id"]: (lesson, task) for lesson, task in primary}
    chosen = [by_id[task_id] for task_id in chosen_ids if task_id in by_id]

    number = int(previous.get("attempt") or 0) + 1 if previous else 1
    forms = dict(previous.get("forms") or {}) if isinstance(previous.get("forms"), dict) else {}
    tasks, problems, built_infos = [], [], {}
    for lesson, task in chosen:
        task_id = task["id"]
        form = _next_form(previous, results, task_id)
        task_seed = rng.randrange(1, 1000000)
        folder = f"exam-{gate}/{task_id}"
        try:
            info = scenarios.build(app, task["build"], folder, scenario_id=folder,
                                   key=task_id, lesson_id=lesson.id, seed=task_seed,
                                   form=form, reset=True)
        except ToolTrouble as exc:
            problems.append((task_id, exc))
            continue
        except Refused:
            raise
        forms[task_id] = form
        built_infos[task_id] = info
        tasks.append({"id": task_id, "lesson": lesson.id, "title": str(task.get("title", "")),
                      "minutes": progress.task_minutes(task), "form": form, "seed": task_seed,
                      "folder": folder, "result": None, "graded": None})
    attempt = {"attempt": number, "kind": kind, "started": app.stamp(),
               "tasks": tasks, "forms": forms}
    attempts[gate] = attempt
    app.store.save(state, events=[{
        "type": "exam-started", "gate": gate, "attempt": number, "kind": kind,
        "tasks": [{"id": t["id"], "form": t["form"], "seed": t["seed"]} for t in tasks],
        "build_failed": [task_id for task_id, _exc in problems]}])
    for position, (task_id, exc) in enumerate(problems):
        if position:
            out("")
        out(TEXT["build_failed_head"].format(number=position + 1, id=task_id))
        problem = runner.make_problem(app, exc)
        for line in runner.render_problem(app, TEXT["head"].format(label=_label(gate)),
                                          problem, place=task_id):
            out(line)
    if problems:
        out("")
    if not tasks:
        out(TEXT["all_build_failed"])
        return EXIT_PROBLEM
    missing = [lesson_id for lesson_id in syllabus_gate_lessons(gate)
               if lesson_id not in progress.gate_lessons(pool)]
    if kind == "full" and missing and not problems:
        out(TEXT["too_few"].format(lessons=_lesson_list(missing), n=len(tasks)))
        out("")
    if unusable:
        out(TEXT["skipped_bad"].format(n=len(unusable), ids="、".join(unusable)))
        out("")
    _show(app, state, gate, attempt, infos=built_infos)
    return EXIT_PROBLEM if problems else EXIT_OK


def _show(app, state, gate, attempt, reopened=False, infos=None):
    """Print the tasks of ``attempt`` (no hints)."""
    out = app.console.out
    number = attempt.get("attempt", 1)
    label = {"retest": TEXT["head_retest"], "again": TEXT["head_again"],
             "practice": TEXT["head_practice"]}.get(
        attempt.get("kind"), TEXT["head_attempt"]).format(n=number)
    out(app.console.paint(TEXT["head"].format(label=_label(gate)).strip()
                          + " · " + label, "bold"))
    tasks = [t for t in attempt.get("tasks", []) if isinstance(t, dict)]
    pending = [t for t in tasks if t.get("result") not in (PASS, FAIL)]
    minutes = sum(progress.task_minutes(t) for t in pending)
    out(TEXT["count"].format(n=len(pending), minutes=minutes))
    verdict, _date = progress.explain_record(progress.explain_of(state, gate))
    if verdict != progress.EXPLAIN_PASS:
        if _status(app, state, gate).practical_done:
            out(TEXT["count_explain_due"].format(minutes=EXPLAIN_MINUTES, gate=gate))
        else:
            out(TEXT["count_explain"].format(minutes=EXPLAIN_MINUTES))
    out("")
    out(TEXT["rules_head"])
    for key in ("rule_1", "rule_2", "rule_3"):
        out("  - " + TEXT[key])
    for position, entry in enumerate(tasks, 1):
        out("")
        title = entry.get("title", "")
        if entry.get("result") in (PASS, FAIL):
            out(TEXT["task_graded"].format(number=position, title=title,
                                           result=TEXT["result_" + entry["result"]]))
            continue
        _lesson, task = _find_task(app, entry.get("id"))
        if task is None:
            out(TEXT["task_gone"].format(number=position, id=entry.get("id")))
            continue
        folder = scenarios.scenario_folder(app, entry["folder"])
        info = (infos or {}).get(entry["id"]) or scenarios.read_info(folder)
        out(app.console.paint(TEXT["task_head"].format(
            number=position, title=title, minutes=progress.task_minutes(entry)), "bold"))
        if not info.exists:
            out("  " + TEXT["task_missing"].format(path=app.show(folder), gate=gate))
            continue
        text = scenarios.fill_text(app, task["task"][entry["form"]], info)
        for line in str(text).strip().splitlines():
            out("  " + line)
        for line in info.todo:
            out("  " + line)
        out("  " + TEXT["task_folder"].format(path=app.show(info.path)))
        # The rule of the scenario command (tool-api 15.1): when the task text
        # or a todo line already says where to cd (usually one folder deeper),
        # the tool's own cd line would send the learner to the wrong folder.
        if not gives_cd(text, info.todo, app.show(info.path)):
            out("  " + TEXT["task_cd"].format(path=_shell_path(app, info.path)))
    out("")
    out(TEXT["finish_head"])
    out("  " + TEXT["finish_cd"].format(workspace=_shell_path(app, app.root)))
    out("  " + TEXT["finish_grade"].format(gate=gate))
    if reopened:
        out("")
        out(TEXT["open_again"].format(gate=gate))


def _shell_path(app, path):
    from .scenario import shell_path
    return shell_path(app, path)


def gives_cd(text, todo=(), folder=""):
    """True when the task already tells the learner which folder to enter.

    That is: the task text or one of its todo lines contains a ``cd ``
    command, or the text says 「进入 <a folder inside the task folder>」.
    """
    lines = [str(text)] + [str(line) for line in (todo or [])]
    if any("cd " in line for line in lines):
        return True
    return bool(folder) and any("进入 " + folder in line for line in lines)


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------
def _summary(tasks):
    passed = sum(1 for t in tasks if t.get("result") == PASS)
    problems = sum(1 for t in tasks if t.get("result") == PROBLEM)
    text = TEXT["summary_line"].format(passed=passed, total=len(tasks))
    if problems:
        text += TEXT["summary_problem"].format(n=problems)
    return text


def _after_lines(gate, summary, fails):
    """What comes next after a graded sitting, as paragraphs (lists of lines)."""
    if summary.practical_done:
        return [_passed_lines(gate, summary)]
    if fails:
        return [[TEXT["retest"].format(gate=gate, n=len(summary.open_lessons))]]
    if summary.open_lessons:
        return [[TEXT["lessons_left"].format(n=len(summary.open_lessons),
                                             lessons=_lesson_list(summary.open_lessons),
                                             gate=gate)]]
    return []


def _grade(app, state, gate, answers):
    out = app.console.out
    attempts = _attempts(state)
    attempt = attempts.get(gate)
    tasks = [t for t in (attempt.get("tasks") or []) if isinstance(t, dict)] \
        if isinstance(attempt, dict) else []
    if not tasks:
        app.store.save(state)
        out(TEXT["no_attempt"].format(gate=gate))
        return EXIT_NOT_YET
    if not _is_open(attempt):
        app.store.save(state)
        summary = _status(app, state, gate)
        out(TEXT["closed"].format(gate=gate, n=attempt.get("attempt", 1), summary=_summary(tasks)))
        if summary.practical_done:
            for line in _passed_lines(gate, summary):
                out(line)
        elif any(t.get("result") == FAIL for t in tasks):
            out(TEXT["closed_next"].format(gate=gate))
        else:
            out(TEXT["closed_done"])
            for paragraph in _after_lines(gate, summary, []):
                for line in paragraph:
                    out(line)
        return EXIT_OK
    todo = [t for t in tasks if t.get("result") not in (PASS, FAIL)]
    regrade = [t for t in todo if t.get("result") == PROBLEM]
    out(app.console.paint(TEXT["grade_head"].format(
        label=_label(gate), n=attempt.get("attempt", 1)), "bold"))
    if regrade and len(regrade) == len(todo) and len(todo) < len(tasks):
        out(TEXT["regrade_only"].format(n=len(todo)))
    results = _results(state, gate)
    details = {}
    events = []
    for entry in todo:
        position = tasks.index(entry) + 1
        heading = TEXT["grade_task"].format(number=position, title=entry.get("title", ""))
        result = _grade_one(app, state, entry, answers)
        if result.answers_used:
            del answers[:result.answers_used]
        out("")
        for line in runner.render_result(app, result, heading, place=entry.get("id", "")):
            out(line)
        outcome = RESULT_OF[result.outcome]
        entry["result"] = outcome
        entry["graded"] = app.stamp()
        details[entry["id"]] = result.to_dict()
        events.append({"type": "exam-task", "gate": gate, "task": entry["id"],
                       "attempt": attempt.get("attempt", 1), "form": entry.get("form"),
                       "seed": entry.get("seed"), "outcome": result.outcome})
        if outcome in (PASS, FAIL):
            record = results.get(entry["id"]) if isinstance(results.get(entry["id"]), dict) else {}
            history = list(record.get("history") or []) if isinstance(record.get("history"), list) else []
            history.append({"attempt": attempt.get("attempt", 1), "form": entry.get("form"),
                            "result": outcome, "date": app.today.isoformat()})
            results[entry["id"]] = {
                "form": entry.get("form"), "result": outcome, "date": app.today.isoformat(),
                "seed": entry.get("seed"), "attempt": attempt.get("attempt", 1),
                "title": entry.get("title", ""), "lesson": entry.get("lesson", ""),
                "history": history}
    app.store.save(state, events=events)

    summary = _status(app, state, gate)
    problems = [t for t in tasks if t.get("result") == PROBLEM]
    fails = [t for t in tasks if t.get("result") == FAIL]
    out("")
    out(TEXT["result_head"].format(summary=_summary(tasks)))
    if not problems and not fails:
        out(TEXT["passed_all"])
    if fails:
        out("")
        out(TEXT["practice_head"])
        catalog = app.catalog()
        for entry in fails:
            lesson = catalog.lesson(entry.get("lesson", ""))
            out("  - " + TEXT["practice_line"].format(
                lesson=entry.get("lesson", ""), lesson_title=lesson.title if lesson else "",
                title=entry.get("title", "")))
        if attempt.get("kind") == "practice":
            out(TEXT["practice_only"])
    if not problems:
        for paragraph in _after_lines(gate, summary, fails):
            out("")
            for line in paragraph:
                out(line)
    if problems:
        out("")
        out(TEXT["problem_note"].format(n=len(problems), gate=gate))
    if answers:
        out("")
        out(TEXT["unused_answers"].format(n=len(answers)))
    code = EXIT_PROBLEM if problems else (EXIT_NOT_YET if fails else EXIT_OK)
    app.store.write_result({
        "target": gate, "kind": "exam", "title": _title(gate),
        "attempt": attempt.get("attempt", 1), "exit_code": code,
        "practical_done": summary.practical_done, "explain": summary.explain,
        "gate_done": summary.done,
        "tasks": [{"id": t.get("id"), "form": t.get("form"), "seed": t.get("seed"),
                   "result": t.get("result")} for t in tasks],
        "details": details})
    return code


def _grade_one(app, state, entry, answers):
    """Grade one task of a sitting; always returns a ``CheckResult``."""
    lesson, task = _find_task(app, entry.get("id"))
    if task is None:
        return runner.CheckResult(runner.PROBLEM, problem={
            "summary": TEXT["gone_summary"].format(id=entry.get("id")),
            "where": "", "detail": "", "recovery": ""})
    try:
        folder = scenarios.scenario_folder(app, entry.get("folder", ""))
    except Refused as exc:
        return runner.CheckResult(runner.PROBLEM, problem={
            "summary": exc.message, "where": "", "detail": "", "recovery": ""})
    info = scenarios.read_info(folder)
    if not info.exists or folder.is_symlink() or info.key != entry.get("id"):
        return runner.CheckResult(runner.NOT_YET, fails=[{
            "where": TEXT["missing_where"].format(path=app.show(folder)),
            "saw": TEXT["missing_saw"], "missing": TEXT["missing_missing"]}])
    # An exam answer is final: ``ctx.final`` words a wrong answer without
    # "run it again" (tool-api R11).
    return runner.run_check(app, task["grade"], lesson=lesson, scenario=info,
                            state=state, answers=answers, warn_unused=False, final=True)


# ---------------------------------------------------------------------------
# The explain-back verdict
# ---------------------------------------------------------------------------
def _explain(app, state, gate, verdict):
    """Record the verdict of the explain-back questions (``--explain pass|again``)."""
    out = app.console.out
    exams = state.get("exams") if isinstance(state.get("exams"), dict) else {}
    if not _graded(exams.get(gate)):
        app.store.save(state)
        out(TEXT["explain_too_early"].format(gate=gate))
        return EXIT_NOT_YET
    before, before_date = progress.explain_record(progress.explain_of(state, gate))
    record = progress.record_explain(state, gate, verdict, app.today)
    app.store.save(state, events=[{"type": "exam-explain", "gate": gate,
                                   "result": verdict, "date": record["date"]}])
    if verdict == progress.EXPLAIN_AGAIN:
        if before == progress.EXPLAIN_PASS:
            # The latest verdict counts: say so when it takes a pass back.
            out(TEXT["explain_withdrawn"].format(date=before_date or "-", name=gate_name(gate)))
        out(TEXT["explain_again"].format(gate=gate))
        return EXIT_OK
    out(TEXT["explain_pass"].format(date=record["date"]))
    summary = _status(app, state, gate)
    if summary.done:
        out(TEXT["gate_passed"].format(name=gate_name(gate), date=record["date"]))
    elif summary.open_lessons:
        out(TEXT["explain_practical_left"].format(
            n=len(summary.open_lessons), lessons=_lesson_list(summary.open_lessons), gate=gate))
        out(TEXT["explain_kept"].format(name=gate_name(gate)))
    return EXIT_OK
