# 核实记录

> **核对日期** 2026-11-19 ｜ 回到[路线图](../../ROADMAP.md)

路线图和它的几页附页里的小时数、版本号、百分比和说法，出处都在这一页。

“今天打开”指写这份文件时直接打开了原始出处。“经调研简报”指数字取自建课调研的简报，简报注明了它当天读过的出处。简报的整理版在 `docs/research/`；五份模拟设计评审的原文没有公开。

文中的“资深评审”，指建课前给第 1 版设计挑错的五个 AI 评审之一：它扮演一位资深全栈工程师。另外四个分别从可建造性、零基础视角、教学设计、失败预演（假设半年后失败，倒推原因）的角度挑错。这些都是 AI 在检查 AI，不是真人的意见。

## 时间与节奏

| 数字 | 出处 | 怎么核实的 |
|---|---|---|
| 阶段 2～11 的规划用时、每周 5 / 10 / 20 小时的日历表（阶段 2 以后的格子）、每周 8～10 小时分三次的建议 | [设计文档](../design/2026-11-19-fullstack-learning-workspace-design.md)第 5.5 节 | 照抄 |
| 累计小时：8.5、45、195～245、255～335、305～405、385～515、465～635、645～875、745～1,015、845～1,155、885～1,215、1,035～1,465；合计约 1,035～1,465 小时 | 阶段 0、1 取工具算出的数（`python3 tools/dev/build_reference.py`），阶段 2～11 取设计文档第 5.5 节 | 本页计算（2026-11-20）。阶段 0、1 合起来是 8.5 + 36.5 = 45 小时（两个阶段各自按半小时取整后相加；不取整是 524 + 2,201 = 2,725 分钟，约 45.4 小时）。阶段 2 以后的规划值本来就是整十小时的估计；45 是整数，累计时没有半小时要舍去，例如 45 + 150 = 195。合计就是阶段 11 的累计：1,035～1,465 |
| 日历表里偏短的几格：每周 5 小时学到阶段 9 是 3.25～4.4 年（表里写“3 年多”）；每周 10 小时学到阶段 9 最长约 2.2 年（表里写“1 年半～2 年”）；每周 20 小时学到阶段 3 最长约 3.9 个月（表里写“约 3 个月”）、学到阶段 9 最长约 13 个月（表里写“10 个月～1 年”）；学完阶段 0～1：45 ÷ 5 = 9 周、45 ÷ 10 = 4.5 周、45 ÷ 20 ≈ 2.3 周 | 845～1,155 ÷ 260；1,155 ÷ 520；335 ÷ 20 ÷ 4.33；1,155 ÷ 20 ÷ 4.33；45 ÷ 每周小时数 | 本页计算（2026-11-20）。阶段 2 以后的格子照设计文档原样保留，路线图在表下说明 |
| “下周、第 3 个月、第 12 个月”学到哪里 | 每周小时数 × 周数，对照累计小时 | 本页计算 |
| 阶段 0 有 12 站，阶段 1 有 40 站（八课两站、八课三站）；按 G5a 算出每站分钟，阶段 0 约 8.5 小时、阶段 1 约 36.5 小时（站、收尾、关卡和讲解题，加 15% 复习；每课收尾的分钟也按 G5a 算，不加失败的 3 分钟；学习者要读的每一行输出都算，课文里没印出来的也算，例如 journal 的 5 个提问和 2 行结果；检查打印的结果算在检查的 1 分钟里） | [建课计划](../plans/2026-11-19-batch-1-plan.md)第 4 节、G5a | 工具从各课 META 算出（2026-11-20） |
| 第 1 版估计 800～1,100 小时；资深评审认为实际约是它的 1.3～1.5 倍，并给了逐阶段估计 | 设计文档的估计（依据一份没有公开的 AI 评审，不是测量）：800～1,100 小时和“评审认为原估计偏乐观”见设计文档第 0 节，逐阶段规划用时见第 5.5 节 | 照抄设计文档。1.3～1.5 倍和逐阶段估计出自那份评审，评审没有公开，读者没法核对。阶段 2、3 和 6～11 的规划用时采用了它的估计；数据和后端两个阶段例外：它估计合计 150～200 小时，设计文档定的是 130～180。这些估计是 AI 评审按经验给的，不是测量 |
| 资深评审的整体规划区间 1,200～1,600 小时；阶段 1 估 35～45 小时；每周 8～10 小时、至少分三次 | 设计文档的估计（依据一份没有公开的 AI 评审，不是测量）：每周 8～10 小时、至少分三次见设计文档第 5.5 节 | 照抄设计文档。1,200～1,600 小时和 35～45 小时只出现在那份评审里，没有写进设计文档，读者没法核对；路线图没有用这两个数 |
| 一次复习最多 8 道题或 10 分钟；隔十天以上建议回归流程；学到七成时提醒 | 建课计划 I4 | 读原文 |

