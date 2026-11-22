"""``doctor [--net]``: a read-only report on the learner's environment (plan I4).

Three groups: 没问题 (ok) / 需要处理 (todo) / 仅提示 (info).  Every line says
what was looked at; a todo line names the lesson (or the tutor) that handles
it.  The command changes no setting and no repository.  Its only write is
``learner/last-result.json`` (through ``app.store.write_result``), so that the
tutor can read the findings; that record never contains the Git identity
values, which are not even kept in memory beyond "set / not set".

Each check runs on its own: a check that cannot look (a program missing, a
timeout, an unexpected error) becomes a 仅提示 line "无法判断" and the other
checks go on.  The exit code is 0 unless the doctor itself failed (for
example ``learner/`` cannot be written).

``learner/state.json`` is read directly and only for reading (never through
``app.store.load()``, so a damaged file changes nothing here): the decision
``workspace_location`` of lesson 0.2c and which stations have passed (lesson
1.11, station 1.12a and later lessons: whether the learner reached lesson 1.12).
Starter files are compared with ``starter_manifest.json`` (plan G11a).

Things a test may replace (module attributes, not environment variables, so
that the learner never sees a knob): ``XATTR`` (path of the program that
lists extended attributes), ``NET_URL`` and ``NET_TIMEOUT``, ``open_url`` (the
function that makes the --net request).
"""

import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from .. import cmdkit, gitread, syllabus
from .. import scenario as scenarios
from ..errors import EXIT_OK, ToolTrouble
from ..store import reason as os_reason

XATTR = "/usr/bin/xattr"
ICLOUD_ATTRIBUTE = "com.apple.file-provider-domain-id"
NET_URL = "https://github.com"
NET_TIMEOUT = 8
RUN_TIMEOUT = 10
XATTR_TIMEOUT = 5
MIN_PYTHON = (3, 9)
#: Lesson 1.6 handles signing that fails because gpg is missing (plan G7);
#: lesson 1.11 is where SSH signing is chosen and set up.
GPG_SIGNING_LESSON = "1.6"
SSH_SIGNING_LESSON = "1.11"
#: The lesson that installs gh when the baseline does not name one.
GH_LESSON = "1.11"
#: A .git in the workspace root is the learner's own git init of lesson 1.12
#: once this lesson is done (or a later lesson has a passed station).
WORKSPACE_REPO_BEFORE = "1.11"
VI_NAMES = ("vi", "vim")
#: Programs that "edit" nothing: Git would accept an empty message silently.
NOT_EDITORS = ("true", ":", "false", "cat")

OK = "ok"
TODO = "todo"
INFO = "info"
GROUPS = (OK, TODO, INFO)

BASELINE = Path(__file__).resolve().parent.parent / "baseline.json"

SUMMARY = "检查这台电脑的学习环境（只看不改）"

DESCRIPTION = """\
检查这台电脑上和课程有关的设置，分三组列出：没问题 / 需要处理 / 仅提示。
"需要处理"的每一行都写了哪一课会带你处理，不用现在自己动手。
这个命令只看不改；结果另存一份到 learner/last-result.json，导师可以直接看。
Git 的用户名和邮箱只说"已设置"或"未设置"，不会显示内容。

例子：
  python3 tools/course.py doctor
  python3 tools/course.py doctor --net     也检查能不能连上 github.com"""

