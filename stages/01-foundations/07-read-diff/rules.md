### GIT-03 提交前先看改了什么

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：每次 `git commit` 之前，先运行 `git status` 看有哪些文件，再运行 `git diff --staged`，把这次要提交的改动一行一行看一遍。
- **谁说的**：《Pro Git》第 2 版英文版（Git 官方网站上的书）2.2 节「Viewing Your Staged and Unstaged Changes」，说 `git diff`（带或不带 `--staged`）最常用来回答“改了什么还没暂存”和“暂存了什么、马上要提交” https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository （中文版：https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库 ）；同一本书 5.2 节「Commit Guidelines」还建议提交前运行 `git diff --check`，查出多余的空白（这是另一项检查，本课不练） https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project ；git-diff 手册（网页版标注最近更新于 Git 2.56.0；建课时核对用的 Git 2.54.0 自带的手册这一处说法相同）说明 `--staged` 和 `--cached` 同义 https://git-scm.com/docs/git-diff 。分清两件事：提交前用这两条命令看清“暂存了什么、马上要提交”，是 Pro Git 教的 Git 用法，所以规则类型按七步判断法第 4 步是惯例·平台与工具；Pro Git 没有要求“每一次提交前都必须看”，这一点只决定约束力：对所有项目是推荐，本课程的练习里每次都看，是必须（适用范围：本课程）。
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 Git 大版本变化（比如 Git 3.0 发布）时
- **谁来管**：没有人：Git 不会拦你，这门课的检查也不查这一步，靠你自己的习惯；**不遵守的后果**：误删的内容、调试用的临时改动会跟着存进历史，事后只能一个提交一个提交地翻出来。
- **为什么**：提交存的是暂存区里的东西，不是你记得自己改过的东西。`git status` 只告诉你哪些文件变了，`git diff --staged` 才告诉你每个文件里具体哪一行变了。提交之前看一眼只要几秒钟；提交以后再发现，就要在历史里找。
- **正例**：

      git status
      git diff --staged
      git commit -m "改了标题的颜色"

- **反例**：改完直接 `git add .`（第 1.6 课说过：点是“当前文件夹里的一切”），接着 `git commit -m "小改动"`，从头到尾没看过改了哪些行。
- **怎么检查**：复习题 1.7-r1；人工检查：每次敲 `git commit` 之前，终端里最近的一条命令应该是 `git diff --staged`。
- **例外**：无。改动很大、一屏看不完时也不跳过：先用 `git status` 看文件清单，再按文件逐个看。
- **旧教程提醒**：老资料常写 `git diff --cached`，它和 `--staged` 完全一样，两种都对；`--staged` 是 Git 1.6.1 加上的好记的别名。
- **学于**：1.7
