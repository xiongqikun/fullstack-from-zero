# 1.16 阶段作品与验收

> **用时** 3 站，约 140 分钟；开始之前核对行规笔记和学习仓库另需约 10 分钟（有漏写的，每补一条再加约 3 分钟；要提交推送的，再加约 10 分钟）；另有阶段验收 gate-1，单独一段时间，约 55～65 分钟 ｜ **前置** 1.15 ｜ **核实** 2026-11-20 · git 2.54 · macOS 27.2 · python3 3.14
> **学完你能** 把网页和学习仓库整理到“交得出手”的状态；在不看提示的情况下通过阶段验收 gate-1；用证据给这一阶段做一次复盘，定好阶段 2 怎么学。
> **本课行规** PM-03（见文末）

这是阶段 1 的最后一课。它不教新的命令，只把前 15 课学到的东西用在你自己的作品上，再用一次不给提示的考试证明你真的会了。

## 先想一想

你修好了一辆自行车，要交给朋友骑。说“修好了”之前，你会检查哪几样？

先在心里或纸上写两三条，第 1 站的概念讲完以后回来对一对。

## 开始之前（不算在三站的时间里）

前面每一课的收尾，都让你在 `notes/my-rules.md` 里那一课每条行规的小标题下面写一两句自己的话。第 1 站的检查要看阶段 0 和阶段 1 的 29 条都写了。它只看每个小标题下面的几行，小标题本身不算。写好的样子是这样：

```markdown
### GIT-03 提交前先看改了什么
提交前我先 git diff --staged 看一眼，上周就靠它发现多改了一行。
```

运行 `code notes/my-rules.md`，从上往下看一遍，哪个小标题下面还空着就补上，⌘S 保存。看一遍约 5 分钟，每补一条约 3 分钟。

然后在学习工作区运行 `git status`，看学习仓库有没有落下的东西。`learner/` 下的文件和 `PROGRESS.md` 是工具随时会改的，检查不看它们，收尾的备份会一起提交。还列着别的文件（刚补的笔记，或者导师改正课文错误（勘误）时动过的 `CHANGELOG.md`、`stages/` 下的文件）：按第 1.12 课收尾的那一组命令提交并推送，约 10 分钟。漏写的笔记，第 1 站的检查会全部列出来；没提交的文件，它会列出前几个，`git status` 里能看到全部。

## 第 1 站：整理作品（约 40 分钟）

### 概念

第 0.4 课你给每个任务定过“完成的定义”：做到哪些事，才算真的做完。这一站把同一个想法用在整个阶段上。一个阶段的作品，要满足三件事才算交得出手：

- **看得到**：别人不用来你电脑前，也能看到它。网页在网上，最新的提交已经推送。
- **看得懂**：别人打开就知道这是什么、里面有什么、能不能拿去用。README 和仓库对得上，提交历史一条条读得懂。
- **拿得回来**：你的电脑坏了，作品也丢不了。远程仓库里有完整的一份。

这样一组能拿给别人看、证明你做得出来的作品，叫**作品集（portfolio）**。你现在的作品集有两样：网页 `my-site`，和你的学习仓库（本机的 `fullstack-from-zero` 文件夹，GitHub 上的私有仓库 `my-fullstack-learning`）。

回到“先想一想”：骑得动，是“看得到、能用”；告诉朋友座椅怎么调，是“看得懂”；留着发票和保修卡，是“拿得回来”。这个类比在哪里不成立：自行车交出去就不在你手里了；你的作品还在你自己的电脑上，你会继续改它，所以每次改完都要重新确认一遍。

下面这张交付清单，就是这一站的“完成的定义”：

| 要求 | 怎么确认 |
|---|---|
| README 第一行是标题，写了真实的网页网址，写明用的是什么许可证 | 打开 README.md 看 |
| README 提到了仓库最上层的每个文件（README 自己除外），一般写在「里面有什么」那一节 | `git ls-files` 和 README 对一对 |
| 仓库里有 LICENSE | `git ls-files` |
| 网页大标题「你好，我是____」里的空填好了（填笔名就行，网页是公开的） | 打开 index.html 看 |
| 提交历史读得懂：1.10 课以后的提交都按约定式提交写（更早的不用改，历史不重写） | `git log --oneline` |
| 没有落下没提交的改动，提交都已推送 | `git status` 说 `nothing to commit, working tree clean` 和 `Your branch is up to date with 'origin/main'.` |
| 学习仓库里，阶段 0 和阶段 1 的每条行规都有你自己的话；日志都已提交、推送 | 「开始之前」那一步；在学习工作区里 `git status` |