TEXT = {
    "title": "环境检查 · {date}",
    "intro": "只看不改：这个命令不会改动你电脑上的任何设置。",
    "group_ok": "没问题",
    "group_todo": "需要处理",
    "group_info": "仅提示",
    "group_count": "{name}（{n} 项）",
    "group_empty": "（没有）",
    "arrow": " → {who}",
    "lesson": "第 {lesson} 课会带你处理",
    "tutor": "把这一行发给导师",
    # The lesson that handles a todo line is already done: no future tense.
    "tutor_after": "第 {lesson} 课已经学过了，把这一行发给导师",
    "summary_todo": "小结：有 {n} 项需要处理。每一项后面写了谁来处理，不用现在自己动手。",
    "summary_clean": "小结：没有需要处理的事。",
    "saved": "这份结果也存到了 learner/last-result.json，导师可以直接看。",
    "help_net": "也检查能不能连上 github.com（最多等 {seconds} 秒，不发送任何数据）",
    "failed_check": "{topic}：这一项没查成（{reason}），无法判断。",
    "internal_error": "工具内部出错",
    # -- topics (what was looked at) ----------------------------------------
    "t_macos": "macOS 版本",
    "t_shell": "登录用的 shell",
    "t_python": "python3",
    "t_git": "Git",
    "t_identity": "Git 身份（user.name 和 user.email）",
    "t_signing": "提交签名",
    "t_editor": "Git 的编辑器",
    "t_branch": "新仓库的第一个分支名",
    "t_excludes": "全局忽略文件",
    "t_workspace": "学习工作区的位置",
    "t_developer": "~/Developer 文件夹",
    "t_code": "code 命令（从终端打开 VS Code）",
    "t_gh": "GitHub CLI（gh 命令）",
    "t_net": "能不能连上 github.com",
    # -- macOS --------------------------------------------------------------
    "macos_ok": "macOS 版本：{version}",
    "macos_older": "macOS 版本：{version}，比课程核对时用的 {baseline} 旧。界面和课文可能有出入，遇到对不上的地方告诉导师。",
    "macos_missing": "macOS 版本：找不到 sw_vers 命令，无法判断（这台电脑可能不是 Mac）。",
    "macos_unknown": "macOS 版本：sw_vers 的输出看不懂，无法判断。",
    # -- shell --------------------------------------------------------------
    "shell_ok": "登录用的 shell：zsh {version}（{path}）",
    "shell_ok_noversion": "登录用的 shell：zsh（{path}，版本看不出来）",
    "shell_other": "登录用的 shell：{name}（{path}）。课程是按 zsh 写的，提示符和配置文件的名字会和课文不同；把这一行告诉导师。",
    "shell_unknown": "登录用的 shell：环境变量 SHELL 没有设置，无法判断。",
    # -- python3 --------------------------------------------------------------
    "python_ok": "python3：{version}（{path}，PATH 里排第一个的 python3）",
    "python_old": "python3：PATH 里排第一个的是 {path}，版本 {version}，太旧了。课程的工具至少要 Python 3.9。",
    "python_missing": "python3：在 PATH 里找不到。课程从第 0.1 课起就要用它。",
    "python_unknown": "python3：找到了 {path}，但看不懂它报的版本，无法判断。",
    # -- git ----------------------------------------------------------------
    "git_ok": "Git：{version}",
    "git_missing": "Git：在 PATH 里找不到 git 命令。第 1.6 课开始要用它。",
    "git_broken": "Git：git 命令在，但运行失败（{reason}）。多半是还没装开发者工具（Command Line Tools）。",
    "git_bad_config": "Git：git 命令在，但它的设置文件有一行写坏了（{reason}）。多半是 ~/.gitconfig 被改坏了，Git 的每条命令都会失败。",
    "git_who": "第 1.6 课之前要弄好，把这一行发给导师",
    "git_skipped": "Git 的设置：因为 git 用不了，身份、签名、编辑器这些都没法查。",
    # -- identity -----------------------------------------------------------
    "identity_ok": "Git 身份：user.name 已设置，user.email 已设置（这里不显示内容）。",
    "identity_todo": ("Git 身份：user.name {name}，user.email {email}。没设置的那一项，Git 会拿这台 Mac 的"
                      "账户名和电脑名自己拼一个：提交照样能成功，只是会多打印一段英文提示，"
                      "拼出来的名字和地址也会记进每一个提交里。"),
    "identity_who": "第 1.6 课会带你正式设好",
    "set": "已设置",
    "unset": "未设置",
    # -- signing ------------------------------------------------------------
    "signing_off": "提交签名：没有打开。",
    "signing_ok": "提交签名：已经打开（格式 {format}），签名程序 {program} 找到了。钥匙能不能用，要第一次提交时才知道。",
    "signing_no_program": "提交签名：已经打开（commit.gpgsign=true，格式 {format}），但找不到签名程序 {program}。现在每次 git commit 都会失败。",
    "signing_empty_program": ("提交签名：已经打开（commit.gpgsign=true，格式 {format}），但设置 {key} 是空的："
                              "Git 会去运行一个没有名字的程序。现在每次 git commit 都会失败。"),
    "signing_ssh_ok": "提交签名：已经打开（格式 ssh），签名程序和钥匙都找到了。",
    "signing_ssh_no_key": ("提交签名：已经打开（commit.gpgsign=true，格式 ssh），但没有设置用哪把钥匙"
                           "（user.signingkey）。现在每次 git commit 都会失败。"),
    "signing_ssh_missing_key": ("提交签名：已经打开（commit.gpgsign=true，格式 ssh），但设置里写的钥匙文件 {path} "
                                "不存在。现在每次 git commit 都会失败。"),
    "signing_unknown_format": "提交签名：已经打开，但签名格式 gpg.format={format} 看不懂，无法判断。",
    "signing_unreadable": "提交签名：commit.gpgsign 的值看不懂，无法判断。",
    # -- editor -------------------------------------------------------------
    "editor_ok": "Git 的编辑器：{editor}",
    "editor_vi": "Git 的编辑器：{editor}。提交时如果没写 -m，Git 会打开它，新手容易卡在里面。第 1.6 课会把它换掉。",
    "editor_unknown": "Git 的编辑器：git var GIT_EDITOR 没有给出答案，无法判断。",
    "editor_none": "Git 的编辑器：{editor}。这不是一个真正的编辑器（多半是环境变量 GIT_EDITOR 设成了它），提交时不写 -m 也不会打开任何东西。把这一行告诉导师。",
    # -- default branch -----------------------------------------------------
    "branch_ok": "新仓库的第一个分支名：main",
    "branch_other": "新仓库的第一个分支名：{branch}。课程的例子里写的是 main，第 1.6 课会讲到；在那之前看到 {branch} 不用慌。",
    "branch_unknown": "新仓库的第一个分支名：无法判断。",
    # -- excludes file ------------------------------------------------------
    "excludes_ok": "全局忽略文件：有（{path}）",
    "excludes_default_ok": "全局忽略文件：有（{path}，Git 默认的位置）",
    "excludes_none": "全局忽略文件：没有。第 1.9 课会讲忽略文件是什么。",
    "excludes_missing": "全局忽略文件：设置里写的是 {path}，但这个文件不存在。不影响使用，第 1.9 课会讲。",
    # -- workspace ----------------------------------------------------------
    "ws_ok": "学习工作区的位置：{path}，不在同步到云端的文件夹里。",
    "ws_synced": "学习工作区的位置：{path}，在{provider}同步的文件夹里（{ancestor}）。代码放在同步盘里容易出怪问题。",
    "ws_mobile": "学习工作区的位置：{path}，在 iCloud 云盘（iCloud Drive）里。代码放在同步盘里容易出怪问题。",
    "ws_unknown": "学习工作区的位置：{path}。有没有在同步盘里无法判断（{reason}）。",
    "ws_entrance": "~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero 照样能用。",
    "ws_entrance_synced": ("~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero 照样能用；"
                           "学习工作区本身还在同步盘里。"),
    "ws_decided": "这是你在第 0.2 课做的决定：先留在原处。",
    "ws_decided_who": "第 1.12 课把课程变成仓库之前，会再问你一次",
    "ws_no_entrance": ("~/Developer/fullstack-from-zero 这个入口还没有建，课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。"
                       "第 1.12 课把课程变成仓库之前，会再问你一次要不要搬。"),
    "ws_bad_entrance": ("~/Developer/fullstack-from-zero 有一个入口，但它没有通到这个学习工作区（指向的地方不存在，或者是别的文件夹），"
                        "课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。"
                        "第 1.12 课把课程变成仓库之前，会再问你一次要不要搬。"),
    "ws_entrance_who": "对导师说“我先不搬，帮我在 ~/Developer 建一个入口”",
    # Without the clause on lesson 1.12: not synced, or lesson 1.12 already done.
    "ws_no_entrance_plain": "~/Developer/fullstack-from-zero 这个入口还没有建，课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。",
    "ws_bad_entrance_plain": ("~/Developer/fullstack-from-zero 有一个入口，但它没有通到这个学习工作区（指向的地方不存在，或者是别的文件夹），"
                              "课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。"),
    "ws_decided_who_after": "第 1.12 课已经问过你了；想搬的时候对导师说“帮我把课程安置到 ~/Developer”",
    "ws_git": ("学习工作区：最外层有一个 .git，学习工作区已经被当成了一个仓库。把学习工作区变成仓库是"
               "第 1.12 课的事，现在出现，多半是在错的文件夹里运行了 git init。先什么都不要删。"),
    "ws_git_who": "对导师说“急救：学习工作区里多了 .git”",
    "provider_icloud": " iCloud ",
    "provider_other": "云盘",
    "why_no_xattr": "找不到 {program}",
    "why_xattr_failed": "{program} 查看 {folder} 时失败了",
    "why_timeout": "{program} 超过 {seconds} 秒没有结束",
    # -- starter ------------------------------------------------------------
    "t_starter": "练习用的起始文件（starter/）",
    "starter_changed": ("练习用的起始文件（starter/）：{files}，和课程原来的样子对不上。练习不受影响："
                        "练习场景和考试用的都是工具里存的原样。想恢复原样，对导师说“急救：starter 被改动了”。"),
    "starter_one_changed": "{path} 改过",
    "starter_one_missing": "{path} 不见了",
    "starter_more": "等 {n} 个文件",
    # -- ~/Developer --------------------------------------------------------
    "dev_ok": "~/Developer 文件夹：有。",
    "dev_missing": "~/Developer 文件夹：还没有。第 0.2 课会建立它。",
    "dev_not_folder": "~/Developer：有一个同名的东西，但不是文件夹。把这一行告诉导师。",
    # -- code ---------------------------------------------------------------
    "code_ok": "code 命令：有（{path}）",
    "code_missing": "code 命令：在 PATH 里找不到。第 0.1 课第 3 站要用它打开文件。",
    "code_who": "对导师说“急救：code 命令找不到”",
    # -- gh -----------------------------------------------------------------
    "gh_missing": "GitHub CLI（gh）：还没安装。第 {lesson} 课会带你装，在那之前用不到。",
    "gh_missing_late": "GitHub CLI（gh）：在 PATH 里找不到。第 {lesson} 课装过它，后面的课还要用。",
    "gh_present": "GitHub CLI（gh）：已经装了（{version}）。第 {lesson} 课才用到。",
    "gh_ok": "GitHub CLI（gh）：{version}",
    "version_unknown": "版本看不出来",
    # -- network ------------------------------------------------------------
    "net_skipped": "能不能连上 github.com：这次没有检查（要检查就加 --net）。",
    "net_ok": "能不能连上 github.com：{seconds} 秒内连上了。",
    "net_failed": "能不能连上 github.com：{seconds} 秒内没连上（{reason}）。第 1.11 课起才需要；到时还连不上就告诉导师。",
    "net_timeout": "等太久",
    "net_error": "连接出错",
}


