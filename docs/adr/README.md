# 决策记录（ADR）

> **约束力**：参考（适用范围：本课程；现在会读、会查就够了）｜ **规则类型**：惯例·事实标准 ｜ **谁说的**：Michael Nygard《Documenting Architecture Decisions》，2011-11-15，https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions ；模板用 MADR 4.0.0，2024-09-17 发布，是现行最新版，https://adr.github.io/madr/ ｜ **核对日期**：2026-11-19

1. 架构决策记录（Architecture Decision Record，缩写 ADR）是一页左右的备忘：当时遇到什么问题，考虑过哪些方案，选了哪个，为什么，代价是什么。
2. 一篇只记一个决定，而且只记定了以后很难反悔的那种，比如先学哪门语言、代码放在哪里。随手能改的小事不写。
3. 团队为什么留它：后来的人看到一个不明白的旧决定，只有两条路，盲目照办，或者盲目推翻。写下理由，这两条路都可以不走。这是 Nygard 那篇文章的出发点。
4. 你为什么用得上：这门课替你做了一些选择。你有权知道理由，也有权推翻。隔几个月回来，你和导师都能在这里查到当初为什么这样定。
5. 它是哪一类规范：惯例·事实标准。没有法律或平台强制你写。它由 2011 年那篇文章提出，之后在业内流传开；例如亚马逊云（AWS）的官方指南里就有一套 ADR 流程（https://docs.aws.amazon.com/zh_cn/prescriptive-guidance/latest/architectural-decision-records/adr-process.html ，2026-11-19 核实）。
6. 规矩一：按顺序编号，用过的编号不再用。文件名的样子是 `0001-staged-delivery.md`：四位编号，加上英文小写、用短横线连接的标题。
7. 规矩二：已采纳的记录不再改正文。想法变了，就新写一篇，把旧的状态改成“已被取代”，旧的仍然留着。常见的状态有：已提议、已采纳、已拒绝、已弃用、已被取代。
8. 每篇的结构来自 MADR 模板，对应关系是：背景和要回答的问题（Context and Problem Statement）、考虑过的方案（Considered Options）、决定（Decision Outcome）、后果（Consequences）。最后一节“技术清单”放证据和出处（More Information），里面的术语现在看不懂没关系。
9. 本文件夹里属于规范·本课程约定的部分：文件夹叫 `docs/adr`（MADR 建议的是 `docs/decisions`）；小标题用中文；每篇不超过 40 行；状态和日期写在标题下面一行，写法和本课程的课文、规则卡一致。MADR 把它们放在文件最开头的一个标签块里，并注明那一块可选。
10. 这八篇记的是这门课的设计决定，由建课的 Claude 起草。文中的“评审”，指建课前五个互不知情的 AI 给第 1 版设计挑的错：可建造性、零基础视角、资深工程师、教学设计、失败预演（假设半年后失败，倒推原因）。调研简报在 `docs/research/`；五份模拟评审的原文没有公开。

## 索引

| 编号 | 决定 | 状态 | 日期 |
|---|---|---|---|
| [0001](0001-staged-delivery.md) | 分批交付：地图现在给全，课程学到哪建到哪 | 已采纳 | 2026-11-19 |
| [0002](0002-python-first-javascript-later.md) | 先学 Python，再学 JavaScript 和 TypeScript | 已采纳 | 2026-11-19 |
| [0003](0003-stage-order.md) | 阶段顺序：先数据和后端，再现代前端；网页在阶段 1 先上线一次 | 已采纳 | 2026-11-19 |
| [0004](0004-code-outside-cloud-synced-folders.md) | 代码放在 `~/Developer`，不放进网盘同步的文件夹 | 已采纳 | 2026-11-19 |
| [0005](0005-finished-rule-cards-restated-by-learner.md) | 手册给成品规则卡，同时要求你用自己的话再写一遍 | 已采纳 | 2026-11-19 |
| [0006](0006-tutor-contract.md) | 导师规则：三种模式，严格程度你来定，求助不是终点 | 已采纳 | 2026-11-19 |
| [0007](0007-stdlib-only-tools-python-3-9-to-3-14.md) | 学习工具只用 Python 标准库，并且在 Python 3.9 到 3.14 上都能运行 | 已采纳 | 2026-11-19 |
| [0008](0008-github-as-remote-platform.md) | 远程平台用 GitHub，用不了时有后备做法 | 已采纳 | 2026-11-19 |
