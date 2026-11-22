# Git

Git 只记你交给它的东西，也只按你的设置写下作者。这一类规则防的是几件提交以后才发现的事：仓库建错了地方，提交里写进了你不想公开的名字和邮箱，提交了没看过的改动，或者一条命令丢掉了还没提交的修改。这些事大多没有人会拦你，Git 执行时也不提醒，所以要在动手之前看一眼。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（4 张）

### GIT-01 一个项目一个仓库，在项目根目录初始化

- **约束力**：推荐（适用范围：所有项目）；必须（适用范围：本课程）
- **规则类型**：惯例·平台与工具
- **规则**：先 cd 进项目最外层的文件夹（项目根目录），运行 git status 确认它还不在任何仓库里（看到 not a git repository），再在这里运行 git init。标题里的“一个项目一个仓库”（不往上层建，也不在项目里面再建）是这门课对这个做法的读法，下面两份资料没有这样写。
- **谁说的**：《Pro Git》第 2 版中文版 2.1「获取 Git 仓库」（进入项目目录再 git init；2026-11-20 读取）https://git-scm.com/book/zh/v2/Git-基础-获取-Git-仓库 ；git-init 手册（git-scm.com 上的版本最后更新于 Git 2.54.0，和这台电脑的 Git 一致；2026-11-20 读取）https://git-scm.com/docs/git-init
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 Git 发布 3.0 时
- **谁来管**：所有项目里没有人管：Git 不拦你在错的那一层运行 git init；在这门课里，第 1.6 课第 3 站的检查会看 my-site 和它的上层是不是各只有一个仓库；**不遵守的后果**：建高了，几个项目的改动搅进同一段历史，备份和公开都分不开；建低了，项目里有一部分文件 Git 根本看不见。
- **为什么**：git init 在哪个文件夹里运行，就把那个文件夹连同它下面的一切交给 Git 管。在 ~/Developer 里运行，my-site、playground（学习工作区如果在 ~/Developer/fullstack-from-zero，也算在内）都会变成一个大仓库里的普通文件夹；到第 1.13 课公开网站时，你就没法只公开 my-site。在这门课里它是必须：my-site 是一个仓库，第 1.12 课起学习工作区也是一个仓库。
- **正例**：

      cd ~/Developer/my-site
      git status        # 应该看到 fatal: not a git repository，说明这里和上面都还没有仓库
      git init

- **反例**：在 ~/Developer、主文件夹 ~ 或桌面上运行 git init；在项目里面的某个子文件夹里再 git init 一次，造出“仓库套仓库”。
- **怎么检查**：在项目根目录运行 git status，第一行应该是 On branch main；在项目的上一层运行 git status，应该看到 fatal: not a git repository。复习题 1.6-r3。
- **例外**：团队明确决定把多个项目放进一个大仓库（叫 monorepo，单一大仓库）时，按团队的约定做；这是阶段 3 以后的话题，由团队决定，不由个人决定。
- **旧教程提醒**：无。进项目根目录再 git init，这个做法多年没有变。变过的是第一个分支的名字：旧教程里叫 master，GitHub 自 2020 年 10 月起新仓库默认用 main，Git 自己要到还没定日期的 3.0 才改（Git 文档 BreakingChanges，2026-11-19 核对；git-init 手册 2.54.0 版，2026-11-20 核对）；这和本条规则无关，详见第 1.6 课第 1 站末尾的「想多了解」。
- **学于**：1.6

> 原文在第 1.6 课「Git：第一次提交」的 [`rules.md`](../stages/01-foundations/06-first-commit/rules.md)。

### GIT-02 提交前确认身份设置

- **约束力**：推荐（适用范围：所有项目）；必须（适用范围：本课程）
- **规则类型**：惯例·平台与工具
- **规则**：在一台电脑上第一次提交之前，运行 git config get user.name 和 git config get user.email，确认两样都设置了，而且是你愿意公开的名字和邮箱。
- **谁说的**：《Pro Git》第 2 版中文版 1.6「初次运行 Git 前的配置」（每个提交都会写入用户名和邮箱，写入后不可更改；2026-11-20 读取，书里用的是 git config --global 这种老写法）https://git-scm.com/book/zh/v2/起步-初次运行-Git-前的配置 ；GitHub Docs「Setting your commit email address」（用 git config 设的邮箱会出现在你以后推送的提交里；换邮箱之前的提交仍然连着旧邮箱）https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address （2026-11-20 读取的版本）；GitHub Docs「Troubleshooting missing contributions」（提交要用已经加进账号的邮箱或 GitHub 给的 noreply 地址，才算在你名下；像 jane@computer.local 这样的地址加不进账号；2026-11-20 读取）https://docs.github.com/en/account-and-profile/reference/why-are-my-contributions-not-showing-up-on-my-profile ；本机实测：Git 2.54.0（Apple Git-157），身份没设置时提交照样成功
- **核对日期**：2026-11-20；**复核周期**：12 个月
- **谁来管**：所有项目里没有人管：Git 不拦你，没设身份它会自己拼一个；GitHub 也不拒收，只是不把这样的提交算在你名下。在这门课里，第 1.6 课第 1 站和第 3 站的检查会看 user.name 和 user.email 是不是都设置了；**不遵守的后果**：提交里写进一个自动拼出来的身份：你登录这台 Mac 用的全名（常常是真名），加上“用户名@电脑名.local”；公开后谁都能看到，GitHub 也认不出这是你的提交。
- **为什么**：Git 不会因为没设身份就拒绝提交。建课当天实测，它会用你登录这台 Mac 的全名和“用户名@电脑名.local”拼出一个身份，提交照样成功，只在屏幕上多印一段英文提醒，很容易看漏。写进提交的身份要改，就得另造新提交、改写历史（那段提醒提到的补救命令就是这样做的，阶段 2 才学），所以拍之前就定好；之后再改设置，只管以后的提交（GitHub Docs 同一页：换邮箱之前的提交仍然连着旧邮箱）。
- **正例**：

      git config get user.name     # 应该打印出你愿意公开的名字
      git config get user.email    # 应该打印出你愿意公开的邮箱

