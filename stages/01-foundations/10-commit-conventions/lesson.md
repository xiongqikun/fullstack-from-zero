# 1.10 提交规范

> **用时** 2 站，约 95 分钟（学完以后另有小关卡 gate-b，单独一段时间，见收尾）｜ **前置** 1.9 ｜ **核实** 2026-11-20 · git 2.54.0 · macOS 27.2.1 · zsh 5.9
> **学完你能** 把几件混在一起的改动分成几个提交；按约定式提交写出别人和工具都看得懂的提交说明；在五条提交说明里挑出毛病
> **本课行规** COMMIT-02、COMMIT-01（见文末）

## 先想一想

你在整理报销票据。三个月的票据全塞进一个信封，信封上只写「票据」。半年后财务问你：三月那张打车票呢？你会怎么找？如果当时一件事一个信封，信封上写清楚是什么，又会怎样？

先在心里答一下。第 1 站的「概念」读完再回来对一对。

## 第 1 站：一次提交只做一件事（约 40 分钟）

### 概念

这一站只讲一件事：**一张快照里该装多少东西**。

答案是一件完整的事。这样的提交叫**原子提交（atomic commit）**：一次提交只装一件事，可以单独看懂、单独撤回。Git 撤回（阶段 2 学）的单位是一整个提交：三件不相干的事拍进同一张快照，说明就写不清，出了错不知道是哪一件，撤回一件，另外两件也跟着动。

开头那道题的答案：一件事一个信封、信封上写清楚，看一眼信封就找到了，提交也一样。这个类比在一处不成立：Git 看得清一个提交里每一行改了什么，但撤回和写说明都按整个提交来，所以拆不拆，要在提交之前决定。

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

（远程和 `git push` 以后再讲。）

诀窍在图中间那一格：每次只往暂存区放**一件事**的文件，马上提交，再放下一件。

### 跟我做

#### 1. 搭练习场

先回到学习工作区，再搭这一课的练习场：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.10
```

你应该看到：

```text
练习场景 1.10-start 搭好了。
位置：~/Developer/playground/1.10-start

这里有什么：
  网站的副本在这里（练习用，不是你真正的网站；第 2 站的提交做在你自己的 ~/Developer/my-site 里）：~/Developer/playground/1.10-start/my-site
  小店的练习仓库在这里：~/Developer/playground/1.10-start/cafe

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.10-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.10 --reset
```

这一课用的是 `cafe`：一家虚构小店的网页仓库，最新的提交只写着「更新」。

#### 2. 看看「更新」改了什么

先猜一下：「更新」改了几个文件？`git show` 你在 1.7 课用过，加上 `--stat` 只列出改了哪些文件、各改了几行；不写编号就看最新的提交。

```zsh
cd ~/Developer/playground/1.10-start/cafe
git show --stat
```

你应该看到（编号和 Date 那一行你的会不一样）：

```text
commit 464df2a2ba732843ca406f91af032eb08c88b6ee
Author: 练习场 <playground@example.invalid>
Date:   Wed Nov 18 20:00:00 2026 +0800

    更新

 about.txt  | 2 +-
 index.html | 2 +-
 menu.txt   | 2 +-
 3 files changed, 3 insertions(+), 3 deletions(-)
```

> 读懂这句：`3 files changed, 3 insertions(+), 3 deletions(-)` 是「3 个文件有改动，一共加了 3 行，删了 3 行」。`练习场` 是工具搭练习场时用的名字，不是你。

三个文件里各是一件互不相干的事：开门时间从 8:00 提前到 7:30，店名从「湖边咖啡」改成「湖边咖啡馆」，拿铁从 22 元涨到 24 元。

要是拿铁涨价搞错了，用 Git 的撤回命令只能连另外两处好的改动一起撤；只撤这一处要多费好几步。

#### 3. 现在轮到你：一件事一次

仓库里还有三处没提交的改动，各是一件事：`menu.txt` 加了一款新饮品，`about.txt` 改正了门牌号，`README.md` 是新写的说明（留到第 2 站）。

先说出执行后图会怎么变：哪个文件走到暂存区，再走进本地历史？只放 `menu.txt`，提交就只装它：

```zsh
git add menu.txt
git commit -m "菜单加上桂花拿铁"
```

你应该看到（编号你的会不一样）：

```text
[main adf074c] 菜单加上桂花拿铁
 1 file changed, 1 insertion(+)
