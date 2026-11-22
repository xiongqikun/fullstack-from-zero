# 1.12 第一次推送和云端备份

> **用时** 3 站，约 145 分钟 ｜ **前置** 1.11 ｜ **核实** 2026-11-20 · git 2.54.0 · macOS 27.2.1 · zsh 5.9 · gh 2.105.0（gh 的步骤按官方手册和源代码）
> **学完你能** 把整个学习工作区变成一个 Git 仓库，第一次提交之前先查有没有密钥；把它推送到 GitHub 上你自己的私有仓库；从 GitHub 克隆一份出来，确认这份备份真的能用。
> **本课行规** REMOTE-01、REMOTE-02（见文末）

## 先想一想

你手机里的照片，只存在手机里。手机掉进水里，会怎样？

再想一步：你开了云相册，说是“已备份”。你怎么知道，换一台新手机登录以后，那些照片真的都能打开？

想好了先放着，第 3 站开头对答案。

## 第 1 站：学习仓库入库（约 40 分钟）

### 概念

你的笔记、日志和学习记录现在只在这台电脑上。这一站把整个学习工作区收进 Git。收进以后它也是一个仓库，课文叫它**学习仓库**：还是同一个 `fullstack-from-zero` 文件夹，里面早就有两百多个文件。

一句话：**一个早就有很多文件的文件夹，收进仓库之前先看清：哪些被挡在外面，要收的是哪些，内容里有没有密钥。** 提交过的东西会一直留在历史里，下一站还要推到 GitHub，所以这一步在第一次提交之前做。

### 跟我做

#### 1. 先体检

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py doctor
```

报告很长，只看两处。第一处：「学习工作区的位置」那一行在哪一段。搬过家的，它在「✅ 没问题」下面：

```text
  - 学习工作区的位置：~/Developer/fullstack-from-zero，不在同步到云端的文件夹里。
```

它在「⚠️ 需要处理」下面，就是学习工作区还在同步盘里。第 0.2 课说好在这里再问一次：仓库放在同步盘里会被弄坏（WS-01）。

- **现在搬（推荐）**：对导师说“帮我把课程安置到 ~/Developer”。搬好以后在新位置重新打开 Claude（README 的卡片「搬家后怎么找回导师」），从这一步重来。
- **留在原处**：下一站推到 GitHub 的那一份是你的备份。接着做，检查 1.12a 会把决定记下来。
- **拿不准**：对导师说“急救：学习工作区还在同步盘里”。

第二处：「⚠️ 需要处理」下面有没有“提交签名”那一行。有，等一下的提交会失败：把这一行发给导师，说“急救：提交签名”。

#### 2. 建仓库

先说出执行后图会怎么变（1.6 课的四个区域）：`git init` 只是在这里放一本空相册（隐藏的 `.git` 文件夹），不移动任何文件，暂存区、本地历史和远程都还是空的。

```zsh
git init
```

你应该看到（路径最后一段要是 `fullstack-from-zero`）：

```text
Initialized empty Git repository in /Users/你的用户名/Developer/fullstack-from-zero/.git/
```

> 读懂这句：在 ……/fullstack-from-zero/.git/ 建好了一个空的 Git 仓库（再运行一次会说 `Reinitialized existing…`，不要紧）。

#### 3. 故意出错：现在看历史

先猜：空相册里看历史，`git log` 会说什么？

```zsh
git log
```

你应该看到：

```text
fatal: your current branch 'main' does not have any commits yet
```

> 读懂这句：致命错误：你当前的分支 main 还一个提交都没有（分支是一条历史线的名字，1.6 课讲过）。

报错三问：谁在报错？Git（`fatal:`）。关键词？`does not have any commits yet`。我刚才敲了什么？在空仓库里看历史。不是坏了，是还没拍第一张。

#### 4. 读状态，连被挡住的一起看

1.9 课学过 `git status --ignored`。先猜：这么多文件，它会逐个列出来吗？

```zsh
git status --ignored
```

你应该看到（你的列表可能多几项或少几项，以你屏幕上的为准）：

```text
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.editorconfig
	.gitignore
	CHANGELOG.md
	CLAUDE.md
	GLOSSARY.md
	LICENSE
	LICENSE-CC-BY-4.0.txt
	LICENSE-MIT-0.txt
	PROGRESS.md
	README.md
	ROADMAP.md
	STANDARDS.md
	cheatsheets/
	docs/
	gates/
	handbook/
	journal/
	learner/
	notes/
	stages/
	starter/
	templates/
	tools/

