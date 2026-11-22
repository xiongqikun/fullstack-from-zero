export const meta = {
  name: 'tutor-tests',
  description: 'Test the tutor contract (CLAUDE.md and the playbook) in simulation homes with real tool runs: stage each scripted situation, let a fresh tutor answer, judge the replies, fix the contract, run the failed situations again',
  phases: [
    { title: 'Kit', detail: 'one helper that writes learner state through the tool' },
    { title: 'Round 1', detail: 'stage, tutor turns and judge for every situation' },
    { title: 'Fix', detail: 'one owner changes the contract, the playbook, the gates or a test row' },
    { title: 'Round 2', detail: 'the failed situations again, with fresh tutors' },
    { title: 'Confirm', detail: 'an independent look at every change, then a last narrow fix' },
  ],
}

const WS = args.ws
const SCRATCH = args.scratch + '/tutor-tests'
const TODAY = args.today || '2026-11-20'
const NOTES = args.notes || ''
const IDS = args.situations || []
const CARRIED = args.carried || ''
const OPTS = { model: args.model || 'opus', effort: args.effort || 'high' }
const LIMIT = Number(args.concurrency) || 4
const TESTS = WS + '/docs/authoring/tutor-tests.md'
const HELPER = WS + '/docs/authoring/build-kit/stage_state.py'

let active = 0
const waiting = []
async function slot(fn) {
  if (active >= LIMIT) await new Promise(resolve => waiting.push(resolve))
  else active++
  try { return await fn() } finally { const next = waiting.shift(); if (next) next(); else active-- }
}

const BUILDER = `You are an agent working on a local learning workspace for a Chinese-speaking adult who is learning software engineering from zero. Today is ${TODAY}. You were dispatched for an explicit build or test task: the tutoring rules in WS/CLAUDE.md do not bind you.

WORKSPACE ROOT (WS): ${WS}
THE TESTS: ${TESTS} (the scripted situations and what the contract requires in each; its section "How to run a test" is the procedure).
THE CONTRACT UNDER TEST: WS/CLAUDE.md (the rules) and WS/docs/tutor/playbook.md (the procedures); WS/gates/<gate>/rubric.md and examiner-prompt.md belong to it.
TOOL API: WS/docs/authoring/tool-api.md.
YOUR SCRATCH AREA: ${SCRATCH}/<your label>/.

HARD RULES:
- Never touch the real ~/.gitconfig, ~/.zshrc, ~/Developer or any global configuration. No installs, no accounts, no pushes, no git commits inside WS. Simulation homes are made with "python3 tools/dev/make_sim_home.py" under $TMPDIR; work in zsh; in every command that runs the course tool for a simulated learner set HOME to the simulation's home, COURSE_NOW to the situation's date and a time later than any staged session (YYYY-MM-DDTHH:MM, for example 2026-11-20T21:30; a bare date counts as 00:00 and opens a second session), and PYTHONDONTWRITEBYTECODE=1.
- Never run the tool's whole test suite. Leave no __pycache__ or debris in WS.
- Never write the real user name, e-mail address or computer name of this machine into any file, and never print them.
- Your final structured output is a factual report for the orchestrator.
${NOTES}`

const KIT = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    helper: { type: 'string', description: 'absolute path of the helper script' },
    usage: { type: 'string', description: 'how a stage agent calls it: every option, with one worked example per kind of state' },
    tested: { type: 'string' },
    open_issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'helper', 'usage', 'tested', 'open_issues'],
}

const STAGE = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    staged: { type: 'boolean' },
    why_not: { type: 'string' },
    today: { type: 'string', description: 'the date of the situation, YYYY-MM-DD' },
    now: { type: 'string', description: 'the date and time at which the conversation happens, YYYY-MM-DDTHH:MM, later than every session you staged' },
    threads: {
      type: 'array',
      description: 'one entry per conversation to run; each has its own simulation home',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'for example "main", "follow-up A", "variant: lesson 1.8"' },
          sim: { type: 'string', description: 'the simulation folder (remove this one when the test is over)' },
          home: { type: 'string', description: 'the simulated home folder' },
          workspace: { type: 'string', description: 'the folder the tutor works in, as an absolute path' },
          messages: { type: 'array', items: { type: 'string' }, description: 'the learner messages in order, exactly as the learner sends them' },
        },
        required: ['name', 'sim', 'home', 'workspace', 'messages'],
      },
    },
    setup: { type: 'string', description: 'what you created, how, and the tool output that shows the state is the one the situation describes' },
    notes_for_judge: { type: 'string' },
  },
  required: ['id', 'staged', 'today', 'now', 'threads', 'setup'],
}

