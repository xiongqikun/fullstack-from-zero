# Lesson template (plan I1, annotated)

For whoever writes a lesson of this course: a builder agent, a fixer, or a human. This file turns plan I1 into a template that already carries the binding decisions of 2026-11-19 (the repair round's `COMMON.md`, sections 2, 3 and 7). Where an older text differs (the plan's own I1 sample, the early drafts of the 20 lessons), **this file wins for new lessons**; where this file and the plan's section 1 differ, the plan wins and this file is out of date: fix it and log the fix in `CHANGELOG.md`.

Not repeated here, only linked:

- the lesson module `lesson.py`: [`tool-api.md`](tool-api.md) sections 1-12 and 15-16, with the worked module in [`example-lesson/lesson.py`](example-lesson/lesson.py);
- the rule-card format `rules.md`: plan I2 and [`tool-api.md`](tool-api.md) section 13, with the card [`example-lesson/rules.md`](example-lesson/rules.md);
- what "done" means: [`definition-of-done.md`](definition-of-done.md).
- a short lesson text written in these forms: [`example-lesson/lesson.md`](example-lesson/lesson.md) (lesson 99.1; copied to `stages/99-example/01-notes-repo/`, `validate 99.1` gives no warning, checked 2026-11-20).

## 1. The skeleton

Copy everything inside the fence. Angle brackets are placeholders; the numbers in 【】 point to the notes in section 2 and are deleted when you write.

````markdown
# <课号> <标题>【1】

> **用时** <N> 站，约 <X> 分钟 ｜ **前置** <课号> ｜ **核实** <YYYY-MM-DD> · <工具> <版本> · macOS <版本>【2】
> **学完你能** <两到三件看得见的事>
> **本课行规** <规则编号>、<规则编号>（见文末）

## 先想一想

<一个靠生活经验就能答的问题，2 分钟；说清楚在第几站回头对答案>【3】

## 第 1 站：<标题>（约 <分钟> 分钟）【4】

### 概念

<一个新概念。术语第一次出现写成 中文（English），后面跟一句大白话。>【5】
<类比一句，紧接着一句「这个类比在哪里不成立：……」。>

> **想多了解（可跳过）：<小标题>**【6】
> <第二个概念、背景、历史：不算进用时>

### 跟我做

#### 1. <小标题>

<每两三条命令之前：先猜一猜，它会输出什么？>【7】

```zsh
<学习者要敲的命令>
```

你应该看到：

```text
<在模拟家目录里真实运行得到的输出；会不一样的地方标「你的会不一样」>
```

> 读懂这句：<英文输出的大白话>【8】

#### 2. <故意出一次错>【9】

```zsh
<会出错的命令>
```

你应该看到：

```text
<真实的报错>
```

> 读懂这句：……

用“报错三问”读一遍：

- **谁在报错？** ……
- **关键词是什么？** ……
- **我刚才敲了什么？** ……

#### 3. <图形界面里的一步>

〔对照文档，界面可能不同〕<按官方文档写的步骤；界面文字照英文原样，括号里给中文意思>【10】

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

> **旧教程提醒**：以前……；现在……（自 <版本或年份> 起）【11】

### 补全

<半成品：给出步骤骨架，留空让学习者填>

### 自己做

目标：<只给目标；情境和「跟我做」表面上不一样>【12】

- 提示：`python3 tools/course.py hint <站号>`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check <站号>`

> **存档点 <站号>**：到这里可以安全停下。下次可以对导师说“从 <下一站站号> 继续”。【13】

## 第 2 站：<标题>（约 <分钟> 分钟）

<同上>

> **存档点 <最后一站站号>**：到这里可以安全停下。下次可以对导师说“从 <课号> 的收尾继续”。

## 本课行规【14】

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| <编号> | <一句话> | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | <七种标签之一> | <名称、版本或日期> | <YYYY-MM-DD> |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 <算出的分钟> 分钟）【15】

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check <课号>`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「<编号> <卡片标题>」下面用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。

都做完，这一课就完成了。下次可以对导师说“从 <下一课课号> 开始”。【16】

## 想多了解

下面的内容都可以跳过，不算进本课的时间。

- <链接一>（中文）
- <链接二>（English）
````

## 2. Notes

Each note names the rule it comes from. "COMMON" is the repair round's binding decisions of 2026-11-19 (kept in [`build-kit/COMMON.md`](build-kit/COMMON.md), with the rulings of 2026-11-20 at its end; their content is folded into this file and into [`definition-of-done.md`](definition-of-done.md)).

