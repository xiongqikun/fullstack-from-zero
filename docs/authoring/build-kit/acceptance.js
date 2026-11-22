export const meta = {
  name: 'acceptance',
  description: 'End-to-end acceptance of batch 1: five play-throughs with novice-error injection, fixes, then a mechanical acceptance checklist and the QA record',
  phases: [
    { title: 'Play through', detail: 'five segments, each followed literally in one simulation home' },
    { title: 'Fix', detail: 'apply the play-through findings' },
    { title: 'Confirm', detail: 'an independent agent re-plays what was changed; a second fix where something serious is left' },
    { title: 'Accept', detail: 'mechanical checklist over the whole workspace and the QA record' },
  ],
}

const WS = args.ws
const SCRATCH = args.scratch
const PLAN = WS + '/docs/plans/2026-11-19-batch-1-plan.md'
const DESIGN = WS + '/docs/design/2026-11-19-fullstack-learning-workspace-design.md'
const OPTS = { model: args.model || 'opus', effort: args.effort || 'high' }
const NOTES = args.notes || ''
const TODAY = args.today || '2026-11-20'

const COMMON = `You are an agent working on a local learning workspace for a Chinese-speaking adult who is learning software engineering from zero. Today is ${TODAY}. You were dispatched for an explicit build or test task: the tutoring rules in WS/CLAUDE.md do not bind you.

WORKSPACE ROOT (WS): ${WS}
BINDING DOCUMENTS: the plan ${PLAN} (sections 1, 2, 3, 4, 5a, task T4 and section 6) and the design ${DESIGN}. Tool API: WS/docs/authoring/tool-api.md.
YOUR SCRATCH AREA: ${SCRATCH}/<your label>/.

HARD RULES:
- Never touch the real ~/.gitconfig, ~/.zshrc, ~/Developer, the learner's other projects or any global configuration. No installs, no accounts, no pushes, no git commits inside WS. Simulation homes are made with "python3 tools/dev/make_sim_home.py" (plan G8); work in zsh. The reference environment is plan G7.
- Before executing anything read tool-api.md section 17.1.1: your shell differs from the learner's (GIT_EDITOR=true is exported, TERM is empty, Apple's git shim prints cache noise on standard error). Handle each difference as that section says and never report it as a fault of a lesson.
- Testers modify nothing under WS. Fixers keep every change minimal and re-verify it.
- Privacy per plan G10. Leave no __pycache__ or debris in WS.
- Your final structured output is a factual report for the orchestrator.
${NOTES}`

const PLAY = {
  type: 'object',
  properties: {
    segment: { type: 'string' },
    verdict: { type: 'string', enum: ['pass', 'pass-with-issues', 'fail'] },
    lessons: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          completed: { type: 'boolean' },
          minutes_estimate: { type: 'string' },
          start_state_met: { type: 'string', description: 'did the previous lesson really leave what this one assumes' },
          notes: { type: 'string' },
        },
        required: ['id', 'completed', 'start_state_met', 'notes'],
      },
    },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          where: { type: 'string' },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          what_happened: { type: 'string' },
          expected: { type: 'string' },
          suggestion: { type: 'string' },
        },
        required: ['file', 'where', 'severity', 'what_happened', 'suggestion'],
      },
    },
  },
  required: ['segment', 'verdict', 'lessons', 'issues'],
}

const REPORT = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    files: { type: 'array', items: { type: 'string' } },
    verified: { type: 'string' },
    rejected_findings: { type: 'array', items: { type: 'string' } },
    open_issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'files', 'verified', 'rejected_findings', 'open_issues'],
}

const ACCEPT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['accepted', 'accepted-with-known-issues', 'not-accepted'] },
    checklist: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          item: { type: 'string' },
          result: { type: 'string', enum: ['pass', 'fail', 'not-verifiable'] },
          evidence: { type: 'string' },
        },
        required: ['item', 'result', 'evidence'],
      },
    },
    known_issues: { type: 'array', items: { type: 'string' }, description: 'what a learner or the next builder must be told, in plain words' },
    unverifiable: { type: 'array', items: { type: 'string' }, description: 'every learner-facing step nobody could execute (GUI, online, needs an account), by lesson' },
    files: { type: 'array', items: { type: 'string' } },
  },
  required: ['verdict', 'checklist', 'known_issues', 'unverifiable', 'files'],
}

const AFTER_STAGE_0 = 'in the fresh simulation home first create what lessons 0.1-0.4 leave behind (read their lesson.py checks and stated end states: ~/Developer exists, learner/profile.md filled in from templates/profile-template.md with plausible answers, PROGRESS.md, a journal entry)'
const SIM_GIT = 'apply the outcome of lesson 1.6 to the SIMULATION\'s global Git configuration only, as that lesson recommends (HOME must point at the simulation: check with "echo $HOME" before any "git config --global")'
const BY_HAND = 'Say in your report exactly what you had to create by hand.'

