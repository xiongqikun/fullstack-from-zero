# Brief: review-testing-practice

Engineering practice for code quality: code review, testing, safe refactoring (norms, not tool flags).
Raw material for lesson builders. Written 2026-11-19 on the reference Mac (plan G7) (macOS 27.2 arm64, zsh).

Tags: **[local]** = I ran it here today; **[source: URL]** = read in a primary source today; **[memory]** = not verified today.
Source text is paraphrased throughout; tool output is quoted verbatim (shortened).
`<S>` = `<scratch>/research/review-testing-practice`
(scratch space: it can be wiped by a reboot, so the load-bearing snippets are embedded below).

---

## 1. Headline findings

1. **Best teaching arc for "messy script -> maintainable code"** (verified end to end on a deliberately bad moving-average backtest script): (a) pin today's behaviour with a characterization / golden test, (b) refactor in small behaviour-preserving steps into "functional core + imperative shell", (c) only then change behaviour, one bug at a time, each with a regression test. Four successive refactoring steps all reproduced the legacy output; fixing the script's same-bar look-ahead bug then moved the headline Sharpe on the 15-row fixture from **+3.35 to -2.07**. [local]
2. **Lint-clean is not correct.** ruff 0.17.2 with default rules reports 3 findings in the legacy script (unsorted imports, mutable default, bare except). Nothing flags the look-ahead bug, the mutation of the caller's DataFrame, the import-time side effects, or magic numbers used in arithmetic. Only tests and review catch those. [local]
3. **Coverage is a map, not a grade.** A suite with zero meaningful assertions reached 100 % line and branch coverage on a function with a real bug; one hand-computed assertion found the bug. [local]
4. **Float comparison has three tools with three different defaults** and several traps that silently pass or confusingly fail (section 7.1). The worst one for time series: `numpy.testing.assert_allclose` ignores the index, so a series shifted by one day compares equal. [local]
5. **Look-ahead bias needs more than one detector.** Truncation invariance caught 5 kinds of future-data leaks but is blind to "trade on the same bar as the signal"; that needs an alignment test and/or a noise test (leaky Sharpe on pure noise +10.36 vs honest +0.04). [local]
6. **Mock sparingly.** An interaction-style mock test failed on a harmless refactor and passed on a look-ahead bug; the state-based test did the opposite (correct) thing. [local]
7. **Older tutorials mislead on tooling**: pytest 9 config (`[tool.pytest]`, `strict = true`), ruff's 400+ default rules, pandas 3 (copy-on-write; several classic idioms raise or silently do nothing), `pandera.pandas` import, Python >= 3.12 float `sum`. See section 3.
8. **Review norms converge across Google / GitLab / Microsoft**: approve when the change clearly improves code health (not when perfect); keep changes small (about 100-200 lines; 1000 is too large); label comment severity; respond within one business day; the author self-reviews first. Section 4.
9. **For a solo developer pairing with an AI assistant** the workable substitute for a human reviewer is: read your own full diff, demand evidence (command + output), get a review from a fresh context that did not write the code, and never accept a diff you cannot explain. Section 4.7-4.8.
10. **Flaky tests** have four classic causes in data code, each reproduced here: shared mutable state, unseeded randomness, set ordering, legacy global NumPy seed. Section 5.6.

---

## 2. What I verified and how

Throwaway uv project `<S>/lab` (src layout, repo-local git identity), Python 3.12.15, re-run on 3.14.9: **51 tests pass** on both. [local]

| Tool | Version resolved today | Tool | Version resolved today |
|---|---|---|---|
| pytest | 9.2.0 | numpy | 2.5.5 |
| pytest-cov / coverage | 7.1.0 / 7.17.3 | pandas | 3.1.1 |
| hypothesis | 6.170.15 | pandera | 0.36.0 |
| syrupy | 7.0.2 | mypy / pandas-stubs | 2.4.1 / 3.1.0.261029 |
| pytest-regressions | 2.11.0 | ruff (uv tool) / uv | 0.17.2 / 0.13.5 |

Commands that produced the environment (all succeeded) [local]:

```bash
export UV_CACHE_DIR="$TMPDIR/uv-cache"          # sandbox only
uv init --lib --name fxlab --python 3.12 .   # creates .git, .gitignore, pyproject.toml, src/fxlab/{__init__.py,py.typed}
uv add numpy pandas
uv add --dev pytest pytest-cov hypothesis pandera syrupy mypy pandas-stubs   # writes [dependency-groups] dev = [...] (pandas-stubs was added in a second call)
ruff format --check src tests && ruff check src tests && uv run mypy src && uv run pytest --cov
# -> 21 files already formatted / All checks passed! / Success: no issues found in 8 source files / 51 passed
```
`uv run ruff --version` also works here: it falls through to the globally installed uv tool (ruff 0.17.2). [local]

Lab map (paths under `<S>/lab`):
- `legacy/ma_backtest_legacy.py` - the deliberately smelly script (38 lines).
- `refactor_steps/step0..step3_*.py` + `test_every_step_keeps_behaviour.py` - each refactoring step checked against the same golden output.
- `src/fxlab/` - end state: `returns.py`, `signals.py`, `backtest.py` (pure core), `contracts.py`, `io.py`, `cli.py` (shell), `report.py` (dependency injection).
- `tests/` - `test_returns.py` (AAA, approx, parametrize), `test_properties.py` (Hypothesis), `test_lookahead.py` + `lookahead.py`, `test_contracts.py` (pandera), `test_golden.py` + `golden_io.py`, `test_characterization_legacy.py`, `test_regression_bugs.py`, `test_di.py`, `test_cli.py`, `conftest.py`.
- `demos/` - runnable evidence: `float_tolerance_demo.py`, `pandas3_old_idioms.py`, `flaky/`, `covtrap/`, `test_mock_vs_state.py`, `test_hypothesis_finds_bugs.py`, `complexity_before.py` / `complexity_after.py`, `bare_except_demo.py`, `type_hint_demo.py`, `pandera_model_demo.py`.

Web: WebSearch/WebFetch worked. A few pages returned no article body (Google Testing Blog post pages, two Fowler/Bernhardt pages); the Testing Blog feed did work. Gaps are listed in section 11.

---

## 3. What changed recently (where older tutorials now mislead)

