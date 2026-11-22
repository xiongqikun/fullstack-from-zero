# Brief: configuration, secrets, dependency security, logging, error handling (small Python project)

Topic key: `security-config-logging`. Researched 2026-11-19 on the reference Mac (plan G7).
Tags: **[local]** = I ran it here today · **[source: URL]** = read in a primary source today · **[memory]** = not verified.
Lab files (all throwaway, may vanish on reboot): `<scratch>/lab/` where `<scratch>` =
`<scratch>/research/security-config-logging`.
All code shown was executed today. Some blocks are condensed excerpts; the full files in `lab/gooddemo/src/fxlab/` (`settings.py`, `logging_setup.py`, `errors.py`, `cli.py`, `download.py`, `atomic.py`, `validate_df.py`) pass `ruff check` + `ruff format --check` (ruff 0.17.2) with the config in section 7 and were re-run after formatting.

## 0. What was verified, and how

| Area | How | Versions seen today |
|---|---|---|
| uv env files, lock, hashes, audit, export, cooldown | throwaway projects under `lab/` | uv 0.13.5 [local] |
| python-dotenv, pydantic-settings | `uv add` in `lab/envdemo`, Python 3.14.9 | python-dotenv 1.2.4, pydantic-settings 2.16.3, pydantic 2.14.3 [local] |
| Secret scanning, history rewrite | `uvx detect-secrets`, `uvx git-filter-repo` in throwaway repos (repo-local git config only) | detect-secrets 1.5.0, git-filter-repo 2.47.0, git 2.54.0 [local] |
| Vulnerability audit | `uv audit`, `uvx pip-audit` against pinned old `requests`/`jinja2` | pip-audit 2.10.1 [local] |
| Lints | ruff on deliberately bad files | ruff 0.17.2, bandit 1.9.4 [local] |
| Logging, errors, atomic write, retries, downloads | scripts run on Python 3.14.9 | requests 2.34.2, tenacity 9.2.1, pandas 3.1.1, structlog 26.1.0 [local] |
| Notebook hygiene, licences | `uvx nbstripout`, `uvx pip-licenses` | nbstripout 0.9.2, pip-licenses 5.5.5 [local] |
| Docs / specs | 12factor.net, GitHub Docs, uv/ruff docs, Python 3.14 docs, PyPI blog, OWASP, PEPs | fetched today |

Not obtainable through `uvx` (so documented from sources only): **gitleaks / betterleaks / trufflehog** (Go binaries; `gitleaks` is not on PyPI, PyPI `trufflehog` is an abandoned 2021 v2) [local: PyPI JSON].
Sandbox artefacts that are NOT learner problems: `uvx` needed `UV_TOOL_DIR=$TMPDIR/...`; pip-audit needed `--cache-dir`; `ps` was blocked.

## 1. Headline findings (most decision-relevant first)

1. **`git commit` fails when signing is on but gpg is missing.** If global git config has `commit.gpgsign=true`, `gpg.format=openpgp`, `gpg.program=gpg`, but no `gpg` binary exists on PATH, a fresh repo shows [local]:
   `error: cannot run gpg: No such file or directory` / `fatal: failed to write commit object`. Lessons that commit must first handle this (per-repo `git config commit.gpgsign false`, or `git commit --no-gpg-sign`, or the learner fixes signing). Do not touch the global config without the learner deciding.
