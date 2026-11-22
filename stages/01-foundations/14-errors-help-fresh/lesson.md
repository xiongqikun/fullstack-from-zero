# 1.14 排错、求助与“与时俱进”

> **用时** 3 站，约 140 分钟 ｜ **前置** 1.13 ｜ **核实** 2026-11-20 · git 2.54.0 · macOS 27.2.1 · zsh 5.9 · vi（vim 9.1）
> **学完你能** 看到报错先自己读懂、对上原因，常见的几种情况能自己修好；求助时写出别人照着就能重现的问题；拿到一份教程或 AI 的建议，能说出它过没过时、凭什么。
> **本课行规** HELP-01、FRESH-01（见文末）

## 先想一想

你打电话给家电维修：“洗衣机坏了，怎么办？”对方第一句会问你什么？再想一想，如果对方手里拿的是一本十年前的维修手册，你会担心什么？

先在心里答一下，三站都学完会回来对答案。

## 第 1 站：排错实验室（约 40 分钟）

### 概念

报错不是在骂你，是程序留给你的线索。读它用第 0.1 课的报错三问：

1. 谁在报错（哪个程序）？看第一个冒号前面的词：`zsh`、`cp`、`ls`。zsh 是你的 shell（第 0.1 课：在终端里接你命令、照着执行的程序）。Git 的报错常以 `fatal:`（致命错误）或 `error:` 开头，这时报错的是 `git`。冒号前面不是程序名（比如 `hint:`，意思是提示），或者整段话里根本没写程序名时，报错的就是你刚运行的那个程序。
2. 关键词是什么？`No such file or directory` 这类固定说法，每一种对应一类原因。
3. 我刚才敲了什么？把报错里提到的词，和你敲的命令逐个对一遍。

报错像汽车仪表盘上亮起的灯：告诉你是哪个系统出了问题。这个类比在哪里不成立：仪表盘的灯要查手册才懂，终端的报错大多直接写着原因，只是用英文写的。

还有一种“卡住”不出报错：终端像是不理你了。先看屏幕最下面一行：

| 你看到的 | 你在哪里 | 怎么出来 |
|---|---|---|
| `dquote>` 或 `quote>` | 续行提示符（continuation prompt）：一行命令还没输完，终端在等你补上引号 | 按 Ctrl+C |
| 最后一行只有 `:` 或 `(END)` | 分页器 less 里（less 第 1.1 课学，分页器第 1.7 课学） | 按 q |
| 很多行开头是 `~`，最下面一行有文件名 | 编辑器 vi 里（visual editor，终端里的老牌编辑器） | 按 Esc，再输入 `:q!` 回车（不保存退出） |

这一站有五个坏掉的小情况，文件夹名字以 1 到 5 开头。**先不找导师，也不找 AI。** 先读报错，答完三问再动手；卡了五分钟还没头绪，就要一级提示（命令在这一站最后）。

先把实验室搭起来：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.14a
cd ~/Developer/playground/1.14a
```

你应该看到：

```text
练习场景 1.14a 搭好了。
位置：~/Developer/playground/1.14a