### 跟我做

先在练习场的副本里拿清单走一遍，只看不改。副本和你的 `my-site` 是照同样的步骤搭出来的（第 1.13 课结束时的样子），还自带一个“替身仓库”扮演 GitHub。

#### 1. 搭好副本

在学习工作区里运行：

```zsh
python3 tools/course.py scenario 1.16
```

你应该看到：

```text
练习场景 1.16-start 搭好了。
位置：~/Developer/playground/1.16-start

这里有什么：
  网站的副本在这里：~/Developer/playground/1.16-start/my-site
  它的“GitHub”是同一个文件夹里的替身仓库：~/Developer/playground/1.16-start/remote/my-site.git

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.16-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.16 --reset
```

#### 2. 对照清单看一遍

先猜：README 的「里面有什么」，会不会把仓库里的文件都列上？

```zsh
cd ~/Developer/playground/1.16-start/my-site
cat README.md
git ls-files
```

你应该看到（第一句里的笔名你的会不一样）：

````text
# my-site

小林的个人网页：只有一页的小网站，是我学做软件的第一个作品。

## 里面有什么

- index.html：网页的内容
- style.css：网页的样式
- .editorconfig：告诉编辑器用 UTF-8 和 LF

## 怎么查看

在终端里进入这个文件夹，运行下面这条命令，网页会在浏览器里打开：

```zsh
open index.html
```

## 现在做到哪了

还在学习中，会一点一点改。
这个网站现在用 Git 记录每一次改动。

## 许可证

本项目使用 MIT 许可证，全文见 [LICENSE](LICENSE)。

## 网页地址

https://你的用户名.github.io/my-site/
.editorconfig
.gitignore
LICENSE
README.md
index.html
style.css
````

最后六行是 `git ls-files`（1.9 课学过）列出的 Git 管着的文件。拿清单对一对：标题、许可证一节、LICENSE 都有；网址在副本里是占位的，你的 README 里应该是 1.13 课的真网址。「里面有什么」还停在 1.5 课：后来进仓库的 `.gitignore` 没写进去（LICENSE 在「许可证」一节里提到了，也算提到），来访的人只能猜它是干什么的。这就是要补的地方。

#### 3. 故意出个错

先猜：在网站副本里直接运行检查命令，会怎样？

```zsh
python3 tools/course.py check 1.16a
```

你应该看到：

```text
python3: can't open file '/Users/你的用户名/Developer/playground/1.16-start/my-site/tools/course.py': [Errno 2] No such file or directory
```

> 读懂这句：python3 打不开文件 …/my-site/tools/course.py：没有这个文件或文件夹。

报错三问：谁在报错？`python3`。关键词？`can't open file` 和那个路径。我刚才敲了什么？`tools/course.py` 是相对路径，从当前文件夹算起，`my-site` 下面没有 `tools`。检查要回到学习工作区才能运行：

```zsh
cd ~/Developer/fullstack-from-zero
```

### 补全

现在轮到你自己的 `my-site`。把下面的空在心里填好，再动手：

```text
cd ~/Developer/________
code README.md                     # 补上和副本里一样缺的，⌘S 保存
git ____                           # 提交前先看改了什么
git add README.md
git commit -m "____: README 里列全仓库里的文件"
git status                         # 先说出它会说 ahead 还是 up to date
git ____                           # 发到 GitHub
git status                         # 要看到 up to date 和 working tree clean
```

### 自己做

目标：你的作品集满足交付清单的每一行。学习仓库在「开始之前」已经整理好，这一站动的是你真正的 `~/Developer/my-site`。

照「补全」那几行做。用 `code README.md` 打开 README〔对照文档，界面可能不同〕：只改一个文件里的几行，直接打开这个文件就行（ED-01 说的打开整个文件夹，是做项目的时候）。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

「里面有什么」一个文件一行，写它是干什么的。你的仓库多了别的文件，也要列上，比如第 1.15 课加的 `CLAUDE.md`（检查会把没提到的文件名列出来）。1.13 课已经写好的网址和许可证，确认一遍就行。

第 1.15 课在 my-site 里的提交（页脚那一行、CLAUDE.md）还没推送过，所以提交以后、推送之前，`git status` 会说（数字你的会不一样）：

