<!-- 1.16 课的规则卡（计划 I2 的十三个字段）。出处在 2026-11-20 当天重新打开核对过。 -->

### PM-03 每个阶段结束做一次复盘

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：惯例·事实标准
- **规则**：每个阶段（或冲刺、里程碑）结束时，用记录下来的证据回看这一段：做得好的、要改的、下一步；下一步写成一件能做、能检查的事，并在下一段一开始就做。
- **谁说的**：《Scrum 指南》2020 年 11 月版（Ken Schwaber、Jeff Sutherland），“Sprint Retrospective”（回顾会）一节 https://scrumguides.org/scrum-guide.html （官方简体中文译本 https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Chinese-Simplified.pdf ；版本列表 https://scrumguides.org/revisions.html 里 2020 年版是最新的一版；2025 年起另有一份《Scrum Guide Expansion Pack》（Jeff Sutherland、John Coleman、Ralph Jocham，https://scrumexpansion.org/ ），它自称是 2020 年版指南的配套材料（companion），是补充材料，不是新版指南）；《敏捷宣言》（Agile Manifesto，2001）十二条原则的最后一条“团队定期地反思如何能提高成效，并依此调整自身的举止表现。” https://agilemanifesto.org/iso/zhchs/principles.html 。“做得好的 / 要改的 / 下一步”三个小标题和“用证据”的要求是本课程的整理方式，指南没有规定固定的问题清单。
- **核对日期**：2026-11-20；**复核周期**：24 个月，或者《Scrum 指南》出新版时
- **谁来管**：本课程里是第 1.16 课第 3 站的检查；团队里是团队自己和主持回顾的人（用 Scrum 的团队，每个冲刺结束的回顾会是指南规定的固定事件）；没有哪个机构会因为你不做而罚你；**不遵守的后果**：同样的坑下一阶段再踩一遍，计划和实际越差越远，也没人知道为什么。
- **为什么**：做完一段事，记忆很快就会把“卡了三天”美化成“还行”。趁着日志、用时、考试结果都还在，把它们摆出来看一遍，才找得到真正该改的地方。只写感想不会改变任何做法，所以复盘的产出是下一段的一个具体改动。
- **正例**：

      ## 要改的
      - 1.9 课卡了两次，都是因为没先看 git status 就动手。
      ## 下一步
      - 每次动手前先运行 git status，下周的每次学习都这样做，周日复盘时数一数做到了几次。

- **反例**：“这一阶段学得还行，下一阶段继续努力。”（没有证据，也没有能做的下一步）
- **怎么检查**：python3 tools/course.py check 1.16c；复习题 1.16-retro
- **例外**：阶段中途放弃或换方向，也要做一次简短复盘，只是“下一步”可以是“停在这里”。没有例外可以完全跳过。
- **旧教程提醒**：2017 年 11 月版《Scrum 指南》（https://scrumguides.org/scrum-guide-2017.html ）要求下一个冲刺的待办清单（Sprint Backlog，这个冲刺要做的事）里至少包含一条上次回顾会定下的高优先级改进（at least one high priority process improvement）；2020 年 11 月版改成最有影响的改进尽快去做，可以放进下一个冲刺的待办清单，不再规定条数（自 2020 年 11 月起）。
- **学于**：1.16
