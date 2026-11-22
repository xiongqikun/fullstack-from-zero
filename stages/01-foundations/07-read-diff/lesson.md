# 1.7 Git：看懂改了什么

> **用时** 2 站，约 90 分钟 ｜ **前置** 1.6 ｜ **核实** 2026-11-20 · git 2.54.0 · less 668 · macOS 27.2.1 · zsh 5.9
> **学完你能** 提交之前读懂 `git diff` 和 `git diff --staged`，说出哪一行删了、哪一行加了；用 `git log --stat` 和 `git show` 查出历史里某一个提交到底改了什么；被长长的输出“困住”时知道按 `q` 出来。
> **本课行规** GIT-03（见文末）

## 先想一想

朋友帮你改了一份简历，发回来一份新的。你想知道他改了哪几处，又不想逐字对照。你希望有一样什么东西替你做这件事？先在心里答一句。

## 第 1 站：还没提交的改动（约 40 分钟）

### 概念

拍快照（提交）之前，你怎么知道自己改了哪里？打开文件只看得到现在的样子。

Git 能替你对照。对照的结果叫**差异（diff）**：两个版本之间的对照清单，一行一行列出哪些行删掉了、哪些行加上了。这就是「先想一想」里你想要的东西。

类比：Word 或 WPS 的“修订”功能，删掉的字画删除线，加上的字换颜色。这个类比在哪里不成立：Git 默认按**整行**对照，一行里只改了一个字，也算“删掉旧的一行、加上新的一行”。

这一站的两条命令，各比较 Git 图里的一对区域（`diff` 是 difference，差别；`--staged` 是“已经放进暂存区的”）：

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

（远程和 `git push` 以后再讲。）

| 命令 | 比较的两个地方 | 回答的问题 |
|---|---|---|
| `git diff` | 工作区 ↔ 暂存区 | 我改了什么，还没 `git add`？ |
| `git diff --staged` | 暂存区 ↔ 最新的提交 | 我 `git add` 了什么，下一次提交会存进去？ |

### 跟我做

#### 1. 先确认起点

```zsh
cd ~/Developer/my-site
git status
```

你应该看到：

```text
On branch main
nothing to commit, working tree clean
```

如果报 `fatal: not a git repository`：回到 1.6 课第 3 站；或者回到学习工作区（`cd ~/Developer/fullstack-from-zero`）运行 `python3 tools/course.py scenario 1.7`，照它给的 `cd` 进网站的副本，本课的 `~/Developer/my-site` 都换成它。

#### 2. 改一处

```zsh
code .
```

〔对照文档，界面可能不同〕在 VS Code 左边的资源管理器里点 `style.css`，把 `h1` 下面 `color:` 后面的颜色值改成 `#c2410c`（一种橙红色），按 ⌘S 保存。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

#### 3. 一行一行读差异

回到终端，先猜：`git diff` 会列出什么？

```zsh
git diff
```

你应该看到（你的会不一样：减号那一行是你原来的颜色；第 2 行的编号和第 5 行的数字也可能不同，下面会讲）：

```text
diff --git a/style.css b/style.css
index 7cd4dc1..ce2ae60 100644
--- a/style.css
+++ b/style.css
@@ -8,5 +8,5 @@ body {
 }
 
 h1 {
-  color: #0b5cad;
+  color: #c2410c;
 }
```

什么也没输出？多半是没保存：标签页上有圆点，按 ⌘S 再看。屏幕最下面要是只剩一个冒号 `:`，那是 1.1 课学过的 `less`，按 `q` 回到提示符（第 2 站细讲）。

前四行说对照的是哪个文件，先跳过。减号行在终端里是红的，加号行是绿的：

| 这一行 | 意思 |
|---|---|
| `@@ -8,5 +8,5 @@ body {` | 一个**改动块（hunk）**（一处挨在一起的改动）的开头：旧文件第 8 行起 5 行，新文件也是。`body {` 只标出大概位置 |
| 空格开头的行 | 没变的上下文，默认前后各留 3 行 |
| `-` 开头的行 | 删掉的旧行 |
| `+` 开头的行 | 加上的新行 |