## 别的课程公开的数字

| 课程 | 它自己公开的说法 | 出处 | 怎么核实的 |
|---|---|---|---|
| freeCodeCamp 全栈课程 | 6 个各约 300 小时的认证，再加一个全栈结业认证，合计约 1,800 小时 | https://www.freecodecamp.org/news/introducing-freecodecamp-checkpoint-certifications/ （2025-09-18 发布） | 今天打开 |
| Launch School 核心课程（每月 199 美元，预备课免费；靠考核过关） | 8～16 个月以上，约 1,200～1,800 小时以上；之后还有 4～7 个月以上的结业项目；建议每周至少 15 小时，每周 10 小时可以但慢得多 | https://public.launchschool.com/employers 、https://public.launchschool.com/faq | 今天打开。调研简报引用的 https://launchschool.com/courses 今天返回“找不到页面” |
| boot.dev 后端路线（免费账号只能读内容，做题要付费会员） | 多数学员业余学习约 12 个月 | https://www.boot.dev/ | 今天打开 |
| 100Devs | 30 周，每周 20 小时以上，合 600 小时起；它的网站同时写着“从新手到能就业要一年以上” | https://100devs.org/about | 今天打开；600 小时是 30 × 20 |
| roadmap.sh 全栈路线图 | 从零开始要 6 个月到 2 年 | https://roadmap.sh/full-stack 的常见问题 | 今天打开 |
| The Odin Project | 明说没有办法估计 | https://www.theodinproject.com/faq | 今天打开 |
| Full Stack Open | 每一部分约一周、15～20 小时；它要求先会编程，并说这种熟练度通常要至少 100～200 小时的练习 | https://fullstackopen.com/en/part0/general_info | 今天打开 |
| 哈佛 CS50x | 每周的习题要 10～20 小时 | https://cs50.harvard.edu/x/faqs/ | 今天打开 |
| 建课调研的综合估计 | 约 1,150～1,770 小时 | 调研简报 fullstack-curricula 第 8 节 | 经调研简报；是简报作者的综合，不是测量 |

学习者的实际情况：JetBrains 2024 年对计算机学习者的调查里，38% 的人每周学 3～8 小时，20% 的人每周学 9～16 小时。同一份调查里，64% 的人中途放弃过一门课，最常见的三个原因是内容没意思（51%）、时间和负担（45%）、动手练习太少（30%）。出处：JetBrains《Computer Science Learning Curve Survey 2024》，https://lp.jetbrains.com/cs-learning-curve-report-2024/ ，今天打开。

## AI 与学习

| 数字 | 出处 | 怎么核实的 |
|---|---|---|
| 52 人；50% 对 67%；调试题差距最大；约两分钟、不显著；按用法分组：只问概念的 7 人约 65%，整个交出去的 4 人约 39% | Anthropic，《How AI assistance impacts the formation of coding skills》，2026-01-29，https://www.anthropic.com/research/AI-assistance-coding-skills | 今天打开。页面上“低于 40%”指三种得分低的用法合起来，不是单指整个交出去的那一组 |
| 近千名高中生；48%、127%、17% | Bastani 等，《Generative AI without guardrails can harm learning》，PNAS 122(26)，2025；摘要见 https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html | 今天打开摘要 |
| 9.6% 原样使用、76.5% 先在本机运行（13,162 人作答） | Stack Overflow Developer Survey 2026，https://survey.stackoverflow.co/2026/ai/data | 今天打开 |
| “先读后写”有一项中学课堂上的准实验研究支持 | Sentance 等，Computer Science Education 29(2-3)，2019：约 500 名 11～14 岁学生，十节课，对照组不是随机分的，只做了学后测试 | 经调研简报 beginner-programming-pedagogy 第 2.1 节 |

