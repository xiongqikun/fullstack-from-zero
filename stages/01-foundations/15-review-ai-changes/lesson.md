# 1.15 验收 AI 的改动

> **用时** 3 站，约 145 分钟（含收尾） ｜ **前置** 1.14 ｜ **核实** 2026-11-20 · git 2.54.0 · macOS 27.2.1 · zsh 5.9 · python3 3.14.9
> **学完你能** 让 AI（导师）改你的网页，再用 git status、git diff 亲手验收，决定收下还是退回；从一次 AI 改动里挑出多改的文件、像密钥的新文件和写错的提交说明，并在提交里如实写明 AI 参与；给 my-site 写一份 CLAUDE.md，把你给 AI 的规矩留在仓库里。
> **本课行规** AI-01、AI-02（见文末）

## 先想一想

你请装修师傅换一个水龙头。他干完说：“换好了，别的都没动。”你会怎么确认？只听他这一句，还是自己去厨房看一圈：水龙头换了没有、能不能出水、墙上有没有多出一个洞、地上有没有落下工具？

把你的答案记在心里。第 1 站的概念讲完，回头对一对。

## 第 1 站：让 AI 干活，你来验收（约 40 分钟）

### 概念

AI 替你改完文件，改动只是一份**提案**：写进了文件，还没拍进快照。由你来**验收（acceptance review）**：按清单核对，再决定收下还是退回。

类比：AI 是装修师傅，你是房主，看完验收单才签字；在 Git 里，签字就是**你亲手提交**。这个类比在哪里不成立：师傅很少顺手在别的房间多钉钉子，AI 常常会，还说“别的都没动”。所以不听它说，看 Git 记下的改动。

验收清单有五个问题（完整的一页在 `templates/ai-change-checklist.md`）：

1. 改的是不是我要的？
2. 有没有多改？（我没提到的文件、没提到的地方）
3. 能不能正常显示？（打开网页或运行程序看一次）
4. 有没有新增文件？（新文件在 `git status` 的 Untracked files 下面）
5. 有没有不该出现的内容？（密钥、密码、真实姓名、电话、住址）

用到的命令：`git status`；新命令 `git diff --stat`，打印**改动统计（diffstat）**，每个文件改了几行（stat 是 statistics，统计）；`git diff`；`open index.html`。回头看「先想一想」：去厨房看一圈，就是这五问。这就是本课的行规 AI-01：AI 的改动先看 diff 再接受。

### 跟我做

练习场扮演“导师刚改完”：任务是在首页列表下面加一节「我在学什么」，导师说只改了 `index.html`。

#### 1. 搭好练习场

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.15a
```

你应该看到：

```text
练习场景 1.15a 搭好了。
位置：~/Developer/playground/1.15a

这里有什么：
  网站副本：~/Developer/playground/1.15a/my-site（导师刚改完，还没提交；第 1 站用）
  练习仓库：~/Developer/playground/1.15a/fx-tool（AI 刚改完，还没提交；第 2 站用）
  AI 的另一次改动：~/Developer/playground/1.15a/ai-change（网站副本和 AI 的交付说明；第 2 站「自己做」用）

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.15a
  2. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.15a

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.15a --reset
```

检查看的是你自己的网站，等「自己做」做完再运行。

#### 2. 动了哪些文件

先猜：`git status` 会列出几个文件？

```zsh
cd ~/Developer/playground/1.15a/my-site
git status
```

你应该看到：

```text
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   index.html

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：index.html 被修改了，还没放进暂存区。

只有一个文件，没有新文件（第 4 问）。

#### 3. 改了多少

```zsh
git diff --stat
```

你应该看到：

```text
 index.html | 7 +++++++
 1 file changed, 7 insertions(+)
```

> 读懂这句：index.html 改了 7 行，全是新增；一共 1 个文件改了，加了 7 行。

7 行对得上；数字大得出奇，就是多改的信号。

#### 4. 逐行读

先猜：加号开头的有几行？

```zsh
git diff
```

你应该看到（`index` 那一行的编号和列表里“下一步”那一行，你的会不一样；输出比窗口长、底下出现 `:` 时按 q 退出）：

