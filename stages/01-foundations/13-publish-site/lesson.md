# 1.13 把你的网页放到网上

> **用时** 3 站，约 135 分钟 ｜ **前置** 1.12 ｜ **核实** 2026-11-20 · git 2.54 · macOS 27.2 · GitHub 网站和 gh 的步骤对照官方文档
> **学完你能** 给 my-site 加上许可证，让它成为一个合格的公开仓库；用 GitHub Pages 得到一个手机能打开的网址；改一处、推送，亲眼看到网上的网页跟着变。
> **本课行规** PUB-01（见文末）

这是你第一次做出能拿给别人看的东西。到这一课结束，你会有一个自己的网址。

## 先想一想

你在网上看到一张很好看的照片，下面没写任何说明。你可以把它印在自己卖的 T 恤上吗？如果照片下面写着“随便用，注明作者就行”，又怎么样？

先在心里答一下。第 1 站的概念讲完以后回头对答案。

## 第 1 站：公开仓库和许可证（约 40 分钟）

### 概念

你写的网页、代码、文字，一写出来就自动归你，这叫**版权（copyright）**：作者对自己作品天然拥有的权利。别人想复制、修改、拿去分发，都需要你同意。

**许可证（license）**是你提前写好的一份“同意书”：写明别人可以拿你的作品做什么，要遵守什么条件。它放在仓库根目录一个叫 `LICENSE` 的文件里。

类比：许可证像公园门口的告示牌，“可以拍照，可以野餐，不可以摘花”。没有告示牌的私人花园，默认谁都不能进。

这个类比在哪里不成立：告示牌谁都能随手写，许可证却是一份法律文本，自己改几个字，就成了一份没人审过、意思可能说不清的新许可证。所以大家都用现成的、有名字的许可证，比如 **MIT 许可证（MIT License）**。

回头对答案：没说明的照片，默认不能印在 T 恤上卖；写了“随便用，注明作者”，注明作者就可以用。代码也一样。

### 跟我做

#### 1. 公开之前，先查一遍

这一课在你真正的网站文件夹 `~/Developer/my-site` 里做。它的**全部历史**马上要公开：每个提交的内容、作者名字和邮箱。先按第 1.12 课的 REMOTE-02 查一遍。

```zsh
cd ~/Developer/my-site
git status
```

你应该看到最后一行是 `nothing to commit, working tree clean`。`cd` 报 `no such file or directory`，先别往下做，对导师说“急救：my-site 的状态不对”。最后一行不是这个，是有改动没提交：用 `git diff` 看改了什么，要留就按约定式提交提交，不要就按第 1.8 课用 `git restore` 撤掉；拿不准，把屏幕上的字发给导师。

把第 1.7 课的 `--stat` 和第 1.11 课的 `--format` 合起来用。先猜：每个提交会显示哪几样？

```zsh
git log --stat --format='%h %an <%ae>'
```

你应该看到这样开头（分页器 less：按空格往下翻，按 q 退出；编号、名字和邮箱你的会不一样）：

```text
c74ae56 你的名字 <you@example.com>

 style.css | 1 +
 1 file changed, 1 insertion(+)
```

一个一个提交看两样东西：

- **改过哪些文件。** 只应该是 `index.html`、`style.css`、`README.md`、`.editorconfig`、`.gitignore`。出现 `.env`，或者名字里带 `key`、`token`、`password` 的文件，先别往下做，对导师说“急救：公开前发现历史里有密钥文件”。
- **每个提交的第一行。** 这是第 1.11 课学过的格式：编号、作者名字、邮箱。名字和邮箱都会跟着公开。第 1.6 到 1.10 课的提交还写着第 1.6 课设的邮箱：第 1.11 课换隐私地址只管以后的提交。这就是第 1.11 课说好要在这里看的。

再用第 1.12 课的搜法，搜一遍现在文件里的内容：

```zsh
git grep -n -i -E "password|token|secret|key|密码|密钥|令牌"
```

你可能看到这样一行，也可能什么都不输出（你的会不一样）：

```text
.gitignore:6:# 存放密钥和密码的文件，永远不进仓库
```

每一行都读一遍：这一行只是 `.gitignore` 里提到“密钥”的说明文字，没问题。搜到真的密钥或密码，也按上面那句对导师说。

最后用 VS Code 打开 my-site（`code .`）〔对照文档，界面可能不同〕，把 `index.html` 和 `README.md` 从头到尾看一遍（第 1.4 课的标题、第 1.5 课的作者）：里面不要有真名、手机号、住址、工作单位。

