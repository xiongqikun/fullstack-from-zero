# 1.6 Git：第一次提交

> **用时** 3 站，约 135 分钟（含收尾 15 分钟） ｜ **前置** 1.5 ｜ **核实** 2026-11-20 · git 2.54.0 · macOS 27.2.1 · zsh 5.9
> **学完你能** 1. 在任何一个文件夹里用 Git 拍下带说明的快照，并看懂 `git status` 在说什么；2. 你的电脑上 `git commit` 能顺利拍下快照（碰到提交签名的报错也知道怎么处理），Git 的几项一次性设置都按你的决定写好了；3. 你的网站 `~/Developer/my-site` 有了自己的仓库和最初两张快照。
> **本课行规** GIT-01、GIT-02（见文末）

## 先想一想

你大概见过这样一个文件夹：

```text
报告.docx
报告_改.docx
报告_最终版.docx
报告_最终版_v3_真的最终版.docx
```

先在心里答三个问题：哪一个是最新的？第二版和第三版到底差在哪几句？想退回上周二的样子，靠什么？

先别急着查。第 1 站的「概念」里有答案。

## 第 1 站：为什么要版本管理，一次性设置（约 40 分钟）

### 概念

**版本管理**（version control，也叫版本控制）：把一个文件夹每一次像样的状态都存下来，随时能看、能比、能退回。它每存一次都记下什么时候、谁、为什么改，一条命令就能列出来；文件夹里始终只有一份 `报告.docx`，旧的样子都在记录里。

这门课用的版本管理工具叫 **Git**（Git）。Git 通常随 Mac 的命令行开发者工具一起装上；还没有的话，第一次在终端敲 `git` 时 macOS 会请你安装（README「怎么拿到这门课」讲了）。被 Git 管着的文件夹叫**仓库**（repository）。可以把仓库想成一个带相册的文件夹：里面有一个隐藏的 `.git` 文件夹，那就是相册。这个类比在哪里不成立：相册里存的是你选中的改动，不是整台电脑。

拍一张快照（文件夹在那一刻的样子）并写一句说明，叫一次**提交**（commit）。它像游戏存档：存下那一刻的进度，以后能回来。这个类比在哪里不成立：存档会存下全部，提交只存你事先放上“打包台”的那部分（第 2 站讲）。

下面这张图后面几课会一直用，不会改：

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

这一课用到前三格。最右边的「远程」以后再讲（第 1.12 课）。

上面这几个词和这张图是后面几课的地图，先认个脸就行，第 2 站起会一个一个用上。这一站真正要学会的新概念只有一个：**Git 的设置**。写在主文件夹的隐藏文件 `~/.gitconfig` 里的叫**全局设置**（global configuration），对这台电脑上所有仓库都起作用；写在某一个仓库里的，只管那一个仓库。

### 跟我做

终端里先回到学习工作区：

```zsh
cd ~/Developer/fullstack-from-zero
```

#### 1. 看一眼 Git 的版本

`git --version` = 显示 Git 的版本号。先猜它会输出什么，再敲：

```zsh
git --version
```

你应该看到：

```text
git version 2.54.0 (Apple Git-157)
```

> 读懂这句：Git 的版本是 2.54.0，是 Apple 打包的第 157 版。

这一课按 2.54.0 核对。版本号不一样，就把这一行发给导师，导师会先核对受影响的步骤。

#### 2. 改设置之前，先备份

接下来要改 `~/.gitconfig`。先用第 1.2 课学过的 `cp` 复制一份，文件名后面加上今天的日期（格式 `YYYY-MM-DD`）：

```zsh
cp ~/.gitconfig ~/.gitconfig.backup-2026-11-20
```

没有输出就是成功了。哪一步改坏了，用备份盖回去就能复原：`cp ~/.gitconfig.backup-2026-11-20 ~/.gitconfig`（日期换成你的）。看到 `No such file or directory`（没有这个文件）：还没有可备份的，先做第 3 步，再敲一次这条 `cp`。