## 求职

| 数字 | 出处 | 怎么核实的 |
|---|---|---|
| 入门岗位 4.5%、资深岗位 69.3%（美国，2026 年第一季度，软件开发类） | Indeed Hiring Lab，2026-07-23，https://hiringlab.indeed.com/2026/07/23/the-labor-market-is-tilting-toward-seniority/ | 今天打开 |
| 中国开发者 60% 以 Java 为主要语言，全球 28% | JetBrains Research，2026 年 1 月，https://blog.jetbrains.com/research/2026/01/insights-into-china-s-developer-landscape-key-trends/ | 今天打开。一份二手摘要写的是 58.17%，原文写 60% |
| 岗位期望（招聘方对新人的普遍期望）的列表 | 调研简报 standards-landscape 第 5 节（Dropbox IC1、SFIA 9 第 2 级、Google Engineering Practices 等） | 经调研简报；简报说明这些数据都来自美国，没有找到中文市场的同类分析 |
| 进阶阅读“建议每门花 100～200 小时” | Teach Yourself Computer Science，https://teachyourselfcs.com/ （原话是 “Aim for 100-200 hours of study of each topic”） | 今天打开 |

## 本领地图

| 内容 | 出处 | 怎么核实的 |
|---|---|---|
| 12 块本领的来历；四级的含义；二十行、几十行这类刻度；全程目标 | 资深评审第 18 条（没有公开）；调研简报 skill-model 第 3 节 | 读调研简报 skill-model；资深评审没有公开，读者没法核对。四级刻度沿用第 1 版设计文档，第 1 版没有保存在工作区。刻度和目标是调研的归纳，没有在学习者或雇主那里验证过 |
| 这 12 块怎样改出来 | 资深评审第 18 条（没有公开） | 在第 1 版的基础上：新增“调试与读代码”；“项目与团队管理”扩成“需求、沟通与项目管理”并点出四样小本领；“计算机与网络基础”加宽了范围；无障碍、性能、接口设计、数据建模、可观测性、隐私、许可证各自写明了住在哪一块。评审要求总数仍是 12 块，所以“后端”和“数据”并成了一块；并哪两块是路线图定的，评审没有说 |
| 全程目标属于规范·本课程约定 | 建课计划 G3 的判断法 | 本页判断 |
| 调研简报 skill-model 主张 14 块、5 级；课程保留 12 块、4 级 | 调研简报 skill-model；[`docs/curriculum-spine.md`](../curriculum-spine.md) 第 12 节 | 经调研简报 |

## 对标和其他

