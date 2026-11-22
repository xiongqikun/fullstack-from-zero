# Git 速查

> 只收阶段 1 教过的 Git 命令。2026-11-19 在一个模拟环境里逐条运行过（照建课时核对用的那台 Mac 的设置搭的）：Git 2.54.0（Apple Git-157）· zsh 5.9。
> `<文件>` 这样的尖括号是占位写法：换成你自己的名字，尖括号不要敲。标着 **会丢数据** 的，先按 GIT-04 用 `git status` 和 `git diff <文件>` 看清楚，再动手。

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

## 设置（全局设置，一次管所有仓库）

| 命令 | 做什么 | 哪一课 | 小心 |
|---|---|---|---|
| `git --version` | 看 Git 的版本 | 1.6 | |
| `git config get user.name` | 读一项设置；什么都不打印就是没设置 | 1.6 | |
| `git config set --global user.name "你的名字"` | 改一项全局设置（值里有空格就加半角双引号） | 1.6 | 先 `cp ~/.gitconfig ~/.gitconfig.backup-<日期>` 备份 |
| `git config set --global --all core.editor "code --wait"` | 检查说 core.editor 有好几个值时，把它们合成一个 | 1.6（检查打印的提示） | |
| `git config unset --global <设置名>` | 删掉一项全局设置 | 1.11（想多了解） | |
| `git config list --global` | 一行一项列出全局设置（`~/.gitconfig`）里的每一项 | 1.6（想多了解） | |

## 拍快照、看改动

| 命令 | 做什么 | 哪一课 | 小心 |
|---|---|---|---|
| `git init` | 把当前文件夹变成仓库（在项目根目录里运行） | 1.6 | 先 `pwd`，别建在 `~` 或 `~/Developer` |
| `git status` | 看三块区域里各有什么；不知道下一步就先敲它 | 1.6 | |
| `git add <文件>` / `git add .` | 把改动放进暂存区 / 放进这里所有的改动 | 1.6 / 1.12 | `git add .` 之前先看 `git status` |
| `git commit -m "说明"` | 拍一张快照，写一句提交说明 | 1.6 | |
| `git commit -m "feat: 描述" -m "正文"` | 第一行按约定式提交写，第二个 `-m` 是正文 | 1.10 | |
| `git log --oneline` / `git log -1` | 每个提交一行 / 只看最新一个 | 1.6 / 1.11 | |
| `git log --stat` / `git log --format='%h %an <%ae>'` | 每个提交改了哪些文件 / 看作者和邮箱 | 1.7 / 1.11 | |
| `git diff` / `git diff <文件>` | 还没放进暂存区的改动 | 1.7 | |
| `git diff --staged` / `git diff --stat` | 已经放进暂存区的改动 / 只看改了哪些文件、各几行 | 1.7 / 1.15 | |
| `git show <编号>` / `git show --stat` | 看一个提交改了什么 / 只看文件清单 | 1.7 / 1.10 | |
| 屏幕最下面只有 `:` 或 `(END)` | 进了分页器 less：空格翻页，按 q 退出 | 1.7 | |

## 后悔药和不拍名单

| 命令 | 做什么 | 哪一课 | 小心 |
|---|---|---|---|
| `git restore <文件>` | 用暂存区里的版本盖掉工作区里的这个文件（没 `git add` 过改动时，就是上次提交的版本） | 1.8 | **会丢数据**：没提交的改动找不回来 |
| `git restore --staged <文件>` | 把改动从暂存区拿下来，文件本身不动 | 1.8 | |
| `git status --ignored` / `git check-ignore -v <文件>` | 连被忽略的文件一起列 / 这个文件被哪一行规则挡住了 | 1.9 | |
| `git ls-files` | 列出 Git 正在跟踪的文件 | 1.9 | |
| `git rm --cached <文件>` / `git rm -r --cached <文件夹>` | 让 Git 不再跟踪它，文件留在你电脑上 | 1.9 | 历史里还有它：密钥要先作废（REPO-01） |
| `git <命令> -h` | 这条命令的简短用法 | 1.14 | |

## 远程仓库（第 1.12 课）

推送之前先找密钥和隐私（第 1.12 课收尾那一组命令里的一步）；有结果就先停下：

```zsh
git grep --untracked -n -i -E "password|token|secret|key|密码|密钥|令牌" -- notes journal learner
```

| 命令 | 做什么 | 小心 |
|---|---|---|
| `git remote -v` / `git push` | 看远程仓库的地址 / 把本地的提交推上去 | 推上去以后，别处就有了一份 |
| `git clone <网址> <文件夹>` | 把远程仓库复制一份到本地，用来试恢复 | |

## 旧教程提醒

> **旧教程提醒**：教程、很多官方页面（包括 GitHub Docs）和 Git 自己打印的提示里，还常见老写法 `git config --global user.name "小林"`。Git 从 2.46 版（2024 年）起改用 `get`、`set` 这样的子命令，手册把老写法列为过时的写法（git-config 手册 2.56.1 版、Git 2.46.0 的发布说明，2026-11-20 核对）。老写法照样能用；这门课只用新写法。（第 1.6 课）

> **旧教程提醒**：以前的教程（包括《Pro Git》中文版）里，`git init` 之后第一个分支叫 `master`；现在新仓库用 `main`（GitHub 自 2020 年 10 月起默认 `main`，Git 计划在 3.0 改成 `main`）。旧名字还能用，只是不再是惯例。（第 1.6 课）

> **旧教程提醒**：以前丢弃修改写 `git checkout -- 文件名`，取消暂存写 `git reset HEAD 文件名`；现在 Git 在 `git status` 里提示的是 `git restore 文件名` 和 `git restore --staged 文件名`（自 Git 2.23 起，2019 年）。旧写法今天还能用。（第 1.8 课）