> **旧提交里有不想公开的东西怎么办**：旧提交会一直带着当时的作者名字和邮箱（GitHub 文档「Setting your commit email address」，2026-11-20 核对）；文件里的真名现在改掉，旧提交里也还存着。去掉它们只能改写历史，而且不可逆；课程不单独教它，需要时导师在急救里带你做（下面第二个选择）。两个选择都可以：
>
> - 接受：公开了也无所谓，接着往下做。
> - 不接受：先停下。旧提交里有你的真实邮箱，对导师说“急救：公开前发现旧提交里有我的真实邮箱”；文件里或作者那一行有你的真名，对导师说“急救：公开前发现旧提交里有我的真名”。导师先讲后果、带你做安全副本，再由你亲手执行。

#### 2. 选一个许可证

没有许可证，作品由作者保留所有权利：别人不能复制、分发、修改。放在 GitHub 公开仓库里，GitHub 的服务条款也只允许别人**看**和 **fork**（在 GitHub 上复制一份到自己名下）（choosealicense.com「No License」页，2026-11-20 核对）。

GitHub 做的选许可证网站 choosealicense.com 首页给了三条路：跟着你所在社区的习惯走；想简单宽松，用 MIT；想要求别人把改过的版本再发出去时也公开源代码，用 GNU GPLv3（另一种有名字的许可证）。**选哪一个是你的决定，这不是规范。** 本课推荐 MIT，首页说它“短小直接”：随便用，保留我的版权声明，出了问题我不负责。你选了别的，把下面的文件内容换成那一份就行。

#### 3. 建 LICENSE 文件

在浏览器里打开 MIT 许可证的页面〔对照文档，界面可能不同〕，把许可证全文整段复制下来：

```text
https://choosealicense.com/licenses/mit/
```

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

页面说：在项目根目录建一个叫 `LICENSE`（或 `LICENSE.txt`）的纯文本文件（plain text file：只有文字、没有排版格式的文件），把全文放进去。本课程用 `LICENSE`，要全部大写：Mac 不分大小写，GitHub 却把 `license` 当成另一个名字。先建一个空文件：

```zsh
touch LICENSE
```

在 VS Code 左边的文件列表里点 `LICENSE`，把全文粘贴进去〔对照文档，界面可能不同〕。第三行原来是：

```text
Copyright (c) [year] [fullname]
```

把 `[year]` 换成 `2026`，`[fullname]` 换成你愿意公开的名字，比如网页上的笔名或 GitHub 用户名，方括号也删掉。按 ⌘S 保存。

先猜：下面这条命令会输出什么？（`head -n 3` 只看前 3 行，第 1.1 课学过。）

```zsh
head -n 3 LICENCE
```

你应该看到：

```text
head: LICENCE: No such file or directory
```

> 读懂这句：head 说，没有叫 LICENCE 的文件或文件夹。

这是故意敲错的。报错三问：谁在报错？`head`。关键词？`No such file or directory`。我刚才敲了什么？`LICENCE`，英式拼法；文件名是美式的 `LICENSE`，差一个字母终端就找不到。改对再来：

```zsh
head -n 3 LICENSE
```

你应该看到（名字你的会不一样）：

```text
MIT License

Copyright (c) 2026 你的名字
```

还看到 `[year]` 或 `[fullname]`，说明没替换完。什么都没输出，多半是还没按 ⌘S 保存（VS Code 标签页上文件名旁边有个圆点）。

#### 4. 看看 Git 怎么看它

先说出执行后图会怎么变：LICENSE 现在只在工作区里。

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

```zsh
git status
```

你应该看到：

```text
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	LICENSE

nothing added to commit but untracked files present (use "git add" to track)
```

> 读懂这句：有一个 Git 还没跟踪的新文件 LICENSE；用 git add 才会把它放进下一次提交。

先别提交：README 里还要写一句。

### 补全

来访的人先读 README，所以它的最后一节要说用的是什么许可证，并链接到 LICENSE。指向同一个仓库里的文件，链接地址直接写文件名，这叫相对链接。把空填上：

```markdown
## ____

本项目使用 ____ 许可证，全文见 [____](____)。
```

### 自己做

目标：

1. my-site 的 README.md 最后加一节：一个标题，下面一句话写明用的是什么许可证，并链接到 LICENSE。
2. 先用 `git diff` 看一眼改了什么，再把 LICENSE 和 README.md 的这处改动拍成**一个**提交（它们是同一件事），说明按约定式提交写。做完 `git status` 是干净的。

第 1.11 课选了隐私邮箱的，从这个提交起，新提交的作者邮箱以 `@users.noreply.github.com` 结尾。检查会顺便看一眼。

