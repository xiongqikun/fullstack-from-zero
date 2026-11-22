# Research brief: Git fundamentals and the conventions built on top of it (key: git-norms)

Date of all checks: 2026-11-19. Machine: macOS 27.2 arm64, zsh, `git version 2.54.0 (Apple Git-157)` at `/usr/bin/git` (Xcode toolchain).
Audience of this file: lesson builders (raw material, not learner-facing).

Tags: **[local]** = I ran it here today in a throwaway repo under this scratch dir (repo-local identity; the real global git config was never written — `--global` commands were only run with `GIT_CONFIG_GLOBAL` pointing at a scratch file, and `~/.gitconfig` was checksummed before/after). **[source: URL]** = read in a primary source today. **[memory]** = not verified today.
Spec rules below are precise paraphrases, not verbatim text (rule numbers match the originals; read the URL for exact wording). Conventional Commits and SemVer are CC BY 3.0, Keep a Changelog is MIT, Pro Git zh is CC BY-NC-SA 3.0 (link to it, do not copy text into a commercial product), github/gitignore is CC0.

---

## 1. Top findings (read these first)

1. **Possible BLOCKER: every `git commit` fails when signing is configured without GPG.** That happens when the global config contains `commit.gpgsign=true`, `gpg.format=openpgp`, `gpg.program=gpg`, an empty `user.signingkey`, and no `gpg` binary exists (check PATH, /opt/homebrew/bin, /usr/local/bin, /usr/local/MacGPG2/bin). [local]
   ```
   $ git commit -m "test: first commit"
   error: cannot run gpg: No such file or directory
   error: gpg failed to sign the data:
   (no gpg output)
   fatal: failed to write commit object            (exit 128)
   ```
   Merge commits (`git merge --no-ff`) fail the same way; `git stash` and `git tag -a` still work. [local] One-off bypass: `git commit --no-gpg-sign ...` or `git -c commit.gpgsign=false commit ...`; per-repo fix: `git config --local commit.gpgsign false`; permanent fix (learner's decision, lesson 0): `git config --global commit.gpgsign false`. [local, all three verified] Such a key set may be left behind by a Git GUI client — this origin is a guess, not verified. [memory]
2. **Project folders on an iCloud-synced Desktop are at risk** (with Desktop & Documents sync on, `~/Desktop` is backed by `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop`). [local] A `.git` directory inside a synced folder is a known hazard (user reports of " 2" duplicates inside `.git`, `.icloud` placeholders; no Apple statement). [source: https://discussions.apple.com/thread/253527805 (a 2022 user post; the page announces that this forum closes permanently on 2026-11-20, so the link may die) ; web-search snippets of a Stack Overflow question on iCloud Desktop sync vs git, not opened] I simulated conflict copies in `.git` and git then prints `warning: ignoring ref with broken name refs/heads/main 2` / `fatal: bad object refs/heads/main 2`; deleting the `* 2` files repairs it (`find .git -name '* 2'`). [local, simulated] Options, see §9.6.
3. **Apple Git already ships two of the "recommended" settings**: `/Applications/Xcode.app/Contents/Developer/usr/share/git-core/gitconfig` sets `init.defaultBranch=main` and `credential.helper=osxkeychain` (shown with scope `unknown` in `git config --list --show-scope`). So here `git init` creates `main` silently. [local] `git init`/`git clone` also write `core.ignorecase=true` and `core.precomposeunicode=true` into each repo's `.git/config` on macOS. [local]
4. **Only `core.quotepath false` is essential for Chinese**: without it Chinese file names print as `"\345\233\236..."`. Chinese commit messages and even Chinese branch/dir names work out of the box. [local]
5. **Apple Git is not localised**: `LANG=zh_CN.UTF-8 git status` still prints English (no `share/locale` in the toolchain). The course needs a Chinese "message decoder" (§12). [local]
6. **Modern command set is what Git itself now teaches**: `git status` hints say `git restore <file>` / `git restore --staged <file>`; `git switch`/`git restore` were declared no longer experimental in Git 2.51. [local][source: https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.51.0.adoc] But the official Chinese Pro Git (git-scm.com/book/zh/v2, ch. 2.4) still teaches `git reset HEAD <file>` / `git checkout -- <file>`, never mentions `git restore`, and uses `master` throughout. [source: https://git-scm.com/book/zh/v2 + repo progit/progit2-zh, grepped today]
7. **Three verified traps that older advice gets wrong** (§10): (a) `git pull --rebase` after someone force-pushed silently drops your commits that had already been pushed; (b) `--force-with-lease` alone is defeated by a prior `git fetch` — pair it with `--force-if-includes`; (c) the hint printed for an embedded repo (`git rm --cached <dir>`) fails in 2.54 — use `git restore --staged <dir>` or `git rm --cached -f <dir>`. [local]
8. **Standards status today**: Conventional Commits 1.0.0 and SemVer 2.0.0 are current. Keep a Changelog: 1.1.0 is still what keepachangelog.com redirects to, latest git tag is v1.1.2, but a **2.0.0 revision dated 2026-06-07 is published at /en/2.0.0/** (the site's redirect script calls it PREVIEW; its text still differs between the deployed page and the repo). Format is unchanged; it adds guidance on `**Breaking:**` markers and on LLM-drafted changelogs (brief in `AGENTS.md`/`CLAUDE.md`). [source, details in §8.5]
9. **A real Chinese open-source financial-data project documents exactly the "English type + Chinese subject" style**: AKShare's contributing guide requires Conventional Commits and says a Chinese description may follow the type, e.g. `fix(index): 修复 index_all_cni 接口`; it also uses `uv sync` + `uv run pre-commit install`. [source: https://raw.githubusercontent.com/akfamily/akshare/main/docs/contributing.md]
10. **Version landscape**: upstream Git latest tag is v2.56.1 (this Mac: 2.54.0); Git 3.0 has no release date; planned 3.0 defaults: branch `main`, SHA-256, reftable. [source: `git ls-remote --tags https://github.com/git/git`; https://raw.githubusercontent.com/git/git/master/Documentation/BreakingChanges.adoc]

---

## 2. What `git init` does today

Apple Git 2.54 as configured on this Mac [local]:
```
$ git init
Initialized empty Git repository in <dir>/.git/
$ git status
On branch main
No commits yet
nothing to commit (create/copy files and use "git add" to track)
$ cat .git/config          # written by init: bare=false, logallrefupdates=true, ignorecase=true, precomposeunicode=true
```
Vanilla behaviour (same binary with `GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null`) — what the learner will see on Linux/CI/older tutorials [local]:
```
hint: Using 'master' as the name for the initial branch. This default branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
Initialized empty Git repository in <dir>/.git/          (branch: master)
```
- `uv init <name>` (uv 0.13.5) runs `git init` itself and writes `.gitignore` (`__pycache__/`, `*.py[oc]`, `build/`, `dist/`, `wheels/`, `*.egg-info`, `.venv`), `.python-version`, `README.md`, `pyproject.toml`, `src/`. Inside an existing repo it creates no nested `.git` and no `.gitignore`. `--vcs none` disables it. [local]
- Before `git init`, check you are not already inside a repo: `git rev-parse --show-toplevel` (prints the repo root, or `fatal: not a git repository (or any of the parent directories): .git`). One repo per project folder, never the parent that holds several projects. [local, §10 D10]

## 3. One-time global configuration (beginner, macOS, writes Chinese)

Check the current state first (`git config list --global --show-origin`): whether `user.name`/`user.email` are set, whether signing keys as in §1 are present, whether a `core.excludesfile` is set. [local]

Recommended commands — all accepted by git 2.54 against a scratch global file, then a full init -> commit -> bare remote -> push -> clone -> pull -> new-branch-push flow passed using only this config, with Chinese dir/file/branch names [local]:
```
git config --global commit.gpgsign false          # lesson 0, only if §1 applies; learner decides
git config --global core.quotepath false
git config --global init.defaultBranch main       # redundant on Apple Git, makes other machines behave the same
git config --global core.editor "code --wait"     # VS Code is installed; `code -w/--wait` confirmed in `code --help`
git config --global core.autocrlf input
git config --global pull.ff only
git config --global push.autoSetupRemote true
git config --global merge.conflictStyle zdiff3
```
Not needed: `credential.helper` (Apple default osxkeychain), `core.precomposeunicode` (auto-written per repo), `user.*` (if already set). Optional: `fetch.prune true`, `help.autoCorrect prompt`, aliases such as `alias.lg "log --oneline --graph --decorate --all"` (accepted and run [local]).

| Key = value | What it does | Without it (demonstrated) |
|---|---|---|
| `core.quotepath false` | Stop escaping bytes > 0x80 in paths | `?? "\345\233\236\346\265\213\347\254\224\350\256\260.md"` in status / log --stat / ls-files; with it `回测笔记.md` [local] |
| `init.defaultBranch main` | Name of the first branch | vanilla git: `master` + the hint above [local] |
| `core.editor "code --wait"` | Editor for `git commit` without `-m`, merges, `--amend`, `rebase -i` | default is `vi` (`git var GIT_EDITOR`); an editor that returns at once (GUI editor without `--wait`) gives `Aborting commit due to empty commit message.` Precedence: `GIT_EDITOR` > `core.editor` > `VISUAL` > `EDITOR` > `vi` [local] |
| `core.autocrlf input` | Convert CRLF to LF when adding; never convert on checkout | CRLF stored as-is (`git ls-files --eol` shows `i/crlf`); with it `i/lf` plus `warning: in the working copy of 'win2.csv', CRLF will be replaced by LF the next time Git touches it` [local]. GitHub recommends this value for macOS [source: https://docs.github.com/en/get-started/git-basics/configuring-git-to-handle-line-endings] |
| `pull.ff only` | `git pull` only fast-forwards | On diverged history plain `git pull` stops with a 12-line hint (it lists `git config pull.rebase false`, `pull.rebase true`, `pull.ff only`) and `fatal: Need to specify how to reconcile divergent branches.`; with `ff only`: `fatal: Not possible to fast-forward, aborting.` and nothing changes [local] |
| `push.autoSetupRemote true` | First `git push` of a new branch sets its upstream | `fatal: The current branch main has no upstream branch.` -> must type `git push -u origin main` for every new branch [local] |
| `merge.conflictStyle zdiff3` | Conflict blocks also show the common ancestor (`\|\|\|\|\|\|\| <base>`) | only the two sides are shown (§5) [local]; added in Git 2.35 [source: RelNotes/2.35.0] |
| `credential.helper osxkeychain` | Stores HTTPS credentials in the macOS Keychain | not demonstrable without an account; GitHub removed password auth for Git over HTTPS and recommends `gh auth login` or Git Credential Manager [source: https://docs.github.com/en/get-started/git-basics/about-remote-repositories ; .../caching-your-github-credentials-in-git] |
| `core.precomposeunicode true` | Stores decomposed (NFD) macOS file names as NFC | with `false`, a committed `café.txt` created with an NFD name shows up again as untracked. Irrelevant for Chinese: NFC == NFD for CJK ideographs [local] |

Why `pull.ff only` rather than `pull.rebase true` for beginners [local, t43/t22]: after amending an already-pushed commit, Git's own hint says "use 'git pull'"; a merge pull then keeps both the old and the new copy plus a merge commit; `pull --rebase` silently keeps the OLD message (amend lost, `advice.skippedCherryPicks`); `pull.ff only` simply refuses. The local manual entry for `pull.rebase` itself carries a NOTE warning that it can be dangerous unless you understand the implications. Teach `git pull --rebase` / `--no-rebase` later as explicit per-call choices.

Editor facts [local]: `/usr/bin/nano` is a symlink to `pico` (save Ctrl+O, exit Ctrl+X); `vim` exists (escape hatch: `Esc` `:wq` Enter to save, `Esc` `:q!` Enter to abort); no `git gui`/`gitk` in Apple Git. Beginners can avoid the editor entirely: `git commit -m "subject" -m "body paragraph" -m "Refs: #12"` (each `-m` becomes a paragraph) or `git commit -F file`. New-style config subcommands (`git config set/get/unset/list`, Git 2.46+) and the old flags (`--get`, `--list`) both work. [local][source: RelNotes/2.46.0]

## 4. The modern command set — verified cheat sheet

All commands below were run successfully today [local]. Legacy spellings the learner will meet in old tutorials are in the last column.

| Goal | Command | Notes / legacy |
|---|---|---|
| Where am I? | `git status`, `git status -sb` | short codes: `??` untracked, ` M` modified, `M ` staged, `A ` added, `D ` deleted, `UU` conflict, `!!` ignored (`--ignored`) |
| Stage | `git add <file>`, `git add -p` | `-p` prompt: `(1/2) Stage this hunk [y,n,q,a,d,k,K,j,J,g,/,e,p,P,?]?`. `git add .` only covers the current dir downward; `-u` = tracked files only; `-A` = everything |
| Commit | `git commit -m "..."` | `git commit -a` = `add -u` + commit: new files are NOT included |
| Fix last commit | `git commit --amend -m "..."` / `--amend --no-edit` | only before pushing |
| See changes | `git diff` (unstaged), `git diff --staged` (staged), `git diff A B --stat`, `--name-only` | after `git add`, plain `git diff` is empty — a classic confusion; `--cached` = `--staged` |
| History | `git log --oneline --graph --decorate [--all]`, `git log --stat -1`, `git log -- <path>`, `git log --grep=...`, `git show <commit>`, `git show <commit>:<path>` | long output opens the `less` pager: press `q` |
| Unstage | `git restore --staged <file>` | legacy `git reset HEAD <file>`. Before the very first commit it fails with `fatal: could not resolve 'HEAD'` — use `git rm --cached <file>` (that is what status suggests then) |
| Discard edits | `git restore <file>` | legacy `git checkout -- <file>`; NOT recoverable |
| Old version of one file | `git restore --source=<commit> <file>` | |
| Branches | `git switch -c feature/x`, `git switch main`, `git switch -`, `git branch -vv`, `git branch -d x` (`-D` to force) | legacy `git checkout -b`, `git checkout main` |
| Merge | `git merge feature/x` (fast-forward if possible), `git merge --no-ff feature/x`, `git merge --squash feature/x` + commit, `git merge --abort` | |
| Rebase | `git switch feature/x && git rebase main`; `--continue` / `--abort` | rewrites commit ids |
| Shelve | `git stash push -u -m "msg"`, `git stash list`, `git stash show -p`, `git stash pop` | plain `git stash` leaves untracked files behind; `git stash save` is deprecated |
| Undo a commit safely | `git revert <commit>` (merge commit: `git revert -m 1 <merge>`) | adds a new commit |
| Move the branch back | `git reset --soft HEAD~1` (changes stay staged), `git reset HEAD~1` (= `--mixed`, changes stay unstaged), `git reset --hard HEAD~1` (changes destroyed) | history rewriting |
| Safety net | `git reflog`, then `git reset --hard <id>` / `git branch rescue <id>` / `git cherry-pick <id>`; `ORIG_HEAD` right after reset/merge/rebase | reflog entries expire: 90 days (reachable), 30 days (unreachable) by default |
| Tags | `git tag -a v0.1.0 -m "..."`, `git tag -n`, `git tag -l 'v*' --sort=version:refname`, `git describe`, `git push origin v0.1.0`, `git push --follow-tags` | plain `git push` sends no tags; `--follow-tags` sends annotated tags only; `git describe` ignores lightweight tags unless `--tags` |
| Remotes | `git remote add origin <url>`, `git remote -v`, `git remote show origin`, `git fetch`, `git pull`, `git push`, `git clone <url> [dir]`, `git branch -r` | |
| Who/when | `git blame [-L 2,3] <file>` | |
| Find the bad commit | `git bisect start <bad> <good>`, `git bisect run <cmd>`, `git bisect reset` | exit 0 = good, 1..127 except 125 = bad |
| Ignore debugging | `git check-ignore -v <path>`, `git status --ignored`, `git clean -n` (dry run) | |
| Rename/delete | `git mv old new`, `git rm <file>`, `git rm --cached <file>` (stop tracking, keep on disk) | |

Selected real outputs [local]:
```
$ git status                                   # after editing a tracked file
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   src/app/calc.py
$ git merge feature/a                          # main had not moved
Updating e889005..ca9a158
Fast-forward
$ git merge --no-ff --no-edit feature/b
Merge made by the 'ort' strategy.
$ git branch -d experiment
error: the branch 'experiment' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D experiment'
$ git reset --hard HEAD~1  ->  HEAD is now at 934803f feat: line 3
$ git reflog
934803f HEAD@{0}: reset: moving to HEAD~1
2de469c HEAD@{1}: reset: moving to HEAD~1
55678fd HEAD@{2}: commit: revert again
...
4411f4c HEAD@{4}: revert: Revert "feat: line 4"
$ git reset --hard 2de469c  ->  HEAD is now at 2de469c feat: line 4      # "lost" commit is back
$ git bisect run python3 -c "..."  ->  8269927... is the first bad commit ... bisect found first bad commit
```
The local manual's own three-line distinction (paraphrased) [local: `git help git`, "Reset, restore and revert"]: **revert** makes a new commit that undoes others; **restore** puts files back in the working tree (or index) and never moves the branch; **reset** moves the branch tip and therefore changes history.

Rebase facts [local]: rebasing `feature/x` (2 commits) onto a moved `main` prints `Successfully rebased and updated refs/heads/feature/x.` and both commits get new ids; afterwards `main` can fast-forward. After `git merge --squash`, `git branch -d` refuses the branch ("not fully merged") — `-D` is required. Golden rule, as Pro Git zh puts it (paraphrase): do not rebase commits that exist outside your own repository and that others may have built on; only tidy local, unpushed work. [source: progit2-zh book/03-git-branching/sections/rebasing.asc] `git rebase -i` todo lines now look like `pick 91f8c39 # feat: ...` and the template lists pick/reword/edit/squash/fixup/drop. [local]

## 5. A real merge conflict and its resolution [local, repo t07-conflict]

Setup: `strategy.py` has `window = 20`; branch `feature/longer-window` changes it to 60; `main` changes it to 30.
```
$ git merge feature/longer-window
Auto-merging strategy.py
CONFLICT (content): Merge conflict in strategy.py
Automatic merge failed; fix conflicts and then commit the result.        (exit 1)
$ git status
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)
Unmerged paths:
	both modified:   strategy.py
```
File with the default style, and with `merge.conflictStyle zdiff3`:
```
<<<<<<< HEAD                         <<<<<<< HEAD
    window = 30                          window = 30
=======                              ||||||| 66ad5e7
    window = 60                          window = 20
>>>>>>> feature/longer-window        =======
                                         window = 60
                                     >>>>>>> feature/longer-window
```
Resolution: edit the file to the wanted content and delete all marker lines -> `git add strategy.py` (status: "All conflicts fixed but you are still merging.") -> `git commit` (or `git merge --continue`) -> `[main 3c0bc3c] Merge branch 'feature/longer-window'`.
Whole-side shortcuts: `git checkout --ours <f>` / `git restore --theirs <f>`; rebuild the markers: `git restore --merge <f>`; give up: `git merge --abort`. Forgotten markers are caught by `git diff --cached --check` -> `strategy.py:2: leftover conflict marker` (exit 2). VS Code has a 3-way merge editor [source: https://code.visualstudio.com/docs/sourcecontrol/overview]. `git stash pop` and `git revert` can conflict in the same way (`The stash entry is kept in case you need it again.`). [local]

## 6. Practising remotes with no online account [local, repos t06/t21/t22/t27/t32/t36]

```
git init --bare origin.git                    # the "server": no working tree (HEAD, config, objects/, refs/ at top level)
cd alice && git remote add origin ../origin.git
git push -u origin main                       # "* [new branch] main -> main / branch 'main' set up to track 'origin/main'."
git clone origin.git bob                      # second working copy ("warning: You appear to have cloned an empty repository." if empty)
```
Verified exercises and their outputs:
- `git status` wording: `Your branch is ahead of 'origin/main' by 1 commit.` / `is behind ... and can be fast-forwarded.` / `Your branch and 'origin/main' have diverged, and have 1 and 1 different commits each` / `is up to date with 'origin/main'.`
- `git fetch` only moves `origin/*` (`aad6fdd..b41ff1f  main -> origin/main`); files change only on merge/pull.
- Push when the remote has new work: `! [rejected] main -> main (fetch first)`; after amending a pushed commit: `! [rejected] main -> main (non-fast-forward)`.
- Diverged pull under the three policies: `pull.ff only` refuses; `pull.rebase true` -> `Successfully rebased and updated refs/heads/main.` (linear); `pull.rebase false` -> `Merge made by the 'ort' strategy.` and a commit `Merge branch 'main' of ../origin`.
- Pull onto uncommitted edits: `error: Your local changes to the following files would be overwritten by merge: f.txt / Please commit your changes or stash them before you merge.`
- "Protected main" without GitHub: `git --git-dir=origin.git config receive.denyNonFastForwards true` and `receive.denyDeletes true` -> force push answers `remote: error: denying non-fast-forward refs/heads/main (you should pull first)`, deletion `(deletion prohibited)`.
- A bare repo keeps no reflog by default (`core.logAllRefUpdates` unset): after a force push the old commits survive only in clones.
- iCloud note: put the bare repo and practice clones outside synced folders or in a `*.nosync` folder (§9.6).

## 7. `.gitignore` and `.gitattributes`

Rules (local manual `gitignore(5)`, paraphrased) [local]: one pattern per line; `#` comment; trailing `/` = directories only; a `/` at the start or middle anchors the pattern to the `.gitignore`'s own directory, otherwise it matches at any depth; `*` does not cross `/`; `**/` any depth; `!` re-includes, but a file cannot be re-included if its parent directory is excluded; already-tracked files are never affected. Precedence: command line > `.gitignore` files (deeper wins; within a file the last match wins) > `.git/info/exclude` (personal, not shared) > `core.excludesFile` (default `~/.config/git/ignore`; some machines set `~/.gitignore_global`).

Verified cases [local, t14/t16]:
- Works: `data/raw/*` + `!data/**/.gitkeep` (`check-ignore -v` prints `.gitignore:8:!data/**/.gitkeep	data/raw/.gitkeep`). Fails: `data/` + `!data/raw/.gitkeep` (parent excluded).
- Ignoring a committed file does nothing (`.env` still ` M`); fix `git rm --cached .env` + commit — the old content stays in history (`git show HEAD~2:.env` still prints the key).
- `git clean -ndx` would delete ignored files too (`Would remove .env`) — always dry-run with `-n`.
- Empty directories are not tracked -> `.gitkeep` convention. Case-only rename with Finder/`mv` (`readme.md` -> `README.md`) is invisible to git on macOS; `git mv` records it.

github/gitignore `Python.gitignore` as fetched today (223 lines, CC0) [source: https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore]: ignores `__pycache__/`, `*.py[codz]`, `build/`, `dist/`, `*.egg-info/`, `.pytest_cache/`, `.coverage`, `htmlcov/`, `.ipynb_checkpoints`, `.env`, `.envrc`, `.venv`, `venv/`, `.mypy_cache/`, `.ruff_cache/`, `.pypirc`, `*.log`, `/site`, marimo/streamlit/pixi entries; has a `# uv` block whose comment recommends committing `uv.lock` (the ignore line is commented out); `.python-version` is likewise not ignored. Tested against a layout like a typical data project's [local]:
- It does NOT ignore `.DS_Store` (comes from `Global/macOS.gitignore`; a global ignore file may cover it), data files (`data/raw/*.csv`), or a venv dir renamed to stay out of iCloud, such as `.venv.nosync/` behind a `.venv` symlink (only the `.venv` symlink matches; `.venv.nosync/pyvenv.cfg`, `bin/activate` show as untracked).
- Its `lib/` rule also ignores a source folder named `lib/` (`.gitignore:17:lib/	lib/mycode.py`).
- Mitigation that already exists: `uv venv` writes `.venv/.gitignore` containing `*`, and ruff writes `.ruff_cache/.gitignore` with `*` — both self-ignore whatever the directory is called. [local] pytest/mypy caches do the same [memory].

Never commit: secrets (`.env`, API keys, tokens, `.pypirc`, private keys), virtualenvs, caches, OS junk, large/regenerable data, credentials inside notebooks' outputs. GitHub limits: warning above 50 MiB per file, hard block above 100 MiB, browser upload 25 MiB, repos ideally < 1 GB. [source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github]

Before the first commit of the learner's existing project (if any), dry-run `git add .` with a temporary GIT_DIR and read the list: in a typical data project much of what would be staged is generated output (figures, notebooks with embedded outputs), not source. Check generated files and notebook outputs first, and search for secret-like files and key patterns. Rules often missing: `.env`, `dist/`, `build/`, `*.egg-info/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/`. Design decision for builders: commit generated figures and notebook outputs or not (nbstripout 0.9.2 exists on PyPI [source: pypi.org JSON]).

`.gitattributes` basics [local, t05/t34]:
```
* text=auto eol=lf          # normalise text files to LF in the repo (project-level, travels with the repo)
*.png binary                # binary = -text -diff -merge; diff prints "Binary files a/fig.png and b/fig.png differ"
*.parquet binary
CHANGELOG.md merge=union    # both sides' added lines are kept, no conflict (verified with two branches)
```
Inspect with `git check-attr -a <file>` and `git ls-files --eol`; fix already-committed CRLF files with `git add --renormalize .`. [local][source: GitHub line-endings page above]

## 8. Standards

### 8.1 Conventional Commits 1.0.0 (current; site root resolves to v1.0.0; CC BY 3.0) [source: https://www.conventionalcommits.org/en/v1.0.0/ ; raw spec https://raw.githubusercontent.com/conventional-commits/conventionalcommits.org/master/content/v1.0.0/index.md ; zh: https://www.conventionalcommits.org/zh-hans/v1.0.0/]
Shape: `<type>[optional scope]: <description>` / blank line / `[optional body]` / blank line / `[optional footer(s)]`.
Rules, paraphrased with original numbering: (1) every commit MUST start with a type (a noun: `feat`, `fix`, ...), then OPTIONAL scope, OPTIONAL `!`, then a REQUIRED colon and space. (2) `feat` MUST be used when adding a feature. (3) `fix` MUST be used for a bug fix. (4) A scope MAY follow the type; it MUST be a noun for a part of the codebase in parentheses, e.g. `fix(parser):`. (5) A description MUST follow the colon-space immediately: a short summary. (6) A body MAY follow and MUST start one blank line after the description. (7) The body is free-form, any number of paragraphs. (8) Footers MAY follow one blank line after the body; each MUST be token + separator (`: ` or ` #`) + value, modelled on git trailers. (9) Footer tokens MUST use `-` for spaces (`Acked-by`), except `BREAKING CHANGE`. (10) Footer values MAY span lines; parsing stops at the next token/separator. (11) Breaking changes MUST be flagged in the prefix or in a footer. (12) As footer: uppercase `BREAKING CHANGE`, colon, space, description. (13) In the prefix: `!` right before `:`; the footer MAY then be omitted and the description SHALL describe the break. (14) Other types MAY be used. (15) Tools MUST NOT treat the units as case-sensitive, except `BREAKING CHANGE` (uppercase). (16) `BREAKING-CHANGE` is a synonym as a footer token.
SemVer link (summary + FAQ): `fix` -> PATCH, `feat` -> MINOR, any commit with a breaking change -> MAJOR; other types have no implicit version effect. The spec only defines `feat` and `fix`; the familiar list comes from `@commitlint/config-conventional` whose `type-enum` today is build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test (plus: header max 100 chars, type lower-case, subject not capitalised and no trailing `.`). [source: https://raw.githubusercontent.com/conventional-changelog/commitlint/master/@commitlint/config-conventional/src/index.ts] Current Angular list is narrower: build, ci, docs, feat, fix, perf, refactor, test. [source: https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md] FAQ points: a commit matching several types should be split; reverts are not specified (suggested: type `revert` + `Refs:` footer); with a squash-merge workflow only the maintainer needs to write conforming messages.
Official zh terms: 约定式提交; 类型 / 范围 / 描述 / 正文 / 脚注; 破坏性变更; the zh text stresses the colon is the half-width English one. Verified with a regex commit-msg hook: `feat：添加...` (full-width colon), `feat:添加` (no space) and a message without type are rejected; `feat(signal): 添加 20 日均线信号` and `fix!: ...` pass. [local, t31]

### 8.2 Commit-message craft
- Git's own manual: start with one short line (no more than 50 characters), blank line, then a fuller description; the first line is the title used throughout Git. [local: `git help commit`, DISCUSSION]
- Git project guidelines: one commit per logically separate change; subject ~50 chars soft limit, optional `area:` prefix, no full stop; imperative mood, phrased like an order given to the codebase rather than a description of what the patch or the author did; body explains the problem, why this fix, alternatives rejected. [source: https://git-scm.com/docs/SubmittingPatches]
- The widely cited seven rules (cbea.ms, 2014), paraphrased: blank line after the subject; subject about 50 characters (72 as hard cap); capitalise it; no final period; imperative mood (the subject must read naturally as the end of a sentence stating what the commit will do once applied); wrap the body at 72; the body says what and why, not how. [source: https://cbea.ms/git-commit/] Note the clash: Conventional Commits tooling wants a lower-case description after the type.
- Pro Git zh: first line under 50 characters, which it glosses as 25 汉字; then a blank line; then the detailed explanation; imperative mood; `git diff --check` before committing; each commit a logically independent change set, using `git add --patch` to split. [source: progit2-zh book/05-distributed-git/sections/contributing.asc] Measured: a 37-character mixed subject with 23 汉字 occupies 60 terminal columns. [local]
- Atomic commit (working definition for the course): one logical change that is complete on its own (builds/tests pass), can be described in one subject line without "and", and can be reverted alone. GitHub Flow docs say each commit should ideally be an isolated, complete change. [source: https://docs.github.com/en/get-started/using-github/github-flow]
- Trailers: `git commit --trailer "Co-Authored-By: Name <mail>"` appends a footer; `git log --format='%(trailers:key=Co-Authored-By,valueonly)'` reads it. [local] In this Claude Code session the assistant is instructed to end commit messages with a `Co-Authored-By: Claude ...` trailer, to commit/push only when asked, and to branch first when on the default branch. [local: this session's tool instructions]

### 8.3 How Chinese-speaking teams write commits (contributing guides fetched today)
| Project (origin) | Rule | Language of subject |
|---|---|---|
| AKShare (financial data) | Conventional Commits; hooks via `uv run pre-commit install` | Chinese allowed after the type: `fix(index): 修复 index_all_cni 接口` |
| Egg (Alibaba) `CONTRIBUTING.zh-CN.md` | Angular format `<type>(<scope>): <subject>`; types feat/fix/docs/style/refactor/perf/test/chore/deps explained in Chinese; footer for breaking changes and `Closes #1` | example in English |
| Arco Design (ByteDance) `CONTRIBUTING.zh-CN.md` | Conventional Commits, template printed with Chinese labels `<类型>[可选 范围]: <描述>` | not stated |
| TDesign (Tencent) | commitlint config-conventional + commitizen; only `fix`/`feat` feed the changelog | not stated |
| Vant (Youzan) | PR title `type(ComponentName?): message`; branch like `feature/button_color`; one PR = one problem | English examples (`fix(Button): incorrect style`); their template shows a full-width colon — a trap |
| Element (Ele.me) | `[组件名]: 描述信息`, e.g. `Button: fix xxx bug`; rebase before PR; PR to `dev` | English example |
| Apache DolphinScheduler (zh doc) | `[Type-ISSUE_ID][Scope] Subject`, imperative, subject <= 72 chars | English |
| Taro (JD) | Angular style; branches `feat/...`, `chore/...`; maintainers squash | English |
| PaddlePaddle (Baidu) | few commits per PR (squash with `git rebase -i HEAD~3`); no `git push -f` after review starts | - |
| PingCAP | `<subsystem>: <what changed>`, <= 70 chars, imperative, body says why | English |
Sources: raw.githubusercontent.com/{akfamily/akshare/main/docs/contributing.md, eggjs/egg/master/CONTRIBUTING.zh-CN.md, arco-design/arco-design/main/CONTRIBUTING.zh-CN.md, Tencent/tdesign-vue-next/develop/CONTRIBUTING.md, youzan/vant/main/packages/vant/docs/markdown/contribution.zh-CN.md, ElemeFE/element/dev/.github/CONTRIBUTING.zh-CN.md, apache/dolphinscheduler/dev/docs/docs/zh/contribute/join/commit-message.md, NervJS/taro/main/CONTRIBUTING.md, PaddlePaddle/docs/develop/docs/dev_guides/git_guides/submit_pr_guide_cn.md, pingcap/community/master/contributors/commit-message-pr-style.md}.
Pattern: the type/scope prefix is always English; international projects write English subjects, China-facing ones write Chinese after the prefix. Recommendation for this learner: `type(scope): 中文描述` (half-width colon + space, <= ~25 汉字), Chinese body explaining why; keep type, scope, footer tokens in English.
Type glossary for the course (commitlint list; Chinese glosses are mine, consistent with the Egg/Arco/vben explanations): `feat` 新功能 · `fix` 修复缺陷 · `docs` 文档 · `style` 代码格式（不影响逻辑）· `refactor` 重构（不加功能也不修缺陷）· `perf` 性能优化 · `test` 测试 · `build` 构建与依赖 · `ci` 持续集成配置 · `chore` 其他杂务 · `revert` 回滚。
Example message written for this brief (not from a source; passes the regex hook of §11):
```
fix(backtest): 修正手续费被按百分之一计算的错误

回测收益长期偏低，原因是 fee 写成了 0.01（1%），实际费率是 0.001（0.1%）。
本次改为从配置读取费率，并补充一个回归测试。

Refs: #12
```

### 8.4 Semantic Versioning 2.0.0 (current; CC BY 3.0) [source: https://semver.org/spec/v2.0.0.html ; raw https://raw.githubusercontent.com/semver/semver/master/semver.md ; zh https://semver.org/lang/zh-CN/]
Paraphrase by rule number: (1) declare a public API. (2) `X.Y.Z`, non-negative integers, no leading zeros, numeric increase (1.9.0 -> 1.10.0). (3) a released version is immutable; any change is a new version. (4) `0.y.z` is initial development: anything may change, the API is not to be considered stable. (5) `1.0.0` defines the public API. (6) PATCH for backward-compatible bug fixes only. (7) MINOR for backward-compatible additions, and also when something is deprecated; patch resets to 0. (8) MAJOR for any incompatible change; minor and patch reset to 0. (9) pre-release = hyphen + dot-separated identifiers from `[0-9A-Za-z-]` (`1.0.0-alpha.1`), lower precedence than the normal version. (10) build metadata = `+...`, ignored in precedence. (11) precedence: numeric compare of major, minor, patch; a pre-release sorts before its release; identifiers compare left to right (numeric < alphanumeric; more fields wins): `1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0`.
FAQ: start at `0.1.0` and bump the minor for each release while in 0.y.z; `v1.2.3` is a tag name, the version is `1.2.3`; software used in production should probably already be 1.0.0; deprecate in a minor release before removing in a major. zh terms: 语义化版本, 主版本号 / 次版本号 / 修订号, 先行版本号, 版本编译信息.
Python caveat: `pyproject.toml` versions follow the Python version-specifier scheme, not SemVer syntax. `uv version 1.0.0-alpha.1` is stored as `1.0.0a1`; `uv version --bump minor --bump alpha` gave `0.2.0 => 0.3.0a1`, then `--bump rc` -> `0.3.0rc1`, `--bump stable` -> `0.3.0`. [local, uv 0.13.5] The packaging guide notes most Python projects follow SemVer only loosely and that CalVer (`23.12`) is a legitimate alternative. [source: https://packaging.python.org/en/latest/discussions/versioning/] Release ritual verified: set or bump the version with `uv version ...` (use `--frozen` to skip re-locking) -> commit `chore(release): v0.3.0` -> `git tag -a v0.3.0 -m "v0.3.0"` -> `git describe` prints `v0.3.0`. [local]

### 8.5 Keep a Changelog 1.1.0 (default version on the site; MIT) [source: https://keepachangelog.com/en/1.1.0/ ; repo olivierlacan/keep-a-changelog source/en/1.1.0]
Paraphrase: a changelog is a curated, chronological list of notable changes per version, written for humans; every version has an entry; changes are grouped by type; versions and sections are linkable; newest first; each version shows its release date; state whether you follow SemVer. Change types: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Keep an `Unreleased` section on top and move its content into a new version section at release time. File name `CHANGELOG.md`; dates `YYYY-MM-DD`; yanked releases: `## [0.0.5] - 2014-12-13 [YANKED]`. Anti-patterns: pasting the commit log, omitting deprecations, ambiguous dates, recording only some changes. zh title 如何维护更新日志 (更新日志); type names stay in English.
**2.0.0 (dated 2026-06-07 in the project's CHANGELOG; reachable at https://keepachangelog.com/en/2.0.0/; not git-tagged; root still redirects to 1.1.0; no zh translation yet — /zh-CN/2.0.0/ serves only a short placeholder)** [source: raw.githubusercontent.com/olivierlacan/keep-a-changelog/main/{CHANGELOG.md,source/en/2.0.0/index.html.md}; curl of the site root]: same format (six types, dates, `Unreleased`, `[YANKED]`); new guidance — fixed header preamble naming the format version and the versioning scheme; version headings as reference links resolved at the bottom with compare URLs (`[Unreleased]: .../compare/v1.1.0...HEAD`); mark breaks inline with `**Breaking:**` under `Changed`/`Removed`; do not invent extra types (dependencies/performance go under the six); a changelog is the source from which release notes are derived; changelogs generated from Conventional Commits are raw material that a person must curate; CI should only do mechanics; `merge=union` or a `changelog.d/` directory against merge conflicts; and for LLMs the single line worth quoting: "machines can draft, but humans curate" (Keep a Changelog 2.0.0), with the advice to put the changelog brief into `AGENTS.md`/`CLAUDE.md`. The order of the six types differs between the deployed 2.0.0 page (Added ... Security) and the repo's main branch (by urgency: Security, Removed, Changed, Deprecated, Fixed, Added) — still in flux; teach the 1.1.0 order and mention the rest as preview.
Skeleton written for this brief (structure per 1.1.0/2.0.0; wording mine; https://keepachangelog.com/zh-CN/1.1.0/ and https://semver.org/lang/zh-CN/ both answered HTTP 200 today):
```
# 更新日志

本文件记录本项目所有值得注意的变更。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 新增 60 日均线信号。

## [0.1.0] - 2026-11-19

### Added
- 首个可用版本：数据下载、清洗与三个分析笔记本。

[Unreleased]: https://example.com/owner/repo/compare/v0.1.0...HEAD
[0.1.0]: https://example.com/owner/repo/releases/tag/v0.1.0
```

## 9. Branching models, merge policies, naming

9.1 **GitHub Flow** — steps as GitHub names them: create a branch, make changes, create a pull request, address review comments, merge, delete the branch; short descriptive branch names (their examples: `increase-test-timeout`, `add-code-of-conduct`). Fits continuously delivered projects and solo work. [source: https://docs.github.com/en/get-started/using-github/github-flow]
9.2 **Trunk-based development** — everyone integrates into one trunk; branches are short-lived and belong to one workstation; small teams may push straight to trunk, larger ones use short-lived branches + PR; release branches cut late or release from trunk; feature flags for unfinished work. DORA's research markers: three or fewer active branches, merge to trunk at least daily, no code freezes. Close to GitHub Flow; the difference is mainly where releases are cut. [source: https://trunkbaseddevelopment.com/ ; https://dora.dev/capabilities/trunk-based-development/]
9.3 **Git Flow** (V. Driessen, 2010-01-05): `master` + `develop`, supporting `feature`, `release-*`, `hotfix-*` branches, feature merges with `--no-ff`. The author's "Note of reflection" (2020-03-05) says it suits explicitly versioned software or software with several supported versions, and that teams doing continuous delivery should use a simpler workflow such as GitHub Flow. [source: https://nvie.com/posts/a-successful-git-branching-model/]
9.4 **Release branches** (Microsoft guidance, updated 2026): feature branches + PRs + a high-quality `main`; `release/<n>` branches cut from main when needed; fixes are ported between main and release by cherry-pick, not by merging the release branch back. Naming suggestions there: `users/<name>/<desc>`, `feature/<name>`, `bugfix/<desc>`, `hotfix/<desc>`. [source: https://learn.microsoft.com/en-us/azure/devops/repos/git/git-branching-guidance]
9.5 **Merge methods** (GitHub): merge commit (default, `--no-ff`, keeps every commit), squash and merge (one commit on main; loses individual commits/SHAs; trouble if the branch lives on), rebase and merge (linear, new SHAs, unsigned). "Require linear history" forbids merge commits. [source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github] Local equivalents verified: `--no-ff`, `--squash`, rebase + ff. **Protected main**: any protection rule already blocks force pushes and deletion; optional: required PR reviews, status checks, conversation resolution, signed commits, linear history, merge queue, push restrictions; rulesets are the newer stackable mechanism. [source: .../managing-protected-branches/about-protected-branches ; .../managing-rulesets/about-rulesets] Plan availability for personal private repos was not confirmed today.
Branch naming: Git itself rejects spaces, `..`, `~ ^ : ? * [`, a leading `-`, a trailing `/` or `.lock`, `@{`; Chinese names are legal; `feature` and `feature/x` cannot coexist (`cannot lock ref`). [local: `git check-ref-format --branch`] Community spec "Conventional Branch" 1.1.0 (not part of Conventional Commits): `<type>/<description>` with `feature/` (`feat/`), `bugfix/` (`fix/`), `hotfix/`, `release/`, `chore/`, lowercase + hyphens, optional ticket id; 1.1.0 adds AI-agent prefixes `ai/`, `claude/`, `codex/`, `copilot/`, `cursor/`. [source: https://conventionalbranch.org/]
Recommendation: teach GitHub Flow with squash-or-merge into a protected `main`, branch names `feat/...`, `fix/...`, `docs/...`, `chore/...` in ASCII; present trunk-based as the principle behind it (small, short-lived) and Git Flow as history plus "when you maintain several released versions".

9.6 **Where to put repositories on a Mac with iCloud sync**. Verified mechanics [local, t38]: (a) `git init --separate-git-dir <dir outside iCloud>` works for new and existing repos — `.git` becomes a one-line text file `gitdir: <path>` and all objects live elsewhere; (b) the folk trick "rename `.git` to `.git.nosync` and symlink" makes `git status` list `.git.nosync/objects/` etc. as untracked, so `git add .` would add the repository into itself — do not teach it without an ignore rule. Not verified: iCloud's actual treatment of `.git` files and of `*.nosync` names. Safest choices: practice repos in a non-synced location (e.g. `~/git-playground`) or in a `playground.nosync/` subfolder of the course folder; an existing project (if any) either moved out of Desktop/Documents or given `--separate-git-dir`; backup comes from a real remote, not from iCloud.

## 10. Classic beginner disasters and verified recoveries [local unless noted]

| # | Disaster | What Git shows | Recovery (exact, verified) |
|---|---|---|---|
| D1 | Detached HEAD (`git checkout <commit>`); commits made there, then switched away | `You are in 'detached HEAD' state...`; on leaving: `Warning: you are leaving 1 commit behind ... git branch <new-branch-name> c5a874b` | `git branch rescue c5a874b` (or `git switch -c rescue` before leaving); id lost -> `git reflog`. `git switch <commit>` refuses without `--detach` (`fatal: a branch is expected, got commit`) |
| D2 | Secret committed, last commit, not pushed | - | `git rm --cached .env` -> add `.env` to `.gitignore` -> `git commit --amend`. Old blob stays reachable via reflog until `git reflog expire --expire=now --all && git gc --prune=now` |
| D3 | Secret already pushed | - | Rotate/revoke the secret first; rewrite with `git filter-repo --sensitive-data-removal --invert-paths --path <file>`, force-push, ask the host to purge caches; all clones/forks keep it. [source: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository] `git filter-repo` is not installed here; `git filter-branch` prints a warning recommending filter-repo [local] |
| D4 | Large data / `.venv` committed | `git diff --staged --stat` shows `data/prices.parquet \| Bin 0 -> 3000000 bytes` | not pushed: `git reset --soft HEAD~1` -> `git restore --staged .` -> fix `.gitignore` -> re-add; older commit: filter-repo (as D3) |
| D5 | `git add .` staged junk | status lists `A  .env`, `A  notes.tmp` | before commit: `git restore --staged .` (edits stay); after commit: D4. Habit: `git status` + `git diff --staged --stat` before every commit |
| D6 | Nested repository added | `warning: adding embedded git repository: vendor-lib` + hint; index entry is mode 160000 (a pointer, no files) | `git restore --staged vendor-lib` or `git rm --cached -f vendor-lib` (the hint's command without `-f` errors); then delete the inner `.git` if it should be one repo, and add again |
| D7 | Someone force-pushed over your pushed commit | after `git fetch`: `+ 051dab8...c56be58 main -> origin/main (forced update)`, status `[ahead 1, behind 1]` | `git fetch && git rebase origin/main` or `git pull --no-rebase` keep your commit; **`git pull --rebase` drops it silently**; then recover with `git reflog` + `git cherry-pick <id>`; old remote value: `git reflog show origin/main` |
| D8 | You need to rewrite a pushed branch | `! [rejected] ... (non-fast-forward)` | only on your own branch: `git push --force-with-lease --force-if-includes`. With lease alone after a `git fetch`, the push went through and erased a colleague's commit; with both flags: `! [rejected] main -> main (remote ref updated since checkout)`. Never plain `--force` on shared branches |
| D9 | Committed on `main` instead of a branch (not pushed) | - | `git branch feature/g` then `git reset --hard HEAD~1`. Not yet committed: `git switch -c feature/v2` carries the edits along |
| D10 | `git init` in the parent folder / home | every sub-project appears as `?? ProjA/` | nothing committed there: delete that folder's stray `.git`; then `git init` inside the project. Check with `git rev-parse --show-toplevel` |
| D11 | Uncommitted work destroyed (`git restore .`, `git reset --hard`) | - | unstaged edits to tracked files: gone. Untracked files survive `reset --hard` (not `git clean`). Anything that was ever `git add`-ed: `git fsck --lost-found` -> `dangling blob <id>` -> `git cat-file -p <id>` |
| D12 | Merge went wrong | conflict markers / bad merge commit | during: `git merge --abort`; after, unpushed: `git reset --hard ORIG_HEAD`; pushed: `git revert -m 1 <merge>` (without `-m`: `error: commit ... is a merge but no -m option was given.`) |
| D13 | Amended a pushed commit, then followed the hint and pulled | duplicate commits + merge commit | prevention: `pull.ff only`; fix: `git reset --hard origin/main` and redo the change as a new commit |
| D14 | Stuck in an editor/pager | vi screen, or `:` at the bottom | pager: `q`; vi: `Esc :q!` [memory for both keystrokes]; configure `core.editor`, use `-m` [local] |

## 11. What changed compared with older tutorials

- `git switch` / `git restore` (introduced 2.23, stable since 2.51) replace the overloaded `git checkout`; `git checkout` still works and is not deprecated. [local man][source: RelNotes 2.23.0, 2.51.0]
- `git pull` with diverged history errors until a policy is chosen (older tutorials assume a silent merge). [local]
- `git config set/get/unset/list` subcommands since 2.46; hints now say `git config set advice.<x> false`. [local][source: RelNotes 2.46.0, 2.48.0]
- `merge.conflictStyle zdiff3` (2.35), `push.autoSetupRemote`, `--force-if-includes` (2.30), `pull.autoStash` (2.51) exist. [local `git help -c`][source: RelNotes]
- `git stash save` deprecated -> `git stash push`; `git whatchanged` prints "nominated for removal"; `git filter-branch` warns. [local]
- New in 2.52-2.54: `git last-modified`, `git repo info/structure`, experimental `git history reword|split` (reword of an old commit worked here without touching the working tree), hooks defined in config (`hook.<name>.event` + `hook.<name>.command`, `git hook list <event>`; a failing pre-commit hook blocks the commit, `--no-verify` bypasses; a config-based `commit-msg` script enforcing the Conventional Commits prefix worked). [local][source: https://github.blog/open-source/git/highlights-from-git-2-54/ ; RelNotes 2.52.0-2.54.0] `.git/hooks` is still not versioned or cloned.
- Git 3.0 (undated): default branch `main`, SHA-256 object format, reftable ref storage, Rust required to build. [source: BreakingChanges.adoc]
- GitHub: no password auth for Git; default branch of new repos is `main`. [source: about-remote-repositories ; https://github.com/github/renaming]
- `uv init` creates the repo and a `.gitignore`; uv/ruff caches and venvs self-ignore. [local]
- Keep a Changelog 2.0.0 preview and Conventional Branch 1.1.0 (AI prefixes) are 2026 developments. [source]
- Chinese Pro Git lags the English edition on restore/switch (zh sources: 23 `git checkout --`, 21 `git reset HEAD`, 1 `git restore`, 0 `git switch` in the 29 sections sampled; English undoing chapter has a "git restore" section). [source, counted locally]

## 12. Recommended learning order, analogies, and what to skip

Order (each stage verified end to end above):
0. Environment: `git --version`, inspect `git config --list --show-origin`, fix signing (§1), apply §3, decide repo location (§9.6).
1. Local loop in a throwaway repo: `init` -> `status` -> `.gitignore` first -> `add` -> `commit -m` -> `log --oneline` -> `diff` / `diff --staged` -> `show`.
2. Safe undo: `restore`, `restore --staged`, `commit --amend`, `revert`; then `reflog` as the safety net; only then `reset --soft/--mixed/--hard`.
3. Branches: `switch -c`, fast-forward vs merge commit, one deliberate conflict (§5), `branch -d`.
4. Remotes with a local bare repo: `remote add`, `push`, `clone`, `fetch` vs `pull`, rejected push, the three pull policies.
5. Conventions: Conventional Commits in Chinese, atomic commits with `add -p`, annotated tags + SemVer + `uv version --bump`, `CHANGELOG.md`.
6. Team workflow: GitHub Flow, PR review, protected main (simulate with `receive.denyNonFastForwards`), squash vs merge; `stash`; basic `rebase` + the golden rule.
7. Optional: hooks/pre-commit, `bisect`, `blame`, `--force-with-lease --force-if-includes`, `worktree` (`git worktree add ../dir -b branch` verified; Claude Code can work in worktrees), filter-repo.
Skip for a beginner: submodules, `rebase -i` beyond reword/squash, cherry-pick except as rescue, Git Flow as practice, plumbing/internals, SHA-256/reftable, commit signing, `git history`.
First real-project milestone: put the learner's existing project (if any) under Git (review `.gitignore`, first commit `chore: 初始化仓库` or `feat: ...`, tag `v0.1.0`).

Plain-Chinese analogies (author's suggestions; some are finance-flavoured):
- 提交 = 存档点 / 给项目拍一张带说明的快照；仓库 = 带时光机的项目文件夹。
- 工作区 / 暂存区 / 仓库 = 书桌 / 待寄的快递箱 / 档案柜；`git add` 是装箱，`git commit` 是封箱贴单。
- 分支 = 草稿本（平行世界），`main` = 正式稿；合并 = 把草稿誊进正式稿；快进 = 正式稿没动过，直接把书签挪到草稿最后一页。
- HEAD = "你在这里"的书签；分离头指针 = 书签插在某一页上而不是夹在某个分支名上。
- `revert` = 会计的红字冲销（再记一笔相反的分录，账本不撕页）；`reset` = 撕掉账本最后几页（只有没给别人看过的账才能撕）；`--amend` = 改写最后一笔还没报送的分录。
- `reflog` = 行车记录仪：HEAD 去过的每一站都记着，默认约 90 天。
- 远程仓库 = 共享档案柜；`push` 上传存档，`fetch` 只取回消息不动自己的稿子，`pull` = `fetch` + 合并；`--force` = 用自己的存档覆盖共享存档。
- 冲突 = 两个人改了同一句话，Git 不替你做主。`.gitignore` = 门卫的免登记名单。`stash` = 先把桌上没做完的东西塞进抽屉。
- 变基 = 把你的改动搬到最新主线上重演一遍（提交编号会变）。`bisect` = 二分法猜数字。标签 = 给某个存档贴"v1.0.0 正式版"。
- Conventional Commits 的 type = 记账凭证的科目，描述 = 摘要；SemVer = "破坏性.新功能.修复"；CHANGELOG = 写给人看的版本大事记，不是流水账（`git log`）。

English message decoder (all strings captured today [local]):
| Git says | 意思 |
|---|---|
| `nothing to commit, working tree clean` | 没有可提交的改动，工作区干净 |
| `Untracked files` / `Changes not staged for commit` / `Changes to be committed` | 未跟踪 / 已修改未暂存 / 已暂存待提交 |
| `Your branch is ahead of 'origin/main' by 1 commit.` | 本地多 1 个提交，尚未推送 |
| `... is behind ... and can be fast-forwarded.` | 远程有新提交，可以直接快进 |
| `... have diverged` | 本地和远程各有对方没有的提交 |
| `fatal: not a git repository (or any of the parent directories): .git` | 当前文件夹不在任何仓库里 |
| `fatal: The current branch main has no upstream branch.` | 这个分支还没有对应的远程分支 |
| `fatal: Need to specify how to reconcile divergent branches.` | 拉取时两边分叉了，要你决定合并还是变基 |
| `! [rejected] main -> main (fetch first)` | 远程有你没有的提交，先拉取 |
| `CONFLICT (content): Merge conflict in <file>` | 合并冲突，需手工解决 |
| `You are in 'detached HEAD' state.` | 处于分离头指针状态 |
| `error: Your local changes to the following files would be overwritten by merge` | 有未提交的改动会被覆盖，先提交或贮藏 |
| `error: the branch 'x' is not fully merged` | 分支还有未合并的提交，删除会丢失 |
| `Aborting commit due to empty commit message.` | 提交说明为空，提交已取消 |
| `error: cannot run gpg: No such file or directory` | 开启了提交签名但没有 gpg（见 §1） |
| `warning: adding embedded git repository` | 把另一个仓库整个 add 进来了 |

## 13. Chinese-English glossary

Authority: the term table in Pro Git zh's `TRANSLATION_NOTES.asc` (which itself defers to git's `po/zh_CN.po`), cross-checked by counting actual usage in 29 downloaded book sections. [source: https://raw.githubusercontent.com/progit/progit2-zh/master/TRANSLATION_NOTES.asc ; book sources]

| English | Pro Git 中文版用词 | 备注 |
|---|---|---|
| repository / bare repository | 仓库 / 裸仓库 | 术语表写"纯仓库"，正文实际用"裸仓库" |
| working directory, working tree | 工作目录、工作区 | 两者混用 |
| staging area / index | 暂存区（暂存区域）/ 索引 | stage 暂存，unstage 取消暂存 |
| tracked / untracked | 已跟踪 / 未跟踪 | |
| modified / staged / committed | 已修改 / 已暂存 / 已提交 | "三种状态" |
| commit / commit message / commit history | 提交 / 提交说明、提交信息 / 提交历史 | parent 父提交；amend 修补（修补提交） |
| snapshot / checksum / hash | 快照 / 校验和 / 哈希值 | |
| branch / topic branch / long-running branch | 分支 / 主题分支 / 长期分支 | 书中不用"特性分支/功能分支" |
| HEAD / detached HEAD | HEAD（头指针）/ 分离头指针 | 子模块一章也写"游离的 HEAD" |
| checkout / switch | 检出 / （书中未涉及 switch） | |
| merge / merge commit / fast-forward / three-way merge | 合并 / 合并提交 / 快进 / 三方合并 | conflict 冲突，合并冲突；冲突标记 |
| rebase / interactive rebase / squash | 变基 / 交互式变基 / 压缩 | cherry-pick 拣选 |
| revert / reset / undo | 还原 / 重置 / 撤消 | 注意是"撤消" |
| stash | 贮藏 | |
| reflog / ref | 引用日志 / 引用 | |
| tag / annotated tag / lightweight tag | 标签（打标签）/ 附注标签 / 轻量标签 | |
| remote / clone / fetch / pull / push | 远程仓库 / 克隆 / 抓取 / 拉取 / 推送 | force push 强制推送 |
| remote-tracking branch / tracking branch / upstream | 远程跟踪分支 / 跟踪分支 / 上游（上游分支） | |
| pull request / fork / issue | 拉取请求 / 分叉 / 议题 | GitHub 一章里"拉取请求"93 次，维护一节也写"合并请求"（56 次）；collaborator 合作者。Gitee/GitLab 界面称"合并请求" [memory] |
| hook / submodule / alias / patch / diff | 钩子 / 子模块 / 别名 / 补丁 / 差异（diff） | blame 文件标注；bisect 二分查找 |
| .gitignore / pattern | 忽略文件 / 模式（glob 模式） | |
Related specs: Conventional Commits 约定式提交（类型、范围、描述、正文、脚注、破坏性变更）; SemVer 语义化版本（主版本号、次版本号、修订号、先行版本号）; changelog 更新日志.
GitHub's Chinese glossary deviates in places — fetch 提取, checkout 签出, cherry-pick 挑拣, blame 追溯, commit message 提交消息, detached HEAD 拆离的 HEAD, issue 问题 — so learners will meet both vocabularies. [source: https://docs.github.com/zh/get-started/learning-about-github/github-glossary]

## 14. Not verified today

- Real iCloud behaviour toward `.git` contents and `*.nosync` names (only simulated; community reports, no Apple statement).
- Anything needing an account: GitHub/Gitee push, `osxkeychain` prompts, `gh auth login` (gh not installed), branch protection UI, plan availability of protected branches/rulesets for personal private repos.
- Whether the Claude Code desktop app overrides `commit.gpgsign` in its own git calls.
- Where leftover signing keys in `~/.gitconfig` usually come from (a Git GUI client is a guess).
- `git filter-repo` (not installed), SSH commit signing, `fetch.prune` behaviour, `less` rendering of Chinese when LANG is not UTF-8, pytest/mypy cache self-ignore.
- Version where `push.autoSetupRemote` appeared (2.37) and the date GitHub removed password auth (2021-08-13) are from memory; the switch to `main` on 2020-10-01 was verified on 2026-11-20 at https://github.blog/changelog/2020-10-01-the-default-branch-for-newly-created-repositories-is-now-main/ .
- Keep a Changelog 2.0.0 is still changing; re-check before quoting its type order.

## 15. Evidence kept in this scratch directory

Throwaway repos `t01-init` ... `t44-orighead` (one per experiment), helper `mk.sh`, fake global config `fake-global.gitconfig`, local manual dumps in `man/`, downloaded primary sources in `dl/` (`specs/` CC + SemVer + KAC 1.1.0/2.0.0 incl. zh translations, `gitignore/`, `relnotes/` Git 2.23-2.56 + BreakingChanges, `progit-zh/`, `progit-en/`, `zh-guides/`, `commitlint/`, `pypi/`, `kac-site/`, `cc-site/`). Tool versions seen on PyPI today: commitizen 4.19.4, pre-commit 4.7.0, conventional-pre-commit 4.5.0, git-cliff 2.14.2, python-semantic-release 10.7.0, nbstripout 0.9.2, git-filter-repo 2.47.0, towncrier 26.9.0 (none installed).
