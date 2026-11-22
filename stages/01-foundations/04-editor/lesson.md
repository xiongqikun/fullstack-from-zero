# 1.4 编辑器 VS Code

> **用时** 3 站，约 125 分钟 ｜ **前置** 1.3 ｜ **核实** 2026-11-20 · VS Code 1.145.2 · macOS 27.2 · zsh 5.9
> **学完你能** 在终端里用 `code .` 打开一个项目文件夹，改网页、保存、在浏览器里看到变化；用命令面板、快速打开、跨文件搜索和内置终端找东西；给自己的网站写一份 `.editorconfig`。
> **本课行规** ED-01、ED-02（见文末）

这一课大部分步骤在 VS Code 的窗口里，建课的人没法替你点，只能对照官方文档写，所以标着〔对照文档，界面可能不同〕。

课文里的按键符号：⌘ 是 Command 键，⇧ 是 Shift 键，⌃ 是 Control 键。⇧⌘P 就是按住 Shift 和 Command，再按 P。

## 先想一想

你在网上填一张报名表，每一栏都填好了，但没点「提交」就关掉了网页。主办方那边收到你的报名了吗？

先记下你的答案，第 1 站会回头对。

## 第 1 站：打开文件夹，改网页，在浏览器里看（约 40 分钟）

### 概念

第 0.1 课你用 `code` 在编辑器 VS Code 里打开过一个文件；这一课换一种方式：打开整个项目文件夹，改完再保存。

把 VS Code 想成一张工作台。打开文件夹，是把整个项目摆上台面；你在台面上改；保存，才是把改好的放回柜子。浏览器和检查工具看的，都是柜子里的文件。

这个类比在哪里不成立：文件从来没离开文件夹。台面上摆的只是“正在改的样子”，没保存前，它和文件里存的不一样。

### 跟我做

#### 1. 搭一个练习用的网站副本

在你平时敲命令的终端里：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.4
```

你应该看到：

```text
练习场景 1.4-start 搭好了。
位置：~/Developer/playground/1.4-start

这里有什么：
  网站的副本在这里：~/Developer/playground/1.4-start/my-site

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.4-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.4 --reset
```

这个副本照起步网页 `starter/my-site`（第 1.2 课你复制过它）搭，也就是你的 `~/Developer/my-site` 在上这一课之前的样子。「跟我做」在副本里练，「自己做」再动你自己的网站。

#### 2. 一个故意的错：在错的地方打开网页

`open` 是 macOS 自带的命令，意思就是“打开”：用这个文件平时该用的程序打开它，网页文件就用浏览器打开。

照工具给的第 1 步进入练习场景，然后直接打开网页。先猜：会打开吗？

```zsh
cd ~/Developer/playground/1.4-start
open index.html
```

你应该看到（`/Users/` 后面是你的用户名）：

```text
The file /Users/你的用户名/Developer/playground/1.4-start/index.html does not exist.
```

> 读懂这句：文件 /Users/…/1.4-start/index.html 不存在。

用报错三问读它：

- 谁在报错？`open` 这个程序。
- 关键词是什么？`does not exist`（不存在）。它还把它找的完整路径印出来了。
- 我刚才敲了什么？`open index.html`，而我站在 `1.4-start` 里。`index.html` 在下一层的 `my-site` 里面。

进到网站副本里，再看一眼有什么：

```zsh
cd my-site
ls
```

你应该看到：

```text
index.html	style.css
```

#### 3. 先照老办法：只打开一个文件〔对照文档，界面可能不同〕

如果 VS Code 已经开着，先把它整个退出：点一下它的窗口，在屏幕最上面的菜单栏选 `Code > Quit Visual Studio Code`（退出 VS Code）。不退出，文件会塞进开着的那个窗口里。

```zsh
code index.html
```

如果先弹出第 0.1 课见过的 `Do you want to allow untrusted files in this window?`（要不要在这个窗口里打开不受信任的文件？），照那时一样点 `Open`。VS Code 打开一个窗口，里面只有 `index.html`。看左边的资源管理器（Explorer，列出文件的那一栏；没看到就按 ⇧⌘E）：它写着 `NO FOLDER OPENED`（没有打开文件夹），旁边的 `style.css` 根本看不见。资源管理器里如果还是上次开过的文件夹（VS Code 会恢复上次的窗口），选 `File > Close Folder`（关闭文件夹），再运行一次 `code index.html`。

再照上面的办法退出 VS Code。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

#### 4. 打开整个文件夹〔对照文档，界面可能不同〕

```zsh
code .
```

`.` 在终端里代表“我现在所在的文件夹”。`code .` 就是“用 VS Code 打开我脚下这个文件夹”。点和它前面的空格都要用半角：输入法在中文状态会打出 `。`，VS Code 就会去打开一个叫 `。` 的文件，而不是这个文件夹。

窗口上方会出现一条横幅：

```text
Restricted Mode is intended for safe code browsing. Trust this folder to enable all features.
```

> 读懂这句：受限模式是为了安全地浏览代码。信任这个文件夹，才能用上全部功能。

受限模式（Restricted Mode）是 VS Code 的安全模式：文件能看能改，但它不会替你运行文件夹里的东西。这个文件夹是课程工具刚搭的，可以信任：点横幅上的 `Manage`（管理），在打开的 Workspace Trust 页面上点 `Trust`（信任）。这就是第 0.1 课见过的工作区信任；这里的“工作区”指你打开的文件夹，不是学习工作区。别人发来的文件夹，先别急着信任。

> **旧教程提醒**：以前（1.57 版起，2021 年）打开新文件夹时，VS Code 会先弹出对话框问你信不信任；现在（自 1.126 版，2026-06-24 起）新文件夹先在受限模式里打开，只显示这条横幅，由你决定。

第 0.1 课那个对话框问的是单个文件，这条横幅问的是整个文件夹，是两回事。

现在看左边的资源管理器：最上面写着 `MY-SITE`，下面是 `index.html` 和 `style.css`。项目里的文件全在台面上了。

#### 5. 改一处，先别保存，在浏览器里看〔对照文档，界面可能不同〕

在资源管理器里单击 `index.html`，它在右边打开，上方多了一个写着文件名的标签页。第 6 行是：

```html
  <title>我的第一个网页</title>