Ignored files:
  (use "git add -f <file>..." to include in what will be committed)
	learner/last-result.json

nothing added to commit but untracked files present (use "git add" to track)
```

> 读懂这句：还没有提交；Untracked files 是未跟踪的文件，Ignored files 是被忽略的（`git add -f` 是强行收进去，不要用）；最后一行说暂存区是空的。

全是新文件的文件夹，Git 只列名字（`docs/`）。上半段是课程材料和你的记录，下半段是 `.gitignore` 挡住的（全文见这一站末尾的框）。

#### 5. 搜一搜内容

`git status` 不看文件里写了什么。收进去之前，用 `git grep` 在内容里搜像密钥、密码、令牌的词（和 1.3 课的 `grep` 一样）：

```zsh
git grep --untracked -n -i -E "password|token|secret|key|密码|密钥|令牌" -- notes journal learner
```

- `--untracked`：没跟踪的文件也搜（`.gitignore` 挡住的不搜）。现在一个文件都还没跟踪，不加它什么也搜不到。
- `-n` 行号，`-i` 不分大小写（1.3 课）；`-E` 让 `|` 表示“或”。**英文半角引号不能少**（中文输入法的 “ ” 不算），不然 zsh 报 `command not found`。
- `--` 后面是只搜的文件夹：你自己写的东西只在这三个里，课程材料里到处是这些词。**别的仓库没有这三个文件夹**：去掉 `--` 和后面的名字，搜整个仓库。
- 输出很长时进入分页器，按 q 退出。

你应该看到类似（你的会不一样；什么都没打印，就是一行也没搜到）：

```text
notes/my-rules.md:65:### REPO-01 密钥、密码、令牌永不入库
notes/my-rules.md:67:密钥、密码、令牌永远不进仓库。泄露了先作废。
notes/my-rules.md:87:### REMOTE-02 推送或公开之前，先查有没有密钥和隐私
```

逐行读：这是行规笔记，只是提到“密钥”这个词，放行。搜到一串看不懂的字母数字（真的密钥或令牌）：先作废（让它失效、换一个新的），再从文件里拿掉。再想一想：有没有别人的个人信息（手机号、住址、真名）？有，先改掉。

#### 6. 一次收进去，拍第一张

看过了状态和内容，`git add .` 才是放心的（`.` 是当前文件夹，0.2 课讲过）。先说出图会怎么变：全部文件从工作区进到暂存区。

```zsh
git add .
```

这条命令成功时什么也不打印。

提交说明用约定式提交（1.10 课），收材料的类型是 `chore`（杂务）；第二个 `-m` 是正文，如实写材料是谁写的。

```zsh
git commit -m "chore: 导入课程材料" -m "课程材料由 Claude（AI）生成，notes、journal、learner 里是我自己的记录。"
```

引号、冒号用英文半角。终端停在 `dquote>` 上不动，是引号没配对：按 Ctrl+C，重敲。

你应该看到开头这几行（编号和数字你的会不一样），后面每个新文件一行，滚过去就好：

```text
[main (root-commit) f82b092] chore: 导入课程材料
 267 files changed, 77404 insertions(+)
 create mode 100644 .editorconfig
 create mode 100644 .gitignore
 create mode 100644 CHANGELOG.md