#### 3. 确认 Git 知道你是谁

每一个提交都会写上“谁拍的”：一个名字和一个邮箱。`git config get 设置名` = 读一项设置现在的值（get 是“取”）：

```zsh
git config get user.name
git config get user.email
```

你应该看到两行（你的内容会不一样）：

```text
你的名字
you@example.com
```

两行都有内容，身份就设好了，下面那两行设置命令不用敲；能不能公开，第 3 站再决定。

哪一行什么都没打印，就是还没设置。`git config set --global 设置名 值` = 把一项设置写进全局设置（set 是“设定”，`--global` 是“全局那一层”）。只有哪一行什么都没打印，才敲下面两行：把 `小林` 和邮箱换成你自己的（双引号用英文半角）。

```zsh
git config set --global user.name "小林"
git config set --global user.email "xiaolin@example.com"
```

> **旧教程提醒**：教程、很多官方页面（包括 GitHub Docs）和 Git 自己打印的提示里，还常见老写法 `git config --global user.name "小林"`。Git 从 2.46 版（2024 年）起改用 `get`、`set` 这样的子命令（紧跟在命令名后面的第二个词），手册把老写法列为过时的写法（git-config 手册 2.56.1 版、Git 2.46.0 的发布说明（每个新版本附带的改动清单），2026-11-20 核对）。老写法照样能用；这门课只用新写法。

没设也能提交：Git 会自己拼一个身份写进去（这一站末尾的「想多了解」细说），所以拍之前就定好：行规 GIT-02。

#### 4. 试拍一张快照：可能会失败

练习场里备好了一个仓库，要拍的东西都放好了。先搭练习场景：

```zsh
python3 tools/course.py scenario 1.6a
```

你应该看到：

```text
练习场景 1.6a 搭好了。
位置：~/Developer/playground/1.6a

这里有什么：
  试拍用的仓库在这里，要拍的东西已经备好了：~/Developer/playground/1.6a/first-try
  进去：cd ~/Developer/playground/1.6a/first-try

接下来：
  1. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.6a

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.6a --reset
```

进去：

```zsh
cd ~/Developer/playground/1.6a/first-try
```

`git commit -m "说明"` = 拍一张快照，`-m` 后面引号里的那句叫**提交说明**（commit message，m 就是 message）。引号用英文半角 `"`：中文输入法打出的 “ ” 不算引号，会原样变成说明的一部分，说明里有空格时还会让提交失败。敲完如果屏幕变成 `dquote>` 在等你，是引号没配对：按 Ctrl+C 重来〔对照文档，界面可能不同〕。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

> **万一进了 vi**：在这一站「自己做」换掉编辑器之前，忘了写 `-m`，Git 会打开老牌终端编辑器 vi，打字没反应或乱跳。按 Esc，输入 `:q!`（英文冒号、q、感叹号），按回车，不保存直接出来；会看到 `Aborting commit due to empty commit message.`（说明是空的，提交已取消），再敲一次带 `-m` 的命令〔对照文档，界面可能不同〕。

按快门，先猜：会成功吗？

```zsh
git commit -m "第一次试拍"
```

全局设置里打开了提交签名、却没装签名程序的电脑上，会看到：

```text
error: cannot run gpg: No such file or directory
error: gpg failed to sign the data:
(no gpg output)
fatal: failed to write commit object
```

> 读懂这句：错误：运行不了 gpg，没有这个文件或文件夹。错误：gpg 没能给数据签名（gpg 什么也没输出）。致命错误：没能写下这个提交。

如果你看到的是 `fatal: not a git repository`（不是 Git 仓库），说明你不在 first-try 里：先敲上面那条 `cd`，再按快门。

如果这一次直接成功了，看到的是下面「再按一次快门」后面那样的三行，说明你的电脑没打开提交签名。下面几段讲签名是怎么回事，读一读就行；关签名和再按一次快门都跳过，从 `git log --oneline` 接着做。

