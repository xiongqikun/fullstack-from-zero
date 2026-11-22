# 1.3 终端：查找

> **用时** 2 站，约 75 分钟 ｜ **前置** 1.2 ｜ **核实** 2026-11-20 · macOS 27.2.1 · zsh 5.9 · grep 2.6.0（macOS 自带的版本）
> **学完你能** 在一堆文件里找出写着某个词的那一行，并说出它在哪个文件、第几行；按名字找出一个文件放在哪个文件夹里；拿到一条陌生的命令，先拆开说清每一块，再决定敲不敲。
> **本课行规** 没有新行规；第 2 站复习 TERM-01 不照抄看不懂的命令（见文末）

## 先想一想

你家有一个塞满文件袋的柜子。

- 情况一：你记得有张纸上写着“保修三年”，但不记得它在哪个袋子里。
- 情况二：你记得有个袋子的标签是“2025 装修”，但不知道它塞在柜子的哪一层。

这两种情况，哪一种得把纸抽出来一张张读？哪一种只看标签就够了？先在心里答一下，第 1 站的概念讲完后对答案。

## 第 1 站：找内容（约 35 分钟）

### 概念

`grep` 是按内容找的命令。你给它一串字和一个文件，它把文件从头到尾一行一行读，只把含有这串字的行打印出来。一行里含有你要找的那串字，就叫这一行**匹配（match）**上了。

记忆钩子：`grep` = global regular expression print = 在全文里找，找到就打印。正则表达式（regular expression）是一种更复杂的写法，本课不用。

格式和以前的命令一样，是“命令名、选项、对象”，这里的对象有两样：

```text
grep  [选项]  要找的字  在哪个文件里找
```

打个比方：`grep` 像一个拿着荧光笔的人，一行一行地扫，只把有那个词的行抄给你。这个比方在一处不成立：它不懂意思，只比对一模一样的字符。默认它**区分大小写（case-sensitive）**，也就是把大写和小写当成不同的字，`EUR` 找不到 `eur`。

对答案：情况一要读纸上的内容，就是 `grep` 干的事。情况二只看标签，是第 2 站的 `find`。

### 跟我做

#### 1. 先看一眼要搜的文件

回到学习工作区，用第 1.1 课学的 `cat` 看看汇率数据文件：

```zsh
cd ~/Developer/fullstack-from-zero
cat starter/hello-fx/rates.txt
```

你应该看到：

```text
# 示例数据：1 美元可以换多少其他货币。数字是为练习编的，不是真实汇率。
# 每行三列，用空格隔开：货币代码  中文名称  1 美元可换的数量
CNY  人民币    7.10
EUR  欧元      0.92
JPY  日元      150.00
GBP  英镑      0.79
HKD  港币      7.80
KRW  韩元      1350.00
SGD  新加坡元  1.34
AUD  澳元      1.52
```

#### 2. 找一行，带上行号：`-n`

`-n` 是 number 的意思：在每行前面标出它是文件的第几行。先猜：下面这条会打印几行？

```zsh
grep -n JPY starter/hello-fx/rates.txt
```

你应该看到：

```text
5:JPY  日元      150.00
```

只有含 `JPY` 的那一行被打印出来，其余九行都没出现。冒号前面的 `5` 是行号。对照上面 `cat` 的输出数一数：开头两行以 `#` 开头，叫**注释（comment）**：写给人看的说明文字。它们也算行，所以 `JPY` 在第 5 行。

#### 3. 什么也没打印，是什么意思

先猜：把 `JPY` 写成小写会怎样？

```zsh
grep jpy starter/hello-fx/rates.txt
```

你应该看到：什么也没有，提示符直接回来了。

这不是出错。**没有输出，意思是“一行也没匹配上”**。像第 5 步那样把文件名写错，grep 会打印一句报错（第 7 步会讲一个例外）。这里没匹配上，是因为 `grep` 区分大小写，文件里只有大写的 `JPY`。

#### 4. 不管大小写：`-i`

`-i` 是 ignore case 的意思：忽略大小写。

```zsh
grep -i jpy starter/hello-fx/rates.txt
```

你应该看到：

```text
JPY  日元      150.00
```