一减一加挨着，是这一行被改了；只有减号，是删了一行；只有加号，是新加了一行。

> **想多了解（可跳过）：前四行的意思**
> - `diff --git a/style.css b/style.css`：开始对照一个文件，`a/` 是改之前，`b/` 是改之后。
> - `index 7cd4dc1..ce2ae60 100644`：Git 按文件内容给两个版本算出的编号（内容一样，编号就一样），`100644` 是普通文件。
> - `--- a/style.css` 和 `+++ b/style.css`：带 `-` 的行来自改之前，带 `+` 的行来自改之后。

#### 4. 故意出错一次

把文件名少敲一个字母：

```zsh
git diff style.cs
```

你应该看到：

```text
fatal: ambiguous argument 'style.cs': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
```

> 读懂这句：参数 `style.cs` 有歧义：既不是已知的版本（revision，指某一个提交），也不是工作区里的路径。后两行是一种更严格的写法，用不到。

报错三问：Git 在报错（开头是 `fatal`，不是 `zsh:`）；关键词 `not in the working tree`，工作区里没有这个东西；我把 `style.css` 少敲了一个 `s`。文件名敲对时，`git diff style.css` 只看这一个文件的差异。

> **想多了解（可跳过）：在不是仓库的地方运行 git diff**
> 第一行是 `warning: Not a git repository. Use --no-index to compare two paths outside a working tree`（这里不是 Git 仓库），下面一大串用法说明不用读。带 `--staged` 时第一行是 ``error: unknown option `staged'``，原因一样。先 `pwd` 看自己在哪，再 `cd` 进仓库。

#### 5. 放进暂存区以后再看

先说出执行后图会怎么变：`git add style.css` 会把这处改动放到哪个区域？

```zsh
git add style.css
```

没有输出就是成功了。先猜：再运行 `git diff` 会看到什么？

```zsh
git diff
```

你应该看到：什么也没有，直接回到提示符。这不是坏了：改动进了暂存区，工作区和暂存区一模一样，没有差别可列。

```zsh
git status
```

你应该看到：

```text
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   style.css

```

> 读懂这句：下面是准备提交的改动，`style.css` 被修改了（modified）。括号里说，想把它拿出暂存区用 `git restore --staged <file>`（1.8 课讲）。`<file>` 是占位的写法：真敲时换成文件名，尖括号不要敲，`...` 是可以写好几个。

> **旧教程提醒**：以前这里提示的是 `git reset HEAD <file>...`；自 Git 2.23 起，提示换成了那一版新加的 `git restore --staged`。Git 官网上的官方书《Pro Git》的 2.2 节，示例多数还是旧的那句（2026-11-20 核对）。

看暂存区里的改动用另一条命令。短横线和空格都用英文输入法敲：`——staged` 会得到第 4 步那样的 `fatal`；全角空格会让 zsh 或 Git 把它前后的字当成一个词，报 `command not found`、`is not a git command` 或 `invalid option`。

```zsh
git diff --staged
```

你应该看到：和第 3 步的差异一字不差。改动没变，变的是它所在的区域。先不要提交：它留在暂存区，停多久都不会丢，第 2 站要用。

### 补全

把空填上（填在心里或纸上都行，不用运行）：

```text
git ______             # 看改了、但还没 git add 的改动
git ______ ________    # 看已经 git add、下一次提交会存进去的改动
```

### 自己做

目标：同事改了汇率小程序的两个文件，还没提交，其中一个已经 `git add` 过。**不改任何文件**，查出两件事：`convert.py` 里被改的那个数，改之前是多少；`rates.txt` 里删掉的是哪种货币。

回到学习工作区：`cd ~/Developer/fullstack-from-zero`，搭练习场景，再照它给的 `cd` 进同事的仓库：

```zsh
python3 tools/course.py scenario 1.7a
```

查清楚以后，运行检查，把答案敲进去。

- 提示：`python3 tools/course.py hint 1.7a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.7a`

> **存档点 1.7a**：到这里可以安全停下。下次可以对导师说“从 1.7b 继续”。

## 第 2 站：历史里的改动（约 40 分钟）

### 概念

提交以后，改动并没有消失：每个提交的改动都随时能调出来看。

类比：还是第 1.6 课的游戏存档：每个存档都能打开，回到那一刻。这个类比在哪里不成立：存档只能读回来，不会告诉你和上一个差在哪；Git 每次存的也是一张**完整快照**：暂存区里一直放着上次提交时的全部文件，`git add` 只是把你改过的那几个换成新样子，所以拍下的是一整箱；和上一张相比，变了的只有你放上“打包台”的那部分（第 1.6 课说“只存放上打包台的那部分”，指的就是这个）。你要看改动时，Git 把这个提交和上一个现场对照一遍，算出差异。

两条新命令：`git show <提交编号>` 打开一个提交，列出说明和完整差异（show，展示）；`git log --stat` 是历史清单，每个提交下面附一张“改了哪些文件、各改几行”的小统计（stat 是 statistics，统计）。

### 跟我做

#### 1. 提交之前再看一眼

```zsh
cd ~/Developer/my-site
git status
```

你应该看到：

```text
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   style.css