失败了，不是你敲错了。**报错三问**：是 Git 在报错（`error:`、`fatal:` 开头），它运行不了另一个叫 gpg 的程序；关键词是 `cannot run gpg` 和 `failed to write commit object`（提交没写下来）；我刚才敲的是 `git commit`，快照没拍成。

为什么要找 gpg？因为全局设置里打开了**提交签名**（commit signing，给每个提交盖一个只有你能盖的章）：设置 `commit.gpgsign` 的值是 `true`（打开），盖章程序却是没装的 gpg。

它是可选功能（**惯例·平台与工具**，约束力**参考**（适用范围：本机））：没签名的提交 GitHub（第 0.4 课提过的存放代码的网站，第 1.11 课注册）照样接收，除非仓库管理员规定那个仓库必须签名（GitHub Docs「About commit signature verification」，2026-11-19 核对）。

由你决定。推荐：现在关掉签名，第 1.11 课有了 GitHub 账号再选怎么签；随时能改回来（另外两种做法见这一站末尾的「想多了解」）。这是你自己的全局设置，由你亲手改：

```zsh
git config set --global commit.gpgsign false
```

没有输出就是改好了。再按一次快门，先猜这次会看到什么：

```zsh
git commit -m "第一次试拍"
```

你应该看到（你的会不一样：编号）：

```text
[main (root-commit) 91bcb7c] 第一次试拍
 1 file changed, 2 insertions(+)
 create mode 100644 hello.txt
```

> 读懂这句：在 main 上拍下了根提交（root-commit，这个仓库的第一张快照），编号 91bcb7c，说明是“第一次试拍”。1 个文件有改动，增加了 2 行。新建了文件 hello.txt（100644 是“普通文件”的意思，可以不管）。

编号由快照的内容、时间和作者算出来，每个人的都不一样。图上，本地历史那一格多了一张。`git log --oneline` = 看本地历史，每个提交一行（log 是日志，oneline 是一行）：

```zsh
git log --oneline
```

你应该看到（你的会不一样：编号）：

```text
91bcb7c (HEAD -> main) 第一次试拍
```

左边是编号（前 7 位），右边是说明。`main` 是这条历史线的名字，这样的线叫分支（branch，阶段 2 才细讲）；HEAD 是 Git 标“你现在在哪”的记号，`HEAD -> main` 就是“你在 main 的最新一张”。签名关着（你刚关掉的，或者本来就没打开），这个决定会在这一站的检查通过时记进学习记录。

### 补全

Git 的设置命令只有两种样子。把设置名和值填上（答案就在上面的步骤里）：

```text
看一项设置现在的值：  git config get ________
把一项设置改成新值：  git config set --global ________ ________
```

### 自己做

目标：把下面这一项写进全局设置，再用 `git config get` 读一次，确认值和表里一样。

| 设置名 | 改成 | 做什么 | 规则类型 · 约束力 |
|---|---|---|---|
| `core.editor` | `"code --wait"` | Git 要你写长说明时打开 VS Code，不再打开 vi | 规范·本课程约定 · 必须（适用范围：本课程）；推荐（适用范围：本机）；写法出自 GitHub Docs「Associating text editors with Git」（2026-11-20 核对） |

这一站的检查会看这一项，因为不设的话 Git 会打开 vi。`--wait`（等待）让 Git 等你在 VS Code 里关掉那个标签页再继续；少了它，Git 一打开 VS Code 就以为你写完了〔对照文档，界面可能不同〕。值里有空格，整个值要用英文半角双引号括起来；忘了引号，Git 会说 `error: wrong number of arguments, should be 2`（读懂这句：参数（argument：命令名后面跟着的每一个词，第 1.1 课的选项和对象都算；这里是设置名和值）个数不对，应该是 2 个），加上引号再敲一次。

设好以后再忘了 `-m`，打开的就不是 vi，而是 VS Code 里一个叫 `COMMIT_EDITMSG` 的标签页，终端停着等你：在第一行写提交说明，⌘S 保存，关掉这个标签页，提交就完成了；什么都不写就关掉，提交会取消〔对照文档，界面可能不同〕。

