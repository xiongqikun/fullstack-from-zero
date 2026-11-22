# 环境基线：建课时核对课文用的电脑

> **记录日期**：2026-11-19 ｜ **来源**：建课计划 G7（`docs/plans/2026-11-19-batch-1-plan.md` 第 1 节）｜ **不记录**：姓名、用户名、邮箱、电脑名

这一页记的是建课时核对课文用的那台 Mac（装了下表这些软件）在 2026-11-19 那天是什么样子。课文里的每条命令和每段“你应该看到”，都是照着它写、照着它验证的。你的电脑不一定有这些，缺什么 `doctor` 会指出来。你的电脑和它不一样的地方，用下面「怎么刷新」的办法查。电脑上的软件升级之后，这一页会变旧。

**怎么得到的。** 2026-11-19，在那台电脑的终端（terminal，用打字而不是点鼠标来指挥电脑的窗口）里运行只读（read-only）命令得到。只读的意思是只查看，不修改任何东西。写这一页时，又在建课用的环境里用只读命令复核了一遍：有两项只能在那台电脑的终端窗口里看到，没法复核；其余都对得上。`python` 命令一项起初记录不一致，建课计划已按复核结果改正。Git 的全局设置不记具体的值。

**怎么刷新。** 在终端里运行 `python3 tools/course.py doctor`。它只读不写，给你的电脑做一次体检，结果分成三组：没问题、需要处理、仅提示。再运行 `python3 tools/course.py fresh`。它把你电脑上现在的软件版本和课程核实时的版本（存在 `tools/courselib/baseline.json` 里）比一遍，列出需要重新核实的课。结果和下表对不上时，把屏幕上的内容发给导师，说“课文对不上”；导师会核实、更新这一页，并记入 `CHANGELOG.md`。

## 技术清单（现在看不懂没关系）

### 建课用的电脑在 2026-11-19 的状况

| 项目 | 状况 | 对课程意味着什么 |
|---|---|---|
| 系统 | macOS 27.2.1，Apple 芯片 | 课文按 macOS 27 写 |
| 界面语言 | 课程不假设（可能是中文，也可能是英文） | 界面上的字，课文引用英文原文，后面配中文 |
| Shell | zsh 5.9；默认提示符是 `你的用户名@你的电脑名 当前文件夹 %`；`LANG=C.UTF-8` | 示例提示符写作 `你的用户名@你的电脑名 fullstack-from-zero %` |
| 学习用的终端 | Claude 桌面应用的 Terminal 面板（`TERM_PROGRAM=claude-desktop`），是一个普通的登录 zsh | Terminal.app、VS Code 内置终端这类终端是同一个 shell 开在别的窗口里 |
| 编辑器和分页器 | `EDITOR` 和 `PAGER` 都没有设置 | Git 要你写字时打开的是 vi，长输出用 less 分页 |
| Python | `python3` 是 3.14.9（uv 管理，PATH 上最先找到）；`/usr/bin/python3` 是 3.9.6；没有 `pip` | 课程统一敲 `python3`；学习工具兼容 3.9～3.14（决策记录 0007） |
| `python` 命令 | 有，是 uv 管理的一个链接，和 `python3` 是同一个 3.14.9（建课计划 G7） | 很多 Mac 上没有 `python`，所以课文一律写 `python3` |
| Git | 2.54.0（Apple Git-157）；新仓库的默认分支叫 `main`，这来自 Xcode 自带的系统配置，全局并没有设 `init.defaultBranch` | `git init` 在这台电脑上直接得到 `main`；换一台电脑不一定 |
| Git 全局设置 | 因电脑而异，这里不记具体的值。课程按一种常见的坏情况准备：提交签名打开了（`commit.gpgsign=true`、`gpg.format=openpgp`），却没有安装 gpg；`gpg.ssh.program` 和 `gpg.ssh.allowedSignersFile` 这两项设置存在，但值是空的 | 遇到这种情况，每一次 `git commit` 都会失败（`error: cannot run gpg: No such file or directory`）；第 1.6 课处理。`gpg.ssh.program` 是空的，改用 SSH 签名时，提交也会失败（`error: cannot run : No such file or directory`），要先删掉这一项或者改成 `ssh-keygen`；验证签名还要一个真实的 allowed signers 文件；第 1.11 课处理。`python3 tools/course.py doctor` 会指出这两种情况 |
| 全局忽略文件 | 因电脑而异；有的电脑在全局忽略文件（比如 `~/.gitignore_global`）里已经忽略了 `.DS_Store`、`*.log` 这类文件 | 演示“忽略文件”时要用不常被全局忽略的文件 |
| 已安装 | uv 0.13.5、ruff 0.17.2、Node 26.12.0 和 npm 11.20.0（经 nvm）、Homebrew 7.0.10（在 `/opt/homebrew`）、VS Code 1.145.2（带 `code` 命令）、sqlite3 3.54 | 阶段 0～1 不用再装别的，除了第 1.11 课的 `gh` |
| GitHub CLI（`gh`） | 没有安装（第 1.11 课用 Homebrew 装）。课程记下的版本是 2.105.0：2026-11-19 从官方发布页 https://github.com/cli/cli/releases/latest 读到（「GitHub CLI 2.105.0」，标签 v2.105.0，2026-11-18 发布），不是从装好的 `gh` 读的 | `fresh` 在第 1.11 课做完之前显示「还没安装（第 1.11 课会装）」，`doctor` 显示「还没安装。第 1.11 课会带你装」；下次在装了 `gh` 的电脑上核对第 1.11 课时，用 `gh --version` 重新读一遍 |
| 没有安装 | `gh`、`gpg`、`pnpm`、`psql`、`tree` | 课文不能假设它们存在 |
| 文件夹 | 很多 Mac 的桌面和文稿由 iCloud 同步；`~/Developer` 常常还不存在 | 第 0.2 课；决策记录 0004 |