```

> 读懂这句：在 main 上做了根提交（第一个提交），编号 f82b092；267 个文件，新增 77404 行；每个 `create mode` 是一个新文件（`100644` 是普通文件的记号）。

#### 7. 看结果

```zsh
git status
```

你应该看到：

```text
On branch main
nothing to commit, working tree clean
```

> 读懂这句：没有要提交的东西，工作区是干净的。

### 补全

把顺序补完整，写在纸上或心里：

1. 确认位置：`python3 tools/course.py ____`
2. 建仓库：`git ____`
3. 读状态，连被挡住的一起看：`git status ____`
4. 连没跟踪的文件一起搜内容：`git grep ____ -n -i -E "password|token|secret|key|密码|密钥|令牌" -- notes journal learner`
5. 全部放进暂存区：`git add ____`

### 自己做

先搭练习场景：

```zsh
python3 tools/course.py scenario 1.12a
```

它会给你一个菜谱文件夹和一条 `cd` 命令：照它进到**菜谱文件夹本身**（比如 `recipes-amber`），不是上一层的 `1.12a`。里面有几道菜谱和一份 `.gitignore`，还不是仓库。

目标：

- 把菜谱文件夹变成仓库，第一次提交就收进所有该收的文件；它自己的 `.gitignore` 挡住的东西不能进。
- 提交说明用约定式提交格式。
- 做完以后这个仓库的 `git status` 是干净的。

回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.12a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.12a`

> **存档点 1.12a**：到这里可以安全停下。下次可以对导师说“从 1.12b 继续”。

> **想多了解（可跳过）：`.gitignore` 全文**
>
> 想看学习工作区的忽略规则本身，在学习工作区运行 `cat .gitignore`，会看到：
>
> ```text
> # 这个文件告诉 Git：下面这些东西不要收进仓库。
> # 每一行是一条规则，以 # 开头的行是给人看的说明。1.9 课讲过怎么写。
>
> # macOS 自动生成的杂物
> .DS_Store
> ._*
>
> # Python 运行时自动生成的缓存：删了还会再生成，不属于源文件
> __pycache__/
> *.pyc
> .ruff_cache/
>
> # 学习工具每次运行都会重写的“上一次结果”：给导师看的，不是你的进度
> learner/last-result.json
> # 学习工具写文件写到一半时的临时文件：正常会自动删掉，只有电脑突然死机或断电时才会留下
> learner/.*.tmp
>
> # 只和这台电脑有关的调研记录，不外传
> docs/research/local-only/
>
> # Claude 桌面应用留在本机的文件
> .claude/settings.local.json
> .claude/.cc-writes/
>
> # 密钥、密码、令牌：永远不入库（行规 REPO-01）
> .env
> ```
>
> 共同点：换一台电脑恢复时不需要，或者根本不该离开这台电脑。`notes/`、`journal/`、`learner/` 里的其他文件没有被挡住：它们是你的学习记录，正是要备份的。

## 第 2 站：推送到私有仓库（约 40 分钟）

### 概念

**远程仓库**（remote）：放在别处的另一份仓库。像存在别处的另一本相册：你家里那本丢了，别处那本还在。

这个类比在哪里不成立：两本相册不会自己同步。你在本机提交以后，远程那份还是旧的，要你运行 `git push`（推送）把新提交传过去才会更新。反过来，把远程的新提交取回本机叫拉取（pull），阶段 2 再学。

Git 图的最后一个区域，今天开始用：

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

你的远程仓库放在 GitHub 上，设成**私有仓库**（private repository）：只有你和你明确邀请的人能看到。私有不等于“放什么都行”：它在别人的服务器上，以后也可能被改成公开。

### 跟我做

#### 1. 建私有仓库并推送

这次推出去的是第 1 站的那个提交，提交之前已经看过状态、搜过内容。以后每次推送前都要再看再搜，收尾里有完整的一组。

