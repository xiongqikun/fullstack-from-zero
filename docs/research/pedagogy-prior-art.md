# Brief — pedagogy-prior-art

Instructional design and prior art for a self-paced, hands-on, Chinese-language course teaching a beginner "engineering-grade development and management norms". Research date: 2026-11-19.
Claim tags: **[local]** = I ran it on this machine today · **[source: URL]** = read in a primary source today · **[memory]** = not verified today.

## 0. What was verified, and how

- **Web**: WebSearch + WebFetch both worked. Every prior-art site named in the task was opened today except Real Python (HTTP 403 to both curl and WebFetch — bot protection; search index confirms the pages exist). Also blocked for automated reading: pnas.org (403), nature.com (cookie redirect), PubMed HTML (cookie wall), eng-practices-cn.xindoo.xyz (403). Work-arounds used: NCBI E-utilities for PubMed abstracts, OpenAlex/Crossref for 60 DOIs (57 resolved and every returned title matched the intended paper; 3 lookups dropped the connection), arXiv API, Europe PMC full text (Kestin 2025), local text extraction of the Bjork & Bjork 2011 PDF (WebFetch downloaded it; curl reported a certificate-chain error for that host).
- **URL liveness**: 119 candidate URLs fetched with curl; results in `urlcheck1.txt`, `urlcheck2.txt`, `urlcheck3.txt` next to this file. Everything recommended in §11 returned 200 today.
- **Local**: git 2.54.0 (Apple Git-157), Python 3.14.9 (`python3`), 3.12.15, system 3.9.6, uv 0.13.5, ruff 0.17.2, GNU Make 3.81, pytest 9.2.0 (installed only inside a scratch venv). Prototypes that I ran end to end are in `proto/`: `check.py` (auto-checker with hint ladder), `quiz.py` (diagnostic multiple choice), `pytest-variant/test_l01.py`, `sim/` (two collaborators + bare repo).
- Nothing was written outside the scratch directory; global git config was only read, never changed; throwaway repos use repo-local config.

## 1. Most decision-relevant findings

