# 学习工作区和命名

这一类规则管两件事：代码放在哪里，文件和文件夹叫什么名字。代码放进网盘同步的文件夹，同步程序会一个文件一个文件地搬动 Git 的仓库，可能弄丢或弄坏里面的内容。名字里有空格、大写字母或中文，敲命令时容易出错，到了区分大小写的服务器上还可能找不到。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（2 张）

### WS-01 代码不放网盘同步目录

- **约束力**：必须（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：代码和 Git 仓库放在不被 iCloud、OneDrive、Dropbox 这类网盘同步的本地文件夹里；本课程统一放在 `~/Developer` 下面（这个文件夹名是本课程的约定，见“例外”）。想在别处留一份，用远程仓库（放在别处的另一份仓库，第 1.12 课），不用网盘。
- **谁说的**：Git 官方 FAQ（gitfaq，页面写着“last updated in 2.53.0”）“Transfers”一节 https://git-scm.com/docs/gitfaq ；Apple 支持文章 109344《Add your Desktop and Documents files to iCloud Drive》（2026-09-14 发布）https://support.apple.com/en-us/109344 ；Apple《Mac 使用手册》（macOS 27）“Store files in iCloud Drive” https://support.apple.com/guide/mac-help/store-files-in-icloud-drive-mchle5a61431/mac ；同一手册的“If document versions conflict in iCloud Drive on Mac” https://support.apple.com/guide/mac-help/mh40780 ；公开的问题报告：python/cpython 问题 113659（2024-01，跳过隐藏的 .pth 文件）https://github.com/python/cpython/issues/113659 、pypa/setuptools 问题 4595（2024-08-26）https://github.com/pypa/setuptools/issues/4595 、astral-sh/uv 问题 16977（2025-12-04）https://github.com/astral-sh/uv/issues/16977 ；Dropbox 帮助中心“conflicted copy”（2025-05-15 更新）https://help.dropbox.com/organize/conflicted-copy ；Microsoft Learn OneDrive 同步问题排查（2025-01-03）https://learn.microsoft.com/en-us/troubleshoot/sharepoint/sync/troubleshoot-sync-issues
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 macOS 大版本升级之后
- **谁来管**：没有人会拦你，Git 和 macOS 都不报警；只有本课程的 `doctor` 会提醒（列在「需要处理」组里）；**不遵守的后果**：仓库可能缺东西、文件被悄悄改掉、出现“xxx 2”这样的冲突副本，而且很难查出原因。
- **为什么**：Git FAQ 的原话是：不要用云同步服务同步 Git 仓库的任何部分，它们“一个文件一个文件、不停地”同步，不懂仓库的结构，可能造成对象丢失、文件被改动或多出来、分支指针损坏。Apple 支持文章 109344 说明：打开“桌面与文稿”同步后，这两个文件夹里的文件都存放在 iCloud 云盘里。《Mac 使用手册》还说：空间不够时，Mac 可以自动把文稿只存在 iCloud 里（“优化 Mac 存储空间”）。落到一个项目上，有公开的例子。一位开发者的 Python 项目放在 iCloud 同步的“文稿”里，项目自己的 Python 环境（`.venv` 文件夹）里的文件被加上了隐藏标记；他把一个测试文件夹挪进“文稿”，又复现了一次（setuptools 问题 4595）。Python 有时靠 `.pth` 这种小文件，找到你项目自己的代码。出于安全考虑，2024 年初起的各个 Python 版本都会跳过带隐藏标记的 `.pth` 文件（python/cpython 问题 113659）。结果是项目自己的代码突然导入不了。uv 那边也有同样的报告（问题 16977），讨论里有人认为标记是 iCloud 加的，也有人认为是 Spotlight 加的，都是推测。做过复现的只有 setuptools 那位报告人；Apple 的文档里没有写这件事。另一种麻烦是冲突副本。按《Mac 使用手册》，几台设备离线时改了同一个文件，iCloud 会让你选留哪个版本；留下不止一个，后面几个的名字会加上数字（手册的例子是“Seven Wonders 2”）。Dropbox 会在文件名里加“conflicted copy”，OneDrive 会加设备名。这种副本要是出现在 `.git` 文件夹里，仓库就可能坏掉。
- **正例**：

      ~/Developer/fullstack-from-zero
      ~/Developer/my-site
      ~/Developer/playground

- **反例**：

      ~/Desktop/my-site             （“桌面”打开了 iCloud 同步时）
      ~/Documents/projects/demo     （“文稿”也一样）

