# Brief: project-mgmt-norms — management norms around the code, for a solo beginner who may later join or lead a small team

Researched 2026-11-19. Reader: lesson builders (not the learner). Facts are in English; terms and templates are in Chinese so they can be pasted into lessons.
Basis tags: **[local]** = I ran it on this machine today. **[source: URL]** = I read that primary source today (URLs written without `https://`). **[memory]** = not verified today.
Scratch root (called `$S` below): `<scratch>/research/project-mgmt-norms`

## 0. Bottom line for course design

1. Most "agile vocabulary" beginners meet (user story, story points, velocity, epic, Definition of Ready, acceptance criteria, burndown as a rule) is **not in the Scrum Guide 2020**. It comes from XP and community practice. The Guide itself only fixes: Sprint of one month or less, five events, three artifacts each with a commitment (Product Goal, Sprint Goal, Definition of Done), three accountabilities. [source: scrumguides.org/scrum-guide.html]
2. A solo developer cannot "do Scrum" (three accountabilities, team events). What transfers: one goal per period, small finished increments, an explicit **Definition of Done**, and a fixed review-plus-retrospective cadence. The Kanban Guide's minimum (visible workflow, controlled WIP, four flow measures) fits one person without modification. [source: kanbanguides.org/english/]
3. Recommended minimum system ("个人工程管理最小套件"): issues with acceptance criteria → 4-column board with a WIP limit → DoD checklist that is mostly one command → changelog + SemVer tags + release checklist → ADRs → 30-minute weekly review → small debt and risk registers → blameless postmortem after any "wrong numbers were used" event.
4. The whole release / hotfix / rollback / feature-flag / ADR-numbering / issue-form loop was run locally with only git, uv 0.13.5, ruff 0.17.2, make, system Ruby and Python stdlib, offline except for one `uv audit` call (§7). Files that passed are in `$S/sandbox/demo-fx/`.
5. For Chinese framing, the Alibaba Java manual's style (【强制】/【推荐】/【参考】 + 说明/正例/反例 + 版本历史) is verified from the 黄山版 PDF and is the right model for the course's own 规范 document (§5).

## 1. What I verified and how

**Read today (primary unless marked):** Scrum Guide 2020 (EN HTML and the official 简体中文 PDF, text extracted with a local PDFKit script); Kanban Guide v2025.5; Agile Alliance glossary (user stories, epic, DoD, DoR); Bill Wake INVEST; Fowler GivenWhenThen, TechnicalDebt, TechnicalDebtQuadrant; Hodgson Feature Toggles; DSDM MoSCoW; Intercom RICE; Shape Up ch.3; Ron Jeffries "Story Points Revisited"; Mike Cohn on DoR; GitHub Docs (about issues, issue-form syntax, form validation errors, template chooser, sub-issues, issue types, labels, milestones, Projects, board layout, roadmap layout, iteration fields, CODEOWNERS, community health files, security policy, private vulnerability reporting, licensing, READMEs, releases, generated release notes, closing keywords, plans, Dependabot ecosystems); Nygard's ADR post; MADR 4.0.0 and its minimal template; adr.github.io; AWS Prescriptive Guidance "ADR 流程" (zh-CN); Malte Ubl "Design Docs at Google"; *Software Engineering at Google* ch.2 and ch.10; Rust RFC template; Diátaxis (home, start-here); Write the Docs "Docs as Code"; Make a README; Standard Readme spec; Open Source Guides; Keep a Changelog 1.1.0 (en, zh-CN); SemVer 2.0.0 (en, zh-CN); CalVer; Conventional Commits 1.0.0 (en, zh-hans); towncrier docs; choosealicense.com; OSI MulanPSL-2.0; Contributor Covenant 3.0 (en, zh-cn); Google SRE book (postmortem culture, example postmortem, being on-call, managing incidents, release engineering); SRE Workbook (postmortem culture); PagerDuty postmortem template and severity levels; Allspaw "The Infinite Hows"; DORA "Streamlining change approval"; SPEC 0; Python devguide versions; uv docs (locking/syncing, Renovate, Dependabot); PyPI yanking; Google eng-practices (review speed); NIST glossary "risk"; RFC 2119; Alibaba《Java 开发手册（黄山版）》PDF (text extracted locally), p3c README; ruanyf/document-style-guide; chinese-copywriting-guidelines; TAPD docs (Tencent Cloud); Azure Boards zh-CN; Aliyun 卓越架构 "故障复盘"; Simon Tatham "How to Report Bugs Effectively" (en, zh); GTD Weekly Review checklist; ProdPad Now-Next-Later; Personal Kanban 101; CIO RACI article (secondary).

**Could not read today:** Atlassian agile pages (script-rendered, only navigation came back); BMJ Quality & Safety "The problem with '5 whys'" (403; citation confirmed by search only); Etsy "Blameless PostMortems" (403); PMI risk paper (403); ASQ impact-effort matrix (403); Stack Overflow MRE help page (blocked); Kanban University Chinese guide (DNS failure); GitLab handbook meeting pages (navigation only); GB/T 1.1-2020 text; Toyota "ask why five times" page (404). Claims depending on these are tagged [memory].

**Caveat on [source] tags:** web pages were read through a fetch tool that returns a model-written digest of each page, not the raw text. Exact numbers (limits, dates, percentages) should be re-checked on the page before a lesson prints them; one drift already seen: a beta-era discussion found by search gives 50 sub-issues per parent, the current docs digest gives 100. The two PDFs and everything tagged [local] were read or run directly.

**Local runs:** see §7. Nothing was installed globally, nothing pushed, no account used, global Git config untouched (repo-local identity `Demo Learner`). Two PDFs (Chinese Scrum Guide, Alibaba manual) were turned into text with a 15-line Swift + PDFKit program (`$S/tools/pdftext.swift`, built with the CommandLineTools `swiftc`); the extracted text is in `$S/extracted/`, and the term checks and rule counts in §4 and §5 are `grep` results on it.

## 2. What changed recently (older tutorials will mislead here)

