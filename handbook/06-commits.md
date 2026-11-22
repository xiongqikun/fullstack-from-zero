# 提交

提交是你以后查找、比较、撤回改动的单位。一次提交装了几件不相干的事，说明就写不清，撤回时还会把好的改动一起撤掉。这一类规则规定一次提交装什么、第一行说明怎么写，让人和工具都读得懂历史。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（2 张）

### COMMIT-01 提交说明遵循 Conventional Commits

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）；在用检查工具强制执行它的团队里是必须（适用范围：所在团队）
- **规则类型**：惯例·事实标准
- **规则**：提交说明的第一行写成「类型: 描述」或「类型(范围): 描述」：类型是下面清单里的英文小写词，冒号用英文半角，冒号后面正好一个空格，描述可以用中文；需要多说时，空一行再写正文，讲为什么这样改。本课程认可的类型：feat、fix、docs、style、refactor、perf、test、build、ci、chore、revert。小写是 commitlint 常用配置和本课程的要求；规范本身不分大小写（第 15 条）。正好一个空格是本课程的要求；规范只写了“冒号和空格”（第 1 条）。
- **谁说的**：约定式提交（Conventional Commits）1.0.0，中文版 https://www.conventionalcommits.org/zh-hans/v1.0.0/ ，英文原文 https://www.conventionalcommits.org/en/v1.0.0/ （规范只定义了 feat 和 fix，第 14 条允许别的类型，第 15 条说各部分不区分大小写，BREAKING CHANGE 除外）；类型清单和各类型的含义来自检查工具 commitlint 的常用配置（正式名称 @commitlint/config-conventional；读的是它 2026-11-20 的程序原文，其中 type-enum 列出 11 个类型，type-case 要求小写，style 的含义是不影响代码含义的排版改动，比如空格、格式）https://github.com/conventional-changelog/commitlint/blob/master/%40commitlint/config-conventional/src/index.ts ；第一行不超过 50 个字符的建议来自 git-commit 手册 DISCUSSION 一节（网页版标注 2.55.0，到 2.56.1 没有改动；建课时核对用的 Git 2.54.0 自带的手册是同一段话）https://git-scm.com/docs/git-commit ，折合约 25 个汉字的说法来自《Pro Git》第 2 版中文版 5.2 节
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者约定式提交发布新版本时
- **谁来管**：评审人和检查工具；**不遵守的后果**：别人看历史时分不清哪条是新功能、哪条是修错；有些工具会读提交说明，自动整理出每一版改了什么，读不懂就整理不了；团队里装了 commitlint 的话，提交会直接被拦下。
- **为什么**：Git 把第一行当作这次提交的标题，`git log --oneline` 只显示这一行。开头的类型让人和工具一眼看出这次改动是哪一类。冒号和空格的写法固定，工具才能可靠地读出来。
- **正例**：

      feat: 在首页加一条学习计划
      fix(menu): 拿铁的价格改回 22 元
      docs: 添加小店的说明

      新来的店员不知道每个文件放的是什么，先写清楚。

- **反例**：

      更新
      docs： 补充说明           （全角冒号）
      fix:修正链接              （冒号后面没有空格）
      update: 调整列表          （update 不在清单里）

- **怎么检查**：`python3 tools/course.py check 1.10b`；复习题 1.10-f1、1.10-w1；人工检查：提交后运行 `git log --oneline`，看最新一行的类型、冒号和空格。
- **例外**：参与的项目已经有自己的提交说明格式，就在那个项目里按它的来，先用 `git log --oneline` 看看它的历史。比如 Git 项目习惯让第一行以「改动的地方: 」开头（https://git-scm.com/docs/SubmittingPatches ，页面标注 2.56.0，并建议对要改的文件运行 `git log --no-merges` 看现在的习惯），Go 项目要以包名开头（https://go.dev/doc/contribute ），两家都不用约定式提交的类型（2026-11-20 核对）。另外，这条规矩从本课开始：之前已经存在的旧提交不用回头去改（要改就得改写历史），写错的那一条也不用改，下一条写对就行。阶段 2 学到把两条历史线并到一起时，Git 会自动写一条说明，那种说明可以保留原样。
- **旧教程提醒**：不少中文教程把 feat、fix、docs、style、refactor、test、chore 都说成“规范规定的类型”；其实约定式提交从最早的 1.0.0-beta 版到现行的 1.0.0 版，都只定义了 feat 和 fix，其余来自 commitlint 等工具的配置（那份配置源自 Angular 项目的提交约定；Angular 是谷歌的团队维护的一套写网页用的工具）。还有教程把“第一行不超过 50 个字符”说成 Git 的硬规定；Git 手册写的是建议，2.55.0 版手册的原话是 “Though not required, it's a good idea”（不是必须的，但这是个好主意）（2026-11-20 核对）。
- **学于**：1.10

> 原文在第 1.10 课「提交规范」的 [`rules.md`](../stages/01-foundations/10-commit-conventions/rules.md)。

### COMMIT-02 一次提交一件事

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：一次提交只装一件完整的事。手头有几件不相干的改动，就分几次：每次只把属于同一件事的文件放进暂存区，然后提交。
- **谁说的**：《Pro Git》第 2 版中文版 5.2 节「提交准则」（“尝试让每一个提交成为一个逻辑上的独立变更集”）https://git-scm.com/book/zh/v2/%E5%88%86%E5%B8%83%E5%BC%8F-Git-%E5%90%91%E4%B8%80%E4%B8%AA%E9%A1%B9%E7%9B%AE%E8%B4%A1%E7%8C%AE ；GitHub Docs「GitHub flow」（每个提交最好是一个独立、完整的改动，这样容易撤回）https://docs.github.com/en/get-started/using-github/github-flow ；约定式提交 1.0.0 的常见问题：一个提交同时符合几种类型时，“回退并尽可能创建多次提交” https://www.conventionalcommits.org/zh-hans/v1.0.0/
- **核对日期**：2026-11-20；**复核周期**：12 个月
- **谁来管**：评审人；本课程里是检查 1.10a 和小关卡 gate-b 的题目；**不遵守的后果**：用 Git 的撤回命令只能连另外几件一起撤，只撤一件要多费好几步；评审的人也很难看懂这次到底改了什么。
- **为什么**：Git 的撤回命令（阶段 2 学）按一整个提交来，一个提交也只有一句说明。一个提交装三件事，三件事就绑在一起：说明写不清，出了错找不到是哪一件，撤回时会把好的改动一起撤掉。
- **正例**：

      git add menu.txt
      git commit -m "feat(menu): 加上桂花拿铁"
      git add about.txt
      git commit -m "fix(about): 改正地址的门牌号"

- **反例**：三处不相干的改动一起 `git add .`，然后 `git commit -m "更新"`。
- **怎么检查**：`python3 tools/course.py check 1.10a`；复习题 1.10-r1；人工检查：写说明时如果需要“和”“顺便”“还有”，多半应该拆成几个提交。
- **例外**：几处改动离开彼此就不成立（比如改了一个文件名，同时改掉所有引用它的地方），它们就是同一件事，放进一个提交。
- **旧教程提醒**：无
- **学于**：1.10

> 原文在第 1.10 课「提交规范」的 [`rules.md`](../stages/01-foundations/10-commit-conventions/rules.md)。
