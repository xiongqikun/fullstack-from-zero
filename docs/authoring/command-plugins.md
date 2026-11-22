# Command plug-ins (`tools/courselib/commands/<name>.py`)

For the people who write or replace a command of `tools/course.py`. Lesson authors need [`tool-api.md`](tool-api.md) instead; its sections 15-18 also describe the behaviour of `scenario`, `exam`, `review`, `doctor` and `fresh` as lesson authors and testers see it.

## Protocol

Every command is one module in `tools/courselib/commands/`. `courselib.cli` imports every module of that package whose name does not start with `_`, in the order `status check hint scenario review exam journal doctor fresh validate` and then alphabetically. Adding a command means adding a file; nothing else is registered anywhere. A module must expose exactly two functions:

```python
from .. import cmdkit
from ..errors import EXIT_OK

SUMMARY = "一行中文说明（命令列表里显示）"
DESCRIPTION = """多行中文说明和例子（<命令> -h 里原样显示）"""
TEXT = {"done": "……"}            # every user-visible string of the module, in one place

def register(subparsers):
    parser = cmdkit.add_command(subparsers, "name", SUMMARY, description=DESCRIPTION)
    parser.add_argument("target", metavar="<站>", help="站点编号，例如 1.6a")
    parser.add_argument("--reset", action="store_true", help="……")

def run(args) -> int:
    app = args.app                 # the App of this run (paths, clock, environment, console)
    app.console.out(TEXT["done"])
    return EXIT_OK
```

- `cmdkit.add_command` returns a parser whose usage line, help and error messages are Chinese. Usage errors raise `UsageProblem` (exit 64); `-h` prints the help (exit 0). Never call `sys.exit` or `print`; write through `app.console.out` / `app.console.err`.
- `run` returns an exit code: `EXIT_OK` 0, `EXIT_NOT_YET` 1, `EXIT_PROBLEM` 2, `EXIT_USAGE` 64 (`courselib.errors`). It may also raise: `UsageProblem(message)` (64), `Refused(message)` (1, a safety refusal already worded for the learner), `ToolTrouble(summary, detail="", recovery="", where="")` (2, shown as 检查器出问题 with a block for the tutor), `Cancelled` (1). Anything else is caught by `cli.main` and shown as 检查器出问题 without a traceback (`COURSE_DEBUG=1` adds one on standard error).
- A plug-in that fails to import or to register does not take the other commands down: its name stays in the list and reports the failure when called.
- `args.bare` is True when the learner typed no command at all (that runs `status`).
- The command name is folded before parsing (`Check`, `ｃｈｅｃｋ` → `check`). Arguments a command does not take are reported by `cli.main` with a pointer to `<command> -h` (and, for `hint 1.6 a`, the joined id).
- A command that records an outcome calls `app.store.ensure_writable()` **before** doing the work, so the learner never sees an outcome followed by 检查器出问题 (plan I4: exactly one outcome). `check` does this.
- Reading input: `app.console.read(prompt)` returns one line, raises `Cancelled` on end-of-file or Ctrl+C (the CLI then prints a polite line, exit 1) and `UsageProblem` when `COURSE_NONINTERACTIVE=1`. `app.console.confirm(prompt)` is a yes/no question; `app.console.may_ask_optional` is True only when a person is at a terminal (ask optional questions only then).

## What the App gives a command

`app.root` (workspace root), `app.home`, `app.playground`, `app.my_site`, `app.env` (a copy of the environment), `app.now` / `app.today` (follow `COURSE_NOW`), `app.stamp()`, `app.show(path)` (with `~`), `app.rel(path)` (relative to the workspace), `app.scrub(text)` (home folder replaced by `~`, for anything stored), `app.catalog()` (the lessons, loaded once), `app.store` (the state store), `app.console`, `app.child_env()`.

## Library entry points

