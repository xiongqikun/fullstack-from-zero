# 文档

打开一个陌生项目的人，第一件事是找说明。没有 `README.md`，别人看不出这是什么、怎么用，六个月后的你也一样。这一类规则规定说明放在哪里、回答哪几个问题。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（2 张）

### DOC-01 每个项目根目录有 README.md

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：每个项目最外层的文件夹（根目录）里放一个用 Markdown 写的 `README.md`，文件名照惯例大写 README、小写 .md。
- **谁说的**：GitHub Docs「About the repository README file」（在线文档，没有版本号）https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes ：GitHub 在三个位置找 README，先找 `.github`（放 GitHub 专用设置的隐藏文件夹），再找根目录，最后找 `docs`（放文档的子文件夹），找到就显示在项目首页；惯例是放在根目录。Markdown 的写法以 CommonMark 0.31.2（2024-01-28）https://spec.commonmark.org/ 和 GitHub Flavored Markdown 0.29-gfm（2019-04-06）https://github.github.com/gfm/ 为准。
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 GitHub 改了显示 README 的方式时
- **谁来管**：本课程的检查（check 1.5b）；在别的项目里没有人强制，只是 GitHub 只在这几个固定位置找 README；**不遵守的后果**：别人打开你的项目，首页只有一串文件名，不知道这是什么、敢不敢用。
- **为什么**：打开一个陌生文件夹的人，第一件事是找说明。说明放在固定的位置、用固定的名字，人和工具不用猜就能找到。GitHub 这类存放代码的网站会把根目录的 README.md 排好版，直接显示在项目首页；在 VS Code 里打开它、按 ⇧⌘V 也能看到排好版的样子。
- **正例**：

      my-site/
      ├── README.md
      ├── index.html
      └── style.css

- **反例**：说明写在 `说明.docx` 或 `notes.txt` 里；README 放进了某个随便的子文件夹；文件名写成 `readme.txt`。
- **怎么检查**：在项目根目录运行 `ls`，能看到 `README.md`；本课检查 `python3 tools/course.py check 1.5b`。
- **例外**：练习场里用完就扔的文件夹、只放一两个临时文件的草稿文件夹，可以不写。
- **旧教程提醒**：无
- **学于**：1.5

> 原文在第 1.5 课「Markdown 与 README」的 [`rules.md`](../stages/01-foundations/05-markdown-readme/rules.md)。

### DOC-02 README 回答五个问题

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：规范·本课程约定
- **规则**：README 依次回答：这是什么；怎么用或怎么看到效果；文件夹里有什么；现在的状态和下一步打算；作者是谁、用什么许可证。第 1 个问题写在一级标题下面的一两句里，其余每个问题一个小节；没话可说的小节宁可不写，也不留空壳。
- **谁说的**：本课程（“五个问题”这个分法），内容取自两份资料：GitHub Docs「About the repository README file」https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes （README 通常写：项目做什么、为什么有用、怎么开始用、去哪求助、谁在维护）；Make a README（Danny Guo 维护，没有版本号）https://www.makeareadme.com/ （建议的小节有名称、简介、徽章（项目首页上显示状态的小图标）、截图、安装、使用、求助、路线图、参与贡献、作者、许可证、项目状态，并说明每个项目不同，按需挑选）。这两份都只是描述通行做法，没有哪个平台检查 README 的内容，所以规则类型是本课程约定，不是平台惯例。
- **核对日期**：2026-11-20；**复核周期**：12 个月
- **谁来管**：本课程的检查（check 1.5b）；在别的项目里没有人会拦你，读者和评审人会注意；**不遵守的后果**：别人不知道怎么用，几个月后的你自己也想不起来当初怎么运行它。
- **为什么**：README 是写给陌生人的，而六个月后的你也是陌生人。这五个问题正好是一个人第一次打开项目时会依次想问的。答不上来的那个问题，往往就是项目里还没想清楚的地方。
- **正例**：

      # hello-fx

      按固定汇率换算一笔钱的小程序，打印一行结果。

      ## 怎么运行

      ```zsh
      python3 convert.py
      ```

      ## 里面有什么

      - `convert.py`：程序本身
      - `rates.txt`：示例汇率（程序现在还没用到它）

      ## 现在的状态

      练习用。汇率是写死的示例数字，不是真实汇率。

- **反例**：整份 README 只有一行「# my-site」；或者照抄模板，留着「在这里写项目简介」这样的空话。
- **怎么检查**：本课检查 `python3 tools/course.py check 1.5b`（它看 my-site 的 README 有没有至少三个二级标题、一个列表、一个代码块或链接，并提到 index.html；小节回答的是哪几个问题，检查看不出来，由人工检查；第五个问题里的许可证第 1.13 课补上）；复习题 1.5-readme-questions；人工检查：请一个没见过这个项目的人只读 README，看他能不能说出这五个问题的答案。
- **例外**：很小的练习文件夹只回答前三个问题就够了。
- **旧教程提醒**：以前很多 README 开头手写一份目录；现在 GitHub 会按标题自动生成目录（自 2021-04-13 起，见 GitHub 的更新公告（GitHub Changelog）「Table of Contents support in Markdown files」），短的 README 不用手写目录。
- **学于**：1.5

> 原文在第 1.5 课「Markdown 与 README」的 [`rules.md`](../stages/01-foundations/05-markdown-readme/rules.md)。