`gh` 是 GitHub 的命令行工具（GitHub CLI）。1.11 课你用它登录过，登录时选的是 HTTPS（1.11 课讲过的一种连接方式，地址以 `https://` 开头），gh 会替 Git 证明你的身份。这一条命令做三件事：在 GitHub 上建一个仓库、把它记成这里的远程仓库、把提交推上去。

| 部分 | 意思 |
|---|---|
| `gh repo create my-fullstack-learning` | 在 GitHub 上新建一个叫 `my-fullstack-learning` 的仓库：小写英文加短横线（0.2 课 WS-02）。名字故意和课程的公开仓库 `fullstack-from-zero` 不一样：这一个装的是你自己的学习记录 |
| `--private` | 私有。**这一个词决定谁能看到，敲之前再看一眼** |
| `--source=.` | 用当前文件夹这个已有的仓库 |
| `--remote=origin` | 在本机把这个远程仓库叫作 `origin` |
| `--push` | 建好以后把本地的提交推上去 |

```zsh
cd ~/Developer/fullstack-from-zero
gh repo create my-fullstack-learning --private --source=. --remote=origin --push
```

〔对照文档，界面可能不同〕按 gh 的官方手册和源代码，成功时屏幕上会有这几行（中间还会夹着几行 Git 推送的输出）：

```text
✓ Created repository 你的用户名/my-fullstack-learning on github.com
  https://github.com/你的用户名/my-fullstack-learning
✓ Added remote https://github.com/你的用户名/my-fullstack-learning.git
✓ Pushed commits to https://github.com/你的用户名/my-fullstack-learning.git
```

> 读懂这句：在 github.com 上建好了仓库；加好了远程仓库；提交推上去了。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

推送时 gh 还把本地的 `main` 和 GitHub 上的 `main` 对上了，这叫设置**上游**（upstream）。以后在这个仓库里，直接 `git push` 就知道往哪推。

推送报了 `GH007`，照这一站末尾的框「推送被 GH007 拦下」做。报了别的错：用报错三问读一遍，不要换个名字反复试，把整段发给导师。

#### 2. 看远程和状态

先猜：现在 `git status` 的第二行会多出一句什么？

```zsh
git remote -v
git status
```

〔对照文档，界面可能不同〕你应该看到（地址的写法按 gh 的源代码，用户名是你的）：

```text
origin	https://github.com/你的用户名/my-fullstack-learning.git (fetch)
origin	https://github.com/你的用户名/my-fullstack-learning.git (push)
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   learner/log.jsonl
	modified:   learner/state.json

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：远程仓库 origin，取（fetch）和推送（push）都用这个地址。你的分支和 origin/main 一样新；有两个文件改了，还没暂存。

`-v` 是 verbose（详细）：加了才打印地址。`origin` 是远程仓库的惯用名字（Pro Git 2.5 节）；`origin/main` 是 Git 在本机记下的“GitHub 那边的 main 上次是什么样”。

你每运行一次检查或提示，学习工具都会更新 `learner/` 里这两个进度文件。推送只送走已经提交的东西，这两个改动没有跟着出去，收尾时再提交。

#### 3. 故意出错：照旧教程推送

很多旧教程写的推送命令是 `git push origin master`。先猜它在这里会怎样：

```zsh
git push origin master
```

你应该看到：

```text
error: src refspec master does not match any
error: failed to push some refs to 'https://github.com/你的用户名/my-fullstack-learning.git'
```

> 读懂这句：错误：要推送的 master 对不上任何东西；推送到那个地址失败了（refspec、refs 是 Git 说“哪个分支推到哪里”的写法）。

报错三问：谁在报错？Git（`error:`）。关键词？`master does not match any`，这里没有叫 master 的分支。我刚才敲了什么？照旧教程写了 `master`，你的分支叫 `main`。什么也没推出去。以后每次学完，提交以后运行 `git push` 就行；没有新提交时运行它，会看到 `Everything up-to-date`（全都是最新的）。

### 补全

推送这一段，把空填上：

1. 建私有仓库并推送：`gh repo create my-fullstack-learning ____ --source=. --remote=origin --push`
2. 看远程仓库的地址：`git remote ____`
3. 以后推送新提交：`git ____`
4. 推完再看：`git status` 第二行应该是 `Your branch is ____ with 'origin/main'.`

### 自己做

先搭练习场景：

```zsh
python3 tools/course.py scenario 1.12b
```

里面有一个已经推送过一次的练习仓库（比如 `trip-amber`），和它的远程仓库 `remote/trip-….git`。这个远程仓库是本机上的一个文件夹，在练习里代替 GitHub，不联网，也不碰你的 GitHub 账号。照场景给的 `cd` 命令进到**练习仓库本身**（`trip-…` 里面）。

练习仓库里有今天新写的内容，还没提交。目标：

- 提交之前先做第 1 站那样的检查；任何像密钥的东西都不能离开这台电脑。这个仓库里没有 `notes journal learner` 这三个文件夹：搜的时候去掉 `--` 和后面的文件夹名，搜整个仓库。
- 其他新内容（行程里新加的一天、新文件）都要提交并推送到它的远程仓库。
- 做完以后，练习仓库的 `git status` 要说 `Your branch is up to date with 'origin/main'.`，并且工作区是干净的。

要改文件，在练习仓库里运行 `code .`（1.4 课 ED-01），在左边点开要改的文件，改完按 ⌘S 保存。**保存以后、`git add` 之前，再搜一次**，确认那串东西真的不见了。

回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.12b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.12b`

