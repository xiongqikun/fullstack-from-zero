# Lesson module API (`lesson.py`)

Reference for lesson authors, and the only document they need. Everything a `lesson.py` may define and every helper it may call is listed here, with its exact signature and a short example; sections 15-17 explain what the `scenario`, `exam`, `review`, `doctor` and `fresh` commands do with what you write and how to test in a simulation home. A complete worked example that uses each feature once is [`example-lesson/lesson.py`](example-lesson/lesson.py) with its rule card [`example-lesson/rules.md`](example-lesson/rules.md).

- API version: **1** (`courselib.API_VERSION`; `python3 tools/course.py --version` prints it). This interface is frozen for batch 1: names and signatures below will not change while the 20 lessons are written. Anything not listed here is internal and may change. The changes made after the testers' round of 2026-11-19 and the two batches of changes later that day (all within version 1) are listed in section 19.
- Binding context: plan sections I1-I7 and G5 (`docs/plans/2026-11-19-batch-1-plan.md`). Where this file is more detailed than the plan, this file is what `validate` enforces.
- Command plug-ins (for the people who write `tools/courselib/commands/*.py`, not for lesson authors) are described in [`command-plugins.md`](command-plugins.md).

Contents: [1 Ground rules](#1-ground-rules) · [2 Ids, folders, files](#2-ids-folders-and-files) · [3 META](#3-meta) · [4 TERMS](#4-terms) · [5 checks](#5-checks) · [6 The check context `ctx`](#6-the-check-context-ctx) · [7 Git views](#7-git-views-gitrepo-status-commit) · [8 Answers and normalisation](#8-answers-and-normalisation) · [9 HINTS](#9-hints) · [10 SCENARIOS and `sc`](#10-scenarios-and-the-builder-context-sc) · [11 REVIEW](#11-review) · [12 EXAM](#12-exam) · [13 rules.md](#13-rulesmd-rule-cards) · [14 validate and testing](#14-validate-and-testing-your-lesson) · [15 Scenarios, the ladder, exam tasks](#15-scenarios-the-state-ladder-and-exam-tasks) · [16 Writing REVIEW items](#16-writing-review-items) · [17 Environment tools](#17-environment-tools-make_sim_homepy-doctor-fresh) · [18 Behaviour the plan leaves open](#18-behaviour-where-the-plan-leaves-a-choice) · [19 Changes after the testers' round](#19-changes-to-api-v1-after-the-testers-round)

Where the course folder is: every lesson writes `cd ~/Developer/fullstack-from-zero`. A learner who moved the course has the folder there; a learner who kept it in place (decision `workspace_location` = `stay-in-sync`, lesson 0.2c) has an *entrance* there, a symbolic link to the real folder. The tool shows the workspace through `~/Developer/fullstack-from-zero` whenever that path leads to it (section 6.2), so lessons never need a second variant of a path.

---

## 1. Ground rules

1. **Plain Python, standard library only, Python 3.9 syntax.** No `match`, no `X | Y` in annotations evaluated at run time, no parenthesised context managers, no `tomllib`. `validate` compiles every module with a real Python 3.9 when the machine has one.
2. **Import nothing from the tool.** Every helper arrives through two objects: `ctx` (in checks and grading functions) and `sc` (in scenario builders). `import re`, `import datetime` and other standard modules are fine.
3. **Never print, never write** in a check. Report through `ctx.ok` / `ctx.fail` / `ctx.note`. Anything a check prints, on standard output or standard error, and any Python warning it causes is captured (it reaches `learner/last-result.json` as `printed_by_check` for the tutor, never the screen). The same holds for scenario builders. Checks are read-only: they never change the learner's files or repositories.
4. **Every string a learner can see is plain Chinese** (plan G2): short sentences, no "很简单 / 显然 / 只需要", no exclamation marks, Chinese full-width punctuation, a space between Chinese and Latin letters or digits. English is fine in code comments and docstrings.
5. **Module level is data.** Loading a module must have no side effects: no file access, no subprocess, no network, no randomness at import time. A module that raises at import is reported as broken; the other lessons keep working.
6. **The checker must never cry wolf** (plan section 6.2). If your check cannot look (missing program, broken scenario), let it raise or let `ctx` raise: the learner then sees 检查器出问题, not 还没达标. Only say "not yet" about something the learner can fix.
7. **Never reveal the answer** in a failure. Say where you looked, what you saw and what is still missing; not which command produces it. The answer belongs in hint level 4.

## 2. Ids, folders and files

| Thing | Form | Example |
|---|---|---|
| Lesson id | `<stage>.<n>` | `1.6` |
| Station id | lesson id + `a`, `b`, `c` in order | `1.6b` |
| Lesson folder | `stages/<NN>-<stage-slug>/<NN>-<lesson-slug>/` (two digits, kebab-case) | `stages/01-foundations/06-first-commit/` |
| Files in it | `lesson.md` (text, plan I1), `lesson.py` (this API), `rules.md` (rule cards, plan I2) | |
| Scenario key | `"start"`, or a station id, optionally with `-word` suffixes | `"start"`, `"1.6b"`, `"1.6b-broken"`, `"1.6-extra"` |
| Scenario folder | `<playground>/<scenario id>`; the id of `start` is `<lesson>-start`, any other key is its own id | `~/Developer/playground/1.6-start`, `~/Developer/playground/1.6b` |
| Review item id | lesson id + `-` + lower-case word(s) | `1.6-r1`, `1.6-commit-order` |
| Exam task id | lesson id + `-` + lower-case word(s), unique across REVIEW and EXAM | `1.6-x1` |
| Rule id | upper-case prefix + `-` + two digits, fixed by plan section 4 | `GIT-01` |

The playground is `~/Developer/playground` unless the environment variable `COURSE_PLAYGROUND` says otherwise. The learner types `python3 tools/course.py scenario 1.6` (or `1.6-start`) for the `start` scenario and `scenario 1.6b` for a station scenario.

## 3. META

```python
META = {
    "id": "1.6",                          # str, must match the folders
    "slug": "06-first-commit",            # str, exactly the lesson folder name
    "title": "Git：第一次提交",            # str, as in plan section 4
    "stage": 1,                           # int, the number before the dot
    "prerequisites": ["1.5"],             # list of lesson ids, each before this one
    "stations": [                         # 2 or 3 dicts, ids in order a, b, c
        {"id": "1.6a", "title": "为什么要版本管理", "minutes": 20,
         "new_concept": "提交是一张带说明的快照",       # exactly one concept (a str)
         "new_commands": ["git config"]},              # at most five, [] when none
        {"id": "1.6b", "title": "第一次提交", "minutes": 25,
         "new_concept": "改动先进暂存区，再进提交",
         "new_commands": ["git init", "git status", "git add", "git commit -m", "git log --oneline"]},
    ],
    "rules": ["GIT-01", "GIT-02"],        # rule ids of plan section 4; each has a card in rules.md
    "verified": {"date": "2026-11-19",    # the day you executed the lesson
                 "tools": {"git": "2.54.0", "macos": "27.2.1", "zsh": "5.9"}},
    "unverified_steps": [],               # short descriptions of steps marked 〔对照文档…〕 or 〔建课时无法验证〕
}
```

Budgets that `validate` enforces (plan G5, revised by G5a): 2-3 stations; `minutes` an integer from **15 to 40** (error outside; **warning above 30**: the number must be the one calculated with the method of plan G5a, and material that can move belongs in a 「想多了解（可跳过）」 box; 20-25 stays the target); `new_concept` a non-empty string; at most 5 `new_commands` per station and no command counted twice; at most 2 rules per lesson. A station that calculates above 40 must lose material (a 「想多了解（可跳过）」 box, a later lesson that owns the topic, or drop it). Gate exams are never part of a station's `minutes`. Lessons listed in plan section 4 must also match its folder, station ids and rule ids exactly (lesson 1.4 has three stations, 1.4a-1.4c, since 2026-11-19).

The minutes messages: 「1.6a 标了 45 分钟；一站最多 40 分钟（计划 G5a）。这一站要减内容：挪进「想多了解（可跳过）」框、挪到已经讲这个主题的后面一课，或者删掉」 (error), 「1.6a 标了 14 分钟；一站要在 15 到 40 分钟之间（计划 G5a）」 (error), 「1.6a 标了 31 分钟，超过 30 分钟（目标是 20 到 25 分钟）。这个数必须是按计划 G5a 的算法算出来的用时；能挪走的内容放进「想多了解（可跳过）」框」 (warning [G5]). The header line of lesson.md states the sum (section 14, V12).

`verified.tools` keys must be names that `fresh` knows: `macos`, `zsh`, `python3`, `git`, `code`, `brew`, `gh`, `node`, `npm`, `uv`, `ruff`, `sqlite3`, `docker`, `less`, `vi`, `man`, `grep`, `zip`, `claude-desktop`, `chrome` (list in `tools/courselib/syllabus.py`, `TOOL_NAMES`). Values are version strings as the tool prints them.

## 4. TERMS

Every new technical term of the lesson, for the glossary.

```python
TERMS = [
    {"term": "暂存区", "en": "staging area",
     "plain": "准备拍进下一张快照的改动", "first": "1.6b"},
]
```

All four keys are strings; `first` is the station that introduces the term. Use the wording of plan section 5a where it has one. A term may be the first use in only one lesson of the course.

## 5. checks

```python
def check_b(ctx):
    ...

checks = {"1.6a": check_a, "1.6b": check_b}     # one function per station, every station
```

A check takes one argument and returns nothing. The runner looks at what it recorded:

| What happened | Outcome | Exit code |
|---|---|---|
| at least one `ctx.fail(...)` | **还没达标** (every fail is listed: 看了哪里 / 看到了什么 / 还缺什么) | 1 |
| only `ctx.ok(...)` | **通过** | 0 |
| the function raised anything (also `SystemExit`), or recorded neither ok nor fail, or `ctx` could not look (no `git`, a timeout) | **检查器出问题**, "这不是你的错" | 2 |

`ctx.stop()` ends a check early; what was recorded so far decides. One failure outweighs any number of successes. Three kinds of check exist (plan I3); one function may combine them:

- **artifact**: look at files and repositories (sections 6.2-6.4);
- **ask**: ask a question whose answer the learner can only get by doing the task (`ctx.ask`, section 6.6);
- **quiz**: auto-graded multiple choice for concept stations (`ctx.quiz`).

Write each `fail` so that a beginner knows where to look:

```python
ctx.fail("index.html 里还没有你的名字",            # missing: what is still needed
         where="~/Developer/my-site/index.html 的第一个标题",   # where the tool looked
         saw="标题还是「你好，我是____」")             # what it saw there
```

## 6. The check context `ctx`

### 6.1 Reporting

| Signature | Does |
|---|---|
| `ctx.ok(text) -> True` | Records one thing done right (shown under 已经做到). |
| `ctx.fail(missing, where="", saw="") -> False` | Records one thing not there yet. Never put the solution in it. |
| `ctx.note(text)` | A neutral remark under 补充; does not change the outcome. |
| `ctx.expect(condition, ok, missing, where="", saw="") -> bool` | `ok(ok)` if `condition` is true, else `fail(missing, where, saw)`. |
| `ctx.failed` | Property: True once any `fail` was recorded. |
| `ctx.stop()` | Ends the check now (raises an internal signal; do not catch it). |

```python
if ctx.expect(repo.has_commits, "仓库里已经有提交",
              "还没有任何提交", where="练习仓库的历史", saw="git log 里是空的"):
    ctx.note("提交历史可以用 git log --oneline 看。")
if ctx.failed:
    ctx.stop()                           # do not ask a question before the work is there
```

Texts are collapsed to one line: runs of ASCII spaces, tabs and line breaks become one space. Other white space is kept, in particular the ideographic space U+3000 and the non-breaking space U+00A0, so evidence that quotes the learner's text shows exactly what was there. Keep each text under about 40 Chinese characters.

| Signature | Does |
|---|---|
| `ctx.visible(text) -> str` | names invisible characters for `saw=`: U+3000 → 〔全角空格〕, a tab → 〔Tab〕, U+00A0 → 〔不换行空格〕, each ASCII space at the end of a line → `·`. Other characters are kept. (Also `courselib.ui.visible`.) |

```python
title = ctx.read(ctx.my_site / "index.html").splitlines()[0]
if "\u3000" in title:
    ctx.fail("标题里有一个全角空格", where="index.html 的第一行", saw=ctx.visible(title)[:40])
#   看到了什么：<h1>你好〔全角空格〕我是小林</h1>
```

### 6.2 Paths and files (read-only, never raise)

Path rules for every `target`: `"~/x"` is relative to the learner's home (`HOME`); a relative `"x/y"` is relative to the **workspace root**; an absolute path or `pathlib.Path` is used as it is.

| Signature | Returns |
|---|---|
| `ctx.path(target) -> Path` | the absolute path |
| `ctx.show(target, entrance=True) -> str` | the path as the learner reads it, with `~` (`~/Developer/my-site`); the workspace and every path in it through `~/Developer/fullstack-from-zero` when that path leads to it (below); `entrance=False` shows the real place |
| `ctx.exists(target)`, `ctx.is_file(target)`, `ctx.is_dir(target)` | bool |
| `ctx.read(target, default="") -> str` | UTF-8 text (undecodable bytes replaced, BOM dropped); `default` when missing |
| `ctx.read_bytes(target, limit=2097152) -> bytes` | raw bytes (use it to check encodings and CRLF); `b""` when missing |
| `ctx.lines(target) -> list` | lines without line ends; `[]` when missing |
| `ctx.listdir(target, hidden=True) -> list` | sorted names; `hidden=False` drops dot-names; `[]` when missing |
| `ctx.walk(target, everything=False) -> list` | sorted relative paths of all files below; leaves out `.git/`, `.DS_Store`, `.playground` unless `everything`; at most 2000 |
| `ctx.size(target)` | bytes, or None when not a file |
| `ctx.mtime(target)` | `datetime` of the last change, or None |

`ctx.show` (and every path the tool prints) compares paths after resolving links: when HOME reaches a folder through a link (a simulation home under `/tmp`, which is `/private/tmp` on macOS), the path still prints as `~/…`.

**The entrance.** Every path the tool prints (`ctx.show`, `scenario`'s `cd` lines, `exam`, `review`, `check`, `journal`) shows the workspace and every path inside it **through `~/Developer/fullstack-from-zero` whenever that path exists and leads to the workspace**: the moved folder itself, or the entrance link of a learner who stayed. This holds however the path is spelled and also when the tool was started from the real folder. In every other case (nothing there, a broken link, a link to another folder, a real folder that is not the workspace) the real path is shown with `~`. Paths outside the workspace are never rewritten. So `ctx.show(ctx.workspace)` prints `~/Developer/fullstack-from-zero` for a learner with the entrance; a check that must name the real place (lesson 0.2c: 「学习工作区还在同步盘里（…）」) writes `ctx.show(ctx.workspace, entrance=False)`, which prints the real place, for example `~/Desktop/fullstack-from-zero`. `doctor` always shows the real place (section 17.2).

Useful attributes: `ctx.workspace` (workspace root), `ctx.home`, `ctx.playground`, `ctx.my_site` (`~/Developer/my-site`), `ctx.now` (a `datetime`; follows `COURSE_NOW`), `ctx.station` (the station id being checked, or None), `ctx.lesson_id`, `ctx.python` (the interpreter running the tool).

```python
text = ctx.read("~/Developer/my-site/index.html")
if "____" in text:
    ctx.fail("标题里的空还没有填", where=ctx.show(ctx.my_site / "index.html"), saw="还是 ____")
crlf = b"\r\n" in ctx.read_bytes(ctx.my_site / "README.md")
```

### 6.3 Worded expectations

These record a ready-made Chinese ok or fail and return a bool (`need_*` stop the check on failure and return the path or repository).

| Signature | Passes when |
|---|---|
| `ctx.expect_file(target, label=None)` | a file is there (a folder with that name fails with its own wording) |
| `ctx.expect_dir(target, label=None)` | a folder is there |
| `ctx.expect_missing(target, label=None)` | nothing is there any more (for 删除 exercises) |
| `ctx.need_file(target, label=None) -> Path` | like `expect_file`, then stop if missing |
| `ctx.need_dir(target, label=None) -> Path` | like `expect_dir`, then stop if missing |
| `ctx.need_repo(target, label=None, praise=False) -> GitRepo` | the folder itself is a repository (recorded under 已经做到 as 「是一个 Git 仓库：<label>」 **only with `praise=True`**: pass it only where the learner makes the repository in that very station or task, that is where `git init` (or `git clone`) is part of what it asks; a repository the tool built, or one from an earlier lesson, is not praised, section 19 item 12); a folder *inside* another repository fails with "仓库要建在这个文件夹里"; a folder with a `.git` that Git does not recognise (a damaged repository) raises: 检查器出问题 with 「可能损坏了…先不要运行 git init」, never "not a repository yet" |

`label` replaces the path in the message (`"练习仓库里的 README.md"`).

```python
site = ctx.need_dir("~/Developer/my-site", "你的网站文件夹 my-site")
ctx.expect_file(site / "style.css")
```

### 6.4 Git, programs and the environment

| Signature | Returns |
|---|---|
| `ctx.git(target) -> GitRepo` | a read-only view of that folder (section 7); never raises for a non-repository |
| `ctx.git_global(key)` | a value of the learner's global Git config (`~/.gitconfig`), or None. **Never put `user.name` or `user.email` values into a message** (plan G10): say "已设置" / "还没设置". |
| `ctx.git_global_bool(key)` | True / False / None (unset), read with `--type=bool` |
| `ctx.git_global_state(key)` | for a boolean setting: `"true"`, `"false"`, `"unset"` or `"invalid"`. Read with `git config --global --type=bool --get`, so `yes`/`on`/`1` are `"true"`, an empty value (`gpgsign =`) is `"false"`, a key written without `=` is `"true"`, and a value Git cannot read as a boolean (a typo such as `commit.gpgsign=fasle`) is `"invalid"` |
| `ctx.git_global_all(key)` | every value of a multi-valued global key, in file order (`[]` when unset; an empty value is `""`); in the case of plan G7 (and in a simulation home) `ctx.git_global_all("gpg.ssh.program") == [""]` |
| `ctx.git_version()` | e.g. `(2, 54, 0)` |
| `ctx.which(program)` | full path on the learner's PATH, or None |
| `ctx.env(name, default="")` | an environment variable of the learner's shell |
| `ctx.run(argv, cwd=None, timeout=10, stdin_text=None) -> RunResult` | runs a read-only program (a list, no shell; `cwd` defaults to the workspace). A missing program or a timeout is a `RunResult`, not an exception. `timeout` is clamped to 1-60 seconds. A mistake in the check itself raises `ValueError` (the learner sees 检查器出问题): a string instead of a list, an empty list, or `git` as the program |

`RunResult` has `.ok` (exit code 0, not missing, not timed out), `.code`, `.out`, `.err`, `.lines` (non-empty lines of `.out`), `.missing`, `.timed_out`. Pagers are switched off (`PAGER=cat`), `GIT_OPTIONAL_LOCKS=0` is set and no `__pycache__` is written. Use `ctx.run` to run the learner's own program; use `ctx.git` for Git: `ctx.run(["git", ...])` is refused.

`ctx.git_global` and `ctx.git_global_bool` are unchanged (`git_global_bool` answers None for both "unset" and "invalid"). A global configuration file Git cannot read at all (a broken line) makes `git_global_state` / `git_global_all` raise: 检查器出问题 with 「Git 读不了你的全局设置文件（~/.gitconfig），里面可能有一行写坏了。」 and the recovery 「先不要改这个文件。运行 python3 tools/course.py doctor，把结果发给导师。」. Neither logs anything; never put identity values into a message.

```python
state = ctx.git_global_state("commit.gpgsign")
if state == "invalid":
    ctx.fail("commit.gpgsign 的值写错了：修好之前每次提交都会失败",
             where="全局 Git 设置 commit.gpgsign", saw="值既不是 true 也不是 false")
elif state == "true" and not ctx.which("gpg"):
    ctx.fail("提交签名还开着，但这台电脑上没有签名程序", where="全局 Git 设置 commit.gpgsign",
             saw="值是 true，找不到 gpg")
result = ctx.run([ctx.python, "convert.py"], cwd="~/Developer/playground/0.1-start/hello-fx")
ctx.expect(result.ok and "人民币" in result.out, "程序能运行，输出了一行换算结果",
           "程序还不能正常运行", where="python3 convert.py 的输出", saw=(result.err or result.out)[-60:])
```

All Git access is through machine-readable commands (`status --porcelain=v1 -z`, `rev-parse`, `for-each-ref`, `log --format=…`), each with a 10 second timeout, with `GIT_OPTIONAL_LOCKS=0`, `-c diff.autoRefreshIndex=false`, `LC_ALL=C` and `GIT_NO_LAZY_FETCH=1`, so looking never changes the repository and never reaches the network. `repo.query(...)` (section 7) additionally runs against a temporary copy of the index, because porcelain commands such as `git diff` and `git describe --dirty` would otherwise rewrite `.git/index` after a file was only touched. A missing `git` or a timeout raises and becomes 检查器出问题.

### 6.5 Scenarios seen from a check

```python
info = ctx.scenario(key=None, required=True) -> ScenarioInfo
```

- In a **station check** pass the key: `ctx.scenario("start")`, `ctx.scenario("1.6b")`. Without a key the station's own scenario is used (`ctx.station`), if the lesson defines one.
- In the check of a **`do` review item** and in an **exam grading function** call it without arguments (or with the item's scenario key): you get the copy the tool built for that review or exam, not the learner's station folder.
- When the scenario was not built, or was only half built (Ctrl+C, a builder that raised), the check ends with a worded 还没达标 that names the command to build it (`python3 tools/course.py scenario 1.6-start`; the plain command also rebuilds a half-built one, no `--reset` needed). That run is **not counted as an attempt** (`check` says 「练习场景还没准备好，这次不算一次尝试」 and `last-result.json` carries `"counted": false`). With `required=False` you get the info back instead and decide yourself (`info.exists` is False).

`ScenarioInfo` fields: `.path` (the scenario folder, a `Path`), `.exists` (built completely), `.seed` (int), `.form` (`"A"` / `"B"` in an exam, else None), `.facts` (dict recorded by the builder with `sc.fact`), `.todo` (list of lines), `.key`, `.id`, `.lesson`, `.built` (time stamp).

```python
sc = ctx.scenario("start")
repo = ctx.need_repo(sc.path / sc.facts["repo"], "练习仓库")
```

### 6.6 Asking: `ctx.ask` and `ctx.quiz`

```python
ctx.ask(prompt, expected) -> bool
ctx.quiz(question, options, answer, explain="", feedback=None) -> bool
```

`ask` shows `prompt`, reads one line and compares it with `expected` after normalising both (section 8). `expected` is a string, an int (the answer must contain exactly that number: `"3"`, `"３ 个"`, `"三个"` all match 3; for an expected `0`, `"没有"`, `"无"`, `"零"` and `"一个也没有"` match too), a compiled regular expression (must match the whole normalised answer), a function `f(normalised_answer) -> bool`, or a list/tuple/set of those (any may match). Right: records `ok`; wrong: records a `fail` that shows what the learner typed and **never** the expected answer. The typed answer is kept in `ctx.last_answer`.

An empty answer (just Enter) is not an answer: at the terminal the question is asked again with 「这一题要填一个回答（直接回车不算）。」, up to three times, and after three empty answers the whole check is cancelled (exit 1, nothing recorded, no attempt counted). An empty `--answer ""` is a usage error (exit 64).

**Compute `expected` from the learner's real files or from the scenario's facts.** Never hard-code a value the learner could copy from the lesson text: the point of an ask check is that only doing the task yields the answer.

```python
sc = ctx.scenario("start")
ctx.ask("运行 git log --oneline 数一数：练习仓库里有几个提交？", expected=sc.facts["commits"])
ctx.ask("最新一个提交的编号（前 7 位）是什么？",
        expected=lambda typed: len(typed) >= 7 and repo.head.startswith(typed))
```

`quiz` shows the options as A, B, C ... and reads a letter. `options` is a list of 2-6 non-empty strings; `answer` is the letter of the correct one. Accepted spellings: `b`, `Ｂ`, `B.`, `(b)`, `选 B`, `答案是 B`, or the text of an option. The text is compared after normalising both sides (section 8) and folding the dots `.` `。` `．` `·` `・` `•` `‧` `∙` to one, so 「惯例.事实标准」 and 「惯例。事实标准」 name the option 「惯例·事实标准」 (`normalize.fold_dots`, `normalize.option_text_index`); an answer that is the text of two options after folding names none. Letters are read first and unchanged (`B.`, `Ｂ。`); the folding never touches numbers in `ask` answers (`7.20`). An unreadable answer typed at the terminal is asked again (at most three times). `explain` is shown as a note after a right answer. `feedback` maps wrong letters to one sentence that says why that option is wrong without naming the right one. A malformed question (wrong letter, one option) raises: that is the lesson's fault, so it shows as 检查器出问题.

```python
ctx.quiz("git add 做的是哪件事？",
         ["把改动拍成快照", "把改动放进暂存区", "把仓库传到网上"], "B",
         explain="拍快照是 git commit。",
         feedback={"A": "拍快照是另一条命令做的。", "C": "这一课还没有联网。"})
```

Answers come from the terminal, or in order from `--answer` options (`check 1.6b --answer 3 --answer B`), which is how testers and `COURSE_NONINTERACTIVE=1` runs answer. Questions are asked in the order your check calls them; each `ask` or `quiz` consumes one answer. End-of-file or Ctrl+C at a prompt cancels the whole check politely (exit 1, nothing recorded).

Also available: `ctx.normalize(text, case=True) -> str` and `ctx.parse_int(text) -> int | None` (section 8).

**`ctx.final`** (bool, default False) is True when a wrong answer cannot be retried in this sitting: `exam --grade` sets it for every grading function (`runner.run_check(..., final=True)`). Then a wrong `ask` reads 「这个回答和实际情况对不上，这一题记为还没达标。」 instead of 「这个回答和实际情况对不上。回到题目说的地方再看一次，然后重新运行检查」, and a wrong `quiz` 「这一题没有选对，记为还没达标。」 (after the option's `feedback` sentence) instead of 「这一题还没选对。再想一想，重新运行检查」. Station checks and `review --grade` keep the old endings. A grading function may read `ctx.final`; it never sets it, and it never adds its own "run it again" advice.

#### `ctx.choose`: a free decision

```python
ctx.choose(question, options, key=None, explain="", feedback=None) -> value
```

For a question that has **no right answer**: a decision of the learner (keep the course folder where it is or move it; accept or reject an AI change). Never use `ctx.quiz` or `ctx.ask` for those: they print 「这一题还没选对」 or 「答对了：…」.

- `options`: 2-6 options, each a label (`"接受"`) or a `(value, label)` pair when the stored value should differ from what the learner reads (`("stay-in-sync", "先留在原处，我知道风险")`). Labels must be non-empty and different; values are strings, numbers, `True`/`False` or `None`.
- Shown and read exactly like a quiz (A, B, C …; `b`, `Ｂ`, `B.`, `选 B` or the text of an option, dots folded as for `quiz`).
- Records 「你的决定：<label>」 under 已经做到; never 答对了, never a fail. `last-result.json` gets `{"kind": "choose", "prompt": …, "answer": "B", "choice": <label>}` (no `correct` key).
- `key`: the decision is stored as `decisions[key]` in `learner/state.json`, **saved when the check passes**, exactly like `ctx.decide(key, value)` (read it later with `ctx.decision(key)`). A check that fails after a `choose` saves nothing, and the question is asked again next time.
- `explain`: a note shown after any choice. `feedback`: `{letter: note}` for one option.
- Returns the value (the label for plain strings), so the check can branch on it.
- Answers: one `--answer` per question in non-interactive runs (`check 0.2c --answer B`). An answer that names no option is asked again at the terminal with 「请输入 A 到 B 之间的一个字母。」; after three the check is cancelled (exit 1, nothing recorded). From `--answer` it is a usage error (exit 64): 「用法不对：--answer 给的「x」不是 A 到 B 之间的字母，也不是哪个选项的原文。这一题要选一个选项，例如 --answer A」.
- A malformed question (one option, two equal labels, an empty label, an empty `key`) raises: 检查器出问题.

```python
def check_c(ctx):
    if ctx.decision("workspace_location") == "stay-in-sync":
        ctx.ok("你之前决定先把课程留在原处，这个决定已经记下")
        return
    choice = ctx.choose(
        "学习工作区还在同步盘里（" + ctx.show(ctx.workspace, entrance=False) + "）。你怎么决定？",
        [("move", "请导师帮我搬到 ~/Developer（还没搬）"),
         ("stay-in-sync", "先留在原处，我知道风险")],
        key="workspace_location",
        explain="以后想搬，随时对导师说“帮我把课程安置到 ~/Developer”。",
        feedback={"A": "搬好以后，在新位置再运行这个检查。"})
    if choice == "move":
        ctx.fail("课程还没有搬到新位置", where=ctx.show(ctx.workspace, entrance=False),
                 saw="它还在同步盘里")
```

The learner sees for B: `✅ 通过 · 0.2c …` / `已经做到：` / `- 你的决定：先留在原处，我知道风险` / `补充：` / `- 以后想搬，…`.

### 6.7 Learner state (read-only) and decisions

| Signature | Returns / does |
|---|---|
| `ctx.state` | a deep copy of `learner/state.json` (changes are ignored) |
| `ctx.passed(station_id) -> bool` | has that station's check ever passed |
| `ctx.decision(key, default=None)` | a decision recorded earlier |
| `ctx.decide(key, value)` | records a decision of the learner; saved only if this check passes |

```python
ctx.decide("commit_signing", "off" if ctx.git_global_bool("commit.gpgsign") is False else "ssh")
```

Known decision keys: `workspace_location` (values `"not-synced"`, `"stay-in-sync"`; `"move"` if a lesson stores it), `commit_signing`, `commit_email` (`"noreply"` or `"own"`, check 1.11c), `course_product`, `hello_fx_amount` (the amount the learner set in `starter/hello-fx/convert.py`, written by check 0.1c; the cold redo after hint level 4 must use another amount). Use lower-case snake_case for new ones and mention them in your report.

**Gates** (read-only; the rule is in section 15.5):

| Signature | Returns |
|---|---|
| `ctx.gate_done(gate_id) -> bool` | True when the gate is passed: every lesson it covers has a passed task **and** the explain-back is recorded as pass (`exam <gate> --explain pass`). A gate never sat, or with only the practical part passed, is not done. |
| `ctx.gate_result(gate_id) -> GateResult` | a read-only named tuple (assigning raises): `.gate`, `.title` (「本地 Git 关卡」), `.attempts` (sittings started), `.passed` (task ids passed), `.open` (tasks tried without a pass in lessons not passed yet: what to practise; untried tasks are not listed), `.open_titles` (their titles), `.done` (= `gate_done`), `.in_progress` (a sitting has ungraded tasks), `.tasks` (usable tasks of the gate), `.practical_done` (every lesson has a passed task), `.explain` (`"pass"`, `"again"` or None), `.explain_date` (ISO date or None), `.lessons` (lesson ids the gate covers), `.open_lessons` / `.open_lesson_titles` (lessons without a passed task; before the first sitting all of them), `.next_count` / `.next_minutes` (the ungraded tasks and minutes of the open sitting while one is open, an extra practice sitting included; else those of the next sitting; 0 when the practical part is passed and no sitting is open: do not branch on `next_count == 0`, use `.practical_done`). Every sequence is a tuple in learning order. |

An unknown gate id raises (检查器出问题: 「检查函数问的关卡 X 不存在」). Both read `ctx.state` and the lesson catalogue; they never write. Name what is missing with `.open_lesson_titles`, never with `.open`, which is empty before the first sitting.

```python
def check_b(ctx):
    gate = ctx.gate_result("gate-1")
    if gate.in_progress:
        ctx.fail("这一场考试还没有批改完", where="gate-1 最近一场",
                 saw="还没批改：python3 tools/course.py exam gate-1 --grade")
    elif gate.attempts == 0:
        ctx.fail("还没有考 gate-1 的实操题", where="学习记录里的关卡成绩", saw="没有 gate-1 的记录")
    elif not gate.practical_done:
        ctx.fail("还有课的实操题没通过，练好以后补考", where="gate-1 的成绩",
                 saw="还没通过：" + "、".join(gate.open_lesson_titles))
    elif not ctx.gate_done("gate-1"):
        ctx.fail("讲解题还没记为通过", where="gate-1 的讲解题",
                 saw="对导师说“请问我 gate-1 的讲解题”，结果用 exam gate-1 --explain pass 记下")
    else:
        ctx.ok("阶段验收 gate-1 通过了（讲解题 " + (gate.explain_date or "") + "）")
```

### 6.8 Where to pick up next time

`check`, `status` and `journal` give one answer to "what comes next" (`courselib.status.next_step`), always as one of the fixed sentences of COMMON.md section 2. Lesson texts and the tutor's rules quote these strings exactly; a lesson's 存档点 and 收尾 lines use the same sentences (section 14, V1 and V2).

The answer, considered in this order:

1. review items due today (`status` only): 「先做 N 条到期的复习：python3 tools/course.py review」, followed by the next step;
2. the lesson before the current one, all its stations passed but its whole-lesson check not yet: 「从 1.6 的收尾继续」 (only while the current lesson has not been begun). A passed whole-lesson check is read from `state["lesson_checks"]`; a state written before that key existed (2026-11-19) has none, and then the passed `lesson-check` events of `learner/log.jsonl` count (`status.lesson_checked(state, lesson, app)`, `status.logged_lesson_checks(app)`);
3. the gate after that lesson (`syllabus.GATES[gate]["after"]`: gate-0 after 0.4, gate-a after 1.5, gate-b after 1.10, gate-1 after 1.16), not passed: 「做小关卡 gate-a」 while its practical part is open (when a sitting of it is open and not graded, the text names that sitting and `--grade` instead of the task count), 「请问我 gate-a 的讲解题」 when every lesson of the gate has a passed task and the explain-back is not recorded as pass (also while an extra practice sitting is open);
4. the current lesson (the first with a station not passed): 「从 1.6b 继续」 when begun, 「从 1.7 开始」 when not, 「开始上课」 before anything was done;
5. nothing left: 「准备阶段 2」 (the stage after the last stage that has lessons).

**A gate never blocks the next lesson.** Every gate whose lessons are all passed and that is still open adds one line, wherever the learner is: 「小关卡 gate-a「终端与文档关卡」还没有通过，它不挡下一课。准备好了就对导师说“做小关卡 gate-a”。」 or 「小关卡 gate-a「终端与文档关卡」的实操题都通过了，讲解题还没记为通过，它不挡下一课。准备好了就对导师说“请问我 gate-a 的讲解题”。」, or, while a sitting of it is open and not graded, 「小关卡 gate-a「终端与文档关卡」第 1 场考试还没批改完（5 题），它不挡下一课。做完以后批改：python3 tools/course.py exam gate-a --grade」. Gates are named as COMMON.md section 3 says: 「小关卡 gate-a「终端与文档关卡」」, 「小关卡 gate-b「本地 Git 关卡」」, 「gate-0「起步小关卡」」 and 「gate-1「阶段 1 验收」」 (the kind word is left out when the title says it); in a sentence 「小关卡 gate-0」 … 「阶段验收 gate-1」; the sentence to the tutor is always 「做小关卡 <gate>」.

What `check` prints (exact; `{…}` filled in):

| When | Lines |
|---|---|
| a station passed, the next station is open | 「存档点 1.6a：到这里可以安全停下。」 「下一站：1.6b「…」。下次可以对导师说“从 1.6b 继续”。」 |
| a station passed, an earlier station is still open | 「1.6 课还没通过的站：1.6a」 then 「下次可以对导师说“从 1.6a 继续”。」 |
| the last open station passed | 「1.6 课的 3 站都通过了。收尾先做全课检查：python3 tools/course.py check 1.6」 then 「下次可以对导师说“从 1.6 的收尾继续”。」 |
| the whole-lesson check passed | the closing steps left (below), then one of: 「下一课：1.7「Git：看懂改了什么」。下次可以对导师说“从 1.7 开始”。」 + 「课文在 stages/01-foundations/07-read-diff/lesson.md」; 「下一步是小关卡 gate-b「本地 Git 关卡」：5 道实操题，预计 29 分钟，讲解题另需约 10 分钟。开始考试：python3 tools/course.py exam gate-b」 + 「下次可以对导师说“做小关卡 gate-b”。」 (gate-0: 「下一步是 gate-0「起步小关卡」：…」); 「小关卡 gate-b「本地 Git 关卡」的实操题都通过了，还差讲解题（约 10 分钟）：请导师问你讲解题，评完用 python3 tools/course.py exam gate-b --explain pass 记下（要再来一次就写 again）。」 + 「下次可以对导师说“请问我 gate-b 的讲解题”。」; 「已有的课程都学完了。下次可以对导师说“准备阶段 2”。」; then one paragraph per open gate (the lines above) |
| a sitting of the due gate is open and not graded (any check that names what comes next) | 「小关卡 gate-b「本地 Git 关卡」第 1 场考试还没批改完（5 题）：做完以后批改：python3 tools/course.py exam gate-b --grade；想放弃这一场重新出题：python3 tools/course.py exam gate-b --new。」 + 「下次可以对导师说“做小关卡 gate-b”。」 |

The closing steps after a passed whole-lesson check follow COMMON.md section 3: 「收尾还有两件小事：」 / 「1. 行规笔记：运行 code notes/my-rules.md，在小标题「GIT-01 一个项目一个仓库，在项目根目录初始化」「GIT-02 …」下面各用自己的话写一两句，再配一个你自己的例子」 (each title is the full heading of the lesson's rules.md, here shortened with …; 「各」 only for two rules) / 「2. 一句话日志：python3 tools/course.py journal」; from lesson 1.12 on 「收尾还有三件小事：」 with 「3. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做」. A lesson without a new rule has no notes step (COMMON.md section 3): 「收尾还有一件小事：」 / 「1. 一句话日志：python3 tools/course.py journal」 (from lesson 1.12 on 「收尾还有两件小事：」 with the backup as step 2). A passed whole-lesson check is remembered as `state["lesson_checks"][lesson]` (the first time it passed).

`{n}` and the minutes of a due gate describe the practical part of the next sitting (the ungraded tasks of an open sitting; else one task per lesson not passed yet, the failed task in its other form); the explain-back adds about 10 minutes (`status.EXPLAIN_MINUTES`; COMMON.md section 1 under plan G5a: the tutor's questions and verdict are four exchanges at 2 minutes, plus the command that records it, rounded up to a multiple of 5). No sentence of the tool says how many explain-back questions there are (gate-0, gate-a and gate-b add a debugging question). Before a sitting is drawn, a lesson with two tasks counts with their mean, rounded up overall, so the head of the sitting (the exact sum) may differ by a few minutes (section 15.5).

What `status` prints: one line 「下一步：<text>。下次可以对导师说“<sentence>”。」, e.g. 「下一步：打开 stages/00-orientation/01-first-steps/lesson.md，从头开始；做完第 1 站运行 python3 tools/course.py check 0.1a。下次可以对导师说“开始上课”。」, 「下一步：打开 …，从「第 2 站」接着做；做完运行 python3 tools/course.py check 1.6b。下次可以对导师说“从 1.6b 继续”。」, 「下一步：1.6b 检查过 2 次，还没通过。接着改，再运行 python3 tools/course.py check 1.6b。…」, with reviews due 「下一步：先做 3 条到期的复习：python3 tools/course.py review；然后 1.6 课的 3 站都通过了。收尾先做全课检查：python3 tools/course.py check 1.6。下次可以对导师说“从 1.6 的收尾继续”。」, then the open-gate lines. When every station has passed and the next step is neither a lesson's closing steps nor a gate (that is, once the gate after the last lesson, gate-1, is passed), the first line is 「已有的课程的站都通过了（52/52 站）。」 and the next is 「下一步：已有的课程都学完了。下一阶段的课还要准备。下次可以对导师说“准备阶段 2”。」 (「继续下一阶段」 is gone). The 70 % notice 「阶段 N 已完成 70% 以上（d/t 站）。把这条告诉导师：下一阶段的课程需要提前准备。」 appears only while no lesson of a later stage exists.

The first line of `status` says where the learner is. It follows the next step: 「你在：1.6 Git：第一次提交 · 第 2 站「第一次提交」（1.6b）」 for a station or a lesson, 「你在：0.4 像管项目一样管学习 · 收尾」 when the next step is that lesson's closing steps, 「你在：gate-0「起步小关卡」（学完 0.4 课以后）」 or 「你在：小关卡 gate-b「本地 Git 关卡」（学完 1.10 课以后）」 when it is the gate after a lesson. The landing line names gates the same way: 「下一个落脚点是小关卡 gate-a「终端与文档关卡」（学完 1.5），还有 11 站」, 「下一个落脚点是 gate-0「起步小关卡」（学完 0.4），还有 12 站」, 「下一个落脚点是 gate-1「阶段 1 验收」（学完 1.16），还有 n 站」 (a gate after a lesson is its landing point; 「阶段 N 结束」 only where the last lesson of a stage has no gate, e.g. outside the syllabus: 「下一个落脚点是阶段 99 结束（学完 99.1），还有 2 站」) (was 「到下一个落脚点「终端与文档关卡 gate-a」（学完 1.5）：还有 11 站」). **The landing line and the stage line follow the same lesson as the first line** (since 2026-11-20, second pass): at a lesson's closing steps or the gate after it, that lesson; else the lesson of the first open station. So at the end of stage 0 the learner reads 「你在：0.4 像管项目一样管学习 · 收尾」, 「下一个落脚点是 gate-0「起步小关卡」（学完 0.4）：站都通过了，还差 0.4 课的收尾」 and 「阶段 0 起步：已完成 n/n 站（100%）」; when the gate is the next step (due, a sitting open, or only the explain-back left) 「你在：gate-0「起步小关卡」（学完 0.4 课以后）」, then 「落脚点到了：gate-0「起步小关卡」」 and the same stage line. 「还有 0 站」 is never printed. The same holds after 1.5 (gate-a), 1.10 (gate-b) and 1.16 (gate-1; also when 1.16 is the last lesson in the workspace, where the first line used to be 「已有的课程的站都通过了」). Once the gate is passed, every line follows the next lesson. `PROGRESS.md` (`status --write`) has the same lines. After a long break: 「距离上次学习：N 天。隔得有点久，建议先走一遍回归流程：对导师说“我回来了，带我走回归流程”。」 (the quotation marks were 「」).

What `journal` asks: 「下次从哪开始（直接回车 = 从 0.1 的收尾继续）：」, the same sentence without reviews.

Example: `status` in lesson 1.6 with gate-a still open:

```text
学习进度 · 2026-11-27

  你在：1.6 Git：第一次提交 · 第 2 站「第一次提交」（1.6b）
  下一步：打开 stages/01-foundations/06-first-commit/lesson.md，从「第 2 站」接着做；做完运行 python3 tools/course.py check 1.6b。下次可以对导师说“从 1.6b 继续”。
  小关卡 gate-a「终端与文档关卡」还没有通过，它不挡下一课。准备好了就对导师说“做小关卡 gate-a”。
  下一个落脚点是小关卡 gate-b「本地 Git 关卡」（学完 1.10），还有 10 站
  …
```

## 7. Git views: `GitRepo`, `Status`, `Commit`

`repo = ctx.git(path)` or `ctx.need_repo(path)`. Every member is safe on a folder that is not a repository (it answers False, None, 0 or empty; in particular `repo.is_clean()` is **False** there, so `ctx.expect(repo.is_clean(), …)` never passes on the wrong folder).

| Member | Meaning |
|---|---|
| `repo.path` | the folder (`Path`) |
| `repo.exists` | the folder exists |
| `repo.is_repo` | the folder itself is the top of a repository (or a bare repository) |
| `repo.inside_repo` / `repo.toplevel` | the folder sits in some working tree / that tree's top folder (a `git init` in the wrong place shows here) |
| `repo.is_bare` | a bare repository (the stand-in for GitHub in later lessons) |
| `repo.head` / `repo.has_commits` | full hash of HEAD or None / bool |
| `repo.branch` | current branch name, None when detached |
| `repo.ref(name)` | full hash of a branch, tag, `HEAD~1` ..., or None |
| `repo.commit_count(ref="HEAD")` | number of commits reachable |
| `repo.commits(limit=100, ref="HEAD")` | list of `Commit`, newest first |
| `repo.commit(ref="HEAD")` | one `Commit` or None |
| `repo.changed_files(ref="HEAD")` | `[(letter, path)]` changed by that commit (`A` added, `M` modified, `D` deleted; renames show as `D` + `A`) |
| `repo.file_at(ref, path)` | text of a file as stored in a commit, or None |
| `repo.status()` | a `Status` |
| `repo.is_clean()` | the folder is a (non-bare) repository and nothing is staged, modified or untracked |
| `repo.tracked()` / `repo.is_tracked(path)` | paths in the index |
| `repo.is_ignored(path)` / `repo.ignored()` | ignore rules (includes the learner's global ignore file) |
| `repo.config(key, scope=None)` / `repo.config_bool(key, scope=None)` | value seen from here; `scope` `"local"` or `"global"` |
| `repo.branches()` / `repo.tags()` | names |
| `repo.remotes()` | `{name: url}` |
| `repo.upstream()` / `repo.ahead_behind()` | e.g. `"origin/main"` / `(ahead, behind)`, or None |
| `repo.refresh()` | forget cached answers (after `ctx.ask` the learner may have changed things) |
| `repo.query(*args) -> RunResult` | escape hatch: another **read-only** git subcommand. Accepted: `rev-parse`, `rev-list`, `log`, `show`, `status`, `for-each-ref`, `ls-files`, `ls-tree`, `cat-file`, `diff`, `diff-tree`, `diff-index`, `diff-files`, `check-ignore`, `check-attr`, `merge-base`, `describe`, `shortlog`, `count-objects`, `name-rev`, `show-ref`, `blame`. Refused (检查器出问题): any other subcommand (also `grep`, whose `-O` option runs a program) and the options `--output`, `--open-files-in-pager`, `--ext-diff`, `--exec`. Runs on a temporary copy of the index, so the repository is never changed. |

`Status`: `.clean`, `.entries` (each with `.x`, `.y`, `.code` such as `"M "`, `" M"`, `"??"`, `.path`, `.original` for renames), `.staged`, `.unstaged`, `.untracked` (lists of paths), `.code(path)` (two letters or `""`).

`Commit`: `.hash`, `.short`, `.parents` (list), `.author_name`, `.author_email`, `.date` (author date, ISO 8601), `.commit_date`, `.subject`, `.body`, `.message`.

```python
repo = ctx.need_repo(ctx.my_site, "my-site")
last = repo.commit()
ctx.expect(re.match(r"^(feat|fix|docs|style|refactor|test|chore)(\([a-z0-9-]+\))?!?: \S", last.subject),
           "最新提交的说明符合约定式提交的格式", "提交说明的开头要有类型前缀",
           where="最新提交的第一行", saw=f"现在是「{last.subject[:30]}」")
status = repo.status()
if "index.html" in status.unstaged:
    ctx.fail("index.html 改了但还没放进暂存区", where="git status", saw="index.html 是“已修改”")
```

## 8. Answers and normalisation

What a learner types is normalised before any comparison, so that an input method cannot fail someone who knows the answer:

- full-width letters, digits and punctuation become half-width (`１.６Ａ` -> `1.6a`), the ideographic space becomes a space;
- leading and trailing white space is removed, inner runs collapse to one space;
- one pair of wrapping quotes or backticks is removed (`"…"`, `'…'`, `` `…` ``, `“…”`, `‘…’`, `「…」`, `『…』`), and a trailing `。` or `、` is dropped;
- letters are lower-cased (`ctx.normalize(text, case=False)` keeps case).

`ctx.parse_int(text)` reads one whole number wherever a beginner puts it: digits (also full-width) and Chinese numerals 0-9999 (`"一百二十"` 120, `"一百零五"` 105, `"两千"` 2000; a numeral with 万 or 亿, a colloquial short form such as `"一百二"` and two digits in a row give None, never a wrong number; since 2026-11-20, before that `"一百二十"` was read as 20) anywhere in the answer: `"3"`, `"３ 个"`, `"三"`, `"三个文件"`, `"十二"`, `"第二条"` (2), `"第四课"` (4), `"一共三个"` (3), `"共 12 行"` (12), `"大概五个"` (5), `"十分钟"` (10). A Chinese numeral counts only when a measure word (个 条 行 次 站 课 题 …), a non-Chinese character or the end follows it, so 「一共」「一起」「一样」「统一」「唯一」 are words, not numbers. The same number written twice (`"3 个，就是三个"`) is that number. A remark in brackets after a number is left aside (`"4 行（第一行是标题）"` 4, `"3（不确定）"` 3), and a negation counts only when it governs the number itself: directly before it (不是 不到 不足 不止 不超过 没有 没 无 不 非 负, also 不太是 不大是 不一定是 不会是; spaces and an opening bracket in between do not hide it: `"不是（3）"`, `"没有（3 个）"`, `"不 是 5"`, `"不太是 5"`; `"不是3"`, `"没有 3 个"`, `"不到 3 个"`, `"负一"`) or directly after it and its measure word (`"一个也没有"`, `"3 个都不是"`). **One rule for comparison words: an answer that gives a bound and not a number is not a number.** Every comparison word gives None, whichever side of the number it stands on (`normalize.COMPARISON_WORDS`: 少于 小于 低于 不到 不足 不超过 不多于 不少于 至多 最多 至少 最少 超过 多于 大于 高于, before the number, also with 等于 and up to three filler characters from 了 得 也 就 只 都 有 是 要 会 after it, or after the number and up to three Chinese characters; 以上 以下 以内 以外 only after the number; a comparison word alone in brackets counts too and is no aside): `"少于3行"`, `"最多 3 行"`, `"至少有 3 个"`, `"大于等于 3"`, `"超过了 3 个"`, `"至少得 3 个"`, `"最多只有 3 个"`, `"3 个最多"`, `"3 行以上"`, `"5 个以内"`, `"3 个或以上"`, `"3 个文件以上"`, `"3（以上）"`, `"3 个（至少）"` all None. 左右 is not a comparison word: `"3 个左右"` 3, like `"差不多 3 个"`; 以外 in front of a number is not one either: `"除了 . 和 .. 以外有 5 个"` 5. After 第 the number is an ordinal and a word after it bounds nothing: `"第 3 行最多"` 3, `"第三条最多"` 3, `"第 3 行以下"` 3. Without 第 the tool cannot tell a label or "the following" from a bound, so `"3 号最多"` and `"3 行以下是空行"` give None: a which-one question with an int `expected` should ask for 「第几」, or use `ctx.quiz`. Words such as 不算 / 不确定 / 不包括 elsewhere in the answer do not matter, so an answer that repeats the question's own condition is read: `"5 个，不算 . 和 .."` 5, `"3 行，不包括空行"` 3, `"应该是 3 个吧，不太确定"` 3, `"差不多 3 个"` 3. It returns None for no number, two **different** numbers (`"3 或 4"`, `"第二条，共 3 行"`), a range (`"三到四个"`, `"3 到 4 个"`, `"3-4"`), a decimal, a version or a half (`"3.5"`, `"1.6a"`, `"三个半"`), `"三四个"`, a negation of the number (`"没有"`, `"不是3"`, `"没有 3 个"`, `"不是（3）"`), and a bound (`"少于3行"`, `"3 行以上"`). `ctx.ask(..., expected=<int>)` uses it; drop workarounds that strip 「第」「一共」 first. Station ids typed on the command line are normalised the same way, a Chinese full stop or comma inside an id counts as the dot (`1。6a`, `1，6a`, `1,6a` all mean `1.6a`), and punctuation an input method leaves after an id is dropped (`check 1.1a，`, `check 1.1a。` mean `check 1.1a`). A stray space around an option is dropped (`"--again "` is `--again`); a word the command does not take is shown with ui.visible, so a stray space appears as · (「用法不对：不认识的参数：x·」). Command names are folded too (`Check`, `ｃｈｅｃｋ` mean `check`).

A full-width space or a non-breaking space **inside** a word of the command line (`python3 tools/course.py check　1.14a`: the shell does not split there), an option written with full-width or input-method dashes (`——answer`, `－－answer`), or full-width letters in an option name (`--ａｇａｉｎ`) is a usage error (exit 64) that says what happened:

```text
用法不对：命令里混进了全角字符（中文输入法打出来的空格或符号）：check〔全角空格〕1.14a。切回英文输入法，把这一段重新打一遍。
用法不对：命令里混进了全角字符（中文输入法打出来的空格或符号）：--ａｇａｉｎ。混进来的是：ａ、ｇ、ｉ、ｎ。切回英文输入法，把这一段重新打一遍。
```

What still works: full-width digits and letters inside an id (`check １.６ａ`), a full-width space at the very start or end of a word, a full-width command name (`ｃｈｅｃｋ`). The values of `--answer`, `--done`, `--stuck`, `--next`, `--unclear` and `--slow` are the learner's own text and may contain any character.

Other usage errors (exit 64; the second line is always 「看这个命令的说明：python3 tools/course.py <命令> -h」) call a word that starts with `-` a **选项** and every other word a **参数**: 「用法不对：不认识的选项：--wirte」, 「用法不对：不认识的参数：now」, 「用法不对：不认识的选项：--wirte；不认识的参数：now」, 「用法不对：选项 --confidence 后面要跟一个值」, 「用法不对：选项 --confidence 不能是 9（可以用的值：1、2、3、4、5）」, 「用法不对：选项 --confidence 要是一个整数，现在是 x」, 「用法不对：缺少必须的参数：<站或课>」.

## 9. HINTS

Exactly four non-empty, different strings per station, in this order: **方向** (which way to think) → **位置** (which step or place) → **相似例子** (a similar case that is not the answer) → **答案与解释** (the full answer and why).

```python
HINTS = {
    "1.6b": [
        "一共三件事：建仓库、放进暂存区、提交。检查结果里的“还缺什么”说的是哪一件？",
        "先运行 git status：它说文件在哪个区域？",
        "要提交一个叫 todo.txt 的文件：先 git add todo.txt，再 git commit -m \"docs: 添加待办\"。",
        "答案：在 my-site 里运行 git add index.html，再运行 git commit -m \"feat: 第一版首页\"。"
        "解释：git add 把改动放进暂存区，git commit 把暂存区拍成快照。",
    ],
}
```

`hint 1.6b` shows the next level each time and logs it. After level 4 the station is marked 带扶手完成 and a cold redo is due 3-7 days later; a pass after that window, on a day without hints, turns it into 通过. A string may contain line breaks; they are kept.

## 10. SCENARIOS and the builder context `sc`

```python
def build_start(sc):          # exactly one parameter; returns nothing
    ...

SCENARIOS = {"start": build_start, "1.6b-broken": build_broken}
```

Every lesson defines `start`: the practice state a learner has just before this lesson. The tool runs a builder like this (`scenario` command, `review`, `exam`, `validate --build`):

1. The scenario folder `<playground>/<scenario id>` is created. A non-empty folder is never overwritten without `--reset`, and `--reset` deletes a folder only when it holds the tool's marker file `.playground`. A folder outside the playground, a link or a plain file in the way is refused. A folder whose marker says the build never finished is the tool's own and is rebuilt by the plain command (section 15.1 has the full table).
2. **The tool writes the `.playground` marker itself** (with the seed, the form and, after the build, the facts). Builders never write or delete it. The marker is version 2: its first key is `"note": "学习工具的记号文件，请不要改动或删除，也不用打开。"`, then `tool`, `marker` (2), `scenario`, `key`, `lesson`, `seed`, `form`, `built`, `complete`, and `data`: the facts and the todo lines as **base64 of UTF-8 JSON** `{"facts": {...}, "todo": [...]}` (XOR-ed with a one-byte `"mask"` in the rare case that plain base64 would contain a piece of an answer). No fact value, no todo line and no piece of four or more characters of one appears in the file, so a learner's own `grep -rin <word> .` never counts the marker and `cat .playground` shows no answer. **This protects against accidents, not a secret**: never make anything secret a fact. Version 1 markers (plain `facts` and `todo`) are still read; a marker whose `data` cannot be decoded counts as an unfinished build of the tool (`ctx.scenario()` reports it as not built; the plain `scenario` command refuses it, `--reset` rebuilds it). Tests read a marker with `courselib.scenario.read_marker(folder)` (decoded `facts` and `todo`), never with `json.loads`.
3. Your builder fills the folder through `sc`. Every relative path you pass is inside the scenario folder; `..` and absolute paths are refused (检查器出问题).
4. What the builder prints (standard output, standard error, warnings) is discarded; an exception becomes 检查器出问题 and the half-built folder is rebuilt by running the same `scenario` command again.

The learner's real folders (`~/Developer/my-site`, the workspace) are never written by a builder. A `start` scenario that needs "the learner's site in state S4" builds a copy of it inside the scenario folder with `sc.state("S4")`.

### 10.1 Attributes

`sc.root` (the scenario folder, `Path`), `sc.seed` (int), `sc.rng` (a `random.Random` seeded with it), `sc.form` (`"A"` / `"B"` in an exam, else None), `sc.key`, `sc.id`, `sc.lesson_id`, `sc.now` (build time, follows `COURSE_NOW`), `sc.workspace` (workspace root, read-only use), `sc.facts` (what was recorded so far).

### 10.2 Files

| Signature | Does |
|---|---|
| `sc.path(rel=".") -> Path` | absolute path inside the scenario |
| `sc.show(rel=".") -> str` | as the learner reads it: `~/Developer/playground/1.6-start/my-site` |
| `sc.mkdir(rel) -> Path` | creates the folder and its parents |
| `sc.write(rel, text, exact=False, executable=False) -> Path` | UTF-8 text with LF line ends; unless `exact`, the text is dedented, one leading line break dropped and exactly one final line break kept, so a triple-quoted string can be indented with the code |
| `sc.write_bytes(rel, data) -> Path` | raw bytes (another encoding, CRLF) |
| `sc.append(rel, text) -> Path` | appends exactly `text` |
| `sc.touch(rel) -> Path` | an empty file |
| `sc.copy_in(source, rel) -> Path` | copies a file or folder **from the workspace**, skipping `.git`, `__pycache__`, `.DS_Store`. Anything under `starter/` comes from the original recorded in `tools/courselib/starter_manifest.json`, **never from the workspace copy**, which a beginner may have edited (plan G11a): a folder gives every manifest file below it, a file gives that file. A `starter/` path the manifest does not know is a builder mistake: 检查器出问题 with 「搭建练习场的代码要复制 <path>，但起始文件的原样清单里没有它。」 |
| `sc.remove(rel)` / `sc.move(source, dest)` | delete / rename inside the scenario |
| `sc.set_mtime(rel, when)` | modification time from a `datetime` |

```python
sc.copy_in("starter/hello-fx", "hello-fx")
sc.write("hello-fx/notes.txt", """
    第一行
    第二行
""")
sc.write_bytes("crlf.txt", b"a\r\nb\r\n")
```

### 10.3 Git

The builder's Git ignores the learner's global and system configuration, never signs, never runs hooks (`--no-verify`), commits as `练习场 <playground@example.invalid>`, uses `main` as the first branch, and can only reach local paths (no network). It never looks above the scenario folder (`GIT_CEILING_DIRECTORIES`), and `sc.git_commit` refuses (检查器出问题) a folder that is not itself the top of a repository, so a forgotten `sc.git_init` can never commit into some repository around the playground (a stray `git init` in `~/Developer`). On a machine like that of plan G7 a plain `git commit` fails until lesson 1.6; scenarios never depend on that.

| Signature | Does |
|---|---|
| `sc.git_init(rel, branch="main", bare=False) -> Path` | a repository in the sub-folder `rel` (the scenario folder itself cannot be one, because the marker would show up in `git status`) |
| `sc.git_commit(rel, message, add="all", date=None, author=None, allow_empty=False, force=False) -> str` | stages and commits; returns the full hash. `add`: `"all"` (like `git add -A`), a path or list of paths, or None (commit what is staged). `date`: a `datetime`; default is the build time plus one minute per commit, so order is stable. `author`: `("同事小林", "lin@example.invalid")`. `force`: add ignored paths; it applies only when `add` is a path or a list of paths (with `add="all"` ignored files stay out, as with `git add -A`). |
| `sc.git(rel, *args, date=None, author=None, check=True)` | any other git command in `rel` (with the same overrides); returns its output text, or the `RunResult` with `check=False`. The first argument must be the subcommand: global options (`-C`, `-c`, `--git-dir`, `--work-tree` …) are refused, because they would lead out of the scenario |

```python
sc.git_init("notes")
sc.write("notes/a.txt", "一")
sc.git_commit("notes", "docs: 第一条笔记", date=sc.ago(days=2))
sc.git_init("remote.git", bare=True)
sc.git("notes", "remote", "add", "origin", str(sc.path("remote.git")))
sc.git("notes", "push", "-q", "origin", "main")
```

### 10.4 Seeded randomness

The seed makes names differ between learners and attempts, and makes the same seed rebuild the same state. Use only these (or `sc.rng`), never the `random` module directly.

| Signature | Returns |
|---|---|
| `sc.pick(options)` | one item |
| `sc.sample(options, count)` | `count` different items |
| `sc.randint(low, high)` | an int, both ends included |
| `sc.word()` / `sc.words(count)` | neutral lower-case English words for names (`cedar`, `heron` ...) |
| `sc.ago(days=0, hours=0, minutes=0)` | a `datetime` before the build time |

### 10.5 Telling the check and the learner

| Signature | Does |
|---|---|
| `sc.fact(key, value) -> value` | records a JSON-serialisable fact in the marker; checks read it as `info.facts[key]`; exam task texts use it as `{key}` |
| `sc.todo(text)` | a line shown to the learner after the build ("练习仓库在这里：…"); also shown under an exam task's text |
| `sc.state(name, base=".") -> Path` | builds ladder state `"S0"`…`"S7"` of plan I6 under `base` and returns the path of the `my-site` folder in it (implemented by `tools/courselib/states.py`) |
| `sc.site_before(lesson_id=None, base=".") -> Path` | builds the ladder state the learner has just before `lesson_id` (default: this lesson) and records the facts `site`, `site_state`, `site_commits`, `site_owner` (and `site_remote` from S7); see section 15.3. **Use this in `start`** for every lesson that works on the website |

```python
def build_start(sc):
    repo = "notes-" + sc.word()
    count = sc.randint(2, 4)
    sc.git_init(repo)
    for n in range(1, count + 1):
        sc.write(f"{repo}/day-{n}.txt", f"第 {n} 天")
        sc.git_commit(repo, f"docs: 第 {n} 天的笔记")
    sc.fact("repo", repo)
    sc.fact("commits", count)
    sc.todo("练习仓库在这里：" + sc.show(repo))
```

## 11. REVIEW

Spaced-review items. Only `tier: "fluent"` items are scheduled (Leitner boxes: 2 days, 1 week, 3 weeks, 2 months, 6 months); an item enters box 1 when its station first passes. `lookup` (know where to look it up) and `aware` (know it exists) items are kept for the tutor and for reading, not scheduled.

How the `review` command schedules, serves and grades each type (a right answer moves one box up, 模糊 keeps the box, a miss goes back to box 1 due the next day, right in the last box retires the item; at most 8 items or about 10 minutes per session; the return routine after a break; how a `do` item is handed out and graded with `review --grade`), with examples and advice on what makes a good item for a beginner: section 16.

Common keys: `id`, `type`, `tier`, `q` (the question, Chinese). Optional: `station` (the station it belongs to; default: the last station), `rule` (a rule id of this lesson), `explain` (shown after answering).

| `type` | Extra keys | How it is graded |
|---|---|---|
| `recall` | `a`: the model answer | the learner answers in their head, sees `a`, and grades themselves |
| `predict` | `options` (2-6 strings), `answer` (letter) | auto-graded: "what will this command print?" |
| `which` | `options`, `answer` | auto-graded: "which command / file / setting?" |
| `fault` | `options`, `answer` | auto-graded: "what is wrong here?" |
| `do` | `scenario` (a key of SCENARIOS), `check` (a function `check(ctx)`) | the tool builds a fresh copy of that scenario for the item, the learner does the task there, and `check` grades it with the three outcomes |

Optional for choice types: `shuffle` (bool; the tool may shuffle options when true). A choice item must not have `a`; a recall item must not have `options`.

```python
REVIEW = [
    {"id": "1.6-r1", "type": "recall", "tier": "fluent", "station": "1.6b",
     "q": "git add 和 git commit 各做什么？", "a": "git add 放进暂存区；git commit 把暂存区拍成快照。"},
    {"id": "1.6-r2", "type": "predict", "tier": "fluent", "station": "1.6b",
     "q": "改了 a.txt 但还没 git add，git status 会把它列在哪里？",
     "options": ["Changes to be committed", "Changes not staged for commit", "Untracked files"],
     "answer": "B", "explain": "改了但没放进暂存区，就是“没暂存的改动”。"},
    {"id": "1.6-r3", "type": "do", "tier": "lookup", "station": "1.6b",
     "q": "在练习仓库里提交一个新文件。", "scenario": "start", "check": _new_file_committed},
]
```

A `do` item's check calls `ctx.scenario()` (or `ctx.scenario("start")`) to find the copy built for the review. The station check and the `do` check can share one helper function, as in the worked example.

## 12. EXAM

Cold tasks for the gate the lesson belongs to (plan section 4: `gate-0` for 0.x, `gate-a` for 1.1-1.5, `gate-b` for 1.6-1.10, `gate-1` for 1.11-1.16). No hints are offered during an exam. A sitting holds **one task of each lesson** the gate covers (section 15.5), so every lesson needs at least one task; two tasks per lesson let the tool draw one at random and give the learner extra practice. A task's `minutes` is what the head of a sitting adds up, so keep it honest.

```python
EXAM = [
    {
        "id": "1.6-x1",                       # lesson id + "-" + word
        "gate": "gate-b",                     # must be this lesson's gate
        "title": "给一个文件夹建仓库并提交",      # short name for the results table
        "minutes": 5,                         # 1-15
        "build": build_x1,                    # build(sc): sc.form is "A" or "B"; uses sc.seed
        "task": {                             # two parallel forms: same skill, different surface
            "A": "文件夹 {dir}/{folder} 还不是仓库。把它变成仓库，并提交里面的 {file}。",
            "B": "把 {dir}/{folder} 建成仓库，只提交 {file}，不要提交其他文件。",
        },
        "grade": grade_x1,                    # grade(ctx): ctx.scenario() is the built task
    },
]
```

In the task text `{dir}` becomes the task's scenario folder as the learner reads it, and `{name}` becomes `sc.fact("name", …)`. Every placeholder must be a recorded fact (`validate --build` checks it for both forms with a fixed seed). The two forms must differ in text. The builder decides from `sc.form` what differs; the grading function reads `ctx.scenario().form` and `.facts`.

```python
def build_x1(sc):
    folder = "shop-" + sc.word()
    name = sc.pick(["menu.txt", "prices.txt"]) if sc.form == "A" else "index.html"
    sc.write(f"{folder}/{name}", "内容")
    sc.fact("folder", folder)
    sc.fact("file", name)

def grade_x1(ctx):
    info = ctx.scenario()
    repo = ctx.need_repo(info.path / info.facts["folder"], "考试文件夹", praise=True)  # the task asks for git init
    ctx.expect(repo.file_at("HEAD", info.facts["file"]) is not None,
               "文件已经提交", "要求的文件还没有进入提交", where="最新提交", saw="里面没有这个文件")
```

## 13. rules.md (rule cards)

One card per rule id in `META["rules"]`, at most two per lesson, in the format of plan I2. Every field name is bold and followed by a full-width colon `：`; all thirteen fields and the two second labels (`复核周期`, `不遵守的后果`) are mandatory.

```markdown
### GIT-03 提交前先看改了什么

- **约束力**：必须（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：提交前先运行 git diff --staged，看一遍这次要提交的改动。
- **谁说的**：Pro Git 第 2 版 2.2 节 https://git-scm.com/book/zh/v2/…
- **核对日期**：2026-11-19；**复核周期**：12 个月
- **谁来管**：评审人；**不遵守的后果**：把不想要的改动带进历史，事后很难拆开。
- **为什么**：……
- **正例**：（可照抄；可以接一个缩进的代码块）
- **反例**：……
- **怎么检查**：复习题 1.7-r2；或者"人工检查：……"
- **例外**：无
- **旧教程提醒**：无
- **学于**：1.7
```

What `validate` rejects:

- a missing field, a missing `复核周期` or `不遵守的后果`, or field names without bold marks;
- **约束力** that does not start with 必须 / 推荐 / 参考, or has no scope `（适用范围：…）` drawn from 本课程 / 本机 / 所在团队 / 所有项目 (several allowed, separated by 、); text after the bracket is allowed;
- **规则类型** that is not exactly one of: 标准, 行业要求, 岗位期望, 惯例·事实标准, 惯例·平台与工具, 规范·组织, 规范·团队约定, 规范·本课程约定 (a bracketed remark after the label is allowed; 个人偏好 is never a rule type; the dot is `·` U+00B7). `validate` still lets 岗位期望 through, but a card never uses it: STANDARDS.md section 2 says 岗位期望 is not one of the seven types and does not go through the seven steps, and `handbook/00-how-to-read-a-rule.md` says a card's type is one of the seven. An employer's expectation goes into the card's text or STANDARDS.md section 5, not into **规则类型**;
- **谁说的** without a URL, except for 规范·团队约定 and 规范·本课程约定;
- **核对日期** that is not `YYYY-MM-DD` at the start, or lies in the future;
- **学于** that is not this lesson's id;
- a card whose id is not in `META["rules"]`, a rule id without a card, two cards with one id, more than two cards.

A **warning** appears when the type is outside the family plan section 4 gives in brackets (for example the plan says 惯例 and the card says 规范·组织). Keep the honest label from the source if you are sure, and say so in your report. Classify with the seven-step procedure of STANDARDS.md section 2 (plan G3; its wording is the reference): regulator / court / customer / auditor / platform can penalise you → 行业要求; issuing body from the list of standards bodies, with a number → 标准; public, versioned or dated specification or framework that many unrelated projects and tools follow, and not one organisation's guide for its own people → 惯例·事实标准; 「它只是某一个工具或平台本身的工作方式或期待吗（包括它在自己的官方文档里教你怎样用它）？」 → 惯例·平台与工具; one organisation's guide in its own name, written for its own engineers or for its own readers (for example MDN's tutorials) → 规范·组织; this team or this course → 规范·团队约定 / 规范·本课程约定.

## 14. validate and testing your lesson

```bash
python3 tools/course.py validate               # every lesson under stages/
python3 tools/course.py validate 1.6           # one lesson (or a folder path)
python3 tools/course.py validate --build 1.6   # also build every scenario and both forms of every exam task in a temporary folder
python3 tools/course.py validate --json 1.6    # machine-readable
python3 tools/course.py validate --complete    # acceptance: every lesson of plan section 4, lesson.md present, ≥ 4 exam tasks per gate
```

Exit code 0 when there is no error (warnings allowed), 1 otherwise. Findings carry the plan section they come from (`[G5]`, `[I2]`, `[I3]`, `[§4]` ...). `--complete` (acceptance) also requires, for every gate, at least 4 tasks whose `gate` is that gate and a task for every lesson of the gate that exists (「1.10 课还没有关卡 gate-b 的考题：一场考试每课出一题，每一课至少要有一道」).

Mechanical checks of the text, all **warnings** (they never change the exit code). Each names the line (「lesson.md 的第 N 行」, 「lesson.py 的第 N 行」, 「rules.md 的第 N 行」), quotes what it found and gives the fixed form, so a repair can copy the expected line from the message. The fixed sentences are constants of `courselib.validate` (`SAVE_LINE`, `MID_LINE`, `HINT_LINE`, `CHECK_LINE`, `G6_LINE`, `CLOSING_*`, `SUMMARY_*`, `TUTOR_SENTENCES`, `TERM_OWNERS`, `COMMAND_OWNERS`). Code blocks are told apart from prose by their fences; headings inside code blocks are not headings.

| Code | Finding | Example message |
|---|---|---|
| `[G5]` | a heading `## 第 N 站：……（约 X 分钟）` (N a digit or 一…九, brackets full- or half-width) states minutes different from `META["stations"][N-1]["minutes"]`. Only the first 「约 X 分钟」 inside the bracket at the end counts, so 「（约 25 分钟，如果要搬课程文件夹，再加约 10 分钟）」 is read as 25; headings without minutes are ignored | 「lesson.md 第 12 行写的是第 1 站约 30 分钟，META 里 1.6a 是 25 分钟：两处要写同一个按计划 G5a 算出来的数」 |
| `[I3]` | the whole text of an option (trimmed, half-width, lower-case) is a word the review session reads as a command: `q`, `quit`, `exit`, `退出`, `结束`, `不做了` (end), `s`, `skip`, `跳过` (skip) (`courselib.commands.review.RESERVED_WORDS`). Checked: `options` of `which` / `predict` / `fault` items and literal option lists of `ctx.quiz(...)` / `ctx.choose(...)` | 「复习题 1.7-w2 的选项 A 只有「q」：复习时输入 q 会结束这次复习，学习者照着选项原文输入就答不了这一题。把选项写完整，例如「按 q」」 |

**Save points `[I1]` (V1).** Inside every station (from its 「## 第 N 站」 heading to the next level-2 heading) the last line that starts with `> **存档点` must be exactly 「> **存档点 1.6a**：到这里可以安全停下。下次可以对导师说“从 1.6b 继续”。」, and after the last station 「…下次可以对导师说“从 1.6 的收尾继续”。」. The message says what differs: English straight quotes, a wrong sentence (「说的话应该是“从 1.6 的收尾继续”，现在是“从 1.7 开始”」), a missing 「可以」, text in the middle or after the sentence. A station without such a line gets 「第 N 站（1.6b，…起）的末尾没有存档点」; a save point that names another station is reported too. A mid-station save point before a gate, 「> **中途存档点**：<做完了什么>，到这里可以安全停下。下次可以对导师说“做小关卡 gate-0”。」, is allowed; its gate must be the gate of the lesson in the syllabus. Lines inside code blocks (pasted tool output) are not read. When lesson.md has no station headings at all, the older checks (the text mentions 存档点 / check / hint of every station) stay in force.

**The closing section `[I1]` (V2).** The heading is 「## 收尾（约 N 分钟）」. Its numbered steps start with, in this order: 「全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.6`」; 「行规笔记：运行 `code notes/my-rules.md`，在小标题「GIT-01 <title>」「GIT-02 <title>」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。」 (titles exactly as the rules.md headings; 「各」 only for two rules; a lesson without new rules has no such step and is warned if it has one); 「一句话日志：`python3 tools/course.py journal`」; from lesson 1.13 on 「备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。」 (lesson 1.12 itself defines the group: its backup step must contain `git push`, in the step's line or in the code block under it). Only the first line of a step is compared; indented lines and code blocks under it (a pasted sample) are allowed. Which step is which (check, notes, journal, backup) is decided by the step's first line; the lines under it are read only when the first line names none of them, so a backup step whose pasted `git status` lists `notes/my-rules.md` stays the backup step. A lesson's own steps follow, numbered on. The last non-empty prose line of the section is 「都做完，这一课就完成了。下次可以对导师说“从 <next> 开始”。」; for 1.5 and 1.10 (the gates whose `after` in `syllabus.GATES` is that lesson, except the gates that sit inside a station, `validate.GATES_INSIDE` = gate-0 in 0.4c and gate-1 in 1.16b) it is 「都做完，这一课就完成了。下一步是小关卡 gate-a：它是单独的一段时间，开考时工具会打印题数和预计用时。下次可以对导师说“做小关卡 gate-a”。」; the last lesson of the syllabus (1.16) ends with 「下次可以对导师说“准备阶段 2”。」 (any words before it). So 0.4 ends with 「从 1.1 开始」. Lessons outside the syllabus get every check except this last line.

**The parts of a station `[I1]` (V3).** Every station has the level-3 headings 「### 概念」「### 跟我做」「### 补全」「### 自己做」 (a heading may go on after the word, e.g. 「### 自己做：备份你的学习工作区」), in this order. The two last non-empty lines before the station's save point must be 「- 提示：`python3 tools/course.py hint 1.6a`（每运行一次多给一级）」 and 「- 检查（先回到学习工作区）：`python3 tools/course.py check 1.6a`」; only a 「> **想多了解（可跳过）：…**」 box may stand between them and the save point. A `###` part after 「自己做」 (an exam sitting) is allowed only behind a 「中途存档点」 line; the hint and check lines then end the station after that part.

**Marks of plan G6 `[G6]` (V4).** When lesson.md has at least one 〔对照文档，界面可能不同〕 or 〔建课时无法验证〕, the line 「和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。」 occurs exactly once, on its own line, after the first mark, not in a blockquote, word for word (the ASCII-quoted variant is reported). A mark inside backticks or inside a code block is reported. `META["unverified_steps"]` must be non-empty exactly when the text has marks; a G6 line without any mark is reported as well.

**Sentences to the tutor `[G2]` (V5).** In lesson.md (code blocks included, so stale pasted tool output is found) and in every string constant of lesson.py except docstrings (hints, feedback, review items, exam texts), a quoted sentence the learner says to the tutor (after 「对导师说」, 「跟导师说」, 「向导师说」, 「和导师说」, or 「导师……，对它说」; quotes “ ”, " " or 「」; the tutor's own words such as 「导师说“…”」 or 「导师会对你说“…”」 are not read) that is about going on or getting help (it contains 继续, 开始, 收尾, 急救, 干活, 关卡, 讲解, 讲给, 上课, 对不上, 阶段, 回来 or 回归) must be one of the fixed sentences (`validate.TUTOR_SENTENCES`: 开始上课, 从 1.6b 继续, 从 1.6 的收尾继续, 从 1.7 开始, 做小关卡 gate-a, 请问我 gate-0 的讲解题, 急救：…, 干活：…, 回到上课, 课文对不上, 我们来做入学问卷, 帮我把课程安置到 ~/Developer, 我先不搬，帮我在 ~/Developer 建一个入口, 我回来了，带我走回归流程, 请解释这条命令的每一部分，先不要运行, 准备阶段 2). The message names the right form (a bare “急救” gets 「求助要说“急救：<一句话说现象>”」, “继续下一阶段” gets 「要说“准备阶段 2”」). Quoted words that are not said to the tutor (Git's own messages) are not read. Second check: a prose line of lesson.md (outside code blocks and inline code) with straight double quotes around Chinese text, one warning per line; lines with an odd number of quotes are skipped, and lines already reported for their resume sentence, save point or G6 line are not reported twice.

**The course folder `[G10]` (V6).** In lesson.md, lesson.py (every line) and rules.md: `Desktop/Code/fullstack-from-zero` anywhere outside lesson 0.2; the folder's name before the rename of 2026-11-21 as a path part (`/Engineering`, for example `~/Developer/Engineering`) anywhere; a `/Users/<name>` path whose name is ASCII (a Chinese placeholder such as `/Users/你的用户名`, an ellipsis `/Users/…`, `/Users/Shared` and `/Users/Guest` are fine; a fictional ASCII name such as `laowang` is reported, write `/Users/老王` or `你的用户名`); any `/private/tmp/` path. In lesson.md prose and lesson.py strings: 「课程文件夹」 (always), 「练习文件夹」 only on a line that also says fullstack-from-zero, and from lesson 1.6 on a bare 工作区 that clearly means the course folder: 「回到工作区」, or 工作区 directly before or after `~/Developer/fullstack-from-zero`. From lesson 1.12 on the 学习工作区 is a repository, so 工作区 next to `~/Developer/fullstack-from-zero` on a line that also says git, 仓库, 提交, 暂存, 干净 or 改动 is Git's word and is left alone (「~/Developer/fullstack-from-zero 的工作区是干净的」); 「回到工作区」 is always reported. Other uses of 工作区 (Git's working tree, 「在工作区运行」) are left alone.

**Optional material `[I1]` (V7).** A blockquote whose leading bold label (plus a bracket right after it) contains 选做, 选读, 可选 or 可以跳过, or starts with 想多了解 without being 「想多了解（可跳过）」, and any heading that uses one of those words as a label (at the start, in brackets, after 「，」 or a comma, before 「：」, at the end of the heading, or followed by 练习 / 题 / 部分 / 内容 / 阅读 / 材料, or by 的 + 进阶 / 部分 / 内容 / 阅读 / 材料 / 练习 / 题: 「### 选做：……」, 「### ……（可选）」, 「### 可选的进阶」, 「### 这一段可选」, 「### 进阶，可选」, 「### 补充（可以跳过的部分）」) or contains 想多了解 other than the closing 「## 想多了解」, is reported (a word inside a sentence, 「### 自己做（可选的两种做法都行）」, is not) with the one label 「> **想多了解（可跳过）：<小标题>**」.

**The rule summary `[I2]` (V8).** For a lesson with rule ids, the section 「## 本课行规」 holds a table whose header is exactly 「| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |」, one row per rule id, and the line 「完整卡片在本课文件夹的 `rules.md`。」 on its own. The cells 约束力 and 规则类型 must be the card's text (compared after removing white space, punctuation and symbols, so 「必须(适用范围: 本课程)」 equals 「必须（适用范围：本课程）」 and 「・」 equals 「·」); the message quotes both. On the card itself (`rulecards.binding_problems(card)`, a warning in addition to the errors of `check_card`): every 必须 / 推荐 / 参考 outside brackets in 约束力 is followed directly by 「（适用范围：……）」 (「推荐（适用范围：所有项目），本课程里按必须对待」 is reported), and every scope bracket names only 本课程 / 本机 / 所在团队 / 所有项目. A missing 复核周期 was already an error of `check_card` and stays one.

**Old-tutorial boxes `[G4]` (V9).** Every blockquote 「> **旧教程提醒**：…」 in lesson.md (for a list item 「> - **旧教程提醒**：…」 the item only) and every 旧教程提醒 field of a rule card that is not 「无…」 must contain a year (1900-2099), a version number (`2.23`, `v2025.5`, 「第 2 版」), a date, or a named release (a macOS name such as Catalina, Big Sur, Monterey, Ventura, Sonoma, Sequoia, Tahoe; or a product with a major version: 「Python 3」, 「macOS 15」, 「Git 2」), with or without spaces next to Chinese text (「从macOS Catalina起」, 「从Python 3起」). A product name followed by a number and a measure word is a count, not a release: 「Git 2 种写法」 does not count. Lesson and station ids (「第 1.12 课」, `1.6a`) and check dates (「2026-11-19 核对」, 「核对日期：2026-11-19」) do not count: they say when the builder looked, not since when.

**The old form of git config `[G4]` (V10).** `git config` followed by an option or a key, without one of the subcommands `set`, `get`, `unset`, `list` (or `edit`, `rename-section`, `remove-section`, `get-color`, `get-colorbool`), in any code block or inline code of lesson.md, or in a literal hint of `HINTS = {...}` in lesson.py (found by reading the source; reported as 「HINTS['1.6a'] 的第 3 级提示（lesson.py 的第 N 行）」). `git config -h` / `--help` and a bare `git config` are fine. Exempt: the blockquote of a 旧教程提醒, and a code block that holds Git's own identity message (「*** Please tell me who you are.」), which quotes the old form.

**Across lessons `[X]` (V11).** In addition to the pair checks: the same English gloss (`en`, compared case-sensitively, so `PATH` and `path` differ) under two different terms is reported once, naming every lesson and term. For the terms and commands whose owner the course decided (`validate.TERM_OWNERS`: 路径 0.2, 递归 1.2, 令牌 1.9, 提交签名 1.6, 分支 1.6, 讲解题 0.4; `validate.COMMAND_OWNERS`: `python3 tools/course.py scenario` 0.1, `git --version` 1.6, `git commit -m … -m …` 1.10, `mkdir` 0.2, `git config get` 1.6, `git diff <文件名>` 1.7, `git log -1` 1.11, `python3 tools/course.py exam gate-…` and `… --grade` 0.4) the message names the owner and says which lesson drops the entry, also when the owner itself does not list it: 「术语「递归」在 1.2 和 1.3 两课里都算成了第一次出现；按约定它归 1.2 课：1.3 课的 TERMS 去掉这一项，课文里留一句简短的解释」, 「命令 'mkdir' 归 0.2 课（课程约定的归属），1.1 课的 new_commands 不要把它算成新命令」. Commands are compared with `...` read as `…`, white space collapsed and any `gate-x` read as one gate (so `exam gate-0` in 0.4 and `exam gate-1` in 1.16 are the same command).

**The header line `[G5]` (V12).** The line with 「**用时**」 in the first 15 lines must read 「**用时** N 站，约 X 分钟」 (more words may follow); N is the number of stations in META and X is the sum of the stations' `minutes` plus the minutes of the closing heading (read also from 「## 收尾（5 分钟）」, whose missing 约 is V2's finding). A lesson.md without such a line is reported.



Test in a simulation home (plan G8, section 17.1), never in the real one. Environment variables the tool honours:

| Variable | Effect |
|---|---|
| `HOME` | the learner's home (Git's global config, `~/Developer`) |
| `COURSE_PLAYGROUND` | the playground folder (default `~/Developer/playground`) |
| `COURSE_NOW` | "now" as `2026-11-19` or `2026-11-19T10:30:00`, for dates in state, hints, review and commit dates of builders. A test override: the sessions it creates are stored like real ones, so use it only in a throw-away workspace |
| `COURSE_NONINTERACTIVE=1` | never prompt; answers come from `--answer` (a needed answer that is missing is a usage error, exit 64) |
| `NO_COLOR` | no colours (colours appear only on a terminal anyway) |
| `COURSE_DEBUG=1` | builders only: a traceback on standard error when something breaks |

A typical round for one station:

```bash
export COURSE_NOW=2026-11-19T10:00:00
python3 tools/course.py scenario 1.6 --reset          # build the start state
python3 tools/course.py check 1.6b                    # expect 还没达标, exit 1, with a useful "还缺什么"
# ... do the exercise in the playground as the learner would ...
python3 tools/course.py check 1.6b --answer 3         # expect 通过, exit 0
python3 tools/course.py hint 1.6b                     # level 1, then 2, 3, 4
cat learner/last-result.json                          # what the tutor sees
```

Exit codes of every command: 0 passed / ok, 1 not yet (also: refused, or the learner left a prompt), 2 checker problem, 64 usage error.

## 15. Scenarios, the state ladder and exam tasks

What the `scenario` and `exam` commands do with what you write in sections 10 and 12, the state-ladder helpers, and complete examples. Binding context: plan I4 (the commands), I6 (the state ladder), I7 (gates) and section 4 (which lessons feed which gate).

### 15.1 What the learner sees

```bash
python3 tools/course.py scenario 1.7          # the start scenario of 1.7 (also: 1.7-start)
python3 tools/course.py scenario 1.7b         # a station scenario
python3 tools/course.py scenario 1.7 --reset  # throw the old copy away and build afresh
python3 tools/course.py scenario              # list every scenario
```

Output of a successful build (exit 0). The lines under 这里有什么 are your `sc.todo` lines; the steps under 接下来 are added by the tool. A station scenario (`1.7b` or `1.7b-broken`) names the check of its station (`1.7b`). A `start` scenario names no station, because which station looks at the start state is the lesson's business (the first station may be a quiz): it sends the learner back to the lesson text. The tool's own `cd` step is left out when one of your `sc.todo` lines already contains a `cd ` command, so the screen never shows two different `cd` lines:

```text
练习场景 1.7-start 搭好了。
位置：~/Developer/playground/1.7-start

这里有什么：
  网站的副本在这里：~/Developer/playground/1.7-start/my-site

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.7-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.7 --reset
```

For a station scenario the second step reads `做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.7b`. The workspace is shown through `~/Developer/fullstack-from-zero` whenever that path leads to it (section 6.2); without an entrance a learner who stayed sees the real place (for example `cd ~/Desktop/fullstack-from-zero`). The rebuild command carries the id the learner typed, normalised (`1.6B-BROKEN` → `1.6b-broken`; `1.6` stays `1.6`, `1.6-start` stays `1.6-start`). When the scenario was already built (「已经搭好了（…），这次没有动它。」) the last line is 「想从头再来一份（会删掉你在里面做过的改动）：python3 tools/course.py scenario 1.7 --reset」. The old one-line sentence 「练习场里的东西随便改。改乱了就加 --reset 重搭一份，练习场外面的文件不会受影响。」 is gone: lessons that pasted it re-paste the two lines.

Running the same command again does **not** rebuild: it says 之前已经搭好了 and shows the same lines (exit 0), so a learner who forgot where the folder is can simply ask again without losing work.

Safety rules (all enforced by the tool; a refusal is exit 1 with a Chinese explanation):

| Situation | What happens |
|---|---|
| the target folder is empty or missing | built |
| it holds a complete earlier build of the same scenario, no `--reset` | not rebuilt: shown again with 之前已经搭好了 (exit 0) |
| it holds a build the tool started but never finished (the marker says `"complete": false`: Ctrl+C, a builder that raised, git missing), no `--reset` | rebuilt: the half-built folder belongs to the tool, so the plain command is enough |
| it holds something else that carries the marker, no `--reset` | refused: 这个文件夹里已经有东西了, ending with 「工具不会覆盖它。想重新搭一份（会删除这个文件夹里现有的全部内容，再重新搭建）：python3 tools/course.py scenario <id> --reset」 (exam folders keep the older wording) |
| it holds something without the marker (or the marker is a link), with or without `--reset` | refused: 不是工具搭的; nothing is deleted, and `--reset` is not suggested |
| `--reset`, the folder carries the marker `.playground` and lies inside the playground | deleted and rebuilt |
| the scenario folder itself is a link (wherever it points) | refused: 这个位置是一个链接 |
| a folder on the way to it is a link that leads out of the playground | refused, also with `--reset` and also when the place it leads to carries a marker (links are resolved before comparing) |
| a scenario id or `COURSE_PLAYGROUND` that climbs out with `..` | refused |
| the playground is the disk root, the home folder or a folder around it; the workspace, a folder around it or a folder inside it; `~/Developer/my-site`, a folder around it or a folder inside it | refused: 练习场的位置不安全 |

Ctrl+C during a build prints 「搭建被打断了，练习场景 … 没有搭完整」 and the exact command to rebuild it (exit 1). A station check that needs a scenario that is missing or half built ends with 还没达标 naming that command, and that run is **not counted as an attempt** (section 6.5).

The playground is `COURSE_PLAYGROUND` or `~/Developer/playground`. If `~/Developer` does not exist yet, the first build creates it together with the playground (this happens only for scenarios used before lesson 0.2c).

### 15.2 Writing a SCENARIOS builder

A builder is `def build(sc): ...` with exactly one parameter. It fills `sc.root` through `sc` and returns nothing. The full list of `sc` helpers is section 10; the rules that matter most:

1. **Everything through `sc`.** Relative paths only; `..` and absolute paths are refused (检查器出问题). Copy workspace files with `sc.copy_in("starter/hello-fx", "hello-fx")`, never with `shutil` and a path you built yourself. `starter/` material always comes from `tools/courselib/starter_manifest.json` (section 10.2); whoever adds or changes a file under `starter/` on purpose runs `python3 tools/dev/build_starter_manifest.py --write` (a test fails until they do; section 17.6).
2. **Git through `sc` only** (`sc.git_init`, `sc.git_commit`, `sc.git`). These never sign and use the identity `练习场 <playground@example.invalid>`, so they also work on a machine like that of plan G7, where every plain `git commit` fails until lesson 1.6 has dealt with signing. A repository always lives in a sub-folder (`sc.git_init("notes")`), never in `"."`.
3. **Randomness through `sc` only** (`sc.word`, `sc.pick`, `sc.sample`, `sc.randint`). The same seed rebuilds the same state, which is what lets a check compute the expected answer.
4. **Record what a check needs** with `sc.fact(key, value)` (JSON values only), and tell the learner where things are with `sc.todo(text)` (plain Chinese, one line each, paths through `sc.show`).
5. **Never touch the learner's real folders.** A start scenario that needs "the learner's site as it is now" builds a *copy* with the state ladder (section 15.3).
6. **No commands in `sc.todo` that the lesson has not taught yet.** `cd` and the folder are added by the tool.

#### 15.2.1 A station scenario with a deliberate problem

A copy of the learner's site with an uncommitted change, for a lesson on `git restore`. Builders know what they wrote, so they record it as a fact instead of reading it back:

```python
WRONG_LINES = ["<p>这一行是不小心粘进来的。</p>", "<p>测试测试测试</p>", "<p>asdfgh</p>"]


def build_1_8a(sc):
    """A copy of the learner's site with one unwanted, uncommitted change."""
    site = sc.site_before("1.8")                  # state S4: a repository with one commit
    line = sc.pick(WRONG_LINES)
    sc.append(sc.facts["site"] + "/index.html", line + "\n")
    sc.fact("junk", line)
    sc.todo("网站副本里的 index.html 被改坏了：" + sc.show(sc.facts["site"] + "/index.html"))


SCENARIOS = {"start": build_start, "1.8a": build_1_8a}
```

The matching check reads the fact, never a hard-coded value:

```python
def check_a(ctx):
    info = ctx.scenario("1.8a")
    repo = ctx.need_repo(info.path / info.facts["site"], "网站副本 my-site")
    text = ctx.read(repo.path / "index.html")
    ctx.expect(info.facts["junk"] not in text, "多出来的那一行已经去掉了",
               "index.html 里还有那一行多余的内容", where="网站副本的 index.html",
               saw="多余的那一行还在")
    ctx.expect(repo.is_clean(), "工作区是干净的", "还有没处理的改动",
               where="git status", saw="不是 nothing to commit")
```

#### 15.2.2 The `start` scenario

Every lesson defines `start`: the practice state a learner has just before the lesson. For lessons that work on the website, that is the state-ladder copy:

```python
def build_start(sc):
    sc.site_before()                              # the state just before this lesson
    sc.todo("网站的副本在这里：" + sc.show(sc.facts["site"]))


SCENARIOS = {"start": build_start}
```

For lessons that do not need the site (stage 0, the terminal lessons 1.1-1.3), build whatever the lesson starts from: a copy of `starter/hello-fx`, a few files to look at, and so on.

### 15.3 The state ladder (S0-S7)

`tools/courselib/states.py` builds each state of plan I6 under any folder. The source is the original of `starter/my-site` in `starter_manifest.json`, never the learner's workspace copy (plan G11a); a local bare repository stands in for GitHub in S7. Every state is what the lessons' own texts and checks leave in `~/Developer/my-site` (audited against lessons 1.2-1.13 on 2026-11-19; checked again by building every state on 2026-11-20).

#### 15.3.1 What each state contains

| State | End of | `my-site` contains (files) | Commits (subjects, oldest first; the lesson that makes each) |
|---|---|---|---|
| S0 | 1.1 | does not exist | - |
| S1 | 1.2 | `index.html`, `style.css`, byte-for-byte the starter originals (1.2a) | - |
| S2 | 1.4 | the heading `你好，我是____` filled with a pen name and the paragraph replaced by a seeded sentence (1.4a); `.editorconfig` with `root = true`, UTF-8, LF, final newline, 2 spaces for html/css (1.4c) | - |
| S3 | 1.5 | plus `README.md`: `# my-site`, 里面有什么 (a list, `.editorconfig` included), 怎么查看 (the command in a fenced `zsh` block: `open index.html`), 现在做到哪了 (1.5b) | - |
| S4 | 1.6 | a repository on `main`, clean; the README also says 「这个网站现在用 Git 记录每一次改动。」 | 1 `第一版网页` (1.6c: index.html, style.css, README.md, .editorconfig) · 2 `在 README 里写上用 Git 记录改动` (1.6c) |
| S5 | 1.9 | the heading colour `#c2410c` (1.7b), then a seeded other colour (1.9a); `.gitignore` (`drafts/`, `*.tmp`, `.env`) and `drafts/colors.md` on disk, ignored (1.9a) | 3 `改了标题的颜色` (1.7b) · 4 `换了一个标题颜色` (1.9a) · 5 `添加 .gitignore` (1.9a) |
| S6 | 1.10 | a list item added, the heading size set | 6 `feat: 在首页加一条学习计划` (1.10b) · 7 `feat: 调大标题的字号` (1.10b) |
| S7 | 1.13 | plus `LICENSE` (MIT, the pen name as holder) and the README section `## 许可证` / `本项目使用 MIT 许可证，全文见 [LICENSE](LICENSE)。` in one commit (1.13a); the page address in the README, pushed (1.13b); the list line 「我会把网页放到网上」 changed to 「我已经把网页放到了网上」 and a footer link 「这个网页的源代码」 to `https://github.com/你的用户名/my-site`, pushed (1.13c); remote `origin` = `<base>/remote/my-site.git` (bare), upstream `origin/main`, 0 ahead | 8 `docs: 添加 MIT 许可证` (1.13a) · 9 `docs: 在 README 里写上网页地址` (1.13b) · 10 `feat: 列表里写上网页已经上线` (1.13c) · 11 `feat: 在页脚加上源代码的链接` (1.13c) |

Commit counts: S4 2, S5 5, S6 7, S7 11 (`states.COMMIT_COUNT`). Constants a lesson may compare with through its facts: `states.LESSON_COLOR` (`#c2410c`), `README_LICENSE`, `README_PAGES`, `LIST_BEFORE`, `LIST_AFTER`, `FOOTER_LINK`, `REPO_URL`, `EDITORCONFIG`, `DRAFT_NOTE`.

Notes:

- There is no state at the end of 1.7: the commit 1.7b makes (「改了标题的颜色」) first appears in S5. The copy built for 1.8 (S4) therefore has two commits while the learner's own site has three; lesson 1.9's `start` scenario adds the 1.7b commit to its S4 copy itself (three commits, `site_commits` = 3).
- The first five subjects are written the way a beginner writes before lesson 1.10; from the sixth on they follow Conventional Commits 1.0.0 with the types of commitlint's config-conventional. A bigger heading changes what the page shows, so it is `feat:`, not `style:`. Lesson 1.10 says honestly that the commits made before it keep their plain subjects.
- **Read counts and names from the facts** (`site_commits`, `site_owner`, …), never hard-code them; wherever a lesson states a number of commits it adds that the learner's own site may have more. Re-paste any ladder output you quote from a copy the current tool built.
- A test builds each state into a sandbox home's `~/Developer/my-site` and runs the real checks 1.4c (S2), 1.5b (S3), 1.6c (S4), 1.9a (S5) and 1.13a (S7).
- "The page online" in S7 is represented by `main` on the stand-in remote being the same commit as the local `main`: that is what GitHub Pages serves. The address in the README is the placeholder `https://你的用户名.github.io/my-site/` (plan G10).
- "Global signing handled" in S4 is a property of the learner's global Git configuration, not of the folder. The ladder never reads or writes any configuration outside the repository it builds, and the repositories carry no local `user.*` or `commit.gpgsign` setting.
- The pen name is one of 小林, 阿青, 小周, 阿木, 小禾, 阿远, 小舟, 阿北, chosen by the seed. Never the learner's real name.
- Commit dates are counted back from the build time (`COURSE_NOW` when set), none in the future. The same seed and the same build time give the same files and the same commit hashes. `states.build(..., manifest=None)` takes a manifest dict for tests; its `workspace` parameter is accepted but no longer read.

Example (`git log --oneline` in a copy of S7, newest first):

```text
… feat: 在页脚加上源代码的链接
… feat: 列表里写上网页已经上线
… docs: 在 README 里写上网页地址
… docs: 添加 MIT 许可证
… feat: 调大标题的字号
… feat: 在首页加一条学习计划
… 添加 .gitignore
… 换了一个标题颜色
… 改了标题的颜色
… 在 README 里写上用 Git 记录改动
… 第一版网页
```

#### 15.3.2 Which state comes before which lesson

`states.state_before(lesson_id)`: the state reached at the end of the latest ladder lesson *before* `lesson_id`.

| Lessons | State before the lesson |
|---|---|
| 0.1-0.4, 1.1, 1.2 | S0 |
| 1.3, 1.4 | S1 |
| 1.5 | S2 |
| 1.6 | S3 |
| 1.7, 1.8, 1.9 | S4 |
| 1.10 | S5 |
| 1.11, 1.12, 1.13 | S6 |
| 1.14, 1.15, 1.16 | S7 |

(`states.state_after(lesson_id)` gives the state at the end of a lesson.)

#### 15.3.3 The two helpers

| Signature | Does |
|---|---|
| `sc.site_before(lesson_id=None, base=".") -> Path` | builds the state just before `lesson_id` (default: the scenario's own lesson) in `<base>/my-site` and records the facts below. **Use this in `start`.** |
| `sc.state(name, base=".") -> Path` | builds state `"S0"` … `"S7"` by name in `<base>/my-site`; records no facts. Use it when a scenario needs a different state than the one before the lesson (a review item, a broken variant). |

Facts recorded by `sc.site_before` (read them in checks as `info.facts[...]`, or as `{site}` … in exam texts):

| Fact | Value |
|---|---|
| `site` | the folder inside the scenario, e.g. `"my-site"` or `"copy/my-site"` |
| `site_state` | `"S4"` |
| `site_commits` | number of commits in the copy (0 before S4) |
| `site_owner` | the pen name in the heading, or None before S2 |
| `site_remote` | from S7 on: the bare stand-in for GitHub inside the scenario, e.g. `"remote/my-site.git"` |

Both helpers refuse (检查器出问题) when `<base>/my-site` already exists. For S0 the returned folder does not exist: that is the state.

### 15.4 Writing an EXAM task

An exam task is a cold practical: the learner gets only the task text, no hints, and must do the thing in a folder the tool built. Shape (section 12):

```python
EXAM = [
    {
        "id": "1.9-x1",                     # lesson id + "-" + word, unique in REVIEW and EXAM
        "gate": "gate-b",                   # the gate of this lesson (plan section 4)
        "title": "把不该进仓库的文件挡在外面",  # short name: results table and practice list
        "minutes": 6,                       # 1-15; the sum is shown as 预计 … 分钟
        "build": build_x1,                  # build(sc); sc.form is "A" or "B"
        "task": {"A": "…", "B": "…"},       # two parallel forms
        "grade": grade_x1,                  # grade(ctx); ctx.scenario() is the built task
    },
]
```

Rules:

1. **Two parallel forms: same skill, different surface.** Form B is what a learner gets after failing form A (and the other way round), so it must not be answerable by remembering A's answer. Change the file names, the content, the kind of file, the wording; keep the skill and the difficulty.
2. **Names come from the seed.** Every attempt gets a fresh seed, so two attempts never share folder names or expected values. Record everything the text or the grader needs with `sc.fact`.
3. **The text is complete and has no hints.** It says where (`{dir}` plus a fact), what the result must be and how the learner can tell they are done. It never says which command to use when choosing the command is the skill being examined.
4. **Placeholders:** `{dir}` is the task folder as the learner reads it (`~/Developer/playground/exam-gate-b/1.9-x1`); every other `{name}` must be a fact recorded by the builder for *both* forms (`validate --build` checks it).
5. **The grader is a check** (sections 5-8): `ctx.ok` / `ctx.fail` / `ctx.expect`, never print, never write, never reveal the answer in a fail. Read the built task with `ctx.scenario()` (no key). Use `info.form` and `info.facts`. Avoid `ctx.ask` in exam graders unless the answer can only come from doing the task; `--grade` passes `--answer` values through like `check` does.
6. **A grader that cannot look must raise**, not fail: the learner then sees 检查器出问题 for that task, it is not recorded as a fail, and the tutor can regrade it after fixing the lesson.
7. **One task, one folder.** The builder writes only inside its own task folder; tasks of one exam never depend on each other or on the learner's real files.
8. **Where the learner stands.** The tool prints 「这道题的文件夹：<folder>」 and 「先进入这道题的文件夹：cd <folder>。题目里说的文件夹如果在它里面，再 cd 进那一层。」; it leaves its own `cd` line out when the task text or a todo line contains `cd ` or says 「进入 <a folder inside the task folder>」, so the screen never shows two places. When the learner must work one folder deeper (in particular for `git init`), write the `cd` into the text: 「先 cd 进 {dir}/{folder}，把它变成仓库…」. Never hard-code `cd ~/Developer/fullstack-from-zero` in a todo line: the tool prints the way back itself.

#### 15.4.1 A complete example (gate-b, lesson 1.9)

```python
SECRET_FILES = {"A": [".env", "secrets.env", "api-key.txt"], "B": ["config.local.json", "token.txt"]}


def build_x1(sc):
    """A small repository with one file that must not be committed."""
    repo = "shop-" + sc.word()
    secret = sc.pick(SECRET_FILES[sc.form])
    sc.git_init(repo)
    sc.write(repo + "/index.html", "<h1>小店</h1>")
    sc.git_commit(repo, "feat: 小店首页")
    sc.write(repo + "/" + secret, "KEY=" + str(sc.randint(100000, 999999)))
    if sc.form == "B":
        sc.write(repo + "/menu.txt", "今日菜单")      # B: one more file that *should* be committed
    sc.fact("repo", repo)
    sc.fact("secret", secret)
    sc.fact("commits", 1)


def grade_x1(ctx):
    info = ctx.scenario()
    repo = ctx.need_repo(info.path / info.facts["repo"], "考试仓库")
    secret = info.facts["secret"]
    ctx.expect(not repo.is_tracked(secret), "那个文件没有进入仓库",
               "不该进仓库的文件被提交了", where="仓库里被跟踪的文件", saw=secret + " 在里面")
    ctx.expect(repo.is_ignored(secret), "那个文件被忽略规则挡住了",
               "这个文件还没有被任何忽略规则挡住", where="git status --ignored", saw=secret)
    ctx.expect(repo.is_tracked(".gitignore"), ".gitignore 已经提交",
               ".gitignore 还没有进入提交", where="最新的提交", saw="里面没有 .gitignore")
    if info.form == "B":
        ctx.expect(repo.is_tracked("menu.txt"), "menu.txt 已经提交",
                   "该提交的文件还没有提交", where="最新的提交", saw="里面没有 menu.txt")
    ctx.expect(repo.is_clean(), "没有落下的改动", "还有改动没有处理",
               where="git status", saw="不是干净的")


EXAM = [{
    "id": "1.9-x1",
    "gate": "gate-b",
    "title": "把不该进仓库的文件挡在外面",
    "minutes": 6,
    "build": build_x1,
    "task": {
        "A": "仓库 {dir}/{repo} 里多了一个文件 {secret}，它不能进仓库。让 Git 以后都忽略它，并把这条规则提交。",
        "B": "进入 {dir}/{repo}：把 menu.txt 提交进去，但 {secret} 永远不能进仓库；做完以后 git status 要是干净的。",
    },
    "grade": grade_x1,
}]
```

The worked example in [`example-lesson/lesson.py`](example-lesson/lesson.py) has a second, smaller task (`99.1-x1`).

### 15.5 How `exam` uses your tasks

```bash
python3 tools/course.py exam                         # every gate and where it stands
python3 tools/course.py exam gate-b                  # start a sitting (or show the open one again)
python3 tools/course.py exam gate-b --grade          # grade the open sitting
python3 tools/course.py exam gate-b --new            # give up the open sitting, start a new one
python3 tools/course.py exam gate-b --all            # a full sitting; after the practical part: extra practice
python3 tools/course.py exam gate-b --explain pass   # record the explain-back verdict (or: again)
```

**The rule of a gate** (COMMON.md section 1; the pure functions are in `courselib.progress`):

- **Which lessons.** A gate covers the lessons whose usable `EXAM` tasks name it. No gate borrows tasks of another gate: gate-0 covers 0.1-0.4, gate-a 1.1-1.5, gate-b 1.6-1.10, gate-1 **1.11-1.16** (its tasks also use the skills of the earlier lessons).
- **One sitting (场)** holds one task for each lesson the gate covers, in lesson order, at most 6 (`progress.GATE_MAX_TASKS`); when a lesson has two tasks, one is drawn at random. Today: gate-0 4 tasks, gate-a 5, gate-b 5, gate-1 6. **No gate may have more than six lessons**: `gate_full_plan` (`--all`) takes the lessons not passed first, but once all are passed it takes the first six every time, so a seventh lesson would never come up in extra practice.
- **A lesson is passed** once one of its tasks has been passed (a later fail never takes it back). **The practical part is passed** when every lesson of the gate is.
- **After an unsuccessful sitting (补考)** the next sitting holds only the lessons not passed yet; for each, the task tried there last comes back **in its other form** (A, then B, then A). A lesson none of whose tasks was tried yet (its builder failed) gets a random task.
- **The gate is passed** when the practical part is passed **and** the explain-back verdict is recorded as pass (below).
- **Tasks never drawn** are extra practice, never a condition. `--all` starts a full sitting at any time: one task for every lesson, also the lessons already passed, preferring tasks never drawn. After the practical part is passed this is 加练: its fails never take a passed lesson back.
- **Time.** The head of a sitting gives the sum of the `minutes` of exactly the tasks of that sitting (a missing `minutes` counts 5), plus a line for the explain-back (about 10 minutes, `status.EXPLAIN_MINUTES`) while no pass is recorded. Before a sitting is drawn (listing, `check`, `status`) the estimate takes per lesson the task that comes back, or the mean of its tasks, summed and rounded up. Measured on today's pools (2026-11-20, third pass; smallest and largest sum of one task per lesson, and the estimate): gate-0 19-23 minutes of tasks (estimate 21), gate-a 27-33 (30), gate-b 25-33 (29), gate-1 45-55 (50), each plus about 10 for the explain-back: 29-33, 37-43, 35-43 and 55-65 minutes in all. The 「预计 N 分钟」 printed before a sitting is the sum of the tasks only. **The two numbers may differ by a few minutes** (on today's pools by up to 2 for gate-0, 3 for gate-a, 4 for gate-b and 5 for gate-1): `check`, `status` and the listing print the estimate before a sitting is drawn (the expected value over the forms, for example 「预计 29 分钟」 for gate-b), and `exam` prints the sum for the tasks it actually drew (gate-b sittings drawn on 2026-11-20 printed 「预计 30 分钟」 and 「预计 27 分钟」). A lesson never promises that they are equal; it may give the range.
- **What a lesson may promise about its gate:** one task per lesson (the number above); the time the tool prints when the exam starts (「开考时工具会打印题数和预计用时」), or the ranges above; passed when every lesson has a passed task and the explain-back is recorded as passed; a failed task comes back in its other form, only the lessons not passed come back; a gate never blocks the next lesson. Never promise that every task of a pool must be passed, or a number of tasks the tool does not give.

**What the learner sees.**

The listing:

```text
关卡（4 个）：
  gate-0  起步小关卡（0.1 到 0.4 课）：还没考过；一场 4 题，预计 21 分钟
  gate-a  小关卡「终端与文档关卡」（1.1 到 1.5 课）：实操题通过了 3/5 课；下一场 2 题，预计 14 分钟
  gate-b  小关卡「本地 Git 关卡」（1.6 到 1.10 课）：实操题都通过了，还差讲解题
  gate-1  阶段 1 验收（1.11 到 1.16 课）：第 1 场还没批改完（6 题）

开始一个关卡的考试：python3 tools/course.py exam <关卡>，例如 python3 tools/course.py exam gate-0
```

The state words: 「考题还没写好」, 「还没考过；一场 {n} 题，预计 {m} 分钟」, 「实操题通过了 {covered}/{total} 课；下一场 {n} 题，预计 {m} 分钟」, 「第 {n} 场还没批改完（{k} 题）」, 「实操题都通过了，还差讲解题」, 「通过了（讲解题 {date}）」 (the same words appear in `PROGRESS.md`). An extra practice sitting (`--all` after the practical part) that is still open does not hide where the gate stands; it is added at the end: 「实操题都通过了，还差讲解题；第 4 场加练还没批改完（4 题）」, 「通过了（讲解题 {date}）；第 4 场加练还没批改完（4 题）」.

The head of a sitting (gate-a, first sitting):

```text
关卡考试 · 小关卡 gate-a「终端与文档关卡」 · 第 1 场
一共 5 题，每课一题，预计 30 分钟（每题的预计分钟数加起来）。
实操题都通过以后还有讲解题，约 10 分钟：导师问你几个问题，请你讲出“为什么这样做”。

考试规则：
  - 这是不带提示的实操：考试期间没有提示，先别问导师或 AI。
  - 每道题都在练习场里自己的文件夹里做，改坏了也没关系，不会影响你自己的文件。
  - 做不出来的题空着就行。批改以后会告诉你该练什么，准备好再补考。

第 1 题 · 从长文件里读出信息（约 5 分钟）
  ……（the task text, then the builder's sc.todo lines）
  这道题的文件夹：~/Developer/playground/exam-gate-a/1.1-x2
  先进入这道题的文件夹：cd ~/Developer/playground/exam-gate-a/1.1-x2。题目里说的文件夹如果在它里面，再 cd 进那一层。
……
做完以后（或者做不下去了），回到学习工作区批改：
  cd ~/Developer/fullstack-from-zero
  python3 tools/course.py exam gate-a --grade
```

Heads of gate-0 and gate-1: 「关卡考试 · gate-0「起步小关卡」 · 第 1 场」, 「关卡考试 · gate-1「阶段 1 验收」 · 第 1 场」. The line on the explain-back under the count: 「实操题都通过以后还有讲解题，约 10 分钟：导师问你几个问题，请你讲出“为什么这样做”。」 while the practical part is open; in a sitting after it (加练) 「讲解题还差一次，约 10 分钟：对导师说“请问我 gate-b 的讲解题”。」 while the explain-back is not recorded as pass; no line once it is. Other sittings: 「第 {n} 场 · 补考：只考还没通过的课，每课一题，没通过的题换成另一套题面」, 「第 {n} 场 · 完整的一场：每课一题，已经通过的课也再考一次」 (`--all` before the practical part is passed), 「第 {n} 场 · 加练：实操题你已经通过了，这一场的结果不会让通过的课退回去」. A gate some of whose lessons have no task yet: 「这个关卡的考题还没写全：{lessons} 课还没有考题，这一场先考已经写好的 {n} 题。」; with no task at all: 「{gate name}「{title}」的考题还没有写好：…」 and 「这不是你的问题，也不影响你继续往下学。…」 (exit 0).

- **Forms alternate per task across sittings:** A the first time, then B, then A. Each task is built with a fresh seed in `<playground>/exam-<gate>/<task id>`, with the same safety rules as `scenario`.
- **No hints.** The command never mentions `hint`.
- **An open sitting is never rebuilt** by running `exam <gate>` again: the same tasks are shown again (「这一场考试还有题没批改，上面是同一批题目，你已经做的改动都还在。想放弃这一场重新出题：python3 tools/course.py exam gate-b --new」).
- **Grading** runs each grader through the guarded runner with `ctx.final = True` (section 6.6), prints the three outcomes per task and records per task. A task graded 通过 or 还没达标 is final for that sitting; a task whose grader broke stays open and only it is graded on the next `--grade` (「…修好以后再运行 python3 tools/course.py exam gate-b --grade，只会重批这几题。」). A builder that raises drops only its own task from the sitting (检查器出问题 for that one, exit 2).
- **After grading:** 「这一场的结果：通过 2/5 题」, 「这一场的题全部通过了。」 when nothing failed; after a fail the practice list 「接下来练什么：」 / 「  - 1.1 课「终端：新建与查看」：从长文件里读出信息」 and 「练好以后补考：python3 tools/course.py exam gate-a。补考只考还没通过的 3 课，每课一题，没通过的题换另一套题面。」; when lessons are left that this sitting did not hold: 「还有 {n} 课这一场没考到：{lessons}。接着考：python3 tools/course.py exam {gate}」; in a 加练 sitting (kind `practice`) with a fail: 「这是加练：通过的课不会退回去。」 (never in another sitting). Grading a closed sitting again: 「gate-a 第 1 场考试已经批改过了：通过 2/5 题。」 then 「还没通过的课可以补考（每课一题，没通过的题换另一套题面）：python3 tools/course.py exam gate-a」.
- **When the practical part is passed**, `--grade` and `exam <gate>` (which then starts no sitting, exit 0) print 「实操题都通过了。还差讲解题：对导师说“请问我 gate-b 的讲解题”。导师判断以后，用这条命令记下结果：python3 tools/course.py exam gate-b --explain pass（要再来一次就写 again）」, and `exam <gate>` adds 「没抽到的题算加练，不做也不影响通过。想加练一场（每课一题，优先出你还没做过的题，结果不会让通过的课退回去）：python3 tools/course.py exam gate-b --all」. Once the gate is passed the first line is 「小关卡 gate-b 通过了：实操题每课都有一题通过，讲解题也记为通过（2026-11-25）。」 (「阶段验收 gate-1 通过了：…」). Gone: 「…的考题全部通过了」, 「…的 N 道考题你都已经通过了」, 「这个关卡的考题还没写全：现在只有 N 题（正式考试是 4 到 6 题）」.

#### 15.5.1 The explain-back verdict

The explain-back questions (讲解题) belong to every gate: the questions of `gates/<gate>/rubric.md` (two explain-back questions; at gate-0, gate-a and gate-b also one debugging question; about 10 minutes with the verdict), asked by the tutor after the practical part is graded (for gate-1 the learner may use an independent examiner with `gates/gate-1/examiner-prompt.md`). The learner records the verdict:

```bash
python3 tools/course.py exam gate-0 --explain pass     # the tutor or examiner said: passed
python3 tools/course.py exam gate-0 --explain again    # it has to be repeated
```

- Help: 「记下讲解题的结果：导师判断通过写 pass，要再来一次写 again」. The value is folded like a gate id (`PASS`, `ｐａｓｓ`, `pass` with a full-width space after it all mean `pass`). Another value is a usage error (exit 64), two lines: 「用法不对：选项 --explain 不能是 fail（可以用的值：pass、again）」 and 「看这个命令的说明：python3 tools/course.py exam -h」; `--explain` with `--grade`, `--new` or `--all` is a usage error too.
- Stored as `"explain": {"gate-0": {"result": "pass", "date": "2026-11-25"}}` in `learner/state.json` (today's date). The latest verdict counts, so `again` after `pass` takes the pass back, and says so: 「之前记的是“通过”（2026-11-25），现在改成了“再来一次”：小关卡 gate-0 现在还没通过。」 before the again line. The log gets an `exam-explain` event.
- Refused (exit 1, nothing stored) while no task of the gate has a recorded pass or fail: 「gate-0 还没有批改过一场考试，现在还不能记讲解题的结果。先考实操题：python3 tools/course.py exam gate-0，做完批改：python3 tools/course.py exam gate-0 --grade」. Accepted after any graded sitting, also while the practical part is still open.
- Printed: pass 「讲解题的结果记下了：通过（2026-11-25）。」, then 「小关卡 gate-0 通过了：实操题每课都有一题通过，讲解题也记为通过（2026-11-25）。」 or, while lessons are open, 「实操题还有 {n} 课没通过：{lessons}。补考：python3 tools/course.py exam gate-0」 and 「讲解题的“通过”先记着：等实操题每课都有一题通过，小关卡 gate-0 就通过了。」 (whether a pass may be recorded before the practical part is passed is an open decision of the orchestrator); again 「讲解题记为“再来一次”：准备好了再对导师说“请问我 gate-0 的讲解题”。」.

State (tool-owned, in `learner/state.json`):

```json
"exams": {"gate-b": {"1.9-x1": {"form": "A", "result": "fail", "date": "2026-11-19",
                                 "seed": 41237, "attempt": 1, "title": "把不该进仓库的文件挡在外面",
                                 "lesson": "1.9", "history": [{"attempt": 1, "form": "A",
                                 "result": "fail", "date": "2026-11-19"}]}}},
"exam_attempts": {"gate-b": {"attempt": 1, "kind": "full", "started": "2026-11-19T10:00:00",
                             "forms": {"1.9-x1": "A"},
                             "tasks": [{"id": "1.9-x1", "lesson": "1.9", "title": "…", "minutes": 6,
                                        "form": "A", "seed": 41237, "folder": "exam-gate-b/1.9-x1",
                                        "result": "fail", "graded": "2026-11-19T10:40:00"}]}},
"explain": {"gate-b": {"result": "again", "date": "2026-11-19"}}
```

`kind` is `full`, `retest`, `again` (`--all` before the practical part is passed) or `practice` (`--all` after). `exams` holds only results the learner earned (`pass` / `fail`); a grading problem stays in `exam_attempts` only. `learner/last-result.json` of an exam gets every task's full result plus `practical_done`, `explain` and `gate_done`; the log gets `exam-started` and one `exam-task` event per graded task.

Exit codes: `exam <gate>` 0 (also for "no tasks yet" and "practical part passed"), 1 when a folder in the way was refused, 2 when a task could not be built; `--grade` 0 all passed, 1 at least one 还没达标 (or nothing to grade), 2 at least one 检查器出问题; `--explain` 0, 1 when refused; 64 for an unknown gate.

For command writers (`courselib.progress`; a *pool* is a list of `(lesson_id, task_id)` in learning order, or plain task ids): `gate_lessons(pool)`, `gate_open_lessons(pool, results)`, `gate_practical_done(pool, results)`, `gate_open_ids(pool, secondary=(), results)` (tasks tried without a pass in lessons not passed; meaning changed today: untried tasks are not listed), `gate_sitting_plan(pool, results)`, `gate_full_plan(pool, results, drawn=())`, `gate_done(pool, secondary=(), results, explain=None)` (never True without an explain pass), `gate_minutes(entries, cap=6)`, `gate_summary(...)`, **`gate_status(catalog, state, gate)`** (the one call for commands; a dict whose keys read as attributes: `gate`, `tasks`, `attempts`, `passed`, `open`, `lessons`, `open_lessons`, `practical_done`, `explain`, `explain_date`, `done`, `in_progress`, `next_count`, `next_minutes`, `sitting_kind` (the `kind` of the open sitting or None)), `explain_record`, `explain_of`, `record_explain`, `task_minutes`, `GATE_MAX_TASKS`, `EXPLAIN_PASS`, `EXPLAIN_AGAIN`. `Catalog.gate_pool(gate)` returns `(primary, [], unusable)`; `Catalog.gate_lesson_ids(gate)`; `catalog.usable_exam_task(task)`. Gate names: `syllabus.gate_kind`, `gate_name`, `gate_label`, `gate_titled` (also `exam.gate_name`). Where a gate stands in words: `status.gate_state_words(summary)`. Removed from `commands/exam.py`: `gate_pool`, `choose`, `final_grader`, `_usable`, `_open_ids`, `_gate_done`, `MIN_TASKS`.

### 15.6 Testing scenarios and exam tasks

Work in a simulation home (plan G8), never in the real one, with the playground in your scratch folder:

```bash
export COURSE_NOW=2026-11-19T10:00:00
export COURSE_PLAYGROUND="$TMPDIR/pg-$RANDOM"
python3 tools/course.py validate --build 1.9          # every scenario and both forms of every task, fixed seed
python3 tools/course.py scenario 1.9 --seed 7         # a fixed seed (hidden option, for testers)
python3 tools/course.py exam gate-b --seed 7          # fixed task choice and seeds
cat learner/state.json                                # exam_attempts: seeds, forms, folders
# do the tasks as the learner would, then:
python3 tools/course.py exam gate-b --grade           # expect 通过 for correct work
```

For every task, grade at least: correct work on form A, correct work on form B, the untouched folder (must be 还没达标, never a pass and never 检查器出问题), and two plausible wrong attempts. Remember that a learner's machine may sign commits until lesson 1.6 (plan G7): test exam tasks of gate-a and gate-0 in a simulation home where `commit.gpgsign=true` and no `gpg` exist, and make sure nothing in the task needs the learner to commit before 1.6.

## 16. Writing REVIEW items

How the `review` command schedules and grades the items of a lesson's `REVIEW` list (shape: section 11), and how to write items of each type so that they work for a beginner. Plan references: I3 (`REVIEW`), I4 (`review`), G2 (voice).

### 16.1 What the learner experiences

```text
复习 · 2026-11-25

  今天到期：5 道复习题、1 站要重做。这次做 6 道，大约 7 分钟。
  每道题都可以输入 s 跳过、q 结束；做完一道记一道，中途停下不会丢。

第 1/6 题 · 重做 · 1.6b 第一次提交
  你之前看过这一站的完整答案，它记为「带扶手完成」。现在不看提示，把课文 … 里第 2 站的「自己做」重新做一遍。
  做完运行：python3 tools/course.py check 1.6b（通过后这一站改记为「通过」）

第 2/6 题 · 回忆 · 1.6 Git：第一次提交
  git add 和 git commit 各做什么？
  先在心里（或纸上）答一遍。想好了按回车看参考答案（s 跳过，q 结束）：
  参考答案：
    git add 放进暂存区；git commit 把暂存区拍成快照。
  你答得怎么样？1 记得，2 模糊，3 忘了（s 跳过，q 结束）：1
  下次复习：2026-12-02（隔 7 天）。

第 3/6 题 · 预测 · 1.6 Git：第一次提交
  改了 a.txt 但还没 git add，git status 会把它列在哪里？
    A. Changes to be committed
    B. Changes not staged for commit
    C. Untracked files
  输入选项的字母（s 跳过，q 结束）：A
  ❌ 不对。正确答案是 B：Changes not staged for commit
  解释：改了但没放进暂存区，就是“没暂存的改动”。
  没关系，复习就是为了找出忘了的地方。明天（2026-11-26）再来一次。
  …
```

Your `q`, `a`, `options` and `explain` appear exactly as written, indented. Everything else is the tool's.

### 16.2 Scheduling rules

| Rule | Detail |
|---|---|
| Only `tier: "fluent"` is scheduled | `lookup` (know where to look it up) and `aware` (know it exists) items are never served. Keep them: the tutor and later stages read them. |
| When an item enters | When the learner **first passes the station it belongs to**: its `station` key, or the lesson's last station when there is none. The lesson is the part of the id before the first `-` (`1.6-r3` belongs to 1.6). It is first due two days later. |
| Late additions | An item you add after the learner already passed its station is enrolled at the learner's next `review` (the session says 「补排了 N 道复习题」) and is due two days after that. |
| Boxes | Five boxes with intervals of 2 days, 1 week, 3 weeks, 2 months, 6 months. |
| 记得 / correct choice / `do` passed first time | one box up; due after the new box's interval |
| 模糊 / `do` passed after a 还没达标 | same box; due after that box's interval again |
| 忘了 / wrong choice / `do` given up | back to box 1; **due the next day** |
| Retirement | right in box 5 (after about 9 months of correct answers): the item **retires** and never comes back, not even if the station is checked again |
| A session | due cold redos first (at most 2), then due items: *which* items is decided oldest due first, *in which order* mixes the types (two items of one type in a row only when nothing else is left); at most **8** things and about **10 minutes**; a `do` item always comes last and only one is handed out at a time |
| Return routine | if the learner's previous study day is more than 10 days back, the session says so in its first line, serves at most **4 easy items** (lowest boxes among the items last answered right, then items never answered) and no redo or `do` task, and only counts the rest: 「还有 N 条，不急，下次再说。」 |
| Skipping | `s` at any question leaves the item due; `q` ends the session. Every answer is saved at once, so Ctrl+C loses nothing. |

Consequences for you: a learner sees each fluent item about six times over nine months, mixed with items from other lessons, usually weeks after the lesson. **Write every item so that it makes sense on its own, months later, without the lesson text open.** Do not refer to "the example above", "this station" or a file name the learner only met inside the lesson's practice folder.

### 16.3 Keys common to every item

| Key | Required | Meaning |
|---|---|---|
| `id` | yes | `<lesson id>-<lower-case word(s)>`, unique in the course: `1.6-r1`, `1.6-stage-vs-commit`. **Never rename an id after the lesson is published**: the learner's history is stored under it (section 16.7). |
| `type` | yes | `recall`, `which`, `predict`, `fault` or `do` |
| `tier` | yes | `fluent` (scheduled), `lookup`, `aware` |
| `q` | yes | the question, plain Chinese (plan G2); line breaks are kept |
| `station` | no | the station it belongs to; default the last station of the lesson. Set it whenever the item is about an earlier station, so it starts at the right time. |
| `rule` | no | a rule id of this lesson (`GIT-03`) the item practises; `validate` warns if the lesson does not introduce it |
| `explain` | no | one or two sentences shown after the answer (for choice items: after right **and** wrong answers) |

`validate` checks all of this; run it after every change (section 16.8).

How many: two to four `fluent` items per lesson is plenty. Each one costs the learner about six future minutes. Put the rest in `lookup`.

### 16.4 recall

The learner answers in their head, presses Enter, sees `a`, and grades themselves: 1 记得, 2 模糊, 3 忘了. Nothing is compared automatically.

```python
{"id": "1.8-r1", "type": "recall", "tier": "fluent", "station": "1.8b",
 "q": "改坏了一个文件，还没 git add。想让它回到上一次提交时的样子，用哪条命令？这样做有什么风险？",
 "a": "git restore <文件名>。风险：工作区里没提交的改动会直接丢掉，找不回来。",
 "explain": "执行之前先 git status 看一眼，是 GIT-04 的要求。",
 "rule": "GIT-04"},
```

Required: `a` (non-empty). Not allowed: `options`, `answer`.

What makes a good recall item for a beginner:

- **One answer that the learner can check against `a` in five seconds.** "说出两件事" is fine; "谈谈你对 Git 的理解" is not, because nobody can grade it honestly.
- Ask for **why** or **when**, not only **what**: "提交之前，改动要先放到哪里？为什么要有这一步？" Self-grading works best when the learner can tell 记得 from 模糊.
- `a` is the model answer in at most three short sentences, written so that reading it *is* the lesson again. Put the command in it literally (`git restore <文件名>`), with placeholders in angle brackets.
- Avoid questions whose answer is a long exact spelling (a flag list, a URL): use `which` for those, or tier `lookup`.

### 16.5 which, predict, fault

Choice items are graded automatically: the learner types a letter (`b`, `Ｂ`, `B.`, `选 B` and the text of an option, dots folded as for `ctx.quiz`, are all accepted). After the answer the tool says 答对了 or names the right option, then shows `explain`.

| Type | Ask | Typical options |
|---|---|---|
| `which` | which command / file / setting / label does this job? | commands, file names, the seven 规则类型 |
| `predict` | what will this command print / what will change? | exact output lines, "nothing", an error |
| `fault` | what is wrong here? (a command, a commit message, a `.gitignore` line) | the faults, one of them real |

```python
{"id": "1.7-p1", "type": "predict", "tier": "fluent", "station": "1.7a",
 "q": "你改了 index.html 并且已经 git add。现在运行 git diff（不带 --staged），会看到什么？",
 "options": ["index.html 的改动", "什么也不显示", "报错：没有改动"],
 "answer": "B",
 "explain": "git diff 只比较工作区和暂存区；改动已经进了暂存区，要用 git diff --staged 看。"},

{"id": "1.10-f1", "type": "fault", "tier": "fluent", "station": "1.10b",
 "q": "这条提交信息哪里不符合约定式提交？\n\n    Fix: 修好了首页的链接",
 "options": ["类型要小写：fix", "冒号后面不能有空格", "说明不能写中文"],
 "answer": "A", "shuffle": True,
 "explain": "类型是小写的 fix；冒号后面正好一个空格；说明可以用中文。", "rule": "COMMIT-01"},
```

Required: `options` (2 to 6 non-empty strings), `answer` (the letter of the right one). Not allowed: `a` (put the reasoning in `explain`). Optional: `shuffle: True` lets the tool show the options in another order (fixed per item and day, graded by content); leave it out when the order carries meaning ("都不对" last, or options in a natural sequence).

What makes a good choice item for a beginner:

- **Wrong options are real mistakes**, the ones beginners actually make (the misconception lists in the research briefs and `learner/misconceptions.md` are the source). A silly option teaches nothing.
- Three options is usually right. Four at most for stage 0-1. Options about the same length, so the longest is not automatically right.
- `explain` says why the right answer is right **and** why the most tempting wrong one is wrong, in one or two sentences. It is shown to everyone, so do not write "答对了" in it.
- `predict` items quote **real output**, verbatim, as executed in the simulation home (plan G4, G8). If the learner's English UI or a tool version could change the text, prefer a description ("没有任何输出") over a quoted line, or tier `lookup`.
- `fault` items show the faulty thing in a code-like block inside `q` (four spaces of indentation after a blank line), and exactly one option names the real fault.
- No trick questions, no double negatives ("下面哪个不是不对的").

### 16.6 do

A `do` item is a small hands-on task. The tool builds a **fresh copy** of one of the lesson's scenarios for it, tells the learner what to do, and grades it later with your check function.

```python
def _readme_committed(ctx):
    """Shared by the station check and the do item."""
    sc = ctx.scenario("start")            # the review copy when called from review
    repo = ctx.need_repo(sc.path / sc.facts["repo"], "练习仓库")
    ctx.expect(repo.file_at("HEAD", "README.md") is not None,
               "README.md 已经提交", "README.md 还没有进入提交",
               where="练习仓库的最新提交", saw="里面没有 README.md")

REVIEW = [
    {"id": "1.6-d1", "type": "do", "tier": "fluent", "station": "1.6b",
     "q": "练习仓库里有一个还没提交的 README.md。把它提交，提交说明用约定式提交的格式。",
     "scenario": "start", "check": _readme_committed},
]
```

Required: `scenario` (a key of your `SCENARIOS`), `check` (a function taking one argument). Not allowed: `a`, `options`, `answer`.

What happens:

1. In the session the learner reaches the item (always last, at most one per session) and presses Enter. The tool builds `SCENARIOS[scenario]` into `~/Developer/playground/review/<item id>` (replacing an earlier copy of the same item, which carries the tool's marker), and prints `q`, the folder, every `sc.todo(...)` line of the builder, and how to hand it in.
2. The learner leaves the session, does the task in a terminal, and runs `python3 tools/course.py review --grade`.
3. Your `check(ctx)` runs under the guarded runner with the review copy bound: `ctx.scenario()` and `ctx.scenario("<the same key>")` return it. The three outcomes are as for a station check:
   - **通过** on the first `--grade`: one box up; **通过** after one or more 还没达标: 模糊 (same box);
   - **还没达标**: nothing is recorded yet; the learner fixes it and runs `--grade` again, or gives up with `review --give-up` (counts as 忘了, back tomorrow on a new copy);
   - **检查器出问题**: not counted; the item waits.
4. If the folder was deleted meanwhile, the hand-in is cancelled without a grade and the item is served again next time.

If the scenario cannot be built (the builder raises, the playground is unsafe, the builder library is not available), the learner is told politely and the item is skipped without a grade.

What makes a good `do` item for a beginner:

- **Three to five minutes, one skill**, already practised in the station. It is retrieval of a skill, not a new exercise: same kind of task, different surface (another file name, another repository name; use `sc.word()` and `sc.pick()` so the copy differs from the station).
- `q` states the goal and the end state, not the commands ("把它提交，提交说明用约定式提交的格式", not "运行 git add 再运行 git commit"). Put where things are in `sc.todo(...)` lines of the builder ("练习仓库在这里：…").
- The check looks **only inside `ctx.scenario().path`**. Never at `~/Developer/my-site` or the workspace: a review must not depend on, or touch, the learner's real folders.
- Share the check with the station check (as above): one helper, one truth. Use `ctx.scenario("start")` with the same key the item names, so the same code finds the station folder in a station check and the review copy in a review.
- Fails say where the tool looked and what is missing, never the command (section 1, rule 7). A `do` item has no hints; `explain` is not shown for it, so do not rely on it.
- If the check asks a question (`ctx.ask` / `ctx.quiz`), the learner answers it during `--grade` (in tests: `review --grade --answer …`). Compute the expected answer from `ctx.scenario().facts`, never hard-code it.
- Make the item `fluent` only if the learner really should be able to do it from memory months later. Many `do` items are better as `lookup`.

### 16.7 Changing items later

The learner's history is stored in `learner/state.json` under the item **id**. What happens when you change a published lesson:

| Change | Effect |
|---|---|
| reword `q`, `a`, `options`, `explain` | fine; takes effect at the next serving. Keep `answer` pointing at the same meaning. |
| add an item | enrolled at the next `review` if its station already passed |
| change `tier` away from `fluent` | the item stops being served; its record is kept (it comes back if you make it `fluent` again) |
| rename an `id` | the old record is orphaned (the session reports it to the tutor) and the new id starts again in box 1. Do not rename; add a new item and set the old one's tier to `lookup` if you must. |
| delete an item, or the whole lesson module | the record is kept and reported as 「找不到对应的课程或题目」; nothing is served, nothing is counted as due |
| the lesson module fails to load | its items are skipped and reported; they come back when the module is fixed |

### 16.8 Testing your items

`validate` checks the shape (types, tiers, options and letters, `scenario` keys, `check` signatures). Then play the items in a simulation home (plan G8) with a fixed clock:

```bash
export COURSE_NOW=2026-11-19T10:00:00 COURSE_NONINTERACTIVE=1
python3 tools/course.py validate --build 1.6
python3 tools/course.py check 1.6b --answer 3            # first pass: the items are enrolled
COURSE_NOW=2026-11-21T10:00:00 python3 tools/course.py review --answer 1 --answer B
#   recall items take 1 / 2 / 3 (or 记得 / 模糊 / 忘了); choice items take a letter; s skips
COURSE_NOW=2026-11-21T10:00:00 python3 tools/course.py review --grade    # a do item, after doing it
python3 tools/course.py review --give-up
```

Each graded question consumes one `--answer`, in the order the session serves them (the session prints that order: 「第 n/total 题」). Prompts that only wait for Enter never consume one. A missing answer in non-interactive mode is a usage error (exit 64); what was answered before is kept. For a `do` item, run `--grade` once before doing the task (expect 还没达标 with a useful 还缺什么), then after doing it correctly (expect 通过), then try three plausible wrong attempts, exactly as for station checks (plan section 6.2).

### 16.9 Checklist

- [ ] 2-4 `fluent` items per lesson; the rest `lookup` or `aware`
- [ ] every item understandable months later without the lesson text
- [ ] `station` set when the item is about an earlier station
- [ ] recall: one checkable answer; `a` short and literal
- [ ] choice: real beginner mistakes as wrong options; `explain` says why; real output quoted verbatim
- [ ] do: 3-5 minutes, goal not commands, check looks only inside the review copy, shared with the station check
- [ ] plain Chinese per plan G2 in `q`, `a`, `options`, `explain`
- [ ] ids final; never renamed after publication
- [ ] `validate --build` passes; items played once with `COURSE_NOW` and `--answer`

## 17. Environment tools: `make_sim_home.py`, `doctor`, `fresh`

For builders and testers of the course (learners never run `make_sim_home.py`). Binding context: plan G7, G8, G9 and I4.

### 17.1 Simulation homes (`tools/dev/make_sim_home.py`)

Every lesson step is verified in a throw-away home directory that mimics the learner's machine (plan G8), never in the real home. This script builds one.

```bash
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-$(date +%s)-$RANDOM"
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-2" --no-copy          # home only, no workspace copy
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-3" --no-identity      # user.name / user.email left out
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-4" --no-signing       # signing settings left out
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-5" --json             # print the paths as JSON
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-6" --workspace <dir>  # copy another workspace
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-7" --with-learner-files  # also copy journal/, notes/, learner/, PROGRESS.md
python3 tools/dev/make_sim_home.py "$TMPDIR/sim-8" --stay             # the learner who stayed: workspace elsewhere, entrance link
```

What it creates under the target `<sim>`:

| Path | Content |
|---|---|
| `<sim>/home/.gitconfig` | the learner's settings of plan G7, exactly the text below (with `--no-signing` the `signingkey`, `[commit]`, `[gpg]`, `[gpg "ssh"]` and `[tag]` parts are left out; with `--no-identity` `name` and `email`) |
| `<sim>/home/.gitignore_global` | the eight patterns of G7: `.DS_Store` `._*` `.Spotlight-V100` `.Trashes` `.idea/` `*.swp` `*.swo` `*.log` |
| `<sim>/home/Developer/` | empty (the learner creates it in 0.2; delete it if your test needs the state before 0.2) |
| `<sim>/home/Developer/fullstack-from-zero/` | a copy of this workspace without `__pycache__`, `*.pyc`, `.DS_Store`, `.ruff_cache`, `.pytest_cache`, and without the learner-owned top-level `journal/`, `notes/`, `learner/` and `PROGRESS.md` (plan G11; `--with-learner-files` copies them too). What the course itself ships there is copied: `journal/README.md`, `notes/README.md`, `learner/README.md` when they exist, and the skeleton of `notes/my-rules.md` (everything before its first 「## 」 heading and every heading line, each followed by an empty line; the learner's own lines are left out), so testers see the file check's closing step opens (`make_sim_home.copy_skeletons`, `rules_notes_skeleton`). Skipped entirely with `--no-copy` |

```ini
[user]
	name = Learner
	email = learner@example.com
	signingkey = FAKEKEY0000
[commit]
	gpgsign = true
[gpg]
	format = openpgp
	program = gpg
[gpg "ssh"]
	program = 
	allowedSignersFile = 
[tag]
	forceSignAnnotated = false
[core]
	excludesfile = ~/.gitignore_global
```

(`program = ` and `allowedSignersFile = ` end with one space, exactly as `git config` writes an empty value; `~` is written literally, as plan G7 has it.)

With `--stay` the workspace copy goes to `<sim>/home/Desktop/Code/fullstack-from-zero`, `<sim>/home/Developer/fullstack-from-zero` is an entrance (a symbolic link) to it, `learner/state.json` gets `{"decisions": {"workspace_location": "stay-in-sync"}}` unless the copy has a state file, and the last export line is `cd <sim>/home/Developer/fullstack-from-zero`. `--stay` with `--no-copy` is refused (exit 2, 「拒绝：--stay 要复制学习工作区，不能和 --no-copy 一起用。」). The simulation cannot mark the Desktop as synced by iCloud, so `doctor` reports the folder as not synced there (with the entrance sentence).

It then prints the lines to paste into the simulation shell:

```bash
export SIM=/private/tmp/.../sim-1
export HOME=/private/tmp/.../sim-1/home
unset XDG_CONFIG_HOME GIT_CONFIG_GLOBAL
cd /private/tmp/.../sim-1/home/Developer/fullstack-from-zero
```

Safety rules built into the script (exit code 2 and a Chinese 「拒绝：…」 line on standard error when one is broken):

- the target must lie inside the system temporary directory (`tempfile.gettempdir()`, `$TMPDIR` or `/tmp`, all resolved through links) and must not be that directory itself;
- the target must be new or empty;
- the workspace copy must not land inside the workspace it copies;
- the files are written directly; the script never runs `git config --global`, so the real `~/.gitconfig` cannot be touched even when `HOME` was not switched.

Used from Python (the tests do this): `make_sim_home(target, workspace=None, copy=True, identity=True, signing=True, learner_files=False, stay=False) -> dict` with keys `sim`, `home`, `developer`, `workspace`, `entrance` (the link, or None); `write_home(home, identity=True, signing=True)` writes only the two dot-files into an existing home; `gitconfig_text(...)`, `export_lines(info)`, `FAKE_NAME`, `FAKE_EMAIL`, `FAKE_SIGNING_KEY`, `GLOBAL_IGNORE`. Load it with `importlib` from `tools/dev/make_sim_home.py` (see `tools/tests/envstubs.py`).

Verified on 2026-11-19 in a simulation built by this script (Git 2.54.0, no gpg on PATH): `git check-ignore -v a.log` answers from `.gitignore_global:8:*.log`; a plain `git commit` fails exactly as on a machine like that of plan G7:

```text
error: cannot run gpg: No such file or directory
error: gpg failed to sign the data:
(no gpg output)
fatal: failed to write commit object
```

**The empty `gpg.ssh.program` breaks SSH signing** (lesson 1.11): `git -c gpg.format=ssh -c user.signingkey=~/.ssh/id_ed25519.pub commit -m y` with the key file present fails with `error: cannot run : No such file or directory` / `error: ` / `fatal: failed to write commit object`; it works once `gpg.ssh.program` is removed (`git config unset --global gpg.ssh.program`) or set to `ssh-keygen`. Verifying with the empty program prints `error: cannot run : No such file or directory` twice; with the program fixed but `allowedSignersFile` empty, `Good "git" signature with ED25519 key SHA256:…` and `Unable to open allowed keys file "": No such file or directory`; with both keys removed, `error: gpg.ssh.allowedSignersFile needs to be configured and exist for ssh signature verification` / `No signature`. `git tag -a v1 -m v1` with `tag.forceSignAnnotated=false` makes an unsigned annotated tag (exit 0).

#### 17.1.1 Where the agent's shell still differs from the learner's

The simulation copies the learner's files, not the agent's whole environment. Differences seen on 2026-11-19 in the build sandbox, each of which must be handled by the tester and reported, never written into lesson text:

| Agent shell | Learner (G7) | What to do |
|---|---|---|
| `GIT_EDITOR=true` is exported | not set: Git's editor is `vi` | `unset GIT_EDITOR` when the step is about the editor; otherwise remember that `git commit` without `-m` silently aborts here instead of opening vi |
| `TERM` is empty | `TERM=xterm-256color` | with `TERM` empty Git refuses to start vi ("Terminal is dumb, but EDITOR unset"); `export TERM=xterm-256color` only where needed, and never start vi without a terminal |
| `GIT_CONFIG_PARAMETERS` carries proxy settings | not set | harmless for local work |
| Apple's `git` shim prints `couldn't create cache file '/var/folders/.../xcrun_db-…' (errno=Operation not permitted)` on standard error | no such line | sandbox noise; never paste it as expected output |
| No network unless hosts are allowed | normal network | `doctor --net` cannot be verified here |
| `grep` is a shell function from the Claude Code shell snapshot that runs ugrep (`grep --version` prints ugrep) | `/usr/bin/grep` (BSD grep 2.6.0) | run lesson commands in a child shell (`zsh -f -c '…'`; on 2026-11-20 a child `zsh -c` also found `/usr/bin/grep`), or call `/usr/bin/grep`; never paste ugrep's output as expected output |
| `PATH` is the agent's | the same programs (G7), plus anything the learner installs | the simulation keeps the real `PATH`: `python3` is still the one the build machine finds first |

Commits a tester makes in a simulation need `git -c commit.gpgsign=false commit …` (and say so in the report); the learner's own first commit only works after lesson 1.6.

### 17.2 `doctor [--net]`

`python3 tools/course.py doctor` is the read-only environment report of plan I4. It never changes a setting or a repository and never calls `app.store.load()`, so it also works when `learner/state.json` is damaged: it reads that file itself, read only, for the decision `workspace_location` and for the passed stations (lessons 0.2, 1.6, 1.11, 1.12 and the lessons after 1.11; a damaged file counts as empty). Its only write is `learner/last-result.json` (section 17.2.3). Every doctor text that means the course folder says 学习工作区; the location line always shows the real place.

#### 17.2.1 What it looks at

| Key | Looked at | 没问题 | 需要处理（谁来处理） | 仅提示 |
|---|---|---|---|---|
| `macos` | `sw_vers -productVersion` | the version | | major version below the baseline's; no `sw_vers`; unreadable output |
| `shell` | `$SHELL`, `zsh --version` | zsh and its version | | another shell; `SHELL` unset |
| `python3` | first `python3` on `PATH`, `python3 --version` | 3.9 or newer, with its path | below 3.9; not found（导师） | unreadable version |
| `git` | first `git` on `PATH`, `git --version` | the version | not found; found but failing (Command Line Tools missing); found but its configuration has a broken line (「设置文件有一行写坏了」, recognised by Git's `bad config` message, typically a damaged `~/.gitconfig`)（第 1.6 课之前要弄好，把这一行发给导师） | with git unusable, one line says the Git settings were skipped |
| `git.identity` | `user.name`, `user.email` | both 已设置 | either 未设置: 「Git 身份：user.name 未设置，user.email 未设置。没设置的那一项，Git 会拿这台 Mac 的账户名和电脑名自己拼一个：提交照样能成功，只是会多打印一段英文提示，拼出来的名字和地址也会记进每一个提交里。 → 第 1.6 课会带你正式设好」 | |
| `git.signing` | `commit.gpgsign`, `gpg.format`, `gpg.program` / `gpg.<format>.program` (also when set to an **empty** value), `user.signingkey`, `gpg.ssh.defaultKeyCommand` | signing off; or on with the program found (openpgp, x509) or program and key found (ssh): 「提交签名：已经打开（格式 ssh），签名程序和钥匙都找到了。」 | every line names the setting: 「提交签名：已经打开（commit.gpgsign=true，格式 openpgp），但找不到签名程序 gpg。现在每次 git commit 都会失败。」 and 「…格式 openpgp），但设置 gpg.program 是空的：Git 会去运行一个没有名字的程序。现在每次 git commit 都会失败。」（第 1.6 课）; with ssh: 「…（commit.gpgsign=true，格式 ssh），但设置 gpg.ssh.program 是空的：…」, 「…但找不到签名程序 ssh-keygen。…」, 「…但没有设置用哪把钥匙（user.signingkey）。…」, 「…但设置里写的钥匙文件 ~/.ssh/id_ed25519.pub 不存在。…」（第 1.11 课） | unreadable `commit.gpgsign`; unknown format |
| `git.editor` | `git var GIT_EDITOR` (asked again with `TERM=xterm-256color` when the terminal is dumb) | any editor other than vi / vim | | vi or vim（第 1.6 课会把它换掉）; a program that edits nothing (`true`, `:`, `false`, `cat`; usually `GIT_EDITOR=true` in an agent shell); no answer |
| `git.branch` | `git var GIT_DEFAULT_BRANCH` (older Git: `init.defaultBranch`, else `master`) | `main` | | anything else（第 1.6 课会讲到） |
| `git.excludes` | `core.excludesfile` (`--type=path`), else `$XDG_CONFIG_HOME/git/ignore` or `~/.config/git/ignore` | the file exists | | not configured and no default file; configured but missing（第 1.9 课） |
| `workspace` | the resolved workspace root and every ancestor: under `~/Library/Mobile Documents`, or carrying the extended attribute `com.apple.file-provider-domain-id` (read with `/usr/bin/xattr <folder>`, 5 s timeout each; the value is read with `xattr -p` only to tell iCloud from another provider); what is at `~/Developer/fullstack-from-zero` (`App.entrance_kind()`); `decisions.workspace_location` | not in a synced folder: 「学习工作区的位置：<real path>，不在同步到云端的文件夹里。」 (+ 「~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero 照样能用。」 when the entrance is a link) | inside iCloud Drive or a synced folder such as `~/Desktop` (the table below) | `/usr/bin/xattr` missing, failing or timing out: 「无法判断」 |
| `workspace.git` | `<workspace>/.git` (folder or file) and whether the learner has reached lesson 1.12: station 1.12a passed, or every station of lesson 1.11 passed, or any station of a lesson after 1.11 passed (`Doctor.reached_workspace_repo_lesson()`, `doctor.WORKSPACE_REPO_BEFORE = "1.11"`; when the stations of 1.11 cannot be told, only 1.12a counts) | (no line) | `.git` there and lesson 1.12 not reached (lesson 1.12 station 1 starts with doctor and then runs `git init` in the workspace, so a learner who starts that station again gets no line, and none is printed instead): 「学习工作区：最外层有一个 .git，学习工作区已经被当成了一个仓库。把学习工作区变成仓库是第 1.12 课的事，现在出现，多半是在错的文件夹里运行了 git init。先什么都不要删。 → 对导师说“急救：学习工作区里多了 .git”」 | |
| `starter` | every file of `starter_manifest.json` against `<workspace>/starter/` (sha256), except `learner_edits` (`starter/hello-fx/convert.py`) | (no line) | | 「练习用的起始文件（starter/）：starter/hello-fx/rates.txt 不见了、starter/my-site/index.html 改过，和课程原来的样子对不上。练习不受影响：练习场景和考试用的都是工具里存的原样。想恢复原样，对导师说“急救：starter 被改动了”。」 (more than three: 「…等 N 个文件」) |
| `developer` | `~/Developer` | exists | | missing（第 0.2 课会建立它）; exists but is not a folder |
| `code` | `code` on `PATH` | found | not found（第 0.1 课第 3 站要用；→ 对导师说“急救：code 命令找不到”） | |
| `gh` | `gh` on `PATH`, `gh --version`; the lesson in the baseline's `installed_in` (1.11) and whether all its stations passed | installed and that lesson done: 「GitHub CLI（gh）：2.105.0」 | missing after that lesson: 「GitHub CLI（gh）：在 PATH 里找不到。第 1.11 课装过它，后面的课还要用。 → 把这一行发给导师」 | missing before it: 「GitHub CLI（gh）：还没安装。第 1.11 课会带你装，在那之前用不到。」; installed before it: 「GitHub CLI（gh）：已经装了（2.105.0）。第 1.11 课才用到。」 |
| `net` | with `--net` only: one `HEAD https://github.com` through `urllib`, 8 s timeout, no data sent; any HTTP answer (even 403) counts as reachable | reachable | | unreachable or slow; without `--net`: 「这次没有检查」 |

The location line when the workspace is in a synced folder (it stays in 需要处理 on purpose: check 0.2c asks which group it is in). Every text starts 「学习工作区的位置：<real path>，在 iCloud 同步的文件夹里（~/Desktop）。代码放在同步盘里容易出怪问题。」:

| Situation | Then | Arrow (`lesson`) |
|---|---|---|
| no decision, or another one | (nothing more; 「~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero 照样能用。」 when a link is there) | 「→ 第 0.2 课会带你处理」 (0.2) |
| `stay-in-sync`, entrance present | 「~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero 照样能用；学习工作区本身还在同步盘里。这是你在第 0.2 课做的决定：先留在原处。」 | 「→ 第 1.12 课把课程变成仓库之前，会再问你一次」 (1.12) |
| `stay-in-sync`, nothing at `~/Developer/fullstack-from-zero` | 「这是你在第 0.2 课做的决定：先留在原处。~/Developer/fullstack-from-zero 这个入口还没有建，课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。第 1.12 课把课程变成仓库之前，会再问你一次要不要搬。」 | 「→ 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”」 (0.2) |
| `stay-in-sync`, a broken link or a link elsewhere | 「这是你在第 0.2 课做的决定：先留在原处。~/Developer/fullstack-from-zero 有一个入口，但它没有通到这个学习工作区（指向的地方不存在，或者是别的文件夹），课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。第 1.12 课把课程变成仓库之前，会再问你一次要不要搬。」 | same as above (0.2) |
| `stay-in-sync`, a real different folder there (a half-finished move) | 「这是你在第 0.2 课做的决定：先留在原处。」 | 「→ 第 1.12 课把课程变成仓库之前，会再问你一次」 (1.12) |

Once lesson 1.12 is done (all its stations passed) the clause 「第 1.12 课把课程变成仓库之前，会再问你一次要不要搬。」 is left out, and the entrance-present arrow reads 「→ 第 1.12 课已经问过你了；想搬的时候对导师说“帮我把课程安置到 ~/Developer”」.

The location line when the workspace is **not** in a synced folder (or that cannot be told), and nothing or a broken link or a link elsewhere is at `~/Developer/fullstack-from-zero` although the learner has a `workspace_location` decision or has passed lesson 0.2: a 需要处理 line 「学习工作区的位置：<real path>，不在同步到云端的文件夹里。这是你在第 0.2 课做的决定：先留在原处。~/Developer/fullstack-from-zero 这个入口还没有建，课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。 → 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”」 (the sentence on the decision only for `stay-in-sync`; a broken link or a link elsewhere: 「~/Developer/fullstack-from-zero 有一个入口，但它没有通到这个学习工作区（指向的地方不存在，或者是别的文件夹），课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。」). Before lesson 0.2 nothing is said about the entrance.

**Arrows after the lesson.** A 需要处理 line that points at a lesson (「→ 第 1.6 课会带你处理」, 「→ 第 1.6 课会带你正式设好」, 「→ 第 1.6 课之前要弄好，把这一行发给导师」, the signing lines of 1.6 and 1.11) says 「→ 第 1.6 课已经学过了，把这一行发给导师」 once every station of that lesson has passed: the problem came back after the lesson, so the tutor handles it.

Example (a machine like that of plan G7 after 0.2c with the entrance):

```text
⚠️ 需要处理（2 项）
  - 提交签名：已经打开（commit.gpgsign=true，格式 openpgp），但找不到签名程序 gpg。现在每次 git commit 都会失败。 → 第 1.6 课会带你处理
  - 学习工作区的位置：~/Desktop/fullstack-from-zero，在 iCloud 同步的文件夹里（~/Desktop）。代码放在同步盘里容易出怪问题。~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero 照样能用；学习工作区本身还在同步盘里。这是你在第 0.2 课做的决定：先留在原处。 → 第 1.12 课把课程变成仓库之前，会再问你一次
```

Every check runs on its own. A check that raises (a timeout, a missing program, a bug) becomes the 仅提示 line `<topic>：这一项没查成（<reason>），无法判断。` (the reason is Chinese: the tool's own summary, a reason for a file-system error, or 工具内部出错) and the others go on. Git is always asked from the folder `/`, so a repository the learner happens to stand in cannot change the answers; values are the effective ones outside a repository (system plus global configuration).

**Privacy.** The identity values are reduced to 已设置 / 未设置 inside the check and never printed, stored or logged; the signing key id is never printed either. Every path is shown with `~` for the home folder; inside a simulation, paths under the real account's home (for example a `python3` installed there) are also shown with `~`, so the real user name never reaches the screen or `last-result.json`.

#### 17.2.2 Output and exit code

Example: a Mac in the case of plan G7 before lesson 0.2 (assembled from a run in a simulation home, with the workspace check run against a workspace on an iCloud-synced Desktop):

```text
环境检查 · 2026-11-19
只看不改：这个命令不会改动你电脑上的任何设置。

✅ 没问题（8 项）
  - macOS 版本：27.2.1
  - 登录用的 shell：zsh 5.9（/bin/zsh）
  - python3：3.9.6（/usr/bin/python3，PATH 里排第一个的 python3）
  - Git：2.54.0 (Apple Git-157)
  - Git 身份：user.name 已设置，user.email 已设置（这里不显示内容）。
  - 新仓库的第一个分支名：main
  - 全局忽略文件：有（~/.gitignore_global）
  - code 命令：有（/usr/local/bin/code）

⚠️ 需要处理（2 项）
  - 提交签名：已经打开（commit.gpgsign=true，格式 openpgp），但找不到签名程序 gpg。现在每次 git commit 都会失败。 → 第 1.6 课会带你处理
  - 学习工作区的位置：~/Desktop/fullstack-from-zero，在 iCloud 同步的文件夹里（~/Desktop）。代码放在同步盘里容易出怪问题。 → 第 0.2 课会带你处理

仅提示（4 项）
  - Git 的编辑器：vi。提交时如果没写 -m，Git 会打开它，新手容易卡在里面。第 1.6 课会把它换掉。
  - ~/Developer 文件夹：还没有。第 0.2 课会建立它。
  - GitHub CLI（gh）：还没安装。第 1.11 课会带你装，在那之前用不到。
  - 能不能连上 github.com：这次没有检查（要检查就加 --net）。

小结：有 2 项需要处理。每一项后面写了谁来处理，不用现在自己动手。

这份结果也存到了 learner/last-result.json，导师可以直接看。
```

Exit code 0 whatever was found. Exit code 2 (检查器出问题, printed after the report) only when the doctor itself failed, which in practice means `learner/last-result.json` could not be written.

#### 17.2.3 `learner/last-result.json`

```json
{
  "ts": "2026-11-19T10:00:00",
  "kind": "doctor",
  "target": "doctor",
  "net": false,
  "counts": {"ok": 8, "todo": 2, "info": 4},
  "findings": [
    {"key": "git.signing", "group": "todo", "lesson": "1.6",
     "text": "提交签名：已经打开（…）。 → 第 1.6 课会带你处理"},
    {"key": "git.editor", "group": "info", "text": "Git 的编辑器：vi。…"}
  ]
}
```

`key` is the first column of the table in 2.1 (plus `git.skipped` when git is unusable); `group` is `ok` / `todo` / `info`; `lesson` is present on todo lines that a lesson handles (`"1.11"` for the SSH signing lines, `"1.6"` for gpg, `doctor.GPG_SIGNING_LESSON` / `SSH_SIGNING_LESSON`). It replaces the previous last result (a `check` result, for example); the tutor reads `kind` to tell them apart.

#### 17.2.4 Replacing parts in tests

Module attributes of `courselib.commands.doctor`, patched with `unittest.mock.patch.object` (deliberately not environment variables, so the learner never sees a knob): `XATTR` (default `/usr/bin/xattr`), `XATTR_TIMEOUT` (5), `RUN_TIMEOUT` (10), `NET_URL`, `NET_TIMEOUT` (8), `open_url(request, timeout)` (the function that makes the `--net` request). Every program other than `xattr` is found on the `PATH` of `app.env`, so a test controls it by putting a folder of stub scripts first, or alone, on `PATH`.

### 17.3 `fresh`

`python3 tools/course.py fresh` compares the installed tool versions with `tools/courselib/baseline.json` and lists the lessons that may be affected (plan G4, I4). Read-only, offline, writes nothing (not even `last-result.json`). It reads `learner/state.json` directly and only for reading (never through the store; a missing or damaged file counts as nothing passed), to know whether the lesson that installs a tool is done.

For each tool in the baseline it runs the tool's version command (an argument list, no shell, 15 s timeout, `cwd=/`, `LC_ALL=C`), searches the tool's `pattern` in standard output, then in standard error, and classifies:

| Class | Rule |
|---|---|
| 一致 | the same numbers (`5.9` equals `5.9.0`) |
| 小版本变了 | the same major version, something after it differs |
| 大版本变了 | the major version differs. For a tool whose major number is 0 (uv 0.13.5, Ruff 0.17.2) the first two numbers are its major version, because 0.x tools make breaking changes in the minor number: `0.13.5 → 0.14.0` is 大版本变了, `0.13.5 → 0.13.9` is 小版本变了 |
| 还没安装（第 1.11 课会装） | the command is not on `PATH`, the entry has `installed_in`, and that lesson is not done yet (a station of it has not passed). Not a problem: no 说明 line, not counted as drift, lessons that name the tool are not listed |
| 没装 | the command is not on `PATH` (and, for an entry with `installed_in`, that lesson is done) |
| 看不懂版本 | the command ran but its output holds no version the pattern recognises, it failed without output, or it timed out |

Changed versions get （比课程新） or （比课程旧）. Every 没装 and 看不懂版本 gets a line under 「说明：」 saying what was run and what came back (paths with `~`). None of these is an error.

Then, for every usable lesson in `stages/`, the tool names in `META["verified"]["tools"]` are matched against the baseline: a lesson that names a tool whose class is not 一致 is listed with those tools. Tool names that a lesson uses but the baseline does not cover (for example `sqlite3`, `less`) are listed separately as not compared. The report ends with exactly one of:

- 下一步：把这段发给导师，说“帮我核实受影响的课”。 (some lesson is affected)
- 下一步：有工具的版本变了，但现有的课都没有用到它们，可以照常学。想确认的话，把这段发给导师。
- 下一步：所有工具都和课程核对时一样，不用做什么。
- 下一步：装了的工具都和课程核对时一样，不用做什么。还没安装的，到了上面写的那一课会带你装。 (every installed tool agrees, some are still to be installed)

Exit code 0 in all those cases; exit code 2 (检查器出问题) only when `baseline.json` is missing or malformed (also an `installed_in` that is not a lesson id such as `"1.11"`). Today, on the reference Mac's tools (plan G7), ten rows are 一致 and gh is 还没安装（第 1.11 课会装）: `  GitHub CLI（gh 命令）     2.105.0     -         还没安装（第 1.11 课会装）`.

Test knobs: `courselib.commands.fresh.BASELINE` (path of the baseline file) and `RUN_TIMEOUT`.

**For lesson authors:** use the baseline's keys in `META["verified"]["tools"]` (`macos`, `zsh`, `git`, `python3`, `code`, `uv`, `ruff`, `node`, `npm`, `brew`, `gh`) with the version you verified against, for example `{"git": "2.54.0", "macos": "27.2.1"}`. Other names from `courselib.syllabus.TOOL_NAMES` are allowed but are only listed, not compared: tools that ship with macOS (`less`, `vi`, `man`, `grep` 「grep（查找文字的命令）」, `zip` 「zip（打包压缩的命令）」) are deliberately not in the baseline and appear under 「课程模块里提到、但基线里没有记录版本的工具（fresh 不比较它们）」, for example 「  - grep（查找文字的命令）：1.3」.

### 17.4 `tools/courselib/baseline.json`

```json
{
  "schema": 1,
  "verified_on": "2026-11-19",
  "note": "…",
  "tools": {
    "git": {"label": "Git", "version": "2.54.0",
            "command": ["git", "--version"], "pattern": "git version (\\d+(?:\\.\\d+)+)"}
  }
}
```

| Key | Version | Command | Output on the reference Mac, 2026-11-19 |
|---|---|---|---|
| `macos` | 27.2.1 | `sw_vers -productVersion` | `27.2.1` |
| `zsh` | 5.9 | `zsh --version` | `zsh 5.9 (arm64-apple-darwin26.0)` |
| `git` | 2.54.0 | `git --version` | `git version 2.54.0 (Apple Git-157)` |
| `python3` | 3.14.9 | `python3 --version` | `Python 3.14.9` |
| `code` | 1.145.2 | `code --version` | `1.145.2` (first of three lines) |
| `uv` | 0.13.5 | `uv --version` | `uv 0.13.5 (Homebrew 2026-10-22 aarch64-apple-darwin)` |
| `ruff` | 0.17.2 | `ruff --version` | `ruff 0.17.2` |
| `node` | 26.12.0 | `node --version` | `v26.12.0` |
| `npm` | 11.20.0 | `npm --version` | `11.20.0` |
| `brew` | 7.0.10 | `brew --version` | `Homebrew 7.0.10` |
| `gh` | 2.105.0 | `gh --version` | not installed (lesson 1.11 installs it); the version is the latest release on https://github.com/cli/cli/releases/latest, read 2026-11-19 (「GitHub CLI 2.105.0」, tag v2.105.0, released 2026-11-18), `installed_in` `"1.11"` |

The keys are the tool names of `courselib.syllabus.TOOL_NAMES` (so `python3`, `code`, `brew` rather than "python", "vscode", "homebrew"). `pattern` is a Python regular expression searched line by line (`re.MULTILINE`); group 1 is the version. `label` is what the report shows. Optional keys: `installed_in` (the lesson that installs a tool the learner does not have yet) and `note` (where the version came from).

Updating it: change `version` (and `verified_on`) only after the lessons that name the tool have been re-verified with the new version; otherwise `fresh` would stop pointing at them. `fresh` checks the file's shape on every run.

### 17.5 Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/tests -p 'test_doctor.py'
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/tests -p 'test_fresh.py'
PYTHONDONTWRITEBYTECODE=1 /Library/Developer/CommandLineTools/usr/bin/python3 -m unittest discover -s tools/tests -p 'test_doctor.py'
```

`tools/tests/envstubs.py` provides `FakeBin` (a folder of `#!/bin/sh` stub programs: `prints(name, text, code=0, stderr=False)`, `script(name, body)`, `remove(name)`, `real_git()` and `learner_machine()` with the versions of G7, no `gpg`, no `gh`), `xattr_stub(folder, flagged=(), fail=False)` (folders in `flagged` carry the iCloud attribute) and `SECRETS` (the fake identity values that must never appear). Stub scripts run with the test's `PATH`, so inside them call system programs by absolute path (`/bin/sleep`, `/usr/bin/grep`). The doctor tests need a real `git` (they read real configuration from the sandbox home) and are skipped without one.

### 17.6 `tools/dev/build_starter_manifest.py`

For builders and the tutor (Python 3.9+, standard library). `tools/courselib/starter_manifest.json` (`{"schema": 1, "note": …, "learner_edits": ["starter/hello-fx/convert.py"], "files": {path: {"sha256": …, "text" | "base64": …}}}`) holds the original of every file under `starter/`; scenarios, the state ladder and exams build from it (plan G11a).

```bash
python3 tools/dev/build_starter_manifest.py --check     # exit 0 when starter/ and the manifest agree
python3 tools/dev/build_starter_manifest.py --write     # builders: after changing starter material on purpose
python3 tools/dev/build_starter_manifest.py --restore starter/my-site/index.html   # the tutor's repair
```

- `--write` regenerates the manifest from disk (text as text, anything not UTF-8 as base64; `.DS_Store`, `__pycache__`, `*.pyc` skipped). **Run it whenever you add or change a file under `starter/`**; `test_starter_manifest` fails until you do.
- `--check` exits 1 and names each file: `改动过：…`, `不见了：…`, `清单里没有：…`, then 「是被不小心改了：运行 --restore <路径> 恢复原样（只恢复 doctor 点名的文件）。--write 只给建课的人用：故意改了 starter/ 以后，用它更新清单。」. Copies left by `--restore` are listed as `（导师恢复时留下的副本，不算问题：…）` and do not fail. A changed `learner_edits` file (`starter/hello-fx/convert.py`, which lesson 0.1c tells the learner to edit) is listed on its own line 「课文让学习者自己改的文件，改过不算问题：starter/hello-fx/convert.py」 and never makes the exit code 1; alone it gives 「starter/ 和清单一致（N 个文件）；只有课文让学习者自己改的文件改过了，不算问题。」 (exit 0). The builders' guard for that file is `test_starter_manifest`, which calls `compare` directly.
- `--restore PATH ...` (relative to the workspace root, or absolute inside `starter/`) first copies the present file to `PATH.changed` (`PATH.changed-2`, … when taken), then writes the original back; it never deletes and refuses with exit 2 outside `starter/` or for unknown files. A `learner_edits` file is refused (exit 2: 「拒绝：starter/hello-fx/convert.py 是课文让学习者自己改的文件，里面是学习者的练习。真要恢复原样，再加上 --force（改过的那一份照样会留成 .changed）。」) unless `--force` is given.
- `--write` is never run in the learner's workspace: it would make the learner's edited files the new originals. Its `-h` help says so: 「--write  regenerate tools/courselib/starter_manifest.json from starter/ (builders only; never run it in the learner's workspace)」.

The tutor's flow for 「急救：starter 被改动了」 (doctor's starter line): run `--check`, ask the learner whether the files doctor names matter to them, then `--restore` only those files. Library helpers for command authors: `scenario.load_starter_manifest()`, `starter_originals(source)`, `copy_starter(source, target)`, `starter_differences(workspace)`; test knob `scenario.STARTER_MANIFEST`.

## 18. Behaviour where the plan leaves a choice

Choices the toolchain makes where plan I4/I5 leave room or say something slightly different. They are deliberate; testers should not report them as bugs.

| Plan wording | What the tool does | Why |
|---|---|---|
| I5: a missing `state.json` is reported as 检查器出问题 | a missing `state.json` is created; if `log.jsonl` has records the state is rebuilt from them (that is also the recovery path after renaming a corrupt file). A **corrupt** `state.json` is reported as 检查器出问题 with the exact `mv learner/state.json learner/state.json.bad` command and is never overwritten | a fresh workspace has no state file; refusing to start would block the first lesson |
| I5: writes are atomic | `state.json` is written first (temporary file, then rename), the log entry after it; a `learner/` folder or state file that cannot be written is found **before** a check runs, so `check` prints exactly one outcome. A read-only `state.json` is never replaced. `status` still shows progress when it cannot record the session (one ⚠️ line at the end, exit 0) | plan I4: exactly one of three outcomes; a rename would silently replace a protected file |
| I4 check: "optionally asks for a 1-5 confidence rating first" | asked only at a terminal, only before a station's first attempt and only until it has passed; Enter skips; an unreadable answer (「很有把握」) is skipped with a short notice | asking on every retry would nag |
| I4 check: one station or a lesson | `check <lesson>` runs only the stations not yet passed; `--again` re-runs all | a later station may have changed the practice state an earlier one looked at |
| I4 hint: level 4 marks 带扶手完成 | level 4 marks the station `assisted` even before it has passed, and schedules the cold redo 3-7 days later; at a terminal level 4 asks for confirmation first, without a terminal (`--yes`, or the tutor running it through a tool) it is shown directly | the full answer was seen, whatever happens next |
| I4 scenario: "refuses to overwrite a non-empty folder" | a complete earlier build of the same scenario is shown again (exit 0) instead of being refused; a half-built one (`"complete": false`) is rebuilt without `--reset`; anything without the marker is refused, and `--reset` is not suggested for it | a learner who forgot where the folder is asks again; a build the tool never finished holds no learner work |
| I4 check: 还没达标 counts as an attempt | a 还没达标 caused only by a missing or half-built scenario is not counted | the learner has not tried yet |
| I4 doctor / fresh: read-only | `doctor` writes `learner/last-result.json` (its report, for the tutor) and nothing else; it never loads `state.json`. `fresh` writes nothing | the tutor reads the last result |
| I4: `COURSE_NOW` | sessions created under `COURSE_NOW` are stored like real ones | it is a test override for throw-away workspaces; the learner never sets it |
| I7: the practice list after a fail | `exam` prints it and the next `exam <gate>` is the retest on the other form (section 15.5) | |
| I7: 4-6 cold tasks per gate | one sitting holds one task per lesson the gate covers (4, 5, 5, 6 today); the explain-back verdict is recorded with `exam <gate> --explain`; a gate is passed when every lesson has a passed task and the explain-back is recorded as pass | COMMON.md section 1, 2026-11-19 |
| I4 exam: `--all` | a full sitting, one task per lesson, preferring tasks never drawn; after the practical part is passed it is extra practice that never takes a passed lesson back | not "all tasks again": a full sitting stays the length of one sitting |
| I4 status: "the next step" | `status`, `check` and `journal` answer with one function (`status.next_step`, section 6.8); a gate never blocks the next lesson but stays listed | the three must say the same sentence to the tutor |
| `--explain` before any graded sitting | refused; after any graded sitting accepted, also while the practical part is open; the latest verdict counts | the explain-back is about the learner's own practical work |

## 19. Changes to API v1 after the testers' round

Three independent testers attacked the toolchain on 2026-11-19 (items 1-15). Names and signatures above did not change; these behaviours did. Lesson modules written against the earlier text keep working, but check them against this list.

1. `repo.is_clean()` is False for a folder that is not a repository (it was True).
2. `repo.query(...)`: `grep` is no longer accepted; `--ext-diff`, `--open-files-in-pager` and `--exec` are refused like `--output`; every query runs on a temporary copy of the index.
3. `ctx.run(...)` refuses `git` as the program (use `ctx.git`), clamps `timeout` to 1-60 seconds (so `timeout=None` no longer waits forever) and sets `GIT_OPTIONAL_LOCKS=0`. Its docstring no longer says "never raises": a check that calls it wrongly raises `ValueError`.
4. `ctx.ask(...)`: an empty answer is asked again (three empty answers cancel the check); `--answer ""` is a usage error; an expected `0` also accepts 没有 / 无 / 零.
5. `ctx.parse_int(...)` returns None for a negation of the number, also when a digit is present (`"不是3"`). (Since 2026-11-20 only a negation next to the number counts; section 8.)
6. `ctx.need_repo(...)` raises (检查器出问题) for a folder with a `.git` that Git does not recognise.
7. `ctx.scenario(...)`: a missing or half-built scenario still ends the check with 还没达标, but the run is not counted as an attempt; the advice for a half-built one is the plain `scenario <id>` command (no `--reset`).
8. Anything a check or a builder writes to standard error, and every Python warning, is captured like standard output.
9. `sc.git(rel, ...)` refuses a first argument that starts with `-`; `sc.git_commit(...)` refuses a folder that is not itself the top of a repository; builder Git never looks above `sc.root`.
10. The playground may not lie inside the workspace or inside `~/Developer/my-site`, nor contain `~/Developer/my-site`.
11. `tools/dev/make_sim_home.py` no longer copies the learner-owned `journal/`, `notes/`, `learner/` and `PROGRESS.md` (use `--with-learner-files`).
12. The worked example's station check no longer lists 「没有落下还没提交的改动」 as achieved before the learner has made a commit: an untouched practice repository is clean too. Do the same in your checks (only praise what the learner did).
13. `scenario <lesson>` (the `start` scenario) no longer ends with the check command of the lesson's first station; it tells the learner to carry on with the lesson text (section 15.1). The tool's `cd` step is dropped when a `sc.todo` line already gives a `cd ` command.
14. `check <lesson>` lists a station that is 带扶手完成 with its redo window instead of plain 已通过, and adds one line naming those stations under the 全课 headline.
15. `gitwrite.git_commit` tests that the folder is the top of a repository before it stages anything.

Changes of 2026-11-19 evening (two batches by five writers, integrated and documented the same night; all within API version 1, nothing a lesson can call was renamed or removed). Each item names what a lesson author must check:

16. **Minutes (plan G5a).** `validate` accepts `minutes` from 15 to 40, warns above 30, and warns when a 「## 第 N 站：……（约 X 分钟）」 heading disagrees with META or when an option's whole text is a review command such as `q` or `s` (write 「按 q」). Section 3, section 14.
17. **`ctx.choose(question, options, key=None, explain="", feedback=None)`** for free decisions: prints 「你的决定：<label>」, never right or wrong, stores `decisions[key]` like `ctx.decide`. Replace every `ctx.quiz` / `ctx.ask` that has no right answer by it. Section 6.6.
18. **`ctx.gate_done(gate)` and `ctx.gate_result(gate)`** read a gate's results the way `exam` does; never parse `ctx.state["exams"]` yourself. `gate_done` needs the practical part **and** the explain-back recorded as pass; `gate_result` has `practical_done`, `explain`, `explain_date`, `lessons`, `open_lessons`, `open_lesson_titles`, `next_count`, `next_minutes` besides the older fields, and `.open` lists only tasks tried without a pass, so name what is missing with `.open_lesson_titles`. Section 6.7.
19. **`ctx.git_global_state(key)`** (`"true"` / `"false"` / `"unset"` / `"invalid"`) and **`ctx.git_global_all(key)`**; use them instead of reading `git_global` and guessing at typos or empty values. Section 6.4.
20. **`ctx.parse_int`** finds the number anywhere (「第二条」 2, 「一共三个」 3, 「大概五个」 5); drop workarounds that strip 「第」「一共」 before calling it. Section 8.
21. **Messages no longer collapse U+3000 or U+00A0**; quote the learner's text through **`ctx.visible(text)`** (〔全角空格〕, 〔Tab〕, 〔不换行空格〕, trailing ·) instead of a hand-written replacement. Section 6.1.
22. **Paths.** `ctx.show` and every path the tool prints show `~` also when HOME is reached through a link (drop `os.path.realpath` workarounds), and show the workspace through `~/Developer/fullstack-from-zero` whenever that path leads to it (the moved folder or the entrance). Write `cd ~/Developer/fullstack-from-zero` everywhere, quote tool output with that path, and use **`ctx.show(target, entrance=False)`** where a check must name the real place. Never hard-code `cd ~/Developer/fullstack-from-zero` in `sc.todo`. Section 6.2.
23. The traceback of a 检查器出问题 result and everything else the tool stores or asks the learner to send carry `~` for every spelling of the home folder.
24. **Full-width characters on the command line** answer 「用法不对：命令里混进了全角字符（中文输入法打出来的空格或符号）：check〔全角空格〕1.14a。切回英文输入法，把这一段重新打一遍。」 (exit 64), not 「没有 check　1.14a 这个命令」. Section 8.
25. **Usage errors** call a word that starts with `-` a 选项: 「用法不对：不认识的选项：--wirte」 (was 「不认识的参数：--wirte」), 「用法不对：选项 --confidence 后面要跟一个值」; other words stay 参数. Section 8.
26. **What comes next.** `check`, `status` and `journal` say the same sentence of COMMON.md section 2 (「从 1.6b 继续」, 「从 1.6 的收尾继续」, 「从 1.7 开始」, 「做小关卡 gate-a」, 「请问我 gate-a 的讲解题」, 「准备阶段 2」, 「开始上课」); `status` prints 「下一步：……。下次可以对导师说“……”。」, `journal` 「下次从哪开始（直接回车 = 从 0.1 的收尾继续）：」; every open gate adds 「小关卡 gate-a「终端与文档关卡」还没有通过，它不挡下一课。…」. 「继续下一阶段」 and 「对导师说「继续下一阶段」」 are gone. Every 存档点 and 收尾 line uses these sentences; re-paste any check, status or journal output. Section 6.8.
27. **Gate lines in check and status** name the gate as COMMON.md section 3 does and include the explain-back: 「下一步是小关卡 gate-b「本地 Git 关卡」：5 道实操题，预计 29 分钟，讲解题另需约 10 分钟。开始考试：python3 tools/course.py exam gate-b」 (约 10 分钟 since 2026-11-20, item 59; was 「下一步是关卡 gate-b「本地 Git 关卡」：… 分钟。开始考试：…」); 「下一步是 gate-0「起步小关卡」：…」; 「小关卡 gate-b「本地 Git 关卡」的实操题都通过了，还差讲解题（约 10 分钟）：…」. Section 6.8.
28. **Closing steps printed by `check <lesson>`** follow COMMON.md section 3: 「1. 行规笔记：运行 code notes/my-rules.md，在小标题「GIT-01 …」「GIT-02 …」下面各用自己的话写一两句，再配一个你自己的例子」, 「2. 一句话日志：python3 tools/course.py journal」, and from lesson 1.12 on 「收尾还有三件小事：」 with 「3. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做」 (was 「用自己的话把本课行规（…）各写一句到 notes/my-rules.md」 / 「写一句日志：…」). A passed whole-lesson check is stored in `state["lesson_checks"]`. Section 6.8.
29. **`ctx.final`** is True inside `exam --grade`; `ask` and `quiz` then end a wrong answer with 「这个回答和实际情况对不上，这一题记为还没达标。」 / 「这一题没有选对，记为还没达标。」 (since 2026-11-20; was 「…这一场记为还没达标；补考会换一套题面。」, untrue in a 加练 sitting) Do not add your own "run it again" advice to exam graders. Section 6.6.
30. **The marker `.playground` is version 2**: facts and todo lines are stored base64-encoded under `data`, so a learner's `grep -rin` or `cat .playground` never shows an expected answer (against accidents, not a secret); `ctx.scenario().facts` and `.todo` are unchanged; version 1 markers are still read; tests read a marker with `courselib.scenario.read_marker(folder)`. Section 10.
31. **Starter originals (plan G11a).** `sc.copy_in("starter/…")`, the state ladder and exam copies take the original from `tools/courselib/starter_manifest.json`, never the learner's `starter/`; a `starter/` path not in the manifest is 检查器出问题; whoever changes `starter/` runs `python3 tools/dev/build_starter_manifest.py --write`. Lessons must not say that practice copies come from the learner's `starter/`. Sections 10.2, 17.6.
32. **The state ladder** mirrors what lessons 1.2-1.13 leave in `my-site`: `.editorconfig` from S2, a fenced `zsh` block in the S3 README, two commits in S4, `drafts/colors.md` and five commits in S5 (the 1.7b colour `#c2410c` first appears there), `feat: 调大标题的字号` (not `style:`) and seven commits in S6, the licence section, list line and footer link and eleven commits in S7. Read counts from `site_commits`, never hard-code them, and re-paste any ladder output you quote. Section 15.3.
33. **Exam task screens**: the builder's `sc.todo` lines are shown under the task text; the folder line is 「这道题的文件夹：…」 (was 「文件夹：…」) and the cd line 「先进入这道题的文件夹：cd …。题目里说的文件夹如果在它里面，再 cd 进那一层。」 (was 「进入：cd …」), left out when the text or a todo line contains `cd ` or says 「进入 <folder inside the task>」. Section 15.4 rule 8.
34. **The gate rule.** A sitting holds one task per lesson the gate covers (gate-0 4, gate-a 5, gate-b 5, gate-1 6: the lessons 1.11-1.16 only, no borrowing); a lesson counts once one of its tasks is passed; a retest holds only the lessons not yet passed, with the failed task in its other form; never promise that every task of a pool must be passed. Section 15.5.
35. **`exam <gate> --explain pass|again`** records the explain-back verdict in `state["explain"]`; a gate is passed only when the practical part is passed and the explain-back is recorded as pass, so tell the learner to run that command after the tutor's verdict, and to say 「请问我 <gate> 的讲解题」 to start it. Refused before the first graded sitting. Section 15.5.1.
36. **Exam texts to re-paste**: heads 「关卡考试 · 小关卡 gate-a「终端与文档关卡」 · 第 1 场」, 「关卡考试 · gate-0「起步小关卡」 · 第 1 场」, 「关卡考试 · gate-1「阶段 1 验收」 · 第 1 场」 and 「一共 N 题，每课一题，预计 M 分钟（每题的预计分钟数加起来）。」; the listing (gate-1 shows 「阶段 1 验收（1.11 到 1.16 课）：…」); the grading summary and 「实操题都通过了。还差讲解题：…」. Gone: 「…的考题全部通过了」, 「这个关卡的考题还没写全：现在只有 N 题（正式考试是 4 到 6 题）」, 「都已经通过了」. `--all` is a full sitting (加练 after the practical part), never 「全部重考」. Section 15.5.
37. **`scenario <id>`** ends with 「练习场里的东西随便改，练习场外面的文件不会受影响。」 and 「改乱了可以重搭一份：python3 tools/course.py scenario <id> --reset」 (already built: 「想从头再来一份（会删掉你在里面做过的改动）：python3 tools/course.py scenario <id> --reset」); lessons that paste the old one-line sentence re-paste it, and a lesson's own todo line need not repeat the `--reset` advice. Section 15.1.
38. **`doctor`**: the location line is 「学习工作区的位置：<real place>…」 (was 「工作区的位置」) and, for a learner who stayed, names the entrance or the sentence “我先不搬，帮我在 ~/Developer 建一个入口”; the identity line says Git composes an identity and commits; a `.git` in the workspace before 1.12a is 「…对导师说“急救：学习工作区里多了 .git”」; changed starter files get one info line; every signing todo line names 「commit.gpgsign=true，格式 …」, the SSH lines (empty `gpg.ssh.program`, no ssh-keygen, no key, missing key file) point to lesson 1.11, the gpg lines to 1.6; gh is 「GitHub CLI（gh）：还没安装。第 1.11 课会带你装，在那之前用不到。」 (was 「还没装」). Re-paste any doctor output and any quiz that quotes 「工作区的位置」. Section 17.2.
39. **The simulation home** writes `[gpg "ssh"]` with `program` and `allowedSignersFile` present and empty (and `tag.forceSignAnnotated = false`); SSH signing there fails with `error: cannot run : No such file or directory` until `gpg.ssh.program` is unset or set; `--stay` builds the stayed learner's layout with the entrance. Section 17.1.
40. **`status`** no longer prints the 70 % notice while the next stage's lessons already exist (lesson 0.4's sample), and its PROGRESS.md section 「## 关卡」 lists every gate with the state words of the exam listing (「- gate-b 小关卡「本地 Git 关卡」（1.6 到 1.10 课）：实操题都通过了，还差讲解题」; was 「通过 n/m 题（最近一次 …）」).
41. **The syllabus**: lesson 1.4 has three stations (1.4a-1.4c); the rule families carry the labels accepted on 2026-11-19 (WS-02 规范·组织, DOC-02 规范·本课程约定, REPO-01 惯例·事实标准, HELP-01 惯例·平台与工具, AI-01 规范·组织); `GATES["gate-1"]["lessons"]` is 1.11-1.16.
42. **`baseline.json` has `gh`** (2.105.0, from the official release page, `installed_in` 1.11): use `"gh": "2.105.0"` in `META["verified"]["tools"]`; `fresh` prints 「还没安装（第 1.11 课会装）」 for it until lesson 1.11 is done, with the closing sentence 「下一步：装了的工具都和课程核对时一样，不用做什么。还没安装的，到了上面写的那一课会带你装。」. Section 17.3.
43. **`validate` checks the one wording of the recurring parts** (warnings, with the line, what it found and the fixed form): `[I1]` save points and the mid-station save point before a gate, the four parts of every station and the hint and check lines that end 「自己做」, the 收尾 heading, steps and last line, optional-material labels; `[G6]` the G6 line, the marks and `unverified_steps`; `[G2]` sentences to the tutor in lesson.md and lesson.py, straight quotes around Chinese; `[G10]` course-folder paths and names (学习工作区, no 课程文件夹, no `/Users/<ascii>`); `[I2]` the 本课行规 table against the cards and every 约束力 level word with its scope; `[G4]` since-when in every 旧教程提醒 and `git config` without a subcommand; `[G5]` the header's station count and minutes; `[X]` one English gloss under two terms and the decided owners of terms and commands. `validate --complete` also requires a task of its gate in every lesson. Section 14.
44. For command writers: `runner.run_check(..., final=False)`; `Catalog.gate_pool` (now `(primary, [], unusable)`), `Catalog.gate_ids`, `Catalog.gate_lesson_ids`, `catalog.usable_exam_task`; the `progress.gate_*` functions with `progress.gate_status(catalog, state, gate)` as the one call; `status.next_step(app, state, catalog=None, reviews=True, after=None)`, `status.gate_view`, `status.gate_state_words`, `status.lesson_checked`, `status.record_lesson_check`; `check.what_comes_next`, `check.step_lines`, `check.wrapup_lines`; `syllabus.gate_kind` / `gate_name` / `gate_label` / `gate_titled`; `App.entrance()`, `App.entrance_kind()`, `App.entrance_is_link()`, `App.show(path, entrance=True)`, `App.home_spellings()`, `app.account_home()`; `cmdkit.word_kind`, `cmdkit.unknown_words`; `commands.review.RESERVED_WORDS`; `ui.visible`; `commands.scenario.reset_command(typed)`. Removed from `commands/exam.py`: `gate_pool`, `choose`, `final_grader`, `_usable`, `_open_ids`, `_gate_done`, `MIN_TASKS`.

### 19.1 After the two reviews of 2026-11-20

45. **`ctx.parse_int`** reads a negation only next to the number: 「5 个，不算 . 和 ..」 is 5 (lesson 1.1's own condition repeated), 「3（不确定）」 3, 「4 行（第一行是标题）」 4; still None: 「不是3」「没有 3 个」「不到 3 个」「一个也没有」「负一」, ranges 「三到四个」「3 到 4 个」, halves 「三个半」. Section 8.
46. **Closing steps of a lesson without a new rule** (1.3): 「收尾还有一件小事：」 / 「1. 一句话日志：python3 tools/course.py journal」 (from 1.12 on 「收尾还有两件小事：」 with the backup as step 2). The notes step 「用自己的话把这一课最想记住的一点写到 notes/ 里」 is gone. Section 6.8.
47. **An open, ungraded sitting** is named in `check` and `status`: 「小关卡 gate-b「本地 Git 关卡」第 1 场考试还没批改完（5 题）：做完以后批改：python3 tools/course.py exam gate-b --grade；想放弃这一场重新出题：python3 tools/course.py exam gate-b --new。」 + 「下次可以对导师说“做小关卡 gate-b”。」; the note line after the gate's lessons: 「…第 1 场考试还没批改完（5 题），它不挡下一课。做完以后批改：python3 tools/course.py exam gate-b --grade」. Section 6.8.
48. **`status`**: the first line follows the next step (「你在：0.4 像管项目一样管学习 · 收尾」, 「你在：gate-0「起步小关卡」（学完 0.4 课以后）」); the landing line is 「下一个落脚点是小关卡 gate-a「终端与文档关卡」（学完 1.5），还有 11 站」 (was 「到下一个落脚点「终端与文档关卡 gate-a」（学完 1.5）：还有 11 站」); the long-break sentence uses “ ”: 「对导师说“我回来了，带我走回归流程”。」 (also in `review`). A state written before 2026-11-19 without `lesson_checks` reads passed whole-lesson checks from `learner/log.jsonl`. Section 6.8.
49. **Exam listing and PROGRESS.md** with an extra practice sitting open: 「实操题都通过了，还差讲解题；第 4 场加练还没批改完（4 题）」 (was 「第 4 场还没批改完（4 题）」). In the head of such a sitting: 「讲解题还差一次，约 10 分钟：对导师说“请问我 gate-b 的讲解题”。」 (约 10 分钟 since item 59) (or nothing after the explain-back passed); 「这是加练：通过的课不会退回去。」 only in a 加练 sitting. Section 15.5.
50. **`--explain`**: `PASS`, `ｐａｓｓ`, `pass　` are accepted; `again` after a recorded pass prints 「之前记的是“通过”（date），现在改成了“再来一次”：小关卡 gate-0 现在还没通过。」; `pass` before the practical part is passed adds 「讲解题的“通过”先记着：等实操题每课都有一题通过，小关卡 gate-0 就通过了。」. The usage error is 「用法不对：选项 --explain 不能是 fail（可以用的值：pass、again）」. Section 15.5.1.
51. **Command line**: punctuation left after an id is dropped (`check 1.1a，`); a stray space around an option is dropped (`"--again "`); an unknown word shows a stray space as · (「不认识的参数：x·」). Section 8.
52. **`doctor`**: a learner with a `workspace_location` decision (or past lesson 0.2) whose `~/Developer/fullstack-from-zero` is missing or broken gets the entrance sentence also when the folder is not synced; after lesson 1.12 the stayed learner's arrow is 「→ 第 1.12 课已经问过你了；想搬的时候对导师说“帮我把课程安置到 ~/Developer”」; a line that points at a lesson already done says 「→ 第 1.6 课已经学过了，把这一行发给导师」. Section 17.2.
53. **`build_starter_manifest.py`**: `--check` names `starter/hello-fx/convert.py` apart (「课文让学习者自己改的文件，改过不算问题：…」) and does not count it; `--restore` refuses it without `--force`; `--write` is for builders only. Section 17.6.
54. **`validate` false alarms removed**: `[G2]` reads only the learner speaking (对导师说 …), not the tutor's words; `[G10]` leaves Git's 工作区 alone from lesson 1.12 on and accepts `/Users/Guest`; `[I1]` flags 选做 / 可选 in a heading only as a label; `[G4]` accepts a named release (「从 macOS Catalina 起」). Section 14.
55. **The simulation home** copies the course's own `README.md` files of `journal/`, `notes/`, `learner/` and the heading skeleton of `notes/my-rules.md`. Section 17.1.
56. For command writers: `status.lesson_checked(state, lesson, app=None)`, `status.logged_lesson_checks(app)`; `progress.gate_summary` / `gate_status` key `sitting_kind`; `progress.gate_full_plan` takes the lessons not passed first when a gate has more than `GATE_MAX_TASKS` lessons (limit: once all of them are passed it always takes the first six, so no gate may have more than six lessons; item 61); `NextStep.sitting` (the open sitting's number on a `gate` step); `scenario.build(..., typed=None)` / `build_lesson_scenario(..., typed=None)`; `cmdkit.clean_id` strips trailing punctuation; `cli._trim_options`; `doctor.Doctor.entrance_needed()`; `build_starter_manifest.restore(..., force=False)`; `make_sim_home.copy_skeletons`, `rules_notes_skeleton`; `validate.REPO_FROM`.

Second pass of 2026-11-20 (the last before the tool is frozen; writer `tools-minor`). Nothing a lesson can call was renamed or removed:

57. **`ctx.parse_int` and comparison words.** An answer that gives a bound and not a number is not a number: 少于, 小于, 低于, 不到, 不足, 不超过, 不多于, 不少于, 至多, 最多, 至少, 最少, 超过, 多于, 大于, 高于 (before or after the number) and 以上, 以下, 以内, 以外 (after it) give None: 「少于3行」「最多 3 行」「至少有 3 个」「超过了 3 个」「至少得 3 个」「3 行以上」「5 个以内」「3 个或以上」「3（以上）」 (some were read as the bound). 左右 is not one of them: 「3 个左右」 is 3. After 第 the word bounds nothing: 「第 3 行最多」 is 3; without 第, 「3 号最多」 and 「3 行以下是空行」 give None, so a which-one question asks for 「第几」 or uses `ctx.quiz`. A question whose right answer is a bound needs a `ctx.quiz` or a string `expected`, not an int. Section 8.
58. **`ctx.parse_int` and negations**: spaces or an opening bracket between the negation and the number no longer hide it: 「不是（3）」「没有（3 个）」「不 是 5」「不太是 5」 give None (were 3, 3, 5, 5). Unchanged: 「3（不确定）」 3, 「5 个，不算 . 和 ..」 5. Section 8.
59. **The explain-back takes about 10 minutes** (`status.EXPLAIN_MINUTES = 10`, COMMON.md section 1 under plan G5a), and no sentence of the tool says how many questions there are: check and status 「…，讲解题另需约 10 分钟。」 and 「…的实操题都通过了，还差讲解题（约 10 分钟）：请导师问你讲解题，评完用 python3 tools/course.py exam <gate> --explain pass 记下（要再来一次就写 again）。」 (was 「（约 5 分钟）：请导师问你两道讲解题，…」); the head of a sitting 「实操题都通过以后还有讲解题，约 10 分钟：导师问你几个问题，请你讲出“为什么这样做”。」 (was 「…约 5 分钟：导师问你两个“为什么这样做”的问题。」) and 「讲解题还差一次，约 10 分钟：对导师说“请问我 <gate> 的讲解题”。」. A lesson that states a gate's whole time adds about 10 minutes to the tasks (on the pools of 2026-11-20: gate-0 about 29-33, gate-a 37-43, gate-b 35-43, gate-1 55-65; section 15.5); 「预计 N 分钟」 printed before a sitting stays the sum of the tasks. Never write 「两道讲解题」 or 「两个问题」: gate-0, gate-a and gate-b add a debugging question. Re-paste any check, status or exam output that shows these lines. Sections 6.8, 15.5.
60. **`status` at a lesson's closing steps and at the gate after it**: the landing line and the stage line follow the same lesson as the first line. 「你在：0.4 像管项目一样管学习 · 收尾」 is followed by 「下一个落脚点是 gate-0「起步小关卡」（学完 0.4）：站都通过了，还差 0.4 课的收尾」 and 「阶段 0 起步：已完成 n/n 站（100%）」 (was gate-a and 「阶段 1 …：已完成 0/40 站（0%）」); 「你在：gate-0「起步小关卡」（学完 0.4 课以后）」 by 「落脚点到了：gate-0「起步小关卡」」 and the same stage line. The same at 1.5 / gate-a, 1.10 / gate-b and 1.16 / gate-1 (whose landing point is named 「gate-1「阶段 1 验收」」). 「还有 0 站」 is never printed; PROGRESS.md agrees. Section 6.8.
61. **`progress.gate_full_plan`**: no gate may have more than six lessons (`GATE_MAX_TASKS`); with more, the lessons after the sixth would never come up in extra practice once all are passed. Today: gate-0 4, gate-a 5, gate-b 5, gate-1 6. Section 15.5.
62. **`validate`**: `[G4]` accepts a named release without spaces next to Chinese (「从macOS Catalina起」「从 macOS Catalina起默认是 zsh」「从Python 3起」) and no longer accepts a count (「Git 2 种写法」); `[I1]` also reports 可选 / 选做 / 选读 / 可以跳过 at the end of a heading, after a comma, and before 的 + 进阶 / 部分 / 内容 / 阅读 / 材料 / 练习 / 题 (「### 可选的进阶」「### 这一段可选」「### 进阶，可选」「### 补充（可以跳过的部分）」); 「### 自己做（可选的两种做法都行）」 stays fine. Section 14.
63. **`build_starter_manifest.py -h`**: the help of `--write` says 「(builders only; never run it in the learner's workspace)」. Section 17.6.

Pass after the lesson round of 2026-11-20 (writer `tools-r5`, the findings of the 20 blind lesson tests). Nothing a lesson can call was renamed or removed:

64. **`doctor` and a `.git` in the workspace**: the 需要处理 line 「学习工作区：最外层有一个 .git，…先什么都不要删。 → 对导师说“急救：学习工作区里多了 .git”」 is printed only while the learner has not reached lesson 1.12: once every station of lesson 1.11 has passed, or station 1.12a, or any station of a lesson after 1.11, a `.git` there is lesson 1.12's own `git init` and nothing is printed (also not instead). A learner who starts station 1.12a again after a break no longer gets this false alarm. Section 17.2.1.
65. **`validate`, closing steps**: a step is classified (全课检查, 行规笔记, 一句话日志, 备份) by its first line; the indented lines and code blocks under it count only when the first line names none. A backup step whose pasted `git status` lists `notes/my-rules.md` no longer gives 「收尾里没有「备份」这一步」. A lesson may keep its backup routine in one step with the sample output under it. Section 14.
66. **`ctx.need_repo(target, label=None, praise=False)`**: 「是一个 Git 仓库：<label>」 is recorded under 已经做到 only with `praise=True` (item 12: only praise what the learner did). Pass `praise=True` only where the learner makes the repository in that very station or task (`git init`, or `git clone` for a restore); a repository built by a scenario, an exam task or an earlier lesson is not praised. A check that recorded nothing else on a pass would now end as 检查器出问题 (no conclusion): every check must record its own ok lines. Failures and the damaged-repository case are unchanged. Section 6.3.
67. **Tool names**: `grep` 「grep（查找文字的命令）」 and `zip` 「zip（打包压缩的命令）」 may be used in `META["verified"]["tools"]` (lesson 1.3 `"grep": "2.6.0"`, lesson 0.4 `"zip": "3.0"`); they are not in `baseline.json` (they ship with macOS, like `less` and `vi`), so `fresh` lists them under 「课程模块里提到、但基线里没有记录版本的工具（fresh 不比较它们）」. A lesson that pastes that part of `fresh` re-pastes it. Section 17.3.
68. **Option texts with another dot**: `quiz`, `choose` and review choice items compare a typed option text after folding `.` `。` `．` `·` `・` `•` `‧` `∙` to one character on both sides, so 「惯例.事实标准」 is option 「惯例·事实标准」 (was 「你的输入「惯例.事实标准」不是 A 到 F 之间的字母」); a text that matches two options after folding matches none; letters and numbers are read as before. Section 6.6.
69. **Gate minutes before and after the draw**: `check`, `status` and the listing print the expected value over the forms (gate-b 「预计 29 分钟」); `exam` prints the sum of the tasks it drew (「预计 27 分钟」, 「预计 30 分钟」). Never promise that the two numbers are equal; give the range of section 15.5 if a number is needed. Section 15.5.
70. **Station counts**: lesson 1.4 has three stations, so stage 1 has 40 stations and the course 52: 「已有的课程的站都通过了（52/52 站）。」, 「阶段 1 工程师的基本功：已完成 0/40 站（0%）」, at the start of stage 1 「下一个落脚点是小关卡 gate-a「终端与文档关卡」（学完 1.5），还有 11 站」, at 1.6b 「…gate-b「本地 Git 关卡」（学完 1.10），还有 10 站」. Re-paste any quoted count.
71. **Stage hours** (`tools/dev/build_reference.py`): the closing minutes of a lesson are the number in its 「## 收尾（约 N 分钟）」 heading (validate checks the header against it); the fixed rule (5, from 1.12 on 10) is used only when the heading is missing, which is still reported. A heading that differs from the rule is no longer reported; the stage page names it: 「加上 4 课的收尾 30 分钟（第 0.1 课 15 分钟，其余每课 5 分钟）」. Stage 0 is still about 8 hours (426 minutes, 490 with reviews), stage 1 about 34. The gate minutes in these hours are the estimate that `status` and the listing print (gate-b 29); the head of a drawn sitting may differ by a few minutes (item 69), and the generated sentence says so: 「关卡的分钟是工具在开考前估的数；开考时按抽到的题重算，会差几分钟。」 (reworded by the orchestrator on 2026-11-20 after the pass; it said 「关卡的分钟是开考时工具打印的数。」).
72. For command writers: `normalize.OPTION_DOTS`, `normalize.fold_dots(text)`, `normalize.option_text_index(typed, labels)` (used by `context._read_choice` and `commands/review.py`); `doctor.WORKSPACE_REPO_BEFORE`, `doctor.Doctor.reached_workspace_repo_lesson()`; `build_reference.lesson_closing(lesson)`, `LessonInfo.closing`, `check_closing(model, lesson)` now returns the heading's minutes or None; `syllabus.TOOL_NAMES["grep"]`, `["zip"]`.

Cross-check of 2026-11-20 (writer `fix-shared`; two learner-facing strings and one test; nothing a lesson can call changed):

73. **First-aid sentences in tool output** (COMMON section 2: a first-aid sentence has the form “急救：……”): `doctor`'s `code` line now ends 「 → 对导师说“急救：code 命令找不到”」 (was 「 → 导师会带你装好」), the sentence lesson 0.1 teaches; `fresh`'s broken-baseline recovery is 「这不是你的错。把这段发给导师，说“急救：fresh 的基线文件坏了”。」 (was 「…说“fresh 的基线文件坏了”。」). `tools/tests/test_doctor.py` (`test_missing_tools`) and `tools/tests/test_fresh.py` (`test_unreadable_baseline_is_a_checker_problem`) check both. `SimHomeTest.test_refuses_outside_the_temporary_folder` no longer expects `~/sim-should-not-exist` to be refused when `HOME` itself lies in a temporary folder (a G8 simulation home), where it is a legal target.

Closing minutes of 2026-11-20 (writer `closing`, ruling 2 of the orchestrator: every lesson's 「## 收尾（约 N 分钟）」 is calculated by plan G5a like a station, without the 3 minutes for a failed attempt, rounded up to a multiple of 5; the fixed 5 / 10 minutes are withdrawn; `validate` needed no change):

74. **Stage hours sentence** (`tools/dev/build_reference.py`, `hours_sentence`): the fixed rule (5, from 1.12 on 10) is stated only for the lessons whose heading still equals it, and 「其余……」 is left out when there are none. Before, a stage whose every closing differed from the rule still printed 「…，其余每课 5 分钟」, and stage 1 printed 「从第 1.12 课起 10 分钟」 although no such lesson was left. Stage 0 now reads 「加上 4 课的收尾 50 分钟（第 0.1 课 10 分钟、第 0.2 课 15 分钟、第 0.3 课 10 分钟、第 0.4 课 15 分钟）」. `tools/tests/test_build_reference.py` (`test_no_other_lessons_means_no_fixed_rule_in_the_sentence`, `test_the_fixed_rule_is_stated_only_for_the_lessons_that_follow_it`) checks both.