```text
diff --git a/index.html b/index.html
index 4d84134..ce61695 100644
--- a/index.html
+++ b/index.html
@@ -18,6 +18,13 @@
       <li>我已经把网页放到了网上</li>
       <li>下一步：学一点 CSS 排版</li>
     </ul>
+
+    <h2>我在学什么</h2>
+    <ul>
+      <li>终端：新建、复制、查找文件</li>
+      <li>Git：提交、看改动、撤销</li>
+      <li>GitHub：备份和发布网页</li>
+    </ul>
   </main>
 
   <footer>
```

对照清单：是要的那一节（第 1 问），别处没动（第 2 问），没有隐私（第 5 问）。看网页和提交留到「自己做」。

#### 5. 故意出一次错：退回时忘了写文件名

验收不通过就用第 1.8 课的 `git restore` 退回。先看一个常见的错：

```zsh
git restore
```

你应该看到：

```text
fatal: you must specify path(s) to restore
```

> 读懂这句：致命错误：你必须指定要恢复哪些路径（文件）。

报错三问：谁在报错？`git`。关键词？you must specify path(s)：要写文件名。我敲了什么？只有 `git restore`。真要退回写 `git restore index.html`；这里不用退回。

### 补全

把验收的顺序填完整：

```text
git ______            ← 动了哪些文件，有没有新文件
git diff ______       ← 每个文件改了多少行
git ______            ← 逐行读
open ______           ← 亲眼看网页
收下：git add 文件名，然后 git ______ -m "类型: 说明"
退回：git ______ 文件名
```

### 自己做

这次请导师用干活模式（第 0.1 课提过）改你的网站 `~/Developer/my-site` 的页脚，你来验收：这一站练的是验收，不是改网页。

1. 对导师说（引号里那句可以换）：

   > 干活：这是 1.15a，请你改我的网站，我来验收。在 ~/Developer/my-site/index.html 的页脚（footer）里加一行字：“这个网页由我和 AI 一起维护”。只改 index.html，改完不要提交，告诉我你改了什么。

   〔建课时无法验证〕Claude 应用可能先问你允不允许：看清是 `my-site` 里的文件再允许。

   和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

2. 导师改完以后，对它说“回到上课”。五个问题由你来答。
3. 进入 `~/Developer/my-site`：`git status`、`git diff --stat`、`git diff`，再 `open index.html`〔对照文档，界面可能不同〕看页脚。网页是公开的，不能有真名、电话、住址。
4. 收下就 `git add` 要的文件，再提交，这就是签字：`git commit -m "类型: 说明" -m "Co-Authored-By: Claude <noreply@anthropic.com>"`（约定式提交；第二个 `-m` 写明 AI 参与，第 2 站细讲）。不要就 `git restore 文件名`；也可以只收一部分。
- 提示：`python3 tools/course.py hint 1.15a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.15a`

> **想多了解（可跳过）：弹窗问你，不等于你看过**
>
> **旧教程提醒**：以前的资料说 Claude Code（导师背后的编程助手）每改一个文件都先弹窗问你，点了同意就算看过。现在，自 Claude Code v2.1.283 起，它的命令行版和 VS Code 插件默认用自动模式（Auto），很多操作不再问你；桌面应用按你设置里的默认权限模式（permission mode，决定它动手前问不问你的设置，和导师的上课、干活、急救三种模式无关），大多数改文件、跑命令的操作之前都先问你的那一种叫 Manual（Claude Code 官方文档 Permission modes，2026-11-20 核对）。弹不弹窗，都以 `git status` 和 `git diff` 为准。

> **存档点 1.15a**：到这里可以安全停下。下次可以对导师说“从 1.15b 继续”。

## 第 2 站：找茬：一次 AI 改动里的三处问题（约 40 分钟）

### 概念

以**改动本身**为准，不以 AI 的说明为准：AI 交活附的说明是它自己的总结，会漏也会错。常漏三类：

- **范围外的改动（out-of-scope change）**：没让改却改了的地方，常藏在别的文件里。
- **多出来的文件**：草稿、试验文件，最危险的是像密钥的文件。
- **说错的提交说明**：类型不对，或和改动对不上。所以提交说明由你来写。

类比：快递员说“都放好了”，门口却多了一个不是你的箱子。这个类比在哪里不成立：箱子一眼看得见；AI 多建的文件不在 `git diff` 里，只在 `git status` 的 Untracked files 下面。

### 跟我做

