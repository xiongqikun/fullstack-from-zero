# How to generate the next stage

The procedure of the design's section 5.9 (「后面的阶段怎么来」), written as steps with their inputs. It is used by the tutor when the learner says “准备阶段 2” (the tool's `status` prints 「对导师说「继续下一阶段」」 when everything built so far is done, and a 70% notice before that), and by whoever builds the stage. The quality process is the same as for stages 0-1: [`README.md`](README.md) gives the order, [`definition-of-done.md`](definition-of-done.md) the finish line, [`qa-report-format.md`](qa-report-format.md) the reports.

Who decides what (design 5.9): **the learner** decides the topic, the pace and the electives; **the builder** decides order and teaching method and explains them. Nothing is built before the learner has confirmed the one-page design (step 3).

## 0. When to start

- The tool's 70% notice (「阶段 N 已完成 70% 以上……下一阶段的课程需要提前准备」) or the learner's sentence starts the work. If the next stage's lessons already exist under `stages/`, say so and do nothing else.
- The gate of the current stage is read first (`learner/state.json` → `exams` and `explain`; `python3 tools/course.py status`). A failed must-pass criterion is never built upon: the first lesson of the new stage, or a short remedial lesson before it, works on it (`docs/curriculum-spine.md` section 8.2).

## 1. Collect the inputs

Read these files; do not rely on any conversation's memory. Write down for each input its date, so that the design can say how fresh its evidence is.

The learner's files (`learner/`, `journal/`, `notes/`) steer what the stage stresses, how fast it goes and what it repeats. They are never copied into the course: no lesson, card, design or brief names this learner's projects, words, plans or computer (plan G10a). Examples come from public sources or are plainly invented.

