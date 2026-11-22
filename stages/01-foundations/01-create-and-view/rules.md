<!-- 第 1.1 课的规则卡（计划 I2 的十三栏格式）。手册 handbook/ 由这里汇总。 -->

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