这里有什么：
  五个坏掉的情况在这里，一个文件夹一个：~/Developer/playground/1.14a

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.14a
  2. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.14a

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.14a --reset
```


### 跟我做：情况 1，文件“不见了”

目标：把 `notes.txt` 复制一份，叫 `notes-backup.txt`，放在 `notes.txt` 旁边。

```zsh
cd 1-wrong-folder
cp notes.txt notes-backup.txt
```

你应该看到：

```text
cp: notes.txt: No such file or directory
```

> 读懂这句：cp 说：没有叫 notes.txt 的文件或文件夹。

三问：谁在报错？`cp`。关键词？`No such file or directory`：当前文件夹里没有这个名字。我敲了什么？`notes.txt`：要么拼错了，要么它不在我站的地方。

先猜一猜：下面两条命令各会输出什么？

```zsh
pwd
ls
```

你应该看到：

```text
/Users/你的用户名/Developer/playground/1.14a/1-wrong-folder
docs
```

`notes.txt` 不在这里，旁边只有一个 `docs` 文件夹。进去再复制：

```zsh
cd docs
cp notes.txt notes-backup.txt
ls
```

你应该看到：

```text
notes-backup.txt
notes.txt
```

`cp` 成功时什么也不说。记住：看到 `No such file or directory`，先 `pwd` 和 `ls`，确认自己站在哪里。

### 补全：情况 2，命令敲错了

目标：让 `2-typo/diary` 变成一个仓库。别人给了你这条命令，照着敲：

```zsh
cd ~/Developer/playground/1.14a/2-typo/diary
gti init
```

你应该看到：

```text
zsh: command not found: gti
```

> 读懂这句：zsh 说：找不到叫 gti 的命令。

在心里把三问补全：谁在报错？______。关键词？______。我刚才敲了 ______，应该改成 ______。

改好以后敲一遍。成功时你应该看到：

```text
Initialized empty Git repository in /Users/你的用户名/Developer/playground/1.14a/2-typo/diary/.git/
```

> 读懂这句：在这个文件夹里新建了一个空的 Git 仓库。

### 自己做：情况 3 到 5

每个情况只给目标和别人给你的命令。照着敲，读报错，答三问，再修好。

**情况 3：提交了个寂寞。** 进入 `~/Developer/playground/1.14a/3-nothing-staged/notes`，有人改了 `plan.md`。运行 `git commit -m "docs: 更新计划"`。目标：让这处改动真正进入一个提交，最后 `git status` 是干净的。它打印的那段英文，第 1.6 课第 2 站逐句读过。读输出前先回想这张图，提交只拍暂存区里的东西：

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

**情况 4：看着一样的字。** 进入 `~/Developer/playground/1.14a/4-full-width`，从课文里复制这条命令去运行：`ls －a`。目标：看到这个文件夹里的隐藏文件。检查时会问它叫什么名字（每个人的不一样）。

**情况 5：引号没配对。** 进入 `~/Developer/playground/1.14a/5-quote`，把 `my notes.txt` 改名为不带空格的 `my-notes.txt`。别人给你的命令是：`mv "my notes.txt my-notes.txt`。敲完回车，看最下面一行变成了什么，用上面那张表出来〔建课时无法验证〕，再把命令改对。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

三个都做完，回到学习工作区：`cd ~/Developer/fullstack-from-zero`。

- 提示：`python3 tools/course.py hint 1.14a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.14a`

> **存档点 1.14a**：到这里可以安全停下。下次可以对导师说“从 1.14b 继续”。

## 第 2 站：怎么求助（约 40 分钟）

### 概念

自己查了还是不行，就该求助。求助有个顺序，越往前越快：

1. 读报错，答三问（第 1 站）。
2. 看工具自己的说明：屏幕上的提示信息、`man 命令`（第 0.2 课，按 q 退出）；Git 的命令还可以加 `-h`（help：打印一份简短用法）。
3. 看官方文档，比如 Git 的 https://git-scm.com/docs 、GitHub 的 https://docs.github.com/zh 。
4. 把报错原文放进搜索引擎搜，先去掉你自己的文件名和用户名。
5. 问人或问 AI。

到了第 5 步，你要写一个好问题。帮你的人看不到你的电脑，只能照着你写的，在自己电脑上把问题再弄出来一次。所以好问题要有：

- **最小可复现示例**（minimal reproducible example）：去掉一切无关的东西以后，还能让同一个问题再出现一次的最少步骤。通常是一个空文件夹、零到两个文件、三五条命令。
- **五段**：目标、我做了什么、我期望什么、实际看到什么（报错原文，原样粘贴）、版本。

做最小复现像带一小块坏掉的零件去五金店，而不是把整台机器搬过去。这个类比在哪里不成立：零件拆下来就是那一块；最小复现要你自己重新搭一遍，搭的过程中常常就发现了原因。

### 跟我做

先搭这一站的练习场景：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.14b
cd ~/Developer/playground/1.14b
```

你应该看到：

```text
练习场景 1.14b 搭好了。
位置：~/Developer/playground/1.14b

