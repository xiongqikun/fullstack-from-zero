# Definition of done

A lesson or a stage is done when every item below is checked and the evidence is in the builder's or tester's report ([`qa-report-format.md`](qa-report-format.md)). Each item says how to verify it. Most are a command; the few that need a person or an agent say so and name the report field that carries the evidence. The forms the commands look for are those of [`lesson-template.md`](lesson-template.md).

Run everything from the workspace root of a **simulation home** (plan G8, [`tool-api.md`](tool-api.md) section 17.1), never in the learner's real home, with `export PYTHONDONTWRITEBYTECODE=1`. Set two variables first:

```zsh
L=stages/02-programming/01-first-program   # the lesson folder
ID=2.1                                      # the lesson id
```

A command that should print nothing is marked "→ empty". The grep commands find the forms; a hit is a finding to fix, not a verdict on its own (read the line).

## 1. Per lesson

### 1.1 Files and module

- [ ] `lesson.md`, `lesson.py` and `rules.md` exist (a lesson without new rules still has `rules.md`, saying so). `ls $L`
- [ ] `validate` has no error, on Python 3.14 and 3.9, and also with `--build` (every scenario and both forms of every exam task build):
  `python3 tools/course.py validate $ID && python3 tools/course.py validate --build $ID && /Library/Developer/CommandLineTools/usr/bin/python3 tools/course.py validate --build $ID`
