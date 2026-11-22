# 术语表

这里收着阶段 0 和阶段 1 每一课第一次讲到的术语，按上课顺序排。每个词有一句大白话，和它第一次出现的那一站；想看完整的讲法，回到那一课去读。

表后面有一张按英文字母排的索引：看到一个英文词，可以从那里查到中文。

下面的表是工具从每一课的术语清单生成的。同一个词在两课都出现时，只留第一次出现的那一条。要改一个词，改它所在的那一课。

几组容易混的词：学习工作区（fullstack-from-zero 文件夹，0.1a）、工作区（Git 里你正在改的文件，1.6b）和工作区信任（VS Code 的提示，0.1c）；看板（管任务的表，0.4a）和汇率看板（课程产品，0.3a）；标签（网页里的 tag，1.4a）和标签页（VS Code 的 tab，0.1c）；扩展（VS Code 的 extension，1.4c）和扩展名（1.5a）；路径（0.2a）和 PATH（1.11b）；脚注（提交说明的 footer，1.10b）、尾注（trailer，1.15b）和网页的页脚（1.13c）；验收（验收别人的改动，1.15a）和阶段验收（gate-1，1.16b）；协议（protocol，1.11b）和第 0.4 课“累了协议”里的日常说法；存档点（一站的结尾，0.1a）和提交（像游戏存档，1.6a）；说明书（单说时指命令自带的 man page，0.2b）和“项目的说明书”（指 README，1.5b）。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 术语（按上课顺序）

一共 171 个。

