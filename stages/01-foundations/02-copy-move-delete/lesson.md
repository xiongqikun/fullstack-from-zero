# 1.2 终端：复制、移动、删除

> **用时** 2 站，约 85 分钟 ｜ **前置** 1.1 ｜ **核实** 2026-11-20 · macOS 27.2.1 · zsh 5.9
> **学完你能** 在终端里复制文件和整个文件夹、给文件改名和挪地方；建好你自己的网站文件夹 `~/Developer/my-site`；安全地删掉一批不要的文件，而不误删要留的
> **本课行规** TERM-02（见文末）

## 先想一想

你在 Finder 里把一个文件拖进废纸篓，后悔了，能找回来吗？如果是用碎纸机碎掉的呢？

先在心里答一下。第 2 站的“概念”里会回到这个问题。

## 第 1 站：复制和移动（约 30 分钟）

### 概念

复制和移动，都是“把东西从一个地方弄到另一个地方”。区别只有一个：

- **复制（copy）**：做一份一模一样的，原件还在原处。
- **移动（move）**：东西换了地方，原处就没有了。**改名也是移动**：在同一个文件夹里，从旧名字“移动”到新名字。

两条命令都要你说清：从哪里（来源），到哪里（目标）。格式是：

```text
命令  选项  来源  目标
```

还有一条规矩：**目标是一个已经存在的文件夹时，东西会被放进它里面**，而不是换掉它。

打个比方：复制像复印，原件还在你手里；移动像搬家，旧房子空了；改名像换门牌，房子没动。这个比方在一点上不成立：终端里的移动一眨眼就完成，而且**不会问你一句**，目标位置有同名文件也会直接盖掉。

本站的命令，名字都是英文缩写：

- `cp` = copy = 复制
- `cp -R` = copy recursive = 连同文件夹里的东西一起复制。**递归（recursive）** 的意思是“连同里面的文件夹、文件夹里的文件，一层一层全算上”（第 0.4 课 `zip -r` 里的 `-r` 也是它）
- `mv` = move = 移动（也用来改名）

### 跟我做

#### 1. 搭好练习场

先回到学习工作区，让工具搭一个练习用的文件夹：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.2
```

你应该看到：

```text
练习场景 1.2-start 搭好了。
位置：~/Developer/playground/1.2-start