#### 5. 故意敲错一次

把文件名里的 `rates` 少敲一个 `s`：

```zsh
grep -n JPY starter/hello-fx/rate.txt
```

你应该看到：

```text
grep: starter/hello-fx/rate.txt: No such file or directory
```

> 读懂这句：grep 说，`starter/hello-fx/rate.txt` 这个文件或文件夹不存在。

用报错三问读它：

1. **谁在报错？** 行首写着 `grep:`，是 `grep` 这个程序。
2. **关键词是什么？** `No such file or directory`：没有这个文件或文件夹。
3. **我刚才敲了什么？** 文件名敲成了 `rate.txt`，真正的名字是 `rates.txt`。

改法：敲文件名时敲几个字母就按 Tab，让终端替你补全（第 0.2 课学过），就不会拼错。名字没拼错也报这句，多半是你不在学习工作区里：先 `pwd` 看看，再 `cd ~/Developer/fullstack-from-zero`。

报错里的名字是你要找的那个词（比如 `grep: JPY: No such file or directory`），多半是 `-n` 的短横线敲成了全角的 `－`：grep 把 `－n` 当成要找的字，把 `JPY` 当成了文件名。看到 `grep: invalid option -- ` 后面跟着乱码和一大段 `usage:`（usage 是“用法”，第 1.1 课见过），多半是 `-n` 后面敲成了全角空格。两种都切到英文输入法重敲。

> 和第 3 步对比一下：找不到**内容**时什么也不说；找不到**文件**时会报错。

#### 6. 在整个文件夹里找：`-r`

先猜：把对象换成文件夹 `starter`，会怎样？

```zsh
grep -n CNY starter
```

你应该看到：

```text
grep: starter: Is a directory
```

> 读懂这句：grep 说，`starter` 是一个文件夹。它默认只读文件，不进文件夹。

要让它钻进文件夹，加 `-r`（recursive）：就是第 1.2 课 `cp -R` 里说过的递归，不光看这一层，还一层一层钻进所有子文件夹里去看。

下面写的 `-rn` 就是 `-r` 加 `-n`：几个单字母选项可以合写在一个短横线后面（`-rin` 就是三个一起）。

```zsh
grep -rn CNY starter
```

你应该看到（「你的会不一样」：几行的顺序可能不同；第 0.1 课你把 `convert.py` 里的 `7.10` 改成了 `7.20`，`convert.py:8:` 那一行显示你改过的数）：

```text
starter/hello-fx/rates.txt:3:CNY  人民币    7.10
starter/hello-fx/convert.py:8:USD_TO_CNY = 7.10  # 1 美元换多少人民币。这是一个示例数字，不是真实汇率
starter/hello-fx/convert.py:12:    amount_cny = AMOUNT_USD * USD_TO_CNY
starter/hello-fx/convert.py:13:    print(f"{AMOUNT_USD} 美元 ≈ {amount_cny:.2f} 人民币（按 1 美元 = {USD_TO_CNY:.2f} 人民币计算）")
```

搜多个文件时，每行用冒号分成三段：**文件路径 : 行号 : 那一行的内容**。

注意后三行：`convert.py` 里没有单独的 `CNY`，是 `USD_TO_CNY` 里含着这三个字母。这就是“只比对字符，不懂意思”。

#### 7. 一个常见的卡住

只敲了 `grep JPY` 就回车、忘了写文件名，它不会报错，而是停下来等你从键盘输入，看起来像卡住了：光标停在新的一行，什么也不出现。要找的字和文件名之间敲成了全角空格，也会这样：两块连成了一块，grep 把它整个当成要找的字，还是没有文件名。按 Ctrl+C 停下它（第 0.1 课学过），改好再敲。〔建课时无法验证〕

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

### 补全

在学习工作区里，找出 `starter` 文件夹（包括它的子文件夹）里所有写着 `usd` 的行，不管大小写，还要显示行号。把空填上再敲：

```text
grep -___ usd ________
```

填对了，你会看到 4 行，都在 `convert.py` 里，每行开头是 `starter/hello-fx/convert.py:` 加一个行号。

### 自己做

先搭好这一课的练习场景。在学习工作区里运行：

```zsh
python3 tools/course.py scenario 1.3
```

