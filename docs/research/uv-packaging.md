# uv-packaging brief: Python project and environment management with uv 0.13.x and pyproject.toml

Research date: 2026-11-19. Checked on the reference Mac of plan G7 (`docs/plans/2026-11-19-batch-1-plan.md`): macOS 27.2.1 arm64, zsh 5.9, uv 0.13.5 (Homebrew build 2026-10-22), git 2.54.0 (Apple Git-157).
Reader: course builders. The course itself must be written in plain Chinese.

Tags used on claims:
- **[local]** ran today in throwaway projects inside my scratch dir (not in iCloud), always with `export UV_CACHE_DIR="$TMPDIR/uv-cache"`.
- **[source: URL]** read today in a primary source. **[memory]** not verified today.

Throwaway projects (venvs deleted, skeletons and lockfiles kept) are next to this file: `init-tests/`, `flow/`, `hidden-pth/`, `symlink-test/`, `recipe/`, `anatomy/`, `wstest/`, `names/`, `movetest/`.

---

## 0. The findings that should shape the course

1. **`uv init` now makes a packaged `src/` project by default** (`[build-system]` = `uv_build`, `[project.scripts]` entry, `src/<name>/__init__.py`). Every 2024 to mid-2026 tutorial showing a root `main.py`/`hello.py` is out of date; that layout now needs `--no-package`. [local] [source: https://github.com/astral-sh/uv/releases/tag/0.12.0]
2. **The project is installed into `.venv` as an editable install implemented by one `.pth` file** (`site-packages/<module>.pth` holding the absolute path of `src`). [local]
3. **CPython skips `.pth` files that carry the macOS hidden flag, and this is not a 3.14 thing**: every CPython since 3.12.2 / 3.11.8 (Feb 2024) does it, including the 3.12.15 and 3.14.9 on this machine. Changing Python version will not help. [local] [source: https://github.com/python/cpython/issues/113659]
4. **With "Desktop & Documents" sync on, the Desktop and Documents folders are stored in iCloud Drive, and dot-items inside them can carry the hidden flag** while non-dot items do not, according to public bug reports (section 5.3). Any project folder on the Desktop sits in the same synced tree. A `.venv -> .venv.nosync` workaround rests on two public facts: iCloud does not sync `.nosync` items, and a `.venv` symlink to a non-dot directory was reported to work in uv issue 16977 (the same user later doubted it); no public report of the `.nosync` variant over time was found (section 5.5). [source: https://support.apple.com/en-us/109344] [source: https://github.com/pypa/setuptools/issues/4595] [source: https://github.com/astral-sh/uv/issues/16977]
5. **Best setup**: code outside iCloud (`~/Developer/...`) plus a Git remote. If the course must stay on an iCloud-synced Desktop, use a real `.venv.nosync` directory with a `.venv` symlink in every project; it survives `uv sync`, interpreter changes and `uv venv --clear`, but not `rm -rf .venv`. `UV_PROJECT_ENVIRONMENT` is the weaker option (see finding 6). Details in section 5.
6. **The AI assistant's shell and the learner's Terminal see different uv setups** (if `~/.zshrc` exports `UV_*` variables, tool shells do not read them). In the test of section 1 (the Terminal side simulated by setting the variable) `uv init` picked Python 3.12 in the assistant's shell and 3.14 in the Terminal. Always pass `--python 3.14` and commit `.python-version`. [local]
7. **uv 0.13.5 bug: a project name starting with a digit produces a broken package** (`uv init 01-hello` generates `from 01_hello import main`, a SyntaxError). Fixed in 0.13.7; this machine has 0.13.5. Do not name practice projects `01-...` or pass `--name`. [local] [source: https://raw.githubusercontent.com/astral-sh/uv/main/CHANGELOG.md]
8. **`pip` does not exist here and `pip3` is Xcode's Python 3.9 pip**; uv venvs contain no pip. "pip install X" from an old tutorial either fails or installs into the wrong Python. [local]
9. **`uv format`, `uv check`, `uv audit` exist in 0.13.5 but are all experimental** (each prints a warning). `uv format` downloads its own Ruff 0.15.x, not the project's Ruff 0.17.x. [local]
10. **Dev tools go in `[dependency-groups]` (PEP 735), not `[project.optional-dependencies]` and not `[tool.uv] dev-dependencies`.** `uv sync` is exact: it uninstalls anything not selected. [local]
11. **A venv is not relocatable**: after moving or renaming a project folder, console scripts such as `pytest` break until `uv sync --reinstall` (or delete the env and sync). Relevant to any "move the project out of iCloud" step. [local]
12. **Cross-topic machine facts** found on the way: `git init` here yields branch `main` (set by Xcode's system gitconfig); a global `commit.gpgsign=true` with no `gpg` binary on PATH makes `git commit` fail; nested `uv init` inside a folder that has a `pyproject.toml` automatically turns the parent into a uv workspace and edits its `pyproject.toml`. [local]

---

## 1. Machine facts that matter for uv (the reference Mac of plan G7)

| Item | Value | Basis |
|---|---|---|
| uv | 0.13.5; newest on PyPI is 0.13.9 (2026-11-17). Homebrew build, so `uv self update` refuses: "run `brew update && brew upgrade uv`" | [local], [source: https://pypi.org/pypi/uv/json] |
| Pythons | 3.14.9 in a custom `UV_PYTHON_INSTALL_DIR` (its `python3` link on PATH), 3.12.15 in `~/.local/share/uv/python` (uv's default), 3.9.6 at `/usr/bin/python3` (Xcode) | [local] |
| uv-managed Python is marked externally managed | `<managed-python-dir>/cpython-3.14.9-.../lib/python3.14/EXTERNALLY-MANAGED` says "This Python installation is managed by uv and should not be modified.", so a global `python3 -m pip install` is refused under PEP 668 | marker file read [local]; the refusal itself was not executed |
| pip | `pip`: not found. `pip3` = `/usr/bin/pip3` = pip 21.2.4 for Python 3.9. Inside a uv venv: `python -m pip` gives "No module named pip" | [local] |
| Newest tool versions today | ruff 0.17.5, pytest 9.2.0, mypy 2.4.1, ty 0.0.107 (still 0.0.x), numpy 2.5.5 | [local] via PyPI JSON |
| Python download host | `uv python install` fetches from `https://releases.astral.sh/github/python-build-standalone/...` (24 MiB, 3 s). Older notes say github.com | [local] |
| Latest stable Python | 3.15.x (uv 0.13.5 lists 3.15.1; the 0.13.6 changelog adds 3.15.2 and 3.14.10). uv 0.13.0 changed its default for fresh downloads from 3.14 to 3.15, but an installed compatible interpreter is used first | [local] `uv python list`, [source: https://github.com/astral-sh/uv/releases/tag/0.13.0] |

### Different "views" of uv on one machine [local]

If `~/.zshrc` exports `UV_CACHE_DIR`, `UV_PYTHON_INSTALL_DIR`, `UV_PYTHON_BIN_DIR`, `UV_TOOL_DIR`, `UV_TOOL_BIN_DIR` (for example all under one custom folder), an assistant's tool shell that is a non-interactive login zsh can have the custom bin dir on PATH but none of those variables. An assistant shell without the sandbox would presumably look like the right-hand column but with writable `~/.cache/uv` and `~/.local/share/uv` (inferred, not observed).

| | Interactive Terminal (custom `UV_*` exports) | Assistant tool shell (as observed here, sandboxed) |
|---|---|---|
| Managed-Python dir | custom `UV_PYTHON_INSTALL_DIR` (3.14.9) | `~/.local/share/uv/python` (3.12.15) |
| `uv python find` outside a project | 3.14 (simulated by setting the variable) | 3.12 |
| `uv init x` without `--python` | `.python-version` 3.14, `requires-python >=3.14` (simulated) | `.python-version` 3.12, `requires-python >=3.12` |
| Cache | custom `UV_CACHE_DIR` | default `~/.cache/uv` is not writable in the sandbox, hence `$TMPDIR/uv-cache` |
| Tool dir | custom `UV_TOOL_DIR` (ruff 0.17.2 lives here) | `~/.local/share/uv/tools`, not writable: `uvx` fails with "failed to create directory ... Operation not permitted" unless `UV_TOOL_DIR` is redirected |

With a pinned `.python-version` of 3.14 both views pick the same interpreter and neither recreates the environment (`uv sync --dry-run` says "Would make no changes" in both). [local]

---

## 2. `uv init` today (uv 0.13.5) [local]

`uv init demo-fx` prints one line and creates:

```
demo-fx/
├── .git/                 (git init, branch main, no commit yet)
├── .gitignore
├── .python-version       ("3.12" here; minor version only)
├── README.md             (empty, 0 bytes)
├── pyproject.toml
└── src/demo_fx/__init__.py
```

```toml
[project]
name = "demo-fx"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "<git user.name>", email = "<git user.email>" }
]
requires-python = ">=3.12"
dependencies = []

[project.scripts]
demo-fx = "demo_fx:main"

[build-system]
requires = ["uv_build>=0.13.5,<0.14.0"]
build-backend = "uv_build"
```

`.gitignore` written by uv: `__pycache__/`, `*.py[oc]`, `build/`, `dist/`, `wheels/`, `*.egg-info`, `.venv` (no trailing slash). It has no `.DS_Store`, `.env`, `.ipynb_checkpoints/`.
`src/demo_fx/__init__.py` contains `def main() -> None: print("Hello from demo-fx!")`.
`.venv` and `uv.lock` do not exist yet; the first `uv run` / `uv sync` / `uv lock` creates them.

| Command | Result |
|---|---|
| `uv init x` = `--app` = `--package` | as above ("This is the default behavior" in `uv help init`) |
| `uv init --no-package x` | flat: `main.py` with `if __name__ == "__main__"`, no `[build-system]`, no `authors`, no `[project.scripts]`; the project itself is not installed. Run with `uv run main.py` |
| `uv init --lib x` | `src/x/__init__.py` (`def hello() -> str`) plus `src/x/py.typed`; no `[project.scripts]` |
| `uv init --bare x` | only a 4-field `pyproject.toml`; no git, README, `.python-version`, `src/` |
| `uv init --script f.py` | single file with a PEP 723 header (`# /// script`, `requires-python`, `dependencies = []`) |
| `--build-backend hatch` | `requires = ["hatchling"]`, `build-backend = "hatchling.build"`. Choices: uv, hatch, flit, pdm, poetry, setuptools, maturin, scikit |
| `--vcs none` | no `.git` and also no `.gitignore` |
| inside an existing Git repo | no nested `.git` and no `.gitignore` is written |
| folder already has `pyproject.toml` | `error: Project is already initialized in ... (pyproject.toml file exists)`, exit 2 |
| folder has other files but no `pyproject.toml` | works; an existing `README.md` is kept |
| `--author-from none` | omits `authors` (default copies name and e-mail from git config into a file that gets committed and into wheel metadata) |

Naming [local]: `Engineering` becomes `engineering`; `My Project` becomes `my-project` / module `my_project`; `data.tools` becomes `data-tools`; a Chinese folder name fails with "is not a valid package name. Please provide a package name with `--name`" (`uv init --name fx-practice 汇率练习2` works). `01-hello` is accepted but broken on 0.13.5 (finding 7).

Nested init [local]: running `uv init child` inside a folder whose ancestor has a `pyproject.toml` prints "Adding `child` as member of workspace ..." and appends `[tool.uv.workspace] members = ["child"]` to the parent file; the child then shares the parent's `.venv` and `uv.lock` and gets no `.python-version`. `uv init --no-workspace child` makes it standalone. Consequence: keep the course root free of `pyproject.toml`, or always pass `--no-workspace`.

How to run the generated project [local]: `uv run demo-fx` works. `uv run python -m demo_fx` fails ("No module named demo_fx.__main__"), `uv run main.py` fails (no such file), `uv run src/demo_fx/__init__.py` prints nothing.

---

## 3. Daily commands, verified [local]

### Adding and removing

```
$ uv add numpy                    ->  dependencies = ["numpy>=2.5.5"]
$ uv add 'rich>=13'               ->  constraint kept as typed
$ uv add --dev pytest             ->  [dependency-groups] dev = ["pytest>=9.2.0"]
$ uv add --group lint ruff        ->  [dependency-groups] lint = ["ruff>=0.17.5"]
$ uv add --optional plot tabulate ->  [project.optional-dependencies] plot = ["tabulate>=0.10.0"]
$ uv add -r requirements.txt      ->  imports an old requirements file (pins are preserved)
$ uv remove rich
$ uv remove pytest
error: The dependency `pytest` could not be found in `project.dependencies`
hint: `pytest` is in the `dev` group (try: `uv remove pytest --group dev`)
```

- Default bound is a lower bound `>=current`. `uv add --bounds major rich` writes `rich>=15.0.0,<16.0.0` (values: lower, major, minor, exact).
- Every `uv add`/`uv remove` re-locks and re-syncs, so `pyproject.toml`, `uv.lock` and `.venv` change together.
- `uv remove --group lint ruff` leaves an empty `lint = []` behind.
- Outside a project: `error: No pyproject.toml found in current directory or any parent directory`.

### Groups versus extras

| | `[dependency-groups]` (PEP 735, Final 2024-10) | `[project.optional-dependencies]` (extras) |
|---|---|---|
| For | the people working on the project: tests, lint, notebooks | optional features for users of the package |
| Published in wheel metadata | no (verified: built METADATA has no trace of `dev`) | yes (`Provides-Extra: plot`, `Requires-Dist: ...; extra == 'plot'`) |
| uv flags | `--dev`, `--group`, `--only-group`, `--no-group`, `--all-groups`, `--no-default-groups` | `--extra`, `--all-extras` |
| Installed by plain `uv sync` | only `dev` (changeable with `[tool.uv] default-groups = [...]` or `"all"`) | none |

Groups can include each other: `dev = [{ include-group = "test" }, { include-group = "lint" }]` (validated in `anatomy/fxlab`). [source: https://peps.python.org/pep-0735/] [source: https://docs.astral.sh/uv/concepts/projects/dependencies/]

### `uv sync` is exact, `uv run` is not

```
$ uv add --group lint ruff          (installs ruff)
$ uv sync                           ->  - ruff==0.17.5   - tabulate==0.10.0   (non-default group and extra removed)
$ uv sync --all-groups              ->  + ruff
$ uv sync --all-groups --all-extras ->  + tabulate
$ uv sync --no-dev                  ->  removes pytest and friends
$ uv sync --only-group lint         ->  removes everything except ruff, including the project itself
$ uv pip install six ; uv run python -c "import six"   -> still works (uv run does not remove stray packages)
$ uv sync                           ->  - six==1.17.0
```

Status line when nothing changes is now "Checked N packages" (older output said "Audited"). `uv sync --inexact` keeps strays. `uv sync --check` exits non-zero with "The environment is outdated; run `uv sync` to update the environment".

### Lockfile checks and upgrades

```
$ uv lock --check          (pyproject edited by hand, lock stale)
error: The lockfile at `uv.lock` needs to be updated, but `--check` was provided.   exit 1
$ uv sync --locked         same error with `--locked`; nothing is changed (use in CI)
$ uv sync --frozen         installs from the lock as-is without checking it
$ uv tree --outdated       └── six v1.16.0 (latest: v1.17.0)
$ uv lock --upgrade-package six     Updated six v1.16.0 -> v1.17.0
$ uv lock --upgrade                 upgrades everything within the declared constraints
```

A new upstream release never makes the lock stale; only a changed `pyproject.toml` does. Loosening `six==1.16.0` to `six>=1.16` keeps 1.16.0 locked until an explicit upgrade. [local] [source: https://docs.astral.sh/uv/concepts/projects/sync/]

### `uv run`, `uv tree`, `uvx`, tools

- `uv run <cmd>` locks, syncs, then runs; works from any subdirectory. `uv run --with tabulate python ...` adds a package for one command without touching the project. `uv run --no-sync` skips the check.
- `uv run script.py` honours PEP 723 inline metadata; `uv add --script script.py rich` edits the header; `uv lock --script` writes `script.py.lock`.
- `uv tree` shows the graph with `(group: dev)` and `(extra: plot)` annotations; `--depth 1`, `--outdated`.
- `uvx pycowsay hi` and `uvx ruff@0.15.0 --version` run a tool in a throwaway environment; `uvx --from httpie http --version` when command and package names differ. `uv tool install` creates one isolated venv per tool under the tool dir and a symlink in the bin dir, and warns if that dir is not on PATH. Subcommands: run, install, upgrade, list, audit, uninstall, update-shell, dir.

### Python versions

```
$ uv python pin            -> prints the current pin
$ uv python pin 3.14       -> Updated `.python-version` from `3.12` -> `3.14`
$ uv sync                  -> Removed virtual environment at: .venv / Creating virtual environment at: .venv
$ uv python pin 3.11       -> error: The requested Python version `3.11` is incompatible with the project `requires-python` value of `>=3.12`.
$ uv python pin 3.13       -> accepted although 3.13 is not installed; the next sync downloads it
                              (or fails with --no-python-downloads)
```

`requires-python` is the promise about which versions the code supports (it also limits dependency resolution); `.python-version` is the version this checkout uses. `uv python` subcommands: list, install, upgrade, find, pin, dir, uninstall, update-shell. uv prefers managed interpreters over PATH ones (`python-preference = "managed"`), and installed ones over downloads. [local] [source: https://docs.astral.sh/uv/concepts/python-versions/]

### Version, build, export

```
$ uv version                      demo-fx 0.1.0        (--short, --output-format json)
$ uv version --bump patch --dry-run    demo-fx 0.1.0 => 0.1.1
$ uv version --bump minor              0.1.0 => 0.2.0     (edits pyproject.toml, re-locks, re-syncs)
$ uv version 0.3.0
$ uv version --bump minor --bump alpha --dry-run   0.3.0 => 0.4.0a1
$ uv build
Successfully built dist/demo_fx-0.3.0.tar.gz
Successfully built dist/demo_fx-0.3.0-py3-none-any.whl      (dist/ gets its own .gitignore)
```

- uv's own version is `uv --version` or `uv self version`. `uv version` meant uv's version before 0.7.0 (2025-04-29). [source: https://github.com/astral-sh/uv/releases/tag/0.7.0]
- The wheel holds `demo_fx/`, `entry_points.txt`, `METADATA` with `Requires-Dist`. The sdist holds a normalised `pyproject.toml` plus `pyproject.toml.orig`.
- `uv_build` rejects `dynamic = ["version"]` ("Invalid metadata format"), and `uv version` says "We cannot get or set dynamic project versions". The single source of truth is `version = "..."` in `pyproject.toml`; code reads it with `importlib.metadata.version("demo-fx")`, which follows `uv version --bump` immediately (verified).
- `uv export` formats: `requirements.txt` (default, with hashes and `-e .`), `pylock.toml` (PEP 751), `cyclonedx1.5` (experimental). `uv export --no-hashes --no-dev --no-emit-project` gives a plain list.

### `uv pip`: what is left for it

Subcommands: compile, sync, install, uninstall, freeze, list, show, tree, check. In a uv project it is useful for looking (`uv pip list`, `uv pip show`, `uv pip check`) and for old requirements-style projects (`uv venv` then `uv pip install -r requirements.txt`). The docs say not to modify the project environment with it; anything installed that way disappears at the next `uv sync` (verified). It targets `VIRTUAL_ENV` if set, otherwise the `.venv` it finds. [local] [source: https://docs.astral.sh/uv/concepts/projects/layout/]

### New since most tutorials: format, check, audit [local]

```
$ uv format --check
warning: `uv format` is experimental and may change without warning. Pass `--preview-features format-command` to disable this warning.
Downloading ruff v0.15.22 (9.5MiB)
Would reformat: src/demo_fx/messy.py
$ uv check
warning: `uv check` is experimental and may change without warning. ...
Downloading ty v0.0.107 (13.3MiB)
error[invalid-explicit-return]: Return type does not match returned value ...   Found 3 diagnostics
$ uv audit
warning: `uv audit` is experimental and may change without warning. ...
Found no known vulnerabilities and no adverse project statuses in 8 packages
```

- `uv format` = `ruff format` with a Ruff that uv picks itself (default range `>=0.15,<0.16`, resolved to 0.15.22), while `uv add --dev ruff` locks 0.17.5 and the global tool is 0.17.2. Three Ruff versions can disagree. For the course use `uv run ruff format` / `uv run ruff check` so the locked version decides.
- `uv check` runs the `ty` type checker (pre-1.0). `uv audit` queries OSV (`api.osv.dev`), covers all groups and extras, has `--output-format json|sarif`, `--ignore <ID>`.
- Also present: `uv tool audit`, `uv workspace` (metadata, dir, list), `uv auth`, `uv cache size` (experimental), and a preview `uv upgrade` that is not listed in `uv help`.

---

## 4. Where the environment lives and how the project gets into it

- Default: `.venv/` next to `pyproject.toml`, created lazily. It contains its own `.gitignore` with `*` (so Git ignores it even without a project `.gitignore`), `CACHEDIR.TAG`, `pyvenv.cfg` (`uv = 0.13.5`, `prompt = <project>`), and no pip. [local]
- Editable install [local]:
  ```
  .venv/lib/python3.12/site-packages/demo_fx.pth          <- one line: /abs/path/to/demo-fx/src
  .venv/lib/python3.12/site-packages/demo_fx-0.1.0.dist-info/   (direct_url.json: "editable": true)
  .venv/bin/demo-fx                                        <- shebang with the absolute path of .venv/bin/python
  ```
  At startup `site.py` reads every `*.pth` in site-packages and appends the listed directories to `sys.path`. Edits under `src/` are visible immediately, no reinstall. `uv sync --no-editable` copies the package instead (no `.pth`).
- Project commands ignore an activated foreign environment [local]:
  `warning: VIRTUAL_ENV=/x/other does not match the project environment path .venv and will be ignored; use --active to target the active environment instead`
- `UV_PROJECT_ENVIRONMENT` [local]: a relative value is resolved against the project root (`UV_PROJECT_ENVIRONMENT=.venv.nosync uv sync` creates `.venv.nosync`); an absolute value is used as-is. Run uv once without the variable and it silently creates a second environment at `.venv`. There is no `pyproject.toml` / `uv.toml` key for the environment path. [source: https://docs.astral.sh/uv/concepts/projects/config/] [source: https://docs.astral.sh/uv/reference/settings/]
- Moving a project folder [local]: `.venv/bin/proj-a` fails ("cannot execute: No such file or directory"), `import proj_a` fails (stale `.pth`). `uv run proj-a` repairs the project's own entry, but `uv run pytest` still fails on the stale shebang of a third-party script while `uv run python -m pytest` works. Fix: `uv sync --reinstall`, or delete the environment and `uv sync`.
- Activation (`source .venv/bin/activate`) still works but is unnecessary with `uv run`. Do not teach it first.
- Jupyter: `uv add --dev ipykernel`, then `uv run --with jupyter jupyter lab`, or select `.venv/bin/python` in VS Code. Inside notebooks use `!uv add pkg`, not `%pip`. [source: https://docs.astral.sh/uv/guides/integration/jupyter/]

---

## 5. The iCloud problem

### 5.1 The CPython rule [local] [source]

`site.py` in the local 3.14.9 and 3.12.15 (identical logic):

```python
names = [name for name in names if name.endswith(".pth") and not name.startswith(".")]
...
st = os.lstat(fullname)
if ((getattr(st, 'st_flags', 0) & stat.UF_HIDDEN) or
    (getattr(st, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_HIDDEN)):
    _trace(f"Skipping hidden .pth file: {fullname!r}")
    return
```

- Origin: python/cpython issue 113659 "Security risk of hidden pth files" (opened 2024-01-02; fix merged to main 2024-01-16; backport PRs for 3.12, 3.11, 3.10, 3.9, 3.8). Changelog of 3.12.2 (2024-02-06), section Security: "Skip `.pth` files with names starting with a dot or hidden file attribute." [source: https://github.com/python/cpython/issues/113659] [source: https://docs.python.org/release/3.12.2/whatsnew/changelog.html]
- Tag check today on raw.githubusercontent.com: `Lib/site.py` has no hidden check at v3.12.1 and v3.11.7, and has it at v3.12.2, v3.11.8, v3.10.14, v3.9.19, v3.8.19, v3.13.0, branch 3.15 and main (where it also covers the new `.start` files). [local]
- Xcode's Python 3.9.6 has no such check. The `site` documentation page does not mention the rule at all. [local] [source: https://docs.python.org/3/library/site.html]
- Only the `.pth` file's own flag counts: with `chflags hidden` on `.venv` or `site-packages` alone the import still works. [local]

### 5.2 Reproduction outside iCloud [local]

```
$ chflags hidden .venv/lib/python3.14/site-packages/hp314.pth
$ .venv/bin/python -c "import hp314"      -> ModuleNotFoundError: No module named 'hp314'
$ .venv/bin/python -v -c pass 2>&1 | grep hidden
Skipping hidden .pth file: '.../site-packages/hp314.pth'
$ uv run python -c "import hp314"         -> same error; uv sees an installed package ("Checked 1 package") and repairs nothing
$ chflags nohidden <file>                 -> works again
$ uv sync --reinstall-package hp314       -> rewrites the .pth without the flag, works again
```

Same result with Python 3.12.15. uv itself never sets the flag (fresh environments in my scratch dir show none).

### 5.3 Who sets the flag: evidence

- With "Desktop & Documents Folders" sync on, the files in both folders are stored in iCloud Drive [source: https://support.apple.com/en-us/109344]. Apple does not document how a folder shows that it is synced. The health check in 5.6 assumes that a synced folder or one of its ancestors carries the extended attribute `com.apple.file-provider-domain-id`; no public source for that attribute was found (searched 2026-11-20), so a missing attribute means "not known to be synced", not "safe".
- The public reports below agree on one pattern: dot-items in a synced folder get the `hidden` flag, non-dot items do not. In uv issue 16977 a commenter (2026-02-21) shows `ls -lO` output with `hidden` on `.venv` and no flag on `venv`, and blames Spotlight-indexed locations rather than iCloud. Whether a `.nosync` directory and its contents stay free of the flag is not answered by any public report found (searched 2026-11-20).
- [source: https://github.com/pypa/setuptools/issues/4595] (2024-08): a project in `~/Documents` with iCloud sync got the hidden flag on the dot-folder and its contents, not on non-dot folders; maintainer: "ANY .pth file on a .venv environment would be affected and skipped."
- [source: https://github.com/astral-sh/uv/issues/16977] "Local packages can become unimportable due to skipped hidden `.pth` files": open, labelled `external`, no fix in uv. Reports say the environment works and then breaks 5 to 10 minutes later, and that `chflags -R nohidden .venv` "fixes it, re-hiding breaks it again". One user proposed `UV_PROJECT_ENVIRONMENT=venv` (a non-dot directory that iCloud still syncs) plus a `.venv` symlink, later wrote of it "I don't think it does under all conditions", and moved the project out of `~/Documents`; that variant differs from `.venv.nosync`, which iCloud does not sync. A maintainer corrects the scope to "Python 3.8+, not 3.12+".
- Apple documents none of this.

### 5.4 The `.nosync` behaviour: sources

- Apple, iCloud Design Guide (archived, updated 2015-12-17): "One way to prevent files and directories from being stored in iCloud is to add the `.nosync` extension to the file or directory name. ... it does not transfer them to the server. ... they are still bound to their parent directory. When you delete the parent directory in iCloud, or when you evict the parent directory and its contents locally, the entire contents of that directory are deleted, including any `.nosync` items." [source: https://developer.apple.com/library/archive/documentation/General/Conceptual/iCloudDesignGuide/Chapters/iCloudFundametals.html]
- Howard Oakley, 2026-01-06 and 2024-07-09: "iCloud won't sync items with the extensions `.nosync` or `.tmp`"; System Settings offers no exclusion list. [source: https://eclecticlight.co/2026/01/06/exclude-or-include-items-in-backup-search-icloud-drive-and-quicklook-preview/] [source: https://eclecticlight.co/2024/07/09/excluding-folders-and-files-from-time-machine-spotlight-and-icloud-drive/]
- Consequence: a `.nosync` folder has no cloud copy and dies with its parent. Fine for an environment (rebuild with `uv sync`), not acceptable as the only home of source code.

### 5.5 Options compared

| Option | Verdict | Why |
|---|---|---|
| A. Keep code outside iCloud, e.g. `~/Developer/<repo>`, with a Git remote | Most robust and simplest in daily use | Nothing special per project; removes the `.pth` problem, the Git-in-cloud risk (5.7) and the upload of tens of thousands of small files. Backup comes from `git push`, which the course teaches anyway. Costs: an assistant session, its sandbox write scope and its per-folder memory are tied to the folder it was opened in, so moving is a deliberate step by the learner |
| B. Stay in iCloud; real dir `.venv.nosync` plus symlink `.venv` | Best choice if the course stays on an iCloud-synced Desktop | A property of the project folder, so every shell and tool sees it. Reported to work in its parts: iCloud does not sync `.nosync` items [source: https://eclecticlight.co/2026/01/06/exclude-or-include-items-in-backup-search-icloud-drive-and-quicklook-preview/], and a `.venv` symlink to a non-dot directory was reported as a working workaround in uv issue 16977 (comment of 2026-02-21; two days later the same user wrote that it did not hold "under all conditions" and moved the project out of `~/Documents`) [source: https://github.com/astral-sh/uv/issues/16977]. No public report of the `.venv.nosync` variant over time was found (searched 2026-11-20). uv 0.13.5 follows the symlink for `uv sync`, `uv run`, interpreter changes ("Removed virtual environment at: .venv" clears the target, the link stays), `uv sync --reinstall`, `uv venv --clear` [local] |
| C. `UV_PROJECT_ENVIRONMENT=.venv.nosync` | Not recommended here | Per-shell. The assistant's shell does not read `~/.zshrc`, so it would create a second `.venv` in iCloud. No config-file equivalent. Editors and Jupyter look for `.venv`, so a symlink is needed anyway |
| D. `chflags -R nohidden .venv` | First aid only | Flags come back. `uv sync --reinstall-package <name>` has the same short-lived effect |
| E. A non-dot name such as `venv` | Worse than B | Reported to avoid the flag (not tested here, and one reporter found it unreliable), and iCloud would upload the whole environment |
| F. Preview `centralized-project-envs` (env stored in uv's cache, `.venv` becomes a link) and PEP 832 `.venv` redirect files (Draft, preview in uv 0.13.9) | Watch, do not use yet | Works on 0.13.5 via `--preview-features` or `[tool.uv] preview-features = [...]` [local]. But `uv cache prune` deleted all such environments (next sync rebuilt them), and with different cache dirs per shell the `.venv` link flips between caches [local]. [source: https://docs.astral.sh/uv/concepts/projects/layout/] [source: https://peps.python.org/pep-0832/] |

### 5.6 Recipe for option B (run verbatim today) [local]

```sh
uv init --python 3.14 myproj && cd myproj
mkdir .venv.nosync && ln -s .venv.nosync .venv        # before the first uv sync / uv run
printf '.venv.nosync/\n\n# macOS\n.DS_Store\n' >> .gitignore
uv sync && uv run myproj                               # Hello from myproj!
```

Traps, all verified [local]:
- `rm -rf .venv` deletes only the link. The next `uv sync` silently creates a real `.venv` directory and the problem can return. To rebuild an environment use `uv venv --clear && uv sync`, or `uv sync --reinstall`.
- A dangling link (target missing) stops uv: `error: failed to create directory .../.venv: File exists (os error 17)`. Fix: `mkdir .venv.nosync`.
- The link and the real directory are not in Git, so a fresh clone gets a plain `.venv`; repeat the two setup commands per checkout.
- `.gitignore` must say `.venv` without a trailing slash (uv's default does). `.venv/` does not match a symlink and Git then lists `.venv` as untracked.
- `uv venv` without `--clear` on an existing environment errors ("A virtual environment already exists ... Use the `--clear` flag").

Health check. The first three lines only read; on a healthy project that uses option B on an iCloud-synced Desktop they should report `~/Desktop` as the synced ancestor (if the attribute assumption of 5.3 holds), `.venv -> .venv.nosync`, and no hidden `.pth`. The fourth line (run in scratch) may sync the environment first:

```sh
p="$(pwd -P)"; while [ "$p" != "/" ]; do xattr "$p" 2>/dev/null | grep -q com.apple.file-provider-domain-id && echo "iCloud-synced ancestor: $p"; p="$(dirname "$p")"; done
ls -ld .venv                                         # should end with: .venv -> .venv.nosync
find -L .venv -name '*.pth' -flags +hidden           # should print nothing
uv run python -v -c pass 2>&1 | grep -i 'hidden'     # should print nothing
```

### 5.7 Git repositories inside iCloud-synced folders

- Git's own FAQ, shipped with the local git (`git help faq`, section "How do I sync a working tree across systems?"): "It is important not to use a cloud syncing service to sync any portion of a Git repository, since this can cause corruption, such as missing objects, changed or added files, broken refs, and a wide variety of other problems. These services tend to sync file by file on a continuous basis and don't understand the structure of a Git repository." [local] [source: https://git-scm.com/docs/gitfaq]
- Apple Developer Forums 123145 (2019): iCloud renamed a project's `.git` folder to a file "git 2"; accepted answer: "Don't keep Xcode projects in any kind of synced location. Just use git." No Apple staff reply. [source: https://developer.apple.com/forums/thread/123145]
- anthropics/claude-code issue 47241 (2026-04, closed by a stale bot, not confirmed by Apple or maintainers): with Desktop & Documents sync on, `fileproviderd` "silently reverts shell filesystem operations (`mv`, `rm`, `git mv`, etc.) a few seconds after they complete". [source: https://github.com/anthropics/claude-code/issues/47241]
- A single-author preprint lists lock-file propagation and numbered conflict copies such as `refs/heads/main 2`. Treat as illustration only. [source: https://arxiv.org/html/2602.19433v3]
- Apple's Mac Help for macOS 27 describes "Store in iCloud" as: "Store files from your Desktop and Documents folders in iCloud Drive" and "optimize storage by keeping only recently opened files on your Mac when space is needed", so source files can be evicted to the cloud. [source: https://support.apple.com/guide/mac-help/sysp4ee93ca4/mac] Desktop & Documents sync itself: [source: https://support.apple.com/en-us/109344]
- Whether current iCloud Drive uploads dot-items such as `.git` at all is not documented and I could not test it.

Practical reading for the course: one Mac and frequent pushes to a remote keep the risk moderate, but the professional norm is option A. Moving later is itself a good lesson: `git clone <remote> ~/Developer/<repo> && cd ... && uv sync` reproduces the project from the repository and the lockfile alone.

---

## 6. pyproject.toml for a beginner

Validated end to end with uv 0.13.5 (`uv sync`, `uv build`, metadata inspected; kept in `anatomy/fxlab`) [local]:

```toml
[project]                                  # standard metadata (PEP 621); name and version are required
name = "fxlab"                             # distribution name; the module is fxlab (dashes/dots become _)
version = "0.1.0"                          # the single source of the version
description = "Small research toolkit (course demo)"
readme = "README.md"
requires-python = ">=3.12"                 # lower bound only
license = "MIT"                            # SPDX string (PEP 639); becomes License-Expression in METADATA
license-files = ["LICENSE"]
authors = [{ name = "Example Author" }]
classifiers = ["Private :: Do Not Upload"] # PyPI refuses uploads carrying this classifier
dependencies = ["tabulate>=0.9"]           # needed at run time

[project.optional-dependencies]            # extras: published, for users of the package
viz = ["rich>=13"]

[project.scripts]                          # command name = "module:function"; needs a build system
fxlab = "fxlab:main"

[build-system]                             # how to turn the folder into an installable package
requires = ["uv_build>=0.13.5,<0.14.0"]
build-backend = "uv_build"

[dependency-groups]                        # local only (PEP 735)
test = ["pytest>=9"]
lint = ["ruff>=0.17"]
dev = [{ include-group = "test" }, { include-group = "lint" }]

[tool.uv]                                  # one table per tool
default-groups = ["dev"]
[tool.ruff]
line-length = 100
[tool.pytest.ini_options]
testpaths = ["tests"]
```

- `[build-system]` present means uv builds and installs the project itself (editable). Absent means only dependencies are installed and `[project.scripts]` cannot work; `tool.uv.package = true/false` overrides. [source: https://docs.astral.sh/uv/concepts/projects/config/]
- `uv_build` supports pure Python only and expects `src/<name>/__init__.py`. The upper bound in `requires` is deliberate. When uv is newer than the range, 0.13.5 still builds and prints `warning: build_system.requires = ["uv-build>=0.12.0,<0.13.0"] does not contain the current uv version 0.13.5` (simulated). After a future `brew upgrade uv` to 0.14 the learner will see this until the range is edited. [local] [source: https://docs.astral.sh/uv/concepts/build-backend/]
- Why `src/`: the code can only be imported through the installed package, so tests and notebooks exercise what would ship and cannot pick up a stray folder in the working directory. [source: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/]
- PyPA guidance: think twice before an upper bound on `requires-python`; `[build-system]` "should always be present"; the table form of `license` is deprecated. [source: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/]
- `uv.lock`: TOML, `version = 1`, `revision = 5`; one `[[package]]` per resolved package with exact version, source, sdist and wheel URLs and sha256 hashes; the project itself appears as `source = { editable = "." }`; group and extra membership is recorded. It is universal (all platforms in one file), written only by uv, never edited by hand, and committed: "This file should be checked into version control". [local] [source: https://docs.astral.sh/uv/concepts/projects/layout/]
- Commit: `pyproject.toml`, `uv.lock`, `.python-version`, `README.md`, `src/`, `tests/`, `.gitignore`. Never commit: `.venv`, `.venv.nosync/`, `dist/`, `__pycache__/`.

---

## 7. Old tutorial to uv translation table

| Old tutorial says | Today with uv | Checked |
|---|---|---|
| `python -m venv .venv` | nothing; the first `uv run`/`uv sync` creates `.venv` (`uv venv` only for non-project use) | [local] |
| `source .venv/bin/activate` | not needed; prefix commands with `uv run` | [local] |
| `pip install pandas` | `uv add pandas` | [local] |
| `pip install pytest` for development | `uv add --dev pytest` | [local] |
| `pip install -r requirements.txt` | new project: `uv add -r requirements.txt`; existing uv project: `uv sync`; legacy folder: `uv pip install -r requirements.txt` | [local] |
| `pip freeze > requirements.txt` | `uv.lock` is maintained automatically; if a file is demanded: `uv export -o requirements.txt` | [local] |
| `pip install -e .` | automatic: `uv sync` installs the project editable | [local] |
| `pip install --upgrade pkg` | `uv lock --upgrade-package pkg` then `uv sync` | [local] |
| `pip uninstall pkg` | `uv remove pkg` | [local] |
| `pip list`, `pipdeptree` | `uv pip list`, `uv tree` | [local] |
| `python script.py`, `pytest` | `uv run script.py`, `uv run pytest` | [local] |
| `setup.py`, `setup.cfg`, `MANIFEST.in` | `[project]` and `[build-system]` in `pyproject.toml` | [local] |
| `python setup.py sdist bdist_wheel`, `python -m build` | `uv build` | [local] |
| `__version__ = "..."` edited by hand, bump2version | `uv version --bump patch` | [local] |
| `pyenv install 3.13`, `pyenv local 3.13` | `uv python install 3.13`, `uv python pin 3.13` | pin [local]; install tested only into a scratch dir |
| `pipx run tool`, `pipx install tool` | `uvx tool`, `uv tool install tool` | [local] |
| `pip-compile` | `uv lock` (or `uv pip compile requirements.in -o requirements.txt`) | [local] |
| `twine upload dist/*` | `uv publish` (not exercised) | help only |
| `poetry add / lock / install` | `uv add / lock / sync` | [memory] for the Poetry side |
| `[tool.uv] dev-dependencies = [...]` | `[dependency-groups] dev = [...]` | [local] |
| `uv init` then `uv run hello.py` or `main.py` | `uv run <project-name>`; the old flat layout is `uv init --no-package` | [local] |

---

## 8. What changed compared with older tutorials

| Change | Since | Basis |
|---|---|---|
| `uv init` packaged by default, `src/` layout, `uv_build`, `[project.scripts]` | 0.12.0, 2026-07-28 | [source: https://github.com/astral-sh/uv/releases/tag/0.12.0], [local] |
| Broken `.venv` symlink stops discovery with an error; `uv venv --clear` refuses non-venv directories; `uv run script.py` discovers the project from the script's directory; default pre-release mode `if-necessary`; sdists carry `pyproject.toml.orig` | 0.12.0 | same |
| Default stable Python 3.15; cache format changed; no distutils startup patch in new venvs | 0.13.0, 2026-10-09 | [source: https://github.com/astral-sh/uv/releases/tag/0.13.0] |
| `uv_build` is the default backend for packaged projects (was hatchling); `uv python install` puts `python3.x` on PATH; `uv lock --check` exits 1 | 0.8.0, 2025-07-17 | [source: https://github.com/astral-sh/uv/releases/tag/0.8.0]; date from PyPI |
| `uv version` reads and bumps the project version | 0.7.0, 2025-04-29 | [source: https://github.com/astral-sh/uv/releases/tag/0.7.0] |
| `uv add --dev` writes `[dependency-groups]` | 0.4.27, 2024-10-25 | behaviour [local]; version [memory], its date from PyPI |
| `uv format` (Ruff), experimental | 0.8.13, 2025-08-21 | behaviour [local]; version [memory], its date from PyPI |
| `uv check` (ty), experimental | 0.11.18, 2026-06-01 | behaviour [local]; version from a third-party newsletter, date matches PyPI |
| `uv audit` (OSV), experimental | not established | behaviour [local] |
| `uv venv` errors on an existing environment instead of replacing it | by 0.13.5 | [local] |
| `uv export --format pylock.toml`; `license = "MIT"` (PEP 639) accepted by `uv_build` | current | [local] |
| Fixed after 0.13.5: digit-leading project names (0.13.7); PEP 832 redirect-file preview and smaller lockfiles (0.13.9) | 0.13.6 to 0.13.9 | [source: https://raw.githubusercontent.com/astral-sh/uv/main/CHANGELOG.md] |

---

## 9. Beginner pitfalls (ordered by how likely they are here)

1. `ModuleNotFoundError: No module named '<own package>'` although `uv sync` reports success: hidden `.pth` in an iCloud folder (section 5). Looks random because it appears minutes after a working run.
2. Typing `pip install ...` or `pip3 install ...` from an old tutorial: lands in Xcode's Python 3.9 or fails. Rule for the course: inside a project the only install command is `uv add`.
3. `uv sync` "deleting my packages": anything installed by hand, any non-default group and any extra is removed by an exact sync.
4. Looking for `main.py` after `uv init`; trying `python -m <pkg>` without a `__main__.py`.
5. Project created by the assistant pinned to 3.12 while the learner assumed 3.14 (two uv views). Always `--python 3.14`.
6. Folder names: leading digit (broken on 0.13.5), Chinese characters (rejected, needs `--name`), spaces and capitals (silently normalised, so folder name and package name differ).
7. `uv init` in a subfolder of something that already has a `pyproject.toml` creates a workspace and edits the parent file.
8. `rm -rf .venv` on a symlinked environment; cloning into iCloud and forgetting the symlink step.
9. Renaming or moving the project folder and then `uv run pytest` failing on a stale shebang.
10. Editing `uv.lock` by hand, or adding it to `.gitignore`.
11. Hand-editing `pyproject.toml` dependencies and wondering why nothing is installed until the next `uv lock` / `uv sync` / `uv run`; `uv sync --locked` then fails by design.
12. Putting pytest and ruff in `[project.optional-dependencies]` (they get published as an extra) or copying `[tool.uv] dev-dependencies` from an old post.
13. Activating one environment and running uv in another project: uv warns and ignores `VIRTUAL_ENV`.
14. `uv run --with x` or `uv pip install x` for something the code really imports: works today, missing for the next person.
15. `uv self update` on a Homebrew install (refused; use brew).
16. `uv init` copies the git e-mail address into `pyproject.toml`; use `--author-from none` if that is unwanted.
17. First `git commit` in a repo created by `uv init` fails with "error: cannot run gpg: No such file or directory" when global `commit.gpgsign=true` and `gpg.format=openpgp` are set but there is no `gpg` on PATH. `git config commit.gpgsign false` in the repo, or `git -c commit.gpgsign=false commit`, gets through.

---

## 10. Recommendations for the course

Teach first, in this order, each with a visible before and after in the files:
1. One project, three files: `uv init --python 3.14 <name>`, then read `pyproject.toml` together; `uv run <name>`; show that `.venv` and `uv.lock` appeared.
2. `uv add` a real dependency (numpy or pandas), then diff `pyproject.toml` (what I asked for) against `uv.lock` (what I got, exactly).
3. `uv add --dev pytest ruff` and the idea of groups; `uv sync` as "make the environment match the lock, add what is missing, remove what is extra".
4. Throw the environment away and rebuild it (`uv venv --clear && uv sync`): the environment is disposable, the lock is the record.
5. Commit `pyproject.toml`, `uv.lock`, `.python-version`; clone to a second folder and `uv sync --locked` to prove reproducibility.
6. Later lessons: `uv lock --upgrade-package` with `uv tree --outdated`; `uv version --bump`; `uv build` and unzipping the wheel; `uvx`; `uv sync --locked` in CI; `uv audit` as a preview of supply-chain checks.

Skip or only mention: workspaces, `uv pip compile`, `uv publish`, indexes and `uv auth`, other build backends, extension modules, `uv export`, activation scripts, preview features, PEP 723 scripts (a short optional note is enough).

Defaults to use everywhere:
- `uv init --python 3.14 <lowercase-hyphen-name>` (letter first), packaged default layout, `uv_build`.
- Course root folder without a `pyproject.toml`; each practice project standalone.
- On an iCloud-synced Desktop: the `.venv.nosync` recipe plus the health check from 5.6, introduced in the very first lesson as a known quirk of iCloud-synced folders, with option A presented as the professional norm and a later guided move.
- Dev tools as a `dev` dependency group so their versions are locked; run them through `uv run`.
- Add `.venv.nosync/` and `.DS_Store` to `.gitignore`.
- For the learner's existing project (if any): when it already has `requires-python`, `uv_build` and a `.gitignore` that lists `.venv`, nothing in the packaging setup needs redoing; it needs `git init`, tests, lint config and CI.

Plain-Chinese analogies that fit the verified behaviour:
- `pyproject.toml` = 项目的"身份证 + 配料表"：我是谁、我需要什么。
- `uv.lock` = "精确到批次号的采购小票"：每样东西到底买的是哪个版本、从哪买的、校验码是多少。配料表写"面粉 ≥ 1 斤"，小票写"某牌面粉 1.2 斤，批号 xxx"。
- `.venv` = 这个项目专属的"厨房"：可以随时拆掉，照着小票几秒钟重建，所以不进 Git。
- `uv sync` = "照小票盘点厨房：缺的补上，多的拿走"；`uv run` = "先盘点，再开火"。
- `dependencies` 与 `dependency-groups` = "菜里的食材" 与 "厨师自己用的温度计和秤"：后者不会端给客人（不进发布包）。
- extras = "可选加料"，给使用你这个包的人选。
- `requires-python` = 包装上印的"适用版本下限"；`.python-version` = "我这台灶现在用的是哪一版"。
- 可编辑安装（`.pth`）= 厨房门口贴的一张"代码在 src 那边"的路标，不是把代码复印一份。iCloud 给路标盖了"隐藏"章，Python 出于安全规定不看隐藏的路标，于是找不到你的包。
- `src/` 布局 = 把要交付的货放进仓库间，门厅只放说明书和配置，测试只能从"正门"（已安装的包）拿货。
- iCloud 与 Git = 两个管家同时整理同一个抽屉：一个按文件逐个同步，一个按自己的账本整体记账，迟早打架。
- `uvx` = 临时借一把工具用完就还；`uv tool install` = 把工具长期挂在工具墙上。
- `--locked` = "小票必须和配料表对得上，否则停工"（给 CI 用）；`--frozen` = "不核对，直接照小票装"。

---

## 11. Not verified today

- Whether current iCloud Drive uploads dot-items (`.git`, `.gitignore`) at all, and exactly which process sets `UF_HIDDEN`; Apple does not document it and `fileproviderctl` is blocked in the sandbox.
- Whether hidden flags can still appear inside a `.nosync` directory: no public report found answers it (searched 2026-11-20), and no controlled test inside iCloud was run.
- The uv view of an unsandboxed assistant shell and of a real interactive Terminal (the Terminal column in section 1 is simulated by setting `UV_PYTHON_INSTALL_DIR`).
- Introduction versions of `uv format` (0.8.13 from memory), `uv check` (0.11.18 per a third-party newsletter), `uv audit` (unknown) and `[dependency-groups]` support (0.4.27 from memory) were not checked against the uv changelogs; only the release dates of those versions were confirmed on PyPI.
- `uv publish`, `uv auth`, workspaces beyond the nested-init test, and `uv tool install` into the real tool directory were not exercised.
- Behaviour on uv 0.13.6 to 0.13.9 and on 0.14 (only 0.13.5 is installed).
- Side note: I ran `uv cache prune` once on the shared `$TMPDIR/uv-cache` at about 14:50 (removed 1.2 GiB of unused entries). Existing environments are unaffected; other agents may have had to re-download packages.
