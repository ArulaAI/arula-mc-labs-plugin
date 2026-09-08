---
name: lab
description: "Start a lab session. Usage: /lab [lab_number]"
---
1. Read `.claude/lab.json`. If it does not exist, prompt the user for the lab number and create
   a starter from `docs/lab.json.example`.
2. Start journey recording with /journey start.
3. Run the deterministic renderer to display the lab title and objectives:
   ```
   bash "${CLAUDE_PLUGIN_ROOT}/hooks/run-python" "${CLAUDE_PLUGIN_ROOT}/scripts/render_lab.py"
   ```
   Present its stdout to the participant exactly as printed.
4. Do not summarize, rephrase, or reorder the objectives.
5. Do not print the rubric path or implementation metadata.
6. Do not ask a follow-up question.
7. **Stop. Name what comes first, and wait for the learner.**

## Stop after the objectives

Steps 4 to 6 above say not to reword the objectives, not to print internals, and not to ask a
follow-up. This section is about the larger version of the same instinct: not to carry on into the
lab.

This command initialises a session. It is not the beginning of the lab's first stage, and it must
not become it.

An unattended run of this command was once observed taking initialisation as licence to continue:
it read the lab's source repositories, dispatched its analysis sub-agents, reconciled their
findings, drafted the lab's first deliverable, and only then asked the learner the questions that
deliverable was supposed to raise. Every individual step was competent. Taken together they
consumed the first stage before the learner had typed anything, and what was left for them was
approving a document they had not reasoned about.

That is a loss whatever the lab. A learner who is handed a finished first artifact has practised
reviewing, not the thing the stage was built to teach.

So after the renderer has printed, do **not** do any of the following in the same turn, however
useful they would be and however clearly the lab's own guide asks for them at a later stage:

- **No reads of the material under study.** Not the lab's source repositories, service directories,
  or code under review. Not a directory listing, not "just the build file", not one file to orient
  yourself. `.claude/lab.json` and the renderer's output are the whole of this command's input.
- **No sub-agents.** No auditors, implementers, reviewers or exploratory agents.
- **No writes to lab deliverables** -- ledgers, specs, plans, trackers, or any artifact a stage is
  meant to produce.
- **No stage decision questions.** Where a lab defines questions to put to the learner at a stage,
  those require that stage's evidence to exist. Asked at initialisation they are unanswerable, and
  asking them anyway teaches that they are a formality. This is narrower than step 6: even a
  question the lab genuinely does ask later is wrong here.
- **No rubric criteria text.** Step 5 covers the rubric's path; this covers its contents. A rubric's
  criteria describe what will be graded, and for labs that ask the learner to discover something,
  reading the criteria aloud at minute zero tells them the answer. The renderer prints the
  objectives; print nothing else from the rubric.

Stopping while holding useful momentum is the point, not a limitation to work around. If you can
already see what the first stage needs, that is precisely the moment the learner should be the one
to decide it.