```

看到 `nothing to commit, working tree clean`：改动还没做，就回到第 1 站第 2 步；已经提交了，就跳到下面的 `git log --oneline`。`style.css` 在 `Changes not staged for commit` 下面：先 `git add style.css`。

按行规 GIT-03（文末），提交前把要存进去的东西再看一遍：

```zsh
git diff --staged
```

确认只有 `color` 这一处。先说出执行后图会怎么变，再提交（引号用英文的 `"`，中文弯引号会被存进说明里；出现 `dquote>` 就按 Ctrl+C 重来）：

```zsh
git commit -m "改了标题的颜色"
```

你应该看到（你的会不一样：方括号里的编号）：

```text
[main c68477d] 改了标题的颜色
 1 file changed, 1 insertion(+), 1 deletion(-)
```

> 读懂这句：在 main 上新建了提交 c68477d；1 个文件有改动，加了 1 行，删了 1 行。

要是看到的是 `error: cannot run gpg` 开头、`fatal: failed to write commit object` 结尾的几行，提交没成功（改动还在暂存区）：签名还没处理好，回到 1.6 课第 1 站，处理完再提交。

```zsh
git log --oneline
```

你应该看到（你的会不一样：编号；网站要是多拍过快照，会多几行）：

```text
c68477d (HEAD -> main) 改了标题的颜色
236ca4a 在 README 里写上用 Git 记录改动
9cc7008 第一版网页
```

> 读懂这句：最新的提交在最上面。`HEAD` 标的是“你现在在哪个提交上”：main 这条线最新的这一个。

#### 2. 打开一个提交

先猜会看到什么，再把“改了标题的颜色”左边那 7 位编号换进命令：

```zsh
git show c68477d
```

你应该看到（你的会不一样：编号、名字、邮箱、日期）：

```text
commit c68477d6222691e753c9bd510a46c314fade19e6 (HEAD -> main)
Author: 你的名字 <you@example.com>
Date:   Fri Nov 20 07:57:44 2026 +0800

    改了标题的颜色

diff --git a/style.css b/style.css
index 7cd4dc1..ce2ae60 100644
--- a/style.css
+++ b/style.css
@@ -8,5 +8,5 @@ body {
 }
 
 h1 {
-  color: #0b5cad;
+  color: #c2410c;
 }
```

> 读懂这句：上半截是提交的身份：编号、作者（Author）、日期（Date）、说明；下半截就是提交前用 `git diff --staged` 看到的那段差异。

最下面只剩一个冒号 `:` 时，按 `q` 回到提示符（第 4 步细讲）。

#### 3. 故意出错一次

```zsh
git show 1234567
```

你应该看到：

```text
fatal: ambiguous argument '1234567': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
```

报错三问：Git 在报错；关键词 `unknown revision`，不认识的版本（提交编号就是一种版本）；我敲了一个这个仓库里没有的编号。多半是抄错了一位：重新 `git log --oneline`，照着抄。

#### 4. 输出很长时：困住了怎么办

