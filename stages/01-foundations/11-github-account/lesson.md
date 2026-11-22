# 1.11 GitHub：账号、安全与身份

> **用时** 3 站，约 120 分钟 ｜ **前置** 1.10 ｜ **核实** 2026-11-20 · macOS 27.2.1 · git 2.54.0 · Homebrew 7.0.10 · gh 2.105.0（网页步骤和 gh 对照官方文档和源代码）
> **学完你能** 用一个开了双重验证的 GitHub 账号登录；在终端里装好 gh，并让它替你登录 GitHub；决定提交里写哪个邮箱、要不要给提交签名，并在一个提交上亲眼看到结果。
> **本课行规** ACC-01、ACC-02（见文末）

这一课有一半步骤在 GitHub 网页上做。建课时没有账号，没法替你点一遍：这些步骤照 GitHub 当天的官方文档写，标着〔对照文档，界面可能不同〕；完全没法验证的标着〔建课时无法验证〕。

两条贯穿全课的规矩：

- 账号、密码、验证码、恢复码、令牌，都由你自己在自己的浏览器和终端里输入。导师不会向你要这些东西。谁要都不给，包括 AI。
- 注册时的用户名是公开的，第 1.13 课它还会变成你网页网址的一部分。用笔名完全可以。

这一课的 `python3 tools/course.py …` 命令都在学习工作区里运行。回到学习工作区：`cd ~/Developer/fullstack-from-zero`

## 先想一想

如果有人偷看到了你的邮箱密码，他能登录你的邮箱吗？如果登录时，除了密码还要输入你手机上一个每 30 秒就变一次的数字呢？

先在心里答一下。第 1 站的概念讲完以后回来对答案。

## 第 1 站：注册和双重验证（约 35 分钟）

### 概念

GitHub 是一个存放 Git 仓库的网站。它对你有两个用处：给你的仓库在别处留一份（第 1.12 课），以及把作品放到网上给别人看（第 1.13 课）。在 Git 的四区域图上，它就是最右边的“远程”：

```text
   工作区              暂存区              本地历史              远程
（你正在改的文件）   （准备拍进快照的）   （已经拍下的快照）    （别处的另一份）
       │     git add      │    git commit     │      git push       │
       └────────────────▶ └─────────────────▶ └───────────────────▶
```

（远程和 `git push` 以后再讲：第 1.12 课。）

账号里放着你所有的仓库，所以登录要比一般网站更严。办法叫双重验证（two-factor authentication，简称 2FA）：登录时除了密码，还要一样只在你手里的东西。

GitHub 推荐的“第二样东西”是验证器 App（authenticator app，也叫 TOTP app，意思是按时间变化的一次性密码）：手机上的一个小程序，每 30 秒生成一个新的六位数字，过期就作废。登录时 GitHub 有时会往你的邮箱发验证码，那不算双重验证，因为拿到你邮箱的人可以重设密码（GitHub Docs，2026-11-20 核对）。

打个比方：密码像银行卡的密码，验证器 App 像银行卡本身。只知道密码、手里没有卡，取不了钱。

这个比方在哪里不成立：银行卡丢了能去柜台补办；GitHub 的“卡”丢了，GitHub 客服不能替你恢复登录。所以开启时 GitHub 会给你一组恢复码（recovery codes）：手机丢了时用来登录的备用码，每个只能用一次。恢复码和手机一起丢了，多半就再也进不去了：只剩一条要另拿证明、等几个工作日、还不一定批准的人工审核（GitHub Docs，2026-11-20 核对）。

> **对答案**：只偷到密码的人登录不了，因为他没有你的手机，算不出那个六位数字。这就是“第二重”的意义。

### 跟我做

#### 1. 注册账号〔对照文档，界面可能不同〕

已经有 GitHub 账号的，跳到第 2 步；已经用短信开了双重验证的，按本站末尾的说明框做。

1. 在浏览器里打开 `https://github.com/signup`。
2. 按页面提示填写邮箱、密码、用户名。密码用一个只给 GitHub 用的新密码，存进密码管理器（password manager）：专门替你记住密码、加密保存的程序。Mac 自带一个，叫 **Passwords**（密码）App；浏览器问要不要保存密码时，选保存也可以。
3. 页面会要你做一个人机验证的小题，再往你的邮箱发一个验证码，填进去。邮件要等一两分钟。

和你看到的不一样？把屏幕上的内容发给导师，说“课文对不上”。

#### 2. 装一个验证器 App〔对照文档，界面可能不同〕

