# Curriculum spine

> **Audience:** the agents that design and generate stage 2 and later. Not learner-facing; written in English on purpose.
> **Written:** 2026-11-19, with batch 1 (stages 0-1). **Owner:** builder-owned (plan G11). **Learner-facing counterpart:** `ROADMAP.md` (the short map) with its pages `docs/roadmap/` (skill-map, threads, electives, sources) and `stages/<NN-slug>/README.md` (one page per stage).

This file is what keeps separately generated stages one course: the same order, the same product, the same threads, the same words, the same rule ids, and a design that starts from what the learner actually did. Read all of it before you design a stage. Update it in the same batch that changes anything it describes.

## 0. Rules for using this file

1. **Precedence.** The course's founding brief (plan G1) > the design (`docs/design/2026-11-19-fullstack-learning-workspace-design.md`) > the plan (`docs/plans/2026-11-19-batch-1-plan.md`) > this file > the research briefs. For facts (versions, flags, defaults, what a source says), what you verify on the learner's machine or in a primary source **on the day you generate** wins over all of them; report the discrepancy and fix the file that was wrong.
2. **Fixed vs proposed.** Items marked **[fixed]** come from the design or the plan and change only by a new decision record in `docs/adr/`. Items marked **[proposed]** are this file's best reading of the evidence on 2026-11-19; a stage design may change them, and must say so in its "roadmap diff" (section 9.3).
3. **Two files move together.** Anything the learner can see (stage outcome, hours, order, a thread, a yardstick) also lives in `ROADMAP.md` or one of its pages (the stage's `stages/<NN-slug>/README.md`, `docs/roadmap/threads.md`, `docs/roadmap/skill-map.md`, `docs/roadmap/sources.md`). Change both, and log the change in `CHANGELOG.md`.
4. **Research briefs are dated notes.** They were verified on 2026-11-19 and they number the stages differently (section 1). Every version, price, free tier and URL in them decays; re-verify before a lesson relies on it (plan G4). Sanitised copies are planned under `docs/research/<topic>/brief.md` (plan T3). Never copy an absolute scratch path, the learner's name, user name, e-mail address or computer name into any file (plan G10).
5. **Voice.** Everything the learner reads follows plan G2 and the register in section 5. Jargon that a non-programmer cannot follow goes under a heading that reads exactly `技术清单（现在看不懂没关系）`.

## 1. Stage numbering: the design vs the research briefs

The design has **12 stages (0-11)**. The research briefs and the five design reviews were written against the first draft, which had **11 stages (S0-S10)** in a different order. Translate every stage number you read in a brief or review.

| Design stage [fixed] | Name [fixed] | Planning hours [fixed] | Cumulative hours | First-draft stage(s) in briefs and reviews |
|---|---|---|---|---|
| 0 | 起步 | about 5 | 5 | S0 Orientation |
| 1 | 工程师的基本功 | 20-25 | 25-30 | S1 Foundations (minus branches, pull requests, pipes, PATH: moved to the stage 2 engineering strand) |
| 2 | 编程入门（Python） | 150-200 | 175-230 | S2 Python fundamentals, plus the engineering strand |
| 3 | 专业开发规范 | 60-90 | 235-320 | S3 Professional practice |
| 4 | 数据与 SQL | 50-70 | 285-390 | first half of S5 (SQL, data modelling) |
| 5 | 后端与接口设计 | 80-110 | 365-500 | second half of S5 (HTTP API, framework), plus the HTTP part of S4 |
| 6 | Web 基础 | 80-120 | 445-620 | S4 Web basics (HTML, CSS, JavaScript, DOM) |
| 7 | 现代前端 | 180-240 | 625-860 | S6 TypeScript + React |
| 8 | 全栈整合与安全 | 100-140 | 725-1,000 | S7 Integration + security |
| 9 | 交付与运维 | 100-140 | 825-1,140 | S8 Delivery + operations |
| 10 | 团队协作与项目管理 | 40-60 | 865-1,200 | S9 Collaboration |
| 11 | 架构与毕业项目 | 150-250 | 1,015-1,450 | S10 Architecture + capstone |

Note (2026-11-20): the hours of stages 0 and 1 are no longer the design's estimates. `tools/dev/build_reference.py` computes them from the lessons' minutes (stations, closings and gates, plus 15% for reviews): about 8.5 and 36.5 hours, 45 together. The cumulative hours a learner reads are in `ROADMAP.md` (195-245 after stage 2, up to 1,035-1,465 after stage 11). The two columns above are the design's original estimate and stay as its record.

Consequences of the reorder that the briefs do not spell out:

- HTTP is first *needed* in stage 5 (back end), before the "web basics" stage. The request-journey lab (URL, DNS, TCP, TLS, HTTP) that the `cs-fundamentals` brief puts at the start of web basics therefore opens **stage 5**; the browser pipeline, the DOM and the JavaScript event loop stay in stage 6.
- Ports and `localhost` are first needed when PostgreSQL arrives (stage 4), not at the first web server.
- Login exists only from stage 8. Password hashing, session cookies and ownership checks, which the `web-security-2026` brief lists under "backend & DB", move to **stage 8**; injection, parameterised queries and least-privilege database roles stay with stage 4; boundary validation, error handling and SSRF with stage 5.
- The learner's first hand-edited HTML/CSS is in stage 1 (`my-site`), so a server-rendered template in the stage 5 "thin slice" is not their first HTML.
- Decision records: `docs/adr/0003-stage-order.md` (order), `0002-python-first-javascript-later.md` (language), `0001-staged-delivery.md` (staged generation).

Exit ramps [fixed, design 5.5 and the batch-1 task]: after stage 3, after stage 5, after stage 9. Each is a place where stopping is a legitimate outcome; never design a stage so that its artefact is useless without the next one.

## 2. Prerequisite map

### 2.1 Between stages

```text
0 ──▶ 1 ──▶ 2 ──▶ 3 ──▶ 4 ──▶ 5 ──▶ 6 ──▶ 7 ──▶ 8 ──▶ 9 ──▶ 10 ──▶ 11
                  │           └──────────────────▶ 8        └────────▶ 11 (10 recommended, not required)
                  └─ electives: research-code engineering (after 3), job search (after 3, best after 8)
```

| Stage | Hard prerequisites | What it needs from them | What it hands to later stages |
|---|---|---|---|
| 0 | none | - | terminal orientation; workspace location decided (`learner/state.json` → `decisions.workspace_location`); study plan; product choice (0.3) |
| 1 | 0 | paths, `cd`, the check/hint/journal loop | daily terminal and Git loop; `my-site` online (state S7); private course repository with a verified second copy; diff reading; question template |
| 2 | 1 (gate-1 passed) | terminal, editor, commit, push, `.gitignore`, Conventional Commits | Python fluency; the `fx` command-line tool; branches, merges, conflicts, pull requests, review; first tests; type hints; debugging routine |
| 3 | 2 | a program worth hardening; the pull-request loop | project layout, lockfile, lint, format, types, tests, one check command, continuous integration, release `v0.1.0`; config, logging, error handling; supply-chain hygiene |
| 4 | 3 | uv project, tests, CI, Decimal and UTC from stage 2 | schema, queries, transactions, indexes, migrations; SQLite then PostgreSQL; a history database |
| 5 | 4 | the database; HTTP from the request-journey lab taught here | a deployed read API with an OpenAPI description; health endpoint; environment-based config; the service that stays online |
| 6 | 5 for the data-fetching page (HTML and CSS parts need only stage 1) | an API of the learner's own to call | HTML, CSS, JavaScript, DOM, `fetch`, DevTools; same-origin policy and CORS met for real |
| 7 | 6 | JavaScript, the DOM, one no-framework app | TypeScript, React, routing, server state, component tests, a built front end served by the back end |
| 8 | 5 and 7 | API + SPA | authentication, authorisation, privacy features, end-to-end tests, a security checklist with evidence |
| 9 | 8 | a complete application | containers, continuous delivery, monitoring, backups, rollback, own domain, cost control |
| 10 | 9 | a live application to iterate on | team process, human-style review, incident handling, written reporting |
| 11 | 9 (10 recommended) | everything | a product the learner designed and shipped |

Soft dependencies to respect when resequencing inside a stage:

- Stage 2's engineering lessons need code to act on: branches after the first project, pull requests after merging and after a GitHub remote exists (stage 1 leaves one).
- Stage 3 lesson changes travel through the pull-request loop from its first lesson; continuous integration follows the one-command check, so the robot runs exactly what the learner already runs by hand.
- Stage 6 ends with the first Node.js/npm contact and the npm safety habits; stage 7 assumes them.

### 2.2 Between the stage 0-1 lessons [fixed ids, stations and gates: plan section 4, mirrored in `tools/courselib/syllabus.py`]

"Needs" lists the lessons whose skills or artefacts the lesson relies on, beyond simple order. "State" is the `~/Developer/my-site` ladder of plan I6. Once the lesson modules exist, each module's `META["prerequisites"]` is authoritative; if it differs from this table, reconcile and update the table.

| Lesson | Needs | Starts in state | Ends in state | Gate | Hands on |
|---|---|---|---|---|---|
| 0.1 第一次动手 | - | - | - | gate-0 | three commands, Ctrl+C, running and editing `starter/hello-fx/convert.py`, 报错三问, first journal entry, `learner/profile.md` |
| 0.2 文件、路径和代码的家 | 0.1 | - | - | gate-0 | `cd`, Tab completion, absolute and relative paths, `man`, `mkdir -p ~/Developer`, `doctor`, workspace location |
| 0.3 软件是怎么做出来的，规范从哪来 | 0.1 | - | - | gate-0 | parts of a product; the four sources of norms; how to read `STANDARDS.md`; product choice |
| 0.4 像管项目一样管学习 | 0.2 (workspace location), 0.3 | - | - | gate-0 (inside) | tasks, definition of done, weekly plan, return routine, tired protocol, temporary backup |
| 1.1 终端：新建与查看 | 0.2 | S0 | S0 | gate-a | `mkdir`, `touch`, `ls -l/-a`, `cat`, `less`, `head`; what an option is |
| 1.2 终端：复制、移动、删除 | 1.1 | S0 | S1 | gate-a | `cp`, `mv`, `rm`; `~/Developer/my-site` exists |
| 1.3 终端：查找 | 1.2 | S1 | S1 | gate-a | `grep`, `find` |
| 1.4 编辑器 VS Code | 1.2 | S1 | S2 | gate-a | open a folder, edit, save, preview; `.editorconfig` |
| 1.5 Markdown 与 README | 1.4 | S2 | S3 | gate-a (after) | Markdown; README for `my-site` |
| 1.6 Git：第一次提交 | 1.5; 1.2 (playground habits) | S3 | S4 | gate-b | four-area picture; `git config`; the signing problem handled; `init`, `status`, `add`, `commit -m`, `log --oneline` |
| 1.7 Git：看懂改了什么 | 1.6 | S4 | S4 | gate-b | `diff`, `diff --staged`, `show`, `log --stat`; leaving the pager |
| 1.8 Git：后悔药 | 1.7 | S4 | S4 | gate-b | `restore`, `restore --staged` |
| 1.9 Git：什么不该进仓库 | 1.6, 1.8 | S4 | S5 | gate-b | `.gitignore`, `check-ignore`, `rm --cached`; rotate a leaked key first |
| 1.10 提交规范 | 1.7, 1.9 | S5 | S6 | gate-b (after) | one thing per commit; Conventional Commits 1.0.0 |
| 1.11 GitHub：账号、安全与身份 | 1.6 (identity, signing choice), 1.9 | S6 | S6 | gate-1 | account, two-factor authentication, `gh` installed and logged in, private commit e-mail |
| 1.12 第一次推送和云端备份 | 1.11, 1.9, 1.10 | S6 | S6 | gate-1 | the course folder becomes a private repository; push; restore verified from a clone |
| 1.13 把你的网页放到网上 | 1.12, 1.5 | S6 | S7 | gate-1 | public repository, `LICENSE`, GitHub Pages, edit-push-see loop |
| 1.14 排错、求助与"与时俱进" | 1.1-1.13 | S7 | S7 | gate-1 | eight broken situations; question template; judging whether a source is stale; `fresh` |
| 1.15 验收 AI 的改动 | 1.7, 1.8, 1.10 | S7 | S7 | gate-1 | accept or reject an AI change from its diff; project instruction file |
| 1.16 阶段作品与验收 | all of stage 1 | S7 | S7 | gate-1 (inside) | stage artefact tidy; retrospective with estimate vs actual; trigger for stage 2 |

Deliberately **not** taught in stages 0-1 (plan section 4, last paragraph), so stage 2 must not assume them: branches, merging and conflicts, pull requests and review, `commit --amend`, `reflog` and recovery, pipes and redirection, environment variables and `PATH` (1.11 touches `PATH` only as far as installing `gh` needs).

## 3. The product thread

One product runs through the whole course [fixed, design section 4]. Default: an exchange-rate dashboard. The learner may swap it in lesson 0.3; read `learner/profile.md` and `learner/state.json` → `decisions` before assuming the default.

| Stage | Increment (default product) [the "学完你手里有什么" column is fixed in design 5.5] | Shape to keep if the product was swapped | Where it lives |
|---|---|---|---|
| 0 | `starter/hello-fx/convert.py`: run it, change one number; a sample dashboard is dissected as the worked example in 0.3 | a 15-line program that turns an input into an output with one adjustable constant | course workspace (`starter/`) |
| 1 | `my-site`: a hand-written one-page site, online; the product's first public face | one static page about the product | `~/Developer/my-site`, public repository |
| 2 | `fx`: a command-line converter (amount + currency in, converted amount out), grown through versions 0 and 1 and a final project; rates from a file; exact decimals | a pure calculation core with a command-line front | its own repository under `~/Developer` [proposed: one repository per stage project from stage 2; see open question 4] |
| 3 | the same tool as a professional project: tests, lint, types, CI, release `v0.1.0`; optionally a rescued copy of the learner's existing project (if any) | the same core, hardened; no new features | same repository; the optional copy in its own repository, original untouched |
| 4 | a database of historical rates plus queries that answer questions | a store of records over time, with at least one relation worth a join and one question worth an index | same repository or a sibling [open] |
| 5 | a "data window": a read API over that database, deployed and kept online; opens with a thin slice (API + database + one server-rendered page) | a read API with pagination and one write path if the product needs it | deployed service |
| 6 | a hand-written page (no framework) that fetches from the learner's API | one useful page over the API | static hosting; same repository or a sibling [open] |
| 7 | the dashboard's new interface: TypeScript + React single-page app, served by the back end | routes, loading/error/empty states, one form | same origin as the API |
| 8 | sign-in and personal settings (for example watched currencies); security checklist passed | per-user state and an ownership rule to test | same application |
| 9 | own URL, running without the learner's computer; monitored, backed up, reversible | the same application, operated | hosting platform |
| 10 | one team-style iteration on the live application | a backlog of changes on a living system | same application |
| 11 | a product the learner designs and ships (a major version of the dashboard or something new) | learner's choice | learner's choice |

Rules for whoever extends the thread:

- Reuse, do not restart. Each stage's artefact must import, call or deploy the previous stage's artefact. The conversion logic written in stage 2 is still the code that computes in stage 9.
- The product's data rules are fixed from stage 2 on: money as exact decimals with ISO 4217 codes, time stored in UTC and written in ISO 8601 / RFC 3339. Do not hard-code a time zone in examples or checks, and do not assume Asia/Shanghai or UTC+8; ask the learner for their time zone.
- Checks never depend on a live rate source. Use fixtures; a network fetch is a lesson topic, not a checker dependency (plan I4: no network at run time).
- The learner may already have an AI-built project of their own (for example a dashboard) or another existing project (if any). The design says such a project is not modified (design section 3); its only role in the main line is the optional stage 3 rescue of a *copy*. For the dashboard the design says "each stage adds a piece to it" but does not say whether later stages extend existing dashboard code or rebuild the product from zero. The stage outcomes in design 5.5 read as a rebuild (a new command-line core, a new database, a new API, a new interface). Until a stage design settles this with the learner (open question 20), build the thread from zero, use a sample dashboard as the worked example (lesson 0.3; a learner's own dashboard appears only in that lesson's optional read-only tour), and never change the learner's existing code without an explicit request.

## 4. Threads: per-stage checklists

Eight threads run through the stages. The design names four (规范线, 管理线, 交付线, 排错线); the batch-1 task added three (安全线, the AI ladder, the English ladder); this file adds the principles thread (原理线) from the `cs-fundamentals` brief, because "taught just in time" becomes "never taught" without a ledger. Copy the stage's checklist into the stage design and account for every line: done in lesson X, moved to stage Y with a reason, or dropped with a reason.

Tags: `NORM` 规范线 · `MGMT` 管理线 · `DELIV` 交付线 · `DEBUG` 排错线 · `SEC` 安全线 · `AI` AI ladder · `EN` English ladder · `CS` 原理线.

Every NORM item carries the 规则类型 given for that row in the stage's `stages/<NN-slug>/README.md` (section 「这个阶段会学到的规范」). Where the stage page has no row, classify the item with the plan G3 procedure in the stage design and add the row to the stage page. The learner-facing threads are summarised as one matrix in `ROADMAP.md` section 6 and in full in `docs/roadmap/threads.md`.

AI ladder [proposed mapping of the `fullstack-curricula` brief, section 7 item 8, onto the design's numbering]: stages 0-2 **tutor**; stage 3 **reviewer**; stages 4-8 **pair**; stages 9-11 **delegate**. Each rung adds a permission and removes none. It governs course exercises only; elsewhere the assistant works normally (design 5.8). Rule of thumb for exercises: 先手写，再对照，后委托. Every gate keeps AI-off tasks and an explain-back.

### Stage 0 (batch 1, in construction)

Boxes stay unticked until the plan T4 acceptance checklist passes; on 2026-11-19 no lesson folder existed yet.

- [x] NORM: META-01, WS-01, WS-02, META-02, PM-01, PM-02; guided tour of `STANDARDS.md` (0.3c).
- [x] MGMT: tasks with a definition of done (0.4a); weekly plan, fixed slots, return routine, tired protocol (0.4b); intake questionnaire into `learner/profile.md` (0.1a); first journal entry (0.1c).
- [x] DELIV: none.
- [x] DEBUG: first deliberate error and 报错三问 (0.1c); reading errors, `man`, full-width vs half-width (0.2b).
- [x] SEC: code out of the synced folder (0.2c); temporary backup (0.4c). The security thread proper starts in stage 1.
- [x] AI: tutor; the three modes and the status line (0.1a).
- [x] EN: English output shown verbatim, followed by `> 读懂这句：`; each command's expansion once (plan G14).
- [x] CS: what a computer and a product consist of (0.3a); paths (0.2a).

### Stage 1 (batch 1, in construction)

- [x] NORM: the 24 rules of section 6.1.
- [x] MGMT: one-line journal per lesson; question template (HELP-01); estimate vs actual and stage retrospective (1.16c, PM-03).
- [x] DELIV: static page online with GitHub Pages (1.13); remote backup verified by restoring from a clone (1.12c).
- [x] DEBUG: lab of eight broken situations, attempted without AI first (1.14a); one deliberate error per station (plan I1).
- [x] SEC: REPO-01, REPO-02, ACC-01, ACC-02, REMOTE-02, TERM-01, TERM-02, GIT-02; the signing decision (1.6a, 1.11c); "rotate the key first" (1.9b).
- [x] AI: tutor; accepting or rejecting an AI change from its diff (AI-01), honest attribution (AI-02), project instruction file (1.15c).
- [x] EN: as stage 0.
- [x] CS: files, hidden files, paths; Git as snapshots in four areas; GitHub as a server (first light client/server contact). Deferred to stage 2: process, exit code, streams, pipes, environment variables, `PATH`.

### Stage 2 (planned)

- [ ] NORM: PEP 8; type hints from the first functions; explicit `encoding="utf-8"`; Decimal and ISO 4217 for money; UTC and ISO 8601 for time; GitHub Flow with one branch per change; pull-request description (what, why, how verified); never rewrite pushed history; review etiquette with severity labels; a one-page spec before code.
- [ ] MGMT: before each project a one-page spec (user story, acceptance criteria, out of scope) and a task list with estimates; after it a retrospective with estimate vs actual; weekly, one exercise with all AI off and one "read this 80-line program and explain it".
- [ ] DELIV: no deployment; the `fx` repository on GitHub with the pull-request loop, ready for CI in stage 3.
- [ ] DEBUG: a debugging block (read the traceback from the last line; the routine 复现 → 读最后一行 → 定位行号 → 提出假设 → 小实验验证 → 修改 → 没用就撤销 → 重新运行; print; the VS Code debugger; a local tracer); a reading-code lesson; fix-the-bug exercises in every lesson.
- [ ] SEC: all input is untrusted (validate type and range); `secrets` not `random` for tokens; never `eval` or `pickle` untrusted data; fail closed; path-traversal basics; the `uv init` trap (it copies the Git name and e-mail into `pyproject.toml` `authors`): check before pushing to a public repository; only obviously fake credentials in exercises.
- [ ] AI: tutor only (explains, hints, quizzes; never writes exercise code and never debugs for the learner); explain-back after every exercise; unassisted unit checkpoints and gate; in the reading-code lesson the AI supplies code with planted bugs for the learner to review.
- [ ] EN: withdraw the glosses step by step; a handful of new English terms per lesson (the pedagogy brief suggests at most about 8); from the modules lesson on, the official Python tutorial in Chinese (3.14) with the English page beside it; identifiers in English; a small naming vocabulary.
- [ ] CS: one notional machine drawn the same way all stage (names on values; one sheet of scratch paper per call; references and mutation); memory vs disk; `int`, `float`, `Decimal`; `str` vs `bytes`, UTF-8; Unix time, UTC, ISO 8601; list, dict, set, tuple chosen by operation, with timing experiments for Big-O; stack and queue as usage patterns; exit codes, stdin/stdout/stderr, pipes and redirection; environment variables and `PATH`; dependency, lockfile, virtual environment at first sight; one HTTP request and JSON.

### Stage 3 (planned)

- [ ] NORM: `pyproject.toml` (PyPA specification); lockfile committed and `uv sync --locked`; formatter and linter decide style; tests travel with the change; bug fixes start with a failing test; CI on every push and pull request; SemVer 2.0.0; Keep a Changelog 1.1.0; Twelve-Factor III (config in the environment); dependency audit and cooldown; pinned actions and least-privilege workflows; decision records (MADR 4.0.0); definition of done as one command.
- [ ] MGMT: issues with acceptance criteria; a four-column board with a work-in-progress limit (the `project-mgmt-norms` brief suggests Doing ≤ 2); `make check` as the definition of done; a one-page design note and ADR 0001 before the project; a release checklist; a weekly review; the stage retrospective.
- [ ] DELIV: CI running the same check command on push and pull request; Dependabot for `uv` and `github-actions`; first tagged release `v0.1.0` with a hand-written `CHANGELOG.md` and a GitHub release.
- [ ] DEBUG: read a failed CI run; narrow a failure with tests; characterisation (golden) tests before refactoring; the four classic causes of flaky tests (awareness).
- [ ] SEC: supply chain as a first-class topic (OWASP Top 10:2025 A03): lockfile with hashes, `exclude-newer`, `uv audit` or `pip-audit`, how to read an advisory, the upgrade routine; ruff `S` rules; `.env` ignored and `.env.example` committed; a leak drill with a fake key (rotate first); logs without secrets or personal data; least-privilege CI and pinned actions; `SECURITY.md`; licences of dependencies.
- [ ] AI: reviewer. A fresh-context AI reviews the learner's change; the learner reviews AI-written tests and changes with the red-flag checklist (scope, hallucinated APIs, dependencies, swallowed errors, tests that assert nothing, over-engineering, secrets, evidence); "command plus output" as the evidence norm; commit before each agent step; the project instruction file grows by the "corrected twice" rule.
- [ ] EN: one English primary source with two guiding questions in each lesson's reading list.
- [ ] CS: exit codes as the language of automation; stdout vs stderr and logging; configuration through the environment; dependency vs lockfile vs virtual environment; the dependency graph (`uv tree`); caches already relied on; measure before optimising.

### Stage 4 (planned)

- [ ] NORM: parameterised queries only; primary keys, foreign keys, constraints; migrations in the repository; multi-step writes in one transaction; exact numeric types for money and timezone-aware UTC for time; a backup counts only after a restore drill; consistent naming and SQL layout.
- [ ] MGMT: a data inventory (field, meaning, source, retention); decision records for the schema and for the move from SQLite to PostgreSQL; spec and retrospective as before.
- [ ] DELIV: versioned migrations; "Docker as an appliance" (PostgreSQL from a provided `compose.yaml`); a backup-and-restore drill on the development database; database tests in CI.
- [ ] DEBUG: `EXPLAIN QUERY PLAN` (scan vs index search); `database is locked`; constraint errors; `NULL` surprises.
- [ ] SEC: SQL injection demonstrated on the learner's own SQLite lab, then fixed; least-privilege database role; data minimisation in the schema; the legal line (attack only what you own or what a platform offers for practice).
- [ ] AI: pair, for patterns the learner has hand-built once; the learner reviews every AI-proposed schema and query (a schema is the least reversible decision and where AI output most needs an informed reviewer).
- [ ] EN: SQLite and PostgreSQL documentation as the English primary sources.
- [ ] CS: why a database instead of files; relational model, keys, `NULL`; transactions (ACID); indexes and query plans; a server process, a port and `localhost` at the first PostgreSQL contact.

### Stage 5 (planned)

- [ ] NORM: HTTP semantics (RFC 9110); one error format (RFC 9457); an OpenAPI description; plural-noun resources; pagination from the first list endpoint; validation at the boundary with separate create/update/read schemas; no breaking changes to a published API; configuration from the environment; a health endpoint; English commit subjects and pull-request descriptions (default; the learner decides).
- [ ] MGMT: contract first (write the API description before the implementation); a dependency-upgrade procedure (read the release notes, bump, run the tests): the framework is 0.x and breaks often; `THREAT_MODEL.md` version 1; decision records for framework and layering.
- [ ] DELIV: thin slice at the stage opening; first back end online on a free tier that needs no card, using the platform's native Python runtime, with a managed PostgreSQL; a database-free `/healthz`; `.env.example`; the service stays online from here to the end of the course.
- [ ] DEBUG: trace one request (`curl -v`, 4xx vs 5xx, server logs); the diagnosis ladder DNS → refused → timeout → TLS → HTTP.
- [ ] SEC: boundary validation; generic errors, no stack traces to clients; structured logs without personal data; SSRF when the service fetches URLs; rate limiting as a concept; HTTPS basics and reading response headers; first threat model.
- [ ] AI: pair.
- [ ] EN: English commit subjects from here, if the learner agrees.
- [ ] CS: the request-journey lab before any framework; a raw HTTP exchange; URL anatomy; API as a contract; idempotency; waiting vs computing (`def` vs `async def`); the three-box picture (browser, application, database).

### Stage 6 (planned)

- [ ] NORM: HTML Living Standard; semantic elements; WCAG 2.2 basics; ECMAScript; escape user-provided content; HTTPS everywhere; same-origin policy and CORS; Core Web Vitals as the performance yardstick.
- [ ] MGMT: split one interface requirement into independently shippable steps; estimate vs actual continues.
- [ ] DELIV: the static site published through the Pages Actions workflow; DNS and HTTPS by inspection; optional custom domain.
- [ ] DEBUG: DevTools Elements, Console, Network, Application; a real CORS error from the learner's own API; cache confusion; breakpoints.
- [ ] SEC: origin and same-origin policy; cookies and their flags; first XSS (`innerHTML` vs `textContent`); a CORS allow-list on the learner's API; SRI; npm safety habits at the first `npm install` (end of the stage).
- [ ] AI: pair, after one no-framework app has been built by hand.
- [ ] EN: MDN in Chinese first, the English page for reference sections.
- [ ] CS: the browser pipeline (DOM tree, CSSOM, layout, paint; a script blocks parsing); the JavaScript event loop; cookies, sessions and web storage (see); caching and staleness.

### Stage 7 (planned)

- [ ] NORM: TypeScript `strict`; the same four roles as stage 3 (format, lint, type-check, test) in the JavaScript toolchain; lockfile committed and `npm ci`; cooldown and install-script approval; no secrets in the bundle, no tokens in web storage; loading, error and empty states for every data view; component tests at the level of user-visible behaviour; accessibility checks in the test suite.
- [ ] MGMT: a decision record for "Vite single-page app with a router and a server-state library; no meta-framework"; spec and retrospective as before.
- [ ] DELIV: `vite build` to `dist/`; the base-path pitfall; the built app served by the back end from the same origin.
- [ ] DEBUG: rendering bugs (stale state, double render); type errors; the Network panel with a single-page app; failing component tests.
- [ ] SEC: React's escaping and its escape hatches; npm hygiene verified against the official registry.
- [ ] AI: pair.
- [ ] EN: react.dev in Chinese, the English API reference beside it.
- [ ] CS: the component tree and re-rendering; asynchronous data fetching and interface race conditions; JavaScript number limits and large ids in JSON; client-side caching and stale data.

### Stage 8 (planned)

- [ ] NORM: walk OWASP Top 10:2025 against the learner's application; ASVS 5.0.0 level 1 as the checklist; passwords hashed with Argon2id through a maintained library; password rules per NIST SP 800-63B-4; server-side session in a cookie with `HttpOnly`, `Secure`, `SameSite`; ownership checked server-side on every access; personal data minimised, exportable, deletable (PIPL awareness); end-to-end tests for the main flows; a maintained threat model.
- [ ] MGMT: threat model version 2; personal-data inventory; a security checklist where every item links to evidence.
- [ ] DELIV: secrets in the platform's store; staging vs production; same-origin deployment vs CORS; rotation of authentication secrets.
- [ ] DEBUG: bugs that cross interface, API and database; end-to-end test traces.
- [ ] SEC: the consolidation above; a CSRF guard; security headers and a content security policy (report-only, then enforced); privacy features (export, delete, notice); practice platforms as optional enrichment.
- [ ] AI: pair; the gate includes finding security problems in AI-written code.
- [ ] EN: OWASP pages in English with the Chinese Top 10 beside them.
- [ ] CS: origin; cookie attributes; sessions vs tokens; hash vs encoding vs encryption; what TLS does and does not protect; trust boundaries drawn on the learner's own system diagram; race conditions and idempotency (use).

### Stage 9 (planned)

- [ ] NORM: Twelve-Factor in full; containers run as non-root and images hold no secrets; one artefact promoted across environments; certificates issued and renewed automatically; backups with restore drills; every release reversible and migrations expand-then-contract; health checks, logs, alerts; blameless post-mortems; a monthly inventory of accounts, running services and cost.
- [ ] MGMT: release checklist; rollback drill; cost budget; first formal incident post-mortem; an incident runbook.
- [ ] DELIV: in order (the `delivery-ops-2026` brief, section 17): Linux in a container; images, containers, ports, volumes; a Dockerfile for the uv project with `.dockerignore`, non-root user and lint; layer cache and multi-stage builds; Compose with PostgreSQL, health checks and a migration service; push to a registry on a tag; a delivery job with environments, secrets, concurrency and a smoke test; deployment on the chosen platform; migrations in the pipeline; logs, health, uptime monitoring, error tracking; backup and restore drill; rollback drill with a short incident note; custom domain and HTTPS; optional one-week virtual-server lab; cost and teardown checklist.
- [ ] DEBUG: logs and metrics; refused vs timeout vs TLS error vs HTTP error; debugging inside a container.
- [ ] SEC: SSH keys only, firewall, updates, non-root; `.dockerignore`; secret stores, OIDC instead of static keys, environments with approval; HSTS; the incident runbook (rotate, assess, notify).
- [ ] AI: delegate. An agent works from the learner's specification and tests; the learner reads every changed line; merge, deploy and delete decisions stay with the learner.
- [ ] EN: platform documentation in English.
- [ ] CS: Linux as "the same ideas, case-sensitive and without a GUI"; process supervision and SIGTERM; `0.0.0.0` vs `127.0.0.1`; DNS records and TTL; automated certificates; a container as an isolated process from an image (and the virtual machine Docker Desktop hides on a Mac); CDN and build caches.

### Stage 10 (planned)

- [ ] NORM: cadence, goal, review and retrospective (Scrum Guide 2020); board with a work-in-progress limit (Kanban Guide, May 2025); a shared definition of done; the review standard of Google's engineering practices; small changes (about 200 lines); a protected main branch; community health files (`CONTRIBUTING.md`, `CODEOWNERS`, code of conduct, `SECURITY.md`); AI teammates' changes reviewed like anyone's, with honest attribution; estimates with ranges and written status reports.
- [ ] MGMT: a team simulation on the live application: a backlog seeded by the builder (an ambiguous feature request, bug reports, a dependency vulnerability); AI agents as teammates whose pull requests the learner reviews and sometimes rejects; one incident; one written status report; debt and risk registers; one human review point (recommended, optional).
- [ ] DELIV: operating the live service: a monthly dependency update, one schema migration on live data, the uptime check, one incident.
- [ ] DEBUG: an incident drill with a blameless post-mortem.
- [ ] SEC: security review inside the pull-request flow; `CODEOWNERS` on workflows; branch rulesets (not enforceable on a free private repository); signed commits (SSH); private vulnerability reporting; access on- and off-boarding; a dependency-update policy.
- [ ] AI: delegate; written team rules for AI use.
- [ ] EN: one issue or pull request written in English (the open-source elective fits here).
- [ ] CS: the commit graph; merge vs rebase as graph operations; API and schema changes as contract changes between people.

### Stage 11 (planned)

- [ ] NORM: design document (goals, non-goals, approach, alternatives, risks); decision records (MADR 4.0.0); C4 diagrams; monolith first; a one-page privacy impact note; documentation split by purpose (Diátaxis); the graduation self-check with evidence for every earlier checklist.
- [ ] MGMT: the learner sets scope, milestones and a risk register and runs the whole cycle.
- [ ] DELIV: a pipeline from the first day; the stage 9 checklist reapplied to the new product.
- [ ] DEBUG: the learner designs a failure drill for their own system.
- [ ] SEC: trust boundaries; defence in depth; secure defaults; the final threat model; the capstone checklist of the `web-security-2026` brief (section 10) all green; a dependency inventory.
- [ ] AI: delegate; optionally one AI feature in the product (a model API call, an evaluation, a cost budget, a prompt-injection defence).
- [ ] EN: whatever the product's audience needs.
- [ ] CS: small-system design (one database, vertical before horizontal scaling); when a cache, a queue or a CDN earns its place; back-of-envelope estimates; failure modes.

## 5. Register: terms, analogies and the Git picture

Copied from plan section 5a. **Use these; do not invent rivals.** The copy is verbatim from the next paragraph to the line "Other fixed wording".

Chinese renderings follow the terminology table in the `pedagogy-prior-art` brief and the Git glossary in the `git-norms` brief (the wording of the official Chinese Pro Git); where they differ, Pro Git wins. Core analogies are fixed so that 20 lessons written in parallel tell one story. Each analogy is followed, where it is first used, by one sentence on where it stops being true.

| Term | Plain wording | Analogy | Where the analogy breaks |
|---|---|---|---|
| 终端（terminal） | 用打字而不是点鼠标来指挥电脑的窗口 | 对讲机：你说一句，它回一句 | 它不会猜你的意思，错一个字符就不认 |
| 命令（command） | 在终端里敲的一行指令 | 一句口令 | 口令有固定格式：命令名、选项、对象 |
| 路径（path） | 文件在电脑里的地址 | 省、市、街道、门牌 | 相对路径像"从我这里往前走两个路口"，换个出发点就不同 |
| 仓库（repository） | 被 Git 管着的文件夹 | 带相册的文件夹：隐藏的 `.git` 是相册 | 相册里存的是你选中的改动，不是整台电脑 |
| 提交（commit） | 拍一次快照并写一句说明 | 游戏存档 | 只存放进暂存区的内容，不会自动存全部 |
| 暂存区（staging area） | 准备拍进下一张快照的改动 | 打包台：决定哪些东西装进这一箱 | 装箱后再改文件，箱里还是旧的，要重新放 |
| 远程仓库（remote） | 放在别处的另一份仓库 | 存在别处的另一本相册 | 两本不会自动同步，要你推送或拉取 |
| `.gitignore` | 给 Git 的"不拍名单" | 拍照时说好不入镜的东西 | 已经拍进去的，加进名单也不会自动消失 |
| README | 项目的门面和说明书 | 店门口的招牌和告示 | 没人强制你写，但没有它别人不敢进门 |

The Git picture, reused unchanged in every Git lesson (areas not yet taught are shown but marked 「以后再讲」):

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

Other fixed wording: 练习场 (playground), 存档点 (save point), 站 (station), 报错三问, 行规 (the lesson's rule cards), 落脚点 (landing point), 上课 / 干活 / 急救 (the three modes), 带扶手完成 (finished with the last hint level).

### 5.1 Further wording already in front of the learner

These come from the design's glossary (design section 1) and from `ROADMAP.md` and its pages. Keep them stable. The design's glossary rows are **[fixed]**; the `ROADMAP.md` coinages are **[proposed]** until a lesson uses them, after which `GLOSSARY.md` (generated from the lessons' `TERMS`) is the registry of record.

| Term | Plain wording | Source |
|---|---|---|
| 编辑器 | 写代码和文档用的软件 | design 1 |
| Markdown | 带简单排版记号的纯文字 | design 1 |
| Git | 给文件夹拍"带说明的快照"的工具，随时能退回任何一张快照 | design 1 |
| GitHub | 存放快照备份、也能展示作品的网站 | design 1 |
| 推送 | 把本机的快照传到 GitHub | design 1 |
| 分支 | 一份可以放心乱改的平行草稿 | design 1 |
| 合并请求（pull request） | "请先看看我的改动，再决定收不收" | design 1 |
| 前端 / 后端 | 用户看得见的界面 / 在服务器上干活、不露面的程序 | design 1 |
| 数据库 | 专门存数据、能快速查找的程序 | design 1 |
| 上线（部署） | 把程序放到一台一直开着的电脑上，让别人能通过网址使用 | design 1 |
| 数据窗口 | the stage 5 API, in the learner's words | design 5.5 |
| 后悔药 | version history you can go back to | design 5.5, 5.6 |
| 主线 | 正式稿所在的那条线 (the main branch); 分支 is the draft, 主线 the fair copy | `stages/01-foundations/README.md` (技术清单), stage 2 page |
| 流水线 | 代码一推送就自动检查、自动上线的那套自动步骤 (pipeline) | `docs/roadmap/skill-map.md` (方块 8); stage 9 page |
| 落脚点 / 下车点 | 落脚点 = the end of any stage, where stopping is a legitimate outcome (plan 5a); 下车点 = 三个特别推荐的落脚点, after stages 3, 5, 9 | ROADMAP 5 |
| 对标 | an outside yardstick the learner can show an engineer friend | ROADMAP 4; full rows on each stage page |
| 方块 | one of the 12 skill areas | `docs/roadmap/skill-map.md` |
| 原理小课 | a 10-20 minute just-in-time fundamentals lesson | `docs/roadmap/skill-map.md` (方块 1), `docs/roadmap/threads.md` (原理线) |
| 薄片 | the thin full-stack slice at the opening of stage 5 | `stages/05-backend-api/README.md` |
| 工程课 | a lesson of the stage 2 engineering strand | `stages/02-programming/README.md` |
| 约束力 / 规则类型 / 岗位期望 | the two independent labels of plan G3 and the separate label for hiring expectations; plain wordings as in `docs/roadmap/threads.md` (规范线) | plan G3 |
| 装箱 | packaging a program with its runtime (a container); the brief's analogy is the shipping container | `docs/roadmap/threads.md`, stage 9 page |

Analogy candidates for later stages are collected in each research brief's "plain-Chinese analogies" section (for example 测试 = 写给电脑执行的验收清单; `pyproject.toml` = 购物清单 and `uv.lock` = 购物小票; 索引 = 书后的索引; 事务 = 转账要么都成要么都不成; 环境变量 = 进程出门随身带的便签). When two briefs offer rival analogies for one term, pick one in the stage design, add it to this section with its "where it breaks" sentence, and use only that one. Analogies that the `cs-fundamentals` brief found misleading and that must not be used: branch = copy of the folder; Git = cloud sync; container = small virtual machine; environment variable = global setting; API = waiter; HTTP = phone call.

## 6. Rule ids

### 6.1 Assigned [fixed ids: plan section 4. The plan's bracket gives only the label family; `tools/courselib/syllabus.py` holds those families and `validate` checks each card's 规则类型 against them]

| Id | Rule | 规则类型 (full G3 label) | Lesson |
|---|---|---|---|
| META-01 | 报错三问 | 规范·本课程约定 | 0.1 |
| WS-01 | 代码不放网盘同步目录 | 惯例·平台与工具 | 0.2 |
| WS-02 | 命名用小写英文加短横线 | 惯例·平台与工具 | 0.2 |
| META-02 | 每条规范问三件事：谁说的、多强制、哪年的版本 | 规范·本课程约定 | 0.3 |
| PM-01 | 每个任务有明确的完成标准 | 惯例·事实标准 | 0.4 |
| PM-02 | 固定周期复盘 | 惯例·事实标准 | 0.4 |
| TERM-01 | 不照抄看不懂的命令 | 规范·本课程约定 | 1.1 |
| TERM-02 | 删除前先看清要删什么 | 规范·本课程约定 | 1.2 |
| ED-01 | 打开文件夹而不是单个文件 | 惯例·平台与工具 | 1.4 |
| ED-02 | 文本统一 UTF-8 和 LF，用 `.editorconfig` 说明 | 惯例·事实标准 | 1.4 |
| DOC-01 | 每个项目根目录有 README.md | 惯例·平台与工具 | 1.5 |
| DOC-02 | README 回答五个问题 | 惯例·平台与工具 | 1.5 |
| GIT-01 | 一个项目一个仓库，在项目根目录初始化 | 惯例·平台与工具 | 1.6 |
| GIT-02 | 提交前确认身份设置 | 惯例·平台与工具 | 1.6 |
| GIT-03 | 提交前先看改了什么 | 惯例·平台与工具 | 1.7 |
| GIT-04 | 执行会丢数据的命令前先看状态 | 规范·本课程约定 | 1.8 |
| REPO-01 | 密钥、密码、令牌永不入库 | 行业要求 | 1.9 |
| REPO-02 | `.gitignore` 从官方模板起步 | 惯例·平台与工具 | 1.9 |
| COMMIT-01 | 提交信息遵循 Conventional Commits | 惯例·事实标准 | 1.10 |
| COMMIT-02 | 一次提交一件事 | 惯例·平台与工具 | 1.10 |
| ACC-01 | 开启双重验证 | 行业要求 | 1.11 |
| ACC-02 | 提交邮箱用隐私地址 | 惯例·平台与工具 (约束力 推荐, fixed by the plan) | 1.11 |
| REMOTE-01 | 重要仓库在别处有第二份 | 惯例·平台与工具 | 1.12 |
| REMOTE-02 | 公开或推送前检查有没有密钥和隐私 | 行业要求 | 1.12 |
| PUB-01 | 公开仓库三件套 README、LICENSE、.gitignore | 惯例·平台与工具 | 1.13 |
| HELP-01 | 提问给出目标、做法、期望、实际报错原文、版本 | 惯例·事实标准 | 1.14 |
| FRESH-01 | 用一个做法前确认它的版本和日期 | 规范·本课程约定 | 1.14 |
| AI-01 | AI 的改动先看 diff 再接受 | 规范·本课程约定 | 1.15 |
| AI-02 | AI 参与的提交如实署名 | 惯例·平台与工具 | 1.15 |
| PM-03 | 每个阶段结束做一次复盘 | 惯例·事实标准 | 1.16 |

Thirty ids in fifteen families. The 约束力 of each rule (必须 / 推荐 / 参考 with its scope) is set on its card in the lesson's `rules.md`; the handbook and `STANDARDS.md` are assembled from those cards.

The labels above follow the plan G3 procedure inside the family the plan gives (source per row: the `standards-landscape` brief, section 6). Two rows differ from that brief's own code because the plan's family is 惯例: WS-02 (brief N1: 规范·组织, Google's filenames guide) and REMOTE-01 (brief G7: 规范·团队约定). AI-02 follows brief H3 (惯例·平台与工具). If a lesson card settles one of these differently, the plan's family in `syllabus.py` must change in the same batch; record it here and on the stage 0 or stage 1 page.

### 6.2 Naming scheme for new ids [proposed]

- Shape: `FAMILY-NN`. `FAMILY` is two to six upper-case ASCII letters naming a topic family; `NN` is a two-digit number, sequential within the family, starting at 01.
- Continue existing families where the topic fits: the next project-management rule is `PM-04`, the next Git rule `GIT-05`, the next AI rule `AI-03`.
- An id is never renumbered, reused or deleted. A rule that no longer holds keeps its id, is marked retired with a date on its card and in `STANDARDS.md`, and is explained in a "旧教程提醒" box if learners will still meet it elsewhere.
- One id, one rule sentence, one introducing lesson (`学于`). At most two new ids per lesson (plan G5). A rule gets an id only when a lesson teaches it after letting the learner feel the problem (plan I2); a norm merely listed in `STANDARDS.md` or `ROADMAP.md` has no id yet.
- Every card carries 约束力, 规则类型, 谁说的 and 核对日期 with a 复核周期 (plan G3, I2); `validate` rejects a card without any of the 13 fields.
- Register every new id in section 6.1 of this file in the batch that creates it, and add its expected labels to the syllabus data so `validate` can check them.
- Suggested family prefixes for the norms the stage pages (`stages/<NN-slug>/README.md`) name for later stages. They are suggestions; check this table and `STANDARDS.md` for collisions before assigning.

| Family | Topic | First needed |
|---|---|---|
| BR, PR, REV | branches; pull requests; code review | stage 2 |
| PY, TYPE | Python style; type hints | stage 2 |
| DATA | encodings, time, money in programs | stage 2 |
| DBG | debugging routine | stage 2 |
| TEST | tests | stage 2-3 |
| PKG | project layout, dependencies, lockfile | stage 3 |
| CI, REL | continuous integration; versions, changelog, releases | stage 3 |
| CFG, LOG, ERR | configuration and secrets; logging; error handling | stage 3 |
| SUP | supply chain | stage 3, 7 |
| SQL, DB | SQL style and safety; schema, transactions, migrations, backups | stage 4 |
| API, HTTP | API design; HTTP semantics | stage 5 |
| WEB, A11Y, JS | HTML and CSS; accessibility; JavaScript | stage 6 |
| TS, FE | TypeScript; front-end application practice | stage 7 |
| SEC, PRIV | application security; privacy | stage 8 |
| OPS | delivery and operations | stage 9 |
| TEAM | team process | stage 10 |
| ARCH | design documents, decision records, architecture | stage 3, 11 |

## 7. Unit budget and lesson template (by reference)

Do not restate these; follow the plan and `docs/authoring/`.

| Topic | Where it is defined | One-line reminder |
|---|---|---|
| Unit budget | plan G5 | a lesson is 2-3 stations; a station is 20-25 minutes, one new concept, at most five new commands, one independent exercise with one check, and ends at a save point; at most two new rule cards per lesson |
| Lesson text | plan I1 | header block; 先想一想; per station 概念 / 跟我做 / 补全 / 自己做; 本课行规; 收尾 |
| Rule cards | plan I2 | 约束力（with scope）, 规则类型 (one of the seven G3 labels, never 个人偏好), 规则, 谁说的, 核对日期 + 复核周期, 谁来管 + 不遵守的后果, 为什么, 正例, 反例, 怎么检查, 例外, 旧教程提醒, 学于 |
| Lesson module | plan I3 | `META`, `TERMS`, `checks`, `HINTS` (four levels), `REVIEW`, `SCENARIOS`, `EXAM` |
| Tool commands | plan I4; `docs/authoring/tool-api.md` | `status`, `check`, `hint`, `scenario`, `review`, `exam`, `journal`, `doctor`, `fresh`, `validate` |
| Gates | plan I7 | 8-12 observable criteria of which 3-4 are must-pass; 4-6 cold tasks in two parallel forms; two explain-back questions; one debugging task; a separate examiner prompt |
| Verification classes | plan G6 | 已实测 / 仅对照官方文档 / 无法验证, with the fixed marks |
| Freshness | plan G4 | nothing from memory; `verified` metadata per lesson; 旧教程提醒 boxes |
| Quality steps | design 5.10; `docs/authoring/` | real execution in a simulation home; blind play-through with novice-error injection; fact check against primary sources; mechanical budget count; adversarial tests of the tools |

What a later stage's design must decide explicitly, because the plan was written for stages 0-1:

1. **Which supports are withdrawn.** Guidance should shrink as the learner grows (the expertise-reversal finding in the `pedagogy-prior-art` brief). List them: glosses of English output, 补全 steps, command expansions, the number of hint levels before a reveal.
2. **How practice volume fits the budget.** Stage 2 needs far more practice per concept than two or three stations hold (open question 1).
3. **Which exercise kinds the checker supports.** The `beginner-programming-pedagogy` brief requires predict, trace, Parsons, fix, modify, make, explain and review exercises, not only "make the check pass".
4. **Which steps nobody can execute for the learner** (debugger, browser DevTools, platform dashboards) and how they are marked and verified.

## 8. The learner model

### 8.1 What is recorded [fixed: plan I4, I5, G11]

| File | Owner | Content |
|---|---|---|
| `learner/state.json` (schema 1) | tool | `stations`: per station first pass time, attempts, highest hint level, confidence rating, status `passed` / `assisted` / `open` · `review`: per item Leitner box, due date, history · `exams`: per gate and task the form, result, date · `sessions`: date, minutes · `decisions`: free-form keys such as `workspace_location`, `commit_signing` |
| `learner/log.jsonl` | tool | append-only events with timestamps (checks, hints, reviews, exams) |
| `learner/last-result.json` | tool | the last check result, for the tutor |
| `learner/profile.md` | learner | answers to the intake questionnaire of 0.1 (the design names weekly time, session length, English reading level and network environment among its questions) |
| `learner/misconceptions.md` | tutor | misconceptions the tutor has observed |
| `journal/YYYY-MM-DD.md` | learner | per session: 做了什么 / 卡在哪 / 下次从哪开始, optionally 哪里看不懂 / 哪里太慢 |
| `notes/my-rules.md` | learner | each rule in the learner's own words |
| `CHANGELOG.md` | builder | errata: where a lesson did not match the learner's screen |

### 8.2 How the next stage's design must use it [proposed]

A stage design is not accepted without a section "Evidence from the learner model" that answers these questions from the files, with numbers, and states the design decision each answer led to.

| Question | Read | Decision it drives |
|---|---|---|
| How long does a station really take? | `sessions` minutes against stations passed | station length; re-estimate of the stage's hours and of the calendar table in `ROADMAP.md` section 5 |
| When and how often does the learner study? | `sessions` dates; `profile.md` | lesson size; whether practice sets can assume 20-minute or 60-minute sittings; spacing of reviews |
| Where did the learner struggle? | attempts and highest hint level per station; `assisted` stations; the 卡在哪 lines | prerequisite refreshers at the start of the stage; which analogies to replace |
| Is the learner's confidence calibrated? | confidence ratings against outcomes | how many unassisted checkpoints; whether to ask for a rating more often |
| What has been forgotten? | review boxes and lapse history | which fluent items re-enter the new stage's warm-ups; interleaving |
| What is not solid at the gate? | `exams` per task; the gate's practice list | a remedial lesson before new material; never build on a failed must-pass criterion |
| Which misunderstandings persist? | `misconceptions.md` | targeted predict and fix exercises with diagnostic feedback |
| What did the learner decide? | `decisions`; `profile.md` | product thread; signing; strictness; English gloss level; mirrors and hosting if the network environment requires them |
| Where did lessons drift from the screen? | `CHANGELOG.md` errata | which step classes to avoid or re-verify; GUI steps to rewrite as "goal plus text to look for" |
| What did the learner find unclear or slow? | the two optional journal fields | voice, pace, what to cut |

Also required in every stage design: a list of the supports withdrawn (section 7), the stage's thread checklist with every line accounted for (section 4), the product increment (section 3), new rule ids (section 6), new register entries (section 5), and the roadmap diff (section 9.3).

If the files are thin (few sessions, no ratings), say so and design conservatively; do not invent a learner.

## 9. The skill map

### 9.1 Areas and levels [areas: `docs/roadmap/skill-map.md`; scale taken over from the design's first draft, which is not saved in the workspace]

Twelve areas: 1 计算机与网络基础 · 2 工具与工作环境 · 3 编程 · 4 调试与读代码 · 5 前端 · 6 后端与数据 · 7 代码质量 · 8 交付与运维 · 9 安全与隐私 · 10 架构与设计 · 11 需求、沟通与项目管理 · 12 与 AI 协作. Four levels: 知道 / 在指导下会做 / 能独立做 / 能按规范做并讲给别人听. A level counts only with three kinds of evidence: 做 (a passing check), 讲 (an explanation in the learner's words), 证 (an artefact). Level 3 has two sides in every area: build a minimal version without AI, and find the errors in AI or other people's output.

How the areas came about: the first draft's twelve, with the senior engineer's corrections (design review, issue 18). "Debugging and reading code" was added; to stay at twelve, "back end" and "data" were merged (this file's choice; the reviewer did not say which rows to merge); "project and team management" became "requirements, communication and project management" with four named sub-skills (spec writing, estimation, technical writing, English reading); "computer and network fundamentals" was widened. Sub-skills and their homes: accessibility and performance in 5; API design and data modelling in 6; code review in 7; observability and cost in 8; privacy, licences and supply chain in 9; process in 11; building AI features in 12.

### 9.2 Expected movement per stage [proposed]

| Stage | Areas it mainly moves | To about |
|---|---|---|
| 0-1 | 2 → 2; 11 → 2 (own learning only); 12 → 2 (accepting changes only); 1, 4, 8, 9 → 1 | batch 1 (in construction) |
| 2 | 3 → 2-3; 4 → 2-3; 2 → 3; 7 → 2; 1 → 2 | |
| 3 | 7 → 3; 2 → 4; 3 → 3; 12 → 3; 9 → 2; 10 → 2; 8 → 2 | exit ramp |
| 4 | 6 → 2-3 (data); 1 → 2-3 | |
| 5 | 6 → 3 (API); 8 → 2-3; 9 → 2-3 | exit ramp |
| 6 | 5 → 2; 3 (second language) → 2; 1 → 3 | |
| 7 | 5 → 3; 3 → 3-4; 7 → 3-4 | |
| 8 | 9 → 3-4; 6 → 4; 5 → 4 | |
| 9 | 8 → 4; 4 → 4; 1 → 4 | exit ramp |
| 10 | 11 → 3; 7 → 4 (review); 12 → 4 | |
| 11 | 10 → 3; everything consolidated | course target: level 4 except areas 10 and 11 at level 3 |

The course target follows the `skill-model` brief's synthesis (its "L3 in twelve areas, L2 in design and planning", mapped onto this four-level scale). It is a course convention (规范·本课程约定), not an employer's bar (岗位期望), and a solo learner can only partly evidence the levels that involve other people.

### 9.3 The roadmap diff every stage design must contain

A short table: which areas this stage moves, from which level to which, with the gate criterion that evidences each claim; the stage's planning hours against the hours in `ROADMAP.md` and the stage page; any change to order, product increment, threads or yardsticks. A deviation that matters becomes a decision record in `docs/adr/` and an edit to `ROADMAP.md`.

## 10. Yardsticks and research inputs per stage

Yardsticks ("对标") are named in the `ROADMAP.md` overview table (section 4) and listed with URLs and "how it differs" notes on each stage page (`stages/<NN-slug>/README.md`, section 「对标」). All returned a normal page on 2026-11-19. Re-check every URL and every "how it differs from this course" note when the stage is generated; replace a yardstick that has died or gone stale.

| Stage | Yardsticks (2026-11-19) | Research briefs that feed it (topic keys) |
|---|---|---|
| 0 | The Odin Project Foundations (Introduction, Prerequisites); MDN Learn web development, Getting started (zh-CN) | `foundations-macos`, `pedagogy-prior-art`, `fullstack-curricula` |
| 1 | Pro Git 2nd edition (zh), chapters 1-2; MIT Missing Semester 2026 | `foundations-macos`, `git-norms`, `github-collab-ci`, `ai-pairing-norms` |
| 2 | CS50P; University of Helsinki Python Programming MOOC 2026 | `beginner-programming-pedagogy`, `git-norms`, `cs-fundamentals`, `uv-packaging`, `foundations-macos` |
| 3 | Scientific Python Development Guide; Google Engineering Practices | `quality-tooling`, `uv-packaging`, `review-testing-practice`, `security-config-logging`, `github-collab-ci`, `project-mgmt-norms`, `research-code-engineering` |
| 4 | CS50 SQL; PostgreSQL documentation, Part I Tutorial | `backend-data-stack-2026` (sections 7, 11), `cs-fundamentals`, `web-security-2026` |
| 5 | FastAPI tutorial (zh); Zalando RESTful API Guidelines | `backend-data-stack-2026`, `delivery-ops-2026`, `cs-fundamentals`, `web-security-2026` |
| 6 | MDN Learn web development, Core modules (zh-CN); 现代 JavaScript 教程 | `frontend-stack-2026` (steps F1-F5), `cs-fundamentals`, `web-security-2026` |
| 7 | react.dev (zh); Full Stack Open parts 1, 2, 5, 9 (English edition) | `frontend-stack-2026` (steps F6-F10) |
| 8 | OWASP Top 10:2025; OWASP ASVS 5.0.0 | `web-security-2026`, `backend-data-stack-2026` (section 8) |
| 9 | Full Stack Open parts 11-12; The Twelve-Factor App (zh) | `delivery-ops-2026` |
| 10 | Scrum Guide 2020 (zh); Software Engineering at Google | `project-mgmt-norms`, `github-collab-ci`, `ai-pairing-norms` |
| 11 | C4 model; adr.github.io | `cs-fundamentals` (section 2.1, S10), `project-mgmt-norms`, `web-security-2026` (section 10) |
| electives | see `docs/roadmap/electives.md` | `research-code-engineering`, `skill-model`, `fullstack-curricula` (section 6.3) |

Facts in the briefs that were already moving on 2026-11-19 and must be re-verified before use: the PostgreSQL major version (19.0 released 2026-11-19 and marked current in versions.json; 18.7 still supported; the senior review advised teaching on 18.x until 19 has a couple of point releases); the Helsinki MOOC yardstick (the 2026 edition closes at the end of 2026; link the then-current edition); the Python stable line (3.15.2 current, the machine on 3.14.9); FastAPI (0.x, many releases a month); the whole front-end toolchain (default linter, TypeScript, router and test-runner majors all changed between June and November 2026); free tiers and prices of every hosting platform; action versions and the pinning rule for `astral-sh/setup-uv`; `uv audit` (experimental); the GitHub plan limits for private repositories.

## 11. Open questions to settle when stage 2 is generated

1. **Lesson size vs the unit budget.** The stage has 150-200 planning hours; the outline on `stages/02-programming/README.md` has about 44 lessons; a lesson under plan G5 is 40-75 minutes. The `beginner-programming-pedagogy` brief wants about 8-10 exercises per lesson and estimates 80-130 hours for its 25 programming lessons alone. Decide where the practice lives: recommended reading of the evidence is "lessons keep the G5 budget; each is followed by a practice set of mixed exercise kinds done over several sittings; projects and unit checkpoints sit between blocks". State the expected split of hours and check it against `sessions`.
2. **The exercise runner.** Extend `tools/course.py` (standard library only, Python 3.9-3.14, decision record 0007), or add a per-project runner inside the learner's uv project as in the brief's prototype (`uv run learn.py`, pytest underneath, one exercise shown at a time, misconception-specific messages)? Either way the learner must not face raw test-runner output before the testing lesson, and the checker must never print a traceback (plan I4).
3. **Python version.** Stay on 3.14 and pin it in `.python-version` (recommended by two briefs). Decide `requires-python` deliberately: with `>=3.14`, the formatter rewrites `except (A, B):` to the 3.14-only form. Link documentation by version (`/3.14/`), because unversioned links now show 3.15.
4. **Where stage 2 code lives.** Plan G15 names three practice places. Stage 2 needs a fourth kind: one repository per stage project under `~/Developer` (the senior engineer's proposal) and a place for exercise projects. Decide names and whether exercises live inside the course repository. Constraints found by the `uv-packaging` brief on this machine: a project name must not start with a digit (uv 0.13.5); nested `uv init` inside a folder with a `pyproject.toml` creates a workspace; `uv init` now scaffolds a packaged `src/` layout and a `main()` entry point, which is not a day-one program (`--no-package`, `--bare`); pass `--python 3.14`; `--author-from none` avoids writing the Git identity into the file.
5. **Functions before or after loops.** No decisive evidence. The pedagogy brief's judgment: call built-ins from lesson 1, define functions after loops. The outline follows it.
6. **The network lesson.** Standard library or a third-party HTTP client? Which public rate source, if any, appears in a lesson? If the learner already has a dashboard of their own, it may use live sources; ask before choosing. Checks stay offline.
7. **Enforcing "tutor only".** A sentence in `CLAUDE.md` is context, not enforcement. The pedagogy and AI briefs propose a custom output style plus a hook that denies edits under the exercise folders; the build sandbox cannot write `.claude/` settings, so this must ship as a template the learner installs. Decide, and test with adversarial prompts.
8. **Pull-request practice on a free account.** A free personal account cannot enforce branch protection or required checks on a private repository. Either make `fx` public (it then needs the public-repository hygiene of stage 1, including the e-mail check) or teach "the inspector is present but the gate is not locked" honestly.
9. **Seeded-defect review.** Lesson "合并请求（二）" needs a prepared branch with four or five planted defects that the learner must find and send back. Who prepares it, and how is it delivered without the builder committing in the learner's repository (design 5.8)?
10. **Gate ids.** Existing: `gate-0`, `gate-a`, `gate-b`, `gate-1`. `ROADMAP.md` shows `gate-2` ... `gate-11` as provisional stage gates. Unit checkpoints inside stage 2 need ids that do not collide with `gate-a` and `gate-b` (for example `gate-2a` ...). Decide and register in the syllabus data.
11. **Folder slugs for later stages.** Settled in batch 1 (the stage pages exist): `00-orientation`, `01-foundations`, `02-programming`, `03-professional-practice`, `04-data-sql`, `05-backend-api`, `06-web-basics`, `07-modern-frontend`, `08-fullstack-security`, `09-delivery-ops`, `10-team-management`, `11-architecture-capstone`. Lesson folders go inside them as `NN-slug/`.
12. **English support.** How fast the glosses are withdrawn depends on `learner/profile.md`. If the learner reads English comfortably, withdraw in the first block; if not, keep a gloss table for error messages through the stage and add the optional English-for-developers courses listed in `docs/roadmap/threads.md`.
13. **Time-zone and locale examples.** Do not assume Asia/Shanghai, a Chinese system language or a UTC+8 offset, or any other time zone or interface language. Ask the learner.
14. **Mastery threshold and retakes.** The pedagogy brief suggests unit checkpoints of 20-30 minutes with a pass mark of about 80 percent and variant retakes; these numbers are judgment calls. Decide and state them in the gate rubrics.
15. **Classes: how deep.** Enough to read the stage 5 framework code (dataclasses, attributes, methods, composition); inheritance stays shallow.
16. **Continuity at the boundary.** The design triggers generation at 70 percent of a stage. The instructional-design review asks that the first lessons of the next stage exist before the gate. Confirm that the first batch of stage 2 (four or five lessons) is ready before lesson 1.16.
17. **The ledger for the principles thread.** The `cs-fundamentals` brief proposes a learner-visible ledger (see / use / explain per concept), for example a handbook page. Plan section 2 has no such file. Decide where it lives.
18. **Human touchpoints.** Three reviews recommend at least one human look at the learner's work per exit ramp. `ROADMAP.md` offers it as optional. Decide whether stage 2 names a concrete option (a mentor platform, a friend, a public repository).
19. **Region.** If the intake questionnaire says the learner works from mainland China, package mirrors, a second Git host and hosting rules change; some mirrors silently disable safety checks (the `web-security-2026` brief). Nothing about this was verified for the learner on 2026-11-19.
20. **The existing dashboard (not a stage 2 question; recorded so it is not lost).** Does the product thread always rebuild the exchange-rate dashboard from zero, or may a later stage adopt a learner's existing dashboard code (if they have one)? The design does not say (section 3 of this file). Ask the learner before the stage 4 design at the latest; if the existing code is adopted, it enters as "unfamiliar code to read, pin with tests and change", which the senior engineer's review wanted more of.
21. **Cost and lead time of generating a stage.** The reviews asked that the continuation promise state how long generation takes and what it costs the learner in usage. Neither the design nor any brief gives a figure, so `ROADMAP.md` section 8 gives none. Measure both when stage 2 is generated and write them into `ROADMAP.md`.

## 12. Where the evidence and the design differ (followed the design; recorded here)

1. **Total hours.** Design: about 1,000-1,450. The `fullstack-curricula` brief's synthesis: about 1,150-1,770; programmes with real assessment publish 1,200-1,800+; the senior engineer's planning range was 1,200-1,600. `docs/roadmap/sources.md` lists the published figures; `ROADMAP.md` section 5 says the design's figure sits at the low end. Recalibrate from `sessions` after stage 1.
2. **Stage 1 hours.** Design: 20-25 (39 stations). The senior engineer estimated 35-45 and the brief 40-60 for a larger stage 1; the design moved branches, pull requests, pipes and `PATH` to stage 2.
3. **Stage 3 hours.** Design: 60-90 (the senior engineer's figure). The brief: 100-150.
4. **One cell of the calendar table.** Design 5.5 says "3 年多" for stage 9 at 5 hours a week; the design's own hours give 3.2-4.4 years. Three more cells are short at their upper end: 10 h/week to stage 9 (up to 2.2 years, printed 1 年半～2 年), 20 h/week to stage 3 (up to 3.7 months, printed 约 3 个月), 20 h/week to stage 9 (up to 13.2 months, printed 10 个月～1 年). `ROADMAP.md` keeps the design's table and states the longer ends in the sentence under it.
5. **Skill model.** Design: 12 areas x 4 levels. The `skill-model` brief argues for 14 areas x 5 levels (an explicit level 0; separate areas for version control, communication, and learning and professional practice). The twelve were kept, with the reviewer's corrections.
6. **Thin slice.** The senior engineer proposed a guided 8-10 hour "tracer bullet" right after stage 3; the brief proposed a deployed thin slice at the opening of the back-end stage. The design's stage list has no separate unit; `stages/05-backend-api/README.md` places a thin slice at the opening of stage 5 inside that stage's hours.
7. **External human calibration.** Three reviews ask for human review points; the design relies on AI checks plus the learner's own feedback. `ROADMAP.md` offers a human look at each exit ramp as optional.
8. **Language of commit subjects.** Design section 6 fixes "English type prefix + Chinese subject". The senior engineer's English ladder switches subjects to English from stage 5. `ROADMAP.md` presents the switch as a default the learner decides at stage 5.
9. **Stage 1 has no programming lessons.** The brief calls a tools-only stage the highest dropout risk and suggests practising on the learner's existing Python project (if any). The design answers with a program run and edited in 0.1 and a web page online in stage 1; it leaves any existing project of the learner untouched.
10. **Deployment platform.** The `delivery-ops-2026` brief's default for the capstone needs a credit card on file (bills under a small threshold are waived), with a no-card fallback. The design promises that stages 0-8 cost nothing and that stage 9 has free options. Both hold on 2026-11-19 only through the fallback path; free tiers changed several times in 2026. Re-verify at stage 5 (first back-end deployment) and at stage 9.

## 13. Change log of this file

| Date | Change | By |
|---|---|---|
| 2026-11-19 | Roadmap split into a short `ROADMAP.md`, `docs/roadmap/` and twelve stage pages; references updated. Rule labels moved to the revised plan G3 vocabulary (§6.1, §6.2, §7, §9.2); rule-card fields per revised plan I2; stage 0-1 marked as in construction; PostgreSQL 19, Helsinki and calendar-cell notes (§10, §12). | roadmap editor (Claude) |
| 2026-11-19 | First version, written with `ROADMAP.md` for batch 1. Sources: design (second version), plan sections 1, 2, 4, 5a, the five design reviews, twenty research briefs. | roadmap builder (Claude) |
