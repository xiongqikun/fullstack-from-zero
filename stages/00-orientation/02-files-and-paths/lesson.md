# 0.2 文件、路径和代码的家

> **用时** 3 站，约 120 分钟 ｜ **前置** 0.1 ｜ **核实** 2026-11-20 · macOS 27.2.1 · zsh 5.9 · Python 3.14.9
> **学完你能** 在终端里用 `cd` 和路径在文件夹之间走来走去，说出一个文件的完整地址；按报错三问读懂英文报错，用 `man` 查一条命令的用法；说清代码为什么不放在网盘同步的文件夹里，并且给代码定好一个家 `~/Developer`
> **本课行规** WS-01、WS-02（见文末）

## 先想一想

朋友问你住在哪。你可以说“某某市某某区某某路 8 号”，也可以说“从地铁站出来，往前走两个路口，左手边就是”。

这两种说法，哪一种换一个人、换一个出发点来听，还能找到你家？先在心里答一下，第 1 站的“概念”讲完以后回来对答案。

## 第 1 站：路径，在文件夹之间走来走去（约 35 分钟）

### 概念

路径（path）是文件在电脑里的地址。它和寄快递写的地址很像：从大到小一层一层写下去，每一层用斜杠 `/` 隔开。

```text
/Users/你的用户名/Developer/playground
```

读法是：最顶上 `/` 里面的 `Users`，里面的 `你的用户名`，里面的 `Developer`，里面的 `playground`。

地址有两种写法：

- **绝对路径**（absolute path）：从最顶上写起的完整地址，以 `/` 开头，在哪里用都指同一个地方。就像写全了省、市、街道、门牌号。
- **相对路径**（relative path）：从你现在所在的文件夹写起，不以 `/` 开头。就像“从我这里往前走两个路口”。这个类比在这里不成立：听你指路的人会想一想你指的是哪儿，走不通还会回来问；终端不猜也不问，它永远从你现在所在的文件夹出发，照着写的一层一层走。换一个出发点，同一个相对路径就指向别处，甚至什么也找不到。

还有三个符号：

| 符号 | 意思 | 生活里的说法 |
|---|---|---|
| `~` | 你的主文件夹（home folder），也就是 `/Users/你的用户名` | 自己家 |
| `.` | 当前所在的文件夹 | 这里 |
| `..` | 上一级文件夹（parent folder），也就是装着当前文件夹的那一个 | 上一层楼 |

`~/Developer` 和 `/Users/你的用户名/Developer` 是同一个地方：`~` 是绝对路径开头那一段的简写。

回头对一下“先想一想”：写全的地址谁来都能找到，这是绝对路径；“往前走两个路口”只对站在地铁站的人有用，这是相对路径。

### 跟我做

本站新命令：`cd`（change directory，换到另一个文件夹）、`cd ..`、`cd ~`；还有一个新按键：Tab。还会用到第 0.1 课提过的 `scenario`。

打命令之前，先把输入法切到英文。第 2 站会讲为什么。

#### 1. 搭一个练习场景

练习场景是工具在练习场（第 0.1 课提过的 `~/Developer/playground`）里搭的练习用文件夹。

先确认终端在学习工作区里：运行 `pwd`，输出应该以 `fullstack-from-zero` 结尾。不是的话，对导师说“急救：终端不在学习工作区”。

```zsh
python3 tools/course.py scenario 0.2
```

你应该看到：

```text
练习场景 0.2-start 搭好了。
位置：~/Developer/playground/0.2-start

这里有什么：
  一个小镇模样的文件夹：~/Developer/playground/0.2-start/town

接下来：
  1. 进入练习场景：cd ~/Developer/playground/0.2-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 0.2 --reset
```

最后那条 `cd` 是学习工作区现在的位置（你的可能不一样）：这一课每站做完，用它回去运行检查。

#### 2. 用 Tab 少打字，走进去

Tab 补全（tab completion）：名字打开头几个字母，按一下 Tab 键，终端替你补完整，少打字也少打错。〔建课时无法验证〕