在手机上装一个验证器 App。GitHub 不指定是哪一个。它的文档提醒：很多验证器 App 能把验证码安全地备份到云端，选这样的，换手机时不会丢。

#### 3. 开启双重验证〔对照文档，界面可能不同〕

GitHub 网页是英文的，按钮名照原样写，括号里是意思。

1. 点右上角你的头像，再点 **Settings**（设置）。
2. 左边栏 “Access” 一组里，点 **Password and authentication**（密码和认证）。
3. 在 “Two-factor authentication” 一栏，点 **Enable two-factor authentication**（开启双重验证）。
4. 页面上出现一个二维码。在验证器 App 里选“添加账号”或“扫描二维码”，对准它扫。
5. App 里出现一行 GitHub 和一个六位数字。这个数字要填进 “Verify the code from the app”（填入 App 里的数字）下面的框。

先故意做错一次：把 App 里正在显示的数字**最后一位改掉**再填进去（比如 `123456` 填成 `123457`）。页面会出现一行提示，大意是验证码不对，原文以你的屏幕为准〔建课时无法验证〕。用报错三问读它：

- **谁在报错？** GitHub 网站，不是你的电脑，也不是终端。
- **关键词是什么？** 找 failed、invalid、incorrect 这类词，它们都是“不对、失败”的意思。
- **我刚才输了什么？** 一个和 App 对不上的数字。只有手里有这部手机的人才算得出对的那个，正是它安全的原因。

现在填 App 里**正在显示**的数字。

6. 在 “Save your recovery codes”（保存恢复码）下面，点 **Download**（下载）。文件会存进“下载”文件夹，GitHub 文档说默认的文件名是 `github-recovery-codes.txt`。
7. 点 **I have saved my recovery codes**（我已经保存了恢复码）。双重验证就开好了。

> **旧教程提醒**：以前不少教程说“双重验证用短信收验证码就行”。GitHub 自 2023 年 3 月推行强制双重验证起就写明：尽量用验证器 App 或安全密钥，短信不再推荐（GitHub Blog，2023-03-09）。现在的文档也“强烈建议”用验证器 App，因为短信可能被截获，有的地区还收不到（GitHub Docs，2026-11-20 核对）。

### 补全

把下面两行补完整，写在纸上或心里都行：

```text
我的双重验证，主要方式是：________
手机丢了的时候，我用：________ 登录，它每个只能用 ____ 次
```

### 自己做

目标：恢复码现在躺在“下载”文件夹里，像把备用钥匙放在门口地垫下面。把它们放到一个安全的地方，再数一数有几个。

要求：

- 存进密码管理器（GitHub 文档推荐的做法），或者打印出来，放在手机以外的地方；
- 存好以后，删掉“下载”文件夹里的那份；
- 不放进学习工作区（不管它真正在哪个文件夹），也不放进 `~/Developer` 下面的任何文件夹：它们都会变成仓库、推送到 GitHub。第 1.9 课说过，密码这类东西永远不进仓库。

用 Mac 自带的 Passwords App 的话，可以这样存：点左边的 **All**（全部），选中 github.com 那一条，点 **Edit**（编辑），把恢复码贴进 **Notes**（备注）栏，点 **Save**（存储）〔对照文档，界面可能不同〕。

做完回到学习工作区运行检查，它会问你三个问题。

