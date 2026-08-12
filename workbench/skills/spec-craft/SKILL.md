---
name: spec-craft
description: "Use this skill when the user invokes /spec or asks to create, draft, or validate a spec. Turns an intent plus context into a validated, standardised spec the team trusts. Requires the superpowers plugin to be installed as a companion."
---

# spec-craft

## Purpose
Turn a problem statement and context into a validated, standardised spec
conforming to `rules/spec-template.md`. Blocks until the spec passes structural
validation and the human approves it.

## Inputs
- Short problem statement (required)
- Links or notes on relevant ISO message types and API contracts (optional)
- Team non-negotiables (optional)

## Steps
1. **Brainstorm:** Invoke `superpowers:brainstorming` to pressure-test the intent.
   If superpowers is not installed, stop and instruct the user to install it:
   `claude plugin install superpowers@claude-plugins-official`
2. **Draft:** Format the brainstorm output into the `rules/spec-template.md`
   structure. Write the draft to `spec.md` in the current directory.
3. **Validate:** Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/spec-craft/scripts/validate_spec.py spec.md`
   - If gaps are found: list them explicitly and ask the user to address them.
   - Repeat until the script reports `"valid": true`.
4. **Gate:** Present a "ready to work" summary to the developer and stop.
   Do not proceed to implementation without explicit approval.

## Python load-bearing
`validate_spec.py` does all structural checks (required sections, testable ACs).
The model judges completeness and clarity only — it does not override the script.

## Outputs
- `spec.md` — the validated spec
- `spec.status.json` — `{"valid": true/false, "missing_sections": [...], "non_testable_acs": [...]}`

## Acceptance criteria
- A spec missing a required section is reported NOT READY with the section named.
- A spec with a non-testable AC (no Given/When/Then or assertion verb) is reported NOT READY with the AC-ID named.
- A spec that passes all checks produces `"valid": true` in `spec.status.json`.