输入 `cd ~/Dev`，先不要按回车，按一下 Tab，它应该变成 `cd ~/Developer/`。接着输入 `pl`，按 Tab；再输入 `0.2-`，按 Tab。这一行应该变成：

```zsh
cd ~/Developer/playground/0.2-start/
```

按回车。补得不对或者没反应：按 Ctrl+C 放弃这一行，照上面整行打出来也一样。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

`cd` 成功时什么也不说。看提示符：`%` 前面的词从 `fullstack-from-zero` 变成了 `0.2-start`（`你的用户名@你的电脑名 0.2-start %`），那是你现在所在文件夹的名字。复制命令时不要带上提示符：带上了，会看到 `zsh: command not found:` 后面跟着提示符开头的那一段（找不到叫这个名字的命令）。

先猜一猜：`pwd` 打印的是绝对路径还是相对路径？

```zsh
pwd
```

你应该看到（`你的用户名` 那一段，你的会不一样）：

```text
/Users/你的用户名/Developer/playground/0.2-start
```

`pwd` 打印的永远是绝对路径。

#### 3. 先看一眼，再一次走好几层

`ls` 后面跟一个路径：看一眼那里有什么，人不过去。

```zsh
ls town
```

你应该看到：

```text
north   south
```

`cd` 后面可以一次写好几层。`town/north/library` 是相对路径，从你现在站的 `0.2-start` 写起：

```zsh
cd town/north/library
ls
```

你应该看到：

```text
map.txt         reading-room
```

`map.txt` 是文件，`reading-room` 是文件夹；单看名字分不出来，下一站有办法。

#### 4. 往上走：`..`

先猜一猜：运行 `cd ..` 以后，提示符里 `%` 前面的词会变成什么？

```zsh
cd ..
```

它变成了 `north`：你从 `library` 往上走了一层。`cd` 和 `..` 之间要有一个空格；写成 `cd..`，会看到 `zsh: command not found: cd..`（找不到叫 `cd..` 的命令：没有空格，zsh 把 `cd..` 整个当成了一个命令名）。`../south` 的意思是：先往上走一层到 `town`，再进 `south`。

```zsh
ls ../south
```

你应该看到：

```text
market  station
```

#### 5. 故意出错：回家以后，同一个相对路径

`cd ~` 带你回主文件夹，提示符里的文件夹名会变成 `~`。先猜一猜：在那里运行第 3 步的 `ls town`，会怎样？

```zsh
cd ~
ls town
```

你应该看到：

```text
ls: town: No such file or directory
```

> 读懂这句：ls：找不到叫 town 的文件或文件夹。

用第 0.1 课的报错三问读它：

1. **谁在报错？** 冒号前面的第一个词：`ls`。
2. **关键词是什么？** `No such file or directory`，没有这个文件或文件夹。
3. **我刚才敲了什么？** 一个相对路径。从 `~` 往下找 `town`，所以找不到：`town` 在 `0.2-start` 里面。

换成从 `~` 写起的地址，在哪里都一样：

```zsh
ls ~/Developer/playground/0.2-start/town
```

你应该看到：

```text
north   south
```

### 补全

把空填上：

```text
cd ~/Developer/playground/0.2-start/town/south/market
ls ____/station          ← 不离开 market，看一眼旁边的 station
cd ____                  ← 往上走一层，回到 south
```

### 自己做

换一个地方：一座迷宫。先回到学习工作区：运行第 1 步 `scenario` 输出里“回到学习工作区”后面那条 `cd`（比如 `cd ~/Desktop/fullstack-from-zero`），提示符里会是 `fullstack-from-zero`。忘了回来，下面这条命令会报这样一句（中间的地址是你当时所在的文件夹，你的会不一样）：

```text
python3: can't open file '/Users/你的用户名/Developer/playground/0.2-start/tools/course.py': [Errno 2] No such file or directory
```

> 读懂这句：python3：打不开文件 …/0.2-start/tools/course.py，没有这个文件或文件夹。`tools/course.py` 也是一个相对路径，只有从学习工作区出发才找得到。

```zsh
python3 tools/course.py scenario 0.2a
```