这里有什么：
  一个刚建好、还没有提交的大项目：~/Developer/playground/1.14b/big-project
  提问的骨架：~/Developer/playground/1.14b/question.md

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.14b
  2. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.14b

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.14b --reset
```

**第一步：做一个最小复现。** 拿第 1 站情况 4 的问题当例子：它是在一个装了文件的文件夹里出现的。换到一个全新的空文件夹，看最少要几步能让它再出现。先猜一猜：在空文件夹里，它还会报同样的错吗？

```zsh
mkdir mini-example
cd mini-example
ls －a
```

你应该看到：

```text
ls: －a: No such file or directory
```

> 读懂这句：ls 说：没有叫 －a 的文件或文件夹。

三问：谁报错？`ls`。关键词？`No such file or directory`。我敲了什么？`－a`：ls 把全角的减号当成了文件名。一条命令就复现了，说明问题和那个文件夹里的文件无关。

**第二步：查版本。** 只写和问题有关的程序，再加上系统版本。`ls` 是 macOS 自带的，所以写 macOS 的版本号（sw_vers = software version）：

```zsh
sw_vers -productVersion
```

你应该看到类似这样（你的会不一样：建课时核对用的是 27.2.1）：

```text
27.2.1
```

问题和 Git 有关时，再加上第 1.6 课用过的 `git --version` 打印的那一行（末尾括号里的 Apple Git-157 是苹果给自带的 Git 编的号，一起照抄）。

**第三步：写成五段。** 大概是这样：

```markdown
# 提问：ls -a 报 No such file or directory

## 目标
想看当前文件夹里的隐藏文件。

## 我做了什么
mkdir mini-example
cd mini-example
ls －a

## 我期望什么
列出 . 和 .. 这些条目。

## 实际看到什么
ls: －a: No such file or directory