1. **Lesson 1 can break on a Mac with a half-written signing config unless handled**: if `~/.gitconfig` has `commit.gpgsign=true` + `gpg.program=gpg`, but no `gpg` binary exists (PATH, Homebrew, MacGPG2), every `git commit` fails with `error: cannot run gpg: No such file or directory … fatal: failed to write commit object` [local]. Repo-local `git config --local commit.gpgsign false` fixes it [local]. A "环境体检" (preflight) step must come before the first commit, and the fix to *global* config must be the learner's own decision.
2. **No existing resource fits this course's target learner.** Each prior-art item fails on at least one of: Chinese, beginner level, current tooling (uv/ruff/`git switch`/`main`), auto-verification, working with an AI agent. The closest models to copy are: Software Carpentry's episode template (structure), GitHub Skills (state-triggered progress), rustlings / Oh My Git! (check loop + hints + win conditions), Missing Semester 2026 (scope, incl. "Agentic Coding" and "Beyond the Code"), Good Research Code Handbook (tone for researchers, "5-minute exercise").
3. **Evidence on AI and learning is now direct (2025–2026 RCTs)**: unguarded AI help raises practice performance but lowers later unaided performance (PNAS 2025: +48% practice, −17% exam); in a 52-developer RCT the AI group scored 50% vs 67% on a comprehension quiz with no significant speed gain, the largest gap being debugging; the learners who kept their scores asked *conceptual* questions or demanded explanations, those who delegated scored <40% (Anthropic, Jan 2026). A *structured* AI tutor that withholds answers and follows a fixed lesson sequence beat an active-learning class (Harvard RCT, 2025). Design consequence: structure and checks must live in lesson files and scripts, not only in instructions to the AI.
4. **Claude Code already ships a learning mode**: built-in output style `Learning` (adds `Insight` blocks, leaves `TODO(human)` code for the learner). In the desktop app it is selected by `"outputStyle": "Learning"` in a settings file such as `.claude/settings.local.json` (value is case-sensitive) [source: https://code.claude.com/docs/en/output-styles]. The desktop app has a Terminal pane (Ctrl+`) and a `!` prefix so the learner can run commands personally [source: https://code.claude.com/docs/en/desktop].
5. **A plain-Python checker beats raw pytest as the course's feedback channel** for early lessons: my stdlib-only prototype gives "observed → expected → hint" in Chinese and stops at the first failing check; raw pytest output is English, noisy, and truncates Chinese messages [local]. Teach pytest as a subject; do not make beginners read it as course feedback before the testing module.
6. **Older Chinese tutorials are conceptually good but command-stale**: 廖雪峰, Pro Git 中文版 and 阮一峰's cheat sheet all use `master` and `git checkout -- <file>` / `git reset HEAD <file>`; this Mac creates `main` and git's own hints say `git restore` [local + sources in §8]. Recommend them as reading *with a "what differs today" box*.
7. **Git on this Mac speaks English only** (no locale files ship with Apple Git) and shows Chinese file names as octal escapes by default [local]. Lessons must quote English output with Chinese glosses and use ASCII file names (or set repo-local `core.quotepath false`).
8. Recommended lesson size: 30–45 min, ≤3 new concepts, 3–5 checked steps, opening with closed-book recall of earlier lessons, ending with a state check + teach-back; reviews at +1/+3/+7/+21 days (§5).

## 2. Local verification (commands actually run, real output)

### 2.1 Commit-signing blocker and its repo-local fix [local]
```console
$ git init                       # → "Initialized empty Git repository …"; branch is already `main`
$ git add -A && git commit -q -m "docs: 添加学习笔记"
error: cannot run gpg: No such file or directory
error: gpg failed to sign the data:
fatal: failed to write commit object
$ git config --show-origin --show-scope --get-all commit.gpgsign
global	file:/Users/<user>/.gitconfig	true
$ which gpg gpg2          # → not found (also absent from /opt/homebrew/bin, /usr/local/bin, /usr/local/MacGPG2/bin)
$ git config --local commit.gpgsign false && git commit -q -m "docs: 添加学习笔记" && git log --oneline
283928b docs: 添加学习笔记
```
Reproduced in Claude's sandboxed shell on a Mac whose global config turns signing on without gpg; the PATH there already includes `/opt/homebrew/bin`, so an interactive terminal on such a Mac very likely fails the same way (not run there, §12). An annotated tag (`git tag -a`) succeeded without signing [local].

### 2.2 Other git behaviour relevant to lesson and checker design [local]
- `init.defaultbranch main` comes from `/Applications/Xcode.app/Contents/Developer/usr/share/git-core/gitconfig`, so `git init` yields `main` silently even though the user-level setting is unset.
- Chinese paths are escaped by default; `core.quotepath=false` fixes it:
  ```console
  $ git status --short                      →  ?? "\345\255\246\344\271\240\347\254\224\350\256\260.md"
  $ git -c core.quotepath=false status --short  →  ?? 学习笔记.md
  ```
  Chinese commit messages display correctly in `git log`.
- Output is English even with `LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8` (`…/share/locale` does not exist for this git). Current hints: `(use "git restore --staged <file>..." to unstage)`, `(use "git restore <file>..." to discard changes in working directory)`.
- Plain `git pull` on divergent branches is fatal: `hint: You have divergent branches and need to specify how to reconcile them. … fatal: Need to specify how to reconcile divergent branches.` (exit 128). Lessons must teach `git pull --no-rebase` / `--ff-only` or set repo-local `pull.rebase false`.
- New-style subcommands work: `git config list --local`, `git config get commit.gpgsign` (git's own hint text now says `git config set …`).
- **Nested-repo trap**: inside a sub-folder of a parent repo, `git rev-parse --is-inside-work-tree` prints `true` although the folder has no `.git`. A checker must compare `git rev-parse --show-toplevel` with the exercise directory. `git add .` in a parent that contains a practice repo prints `warning: adding embedded git repository: playground/ex01` plus a 14-line hint block; adding `playground/` to the parent `.gitignore` removes the problem.
- `git check-ignore -q .venv/nonexistent` returns 0 for a path that does not exist, so ignore rules can be checked without creating files.
- **Offline collaboration works with a bare repo** (`git init --bare team.git`, two clones): second pusher gets `! [rejected] main -> main (fetch first)`; `git pull --no-rebase` then produces `CONFLICT (content): Merge conflict in notes.md` with standard markers. Remote/PR-style lessons therefore need no GitHub account or network.
- With iCloud "Desktop & Documents" sync on, the Desktop and Documents folders are stored in iCloud Drive (Apple Support 109344, https://support.apple.com/en-us/109344): anything under them, including `.git` and `.venv`, is synced unless excluded (consequences: §9).

### 2.3 Chinese output from scripts; interpreter selection [local]
- `python3` 3.14.9 prints Chinese and emoji correctly even with `LC_CTYPE=C` (`sys.flags.utf8_mode == 1`, stdout `utf-8`), also when piped; system Python 3.9.6 does too. A Chinese-language checker needs no locale setup.
- `uv venv` in the sandbox picked **CPython 3.12.15**, not the 3.14.9 that `python3` resolves to. `uv python list --only-installed` showed 3.14.9 under a custom install directory (for example one set with `UV_PYTHON_INSTALL_DIR`) and 3.12.15 under uv's default `~/.local/share/uv/python/`; the likely cause is that uv prefers its own managed directory, and no `UV_*` variable other than the cache dir is set in the sandbox shell (inference, not confirmed). Lessons should pin the interpreter (`.python-version` / `requires-python`) and checkers should print the interpreter they run under.

### 2.4 Auto-checker prototype (`proto/check.py`, stdlib only, runs on 3.9–3.14) [local]
Lesson "first commit" = five ordered state checks (is a repo root → `.gitignore` ignores `.venv/` → ≥1 commit → subject matches `type: description` → clean tree). Real output of three consecutive runs:
```text
  ❌ [1/5] 练习文件夹是一个 Git 仓库
  我看到的情况：这个文件夹里还没有 .git（它还不是 Git 仓库）
  期望的状态：  练习文件夹是一个 Git 仓库
  先自己想 2 分钟。需要提示时运行： python3 check.py L01 --hint
  ⚠️ 环境提醒：你的 Git 配置要求给每个提交做 GPG 签名（commit.gpgsign=true），但这台电脑上找不到 gpg 程序……这不是你的操作错误。
  （后面还有 4 项检查，通过这一项后再看。）
--- after `--hint` twice ---
  💡 提示 1/3：想一想：Git 把「历史记录」存在哪里？这个文件夹里现在有那个隐藏目录吗？（试试 ls -a）
  💡 提示 2/3：需要用到「初始化」仓库的命令：git 后面跟一个表示“初始化”的英文单词。
--- later, bad commit message ---
  ❌ [4/5] 提交标题符合「类型: 描述」的约定（如 docs: 添加项目说明）
  我看到的情况：最近一次提交的标题是：「first commit」，不符合「类型: 描述」的格式
--- all green ---
🎉 本课全部 5 项检查通过！（共尝试 11 次，用了 5 级提示）
合上教程，回答下面的回想题（写进 学习日志.md）： …
复习安排：2026-11-20、2026-11-22、2026-11-26、2026-12-10
```
Exit code 0 on pass, 1 otherwise, 2 for usage errors; state in `.learning/progress.json` (attempts, per-check fails, hint level, pass date, review dates). Two defects found while testing, to avoid in the real tool: (a) hint level was keyed by lesson+check only, so a second exercise directory inherited revealed hints — key state per exercise and reset the ladder when a check passes; (b) the preflight warning repeats on every run — show it once, in a dedicated preflight lesson.

### 2.5 pytest as a feedback channel [local]
Same checks as pytest tests with Chinese assertion messages (pytest 9.2.0). Default run prints source lines, `E assert (': ' in 'first commit')`, English banners, reports *all* failures, creates `.pytest_cache/`, and the summary line truncates the Chinese text: `FAILED test_l01.py::test_02_提交标题符合约定 - AssertionError: 最近一次提交的...`. Quietest readable form: `pytest -x -q --tb=line --no-header -p no:cacheprovider`; the full message survives only in the traceback line or with a wide terminal (`COLUMNS=200`). Conclusion in §1 item 5.

### 2.6 Diagnostic multiple-choice prototype (`proto/quiz.py`) [local]
Each wrong option maps to one misconception with its own feedback; the right letter is never revealed after a miss. Run with scripted answers A, D, B:
```text
你的答案（A/B/C/D）：❌ 还不对。这是把“暂存区”想成了“文件名清单”。暂存区存的是 add 那一刻的内容快照…… 再想想，重新选。
你的答案（A/B/C/D）：❌ 还不对。第二次修改还停留在工作区，没有经过 git add，所以进不了这次提交。 再想想，重新选。
你的答案（A/B/C/D）：✅ 对。git add 是给“当时的内容”拍照放进暂存区；commit 只提交暂存区。……
```
The scenario itself was verified: after edit → `git add` → edit again, `git status` lists the file under both `Changes to be committed` and `Changes not staged for commit`, and the commit contains only the staged version. Needs an interactive terminal (`input()`); it cannot be driven through Claude's Bash tool without piping.

## 3. Prior-art survey (all read today unless marked)

| Resource | Structure and length | Practice · progress verification | Does especially well | Missing for this learner |
|---|---|---|---|---|
| **MIT Missing Semester 2026** [source: https://missing.csail.mit.edu/] | "nine 1-hour lectures" (Jan 2026), "substantially revised material": Shell · Command-line Environment · Development Environment and Tools · Debugging and Profiling · Version Control and Git · Packaging and Shipping Code · Agentic Coding · Beyond the Code · Code Quality. Notes + video. | 6–18 exercises per lecture, open-ended, **no solutions**, no checker ("the real value … is the journey of discovering the answers"). | Current scope (uv, ruff, pre-commit, CI, agents); Git taught data-model-first; "Beyond the Code" covers commit messages, README, issues, PRs, review, AI etiquette. | Written for CS students at ease in a shell; dense; English. Chinese site missing-semester-cn.github.io shows the 2026 syllabus but the 2026 Git page body is still English; the complete Chinese Git translation is the 2020 edition. |
| **Software Carpentry** shell / git / Python [source: https://swcarpentry.github.io/git-novice/instructor/index.html] | Episodes: shell 7 (4 h 30 m), git 14 (3 h 12 m; episodes of 2–45 min), Python 12 (≈7.5 h). Git lesson has a running story (two colleagues keeping a restaurant's recipes under version control). | Fixed episode template: Overview box (Questions, Objectives) → prose → command → output → callouts → Challenges with collapsed solutions (multiple choice + hands-on) → Key Points. No automatic checking; designed for live teaching. | True-novice pacing; misconception-probing multiple choice; evidence-based design (Instructor Training). | No Chinese (only Spanish listed); no lint/type/CI/uv; no testing lesson in the core (Python lesson stops at Defensive Programming and Debugging). |
| Carpentries Incubator: Python Testing and CI; Intermediate Research Software Development [source: https://carpentries-incubator.github.io/python-intermediate-development/] | Testing lesson: 12 episodes, **alpha, last built 2020-07-27**. Intermediate lesson (beta): 5 sections from environments → testing/CI → design → code review/release → project management. | Same template; optional exercises. | The intermediate lesson is the closest match in *scope* to this course. | Assumes Git, shell and Python; teaches `python3 -m venv` + pip + `requirements.txt`, no uv. |
| **The Good Research Code Handbook** (Mineault, 2021) [source: https://goodresearch.dev/] | 8 lessons: set up project · keep things tidy · decoupled code · test · document code · document project · make it social · sample project. | One "5-minute exercise" per lesson (e.g. turn a commented-out print into an assert); no checks. | Voice aimed at researchers with notebooks; "one project = one paper = one folder = one git repository"; testing numerical code; test progression assert → pytest → CI. | Tooling frozen in 2021–23 (conda, `setup.py`, Python 3.8, no `pyproject.toml`/uv); repo last pushed 2023-10-11. |
| **The Turing Way** [source: https://book.the-turing-way.org/] | Handbook, 5 guides; Guide for Reproducible Research has 17 chapters (Version Control … Code Quality, Code Testing, Code Reviewing Process, CI, Make …). Meant to be dipped into by topic, not read in order. | None. | The *why* of reproducibility and collaboration; checklists. | Reference, not a course. |
| **Scientific Python Development Guide** [source: https://learn.scientific-python.org/development/] | Tutorials (5 pages) → Topical guides → Principles → Patterns; `repo-review` checker; `cookie` template. Repo pushed 2026-11-16. | None for the learner; `repo-review` checks a repository against the guide. | Most current tooling reference: ruff for format + lint, "pre-commit (or prek)", MyPy default with Pyrefly and ty shown alongside. | States it does not cover version control; maintainer-oriented; English. |
| **Hypermodern Python** [source: http://blog.claudiojolowicz.com/posts/hypermodern-python-01-setup/] | 6 articles (first one dated 2020-01-01): setup, testing, linting, typing, docs, CI/CD. Old github.io URL now redirects. | Follow-along project. | Shows the whole "ideal project" in order. | pyenv + Poetry + Nox + Black/Flake8; template pins 2022.6.3, no ruff/uv. Historical only. |
| **Software Engineering at Google** [source: https://abseil.io/resources/swe-book/html/toc.html] | Free HTML (CC BY-NC-ND 4.0); 25 chapters + afterword in parts Thesis / Culture / Processes / Tools. | Reading only. | Why norms exist: ch. 1, 3, 8, 9, 10, 11, 12, 16, 23 suit beginners. | Scale far from a solo project. Chinese: bilingual community translation github.com/qiangmzsx/Software-Engineering-at-Google. |
| **Google Engineering Practices** [source: https://google.github.io/eng-practices/review/reviewer/standard.html] | Code-review guides for reviewers and for change authors. | Reading only. | The review standard: approve once a change "definitely improves the overall code health … even if the CL isn't perfect"; `Nit:` prefix for optional comments. | GitHub repo is archived (last push 2024-09-19); site still loads. Chinese: github.com/xindoo/eng-practices-cn. |
| **GitHub Skills** [source: https://github.com/skills/introduction-to-github] | Courses are template repos copied into the learner's account. Intro course ("takes less than one hour"): create a branch → commit a file → open a PR → merge. | **State-triggered verification**: a workflow fires on the learner's real action (e.g. push to branch `my-first-branch`) and posts the next step as an issue comment (steps in `.github/steps/*.md`, logic in `skills/exercise-toolkit`). | Automatic progress detection inside the real tool. | Needs a GitHub account; English; web-UI flows; pinned courses today are mostly Copilot/agent topics. skills.github.com now redirects to learn.github.com/skills. |
| **Learn Git Branching** [source: https://github.com/pcottle/learnGitBranching] | Browser app; 7 sequences, 36 levels (intro 4, rampup 4, move 4, mixed 5, advanced 3, remote 8 + 8). | Each level has a `goalTreeString` and a `solutionCommand`; solved state shown per level. | Best visual model of the commit graph; **zh_CN locale** (`?locale=zh_CN`); MIT; pushed 2026-11-17. | Simulated git, not the learner's repo. |
| **Oh My Git!** [source: https://github.com/git-learning-game/oh-my-git] | Game on real git; levels are text files with `[description]`, `[setup]` (bash), `[win]` (bash returning 0). | Win conditions are shell checks on repo state. | Proof that "win = commands that inspect state" works. | "Low-maintenance mode", Godot 3 only, last push 2025-12-02; running the macOS build on this machine not tested. |
| **Real Python** (project layout, pytest) | Long-form tutorials, some with quizzes [memory]. | — | — | Could not be read (403). Verify in a browser before recommending. |
| **廖雪峰 Git 教程** [source: https://liaoxuefeng.com/books/git/introduction/index.html] | 13 chapters, tiny steps, story of "时光机穿梭"; self-described "史上最浅显易懂的Git教程". | No exercises or quizzes; video available. | Plain Chinese, motivation, pacing. | Uses `master`; undo chapter teaches only `git checkout -- file` and `git reset HEAD <file>` (no `git restore`); branch chapter teaches both `checkout -b` and `switch -c`. |
| **阮一峰** articles [source: https://www.ruanyifeng.com/blog/2016/01/commit_message_change_log.html] | Commit-message guide (2016-01-06), Git 工作流程 (2015-12-24), 常用 Git 命令清单 (2015-12-09). | Reading only. | Clear concept explanations: Header/Body/Footer, Git flow vs GitHub flow vs GitLab flow. | Tool sections dated (validate-commit-msg deprecated per reader comments; cheat sheet has no `switch`/`restore`). |
| **Pro Git 中文版** [source: https://git-scm.com/book/zh/v2] | 10 chapters + 3 appendices; PDF/EPUB (2.1.80); CC BY-NC-SA 3.0; translation repo pushed 2026-11-04. | Reading only. | Authoritative; source of standard Chinese Git terms. | zh §2.4 still teaches `git reset HEAD <file>` / `git checkout -- <file>`; default branch `master`. |
| **Python最佳实践指南** (Hitchhiker's Guide zh) [source: https://pythonguidecn.readthedocs.io/zh/latest/] | Parts on installation, environments, "写出优雅的Python代码" (结构化您的工程 / 代码风格 / 测试您的代码). | Reading only. | Concept chapters on structure and style, in Chinese. | © 2011–2018; pipenv/virtualenv; Python 2 vs 3. |
| Chinese norm references | Google 风格指南中文版 (Python); 约定式提交; 语义化版本; 如何维护更新日志; 开源指南 (13 guides); 中文技术文档的写作规范; 中文文案排版指北; CS自学指南. | Reading only. | Standards with official or widely used Chinese text. | None is a course. |
| Other models worth copying | **rustlings**: watch mode re-runs the current exercise on every file save, `h` gives a hint, `l` lists progress [source: https://rustlings.rust-lang.org/usage/]. **git-katas**: one folder per kata with `setup.sh`, suggested path of 16 katas, "deliberate Git practice" [source: https://github.com/eficode-academy/git-katas]. **Exercism**: download → run tests locally → submit; optional HINTS.md. **py-rse** (free book, exercises with solutions in an appendix). **CodeRefinery** lessons incl. "Responsible Use of Generative AI in Assisted Coding" (chat / IDE / agentic scenarios). | | | |

## 4. Evidence-based principles → concrete lesson rules

| Principle (source) | What the evidence says | Rule for this course |
|---|---|---|
| Cognitive load (Sweller 1988, *Cognitive Science* 12(2); Sweller, van Merriënboer & Paas 2019; Cowan 2001: about four chunks) | Problem-solving search consumes the capacity novices need for building schemas. | One new idea per step; ≤3 new concepts and ≤5 new commands per lesson; command, expected output and one-line explanation adjacent; everything except the target skill pre-made. Follow Diátaxis for tutorials: "ruthlessly minimise explanation", "ignore options and alternatives" [source: https://diataxis.fr/tutorials/]. |
| Worked examples + fading (Sweller & Cooper 1985; Renkl & Atkinson 2003; Atkinson, Renkl & Merrill 2003) | Worked examples beat problem solving early; fading steps plus prompts to name the principle gave medium-to-large near and far transfer "without requiring additional time on task". | Every lesson: full demo → partly completed task → independent task. Each demo step ends with a "why" prompt. Label sub-goals (Margulieux 2012; Brown & Wilson 2018 tip 6; results for programming tasks were mixed in Morrison et al. 2015). |
| Expertise reversal (Kalyuga et al. 2003; Kirschner, Sweller & Clark 2006) | Techniques that help novices "can lose their effectiveness and even have negative consequences" for experienced learners; guidance matters until prior knowledge is high. | Guidance shrinks module by module; offer a "test-out" (pass the checkpoint first, skip the walkthrough); later lessons give goals, not steps. |
| Retrieval practice (Roediger & Karpicke 2006; Karpicke & Roediger 2008; Dunlosky et al. 2013) | Testing beat re-studying at 2 days and 1 week although re-study felt better; practice testing and distributed practice are "high utility", rereading and highlighting "low". | Open each lesson with 3 closed-book questions on older lessons; end with "close the tutorial and answer"; learner writes the cheat-sheet from memory first, then corrects it. |
| Spacing (Cepeda et al. 2006: 317 experiments; Cepeda et al. 2008) | Optimal gap grows with the retention goal: ~20–40% of a 1-week delay, ~5–10% of a 1-year delay. | Reviews at +1, +3, +7, +21 days, printed by the checker; 30–45 min a day rather than weekend marathons. |
| Interleaving and variation (Rohrer & Taylor 2007; Bjork & Bjork 2011) | Mixed practice slows practice but improves later performance. | Review sets mix Git, tests and lint; repeat each skill in a new context (toy package → the learner's own project, if any). |
| Desirable difficulties; learning ≠ performance (Bjork & Bjork 2011 [source: https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf]; Soderstrom & Bjork 2015; Deslauriers et al. 2019) | "Conditions of learning that make performance improve rapidly often fail to support long-term retention and transfer." Difficulties are desirable only if the learner can respond successfully. Students in active classes learned more but *felt* they learned less. | Tell the learner in lesson 0 that effort is the signal of learning; never reward speed; guarantee eventual success through the hint ladder. |
| Productive failure (Kapur 2008, 2014; Sinha & Kapur 2021: 53 studies, g = 0.36 for problem-solving-first; reversed for domain-general skills and young learners) | Trying before being told helps conceptual understanding when followed by instruction. | ≤5-minute "先试后讲" only for conceptual questions the learner can reason about (e.g. "how would you keep versions without Git — what breaks?"), never for syntax; always contrast their attempt with the canonical answer. Bug hunts happen in throwaway repos. |
| Feedback (Hattie & Timperley 2007; Shute 2008; Metcalfe 2017) | Formative feedback should be "nonevaluative, supportive, timely, and specific"; errors followed by corrective feedback help, most of all for confident errors. | Checker spec in §5.5; predictions are written down before running so that errors are noticed. |
| Assistance dilemma and hints (Koedinger & Aleven 2007; Aleven et al. 2016; Marwan, Williams & Price 2019) | On-demand help "helps, but only so much"; code hints improved a later task only "when they were combined with self-explanation prompts". | Three-level ladder, on request; the last level gives the command and then asks for an explanation in the learner's words; hint use is recorded and triggers a later variant. |
| Mastery learning (Bloom 1984; Kulik, Kulik & Bangert-Drowns 1990: 108 evaluations) | Formative test → correctives → parallel test works, especially for weaker students; but "self-paced mastery programs often reduce the completion rates". | Light gates: a module is done when its checkpoint passes; on failure give a parallel variant, never a dead end. |
| Predict-then-run (Brown & Wilson 2018 tip 4; PRIMM, Sentance et al. 2019: 13 schools, 493 pupils; Lister et al. 2004) | Demonstrations alone teach little; predicting first exposes the mental model; novices are weak at tracing. | Before each new command: write what you expect, run, compare, explain the difference. |
| Self-explanation and teach-back (Chi et al. 1989; Nestojko et al. 2014; Roscoe & Chi 2007; Chi & Wylie 2014) | Good learners explain examples to themselves; expecting to teach improves organisation; tutors drift into "knowledge-telling". | Lesson ends with a 3-sentence explanation to the AI playing a curious newcomer who asks "why?" and does not correct until the learner finishes. |
| Deliberate practice (Ericsson, Krampe & Tesch-Römer 1993) | Improvement comes from effortful practice on specific weaknesses with feedback. | Short katas generated from the checks the learner failed most (the checker stores fails and hint levels). |
| Motivation (Brown & Wilson tip 8; Wilson ch. 10; Ryan & Deci 2000; Gollwitzer 1999) | Authentic tasks; teach first what is "quick to master and immediately useful"; autonomy, competence, relatedness; if-then plans raise follow-through. | Each module ends with "带回你的项目" on the learner's own project (if any); visible progress (`--status`, git log, tags); lesson 0 asks for an if-then study plan. |
| Mental model first (Wilson ch. 2; Missing Semester Git lecture) | Novices "don't yet have a usable mental model of the problem domain"; the MIT lecture teaches Git's data model before its commands on the grounds that a design can be understood whereas an interface can only be memorised (paraphrase). | Draw 工作区 / 暂存区 / 仓库 and the commit graph before the commands; use Learn Git Branching for the picture. |
| Lesson length (Wilson ch. 6; Bradbury 2016) | Wilson: an hour of teaching holds about three to five episodes, each ending in a formative check. Bradbury: published data "do not support the concept of a 10- to 15-min attention limit". | Size lessons by load and by checks, not by an attention-span rule. |

Teaching Tech Together [source: https://teachtogether.tech/en/index.html] is the single best free synthesis (chapters 2–6, 10, 12); its exercise catalogue is the basis of §5.3.

## 5. Recommended lesson design

### 5.1 Lesson template (Markdown skeleton; headings shown in the course language)
```markdown
# 第 N 课：<学完能做到的一件事，用动词开头>
> 预计 30–45 分钟 · 前置：第 N-1 课 · 新概念 ≤3 · 新命令 ≤5 · 练习目录：playground/lessonNN/
## 0 热身回想（3 分钟，不看笔记）      ← 3 questions drawn from earlier lessons (spaced, interleaved)
## 1 为什么要学                        ← one paragraph + one real situation from the learner's own project (if any)
## 2 学完你能……                       ← 2–3 checkable objectives (创建 / 解释 / 修复 …)
## 3 先猜一猜                          ← prediction or ≤5-min try-first question; write the answer down
## 4 跟我做                            ← worked example with labelled sub-goals:
###   4.1 <子目标>：命令 → 预期输出（英文原文 + 中文解释）→ 一句“为什么” → 停一下，用自己的话说
## 5 你来做                            ← faded: A 填空/补全 → B 只给目标、不给步骤
## 6 找茬                              ← a deliberately broken state to diagnose and repair
## 7 检查点                            ← run the checker; 2–3 multiple-choice items with diagnostic distractors
## 8 讲给别人听                        ← teach-back to the AI or the learning log
## 9 小结卡片                          ← terms (EN/中文), commands, one analogy
## 10 带回你的项目（可选）· 延伸阅读（1 中文 + 1 英文，注明哪里已过时）· 下次复习日期
```
### 5.2 Length and pacing
- 30–45 minutes of focused work, 3–5 checked steps, at most two lessons a day, and the next session starts with recall. Reference points read today: Carpentries episodes run 2–50 minutes with whole lessons of 3–4.5 hours split into 7–14 episodes; Missing Semester lectures are one hour each and described by the course as dense; the GitHub Skills introductory course "takes less than one hour"; the Harvard AI-tutor lesson had a median time on task of 49 minutes; the Good Research Code Handbook uses 5-minute exercises.
- Every step must end in something the learner can see (Diátaxis: "deliver visible results early and often").
- Order by Wilson's rule (quick to master + immediately useful first): terminal survival and preflight → local Git → commit conventions and branches → ruff → pytest → type hints and docs → remotes and review (offline bare repo first, GitHub optional) → automation (task runner, hooks, CI) → versions, changelog, releases, issue/milestone management → capstone on the learner's own project (if any).

### 5.3 Exercise types (after Wilson ch. 12, PRIMM, Brown & Wilson)
| Type | Example in this course | Checked by |
|---|---|---|
| Guided step (worked example) | type the shown command, compare with expected output | state check |
| Predict-then-run | "what will `git status` show after …?" | learner compares; quiz item |
| Fill in the blanks (faded) | complete a half-written `.gitignore`, test or commit message | state check |
| Parsons (ordering) | put the six steps of resolving a merge conflict in order | quiz |
| Tracing | draw the commit graph after five commands; then `git log --oneline --graph` | self-check against real output |
| Minimal fix / bug hunt | repo with a secret committed, a failing test, a lint error, a conflict | state check ("win condition") |
| Theme and variation | change one flag and predict the new output | learner compares |
| Refactoring | restructure code while tests stay green | tests + `ruff check` |
| Code review | review a prepared diff with a rubric; write three comments, one marked `Nit:` | AI as second reviewer, with rubric |
| Checkpoint question | multiple choice whose distractors each encode one misconception | quiz script |
| Mini-project | apply the module to the learner's own project (if any) on a branch | checklist + AI review |
| Reflection / teach-back | three sentences in the learning log; explain to the AI | none (journal entry exists) |

### 5.4 Progress tracking
- Machine state: one small JSON file written by the checker (attempts, per-check fails, hint level, pass date, review dates) plus `check.py --status` (verified output: `✅ 第 1 课：…  5/5 项  尝试 11 次`).
- Human-visible progress: the learner's own Git history. Once Git is taught, each finished lesson is a commit and each module an annotated tag, so `git log --oneline` *is* the progress bar and practises the skill being taught.
- A learning log (`journal.md`; ASCII file name because of §2.2) holding predictions, recall answers and teach-back texts.
- Mastery signal: all checks pass and no bottom-level hint was needed; otherwise schedule a variant. Review dates +1/+3/+7/+21 days.
- Practice repos live in a git-ignored `playground/` (or outside the workspace) because of the nested-repo behaviour in §2.2.

### 5.5 How the auto-check script should give feedback
1. Inspect the **state** of files and repos; never ask the learner to paste output.
2. Separate environment problems (missing tool, signing misconfiguration, wrong interpreter) from learner mistakes, in a preflight.
3. Stop at the **first** failing check and say how many remain.
4. Order of every message: what I observed → what was expected → hint. Describe, do not judge ("我看到…", not "你错了").
5. **Hints before answers**: level 1 a question or where to look, level 2 the concept or command family, level 3 the exact command followed by "now say in your own words what it did". Only on request (`--hint`) or after repeated failures. Record the level used.
6. Never repair anything automatically.
7. Accept every correct solution (regex over allowed commit types, not one literal string).
8. Deterministic, offline, under ~2 seconds, stdlib only, exit codes 0/1/2.
9. Chinese prose, English commands; quote git's English phrase with a gloss.
10. Call git with `-c core.quotepath=false`; compare `--show-toplevel` to the exercise directory.
11. On pass: recall questions plus next review dates.
12. Keep checks as short readable functions: in the testing module the learner reads and extends them.
Objective state suits a script; judgement (is this README clear, is this commit message informative) needs a rubric applied by the AI or the learner — Wilson notes automated assessment "only works well at the lowest levels of Bloom's Taxonomy".

## 6. Learning *with* an AI assistant without outsourcing the learning

### 6.1 Evidence (all metadata verified today)
- Shen & Tamkin, "How AI Impacts Skill Formation", arXiv 2601.20245 (Jan 2026) [source: https://www.anthropic.com/research/AI-assistance-coding-skills]: RCT, 52 mostly junior engineers learning the Trio library. Quiz 50% with AI vs 67% without (Cohen's d = 0.738, p = 0.01); time ~23 vs ~25 min (p = 0.391); largest gap on debugging. Six interaction patterns: *AI delegation*, *progressive AI reliance*, *iterative AI debugging* averaged below 40%; *generation-then-comprehension*, *hybrid code-explanation*, *conceptual inquiry* averaged 65% or more. The no-AI group met more errors (median 3 vs 1) and fixed them alone. Caveats stated by the authors: chat assistant rather than an agent (they expect agents to offload more), one-hour task, patterns are correlational.
- Bastani et al., PNAS 122(26) e2422633122 (2025): ~1,000 high-school maths students; plain GPT-4 chat improved practice grades 48% but exam grades fell 17% once access was removed; a tutor version with "prompts designed to safeguard learning" (hints rather than answers, built from teacher-supplied solutions and common mistakes according to press coverage) improved practice 127% and largely removed the harm.
- Kestin et al., *Scientific Reports* 15:17458 (2025): N = 194; a tutor built on seven practices — "(i) facilitating active learning, (ii) managing cognitive load, (iii) promoting a growth mindset, (iv) scaffolding content, (v) ensuring accuracy of information and feedback, (vi) delivering such feedback and information in a targeted and timely fashion, and (vii) allowing for self-pacing" — beat an active-learning class (0.73–1.3 SD). Two design notes: a system prompt alone "could not reliably provide enough structure", so the platform itself walked students through the parts in order; and step-by-step solutions were supplied to the model to keep it accurate.
- Lehmann, Cornelius & Sting, arXiv 2409.09047: substituting learning activities with an LLM lowers understanding, complementing them (asking for explanations) raises it; LLMs "widen the gap" between low and high prior knowledge. Prather et al., ICER 2024 (21 novices): those who struggled "thought they performed better than they did, and finished with an illusion of competence". Kazemitabaar et al., CHI 2023 (69 novices aged 10–17): a code generator during training did not reduce later manual performance — AI is not harmful by itself, the pattern of use is what matters. Gardella et al., arXiv 2604.18538 (2026, n = 22): better performance and lower workload with Copilot, larger (non-significant) drop at a one-week retest.
- Perception is unreliable: experienced developers were 19% slower with AI while believing they were 20% faster (Becker et al., arXiv 2507.09089); learners predict their own retention poorly (Karpicke & Roediger 2008).
- Bjork & Bjork 2011, pp. 60–61: "any time that you, as a learner, look up an answer or have somebody tell or show you something that you could … generate instead, you rob yourself of a powerful learning opportunity."
- Missing Semester 2026, "Beyond the Code" → AI etiquette: disclose meaningful AI use, and do not submit code you cannot explain [source: https://missing.csail.mit.edu/2026/beyond-code/].

### 6.2 Practical rules for the learner ("AI 使用公约")
1. **Try or predict first, then ask.** Write a prediction or a first attempt before any question.
2. **Ask for concepts and hints, not answers** ("解释这个报错的意思，先别给修复命令").
3. **Hands on the keyboard**: type lesson commands yourself in the Terminal pane (or with the `!` prefix); in "你来做" steps the AI neither runs commands nor edits files.
4. **Debug yourself first**: read the message, state a hypothesis, then ask the AI to test the hypothesis.
5. **Generated code must be understood before it is committed**: explain each line back, predict the effect of one change, make that change by hand. If you cannot explain it, it does not go into the repository.
6. **Checkpoints are closed-book and AI-free**; the AI may explain afterwards.
7. **Teach back** with the AI as a curious newcomer.
8. **Delegate only what is already mastered** (expertise reversal), and say so in the commit or PR text.
9. **Weekly no-AI kata** to measure what has really been retained.
10. **Use the AI for what it adds**: reviewer of your commits and PRs with a rubric, generator of extra practice variants, explainer of unfamiliar output, role-play teammate for issues and review.

### 6.3 Claude Code features that support these rules [source: https://code.claude.com/docs/en/output-styles and https://code.claude.com/docs/en/desktop]
- Built-in output styles besides Default: Proactive, Concise, **Explanatory** (adds `Insight` blocks), **Learning** (same blocks, plus "leaves small pieces of code for you to write yourself", marked `TODO(human)`, then waits). Docs caveat: a style "doesn't guarantee that something always happens".
- Desktop app: set `{"outputStyle": "Learning"}` in a settings file such as `.claude/settings.local.json`; `/config` opens Settings there instead of a menu; the value is case-sensitive (`learning` silently gives Default). The `/output-style <name>` command needs Claude Code v2.1.269+; since v2.1.251 a switch applies from the next message. Chinese docs: https://code.claude.com/docs/zh-CN/output-styles.
- Custom style: a Markdown file in the project's `.claude/output-styles/` with front matter `name`, `description`, `keep-coding-instructions: true` — a route to a Chinese tutor persona.
- `CLAUDE.md` in the project is read by the desktop app and the CLI alike.
- Permission modes are now labelled Manual, Accept edits, Plan, Auto, Bypass permissions (older labels: Ask permissions / Auto accept edits / Plan mode). **Manual** suits learning: nothing happens without approval. A diff view allows line comments.
- Terminal pane: "Click Terminal in the session's title bar or press Ctrl+`"; it "shares the same environment as Claude". Commands typed after `!` in the prompt box run in the login shell and Claude responds to their output.
- These are configuration files of the learner's Claude setup. The course should present them as an opt-in step the learner performs (a good first exercise in reading a config file), not something generated silently.
- Give the AI the answers so that it can withhold them accurately: a per-lesson tutor-notes file (expected commands and output, common mistakes, the three hint levels) mirrors what both successful tutors did — the Harvard team "enriched our prompts with comprehensive, step-by-step answers" to keep explanations accurate, and found that sequencing had to be enforced by the platform, not by the prompt. Here the lesson files and the checker play the role of the platform.

### 6.4 Suggested wording for a tutoring contract (to offer to the learner, e.g. as CLAUDE.md content)
```text
本文件夹是一个学习环境。你是教练，不是代工。
1. 学习者没有先写下预测或尝试之前，不要给出命令或代码。
2. 提示分三级：先问引导性问题；再点出概念或命令族；学习者明确要求时才给完整命令，并请他复述作用。
3. 标有“你来做”的步骤，由学习者在终端里亲手输入；你不代为运行，也不修改练习文件。
4. 每次只讲一个新概念；用通俗中文，术语首次出现写成“中文（English）”。
5. 报错时先请学习者读报错并提出假设，再一起验证。
6. 课程检查点由 check 脚本判定；不要绕过或替学习者通过检查。
7. 学习者能讲清楚的内容才允许提交；讲不清就退回上一步。
```

## 7. Chinese–English terminology (163 rows, about 200 terms)

Basis codes: **PG** Pro Git 中文版 · **GH** GitHub Docs 中文 · **PY** docs.python.org/zh-cn · **CC** 约定式提交 · **SV** 语义化版本 · **KC** 如何维护更新日志 · **MS** Microsoft Learn zh-cn · **RY** 阮一峰 · **LXF** 廖雪峰 · **EP** eng-practices-cn · **SWE** SWE-at-Google 中文仓库 · **FA** FastAPI 中文文档 (all read today) · **m** = common usage from memory.
House rule: first occurrence "中文（English）"; commands, sub-command names and file names are never translated. GitHub's Chinese docs contain awkward machine-style renderings (fork → "创建分支", origin → "原点", HEAD → "头部", Markdown → "加价", build → "生成") — do not copy those.

| English | Preferred | Also seen | Basis / note |
|---|---|---|---|
| version control | 版本控制 | 版本管理 | PG |
| repository (repo) | 仓库 | 存储库 (GH, MS), 版本库 (LXF), 代码库 (RY) | PG; prefer 仓库 |
| working directory / working tree | 工作区 | 工作目录 (PG), 工作树 (GH) | PG uses both 工作目录 and 工作区; RY, LXF 工作区 |
| staging area / index | 暂存区 | 索引 | PG, RY, LXF |
| stage / unstage | 暂存 / 取消暂存 | | PG |
| tracked / untracked | 已跟踪 / 未跟踪 | 未追踪 | PG |
| commit (noun, verb) | 提交 | | PG, GH |
| commit message | 提交信息 | 提交说明 (PG, CC), 提交消息 (GH) | pick one: 提交信息 |
| commit hash / SHA | 提交哈希 | 提交标识符 (GH), 版本号 (LXF) | m |
| snapshot | 快照 | | PG |
| history / log | 提交历史 / 日志 | 历史记录 | PG |
| diff | 差异 | 补丁；often left as diff | PG, GH |
| branch | 分支 | | all |
| default branch (main) | 默认分支（主分支） | | GH, LXF |
| feature / topic branch | 功能分支 | 主题分支 (PG, GH), 特性分支 | RY, GH |
| HEAD | HEAD（当前位置） | 头部 (GH — avoid) | keep English |
| detached HEAD | 分离头指针 | 拆离的 HEAD (GH) | m |
| checkout | 检出 | 签出 (GH) | PG |
| switch | 切换（分支） | | PG prose |
| restore | 恢复（文件） | 还原 | m |
| merge | 合并 | | all |
| merge commit | 合并提交 | | PG |
| fast-forward | 快进 | 快进模式 (LXF) | PG, GH |
| three-way merge | 三方合并 | | PG |
| common ancestor | 公共祖先 | | PG |
| merge conflict | 合并冲突 | 冲突 | PG, GH |
| conflict marker | 冲突标记 | 冲突解决标记 (PG) | |
| resolve (a conflict) | 解决冲突 | | PG |
| rebase | 变基 | often left as rebase (LXF) | PG, GH |
| squash | 压缩（提交） | left in English (CC) | GH |
| cherry-pick | 拣选 | 挑拣 (GH, MS) | MS uses both |
| revert | 还原（提交） | 回退, 撤销 | CC; distinguish from reset |
| reset | 重置 | 版本回退 (LXF, for `--hard`) | PG |
| amend | 修补（上一次提交） | 修订 | PG "修补提交" |
| stash | 贮藏 | 储藏；never "暂存" | PG |
| tag | 标签 | 标记 (GH) | PG, LXF |
| annotated tag | 附注标签 | | m (PG) |
| remote | 远程仓库 | 远端, 远程库 | PG, RY, GH |
| origin | origin（默认远程名） | 原点 (GH — avoid) | keep English |
| upstream | 上游 | | PG, RY |
| tracking branch | 跟踪分支 | | PG |
| clone | 克隆 | | all |
| fetch | 抓取 | 提取 (GH), 获取 | PG |
| pull | 拉取 | | PG, GH |
| push | 推送 | | PG, GH |
| force push | 强制推送 | | GH |
| fork | 复刻（常直接说 fork） | 分叉 (PG), 派生, "创建分支" (GH — avoid) | no consensus; keep English + gloss |
| pull request (PR) | 拉取请求（PR） | 合并请求 = GitLab 的 merge request (MR) | PG, GH, MS; RY notes MR is GitLab's name |
| draft PR | 草稿 PR | | MS |
| code review | 代码评审 | 代码审查 (PG, GH, SWE), 审阅 | EP and MS use 评审; both common — choose one, mention the other once |
| reviewer / author | 评审者 / 作者 | 审阅者 (MS), 审查者 | EP |
| approve / LGTM | 批准 / LGTM | | EP |
| nit | 小问题（Nit） | | m |
| issue | 议题 | 问题；often left as issue | GH, PG |
| milestone | 里程碑 | | GH |
| label | 标签（label） | | GH; clashes with tag — always add the English |
| assignee | 负责人 | 代理人 (GH) | m |
| maintainer / contributor / collaborator | 维护者 / 贡献者 / 协作者 | | GH, PG |
| .gitignore | 忽略规则（.gitignore） | 忽略文件 | PG |
| hook | 钩子 | 挂钩 | GH |
| pre-commit hook | 提交前钩子 | | m |
| blame | 追溯（blame） | | GH |
| bisect | 二分查找 | | m (PG) |
| submodule | 子模块 | | PG |
| monorepo | 单体仓库 | | m |
| trunk-based development | 主干开发 | | m |
| hotfix | 热修复 | 紧急问题分支 (PG), 补丁分支 (RY) | m |
| Git flow / GitHub flow | keep English | | RY |
| terminal / shell | 终端 / shell（命令行） | 命令行解释器 | m |
| command / argument / option (flag) | 命令 / 参数 / 选项 | 标志 | m |
| path (absolute / relative) | 路径（绝对 / 相对） | | m |
| current directory / home directory | 当前目录 / 主目录 | 家目录 | m |
| pipe / redirect | 管道 / 重定向 | | m |
| environment variable | 环境变量 | | m |
| exit code | 退出码 | 返回码 | m |
| virtual environment | 虚拟环境 | | PY |
| interpreter | 解释器 | | PY |
| package / module | 包 / 模块 | | PY |
| dependency | 依赖 | 依赖项 | m; SV "依赖地狱" |
| lock file | 锁文件 | 锁定文件 | m |
| build backend | 构建后端 | | m |
| wheel / sdist | wheel / 源码分发包 | 轮子 | m; no official Chinese packaging glossary (the zh-cn URL is 404) |
| src layout | src 布局 | | m |
| editable install | 可编辑安装 | | m |
| entry point | 入口点 | | m |
| lint / linter | 静态检查 / 静态检查工具 | 代码检查, 代码规范检查；"Lint" left as is (Google 风格指南中文版) | m |
| formatter | 格式化工具 | 代码格式化程序 | m |
| style guide | 风格指南 | 编码规范 | SWE |
| static analysis | 静态分析 | | SWE |
| type hint | 类型提示 | 类型标注, 类型注解 | PY and FA: 类型提示 |
| annotation | 标注 | 注解 | PY |
| type checker | 类型检查器 | | PY "静态类型检查器" |
| generic | 泛型 | | PY |
| docstring | 文档字符串 | | PY |
| comment | 注释 | | m |
| naming convention | 命名约定 | 命名规范 | m |
| decorator | 装饰器 | | PY |
| argument / parameter | 参数（实参）/ 形参 | | PY |
| exception | 异常 | | m |
| refactoring | 重构 | | RY |
| technical debt | 技术债 | 技术债务 | m |
| code smell | 代码异味 | 坏味道 | m |
| readability / maintainability | 可读性 / 可维护性 | | m |
| magic number | 魔法数字 | 魔术数字 | m |
| dead code | 死代码 | 无用代码 | m |
| DRY | 不要重复自己（DRY） | | m |
| reproducibility | 可复现性 | 可重复性, 可再现性 | m |
| unit test | 单元测试 | | SWE |
| integration / end-to-end test | 集成测试 / 端到端测试 | | m |
| regression test | 回归测试 | | m |
| smoke test | 冒烟测试 | | m |
| test case / test suite | 测试用例 / 测试套件 | | PY |
| test runner / test discovery | 测试运行器 / 测试发现 | | PY |
| assertion | 断言 | | PY |
| fixture | 夹具（fixture） | 测试脚手架 (PY), 固件, 测试夹具 | no consensus; keep English + 夹具 |
| mock / test double / stub | 模拟对象 / 测试替身 / 桩 | 测试替代 (SWE) | PY "模拟对象" |
| parametrize | 参数化 | | m |
| coverage | 覆盖率 | 测试覆盖率 | m |
| skip / expected failure | 跳过 / 预期失败 | | PY |
| edge case | 边界情况 | 边缘情况 | m |
| TDD | 测试驱动开发 | | m |
| continuous integration (CI) | 持续集成 | | GH, SWE, RY |
| continuous delivery / deployment (CD) | 持续交付 / 持续部署 | 持续发布 (RY) | GH, SWE |
| pipeline | 流水线 | 管道 (GH) | m |
| workflow | 工作流 | 工作流程 | GH |
| job / step / runner | 作业 / 步骤 / 运行器 | 运行程序 | GH |
| action (GitHub Actions) | Action（操作） | 动作 | GH; usually untranslated |
| build | 构建 | 生成 (GH, MS) | m |
| artifact | 构建产物 | 工件, 制品 | m |
| status check | 状态检查 | | GH |
| protected branch | 受保护分支 | | GH |
| deploy / production | 部署 / 生产环境 | | GH |
| rollback | 回滚 | | m |
| release | 发布 | 发行版 (GH, for the Releases page), 发行 (SV) | KC |
| release notes | 发布说明 | 发行说明 (GH) | |
| changelog | 变更日志 | 更新日志 (KC) | KC's official title is 如何维护更新日志 |
| semantic versioning | 语义化版本 | | SV |
| major / minor / patch | 主版本号 / 次版本号 / 修订号 | | SV |
| pre-release | 预发布版本 | 先行版本 (SV) | |
| breaking change | 破坏性变更 | 不兼容变更 (SV, RY) | CC |
| backward compatible | 向后兼容 | 向下兼容 (SV) | both mean the same |
| deprecate | 弃用 | | SV |
| yanked | 撤下（的版本） | | KC |
| Conventional Commits | 约定式提交 | | CC |
| type / scope / footer (of a commit) | 类型 / 范围 / 脚注 | | CC |
| README | README（自述文件） | | GH keeps README |
| license | 许可证 | 许可 (GH), 许可协议 | m |
| contributing guide / code of conduct | 贡献指南 / 行为准则 | | 开源指南 |
| requirement | 需求 | | m |
| user story / acceptance criteria | 用户故事 / 验收标准 | | m |
| backlog | 待办列表 | 积压工作 (MS) | m |
| sprint / iteration | 冲刺 / 迭代 | | m |
| kanban board | 看板 | | m |
| roadmap | 路线图 | | m |
| work item / ticket | 工作项 / 工单 | | MS |
| ADR | 架构决策记录（ADR） | | m |
| definition of done | 完成的定义（DoD） | | m |
| scope creep | 范围蔓延 | | m |
| MVP | 最小可行产品 | | m |
| postmortem / retrospective | 事后复盘 / 回顾 | | m |
| pair programming | 结对编程 | | m |
| rubber-duck debugging | 小黄鸭调试法 | | m |
| minimal reproducible example | 最小可复现示例 | | m |

## 8. What changed recently compared with older tutorials

- **Missing Semester**: the 2020 syllabus (11 lectures incl. Vim, data wrangling, metaprogramming) is now "previous years"; the 2026 edition has 9 lectures including Agentic Coding, Beyond the Code, Code Quality, Packaging and Shipping Code, and states that AI is "folded … into each lecture" [source: https://missing.csail.mit.edu/].
- **Git**: default branch `main` on this Mac; `git status` hints say `git restore`; `git switch -c` / `git switch` / `git restore <file>` all work; `git pull` refuses divergent histories until a strategy is chosen; `git config get/set/list` subcommands exist [local]. 廖雪峰's undo chapter, Pro Git zh §2.4 and 阮一峰's cheat sheet predate all of this [sources in §3].
- **GitHub Skills** moved under learn.github.com; exercises are delivered through issue comments by `skills/exercise-toolkit`; most pinned courses are about Copilot and agents [source: https://github.com/skills].
- **google/eng-practices** repo is archived (`archived: true`, last push 2024-09-19); the site is still served [local: GitHub API + curl].
- **Hypermodern Python** (2020) is superseded: blog moved, author promotes a 2024 book, template still Poetry + Nox + Black + Flake8.
- **Scientific Python guide** now writes "pre-commit (or prek)" and shows MyPy next to Pyrefly and ty; ruff covers formatter and linter [source: https://learn.scientific-python.org/development/guides/style/].
- **Carpentries** Curriculum Development Handbook is deprecated in favour of Collaborative Lesson Development Training [source: https://cdh.carpentries.org/].
- **Claude Code**: four built-in styles besides Default; permission modes renamed (Manual / Accept edits / Plan / Auto / Bypass permissions); Terminal pane in the desktop app.
- **Evidence**: before 2025 the advice "don't let AI do your homework" was opinion; there are now randomised studies (§6.1).
- **GitHub Docs** path for the hello-world tutorial is now `/get-started/using-github/hello-world` (older links redirect) [local: curl].

## 9. Pitfalls a beginner will hit

1. First `git commit` dies with `cannot run gpg` (§2.1). Looks like the learner's fault; it is configuration.
2. Tutorial says `master`, the machine says `main`; tutorial says `git checkout -- file`, git itself suggests `git restore`.
3. Git messages are English; Chinese file names appear as `"\345\255…"`.
4. `git pull` → `fatal: Need to specify how to reconcile divergent branches`.
5. Practice repo created inside another repo: `git status` behaves strangely, parent warns about an "embedded git repository".
6. Project folders on an iCloud-synced Desktop: sync daemons and `.git` / `.venv` directories interact badly (duplicate "name 2" files, evicted files) [memory]; I only confirmed that a Desktop can be iCloud-managed, not the failure itself.
7. What Claude's sandboxed shell sees differs from the learner's terminal: network blocked; `/usr/bin/make` prints `make: error: couldn't create cache file '…/xcrun_db-…' (errno=Operation not permitted)` twice before running [local]; `uv` chose a different Python (§2.3). "It worked for Claude" and "it works for me" are different facts.
8. Letting the AI do every step: high completion, low retention, and an illusion of competence (§6.1).
9. Raw pytest, ruff and git output is English and dense; without glosses the learner pastes it to the AI unread, which is the lowest-scoring pattern in the Anthropic study ("iterative AI debugging").
10. Terminology drift: three renderings for one word across docs (存储库 / 仓库 / 版本库); two meanings of 标签 (tag, label); "暂存" used for both stage and stash in some texts.
11. Self-paced courses stall: mastery gates that are too strict cut completion (Kulik et al. 1990).
12. Real Python and some publisher pages block automated fetching, so "the AI could not open the link" does not mean the link is dead.

## 10. Recommendations for the course

- **Teach first**: (0) how to learn here: effort ≠ failure, the AI contract, Terminal pane, ten survival commands (`pwd`, `ls -a`, `cd`, Tab completion, ↑, Ctrl+C), preflight check; (1) local Git with the three-areas model; (2) small commits with Conventional Commits; (3) branches and one deliberately caused conflict.
- **Then**: ruff (format, then lint) → first pytest test → fixtures and parametrisation on numerical code → type hints and docstrings → README → offline "team" with a bare repo → optional GitHub (account creation is the learner's own step) → task runner / hooks / CI → SemVer, changelog, tags, issue and milestone hygiene → capstone on the learner's own project (if any).
- **Skip for now**: interactive rebase, submodules, Git flow, commit signing, Docker, tox/nox matrices, strict type checking, mocking frameworks, property-based testing, monorepos.
- **Defaults**: `main`; six commit types (feat, fix, docs, test, refactor, chore); subject ≤ 72 characters; ASCII file names; one practice repo per lesson under a git-ignored `playground/`; Manual permission mode and the Learning style while studying; checker in plain Python.
- **Toy domain**: a tiny returns / moving-average / max-drawdown package — a small numeric domain, so it adds little load, and tests on numbers show floating-point tolerance naturally.
- **Suggested module map** (a starting point for the designers; lesson counts are estimates, about 30 lessons × 30–45 min in total):

| # | Module | Lessons | Works offline | "带回你的项目" outcome |
|---|---|---|---|---|
| 0 | 起步：学习方法、终端、环境体检、AI 公约 | 2 | yes | study plan and learning log exist |
| 1 | 本地 Git：三个区域、提交、查看历史、忽略规则、恢复 | 4 | yes | a copy of the learner's own project (if any) has a repository, sensible ignore rules, a clean first commit |
| 2 | 提交规范与分支：约定式提交、分支、合并、一次冲突 | 3 | yes | one feature branch merged with well-formed commits |
| 3 | 代码风格：格式化与静态检查 | 2 | yes | project formatted; one finding understood and fixed by hand |
| 4 | 测试：第一个测试、浮点比较、参数化、夹具 | 4 | after one install | 3–5 tests on a numerical function including an edge case |
| 5 | 类型提示与文档：标注、文档字符串、README | 3 | yes | public functions annotated; README answers what / why / how / install |
| 6 | 协作：远程仓库（本地裸仓库）、推送与拉取、评审；GitHub 可选 | 3 | yes | one change reviewed against a rubric before merging |
| 7 | 自动化：一条命令跑全部检查、提交前钩子、CI 概念 | 3 | partly | the single check command is green |
| 8 | 版本与管理：语义化版本、变更日志、标签、议题与里程碑、技术债清单 | 3 | yes | `v0.1.0` tag, CHANGELOG, a short backlog |
| 9 | 结业：把全部规范落到真实项目 | 2–3 | — | project passes a written checklist |

- **Plain-Chinese analogies** (suggestions, not sourced): commit = 游戏存档 / 实验记录本的一页；暂存区 = 打包台（装箱后再封箱贴单）；分支 = 平行草稿；合并 = 把草稿并回正本；远程仓库 = 云端备份兼协作中心；.gitignore = 不入库清单；linter = 语法与拼写检查；formatter = 自动排版；类型提示 = 给插座标上电压；测试 = 回测前的数据校验 / 体检；fixture = 实验前备好的标准样本；CI = 每次提交后的自动质检；代码评审 = 同行评议；技术债 = 信用卡欠款，拖得越久利息越高；重构 = 整理房间但不换家具；锁文件 = 购物小票，pyproject.toml = 购物清单；语义化版本 = 写给使用者的承诺；变更日志写给人看，git log 写给开发者看；PR = "请把我的修改并进去"的申请单。

## 11. Further reading per topic (each returned HTTP 200 today)

| Topic | Chinese | English |
|---|---|---|
| How to learn | — | https://teachtogether.tech/en/index.html · https://www.learningscientists.org/ |
| Shell | https://wangdoc.com/bash/ · https://github.com/jlevy/the-art-of-command-line/blob/master/README-zh.md · https://billie66.github.io/TLCL/ | https://swcarpentry.github.io/shell-novice/ · https://missing.csail.mit.edu/2026/course-shell/ |
| Git basics | https://learngitbranching.js.org/?locale=zh_CN · https://liaoxuefeng.com/books/git/introduction/index.html · https://git-scm.com/book/zh/v2 (ch. 1–3) · https://missing-semester-cn.github.io/2020/version-control/ · https://training.github.com/downloads/zh_CN/github-git-cheat-sheet/ | https://swcarpentry.github.io/git-novice/ · https://missing.csail.mit.edu/2026/version-control/ · https://github.com/eficode-academy/git-katas |
| Git rescue | https://ohshitgit.com/zh · https://github.com/k88hudson/git-flight-rules/blob/master/README_zh-CN.md | https://ohshitgit.com/ |
| Commit messages | https://www.conventionalcommits.org/zh-hans/v1.0.0/ · https://www.ruanyifeng.com/blog/2016/01/commit_message_change_log.html (format yes, tools no) | https://missing.csail.mit.edu/2026/beyond-code/ |
| Branching, PRs, review | https://www.ruanyifeng.com/blog/2015/12/git-workflow.html · https://docs.github.com/zh/get-started/using-github/hello-world · https://github.com/xindoo/eng-practices-cn | https://google.github.io/eng-practices/ · https://github.com/skills/introduction-to-github |
| Style and lint | https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/contents.html | https://peps.python.org/pep-0008/ · https://docs.astral.sh/ruff/ · https://learn.scientific-python.org/development/guides/style/ |
| Type hints | https://fastapi.tiangolo.com/zh/python-types/ · https://docs.python.org/zh-cn/3/glossary.html | — |
| Testing | https://docs.python.org/zh-cn/3/library/unittest.html (terms) | https://goodresearch.dev/testing · https://docs.pytest.org/en/stable/ |
| Project structure, packaging | https://pythonguidecn.readthedocs.io/zh/latest/writing/structure.html (concepts; tools dated) | https://docs.astral.sh/uv/guides/projects/ · https://learn.scientific-python.org/development/ · https://py-pkgs.org/ |
| CI | https://www.ruanyifeng.com/blog/2015/09/continuous-integration.html · https://docs.github.com/zh/actions/get-started/understand-github-actions | https://missing.csail.mit.edu/2026/code-quality/ |
| Versions, changelog, releases | https://semver.org/lang/zh-CN/ · https://keepachangelog.com/zh-CN/1.1.0/ · https://docs.github.com/zh/repositories/releasing-projects-on-github/about-releases | https://missing.csail.mit.edu/2026/shipping-code/ |
| Docs and writing | https://github.com/ruanyf/document-style-guide · https://github.com/sparanoid/chinese-copywriting-guidelines · https://opensource.guide/zh-hans/ | https://diataxis.fr/ |
| Engineering culture, management | https://github.com/qiangmzsx/Software-Engineering-at-Google · https://agilemanifesto.org/iso/zhchs/manifesto.html · https://docs.github.com/zh/issues · https://csdiy.wiki/ · https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way/blob/main/README-zh_CN.md | https://abseil.io/resources/swe-book/html/toc.html |
| Reproducible research code | — | https://goodresearch.dev/ · https://book.the-turing-way.org/ · https://third-bit.com/py-rse/ · https://coderefinery.org/lessons/ |
| Working with AI | https://code.claude.com/docs/zh-CN/output-styles | https://www.anthropic.com/research/AI-assistance-coding-skills · https://missing.csail.mit.edu/2026/agentic-coding/ · https://coderefinery.github.io/coding-with-ai/ |

## 12. Not verified today

- Whether `git commit` also fails in an interactive terminal on a Mac with the half-written signing config (a login shell may add PATH entries the sandbox lacks).
- Real Python content, structure and paywall status (403 to automated clients).
- The effects of iCloud sync on `.git` / `.venv` directories (only the fact of syncing was confirmed).
- Whether Oh My Git! runs on macOS 27 arm64; whether it has a Chinese translation.
- Contents and pricing of Anthropic Academy courses (only that anthropic.skilljar.com loads); content of Atlassian's Chinese Git/agile pages (page loads, body not inspected).
- Exact wording of the 2026 Missing Semester AI-etiquette section (read through a summarising fetch; paraphrased above).
- Per-pattern quiz scores in the Anthropic study are approximate (read from a chart, per the page).
- Whether the Chinese site eng-practices-cn.xindoo.xyz works in a browser (403 to automated clients; the GitHub repo loads).
- Renderings tagged **m** in §7 are common usage from memory, not checked against a named source today; 术语在线 was not consulted.
- "Software engineering is programming integrated over time" (often quoted from SWE at Google ch. 1) was not re-read today [memory].
- The Claude Code version bundled in the desktop app; output-style behaviour was read from documentation, not exercised.