这里有什么：
  练习用的文件在这里：~/Developer/playground/1.2-start

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.2-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.2 --reset
```

以前搭过的话，它会说“之前已经搭好了”，也没问题。进去看看：

```zsh
cd ~/Developer/playground/1.2-start
ls
```

你应该看到：

```text
notes.txt       recipes
```

`notes.txt` 是文件，`recipes` 是文件夹，里面有两份菜谱。`ls` 按窗口宽度分列，你的排法可能不一样，名字是一样的。用 `ls -a` 还会看到 `.playground`：那是工具的标记文件，别动它。

#### 2. 复制一个文件

先猜：执行完，`ls` 会多出什么？

```zsh
cp notes.txt notes-copy.txt
ls
```

你应该看到（`cp` 自己什么也不说，没有消息就是做完了）：

```text
notes-copy.txt  notes.txt       recipes
```

原件还在，多了一份 `notes-copy.txt`。

#### 3. 复制一个文件夹：先故意出一次错

用同样的写法复制文件夹 `recipes`：

```zsh
cp recipes recipes-copy
```

你应该看到：

```text
cp: recipes is a directory (not copied).
```

> 读懂这句：cp 说，recipes 是一个文件夹（directory），所以没有复制。

用“报错三问”读一遍：

- **谁在报错？** 开头是 `cp:`，是复制命令自己。
- **关键词是什么？** `is a directory`、`not copied`：它是文件夹，没复制。
- **我刚才敲了什么？** 让 `cp` 复制文件夹，却没告诉它“连同里面的东西”。

复制文件夹要加选项 `-R`，注意是大写的 R：

```zsh
cp -R recipes recipes-copy
ls recipes-copy
```

你应该看到：

```text
dumplings.txt   noodles.txt
```

网上不少教程是照着 Linux 写的，会用小写的 `cp -r`。在 Mac 上请用大写的 `-R`：Mac 自带的说明书 `man cp`（macOS 27.2 上的 2025-09-02 版，2026-11-19 核对）写着，`-r` 是历史遗留的选项，各个系统上的做法不一样，强烈不建议用。

#### 4. 目标已经存在时会怎样

先猜：`recipes-copy` 已经存在了。同一条命令再运行一次，会报错、覆盖，还是别的？

```zsh
cp -R recipes recipes-copy
ls recipes-copy
```

你应该看到：

```text
dumplings.txt   noodles.txt     recipes
```

`recipes-copy` 里多了一个 `recipes` 文件夹：目标是已有的文件夹，东西就被放进它里面。**同一条复制命令运行两次，就会多套一层。** 待会儿建网站文件夹时要记住这一点。

#### 5. 改名和移动

先猜：改名之后，`ls` 里还有 `notes-copy.txt` 吗？

```zsh
mv notes-copy.txt old-notes.txt
ls
```

你应该看到：

```text
notes.txt       old-notes.txt   recipes         recipes-copy
```

旧名字没了，新名字出现了：这就是在原地移动。再把它移进 `recipes-copy`，目标是已有的文件夹，所以它会被放进去：

```zsh
mv old-notes.txt recipes-copy
ls recipes-copy
```

你应该看到：

```text
dumplings.txt   noodles.txt     old-notes.txt   recipes
```

### 补全

在心里补上空着的部分，答案都在上面的步骤里：

1. 把 `notes.txt` 复制一份，叫 `notes-backup.txt`：`cp ________ ________`
2. 把 `notes-backup.txt` 改名为 `monday.txt`：`____ notes-backup.txt monday.txt`
3. 把文件夹 `recipes` 连同里面的东西复制一份，叫 `recipes-2`：`cp ____ recipes recipes-2`

### 自己做

这次是真的：建立你自己的网站文件夹。

学习工作区里有一份起步网页 `starter/my-site`，里面是 `index.html` 和 `style.css`。用你刚学的命令，在 `~/Developer` 里做出你自己的那一份：

- 最后要有文件夹 `~/Developer/my-site`，**里面直接**就是 `index.html` 和 `style.css`，不能多套一层；
- 学习工作区里的 `starter/my-site` 原件要留着（要复制，不是移动）。

命令只运行一次。做完用 `ls ~/Developer/my-site` 看一眼。这个文件夹之后的十几课都会用到，第 1.13 课它会上线。

- 提示：`python3 tools/course.py hint 1.2a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.2a`

> **存档点 1.2a**：到这里可以安全停下。下次可以对导师说“从 1.2b 继续”。

## 第 2 站：删除和安全（约 40 分钟）

### 概念

回到开头的问题。在 Finder 里选中一个文件，按 ⌘⌫（Command 键加 Delete 键），它会进**废纸篓（Trash）**；后悔了，在废纸篓里选中它，选菜单 File > Put Back（放回原处）就回去了；清倒废纸篓之后才真正没了。〔对照文档，界面可能不同〕

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

**`rm` 删东西不经过废纸篓。** 用它删掉的文件立刻就没了，没有“撤销”，删完一句话也不说。

它像碎纸机：塞进去就碎了。这个比方在一点上不成立：碎纸机只碎你亲手塞进去的那几张；`rm` 配上通配符（比如 `*.tmp`，一次代表一批名字，第 4 步细讲），一次能删掉一整批名字，其中可能有你没看见的。

所以本站只讲一个道理：**删之前先看清要删什么。** 可能还想要回来的东西，到 Finder 里删；终端里只删你确定不要的，比如练习场里的副本、临时文件。

本站三条命令：

- `rm` = remove = 删除文件
- `rm -r` = remove recursive = 连同文件夹和里面的东西一起删。`rm` 的 `-r` 和 `-R` 一样（`man rm`：`-r Equivalent to -R`），要分清大小写的是 `cp`
- `rmdir` = remove directory = 只删空文件夹，里面有东西就拒绝

第 1.1 课表里的 `rm -rf` 本课不用，见文末「想多了解」。

### 跟我做

还在上一站的练习场里做。关过终端的话，先进去：

```zsh
cd ~/Developer/playground/1.2-start
```

#### 1. 名字里有空格：先故意出一次错

先建一个名字里带空格的文件。两边的引号是英文半角的 `"`：

