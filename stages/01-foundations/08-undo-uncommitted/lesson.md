# 1.8 Git：后悔药

> **用时** 2 站，约 90 分钟 ｜ **前置** 1.7 ｜ **核实** 2026-11-20 · git 2.54.0 · macOS 27.2.1 · zsh 5.9
> **学完你能** 把一个改乱了、还没提交的文件变回上次存档的样子；把误放进暂存区的改动拿下来，文件内容不变；看一眼 `git status` 就说出该用哪条命令。
> **本课行规** GIT-04（见文末）

这一课只管**还没提交**的改动。已经提交了怎么改、丢了的提交怎么找回来，放在阶段 2 再学。

## 先想一想

你有一份昨天复印好的存档。今天你在原件上乱涂了几笔，就拿昨天的复印件整张盖上去，当作新的原件。

- 今天乱涂的那几笔还在吗？
- 如果今天你还在原件上写了几行有用的字，它们还在吗？

先在心里答一下，第 1 站的概念讲完以后回头对答案。

## 第 1 站：丢掉工作区里的修改（约 40 分钟）

### 概念

第 1.6 课的四区域图，这一课还用它：

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

（远程和 `git push` 以后再讲。）

到现在为止，箭头都往右走。这一课学两条往左走的路：

```text
   工作区  ◀──────────  暂存区  ◀──────────  本地历史
        git restore 文件     git restore --staged 文件
          （第 1 站）            （第 2 站）
```

`git restore 文件名`（restore = 恢复）用暂存区里的版本盖掉工作区里的这个文件。改动还没 `git add` 的文件，暂存区里放的就是上次提交的版本，所以效果是**文件回到上次提交时的样子**。这叫丢弃修改（discard changes）。

打个比方：提交像游戏存档，`git restore` 像给这一个文件“读档”。这个类比在哪里不成立：游戏读档是整个进度一起退；`git restore` 只退你点名的文件。

最要紧的一句：**没 `git add` 过的改动，Git 手里没有副本，`git restore` 一盖就再也找不回来。** 所以它是一条会丢数据的命令（destructive command）。

回头对答案：乱涂的没了，有用的那几行也没了，因为复印件是整张盖上去的。`git restore` 也是整个文件一起盖。

### 跟我做

#### 1. 搭练习场景

先回到学习工作区，搭好这一课的练习场景：

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.8
```

屏幕上的说明里，你要找的是这两行：

```text
这里有什么：
  进入网站副本：cd ~/Developer/playground/1.8-start/my-site
  这是练习用的副本，你真正的 my-site 不受影响。
```

这一站和下一站都在这份副本里练，照「进入网站副本」那一行进去：

```zsh
cd ~/Developer/playground/1.8-start/my-site
```

#### 2. 模拟一次手滑

假设你想复制一份样式表做实验，手一快，把目标写成了 `index.html`。`cp` 遇到同名的目标会直接盖掉，不问你：

```zsh
cp style.css index.html
```

现在 `index.html` 里装的是样式表，网页没了。好在这里是仓库，还有救。

#### 3. 先看状态

先说出执行后图会怎么变：`index.html` 现在在哪个区域有改动？

```zsh
git status
```

你应该看到：

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   index.html

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：你在 main 上（第 1.6 课说的分支，现在不用管）。有改动还没放进暂存区。括号里第二行：用 “git restore <file>…” 丢掉工作区里的改动（`<file>` 是第 1.7 课见过的占位写法，真敲时换成文件名，不带尖括号）。已修改：index.html。最后一行：还没有改动放进下一次提交（`git commit -a` 这门课不用）。

不知道怎么办时，先读 `git status` 括号里的话：Git 把能用的命令写在那里。

#### 4. 再看会丢掉什么

动手之前，先用第 1.7 课的 `git diff` 看清会丢掉什么：

```zsh
git diff index.html
```

你应该看到（输出很长；如果屏幕底下出现冒号 `:` 或 `(END)`，那是分页器，看完按 `q` 退出）：

```text
diff --git a/index.html b/index.html
index 3e927d1..7cd4dc1 100644
--- a/index.html
+++ b/index.html
@@ -1,26 +1,12 @@
-<!DOCTYPE html>
-<html lang="zh-CN">
-<head>
-  <meta charset="utf-8">
-  <meta name="viewport" content="width=device-width, initial-scale=1">
-  <title>我的第一个网页</title>
-  <link rel="stylesheet" href="style.css">
-</head>
-<body>
-  <main>
-    <h1>你好，我是阿北</h1>
+/* 网页的样式：改一个值，保存，再刷新浏览器，就能看到变化。 */
+body {
+  max-width: 40rem;
+  margin: 2rem auto;
+  padding: 0 1rem;
+  font-family: system-ui, sans-serif;
+  line-height: 1.7;
+}
 
