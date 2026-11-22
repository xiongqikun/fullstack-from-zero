# GitHub 速查

> 只收第 1.11～1.13 课用到的操作。建课时没有 GitHub 账号，也不在建课的电脑上装软件：网页上的步骤对照 GitHub Docs，`gh` 的命令对照 GitHub CLI 手册（cli.github.com/manual，2026-11-19 打开核对），所以这些步骤都带着标记；终端里的 `which` 和 `git config` 在模拟环境里运行过。网页是英文的，按钮名照原样写。
> 密码、验证码、恢复码、令牌：永远不发给任何人，AI 也一样（ACC-01、REPO-01）。

## 账号和安全（第 1.11 课，网页上做）

| 去哪里 | 做什么 | 小心 |
|---|---|---|
| `https://github.com/signup`〔对照文档，界面可能不同〕 | 注册账号：邮箱、只给 GitHub 用的新密码、用户名（用户名是公开的，用笔名可以） | 密码存进 Passwords App |
| 头像 → **Settings** → **Password and authentication** → **Enable two-factor authentication**〔对照文档，界面可能不同〕 | 用手机上的验证器 App 扫二维码，开启双重验证（ACC-01） | 恢复码下载下来，存进 Passwords App 的 Notes 栏 |
| 头像 → **Settings** → **Emails**〔对照文档，界面可能不同〕 | 勾 **Keep my email addresses private** 和 **Block command line pushes that expose my email**，复制 `数字+你的用户名@users.noreply.github.com`（ACC-02） | 决定继续用自己的邮箱的，把 **Block command line pushes that expose my email** 的勾去掉，不然第 1.12 课的推送会被拒绝（第 1.11 课第 3 站） |

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

## 让电脑认识 GitHub（第 1.11 课，终端里做）

| 命令 | 做什么 | 小心 |
|---|---|---|
| `brew install gh`〔建课时无法验证〕 | 用 Homebrew 装 GitHub CLI（`gh`） | 最后是 `Error:` 开头的话，整段发给导师，别自己搜命令照抄 |
| `which gh` / `gh --version`〔对照文档，界面可能不同〕 | gh 装在哪 / 看 gh 的版本 | |
| `gh auth login`〔对照文档，界面可能不同〕 | 登录：依次选 `GitHub.com`、`Login with a web browser`、`HTTPS`、`Yes`，再到浏览器里填一次性验证码 | |
| `gh auth status`〔对照文档，界面可能不同〕 | 看登录状态，只看不改 | 它有一个把令牌原样显示出来的选项：永远不要用 |
| `git config set --global user.email "数字+你的用户名@users.noreply.github.com"` | 让以后的提交写上隐私地址（Emails 页上复制的那个） | 已经写进旧提交的邮箱改不了 |

## 推送和上线（第 1.12、1.13 课）

| 命令或操作 | 做什么 | 小心 |
|---|---|---|
| `gh repo create my-fullstack-learning --private --source=. --remote=origin --push`〔对照文档，界面可能不同〕 | 在 GitHub 上建私有仓库，把当前文件夹的仓库记成 origin，推上去（1.12） | 先 `pwd`：必须在学习工作区里 |
| `gh repo create my-site --public --source=. --remote=origin --push`〔建课时无法验证〕 | 同上，但是公开的（1.13） | 先 `pwd`：必须在 my-site 里。公开以后别人下载的副本收不回来 |
| `gh browse --settings`〔对照文档，界面可能不同〕 | 在浏览器里打开这个仓库的设置页（1.13） | |
| **Pages** → Source 选 **Deploy from a branch** → **main**、**/ (root)** → **Save**〔对照文档，界面可能不同〕 | 用 GitHub Pages 把网页放到网上；最长约 10 分钟后出现 **Visit site**（1.13） | 看到 404 多半是还没等够，或者没点 Save |

推送之前先查密钥和隐私（REMOTE-02），按第 1.12 课收尾那一组命令做；Git 的命令见 `cheatsheets/git.md`。

## 旧教程提醒

> **旧教程提醒**：以前的教程会说“git push 时终端问 Password，就输入 GitHub 账号密码”；现在这样做会失败，因为 GitHub 自 2021 年 8 月 13 日起不再接受账号密码做 Git 操作。GitHub 文档现在推荐用 GitHub CLI（也就是 `gh auth login`），或者另一个专门保管登录凭据的程序 Git Credential Manager（GitHub Blog 与 GitHub Docs，2026-11-19 核对）。（第 1.11 课）

> **旧教程提醒**：很多旧教程让你新建一个叫 `gh-pages` 的分支来放网页。现在可以直接选 main：GitHub 自 2016-08-17 起允许从主分支发布项目网站（GitHub 博客 “Simpler GitHub Pages publishing”），自 2020-09-03 起允许任何分支（GitHub 更新日志 “Build and deploy GitHub Pages from any branch”）。`gh-pages` 分支今天仍然能用，但这一课用不着它。（第 1.13 课）