回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.13a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.13a`

> **存档点 1.13a**：到这里可以安全停下。下次可以对导师说“从 1.13b 继续”。

## 第 2 站：用 GitHub Pages 上线（约 40 分钟）

### 概念

**上线（deploy，也叫部署）**：把作品放到一台一直开着的电脑上，让别人通过网址访问。你的 Mac 合上盖子，网页还在。

**GitHub Pages** 是 GitHub 免费托管静态网站（static site：只有现成网页文件、不需要在服务器上运行程序的网站，比如 my-site）的服务：它从你仓库的一个分支（第 1.6 课说过，你只有一条，叫 main）取出网页文件，发布成一个网址：

```text
https://你的用户名.github.io/my-site/
```

类比：GitHub Pages 像一个二十四小时开着的橱窗，路过的人随时能看到你的作品。这个类比在哪里不成立：橱窗里摆的是你**推送上去**的那一份，不是你电脑上正在改的那一份。

两条硬条件，来自 GitHub 文档「Creating a GitHub Pages site」（2026-11-20 核对）：用免费账号（GitHub Free）时，仓库**必须是公开的**；推送之后，网页最长要等大约 10 分钟才更新。第 1.12 课的学习仓库还是私有的，这一课只公开 my-site。

### 跟我做

#### 1. 还没有远程仓库时推送

先猜：my-site 还没有连任何远程仓库，现在运行 `git push` 会怎样？

```zsh
cd ~/Developer/my-site
git push
```

你应该看到：

```text
fatal: No configured push destination.
Either specify the URL from the command-line or configure a remote repository using

    git remote add <name> <url>

and then push using the remote name

    git push <name>

```

> 读懂这句：致命错误：没有设置推送的目的地。要么在命令里写上地址，要么先配置一个远程仓库。

报错三问：谁在报错？`git`。关键词？`No configured push destination`。我刚才敲了什么？`git push`，可 my-site 还没有远程仓库。它建议的 `git remote add` 不用敲：下面的 `gh` 命令会顺手加好。

#### 2. 建公开仓库并推送

下面的命令用 `--source=.` 表示“用这里的仓库”，所以先确认你在哪里：

```zsh
pwd
```

你应该看到：

```text
/Users/你的用户名/Developer/my-site
```

最后一段必须是 `my-site`。是 `fullstack-from-zero` 的话，这条命令会拿学习仓库去建公开仓库，先别敲。

> 敲回车之前再想一秒：公开以后，别人已经下载或者 fork 的副本，你再改回私有也收不回来。第 1 站的检查做完了吗？

```zsh
gh repo create my-site --public --source=. --remote=origin --push
```

`.` 要用英文输入法敲：中文输入法打出来的 `。` 不是 `.`。

拆开读（GitHub CLI 手册 gh repo create，2026-11-20 核对）：

| 部分 | 意思 |
|---|---|
| `gh repo create my-site` | 在 GitHub 上建一个叫 my-site 的仓库 |
| `--public` | 公开（第 1.12 课那条写的是 `--private`） |
| `--source=.` | 用当前文件夹里的本地仓库 |
| `--remote=origin` | 在本地把它记成叫 origin 的远程仓库 |
| `--push` | 把本地的提交推送上去 |

这一步要联网和你在第 1.11 课登录的账号，建课时没法运行〔建课时无法验证〕。成功时是几行带 `✓` 的话。它说要先运行 `gh auth login`，就按第 1.11 课再登录一次；还不行，对导师说“急救：gh 登录不上”。看到 `error` 或 `already exists`，先别重试，把屏幕上的字发给导师。

```zsh
git remote -v
```

你应该看到（用户名你的会不一样；这两行建课时没法实测〔建课时无法验证〕）：

```text
origin	https://github.com/你的用户名/my-site.git (fetch)
origin	https://github.com/你的用户名/my-site.git (push)
```

先说出执行后图会怎么变：推送过以后，“本地历史”和“远程”里是同一批快照。

```zsh
git status
```

你应该看到：

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

> 读懂这句：你的 main 和 origin 上的 main 一致，也没有没提交的改动。

#### 3. 打开 Pages

```zsh
gh browse --settings
```

`gh browse --settings` 在浏览器里打开这个仓库的设置页（GitHub CLI 手册 gh browse，2026-11-20 核对）。然后按 GitHub 文档「Configuring a publishing source for your GitHub Pages site」（2026-11-20 核对）做〔对照文档，界面可能不同〕：

1. 左边栏 “Code, planning, and automation”（代码、规划和自动化）一组里，点 **Pages**。
2. “Build and deployment”（构建和部署）下面，“Source”（来源）选 **Deploy from a branch**（从一个分支发布）。
3. 分支的下拉菜单选 **main**，旁边文件夹的下拉菜单选 **/ (root)**（根目录）。
4. 点 **Save**（保存）。

最长要等大约 10 分钟，等的时候先做「补全」和「自己做」的前两步。发布好以后刷新这一页，会出现你的网址和 **Visit site**（访问网站）按钮。点它，再用手机浏览器打开同一个网址〔对照文档，界面可能不同〕。

看到写着 404（找不到网页）的页面〔对照文档，界面可能不同〕：多半是还没等够，或者少做了一步（比如没点 Save），回设置页对一遍再等。Pages 用不了（比如你不愿意公开这个仓库），对导师说“急救：Pages 用不了”；备选办法在文末「想多了解」。

> **旧教程提醒**：很多旧教程让你新建一个叫 `gh-pages` 的分支来放网页。GitHub 自 2016-08-17 起允许从主分支发布（GitHub 博客 “Simpler GitHub Pages publishing”），自 2020-09-03 起允许任何分支（GitHub 更新日志 “Build and deploy GitHub Pages from any branch”）。现在直接选 main。

### 补全

网址由两部分拼成，把空填上：

```text
https://____.github.io/____/
```

第一个空是你的 GitHub 用户名（`git remote -v` 那行地址里 `github.com/` 后面那一段），写成全部小写；第二个空是仓库名。

### 自己做

目标：

1. 在 my-site 的 README.md 最后加一节“网页地址”，写上你的网址。
2. 按约定式提交写说明，提交，然后推送。做完 `git status` 的第二行是 `Your branch is up to date with 'origin/main'.`。
3. 用手机打开你的网页。检查器不联网，看不到 GitHub 上的设置，所以检查最后会问你手机上打开的网址和看到的样子，靠你亲眼确认。

回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.13b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.13b`

