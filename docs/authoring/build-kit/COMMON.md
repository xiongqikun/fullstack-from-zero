# Repair round: binding decisions (orchestrator, 2026-11-19)

> **What this file is.** The orchestrator's binding decisions of 2026-11-19 for the repair round of stages 0-1: the `COMMON.md` that [`fix-lessons-round.js`](fix-lessons-round.js) put into the briefing folder of every lesson fixer (section 9 was kept up to date with the tool changes of 2026-11-20 while the round ran). It is kept here as the record that [`../lesson-template.md`](../lesson-template.md), [`../tool-api.md`](../tool-api.md) and the comments in `tools/` cite as "COMMON section N" or "COMMON §N".
>
> **Where its content lives now.** The forms of a lesson (sections 1, 3, 5, 7) are folded into [`../lesson-template.md`](../lesson-template.md) and [`../definition-of-done.md`](../definition-of-done.md); the tool changes (section 9) into [`../tool-api.md`](../tool-api.md) sections 19 and 19.1 and into the validator; the sentences for talking to the tutor (section 2) into `CLAUDE.md` and `docs/tutor/playbook.md`; the facts of section 6 into the plan (G7, G11a) and the lessons. For new work, read those files; this one records why they say what they say.
>
> **What was changed in this copy** (copied into the workspace on 2026-11-20): the sentence of section 1 about a fixed 5 or 10 minutes for the 收尾 is marked as withdrawn, and the section [Rulings of 2026-11-20](#rulings-of-2026-11-20) is added at the end, and the example link `[LICENSE](LICENSE)` in section 6 is set as code. Everything else is the text as the fixers read it. Any path in it that points outside the workspace means the build folder of that run (`<build folder>/…`), which is not kept: such paths are historical.

These decisions were taken after reading the 20 blind-test reports and the audit of the seams between the lessons. They bind the lesson fixers, the testers and the writers of the shared files. Where they differ from older wording of the plan, they win; the plan itself was updated where a rule is named (G5a, G7, G11a).

Why this round exists: the 20 lessons were written at the same time by writers who could not see each other. Each lesson alone is close to done; what is still wrong is (a) times that were labelled 25 minutes and are really 30 to 45, (b) checks that fail correct work or say something untrue, (c) sentences, file names and terms that differ from lesson to lesson, (d) a few facts and labels. The course is for a true beginner and promises to say, for every practice, how binding it is, who says so, and that it is current.

## 1. Time: plan G5a

- Station minutes are calculated, never fitted to a target. Allowed: 15 to 40. Target: 20 to 25. Above 30 the validator warns ([G5]); above 40 it refuses.
- The calculation: prose outside code blocks and outside 「想多了解」 boxes at 180 Chinese characters per minute; each line of output the learner must read at 10 seconds (at most 2 minutes per block); each command the learner types at 40 seconds, or 70 seconds when it is longer than 40 characters or contains quotes or a pipe; Chinese text the learner composes (notes, README text, answers) at 15 characters per minute; each GUI action sequence (open an app, a menu path, a browser round trip) at 1 minute, first-time flows (sign-up, install, a settings page) estimated one by one; each check run at 1 minute plus 45 seconds per question it asks; each exchange with the tutor at 2 minutes; plus 3 minutes per station for one failed attempt. Add up, round up to the next multiple of 5.
- Trim before you label: one new concept per station; a second concept becomes a one-clause gloss, moves into a box headed 「想多了解（可跳过）」, or goes to the lesson that owns it. Boxes of this kind sit at the end of the station or in the lesson's closing section 「想多了解」, and are not counted.
- The lesson header gives the sum: 「**用时** N 站，约 X 分钟」, where X is the sum of the stations plus the 收尾. ~~(5 minutes; from lesson 1.12 on 10 minutes, because of the backup step).~~ **Withdrawn on 2026-11-20:** the minutes of the 收尾 are calculated, not fixed; see ruling 2 in the section [Rulings of 2026-11-20](#rulings-of-2026-11-20). Every station heading gives its own minutes: 「## 第 2 站：……（约 30 分钟）」.
- Gates: gate-0 stays inside station 0.4c as the plan row says, but as its own sitting behind a save point, with its own stated time; gate-a is taken after lesson 1.5 and gate-b after lesson 1.10, each announced by the tool after the whole-lesson check; gate-1 is the subject of station 1.16b, whose minutes cover the debugging task and the explain-back answers while the exam tasks are stated separately. A gate's stated time is the sum of the `minutes` of the tasks of one attempt plus 10 minutes for the explain-back part (two explain-back questions and, at gate-0, gate-a and gate-b, one debugging question, then the verdict and the command that records it: four exchanges with the tutor under G5a). The tool prints 「讲解题另需约 10 分钟」; no lesson and no sentence of the tool says how many questions there are. One attempt holds one task for each lesson the gate covers (gate-0: four tasks; gate-a and gate-b: five; gate-1: six, one for each of the lessons 1.11 to 1.16, whose tasks also use the skills of the earlier lessons). A gate is passed when every lesson it covers has a passed task and the explain-back questions are recorded as passed; a task that was not passed comes back in the next sitting in its other form, and only such tasks come back. The tool says so in its own words; a lesson that describes a gate does not promise anything else (for example that all tasks of a pool must be passed, or a number of tasks that the tool does not give).

## 2. Sentences for talking to the tutor (fixed)

Chinese quotation marks in learner-facing text are the full-width pair “ ” (plan G2); inside the code of lesson.py use whatever the file already uses, but the text the learner sees shows “ ”.

| situation | the learner says exactly | who introduces it |
|---|---|---|
| start, or continue wherever the course stands | “开始上课” | README, lesson 0.1 |
| continue at a station | “从 1.6b 继续” | the tool prints it after each station that is not the last |
| continue at the closing steps of a lesson | “从 1.6 的收尾继续” | the tool prints it after the last station |
| start the next lesson | “从 1.7 开始” | the tool prints it after the whole-lesson check |
| take a gate | “做小关卡 gate-a” | the tool prints it when a gate is due |
| explain-back questions of a gate | “请问我 gate-0 的讲解题” | lesson 0.4 first; the tool prints it when the practical tasks of a gate are passed |
| something is broken | “急救：<一句话说现象>” | lesson 0.1 (one line) |
| this is not an exercise, just do it | “干活：<要做的事>” | lesson 0.1 (one line); first used in lesson 1.15 |
| back to the lesson | “回到上课” | lesson 1.15, where it is first needed |
| the text and the screen differ | “课文对不上” (then paste what the screen shows) | the G6 line of every lesson |
| first questionnaire | “我们来做入学问卷” | lesson 0.1 |
| move the course folder | “帮我把课程安置到 ~/Developer” | lesson 0.2 |
| keep the folder where it is, but make the usual path work | “我先不搬，帮我在 ~/Developer 建一个入口” | lesson 0.2 |
| back after a long break | “我回来了，带我走回归流程” | the status command prints it |
| explain a command without running it | “请解释这条命令的每一部分，先不要运行” | lesson 1.1 (rule TERM-01) |
| prepare the next stage | “准备阶段 2” | lesson 1.16 |

Rules: a lesson never invents another sentence for one of these situations (no “从本课行规继续”, “从收尾继续”, “做 0.3 的收尾”, “从 0.4c 的小关卡继续”, “回到上课，我来验收 1.15a”: say “回到上课” and then what you want). 「讲给导师听」 is the plan's name for the activity of explaining something back to the tutor and may be used as such; the sentence that starts it at a gate is the one in the table. Lesson 0.1 introduces the three modes in ONE line (the tutor is a coach in lessons; “急救：……” when something is broken; “干活：……” for work that is not an exercise, used from lesson 1.15 on), not as a concept of its own. A lesson may define a situation-specific first-aid sentence in the form “急救：……” (for example “急救：学习工作区里多了 .git”, which doctor prints; a first-aid sentence that means the course folder says 学习工作区, never a bare 工作区); every such sentence is listed in open_issues with the prefix "tutor contract needs:" and what the tutor must do. The first line of every reply of the tutor is the status line 「【教练模式】……」; the three modes are 上课, 干活, 急救.

The explain-back questions (讲解题) belong to every gate: the questions of `gates/<gate>/rubric.md` (two explain-back questions; at gate-0, gate-a and gate-b also one debugging question; about 10 minutes), asked by the tutor in the usual conversation (for gate-1 the learner may instead use an independent examiner: a new conversation that is not opened on the course folder, with `gates/gate-1/examiner-prompt.md`). The verdict is recorded with a command of the tool that the learner runs when the tutor or the examiner has given it: `python3 tools/course.py exam gate-0 --explain pass`, or `--explain again` when it has to be repeated. A gate is passed when its practical tasks are passed and its explain-back is recorded as pass. A gate never blocks the next lesson: the tool keeps showing what is still open.

First-aid cases the tutor's playbook already covers (section 5 of `docs/tutor/playbook.md`; a lesson uses exactly these sentences and points to no other procedure): read that section before you word a first-aid sentence in your lesson, and report a case your lesson needs and the playbook lacks under open_issues with the prefix "tutor contract needs:".

The tutor may not: commit or push for the learner unless asked in that conversation; change global configuration (the learner types such commands); do an exercise for the learner in the learner's real folders. One exception is written into the tutor rules for lesson 1.15: on the learner's request in station 1.15a the tutor edits `~/Developer/my-site` and leaves the change uncommitted for the learner to review.

## 3. Recurring parts of a lesson: one wording

Table A of section 11 (from the audit) is binding with the exceptions stated here; where the two differ, this section wins.

- Save point after a station that is not the last: 「> **存档点 1.6a**：到这里可以安全停下。下次可以对导师说“从 1.6b 继续”。」 After the last station: 「> **存档点 1.6c**：到这里可以安全停下。下次可以对导师说“从 1.6 的收尾继续”。」 Before a gate that sits inside a lesson (0.4c, 1.16b): 「> **中途存档点**：<做完了什么>，到这里可以安全停下。下次可以对导师说“做小关卡 gate-0”。」 Nothing else is added to these lines.
- The last lines of every 「自己做」, in this order: 「- 提示：`python3 tools/course.py hint 1.6a`（每运行一次多给一级）」 and 「- 检查（先回到学习工作区）：`python3 tools/course.py check 1.6a`」.
- The closing section 「## 收尾（约 N 分钟）」, in this order:
  1. 「全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.6`」
  2. 「行规笔记：运行 `code notes/my-rules.md`，在小标题「GIT-01 ……」「GIT-02 ……」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。」 (name each rule id of the lesson with its title exactly as in rules.md; a lesson without a new rule drops this step)
  3. 「一句话日志：`python3 tools/course.py journal`」
  4. from lesson 1.12 on: 「备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。」 (lesson 1.12 defines the group of commands; the later lessons do not repeat them)
  Then the last line: 「都做完，这一课就完成了。下次可以对导师说“从 1.7 开始”。」; where a gate comes next (after 1.5 and 1.10): 「都做完，这一课就完成了。下一步是小关卡 gate-a：它是单独的一段时间，开考时工具会打印题数和预计用时。下次可以对导师说“做小关卡 gate-a”。」 A lesson may add its own closing steps before that last line, numbered on.
- Returning to the course folder before a command of the course tool: 「回到学习工作区：`cd ~/Developer/Engineering`」. This one path works for every learner (section 6: the entrance). No lesson tells the learner to replace it by another path, and no lesson other than 0.2 writes `~/Desktop/Code/Engineering`. The proposal A11 of the audit, and every finding that asks for a note of the kind 「没搬的换成 cd ~/Desktop/Code/Engineering」, is superseded by this decision: do not add such notes, remove the ones that exist (lesson 0.4 has one), and report those findings as rejected with the words "superseded by the entrance decision".
- Names: 学习工作区 is the course folder (never 课程文件夹, 练习文件夹, or a bare 工作区, which from lesson 1.6 on is Git's word for the files you can see and edit in a repository; lesson 1.6 states the difference once); 学习仓库 is the course folder once it is a repository (from 1.12 on); 练习场 is `~/Developer/playground/` and 练习场景 one scenario folder in it; 你的网站 is `~/Developer/my-site`. Gates are 「小关卡 gate-0 / gate-a / gate-b」 and 「阶段验收 gate-1」; the sentence is always “做小关卡 <gate>”.
- Keys: lesson 0.1 introduces 「Cmd+S（键帽上印着 ⌘ command；课文以后写 ⌘S）」. After that the symbols are used as the menus show them: ⌘S, ⌘Z, ⌘A, ⌘C, ⌘V, ⇧⌘P and so on, each explained at its first use. Ctrl+C, Tab, Esc, 回车（Enter） and 空格 are written as words.
- Optional material: 「> **想多了解（可跳过）：<小标题>**」 inside a station, or the closing section 「## 想多了解」 whose first line says that everything in it can be skipped. Not 选做, 可选, 选读 or 可以跳过.
- The rule summary in lesson.md: a table 「| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |」 followed by 「完整卡片在本课文件夹的 `rules.md`。」 The cells for 约束力 and 规则类型 are copied from the card.
- Code fences: commands the learner types in the terminal are in a block that opens with ```zsh (the learner's shell is zsh, and lesson 1.5 teaches this label); what the screen shows is in a block that opens with ```text; file contents use the label of their kind (```html, ```css, ```markdown, ```python, ```gitignore, ```ini). No ```bash and no unlabelled block.
- What the learner sees in pasted output: the home folder is `~`; the prompt is `你的用户名@你的电脑名 文件夹 %`; a name is 「你的名字」; an e-mail address is `you@example.com`; output that differs on the learner's machine (dates, hashes, sizes, the number of commits) is marked 「你的会不一样」.
- The G6 line, exactly once per lesson that has a marked step, directly after the first marked step, not inside a blockquote: 「和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。」 The marks are written 〔对照文档，界面可能不同〕 and 〔建课时无法验证〕, never inside backticks; META["unverified_steps"] lists the same steps.
- Every 「旧教程提醒」 says since when (a version or a year).

## 4. Shared files (refer to them by exactly these paths)

Written today and present in the workspace: `README.md`, `CLAUDE.md` with `docs/tutor/playbook.md` (the tutor's rules and the step-by-step procedures for every fixed sentence and every first-aid case), `CHANGELOG.md`, `templates/`, `gates/<gate>/rubric.md` and `examiner-prompt.md`, `cheatsheets/`. Read the one your lesson refers to and make the lesson agree with it; where the shared file is wrong, say so in open_issues ("shared file needs:") instead of bending the lesson. Being generated while the lessons are repaired, so possibly absent or incomplete when you look: `handbook/`, `GLOSSARY.md`, `notes/my-rules.md` and the tables inside `STANDARDS.md` and the stage pages.


- `notes/my-rules.md` exists from the first day (it is created with the course, then it is the learner's and is never overwritten). Format: a title and three lines of instruction; then for each lesson a heading 「## 0.1 第一次动手」 and under it one heading per rule of that lesson, exactly as the card's heading in rules.md: 「### META-01 遇到报错先问三件事」, followed by an empty line where the learner writes. Consequences: lesson 0.1 opens this file, it does not create it; every closing section uses step 2 of section 3; a check that reads this file (lesson 1.16) counts as the learner's words only the non-empty lines BELOW a rule's heading up to the next heading, never the heading's own title, and a line the learner wrote elsewhere that starts with the rule id still counts.
- `learner/profile.md` is written by the tutor during lesson 0.1 from `templates/profile-template.md`, which holds exactly these eight headings and nothing else: 「## 学习目的」「## 每周时间与固定时段」「## 一次能坐多久」「## 英文阅读」「## GitHub」「## 想做的作品」「## 导师严格度」「## 以前用过终端吗」. Each answer goes on the lines below its heading. Lesson 0.3 has the learner add the line 「课程产品：……」; lesson 0.4 has the learner add the sections 「## 每周学习时间」 and 「## 累了协议」. Checks that read the profile accept a heading with a number or bold marks in front and name the exact heading they miss.
- `templates/`: `profile-template.md`, `weekly-review.md` (three questions: 这周做了什么 / 卡在哪 / 下周改一件什么), `ask-for-help.md` (the skeleton of lesson 1.14), `ai-change-checklist.md` (the five questions of lesson 1.15, same words, same order), `retro.md` (the six headings of lesson 1.16), `readme-template.md` (the five questions of lesson 1.5, each followed by a line in the form （在这里写……）).
- `gates/gate-0/`, `gates/gate-a/`, `gates/gate-b/`, `gates/gate-1/`: each with `rubric.md` and `examiner-prompt.md`.
- `handbook/` (all rule cards by family; `handbook/README.md` is the index of every rule id with its lesson), `GLOSSARY.md`, `cheatsheets/terminal.md`, `cheatsheets/git.md`, `cheatsheets/markdown.md`, `cheatsheets/vscode.md`, `cheatsheets/github.md`, `README.md` (with the card 「搬家后怎么找回导师」), `CLAUDE.md` (the tutor's rules; in learner-facing text call it 导师规则（`CLAUDE.md`）), `CHANGELOG.md`.
- A lesson that needs more from one of these files than this section says reports it in open_issues with the prefix "shared file needs:".

## 5. Who owns a term or a command

The lesson where the learner first needs a word owns it (it is in TERMS with `first` there and gets its definition there); a later lesson may repeat a one-clause gloss but does not list it as first. Decided collisions: 路径 belongs to 0.2 (0.1 glosses it in a clause); the command `python3 tools/course.py scenario` is new in 0.1 only; 递归 belongs to 1.2; 令牌 to 1.9; 提交签名 to 1.6; 分支 to 1.6 (a one-sentence gloss; the topic is stage 2); `git --version` to 1.6; `git commit -m … -m …` to 1.10. Further owners follow in section 10 (the ledger of the audit); where section 10 and this list differ, this list wins.

## 6. Facts fixed today

- The global Git settings the course prepares for (plan G7): `commit.gpgsign=true`, `gpg.format=openpgp`, `gpg.program=gpg`, `tag.forceSignAnnotated=false`, and the two keys `gpg.ssh.program` and `gpg.ssh.allowedSignersFile` present with empty values; no gpg installed. The simulation home now reproduces this. A lesson states them as a case the learner may meet, not as checked facts of the learner's own computer.
- The state ladder: state S6 records the subject `feat: 调大标题的字号` (it said `style:`); the README of state S3 passes check 1.5b; lesson 1.9 makes the commit 「改了标题的颜色」.
- The learning workspace has two possible places after lesson 0.2. A learner who moves has the real folder at `~/Developer/Engineering`. A learner who decides to stay (decision `workspace_location` = `stay-in-sync`) gets an entrance at the same path: a symbolic link `~/Developer/Engineering` that points to the folder where it is, made by the tutor on the sentence of section 2 (or by the learner with the one command lesson 0.2 gives in a skippable box). So every later lesson writes `cd ~/Developer/Engineering` and it works in both cases; no later lesson needs a second variant. Only lesson 0.2 explains the entrance (one sentence; the word 符号链接 in a skippable box), lesson 0.2's check for the staying learner verifies that the entrance exists and leads to the workspace, and lesson 1.12 asks the staying learner again before `git init`.
- The history of 你的网站 is fixed, commit by commit (the tool's state ladder builds exactly this; tool-api.md section 15.3): 1.6c 「第一版网页」 (index.html, style.css, README.md and the `.editorconfig` that lesson 1.4 made the learner write) and 「在 README 里写上用 Git 记录改动」; 1.7b 「改了标题的颜色」; 1.9a 「换了一个标题颜色」 and 「添加 .gitignore」; 1.10b 「feat: 在首页加一条学习计划」 and 「feat: 调大标题的字号」; 1.13a 「docs: 添加 MIT 许可证」 (LICENSE and the README section together); 1.13b 「docs: 在 README 里写上网页地址」; 1.13c 「feat: 列表里写上网页已经上线」 and 「feat: 在页脚加上源代码的链接」. A lesson's hints and answers use exactly these subjects for the commits it asks for in 你的网站, its pasted `git log` output comes from a copy the ladder built, and wherever a number of commits is stated the text adds that the learner's own site may have more. Lesson 1.10 says honestly that the commits made before it keep their plain subjects: history is not rewritten.
- `git config` is taught in the form with a subcommand, in every lesson: `git config set --global <name> <value>`, `git config get <name>`, `git config unset --global <name>`, `git config list`. The manual of Git (git-config, page last updated in Git 2.56.1, read 2026-11-19) lists the forms without a subcommand and the options --get, --unset, --list, --add, --replace-all under 「deprecated modes」 and recommends the new syntax. Lesson 1.6 owns this: it teaches the new forms and carries the one 旧教程提醒 box (old tutorials, many official pages, and Git's own hints still show `git config --global user.name …`; that form still works on this computer; since which version the subcommands exist: verify in Git's release notes before stating it). Every other lesson uses the same forms without a second explanation. Each form a lesson shows is executed on Git 2.54 in the simulation first.
- Starter material (plan G11a): everything the tool builds (scenarios, the state ladder, exams) comes from the original starter files, also when the learner changed their copy; `starter/hello-fx/convert.py` is the one starter file a lesson asks the learner to edit.
- National standards as everyday examples (checked today on openstd.samr.gov.cn): the size of A4 paper is a recommended standard (GB/T 148-1997, 推标, 现行); household plugs and sockets are a mandatory standard (GB 1002-2024, 强标, in force since 2025-08-01; products that do not meet a mandatory standard may not be produced or sold: 《标准化法》第二十五条). STANDARDS.md section 2 now says: 「像 A4 纸的尺寸（推荐性国家标准 GB/T 148-1997）：没人逼你用，但不按它做，打印机、复印机、文件夹就都和你对不上。」 and, for 惯例·事实标准: 「像写信的格式：开头写称呼、结尾写“此致敬礼”。没有法律规定，但大家都这么写」.

## 7. Labels

Accepted today after the audit of all 30 cards (the cards are the reference; STANDARDS.md, the stage pages and the tool's syllabus are brought into line with them): WS-02 规范·组织; DOC-02 规范·本课程约定; REPO-01 惯例·事实标准; HELP-01 惯例·平台与工具; AI-01 规范·组织 (the order of the review steps is the course's own). Two rules follow for every card and every lesson text. First, the type of a rule never changes with the situation; only its 约束力 does (lesson 0.3 teaches and grades this): a contract or a company policy that names a rule is itself a 行业要求 for that project, while the named rule keeps its type. Second, every 约束力 is a level word with a scope (必须 / 推荐 / 参考（适用范围：……）), also for the course scope: not 「练习里每次提交都按这条做」 but 「必须（适用范围：本课程）；推荐（适用范围：所有项目）」. Step 4 of the seven-step procedure reads 「它只是某一个工具或平台本身的工作方式或期待吗（包括它在自己的官方文档里教你怎样用它）？」 in every place that states it. 复核周期 follows the header of STANDARDS.md: 6 months for law and platform policy, 12 for conventions of tools and platforms, 24 for stable community norms.

The label of a rule card follows from its source by the seven-step procedure (STANDARDS.md section 2, plan G3), not from the hint in plan section 4. A [§4] warning for an honest label is acceptable and is recorded under deviations_from_plan. 约束力 says how binding the rule is for this learner today and in which scope; 规则类型 says where the rule comes from; 谁来管 names only somebody who really can and does enforce it. Where a rule covers two different things with different enforcers (REMOTE-02: other people's personal data against one's own secrets), the card says so in plain words instead of claiming the stronger label for both.

## 8. Reports

open_issues entries begin with one of: "tutor contract needs:", "shared file needs:", "tool needs:", "lesson <id> needs:". Anything a later reader must know about the learner's machine after the lesson goes into end_state.


## 9. What changed in the tool today (complete list for lesson authors)

The tool is frozen for this round. Where a detail of wording differs between section 3 above, section 11 below and the fixed forms the validator checks (part E of this section), the validator's form wins, because your lesson must end with a clean validate; report the difference under open_issues ("tool needs:").

COMPLETE LIST, BOTH BATCHES OF 2026-11-19 PLUS THE REVIEW FIXES OF 2026-11-20 AND THE LAST SMALL PASS OF 2026-11-20 (API version 1; nothing a lesson can call was renamed or removed). Reference: docs/authoring/tool-api.md section 19 items 16-44 and section 19.1 items 45-63.

A. NEW OR CHANGED CALLS IN lesson.py

1. ctx.choose(question, options, key=None, explain="", feedback=None) -> value
   - For decisions with no right answer.
   - options: 2-6 labels, or (value, label) pairs.
   - Prints 「你的决定：<label>」; never right or wrong.
   - With key, it stores decisions[key] when the check passes, like ctx.decide.
   - Example: choice = ctx.choose("你怎么决定？", [("move", "请导师帮我搬到 ~/Developer（还没搬）"), ("stay-in-sync", "先留在原处，我知道风险")], key="workspace_location")
   - A bad --answer gives 「用法不对：--answer 给的「x」不是 A 到 B 之间的字母，也不是哪个选项的原文。这一题要选一个选项，例如 --answer A」.

2. ctx.gate_done(gate) -> bool
   - True only when every lesson the gate covers has a passed task AND the explain-back is recorded as pass.
   - Example: if ctx.gate_done("gate-1"): ctx.ok("阶段验收 gate-1 通过了")

3. ctx.gate_result(gate) -> GateResult (read-only named tuple)
   - Older fields: gate, title, attempts, passed, open, open_titles, done, in_progress, tasks.
   - New fields: practical_done, explain ("pass"/"again"/None), explain_date, lessons, open_lessons, open_lesson_titles, next_count, next_minutes.
   - .open lists only tasks tried without a pass, and is empty before the first sitting, so name what is missing with .open_lesson_titles.
   - .next_count / .next_minutes are the open sitting's ungraded tasks and minutes while a sitting is open, an extra practice sitting included. They are 0 only when the practical part is passed and no sitting is open. Never branch on next_count == 0; use .practical_done.
   - Example: ctx.fail("还有课的实操题没通过，练好以后补考", where="gate-1 的成绩", saw="还没通过：" + "、".join(ctx.gate_result("gate-1").open_lesson_titles))
   - An unknown gate raises 检查器出问题.

4. ctx.git_global_state(key) -> "true" | "false" | "unset" | "invalid"
   - A typo such as fasle gives "invalid".

5. ctx.git_global_all(key) -> list of all values; [] when unset.
   - In the case of plan G7 (and in the simulation home): ctx.git_global_all("gpg.ssh.program") == [""].
   - A broken ~/.gitconfig makes both 4 and 5 raise 检查器出问题: 「Git 读不了你的全局设置文件（~/.gitconfig），里面可能有一行写坏了。」

6. ctx.visible(text) -> str
   - U+3000 → 〔全角空格〕, tab → 〔Tab〕, U+00A0 → 〔不换行空格〕, a trailing space → ·.
   - Use it in saw=. Messages no longer collapse U+3000 or NBSP.

7. ctx.final (bool, read-only)
   - True inside exam --grade.
   - A wrong ask ends 「这个回答和实际情况对不上，这一题记为还没达标。」
   - A wrong quiz ends 「这一题没有选对，记为还没达标。」 (after the option's feedback sentence).
   - Changed 2026-11-20. It was 「…这一场记为还没达标；补考会换一套题面。」, which was untrue in an extra practice sitting.
   - Never add your own retry advice to graders; exam prints what comes next.

8. ctx.show(target, entrance=True)
   - The workspace and every path inside it print through ~/Developer/Engineering whenever that path leads there: the moved folder, or the entrance link of a learner who stayed.
   - entrance=False prints the real place. Use it in 0.2c: ctx.show(ctx.workspace, entrance=False) gives the real place, for example ~/Desktop/Engineering.
   - ~ is also used when HOME is reached through a link, so drop realpath workarounds.

9. ctx.parse_int finds the number anywhere.
   - 「第二条」 2, 「第四课」 4, 「一共三个」 3, 「共 12 行」 12, 「大概五个」 5, 「十分钟」 10.
   - Chinese numerals are read from 0 to 9999: 「一百二十」 120, 「一百零五」 105, 「两千」 2000. A numeral with 万 or 亿, a colloquial short form (「一百二」) and two digits in a row (「三四个」) give None.
   - A remark in brackets after the number is left aside: 「4 行（第一行是标题）」 4, 「3（不确定）」 3.
   - A negation counts only next to the number (since 2026-11-20). Words such as 不算 / 不确定 / 不包括 elsewhere do not matter: 「5 个，不算 . 和 ..」 5 (lesson 1.1's own condition repeated), 「3 行，不包括空行」 3, 「应该是 3 个吧，不太确定」 3, 「差不多 3 个」 3, 「3 个左右」 3.
   - Spaces or an opening bracket between the negation and the number do not hide it (last pass of 2026-11-20): 「不是（3）」 「没有（3 个）」 「不 是 5」 「不太是 5」 give None.
   - One rule for comparison words (last pass of 2026-11-20): an answer that gives a bound and not a number is not a number. 少于 小于 低于 不到 不足 不超过 不多于 不少于 至多 最多 至少 最少 超过 多于 大于 高于 (before or after the number) and 以上 以下 以内 以外 (after it) give None: 「少于3行」 「最多 3 行」 「至少有 3 个」 「超过了 3 个」 「至少得 3 个」 「3 行以上」 「5 个以内」 「3 个或以上」 「3（以上）」 「3 个（至少）」. 左右 is not one of them. A question whose right answer is a bound needs ctx.quiz or a string expected, not an int. After 第 the word bounds nothing: 「第 3 行最多」 3, 「第 3 行以下」 3; without 第, 「3 号最多」 and 「3 行以下是空行」 give None, so a which-one question with an int expected asks for 「第几」 or uses ctx.quiz.
   - None for:
     - two different numbers 「第二条，共 3 行」;
     - ranges 「三到四个」 「3 到 4 个」 「3-4」;
     - decimals, versions and halves 「3.5」 「1.6a」 「三个半」;
     - 三四个;
     - a negation of the number 「不是3」 「没有 3 个」 「不到 3 个」 「一个也没有」 「负一」 「不是（3）」;
     - a bound 「少于3行」 「3 行以上」.
   - Drop workarounds that strip 第 or 一共.

10. sc.copy_in("starter/…", rel)
   - Copies the ORIGINAL from tools/courselib/starter_manifest.json, never the learner's copy.
   - An unknown starter/ path is 检查器出问题: 「搭建练习场的代码要复制 <path>，但起始文件的原样清单里没有它。」
   - Whoever changes starter/ runs python3 tools/dev/build_starter_manifest.py --write (builders only; never in the learner's workspace).

11. Marker .playground version 2.
   - Facts and todo lines are base64 under "data". This is against accidents, not a secret, so never make a fact secret.
   - ctx.scenario().facts and .todo are unchanged; version 1 markers are still read.
   - Tests use courselib.scenario.read_marker(folder).

12. State ladder (sc.site_before / sc.state)
   - S2: .editorconfig.
   - S3: README with a ```zsh block.
   - S4: 2 commits, 「第一版网页」 and 「在 README 里写上用 Git 记录改动」.
   - S5: drafts/colors.md (ignored), 5 commits (1.7b 改了标题的颜色 with #c2410c; 1.9a 换了一个标题颜色 and 添加 .gitignore).
   - S6: 7 commits, the last 「feat: 调大标题的字号」 (not style:).
   - S7: README 「## 许可证」 with `[LICENSE](LICENSE)`, list line 「我已经把网页放到了网上」, footer link 「这个网页的源代码」, 11 commits.
   - Always read info.facts["site_commits"], e.g. expected=info.facts["site_commits"] + 1.
   - New constants: states.LESSON_COLOR, README_LICENSE, README_PAGES, LIST_BEFORE, LIST_AFTER, FOOTER_LINK, REPO_URL, EDITORCONFIG, DRAFT_NOTE.

13. Exam tasks
   - sc.todo lines are shown under the task text.
   - Folder line: 「这道题的文件夹：<folder>」 (was 「文件夹：…」).
   - cd line: 「先进入这道题的文件夹：cd <folder>。题目里说的文件夹如果在它里面，再 cd 进那一层。」 (was 「进入：cd …」).
   - The cd line is left out when the text or a todo line contains "cd " or says 「进入 <folder inside the task>」.
   - Write 「先 cd 进 {dir}/{folder}，…」 when the learner must stand deeper.
   - Never put cd ~/Developer/Engineering into sc.todo.

14. META
   - minutes from 15 to 40, a warning above 30 (the honest G5a number).
   - Each 「## 第 N 站：……（约 X 分钟）」 heading must equal META.
   - Lesson 1.4 must have stations 1.4a, 1.4b and 1.4c.
   - "gh": "2.105.0" is a valid, compared key in verified.tools.

B. THE GATE RULE (what a lesson may promise)

- One sitting holds one task per lesson the gate covers:
  - gate-0: 0.1-0.4, 4 tasks.
  - gate-a: 1.1-1.5, 5 tasks.
  - gate-b: 1.6-1.10, 5 tasks.
  - gate-1: 1.11-1.16 only, 6 tasks. No borrowing; its tasks also use earlier skills.
- A lesson counts once one of its tasks is passed. The practical part is passed when every lesson counts.
- A retest (补考) holds only the lessons not yet passed, with the failed task in its other form (A/B).
- The gate is passed when the practical part is passed AND the explain-back is recorded with python3 tools/course.py exam <gate> --explain pass (or --explain again).
  - The learner starts the explain-back by saying “请问我 <gate> 的讲解题”.
  - --explain is refused before the first graded sitting.
  - The latest verdict counts. An again that replaces a pass says so.
  - A pass recorded before the practical part is passed is kept and counts once it is.
- A gate never blocks the next lesson. A sitting that was started and not graded is shown as such (with --grade) wherever the learner is.
- --all is a full sitting, one task per lesson, preferring tasks never drawn. After the practical part it is 加练 and never takes a passed lesson back. Never call it 全部重考.
- Time: the head prints 「一共 N 题，每课一题，预计 M 分钟（每题的预计分钟数加起来）。」; the explain-back adds about 10 minutes (two explain-back questions and, at gate-0, gate-a and gate-b, a debugging question, then the verdict and the command that records it: four exchanges with the tutor under plan G5a).
  - Today's ranges of the tasks (recomputed from the catalog, 2026-11-20): gate-0 19-23 (+10, about 30-35); gate-a 27-33 (about 40-45); gate-b 25-33 (about 35-45); gate-1 43-55 (about 55-65).
  - The safest wording: 「开考时工具会打印题数和预计用时」.
- Never promise that all tasks of a pool must pass, or 4-6 tasks, or a time outside the ranges above. Never say how many explain-back questions there are (no 「两道讲解题」, no 「两个问题」).

C. LEARNER-FACING STRINGS A LESSON MAY HAVE PASTED (old → new)

1. check, resume sentences:
   - 「下一站：1.6b「…」。下次可以对导师说“从 1.6b 继续”。」
   - 「1.6 课还没通过的站：…」 + 「下次可以对导师说“从 1.6a 继续”。」
   - After the last station: 「1.6 课的 3 站都通过了。收尾先做全课检查：python3 tools/course.py check 1.6」 + 「下次可以对导师说“从 1.6 的收尾继续”。」
   - Next lesson: 「下一课：1.7「Git：看懂改了什么」。下次可以对导师说“从 1.7 开始”。」 + 「课文在 stages/…/lesson.md」
   - End: 「已有的课程都学完了。下次可以对导师说“准备阶段 2”。」

2. check, gate lines:
   - Old: 「下一步是关卡 gate-b「本地 Git 关卡」：N 道实操题，预计 M 分钟。开始考试：…」
   - New: 「下一步是小关卡 gate-b「本地 Git 关卡」：5 道实操题，预计 29 分钟，讲解题另需约 10 分钟。开始考试：python3 tools/course.py exam gate-b」 (约 10 分钟 since the last pass of 2026-11-20; it was 约 5 分钟) + 「下次可以对导师说“做小关卡 gate-b”。」
   - gate-0: 「下一步是 gate-0「起步小关卡」：…」. gate-1: 「下一步是 gate-1「阶段 1 验收」：…」.
   - A sitting of the due gate is open and not graded (new 2026-11-20): 「小关卡 gate-b「本地 Git 关卡」第 1 场考试还没批改完（5 题）：做完以后批改：python3 tools/course.py exam gate-b --grade；想放弃这一场重新出题：python3 tools/course.py exam gate-b --new。」 + 「下次可以对导师说“做小关卡 gate-b”。」
   - Explain due: 「小关卡 gate-b「本地 Git 关卡」的实操题都通过了，还差讲解题（约 10 分钟）：请导师问你讲解题，评完用 python3 tools/course.py exam gate-b --explain pass 记下（要再来一次就写 again）。」 + 「下次可以对导师说“请问我 gate-b 的讲解题”。」
   - Every open gate adds one of:
     - 「小关卡 gate-a「终端与文档关卡」还没有通过，它不挡下一课。准备好了就对导师说“做小关卡 gate-a”。」
     - 「…的实操题都通过了，讲解题还没记为通过，它不挡下一课。准备好了就对导师说“请问我 gate-a 的讲解题”。」
     - (new) 「小关卡 gate-a「终端与文档关卡」第 1 场考试还没批改完（5 题），它不挡下一课。做完以后批改：python3 tools/course.py exam gate-a --grade」

3. check, closing steps:
   - Old: 「1. 用自己的话把本课行规（…）各写一句到 notes/my-rules.md」 / 「2. 写一句日志：…」
   - New: 「1. 行规笔记：运行 code notes/my-rules.md，在小标题「GIT-01 <full title from rules.md>」「GIT-02 <title>」下面各用自己的话写一两句，再配一个你自己的例子」 / 「2. 一句话日志：python3 tools/course.py journal」.
   - From 1.12 on the head is 「收尾还有三件小事：」 and step 3 is 「备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做」.
   - A lesson without a new rule (1.3), new 2026-11-20: 「收尾还有一件小事：」 / 「1. 一句话日志：python3 tools/course.py journal」 (from 1.12 on 「收尾还有两件小事：」 with the backup as step 2). The old 「用自己的话把这一课最想记住的一点写到 notes/ 里」 is gone.

4. status:
   - The 下一步 line: 「下一步：<text>。下次可以对导师说“<sentence>”。」, e.g. 「…做完第 1 站运行 python3 tools/course.py check 0.1a。下次可以对导师说“开始上课”。」
   - With reviews: 「下一步：先做 N 条到期的复习：python3 tools/course.py review；然后 …。下次可以对导师说“…”。」, then the open-gate lines (2 above).
   - First line (new 2026-11-20), following the next step:
     - 「你在：1.6 Git：第一次提交 · 第 2 站「第一次提交」（1.6b）」 for a station or a lesson;
     - 「你在：0.4 像管项目一样管学习 · 收尾」 when the next step is that lesson's closing steps;
     - 「你在：gate-0「起步小关卡」（学完 0.4 课以后）」 or 「你在：小关卡 gate-b「本地 Git 关卡」（学完 1.10 课以后）」 when it is the gate.
   - Landing line (new 2026-11-20): 「下一个落脚点是小关卡 gate-a「终端与文档关卡」（学完 1.5），还有 10 站」, 「下一个落脚点是 gate-0「起步小关卡」（学完 0.4），还有 12 站」, 「下一个落脚点是 gate-1「阶段 1 验收」（学完 1.16），还有 n 站」 (「阶段 N 结束」 only where a stage's last lesson has no gate). Was 「到下一个落脚点「终端与文档关卡 gate-a」（学完 1.5）：还有 10 站」.
   - Landing and stage lines at a lesson's closing steps or the gate after it (last pass of 2026-11-20): they follow the same lesson as the first line, and 「还有 0 站」 is never printed.
     - Closing steps: 「你在：0.4 像管项目一样管学习 · 收尾」, 「下一个落脚点是 gate-0「起步小关卡」（学完 0.4）：站都通过了，还差 0.4 课的收尾」, 「阶段 0 起步：已完成 n/n 站（100%）」 (were gate-a 「…（学完 1.5），还有 10 站」 and 「阶段 1 工程师的基本功：已完成 0/39 站（0%）」).
     - The gate is the next step (due, a sitting open, or only the explain-back left): 「你在：gate-0「起步小关卡」（学完 0.4 课以后）」, 「落脚点到了：gate-0「起步小关卡」」, the same stage line.
     - The same after 1.5 (小关卡 gate-a「终端与文档关卡」), 1.10 (小关卡 gate-b「本地 Git 关卡」) and 1.16 (gate-1「阶段 1 验收」; the first line there was 「已有的课程的站都通过了（N/N 站）。」 and now is 「你在：1.16 阶段作品与验收 · 收尾」 or 「你在：gate-1「阶段 1 验收」（学完 1.16 课以后）」 until gate-1 is passed).
     - Once the gate is passed every line follows the next lesson. PROGRESS.md has the same lines.
   - Long break: 「距离上次学习：N 天。隔得有点久，建议先走一遍回归流程：对导师说“我回来了，带我走回归流程”。」 (was 「…」 quotes; the same in review: 「想把落下的内容理一理，可以对导师说“我回来了，带我走回归流程”。」).
   - All done (every station passed and gate-1, the gate after the last lesson, passed; before that the first line follows 1.16's closing steps or gate-1): 「已有的课程的站都通过了（N/N 站）。」 + 「下一步：已有的课程都学完了。下一阶段的课还要准备。下次可以对导师说“准备阶段 2”。」. 「继续下一阶段」 is gone.
   - The 70% notice is not shown while the next stage's lessons exist.
   - PROGRESS.md: 「- gate-b 小关卡「本地 Git 关卡」（1.6 到 1.10 课）：<state>」. Was 「通过 n/m 题（最近一次 …）」.

5. journal:
   - 「下次从哪开始（直接回车 = 从 0.1 的收尾继续）：」. The default is the canonical sentence.

6. exam:
   - Heads: 「关卡考试 · 小关卡 gate-a「终端与文档关卡」 · 第 1 场」, 「关卡考试 · gate-0「起步小关卡」 · 第 1 场」, 「关卡考试 · gate-1「阶段 1 验收」 · 第 1 场」.
   - Count lines:
     - 「一共 5 题，每课一题，预计 30 分钟（每题的预计分钟数加起来）。」
     - 「实操题都通过以后还有讲解题，约 10 分钟：导师问你几个问题，请你讲出“为什么这样做”。」 while the practical part is open (was 「…约 5 分钟：导师问你两个“为什么这样做”的问题。」);
     - in a 加练 sitting (new): 「讲解题还差一次，约 10 分钟：对导师说“请问我 gate-b 的讲解题”。」, or no line after the explain-back passed.
   - Retest head: 「第 n 场 · 补考：只考还没通过的课，每课一题，没通过的题换成另一套题面」.
   - Listing: 「  gate-1  阶段 1 验收（1.11 到 1.16 课）：还没考过；一场 6 题，预计 49 分钟」.
     - The states are 还没考过… / 实操题通过了 c/t 课；下一场… / 第 n 场还没批改完（k 题） / 实操题都通过了，还差讲解题 / 通过了（讲解题 date).
     - With an extra practice sitting open (new) 「实操题都通过了，还差讲解题；第 4 场加练还没批改完（4 题）」 or 「通过了（讲解题 date）；第 4 场加练还没批改完（4 题）」. The same words are used in PROGRESS.md.
   - After a fail: 「练好以后补考：python3 tools/course.py exam gate-a。补考只考还没通过的 N 课，每课一题，没通过的题换另一套题面。」; 「这是加练：通过的课不会退回去。」 only in a 加练 sitting.
   - Practical part passed: 「实操题都通过了。还差讲解题：对导师说“请问我 <gate> 的讲解题”。导师判断以后，用这条命令记下结果：python3 tools/course.py exam <gate> --explain pass（要再来一次就写 again）」.
   - Recording pass: 「讲解题的结果记下了：通过（YYYY-MM-DD）。」, then:
     - 「小关卡 gate-0 通过了：实操题每课都有一题通过，讲解题也记为通过（YYYY-MM-DD）。」;
     - or, before the practical part is passed, 「实操题还有 N 课没通过：…。补考：python3 tools/course.py exam gate-0」 + (new) 「讲解题的“通过”先记着：等实操题每课都有一题通过，小关卡 gate-0 就通过了。」
   - Recording again: 「讲解题记为“再来一次”：准备好了再对导师说“请问我 gate-0 的讲解题”。」. After a recorded pass it is preceded by (new) 「之前记的是“通过”（YYYY-MM-DD），现在改成了“再来一次”：小关卡 gate-0 现在还没通过。」
   - --explain accepts PASS, ｐａｓｓ, 「pass」 with a full-width space. A bad value: 「用法不对：选项 --explain 不能是 fail（可以用的值：pass、again）」 + 「看这个命令的说明：python3 tools/course.py exam -h」.
   - Missing tasks: 「这个关卡的考题还没写全：{lessons} 课还没有考题，这一场先考已经写好的 N 题。」
   - Wrong answers inside grading: see A7.
   - Gone: 「…的考题全部通过了」, 「现在只有 N 题（正式考试是 4 到 6 题）」, 「都已经通过了」, 「…补考会换一套题面。」 in graders.

7. scenario:
   - Old one line: 「练习场里的东西随便改。改乱了就加 --reset 重搭一份，练习场外面的文件不会受影响。」
   - New two lines: 「练习场里的东西随便改，练习场外面的文件不会受影响。」 and 「改乱了可以重搭一份：python3 tools/course.py scenario <id> --reset」.
   - Already built: 「想从头再来一份（会删掉你在里面做过的改动）：python3 tools/course.py scenario <id> --reset」.
   - A folder holding another build of the tool: the refusal names the id the learner typed (「…python3 tools/course.py scenario 1.3 --reset」, was 「scenario 1.3-start --reset」).
   - The cd line reads 「回到学习工作区：cd ~/Developer/Engineering」 for every learner with the entrance.

8. Usage errors:
   - Old 「用法不对：不认识的参数：--wirte」 → new 「用法不对：不认识的选项：--wirte」.
   - 「用法不对：选项 --confidence 后面要跟一个值」; other words stay 参数.
   - Full-width input: 「用法不对：命令里混进了全角字符（中文输入法打出来的空格或符号）：check〔全角空格〕1.14a。切回英文输入法，把这一段重新打一遍。」 (was 「没有 check　1.14a 这个命令」).
   - New 2026-11-20:
     - punctuation an input method leaves after an id is dropped (`check 1.1a，` and `check 1.1a。` work, were 「看不懂「1.1a，」」);
     - a stray space around an option is dropped (`"--again "` works);
     - an unknown word shows its stray space as ·: 「用法不对：不认识的参数：x·」.

9. doctor:
   - Location: 「学习工作区的位置：<real path>，…」 (was 「工作区的位置」).
   - Stayed learner, synced, entrance present: 「…~/Developer/Engineering 是通往它的入口，课文里的 cd ~/Developer/Engineering 照样能用；学习工作区本身还在同步盘里。这是你在第 0.2 课做的决定：先留在原处。 → 第 1.12 课把课程变成仓库之前，会再问你一次」. After 1.12 is done (new): 「→ 第 1.12 课已经问过你了；想搬的时候对导师说“帮我把课程安置到 ~/Developer”」.
   - Stayed learner, entrance missing: 「…~/Developer/Engineering 这个入口还没有建，… → 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”」. The 1.12 clause is left out after 1.12.
   - New 2026-11-20: the same entrance sentence (a 需要处理 line) also when the folder is not synced or that cannot be told, once the learner has a workspace_location decision or passed 0.2: 「学习工作区的位置：<real path>，不在同步到云端的文件夹里。这是你在第 0.2 课做的决定：先留在原处。~/Developer/Engineering 这个入口还没有建，课文里的 cd ~/Developer/Engineering 现在走不通。 → 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”」 (or the broken-entrance wording).
   - Identity: 「…没设置的那一项，Git 会拿这台 Mac 的账户名和电脑名自己拼一个：提交照样能成功… → 第 1.6 课会带你正式设好」.
   - Signing lines name the setting: 「提交签名：已经打开（commit.gpgsign=true，格式 ssh），但设置 gpg.ssh.program 是空的：Git 会去运行一个没有名字的程序。现在每次 git commit 都会失败。 → 第 1.11 课会带你处理」. All SSH lines point to 1.11; the gpg lines point to 1.6.
   - New 2026-11-20: a line that points at a lesson already done says 「→ 第 1.6 课已经学过了，把这一行发给导师」 (same for 1.11, identity and git lines).
   - gh: 「GitHub CLI（gh）：还没安装。第 1.11 课会带你装，在那之前用不到。」 (was 还没装).
   - New line: 「…对导师说“急救：学习工作区里多了 .git”」.
   - New starter line: 「…想恢复原样，对导师说“急救：starter 被改动了”。」.

10. fresh:
   - gh row: 「还没安装（第 1.11 课会装）」 until 1.11 is done.
   - Closing sentence: 「下一步：装了的工具都和课程核对时一样，不用做什么。还没安装的，到了上面写的那一课会带你装。」
   - gh is no longer listed as not compared.

D. THE ENTRANCE

- Every lesson writes cd ~/Developer/Engineering and nothing else. No 「没搬的换成 …」 notes.
- The tool shows that path whenever it leads to the workspace.
- Only 0.2 explains the entrance. A check naming the real place uses ctx.show(..., entrance=False).
- Testers use make_sim_home.py <dir> --stay.

E. VALIDATOR CHECKS BY TAG (warnings unless marked)

- [G5] minutes 15-40 (outside: error; above 30: warning); a heading's minutes against META; the header 「**用时** N 站，约 X 分钟」 (N = stations, X = stations plus 收尾).
- [I3] an option whose whole text is q, s or another review command.
- [I1] save points:
  - 「> **存档点 1.6a**：到这里可以安全停下。下次可以对导师说“从 1.6b 继续”。」
  - after the last station: 「…“从 1.6 的收尾继续”。」
  - mid-station: 「> **中途存档点**：<做完了什么>，到这里可以安全停下。下次可以对导师说“做小关卡 gate-0”。」
- [I1] station parts: 概念 / 跟我做 / 补全 / 自己做 in that order. The last two lines are 「- 提示：`python3 tools/course.py hint 1.6a`（每运行一次多给一级）」 and 「- 检查（先回到学习工作区）：`python3 tools/course.py check 1.6a`」. An exam part goes only behind a 中途存档点.
- [I1] the closing section:
  - heading 「## 收尾（约 N 分钟）」;
  - steps:
    - 「1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.6`」
    - 「2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「ID 标题」…下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。」 (none in a lesson without a new rule)
    - 「3. 一句话日志：`python3 tools/course.py journal`」
    - from 1.13 「4. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。」 (1.12 itself must contain git push);
  - last line 「都做完，这一课就完成了。下次可以对导师说“从 1.7 开始”。」;
    - for 1.5 and 1.10 the gate sentence 「…下一步是小关卡 gate-a：它是单独的一段时间，开考时工具会打印题数和预计用时。下次可以对导师说“做小关卡 gate-a”。」;
    - 1.16 ends 「…下次可以对导师说“准备阶段 2”。」;
    - 0.4 ends “从 1.1 开始”.
- [I1] optional material: only 「> **想多了解（可跳过）：<小标题>**」 or the closing 「## 想多了解」. In headings, 选做 / 选读 / 可选 / 可以跳过 are reported only as a label: at the start, in brackets, after 「，」 or a comma, before 「：」, at the end of the heading, or followed by 练习/题/部分/内容/阅读/材料 or by 的 + 进阶/部分/内容/阅读/材料/练习/题 (「### 可选的进阶」, 「### 这一段可选」, 「### 进阶，可选」, 「### 补充（可以跳过的部分）」 are reported since the last pass of 2026-11-20). 「### 自己做（可选的两种做法都行）」 is fine (since 2026-11-20).
- [G6] the line 「和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。」 appears exactly once, after the first mark, not in a blockquote. Marks never go in backticks or code. unverified_steps is non-empty exactly when marks exist.
- [G2] sentences the learner says to the tutor in lesson.md and lesson.py are only the fixed ones of COMMON section 2.
  - Only 对导师说 / 跟导师说 / 向导师说 / 和导师说 and 「导师……，对它说」 are read. The tutor's own words (「导师说“…”」, 「导师会对你说“…”」) are not, since 2026-11-20.
  - Straight double quotes around Chinese in prose are warned.
- [G10]:
  - no Desktop/Code/Engineering outside 0.2;
  - no /Users/<ascii> (/Users/Shared and /Users/Guest are fine) and no /private/tmp/;
  - no 课程文件夹;
  - from 1.6 on no 回到工作区 and no 工作区 next to ~/Developer/Engineering. From 1.12 on, 工作区 next to it on a line that also says git, 仓库, 提交, 暂存, 干净 or 改动 is Git's word and is left alone.
- [I2] 本课行规: the table 「| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |」 with cells copied from the card, then 「完整卡片在本课文件夹的 `rules.md`。」. Every 必须/推荐/参考 on a card is followed directly by （适用范围：本课程/本机/所在团队/所有项目）.
- [G4] every 旧教程提醒 (box or card field) says since when: a year, a version, a date, or a named release (「从 macOS Catalina 起」, 「Python 3」; also without spaces next to Chinese: 「从macOS Catalina起」, 「从Python 3起」). A product name with a number and a measure word is a count, not a release: 「Git 2 种写法」 does not count. No git config without a subcommand (set/get/unset/list) in code, inline code or HINTS.
- [X] one English gloss per term. Decided owners: 路径 0.2, 递归 1.2, 令牌 1.9, 提交签名 1.6, 分支 1.6, 讲解题 0.4; scenario 0.1, git --version 1.6, git commit -m … -m … 1.10, mkdir 0.2, git config get 1.6, git diff <文件名> 1.7, git log -1 1.11, exam gate-… and --grade 0.4.
- [§4] syllabus stations (1.4 needs 1.4c) and the accepted rule labels (WS-02 规范·组织, DOC-02 规范·本课程约定, REPO-01 惯例·事实标准, HELP-01 惯例·平台与工具, AI-01 规范·组织).
- [I7] (error, --complete only) every lesson of a gate has a task of that gate.

F. FOR TESTERS

- make_sim_home: the [gpg "ssh"] program and allowedSignersFile keys are present and empty. SSH signing there fails with 「error: cannot run : No such file or directory」 until gpg.ssh.program is unset or set.
- --stay builds the stayed learner's layout.
- The sim copy now carries the course's own journal/README.md, notes/README.md and learner/README.md and the heading skeleton of notes/my-rules.md (when they exist in the workspace; today notes/ does not).
- Tests read markers with read_marker.
- build_starter_manifest.py:
  - --check lists starter/hello-fx/convert.py apart (「课文让学习者自己改的文件，改过不算问题：…」) and does not count it;
  - --restore refuses it without --force;
  - --write is for builders only; its -h help says 「(builders only; never run it in the learner's workspace)」.



### Tool changes that concern several lessons
- all lessons: station minutes must be the honest G5a number (15-40, above 30 warns), and each 「## 第 N 站：……（约 X 分钟）」 heading must equal META.
- all lessons: re-paste any quoted check output after a whole-lesson check (new closing lines and gate wording, the open-sitting line), any scenario closing line (two lines), any status sample (first line 「你在：…」 and landing line 「下一个落脚点是…（学完 …），还有 n 站」; at a lesson's closing steps or the gate after it the landing and stage lines follow that lesson: 「下一个落脚点是…（学完 …）：站都通过了，还差 … 课的收尾」 or 「落脚点到了：…」), and any exam wrong-answer line (no 「补考会换一套题面」).
- all lessons: write cd ~/Developer/Engineering only; remove any 「没搬的换成 cd ~/Desktop/Code/Engineering」 note (superseded by the entrance decision).
- 99.1 (docs/authoring/example-lesson): outside the syllabus, so every new form check except the closing last line applies; it now shows form warnings. The owner of docs/authoring should make it follow the fixed forms.


## 10. Ledger of terms and commands (from the audit; the owners named here are binding)

```text
=== LEDGER 1a: TERMS entries (all 158, course order). Format: term (en) | first station | plain to keep | verdict ===
课文 (lesson text) | 0.1a | 这门课每一课的文字说明，告诉你一步步做什么 | owner
导师 (tutor) | 0.1a | 按这个工作区的规则当教练的 Claude：给提示，不替你做练习 | owner
学习工作区 (workspace) | 0.1a | Engineering 这个文件夹：课文、工具和你的笔记都在里面 | OWNER. 0.2 uses 课程文件夹 (15x), so drop it. Bare 工作区 for Engineering must go after 1.6b: 1.12 (8 places) and 1.14 l.182. Before 1.6 it is tolerable but 学习工作区 is preferred: 0.3 l.483, 0.4 l.439, 1.1 l.502, 1.2 l.191-206, 1.4 l.252, 1.5 l.192/357
路径 (path) | 0.1a | — | DROP (decided owner 0.2a); prose clause at l.51 stays
状态行 (status line) | 0.1a | 导师每次新对话第一条消息的第一行… | owner
存档点 (save point) | 0.1a | 每一站的结尾… | owner (5a: 提交 is also likened to 游戏存档; 1.8 says 存档 for commit, which is acceptable)
终端 (terminal) | 0.1b | 用打字而不是点鼠标来指挥电脑的窗口 | owner (5a 对讲机 analogy and its break sentence are present)
命令 (command) | 0.1b | 在终端里敲的一行指令 | owner (5a analogy 口令 not used; 1.1a gives 命令名、选项、对象)
提示符 (prompt) | 0.1b | 终端每行开头那段字，以 % 结尾 | owner
命令解释器 (shell) | 0.1b | — | OWNER 0.1b, but rename the term to "shell" (register); plain: 在终端里接你命令、照着执行的程序，中文有时叫命令解释器；你的 Mac 上它叫 zsh. Reminders in 0.2b l.331, 1.1a l.210, 1.2b l.390 and 1.14c l.532 are fine
程序 (program) | 0.1c | 一份写着一步步指令、交给电脑去执行的文本文件 | owner
解释器 (interpreter) | 0.1c | 读程序文件、照着一行行执行的那个软件 | owner
编辑器 (editor) | 0.1c | 写代码和文档用的软件，你电脑上是 VS Code | OWNER; 1.4a l.21 re-gloss "编辑器（editor）" → shorten
练习场 (playground) | 0.1c | 工具专门放练习材料的文件夹… | OWNER; 0.2a l.76, 0.3a l.62 (bold) and 1.1 l.15 re-define → shorten
路径 (path) | 0.2a | 文件在电脑里的地址（may add 一层层文件夹的名字用 / 隔开） | OWNER (decided); 1.3b l.368 "（path）" → drop
绝对路径 / 相对路径 | 0.2a | as listed | owner
主文件夹 (home folder) | 0.2a | 你这个用户在电脑上的“家”，写作 ~ | OWNER; rival 个人文件夹 in 0.1 l.492 and 1.3 l.359/387 → replace
上一级文件夹 / Tab 补全 | 0.2a | as listed | owner
说明书 (man page) / 全角字符 / 半角字符 | 0.2b | as listed | owner (1.5a l.36 bold **半角** is a reminder: OK)
云同步文件夹 / 短横线命名 | 0.2c | as listed | owner
前端 / 后端 / 数据 / 运行环境 / 状态码 | 0.3a | as listed | owner
服务器 (server) | 0.3a | 一台一直开着、专门回答别人请求的电脑 | OWNER (topic station); 0.2c l.538 forward clause "服务器（server，…）" acceptable
软件生命周期 / 需求 / 测试 / 运维 / 岗位期望 | 0.3b | as listed | owner
规则类型 / 约束力 / 标准 / 行业要求 / 惯例 / 个人偏好 | 0.3c | as listed | owner (0.1 l.541-545 forward-mentions with 第 0.3 课细讲: OK)
任务 / 看板 / 完成的定义 / 在制品限制 | 0.4a | as listed | owner
迭代 (iteration) | 0.4b | as listed | owner
复盘 (retrospective) | 0.4b | 一轮结束后回头看：哪里顺、哪里卡、下一轮改一件什么 | OWNER; 1.16c l.604 re-introduces it in bold with a new analogy (下棋 replaces 跑步训练) → back-reference
备份 / 压缩包 | 0.4c | as listed | owner
关卡 (gate) | 0.4c | as listed | owner
选项 (option) | 1.1a | 跟在命令后面、以短横线开头的开关… | OWNER (plan row). 0.2b l.368 forward gloss with 第 1.1 课会细讲: OK. 0.3b l.322 second "（option）" gloss → shorten. 0.4a l.66 calls --write 参数（argument）: contradiction → fix 0.4. 1.1a should acknowledge 0.2
隐藏文件 (hidden file) | 1.1a | as listed | owner
文本文件 (text file) | 1.1b | as listed | owner
复制 / 移动 | 1.2a | as listed | owner (门牌 analogy matches 5a 路径)
递归 (recursive) | 1.2a | 连同里面的文件夹、文件夹里的文件，一层一层全算上 | OWNER (decided); 0.4c l.343 forward clause OK; 1.2 may say 0.4 zip -r 见过
废纸篓 / 通配符 | 1.2b | as listed | owner
引号 (quotes) | 1.2b | 把带空格的名字括起来… | OWNER (plan row); 0.2a l.231 already glossed "引号（quote…）" → 1.2 says 0.2 提过
匹配 / 区分大小写 | 1.3a | as listed | owner
递归 (recursive) | 1.3a | — | DROP (decided); l.162 bold re-definition → reminder
模式 (pattern) | 1.3b | 描述“名字长什么样”的写法… | OWNER (Pro Git: pattern = 模式); 1.9a 匹配模式 → rename
受限模式 / 资源管理器 / 自动保存 | 1.4a | as listed | owner (0.1c l.457 mentions 用受限模式打开 in a clause: OK)
标签 (tag) | 1.4a | 网页文件里尖括号括起来的记号… | OWNER = HTML tag; VS Code tab = 标签页 (0.1c). The "标签上…圆点" wording in 1.5 l.120, 1.6 l.472/713, 1.7 l.105, 1.9 l.196 and 1.13 l.174 is covered by the disambiguation sentence added to 1.4
命令面板 / 快速打开 / 内置终端 / 字符编码 / 换行符 / 缩进 / EditorConfig | 1.4b | as listed | owner
扩展 (extension) | 1.4b | 给 VS Code 加功能的附加程序 | owner (near-homonym of 1.5a 扩展名; GLOSSARY should cross-reference)
Markdown / 扩展名 / 预览 / 标题 / 行内代码 / 代码块 | 1.5a | as listed | owner (0.1 l.164 Markdown forward clause OK)
README (README) | 1.5b | as listed | owner (5a 招牌 analogy present)
根目录 (root directory) | 1.5b | 一个项目最外层的那个文件夹 | OWNER; 0.3 l.483 uses it early → reword; 1.6c 项目根目录 duplicates it
版本管理 (version control) | 1.6a | as listed | OWNER; add 也叫版本控制 (Pro Git)
仓库 (repository) | 1.6a | 被 Git 管着的文件夹，隐藏的 .git 文件夹里存着全部快照 | OWNER (5a 相册 analogy present). 0.2c l.468 and 0.3c l.414 forward clauses OK. 仓库 = 'warehouse' in analogies 0.2 l.460 and 0.3 l.50 → 库房
提交 (commit) | 1.6a | 拍一次快照并写一句说明 | owner (5a 游戏存档 analogy present)
全局设置 (global configuration) | 1.6a | as listed | owner
提交签名 (commit signing) | 1.6a | 给提交盖一个只有你能盖的章… | OWNER (decided); 1.11c TERMS drop, prose reminder without English
分支 (branch) | 1.6a | 一条历史线的名字；新仓库自带一条，这门课里叫 main | OWNER (decided). Prose re-definitions to shorten: 1.8 l.112, 1.12 l.136 (bold), 1.13 l.265 (and its TERMS). 1.7 l.63 is a reminder: OK
工作区 (working tree) | 1.6b | 你正在改的那些文件… | OWNER; must add the disambiguation from 学习工作区 that 0.2c promised
暂存区 (staging area) | 1.6b | 准备拍进下一张快照的改动 | owner (5a 打包台 analogy present; 1.8b reuses it)
未跟踪 (untracked) | 1.6b | as listed | OWNER; 1.8a l.243 跟踪（track） gloss OK; 1.9b l.278 bold 已跟踪（tracked） → reminder
本地历史 (commit history) | 1.6b | as listed | owner
项目根目录 (project root) | 1.6c | — | DROP (duplicate of 1.5b 根目录); keep the prose as a reminder
差异 (diff) / 改动块 (hunk) | 1.7a | as listed | owner (1.13c/1.15a "改动清单" is descriptive: OK)
分页器 (pager) | 1.7b | 输出太长时，Git 交给它一屏一屏地显示的程序，这台电脑上是 less | OWNER; 1.14 l.30 attributes it to 1.1 → fix
丢弃修改 / 会丢数据的命令 | 1.8a | as listed | owner
取消暂存 (unstage) | 1.8b | as listed | owner
忽略文件 (.gitignore) | 1.9a | as listed | owner (5a 不拍名单 analogy and its break sentence present)
匹配模式 (pattern) | 1.9a | — | RENAME to 模式, referring back to 1.3b
全局忽略文件 / 源文件 / 密钥 / 接口 | 1.9a | as listed | owner (密钥 = secret; 1.11c deliberately uses 钥匙 for an SSH key: OK)
令牌 (token) | 1.9a | 一种通行证：程序拿着它就能代表你去用某个网站的服务；它代替密码，可以单独作废 (drop 临时) | OWNER (decided)
取消跟踪 / 作废密钥 / 推送保护 | 1.9b | as listed | owner
原子提交 (atomic commit) | 1.10a | as listed | owner
约定式提交 / 类型 / 范围 / 正文 / 破坏性变更 | 1.10b | as listed, but 提交信息 → 提交说明 in each plain text | owner
GitHub / 双重验证 / 验证器 App / 恢复码 / 密码管理器 | 1.11a | as listed | owner (0.4 l.339 forward clause for GitHub: OK)
源代码 / 包管理器 / 协议 | 1.11b | as listed | owner (协议 = protocol; 0.4's 累了协议 is the everyday sense: GLOSSARY lists only protocol)
PATH (PATH) | 1.11b | as listed | owner; add a clause saying it is not 0.2's 路径
令牌 (token) | 1.11b | — | DROP (decided)
隐私邮箱地址 (noreply email address) | 1.11c | as listed | owner
提交签名 (commit signing) | 1.11c | — | DROP (decided)
远程仓库 (remote) | 1.12b | as listed | OWNER (5a 另一本相册 analogy present); 0.2c forward clause OK
推送 (push) | 1.12b | as listed | OWNER; 1.9b l.470 bold forward definition → unbold clause
私有仓库 / 上游 | 1.12b | as listed | owner
克隆 / 恢复测试 | 1.12c | as listed | owner
许可证 / 版权 / MIT 许可证 | 1.13a | as listed | owner (1.5b l.235 forward clause OK)
上线 (deploy) | 1.13b | as listed | OWNER; add 也叫部署
分支 (branch) | 1.13b | — | DROP (decided)
静态网站 / GitHub Pages | 1.13b | as listed | owner
交付循环 (delivery loop) | 1.13c | as listed | owner
续行提示符 (continuation prompt) | 1.14a | as listed | owner (0.1b reads dquote> without naming it: OK)
最小可复现示例 | 1.14b | as listed | owner
发布说明 / 弃用 / 知识截止日期 | 1.14c | as listed | OWNER; 1.8 l.245 uses 弃用 earlier → add a clause gloss
验收 / 改动统计 | 1.15a | as listed | OWNER; 1.16b uses 验收 = stage exam → link the two senses
范围外的改动 / 尾注 | 1.15b | as listed | OWNER; 尾注 must point to 1.10b 脚注 (CC footer)
项目说明文件 | 1.15c | as listed | owner
作品集 | 1.16a | as listed | owner
讲解题 (explain-back question) | 1.16b | — | MOVE: owner 0.4c (first needed in gate-0); 1.16 drops it
考官 / 补考 | 1.16b | as listed | owner
回顾会 (Sprint Retrospective) | 1.16c | as listed | owner

=== LEDGER 1b: terms the prose introduces (bold or 中文（English）) that no TERMS lists ===
标签页 (tab) | 0.1c l.474 bold | owner 0.1c, add to GLOSSARY | 1.4a l.132 re-gloss → drop English
工作区信任 (Workspace Trust) | 0.1c l.457 bold | owner 0.1c | 1.4a reuses it: OK; 1.4 must reconcile the 0.1 dialog with its 旧教程提醒
项目文件夹 (project folder) | 0.1a l.38 | owner 0.1a | 0.2c l.631 and 1.15c l.527 (bold) → shorten
落脚点 | 0.1a l.104 bold | owner 0.1a | 0.4a l.64 bold re-definition → shorten
阶段 / 到期的复习 / 日志 / 小标题 | 0.1a bold | owner 0.1a | —
上课 / 干活 / 急救 | 0.1a l.126-132 | owner 0.1a | the 0.1 pointer 第 0.4 课细讲 is false; 1.15a uses 干活
报错 (error message) | used from 0.1; English gloss only in 1.14a l.17 | owner 0.1b (add the gloss) | 1.14 drops the English
参数 (argument) | 0.4a l.66 bold | register: argument = any word after the command | 0.4 must stop calling --write a 参数 instead of a 选项
对象 (operand) | 1.1a l.54-58 | owner 1.1a | 1.3a reuses it: OK
字节 (byte) / 目录 (directory) | 1.1a | owner 1.1a | 1.2a l.111 文件夹（directory） reminder OK
注释 (comment) | 1.3a l.90 bold | owner 1.3a, add to GLOSSARY | 0.1c "# 后面是说明", 1.9 and 1.12 "以 # 开头的行是给人看的说明" are consistent
Git | 0.2c clause, 1.6a l.28 bold | owner 1.6a, add to TERMS | —
提交说明 (commit message) | 0.3c l.431 clause | owner 1.6 (add to GLOSSARY) | 1.10 rival 提交信息 → change
HEAD | 1.6a l.211 clause | owner 1.6a | 1.8b l.415 clause OK; 1.7 old-tutorial box mention OK
快照 (snapshot) | 1.6a | owner 1.6a (word used inside 提交's definition, never glossed) | GLOSSARY may add it
版本 (revision) / 已修改 (modified) / 作者 / 日期 | 1.7 | owner 1.7 | —
占位写法 <file> | used 1.7 l.96/206, explained 1.8 l.114 | owner 1.7 | 1.8 becomes a reminder
跟踪 (track) | 1.8a l.243 | owner 1.8a | 1.9b l.278 bold → reminder
访达 (Finder) / 公开仓库 / ASVS | 1.9 | owner 1.9 | 1.11c and 1.13a reuse 公开仓库: OK
脚注 (CC footer) | 1.10b l.278 (quoted spec) | owner 1.10b | 1.15b 尾注 must link to it
钥匙串 (keyring) / 钥匙 (SSH key) / 通行密钥 (passkey) | 1.11 | owner 1.11 | kept distinct from 密钥 (secret): OK
GitHub CLI / 取 (fetch) / 推 (push) / origin | 1.12b | owner 1.12b | 1.13b l.375 repeats as a reminder: OK
页脚 (HTML footer) | 1.13c l.606 defined | owner 1.13c | 1.15a l.246 "页脚（footer）" reminder OK
CI / 相对链接 / GitHub Free | 1.13 | owner 1.13 | —
基线 / 五段式提问 | 1.14 | owner 1.14 | —
提案 | 1.15a | owner 1.15a | —
冷考 / 实操题 / 排错题 | 1.16b | owner 1.16b | —
Scrum / Sprint | 0.4c l.507 clause | owner 0.4c | 1.16c l.616 re-gloss (adds 冲刺) → say 0.4 提过

=== LEDGER 2: commands and options (first real appearance vs META new_commands) ===
python3 tools/course.py (status) | 0.1a l.82 | META 0.1a | OK
python3 tools/course.py hint / check | 0.1a | META 0.1a | OK
pwd / ls / clear (+ Ctrl+C key) | 0.1b | META 0.1b | OK
python3 <文件> / code <file> | 0.1c | META 0.1c | OK
python3 tools/course.py journal | 0.1c (收尾) | META 0.1c | OK
python3 tools/course.py scenario | 0.1c l.492 (recovery note) | META 0.1c, but also claimed by 0.2a, 0.3a and 0.4a | decided: 0.1 owns; DROP from 0.2a, 0.3a and 0.4a
scenario … --reset | printed by the tool from 0.2a on; first typed in 1.2b l.432 | never in META | acceptable (tool-printed)
cd, cd .., cd ~ | 0.2a (0.1c only mentions it) | META 0.2a | OK
ls --help | 0.2b l.356 (deliberate error) | none | OK as an error demo
man | 0.2b | META 0.2b | OK
ls -F | 0.2b l.418 (taught) | none | ADD to META 0.2b
mkdir | 0.2c l.482 (`mkdir ~/Developer`, with expansion make directory) | claimed new by 1.1a | DROP from 1.1a (0.2c's mkdir -p covers it)
mkdir -p | 0.2c | META 0.2c | OK
python3 tools/course.py doctor | 0.2c | META 0.2c | OK
python3 --version | 0.3b | META 0.3b | OK
python3 tools/course.py status --write | 0.4a (status -h appears only in tool output) | META 0.4a | OK
python3 tools/course.py review | 0.4b | META 0.4b | OK
zip -r -q / zip -T | 0.4c | META 0.4c | OK
python3 tools/course.py exam gate-0 [--grade] | 0.4c | META 0.4c; exam gate-1 [--grade] claimed again by 1.16b; gate-a named in 1.5 l.407 and gate-b in 1.10 l.469 without claims | DROP from 1.16b
touch / ls -l / ls -a | 1.1a | META 1.1a | OK (ls --all is an error demo)
cat / less / head | 1.1b | META 1.1b | OK
head -n | 1.1b l.368 (taught) | none | ADD to META 1.1b
tail -n | 1.1 想多了解 only | none | OK
cp / cp -R / mv | 1.2a | META 1.2a | OK (cp -r mentioned)
rm / rm -i / rm -r / rmdir | 1.2b | META 1.2b | OK
grep / -n / -i / -r (-rn combined) | 1.3a | META 1.3a | OK (-E/-F in a box)
find . -name | 1.3b | META 1.3b | OK
code . / open | 1.4a | META 1.4a | OK
(1.5: no new commands) | — | META [] | OK
git --version | 1.6a | META 1.6a; claimed again by 1.14b | decided: DROP from 1.14b
git config (--global) | 1.6a | META 1.6a 'git config'; 1.9a claims 'git config get' | 1.6 should teach git config get/set; then 1.9 drops 'git config get'. --replace-all (trouble box l.254) → set --all
git commit -m | 1.6a | META 1.6a | OK
git log --oneline | 1.6a | META 1.6a | OK
git init / git status / git add | 1.6b | META 1.6b | OK (git commit -a is mention-only: "不要用")
vi | 1.6a trouble box (how to exit only) | META 1.14a | OK (typed first in 1.14a)
git diff / git diff --staged | 1.7a | META 1.7a | OK
git diff <文件名> | 1.7a l.153 (git diff style.cs, error demo); typed 1.8b l.337 | claimed by 1.15b | DROP from 1.15b
git show / git log --stat | 1.7b | META 1.7b | OK
git restore / git restore --staged | 1.8a / 1.8b | META | OK
git status --ignored / git check-ignore -v | 1.9a | META 1.9a | OK
git ls-files / git rm --cached / git rm -r --cached | 1.9b | META 1.9b | OK
git show --stat | 1.10a | META 1.10a | OK
git commit -m … -m … | 1.10b l.370 | META 1.10b; claimed again by 1.15b | decided: DROP from 1.15b
which / brew install / gh --version / gh auth login / gh auth status | 1.11b | META 1.11b | OK
git log --format | 1.11c | META 1.11c | OK
git log -1 | 1.11c l.420 (taught) | not in 1.11c; claimed by 1.15b | ADD to 1.11c, DROP from 1.15b
ssh-keygen -t -C / git config gpg.format / user.signingkey / --unset | 1.11c 选做 box | none | OK (optional); --unset → unset
gh config set | 1.11 想多了解 | none | OK
git add . | 1.12a (mentioned in 1.6 l.493 and 1.9 l.102) | META 1.12a | OK
gh repo create --private --source --remote --push | 1.12b | META 1.12b | OK
git remote -v / git push / git grep --untracked -n -i -E | 1.12b | META 1.12b | OK (git push origin master is a deliberate error)
gh repo view --json | 1.12 想多了解 | none | OK
git clone / diff -r -q (-x) / rm -rf | 1.12c | META 1.12c | OK (-x and -f explained)
gh repo create --public / gh browse --settings | 1.13b | META 1.13b | OK
git <命令> -h / sw_vers -productVersion | 1.14b | META 1.14b | OK
python3 tools/course.py fresh | 1.14c | META 1.14c | OK
echo | 1.14 想多了解 | none | OK
git diff --stat | 1.15a | META 1.15a | OK
(1.16: no genuinely new commands) | — | META 1.16b lists exam gate-1 | DROP
```


## 11. One wording for the recurring parts (from the audit; section 3 above wins where they differ)

```text
TABLE A. ONE canonical wording per recurring element (proposed; every finding above applies these)

A1 Save point, any station except the last (the tool prints the same sentence in check.py: 「下次可以对导师说“从 {next} 继续”」):
> **存档点 1.6a**：到这里可以安全停下。下次可以对导师说“从 1.6b 继续”。
A2 Save point, last station of a lesson:
> **存档点 1.6c**：到这里可以安全停下。下次可以对导师说“从 1.6 的收尾继续”。
A3 Mid-station save point before a gate that sits inside a lesson (0.4c, 1.16b):
> **中途存档点**：<做完了什么>，到这里可以安全停下。下次可以对导师说“做小关卡 gate-0”。
A4 Last line of 收尾: 「三件都做完，这一课就完成了。下次可以对导师说“从 <下一课课号> 开始”。」. Where a gate comes next (1.5 → gate-a, 1.10 → gate-b): 「…它是单独的一段时间，开考时工具会打印题数和预计用时。下次可以对导师说“做小关卡 gate-a”。」
A5 Hint and check, the last lines of every 自己做, in this order:
- 提示：`python3 tools/course.py hint 1.6a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.6a`
A6 收尾 list:
## 收尾（约 N 分钟）
1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.6`
2. 用自己的话把本课行规 GIT-01、GIT-02 各写一句到 `notes/my-rules.md`（`code notes/my-rules.md`，写完按 ⌘S 保存）
3. 一句话日志：`python3 tools/course.py journal`
4. （1.12 起每课都有）把今天的笔记和日志备份到云端：按第 1.12 课收尾的那一组命令做（git status → git grep --untracked … → git add . → git commit -m "docs: 记下第 <课号> 课的行规和日志" → git push → git status）
A7 Erratum line, exactly once, directly after the first marked step: 「和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。」 (full-width quotes, not inside a blockquote, marks not in backticks)
A8 Optional material: 「> **想多了解（可跳过）：<小标题>**」. Not 选做, 可选, 选读 or 可以跳过.
A9 First aid: 「对导师说“急救：<一句话说现象>”」. Never a bare “急救”.
A10 Rule summary in lesson.md: a table 「| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |」, then 「完整卡片在本课文件夹的 `rules.md`。」 约束力 is written as on the card: 必须/推荐/参考（适用范围：…）.
A11 Returning to the course folder, lessons 0.3-1.12, first occurrence per lesson: 「（第 0.2 课选了“先留在原处”的，这一课里每条 `cd ~/Developer/Engineering` 都换成 `cd ~/Desktop/Code/Engineering`。）」. From 1.13 on the text may assume ~/Developer/Engineering, because 1.12 lines 41-47 make the learner move.
A12 Names: 学习工作区 is the course folder; bare 工作区 means only Git's working tree, from 1.6 on. 学习仓库 is the course folder once it is a repository (1.12+). 练习场 is ~/Developer/playground/ and 练习场景 one scenario folder in it. my-site / 你的网站 is ~/Developer/my-site. Never 课程文件夹 or 练习文件夹.
A13 Keys: 0.1 introduces 「Cmd+S（键帽上的 ⌘；课文以后写 ⌘S）」. After that ⌘S / ⌘R / ⇧⌘P, as 1.4 line 9 defines them.
A14 Gate naming: 「小关卡 gate-0 / gate-a / gate-b」 and 「阶段验收 gate-1」. The resume sentence is always 「做小关卡 <gate>」, as the decision fixes it.

TABLE B. Departures per lesson (SP = save points; LSP = last-station save point; END = next-step line at end of 收尾; HC = hint/check form; ER = erratum line; OPT = optional label; WS = workspace cd for the old place; BK = backup push in 收尾)
0.1  SP ASCII, no 可以 | LSP "从 0.2a 继续" | END missing | HC 卡住了： | ER ASCII | WS n/a
0.2  SP no 可以 | LSP "从 0.3 开始" | END missing | HC ok | ER 3x | names 课程文件夹 x16 | WS sentence for option B missing
0.3  SP no 可以 | LSP "做 0.3 的收尾" | END missing | HC 检查 before 提示 | ER ok | OPT ok | WS x6 hard-coded
0.4  SP ASCII | LSP "从 1.1 开始", mid "从 0.4c 的小关卡继续" | END "下一课是第 1.1 课" | HC 卡住了要一条提示 | ER ASCII, placed after the gate | WS only line 439
1.1  SP no 可以 | LSP "从本课行规继续" | END missing | HC prose | ER ok | WS x5
1.2  SP no 可以 | LSP ok | END missing | HC one line | ER ok | WS x6
1.3  SP no 可以 | LSP "下次从本课的「收尾」接着做" | END missing | HC 卡住了： | OPT 选读/可以跳过 | WS x5 | TERM-01 约束力 contradicts 1.1
1.4  SP no 可以 | LSP "从 1.4 收尾继续" | END missing | HC one line | WS x7
1.5  SP ASCII | LSP "从收尾继续" | END gate-a sentence not canonical | HC 卡住了： | ER ASCII | OPT 可以跳过 | WS x4
1.6  SP ASCII | LSP "下一课是 1.7，对导师说"开始上课"" | END missing | HC ok | ER ASCII | first aid bare 急救 | WS x7
1.7  SP ASCII | LSP "从 1.8 继续" | END missing | HC ok | ER ASCII | OPT 可以跳过 | WS x4
1.8  SP no 可以 | LSP "“开始上课”，从本课的收尾接着做" | END missing | HC 卡住了要提示 | ER none (no marks: ok) | WS x7
1.9  SP no 可以 | LSP "从 1.9 课的收尾继续" | END missing | HC one line | WS x3
1.10 SP ASCII | LSP "从 1.10 收尾继续" | END gate-b sentence not canonical | HC - 卡住了： | ER ASCII | WS x3
1.11 SP ASCII | LSP "从 1.11 收尾继续" | END missing | HC 卡住了： | ER ASCII in blockquote | OPT 选做 | marks in backticks | WS x3
1.12 SP no 可以 | LSP "从 1.12 收尾继续" | END missing | HC 卡住了： | ER ASCII | OPT 可以跳过 | WS L37 comes before the stay check | BK defines the routine | bare 工作区 x6
1.13 SP no 可以 | LSP "从第 1.14 课开始" | END missing | HC one line | ER ASCII | 开始之前 before 先想一想 | BK ok
1.14 SP ASCII | LSP "从 1.15 继续" | END missing | HC one line | ER ASCII | no 补全 in station c | BK missing
1.15 SP ASCII | LSP "从收尾继续" | END missing | HC one line | ER ASCII | OPT 可选/可以跳过 | BK missing
1.16 SP no 可以 | LSP "准备阶段 2" | END "阶段 1 到这里结束" | HC ok | ER ASCII | no save point before the exam | BK departs (git add notes journal, no secret scan)

TABLE C. Decision ledger checked mechanically (ast parse of META/TERMS)
new_commands declared in more than one lesson: "python3 tools/course.py scenario" 0.1c (owner), 0.2a, 0.3a, 0.4a | "git --version" 1.6a (owner), 1.14b | "git commit -m … -m …" 1.10b (owner), 1.15b.
TERMS declared in more than one lesson: 路径 0.1a/0.2a (owner 0.2) | 递归 1.2a/1.3a (owner 1.2) | 提交签名 1.6a/1.11c (owner 1.6) | 分支 1.6a/1.13b (owner 1.6) | 令牌 1.9a/1.11b (owner 1.9).
S6 subject "style: 调大标题的字号" still present: 1.13 lesson.md 21, 74; 1.16 lesson.md 158, 357, 403. 1.10 lesson.py line 467 already uses "feat: 调大标题的字号".

TABLE D. G6 marks against META.unverified_steps (count of marks / unverified entries / erratum lines)
0.1 12/8/1 | 0.2 5/4/3 | 0.3 4/4/1 | 0.4 3/5/1 (the line comes late; lines 491 and 260 are unmarked) | 1.1 3/3/1 | 1.2 2/2/1 | 1.3 3/3/1 (wrong class in 收尾) | 1.4 12/10/1 | 1.5 5/4/1 | 1.6 4/4/1 (1.6c unmarked) | 1.7 2/2/1 | 1.8 0/0/0 | 1.9 3/3/1 | 1.10 1/2/1 (自己做 VS Code unmarked) | 1.11 13/10/1 | 1.12 4/4/1 | 1.13 11/10/1 | 1.14 6/6/1 | 1.15 4/4/1 | 1.16 7/5/1.

TABLE E. G4 旧教程提醒 boxes without a since-when: 0.3 lesson.md 514; 1.10 lesson.md 307; 1.11 lesson.md 92. In rules.md: 1.5 DOC-01 line 20 and 1.11 ACC-01 line 16 (single-lesson cards, left to their testers).
```


## Rulings of 2026-11-20

Taken by the orchestrator on 2026-11-20 for the acceptance of stages 0-1 and the tutor tests (the orchestrator's notes of that day; where those notes and the sections above differ, the notes win). They are not to be re-opened: a finding that only repeats one of them is not a finding. The wording is the notes' own, with a short label in bold before each ruling; the last sentences of ruling 2 described the run of that morning and are put in the past here.

1. **G5a, what counts as prose.** "Chinese characters" in plan G5a means Han characters. Punctuation, digits, Latin letters and inline code are not counted: the rate of 180 characters a minute is about half of an ordinary adult's reading speed and already allows for them. A stated number of minutes stands when a recount by this rule gives the same 5-minute step. A difference of less than one minute between two counts is never a finding, and nobody trims or relabels a station for it. Report a station only when your own count by this rule differs from the stated minutes by more than 5.
2. **G5a, the closing section (收尾).** Its minutes are calculated like a station's, without the 3 minutes for a failed attempt, and rounded up to the next multiple of 5. The fixed 5 or 10 minutes of section 1 above are withdrawn. On 2026-11-20 one agent recalculated the closing of all 20 lessons (the 「## 收尾（约 N 分钟）」 heading, the sum in the lesson header, and the hours that follow from them in `README.md`, `ROADMAP.md`, `docs/roadmap/sources.md` and the two stage pages); during that run nobody else reported or changed closing minutes, header sums or hours.

   **How the closing is counted** (settled on 2026-11-20 by the agents that recalculated the closing and checked the recalculation):
   - Every line the learner reads at the terminal counts, at 10 seconds a line, whether or not the lesson prints it. The journal command always prints 7 lines (5 prompts and 2 result lines).
   - A check's printed result is inside its minute: the whole-lesson check is one check run of 1 minute, reading its result included; once the stations have passed it asks no question.
   - A rule note is its command (`code notes/my-rules.md`), one GUI sequence and 40 composed characters per rule card; the journal is its command, about 25 composed characters and its 7 lines; from lesson 1.13 on the backup is the commands, the output lines and the commit message of lesson 1.12's group.
   - There is no allowance for a failed attempt. Add up and round up to the next multiple of 5.

   Note 15 of [`../lesson-template.md`](../lesson-template.md) and the hours row of `docs/roadmap/sources.md` say the same. Result, as `python3 tools/dev/build_reference.py --check` prints it after the recalculation: stage 0 about 8.5 hours (stations 375, closing 50, gate 31 minutes), stage 1 about 36.5 hours (stations 1520, closing 255, gates 139 minutes), each with 15% added for reviews and rounded to the half hour.
3. **Lesson 1.13, the learner who cannot use GitHub Pages.** Checks 1.13b and 1.13c stay open and status keeps pointing at 1.13b; the lesson's box and playbook §5 tell the learner to say “从 1.14 开始”. Accepted as a known issue (the tool is frozen).
4. **说明书.** Used alone it means a command's man page (lesson 0.2b owns the term). Lesson 1.5 calls the README 「项目的说明书」 in the everyday sense. `GLOSSARY.md` names the pair among the confusable words. No further change.
5. **Station 1.14a** has five broken situations, not the eight of plan section 4; the other three are review items. Accepted departure from the plan.
6. **The course folder in a first-aid sentence.** A lesson's first-aid sentence that means the course folder says 学习工作区 (“急救：终端不在学习工作区”); the playbook recognises the older wording.
7. **Used before defined.** Used-before-defined entries that the last blind tester himself called acceptable, and that the lesson's fixer left with a reason, stay as they are.