const TURN = {
  type: 'object',
  properties: {
    reply: { type: 'string', description: 'the exact text you send to the user, complete, from its first line to its last' },
    actions: { type: 'array', items: { type: 'string' }, description: 'in order: every file you read (path), every command you ran (the command, then one line on what it printed), every file you wrote or changed (path and what)' },
  },
  required: ['reply', 'actions'],
}

const VERDICT = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    verdict: { type: 'string', enum: ['pass', 'fail', 'not-run'] },
    rows: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          row: { type: 'string', description: 'C1..C5, or the Must / Must not point in a few words' },
          result: { type: 'string', enum: ['met', 'missed', 'not-applicable'] },
          quote: { type: 'string', description: 'the words of the reply, or the action, that decide it' },
        },
        required: ['row', 'result', 'quote'],
      },
    },
    failures: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          row: { type: 'string' },
          cause: { type: 'string', enum: ['missing rule', 'ambiguous rule', 'rule buried too deep', 'contradiction in the contract', 'contract contradicts a lesson or the tool', 'clear rule ignored by the tutor', 'test row wrong or out of date', 'staging fault', 'harness artefact'] },
          what_happened: { type: 'string' },
          file: { type: 'string' },
          where: { type: 'string' },
          change: { type: 'string', description: 'the exact wording change: the old words and the new words' },
        },
        required: ['row', 'cause', 'what_happened', 'change'],
      },
    },
    contract_notes: { type: 'string', description: 'anything about the contract itself that this situation showed, even where the reply passed' },
    transcript_file: { type: 'string' },
    sims_removed: { type: 'boolean' },
  },
  required: ['id', 'verdict', 'rows', 'failures'],
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

const CONFIRM = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['clean', 'issues'] },
    checked: { type: 'string' },
    still_open: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          where: { type: 'string' },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          problem: { type: 'string' },
          evidence: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['where', 'severity', 'problem', 'evidence', 'fix'],
      },
    },
  },
  required: ['verdict', 'checked', 'still_open'],
}

phase('Kit')
const kit = args.helper_ready ? { helper: HELPER, usage: `It exists and is tested. Read its docstring and run "python3 ${HELPER} --help-spec" for the full reference; the commands are apply, show, peek and --self-test. Examples of specs are in ${SCRATCH}/kit/.`, open_issues: [] } : await slot(() => agent(`${BUILDER}

YOUR LABEL: kit
YOUR TASK: write the helper that the stage agents of this test use to give a simulated learner the state a situation describes, and prove that it works. Twenty-five agents will each stage one situation with it right after you, so it has to be dependable and its usage has to be exact.

1. Read ${TESTS} completely (every "Setup" line tells you a kind of state that must be producible), tool-api.md (the sections on learner/state.json, sessions, hints, review scheduling, exam attempts, decisions, the journal, doctor and COURSE_NOW), and the code that owns that state under WS/tools/courselib/ and WS/tools/dev/make_sim_home.py.
2. Write ${HELPER} (Python 3.9 compatible, standard library only, no real names anywhere). It is run with HOME pointing at a simulation home and the working directory in that simulation's workspace copy; it refuses to run when HOME is not under a temporary folder. It writes state ONLY through the tool's own functions (import courselib from the workspace's tools/ folder), never by composing JSON by hand, so that the files are exactly what the tool itself would have written. It must be able to: mark a range of stations passed on given dates (with or without the whole-lesson check, with or without hints used and at which level); record study sessions on given dates; make a given number of review items due on a date; draw a gate sitting and leave it ungraded, or graded with chosen tasks passed and failed; record or not record an explain-back result; set a decision (for example workspace_location); fill learner/profile.md from templates/profile-template.md with a chosen strictness (严格 / 适中 / 宽松), weekly hours and a 累了协议; add a journal entry on a date. Where the tool offers no function for something, say so under open_issues and give the smallest honest alternative.
3. Prepare and test it in your scratch area first, in simulation homes of your own, on at least these three states: S2 (stations 0.1a to 1.6a passed, last session 2026-11-24, three review items due on 2026-11-26), S14 (gate-b graded, all practical tasks passed, no explain record) and S21 (a gate-b sitting drawn and not graded while the learner goes on). For each, run status, review (non-interactive), exam <gate> and doctor in the simulation with COURSE_NOW set and check that they print what the situation needs. Then copy the finished helper into place in one step and run its own self-test once more from there ("python3 ${HELPER} --self-test" must build a simulation home, write a state, check it with status and remove the home).
4. Return the usage as text a stage agent can follow without reading the code. Remove your simulation homes.`, { label: 'kit', phase: 'Kit', schema: KIT, ...OPTS }))

