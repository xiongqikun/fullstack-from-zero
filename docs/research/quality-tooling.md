# Brief: quality-tooling (lint/format, type checking, tests, git hooks, task runner, .editorconfig)

Verified 2026-11-19 on macOS 27.2.1 arm64 / zsh, inside the Claude Code Bash sandbox.
Tags: **[local]** = ran here today; **[source: URL]** = read in a primary source today; **[memory]** = not verified.
`<scratch>` = the directory that contains this file.

## 0. What was verified and how
- Throwaway package `fxkit` (uv 0.13.5, src layout, `uv_build` backend, Python 3.14.9 venv, pandas 3.1.1,
  numpy 2.5.5) at `<scratch>/demo/`: a real git repo with 8 commits (7 through the hooks, 1 deliberately with
  `--no-verify`). `make check` and `git commit` pass there. Section 8 lists its config files. [local]
- Edge cases in sibling folders: `ruff-lab`, `types-lab`, `pytest-lab`, `make-lab`, `nobuild`, `nosync-lab`,
  `nosync-lab2`, `cache-lab`. Versions/dates: PyPI JSON API. Hook revs: `git ls-remote --tags` (GitHub API was rate-limited).
- Measurements of a private project are not published (rule G10a); this brief keeps only conclusions with a
  public basis. Where such a conclusion needed a public source after the fact, the source is cited with the
  date it was checked (2026-11-20).

## 1. Decisions at a glance

| Area | Teach | Verified version (date) | Mention only |
|---|---|---|---|
| Lint + format | Ruff, always as `uv run ruff` | 0.17.5 (2026-11-12); the global uv tool is 0.17.2 | Black, isort, flake8, pylint as history |
| Types | mypy with `strict = true` | 2.4.1 (2026-10-28), runs on Python 3.14 | ty 0.0.107 (beta), basedpyright 1.40.2 / Pyright 1.1.414, Pyrefly 1.5.0 |
| Tests | pytest + pytest-cov, a taste of hypothesis | pytest 9.2.0, pytest-cov 7.1.0, coverage 7.17.3, hypothesis 6.170.15 | unittest, tox/nox |
| Git hooks | pre-commit, `.pre-commit-config.yaml` | pre-commit 4.7.0 (2026-10-12) | prek 0.5.11, a faster drop-in runner |
| Task runner | Makefile | GNU Make 3.81 (preinstalled) | just 1.59.0, poethepoet 0.49.0 |
| Editor norms | `.editorconfig` | spec 0.17.2 | |

Install command that was run: `uv add --dev ruff pytest pytest-cov mypy pandas-stubs hypothesis pre-commit`
(writes `[dependency-groups] dev`; `uv sync` / `uv run` install that group by default). [local]

## 2. Environment facts that can bite on the reference Mac (plan G7)
1. **`uv run` fails inside the Claude Code sandbox unless the cache is redirected.** [local]
   `error: Could not acquire lock ... Operation not permitted ... ~/.cache/uv/.tmpXXXX`. It works with
   `UV_CACHE_DIR="$TMPDIR/uv-cache" uv run ...`, with `UV_NO_CACHE=1 uv run ...` (only while the venv is in
   sync), or by calling `.venv/bin/ruff|mypy|pytest` directly. Everything the course wraps around `uv run`
   (Makefile, local hooks) inherits this when Claude runs it. In the learner's own Terminal it just works.
2. **pre-commit cannot bootstrap its hook environments inside the sandbox without workarounds.** [local]
   (a) `PermissionError ... ~/.cache/pre-commit`; (b) `Proxy CONNECT aborted`, because pre-commit strips
   `GIT_CONFIG_PARAMETERS` (where the sandbox puts its proxy setting) from git's environment; (c) pip in hook
   environments fails TLS: `SSLCertVerificationError('OSStatus -26276')`. It worked here only with
   `PRE_COMMIT_HOME=$TMPDIR/...`, `GIT_HTTP_PROXY_AUTHMETHOD=basic`, `PIP_USE_DEPRECATED=legacy-certs`.
   Once the environments exist, pre-commit runs against a read-only store (verified with `chmod -R a-w`).
   Consequence: the learner runs `uv run pre-commit install --install-hooks` once in their own Terminal.
3. **`git commit` fails when signing is on but gpg is missing.** [local] If `~/.gitconfig` has `commit.gpgsign=true`,
   `gpg.format=openpgp`, `gpg.program=gpg` and there is no `gpg` binary on PATH or in the usual locations:
   `error: cannot run gpg: No such file or directory ... fatal: failed to write commit object`.
   The throwaway repo used `git config --local commit.gpgsign false`. The git lessons must settle this
   (install gnupg, SSH signing, or no signing) before any hook lesson.
4. **Three Ruff versions can be in play.** [local] `ruff` (global uv tool) 0.17.2; `uv run ruff` (project,
   from `uv.lock`) 0.17.5; `uv format` (experimental uv subcommand) downloaded Ruff 0.15.22, because its default
   constraint in uv 0.13.5 is `>=0.15,<0.16`, and so did not format the README (9 files instead of 10).
5. `/usr/bin/make` in the sandbox prints two `xcrun ... couldn't create cache file` errors and then works
   (exit 0); `/Library/Developer/CommandLineTools/usr/bin/make` is silent. [local]
6. **iCloud Desktop + a `.venv -> .venv.nosync` symlink (a common workaround).** [local, simulated in `nosync-lab`]
   - `.gitignore` entry `.venv/` does not ignore a symlink named `.venv` (`?? .venv`); it must be `.venv`
     without the slash, plus `.venv.nosync/`.
   - Ruff's default excludes cover `.venv` and `site-packages` but not `.venv.nosync`, and **Ruff honours
     `.gitignore` only inside a git repository**. So in a project with no repo yet Ruff would lint and format
     files inside `.venv.nosync/`.
     Fix: `[tool.ruff] extend-exclude = [".venv.nosync"]` (verified), or run `git init` first (verified).
   - Tool caches land in the synced folder. All of them can be moved into one
     `.cache.nosync/` folder (verified in `cache-lab`): `[tool.ruff] cache-dir`, `[tool.mypy] cache_dir`,
     `[tool.pytest] cache_dir`, `[tool.coverage.run] data_file`, `[tool.coverage.html] directory`, env
     `HYPOTHESIS_STORAGE_DIRECTORY`. Whether iCloud really skips it was not tested; moving projects out of
     iCloud is the cleaner fix.