| Input | What to take from it |
|---|---|
| `learner/state.json` | per station: attempts, highest hint level, status (`passed`, `assisted`), confidence; `review` boxes and lapses; `exams` and `explain` per gate; `sessions` (dates and minutes); `decisions` (`workspace_location`, `commit_signing`, `course_product`, …) |
| `learner/log.jsonl` | the event history behind those numbers: how long a station really took, where hints were taken, which review items keep coming back |
| `learner/profile.md` | the eight questionnaire answers plus 「课程产品」, 「每周学习时间」 and 「累了协议」: goal, weekly time and fixed slots, sitting length, English reading, GitHub access, the product the learner wants, strictness |
| `learner/misconceptions.md` | misunderstandings the tutor observed and whether they were resolved |
| `journal/` | the 卡在哪 lines and the optional 哪里看不懂 / 哪里太慢 fields |
| `notes/stage-1-retro.md` | the learner's retrospective of lesson 1.16c, above all the section 「给课程的反馈」 and the planned weekly time |
| `CHANGELOG.md` | errata: where lessons did not match the learner's screen, so which kinds of steps to avoid or re-verify |
| [`docs/curriculum-spine.md`](../curriculum-spine.md) | section 2 (prerequisites between stages), 3 (the product thread), 4 (the stage's thread checklist), 5 (register), 6 (rule ids and the naming scheme for new ones), 7 (what a later stage must decide explicitly: supports withdrawn, practice volume, exercise kinds, steps nobody can execute), 8.2 (the questions the stage review must answer from the learner model), 9 (the skill map) |
| `stages/<NN-stage>/README.md` | the planned goals, product, norms and lesson list of the stage; it is a plan, re-ordered from the evidence |
| `ROADMAP.md`, `docs/roadmap/` | where the stage sits, the electives, the skill map, the sources |
| `STANDARDS.md`, `handbook/` | the rule cards already in force; new cards must not contradict them, and their 复核周期 tell which are due |
| `docs/research/` (sanitised copies) or the build copies `<research>/<topic>/brief.md` | the facts the stage builds on; **every brief is dated 2026-11-19**, so step 2 re-verifies what ages fast |
| `docs/adr/` | decisions already taken (staged delivery, Python first, stage order, code outside synced folders, …); a design that departs from one writes a new ADR |

## 2. Re-verify what ages fast

Every fact the new stage uses is verified on the learner's machine (in a simulation home that mirrors it) or in a primary source opened that day (plan G4). The research of 2026-11-19 recorded how fast these things change; re-check them first, in this order:

1. **Installed tool versions and the baseline.** `python3 tools/course.py fresh` compares the machine with `tools/courselib/baseline.json` and lists the affected lessons. VS Code ships a stable release every week (since 1.111, 2026-03-09); uv, Ruff, Node.js, npm and Homebrew changed major or minor lines in the months before 2026-11; Git releases every 10 to 13 weeks; `gh` and Claude Code change their output and defaults between releases. Update the baseline through the tool's owner, not by hand.
2. **Defaults that changed recently** and that a stage 2-3 lesson would quote: Ruff's default rule set (0.16.0), the layout `uv init` creates (0.12.0), the Python version uv downloads by default (0.13.0), npm's newest major, mypy's parser. These are the exact cases where the model's own memory is behind (the `currency-mechanisms` brief, section 1).
3. **Support and end-of-life dates.** Python (devguide.python.org/versions), Node.js (github.com/nodejs/release), macOS (Apple's version list). A tutorial that installs an end-of-life version is wrong.
4. **Platform UI and policy.** GitHub settings pages, two-factor rules, Pages, push protection; the Claude desktop app and Claude Code permission modes (lesson 1.15). These change without a version number: re-read the official page and keep the G6 marks.
5. **Rule cards due for review.** Every card whose 核对日期 plus 复核周期 has passed (6 months for law and platform policy, 12 for conventions of tools and platforms, 24 for stable community norms, per the header of `STANDARDS.md`), and every card the new stage cites.
6. **The research briefs themselves.** A brief older than its topic's cycle is refreshed before use: re-run the research for the topics the stage needs (the topics are listed in plan G13) and keep the new brief's date. Sanitise the copy that goes into `docs/research/` (no user name, e-mail address or computer name).

Record each re-verified fact with its source and date; it goes into the design (step 3) and later into the lessons' `verified` metadata.

## 3. Stage review and a one-page design

Write `docs/design/<YYYY-MM-DD>-stage-<N>-design.md`. Its **evidence from the learner model** (the answers to every question of `docs/curriculum-spine.md` section 8.2, with numbers from step 1, and the decision each answer led to) goes into `learner/stage-<N>-evidence.md`, never into the design file (plan G10a); the design file says in general words which decisions rest on that evidence. If the files are thin (few sessions, no ratings), say so and design conservatively; do not invent a learner.

The page itself, in plain Chinese for the learner (plan G2), on one screen:

- the stage goal and the product increment, written for the default product (the exchange-rate dashboard); a topic the learner chose is shown to them and recorded in their evidence file;
- the lesson list in order, two or three stations each, with the estimated hours derived by plan G5a (station minutes plus gate minutes plus 15% for reviews), and the batches (step 6);
- what changes in the way of learning (the supports withdrawn as the learner grows; spine section 7);
- the new rule ids and their families (spine section 6.2), and the electives offered;
- the questions put to the learner: topic, weekly pace, electives (their answers go into the evidence file, not into the design file).

The tutor shows the page and asks the learner to confirm or change it. Record the date and the answers at the top of that evidence file; the design file notes only that the design was confirmed and on which date. Only then build.

## 4. Plan the build

- Extend the plan: a stage plan in `docs/plans/` with the syllabus rows (ids, folders, stations with one concept each, new rules, gates) in the form of plan section 4, and any new global constraint. Plan section 1 stays binding.
- Extend `tools/courselib/syllabus.py` (ids, folders, stations, rule ids, gates) together with the plan; the tool's owner adds whatever the stage needs from the tool (new check kinds, ladder states, exam support) and documents it in [`tool-api.md`](tool-api.md).
- Write the per-lesson briefs into a `lessons.json` in the form of [`build-kit/lessons.json`](build-kit/lessons.json): `id`, `stage_dir`, `folder`, `title`, `briefs` (research topics), `notes` (what the lesson must and must not do, its start state, its traps).

## 5. Build, test, fix, accept

1. **Build** each lesson with [`build-kit/build-lessons.js`](build-kit/build-lessons.js): one builder per lesson writes `lesson.md`, `lesson.py`, `rules.md` from [`lesson-template.md`](lesson-template.md), executes every command in a simulation home, and reports per [`qa-report-format.md`](qa-report-format.md).
2. **Blind test** in the same run: a different agent with only the lesson folder and the tool follows the text literally and injects the novice errors; a fixer applies the findings; a second test confirms where there were blockers.
3. **Seams.** After all lessons of a batch exist, audit them in order (terms and commands, tutor sentences, rule cards, recurring forms, the state they hand to each other) and repair with [`build-kit/fix-lessons-round.js`](build-kit/fix-lessons-round.js), whose briefing folder holds one `COMMON.md` of binding decisions (the one of stages 0-1 is kept as [`build-kit/COMMON.md`](build-kit/COMMON.md)) and one file per lesson.
4. **Shared files** with [`build-kit/build-shared-docs.js`](build-kit/build-shared-docs.js): regenerate `handbook/` and `GLOSSARY.md` with `tools/dev/build_reference.py`; update `STANDARDS.md`, the cheat sheets, the gates' `rubric.md` and `examiner-prompt.md`, `templates/`, the tutor rules (`CLAUDE.md` and `docs/tutor/playbook.md`) for every new sentence the learner is told to say, the stage page and `ROADMAP.md`.
5. **Accept** with [`build-kit/acceptance.js`](build-kit/acceptance.js): a play-through in order in one simulation home, fixes, confirmation, and the mechanical checklist of [`definition-of-done.md`](definition-of-done.md) section 2.

## 6. Deliver in small batches

- Four or five lessons per batch (design 5.9). The learner does the first lesson of a batch before the rest of it is finished, and the tutor collects what was unclear or slow (the two journal fields) before the next lessons are fixed.
- What the tutor tells the learner about the build effort (playbook §14 step 5): the design conversation (step 2 of the order of work) is one conversation of about 30-60 minutes of the learner's attention. How many further conversations a batch takes, and how long each is, was not measured when stages 0-1 were built (they were built in one long session before the learner started): the number of conversations is **not measured yet**. After each batch, write the measured number and length of the conversations here, so that the next estimate rests on it.
- Each batch is delivered only when its lessons meet [`definition-of-done.md`](definition-of-done.md) section 1; the stage is finished when section 2 holds.
- Commits in the learning repository are the learner's: builders commit nothing there (plan G9). The learner's 1.12 backup routine carries the new files to the private remote.

## 7. Record

- `CHANGELOG.md`: one entry per batch: lessons added, what changed in earlier lessons and shared files, which facts were re-verified (step 2) with their dates.
- `ROADMAP.md` and the stage page: the hours recomputed from the lessons' minutes (plan G5a).
- `docs/curriculum-spine.md`: the stage's thread checklist marked, new register entries, new rule ids.
- The design file: what was built differently from the confirmed page, and why.