# ---------------------------------------------------------------------------
# Plug-in protocol
# ---------------------------------------------------------------------------
#: Pointers that speak of a lesson still to come; replaced once it is done.
_FUTURE_WHO = (TEXT["git_who"], TEXT["identity_who"])


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "doctor", SUMMARY, description=DESCRIPTION)
    parser.add_argument("--net", action="store_true",
                        help=TEXT["help_net"].format(seconds=NET_TIMEOUT))
    return parser


def run(args):
    app = args.app
    doctor = Doctor(app, net=bool(getattr(args, "net", False)))
    findings = doctor.examine()
    for line in render(app, findings):
        app.console.out(line)
    app.console.flush()
    # The report is on the screen before anything is written: if the write
    # fails, the learner still has it and sees 检查器出问题 below it.
    app.store.write_result(result_record(findings, doctor.net))
    app.console.out("")
    app.console.out(TEXT["saved"])
    return EXIT_OK


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------
class Finding:
    """One line of the report."""

    def __init__(self, key, group, text, lesson=None, who=None):
        self.key = key
        self.group = group
        self.text = text
        self.lesson = lesson
        self.who = who

    def line(self):
        """The text as shown, with "→ who handles it" for a todo line."""
        if self.group != TODO:
            return self.text
        if self.who:
            who = self.who
        elif self.lesson:
            who = TEXT["lesson"].format(lesson=self.lesson)
        else:
            who = TEXT["tutor"]
        return self.text + TEXT["arrow"].format(who=who)

    def to_dict(self):
        data = {"key": self.key, "group": self.group, "text": self.line()}
        if self.lesson:
            data["lesson"] = self.lesson
        return data

    def __repr__(self):
        return f"<Finding {self.key} {self.group}>"


