# 0004 代码放在 `~/Developer`，不放进网盘同步的文件夹

> **状态**：已采纳（accepted）｜ **日期**：2026-11-19 ｜ **谁定的**：Claude 提出；搬不搬由你点头 ｜ **征求过意见**：五份设计评审

## 背景和要回答的问题

很多 Mac 的桌面（Desktop）和文稿（Documents）两个文件夹开着 iCloud 同步：苹果的网盘会在后台把里面的文件自动上传，并在你的各台设备之间保持一致。课程文件夹也可能就放在桌面里。写代码的工具和这种同步合不来，公开的问题报告里有现成的例子（见文末「技术清单」）。要回答的是：代码放在哪里，备份靠什么？

## 考虑过的方案

* 甲：留在桌面，靠给文件夹改名这类变通办法，让 iCloud 跳过个别文件夹。
* 乙：关掉桌面和文稿的 iCloud 同步。
* 丙：代码放进不同步的 `~/Developer`（`~` 表示你的个人文件夹），备份交给 Git（给文件夹拍“带说明的快照”的工具）的远程仓库（remote），也就是放在别处的另一份。

## 决定

选丙。甲靠的不是系统正式提供的开关，而且每个项目都要重做一遍。乙会波及你电脑上别的文件：按苹果的说明，关掉之后原有文件留在 iCloud 里，本机会新建桌面和文稿文件夹，原来的文件不在里面。丙里“代码不放同步目录”是同行通行的做法（惯例·平台与工具），对应规则卡（手册里一条规范的完整说明）WS-01，在第 0.2 课学；文件夹具体叫 `~/Developer`，是本课程的选择。

搬家不由你自己敲命令。你点头之后，由 Claude 按“先复制、核对、保留旧的”搬到 `~/Developer/fullstack-from-zero`；可以在课程建好时搬，也可以到第 0.2 课再搬。你不同意就留在原处，课程照样能用；这个决定会记进你的学习档案，第 0.2 课讲清风险。

### 后果

* 好处：同步不会再在背后改动、挪走或复制你的代码文件。练习场（playground，随便折腾、弄坏了能重建的练习文件夹）和你的网页也都放在 `~/Developer` 下面。
* 代价：离开 iCloud，就少了那份自动的第二份拷贝，别的设备上也看不到这些文件了。对策：第 0.4 课带你做一个临时备份；第 1.12 课把快照传到 GitHub（存放快照备份的网站）；“在别处有第二份，并且试过能恢复”是阶段 1 的过关条件。
* 代价：Claude 应用是按文件夹记事的，换了位置，它当成一个新项目。所以学习状态全部存在课程文件夹里的文件中，不靠对话记忆。
* 不动的：你手上已有的其他项目（如果有）仍在原处，这次不搬。

## 技术清单（现在看不懂没关系）

* Git 官方 FAQ “How do I sync a working tree across systems?”：不要用云同步服务同步 Git 仓库的任何部分，否则会造成对象丢失、文件被改动或多出、引用损坏等问题；这类服务逐个文件持续同步，不理解仓库的结构。出处：https://git-scm.com/docs/gitfaq ，本机 `git help faq`（Git 2.54.0）里也有，2026-11-19 核实。
* 苹果的说明：这项功能同步的是 Desktop 和 Documents 两个文件夹（https://support.apple.com/en-us/109344 ）；关闭之后的行为（https://support.apple.com/en-us/126628 ）。2026-11-19 核实。
* 甲的变通细节（`.nosync` 这类改名办法）：调研简报 uv-packaging 第 5 节、foundations-macos 第 5 节。
* 一种已知的事故（虚拟环境里的文件被打上“隐藏”标记，Python 找不到项目自己的代码），证据以公开的问题报告为准：https://github.com/pypa/setuptools/issues/4595 （项目在 iCloud 同步的“文稿”里，`.venv` 里的文件被加上隐藏标记，报告人复现过）、https://github.com/python/cpython/issues/113659 （Python 跳过隐藏的 .pth 文件）、https://github.com/astral-sh/uv/issues/16977 （同样的症状，讨论里对是谁加的标记还有不同说法），2026-11-20 核实。
* Git 仓库放进网盘后坏掉的公开报告：Apple 开发者论坛 https://developer.apple.com/forums/thread/811085 （打开“桌面与文稿”同步后仓库报 Bad object）、Microsoft Tech Community https://techcommunity.microsoft.com/discussions/onedriveforbusiness/onedrive-is-corrupting-my-git-repositories/3898283 （OneDrive 同步完 `.git` 以后仓库失效），2026-11-20 核实。
* 第 1 版让你在第 0.6 课自己用命令搬整个文件夹。评审认为这是风险最大、最难验证的一步，所以改成现在的做法：资深工程师评审第 2 条、教学设计评审第 1 条、零基础视角评审第 8 条、失败预演评审第 9 条。
* “按文件夹记事”：Claude 的自动记忆按项目文件夹存放（https://code.claude.com/docs/en/memory ，2026-11-19 核实）。
