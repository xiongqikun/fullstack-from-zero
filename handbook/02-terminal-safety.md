# 终端安全

终端照字面执行你敲的每一个字，不会问你“确定吗”。这一类规则让你在运行看不懂的命令之前先停下来弄懂，在删除之前先看清要删什么。终端里删掉的东西不进废纸篓，这两步各花几秒钟，挡住的是找不回来的损失。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（2 张）

### TERM-01 不照抄看不懂的命令

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：规范·本课程约定
- **规则**：运行一条从别处复制来的命令之前，先能说出它的每一部分在做什么；说不出来，就先查 `man`，或者请导师逐段解释。看到 `sudo`、`rm -rf`，或者把网上下载的内容直接交给 shell 执行（`curl … | sh`、`curl … | bash`、`bash -c "$(curl …)"`），先停下，弄懂再决定。
- **谁说的**：本课程约定（2026-11-19 定，2026-11-20 复核）。没有哪条法律、标准或平台规定这样做，是本课程按下面的来源定的。依据：MDN Web Docs《Command line crash course》（2026-09-12 修改，2026-11-20 核对），原意是“命令复杂起来以后，要先想清楚它会做什么，先在测试文件夹里试过，再在真正的文件夹里运行” https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line ；Microsoft Threat Intelligence《Think before you Click(Fix): Analyzing the ClickFix social engineering technique》（2025-08-21，2026-11-20 核对），记录了骗人把恶意命令粘贴进终端运行的手法（也针对 macOS），建议之一是让使用者清楚自己复制粘贴的是什么 https://www.microsoft.com/en-us/security/blog/2025/08/21/think-before-you-clickfix-analyzing-the-clickfix-social-engineering-technique/ ；Homebrew FAQ（页面不标日期和版本，2026-11-20 查阅；“Why does Homebrew say sudo is bad?”一条：用 sudo 运行 brew，等于把管理员权限交给所有能改 Homebrew 代码的人）https://docs.brew.sh/FAQ
- **核对日期**：2026-11-20（上面每个网页当天重新打开核对过）；**复核周期**：12 个月，或者 macOS 的终端加了新的粘贴保护、上面的来源改版时
- **谁来管**：没有人会拦你；**不遵守的后果**：一条看不懂的命令可能删掉文件、改掉系统设置，或者把别人的程序装进你的电脑，而且往往没有撤销的办法。
- **为什么**：终端不会问你“确定吗”，它照字面执行。现在常见的骗术就是在网页、广告或聊天里给你一条“修复问题”的命令，让你复制进终端，运行后它下载并执行别人的程序。网上的命令还经常是给别的系统写的（比如 Linux），在 Mac 上不认，甚至做的事不一样。先弄懂，才知道它会不会伤到你。
- **正例**：教程里写着 `head -n 5 notes.txt`。先运行下面第一条，在手册里查到 `-n` 后面的数字是“显示几行”；弄懂了，再运行第二条：

      man head
      head -n 5 notes.txt

- **反例**：在一个“修复 Mac 磁盘空间”的网页上看到 `curl -fsSL https://某个网址/fix.sh | sh`，没看懂就复制进终端回车；或者看到报错 Permission denied，就在命令前面加上 `sudo` 再来一次。
- **怎么检查**：复习题 1.1-r5；人工检查：运行之前，用一句话说出命令名、每个选项和每个对象各是什么意思。说不出来的那一部分，先查 `man` 或问导师。
- **例外**：软件官网的官方安装命令有时就是“下载后直接交给 shell 运行”的写法。例如 Homebrew 官网 https://brew.sh/ （2026-11-20 查阅）的安装命令是 `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`，网页上说脚本会先说明要做什么、停下来再动手。这种情况也要先确认网址真的是官方的，读过说明再决定；看不懂就请导师逐段解释。阶段 1 里只有电脑上还没有 Homebrew 的人，会在第 1.11 课装它时碰到这类命令（先确认网址、读过说明，再和导师一起看）；阶段 1 后面唯一要装的程序是第 1.11 课的 `gh`，命令 `brew install gh` 出自 GitHub CLI 的官方说明。
- **旧教程提醒**：以前 Mac 默认的 shell 是 bash，老教程会写“Mac 的终端用的是 bash”，给的设置步骤也是给 bash 的；自 macOS 10.15（2019 年）起 Mac 默认用 zsh（Apple 支持文章 102360《Use zsh as the default shell on Mac》，2026-06-15 发布，2026-11-20 核对，https://support.apple.com/en-us/102360 ）。不变的一点：文档里命令前面的 `$` 一直是表示提示符的写法，现在也一样；你自己的提示符结尾是 `%`（建课时在 Mac 上实测）。两者都不是命令的一部分，不要复制进去。
- **学于**：1.1