- 提示：`python3 tools/course.py hint 1.11a`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.11a`

> **想多了解（可跳过）：已经用短信开了双重验证的人**
>
> 装好第 2 步的验证器 App，在 Settings → Password and authentication 页面的 “Two-factor methods” 里，给验证器 App 点 **Add**（添加），扫码、填数字、点 **Save**（保存）；再在 “Preferred 2FA method”（首选方式）里选它〔对照文档，界面可能不同〕。恢复码在同一页 Recovery codes 旁边点 **View**（查看）就能下载，然后做「补全」和「自己做」。

> **想多了解（可跳过）：确认第二步真能用**
>
> 在 GitHub 网页上退出登录（点头像，最下面的 **Sign out**），再重新登录，输完密码后用验证器 App 的六位数字完成第二步〔对照文档，界面可能不同〕。不做也可以：GitHub 文档写明，开启后有 28 天的“检查期”，这期间你用过一次第二步就算过关；没用过的话，第 28 天 GitHub 会在你登录着的时候请你做一次。

> **存档点 1.11a**：到这里可以安全停下。下次可以对导师说“从 1.11b 继续”。

## 第 2 站：让电脑认识 GitHub（约 35 分钟）

### 概念

现在要让你的电脑也能以你的身份和 GitHub 打交道。下一课 `git push` 往 GitHub 送东西时，GitHub 要知道是谁在送。

在终端里输账号密码不行：GitHub 从 2021 年 8 月 13 日起不再接受用账号密码做 Git 操作（GitHub Blog，2026-11-19 核对）。现在的做法是第 1.9 课说过的令牌：这里是 GitHub 发给 gh 这个程序的通行证，代替密码使用。

打个比方：在酒店前台出示身份证（在浏览器里登录、过双重验证），前台给你一张房卡（令牌）。之后进门刷房卡就行，不用每次掏身份证。房卡丢了，前台把它作废、再发一张，身份证不用换。

这个比方在哪里不成立：酒店房卡退房就失效；这一课拿到的令牌默认一直有效，直到你作废它。所以它和密码一样要保密。

替你去“前台”领房卡、再替你保管好的，是 GitHub 官方的命令行工具 GitHub CLI，命令名是 `gh`。它把令牌存进 Mac 的钥匙串（系统专门存密码的地方），而不是一个谁都能打开的文本文件。

> **工具小贴士：Homebrew 和 PATH**
> `gh` 要先装。装它的 Homebrew（命令名 `brew`）是一个包管理器（package manager）：替你下载、安装、升级命令行程序的程序。课程核对时用的是 7.0.10。你的电脑上还没有它的话，敲 `brew --version` 会看到 `command not found`：先按官网 https://brew.sh/ 的说明装好它（第 1.1 课 TERM-01 说的例外：先确认网址真是官网、读过说明），再往下做。
> 敲一个命令名时，终端会按顺序翻一串文件夹去找这个程序，这串文件夹叫 PATH（全大写，和第 0.2 课的路径不是一回事：PATH 是一串路径）。找不到，就报 `command not found`。

### 跟我做

#### 1. 故意出错：在装之前就用 gh

```zsh
gh --version
```

你应该看到：

```text
zsh: command not found: gh
```

> 读懂这句：zsh 说，找不到叫 gh 的命令。

用报错三问读它：

- **谁在报错？** zsh，也就是终端里的 shell，不是 gh。
- **关键词是什么？** `command not found`：PATH 里的每个文件夹都翻过了，没有这个程序。
- **我刚才敲了什么？** 一个还没装的程序，拼写没错。

#### 2. 用 Homebrew 装 gh〔建课时无法验证〕

GitHub CLI 的官方说明（github.com/cli/cli，2026-11-19 核对）在 macOS 下列的第一种安装方式就是 Homebrew。按第 1.1 课的 TERM-01 先认清它：`brew` 是命令名，`install` 是“安装”，`gh` 是要装的程序。

```zsh
brew install gh
```

建课时不能在本机装软件，下面是照 Homebrew 7.0.10 的源代码（写成这个程序的原文）整理的：先是一些以 `==>` 开头的进度行，有时它会先花一两分钟更新自己的软件清单。快结束时有一行以啤酒杯图标开头，最后几行一般是这样（数字你的会不一样，中间有时还夹着别的 `==>` 行）：

```text
🍺  /opt/homebrew/Cellar/gh/2.105.0: …（文件个数和大小）
==> Caveats
zsh completions have been installed to:
  /opt/homebrew/share/zsh/site-functions