```

尖括号里的 `<title>` 和 `</title>` 叫标签（tag），告诉浏览器中间的字是网页标题，显示在浏览器的标签页上。VS Code 顶上每个文件的小格子叫标签页（第 0.1 课见过），后面几课也简称“VS Code 的标签”，和网页里的标签（tag）是两回事。只改两个标签中间的字，改成：

```html
  <title>练习：改标题</title>
```

先别保存。看 VS Code 标签页上的文件名：旁边多了一个实心圆点。圆点的意思是“改动还在台面上，还没保存”。

回到你敲命令的终端（还在 `my-site` 副本里）。先猜：浏览器标签页上会显示哪个网页标题？

```zsh
open index.html
```

浏览器打开网页，标签页上还是“我的第一个网页”，因为文件还没保存。

#### 6. 保存，再刷新〔对照文档，界面可能不同〕

回到 VS Code，按 ⌘S 保存。圆点消失了。再回到浏览器，按 ⌘R 刷新：标签页上变成了“练习：改标题”。

对一对“先想一想”：没点「提交」，主办方收不到；没按 ⌘S，浏览器看到的也还是旧文件。想让 VS Code 自动保存，见文末「想多了解」。

### 补全

在纸上或心里把空填上，然后对照上面的步骤：

```text
1. 进入你自己的网站文件夹：cd ________
2. 用 VS Code 打开整个文件夹：code ___
3. 改完以后，标签页上有圆点，按 ____ 保存
4. 在终端里用浏览器看网页：open __________，浏览器里按 ⌘R 刷新
```

### 自己做

目标：改你自己的网站 `~/Developer/my-site`。不是练习场的副本，也不是学习工作区里的 `starter/my-site`（那是课程的原件，不是你的网站）。

1. 在 VS Code 里打开整个 `~/Developer/my-site` 文件夹。这是另一个文件夹，窗口上方又会出现受限模式的横幅，照第 4 步信任它。
2. `<h1>` 和 `</h1>` 中间是网页的大标题（h1 是第一级标题）。把 `<h1>你好，我是____</h1>` 里的空填上名字，下划线一起删掉。用笔名就可以：这个网页第 1.13 课会公开到网上，谁都看得到。
3. `<p>` 和 `</p>` 中间是一段话（p 是 paragraph，段落）。把这一段换成你自己写的一句话。
4. 保存，用浏览器打开这个网页，看大标题和那段话变了没有。

刚才你先只开了一个文件，左边什么都没有；打开文件夹以后，整个项目才摆上台面。这就是本课第一条行规 ED-01：做项目时打开项目文件夹，而不是单个文件（卡片摘要见文末）。

- 提示：`python3 tools/course.py hint 1.4a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.4a`

> **存档点 1.4a**：到这里可以安全停下。下次可以对导师说“从 1.4b 继续”。

## 第 2 站：命令面板、快速打开、搜索和内置终端（约 30 分钟）

### 概念

VS Code 有几千个功能，菜单里放不下，也没人记得住每个按钮在哪。它的办法是：每个功能都有一个英文名字，按 ⇧⌘P 打开命令面板（Command Palette），输入名字里的几个词，就能找到并使用这个功能。官方文档的原话是，从这里“你可以用到 VS Code 的全部功能”。

把命令面板想成商场的总服务台：不用记每家店在几楼，说出名字，服务台带你去。

这个类比在哪里不成立：服务台的人能听懂你的意思，命令面板只按字面去匹配功能的英文名字。这门课按英文界面的 VS Code 写；英文界面里，输入中文找不到功能。

同一个“按名字找”的办法，还有两个用处：

| 快捷键 | 名字 | 按什么找 |
|---|---|---|
| ⇧⌘P | 命令面板（Command Palette） | 功能的名字 |
| ⌘P | 快速打开（Quick Open） | 文件名 |
| ⇧⌘F | 跨文件搜索（search across files） | 所有文件里的文字 |

> **旧教程提醒**：以前 VS Code 每个月发一个新版本，版本按月份起名（例如 1.110 版叫 February 2026，2026-03-04 发布），教程截图能用很久；现在每周发一个稳定版（正式给大家用的版本；自 1.111 版，2026-03-09 起）。所以这门课教你记功能的名字（在命令面板里搜），不教你记按钮在屏幕上的位置。

### 跟我做

#### 1. 搭练习场，用 VS Code 打开

在你平时敲命令的终端里：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.4b
```