const SEGMENTS = [
  { key: 'stage-0', lessons: '0.1, 0.2, 0.3, 0.4', start: 'a fresh copy of the workspace with no learner/ state at all: begin exactly where a new learner begins, by reading README.md and following it into lesson 0.1', extra: 'Include the first ten minutes: everything README.md asks before lesson 0.1. Take gate-0 at the end.' },
  { key: 'stage-1-part-1', lessons: '1.1, 1.2, 1.3, 1.4', start: 'what a learner has after stage 0: ' + AFTER_STAGE_0 + '. ' + BY_HAND, extra: 'Lesson 1.4 is mostly GUI: check that every step you cannot execute is marked per plan G6 and judge whether a learner could follow it from the text alone; do the file edits it asks for with a plain-text edit so that later lessons find the state they expect.' },
  { key: 'stage-1-part-2', lessons: '1.5, 1.6, 1.7, 1.8', start: 'what a learner has after lesson 1.4: ' + AFTER_STAGE_0 + '; then build the start scenario of lesson 1.5 (python3 tools/course.py scenario 1.5: the state the ladder of the tool gives a learner at that point, tool-api.md section 15.3) and copy its my-site to ~/Developer/my-site in the simulation. ' + BY_HAND, extra: 'Take gate-a after 1.5. Lesson 1.6 must be met with the signing problem of plan G7 present (the simulation home has it): follow the lesson through it exactly as written.' },
  { key: 'stage-1-part-3', lessons: '1.9, 1.10, 1.11, 1.12', start: 'what a learner has after lesson 1.8: ' + AFTER_STAGE_0 + '; build the start scenario of lesson 1.9 and copy its my-site to ~/Developer/my-site in the simulation (a learner who followed lesson 1.7 exactly has one commit more, 「改了标题的颜色」: make it by hand as lesson 1.7b says, so that the history matches the one a learner has); ' + SIM_GIT + '. ' + BY_HAND, extra: 'Take gate-b after 1.10. For 1.11 and 1.12 no account and no gh exist here: use a local bare repository as the stand-in remote for the Git mechanics, check that every step you cannot execute is marked per plan G6, and judge whether a learner could follow those steps from the text alone.' },
  { key: 'stage-1-part-4', lessons: '1.13, 1.14, 1.15, 1.16', start: 'what a learner has after lesson 1.12: ' + AFTER_STAGE_0 + '; build the start scenario of lesson 1.13 and copy its my-site to ~/Developer/my-site in the simulation; ' + SIM_GIT + '; make the simulation\'s workspace copy a repository with one commit, a local bare repository as its remote origin, and main pushed with an upstream, as lesson 1.12 leaves it. ' + BY_HAND, extra: 'Take gate-1 inside 1.16. For 1.13 use a local bare repository as the stand-in for GitHub and check the marking of every step you cannot execute (plan G6). In 1.16 fill notes/my-rules.md as a learner would, so that its check can pass.' },
]

phase('Play through')
const plays = await parallel(SEGMENTS.map(s => () => agent(`${COMMON}

YOUR LABEL: play-${s.key}
YOUR TASK: play through lessons ${s.lessons} in order, in ONE simulation home, as a careful beginner would. Start from ${s.start}.

RULES OF THE PLAY-THROUGH
- Follow each lesson.md literally, typing what it says. Do each exercise using only what the lessons so far have taught; use the hint command level by level only when a real beginner would be stuck, and record the level. Run every check. Write the journal line. Run "python3 tools/course.py status" after each lesson and confirm what it says is true.
- Between lessons inside your segment do NOT rebuild with a "start" scenario: the end of one lesson must really be the beginning of the next. If a lesson assumes something the previous one did not leave behind, that is a finding.
- In every lesson make two beginner mistakes from this list, rotating through it: full-width punctuation or a full-width space in a command; the wrong directory; an unsaved edit; a pasted prompt or leading $; an unclosed quote; stuck in vi or less; an empty Enter; a name with a space; (Git) committing with nothing staged. Report whether the text or the tool rescued you.
- At each gate run the exam and grade it once with a deliberate mistake in one task and then take the retest correctly; read every line the tool prints (the number of tasks, the minutes, what comes next) and compare with what the lesson and gates/<gate>/rubric.md say. Then record the explain-back part as the lesson says, first with --explain again and then with --explain pass, and run check, status and exam after each to see that what they print is true. Once per segment move COURSE_NOW forward (three days, then three weeks) and run a review session: are the items that come back the right ones, and are they answerable?
- Read as one continuous course: report anything explained twice in different words, two names for one thing, an analogy that contradicts an earlier one (plan section 5a), a forward promise no later lesson keeps, a sudden change of tone or difficulty, a station with more than one new concept, a rule card whose label or source looks wrong, and any sentence a beginner could not follow.
- Time: for two stations of your segment calculate the minutes with the calculation of plan G5a (count the components) and compare with the minutes the lesson states; report a difference of more than 5 minutes. For every lesson also note the minutes your own run suggests for a slow-typing beginner.
${s.extra}`, { label: 'play:' + s.key, phase: 'Play through', schema: PLAY, ...OPTS })))

