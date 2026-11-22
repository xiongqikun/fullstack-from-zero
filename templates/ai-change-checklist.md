# 验收 AI 的改动：五个问题

AI（包括导师）改完东西，你先按这一页过一遍，五个都答“没问题”，再决定收不收。这一页来自行规 AI-01（第 1.15 课）：AI 的改动先看 diff 再接受。

先在项目文件夹里运行这三条命令，再打开看一次效果：

```zsh
git status
git diff --stat
git diff
```

- `git status`：哪些文件改了，有没有新文件（新文件在 Untracked files 下面）。
- `git diff --stat`：每个文件改了几行，先看个大概。
- `git diff`：一行一行看改了什么（输出很长、屏幕最下面出现 `:` 时，按 q 退出）。
- 看效果：网页就运行 `open index.html`；程序就运行一次，比如 `python3 convert.py`。

## 五个问题

1. 改的是不是我要的？
2. 有没有多改？（我没提到的文件、没提到的地方）
3. 能不能正常显示？（打开网页或运行程序看一次）
4. 有没有新增文件？（新文件在 `git status` 的 Untracked files 下面）
5. 有没有不该出现的内容？（密钥、密码、真实姓名、电话、住址）

有一个答不上来或者“有问题”，先别提交：请 AI 改，或者自己改，改完从第 1 题重新过一遍。

## 收下以后

AI 参与的提交加尾注：`-m "Co-Authored-By: Claude <noreply@anthropic.com>"`

例如：`git commit -m "feat: 在首页加一节我在学什么" -m "Co-Authored-By: Claude <noreply@anthropic.com>"`（行规 AI-02）。