```text
On branch main
Your branch is ahead of 'origin/main' by 3 commits.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

> 读懂这句：你的分支比 origin/main 领先 3 个提交。（用 git push 把本地的提交发布出去。）

“领先”就是“本地有、远程还没有”：这时电脑坏了，这些提交就丢了，所以还要推送。推送到 GitHub 时，`To` 那一行是 `https://github.com/…`〔建课时无法验证〕。

`git diff` 什么都没输出、`git commit` 说 `nothing to commit, working tree clean`：本来就没改什么（README 早已列全），就跳过提交；改过却看到它，多半是还没保存，按 ⌘S 再从 `git diff` 重来。

检查最后会问你 `my-site` 最新一个提交的编号：提交时那一行 `[main 1a2b3c4]` 里的 7 位就是；跳过了提交的，在 `my-site` 里运行 `git log --oneline` 看第一行。

- 提示：`python3 tools/course.py hint 1.16a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.16a`

> **想多了解（可跳过）：git diff 末尾多了一行 \ No newline at end of file**
>
> 意思是文件末尾没有换行符。这不影响网页。回到 VS Code，在最后一行后面按一次回车、保存，再看 `git diff`，这一行就没有了。第 1.4 课的 `.editorconfig` 让编辑器保存时自动补上它，所以多数时候你看不到这一行。

> **想多了解（可跳过）：在手机上看一眼**
>
> 推送以后过一两分钟，用手机浏览器打开你的网页网址，就是“别人看得到”最直接的证明。

> **存档点 1.16a**：到这里可以安全停下。下次可以对导师说“从 1.16b 继续”。

## 第 2 站：阶段验收（约 40 分钟）

这一站的时间只算排错题和写讲解题的回答；阶段验收 gate-1 的考试在中途存档点后面，时间另算。

### 概念

一站的检查，是在你刚学完、课文还开着的时候做的。验收要回答另一个问题：过了几天、不看提示、换一个没见过的情境，你还做得出来吗？这种考法叫**冷考（cold test）**。第 1.15 课的“验收”是你验收 AI 交来的改动；这一次被验收的是你自己。

这一站的验收有三部分：

1. **排错题**：一个坏掉的网站副本，你找出原因、修好，再说出是哪个提交惹的祸。这一站的「自己做」就是它。
2. **实操题**：`exam gate-1` 在练习场里现搭题目，第 1.11～1.16 课每课一道，名字随机，没有提示；后面几课的题也要用到前面学的本事。
3. **讲解题**（gate-0 里做过）：先把回答写进 `notes/gate-1-explain.md`，再讲给考官听。考官就是只按评分标准和你的证据判过没过、不教你的那一方：可以是导师，也可以是一个新开的 Claude 对话。

**怎样算通过**：阶段验收 gate-1 本身看两样：第 1.11～1.16 课每一课都有一道实操题通过，讲解题评为通过并用 `exam gate-1 --explain pass` 记下。这一站的检查再加一样：排错题修好。三样都做到，阶段 1 就过关了。

**没通过会怎样**：不从头再来。练好再运行 `exam gate-1`，只考还没通过的课，题换另一套题面，这就是补考。

冷考像驾照路考：教练不说话，路线也不是你练熟的那条。这个类比在哪里不成立：路考没过要重新排队，这里随时只补没通过的课。

### 跟我做

#### 1. 看看 gate-1 现在的样子

先猜：不带关卡名，这条命令会开考吗？

```zsh
python3 tools/course.py exam
```

你应该看到（日期和分钟数你的会不一样）：

```text
关卡（4 个）：
  gate-0  起步小关卡（0.1 到 0.4 课）：通过了（讲解题 2026-11-18）
  gate-a  小关卡「终端与文档关卡」（1.1 到 1.5 课）：通过了（讲解题 2026-11-18）
  gate-b  小关卡「本地 Git 关卡」（1.6 到 1.10 课）：通过了（讲解题 2026-11-18）
  gate-1  阶段 1 验收（1.11 到 1.16 课）：还没考过；一场 6 题，预计 50 分钟

开始一个关卡的考试：python3 tools/course.py exam <关卡>，例如 python3 tools/course.py exam gate-0
```

不带关卡名只是列一列，不会开考。gate-1 那一行说一场几题、大约多久，讲解题另加约 10 分钟。前面的关卡没通过的，那一行会写还差什么。

#### 2. 故意出个错

把关卡名里的短横线漏掉：

