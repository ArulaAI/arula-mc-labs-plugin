---
name: hand-off
description: "Close out the stage that just finished. Appends a structured checkpoint to docs/workflow-tracker.md. Run it at every stage boundary."
---

You are closing out the stage the user just finished. You are not starting the next one and you
are not writing a project report. Keep it short and factual.

1. From the conversation so far, identify: which stage just closed, what artifact(s) it produced
   or changed, what verdict or decision was reached (a tool verdict where one exists — e.g.
   `spec.status.json valid:true`, `VALIDATION: PASS/FAIL`, `REVIEW: APPROVE / REQUEST CHANGES /
   BLOCKER`, a test or build result — otherwise the user's explicit call), what the user confirmed
   at the stage's human gate, and anything left open.
2. If any of that is ambiguous, ask in one line rather than guessing.
3. Append one entry to `docs/workflow-tracker.md` (create it if absent) in exactly this format:

   ```
   ## Stage <n> — <stage name>
   - **Closed:** <UTC timestamp>
   - **Artifacts:** <files created or changed this stage>
   - **Verdict / decision:** <the tool verdict, or the user's explicit call>
   - **Human gate:** <one line — what the user confirmed before moving on>
   - **Open items:** <anything carried forward, or "none">
   - **Next step:** <the one thing that happens next>
   ```

4. If the project provides `.claude/scripts/journey_event.py`, run it from the workspace root to
   record the boundary; otherwise skip this step — the plugin's `journey_record.py` hook already
   captures session events automatically.
5. Confirm back in one line that the stage is recorded.

`docs/workflow-tracker.md` is the human-readable record. The graded evidence is the hook-captured
journey, which is independent of what this command writes — so a thin or skipped hand-off never
silently breaks grading integrity.

Do not restate the spec, the diff or the code. Do not summarise the whole session. This is one
stage's close-out record.