练习场 1.15a 里的 `fx-tool` 是汇率小程序。AI 的任务：打印结果后，再提醒一句“这是示例汇率”。AI 交活时说：

```text
我做了什么：在 convert.py 里加了一行 print。运行 python3 convert.py 可以看到提醒。
建议的提交说明：feat: 输出里提醒这是示例汇率
```

#### 1. 动了哪些文件，改了多少

先猜：`git status` 会列出几个文件？

```zsh
cd ~/Developer/playground/1.15a/fx-tool
git status
```

你应该看到：

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   convert.py
	modified:   rates.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	ai-scratch.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：convert.py 和 rates.txt 被修改了；还有一个 Git 没跟踪过的新文件 ai-scratch.txt。

```zsh
git diff --stat
```

你应该看到：

```text
 convert.py | 1 +
 rates.txt  | 2 +-
 2 files changed, 2 insertions(+), 1 deletion(-)
```

> 读懂这句：convert.py 加了 1 行；rates.txt 删 1 行、加 1 行，就是改了 1 行。

AI 说动了一个文件，Git 说三个。

#### 2. 逐行读

```zsh
git diff
```

你应该看到：

```text
diff --git a/convert.py b/convert.py
index 6d712ba..4deb7e7 100644
--- a/convert.py
+++ b/convert.py
@@ -11,6 +11,7 @@ USD_TO_CNY = 7.10  # 1 美元换多少人民币。这是一个示例数字，不
 def main():
     amount_cny = AMOUNT_USD * USD_TO_CNY
     print(f"{AMOUNT_USD} 美元 ≈ {amount_cny:.2f} 人民币（按 1 美元 = {USD_TO_CNY:.2f} 人民币计算）")
+    print("提醒：这是示例汇率，不是真实汇率")
 
 
 if __name__ == "__main__":
diff --git a/rates.txt b/rates.txt
index dc5a824..4a4af73 100644
--- a/rates.txt
+++ b/rates.txt
@@ -1,6 +1,6 @@
 # 示例数据：1 美元可以换多少其他货币。数字是为练习编的，不是真实汇率。
 # 每行三列，用空格隔开：货币代码  中文名称  1 美元可换的数量
-CNY  人民币    7.10
+CNY  人民币    7.30
 EUR  欧元      0.92
 JPY  日元      150.00
 GBP  英镑      0.79
```

第 1、2、5 问：`convert.py` 只多了一行 print，没有别的；`rates.txt` 里的汇率被改了，任务没提它，是范围外的改动。照第 1.8 课退回：

```zsh
git restore rates.txt
```

没有输出。

#### 3. 故意出一次错：用 restore 对付新文件

先猜：同一条命令能退回 `ai-scratch.txt` 吗？

```zsh
git restore ai-scratch.txt
```

你应该看到：

```text
error: pathspec 'ai-scratch.txt' did not match any file(s) known to git
```

> 读懂这句：错误：路径 'ai-scratch.txt' 对不上任何 Git 认识的文件。

报错三问：谁在报错？`git`。关键词？did not match any file(s) known to git：Git 不认识它。我敲了什么？对新文件用了 `git restore`，它只能恢复 Git 记录过的文件。新文件先看清再删（第 1.2 课 TERM-02）：

```zsh
cat ai-scratch.txt
rm ai-scratch.txt
```

你应该看到：

```text
草稿：我先试了两种写法，留着备用。
print("注意：示例汇率")
```

#### 4. 亲手运行一次（第 3 问）

```zsh
python3 convert.py
```

你应该看到：

```text
100 美元 ≈ 710.00 人民币（按 1 美元 = 7.10 人民币计算）
提醒：这是示例汇率，不是真实汇率
```

#### 5. 提交说明由你来写

类型 `feat` 对得上：多了一个新输出。AI 写的要如实写明，这是行规 AI-02：在第 1.10 课说的脚注（提交说明的最后一段，不是网页页脚）写一行 `名字: 内容`，叫**尾注（trailer）**，比如 `Co-Authored-By: Claude <noreply@anthropic.com>`（共同作者；noreply 是不收信的地址）。

第二个 `-m`（第 1.10 课）写尾注，放在半角引号 `"` 里（不然 zsh 会把 `<` 当成“从文件读”）：打成中文引号会报 `zsh: no such file or directory: noreply@anthropic.com`，什么也没提交；少打一个引号，命令停在 `dquote>`，按 Ctrl+C 重新敲。先说出第 1.6 课那张四个区域的图会怎么变：`convert.py` 到暂存区，再到本地历史。