```

#### 4. 故意出一次错

接下来故意漏掉一步：不 `git add`，直接提交地址的改动。先猜一下 Git 会怎么回答。

```zsh
git commit -m "修正地址"
```

你应该看到：

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   about.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	README.md

no changes added to commit (use "git add" and/or "git commit -a")
```

用报错三问读它：

1. **谁在报错？** Git。它没有拍快照，而是把 `git status` 的内容又给你看了一遍。
2. **关键词是什么？** 最后一行的 `no changes added to commit`：暂存区是空的。
3. **我刚才敲了什么？** 只敲了 `git commit`，前面没有 `git add`。上一次提交已经把暂存区里的东西拍走了。

> 读懂这句：`Changes not staged for commit` 下面是改了但还没放进暂存区的，`Untracked files` 下面是 Git 还没管的新文件；最后一行是「没有改动要提交（用 git add，或者用 git commit -a）」。

提示里的 `git commit -a` 会把 Git 已经在管的、改过的文件一起装进去，这一站不用它。改正：先放进暂存区，再提交。

```zsh
git add about.txt
git commit -m "修正地址"
```

你应该看到（编号你的会不一样）：

```text
[main 9a129fa] 修正地址
 1 file changed, 1 insertion(+), 1 deletion(-)
```

先说出 `git log --oneline` 会多出几行，再运行：

```zsh
git log --oneline
```

你应该看到（编号你的会不一样）：

```text
9a129fa 修正地址
adf074c 菜单加上桂花拿铁
464df2a 更新
e172227 添加小店网页
```

两件事，两个提交，互不牵连。

### 补全

在心里把骨架补完整：`a.txt` 和 `b.txt` 各改了一件不相干的事，要分成两个提交。

```text
git ____ a.txt
git commit -m "……"
git ____ b.txt
git ______ -m "……"
git log --oneline        （这时应该多出 __ 行）
```

### 自己做

目标：旅行计划仓库里有两处还没提交的改动，是两件不相干的事。把它们分成两个提交，每个提交只装一件事；说明用一句中文写清楚做了什么就行。

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.10a
```

仓库在场景文件夹里面一层：照工具打印的「进入练习仓库：cd …」那一行进去。在外面那一层运行 Git 命令会看到 `fatal: not a git repository`（那一层不是仓库）。

两件事进了同一个提交，用学过的命令拆不开，也不用拆：回到学习工作区，运行工具最后一行那条 `--reset` 命令重搭一份，照新打印的 cd 那一行进去再做（仓库名字会变）。

做完以后回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.10a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.10a`

> **存档点 1.10a**：到这里可以安全停下。下次可以对导师说“从 1.10b 继续”。

## 第 2 站：写好提交说明（约 40 分钟）

### 概念

回头看刚才那几条提交说明（很多中文资料也叫提交信息）：「更新」什么也没说；「菜单加上桂花拿铁」「修正地址」说清了做什么，可扫一眼历史，分不出哪条是加新东西、哪条是改错。

很多项目和工具在用一种公开的写法：**约定式提交（Conventional Commits）**，现行版本 1.0.0。它是有版本号、很多工具照着读的社区规范，所以规则类型是**惯例·事实标准**：没有机构能罚你。但不是每个项目都用它（例子见本站最后的「想多了解」）。

规范中文版给的结构：

```text
<类型>[可选 范围]: <描述>

[可选 正文]

[可选 脚注]
```