- **反例**：从没看过身份设置就开始提交；在提交里用了真实全名和私人邮箱，第 1.13 课公开网站时才发现。
- **怎么检查**：python3 tools/course.py doctor 的「Git 身份」一行要是“user.name 已设置，user.email 已设置”；python3 tools/course.py check 1.6a 和 check 1.6c 也会看。复习题 1.6-r4。
- **例外**：某个仓库要用别的身份（比如公司的项目），在那个仓库里用不带 --global 的 git config set 单独设置一次；这仍然是在提交前确认身份。
- **旧教程提醒**：旧教程（包括《Pro Git》中文版）和 Git 自己打印的提示写的是 git config --global user.name 这种老写法；Git 从 2.46 版（2024 年）起改用 git config get、git config set 这样的子命令，手册把老写法列为过时的写法（git-config 手册 2.56.1 版，2026-11-20 核对）。老写法还能用，这门课只用新写法。
- **学于**：1.6

> 原文在第 1.6 课「Git：第一次提交」的 [`rules.md`](../stages/01-foundations/06-first-commit/rules.md)。

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

> 原文在第 1.7 课「Git：看懂改了什么」的 [`rules.md`](../stages/01-foundations/07-read-diff/rules.md)。

### GIT-04 执行会丢数据的命令前先看状态

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：规范·本课程约定
- **规则**：运行 `git restore 文件名` 这类会丢掉没提交改动的命令之前，先运行 `git status` 看有哪些文件改了，再用 `git diff 文件名` 看清这次会丢掉的具体内容；确认以后只点名要丢的那个文件。（“文件名”换成真正的文件名。）
- **谁说的**：本课程约定（2026-11-19 定）。依据两份官方资料：Git 自带手册 git-restore（建课时核对用的 Git 2.54.0 自带的手册，手册日期 2026-04-19；网页版 https://git-scm.com/docs/git-restore ，最近一次修改在 Git 2.55.0，到 2.56.1 都没再改）说明 `git restore` 用暂存区或指定提交里的内容覆盖工作区的文件；《Pro Git》第 2 版英文版 2.4 节 “Undoing Things” https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things 明确说 `git restore <file>`（尖括号是占位写法，表示“换成文件名”，真敲时不带尖括号）是一条危险的命令，文件里的本地改动会消失。两份资料都没有规定“丢之前先看 status 和 diff”这个步骤，这一步是本课程定的。
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 Git 3.0 发布时
- **谁来管**：没有人。Git 执行时不提醒、不确认，检查器也看不到你丢之前有没有先看；**不遵守的后果**：还没放进暂存区、也没提交过的改动被直接盖掉，Git 里没有它的任何副本，找不回来。
- **为什么**：`git restore` 执行成功时什么也不打印，看不出它刚刚丢掉了什么。改动一旦被盖掉，`git diff` 里不再有，`git log` 里也从来没有过。多花十秒看一眼状态和改动清单，就能发现“这个文件里还有我想要的东西”。
- **正例**：

      git status
      git diff style.css
      git restore style.css
      git status

- **反例**：什么也不看，直接在仓库根目录运行 `git restore .`：点代表当前文件夹，这个文件夹里所有还没 `git add` 的改动一起丢掉。
- **怎么检查**：复习题 1.8-r1、1.8-r4、1.8-d1；人工检查：回头看终端里自己敲过的命令，每一条 `git restore`（不带 `--staged`）前面都有一条 `git status` 和一条 `git diff`。
- **例外**：无。`git restore --staged 文件名` 只把改动从暂存区拿下来、不碰文件，不会丢数据，用之前看一眼状态是好习惯，但不在这条规则管的范围里。
- **旧教程提醒**：旧教程用 `git checkout -- 文件名` 丢弃修改。它今天还能用，同样找不回来，同样要先看状态；现在 Git 自己提示的写法是 `git restore 文件名`（自 Git 2.23 起有；Git 2.51 起不再算实验性的命令，也就是官方不再说它的用法以后可能会变）。
- **学于**：1.8

> 原文在第 1.8 课「Git：后悔药」的 [`rules.md`](../stages/01-foundations/08-undo-uncommitted/rules.md)。
