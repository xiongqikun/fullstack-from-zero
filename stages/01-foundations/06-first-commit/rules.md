<!-- 第 1.6 课的规则卡。格式见建课计划 I2：十三个字段，全部必填。 -->

### GIT-01 一个项目一个仓库，在项目根目录初始化

- **约束力**：推荐（适用范围：所有项目）；必须（适用范围：本课程）
- **规则类型**：惯例·平台与工具
- **规则**：先 cd 进项目最外层的文件夹（项目根目录），运行 git status 确认它还不在任何仓库里（看到 not a git repository），再在这里运行 git init。标题里的“一个项目一个仓库”（不往上层建，也不在项目里面再建）是这门课对这个做法的读法，下面两份资料没有这样写。
- **谁说的**：《Pro Git》第 2 版中文版 2.1「获取 Git 仓库」（进入项目目录再 git init；2026-11-20 读取）https://git-scm.com/book/zh/v2/Git-基础-获取-Git-仓库 ；git-init 手册（git-scm.com 上的版本最后更新于 Git 2.54.0，和这台电脑的 Git 一致；2026-11-20 读取）https://git-scm.com/docs/git-init
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 Git 发布 3.0 时
- **谁来管**：所有项目里没有人管：Git 不拦你在错的那一层运行 git init；在这门课里，第 1.6 课第 3 站的检查会看 my-site 和它的上层是不是各只有一个仓库；**不遵守的后果**：建高了，几个项目的改动搅进同一段历史，备份和公开都分不开；建低了，项目里有一部分文件 Git 根本看不见。
- **为什么**：git init 在哪个文件夹里运行，就把那个文件夹连同它下面的一切交给 Git 管。在 ~/Developer 里运行，my-site、playground（学习工作区如果在 ~/Developer/fullstack-from-zero，也算在内）都会变成一个大仓库里的普通文件夹；到第 1.13 课公开网站时，你就没法只公开 my-site。在这门课里它是必须：my-site 是一个仓库，第 1.12 课起学习工作区也是一个仓库。
- **正例**：

      cd ~/Developer/my-site
      git status        # 应该看到 fatal: not a git repository，说明这里和上面都还没有仓库
      git init

- **反例**：在 ~/Developer、主文件夹 ~ 或桌面上运行 git init；在项目里面的某个子文件夹里再 git init 一次，造出“仓库套仓库”。
- **怎么检查**：在项目根目录运行 git status，第一行应该是 On branch main；在项目的上一层运行 git status，应该看到 fatal: not a git repository。复习题 1.6-r3。
- **例外**：团队明确决定把多个项目放进一个大仓库（叫 monorepo，单一大仓库）时，按团队的约定做；这是阶段 3 以后的话题，由团队决定，不由个人决定。
- **旧教程提醒**：无。进项目根目录再 git init，这个做法多年没有变。变过的是第一个分支的名字：旧教程里叫 master，GitHub 自 2020 年 10 月起新仓库默认用 main，Git 自己要到还没定日期的 3.0 才改（Git 文档 BreakingChanges，2026-11-19 核对；git-init 手册 2.54.0 版，2026-11-20 核对）；这和本条规则无关，详见第 1.6 课第 1 站末尾的「想多了解」。
- **学于**：1.6

### GIT-02 提交前确认身份设置

- **约束力**：推荐（适用范围：所有项目）；必须（适用范围：本课程）
- **规则类型**：惯例·平台与工具
- **规则**：在一台电脑上第一次提交之前，运行 git config get user.name 和 git config get user.email，确认两样都设置了，而且是你愿意公开的名字和邮箱。
- **谁说的**：《Pro Git》第 2 版中文版 1.6「初次运行 Git 前的配置」（每个提交都会写入用户名和邮箱，写入后不可更改；2026-11-20 读取，书里用的是 git config --global 这种老写法）https://git-scm.com/book/zh/v2/起步-初次运行-Git-前的配置 ；GitHub Docs「Setting your commit email address」（用 git config 设的邮箱会出现在你以后推送的提交里；换邮箱之前的提交仍然连着旧邮箱）https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address （2026-11-20 读取的版本）；GitHub Docs「Troubleshooting missing contributions」（提交要用已经加进账号的邮箱或 GitHub 给的 noreply 地址，才算在你名下；像 jane@computer.local 这样的地址加不进账号；2026-11-20 读取）https://docs.github.com/en/account-and-profile/reference/why-are-my-contributions-not-showing-up-on-my-profile ；本机实测：Git 2.54.0（Apple Git-157），身份没设置时提交照样成功
- **核对日期**：2026-11-20；**复核周期**：12 个月
- **谁来管**：所有项目里没有人管：Git 不拦你，没设身份它会自己拼一个；GitHub 也不拒收，只是不把这样的提交算在你名下。在这门课里，第 1.6 课第 1 站和第 3 站的检查会看 user.name 和 user.email 是不是都设置了；**不遵守的后果**：提交里写进一个自动拼出来的身份：你登录这台 Mac 用的全名（常常是真名），加上“用户名@电脑名.local”；公开后谁都能看到，GitHub 也认不出这是你的提交。
- **为什么**：Git 不会因为没设身份就拒绝提交。建课当天实测，它会用你登录这台 Mac 的全名和“用户名@电脑名.local”拼出一个身份，提交照样成功，只在屏幕上多印一段英文提醒，很容易看漏。写进提交的身份要改，就得另造新提交、改写历史（那段提醒提到的补救命令就是这样做的，阶段 2 才学），所以拍之前就定好；之后再改设置，只管以后的提交（GitHub Docs 同一页：换邮箱之前的提交仍然连着旧邮箱）。
- **正例**：

      git config get user.name     # 应该打印出你愿意公开的名字
      git config get user.email    # 应该打印出你愿意公开的邮箱

- **反例**：从没看过身份设置就开始提交；在提交里用了真实全名和私人邮箱，第 1.13 课公开网站时才发现。
- **怎么检查**：python3 tools/course.py doctor 的「Git 身份」一行要是“user.name 已设置，user.email 已设置”；python3 tools/course.py check 1.6a 和 check 1.6c 也会看。复习题 1.6-r4。
- **例外**：某个仓库要用别的身份（比如公司的项目），在那个仓库里用不带 --global 的 git config set 单独设置一次；这仍然是在提交前确认身份。
- **旧教程提醒**：旧教程（包括《Pro Git》中文版）和 Git 自己打印的提示写的是 git config --global user.name 这种老写法；Git 从 2.46 版（2024 年）起改用 git config get、git config set 这样的子命令，手册把老写法列为过时的写法（git-config 手册 2.56.1 版，2026-11-20 核对）。老写法还能用，这门课只用新写法。
- **学于**：1.6
