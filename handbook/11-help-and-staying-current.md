# 求助和与时俱进

帮你的人看不到你的电脑，只能靠你给的目标、步骤、报错原文和版本来重现问题。工具一直在变，教程、问答和 AI 的回答里有不少是旧版本的做法。这一类规则让你把问题问清楚，并在照着一份资料动手之前，先查它的日期和版本。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（2 张）

### HELP-01 提问给出目标、做法、期望、实际报错原文、版本

- **约束力**：推荐（适用范围：所有项目）；在本课程里向导师求助时是必须（适用范围：本课程）
- **规则类型**：惯例·平台与工具
- **规则**：求助前先做一个最小可复现示例；提问写五段：目标、我做了什么（从空文件夹开始的每条命令）、我期望什么、实际看到什么（报错原文，原样粘贴）、版本。
- **谁说的**：各个平台在自己的帮助页里对“怎么报告问题”的要求。uv（第 2 阶段要用的 Python 工具）官方文档“Reproducible examples” https://docs.astral.sh/uv/reference/troubleshooting/reproducible-examples/ （页面日期 2026-11-17；要求写明操作系统和架构、uv 和相关工具的版本、能直接运行的命令、详细日志，并把例子删到最小）；Python 3.15.2 文档“Dealing with Bugs” https://docs.python.org/3/bugs.html （要求写期望和实际发生了什么、平台和版本）；Stack Overflow（程序员问答网站）帮助中心“How to create a Minimal, Reproducible Example” https://stackoverflow.com/help/minimal-reproducible-example （2026-11-19 返回 403，2026-11-20 网站拒绝了自动访问，内容只经搜索摘要核对，没有读到原文）。这三处各自写着自己的要求；只有 Stack Overflow 在自己的网站上执行它（见“谁来管”），另外两处只是期待。背景：Eric S. Raymond、Rick Moen《How To Ask Questions The Smart Way》修订版 3.10（2014-05-21）http://www.catb.org/~esr/faqs/smart-questions.html ，“Before You Ask”和“Describe the goal, not the step”两段；中文版《提问的智慧》（基于原文 3.10 版）https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way/blob/main/README-zh_CN.md
- **核对日期**：2026-11-20；**复核周期**：12 个月（uv、Python、Stack Overflow 的帮助页会改），或者 Stack Overflow 帮助页能打开时补读原文
- **谁来管**：没有法律或合同管它。在 Stack Overflow 上，社区成员和版主会把缺少必要细节的问题关闭：关闭后别人不能再回答，补好细节可以申请重新打开（这一点 2026-11-20 只经 Stack Overflow 公司的企业版帮助页“What does it mean if a question is closed”和搜索摘要核对，公开站的帮助页没有读到）。这只管在那一个网站上提的问题，所以整条规则仍是惯例·平台与工具，不是行业要求。在别的地方（项目的问题追踪页、导师、同事），回答的人和项目维护者自己决定帮不帮；**不遵守的后果**：在 Stack Overflow 上问题被关闭；在别处问题没人回答，或者被要求补信息，来回好几轮才说清楚。
- **为什么**：帮你的人看不到你的电脑。只有目标、步骤、报错原文和版本都在，对方才能在自己电脑上重现问题；做最小复现的过程中，你常常自己就找到了原因。截图里的字没法复制和搜索，改写过的报错会丢掉关键词。
- **正例**：

      # 提问：新仓库里 git restore --staged 报 could not resolve 'HEAD'
      ## 目标
      想把 a.txt 从暂存区拿出来。
      ## 我做了什么
      mkdir mini
      cd mini
      git init
      touch a.txt
      git add a.txt
      git restore --staged a.txt
      ## 我期望什么
      a.txt 回到“未跟踪”。
      ## 实际看到什么
      fatal: could not resolve 'HEAD'
      ## 版本
      git version 2.54.0 (Apple Git-157)；macOS 27.2.1

- **反例**：“git 坏了，怎么办？”；只发一张截图；把报错改写成“它说找不到什么东西”；贴出几十个文件的大项目让别人自己找；路径里带着自己的用户名。
- **怎么检查**：复习题 1.14-question-parts（会排进 `review`）；1.14b 的检查（`python3 tools/course.py check 1.14b`）会看最小复现、五段、报错原文和版本号。
- **例外**：只是问“这个命令是什么意思”这类概念问题时，不需要复现步骤，但仍要写目标和你已经查过的地方。
- **旧教程提醒**：《提问的智慧》写于 2001 年、最后修订于 2014 年，语气很冲，里面的论坛和邮件列表很多已经不在了；有用的是方法，不是语气。
- **学于**：1.14

> 原文在第 1.14 课「排错、求助与“与时俱进”」的 [`rules.md`](../stages/01-foundations/14-errors-help-fresh/rules.md)。

### FRESH-01 用一个做法前确认它的版本和日期

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：规范·本课程约定
- **规则**：照着任何教程、问答或 AI 的建议动手之前，做三查：它是哪天写的，它说的是哪个版本，官方文档和你电脑上的工具（`-h`、`man`、提示信息、`python3 tools/course.py fresh`）现在是不是还这么说。
- **谁说的**：本课程计划 G4“与时俱进”和课程调研 docs/research/currency-mechanisms.md 第 1.4 节（2026-11-19 版）；做法依据的官方页面（2026-11-20 打开核对）：Git 文档 https://git-scm.com/docs （每页写着“last updated in”哪个版本，默认显示最新版，页面顶上的 Latest version 菜单能换版本）、GitHub 更新日志 https://github.blog/changelog/ 、VS Code 发布说明 https://code.visualstudio.com/updates
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 `fresh` 报告有工具的版本变了
- **谁来管**：导师和你自己；**不遵守的后果**：照着过时的步骤做，轻则结果和教程对不上，重则用上已经不安全或已经失效的做法，还以为是自己做错了。
- **为什么**：工具常常几周就出一个新版本（VS Code 自 2026 年 3 月起每周出一个正式版），规范几年才出一个新版（约定式提交至今还是 1.0.0）。资料的日期只能提醒你去查；真正说了算的是你电脑上装的工具和它的官方文档。AI 也有知识截止日期，它会很有把握地说出旧做法。
- **正例**：看到 2020 年的资料写 `git checkout -- index.html`，先在自己的仓库里看 `git status` 的提示，发现现在推荐 `git restore index.html`，再去 https://git-scm.com/docs/git-restore 确认。
- **反例**：照抄一篇老博客里的 `git push origin master`，推送失败后反复重试；或者认定“2019 年的东西一律过时”，把还有效的约定式提交 1.0.0 也扔掉。
- **怎么检查**：复习题 1.14-who-decides；运行 `python3 tools/course.py fresh`，看结论是不是“一致”。
- **例外**：无
- **旧教程提醒**：无（这张卡本身就是用来识别旧教程的）
- **学于**：1.14

> 原文在第 1.14 课「排错、求助与“与时俱进”」的 [`rules.md`](../stages/01-foundations/14-errors-help-fresh/rules.md)。