你应该看到：

```text
练习场景 1.4b 搭好了。
位置：~/Developer/playground/1.4b

这里有什么：
  学习笔记在这里：~/Developer/playground/1.4b/study
  用编辑器打开它：cd ~/Developer/playground/1.4b/study，然后 code .

接下来：
  1. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.4b

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.4b --reset
```

照「这里有什么」的第二行做，这正是第 1 站学的动作：

```zsh
cd ~/Developer/playground/1.4b/study
code .
```

〔对照文档，界面可能不同〕新窗口里同样有受限模式的横幅。这个文件夹也是课程工具搭的，照第 1 站的办法信任它：下一步要用终端，受限模式里 VS Code 不让开终端。

这是一个学习笔记的文件夹：每个月一个子文件夹，里面是几份 `.md` 结尾的笔记（一种纯文本笔记，第 1.5 课细讲）。

#### 2. 用命令面板打开内置终端〔对照文档，界面可能不同〕

按 ⇧⌘P，输入 `new terminal`，列表里出现 `Terminal: Create New Terminal`（终端：新建终端），按回车。

窗口下方出现一个终端，这就是内置终端（integrated terminal）。它不是另一种终端，里面跑的还是你平时用的 zsh，只是换了一个窗口，提示符也一样：`你的用户名@你的电脑名 study %`。它从 VS Code 打开的那个文件夹开始。在内置终端里敲：

```zsh
pwd
```

你应该看到（你的用户名会不一样）：

```text
/Users/你的用户名/Developer/playground/1.4b/study
```

下次打开命令面板时，留意那一行右边写着的快捷键：⌃⇧`，就是新建终端。只想把终端面板收起或打开，按 ⌃`（` 是数字 1 左边那个键）。

#### 3. 一个故意的错：文件在哪一层？

笔记里有一份 `plan.md`。在内置终端里直接看它，先猜：能看到吗？

```zsh
cat plan.md
```

你应该看到：

```text
cat: plan.md: No such file or directory
```

> 读懂这句：cat：plan.md：没有这个文件或文件夹。

报错三问：谁在报错？`cat`。关键词？`No such file or directory`。我刚才敲了什么？`cat plan.md`，而 `plan.md` 不在我脚下这一层，在某个月份的子文件夹里。是哪一个？

#### 4. 快速打开：按文件名找〔对照文档，界面可能不同〕

按 ⌘P，输入 `plan`。列表里出现 `plan.md`，右边的灰字是它所在的文件夹：`2026-10`。按回车，它就在编辑器里打开了。

知道了位置，回到内置终端，带上这一层再看：

```zsh
cat 2026-10/plan.md
```

你应该看到：

```text
# 这个月的计划