const usage = kit ? `THE STATE HELPER: ${kit.helper || HELPER}\n${kit.usage}\n${(kit.open_issues || []).length ? 'KNOWN LIMITS OF THE HELPER: ' + kit.open_issues.join(' | ') : ''}` : `THE STATE HELPER could not be written; create the learner files as the section "How to run a test" says, through the tool where possible.`

const stagePrompt = (id, round) => `${BUILDER}

YOUR LABEL: stage-${id}-r${round}
YOUR TASK: stage situation ${id} of ${TESTS}: build the simulation home or homes in which a fresh tutor will meet the learner, exactly as the "Setup" line and the section "How to run a test" (step 1) describe. You do not play the tutor and you do not judge.

${usage}

WHAT TO DO
1. Read the common part and the rows of ${id} in ${TESTS}. Decide the conversations ("threads") to run. One thread is one conversation: the learner's first message and, where the situation scripts them, the follow-up messages in order. A situation with branches (Follow-up A and Follow-up B, or a Variant) needs one thread per branch, each starting again from the first message. A situation whose learner answers the tutor's questions (for example scripted answers to explain-back questions) is one thread with those answers in order; where the script does not give the words of an answer that the tutor will need (for example "answer question 2 adequately"), write a plausible beginner's answer of the required quality yourself. When the learner "pastes" tool output, produce that output for real in the simulation and put it into the message verbatim.
2. For each thread make its own simulation home with "python3 tools/dev/make_sim_home.py" under $TMPDIR, named tt-r${round}-${id}-<n> (use the options the situation needs: a learner who stayed, a workspace somewhere else, and so on). Give the learner the state of the "Setup" line with the helper; set the time of the situation with COURSE_NOW as YYYY-MM-DDTHH:MM, later than any session you stage (use the date the situation names, or ${TODAY} if it names none, with a time such as T21:30), and report that value as "now". Create by hand only what no tool function writes (for example the edit the tutor is said to have made before the conversation, or a changed starter file). After building each simulation, remove <simulated workspace>/docs/authoring/tutor-tests.md, so that the tutor cannot read the expected rows.
3. Check each simulation the way a tutor would see it: run status (and doctor, review or exam where the situation depends on them) with HOME and COURSE_NOW set, and compare with what the situation says. If it differs, fix the staging. Be careful: status records a study session on the date of COURSE_NOW. If the situation depends on the last session date (for example "last session 2026-11-24, today 2026-11-26"), run your checks in a throw-away copy of the simulation, or with a COURSE_NOW that equals the last session date, so that the simulation the tutor gets holds exactly the sessions the situation describes.
4. Report: today (the situation's date), the threads (sim folder, home, the workspace folder as an absolute path that the tutor works in, the learner messages), what you created and the output that proves the state, and anything the judge must know (for example "the simulation has no network, so the tutor cannot open a web page"). If the situation cannot be staged honestly, set staged to false and say why. Do NOT remove the simulation homes: the tutor and the judge use them.`

