# Brief: beginner-programming-pedagogy

Topic: how to teach programming (Python) to an adult absolute beginner when an AI assistant is always available.
Date of research: 2026-11-19. Audience: the agents who will design and write Stage 2 ("programming fundamentals with Python") and configure the AI tutor.

Tags: **[local]** = I ran it on this machine today. **[source: URL]** = I read it at that URL today (if marked "secondary", I only saw an abstract, a search summary or a third-party description). **[memory]** = not verified today. Opinions are marked "judgment".

---

## 0. What I verified and how

| What | How | Result |
|---|---|---|
| Toolchain | `uv --version`, `python3 --version`, `uv run pytest --version`, `ruff --version` | uv 0.13.5, CPython 3.14.9 (uv-managed; `python` and `python3` both resolve to it), pytest 9.2.0 (resolved today from PyPI), ruff 0.17.2 [local] |
| Beginner error messages | 30 typical mistakes run under 3.14.9 (`errors-demo/run_snippets.py`) | real messages recorded in section 6 [local] |
| Exercise format | built `prototype/` (uv project + pytest + `learn.py` runner + self-check + tracer), simulated a learner session with wrong and right answers | works end to end; pitfalls found are in section 8 [local] |
| Pedagogy literature | WebFetch of primary pages; five PDFs (CS50 Duck, Parsons review, Xie 2019, Michaeli 2019, PRIMM seminar paper) text-extracted locally with pypdf | section 2-3 |
| Curricula | fetched each curriculum's own site | section 4 |
| Could NOT verify | interactive REPL (sandbox has no pty), VS Code debugger, Claude Code hooks, iCloud effects, several paywalled papers (PMC / Nature / Springer / ACM returned 403 or bot walls) | listed in section 13 |

Scratch layout (all under this directory): `brief.md`, `prototype/` (the working exercise format), `errors-demo/`, `misc-checks/`, `ruff-demo/`, `downloads/` (PDF text extracts), `scripts/`.

---

## 1. Decision summary

