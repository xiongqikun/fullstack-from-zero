"""The state ladder of the learner's website (plan I6): S0 ... S7.

Each state is what ``~/Developer/my-site`` contains at the end of one lesson.
Lesson scenarios rebuild a *copy* of it inside the playground, so that a
lesson can start from the right state without touching the learner's real
site, and so that a learner whose site got broken can be given back the state
the lessons left them with.  Every state mirrors what the lessons' own texts
and checks leave in ``~/Developer/my-site`` (checked against lessons 1.2-1.13
on 2026-11-19):

======  ==================  ==========================================================
State   end of lesson       ``my-site`` contains
======  ==================  ==========================================================
S0      1.1                 does not exist
S1      1.2                 ``index.html``, ``style.css`` copied from the starter
S2      1.4                 the heading and the paragraph edited; ``.editorconfig`` (1.4c)
S3      1.5                 plus ``README.md``
S4      1.6                 a Git repository with two commits (1.6c: first version, README)
S5      1.9                 plus ``.gitignore`` and ``drafts/``; five commits
                            (1.7b: the heading colour; 1.9a: another colour, .gitignore)
S6      1.10                seven commits, the latest two in Conventional Commits form
S7      1.13                ``LICENSE``, the page address, a public remote, the page
                            online; eleven commits
======  ==================  ==========================================================

There is no state at the end of 1.7: the commit lesson 1.7 makes
(「改了标题的颜色」) first appears in S5, so the copy built for 1.8 and 1.9
(S4) has two commits while the learner's own site already has three.

The source of the site is the original of ``starter/my-site`` recorded in
``starter_manifest.json`` (plan G11a), never the workspace copy, which the
learner may have edited.  In S7 a local bare repository
(``<base>/remote/my-site.git``) stands in for GitHub; "the page online" is
represented by ``main`` being pushed to it, which is what GitHub Pages would
serve.

"Global signing handled" (S4) is a property of the learner's global Git
configuration, not of the folder.  Nothing here reads or writes any
configuration outside the repository being built: every commit goes through
``courselib.gitwrite``, which switches the global configuration off, never
signs and uses the practice identity.

A build is deterministic: the same ``seed`` and the same ``now`` give the same
files and the same commit hashes.  Everything is written below ``base`` and
nowhere else.

Entry points:

- ``build_state(name, base, workspace=None, now=None, seed=None, env=None)``
  builds one state and returns the path of the ``my-site`` folder (called by
  ``sc.state``);
- ``build(name, base, ...)`` does the same and returns a ``Built`` with the
  facts (owner name, commit count, remote path ...);
- ``state_before(lesson_id)`` names the state a learner has just before a
  lesson (used by ``sc.site_before``).
"""

import datetime
import os
import random
from pathlib import Path

from . import gitwrite
from . import scenario as _scenario
from .errors import ToolTrouble

#: The ladder in order: name -> (lesson at whose end it is reached, description).
LADDER = (
    ("S0", "1.1", "my-site 还不存在"),
    ("S1", "1.2", "index.html 和 style.css，从 starter 复制过来"),
    ("S2", "1.4", "标题和那段话改过，加了 .editorconfig"),
    ("S3", "1.5", "再加一个 README.md"),
    ("S4", "1.6", "是一个 Git 仓库，有两个提交"),
    ("S5", "1.9", "再加 .gitignore 和 drafts 文件夹，五个提交"),
    ("S6", "1.10", "七个提交，最新的两个符合约定式提交"),
    ("S7", "1.13", "有 LICENSE、网页地址和公开的远程仓库，网页已上线，十一个提交"),
)
NAMES = tuple(name for name, _after, _text in LADDER)
REACHED_AT = {name: after for name, after, _text in LADDER}
DESCRIPTION = {name: text for name, _after, text in LADDER}

SITE = "my-site"
REMOTE = "remote/my-site.git"
STARTER = "starter/my-site"
PAGES_URL = "https://你的用户名.github.io/my-site/"

TEXT = {
    "unknown": "没有 {name} 这个网站状态。可以用的是 S0 到 S7。",
    "exists": "要搭网站状态的位置已经有东西了：{path}",
    "no_starter": "起始文件的原样清单里找不到网站的起始文件：{path}",
    "no_heading": "starter/my-site/index.html 里找不到要改的标题或段落，网站状态搭不了。",
    "no_anchor": "starter/my-site/{file} 和网站状态需要的样子对不上（找不到「{text}」），网站状态搭不了。",
}