const tutorPrompt = (thread, today, now, turns, message) => `You are Claude, working in the Claude desktop app, in the Code tab. The project folder of this session is ${thread.workspace}. The project instructions of this folder are in the file ${thread.workspace}/CLAUDE.md: read that file completely before anything else and follow it, as you follow the project instructions the app loads for you.

Notes from the app about this session (they are not from the user):
- The user's home folder is ${thread.home}. Your shell does not start there, so begin every shell command you run with:  export HOME="${thread.home}" COURSE_NOW="${now}" PYTHONDONTWRITEBYTECODE=1; cd "${thread.workspace}" &&   (COURSE_NOW is how this machine's clock reaches the tools: keep it exactly as written, with its time; today is ${today}).
- Read and write only inside ${thread.home}. Nothing outside it belongs to this session.
- In this session you have no tool that opens a file or a terminal pane for the user, and you cannot see the user's terminal: you see only what the user sends you.
- The user is not at the keyboard while you work on this turn: do what you would do before answering, then write the one reply you would send now, and stop where you would wait for the user.
${turns.length ? `
THE CONVERSATION SO FAR (earlier turns of this same conversation; what you did then is already done, the files are as you left them):
${turns.map((t, i) => `--- user, message ${i + 1} ---\n${t.learner}\n--- your reply ${i + 1} ---\n${t.reply}\n--- what you did before reply ${i + 1} ---\n${(t.actions || []).join('\n').slice(0, 6000)}`).join('\n')}
` : ''}
--- user, message ${turns.length + 1} ---
${message}

Return your reply exactly as you send it (the complete text), and the list of what you did before sending it: every file you read, every command you ran with one line on what it printed, every file you wrote or changed.`

const judgePrompt = (id, round, st, transcripts) => `${BUILDER}

YOUR LABEL: judge-${id}-r${round}
YOUR TASK: judge situation ${id} of ${TESTS}. A fresh agent that had only the simulated workspace (its CLAUDE.md and the files that file sends a tutor to) answered the learner. You are a different agent: you did not stage the situation and you did not answer it. Modify nothing under WS.

1. First save the transcripts below as readable Markdown (each learner message, each reply in full, the actions) to ${SCRATCH}/r${round}/${id}-transcript.md.
2. Read the common rows C1 to C5 and the rows of ${id} in ${TESTS}, the sections of WS/CLAUDE.md and WS/docs/tutor/playbook.md that the situation names, and the rubric or lesson it refers to. Then look into each simulation folder to see what the tutor really did there: files written or changed (compare with a fresh copy where needed), learner/state.json, learner/log.jsonl (hint levels, sessions), anything created outside the places CLAUDE.md section 8 allows.
3. Score every row: each Must met, no Must not present, C1 to C5. Quote the words of the reply or the action that decide each row. One miss fails the situation. Judge what the contract requires, not style: a reply that does the right thing in other words passes.
4. For every miss name the cause honestly. If the tutor did what CLAUDE.md and the playbook say and the test row asks for something no rule requires, or the row is out of date, the cause is the test row. If the staging did not give the state the situation describes, it is a staging fault. If the miss comes only from the way this test is run (the note about the home folder, no tool to open files, a missing network, no second speaker), it is a harness artefact. Otherwise say whether a rule is missing, ambiguous, buried too deep, contradicted inside the contract, contradicted by a lesson or by what the tool prints, or was clear and ignored. Give the exact wording change for the file that has to change (old words, new words); for "clear rule ignored" say what would make the rule harder to miss (position, wording), or that nothing should change.
5. Under contract_notes report anything else this run showed about the contract: a rule a model cannot act on, a procedure that does not match what the tool printed in the simulation, a sentence of the playbook the tool or the lesson no longer uses.
6. Last, remove the simulation folders of this situation (the "sim" paths below) and nothing else.

THE STAGING REPORT:
${JSON.stringify({ today: st.today, setup: st.setup, notes_for_judge: st.notes_for_judge }).slice(0, 20000)}

THE TRANSCRIPTS:
${JSON.stringify(transcripts).slice(0, 120000)}`

async function runSituation(id, round) {
  const ph = 'Round ' + round
  const st = await slot(() => agent(stagePrompt(id, round), { label: `stage:${id}:r${round}`, phase: ph, schema: STAGE, ...OPTS }))
  if (!st || !st.staged || !(st.threads || []).length) return { id, round, staged: false, why_not: st ? st.why_not : 'the stage agent returned nothing', transcripts: [], verdict: null }
  const transcripts = []
  for (let t = 0; t < st.threads.length; t++) {
    const th = st.threads[t]
    const turns = []
    for (let k = 0; k < (th.messages || []).length; k++) {
      const r = await slot(() => agent(tutorPrompt(th, st.today, /T\d\d:\d\d/.test(String(st.now || '')) ? st.now : st.today + 'T21:30', turns, th.messages[k]), { label: `tutor:${id}:${t + 1}.${k + 1}:r${round}`, phase: ph, schema: TURN, ...OPTS }))
      if (!r) break
      turns.push({ learner: th.messages[k], reply: r.reply, actions: r.actions || [] })
    }
    transcripts.push({ thread: th.name, sim: th.sim, home: th.home, workspace: th.workspace, turns })
  }
  const verdict = await slot(() => agent(judgePrompt(id, round, st, transcripts), { label: `judge:${id}:r${round}`, phase: ph, schema: VERDICT, ...OPTS }))
  return { id, round, staged: true, today: st.today, verdict }
}

