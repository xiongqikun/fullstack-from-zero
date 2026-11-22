这个阶段的课文还没有建。学到上一阶段七成时，对导师说“准备阶段 10”。

# 阶段 10：团队协作与项目管理

> **规划用时** 40～60 小时 ｜ **前置** 阶段 9 ｜ **核实日期** 2026-11-19 ｜ 回到[路线图](../../ROADMAP.md)

下面是计划，建这个阶段时会按你的真实进度和当时的工具重新定。

## 目标

学会在团队里做事：需求怎么来，任务怎么分，改动怎么评审，版本怎么发，出了事怎么复盘。你是一个人学，团队由 AI 队友和事先准备好的任务清单来模拟。

## 作品

在已经上线的看板上，按团队流程完成一轮完整的迭代（一个固定周期里完成的一批工作，比如两周）。

具体是这样一串事：任务清单里有一条说不清的需求，比如“看板要能提醒我”；你先问清楚、写成带完成标准的任务；AI 队友提交改动，你来评审，至少退回一次并写明理由；中间处理一个缺陷报告和一次故障；最后发布新版本，写一份进度报告，开一次复盘。这一串事都留下记录。

## 这个阶段会学到的规范（计划）

表里只标规则类型，而且是计划；约束力、谁说的、核对日期在建这个阶段时定，写在每条规范的卡片上。

| 规范 | 规则类型 |
|---|---|
| 固定周期、周期目标、周期末的评审和复盘（《Scrum 指南》2020 版，一份公开的团队工作方法说明） | 惯例·事实标准 |
| 任务上看板，同时在做的事有上限（《看板指南》2025 年 5 月版） | 惯例·事实标准 |
| “完成的定义”全队一致 | 惯例·事实标准（《Scrum 指南》） |
| 评审的标准：改动确实让代码更健康就放行，不求完美 | 规范·组织（谷歌公开的工程实践） |
| 一次改动要小，大约两百行以内 | 规范·组织（《Software Engineering at Google》讲代码评审的一章） |
| 主线受保护：检查没过、没人评审就合不进去 | 规范·团队约定 |
| 仓库备齐协作文件：怎么参与、谁负责哪块、行为准则、安全问题怎么报 | 惯例·平台与工具（GitHub 官方文档） |
| AI 队友的改动走同样的评审，提交如实署名 | 规范·组织（一些大型开源项目的公开规定） |
| 估算带范围，要延期提前说；定期写进度报告 | 岗位期望（招聘方和团队对新人的普遍期望，不是法律义务） |

## 过关方式

一轮迭代的全部痕迹都在：需求、任务、评审记录、发布说明、复盘；其中至少退回过一次 AI 队友的改动并写明理由。建议在这里找一位真人工程师评审你的一个改动。

## 前置

阶段 9。迭代的对象是那个在线的看板。

## 规划用时

40～60 小时。

## 对标

| 对标 | 语言 | 网址 | 和本课程的差别 |
|---|---|---|---|
| 《Scrum 指南》2020 版 | 中文（官方译本） | https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Chinese-Simplified.pdf | 它讲的是团队；一个人只能借用其中几样做法 |
| 《Software Engineering at Google》（谷歌工程师写的软件工程书） | 英文（全书免费网页版） | https://abseil.io/resources/swe-book/html/toc.html | 讲的是超大公司的做法；本课程读讲评审、测试、文档的几章 |

网址都在 2026-11-19 打开过。

## 技术清单（现在看不懂没关系）

- GitHub Issues、议题表单、合并请求模板、里程碑、Projects 看板。
- `CONTRIBUTING.md`、`CODEOWNERS`、`SECURITY.md`、行为准则（Contributor Covenant 3.0）。
- 分支保护与规则集。注意：免费的个人账号在私有仓库里没法强制执行这些规则，公开仓库可以。
- 评审：Google Engineering Practices、Conventional Comments；用 SSH 密钥给提交签名。
- 流程词汇：Scrum Guide 2020 的三个工件和各自的承诺；Kanban Guide 的 WIP 与流动指标；user story、story point、velocity 只认识，不操练。
- 估算与周报；技术债清单与风险清单；事故演练与 blameless postmortem。
- 给开源项目提一次小改动可以放在这里做，见[选修分支](../../docs/roadmap/electives.md)。
- 规则类型的出处：scrumguides.org；kanbanguides.org；Google Engineering Practices（The Standard of Code Review）；《Software Engineering at Google》Code Review 一章（“about 200 lines of code”）；GitHub Docs 关于 community health files；Linux 内核 coding-assistants 规则、Apache 的 generative tooling 指引；岗位期望见 `standards-landscape` 调研简报第 5.2 节第 1 条（Dropbox IC1、SFIA 9 第 2 级）。
- 关卡编号（暂定）：`gate-10`。