-    <p>我想把学到的东西一点一点放到这里。</p>
-
-    <ul>
-      <li>我会用终端管理文件</li>
-      <li>我会用 Git 记录每一次改动</li>
-      <li>我会把网页放到网上</li>
-    </ul>
-  </main>
-
-  <footer>
-    我常查的网页资料：<a href="https://developer.mozilla.org/zh-CN/">MDN</a>
-  </footer>
-</body>
-</html>
+h1 {
+  color: #0b5cad;
+}
```

「你的会不一样」：`index` 后面第一串编号、标题里的名字和那一段话，每个人的副本都不同。

不用逐行读，只看每行开头：`-` 行是存档里原来有的，`git restore` 以后会回来；`+` 行是现在多出来的，以后会消失，找不回来；开头是空格的行两边一样。这里 `+` 行是样式表的复制品，丢了无所谓。确认了，再动手。

#### 5. 丢掉这处改动

先猜：下面这条命令执行成功时，会打印什么？

```zsh
git restore index.html
```

你应该看到：什么也没有，直接回到提示符。成功了就不说话。再看状态：

```zsh
git status
```

你应该看到：

```text
On branch main
nothing to commit, working tree clean
```

> 读懂这句：没有可以提交的改动，工作区是干净的。

网页回来了。被盖掉的那份样式表再也找不回来：Git 从来没存过它。这次丢的是复制品；可如果那是你写了一下午、还没 `git add` 的内容，它也会这样无声无息地消失。这就是本课行规 GIT-04 要防的事。

#### 6. 故意出错一次

文件名少打一个字母：

```zsh
git restore index.htm
```

你应该看到：

```text
error: pathspec 'index.htm' did not match any file(s) known to git
```

> 读懂这句：错误：你写的路径 'index.htm' 和 Git 认识的任何文件都对不上。（pathspec 是 Git 对“写在命令后面的文件名”的叫法。）

用报错三问读它：

1. **谁在报错？** Git（开头的 `error:`）。
2. **关键词是什么？** `did not match any file(s) known to git`：Git 不认识这个文件。
3. **我刚才敲了什么？** `index.htm`，少了 `l`。

Git 只认识它跟踪（track）的文件：你 `git add` 过、它手里有版本的文件。从没 `git add` 过的新文件也会报这一句。

> **旧教程提醒**：《Pro Git》（Git 官方网站上的书）中文版至今写的是旧写法：丢弃修改写 `git checkout -- 文件名`，取消暂存（第 2 站讲）写 `git reset HEAD 文件名`（HEAD 是第 1.6 课 `git log` 里见过的“你现在在这里”）。现在 Git 在 `git status` 里提示的是 `git restore 文件名` 和 `git restore --staged 文件名`（自 Git 2.23 起，2019 年）。旧写法还能用，`git checkout --` 同样找不回来；`git reset` 换了选项会丢改动、甚至挪动历史，阶段 2 才学，现在别碰。

### 补全

下面是“看、看、丢、看”的骨架。先在心里填上横线（跟我做第 3 到 5 步里都有），自己做就照它来：

```text
git ______                 # 看：哪些文件改了
git ______ 文件名          # 看：这个文件会丢掉什么（底下出现 : 或 (END) 就按 q 退出）
git ______ 文件名          # 丢：只点名要丢的那个文件
git ______                 # 看：确认它不在改动列表里了
```

### 自己做

换一个仓库：小咖啡店的说明文件。两个文件都改过、都没 `git add`，一个改动是想要的，一个是手滑弄乱的：先看清楚，只丢掉弄乱的那个，不要提交。

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.8a
```