1. **Title.** `# <课号> <标题>`, the title exactly as in `tools/courselib/syllabus.py` and the stage page. Lesson ids `<stage>.<n>`, station ids lesson id plus a letter, folders kebab-case (plan G12).
2. **Header.** 「**用时** N 站，约 X 分钟」, where X is the sum of the stations plus the 收尾 (COMMON §1). The tools named after 核实 are the ones in `META["verified"]["tools"]`, so that `fresh` can find the lesson when one of them changes.
3. **先想一想.** Everyday experience only; no term the lesson has not introduced.
4. **Station minutes.** Calculated with plan G5a, never fitted to a target: prose at 180 characters per minute, 10 seconds per output line to read (at most 2 minutes per block), 40 seconds per typed command (70 when longer than 40 characters or with quotes or a pipe), 15 characters per minute of Chinese the learner composes, 1 minute per GUI sequence, 1 minute plus 45 seconds per question for each check run, 2 minutes per exchange with the tutor, plus 3 minutes for one failed attempt; round up to a multiple of 5. Allowed 15-40, target 20-25, `validate` warns above 30. The number in the heading equals `META["stations"][i]["minutes"]` (`validate` warns otherwise). A gate is never part of a station: it is its own sitting behind a 中途存档点 (COMMON §3).
5. **One new concept per station** (plan G5, G5a). A second concept becomes a one-clause gloss, a 想多了解 box, or goes to the lesson that owns it. Terms: the lesson where the learner first needs a word owns it (TERMS `first` there); an earlier lesson may forward-gloss it in one unbolded clause ending 「第 X 课细讲」 and never lists it in TERMS; a later lesson repeats at most a one-clause reminder, without bold and without （English） (COMMON §5). Analogies and Chinese renderings come from the register (plan section 5a, `docs/curriculum-spine.md` section 5); do not invent rivals.
6. **Optional material.** Exactly 「> **想多了解（可跳过）：<小标题>**」 inside a station, or the closing 「## 想多了解」 whose first line says everything in it can be skipped. Never 选做, 可选, 选读 or 可以跳过. Not counted in the minutes.
7. **Prediction.** Every two or three commands, ask the learner to predict the output. Git lessons pair every worked step with `git status` or `git log --oneline` and the question 「先说出执行后图会怎么变」, and reuse the four-area picture of plan section 5a unchanged.
8. **English output** is shown verbatim and followed by 「> 读懂这句：」 (plan G14). Each command gets its expansion once as a memory hook (`pwd` = print working directory = 打印当前所在目录). Pasted output is real output from a simulation home (plan G8): the home folder is `~`, the prompt is `你的用户名@你的电脑名 文件夹 %`, a name is 「你的名字」, an e-mail address is `you@example.com`, and output that differs on the learner's machine (dates, hashes, sizes, number of commits) is marked 「你的会不一样」 (COMMON §3, plan G10). Do not edit what the simulation printed, time zones in `Date:` lines included: mark it instead.
9. **One deliberate error per station**, read with the 报错三问 (谁在报错？关键词是什么？我刚才敲了什么？).
10. **Verification marks** (plan G6). A step nobody could execute is marked 〔对照文档，界面可能不同〕 (checked against official documentation today) or 〔建课时无法验证〕, never inside backticks, and listed in `META["unverified_steps"]`. Directly after the **first** marked step, once per lesson and not inside a blockquote: 「和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。」. UI labels are quoted in English (the learner's system language) with a Chinese gloss (plan G7).
11. **旧教程提醒** (plan G4): 「> **旧教程提醒**：以前……；现在……（自 <版本或年份> 起）」. Every box says since when; a box without a date is not done (COMMON §3).
12. **自己做** has exactly one exercise and one check (plan G5); the last two lines are the hint line and the check line, in this order and in exactly this wording (COMMON §3).
13. **Save points** (COMMON §3). After a station that is not the last: 「从 <下一站> 继续」. After the last station: 「从 <课号> 的收尾继续」. Before a gate inside a lesson: 「> **中途存档点**：<做完了什么>，到这里可以安全停下。下次可以对导师说“做小关卡 <gate>”。」 Nothing else is added to these lines, and no lesson invents another sentence for talking to the tutor: the fixed sentences (开始上课, 急救：<现象>, 干活：<事>, 回到上课, 课文对不上 and the others) are listed in the tutor rules `CLAUDE.md`. A situation-specific first-aid sentence has the form “急救：……” and is reported to the writer of the tutor rules.
14. **Rule summary.** At most two new rule cards per lesson (plan G5). The cells 约束力 and 规则类型 are copied from the card. 约束力 is always a level word with a scope, also for the course (「必须（适用范围：本课程）；推荐（适用范围：所有项目）」). 规则类型 is one of the seven labels of plan G3 chosen by the seven-step procedure in `STANDARDS.md` section 2; it never changes with the situation, only 约束力 does (COMMON §7). A card is introduced only after the learner has felt the problem it prevents.
15. **收尾.** Items 1-3 always, in this order and wording. Item 2 names every rule id of the lesson with its card title exactly as in `rules.md` (a lesson without a new rule drops it). Item 4 from lesson 1.12 on, in every later lesson and stage. The minutes of the 收尾 are calculated with plan G5a like a station's, without the 3 minutes for a failed attempt, and rounded up to a multiple of 5 (ruling of 2026-11-20; the fixed 5 or 10 minutes are withdrawn): the whole-lesson check is one check run (1 minute, which includes reading its result, printed in the lesson or not; it asks no question once the stations have passed), a rule note is its command, one GUI sequence and 40 composed characters per rule card, the journal is its command, about 25 composed characters and the 7 lines it prints (5 prompts, 2 result lines: every output line the learner reads counts, whether or not the lesson shows it), and from lesson 1.13 on the backup is the commands, output lines and commit message of lesson 1.12's group. A lesson may add its own steps after item 4, numbered on.
16. **Last line.** 「都做完，这一课就完成了。下次可以对导师说“从 <下一课> 开始”。」 Where a gate comes next: 「都做完，这一课就完成了。下一步是小关卡 <gate>：它是单独的一段时间，开考时工具会打印题数和预计用时。下次可以对导师说“做小关卡 <gate>”。」

Further fixed forms (COMMON §3): the course folder is 学习工作区 (never 课程文件夹, 练习文件夹, or a bare 工作区, which from lesson 1.6 on is Git's working tree); returning to it is always 「回到学习工作区：`cd ~/Developer/fullstack-from-zero`」, which works for every learner because of the entrance made in lesson 0.2; keys are written as the menus show them (⌘S, ⇧⌘P), each explained at first use, while Ctrl+C, Tab, Esc, 回车（Enter） and 空格 are written as words; Chinese quotation marks are “ ”.

**Code fences.** Commands the learner types go in a ```` ```zsh ```` fence, outputs in ```` ```text ````. Reason: the learner's shell is zsh, lesson 1.5 teaches ```` ```zsh ```` as the label for terminal commands, and GitHub's Linguist lists both `zsh` and `bash` as aliases of the same language "Shell" (`lib/linguist/languages.yml`, read 2026-11-19), so the highlighting is identical. Since the repair round no lesson of stages 0-1 uses ```` ```bash ```` (checked 2026-11-20: `grep -l '```bash' stages/*/*/lesson.md` finds none).

**Voice** (plan G2): plain Chinese, second person 「你」, short sentences, one idea per paragraph, full-width punctuation in prose and half-width inside code, one space between Chinese and Latin letters or digits. Never 很简单, 显然, 只需要; no exclamation marks, no emoji in prose (tool output may show ✅ ❌ ⚠️); never talk down; give a reason, and a choice where the learner has one.

## 3. Worked example: lesson 1.2

Lesson 1.2 「终端：复制、移动、删除」 (`stages/01-foundations/02-copy-move-delete/`) is the worked example. Its first blind test found no blocker and the fewest problems of the 20 lessons (2026-11-19), and it shows the three things that are hardest to get right: an analogy that is honest about where it stops, an error that the learner provokes and reads, and a rule that arrives only after the learner has felt why it exists. Its save points, hint and check lines and 收尾 were written before the forms of section 1 were fixed: copy those from the skeleton above, not from the lesson.

**Excerpt 1: a concept with its analogy and where the analogy breaks** (station b, 概念).

```markdown
**终端里没有废纸篓。** 用 `rm` 删掉的文件立刻就没了，不进废纸篓，没有“撤销”，删完一句话也不说。

它像碎纸机：塞进去就碎了。这个比方在一点上不成立：碎纸机只碎你亲手塞进去的那几张；`rm` 配上通配符，一次能删掉一整批名字，其中可能有你没看见的。
```

Good because: the fact comes first and in plain words; the analogy is everyday; the break sentence is not a ritual, it carries the lesson's real warning (wildcards).

**Excerpt 2: a deliberate error read with the 报错三问** (station a, step 3).

```markdown
cp: recipes is a directory (not copied).

> 读懂这句：cp 说，recipes 是一个文件夹（directory），所以没有复制。

- **谁在报错？** 开头是 `cp:`，是复制命令自己。
- **关键词是什么？** `is a directory`、`not copied`：它是文件夹，没复制。
- **我刚才敲了什么？** 让 `cp` 复制文件夹，却没告诉它“连同里面的东西”。
```

Good because: the learner makes the mistake a beginner would make anyway, with the real message from the simulation; each of the three answers is short and points at a word on the screen; the fix (`cp -R`) follows directly, with a 旧教程提醒 about `cp -r` that says since when and where it was checked.

**Excerpt 3: the rule after the problem** (station b, steps 1-2).

```markdown
rm: my: No such file or directory
rm: list.txt: No such file or directory

这次只是报错。可如果这里碰巧有个 `list.txt`，它已经没了。

> **TERM-02 删除前先看清要删什么**：先用 `ls` 加上和删除时一模一样的名字或通配符看一遍，确认列出来的正是要删的，再把 `ls` 换成 `rm`。
```

Good because: the learner first watches a space split one name into two and sees what that could have destroyed; only then does the rule appear, as one sentence that can be followed literally, with its two labels and a pointer to the full card (`rules.md`), whose 谁说的 names the MDN page and the Apple guide with dates.