| 内容 | 出处 | 怎么核实的 |
|---|---|---|
| 各阶段页面上的全部对标网址 | 各网址 | 今天逐个打开，都返回正常页面 |
| 赫尔辛基大学 Python MOOC 2026 版开到 2026 年底 | https://programming-26.mooc.fi/ （“The course will be open until the end of the year 2026.”） | 今天打开 |
| FastAPI 中文教程由 AI 在人的引导下翻译，页面提醒可能有误 | https://fastapi.tiangolo.com/zh/tutorial/ 页首的翻译说明 | 今天打开 |
| OWASP ASVS 5.0.0 有官方简体中文 PDF | https://asvs.owasp.org/downloads/ | 今天打开；调研简报 web-security-2026 第 0 节也记着 |
| OWASP Top 10:2025 的简体中文页网址写着 zh-Hant | https://top10.owasp.org/2025/zh-Hant/ | 经调研简报 web-security-2026；事实核查 2026-11-19 确认：正文是简体字，站点菜单标为「简体中文」，`/2025/zh-Hans/` 返回 404 |
| 选修分支技术清单里的网址 | 各网址 | 今天逐个打开。《Hello 算法》的网站对自动访问返回“请求太多”，所以改列它的代码仓库 |
| 原理小课每次十几分钟 | 调研简报 cs-fundamentals 第 0 节（原文是 10～20 分钟） | 经调研简报 |
| 薄片“几十行” | 调研简报 fullstack-curricula：34 行程序、14 行模板、21 行测试，当天在建课用的电脑上跑通 | 经调研简报 |
| 一次改动约两百行以内 | 《Software Engineering at Google》讲代码评审的第 9 章（“about 200 lines of code”） | 经调研简报 skill-model；事实核查今天打开过原文 |
| 看板上同时在做的不超过两件 | 调研简报 project-mgmt-norms 第 6 节的建议默认值 | 经调研简报 |
| 阶段 0～8 不需要额外花钱；阶段 9 有免费方案 | 设计文档第 6 节 | 照抄 |
| 2026 年有几家平台取消或改动了免费档；有的平台要绑卡 | 调研简报 delivery-ops-2026 第 2 节 | 经调研简报 |
| 《网络安全法》禁止非法侵入他人网络 | 调研简报 web-security-2026 第 11 节，引 2016 年文本第二十七条 | 经调研简报。2025 年修正后条号有变，调研没有核实新条号 |
| 第 0 课小程序第一次运行时显示的那一行 | `starter/hello-fx/convert.py` | 今天在建课环境里运行 |

## 规则类型

| 内容 | 出处 | 怎么核实的 |
|---|---|---|
| 约束力和七种规则类型、岗位期望、个人偏好、判断顺序 | 建课计划 G3（2026-11-19 修订）；调研简报 standards-landscape 第 3、5 节；设计文档第 5.3 节 | 读原文 |
| 阶段 0～1 每条规范的规则类型 | 各课的规则卡片（`rules.md`）：按[规范地图](../../STANDARDS.md)第 2 节的七步判断法，从每条规范的出处判断；建课计划第 4 节方括号里的大类只是建课前的提示 | 2026-11-20 复核全部 30 张卡片后定稿，卡片为准：比如 WS-02 是规范·组织，REMOTE-01 是惯例·平台与工具 |
| 《个人信息保护法》第六条（最小范围）、第四十五条（查阅、复制）、第四十七条（删除）、第五十五条（事前做个人信息保护影响评估的几种情形） | https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm | 今天打开 |
| Chrome 默认在打开没加密的公开网站前先提醒 | Google 2026-10-21 公告 https://blog.google/security/chrome-now-warns-before-insecure-http-connections/ | 经调研简报 cs-fundamentals 第 5 节 |
| GitHub 对贡献代码的账号强制双重验证 | GitHub Docs “About mandatory two-factor authentication” | 经调研简报 standards-landscape；事实核查今天打开过 |

## 技术清单（现在看不懂没关系）

版本：