> **存档点 1.12b**：到这里可以安全停下。下次可以对导师说“从 1.12c 继续”。

> **想多了解（可跳过）：旧教程和亲眼确认私有**
>
> - **旧教程提醒**：以前新仓库的第一个分支叫 `master`，教程写 `git push origin master`；现在 GitHub 新建仓库默认是 `main`（自 2020-10-01 起），建课时核对用的 Mac 上，`git init` 也给 `main`（原因见第 1.6 课「把 main 写进自己的设置」）。（GitHub Changelog 2020-10-01；建课时实测，2026-11-20）
> - **旧教程提醒**：以前推送时终端会要你输入 GitHub 的账号密码；现在 GitHub 不再接受账号密码做 Git 操作（自 2021-08-13 起），改用令牌、SSH（另一种连接方式，1.11 课提过）或 GitHub CLI。你用 gh 登录过，不会问你密码。（GitHub 博客“Token authentication requirements for Git operations”，2020-12-15 发布，2026-11-19 核对）
> - 亲眼确认 GitHub 上的仓库是私有的：在学习工作区运行 `gh repo view --json visibility`（`--json` 让 gh 用程序好读的格式打印）。〔对照文档，界面可能不同〕应该看到 `"visibility": "PRIVATE"`。如果是 `PUBLIC`，先停下，对导师说“急救：学习仓库成了公开的”。

> **想多了解（可跳过）：推送被 GH007 拦下**
>
> 没遇到就跳过。〔建课时无法验证〕第一次推送时报了这一行：
>
> ```text
> remote: error: GH007: Your push would publish a private email address.
> ```
>
> 读懂这句：远程（GitHub）报错：GH007，这次推送会公开一个你设成不公开的邮箱。
>
> 这是 1.11 课勾的“拦下来”在起作用：最新的提交用的是你账号里不公开的邮箱（你在 1.11 课选了继续用自己的邮箱，又没去掉那个勾）。仓库已经建好，只是提交没推上去。不要改写历史，两个办法选一个：
>
> - **照 1.11 课的决定**：回到 GitHub 的 Emails 页，把 **Block command line pushes that expose my email** 的勾去掉〔对照文档，界面可能不同〕，再运行 `git push --set-upstream origin main`，不用新提交。
> - **改用隐私地址**：照 1.11 课第 6 步运行 `git config set --global user.email "你的隐私地址"`，再做一个新提交（`git add .`，然后 `git commit -m "chore: 记录学习进度"`），最后 `git push --set-upstream origin main`。
>
> 两种办法里的 `--set-upstream` 都是 gh 本来替你做的设上游。