照屏幕上「进入练习仓库」那一行 `cd` 进去。git 要是说 `fatal: not a git repository (or any of the parent directories): .git`（这里和上面的文件夹都不是 Git 仓库），就是还没进去。想要的那处也丢了，就重搭一份再来：`python3 tools/course.py scenario 1.8a --reset`。

做完回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.8a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.8a`

> **存档点 1.8a**：到这里可以安全停下。下次可以对导师说“从 1.8b 继续”。

## 第 2 站：从暂存区拿下来，以及哪种情况用哪个（约 40 分钟）

### 概念

第 1.6 课的类比：暂存区是打包台，决定哪些东西装进下一箱（下一个提交）。

有时你把东西放上了打包台，又发现这次不该装箱：还没写完，或者放错了。把它拿回书桌、东西本身不动，这叫取消暂存（unstage）：

```zsh
git restore --staged 文件名
```

`--staged` 的意思是“这次恢复的是暂存区”：用上次提交的版本盖掉暂存区里的这个文件，工作区的文件一个字不碰，所以它**不会丢数据**。

这个类比在哪里不成立：打包台上放的是 `git add` 那一刻的一份拷贝，不是文件本身；“拿下来”是把那一格恢复成上次存档的样子，书桌上的文件从没动过。

### 跟我做

回到网站副本里练：

```zsh
cd ~/Developer/playground/1.8-start/my-site
```

#### 1. 更糟的手滑：盖掉了，还 git add 了

```zsh
cp style.css index.html
git add index.html
```

先说出执行后图会怎么变：被盖掉的 `index.html` 现在到了哪个区域？

```zsh
git status
```

你应该看到：

```text
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   index.html

```

> 读懂这句：有改动准备提交了。括号里：用 “git restore --staged <file>…” 取消暂存。已修改：index.html。

#### 2. 先从暂存区拿下来

先猜：现在直接 `git restore index.html` 有用吗？看图：它用**暂存区**的版本盖工作区，可暂存区里已经是坏的那份，盖了也不变。所以先拿下来，先说出执行后图会怎么变：

```zsh
git restore --staged index.html
git status
```

你应该看到（第一条成功时什么也不打印）：

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   index.html

no changes added to commit (use "git add" and/or "git commit -a")
```

> 读懂这句：`index.html` 从 “Changes to be committed”（准备提交）挪到了 “Changes not staged for commit”（改了、还没放进暂存区）。

#### 3. 看清会丢什么，然后丢掉

照 GIT-04，丢之前先看会丢什么：

```zsh
git diff index.html
```

你应该看到：又是第 1 站第 4 步那段长对比（开头一样是 `diff --git a/index.html b/index.html`）：`--staged` 没碰文件。认出来就行，不用重读（底下出现冒号或 `(END)` 就按 `q`）。然后丢掉，再看状态：

```zsh
git restore index.html
git status
```

你应该看到：

```text
On branch main
nothing to commit, working tree clean
```

网页回来了。

#### 4. 故意出错一次

忘了写文件名：

```zsh
git restore --staged
```

你应该看到：

```text
fatal: you must specify path(s) to restore
```

> 读懂这句：致命错误：你必须指定要恢复的路径。

用报错三问读它：

1. **谁在报错？** Git。`fatal:` 是它最重的一级报错；这一次什么都没改。
2. **关键词是什么？** `must specify path(s)`：必须写出文件名。
3. **我刚才敲了什么？** `--staged` 后面没有文件名。

另外，`--staged` 是两个半角短横线；打成全角 `－－staged` 或长破折号 `—staged`，会报第 1 站那句 `did not match`。