这一课只用第一行和正文；最后的**脚注（footer）**是正文后面几行固定格式的附加信息，第 1.15 课用到时再讲。第一行拆开看：

- **类型（type）**：开头的英文小词，说明这次改动是哪一类。
- **范围（scope）**：可以不写；要写就放在类型后面的圆括号里，比如 `fix(menu):`。
- **冒号和一个空格**：规范第 1 条写的是“必要的冒号（英文半角）和空格”，中文的「：」不算；只空一个是本课程的要求。
- **描述**：一句话说做了什么，可以用中文。

规范本身**只定义了** `feat` 和 `fix`，允许用别的类型；其他常用类型来自 commitlint（在提交时自动检查提交说明的程序）的常用配置（预先设好的一套规则）。按那份配置的原文翻译：

| 类型 | 用在什么时候 | 来自 |
|---|---|---|
| `feat` | 新增一个功能 | 规范 |
| `fix` | 修好一个错误 | 规范 |
| `docs` | 只改文档，比如 README | 工具配置 |
| `style` | 只改代码的排版格式（空格、缩进、换行），不改变效果 | 工具配置 |

`style` 不是指网页的样式（`style.css` 里写的那种，叫 CSS）。改了网页看起来的样子（加一条内容、调大字号），本课程算作 `feat`。

那份配置一共认 11 个类型，清单在本课 `rules.md` 的 COMMIT-01 卡片里。本课程认这 11 个，并要求小写；规范本身不分大小写。

**正文（body）讲为什么。** 改了什么，看改动就知道；看不出来的是为什么。命令行里给两个 `-m`：第一个是第一行，第二个是正文，Git 会在中间空一行。

> **旧教程提醒**：不少中文教程把 docs、style、chore 说成“规范规定的类型”。其实约定式提交从最早的测试版 1.0.0-beta 到现行的 1.0.0 版都只定义了 feat 和 fix；其他类型来自 commitlint 等工具的配置。

**多强制。** 这条规矩的约束力：推荐（适用范围：所有项目），设了检查工具拦下不合格式说明的团队里是必须（适用范围：所在团队）；项目已经有自己的写法，就按那个项目的来，先用 `git log --oneline` 看看它的历史。这门课从这一课起是必须（适用范围：本课程）：这一课的检查、小关卡 gate-b 里第 1.10 课的题和后面几课的检查都会看它；其他题不看说明的格式，但照样按它写。

### 跟我做

#### 1. 回到小店，暂存第三件事

剩下的 `README.md` 是一份说明文档，类型是 `docs`。先说出执行后图会怎么变：`README.md` 会从哪一格走到哪一格？然后把它放进暂存区：

```zsh
cd ~/Developer/playground/1.10-start/cafe
git add README.md
```

#### 2. 故意出一次错

这次故意少打一个引号：描述后面的 `"` 不打，直接按回车。

```zsh
git commit -m "docs: 添加小店的说明
```

你应该看到：命令没有执行，新的一行行首是

```text
dquote>
```

用报错三问读它：

1. **谁在报错？** 不是 Git，是终端里的 zsh。它还在等你把话说完，没有把命令交给 Git。
2. **关键词是什么？** `dquote`，是 double quote（双引号）的缩写：zsh 还在等配对的另一个双引号。
3. **我刚才敲了什么？** 引号只打了左边一个。

按 Ctrl+C，回到平常的提示符，什么都没有提交。〔建课时无法验证〕

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

要是你补上 `"` 再回车，提交已经做成了（没有正文），跳过第 3 步。第 4 步的 `git show --stat` 里就没有正文那两行。

引号和冒号一样要用英文半角。中文引号 `“ ”` zsh 不认：Git 会报错，有时还会把引号当成说明的一部分提交进去。

#### 3. 写一条带正文的提交

先说出执行后图会怎么变：暂存区里的 `README.md` 会去哪里？