你应该看到（「你的会不一样」：客户代号和文件名每个人不同）：

```text
练习场景 1.3-start 搭好了。
位置：~/Developer/playground/1.3-start

这里有什么：
  第 1 站要用：订单文件夹 ~/Developer/playground/1.3-start/orders
  要找的客户代号：juniper（文件里的大小写可能和这里不一样）
  第 2 站要用：备份文件夹 ~/Developer/playground/1.3-start/backup
  要找的文件：piano-plan.md

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.3-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.3 --reset
```

忘了自己的词，再运行一次同样的命令，它会把这些再显示一遍，不会重搭。

**目标**：`orders` 文件夹里是一家小店几个月的订单，分在好几层子文件夹里。其中只有一行写着场景给你的那个客户代号。找出这一行在哪个文件、第几行。

隐藏文件 `.playground` 是工具的标记文件，和这道题无关，别动它。

搜的时候报 `grep: orders: No such file or directory`，多半是还没进入练习场景：先 `cd ~/Developer/playground/1.3-start`，再搜。

检查会问两件事：哪个文件、第几行。

- 提示：`python3 tools/course.py hint 1.3a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.3a`

> **想多了解（可跳过）：旧教程里的 egrep 和 fgrep**
>
> grep 有两大家：GNU 版，是 GNU 这个自由软件项目写的，Linux（另一种操作系统，很多服务器用它）上常见；BSD 版，你的 Mac 自带的就是。以前的教程里常见 `egrep` 和 `fgrep` 两个命令。
>
> **旧教程提醒**：以前写 `egrep`、`fgrep`；现在写成 `grep -E`（按扩展的正则表达式来找）和 `grep -F`（把要找的字当成普通字符，一个也不特殊对待）。自 GNU grep 3.8（2022-09-02 发布）起，这两个旧命令一运行就提示它们已经过时（出处：GNU grep 3.8 的发布公告，https://lists.gnu.org/archive/html/info-gnu/2022-09/msg00001.html ，2026-11-20 核对）。有些 Linux 发行版（各家打包好、可以直接安装的 Linux，比如 Debian）在自己打包的版本里把这条提示关掉了；macOS 自带的 `egrep` 也不会提示（建课时实测）。没有提示，写法也照样跟着新的走。

> **存档点 1.3a**：到这里可以安全停下。下次可以对导师说“从 1.3b 继续”。

## 第 2 站：找文件（约 35 分钟）

### 概念

`find` 是按名字找文件的命令，名字就是英文的“找”。它从你给的起点文件夹开始，一层层往下翻，把名字对得上的文件一个个列出来。它不打开文件，不看里面写了什么。

```text
find  从哪里开始找  -name  "名字的模式"
```

- 起点可以写任何文件夹的路径；写 `.`，意思是“当前文件夹”。
- `-name` 是选项，意思是“按名字比对”。它虽然只有一个短横线，却是一整个词，不能像 `-rin` 那样拆成几个字母（find 的说明书把这类选项叫 primary，意思是“条件”）。
- 后面那一块是**模式（pattern）**：描述“名字长什么样”的写法。可以写全名，比如 `"style.css"`；也可以用第 1.2 课学过的通配符 `*`，比如 `"*.css"` 表示所有以 `.css` 结尾的名字。

打个比方：`find` 像在柜子里看标签找袋子，从你指定的那一层开始往下翻，只看标签，不拆开。这个比方在一处不成立：标签要和模式一字不差地对上才算，大小写也算数，`Convert.py` 对不上 `convert.py`。

带 `*` 的模式**一定要加引号**。第 1.2 课说过，`*` 是 shell 在命令运行之前先展开的。加了引号，shell 就不碰它，原样交给 `find`，由 `find` 去每一层子文件夹里比对。下面会看到不加引号时出什么事。

这一条不是本课程定的规矩，是 shell 本来的工作方式：规则类型是惯例·平台与工具；出处是 zsh 5.9 官方手册 Options 一章 NOMATCH 一条（没有匹配就报错；网页版现在是 5.9.2，https://zsh.sourceforge.io/Doc/Release/Options.html ，2026-11-20 核对，12 个月后复核）。bash（另一种常见的 shell）等别的 shell 也会先展开 `*`，只是一个也对不上时不报错。约束力是必须（适用范围：所有项目）：不加引号，轻则报错，重则悄悄漏找。