def render(app, findings):
    lines = [TEXT["title"].format(date=app.today.isoformat()), TEXT["intro"]]
    marks = {OK: "✅ ", TODO: "⚠️ ", INFO: ""}
    paint = {OK: "ok", TODO: "warn", INFO: "bold"}
    for group in GROUPS:
        items = [f for f in findings if f.group == group]
        name = TEXT["group_" + group]
        lines.append("")
        lines.append(app.console.paint(
            marks[group] + TEXT["group_count"].format(name=name, n=len(items)), paint[group]))
        if not items:
            lines.append("  " + TEXT["group_empty"])
        for item in items:
            lines.append("  - " + item.line())
    todo = len([f for f in findings if f.group == TODO])
    lines.append("")
    if todo:
        lines.append(TEXT["summary_todo"].format(n=todo))
    else:
        lines.append(TEXT["summary_clean"])
    return lines


def result_record(findings, net):
    counts = {group: len([f for f in findings if f.group == group]) for group in GROUPS}
    return {
        "kind": "doctor",
        "target": "doctor",
        "net": bool(net),
        "counts": counts,
        "findings": [f.to_dict() for f in findings],
    }


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
class RunFailed(Exception):
    """A program could not be run or did not finish in time."""


def parse_version(text):
    """The first dotted number in ``text`` as a tuple of ints, or None."""
    match = re.search(r"(\d+(?:\.\d+)+|\d+)", str(text or ""))
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def version_text(numbers):
    return ".".join(str(n) for n in numbers)