1. 学会用编辑器打开整个文件夹
2. 给网站写一份 README
```

#### 5. 跨文件搜索：按文字找〔对照文档，界面可能不同〕

哪几份笔记提到了“汇率”？按 ⇧⌘F，在左边的搜索框里输入 `汇率`。结果按文件分组：`terminal.md` 和 `website.md` 两个文件，每个文件下面是写着“汇率”的那一行，点一下就跳到那里。

它找的是你打开的这个文件夹里的所有文件。只打开一个文件时，它只搜已经打开的文件，这也是 ED-01 要你打开整个文件夹的原因之一。

同样的事，第 1.3 课的 `grep` 在内置终端里也能做：

```zsh
grep -rn 汇率 .
```

你应该看到（两行的先后顺序你的可能不一样）：

```text
./2026-11/website.md:3:想在网页上放一个汇率换算的小工具。
./2026-09/terminal.md:4:顺手查了一次美元兑人民币的汇率。
```

两种办法都对。编辑器里点结果就能跳过去改；终端里的结果可以接着用别的命令处理。

### 补全

在纸上或心里填空：

```text
想按名字用一个功能（比如新建终端）：按 ______
想按文件名打开一个文件：按 ____
想在所有文件里找一串字：按 ______
想把终端面板收起或打开：按 ____
```

### 自己做

目标：同一个 `study` 文件夹里，有一份笔记写着一行以“暗号：”开头的字。找到它在哪个文件里。

用 ⇧⌘F 或者内置终端都行。检查会问你一个问题：暗号写在哪个文件里。回答文件名（比如 `xxx.md`；带不带它所在的文件夹都行）。检查命令也可以在内置终端里运行：先 `cd ~/Developer/fullstack-from-zero`。

- 提示：`python3 tools/course.py hint 1.4b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.4b`

> **存档点 1.4b**：到这里可以安全停下。下次可以对导师说“从 1.4c 继续”。

## 第 3 站：编码、换行和 .editorconfig（约 40 分钟）

### 概念

文字存进文件时，要按一张对照表变成一串数字，这张表叫字符编码（character encoding）。读文件的程序再按一张表把数字变回文字。两边用的不是同一张表，就出乱码。UTF-8 是现在全世界通用的那一张，VS Code 默认按它读写。

文件里还有一种看不见的字符，表示“这一行结束了”，叫换行符（line ending）。Mac 用 LF（line feed，换行）一个字符，Windows 常用 CRLF（回车加换行）两个字符。两种混着用，一行字没改，以后的 Git（第 1.6 课开始学的、记录改动的工具）也会把整行算成改过。

编码和换行合在一起，就是一个文本文件的“格式”。把它像电报码本一样想：发报的和收报的拿同一本码本，才对得上。

这个类比在哪里不成立：收报员发现码本不对会停下来；电脑不会，它照样往下读，只是读出乱码。所以格式要事先写成约定，放在项目里。

### 跟我做

#### 1. 搭练习场，用 VS Code 打开

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.4-notes
```

你应该看到：

```text
练习场景 1.4-notes 搭好了。
位置：~/Developer/playground/1.4-notes

这里有什么：
  两份笔记在这里：~/Developer/playground/1.4-notes/notes
  用编辑器打开它：cd ~/Developer/playground/1.4-notes/notes，然后 code .

接下来：
  1. 回到学习工作区：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.4-notes --reset
```

「接下来」那一行是回学习工作区，先不用照做；照「这里有什么」的第二行打开它：

```zsh
cd ~/Developer/playground/1.4-notes/notes
code .
```

〔对照文档，界面可能不同〕照第 1 站的办法信任这个文件夹。两份笔记是“两台电脑写的”：`today.md` 是你在这台 Mac 上写的，`old-pc.txt` 来自一台旧的 Windows 电脑。

#### 2. 亲眼看一次乱码〔对照文档，界面可能不同〕

按 ⌘P，输入 `old`，选中 `old-pc.txt`，按回车。打开的是一堆问号一样的符号，读不出字。再看窗口最下面那一条状态栏的右边：这个文件那里写着 `CRLF`；切到 `today.md`，那里写着 `LF`。这就是两种换行符。

再按 ⇧⌘F，搜 `汇率`。结果只列出 `today.md` 一个文件。`old-pc.txt` 里明明也写着“汇率”，却搜不到。