### 跟我做

#### 1. 按全名找

进入 `starter` 文件夹，找 `convert.py` 在哪：

```zsh
cd ~/Developer/fullstack-from-zero/starter
find . -name "convert.py"
```

你应该看到：

```text
./hello-fx/convert.py
```

读法：`./` 是起点（当前文件夹），`hello-fx` 是它所在的文件夹，最后是文件名。文件名前面紧挨着的那一段，就是“它所在的那一层文件夹”。

#### 2. 按模式找

先猜：这一层文件夹里有 `.css` 文件吗？`find` 能找到吗？

```zsh
find . -name "*.css"
```

你应该看到：

```text
./my-site/style.css
```

#### 3. 什么也没打印

```zsh
find . -name "Convert.py"
```

你应该看到：什么也没有，提示符直接回来了。和 `grep` 一样，没有输出就是“没找到”，不是出错。这里没找到，是因为 `-name` 区分大小写。

引号要用半角的 `"`。敲成中文输入法的全角引号 `“convert.py”`，同样什么也不打印：全角引号被当成了名字的一部分。

`-name` 的短横线敲成了全角的 `－`，find 不认它是选项，会先把当前文件夹里的东西全列一遍，最后报 `find: －name: No such file or directory`，下一行对引号里的名字也报同样的错：它把这两块都当成了起点，也就是要往下翻的文件夹。切到英文输入法重敲短横线。

#### 4. 故意出错：模式不加引号

还在 `starter` 里，把引号去掉：

```zsh
find . -name *.css
```

你应该看到：

```text
zsh: no matches found: *.css
```

> 读懂这句：zsh 说，`*.css` 没有找到任何匹配的名字。

用报错三问读它：

1. **谁在报错？** 行首是 `zsh:`，不是 `find:`。报错的是 zsh，`find` 根本没有运行。
2. **关键词是什么？** `no matches found`：没有匹配。
3. **我刚才敲了什么？** `*.css` 没加引号。zsh 先拿它去**当前这一层**（`starter`）里找以 `.css` 结尾的名字，这一层一个也没有（`style.css` 在下一层的 `my-site` 里），zsh 就停下来报错了。

改法：加上半角引号，写成 `"*.css"`，就是第 2 步的样子。如果你明明加了引号还看到这句，看看是不是全角的 `“*.css”`：报错会是 `zsh: no matches found: “*.css”`，引号也印在里面。

如果敲完回车，提示符变成了 `dquote>`，说明引号只敲了一个，zsh 在等你把它配对。按 Ctrl+C 回到正常的提示符，重敲一遍。〔建课时无法验证〕

### 补全：拆开一条命令

第 1.1 课的行规 TERM-01 说：不照抄看不懂的命令。拿到一条陌生的命令，先拆成几块，每块说出它做什么，说得清再敲。

拆开这一条，把右边一栏填上（写在纸上或心里都行）：

```text
grep -rin "h1" ~/Developer/playground/1.3-start/my-site
```

| 哪一块 | 它做什么 |
|---|---|
| `grep` | ______ |
| `-rin` | 三个选项合写：`-r` ______，`-i` ______，`-n` ______ |
| `"h1"` | ______（`h1` 是网页里大标题的标记，第 1.4 课细讲） |
| `~/Developer/playground/1.3-start/my-site` | ______ |

每一块都说得清了，再敲它。它只看不改，你应该看到两行：一行在 `index.html` 的第 11 行，一行在 `style.css` 的第 10 行。行首是 `/Users/你的用户名/...` 开头的完整路径，因为 zsh 先把 `~` 换成了你的主文件夹的完整路径。

### 自己做

**目标**：`~/Developer/playground/1.3-start/backup` 是一份旧电脑的备份，文件散在好几层子文件夹里。

1. 场景给了你一个文件名（`scenario 1.3` 输出里「这里有什么」下面「要找的文件：」那一行）。找出这个文件所在的那一层文件夹叫什么。
2. 数一数 `backup` 里（所有子文件夹都算）一共有几个名字以 `.csv` 结尾的文件。

