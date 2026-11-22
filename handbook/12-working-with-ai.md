# 和 AI 一起干活

AI 交来的说明是它自己的总结，会漏，也会说错；Git 记下的改动清单才是事实。提交是你签字的那一步，签了字，出了问题算你的。这一类规则让你先看改动再接受，并在提交里如实写明 AI 参与过。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（2 张）

### AI-01 AI 的改动先看 diff 再接受

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：规范·组织
- **规则**：AI 改完之后、你提交之前，按顺序看 git status、git diff --stat、git diff，再亲眼看效果（打开网页或运行程序）；改动清单里每一处你都能说清是什么、为什么，才由你亲手提交，否则用 git restore 退回、用 rm 清掉多出来的文件。
- **谁说的**：开源安全基金会（OpenSSF，Linux 基金会旗下推动开源软件安全的组织）最佳实践与 AI/ML 工作组《Security-Focused Guide for AI Code Assistant Instructions》（2025-08-01）说开发者对代码造成的后果负责，AI 生成的代码不能绕过代码评审（有人逐行看过改动再放行）、测试和版本管理 https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions ；GitHub Docs《Review AI-generated code》要求留意编造的接口、被忽略的约束、被删掉或跳过的测试 https://docs.github.com/en/copilot/tutorials/review-ai-generated-code ；LLVM（一个很大的开源编译器项目；编译器是把程序翻译成电脑能直接执行的指令的软件）《AI Tool Use Policy》（页面更新于 2026-11-19）：贡献者永远是作者，对自己的贡献负全部责任 https://llvm.org/docs/AIToolPolicy.html 。验收的先后顺序是本课程的做法（第 1.15 课，2026-11-20 版）。规则类型按七步判断法在第 5 步停下：AI 生成的代码不能绕过评审，是 OpenSSF 的工作组以自己组织的名义写明的。
- **核对日期**：2026-11-20；**复核周期**：6 个月（AI 工具和各组织的 AI 政策变得快），或者课程换了导师工具时
- **谁来管**：评审人（在这门课里就是你自己；在团队里是看你改动的同事）；**不遵守的后果**：AI 顺手改的、多加的、说错的东西进了历史，甚至被推送到公开仓库，事后才发现就要花更多工夫收拾。
- **为什么**：AI 的交付说明只是它自己的总结，会漏、会说错；git 记下的改动清单才是事实。第 2 站里 AI 说只改了一个文件，git status 列出了三个文件。提交是你签字的那一步，签了字，出了问题算你的。
- **正例**：

      git status
      git diff --stat
      git diff
      open index.html
      git add index.html
      git commit -m "feat: 在首页加一节我在学什么" -m "Co-Authored-By: Claude <noreply@anthropic.com>"

- **反例**：AI 说“改好了，测试都过了”，你没看改动就 git add . 加 git commit；或者让 AI 自己提交、自己推送，事后才去看。
- **怎么检查**：复习题 1.15-r1、1.15-d1；人工检查：提交前最后一次 git status 里列出的每个文件，你都能说出它为什么改。
- **例外**：无。改动很大、读不完时，不是跳过验收，而是请 AI 拆成几次小改动，一次验收一次。
- **旧教程提醒**：旧资料说 Claude Code 每改一个文件、每跑一条命令都先问你，你点了同意就算看过；现在，自 Claude Code v2.1.283 起，它的命令行版和 VS Code 插件默认用自动模式（Auto），很多操作不再问你；Claude 桌面应用按你设置里的默认权限模式，开始前看一眼输入框旁边的模式选择，大多数改文件、跑命令的操作之前都先问你的那一种叫 Manual（Claude Code 文档 Permission modes，2026-11-20 核对）。没有弹窗问你，不等于什么都没改，以 git status 和 git diff 为准。
- **学于**：1.15

> 原文在第 1.15 课「验收 AI 的改动」的 [`rules.md`](../stages/01-foundations/15-review-ai-changes/rules.md)。

### AI-02 AI 参与的提交如实署名

- **约束力**：推荐（适用范围：所有项目）；必须（适用范围：本课程）；项目有自己的 AI 政策时以项目的为准
- **规则类型**：惯例·平台与工具
- **规则**：一次提交里有 AI 写的或起草的内容，就在提交说明的最后一段加一行尾注写明，比如 Co-Authored-By: Claude <noreply@anthropic.com>；项目规定了别的写法（Assisted-by:、Generated-by:）就用项目的。署名不转移责任：你仍然是作者，要能讲清每一行。
- **谁说的**：Claude Code 文档 Settings reference 的 attribution 一节：默认给提交加 `Co-Authored-By: <name> <noreply@anthropic.com>`，名字是提交时用的模型名（比如 Claude Sonnet 5；2026-11-20 再次核对） https://code.claude.com/docs/en/settings-reference ；GitHub Docs《Creating a commit with multiple authors》：描述之后空一行，每位合作者一行 `Co-authored-by: name <name@example.com>` https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors ；LLVM《AI Tool Use Policy》要求给含大量工具生成内容的贡献加标注，举例用 `Assisted-by:` 尾注 https://llvm.org/docs/AIToolPolicy.html ；Apache 软件基金会《Generative Tooling》建议在提交说明里写 `Generated-by:` 或 `Co-authored-by:` https://www.apache.org/legal/generative-tooling.html ；Linux 内核（Linux 系统最核心的那部分程序）文档《AI Coding Assistants》（7.4.0-rc3）：AI 不得添加 Signed-off-by，由提交的人负全部责任 https://docs.kernel.org/process/coding-assistants.html
- **核对日期**：2026-11-20（Claude Code 文档；其余来源 2026-11-19）；**复核周期**：12 个月（或者 Claude Code 的署名设置变了时）
- **谁来管**：评审人；在要求标注的开源项目里，维护者可以拒收没标注的贡献；**不遵守的后果**：以后查问题时分不清哪些改动出自 AI，也可能违反你参与的项目的规定。
- **为什么**：仓库是账本，聊天记录过几周就找不到了。尾注写进提交，三个月后一条命令就能找出所有 AI 参与过的提交，回头复查时知道该重点看哪里。各家写法还没统一，但“如实写明”这件事，上面几个来源说法一致。
- **正例**：

      git commit -m "docs: 添加给 AI 的项目说明" -m "Co-Authored-By: Claude <noreply@anthropic.com>"

- **反例**：AI 起草、你几乎没改的文件，提交说明里只字不提；或者反过来，让 AI 替你写上 Signed-off-by 之类代表你本人担保的行。
- **怎么检查**：检查 1.15b 会看那次提交有没有尾注，复习题 1.15-d1 也一样；命令 `git log -1` 看最新提交的说明末尾有没有那一行。
- **例外**：AI 只回答了你的问题、文件完全是你自己写的，不用加。
- **旧教程提醒**：旧资料说 Claude Code 用 includeCoAuthoredBy 这个设置开关署名；现在它已弃用（自 Claude Code v2.0.62 起），换成 attribution（署名）设置（Claude Code 文档 Settings reference，2026-11-19 核对）。
- **学于**：1.15

> 原文在第 1.15 课「验收 AI 的改动」的 [`rules.md`](../stages/01-foundations/15-review-ai-changes/rules.md)。