1. **Performance is not learning.** Every well-controlled 2024-2026 study says the same thing: AI help raises task scores during practice and does not raise (often lowers) what the learner can do alone afterwards. The course must therefore measure progress with **unassisted checkpoints**, not with "exercises passed while the tutor was available". (section 3)
2. **Guardrails change the outcome.** Hint-first tutors (no direct answers) largely remove the harm; unrestricted answer-giving creates it. So "coach, not ghost-writer" is the right product decision, but it has to be enforced by design (hint ladder, runner, hooks), not just by a sentence in a prompt. (sections 3, 9)
3. **Read before write.** Sequence inside every lesson: predict, run, investigate (trace), modify, make. Writing from a blank file is the last step, not the first. (section 2)
4. **"Make the failing tests pass" alone is the wrong exercise diet.** Add predict, trace-table, Parsons, fix-the-bug and explain-in-plain-Chinese exercises. All of these can be auto-checked locally with only uv + pytest; the prototype proves it. (section 8)
5. **Teach one explicit notional machine** (names stuck on values; one sheet of scratch paper per function call) and target the known misconception list with diagnostic feedback. (sections 2.4, 2.7)
6. **Teach debugging explicitly, early, as a procedure.** (section 2.8)
7. **Mastery gates** per unit (about 80 percent, retake with variants) because later lessons build strictly on earlier ones. (section 2.9)
8. Stage 2 should take roughly **80-130 hours** (judgment, anchored on CS50P = 10 weeks and Helsinki's intro course = 5 ECTS); 25 lessons is fine as a skeleton if each lesson is 3-5 hours including exercises and projects.
9. The built-in Claude Code "Learning" output style is designed for people who can already code (Claude writes most of it and leaves a few lines). For exercise sessions write a **custom style** and block tutor edits to exercise files with a hook. (section 9)
10. Python 3.15 is the current stable release (9 Oct 2026). Staying on 3.14 is fine; pin it and know the differences. (section 5)

---

## 2. Evidence and techniques

### 2.1 PRIMM (Predict, Run, Investigate, Modify, Make) - Sue Sentance
- Five stages: predict what a short teacher-written program does; run it to check (no typing-in of code, so attention stays on behaviour); investigate through tracing, annotating, Parsons puzzles, debugging; modify in growing steps; make a new program reusing the ideas. Phases can repeat. [source: https://primmportal.com/]
- Five principles: read code before writing it; talk about programs; focus on comprehension (Block Model); start from existing starter programs so the learner is not yet responsible for failures; move ownership gradually from "theirs" to "mine" (builds on Use-Modify-Create). [source: https://www.raspberrypi.org/app/uploads/2022/08/Teaching_Programming_with_PRIMM-1.pdf]
- Evidence: quasi-experimental study (non-equivalent control group, post-test), about 500 pupils aged 11-14, ten lessons over 8-12 weeks covering sequence, selection, iteration in Python; statistically significant post-test difference in favour of PRIMM; nine teacher interviews valued structure and collaboration. Journal: Computer Science Education 29(2-3), 2019, DOI 10.1080/08993408.2019.1608781. [source: same PDF; https://api.crossref.org/works/10.1080/08993408.2019.1608781]
- Caveat: schoolchildren in classrooms with a teacher, not a solo adult; effect size not seen today. Transfer to our setting is plausible, not proven (judgment).
- Use here: PRIMM is the lesson skeleton. The "talk" principle maps to explaining code to the tutor in plain Chinese.

### 2.2 Worked examples, subgoal labels, faded examples
- Step-by-step worked examples whose steps carry names (subgoal labels) help novices see that different-looking problems share a structure; reported gains in performance. [source: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006023 (tip 6, citing Margulieux, Morrison)]
- Semester-long study, 265 CS1 students: subgoal-labelled worked examples improved quiz scores (within a week of learning), not exam means, but lowered exam variance and the number of students who failed or withdrew; biggest benefit for students at risk. [source: search summary of DOI 10.1186/s40594-020-00222-7, secondary]
- Faded examples: each successive problem removes some scaffolding until the learner solves a full one. [source: https://teachtogether.tech/en/index.html]
- Worked examples help novices and stop helping (then hurt) as expertise grows (expertise-reversal), so fade them. [source: search summary of Kirschner, Sweller, Clark 2006, secondary] [memory for the Kalyuga attribution]
- Use here: every new construct gets one worked example with 3-5 labelled steps written as comments (Chinese label + English term), then a faded copy with blanks, then an independent problem.

### 2.3 Parsons problems (reorder scrambled lines)
- Systematic review (ITiCSE 2022 working group, Ericson, Denny, Prather et al.): 22 papers report learning gains across basic, faded, adaptive and distractor variants (27-736 participants, mostly Python and Java); nine papers on cognitive load find it lower than writing equivalent code; evidence quality rated high. Only two randomized studies compare directly with writing code. Novices benefit most; more advanced students gain more from fix/write tasks; some learners dislike them; distractor evidence is mixed (one study: a suboptimal-path distractor hurt efficiency). [source: https://acris.aalto.fi/ws/portalfiles/portal/131069230/Parsons_Problems_and_Beyond_-_Systematic_Literature_Review_and_Empirical_Study_Designs_.pdf, text extracted locally]
- Parsons problems take less time than writing code for an equivalent learning outcome (Ericson 2017), and learners attempt them more readily than nearby multiple-choice questions. [source: https://teachtogether.tech/en/index.html; PLOS tip 10]
- Use here: one Parsons per lesson in units A-C, fading out in D-E; also the format of hint level 4 ("here are the lines of a solution, scrambled").

### 2.4 Tracing ("be the interpreter") and the notional machine
- Multi-national study (Lister et al., ITiCSE 2004): many novices are weak at reading and tracing code, skills that precede problem solving. Lopez et al. 2008: tracing precedes explaining, and tracing plus explaining precede writing; tracing explained about 15 percent of variance in writing scores. [source: search summary, secondary]
- Xie et al. 2019 propose four skills in order: tracing, writing syntax, comprehending templates, writing with templates ("read before write; semantics before templates"); incremental teaching improved exercise completion and post-test understanding, but the study had nine participants (5 vs 4), so treat as a design theory, not proof. [source: https://faculty.washington.edu/ajko/papers/Xie2019IntroCSTheoryOfInstruction.pdf, text extracted locally]
- Tracing variable values on paper next to their names was the most effective sketching strategy; teach learners to trace when debugging. [source: https://teachtogether.tech/en/index.html (citing Cunningham 2017)]
- Notional machine = an idealised model of how programs run; Teaching Tech Together gives a 12-rule one for Python (call stack + heap; data has type and value; numbers/strings immutable; collections hold references; a call pushes a frame; lookup goes local then global; return pops the frame). Sorva: make the notional machine an explicit learning objective. [source: https://teachtogether.tech/en/index.html; search summary of Sorva 2013, secondary]
- Python Tutor visualises frames, objects and references step by step; free; 25M+ users since 2010. Needs a browser and network. [source: https://pythontutor.com/]
- Local alternative verified: `prototype/tools/trace.py` (60 lines, `sys.settrace`) prints each executed line and the variables it changed. On `b = a; b.append(4)` it shows `a` and `b` changing together, which is the aliasing lesson in one line of output. [local]

### 2.5 Predictions
- Watching a demonstration does not improve learning by itself; committing to a prediction first does (physics-education evidence), and wrong predictions should trigger exploration, not criticism. [source: PLOS tip 4]
- Use here: predict exercises that must be answered with a literal value before running (the prototype rejects `predict_1 = b`).

### 2.6 Live coding
- Recommended practice (write code in front of learners, make and fix mistakes aloud, start from a skeleton to avoid boilerplate). [source: PLOS tip 3]
- A 2021 literature review found little empirical evidence that live coding improves learning; students find static examples more efficient for simple topics. [source: search summary of Selvaraj et al. ITiCSE 2021, secondary]
- Use here: the tutor "live codes" worked examples in small steps with the learner predicting the next line, and deliberately shows a mistake being diagnosed. Do not rely on it as the main mechanism.

### 2.7 Novice misconceptions (catalogue to build checks from)
Sources: progmiscon.org lists 30 Python misconceptions, each with origin, symptoms and how to build on it [source: https://progmiscon.org/misconceptions/Python/]; Teaching Tech Together [source: https://teachtogether.tech/en/index.html]; my local runs. Qian and Lehman 2017 group difficulties into syntactic, conceptual and strategic knowledge [source: search summary, secondary].

| Misconception | Probe (predict question) | What actually happens [local] | Remedy / analogy |
|---|---|---|---|
| The computer understands what I mean (the "superbug") | program with a misleading variable name | does exactly what is written | 解释器是极其听话、毫无常识的实习生 |
| `=` means "equals" (AssignCompares) | `x = 10; x = x + 1` | 11 | 读作"设为"：先算右边，再把名字贴上去 |
| Variables update like spreadsheet cells | `price = 20; total = price * 3; price = 100` | total stays 60 | 赋值只在执行那一行时算一次 |
| `b = a` links b to a forever / assignment moves the value | `a = 5; b = a; a = 8` | b is 5 | trace table |
| Variables contain objects; assignment copies (VariablesHoldObjects, AssignmentCopiesObject) | `a = [1,2,3]; b = a; b.append(4); print(a)` | `[1, 2, 3, 4]` | 名字是标签/链接，不是盒子；`copy()` 才是复印 |
| print is the same as return | `def add(a,b): print(a+b)` then `add(1,2) + 1` | `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'` | print 是念出来，return 是交到你手上 |
| A function runs when it is defined; return does not exit immediately (DeferredReturn) | def with a print inside, never called | prints nothing | 菜谱不等于做菜 |
| `if` repeats while true (IfIsLoop); if-else equals two ifs | trace an if inside a loop | body runs once per evaluation | trace table |
| `input()` gives a number | `age = input(); age + 1` | `TypeError: can only concatenate str (not "int") to str` | 键盘敲进来的永远是文字 |
| Methods change strings in place | `s = "abc"; s.upper(); print(s)` | `abc` | 字符串是打印好的纸，只能换新的 |
| `list.sort()` returns the sorted list | `print(xs.sort())` | `None` | 动作 vs 结果 |
| `range(1, 5)` includes 5 | `list(range(1, 5))` | `[1, 2, 3, 4]` | 左闭右开 |
| Function can change my local counter | `count = 0` then `count += 1` inside a def | `UnboundLocalError: cannot access local variable 'count' where it is not associated with a value` | 每次调用一张新草稿纸 |
| Default list argument is fresh each call | `def add_item(item, bag=[])` called twice | second call returns `['a', 'b']`; ruff flags B006 by default | 默认值只在 def 时造一次 |
| `and`/`or` evaluate both sides; `== True` needed | `x != 0 and 10 / x > 1` | short-circuits | - |
| `is` means equal | `[1,2] == [1,2]`, `[1,2] is [1,2]` | True, False | 同样的内容 vs 同一个东西 |
| `0.1 + 0.2 == 0.3` | - | False (`0.30000000000000004`) | 计算器位数有限 |
| Indentation is decoration | move a `print` into a loop body | prints every iteration | 缩进 = "属于谁" |

### 2.8 Teaching debugging explicitly
- Michaeli and Romeike (WiPSCE 2019): a 10-minute explicit lesson on a systematic process (distinguish compile-time, runtime and logic errors; form a hypothesis from observed behaviour, test it, refine; undo changes that did not help) raised self-efficacy and debugging performance versus a control class that only practised (post-test median 4 vs 2 errors fixed out of 9, p = 0.049; n = 13 vs 15, ages 15-16, Java). Small sample, no randomisation. [source: https://computingeducation.de/pub/2019_Michaeli-Romeike_WIPSCE19.pdf, text extracted locally]
- Good debuggers trace by hand, use a debugger, write tests and re-read the spec; reading code is the most effective way to find bugs; learners spend 13-25 percent of their time reading error messages, and reading them is as hard as reading code, so show how to read them. [source: https://teachtogether.tech/en/index.html]
- In the Anthropic trial, debugging questions showed the largest gap between AI users and hand-coders, and "iterative AI debugging" (asking the AI to fix or verify) was the worst interaction pattern (24 percent quiz average). [source: https://www.anthropic.com/news/AI-assistance-coding-skills]
- Use here: a fixed routine the learner applies before asking the tutor: 复现 → 读最后一行 → 定位行号 → 提出假设 → 做一个小实验验证 → 修改 → 没用就撤销 → 重新运行检查. The tutor coaches the routine and never applies the fix.

### 2.9 Mastery learning
- Bloom 1968: require a mastery level (for example 90 percent) on a unit before moving on; formative test, targeted correctives, retest. Meta-analyses report positive effects (Kulik et al. 1990, 108 studies, strongest for weaker students; an average effect of 0.59 is quoted); criticisms: extra time, effects mostly on experimenter-made tests, short studies. [source: https://en.wikipedia.org/wiki/Mastery_learning, secondary]
- In CS education there is no single standard implementation; common elements are self-pacing and unlimited retakes. [source: search summary of Garner, Denny, Luxton-Reilly 2019, secondary]
- Use here: unit checkpoints without AI, pass mark about 80 percent, correctives chosen by misconception tag, retake with variant questions. Self-paced by nature.

### 2.10 Memory and cognitive load (Hermans; Wilson)
- The Programmer's Brain (Felienne Hermans, Manning, August 2021, 256 pages): three kinds of confusion when reading code map to three systems: lack of knowledge (long-term memory), lack of information (short-term memory), lack of processing power (working memory). [source: https://www.manning.com/books/the-programmers-brain; https://livebook.manning.com/book/the-programmers-brain/chapter-1] Chapter topics include flashcards for syntax, state tables for complex code, a misconceptions chapter, naming. [source: search summary, secondary] [memory: spaced repetition of flashcards and reading code aloud are her concrete recommendations]
- Working memory is tiny (7 plus or minus 2, more likely 4 plus or minus 1); do a 1-2 minute formative check every 10-15 minutes; each wrong option in a multiple-choice question should diagnose one specific misconception; repetition without feedback hardens bad habits. [source: https://teachtogether.tech/en/index.html]
- Novices lack a mental model and reason by analogy and guesswork; the teacher's job is to help them build a usable model, even a simplified one. [source: same]
- Retrieval practice and spacing improve retention [memory]. Use here: 3 warm-up questions per lesson drawn from older lessons; a small flashcard deck for syntax and English terms.

### 2.11 Brown and Wilson's ten tips, mapped to a solo learner with an AI tutor
[source: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006023]
1. No "geek gene": only 5.8 percent of intro grade distributions were multimodal. Tutor never implies talent; praises process.
2. Peer instruction: no peers here; the tutor can pose a diagnostic multiple-choice question, wait for a committed answer, then discuss. Weak substitute (judgment).
3. Live coding: see 2.6.
4. Predictions: core of every lesson.
5. Pair programming: learner drives, tutor navigates (questions only). Evidence for AI-as-partner is thin (judgment).
6. Worked examples with labelled subgoals: see 2.2.
7. One language: transfer only happens after mastery. See "challenges" about the roadmap's switch to JavaScript.
8. Authentic tasks: motivation matters more than measured performance; provide prewritten helpers so results are visible quickly.
9. Novices are not experts: small self-contained tasks, paper planning, tools sized for beginners.
10. Don't just code: Parsons problems and other non-writing tasks.

---

## 3. Novices learning with LLM assistants (2023-2026)

| Study | Design | Finding | Implication |
|---|---|---|---|
| Bastani et al., PNAS 122(26), July 2025 [source: https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html] | Field experiment, nearly 1000 high-school maths students; "GPT Base" (plain chat) vs "GPT Tutor" (prompts that safeguard learning) vs none | Practice grades +48% (Base) and +127% (Tutor); on the later unassisted exam Base students scored 17% lower than students who never had AI; Tutor guardrails largely removed the harm | Hints-not-answers is the difference between harm and no harm |
| Shen and Tamkin (Anthropic), arXiv 2601.20245, Jan 2026 [source: https://www.anthropic.com/news/AI-assistance-coding-skills] | RCT, 52 mostly junior developers learning the Trio library; 35-minute task then quiz | AI group 50% vs hand-coding 67% on the quiz (d = 0.738, p = 0.01); speed gain about 2 minutes, not significant; largest gap on debugging. Low-scoring patterns: full delegation (39%), progressive reliance (35%), iterative AI debugging (24%). High-scoring: generate then ask to understand (86%), code plus explanation (68%), conceptual questions only (65%) | The tutor should push the three high-scoring patterns and block the three low-scoring ones. Limits: small, immediate test, associative patterns |
| Bassner et al. (TUM), Computers and Education: AI, vol 10, June 2026 [source: https://portal.fis.tum.de/en/publications/less-stress-better-scores-same-learning-the-dissociation-of-perfo/] | 3-arm RCT, N = 275 CS1 students, 90-minute task: scaffolded hint tutor (Iris) vs unrestricted ChatGPT vs web only | Both AI arms scored much higher on the task and reported less frustration; neither produced more learning (pre/post test, code comprehension). Only the scaffolded tutor raised intrinsic motivation; students rated ChatGPT as more helpful ("comfort trap") | Even a good coach improves performance and motivation, not automatically learning. Learners will prefer the tool that teaches them less |
| Prather et al., ICER 2024 [source: https://arxiv.org/abs/2405.17739] | 21 CS1 students observed with eye tracking | 20 of 21 finished, but struggling students kept or worsened their metacognitive problems and ended with an illusion of competence; strong students used AI to speed up code they already planned | The weakest learners are the most at risk and the least aware of it; ask for confidence ratings and check them |
| Kazemitabaar et al., CHI 2023 [source: https://arxiv.org/abs/2302.07427] | 69 novices aged 10-17, 45 Python tasks, half with Codex | Higher completion (1.15x) and scores (1.8x) while authoring; no loss on manual modification tasks; retention one week later slightly better but not significant; learners with more prior knowledge benefited most | AI generation plus mandatory modification of the result is not harmful; prior knowledge decides who benefits |
| Lehmann, Cornelius, Sting, arXiv 2409.09047 (2024, rev. 2025) [source: https://arxiv.org/abs/2409.09047] | Two pre-registered lab experiments + field study | No overall effect; using the LLM as a substitute (have it produce solutions) covers more topics with less understanding; using it as a complement (ask for explanations) improves understanding; gap between low and high prior knowledge widens | Same split as the Anthropic patterns |
| Liu, Malan et al., SIGCSE 2024 (CS50 Duck) [source: https://cs.harvard.edu/malan/publications/V1fp0567-liu.pdf, text extracted locally] | Deployment report, about 70 then about 500 on-campus students plus thousands online | Tools built to guide toward solutions instead of giving them; throttling (10 "hearts", one regained every three minutes) to make students think before asking; 88% of 25 curricular answers judged correct; most students found it helpful | Throttling is a legitimate pedagogical device; tutors are wrong more than one time in ten |
| Kazemitabaar et al., CHI 2024 (CodeAid) [source: https://arxiv.org/abs/2401.11314] | 700 students, 12 weeks, 8000 uses | Assistant answers conceptually, gives pseudo-code and annotates the student's own code without writing the solution. Design considerations: exploit AI's strengths; make asking easy while still requiring thought; avoid direct answers; keep the student in control | Template for hint levels |
| Kestin et al., Scientific Reports 15:17458, June 2025 [source: search summaries, secondary; publisher blocked] | Crossover RCT, 194 Harvard physics students, engineered AI tutor vs active-learning class | Higher post-test scores in less time with the tutor; tutor was told to give one step at a time, not to reveal the full solution in one message, to let students try first, and was fed prepared solutions | A carefully scripted tutor can teach well; two topics, short-term test |
| Nie et al., arXiv 2407.09975 [source: search summary, secondary] | RCT in a massive free intro coding course | Offering GPT-4 lowered exam participation overall; those who adopted it scored higher | Availability itself can reduce engagement |
| Fan et al., BJET (online Dec 2024) [source: search summary, secondary] | 117 students, essay task, ChatGPT vs human expert vs tool vs none | ChatGPT group improved the essay most but showed no advantage in knowledge gain or transfer ("metacognitive laziness") | Not programming, same pattern |
| Vadaparty, Zingaro, Porter et al., ITiCSE 2024 (CS1-LLM) [source: search summary of arXiv 2406.15379, secondary] | Experience report of a CS1 redesigned around LLMs | Less time on syntax and blank-page writing; more on explaining, testing, debugging and decomposing; final exam tested both unaided and assisted work | The skills that matter more with AI are reading, testing, debugging, decomposition |
| Padiyath et al., ITiCSE 2026, via Guzdial's blog [source: https://computinged.wordpress.com/] | Students write a private contract about when they will and will not use GenAI and revise it after each midterm | No numbers in the post; presented as harm reduction through self-regulation | Cheap to adopt: a learner-written AI-use contract |

Cross-cutting points:
- A widely cited 2025 meta-analysis claiming a large positive ChatGPT effect (g = 0.867, Wang and Fan) is now marked RETRACTED. Do not cite it. [source: https://ideas.repec.org/a/pal/palcom/v12y2025i1d10.1057_s41599-025-04787-y.html]
- Guzdial (Feb 2026): GenAI is closer to a car than a bicycle for the mind; it outsources thinking, so deliberate mental exercise is the remedy; tools that embed GenAI in a purpose-built learning environment show the best outcomes. [source: https://computinged.wordpress.com/2026/02/16/genai-as-automobile-for-the-mind-and-exercise-as-the-antidote/]
- Students themselves say an AI teaching assistant should break work into steps for them to write, not write it. [source: search summary of Denny et al. 2024, arXiv 2405.14178, secondary]
- Anthropic's own usage analysis (574,740 student conversations): about 47 percent were "direct" requests for answers or outputs; computer science is heavily over-represented. [source: https://www.anthropic.com/news/anthropic-education-report-how-university-students-use-claude]

What helps: predicting before seeing; asking conceptual questions; asking for explanations of generated or given code and then being quizzed; stepwise hints; modifying AI-written code by hand; throttled access; explicit self-regulation. What harms: delegation of the whole task; asking the AI to debug; accepting code without reading it; using the AI before attempting; judging progress by task completion.

---

## 4. Survey of beginner Python curricula (as of today)

| Curriculum | Sequence | Exercise style and checking | AI stance | Chinese |
|---|---|---|---|---|
| **CS50P** (Harvard) [source: https://cs50.harvard.edu/python/] | 0 Functions, Variables; 1 Conditionals; 2 Loops; 3 Exceptions; 4 Libraries; 5 Unit Tests; 6 File I/O; 7 Regular Expressions; 8 OOP; 9 Et Cetera; final project | about five small programs per week (problem set 0 has five), written in a cloud VS Code (cs50.dev); each has manual test instructions, a couple of one-line hints, then `check50 cs50/problems/2022/python/<name>` (black-box stdin/stdout tests) and `submit50`; deadline currently shown as 2027-06-30 [source: https://cs50.harvard.edu/python/psets/0/indoor/] | Own guarded tutor (CS50 Duck) allowed; other AI that suggests or completes code is "not reasonable" [source: https://cs50.harvard.edu/python/honesty/] | No official Chinese version listed (site links Portuguese and Spanish for CS50x) |
| **Python for Everybody** (Severance) [source: https://www.py4e.com/lessons] | Install; Why Program; Variables; Conditionals; Functions; Loops; Strings; Files; Lists; Dictionaries; Tuples; Regex; Network; Web Services; OOP; Databases; Visualization (17 lessons) | Autograded assignments via the Tsugi framework; CC BY 4.0 | not stated | Chinese book translation "in progress" (PDF/EPUB, GitHub source, Bilibili videos) [source: https://www.py4e.com/book] |
| **Automate the Boring Stuff, 3rd ed.** (Sweigart, No Starch, April 2025, 672 pp.) [source: https://nostarch.com/automate-boring-stuff-python-3rd-edition; https://automatetheboringstuff.com/] | Part I: Basics; if-else and Flow Control; Loops; Functions; Debugging; Lists; Dictionaries; Strings (ch. 1-8). Part II: 16 automation chapters (regex, files, CLI programs, scraping, Excel, SQLite, PDF, CSV/JSON, scheduling, email, images, OCR, GUI automation, speech) | Practice questions with answers, projects; separate workbook; no autograder; free to read online | - | 3rd edition in Simplified Chinese: not found; the Chinese edition I could confirm is of an earlier edition [source: search, secondary] |
| **Think Python, 3rd ed.** (Downey, O'Reilly, 2024) [source: https://allendowney.github.io/ThinkPython/; https://allendowney.github.io/ThinkPython/chap00.html] | Functions before conditionals; recursion before iteration; strings+regex; lists; dicts; tuples; text analysis; files and databases; four OOP chapters | Every chapter is a Jupyter notebook (Colab); 3rd edition adds `doctest`/`unittest` and exercises on them, explicitly because AI assistants make testing more important | Each chapter ends with advice on using AI assistants to learn; stresses vocabulary to prompt and to read errors | Traditional Chinese print edition exists; a community Simplified Chinese translation is on Gitee (unofficial) [source: search, secondary] |
| **Official tutorial** [source: https://docs.python.org/3.14/tutorial/index.html] | Interpreter; informal intro; control flow; data structures; modules; I/O; errors; classes; stdlib tour; venvs | No exercises | - | Full zh-CN translation of 3.14 (all 16 chapter titles translated; code and error text stay English) [source: https://docs.python.org/zh-cn/3.14/tutorial/index.html]. The tutorial itself says it is for programmers new to Python, not for people new to programming. Use it as a reference to learn doc-reading, not as the course spine |
| **Real Python** "Python Basics" path [source: search summary, secondary; direct fetch returned 403] | about 18 resources: syntax, data structures, functions, OOP | Video courses and tutorials behind membership; quizzes free; an AI mentor product | - | English only |
| **Exercism Python track** [source: https://exercism.org/tracks/python; https://raw.githubusercontent.com/exercism/python/main/config.json] | Concept exercises: basics, bools, numbers, conditionals, comparisons, strings, string methods, lists, list methods, loops, tuples, dicts, dict methods, unpacking, sets, classes, generators | 146 exercises listed on the track page; the repo config has 21 concept-exercise entries (17 active, 3 work-in-progress, 1 deprecated) and about 129 active practice exercises; each is a stub file plus `<name>_test.py`; run locally with `python3 -m pytest -o markers=task <file>_test.py` (docs example shows pytest 8.3.3 and suggest `-x --ff`) or in the browser; free human mentoring [source: https://exercism.org/docs/tracks/python/tests] | - | Site now has a zh-CN locale and the exercise instructions I opened were translated [source: https://exercism.org/zh-CN/tracks/python/exercises/guidos-gorgeous-lasagna]. Coverage of all exercises not checked |
| **廖雪峰 Python 教程** [source: https://liaoxuefeng.com/books/python/introduction/index.html] | 简介, 安装, 第一个程序, Python基础, 函数, 高级特性, 函数式编程, 模块, 面向对象, 面向对象高级, 错误调试测试, IO, 进程和线程, 正则, 常用模块, 第三方模块, 图形界面, 网络, 邮件, 数据库, Web开发, 异步IO | Prose + static code + a small exercise per section; no autograder; states it follows the latest Python 3 | none | Native Chinese. Fast pace and early advanced topics (functional programming, processes); good secondary reading, weak as a first course for a non-programmer (judgment) |
| Also worth knowing: **Helsinki Python Programming MOOC 2026** [source: https://programming-26.mooc.fi/; /grading-and-exams] | two 5-ECTS courses, 14 parts | exercises are auto-assessed (TMC system; secondary, from search); grade = 50% exercises + 50% exam; suspected cheating can lead to an interview where the student must explain the solution | no AI policy on the pages read | English/Finnish |
| **futurecoder** [source: https://futurecoder.io/; README] | interactive beginner course | stepwise hints, Parsons problems after hints, gradual solution reveal, predict-the-output questions, friendlier tracebacks, Python Tutor / snoop / birdseye | - | Site lists 中文 among its languages (completeness not checked); MIT licence |

What to borrow:
- CS50P: black-box stdin/stdout checks, one-line hints per problem, unit tests as a first-class early topic (week 5), own guarded tutor plus a ban on answer-giving AI.
- Think Python 3e: testing introduced because of AI; AI-use advice per chapter.
- ATBS 3e: debugging as its own early chapter (ch. 5, right after functions); practical automation projects as motivation.
- Exercism: stub + test file layout; story-framed concept exercises with task lists; `hints.md`.
- futurecoder and rustlings: one exercise at a time, hints before solution, Parsons as a late hint.
- Helsinki: many tiny exercises; exam counts half; oral follow-up as honesty check.
- Chinese-language support material: official zh-CN tutorial (reference), 廖雪峰 (second explanation), Exercism zh-CN (extra practice).

Sequencing disagreement to be aware of: CS50P, PY4E and Think Python define functions before loops; ATBS and Exercism put loops and conditionals first. No decisive evidence either way was found (judgment: for a zero-background adult, call built-in functions from lesson 1, define functions after loops).

---

## 5. What changed recently (older tutorials will mislead)

- **Python 3.15 is the current stable series** (3.15.0 on 2026-10-09; 3.15.2 on 2026-10-25); 3.14 is in bugfix support; 3.10 reached end-of-life in October 2026. [source: https://www.python.org/downloads/] uv 0.13.5 already offers cpython-3.15.1 for download. [local] 3.15 makes UTF-8 the default text encoding everywhere and adds smarter `AttributeError` hints (for example suggesting `.append` when someone writes `.push`). [source: https://docs.python.org/3.15/whatsnew/3.15.html] Recommendation: keep 3.14 (it is this machine's default), pin it in `.python-version`, always write `encoding="utf-8"` in `open()`.
- **Error messages are much better than in screenshots from 2015-2021 tutorials**: "Did you mean" for misspelled keywords (new in 3.14), names and attributes; "Did you forget to import"; exact carets under the failing sub-expression. [local, section 6] [source: https://docs.python.org/3.14/whatsnew/3.14.html]
- **`except ValueError, TypeError:` without parentheses is valid in 3.14** and the official tutorial now uses it. `ruff format` 0.17.2 with `requires-python = ">=3.14"` rewrites the parenthesised form to the bare form; the result is a SyntaxError on the system Python 3.9.6. [local] Teach both spellings and say which versions accept the new one.
- **The REPL was replaced in 3.13**: colour, multi-line editing, history, F1 help, F3 paste mode, `exit` without parentheses; 3.14 adds syntax highlighting and import completion. [source: https://docs.python.org/3.14/tutorial/appendix.html; whatsnew 3.14] (not testable here: no pty in the sandbox)
- f-strings may reuse the same quote type inside braces (3.12+): `f"{d["k"]}"` works. [local]
- Type hints use built-ins: `list[float]`, `float | None`; no `typing.List`/`Optional` imports needed; annotations are evaluated lazily in 3.14. [local] [source: whatsnew 3.14]
- t-strings (`t"..."`, 3.14) exist and are not f-strings; postpone. [source: whatsnew 3.14]
- `print(2**20000)` raises `ValueError: Exceeds the limit (4300 digits) for integer string conversion`. Beginners playing with big numbers hit this. [local]
- **uv replaces the venv/pip ritual**: `uv init`, `uv add --dev pytest`, `uv run file.py`; no activation step. `uv init` writes a `main.py` containing `def main()` and `if __name__ == "__main__":`, which is not a day-one program. [local]
- **pytest 9** (9.0 on 2025-11-05; 9.2.0 on 2026-10-27): native `[tool.pytest]` table in `pyproject.toml` with real TOML lists; `[tool.pytest.ini_options]` still works; 9.2 requires `ids=` etc. to be passed by keyword in `parametrize`; Python 3.9 dropped. [source: https://docs.pytest.org/en/stable/reference/customize.html; https://docs.pytest.org/en/stable/changelog.html] [local: `[tool.pytest]` works]
- **ruff 0.17.2 default rule set is broad**: with `--isolated` (no config) it flags mutable default arguments (B006), bare `except` (E722), try-except-pass (S110), needless if/else returns (SIM103), unused imports (F401), `subprocess.run` without `check` (PLW1510), `exec` (S102). Older articles describe a much smaller default. [local]
- Textbooks changed for the AI era: Think Python 3e (2024) and ATBS 3e (2025); Exercism has a Chinese locale; CS50 ships its own guarded tutor and forbids other AI. [sources in section 4]
- Claude Code now has four built-in output styles besides the default (Proactive, Concise, Explanatory, Learning) and supports custom styles as Markdown files. [source: https://code.claude.com/docs/en/output-styles]

---

## 6. Real output from this machine (use these in lessons instead of old screenshots)

Command: `python3 errors-demo/run_snippets.py` under CPython 3.14.9. [local] Selected results:

```
whille True:                     SyntaxError: invalid syntax. Did you mean 'while'?
if x > 2        (no colon)       SyntaxError: expected ':'
if x = 3:                        SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
print('hello'   (unclosed)       SyntaxError: '(' was never closed
def f():\nprint('hi')            IndentationError: expected an indented block after function definition on line 1
print(totl)                      NameError: name 'totl' is not defined. Did you mean: 'total'?
print(math.sqrt(4))              NameError: name 'math' is not defined. Did you forget to import 'math'?
'18' + 1                         TypeError: can only concatenate str (not "int") to str
int('abc')                       ValueError: invalid literal for int() with base 10: 'abc'
xs[3] on a 3-item list           IndexError: list index out of range
d['b']                           KeyError: 'b'
s.uper()                         AttributeError: 'str' object has no attribute 'uper'. Did you mean: 'upper'?
print(s.upper)  (no call)        <built-in method upper of str object at 0x...>      (no error at all)
print 'hello'                    SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?
print（'你好'）  (full-width)     SyntaxError: invalid character '（' (U+FF08)
print(“你好”)   (curly quotes)   SyntaxError: invalid character '“' (U+201C)
nums(0)                          TypeError: 'list' object is not callable
s[0] = 'X'                       TypeError: 'str' object does not support item assignment
d[[1, 2]] = 1                    TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
greet()  (missing argument)      TypeError: greet() missing 1 required positional argument: 'name'
file named random.py             AttributeError: module 'random' has no attribute 'randint' (consider renaming
                                 '.../random.py' since it has the same name as the standard library module ...)
```

Other verified behaviours [local]: `年龄 = 18` is a legal identifier; `len("你好")` is 2; `bool("False")` is True; `round(2.5)` is 2; `-7 // 2` is -4; `input("年龄？")` writes its prompt to standard output even when input is piped (matters for output checks); `uv run hello.py` works in a folder with no project and creates nothing.

Plain pytest 9.2 failure output for a learner-written test [local]:
```
>       assert total_price([10, 20, 30]) == 60
E       assert 30 == 60
E        +  where 30 = total_price([10, 20, 30])
```

---

## 7. Recommended design for Stage 2 (about 25 lessons, Python 3.14)

### 7.1 Principles (each tied to section 2 or 3)
1. PRIMM cycle in every lesson; writing from scratch comes last.
2. One notional machine, drawn the same way all stage long: L3 names-on-values, L8 call frames, L12 references and mutation, L21 objects.
3. One language, one toolchain: Python, `uv run`, VS Code. No notebooks, no second runner.
4. Worked example with labelled steps, then faded example, then independent problem.
5. Checks give misconception-specific feedback.
6. Debugging is a taught procedure (L6 first contact, L10 full lesson, L23 on other people's code).
7. Unit checkpoints without AI decide progression.
8. Spaced retrieval: warm-up questions from older lessons.
9. Authentic small projects, ideally from the learner's own world (ask in Stage 0; if the learner already has a small project of their own, for example one an AI helped write, reading and re-implementing a slice of it is a natural capstone).
10. English arrives gradually: at most about 8 new English terms per lesson; error messages are read in English with a gloss table; from L18 the learner reads official docs (zh-CN first, then the English page).

### 7.2 Lesson sequence

| # | Lesson (中文题目) | Core content | Main misconception targeted | New exercise kinds |
|---|---|---|---|---|
| 1 | 程序与解释器 | run a file with `uv run`, `print`, comments, REPL vs file, cause a NameError and a SyntaxError on purpose | the computer understands intent | predict, fix |
| 2 | 值、类型与表达式 | int, float, str, bool; operators; precedence; `type()`; first f-string | `"18"` vs `18`; `/` vs `//` | predict |
| 3 | 变量与赋值 | names on values, sequential execution, reassignment, `+=` | `=` as equality; spreadsheet model | trace |
| 4 | 字符串与输入 | `input`, `int()`/`float()`/`str()`, indexing, slicing, `len`, methods return new strings | input gives numbers; methods mutate strings | fix, make (scripts) |
| 5 | 条件判断 | comparisons, `and`/`or`/`not`, `if`/`elif`/`else` | if is a loop; two ifs equal if-else | Parsons |
| - | Project A + checkpoint A | converter with input validation (for example a currency or unit converter with a fee) | | |
| 6 | while 循环 | loop trace table, counters, sentinel values, `break`, Ctrl-C | condition re-checked continuously | trace |
| 7 | for 循环与 range | iterating strings and ranges; patterns: accumulate, count, max, search | range includes its end; loop variable | Parsons, trace |
| 8 | 函数一：定义与调用 | `def`, parameters and arguments, `return` vs `print`, `None`, call frames | print equals return; defining runs the body | make (functions) |
| 9 | 函数二：作用域与设计 | local scope, default and keyword arguments, docstrings, type hints as labels, decomposition | functions can change my locals | modify |
| 10 | 调试专题 | error taxonomy, reading tracebacks bottom-up, the debugging routine, print debugging, VS Code debugger, `tools/trace.py` | random changes fix bugs | fix (logic bugs) |
| - | Project B + checkpoint B | number-guessing game, then refactor into functions | | |
| 11 | 列表 | indexing, slicing, iteration, `append`/`pop`, `sort` vs `sorted`, `in` | `sort()` returns a list; off-by-one | make |
| 12 | 引用与可变性 | aliasing, `copy`, `is` vs `==`, lists as arguments, mutable default, tuples | assignment copies | predict, trace |
| 13 | 字典与集合 | lookup, `get`, `items`, counting and grouping patterns, sets | dict has positions | make |
| 14 | 嵌套数据与推导式 | list of dicts, JSON-shaped data, `sorted(key=...)`, comprehensions (read first) | - | Parsons |
| 15 | 文本处理 | `split`/`join`/`strip`/`replace`, formatting numbers, Chinese text and Unicode | strings are byte arrays | make |
| - | Project C + checkpoint C | in-memory ledger (list of dicts) with summaries | | |
| 16 | 文件读写 | `pathlib`, `with open(..., encoding="utf-8")`, CSV and JSON, working directory | paths are relative to the file | fix |
| 17 | 异常处理 | `try`/`except`/`else`/`finally`, `raise`, specific exceptions, both `except` spellings | catch everything silently | modify |
| 18 | 模块与标准库 | `import`, own modules, `if __name__ == "__main__"`, `random`/`datetime`/`json`, reading docs | file named like a stdlib module | explain |
| 19 | 第三方包与 uv | `pyproject.toml`, `uv add`, lockfile, what `.venv` is | pip install globally | make |
| 20 | 写测试 | pytest test functions, parametrize, edge cases, reading failure output, test-first once | tests prove correctness | write-tests |
| - | Project D + checkpoint D | ledger v2: file persistence, menu, own tests | | |
| 21 | 类与对象一 | `class`, `__init__`, attributes, methods, `@dataclass` | `__init__` returns the object; class equals object | predict, make |
| 22 | 类与对象二 | composition, `__repr__`, when not to use a class | inheritance everywhere | modify |
| 23 | 读代码与重构 | reading unfamiliar code, small refactors under tests, reviewing AI-written code with planted bugs | passing tests means good code | review |
| 24 | 命令行程序 | `argparse`, exit codes, stdin/stdout/stderr | - | make |
| 25 | 结业项目与阶段考核 | re-read and rebuild a slice of the learner's own project, if any (or a CLI tool); unassisted stage exam | | |

Postpone to later stages: recursion (optional enrichment), regular expressions, generators, decorators, lambda and functional tools, `match`, async, inheritance in depth, logging, packaging, strict typing, ruff/format tooling as a topic, t-strings, `global`.

### 7.3 Lesson template (judgment, built from 2.1-2.10)
1. 热身 (5 min): three retrieval questions from older lessons.
2. 预测 (10 min): 2-3 predict exercises on the new construct, before any explanation.
3. 讲解 (15 min): worked example with labelled steps; notional-machine picture; English terms table.
4. 运行与探究 (15 min): run, trace table by hand, compare with `tools/trace.py`, one Parsons.
5. 修改 (15 min): one fix-the-bug, one extend-the-program.
6. 创作 (20 min): one or two write-from-scratch tasks checked by tests.
7. 讲解回放 (5 min): explain one program in plain Chinese to the tutor.
8. 手册 (5 min): the learner writes (not the AI) one handbook entry: the concept in their own words, one pitfall they hit, one error message they met.
About 8-10 exercises per lesson; roughly 220 exercises and 5 projects in the stage.

### 7.4 Checkpoints
20-30 minutes, tutor refuses help, runner hides hints; new variant items: 3 trace, 2 fix, 2 write, 1 explain. Record a confidence rating (0-100) before checking and compare it with the score (calibration against the illusion of competence). Pass at about 80 percent; otherwise assign correctives by misconception tag and retake a variant next session.

---

## 8. Exercise and auto-check format: specification and working prototype

Location: `prototype/` in this directory. 917 lines including lockfile; runner 191 lines, fixtures 167 lines. Standard library + pytest only. [local]

### 8.1 Commands that were run successfully
```
uv init --app --no-package --vcs none --no-workspace --author-from none --python 3.14 --name py-fundamentals-prototype prototype
uv add --dev pytest            # -> pytest==9.2.0, pluggy 1.7.0, iniconfig 2.3.1, packaging 26.3, pygments 2.21.0
uv run tools/selfcheck.py      # author check, 3.3 s for 5 exercises
uv run learn.py                # learner command, 0.35 s
uv run learn.py hint | list | check L07_loops/ex1_trace
uv run tools/trace.py FILE
uv run pytest                  # raw: "11 failed, 1 passed in 0.11s" on untouched starters
ruff check . && ruff format --check .    # clean
```
`uv init` needed `--author-from none` to avoid reading git identity, and I deleted the generated `main.py`.

### 8.2 Layout and config
```
exercises.toml                      ordered manifest: id, kind, title, optional reflect question
exercises/<lesson>/<name>.py        the only files the learner edits
checks/<lesson>/test_<name>.py      pytest checks
hints/<lesson>/<name>.md            three graduated hints ("## 提示 1..3")
solutions/<lesson>/<name>.py        reference solutions
conftest.py                         fixtures: exercise_file, literal_answer, run_script, load_exercise; JSON report
learn.py                            runner; writes .progress.json
tools/selfcheck.py, tools/trace.py
```
```toml
[dependency-groups]
dev = ["pytest>=9.2.0"]

[tool.pytest]                       # native TOML table, pytest >= 9.0
testpaths = ["checks"]
addopts = ["--import-mode=importlib", "-p", "no:cacheprovider", "--no-header", "-q"]

[tool.ruff]
line-length = 110
extend-exclude = ["exercises/**/*_parsons.py"]   # scrambled on purpose, not valid Python until solved
```

### 8.3 Five exercise kinds demonstrated
1. **predict** (`L03_variables/ex1_predict.py`): code followed by `predict_1 = ...`; the learner replaces `...` with a literal. The check reads the file with `ast` without running it, so `predict_1 = b` is rejected.
2. **fix** (`L04_input/ex1_fix_age.py`): a two-line program that raises the classic `TypeError`; checked by running it as a subprocess with stdin fed in.
3. **trace** (`L07_loops/ex1_trace.py`): `trace_total = [..., ..., ...]`, one value per loop round.
4. **parsons** (`L07_loops/ex2_parsons.py`): six scrambled, un-indented lines including one distractor; check = "only the given lines are used" (multiset comparison) + "prints 2550".
5. **make** (`L08_functions/ex1_make.py`): `def is_leap_year(year): ...` with four parametrised cases.
Not prototyped, recommended: **modify** (extend a working program), **explain** (free text judged by the tutor against a rubric; the runner only records that it exists), **review** (find planted bugs in AI-style code), **quiz** (multiple choice whose wrong options each map to one misconception), **write-tests** (learner's tests must fail on a buggy implementation and pass on a correct one).

### 8.4 What the learner sees (real output)
```
进度 □□□□□ 0/5
▶ 第 1 题 [预测] 赋值不是等号：先预测，再运行
  文件：exercises/L03_variables/ex1_predict.py

✗ 还没通过（第 2 次检查）

  · predict_1 还不对（你填的是 8）。你可能认为 b = a 把 b 和 a “绑”在了一起。其实赋值只在执行的那一刻，
    把 a 当时的值交给 b；之后 a 再变，b 不受影响。
  · predict_3 还不对（你填的是 300）。total 不像 Excel 单元格那样自动重算。...

改好并保存后再运行：uv run learn.py
卡住了：uv run learn.py hint   （已看提示 1/3）
```
Other verified responses: unfilled blank ("predict_1 里还有 ... 没填"); non-literal answer ("请直接写出你预测的值...这道题要你来当解释器"); learner program crashes (the real traceback is shown with "从最后一行往上读"); accidental infinite loop ("程序运行了 5 秒还没结束。可能是死循环..."); wrong output ("输入 18 时，期望看到这一行：明年你就 19 岁了 / 但你的程序打印的是：...181 岁了"); trace error on round 3 gets a targeted message about the `if`; Parsons with an invented line ("拼图题只能使用给定的代码行"); function that prints instead of returning ("返回了 None。你的函数用 print 显示了结果，但没有 return"); full-width semicolon (`SyntaxError: invalid character '；' (U+FF1B)` shown verbatim); hint requested before any attempt ("先自己试一次...再来看提示"); on success a reflection question ("先别急着往下——用自己的话回答...").
`.progress.json` per exercise: `attempts`, `hints_used`, `passed`, `passed_on_attempt`, `last_checked`.
Author self-check output: `OK   L03_variables/ex1_predict    starter fails: True  solution passes: True  hints: 3` for all five.

### 8.5 Rules for writing checks (each learned or confirmed while building) [local]
1. Show one exercise at a time. Raw `uv run pytest` on a fresh workspace prints eleven failures at once; that is the wrong first experience.
2. Fail with `pytest.fail(message, pytrace=False)`: one plain paragraph, no traceback through test code.
3. When failing from inside an `except` block, re-raise `from None`. Otherwise pytest prints the internal exception plus "During handling of the above exception, another exception occurred" in front of the message (this happened in the first version).
4. Predict and trace checks must never print the expected value; behaviour checks should print expected versus actual.
5. Map known wrong answers to the misconception behind them (a dict in the check file).
6. Run script exercises in a subprocess with a timeout (5 s) and feed stdin; the runner adds a 30 s outer timeout. In-process execution would hang on `while True`.
7. `input()` prompts appear in captured output; compare with "expected line is contained in output", not equality.
8. Show errors from the learner's own code verbatim (path shortened). Reading real error messages is a goal, so do not paraphrase them away.
9. Give parametrised cases ASCII ids: pytest escapes non-ASCII ids (`明年...`).
10. Use `--import-mode=importlib` so two lessons may both contain `test_ex1_*.py`.
11. Use `...` as the blank: it is valid Python, so starter files run without scaffolding or imports.
12. Truncate long program output in messages (the first Parsons failure printed 50 lines).
13. Parsons starters are invalid Python by design: exclude them from ruff, and expect red squiggles in the editor.
14. Gate hints: none before a first attempt, one level at a time, usage recorded.
15. Ship a self-check (starter fails, solution passes, at least three hints) and run it before every commit of new lessons.
16. Reset an exercise with `git restore <file>`; it reuses a Stage 1 skill instead of adding a runner feature.
17. Keep the tracer honest: the first version compared live objects and missed `b.append(4)` because its "previous" snapshot was the same list. Snapshot with `repr()`. (The bug is itself the aliasing lesson.)

---

## 9. Rules for the AI tutor in Stage 2

Basis: sections 3 (Bastani, Anthropic, TUM, Prather, CS50, CodeAid, Kestin), 2.8, 2.10.

### 9.1 Mode
Stage 2 runs in "学习模式": the tutor is a coach. It may run `uv run learn.py`, read `.progress.json`, read the learner's files, and write only in its own notes (learner model) and in new practice variants. It must not edit files under `exercises/` or the learner's project code. An output style is an instruction, not a guarantee; the Claude Code docs say hooks are the mechanism for things that must always happen, so block Edit/Write on those paths with a hook. [source: https://code.claude.com/docs/en/output-styles] (hook itself not tested here)
The built-in Learning style has Claude implement the routine parts and leave a few lines marked `TODO(human)` for the user. That is the inverse of what a zero-beginner needs in exercises; use a custom style file in `.claude/output-styles/` (frontmatter `name`, `description`, `keep-coding-instructions`) and set `outputStyle` in `.claude/settings.local.json`. [source: same]

### 9.2 Hint ladder (one rung per turn; record the highest rung reached)
0. **澄清**: ask what they tried, what they expected, what happened. Often solves it.
1. **定位**: point at where to look (a line, a word in the error message, a lesson section) with a question.
2. **概念**: re-explain the idea with a different analogy or a trace table of a smaller case.
3. **同类例题**: a worked example of a different problem with the same structure, with labelled steps.
4. **骨架**: the plan in Chinese pseudo-code, or the solution's lines scrambled (Parsons), or code with blanks.
5. **揭示**: the full solution to this exercise, only after two genuine attempts plus rungs 1-4, or when a time box (about 25-30 minutes on one exercise) is exceeded. Then the learner explains each line back, the exercise is logged as "assisted", and a variant is scheduled for unassisted re-solving in a later session.

### 9.3 When to explain directly, when to withhold
Explain directly: anything that is not the learning objective of the current exercise (tool glitches, editor behaviour, an English word, syntax the lesson has not taught yet); a direct conceptual question ("what does return mean?"), followed by a prediction question; after rung 4 failed.
Withhold: the solution to the current exercise; the fix for a bug in the learner's exercise code (coach the debugging routine instead: "最后一行说了什么？哪一行？你的假设是？怎么验证？"); any help before a first attempt; rewriting the learner's code "more cleanly" without being asked.
Always: one question at a time; short turns; plain Chinese with the English term in brackets on first use; never "很简单" or "显然"; praise the process, not talent; state uncertainty (tutors are wrong more than one time in ten in the CS50 data).

### 9.4 Checking understanding (never "懂了吗？")
- Predict a variant ("把第 3 行和第 4 行交换，输出是什么？").
- Explain in plain Chinese what a program is for, not line by line.
- Trace table for a small input.
- Spot the planted bug in tutor-written code.
- Transfer: same idea, new surface.
- Ask for a confidence rating before revealing correctness; log calibration.
Write the evidence into a learner-model file (misconceptions seen, rung reached, calibration) so later lessons can be generated to fit.

### 9.5 "直接告诉我答案吧"
1. Acknowledge without lecturing ("卡了这么久确实烦").
2. Ask one triage question: 不懂题意 / 不知道从哪开始 / 写了但报错 / 结果不对？
3. Offer a choice of the next rung or a similar worked example.
4. If the learner insists again, or the time box is exceeded, or the exercise is not on the mastery path: reveal as a worked example with labelled steps (rung 5 protocol). Do not refuse a second time; refusal loops destroy trust and the learner can get the answer elsewhere anyway.
5. If the request is about something outside the objective (setup, typo hunt in a config file): just fix or answer.
Rationale to share with the learner once, in Stage 0: the 17-point quiz gap, the "comfort trap", and that unassisted checkpoints decide progression. Have the learner write their own AI-use contract and revisit it after each checkpoint.

### 9.6 Allowed AI uses in Stage 2 (complement, not substitute)
Explaining an error message after the learner has tried to read it; generating extra practice variants; reviewing a finished solution with questions; explaining the reference solution after a pass; in L23, supplying code to be reviewed.

### 9.7 Draft custom output style (frontmatter fields taken from the docs; the file itself is untested)
```markdown
---
name: 教练模式
description: 零基础编程教练：给提示，不代写
---
你是一位编程教练。学习者是零基础的成年人，用简体中文交流；术语第一次出现时附英文原词。

硬性规则
1. 不修改 exercises/ 下的任何文件，也不替学习者写当前练习的答案。
2. 学习者还没有自己尝试并运行 `uv run learn.py` 之前，不给提示。
3. 每次只给一级提示，顺序是：澄清 → 定位 → 概念 → 同类例题 → 骨架 → 揭示。记录到了第几级。
4. 遇到报错不直接修：先请学习者读最后一行，说出假设和验证办法。
5. 讲解之后必须出一道预测题或请学习者用自己的话复述，不问“懂了吗”。
6. 与本题学习目标无关的问题（工具故障、英文单词、还没学到的语法）直接回答。
7. 学习者第二次明确要答案，或单题超过 25 分钟：以带步骤标签的范例形式给出，随后请其逐行解释，并把该题记为“有协助”，安排变式题。
8. 每轮回复简短，只问一个问题；不说“很简单”“显然”；肯定过程，不评价天赋；不确定时明说。
9. 阶段考核（checkpoint）期间不提供任何帮助。
```
`keep-coding-instructions` is left at its default (false) because the docs say to omit it when Claude is not doing software engineering; builders should try both settings. Pair the style with a hook that denies Edit/Write under `exercises/` (guarantee) and with `CLAUDE.md` for project facts (commands, folder map, where `.progress.json` and the learner-model file live).

---

## 10. Pitfalls a beginner will hit

1. Chinese input method: full-width `（ ） ： ； ，` and curly quotes inside code produce `SyntaxError: invalid character`. Teach it in lesson 1.
2. Naming a file `random.py`, `test.py`, `math.py` or `turtle.py` shadows the standard library; 3.14's message says so explicitly.
3. `input()` returns text; `"18" + 1` fails; `"18" * 2` silently gives `1818`.
4. `print` versus `return`; functions that return `None`.
5. Forgetting to call (`s.upper` without parentheses) gives no error, just strange output.
6. Editing a file and not saving before running.
7. Running from the wrong folder: relative paths depend on the terminal's current directory.
8. Infinite loops: learn Ctrl-C in the while lesson.
9. Reading only the first line of a traceback; the conclusion is on the last line.
10. Aliasing: `b = a` on lists; mutable default arguments.
11. Off-by-one with `range` and slicing.
12. Copying error text into the AI before reading it (the pattern with the worst learning outcome).
13. Believing a passed exercise means understanding (illusion of competence).
14. Old tutorials: `python -m venv`, `pip install`, `source .venv/bin/activate`, `typing.List`, "parentheses are required after except", screenshots of terse error messages.
15. `uv init` output (a `main()` function and `__name__` idiom) on day one.
16. Parsons files show editor errors until solved; raw `uv run pytest` shows every unfinished exercise.
17. Floating point surprises (`0.1 + 0.2`), `round(2.5)` is 2.
18. A workspace on an iCloud-synced Desktop: a `.venv` with thousands of files inside a synced folder is a known source of trouble (not tested today; another brief should own this).

---

## 11. Plain-Chinese analogies that survive later lessons

- 解释器：极其听话、毫无常识的实习生，一行一行照做。
- 变量：贴在值上的名字标签（不是盒子）。盒子比喻在列表上会失效，标签比喻一直成立。
- `=`：读作"设为"。先算右边，再贴标签。
- 引用：同一份在线文档的两个链接；`copy()` 才是复印。
- 可变与不可变：白板可以擦改；打印好的纸只能换一张。
- 函数：小机器或菜谱。参数是进料口，`return` 是出料口；`print` 只是念出来。
- 调用栈：每次调用发一张新草稿纸，函数结束就收走。
- 列表：一排从 0 开始编号的储物柜（编号是"离开头几格"）。
- 字典：通讯录，按名字查而不是按位置。
- 缩进：表示"属于谁"。
- 异常和 traceback：事故单，最后一行是结论，上面是事发地点。
- 调试：看病。症状，假设，化验，确诊，治疗，复查。
- 测试：验收清单。
- 类与对象：表格模板与填好的表。
- 虚拟环境：每个项目自己的工具箱，uv 负责管理。
- AI 助手：汽车而不是自行车；想锻炼身体就得自己走。

---

## 12. Challenges to the planned product

1. "Coach, not ghost-writer" is necessary and not sufficient: the TUM trial's scaffolded tutor improved scores and motivation, not learning. Progress must be defined by unassisted checkpoints.
2. The default Claude Code Learning style does not fit; custom style plus hook enforcement is needed.
3. The exercise system must support non-writing kinds (predict, trace, Parsons, fix, explain), not only failing tests.
4. Roadmap order: the plan goes Python (stages 2-3), then JavaScript (stage 4), then back to Python for backend (stage 5), then TypeScript (stage 6). Transfer between languages only works after mastery (tip 7). Consider: HTML/CSS and "how the web works" after stage 3, then SQL and FastAPI in Python, and JavaScript/TypeScript/React only after that; or at least gate stage 4's JavaScript behind the stage 2 exam (judgment).
5. Twenty-five lessons is a skeleton, not a time budget: plan 80-130 hours and say so to the learner.
6. A local, solo workspace loses the two best-evidenced social techniques (peer instruction, pair programming). Add an optional human touchpoint (Exercism mentoring is free; a periodic human code review).
7. Stages 2 and 3 should overlap slightly: the learner runs tests from lesson 1, writes them in L20, sees type hints from L9, commits after every lesson. Keep ruff, typing strictness and project structure for stage 3 so that stage 2 keeps one toolchain.
8. Hiding solutions is pointless when an AI is one click away; rely on the contract, the hint ladder and the checkpoints.
9. The handbook should be written by the learner (generation and self-explanation), reviewed by the AI, never drafted by it.
10. Version: plan says 3.14, current stable is 3.15. Keep 3.14, pin it, and decide deliberately whether `requires-python = ">=3.14"` (which makes ruff emit 3.14-only syntax) is wanted.

---

## 13. Not verified

- PRIMM effect size and the full journal paper (publisher and repository returned 403); I relied on Sentance's own seminar paper.
- Numbers of Margulieux 2020, Kestin 2025, Nie 2024, Fan 2024, Lopez 2008, Garner 2019, Selvaraj 2021, Qian and Lehman 2017, Sorva 2013: abstract or search-summary level only.
- Bastani's actual tutor prompts; Kestin's prompt text.
- Contents of The Programmer's Brain beyond the publisher page and chapter 1 headings.
- Real Python path contents (403); CS50P Chinese subtitles; official Simplified Chinese editions of ATBS 3e and Think Python 3e (none found, which is not proof of absence); the Chinese edition of Python Crash Course 3e.
- Exercism zh-CN coverage beyond the one exercise page opened; futurecoder's Chinese translation quality.
- Interactive REPL behaviour (no pty in sandbox); VS Code debugger flow; Python Tutor's supported Python version.
- Hook-based blocking of tutor edits; behaviour of a custom output style in the desktop app.
- iCloud interaction with `.venv` and file watching.
- Hours per lesson, exercises per lesson, the 80 percent mastery threshold and the 25-30 minute time box are judgment calls, not measured values.
- The functions-before-loops versus loops-before-functions question has no decisive evidence that I found.

---

## 14. Source list

Pedagogy: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006023 · https://teachtogether.tech/en/index.html · https://primmportal.com/ · https://www.raspberrypi.org/app/uploads/2022/08/Teaching_Programming_with_PRIMM-1.pdf · https://acris.aalto.fi/ws/portalfiles/portal/131069230/Parsons_Problems_and_Beyond_-_Systematic_Literature_Review_and_Empirical_Study_Designs_.pdf · https://faculty.washington.edu/ajko/papers/Xie2019IntroCSTheoryOfInstruction.pdf · https://computingeducation.de/pub/2019_Michaeli-Romeike_WIPSCE19.pdf · https://progmiscon.org/misconceptions/Python/ · https://en.wikipedia.org/wiki/Mastery_learning · https://www.manning.com/books/the-programmers-brain · https://pythontutor.com/ · https://computinged.wordpress.com/

LLM studies: https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html · https://www.anthropic.com/news/AI-assistance-coding-skills · https://arxiv.org/abs/2601.20245 · https://portal.fis.tum.de/en/publications/less-stress-better-scores-same-learning-the-dissociation-of-perfo/ · https://arxiv.org/abs/2405.17739 · https://arxiv.org/abs/2302.07427 · https://arxiv.org/abs/2409.09047 · https://cs.harvard.edu/malan/publications/V1fp0567-liu.pdf · https://arxiv.org/abs/2401.11314 · https://www.anthropic.com/news/anthropic-education-report-how-university-students-use-claude · https://ideas.repec.org/a/pal/palcom/v12y2025i1d10.1057_s41599-025-04787-y.html · https://code.claude.com/docs/en/output-styles

Curricula and formats: https://cs50.harvard.edu/python/ · https://www.py4e.com/lessons · https://automatetheboringstuff.com/ · https://nostarch.com/automate-boring-stuff-python-3rd-edition · https://allendowney.github.io/ThinkPython/ · https://docs.python.org/zh-cn/3.14/tutorial/index.html · https://exercism.org/tracks/python · https://liaoxuefeng.com/books/python/introduction/index.html · https://programming-26.mooc.fi/ · https://futurecoder.io/ · https://rustlings.rust-lang.org/usage · https://github.com/gregmalcolm/python_koans

Language and tools: https://www.python.org/downloads/ · https://docs.python.org/3.14/whatsnew/3.14.html · https://docs.python.org/3.15/whatsnew/3.15.html · https://docs.python.org/3.14/tutorial/appendix.html · https://docs.pytest.org/en/stable/reference/customize.html · https://docs.pytest.org/en/stable/changelog.html