| Need | Call |
|---|---|
| Resolve a typed lesson or station | `cmdkit.find_target(app, text, want="any" / "station" / "lesson") -> (lesson, station_or_None)` |
| Load / save state | `state = app.store.load()`; change the dict; `app.store.save(state, events=[{"type": "...", ...}])` (writes `state.json` first, then the log, so a failed write leaves no log entry). Never write `learner/` files yourself. A corrupt state raises `StateTrouble` (a `ToolTrouble`) with a recovery instruction; let it propagate. `app.store.ensure_writable()` raises `ToolTrouble` now if a later save would fail. |
| A Chinese reason for an `OSError` | `store.reason(exc)` (never an English class name on screen) |
| Log without a state change | `app.store.log("kind", field=value)` |
| Last result for the tutor | `app.store.write_result(dict)` |
| Count study time | `progress.touch_session(state, app.now)` before saving |
| Run a check function | `runner.run_check(app, function, lesson=lesson, station_id=None, answers=[...], scenario=info, state=state) -> CheckResult` (`.outcome` passed / not_yet / problem, `.exit_code`, `.counted` (False when the check stopped only because its scenario is not built), `.to_dict()`); print with `runner.render_result(app, result, heading)`. Standard output, standard error and warnings of the function are captured (`ui.captured`) |
| Find a scenario | `app.catalog().scenario(text) -> (lesson, key, builder)` or None; `app.catalog().scenario_ids()` |
| Build a lesson scenario | `scenario.build_lesson_scenario(app, lesson, key, seed=None, reset=False) -> ScenarioInfo` |
| Build anything under the playground | `scenario.build(app, builder, folder, scenario_id="", key="", lesson_id="", seed=None, form=None, reset=False)`; all safety rules (inside the playground, marker, no overwrite without reset) are inside it |
| Find a built scenario again | `scenario.read_info(scenario.scenario_folder(app, folder))` |
| Fill a task text | `scenario.fill_text(app, task["task"][form], info)` (`{dir}` and facts) |
| Review schedule | `schedule.due_items(state, today)`, `schedule.answer(state, item_id, "right" / "fuzzy" / "wrong", today)` (`schedule.grade(state, item_id, correct, today)` is the two-way form), `schedule.is_retired(record)`, `schedule.box_counts(state)`, `schedule.INTERVAL_DAYS` |
| Review sessions | `review.due_count(state, catalog, today)` and `review.next_due(state, catalog, today)` (what `status` shows: servable items only, no retired, orphaned or pending ones); `review.make_plan(state, catalog, today, days_away)` (what one session serves); `review.redo_tasks(state, catalog, today)`; `review.sync_enrolment(state, catalog, today)` |
| Review items / exam tasks | `app.catalog().review_item(item_id) -> (lesson, item)`; `app.catalog().exam_tasks(gate) -> [(lesson, task)]`; `syllabus.GATES` |
| Read-only Git outside a check | `gitread.GitReader(app.child_env())` with `.global_config(key)`, `.global_bool(key)`, `.version()`; `gitread.GitRepo(path, reader)` |

## Notes on the individual commands

All ten commands are built.

- **scenario**: resolves with `catalog.scenario`, builds with `build_lesson_scenario`, then prints the folder (`app.show(info.path)`) and `info.todo`. `--reset` is the only way to replace a non-empty folder the tool finished building; a half-built one (marker `"complete": false`) is rebuilt without it; the library refuses anything without the `.playground` marker, a link, and anything outside the playground (`Refused`, exit 1). Ctrl+C during the build prints the command to rebuild (exit 1).
- **review** (built; see `courselib/review.py` and `commands/review.py`): a `do` item is built with `scenario.build(app, lesson.scenarios[item["scenario"]], "review/<item id>", key=item["scenario"], lesson_id=lesson.id, reset=True)` and graded with `runner.run_check(app, item["check"], lesson=lesson, scenario=info, state=state)`. Passing `key=item["scenario"]` matters: the item's check may call `ctx.scenario("start")`, which returns the bound review copy only when the keys agree. Choice items can be asked with `CheckContext.quiz` through a small check function, or rendered directly.
- **exam** (built; see `commands/exam.py`): the tasks of a sitting come from `app.catalog().gate_pool(gate)` (one task per lesson the gate covers); each is built with `scenario.build` in `exam-<gate>/<task id>` with `form="A"` or `"B"` and a seed. The open sitting is kept in `state["exam_attempts"]`; a graded task is stored as `state["exams"][gate][task_id] = {"form", "result": "pass" | "fail", "date": "YYYY-MM-DD", "seed", "attempt", "title", "lesson", "history"}` (`status --write` reads that shape).
- **doctor** and **fresh**: read-only towards the learner's machine. They do not call `app.store.load()` (they must work when the state file is damaged). `doctor` writes its report to `learner/last-result.json` and nothing else; `fresh` writes nothing. `fresh` reads `META["verified"]["tools"]` of each lesson and `tools/courselib/baseline.json` with the names of `syllabus.TOOL_NAMES`. Both are described for testers in `tool-api.md` section 17.
- **states.py** (plan I6) is called by `sc.state(name, base)` as `states.build_state(name, base, **kw)`, where the keyword arguments it may accept are `workspace`, `now`, `seed` and `env`; it returns the path of the `my-site` folder it built under `base` (or None to mean `base / "my-site"`). It must build only under `base`, and make commits through `courselib.gitwrite` (`git_init`, `git_commit`, `run_git`), which applies the signing-off and identity overrides. `gitwrite.git_commit` refuses a folder that is not itself the top of a repository; `sc.state` and `sc.site_before` pass an environment with `GIT_CEILING_DIRECTORIES` set to the scenario folder.