- 提示：`python3 tools/course.py hint 1.6a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.6a`

> **想多了解（可跳过）：把 main 写进自己的设置**
>
> 刚才的试拍已经在 main 上了，那是因为 Apple 在 Git 安装包里另放了一份设置文件，里面写着 main（Git 是跟着 Apple 给开发者的工具包 Xcode 装上的）。那是第三层设置，你不用管，也不要改。Git 自己的内置默认还是 master，要到 Git 3.0 才改成 main；Git 的文档 BreakingChanges 在 2026-11-19 写的是这个版本“还没有计划的发布日期”。想让新仓库的第一个分支换了 Git 也叫 main，可以把它写进你自己的全局设置（规则类型：惯例·平台与工具；约束力：推荐（适用范围：所有项目））：
>
> ```zsh
> git config set --global init.defaultBranch main
> ```
>
> **旧教程提醒**：以前的教程（包括《Pro Git》中文版，Git 官方网站 git-scm.com 上免费的那本 Git 书）里，`git init` 之后第一个分支叫 `master`；现在新仓库用 `main`（GitHub 自 2020 年 10 月起默认 `main`，Git 计划在 3.0 改成 `main`）。旧名字还能用，只是不再是惯例。

> **想多了解（可跳过）：签名的另外两种做法**
>
> 除了关掉，还有两条路。一是保持打开、配好盖章的程序：第 1.11 课最后的「想多了解」讲用 SSH 钥匙（一种证明“我是我”的钥匙）签名（要先有 GitHub 账号）；用 gpg 签名这门课不讲。二是签名开着、每次提交时临时绕过：忘了一次就失败一次，不建议。

> **想多了解（可跳过）：没设身份会怎样**
>
> 身份没设置时 `git commit` 并不拒绝，而是拿你登录这台 Mac 的全名和“用户名@电脑名.local”拼一个身份写进提交（建课时在 Git 2.54.0 上试过），屏幕上只多印一段英文提醒，很容易看漏。写进提交的身份要改，就得另造新提交、改写历史（阶段 2 才学）。

> **存档点 1.6a**：到这里可以安全停下。下次可以对导师说“从 1.6b 继续”。

## 第 2 站：第一次提交（约 40 分钟）

### 概念

这一站的新概念：**改动先放进暂存区，再拍成提交**。对着第 1 站那张图看前三格：

- **工作区**（working tree）：一个仓库里你正在改的那些文件，就是你在文件夹里看到的样子。它是 Git 的词，不是课程那个“学习工作区”（`fullstack-from-zero` 文件夹）。
- **暂存区**（staging area）：准备拍进下一张快照的改动。它像打包台：你决定哪些东西装进这一箱。这个类比在哪里不成立：装箱以后你再改那个文件，箱里的还是旧的，要重新放一次。
- **本地历史**（commit history）：已经拍下的快照，一张接一张，存在你自己的电脑上。

为什么要多一个暂存区？手头常常同时改着几样东西，暂存区让你挑出改好的先拍。

### 跟我做

回到学习工作区，搭这一站的练习场景：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.6b
```

你应该看到（你的会不一样：`shop-` 后面那个词每个人不同）：

```text
练习场景 1.6b 搭好了。
位置：~/Developer/playground/1.6b