7. `uv init --package` here wrote `requires-python = ">=3.12"` and `.python-version` 3.12 (`uv python find`
   returns the managed 3.12.15 although `python3` is 3.14.9) and copied the git user name and e-mail into
   `authors`. Pass `--python 3.14`; decide deliberately what goes into `authors`. [local]
8. `git init` creates `main` here: Xcode's system gitconfig sets `init.defaultbranch main`. [local]

## 3. Ruff 0.17.x
### 3.1 The change older tutorials miss: the default rule set
- Until 0.15.x the default was `select = ["E4", "E7", "E9", "F"]` (59 rules). **Ruff 0.16.0 (2026-07-23) raised
  it to 413 rules** and dropped 18 opinionated E/F rules from it (E401, E402, E701-E703, E711-E714, E721,
  E731, E741-E743, F403, F405, F406, F722). 0.17.0 (2026-10-09) removed 7 `DTZ` rules and restored F406.
  [source: https://astral.sh/blog/ruff-v0.16.0] [source: https://raw.githubusercontent.com/astral-sh/ruff/main/BREAKING_CHANGES.md]
- Measured: `ruff check --isolated --show-settings` lists **407 enabled rules** in 0.17.2 and 0.17.5; the tool
  knows 977 rules (832 stable, 145 preview). By prefix: PYI 47, UP 42, F 40, RUF 36, PLE 33, B 29, SIM 21,
  PLW 20, C4 17, FURB 17, PLR 13, ASYNC 10, and single rules such as `I001`, `E722`, `E902`, `W605`, `D419`,
  `N999`, `S102/S110/S112`, `T100`. [local]
- The defaults follow Ruff's new rule categories (a preview feature): correctness, suspicious, complexity,
  performance, style are on; security, formatting, pedantic, restriction are off. `ruff rule --all
  --output-format json` shows a `category` per rule: `E711`, `N802`, `D103`, `PLR0913`, `ANN001` are
  "pedantic"; `E501`, `W291` "formatting"; `C901`, `S101`, `T201` "restriction". Four new preview rules have a
  name and a category but no code. [local] [source: https://docs.astral.sh/ruff/linter/]
- Official guidance is split. The tutorial calls the default set a good starting point and adds rules with
  `extend-select`; `ruff config lint.select` shows `extend-select = ["B", "Q"]` "on top of the defaults"; the
  linter page still says "Prefer lint.select over lint.extend-select" and "start with a small set
  (`select = ["E", "F"]`)". [source: https://docs.astral.sh/ruff/tutorial/] [source: https://docs.astral.sh/ruff/linter/] [local]
- Old behaviour back: `select = ["E4", "E7", "E9", "F"]` (7 findings instead of 14 on the sample below). [local]

### 3.2 Commands (all run)

```
uv run ruff check                        # lint; exit 1 when there are findings
uv run ruff check --fix                  # apply safe fixes
uv run ruff check --fix --unsafe-fixes   # also fixes that may change behaviour: read the diff
uv run ruff check --statistics           # count per rule, marks the fixable ones
uv run ruff check --output-format concise
uv run ruff rule B006                    # what, why, example, fix safety (the rule name works too)
uv run ruff linter                       # prefix -> origin (B = flake8-bugbear ...)
uv run ruff config lint.select           # documentation of one option
uv run ruff check --show-settings FILE   # resolved settings and enabled rules
uv run ruff format                       # rewrite files
uv run ruff format --check               # exit 1 when a file would change
uv run ruff format --diff                # same, and print the diff
```

Zero-config output on a deliberately messy file (excerpt): [local]

```
B006 Do not use mutable data structures for argument defaults
 --> messy.py:6:76
help: Replace with `None`; initialize within function
note: This is an unsafe fix and may change runtime behavior
Found 14 errors.
[*] 7 fixable with `--fix` (4 unsafe fixes available with `--fix --unsafe-fixes`).
```

- That file gets I001, F401 x3, UP035, UP006 x2, UP045, B006, E722, S110, F841, SIM103, UP031 with defaults;
  `weights == None` (E711) and the function name `Mean` (N802) are not reported. `--fix` fixed 8 of 14;
  `--fix --unsafe-fixes` left only the bare `except: pass`. [local]
- Since 0.16 the default output prints each fix as a diff; since 0.17 unsafe fixes are shown too, but applying
  them still needs `--unsafe-fixes`. [local] [source: BREAKING_CHANGES.md]
- `ruff format` does not sort imports; `ruff check --fix` does (I001 is a default rule). Order: `check --fix`,
  then `format`. A combined command is only "planned". [source: https://docs.astral.sh/ruff/formatter/] [local]
- The formatter is Black-compatible and follows the "2026 style guide" since 0.15.0 (2026-02-03).
  [source: https://astral.sh/blog/ruff-v0.15.0] **With target py314 it rewrites `except (ValueError, TypeError):`
  to `except ValueError, TypeError:`** (PEP 758; a syntax error before 3.14). Verified with `--target-version
  py314`; unchanged with py312. Any project that targets `>=3.14` will see it. [local]
- Since 0.16 `ruff format` also formats Python code blocks in Markdown (README); it formats `.ipynb` cells;
  `ruff check` lints notebooks (`analysis.ipynb:cell 2:1:8: F401 ...`) but not Markdown. Opt out with
  `extend-exclude = ["*.md"]`. [local] [source: blog 0.16]
- `target-version` is inferred from `requires-python` (`>=3.12` resolved to 3.12). With neither set, the
  default is 3.11 since 0.17.0. [local] [source: BREAKING_CHANGES.md]

### 3.3 Suppression comments

```python
import os  # noqa: F401
import sys  # ruff: ignore[F401] kept for a doctest elsewhere
# ruff: ignore[B006]
def cached(key, store={}): ...
```

All three forms were run; a `ruff: ignore` comment on the line above covers a whole multi-line statement, and a
free-text reason may follow the code (0.16+). `--add-noqa` and `--add-ignore` write comments for every current
finding; RUF100 (unused `noqa`) is a default rule; with `--preview` comments use names
(`# ruff: ignore[unused-import]`). [local] Block form `# ruff: disable[CODE]` / `# ruff: enable[CODE]` (0.15+)
and `# ruff: file-ignore[CODE]` (0.16+) were read about, not run. [source: blog 0.16]

### 3.4 Recommended selection: keep the defaults, add eight families (512 rules enabled)
What the defaults already give (do not re-list them): `F` Pyflakes, undefined names and unused imports;
most of `B` bugbear, e.g. mutable default arguments; `UP` pyupgrade, modern syntax for the target Python;
`SIM` simplifications; `I001` import sorting; curated parts of `RUF`, `PL*`, `C4`, `FURB`, `PERF`, `TRY`.
The eight added families and the four ignores are justified line by line in the config in 8.1.

Optional later, each with a known cost: `PLR09` (too many arguments/branches; numeric analysis functions hit the
5-argument limit), `ARG`, `ERA` (commented-out code), `DTZ` (naive datetimes), `S` (bandit: flags `assert` and
stdlib `random`; Ruff itself calls the category noisy), `T20` (`print`), `ANN` (redundant with mypy strict).
Never `ALL`.

On a pandas/NumPy-style sample the defaults gave 3 findings and this selection 13: N802, D103, A002, B006, PD002,
N806 (a matrix named `X`), PD011, NPY002, PD015, PD003, E712, SIM102 x2. `dict.values()` was not mistaken for
pandas. For matrix names the option `[tool.ruff.lint.pep8-naming] extend-ignore-names` exists (not run). [local]

### 3.5 Chinese text [sources checked 2026-11-20]
- `RUF001/RUF002/RUF003` flag "ambiguous" Unicode characters in strings, docstrings and comments. The RUF002
  page's own example is a full-width parenthesis (U+FF09), the kind of punctuation Chinese text is full of.
  They are not defaults (3.1), but `select = [..., "RUF"]` (common in older configs) or `ALL` enables them.
  `lint.allowed-confusables` lists characters to accept.
  [source: https://docs.astral.sh/ruff/rules/ambiguous-unicode-character-docstring/]
  [source: https://docs.astral.sh/ruff/settings/ (`lint.allowed-confusables`)]
- `D415` (on in the Google convention) wants the first docstring line to end in a period, question mark or
  exclamation point. Ruff's source checks exactly the three ASCII marks `.`, `!`, `?`, so a summary that ends
  in the Chinese full stop `。` is reported; the fix, marked unsafe, appends `.`. Hence the ignore in 8.1.
  [source: https://docs.astral.sh/ruff/rules/missing-terminal-punctuation/]
  [source: https://raw.githubusercontent.com/astral-sh/ruff/main/crates/ruff_linter/src/rules/pydocstyle/rules/ends_with_punctuation.rs]
- `line-length`: on lines with East Asian characters Ruff adds up the Unicode width of each character instead
  of counting characters [source: https://docs.astral.sh/ruff/settings/ (`line-length`)]; Chinese characters
  are "wide", two columns each [memory: Unicode UAX #11]. The formatter "only makes a best-effort attempt to
  wrap lines", so formatted code may still trigger E501 [source: https://docs.astral.sh/ruff/formatter/,
  "Conflicting lint rules"]. Hence `ignore = ["E501"]`; the alternative is `line-length = 100` and keeping the
  rule. Suggestion (not measured on a public project): with Chinese comments and docstrings, expect many E501
  findings that the formatter cannot remove.

## 4. Type checking
### 4.1 Landscape today

| Tool | Version (date) | Status | Seen here [local] |
|---|---|---|---|
| mypy | 2.4.1 (2026-10-28); 2.0.0 on 2026-05-06 | stable | compiled wheel on 3.14; demo with pandas: 1.9 s cold, 0.15 s warm |
| ty (Astral) | 0.0.107 (2026-11-18); beta since 2025-12-16 | **beta**, about two releases a week | 0.8 s on the demo; rich diagnostics; shows types as `float*` |
| basedpyright / Pyright | 1.40.2 (2026-10-04) on Pyright 1.1.414 (2026-09-10) | stable | bundles Node; 4 errors + 10 warnings on the 23-line sample |
| Pyrefly (Meta) | 1.5.0 (2026-11-19); 1.0.0 on 2026-05-12 | stable | no config = preset `basic` = **0 errors** on the sample; 4 with `--preset default` |

- ty README: "ty is currently in beta", "uses 0.0.x versioning", "does not yet have a stable API; breaking
  changes, including changes to diagnostics, may occur between any two versions". No `--strict` flag, no plugin
  system. The beta post aimed at a stable release in 2026; none was found. [source: https://github.com/astral-sh/ty]
  [source: https://docs.astral.sh/ty/reference/typing-faq/] [source: https://astral.sh/blog/ty]
- `uv check` (uv 0.13.5) runs ty and prints "`uv check` is experimental and may change without warning". [local]
- pandas-stubs is "tested with mypy, pyright and pyrefly"; ty is not listed. [source: https://github.com/pandas-dev/pandas-stubs]
- mypy 2.0 turned on `--local-partial-types` and `--strict-bytes`, changed `--allow-redefinition`, dropped
  Python 3.9. 2.4 makes the native parser the default, supports Python 3.15 syntax and parallel checking
  (`-n`). [source: https://mypy.readthedocs.io/en/stable/changelog.html] `mypy -n 4` failed in this sandbox
  ("Failed to establish connection with worker"); a small project does not need it. [local]

**Recommendation: teach mypy.** It is stable, a plain Python dev dependency, one of the three checkers
pandas-stubs is tested against, strict mode is one switch, and every error code is documented and searchable.
Speed no longer separates the tools at this project size. Show `uvx ty check` once as a second opinion and
say that it is beta: lessons built on ty's diagnostics would go stale within weeks.

### 4.2 Install, configure, run (all run)
`uv add --dev mypy pandas-stubs`, then `uv run mypy` (reads `[tool.mypy]`, exit 1 on errors).

```toml
[tool.mypy]
files = ["src", "tests"]
strict = true
warn_unreachable = true
enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool"]
pretty = true
show_error_code_links = true

[[tool.mypy.overrides]]          # for a library that has neither stubs nor a py.typed marker
module = ["foobar.*"]            # placeholder name, as in the mypy docs
ignore_missing_imports = true
```

The override block is copied from the mypy docs, not run on the demo. The docs list better options first (a
newer version of the library with types, a stub package, your own stubs) and show the error it silences:
`module is installed, but missing library stubs or py.typed marker`.
[source: https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-library-stubs-or-py-typed-marker, checked 2026-11-20]

Deliberately wrong snippet (`types-lab/wrong.py`, lines 19-22) and the real default-mode output:

```python
def annualised_return(daily_returns: list[float], days: int = 252) -> float: ...
def find_ticker(tickers: dict[str, float], name: str) -> float | None: ...
result: int = annualised_return([0.01, "0.02", -0.005])   # line 19
price = find_ticker({"AAPL": 190.0}, "MSFT")
print(price + 1.0)                                        # line 21
print(annualised_return(0.01))                            # line 22
```

```
wrong.py:19: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
wrong.py:19: error: List item 1 has incompatible type "str"; expected "float"  [list-item]
wrong.py:21: error: Unsupported operand types for + ("None" and "float")  [operator]
wrong.py:21: note: Left operand is of type "float | None"
wrong.py:22: error: Argument 1 to "annualised_return" has incompatible type "float"; expected "list[float]"  [arg-type]
Found 4 errors in 1 file (checked 1 source file)
```

ty on line 22: `error[invalid-argument-type]: Argument to function `annualised_return` is incorrect` ...
`Expected `list[float]`, found `float*``, with source context and the parameter declaration. [local]

### 4.3 Traps verified here [local]
- **Default mypy prints `Success` for unannotated code**: `def total(prices): return "sum: " + 1` passes;
  `--strict` reports 3 errors. Strict mode is what makes the tool meaningful for a beginner.
- `float ** float` is typed `Any`, so `return total ** (days / n) - 1` gives `Returning Any from function
  declared to return "float"  [no-any-return]` under strict. Same for `series.std() * np.sqrt(n)`
  (`np.sqrt(252)` reveals as `Any`). Fix: wrap in `float(...)`.
- pandas 3.1.1 ships no `py.typed`. Without stubs: `Library stubs not installed for "pandas"
  [import-untyped]`, hint `python3 -m pip install pandas-stubs`; in a uv project that is
  `uv add --dev pandas-stubs` (3.1.0.261029; the version tracks pandas' major.minor).
- numpy 2.5.5 ships `py.typed`; nothing to install. `numpy.typing.mypy_plugin` is marked deprecated since
  NumPy 2.3 in its own source: do not copy `plugins = ["numpy.typing.mypy_plugin"]` from old tutorials.
- With pandas-stubs, bare `pd.Series` / `pd.DataFrame` annotations pass strict mode. `pd.Series[float]` is
  understood by mypy but **raises `TypeError: type 'Series' is not subscriptable` at import on Python 3.12**;
  it only works on 3.14, where annotations are evaluated lazily. Teach plain `pd.Series`.
- Stubs do not know column names (`frame["clsoe"]` passes), and `prices.no_such_method()` yields the
  misleading `"float" not callable  [operator]`.
- `# type: ignore` (mypy) and `# noqa` / `# ruff: ignore` (Ruff) are separate systems. With the config above
  a bare `# type: ignore` is rejected (`[ignore-without-code]`, it suggests `type: ignore[assignment]`) and a
  stale one is reported (`[unused-ignore]`).

## 5. pytest, coverage, hypothesis
### 5.1 Configuration: what is right today
- pytest 9.0 (2025-11) added native TOML: `[tool.pytest]` in `pyproject.toml` (or `pytest.toml` with a
  `[pytest]` table), using real TOML types. `[tool.pytest.ini_options]` "remains supported, but both tables
  cannot be used at the same time". [source: https://docs.pytest.org/en/stable/changelog.html]
  [source: https://docs.pytest.org/en/stable/reference/customize.html]
- On 9.2.0 [local]: both tables give `ERROR: ... Cannot use both [tool.pytest] (native TOML types) and
  [tool.pytest.ini_options]`; `addopts = "-ra -q"` in the native table gives `config option 'addopts' expects a
  list for type 'args', got str`; `[tool.pytest.ini_options]` alone still works.
- `strict = true` (9.0+) enables `strict_config`, `strict_markers`, `strict_parametrization_ids`,
  `strict_xfail`: a misspelt key becomes `ERROR: Unknown config option: testpath` (exit 4) instead of a warning,
  an unregistered marker `'slwo' not found in `markers` configuration option`. The docs recommend it and warn
  that later versions may add checks. [local] [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html]
- The same page recommends `--import-mode=importlib` for new projects and `src/<pkg>/` + `tests/` without
  `__init__.py`. Cost: test modules cannot import each other by bare name; shared helpers go in `conftest.py`.
- Also in 9.x: Python 3.9 dropped; `subtests` fixture (experimental); 9.1 `--max-warnings`; 9.2 makes
  `indirect` / `ids` / `scope` of `parametrize` keyword-only. [source: changelog]

```toml
[tool.pytest]
minversion = "9.0"
testpaths = ["tests"]
addopts = ["-ra", "--import-mode=importlib"]
strict = true
markers = ["slow: slow tests (deselect with -m 'not slow')"]

[tool.coverage.run]
source_pkgs = ["fxkit"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = true
fail_under = 90
exclude_also = ["if TYPE_CHECKING:"]
```

### 5.2 src layout + uv: how tests find the package [local]
- With a `[build-system]` table, `uv sync` / `uv run` install the project itself in editable mode, so
  `from fxkit.returns import ...` works in tests with no path tricks.
- Without it: `ModuleNotFoundError: No module named 'mypkg'`. Fix A: `[tool.pytest] pythonpath = ["src"]`.
  Fix B: add the `uv_build` build system.
- `uv run` re-syncs first: after an edit to `pyproject.toml` it prints `Uninstalled 1 package / Installed 1 package`.

### 5.3 Features exercised in `demo/tests/` (20 tests, 1.1 s)
Fixtures in `conftest.py`; `tmp_path`; `monkeypatch.setenv/delenv`; `capsys.readouterr()`;
`@pytest.mark.parametrize(("series", "expected"), [...], ids=[...])`; custom marker `slow`; `pytest.approx`;
`pytest.raises(ValueError, match="...")`; `pd.testing.assert_series_equal`; in a lab also `skip`, `skipif`,
`xfail(strict=True, raises=...)` with `-ra`, and `--setup-show` (prints fixture setup/teardown order).

```
uv run pytest                    # everything
uv run pytest -x                 # stop at the first failure
uv run pytest -k drawdown        # name filter; "one or four" also works
uv run pytest -m "not slow"      # marker filter
uv run pytest --lf               # only the tests that failed last time (--ff: those first, then the rest)
uv run pytest tests/test_returns.py::test_max_drawdown
uv run pytest --cov              # report and gate driven by [tool.coverage.*]
uv run pytest --cov --cov-report=html            # htmlcov/index.html
uv run coverage run -m pytest && uv run coverage report
```

Also run, each as its own option: `-q`, `-v`, `--collect-only -q`, `--durations=3`, `--ff`.

Real failure output; this is why `pytest.approx` exists:

```
>       assert cumulative([0.1, 0.1]) == pytest.approx(0.20)
E       assert 0.2100000000000002 == 0.2 ± 2.0e-07
FAILED tests/test_a.py::test_two_fails - assert 0.2100000000000002 == 0.2 ± 2...
========================= 2 failed, 2 passed in 0.29s ==========================
```

The coverage table lists per file `Stmts  Miss  Branch  BrPart  Cover  Missing` (e.g. `86%   33-34, 54-55`); below
`fail_under` pytest prints `FAIL Required test coverage of 90.0% not reached. Total coverage: 86.89%` and exits 1. [local]

- Exit codes: 0 pass, 1 failures, 4 config/usage error, 5 no tests collected (a file `checks.py` with
  `def check_something()` collects nothing). [local]
- pytest-cov 7.0 removed its own subprocess measurement and needs coverage >= 7.10.6.
  [source: https://pytest-cov.readthedocs.io/en/latest/changelog.html] coverage.py uses the `sysmon` core by
  default on Python 3.14. [source: https://coverage.readthedocs.io/en/latest/config.html]
- Hypothesis in one example. The property "max drawdown never crashes for prices >= 0" failed at once with
  `ZeroDivisionError` and the shrunk report `Failing test case: test_max_drawdown_never_crashes(series=[0.0],)`:
  a real bug in the demo package. It writes `.hypothesis/`. [local]

## 6. pre-commit (and prek)
### 6.1 Facts
- pre-commit 4.7.0. Since 4.0 the stage names are `pre-commit`, `pre-push`, `pre-merge-commit` (the old
  `commit` / `push` are deprecated; `pre-commit migrate-config` rewrites them). 4.4 added `language:
  unsupported` as an alias of `language: system`, which "will eventually be deprecated"; both work in 4.7.0
  and in prek. [source: https://raw.githubusercontent.com/pre-commit/pre-commit/main/CHANGELOG.md] [local]
- `pre-commit sample-config` still prints `rev: v3.2.0`; current is v6.0.0. Run `pre-commit autoupdate`
  afterwards (seen: `updating v4.6.0 -> v6.0.0`, `updating v0.15.0 -> v0.17.5`). [local]
- Current revs [local: `git ls-remote --tags`]: pre-commit-hooks `v6.0.0`; ruff-pre-commit `v0.17.5`;
  conventional-pre-commit `v4.5.0`; gitleaks `v8.30.1`; detect-secrets `v1.5.0` (2024); nbstripout `0.9.2`;
  uv-pre-commit `0.13.9`; mirrors-mypy `v2.4.1`.
- ruff-pre-commit hook ids are `ruff-check` and `ruff-format`; `ruff` is labelled "legacy alias" in the
  manifest. `ruff-check --fix` must come before `ruff-format`. `ruff-format` now covers `markdown` too.
  [local: cloned manifest] [source: https://github.com/astral-sh/ruff-pre-commit]
- The Ruff version in `.pre-commit-config.yaml` (`rev`) and the one in `uv.lock` are independent: bump both.

### 6.2 Install and daily use (all run)

```
uv add --dev pre-commit
uv run pre-commit install --install-hooks   # writes .git/hooks/pre-commit and commit-msg
uv run pre-commit run --all-files           # first run 59 s here (builds hook environments), later 0.9 s
uv run pre-commit run ruff-check --all-files
uv run pre-commit autoupdate
SKIP=mypy git commit -m "docs: ..."         # skip one hook once
git commit --no-verify                      # skip all hooks; the emergency exit, teach it honestly
```

- Use the dev dependency, not `uvx`. The hook script stores the absolute path of the Python that installed
  it: `<project>/.venv/bin/python` with `uv run pre-commit install`, but `.../uv-cache/archive-v0/<hash>/bin/python`
  with `uvx pre-commit install`, which vanishes when the uv cache is cleaned. After moving the project folder
  or rebuilding `.venv` elsewhere, rerun the install. [local]
- When hooks change files the commit stops (`ruff check....Failed` / `- files were modified by this hook` /
  `Found 3 errors (2 fixed, 1 remaining).`); `git status` shows `AM`. Review, `git add`, commit again. [local]
- **`default_stages: [pre-commit]` is needed** once the commit-msg hook type is installed. Without it every
  hook that declares no stage ran a second time in the commit-msg stage. [local]
- Conventional Commits hook (types: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test).
  Accepted: `feat(returns): add sortino ratio`, `fix!: ...`, `Fix: ...`, `docs: 更新中文说明`, merge commits.
  Rejected: `first commit`, `update readme`, `wip: something`, `feat:missing space`. On rejection it suggests
  `git commit --edit --file=.git/COMMIT_EDITMSG`. [local]
- The local mypy hook works, and a `stages: [pre-push]` pytest hook ran with `--hook-stage pre-push`. Many
  teams keep hooks to fast file-level checks and leave mypy and pytest to `make check` and CI. Inside the
  Claude sandbox an `entry: uv run ...` hook needs fact 2.1. [local]

### 6.3 Secrets, large files, notebooks
- `detect-private-key` only finds key headers: it flagged a fake RSA key file, not an AWS key or a GitHub
  token in a `.py` file. `check-added-large-files` (default 500 kB) blocked an 800 kB file. [local]
- **A notebook with embedded outputs can pass 500 kB** and is then blocked. The
  `nbstripout` hook (0.9.2) cut a 684 kB test notebook to 0.4 kB, after which the size check passed, but it
  empties the outputs in the working file. `nbstripout --install` (a git filter) keeps them locally; it stores
  an interpreter path and failed when installed from an ephemeral `uv run --with` environment. The course has
  to choose a notebook policy before the first notebook commit. [local]
- gitleaks README: "Gitleaks is feature complete"; future releases are security patches; the maintainer is
  moving to Betterleaks (v2 in development). Hooks: `gitleaks` (`language: golang`, builds from source),
  `gitleaks-docker`, `gitleaks-system`. **Not run here**: the Go toolchain and module downloads failed in the
  sandbox. [source: https://github.com/gitleaks/gitleaks] [local: manifest, failed install]
- detect-secrets v1.5.0 installed and ran on Python 3.14 and found the fake AWS key, GitHub token and private
  key. On the AWS-shaped key **it tried to connect to `sts.amazonaws.com`** (its verification feature; the
  sandbox blocked it; the key was AWS's documentation example). Its README lists `--no-verify` (not run).
  [local] [source: https://github.com/Yelp/detect-secrets]
- Baseline for the first hook lesson: `detect-private-key` + `check-added-large-files`. Add a real scanner
  when the learner gets a remote, and say that the usual choice (gitleaks) is in maintenance mode.

### 6.4 prek
- prek 0.5.11 (2026-11-16): Rust single binary, "drop-in alternative to pre-commit"; its README lists
  CPython, FastAPI, Ruff, Airflow, Home Assistant among users; optional native `prek.toml`.
  [source: https://github.com/j178/prek]
- It ran the unchanged `.pre-commit-config.yaml`: first run 5.6 s (pre-commit: 59 s), warm 0.3 s (0.9 s), one
  measurement each. It builds Python hook environments with uv and did not hit the pip TLS failure.
  `uv add --dev prek`, `uv run prek run --all-files`, `prek install`, `prek list`, `prek autoupdate` work. [local]
- Recommendation: teach the config file with `pre-commit`, because hook READMEs, error messages and search
  results use its commands; add one paragraph saying `prek` reads the same file.

## 7. Task runner

| Option | Install | Verified here | For a beginner | Against |
|---|---|---|---|---|
| **Makefile** | none: GNU Make 3.81 ships with the Command Line Tools | every target in 8.3 | language-neutral and found in most repositories; `make check` is a convention people recognise | TAB rule, `.PHONY`, `$$` |
| just 1.59.0 | `uv add --dev rust-just`, `uv run just` (or brew) | `just`, `just check`, `just test -k drawdown -q` | readable, `just --list`, passes arguments | one more tool and file |
| poethepoet 0.49.0 | `uv add --dev poethepoet`, `uv run poe` | `poe`, `poe check` (sequences in `[tool.poe.tasks]`) | lives in `pyproject.toml`, no tabs | Python-only habit |
| plain `uv run ...` | none | yes | nothing to learn | five commands to remember; humans and CI drift apart |

**Recommendation: Makefile** with one-line recipes. uv 0.13.5 has no task runner; `uv format` and `uv check`
are experimental single-purpose commands. Pitfalls reproduced [local]: spaces instead of a TAB give
`Makefile:2: *** missing separator.  Stop.`; a directory `test/` plus a non-`.PHONY` target gives
`make: `test' is up to date.`; the first failing step stops the chain (`make: *** [lint] Error 1`, exit 2;
`make -k` continues). `make -n check` prints the commands without running them;
`make test ARGS="-k drawdown -q"` passes options; `make check` took 2.3 s on the demo.

## 8. Verified reference files (in `<scratch>/demo/`; blank lines and header comments trimmed here)
### 8.1 `pyproject.toml`: Ruff (the pytest, coverage and mypy blocks are in 5.1 and 4.2)

```toml
[tool.ruff]
line-length = 88 # Ruff's default. The formatter wraps code to this width.

[tool.ruff.lint]
# Ruff >= 0.16 enables about 400 curated rules with no configuration at all.
# `extend-select` ADDS rule families on top of them; `select` would REPLACE them.
extend-select = [
    "E",   # pycodestyle: PEP 8 basics the defaults leave out (`== None`, `lambda` assignment)
    "N",   # pep8-naming: snake_case functions and variables, CapWords classes
    "D",   # pydocstyle: public functions and classes need a docstring
    "C90", # mccabe: warn when one function has too many branches
    "A",   # flake8-builtins: do not overwrite `list`, `sum`, `id`, ...
    "PT",  # flake8-pytest-style: consistent pytest idioms
    "PD",  # pandas-vet: pandas anti-patterns (`inplace=True`, `.values`, ...)
    "NPY", # NumPy rules: legacy `np.random.*`, aliases removed in NumPy 2
]
ignore = [
    "E501", # line length is the formatter's job; it cannot wrap long comments or strings
    "D100", # no docstring required at the top of every module
    "D104", # ... nor in every package `__init__.py`
    "D415", # allow a docstring summary that ends with the Chinese full stop
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D"] # tests do not need docstrings

[tool.ruff.format]
docstring-code-format = true
```

For a project that uses the `.venv.nosync` symlink add `extend-exclude = [".venv.nosync"]` under `[tool.ruff]` (see 2.6; verified in
`nosync-lab2`, not part of the demo file).

### 8.2 `.pre-commit-config.yaml`

```yaml
default_install_hook_types: [pre-commit, commit-msg]
default_stages: [pre-commit]
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: detect-private-key
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.5
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.5.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
  - repo: local          # optional; many teams leave this to `make check` and CI
    hooks:
      - id: mypy
        name: mypy (project environment)
        entry: uv run mypy
        language: system
        types: [python]
        pass_filenames: false
```

### 8.3 `Makefile` (every recipe line starts with a TAB)

```make
.DEFAULT_GOAL := help
.PHONY: help install format lint typecheck test cov check hooks clean
help: ## Show this help
	@grep -E "^[a-z-]+:.*## " $(MAKEFILE_LIST) | awk -F ":.*## " '{printf "  make %-10s %s\n", $$1, $$2}'
install: ## Create .venv and install all dependencies from uv.lock
	uv sync
format: ## Auto-fix lint findings, then format the code
	uv run ruff check --fix
	uv run ruff format
lint: ## Check lint rules and formatting without changing files
	uv run ruff check
	uv run ruff format --check
typecheck: ## Run the mypy type checker
	uv run mypy
test: ## Run the tests (extra options: make test ARGS="-k drawdown -x")
	uv run pytest $(ARGS)
cov: ## Run tests with a coverage report
	uv run pytest --cov
check: lint typecheck cov ## Everything CI runs: lint + types + tests with coverage
hooks: ## Install the git hooks (once per clone)
	uv run pre-commit install
clean: ## Remove caches and coverage output
	rm -rf .ruff_cache .mypy_cache .pytest_cache .hypothesis htmlcov .coverage
```

### 8.4 `.editorconfig`

```ini
root = true
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4
[*.{yml,yaml,json}]
indent_size = 2
[*.md]
trim_trailing_whitespace = false
[Makefile]
indent_style = tab
```

- Resolved with the reference Python core (`uvx --from editorconfig editorconfig <absolute path>`): `.py`
  4 spaces, `.yaml` 2 spaces, `Makefile` tab, `.md` keeps trailing whitespace. [local]
- Spec 0.17.2 has nine keys (the seven used above plus `tab_width`, `spelling_language`); `max_line_length` is
  not among them. Comments are whole lines only; later sections and closer files win; `root = true` stops the
  upward search. [source: https://spec.editorconfig.org/index.html]
- Built in: PyCharm/JetBrains, GitHub, Vim, Neovim, Xcode; VS Code and Sublime need a plugin.
  [source: https://editorconfig.org/] It only advises editors; `ruff format` and the whitespace hooks enforce.

### 8.5 `.gitignore` lines these tools need
`__pycache__/`, `*.py[cod]`, `.venv`, `.venv.nosync/`, `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`,
`.hypothesis/`, `.coverage`, `.coverage.*`, `htmlcov/`, `.DS_Store`. [local: `git status --ignored`]

## 9. What changed compared with older tutorials
1. Ruff with no configuration now means about 400 rules, not E and F (0.16.0). "Ruff only checks E and F by
   default" is wrong today, and `select = ["E", "F"]` now reduces coverage.
2. Ruff: `ruff format` touches Markdown code blocks and notebooks; hook id `ruff` became `ruff-check`;
   `# ruff: ignore[...]`, `# ruff: disable/enable[...]`, `--add-ignore` exist next to `# noqa`; fix diffs are
   printed by default; `ruff-lsp` is gone (0.17.0); rule names and categories are arriving in preview.
3. Selecting the whole `RUF` family or `ALL` floods Chinese text with RUF001-003.
4. With a Python 3.14 target the formatter writes `except A, B:` without parentheses.
5. mypy is 2.x: new defaults, native parser, no Python 3.9. The NumPy mypy plugin is deprecated. Hints that
   say `pip install <stubs>` or `mypy --install-types` become `uv add --dev <stubs>`.
6. ty is beta, not 1.0; Pyrefly reached 1.0 in May 2026.
7. pytest 9: `[tool.pytest]` with TOML types and `strict = true`; `[tool.pytest.ini_options]` is the
   compatibility form and cannot be mixed in. `pytest.ini`, `setup.cfg`, `tox.ini`, `.coveragerc`, `mypy.ini`,
   `.flake8` are unnecessary: one `pyproject.toml` configured all four tools here.
8. pytest-cov 7 dropped subprocess measurement; coverage uses `sys.monitoring` on 3.14.
9. pre-commit: stage names changed in 4.0; `sample-config` revs are years old; gitleaks is in maintenance
   mode; prek is a widely used drop-in.
10. uv ships experimental `uv format` and `uv check`; `uv format` did not use the project's pinned Ruff.

## 10. Beginner pitfalls, ranked by how likely a beginner on a Mac hits them (a judgement, not a measurement)
1. `git commit` fails on gpg signing before any hook runs (2.3).
2. `ruff` instead of `uv run ruff` gives a different version (2.4).
3. The first `pre-commit` run from inside Claude Code fails on cache directory, proxy or TLS (2.2).
4. Hooks rewrite files and the commit "fails"; the fix is `git add` and commit again (6.2).
5. Notebooks over 500 kB are rejected by `check-added-large-files` (6.3).
6. Chinese punctuation and docstrings trigger RUF001-003, D415, E501 (3.5).
7. mypy prints `Success` on unannotated code; `float ** float` and `np.sqrt()` are `Any` (4.3).
8. Missing type information: pandas needs `pandas-stubs`; a library with neither stubs nor `py.typed` needs a
   per-module override (4.2, 4.3).
9. `pd.Series[float]` annotations crash at import on Python 3.12 (4.3).
10. `ruff format` neither sorts imports nor fixes lint; `ruff check --fix` does not reflow lines (3.2).
11. `--unsafe-fixes` can change behaviour (B006 rewrites the default argument): read the diff.
12. Makefile recipes need a TAB; targets need `.PHONY` (7).
13. pytest collects nothing unless files and functions are named `test_*` (exit 5); floats need `approx`.
14. Mixing `[tool.pytest]` with `[tool.pytest.ini_options]`, or writing `addopts` as a string (5.1).
15. `default_stages` missing once a commit-msg hook is installed (6.2).
16. Reading a coverage percentage as "tested"; setting `fail_under` high on day one.

## 11. Recommendations for the course
Order, one visible habit per step and never two new tools in one lesson:
1. **Format**: `uv add --dev ruff`, `uv run ruff format --diff`, then `uv run ruff format`. Immediate, safe,
   visual. Commit before and after so the change is reviewable.
2. **Lint with no configuration**: `uv run ruff check`, read three findings with `ruff rule <code>`, apply
   `--fix`, discuss one `--unsafe-fixes` diff. Suggestion (not measured on a public project): the learner's own
   project, if any, makes a good first exercise.
3. **Tests**: first test of a pure function, `pytest.approx`, `parametrize`, then `tmp_path`, `monkeypatch`,
   `capsys`, then `--cov` as a flashlight. Introduce `fail_under` late and low.
4. **Types**: `uv add --dev mypy pandas-stubs`, strict from the start, a per-module override for any untyped
   library (4.2), `float(...)` around NumPy scalars.
5. **One command**: `make check`, with the statement that CI will run exactly this.
6. **Hooks**: hygiene hooks and Ruff first; the commit-msg hook when Conventional Commits are introduced;
   the notebook policy before the first notebook commit.
7. **Stricter lint**: add the `extend-select` families one at a time (E, N, D, then PD and NPY), one commit each.

Skip or postpone: Black/isort/flake8/pylint setup, tox/nox, `select = ["ALL"]`, `uv format` / `uv check`, ty
as the gate, pytest plugins beyond pytest-cov, parallel test runs, mutation testing, mypy plugins.

Sensible defaults: line length 88; Google docstrings; mypy strict; `strict = true` in pytest; branch coverage;
tool versions pinned through `uv.lock` and upgraded deliberately together with `pre-commit autoupdate`
(`uv lock --upgrade-package ruff` is the usual command; not run here [memory]).

Plain-Chinese analogies that match what the tools were seen to do:
- Formatter: 自动排版。内容不变，只统一版式；谁写的代码看起来都一样。
- Linter: 拼写和语法检查的红色波浪线。`ruff rule B006` 就是点开波浪线看解释。
- 安全修复 / 不安全修复: 改错别字 与 改句子意思 的区别；后者必须自己读一遍 diff。
- Type checker: 量纲检查。把"价格"和"收益率"相加之前先核对单位；程序还没运行就能发现。
- 测试: 给函数"对答案"。`parametrize` 是同一道题换几组数字；fixture 是实验前摆好的器材。
- `pytest.approx`: 小数比较要留误差，像对账时允许分位差。
- 覆盖率: 手电筒照到了哪里；照到不等于检查过。
- pre-commit: 提交前的安检门，像下单前的风控检查；`--no-verify` 是应急通道，用了要说明原因。
- Makefile: 把一串命令存成快捷键；`make check` 就是"交卷前全部自查一遍"。
- `.editorconfig`: 团队的排版公约，编辑器自动遵守。
- `uv.lock` 里的工具版本: 全班用同一把尺子，换尺子要单独记一笔。

## 12. Not verified / open
- gitleaks and Betterleaks were not executed (Go toolchain and module downloads failed in the sandbox).
- Pyright itself was not run, only basedpyright 1.40.2 ("based on pyright 1.1.414").
- Whether iCloud skips `.cache.nosync`.
- VS Code / Pylance behaviour and editor plugins. [memory]
- Read about but not run: `ruff: disable/enable`, `ruff: file-ignore`, `extend-ignore-names`,
  `detect-secrets --no-verify`, `uv lock --upgrade-package`.
- Ruff's rule categories and rule names are preview features; how selections are written may change.
- Whether Ruff's `N802`/`N803` report Chinese identifiers: not checked on public or invented code.
- pytest 9.0.0 is dated 2025-11-05 in the changelog and 2025-11-08 on PyPI.

## 13. Primary sources read today
Ruff: astral.sh/blog/ruff-v0.16.0 and ruff-v0.15.0; BREAKING_CHANGES.md and CHANGELOG.md in astral-sh/ruff;
github.com/astral-sh/ruff/releases; docs.astral.sh/ruff (configuration, default-rules, linter, formatter,
tutorial); github.com/astral-sh/ruff-pre-commit. Types: mypy.readthedocs.io changelog; github.com/astral-sh/ty;
docs.astral.sh/ty and its typing FAQ; astral.sh/blog/ty; github.com/microsoft/pyright/releases;
github.com/pandas-dev/pandas-stubs. Tests: docs.pytest.org (changelog, customize, goodpractices);
pytest-cov changelog; coverage.readthedocs.io config. Hooks: pre-commit CHANGELOG.md;
github.com/pre-commit/pre-commit-hooks; gitleaks, betterleaks, Yelp/detect-secrets, j178/prek READMEs;
docs.astral.sh/uv/guides/integration/pre-commit. Other: spec.editorconfig.org; editorconfig.org; pypi.org JSON API.
Added 2026-11-20 (to replace private measurements): docs.astral.sh/ruff rule pages for RUF002 and D415, the
`line-length` and `lint.allowed-confusables` settings, the formatter's "Conflicting lint rules"; Ruff's
`ends_with_punctuation.rs` on GitHub; mypy "Running mypy and managing imports" (missing library stubs).