phase('Fix')
const fixes = await parallel(SEGMENTS.map((s, i) => () => {
  const p = plays[i]
  if (!p || !p.issues || p.issues.length === 0) return Promise.resolve(null)
  return agent(`${COMMON}

YOUR LABEL: fix-${s.key}
YOUR TASK: fix what the play-through of lessons ${s.lessons} found. Edit only files the findings name plus what must change with them (a lesson's lesson.md, lesson.py and rules.md; a cheat sheet or template entry; a tool message). Four other fixers are working on the other lessons at the same time: do not touch lesson folders outside your segment, and if a finding needs a change in a shared file (tools/, README.md, CLAUDE.md, cheatsheets/, templates/, the hand-written part of a handbook chapter above its marker line), make the smallest possible edit in one step and list it in your report. Never edit the generated parts of handbook/ and GLOSSARY.md (below the marker line): they are rebuilt from the lessons by "python3 tools/dev/build_reference.py" after you finish, so a changed rule card or TERMS entry needs no further edit from you. Fix every blocker and major; fix minors unless you can cite the plan against them. Re-execute every changed command in a fresh simulation home, re-test every changed check on right and wrong work, and finish with "python3 tools/course.py validate <lesson id>" and "validate --build <lesson id>" for every lesson you changed, on both Python versions. Do NOT run the tool's whole test suite (several runs at the same time have overloaded this machine; the acceptance step runs it once): if a finding made you change a file under tools/, run only the test files of that module and name the change in your report.

PLAY-THROUGH REPORT:
${JSON.stringify(p).slice(0, 110000)}`, { label: 'fix:' + s.key, phase: 'Fix', schema: REPORT, ...OPTS })
}))

phase('Confirm')
const serious = p => !!p && (p.verdict === 'fail' || (p.issues || []).some(i => i.severity !== 'minor'))
const confirms = await parallel(SEGMENTS.map((s, i) => async () => {
  const p = plays[i]
  const f = fixes[i]
  if (!f || !serious(p)) return null
  const c = await agent(`${COMMON}

YOUR LABEL: confirm-${s.key}
YOUR TASK: an independent check of the fixes made to lessons ${s.lessons} after their play-through. You are a tester: modify nothing under WS. Start from ${s.start}.
For every blocker and major of the play-through report below: bring a fresh simulation home to the situation in which the problem showed, follow the lesson text as it is NOW, and say whether the problem is gone. Then play every station that the fix report says was changed once more from its beginning to its check, with one beginner mistake from the usual list in each, and look at what the change may have broken next to it (the next station, the lesson's check, hints, review items, exam tasks, the pasted outputs). Report with the play-through schema: issues = what is still wrong or newly wrong (file, place, severity, what happened, suggestion); lessons = the lessons you touched.

PLAY-THROUGH REPORT:
${JSON.stringify(p).slice(0, 60000)}

FIX REPORT:
${JSON.stringify(f).slice(0, 30000)}`, { label: 'confirm:' + s.key, phase: 'Confirm', schema: PLAY, ...OPTS })
  if (!serious(c)) return { confirm: c, fix2: null }
  const fix2 = await agent(`${COMMON}

YOUR LABEL: fix2-${s.key}
YOUR TASK: a second, narrow fix for lessons ${s.lessons}. An independent agent re-played the lessons after the first fix and still found what is listed below. Same ownership rules as the first fixer: edit only the lesson folders of your segment plus the smallest possible edit in a shared file that a finding needs (list each such edit); never edit the generated parts of handbook/ and GLOSSARY.md. Fix every blocker and major; re-execute every changed command in a fresh simulation home, re-test every changed check on right and wrong work, run "python3 tools/course.py validate <lesson id>" and "validate --build <lesson id>" for every lesson you changed on both Python versions; do NOT run the tool's whole test suite (the acceptance step runs it once), only the test files of a tool module you had to change.

CONFIRM REPORT:
${JSON.stringify(c).slice(0, 80000)}`, { label: 'fix2:' + s.key, phase: 'Confirm', schema: REPORT, ...OPTS })
  log('acceptance: ' + s.key + ' needed a second fix; it is verified only by the mechanical checklist that follows')
  return { confirm: c, fix2 }
}))