> **存档点 1.13b**：到这里可以安全停下。下次可以对导师说“从 1.13c 继续”。

## 第 3 站：改一处、推送、看网页更新（约 35 分钟）

### 概念

**交付循环（delivery loop）**：改动 → 看改动清单 → 提交 → 推送 → 确认上线，然后下一圈。很多团队也转这个圈，只是有几步交给了机器（阶段 3 和阶段 9 会学）。顺序不变，所以先用手走熟。

类比：给橱窗换展品。在工作间改好，检查一遍，打包贴标签，送过去，再走到橱窗前看一眼。

这个类比在哪里不成立：橱窗收到货要过一会儿才摆上去，浏览器也可能还记着旧的样子，所以推送完等一两分钟再刷新。

### 跟我做

#### 1. 改一处

在 VS Code 里打开 `index.html`，把列表里这一行：

```html
      <li>我会把网页放到网上</li>
```

改成：

```html
      <li>我已经把网页放到了网上</li>
```

按 ⌘S 保存。以前改过这一行的，挑列表里别的一行，改成你现在的情况。

#### 2. 看改动清单

```zsh
cd ~/Developer/my-site
git diff
```

你应该看到（`index` 那一行的编号和最后几行你的会不一样）：

```text
diff --git a/index.html b/index.html
index 4a7c29b..80d90bc 100644
--- a/index.html
+++ b/index.html
@@ -15,7 +15,7 @@
     <ul>
       <li>我会用终端管理文件</li>
       <li>我会用 Git 记录每一次改动</li>
-      <li>我会把网页放到网上</li>
+      <li>我已经把网页放到了网上</li>
       <li>下一步：学会用 Git 管理改动</li>
     </ul>
   </main>
```

清单里只有你改的那一行，没有意外。什么都没输出，多半是还没按 ⌘S 保存。

#### 3. 故意漏一步

先猜：还没 `git add`，也没 `git commit`，直接推送会怎样？

```zsh
git push
```

你应该看到：

```text
Everything up-to-date
```

> 读懂这句：一切都是最新的。

这不是报错，却是新手最常踩的坑：网上的网页一点没变。报错三问：谁在说话？`git`。关键词？`up-to-date`，没有要送的东西。我刚才敲了什么？只有 `git push`。推送只送**已经提交**的快照，改动还没走过第 1 站那张图上 `git add` 和 `git commit` 两段箭头。

