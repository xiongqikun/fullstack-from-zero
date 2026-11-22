# Research brief: foundations-macos (stages 0-1 on macOS 27, zsh 5.9)

Date of all checks: 2026-11-19. Raw material for lesson builders, not learner-facing text.

**Tags.** `[local]` = I ran or read it on this machine today. `[source: URL]` = read in that primary source today. `[memory]` = not verified today.
**Privacy.** User name, host name and private folder names are replaced by `you`, `host`, `<playground>`.
**Method.** Commands were run in a throwaway playground inside my scratch directory, in a clean shell (`/bin/zsh -f`, zsh 5.9) so the learner's start-up files could not hide default behaviour; the learner's real interactive environment was inspected read-only with `zsh -l -i -c ...`. VS Code facts come from the official docs plus read-only inspection of the installed app bundle (version 1.145.2). Nothing outside the scratch directory was written.

**Limits of this sandbox (why some things are marked unverified).** No pseudo-terminal (so no Tab completion, Ctrl+R, `less` keys, prompts), no GUI (no Finder, VS Code or Warp screens), and these programs refuse to run: `ps`, `pgrep`, `sudo`, `open`, `brctl`, `fileproviderctl`, `man -k` [local]. `/usr/bin/trash` was not executed because it writes to the user's Trash.

---

## 1. Findings that should change decisions (read this first)

1. **`git commit` fails when Git is set to sign without GPG.** If global Git config has `commit.gpgSign = true`, `gpg.program = gpg`, `gpg.format = openpgp`, but no `gpg` exists on the login-shell PATH, every commit fails [local]. Real output in a scratch repo with that configuration:
   ```
   error: cannot run gpg: No such file or directory
   error: gpg failed to sign the data:
   fatal: failed to write commit object
   ```
   Repo-local `git config commit.gpgsign false` (or `git -c commit.gpgsign=false commit ...`) makes commits work [local]. The Git lessons (1.6+) and any auto-check that commits must check for this before the learner's first commit. I did not touch global config.
