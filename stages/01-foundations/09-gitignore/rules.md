### REPO-01 密钥、密码、令牌永不入库

- **约束力**：必须（适用范围：所有项目）
- **规则类型**：惯例·事实标准（OWASP ASVS：公开、带版本号的安全要求清单）
- **规则**：密钥、密码、令牌不写进任何会被提交的文件；放它们的文件（比如 `.env`）在第一次提交之前就写进 `.gitignore`。万一提交了，先到发密钥的地方把它作废、换新的，再让 Git 放手这个文件。
- **谁说的**：OWASP Application Security Verification Standard（ASVS）5.0.0（2025 年 5 月）第 13.3.1 条 https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x22-V13-Configuration.md （这一条要求密钥由专门的密钥管理方案保管，不能出现在源代码（程序的原文）和构建产物（程序打包出来的文件）里。它属于 ASVS 第 2 级：ASVS 把要求分三级，说大多数应用都该努力做到第 2 级，做到哪一级由各家按自己的风险决定，见 https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x03-What-is-the-ASVS.md 。本课程把其中“不进仓库”这一半定为所有项目都必须）；OWASP Secrets Management Cheat Sheet 第 9.2 节 https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html （泄露的密钥要立即作废，并尽快换上新的）；GitHub Docs「Removing sensitive data from a repository」https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository （第一步是作废或更换密钥；改写历史用 git-filter-repo 2.47 以上；改写以后，别人下载走的副本、别人在 GitHub 上复制的副本和 GitHub 的缓存页面里可能还有）；GitHub Docs「About push protection」https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection （个人账号的推送保护默认打开，拦下推送到公开仓库、而且认得出类型的密钥；推送的人可以选择放行，它只认得出页面列出的几类密钥）。ASVS 按版本号引用，其余三页是持续更新的网页，按核对日期引用。
- **核对日期**：2026-11-20；**复核周期**：6 个月（平台功能变化快），或者 ASVS 出新版、GitHub 改了推送保护的默认设置时
- **谁来管**：在你自己的项目里没有人能罚你。GitHub 的密钥扫描和推送保护是工具，不是处罚：默认会拦一道，但你自己可以放行，认不出的格式也拦不住。合同、审计或公司的安全制度写了这一条时，管的是签了合同、接受审计的公司和在那里干活的人：那条合同条款或制度本身是行业要求，管你的是客户、审计方或公司；ASVS 的规则类型不变，还是惯例·事实标准，只是在那个项目里约束力是必须（适用范围：所在团队）；**不遵守的后果**：别人拿到密钥就能冒用你的账号、花你的钱、看你的数据，而且历史里的密钥删不干净。
- **为什么**：仓库会被复制、推送、公开，历史里的每一个版本都留着。一个密钥只要进过一次提交，就要当它已经泄露。挡在门外比事后清理便宜得多。
- **正例**：

      # .gitignore 里，第一次提交之前就写好
      .env

- **反例**：把 `API_KEY=...` 直接写在 `convert.py` 里提交；或者以为“后来删掉这一行再提交一次”就没事了。
- **怎么检查**：提交前运行 `git status`，看列出的文件里有没有放密钥的文件；用 `git check-ignore -v .env` 确认它被挡住；复习题 1.9-r2。
- **例外**：故意公开的假数据和示例文件，比如只写了键名、没有真实值的 `.env.example`（以后的阶段会用到）。
- **旧教程提醒**：旧教程常教用 `git filter-branch` 或 BFG（两种改写历史的工具）把密钥从历史里删掉，好像删干净就安全了。现在 Git 自 2.24（2019 年）起不鼓励用 filter-branch，GitHub Docs 改用 git-filter-repo（现在推荐的改写历史的工具，2.47 以上）；而且官方给的顺序是先作废密钥，清理历史是之后的事，单靠清理不够，别人复制走的副本里还有。
- **学于**：1.9

### REPO-02 .gitignore 从官方模板起步

- **约束力**：推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：新项目先看 GitHub 官方模板库里有没有对应语言或工具的模板（比如 Python 项目用 `Python.gitignore`）；有就从它起步，再补上只属于这个项目的几行，并读一遍自己加了什么。
- **谁说的**：GitHub「github/gitignore」模板库 https://github.com/github/gitignore （README 说明：根目录是常用模板，`Global` 文件夹是编辑器、工具和操作系统的模板，可以放进全局忽略文件，或者合进项目的模板；许可证 CC0-1.0）；GitHub Docs「Ignoring files」https://docs.github.com/en/get-started/git-basics/ignoring-files （GitHub 维护一份官方推荐的 .gitignore 列表）；Git 手册 gitignore(5) https://git-scm.com/docs/gitignore （人人都要忽略的写进 .gitignore，只和自己电脑或编辑器有关的写进 core.excludesFile；该页最后修改于 Git 2.55.0，本机是 2.54.0）。
- **核对日期**：2026-11-20；**复核周期**：12 个月
- **谁来管**：没有人；**不遵守的后果**：自己写的名单容易漏，缓存、虚拟环境、`.env` 这类东西会被 `git add .` 一起带进仓库。
- **为什么**：每种语言和工具都会生成自己的一堆杂物，名字五花八门。模板是很多人踩过坑之后整理出来的，比自己凭记忆写全得多。读一遍，你也知道这个项目会产生哪些东西。
- **正例**：Python 项目的 `.gitignore` 从 `Python.gitignore` 起步，里面已经有 `__pycache__/` 和 `.env`；再在末尾加上项目自己的 `secret-token.txt`。
- **反例**：只凭印象写一两行，或者从网上随便一篇文章里抄一份没读过的长名单。
- **怎么检查**：人工检查：打开 `.gitignore`，看开头是否来自对应的官方模板，自己加的行是否都看得懂；`git status --ignored` 看被挡住的是不是你想挡的。
- **例外**：没有对应模板的项目（比如你手写的 `my-site`，只有 HTML 和 CSS，没有程序会生成杂物）：从最少的几行开始，用到什么再加。操作系统和编辑器的杂物（比如 `.DS_Store`）放在全局忽略文件里也可以（你的电脑有没有设置过，第 1.9 课「想多了解」讲怎么看）。
- **旧教程提醒**：无
- **学于**：1.9
