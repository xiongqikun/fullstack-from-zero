# Brief `skill-model`: a competency model for a professional full-stack engineer that a beginner can self-assess

Research date: 2026-11-19 (macOS 27.2.1 arm64). Raw material for lesson builders, not a message to the learner.
Tags: **[local]** ran or parsed on this machine today · **[source: URL]** read in that source today (marked *secondary* when it is press coverage or a search summary rather than the primary document) · **[memory]** not verified today · **[synthesis]** my own design decision built on the cited sources (not a fact about the world).

## 0. Decision summary

1. **Model**: 14 skill areas in 4 clusters x 5 levels (L0-L4). L2 is the *junior hire line*, L3 the *independent developer* line and the course target for 12 areas (L2 for design and planning); L4 needs real team experience and is out of course scope. [synthesis, anchored in sections 2-4]
2. **"Professional" is not "knows more tools"**. Every ladder I read grades autonomy, scope and quality habits; roadmap.sh's Full Stack roadmap (37 nodes) has zero nodes for testing, code review, documentation, accessibility, performance or debugging. [local]
3. **AI raises the value of specifying, decomposing, reviewing and verifying, and it measurably weakens learning when it is used as a ghost-writer.** DORA 2025: AI is an amplifier, throughput up, instability still up, 30% of respondents trust AI code little or not at all. Anthropic RCT (Jan 2026): AI-assisted learners scored 50% vs 67% on a comprehension quiz, largest gap in debugging. [sources in section 6]
4. **The planned roadmap has no home for two areas** (AI collaboration, debugging) and reaches five areas only in stage 7 or later (security S7, delivery S8, planning and communication S9, design S10). Ten sub-skills are not named at all or only implicit (accessibility, performance, privacy, licences/ethics, estimation, English reading, user focus, postmortems, code reading, CS basics). [local: `skillmap.py matrix`]
5. **Self-rating alone is unreliable for novices** (illusion of competence with GenAI; experienced developers misjudged their own speed by about 40 points in METR's 2025 trial). Require an artefact for every claim of L2 or higher. [sources in section 6]
6. **progression.fyi no longer exists as a framework library**: today it answers HTTP 301 to a commercial page. Use the primary frameworks listed in section 2 instead. [local]

## 1. What I verified and how

Tools used for every [local] claim:

```text
$ python3 --version
Python 3.14.9
$ uv --version
uv 0.13.5 (Homebrew 2026-10-22 aarch64-apple-darwin)
$ ruff --version
ruff 0.17.2
$ git --version
git version 2.54.0 (Apple Git-157)
```

| Item | Method today | Result |
|---|---|---|
| progression.fyi | `curl -sS -o /dev/null -D - https://www.progression.fyi/` [local] | `HTTP/2 301`, `location: https://careerminds.com/job-architecture` (same for the bare domain). The Wayback Machine still holds HTTP 200 snapshots up to 2026-09-15; I downloaded `https://web.archive.org/web/20260915073931id_/https://progression.fyi/` with curl (gzip body) and it lists 75 frameworks (index at the end of section 2). Careerminds announced acquiring Progression in Oct 2024 [source: careerminds.com/blog/careerminds-acquires-progression, secondary/search]. |
| SWEBOK | `curl` of `https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf`, text via `uv run --no-project --with pypdf python -I tools/pdf_extract.py` [local] | Cover reads "v4.0a, Released August 2026"; 411 pages; PDF ModDate 2026-08-04; HTTP Last-Modified 4 Aug 2026; copyright line 2014-2025; 18 knowledge areas. The landing page computer.org/education/bodies-of-knowledge/software-engineering returned HTTP 403 to my fetcher. |
| DORA 2025 and 2024 reports | `curl` of both PDFs from services.google.com, text via pypdf [local] | 2025: "State of AI-assisted Software Development", v. 2025.2, 142 pages, survey 13 Jun-21 Jul 2025, nearly 5,000 respondents plus 100+ hours of interviews. 2024: v. 2024.3, 120 pages. |
| roadmap.sh | `curl https://roadmap.sh/<slug>.json` for full-stack, frontend, backend, devops; parsed with `tools/roadmap_themes.py` [local] | HTTP 200; `updatedAt` 2026-01-06, 2026-07-15, 2026-02-07, 2026-10-27. The old GitHub raw path `src/data/roadmaps/full-stack/full-stack.json` now returns 404. |
| SFIA 9 (en and zh), UK government framework, Dropbox, engineeringladders.com, career-ladders.dev, DORA web pages, Stack Overflow 2025 and 2026, Octoverse 2026, Anthropic, METR, Veracode, arXiv, Stanford, abseil.io (SWE at Google), sre.google, pragprog.com/tips, 12factor.net, OpenSSF Scorecard, W3C, web.dev | WebFetch of the pages named in the tags below | See sections 2, 5, 6. |
| Chinese national occupational skill standard 4-04-05-01 (2022) | PDF fetched from a college mirror (wic.edu.cn), text extracted with pypdf [local] | 23 pages; four grades; see section 2. Not fetched from mohrss.gov.cn itself. |
| Not reachable today | | SWECOM page on computer.org (403); CircleCI matrix (Google Sheets); GitLab career matrix body (only navigation returned); Veracode's July 2026 press release (403); web.archive.org through the fetch tool. |

Downloading and parsing pattern that worked in this sandbox (network hosts must be allow-listed per command):

```sh
export UV_CACHE_DIR="$TMPDIR/uv-cache"
curl -sS -L -o downloads/dora/dora2025.pdf https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf   # 200, 15479474 bytes
uv run --no-project --with pypdf python -I tools/pdf_extract.py downloads/dora/dora2025.pdf extracted/dora2025.txt                      # pages=142
```

## 2. What the real frameworks look like today

| Framework | Status today | Structure | What I took from it |
|---|---|---|---|
| **SFIA 9** | Current standard, published Oct 2024; SFIA 10 "in consultation", tentatively Q2 2027-Q1 2028, with an interim consultation on AI [source: sfia-online.org/en/sfia-9, /en/sfia-10] | 7 levels of responsibility: Follow, Assist, Apply, Enable, Ensure/advise, Initiate/influence, Set strategy/inspire/mobilise. 16 generic attributes, business skills and behavioural factors (Autonomy, Influence, Complexity, Knowledge, Collaboration, Communication, Improvement mindset, Creativity, Decision-making, Digital mindset, Leadership, Learning and development, Planning, Problem-solving, Adaptability, Security/privacy/ethics). The A-Z page lists 147 professional skills (count reported by the fetch tool) [source: sfia-online.org/en/sfia-9/responsibilities and .../generic-attributes-business-skills-behaviours, .../all-skills-a-z] | Levels are defined by autonomy and review frequency, not by tool lists: level 1 works under close direction with work closely reviewed, level 2 under routine direction, level 3 under general direction with review at milestones, level 4 with considerable personal responsibility [source: .../autonomy]. The PROG skill starts at level 2 with *simple* programs and checking one's own work, moves to *moderately complex* programs and joint reviews at 3, and to *complex* programs and leading reviews at 4 [source: sfia-online.org/en/sfia-9/skills/programming-software-development]. |
| **UK Government Digital and Data Profession Capability Framework** | Renamed from "DDaT" on 1 Dec 2023; home page last updated 30 Sep 2026 (domain moved to understand-digital-data-roles-skills.service.gov.uk; the old ddat-capability-framework domain 301-redirects) [source: understand-digital-data-roles-skills.service.gov.uk] | 53 roles in 8 groups. Four skill levels: Awareness (can describe the fundamentals), Working (can apply with some support), Practitioner (applies without support, picks tools, shares knowledge), Expert (leads and teaches). Software developer role: 10 skills, 9 role levels from apprentice to principal [source: .../role/software-developer, page updated 29 Aug 2025] | The cleanest public definition of the **junior line**: a junior developer needs Programming-and-build, Information security, Modern development standards, Prototyping and Service support at *Working*, and only *Awareness* of Systems design, Systems integration, User focus and Capacity management. A (mid) developer needs Practitioner in programming, security, standards, prototyping and user focus, Working in systems design and integration. |
| **Dropbox Engineering Career Framework** | Public, guideline version v2.9.1 [source: dropbox.github.io/dbx-career-framework] | IC1-IC7 (plus manager track M3-M7); core responsibilities in four pillars (Results, Direction, Talent, Culture) plus a discipline-specific Craft pillar | IC1 carries out defined tasks with specific guidance, owns mistakes, escalates when stuck, and writes clear code whose bugs sit in edge cases rather than the main path. IC2 carries out defined projects with high-level guidance and understands existing designs. IC3 independently solves ambiguous problems, leads a project through milestones and mentors [source: .../ic1_software_engineer.html, ic2, ic3]. |
| **engineeringladders.com** | Open source, Apache-2.0 [source: engineeringladders.com, github.com/jorgef/engineeringladders] | Five axes x five steps: Technology (Adopts...Creates), System (Enhances...Leads), People (Learns...Manages), Process (Follows...Defines), Influence (Subsystem...Community) | A compact reminder that People and Process are axes of their own, not a footnote to technology. |
| **career-ladders.dev** (Sarah Drasner) | Public [source: career-ladders.dev/engineering] | Engineer I, II, Senior, Staff, Principal, Distinguished | Entry level = finishes clearly defined tasks and says so when blocked. |
| **Etsy Engineering Career Ladder** | Public, HTTP 200 today [local]; [source: etsy.github.io/Etsy-Engineering-Career-Ladder] | Engineer I, II, Senior, Staff, Senior Staff, Principal; competencies rated on five proficiency steps (Beginner, Intermediate, Advanced, Expert, Leading Expert) | Another five-step proficiency scale in real use. Engineer I = still building professional foundations, completes narrowly defined work that comes with clear instructions, is collaborative and curious. |
| **SWEBOK Guide v4.0a** | Free PDF for personal and academic use; v4.0 came out Oct 2024 [source: en.wikipedia.org/wiki/Software_Engineering_Body_of_Knowledge, secondary]; the file served today is labelled v4.0a [local] | 18 knowledge areas: Requirements, Architecture*, Design, Construction, Testing, Operations*, Maintenance, Configuration Management, Management, Process, Models and Methods, Quality, Security*, Professional Practice, Economics, Computing/Mathematical/Engineering Foundations (* = new versus the 15 of v3) [local] | The official list of "what a software engineer should know" now includes architecture, operations and security as first-class areas, and Professional Practice covers ethics, legal issues (licences, copyright, data privacy), documentation, and communication skills including reading/summarising and writing [local: chapter 14 table of contents]. Its foreword says Agile and DevOps were woven into almost all areas and AI/ML into the foundations [local]. |
| **roadmap.sh** | Live JSON per roadmap [local] | Technology graphs. Full Stack: HTML, CSS, JavaScript, npm, Git, GitHub, React, Tailwind CSS, Node.js, PostgreSQL, Redis, JWT Auth, RESTful APIs, Linux Basics, Basic AWS Services, Monit, Ansible, GitHub Actions, Terraform, with 13 project checkpoints | A technology map, not a competency model (see the theme count below). Useful for vocabulary and for its checkpoint-project rhythm. Frontend and Backend roadmaps now place an "AI Assisted Coding" block (Claude Code, Copilot, Cursor, How LLMs work, Prompting Techniques, Agents) right after the basics, as topic 11 of 37 and 11 of 23 [local]. |
| **China: 《计算机程序设计员国家职业技能标准（2022年版）》** 职业编码 4-04-05-01 | Issued by 人力资源社会保障部 with 工业和信息化部; first printed Sept 2022 [local: PDF text] | Four grades: 四级/中级工, 三级/高级工, 二级/技师, 一级/高级技师 (the 2022 revision removed 五级/初级工). Occupational functions: 程序开发准备, 程序编写与修改, 程序调试与验证, and from 技师 upward 技术管理与培训指导 | An official Chinese-language ladder with the same shape as the western ones: 识读设计文档 at the lowest grade, 编写、提交设计文档 next, then 需求文档 and 培训指导; the top grade adds 性能验证 and 安全验证. Its required basics explicitly include 专业外语的阅读与理解, software licences, and eleven laws and regulations including 个人信息保护法, 数据安全法, 网络安全法 and 著作权法 [local]. |
| **SWECOM** (IEEE software engineering competency model) | Primary page not reachable today | Five levels (technician, entry-level practitioner, practitioner, technical leader, senior software engineer) [source: arxiv.org/abs/2607.12259 as summarised by search, secondary] | A July 2026 paper proposes adding two competencies to it: AI Literacy and AI development [source: arxiv.org/abs/2607.12259]. |

Archived index of public ladders (from the 2026-09-15 progression.fyi snapshot; 75 entries) with a liveness check of the engineering ones run today with `curl -o /dev/null -w "%{http_code}"` [local]. HTTP 200: dropbox.github.io/dbx-career-framework, etsy.github.io/Etsy-Engineering-Career-Ladder, engineering-progression.ft.com (Financial Times), github.com/Financial-Times/engineering-progression, github.com/monzo/progression-framework (MIT licence), github.com/jorgef/engineeringladders, career-ladders.dev, circleci.com/blog/why-we-re-designed-our-engineering-career-paths-at-circleci, dresscode.renttherunway.com/blog/ladder, developer.squareup.com/blog/squares-growth-framework-for-engineers-and-engineering-managers, github.com/urbanairship/techladder, github.com/devexperts/grading-system. Gone or moved: basecamp.com/handbook/appendix-05-titles-for-programmers (404), github.com/meetup/engineering-roles (404), github.com/WeTransfer/product-engineering-career-framework (404), inviqa.github.io/engineering-progression-framework (301 to progression.invi.qa), snowflake.medium.com (403 to my client; its repository says Medium no longer uses the tool [source: github.com/Medium/snowflake]). Other names in the index, not checked: Khan Academy, Kickstarter, Spotify, Songkick, Buffer, Carta, Patreon, Artsy, Envoy, Fog Creek, Construx, GitLab, GOV.UK, Intent Media, Red Hat, Wise, Zendesk and about 45 more (mostly design and product ladders).

roadmap.sh theme count, run on the files downloaded today (`python3 -I tools/roadmap_themes.py downloads/roadmap/full-stack.json ...`) [local]:

```text
$ python3 -I tools/roadmap_themes.py downloads/roadmap/full-stack.json
== full-stack  updatedAt=2026-01-06  topic+subtopic nodes=37
   testing                0  
   security               1  JWT Auth
   accessibility          0  
   performance            0  
   docs/writing           0  
   code review            0  
   version control        3  Git, GitHub, GitHub Actions
   ci/cd                  2  Checkpoint — CI / CD, GitHub Actions
   monitoring/incidents   1  Checkpoint — Monitoring
   architecture           0  
   privacy/licensing      0  
   estimation/planning    0  
   debugging              0  
   AI-assisted coding     0  
```
For comparison the same script finds, in Frontend (120 nodes, updated 2026-07-15): testing 5, security 6, accessibility 1, performance 2, code review 1, AI-assisted coding 8; in Backend (155 nodes): testing 4, security 13, code review 1, architecture 3, AI-assisted coding 7; none of the four roadmaps has a node for debugging, estimation/planning, privacy or licensing.

## 3. The model

### 3.1 Level scale (render with `python3 skillmap/skillmap.py render`) [synthesis]

Driving-licence analogy for lessons: L0 = 坐在后座（别人或 AI 在开车）; L1 = 教练坐在副驾，有副刹车; L2 = 拿到驾照，熟悉的路能自己开; L3 = 陌生城市、下雨的夜里也能把乘客安全送到，并对结果负责; L4 = 能当教练、能给车队排路线。

"Without help" needs a precise meaning now that an AI can do the task. Recommended rule for every self-rating: the claim counts only if the learner can (1) **do** it with AI code generation switched off (documentation allowed), (2) **explain** it in their own words, and (3) **point to an artefact** (commit, file, passing check). From L3 upward AI assistance is allowed, but the learner must be able to read every changed line and modify the result without AI.

| 级别 | 中文名 | English | 含义 | 对应的公开框架 |
|---|---|---|---|---|
| L0 | 未入门 | Not yet | 没接触过，或只能让别人/AI 全权代做，自己说不清做了什么。 | （无对应职业级别） |
| L1 | 入门·跟着做 | Guided | 在教程、导师或 AI 的一步步指导下能完成；能用自己的话讲出每一步在干什么。 | SFIA 1 跟随 Follow；UK Awareness；Dreyfus novice |
| L2 | 上手·小事独立 | Working | 简单、明确的小任务能独立完成（不让 AI 代写），常见问题能自己查文档解决，会检查自己的工作。 | SFIA 2 协助 Assist；UK Working（junior developer）；Dropbox IC1；国标四级/中级工 |
| L3 | 胜任·独立负责 | Independent | 能独立负责一个中等复杂度功能或小项目的全过程，按工程规范交付，并参与评审别人（含 AI）的工作。 | SFIA 3 应用 Apply；UK Practitioner（developer）；Dropbox IC2；国标三级/高级工 |
| L4 | 熟练·能带人 | Leading | 能处理复杂或模糊的问题，主导评审、选型和规范，指导他人。通常需要真实团队经验，超出本课程范围。 | SFIA 4 帮助 Enable；UK Practitioner→Expert（senior/lead）；Dropbox IC3；国标二级/技师 |

#### 1. 工具与环境 / Tools & environment（`tools`，A 基本功，课程目标 L3）

比喻：厨师的刀和灶：工具不顺手，再好的菜谱也做不出来。

- L0：只会用鼠标点图形界面，不知道终端是什么。
- L1：能照着步骤在终端里切换目录、查看文件、运行一个现成命令；能用编辑器打开文件夹、编辑并保存。
- L2：不看教程能完成日常操作：建/移/删文件，安装并运行项目依赖（uv、npm）；看到 command not found、permission denied、No such file 能自己判断原因并解决。
- L3：能从零搭好一个项目的开发环境，并写成别人照做就能成功的步骤；会用环境变量、PATH 和 Shell 配置；能靠 --help 和官方文档学会一个没用过的命令行工具。
- L4：能为团队统一并自动化环境（脚本、任务运行器、容器）；能排查「我电脑上能跑、别处不行」的环境差异。

#### 2. 版本控制与协作流程 / Version control & collaboration（`vcs`，A 基本功，课程目标 L3）

比喻：游戏存档，加上多人同时改一份文件时的交通规则。

- L0：靠「复制一份、改名 final_v2」保存版本。
- L1：能照着步骤完成 init、add、commit、push；能说出一次提交（commit）就是一个存档点。
- L2：独立完成日常循环：小步提交并写清楚提交说明，查看 diff 和 log，建分支，用 restore 或 revert 撤销一次错误修改，把仓库推到 GitHub。
- L3：能走完 issue → 分支 → PR → 评审 → 合并的完整流程；PR 小而聚焦，写明改了什么、为什么、怎么验证；能解决常见合并冲突；能认真评审别人或 AI 的改动并提出具体意见。
- L4：能为项目制定分支、发布和评审规范并配置保护规则；能用 bisect、reflog 找回丢失的工作或定位引入问题的提交；能指导他人。

#### 3. 编程基础 / Programming fundamentals（`programming`，A 基本功，课程目标 L3）

比喻：先会读、再会写：语法是字词，函数和模块是段落和文章结构。

- L0：看不懂代码。
- L1：能读懂并逐行讲解 20 行以内的程序；能照例子改参数，并在运行前预测结果。
- L2：不让 AI 代写，能独立写出 50–100 行、解决一个明确小问题的程序（变量、条件、循环、函数、列表与字典、文件读写）。
- L3：能把一个中等问题拆成多个函数和模块并实现；会读文档使用标准库和第三方库；能读懂陌生代码库的一个模块并在其中安全地加功能；第二门语言（JavaScript/TypeScript）达到 L2。
- L4：写出的代码别人容易读、容易改，并能说明取舍；对常用数据结构和复杂度有直觉；能快速上手新语言或框架并遵循其惯用法。

#### 4. 调试与问题解决 / Debugging & problem solving（`debugging`，A 基本功，课程目标 L3）

比喻：医生看病：先复现症状，再提出假设、做检查、对症下药。

- L0：一报错就卡住，或者整段复制给 AI 或别人。
- L1：能把报错信息完整读完，找到出错的文件和行号；会用 print 查看变量的值。
- L2：能稳定复现问题，用「提出假设 → 验证」的方式定位常见错误；会用调试器的断点和单步；能写出别人看得懂的求助：现象、期望、已尝试、最小示例。
- L3：能定位跨多个文件、前后端或数据库的问题；会看日志、浏览器开发者工具和网络请求；修完会补一个防止复发的测试；能判断 AI 给出的修复是否治本。
- L4：能排查偶发、性能、并发和线上环境的疑难问题；能主持事故复盘，并把教训变成自动化检查。

#### 5. 代码质量与测试 / Code quality & testing（`quality`，B 工程质量，课程目标 L3）

比喻：出厂质检：不靠「我试过了」，靠任何人都能重复的检查。

- L0：能跑就行，靠手动点一点来确认。
- L1：能运行现成的测试和检查工具（pytest、ruff），看懂通过与失败。
- L2：能为自己的函数写基本的单元测试（正常、边界、错误输入）；提交前自己跑检查并修掉警告；能做小重构（改名、提取函数）并保持测试通过。
- L3：测试随功能一起交付；会用类型标注、夹具和测试替身，把覆盖率当参考而不是目标；检查在 CI 上自动运行；能评审测试是否真的验证了行为（包括 AI 写的测试）。
- L4：能为项目设计测试策略（单元、集成、端到端的比例），治理不稳定测试，带头重构遗留代码并保持随时可发布。

#### 6. 安全与隐私 / Security & privacy（`security`，B 工程质量，课程目标 L3）

比喻：门锁、保险柜和访客登记：默认不信任任何外来输入。

- L0：把密码、密钥直接写在代码里或发到聊天里。
- L1：知道密钥不能进仓库，会用 .gitignore 和 .env；知道不能随便运行来历不明的脚本和命令。
- L2：能说出常见风险的含义（注入、XSS、弱口令、越权）；对所有外部输入做校验；依赖有锁文件并知道如何更新；知道哪些数据属于个人信息。
- L3：能用成熟的库正确实现登录、会话和权限；能按 OWASP 清单自查并修复；能审查 AI 生成代码里的安全问题；按最小必要原则收集和保存个人数据。
- L4：能做威胁建模，安排安全测试和依赖供应链治理；能处理安全事件并推动整改；了解个保法、GDPR 等法规对设计的影响。

#### 7. 交付与运维 / Delivery & operations（`delivery`，B 工程质量，课程目标 L3）

比喻：从后厨到餐桌：出菜流程、上菜，以及客人吃出问题时怎么处理。

- L0：程序只存在于自己的电脑上。
- L1：能照文档把项目在本机跑起来；能说出开发环境和生产环境的区别。
- L2：能写出一键式的本地命令（安装、测试、运行）；能看懂并修复一次 CI 失败；会用 Docker 运行一个现成的镜像。
- L3：能为项目配置 CI（检查加测试）和自动部署；能把应用部署到一台服务器或云平台，配置环境变量、日志和健康检查；出问题能回滚；有版本号和变更记录。
- L4：能设计发布策略（灰度、回滚、数据库迁移）和监控告警；用交付指标（部署频率、变更前置时间、变更失败率等）持续改进；能主持对事不对人的复盘。

#### 8. 前端与用户体验 / Front-end & user experience（`frontend`，C 全栈技术，课程目标 L3）

比喻：店面和柜台：客人看到、摸到的一切。

- L0：不知道网页是怎么显示出来的。
- L1：能照例子写出含标题、段落、链接、图片、表单的静态网页，并用 CSS 调整样式。
- L2：能独立做出在手机和电脑上都好用的页面；能用 JavaScript 处理点击、表单校验、请求接口并更新页面；会用浏览器开发者工具查看元素和网络请求。
- L3：能用 TypeScript 和 React（或同类框架）做出多页面应用：拆分组件、管理状态、路由、调用后端接口、处理加载与错误；达到基本的无障碍要求（语义化标签、键盘可操作、对比度）和性能要求（核心网页指标）；有组件测试。
- L4：能设计前端架构和组件库，系统地优化性能与无障碍，制定前端规范并指导他人。

#### 9. 后端与数据 / Back-end, APIs & databases（`backend`，C 全栈技术，课程目标 L3）

比喻：后厨和仓库：按订单做菜，管好库存和账本。

- L0：分不清服务器、数据库、接口分别是什么。
- L1：能讲清「浏览器发请求 → 服务器处理 → 数据库读写 → 返回响应」的过程；能用现成工具发一个 HTTP 请求、执行一条 SELECT 查询。
- L2：能独立写出带增删改查的简单接口（如 FastAPI），并用 SQL 建表、查询和关联；能读懂状态码和接口文档。
- L3：能设计并实现一组规范的 REST 接口：数据建模、输入校验、分页、错误处理、认证授权、数据库迁移和事务；有接口测试和自动生成的文档；能发现并解决慢查询（索引、N+1）。
- L4：能在容量与一致性之间做取舍（缓存、队列、并发），设计可演进的数据模型和接口版本策略，并指导他人。

#### 10. 系统设计与架构 / System design & architecture（`design`，C 全栈技术，课程目标 L2）

比喻：盖房前的图纸：先想清楚承重墙，再砌砖。

- L0：想到哪写到哪，所有代码堆在一个文件里。
- L1：能看懂一张简单的系统框图（前端、后端、数据库），并说出各部分的职责。
- L2：能把一个小项目按职责拆成模块和文件，并说明为什么这样分；能画出自己项目的结构图。
- L3：动手前能写一页设计说明（目标、方案、备选方案与取舍、风险）；能判断新代码在已有结构中该放哪里；能把需求拆成可以独立交付的小步骤；能评估 AI 给出的方案是否合适。
- L4：能为新系统做技术选型和架构设计，记录架构决策（ADR），规划演进并偿还技术债，让团队达成共识。

#### 11. 需求、计划与估算 / Requirements, planning & estimation（`planning`，D 协作与成长，课程目标 L2）

比喻：装修前先问清业主要什么，再排工期、报预算。

- L0：拿到一个模糊的想法就直接开写。
- L1：能把「我想要什么」写成几条可以检验的验收标准（做到什么才算完成）。
- L2：能把一个功能拆成若干个一两小时的小任务并排好顺序；先估时间、再记录实际用时，知道自己的偏差有多大。
- L3：能把模糊需求问清楚并写成 issue 或规格说明；维护任务看板；给出有依据、带范围的估算，并提前预警延期；能区分必须有和可以晚点做。
- L4：能规划多周的里程碑，管理范围和风险，协调多方干系人，并用数据复盘计划的准确度。

#### 12. 沟通、文档与英文阅读 / Communication, docs & reading English（`communication`，D 协作与成长，课程目标 L3）

比喻：交接班记录：写给下一个人，也写给三个月后的自己。

- L0：代码没有任何说明；遇到问题只会说「不行了」。
- L1：能用 Markdown 写一份 README（这是什么、怎么运行）；能借助翻译读懂英文报错和文档的大意。
- L2：写的提交说明、PR 描述和求助帖，没参与的人也能看懂；能直接阅读英文官方文档的入门和教程部分并照做；认识常见的英文技术词汇。
- L3：能写设计说明、变更记录和操作手册；在评审中能给出、也能接受具体而对事不对人的意见；能独立查阅英文参考文档、更新日志和 issue 讨论，并用英文写简短的 issue 或 PR。
- L4：能做技术分享，撰写规范和决策记录，向非技术人员解释取舍并促成决定。

#### 13. AI 协作与验证 / Working with AI agents（`ai`，D 协作与成长，课程目标 L3）

比喻：带一个手很快、但会自信地出错的实习生：你负责交代清楚、检查验收，并对结果负责。

- L0：让 AI 全权代写，不看就用，说不出代码做了什么。
- L1：会向 AI 提概念性的问题来帮助自己理解；对 AI 的回答保持怀疑，关键说法会去官方文档核对。
- L2：能给 AI 清楚的任务说明（目标、约束、验收标准）；逐行读懂 AI 的改动（diff）之后才接受；用运行和测试来验证，而不是「看起来对」。
- L3：能把大任务拆成小步交给 AI，每一步都用 Git 存档、可以回滚；能发现 AI 代码里的错误、安全漏洞和多余的复杂度；能为项目写好给 AI 的说明和规则；清楚哪些事不该交给 AI（密钥、不可逆操作、自己还不会验证的东西）。
- L4：能设计团队的 AI 使用规范和质量闸门（评审、测试、安全扫描），编排多个智能体的工作流，并衡量它对交付质量的真实影响。

#### 14. 学习与职业素养 / Learning & professional practice（`growth`，D 协作与成长，课程目标 L3）

比喻：运动员的训练计划和职业操守。

- L0：靠收藏教程和看视频，很少动手；害怕犯错。
- L1：能按固定节奏练习并记学习日志；卡住时知道去哪里找答案（官方文档、搜索、提问）。
- L2：会主动找反馈并据此改进；出错后能写一份简短复盘（发生了什么、为什么、下次怎么防）；知道开源许可证和版权的基本含义。
- L3：能独立用官方文档和源码学会一项新技术，并做出可以运行的示例；对自己的交付负责到底；遵守保密、许可证和职业道德要求；持续维护个人工程手册。
- L4：能指导新人、分享经验，推动团队改进做事方式；长期经营自己的知识组合。

### 3.2 Target profile and hire line [synthesis]

- **Junior hire line = L2 in clusters A and B plus `frontend`, `backend`, `communication`, `ai`, `growth`; L1 in `design` and `planning`.** This mirrors the UK junior developer profile (Working in programming, standards, security, service support; Awareness in systems design, integration and user focus) and Dropbox IC1.
- **Course graduation target = L3 in 12 areas, L2 in `design` and `planning`** (the UK "developer" profile: Practitioner in programming, security, standards, user focus; Working in systems design). A solo learner can only partly evidence L3 in `planning`, `communication` and code review, because those levels involve other people; say so honestly in stage 0.
- A beginner's honest starting profile is L0 almost everywhere, including `ai`: directing an agent to build a project one cannot read is the L0 statement of that area and matches the lowest-scoring "AI delegation" pattern in Anthropic's trial (section 6). Frame this kindly: L0 means "not yet", and stage 1 moves three areas to L1-L2 within weeks.

### 3.3 Evidence checks for the areas that stages 0-1 touch [synthesis; every command below was run here on a throwaway repository]

| Claim | 做 (auto-check) | 讲 (explain-back) | 证 (artefact) |
|---|---|---|---|
| `tools` L1 | Files and folders created through the terminal exist at the expected paths (`test -d`, `test -f`) | "What does each part of `ls -la ~/Documents` mean?" | Cheat-sheet page in the handbook, in the learner's own words |
| `tools` L2 | A planted problem (wrong path, missing execute permission) is fixed and the script runs | "Why did the shell say command not found?" | Three-line note on the cause |
| `vcs` L1 | `git rev-list --count HEAD` is at least 1 | "What is the difference between saving a file and committing?" | The first commit |
| `vcs` L2 | At least 5 commits with descriptive subjects, one merge, one revert, `.gitignore` tracked, nothing unpushed or uncommitted (commands below) | "How would you undo your last commit without losing history?" | The repository itself |
| `communication` L1 | `README.md` exists and contains a title and a run section | "Who is this README for?" | The README |
| `debugging` L1 | Given a planted traceback, the learner writes the failing file and line into an answer file | "Read the last line of the error aloud; what does it claim?" | Answer file |
| `ai` L1 | none (not automatable) | "Which AI statement did you check today, and where?" | Handbook entry with the documentation URL |
| `growth` L1 | Learning log has dated entries with estimated and actual minutes | "What will you do differently next session?" | The log |

```text
$ git rev-list --count HEAD                                                        -> 6
$ git log --format=%s | python3 -c "import sys; print(sum(1 for line in sys.stdin if 10 <= len(line.strip()) <= 72))"   -> 6
$ git log --merges --oneline | wc -l                                               -> 1
$ git log --oneline --grep='^Revert' | wc -l                                       -> 1
$ git ls-files --error-unmatch .gitignore >/dev/null 2>&1 && echo yes || echo no   -> yes
$ git rev-parse --abbrev-ref --symbolic-full-name '@{u}'                           -> origin/main
$ git rev-list --count '@{u}..HEAD'                                                -> 0
$ git status --porcelain | wc -l                                                   -> 0
```

Count characters with Python, not with awk: on this Mac `awk '{print length($0)}'` (awk version 20200816) reports 33 for the 11-character subject 修复登录页面的错误提示 even with `LC_ALL=en_US.UTF-8`, and `wc -m` reports 11 only when a UTF-8 locale is set (33 with `LANG` unset, as in this sandbox); Python's `len()` reports 11 [local]. A length rule tuned for English (10-72 characters) also rejects good short Chinese subjects, so `probe/norms_probe.py` accepts 4 or more Chinese characters.

## 4. Where each area comes from

| Area (id) | SFIA 9 | SWEBOK v4.0a | UK developer skill | DORA capability / other |
|---|---|---|---|---|
| 工具与环境 `tools` | METL, SYSP | Construction; Computing Foundations | Modern development standards | Pragmatic Programmer tips 25-26 (plain text, shell); 国标 "搭建开发环境" |
| 版本控制与协作流程 `vcs` | CFMG, RELM | Configuration Management | Modern development standards | Version control, Trunk-based development, Working in small batches, Streamlining change approval; SWE at Google ch. 9, 16 |
| 编程基础 `programming` | PROG | Construction; Foundations (3 KAs) | Programming and build | Dropbox "Code Fluency"; 国标 "程序编写与修改" |
| 调试与问题解决 `debugging` | Problem-solving attribute; PBMG | Construction; Testing; Maintenance | Service support | Pragmatic tips 29-34; 国标 "程序调试与验证"; Anthropic RCT |
| 代码质量与测试 `quality` | TEST, NFTS, QUAS | Testing; Quality | Modern development standards | Test automation, Continuous integration, Code maintainability; SWE at Google ch. 8, 11-14, 20 |
| 安全与隐私 `security` | SCTY, VUAS; Security/privacy/ethics attribute | Security (new); Professional Practice (data privacy) | Information security | Pervasive security; OpenSSF Scorecard; Veracode; 个保法 in 国标 |
| 交付与运维 `delivery` | DEPL, RELM, ITOP, USUP | Operations (new); Configuration Management (release) | Availability and capacity management; Service support | Continuous delivery, Deployment automation, Monitoring and observability; five delivery metrics; SRE postmortems; 12-factor |
| 前端与用户体验 `frontend` | HCEV, USEV, ACIN | Design (user interface) | User focus; Prototyping | roadmap.sh Frontend; WCAG 2.2; Core Web Vitals |
| 后端与数据 `backend` | DBDS, DTAN, SINT | Design; Construction; Computing Foundations | Systems integration | Database change management; roadmap.sh Backend |
| 系统设计与架构 `design` | SWDN, DESN, ARCH | Architecture (new); Design | Systems design | Loosely coupled teams; Dropbox "Software/Architecture Design" |
| 需求、计划与估算 `planning` | REQM, PRMG, MEAS; Planning attribute | Requirements; Management; Economics | User focus | User-centric focus, Visibility of work, Work in process limits; Pragmatic tips 23-24 |
| 沟通、文档与英文阅读 `communication` | Communication, Collaboration attributes; INCA | Professional Practice (communication skills) | (all skills: "document") | Documentation quality; SWE at Google ch. 2, 3, 10; 国标 "专业外语的阅读与理解" |
| AI 协作与验证 `ai` | Digital mindset attribute; AIDE | none (mentions only) | none | DORA AI Capabilities Model; GitHub "new identity" study; arXiv 2607.12259; roadmap.sh AI block |
| 学习与职业素养 `growth` | Learning and development, Improvement mindset, Adaptability | Professional Practice (ethics, legal) | (role-level descriptions) | Learning culture, Generative culture; Dropbox Talent and Culture pillars; 国标 "职业守则" |

SFIA code names [source: sfia-online.org/en/sfia-9/all-skills-a-z]: PROG Programming/software development, SWDN Software design, DESN Systems design, ARCH Solution architecture, TEST Functional testing, NFTS Non-functional testing, QUAS Quality assurance, CFMG Configuration management, RELM Release management, DEPL Deployment, ITOP Infrastructure operations, USUP Incident management, PBMG Problem management, SCTY Information security, VUAS Vulnerability assessment, HCEV User experience design, USEV User experience evaluation, ACIN Accessibility and inclusion, DBDS Database design, DTAN Data modelling and design, SINT Systems integration and build, REQM Requirements definition and management, PRMG Project management, MEAS Measurement, INCA Content design and authoring, METL Methods and tools, SYSP System software administration, AIDE AI and data ethics. The assignment of codes to my areas is [synthesis].

Official Chinese terms: SFIA's Chinese site renders the levels as 跟随、协助、应用、帮助、确保/建议、主动/影响、制定战略/激励/动员 and the attributes as 自主性、影响力、复杂性、知识、协作、通信、改进心态、创造性、决策力、数字化思维、领导力、学习与发展、规划、问题解决、适应性、安全、隐私与道德 [source: sfia-online.org/zh/sfia-9/responsibilities and .../generic-attributes-business-skills-behaviours]. Some read like literal translation (Communication as 通信, Enable as 帮助); for lessons prefer 沟通 and 带动/赋能 and mention the official wording once.

## 5. "Engineering-grade" versus "it works on my machine"

One-sentence definition to teach: “Software engineering is programming integrated over time.” [source: abseil.io/resources/swe-book/html/ch01.html] The same chapter adds scale (more people) and trade-offs, and calls a project sustainable when the team stays *able* to react to change for the software's whole life. Plain-Chinese analogy [synthesis]: 家常菜和餐厅后厨的区别。在家做菜「这次好吃」就行；餐厅要求换一个厨师、换一天、换一家分店，端出来的菜都一样，而且经得起卫生检查，出了问题能查到是哪一步。

| # | Norm (中文) | Observable evidence | Why (source) |
|---|---|---|---|
| 1 | Everything in version control, small frequent commits, can roll back (版本控制、小步提交、能回滚) | History of small commits with meaningful subjects; a revert the learner did personally | DORA 2025: the benefit of AI on individual effectiveness grows with commit frequency, and on team performance with frequent use of rollback; version control is described as a psychological safety net [local: DORA 2025 PDF p. 56-57]. Pragmatic Programmer tip 28 [source: pragprog.com/tips]. |
| 2 | Small batches (小批量) | PRs of roughly 200 lines or fewer | Google's guidance for a "small" change is about 200 lines [source: abseil.io/resources/swe-book/html/ch09.html]. DORA 2024 estimated that each 25% rise in AI adoption went with 1.5% lower throughput and 7.2% lower stability and suspected growing change size [local: DORA 2024 PDF p. 39-40]. |
| 3 | Review before merge (合并前评审) | PR with a description (what, why, how verified) and review comments | Google requires a peer approval, an owner approval and a readability approval; the listed benefits are correctness, comprehensibility, consistency, shared ownership, knowledge sharing and a historical record [source: abseil.io/resources/swe-book/html/ch09.html]. Reviewers approve once a change clearly improves code health even if imperfect [source: google.github.io/eng-practices/review/reviewer/standard.html]. |
| 4 | Automated tests and CI on every change (自动化测试与持续集成) | Tests in the repo; CI workflow; green check on PRs | Automated testing is what lets software change safely; suggested mix about 80% unit, 15% integration, 5% end-to-end; coverage only shows that a line ran, not that the result was checked [source: abseil.io/resources/swe-book/html/ch11.html]. |
| 5 | Reproducibility (可复现) | Declared and locked dependencies, pinned interpreter, one documented command to install/test/run, config outside the code | Twelve-Factor App factors II (declare and isolate dependencies), III (config in the environment), X (keep development and production alike) [source: 12factor.net]. |
| 6 | Documentation treated like code (文档即代码) | README, docstrings, changelog reviewed with the code | SWE at Google ch. 10 [source: abseil.io/resources/swe-book/html/ch10.html]; "Documentation quality" is a DORA core capability [source: dora.dev/capabilities]. |
| 7 | Automated style and static analysis (自动化检查) | Formatter/linter config, checks in CI | SWE at Google ch. 8 and 20 (table of contents) [source: abseil.io/resources/swe-book/html/toc.html]; Scorecard check "SAST" [source: github.com/ossf/scorecard/blob/main/docs/checks.md]. |
| 8 | Security hygiene (安全卫生) | No secrets tracked, least-privilege CI tokens, dependency updates, input validation, SECURITY.md | Scorecard checks Token-Permissions, Dependency-Update-Tool, Pinned-Dependencies, Security-Policy, Vulnerabilities, Branch-Protection, Code-Review [same source]. Veracode's spring 2026 update: only about 55% of 80 AI code-generation tasks produced secure code, cross-site scripting passed 15% of the time, and the pass rate is roughly where it was two years ago [source: veracode.com/blog/spring-2026-genai-code-security]. |
| 9 | Learning from incidents (对事不对人的复盘) | A written postmortem with causes and follow-up actions | A postmortem is a written record of an incident, its impact and the actions taken, and it stays blameless by looking for contributing causes rather than culprits [source: sre.google/sre-book/postmortem-culture]. Pragmatic tip 29. |
| 10 | Measuring delivery (度量交付) | Team tracks the five DORA metrics | Throughput: change lead time (变更前置时间), deployment frequency (部署频率), failed deployment recovery time (失败部署恢复时间). Instability: change fail rate (变更失败率), deployment rework rate (部署返工率) [source: dora.dev/guides/dora-metrics, updated 5 Jan 2026; Chinese renderings are mine]. |
| 11 | Estimation and early warning (估算与预警) | Estimate-versus-actual log; issues with scope | Pragmatic tips 23-24 (estimate to avoid surprises; revise the schedule as the code evolves) [source: pragprog.com/tips]; SWEBOK ch. 9 covers planning and measurement [local]. |
| 12 | Ownership and asking for help (负责到底、及时求助) | Mistakes written up; blocked items raised early | Dropbox IC1 owns decisions and mistakes and escalates when stuck [source: dropbox.github.io/dbx-career-framework/ic1_software_engineer.html]. |
| 13 | User focus (以用户为中心) | Acceptance criteria written before code | DORA 2025: AI adoption can hurt teams that lack a user-centric focus and helps strongly when it is present [local: DORA 2025 PDF p. 64]; "User focus" is a UK developer skill. |
| 14 | Legal and ethical basics (许可证、隐私、职业道德) | LICENSE file; personal-data fields identified | SWEBOK Professional Practice [local]; 国标 required knowledge [local]; Scorecard "License" check. |

Glossary seeds for the norms (my renderings; keep the English beside the Chinese): version control 版本控制 · commit 提交 · code review 代码评审 · pull request (PR) 拉取请求 · continuous integration (CI) 持续集成 · lockfile 锁文件 · reproducible 可复现 · rollback 回滚 · small batches 小批量 · acceptance criteria 验收标准 · blameless postmortem 对事不对人的复盘 · technical debt 技术债 · threat modelling 威胁建模 · data minimisation 最小必要 · architecture decision record (ADR) 架构决策记录 · accessibility 无障碍 · Core Web Vitals 核心网页指标.

A machine-checkable version of this table exists as a prototype: `probe/norms_probe.py` (standard library only, read-only). Real output on two throwaway repositories built by `probe/make_demo_repos.sh` (same 10-line tip calculator; in `demo/pro`, `uv run pytest -q` printed `3 passed`, `ruff check .` printed `All checks passed!`) [local]:

```text
$ python3 probe/norms_probe.py probe/demo/hobby
project: hobby   observable norms: 0/13
  [MISS] vcs           project is a Git repository with history  (1 commit(s))
  [MISS] vcs           commit subjects are descriptive (not 'update'; 10-72 chars or 4+ Chinese chars)  (0/1 descriptive; 0 in Conventional Commits form)
  [MISS] vcs           .gitignore is tracked
  [MISS] communication README explains how to install/run/test  (no README)
  [MISS] growth        LICENSE file present
  [MISS] delivery      CHANGELOG or version tags present
  [MISS] tools         dependencies declared AND locked (reproducible install)  (no lockfile)
  [MISS] quality       automated tests exist
  [MISS] quality       linter/formatter configured
  [MISS] delivery      CI workflow runs on every change
  [MISS] security      no .env file or secret-looking string is tracked  (.env)
  [MISS] security      SECURITY.md or dependency-update config present
  [MISS] ai            instructions for AI agents are versioned (CLAUDE.md / AGENTS.md)
$ python3 probe/norms_probe.py probe/demo/pro
project: pro   observable norms: 12/13
  [PASS] vcs           project is a Git repository with history  (6 commit(s))
  [PASS] vcs           commit subjects are descriptive (not 'update'; 10-72 chars or 4+ Chinese chars)  (6/6 descriptive; 6 in Conventional Commits form)
  [PASS] vcs           .gitignore is tracked
  [PASS] communication README explains how to install/run/test  (README.md)
  [PASS] growth        LICENSE file present
  [PASS] delivery      CHANGELOG or version tags present
  [PASS] tools         dependencies declared AND locked (reproducible install)  (pyproject.toml+uv.lock)
  [PASS] quality       automated tests exist
  [PASS] quality       linter/formatter configured
  [PASS] delivery      CI workflow runs on every change
  [PASS] security      no .env file or secret-looking string is tracked
  [MISS] security      SECURITY.md or dependency-update config present
  [PASS] ai            instructions for AI agents are versioned (CLAUDE.md / AGENTS.md)
```
This is a teaching aid for stage 3 ("turn the hobby repo into the pro repo, one commit per norm"), not a substitute for judgement; a repository can pass all 13 checks and still be wrong.

## 6. How AI coding agents shift the skill model (evidence, 2024-2026)

| Source (date) | Finding | Consequence for the model |
|---|---|---|
| DORA 2025 report, v. 2025.2 [local: PDF] | 90% of respondents use AI at work, median 2 hours on the last workday; 65% rely on it a moderate amount or more; over 80% feel more productive and 59% see better code quality; trust in AI output: 4% a great deal, 20% a lot, 46% somewhat, 23% a little, 7% none. AI adoption now goes with higher throughput but still with higher delivery instability. Central message: AI amplifies the strengths and the dysfunctions that already exist. | Good habits come first; AI multiplies whatever is there. |
| DORA AI Capabilities Model [local: PDF p. 49-64] | Seven capabilities that amplify AI's benefit: Clear and communicated AI stance; Healthy data ecosystems; AI-accessible internal data; Strong version control practices; Working in small batches; User-centric focus; Quality internal platforms. The report tells leaders to train people to guide, evaluate and validate AI output rather than merely to use it, and names verification, orchestration and workflow design as increasingly central tasks. | Three of the seven are individual habits a beginner can learn: version control with rollback, small batches, user focus. |
| DORA 2025, skills question [local: PDF p. 47] | Respondents ranked eight skills; heavier AI adoption raised the perceived importance only of prompt engineering and, unexpectedly, syntax memorisation; problem solving, reading and reviewing code, teamwork, understanding the codebase, documentation and writing code did not move. | Fundamentals are not perceived as obsolete by practitioners. |
| DORA 2025, essay by Matt Beane [local: PDF p. 88] | Default use of AI removes the hands-on work through which novices used to learn from seniors; organisations should measure skill development together with productivity. | Supports a coach-not-ghost-writer tutor and explicit skill tracking. |
| DORA "ROI of AI-assisted Software Development", v. 2026.01 [source: dora.dev/ai/roi (landing page, updated 22 Apr 2026); infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report, secondary] | Expect a J-curve: an early dip caused by the learning curve, a "verification tax" (the cost of reviewing AI output) and downstream processes that must adapt. | Reviewing is now a main cost centre; teach it as a skill. |
| Stack Overflow Developer Survey 2025 [source: survey.stackoverflow.co/2025/ai] | 84% use or plan to use AI tools; 3.1% highly trust and 29.6% somewhat trust the accuracy of AI output, 26.1% somewhat and 19.6% highly distrust it; 66% are frustrated by answers that are almost right; 45.2% say debugging AI code takes longer; 75.3% would still ask a person when they do not trust the AI. Learners: 53% favourable. | "Almost right" is the normal failure mode, so the learner must be able to spot it. |
| Stack Overflow Developer Survey 2026 [source: survey.stackoverflow.co/2026 and /2026/ai] | 30,903 responses from 169 countries; 73% use coding assistants or agents daily; trust options were reworded: 48.0% trust AI when the output is easy to verify, 16.3% for many tasks but not important decisions, 16.3% only for low-risk tasks, 12.3% not for most tasks, 6.6% including important decisions; 17.1% avoid AI in some cases for fear of losing skills. (The survey page itself sets 87% with some level of trust against 31% in 2025; the answer options differ, so I would not teach that as a trend.) | Trust is conditional on verifiability: verification skill is what converts AI output into usable work. |
| GitHub Octoverse 2026 [source: github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents] | Window 1 Oct 2025-30 Sep 2026; 225 million+ developers; 34.3 billion commits; by September over 40% of pull requests started from an agent's first draft (17% in March); TypeScript first, Python second, JavaScript third by contributors; AI-assisted code review usage up more than 90%. | Reading and judging a diff one did not write is becoming the most frequent daily activity. |
| GitHub, "The new identity of a developer" (8 Dec 2025, 22 interviews with heavy AI users) [source: github.blog/news-insights/octoverse/the-new-identity-of-a-developer-what-changes-and-what-doesnt-in-the-ai-era] | Work shifts from implementing to directing and verifying. Skills named: AI fluency, fundamentals (to judge output), product understanding, delegation and orchestration, architecture, verification and quality control; many interviewees spend more time verifying than generating. | Source of the `ai` area's L2-L4 wording. |
| Anthropic, "How AI assistance impacts the formation of coding skills" (29 Jan 2026; RCT, 52 mostly junior engineers learning the Trio library) [source: anthropic.com/research/AI-assistance-coding-skills] | Quiz score 50% with AI versus 67% by hand (Cohen's d 0.74, p = 0.01); no significant time saving; largest gap on debugging questions. Low-scoring patterns (under 40%): full delegation, progressive reliance, letting the AI debug. High-scoring patterns (65% and above): asking conceptual questions only, generating code then asking follow-up questions until it is understood, asking for code together with explanations. Small sample, immediate test, chat sidebar rather than an agent. | The best direct evidence for how the tutor should behave. |
| Anthropic, "How AI is transforming work at Anthropic" (2 Dec 2025; 132 surveyed, 53 interviews) [source: anthropic.com/research/how-ai-is-transforming-work-at-anthropic] | Engineers delegate tasks that are easy to verify, low-stakes or repetitive and keep design; the authors describe a paradox of supervision: overseeing the AI needs the very skills that atrophy when it is overused; some seniors report fewer questions from juniors. | Hand skills are a prerequisite for supervision, not an alternative to AI. |
| METR (10 Jul 2025; update 24 Feb 2026) [source: metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study and metr.org/blog/2026-02-24-uplift-update] | 2025: 16 experienced open-source developers, 246 tasks; with AI allowed they took 19% longer, although they had forecast a 24% speed-up and afterwards still believed they had been 20% faster. 2026 update: new estimates of 18% and 4% faster with intervals that include zero; METR calls its own data unreliable because many developers now refuse to work without AI, and labels the 2025 result historical. | Do not teach "AI makes you slower" as current fact; do teach that felt productivity is not evidence. |
| He et al., MSR '26 (arXiv 2511.04427) [source: arxiv.org/abs/2511.04427] | Projects adopting Cursor showed a large but transient rise in velocity and a persistent rise in static-analysis warnings and code complexity, which in turn slowed later velocity. | Quality gates must exist before agents are turned loose. |
| Stanford Digital Economy Lab "Canaries" dashboard (updated 21 Oct 2026) [source: digitaleconomy.stanford.edu/project/canaries-dashboard] | Since November 2022, large employment declines for 22-25-year-old software developers, modest declines for the next age groups, growth for older ones (payroll data; correlational). | The entry bar has risen: a junior must show judgement and verified, well-engineered work, not just output. |
| Prather et al., ICER 2024 (arXiv 2405.17739) [source: arxiv.org/abs/2405.17739 via search summary, secondary] | With GenAI tools, novices who were already doing well accelerated, while struggling novices kept their metacognitive problems and often believed they understood more than they did. | Novice self-assessment needs external checks. |
| Lee et al., CHI 2025 (Microsoft Research/CMU, 319 knowledge workers) [source: search summary of microsoft.com/en-us/research, secondary] | More confidence in the AI went with less critical thinking, more self-confidence with more; some participants could not verify answers for lack of domain knowledge. | Domain knowledge is what makes verification possible. |

Skills that gain weight [synthesis from the rows above]: writing a precise task statement with acceptance criteria; decomposing work into small, separately verifiable steps; reading diffs and unfamiliar code; testing as the verification interface; debugging by hypothesis; Git as a safety net (commit before every agent step, revert without fear); security review of generated code; architectural judgement ("does this belong here?"); knowing what never to delegate (secrets, irreversible operations, anything one cannot yet verify).

What must still be learned by hand so that AI output can be verified [synthesis]: (1) tracing code line by line and predicting its output; (2) reading tracebacks and error messages; (3) the daily Git loop including undo; (4) writing assertions and small tests; (5) core language constructs and data structures in one language, then a second; (6) HTTP requests and responses and basic SQL, typed by hand at least once; (7) the common vulnerability classes, demonstrated on the learner's own code; (8) writing an acceptance criterion and a one-page design note. The rule for exercises: 先手写，再对照，后委托 (write it by hand, compare with the AI's version, only then delegate that kind of task).

Tutor behaviour that follows from the Anthropic trial [synthesis]: at L0-L2 of an area the tutor answers conceptual questions, gives hints and reviews the learner's code, but does not write the solution and does not debug for the learner; at L3 it may generate code if the learner then explains it and makes one change without AI; every exercise ends with an explain-back question.

## 7. Roadmap stages versus skill areas

Output of `python3 skillmap/skillmap.py validate` and `matrix` (the stage data encodes the planned roadmap as described to me; P = primary home, s = secondary practice) [local; the P/s assignments are synthesis]:

```text
$ python3 skillmap/skillmap.py validate
areas=14 levels=5 stages=11 clusters=4 watchlist=12
OK
$ python3 skillmap/skillmap.py matrix
P = primary home, s = secondary practice, . = not planned
area            S0  S1  S2  S3  S4  S5  S6  S7  S8  S9  S10  P  s
tools           .   P   s   s   .   .   .   .   s   .   .    1  3  工具与环境
vcs             .   P   .   P   .   .   .   .   .   s   .    2  1  版本控制与协作流程
programming     .   .   P   .   s   .   .   .   .   .   .    1  1  编程基础
debugging       .   s   s   .   .   .   .   .   .   .   .    0  2  调试与问题解决
quality         .   .   .   P   .   s   s   s   .   .   s    1  4  代码质量与测试
security        .   .   .   s   .   s   .   P   s   .   s    1  4  安全与隐私
delivery        .   .   .   s   .   .   .   .   P   .   s    1  2  交付与运维
frontend        .   .   .   .   P   .   P   s   .   .   s    2  2  前端与用户体验
backend         .   .   .   .   s   P   .   s   .   .   s    1  3  后端与数据
design          .   .   .   .   .   .   s   .   .   .   P    1  1  系统设计与架构
planning        .   .   .   s   .   .   .   .   .   P   s    1  2  需求、计划与估算
communication   s   s   .   s   .   .   .   .   .   P   s    1  4  沟通、文档与英文阅读
ai              s   .   .   .   .   .   .   .   .   .   .    0  1  AI 协作与验证
growth          P   s   .   .   .   .   .   .   .   s   .    1  2  学习与职业素养

areas with NO primary stage: debugging (调试与问题解决), ai (AI 协作与验证)
areas whose first primary stage is S7 or later: security (S7), delivery (S8), planning (S9), communication (S9), design (S10)

watchlist (sub-skills the plan does not name):
  [no      ] AI 协作与验证（任务说明、拆解、读 diff、验证、安全判断）  ->  从阶段 1 起作为贯穿线；阶段 3 设专门一课；阶段 7、9 再深化。
  [implicit] 调试方法（复现、假设、验证、读报错）  ->  阶段 2 单列一课；阶段 4 浏览器开发者工具、阶段 5 查询计划、阶段 8 日志各回访一次。
  [implicit] 读代码与评审（先读后写）  ->  阶段 2 起每课都有「读一段、讲一段、改一段」；阶段 3 加入带埋点缺陷的评审练习。
  [no      ] 无障碍（WCAG 2.2、语义化、键盘操作）  ->  阶段 4 讲语义化 HTML 时一并讲；阶段 6 用自动化检查复查。
  [no      ] 性能（核心网页指标、慢查询、剖析）  ->  阶段 5 讲索引与 N+1；阶段 6 讲 LCP、INP、CLS；阶段 8 讲监控。
  [no      ] 数据隐私与合规（个人信息、个保法、最小必要）  ->  阶段 5 建模时标注个人信息字段；阶段 7 与安全一起讲。
  [no      ] 许可证、版权与职业道德  ->  阶段 1 建第一个 GitHub 仓库时选许可证；阶段 3 讲依赖许可证；阶段 9 讲职业守则。
  [implicit] 估算（先估后量、记录偏差）  ->  从阶段 1 的学习日志开始：每个练习先写预计用时，再写实际用时。
  [implicit] 需求与用户视角（验收标准、用户故事）  ->  阶段 2 起每个小项目先写三条验收标准；阶段 9 系统化。
  [no      ] 英文技术文档阅读  ->  每课 5–10 个术语进词汇表；阶段 1 起安排读一页官方文档的任务，逐步加长。
  [implicit] 事故复盘（对事不对人）  ->  阶段 1 第一次 Git 事故就写三行复盘；阶段 8 写正式的线上事故复盘。
  [implicit] 计算机基础（数据结构、复杂度直觉、进程与网络）  ->  不做刷题课；在阶段 2、4、5、8 各放一小节「刚好够用」的基础知识。
```

Reading of the matrix [synthesis]:

- **`ai` has no home.** The product configures an AI tutor, but no stage teaches working with agents as a professional skill, although a beginner's only experience with AI is often delegation. Make it a thread: S1 (ask conceptual questions; verify one AI claim against official documentation), S3 (task statement, reading a diff, commit before each agent step, project instruction file), S7 (security review of generated code), S9 (team rules for AI use).
- **`debugging` has no home.** It is the area with the largest AI-related learning gap. Give it a lesson in S2 and revisit it in S4 (browser developer tools), S5 (queries), S8 (logs).
- **Five areas start late.** Use thin early slices: a first CI run in S3, a first deployment of a static page in S4, acceptance criteria from the first project in S2, an estimate-versus-actual line in every exercise from S1, a one-paragraph design note from S3. This matches roadmap.sh's rhythm of a small project checkpoint after every block [local].
- **Sub-skills the plan does not name** (see the watchlist in the output): accessibility, performance, data privacy, licences and ethics, English reading; implicit only: debugging method, code reading and review, estimation, user focus, postmortems, CS basics.
- **Consciously out of scope** (say so in stage 0): mobile apps, data science/ML engineering, Kubernetes-scale operations, multi-agent orchestration (L4 of `ai`). roadmap.sh's Full Stack roadmap lists Ansible, Terraform and several AWS services; the UK junior profile asks only for *awareness* of capacity, integration and systems design, so these can wait.

## 8. What changed recently (older tutorials and my own memory would mislead)

- progression.fyi, the usual link for "public career ladders", now redirects to a sales page [local].
- The UK "DDaT" framework has a new name and a new domain (last change 30 Sep 2026) [source: understand-digital-data-roles-skills.service.gov.uk].
- SWEBOK has 18 knowledge areas since v4 (architecture, operations and security added); texts that cite 15 areas describe v3 [local].
- SFIA 9 (Oct 2024) is current; SFIA 10 is in consultation and is examining AI's impact [source: sfia-online.org/en/sfia-10].
- DORA's "four key metrics" are now five, "time to restore" is now failed deployment recovery time and sits under throughput, and the 2025 report replaced the low/medium/high/elite tiers with seven team archetypes (Foundational challenges, Legacy bottleneck, Constrained by process, High impact low cadence, Stable and methodical, Pragmatic performers, Harmonious high-achievers) [source: dora.dev/guides/dora-metrics; local: the word "elite" occurs 0 times in the 2025 report text and 10 times in the 2024 text].
- DORA's AI finding flipped on throughput between 2024 (negative) and 2025 (positive); instability stayed negative [local]. The capability catalogue on dora.dev now has 34 entries, 7 of them tagged AI [source: dora.dev/capabilities]; the book *Accelerate* (2018) described four metrics and 24 capabilities [memory].
- METR's "19% slower" is labelled historical by METR itself [source: metr.org/blog/2026-02-24-uplift-update].
- Stack Overflow's 2026 survey changed the trust question; 2025 and 2026 trust numbers are not comparable [source: survey.stackoverflow.co/2026].
- Agents start over 40% of GitHub pull requests (Sept 2026); TypeScript is the most used language by contributors, Python second [source: github.blog Octoverse 2026].
- roadmap.sh roadmaps are served as JSON from the site; the four I fetched were last changed between January and October 2026, and Frontend/Backend now contain AI-assisted coding topics [local].
- The Pragmatic Programmer tips page lists 100 tips (20th anniversary edition) [source: pragprog.com/tips]; older tip numbers do not match.
- Seen while building the demo: `uv init --lib` (uv 0.13.5) writes `build-backend = "uv_build"` with `requires = ["uv_build>=0.13.5,<0.14.0"]`; ruff 0.17.2 with no configuration file reported 407 enabled rules and flagged import order, a blind `except` and an unclosed `open()`; the latest releases are actions/checkout v7.0.1 and astral-sh/setup-uv v10.3.3 (my memory said v5 and v7) [local; source: github.com/actions/checkout/releases, github.com/astral-sh/setup-uv/releases]. Details belong to the tooling briefs; I list them as proof that version numbers must be checked.

## 9. Pitfalls a beginner will hit with a skill map

1. Rating recognition instead of ability ("I have heard of Git" counted as L2). Counter: every level statement starts with 能 and names an action; L2+ needs an artefact.
2. Counting what the AI produced as one's own level. Counter: the do/explain/evidence rule in 3.1.
3. Reading a 14 x 5 grid as 70 boxes to tick in order. Counter: show only cluster A in detail in stage 0; unlock the others as stages begin.
4. Comparing oneself with senior ladders (Dropbox IC4+, SFIA 5+). Counter: show only L0-L4 and say that L4 needs a team.
5. Equating "full-stack" with every box on roadmap.sh. Counter: section 2 theme count; the map is breadth of technology, the ladder is depth of responsibility.
6. Believing felt speed (METR 2025). Counter: estimate-versus-actual log.
7. Treating level names as job titles or salary bands. They are not; company ladders differ.
8. Discouragement at seeing L0 fourteen times. Counter: call L0 未入门 ("not yet") and show the first movement within the first week.
9. Chinese terminology drift: the same English term has several renderings (review 评审/审查, deployment 部署/发布, SFIA's 通信 for communication). Counter: one glossary, English term always shown beside the Chinese.
10. Over-trusting automated probes: passing checks proves the artefact exists, not that the learner understands it.
11. Check scripts written for English text misjudge Chinese (byte counts instead of character counts, minimum-length rules); see 3.3.

## 10. Recommendations for the course

Structure
- Make the skill map the spine: a single data file (prototype: `skillmap/skillmap.toml`), each lesson's front matter names the area and level it serves (for example `skills: ["vcs:L2"]`), each auto-check script records evidence for exactly one level statement, and the handbook gets a page 我的能力地图 regenerated at the end of every stage.
- Baseline self-assessment in stage 0 (ten minutes, mostly L0, no shame); re-assess at each stage end; a claim of L2+ without evidence is displayed as L1 (prototype: `skillmap.py assess`, which printed `vcs L1 [#-|-] target L3 !` for an unevidenced L2 claim) [local].
- Present four clusters first (A 基本功, B 工程质量, C 全栈技术, D 协作与成长), then areas.
- State the target honestly: L2 = can be hired as a junior who still needs guidance; L3 = works independently; "professional full-stack engineer" in the usual sense is L3 across the board plus team experience.

Teach first
- Git as a safety net before any further AI-driven change to the learner's existing project, if any (commit, diff, restore, revert).
- Reading: error messages, a 20-line program, a diff. Reading precedes writing in every stage.
- README and commit messages as the first writing tasks; English terms beside Chinese from day one.
- Tests as "a written promise the computer can check", introduced in S2 with plain `assert`, formalised with pytest in S3.
- One explicit lesson on how to work with the AI tutor (which requests help learning, which replace it), using the six interaction patterns from the Anthropic trial.

Postpone
- Architecture patterns, microservices, infrastructure-as-code, container orchestration, algorithm drills, agent orchestration.
- The five DORA metrics until S8 (they describe teams and services, not a learner's exercises).

Add (missing from the plan)
- Threads from S1: AI collaboration, English reading (5-10 terms per lesson, one page of official documentation per stage, growing), estimate-versus-actual, three-line postmortems.
- Lessons: debugging method (S2), code reading and review with seeded defects (S2-S3), semantic HTML and accessibility basics (S4), query performance and N+1 (S5), Core Web Vitals (S6: LCP at most 2.5 s, INP at most 200 ms, CLS at most 0.1 at the 75th percentile [source: web.dev/articles/vitals]), personal data and data minimisation with the Chinese legal names (S5, S7), licences (S1 when the first repository is created, S3 for dependencies), professional ethics (S9).
- WCAG 2.2 is the current W3C Recommendation (edition dated 12 Dec 2024; four principles: perceivable, operable, understandable, robust; levels A/AA/AAA) [source: w3.org/TR/WCAG22]; teach the idea and three checks, not the whole standard.

Sensible defaults
- Level vocabulary: L0 未入门, L1 入门·跟着做, L2 上手·小事独立, L3 胜任·独立负责, L4 熟练·能带人.
- Evidence types: 做 (a passing auto-check), 讲 (an explain-back answer in the handbook), 证 (a commit, PR or document).
- A stage is complete when its primary areas reach the stage's stated level with evidence, not when the lessons have been read.
- Keep the probe and the map as separate tools: the probe inspects a repository, the map records a person.

## 11. Not verified or uncertain

- Whether the SWEBOK "v4.0a" file of August 2026 differs in content from the v4.0a that search results date to September 2025; I only read the file served today.
- SWECOM's level names and its 13 skill areas (primary page returned 403).
- The July 2026 Veracode report (56% pass rate, per press coverage); I read only the spring 2026 blog post (55%).
- The Lee et al. CHI 2025 and Prather et al. ICER 2024 findings come from search summaries, not from the papers.
- Stack Overflow 2025 total respondents (about 49,000) and survey dates [memory]; the AI question had 33,662 responses [source].
- The count of 147 SFIA skills and "26 skills added in SFIA 9" were reported by the fetch tool's reading of the pages; not hand-counted.
- The Chinese standard was read from a college mirror; edition and content match its own title page, but I did not reach mohrss.gov.cn.
- Dreyfus stage names used as an anchor for L1 [memory]. European Accessibility Act dates, PIPL effective date [memory].
- The level statements, the mapping of L0-L4 to SFIA/UK/Dropbox/国标 levels, the target profile and the P/s matrix are synthesis and have not been validated with learners or employers.
- Chinese book titles for the three cited books: only 《Google软件工程》(中国电力出版社) was seen today, and only in a search summary.

## 12. Files in this scratch directory

Root: `<scratch>/research/skill-model/`

- `brief.md` (this file), `brief.src.md` and `build_brief.py` (regenerate the command outputs embedded above).
- `skillmap/skillmap.toml` (the model as data), `skillmap/skillmap.py` (`validate`, `matrix`, `render`, `assess FILE`), `skillmap/self_assessment.example.toml`.
- `probe/norms_probe.py`, `probe/make_demo_repos.sh`, `probe/demo/hobby`, `probe/demo/pro`, `probe/demo-vcs/work` (the repository behind the Git checks in 3.3).
- `tools/pdf_extract.py`, `tools/pdf_meta.py`, `tools/roadmap_nodes.py`, `tools/roadmap_themes.py`.
- `downloads/` (DORA 2024 and 2025 PDFs, SWEBOK v4.0a PDF, four roadmap.sh JSON files, the Chinese standard PDF, the archived progression.fyi page) and `extracted/` (their text). These are third-party copyrighted documents kept only for reference; do not redistribute them in the course.
