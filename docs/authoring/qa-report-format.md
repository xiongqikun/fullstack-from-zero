# QA report format

What a builder and an independent tester must report, so that the next person can act on the report without asking. The authoritative versions are the JSON schemas inside the workflow scripts of [`build-kit/`](build-kit/); this page explains them field by field. When a script changes, change this page in the same edit.

| Report | Who writes it | Schema |
|---|---|---|
| Build report | the builder of one lesson | `BUILD_REPORT` in `build-kit/build-lessons.js` |
| Fix report | a fixer of one lesson (repair round) | `FIX_REPORT` in `build-kit/fix-lessons-round.js` |
| Test report | the independent blind tester of one lesson | `TEST_REPORT` in `build-kit/build-lessons.js`; extended in `build-kit/fix-lessons-round.js` |
| Play-through report | a tester who plays several lessons in order | `PLAY` in `build-kit/acceptance.js` |
| Writer / fixer report | the writer or fixer of a shared file; a fixer after a play-through | `REPORT` in `build-kit/build-shared-docs.js` and in `build-kit/acceptance.js` |
| Review verdict | a reviewer of the shared files (mechanical, consistency, newcomer, tutor judge) | `VERDICT` in `build-kit/build-shared-docs.js` |
| Tutor simulation | a fresh agent that answers scripted learner messages with only `CLAUDE.md` | `SIM` in `build-kit/build-shared-docs.js` |
| Acceptance record | the final acceptance agent | `ACCEPT` in `build-kit/acceptance.js` |

## 1. Rules for every report

- **Facts, not impressions.** Each claim says what was run or opened and what came back. "Works" is not evidence; the command and its exit code are.
- **Nothing private.** No real name, user name, e-mail address or computer name, no simulation path under `/private/tmp`, no fake identity of the simulation (plan G10). Paths are written with `~`.
- **Workarounds are reported, never hidden.** Every environment variable, flag or substitute path the agent needed and the learner would not have (for example `COURSE_NONINTERACTIVE=1`, `git -c commit.gpgsign=false`, `unset GIT_EDITOR`; [`tool-api.md`](tool-api.md) section 17.1.1) is named, and none of them may appear in lesson text.
- **Open issues are addressed.** Each entry of `open_issues` begins with one of: `tutor contract needs:`, `shared file needs:`, `tool needs:`, `lesson <id> needs:` and says what the addressee must do.
- **Rejected findings carry a reason** that cites the plan, the design or a decision of the orchestrator (for example "superseded by the entrance decision").

## 2. Build report and fix report (one lesson)

| Field | Required | What goes in it |
|---|---|---|
| `lesson_id` | yes | `1.6` |
| `summary` | yes | What the lesson now teaches and the main choices, in a few sentences |
| `files` | yes | Every file written, absolute paths |
| `findings_handled` | fix report | One entry per finding: `finding` (a few words plus its source: tester, seam auditor, tool round, orchestrator), `action` (`fixed`, `rejected`, `not-mine`), `note` (what changed, or the reason and evidence for rejecting) |
| `minutes_calculation` | fix report; recommended in a build report | Per station: the count of each component of the plan G5a calculation, the resulting minutes, and what was moved into 「想多了解（可跳过）」 or cut |
| `commands_executed` | yes | How many lesson commands were executed verbatim in the simulation home; the result of `validate` and `validate --build` on Python 3.14 and 3.9; the check tests (correct work and each wrong attempt, with the outcome) |
| `unverifiable_steps` | yes | Steps that could not be executed (GUI, online, needs an account) and how each is marked (plan G6) |
| `sources_checked` | yes | For every rule card source: URL and the version or edition confirmed today |
| `station_minutes` | build report | The minutes per station |
| `end_state` | yes | Exactly what exists on the learner's machine after the lesson: files and folders, repository state and commit subjects, global settings changed, learner state (stations passed, review items enrolled, decisions recorded). Later lessons depend on it |
| `deviations_from_plan` | yes | Each departure from the plan and why (an honest label that triggers a `[§4]` warning goes here) |
| `open_issues` | yes | See section 1 |

## 3. Test report (one lesson, blind)

The tester did not write the lesson and reads only the lesson folder, the plan sections named in the brief, [`tool-api.md`](tool-api.md) and the tool. Needing anything else is a finding.

| Field | Required | What goes in it |
|---|---|---|
| `lesson_id` | yes | |
| `verdict` | yes | `fail`: a beginner following the text would be stopped or misled, or a check gives a wrong verdict. `pass-with-issues`: anything else worth fixing. `pass`: nothing a careful editor would change |
| `issues` | yes | One object per issue: `where` (station and step, or file and line), `severity`, `what_happened`, `expected`, `suggestion` |
| `novice_errors` | yes | For each injected mistake: what the learner would see, and whether the text or the checker rescues them |
| `used_before_defined` | yes | Every term, command, option, symbol or key used before it is explained in this lesson or taught in an earlier lesson |
| `budget` | yes | Per station: new concepts and new commands against plan G5, and the tester's own G5a calculation (with its components) next to the minutes the lesson states |
| `sources` | yes | For each rule card: did the source load today, does it say what the card claims, is the version current; is each 旧教程提醒 true |
| `tool_results` | yes | `validate`, each check (correct work and at least four wrong attempts), hints, review items, scenarios and exam tasks: what was run and what happened |

**Severity.** `blocker`: the learner is stopped, misled into damage, or a check gives a wrong verdict. `major`: the learner can go on but loses time or trust, or a binding form (plan section 1, [`lesson-template.md`](lesson-template.md)) is broken. `minor`: wording, polish, a missing nicety. A lesson is done only when the last test has no blocker and no major ([`definition-of-done.md`](definition-of-done.md)).

## 4. Play-through report (several lessons in order)

| Field | Required | What goes in it |
|---|---|---|
| `segment` | yes | Which lessons, for example `1.5-1.8` |
| `verdict` | yes | as in section 3 |
| `lessons` | yes | Per lesson: `id`, `completed` (true or false), `start_state_met` (did the previous lesson really leave what this one assumes), `minutes_estimate`, `notes` |
| `issues` | yes | As in section 3, plus `file` (the file to change); `expected` is optional |

A play-through never rebuilds a `start` scenario between lessons of its segment: the end of one lesson must be the beginning of the next.

## 5. Writer report and acceptance record

**Writer / fixer report** (`REPORT`): `summary`, `files`, `verified` (what was executed or checked, with the real results), `rejected_findings` (fixers: each finding not applied, with its reason), `open_issues`. In `build-shared-docs.js` it also requires `problems_found_in_lessons`: inconsistencies between lessons, or between a lesson and the plan, that the writer noticed and did not fix.

**Review verdict** (`VERDICT`): `verdict` (as in section 3), `checked` (what was read or run), `issues` (each with `file`, `where`, `severity`, `problem`, `suggestion`).

**Tutor simulation** (`SIM`): `replies`, one per scripted situation, each with `scenario`, `files_read_first`, `reply` (exactly what the tutor would say to the learner, in Chinese) and `actions` (tools or commands it would use, and anything it would write to a file). A judge scores the replies against `CLAUDE.md` and writes a review verdict.

**Acceptance record** (`ACCEPT`): `verdict` (`accepted`, `accepted-with-known-issues`, `not-accepted`); `checklist` (each `item` with `result` `pass`, `fail` or `not-verifiable` and its `evidence`); `known_issues` (what the learner or the next builder must be told, in plain words); `unverifiable` (every learner-facing step nobody could execute, by lesson); `files`.