| Topic | State today | Basis |
|---|---|---|
| Scrum Guide | 2020 is still the official text. Versus 2017: "Development Team" became "Developers"; one team with three accountabilities (official 中文版 says 三种职责); Product Goal added; each artifact has a commitment; "self-managing" replaces "self-organizing"; the three Daily Scrum questions were removed; IT-specific words removed. A separate community "Scrum Guide Expansion Pack" (2025, Jocham / Coleman / Sutherland) is a companion, not a replacement. | [source: scrumguides.org/scrum-guide.html; scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Chinese-Simplified.pdf p.13-14]; Expansion Pack via search only |
| Kanban Guide | v2025.5 (1 May 2025) supersedes v2020.12. WIP must be controlled but a per-column limit is not required; an SLE (for example 85% of items within 8 days) is part of the Definition of Workflow. | [source: kanbanguides.org/english/] |
| ADR templates | MADR 4.0.0 (2024-09-17): name is again "Markdown Architectural Decision Records"; optional YAML front matter `status / date / decision-makers / consulted / informed`; full, minimal and bare templates; folder `docs/decisions`. | [source: adr.github.io/madr/] |
| Contributor Covenant | 3.0 is the latest (section names changed: Encouraged / Restricted Behaviors, "Addressing and Repairing Harm" ladder). A 简体中文 translation of 3.0 exists ("贡献者公约"). Tutorials pointing at 2.1 or 1.4 are stale. | [source: contributor-covenant.org/version/3/0/code_of_conduct/; contributor-covenant.org/translations/] |
| Keep a Changelog | Format version still 1.1.0 (site's own changelog is at 1.1.2, 2024-09-27). | [source: keepachangelog.com/en/1.1.0/] |
| GitHub Issues | Sub-issues (≤100 per parent, 8 levels), issue types (default Task / Bug / Feature, also for user-owned repos), issue dependencies exist. Tasklist blocks were retired 2025-04-30; the single legacy `ISSUE_TEMPLATE.md` was retired 2025-03-30; Projects (classic) was sunset 2024-08-23. | [source: docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues; .../using-issues/adding-sub-issues; .../configuring-issues/managing-issue-types-in-an-organization]; retirement dates from github.blog changelog titles via search |
| GitHub issue forms | Docs still label YAML issue forms "public preview". New since older tutorials: `upload` field type, top-level `type:` and `projects:` keys. | [source: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms] |
| Community health files | Table lists ACCESSIBILITY.md and VULNERABILITY_REPORT.yml next to CODE_OF_CONDUCT, CONTRIBUTING, FUNDING, SECURITY, SUPPORT and the templates; GOVERNANCE.md is not in it (older lists included it [memory]). Lookup order `.github/` → root → `docs/`. LICENSE cannot be an account-wide default. | [source: docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file] |
| GitHub Free, private repos | Protected branches, code owners, required reviewers, wikis, Pages and insights graphs are listed under Pro, so a CODEOWNERS file in a private repo on Free is not enforced. | [source: docs.github.com/en/get-started/learning-about-github/githubs-plans] |
| Python lifecycle | 3.15 released 2026-10-09 (bugfix); 3.14 bugfix; 3.13, 3.12, 3.11 security-only; 3.10 end-of-life since 2026-10. Bugfix phase is 2 years from 3.13 on. SPEC 0 lets scientific packages drop Python 3.12 in 2026 Q4. | [source: devguide.python.org/versions/; scientific-python.org/specs/spec-0000/] |
| uv | `uv version --bump <major / minor / patch / …>`, `uv audit` (prints "experimental"), `uv check` (type check via ty), `uv format` are built-in commands; plain `uv init` now creates a packaged `src/` project with `uv_build` and fills `authors` from your Git identity. Older tutorials use bump2version, pip-audit, a flat `main.py`. | [local] `uv --help`, `uv init`, `uv audit` |
| Dependency bots | Dependabot has a `uv` ecosystem (table lists supported version "v0.11"; this machine has 0.13.5, so compatibility is unverified) and a `cooldown` option; uv docs still say some cases do not work. | [source: docs.github.com/en/code-security/dependabot/ecosystems-supported-by-dependabot/supported-ecosystems-and-repositories; docs.astral.sh/uv/guides/integration/dependabot/] |
| Tools that vanished or moved | Pivotal Tracker (origin of feature / bug / chore / release) shut down 2025-04-30. PagerDuty's response guide moved to docs.pagerduty.com (301 today). The old DSDM MoSCoW URL is 404; content now at agilebusiness.org "What is MoSCoW Prioritization?". | search; [local] observed redirects |
| Alibaba manual | Latest is still 黄山版 1.7.1 (2022-02-03); since 华山版 (2019) the title no longer contains "阿里巴巴". | [source: github.com/alibaba/p3c; PDF 附 1 版本历史] |
| Git default branch here | Global `init.defaultBranch` is unset, yet `git init` creates `main`, because Xcode's bundled gitconfig sets it. | [local] `git config --show-origin --get-all init.defaultBranch` |

## 3. Facts and recommendations by area

### A. From idea to work items

- **Problem statement first.** Shape Up's "narrow the problem": ask what is actually going wrong before asking what to build; set an *appetite* (time you are willing to spend: 1-2 weeks small batch, 6 weeks big batch) instead of estimating a fixed scope. [source: basecamp.com/shapeup/1.2-chapter-03]
- **User story** = a small increment of value written from the user's side; a placeholder for a conversation, not a specification. History: XP 1998; role-feature-benefit template and the "3 C's" 2001; INVEST 2003; Given-When-Then 2006. Pitfalls: turning a requirements document into "stories"; UI components as stories. [source: agilealliance.org/glossary/user-stories/]
- **INVEST** (Bill Wake, 2003): Independent, Negotiable, Valuable, Estimable, Small (a few person-days up to a few person-weeks), Testable. Same article: SMART tasks (Specific, Measurable, Achievable, Relevant, Time-boxed). [source: xp123.com/articles/invest-in-good-stories-and-smart-tasks/]
- **Given-When-Then** (Terhorst-North and Matts, BDD): Given = state before, When = the behaviour, Then = expected observable change. Same shape as Arrange-Act-Assert, so each acceptance criterion maps to one test. [source: martinfowler.com/bliki/GivenWhenThen.html]
- **Epic** = a story too big for one iteration, kept as a placeholder and split when needed (Cohn 2004). Pitfalls: building machinery around epics; estimating them. Themes are groupings, not a hierarchy level. [source: agilealliance.org/glossary/epic/]
- **GitHub mapping:** epic = parent issue with sub-issues (or a milestone); story = issue; task = sub-issue or `- [ ]` checklist line; type = issue type (Task / Bug / Feature) or default labels (`bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`). [source: docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels]
- **Bug vs feature vs chore** (a classification popularised by Pivotal Tracker; [memory] for the exact original definitions). One table worth teaching, because it links five conventions the learner will meet separately:

| Work type | GitHub type / label | Commit type (Conventional Commits) | Changelog section | SemVer bump |
|---|---|---|---|---|
| 需求 Feature | Feature / `enhancement` | `feat` | Added, Changed | MINOR |
| 缺陷 Bug | Bug / `bug` | `fix` | Fixed | PATCH |
| 杂务 Chore (no user-visible change) | Task | `chore` `refactor` `build` `ci` `test` | none | none |
| 文档 Docs | `documentation` | `docs` | none | none |
| 不兼容变更 Breaking | any | `feat!` / footer `BREAKING CHANGE:` | Changed, Removed | MAJOR |
| 弃用 / 安全 | any | `feat` / `fix` | Deprecated / Security | MINOR / PATCH |

  [source: conventionalcommits.org/en/v1.0.0/; keepachangelog.com/en/1.1.0/; semver.org]
- **Good bug report** (Tatham, 1999, official 中文译本《如何有效地报告 Bug》): let the developer see the failure or give exact steps to reproduce it (重现); report symptoms (症状: what you saw, what you expected, error text verbatim) separately from your diagnosis (诊断, optional); give versions; be precise. [source: chiark.greenend.org.uk/~sgtatham/bugs.html; .../bugs-cn.html]
- **Good issue on GitHub:** YAML issue forms force the fields. Rules that bite: files live in `.github/ISSUE_TEMPLATE/` on the default branch; `name`, `description`, `body` required; `name` longer than 3 characters; at least one non-markdown field; unique `id`s and labels; labels named in the form must already exist; dropdown option "None" is reserved; quote `yes` / `no` / `true`. Chooser config: `config.yml` with `blank_issues_enabled` and `contact_links` (`name`, `url`, `about`). [source: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/common-validation-errors-when-creating-issue-forms; .../configuring-issue-templates-for-your-repository]
- **Estimating, and when not to.** The Scrum Guide only says Developers "size" items. Jeffries (who may have coined story points) now regrets their use for comparing teams, tracking and date prediction; he recommends slicing stories thin (ideally under a day) and delivering often. The Kanban Guide forecasts from history (SLE) instead of estimating each item. [source: ronjeffries.com/articles/019-01ff/story-points/Index.html; kanbanguides.org/english/] **Recommendation for a solo beginner:** no points, no velocity. Right-size instead: if an item will not fit in about two days, split it; give anything larger an appetite; after four weeks count finished items per week and forecast from that.
- **Prioritisation.** MoSCoW (DSDM): Must = minimum usable subset (test: "what happens if it is missing?"; if a workaround exists it is not a Must), Should, Could, Won't have *this time*; keep Must effort near 60% or less and about 20% Could as contingency; start everything at Won't and promote. [source: agilebusiness.org "What is MoSCoW Prioritization?"] RICE (Intercom, 2018) = Reach × Impact × Confidence ÷ Effort, with impact 3 / 2 / 1 / 0.5 / 0.25 and confidence 100 / 80 / 50%; the article itself warns not to follow the score blindly. [source: intercom.com/blog/rice-simple-prioritization-for-product-managers/] Value-versus-effort 2×2 (quick wins, big bets, fill-ins, time sinks) is common practice [memory]. **Recommendation:** MoSCoW per milestone, value-versus-effort in the weekly review; mention RICE only as vocabulary (with one user, "Reach" is meaningless).
- **Definition of Ready** is not in the Scrum Guide (it only says an item is ready when the team can finish it within one Sprint). First formal description October 2008, usually INVEST-based. Cohn warns a strict DoR becomes a stage gate; phrase it as guidelines. [source: agilealliance.org/glossary/definition-of-ready/; mountaingoatsoftware.com/blog/the-dangers-of-a-definition-of-ready]
- **Definition of Done.** Scrum Guide: a formal description of the quality an Increment must meet; an item that misses it is not released and goes back to the backlog. Agile Alliance pitfalls: an over-long list; a DoD that is not written down and visible. Scrum.org: DoD applies to every item; acceptance criteria belong to one item and are not part of Scrum. [source: scrumguides.org/scrum-guide.html; agilealliance.org/glossary/definition-of-done/; scrum.org/resources/blog/what-difference-between-definition-done-and-acceptance-criteria] A realistic DoD for a small Python / data-analysis project is template T4.

### B. Flow

- **Kanban Guide minimum.** Definition of Workflow (DoW) = work item definition; start and finish points; one or more in-between states; how WIP is controlled; explicit policies for moving items; an SLE. Four measures: WIP, throughput (items finished per time unit), work item age (time since start of an unfinished item), cycle time (start to finish). [source: kanbanguides.org/english/]
- **Personal Kanban** has two rules: visualise your work, limit your work in progress. [source: personalkanban.com/personal-kanban-101]
- **GitHub Projects**: table, board and roadmap layouts over issues and PRs, user-level or org-level; custom fields (single select, number, date, iteration); built-in automation (auto-add, auto-archive), charts, status updates. Board column limit: column menu → **Set column limit**; it only highlights the count, it never blocks. Roadmap: **Date fields** (start, target), **Markers** for milestones and iterations, zoom **Month / Quarter / Year**. Iteration field filters: `iteration:@current`, `@next`, `@previous`. [source: docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects; .../customizing-views-in-your-project/customizing-the-board-layout; .../customizing-the-roadmap-layout; .../understanding-fields/about-iteration-fields]
- **Scrum events for reference** (awareness only): Sprint ≤ 1 month; Planning ≤ 8 h; Daily Scrum 15 min; Review ≤ 4 h; Retrospective ≤ 3 h (for a one-month Sprint); team of 10 or fewer. [source: scrumguides.org/scrum-guide.html]
- **What a solo developer should adopt.** Board with four columns `待办 Backlog → 就绪 Ready (≤5) → 进行中 Doing (≤2) → 完成 Done`; one weekly goal sentence; weekly review (T9); milestones for releases. Skip: daily stand-up, roles, points, burndown. Before a GitHub remote exists the board can be a Markdown file (`docs/board.md`); if `gh` is not installed yet, use the web UI.
- **Milestones and roadmaps.** A GitHub milestone groups issues and PRs, has a description, due date, completion percentage and can be re-ordered by drag (up to 500 open items). [source: docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones] Roadmap format for one person: Now / Next / Later (Janna Bastow): Now = defined and certain, Next = less detail, Later = problems not yet shaped; cards are problems and outcomes, not dated features. [source: prodpad.com/blog/invented-now-next-later-roadmap/]
- **Weekly review.** Sources to borrow from: the Sprint Retrospective's purpose (inspect how the period went, pick the most helpful change) and the GTD weekly review (Get Clear, Get Current, Get Creative). [source: scrumguides.org/scrum-guide.html; gettingthingsdone.com Weekly_Review_Checklist.pdf]
- **Changelogs and release notes as communication.** Keep a Changelog: written for humans; one entry per version; newest first; ISO dates; types Added / Changed / Deprecated / Removed / Fixed / Security; keep an `Unreleased` section; mark pulled versions `[YANKED]`; a git-log dump is not a changelog. [source: keepachangelog.com/en/1.1.0/] GitHub "Generate release notes" lists merged pull requests, contributors and a full-changelog link, configurable in `.github/release.yml` (`changelog.exclude.labels`, `categories[].title / labels`); it is built from PRs, so commits pushed straight to `main` do not become items (the docs do not say this explicitly; inference). [source: docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes] Tags are Git; releases are a GitHub feature on top of tags. [source: docs.github.com/en/repositories/releasing-projects-on-github/about-releases]

### C. Decisions and documents

- **ADR (Nygard, 2011).** One short record per architecturally significant decision (structure, non-functional characteristics, dependencies, interfaces, construction techniques). Sections: Title, Context, Decision ("We will …"), Status (proposed, accepted, deprecated, superseded), Consequences (good, bad and neutral). Stored in the repo, numbered sequentially, numbers never reused; a reversed decision is kept and marked superseded; one or two pages; full sentences. [source: cognitect.com/blog/2011/11/15/documenting-architecture-decisions]
- **MADR 4.0.0.** Folder `docs/decisions`, file `NNNN-title-with-dashes.md`. Required: title, Context and Problem Statement, Considered Options, Decision Outcome; optional: Decision Drivers, Consequences, Confirmation, Pros and Cons of the Options, More Information. Licence MIT OR CC0-1.0. [source: adr.github.io/madr/; raw.githubusercontent.com/adr/madr/4.0.0/template/adr-template-minimal.md] MADR adds what Nygard's format lacks: the options that lost.
- **Lifecycle (AWS guidance).** Proposed → Accepted or Rejected (record why) → Superseded. An accepted ADR is immutable; a new insight means a new ADR that supersedes the old one. Review meeting starts with 10-15 minutes of silent reading. Reviewers cite ADRs in code review. [source: docs.aws.amazon.com/zh_cn/prescriptive-guidance/latest/architectural-decision-records/adr-process.html] adr.github.io notes ADR can be read as "any decision record". [source: adr.github.io]
- **Design doc (Google, Malte Ubl).** Written before coding for work whose solution is not obvious. Sections: Context and scope; Goals and non-goals; the design (overview first, trade-offs, system-context diagram, APIs, data storage; little code); Alternatives considered; Cross-cutting concerns (security, privacy, observability). 10-20 pages for a large design, 1-3 pages for a "mini design doc". Do not write one when the solution is unambiguous or the doc would be an implementation manual. Lifecycle: draft and iterate → review → implement and update → revisit later. [source: industrialempathy.com/posts/design-docs-at-google/] **RFC** is the same idea with a public comment period; the Rust template: Summary, Motivation, Guide-level explanation, Reference-level explanation, Drawbacks, Rationale and alternatives, Prior art, Unresolved questions, Future possibilities. [source: raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md]
- **Design doc vs ADR:** design doc = thinking before a piece of work (several decisions, may be updated); ADR = one decision, frozen once accepted. For a solo project: mini design doc for anything over about three days or touching data correctness; ADR whenever a choice would be expensive to reverse (data source, storage format, backtest conventions, dependency manager).
- **README.** GitHub: what the project does, why it is useful, how to get started, where to get help, who maintains it; searched in `.github/`, root, `docs/`; content beyond 500 KiB is truncated; use relative links. [source: docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes] Standard Readme required sections: Title, Short Description (<120 chars), Table of Contents (if ≥100 lines), Install, Usage, Contributing, License (last); one non-English README needs no language tag. [source: raw.githubusercontent.com/RichardLitt/standard-readme/main/spec.md] Make a README adds Badges, Visuals, Support, Roadmap, Project status. [source: makeareadme.com]
- **CONTRIBUTING / CODE_OF_CONDUCT / LICENSE / SECURITY.** Open Source Guides: every public project needs LICENSE, README, CONTRIBUTING (how to report bugs, propose features, set up and run tests), CODE_OF_CONDUCT (and be ready to enforce it). [source: opensource.guide/starting-a-project/] SECURITY.md states supported versions and how to report a vulnerability; private vulnerability reporting (public repos): Settings → Advanced Security → Private vulnerability reporting → Enable. [source: docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository; .../configuring-private-vulnerability-reporting-for-a-repository] Contributor Covenant 3.0: fill in the reporting contact and adapt the enforcement ladder (Warning → Temporarily Limited Activities → Temporary Suspension → Permanent Ban); CC BY-SA 4.0. [source: contributor-covenant.org/version/3/0/code_of_conduct/]
- **Licence choice.** No licence means default copyright: others may only view and fork under GitHub's terms. Simple and permissive → MIT; share-alike → GPLv3; otherwise follow your community. [source: choosealicense.com; choosealicense.com/no-permission/] File at repo root (the docs name `LICENSE.txt`, `LICENSE.md`, `LICENSE.rst`; a bare `LICENSE` is the usual convention [memory]), detected by Licensee. [source: docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository] MulanPSL-2.0 (木兰宽松许可证) is OSI-approved, bilingual, Chinese text prevails. [source: opensource.org/license/mulanpsl-2-0] **For a private personal project:** no licence file is needed while private; decide before making it public, and check that market data and vendor code may be redistributed at all [memory].
- **Docs as code.** Docs live in version control, in plain-text markup, go through review and automated checks, and are tracked with issues. [source: writethedocs.org/guide/docs-as-code/] Google: give docs owners, review them like code, record a freshness date, delete or mark stale docs; answer WHO / WHAT / WHEN / WHERE / WHY at the top. [source: abseil.io/resources/swe-book/html/ch10.html]
- **Diátaxis.** Four kinds by user need: tutorial (learning, doing under guidance), how-to guide (a competent user reaching a goal), reference (facts, structured like the product), explanation (background and why). Two axes: action vs cognition, acquisition (study) vs application (work). Adopt it one small improvement at a time; do not restructure top-down. [source: diataxis.fr/start-here/] Common Chinese renderings 教程 / 操作指南 / 参考 / 解释说明 are [memory]; no official Chinese translation was verified.

### D. Quality and risk management

- **Technical debt (Cunningham's metaphor, Fowler's wording).** Cruft makes change harder; the extra effort per change is the interest; cleaning up is paying principal. Pay it down gradually and mostly in code you change often; crufty but stable code can wait. Quadrant: deliberate or inadvertent × prudent or reckless; prudent-inadvertent debt ("now we know how we should have built it") is unavoidable. [source: martinfowler.com/bliki/TechnicalDebt.html; martinfowler.com/bliki/TechnicalDebtQuadrant.html] Register = T10. Tool hook: ruff rules `TD002` / `TD003` demand an author and an issue link on every TODO, `FIX001` / `FIX002` list FIXME / TODO lines. [local]
- **Risk register.** NIST: risk is a function of the adverse impact if an event occurs and the likelihood that it occurs. [source: csrc.nist.gov/glossary/term/risk] The 1-5 × 1-5 scoring grid and the four responses (avoid, transfer, mitigate, accept) are standard project-management practice [memory]. Data-project rows worth seeding: data-vendor change, look-ahead bias, single maintainer, laptop loss with no off-machine remote, breaking upgrade of pandas / numpy, leaked API key.
- **Dependency and upgrade policy.** uv: `uv run` / `uv sync` re-lock automatically after you edit `pyproject.toml`, but locked versions move to newer upstream releases only when you ask; `uv lock --check` fails if `uv.lock` and `pyproject.toml` disagree; `uv lock --upgrade` (all) and `uv lock --upgrade-package <pkg>` (one) stay within the constraints in `pyproject.toml`. [source: docs.astral.sh/uv/concepts/projects/sync/] Present in `--help` here: `uv tree --outdated`, `uv lock --exclude-newer`, `uv audit`. [local] SPEC 0: support Python versions for 3 years and core scientific packages for 2 years after release. [source: scientific-python.org/specs/spec-0000/] Bots: Dependabot `package-ecosystem: "uv"` with `cooldown: default-days: 7`; Renovate detects `uv.lock` (`lockFileMaintenance`). [source: docs.astral.sh/uv/guides/integration/dependabot/; docs.astral.sh/uv/guides/integration/renovate/] **Policy to teach:** commit `uv.lock`; upgrade on a calendar (monthly) in a dedicated branch, run tests, note it in the changelog only if users are affected; upgrade one package immediately for a security fix; never upgrade in the same change as a feature.
- **Versioning.** SemVer 2.0.0: MAJOR incompatible, MINOR compatible feature, PATCH compatible fix; `0.y.z` means anything may change; deprecate in a minor release before removing in a major; never modify a released version, release a new one. [source: semver.org] CalVer suits projects with a broad or time-driven scope and must be paired with a changelog. [source: calver.org] Note for Chinese teams: the Alibaba manual uses the same three names (主版本号.次版本号.修订号) but requires starting at 1.0.0 and tolerates tiny incompatible changes in a minor version, which differs from SemVer. [source: Alibaba 黄山版 PDF, 工程结构 (二) 第 2 条]
- **Release and change management.** Google SRE: reproducible (hermetic) builds from a known revision with pinned tools; fixes go to mainline first and are cherry-picked onto the release branch; keep an auditable list of what a release contains. [source: sre.google/sre-book/release-engineering/] DORA: heavyweight external approval (change advisory board) slows delivery and does not lower change-fail rate; peer review inside the normal workflow plus automated tests works better. [source: dora.dev/capabilities/streamlining-change-approval/] For one person: a PR to yourself + `make dod` + the release checklist (T8) is the change-approval process.
- **Rollback options, cheapest first:** (1) turn a feature flag off; (2) `git revert <sha>` (new commit, history intact); (3) run the previous tag (`git switch --detach vX.Y.Z && uv sync --locked`); (4) for a package on PyPI, yank the release: installers skip it unless pinned with `==`. [local for 1-3; source: docs.pypi.org/project-management/yanking/]
- **Hotfix flow.** If `main` is releasable: fix on `main`, bump PATCH, tag. If `main` holds unreleased work: branch from the release tag, fix, bump PATCH, tag, merge back (expect a CHANGELOG conflict; §7). Larger teams avoid that conflict with changelog fragments (towncrier 26.9.0). [local; source: towncrier.readthedocs.io/en/stable/]
- **Feature flags (Hodgson).** Four kinds: release (days to weeks), experiment, ops (kill switch), permission. Flags are inventory with a carrying cost: add the removal task when you add the flag, give it an expiry ("time bomb"), keep the decision in one named function, default to old behaviour, test the production configuration and the all-off fallback. Configuration grows from hard-coded → environment variable or CLI → config file → database. [source: martinfowler.com/articles/feature-toggles.html] Beginner level = one env-var boolean plus an inventory file (§7).
- **Incident response (awareness).** Declare an incident early if a second team is needed, users can see it, or it is unsolved after an hour; separate roles (incident command, operations, communication, planning); one live incident document; priorities: stop the bleeding, restore service, preserve evidence. [source: sre.google/sre-book/managing-incidents/] Severity ladders exist (PagerDuty SEV-1 … SEV-5; when unsure pick the higher). [source: docs.pagerduty.com/ops-guides/incident-response-guide/severity-levels] Chinese teams commonly say 故障等级 P0-P4 [memory]. Solo data-project version: S1 = wrong numbers were used for a decision, data lost, or a secret leaked; S2 = pipeline down or late; S3 = cosmetic.
- **Blameless postmortem.** A written record of impact, mitigation, root causes and follow-ups; triggers defined in advance (user-visible outage, data loss, manual intervention, slow resolution, monitoring miss); assume good faith and fix systems, not people; review it (an unreviewed postmortem might as well not exist) and share it. Example structure: Summary, Impact, Root Causes, Trigger, Resolution, Detection, Action Items (type: mitigate / prevent / process / other; owner; bug), Lessons Learned (went well / went wrong / got lucky), Timeline in UTC. [source: sre.google/sre-book/postmortem-culture/; sre.google/sre-book/example-postmortem/] Workbook: quantify impact, neutral language, each action item has one owner, a priority, a tracking issue and a verifiable end state; prefer prevention built into the system over "be more careful"; publish within about a week. [source: sre.google/workbook/postmortem-culture/] PagerDuty's template names the cause section "Contributing Factors". [source: docs.pagerduty.com/ops-guides/incident-response-guide/postmortem-template]
- **5 Whys and its critiques.** Allspaw (2014): it assumes one linear causal chain, the result depends on who asks, "why" drifts to "who", it tends to stop at human error, and it implies a single root cause; ask "how" and collect several contributing conditions instead. [source: kitchensoap.com/2014/11/14/the-infinite-hows-or-the-dangers-of-the-five-whys/] Card, "The problem with '5 whys'", BMJ Qual Saf 2017;26(8):671-677 makes the same case in healthcare [citation via search; text not read]. Chinese practice still names 5 Why explicitly and pairs 复盘 with 定级定责 (grading and assigning responsibility); action items must be SMART, have an owner, an acceptor and a deadline of at most three months. [source: help.aliyun.com/zh/document_detail/2573892.html] **Teach:** 5 Whys as a first drill, then immediately ask "what else had to be true?" at each level so the chain becomes a tree; state the cultural difference between blameless and 定责 honestly.
- **On-call (awareness only).** Being reachable for production problems; response targets follow the service's availability target (about 5 minutes for user-facing, 30 for less urgent); primary and secondary rotation; at most 50% of time on operations and 25% on-call; playbooks reduce stress errors. [source: sre.google/sre-book/being-on-call/] Solo equivalent: a `docs/runbook.md` for any scheduled job.

### E. Team norms

- **RACI.** Responsible does the work (one or more); Accountable owns the result and signs off (exactly one per task); Consulted gives input before; Informed is told after. Check each row for no R, no A or several A. [source (secondary): cio.com/article/287088/project-management-what-is-raci-and-how-does-it-improve-clarity.html] **Angle for this learner:** when pairing with an AI assistant, the assistant can be R or C; the human is always the single A.
- **Code ownership.** `CODEOWNERS` in `.github/`, root or `docs/` on the base branch; `pattern owner…` per line; the **last** matching pattern wins; owners need write access; gitignore-like but no `!` negation and no `[ ]` ranges; under 3 MB; enforcement needs "Require review from Code Owners" in branch protection or a ruleset. [source: docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners]
- **Review turnaround.** Google: respond within one business day at most; response time matters more than total time; do not interrupt focused work, answer at the next break; approve with minor comments when you trust the author; ask to split large changes. [source: google.github.io/eng-practices/review/reviewer/speed.html]
- **Bus factor.** Number of people who must disappear before the project is doomed; raise it with documentation, working together, and a primary plus secondary owner per area. A good postmortem per the same chapter: summary, timeline, primary cause, impact, action items with owners, prevention items, lessons. [source: abseil.io/resources/swe-book/html/ch02.html] A solo project has bus factor 1; documents, ADRs and an off-machine Git remote are the mitigation.
- **Meeting notes and decision log.** Agenda before, notes during, decisions and action items (owner, date) at the top, stored next to the code (`docs/meetings/2026-11-19-topic.md`); decisions that matter become ADRs [memory; GitLab handbook not readable today].
- **Onboarding.** README quick start that works on a clean clone, CONTRIBUTING with setup / test / conventions, a first-day checklist. For a solo developer the "new hire" is yourself in six months [memory].
- **Closing keywords** link PRs and commits to issues: `close(s|d)`, `fix(es|ed)`, `resolve(s|d)` + `#N`; they only act on the default branch. [source: docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue]

## 4. Chinese terminology (use the first form in lessons; show the English once)

| English | 中文说法 | Basis |
|---|---|---|
| requirement / user story | 需求；用户故事（TAPD 文档直接写“需求 = User Story”；微软文档译“用户情景”） | [source: cloud.tencent.com/document/product/624/44285; learn.microsoft.com/zh-cn/azure/devops/boards/boards/kanban-overview] |
| acceptance criteria | 验收标准 | [source: Aliyun 复盘文档 uses 验收标准 / 验收人]; as a story term [memory] |
| Definition of Done / Ready | 完成的定义（DoD）；就绪的定义（DoR） | 完成的定义 [source: Azure zh-CN]; 官方中文 Scrum 指南保留英文 Definition of Done [source: Scrum zh PDF]; DoR [memory] |
| epic / task / bug | 史诗（微软亦作“长篇故事”）；任务；缺陷 / Bug | [source: Azure zh-CN; TAPD] |
| chore | 杂务 / 日常维护（多直接说 chore） | [memory] |
| backlog | 待办列表 / 需求池（微软译“积压工作”；官方 Scrum 指南保留 Product Backlog） | [source: Azure zh-CN; Scrum zh PDF] |
| sprint / iteration / timebox | 迭代（TAPD）/ 冲刺（微软）/ Sprint（官方指南保留英文）；时间盒 | [source: TAPD; Azure; Scrum zh PDF] |
| refinement; stakeholder | 精化（口语：需求梳理）；利益攸关者 / 干系人 | 精化、利益攸关者 [source: Scrum zh PDF]; 梳理、干系人 [memory] |
| Kanban board; WIP limit; swimlane | 看板；在制品限制 / WIP 限制；泳道 | 看板、泳道、WIP 限制 [source: Azure zh-CN]; 在制品 [memory] |
| cycle time; lead time; throughput | 周期时间；前置时间 / 交付周期；吞吐量 | [source: Azure zh-CN]; 吞吐量 [memory] |
| stand-up; burndown chart | 站会；燃尽图 | [source: TAPD] |
| issue; pull request; label; milestone; repository | 议题（也见“问题”，口语直接说 issue）；拉取请求 / PR（GitLab、Gitee 叫合并请求 MR）；标签；里程碑；存储库 / 仓库 | [source: docs.github.com/zh/issues/tracking-your-work-with-issues/learning-about-issues/about-issues]; MR、仓库 [memory] |
| roadmap; priority; estimate | 路线图；优先级；估算 / 工作量评估 | [source: Azure zh-CN; TAPD] |
| changelog; release notes | 更新日志（Keep a Changelog 中文版用词）/ 变更日志；发布说明 | [source: keepachangelog.com/zh-CN/1.1.0/]; 发布说明 [memory] |
| Added / Changed / Deprecated / Removed / Fixed / Security | 新增 / 变更 / 已弃用 / 已移除 / 已修复 / 安全 | [source: keepachangelog.com/zh-CN/1.1.0/] |
| Semantic Versioning | 语义化版本：主版本号.次版本号.修订号；先行版本号；向下兼容 | [source: semver.org/lang/zh-CN/] |
| Conventional Commits; code of conduct | 约定式提交；行为准则（Contributor Covenant = 贡献者公约） | [source: conventionalcommits.org/zh-hans/v1.0.0/; contributor-covenant.org/zh-cn/version/3/0/code_of_conduct/] |
| release; rollback; hotfix; gradual rollout | 发布 / 发版 / 上线；回滚；热修复 / 紧急修复；灰度发布 | 回滚 appears in Alibaba 手册; others [memory] |
| feature flag | 功能开关 / 特性开关 | [memory] |
| ADR; design doc; design review | 架构决策记录；设计文档 / 技术方案；设计评审 | [source: docs.aws.amazon.com/zh_cn/prescriptive-guidance/latest/architectural-decision-records/adr-process.html; Alibaba 手册 设计规约] |
| proposed / accepted / rejected / superseded | 已提议 / 已接受 / 已拒绝 / 已取代 | [source: AWS zh_cn ADR 流程] |
| postmortem; retrospective; action item | 复盘（故障复盘）；回顾会；改进措施 / Action | [source: help.aliyun.com/zh/document_detail/2573892.html]; 回顾会 [memory] |
| blameless; root cause; incident; severity; on-call | 对事不对人 / 无指责；根因；故障 / 事故；故障等级；值班 | 故障等级 [source: Aliyun]; others [memory] |
| technical debt; risk register | 技术债 / 技术债务；风险登记册 / 风险清单 | [memory] |
| code review; code owner; RACI; bus factor | 代码评审 / 代码审查（CR）；代码所有者 / 负责人；RACI 矩阵（负责 / 拍板问责 / 咨询 / 知会）；巴士因子 | 代码审查 [source: AWS zh_cn]; others [memory] |
| reproduce; symptom; diagnosis | 重现 / 复现；症状；诊断 | [source: chiark.greenend.org.uk/~sgtatham/bugs-cn.html] |
| tutorial / how-to / reference / explanation; docs as code | 教程 / 操作指南 / 参考 / 解释说明；文档即代码 | [memory] |
| team idioms | 需求评审、排期、提测、验收、上线、沉淀（把经验写成文档） | 沉淀、评审 [source: Alibaba 手册]; others [memory] |

Finding worth telling the learner: the **official** Chinese Scrum Guide leaves Sprint, Product Backlog, Increment, Developers and Definition of Done in English and translates only general words (工件, 事件, 时间盒, 精化, 承诺, 透明, 检视, 适应). Mixed Chinese-English speech ("这个 story 的 DoD 是什么") is normal in Chinese teams. [local grep of the extracted PDF]

## 5. How "规范 / 规约" documents are written in Chinese teams (verified on the Alibaba manual)

Verified from《Java 开发手册（黄山版）》1.7.1, 2022-02-03, 55 pages, Apache-2.0 repository [source: raw.githubusercontent.com/alibaba/p3c/master/Java开发手册(黄山版).pdf, text extracted locally to `$S/extracted/alibaba-java-manual-huangshan.txt`]:

- **Three binding levels**, ordered by constraint strength and by how fault-sensitive the rule is: 【强制】 【推荐】 【参考】. Occurrences in the text: 193 / 97 / 37, so roughly 6 : 3 : 1. [local count; includes the preface's own mention]
- **Rule anatomy:** a number, a level tag, one imperative sentence; then optional 说明 (extends and explains), 正例 (the way to do it), 反例 (the trap, often a real incident). Counts: 说明 192, 正例 94, 反例 66. Many rules carry a number threshold (for example "more than 3 states → draw a state diagram"), which makes them checkable.
- **Document anatomy:** 前言 (why, scope, how to read) → seven dimensions (编程规约, 异常日志, 单元测试, 安全规约, MySQL 数据库, 工程结构, 设计规约) with numbered sub-sections → 附 1 版本历史 (version, date, edition name, what changed) → 附 2 专有名词解释 → 附 3 错误码列表. Editions have memorable names (华山版, 泰山版, 嵩山版, 黄山版).
- **Tone and argument:** the preface justifies rules with a traffic-law analogy (rules limit individual freedom to protect everyone and lower collaboration cost) and the idiom 无规矩不成方圆. Rules that can be machine-checked ship as an IDE plugin and PMD rules. [source: github.com/alibaba/p3c]
- **Management-relevant rules inside it** (useful quotes to paraphrase in lessons): storage and data-structure designs must pass review and be written down (设计规约 1, 强制); "agile = stories + coding + release" is called a misunderstanding, key designs and documents are still required (15, 推荐); a design document exists to clarify requirements, straighten logic and support later maintenance (16, 参考); "code is the documentation" is called wrong (19, 参考); unit tests follow AIR (Automatic, Independent, Repeatable) (单元测试 1, 强制).
- **International equivalents:** RFC 2119 MUST / SHOULD / MAY, to be used sparingly. [source: rfc-editor.org/rfc/rfc2119] Chinese national-standard wording 应 / 宜 / 可 (GB/T 1.1) is [memory].
- **Chinese writing norms for the documents themselves:** ruanyf《中文技术文档的写作规范》(structure: 简介, 快速上手, 入门篇, 进阶篇, API, FAQ, 附录; file names lowercase, half-width, hyphen-separated, no spaces or Chinese) and《中文文案排版指北》(space between Chinese and Latin letters or digits, full-width punctuation in Chinese sentences, correct capitalisation such as GitHub). [source: github.com/ruanyf/document-style-guide; github.com/sparanoid/chinese-copywriting-guidelines]

**Recommendation:** have the learner write `docs/规范.md` (or `docs/engineering-rules.md`) for their own project in exactly this format: 10-15 rules to start, about 6 强制 (each one machine-checkable or checklist-checkable), each with one 说明 and a 正例 / 反例 taken from their own repository, plus a 版本历史 table. Rule format is template T11.

## 6. Recommended defaults (opinionated; every item is small enough for one lesson)

| Area | Default | Why |
|---|---|---|
| Work items | GitHub Issues with two YAML forms (bug, feature); labels = GitHub defaults | forms validated locally; zero setup |
| Size rule | split anything over about 2 days; no story points | Jeffries; Kanban SLE |
| Board | 4 columns, Doing ≤ 2, Ready ≤ 5 | Kanban Guide minimum; Personal Kanban |
| Cadence | weekly review, same slot, 30-45 min, 5-line note in `docs/weekly/` | replaces Sprint events |
| DoD | T4, enforced by `make dod` + PR template | visible and mostly automatic |
| Versioning | SemVer, start at `0.1.0`, tags `vX.Y.Z` (annotated) | uv default version is 0.1.0 [local] |
| Changelog | Keep a Changelog 1.1.0, hand-written, updated in the same change | humans read it |
| Decisions | `docs/adr/NNNN-slug.md`, MADR-minimal + status / date front matter | adds "options considered" to Nygard |
| Design | mini design doc (1-3 pages) only for > 3 days or correctness-critical work | Google heuristic |
| Docs layout | README (quick start) + `docs/` growing toward Diátaxis | iterate, do not restructure |
| Debt and risk | two Markdown tables, reviewed first week of each month | cheap, visible |
| Dependencies | commit `uv.lock`; monthly `uv lock --upgrade` branch; `uv audit` before release | uv docs; [local] |
| Incidents | 3 severities; postmortem (T7) for every S1 | SRE triggers, scaled down |
| Licence | none while private; MIT (or MulanPSL-2.0) when published | choosealicense |

## 7. Local experiments (all [local], run 2026-11-19; uv needs `export UV_CACHE_DIR="$TMPDIR/uv-cache"` in this sandbox)

Everything below lives in `$S/sandbox/demo-fx/` (a throwaway uv project with 10 commits and 3 tags). Helper scripts are standard-library only: `scripts/new_adr.py`, `scripts/changelog.py`, `scripts/check_flags.py`, `scripts/check_issue_forms.rb`, `scripts/weekly_review.sh`.

**7.1 Project and repo** — `uv init --app --vcs none --no-readme --name demo-fx demo-fx` produced `src/demo_fx/__init__.py`, `.python-version` (3.12 here) and a `pyproject.toml` with `[project.scripts]` and `build-backend = "uv_build"`; `authors` was filled from the global Git identity (pass `--author-from none` to avoid that). `uv lock --offline && uv sync --offline` worked with no network. Then `git init -b main` and repo-local `git config --local user.name / user.email`.

**7.2 Issue forms checked offline** — `/usr/bin/ruby scripts/check_issue_forms.rb` (system Ruby 2.6.10, stdlib YAML; rules copied from the GitHub validation-error page):
```
ok  .github/ISSUE_TEMPLATE/bug_report.yml (9 fields, 5 required)
ok  .github/ISSUE_TEMPLATE/config.yml (template chooser config)
ok  .github/ISSUE_TEMPLATE/feature_request.yml (5 fields, 3 required)
ok  .github/release.yml (valid YAML)
ok  .github/dependabot.yml (valid YAML)
```
Limit: GitHub's own server-side validation was not exercised (nothing was pushed).

**7.3 ADR numbering** — `python3 scripts/new_adr.py use-uv-for-dependencies "用 uv 管理依赖和虚拟环境"` → `created docs/adr/0002-use-uv-for-dependencies.md` (next number = highest existing + 1, date filled, status `proposed`).

**7.4 Feature flag** (one env-var boolean, one decision point, default = old behaviour):
```
$ uv run demo-fx                                → signal v1 (default): +0.0800
$ DEMO_FX_FF_NEW_SIGNAL=1 uv run demo-fx     → signal v2 (flag on): +0.0100
$ python3 scripts/check_flags.py 2027-01-15     → EXPIRED  new_signal   owner=demo-learner expires=2026-12-31   (exit 1)
```
`flags.toml` holds `owner`, `reason`, `issue`, `expires` per flag; the check is the "time bomb".

**7.5 Release** —
```
$ uv version --bump minor --dry-run     → demo-fx 0.1.0 => 0.2.0
$ uv version --bump minor               → rewrites pyproject.toml, re-locks, re-installs 0.2.0
$ python3 scripts/changelog.py release 0.2.0   → [Unreleased] becomes "## [0.2.0] - 2026-11-19", link refs updated
$ git add -A && git commit -m "chore(release): 0.2.0" && git tag -a v0.2.0 -m "demo-fx 0.2.0"
$ python3 scripts/changelog.py show 0.2.0      → prints that version's section = text for the release notes
$ git log --oneline v0.1.0..v0.2.0             → the commits in this release
```
`uv version --bump` accepts `major, minor, patch, stable, alpha, beta, rc, post, dev`; `uv version --short` prints just the number.

**7.6 DoD as one command** — `Makefile` target `dod: lint format-check lock-check changelog-check`, run with `/Library/Developer/CommandLineTools/usr/bin/make dod`:
```
ruff check .            → All checks passed!
ruff format --check .   → 9 files already formatted
uv lock --check         → Resolved 1 package in 1ms
changelog: [Unreleased] section present
DoD: all automatic checks passed
```
Failure case (a dependency added to `pyproject.toml` without re-locking): `error: The lockfile at uv.lock needs to be updated, but --check was provided.` → `make: *** [lock-check] Error 1`. pytest and a type checker are not installed here, so those two DoD lines were not run.

**7.7 Hotfix on a released tag** — `git switch -c hotfix/0.2.1 v0.2.0` → fix → `uv version --bump patch` → `changelog.py release 0.2.1` → commit → `git tag -a v0.2.1` → `git switch main && git merge --no-ff hotfix/0.2.1`. Result: `CONFLICT (content): Merge conflict in CHANGELOG.md` because `main` had added an Unreleased entry in the same place. Resolved by keeping both blocks (Unreleased entry above, `[0.2.1]` section below). Graph afterwards:
```
*   5a29c2d merge: hotfix 0.2.1 back into main
|\
| * edb888b (tag: v0.2.1, hotfix/0.2.1) fix: clear error for too-short price series
* | 341b41e feat: add spread helper
|/
* 7268cbf (tag: v0.2.0) chore(release): 0.2.0
```

**7.8 Rollback** — `git revert --no-edit 341b41e` also conflicted in CHANGELOG.md (fix the file, `git add`, `git revert --continue`); while a revert is in progress `git switch` refuses ("cannot switch branch while reverting"). Running the old release: `git switch --detach v0.2.0 && uv sync --locked && uv run demo-fx` printed the 0.2.0 behaviour and `uv version --short` → `0.2.0`; `git switch main && uv sync --locked` returned to `0.2.1`.

**7.9 Debt markers** — `ruff check --isolated --select FIX,TD --output-format concise example.py`:
```
example.py:2:7: TD002 Missing author in TODO; try: `# TODO(<author_name>): ...` or `# TODO @<author_name>: ...`
example.py:2:7: TD003 Missing issue link for this TODO
example.py:3:7: FIX001 Line contains FIXME, consider resolving the issue
```
A TODO written as `# TODO(name): text` followed by a line with an issue URL passes TD002 / TD003 (only FIX002 remains).

**7.10 Review raw material** — `git log --since="7 days ago" --no-merges --pretty="%h %ad %s" --date=short`; `git tag -l --sort=-v:refname`; `git diff --shortstat v0.1.0..HEAD` → `8 files changed, 128 insertions(+), 10 deletions(-)`; `git shortlog -sn --no-merges HEAD` and `git log --format="%an" -- src/ | sort | uniq -c` (who knows which part).

**7.11 Dependency audit** — `uv audit --frozen` (needs network to the OSV service; refuses `--offline`): `warning: uv audit is experimental and may change without warning.` then `Found no known vulnerabilities and no adverse project statuses in 0 packages`.

**7.12 Config snippets that parsed and are ready to paste** (full files in the sandbox):
```yaml
# .github/ISSUE_TEMPLATE/config.yml
blank_issues_enabled: false
contact_links:
  - name: "使用问题 / 讨论"
    url: https://example.com/demo/demo-fx/discussions
    about: "不确定是不是 bug？先来这里问。"
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule: { interval: "weekly" }
    cooldown: { default-days: 7 }
# .github/release.yml
changelog:
  categories:
    - { title: "新增 Added", labels: ["enhancement"] }
    - { title: "修复 Fixed", labels: ["bug"] }
    - { title: "其他 Other", labels: ["*"] }
```
```text
# .github/CODEOWNERS — pattern then owners; the LAST matching line wins
*                       @demo-learner
/src/demo_fx/risk/   @demo-learner @demo-reviewer
```
```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml — compact variant, parsed and rule-checked here (7 fields, 5 required)
name: "缺陷报告 (Bug report)"
description: "程序的实际行为与预期不一致"
title: "[Bug]: "
labels: ["bug"]
body:
  - type: textarea
    id: what-happened
    attributes: { label: "发生了什么（实际结果）", description: "只写看到的现象；报错信息原样粘贴。" }
    validations: { required: true }
  - type: textarea
    id: expected
    attributes: { label: "预期结果" }
    validations: { required: true }
  - type: textarea
    id: steps
    attributes: { label: "复现步骤（最小可复现示例）", value: "1. \n2. \n3. " }
    validations: { required: true }
  - type: textarea
    id: logs
    attributes: { label: "完整报错 / 日志", render: shell }
  - type: input
    id: version
    attributes: { label: "版本 / 提交号", description: "`uv version --short` 或 `git rev-parse --short HEAD` 的输出" }
    validations: { required: true }
  - type: dropdown
    id: severity
    attributes: { label: "影响程度", options: ["结果错误（数字不可信）", "程序崩溃 / 无法运行", "功能可用但不方便", "文字 / 外观问题"] }
    validations: { required: true }
  - type: checkboxes
    id: checks
    attributes: { label: "提交前自查", options: [{ label: "我已搜索过现有 issue，没有重复", required: true }] }
```
```make
# Makefile (recipe lines start with a TAB). Works with the GNU Make 3.81 on this machine.
DOD_CHECKS = lint format-check lock-check changelog-check
.PHONY: dod $(DOD_CHECKS)
dod: $(DOD_CHECKS)
	@echo "DoD: all automatic checks passed"
lint:
	ruff check .
format-check:
	ruff format --check .
lock-check:
	uv lock --check
changelog-check:
	@python3 scripts/changelog.py show Unreleased > /dev/null && echo "changelog: [Unreleased] section present"
```
```python
# Feature flag at beginner level: one helper, one decision point, unset = old behaviour.
def flag_enabled(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get("DEMO_FX_FF_" + name.upper())
    return default if raw is None else raw.strip().lower() in {"1", "true", "yes", "on"}

def signal(prices: list[float]) -> float:
    return _signal_v2(prices) if flag_enabled("new_signal") else _signal_v1(prices)
```

Side observations for other agents [local]: ruff 0.17.2 with no configuration (`--isolated`) reported `FURB167` on `re.S`, so its default rule set is wider than the old E / F defaults; `ruff format --check .` counted the repository's Markdown files as well as the `.py` files (verbose log shows `README.md`, `CHANGELOG.md`, ADRs as included paths); `uv run`, `uv version --bump` and `uv sync` re-lock and re-install silently, which surprises beginners.

## 8. Templates (Chinese, ready to adapt; T1 / T2 also exist as validated YAML forms in the sandbox)

**T1 需求 / 用户故事 issue**
```markdown
标题：<动词开头，说清结果>，例：支持按月输出回测收益率
## 问题陈述（为什么要做）
谁、在什么场景、遇到什么麻烦；现在怎么凑合。先写问题，不写方案。
## 用户故事
作为 <角色>，我想要 <做到什么>，以便 <得到什么价值>。
## 验收标准（每条都能写成一个测试）
- [ ] 假如 <前置条件>，当 <动作>，那么 <可观察的结果>
## 不做什么（范围之外）
## 备注
优先级：Must / Should / Could / Won't（这次不做）　预计大小：≤2 天（否则先拆分）　依赖：数据 / 密钥 / 他人
```

**T2 缺陷报告**
```markdown
标题：[Bug] <现象>，例：[Bug] 2020-02 的月收益率为 NaN
## 实际结果（只写看到的现象，报错原样粘贴）
## 预期结果
## 复现步骤（最小可复现示例：最少的数据 + 确切的命令）
1.
## 环境
版本 / 提交号（uv version --short；git rev-parse --short HEAD）；系统；Python；uv
## 影响程度
结果错误（数字不可信）/ 崩溃无法运行 / 可用但不方便 / 文字外观
## 我的猜测（可选，和上面的“症状”分开写）
```

**T3 用户故事 + 验收标准（回测示例）**
```markdown
作为每月复盘策略的研究者，我想要一条命令重新生成回测结果，以便确认结论不是某次手工操作的偶然产物。
- [ ] 假如 data/ 下有 2015-01 至 2024-12 的日收盘价（含 3 个缺失交易日），当运行 `uv run demo-fx backtest`，那么输出 120 行月度收益率且没有 NaN
- [ ] 假如随机种子固定，当连续运行两次，那么两次输出逐字节相同
- [ ] 假如把数据截到 2019-12，当重新运行，那么 2019-12 及之前各月的数值不变（没有用到未来数据）
INVEST 自查：独立 / 可协商 / 有价值 / 可估算 / 足够小 / 可测试
```

**T4 完成的定义（DoD），小型 Python / 数据分析项目**
```markdown
【强制】
- [ ] 该条目的验收标准全部满足，并且每条都有对应测试；修 bug 先写出能复现它的失败测试
- [ ] `uv run pytest` 全部通过
- [ ] `ruff check .` 与 `ruff format --check .` 通过
- [ ] `uv lock --check` 通过：依赖只通过 `uv add` 进入 pyproject.toml，uv.lock 已提交
- [ ] 结果可复现：随机种子固定；数据来源、日期范围、版本写在文档或输出里；已自查没有用到未来数据
- [ ] 仓库里没有密钥、账号、未经许可的原始数据
- [ ] 用户能感知的变化已写进 CHANGELOG.md 的 [Unreleased]
- [ ] 提交说明写清“做了什么、为什么”，并关联 issue（Closes #N）
【推荐】
- [ ] 类型检查通过（`uv check` 或项目选定的工具）
- [ ] README / 文档同步；notebook 已“重启并全部运行”过
- [ ] 难以反悔的取舍已写成 ADR；新开的功能开关已登记负责人和到期日
- [ ] 自己逐行看过 diff；AI 助手写的每一行自己都能解释
【参考】
- [ ] 覆盖率、运行时间没有明显变差
```
其中能自动检查的几条（pytest、ruff、`uv lock --check`、更新日志是否有 [Unreleased]）可以收进一条命令 `make dod`；§7.6 实际跑通了除 pytest 以外的四项检查。

**T5 架构决策记录（ADR）** — 文件名 `docs/adr/NNNN-英文短横线标题.md`，编号递增、永不复用
```markdown
---
status: proposed        # proposed 已提议 | accepted 已接受 | rejected 已拒绝 | deprecated 已弃用 | superseded by ADR-NNNN 已被取代
date: YYYY-MM-DD
decision-makers: <谁拍板>
---
# NNNN. <问题 + 选择，一句话>
## 背景与问题（Context and Problem Statement）
当时的事实、约束、要回答的问题。两三句，中立地写。
## 考虑过的方案（Considered Options）
- 方案 A　- 方案 B　- 不做 / 维持现状
## 决定（Decision Outcome）
我们选择“方案 X”，因为……
### 后果（Consequences）
- 好处：　- 代价 / 风险：　- 出现什么信号时要重新审视：
```
规则：已接受的 ADR 不再改正文；想法变了就新写一篇，并把旧的 status 改成 `superseded by ADR-NNNN`。Nygard 原版只有 Title / Status / Context / Decision / Consequences 五段，可作为更短的备选。

**T6 迷你设计文档（1-3 页）** — `docs/design/YYYY-MM-标题.md`
```markdown
# <标题>　作者 / 日期 / 状态（草稿 → 评审中 → 已定稿 → 已实现）
## 1. 背景与范围：现在是什么情况，这次要做的是什么（不是需求清单）
## 2. 目标 / 非目标：非目标 = 有人可能以为要做、但这次明确不做的事
## 3. 方案：先给总览（一张图或五行字），再写关键取舍：数据从哪来、存成什么、对外接口长什么样
## 4. 考虑过的其他方案：各自的好处、代价、为什么没选
## 5. 横切关注点：数据正确性与可复现、安全与密钥、性能、可观测（日志）、回滚办法
## 6. 未决问题　## 7. 里程碑：拆成哪几个 ≤2 天的 issue
```
不用写的情况：做法没有悬念；或者写出来只是操作手册。

**T7 复盘 / 事后回顾（对事不对人）** — `docs/postmortems/YYYY-MM-DD-标题.md`
```markdown
# <事件标题>　日期 / 作者 / 状态（草稿 → 已评审 → 改进项全部关闭）　严重程度 S1 / S2 / S3
## 摘要：三句话，发生了什么、影响多大、现在是否已恢复
## 影响：用数字写（哪些结果错了、错了多久、谁用过这些结果、损失多少时间或钱）
## 时间线（写明时区）：引入 → 发生 → 发现 → 开始处理 → 止损 → 恢复
## 发现方式：怎么知道出事的？能不能更早知道？
## 触发因素与促成因素：不止一条；写“系统哪里允许了这件事发生”，不写“某人不小心”
## 处理与恢复：做了什么来止损和修复
## 做得好的 / 做得不好的 / 侥幸的
## 改进项
| 改进项 | 类型（止损 / 预防 / 发现 / 流程） | 负责人 | 截止日 | issue | 怎样算完成 |
```
写作规则：只写事实和当时的想法（“当时为什么觉得这样做是对的”）；改进项必须可验证，“以后小心”不算；一周内写完并找人（或让 AI 助手）评审。

**T8 发布检查清单（含回滚与热修复）**
```markdown
发布前
- [ ] main 上 `make dod` 通过；里程碑里的 issue 都已关闭或移走
- [ ] [Unreleased] 读起来是给用户看的话，不是提交记录
- [ ] 决定版本号：不兼容 → 主版本；新功能 → 次版本；只修 bug → 修订号（0.y.z 阶段可以放宽，但要写明）
- [ ] 回滚办法写下来了：上一个可用版本是 vA.B.C；需要回滚时执行什么
发布
- [ ] `uv version --bump <major|minor|patch>`
- [ ] 把 [Unreleased] 改成 `## [X.Y.Z] - YYYY-MM-DD`，更新底部链接
- [ ] `git add pyproject.toml uv.lock CHANGELOG.md && git commit -m "chore(release): X.Y.Z"`，`git tag -a vX.Y.Z -m "…"`，`git push --follow-tags`
- [ ] 在 GitHub 上从该 tag 建 Release，正文粘贴这一版的更新日志
发布后
- [ ] 在干净目录里按 README 从头装一遍、跑一遍
- [ ] 过期的功能开关已删除；下一个里程碑已建好
回滚（按代价从小到大）：关功能开关 → `git revert <提交>` → 切回上一个 tag 并 `uv sync --locked`
热修复：main 可发布就直接在 main 上修并发修订号；否则 `git switch -c hotfix/X.Y.Z vX.Y.(Z-1)` → 修 → 发版 → 合并回 main（CHANGELOG.md 大概率冲突：两段都保留）
```
（`git push --follow-tags` 与 GitHub Release 步骤未在本机执行；其余均已在 §7 跑通。）

**T9 每周回顾（30-45 分钟，固定时间）** — `docs/weekly/2026-W47.md`
```markdown
1. 清空（5 分钟）：脑子里、便签里、聊天记录里的想法和 TODO 全部变成 issue
2. 回看（10 分钟）：这周完成了什么（`git log --since="7 days ago"`、已关闭的 issue）；亲手跑一遍成果；
   看流动：进行中有几项、最老的一项卡了几天、这周完成了几项
3. 复盘（10 分钟）：一件顺利的事；一件别扭的事；下周只试一个小改进
4. 计划（10 分钟）：一句话的本周目标；从待办里挑 3-5 项放进“就绪”；看一眼里程碑日期
5. 每月第一周加做：技术债表、风险表、依赖升级（`uv lock --upgrade` 单独一个分支）
记录五行：本周目标是否达成 / 完成项数 / 最大的阻碍 / 下周目标 / 要试的一个改进
```

**T10 技术债登记表 + 风险登记表** — `docs/debt-register.md`、`docs/risk-register.md`
```markdown
| 编号 | 欠的是什么 | 在哪 | 怎么欠下的（有意 / 无意） | 利息（它让什么变慢、变危险） | 还清代价 | 何时必须还 | issue |
| D-003 | 收益率计算写死 252 个交易日 | src/…/vol.py | 有意，为赶第一版 | 换市场时结果会悄悄算错 | 小 | 接入第二个市场之前 | #12 |

| 编号 | 风险 | 可能性 1-5 | 影响 1-5 | 分值 | 应对（规避 / 转移 / 减轻 / 接受） | 预警信号 | 负责人 | 复查日 |
| R-002 | 数据源改接口或收费 | 3 | 4 | 12 | 减轻：原始数据本地留存，取数代码集中在一个模块 | 取数任务连续失败 | 我 | 每月 |
```
还债规则：改到哪里顺手还哪里；影响结果正确性的债立刻还；代码里的 TODO 必须写成 `# TODO(名字): 说明` 并在下一行附 issue 链接（ruff TD002 / TD003 可检查）。

**T11 规范条目格式（仿《Java 开发手册》）**
```markdown
3.【强制】依赖只能通过 `uv add` 加入，uv.lock 必须提交。
说明：只在本机 pip install 的包，别人和三个月后的自己都装不出同样的环境。
正例：`uv add pandas` 后提交 pyproject.toml 与 uv.lock。
反例：notebook 里 `!pip install xxx`，换电脑后回测结果对不上。
（文末附“版本历史”表：版本 / 日期 / 变更摘要）
```

**T12 个人看板的“工作流定义”** — 贴在看板说明里
```markdown
工作项：一个 issue = 一件 ≤2 天能做完、做完后看得出区别的事
列：待办 → 就绪（≤5）→ 进行中（≤2）→ 完成
进“就绪”：问题写清、有验收标准、不依赖还没到手的数据或权限
进“进行中”：进行中少于 2 项才能拉新的；被卡住就标“阻塞”并写原因，不另开新坑
进“完成”：满足完成的定义（DoD）
预期：大多数条目 5 天内完成；超过就拆分或在周回顾里讨论
```

## 9. Pitfalls a beginner will hit

1. Taking Scrum-flavoured vocabulary as "the standard" and adding points, velocity and ceremonies to a one-person project.
2. Writing the solution as the story ("加一个按钮"); writing acceptance criteria that cannot fail.
3. Bug reports that say "不能用了" or give a diagnosis without symptoms, versions or steps.
4. Confusing DoD (same for every item) with acceptance criteria (specific to one item); a DoD of 25 aspirational lines that nobody runs.
5. Starting many things: no WIP limit, or a board with seven columns.
6. Changelog pasted from `git log`; forgetting `[Unreleased]`; editing CHANGELOG.md on two branches (conflict shown in §7.7 and §7.8).
7. Editing an accepted ADR instead of superseding it; reusing numbers; writing ADRs for trivial, reversible choices.
8. Believing "public on GitHub" means open source; publishing without a licence; publishing data or keys.
9. GitHub mechanics: issue forms and closing keywords only work from the default branch; labels named in a form must exist; a column limit does not block; CODEOWNERS and branch protection are unavailable for private repos on the Free plan; generated release notes are empty without pull requests.
10. Feature flags that default to on, are tested in one state only, or are never removed.
11. Postmortems that end with "以后小心" or name a culprit; 5 Whys stopping at "人为失误"; action items without owner, date or done-criterion.
12. `git revert` versus rewriting history; a revert can conflict and blocks branch switching until finished or aborted.
13. Tagging without bumping the version or the changelog, or forgetting to push tags.
14. `uv init` writing your real name and e-mail into `pyproject.toml`.
15. Introducing all templates on day one, then abandoning them. One artifact per lesson, applied to the learner's own project (if any).
16. Chinese UI and doc translations differ by vendor (议题 / 问题, 拉取请求 / 合并请求, 迭代 / 冲刺, 用户故事 / 用户情景): fix one glossary for the course.

## 10. Recommendations for the course

**Teach first (in this order, each on the learner's own project if there is one, otherwise on the course's practice project):** (1) problem → issue with acceptance criteria, plus one real bug report; (2) board, WIP limit, Definition of Workflow; (3) DoD and `make dod`; (4) changelog, SemVer, first tag and release checklist; (5) ADR 0001 ("why uv", "why this data source") and one mini design doc; (6) weekly review; (7) debt and risk registers; (8) an incident drill with a blameless postmortem (scenario: returns were wrong because of look-ahead bias); (9) team norms: CONTRIBUTING, CODEOWNERS, review turnaround, RACI with an AI assistant, bus factor; (10) docs architecture (Diátaxis), README standard, LICENSE / SECURITY / CODE_OF_CONDUCT; capstone: the learner's own 规范 document in 【强制】/【推荐】/【参考】 form.

**Mention but do not drill:** story points, velocity, burndown, planning poker, RICE arithmetic, Scrum roles and events, on-call rotations, incident command roles, change advisory boards, RFC processes, CalVer, towncrier, Renovate, RASCI.

**Skip:** scaled frameworks, certification vocabulary, tool comparisons (Jira and similar).

**Plain-Chinese analogies that fit:** DoD = 出厂质检单（全班统一的交卷要求）, 验收标准 = 这道题的评分标准; WIP 限制 = 灶台只有两个火眼，“先做完，再开始”; 看板 = 餐厅出菜口的小票; ADR = 决策的病历，不能涂改只能续写; 更新日志 = 应用商店里的“更新说明”，git log 是厨房流水账; 语义化版本 = “大改.加功能.修 bug”; 技术债 = 信用卡，利息是以后每次改动都更慢，只修常走的那段路; 功能开关 = 电闸; 无指责复盘 = 航空事故调查，目的是不再发生，不是找人背锅（“复盘”一词来自围棋 [memory]）; 风险登记 = 出门前看天气：可能性 × 后果; 巴士因子 = 只有一个人有钥匙; RACI = 谁干活、谁拍板、问谁、告诉谁; 规范 = 交通规则（手册前言自己的比喻）; Diátaxis = 学车的教练课 / 导航路线 / 地图 / 讲原理的文章（the site itself uses a driving lesson and a nautical chart).

**Honest framing to include:** these norms exist to lower the cost of working with other people and with your future self; a solo beginner should run the smallest version that still produces evidence (a passing `make dod`, a tag, a changelog entry, an ADR, a weekly note), and grow it only when something hurts.

## 11. Not verified today

- Content of Card (2017) BMJ paper, Etsy "Blameless PostMortems", PMI / ASQ pages, GitLab handbook meeting rules, GB/T 1.1-2020 wording (应 / 宜 / 可), Atlassian definitions: all [memory] or search-snippet level.
- Every glossary row tagged [memory], including 故障等级 P0-P4 conventions, 功能开关, 灰度发布, 技术债, 巴士因子, and the Chinese names for the four Diátaxis types.
- GitHub server-side behaviour: issue forms rendering, `cooldown` under the `uv` Dependabot ecosystem, generated release notes, `git push --follow-tags`, branch protection, Projects: read in docs, not exercised (no remote, `gh` not installed).
- Dependabot's listed uv version ("v0.11") against uv 0.13.5 lockfiles; uv docs say some Dependabot cases still fail.
- The GitHub plans page as summarised today lists Actions on Free as an included monthly compute amount in dollars rather than minutes; I did not read the billing page.
- Exact release date of Contributor Covenant 3.0 (mid-2025 per secondary sources) and the detailed MADR 3 → 4 differences.
- Scrum Guide Expansion Pack contents (search results only).
- `uv run pytest` and a type checker in the DoD (not installed here); `uv tree --outdated` and `uv lock --upgrade` against real dependencies (flags seen in `--help` only).
- Counts from the Alibaba PDF are from machine-extracted text and may be off by a few.
- Budget heuristics such as "reserve 10-20% of time for debt" are folklore; I left them out of the templates.