## 第 3 站：验证备份真的能用（约 40 分钟）

### 概念

对一下开头的答案：只在手机里的照片，手机一坏就没了。云相册说“已备份”，你也只有真的在另一台手机上打开过，才知道它是完整的。

工程里常说：**没恢复过的备份只是愿望**（美国网络安全和基础设施安全局（CISA）的《勒索软件防范指南》（#StopRansomware Guide）2023 年 9 月版也要求定期测试备份）。备份可能早就停了、只备了一半，或者取不出来。验证的办法只有一个：真的恢复一次，叫**恢复测试**（restore test）。

对 Git 仓库，恢复就是**克隆**（clone）：从远程仓库复制一份完整的仓库到本机，连同全部历史。这一站把你 GitHub 上的那一份克隆到练习场，和原来的比一比，再删掉。

### 跟我做

#### 1. 克隆到练习场

克隆要用 GitHub 上仓库的地址。不要自己拼，从 `git remote -v` 里复制：

```zsh
cd ~/Developer/fullstack-from-zero
git remote -v
```

选中 `origin` 后面那个 `https://github.com/……/my-fullstack-learning.git`（只要地址，不要后面的 `(fetch)`），按 ⌘C 复制（⌘ 是 ⌘S 里那个 command 键）。然后到 `~/Developer`（这样后面比较时路径短），敲 `git clone `（后面有一个空格），按 ⌘V 粘贴地址，再敲一个空格和 `playground/restore-test`：

```zsh
cd ~/Developer
git clone https://github.com/你的用户名/my-fullstack-learning.git playground/restore-test
```

代码块里的 `你的用户名` 只是占位，你粘贴进来的是你自己的。最后一项是放到哪里：练习场里一个新文件夹 `restore-test`。名字里不能有空格：多一个空格，Git 会当成两样东西，报 `fatal: Too many arguments.`，后面跟一大段英文用法说明。名字用短横线，重敲一遍。

你应该看到第一行是（〔建课时无法验证〕从 GitHub 克隆时，后面还有几行 `remote: Enumerating objects…`、`Receiving objects: 100%…` 这样的传输进度，最后一行以 `done.` 结尾，数字你的会不一样）：

```text
Cloning into 'playground/restore-test'...
```

> 读懂这句：正在克隆到 playground/restore-test……

〔建课时无法验证〕终端要是问 `Username for 'https://github.com':`（多半是 Git 没拿到 gh 存好的登录），什么也不要输入，按 Ctrl+C，对导师说“急救：git 要我输入 GitHub 用户名”。

#### 2. 比较最新的提交

先猜：两边最新提交的编号会一样吗？

```zsh
cd playground/restore-test
git log --oneline -1
cd ~/Developer/fullstack-from-zero
git log --oneline -1
```

`git log` 从最新的往下排，`-1` 表示只看最上面、最新的一个。你应该看到（编号你的会不一样，但两边要相同）：

```text
f82b092 chore: 导入课程材料
f82b092 chore: 导入课程材料
```

编号一样，说明 GitHub 上那份的历史和你本机的一样新。

#### 3. 比较文件

`diff` 是 difference（差别）。`-r` 一层层往文件夹里比，`-q` 只说哪些不一样、不列具体内容，`-x .git` 跳过两边的 `.git` 相册本身：

```zsh
cd ~/Developer
diff -r -q -x .git fullstack-from-zero playground/restore-test
```

你应该看到类似（你的会不一样）：

```text
Only in fullstack-from-zero: .claude
Only in fullstack-from-zero/learner: last-result.json
Files fullstack-from-zero/learner/log.jsonl and playground/restore-test/learner/log.jsonl differ
Files fullstack-from-zero/learner/state.json and playground/restore-test/learner/state.json differ
```