2. **The classic first command breaks in zsh.** `echo "Hello, World!"` typed at an interactive zsh prompt gives `dquote>` and then `zsh: unmatched "` because `!"` is history-expansion syntax [local]. `echo 'Hello, World!'` (single quotes), `echo Hello!` and `echo "Hello! there"` work [local].
3. **`pip3` and `python3` are different Pythons.** `python3` = 3.14.9 (uv-managed, first on PATH); `pip3` = `/usr/bin/pip3` = pip 21.2.4 for Xcode's Python 3.9; `pip` = `command not found` [local]. Never teach `pip3 install`.
4. **The AI tutor's shell is not the learner's Terminal.** In Claude Code's Bash tool `grep`, `find` and `rg` are wrapper functions (`grep --version` prints `ugrep 7.8.4`; the real `/usr/bin/grep` is `grep (BSD grep, GNU compatible) 2.6.0-FreeBSD`), `LANG` is empty, and error prefixes look like `(eval):cd:18:` [local]. Lessons must quote output captured from a clean zsh, and the tutor must not present its own tool output as "what you will see".
5. **VS Code is now agent-first and ships weekly.** The official "getting started" URL redirects to an agents tutorial that requires a GitHub sign-in; Chat sits in the Secondary Side Bar by default; Stable releases are weekly since 1.111 (2026-03-09) [source: https://code.visualstudio.com/docs/agents/agents-tutorial] [source: https://code.visualstudio.com/updates/v1_111]. Check whether the learner's own user settings already turn on AI inline completions or a strict type-checking mode. A workspace-level `"chat.disableAIFeatures": true` exists and is allowed in workspace settings (scope: window) [local][source: https://code.visualstudio.com/docs/supporting/faq].
6. **New folders open in Restricted Mode with a banner, not a dialog.** `security.workspace.trust.startupPrompt` defaults to `never` in the installed build [local] and in the docs [source: https://code.visualstudio.com/docs/editing/workspaces/workspace-trust]. Opening a terminal, running tasks, debugging and AI agents are limited until the learner trusts the folder.
7. **Check the learner's iCloud state.** Whether Desktop & Documents sync is on; whether "Optimize Mac Storage" is on (`defaults read com.apple.bird optimize-storage`); whether dataless (cloud-only) items exist under Desktop or Documents; whether `~/Developer` exists. iCloud can put the BSD `hidden` flag on files inside a virtual environment in a synced folder, which makes Python skip `.pth` files (section 5) [local].
8. **Chinese input defaults work against code.** Apple Pinyin uses full-width punctuation unless half-width is switched on (`usesHalfwidthPunctuation = 0` means off); Control-Space is commonly the system shortcut for switching input source [local], which is also VS Code's default "Trigger Suggest" key, so the system will most likely take the keystroke first (inference; not seen on screen).
9. **`<details>` hints render in both places but are plain text in the editor.** GitHub's renderer and VS Code's preview both keep `<details>/<summary>` and render Markdown inside it; task lists and `> [!NOTE]` alerts render on GitHub only (section 7) [local].

---

## 2. The machine as the learner will meet it [local]

| Item | Value |
|---|---|
| OS | macOS 27.2.1 (build 26B131), arm64. Apple's guides call it "macOS 27 Golden Gate" [source: https://support.apple.com/guide/terminal/welcome/mac] |
| Shell | `/bin/zsh`, zsh 5.9. `/bin/bash` is 3.2.57 |
| Prompt | Default `PS1="%n@%m %1~ %# "` from `/etc/zshrc`, shown as `you@host ~ %` |
| Locale | `/etc/zprofile` now exports `LANG=C.UTF-8` when LANG is unset (new compared with older macOS) |
| History | `~/.zsh_history`, `HISTSIZE=2000`, `SAVEHIST=1000`; Apple Terminal also keeps per-window history in `~/.zsh_sessions/` |
| Aliases | Only zsh's two defaults (`run-help=man`, `which-command=whence`). No `ll` |
| `~/.zprofile` | Usually holds lines added by installers, for example Homebrew (`eval "$(/opt/homebrew/bin/brew shellenv)"`); differs per machine |
| `~/.zshrc` | Often edited by installers (version managers, tool completions, `compinit`) and by the learner; differs per machine, so read it before teaching |
| PATH order | Installers usually put their own directories before `/opt/homebrew/bin`, ..., `/usr/local/bin`, `/usr/bin`, `/bin`; check with `echo $PATH \| tr ':' '\n'` |
| Tools | `git` 2.54.0 (Apple Git-157) at `/usr/bin/git`; `python3`/`python` from uv (3.14.9); `/usr/bin/python3` is 3.9.6; `uv` 0.13.5 (Homebrew); `ruff` 0.17.2; `node` v26.12.0; `code` = `/usr/local/bin/code` (symlink into the VS Code app); `brew` 7.0.10 at `/opt/homebrew`; `jq` at `/usr/bin/jq` |
| Not present | `rg`, `fd`, `tree`, `bat`, `gpg`, `dos2unix`, GNU coreutils (`gls`, `gsed`), `tldr` |
| Editors in terminal | `nano` is a symlink to `pico`; `vi` -> `vim` 9.1; `less` 668. `EDITOR`/`VISUAL` unset; `git var GIT_EDITOR` prints `vi`, so `git commit` without `-m` opens vim; Git's pager is `less` (leave with `q`) |
| Developer tools | `xcode-select -p` = `/Applications/Xcode.app/Contents/Developer`; Command Line Tools package 27.2 also installed; `/usr/bin/git`, `/usr/bin/python3`, `/usr/bin/make` are shims |
| Apple's built-in Git config | `credential.helper = osxkeychain`, `init.defaultBranch = main` |
| Global gitignore | Not set by default; some machines have one from an earlier setup (`git config get core.excludesFile`) |
| Finder | "Show all filename extensions" and "show hidden files" are not set (defaults: off). System language order differs per learner, so lessons name menus in English with a Chinese gloss |
| Terminal apps | Terminal 2.15 (default profile "Basic"); VS Code 1.145.2 |
| Filesystem | Case-insensitive, case-preserving: writing `README.md` after `Readme.md` overwrites the same file; `cat Fruits.TXT` opens `fruits.txt` |

---

## 3. Terminal: verified teaching material

All transcripts are real output from this machine in a clean zsh. In an interactive window the error prefix is `zsh:` (with `-c` it is `zsh:1:`); `cd` errors read `cd: no such file or directory: x`.

### 3.1 Opening a terminal, prompt, stopping things
- Terminal.app: Spotlight (Command-Space), type Terminal; or `/Applications/Utilities`. Apple's example prompt is `michael@<computer-name> ~ %` (Apple's host name replaced by a placeholder in this copy) = user, computer, current folder, prompt symbol [source: https://support.apple.com/guide/terminal/open-or-quit-terminal-apd5265185d-f365-44cb-8b09-71a064a42125/mac].
- From Finder: View > Show Path Bar, Control-click a folder in the path bar, "Open in Terminal" [source: https://support.apple.com/guide/terminal/open-new-terminal-windows-and-tabs-trmlb20c7888/mac]. Dragging a file or folder into the window inserts its absolute path [source: https://support.apple.com/guide/terminal/drag-items-into-a-terminal-window-trml106/mac].
- VS Code: ⌃` toggles the integrated terminal; it starts in the opened folder and runs a login shell like Terminal.app [source: https://code.visualstudio.com/docs/terminal/basics] [source: https://code.visualstudio.com/docs/terminal/profiles].
- Terminal.app keys: Command-K clear to start, Command-T tab, Command-N window, Command-Plus/Minus font size, Control-A/E line start/end, Control-U delete the line, Control-W delete word, Option-Left/Right by word, Control-R reverse history search, Command-Period = Control-C [source: https://support.apple.com/guide/terminal/keyboard-shortcuts-trmlshtcts/mac]. zsh's own bindings on this Mac agree: `^A ^E ^U(kill-whole-line) ^K ^W ^L(clear-screen) ^R ^D(delete-char-or-list) ^I(expand-or-complete)`; Up arrow = `up-line-or-search` [local].
- Ways out, to teach in the first lesson: Control-C (stop a command, and leave `dquote>` / `quote>` / `>` continuation prompts), `q` (leave `less`/`man`), `exit` or Control-D on an empty line (end the shell), `:q!` then Return (leave vim) [memory for the keys; bindings above are local].
- `history` in zsh lists only the last 16 entries; `history 1` lists all; `!!` repeats the last command [local].
- Tab completion: when `~/.zshrc` runs `compinit` (many installers add it), the full completion system is loaded (`compdef` exists in the login shell) [local]; what it looks like on screen is [memory]. In VS Code's terminal a separate suggestion widget appears as well (terminal IntelliSense is on by default; Tab inserts the suggestion) [local][source: https://code.visualstudio.com/docs/terminal/shell-integration].

### 3.2 Navigation (lesson 0.5)
```
% pwd
<playground>
% mkdir notes
% mkdir -p projects/hello/src
% mkdir projects/a/b
mkdir: projects/a: No such file or directory
% ls -F
notes/
projects/
% ls -la
drwxr-xr-x@ 4 you  wheel  128 Nov 19 15:07 .
drwxr-xr-x@ 3 you  wheel   96 Nov 19 15:07 ..
drwxr-xr-x@ 3 you  wheel   96 Nov 19 15:07 notes
% cd projects/hello/src; cd ../..; pwd      -> <playground>/projects
% cd nonexistent
cd: no such file or directory: nonexistent
% cd notes/todo.txt
cd: not a directory: notes/todo.txt
```
`cd` alone goes home; `cd -` goes back and prints the folder; `echo ~` prints `/Users/you` [local]. The `@` after the permissions means "has extended attributes" (here `com.apple.provenance`); see them with `ls -l@` [local].

### 3.3 Safe file operations (lesson 1.1)
```
% cp notes notes-copy
cp: notes is a directory (not copied).
% cp -R notes notes-copy
% echo IMPORTANT > a.txt; echo junk > b.txt; mv b.txt a.txt; cat a.txt
junk                                  <- mv and cp overwrite silently
% mv -i b.txt a.txt
overwrite a.txt? (y/n [n]) not overwritten
% rm notes-copy
rm: notes-copy: is a directory
% rmdir notes-copy
rmdir: notes-copy: Directory not empty
% rm -i b.txt
remove b.txt?
```
- `mv -n` never overwrites; `cp -i`, `mv -i`, `rm -i` ask first [local].
- zsh itself asks before `rm *`: `zsh: sure you want to delete all 3 files in <folder> [yn]?` (interactive shells only; not for `rm -r folder`) [local].
- **BSD trailing-slash trap:** `cp -R src/ dest` copies the *contents* of `src`; `cp -R src dest` copies the folder itself [local].
- **Trash from the terminal:** `/usr/bin/trash` ships with macOS; `man trash` says "First appeared in macOS 15.0"; usage `trash [-v] [-s] FILE...` [local, man page and binary only; not executed]. Older advice to `brew install trash` is obsolete. VS Code's Explorer delete also goes to the Trash (`files.enableTrash` default true) [local].
- `rm` has no undo: `man rm` lists `-P` as "no effect" and `-W` (undelete) as limited [local].

### 3.4 Viewing and searching (lesson 1.2)
`cat -n`, `head -n 2`, `tail -n 2`, `wc -l`, `grep -n`, `grep -i`, `grep -c`, `grep -v`, `grep -r "milk" .`, `grep -rn --include="*.txt" apple .`, `find . -name "*.txt"`, `find . -iname`, `find . -type d` all behave as expected with the real BSD tools in a clean zsh [local]. `grep` exits 1 when nothing matches (no message). Example of the tutor-shell difference: `grep -r "milk" .` prints `./notes/todo.txt:buy milk` in the learner's shell but `notes/todo.txt:buy milk` in Claude Code's Bash tool [local].
```
% find . -name *.txt          (unquoted, two .txt files in the folder)
find: fruits.txt: unknown primary or operator
% find -name "*.txt"
find: illegal option -- n      (BSD find needs a path: find . -name ...)
```
ripgrep is not installed; mention it only as awareness (VS Code search uses it internally [memory]).

### 3.5 Pipes and redirection
```
% echo "first line" > out.txt; echo "second line" >> out.txt; echo oops > out.txt; cat out.txt
oops                                   <- > replaces the whole file
% ls nosuchdir > listing.txt           (error still appears on screen; file is empty)
% ls nosuchdir 2> errors.txt           (error goes to the file)
% ls notes nosuchdir > all.txt 2>&1
% cat fruits.txt | grep -i banana | wc -l
       2
% cd nosuchdir && echo "not shown"     ;  cd nosuchdir || echo "cd failed, so this runs"
% true; echo $?; false; echo $?        -> 0 then 1
```
`setopt noclobber` makes `>` refuse to overwrite (`zsh: file exists: out.txt`); `>|` forces [local]. Also verified: `tee`, `$(date +%Y-%m-%d)`, here-documents.

### 3.6 Wildcards and quoting: zsh-specific behaviour
```
% ls *.md
zsh: no matches found: *.md            (bash would pass *.md through to ls)
% echo fastapi[standard]
zsh: no matches found: fastapi[standard]
% echo https://example.com/search?q=zsh&lang=zh
zsh: no matches found: https://example.com/search?q=zsh     (and & starts a background job)
% touch my notes.txt; ls               -> two files: my, notes.txt
% cat "my notes.txt"; cat my\ notes.txt; cat 'my notes.txt'   -> all three work
% mkdir 学习笔记; touch 学习笔记/第一课.md; ls 学习笔记/*.md   -> works
% ls **/*.md                           -> recursive glob works by default
% echo *                               -> does not include dot-files;  echo .*  never includes . or ..
```
Rule to teach: quote anything containing spaces, `* ? [ ] & ! $ # ( )` or a URL. zsh option NOMATCH is the default: "If a pattern for filename generation has no matches, print an error" [source: https://zsh.sourceforge.io/Doc/Release/Options.html]. Variables: `GREETING = hello` gives `command not found: GREETING`; double quotes expand `$VAR`, single quotes do not [local].

Comments: default interactive zsh does **not** treat `#` as a comment (`echo hi # x` prints `hi # x`; `ls x # note` complains about `#` and `note`). A `~/.zshrc` that sets `interactive_comments` makes pasted comments work [local]. Do not rely on that in lessons meant to be portable.

### 3.7 Environment, PATH, which/type, start-up files, aliases (lesson 1.3)
```
% which ls; which cd; which python3
/bin/ls
cd: shell built-in command
<uv-bin-dir>/python3
% which -a python3
<uv-bin-dir>/python3
/usr/bin/python3
% type ls; type cd
ls is /bin/ls
cd is a shell builtin
% nosuchcommand
zsh: command not found: nosuchcommand
% PATH=/nonexistent; ls
zsh: command not found: ls
% MYVAR=inline zsh -f -c 'echo "[$MYVAR]"'     -> [inline]; plain MYVAR=abc is not seen by child programs until exported
```
- Start-up order: `.zshenv`, then for login shells `/etc/zprofile` and `~/.zprofile`, then for interactive shells `/etc/zshrc` and `~/.zshrc`, then `.zlogin` [source: https://zsh.sourceforge.io/Doc/Release/Files.html]. Terminal.app and VS Code's terminal start login shells on macOS, so both files run [source: https://code.visualstudio.com/docs/terminal/profiles].
- Old tutorials say "edit `~/.bash_profile`": wrong since macOS 10.15, where zsh became the default [source: https://support.apple.com/en-us/102360].
- **Safe practice without touching the real files:** `ZDOTDIR=/path/to/practice-dir zsh -i` starts a shell that reads `practice-dir/.zshrc` instead of `~/.zshrc`; verified with an alias defined there. `zsh -n file` checks syntax without running (`bad.zshrc:3: unmatched "`, exit 1) [local].
- An alias defined and used on the same command line does not work (aliases expand when the line is read); on the next line it does [local].

### 3.8 Permissions and sudo
```
% ./hello.sh
zsh: permission denied: ./hello.sh
% hello.sh
zsh: command not found: hello.sh        (current folder is not on PATH; use ./hello.sh)
% chmod +x hello.sh; ls -l hello.sh; ./hello.sh
-rwxr-xr-x@ 1 you  wheel  34 Nov 19 15:10 hello.sh
hello from script
% chmod 000 secret.txt; cat secret.txt
cat: secret.txt: Permission denied
```
`chmod u+x`, `chmod 644`, `chmod 755`, `stat -f "%Sp %OLp %N"` verified; `umask` is `022` [local]. `sudo` could not be run here. Teach it as awareness only: Homebrew is designed so that "you don't need sudo after Homebrew's initial installation" [source: https://docs.brew.sh/Installation]. "Operation not permitted" (macOS privacy or system protection) is a different message from "Permission denied" (file mode) [memory for the distinction; both strings seen locally].

### 3.9 Processes
`sleep 300 &` then `jobs` shows `[1]  + running    sleep 300`; after a stop signal `[1]  + suspended (signal)  sleep 300`; `kill %1` and `kill <pid>` end it; `kill -l` lists signal names [local]. `ps` and `pgrep` are blocked in this sandbox, so no real `ps` output is included. Control-C / Control-Z / `fg` at a real keyboard are [memory]. Postpone `ps`/ports until servers appear (stage 5).

### 3.10 Getting help
```
% ls --help
ls: unrecognized option `--help'
usage: ls [-@ABCFGHILOPRSTUWXabcdefghiklmnopqrstuvwxy1%,] [--color=when] [-D format] [file ...]
% cp --help            -> cp: illegal option -- -   (then a usage line)
% help cd              -> zsh: command not found: help
% man cd               -> shows the generic BUILTIN(1) page, not zsh's cd
% man nosuchcommandxyz -> No manual entry for nosuchcommandxyz
```
BSD core tools have no `--help`; use `man ls` (pager: Space, `b`, `/word`, `n`, `q`). Modern tools do: `git --help`, `python3 --help`, `uv --help`, `code --help` [local]. zsh builtins are in `man zshbuiltins`.
`uvx tldr tar` works without installing anything permanently and `uvx tldr -L zh ls` prints Chinese pages (tldr 3.4.4) [local]. Caveat: the default page for `ls` shows GNU options such as `ls --all`, which fail on macOS [local].

### 3.11 Hidden files, extensions, encodings, line endings
- `ls -a` shows dot-files; `ls -A` omits `.` and `..` [local]. Finder: Shift-Command-Period toggles hidden files [memory]. Finder > Settings > Advanced > "Show all filename extensions" [source: https://support.apple.com/guide/mac-help/show-or-hide-filename-extensions-on-mac-mchlp2304/mac].
- A second kind of hidden: the BSD `hidden` flag. `chflags hidden f` then `ls -lO f` shows `hidden`; `chflags nohidden` clears it [local]. This matters for iCloud (section 5).
- `.DS_Store`: Finder's per-folder view-settings file [memory]. One often sits in a project root; a global gitignore may already ignore it [local]; iCloud does not sync it [source: https://eclecticlight.co/2026/01/06/exclude-or-include-items-in-backup-search-icloud-drive-and-quicklook-preview/]. Still put `.DS_Store` in every repository's own `.gitignore`, because a global ignore does not travel with the repository.
- Extensions: Finder hides them by default here, so `notes.txt` may display as `notes`; `file <name>` reports the real content type whatever the extension [local]. TextEdit saves rich text (`.rtf`) unless switched to plain text, so do not use it to create code or Markdown files [memory].
```
% printf '你好, world\n' > utf8.txt; file utf8.txt; wc -c utf8.txt; wc -m utf8.txt
utf8.txt: Unicode text, UTF-8 text
      14 utf8.txt          (bytes)
      10 utf8.txt          (characters: each Chinese character is 3 bytes)
% iconv -f UTF-8 -t GBK utf8.txt > gbk.txt; file gbk.txt; cat gbk.txt
gbk.txt: ISO-8859 text
���, world
% python3 -c "print(open('gbk.txt', encoding='utf-8').read())"
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4 in position 0: invalid continuation byte
% file crlf.txt; cat -v crlf.txt
crlf.txt: ASCII text, with CRLF line terminators
line1^M
% ./crlf.sh
zsh: ./crlf.sh: bad interpreter: /bin/zsh^M: no such file or directory
```
`iconv -f GBK -t UTF-8` repairs the text; `tr -d '\r'` removes CR; a UTF-8 BOM shows as `UTF-8 (with BOM) text`; a file without a final newline counts as 0 lines in `wc -l` [local].

### 3.12 Homebrew, nvm, Command Line Tools, `open`, `code`
- Homebrew: "The Package Manager for Everywhere"; installs each package into its own folder in the Cellar and links it into the prefix (`/opt/homebrew` on Apple silicon); supports macOS 15 or later [source: https://brew.sh/] [source: https://docs.brew.sh/Installation]. Here: Homebrew 7.0.10 [local]. Read-only commands for a lesson: `brew --version`, `brew --prefix`, `brew list`.
- nvm 0.40.8 was seen installed through Homebrew, which the nvm README says "is not supported"; current upstream is v0.41.0 [local][source: https://raw.githubusercontent.com/nvm-sh/nvm/master/README.md]. Awareness only until stage 4.
- `xcode-select --install` is not needed here. Keep one line for the error after OS updates ("invalid active developer path") [memory].
- `open` usage text was read (`open .`, `open -a <app>`, `open -R` reveal in Finder, `open -t`), but Launch Services is blocked in this sandbox, so no run [local for the help text].
- `code --help` (1.145.2): `code .`, `code <file>`, `-g file:line`, `-n`, `-r`, `-d a b`, `-w/--wait`, `--profile <name>`, `--list-extensions`, `--install-extension <id>` [local]. The palette command that installs the launcher is now titled "Shell Command: Install 'code' and optionally 'copilot' commands in PATH" and offers to install the Copilot CLI [local][source: https://code.visualstudio.com/docs/setup/mac].

### 3.13 BSD versus GNU (Linux tutorials and AI answers often assume GNU)
Fail on this Mac: `ls --all`, `sed -i "s/a/b/" f` (needs `sed -i ''`), `grep -P`, `date -d yesterday` (use `date -v-1d`), `head -n -1`, `find -name x` without a path. Work: `ls --color=auto`, `readlink -f`, `xargs -r` [local]. Teach the reflex "an option was rejected, so check `man`", not GNU installs.

### 3.14 Messages the learner will see (every string captured locally; the "usual cause" column is my explanation)

| Message | Plain meaning | Usual cause |
|---|---|---|
| `zsh: command not found: X` | No program called X on PATH | Typo, tool not installed, pasted the `$` or `%` prompt character (`command not found: $`) |
| `no such file or directory` | That path does not exist from here | Wrong folder, typo, missing quotes around spaces |
| `zsh: no matches found: ...` | A wildcard character matched nothing | Unquoted `*`, `?`, `[ ]`, URL |
| `dquote>` / `quote>` | zsh is waiting for a closing quote | Unclosed quote, `!"`; press Control-C |
| `zsh: parse error near ...` | The line is not valid shell | Trailing `|`, stray symbol |
| `Permission denied` | File mode forbids it | Script not executable, protected file |
| `Operation not permitted` | macOS itself refused | Privacy protection of Desktop/Documents/Downloads, system areas |
| `is a directory` / `Not a directory` / `File exists` / `Directory not empty` | As written | `rm`/`cp` without `-r`/`-R`, `cd` into a file, `mkdir` twice |
| `illegal option` / `unrecognized option` + `usage:` | The tool does not know that option | GNU option on a BSD tool |
| `bad interpreter: ...^M` | The script has Windows line endings | CRLF file |

---

## 4. VS Code for beginners, as it is today

**Verified in docs and in the installed build (1.145.2); no screen was seen.** Latest Stable is 1.147 (2026-11-18) [source: https://code.visualstudio.com/updates]. VS Code "ships weekly releases" [source: https://code.visualstudio.com/docs/setup/mac], so teach command names and settings keys, not screenshots.

- **Layout:** Activity Bar, Primary Side Bar (Explorer, Search, Source Control, Extensions), Editor, Panel (terminal, problems), Status Bar, and a Secondary Side Bar that "by default, contains the Chat view" [source: https://code.visualstudio.com/docs/getstarted/userinterface].
- **Open a folder:** File > Open... (⌘O; the command is titled "Open..." and takes files or folders; "Open Folder..." has no default macOS shortcut) [local, bundle] or `code .`. A single click opens a file in *preview mode* (italic tab title, replaced by the next file); double-click keeps it; `workbench.editor.enablePreview` turns this off [source: same][local].
- **Trust:** new folder -> Restricted Mode banner; trust via the banner's Manage link or "Workspaces: Manage Workspace Trust". Trusting a parent folder (for example `~/Developer`) covers its subfolders [source: https://code.visualstudio.com/docs/editing/workspaces/workspace-trust].
- **Settings:** ⌘, opens the Settings editor; "Preferences: Open User Settings (JSON)" / "Open Workspace Settings (JSON)"; user file is `~/Library/Application Support/Code/User/settings.json`; workspace file is `.vscode/settings.json`; workspace overrides user; `@modified` filters changed settings; language blocks look like `"[markdown]": {...}` [source: https://code.visualstudio.com/docs/configure/settings].
- **Saving:** default is manual save (dot on the tab); File > Auto Save toggles `afterDelay`; values `off | afterDelay | onFocusChange | onWindowChange`, delay 1000 ms [source: https://code.visualstudio.com/docs/editing/codebasics]. Format on save is off by default and "when `files.autoSave` is set to `afterDelay`, the file will only be formatted when saved explicitly" [local, setting description in the build]. So `onFocusChange` is the auto-save mode that still formats.
- **Defaults confirmed in the build:** `files.encoding` `utf8`; `files.insertFinalNewline` false; `files.trimTrailingWhitespace` false; `explorer.confirmDelete` true; terminal IntelliSense (`terminal.integrated.suggest.enabled`) true; Markdown files get word wrap on and Unicode highlighting off [local].
- **Markdown:** ⇧⌘V toggles preview, ⌘K V opens it to the side [source: https://code.visualstudio.com/docs/languages/markdown][local keybindings]. Built in: KaTeX math and Mermaid diagrams. There is also an experimental rendered "Markdown Editor" (reopen from the breadcrumbs editor-type dropdown); in 1.147 it edits tables cell by cell and renders `<details>` [source: https://code.visualstudio.com/updates/v1_147].
- **Source Control view:** ⌃⇧G; needs Git installed and `user.name`/`user.email` set; staging selects changes for the next commit [source: https://code.visualstudio.com/docs/sourcecontrol/overview]. Commits made from this view hit the gpg failure of section 1 too, if the machine has it.
- **Extensions:** ⇧⌘X. Workspace recommendations live in `.vscode/extensions.json` as `{"recommendations": ["publisher.name"]}`; VS Code prompts on first open; since 1.97 installing from a new publisher asks for publisher trust [source: https://code.visualstudio.com/docs/configure/extensions/extension-marketplace].
- **Check what is installed** (`code --list-extensions`): a learner may already have Python, Pylance, Jupyter, GitLens and AI extensions. The course needs Ruff, EditorConfig, markdownlint and, if wanted, the Chinese language pack. Git needs no extra extension (support is built in); GitLens adds inline blame text that a beginner may find noisy [memory].
- **IDs checked today:** `EditorConfig.EditorConfig` 0.18.2 (VS Code still needs this extension; it is listed under "Download a Plugin") [source: https://editorconfig.org/] [source: https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig]; `DavidAnson.vscode-markdownlint` 0.62.1 [source: https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint]; `charliermarsh.ruff` (bundles ruff 0.17.5, prefers the environment's ruff) [source: https://raw.githubusercontent.com/astral-sh/ruff-vscode/main/README.md]; `MS-CEINTL.vscode-language-pack-zh-hans` [source: https://marketplace.visualstudio.com/items?itemName=MS-CEINTL.vscode-language-pack-zh-hans].
- **Chinese UI:** Command Palette > "Configure Display Language"; locale code `zh-cn`; restart required [source: https://code.visualstudio.com/docs/configure/locales]. Recommendation: keep the UI in English and give Chinese glosses in lessons, because command names, docs and error searches are English; offer the language pack as an opt-in.
- **Shortcuts that matter (macOS)** [source: https://code.visualstudio.com/docs/reference/default-keybindings]: ⇧⌘P Command Palette, ⌘P Quick Open, ⌘B sidebar, ⌃` terminal, ⌘S save, ⌘, settings, ⇧⌘E Explorer, ⇧⌘F search in files, ⌃⇧G Source Control, ⇧⌘X Extensions, ⌘F find, ⌘/ comment, ⌥↑/⌥↓ move line, ⇧⌥F format document, ⌘D next match, ⌃G go to line, ⌘W close editor, ⇧⌘V Markdown preview, ⌘K ⌘S shortcut list.
- **Unicode highlighting (useful for Chinese typists).** In code files VS Code boxes characters that look like ASCII. From the build's table, with English or Chinese UI alike (the table key is `zh-hans`, the UI locale is `zh-cn`, so the Chinese exemption does not apply by default): flagged `（ ） ， ： ； ！ ？ ‘ ’`; full-width space U+3000 flagged as invisible; **not flagged** `“ ” 。 、 《 》 【 】 —`. Strings are checked, comments are not in a trusted workspace; Markdown and plain text are exempt [local, bundle data; not seen on screen].

**Config files validated here** (keys exist in this build; JSON parses) [local]:
```jsonc
// .vscode/settings.json
{
  "files.autoSave": "onFocusChange",
  "files.eol": "\n",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true,
  "[markdown]": { "files.trimTrailingWhitespace": false },
  "editor.renderWhitespace": "boundary",
  "workbench.editor.enablePreview": false,
  "chat.disableAIFeatures": true,
  "python.analysis.typeCheckingMode": "standard"
}
// .vscode/extensions.json
{ "recommendations": ["editorconfig.editorconfig", "davidanson.vscode-markdownlint", "ms-python.python", "charliermarsh.ruff"] }
```
```ini
# .editorconfig
root = true
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4
[*.md]
trim_trailing_whitespace = false
```
`chat.disableAIFeatures` "disable[s] and hide[s] built-in AI features provided by GitHub Copilot, including chat and inline suggestions" [local, setting description]. Whether it affects the separately installed Claude Code extension was not tested.

---

## 5. The iCloud-synced Desktop

### 5.1 Why code should not live there
- Git's own FAQ: "It is important not to use a cloud syncing service to sync any portion of a Git repository, since this can cause corruption, such as missing objects, changed or added files, broken refs" because such services "sync file by file on a continuous basis and don't understand the structure of a Git repository" [source: https://git-scm.com/docs/gitfaq].
- Dataless files: since macOS Sonoma iCloud Drive keeps evicted files as metadata-only placeholders; content is fetched on access ("materialization"), which can be slow or fail with time-outs (`ETIMEDOUT`); the flag is `SF_DATALESS` [source: https://developer.apple.com/tutorials/data/documentation/technotes/tn3150-getting-ready-for-data-less-files.json]. With "Optimize Mac Storage" on, "your Mac can automatically store documents in iCloud when more space is needed" [source: https://support.apple.com/guide/mac-help/store-files-in-icloud-drive-mchle5a61431/mac]. Evicted files "exist there as a dataless file"; with Optimise Mac Storage off, local copies stay in sync and keep their data [source: https://eclecticlight.co/2026/08/25/an-icloud-primer/]. Older macOS used hidden `.name.icloud` stub files instead, so detection scripts from old tutorials are wrong [memory; seen only in search summaries today].
- Hidden flags: iCloud can put the BSD `hidden` flag on files inside a virtual environment in a synced folder, and Python 3.14's `site.py` skips `.pth` files with that flag ("Skipping hidden .pth file") [local]. The result is a `No module named ...` failure; `chflags -R nohidden` clears the flag, and rebuilding the environment outside the synced folder avoids it. An independent test found iCloud Drive does not preserve or sync BSD flags reliably [source: https://eclecticlight.co/2026/06/02/bsd-flags-are-incompatible-with-icloud-drive/]. Why iCloud sets the flag was not established.
- Volume: one Python environment can hold 15,000 to 24,000 files; a user reported 15-20 hours repairing Google Drive sync, and the consensus advice was to keep environments out of synced folders [source: https://discuss.python.org/t/venvs-silently-install-25-000-files-a-real-problem-for-users-on-google-drive/106492].
- Conflict copies (`name 2`) inside `.git`: only community reports were found (for example an Apple Developer Forums thread whose accepted answer is "Don't keep Xcode projects in any kind of synced location. Just use git.") [source: https://developer.apple.com/forums/thread/123145].
- `.nosync`: "iCloud won't sync items with the extensions .nosync or .tmp", applied to folder names; there is no exclusion list in System Settings [source: https://eclecticlight.co/2026/01/06/exclude-or-include-items-in-backup-search-icloud-drive-and-quicklook-preview/]. I found no Apple documentation for it, and no public report shows that it keeps the hidden flag away, so treat it as a workaround, not a home for code.
- A side benefit of leaving Desktop: Desktop, Documents and Downloads are privacy-protected, so each terminal app needs permission (System Settings > Privacy & Security > Files & Folders) [source: https://support.apple.com/guide/mac-help/control-access-to-files-and-folders-on-mac-mchld5a35146/mac]; `~/Developer` is not in that list.

### 5.2 `~/Developer`
Not synced by Desktop & Documents (only those two folders are) [source: https://support.apple.com/en-us/109344]. The system ships a dedicated icon, `CoreTypes.bundle/.../DeveloperFolderIcon.icns` [local]; that Finder applies it to `~/Developer` is a community report, not seen here [memory]. The folder name is not localized (Desktop/Documents/Downloads show as 桌面/文稿/下载 in a Chinese UI but are English on disk) [local].

### 5.3 Do not "fix" it by switching the feature off
Turning off Desktop & Documents Folders leaves existing files in iCloud Drive and creates new *empty* local Desktop and Documents folders; files must be dragged back by hand [source: https://support.apple.com/en-us/126628]. Path: System Settings > [your name] > iCloud > Drive. A beginner would see an empty Desktop.

### 5.4 Checks that work on this Mac [local]
```
% xattr ~/Desktop
com.apple.file-provider-domain-id          <- present = the folder is managed by a sync provider
% xattr -p com.apple.file-provider-domain-id ~/Desktop
com.apple.CloudDocs.iCloudDriveFileProvider/<UUID>
% find <old-location> -flags +dataless | wc -l      -> 0 means every file's content is on this Mac
% find <folder> -flags +hidden | wc -l               -> items carrying the hidden flag
```
- `find -flags +dataless` and `ls -lO` were validated against a real dataless folder elsewhere on this Mac (`ls -ldO` shows `compressed,dataless`; `stat -f %Sf` the same; Python `st_flags & stat.SF_DATALESS` true). No dataless *file* existed to test with.
- Two standard-library scripts were written and run: `check_dataless.py` (counts dataless items with `os.lstat`) and `detect_sync.py` (walks up parents looking for the attribute above; reports `SYNCED` for anything under Desktop or Documents and `LOCAL` for Downloads, home and the scratch folder). `os.listxattr` does not exist in Python on macOS, so the script calls `/usr/bin/xattr`. Both are in my scratch directory and can seed `tools/check.py`.
- If something is cloud-only: Finder, Control-click, "Download Now"; "Keep Downloaded" pins it [source: https://support.apple.com/guide/mac-help/work-with-folders-and-files-in-icloud-drive-mchl1a02d711/27/mac/27]. `brctl download <path>` is in `man brctl` but could not be run.

### 5.5 Relocation runbook, rehearsed end to end against a fake home folder [local]
```
% find <old-location>/Engineering -flags +dataless | wc -l      -> must print 0
% find <old-location>/Engineering | wc -l                        -> note the number
% mkdir -p ~/Developer
% cp -R <old-location>/Engineering ~/Developer/                  (no slash after Engineering)
% find ~/Developer/Engineering | wc -l                           -> same number
% diff -rq <old-location>/Engineering ~/Developer/Engineering && echo "两边内容完全一样"
% find ~/Developer/Engineering -flags +hidden | wc -l            -> 0
% cd ~/Developer/Engineering && pwd
```
What the rehearsal and side tests showed:
- Plain `cp -R` does **not** carry the `hidden` flag; `mv`, `cp -Rp`, `cp -a` and `ditto` do; `rsync -a` does not. After a move (Terminal `mv` or a Finder drag), run `chflags -R nohidden <folder>` [local]. This is the main reason to copy rather than move.
- Running the `cp -R` line twice does not nest folders; `mkdir` twice prints `File exists`, `mkdir -p` is silent [local].
- `diff -rq` prints "Directory loop detected" when a symlink points to a folder; exclude environments with `-x .venv -x node_modules` [local].
- **Virtual environments do not survive a move.** After moving a test project: console scripts fail (`.venv/bin/cowsay: ... old-place/proj/.venv/bin/python: No such file or directory`) and `source .venv/bin/activate` silently points at the old path, so `which python` shows the global Python. Recreating the environment fixes it [local]. Rule: never copy `.venv`/`node_modules`; rebuild them (`uv sync`, `npm install`).
- A Git repository does survive `mv` (status and log intact) [local].
- A Finder drag out of a synced folder is a move: items are "copied to your Mac and removed from iCloud Drive on all your devices" [source: same Apple page as above].
- Suggested order for a beginner: check, copy, verify, switch all tools to the new folder, mark the old folder as retired (rename it), and put it in the Trash only after the stage is passed.

---

## 6. First-week stumbling blocks for a Chinese-speaking beginner

Real messages from this machine [local]:
```
% ls　-l          (full-width space)    zsh: command not found: ls　-l
% ls －l          (full-width hyphen)   ls: －l: No such file or directory
% cd ～                                 cd: no such file or directory: ～
% cat f.txt ｜ grep apple               cat: ｜: No such file or directory
% echo one；echo two                    one；echo two          (no error, wrong result)
% git commit -am “second try”           fatal: paths 'try” ...' with -a does not make sense   (curly quotes do not quote)
% git commit -am "docs：全角冒号"         accepted silently; log shows  f99194e docs：全角冒号
print（"hello"）      SyntaxError: invalid character '（' (U+FF08)
print(“hello”)        SyntaxError: invalid character '“' (U+201C)
if x == 1：           SyntaxError: invalid character '：' (U+FF1A)
["a"，"b"]            SyntaxError: invalid character '，' (U+FF0C)
　　print("x")        SyntaxError: invalid non-printable character U+3000
print("你好，世界！")  works: full-width punctuation inside a string is fine
```
Fixes:
- **Switch input source with Caps Lock.** System Settings > Keyboard > Text Input > Edit: "Use the Caps Lock key to switch to and from [last used Latin input source]"; also "Automatically switch to a document's input source" [source: https://support.apple.com/guide/mac-help/change-input-sources-settings-mchl84525d76/mac]. Habit: look at the menu-bar input indicator before typing a command.
- Pinyin has "Use halfwidth punctuation: Automatically use half-width punctuation marks whenever possible" (shortcut Option-Shift-H) [source: https://support.apple.com/guide/chinese-input-method/change-chinese-and-cantonese-settings-cim21aa5fa50/mac]. It degrades Chinese prose, so offer it as optional; the Caps Lock habit is the real fix.
- "Use smart quotes and dashes" (same settings pane) turns `"` into curly quotes in apps such as Notes, Pages, Mail [source: same Apple page]. Rule: never draft commands or code in those apps or in chat apps; copy from the lesson or type in the terminal/VS Code.
- Common Pinyin-mode slips: `\` gives `、`, `` ` `` gives `·`, Shift-4 gives `¥`, Shift-6 gives `……`, `[` gives `【` [memory].
- Control-Space is commonly the input-source shortcut on a Mac with a Chinese input source [local] ("Select the previous or next input source" [source: https://support.apple.com/en-us/102650]); tutorials that say "press Ctrl+Space for suggestions" will confuse. Suggestions appear automatically anyway.
- Chinese file names work in zsh, but `git status` prints them as `"\345\255\246..."` unless `core.quotepath=false` [local]. Keep file and folder names in lowercase English with hyphens; content in Chinese.
- A full-width colon in a commit prefix (`docs：...`) is a likely slip with the planned "English type + Chinese description" convention, and Git accepts it without complaint (transcript above); have the checker test for it.
- Typing: 10-15 minutes a day on symbols and digits (`~ | \ / $ & * # - _ { } [ ]`) matters more than speed [memory].
- Reading English errors: teach the shape `program: what it tried: what went wrong`, read the last line of a Python traceback first, and keep section 3.14 as a bilingual glossary. Every message there is real.

---

## 7. Markdown and README

- Specs: CommonMark 0.31.2 (2024-01-28) is current [source: https://spec.commonmark.org/]; the GFM spec is 0.29-gfm (2019) and adds tables, task lists, strikethrough, autolinks, disallowed raw HTML [source: https://github.github.com/gfm/]. GitHub features added since (alerts, footnotes, Mermaid) are documented only in GitHub Docs. VS Code "targets the CommonMark Markdown specification using the markdown-it library" [source: https://code.visualstudio.com/docs/languages/markdown].
- **Rendering test** of one sample file: GitHub's Markdown API, and markdown-it 15.0.3 with `html: true` (the option VS Code's bundled engine sets) [local]:

| Feature | GitHub | VS Code built-in preview (inferred from engine + bundle) |
|---|---|---|
| Headings, emphasis, code, links, tables, `~~strike~~` | yes | yes |
| `<details><summary>` with Markdown inside | yes | yes (HTML passes through; needs blank lines around inner Markdown) |
| Task lists `- [ ]` | checkboxes | literal `[ ]` text (no checkbox code in the bundle) |
| Alerts `> [!NOTE]` | styled box | ordinary blockquote showing `[!NOTE]` |
| Footnotes `[^1]` | yes | no |
| Mermaid | yes, in issues, pull requests, discussions, wikis and Markdown files [source: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams] | yes (built-in extension `mermaid-markdown-features`) |
| Math | yes [memory] | yes (built-in extension `markdown-math`, KaTeX) |
| Single newline inside a paragraph | same paragraph in `.md` files; `<br>` in issues/comments | same paragraph (`markdown.preview.breaks` false) |

- GitHub's own `<details>` example leaves a blank line after `<details>`, after `</summary>` and before `</details>`; `<details open>` starts expanded [source: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections]. Line breaks in `.md` files need two trailing spaces, a backslash or `<br/>` [source: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax].
- **markdownlint flags the hints.** markdownlint-cli2 0.24.1 on a sample lesson: `MD033/no-inline-html Inline HTML [Element: details]` (also `summary`, `kbd`). With `.markdownlint.jsonc` = `{ "MD013": false, "MD033": { "allowed_elements": ["details", "summary", "kbd", "br"] } }` it reports 0 issues [local].
- Essentials to teach, in order: paragraphs and blank lines, `#` headings, emphasis, lists (and the blank line before a list), links and relative links, inline code and fenced code blocks with a language name, blockquotes, images, tables, then task lists and `<details>` as GitHub-flavoured extras [memory for the ordering].
- README conventions: say what the project does, why it is useful, how to get started, where to get help, who maintains it; GitHub shows a README from `.github`, then the root, then `docs`; relative links are preferred; content beyond 500 KiB is cut [source: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes].

---

## 8. What changed compared with older tutorials

The "Today" column is backed by the sections above unless tagged; the "Older advice" column is from memory.

| Older advice | Today |
|---|---|
| Put shell settings in `~/.bash_profile` | zsh is the default since macOS 10.15: `~/.zshrc` / `~/.zprofile` |
| `echo "Hello, World!"` as the first command | Gives `dquote>` in zsh; use single quotes |
| `brew install trash` | `/usr/bin/trash` is built in since macOS 15 |
| Homebrew = "missing package manager for macOS", any macOS | "The Package Manager for Everywhere"; macOS 15+; `.pkg` installer exists |
| `pip install ...` | `pip` absent, `pip3` is the system Python 3.9's; use uv |
| iCloud placeholders are `.name.icloud` files | APFS dataless files with a flag |
| System Preferences > Apple ID > iCloud | System Settings > [your name] > iCloud > Drive |
| Desktop/Documents appear under "iCloud" in the Finder sidebar | From macOS 26 they appear under Favorites with a cloud icon [source: https://support.apple.com/en-us/109344] |
| VS Code monthly releases, modal "Do you trust the authors" dialog | Weekly releases; Restricted Mode banner by default |
| "Shell Command: Install 'code' command in PATH" | Now "... 'code' and optionally 'copilot' commands in PATH" |
| Mermaid in preview needs an extension | Built in |
| VS Code tutorial = edit a file by hand | Official tutorial is agent-driven; AI features can be disabled per workspace |
| Separate Black, isort, Flake8 extensions | One Ruff extension (format, fix and organize imports on save) [source: https://raw.githubusercontent.com/astral-sh/ruff-vscode/main/README.md] |
| `git init` creates `master` | Apple's bundled config sets `init.defaultBranch = main` [local] |
| Missing Semester 2020 | The 2026 edition has nine lectures, adds "Agentic Coding", and still starts with the shell [source: https://missing.csail.mit.edu/] |

---

## 9. Recommendations for the course

**Teach first (stage 0):** what a terminal is and how to leave anything (Control-C, `q`, `exit`); prompt anatomy; `pwd`, `ls`, `cd`, `cd ..`, `cd ~`, Tab, Up arrow, Command-K; "copy the command, not the prompt symbol"; quotes around names with spaces; the input-source check before typing.
**Then (stage 1):** `mkdir -p`, `touch`, `cp -R`, `mv -i`, Trash before `rm`; `cat`/`less`/`head`/`tail`; `grep` and `find` with quoted patterns; `|`, `>`, `>>`; then PATH, `which -a`, `export`, start-up files (read first, edit one alias in a `ZDOTDIR` practice shell, back up before touching the real file); `chmod +x` only when the first script appears.
**Postpone:** `sudo` beyond awareness, numeric chmod, `ps`/`kill` details, `find -exec`, `xargs`, `sed`/`awk`, regular expressions, vim beyond quitting, Homebrew installs until a lesson needs one, nvm until stage 4, ripgrep, Warp features.

**Defaults:**
1. Reference terminal for stages 0-1: Apple Terminal (documented by Apple for macOS 27, no account, no AI). From lesson 1.4 also the VS Code terminal. Warp optional; if used, switch off "Autodetect agent prompts in terminal input" (Settings > Agents > Warp Agent > Input), which is on for new users and sends natural-language-looking input to an agent [source: https://docs.warp.dev/agents/local-agents/interacting-with-agents/terminal-and-agent-modes/].
2. Show commands without a prompt character in copyable blocks; show expected output separately; never put a `# comment` on a command line meant for pasting.
3. Ship `.editorconfig`, `.vscode/settings.json`, `.vscode/extensions.json`, `.markdownlint.jsonc` as in sections 4 and 7.
4. Lesson files: lowercase English names with hyphens; hints in `<details>` with blank lines inside.
5. Environment check (lesson 0.4) should print versions and also test: folder not under a synced location, `gpg` signing setting versus `gpg` presence, `python3` location, input source hint.
6. Git lessons: set `commit.gpgsign false` and `core.quotepath false` in the practice repositories' local config (verified), and explain the global setting when the learner is ready to decide.

**Plain-Chinese analogies (suggestions):**
- 终端：给电脑递"文字小纸条"；shell 是接纸条的服务员；提示符 `%` 是他说"请讲"。
- 路径：地址。绝对路径是从省市写起的完整地址；相对路径是"从我现在站的地方往里走"；`~` 是自己家，`..` 是上一层楼。
- PATH：电脑找命令时按顺序翻的"通讯录"，先翻到谁就用谁（所以 `python3` 和 `pip3` 可能不是一家人）。
- `rm`：碎纸机；废纸篓（`trash`、Finder 删除）还能捡回来。
- 管道 `|`：流水线；`>` 是撕掉旧页重写，`>>` 是接着往下写。
- 权限：门禁卡，读/写/执行三种权限，分给主人、同组、其他人。`sudo` 是借管理员的万能钥匙。
- iCloud 同步：一位勤快的管家，不停把你桌上每张纸拿去复印寄走；你正在装订账本（Git）时他也来抽页。`~/Developer` 是管家不进的工作间，备份交给 Git 远程仓库。
- 仅在云端的文件：书架上的"代书板"，书在仓库里，用时才调来。
- 全角/半角：长得像但尺寸不同的插头，代码只认半角。
- 编码：文字的"密码本"；乱码就是拿错了密码本。UTF-8 是全世界通用的那一本。
- 受限模式：到陌生人家里，先不乱碰东西。
- 斜体标签页：只是"翻看一下"，还没钉住。

---

## 10. Where the evidence challenges the current plan

1. **Reading lessons before lesson 1.4.** Collapsed hints are visible as plain text unless the file is viewed in a renderer. The plan teaches VS Code at 1.4 but needs rendered Markdown from 0.1. Add a five-minute "how to read these lessons" step at the very start (open the folder, trust it, ⇧⌘V), or put answers in separate files. Worth testing on screen: the workspace setting `workbench.editorAssociations` mapping lesson files to `vscode.markdown.preview.editor` (that view type exists in the build [local]; the effect is untested).
2. **Lesson 0.6 (move out of iCloud) needs more than lesson 0.5 teaches** (`mkdir`, `cp -R`, `find`, `diff`). Present it as a fully scripted walk-through with the rehearsed commands in 5.5, copy-then-verify rather than move, and a checker based on `detect_sync.py`. Include "rebuild, do not copy, virtual environments" for later use on any existing project the learner has (if any).
3. **Tutor continuity after the move.** Claude Code names its per-project data folder after the folder path (observed: one entry per absolute path under `~/.claude/projects/`) [local]. After the move the tutor starts from a different path; whether its per-project memory follows was not tested. Keep all tutor state in files inside the workspace, as the design already intends, and make "reopen in the new folder" an explicit checked step.
4. **Git lessons will fail at the first commit** unless the gpg setting is handled (section 1). Also plan for vim opening on `git commit` without `-m`, and for Chinese file names in `git status`.
5. **Lesson 1.4 cannot be a classic VS Code tour.** It has to cover Restricted Mode, where the Chat panel is and why AI is switched off in this workspace, preview-mode tabs, and auto save; and it should rely on Command Palette names because the UI changes weekly. A global Pylance `strict` setting, if the learner has one, will flood beginner code with warnings in stage 2 unless the workspace overrides it.
6. **Terminal choice.** Some learners already use Warp. For foundations, Terminal.app is the safer reference; Warp's agent auto-detection can swallow mistyped commands.
7. **"Uses only Python's built-in features" for the checker is feasible**, with one caveat found here: extended attributes need `/usr/bin/xattr` via `subprocess` because `os.listxattr` is missing on macOS.
8. **The tutor must not relay its own shell's output** (finding 4 in section 1); lesson transcripts need to come from a clean zsh, as in this brief.

---

## 11. Not verified

- Anything on screen: Finder menus and iCloud status icons, the hammer icon on `~/Developer`, VS Code's Restricted Mode banner, Chat panel position, Unicode highlight boxes, Markdown preview appearance (preview behaviour is inferred from the engine and bundle), the experimental Markdown Editor, Warp's interface.
- Interactive terminal behaviour: Tab completion, Control-R search, Control-C/Control-Z at a keyboard, `less` and `man` paging, vim.
- `ps`, `pgrep`, `sudo`, `open`, `brctl`, `fileproviderctl`, `man -k` (blocked here); `/usr/bin/trash` (not executed).
- Detection of a dataless *file* (only a dataless folder was available); how to force a download from the terminal.
- Why iCloud sets the `hidden` flag on files, and whether `.nosync` is still honoured on macOS 27 (the source describes macOS 15 and 26).
- Whether a Finder drag preserves the `hidden` flag (expected, since `mv` does).
- Whether moving something out of a synced folder places a copy in iCloud's "Recently Deleted".
- The meaning of the preference keys `com.apple.bird optimize-storage` and `com.apple.finder FXICloudDrive*` (read locally; undocumented).
- The wording of macOS privacy prompts for terminal apps, and whether Terminal, Warp and VS Code already have access to Desktop.
- Whether `chat.disableAIFeatures` affects third-party AI extensions such as Claude Code.
- Whether `workbench.editorAssociations` can open only lesson files in preview by default.
- Pinyin-mode key-to-symbol mappings; the Finder shortcut for hidden files.
- Whether Claude Code's per-project memory follows a moved folder.

## 12. Files left in the scratch directory

`check_dataless.py`, `detect_sync.py`, `rehearsal.zsh` (relocation rehearsal), `sample-workspace/` (validated `.vscode/` files and `.editorconfig`), `mdtest/` (sample Markdown, GitHub API output, markdownlint config and sample lesson), `playground/` (terminal experiments).