| 内容 | 出处 | 怎么核实的 |
|---|---|---|
| macOS 27.2.1、zsh 5.9、Python 3.14.9、Git 2.54.0、VS Code 1.145.2、Homebrew 7.0.10、uv 0.13.5、ruff 0.17.2、Node 26.12.0、npm 11.20.0、sqlite3 3.54；没装 gh | 建课计划 G7（在建课时核对课文用的那台 Mac 的终端里核实）；[`docs/environment-baseline.md`](../environment-baseline.md) | 读原文 |
| Python 最新稳定版 3.15.2；3.14 仍在修缺陷的维护期 | https://www.python.org/downloads/ | 今天打开 |
| PostgreSQL 19.0 于 2026-11-19 发布，是现行版本；18 仍受支持，18 系最新 18.7 | https://www.postgresql.org/versions.json 、https://www.postgresql.org/ | 今天打开（发布公告已上首页）。路线图草稿当天早些时候写的“19 在发布候选阶段”已经过时 |
| pytest 9.2.0、pytest-cov 7.1.0、mypy 2.4.1、pre-commit 4.7.0、GNU Make 3.81；ruff 最新 0.17.5、0.16.0 起默认约 400 条规则（准确数是 413） | 调研简报 quality-tooling、security-config-logging | 经调研简报；事实核查今天在 PyPI 上对过 |
| FastAPI 0.165.0、Pydantic 2、SQLAlchemy 2.1、Alembic 1.20、psycopg 3、`app.frontend()`；FastAPI 生成 OpenAPI 3.1，规范现行是 3.2.1（2026-09-10） | 调研简报 backend-data-stack-2026、standards-landscape | 经调研简报 |
| Node.js 26 LTS、Vite 8、TypeScript 7、React 19、React Router 8、TanStack Query 5、zod 4、Vitest 5、Oxlint；2026 年 6 到 11 月间的变动 | 调研简报 frontend-stack-2026 | 经调研简报 |
| Compose v5；免费档在 2026 年的变动；平台建议 | 调研简报 delivery-ops-2026 | 经调研简报 |
| OWASP Top 10 现行是 2025 版；ASVS 5.0.0；NIST SP 800-63B-4；《个人信息保护法》 | 调研简报 web-security-2026；https://top10.owasp.org/2025/ 、https://asvs.owasp.org/ 、https://csrc.nist.gov/pubs/sp/800/63/b/4/final 、https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm | 经调研简报；四个网址今天能打开 |
| Conventional Commits 1.0.0、SemVer 2.0.0、Keep a Changelog 1.1.0、MADR 4.0.0（2024-09-17）、Scrum Guide 2020、Kanban Guide 2025 年 5 月版、Contributor Covenant 3.0 | 调研简报 git-norms、project-mgmt-norms | 经调研简报；前三个的中文页和 Scrum 指南中文版今天能打开 |

旧教程和平台的事实：

| 内容 | 出处 | 怎么核实的 |
|---|---|---|
| 《Pro Git》中文版仍教 `git checkout -- 文件` 和 `git reset HEAD 文件`，主线叫 `master` | 调研简报 git-norms 第 1 节 | 经调研简报；事实核查今天打开第 2.4 节确认 |
| Full Stack Open 中文版落后；The Twelve-Factor App 正文自 2017 年未改 | 调研简报 fullstack-curricula、security-config-logging | 经调研简报 |
| ruff“规则全开”（`ALL`）多半是噪音 | Ruff 官方文档《The Ruff Linter》的“Rule selection”一节：“Use `ALL` with discretion”，并建议先开一小组规则、一次加一组；同一页讲规则分类时说 security 类“can be quite noisy”。https://docs.astral.sh/ruff/linter/ 。中文文本里的全角标点会被 RUF001～RUF003 当成容易混淆的字符报出来（规则页自己的例子就是一个全角括号）：https://docs.astral.sh/ruff/rules/ambiguous-unicode-character-docstring/ | 2026-11-20 打开。官方文档只说要慎用、哪几类噪音大，没有给比例；“多半”是课程的归纳，没有在公开项目上测量 |
| 证书有效期逐步缩短 | 调研简报 cs-fundamentals 第 5 节（引 CA/Browser Forum 的 SC-081v3 决议） | 经调研简报 |
| 免费个人账号在私有仓库里没法强制分支保护；GitHub Pages 在免费账号下只对公开仓库开放 | 调研简报 github-collab-ci 第 1 节、delivery-ops-2026 第 2 节 | 经调研简报 |
| `uv audit` 仍标为实验性；`astral-sh/setup-uv` 不再提供只写大版本的标签 | 调研简报 security-config-logging 第 1 节、github-collab-ci 第 1 节 | 经调研简报 |
| 2026 年 6 月到 11 月间，前端默认的检查工具、TypeScript、路由和测试工具都换了大版本 | 调研简报 frontend-stack-2026 第 9 节 | 经调研简报 |
