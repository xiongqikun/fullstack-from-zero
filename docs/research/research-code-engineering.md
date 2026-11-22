# Brief: engineering norms for research / analysis code (backtest flavour)

Topic key: `research-code-engineering` · verified 2026-11-19 on the reference Mac (plan G7) (macOS 27.2.1 arm64)
Tags: **[local]** = I ran it here today · **[source: URL]** = read in a primary source today · **[memory]** = not verified.
Audience: lesson builders. Everything below is raw material, not learner-facing text.

---

## 0. What was verified and how

- Scratch project `example/minibt/` (uv 0.13.5, `uv init --package`, Python 3.14.9): pandas 3.1.1, numpy 2.5.5,
  pytest 9.2.0, hypothesis 6.170.15, pandera 0.36.0, jupytext 1.19.6, nbstripout 0.9.2, nbqa 1.10.0,
  papermill 2.7.0, marimo 0.25.2, nbconvert 7.17.2, nbclient 0.11.0, nbmake 1.5.5, nbdime 4.0.4, ipykernel 7.4.0.
  All installed on 3.14 without trouble [local]. ruff 0.17.2 is the global uv tool; git 2.54.0; GNU Make 3.81.
- The running example ends at: 40 tests green on Python 3.14 **and** 3.12 (`uv run --isolated --locked --python 3.12 pytest`),
  `ruff check` + `ruff format --check` clean, two CLI runs byte-identical (same SHA-256 for `metrics.json`, `daily.csv`),
  identical across 3.12/3.14 under the same `uv.lock` [local].
- Measurements of a private project are not published (rule G10a); this brief keeps only conclusions with a
  public basis. Advice that has no public basis is marked "suggestion (not measured on a public project)".
