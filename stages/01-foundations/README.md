# 阶段 1：工程师的基本功

> **规划用时** 约 36.5 小时（16 课，40 站）｜ **前置** 阶段 0 ｜ **核实日期** 2026-11-19 ｜ 回到[路线图](../../ROADMAP.md)

## 目标

把工程师每天都在用的四样基本功练到手熟：在终端里管文件，用编辑器（写代码和文档用的软件，本课程用的编辑器是 VS Code）写东西，用 Markdown（带简单排版记号的纯文字）写说明，用 Git（给文件夹拍“带说明的快照”的工具）给工作存档，并备份到 GitHub（存放快照备份、也能展示作品的网站）。

同时学三件护身的事：出了错怎么查，怎么求助，怎么验收 AI 的改动。

## 作品

一个你手写、放在网上、手机能打开的网页，文件夹叫 `my-site`。它是产品在网上的第一块地盘。

- 你从一个现成的起步网页改起。它有一个标题、一段话、一个列表和一个链接，标题写着“你好，我是____”。
- 横线上填什么由你定，可以是昵称，不必写真名。这个网页是公开的，谁都看得到，所以不要放手机号、住址、工作单位这类个人信息。第 1.12 课和第 1.13 课会教你公开之前怎么检查。
- 学完时你会得到一个网址，用手机浏览器打开就能看到这一页。

另外，你的学习记录变成一个有“后悔药”的仓库（被 Git 管着的文件夹）：每次改了什么都看得见，不满意能退回。它在 GitHub 上有一份只有你自己看得到的备份，并且你亲手试过能恢复。

## 课表

