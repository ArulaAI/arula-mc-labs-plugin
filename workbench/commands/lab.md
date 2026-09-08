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