原因：`old-pc.txt` 是旧电脑按 GBK（以前中文 Windows 常用的一张表）存的。VS Code 按 UTF-8 去读，就成了乱码；按 UTF-8 去搜，也找不到。

#### 3. 一个故意的错

这个文件夹里有没有一份写着约定的文件？照第 2 站的办法打开内置终端（⇧⌘P，输入 `new terminal`），试试。先猜：会看到什么？

```zsh
cat .editorconfig
```

你应该看到：

```text
cat: .editorconfig: No such file or directory
```

> 读懂这句：cat：.editorconfig：没有这个文件或文件夹。

报错三问：谁在报错？`cat`。关键词？`No such file or directory`。我刚才敲了什么？要看一个还不存在的文件。下面就来建它。

#### 4. 写一份 .editorconfig〔对照文档，界面可能不同〕

EditorConfig 是一种公开、有版本号、很多编辑器都照着做的约定写法（2026-11-20 核对时是 0.17.2 版），规则卡上算作“惯例·事实标准”。约定写在项目最外层一个叫 `.editorconfig` 的文件里：开头有一个点，全是小写，后面不加 `.txt` 之类的结尾。

在 VS Code 左边的资源管理器里，把鼠标移到 `NOTES` 那一行上，点出现的 `New File...`（新建文件）图标，输入 `.editorconfig`，回车。在打开的空文件里写下面几行，最后一行写完也按一次回车：

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
```

按 ⌘S 保存。每一行的意思：

- `root = true`：这是最外层的一份，编辑器不用再往上一层文件夹里找。它要写在第一个方括号之前。
- `[*]`：方括号里写“下面几行管哪些文件”，`*` 是所有文件。
- `charset = utf-8`：用 UTF-8 存。中间有短横线；写成 `utf8`，EditorConfig 不认，编辑器会悄悄忽略。你网页第 4 行的 `<meta charset="utf-8">` 是同一个意思，那是写给浏览器看的。
- `end_of_line = lf`：换行符用 LF。
- `insert_final_newline = true`：文件最后留一个换行，就是你刚才在最后一行按的那次回车。

符号全部用半角。输入法如果还在中文状态，`=` 和 `[ ]` 很容易变成全角的 `＝`、`【 】` 或 `［ ］`，EditorConfig 不认。

这份文件管的是“以后怎么存”，它不会把已经存好的 `old-pc.txt` 变回正常的字。

〔对照文档，界面可能不同〕VS Code 自己不读 `.editorconfig`（建课时核对的 1.145.2 是这样）：要装一个扩展（extension，给 VS Code 加功能的附加程序）它才会照着做。你打开这个文件时，右下角可能弹出提示，问要不要安装推荐的 EditorConfig 扩展。装不装都能通过这一站的检查；怎么装，见文末「想多了解」。

### 补全

`.editorconfig` 还能只管某一种文件，比如缩进（indentation，一行开头空出来的那一段）。缩进用两个设置写：`indent_style`（用 `space` 空格还是 `tab` 制表符：按 Tab 键打出的那一个看不见的字符）和 `indent_size`（每层几格）。只管名字以 `.md` 结尾的文件，方括号里写 `[*.md]`。

在纸上或心里填空：想在文件最后加一块，让 `.md` 文件用空格缩进，每层 4 格。

```ini
[*.___]
indent_style = _____
indent_size = _
```

### 自己做

目标：给你自己的网站 `~/Developer/my-site` 写一份 `.editorconfig`：

- 它是最外层的一份；
- 所有文件用 UTF-8、换行用 LF、文件最后留一个换行；
- 网页文件（`.html`）和样式文件（`.css`，管网页长什么样）用空格缩进，每层 2 格（起步网页现在就是这么缩进的）。

最省事的做法：用第 1.2 课的 `cp` 把 `notes` 里那份复制到 `~/Developer/my-site`，再在 `my-site` 的 VS Code 窗口里打开它，照补全的样子在最后加两块：一块管 html，一块管 css。从头写也可以。复制完用 `ls -a ~/Developer/my-site` 看：名字以点开头，`ls` 不加 `-a` 不会列出它（第 1.1 课）。

没装扩展时，通过的结果里会多一行补充，你应该看到：

```text
  补充：
    - VS Code 里还没装 EditorConfig 扩展：这个文件现在只对认识它的工具起作用。