这里有什么：
  日记文件夹 diary：~/Developer/playground/1.6b/diary
  小店菜单文件夹：~/Developer/playground/1.6b/shop-kelp

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.6b
  2. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.6b

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.6b --reset
```

跟我做用 `diary`。`git init` 在哪里运行，就把哪个文件夹变成仓库，所以进去以后先用 `pwd` 看一眼位置：

```zsh
cd ~/Developer/playground/1.6b/diary
pwd
```

你应该看到（你的会不一样：用户名），最后一段是 `diary`：

```text
/Users/你的用户名/Developer/playground/1.6b/diary
```

#### 1. 故意早了一步：还没建仓库就问状态

`git status`（status = 状态）问 Git：每个文件在哪一格？diary 还只是个普通文件夹，先猜：会怎样？

```zsh
git status
```

你应该看到：

```text
fatal: not a git repository (or any of the parent directories): .git
```

> 读懂这句：致命错误：这里不是 Git 仓库（它的上层文件夹也都不是），找不到 .git。

报错三问：是 Git 在报错（`fatal:` 开头）；关键词是 `not a git repository`（不是仓库）；我刚才在一个还没建仓库的文件夹里问状态。

#### 2. 把文件夹变成仓库

`git init` = 在当前文件夹里建一个仓库（init 是 initialize，初始化）：

```zsh
git init
```

你应该看到（你的会不一样：用户名）：

```text
Initialized empty Git repository in /Users/你的用户名/Developer/playground/1.6b/diary/.git/
```

> 读懂这句：在这个位置建好了一个空的 Git 仓库，相册就是里面的 `.git` 文件夹。

路径要以 `diary/.git/` 结尾。不是的话先停下，什么也别删：以 `fullstack-from-zero/.git/` 结尾，对导师说“急救：学习工作区里多了 .git”；是别的地方，对导师说“急救：git init 建错了地方”，并把那一行发过去。

#### 3. 放进暂存区，再提交

`git add 文件名` = 把这个文件现在的样子放进暂存区。只放 `monday.txt`，先说出图会怎么变：

```zsh
git add monday.txt
git status
```

你应该看到：

```text
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   monday.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	todo.txt

```

> 读懂这句：在 main 分支上，还没有提交。要提交的改动（Changes to be committed，已经在暂存区）：新文件 monday.txt（括号里是把它拿出暂存区的命令，现在用不到）。Untracked files 下面的 todo.txt 是**未跟踪**（untracked）的：在文件夹里，但 Git 还从来没收过它。

现在按快门，先猜：这一次会拍下几个文件？

```zsh
git commit -m "添加周一日记"
```

你应该看到（你的会不一样：编号）：

```text
[main (root-commit) c98a02b] 添加周一日记
 1 file changed, 1 insertion(+)
 create mode 100644 monday.txt
```

只拍下了暂存区里的 monday.txt；todo.txt 还在工作区，没被收。

#### 4. 改一次，再拍一次：改 → 暂存 → 提交

以后每天都是这个循环。用 VS Code 打开这个文件夹（第 1.4 课学过）：

```zsh
code .
```

在 `monday.txt` 里加一行 `周一：第一次提交成功了。`，按 ⌘S 保存，回到终端。先说出图会怎么变：

```zsh
git status
```

你应该看到：

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   monday.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	todo.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：有改了、还没放进暂存区的文件（Changes not staged for commit）：monday.txt 被修改过（第二个括号里的 `git restore` 会丢掉这处改动，现在不要用）。最后一行：还没有改动放进暂存区；里面的 `git commit -a` 这门课不用。

没看到 `modified:   monday.txt`？多半是没保存：VS Code 标签页上文件名旁边有圆点 ● 就是还没存〔对照文档，界面可能不同〕。

放进暂存区，拍下来，再看一眼本地历史。先猜：这一次还会有 `root-commit` 吗？

```zsh
git add monday.txt
git commit -m "周一日记补一句"
git log --oneline
```

你应该看到（你的会不一样：编号）：

```text
[main 2a5f910] 周一日记补一句
 1 file changed, 1 insertion(+)
