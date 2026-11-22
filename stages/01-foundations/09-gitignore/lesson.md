# 1.9 Git：什么不该进仓库

> **用时** 2 站，约 95 分钟 ｜ **前置** 1.8 ｜ **核实** 2026-11-20 · git 2.54.0 · macOS 27.2.1 · zsh 5.9
> **学完你能** 给一个项目写 `.gitignore`，并用命令证明它起了作用；让 Git 放手一个已经提交的文件，而文件留在电脑上；说出密钥泄露以后的第一步。
> **本课行规** REPO-01、REPO-02（见文末）

## 先想一想

你要把书桌拍一张照片发到网上。拍之前，你会先把哪三样东西拿开？想好三样，第 1 站的“概念”讲完以后对一对。

## 第 1 站：给 Git 一份不拍名单（约 40 分钟）

### 概念

仓库里放**源文件（source file）**：你亲手写的、别人重建项目必须拿到的文件。三类东西不该进仓库：

- **能重新生成的**：程序自己产生的缓存（为了下次更快而存下的中间文件），比如 Python 的 `__pycache__/` 文件夹。
- **私密的**：**密钥（secret）**，拿到就能冒充你“开门”的一串字符。比如密码；接口密钥（API key），你的程序拿它到网站的接口（留给程序取数据的入口）取数据；令牌（token），代替密码的通行证，可以单独作废。它们常放在隐藏文件 `.env` 里。
- **太大的**：视频、大数据文件。GitHub（存放代码仓库的网站，第 1.11 课注册）拒收大约 100 MB 以上的文件。

对一对“先想一想”：钥匙是私密的，饮料瓶随时能再有，一箱旧杂志太大。

项目最外层的 **`.gitignore`** 文件就是给 Git 的“不拍名单”（也叫忽略文件）。每行一条模式（pattern，第 1.3 课学过），常用三种：

| 写法 | 意思 | 例子 |
|---|---|---|
| 一个名字 | 叫这个名字的文件或文件夹 | `.env` |
| 名字加斜杠 | 只指这个文件夹，连同里面的一切 | `__pycache__/` |
| 星号加扩展名 | 所有以这个扩展名结尾的文件 | `*.bak` |

以 `#` 开头的行是写给人看的说明，Git 不管。

类比：拍照前说好“这几样不入镜”。这个类比在哪里不成立：已经拍进照片的，事后加进名单也不会消失（第 2 站）。

在图上，名单管 `git add` 这一步：名单里的文件不会被放上打包台。

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

（远程和 `git push` 以后再讲。）

### 跟我做

#### 1. 一个乱糟糟的练习项目

回到学习工作区：`cd ~/Developer/fullstack-from-zero`，然后搭练习场景：

```zsh
python3 tools/course.py scenario 1.9-demo
```

你应该看到：

```text
练习场景 1.9-demo 搭好了。
位置：~/Developer/playground/1.9-demo

这里有什么：
  练习项目在这里：~/Developer/playground/1.9-demo/hello-fx
  先进去：cd ~/Developer/playground/1.9-demo/hello-fx
  旁边的 weather 是第 2 站才用的仓库，现在先不用管它。

接下来：
  1. 回到学习工作区：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.9-demo --reset
```

照“这里有什么”里那条 `cd` 进去：

```zsh
cd ~/Developer/playground/1.9-demo/hello-fx
```

这是 0.1 课换算小程序的一个仓库，多了五样没跟踪的东西：笔记 `notes.md`（该进仓库）、装着假密钥的 `.env` 和 `secret-token.txt`、缓存 `__pycache__/`、旧备份 `rates.txt.bak`。一句 `git add .`（点 = 这里的一切）就会把它们全放上打包台。

#### 2. 写项目自己的名单

〔对照文档，界面可能不同〕用 VS Code 打开 `.gitignore`：

```zsh
code .gitignore
```

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

打开的是空白编辑页，按 ⌘S 保存时文件才建好。

页面不是空白的：你不在 hello-fx 里，别保存，关掉它，先 `cd` 进去。

已经保存了，下一步 Git 才说 `not a git repository`：也是没进 hello-fx。打开时页面上原来就有字（多半是学习工作区自己的 `.gitignore`），在那个标签页里按 ⌘Z 一步步撤回刚加的四行，再按 ⌘S。然后 `cd` 进去，从 `code .gitignore` 重做。

这里只写一个小文件，单独打开它也行；正经做项目还是按 ED-01 用 `code .` 打开整个文件夹。

输入四行，按 ⌘S：

```gitignore
.env
secret-token.txt
__pycache__/
*.bak
```