```

你刚才亲眼看到了乱码和搜不到。把格式写成约定放进项目，就是本课第二条行规 ED-02（卡片摘要见下面）。

- 提示：`python3 tools/course.py hint 1.4c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.4c`

> **存档点 1.4c**：到这里可以安全停下。下次可以对导师说“从 1.4 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| ED-01 | 打开文件夹而不是单个文件 | 推荐（适用范围：所有项目） | 惯例·平台与工具 | VS Code 官方文档（介绍界面、终端、在 Mac 上安装的三页，页面日期 2026-11-18） | 2026-11-20 |
| ED-02 | 文本统一 UTF-8 和 LF，用 `.editorconfig` 说明 | 推荐（适用范围：所有项目）；在本课程的 `my-site` 和学习工作区里是必须（适用范围：本课程） | 惯例·事实标准（EditorConfig 是写下这些约定的公开格式，它本身不规定用 UTF-8 还是 LF；UTF-8 这一半另有标准撑腰：WHATWG HTML 标准要求网页里声明编码的 `<meta charset>` 写 utf-8；LF 这一半出自 Git 官方 FAQ，属于惯例·平台与工具） | EditorConfig 规范 0.17.2（EditorConfig 项目发布的公开规范）；Git 官方 FAQ（Git 自己的常见问题文档，页面写着最后更新于 Git 2.53.0）；WHATWG（制定网页 HTML 标准的组织）的 HTML 标准 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 15 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.4`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「ED-01 打开文件夹而不是单个文件」「ED-02 文本统一 UTF-8 和 LF，用 .editorconfig 说明」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 1.5 开始”。

## 想多了解

这一节都可以跳过。

> **想多了解（可跳过）：自动保存**〔对照文档，界面可能不同〕
> 菜单 `File > Auto Save`（文件 > 自动保存）是一个开关。打开以后，你停手约一秒，VS Code 就替你保存，标签页上不再出现圆点。默认是关着的，要你自己按 ⌘S。开不开是个人偏好，没有哪条规范规定；只要记住，浏览器和检查工具看的都是保存以后的文件。

> **想多了解（可跳过）：装上 EditorConfig 扩展**〔对照文档，界面可能不同〕
> 没装时，`.editorconfig` 是写给人和工具看的约定：本课的检查和以后的考题会看它，自带 EditorConfig 支持的编辑器会照它做。在那条推荐提示上点 `Install`（安装）；没看到提示就按 ⇧⌘X 打开扩展（Extensions）视图（命令面板里叫 `View: Show Extensions`），在搜索框里输入 `EditorConfig`，选发布者（publisher）是 EditorConfig 的那一个，点 `Install`。第一次装这个发布者的扩展时，VS Code 会问你信不信任它，确认发布者是 EditorConfig 再点 `Trust Publisher & Install`。装上以后，VS Code 保存文件时才会照 `.editorconfig` 的约定去做。

> **想多了解（可跳过）：一块管两种文件**
> 管 html 和管 css 的两块写的一样，可以合成一块：方括号里用花括号把两种结尾括起来，逗号隔开，写成 `[*.{html,css}]`。逗号旁边不要加空格：EditorConfig 会把空格也当成文件名的一部分。两种写法检查都认。

> **想多了解（可跳过）：缩进 2 格还是 4 格**
> 缩进几格不是 ED-02 本身的内容，是每个项目自己的约定。你的网站用 2 格，是因为起步网页就是这么写的；Google 的 HTML/CSS 风格指南（2026-11-20 核对，网址在 `rules.md` 的 ED-02 卡片里）也写着 “Indent by 2 spaces at a time”（每层缩进 2 个空格）。

> **想多了解（可跳过）：用 file 看一个文件的编码**
> macOS 自带的 `file` 命令会猜一个文件是什么格式。在 `notes` 文件夹里运行 `file today.md old-pc.txt`，会看到 `today.md` 是 `Unicode text, UTF-8 text`，`old-pc.txt` 是 `ISO-8859 text, with CRLF line terminators`：它认不出 GBK，只知道不是 UTF-8；后半句说的是这个文件用 CRLF 换行。

- VS Code 官方文档：基本编辑（保存、自动保存、跨文件搜索）https://code.visualstudio.com/docs/editing/codebasics （English）
- EditorConfig 官网，有支持它的编辑器名单 https://editorconfig.org/ （English）
- EditorConfig 规范全文 https://spec.editorconfig.org/ （English）