> 读懂这句：Only in fullstack-from-zero = 只有 fullstack-from-zero 里有；Files … differ = 两边这个文件内容不同。

逐行对：

- `Only in fullstack-from-zero` 的每一项，要么能在 `.gitignore` 里找到挡住它的那一行，要么是空文件夹（Git 只记文件，空文件夹不进仓库）。都不是的，问导师。
- `differ` 的两个，是推送以后才改的进度文件，还没提交。

除此之外没有别的不同，说明**提交过的东西都在备份里**。反过来也是一条教训：没提交、没推送的东西，备份里没有。

#### 4. 故意出错：再克隆一次

先猜：同样的命令再运行一遍，会怎样？按 ↑ 键可以把刚才的命令翻出来，翻到那条 `git clone` 按回车：

```zsh
git clone https://github.com/你的用户名/my-fullstack-learning.git playground/restore-test
```

你应该看到：

```text
fatal: destination path 'playground/restore-test' already exists and is not an empty directory.
```

> 读懂这句：致命错误：目标路径 playground/restore-test 已经存在，而且不是空文件夹。

报错三问：谁在报错？Git（`fatal:`）。关键词？`already exists`，已经存在。我刚才敲了什么？往一个已经有东西的文件夹里克隆。Git 不会覆盖已有的文件夹，这是在保护你。

#### 5. 删掉副本

比较完了，副本没用了。删除前先看清要删什么（1.2 课 TERM-02）：

```zsh
ls playground
```

你应该看到 `restore-test` 和练习场景的文件夹（你的会不一样）：

```text
1.12a  1.12b  restore-test
```

Git 把仓库里存数据的文件设成了只读。只用 `rm -r` 的话，终端会对每个只读文件问一遍要不要删（macOS 的 `rm` 手册这么写）。所以这里加 `-f`（force，强制，不再逐个问）。正因为它不再问，**敲回车之前再看一遍路径**：只删 `playground/restore-test`。

```zsh
rm -rf playground/restore-test
ls playground
```

`rm -rf` 成功时什么也不打印。你应该看到 `restore-test` 不见了：

```text
1.12a  1.12b
```

### 补全

恢复测试的四步，把空填上：

1. 克隆到练习场：`git ____ <远程地址> playground/restore-test`
2. 两边各看最新一个提交：`git log --oneline ____`
3. 比较文件，跳过 `.git`：`diff -r -q -x ____ fullstack-from-zero playground/restore-test`
4. 看清以后删掉副本：`rm ____ playground/restore-test`

### 自己做

先搭练习场景：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.12c
```

故事：一个相册项目（比如 `album-amber`）原来的文件夹已经没了，只剩它的远程仓库 `remote/album-….git`（在练习里代替 GitHub）。

目标：

- 把项目恢复到场景说的位置，恢复出来的历史要和远程仓库的一样。
- 在恢复出来的仓库里看提交历史，找到最早的那个提交。检查时会问你它的说明。
- 学习工作区的备份也要是最新的：学习仓库里所有提交都已经推送。检查器不联网，它比的是你上一次推送时本机记下的 `origin/main`。

回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.12c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.12c`

> **存档点 1.12c**：到这里可以安全停下。下次可以对导师说“从 1.12 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| REMOTE-01 | 重要仓库在别处有第二份，并且试过能恢复 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 惯例·平台与工具 | 《Pro Git》第 2 版中文版 1.1 节；Git 官方 FAQ（gitfaq：不要用云同步服务同步仓库，用 push 和 pull）；佐证：CISA《#StopRansomware Guide》（勒索软件防范指南）2023 年 9 月版 | 2026-11-20 |
| REMOTE-02 | 推送或公开之前，先查有没有密钥和隐私 | 必须（适用范围：所有项目） | 行业要求（只对别人的个人信息成立；你自己的密钥见 1.9 课 REPO-01，惯例·事实标准） | GitHub 使用政策（Acceptable Use Policies）第 3、8 节和执行说明；《个人信息保护法》第九条、第七十二条；GitHub Docs “About push protection” | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

