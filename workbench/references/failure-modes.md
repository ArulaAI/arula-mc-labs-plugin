# Five Failure Modes

These are the canonical taxonomy used by `code-to-spec-validator` to score a diff.
Load this file verbatim as part of the validator's input context.

## Failure Mode 1 — Spec Drift
The implementation diverges from what the spec says: different field names,
wrong logic, missing requirement, or behaviour that contradicts the spec.

**Verdict: FAIL** if any AC from the spec has no corresponding implementation.

## Failure Mode 2 — Missing Acceptance Criterion
At least one AC from the spec has no corresponding code path or test.
The AC exists in the spec but is not exercised by any diff in this issue.

**Verdict: FAIL** if any AC is unaddressed.

## Failure Mode 3 — Unsafe Data Handling
PAN, credentials, or sensitive ISO fields are logged, persisted, transmitted
insecurely, or written to a journey file without redaction.

**Verdict: FAIL** — no exceptions. See `payments-guardrails.md`.

## Failure Mode 4 — Broken Contract
A downstream API contract, ISO message boundary, or emulator interface is
violated. Includes: wrong field type, wrong sequence, missing mandatory field,
undocumented breaking change.

**Verdict: FAIL** if the contract change is not explicitly approved in the PR.

## Failure Mode 5 — Missing Human Gate
A step that requires developer approval (see `ai-use-policy.md`) ran without it,
or the override was not recorded with a reason in the journey log.

**Verdict: FAIL** — gate bypasses are never acceptable without a recorded reason.