## 版本
macOS 27.2.1
```

### 补全

把上面例子里“我做了什么”和“实际看到什么”放在一起看：报错里的 `－a` 和你想敲的 `-a` 差在哪里？回答你的人最可能先说哪一句？在心里答完再往下读。

问题写清楚的那一刻，答案往往已经出来了。这是最小复现最常见的好处。

现在看本课的第一条行规：

> **HELP-01 提问给出目标、做法、期望、实际报错原文、版本**
> 约束力：推荐（适用范围：所有项目）；在本课程里向导师求助时是必须（适用范围：本课程）。规则类型：惯例·平台与工具。谁说的：各个平台对“怎么报告问题”的要求，比如 uv（第 2 阶段要用的 Python 工具）官方文档“Reproducible examples”、Python 3.15.2 文档“Dealing with Bugs”、Stack Overflow（程序员问答网站）帮助中心；背景是《How To Ask Questions The Smart Way》修订版 3.10 和它的中文版《提问的智慧》。核对日期：2026-11-20。

导师那边也照这个规矩来：从这一课起，你求助时，导师会先请你答报错三问，再请你给出目标、你敲了什么、期望什么、实际看到的原文和版本，然后给提示。真出了急事，缺几项也照样先帮你修。

### 自己做

`~/Developer/playground/1.14b/big-project` 是一个刚建好、还没有任何提交的项目，十几个文件都已经放进了暂存区。你想把 `index.html` 从暂存区拿出来，运行了：

```zsh
cd ~/Developer/playground/1.14b/big-project
git restore --staged index.html
```

你会看到：

```text
fatal: could not resolve 'HEAD'
```

> 读懂这句：fatal（致命错误）：没法找到 HEAD 指的是什么。HEAD 是 Git 给“你现在所在的最新那个提交”起的名字。

这一站不要求你修好它，要求你把它问清楚：

1. 先回到练习场景：`cd ~/Developer/playground/1.14b`。在这里新建一个叫 `mini` 的文件夹，从空文件夹开始，用最少的文件和命令让**同一个报错**再出现一次。
2. 用 VS Code 打开整个练习场景文件夹（第 1.4 课的 ED-01）：运行 `code ~/Developer/playground/1.14b`，在左边的 Explorer（资源管理器）里点 `question.md`〔对照文档，界面可能不同〕。“目标”和“我期望什么”已经替你写好了。第一行的标题和其余三段，把括号连同说明一起删掉，换成你自己的：命令从空文件夹写起，一条一行；报错从终端复制，原样粘贴，不改写、不截图；版本写 `git --version` 的输出和上面查到的 macOS 版本。写完按 ⌘S 保存。
3. 路径里不要出现你的用户名：用 `~` 开头的写法。

做完回到学习工作区：`cd ~/Developer/fullstack-from-zero`。

- 提示：`python3 tools/course.py hint 1.14b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.14b`

> **想多了解（可跳过）：Git 命令的简短用法**
> Git 的每条命令都有一份简短的用法，加 `-h`（h = help）就能看到，比如 `git restore -h`。它一共三十来行，开头和中间两行是这样（“……”是省掉的地方）：
>
> ```text
> usage: git restore [<options>] [--source=<branch>] <file>...
>
> ……
>     -S, --[no-]staged     restore the index
>     -W, --[no-]worktree   restore the working tree (default)
> ……
> ```
>
> 读懂这句：用法是 git restore 加选项加文件名。-S 和 --staged 是同一个选项的短写和长写，恢复暂存区（index 是暂存区的英文名之一）；-W 或 --worktree 恢复工作区，不写选项时就是它。

> **想多了解（可跳过）：以后在真实项目里求助**
> 学习工作区里的 `templates/ask-for-help.md` 是同样的五段骨架，最下面写着用法。复制一份再写，不改模板本身。

> **存档点 1.14b**：到这里可以安全停下。下次可以对导师说“从 1.14c 继续”。

## 第 3 站：判断一份资料是否过时（约 35 分钟）

### 概念

工具几周就出一个新版本，而网上的教程、问答和 AI 的回答，写的都是写下那一天的样子。拿到任何一份资料，先做三查：

1. **日期**：它是哪天写的、哪天更新的？越老越要查，但老不等于错。
2. **版本**：它说的是哪个版本、哪个系统？和你电脑上的比一比。
3. **官方现在怎么说**：看你电脑上的工具自己的提示、它的官方文档，或者发布说明（release notes：软件每出一个新版本，官方写的“这次改了什么”）。这一查最后说了算。

过时也分程度：有的已经不能用；有的还能用，但官方说以后会去掉，叫弃用（deprecated）；有的还能用，只是大家不这么做了。

判断资料新旧像看食品的保质期：日期提醒你留心。这个类比在哪里不成立：过期的食品就不该吃；几年前的资料可能仍然完全正确，要查过才知道。

AI 学习的资料截止到某一天，叫知识截止日期（knowledge cutoff），那以后的变化它不知道，却可能说得很肯定。导师也是 AI：它说的版本号和命令，你都可以问一句“你确定吗”，它会重新去查。

### 跟我做

**第一步：让工具帮你比版本。** 先猜一猜：它会说什么？

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py fresh
```

你应该看到类似这样（你的会不一样：日期是今天；“课程模块里提到”那几行会随课程更新而变。这份是在建课时核对用的那台 Mac 上运行的，所以每一行都“一致”。「这台电脑」一列是你自己的版本：没装的工具会显示“没装”；你的 `python3` 是 3.9 这类旧版本时，结论是“比课程旧”，最后会列出可能受影响的课。照最后一行“下一步”做）：

```text
版本核对 · 2026-11-20
课程里的命令是在 2026-11-19 用下面这些版本核对的。只看不改，不联网。

  工具                      课程核对时  这台电脑  结论
  macOS                     27.2.1      27.2.1    一致
  zsh                       5.9         5.9       一致
  Git                       2.54.0      2.54.0    一致
  Python（第一个 python3）  3.14.9      3.14.9    一致
  VS Code（code 命令）      1.145.2     1.145.2   一致
  uv                        0.13.5      0.13.5    一致
  Ruff                      0.17.2      0.17.2    一致
  Node.js                   26.12.0     26.12.0   一致
  npm                       11.20.0     11.20.0   一致
  Homebrew                  7.0.10      7.0.10    一致
  GitHub CLI（gh 命令）     2.105.0     2.105.0   一致

可能受影响的课：没有。

课程模块里提到、但基线里没有记录版本的工具（fresh 不比较它们）：
  - grep（查找文字的命令）：1.3
  - less（分页器）：0.2、1.1、1.7
  - vi（Git 默认的编辑器）：1.6、1.14
  - zip（打包压缩的命令）：0.4

下一步：所有工具都和课程核对时一样，不用做什么。
```

