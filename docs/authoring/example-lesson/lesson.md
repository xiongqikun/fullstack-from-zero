# 99.1 示例课：给练习仓库加一份说明

> **用时** 2 站，约 55 分钟 ｜ **前置** 无 ｜ **核实** 2026-11-20 · git 2.54.0 · python3 3.14.9
> **学完你能** 读懂 `git log --oneline` 的每一行；在练习仓库里加一个文件并提交
> **本课行规** EX-01 练习只在练习场里做（见文末）

这不是课程里的一课。它是写给建课的人看的示例课文：和 `lesson.py`、`rules.md` 放在一起，演示课文的每一个固定写法（`docs/authoring/lesson-template.md`）。

## 先想一想

玩游戏时你存过档吗？存档留下了哪两样东西？第 1 站末尾对一对你的答案。

## 第 1 站：提交是什么（约 15 分钟）

### 概念

**提交（commit）**：给项目当前的样子拍一张带说明的快照。

它像游戏存档：记下那一刻的全部进度，还能给存档起个名字。这个类比在哪里不成立：游戏一般自动存全部进度，提交只拍你事先挑好、放进暂存区的那些改动（第 2 站讲）。

### 跟我做

#### 1. 搭一个练习仓库

回到学习工作区：`cd ~/Developer/fullstack-from-zero`

```zsh
python3 tools/course.py scenario 99.1
```

你应该看到（`notes-` 后面的词每次随机，你的会不一样）：

```text
练习场景 99.1-start 搭好了。
位置：~/Developer/playground/99.1-start

这里有什么：
  练习仓库在这里：~/Developer/playground/99.1-start/notes-coral
  先进去看一看：cd ~/Developer/playground/99.1-start/notes-coral，然后运行 git log --oneline

接下来：
  1. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 99.1 --reset
```

#### 2. 看历史

先猜一猜：下面这条命令会打印几行？

```zsh
cd ~/Developer/playground/99.1-start/notes-coral
git log --oneline
```

你应该看到（编号、说明和行数，你的会不一样）：

```text
07915ba docs: 记录一次排错
16cdfde docs: 写下本周计划
```

每一行是一次提交：左边是编号，右边是那次写的说明。最新的在最上面。

### 补全

照着上面的样子，把空填上：

```text
看每个提交一行的简短历史：git log ________
```

### 自己做

目标：答对检查问你的两道题：提交是什么，`git log --oneline` 的一行代表什么。

- 提示：`python3 tools/course.py hint 99.1a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 99.1a`

> **存档点 99.1a**：到这里可以安全停下。下次可以对导师说“从 99.1b 继续”。

## 第 2 站：加一份说明并提交（约 20 分钟）

### 概念

**暂存区（staging area）**：提交之前，放“这一次要拍进快照的改动”的地方。`git add` 把改动放进去，`git commit` 把里面的东西拍成快照。

它像打包台：决定哪些东西装进这一箱。这个类比在哪里不成立：装箱以后再改文件，箱里还是旧的，要重新放一次。

### 跟我做

#### 1. 故意敲错一次

先猜一猜：给 `git add` 一个不存在的文件名，会怎样？

```zsh
git add READ.md
```

你应该看到：

```text
fatal: pathspec 'READ.md' did not match any files
```

> 读懂这句：fatal（致命错误，命令停下了）：你给的名字 READ.md 对不上任何文件。

用“报错三问”读一遍：

- **谁在报错？** Git：开头的 `fatal:` 是 Git 的写法。
- **关键词是什么？** `did not match any files`：没有对得上的文件。
- **我刚才敲了什么？** `READ.md`，少了 `ME`。

#### 2. 放进暂存区

新建 `README.md`，第一行写 `# 我的笔记`，保存。再运行：

```zsh
git add README.md
git status
```

你应该看到：

```text
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	new file:   README.md
```

> 读懂这句：Changes to be committed 是“准备提交的改动”：README.md 已经在暂存区里了。

### 补全

```text
1. 把文件放进暂存区：git ________ README.md
2. 拍成快照：git commit -m "________"
```

### 自己做

目标：在练习仓库里，`README.md` 的第一行是一级标题，它已经提交，仓库里没有落下没提交的改动。检查最后会问你：动手之前，仓库里有几个提交？

- 提示：`python3 tools/course.py hint 99.1b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 99.1b`

> **存档点 99.1b**：到这里可以安全停下。下次可以对导师说“从 99.1 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| EX-01 | 练习只在练习场里做 | 必须（适用范围：本课程） | 规范·本课程约定 | 本课程示例课 docs/authoring/example-lesson（2026-11-19 版） | 2026-11-19 |

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 20 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 99.1`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「EX-01 练习只在练习场里做」下面用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。

都做完，这一课就完成了。下次可以对导师说“从 99.2 开始”。

## 想多了解

下面的内容都可以跳过，不算进本课的时间。

- 《Pro Git》第 2 版中文版第 2 章「Git 基础」：https://git-scm.com/book/zh/v2
