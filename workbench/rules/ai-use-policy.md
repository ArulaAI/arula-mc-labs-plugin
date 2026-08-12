# AI Use Policy

## What Claude may do autonomously
- Read files, search the codebase, run tests
- Write and edit code in the current working branch
- Run `claude plugin validate`
- Run `quality_gates.py` checks
- Write to the journey log

## What requires human approval (gates)
- Creating a pull request
- Opening a GitHub Issue
- Pushing to `main`
- Any override of a failed quality gate (must record reason)
- Any action that writes outside the project directory

## Audit trail
- Every gate decision (approve / override) is appended to `journey/<session>.jsonl`
- Override reason is required and logged with the override event
- The journey file is append-only and must not be edited after writing

## Anti-sycophancy rule
- The `code-to-spec-validator` and `pr-reviewer` subagents run with clean context
- They must not see the building context that produced the artifact they judge
- Their findings must not be softened or filtered before presenting to the developer
