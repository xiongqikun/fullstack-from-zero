"""Git for scenario builders: the only place where the tool changes a repository.

Everything built here lives in a folder the tool itself created.  Three things
make the result the same on every machine:

1. The learner's global and system Git configuration is switched off for the
   builder (``GIT_CONFIG_GLOBAL`` and ``GIT_CONFIG_SYSTEM`` point at the null
   device), so a global ignore file, a hook path or a commit template cannot
   change what gets built.
2. Signing is switched off and a fixed identity is used for the tool's own
   commits (``-c commit.gpgsign=false -c user.name=练习场
   -c user.email=playground@example.invalid``).  On a machine with the common bad case of plan G7 a
   plain ``git commit`` fails until lesson 1.6 has dealt with signing; the
   tool must never depend on that.
3. Only the ``file`` transport is allowed (``GIT_ALLOW_PROTOCOL=file``): a
   builder can push to a local bare repository but can never reach the network.
4. ``git_commit`` commits only in a repository whose top folder is exactly the
   folder it was given.  A folder that was never ``git init``-ed inside some
   other repository (a stray ``git init`` in ``~/Developer``) is refused
   instead of committing that other repository's files.  Scenario builders
   also get ``GIT_CEILING_DIRECTORIES`` set to their scenario folder.

Nothing here writes to any configuration outside the repository being built.
"""

import datetime
import os
import shutil
import subprocess

from .errors import ToolTrouble
from .gitread import DROP_ENV, RunResult

IDENTITY_NAME = "练习场"
IDENTITY_EMAIL = "playground@example.invalid"
DEFAULT_BRANCH = "main"
TIMEOUT = 30.0

TEXT = {
    "no_git": "这台电脑上找不到 git 命令，搭不了练习场。",
    "failed": "搭建练习场时一条 git 命令失败了。",
    "timeout": "搭建练习场时一条 git 命令超过 {seconds} 秒没有结束。",
    "not_top": "搭建练习场的代码想在一个还不是 Git 仓库的文件夹里提交：{path}",
}

_DROP = DROP_ENV + (
    "GIT_TEMPLATE_DIR", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE",
    "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_DATE",
    "GIT_CONFIG", "GIT_CONFIG_COUNT", "GIT_EXTERNAL_DIFF", "GIT_SSH", "GIT_SSH_COMMAND",
)


def overrides(author=None):
    """The ``-c`` options every builder command gets."""
    name, email = author if author else (IDENTITY_NAME, IDENTITY_EMAIL)
    return [
        "-c", "commit.gpgsign=false",
        "-c", "tag.gpgsign=false",
        "-c", f"user.name={name}",
        "-c", f"user.email={email}",
        "-c", f"init.defaultBranch={DEFAULT_BRANCH}",
        "-c", "core.quotePath=false",
        "-c", "core.autocrlf=false",
        "-c", "advice.detachedHead=false",
    ]


def builder_env(env, date=None):
    """The environment for builder commands (see the module docstring)."""
    child = dict(env)
    for name in _DROP:
        child.pop(name, None)
    child.update({
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ALLOW_PROTOCOL": "file",
        "GIT_EDITOR": "true",
        "GIT_PAGER": "cat",
        "PAGER": "cat",
        "LC_ALL": "C",
    })
    if date is not None:
        text = format_date(date)
        child["GIT_AUTHOR_DATE"] = text
        child["GIT_COMMITTER_DATE"] = text
    return child


def format_date(date):
    """A commit date for Git: a datetime or an ISO string, to the second."""
    if isinstance(date, datetime.datetime):
        return date.replace(microsecond=0).isoformat()
    if isinstance(date, datetime.date):
        return date.isoformat() + "T12:00:00"
    return str(date)


def run_git(cwd, args, env, date=None, author=None, check=True, timeout=TIMEOUT):
    """Run ``git <args>`` in ``cwd`` as a builder and return a ``RunResult``.

    With ``check`` (the default) a failing command raises ``ToolTrouble``.
    """
    program = shutil.which("git", path=env.get("PATH"))
    if not program:
        raise ToolTrouble(TEXT["no_git"])
    command = [program] + overrides(author) + [str(arg) for arg in args]
    shown = "git " + " ".join(str(arg) for arg in args)
    try:
        done = subprocess.run(
            command, cwd=str(cwd), env=builder_env(env, date), stdin=subprocess.DEVNULL,
            capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise ToolTrouble(TEXT["timeout"].format(seconds=int(timeout)), detail=shown)
    except OSError as exc:
        raise ToolTrouble(TEXT["failed"], detail=f"{shown}\n{exc!r}")
    result = RunResult(done.returncode, done.stdout.decode("utf-8", "replace"),
                       done.stderr.decode("utf-8", "replace"))
    if check and result.code != 0:
        raise ToolTrouble(TEXT["failed"],
                          detail=f"{shown}\nexit {result.code}\n{result.err.strip()}")
    return result


def git_init(path, env, branch=DEFAULT_BRANCH, bare=False):
    """Create a repository at ``path`` (the folder is created when missing)."""
    os.makedirs(str(path), exist_ok=True)
    args = ["init", "--quiet", f"--initial-branch={branch}"]
    if bare:
        args.append("--bare")
    run_git(path, args, env)
    return path


def git_commit(path, message, env, add="all", date=None, author=None,
               allow_empty=False, force=False):
    """Stage and commit in the repository at ``path``; return the new full hash.

    ``add`` is "all" (stage every change, like ``git add -A``), a list of
    paths relative to the repository, or None (commit what is already staged).
    ``force`` adds listed paths even when an ignore rule matches them.
    """
    # Look before touching anything: staging in a folder that is not itself a
    # repository would stage files of whatever repository lies around it.
    top = run_git(path, ["rev-parse", "--show-toplevel"], env, check=False)
    if top.code != 0 or not _same_folder(top.out.strip(), path):
        raise ToolTrouble(TEXT["not_top"].format(path=path),
                          detail="rev-parse --show-toplevel: " + (top.out.strip() or top.err.strip()))
    if add == "all":
        run_git(path, ["add", "-A"], env)
    elif add:
        paths = [add] if isinstance(add, str) else list(add)
        run_git(path, ["add"] + (["-f"] if force else []) + ["--"] + [str(p) for p in paths], env)
    args = ["commit", "--quiet", "--no-verify", "-m", message]
    if allow_empty:
        args.append("--allow-empty")
    run_git(path, args, env, date=date, author=author)
    return run_git(path, ["rev-parse", "HEAD"], env).out.strip()


def _same_folder(a, b):
    if not a:
        return False
    try:
        return os.path.samefile(str(a), str(b))
    except OSError:
        return False