星号、斜杠、点要用英文半角，全角的 `＊` `／` `．` Git 不认。命令里也一样：中文输入法有时会把 `--` 打成 `——`，`git status ——ignored` 不报错，却说 `working tree clean`（干净）。输出比课文少（说干净、只有文件名或什么也没有），先查横线和点。

先说出哪几样会被挡住，再看 `git status` 加上 `--ignored`，把被挡住的也列出来：

```zsh
git status --ignored
```

你应该看到：

```text
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore
	notes.md

Ignored files:
  (use "git add -f <file>..." to include in what will be committed)
	.DS_Store
	.env
	__pycache__/
	rates.txt.bak
	secret-token.txt

nothing added to commit but untracked files present (use "git add" to track)
```

> 读懂这句：`Untracked files` 是“还没跟踪的文件”，`Ignored files` 是“被名单挡住的文件”，括号里说 `git add -f`（force，强行）能硬塞进去：别对密钥这么做。

`.env` 还在 Untracked files 下？多半没保存：标签上文件名旁的圆点就是“没保存”。

未跟踪的只剩该进仓库的两个。`.DS_Store` 是访达（Finder）放的文件。上面的输出来自一台设置过全局忽略文件（global ignore file）的电脑：那份名单（比如 `~/.gitignore_global`）里写了 `.DS_Store`，所以它在 Ignored files 下。你的电脑没设置过的话，它会排在 Untracked files 下，这一站先不用管它。全局忽略文件只在设置它的那台电脑上有效，别人的电脑上没有它，所以密钥和缓存要写进跟着仓库走的 `.gitignore`。名单一保存就生效，它自己也要提交。

#### 3. 问是谁挡的

`git check-ignore -v` 告诉你一个文件被哪条规则挡住（check-ignore = 检查是否被忽略，`-v` = verbose，说详细一点）：

```zsh
git check-ignore -v secret-token.txt
```

你应该看到：

```text
.gitignore:2:secret-token.txt	secret-token.txt
```

> 读懂这句：冒号隔开的三段是“哪个文件 : 第几行 : 哪条规则”，空白后面是你问的文件。

没被挡住的文件，它什么也不输出。

#### 4. 故意出个错

只敲命令，不写文件名：

```zsh
git check-ignore -v
```

你应该看到：

```text
fatal: no path specified
```

用报错三问读它：

- 谁在报错？没写程序名，但这是你刚敲的 `git`。`fatal` 表示没做成。
- 关键词是什么？`no path specified`：没有指定路径。
- 我刚才敲了什么？`git check-ignore -v`，少了文件名。

### 补全

在纸上或心里填空，再和“概念”里的表对一对：

```gitignore
# 所有 .zip 压缩包
____
# 一个叫 logs 的文件夹
____
```

### 自己做

换成你自己的网站 `~/Developer/my-site`。它第 1.13 课会公开，草稿不能进去。

目标：

1. 在 `my-site` 里建一个 `drafts` 文件夹，里面放一个空的笔记文件 `colors.md`（用 `mkdir`（第 0.2 课）和 `touch`（第 1.1 课）；名字用小写英文，WS-02）。
2. 第 1.7 课你把标题颜色改成了 `#c2410c`。再挑一个颜色，比如 `#2a7f62`（一种绿色），改掉 `style.css` 里 `h1` 下面 `color:` 后面的值，保存。
3. 写 `my-site` 自己的 `.gitignore`（按 ED-01 先 `code .`）：`drafts` 文件夹、所有 `.tmp` 文件、`.env` 文件都不进仓库。
4. 新颜色和 `.gitignore` 分两次提交（为什么，第 1.10 课讲），说明写“换了一个标题颜色”和“添加 .gitignore”。做完 `git status` 是干净的。如果 `git status` 还列着 `.DS_Store`（说明你的电脑没设置全局忽略文件），把 `.DS_Store` 也写进这份 `.gitignore`。

检查会问：挡住草稿的规则在 `.gitignore` 第几行。用这一站的命令查。

- 提示：`python3 tools/course.py hint 1.9a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.9a`

> **存档点 1.9a**：到这里可以安全停下。下次可以对导师说“从 1.9b 继续”。

## 第 2 站：已经进了仓库怎么办（约 40 分钟）

### 概念

名单只管没被跟踪的文件。进过提交的文件是已跟踪的（第 1.8 课：Git 手里有它的版本），写进名单也照样被管。

让 Git 放手、文件留在电脑上，叫**取消跟踪（untrack）**：`git rm --cached <文件>`，`--cached` = 只动暂存区。文件夹加 `-r`（同 1.2 课）：`git rm -r --cached <文件夹>`。