为什么 REMOTE-02 是“行业要求”：这说的是“别人的个人信息”那一半。未经同意把别人的个人信息推上 GitHub，平台可以按使用政策删内容、封账号；在单位里处理个人信息，还有《个人信息保护法》。“你自己的密钥”那一半没有人罚你（1.9 课的 REPO-01 是惯例·事实标准），但后果是真的：密钥被人拿去用，费用和损失都是你的。1.9 课说过的推送保护（push protection），只拦推到公开仓库、它认得出的密钥；你的私有仓库没有人替你拦，只能靠提交和推送前的这一步检查。

## 收尾（约 25 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.12`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「REMOTE-01 重要仓库在别处有第二份，并且试过能恢复」「REMOTE-02 推送或公开之前，先查有没有密钥和隐私」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 备份：把今天的笔记和日志推到云端，最后由 `git push` 推上去。以后每次学完都做这一组（第 4 到 6 步），导师也会提醒你。分两段做，**一条一条敲，不要整块粘贴**。

   第一段，先看：

   ```zsh
   cd ~/Developer/fullstack-from-zero
   git status
   git grep --untracked -n -i -E "password|token|secret|key|密码|密钥|令牌" -- notes journal learner
   ```

5. 读第一段的输出。`git status` 你应该看到类似（你的会不一样；哪天第一次写日志，那天的日志文件会出现在 `Untracked files` 下面）：

   ```text
   On branch main
   Your branch is up to date with 'origin/main'.

   Changes not staged for commit:
     (use "git add <file>..." to update what will be committed)
     (use "git restore <file>..." to discard changes in working directory)
   	modified:   learner/log.jsonl
   	modified:   learner/state.json
   	modified:   notes/my-rules.md

   Untracked files:
     (use "git add <file>..." to include in what will be committed)
   	journal/2026-11-20.md

   no changes added to commit (use "git add" and/or "git commit -a")
   ```

   列表里有你不认识的文件，先停下问导师。`git grep` 搜到的每一行都读一遍：只是提到这些词的说明，放行；真的密钥或令牌：先作废（让它失效、换一个新的），再从文件里拿掉。

6. 都读过了，再做第二段。以后每课把提交说明里的 `1.12` 换成那一课的课号。

   ```zsh
   git add .
   git commit -m "docs: 记下第 1.12 课的行规和日志"
   git push
   git status
   ```

   最后 `git push` 和 `git status` 你应该看到（编号你的会不一样；`To` 这一行前面还有几行 `Enumerating objects…`、`Writing objects…` 这样的传输进度）：

   ```text
   To https://github.com/你的用户名/my-fullstack-learning.git
      f82b092..aaa9e00  main -> main
   On branch main
   Your branch is up to date with 'origin/main'.

   nothing to commit, working tree clean
   ```

   > 读懂这句：推送到这个地址：`main -> main` 是“本地的 main 推到远程的 main”，从 f82b092 前进到 aaa9e00。你的分支和 origin/main 一样新，工作区干净。

   如果 `git commit` 说 `no changes added to commit`（没有加进提交的改动），`git push` 又说 `Everything up-to-date`，就是今天的改动没提交、也没推上去：回到 `git add .` 那一步。

   只记了学习进度、没写笔记的日子，提交说明写 `chore: 记录学习进度` 就好。

都做完，这一课就完成了。下次可以对导师说“从 1.13 开始”。

## 想多了解

下面的内容都可以跳过。

- Pro Git 第 2 版 2.5 节“远程仓库的使用”（中文）：https://git-scm.com/book/zh/v2/Git-基础-远程仓库的使用 。书里的例子用 `master`，你的分支是 `main`，照着读时换一下。
- GitHub CLI 手册里 `gh repo create` 的全部选项（English）：https://cli.github.com/manual/gh_repo_create
- GitHub Docs：从仓库里删除敏感数据，万一推上去了怎么办（English）：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