| 术语 | English | 大白话 | 第一次出现 |
|---|---|---|---|
| 课文 | lesson text | 这门课每一课的文字说明，告诉你一步步做什么 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 导师 | tutor | 按这个工作区的规则当教练的 Claude：给提示，不替你做练习 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 学习工作区 | workspace | fullstack-from-zero 这个文件夹：课文、工具和你的笔记都在里面 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 终端 | terminal | 用打字而不是点鼠标来指挥电脑的窗口 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 命令 | command | 在终端里敲的一行指令 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 项目文件夹 | project folder | Claude 桌面应用里一次会话干活的那个文件夹；上课时选 fullstack-from-zero | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 存档点 | save point | 每一站的结尾，到这里可以放心停下，下次从下一站接着学 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 状态行 | status line | 导师每一条回复的第一行，以【教练模式】开头，说明导师读了学习工作区里的规则 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 行规 | lesson rules | 这一课定下、以后一直要守的规矩；每条有编号，完整卡片在本课的 rules.md 里 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 落脚点 | landing point | 学完一段、可以停下回头看的地方，通常是一个关卡；运行 python3 tools/course.py 会告诉你离它还有几站 | [0.1a](stages/00-orientation/01-first-steps/lesson.md) |
| 提示符 | prompt | 终端每行开头那段字，以 % 结尾，表示“请讲” | [0.1b](stages/00-orientation/01-first-steps/lesson.md) |
| 报错 | error message | 程序告诉你它没办成、卡在哪里的那段话 | [0.1b](stages/00-orientation/01-first-steps/lesson.md) |
| shell | shell | 在终端里接你命令、照着执行的程序，中文有时叫命令解释器；你的 Mac 上它叫 zsh | [0.1b](stages/00-orientation/01-first-steps/lesson.md) |
| 程序 | program | 一份写着一步步指令、交给电脑去执行的文本文件 | [0.1c](stages/00-orientation/01-first-steps/lesson.md) |
| 解释器 | interpreter | 读程序文件、照着一行行执行的那个软件，比如 python3 | [0.1c](stages/00-orientation/01-first-steps/lesson.md) |
| 编辑器 | editor | 写代码和文档用的软件，本课程用的编辑器是 VS Code | [0.1c](stages/00-orientation/01-first-steps/lesson.md) |
| 工作区信任 | Workspace Trust | VS Code 打开来路不明的文件前先问一句的提示；这里的“工作区”是 VS Code 自己的说法，不是学习工作区 | [0.1c](stages/00-orientation/01-first-steps/lesson.md) |
| 标签页 | tab | VS Code 顶上每个打开的文件占的一个小格子 | [0.1c](stages/00-orientation/01-first-steps/lesson.md) |
| 练习场 | playground | 工具专门放练习材料的文件夹（~/Developer/playground），弄坏了也不要紧 | [0.1c](stages/00-orientation/01-first-steps/lesson.md) |
| 路径 | path | 文件在电脑里的地址 | [0.2a](stages/00-orientation/02-files-and-paths/lesson.md) |
| 绝对路径 | absolute path | 从最顶上（/ 或 ~）写起的完整地址，在哪里用都指同一个地方 | [0.2a](stages/00-orientation/02-files-and-paths/lesson.md) |
| 相对路径 | relative path | 从你现在所在的文件夹写起的地址，换个出发点就指向别处 | [0.2a](stages/00-orientation/02-files-and-paths/lesson.md) |
| 主文件夹 | home folder | 你这个用户在电脑上的“家”，写作 ~ | [0.2a](stages/00-orientation/02-files-and-paths/lesson.md) |
| 上一级文件夹 | parent folder | 装着当前文件夹的那个文件夹，写作 .. | [0.2a](stages/00-orientation/02-files-and-paths/lesson.md) |
| Tab 补全 | tab completion | 名字打一半按 Tab 键，终端替你补完整 | [0.2a](stages/00-orientation/02-files-and-paths/lesson.md) |
| 说明书 | manual page (man page) | 命令自带的使用说明，用 man 命令打开 | [0.2b](stages/00-orientation/02-files-and-paths/lesson.md) |
| 全角字符 | full-width character | 中文输入法打出来的、占一个汉字宽的字母、数字、标点和空格；写在命令名、选项、分隔的空格和 ~ / - 这类符号里，命令就不认 | [0.2b](stages/00-orientation/02-files-and-paths/lesson.md) |
| 半角字符 | half-width character | 英文输入状态下打出来的普通字母、数字、标点和空格；命令名、选项、分隔的空格和 ~ / - 这类符号只认它们 | [0.2b](stages/00-orientation/02-files-and-paths/lesson.md) |
| 云同步文件夹 | cloud-synced folder | 里面的文件会被自动上传到云端、再同步到别的设备的文件夹 | [0.2c](stages/00-orientation/02-files-and-paths/lesson.md) |
| 短横线命名 | kebab-case | 名字全用小写英文，单词之间用短横线 - 连接，例如 my-site | [0.2c](stages/00-orientation/02-files-and-paths/lesson.md) |
| 前端 | front end | 用户直接看到、直接操作的那一块，比如浏览器里的网页 | [0.3a](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 后端 | back end | 在别处等着回答前端提问的程序 | [0.3a](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 服务器 | server | 一台一直开着、专门回答别人请求的电脑 | [0.3a](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 数据 | data | 软件要记住的内容，比如每天的汇率，和程序分开存放 | [0.3a](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 运行环境 | runtime environment | 程序运行时离不开的那些机器、系统和软件 | [0.3a](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 状态码 | status code | 后端回答里表示结果的三位数编号，比如 404 表示没找到 | [0.3a](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 软件生命周期 | software development life cycle | 一个软件从想法到上线、再到长期维护要走的几步 | [0.3b](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 需求 | requirements | 写清楚要做什么、给谁用、做到什么程度算好 | [0.3b](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 测试 | testing | 用事先写好的检查证明程序做得对 | [0.3b](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 运维 | operations | 软件上线以后让它一直好好运行：盯着、修、备份 | [0.3b](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 岗位期望 | job expectation | 雇主对从业者的普遍期望，不是法律义务 | [0.3b](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 规则类型 | rule type | 一条规矩是谁定的，课程分七种 | [0.3c](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 约束力 | obligation level | 一条规矩在你的处境里有多强制：必须、推荐、参考 | [0.3c](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 标准 | standard | 标准组织正式发布、带编号的文件 | [0.3c](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 行业要求 | compliance requirement | 法律、合同、审计或平台强制政策，别人能拿它追究你 | [0.3c](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 惯例 | convention | 没人能罚你，但工具和同行都默认你这么做 | [0.3c](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 个人偏好 | personal preference | 可以自己决定的事，不是规则 | [0.3c](stages/00-orientation/03-how-software-is-made/lesson.md) |
| 任务 | task | 小到一次能做完、做完能看出区别的一件事；在这门课里一站就是一个任务 | [0.4a](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 看板 | Kanban board | 把每件事放进「待办、进行中、完成」几栏的一张表，一眼看出做到哪了 | [0.4a](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 完成的定义 | Definition of Done, DoD | 事先写好的几条看得见的标准，全部满足才算完成 | [0.4a](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 在制品限制 | WIP limit (work in progress) | 同时开着、还没做完的事最多几件；这门课是一次只开一课 | [0.4a](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 带扶手完成 | finished with help | 看过提示的第 4 级（完整答案）以后才通过的一站；三到七天后要不看提示再做一遍 | [0.4b](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 迭代 | iteration | 按固定周期重复的一轮：计划、去做、回头看、调整 | [0.4b](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 复盘 | retrospective | 一轮结束后回头看：哪里顺、哪里卡、下一轮改一件什么 | [0.4b](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 备份 | backup | 放在别处的第二份，原来那份坏了或丢了还能找回来 | [0.4c](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 压缩包 | zip archive | 把一个文件夹连同里面的所有文件装进一个 .zip 文件 | [0.4c](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 关卡 | gate | 学完几课后一次不给提示的小考，题目每次随机生成 | [0.4c](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 讲解题 | explain-back question | 要你用自己的话讲清“为什么这样做，而不是那样做”的题，由导师问 | [0.4c](stages/00-orientation/04-manage-your-learning/lesson.md) |
| 选项 | option | 跟在命令后面、以短横线开头的开关，用来改变命令的做法，比如 ls -l 里的 -l | [1.1a](stages/01-foundations/01-create-and-view/lesson.md) |
| 隐藏文件 | hidden file | 名字以点开头的文件或文件夹，ls 默认不列出来，加 -a 才看得见 | [1.1a](stages/01-foundations/01-create-and-view/lesson.md) |
| 字节 | byte | 计算机里算文件大小的基本单位，一个英文字母占 1 字节；ls -l 里日期前面的数字就是字节数 | [1.1a](stages/01-foundations/01-create-and-view/lesson.md) |
| 文本文件 | text file | 里面只有文字的文件，可以直接在终端里显示；图片、压缩包这类文件不是 | [1.1b](stages/01-foundations/01-create-and-view/lesson.md) |
| 复制 | copy | 做一份一模一样的，原件还在原处 | [1.2a](stages/01-foundations/02-copy-move-delete/lesson.md) |
| 移动 | move | 把东西换个地方或换个名字，原处就没有了；改名也是移动 | [1.2a](stages/01-foundations/02-copy-move-delete/lesson.md) |
| 递归 | recursive | 连同里面的文件夹、文件夹里的文件，一层一层全算上 | [1.2a](stages/01-foundations/02-copy-move-delete/lesson.md) |
| 废纸篓 | Trash | 在 Finder 里删掉的东西先去的地方，还能放回原处 | [1.2b](stages/01-foundations/02-copy-move-delete/lesson.md) |
| 通配符 | wildcard | 在名字里代替“任意几个字符”的符号，最常用的是 * | [1.2b](stages/01-foundations/02-copy-move-delete/lesson.md) |
| 引号 | quotes | 把带空格的名字括起来，让终端把它当成一个整体 | [1.2b](stages/01-foundations/02-copy-move-delete/lesson.md) |
| 匹配 | match | 一行里含有你要找的那串字，就叫这一行匹配上了 | [1.3a](stages/01-foundations/03-search/lesson.md) |
| 区分大小写 | case-sensitive | 把大写字母和小写字母当成不同的字，EUR 和 eur 对不上 | [1.3a](stages/01-foundations/03-search/lesson.md) |
| 注释 | comment | 写给人看的说明文字，程序不照着它做事；本课的文件里它以 # 开头 | [1.3a](stages/01-foundations/03-search/lesson.md) |
| 模式 | pattern | 描述“名字长什么样”的写法，比如 *.css 表示所有以 .css 结尾的名字 | [1.3b](stages/01-foundations/03-search/lesson.md) |
| 受限模式 | Restricted Mode | VS Code 打开一个还没被你信任的文件夹时的安全模式：能看能改，但不自动运行里面的东西 | [1.4a](stages/01-foundations/04-editor/lesson.md) |
| 资源管理器 | Explorer | VS Code 左边那一栏，列出打开的文件夹里所有的文件 | [1.4a](stages/01-foundations/04-editor/lesson.md) |
| 自动保存 | Auto Save | 停手一秒左右，编辑器就替你把改动写进文件 | [1.4a](stages/01-foundations/04-editor/lesson.md) |
| 标签 | tag | 网页文件里尖括号括起来的记号，比如 &lt;h1>，告诉浏览器中间的字是什么；不是 VS Code 顶上的标签页（tab） | [1.4a](stages/01-foundations/04-editor/lesson.md) |
| 命令面板 | Command Palette | 按 ⇧⌘P 弹出的输入框，输入功能的名字就能用这个功能 | [1.4b](stages/01-foundations/04-editor/lesson.md) |
| 快速打开 | Quick Open | 按 ⌘P 弹出的输入框，输入文件名的几个字母就能打开文件 | [1.4b](stages/01-foundations/04-editor/lesson.md) |
| 跨文件搜索 | search across files | 按 ⇧⌘F，在打开的文件夹的所有文件里找一串字 | [1.4b](stages/01-foundations/04-editor/lesson.md) |
| 内置终端 | integrated terminal | VS Code 窗口下方的终端，和你平时用的是同一个 zsh | [1.4b](stages/01-foundations/04-editor/lesson.md) |
| 字符编码 | character encoding | 把文字存成字节的一套对照表；读和写用的不是同一套，就出乱码 | [1.4c](stages/01-foundations/04-editor/lesson.md) |
| 换行符 | line ending | 文件里表示“这一行结束了”的看不见的字符；Mac 用 LF，Windows 常用 CRLF | [1.4c](stages/01-foundations/04-editor/lesson.md) |
| 缩进 | indentation | 一行开头空出来的那一段，用来表示这一行在上一层里面 | [1.4c](stages/01-foundations/04-editor/lesson.md) |
| 扩展 | extension | 给 VS Code 加功能的附加程序，要另外安装（不是第 1.5 课的扩展名） | [1.4c](stages/01-foundations/04-editor/lesson.md) |
| EditorConfig | EditorConfig | 一份写在项目里的 .editorconfig 文件，告诉各种编辑器这个项目的文本统一用什么格式 | [1.4c](stages/01-foundations/04-editor/lesson.md) |
| Markdown | Markdown | 一种用 #、-、` 这类普通符号标出标题、列表、代码的纯文本写法 | [1.5a](stages/01-foundations/05-markdown-readme/lesson.md) |
| 扩展名 | file extension | 文件名最后一个点后面的那几个字母，表示文件是哪一种，比如 .md 是 Markdown | [1.5a](stages/01-foundations/05-markdown-readme/lesson.md) |
| 预览 | preview | 编辑器把 Markdown 显示成排好版的样子，只是看，不改文件 | [1.5a](stages/01-foundations/05-markdown-readme/lesson.md) |
| 标题 | heading | 以 # 开头的一行，# 的个数是级别：一个 # 是一级标题 | [1.5a](stages/01-foundations/05-markdown-readme/lesson.md) |
| 行内代码 | inline code | 一句话里用一对反引号 ` 包起来的命令或文件名 | [1.5a](stages/01-foundations/05-markdown-readme/lesson.md) |
| 代码块 | fenced code block | 上下各一行三个反引号 ``` 围起来的几行，原样显示，常用来放命令 | [1.5a](stages/01-foundations/05-markdown-readme/lesson.md) |
| README | README | 项目的门面和说明书：放在项目最外层文件夹，告诉别人这是什么、怎么用 | [1.5b](stages/01-foundations/05-markdown-readme/lesson.md) |
| 根目录 | root directory | 一个项目最外层的那个文件夹，比如 my-site 本身 | [1.5b](stages/01-foundations/05-markdown-readme/lesson.md) |
| 版本管理 | version control | 把文件夹每一次像样的状态都存下来，随时能看、能比、能退回；《Pro Git》中文版叫版本控制 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| Git | Git | 这门课用的版本管理工具；通常随 Mac 的命令行开发者工具一起装上，还没有的话，第一次在终端敲 git 时 macOS 会请你安装（README「怎么拿到这门课」讲了） | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 仓库 | repository | 被 Git 管着的文件夹，隐藏的 .git 文件夹里存着全部快照 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 提交 | commit | 拍一次快照并写一句说明 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 提交说明 | commit message | 写在每个提交上的那句话，说清这次改了什么；git commit -m 后面引号里的就是 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| HEAD | HEAD | Git 用来标“你现在在哪”的记号，平时指向当前分支最新的那个提交 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 全局设置 | global configuration | 写在 ~/.gitconfig 里、对这台电脑上所有仓库都起作用的 Git 设置 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 提交签名 | commit signing | 给提交盖一个只有你能盖的章，让别人能核对这个提交确实是你做的 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 参数 | argument | 命令名后面跟着的每一个词，选项和对象都算；git config set 后面的设置名和值就是两个参数 | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 分支 | branch | 一条历史线的名字；新仓库自带一条，这门课里叫 main | [1.6a](stages/01-foundations/06-first-commit/lesson.md) |
| 工作区 | working tree | 一个仓库里你正在改的那些文件，就是你在文件夹里看到的样子（不是学习工作区） | [1.6b](stages/01-foundations/06-first-commit/lesson.md) |
| 暂存区 | staging area | 准备拍进下一张快照的改动 | [1.6b](stages/01-foundations/06-first-commit/lesson.md) |
| 未跟踪 | untracked | 在文件夹里，但 Git 还从来没有收过它的文件 | [1.6b](stages/01-foundations/06-first-commit/lesson.md) |
| 本地历史 | commit history | 已经拍下的快照，一张接一张，存在你自己的电脑上 | [1.6b](stages/01-foundations/06-first-commit/lesson.md) |
| 差异 | diff | 两个版本之间的对照清单：哪些行删掉了，哪些行加上了 | [1.7a](stages/01-foundations/07-read-diff/lesson.md) |
| 改动块 | hunk | diff 里以 @@ 开头的一段，是文件里挨在一起的一处改动 | [1.7a](stages/01-foundations/07-read-diff/lesson.md) |
| 占位写法 | placeholder | 命令说明里用尖括号括起来的一段，比如 &lt;file>：真敲的时候换成具体的名字，尖括号不敲 | [1.7a](stages/01-foundations/07-read-diff/lesson.md) |
| 分页器 | pager | 输出太长时，Git 交给它一屏一屏地显示的程序，这台电脑上是 less | [1.7b](stages/01-foundations/07-read-diff/lesson.md) |
| 丢弃修改 | discard changes | 让文件回到存档里的样子，中间改的内容不要了 | [1.8a](stages/01-foundations/08-undo-uncommitted/lesson.md) |
| 会丢数据的命令 | destructive command | 执行以后，有些内容就再也找不回来的命令 | [1.8a](stages/01-foundations/08-undo-uncommitted/lesson.md) |
| 跟踪 | track | Git 管着这个文件：你 git add 过它，暂存区或存档里有它的版本 | [1.8a](stages/01-foundations/08-undo-uncommitted/lesson.md) |
| 取消暂存 | unstage | 把改动从暂存区拿下来，文件本身的内容不变 | [1.8b](stages/01-foundations/08-undo-uncommitted/lesson.md) |
| .gitignore | .gitignore | 给 Git 的“不拍名单”：写在里面的文件，Git 不再提醒你提交；也叫忽略文件 | [1.9a](stages/01-foundations/09-gitignore/lesson.md) |
| 全局忽略文件 | global ignore file (core.excludesFile) | 只在这台电脑上起作用、管所有仓库的不拍名单 | [1.9a](stages/01-foundations/09-gitignore/lesson.md) |
| 源文件 | source file | 你亲手写的、别人要重建这个项目必须拿到的文件 | [1.9a](stages/01-foundations/09-gitignore/lesson.md) |
| 密钥 | secret | 拿到就能冒充你“开门”的一串字符，比如密码、令牌、接口密钥 | [1.9a](stages/01-foundations/09-gitignore/lesson.md) |
| 接口密钥 | API key | 网站发给你、让你的程序去用它的接口（网站留给别的程序取数据、办事的入口）时出示的密钥 | [1.9a](stages/01-foundations/09-gitignore/lesson.md) |
| 令牌 | token | 一种通行证：程序拿着它就能代表你去用某个网站的服务；它代替密码，可以单独作废 | [1.9a](stages/01-foundations/09-gitignore/lesson.md) |
| 取消跟踪 | untrack (git rm --cached) | 让 Git 不再管某个文件，但文件本身还留在你的电脑上 | [1.9b](stages/01-foundations/09-gitignore/lesson.md) |
| 作废密钥 | revoke / rotate a secret | 到发密钥的网站让旧的失效，必要时换一个新的 | [1.9b](stages/01-foundations/09-gitignore/lesson.md) |
| 公开仓库 | public repository | 谁都能看的仓库 | [1.9b](stages/01-foundations/09-gitignore/lesson.md) |
| 推送保护 | push protection | GitHub 在你往公开仓库推送时检查有没有认得出的密钥，有就先拦下来；你自己可以选择放行 | [1.9b](stages/01-foundations/09-gitignore/lesson.md) |
| 原子提交 | atomic commit | 一次提交只装一件完整的事，可以单独看懂、单独撤回 | [1.10a](stages/01-foundations/10-commit-conventions/lesson.md) |
| 约定式提交 | Conventional Commits | 一份公开的提交说明写法规范，第一行写成「类型: 描述」 | [1.10b](stages/01-foundations/10-commit-conventions/lesson.md) |
| 类型 | type | 提交说明开头的英文小词，说明这次是新功能、修复还是文档 | [1.10b](stages/01-foundations/10-commit-conventions/lesson.md) |
| 范围 | scope | 类型后面圆括号里的词，说明改的是项目的哪一块 | [1.10b](stages/01-foundations/10-commit-conventions/lesson.md) |
| 正文 | body | 提交说明第一行之后、空一行再写的详细说明，讲为什么这样改 | [1.10b](stages/01-foundations/10-commit-conventions/lesson.md) |
| 破坏性变更 | breaking change | 会让别人原来的用法失效的改动，要在提交说明里特别标出来 | [1.10b](stages/01-foundations/10-commit-conventions/lesson.md) |
| 脚注 | footer | 提交说明正文后面几行固定格式的附加信息，例如写明谁参与了这次改动 | [1.10b](stages/01-foundations/10-commit-conventions/lesson.md) |
| GitHub | GitHub | 存放 Git 仓库的网站：给仓库在别处留一份，也能把作品给别人看 | [1.11a](stages/01-foundations/11-github-account/lesson.md) |
| 双重验证 | two-factor authentication, 2FA | 登录时除了密码，还要一样只在你手里的东西，比如手机上的六位数字 | [1.11a](stages/01-foundations/11-github-account/lesson.md) |
| 验证器 App | authenticator app / TOTP app | 每 30 秒生成一个新的六位数字的手机或电脑程序（TOTP：按时间变化的一次性密码） | [1.11a](stages/01-foundations/11-github-account/lesson.md) |
| 恢复码 | recovery codes | 手机丢了时用来登录的一组一次性备用码 | [1.11a](stages/01-foundations/11-github-account/lesson.md) |
| 密码管理器 | password manager | 专门替你记住密码、加密保存的程序；Mac 自带的一个叫 Passwords（密码） | [1.11a](stages/01-foundations/11-github-account/lesson.md) |
| 源代码 | source code | 写成一个程序的原文，程序员看的是它 | [1.11b](stages/01-foundations/11-github-account/lesson.md) |
| 包管理器 | package manager | 替你下载、安装、升级命令行程序的程序；Homebrew 是其中一个 | [1.11b](stages/01-foundations/11-github-account/lesson.md) |
| PATH | PATH | 终端找命令时按顺序翻的一串文件夹；全大写，和第 0.2 课的路径不是一回事：PATH 是一串路径 | [1.11b](stages/01-foundations/11-github-account/lesson.md) |
| 协议 | protocol | 两个程序之间说好的连接方式；这门课里 Git 连 GitHub 用 HTTPS（网址开头的 https） | [1.11b](stages/01-foundations/11-github-account/lesson.md) |
| 隐私邮箱地址 | noreply email address | GitHub 给你的一个不收信的邮箱地址，专门写进提交里，不暴露真实邮箱 | [1.11c](stages/01-foundations/11-github-account/lesson.md) |
| 远程仓库 | remote | 放在别处的另一份仓库，要你推送或拉取才会同步 | [1.12b](stages/01-foundations/12-push-and-backup/lesson.md) |
| 推送 | push | 把本机仓库里新的提交传到远程仓库 | [1.12b](stages/01-foundations/12-push-and-backup/lesson.md) |
| 私有仓库 | private repository | 只有你和你邀请的人能看到的 GitHub 仓库 | [1.12b](stages/01-foundations/12-push-and-backup/lesson.md) |
| 上游 | upstream | 本地分支默认推送到的那个远程分支，例如 origin/main | [1.12b](stages/01-foundations/12-push-and-backup/lesson.md) |
| 克隆 | clone | 从远程仓库完整复制一份仓库到本机，连同全部历史 | [1.12c](stages/01-foundations/12-push-and-backup/lesson.md) |
| 恢复测试 | restore test | 真的从备份里取一份出来，确认它是完整、能用的 | [1.12c](stages/01-foundations/12-push-and-backup/lesson.md) |
| 许可证 | license | 写明别人可以怎样使用你作品的一份声明，通常放在仓库根目录的 LICENSE 文件里 | [1.13a](stages/01-foundations/13-publish-site/lesson.md) |
| 版权 | copyright | 作者对自己作品天然拥有的权利；没有许可证时，别人不能复制、修改、分发 | [1.13a](stages/01-foundations/13-publish-site/lesson.md) |
| MIT 许可证 | MIT License | 一种有名字的宽松许可证，全文只有一页：别人几乎可以随意使用，只要保留你的版权声明，你也不承担责任 | [1.13a](stages/01-foundations/13-publish-site/lesson.md) |
| 上线 | deploy | 把作品放到一台一直开着的电脑上，让别人通过网址访问；也叫部署 | [1.13b](stages/01-foundations/13-publish-site/lesson.md) |
| 静态网站 | static site | 只有现成的网页文件、不需要在服务器上运行程序的网站，比如 my-site | [1.13b](stages/01-foundations/13-publish-site/lesson.md) |
| GitHub Pages | GitHub Pages | GitHub 提供的免费网页托管：把仓库里的网页文件发布成一个网址 | [1.13b](stages/01-foundations/13-publish-site/lesson.md) |
| 交付循环 | delivery loop | 改动、看改动清单、提交、推送、确认上线，这一圈反复做；以后的阶段会让机器替你做其中几步 | [1.13c](stages/01-foundations/13-publish-site/lesson.md) |
| 续行提示符 | continuation prompt | 一行命令还没输完整时，终端显示的等待提示，比如 dquote> | [1.14a](stages/01-foundations/14-errors-help-fresh/lesson.md) |
| 最小可复现示例 | minimal reproducible example | 去掉一切无关的东西以后，还能让同一个问题再出现一次的最少步骤 | [1.14b](stages/01-foundations/14-errors-help-fresh/lesson.md) |
| 发布说明 | release notes | 软件每出一个新版本，官方写的“这次改了什么” | [1.14c](stages/01-foundations/14-errors-help-fresh/lesson.md) |
| 基线 | baseline | 课程记下的、核对课文时各个工具的版本表 | [1.14c](stages/01-foundations/14-errors-help-fresh/lesson.md) |
| 弃用 | deprecated | 官方说这个做法以后会去掉，现在还能用，但不该再新学它 | [1.14c](stages/01-foundations/14-errors-help-fresh/lesson.md) |
| 知识截止日期 | knowledge cutoff | AI 学习的资料截止到哪一天；那以后的变化它不知道，只能去查 | [1.14c](stages/01-foundations/14-errors-help-fresh/lesson.md) |
| 验收 | acceptance review | 按清单核对别人交来的改动，再决定收下还是退回 | [1.15a](stages/01-foundations/15-review-ai-changes/lesson.md) |
| 改动统计 | diffstat | git diff --stat 打印的那几行：哪些文件改了、各改了多少行 | [1.15a](stages/01-foundations/15-review-ai-changes/lesson.md) |
| 范围外的改动 | out-of-scope change | 没让改却被改了的地方，常常藏在别的文件里 | [1.15b](stages/01-foundations/15-review-ai-changes/lesson.md) |
| 尾注 | trailer | 提交说明末尾“名字: 内容”格式的行，第 1.10 课说的脚注里的一种，比如写明 AI 参与了这次提交 | [1.15b](stages/01-foundations/15-review-ai-changes/lesson.md) |
| 项目说明文件 | project instruction file (CLAUDE.md, AGENTS.md) | 放在仓库根目录、写给 AI 看的项目规矩，在这个项目里开工时 AI 先读它 | [1.15c](stages/01-foundations/15-review-ai-changes/lesson.md) |
| 作品集 | portfolio | 能拿给别人看、证明你做得出来的一组作品 | [1.16a](stages/01-foundations/16-stage-project-and-gate/lesson.md) |
| 冷考 | cold test | 过了几天、不看提示、换一个没见过的情境再做一次，看你是不是真的会了 | [1.16b](stages/01-foundations/16-stage-project-and-gate/lesson.md) |
| 考官 | examiner | 只按评分标准和你的证据判过没过、不教你的那一方（这里是导师，或者一个新开的 Claude 对话） | [1.16b](stages/01-foundations/16-stage-project-and-gate/lesson.md) |
| 补考 | retest | 只重考还没通过的那几课，并且换另一套题面 | [1.16b](stages/01-foundations/16-stage-project-and-gate/lesson.md) |
| 回顾会 | Sprint Retrospective | Scrum 里每个冲刺结束时，团队一起复盘、定改进的固定会议 | [1.16c](stages/01-foundations/16-stage-project-and-gate/lesson.md) |

## 英文索引

按英文字母排；开头的点（比如 `.gitignore` 的点）不算。

| English | 术语 | 第一次出现 |
|---|---|---|
| absolute path | 绝对路径 | 0.2a |
| acceptance review | 验收 | 1.15a |
| API key | 接口密钥 | 1.9a |
| argument | 参数 | 1.6a |
| atomic commit | 原子提交 | 1.10a |
| authenticator app / TOTP app | 验证器 App | 1.11a |
| Auto Save | 自动保存 | 1.4a |
| back end | 后端 | 0.3a |
| backup | 备份 | 0.4c |
| baseline | 基线 | 1.14c |
| body | 正文 | 1.10b |
| branch | 分支 | 1.6a |
| breaking change | 破坏性变更 | 1.10b |
| byte | 字节 | 1.1a |
| case-sensitive | 区分大小写 | 1.3a |
| character encoding | 字符编码 | 1.4c |
| clone | 克隆 | 1.12c |
| cloud-synced folder | 云同步文件夹 | 0.2c |
| cold test | 冷考 | 1.16b |
| command | 命令 | 0.1a |
| Command Palette | 命令面板 | 1.4b |
| comment | 注释 | 1.3a |
| commit | 提交 | 1.6a |
| commit history | 本地历史 | 1.6b |
| commit message | 提交说明 | 1.6a |
| commit signing | 提交签名 | 1.6a |
| compliance requirement | 行业要求 | 0.3c |
| continuation prompt | 续行提示符 | 1.14a |
| convention | 惯例 | 0.3c |
| Conventional Commits | 约定式提交 | 1.10b |
| copy | 复制 | 1.2a |
| copyright | 版权 | 1.13a |
| data | 数据 | 0.3a |
| Definition of Done, DoD | 完成的定义 | 0.4a |
| delivery loop | 交付循环 | 1.13c |
| deploy | 上线 | 1.13b |
| deprecated | 弃用 | 1.14c |
| destructive command | 会丢数据的命令 | 1.8a |
| diff | 差异 | 1.7a |
| diffstat | 改动统计 | 1.15a |
| discard changes | 丢弃修改 | 1.8a |
| editor | 编辑器 | 0.1c |
| EditorConfig | EditorConfig | 1.4c |
| error message | 报错 | 0.1b |
| examiner | 考官 | 1.16b |
| explain-back question | 讲解题 | 0.4c |
| Explorer | 资源管理器 | 1.4a |
| extension | 扩展 | 1.4c |
| fenced code block | 代码块 | 1.5a |
| file extension | 扩展名 | 1.5a |
| finished with help | 带扶手完成 | 0.4b |
| footer | 脚注 | 1.10b |
| front end | 前端 | 0.3a |
| full-width character | 全角字符 | 0.2b |
| gate | 关卡 | 0.4c |
| Git | Git | 1.6a |
| GitHub | GitHub | 1.11a |
| GitHub Pages | GitHub Pages | 1.13b |
| .gitignore | .gitignore | 1.9a |
| global configuration | 全局设置 | 1.6a |
| global ignore file (core.excludesFile) | 全局忽略文件 | 1.9a |
| half-width character | 半角字符 | 0.2b |
| HEAD | HEAD | 1.6a |
| heading | 标题 | 1.5a |
| hidden file | 隐藏文件 | 1.1a |
| home folder | 主文件夹 | 0.2a |
| hunk | 改动块 | 1.7a |
| indentation | 缩进 | 1.4c |
| inline code | 行内代码 | 1.5a |
| integrated terminal | 内置终端 | 1.4b |
| interpreter | 解释器 | 0.1c |
| iteration | 迭代 | 0.4b |
| job expectation | 岗位期望 | 0.3b |
| Kanban board | 看板 | 0.4a |
| kebab-case | 短横线命名 | 0.2c |
| knowledge cutoff | 知识截止日期 | 1.14c |
| landing point | 落脚点 | 0.1a |
| lesson rules | 行规 | 0.1a |
| lesson text | 课文 | 0.1a |
| license | 许可证 | 1.13a |
| line ending | 换行符 | 1.4c |
| manual page (man page) | 说明书 | 0.2b |
| Markdown | Markdown | 1.5a |
| match | 匹配 | 1.3a |
| minimal reproducible example | 最小可复现示例 | 1.14b |
| MIT License | MIT 许可证 | 1.13a |
| move | 移动 | 1.2a |
| noreply email address | 隐私邮箱地址 | 1.11c |
| obligation level | 约束力 | 0.3c |
| operations | 运维 | 0.3b |
| option | 选项 | 1.1a |
| out-of-scope change | 范围外的改动 | 1.15b |
| package manager | 包管理器 | 1.11b |
| pager | 分页器 | 1.7b |
| parent folder | 上一级文件夹 | 0.2a |
| password manager | 密码管理器 | 1.11a |
| PATH | PATH | 1.11b |
| path | 路径 | 0.2a |
| pattern | 模式 | 1.3b |
| personal preference | 个人偏好 | 0.3c |
| placeholder | 占位写法 | 1.7a |
| playground | 练习场 | 0.1c |
| portfolio | 作品集 | 1.16a |
| preview | 预览 | 1.5a |
| private repository | 私有仓库 | 1.12b |
| program | 程序 | 0.1c |
| project folder | 项目文件夹 | 0.1a |
| project instruction file (CLAUDE.md, AGENTS.md) | 项目说明文件 | 1.15c |
| prompt | 提示符 | 0.1b |
| protocol | 协议 | 1.11b |
| public repository | 公开仓库 | 1.9b |
| push | 推送 | 1.12b |
| push protection | 推送保护 | 1.9b |
| Quick Open | 快速打开 | 1.4b |
| quotes | 引号 | 1.2b |
| README | README | 1.5b |
| recovery codes | 恢复码 | 1.11a |
| recursive | 递归 | 1.2a |
| relative path | 相对路径 | 0.2a |
| release notes | 发布说明 | 1.14c |
| remote | 远程仓库 | 1.12b |
| repository | 仓库 | 1.6a |
| requirements | 需求 | 0.3b |
| restore test | 恢复测试 | 1.12c |
| Restricted Mode | 受限模式 | 1.4a |
| retest | 补考 | 1.16b |
| retrospective | 复盘 | 0.4b |
| revoke / rotate a secret | 作废密钥 | 1.9b |
| root directory | 根目录 | 1.5b |
| rule type | 规则类型 | 0.3c |
| runtime environment | 运行环境 | 0.3a |
| save point | 存档点 | 0.1a |
| scope | 范围 | 1.10b |
| search across files | 跨文件搜索 | 1.4b |
| secret | 密钥 | 1.9a |
| server | 服务器 | 0.3a |
| shell | shell | 0.1b |
| software development life cycle | 软件生命周期 | 0.3b |
| source code | 源代码 | 1.11b |
| source file | 源文件 | 1.9a |
| Sprint Retrospective | 回顾会 | 1.16c |
| staging area | 暂存区 | 1.6b |
| standard | 标准 | 0.3c |
| static site | 静态网站 | 1.13b |
| status code | 状态码 | 0.3a |
| status line | 状态行 | 0.1a |
| tab | 标签页 | 0.1c |
| tab completion | Tab 补全 | 0.2a |
| tag | 标签 | 1.4a |
| task | 任务 | 0.4a |
| terminal | 终端 | 0.1a |
| testing | 测试 | 0.3b |
| text file | 文本文件 | 1.1b |
| token | 令牌 | 1.9a |
| track | 跟踪 | 1.8a |
| trailer | 尾注 | 1.15b |
| Trash | 废纸篓 | 1.2b |
| tutor | 导师 | 0.1a |
| two-factor authentication, 2FA | 双重验证 | 1.11a |
| type | 类型 | 1.10b |
| unstage | 取消暂存 | 1.8b |
| untrack (git rm --cached) | 取消跟踪 | 1.9b |
| untracked | 未跟踪 | 1.6b |
| upstream | 上游 | 1.12b |
| version control | 版本管理 | 1.6a |
| wildcard | 通配符 | 1.2b |
| WIP limit (work in progress) | 在制品限制 | 0.4a |
| working tree | 工作区 | 1.6b |
| workspace | 学习工作区 | 0.1a |
| Workspace Trust | 工作区信任 | 0.1c |
| zip archive | 压缩包 | 0.4c |
