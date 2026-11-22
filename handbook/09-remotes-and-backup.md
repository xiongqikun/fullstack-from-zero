# 远程仓库和备份

只在一台电脑上的仓库，电脑坏了就全没了。备份也可能不完整，只有真的恢复一次，才知道它能用。这一类规则让你在别处留一份完整的仓库，并在推送之前先查有没有密钥和别人的个人信息。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 这一类的卡片（2 张）

### REMOTE-01 重要仓库在别处有第二份，并且试过能恢复

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：重要的仓库（在本课程里是学习工作区和 my-site）至少在另一台机器上有一份远程仓库（例如 GitHub 上的私有仓库），每次学完或干完活就推送；至少亲手从那份远程仓库克隆恢复过一次，确认它是完整的。
- **谁说的**：《Pro Git》第 2 版中文版 1.1 节“关于版本控制”：分布式版本控制里“每一次的克隆操作，实际上都是一次对代码仓库的完整备份” https://git-scm.com/book/zh/v2/起步-关于版本控制 ；Git 官方 FAQ（gitfaq，最后更新于 Git 2.53.0，到 2.56.1 没有改动）“How do I sync a working tree across systems?”：不要用云同步服务同步仓库的任何部分，改用 push 和 pull https://git-scm.com/docs/gitfaq ；佐证“备份要定期测试能否恢复”：美国网络安全和基础设施安全局 CISA 的《#StopRansomware Guide》（勒索软件防范指南）2023 年 9 月版 https://www.cisa.gov/stopransomware/ransomware-guide
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 gitfaq 的这一条改动时
- **谁来管**：没有人；**不遵守的后果**：电脑丢了、硬盘坏了或者误删了，几个月的笔记和作品可能一起没了。
- **为什么**：只在一台电脑上的仓库，Git 的“后悔药”救不了硬件故障。远程仓库是第二份完整的拷贝，连历史都在。但备份可能过期、不完整，甚至根本取不出来，只有真的恢复一次才知道它能用。
- **正例**：每次学完，提交以后运行一次

      git push
      git status

  第一次推送以后，克隆到练习场比较一次：

      cd ~/Developer
      git clone https://github.com/你的用户名/my-fullstack-learning.git playground/restore-test
      cd playground/restore-test
      git log --oneline -1

- **反例**：仓库只在桌面上，靠 iCloud 同步当备份；或者半年前推送过一次，之后再也没推，也从没试过能不能取回来。
- **怎么检查**：`python3 tools/course.py check 1.12c`（学习工作区有 origin、有上游、没有没推送的提交）；`git status` 第二行要写 `Your branch is up to date with 'origin/main'.`；复习题 1.12-remote、1.12-restore。
- **例外**：只为一次练习建、用完就扔的仓库（比如练习场里的）不需要备份。
- **旧教程提醒**：老资料会把 iCloud、Dropbox 这类同步盘当成代码的备份。现在 Git 官方 FAQ 明确说不要用云同步服务同步仓库的任何部分，会损坏仓库；备份和换电脑都用 push 和 pull（自 Git 2.46.0 起，gitfaq 里加进了这一条；2026-11-19 对照 git 源码仓库各版本的 Documentation/gitfaq.txt 核对）。
- **学于**：1.12

> 原文在第 1.12 课「第一次推送和云端备份」的 [`rules.md`](../stages/01-foundations/12-push-and-backup/rules.md)。

### REMOTE-02 推送或公开之前，先查有没有密钥和隐私

- **约束力**：必须（适用范围：所有项目）
- **规则类型**：行业要求（只对别人的个人信息成立；你自己的密钥见 1.9 课 REPO-01，惯例·事实标准）
- **规则**：第一次提交、每次推送、把仓库改成公开之前，先读一遍 `git status`，再用 `git grep --untracked` 把要收进去、要推出去的文件（连还没跟踪的新文件）搜一遍像密钥、密码、令牌的内容，并想一想有没有别人的个人信息；有就先处理，再提交和推送。
- **谁说的**：GitHub 使用政策（Acceptable Use Policies）第 3 节（禁止未经同意发布他人的个人信息）、第 8 节（禁止滥用个人信息）、第 11 节之后不编号的执行说明（Enforcement：可以暂停、终止账号，删除内容）https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies ；《中华人民共和国个人信息保护法》第九条（处理者要保障所处理的个人信息的安全，2021-11-01 施行；第七十二条：个人或者家庭事务不适用）https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm ；GitHub Docs “About push protection”：用户的推送保护默认开启，只拦推到公开仓库的密钥，而且可以放行 https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection
- **核对日期**：2026-11-20；**复核周期**：6 个月（平台政策变得快），或者 GitHub 改动使用政策、推送保护时
- **谁来管**：别人的个人信息：平台（GitHub 可以按使用政策删内容、限制账号），在单位里处理个人信息时还有《个人信息保护法》和审计；你自己的密钥：没有人罚你，推送保护只拦推到公开仓库、它认得出的密钥，你自己还可以放行，后果由你承担；**不遵守的后果**：密钥被别人拿去用、产生费用或数据被偷；推上去以后再删也收不回来，克隆过的人手里还有。
- **为什么**：这条规则管两件事。别人的个人信息：GitHub 使用政策第 3、8 节禁止未经同意发布、滥用，平台可以删内容、封账号，所以类型是行业要求（七步判断法第 1 步就停下）。你自己的密钥：没有第三方能罚你，它的来历是 1.9 课的 REPO-01（惯例·事实标准），但后果一样是真的。提交了的东西会一直留在历史里，推送以后还会到别人的服务器上。`git status` 只告诉你哪个文件改了，不看内容；密钥常常是顺手粘进笔记里的一行。不加 `--untracked` 的 `git grep` 只搜已经被跟踪的文件，今天新写的文件会漏掉。你的私有仓库没有人替你拦：推送保护只管公开仓库。一旦推送，就只能先作废密钥，再考虑擦历史（1.9 课 REPO-01）。
- **正例**：

      git status
      git grep --untracked -n -i -E "password|token|secret|key|密码|密钥|令牌" -- notes journal learner

  `--` 后面的 `notes journal learner` 是学习工作区里你自己写东西的三个文件夹（课程材料里到处是这些词，搜出来全是说明）。在别的仓库里，去掉 `--` 和后面的文件夹名，搜整个仓库。输出很长时会进入分页器，按 q 退出。逐行读搜到的内容：是课文或你自己写的说明，放行；是真的密钥或令牌，先作废（让它失效、换一个新的），再从文件里拿掉或挡进 `.gitignore`，然后提交和推送。
- **反例**：觉得“反正是私有仓库”就直接 `git add .`、`git push`，没看过要推上去的是什么；或者在别的仓库里照抄 `-- notes journal learner`，那个仓库没有这三个文件夹，搜索什么也没搜就结束了。
- **怎么检查**：复习题 1.12-preflight；人工检查：提交和推送前，在终端里能看到自己刚运行过的 `git status` 和 `git grep`。
- **例外**：无。搜到的是课文、说明里提到的词（不是真的密钥），读过、确认过就可以提交和推送。
- **旧教程提醒**：无
- **学于**：1.12

> 原文在第 1.12 课「第一次推送和云端备份」的 [`rules.md`](../stages/01-foundations/12-push-and-backup/rules.md)。