```zsh
git add convert.py
git commit -m "feat: 输出里提醒这是示例汇率" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

你应该看到（编号你的会不一样）：

```text
[main e93078e] feat: 输出里提醒这是示例汇率
 1 file changed, 1 insertion(+)
```

> 读懂这句：新建了提交 e93078e；1 个文件改了，加了 1 行。

作者还是你，尾注不转移责任。

### 补全

`git status` 里出现了下面三种情况，填上处理办法：

```text
modified:   任务要的文件        → 读完 git diff，git ______，再 git commit -m "…" -m "______: Claude <noreply@anthropic.com>"
modified:   任务没提到的文件    → git ______ 文件名
Untracked:  任务没提到的新文件  → 先 ______ 文件名 看内容，确认不要再 ______ 文件名
```

### 自己做

AI 的另一次改动在 `~/Developer/playground/1.15a/ai-change`：网站副本 `my-site` 和交付说明 `ai-report.txt`。问题有三处，说明一处没提。

1. 进入 `ai-change/my-site`，用 `cat ../ai-report.txt` 读交付说明（`..` 是上一级文件夹）。
2. 按清单验收（这一站不用打开网页），找出三处问题：一个不该改的文件、一个像密钥的新文件、一条类型不对的建议提交说明。
3. 收拾干净：范围外的改动退回，像密钥的文件看清后删掉，任务要的那一节用对的类型提交并加尾注，最后 `git status` 干净。像密钥的文件千万不要提交，类型和尾注也要一次写对：提交以后改不了，只能重搭练习场。
- 提示：`python3 tools/course.py hint 1.15b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.15b`

> **想多了解（可跳过）：看完整的提交说明，尾注的写法**
>
> `git log --oneline` 只显示第一行；`git log -1`（第 1.11 课用过）显示最新一个提交的全部说明，尾注在最后一段：
>
> ```text
> commit e93078e25491b5a69a4f5b234eda52b5d066397e
> Author: 你的名字 <you@example.com>
> Date:   Fri Nov 20 09:34:28 2026 +0800
>
>     feat: 输出里提醒这是示例汇率
>     
>     Co-Authored-By: Claude <noreply@anthropic.com>
> ```
>
> （编号、名字、邮箱和时间你的会不一样。）Claude Code 自己提交时，尾注里写的是提交时用的模型名，比如 `Claude Sonnet 5`；本课用简写 `Claude`（Claude Code 文档 Settings reference，2026-11-20 核对）。GitHub 文档写 `Co-authored-by`，Claude Code 写 `Co-Authored-By`：`git log` 按尾注名字查找时不分大小写（Git 2.54 的 git log 手册，2026-11-20 在本机核对），两种都找得到。

> **存档点 1.15b**：到这里可以安全停下。下次可以对导师说“从 1.15c 继续”。

## 第 3 站：给 AI 立规矩（约 40 分钟）

### 概念

前两站里，你每次都要再说一遍“只改 index.html”“改完不要提交”。话写在聊天里，会话（你和 AI 的一次对话）一结束就没了。

**项目说明文件（project instruction file）**就是把这些规矩写进仓库的一个文件。Claude Code（导师背后那个能读写文件、运行命令的编程助手）用项目根目录的 `CLAUDE.md`：在这个项目里开工时先读它。

类比：给新同事留一张交接单，谁来接手都先看它。这个类比在哪里不成立：同事会照做，AI 不一定。官方文档的原话：Claude treats them as context, not enforced configuration（当作背景信息，不是强制执行的设置）。所以验收照样要做。

这份文档（How Claude remembers your project，2026-11-20 核对）还说：开工时读项目文件夹（第 0.1 课选过）和它上面各层的 CLAUDE.md；建议少于 200 行。`my-site` 不在学习工作区里面，也不在它上面，所以导师不读 `my-site/CLAUDE.md`。规矩要能核对，比如“只改我点名的文件”；仓库公开，不写隐私。

规则类型**惯例·平台与工具**（一个工具自己的做法）；约束力**推荐**（适用范围：所有项目），前提是那个项目用 Claude Code。

### 跟我做

练习场里有一份 AI 起草、还没提交的 CLAUDE.md。先验收，再提交。

#### 1. 搭好练习场，看状态

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.15c
cd ~/Developer/playground/1.15c/my-site
git status
```