const failed = rs => rs.filter(r => r && (!r.verdict || r.verdict.verdict !== 'pass'))
const brief = rs => rs.map(r => ({ id: r.id, round: r.round, staged: r.staged, why_not: r.why_not, verdict: r.verdict ? r.verdict.verdict : 'not-run', failures: r.verdict ? r.verdict.failures : [], contract_notes: r.verdict ? r.verdict.contract_notes : '', transcript: `${SCRATCH}/r${r.round}/${r.id}-transcript.md` }))

const OWNER = `You own WS/CLAUDE.md, WS/docs/tutor/playbook.md, everything under WS/gates/ and ${TESTS}. You edit nothing else: if a lesson, a cheat sheet, a template or the tool has to change, report it under open_issues, starting with "lesson <id> needs:", "shared file needs:" or "tool needs:", with the exact replacement text. Before your first edit, if ${SCRATCH}/snapshot does not exist yet, copy those four paths into it unchanged (it is what the confirmer compares with). Keep WS/CLAUDE.md under about 220 lines: detail belongs in the playbook. Keep every change minimal. A test row is changed only when the judge showed that it asks for something no rule requires or that it is out of date; never loosen a row to make a reply pass. After your changes re-read CLAUDE.md and the playbook from top to bottom for contradictions, and check each changed sentence against what the lessons tell the learner the tutor will do (search the lessons for 导师) and against what the tool prints.`

phase('Round 1')
const round1 = (await parallel(IDS.map(id => () => runSituation(id, 1)))).map((r, i) => r || { id: IDS[i], round: 1, staged: false, why_not: 'the run of this situation stopped with an error', verdict: null })
const failed1 = failed(round1)
log(`tutor tests, round 1: ${round1.length - failed1.length} of ${round1.length} passed; not passed: ${failed1.map(r => r.id).join(', ') || 'none'}`)

phase('Fix')
const fix1 = !(failed1.length || CARRIED) ? null : await slot(() => agent(`${BUILDER}

YOUR LABEL: fix-1
YOUR TASK: change the tutor contract so that what round 1 of the tutor tests showed is put right. ${OWNER}

WHAT YOU GET
- The verdicts of the situations that did not pass, with the cause and the wording change the judge proposes, and the judges' notes on the contract from all situations (below). The full transcripts are in ${SCRATCH}/r1/<id>-transcript.md: read the transcript before you act on a verdict, and decide yourself whether the judge is right.
- A list of items carried over from the cross-check that concern your files${CARRIED ? ': read ' + CARRIED + ' completely and deal with every item (done already, done now, or rejected with the reason)' : ' (none)'}.

HOW TO DECIDE
- "missing rule", "ambiguous rule", "rule buried too deep", "contradiction": change CLAUDE.md or the playbook. Prefer moving or sharpening a sentence to adding one.
- "clear rule ignored by the tutor": change something only if the same rule was ignored in more than one situation or sits where a model reaches it too late; say what you did.
- "test row wrong or out of date": correct the row in ${TESTS}.
- "staging fault" and "harness artefact": change nothing in the contract; if the section "How to run a test" of ${TESTS} should warn the next runner, add one sentence there. Also add to that section one sentence that names the state helper WS/docs/authoring/build-kit/stage_state.py and the script WS/docs/authoring/build-kit/tutor-tests.js that runs these tests.
- A situation that could not be staged: say why under open_issues.
Report every finding you rejected, with the reason.

ROUND 1, NOT PASSED:
${JSON.stringify(brief(failed1)).slice(0, 120000)}

ROUND 1, NOTES ON THE CONTRACT FROM THE SITUATIONS THAT PASSED:
${JSON.stringify(round1.filter(r => r.verdict && r.verdict.verdict === 'pass' && r.verdict.contract_notes).map(r => ({ id: r.id, contract_notes: r.verdict.contract_notes }))).slice(0, 40000)}`, { label: 'fix:1', phase: 'Fix', schema: REPORT, ...OPTS }))