```zsh
touch "my list.txt"
```

引号要成对：提示符变成 `dquote>`，就是少了后一个引号，按 Ctrl+C 退出重敲。中文输入法的弯引号 `“ ”` 不算引号，会变成名字的一部分。

现在不加引号，直接删它：

```zsh
rm my list.txt
```

你应该看到：

```text
rm: my: No such file or directory
rm: list.txt: No such file or directory
```

> 读懂这句：rm 说，找不到叫 my 的文件或文件夹；也找不到叫 list.txt 的。

用“报错三问”读一遍：

- **谁在报错？** `rm:`，删除命令自己。
- **关键词是什么？** 两行都是 `No such file or directory`，它找的是 `my` 和 `list.txt` 两个名字。
- **我刚才敲了什么？** 空格把一个名字切成了两半，`rm` 以为我要删两个文件。

这次只是报错。可如果这里碰巧有个 `list.txt`，它已经没了。

第 0.2 课提过一次：名字里有空格，就用**引号（quotes）** 把整个名字括起来，让终端把它当成一个整体。这一站把它用熟：

```zsh
rm "my list.txt"
```

这次没有报错，`my list.txt` 就删掉了。所以课程让你起名用小写英文加短横线：没有空格，就不会被切开。

#### 2. 本课行规：删之前先看清

下面每一步都照课程定的这条规矩做：

> **TERM-02 删除前先看清要删什么**：先用 `ls` 加上和删除时一模一样的名字或通配符看一遍，确认列出来的正是要删的，再把 `ls` 换成 `rm`。（约束力、规则类型和出处见文末的「本课行规」。）

#### 3. 删文件夹

上一站做出来的 `recipes-copy` 已经没用了。（重搭过练习场、没有它的，先运行 `cp -R recipes recipes-copy`，下面会少两个名字。）按 TERM-02，删之前先看里面有什么：

```zsh
ls -a recipes-copy
```

你应该看到：

```text
.               dumplings.txt   old-notes.txt
..              noodles.txt     recipes
```

除了 `.` 和 `..`，都是副本，可以删。

为什么加 `-a`：第 1.1 课说过，名字以点开头的隐藏文件，`ls` 不列出来，`ls -a` 才看得见。`rm -r` 会连看不见的一起删；一个用 `ls` 看着是空的文件夹，`rmdir` 也可能说 `Directory not empty`（不是空的），因为里面藏着隐藏文件。所以删文件夹之前，用 `ls -a` 看一遍。

`rm` 默认只删文件，不加选项删文件夹，它会说 `rm: recipes-copy: is a directory`（这是一个文件夹）。连同文件夹和里面的东西一起删，加 `-r`：

```zsh
rm -r recipes-copy
```

它不会问你，`recipes-copy` 和里面的东西就都没了。

空文件夹用 `rmdir` 删。它只删空的，所以更安全。照样先看一眼：

```zsh
mkdir empty-box
ls -a empty-box
```

你应该看到：

```text
.       ..
```

只有 `.` 和 `..`，说明它是空的。删掉它：

```zsh
rmdir empty-box
```

什么都不显示，`empty-box` 已经没了。

#### 4. 通配符：先看，再删

**通配符（wildcard）** 是在名字里代替“任意几个字符”的符号，最常用的是 `*`。`*.tmp` 的意思是“所有以 `.tmp` 结尾的名字”。