2a5f910 (HEAD -> main) 周一日记补一句
c98a02b 添加周一日记
```

没有 `root-commit` 了：这是第二张，历史里最新的一张在最上面。

### 补全

把这个每天都用的循环填完整：

```text
在编辑器里改文件并保存
→ git ________          （看看改了什么、在哪一格）
→ git add ________      （把改好的放进暂存区）
→ git ________ -m "________"
→ git log --oneline     （确认历史里多了一行）
```

### 自己做

换到小店菜单文件夹：它和 diary 并排，名字是 scenario 输出里 `shop-` 开头的那个，从 diary 用 `cd ../` 加上这个名字进去。

目标：

1. 把这个文件夹变成仓库（`git init` 之前先 `pwd`）。
2. 只提交 `menu.txt`，提交说明用一句中文写清你做了什么。`draft.txt` 是还没定的草稿，留在仓库外面。
3. 做完以后，`git status` 里只剩 `draft.txt` 一个未跟踪的文件。

提交时看到 `nothing added to commit but untracked files present`（读懂这句：暂存区里没有东西可拍，只有未跟踪的文件）？是少了 `git add menu.txt` 这一步，补上再提交。

- 提示：`python3 tools/course.py hint 1.6b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.6b`

> **想多了解（可跳过）：为什么不用 `git add .`**
>
> 很多教程写 `git add .`（点是“当前文件夹里的一切”）。它会把草稿、临时文件甚至带密码的文件一起放进暂存区，拍进历史就很难抹掉。这门课的做法：先读过 `git status`、确认每个文件都该收，才用 `git add .`；拿不准就按名字点（规则类型：规范·本课程约定；约束力：必须（适用范围：本课程））。哪些文件不该收，第 1.9 课讲；`git add .` 本身归第 1.12 课讲。

> **存档点 1.6b**：到这里可以安全停下。下次可以对导师说“从 1.6c 继续”。

## 第 3 站：给 my-site 建仓库（约 40 分钟）

### 概念

这一站的新概念：**一个项目一个仓库，建在项目的根目录**。根目录就是第 1.5 课写 README 时说的：一个项目最外层的那个文件夹。你的网站的根目录是 `~/Developer/my-site`。

`git init` 在哪个文件夹里运行，就把那个文件夹连同它下面的一切交给 Git。建高了，比如在 `~/Developer` 里运行，你的学习工作区、网站和练习场就全成了一个大仓库里的三个文件夹；到第 1.13 课要公开网站时，就没法只公开 my-site。Git 不会拦你，所以动手之前，先自己确认 my-site 和它的上层都还不是仓库。

### 跟我做

这一站在你真正的网站上做，不在练习场里。进去，确认位置，再用 `ls -a`（第 1.1 课学过）连隐藏文件一起列出来：

```zsh
cd ~/Developer/my-site
pwd
ls -a
```

你应该看到（你的会不一样：用户名；名字的排列和窗口宽度有关）：

```text
/Users/你的用户名/Developer/my-site
.		.editorconfig	index.html
..		README.md	style.css
```

`.editorconfig` 是第 1.4 课你写的那份格式约定，以点开头，所以要 `ls -a` 才看得见；它也是网站的一部分，要一起进仓库。如果第 1.5 课以后你还加过别的网站文件，会多几个名字，下面 `git add` 时按名字一起加上（`.DS_Store` 是 macOS 的 Finder（访达）自己生成的文件，不用加）；拿不准就问导师。

#### 1. 先确认这里还没有仓库

先猜：在这里运行 `git status`，会看到什么？

```zsh
git status
```

你应该看到：

```text
fatal: not a git repository (or any of the parent directories): .git
```

报错三问：是 Git 在报错；关键词是 `or any of the parent directories`（上层文件夹也都不是）；我刚才在 my-site 里问状态。这一次报错是好消息：my-site 和它上面的 `~/Developer`、`~` 都不在任何仓库里，可以放心在这里建。如果你看到的不是这一行，而是以 `On branch` 开头的状态，说明 my-site 已经在某个仓库里了：先停下，不要运行 `git init`，什么也别删，对导师说“急救：my-site 已经在一个仓库里了”，并把屏幕上的内容发过去。

#### 2. 拍之前：这个名字和邮箱，你愿意公开吗

从这一张起，你给网站拍的每一张快照，都会在第 1.13 课跟着网站一起公开，上面写着第 1 站确认过的名字和邮箱。拍了以后再改，要另造新提交、改写历史（阶段 2 才学）；之后改设置也只管以后的提交，之前的提交仍然连着旧邮箱（GitHub Docs「Setting your commit email address」，2026-11-20 核对）。所以现在就决定：

- 名字和邮箱都愿意让任何人看到：什么都不用做，往下走。
- 不愿意：现在就换成你愿意公开的。名字可以用笔名。邮箱用一个你自己能收信、只用来写代码的地址（这是建议，不是规定）：GitHub 只把用“已经加进你账号的邮箱”或它给你的隐私地址拍的提交算在你名下（GitHub Docs「Troubleshooting missing contributions」，2026-11-20 核对），第 1.11 课会改用这个隐私地址。换法和第 1 站一样，把示例换成你自己的：

```zsh
git config set --global user.email "xiaolin.code@example.com"
```

拿不准就先停在这里问导师，不要先拍。

#### 3. 建仓库，拍第一版

`pwd` 刚才已经确认过：你在 my-site 里。先说出每一步之后图会怎么变：

```zsh
git init
git status
```

你应该看到（你的会不一样：用户名）：

```text
Initialized empty Git repository in /Users/你的用户名/Developer/my-site/.git/
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.editorconfig
	README.md
	index.html
	style.css