你应该看到：

```text
练习场景 1.15c 搭好了。
位置：~/Developer/playground/1.15c

这里有什么：
  网站副本：~/Developer/playground/1.15c/my-site（AI 起草的 CLAUDE.md 还没提交）

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.15c
  2. 做完以后回到学习工作区，再运行检查：cd ~/Developer/fullstack-from-zero，然后 python3 tools/course.py check 1.15c

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.15c --reset
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	CLAUDE.md

nothing added to commit but untracked files present (use "git add" to track)
```

> 读懂这句：有一个 Git 没跟踪过的新文件 CLAUDE.md，暂存区里没有东西。

新文件不在 `git diff` 里，用 `cat` 读。检查等「自己做」做完再运行。

#### 2. 读草稿，找出不该有的那一条

```zsh
cat CLAUDE.md
```

你应该看到：

```text
# my-site：给 AI 的项目说明

这是一个只有一页的个人网页，我用它学做软件。仓库是公开的。

## 规矩

- 只改我点名的文件；想顺手改别的，先列出来问我。
- 不新建文件，除非我同意。
- 改完直接提交并推送，不用等我看。
```

最后一条和 AI-01 正好相反：它让 AI 跳过你的验收。

#### 3. 故意出一次错：还没 add 就提交

先猜：不先 `git add`，直接提交，会怎样？

```zsh
git commit -m "docs: 添加给 AI 的项目说明"
```

你应该看到：

```text
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	CLAUDE.md

nothing added to commit but untracked files present (use "git add" to track)
```

> 读懂这句：暂存区是空的，什么都没提交；有一个未跟踪的文件，要跟踪就用 git add。

报错三问：

- **谁在报错？** `git`。没写 error，但什么都没提交。
- **关键词是什么？** nothing added to commit：暂存区是空的。
- **我刚才敲了什么？** 跳过了 `git add`。快照只拍暂存区里的东西。

#### 4. 改掉坏规矩

只改一行，直接打开这个文件（ED-01 的“打开整个文件夹”说的是做项目）。

```zsh
code CLAUDE.md
```

〔对照文档，界面可能不同〕把最后一行改成 `- 改完不要提交，等我看完 git diff 自己提交。`，按 ⌘S 保存。标签页上的圆点消失才算存好（第 1.4 课）；没存好就提交，进去的还是旧的那一行。

#### 5. 提交

AI 起草的，照第 2 站加尾注；说明文字用 `docs` 类型。先说出四个区域的图会怎么变：`CLAUDE.md` 从工作区到暂存区，再到本地历史。

```zsh
git add CLAUDE.md
git commit -m "docs: 添加给 AI 的项目说明" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

你应该看到（编号你的会不一样）：

```text
[main a0ca58e] docs: 添加给 AI 的项目说明
 1 file changed, 9 insertions(+)
 create mode 100644 CLAUDE.md