```zsh
git commit -m "docs: 添加小店的说明" -m "新来的店员不知道每个文件放的是什么，先写清楚。"
```

你应该看到（编号你的会不一样）：

```text
[main dbf9a04] docs: 添加小店的说明
 1 file changed, 5 insertions(+)
 create mode 100644 README.md
```

> 读懂这句：`create mode 100644 README.md` 是「新建了文件 README.md」，`100644` 是普通文件的标记，不用管它。

#### 4. 看历史和正文

```zsh
git log --oneline
```

你应该看到（编号你的会不一样）：

```text
dbf9a04 docs: 添加小店的说明
9a129fa 修正地址
adf074c 菜单加上桂花拿铁
464df2a 更新
e172227 添加小店网页
```

最上面一条一眼就能看出只改了文档。正文 `--oneline` 不显示，要用 `git show --stat` 看：

```zsh
git show --stat
```

你应该看到（编号和 Date 那一行你的会不一样；Author 是你在 1.6 课设置的名字和邮箱）：

```text
commit dbf9a048303ed8503e71279a6d8fe1ccce7f1649
Author: 你的名字 <you@example.com>
Date:   Fri Nov 20 09:03:43 2026 +0800

    docs: 添加小店的说明
    
    新来的店员不知道每个文件放的是什么，先写清楚。

 README.md | 5 +++++
 1 file changed, 5 insertions(+)
```

第一行和正文中间的空行，是第二个 `-m` 的效果。

### 补全：找茬

下面五条提交说明，每条**正好有一处**毛病，心里想好在哪。检查时工具会一条一条问你，输入字母回答。

```text
1. docs： 补充 README 里的查看方法
2. 修正首页标题的错别字
3. feat: 加上联系方式，顺便把背景改成浅灰色
4. fix:修正页脚链接的地址
5. update: 调整列表的内容
```

### 自己做

目标：在你的网站 `~/Developer/my-site` 里做两处互不相干的改进，每处一个提交，第一行都符合约定式提交。

第 1.6 到 1.9 课拍的提交（「第一版网页」「添加 .gitignore」这些）是学这条规矩之前写的，留着不用改：要改就得改写历史（阶段 2 才学），很多项目也是从某一天起才统一格式的。从这一课起的新提交按约定式提交写。

改什么由你定，可以参考这两件：

- 在 `index.html` 的列表里加一条你接下来想学的东西。这一页在 1.13 课会公开，不要写手机号、住址这类个人信息。
- 在 `style.css` 里把标题调大：在 `h1 {` 和 `}` 之间（1.7 课你改颜色的那一段）加一行 `font-size: 2.25rem;`，就是网页默认字号的 2.25 倍。

先 `cd ~/Developer/my-site`。用 VS Code 改文件，按 ⌘S 保存，和 1.4 课一样；提交时忘了写 `-m`，Git 会打开 1.6 课设好的 VS Code 标签页 `COMMIT_EDITMSG`，什么都不写就关掉它，这次提交就取消了。〔对照文档，界面可能不同〕改完一件提交一件。提交时 Git 说 `nothing to commit`（没有要提交的东西），多半是没保存：标签页上有圆点，按 ⌘S 再提交。

写错了不用改，再做一处改进、这次写对就行：检查看最新的提交合格，并且最近三个里有两个合格，然后问你五道找茬题。每个提交是不是只装一件事，靠你自己把关。

- 提示：`python3 tools/course.py hint 1.10b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.10b`