- [ ] No `[G5]` warning (a station heading's minutes differ from META) and no `[I3]` warning (an option whose whole text is `q` or `s`): `python3 tools/course.py validate $ID | grep -E '\[G5\]|\[I3\]'` → empty. A warning for minutes above 30 is acceptable only with the G5a calculation in the report (`minutes_calculation`).
- [ ] No term and no new command claimed by an earlier lesson (plan section 5a; the owner rule in [`lesson-template.md`](lesson-template.md) note 5). Run the script in section 3 of this file → empty.
- [ ] No debris: `find $L -name __pycache__ -o -name '*.pyc' -o -name .DS_Store` → empty.

### 1.2 Text: the recurring parts

- [ ] Header: `grep -c -E '^> \*\*用时\*\* [0-9] 站，约 [0-9]+ 分钟' $L/lesson.md` prints 1, and the X equals the sum of the station minutes plus the 收尾.
- [ ] Every station heading has its minutes: `grep -c -E '^## 第 [0-9]+ 站：.*（约 [0-9]+ 分钟）$' $L/lesson.md` equals the number of stations in META.
- [ ] Save points in the canonical form:
  `grep -n '^> \*\*存档点' $L/lesson.md | grep -v -E '：到这里可以安全停下。下次可以对导师说“从 ([0-9]+\.[0-9]+[a-c] 继续|[0-9]+\.[0-9]+ 的收尾继续)”。$'` → empty; a gate inside the lesson has one line starting `> **中途存档点**：` and ending `下次可以对导师说“做小关卡 <gate>”。`
- [ ] Hint and check lines, one pair per station: both counts equal the number of stations.

  ```zsh
  grep -c -E '^- 提示：`python3 tools/course.py hint [0-9.]+[a-c]`（每运行一次多给一级）$' $L/lesson.md
  grep -c -E '^- 检查（先回到学习工作区）：`python3 tools/course.py check [0-9.]+[a-c]`$' $L/lesson.md
  ```
- [ ] 收尾: `grep -c -E '^## 收尾（约 [0-9]+ 分钟）$' $L/lesson.md` prints 1; its first three items are the canonical ones (and item 4, the backup, from lesson 1.12 on); its last line matches
  `grep -c -E '^都做完，这一课就完成了。(下次可以对导师说“从 [0-9]+\.[0-9]+ 开始”。|下一步是小关卡 gate-[0-9a-z]+：.*下次可以对导师说“做小关卡 gate-[0-9a-z]+”。)$' $L/lesson.md` → 1.
- [ ] Rule summary (when the lesson has rules): both counts are 1.

  ```zsh
  grep -c '^| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |$' $L/lesson.md
  grep -c '^完整卡片在本课文件夹的 `rules.md`。$' $L/lesson.md
  ```
- [ ] No rival wording: `grep -n -E '选做|可选|选读|可以跳过|课程文件夹|练习文件夹|从本课行规继续|从收尾继续|做 [0-9.]+ 的收尾' $L/lesson.md $L/lesson.py` → empty; `grep -n 'Desktop/Code/fullstack-from-zero' $L/*` → empty (only lesson 0.2 may name it); `grep -n '/Engineering' $L/*` → empty (the course folder's name before 2026-11-21; `validate` reports it too).
- [ ] Sentences for the tutor are the fixed ones, with full-width quotes: `grep -n -E '说"|说「' $L/lesson.md` → empty; every “……” the learner is told to say is in the table of `CLAUDE.md` section 3, or is a “急救：……” sentence reported under `open_issues` as "tutor contract needs:" (person check of the hits of `grep -n -o '说“[^”]*”' $L/lesson.md`).
- [ ] Optional boxes in the one form: `grep -n '想多了解' $L/lesson.md` shows only `> **想多了解（可跳过）：` lines and the heading `## 想多了解`.
- [ ] Terminal commands in `zsh` fences, output in `text` fences: `` grep -c '^```bash' $L/lesson.md `` → 0.

### 1.3 Text: truth, freshness, privacy, voice

- [ ] Every command of 「跟我做」 was executed verbatim in a simulation home and its real output pasted (evidence: `commands_executed` in the builder's report; the blind tester re-runs them).
- [ ] G6 marks: if `grep -c -E '〔对照文档，界面可能不同〕|〔建课时无法验证〕' $L/lesson.md` is above 0, then `grep -c '^和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。$' $L/lesson.md` is exactly 1, the line comes directly after the first mark, `` grep -n '`〔' $L/lesson.md `` → empty, and every marked step is in `META["unverified_steps"]`.
- [ ] Every 旧教程提醒 says since when: `grep -h '旧教程提醒' $L/lesson.md $L/rules.md | grep -v -E '[0-9]{4}|[0-9]+\.[0-9]+'` → empty.
- [ ] Every rule card source opened today (evidence: `sources_checked`; the tester's `sources`). Every 约束力 carries a scope: `grep -n '^- \*\*约束力\*\*' $L/rules.md | grep -v '适用范围'` → empty.
- [ ] Privacy (plan G10): `grep -n -E "/Users/[^你<]|/private/|/tmp/|learner@example\.com|\bLearner\b|FAKEKEY|$(id -un)" $L/*` → empty (the fake identity of the simulation must never leak); output paths show `~`.
- [ ] Publishable (plan G10a), person check: the lesson states no fact about one particular learner or their computer (their projects, words, plans, time zone, installed software, settings); what depends on the reader's machine is said conditionally; every case is public (address and date checked) or plainly invented. The automated part is the stage-level `export_public.py --check` (section 2).
- [ ] Voice (plan G2): `grep -n -E '很简单|显然|只需要|！' $L/lesson.md` → empty; no emoji outside pasted tool output.
- [ ] Every step the learner cannot do without an account or a GUI is marked and kept few (plan section 6, point 3).

### 1.4 Behaviour

- [ ] Every check passes on correct work and fails helpfully (看了哪里、看到了什么、还缺什么, no answer given) on at least three plausible wrong attempts (builder: `commands_executed`; tester: `tool_results`, at least four attempts of their own).
- [ ] A check never cries wolf: no false 还没达标 on any correct variant the tester tried; a broken environment gives 检查器出问题, exit 2, no traceback.
- [ ] Hints: four levels per station; level 1 points without telling; level 4 is a correct answer with its explanation (tester: `tool_results`).
- [ ] Scenarios: `start` exists and builds the state the lesson assumes; every scenario prints where it is (`validate --build`).
- [ ] Review items honest in tier (only what a professional does without thinking is `fluent`), answerable, none whose option is a review command.
- [ ] The independent blind test (a different agent, given only the lesson folder and the tool) ends with no blocker and no major left (`verdict` of the last test report is `pass` or `pass-with-issues` with only minors).
- [ ] The novice-error list was injected (full-width punctuation or space, wrong folder, unsaved file, pasted prompt or `$`, unclosed quote, stuck in vi or less, empty Enter, a name with a space; Git: committing with nothing staged, the signing failure of plan G7) and each is rescued by the text or the checker (tester: `novice_errors`).
- [ ] `end_state` in the report says exactly what exists on the learner's machine afterwards, and the next lesson's `start` scenario builds that state.

## 2. Per stage

- [ ] Every lesson of the stage's syllabus exists and is done (section 1): `python3 tools/course.py validate --complete` has no error.
- [ ] The stage design was confirmed by the learner before the build (the design file under `docs/design/` carries the date of the confirmation; what the learner decided, such as topic, pace and electives, is in `learner/stage-<N>-evidence.md`, plan G10a).
- [ ] Gates: for every gate of the stage, `gates/<gate>/rubric.md` and `gates/<gate>/examiner-prompt.md` exist (`ls gates/<gate>`); the rubric has 8-12 observable criteria, 3-4 of them must-pass, two explain-back questions and one debugging task (plan I7); one attempt holds one task for each lesson the gate covers, and the pool has a second form of every task (`validate --complete`; `exam <gate>` in a simulation home prints the number of tasks and the minutes).
- [ ] The seams were audited after the lessons existed: terms and commands (one owner each), tutor sentences against `CLAUDE.md` and `docs/tutor/playbook.md`, rule cards against `STANDARDS.md`, recurring forms against [`lesson-template.md`](lesson-template.md), the state the lessons hand to each other.
- [ ] Generated references are current: `python3 tools/dev/build_reference.py --check` exits 0 (it regenerates `handbook/` and `GLOSSARY.md` from the `rules.md` cards and `TERMS`).
- [ ] Cheat sheets cover the stage: every `new_commands` entry of the stage appears in one of `cheatsheets/*.md` (script in section 3, `--cheatsheets`), each sheet still fits one screen, and its 旧教程提醒 boxes carry a since-when.
- [ ] Hours: the stage page and `ROADMAP.md` state the hours derived by plan G5a (station minutes plus gate minutes plus 15% for reviews), not a target.
- [ ] The tool's tests pass on both Pythons: `python3 -m unittest discover -s tools/tests` and the same with `/Library/Developer/CommandLineTools/usr/bin/python3`.
- [ ] End-to-end acceptance (plan T4; `build-kit/acceptance.js`): the stage was played through in order in one simulation home with novice-error injection; the verdict is `accepted` or `accepted-with-known-issues`, and the known issues are written for the learner in plain words.
- [ ] `CHANGELOG.md` has an entry for the stage (what was added, what changed in earlier stages, which facts were re-verified).
- [ ] Privacy sweep over everything written for the stage (the grep of section 1.3, over the whole workspace except `learner/`, `journal/`, `notes/` and `docs/research/local-only/`) → empty.
- [ ] Publishable (plan G10a): `python3 tools/dev/export_public.py --check` exits 0. It leaves out `learner/`, `journal/`, `notes/` and `docs/research/local-only/`, and also looks for the private terms listed in `docs/research/local-only/public-denylist.txt`.
- [ ] No debris in the workspace: `find . -name __pycache__ -o -name '*.pyc' -o -name .DS_Store` → empty.

## 3. Script: owners and cheat-sheet coverage

Save it in your scratch folder (not in the workspace) and run it from the workspace root with `python3 -I <script>`; add `--cheatsheets` for the coverage check. It reads the modules with `ast` and runs no lesson code.

```python
import ast, collections, glob, sys

def lit(path, name):
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == name:
            return ast.literal_eval(node.value)

def order(path):
    stage, n = lit(path, "META")["id"].split(".")
    return int(stage), int(n)

terms, commands = collections.defaultdict(list), collections.defaultdict(list)
for path in sorted(glob.glob("stages/*/*/lesson.py"), key=order):
    for term in lit(path, "TERMS") or []:
        terms[term["term"]].append(term["first"])
    for station in lit(path, "META")["stations"]:
        for command in station["new_commands"]:
            commands[command].append(station["id"])

for kind, table in (("term", terms), ("command", commands)):
    for key, owners in table.items():
        if len(owners) > 1:
            print(f"{kind} claimed twice: {key}: {', '.join(owners)}")

if "--cheatsheets" in sys.argv:
    # a command counts as covered when each of its words (placeholders and
    # gate names left out) appears somewhere in the cheat sheets
    sheets = "".join(open(p, encoding="utf-8").read() for p in glob.glob("cheatsheets/*.md"))
    for command, owners in commands.items():
        words = [w for w in command.split()
                 if not w.startswith("<") and w != "…" and not w.startswith("gate-")]
        if not all(w in sheets for w in words):
            print(f"not in any cheat sheet: {command} ({owners[0]})")
```

On 2026-11-19 the first part printed exactly the eight duplicates that the repair round of stages 0-1 decided (路径, 递归, 提交签名, 分支, 令牌; `scenario`, `git --version`, `git commit -m … -m …`), so it finds what it should; with `--cheatsheets` it printed nothing for the five sheets of stages 0-1.