先建三个临时文件，再按 TERM-02 用 `ls` 看通配符会选中哪些：

```zsh
touch a.tmp b.tmp c.tmp
ls *.tmp
```

你应该看到：

```text
a.tmp   b.tmp   c.tmp
```

正是要删的三个。现在把 `ls` 换成 `rm`，名字部分一个字不改：

```zsh
rm *.tmp
```

它什么也不说，三个文件已经没了。先猜：再运行一次 `ls *.tmp`，会看到什么？

```zsh
ls *.tmp
```

你应该看到：

```text
zsh: no matches found: *.tmp
```

> 读懂这句：zsh 说，没有任何名字能对上 *.tmp。

谁在报错？开头是 `zsh:`，不是 `ls:`。zsh 就是第 0.1 课说的 shell（命令解释器）：它先读懂你敲的整行，把 `*.tmp` 换成对得上的那些名字，再去叫 `ls` 或 `rm` 干活。这一次一个都对不上，`ls` 根本没运行：三个都删干净了。

### 补全

在心里补上空着的部分：

1. 删掉名字里有空格的文件 `old draft.txt`：`rm ________________`
2. 删掉所有以 `.log` 结尾的文件，按 TERM-02 先看再删：先 `____ *.log`，确认无误再 `____ *.log`

### 自己做

工具会搭一个“下载文件夹”，里面有该删的，也有要留的。

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.2b
```

你应该看到类似这样的说明。文件夹的名字（这里是 `old-ember` 和 `installer-olive`）和 `.tmp` 文件的个数每个人不一样，以你屏幕上的为准：

```text
练习场景 1.2b 搭好了。
位置：~/Developer/playground/1.2b

这里有什么：
  要清理的文件夹：~/Developer/playground/1.2b/downloads
  先进去：cd ~/Developer/playground/1.2b/downloads
  要删的：所有以 .tmp 结尾的文件；report copy.txt；空文件夹 old-ember；文件夹 installer-olive（连同里面的东西）
  其他的都要留下。删之前先数一数有几个 .tmp 文件，检查时会问你。

接下来：
  1. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.2b

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.2b --reset
```

目标：删掉工具列出的“要删的”那几样，其他的一个都不能少。删之前**数一数有几个 `.tmp` 文件**：检查看完文件夹会问你，输入一个数字，按回车。

第 1.1 课的检查提醒过你有东西建错了地方？本课收尾第 4 步会带你清掉它。全课检查只列出行规笔记和日志两件小事，第 4 步要照课文做，别跳过。

- 提示：`python3 tools/course.py hint 1.2b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.2b`

> **存档点 1.2b**：到这里可以安全停下。下次可以对导师说“从 1.2 的收尾继续”。

## 本课行规

这条是这门课定的规矩：不是标准，也没有人能因为你不遵守而罚你。它背后的事实来自官方资料：MDN（Mozilla 维护的网页技术文档网站）的命令行入门写明 `rm` 的删除是永久的、不能从废纸篓找回；Apple 的 Mac 使用手册写明 Finder 删除的东西进废纸篓，清倒之后才永久删除。

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| TERM-02 | 删除前先看清要删什么 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 规范·本课程约定 | 本课程约定（2026-11-19 版）；依据 MDN《Command line crash course》（2026-09-12 修改）和 Apple《Mac 使用手册》（macOS 27 版） | 2026-11-19 |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 15 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.2`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「TERM-02 删除前先看清要删什么」下面用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 清理第 1.1 课建错地方的东西（没有就跳过）：第 1.1 课里如果有东西建错了地方（检查提醒过的，比如学习工作区里多了 `memo` 或 `trip`；或者课文说过的、`mkdir －p x` 多建出来的 `－p` 文件夹），现在照 TERM-02 清掉：先 `cd` 到它所在的那一层，用 `ls -a 名字` 看清里面有什么，确认是建错的，再用 `rm -r 名字` 删掉。`－p` 里的横线是全角的，名字从 `ls` 的结果里复制最稳。学习工作区里的一定要清：第 1.12 课会把学习工作区里的东西都存进仓库。拿不准是不是建错的，先留着，问导师。