phase('Accept')
const accept = await agent(`${COMMON}

YOUR LABEL: accept
YOUR TASK: the mechanical acceptance of batch 1, and its QA record. You may write only: WS/docs/authoring/qa/batch-1-acceptance.md (the record), the header line of WS/ROADMAP.md that states the present status, one entry in WS/CHANGELOG.md, the stage 0-1 checklist boxes in WS/docs/curriculum-spine.md, through the generator only the generated parts (WS/handbook/, WS/GLOSSARY.md, WS/STANDARDS.md, the stage pages, the headings of WS/notes/my-rules.md), and, only where checklist item 11 finds a difference, the hours of stages 0 and 1 and the sums and calendar figures that depend on them in WS/README.md, WS/ROADMAP.md, WS/docs/roadmap/sources.md and the hand-written lines of the two stage pages (every number from the generator; show the arithmetic in the record).

FIRST: the fixers above may have changed rule cards or TERMS. Run "python3 tools/dev/build_reference.py" once so that the handbook and the glossary are rebuilt from the lessons, then "python3 tools/dev/build_reference.py --check" (it must exit 0).

CHECKLIST (verify each item yourself; give the evidence):
1. The workspace tree matches plan section 2; nothing unexpected at the top level; no __pycache__, no temporary files.
2. "python3 tools/course.py validate" and "validate --complete" pass in a fresh simulation home (paste the output). The tool's test suite passes on Python 3.14 and on Python 3.9 (run one after the other, never both at once; paste the counts).
3. All 20 lesson folders of plan section 4 exist with lesson.md, lesson.py and rules.md; every station has a check and exactly four hints; every lesson has a "start" scenario that builds; every lesson module imports on Python 3.9.
4. All 30 rule ids of plan section 4 have exactly one card with all thirteen fields (plan I2); the handbook copies are identical to the lessons' cards; every card's 规则类型 is one of the seven labels; STANDARDS.md section 3 agrees with the cards (id, title, label family, 约束力).
5. The state ladder S0-S7 (plan I6) builds, and each lesson's "start" equals the previous lesson's stated end.
6. Every relative Markdown link under WS resolves (ignore docs/research/). Every file, command, template and gate that a learner-facing page mentions exists.
7. Gates gate-0, gate-a, gate-b and gate-1 each have rubric.md and examiner-prompt.md; "exam <gate>" produces a sitting with one task for each lesson the gate covers and grades it; a retest holds only the lessons not passed; "exam <gate> --explain pass" is refused before a graded sitting and recorded after one; the time each lesson and rubric states for a gate agrees with what the tool prints plus about 10 minutes for the explain-back part.
8. WS/CLAUDE.md exists, begins with the "who are you" section, and requires the fixed status line; README.md tells a newcomer the exact first step and what to do if the status line is missing.
9. Privacy: no real user name, e-mail address or computer name in any file outside docs/research/local-only/ (search for the account name of this machine, obtained with "id -un", for the output of "scutil --get ComputerName" and "hostname", and for e-mail patterns; do not print the values you search for). Report file and line only.
10. Freshness: every lesson's META has verified.date and verified.tools; "python3 tools/course.py fresh" runs; every learner-facing step that could not be executed is marked per plan G6 and listed in META["unverified_steps"]. Collect the full list of such steps by lesson.
11. Budgets (plan G5 with its revision G5a): per station one new concept, at most five new commands and stated minutes between 15 and 40; per lesson at most two new rule cards; the hours that ROADMAP.md, README.md and the two stage pages state for stages 0 and 1 equal the numbers the generator derives from the lessons' minutes (python3 tools/dev/build_reference.py prints them). List violations.
12. The promises of the design's section 5.10 that can be checked: list for each of its five quality steps what evidence exists in the workspace or in the build reports below.

Then write WS/docs/authoring/qa/batch-1-acceptance.md in plain Chinese: what was checked and how, the results, the full list of steps nobody could execute and why, the known issues, and what the first five real study sittings are expected to calibrate. Update the status line in ROADMAP.md and add the CHANGELOG entry accordingly (say honestly "已验收" or "已验收，有已知问题").

PLAY-THROUGH REPORTS:
${JSON.stringify(plays).slice(0, 60000)}

FIX REPORTS:
${JSON.stringify(fixes).slice(0, 40000)}

CONFIRM REPORTS AND SECOND FIXES:
${JSON.stringify(confirms).slice(0, 40000)}`, { label: 'accept', phase: 'Accept', schema: ACCEPT, ...OPTS })

return { plays, fixes, confirms, accept }
