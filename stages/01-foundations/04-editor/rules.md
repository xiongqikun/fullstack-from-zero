### ED-01 打开文件夹而不是单个文件

- **约束力**：推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：用编辑器做一个项目时，打开项目最外层的文件夹（在那个文件夹里运行 `code .`），而不是只打开其中一个文件。
- **谁说的**：VS Code 官方文档（页面日期 2026-11-18）："After you open a folder in VS Code, the contents of the folder are shown in the Explorer view." https://code.visualstudio.com/docs/getstarted/userinterface ；内置终端 "By default, the terminal will open at the folder that is opened in the Explorer." https://code.visualstudio.com/docs/terminal/basics ；macOS 安装说明 "Run `code .` in any folder to start editing files in that folder." https://code.visualstudio.com/docs/setup/mac ；VS Code 1.145.2 安装包里的提示文字："You have not opened or specified a folder. Only open files are currently searched"
- **核对日期**：2026-11-20；**复核周期**：12 个月（工具的惯例；VS Code 每周发一个新版本，界面文字变了就提前复核）
- **谁来管**：没有人：VS Code 不拦你只开一个文件，本课程的检查也看不到你打开的是什么；后果来自工具的工作方式；**不遵守的后果**：资源管理器里只看得到这一个文件，跨文件搜索只搜已经打开的文件，内置终端不从项目文件夹开始。
- **为什么**：编辑器的很多功能都以“打开的文件夹”为单位：列出文件、按名字找文件、在所有文件里找字、终端从哪里开始、项目里的设置文件（比如 `.editorconfig`）。只开一个文件，这些功能都落了空，你还以为是编辑器不好用。
- **正例**：

      cd ~/Developer/my-site
      code .

- **反例**：`code index.html`（只开一个文件，左边的资源管理器显示 NO FOLDER OPENED）；在主文件夹 `~` 里运行 `code .`（打开的是整个主文件夹，不是这个项目）。
- **怎么检查**：`python3 tools/course.py check 1.4a`（它只看你改好的网页，看不到你打开的是文件还是文件夹）；复习题 1.4-r1；人工检查：VS Code 左边资源管理器最上面显示的是项目文件夹的名字（例如 MY-SITE），不是 NO FOLDER OPENED，也不是你的用户名。
- **例外**：只是临时看一眼某个文件、不做项目时，可以只开文件（第 0.1 课就是这样打开 `convert.py` 的）。
- **旧教程提醒**：老教程（1.57 版起，2021 年 5 月）说打开新文件夹时会先弹出一个对话框，问你信不信任这个文件夹的作者。现在新文件夹先在受限模式（Restricted Mode）里打开，窗口上方只出现一条横幅，由你决定要不要信任；单独打开一个文件时，仍可能弹出另一个对话框，问要不要打开这个不受信任的文件（自 1.126 版，2026-06-24 起：设置 `security.workspace.trust.startupPrompt`，也就是“打开还没信任的文件夹时，问不问你信不信任它”的那个设置，默认值从 `once`（第一次打开时问一次）改成 `never`（不问），同时去掉了 Trust Parent 按钮（“信任上一层文件夹”的按钮）。出处 https://code.visualstudio.com/updates/v1_126 ，2026-11-20 在 1.145.2 里核对过）。
- **学于**：1.4

### ED-02 文本统一 UTF-8 和 LF，用 .editorconfig 说明

- **约束力**：推荐（适用范围：所有项目）；在本课程的 `my-site` 和学习工作区里是必须（适用范围：本课程）
- **规则类型**：惯例·事实标准（EditorConfig 是写下这些约定的公开格式，它本身不规定用 UTF-8 还是 LF；UTF-8 这一半另有标准撑腰：WHATWG HTML 标准要求网页里声明编码的 `<meta charset>` 写 utf-8；LF 这一半出自 Git 官方 FAQ，属于惯例·平台与工具）
- **规则**：项目里的文本文件统一用 UTF-8 编码、LF 换行、文件最后留一个换行，并把这些约定写进项目根目录的 `.editorconfig`，让各种编辑器照着做。
- **谁说的**：EditorConfig 规范 0.17.2 https://spec.editorconfig.org/ 和官网 https://editorconfig.org/ （VS Code 不在“不用插件”的名单里，在 "Download a Plugin" 一栏）；VS Code 扩展 EditorConfig（发布者 EditorConfig，0.18.2）https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig ；Git 官方 FAQ（gitfaq，最后更新于 Git 2.53.0）"we recommend that text files be stored in UTF-8 without a byte-order mark (BOM) with LF (Unix-style) endings"（BOM 是有的程序在文件开头加的一个看不见的标记）https://git-scm.com/docs/gitfaq ；WHATWG HTML Living Standard（页面写着 Last Updated 19 November 2026）`<meta charset>` 的值必须是 utf-8 https://html.spec.whatwg.org/multipage/semantics.html#charset
- **核对日期**：2026-11-20；**复核周期**：12 个月（卡片里有 VS Code 要不要另装扩展的事实，按工具算），或者 VS Code 宣布内置 EditorConfig 支持时
- **谁来管**：工具和评审人；**不遵守的后果**：别人的电脑或网站读出乱码；用 Windows 的同事一改，整份文件每一行都显示成“改过了”；有的程序因为看不懂行尾多出来的 CR（回车符，CRLF 里的那个 CR）而报错。
- **为什么**：文字存进文件时要按一张对照表变成字节（计算机里算文件大小的基本单位，第 1.1 课见过；可以想成一个个数字），这张表叫字符编码。写的人和读的人用的不是同一张表，就出乱码；你在本课练习场里亲眼见过 GBK 文件按 UTF-8 读出来的样子。换行也有两种写法，混在一起时 Git 会把没改的行也算成改动。把约定写进 `.editorconfig`，换一个人、换一个编辑器，也照同样的格式存。正例里管缩进的那两块只是你的网站的写法：缩进 2 格还是 4 格不是这条规则的内容，是各项目自己的约定（例如 Google HTML/CSS 风格指南写着 "Indent by 2 spaces at a time"，https://google.github.io/styleguide/htmlcssguide.html ，2026-11-20 核对，页面没有修订日期）。VS Code 自己不读 `.editorconfig`：到 1.145.2（2026-11-20 核对）仍要装 EditorConfig 扩展，VS Code 只会在你打开 `.editorconfig` 时推荐它；有的教程说它“自带 EditorConfig 支持”，不对。
- **正例**：

      root = true

      [*]
      charset = utf-8
      end_of_line = lf
      insert_final_newline = true

      [*.html]
      indent_style = space
      indent_size = 2

      [*.css]
      indent_style = space
      indent_size = 2

- **反例**：`charset = utf8`（规范里没有这个写法，编辑器会悄悄忽略）；文件名写成 `editorconfig.txt`；用全角符号写 `［*］` 或 `charset ＝ utf-8`；同一个项目里有的文件 UTF-8、有的 GBK。
- **怎么检查**：`python3 tools/course.py check 1.4c`；复习题 1.4-f1；人工检查：用 `cat .editorconfig` 看一遍；想看某个文件实际的编码，用 macOS 自带的 `file 文件名`（本课「想多了解」里讲过）：UTF-8 的文件显示 `UTF-8 text`（只有英文字母的显示 `ASCII text`），带 CRLF 换行的会多出 `with CRLF line terminators`。
- **例外**：别的工具强制要求另一种格式的文件（比如只认 CRLF 的 Windows 批处理文件 `.bat`，Windows 上的一种命令脚本），在 `.editorconfig` 里给它单独写一块。
- **旧教程提醒**：无
- **学于**：1.4