做完回到学习工作区（`cd ~/Developer/fullstack-from-zero`）运行检查。它会问你三个问题：前两个是上面的两件事，第三个请你拆开一条命令，说出其中一块的意思。

- 提示：`python3 tools/course.py hint 1.3b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.3b`

> **想多了解（可跳过）：不加引号的另外两张脸**
>
> - 当前这一层有好几个对得上的文件时，zsh 把 `*` 换成这几个名字，`find` 收到的是 `-name` 后面跟着一串文件名。比如在学习工作区的最上层敲 `find . -name *.md`，会看到 `find: CLAUDE.md: unknown primary or operator`（find 说：`CLAUDE.md` 这一块它看不懂，既不是它认识的条件（primary，也就是 `-name` 这类选项），也不是它认识的连接词）。冒号中间是这一层按字母顺序排第二的 `.md` 文件名。
> - 当前这一层正好只有一个对得上的文件时，zsh 把 `*.md` 换成这一个名字，命令不报错，但 `find` 只去找同名的文件，别的全漏掉。数出来的个数比实际少、终端又没报错，多半就是这种情况。
> - 改法都一样：**模式里有 `*`，就加半角引号**。

> **想多了解（可跳过）：起点的两种写法**
>
> - 起点可以写任何路径，比如 `find ~/Developer/playground/1.3-start -name "*.css"`。打印出来的路径从起点开始写：起点是 `.`，就以 `./` 开头；起点是 `~/...`，zsh 先把 `~` 换成你的主文件夹，打印出来是 `/Users/你的用户名/Developer/playground/1.3-start/my-site/style.css` 这样的完整路径。
> - 网上很多教程是在 Linux 上写的，那里可以省掉起点，直接写 `find -name "*.css"`。在你的 Mac 上这样写会报错：
>
> ```text
> find: illegal option -- n
> usage: find [-H | -L | -P] [-EXdsx] [-f path] path ... [expression]
>        find [-H | -L | -P] [-EXdsx] -f path [path ...] [expression]
> ```
>
> 读懂这句：find 说 `-n` 是不认识的选项，并给出用法：先写路径，再写条件。Mac 上的 find 在起点之前只收单字母选项；起点省掉了，它就把 `-name` 当成 `-n -a -m -e` 几个合写的单字母选项去读，第一个 `-n` 就不认识。所以在 Mac 上起点不能省。

> **存档点 1.3b**：到这里可以安全停下。下次可以对导师说“从 1.3 的收尾继续”。

## 本课行规

本课没有新行规。第 2 站的「补全」复习的是第 1.1 课的这一条：

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| TERM-01 | 不照抄看不懂的命令 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 规范·本课程约定 | 本课程约定，依据 MDN（Mozilla 办的网页开发文档站）的命令行教程和 Microsoft 安全团队的分析（出处见卡片） | 2026-11-20 |

在这门课里必须照做；离开这门课以后，也建议在所有项目里照做。规则类型是规范·本课程约定，也就是这门课自己定的规矩。完整卡片（出处网址、正例反例）在第 1.1 课文件夹的 `rules.md`：`stages/01-foundations/01-create-and-view/rules.md`。

用在今天的两个命令上：`grep` 和 `find -name` 只看不改，拆错了也弄不坏文件；会改动或删除文件的命令（比如第 1.2 课的 `rm`），说不清每一块就不要敲。

## 收尾（约 5 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.3`
2. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 1.4 开始”。

## 想多了解

这一节都可以跳过。

- 本机手册：`man grep`、`man find`（按 q 退出）。英文，写的正是你电脑上的这两个版本。
- MIT《The Missing Semester of Your CS Education》2026 版第 1 讲，在 “What is available in the shell?” 一节里讲了 `grep` 和 `find`（英文）：https://missing.csail.mit.edu/2026/course-shell/
- 同一门课 2020 版“Shell 工具和脚本”一讲的中文译本，查找文件、查找代码两节讲得更细，也提到了更快的查找工具 ripgrep（中文；2020 版，个别写法比本课旧）：https://missing-semester-cn.github.io/2020/shell-tools/