```zsh
python3 tools/course.py exam gate1
```

你应该看到：

```text
用法不对：没有「gate1」这个关卡。
可以用的关卡：gate-0、gate-a、gate-b、gate-1
```

报错三问：谁在报错？课程工具（它的话都是中文）。关键词？「没有「gate1」这个关卡」。我刚才敲了什么？`gate1`，少了 `-`。工具顺便列出了能用的名字，照着改就行。

### 补全

排错题动手之前，先把思路填完整（用到的是 1.7 课的 `git log --stat`、`git show` 和 1.9 课第 2 站）：

```text
现象：git status 说一个 .tmp 文件被改了，可 .gitignore 里明明写着 *.tmp
猜想：“不拍名单”只管 ________ 的文件
验证：git log --stat 里最早（最下面）列出这个文件的提交，就是把它带进来的那个（输出长，按 q 退出）
修法：让 Git 不再管它，但文件留在电脑上；再提交一次，说明用约定式提交
确认：git status 是 ________ 的
```

### 自己做

**1. 排错题。** 它是验收的一部分：先别看提示。看到第 4 级（完整答案）也没关系，这一站会记成“带扶手完成”，几天后要不看提示再做一次。搭好坏掉的副本：

```zsh
python3 tools/course.py scenario 1.16b
```

你应该看到（文件名你的会不一样）：

```text
练习场景 1.16b 搭好了。
位置：~/Developer/playground/1.16b

这里有什么：
  网站副本在这里：~/Developer/playground/1.16b/my-site
  现象：git status 总说 todo.tmp 被修改了，可 .gitignore 里明明写着 *.tmp。

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.16b
  2. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.16b

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.16b --reset
```

进入副本看现象：

```zsh
cd ~/Developer/playground/1.16b/my-site
git status
```

你应该看到（文件名你的会不一样）：

```text
On branch main
Your branch is ahead of 'origin/main' by 2 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   todo.tmp

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：有一处没暂存的改动：那个 .tmp 文件被修改了。（没有加进暂存区的东西不会被提交。）

目标：这个 `.tmp` 文件留在电脑上，但以后不再被 Git 管；用一个符合约定式提交的提交记下这件事；最后 `git status` 不再列出要提交的改动。这个副本是练习用的，不用推送，`ahead of 'origin/main'` 那一行会一直在。检查会问你：是哪个提交把它带进仓库的（编号前 7 位）。

工具让你做完就检查。这一站的检查连 gate-1 一起看，留到考完再运行。

**2. 写下讲解题的回答。** 回到学习工作区，新建一个文件：

```zsh
cd ~/Developer/fullstack-from-zero
code notes/gate-1-explain.md
```

〔对照文档，界面可能不同〕把下面的骨架粘进去，在每个“（你的回答）”那里用你自己的话写一两句（每题至少 30 个字），⌘S 保存。先不翻课文、不问 AI：

```markdown
# 阶段 1 验收：讲清为什么

## 问题 1
为什么密码、令牌这类文件要在提交之前就用 .gitignore 挡住，而不是提交以后再删掉？
（你的回答）

## 问题 2
为什么学习仓库要推送到 GitHub、并且试着克隆回来，而不是只靠 iCloud 同步来备份？
（你的回答）
```

然后提交。这次不用推送，收尾的备份会把它推上去：

```zsh
git add notes/gate-1-explain.md
git commit -m "docs: 写下阶段 1 的讲解题"
```

你应该看到（编号和行数你的会不一样）：

```text
[main 27c5537] docs: 写下阶段 1 的讲解题
 1 file changed, 9 insertions(+)
 create mode 100644 notes/gate-1-explain.md
```

`git add` 说 `fatal: pathspec 'notes/gate-1-explain.md' did not match any files`（路径没有对上任何文件）的话，多半是文件还没保存（新文件不保存就不存在），或者你不在学习工作区里：先按 ⌘S，再用 `pwd` 看一眼在哪。

收尾备份时，查密钥的那一步会列出这个文件里问题 1 那一行（也许还有你的回答）：它是题目，不是密钥，读一遍就放行。

> **中途存档点**：排错题做完、讲解题的回答写好并提交了，到这里可以安全停下。下次可以对导师说“做小关卡 gate-1”。

### 阶段验收 gate-1（单独一段时间，约 55～65 分钟）

实操题的题数和预计用时，开考时工具会打印（一般 45～55 分钟）；讲解题另需约 10 分钟。可以分两次做：先实操题，再讲解题。考试中没有提示，先别问导师或 AI；做不出来的题空着就行。

#### 实操题

找一段不会被打断的时间，在学习工作区里开考：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py exam gate-1
```