def read_baseline_version(tool):
    """The baseline version of ``tool`` as a tuple, or None (never raises)."""
    try:
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
        return parse_version(data["tools"][tool]["version"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def read_baseline_entry(tool):
    """The baseline entry of ``tool`` as a dict, {} when unreadable (never raises)."""
    try:
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
        entry = data["tools"][tool]
        return entry if isinstance(entry, dict) else {}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def account_home():
    """Home folder of the login account from the user database, or ""."""
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_dir or ""
    except (ImportError, KeyError, OSError, AttributeError):
        return ""


def first_line(text, limit=80):
    for line in str(text or "").splitlines():
        if line.strip():
            line = line.strip()
            return line if len(line) <= limit else line[: limit - 1] + "…"
    return ""


class Doctor:
    """Runs every check for one App and collects the findings."""

    def __init__(self, app, net=False):
        self.app = app
        self.net = net
        self._state = None
        self.env = app.child_env()
        self.path_list = self.env.get("PATH", "")
        self.findings = []
        self.git_ok = False
        self.reader = gitread.GitReader(self.env, timeout=RUN_TIMEOUT)

    # -- running programs ---------------------------------------------------
    def which(self, name):
        """Absolute path of program ``name`` (a bare name or a path), or None."""
        if not name:
            return None
        if os.sep in name:
            path = self.app.expand(name)
            return str(path) if path.is_file() and os.access(str(path), os.X_OK) else None
        return shutil.which(name, path=self.path_list)

    def run(self, argv, timeout=RUN_TIMEOUT):
        """``(code, out, err)`` of a finished program; RunFailed otherwise."""
        env = dict(self.env)
        env["LC_ALL"] = "C"
        try:
            done = subprocess.run([str(a) for a in argv], env=env, cwd="/",
                                  stdin=subprocess.DEVNULL, capture_output=True,
                                  timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            raise RunFailed("timeout")
        except OSError as exc:
            raise RunFailed(type(exc).__name__)
        return (done.returncode, done.stdout.decode("utf-8", "replace"),
                done.stderr.decode("utf-8", "replace"))

    def git(self, *args):
        """A read-only git command run from "/" (never inside a repository)."""
        return self.reader.run("/", *args)

    def config(self, key, kind=None):
        """The effective value of ``key`` outside any repository, or None.

        Raises ValueError when Git cannot read the value as ``kind``.
        """
        args = ["config"]
        if kind:
            args.append("--type=" + kind)
        args += ["--get", key]
        result = self.git(*args)
        if result.code == 0:
            return result.out.rstrip("\n")
        if result.code == 1:
            return None
        raise ValueError(first_line(result.err))

    def show(self, path):
        return self.scrub(self.app.show(path))

    def scrub(self, text):
        """``app.scrub`` plus the login account's own home folder.

        In a simulation (HOME points elsewhere) programs still come from the
        real account's folders; their paths must not carry the user name.
        """
        text = self.app.scrub(text)
        account = account_home()
        if account and account not in ("/", str(self.app.home)):
            text = text.replace(account.rstrip("/") + "/", "~/")
        return text

    def add(self, key, group, text, lesson=None, who=None):
        if group == TODO and lesson and (who is None or who in _FUTURE_WHO) \
                and self.lesson_done(lesson):
            # "→ 第 1.6 课会带你处理" is untrue once lesson 1.6 is done.
            who = TEXT["tutor_after"].format(lesson=lesson)
        self.findings.append(Finding(key, group, self.scrub(text), lesson=lesson, who=who))

    # -- the whole examination ----------------------------------------------
    def examine(self):
        checks = [
            ("macos", "t_macos", self.check_macos),
            ("shell", "t_shell", self.check_shell),
            ("python3", "t_python", self.check_python),
            ("git", "t_git", self.check_git),
            ("git.identity", "t_identity", self.check_identity),
            ("git.signing", "t_signing", self.check_signing),
            ("git.editor", "t_editor", self.check_editor),
            ("git.branch", "t_branch", self.check_branch),
            ("git.excludes", "t_excludes", self.check_excludes),
            ("workspace", "t_workspace", self.check_workspace),
            ("workspace.git", "t_workspace", self.check_workspace_git),
            ("starter", "t_starter", self.check_starter),
            ("developer", "t_developer", self.check_developer),
            ("code", "t_code", self.check_code),
            ("gh", "t_gh", self.check_gh),
            ("net", "t_net", self.check_net),
        ]
        for key, topic, check in checks:
            if key.startswith("git.") and not self.git_ok:
                continue
            try:
                check()
            except Exception as exc:  # noqa: BLE001 - one broken check never stops the others
                if isinstance(exc, ToolTrouble):
                    reason = exc.summary
                elif isinstance(exc, OSError):
                    reason = os_reason(exc)
                else:
                    reason = TEXT["internal_error"]
                self.add(key, INFO, TEXT["failed_check"].format(topic=TEXT[topic], reason=reason))
        return self.findings

    # -- system -------------------------------------------------------------
    def check_macos(self):
        program = self.which("sw_vers")
        if not program:
            self.add("macos", INFO, TEXT["macos_missing"])
            return
        try:
            code, out, _ = self.run([program, "-productVersion"])
        except RunFailed:
            code, out = 1, ""
        version = parse_version(out) if code == 0 else None
        if not version:
            self.add("macos", INFO, TEXT["macos_unknown"])
            return
        baseline = read_baseline_version("macos")
        if baseline and version[:1] < baseline[:1]:
            self.add("macos", INFO, TEXT["macos_older"].format(
                version=version_text(version), baseline=version_text(baseline)))
        else:
            self.add("macos", OK, TEXT["macos_ok"].format(version=version_text(version)))

    def check_shell(self):
        shell = self.env.get("SHELL", "").strip()
        if not shell:
            self.add("shell", INFO, TEXT["shell_unknown"])
            return
        name = os.path.basename(shell)
        if name != "zsh":
            self.add("shell", INFO, TEXT["shell_other"].format(name=name, path=self.show(shell)))
            return
        version = None
        try:
            code, out, _ = self.run([shell, "--version"])
            if code == 0:
                match = re.search(r"zsh (\d+(?:\.\d+)+)", out)
                version = match.group(1) if match else None
        except RunFailed:
            version = None
        if version:
            self.add("shell", OK, TEXT["shell_ok"].format(version=version, path=self.show(shell)))
        else:
            self.add("shell", OK, TEXT["shell_ok_noversion"].format(path=self.show(shell)))

    def check_python(self):
        program = self.which("python3")
        if not program:
            self.add("python3", TODO, TEXT["python_missing"])
            return
        try:
            code, out, err = self.run([program, "--version"])
        except RunFailed:
            code, out, err = 1, "", ""
        match = re.search(r"Python (\d+(?:\.\d+)+)", out + "\n" + err) if code == 0 else None
        if not match:
            self.add("python3", INFO, TEXT["python_unknown"].format(path=self.show(program)))
            return
        version = parse_version(match.group(1))
        if version[:2] < MIN_PYTHON:
            self.add("python3", TODO, TEXT["python_old"].format(
                path=self.show(program), version=match.group(1)))
        else:
            self.add("python3", OK, TEXT["python_ok"].format(
                version=match.group(1), path=self.show(program)))

    # -- Git ----------------------------------------------------------------
    def check_git(self):
        program = self.which("git")
        if not program:
            self.add("git", TODO, TEXT["git_missing"], lesson="1.6", who=TEXT["git_who"])
            self.add("git.skipped", INFO, TEXT["git_skipped"])
            return
        try:
            code, out, err = self.run([program, "--version"])
        except RunFailed as exc:
            code, out, err = 1, "", str(exc)
        match = re.search(r"git version (\S+)(.*)", out) if code == 0 else None
        if not match:
            reason = first_line(err) or first_line(out) or f"exit {code}"
            key = "git_bad_config" if "bad config" in (err + out) else "git_broken"
            self.add("git", TODO, TEXT[key].format(reason=reason), lesson="1.6",
                     who=TEXT["git_who"])
            self.add("git.skipped", INFO, TEXT["git_skipped"])
            return
        self.git_ok = True
        self.add("git", OK, TEXT["git_ok"].format(version=(match.group(1) + match.group(2)).strip()))

    def check_identity(self):
        # Only "set / not set" leaves this function: the values are dropped here.
        name_set = bool((self.config("user.name") or "").strip())
        email_set = bool((self.config("user.email") or "").strip())
        if name_set and email_set:
            self.add("git.identity", OK, TEXT["identity_ok"])
        else:
            # Verified with Git 2.54 in a simulation home without identity: a
            # commit succeeds, made by "<account full name> <user@computer.local>",
            # with the notice "Your name and email address were configured
            # automatically based on your username and hostname".
            self.add("git.identity", TODO, TEXT["identity_todo"].format(
                name=TEXT["set"] if name_set else TEXT["unset"],
                email=TEXT["set"] if email_set else TEXT["unset"]), lesson="1.6",
                who=TEXT["identity_who"])

    def check_signing(self):
        try:
            sign = self.config("commit.gpgsign", kind="bool")
        except ValueError:
            self.add("git.signing", INFO, TEXT["signing_unreadable"])
            return
        if sign != "true":
            self.add("git.signing", OK, TEXT["signing_off"])
            return
        fmt = (self.config("gpg.format") or "openpgp").strip().lower()
        if fmt in ("openpgp", "x509"):
            default = "gpg" if fmt == "openpgp" else "gpgsm"
            configured = self.config(f"gpg.{fmt}.program")
            if configured is None and fmt == "openpgp":
                configured = self.config("gpg.program")
            if configured is not None and not configured.strip():
                key = f"gpg.{fmt}.program" if self.config(f"gpg.{fmt}.program") is not None \
                    else "gpg.program"
                self.add("git.signing", TODO, TEXT["signing_empty_program"].format(
                    format=fmt, key=key), lesson=GPG_SIGNING_LESSON)
                return
            program = (configured or default).strip()
            if self.which(program):
                self.add("git.signing", OK, TEXT["signing_ok"].format(format=fmt, program=program))
            else:
                self.add("git.signing", TODO, TEXT["signing_no_program"].format(
                    format=fmt, program=program), lesson=GPG_SIGNING_LESSON)
            return
        if fmt != "ssh":
            self.add("git.signing", INFO, TEXT["signing_unknown_format"].format(format=fmt))
            return
        configured = self.config("gpg.ssh.program")
        if configured is not None and not configured.strip():
            # A ~/.gitconfig can carry this key with an empty value (plan
            # G7): Git then tries to run a program without a name and every
            # ssh-signed commit fails with "error: cannot run : No such file or
            # directory" (verified with Git 2.54 in a simulation home).
            self.add("git.signing", TODO, TEXT["signing_empty_program"].format(
                format=fmt, key="gpg.ssh.program"), lesson=SSH_SIGNING_LESSON)
            return
        # Everything about SSH signing is lesson 1.11 (choosing it, its key,
        # its program); the gpg failure of an openpgp setup is lesson 1.6.
        program = (configured or "ssh-keygen").strip()
        if not self.which(program):
            self.add("git.signing", TODO, TEXT["signing_no_program"].format(
                format=fmt, program=program), lesson=SSH_SIGNING_LESSON)
            return
        key = (self.config("user.signingkey") or "").strip()
        if not key:
            if (self.config("gpg.ssh.defaultKeyCommand") or "").strip():
                self.add("git.signing", OK, TEXT["signing_ssh_ok"])
            else:
                self.add("git.signing", TODO, TEXT["signing_ssh_no_key"],
                         lesson=SSH_SIGNING_LESSON)
            return
        if key.startswith(("key::", "ssh-", "ecdsa-")):
            self.add("git.signing", OK, TEXT["signing_ssh_ok"])
            return
        path = self.app.expand(key)
        if path.is_file():
            self.add("git.signing", OK, TEXT["signing_ssh_ok"])
        else:
            self.add("git.signing", TODO, TEXT["signing_ssh_missing_key"].format(
                path=self.show(path)), lesson=SSH_SIGNING_LESSON)

    def check_editor(self):
        result = self.git("var", "GIT_EDITOR")
        editor = result.out.strip() if result.code == 0 else ""
        if not editor and self.env.get("TERM", "dumb") in ("", "dumb"):
            # Without a real terminal Git refuses to name its default editor
            # ("Terminal is dumb, but EDITOR unset"); ask as from a terminal.
            env = dict(self.env)
            env["TERM"] = "xterm-256color"
            again = gitread.GitReader(env, timeout=RUN_TIMEOUT).run("/", "var", "GIT_EDITOR")
            editor = again.out.strip() if again.code == 0 else ""
        if not editor:
            self.add("git.editor", INFO, TEXT["editor_unknown"])
            return
        words = editor.split()
        name = os.path.basename(words[0]) if words else ""
        if name in VI_NAMES:
            self.add("git.editor", INFO, TEXT["editor_vi"].format(editor=editor))
        elif name in NOT_EDITORS:
            self.add("git.editor", INFO, TEXT["editor_none"].format(editor=editor))
        else:
            self.add("git.editor", OK, TEXT["editor_ok"].format(editor=editor))

    def check_branch(self):
        result = self.git("var", "GIT_DEFAULT_BRANCH")
        branch = result.out.strip() if result.code == 0 else ""
        if not branch:
            # Git older than 2.41 has no GIT_DEFAULT_BRANCH; its default is master.
            try:
                branch = (self.config("init.defaultBranch") or "master").strip()
            except ValueError:
                branch = ""
        if not branch:
            self.add("git.branch", INFO, TEXT["branch_unknown"])
        elif branch == "main":
            self.add("git.branch", OK, TEXT["branch_ok"])
        else:
            self.add("git.branch", INFO, TEXT["branch_other"].format(branch=branch))

    def check_excludes(self):
        try:
            configured = self.config("core.excludesfile", kind="path")
        except ValueError:
            configured = self.config("core.excludesfile")
        if configured:
            path = self.app.expand(configured)
            if path.is_file():
                self.add("git.excludes", OK, TEXT["excludes_ok"].format(path=self.show(path)))
            else:
                self.add("git.excludes", INFO, TEXT["excludes_missing"].format(path=self.show(path)))
            return
        xdg = self.env.get("XDG_CONFIG_HOME", "").strip()
        base = Path(xdg) if xdg else self.app.home / ".config"
        default = base / "git" / "ignore"
        if default.is_file():
            self.add("git.excludes", OK, TEXT["excludes_default_ok"].format(path=self.show(default)))
        else:
            self.add("git.excludes", INFO, TEXT["excludes_none"])

    # -- where things live --------------------------------------------------
    def check_workspace(self):
        root = Path(os.path.realpath(str(self.app.root)))
        # The real place, never through ~/Developer/fullstack-from-zero: this line
        # says where the folder is.  The entrance is named in its own words.
        shown = self.scrub(self.app.show(root, entrance=False))
        mobile = Path(os.path.realpath(str(self.app.home / "Library" / "Mobile Documents")))
        if root == mobile or mobile in root.parents:
            self.synced(TEXT["ws_mobile"].format(path=shown))
            return
        program = XATTR
        if not (os.path.isfile(program) and os.access(program, os.X_OK)):
            self.add("workspace", INFO, TEXT["ws_unknown"].format(
                path=shown, reason=TEXT["why_no_xattr"].format(program=program)))
            return
        trouble = ""
        for folder in [root] + list(root.parents):
            try:
                code, out, _ = self.run([program, str(folder)], timeout=XATTR_TIMEOUT)
            except RunFailed as exc:
                if str(exc) == "timeout":
                    trouble = TEXT["why_timeout"].format(program=program, seconds=XATTR_TIMEOUT)
                else:
                    trouble = TEXT["why_xattr_failed"].format(program=program,
                                                              folder=self.show(folder))
                continue
            if code != 0:
                trouble = trouble or TEXT["why_xattr_failed"].format(
                    program=program, folder=self.show(folder))
                continue
            names = [line.strip() for line in out.splitlines()]
            if ICLOUD_ATTRIBUTE in names:
                self.synced(TEXT["ws_synced"].format(
                    path=shown, ancestor=self.show(folder),
                    provider=self.provider(program, folder)))
                return
        if trouble:
            text, group = TEXT["ws_unknown"].format(path=shown, reason=trouble), INFO
        else:
            text, group = TEXT["ws_ok"].format(path=shown), OK
        if self.entrance_needed():
            # Not synced (or not known), but the learner's cd ~/Developer/fullstack-from-zero
            # does not lead here: the same sentence as in the synced case.
            kind = self.app.entrance_kind()
            decided = TEXT["ws_decided"] if self.decision("workspace_location") == "stay-in-sync" else ""
            self.add("workspace", TODO, text + decided
                     + TEXT["ws_no_entrance_plain" if kind == "missing" else "ws_bad_entrance_plain"],
                     lesson="0.2", who=TEXT["ws_entrance_who"])
            return
        self.add("workspace", group, text + self.entrance_note(synced=False))

    def entrance_needed(self):
        """Does ``cd ~/Developer/fullstack-from-zero`` fail although lesson 0.2 is behind the learner?

        True when nothing or a broken link is at ``~/Developer/fullstack-from-zero``
        and the learner has made the decision of lesson 0.2c (or passed 0.2).
        Before lesson 0.2 no lesson writes that path.
        """
        if self.app.entrance_kind() not in ("missing", "broken"):
            return False
        return self.decision("workspace_location") is not None or self.lesson_done("0.2")

    def entrance_note(self, synced):
        """A sentence on ``~/Developer/fullstack-from-zero`` when it is the entrance, else "".

        The entrance is a symbolic link that leads to the workspace (COMMON
        section 6); a learner who moved the course has the folder itself
        there and needs no sentence.
        """
        if self.app.entrance_kind() != "link":
            return ""
        return TEXT["ws_entrance_synced" if synced else "ws_entrance"]

    def synced(self, text):
        """The todo line for a workspace in a synced folder.

        Lesson 0.2c records the learner's choice to keep it there
        (``decisions.workspace_location == "stay-in-sync"``).  Then the line
        says so, and what it says next depends on ``~/Developer/fullstack-from-zero``:

        - the entrance (a link to the workspace): it is named, the folder
          itself is still in the synced place, lesson 1.12 asks again;
        - nothing there, or a link that leads nowhere or elsewhere: the
          sentence to say to the tutor to get the entrance;
        - a real folder that is not the workspace (a half-finished move) or
          the workspace itself: no word about the entrance.

        It stays a todo line: check 0.2c asks which group this line is in.
        """
        kind = self.app.entrance_kind()
        if self.decision("workspace_location") != "stay-in-sync":
            self.add("workspace", TODO, text + self.entrance_note(synced=True), lesson="0.2")
            return
        asked_again = self.lesson_done("1.12")
        if kind in ("missing", "broken"):
            name = "ws_no_entrance" if kind == "missing" else "ws_bad_entrance"
            self.add("workspace", TODO, text + TEXT["ws_decided"]
                     + TEXT[name + ("_plain" if asked_again else "")],
                     lesson="0.2", who=TEXT["ws_entrance_who"])
            return
        self.add("workspace", TODO, text + self.entrance_note(synced=True) + TEXT["ws_decided"],
                 lesson="1.12",
                 who=TEXT["ws_decided_who_after" if asked_again else "ws_decided_who"])

    # -- the learner's state, read only ---------------------------------------
    def learner_state(self):
        """``learner/state.json`` as a dict, read without the store; {} when unreadable.

        The doctor never loads the state through ``app.store`` (it must work
        when the file is damaged) and never writes it.
        """
        if getattr(self, "_state", None) is None:
            self._state = {}
            try:
                with open(self.app.store.state_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                if isinstance(data, dict):
                    self._state = data
            except (OSError, ValueError, AttributeError):
                pass
        return self._state

    def decision(self, key):
        decisions = self.learner_state().get("decisions")
        return decisions.get(key) if isinstance(decisions, dict) else None

    def passed(self, station_id):
        stations = self.learner_state().get("stations")
        record = stations.get(station_id) if isinstance(stations, dict) else None
        return isinstance(record, dict) and bool(record.get("first_pass"))

    def reached_workspace_repo_lesson(self):
        """The learner has reached lesson 1.12, whose station 1 runs git init here.

        Reached: station 1.12a passed, or every station of lesson 1.11 passed,
        or any station of a lesson after 1.11 passed.  When the stations of
        1.11 cannot be told (no syllabus row), only 1.12a counts, as before.
        """
        if self.passed("1.12a"):
            return True
        before = syllabus.lesson_entry(WORKSPACE_REPO_BEFORE)
        if not before or not before.get("stations"):
            return False
        if all(self.passed(station) for station in before["stations"]):
            return True
        stations = self.learner_state().get("stations")
        if not isinstance(stations, dict):
            return False
        limit = syllabus.lesson_key(WORKSPACE_REPO_BEFORE)
        for station_id in stations:
            match = re.fullmatch(r"(\d+)\.(\d+)[a-z]", str(station_id))
            if (match and (int(match.group(1)), int(match.group(2))) > limit
                    and self.passed(station_id)):
                return True
        return False

    def check_workspace_git(self):
        """A ``.git`` in the workspace root before the learner reached lesson 1.12.

        Lesson 1.12 station 1 starts with doctor and then runs git init in
        the workspace; a learner who starts that station again must not get
        a false alarm, so the line stops once lesson 1.11 is done.
        """
        root = Path(os.path.realpath(str(self.app.root)))
        if not os.path.lexists(str(root / ".git")) or self.reached_workspace_repo_lesson():
            return
        self.add("workspace.git", TODO, TEXT["ws_git"], who=TEXT["ws_git_who"])

    def check_starter(self):
        """starter/ files that differ from the manifest (plan G11a); silent when equal."""
        differences = scenarios.starter_differences(self.app.root)
        if not differences:
            return
        names = [TEXT["starter_one_" + kind].format(path=path) for path, kind in differences[:3]]
        files = "、".join(names)
        if len(differences) > 3:
            files += TEXT["starter_more"].format(n=len(differences))
        self.add("starter", INFO, TEXT["starter_changed"].format(files=files))

    def provider(self, program, folder):
        """" iCloud " when the attribute names Apple's iCloud Drive, else "云盘"."""
        try:
            code, out, _ = self.run([program, "-p", ICLOUD_ATTRIBUTE, str(folder)],
                                    timeout=XATTR_TIMEOUT)
        except RunFailed:
            return TEXT["provider_other"]
        if code == 0 and "CloudDocs" in out:
            return TEXT["provider_icloud"]
        return TEXT["provider_other"]

    def check_developer(self):
        folder = self.app.home / "Developer"
        if folder.is_dir():
            self.add("developer", OK, TEXT["dev_ok"])
        elif folder.exists():
            self.add("developer", INFO, TEXT["dev_not_folder"])
        else:
            self.add("developer", INFO, TEXT["dev_missing"])

    def check_code(self):
        program = self.which("code")
        if program:
            self.add("code", OK, TEXT["code_ok"].format(path=self.show(program)))
        else:
            self.add("code", TODO, TEXT["code_missing"], lesson="0.1", who=TEXT["code_who"])

    def lesson_done(self, lesson_id):
        """Every station of ``lesson_id`` (from the syllabus) has passed."""
        entry = syllabus.lesson_entry(lesson_id)
        return bool(entry and entry["stations"]) and all(
            self.passed(station) for station in entry["stations"])

    def check_gh(self):
        """gh, which lesson 1.11 installs: the same lesson ``fresh`` names.

        Before that lesson is done a missing gh is only a notice; afterwards
        the later lessons need it, so a missing gh is a todo line.
        """
        lesson = read_baseline_entry("gh").get("installed_in") or GH_LESSON
        program = self.which("gh")
        if not program:
            if self.lesson_done(lesson):
                self.add("gh", TODO, TEXT["gh_missing_late"].format(lesson=lesson),
                         who=TEXT["tutor"])
            else:
                self.add("gh", INFO, TEXT["gh_missing"].format(lesson=lesson))
            return
        version = ""
        try:
            code, out, _ = self.run([program, "--version"])
            if code == 0:
                match = re.search(r"gh version (\d+(?:\.\d+)+)", out)
                version = match.group(1) if match else ""
        except RunFailed:
            version = ""
        version = version or TEXT["version_unknown"]
        if self.lesson_done(lesson):
            self.add("gh", OK, TEXT["gh_ok"].format(version=version))
        else:
            self.add("gh", INFO, TEXT["gh_present"].format(version=version, lesson=lesson))

    def check_net(self):
        if not self.net:
            self.add("net", INFO, TEXT["net_skipped"])
            return
        reason = probe_url(NET_URL, NET_TIMEOUT)
        if reason is None:
            self.add("net", OK, TEXT["net_ok"].format(seconds=NET_TIMEOUT))
        else:
            self.add("net", INFO, TEXT["net_failed"].format(seconds=NET_TIMEOUT, reason=reason))


# ---------------------------------------------------------------------------
# The network probe (only with --net)
# ---------------------------------------------------------------------------
def open_url(request, timeout):
    """``urllib.request.urlopen``; a test replaces this attribute."""
    return urllib.request.urlopen(request, timeout=timeout)


def probe_url(url, timeout):
    """None when the server answered at all; otherwise a short Chinese reason.

    A HEAD request: nothing is sent but the request line and standard
    headers.  Any HTTP answer, even an error status, proves the server can be
    reached.
    """
    request = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "course-doctor"})
    try:
        response = open_url(request, timeout)
        _close(response)
        return None
    except urllib.error.HTTPError as answer:
        _close(answer)
        return None
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        if isinstance(reason, OSError) and "timed out" in str(reason):
            return TEXT["net_timeout"]
        return TEXT["net_error"] + "：" + first_line(str(reason or exc), 60)
    except OSError as exc:
        if "timed out" in str(exc):
            return TEXT["net_timeout"]
        return TEXT["net_error"] + "：" + type(exc).__name__
    except Exception as exc:  # noqa: BLE001 - --net must report, never crash
        return TEXT["net_error"] + "：" + type(exc).__name__


def _close(response):
    close = getattr(response, "close", None)
    if callable(close):
        try:
            close()
        except Exception:  # noqa: BLE001, S110 - closing is a courtesy; the answer is known
            pass