> 原文在第 1.1 课「终端：新建与查看」的 [`rules.md`](../stages/01-foundations/01-create-and-view/rules.md)。

### TERM-02 删除前先看清要删什么

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：规范·本课程约定
- **规则**：在终端里删除之前，先在同一个文件夹里用 `ls` 加上和删除时一模一样的名字或通配符看一遍，确认列出来的正是要删的，再把 `ls` 换成 `rm`；删文件夹之前用 `ls -a` 看，连名字以点开头、`ls` 不列出来的隐藏文件一起看清；名字里有空格就加引号；可能还想要回来的东西，不在终端里删，在 Finder 里删（进废纸篓）。
- **谁说的**：本课程约定（2026-11-19 版）。依据：MDN（Mozilla 维护的网页技术文档网站）《Command line crash course》（2026-09-12 修改，2026-11-19 打开核对）写明 `rm` 的删除是永久的、不能从废纸篓找回，`rm -r` 删掉的东西会永远消失，并建议先在测试文件夹里试 https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line ；建课时核对用的 Mac 上的 `man rm`（macOS 27.2 自带，2018-11-10 版，2026-11-19 核对）没有任何“放进废纸篓”的选项，里面唯一和“恢复”有关的 `-W` 只在一种很少见的特殊磁盘设置里有用，找不回普通删掉的文件；Apple《Mac 使用手册》“在 Mac 上删除文件和文件夹”（macOS 27 版，中文，2026-11-19 打开核对）写明 Finder 里选中后按 Command-Delete 会把东西放进废纸篓，可以用“文件”>“放回原处”（英文界面是 File > Put Back）找回，清倒废纸篓之后才永久删除 https://support.apple.com/zh-cn/guide/mac-help/mchlp1093/mac
- **核对日期**：2026-11-19；**复核周期**：12 个月，或者 macOS 大版本升级之后
- **谁来管**：没有人；**不遵守的后果**：删错的文件找不回来，常常也没有人能帮你找回来。
- **为什么**：终端里的 `rm` 不出声、不确认、不进废纸篓，执行完就没了。通配符一次能选中一批名字，其中可能有你没想到的；名字里的空格会让一个名字变成两个。先用 `ls` 看一遍，花两秒钟，就能在删之前发现这些问题。
- **正例**：

      ls *.tmp
      rm *.tmp
      ls "report copy.txt"
      rm "report copy.txt"

- **反例**：在没看过的文件夹里直接 `rm *`（删掉里面所有的名字）；只用 `ls` 看过一个文件夹“是空的”，就 `rm -r` 它（隐藏文件 `ls` 不列出来）；删带空格的名字不加引号，写成 `rm report copy.txt`；用 `rm -r` 删一个装着东西、但没看过里面有什么的文件夹。
- **怎么检查**：复习题 1.2-r1、1.2-r4；动手题 1.2-d1（复习命令不会出它；想再练一次，在学习工作区里运行 `python3 tools/course.py scenario 1.2b --reset` 重搭一份，做完运行 `python3 tools/course.py check 1.2b`）；人工检查：每次敲 `rm` 之前，屏幕上紧挨着的上一条命令应该是同样名字的 `ls`。
- **例外**：无。练习场里删错了可以用 `python3 tools/course.py scenario <编号> --reset` 重搭，但这不是例外，只是练习场的好处。
- **旧教程提醒**：以前想从终端把文件放进废纸篓，教程会让你另外装一个第三方的 `trash` 工具；现在 macOS 15 起系统自带 `trash` 命令（建课时核对用的 Mac 上，`man trash` 写着 First appeared in macOS 15.0，2026-11-19 核对）。本课程阶段 1 不用它：可能还想要的东西，照样在 Finder 里删。
- **学于**：1.2

> 原文在第 1.2 课「终端：复制、移动、删除」的 [`rules.md`](../stages/01-foundations/02-copy-move-delete/rules.md)。