```

> 读懂这句：gh 已经装进 `/opt/homebrew/Cellar/gh/<版本号>` 这个文件夹。注意事项（Caveats）：zsh 的命令补全装好了，不用管。

如果出现以 `Error:` 开头的红字，不要自己搜一条命令照抄，先停下，把整段输出发给导师，说“急救：brew 装 gh 报 Error”。

#### 3. 再找一次 gh〔建课时无法验证〕

`which` 是英文“哪一个”：问终端，这个命令用的是哪个文件夹里的程序。先猜它会输出什么。

```zsh
which gh
```

你应该看到：

```text
/opt/homebrew/bin/gh
```

Homebrew 把程序装进 `Cellar`，再在 `/opt/homebrew/bin` 里放一个指向它的“快捷方式”。这个文件夹本来就在 PATH 里，所以装完马上能用。

```zsh
gh --version
```

你应该看到两行（版本号和日期你的会不一样）：

```text
gh version 2.105.0 (2026-11-18)
https://github.com/cli/cli/releases/tag/v2.105.0
```

> 读懂这句：gh 的版本是 2.105.0，括号里是它的日期；第二行是它的更新说明网址。

#### 4. 登录〔对照文档，界面可能不同〕

```zsh
gh auth login
```

`auth` 是 authentication（认证）的缩写。gh 会一个接一个地问问题，用上下方向键选、按回车确认。下面是每个问题的原文（取自 gh 2.105.0 的源代码和 GitHub 文档）和要选的回答：

| gh 问的 | 意思 | 选 |
|---|---|---|
| `Where do you use GitHub?` | 你在哪里用 GitHub？ | `GitHub.com` |
| `How would you like to authenticate GitHub CLI?` | 你想怎么登录？ | `Login with a web browser`（用浏览器登录） |
| `What is your preferred protocol for Git operations on this host?` | Git 操作用哪种协议？ | `HTTPS` |
| `Authenticate Git with your GitHub credentials?` | 让 Git 也用这份登录凭据吗？ | `Yes`（直接回车就是 Yes） |

第三个问题里的协议（protocol），是 Git 和 GitHub 之间说好的连接方式。选 HTTPS（网址开头的那个 https），由 gh 存好的令牌证明你的身份；另一种 SSH（一套用一对钥匙证明身份的办法）这门课先不用。

中间要是冒出 `! Did you know …` 一行，是推荐，不是报错（见本站末尾的框）。问完以后，屏幕上会出现：

```text
! First copy your one-time code: XXXX-XXXX
Press Enter to open https://github.com/login/device in your browser...
```

> 读懂这句：先记下这个一次性验证码；按回车，在浏览器里打开 github.com/login/device。

`XXXX-XXXX` 每次都不同。按回车，在打开的 GitHub 页面里填入它，点 **Authorize**（授权）。浏览器没自己打开，就手动打开这个网址。

回到终端，你应该看到以 `✓` 开头的几行，最后一行是：

```text
✓ Logged in as 你的用户名
```

> 读懂这句：已经以“你的用户名”登录。

#### 5. 看登录状态〔对照文档，界面可能不同〕

先猜：`status` 是“状态”，这条命令会不会改动什么？

```zsh
gh auth status
```

你应该看到类似下面的几行（格式取自 gh 2.105.0 的源代码；用户名、星号个数、权限列表你的会不一样）：

```text
github.com
  ✓ Logged in to github.com account 你的用户名 (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

> 读懂这句：已经用“你的用户名”登录 github.com，令牌存在系统的钥匙串（keyring）里；这是当前在用的账号；Git 操作走 https；令牌只露出开头，后面用星号挡住了；最后一行是令牌的权限范围，以后用到再讲。

`gh auth status` 只看不改。它有一个选项会把令牌原样显示出来，**永远不要用它**；令牌也永远不要复制到聊天窗口里。导师有时能看到你的终端面板，所以屏幕上也别让它出现。

> **旧教程提醒**：以前的教程会说“git push 时终端问 Password，就输入 GitHub 账号密码”；自 2021 年 8 月 13 日起这样做会失败。GitHub 文档现在推荐用 GitHub CLI（`gh auth login`），或者专门保管登录凭据的程序 Git Credential Manager（GitHub Blog 与 GitHub Docs，2026-11-19 核对）。

### 补全

把空填上：

```text
/opt/homebrew/bin 本来就在 ____ 里，所以 brew 装完 gh，敲 gh 终端马上找得到。
gh 登录以后拿到的是一个 ____，它代替密码，存在 Mac 的钥匙串里。
```

### 自己做

目标：不往上翻课文，自己查清楚三件事，前两件问的是 brew：

1. 你敲 `brew` 时，终端用的是哪个位置的 brew；
2. 你的 Homebrew 是哪个版本；
3. gh 现在有没有登录，Git 操作走的是哪种协议。

查完回到学习工作区运行检查，它会问你这三件事。

- 提示：`python3 tools/course.py hint 1.11b`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.11b`

> **想多了解（可跳过）：登录时冒出的 `!` 提示**
>
> `gh auth login` 问问题的中间，可能冒出这样一行（取自 gh 2.105.0 的源代码）：`! Did you know that expiring tokens can be requested with --expiring? Read more at https://gh.io/gh-expiring-tokens` 读懂这句：你知道吗，加 --expiring 可以要一个会自动过期的令牌；详情见这个网址。这一课不用它。

> **存档点 1.11b**：到这里可以安全停下。下次可以对导师说“从 1.11c 继续”。

## 第 3 站：提交邮箱隐私和签名的选择（约 35 分钟）

### 概念

这一站先动手，看到问题，再讲道理：概念在「跟我做」第 4 步之后。

### 跟我做

#### 1. 搭一个网站的练习副本

```zsh
python3 tools/course.py scenario 1.11
```

你应该看到：

```text
练习场景 1.11-start 搭好了。
位置：~/Developer/playground/1.11-start

这里有什么：
  网站的练习副本在这里：~/Developer/playground/1.11-start/my-site

接下来：
  1. 进入练习场景：cd ~/Developer/playground/1.11-start
  2. 接着按课文往下做。每做完一站，回到学习工作区运行课文里给出的检查命令：cd ~/Developer/fullstack-from-zero

练习场里的东西随便改，练习场外面的文件不会受影响。
改乱了可以重搭一份：python3 tools/course.py scenario 1.11 --reset
```

这是一份按第 1.10 课结束时的 `my-site` 搭的副本。在这里随便试，不会碰到你真正的网站。

#### 2. 故意出错：在仓库外面看历史

进入练习场景：

```zsh
cd ~/Developer/playground/1.11-start
```

`git log` 加上 `--format` 选项，可以自己决定每个提交显示哪些信息。`%h` 是提交编号的前几位，`%an` 是作者名字（author name），`%ae` 是作者邮箱（author email）。

```zsh
git log --format='%h %an <%ae>'
```

两个单引号要用英文半角的 `'`。中文输入法打出的 `‘ ’` 不算引号，zsh 会报 `zsh: no such file or directory: %ae`，看到它就切到英文输入法重敲一遍。少打了右边的 `'`，新的一行行首是 `quote>`（和 1.10 课的 `dquote>` 一样，zsh 在等另一个引号）：按 Ctrl+C〔建课时无法验证〕，重敲。

你应该看到：

```text
fatal: not a git repository (or any of the parent directories): .git
```

> 读懂这句：致命错误：这里不是 Git 仓库（往上的各层文件夹也都不是），找不到 .git。

用报错三问读它：

- **谁在报错？** git。
- **关键词是什么？** `not a git repository`：这里不是仓库。
- **我刚才敲了什么？** 在 `1.11-start` 里看历史。可仓库是它里面的 `my-site`，`1.11-start` 只是装它的盒子。

#### 3. 看看每个提交里写着谁

```zsh
cd my-site
```

先猜：练习副本是工具搭的，提交里的作者会是谁？

```zsh
git log --format='%h %an <%ae>'
```

你应该看到七行（编号你的会不一样）：

```text
9bc16b2 练习场 <playground@example.invalid>
28ae975 练习场 <playground@example.invalid>
b0892e0 练习场 <playground@example.invalid>
5d0da81 练习场 <playground@example.invalid>
bc18a53 练习场 <playground@example.invalid>
d6dcb90 练习场 <playground@example.invalid>
72256b5 练习场 <playground@example.invalid>
```

这七个提交对应你第 1.6 到 1.10 课在自己网站上拍的那几次，只是作者写成了工具“练习场”（你自己的网站可能多几个，第 1.10 课那两条说明也是你自己写的）。

#### 4. 用你自己的身份提交一次

先说出执行后图会怎么变：下面 `git add` 以后，`thanks.txt` 在第 1 站那张四区域图的哪一格？`git commit` 以后呢？

```zsh
touch thanks.txt
git add thanks.txt
git commit -m "docs: 添加 thanks.txt"
```

你应该看到（编号你的会不一样）：

```text
[main e3ba141] docs: 添加 thanks.txt
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 thanks.txt
```

对一下：`git add` 把它放进暂存区，`git commit` 把它拍进本地历史；远程那一格没变。如果看到的是 `error: cannot run gpg: No such file or directory`，说明第 1.6 课关掉签名的那一步没生效：先别往下做，对导师说“急救：提交签名”。

先猜：这个新提交里，作者会写成什么？下面的 `-1` 的意思是只看最新的一个。

```zsh
git log -1 --format='%h %an <%ae>'
```

你应该看到你在第 1.6 课确认过（或改过）的名字和邮箱（下面是示意，你的会不一样）：

```text
e3ba141 你的名字 <you@example.com>
```

停下来看这一行。**每个提交里都写着作者的名字和邮箱。** 第 1.13 课你的网站仓库会公开，到那时任何人都能这样看到它们，还能用程序成批抓走邮箱，招来垃圾邮件和钓鱼邮件。

这就是这一站的概念。

打个比方：每个提交像一封信，信封上印着寄件人的名字和地址。

这个比方在哪里不成立：普通的信只有收信人看得到；公开仓库里的提交，像是把所有信封钉在街边的公告栏上，路过的人都能看、能抄，而且钉上去就收不回来。

GitHub 的办法是给你一个隐私邮箱地址（noreply email address）：一个不收信的地址，专门写进提交里。GitHub 照样能认出这些提交是你的，别人却看不到你的真实邮箱。这就是本课的第二条行规 ACC-02（卡片在文末）。

#### 5. 在 GitHub 上打开邮箱隐私〔对照文档，界面可能不同〕

1. 点右上角头像 → **Settings** → 左边栏 “Access” 一组里的 **Emails**（邮箱）。
2. 勾选 **Keep my email addresses private**（不公开我的邮箱地址）。
3. 勾选 **Block command line pushes that expose my email**（从命令行推送的提交会暴露我的邮箱时，拦下来）。
4. 勾选以后，在这个页面上找到你的隐私地址。2017 年 7 月 18 日以后注册的账号，它的样子是 `一串数字+你的用户名@users.noreply.github.com`。把它整个复制下来。

#### 6. 让 Git 以后用这个地址

把下面引号里的内容换成你刚复制的地址，再运行。引号同样要用英文半角的 `"`：

```zsh
git config set --global user.email "12345678+你的用户名@users.noreply.github.com"
```

这条命令什么也不输出。用第 1.6 课学过的 `git config get` 查一下：

```zsh
git config get user.email
```

你应该看到你的隐私地址（你的会不一样）：

```text
12345678+你的用户名@users.noreply.github.com
```

有两件事要知道：

- **改设置只影响以后的提交。** 刚才 `thanks.txt` 那个提交里还是旧邮箱，你真正的 `my-site` 里第 1.6 到 1.10 课的提交也是。第 1.13 课公开 `my-site` 之前，会带你看一遍历史里有哪些旧邮箱，再决定怎么办。
- **名字也会公开。** 不想公开真名，可以同样把 `user.name` 换成笔名，由你决定。

想继续用自己的邮箱也可以（ACC-02 是推荐，不是必须），只是它会跟着每个提交公开。这样选的话，一定回到第 5 步的 Emails 页，把 **Block command line pushes that expose my email** 的勾去掉，不然第 1.12 课的推送会被 GitHub 拒绝：原因见本站末尾的说明框。

#### 7. 提交签名：这一课先不签

第 1.6 课你把提交签名关掉了，这一课继续关着。签不签名由你决定：GitHub 不要求，个人学习仓库也没有人要求。想现在就用 SSH 给提交签名，步骤在本课最后的「想多了解」里，约 25 分钟。两种选择以后都能改。

### 补全

想只看最近三个提交的编号和作者邮箱，把空补上（补完可以在练习副本里试一下）：

```text
git log -__ --format='%h ____'
```

### 自己做

目标：在练习副本 `~/Developer/playground/1.11-start/my-site` 里，再做一个**新的**提交，改哪个文件由你定（不要再用 `thanks.txt`；做过「想多了解」里签名那一节的，也不要用 `signed.txt`）；提交说明照第 1.10 课的约定式提交格式写。它的作者邮箱要是你在第 6 步决定用的那个地址，并且符合你对签名的选择。

然后回到学习工作区运行检查。它会看你的新提交，再问你两个问题：你现在的提交邮箱是哪一种，提交签名是哪一种。检查只核对邮箱的“样子”，不会把它显示出来。

- 提示：`python3 tools/course.py hint 1.11c`（每运行一次多给一级）
- 检查（先回到学习工作区）：`python3 tools/course.py check 1.11c`

> **想多了解（可跳过）：用自己的邮箱时，为什么要去掉那个勾**
>
> 勾着 **Block command line pushes that expose my email** 时，每次推送 GitHub 都看最新的那个提交（GitHub Docs 写明它只检查最新的提交，2026-11-20 核对）：它的作者邮箱如果是你账号里设成不公开的邮箱，整次推送就被拒绝。你的邮箱如果就是注册 GitHub 用的那个，第 1.12 课第一次推送就会被拦下，屏幕上会有一行类似这样的英文〔建课时无法验证〕：`remote: error: GH007: Your push would publish a private email address.` 读懂这句：GitHub 那边报错，你这次推送会公开一个设成不公开的邮箱地址。

> **想多了解（可跳过）：让第 1.6 到 1.10 课的旧提交也算在你名下**
>
> GitHub 只把用“已经加进你账号的邮箱”或隐私地址做的提交算在你名下。第 1.6 课设的邮箱如果不是你注册 GitHub 用的那个，可以在第 5 步那个 Emails 页的 **Add email address**（添加邮箱）框里填上它，点 **Add**，再点 GitHub 发到那个邮箱里的确认链接〔对照文档，界面可能不同〕。这样旧提交也算你的；“不公开”的设置同样管它（GitHub Docs「Adding an email address to your GitHub account」，2026-11-20 核对）。

> **存档点 1.11c**：到这里可以安全停下。下次可以对导师说“从 1.11 的收尾继续”。

## 本课行规

| 编号 | 规则 | 约束力 | 规则类型 | 谁说的 | 核对日期 |
|---|---|---|---|---|---|
| ACC-01 | GitHub 账号开启双重验证 | 必须（适用范围：本课程）；推荐（适用范围：所有项目） | 行业要求（平台强制政策） | GitHub Docs「About mandatory two-factor authentication」「Configuring two-factor authentication」等三篇与 GitHub Blog（2023-03-09） | 2026-11-20 |
| ACC-02 | 提交邮箱用 GitHub 的隐私地址 | 推荐（适用范围：所有项目） | 惯例·平台与工具 | GitHub Docs「Setting your commit email address」「Email addresses reference」「Blocking command line pushes that expose your personal email address」 | 2026-11-20 |

完整卡片在本课文件夹的 `rules.md`。

ACC-01 对你的约束力：这门课要求每个学习者都开（必须，本课程）；GitHub 对还没被它选中的账号是“强烈建议”（推荐）；账号一旦因为“贡献代码”被 GitHub 选中，就由平台强制，过了 45 天设置期和 7 天宽限期不开就进不了 GitHub.com。主要方式用验证器 App 是 GitHub 的推荐，不是强制。

## 收尾（约 15 分钟）

1. 全课检查（在学习工作区里运行）：`python3 tools/course.py check 1.11`
2. 行规笔记：运行 `code notes/my-rules.md`，在小标题「ACC-01 GitHub 账号开启双重验证」「ACC-02 提交邮箱用 GitHub 的隐私地址」下面各用自己的话写一两句，再配一个你自己的例子，写完按 ⌘S 保存。
3. 一句话日志：`python3 tools/course.py journal`

都做完，这一课就完成了。下次可以对导师说“从 1.12 开始”。

## 想多了解

这一节的内容都可以跳过。

### 用 SSH 给提交签名（约 25 分钟）

SSH 原本是一套用一对钥匙证明“我是我”的办法：私钥只留在你的电脑上，公钥可以交给别人。它的钥匙也能拿来给提交盖章，GitHub 文档说这是最容易生成的一种签名（GitHub Docs「About commit signature verification」，2026-11-19 核对）。下面第 1 到 4 步在终端里做，第 5 步在 GitHub 网页上做。

**1. 生成一把专门的钥匙。** `ssh-keygen` 是生成钥匙的程序；`-t` 选钥匙的种类，`ed25519` 是 GitHub 文档推荐的一种；`-C` 是贴在钥匙上的备注，这里写你的隐私地址：

```zsh
ssh-keygen -t ed25519 -C "12345678+你的用户名@users.noreply.github.com"
```

它会依次问三句话〔建课时无法验证〕：

```text
Generating public/private ed25519 key pair.
Enter file in which to save the key (/Users/你的用户名/.ssh/id_ed25519):
Enter passphrase for "/Users/你的用户名/.ssh/id_ed25519" (empty for no passphrase):
Enter same passphrase again:
```

> 读懂这句：正在生成一对钥匙；钥匙存在哪里（直接回车用默认位置）；给钥匙设一个口令（直接回车表示不设）；再输一遍口令。

第一句直接回车。多出一行 `Created directory` 的话，是它刚替你建了 `.ssh` 文件夹，正常。如果它问 `Overwrite (y/n)?`，说明你以前有过同名的钥匙：输入 `n` 停下，把屏幕发给导师，说“急救：ssh-keygen 问要不要覆盖”。GitHub 文档建议设一个口令；设了口令，以后每次提交它会问你一次，输入时屏幕上什么都不显示，这是正常的。最后你会看到（指纹和图案你的会不一样）：

```text
Your identification has been saved in /Users/你的用户名/.ssh/id_ed25519
Your public key has been saved in /Users/你的用户名/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 12345678+你的用户名@users.noreply.github.com
The key's randomart image is:
```

> 读懂这句：私钥存在 id_ed25519，公钥存在 id_ed25519.pub；这把钥匙的指纹是……；这把钥匙的方框图案是（图案在屏幕上，这里没有抄）。

指纹（fingerprint）是这把钥匙的一串简短编号，用来核对两边是不是同一把；方框图案是把指纹画成图，可以不管。`id_ed25519` 是私钥，只留在你的电脑上，永远不给任何人；`id_ed25519.pub` 是公钥，可以给 GitHub。

**2. 告诉 Git 用这把钥匙签名。** 签名格式（`gpg.format`）用 SSH，签名用的钥匙（`user.signingkey`）是这把公钥，再打开自动签名（`commit.gpgsign`）：

```zsh
git config set --global gpg.format ssh
git config set --global user.signingkey ~/.ssh/id_ed25519.pub
git config set --global commit.gpgsign true
```

三条都没有输出。

**3. 在练习副本里试一次。**

```zsh
cd ~/Developer/playground/1.11-start/my-site
touch signed.txt
git add signed.txt
git commit -m "docs: 试一次签名"
```

如果你的全局设置里有一项 `gpg.ssh.program`（用哪个程序做 SSH 签名），值却是空的，你会看到：

```text
error: cannot run : No such file or directory
error: 
fatal: failed to write commit object
```

> 读懂这句：错误：运行不了“（空）”这个程序，没有这个文件；致命错误：提交没写成。

报错三问：谁在报错？git。关键词？`cannot run` 后面本该是一个程序名，这里却是空的。我刚才做了什么？打开了 SSH 签名，Git 就去运行那个“没有名字的程序”。如果你的提交直接成功了（看到和下面第 4 步一样的三行），说明你的设置里没有这个空值，跳过第 4 步。

**4. 把这一项删掉，再提交一次。** `git config unset --global` 是“从全局设置里删掉这一项”；删掉以后，Git 用它自带的默认程序 `ssh-keygen`：

```zsh
git config unset --global gpg.ssh.program
git commit -m "docs: 试一次签名"
```

你应该看到（编号你的会不一样）：

```text
[main a691335] docs: 试一次签名
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 signed.txt
```

全局设置里如果还有一项值是空的 `gpg.ssh.allowedSignersFile`，它只在你要求 Git 在本机核对签名时才用到（比如 `git log --show-signature` 会多打印几行，其中有一行 `Unable to open allowed keys file ""`），这门课不做这件事，可以不管。以后想撤回签名，运行 `git config set --global commit.gpgsign false`。做完回到第 3 站的「自己做」：新提交要在打开签名以后做，检查会看它上面有没有签名。

**5. 把公钥交给 GitHub〔对照文档，界面可能不同〕。** 头像 → **Settings** → “Access” 里的 **SSH and GPG keys** → **New SSH key**。Title 写一个你认得的名字（比如“我的 Mac 签名”）；Key type 选 **Signing Key**（签名用）；把公钥贴进 Key 框，点 **Add SSH key**。公钥的内容这样拿：运行 `code ~/.ssh/id_ed25519.pub`，在 VS Code 里全选、复制，然后关掉这个文件，不要改它。添加以后，你推送上去的签名提交在 GitHub 网页上打开就会显示 **Verified**（已验证）：第 1.12 课推送以后，在 GitHub 网页上打开那个提交就能看到。

> **旧教程提醒**：以前的教程说“给提交签名必须先装 GPG（一个专门做加密和签名的老牌程序）”；现在 Git 2.34 起可以直接用 SSH 钥匙签名，GitHub 自 2022 年 8 月 23 日起能核对 SSH 签名（GitHub Docs 与 GitHub Changelog，2026-11-19 核对）。

### 链接

- GitHub 文档中文版：配置双重身份验证（中文）https://docs.github.com/zh/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication
- 通行密钥（passkey，GitHub 中文文档叫“密钥”）：存在你设备里、用指纹或设备密码解锁的登录钥匙，只认真正的 github.com，所以很难被钓鱼网站骗走。它是一种登录方式，登录时可以同时顶替密码和双重验证；但它不能当你双重验证的第一种方式：GitHub 要求先用验证器 App（或短信）开好双重验证，才能把通行密钥当作双重验证来用，所以验证器 App 和恢复码照样要留着（GitHub Docs“About passkeys”“Configuring two-factor authentication”，2026-11-20 核对）。说明见“关于密钥”（中文）https://docs.github.com/zh/authentication/authenticating-with-a-passkey/about-passkeys
- gh 默认会发送不带你名字的使用统计（GitHub 的说法是 pseudonymous，假名化）；不想发送，可以运行 `gh config set telemetry disabled`。说明见 GitHub CLI telemetry（English）https://docs.github.com/en/github-cli/github-cli/github-cli-telemetry