它会打印起点和一条相对路径（名字每个人都不一样）。照着走，看终点有什么文件，再写出这个文件从 `~` 写起的完整地址：用 `pwd` 看那个文件夹的地址，把开头的 `/Users/你的用户名` 换成 `~`，最后加上 `/` 和文件名。然后回到学习工作区运行检查：它先问文件名，再问完整地址。

- 提示：`python3 tools/course.py hint 0.2a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 0.2a`

> **想多了解（可跳过）：名字里带空格**
>
> 名字里带空格的文件夹，路径要用引号（quote，就是 `"` 这个符号）括起来，比如 `cd "My Folder"`。不加引号，`cd My Folder` 会报这样一句：
>
> ```text
> cd: string not in pwd: My
> ```
>
> 读懂这句：cd：在当前的路径里找不到 My 这串字。终端把 `My` 和 `Folder` 当成了两样东西，`cd` 拿它们做了另一件事。
>
> 引号要成对。少打一个，下一行的开头会变成 `dquote>`，终端在等你把引号补上：按 Ctrl+C 放弃这一行，重新打。第 3 站的命名规矩会让你很少碰到这种名字。

> **存档点 0.2a**：到这里可以安全停下。下次可以对导师说“从 0.2b 继续”。

## 第 2 站：读懂报错，查说明书（约 30 分钟）

### 概念

报错不是电脑在骂你。它是写这个程序的人留给你的话，大多有固定的格式：

```text
程序名: 它在处理的东西: 出了什么问题
```

第 1 站的 `ls: town: No such file or directory` 就是这样。

每条命令还带着一份说明书（manual page，常简称 man page），写着它能做什么、可以加哪些写法，用 `man` 命令打开。报错告诉你哪里不对，说明书告诉你该怎么写。

### 跟我做

本站新命令：`man`（manual，说明书），在说明书里按 `q` 退出；还有第 3 步的 `ls -F`。

#### 1. 故意出错：混进一个全角字符

用中文输入法打字时，打出来的空格、字母和标点常常是全角字符（full-width character）：占一个汉字那么宽，看着像，对电脑却是另一个字符。命令名、选项（option，像 `-F` 这样以 `-` 开头、改变命令做法的写法，第 3 步会用到）、隔开它们的空格，还有 `~`、`/`、`-` 这类有特殊作用的符号，都只认英文状态下打出来的半角字符（half-width character）。（中文的文件夹名照样能写进命令，比如 `cd 学习笔记`。）

下面第二行，`cd` 和 `town` 中间故意放了一个全角空格。先走进练习场景，再把第二行原样复制到终端：

```zsh
cd ~/Developer/playground/0.2-start
cd　town
```

你应该看到：

```text
zsh: command not found: cd　town
```

> 读懂这句：zsh：找不到叫“cd　town”的命令。

报错三问：

1. **谁在报错？** `zsh`，就是第 0.1 课说的 shell：在终端里接你命令、照着执行的程序。
2. **关键词是什么？** `command not found`，找不到这个命令。
3. **我刚才敲了什么？** 报错把 `cd　town` 整个当成了命令的名字，说明中间那个“空格”不是真的空格。

改法：切到英文输入法，把这一行重新打一遍。切换的办法：点菜单栏右边的输入法菜单（Input menu），选一个英文的，比如 ABC。〔对照文档，界面可能不同〕全角的字母和标点（`ｃｄ`、`－`）也会这样捣乱。打命令之前，先看一眼输入法。

```zsh
cd town
```

这次没有报错，提示符里的文件夹名变成了 `town`。

#### 2. 打开说明书

```zsh
man ls
```

终端整屏换成了说明书。最上面几行是：

```text
LS(1)                       General Commands Manual                      LS(1)

NAME
     ls – list directory contents

SYNOPSIS
     ls [-@ABCFGHILOPRSTUWabcdefghiklmnopqrstuvwxy1%,] [--color=when]
        [-D format] [file ...]
```

> 读懂这句：第一行的 `LS(1)` 是说明书的编号，先不用管。NAME（名字）：ls，列出文件夹里的内容。SYNOPSIS（用法概要）：ls 后面可以加的写法和文件名。

