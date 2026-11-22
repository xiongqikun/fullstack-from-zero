<!-- 第 1.11 课的两张规则卡（格式见计划 I2）。核对日期是建课当天实际打开来源的日期。 -->

### ACC-01 GitHub 账号开启双重验证

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：行业要求（平台强制政策）
- **规则**：注册当天就开启双重验证，并把恢复码存进密码管理器或打印出来，放在手机以外的地方。主要方式按 GitHub 的推荐用验证器 App（这一点是平台的推荐，不是强制）；以后可以再加一把通行密钥。
- **谁说的**：GitHub Docs “About mandatory two-factor authentication” https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication ；“Configuring two-factor authentication” https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication ；“Configuring two-factor authentication recovery methods” https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication-recovery-methods ；GitHub Blog “Raising the bar for software security: GitHub 2FA begins March 13”（2023-03-09）（文档页面没有版本号，2026-11-20 读取的版本；GitHub 文档原话：TOTP 是推荐的主要方式，目前不支持把通行密钥或安全密钥当主要方式）
- **核对日期**：2026-11-20；**复核周期**：6 个月（平台政策变得快），或者 GitHub 宣布接受通行密钥当主要方式时
- **谁来管**：平台（GitHub），只管被它选中的“贡献代码”账号，对其他账号是“强烈建议”；对你：现在是本课程要求，一旦被 GitHub 选中，就成了平台强制；**不遵守的后果**：账号一旦被选中，45 天设置期加 7 天宽限期过后，不开双重验证就进不了 GitHub.com；账号被盗，你所有的仓库和网页都可能被人改掉。
- **为什么**：只有密码时，密码泄露就等于账号丢了。GitHub 自 2023 年 3 月起要求在 GitHub.com 上贡献代码的用户开启双重验证：账号发布过 App 或 Action、创建过发行版（release）、当过有仓库的组织的所有者，这类事情就会让它被选中，选中时会收到邮件。GitHub 还写明，邮箱验证不算第二步，因为拿到你邮箱的人可以重设密码。
- **正例**：验证器 App 已绑定；全部恢复码存在密码管理器（比如 Mac 自带的 Passwords App）里，或者打印出来锁好，“下载”文件夹里的那份已经删掉；退出再登录时用验证器 App 完成第二步。
- **反例**：只用短信；以为邮箱验证码就是双重验证；恢复码截图存在同一部手机的相册里；恢复码放进学习工作区（不管它真正在哪个文件夹）、`~/Developer` 下的任何文件夹或任何仓库里（这些文件夹会变成仓库、被推送到 GitHub）；等 GitHub 发邮件催了再说。
- **怎么检查**：复习题 1.11-r1、1.11-r2；人工检查：在 GitHub 的 Settings → Password and authentication 页面，确认 Two-factor authentication 一栏显示已经开启，并说得出恢复码存在哪里。
- **例外**：由公司统一管理的企业账号（Enterprise Managed Users）由公司的登录系统负责，不适用这条个人账号政策。
- **旧教程提醒**：旧教程常说“双重验证用短信就行”。GitHub 自 2023 年 3 月推行强制双重验证起写明：尽量用安全密钥和验证器 App，短信不再推荐（GitHub Blog，2023-03-09）；现在的文档“强烈建议”用验证器 App，因为短信可能被截获，有的地区还收不到。
- **学于**：1.11

### ACC-02 提交邮箱用 GitHub 的隐私地址

- **约束力**：推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：在 GitHub 的 Emails 设置页勾选 Keep my email addresses private 和 Block command line pushes that expose my email，再把 Git 的 `user.email` 设成页面上给出的 noreply 地址。
- **谁说的**：GitHub Docs “Setting your commit email address” https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address ；“Email addresses reference” https://docs.github.com/en/account-and-profile/reference/email-addresses-reference ；“Blocking command line pushes that expose your personal email address” https://docs.github.com/en/account-and-profile/how-tos/email-preferences/blocking-command-line-pushes-that-expose-your-personal-email-address （2026-11-20 读取的版本）
- **核对日期**：2026-11-20；**复核周期**：12 个月
- **谁来管**：平台（只在你勾选“阻止推送”以后才会拦，而且每次推送只看最新的一个提交；继续用自己邮箱的人要把这个勾去掉，否则推送会被拒绝）；**不遵守的后果**：你的真实邮箱跟着每个提交公开，任何人都能用程序批量抓走，招来垃圾邮件和钓鱼邮件。
- **为什么**：每个提交里都写着作者的名字和邮箱，推送到公开仓库后，谁都能用 `git log` 看到。隐私地址照样能让 GitHub 把提交算在你的账号名下，只是不收信。改设置只影响以后的提交，以前的提交里还是旧邮箱；GitHub 文档写明“阻止推送”只检查最新的一个提交，所以更早的提交会照原样公开。
- **正例**：

      git config set --global user.email "12345678+你的用户名@users.noreply.github.com"
      git log -1 --format='%h %an <%ae>'

- **反例**：把常用的私人邮箱写进 `user.email`，然后推送到公开仓库；以为改了设置，以前的提交就会跟着改。
- **怎么检查**：在仓库里运行 `git log --format='%h %ae'`，每一行的邮箱都应该以 `@users.noreply.github.com` 结尾；复习题 1.11-r5。
- **例外**：单位要求用工作邮箱提交时，按单位的规定；你想让别人通过提交联系你时，也可以用自己的邮箱，这是你的选择。
- **旧教程提醒**：很多教程只教设置 `user.email` 为“你的邮箱”，不提隐私地址。GitHub 至少从 2017 年 4 月起就请想保密的人打开隐私设置、用隐私地址提交：那时它加上了“阻止暴露邮箱的推送”这一项（GitHub Blog “Private emails, now more private”，2017-04-11，2026-11-20 核对）。地址的样子后来又改过一次：2017 年 7 月 18 日以后注册的账号，隐私地址的样子是 `编号+用户名@users.noreply.github.com`；没有编号的旧样子只属于那之前开启隐私设置的老账号。
- **学于**：1.11