都做完，这一课就完成了。下次可以对导师说“从 1.3 开始”。

## 想多了解

下面的内容都可以跳过，不算进本课的时间。

**来源末尾的斜杠 `/`。** 在 Mac 上，`cp -R` 的来源末尾加不加 `/`，结果不一样：不加，复制的是文件夹本身；加了，复制的是文件夹里面的东西。下面是建课时在练习场里真实运行的结果，`backup` 是事先建好的空文件夹。每行开头的 `%` 是提示符（你终端里命令前面的那个 `%`），不用敲：

```text
% cp -R recipes backup
% ls backup
recipes
% cp -R recipes/ backup
% ls backup
dumplings.txt   noodles.txt     recipes
```

第一次，`backup` 里多了一个 `recipes` 文件夹；第二次，菜谱文件直接散落在 `backup` 里。`man cp` 写着：来源以 `/` 结尾时，复制的是“目录里的内容，而不是目录本身”。目标还不存在时，加不加斜杠结果一样；目标是已有的文件夹（比如 `~/Developer`）时，差别就出来了。抄来的命令如果来源末尾带斜杠，要多看一眼。

**`rmdir` 遇到不空的文件夹。** 它会拒绝，你会看到这样一句（建课时对装着东西的 `recipes-copy` 试过）：

```text
rmdir: recipes-copy: Directory not empty
```

> 读懂这句：rmdir 说，recipes-copy 这个文件夹不是空的。

**`rm -rf` 里的 `-f`。** `-f` = force = 强制：碰到受保护的文件也不先问你，名字不存在也不报错。和 `-r` 合在一起，就是“整个文件夹一声不响地删掉”。所以看到别人给的命令里有 `rm -rf`，先停下来看清它要删的是什么。

**`rm -i`：每删一个都先问你。** `-i` = interactive = 一问一答。把 `rm *.tmp` 写成 `rm -i *.tmp`，它会一个一个地问：

```text
remove a.tmp? y
remove b.tmp? n
```

> 读懂这句：remove a.tmp? 意思是“要删除 a.tmp 吗？”

每行末尾的 `y` 或 `n` 是你敲的：输入 `y`（yes）再按回车就删，输入 `n` 就跳过这一个。名字很多时一个一个答很累，所以它代替不了 TERM-02：先用 `ls` 看清，才是正路。

**zsh 对 `rm *` 多问的一句。** 单独一个 `*` 代表当前文件夹里的所有名字。对 `rm *`，zsh 会先问你，建课时在练习场里看到的是：

```text
zsh: sure you want to delete all 5 files in /Users/你的用户名/Developer/playground/1.2-start [yn]?
```

> 读懂这句：zsh 问，你确定要删除这个文件夹里的全部 5 个文件吗？回答 y 或 n。

你看到的个数会不一样，路径是完整的写法，用的是你自己的用户名。别指望这一句救你：它只管 `rm *` 和 `rm 某个文件夹/*` 这两种写法。像 `rm *.tmp`、`rm q*` 这样带了别的字符的，它一句也不问，建课时试过，`rm q*` 直接就删了。

> **旧教程提醒**：以前想从终端把文件放进废纸篓，教程会让你另外装一个第三方的 `trash` 工具；现在 macOS 15 起系统自带 `trash` 命令（建课时核对用的 Mac 上，`man trash` 写着 First appeared in macOS 15.0，2026-11-19 核对）。本课程阶段 1 不用它：可能还想要的东西，照样在 Finder 里删。

链接：

- MDN《Command line crash course》（English）：https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line
- Apple《在 Mac 上删除文件和文件夹》（中文，Mac 使用手册）：https://support.apple.com/zh-cn/guide/mac-help/mchlp1093/mac
- 在终端里运行 `man cp`、`man rm`，按空格翻页，按 `q` 退出（English）