在说明书里可以用这几个键〔对照文档，界面可能不同〕：

| 按键 | 作用 |
|---|---|
| 空格 | 往下翻一页 |
| `/` 再输入一个词，回车 | 往下找这个词（大小写要一样）。屏幕最下面出现 `Pattern not found`，就是没找到：检查拼写和大小写 |
| `n` | 找下一处 |
| `q` | 退出，回到终端。Ctrl+C 在说明书里不管用，要按 `q` |

试一试：按 `/`，输入 `slash`（斜杠），回车。屏幕跳到这一段：

```text
     -F      Display a slash (‘/’) immediately after each pathname that is a
             directory, an asterisk (‘*’) after each that is executable, an at
             sign (‘@’) after each symbolic link, ...
```

> 读懂这句：-F：在每个文件夹的名字后面紧跟着显示一个斜杠 /，在可以运行的文件后面显示一个星号 *……

按 `q` 退出。英文不用全懂，抓住第一句就够了。

#### 3. 用查到的东西

`-F` 就是第 1 步说的选项，第 1.1 课细讲。第 1 站分不清 `map.txt` 和 `reading-room` 哪个是文件夹。先猜一猜：加上 `-F`，哪个名字后面会多一个 `/`？

```zsh
cd north/library
ls -F
```

你应该看到：

```text
map.txt         reading-room/
```

### 补全

把“查说明书”的空填上：

```text
man ____            ← 打开 ls 的说明书
按 ____ ，输入 slash，回车   ← 搜索
按 ____             ← 退出说明书
```

### 自己做

换一个文件夹、换一个要查的选项。先回到学习工作区（第 1 站「自己做」开头用过的那条 `cd`），再运行：

```zsh
python3 tools/course.py scenario 0.2b
```

它会告诉你要让 `ls` 换一种什么排列顺序，以及在说明书里搜哪个英文关键词。查到选项以后，在那个文件夹里用它运行 `ls`，记下排在最前面的文件名。检查会先问一道读报错的题，再问你查到的选项和那个文件名。

- 提示：`python3 tools/course.py hint 0.2b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 0.2b`