开头和结尾像这样（题目、名字和文件夹每次随机，你的会不一样；中间省略了五道题）。预计分钟数是抽到的六道题加起来的，和列表里那个开考前估的数可能差几分钟：

```text
关卡考试 · gate-1「阶段 1 验收」 · 第 1 场
一共 6 题，每课一题，预计 53 分钟（每题的预计分钟数加起来）。
实操题都通过以后还有讲解题，约 10 分钟：导师问你几个问题，请你讲出“为什么这样做”。

考试规则：
  - 这是不带提示的实操：考试期间没有提示，先别问导师或 AI。
  - 每道题都在练习场里自己的文件夹里做，改坏了也没关系，不会影响你自己的文件。
  - 做不出来的题空着就行。批改以后会告诉你该练什么，准备好再补考。
……
第 6 题 · 按说明把一个文件夹建成规范的仓库（复习 1.6、1.9、1.10 课）（约 15 分钟）
  文件夹 ~/Developer/playground/exam-gate-1/1.16-x1/shop-pine 是一个还没有版本管理的小网页。把它变成 Git 仓库并提交，要求：secrets.env 和 cache/ 文件夹永远不能进仓库；至少两个提交，每个提交只做一件事；每条提交说明都符合约定式提交；做完以后 git status 是干净的。
  这道题的文件夹：~/Developer/playground/exam-gate-1/1.16-x1
  先进入这道题的文件夹：cd ~/Developer/playground/exam-gate-1/1.16-x1。题目里说的文件夹如果在它里面，再 cd 进那一层。

做完以后（或者做不下去了），回到学习工作区批改：
  cd ~/Developer/fullstack-from-zero
  python3 tools/course.py exam gate-1 --grade
```

一题一题做。做完（或者做不下去了）回到学习工作区批改：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py exam gate-1 --grade
```

批改时有的题会问你一个问题（比如是哪个提交弄坏了网页），照你做题时看到的回答。批改过的题在这一场里就定了，答错了也不能当场改。有没通过的课，工具会告诉你练什么、怎么补考。每一课都有一道题通过以后，最后一行是：

```text
实操题都通过了。还差讲解题：对导师说“请问我 gate-1 的讲解题”。导师判断以后，用这条命令记下结果：python3 tools/course.py exam gate-1 --explain pass（要再来一次就写 again）
```

#### 讲解题

讲给考官听，二选一〔建课时无法验证〕：

- **导师**：在平时上课的对话里对导师说“请问我 gate-1 的讲解题”。导师先读你的 `notes/gate-1-explain.md`，再请你不看笔记讲一遍，按 `gates/gate-1/rubric.md` 评。
- **独立的考官**：在 Claude 桌面应用里新开一个对话，项目文件夹**不要**选 fullstack-from-zero：这样它只看得到你贴过去的东西，判的就只是你的证据。运行 `code gates/gate-1/examiner-prompt.md` 打开考官说明，⌘A（按住 Command 再按 A）全选、⌘C 复制，粘贴到新对话里发出去。它会请你再贴三样：`notes/gate-1-explain.md` 的全文、`exam gate-1 --grade` 最后一次的输出、`check 1.16b` 的输出（排错题由它判；这时它还会列出讲解题没记下，正常）。然后它一题一题问你，最后写出结论。这个新对话和导师不共享记忆，结论要你自己带回来。

评完，你自己运行这条命令记下结果（没过就把 `pass` 换成 `again`，过几天换个问法再讲一次）：

```zsh
python3 tools/course.py exam gate-1 --explain pass
```

实操题都通过以后记下“通过”，你应该看到（日期你的会不一样）：

```text
讲解题的结果记下了：通过（2026-11-20）。
阶段验收 gate-1 通过了：实操题每课都有一题通过，讲解题也记为通过（2026-11-20）。
```

记在文件里，下一次对话的导师才知道结果。

#### 运行这一站的检查

最后运行这一站的检查。它看三样：排错题修好了，讲解题的回答写了并提交了，阶段验收 gate-1 通过了。

- 提示：`python3 tools/course.py hint 1.16b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.16b`

> **存档点 1.16b**：到这里可以安全停下。下次可以对导师说“从 1.16c 继续”。

## 第 3 站：复盘和下一段（约 40 分钟）

### 概念

第 0.4 课你每周做过复盘：一轮结束后回头看，哪里顺、哪里卡、下一轮改一件什么。这一站把它用在整整一个阶段上，回答三个问题：

1. **做得好的**：哪些做法让你学得顺，下一阶段要保留？
2. **要改的**：哪里卡住了、慢了、反复出错？
3. **下一步**：下一阶段具体改一件什么事？要写成能做、能检查的事，比如“每次动手前先运行 git status”，而不是“以后细心一点”。

阶段复盘要看证据，不靠感觉。你手里有三样证据：工具记下的学习用时、`journal/` 里每次的“卡在哪”、这一课的验收结果。拿计划和实际比一比，最能说明问题：路线图 `ROADMAP.md` 给每个阶段估了小时数，你实际用了多少？差得多，下一阶段的每周计划就要跟着调。

用 Scrum（第 0.4 课提过）的团队，每个冲刺（Sprint，一个月以内的固定一段时间）结束都开一次回顾会（Sprint Retrospective），一起复盘、定下要改进的地方。行规 PM-03 的来源就是它（三个小标题是本课程的整理方式）。

### 跟我做

#### 1. 拿出用时的证据

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py status
```