- **怎么检查**：运行 `python3 tools/course.py doctor`，看「学习工作区的位置」那一行在不在「需要处理」组里；第 0.2c 站的检查；复习题 0.2-code-home。
- **例外**：不是代码的东西（截图、PDF、文档草稿）可以放网盘。学习工作区在第 1.12 课之前还不是仓库，所以在那之前你可以决定先留在原处：这个决定记在 `learner/state.json` 里，`~/Developer/fullstack-from-zero` 放一个通向原处的入口，第 1.12 课把它变成仓库之前会再问你一次。它一旦成了仓库，这个例外就不再适用。文件夹的名字 `~/Developer` 是本课程的约定（规范·本课程约定）；在你自己的其他项目里，`~/code`、`~/Projects` 这类不被同步的文件夹同样可以，选哪个是个人偏好。macOS 的系统文件里有一个给叫 Developer 的文件夹准备的图标（`DeveloperFolderIcon.icns`，在 `/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/`），这只是观察到的现象，不是 Apple 写下的规定。
- **旧教程提醒**：以前很多入门教程让你“在桌面上新建一个项目文件夹”；现在 Mac 可以把桌面和文稿同步到 iCloud（自 macOS Sierra 10.12，2016 年起），这个做法在打开了同步的 Mac 上会出问题。
- **学于**：0.2

> 原文在第 0.2 课「文件、路径和代码的家」的 [`rules.md`](../stages/00-orientation/02-files-and-paths/rules.md)。

### WS-02 命名用小写英文加短横线

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目），那个项目有自己的命名约定时按它的
- **规则类型**：规范·组织
- **规则**：文件和文件夹的名字用小写英文字母、数字和短横线 `-`，不用空格、中文和大写；日期写成 `YYYY-MM-DD`。三个例外：Python 文件用下划线 `_`（例如 `exchange_rates.py`）；约定俗成的大写名字照旧（`README.md`、`LICENSE`、`CHANGELOG.md`、`CLAUDE.md`、`ROADMAP.md`）；系统和工具自己定的名字照旧（`Developer`、`Desktop`、`Documents`）。
- **谁说的**：Google developer documentation style guide“Filenames and file types” https://developers.google.com/style/filenames （原文：文件和文件夹名用小写；用短横线，不用下划线；只用 ASCII 字母和数字）；MDN“Dealing with files”（2026-09-11 修改）https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Dealing_with_files ；Python 文件的例外：PEP 8“Package and Module Names”（Active，2025-04-04 修改）https://peps.python.org/pep-0008/ ；本课程的取法：建课计划 G12 `docs/plans/2026-11-19-batch-1-plan.md`；日期写法 `YYYY-MM-DD` 来自国际标准 ISO 8601（ISO 8601-1:2019《Date and time — Representations for information interchange — Part 1: Basic rules》，有 2022 年的修正 Amd 1；规范地图 `STANDARDS.md` 目录 F09），本课程照它写。命名这一部分是一家组织的规矩，日期这一部分是标准，类型按卡片的主体（命名）标；ISO 网站今天拒绝自动访问，现行状态是在瑞典标准协会的目录里核对的 https://www.sis.se/en/produkter/standardization/information-sciences-publishing/documents-in-administration-commerce-and-industry/iso-8601-12019
- **核对日期**：2026-11-20；**复核周期**：12 个月（日期写法跟 ISO 8601 的修订走：新版发布时复核）
- **谁来管**：评审人（本课程里是导师和考题 0.2-x2）；没有工具会自动拦你；**不遵守的后果**：命令里处处要加引号，网址里出现 `%20`，换到区分大小写的服务器上文件就找不到了。
- **为什么**：名字里有空格，终端会把它当成两样东西，路径要加引号（第 0.2a 站末尾的「想多了解」）。混进一个中文或全角字符，就得来回切换输入法，命令很容易打错（第 0.2b 站你见过）。这台 Mac 不区分大小写，`~/developer` 和 `~/Developer` 是同一个地方；但大多数网站服务器区分大小写，在这里能用的名字到了服务器上可能就找不到。全用小写，这个坑就踩不到。
- **正例**：

      my-site/
      notes/2026-11-19-paths.md
      exchange_rates.py           （Python 文件用下划线）
      README.md                   （约定俗成的大写名字）

- **反例**：

      My Site (final)/
      学习笔记.md
      新建文件夹 2/
      Notes.md 和 notes.md 同时存在

- **怎么检查**：人工检查：起名之前对照这张卡；复习题 0.2-naming；考题 0.2-x2。
- **例外**：上面“规则”里的三类名字；文件里面的内容可以放心写中文。以后学到的语言或框架有自己的命名约定时，按它们的来（到时候课文会说）。
- **旧教程提醒**：无
- **学于**：0.2

> 原文在第 0.2 课「文件、路径和代码的家」的 [`rules.md`](../stages/00-orientation/02-files-and-paths/rules.md)。