nothing added to commit but untracked files present (use "git add" to track)
```

第一行的路径要以 `my-site/.git/` 结尾；不是的话先停下，什么也别删，把这一行发给导师，说“急救：git init 建错了地方”。

四个文件都是未跟踪的。按名字把它们一起放进暂存区（`git add` 后面可以跟好几个文件名，用空格隔开）：

```zsh
git add .editorconfig index.html style.css README.md
git status
```

你应该看到：

```text
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   .editorconfig
	new file:   README.md
	new file:   index.html
	new file:   style.css

```

拍下网站的第一版。提交说明先用一句平常的中文；提交说明的行业惯例，第 1.10 课专门讲。

```zsh
git commit -m "第一版网页"
```

你应该看到（你的会不一样：编号和行数）：

```text
[main (root-commit) 717aad7] 第一版网页
 4 files changed, 70 insertions(+)
 create mode 100644 .editorconfig
 create mode 100644 README.md
 create mode 100644 index.html
 create mode 100644 style.css
```

先猜：现在 `git status` 会说什么？

```zsh
git status
git log --oneline
```

你应该看到（你的会不一样：编号）：

```text
On branch main
nothing to commit, working tree clean
717aad7 (HEAD -> main) 第一版网页
```

> 读懂这句：在 main 分支上。没有要提交的东西，工作区是干净的。

“工作区是干净的”：文件夹现在的样子和最新那张快照一模一样。这是你每次收工前想看到的那一行。

### 补全

动手建仓库之前的三个确认，把空填上：

```text
1. 我站在项目的 ________ 里（pwd 的最后一段是项目的名字）。
2. 运行 git status，看到的是 fatal: not a ________ ________，说明这里和上层都还没有仓库。
3. git add 后面写的是文件的 ________，而不是一个点。
```

### 自己做

目标：给你的网站再拍一张快照。

1. 在 `~/Developer/my-site/README.md` 里加一句 `这个网站现在用 Git 记录每一次改动。`（放在哪一段由你定），保存。
2. 把这处改动提交，提交说明写 `在 README 里写上用 Git 记录改动`（后面几课的例子都用这一句）。
3. 最后 `git status` 要显示 `nothing to commit, working tree clean`，`git log --oneline` 至少有两行（多拍过快照的会多几行，也算对）。

改完以后 `git status` 里没有 `modified:   README.md`，或者提交时只看到 `nothing to commit, working tree clean`？多半是没保存：看 VS Code 标签页上有没有圆点 ●，按 ⌘S 再来〔对照文档，界面可能不同〕。提交时看到 `no changes added to commit`（没有改动放进暂存区）？是少了一步：先 `git add README.md`，再提交。看到 `error: pathspec 'README' did not match any file(s) known to git`（路径 README 对不上任何文件）？是引号打成了中文的 “ ”：Git 把说明里空格后面的词当成了文件名，提交没拍成。切到英文输入法，用 `"` 再敲一次。