```

> 读懂这句：新建了提交 a0ca58e；1 个文件改了，加了 9 行；新建了文件 CLAUDE.md。

对一对刚才说的图：

```zsh
git log --oneline -2
```

你应该看到（编号你的会不一样）：

```text
a0ca58e (HEAD -> main) docs: 添加给 AI 的项目说明
5828496 (origin/main) feat: 在页脚加上源代码的链接
```

### 补全

```text
CLAUDE.md 放在仓库的 ______ 目录
每条规矩写成一行，开头是 ______
提交它用的类型：______
```

### 自己做

给你自己的 `~/Developer/my-site` 写一份 CLAUDE.md，里面至少三条**你自己定的**规矩。

1. 想一想前两站里你最想让 AI 记住什么。例子：“改 style.css 之前，先告诉我要改哪一条”“网页上不要出现我的真名、电话和住址”。别照抄课文原句，检查认得出。意思要自己定，措辞可以请 AI 帮着改。
2. 在 `~/Developer/my-site` 里运行 `code CLAUDE.md`，写一个标题，再写至少三条规矩，每条一行，以半角的 `- ` 开头。按 ⌘S 保存。
3. 验收自己的文件：`git status` 确认只多了 CLAUDE.md，`cat CLAUDE.md` 读一遍，里面不写隐私。
4. 提交，类型用 `docs`。AI 起草过或改过措辞，就按 AI-02 加尾注；全是自己写的，不加。
5. 检查会请你选：这份文件全是你自己写的，还是 AI 帮过忙。
- 提示：`python3 tools/course.py hint 1.15c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.15c`

> **想多了解（可跳过）：试试效果**
>
> 〔对照文档，界面可能不同〕在 Claude 应用里新开一个会话，项目文件夹选 `~/Developer/my-site`（点输入框旁边的项目文件夹按钮选），请它做一件和你的规矩有关的小事，看它有没有照做。这个会话不在学习工作区里，没有导师规则，Claude 会照常替你干活。不管它照没照做，改动都照第 1 站验收。

> **想多了解（可跳过）：AGENTS.md**
>
> 跨工具的同类文件叫 `AGENTS.md`：写给各种编程 AI 的说明文件。agents.md 网站说它由 Linux 基金会下的 Agentic AI Foundation（智能体 AI 基金会）管理，有 6 万多个开源项目在用，没有版本号，也没有必填格式（2026-11-19 打开核对）。它的规则类型，按第 0.3 课的七步判断法一步一步问：第 3 步问“它是公开发布、写明版本、很多互不相干的项目和工具都照着做的规范吗”，它没写明版本，所以这一步不停；第 4 步问“它只是某一个工具或平台本身的工作方式或期待吗（包括它在自己的官方文档里教你怎样用它）？”，对你用的 Claude Code 来说是：项目里没有 CLAUDE.md 时去读 AGENTS.md，是它官方文档写明的工作方式。所以在这门课里它是**惯例·平台与工具**；哪天它有了写明版本的规范，就该改成惯例·事实标准。你现在只用 Claude，写 CLAUDE.md 就够了。
>
> **旧教程提醒**：以前的文章说 Claude Code 只认 CLAUDE.md；现在，自 Claude Code v2.1.277 起，项目里没有 CLAUDE.md 时它会读 AGENTS.md，两个都有时默认只读 CLAUDE.md（Claude Code 官方文档 How Claude remembers your project，2026-11-20 核对）。

> **存档点 1.15c**：到这里可以安全停下。下次可以对导师说“从 1.15 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| AI-01 | AI 的改动先看 diff 再接受 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 规范·组织 | 开源安全基金会 OpenSSF 的指南（2025-08-01，这个组织以自己的名义写明，所以是规范·组织）；GitHub Docs；开源编译器项目 LLVM 的 AI 政策；验收顺序是本课程的做法 | 2026-11-20 |
| AI-02 | AI 参与的提交如实署名 | 推荐（适用范围：所有项目）；必须（适用范围：本课程）；项目有自己的 AI 政策时以项目的为准 | 惯例·平台与工具 | Claude Code 文档 Settings reference（设置说明）；GitHub Docs 多作者提交；LLVM、Linux 等开源项目的 AI 政策（卡片里列全） | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 25 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.15`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「AI-01 AI 的改动先看 diff 再接受」「AI-02 AI 参与的提交如实署名」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。

都做完，这一课就完成了。下次可以对导师说“从 1.16 开始”。

## 想多了解

这一节的内容都可以跳过。

为什么这一课值得花时间：会写代码的 AI 越来越普遍，值钱的技能正在变成“说清楚要什么”和“验收交来的东西”。GitHub 研究团队 2025-12-08 发布的访谈（22 位深度使用 AI 的工程师）说，交代任务和核实结果成了他们的主要工作；Stack Overflow 2026 年开发者调查的 AI 一节里，48% 的人说，答案容易核实的时候，他们会信任 AI（原文：trust AI when they can easily validate the answers）。两处都在 2026-11-19 打开核对。

- GitHub 研究文章：The new identity of a developer（AI 时代开发者的工作怎么变了）https://github.blog/news-insights/octoverse/the-new-identity-of-a-developer-what-changes-and-what-doesnt-in-the-ai-era/ （English）
- Claude Code 官方文档：How Claude remembers your project（CLAUDE.md 和 AGENTS.md 怎么读）https://code.claude.com/docs/en/memory （English）
- GitHub Docs：Review AI-generated code（验收 AI 代码时看什么）https://docs.github.com/en/copilot/tutorials/review-ai-generated-code （English）