- Web (all fetched today): the handbooks/guides named in section 4; docs of ruff, jupytext, nbstripout, nbQA,
  papermill, marimo, pandera, DVC, MLflow, uv, NumPy random, pandas 3.0 whatsnew, FRED; two papers read from PDF.
  Release dates come from the PyPI JSON API [source: https://pypi.org/pypi/<name>/<version>/json].

---

## 1. TL;DR for course designers

1. **Suggestion (not measured on a public project): a learner's existing analysis project, if any, can be a better
   starting point than "one long notebook".** The gaps this topic closes are the ones the public guides in section 4
   name: raw files without provenance (CCDS "Raw data is immutable"; the Turing Way compendium), no tests, functions
   living inside notebooks (Good Research Code Handbook, /tidy), notebooks stored with their outputs (what nbstripout
   and jupytext exist for), editing code to control behaviour (Wilson et al. 2017, "Do not comment and uncomment
   sections of code..."), no record of which code produced which result (Good Research Code Handbook, /pipelines).
2. **Old tutorials now mislead on four big things**: ruff's default rule set (59 -> 413 rules in 0.16.0, 2026-07-23),
   pandas 3 (Copy-on-Write always on, `str` dtype, `datetime64[us]`, `'M'`/`'H'` aliases removed, `pct_change` no longer
   forward-fills), pandera's import path (`import pandera.pandas as pa`), and "use conda + setup.py + `pip install -e .`"
   (uv does the editable install by itself). Details in section 2.
3. **`ruff check` on `.ipynb` is a kernel-free approximation of "Restart & Run All"**: F821 flagged both a variable used
   before its defining cell and a variable whose cell was deleted [local]. It does *not* look at execution counters; a
   short script does (`example/minibt/scripts/check_notebooks.py`, about 35 lines) [local].
4. **In the Claude Code sandbox no Jupyter kernel can start** (`PermissionError: [Errno 1] Operation not permitted` on
   socket bind) -> `jupyter nbconvert --execute`, `papermill`, `pytest --nbmake`, `marimo export html` all fail when the
   assistant runs them [local]. Plain `python notebook.py` (jupytext percent format or marimo) works. Design lessons so that
   everything that must be reproducible runs as a script / CLI; keep "execute the .ipynb" as a human-terminal step.
5. **A missing `.shift(1)` produced a mean Sharpe of 7.18 on pure random walks** (honest version: 0.03) [local]. This single
   demo plus a 15-line "future-perturbation" test is the highest-value backtest lesson.
6. **Best-of-58 parameter pairs on noise: in-sample Sharpe +0.44, out-of-sample +0.01** [local]; the published formula
   (Bailey et al. 2014) was reproduced numerically: 45 trials on 5 years, or 7 trials on 2 years, give an expected best
   Sharpe of ~1.0 with zero true edge [local + source]. Hence the experiment log that records *every* run.
7. **A public FRED FX series contains the calendar lesson**: `DEXCHUS` (USD/CNY) repeats the same value across Chinese
   holidays (183 exact repeats since 2015, clustered in Feb/May/Oct; 7.1928 printed five days running in Feb 2024) and
   has 516 empty rows (e.g. 2024-02-19, a US holiday) [local, on a downloaded copy].
8. **Sensible defaults that all worked here**: TOML config read with stdlib `tomllib` into a frozen dataclass; `argparse`
   CLI exposed through `[project.scripts]`; sidecar `*.meta.json` with SHA-256 next to each raw file; run folder named
   `<commit7>[-dirty]_<confighash>`; one-line-per-run `experiments.csv`; `np.random.default_rng(seed)` created once and
   passed down; returns in decimals, costs in bps, units in names.
9. **Teach, in this order**: hidden state & run-all -> move one function to `src/` -> first known-answer test -> the
   look-ahead test -> config + CLI -> manifest + experiment log -> stripping/pairing notebooks. **Awareness only**: marimo,
   papermill, nbQA, DVC, MLflow, Docker, Snakemake, the `ccds` generator.
10. **Possible machine blocker outside this topic but fatal for the first Git lesson**: if global git config has
    `commit.gpgsign=true` with `gpg.program=gpg` and no `gpg` is installed (section 3), every `git commit` fails with
    `error: cannot run gpg: No such file or directory` / `fatal: failed to write commit object` [local]. My throwaway
    repos used repo-local `git config commit.gpgsign false`. The learner must choose (install gpg / SSH signing /
    signing off); do not silently change the global config.
11. **`ruff format .` rewrites Python inside Markdown** (fences tagged `python`/`py`/`pycon`) [local]. A Markdown-based
    course that shows intentionally messy "before" code must exclude `*.md` from the formatter or tag those blocks `text`.

---

## 2. What changed recently (older tutorials vs today)

| Topic | Older tutorials say | Verified today |
|---|---|---|
| Ruff default rules | "defaults are `E4,E7,E9,F`; add `I`,`B`,`UP` yourself" | 0.16.0 (2026-07-23) enables 413 rules by default, "up from 59"; revert with `select = ["E4","E7","E9","F"]` [source: https://astral.sh/blog/ruff-v0.16.0]. Measured in 0.17.2: **407** enabled with no config, incl. I001, B006, B018, SIM115, UP017, BLE001, TRY004, RUF100; **not** enabled: E501, E402, E711, S101, PLR2004, T201, all `NPY`, all `PD`, most `DTZ` (only DTZ002/003/004), `D100`, `ANN*` [local]. |
| Ruff + notebooks | "use nbQA to run linters on notebooks" | `.ipynb` is "linted and formatted by default on version 0.6.0 and higher" [source: https://docs.astral.sh/ruff/configuration/]. nbQA is only needed for tools without notebook support. |
| Ruff formats Markdown | n/a | 0.16 formats Python code blocks inside `*.md`; `*.md` is in the default include list [source: ruff-v0.16.0 blog; local `--show-settings`]. Reproduced on 0.17.2: `ruff format` rewrote fences tagged `python`, `py`, `pycon` and `python title="x.py"`; fences tagged `text` or untagged were left alone; `ruff check` ignores `.md`. Opt out with `[tool.ruff.format] exclude = ["*.md"]` (or `extend-exclude`) [local]. **A Markdown lesson that shows deliberately messy "before" code in a `python` fence will be silently tidied by `ruff format .`** |
| pandas CoW | "`SettingWithCopyWarning`, add `.copy()`" | pandas 3.0.0 (2026-01-21): CoW always on; chained assignment does nothing and warns `ChainedAssignmentError`; option `mode.copy_on_write` deprecated (`Pandas4Warning`) [source: https://pandas.pydata.org/docs/whatsnew/v3.0.0.html; local]. |
| pandas strings | "string columns are `object`" | default dtype is `str` (`StringDtype(storage='python', na_value=nan)` when pyarrow is absent) [local]. |
| pandas datetimes | "always `datetime64[ns]`" | `date_range`, `to_datetime`, `read_csv(parse_dates=)` all give `datetime64[us]`; `idx.astype("int64")` is now microseconds (1000x smaller), `Timestamp.value` still ns [local; whatsnew]. |
| pandas offsets | `resample("M")`, `freq="H"` | `'M','Q','Y','BM','H','T'` raise `ValueError`; use `'ME','QE','YE','BME','h','min'` [local]. |
| `pct_change` | silently pads NaN | `fill_method` must be `None`; a NaN price gives NaN returns on that day and the next [local]. |
| pandas deps | needs `pytz`, `six` | resolved set for pandas 3.1.1 was only numpy, python-dateutil 4.0.0, tzdata [local]; parquet still needs pyarrow (`to_parquet` -> `ImportError`) [local]. |
| pandera | `import pandera as pa` | recommended `import pandera.pandas as pa` (module introduced in 0.24.0); top-level access emits a `FutureWarning` [source: https://pandera.readthedocs.io/en/stable/; local on 0.36.0]. |
| NumPy random | `np.random.seed(0)` | "we do recommend transitioning to `Generator`"; create with `default_rng(seed)` [source: https://numpy.org/doc/stable/reference/random/index.html]. Ruff rule NPY002 flags the legacy calls but is not on by default [local]. |
| Project setup | conda `environment.yml`, `setup.py` + `pip install -e .` (Good Research Code Handbook, 2021); conda preferred and `requirements.txt` in the tree (CCDS docs) | `uv init --package` + `uv add`; uv installs the project editable by default [source: https://docs.astral.sh/uv/concepts/projects/sync/]; here via a one-line `minibt.pth` in site-packages [local]. |
| CCDS | `cookiecutter <repo-url>` (v1) | v2 uses the `ccds` command from `cookiecutter-data-science` (latest 2.3.0, 2025-07-24); options include `uv` and `ruff` [source: https://cookiecutter-data-science.drivendata.org/]. Its printed tree still shows `requirements.txt` + `setup.cfg` for flake8. |
| Hypermodern Python | pyenv + Poetry + Nox + flake8 + black | the blog series is dated 2020-01-01 [source: http://blog.claudiojolowicz.com/posts/hypermodern-python-01-setup/]; the 2024 O'Reilly book covers uv/Ruff [secondary: search result]. Treat as history. |
| `sum()` of floats | "`sum([.1,.2,.3]) != sum([.3,.2,.1])`" | equal on 3.14 (compensated summation) [local]; pandas `Series.sum()` of the same numbers in another order still differed by 2.8e-14 [local] -> compare with tolerance. |
| Cache dirs in `.gitignore` | list `.pytest_cache`, `.hypothesis`, `.venv` | each of those now ships its own inner `.gitignore` containing `*` [local]. Listing them is harmless, not required. |

---

## 3. Machine / sandbox facts that touch this topic

- **Editable install vs iCloud.** The project is importable in notebooks because uv writes
  `.venv/lib/python3.14/site-packages/<pkg>.pth` (one line: the `src` path). Python 3.14 `site.py` skips `.pth` files that
  carry the macOS hidden flag. Reproduced: `chflags hidden minibt.pth` -> `ModuleNotFoundError: No module named 'minibt'`;
  `python -v` prints `Skipping hidden .pth file: ...`; `chflags nohidden` fixes it [local]. That iCloud Desktop sync sets
  this flag is reported, not re-observed today [memory]. A common workaround is
  `.venv -> .venv.nosync`.
- **Sandbox, when the assistant runs things** [local]: (a) kernels cannot bind ports (see TL;DR 4); IPC transport also
  failed (`Kernel died before replying to kernel_info`). (b) `~/.jupyter` does not exist and cannot be created -> jupytext
  CLI crashes with a long traceback ending in `PermissionError ... '/Users/<user>/.jupyter'` until
  `JUPYTER_CONFIG_DIR`, `JUPYTER_DATA_DIR`, `JUPYTER_RUNTIME_DIR`, `IPYTHONDIR` point into `$TMPDIR`. (c) marimo warns
  about `~/.config/marimo` unless `XDG_CONFIG_HOME` is redirected. (d) I always set `UV_CACHE_DIR="$TMPDIR/uv-cache"`
  as instructed (not tested without). Whether kernels start in the learner's own Terminal was not tested (it is the
  documented normal case). Allowing local port binding in the sandbox is a user setting
  (`sandbox.network.allowLocalBinding`) - their decision.
- `git init` already yields branch `main` because Xcode's bundled gitconfig sets `init.defaultBranch` [local].
- **Global git settings can change what lessons will show** [local]: `commit.gpgsign=true`, `gpg.format=openpgp`,
  `gpg.program=gpg` with no `gpg` installed -> commits fail (TL;DR 10). And a global `core.excludesfile` (for example
  `~/.gitignore_global`) may ignore `.DS_Store`, `._*`, `.idea/`, `*.swp`, `*.swo` and **`*.log`**: with such a file,
  `experiments.log` never appeared in `git status` of a fresh repo (`git check-ignore -v` names the global file and line)
  while `experiments.csv` did. Name lab logs `.csv`/`.md`.
- `uv init` chose Python 3.12 (`.python-version` = 3.12, `requires-python >=3.12`) although `python3` is 3.14.9; I pinned
  with `uv python pin 3.14` [local]. numpy 2.5.5 itself requires Python >= 3.12 [source: PyPI JSON].
- The assistant's safety check refused `cd <project> && rm -rf reports/*`; do not build exercises on such cleanups.

---

## 4. Primary sources: what each contributes

**Good Research Code Handbook** (Patrick Mineault, (c) 2021-2022; "for grad students, postdocs and PIs who do a lot of
programming as part of their research") [source: https://goodresearch.dev/]
- "one project = one paper = one folder = one git repository"; skeleton `data/ docs/ results/ scripts/ src/ tests/`
  [source: /setup]. Its tooling (conda, Python 3.8, `setup.py`, flake8/pylint/black) is outdated; the ideas are not.
- Notebooks: keep "IO, long-running pipelines, and functions and classes out of jupyter notebooks"; restart kernel and
  run all before committing; a notebook should run in "a minute or less"; jupytext for refactoring [source: /tidy].
- "Concentrate your IO in their own functions rather than sprinkling them throughout the code"; write pure functions;
  smells: magic numbers, globals, embedded configuration [source: /decoupled].
- Tests: "Good code yells loudly when something goes wrong"; "If something caused a bug, write a test for it"; start
  with inline `assert`, move to pytest; lesson bullets "Isolate numeric code", "Make numeric functions pure if
  practical" [source: /testing].
- Provenance: "A lightweight workaround is to record the git hash with each result"; command-line flags instead of
  editing variables; shell file / Makefile as executable documentation [source: /pipelines].

**The Turing Way** [source: https://book.the-turing-way.org/reproducible-research/...]
- Definitions (2x2 of same/different data x analysis): *reproducible* = "the same analysis steps performed on the same
  dataset consistently produces the same answer"; *replicable* = same analysis, different data; *robust* = same data,
  different analysis; *generalisable* = both differ [source: .../overview/overview-definitions]. Useful vocabulary: the
  course targets "reproducible" first; out-of-sample tests are about "replicable".
- Research compendium: "Files should be organized in a conventional folder structure; Data, methods, and output should
  be clearly separated; The computational environment should be specified"; raw data marked **read-only** [.../compendia].
- Backups: "2 or 3 copies of your files, stored on at least 2 different storage media, in different locations"
  [.../rdm/rdm-storage]. Make "uses the modification time of prerequisites to update targets only when needed" [.../make].

**Cookiecutter Data Science v2** [source: https://cookiecutter-data-science.drivendata.org/opinions/]
- "Raw data is immutable"; "Don't ever edit your raw data. Especially not manually. And especially not in Excel."
- "by default, the `data/` folder is included in the `.gitignore` file."
- "Notebooks are for exploration and communication, source files are for repetition"; naming
  `<step>-<ghuser>-<description>.ipynb` e.g. `0.3-bull-visualize-distributions.ipynb`; "Don't write code to do the same
  task in multiple notebooks"; refactor useful code into the package; `%load_ext autoreload` / `%autoreload 2`.
- "Data analysis is a directed acyclic graph"; "We prefer make"; secrets in `.env`, never committed.
- Tree: `data/{external,interim,processed,raw}`, `notebooks/`, `references/`, `reports/figures/`, `models/`, a module
  with `config.py dataset.py features.py plots.py modeling/` [source: README on GitHub]. Recommends `nbautoexport`.

**Scientific Python Development Guide** [source: https://learn.scientific-python.org/development/]
- Aimed at people with "a pile of scientific Python scripts or Jupyter notebooks that are becoming unwieldy"; tutorials
  go dev-environment -> module -> packaging -> test -> docs.
- Design principles worth quoting [.../principles/design/]: "I/O-related functions should only perform I/O";
  "If you can get away with writing functions processing existing datatypes like a DataFrame, do so"; "Overly
  permissive code can lead to very confusing bugs"; error messages should "Include what the wrong value was, what was
  wrong with it, and perhaps how it might be fixed". Process [.../principles/process/]: "No code is ever right the
  first (or second) time."
- `sp-repo-review` checks a repo against the guide: `pipx run 'sp-repo-review[cli]' <path>` [.../guides/repo-review/]
  (not run here).

**Wilson et al. 2017, "Good enough practices in scientific computing"** [source: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510]
- Box 1 items that map 1:1 onto lessons: "Save the raw data."; "Record all the steps used to process data.";
  "Decompose programs into functions."; "Give functions and variables meaningful names."; "Do not comment and uncomment
  sections of code to control a program's behavior."; "Provide a simple example or test data set."; "Put each project in
  its own directory"; "Name all files to reflect their content or function."; "Use a version control system."

**Tools** (what their own docs say; local results are in sections 6 and 9)
- **nbstripout 0.9.2** (released 2026-11-17): git filter, strips outputs at `git add`; the README says the filter is
  declared `required` [source: https://github.com/kynan/nbstripout].
- **jupytext 1.19.6**: its README advises versioning the `.py` notebook and says you "might exclude `.ipynb` files
  from version control (unless you want to see the outputs versioned!)" [source: https://github.com/mwouts/jupytext].
- **papermill 2.7.0**: tag a cell `parameters`; an `injected-parameters` cell is added after it
  [source: https://papermill.readthedocs.io/en/latest/usage-parameterize.html]. **nbQA 1.10.0**: any linter on notebooks.
- **marimo 0.25.2**: notebook stored as a `.py` file, reactive, "no hidden state", runs as a script; the same variable
  cannot be defined in two cells; no IPython magics [source: https://docs.marimo.io/ and /guides/coming_from/jupyter/].
- Awareness only, not installed: **DVC** ("Git for data": `.dvc` pointer files in git, data in a cache/remote;
  `uv tool install dvc`) [source: https://doc.dvc.org/start]; **MLflow Tracking** ("an API and UI for logging parameters,
  code versions, metrics, and output files"; local `mlruns` dir) [source: https://mlflow.org/docs/latest/ml/tracking/].

---

## 5. Repository layout, naming, and what goes into Git

Recommended target (a small evolution of a typical existing analysis project, not a new template):

```
project/
├── pyproject.toml  uv.lock  .python-version  README.md  Makefile(optional)
├── configs/            <- one TOML per experiment family (tracked)
├── data/
│   ├── raw/            <- immutable inputs exactly as downloaded (+ <file>.meta.json sidecars)
│   ├── interim/        <- optional
│   └── processed/      <- anything code can regenerate
├── notebooks/          <- 01_topic.ipynb (+ paired 01_topic.py if jupytext); thin: import, call, look
├── src/<package>/      <- all logic: data loaders, signals, backtest, metrics, provenance, cli
├── tests/              <- pytest; tests/golden/ for frozen expected numbers
├── reports/            <- generated: figures, run folders; experiments.csv is the lab notebook
└── scripts/ or experiments/  <- one-off runnable studies that import the package
```

Git rules verified in the example [local]:

```gitignore
data/raw/*
!data/raw/*.meta.json      # fingerprints ARE tracked even when the data is not
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep
reports/*
!reports/experiments.csv   # the experiment log is tracked
.env
.DS_Store
```

- Track: code, configs, `uv.lock`, tests, golden files, notebooks *without outputs* (or the paired `.py`), the raw-data
  manifest, the experiment log, small final figures only if deliberately published.
- Do not track: `.venv`, raw/processed data by default, generated run folders, secrets, notebook outputs.
- GitHub warns at 50 MiB and blocks at 100 MiB per file
  [source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github].
  So if the raw data is only a few MB, committing raw snapshots is technically fine and is the simplest "data
  versioning" for a beginner - *if* the repo is private and the data terms allow it. Otherwise track only the manifest. DVC is unnecessary at this size.
- Notebook naming: `01_topic.ipynb` (two-digit order + snake_case topic) is fine for a solo
  project; CCDS's initials segment only matters in teams.
- A hash manifest also exposes sync-conflict duplicates such as the "file 2.csv" copies iCloud can leave in `data/raw` [memory].

---

## 6. Notebook hygiene

**The rule set** (sources in section 4): notebooks narrate and display; modules compute. A notebook cell should mostly
be `from pkg import f` -> `result = f(config)` -> look. Each notebook starts with a question and an expectation written
before running, and ends with a finding. Before committing: restart, run all, runs in about a minute.

**Stale imports are hidden state too** [local, IPython 9.18.1 driven in-process]: after `import mymod`, editing
`mymod.py` (252 -> 260) left the running session returning 252; after `%load_ext autoreload` + `%autoreload 2`
(the snippet CCDS recommends) the next edit (-> 365) was picked up. Without it, "I fixed the function but the notebook
still shows the old number" is guaranteed once logic moves into `src/`.

**Ruff on notebooks** [local, ruff 0.17.2]

```
$ ruff check --output-format concise hidden_state.ipynb      # no extra tool, no kernel (excerpt; comments are mine)
hidden_state.ipynb:cell 2:1:37: F821 Undefined name `scale`     <- defined in a LATER cell (run out of order)
hidden_state.ipynb:cell 4:1:30: F821 Undefined name `window`    <- its defining cell was deleted
$ ruff check --fix demo.ipynb ; ruff format demo.ipynb           # outputs and execution counts were preserved
```
- Location format is `file.ipynb:cell N:line:col`, where N counts **all** cells (markdown included). nbQA prints
  `cell_N` counting **code cells only** - the same cell was "cell 3" for ruff and `cell_2` for nbQA.
- `%matplotlib inline` and `!ls` lines are accepted. B018 (bare expression) skips the last expression of a notebook
  cell [source: https://docs.astral.sh/ruff/rules/useless-expression/], but the same code as a jupytext `.py` file *is*
  flagged -> `per-file-ignores = {"notebooks/*.py" = ["B018"]}` [local].
- Notebook-only relaxations go in `[tool.ruff.lint.per-file-ignores] "*.ipynb" = [...]`; exclude from formatting only
  with `[tool.ruff.format] exclude = ["*.ipynb"]` [source: ruff configuration docs].
- Research-relevant rule families are opt-in: `extend-select = ["NPY", "PD"]` gave `NPY002` for `np.random.seed`,
  `PD002` for `inplace=True`, `PD011` for `.values` [local].
- marimo-generated files trip `PLR1711` (useless `return`) under the new defaults [local].

**nbstripout** [local]

```
$ uv add --dev nbstripout
$ .venv/bin/nbstripout --install --attributes .gitattributes   # once per clone (`uv run nbstripout ...` is the same binary)
$ cat .gitattributes
*.ipynb filter=nbstripout
*.zpln filter=nbstripout
*.ipynb diff=ipynb
$ .venv/bin/nbstripout --status     # exit 0 when installed, 1 when not
```
- Result: working copy keeps outputs; committed blob has `outputs=0 exec_counts=[None, None, None]`.
- The filter command stored in `.git/config` is an **absolute path to the venv's python** and is `required = true`.
  Two different failure modes, both reproduced: (a) filter configured but its path gone (venv moved/recreated) ->
  `git add` aborts with `fatal: demo.ipynb: clean filter 'nbstripout' failed` (exit 128); (b) **fresh clone**:
  `.gitattributes` arrives, `.git/config` does not, `nbstripout --status` exits 1 - and `git add` + `git commit`
  succeed silently **with the outputs inside the committed blob**. The protection is per clone; (b) gives no warning.
- After merely re-running a notebook, `git status` shows ` M nb.ipynb` while `git diff` is empty and the cleaned file
  hashes to the same blob as the index [local]; `git add nb.ipynb` clears it and stages nothing. (Cause, as far as I
  recall: git treats a changed file size as "modified" before consulting the filter [memory].)
- `git checkout -- nb.ipynb` gave back the stripped version: local outputs were gone (smudge is `cat`). The same must
  hold for `git restore` / `stash` / switching branches, which I did not run.
- Guard against (b): `nbstripout --verify notebooks/*.ipynb` exits 0 when nothing would be stripped, 1 (naming the
  file, modifying nothing) when any notebook still has outputs [local]. Note it inspects the *working copy*, so it
  belongs in CI / a pre-push check on a fresh checkout, not in a local `make check` where outputs legitimately exist.
  The pre-commit hook (`rev: 0.9.2`, `id: nbstripout`) instead modifies the working copy
  [source: https://github.com/kynan/nbstripout].

**jupytext** [local]

```
$ uv run jupytext --to py:percent nb.ipynb                        # one-off conversion
$ uv run jupytext --set-formats ipynb,py:percent nb.ipynb         # pair (writes metadata.jupytext.formats)
$ uv run jupytext --sync nb.ipynb                                  # after editing either file
# project-wide default pairing, no per-notebook metadata needed:
[tool.jupytext]
formats = "ipynb,py:percent"
```
- Magics are commented out in the `.py` (`# %matplotlib inline`), so the script runs with plain `python`.
- `uv run python notebooks/01_x.py` is the kernel-free "run everything top to bottom" (works in the sandbox).
- With pairing, commit the `.py`, and either ignore `.ipynb` or strip it.

**papermill** [local]: `papermill in.ipynb out.ipynb -p window 60 -p seed 7 --prepare-only` injected a cell tagged
`injected-parameters` and recorded `{'seed': 7, 'window': 60}` in notebook metadata; `--help-notebook` lists inferred
parameters. A notebook without `kernelspec` metadata fails ("No kernel name found..."; with `-k python3`: "No language
found"); `jupytext --set-kernel python3` fixed both. Real execution not verifiable here.
**marimo** [local]: `marimo convert nb.ipynb -o nb.py` produced `@app.cell` functions; `python nb.py` ran it;
`marimo check` passed; `marimo export ipynb` worked; `marimo export html` needs a socket (failed in sandbox).

**Decision for the course** (a judgement call, both options verified): 
- Option A, smallest change to current habits: keep `.ipynb` + `ruff check` + nbstripout filter. Weakness: per-clone
  setup with a silent failure mode (b) and an absolute venv path in `.git/config`.
- Option B, more robust once understood: jupytext pairing via `[tool.jupytext]`, commit the `.py`, put `*.ipynb` in
  `.gitignore`. Nothing can leak outputs, diffs are plain Python, and the assistant can lint and *run* the notebook
  in the sandbox. Cost: two files per notebook and a `--sync` habit (JupyterLab integration not tested here).
- For a solo learner on one machine either works; I would teach A first (one command, immediate before/after diff),
  then B as the upgrade. marimo = a 10-minute awareness demo of "no hidden state by construction". Skip nbQA and
  papermill for now: with a CLI and config files, "parameterised runs" do not need notebooks at all.

---

## 7. Reproducibility checklist (each item exercised in the example)

| Concern | Norm | Verified evidence |
|---|---|---|
| Environment | commit `uv.lock`; run with `--locked` in automation | after hand-editing `pyproject.toml`: `uv lock --check`, `uv run --locked`, `uv sync --locked` all exit 1 with "The lockfile at `uv.lock` needs to be updated" [local]. `--frozen` uses the lock without checking [source: uv sync docs]. 139 packages locked for this small example. |
| Randomness | one `rng = np.random.default_rng(seed)`, seed in config, pass `rng` down; never a global seed | identical bootstrap CI on every run; `test_same_inputs_same_numbers` asserts exact equality [local]. NumPy only promises the same stream for the same build/environment; streams may change in feature releases [source: https://numpy.org/doc/stable/reference/random/compatibility.html] -> the lockfile is part of the seed. |
| Hidden ordering | `sorted()` for sets and directory listings | 4 fresh processes printed 4 different orders for a set of 5 currency codes; `os.listdir` returned `['c_2023.csv','b_2024.csv','a_2025.csv','10.csv','9.csv','Z.csv']` [local]. |
| Float noise | compare with tolerance (`pytest.approx`, `np.testing.assert_allclose`, `pd.testing.assert_frame_equal(rtol=...)`) | reordered pandas sum differed by 2.8e-14 [local]. |
| Raw data | immutable; sidecar with source, date, rows, sha256; loader verifies the hash | editing one number in the CSV -> `ValueError: ... Raw data is immutable` [local]. |
| Config | all knobs in TOML; unknown/missing keys are errors; unit sanity checks | `slow_windw = 99` rejected; `cost_bps = 100` rejected as "percent instead of basis points?" [local]. |
| Provenance | every result folder has `manifest.json`: git commit, dirty flag, config + hash, data sha256, python, platform, package versions, command | see excerpt in section 10 [local]. |
| Dirty tree | results you keep must come from a commit: `--require-clean` | exit 2 "uncommitted changes; commit first" [local]. |
| Experiment log | append one CSV row per run, including failures and boring runs | 12 rows after the session: all 10 runs of the base config (5 commits plus one pre-git run, 3 of them dirty) logged Sharpe 0.2465; both 5 bp runs 0.2207 [local]. |
| Pipeline | one command reproduces everything (`make run` or the CLI) | GNU Make 3.81: second `make run` -> "Nothing to be done"; after `touch configs/base.toml` it reran [local]. |
| Stored tables | CSV round-trips floats exactly but loses dtypes/freq (dates come back as `str` without `parse_dates`) | [local]. Parquet would keep dtypes [memory] but needs pyarrow: `to_parquet` raised `ImportError` here [local]. |

Two design traps I hit while building the example (worth turning into exercises):
1. Naming the run folder by config hash alone let a dirty run overwrite a clean run's folder. Fix: `<commit7>[-dirty]_<confighash>`.
2. A tracked experiment log makes the tree dirty after every run, so the next `--require-clean` run refused to start.
   Fix: exclude the output folder from the dirty check: `git status --porcelain -- . ":(exclude)reports"`.

Point-in-time note: FRED says "All data are subject to revision" and offers vintages through ALFRED
[source: https://fred.stlouisfed.org/series/DEXCHUS]; the API's real-time period "marks when facts were true or when
information was known until it changed", default "today" [source: https://fred.stlouisfed.org/docs/api/fred/realtime_period.html].
Consequence (reasoning from FRED's own statement, not a measurement): a loader that overwrites its saved copy on
every refresh, with no retrieval date or hash recorded, silently replaces the earlier vintage. Cheapest fix: save
the bytes as received plus a
sidecar (`url`, `retrieved_at`, `sha256`, `n_rows`, `last_observation`); refresh into a new dated file.

---

## 8. Backtest / research defences -> test, assertion or review item

All numbers from `example/minibt/experiments/*.py` [local]; data are synthetic unless stated.

| Hazard (plain analogy) | Evidence to show learners | Test / assertion | Review checklist line |
|---|---|---|---|
| **Look-ahead bias** (用明天的报纸做今天的决定) | 200 random walks x 10 years, zero cost. Mean Sharpe honest vs unshifted: 1/5 MA **0.03 vs 7.18**; 5/20 **0.03 vs 0.72**; 20/60 **0.03 vs 0.13**. Faster signal = bigger inflation. | *Future-perturbation test*: scramble prices from index `cut` on; positions up to and including `cut` must be unchanged. Plus a "teeth" test proving the buggy twin fails it. | "Where is the `.shift(1)`? Which timestamp is the decision, which is the fill?" Suspect any Sharpe > ~3 from a simple daily rule. |
| **Point-in-time data** (当时的报纸 vs 事后修订的史书) | `merge_asof` on observation month gave Feb's rate to 1 Feb; joining on `available_at` with `allow_exact_matches=False` gave NaN until the release date. | assert every joined row has `available_at < decision_time`; store both period and release timestamp. | "For each input: when could I have known this number?" Monthly rate series are often monthly averages stamped on the 1st, and some sources lag several months [memory]. |
| **Survivorship bias** (只采访中奖的人) | 500 assets, true drift 0, delist after -60%: 31% delisted; median 10-year return **-1.2%** for the full universe vs **+41.8%** for survivors; mean annual log return -0.60% vs +4.15%. | assert the universe at date t is built from a membership table with start/end dates; assert a long sample contains some delisted names. | "Is today's constituent list used for past dates?" |
| **Data snooping / multiple testing** (先射箭后画靶) | best of 58 MA pairs on noise: IS **+0.44**, same pair OOS **+0.01**, 41% of walks show best IS Sharpe > 0.5. Formula check: N=45/5y -> 1.00, N=7/2y -> 0.98, simulated 1.00 / 0.94. | not a unit test: the append-only experiment log gives N; report N with every headline number; keep a final hold-out touched once. | "How many variants were tried? Was the hypothesis written before looking?" |
| **Calendars / stale prices** (停摆的钟) | synthetic: forward-filling a market closed 12% of days created 179 fake zero-return days, cut same-day correlation 0.786 -> 0.705, and created a fake lead-lag 0.028 -> 0.108. Real: 2024 had 252 NYSE vs 242 Shanghai sessions, 19 days open only in NY and 9 only in Shanghai (`exchange_calendars` 4.13.3). | assert index sorted, unique, tz policy explicit; cap the share of exact-zero returns and the longest run of identical prices; inner-join on common sessions unless a fill is justified in writing. | "Which calendar is each series on? What happens on days only one market is open?" |
| **Time zones** | NY Friday 16:00 close = Saturday 05:00 in Shanghai; "same date" Shanghai close is 14 h earlier (07:00 vs 21:00 UTC). | assert `index.tz` is what the function documents; convert to UTC at the boundary. | "Can the earlier market's close know the later market's close of the same date?" |
| **Transaction costs** (只算收入不算油费) | base run: 43 trades cost 0.43% in total at 1 bp; Sharpe 0.25 -> 0.22 at 5 bp. | `test_costs_never_help` (0 < 1 < 10 bp ordering); hand-computed 4-day example with 10 bp = 0.001 per trade; flat signal earns exactly 0. | "Cost is a named config field with a unit; results shown at 0x / 1x / 2x cost." |
| **Unit mix-ups** (mg 还是 g) | Stage-0 script silently multiplies returns by 100. | metrics refuse `abs(r) > 1`; property test: scaling prices by any constant leaves every return unchanged. | "Decimal, percent or bp? Which annualisation factor, and is it a parameter?" |

Real-data version of the calendar row, from a downloaded copy of the public FRED series `DEXCHUS` [local; the counts depend on the download date]: 11,956 rows, 516
empty (e.g. US holidays); since 2015, 183 of 2,957 observations exactly repeat the previous value (6.2%), longest run 6 days,
by month Feb 38 / May 24 / Oct 58; gaps between observations are 1 day x2308, 3 days x522, 4 days x92, 5 days x3;
annualised vol 3.88% (all days) vs 4.01% (dropping zero-change days). The series is "Noon buying rates in New York
City for cable transfers payable in foreign currencies" from the H.10 release; today the page showed the latest
observation 2026-11-13, updated Nov 16, next release Nov 23 [source: https://fred.stlouisfed.org/series/DEXCHUS] - so
it is neither a tradable Shanghai close nor known on its own date.

Published anchors:
- Bailey, Borwein, Lopez de Prado, Zhu (2014): expected best in-sample Sharpe among N skill-less trials over y years is
  about `y^-1/2 * ((1-g) Z^-1[1-1/N] + g Z^-1[1-1/(N e)])`, g = 0.5772; "if only 5 years of data are available, no more
  than 45 independent model configurations should be tried"; a backtest "which does not report the number of trials N
  ... makes it impossible to assess the risk of overfitting" [source: https://carmamaths.org/jon/backtest.pdf, pp. 9-12].
- Harvey, Liu, Zhu: "a newly discovered factor needs to clear a much higher hurdle, with a t-ratio greater than 3.0"
  [source: https://www.nber.org/papers/w20592].
- Arnott, Harvey, Markowitz (2018) seven-point protocol - ready-made review checklist: 1 Research Motivation, 2 Multiple
  Testing and Statistical Methods ("keep track of all models and variables that were tried (both successful and
  unsuccessful)"), 3 Data and Sample Choice, 4 Cross-Validation ("true out-of-sample tests are only possible in live
  trading"; "are trading costs and data revisions taken into account?"), 5 Model Dynamics, 6 Complexity, 7 Research
  Culture ("most tests will fail") [source: SSRN 3275654 working-paper PDF, Exhibit 2, read via a mirror].

---

## 9. Data validation at boundaries, schema drift, units

- **Where**: validate once where data enters (after download/read) and once where results leave (before a report).
  Inside, trust the types. A loader that rejects an unexpected column layout is already such a check.
- **Plain checks first** (`src/minibt/data.py`): index is `DatetimeIndex`, tz policy, sorted, unique, no NaN, positive,
  max one-day move < 50%; each raises a message saying what is wrong. Exercised by `tests/test_data.py` (10 tests).
- **pandera when tables multiply** [local, 0.36.0 on pandas 3.1.1]:

```python
import pandera.pandas as pa
from pandera.typing.pandas import DataFrame, Index, Series

class Prices(pa.DataFrameModel):
    date: Index[pd.DatetimeTZDtype] = pa.Field(dtype_kwargs={"unit": "us", "tz": "UTC"}, unique=True)
    close: Series[float] = pa.Field(gt=0)
    ret_dec: Series[float] = pa.Field(ge=-0.5, le=0.5, nullable=True)
    class Config:
        strict = True          # unknown columns = schema drift = error

@pa.check_types
def clean(df: DataFrame[Prices]) -> DataFrame[Prices]: ...
```
  Caught with `Prices.validate(df, lazy=True)`: extra column, renamed column, numbers arriving as text, naive
  timestamps, and `-14.0` in a decimal-return column. **Not caught**: `0.28` meant as 0.28% - a range check cannot see
  every unit error. Also: pandera accepted a `datetime64[us]` column against a schema declaring `datetime64[ns]` (it
  does not compare datetime units), so old schemas keep passing on pandas 3.
- **Unit conventions that prevented mistakes in the example**: returns always decimal; costs always bps with a named
  constant `BPS = 1e-4`; suffixes in names (`cost_bps`, `ret_dec`, `rate_pct`, `_utc`); `periods_per_year` is a required
  argument, never a buried 252; functions that take returns reject `abs(r) > 1`; config rejects `cost_bps >= 100`.
  Suggested exercise (not measured on a public project): refactor a module that mixes yields in percent, spreads in
  percentage points and log returns in decimals, documented only in docstrings, with 252 as a module constant.

---

## 10. Staged path with the verified running example

`example/minibt/` = MA-crossover long/flat backtest on a seeded driftless random walk (truth: no edge), 552 lines of
package code, 406 lines of tests.

| Stage | What changes | Learner-visible proof |
|---|---|---|
| 0 | `legacy/stage0_one_long_script.py`: 14 lines, 7 marked sins (cwd-dependent path, magic numbers, percent switch, look-ahead, no costs, bare 252, screen-only result) | prints `sharpe 0.35` |
| 1 | make it rerunnable: fixed seed, relative-to-project paths, raw file + `.meta.json`, `git init`, first commit | same number twice |
| 2 | move logic into `src/minibt/{data,signals,backtest,metrics}.py` as pure functions; notebook only imports | `uv run python notebooks/01_explore_ma_crossover.py` |
| 3 | tests: known-answer, future-perturbation, cost ordering, unit guards, data checks, property-based, golden file | `40 passed in 2.74s` |
| 4 | `configs/base.toml` -> frozen dataclass; `minibt run --config ... [--cost-bps 5]` via `[project.scripts]` | honest Sharpe `0.25 (90% bootstrap CI -0.21 .. 0.76)` |
| 5 | `manifest.json`, `report.md`, `experiments.csv`, `--require-clean`, run folder `<commit>_<confighash>` | identical SHA-256 on rerun, on 3.12 and 3.14 |
| 6 | automation: `ruff check`, `ruff format --check`, `uv run --locked pytest`, Makefile; then nbstripout / jupytext | `make run` -> "Nothing to be done" |

Commands and real output [local] (one session at commit `b21089f`; report lines elided with `...`, absolute path in
"saved to" shortened):

```
$ uv run minibt run --config configs/base.toml --require-clean --note "baseline 20/60, 1bp"
# Backtest report
- code: `b21089f5b7`  |  config: `283f0d01b9a5`  |  data sha256: `c2d78b483ee0`
- created (UTC): 2026-11-19T12:13:59Z  |  python 3.14.9  |  packages: {'minibt': '0.1.0', 'pandas': '3.1.1', 'numpy': '2.5.5'}
- parameters: {'data_path': 'data/raw/prices.csv', 'fast_window': 20, 'slow_window': 60, 'cost_bps': 1.0, 'periods_per_year': 252, 'seed': 20261119}
...
| annualised return | 1.64% |
| Sharpe ratio | 0.25 (90% bootstrap CI -0.21 .. 0.76) |
| max drawdown | -12.39% |
| trades | 43 |
| total cost paid | 0.4300% |
saved to reports/b21089f_283f0d01b9a5
$ uv run minibt run --config configs/base.toml --require-clean --cost-bps 5 --note "cost sensitivity 5bp" | grep Sharpe
| Sharpe ratio | 0.22 (90% bootstrap CI -0.24 .. 0.73) |
$ (edit src/minibt/signals.py without committing) ; uv run minibt run --config configs/base.toml --require-clean
error: uncommitted changes; commit first or drop --require-clean
exit code: 2
$ tail -n 2 reports/experiments.csv
2026-11-19T12:13:59Z,b21089f5b7,False,283f0d01b9a5,c2d78b483ee0,20,60,1.0,0.2465,0.016432,-0.123939,"baseline 20/60, 1bp"
2026-11-19T12:14:00Z,b21089f5b7,False,beea1d865cff,c2d78b483ee0,20,60,5.0,0.2207,0.014712,-0.12674,cost sensitivity 5bp
```
Earlier in the same repo: `uv run python legacy/stage0_one_long_script.py` printed `sharpe 0.35`; a run made before
`git init` was reported as ``code: `NO-GIT` `` and logged with an empty commit; runs with uncommitted edits (without
`--require-clean`) printed `warning: uncommitted changes - this result cannot be tied to one commit` and were logged
with `git_dirty=True`; once run folders were named by commit, such a run landed in `1e34c99-dirty_283f0d01b9a5/`.
Log header:
`created_at_utc,git_commit,git_dirty,config_hash,data_sha256,fast_window,slow_window,cost_bps,sharpe,ann_return,max_drawdown,note`.

`manifest.json` keys: `git{branch, commit (40 hex), dirty}`, `config{...}`, `config_hash`, `data_sha256` (64 hex),
`python` ("3.14.9"), `platform` ("macOS-27.2.1-arm64-arm-64bit-Mach-O"), `packages{minibt, numpy, pandas}`, `command`
(full argv), `created_at_utc`.

The core test (condensed from `tests/test_backtest.py`; works unchanged for any strategy function):

```python
def positions_ignore_the_future(backtest_fn, prices, cut):
    rng = np.random.default_rng(0)
    shocked = prices.copy()
    shocked.iloc[cut:] = shocked.iloc[cut:] * rng.uniform(0.5, 1.5, size=len(prices) - cut)
    pos = lambda p: backtest_fn(p, ma_crossover_signal(p, 5, 20), cost_bps=0.0)["position"]
    return pos(prices).iloc[: cut + 1].equals(pos(shocked).iloc[: cut + 1])
```

Other teaching moments verified: changing `ddof=1` to `ddof=0` in one metric made the golden-file test and one unit
test fail (`2 failed, 38 passed`); the golden file is refreshed deliberately with `UPDATE_GOLDEN=1`; hypothesis found no
counter-example to "rescaling prices changes nothing" in 100 cases.

Suggested capstone checklist for a learner's existing project, if any (not measured on a public project; each item
is a practice from sections 7-10): add `*.meta.json` + hash check to the data loaders; move functions that live in
notebooks into `src/` with tests; one constants/config home instead of constants repeated across notebooks; replace
"edit a value in a cell" with a CLI option or config file; unit-suffix columns whose unit is not obvious; a
stale-price check for any loader of prices or rates; stamp each saved figure folder with a manifest.

---

## 11. Pitfalls a beginner will hit

1. First `git commit` fails when gpg signing is configured but no gpg is installed - see TL;DR 10.
2. `ModuleNotFoundError` for the project's own package inside an iCloud-synced folder (hidden `.pth`) - section 3.
3. First `ruff check` shows rule codes no tutorial mentions (ISC004, TRY004, RUF046, UP017, BLE001); copying an old
   `select = ["E","F"]` both hides the new checks and switches on E501 (`Line too long (126 > 88)`), which the defaults
   leave off [local].
4. `# noqa: S603` copied from older code is itself reported (`RUF100 Unused noqa directive (non-enabled: S603)`); old
   `"tests/*" = ["S101"]` ignores are unnecessary under defaults [local].
5. `df[mask]["col"] = x` silently does nothing on pandas 3; `resample("M")` raises; `pct_change()` leaves NaN.
6. nbstripout: after recreating/moving the venv `git add` aborts; in a fresh clone without `--install` outputs are
   committed silently; "modified" notebooks with an empty diff; outputs vanish after `git checkout`.
7. jupytext pair edited on both sides without `--sync`; magics become comments in the `.py`.
8. papermill/nbconvert/nbmake "work on my Terminal, fail for the assistant" (sandbox) - and papermill needs kernelspec
   metadata in the notebook.
9. Believing a seed alone gives reproducibility: unsorted sets/listdir, upgraded numpy, or a refreshed raw file change
   results with the same seed.
10. Committing after running: the manifest then points at a commit that did not produce the result. Order is
    commit -> run -> (commit the log).
11. Range checks give false comfort for units (0.28 passes as a decimal return).
12. Forward-filling to "align" two markets; treating FRED dates as tradable closes; joining monthly averages on the
    first day of their month.
13. Tuning parameters on the full sample, then reporting only the winner - and not knowing how many were tried.
14. A golden-file test updated reflexively whenever it fails defeats its purpose; the diff of the JSON is the review.
15. `Path.cwd()`-relative paths break when the notebook is launched from `notebooks/`; resolve from the package or a
    project-root marker.
16. Running `ruff format .` over lesson notes and finding the "bad example" code blocks quietly corrected (section 2).
17. Old datetime habits on pandas 3: `idx.astype("int64") // 10**9` no longer yields seconds (values are microseconds).
18. A lab log named `*.log` is invisible to git when a global ignore file lists `*.log` - it looks saved but is never committed.

---

## 12. Recommendations for the course

**Where this topic sits.** The draft design document found in the workspace (`Engineering/docs/design/`, status
"draft, awaiting approval"; read-only, treated as context) makes "research-code engineering norms" an elective
after the professional-norms stage, with a first batch that only covers orientation, terminal, Markdown and Git. If
that stands: (a) the first batch needs just four facts from this brief - the gpg commit blocker (first-commit lesson),
the global `*.log` ignore and self-ignoring cache folders ("what not to track" lesson), the iCloud/`.pth` mechanism
(the "move out of iCloud" lesson), and `ruff format` rewriting Python fences in Markdown lessons; (b) everything else
feeds the later Python/norms stages and the "engineer your existing project" elective, where section 10's capstone list
applies. The stdlib-only `scripts/check_notebooks.py` fits a "self-check scripts use only the standard library" rule.

**Teach first within this topic (highest payoff per minute)**
1. Hidden state: run `ruff check` on a doctored notebook (F821 x2), then "Restart & Run All" / `python nb.py`.
2. Extract one function from a notebook into `src/<pkg>/`, import it back, show that the notebook got shorter.
3. One known-answer test with numbers small enough for a calculator (the 4-day example).
4. The look-ahead demo (7.18 vs 0.03) and the future-perturbation test; let the learner break and repair `.shift(1)`.
5. Config + CLI: replace an edited constant with `--config`; reject a typo'd key.
6. Manifest + experiment log; run twice and compare hashes; then change the data file by one digit.
7. Notebook diffs: nbstripout (default) and what the diff looks like before/after.

**Second pass**: pandera at the boundary; property-based and golden-file tests; calendars with the public FRED
`DEXCHUS` series; multiple-testing simulation and the seven-point protocol as a pre-flight checklist; Makefile as a DAG.

**Awareness only (one paragraph each)**: marimo; papermill; nbQA; nbdime (`nbdiff -s a.ipynb b.ipynb` worked); DVC;
MLflow; Docker; Snakemake/Dagster; `ccds`; `sp-repo-review`; ALFRED vintages; purged cross-validation [memory].

**Skip**: conda workflows, `setup.py`, PYTHONPATH tricks, flake8/black/isort as separate tools, Hydra-style config
frameworks, `pint` unit libraries, class hierarchies for strategies.

**Plain-Chinese analogies that fit the verified demos**
- 原始数据不可变：像博物馆展品，只能看不能改；清洗是在复印件上做笔记。指纹（SHA-256）= 展品的防伪编号。
- Notebook 与模块：notebook 是草稿纸/实验记录本，`src/` 是誊写进教科书的公式，测试是书后的验算。
- 隐藏状态：厨房台面上上次剩下的半成品——菜谱里没写，这次却用上了。Restart & Run All = 清台后照菜谱从头做一遍。
- `pyproject.toml` 是购物清单（"牛奶"），`uv.lock` 是购物小票（品牌、批次都写死）。
- 随机种子：约定好的洗牌手法，同一个种子洗出同一副牌；但换了一副牌（数据/库版本）结果照样变。
- 配置文件：把散落在机器内部的旋钮集中到一块控制面板上。
- manifest：食品包装上的"生产批号 + 配料表 + 生产线"——哪次提交、哪份数据、哪组参数。
- 实验日志：失败的实验也要记，否则不知道一共试了多少次（多重检验的分母）。
- 前视偏差：用明天的报纸做今天的决定；"未来扰动测试" = 把明天的报纸乱改一通，今天的决定不该变。
- 幸存者偏差：只采访中奖的人问彩票值不值得买。 数据窥探：先射箭、后画靶。
- 陈旧价格：停摆的钟，看着没波动，其实是没报价。 交易成本：只算流水，不算油费和平台抽成。
- 单位写进名字（`cost_bps`、`ret_dec`、`rate_pct`）：像药品剂量必须写清 mg 还是 g。
- 黄金文件测试：重构前先给结果拍张照，重构后对着照片检查。

---

## 13. Not verified today

- Kernel-based execution (`jupyter nbconvert --execute`, `jupyter execute`, `papermill` full run, `pytest --nbmake`,
  `jupytext --execute`, `marimo edit/run/export html`): only the failure mode in the sandbox was observed.
- JupyterLab UI steps (adding the `parameters` tag, menu names) - from papermill docs, not clicked through.
- That iCloud sets the hidden flag on venv files and leaves "file 2.csv" conflict copies: reported, not observed today.
- Ruff 0.17.0's own breaking changes (only 0.16.0's post was read); 413 default rules per the 0.16 blog vs 407
  measured in 0.17.2 - not reconciled.
- `ccds` generation and `sp-repo-review` were not run (template hooks / writes outside scratch); DVC and MLflow were
  not installed; the Hypermodern Python *book* contents come from a search-result summary.
- Arnott-Harvey-Markowitz was read from a third-party mirror of the SSRN working paper (Oct 2018 version), not the
  journal version; the Harvey-Liu-Zhu quote is from the NBER abstract.
- Publication lags of monthly rate sources and FRED's exact publication lag for H.10 were not measured today; `exchange_calendars`
  XSHG is the stock-exchange calendar, used only as a proxy for onshore CNY trading days.
- Why `sum()` of floats is now order-independent (compensated summation): observed behaviour, cause from memory.
- JupyterLab's automatic jupytext pairing on save, `git restore`/`stash` with the nbstripout filter, pre-commit hooks.

---

## Appendix: files in this scratch directory

- `example/minibt/` - running example (git repo, 7 commits, repo-local identity, signing disabled locally):
  `src/minibt/{config,data,signals,backtest,metrics,provenance,pipeline,cli}.py`, `tests/` (7 files, 40 tests,
  `golden/base_metrics.json`), `configs/base.toml`, `legacy/stage0_one_long_script.py`, `experiments/*_demo.py` (4),
  `notebooks/01_explore_ma_crossover.{py,ipynb}`, `scripts/check_notebooks.py`, `Makefile`, `reports/experiments.csv`.
- `t_ruff_nb/` (demo + hidden-state notebooks), `t_nbstripout/` + `t_clone_parent/` (filter repo and its fresh clone),
  `t_jupytext*/`, `t_exec/` (papermill / marimo / kernel failures), `t_ruff_rules/`, `t_cal/` (exchange_calendars
  venv), `pdftools/` (text extracted from the two papers).