> **想多了解（可跳过）：第一行多长、另外 7 个类型、破坏性变更、中文引号、别的项目的写法和一个中文项目的例子**
>
> - 第一行写短一点：Git 手册建议不超过 50 个字符，《Pro Git》第 2 版中文版（Git 官网上的教程书）折算成约 25 个汉字。这是建议，超过了也照样提交；有些教程把它说成 Git 的硬规定，其实 git-commit 手册写的是 “Though not required”（不是必须的；2026-11-20 核对 2.55.0 版手册）。
> - commitlint 那份配置里另外 7 个类型是 `refactor`（重写代码但不改功能）、`test`、`chore`、`perf`、`build`、`ci`、`revert`，以后用到再讲。
> - 类型后面加 `!`（比如 `feat!:`）表示**破坏性变更（breaking change）**：会让别人原来的用法失效的改动。
> - 用中文引号敲 `git commit -m “docs: 添加小店的说明”`，Git 回答 `error: pathspec '添加小店的说明”' did not match any file(s) known to git`（pathspec 是 Git 说的“文件路径”：这句是“找不到叫这个名字的文件”）：中文引号没把整句包起来，Git 把后半句当成了文件名，什么都没提交。说明里没有空格时（比如 `“docs:x”`），引号会被当成说明的一部分提交进去。
> - 参与别人的项目时，先看它自己的写法。Git 项目的投稿说明（SubmittingPatches）说，第一行大多以「改动的地方: 」开头，比如 `doc: clarify distinction between sign-off and pgp-signing`，并建议拿不准时对要改的文件运行 `git log --no-merges` 看现在的习惯；Go 项目的投稿说明要以包名开头，比如 `math: improve Sin, Cos and Tan precision for very large arguments`（两页都在 2026-11-20 核对）。
> - 代码公开在网上的金融数据项目 AKShare，贡献指南（https://akshare.akfamily.xyz/contributing.html ，2026-11-20 核对）要求遵循约定式提交，并说类型后面可以接中文描述，例子是 `fix(index): 修复 index_all_cni 接口`。

> **存档点 1.10b**：到这里可以安全停下。下次可以对导师说“从 1.10 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| COMMIT-02 | 一次提交只装一件完整的事 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 惯例·平台与工具 | 《Pro Git》第 2 版中文版（Git 官网上的教程书）5.2 节；GitHub Docs「GitHub flow」（GitHub：放代码的网站，1.11 课注册）；约定式提交常见问题 | 2026-11-20 |
| COMMIT-01 | 提交说明第一行写成「类型(可选范围): 描述」 | 必须（适用范围：本课程）；推荐（适用范围：所有项目）；在用检查工具强制执行它的团队里是必须（适用范围：所在团队） | 惯例·事实标准 | 约定式提交 1.0.0；commitlint 常用配置；git-commit 手册 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 15 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.10`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「COMMIT-01 提交说明遵循 Conventional Commits」「COMMIT-02 一次提交一件事」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

小关卡 gate-b 考第 1.6 到 1.10 课：每课一道实操题（第一场五道；补考只考还没通过的课），每道都在练习场里新搭的练习场景里做，没有提示，由工具批改；实操题都通过以后，对导师说“请问我 gate-b 的讲解题”，讲解题另需约 10 分钟。评分标准在 `gates/gate-b/rubric.md`。

都做完，这一课就完成了。下一步是小关卡 gate-b：它是单独的一段时间，开考时工具会打印题数和预计用时。下次可以对导师说“做小关卡 gate-b”。

## 想多了解

这一节都可以跳过。

- 约定式提交 1.0.0 中文版，含常见问题（中文）：https://www.conventionalcommits.org/zh-hans/v1.0.0/ 。中文版可能比英文版更新得慢，两边说法不一样时以英文版 https://www.conventionalcommits.org/en/v1.0.0/ 为准。
- 《Pro Git》第 2 版中文版 5.2 节「向一个项目贡献」里的「提交准则」（中文）：https://git-scm.com/book/zh/v2/%E5%88%86%E5%B8%83%E5%BC%8F-Git-%E5%90%91%E4%B8%80%E4%B8%AA%E9%A1%B9%E7%9B%AE%E8%B4%A1%E7%8C%AE
- git-commit 手册的 DISCUSSION 一节，第一行 50 个字符的建议原文在这里（English）：https://git-scm.com/docs/git-commit