输出有好几行。找到「累计学习」这一行，它是这样的（小时数和次数你的会不一样）：

```text
  累计学习：约 25.0 小时（21 次）（按每次学习第一条和最后一条命令之间的时间算，实际会更多）
```

记下这个小时数。它只算命令之间的时间，真实用时会更多。

计划用时在路线图里：运行 `code ROADMAP.md`〔对照文档，界面可能不同〕，在「时间和节奏」一节的「落脚点」表里，找「学完」是「阶段 1」的那一行，看它的「累计小时」：这是阶段 0 加阶段 1 的计划用时。

#### 2. 故意出个错

复盘文件还没建，先试着看它：

```zsh
cat notes/stage-1-retro.md
```

你应该看到：

```text
cat: notes/stage-1-retro.md: No such file or directory
```

> 读懂这句：cat：notes/stage-1-retro.md：没有这个文件或文件夹。

报错三问：谁在报错？`cat`。关键词？`No such file or directory`。我刚才敲了什么？一个还不存在的文件。下一步就建它。

#### 3. 看日志里的“卡在哪”

```zsh
ls journal
```

你应该看到每次学习写的日志，一天一个文件（日期和个数你的会不一样）：

```text
2026-11-18.md
README.md
```

挑最近的一天，用 `cat journal/` 加文件名打开，看“卡在哪”那一行。同一类问题出现两次以上，就写进“要改的”。

#### 4. 建复盘文件

课程准备好了复盘的骨架 `templates/retro.md`，里面是六个小标题。复制一份，再打开：

```zsh
cp templates/retro.md notes/stage-1-retro.md
code notes/stage-1-retro.md
```

〔对照文档，界面可能不同〕先从上往下读一遍六个小标题，还不用填。

### 补全

“要改的”和“下一步”要一一对应。把右边补成一件能做、能检查的事：

```text
要改的：常常忘了推送，第二天才发现        → 下一步：________
要改的：卡住半小时才去要提示              → 下一步：________
要改的：只有周末学，一周一次，总是忘      → 下一步：________
```

### 自己做

目标：`notes/stage-1-retro.md` 里六节都有你自己的内容：做得好的、要改的、下一步、用时（计划和实际两个数字）、下一阶段的每周计划（每周几小时、哪几天）、给课程的两条反馈；它已经提交。

**1. 填。** 照你的证据填，每节至少写一句：标题里的“（填阶段号）”改成 1；「用时」的计划写路线图里的小时数，实际写 `status` 的小时数（写 30 或 三十 都行）；最后那段「用法」读完删掉。写完按 ⌘S 保存。

「下一阶段的每周计划」写你真能做到的数字。路线图建议每周 8～10 小时、至少分三次；少一些也可以，只是阶段 2 会拉得更长。「给课程的反馈」那两问，导师准备阶段 2 时会读，越具体越有用，比如“1.9 课第 2 站 git rm --cached 那一段看了三遍”。

**2. 提交。** 先说出提交以后，新文件会从哪一区到哪一区：从工作区进暂存区，再进本地历史；推送到远程，留给收尾的备份。

```zsh
git status
```