# Neutral pen names for the heading of the practice copy.  Never the learner's
# real name (plan G10).
OWNERS = ("小林", "阿青", "小周", "阿木", "小禾", "阿远", "小舟", "阿北")
INTROS = (
    "我在学做网页，每天进步一点。",
    "这是我学写代码时做的第一个网页。",
    "我想把学到的东西一点一点放到这里。",
    "这一页记录我从零开始学做软件的过程。",
)
#: The colour lesson 1.7 tells every learner to give the heading.
LESSON_COLOR = "#c2410c"
#: Colours a learner may pick in 1.9a ("挑一个颜色"); never LESSON_COLOR.
COLORS = ("#2a7f62", "#8a3ffc", "#0e7490", "#b91c1c", "#4d7c0f", "#9333ea")
PLANS = (
    "下一步：学会用 Git 管理改动",
    "下一步：把网页放到网上",
    "下一步：学一点 CSS 排版",
    "下一步：给网页加一张图片",
)
SIZES = ("2rem", "2.25rem", "2.5rem")

STARTER_HEADING = "你好，我是____"
STARTER_PARAGRAPH = "这是我的第一个网页。我正在从零开始学习做软件。"
STARTER_COLOR = "color: #0b5cad;"

EDITORCONFIG = """\
# 告诉编辑器：这个文件夹里的文件用什么编码、怎么换行、怎么缩进
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true

[*.{html,css}]
indent_style = space
indent_size = 2
"""

# Lesson 1.5b: one title, sections, a list, a code block, index.html named.
README = """\
# my-site

{owner}的个人网页：只有一页的小网站，是我学做软件的第一个作品。

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
"""
#: Lesson 1.6c: one sentence saying that Git now records the changes.
README_GIT_LINE = "还在学习中，会一点一点改。\n"
README_GIT = "还在学习中，会一点一点改。\n这个网站现在用 Git 记录每一次改动。\n"
#: Lesson 1.9a: a note that only the learner sees (ignored by .gitignore).
DRAFT_NOTE = "drafts/colors.md"
DRAFT_TEXT = """\
# 想试的标题颜色

- {first}
- {second}
"""
#: Lesson 1.13a: the README's last section names the licence and links to it.
README_LICENSE = "\n## 许可证\n\n本项目使用 MIT 许可证，全文见 [LICENSE](LICENSE)。\n"
#: Lesson 1.13b: a section with the page address.
README_PAGES = "\n## 网页地址\n\n{url}\n"
#: Lesson 1.13c (跟我做): the list line that is now true.
LIST_BEFORE = "      <li>我会把网页放到网上</li>"
LIST_AFTER = "      <li>我已经把网页放到了网上</li>"
#: Lesson 1.13c (自己做): a footer link to the repository page.
FOOTER_ANCHOR = '<a href="https://developer.mozilla.org/zh-CN/">MDN</a>'
FOOTER_LINK = '，<a href="{url}">这个网页的源代码</a>'
REPO_URL = "https://github.com/你的用户名/my-site"

GITIGNORE = """\
# 不放进仓库的东西
# 草稿文件夹：只留在自己电脑上
drafts/
# 编辑器或程序留下的临时文件
*.tmp
# 存放密钥和密码的文件，永远不进仓库
.env
"""