小心：漏了 `--cached`，文件会从电脑上也删掉。没提交的话用第 1.8 课的两步找回：`git restore --staged <文件>`，再 `git restore <文件>`。

在图上，文件离开暂存区，下一张快照里没有它；但**本地历史里的旧快照不会变**。

类比：照片已经进了相册，从今天起不拍它，旧照片还在。这个类比在哪里不成立：相册能撕页，Git 的历史很难改，别人复制走的更改不了。所以密钥进过一次提交，就当它已经泄露。

### 跟我做

#### 1. 一个提交过密钥的仓库

进 weather 仓库（找不到它，就回到学习工作区：`cd ~/Developer/fullstack-from-zero`，再运行第 1 站的 `scenario` 命令），看 Git 跟踪着哪些文件（ls-files = list files）。先猜：会列出 `.gitignore` 吗？

```zsh
cd ~/Developer/playground/1.9-demo/weather
git ls-files
```

你应该看到：

```text
.env
index.html
```

这里有一份没提交的 `.gitignore`，写着 `.env`，可 `.env` 照样被跟踪：它早就提交过，名单管不到。Git 手册 gitignore 里写着 Files already tracked by Git are not affected（已经被跟踪的文件不受影响）。

#### 2. 故意出个错，再让 Git 放手

故意漏掉隐藏文件名前的点：

```zsh
git rm --cached env
```

你应该看到：

```text
fatal: pathspec 'env' did not match any files
```

报错三问：谁在报错？`git`。关键词？`did not match any files`：你写的路径（pathspec）env 对不上任何文件。我敲了什么？`env`，少了点。（在别的仓库里敲也是这一句；在不是仓库的文件夹里，看到的是 `fatal: not a git repository`：先 `cd` 进 weather。）

没伤害任何东西。补上点，先说出图会怎么变：

```zsh
git rm --cached .env
git status
```

你应该看到：

```text
rm '.env'
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	deleted:    .env

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore

```

> 读懂这句：`rm '.env'` 是“从暂存区拿掉了 .env”；`deleted: .env` 是“下一个提交会去掉它”。它不在 Untracked files 里：名单这次挡住了它。

`.env` 本身还在电脑上。

#### 3. 提交，然后翻历史

```zsh
git add .gitignore
git commit -m "不再跟踪 .env"
```

你应该看到（你的会不一样：提交编号）：

```text
[main e217232] 不再跟踪 .env
 2 files changed, 2 insertions(+), 1 deletion(-)
 delete mode 100644 .env
 create mode 100644 .gitignore
```

> 读懂这句：`delete mode` 是“离开仓库”，`create mode` 是“进了仓库”。

先说出图会怎么变，再看：

```zsh
git status
```

你应该看到：

```text
On branch main
nothing to commit, working tree clean
```

用 1.7 课的 `git show` 看最新的提交（不写编号就是最新的）：

```zsh
git show
```

你应该看到（你的会不一样：编号、名字和时间）：

```text
commit e2172320ada0f9042c1e30a0f87882b5f78e7001
Author: 你的名字 <you@example.com>
Date:   Fri Nov 20 08:30:20 2026 +0800

    不再跟踪 .env

diff --git a/.env b/.env
deleted file mode 100644
index 7ebbf2c..0000000
--- a/.env
+++ /dev/null
@@ -1 +0,0 @@
-WEATHER_API_KEY=demo-7c2e-not-a-real-key
diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000..7d4625c
--- /dev/null
+++ b/.gitignore
@@ -0,0 +1,2 @@
+# 密钥，永远不进仓库
+.env
```

> 读懂这句：`deleted file mode` 是“删掉了这个文件”，`+++ /dev/null` 是“改之后什么也没有”（/dev/null 是永远空着的特殊文件）。

减号那一行就是密钥全文：连这个“不再跟踪”的提交都记下了它，谁拿到仓库都能看到。（停在冒号或 `(END)` 就按 q 退出。）

#### 4. 真的泄露了，先做什么

密钥是真的话，顺序是（GitHub 的官方文档 GitHub Docs 和做网络安全的非营利组织 OWASP 说法一致）：

1. **先作废密钥（revoke）**：〔对照文档，界面可能不同〕在发密钥的网站（“API keys”“Tokens”一类的设置页）让它失效，换个新的（rotate）。只有这一步让它开不了门。
2. **再让 Git 放手**：写进名单，`git rm --cached`，提交。
3. **清理历史**是进阶操作，这里不教；别人复制走的还有，它代替不了第 1 步。