你应该看到类似这样（`learner/` 下的文件、今天的日志也可能列出来，你的列表会不一样）：

```text
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   learner/log.jsonl
	modified:   learner/state.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	notes/stage-1-retro.md

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：本地比 origin/main 多 1 个提交（第 2 站讲解题的那个，收尾时一起推送；已经推送过的，这一行是 up to date）；有没暂存的修改（learner/ 下的两个文件），还有一个 Git 还没管的新文件 notes/stage-1-retro.md。

这次只提交复盘文件（COMMIT-02：一次提交一件事）：

```zsh
git add notes/stage-1-retro.md
git commit -m "docs: 阶段 1 复盘"
```

你应该看到（编号和行数你的会不一样）：

```text
[main 163be12] docs: 阶段 1 复盘
 1 file changed, 24 insertions(+)
 create mode 100644 notes/stage-1-retro.md
```

`git add` 说 `pathspec … did not match any files` 的话，多半是不在学习工作区里，或者文件名打错了（比如后面多了一个中文逗号）。改完忘了保存，提交进去的是没填的骨架：检查会指出来，按 ⌘S 保存后再 `git add`、`git commit` 一次。

检查会问你一个问题：`status` 显示你累计学了约多少小时。

- 提示：`python3 tools/course.py hint 1.16c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.16c`

> **想多了解（可跳过）：旧资料里的回顾会**
>
> **旧教程提醒**：照 2017 年 11 月版《Scrum 指南》写的资料会说，下一个冲刺的待办清单（Sprint Backlog，这个冲刺要做的事）里至少要有一条上次回顾会定下的改进；现在的 2020 年 11 月版改成：最有影响的改进尽快去做，可以放进下一个冲刺的待办清单，不再规定条数（自 2020 年 11 月起）。指南写的是团队讨论这个冲刺什么做得好、遇到了什么问题、问题有没有解决，没有规定一张固定的问题清单；“做得好的 / 要改的 / 下一步”是常见的整理方式，这门课用它。网上还会搜到 2025 年起的《Scrum Guide Expansion Pack》：它是 2020 年版指南的补充材料，不是新版指南。

> **存档点 1.16c**：到这里可以安全停下。下次可以对导师说“从 1.16 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| PM-03 | 每个阶段结束做一次复盘：用记录下来的证据回看做得好的、要改的、下一步；下一步写成一件能做、能检查的事 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 惯例·事实标准 | 《Scrum 指南》2020 年 11 月版「回顾会」（Sprint Retrospective）；《敏捷宣言》十二条原则的最后一条 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 20 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.16`

   三站都通过时，你应该看到下面这样（日期你的会不一样）：

   ```text
   全课检查 · 1.16 阶段作品与验收

     ✅ 1.16a 整理作品：已通过（2026-11-20）
     ✅ 1.16b 阶段验收：已通过（2026-11-20）
     ✅ 1.16c 复盘和下一段：已通过（2026-11-20）

   ✅ 通过 · 全课 1.16：3 站都已通过

     收尾还有三件小事：
       1. 行规笔记：运行 code notes/my-rules.md，在小标题「PM-03 每个阶段结束做一次复盘」下面用自己的话写一两句，再配一个你自己的例子
       2. 一句话日志：python3 tools/course.py journal
       3. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做

     已有的课程都学完了。下次可以对导师说“准备阶段 2”。
   ```

2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「PM-03 每个阶段结束做一次复盘」下面用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。

阶段 1 到这里结束。你手里有一个放在网上的网页、一个有后悔药和云端备份的学习仓库，还有一份写着证据的复盘。说“准备阶段 2”以后，导师会读你复盘里的每周计划和反馈，先和你一起写一页纸的阶段 2 小设计；你确认主题和节奏以后，再分几批建课、试做、交给你。在那之前，照常做复习。

都做完，这一课就完成了。下次可以对导师说“准备阶段 2”。

## 想多了解

这一节都可以跳过。

- 《Scrum 指南》2020 年 11 月版，官方简体中文译本（中文）：https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Chinese-Simplified.pdf ，看“Sprint Retrospective”一节，一页不到。
- 敏捷宣言遵循的原则（中文）：https://agilemanifesto.org/iso/zhchs/principles.html ，十二条原则的最后一条讲的就是定期反思和调整。
- 《Scrum 指南》2020 年 11 月版英文原文（English）：https://scrumguides.org/scrum-guide.html