> **想多了解（可跳过）：网上常见的 `--help`**
>
> 网上很多教程让你用 `命令 --help` 看帮助。macOS 自带的很多命令不认这个写法，比如 `ls --help` 会说：
>
> ```text
> ls: unrecognized option `--help'
> usage: ls [-@ABCFGHILOPRSTUWXabcdefghiklmnopqrstuvwxy1%,] [--color=when] [-D format] [file ...]
> ```
>
> 读懂这句：ls：不认识 `--help` 这个选项。用法：ls 后面可以跟方括号里列出的这些写法，再跟文件名。
>
> 在这台 Mac 上，自带命令的用法看 `man`；以后要学的 `git`、`python3` 认 `--help`。

> **存档点 0.2b**：到这里可以安全停下。下次可以对导师说“从 0.2c 继续”。

## 第 3 站：给代码安个家（约 40 分钟）

### 概念

如果你的 Mac 打开了 iCloud 的“桌面与文稿”同步，`~/Desktop`（桌面）和 `~/Documents`（文稿）里的文件都存在 iCloud 云盘里，还会同步到你的其他设备。这种文件夹叫云同步文件夹（cloud-synced folder）。学习工作区在不在这样的文件夹里，第 3 步的 doctor 会告诉你。

打个比方：同步像一位勤快的管家，不停地把你桌上的纸一张一张拿去复印、寄走。可一个代码项目是成千上万个互相关联、随时在改的文件，这样拿会出事：

- 文件被悄悄改掉，或者被加上奇怪的标记；
- 空间紧张时，文件只留在云端，工具要用时取不到；
- 两台设备上改得不一样，冒出 `xxx 2` 这样的冲突副本。

这个类比在这里不成立：真的管家会问你一声，iCloud 不会。

这不是假设：Git（版本管理工具，第 1.6 课开始学）的官方常见问题（FAQ）明说：不要用云同步服务同步 Git 仓库（被 Git 管着的项目文件夹）的任何部分。网上也有公开的例子：有人把 Python 项目放在 iCloud 同步的“文稿”里，项目里的文件被加上了隐藏标记，程序突然报找不到项目自己的模块（问题报告见文末「想多了解」）。

所以代码放在一个不被同步的固定文件夹里；想在别处留一份，以后用远程仓库（放在 GitHub 这类网站上的另一份，第 1.12 课），不用网盘。本课程统一用 `~/Developer`；换成别的不被同步的文件夹（比如 `~/code`）也可以，那是个人偏好。

> **旧教程提醒**：以前很多入门教程让你“在桌面上新建项目文件夹”；自 macOS Sierra 10.12（2016 年）起，桌面和文稿可以同步到 iCloud，打开了同步再这样做，就会出上面的问题。

### 跟我做

本站新命令：`mkdir`（make directory，建文件夹）和它的选项 `-p`，以及课程工具的 `doctor`。

#### 1. 故意出错：建一个已经有的文件夹

这一站都在学习工作区里做（提示符里是 `fullstack-from-zero`）。`~/Developer` 已经有了：工具搭练习场景时，发现没有就会顺手建好。先猜一猜：再建一次会怎样？

```zsh
mkdir ~/Developer
```

你应该看到（`你的用户名` 那一段，你的会不一样）：

```text
mkdir: /Users/你的用户名/Developer: File exists
```

> 读懂这句：mkdir：/Users/你的用户名/Developer 已经存在了。报错里显示的是 `~` 换成完整地址以后的样子。

报错三问：谁在报错？`mkdir`。关键词？`File exists`，已经有了。我敲了什么？要建一个已经存在的文件夹。

#### 2. `mkdir -p`：有了就不动，没有就连中间的一起建

```zsh
mkdir -p ~/Developer
```

什么也没有输出，这就是成功了。`-p` 有两件本事（`man mkdir` 里写着）：中间缺的各层一起建出来；已经有了也不报错，多运行几次也没关系。

这一步要是也报 `File exists`，多半是 `-p` 的短横线打成了全角，学习工作区里会多出一个叫 `－p` 的空文件夹。切到英文重打，再对导师说“急救：学习工作区里多了一个 －p 文件夹”，导师带你把它移走。

试一下一条命令建好几层：小镇里的 `east` 和它里面的 `park` 都还不存在。

```zsh
mkdir -p ~/Developer/playground/0.2-start/town/east/park
ls ~/Developer/playground/0.2-start/town
```

你应该看到：

```text
east    north   south
```

#### 3. 让课程工具检查一遍环境

```zsh
python3 tools/course.py doctor
```

你会看到类似这样的报告（你的会不一样）：

```text
环境检查 · 2026-11-20
只看不改：这个命令不会改动你电脑上的任何设置。

✅ 没问题（10 项）
  - macOS 版本：27.2.1
  - 登录用的 shell：zsh 5.9（/bin/zsh）
  - python3：3.14.9（/usr/local/bin/python3，PATH 里排第一个的 python3）
  - Git：2.54.0 (Apple Git-157)
  - Git 身份：user.name 已设置，user.email 已设置（这里不显示内容）。
  - 提交签名：没有打开。
  - 新仓库的第一个分支名：main
  - 全局忽略文件：有（~/.gitignore_global）
  - ~/Developer 文件夹：有。
  - code 命令：有（/usr/local/bin/code）

⚠️ 需要处理（1 项）
  - 学习工作区的位置：~/Desktop/fullstack-from-zero，在 iCloud 同步的文件夹里（~/Desktop）。代码放在同步盘里容易出怪问题。 → 第 0.2 课会带你处理

仅提示（3 项）
  - Git 的编辑器：vi。提交时如果没写 -m，Git 会打开它，新手容易卡在里面。第 1.6 课会把它换掉。
  - GitHub CLI（gh）：还没安装。第 1.11 课会带你装，在那之前用不到。
  - 能不能连上 github.com：这次没有检查（要检查就加 --net）。

小结：有 1 项需要处理。每一项后面写了谁来处理，不用现在自己动手。