- 提示：`python3 tools/course.py hint 1.6c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.6c`

> **想多了解（可跳过）：建高了，git status 会是什么样**
>
> 建课时在一个照课程的文件夹布局搭的模拟环境里，在 `~/Developer` 里运行了 `git init`，再运行 `git status`，看到的是：
>
> ```text
> On branch main
>
> No commits yet
>
> Untracked files:
>   (use "git add <file>..." to include in what will be committed)
> 	fullstack-from-zero/
> 	my-site/
> 	playground/
>
> nothing added to commit but untracked files present (use "git add" to track)
> ```
>
> 你的学习工作区、网站和练习场全被当成了一个大仓库里的三个文件夹。这一段只看不做，不要在 `~/Developer` 里运行 `git init`。

> **存档点 1.6c**：到这里可以安全停下。下次可以对导师说“从 1.6 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| GIT-01 | 一个项目一个仓库：先 cd 进项目根目录，用 `git status` 确认还不在任何仓库里，再 `git init` | 推荐（适用范围：所有项目）；必须（适用范围：本课程） | 惯例·平台与工具 | 《Pro Git》第 2 版中文版 2.1；git-init 手册 | 2026-11-20 |
| GIT-02 | 第一次提交之前，确认 `user.name` 和 `user.email` 都设置了，而且是你愿意公开的 | 推荐（适用范围：所有项目）；必须（适用范围：本课程） | 惯例·平台与工具 | 《Pro Git》第 2 版中文版 1.6；GitHub Docs「Setting your commit email address」；本机实测 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

这两条都是**惯例·平台与工具**：没有哪个机构为它们发文件，但 Git 就是这样工作的，GitHub 也照这个认人。在所有项目里它们都只是推荐：Git 不拦你，也没有人来查；在这门课里是必须，这一课的检查会看。《Pro Git》是 Git 官方网站 git-scm.com 上免费的 Git 书。

## 收尾（约 15 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.6`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「GIT-01 一个项目一个仓库，在项目根目录初始化」「GIT-02 提交前确认身份设置」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 1.7 开始”。

## 想多了解

这一节的内容都可以跳过，不影响后面的课。

- **中文文件名显示成一串数字**：Git 默认把中文文件名显示成 `"\347\254\224\350\256\260.txt"` 这样的样子。想让它原样显示 `笔记.txt`，可以设 `git config set --global core.quotepath false`。规则类型：规范·本课程约定；约束力：参考（适用范围：本机）。
- **看全部设置**：`git config list --global` 一行一项列出你全局设置（`~/.gitconfig`）里的每一项，格式是 `设置名=值`；不加 `--global`，还会列出 Apple 放的那一层（第 1 站「想多了解」说的第三层），在仓库里运行还有那个仓库自己的设置。改设置之前和之后各看一次，就知道改了什么。
- **签名的新做法**：以前的说法是“给提交签名必须装 GPG”；现在 Git 2.34 起也可以用 SSH（一种登录别的电脑、证明“我是我”的钥匙，第 1.11 课讲）来签名，GitHub 的文档说这是最容易生成的一种（2026-11-19 核对）。第 1.11 课再选。
- 阅读：《Pro Git》第 2 版 1.6「初次运行 Git 前的配置」（中文）：https://git-scm.com/book/zh/v2/起步-初次运行-Git-前的配置 。注意：这本书写于 Git 2.46 之前，用的是不带 get、set 的老写法，第一个分支也还叫 `master`。
- 阅读：GitHub Docs「About commit signature verification」（English），第 1.11 课选择签名方式时会用到：https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification
- 阅读：Git 文档「BreakingChanges」（English），Git 3.0 计划改掉哪些默认值：https://git-scm.com/docs/BreakingChanges