课程记下的这张版本表叫基线（baseline）。表的后半截里，Homebrew 你在第 1.11 课用过；uv、Ruff、Node.js、npm 以后几个阶段才用，现在不用管。

哪天某个工具升级了，结论会变成“小版本变了”或“大版本变了”（版本号第一个数变了是大版本，后面的数变了是小版本）。如果有课用到了变了的工具，最后一行会变成：

```text
下一步：把这段发给导师，说“帮我核实受影响的课”。
```

看到它就照做。如果现有的课都没用到它，工具会说可以照常学。

**第二步：故意站错地方。** 先猜一猜：在主文件夹里运行同一条命令，会怎样？

```zsh
cd ~
python3 tools/course.py fresh
```

你应该看到：

```text
python3: can't open file '/Users/你的用户名/tools/course.py': [Errno 2] No such file or directory
```

> 读懂这句：python3 说：打不开这个文件，没有这个文件或文件夹。

三问：谁报错？`python3`。关键词？`can't open file`。我敲了什么？`tools/course.py`：它从当前文件夹算起，而我站在主文件夹里。回到学习工作区：

```zsh
cd ~/Developer/fullstack-from-zero
```

**第三步：拿你电脑上的工具当裁判。** 一份 2018 年的资料说：放弃对文件的修改，用 `git checkout -- 文件名`。问问你自己的 Git。先搭一份网站副本，进去删掉一个文件：

```zsh
python3 tools/course.py scenario 1.14
cd ~/Developer/playground/1.14-start/my-site
rm style.css
git status
```

副本删坏了也不影响真正的 `~/Developer/my-site`。

先说出执行后图会怎么变：工作区少了一个文件，暂存区和本地历史都没变。`git status` 你应该看到：