```zsh
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

> 读懂这句：和 origin/main 一致，但 index.html 改了还没放进暂存区，也就没有新提交可以推送。

#### 4. 把这一圈走完

先说出每一步之后图会怎么变，再敲：

```zsh
git add index.html
git commit -m "feat: 列表里写上网页已经上线"
git push
```

你应该看到（编号你的会不一样；`git push` 前面可能还有几行 `Enumerating objects` 这样的进度）：

```text
[main 6fe4f92] feat: 列表里写上网页已经上线
 1 file changed, 1 insertion(+), 1 deletion(-)
To https://github.com/你的用户名/my-site.git
   e1c2e2a..6fe4f92  main -> main
```

> 读懂这句：推送到了你的仓库，远程的 main 从 e1c2e2a 前进到了 6fe4f92。

`To` 那一行的地址建课时没法实测〔建课时无法验证〕。再运行一次 `git status`，第二行应该又是 `Your branch is up to date with 'origin/main'.`。

#### 5. 看网页更新

回到浏览器里你的网页，按 ⌘R 刷新（R 是 reload，重新载入）〔对照文档，界面可能不同〕。等一两分钟再刷新，直到看到“我已经把网页放到了网上”。

### 补全

把交付循环的命令按顺序填上：

```zsh
# 1. 在 VS Code 里改文件，按 ⌘S 保存
git ____          # 2. 看改动清单
git ____ index.html
git ____ -m "____: ____"   # 3. 拍成快照，说明按约定式提交写
git ____          # 4. 送到 GitHub
# 5. 等一会儿，刷新网页确认
```

### 自己做

目标：在网页的页脚加一个链接，文字写“这个网页的源代码”，指向你的仓库页面 `https://github.com/你的用户名/my-site`。然后走完这一圈：看改动清单，按约定式提交提交，推送，刷新网页，点新链接确认它打开了你的仓库。

页脚是 `index.html` 里 `<footer>` 和 `</footer>` 中间那一块，里面已经有一个链接：

```html
    我常查的网页资料：<a href="https://developer.mozilla.org/zh-CN/">MDN</a>
```

`<a href="地址">文字</a>` 就是一个链接：`href` 后面引号里是点了去哪儿，`>` 和 `</a>` 中间是网页上显示的字。照它的样子，把新链接接在 MDN 那个链接后面。

回到学习工作区：`cd ~/Developer/fullstack-from-zero`

- 提示：`python3 tools/course.py hint 1.13c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.13c`

> **存档点 1.13c**：到这里可以安全停下。下次可以对导师说“从 1.13 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| PUB-01 | 公开仓库三件套：README、LICENSE、.gitignore | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 惯例·平台与工具 | GitHub Docs「Creating a new repository」「About community profiles for public repositories」「Licensing a repository」；choosealicense.com | 2026-11-20 |

GitHub 新建仓库时让你顺手创建的正是这三样，“三件套”是本课程的叫法。在本课程里你的 my-site 公开之前三样都要有，所以是必须；别的项目里是推荐。

完整卡片在本课文件夹的 `rules.md`。

## 收尾（约 20 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.13`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「PUB-01 公开仓库三件套：README、LICENSE、.gitignore」下面用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`
4. 备份：把今天的笔记和日志推到云端，按第 1.12 课收尾的那一组命令做。

都做完，这一课就完成了。下次可以对导师说“从 1.14 开始”。

## 想多了解

这一节的内容都可以跳过。

> **想多了解（可跳过）：GitHub Pages 用不了的备选**
>
> 一个备选是 Render 的免费静态网站：连上 GitHub 仓库以后，每次推送自动更新，网址是 `onrender.com` 前面加一个只属于你的名字，叫子域名（subdomain：挂在别人网址下面的名字，就像 `你的用户名.github.io` 挂在 `github.io` 下面）（render.com 文档「Static Sites」，2026-11-20 核对）〔对照文档，界面可能不同〕。它要另注册一个账号，注册由你自己决定、自己做。不上线也能学完这一课的大部分：在 my-site 里运行 `open index.html`，网页照样在你自己的浏览器里打开。走这两条路，检查 1.13b 都过不了：它要看到 GitHub 上的仓库，还要在 README 里看到 `github.io` 的网址；连 GitHub 仓库也不建的，1.13c 也过不了。`status` 的“下一步”会一直停在 1.13b，后面的课照样可以上。对导师说“急救：Pages 用不了”的时候，把你选的路告诉他。

- choosealicense.com「No License」页，讲没有许可证会怎样，页面上的语言菜单可以选中文：https://choosealicense.com/no-permission/ （English，可切换中文）
- choosealicense.com 中文版：https://choosealicense.com/zh/ （中文）
- GitHub Docs「What is GitHub Pages?」：https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages （English）
- GitHub Docs「Licensing a repository」：https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository （English）