没法在建课环境里复核的两项：学习用终端的 `TERM_PROGRAM`，以及 Git 在那台电脑上实际打开哪个编辑器。原因见下面的第 2 条差别。

### 你的终端和建课沙箱的差别

验证课文的 AI 不在你的终端里干活。它在一个受限制的沙箱（隔离出来的运行环境）里，用一个模仿上表的临时主目录。所以“在沙箱里通过”不等于“在你那里通过”。要紧的差别是这五条：

- **主目录是模拟的。** 验证只在 `tools/dev/make_sim_home.py` 生成的临时主目录里进行，不碰你真正的 `~`、`~/.gitconfig`、`~/.zshrc` 和 `~/Developer`。模拟主目录里的身份是 `Learner` 和 `learner@example.com`，签名设置照上表那种常见的坏情况：签名打开，没有 gpg，`gpg.ssh.program` 和 `gpg.ssh.allowedSignersFile` 存在但是空的。要模拟第 0.2 课选了“先留在原处”的学习者，加 `--stay`：学习工作区放在 `~/Desktop/Code/fullstack-from-zero`，`~/Developer/fullstack-from-zero` 是指向它的入口（符号链接）。
- **沙箱不是交互式终端。** 那里 `tty` 报告 `not a tty`，`TERM` 和 `LANG` 是空的，还被注入了 `GIT_EDITOR=true`：`git var GIT_EDITOR` 在沙箱里输出 `true`，在你那里是 `vi`。所以 AI 不会被困在 vi 或 less 里，而你会。会打开编辑器或分页器的步骤，要按你的环境来写。
- **沙箱里的输出不能直接抄进课文。** 那里的 `grep` 和 `find` 是包装过的函数（`grep --version` 显示 ugrep），报错前缀是 `(eval):cd:1:` 这种样子。在模拟主目录里，`/usr/bin/git` 和 `/usr/bin/python3` 每次还会多打印一行 `error: couldn't create cache file …`。课文里的“你应该看到”要取自干净的 zsh。
- **沙箱禁止的事。** 不能监听端口，不能用 `open` 打开应用或网页，`code` 命令运行不了，联网要逐个域名放行。VS Code、GitHub 网站、Claude 应用里点鼠标的步骤没有人替你点过，课文里标着〔对照文档，界面可能不同〕。
- **沙箱专用的绕行办法。** 测 Python 3.9 用 `/Library/Developer/CommandLineTools/usr/bin/python3`；用 uv 之前先 `export UV_CACHE_DIR="$TMPDIR/uv-cache"`。凡是你用不着的绕行办法（环境变量、参数、替代路径），验证的人都要上报，不许写进课文。