phase('Round 2')
const again = failed1.map(r => r.id)
const round2 = again.length ? (await parallel(again.map(id => () => runSituation(id, 2)))).map((r, i) => r || { id: again[i], round: 2, staged: false, why_not: 'the run of this situation stopped with an error', verdict: null }) : []
const failed2 = failed(round2)
if (again.length) log(`tutor tests, round 2: ${round2.length - failed2.length} of ${round2.length} passed; still not passed: ${failed2.map(r => r.id).join(', ') || 'none'}`)

const fix2 = failed2.length ? await slot(() => agent(`${BUILDER}

YOUR LABEL: fix-2
YOUR TASK: a second, narrow change of the tutor contract. After the first fix the situations below were run again with fresh tutors and still did not pass. ${OWNER}
Read the transcript of each (${SCRATCH}/r2/<id>-transcript.md) and the first fixer's report below. Decide for each whether the contract, the test row or the staging is at fault, and act as the first fixer was told to: change the contract only where the transcript shows that a rule is missing, unclear, contradicted or placed too late. These changes will not be run again in this test, so be conservative, and say plainly under open_issues which situations remain unproven.

ROUND 2, NOT PASSED:
${JSON.stringify(brief(failed2)).slice(0, 120000)}

THE FIRST FIXER'S REPORT:
${JSON.stringify(fix1).slice(0, 30000)}`, { label: 'fix:2', phase: 'Round 2', schema: REPORT, ...OPTS })) : null

phase('Confirm')
const confirm = !(fix1 || fix2) ? null : await slot(() => agent(`${BUILDER}

YOUR LABEL: confirm
YOUR TASK: an independent check of every change the fixers made to the tutor contract in this test. You did not make the changes. Modify nothing under WS.

1. Compare ${SCRATCH}/snapshot (the state before the fixers) with WS/CLAUDE.md, WS/docs/tutor/playbook.md, WS/gates/ and ${TESTS} as they are now (diff -r). Read every changed passage in its section.
2. For each change decide: is it true (check every command, option, file name and quoted tool sentence it contains: run the tool in a simulation home of your own, read the lesson it names); does it contradict another sentence of CLAUDE.md or the playbook; does it contradict what a lesson tells the learner the tutor will do, or what the tool prints; can a model act on it; did it loosen a test row without a reason given in the fixers' reports.
3. Check that CLAUDE.md still begins with section 0, still requires the status line as the first line of every reply, and is under about 220 lines; that every sentence in the table of section 3 still has its playbook section; that every "急救：……" sentence the lessons, README.md and the tool tell the learner to say has an entry in playbook §5 (search for 急救： in WS/stages, WS/README.md and WS/tools/courselib).
4. Report what is still wrong or newly wrong, with the place, the evidence and the exact fix. Remove your simulation homes.

THE FIXERS' REPORTS:
${JSON.stringify([fix1, fix2]).slice(0, 60000)}`, { label: 'confirm', phase: 'Confirm', schema: CONFIRM, ...OPTS }))

const serious = confirm && (confirm.still_open || []).length > 0
const fix3 = serious ? await slot(() => agent(`${BUILDER}

YOUR LABEL: fix-3
YOUR TASK: put right what the independent check of the fixers' changes found. ${OWNER}
Reproduce each finding first; fix every blocker and major and every minor you cannot cite a reason against; report what you rejected and why.

THE CHECK'S FINDINGS:
${JSON.stringify(confirm.still_open).slice(0, 60000)}`, { label: 'fix:3', phase: 'Confirm', schema: REPORT, ...OPTS })) : null

return {
  kit,
  round1: brief(round1),
  fix1,
  round2: brief(round2),
  fix2,
  confirm,
  fix3,
  passed_round1: round1.filter(r => r.verdict && r.verdict.verdict === 'pass').map(r => r.id),
  passed_round2: round2.filter(r => r.verdict && r.verdict.verdict === 'pass').map(r => r.id),
  not_passed: failed2.map(r => r.id),
}