LICENSE = """\
MIT License

Copyright (c) {year} {owner}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Commit subjects, oldest first, with the lesson whose text makes the commit
# in the learner's own site and the first state that contains it.  The first
# five are written the way a beginner writes before lesson 1.10; from the sixth
# on they follow Conventional Commits 1.0.0 with the types of commitlint's
# config-conventional (a bigger heading is a new feature, ``feat``; ``style``
# is formatting that does not change what the page shows).  ``days`` is how
# long before "now" each was made.
COMMITS = (
    {"subject": "第一版网页", "days": 9},                          # 1.6c  -> S4
    {"subject": "在 README 里写上用 Git 记录改动", "days": 9},      # 1.6c  -> S4
    {"subject": "改了标题的颜色", "days": 8},                      # 1.7b  -> S5 (no state ends at 1.7)
    {"subject": "换了一个标题颜色", "days": 6},                    # 1.9a  -> S5
    {"subject": "添加 .gitignore", "days": 6},                     # 1.9a  -> S5
    {"subject": "feat: 在首页加一条学习计划", "days": 4},          # 1.10b -> S6
    {"subject": "feat: 调大标题的字号", "days": 4},                # 1.10b -> S6
    {"subject": "docs: 添加 MIT 许可证", "days": 2},               # 1.13a -> S7
    {"subject": "docs: 在 README 里写上网页地址", "days": 1},      # 1.13b -> S7 (pushed)
    {"subject": "feat: 列表里写上网页已经上线", "days": 0},        # 1.13c -> S7
    {"subject": "feat: 在页脚加上源代码的链接", "days": 0},        # 1.13c -> S7 (pushed)
)
#: How many of COMMITS exist in each state.
COMMIT_COUNT = {"S0": 0, "S1": 0, "S2": 0, "S3": 0, "S4": 2, "S5": 5, "S6": 7, "S7": 11}


class Built:
    """What ``build`` made: ``site`` (Path), ``name`` and ``facts`` (dict)."""

    def __init__(self, name, site, facts):
        self.name = name
        self.site = Path(site)
        self.facts = dict(facts)

    def __repr__(self):
        return f"<Built {self.name} {self.site}>"


def normalise_name(name):
    """ "s4" -> "S4"; raises ``ToolTrouble`` for anything that is not S0-S7."""
    text = str(name).strip().upper()
    if text not in NAMES:
        raise ToolTrouble(TEXT["unknown"].format(name=name))
    return text


def state_before(lesson_id):
    """The ladder state a learner has just before lesson ``lesson_id`` starts.

    "1.7" -> "S4" (S4 is reached at the end of 1.6).  Lessons of stage 0 and
    1.1 start from S0.  A lesson id that cannot be read gives "S0".
    """
    key = _lesson_key(lesson_id)
    best = "S0"
    for name, after, _text in LADDER:
        if _lesson_key(after) < key:
            best = name
    return best


def state_after(lesson_id):
    """The ladder state a learner has at the end of lesson ``lesson_id``."""
    key = _lesson_key(lesson_id)
    best = "S0"
    for name, after, _text in LADDER:
        if _lesson_key(after) <= key:
            best = name
    return best


def _lesson_key(lesson_id):
    parts = str(lesson_id).split(".")
    try:
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return (-1, -1)


def _rank(name):
    return NAMES.index(name)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _read(path):
    with open(str(path), "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _replace_once(text, old, new, file_name):
    if old not in text:
        raise ToolTrouble(TEXT["no_anchor"].format(file=file_name, text=old.strip()))
    return text.replace(old, new, 1)


def _choices(seed):
    """Every seeded choice of the ladder, made once, in a fixed order."""
    rng = random.Random(int(seed) * 7919 + 104729)
    picks = {
        "owner": rng.choice(OWNERS),
        "intro": rng.choice(INTROS),
        "color": rng.choice(COLORS),
        "plan": rng.choice(PLANS),
        "size": rng.choice(SIZES),
    }
    picks["other_color"] = rng.choice([c for c in COLORS if c != picks["color"]])
    return picks


def build(name, base, workspace=None, now=None, seed=None, env=None, manifest=None):
    """Build ladder state ``name`` in ``<base>/my-site`` and return a ``Built``.

    The starter files come from the original recorded in the starter manifest
    (``manifest``: a dict as ``courselib.scenario.load_starter_manifest``
    returns it, default the tool's own), never from the workspace.
    ``workspace`` is accepted for compatibility and no longer read.  ``now``
    is the build time (commit dates are counted back from it); ``seed`` makes
    the names and small edits differ between learners; ``env`` the
    environment for Git (default: this process's).
    """
    name = normalise_name(name)
    base = Path(base)
    now = (now or datetime.datetime.now()).replace(microsecond=0, tzinfo=None)
    seed = 0 if seed is None else int(seed)
    env = dict(os.environ if env is None else env)
    site = base / SITE
    if site.exists() or site.is_symlink():
        raise ToolTrouble(TEXT["exists"].format(path=site))
    picks = _choices(seed)
    rank = _rank(name)
    facts = {"state": name, "site": SITE, "commits": COMMIT_COUNT[name],
             "owner": picks["owner"] if rank >= _rank("S2") else None}
    if rank == 0:
        return Built(name, site, facts)

    # S1 (1.2a): the original starter files
    originals = _starter_site(manifest)
    base.mkdir(parents=True, exist_ok=True)
    site.mkdir()
    for file_name in ("index.html", "style.css"):
        with open(str(site / file_name), "wb") as handle:
            handle.write(originals[file_name])
    if rank == _rank("S1"):
        return Built(name, site, facts)

    # S2 (1.4a): the heading and the paragraph edited; (1.4c) .editorconfig
    page = _read(site / "index.html")
    if STARTER_HEADING not in page or STARTER_PARAGRAPH not in page:
        raise ToolTrouble(TEXT["no_heading"])
    page = page.replace(STARTER_HEADING, "你好，我是" + picks["owner"], 1)
    page = page.replace(STARTER_PARAGRAPH, picks["intro"], 1)
    _write(site / "index.html", page)
    _write(site / ".editorconfig", EDITORCONFIG)
    facts["heading"] = "你好，我是" + picks["owner"]
    facts["paragraph"] = picks["intro"]
    if rank == _rank("S2"):
        return Built(name, site, facts)

    # S3 (1.5b): a README
    _write(site / "README.md", README.format(owner=picks["owner"]))
    if rank == _rank("S3"):
        return Built(name, site, facts)

    # S4 (1.6c): a repository, the first version, then one README sentence
    gitwrite.git_init(site, env)
    _commit(site, env, now, 0)
    _edit(site / "README.md", README_GIT_LINE, README_GIT)
    _commit(site, env, now, 1)
    if rank >= _rank("S5"):
        # 1.7b: the colour every learner is told to use
        _edit(site / "style.css", STARTER_COLOR, f"color: {LESSON_COLOR};")
        _commit(site, env, now, 2)
        # 1.9a: a colour of the learner's choice, then .gitignore; the drafts
        # note stays on the computer only (ignored)
        _edit(site / "style.css", f"color: {LESSON_COLOR};",
              "color: {};".format(picks["color"]))
        _commit(site, env, now, 3)
        _write(site / ".gitignore", GITIGNORE)
        _write(site / DRAFT_NOTE, DRAFT_TEXT.format(first=picks["color"],
                                                    second=picks["other_color"]))
        _commit(site, env, now, 4)
        facts["color"] = picks["color"]
    if rank >= _rank("S6"):
        # 1.10b: two unrelated improvements, one commit each
        _edit(site / "index.html", "    </ul>",
              "      <li>{}</li>\n    </ul>".format(picks["plan"]))
        _commit(site, env, now, 5)
        colour = "color: {};".format(picks["color"])
        _edit(site / "style.css", colour, "{}\n  font-size: {};".format(colour, picks["size"]))
        _commit(site, env, now, 6)
        facts["plan"] = picks["plan"]
    if rank >= _rank("S7"):
        # 1.13a: LICENSE and the README's licence section in one commit
        year = (now - datetime.timedelta(days=COMMITS[7]["days"])).year
        _write(site / "LICENSE", LICENSE.format(year=year, owner=picks["owner"]))
        _append(site / "README.md", README_LICENSE)
        _commit(site, env, now, 7)
        # 1.13b: the page address, pushed to the stand-in for GitHub
        _append(site / "README.md", README_PAGES.format(url=PAGES_URL))
        _commit(site, env, now, 8)
        remote = base / REMOTE
        gitwrite.git_init(remote, env, bare=True)
        gitwrite.run_git(site, ["remote", "add", "origin", str(remote)], env)
        gitwrite.run_git(site, ["push", "--quiet", "-u", "origin", gitwrite.DEFAULT_BRANCH], env)
        # 1.13c: one list line made true, then a footer link; both pushed
        _edit(site / "index.html", LIST_BEFORE, LIST_AFTER)
        _commit(site, env, now, 9)
        _edit(site / "index.html", FOOTER_ANCHOR,
              FOOTER_ANCHOR + FOOTER_LINK.format(url=REPO_URL))
        _commit(site, env, now, 10)
        gitwrite.run_git(site, ["push", "--quiet", "origin", gitwrite.DEFAULT_BRANCH], env)
        facts["remote"] = REMOTE
        facts["pages_url"] = PAGES_URL
    facts["head"] = gitwrite.run_git(site, ["rev-parse", "HEAD"], env).out.strip()
    return Built(name, site, facts)


def _starter_site(manifest=None):
    """``{"index.html": bytes, "style.css": bytes}``: the originals of starter/my-site."""
    try:
        originals = _scenario.starter_originals(STARTER, manifest)
    except ToolTrouble:
        raise ToolTrouble(TEXT["no_starter"].format(path=STARTER))
    for file_name in ("index.html", "style.css"):
        if file_name not in originals:
            raise ToolTrouble(TEXT["no_starter"].format(path=STARTER + "/" + file_name))
    return originals


def _edit(path, old, new):
    """Replace ``old`` by ``new`` once in the file ``path`` (``ToolTrouble`` if absent)."""
    _write(path, _replace_once(_read(path), old, new, path.name))


def _append(path, text):
    _write(path, _read(path).rstrip("\n") + "\n" + text)


def _commit(site, env, now, number):
    entry = COMMITS[number]
    # Counted back from "now", one minute apart within a day, so the order is
    # stable and no commit lies in the future.
    when = (now - datetime.timedelta(days=entry["days"], hours=2)
            + datetime.timedelta(minutes=number))
    return gitwrite.git_commit(site, entry["subject"], env, add="all", date=when)


def build_state(name, base, workspace=None, now=None, seed=None, env=None, manifest=None):
    """Build ladder state ``name`` under ``base``; return the ``my-site`` path.

    This is the function ``sc.state(name, base)`` calls.  For S0 the returned
    folder does not exist.
    """
    return build(name, base, workspace=workspace, now=now, seed=seed, env=env,
                 manifest=manifest).site