这就是行规 REPO-01（见文末）。

### 补全

让 Git 放手一个已经提交的 `notes.tmp`，填上空（不用真的做）：

```text
1. 在 .gitignore 里加一行：____
2. 让 Git 放手，文件留在电脑上：git rm ____ notes.tmp
3. git add .gitignore，再提交
```

### 自己做

```zsh
cd ~/Developer/fullstack-from-zero
python3 tools/course.py scenario 1.9b
```

照“这里有什么”的 `cd` 进去。这个相册仓库提交过两样不该进去的东西：一个密钥文件，一个能重新生成的缩略图文件夹。

目标：

1. 找出是哪两样。
2. 让 Git 不再跟踪它们，以后也不再提醒；它们本身留在电脑上。
3. 把改动提交，`git status` 是干净的。

检查最后有一道选择题：密钥是真的，第一步做什么。

- 提示：`python3 tools/course.py hint 1.9b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.9b`

> **存档点 1.9b**：到这里可以安全停下。下次可以对导师说“从 1.9 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| REPO-01 | 密钥、密码、令牌永不入库；进去了先作废 | 必须（适用范围：所有项目） | 惯例·事实标准（OWASP ASVS：公开、带版本号的安全要求清单） | OWASP 应用安全验证标准（ASVS）5.0.0 第 13.3.1 条（第 2 级）；GitHub Docs | 2026-11-20 |
| REPO-02 | `.gitignore` 从官方模板起步，再补自己的几行 | 推荐（适用范围：所有项目） | 惯例·平台与工具 | github/gitignore 模板库；Git 手册 gitignore | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

REPO-01 的类型是“惯例·事实标准”：ASVS 把要求分三级，这一条在第 2 级；ASVS 说大多数应用都该努力做到这一级，做到哪一级由各家按风险决定。你自己的项目里没人能因它罚你，本课程仍定为所有项目都必须：后果收不回，别人拿到密钥就能冒用你的账号、花你的钱。合同或公司制度写了这一条时，那条条款是行业要求，ASVS 的类型不变（第 0.3 课）。

往**公开仓库**（谁都能看的仓库）推送（传到 GitHub 上，第 1.12 课学）时，GitHub 的**推送保护（push protection）**默认拦下认得出的密钥〔对照文档，界面可能不同〕。它是工具，不是处罚：你能放行，认不出的照样推上去。

REPO-02：GitHub 的官方模板库 github/gitignore 按语言整理好了模板，有就从它起步，再补自己的几行；`my-site` 没有对应的，从最少的几行开始。

## 收尾（约 15 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.9`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「REPO-01 密钥、密码、令牌永不入库」「REPO-02 .gitignore 从官方模板起步」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 1.10 开始”。

## 想多了解

下面的内容都可以跳过。

- 你的电脑有没有全局名单：运行 `git config get core.excludesfile`。有输出（比如 `~/.gitignore_global`），就是设置过，用 `cat` 加这个文件名能看到里面的每一行，Mac 上常见的有 `.DS_Store`、`._*`、`.Spotlight-V100`、`.Trashes`；什么也不输出，多半是没设置过（Git 还会看一个默认位置 `~/.config/git/ignore`，这个文件一般不存在）。名单里写了 `.DS_Store` 的，在 hello-fx 里运行 `git check-ignore -v .DS_Store`，会看到挡住它的是这个文件的哪一行（文件名前面是你主文件夹的完整写法）。GitHub 的准确说法是拒收超过 100 MiB 的文件（MiB 是按 1024 进位的兆字节，100 MiB 约 105 MB），超过 50 MiB 的会先给警告。文件名里有中文时，Git 会显示成 `"drafts/\351\242\234…"` 这样的编码，这也是 WS-02 要你用小写英文起名的一个原因。
- github/gitignore 官方模板库（English）：https://github.com/github/gitignore 。`Global` 文件夹里是操作系统和编辑器的模板（比如 `macOS.gitignore`），说明里建议把它们放进全局名单，或者合进项目的模板。
- Git 手册 gitignore，写法的全部细节（English）：https://git-scm.com/docs/gitignore
- 旧教程提醒：以前很多教程教用 `git filter-branch` 或 BFG（改写历史的工具）把密钥删掉就算完；现在 Git 自 2.24（2019 年）起不鼓励 filter-branch，GitHub Docs 改用 git-filter-repo（现在推荐的改写历史工具），而且第一步是作废密钥。完整流程见 GitHub Docs「Removing sensitive data from a repository」（English）：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