### 哪种情况用哪个

先看 `git status` 里文件列在哪一段，再查表：

| 我想撤销的是…… | `git status` 里它在哪一段 | 用哪条命令 | 文件里的内容 |
|---|---|---|---|
| 还没 `git add` 的改动，不要了 | Changes not staged for commit | 先 `git diff 文件名` 看清，再 `git restore 文件名` | 回到存档的样子，丢的找不回 |
| 已经 `git add` 了，这次先不提交，内容要留着 | Changes to be committed | `git restore --staged 文件名` | 不变 |
| 已经 `git add` 了，改动也不要了 | Changes to be committed | 先 `git restore --staged 文件名`，再 `git diff 文件名` 看清，最后 `git restore 文件名` | 回到存档的样子，丢的找不回 |

### 补全

新文件被误放进暂存区，也一样。第四行的横线上填好再敲：它要让 about.html 不进下次提交，文件留着。

```zsh
cp index.html about.html
git add about.html
git status
git ______ about.html
git status
```

第一次 `git status` 看 about.html 列在哪一段，你应该看到：

```text
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	new file:   about.html

```

> 读懂这句：准备提交的改动：新文件（new file）：about.html。

填对以后，第二次 `git status` 看它挪到了哪一段，你应该看到：

```text
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	about.html

nothing added to commit but untracked files present (use "git add" to track)
```

> 读懂这句：未跟踪的文件：about.html（括号里：用 git add 把它加进下一次提交）。最后一行：没有改动准备提交，但有未跟踪的文件（可以用 git add 开始跟踪）。

`about.html` 还在文件夹里，留着不用管。

> **想多了解（可跳过）：这个新文件要是也不要了**
>
> `git restore about.html` 帮不上忙：Git 手里没有它的版本，会报第 1 站那句 `did not match`。要删它得用第 1.2 课的 `rm`，删之前照第 1.2 课的行规 TERM-02 先看清楚要删什么。

### 自己做

换一个仓库：一份旅行计划，三个文件，三种结局，哪个是哪种搭好后屏幕上会写。不要提交。

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.8b
```

照「进入练习仓库」那一行 `cd` 进去再做。要留着的内容丢了，就重搭一份再来：`python3 tools/course.py scenario 1.8b --reset`。

做完回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.8b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.8b`

> **存档点 1.8b**：到这里可以安全停下。下次可以对导师说“从 1.8 的收尾继续”。

## 本课行规

你在第 1 站第 5 步已经体会过它要防的事：`git restore` 成功时一声不响，被盖掉的内容 Git 里没有副本。

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| GIT-04 | 运行 `git restore 文件名` 这类会丢掉没提交改动的命令之前，先 `git status` 看哪些文件改了，再 `git diff 文件名` 看清会丢掉什么，确认以后只点名要丢的那个文件 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 规范·本课程约定 | 本课程约定；依据 Git 手册 git-restore（网页版最近一次修改在 Git 2.55.0）和《Pro Git》第 2 版英文版 2.4 节 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

为什么是这两种约束力：Git 官方网站上的书《Pro Git》说 `git restore` 加文件名是一条危险的命令，但没有规定“丢之前先看 status 和 diff”这个步骤；这个步骤是这门课定的，所以规则类型是**规范·本课程约定**，在本课程里是**必须**。以后在你自己的仓库里，没人检查你，但它防的损失是真的，所以对所有项目是**推荐**。

## 收尾（约 10 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.8`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「GIT-04 执行会丢数据的命令前先看状态」下面用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 1.9 开始”。

## 想多了解

这一节的内容都可以跳过，不影响后面的课。

- English：Git 官方手册 git-restore https://git-scm.com/docs/git-restore
- English：《Pro Git》第 2 版 2.4 撤消操作，有 `git restore` 一节 https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things
- 中文：《Pro Git》中文版 2.4 撤消操作，用的是旧写法 `git checkout --` 和 `git reset HEAD`，对照着读 https://git-scm.com/book/zh/v2/Git-基础-撤消操作