搭一个历史很长的小店网站。回到学习工作区：`cd ~/Developer/fullstack-from-zero`，再运行：

```zsh
python3 tools/course.py scenario 1.7b
```

你应该看到（你的会不一样：`shop-` 后面的词和那句提交说明）：

```text
练习场景 1.7b 搭好了。
位置：~/Developer/playground/1.7b

这里有什么：
  小店网站的仓库在这里：~/Developer/playground/1.7b/shop-meadow
  两位同事已经在里面提交了 14 次。
  「自己做」要找的那个提交，说明写的是「整理一下」。
  先进去：cd ~/Developer/playground/1.7b/shop-meadow

接下来：
  1. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.7b

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.7b --reset
```

照你屏幕上那一行 `cd` 进去。先猜：每个提交下面会多出什么？

```zsh
git log --stat
```

屏幕最上面是这样开头的（你的会不一样：编号和日期）：

```text
commit 94f00df9d363f683e234b38e73216f7b2b7a80ab (HEAD -> main)
Author: 同事小林 <lin@example.invalid>
Date:   Thu Nov 19 01:57:49 2026 +0800

    营业时间写上节假日

 hours.txt | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

commit 06e0cab67039d256b442fb5246ed4fe0515556a8
Author: 同事阿青 <qing@example.invalid>
Date:   Wed Nov 18 01:57:49 2026 +0800

    首页提到订座电话

 index.html | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

> 读懂这句：`hours.txt | 2 +-` 是这个文件有 2 行变动，一加一减；最后一行是改了 1 个文件，加 1 行，删 1 行。

〔对照文档，界面可能不同〕这次输出有一百多行，最下面只剩一个冒号 `:`，提示符不见了。这不是卡住：输出超过一屏时，Git 把它交给**分页器（pager）**一屏一屏地显示，这台电脑上就是 1.1 课学过的 `less`。按键也一样：空格翻一屏，到底显示 `(END)`，按 `q` 回到提示符。翻几屏，再按 `q`。

在这里按 Ctrl+C 退不出来，要按 `q`；误按字母进了别的画面（比如 `h` 是帮助页），也按 `q`，可能要按两次；最下面变成一句提问（比如 `log file:`），先按 delete 键（键盘右上方的删除键）取消，再按 `q`。输出一屏放得下时不进这个界面，也正常。

### 补全

把空填上（不用运行）：

```text
git ___ ______            # 历史清单，每个提交附上改了哪些文件
git ____ <提交编号>        # 打开一个提交，看它的说明和完整差异
______                    # 在分页器里按这个键退出
```

### 自己做

目标：小店仓库里有一个说明写得很含糊的提交（说明在搭练习场景时的屏幕上；忘了就在学习工作区里再运行一次 `python3 tools/course.py scenario 1.7b`，它只再显示一遍）。查出三件事：它改的是哪个文件；哪一样东西被整行删掉了；有一样东西的价格变了：它现在卖多少元。不改任何文件。

- 提示：`python3 tools/course.py hint 1.7b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.7b`

> **存档点 1.7b**：到这里可以安全停下。下次可以对导师说“从 1.7 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| GIT-03 | 每次 `git commit` 之前，先 `git status` 看有哪些文件，再 `git diff --staged` 把要提交的改动一行一行看一遍 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 惯例·平台与工具 | 《Pro Git》第 2 版英文版 2.2、5.2 节；git-diff 手册（网页版 Git 2.56.0） | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 10 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.7`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「GIT-03 提交前先看改了什么」下面用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 1.8 开始”。

## 想多了解

这一节的内容都可以跳过，不影响后面的课。

- 中文：《Pro Git》2.2 节「记录每次更新到仓库」里的“查看已暂存和未暂存的修改” https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库 （多数示例输出是旧版 Git 的提示，见第 1 站的旧教程提醒）
- 中文：《Pro Git》2.3 节「查看提交历史」 https://git-scm.com/book/zh/v2/Git-基础-查看提交历史
- English：git-diff 官方手册（想按词而不是按整行对照，看里面的 `--word-diff`） https://git-scm.com/docs/git-diff