| Area | Older tutorials say | True on this machine today |
|---|---|---|
| pytest config | `[tool.pytest.ini_options]`, `addopts = "--strict-markers"` | pytest 9.0 (2025-11-05) added a native-TOML `[tool.pytest]` table (also `pytest.toml`) and `strict = true`, which turns on strict_config, strict_markers, strict_xfail, strict_parametrization_ids. The old table still works; using both is an error ("Cannot use both [tool.pytest] ... and [tool.pytest.ini_options]"). [source: https://docs.pytest.org/en/stable/changelog.html] [source: https://docs.pytest.org/en/stable/reference/customize.html] [local] |
| pytest 9.x details | - | Python 3.9 dropped (9.0); `subtests` fixture built in (9.0); in 9.2 (2026-10-27) `ids`/`indirect`/`scope` of parametrize are keyword-only and, under strict markers, typos in `-m` expressions are errors. [source: changelog] [local for `-m`] |
| ruff defaults | "ruff only enables E and F by default" | ruff 0.16.0 (2026-07-23) raised the default set from 59 to 413 rules; 0.17.2 here enables 407. Default-on now: E722 bare-except, BLE001 blind-except, S110 try-except-pass, B006 mutable default, B015 pointless comparison, TRY002, I001 import sorting. Still off: C901, PLR09xx, PLR2004, T201, N8xx, D1xx, E501, E711/E712, E741, S101, NPY002, PD*. [source: https://github.com/astral-sh/ruff/releases/tag/0.16.0] [local: `ruff check --show-settings --isolated`] |
| pandas | chained assignment "works with a warning"; `fillna(method="ffill")`; `df.append`; `resample("M")`; `s[0]`; `applymap` | pandas 3.1.1: copy-on-write is always on. `df["sig"][mask] = 1` leaves `df` unchanged and only emits a `ChainedAssignmentError` warning; `fillna(method=...)` -> TypeError; `append`/`applymap` -> AttributeError; `resample("M")` -> ValueError (use `"ME"`); `s[0]` on a DatetimeIndex -> KeyError (use `.iloc[0]`); string columns have dtype `str`; parsed dates are `datetime64[us]` (not `ns`); `pct_change()` no longer forward-fills gaps. [local: `demos/pandas3_old_idioms.py`] |
| pandas.testing | "assert_frame_equal just compares values" | It also compares dtypes, index type and - in 3.1.1 - the index `freq`: a `bdate_range` index vs the same dates read from CSV fails with `Attribute "freq" are different` unless `check_freq=False`. `by_blocks` is deprecated (3.1). [local] [source: https://pandas.pydata.org/docs/reference/api/pandas.testing.assert_frame_equal.html] |
| NumPy random | `np.random.seed(0)` | Legacy global `RandomState`; docs recommend `rng = np.random.default_rng(seed)` and passing `rng` around. `assert_allclose(..., strict=True)` exists since 2.0. [source: https://numpy.org/doc/stable/reference/random/index.html] [local] |
| Python floats | "`sum([0.1]*10)` is not 1.0" | Still so on the system Python 3.9.6 (`0.9999999999999999`), but **no longer on 3.12.15 / 3.14.9**: float `sum` is now compensated and returns exactly 1.0. `0.1 + 0.2 == 0.3` is still False everywhere, so use that as the classroom example. [local] |
| pandera | `import pandera as pa` | Emits a FutureWarning; use `import pandera.pandas as pa`. Install extra is `pandera[pandas]`. [local] [source: https://pandera.readthedocs.io/en/stable/] |
| dev dependencies | `requirements-dev.txt`, `[tool.uv] dev-dependencies` | `uv add --dev X` writes `[dependency-groups] dev = [...]`. [local] |
| Hypothesis in CI | "set derandomize yourself" | A built-in `ci` profile activates when `CI` is set: derandomize=True, deadline=None, database=None, print_blob=True. [source: https://hypothesis.readthedocs.io/en/latest/reference/api.html] [local] |
| Test-shape debate | "the pyramid is the rule" | Google now frames it as trade-offs (SMURF: speed, maintainability, utilization, reliability, fidelity; 2024) and Fowler argues the pyramid/trophy/honeycomb fight is mostly about definitions (2021). Section 5.2. |
| AI pair-programming | "review style nits" | Official Claude Code guidance (2026) is: give the agent a runnable check, ask for evidence, review with a fresh subagent (`/code-review`), and do not fix every finding. Section 4.8. |

---

## 4. Code review norms

### 4.1 The standard (Google Engineering Practices)
- Approve once the change clearly improves overall code health, even if imperfect; the bar is improvement, not perfection, and a useful change should not wait days over polish. Never accept a change that makes code health worse (emergencies aside). [source: https://google.github.io/eng-practices/review/reviewer/standard.html]
- Facts and data beat opinions; the style guide is the authority on style; anything it does not cover is preference - follow existing code or let the author choose. Design is not a style matter and is argued on engineering principles.
- Minor optional points are prefixed `Nit:`. Teaching comments are welcome but marked non-blocking.
- Disagreement: try to agree from the guidelines, then talk live and write the outcome back on the change, then escalate. Do not let a change sit.

### 4.2 What a reviewer looks for
- Google's list: design, functionality (edge cases, concurrency), complexity (can a reader understand it quickly? is it more generic than today's problem needs?), tests (in the same change; would they fail if the code broke? are assertions clear?), naming, comments (explain *why*, not *what*), style, consistency, documentation, every line read, wider context, and say what is good. [source: https://google.github.io/eng-practices/review/reviewer/looking-for.html]
- Order of work: read the description and decide whether the change should exist; review the main part first and send design objections immediately; then the rest; reading the tests first often helps. [source: https://google.github.io/eng-practices/review/reviewer/navigate.html]
- Microsoft's playbook adds concrete questions: single responsibility per function? more than three arguments? unneeded functionality? errors handled explicitly? any personal data logged? tests in the same PR, sensible, edge cases covered? It also says: prefer "we"/"this line" over "you", ask questions rather than assert, explain why. [source: https://microsoft.github.io/code-with-engineering-playbook/code-reviews/process-guidance/reviewer-guidance/]

### 4.3 Size and speed (numbers worth teaching)

| Norm | Number | Basis |
|---|---|---|
| Reasonable change size | about 100 lines is usually fine, about 1000 usually too large; 200 lines in 1 file may be fine, across 50 files usually not | [source: https://google.github.io/eng-practices/review/developer/small-cls.html] |
| Merge request target | around 200 lines | [source: https://docs.gitlab.com/development/code_review/] |
| Review session | 200-400 lines at a time, under 500 lines/hour, at most about 60 minutes | [source: https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/] |
| Response time | at most one business day; respond at a natural break, do not interrupt focused work | [source: https://google.github.io/eng-practices/review/reviewer/speed.html] |

Also from the small-changes page: one self-contained change with its tests; keep refactorings in separate changes from features and bug fixes; a reviewer may reject a change just for being too large. Google's Testing Blog repeats this in 2024 (keep every pull request small and single-purpose) and 2026 (prefactoring: first restructure so the feature fits, as its own change). [source: https://feeds.feedburner.com/blogspot/RLXA - Testing Blog feed, posts of 2024-07-16 and 2026-07-21]

### 4.4 Change descriptions
First line: short, specific, imperative, able to stand alone in history, then a blank line. Body: what and why, the problem, why this approach, shortcomings, context that a reader will not find in the code. Vague one-liners that name neither the thing nor the reason are the anti-pattern. Re-read the description before merging because the change evolved during review. My examples for the course: good `Shift MA-crossover position one bar to remove look-ahead`; bad `fix`, `update code`, `wip`. [source: https://google.github.io/eng-practices/review/developer/cl-descriptions.html]

### 4.5 Writing comments: severity labels and Conventional Comments
- Google: be kind, comment on the code not the person, explain reasoning, and label severity: `Nit:` (minor), `Optional:` / `Consider:` (suggestion), `FYI:` (no action needed). If you had to ask what code does, the fix is clearer code or a code comment, not an explanation in the review thread. [source: https://google.github.io/eng-practices/review/reviewer/comments.html]
- Conventional Comments format (GitLab tells its engineers to use it) [source: https://conventionalcomments.org/] [source: https://docs.gitlab.com/development/code_review/]:

```
<label> [decorations]: <subject>

[discussion]
```
- Labels: praise, nitpick, suggestion, issue, todo, question, thought, chore, note (optional extras: typo, polish, quibble). Decorations: `(blocking)`, `(non-blocking)`, `(if-minor)`, plus topical ones such as `(security)`, `(test)`. Guidance: at least one sincere praise per review; pair an issue with a suggestion; use a question when unsure a problem is real.
- Examples in our domain (mine): `issue (blocking): signal uses close[t] and earns return[t]; shift the position one bar.` / `nitpick (non-blocking): rename d -> prices.` / `question: is 252 right for a crypto series that trades 365 days?`

### 4.6 Handling review comments (author side)
Do not take it personally; never answer in anger. If the reviewer did not understand the code, change the code (or add a code comment) rather than explaining in the thread - future readers will have the same question. When you disagree, explain trade-offs and ask what is being suggested. [source: https://google.github.io/eng-practices/review/developer/handling-comments.html] A 2026 Google Testing Blog tip adds: "Done" is fine when the fix is obvious; add a line of context when the change does not show how you addressed the comment, when you chose between options, or when an offline talk shaped the result. [source: Testing Blog feed, 2026-05-12] GitLab: push feedback changes as separate commits so the reviewer can see them. [source: https://docs.gitlab.com/development/code_review/]

### 4.7 Distilled checklists (ready to translate)
**Author, before asking for review** (Google author guide + GitLab author responsibilities + Microsoft author guidance):
1. One purpose per change; refactoring separated from behaviour change; roughly <= 200 changed lines.
2. Tests added or updated in the same change; format, lint, type-check and tests pass locally.
3. Read your whole diff yourself first: unrelated edits, debug prints, commented-out code, secrets, data files.
4. Description: imperative summary line; what and why; how it was verified (command + output); known limits.
5. Non-obvious decisions are explained in code comments or the description.
6. Golden / snapshot files changed? Say why, and show the before/after numbers.

**Reviewer**:
1. Do I understand what and why from the description? Should this change exist?
2. Design: right place, simplest thing that solves today's problem, no speculative generality.
3. Correctness: empty input, one row, NaN, zero volatility, duplicates, unsorted dates, first/last bar; for backtest code: can any value at date t depend on data after t?
4. Tests: present, would fail if the code were wrong, assert real expected values (not recomputed by the same formula), readable.
5. Readability: names, function size, nesting; comments say why; public functions have docstrings.
6. Errors: nothing swallowed, messages name the offending value; no print debugging left.
7. Style: leave to the formatter/linter; anything else is `Nit:`.
8. I read every line; I said at least one specific good thing; verdict = "is the codebase better with this?".

### 4.8 Reviewing alone, and reviewing AI-generated code
Solo self-review loop, verified in the lab repo [local]:

```bash
git status --short            # what did I touch?            ->  M src/fxlab/returns.py
git diff --stat               # how big is it?               ->  1 file changed, 2 insertions(+), 1 deletion(-)
git diff                      # read every line as if a stranger wrote it (git diff --staged after git add)
git diff --check              # whitespace slips             ->  src/fxlab/returns.py:30: trailing whitespace.
uv run pytest -q              # evidence                     ->  5 failed, 46 passed
git restore <file>            # throw the experiment away
```
In that run the diff contained a stray `print(drawdown)` and a silent `252 -> 250` change; the diff read-through shows both, and the one-character change turned 5 tests red (hand-computed Sharpe, snapshot, CLI, DI report, legacy equivalence) - a concrete demonstration that the safety net works. [local]
Other solo substitutes for a second pair of eyes: review the next morning; review in a different view than the editor; write the description first (if you cannot say what and why in three lines, the change is too big); use the Conventional Comments labels on your own notes. [memory - common practice]

AI-specific guidance from primary sources:
- GitHub Docs: run tests and static analysis first; check the code solves the *right* problem and fits the project; reject code that would be harder to fix than to rewrite; verify every suggested package exists, is maintained and licensed; watch for hallucinated APIs, silently ignored constraints, plausible-but-wrong logic, and **deleted or skipped tests**. [source: https://docs.github.com/en/copilot/tutorials/review-ai-generated-code]
- Claude Code docs: without something runnable, an agent can only judge completion by appearance, so give it a check that returns pass/fail (a test file, a linter, a script that diffs output against a fixture) and put that command in CLAUDE.md; always ask for evidence - the command it ran and its output; have the diff reviewed by a fresh subagent that never saw the conversation (`/code-review`, alias `/review`; with no target it reviews the branch's commits plus uncommitted changes; `--fix` applies findings); when reviewing against a spec, tell the reviewer to skip style, because a reviewer asked to find problems always finds something and fixing everything yields needless abstraction and tests for impossible cases. [source: https://code.claude.com/docs/en/best-practices.md] [source: https://code.claude.com/docs/en/code-review-local]
- OpenSSF (2025-08-01): the human stays accountable; assume AI code has flaws; verify dependencies (one cited study: 19.7 % of 2.23 M generated package references did not exist - "slopsquatting" risk); asking the model to critique and then improve its own answer helps; telling the model to play a security-expert persona is not recommended. [source: https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions]
- Simon Willison (2025-12-18): handing over unproven code pushes the real work onto the reviewer; the author must first watch the change work, and should attach an automated test that goes red when the implementation is reverted. Accountability stays with the human. [source: https://simonwillison.net/2025/Dec/18/code-proven-to-work/]
- GitLab: address the AI reviewer's comments before asking a human. [source: https://docs.gitlab.com/development/code_review/]

Red flags in AI-written *tests* (each reproduced locally unless marked):

| Red flag | Evidence |
|---|---|
| Expected value recomputed with the same formula as the code (tautology) | passes against a buggy `position_size`; hand-computed test fails `assert 2000.0 == 500 ± 5.0e-04` [local: `demos/covtrap/`] |
| No assertion, or a bare comparison without `assert` | test passes silently; ruff default rule B015 flags the pointless comparison [local] |
| `return x == y` instead of `assert` | passes with only `PytestReturnNotNoneWarning`; `filterwarnings = ["error"]` makes it fail [local] |
| Heavy mocking of pandas/own code | section 5.7 [local] |
| Tests deleted, skipped, xfailed, tolerances loosened, goldens regenerated to get green | named by GitHub Docs and by Kent Beck's list of TDD mistakes [source: https://newsletter.kentbeck.com/p/canon-tdd] |
| `try/except` that returns a default "to be safe" | turns a typo into the number 0.0 [local: `demos/bare_except_demo.py`] |
| Pre-2024 pandas idioms | several now raise or silently do nothing (section 3) [local] |

Rule of thumb for the learner: never merge a diff you cannot explain line by line; ask the assistant to explain it in plain Chinese, then break the implementation on purpose and watch a test go red.

---

## 5. Testing practice

### 5.1 What to test, what not to test
- Test behaviours through the public interface, not methods or private helpers; a test should only need to change when behaviour changes. [source: https://abseil.io/resources/swe-book/html/ch12.html]
- Do not test trivial code; check observable results instead of which internal calls were made. [source: https://martinfowler.com/articles/practical-test-pyramid.html]
- If you care that a behaviour keeps working, put a test on it (Google's rule of thumb for what must be tested). [source: https://abseil.io/resources/swe-book/html/ch11.html]
- Priority list for a backtest / data-analysis codebase (my synthesis): pure calculations with tiny hand-computed cases -> edge cases (empty, one row, NaN, zero volatility, duplicates, unsorted) -> invariants -> alignment/look-ahead -> validation at the I/O boundary -> one golden end-to-end run. Not worth testing: that pandas' `rolling().mean()` works, plot pixels, exact log wording, exploratory notebook cells.

### 5.2 The test pyramid and its critiques

| View | Claim | Basis |
|---|---|---|
| Pyramid (Cohn 2009, via Fowler 2012) | many fast unit tests, fewer service tests, very few UI tests; "ice-cream cone" is the anti-pattern; when a high-level test fails, add a unit test for it | [source: https://martinfowler.com/bliki/TestPyramid.html] |
| Google mix | about 80 % unit, 15 % integration, 5 % end-to-end; classify by *size* (small = one process, no I/O, no network, no sleep) as well as scope | [source: https://abseil.io/resources/swe-book/html/ch11.html] |
| Testing trophy (Dodds 2021) | static checks at the base, mostly integration tests; the closer tests are to real use, the more confidence | [source: https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications] |
| Fowler 2021 | pyramid vs trophy vs honeycomb mostly differ in what "unit" means (solitary vs sociable); what matters is fast, reliable, expressive tests with clear boundaries | [source: https://martinfowler.com/articles/2021-test-shapes.html] |
| SMURF (Google 2024) | judge tests on Speed, Maintainability, Utilization, Reliability, Fidelity; unit tests win all but fidelity | [source: Testing Blog feed, 2024-10-15] |

For this learner: "static checks (ruff, mypy) + many small pure-function tests + a handful of golden/contract tests + almost no end-to-end" is the pyramid in practice; separating I/O from computation is what makes the cheap tests possible.

### 5.3 Anatomy, naming, one behaviour per test
- pytest's own vocabulary: Arrange, Act (one action that triggers the behaviour under test), Assert, Cleanup. [source: https://docs.pytest.org/en/stable/explanation/anatomy.html] (Arrange-Act-Assert is usually credited to Bill Wake, 2001 [memory].)
- One behaviour per test; name the test after the behaviour and expected outcome (a name needing "and" is two tests); no loops/ifs in tests; prefer descriptive, self-contained tests over de-duplicated ones (DAMP over DRY). [source: https://abseil.io/resources/swe-book/html/ch12.html]
- Discovery rules: files `test_*.py` or `*_test.py`, functions `test*`, classes `Test*` without `__init__`. [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html]

Verified example (`tests/test_returns.py`) [local]:
```python
def test_simple_returns_matches_hand_computed_values():
    # Arrange: 100 -> 110 is +10%, 110 -> 99 is -10%
    prices = pd.Series([100.0, 110.0, 99.0])
    # Act
    result = simple_returns(prices)
    # Assert
    assert math.isnan(result.iloc[0])
    assert result.iloc[1:].tolist() == pytest.approx([0.10, -0.10])

@pytest.mark.parametrize(
    ("equity", "expected"),
    [
        pytest.param([100.0, 120.0, 90.0, 130.0], -0.25, id="one-drawdown"),
        pytest.param([100.0, 101.0, 102.0], 0.0, id="always-rising"),
        pytest.param([100.0], 0.0, id="single-point"),
    ],
)
def test_max_drawdown_known_cases(equity, expected):
    assert max_drawdown(pd.Series(equity)) == pytest.approx(expected)
```
Output line: `tests/test_returns.py::test_max_drawdown_known_cases[one-drawdown] PASSED`.

### 5.4 Fixtures vs helper functions
- Fixtures are for the Arrange step that needs a lifecycle or is shared: requested by argument name, default scope `function`, teardown after `yield`, shared through `conftest.py`, "factory as fixture" when a test needs several variants. [source: https://docs.pytest.org/en/stable/how-to/fixtures.html]
- Values a test's assertion depends on should be visible in the test body; use helpers with overridable defaults rather than mysterious shared constants. [source: https://abseil.io/resources/swe-book/html/ch12.html]
- Verified [local]: factory fixture `make_prices(n_days=250, seed=42)`; built-ins `tmp_path`, `monkeypatch`, `capsys`, `caplog`; a module-scoped fixture that runs the legacy script once cut that file from 2.34 s to 0.95 s (it must use `tmp_path_factory`, because `tmp_path` is function-scoped). A fixture defined in `tests/conftest.py` is invisible to tests outside `tests/` (`fixture 'small_prices' not found`).
- Helper modules: with `--import-mode=importlib`, `from tests.lookahead import ...` worked with or without `tests/__init__.py`; with the default `prepend` mode it needs `tests/__init__.py` (otherwise `ModuleNotFoundError: No module named 'tests'`). pytest's docs recommend `importlib` for new projects. [local] [source: goodpractices page]

### 5.5 Test data
- Prefer tiny inputs whose expected output can be computed by hand; state them in the test.
- Use non-default values (not 0, not "", not the first enum member) and a different value for each argument, so a test cannot pass when the code ignores or swaps inputs; cover boundaries; consider generated inputs. [source: Testing Blog feed, "Choosing Values for Robust Tests", 2026-06-04]
- Never commit real, large or licensed market data as fixtures; generate reproducible synthetic series (`np.random.default_rng(seed)`) or keep a 10-20 row CSV. [my recommendation]

### 5.6 Determinism and flaky tests
- A non-deterministic test teaches people to ignore red, which infects the healthy tests; quarantine and fix quickly. Causes: lack of isolation, async waits, remote services, time, resource leaks; always wrap the system clock so tests can substitute it. [source: https://martinfowler.com/articles/nonDeterminism.html]
- pytest's page lists uncontrolled system state, order dependence, and over-strict float assertions (use `pytest.approx`) as root causes. [source: https://docs.pytest.org/en/stable/explanation/flaky.html] Google: around 0.15 % flaky; tests lose value as flakiness approaches 1 %. [source: SWE book ch. 11]
- Reproduced in `demos/flaky/test_flaky_examples.py` [local]:

| Cause | Observation |
|---|---|
| Shared module-level cache mutated by another test | `a then b`: 1 failed, 1 passed; `b alone`: passed; `b then a`: 2 passed |
| Unseeded `default_rng()` and `mean() > 0` | 10 runs: 6 failed, 4 passed |
| `list(a_set)[0]` | fails for PYTHONHASHSEED 0, 2, 3, 5; passes for 1, 4 |
| `np.random.seed(0)` in one test, `np.random.rand()` in the next | passes in order, fails when run alone |

Fixes: no module-level mutable state (or reset it in a fixture); pass an explicit `rng`; sort before indexing; pass dates/clocks in as arguments.

### 5.7 Mocking sparingly
- Vocabulary (Meszaros via Fowler): dummy, fake, stub, spy, mock; state verification vs behaviour verification. Fowler remains a "classic" tester and worries about coupling tests to implementation. [source: https://martinfowler.com/articles/mocksArentStubs.html]
- Google: prefer real implementations when fast and deterministic; otherwise a fake; over-used stubs and interaction checks give brittle tests that fail on any internal change (change-detector tests); test state, not interactions. [source: https://abseil.io/resources/swe-book/html/ch13.html]
- Verified (`demos/test_mock_vs_state.py`): three moving-average implementations - original, an equivalent refactor (`rolling(window=window, min_periods=window)`), and a buggy one (`.shift(-1)`). [local]

| Test style | original | harmless refactor | look-ahead bug |
|---|---|---|---|
| `MagicMock` + `assert_called_once_with(3)` | pass | **FAIL** (false alarm) | **pass** (missed bug) |
| real Series, compare numbers | pass | pass | **FAIL** (caught) |

For this course: teach fakes plus dependency injection (section 6.5) and `monkeypatch` (section 6.6); postpone `unittest.mock`.

### 5.8 Coverage: a signal, not a target
- Coverage finds untested code; as a number it says little about test quality. Expect thoughtful testing to land in the high 80s-90s; be suspicious of 100 %; tests without assertions game it. Enough tests = bugs rarely escape and you are not afraid to change code. [source: https://martinfowler.com/bliki/TestCoverage.html]
- Google: coverage measures lines executed, not results checked; a target such as 80 % tends to become a ceiling. [source: SWE book ch. 11] Widely quoted Google guideline: 60 % acceptable, 75 % commendable, 90 % exemplary, with no ideal number - **not verified against the primary page today** (article body not retrievable). [memory/secondary]
- Verified trap (`demos/covtrap/`) [local]:
```
risk.py       6      0      4      0   100%        <- two tests, no assertion on the result
...
E       assert 2000.0 == 500 ± 5.0e-04             <- one hand-computed assertion finds the bug
```
- Verified config and commands [local]: `uv run pytest --cov` -> `Required test coverage of 85.0% reached. Total coverage: 98.63%`; `--cov-fail-under=100` -> `FAIL Required test coverage of 100% not reached` and exit code 1. Rounding quirk: with the default precision of 0, `--cov-fail-under=99` at 98.63 % printed the FAIL line but exited 0; with `--cov-precision=2` it exited 1 - so set the floor comfortably below the current value. coverage writes `.coverage` (add it and `htmlcov/` to `.gitignore`; `.pytest_cache/` and `.hypothesis/` ignore themselves). `exclude_also` (coverage >= 7.2) adds exclusions without losing `# pragma: no cover`. [source: https://coverage.readthedocs.io/en/latest/config.html]
- Teaching stance: turn on branch coverage, read the "Missing" column to decide what to test next, set `fail_under` as a floor slightly below current, never chase 100 %.

### 5.9 A regression test for every bug fix
First write a test that exposes the bug, then fix; a bug also signals a gap, so look for sibling cases. [source: https://martinfowler.com/bliki/SelfTestingCode.html] Verified red -> green [local]:
```
>       assert result.loc["2024-01-08", "strategy_return"] == pytest.approx(0.0)
E         Obtained: 0.028126213592232996      <- legacy behaviour: earns the bar that produced the signal
E         Expected: 0.0 ± 1.0e-12
```
After the fix (position = signal shifted one bar) `tests/test_regression_bugs.py` passes: 3 regression tests, each named after its symptom.

### 5.10 TDD: red-green-refactor, and when it helps
- Canon TDD (Beck, 2023): write a list of test scenarios; turn exactly one into a runnable test; make it pass; optionally refactor; repeat. Typical mistakes: assertion-free tests, writing all tests first, copying computed output into expected values, refactoring while making the test pass, abstracting too early. [source: https://newsletter.kentbeck.com/p/canon-tdd]
- Fowler: the most common failure is skipping the refactor step; what matters most is ending up with self-testing code, whichever order it was written in. [source: https://martinfowler.com/bliki/TestDrivenDevelopment.html] [source: SelfTestingCode]
- For this learner (my judgement): test-first is natural for bug fixes and for pure functions with a known worked example; for exploratory research where the answer is unknown, explore first, then pin with hand-computed cases and characterization tests before trusting or refactoring.

### 5.11 Recommended pytest/coverage configuration (verified as written) [local]
```toml
[tool.pytest]
minversion = "9.0"
testpaths = ["tests"]
addopts = ["--import-mode=importlib", "-ra"]
strict = true
# markers = ["slow: takes more than a second"]
# filterwarnings = ["error"]

[tool.coverage.run]
source = ["fxlab"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = true
fail_under = 85
exclude_also = ["if __name__ == .__main__.:"]
```
What `strict = true` did in a throwaway folder (`<S>/pt9_strict`) [local]:
```
@pytest.mark.slwo (typo)            -> 'slwo' not found in `markers` configuration option       (collection error)
parametrize("x", [1, 1])            -> IDs: 1, 1 / Duplicates: 1 ... use ids=... or pytest.param(..., id=...)
xfail test that passes              -> FAILED ... [XPASS(strict)] known bug #12
tesptaths = ["tests"] (typo)        -> ERROR: Unknown config option: tesptaths
pytest -m "not slwo"                -> ERROR: Unknown marker(s) in '-m' expression: slwo.
```
Without strict mode the same file gave `3 passed, 1 xpassed, 1 warning`.

---

## 6. Safe refactoring of legacy scripts

### 6.1 Vocabulary
- Refactoring = changing internal structure without changing observable behaviour, as a series of small steps. [source: https://martinfowler.com/bliki/DefinitionOfRefactoring.html] "Two hats" (either restructuring or adding behaviour, never both at once) [memory - Fowler's "Workflows of Refactoring" body was not retrievable]. Beck: structure changes are cheap to reverse, behaviour changes are not, so review them differently. [source: https://newsletter.kentbeck.com/p/structure-and-behavior]
- Characterization test = documents what the code actually does, not what it should do. Recipe: write a test with an expected value you know is wrong, run it, paste the actual value in, rename the test. If it reveals a suspicious behaviour, keep the test until you have confirmed it is a bug. [source: https://michaelfeathers.silvrback.com/characterization-testing]
- Seam = a place where behaviour can be changed without editing at that place (pass a function as a parameter, replace a module attribute). [source: https://martinfowler.com/bliki/LegacySeam.html]
- Code smell = a quickly spotted surface sign that usually (not always) indicates a deeper problem; coined by Kent Beck. [source: https://martinfowler.com/bliki/CodeSmell.html]
- Refactoring names used below are from Fowler's catalog (66 entries): Extract Function, Extract Variable, Rename Variable, Replace Magic Literal, Split Phase, Change Function Declaration, Encapsulate Variable, Replace Nested Conditional with Guard Clauses, Remove Dead Code. [source: https://refactoring.com/catalog/]

### 6.2 Smells in beginner data / backtest scripts (all present in `legacy/ma_backtest_legacy.py` unless noted)

| Smell | Legacy code | Why it hurts | Fix | Who notices |
|---|---|---|---|---|
| Runs at import, no main guard | `df = pd.read_csv("prices.csv")` at top level | importing it for a test raises FileNotFoundError [local] | `main()` + `if __name__ == "__main__":` | nobody automatically |
| Hard-coded relative paths | `"prices.csv"`, `"result.csv"` | depends on current directory | pass `Path` arguments | review |
| Globals as inputs/outputs | `fast = 3`, `global result` | hidden coupling, order dependence | parameters and return values | ruff PLW0603 (off by default) |
| Mutable / early-bound defaults | `def calc(d=df, l=[])` | state shared across calls | no default, or `None` | ruff B006 (default) |
| Mutates its argument | `d["ma1"] = ...` | caller's table changes; copy-on-write does not prevent it [local] | build and return a new frame | test compares input before/after |
| Bare except + print | `except: print("error")` | bad input prints "error", then crashes later with `NameError: name 'result' is not defined` [local] | let it raise; specific exception with a message | ruff E722 (default) |
| Magic numbers | `0.001`, `np.sqrt(252)` | meaning and unit unknown | named constants / frozen config dataclass | PLR2004 only sees comparisons, off by default -> review |
| Cryptic names | `d`, `l`, `ma1`, `sig`, `dd` | reader must decode | Rename Variable | E741 for `l` only (off by default) -> review |
| I/O mixed with maths | read, compute, print, write in one flow | cannot test maths without files | Split Phase: core vs shell | review: "can I call it on an in-memory frame?" |
| Non-deterministic output | `print("run at", datetime.now())` | golden output differs every run | inject the clock; log it | DTZ005 (off by default) |
| Look-ahead | `d["sig"] * d["ret"]` | performance inflated | position = signal shifted one bar | alignment + noise tests (7.5) |
| No input validation | assumes column, order, uniqueness | wrong data gives plausible numbers | validate at the boundary (7.6) | tests |
| Outdated pandas idioms (general) | chained assignment etc. | silently wrong after upgrade [local] | `.loc`, `.ffill()`, `pd.concat` | characterization test run on upgrade |
| Copy-paste blocks (general) | - | fixes applied in one copy only | Extract Function, but only for truly identical logic (Google 2024: do not DRY prematurely) | review |

ruff on the legacy script [local]: default rules -> `I001`, `B006`, `E722` (3 findings); with `--select E,W,F,B,C90,PLR,PLW,T20,N,S,BLE,ERA,PD,NPY,DTZ,I,UP,SIM,ARG,RUF` -> 12 findings (adds E741, ARG001, PLW0603, 5x T201, DTZ005).

### 6.3 Verified step-by-step path
Characterization harness: copy the fixture CSV into `tmp_path`, run the script as a subprocess with that working directory, drop the line starting with `run at` (a "scrubber" for the timestamp), compare stdout with `tests/golden/legacy_stdout.txt` and `result.csv` with a golden CSV. Golden stdout:
```
sharpe 3.3492
max dd -0.0473
final equity 1.0662
```
| Step | Change (structure only) | Check | ruff default / extended findings |
|---|---|---|---|
| 0 | legacy as is | golden created, reviewed, committed | 3 / 12 |
| 1 | body into `main()` + guard; remove bare except, unused default, `global` | PASSED | 1 / 6 |
| 2 | named constants, parameters, honest names, `prices.copy()` | PASSED | 1 / 6 |
| 3 | pure `run_backtest` + `summarize` (core); `load_prices` + `main(prices_path, out_path, now=datetime.now)` (shell) | PASSED | 0 / 3 |
| 4 | package `src/fxlab` with type hints, docstrings, validation, logging, `BacktestConfig` | with `signal_lag=0` the return and equity series are bit-for-bit equal to legacy (`check_exact=True`); Sharpe 3.3492 | 0 default findings |
| 5 | **behaviour change**: default `signal_lag=1`, driven by a failing regression test; new golden reviewed | Sharpe -2.0728, max drawdown -0.0843, final equity 0.9578 | - |

`uv run pytest refactor_steps -v` -> `4 passed in 3.83s`. [local] Steps 1-4 never changed a number; step 5 changed numbers on purpose, in its own commit, with the golden diff as the reviewable artefact.

### 6.4 Golden-master / snapshot files: three verified options
1. Hand-rolled helper (best for teaching; `tests/golden_io.py`, shown slightly condensed) [local]:
```python
def assert_matches_golden(actual: pd.DataFrame, golden_path: Path, *, update: bool, rtol: float = 1e-9) -> None:
    if update:
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        actual.to_csv(golden_path)          # default float format keeps 100.0 a float
        return
    if not golden_path.exists():
        raise AssertionError(f"golden file {golden_path.name} is missing; run pytest --update-golden, then REVIEW it")
    expected = pd.read_csv(golden_path, parse_dates=["date"], index_col="date")
    assert_frame_equal(actual, expected, check_exact=False, rtol=rtol, atol=1e-12, check_freq=False)
```
with a `--update-golden` flag registered through `pytest_addoption` in `conftest.py` and exposed as an `update_golden` fixture. Failure output names the column and position: `DataFrame.iloc[:, 4] (column name="strategy_return") values are different (20.0 %) ... At positional index 5, first diff: -0.0208679... != -0.0198679...`.
2. syrupy 7.0.2: `assert summary == snapshot`; first run fails ("Snapshot ... does not exist!"), `pytest --snapshot-update` writes `tests/__snapshots__/test_golden.ambr`; comparison is exact, so round floats first. Requires Python >= 3.11, pytest >= 8. [local] [source: https://github.com/syrupy-project/syrupy]
3. pytest-regressions 2.11.0: `dataframe_regression.check(df, default_tolerance={"atol": 1e-12, "rtol": 1e-9})`, `num_regression`, `data_regression`; first run fails and creates the file, `--force-regen` updates. Works with pandas 3.1.1. [local] [source: https://pytest-regressions.readthedocs.io/en/latest/overview.html]

Pitfalls found while building these [local]: writing with `float_format="%.12g"` turns `100.0` into `100`, the column reads back as int64 and the comparison fails on dtype; the CSV round trip drops the index `freq` (`check_freq=False`); wall-clock text must be scrubbed or injected; a subprocess per test is slow (share it per module). Discipline: a golden update is a behaviour change - separate commit, explain why, read the diff of the golden file.

### 6.5 Functional core, imperative shell; dependency injection in plain Python
- Keep business logic in pure functions that work only on the data they are given; keep database/network/file/clock work in a thin shell that calls them; the core is then testable in isolation and reusable. [source: Testing Blog feed, "Simplify Your Code: Functional Core, Imperative Shell", 2025-10-20] (Term from Gary Bernhardt's 2012 "Boundaries" talk and screencast. [source: https://www.destroyallsoftware.com/talks/boundaries])
- Verified end state [local]: `run_backtest(prices, config) -> DataFrame` never touches files and never mutates its input (regression test `test_regression_backtest_does_not_mutate_its_input`); `cli.main(argv) -> int` parses arguments, loads, calls the core, saves, logs, returns an exit code (2 for unreadable input).
- Dependency injection without any framework = pass collaborators as arguments [local]:
```python
def daily_report(symbol: str, load_prices: Callable[[str], pd.DataFrame], today: date,
                 config: BacktestConfig | None = None) -> str: ...
def bootstrap_mean_ci(returns: pd.Series, rng: np.random.Generator, n_resamples: int = 1000) -> tuple[float, float]: ...

def test_daily_report_uses_injected_loader_and_date(small_prices):
    requested = []
    def fake_loader(symbol: str) -> pd.DataFrame:      # a fake: tiny working stand-in
        requested.append(symbol)
        return small_prices
    report = daily_report("TEST", load_prices=fake_loader, today=date(2024, 1, 22))
    assert report == "2024-01-22 TEST sharpe=-2.07 mdd=-8.43%"
    assert requested == ["TEST"]
```
Three things to inject in analysis code: the data source, the clock, the random generator.

### 6.6 Seams for code you cannot restructure yet
`monkeypatch` replaces a module attribute, an environment variable or the clock for one test and undoes it afterwards; `capsys` captures prints. Verified on a legacy function that calls a paid API, reads `os.environ` and `datetime.date.today()` [local: `<S>/seam_lab`]:
```python
def test_print_report_formats_one_line(monkeypatch, capsys):
    monkeypatch.setattr(legacy_report, "fetch_last_close", lambda symbol: 108.0)
    monkeypatch.setenv("RISK_LIMIT", "0.05")
    monkeypatch.setattr(legacy_report.datetime, "date", FixedDate)   # subclass overriding today()
    legacy_report.print_report("TEST")
    assert capsys.readouterr().out == "2024-01-22 TEST close=108.00 limit=5.0%\n"
```
Use this to get a first test in place, then refactor towards injected arguments.

---

## 7. Testing numerical and quantitative code

### 7.1 Floating-point tolerance: tools, defaults, traps

| Tool | Rule and defaults | Use for |
|---|---|---|
| `pytest.approx(expected)` | rel=1e-6 **or** abs=1e-12, relative to `expected`; scalars, lists, dicts, NumPy arrays | scalars and small lists [source: https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx] |
| `numpy.testing.assert_allclose(actual, desired)` | `abs(a-d) <= atol + rtol*abs(d)`, rtol=1e-7, **atol=0**, equal_nan=True, `strict=False` | arrays [source: https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_allclose.html] |
| `np.isclose` / `np.allclose` | rtol=1e-5, atol=1e-8 (looser; returns bool, raises nothing) | not for tests [source: pytest docs comparison table] |
| `pandas.testing.assert_series_equal` / `assert_frame_equal` | floats rtol=1e-5, atol=1e-8; ints exact; also dtype, index, names, freq | anything with an index [source: pandas docs] |

Observed with `demos/float_tolerance_demo.py` [local]:
```
0.1 + 0.2 == 0.3                                   -> False
0.1 + 0.2 == pytest.approx(0.3)                    -> True     (repr: 0.3 ± 3.0e-07)
1e-10 == pytest.approx(0.0)                        -> False    (near zero only abs=1e-12 applies)
assert_allclose(1e-10, 0.0)                        -> AssertionError (atol=0); passes with atol=1e-9
100.001 == pytest.approx(100)                      -> False;   rel=1e-4 -> True
nan == pytest.approx(nan)                          -> False;   nan_ok=True -> True; assert_allclose treats NaN==NaN
pd.Series([0.1+0.2]) == pytest.approx(pd.Series([0.3]))  -> a boolean Series containing False
{'a': [0.1+0.2]} == pytest.approx({'a': [0.3]})    -> TypeError (nested);   0.3 < pytest.approx(0.4) -> TypeError
assert_allclose(np.ones(3), 1.0)                   -> passes (broadcast);   strict=True -> AssertionError
assert_frame_equal(int_frame, float_frame)         -> AssertionError (dtype); check_dtype=False passes
assert_frame_equal(reordered_columns, ordered)     -> AssertionError; check_like=True passes
assert_allclose(series, same_values_shifted_one_day) -> passes;  assert_series_equal -> "Series.index are different"
index datetime64[ns] vs datetime64[us]             -> AssertionError (dtype) unless check_index_type=False
```
Rules to teach: (1) never `==` on computed floats; (2) pick the tolerance from the meaning of the number (returns: abs 1e-12 for exact algebra, 1e-9 after long chains); (3) comparing with zero needs an absolute tolerance; (4) anything with dates goes through `pandas.testing`, never `approx` or `assert_allclose`; (5) summation order changes the last digits (`np.sum([1e16, 1, -1e16])` gives 0.0, reordered gives 1.0 [local]).

### 7.2 Tiny hand-computable fixtures
Keep a 10-20 row CSV in the repo (`data/prices_small.csv`, 15 closes) and write expectations a person can check with a calculator: mean 0.01 and sample std 0.01 give a daily Sharpe of 1, so `annualized_sharpe == pytest.approx(np.sqrt(252))`; +10 % twice compounds to 0.21, not 0.20. [local]

### 7.3 Property-based tests (Hypothesis)
- You state a property for a whole class of inputs; Hypothesis generates cases (default 100, deadline 200 ms each), shrinks a failure to a minimal example, and replays it from `.hypothesis/examples` on later runs. [source: https://hypothesis.readthedocs.io/en/latest/reference/api.html]
- Useful invariants (all pass in `tests/test_properties.py`) [local]: max drawdown always in [-1, 0]; returns do not depend on the price unit (scale invariance); prices -> returns -> compounding recovers last/first - 1 (round trip); drawdown is zero exactly for never-falling curves.
- Two plausible beginner bugs that a hand-picked example misses and Hypothesis finds, with shrunk counter-examples [local: `demos/test_hypothesis_finds_bugs.py`]:
```
max_drawdown_naive = (min - max) / max          -> Failing test case: prices=[1.0, 2.0]       (assert -0.5 == 0.0)
cumulative_returns_naive = returns.cumsum()     -> Failing test case: prices=[1.0, 2.0, 1.0]  (ACTUAL 0.5, DESIRED 0.)
```
- A lesson that happened by accident: my first round-trip property drew arbitrary prices between 0.01 and 1e6 and passed twice, then failed on a later run with `prices=[0.015625, 602041.0, 0.01171875]` (relative error 5.7e-9 from cancellation). Not a code bug - the generator described an unrealistic domain. Fix: generate realistic *returns* (-50 % to +100 %) and build prices from them; pin interesting cases with `@example(...)`. So: property tests draw new random cases each local run and can go red later; that is new information, not flakiness. With `CI` set, Hypothesis derandomizes automatically. [local]
- `hypothesis.extra.pandas` and `hypothesis.extra.numpy` work with pandas 3.1.1 / numpy 2.5.5. [local] Failure reports include an "Explanation" block listing library lines - noise for beginners.

### 7.4 Deterministic randomness
Create one `rng = np.random.default_rng(seed)` and pass it down; never rely on `np.random.seed` global state (order-dependent, section 5.6). scikit-learn's docs give the same advice for `random_state`. [source: https://numpy.org/doc/stable/reference/random/index.html] [source: https://scikit-learn.org/stable/common_pitfalls.html] Test both "same seed, same result" and a property of the result (`low < mean < high`), not a hard-coded random number. [local: `tests/test_di.py`]

### 7.5 Detecting look-ahead bias
Definition to borrow: leakage is using information that would not be available at prediction time, which makes results too optimistic; e.g. normalise with statistics of the training part only, never of all the data. [source: https://scikit-learn.org/stable/common_pitfalls.html]
- Detector 1 - truncation invariance (helper in `tests/lookahead.py`) [local]:
```python
def assert_truncation_invariant(transform, data, cutoffs=None) -> None:
    """Outputs for rows < cutoff must be identical whether or not later rows exist."""
    full = transform(data)
    if cutoffs is None:
        cutoffs = list(range(10, len(data), 5))
    for cutoff in cutoffs:
        truncated = transform(data.iloc[:cutoff])
        _assert_equal(full.iloc[:cutoff], truncated)   # pandas.testing with rtol=atol=1e-12, check_freq=False
```
- Detector 2 - future perturbation: multiply every row at or after the cutoff by random noise; outputs before the cutoff must not move.
- Detector 3 - alignment on hand-checkable data: `position == signal.shift(1)`.
- Detector 4 - noise test: on a seeded driftless random walk (2500 days) an honest strategy must have |Sharpe| < 1 (about 3 standard errors).

Results [local: `tests/test_lookahead.py`, 14 tests pass]:

| Case | Truncation test | Noise test |
|---|---|---|
| causal MA crossover, expanding z-score, whole backtest with 1-bar lag | passes | Sharpe +0.04 (fast=1, slow=2, no costs) |
| full-sample z-score, `shift(-1)`, `rolling(center=True)`, `bfill`, divide by global max, full-sample rank | **caught** (5 of 5 + z-score) | - |
| same-bar execution (`signal[t] * return[t]`) | **not caught** - it uses no later rows | **caught**: Sharpe +10.36, equity x12,100 |

Two cautions verified: a leak is visible only at some cutoffs (one `bfill` leak showed at 22 of 240), so check many; and with slow windows (5/20) the same-bar bug inflates the noise Sharpe only from -0.12 to +0.50, so "it does not look too good" proves nothing. Always test the detector itself on a known-bad transform.

### 7.6 Data contracts
Validate where data enters (after `read_csv`), fail loudly with a message that names the problem. Plain-Python version (`src/fxlab/contracts.py`): custom `PriceDataError(ValueError)`, checks for the `close` column, DatetimeIndex, duplicates, ordering, NaN, positivity. The same contract with pandera 0.36.0 [local]:
```python
import pandera.pandas as pa
PRICE_SCHEMA = pa.DataFrameSchema(
    columns={"close": pa.Column(float, checks=pa.Check.gt(0), nullable=False)},
    index=pa.Index("datetime64[ns]", unique=True, name="date"),
    checks=pa.Check(lambda frame: frame.index.is_monotonic_increasing, error="dates not sorted"),
)
PRICE_SCHEMA.validate(frame)             # raises pandera.errors.SchemaError at the first problem
PRICE_SCHEMA.validate(frame, lazy=True)  # raises SchemaErrors; .failure_cases lists every problem:
#   Index   date   field_uniqueness   2024-01-02 ...
#   Column  close  not_nullable       NaN
#   Column  close  greater_than(0)    -5.0
```
Class style also verified: `class Prices(pa.DataFrameModel)` with `pa.Field(gt=0)` and `@pa.check_types` on a function. Note: the index dtype spec accepted `datetime64[us]` data even when written as `[ns]`. Start the course with the plain function (no new dependency, teaches the idea), then show pandera. End-to-end effect on a CSV with a `Close` header [local]: legacy script prints `error` then dies with `NameError: name 'result' is not defined` (exit 1); the refactored CLI logs `PriceDataError: missing 'close' column; got ['Close']` (exit 2).

### 7.7 Golden files for backtest results
One golden per strategy/config on the tiny fixture, compared with tolerance (section 6.4), plus a rounded summary snapshot. It answers "did any number move?" - not "are the numbers right?". Pair it with hand-computed unit tests and the look-ahead detectors.

---

## 8. Readability norms

### 8.1 Naming
PEP 8: modules and packages short lowercase; classes CapWords; functions and variables lower_with_underscores; constants UPPER_WITH_UNDERSCORES; exceptions end in Error; never `l`, `O`, `I` as names; the guiding idea is that code is read far more often than written. [source: https://peps.python.org/pep-0008/] Google: descriptive names, avoid abbreviations; single letters only for counters and similar tiny scopes. [source: https://google.github.io/styleguide/pyguide.html] For data code: say what and in which unit (`daily_returns`, `cost_per_turnover`, `fast_window`), not `df2`, `tmp`, `x1`.

### 8.2 Function size and complexity

| Measure | Threshold | Basis |
|---|---|---|
| Function length | consider splitting beyond about 40 lines (no hard limit) | [source: Google Python Style Guide 3.18] |
| Cyclomatic complexity | 10 (McCabe); up to 15 only for teams with strong process | [source: NIST SP 500-235, 1996, section 2.5 - https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication500-235.pdf] |
| ruff C901 `max-complexity` | 10 (rule off by default) | [local: `ruff config lint.mccabe.max-complexity`] |
| ruff PLR0912 branches / PLR0915 statements / PLR0913 arguments / PLR0911 returns | 12 / 50 / 5 / 6 (all off by default) | [local: `ruff rule ...`] |
| Arguments | reviewer question: more than three? | [source: Microsoft reviewer guidance] |
| Line length | ruff 88; PEP 8 79 (99 by team agreement); Google 80 | [local] [source] |

Verified example: a 5-level nested classifier -> `C901 'classify' is too complex (11 > 10)`, `PLR0912 Too many branches (15 > 12)`; after extracting `is_tradable`, `momentum_action`, `classify_row` with guard clauses the largest function scores 4 and outputs are identical on all 15 input combinations. [local: `demos/complexity_*.py`]

### 8.3 Comments vs docstrings
- Comments explain why; a comment that contradicts the code is worse than none. [source: PEP 8] Do not describe what the code does. [source: Google style guide 3.8] Keep comments short and self-contained; describe the contract rather than the implementation. [source: Testing Blog feed, 2024-08-21]
- Docstrings: triple double quotes; all public modules, functions, classes, methods; one-line form is an imperative phrase ending in a period ("Return ..."), not a restated signature; multi-line = summary line, blank line, details; document arguments, return value, side effects, exceptions. [source: https://peps.python.org/pep-0257/] Google layout adds `Args:`, `Returns:`, `Raises:` sections and requires a docstring for functions that are public, non-trivial or non-obvious. [source: Google style guide]
- ruff: select `D` and set `lint.pydocstyle.convention = "google"`; the lab's `src/` passes that selection. [local]

### 8.4 Type hints as documentation
The runtime does not enforce annotations; type checkers, IDEs and linters use them. [source: https://docs.python.org/3/library/typing.html] Verified with mypy 2.4.1 [local]:
```
error: Argument "fast" to "BacktestConfig" has incompatible type "str"; expected "int"  [arg-type]
error: Argument 1 to "max_drawdown" has incompatible type "list[float]"; expected "Series[Any]"  [arg-type]
error: Argument 1 to "run_backtest" has incompatible type "str"; expected "DataFrame"  [arg-type]
```
(running the same file instead fails late with `AttributeError: 'list' object has no attribute 'empty'`). Two setup traps: without `pandas-stubs` mypy reports `Library stubs not installed for "pandas"`; without the `py.typed` marker that `uv init --lib` creates, mypy skips your own package ("missing library stubs or py.typed marker"). [local]

### 8.5 Error handling: fail loudly
- A bare `except:` also catches SystemExit and KeyboardInterrupt; acceptable only when the handler logs the traceback or re-raises; derive custom exceptions from Exception; use `raise X from Y`. [source: PEP 8] Use built-in classes such as ValueError for violated preconditions; never use `assert` for validation; keep `try` blocks small. [source: Google style guide 2.4] `python -O` really removes asserts (`ran past the assert under -O`). [local]
- Verified consequence [local: `demos/bare_except_demo.py`]: a typo inside `try` with `except: return 0.0` yields `bad : 0.0` instead of an error - a silent wrong number, the worst outcome in research code.
- ruff default rules now cover the basics: E722, BLE001, S110/S112, TRY002. [local]
- Test errors with `pytest.raises(ValueError, match="strictly positive")`; ruff PT011 flags `raises` without `match` (off by default). [local]

### 8.6 Logging vs print
Python's HOWTO: `print()` for a command-line program's normal output; a logger's `info`/`debug` for events during operation; `warnings.warn` when the caller should change their code; raise an exception to report an error; `logger.error`/`exception` when an error is handled without raising. Default level is WARNING; use `logger = logging.getLogger(__name__)` per module; libraries must not configure handlers. [source: https://docs.python.org/3/howto/logging.html] In the lab the shell calls `logging.basicConfig` once, the core does not log at all, and tests read logs through `caplog` (`caplog.records[-1].exc_info is not None` proves the traceback was kept). ruff T201 flags `print` but is off by default. [local]

---

## 9. Pitfalls a beginner will hit (all observed today unless tagged)
1. `pytest: command not found` - it is a project dev dependency; run `uv run pytest`. [memory for the message; pytest is not installed globally on this machine]
2. Forgetting `assert` (bare comparison, or `return`): the test passes. B015 and `filterwarnings = ["error"]` help.
3. `assert series == pytest.approx(other_series)` - not supported; use `pandas.testing`.
4. Comparing with 0.0 using only a relative tolerance fails forever; give `abs=` / `atol=`.
5. `assert_frame_equal` failing on `freq`, dtype (int vs float, `ns` vs `us`) or column order rather than on values - read the first line of the message.
6. Golden CSV written with a short float format changes dtypes; regenerate-until-green hides real changes.
7. `from tests.helper import ...` -> ModuleNotFoundError in default import mode without `tests/__init__.py`; fixtures in `tests/conftest.py` are not visible outside `tests/`.
8. Unregistered marker typos are only warnings unless `strict = true`.
9. Selecting ruff's `S` group flags every `assert` in tests (S101) and `PLR2004` flags literals in assertions: add per-file ignores for `tests/**`. Lab run: 62 findings in tests with an extended selection, almost all S101 and E501.
10. mypy on pandas code needs `pandas-stubs`; deleting `py.typed` silently disables checking of your own package for other code.
11. Chained assignment copied from old tutorials no longer changes the DataFrame in pandas 3 - only a warning.
12. A function that adds columns to its argument still changes the caller's DataFrame.
13. Hypothesis: first failure output is long; `.hypothesis/` appears in the project (self-ignoring); tests can newly fail on a later run.
14. Subprocess-based characterization tests cost about 0.7 s each; share the run with a module-scoped fixture.
15. Treating a green golden test as proof of correctness - it pinned the look-ahead bug faithfully until a human questioned it.
16. Mixing refactoring and bug fixes in one commit - the golden diff then cannot tell you which one moved the numbers.
17. Believing an assistant's "all tests pass" without seeing the command and output.
18. A coverage floor set right at the current value: the report can print FAIL while the exit code stays 0 (integer rounding), or flip on a one-line change.
19. `Series == pytest.approx(...)` and `assert_allclose` on date-indexed data both ignore or mishandle the index - misaligned dates are themselves a look-ahead bug.

---

## 10. Recommendations for the course

**Order (each step ends with something runnable):**
1. Reading a diff and the author checklist (`git status`, `git diff --stat`, `git diff`, `git diff --check`) - the habit everything else hangs on.
2. First test = characterization test of the learner's own script (subprocess + golden text). Teaches pytest, fixtures, `tmp_path`, and gives a safety net immediately.
3. Refactor in three structure-only steps (main guard -> named constants and parameters -> core/shell), rerunning the same test after each.
4. Unit tests for the extracted pure functions: AAA, hand-computed fixtures, `pytest.approx`, `parametrize`, `pytest.raises(match=...)`.
5. Readability pass: names, docstrings (Google layout), type hints + mypy, exceptions instead of silent defaults, logging in the shell.
6. First bug fix test-first: the look-ahead regression test (red), the fix (green), the reviewed golden update.
7. Backtest-specific safety: `pandas.testing`, look-ahead detectors, data contract (plain function, then pandera).
8. Coverage as a map (run it, read "Missing", demonstrate the 100 %-without-assertions trap).
9. Review module: Conventional Comments, reviewer checklist, reviewing AI output (evidence, fresh reviewer, red-flag table). Practise by reviewing the legacy script and one AI-written test file.
10. Optional/advanced: Hypothesis; syrupy or pytest-regressions; flaky-test clinic.

**Sensible defaults:** the config in 5.11; tests in `tests/` mirroring `src/` file names; test names `test_<function>_<scenario>_<expectation>`; tolerance `pytest.approx` default for scalars, `rtol=1e-9, atol=1e-12` for tables; one 15-row CSV fixture plus a seeded generator; `fail_under` a few points below current coverage; change size <= 200 lines; refactor commits separate from behaviour commits; every bug fix carries a `test_regression_*`.

**Skip or postpone:** `unittest.TestCase` classes, mocking frameworks, strict TDD as a rule, 100 % coverage goals, mutation testing, tox/nox matrices, BDD tools, end-to-end test infrastructure, pytest plugin zoo (xdist, randomly) - mention, do not teach.

**Plain-Chinese analogies (mine):**
- characterization test = 装修前先给房子拍照存档；golden file = 对账用的"标准答案"，改答案必须说明理由。
- refactoring vs behaviour change ("two hats") = 整理房间和添置家具不要同时做。
- functional core / imperative shell = 厨房只管做菜（纯计算），前厅负责进货和上菜（读写文件、联网、看时间）。
- dependency injection = 食材由别人递进来，函数自己不出门买菜。
- unit test = 体检的单项指标；regression test = 出过事的路口装上摄像头。
- coverage = 巡逻路线图：走到过不等于检查过。
- flaky test = 时灵时不灵的烟雾报警器，最后没人再信它。
- bare except = 把报警器的电池拔掉；magic number = 没贴标签的药瓶。
- look-ahead bias = 用明天的报纸做今天的交易；truncation test = 把未来的数据遮住，过去的结果不应该变。
- tolerance = 游标卡尺的公差；property-based test = 不出例题，只规定"定律"，让机器出一百道题找反例。
- mock = 替身演员，用多了测的是替身不是本人。
- code review = 交稿前的校对；self-review = 发邮件前自己再读一遍；Nit = "小毛病，可改可不改"。
- data contract = 进货验收单；type hint = 插头的形状；docstring = 说明书，comment = 只写"为什么"的便利贴。

---

## 11. Not verified today
- Google Testing Blog "Code Coverage Best Practices" (60/75/90 %) and "Just Say No to More End-to-End Tests" (70/20/10): page bodies were not served to the fetch tool; numbers come from memory and secondary snippets.
- Fowler "Workflows of Refactoring" (two hats) and Bernhardt's screencast description: bodies not retrievable; Feathers' definition of legacy code as code lacking tests, and Bill Wake as the origin of AAA: [memory].
- SmartBear article is the vendor's summary of its Cisco study; the study's size was not on the page.
- pytest.approx support for datetime/timedelta: the reference page and the changelog summary disagreed on the version (8.4 vs 9.1); not tested.
- Which ruff release changed the default count from 413 (0.16.0 notes) to 407 (0.17.2 locally).
- Hypothesis storage relocation via environment variable; behaviour of `.pytest_cache` / `.hypothesis` / `.coverage` inside an iCloud-synced folder.
- `git add -p` and anything interactive; GitHub pull-request UI; the Claude Code desktop app's review UI (`/code-review` behaviour is from the docs, not exercised).
- Mutation-testing tools (mutmut, cosmic-ray) were not run; the "break it by hand and watch a test fail" exercise was.
- No real learner project was opened; the legacy script here is a stand-in with typical smells.
- pandas `check_freq` is documented as changing behaviour in future versions; only 3.1.1 behaviour was observed.

## 12. Primary sources read today
Google eng-practices: /review/reviewer/{standard,looking-for,navigate,comments,speed}.html, /review/developer/{small-cls,cl-descriptions,handling-comments}.html (https://google.github.io/eng-practices/) · https://conventionalcomments.org/ · https://docs.gitlab.com/development/code_review/ · https://microsoft.github.io/code-with-engineering-playbook/code-reviews/ (+ process-guidance/author-guidance, reviewer-guidance, recipes/python) · https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/ · https://docs.github.com/en/copilot/tutorials/review-ai-generated-code · https://code.claude.com/docs/en/best-practices.md · https://code.claude.com/docs/en/code-review-local · https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions · https://simonwillison.net/2025/Dec/18/code-proven-to-work/ · Fowler: bliki TestPyramid, TestCoverage, TestDrivenDevelopment, SelfTestingCode, DefinitionOfRefactoring, CodeSmell, LegacySeam; articles practical-test-pyramid, 2021-test-shapes, nonDeterminism, mocksArentStubs (https://martinfowler.com/) · https://refactoring.com/catalog/ · https://michaelfeathers.silvrback.com/characterization-testing · https://newsletter.kentbeck.com/p/canon-tdd · https://newsletter.kentbeck.com/p/structure-and-behavior · https://testdesiderata.com/ · https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications · Software Engineering at Google ch. 11-13 (https://abseil.io/resources/swe-book/html/ch11.html) · Google Testing Blog feed (https://feeds.feedburner.com/blogspot/RLXA; posts 2024-05 to 2026-10) · pytest docs: changelog, reference/customize, explanation/{anatomy,goodpractices,flaky}, how-to/fixtures, reference (approx) (https://docs.pytest.org/en/stable/) · https://hypothesis.readthedocs.io/en/latest/reference/api.html · numpy assert_allclose and random docs · pandas assert_frame_equal docs · https://pandera.readthedocs.io/en/stable/ · https://coverage.readthedocs.io/en/latest/config.html · https://github.com/syrupy-project/syrupy · https://pytest-regressions.readthedocs.io/en/latest/overview.html · https://github.com/astral-sh/ruff/releases/tag/0.16.0 · https://docs.astral.sh/ruff/default-rules/ · PEP 8, PEP 257 · https://google.github.io/styleguide/pyguide.html · Python docs: howto/logging, library/typing · https://scikit-learn.org/stable/common_pitfalls.html · NIST SP 500-235.