2. **`uv init` does not protect `.env`.** The generated `.gitignore` only lists `__pycache__/`, `*.py[oc]`, `build/`, `dist/`, `wheels/`, `*.egg-info`, `.venv`; `git check-ignore .env` exits 1 (not ignored) [local]. The secrets block must be added by hand before the first commit.
3. **`uv run` does not read `.env` unless asked**: `uv run --env-file .env ...` or `UV_ENV_FILE=.env`; real environment variables win over the file; a missing file is a hard error (exit 2) [local].
4. **Ruff's defaults changed massively**: since v0.16.0 (2026-07-23) Ruff enables ~400 rules by default instead of the old `E4,E7,E9,F` (59 rules) [source: https://astral.sh/blog/ruff-v0.16.0]; ruff 0.17.2 here enables 407, including `E722`, `BLE001`, `S102`, `S110`, `S112`, `LOG015`, `TRY002`, `PLW1510` [local]. Old tutorials ("add `select = [...]` to get bugbear") are outdated, and `select = [...]` now *shrinks* the rule set; use `extend-select`.
5. **uv has a native audit**: `uv audit` (announced 2026-06-08, OSV-backed, still *experimental*) works on 0.13.5 and exits 1 on findings [local][source: https://astral.sh/blog/uv-audit]. `uvx pip-audit` remains the stable alternative.
6. **Dependency cooldown is one line**: `[tool.uv] exclude-newer = "7 days"` works [local]; PyPI's own incident report (posted 2026-04-02) on the LiteLLM/Telnyx package compromise recommends cooldowns + hashed lock files [source: https://blog.pypi.org/posts/2026-04-02-incident-report-litellm-telnyx-supply-chain-attack/].
7. **Secret-scanner landscape moved**: gitleaks README now says it is "feature complete", security patches only, author moved to **Betterleaks** (MIT; v1.10.1 stable, v2 in RC) [source: https://github.com/gitleaks/gitleaks, https://github.com/betterleaks/betterleaks]. `detect-secrets` (last release May 2024) still runs on Python 3.14 but **contacts provider APIs to verify findings unless `--no-verify`** [local: sandbox blocked calls to api.stripe.com and sts.amazonaws.com].
8. **Linters are not secret scanners**: ruff `S105-S107` and bandit both missed `API_KEY = "sk_live_..."` and a password inside a DB URL. Tested names [local]: `S105` fires for `password`, `passwd`, `pwd`, `token`, `api_token`, `secret`, `SECRET_KEY`, `aws_secret_access_key`; it stays silent for `api_key`, `API_KEY`, `apikey`, `access_key`, `auth`, `credentials`, `db_url`.
9. **Python 3.14 syntax news that contradicts old tutorials**: `except ValueError, TypeError:` (no parentheses) is valid again (PEP 758) and `ruff format` with `target-version = py314` *removes* the parentheses; `return` inside `finally` now emits `SyntaxWarning` (PEP 765) [local][source: https://docs.python.org/3.14/whatsnew/3.14.html].
10. **The Twelve-Factor text is unchanged since 2017** on 12factor.net; it was open-sourced Nov 2024 and a rewrite lives on the `next` branch (last commit 2025-07-10), not yet published [source: https://12factor.net/, https://12factor.net/blog, https://github.com/twelve-factor/twelve-factor].

## 2. The Twelve-Factor App: current state and what applies

- Site footer: "Written by Adam Wiggins - Last updated 2017". Blog: "Twelve-Factor App Methodology is now Open Source" (12 Nov 2024); maintainers are "getting organized for larger updates" (Dec 2024). The `next` branch restructures each factor into numbered sub-points; the drafts of *config*, *dependencies*, *logs* that I read keep the same substance as 2017 [source: URLs above + raw `next/content/*.md`].
- Twelve-factor targets web services. For a solo analysis project, teach four factors and name the rest only as vocabulary:

| Factor (2017 wording) | Core idea [source: 12factor.net/<factor>] | Translation for a solo analysis project |
|---|---|---|
| II Dependencies: "Explicitly declare and isolate" | Manifest + isolation tool; never rely on system packages or tools | `pyproject.toml` + `uv.lock` + `.venv`; `uv run`, never system `python3` (3.9.6 here) |
| III Config: "Store config in the environment" | Config = what varies between deploys; litmus test: could the repo be open-sourced right now without leaking credentials? | API keys, data paths, timeouts come from env / `.env`; code holds defaults only |
| X Dev/prod parity | Keep time, people and tool gaps small | Same Python + same lock on laptop, CI and any future server: `.python-version`, `uv sync --locked` |
| XI Logs: "Treat logs as event streams" | App writes events to stdout, never manages log files or routing | Use `logging` to the console; a rotating file under `logs/` is a pragmatic extra for long batch jobs |

- Nuance to state honestly: twelve-factor says env vars beat untracked config files because files get committed by accident; a `.env` file is exactly such a file and is acceptable only with `.gitignore` + scanner as guard rails. OWASP also notes env vars are visible to every process of the user and can show up in dumps [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html]. Password managers / OS keychain / cloud secret stores are awareness items only.

## 3. Configuration and secrets

### 3.1 Files and rules

```gitignore
# --- secrets & local config (add BEFORE the first commit) ---
.env*
!.env.example
*.pem
*.key
secrets/
```
- `.env*` + `!.env.example` is deliberately broader than the common `.env` / `.env.*` pair: the latter does **not** ignore `.envrc` or a duplicate such as `.env 2` [local: `lab/ign2`].
- `.env.example` is committed: every key, no real values, short comments. A tested sync check (fits a unit test) [local]:
  `assert set(Settings.model_fields) == {k.lower() for k in dotenv_values(".env.example")}`.
- `chmod 600 .env` works (`-rw-------`) [local]. If the project lives in an iCloud-synced Desktop folder, a `.env` there is also uploaded to iCloud [memory: sync behaviour not tested]; use low-privilege, revocable keys.
- `.gitignore` never untracks a file that is already tracked: `M scratch.txt` kept showing until `git rm --cached scratch.txt` [local: `lab/ignrepo`].
- With the `uv_build` backend, `uv build` shipped only `src/` + metadata; `.env` was not in the sdist or wheel [local].

### 3.2 Three levels of reading config (teach in this order)

Level 1, standard library, fail fast [local, exit 1 with the message when unset]:
```python
def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"Missing required environment variable {name}. Copy .env.example to .env and fill it in.")
    return value

timeout = float(os.environ.get("REQUEST_TIMEOUT", "10"))  # env values are ALWAYS strings
```
Level 2, `python-dotenv` (`load_dotenv()` at program start) [local, v1.2.4]:
- Signature default `override=False`: real env vars win (`DATA_DIR=/from/shell` beat the file).
- `find_dotenv()` searches upward from the *calling script's* directory, not the cwd; from `python -c` in another directory it found nothing and `load_dotenv()` returned `False` silently.
- `dotenv.ipython` exists (`%load_ext dotenv` / `%dotenv` in notebooks; module presence checked, magic not run). The `dotenv` CLI needs the extra `python-dotenv[cli]`.

Level 3, `pydantic-settings`: one typed, validated object (recommended end state) [local, lint-clean]:
```python
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # optional: silently skipped if the file does not exist
        env_file_encoding="utf-8",
        extra="ignore",  # .env may contain keys this class does not know about
    )

    data_api_key: SecretStr  # required: no default -> fail fast when missing
    data_dir: Path = Path("data")
    request_timeout: float = Field(default=10.0, gt=0, le=120)
```
Real output [local]:
```
Settings(data_api_key=SecretStr('**********'), data_dir=PosixPath('data'), request_timeout=10.0)
model_dump_json: {"data_api_key":"**********","data_dir":"data","request_timeout":10.0}
REQUEST_TIMEOUT=30 in the shell -> request_timeout 30.0          (env beats .env)
REQUEST_TIMEOUT=abc -> ValidationError ... unable to parse string as a number [type=float_parsing, input_value='abc']
no .env, no env var -> ValidationError: data_api_key  Field required [type=missing]
```
- Priority: init kwargs > environment variables > dotenv file > secrets dir > defaults; names are case-insensitive by default [source: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/].
- **Pitfall A**: without `extra="ignore"`, any unknown key in `.env` raises `extra_forbidden` [local].
- **Pitfall B (leak)**: pydantic errors print the offending value. An unknown `DB_PASSWORD=...` line produced `Extra inputs are not permitted [type=extra_forbidden, input_value='hunter2-not-real', ...]` in the traceback; `hide_input_in_errors=True` in `SettingsConfigDict` removed the value [local].
- Read a secret only at the point of use: `settings.data_api_key.get_secret_value()`.

### 3.3 `uv run --env-file` (uv 0.13.5) [local]

| Check | Result |
|---|---|
| `uv run python show_env.py` with `.env` present | variables are `None` (no auto-loading) |
| `uv run --env-file .env ...` / `UV_ENV_FILE=.env uv run ...` | loaded |
| same key in shell and file | shell wins |
| `--env-file .env --env-file .env.local` | later file wins; `UV_ENV_FILE=".env .env.local"` (space separated) works |
| `--no-env-file` | overrides `UV_ENV_FILE` |
| missing file | `error: No environment file found at: .env.missing`, exit 2 |
| syntax | `export KEY=v`, quoted multi-line, `${VAR}` interpolation, inline `# comment` work |
| where it exists | `uv run`, `uvx` / `uv tool run`; not `uv sync` / `uv lock` / `uv add` |

- No `pyproject.toml` setting for env files; parser is the Rust `dotenvy` crate [source: https://docs.astral.sh/uv/concepts/configuration-files/].
- **Parser mismatch pitfall**: `UNQUOTED=hello world` is accepted by python-dotenv but makes uv print only `warning: Failed to parse environment file ... at position 6` and silently skip that line **and every line after it**, exit code still 0 [local]. Rule for the course: one `KEY=value` per line, no spaces around `=`, quote anything containing spaces.
- Teaching choice: `uv run --env-file .env` (code stays free of dotenv logic, twelve-factor style) versus `env_file=".env"` in `Settings` (also works in notebooks/IDE runs). Recommend the `Settings` route as the default and show `--env-file` as the same idea from the outside.

### 3.4 A secret was committed: the drill (all steps run in `lab/leakrepo*`) [local]

Order of operations confirmed by GitHub Docs: "you need to revoke and/or rotate that secret" first; once it cannot be used, rewriting history may be unnecessary [source: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository].

1. Deleting in a later commit does not help. After commit 2 removed the key, the working tree was clean but (the drill used a Stripe-shaped fake key; it is shown as `FAKE_KEY_FOR_DEMO_0000` here so that secret scanners do not flag this brief):
```
$ git log --oneline -S"FAKE_KEY_FOR_DEMO"    # both commits touch the string
$ git grep -n "FAKE_KEY_FOR_DEMO\|hunter2" $(git rev-list --all)
8533346...:.env:2:DB_PASSWORD=hunter2-not-real
8533346...:fetch_prices.py:3:API_KEY = "FAKE_KEY_FOR_DEMO_0000...
```
2. Rotate/revoke at the provider (the only step that actually restores safety).
3. Stop tracking: `git rm --cached .env`, add ignore rules, commit.
4. Optional history rewrite on a **fresh clone** (`git filter-repo` is not built into git 2.54: `git: 'filter-repo' is not a git command`; `uvx git-filter-repo` works, or `brew install git-filter-repo` per GitHub Docs):
```
uvx git-filter-repo --sensitive-data-removal --invert-paths --path .env
uvx git-filter-repo --sensitive-data-removal --replace-text ../replacements.txt   # lines: SECRET==>***REMOVED***
```
   Observed: both commit hashes changed (`c128498 -> e0b484e`, `8533346 -> f82419e`), `origin` remote was removed, `git grep` over all commits found nothing (exit 1), and the tool printed "NEXT STEPS": `git push --force --mirror origin`, contact server admins, colleagues re-clone. On a non-fresh clone it aborts: `Refusing to destructively overwrite repo history since this does not look like a fresh clone`.
5. On GitHub: forks, old clones, PR refs and cached views still hold the data; GitHub Support must purge server-side; signatures are invalidated [source: same GitHub page].
- `git filter-branch` still exists but git 2.54 itself prints `WARNING: git-filter-branch has a glut of gotchas ... use an alternative filtering tool such as 'git filter-repo'` [local]. Do not teach it or BFG.

### 3.5 Secret scanners

| Tool | Scans | Status today | Notes |
|---|---|---|---|
| `detect-secrets` 1.5.0 (PyPI) | current files only, not history | last release May 2024; ran under Python 3.12 and 3.14 via `uvx` [local] | HEAD scan returned `{}` although history held 2 secrets; at the leaking commit it flagged Stripe key, AWS key, "Secret Keyword", high-entropy strings. Use `--no-verify`. |
| gitleaks v8.30.1 (21 Mar 2026) | git history (`gitleaks git`), dirs (`gitleaks dir`), stdin | "feature complete", security patches only; `detect`/`protect` deprecated since v8.19 [source: gitleaks README, releases page] | MIT; `brew install gitleaks`; `# gitleaks:allow`, `.gitleaksignore` |
| Betterleaks | git, filesystem (`betterleaks fs`), stdin | successor by the gitleaks author; v1.10.1 "Latest", v2.0.0-rc.9 pre-release [source: betterleaks README, releases] | MIT; no provider calls unless `--validate` |
| TruffleHog v3 | git, filesystem, many SaaS | active; **AGPL-3.0**; verification against live services is on by default (`--no-verification` to disable) [source: https://github.com/trufflesecurity/trufflehog] | `brew install trufflehog`; PyPI `trufflehog` 2.2.1 (2021) is obsolete |
| GitHub secret scanning + push protection | whole history, issues, PRs | free and automatic on public repos; *push protection for users* is on by default and blocks pushes of recognised secrets to public repos; private org repos need GitHub Secret Protection [source: https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning, .../about-push-protection] | server-side, cannot be skipped with `--no-verify` |

Verified local workflow with detect-secrets [local: `lab/dsrepo`]:
```
uvx detect-secrets scan --no-verify > .secrets.baseline            # {"results": {}} on a clean repo
uvx --from detect-secrets detect-secrets-hook --no-verify --baseline .secrets.baseline app.py
  ERROR: Potential secrets about to be committed to git repo!  ... Secret Type: Stripe Access Key  Location: app.py:2   (exit 1)
# a line ending with  "# pragma: allowlist secret"  -> exit 0
```
A hand-written `.git/hooks/pre-commit` (then `chmod +x`) blocked `git commit` with that error; `git commit --no-verify` bypassed it [local]. Lesson: local hooks are a seat belt; server-side push protection is the airbag.
```sh
#!/bin/sh
files=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$files" ] && exit 0
exec uvx --from detect-secrets detect-secrets-hook --no-verify --baseline .secrets.baseline $files
```

### 3.6 Other leak channels worth one sentence each

- **Notebook outputs**: a notebook whose *source* only prints `os.environ[...]` still stored the key and client rows in its saved *output*; `uvx nbstripout nb.ipynb` emptied outputs and `execution_count`; `nbstripout --verify` exits 1 if anything would be stripped [local: `lab/nbdemo`].
- **Logs and tracebacks**: see 5.3.
- **Command-line arguments** (`--api-key xxx`) end up in shell history and the process list [memory: `ps` blocked here].
- **URLs**: send keys in headers, not query strings; URLs get logged [memory].
- **Screenshots / AI chat**: pasting `.env` into an assistant or a screenshot is disclosure [practice, no source].

## 4. Dependency and supply-chain security

### 4.1 Lock file and hashes [local]

- `uv.lock` starts with `version = 1`, `revision = 5`, and stores per-file `hash = "sha256:..."`, `size`, `upload-time` for every sdist and wheel. Docs: "This file should be checked into version control"; it "should not be edited manually" [source: https://docs.astral.sh/uv/concepts/projects/layout/].
- Hashes are enforced: after changing 4 hex digits of one wheel hash, `uv sync --frozen` (fresh cache) failed with `Hash mismatch for idna==3.20  Expected: sha256:...0000  Computed: sha256:...582c`.
- Stale-lock detection: `uv lock --check`, `uv sync --locked`, `uv run --locked` all exit 1 with `error: The lockfile at uv.lock needs to be updated, but --locked was provided` (`--check` for `uv lock --check`) plus `hint: To update the lockfile, run uv lock` when `pyproject.toml` changed; exit 0 when in sync. `--frozen` uses the lock without checking [source: https://docs.astral.sh/uv/concepts/projects/sync/].
- Exports: `uv export --format requirements.txt` (hashes included by default), `--format pylock.toml` (PEP 751, the standard lock format approved April 2025 [source: https://packaging.python.org/en/latest/specifications/pylock-toml/]), `--format cyclonedx1.5` (SBOM; prints `experimental`, preview feature `sbom-export`).

### 4.2 Auditing for known vulnerabilities [local: `lab/auditdemo`, `lab/fixdemo`]

Setup: `uv add "requests==2.25.1" "jinja2==2.11.2"`.
```
$ uv audit
warning: `uv audit` is experimental and may change without warning. Pass `--preview-features audit-command` to disable this warning.
Found 36 known vulnerabilities and no adverse project statuses in 7 packages
idna 2.10 has 4 known vulnerabilities:
- PYSEC-2024-60: ... denial of service from specially crafted inputs to idna.encode
  Fixed in: 3.7
...                                                     # exit code 1
$ uv export --format requirements.txt --no-emit-project -o req.txt
$ uvx pip-audit -r req.txt --disable-pip
Found 34 known vulnerabilities in 4 packages             # exit code 1
$ uv export --format pylock.toml -o pylock.toml && uvx pip-audit --locked .     # same 34
```
- `uv audit` reads the lock, queries OSV, also reports "adverse" statuses (archived / deprecated / quarantined, PEP 792 Final) [source: https://astral.sh/blog/uv-audit, https://peps.python.org/pep-0792/]. Flags: `--ignore ID`, `--ignore-until-fixed ID`, `--no-dev`, `--output-format text|json|sarif`. JSON top-level keys: `schema` (`"version": "preview"`), `summary`, `vulnerabilities`, `adverse_statuses`.
- **False-green trap**: bare `uvx pip-audit` run inside this vulnerable project printed `No known vulnerabilities found` (exit 0), because it audited its own throwaway tool environment [local]. It must be pointed at the project: `-r <exported requirements> --disable-pip` or `--locked .` with a `pylock.toml` (both verified above). `uvx pip-audit .` (resolves via an internal pip) failed here on the sandbox proxy's TLS, not tested further. Default service is `pypi`; `-s osv` is optional.
- Experimental malware lookup during sync: `UV_MALWARE_CHECK=1 uv sync` printed `warning: Malware checks are experimental ... --preview-features malware-check` [local].
- Community-reported open bugs in `uv audit` (false-clean on truncated OSV responses) exist [source: search hit astral-sh/uv issue #22102; not read in full]. Treat it as a helper, keep Dependabot alerts or pip-audit as a second opinion.

Fix workflow, the part beginners get wrong:
```
$ uv add "requests>=2.33" "jinja2>=3.1.6"       # direct deps fixed ...
$ uv audit    -> still 18 vulnerabilities       # ... transitive idna 2.10 / urllib3 1.26.20 stayed locked
$ uv lock --upgrade-package idna --upgrade-package urllib3
Updated idna v2.10 -> v3.20
Updated urllib3 v1.26.20 -> v2.8.0
$ uv audit    -> Found no known vulnerabilities and no adverse project statuses in 7 packages   (exit 0)
$ uv sync --locked
```
uv prefers already-locked versions, so `uv add` never refreshes unrelated transitive packages; `uv lock --upgrade` refreshes everything within the declared ranges. `uv tree --outdated` shows `requests v2.25.1 (latest: v2.34.2)` style hints [local].

### 4.3 Cooldown, bots, pinning, names, licences

- **Cooldown** [local]: adding
  ```toml
  [tool.uv]
  exclude-newer = "7 days"
  ```
  printed `Resolving despite existing lockfile due to addition of global exclude newer 2026-11-12T...` and wrote `exclude-newer-span = "P7D"` into `uv.lock`. Accepted: RFC 3339 timestamps, "friendly" durations (`24 hours`, `1 week`, `30 days`), ISO 8601 durations (`P7D`); default is none; per-package override `exclude-newer-package = { pkg = false }` [local help text][source: https://docs.astral.sh/uv/reference/settings/]. pip has the equivalent `--uploaded-prior-to P3D` [source: https://pip.pypa.io/en/stable/cli/pip_install/, docs v26.3].
- **Why**: in the LiteLLM/Telnyx incident malicious releases were live for 2h32m and 3h42m before quarantine; PyPI recommends cooldowns, hashed lock files (`pip freeze` is not a lock file), and for maintainers Trusted Publishers, 2FA, zizmor [source: PyPI incident report above]. PyPI also flags look-alike names at project creation and processed 2,000+ malware reports in 2025 [source: https://blog.pypi.org/posts/2025-12-31-pypi-2025-in-review/].
- **Update bots** (awareness until the project is on GitHub): Dependabot supports `package-ecosystem: "uv"` with an optional `cooldown: default-days: 7`; uv docs note "some use cases ... not yet working" (astral-sh/uv#2512). Renovate updates `pyproject.toml` + `uv.lock`, has `lockFileMaintenance` and `minimumReleaseAge` [source: https://docs.astral.sh/uv/guides/integration/dependabot/, .../renovate/]. GitHub's support table lists uv "v0.11" while this machine writes locks with 0.13.5; compatibility not tested.
- **Pinning policy**: `uv add x` writes a lower bound (`"pydantic-settings>=2.16.3"`) [local]; exact versions live in `uv.lock`. Applications/analyses: ranges in `pyproject.toml` + committed lock. Libraries: ranges only, never `==` in metadata ("overly-restrictive") [source: https://packaging.python.org/en/latest/discussions/install-requires-vs-requirements/].
- **Fewer dependencies**: each one brings friends (`requests` pulled 4 more packages) [local]. Ask "is it in the standard library?" before `uv add`.
- **Name traps (typo-/slopsquatting)**: import name and PyPI name differ. Verified today on PyPI [local]: `dotenv` = "Deprecated package" (correct: `python-dotenv`); `sklearn` = deprecated stub (correct: `scikit-learn`); `bs4` = dummy (correct: `beautifulsoup4`); `yaml`, `dateutil`, `cv2` do not exist (correct: `PyYAML`, `python-dateutil`, `opencv-python`); `PIL` is a 1.1.6 relic (correct: `Pillow`). An AI assistant can invent plausible package names; check the PyPI page before `uv add`.
- **Licences**: `uvx pip-licenses --python .venv/bin/python --format=markdown` listed e.g. `chardet 4.0.0 | LGPL`, `certifi | MPL 2.0`, `requests | Apache` [local]. Awareness: permissive (MIT/BSD/Apache) vs copyleft (GPL/AGPL) matters when distributing [memory]. Own project: `license = "MIT"` as an SPDX string per PEP 639; the table form is deprecated [source: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/].
- **SBOM** = ingredient list of software (CycloneDX / SPDX; PEP 770 Final lets wheels carry SBOMs) [source: https://peps.python.org/pep-0770/]. **OpenSSF Scorecard** = automated 0-10 health checks (Pinned-Dependencies, Token-Permissions, Dangerous-Workflow, Branch-Protection, Dependency-Update-Tool, SAST, Security-Policy, Vulnerabilities, Maintained, ...) viewable at scorecard.dev [source: https://github.com/ossf/scorecard]. One slide each.
- **OWASP Top 10:2025** names this brief's topics: A03 Software Supply Chain Failures, A09 Security Logging and Alerting Failures, A10 Mishandling of Exceptional Conditions [source: https://top10.owasp.org/2025].

## 5. Logging norms (Python 3.14.9) [local unless tagged]

### 5.1 Facts to teach

- Decision table from the official HOWTO [source: https://docs.python.org/3.14/howto/logging.html]: normal program output of a CLI -> `print()`; status/diagnostics -> `logger.info()` / `logger.debug()`; "something odd, still working" -> `logger.warning()`; error the caller must handle -> raise an exception; error you caught and are not re-raising -> `logger.error()` / `logger.exception()`.
- Levels: DEBUG 10, INFO 20, WARNING 30, ERROR 40, CRITICAL 50; default threshold WARNING.
- Unconfigured logging: `debug`/`info` vanish; WARNING+ goes to stderr as a bare message via the "last resort" handler.
- `logging.basicConfig()` "does nothing if the root logger already has handlers configured, unless ... force is set to True" [source: https://docs.python.org/3.14/library/logging.html]; verified: second call ignored, `force=True` works. Bare `basicConfig()` uses `%(levelname)s:%(name)s:%(message)s` and keeps WARNING.
- Logs go to **stderr**, results to **stdout**: `python run_job.py 2>/dev/null` printed nothing; `cli.py ... 2>/dev/null` printed only `0.2817%`.
- `logger.exception("msg")` = ERROR + traceback, only inside `except`; called outside it prints `NoneType: None`. `logger.error(..., exc_info=True)` is equivalent.
- Lazy formatting matters: `log.debug("value=%s", obj)` never called `obj.__str__` while DEBUG was off; `log.debug(f"value={obj}")` did (ruff `G004`).
- `logging.warn` / `Logger.warn` still exist in 3.14 but emit `DeprecationWarning` ("use 'warning' instead"); ruff `G010` is on by default and auto-fixable.
- `logging.captureWarnings(True)` routes `warnings.warn` into logger `py.warnings`.
- 3.14 news: `QueueListener` is a context manager [source: whatsnew/3.14]; nothing a beginner needs.
- Notebooks: if `basicConfig` appears to do nothing, a handler already exists; use `force=True` [memory, not tested in Jupyter].

### 5.2 Minimal module pattern + one configuration point

In every module: `logger = logging.getLogger(__name__)` (after `import logging`). In the single entry point only: `setup_logging(level="INFO", log_dir=Path("logs"))`. The configuration function (condensed layout; `RedactSecretsFilter` is described in 5.3):
```python
def setup_logging(level: str = "INFO", log_dir: Path | None = None) -> None:
    handlers: dict = {
        "console": {"class": "logging.StreamHandler", "stream": "ext://sys.stderr",
                    "formatter": "plain", "filters": ["redact"]}
    }
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {"class": "logging.handlers.RotatingFileHandler",
                            "filename": str(log_dir / "run.log"), "maxBytes": 1_000_000,
                            "backupCount": 3, "encoding": "utf-8",
                            "formatter": "plain", "filters": ["redact"]}
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,  # keep loggers created at import time alive
        "filters": {"redact": {"()": RedactSecretsFilter}},
        "formatters": {"plain": {"format": "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                                 "datefmt": "%Y-%m-%dT%H:%M:%S%z"}},
        "handlers": handlers,
        "root": {"level": level, "handlers": list(handlers)},
        "loggers": {"urllib3": {"level": "WARNING"}},  # quieten a chatty third-party library
    })
    logging.captureWarnings(True)
```
Output: `2026-11-19T14:44:14+0800 INFO     fxlab.prices: fetching USDCNY`, and for a caught error `ERROR run_job: fetch failed` followed by the full traceback; the same lines land in `logs/run.log`.
- A simpler first lesson is `logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s: %(message)s")` in `main()`; introduce `dictConfig` only when a file handler is wanted.
- Library etiquette [source: logging HOWTO]: a package never configures logging on import; at most `logging.getLogger(__name__).addHandler(logging.NullHandler())`; "do not log to the root logger" (ruff `LOG015`, on by default).

### 5.3 Never log secrets

```python
_SECRET_PATTERN = re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\b(\s*[=:]\s*)(\S+)")


class RedactSecretsFilter(logging.Filter):
    """Last line of defence: mask 'api_key=xxx' style fragments."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()  # merge msg % args first
        redacted = _SECRET_PATTERN.sub(r"\1\2***", message)
        if redacted != message:
            record.msg, record.args = redacted, None
        return True
```
- This filter turned `logger.debug("... api_key=%s", key)` into `api_key=***` in console and file. **But** it only rewrites the message: the traceback printed by `logger.exception` still showed a source line containing a literal key. A filter is the last line of defence; the rules are: keep secrets in `SecretStr`, log identifiers not values, never log whole config dicts, request headers or `os.environ`.
- OWASP's exclude list: passwords, access tokens, session IDs, connection strings, encryption keys, payment data, sensitive personal data; file paths and internal hostnames need care [source: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html].
- `logs/` belongs in `.gitignore` (a personal global ignore file may already ignore `*.log` on your machine, but collaborators will not have it).

### 5.4 Structured logging (awareness)

- Idea: one JSON object per event so machines can filter. Stdlib-only formatter (10 lines) printed `{"ts": "...", "level": "INFO", "logger": "fxlab.prices", "msg": "下载完成", "symbol": "USDCNY", "rows": 250}` using `extra={...}`; structlog 26.1.0 on 3.14 printed `{"symbol": "USDCNY", "age_days": 3, "event": "stale_data", "level": "warning", "timestamp": "..."}` [local]. Not needed for a solo project; mention and move on.

## 6. Error-handling norms [local unless tagged]

### 6.1 Rules with the evidence behind each

| Rule | Evidence / detail |
|---|---|
| Fail fast, close to the cause | missing config stops at startup with one clear line (3.2), not 20 minutes into a run |
| Catch specific exceptions | `KeyboardInterrupt` and `SystemExit` are not `Exception` subclasses, so `except Exception` keeps Ctrl-C working while bare `except:` swallows it; `FileNotFoundError -> OSError -> Exception`; `TimeoutError` is an `OSError` |
| Never `except: pass` | ruff defaults flag `E722`, `BLE001`, `S110`, `S112` |
| Small custom hierarchy | `FxLabError(Exception)` + `ConfigError`, `DataDownloadError`, `DataValidationError`; top level catches only the base class |
| Chain causes | `raise DataValidationError(...) from exc` prints "The above exception was the direct cause..."; ruff `B904` flags a missing `from` (needs `extend-select = ["B"]`) |
| Add context, do not lose it | `exc.add_note("hint: ... row 42 of prices.csv")` (3.11+) appears under the traceback |
| Validate at the boundary | parse CLI args / CSV / API JSON once into trusted values; inner functions stay simple |
| Do not validate with `assert` | `python -O` removed the check: `paid -5` (ruff `S101`; allow in tests) |
| Avoid silent coercion | `pd.to_numeric(..., errors="coerce")` turned `'N/A?'` into `nan` without a word; `errors="raise"` + a `DataValidationError` named the bad cell (pandas 3.1.1) |
| `finally` must not `return` | swallowed a `ValueError` completely; `SyntaxWarning` on 3.14; ruff `B012` (default) |
| Exit codes | 0 success, 1 failure, 2 usage error (argparse does this itself), 130 after Ctrl-C (unhandled `KeyboardInterrupt` also gave 130); `sys.exit("msg")` prints to stderr and exits 1; use `sys.exit`, not `exit()` (`PLR1722`, default) |
| Unexpected bug = crash loudly | `--bug` produced a traceback and exit 1; no catch-all that hides it |

### 6.2 Exception hierarchy, boundary validation, CLI skeleton

Ran: `7.10 7.12` -> `0.2817%` exit 0; `7.10 abc` -> `ERROR fxlab.cli: price #2 is not a number: 'abc'` exit 1; `--nope` -> usage text, exit 2.
```python
class FxLabError(Exception):
    """Base class for every error this project raises on purpose."""


class ConfigError(FxLabError): ...  # missing or invalid configuration
class DataDownloadError(FxLabError): ...  # source unreachable or unusable answer
class DataValidationError(FxLabError): ...  # data violates an assumption


def parse_prices(raw: list[str]) -> list[float]:
    """Boundary validation: turn untrusted text into trusted numbers or fail loudly."""
    prices: list[float] = []
    for position, text in enumerate(raw, start=1):
        try:
            value = float(text)
        except ValueError as exc:
            raise DataValidationError(f"price #{position} is not a number: {text!r}") from exc
        if value <= 0:
            raise DataValidationError(f"price #{position} must be positive, got {value}")
        prices.append(value)
    if len(prices) < 2:
        raise DataValidationError("need at least 2 prices to compute a return")
    return prices


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)  # argparse exits with code 2 on usage errors
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    try:
        prices = parse_prices(args.prices)  # raises DataValidationError(...) from exc
        print(f"{simple_return(prices):.4%}")  # the RESULT goes to stdout; logs go to stderr
        return EXIT_OK
    except FxLabError as exc:  # expected, explainable failures
        logger.error("%s", exc)
        logger.debug("details", exc_info=True)  # traceback only in verbose mode
        return EXIT_FAILURE
    except KeyboardInterrupt:
        logger.warning("interrupted by user")
        return EXIT_INTERRUPTED


if __name__ == "__main__":
    sys.exit(main())
```

### 6.3 Network calls: timeout, retry, idempotent download, atomic write

- `requests`: "By default, requests do not time out unless a timeout value is set explicitly"; "By default, Requests does not retry failed connections" [source: https://requests.readthedocs.io/en/latest/user/advanced/]. Use `timeout=(3.05, 30)` (connect, read); ruff `S113` flags a missing timeout (needs `S`).
- Retry only what is safe and transient, a bounded number of times, with growing waits:
```python
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504),
              allowed_methods=("GET", "HEAD"))
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry))
```
- tenacity 9.2.1 for arbitrary functions [local]:
  `@retry(retry=retry_if_exception_type((TimeoutError, ConnectionError)), stop=stop_after_attempt(4), wait=wait_exponential_jitter(multiplier=0.1, max=2), before_sleep=before_sleep_log(logger, logging.WARNING), reraise=True)`.
  Logged `Retrying ... in 0.172 seconds as it raised TimeoutError`, succeeded on attempt 3, gave up after 4. **`initial=` is deprecated** (`DeprecationWarning: The 'initial' parameter is deprecated, use 'multiplier' instead`). A blanket `@retry` also re-ran a deterministic `ValueError` three times: retry lists must name transient errors only.
- Idempotent + atomic download (ran against pypi.org): skip if the target exists, `raise_for_status()`, stream to a temp file in the same directory, `os.replace` to the final name, wrap `requests.RequestException` in `DataDownloadError`. Output: `saved data/raw/pypi_requests.json (192973 bytes, sha256=bcfc6a202592)`, second run `skip, already downloaded`, 404 -> `ERROR ... could not download ...: 404 Client Error`.
- Atomic write helper (ran; crash simulated with a failing `os.fsync`):
```python
def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as tmp:
            tmp.write(text)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)  # atomic rename; temp file must be on the same filesystem
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
```
  Naive `open("w")` + crash left `['date,close']` (data destroyed); the atomic version left the old two-line file intact and no leftover temp file.
- Design habit for market data: raw downloads are immutable and date-stamped (`data/raw/usdcny_2026-11-18.csv`); re-running a day never rewrites another day [practice].
- Python 3.14 `tarfile.extractall()` refused `../evil.txt` by default (`OutsideDestinationError`); older tutorials warn this is unsafe by default [local].

## 7. Secure-coding lints with ruff 0.17.2 [local]

- Defaults: 407 rules. Relevant ones already on: `E722`, `BLE001`, `S102`, `S110`, `S112`, `B012`, `LOG001/002/009/014/015`, `G010/G101/G201/G202`, `TRY002/004/201/203/401`, `PLW1508` (non-string env default), `PLW1510` (`subprocess.run` without `check`), `PLR1722`, `SIM115`. Default-set history: 0.16.0 went from 59 to 413 rules; 0.17.0 (2026-10-09) removed seven `DTZ` rules from the defaults [source: https://astral.sh/blog/ruff-v0.16.0, https://github.com/astral-sh/ruff/releases/tag/0.17.0, https://docs.astral.sh/ruff/default-rules/].
- On the deliberately bad file the defaults found 9 issues, old-style `--select E4,E7,E9,F` found 1, `--select S` found 23: `S105/S106/S107` hardcoded password names, `S113` no timeout, `S501` `verify=False`, `S310` `urlopen`, `S605/S602/S607` shell use, `S307` `eval`, `S301` pickle, `S506` `yaml.load`, `S608` SQL built from strings (twice), `S311` `random` for tokens, `S324` md5, `S306` `mktemp`, `S108` `/tmp/...`, `S103` chmod 777, `S101` assert, `S110`, `S112`, `S102`. Bandit 1.9.4 reported the same set plus import notes and severity levels; no need to install bandit separately.
- `S4xx` import rules are preview-only; `S` rules have no autofix [source: https://docs.astral.sh/ruff/rules/].
- Recommended project config (validated: bad files flagged, the good snippets in this brief pass):
```toml
[tool.ruff.lint]
# extend-select ADDS to Ruff's defaults; `select` would REPLACE them.
extend-select = [
    "S",    # flake8-bandit: basic secure-coding checks
    "G",    # logging format mistakes, e.g. f-strings inside log calls
    "B",    # the rest of bugbear, e.g. B904 `raise ... from err`
    "T20",  # stray print() in library code
    "DTZ",  # naive datetimes (time zones matter for market data)
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]        # pytest relies on plain assert
"scripts/**" = ["T20"]       # scripts may print their results
"src/*/cli.py" = ["T20"]     # the CLI prints its result to stdout on purpose
"notebooks/**" = ["T20"]
```
- Do **not** add the whole `TRY` group for beginners: `TRY400` fired on the intentional `logger.error("%s", exc)` for expected errors, `TRY300`/`TRY003` (and `EM101` from the separate `EM` group) are style opinions. The five sensible `TRY` rules are already defaults.
- For analysis code note `S311` is a false positive for simulations (`random` with a seed is correct there; `secrets.token_urlsafe()` is for tokens) and `S301` fires on every pickle load: explain, then `# noqa: S311` with a reason, or ignore per file.
- Ruff 0.17 assumes Python 3.11 when no version is configured [source: ruff 0.17.0 release notes]; set `requires-python` so the formatter/linter target is explicit (see finding 9).

## 8. Data and privacy hygiene

Verified ignore block (`git check-ignore -v` + `git add -A` in `lab/ignrepo`) [local]:
```gitignore
# data: keep the folder structure, never the contents
data/**
!data/**/
!data/**/.gitkeep
!data/README.md
!data/sample/**
# bulky / generated artefacts
*.parquet
*.feather
*.h5
*.pkl
*.sqlite
logs/
output/
```
- Result: `data/raw/usdcny_2026.csv`, `*.parquet`, `model.pkl`, `logs/`, `output/` ignored; `.gitkeep` files, `data/README.md`, `data/sample/tiny_prices.csv`, notebooks and source staged.
- Order matters: `data/sample/tiny.parquet` was still ignored because the later `*.parquet` line wins over the earlier `!data/sample/**`.
- Reading `git check-ignore -v`: a line whose pattern starts with `!` means the file is **not** ignored (the command still exits 0); confusing for beginners.
- What must stay out of Git, and why: (1) large files: GitHub warns above 50 MiB, "blocks files larger than 100 MiB", wants repos "ideally less than 1 GB" [source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github]; history keeps every version forever; (2) licensed vendor data: redistribution is usually forbidden by contract [memory]; (3) personal data (client lists, account numbers, anything under PIPL/GDPR) [memory]; (4) secrets; (5) regenerable outputs.
- Commit instead: the download script, a tiny synthetic or public sample under `data/sample/`, and `data/README.md` describing source, licence, retrieval date and how to rebuild.
- Find big files before committing: `uvx git-filter-repo --analyze` wrote `path-all-sizes.txt` etc. under `.git/filter-repo/analysis/` [local].
- Notebooks: outputs embed data; `nbstripout` (3.6) or "Clear all outputs" before committing.
- Awareness only: **Git LFS** stores pointer files in Git and content elsewhere (2 GB per file on GitHub Free) [source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage]; **DVC** 3.67.1 tracks data with small `.dvc` files in Git and the content in a cache/remote (`dvc init`, `dvc add`, `dvc push/pull`) [source: https://doc.dvc.org/start]. Neither is needed until data must be shared or versioned.

## 9. Changed recently (older tutorials now mislead)

| Old belief | Today |
|---|---|
| Ruff checks only E/F unless you `select` more | ~400 default rules since 0.16; `select` narrows, `extend-select` adds [local][source] |
| "Use pip-audit / safety; uv has nothing" | `uv audit` (experimental), `UV_MALWARE_CHECK`, `uv export --format cyclonedx1.5` [local] |
| `requirements.txt` + `pip freeze` is the lock | `uv.lock` with hashes; standard `pylock.toml` (PEP 751) exists; `pip-audit --locked` reads it [local][source] |
| Update immediately to latest | cooldown (`exclude-newer`, pip `--uploaded-prior-to`, Dependabot `cooldown`, Renovate `minimumReleaseAge`) is mainstream after 2025-26 incidents [source] |
| "Install gitleaks" as the default answer | gitleaks is in maintenance; Betterleaks is the successor; `gitleaks detect/protect` are deprecated spellings [source] |
| `pip install trufflehog` | obsolete v2 on PyPI; v3 is a Go binary, AGPL [local][source] |
| `git filter-branch` or BFG to purge | git itself warns against filter-branch; GitHub Docs use `git-filter-repo --sensitive-data-removal` (>= 2.47) [local][source] |
| `except A, B:` is a Python 2 bug | valid in 3.14; ruff format produces it when targeting py314 [local] |
| `return` in `finally` is merely bad style | `SyntaxWarning` in 3.14 [local] |
| `python-dotenv` auto-magically everywhere | `uv run --env-file`, and pydantic-settings reads `.env` itself [local] |
| pydantic v1 `class Config: env_file = ...`, `from pydantic import BaseSettings` | that import now raises `PydanticImportError: BaseSettings has been moved to the pydantic-settings package`; use `model_config = SettingsConfigDict(...)` [local] |
| tenacity `wait_exponential_jitter(initial=...)` | `multiplier=`; `initial` deprecated in 9.2.1 [local] |
| tar extraction is unsafe by default | 3.14 default filter blocks path traversal [local] |
| `license = {text = "MIT"}` | SPDX string `license = "MIT"` (PEP 639) [source] |
| OWASP Top 10 = 2021 list | 2025 edition adds supply chain (A03) and exceptional conditions (A10) [source] |
| Twelve-factor is a frozen Heroku document | open-sourced 2024, rewrite in progress, published text still 2017 [source] |

## 10. Pitfalls a beginner will hit (ranked by likelihood here)

1. First `git commit` fails with the gpg error (finding 1).
2. `git add -A` stages `.env` because `uv init`'s `.gitignore` lacks it; adding the rule later does not untrack it.
3. "I deleted the key in the next commit, so it is gone."
4. `.env` values not visible when using `uv run` without `--env-file`; or `load_dotenv()` silently returning `False`.
5. A space in an unquoted `.env` value silently drops the rest of the file under `uv run --env-file`.
6. Env values are strings: `os.getenv("TIMEOUT", 10)` (ruff `PLW1508`), `"False"` is truthy.
7. pydantic-settings `extra_forbidden` on unknown `.env` keys; validation errors echoing secret values.
8. Notebook outputs committed with data or keys inside.
9. `logging.info(...)` on the root logger, `basicConfig` called twice, `print` debugging left in library code, f-strings in log calls.
10. `except Exception: pass`, or logging an error and continuing with bad data.
11. `requests.get(url)` without timeout hanging a batch job forever; retry decorators without a stop condition.
12. Writing results with `open(path, "w")` and getting a half-written CSV after a crash.
13. `uv add` fixing the direct dependency while vulnerable transitive pins stay in `uv.lock`.
14. Treating `uv audit` green as proof of safety (experimental; known-vulnerability lists only).
15. Installing a package by its import name (`dotenv`, `sklearn`, `bs4`) or a name suggested by an AI without checking PyPI.
16. Running `detect-secrets scan` without `--no-verify` (candidate secrets are sent to provider APIs for verification).
17. `uvx pip-audit` with no arguments auditing the wrong environment.
18. Large data files committed once: the repo stays big forever.

## 11. Recommendations for the course

**Teach first (in this order, each with a 10-minute hands-on):**
1. Secrets block in `.gitignore` + `.env` + `.env.example` before any commit; prove it with `git check-ignore -v .env` and `git status`.
2. Config from the environment: `require_env` (5 lines) then the `Settings` class; make a missing key fail at startup.
3. The leak drill in a throwaway repo with a fake key: commit, "delete", find it with `git log -S`, then say "rotate first". `git-filter-repo` as an instructor-run demo, not a required skill.
4. Logging: module logger, one `basicConfig` in `main()`, levels, `logger.exception`, `%s` formatting, stdout vs stderr.
5. Errors: one base exception + three subclasses, `raise ... from`, boundary validation of a price CSV, exit codes checked with `echo $?`.
6. Robust I/O: timeout, bounded retry, skip-if-exists, atomic write (the "crash in the middle" demo is memorable).
7. Dependencies: commit `uv.lock`, `uv sync --locked`, `uv audit` on a deliberately old pin, the two-step fix, `exclude-newer`.
8. Ruff `extend-select` block; fix 3-4 findings on the learner's own code, discuss one justified `# noqa`.
9. Data hygiene: data ignore block, `data/README.md`, strip notebook outputs.

**Awareness only (one screen each):** twelve-factor as a list, OWASP Top 10:2025, Dependabot/Renovate, GitHub secret scanning + push protection, SBOM, Scorecard, licences, Git LFS/DVC, structured logging/structlog, keychain/secret managers, Betterleaks/gitleaks/TruffleHog names.

**Skip:** Vault/KMS, Docker/Kubernetes secrets, Sigstore/SLSA/attestations, OpenTelemetry, `QueueHandler`, `ExceptionGroup`/`except*`, async, BFG, GPG signing setup, `logging.config.fileConfig`.

**Sensible defaults to hard-code in templates:** ignore blocks from 3.1 and 8; `Settings` from 3.2; log format `%(asctime)s %(levelname)-8s %(name)s: %(message)s` at INFO with `-v` for DEBUG; exit codes 0/1/2/130; `TIMEOUT = (3.05, 30)`; `Retry(total=3, backoff_factor=0.5)` for GET; ruff block from 7; `[tool.uv] exclude-newer = "7 days"`; CI later: `uv sync --locked`, `uv run ruff check`, `uv audit` (non-blocking while experimental) or `uvx pip-audit`.

**Applying to the learner's existing project (if any; often no Git, no tests yet):** before `git init`, search for secrets and bulky data, write `.gitignore`, strip notebook outputs; only then make the first commit, so no history cleanup is ever needed. Both commands work with macOS grep/find [local]:
`grep -rniE "api_key|token|password|secret" --include="*.py" --include="*.ipynb" .` (the `-i` matters: without it `API_KEY = ...` was missed) and
`find . -type f -size +10M -not -path '*/.venv/*' -not -path '*/.git/*'`.

**Plain-Chinese analogies that fit:**
- 密钥 = 家门钥匙；`.env` = 放在自家抽屉里；`.env.example` = 只贴标签的空钥匙钩；提交到 Git = 把钥匙照片印进了每一本账本。
- Git 历史 = 监控录像，后来把钥匙收起来，录像里它还在；轮换密钥 = 换锁（唯一真正有效的补救）；重写历史 = 把账本全部重抄，但别人手里的复印件收不回。
- `SecretStr` = 银行卡号打码显示；push protection = 寄快递前的安检机；本地 hook = 安全带，可以不系，所以服务器端还要有气囊。
- `pyproject.toml` = 菜谱（"面粉 500 克以上"）；`uv.lock` = 带批次号和防伪码的购物小票；hash = 防伪码；`uv audit` = 拿小票去对食品召回名单；cooldown = 新菜先让别人试吃一周。
- typosquatting = "康帅傅"冒充"康师傅"；SBOM = 配料表；Scorecard = 餐厅卫生评级。
- 日志 = 行车记录仪 / 黑匣子，`print` = 随口喊一声；日志级别 = 天气预警颜色；`logger.exception` = 事故报告附现场照片（traceback）。
- fail fast = 保险丝早跳闸；`except: pass` = 把烟雾报警器的电池拔了；边界校验 = 进门安检一次，屋里不再反复查。
- 退出码 = 交给自动化流程的成绩单（0 及格）；timeout = 电话响 30 秒没人接就挂；带退避的重试 = 隔一会儿再打，间隔越来越长，最多三次；幂等 = 电梯按钮按一次和按十次一样；原子写入 = 先在草稿纸写完，再一次性换上正式页。
- 数据不进仓库 = 仓库放菜谱不放食材；授权数据 = 借来的书不能复印分发。

## 12. Could not verify today

- gitleaks / Betterleaks / TruffleHog behaviour (not runnable via `uvx`); only READMEs and release pages were read. Betterleaks v2 CLI may still change.
- Dependabot's uv support against a `uv.lock` written by uv 0.13.5 (GitHub lists uv "v0.11"); Dependabot alert pricing/availability wording.
- `uv audit` open-bug status beyond a search-result summary of issue #22102.
- iCloud behaviour for `.env` files and conflict copies; Jupyter-specific logging behaviour; `%dotenv` magic at runtime; `ps`/shell-history exposure of CLI arguments.
- Legal statements about data licences and PIPL/GDPR are general knowledge, not checked against sources.
- GitHub API calls were rate-limited once; release dates came from the HTML release pages instead.