这份结果也存到了 learner/last-result.json，导师可以直接看。
```

报告分三组：「✅ 没问题」不用管；「⚠️ 需要处理」每一行的箭头后面写着哪一课来处理，现在不用动手；「仅提示」知道一下就行。很多词（提交签名、PATH、gh 等）后面的课会讲。这一站只看「学习工作区的位置」：上面这份报告里它在「需要处理」组，因为学习工作区在 iCloud 同步的桌面里。

#### 4. 家里的东西怎么起名：行规 WS-02

本课程里的名字用小写英文字母和数字，单词之间用短横线 `-` 连起来，比如 `my-site`，这叫短横线命名（kebab-case）；日期写成 `YYYY-MM-DD`。第 2 站的全角字符是原因之一，完整的理由和三类例外（比如 `README.md`）见文末「本课行规」的 WS-02。

### 补全

把空填上：

```text
mkdir ____ ~/Developer        ← 已经有了也不报错
python3 tools/course.py ____  ← 检查环境
「学习工作区的位置」在 doctor 报告的 ____ 组里   ← 看你自己的报告
```

### 自己做

这一次做的是真事：让以后每一课开头的 `cd ~/Developer/fullstack-from-zero` 都走得通。看你的 doctor 报告里「学习工作区的位置」那一行。

**它在「✅ 没问题」里，地址是 `~/Developer/fullstack-from-zero`**：已经在家了，直接运行检查。

**它在「⚠️ 需要处理」里，说在同步盘里**：两条路选一条。

**A. 请导师帮你搬（推荐）。** 对导师说“帮我把课程安置到 ~/Developer”。导师把整个学习工作区复制到 `~/Developer/fullstack-from-zero`，核对两边一样，旧的留着不删；笔记、日志和进度一起过去。Claude 桌面应用请你批准导师要运行的命令时，点允许：它要写到项目文件夹外面。〔对照文档，界面可能不同〕然后照 `README.md` 的卡片「搬家后怎么找回导师」开一个新会话，项目文件夹选 `~/Developer/fullstack-from-zero`。〔对照文档，界面可能不同〕在新会话的终端里运行 `pwd`，结尾是 `/Developer/fullstack-from-zero`，就在那里运行检查。

**B. 先留在原处（比 A 少用约 10 分钟）。** 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”。导师在 `~/Developer` 里放一个叫 `fullstack-from-zero` 的入口，通向学习工作区现在的位置，以后课文里的 `cd ~/Developer/fullstack-from-zero` 照样能用。建好以后运行检查。第 1.12 课之前会再问你一次；想搬，随时说 A 里的那句话。

**它在「✅ 没问题」里、地址却不是 `~/Developer/fullstack-from-zero`；或者它说入口还没有建（或没有通到学习工作区），不管在哪一组**：照 B 请导师建入口，再运行检查。

检查会请你再运行一次 doctor，说出那一行在哪一组；学习工作区还在同步盘里时，还会问你的决定。

- 提示：`python3 tools/course.py hint 0.2c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 0.2c`

> **想多了解（可跳过）：入口是什么，不靠导师怎么建**
>
> 入口是一个符号链接（symbolic link）：一个很小的特殊文件，里面只记着另一个文件夹的地址，`cd` 进它，就到了那个文件夹。自己建要两步。先确认那里还什么都没有（`-l` 显示详细信息，`-d` 只看这个名字本身、不进去看里面）：
>
> ```zsh
> ls -ld ~/Developer/fullstack-from-zero
> ```
>
> 应该看到 `ls: /Users/你的用户名/Developer/fullstack-from-zero: No such file or directory`。然后用一条命令建入口，前一个地址换成学习工作区真正的位置（doctor 里「学习工作区的位置」写着的那个；比如它在 `~/Desktop/fullstack-from-zero`，就是这一条）：
>
> ```zsh
> ln -sn ~/Desktop/fullstack-from-zero ~/Developer/fullstack-from-zero
> ```
>
> `ln -s` 建符号链接。`-n` 防的是一个坑：那里已经有入口时，带 `-n` 的命令会报 `File exists`，不带它的命令不报错，却会在学习工作区里面再建一个 `fullstack-from-zero`。建好以后运行 `ls -l ~/Developer`，会看到一行以 `fullstack-from-zero -> /Users/你的用户名/Desktop/fullstack-from-zero` 结尾。

> **想多了解（可跳过）：这台 Mac 不分大小写**
>
> 名字的大小写写错了，在这台 Mac 上照样能找到：
>
> ```zsh
> ls ~/developer
> ```
>
> 列出的是 `~/Developer` 里面的东西（至少有 `playground`）：`developer` 和 `Developer` 在这里是同一个地方。大多数网站服务器（server，放网页、让别人从网上访问的电脑）却区分大小写，在那里它们是两个不同的名字：在这台 Mac 上能用的写法，到了服务器上可能就找不到。这也是 WS-02 让名字全用小写的一个原因。

> **存档点 0.2c**：到这里可以安全停下。下次可以对导师说“从 0.2 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| WS-01 | 代码不放网盘同步目录。本课程统一放 `~/Developer`（本课程的约定；换别的不同步的文件夹是个人偏好） | 必须（适用范围：所有项目） | 惯例·平台与工具 | Git 官方常见问题 gitfaq（页面写着 last updated in 2.53.0）；Apple 支持文章 109344（2026-09-14）和《Mac 使用手册》（macOS 27） | 2026-11-20 |
| WS-02 | 名字用小写英文加短横线，日期写成 `YYYY-MM-DD`；Python 文件、约定俗成的大写名字、系统定的名字例外 | 必须（适用范围：本课程）；推荐（适用范围：所有项目），那个项目有自己的命名约定时按它的 | 规范·组织 | Google 开发者文档风格指南“Filenames and file types”；MDN“Dealing with files”（2026-09-11）；PEP 8；日期写法：ISO 8601 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

约束力说的是“有多强制、在哪里强制”，规则类型说的是“谁定的”，这是两回事。WS-01 对所有项目都是“必须”，可它不是法律，也不是标准组织发布的，而是 Git 这个工具自己的文档写明的要求：不遵守，没有人会罚你，但工具会出毛病。WS-02 的命名部分是一家公司（Google）给自己的文档作者定的规矩，很多人照着用；本课程采用了它，所以在课程里是“必须”，在别的项目里是“推荐”。第 0.3 课会细讲这些规则类型。

表里的出处：gitfaq 是 Git 官方的常见问题页；MDN 是 Mozilla 维护的网页技术文档；PEP 8 是 Python 官方的代码风格指南；ISO 8601 是日期和时间写法的国际标准。

## 收尾（约 15 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 0.2`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「WS-01 代码不放网盘同步目录」「WS-02 命名用小写英文加短横线」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 0.3 开始”。

