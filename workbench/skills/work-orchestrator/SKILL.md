---
name: work-orchestrator
description: "Use this skill when the user invokes /build or asks to implement a spec, drive a spec to a PR, or run the full development pipeline. Takes a validated spec and drives it to a reviewed, gated PR per issue."
---

# work-orchestrator

## Purpose
Take a validated spec and drive each issue to a reviewed, gated PR with
the developer in control at each gate.

## Inputs
- A validated spec (`spec.md` + `spec.status.json` with `"valid": true`)

## Pipeline (per issue)
1. **Plan:** Run the `planner` subagent with the spec. Python writes issues to
   `issues.json` and opens GitHub Issues via `issue.py`.
2. **TDD:** Invoke `sdet-architect` to write failing tests for the issue.
3. **Code generation:** Implement until the issue's tests pass.
   `test_runner.py` runs the tests; the model edits code.
4. **Code-to-spec validation (fresh context):** Spawn the `code-to-spec-validator`
   subagent with only the spec, the issue, and the diff.
   It must never see the building context.
5. **PR review (fresh context):** Spawn the `pr-reviewer` subagent with only
   the diff and `rules/coding-standards.md`.
6. **Quality gates:** Run `python3 hooks/quality_gates.py pre-tool`.
   A non-zero exit stops the issue and reports why.
7. **Human approval gate:** Present the validator notes, reviewer notes, and
   gate results. Stop and wait for explicit developer approval.
8. **PR creation:** On approval, `pr.py` opens the PR with spec link,
   validator notes, reviewer notes, and gate results attached.

## Gates and overrides
- No PR is created if the validator fails, reviewer flags a BLOCKER, or any gate fails.
- Developer may override with a recorded reason: `{"event":"override","reason":"..."}` appended to journey log.

## Fallback
If the CLI cannot spawn subagents inline, `scripts/orchestrate.py` calls
`claude --print` for each judgment stage and Python for deterministic stages.
The pipeline stages are identical either way.

## Python load-bearing
`issue.py`, `git_diff.py`, `test_runner.py`, `pr.py`, `secret_scan.py` —
all deterministic operations are delegated to these modules.

## Outputs
- One PR per issue with auditable trail
- `issues.json` updated with status per issue

## Acceptance criteria
- No PR is created if code-to-spec validation fails.
- No PR is created if PR review flags a BLOCKER.
- No PR is created if any quality gate fails (without recorded override).
- Validator and reviewer each run as a separate subagent (confirmed by distinct invocations).