```text
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	deleted:    style.css

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：分支和远程的 origin/main 一样新；有没放进暂存区的改动：style.css 被删了。要放弃工作区里的这个改动，用 git restore 加文件名。

Git 的提示写的是 `git restore`，不是 `git checkout --`。用它把文件救回来：

```zsh
git restore style.css
git status
```

你应该看到：

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

结论：那份资料的做法还能用，但已经不是 Git 现在推荐的写法。

> **旧教程提醒**：以前放弃修改写 `git checkout -- 文件名`；现在（自 Git 2.23 起，2019 年）有专门的 `git restore 文件名`。旧写法还能用。

本课的第二条行规：

> **FRESH-01 用一个做法前确认它的版本和日期**
> 约束力：必须（适用范围：本课程）；推荐（适用范围：所有项目）。规则类型：规范·本课程约定。谁说的：本课程计划 G4“与时俱进”，做法依据 Git、GitHub、VS Code 的官方文档和发布说明。核对日期：2026-11-20。

### 补全

用同样的三查判断下面这份资料，在心里把空填上：

> 资料（2019 年的一篇博客，写给 Git 2.23）：“git restore 是实验性（experimental：官方说以后还可能改）命令，新手先别用。”

1. 日期：____ 年写的，要查。
2. 版本：它写给 Git ____；你电脑上是 Git ____（第一步 fresh 的表里有）。
3. 官方现在怎么说：Git 2.51 的发布说明里有一句 `"git switch" and "git restore" are declared to be no longer experimental.`（git switch 和 git restore 宣布不再是实验性的；git switch 是换分支用的命令，第 2 阶段才学）。
4. 结论：这份资料 ____（还对 / 过时了）。

git-scm.com 的文档页默认写最新版 Git，页面顶上的 Latest version 菜单能换成你的版本〔对照文档，界面可能不同〕。

### 自己做

检查会给你看三段短资料，问它们现在怎么样，要靠这三条命令的结果判断：`ls --help`、`git log --oneline`、`git --version`。你还在网站副本里，先在这里各运行一次，看清输出，再回到学习工作区：`cd ~/Developer/fullstack-from-zero`。

- 提示：`python3 tools/course.py hint 1.14c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.14c`

> **想多了解（可跳过）：发布说明在哪里**
> 下面三处在 2026-11-20 核对过，什么时候想看都可以去〔对照文档，界面可能不同〕：
>
> | 软件 | 去哪里看 | 2026-11-20 看到的 |
> |---|---|---|
> | Git | https://git-scm.com 首页，最新版本号旁边的 Release Notes 链接；每条命令的文档页写着它“last updated in”哪个版本 | 最新是 2.56.1（2026-10-26）；建课时核对用的 Mac 上，苹果自带的是 2.54.0 |
> | VS Code | https://code.visualstudio.com/updates ，某个版本是 `/updates/v1_147` 这样的地址 | 最新是 1.147（2026-11-18） |
> | GitHub | https://github.blog/changelog/ ，可以按类型筛选，Retired 一类是“去掉了什么” | 最新一条是 2026-11-19 的 |
>
> 最新版比你电脑上的新，不等于你要马上升级。课程按建课时核对的版本写；什么时候升级，导师会和你一起看发布说明再决定。

> **存档点 1.14c**：到这里可以安全停下。下次可以对导师说“从 1.14 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| HELP-01 | 提问给出目标、做法、期望、实际报错原文、版本 | 推荐（适用范围：所有项目）；在本课程里向导师求助时是必须（适用范围：本课程） | 惯例·平台与工具 | 各个平台对“怎么报告问题”的要求：uv 文档“Reproducible examples”；Python 3.15.2 文档“Dealing with Bugs”；Stack Overflow 帮助中心；背景：《How To Ask Questions The Smart Way》修订版 3.10（2014）及中文版《提问的智慧》 | 2026-11-20 |
| FRESH-01 | 用一个做法前确认它的版本和日期 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 规范·本课程约定 | 本课程计划 G4；Git、GitHub、VS Code 的官方文档和发布说明 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

建课时 Stack Overflow 的帮助页打不开，这一处来源只按搜索摘要核对过；你自己用浏览器可以打开看。

回到开头的“先想一想”：维修师傅第一句会问型号和到底哪里不转，这就是“版本”和“实际看到什么”；十年前的手册要先对一下型号和年份，这就是三查。

## 收尾（约 25 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.14`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「HELP-01 提问给出目标、做法、期望、实际报错原文、版本」「FRESH-01 用一个做法前确认它的版本和日期」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。

都做完，这一课就完成了。下次可以对导师说“从 1.15 开始”。

## 想多了解

这一节都可以跳过，不影响检查。

- **旧教程提醒**：以前 `git push` 时输入 GitHub 账号密码；现在 GitHub 不再接受账号密码，要用令牌，或者用 GitHub CLI（第 1.11 课装的 `gh`）这类工具替你登录（自 2021-08-13 起）。
- **旧教程提醒**：很多老的 Mac 入门教程是为 bash（另一种 shell，旧版 macOS 默认用它）写的，让你改 `~/.bash_profile`（bash 的设置文件），第一条命令常是 `echo "Hello, World!"`（echo：把后面的字原样打印出来）。自 macOS 10.15 起，Mac 默认的 shell 是 zsh，设置文件是 `~/.zshrc`（以后讲 PATH 时会用到）；在 zsh 里 `!"` 有特殊含义，那一行会停在 `dquote>`，照第 1 站的表出来，改用单引号：`echo 'Hello, World!'`。
- **旧教程提醒**：以前新仓库的第一个分支叫 master，教程写 `git push origin master`；现在 GitHub 新仓库默认叫 main，建课时核对用的 Mac 上 `git init` 也给 main（GitHub 自 2020-10-01 起）。
- 《提问的智慧》（中文）：https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way/blob/main/README-zh_CN.md 。原文写于 2001 年，语气很冲，看方法，不必学语气。
- Reproducible examples（English，uv 官方文档）：https://docs.astral.sh/uv/reference/troubleshooting/reproducible-examples/
- Git 2.51 发布说明（English）：https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.51.0.adoc ，里面一句写着 git switch 和 git restore 不再是实验性的。
