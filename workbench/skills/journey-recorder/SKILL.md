---
name: journey-recorder
description: "Use this skill when the user invokes /journey start, /journey stop, or /journey export, or asks to start/stop recording a lab session, export a journey, or view what was captured."
---

# journey-recorder

## Purpose
Record what a learner does in a lab (prompts, decisions, artifacts, gate results)
for playback and grading by `lab-grader`.

## Inputs
- Subcommand: `start | stop | export`
- For `export`: session ID (optional — defaults to current session)

## Steps

### /journey start
1. Set `WORKBENCH_JOURNEY_DIR` to `journey/` in the current project.
2. Print the session ID so the learner can reference it.
3. The hooks (`hooks.json`) will record events automatically from this point.

### /journey stop
1. Append a `stop` event to the journey file.
2. Print the journey file path.

### /journey export <session_id>
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/journey-recorder/scripts/recorder.py export <session_id>`
2. This converts `journey/<session_id>.jsonl` to `journey/<session_id>.md` (human-readable).
3. Print the path of the exported file.

## Python load-bearing
`recorder.py` manages the export from JSONL to readable markdown.
The hook (`journey_record.py`) handles all event appending — the skill only
controls start/stop/export.

## Outputs
- `journey/<session>.jsonl` — append-only event log (written by hooks)
- `journey/<session>.md` — human-readable export (written by recorder.py)

## Acceptance criteria
- A completed lab produces a journey file showing each stage the learner passed through.
- The exported `.md` is human-readable and lists events chronologically.
- No PAN or secrets appear in any journey file.