## 想多了解

这一节都可以跳过。

用一个键切换中英文输入法〔对照文档，界面可能不同〕：打开 System Settings（系统设置）> Keyboard（键盘），在 Text Input（文字输入）那里点 Edit（编辑），打开 “Use the Caps Lock key to switch to and from …”（用大写锁定键切换）。以后按一下 Caps Lock 就能在中英文之间切换。这个选项只有在加了中文输入法以后才会出现。

- MDN“Dealing with files”（English）：文件命名为什么这样要求 https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Dealing_with_files
- Git 官方常见问题的“Transfers”一节（English）：为什么不能用云同步服务同步仓库 https://git-scm.com/docs/gitfaq
- Apple 支持《将“桌面”和“文稿”文件添加到 iCloud 云盘》（中文）https://support.apple.com/zh-cn/109344
- setuptools 的问题报告 4595（English）：项目在 iCloud 同步的“文稿”里，`.venv` 里的文件被加上隐藏标记，项目自己的包导入不了；报告人还把测试文件夹挪进“文稿”复现了一次 https://github.com/pypa/setuptools/issues/4595
- uv 的问题报告 16977（English）：项目放在“文稿”里，项目自己的包时好时坏，最后导入不了；后面的讨论里有人认为和 iCloud 同步有关 https://github.com/astral-sh/uv/issues/16977