<!-- 生成开始：python3 tools/dev/build_reference.py，请不要手改这一段 -->
| 课 | 标题 | 各站 | 站的分钟 | 本课行规 | 课文 |
|---|---|---|---|---|---|
| 1.1 | 终端：新建与查看 | a 新建（35 分钟）；b 查看（35 分钟） | 70 | [TERM-01](../../handbook/02-terminal-safety.md#term-01-不照抄看不懂的命令) | [lesson.md](01-create-and-view/lesson.md) |
| 1.2 | 终端：复制、移动、删除 | a 复制和移动（30 分钟）；b 删除和安全（40 分钟） | 70 | [TERM-02](../../handbook/02-terminal-safety.md#term-02-删除前先看清要删什么) | [lesson.md](02-copy-move-delete/lesson.md) |
| 1.3 | 终端：查找 | a 找内容（35 分钟）；b 找文件（35 分钟） | 70 | 无 | [lesson.md](03-search/lesson.md) |
| 1.4 | 编辑器 VS Code | a 打开文件夹、编辑、保存、在浏览器里看效果（40 分钟）；b 命令面板、快速打开、搜索和内置终端（30 分钟）；c 编码、换行和 .editorconfig（40 分钟） | 110 | [ED-01](../../handbook/03-editor.md#ed-01-打开文件夹而不是单个文件)、[ED-02](../../handbook/03-editor.md#ed-02-文本统一-utf-8-和-lf用-editorconfig-说明) | [lesson.md](04-editor/lesson.md) |
| 1.5 | Markdown 与 README | a Markdown 语法（35 分钟）；b README 是项目的门面（30 分钟） | 65 | [DOC-01](../../handbook/04-documents.md#doc-01-每个项目根目录有-readmemd)、[DOC-02](../../handbook/04-documents.md#doc-02-readme-回答五个问题) | [lesson.md](05-markdown-readme/lesson.md) |
| 1.6 | Git：第一次提交 | a 为什么要版本管理，一次性设置（40 分钟）；b 第一次提交（40 分钟）；c 给 my-site 建仓库（40 分钟） | 120 | [GIT-01](../../handbook/05-git.md#git-01-一个项目一个仓库在项目根目录初始化)、[GIT-02](../../handbook/05-git.md#git-02-提交前确认身份设置) | [lesson.md](06-first-commit/lesson.md) |
| 1.7 | Git：看懂改了什么 | a 还没提交的改动：git diff 和 git diff --staged（40 分钟）；b 历史里的改动：git log --stat 和 git show（40 分钟） | 80 | [GIT-03](../../handbook/05-git.md#git-03-提交前先看改了什么) | [lesson.md](07-read-diff/lesson.md) |
| 1.8 | Git：后悔药 | a 丢掉工作区里的修改（40 分钟）；b 从暂存区拿下来，以及哪种情况用哪个（40 分钟） | 80 | [GIT-04](../../handbook/05-git.md#git-04-执行会丢数据的命令前先看状态) | [lesson.md](08-undo-uncommitted/lesson.md) |
| 1.9 | Git：什么不该进仓库 | a 给 Git 一份不拍名单（40 分钟）；b 已经进了仓库怎么办（40 分钟） | 80 | [REPO-01](../../handbook/07-repository-hygiene.md#repo-01-密钥密码令牌永不入库)、[REPO-02](../../handbook/07-repository-hygiene.md#repo-02-gitignore-从官方模板起步) | [lesson.md](09-gitignore/lesson.md) |
| 1.10 | 提交规范 | a 一次提交只做一件事（40 分钟）；b 写好提交说明（40 分钟） | 80 | [COMMIT-01](../../handbook/06-commits.md#commit-01-提交说明遵循-conventional-commits)、[COMMIT-02](../../handbook/06-commits.md#commit-02-一次提交一件事) | [lesson.md](10-commit-conventions/lesson.md) |
| 1.11 | GitHub：账号、安全与身份 | a 注册和双重验证（35 分钟）；b 让电脑认识 GitHub（35 分钟）；c 提交邮箱隐私和签名的选择（35 分钟） | 105 | [ACC-01](../../handbook/08-accounts-and-identity.md#acc-01-github-账号开启双重验证)、[ACC-02](../../handbook/08-accounts-and-identity.md#acc-02-提交邮箱用-github-的隐私地址) | [lesson.md](11-github-account/lesson.md) |
| 1.12 | 第一次推送和云端备份 | a 学习仓库入库（40 分钟）；b 推送到私有仓库（40 分钟）；c 验证备份真的能用（40 分钟） | 120 | [REMOTE-01](../../handbook/09-remotes-and-backup.md#remote-01-重要仓库在别处有第二份并且试过能恢复)、[REMOTE-02](../../handbook/09-remotes-and-backup.md#remote-02-推送或公开之前先查有没有密钥和隐私) | [lesson.md](12-push-and-backup/lesson.md) |
| 1.13 | 把你的网页放到网上 | a 公开仓库和许可证（40 分钟）；b 用 GitHub Pages 上线（40 分钟）；c 改一处、推送、看网页更新（35 分钟） | 115 | [PUB-01](../../handbook/10-publishing.md#pub-01-公开仓库三件套readmelicensegitignore) | [lesson.md](13-publish-site/lesson.md) |
| 1.14 | 排错、求助与“与时俱进” | a 排错实验室（40 分钟）；b 怎么求助（40 分钟）；c 判断一份资料是否过时（35 分钟） | 115 | [HELP-01](../../handbook/11-help-and-staying-current.md#help-01-提问给出目标做法期望实际报错原文版本)、[FRESH-01](../../handbook/11-help-and-staying-current.md#fresh-01-用一个做法前确认它的版本和日期) | [lesson.md](14-errors-help-fresh/lesson.md) |
| 1.15 | 验收 AI 的改动 | a 让 AI 干活，你来验收（40 分钟）；b 找茬：一次 AI 改动里的三处问题（40 分钟）；c 给 AI 立规矩（40 分钟） | 120 | [AI-01](../../handbook/12-working-with-ai.md#ai-01-ai-的改动先看-diff-再接受)、[AI-02](../../handbook/12-working-with-ai.md#ai-02-ai-参与的提交如实署名) | [lesson.md](15-review-ai-changes/lesson.md) |
| 1.16 | 阶段作品与验收 | a 整理作品（40 分钟）；b 阶段验收（40 分钟）；c 复盘和下一段（40 分钟） | 120 | [PM-03](../../handbook/13-managing-work.md#pm-03-每个阶段结束做一次复盘) | [lesson.md](16-stage-project-and-gate/lesson.md) |

阶段 1 一共约 36.5 小时。这个数是这样算的：40 站一共 1520 分钟，加上 16 课的收尾 255 分钟（第 1.1 课 10 分钟、第 1.2 课 15 分钟、第 1.4 课 15 分钟、第 1.5 课 15 分钟、第 1.6 课 15 分钟、第 1.7 课 10 分钟、第 1.8 课 10 分钟、第 1.9 课 15 分钟、第 1.10 课 15 分钟、第 1.11 课 15 分钟、第 1.12 课 25 分钟、第 1.13 课 20 分钟、第 1.14 课 25 分钟、第 1.15 课 25 分钟、第 1.16 课 20 分钟，其余每课 5 分钟）、小关卡 gate-a、小关卡 gate-b 和阶段验收 gate-1 一场的实操题分别约 30、29、50 分钟、讲解题各约 10 分钟，合计 1914 分钟；再加 15% 留给复习，约 2201 分钟，四舍五入到半小时。关卡的分钟是工具在开考前估的数；开考时按抽到的题重算，会差几分钟。
<!-- 生成结束 -->

每一课的文件夹里有三样东西：课文 `lesson.md`、规则卡片 `rules.md`，和给课程工具用的 `lesson.py`。

几个词先说一句，每个都在对应的那一课细讲：diff 是“改动清单”，逐行列出哪里删了、哪里加了；UTF-8 是现在通用的文字存法；LF 是换行的一种写法；`.gitignore` 是给 Git 的“不拍名单”；LICENSE 是写明别人可以怎样使用你作品的许可证文件；令牌是一种通行证：程序拿着它就能代表你去用某个网站的服务，它代替密码，可以单独作废；双重验证是登录时除了密码还要第二样凭证。

## 这个阶段会学到的规范

一共 24 条，都在上面的课表里。表里只标规则类型；约束力（必须、推荐、参考，括号里写适用范围）、谁说的和核对日期写在每条规范的卡片上，学到那一课时给出。带约束力的总表在[规范地图](../../STANDARDS.md)第 3 节。

规则类型说的是规则从哪来，分好就不再变；处境变了，变的只是约束力。比如一份合同点了 REPO-01 的名，那条合同条款对你是行业要求，REPO-01 本身还是惯例·事实标准，只是在那个项目里成了必须。

分量最重的十条是：ACC-01、REMOTE-02（行业要求：平台或法律能拿它追究你；REMOTE-02 指的是别人的个人信息）；REPO-01、COMMIT-01、ED-02（惯例·事实标准）；GIT-02、GIT-03、COMMIT-02（惯例·平台与工具）；REMOTE-01、AI-01（前一条是惯例·平台与工具，后一条是规范·组织）。REMOTE-01 在第 1.12 课第 3 站当场验证：你把学习仓库从云端克隆一份到练习场，和原件比较，检查会核对两边一样。

## 过关方式

三道关卡，每道都是单独的一段时间，开考时工具会打印题数和预计用时：

- 第 1.5 课之后：小关卡 gate-a（终端与文档关卡）。下次对导师说“做小关卡 gate-a”。
- 第 1.10 课之后：小关卡 gate-b（本地 Git 关卡）。下次对导师说“做小关卡 gate-b”。
- 第 1.16 课第 2 站：阶段验收 gate-1（阶段 1 验收）。在全新生成的情境里动手完成几道题，解决一个故障，再把“为什么这样做”讲给考官听。

每道关卡都分两部分：

- **实操题**：不给提示，题目里的名字每次随机生成。第一场每课一道：gate-a 和 gate-b 各五道（每道关卡管五课），gate-1 六道（第 1.11 到 1.16 课各一道，题里也要用到前面几课的本事）。做题时不问导师，也不用 AI。
- **讲解题**：实操题都过了，对导师说“请问我 gate-a 的讲解题”（换成你考的那道关卡）。gate-1 的讲解题也可以交给一个另开的“考官”对话来判，做法在第 1.16 课。结论出来以后，你自己运行 `python3 tools/course.py exam gate-a --explain pass` 记下来；要再讲一次，就记 `--explain again`。

关卡管的那几课，每课都有一道实操题通过，讲解题也记为通过，这道关卡就过了。没过的题，下一场换一套题面再考，只考没过的那几道。关卡不挡下一课：工具会一直显示还有什么没过。

## 前置

阶段 0。

## 规划用时

约 36.5 小时：16 课，40 站。光是站就有约 25 小时（1520 分钟），其余是每课的收尾、三次关卡和留给复习的一成半；算式在上面「课表」下面那一段，由工具按各站的分钟算出。

## 对标

| 对标 | 语言 | 网址 | 和本课程的差别 |
|---|---|---|---|
| 《Pro Git》（Git 官方网站上的免费书）第 2 版第 1、2 章 | 中文 | https://git-scm.com/book/zh/v2 | 中文版有几处旧写法，本课程教现在的写法，学到 Git 时会一一指出（细节见下面的技术清单） |
| MIT《The Missing Semester of Your CS Education》（麻省理工给学生补工具课的讲义）2026 版 | 英文；中文站 https://missing-semester-cn.github.io/ 部分译完，2026 年的课表还有一部分没翻译 | https://missing.csail.mit.edu/ | 它面向已经会编程的学生，节奏快得多 |

两个网址都在 2026-11-19 打开过。

## 技术清单（现在看不懂没关系）

- 终端：`mkdir`、`touch`、`ls -l`、`ls -a`、`cat`、`less`、`head`、`head -n`、`cp`、`cp -R`、`mv`、`rm`、`rm -i`、`rm -r`、`rmdir`、`grep -n -r -i`、`find . -name`、`which`、`diff -r -q`、`sw_vers -productVersion`；通配符和引号入门。
- 编辑器：VS Code 的 `code .`、命令面板、内置终端；`open index.html`；`.editorconfig`。
- 文档：GitHub 风格的 Markdown；`README.md`。
- Git：`git --version`；`git config` 用带子命令的写法：`git config set --global`、`git config get`、`git config unset --global`、`git config list`（Git 2.46.0 起旧写法弃用，见[规范地图](../../STANDARDS.md)第 6 节「旧教程常见的过时说法」）；`git init`、`git status`、`git add`、`git add .`、`git commit -m`、`git commit -m … -m …`、`git log --oneline`、`git log -1`、`git log --format`、`git diff`、`git diff --staged`、`git diff --stat`、`git show`、`git show --stat`、`git log --stat`、`git restore`、`git restore --staged`、`.gitignore`、`git status --ignored`、`git check-ignore -v`、`git ls-files`、`git rm --cached`、`git remote -v`、`git push`、`git clone`、`git grep`、`git <命令> -h`。四个区域：工作区、暂存区、本地历史、远程。
- 有的电脑上会碰到的一个问题：Git 打开了“每次提交都要签名”，但签名程序没装，这样任何提交都会失败。第 1.6 课教你看出来、处理掉。
- 规范文本：Conventional Commits 1.0.0；EditorConfig。
- GitHub：双重验证；命令行工具 `gh`（`brew install gh`、`gh --version`、`gh auth login`、`gh auth status`、`gh repo create`、`gh browse --settings`）；GitHub Pages；`LICENSE`。
- 课程工具：`python3 tools/course.py fresh`、`exam gate-a`、`exam gate-b`、`exam gate-1`（加 `--grade` 批改，加 `--explain pass` 记下讲解题的结论）、`review`、`scenario`。
- 建课当天核实的版本：Git 2.54.0（Apple Git-157）、Homebrew 7.0.10、VS Code 1.145.2。还没装 `gh` 的，第 1.11 课带你装。
- 《Pro Git》中文版的旧写法：它仍教 `git checkout -- 文件` 和 `git reset HEAD 文件`，并把主线叫 `master`；本课程教 `git restore`、`git restore --staged`，主线叫 `main`。
- 推迟到阶段 2 工程课的内容：分支、合并与冲突、合并请求和评审流程、`git commit --amend`、`git reflog`、管道与重定向、环境变量和 PATH（第 1.11 课只碰到安装 `gh` 需要的那一点）。
- 规则类型的判定依据：[规范地图](../../STANDARDS.md)第 2 节的七步判断法（按顺序问，遇到第一个「是」就停）；每张卡片上写着出处和核对日期。建课计划 G3（[`docs/plans/2026-11-19-batch-1-plan.md`](../../docs/plans/2026-11-19-batch-1-plan.md)）是这套标签的来源；计划第 4 节写的类型只是建课前的提示，和卡片不一致时以卡片为准。
