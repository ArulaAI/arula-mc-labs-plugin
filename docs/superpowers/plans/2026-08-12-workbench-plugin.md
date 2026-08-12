# Workbench Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish the `workbench` Claude Code plugin for Mastercard AU — a private-marketplace plugin that standardises spec, test, build, review and ship, and powers the Learning Labs journey capture and grading.

**Architecture:** Sequential milestone build (Option A) on a single `main` branch with feature branches per issue; plugin lives in `workbench/`, marketplace entry in `marketplace/`, both in the monorepo `ArulaAI/arula-mc-labs-plugin`. Each milestone ends with a passing `claude plugin validate ./workbench`. The shared Python layer in `scripts/lib/` is the deterministic backbone; the model only does synthesis and judgment.

**Tech Stack:** Claude Code plugin system (v2.1.177+), Python 3.11+ (scripts), `gh` CLI (GitHub Issues + PRs), `claude plugin validate`, superpowers companion plugin (brainstorming + writing-plans skills).

## Global Constraints

- Plugin name: `workbench` (kebab-case, no spaces)
- Repo: `ArulaAI/arula-mc-labs-plugin`, private
- Claude Code CLI minimum: 2.1.177
- Python minimum: 3.11; `scripts/lib/` modules use stdlib only (no pip installs); skill-specific scripts under `skills/*/scripts/` may use pip-installed packages — document any dependency in the skill's SKILL.md
- All file names: kebab-case for directories, snake_case for Python files
- `plugin.json` required field: `name`; auto-discovery handles components — no explicit paths
- Every `SKILL.md` and agent `.md` must have YAML frontmatter with at minimum `name` and `description`
- Hooks file: `hooks/hooks.json` with `{ "hooks": { ... } }` wrapper
- No PAN, credentials, or secrets may appear in logs, diffs, or journey files
- Five failure modes live in `references/failure-modes.md` and are loaded verbatim by `code-to-spec-validator`
- Superpowers plugin is a required companion — document this in README and ARCHITECTURE.md

---

## Task 1: GitHub repo + plugin scaffold + marketplace entry

**Files:**
- Create: `workbench/.claude-plugin/plugin.json`
- Create: `marketplace/.claude-plugin/marketplace.json`
- Create: `workbench/README.md` (stub — full content in Task 14)
- Modify: `.git/config` (remote origin)

**Interfaces:**
- Produces: a valid local plugin directory at `workbench/` that passes `claude plugin validate ./workbench`

- [ ] **Step 1: Create the GitHub repo**

```bash
gh repo create ArulaAI/arula-mc-labs-plugin \
  --private \
  --description "Mastercard AU engineering workbench Claude Code plugin" \
  --source . \
  --remote origin \
  --push
```

- [ ] **Step 2: Scaffold the plugin directory**

```bash
mkdir -p workbench/.claude-plugin
mkdir -p workbench/commands
mkdir -p workbench/skills
mkdir -p workbench/agents
mkdir -p workbench/hooks
mkdir -p workbench/rules
mkdir -p workbench/scripts/lib
mkdir -p workbench/references
mkdir -p workbench/docs
mkdir -p marketplace/.claude-plugin
```

- [ ] **Step 3: Write `workbench/.claude-plugin/plugin.json`**

```json
{
  "name": "workbench",
  "version": "0.1.0",
  "description": "Mastercard AU engineering workbench: spec, test, build, review and ship for Claude Code.",
  "author": {
    "name": "Arula.AI / InRhythm",
    "email": "rbuchanan@inrhythm.com"
  },
  "keywords": ["spec-driven", "sdet", "tdd", "governance", "payments"]
}
```

- [ ] **Step 4: Write `marketplace/.claude-plugin/marketplace.json`**

```json
{
  "name": "mastercard-workbench",
  "owner": "Mastercard AU (private)",
  "plugins": [
    {
      "name": "workbench",
      "source": "../workbench",
      "description": "Engineering workbench plugin"
    }
  ]
}
```

- [ ] **Step 5: Write stub `workbench/README.md`**

```markdown
# workbench

Mastercard AU engineering workbench Claude Code plugin.

> Full documentation in `docs/ARCHITECTURE.md` and `docs/EXTENDING.md`.
```

- [ ] **Step 6: Validate the plugin**

```bash
claude plugin validate ./workbench
```

Expected: no errors. Warnings about empty component directories are acceptable at this stage.

- [ ] **Step 7: Commit and push**

```bash
git add workbench/ marketplace/
git commit -m "feat(M1): scaffold plugin manifest and marketplace entry"
git push origin main
```

---

## Task 2: Rules, references, and shared Python lib

**Files:**
- Create: `workbench/rules/coding-standards.md`
- Create: `workbench/rules/ai-use-policy.md`
- Create: `workbench/rules/spec-template.md`
- Create: `workbench/rules/payments-guardrails.md`
- Create: `workbench/references/failure-modes.md`
- Create: `workbench/references/payments-checklist.md`
- Create: `workbench/references/pan-patterns.txt`
- Create: `workbench/references/iso-field-map.yaml`
- Create: `workbench/references/risk-weight-table.yaml`
- Create: `workbench/references/spec-template-reference.md`
- Create: `workbench/scripts/lib/git_diff.py`
- Create: `workbench/scripts/lib/test_runner.py`
- Create: `workbench/scripts/lib/coverage.py`
- Create: `workbench/scripts/lib/pr.py`
- Create: `workbench/scripts/lib/spec_check.py`
- Create: `workbench/scripts/lib/secret_scan.py`
- Create: `workbench/scripts/lib/issue.py`
- Create: `workbench/scripts/lib/__init__.py`
- Test: run each lib module with `python3 -m workbench.scripts.lib.<module>` (each has a `if __name__ == "__main__"` smoke test)

**Interfaces:**
- Produces: importable Python modules at `workbench/scripts/lib/*.py`; rules files auto-loaded by Claude Code

- [ ] **Step 1: Write `workbench/rules/coding-standards.md`**

```markdown
# Coding Standards

## General
- All functions must have a single clear responsibility
- No function longer than 50 lines
- All public functions must have a docstring (one line)
- Use snake_case for Python, kebab-case for file/directory names

## Payments-specific
- Never log, print, or write PAN (Primary Account Number) values — mask as `****-****-****-XXXX`
- Never log full ISO 8583 field 2 (PAN), field 35 (track 2), field 45 (track 1)
- All sensitive ISO fields must be redacted before writing to any log or journey file
- Authorization flows must match the spec's sequence diagram exactly

## Testing
- Every acceptance criterion in the spec must map to at least one test
- Tests must be deterministic — no random data, fixed seeds where randomness is needed
- Integration tests must use real filesystem / real subprocess — no mocking of OS calls

## Git
- One commit per logical change
- Commit messages: `type(scope): description` (feat, fix, docs, test, chore)
- No binary files in commits
- No secrets, PAN, or credentials in any commit
```

- [ ] **Step 2: Write `workbench/rules/ai-use-policy.md`**

```markdown
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
```

- [ ] **Step 3: Write `workbench/rules/spec-template.md`**

```markdown
# Spec Template

Every spec produced by `spec-craft` must contain all seven sections below.
A spec is NOT READY if any section is missing or if any acceptance criterion
is non-testable (i.e., cannot be verified by a test or a deterministic check).

---

## Context
_What problem are we solving and why now? Max 3 sentences._

## Scope
_What is explicitly in scope and out of scope for this change._

## Interfaces
_API contracts, ISO message types, downstream services touched.
List each interface as: name | direction (in/out) | format | owner._

## Data
_Data structures, field definitions, persistence requirements.
Reference ISO field numbers where applicable._

## Acceptance Criteria
_Numbered list. Each criterion must be independently testable._
_Format: AC-N: [Given/When/Then or assertion statement]_

## Non-Negotiables
_Constraints that cannot be traded off: compliance, security, SLA._

## Risks
_Known risks and mitigations. At minimum address: data integrity, downstream impact._
```

- [ ] **Step 4: Write `workbench/rules/payments-guardrails.md`**

```markdown
# Payments Guardrails

## PAN Handling
- PAN must never appear in logs, console output, journey files, or PR descriptions
- Use `secret_scan.py:scan_for_pan()` before any write operation on data that may contain PAN
- Mask format: first 6 + last 4 digits visible, remainder as `*`

## ISO Field Constraints
- Field 2 (PAN): always masked
- Field 35 (Track 2): always redacted entirely
- Field 45 (Track 1): always redacted entirely
- Field 52 (PIN block): always redacted entirely
- All other fields: log only field number and length, not value, in audit contexts

## Authorization Flow
- Authorization requests must follow the spec's sequence diagram exactly
- Any deviation from the sequence is a Failure Mode 1 (spec drift) finding
- Holds and partial authorizations must be handled explicitly — no silent fallthrough

## Downstream Contracts
- Any change to a downstream API contract must be flagged as Failure Mode 4
- Contract changes require explicit sign-off in the PR description
```

- [ ] **Step 5: Write `workbench/references/failure-modes.md`**

```markdown
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
```

- [ ] **Step 6: Write `workbench/references/payments-checklist.md`**

```markdown
# Payments Red-Team Review Checklist

Used by `red-team-review` skill and `pr-reviewer` subagent.

## PAN and Sensitive Data
- [ ] No PAN in logs, outputs, or journey files
- [ ] Track 1/2 data not persisted or logged
- [ ] PIN block never logged or transmitted unencrypted

## Authorization
- [ ] Authorization sequence matches spec exactly
- [ ] Partial auth handled explicitly
- [ ] Decline path returns correct ISO response code
- [ ] Timeout path does not silently approve

## Contracts
- [ ] No undocumented breaking changes to downstream APIs
- [ ] ISO field types match the field map
- [ ] Mandatory ISO fields are present in all message paths

## Audit
- [ ] Every gate decision is journaled
- [ ] Override reasons are recorded
- [ ] Journey file is append-only

## General Security
- [ ] No credentials in code or config
- [ ] No hardcoded URLs pointing to production
- [ ] No debug flags left enabled
```

- [ ] **Step 7: Write `workbench/references/pan-patterns.txt`**

```
# PAN detection patterns (Python regex, one per line, comments with #)
# Luhn-checkable 13-19 digit sequences
\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b
# Generic 16-digit with optional separators (catch-all)
\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b
# Track 2 equivalent data
;[0-9]{13,19}=[0-9]{4}[0-9]*\?
```

- [ ] **Step 8: Write `workbench/references/iso-field-map.yaml`**

```yaml
# ISO 8583 field reference (subset — payments-critical fields)
fields:
  2:  { name: PAN,            type: LLVAR, max: 19, sensitive: true }
  3:  { name: ProcessingCode, type: N,     len: 6,  sensitive: false }
  4:  { name: Amount,         type: N,     len: 12, sensitive: false }
  7:  { name: TransmissionDateTime, type: N, len: 10, sensitive: false }
  11: { name: STAN,           type: N,     len: 6,  sensitive: false }
  12: { name: LocalTime,      type: N,     len: 6,  sensitive: false }
  13: { name: LocalDate,      type: N,     len: 4,  sensitive: false }
  22: { name: POSEntryMode,   type: N,     len: 3,  sensitive: false }
  35: { name: Track2Data,     type: LLVAR, max: 37, sensitive: true }
  37: { name: RRN,            type: AN,    len: 12, sensitive: false }
  38: { name: AuthCode,       type: AN,    len: 6,  sensitive: false }
  39: { name: ResponseCode,   type: AN,    len: 2,  sensitive: false }
  41: { name: TerminalID,     type: ANS,   len: 8,  sensitive: false }
  42: { name: MerchantID,     type: ANS,   len: 15, sensitive: false }
  45: { name: Track1Data,     type: LLVAR, max: 76, sensitive: true }
  49: { name: Currency,       type: N,     len: 3,  sensitive: false }
  52: { name: PINBlock,       type: B,     len: 8,  sensitive: true }
  55: { name: EMVData,        type: LLLVAR,max: 255,sensitive: false }
```

- [ ] **Step 9: Write `workbench/references/risk-weight-table.yaml`**

```yaml
# Release risk scoring weights (used by release-risk-scorer)
# Total score >= threshold triggers a block
threshold: 70
factors:
  pan_path_change:      { weight: 30, description: "Change touches PAN handling code" }
  auth_flow_change:     { weight: 25, description: "Change alters authorization sequence" }
  contract_change:      { weight: 20, description: "Downstream API contract modified" }
  hold_logic_change:    { weight: 15, description: "Holds or partial auth logic modified" }
  new_iso_field:        { weight: 10, description: "New ISO field added or removed" }
  no_tests:             { weight: 25, description: "Changed files have no test coverage" }
  no_spec:              { weight: 20, description: "No spec linked in PR description" }
  no_validator_run:     { weight: 15, description: "code-to-spec-validator not run" }
```

- [ ] **Step 10: Write `workbench/references/spec-template-reference.md`**

```markdown
# Spec Template — Annotated Example

This is a worked example of a correctly completed spec.
`spec_check.py` uses the section headers below as the required-section list.

---

## Context
We need to add partial authorisation support to the AU acquiring gateway.
Currently, a transaction is either fully approved or fully declined.
Mastercard mandates partial auth support by Q4.

## Scope
In scope: partial auth flag in ISO field 56, response code 10, amount field update.
Out of scope: cardholder notification, statement rendering, settlement changes.

## Interfaces
| Name | Direction | Format | Owner |
|---|---|---|---|
| Acquiring gateway | out | ISO 8583 | Platform team |
| Core banking | in | ISO 8583 | Core team |

## Data
- Field 56 (Additional Data): bit 0 = partial auth supported (1) / not supported (0)
- Field 4 (Amount): updated to approved amount in partial auth response
- Response code 10: partial approval

## Acceptance Criteria
- AC-1: Given a transaction request with field 56 bit 0 = 1, when the issuer partially approves, then the response carries code 10 and field 4 equals the approved amount.
- AC-2: Given a transaction request with field 56 bit 0 = 0, when the issuer partially approves, then the response carries code 05 (decline) and field 4 is unchanged.
- AC-3: Given any transaction, when field 56 is absent, then partial auth is treated as not supported.

## Non-Negotiables
- PAN must not appear in any log entry related to partial auth processing.
- Response code 10 must only be used for partial approvals — never for full approvals.

## Risks
- Risk: Core banking may not handle field 56 — mitigation: integration test with emulator.
- Risk: Existing decline logic may suppress code 10 — mitigation: regression test suite.
```

- [ ] **Step 11: Write `workbench/scripts/lib/__init__.py`**

```python
"""Shared deterministic helpers for workbench plugin skills."""
```

- [ ] **Step 12: Write `workbench/scripts/lib/git_diff.py`**

```python
"""Git and diff helpers — extract diffs, list changed files, stage and commit."""
import subprocess
import sys


def get_diff(base: str = "HEAD", paths: list[str] | None = None) -> str:
    """Return unified diff between base and working tree."""
    cmd = ["git", "diff", base, "--"]
    if paths:
        cmd.extend(paths)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def list_changed_files(base: str = "HEAD") -> list[str]:
    """Return list of files changed since base."""
    result = subprocess.run(
        ["git", "diff", "--name-only", base, "--"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in result.stdout.splitlines() if f]


def stage_files(paths: list[str]) -> None:
    """Stage specific files for commit."""
    subprocess.run(["git", "add", "--"] + paths, check=True)


def commit(message: str) -> str:
    """Commit staged changes. Returns the new commit SHA."""
    subprocess.run(["git", "commit", "-m", message], check=True)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


if __name__ == "__main__":
    print("changed files:", list_changed_files())
    print("smoke test: OK")
```

- [ ] **Step 13: Write `workbench/scripts/lib/test_runner.py`**

```python
"""Run test commands, parse pass/fail/coverage output."""
import re
import subprocess
from dataclasses import dataclass


@dataclass
class TestResult:
    passed: int
    failed: int
    errors: int
    coverage_pct: float | None
    output: str
    returncode: int

    @property
    def success(self) -> bool:
        return self.returncode == 0 and self.failed == 0 and self.errors == 0


def run_tests(command: list[str], cwd: str | None = None) -> TestResult:
    """Run a test command and parse its output."""
    result = subprocess.run(
        command, capture_output=True, text=True, cwd=cwd
    )
    output = result.stdout + result.stderr
    passed = _parse_int(r"(\d+) passed", output)
    failed = _parse_int(r"(\d+) failed", output)
    errors = _parse_int(r"(\d+) error", output)
    coverage = _parse_float(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
    return TestResult(
        passed=passed, failed=failed, errors=errors,
        coverage_pct=coverage, output=output, returncode=result.returncode,
    )


def _parse_int(pattern: str, text: str) -> int:
    m = re.search(pattern, text)
    return int(m.group(1)) if m else 0


def _parse_float(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


if __name__ == "__main__":
    r = run_tests(["python3", "-m", "pytest", "--version"])
    print("smoke test returncode:", r.returncode, "OK")
```

- [ ] **Step 14: Write `workbench/scripts/lib/coverage.py`**

```python
"""Coverage delta math, threshold checks, AC-to-test-file mapping."""
import json
import re
from pathlib import Path


def check_threshold(coverage_pct: float | None, threshold: float = 80.0) -> bool:
    """Return True if coverage meets or exceeds threshold."""
    if coverage_pct is None:
        return False
    return coverage_pct >= threshold


def coverage_delta(before: float | None, after: float | None) -> float:
    """Return coverage change (after - before). None treated as 0."""
    return (after or 0.0) - (before or 0.0)


def map_acs_to_tests(spec_path: str, test_dir: str) -> dict[str, list[str]]:
    """
    Return a mapping of AC-N identifiers to test files that reference them.
    Looks for 'AC-N' string literals in test files.
    """
    spec = Path(spec_path).read_text()
    ac_ids = re.findall(r"(AC-\d+)", spec)
    mapping: dict[str, list[str]] = {ac: [] for ac in ac_ids}
    for test_file in Path(test_dir).rglob("test_*.py"):
        content = test_file.read_text()
        for ac in ac_ids:
            if ac in content:
                mapping[ac].append(str(test_file))
    return mapping


def find_uncovered_acs(mapping: dict[str, list[str]]) -> list[str]:
    """Return AC IDs with no test files."""
    return [ac for ac, files in mapping.items() if not files]


if __name__ == "__main__":
    print("threshold 80%:", check_threshold(85.0))
    print("threshold 80%:", check_threshold(79.9))
    print("smoke test: OK")
```

- [ ] **Step 15: Write `workbench/scripts/lib/pr.py`**

```python
"""GitHub PR and check-run management via gh CLI."""
import json
import subprocess


def create_pr(title: str, body: str, base: str = "main", draft: bool = False) -> str:
    """Create a PR and return its URL."""
    cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
    if draft:
        cmd.append("--draft")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def add_pr_comment(pr_number: int, body: str) -> None:
    """Add a comment to an existing PR."""
    subprocess.run(
        ["gh", "pr", "comment", str(pr_number), "--body", body], check=True
    )


def get_pr_number(branch: str) -> int | None:
    """Return PR number for the given branch, or None if not found."""
    result = subprocess.run(
        ["gh", "pr", "view", branch, "--json", "number"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout).get("number")


def build_pr_body(spec_path: str, issue_number: int, validator_notes: str,
                  reviewer_notes: str, gate_results: str) -> str:
    """Assemble the standard PR body used by work-orchestrator."""
    return f"""## Spec
See issue #{issue_number} — spec: `{spec_path}`

## Code-to-Spec Validation
{validator_notes}

## PR Review
{reviewer_notes}

## Quality Gates
{gate_results}
"""


if __name__ == "__main__":
    print("pr.py loaded — smoke test: OK")
```

- [ ] **Step 16: Write `workbench/scripts/lib/spec_check.py`**

```python
"""Template conformance checks, required-section presence, AC testability linter."""
import json
import re
from pathlib import Path

REQUIRED_SECTIONS = [
    "## Context",
    "## Scope",
    "## Interfaces",
    "## Data",
    "## Acceptance Criteria",
    "## Non-Negotiables",
    "## Risks",
]


def check_sections(spec_text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in spec_text]


def extract_acs(spec_text: str) -> list[tuple[str, str]]:
    """Return list of (AC-ID, text) tuples from the spec."""
    return re.findall(r"(AC-\d+):\s*(.+)", spec_text)


def check_ac_testability(ac_text: str) -> bool:
    """
    Return True if the AC is testable (contains Given/When/Then or an assertion verb).
    A heuristic check — the model judges completeness; this catches obvious failures.
    """
    keywords = ["given", "when", "then", "must", "shall", "returns", "produces", "equals"]
    return any(k in ac_text.lower() for k in keywords)


def validate_spec(spec_path: str) -> dict:
    """
    Run all structural checks on a spec file.
    Returns: { "valid": bool, "missing_sections": [...], "non_testable_acs": [...] }
    """
    text = Path(spec_path).read_text()
    missing = check_sections(text)
    acs = extract_acs(text)
    non_testable = [ac_id for ac_id, ac_text in acs if not check_ac_testability(ac_text)]
    valid = not missing and not non_testable
    return {"valid": valid, "missing_sections": missing, "non_testable_acs": non_testable}


def write_status(spec_path: str, result: dict) -> str:
    """Write spec.status.json next to the spec file. Returns the status file path."""
    status_path = spec_path.replace(".md", ".status.json")
    Path(status_path).write_text(json.dumps(result, indent=2))
    return status_path


if __name__ == "__main__":
    import tempfile, os
    sample = "\n".join(REQUIRED_SECTIONS) + "\nAC-1: Given X when Y then Z"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(sample)
        tmp = f.name
    result = validate_spec(tmp)
    os.unlink(tmp)
    assert result["valid"], result
    print("smoke test: OK", result)
```

- [ ] **Step 17: Write `workbench/scripts/lib/secret_scan.py`**

```python
"""PAN pattern detection and secret pattern matching."""
import re
from pathlib import Path

# Load patterns from references/pan-patterns.txt at import time (relative to lib/)
_PATTERN_FILE = Path(__file__).parent.parent.parent / "references" / "pan-patterns.txt"

def _load_patterns() -> list[re.Pattern]:
    if not _PATTERN_FILE.exists():
        return []
    patterns = []
    for line in _PATTERN_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            try:
                patterns.append(re.compile(line))
            except re.error:
                pass
    return patterns

_PATTERNS = _load_patterns()

# Common secret patterns (API keys, tokens, passwords)
_SECRET_PATTERNS = [
    re.compile(r'(?i)(password|passwd|secret|api_key|apikey|token|auth)\s*[=:]\s*["\']?\S{8,}'),
    re.compile(r'(?i)bearer\s+[A-Za-z0-9\-._~+/]{20,}'),
]


def scan_for_pan(text: str) -> list[str]:
    """Return list of PAN-like matches found in text."""
    matches = []
    for pattern in _PATTERNS:
        matches.extend(pattern.findall(text))
    return matches


def scan_for_secrets(text: str) -> list[str]:
    """Return list of secret-like matches found in text."""
    matches = []
    for pattern in _SECRET_PATTERNS:
        matches.extend(m.group(0) for m in pattern.finditer(text))
    return matches


def scan_file(path: str) -> dict:
    """Scan a file for PAN and secrets. Returns {"pan": [...], "secrets": [...]}."""
    text = Path(path).read_text(errors="replace")
    return {"pan": scan_for_pan(text), "secrets": scan_for_secrets(text)}


def scan_diff(diff_text: str) -> dict:
    """Scan a unified diff for PAN and secrets in added lines (+)."""
    added = "\n".join(
        line[1:] for line in diff_text.splitlines() if line.startswith("+") and not line.startswith("+++")
    )
    return {"pan": scan_for_pan(added), "secrets": scan_for_secrets(added)}


if __name__ == "__main__":
    result = scan_for_pan("Card: 4111111111111111")
    print("PAN found:", bool(result), "smoke test: OK")
```

- [ ] **Step 18: Write `workbench/scripts/lib/issue.py`**

```python
"""Write/read issues.json, open/close GitHub Issues via gh CLI."""
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Issue:
    number: int
    title: str
    body: str
    acs: list[str]
    status: str = "open"
    github_number: int | None = None
    branch: str | None = None


def load_issues(path: str = "issues.json") -> list[Issue]:
    """Load issues from JSON file."""
    data = json.loads(Path(path).read_text())
    return [Issue(**i) for i in data]


def save_issues(issues: list[Issue], path: str = "issues.json") -> None:
    """Save issues to JSON file."""
    Path(path).write_text(json.dumps([asdict(i) for i in issues], indent=2))


def open_github_issue(title: str, body: str, labels: list[str] | None = None) -> int:
    """Create a GitHub Issue and return its number."""
    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    if labels:
        for label in labels:
            cmd += ["--label", label]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # gh returns the issue URL; extract the number
    url = result.stdout.strip()
    return int(url.rstrip("/").split("/")[-1])


def close_github_issue(issue_number: int, comment: str | None = None) -> None:
    """Close a GitHub Issue, optionally adding a closing comment."""
    if comment:
        subprocess.run(
            ["gh", "issue", "comment", str(issue_number), "--body", comment], check=True
        )
    subprocess.run(["gh", "issue", "close", str(issue_number)], check=True)


if __name__ == "__main__":
    issues = [Issue(number=1, title="Test", body="Body", acs=["AC-1"])]
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name
    save_issues(issues, tmp)
    loaded = load_issues(tmp)
    os.unlink(tmp)
    assert loaded[0].title == "Test"
    print("smoke test: OK")
```

- [ ] **Step 19: Smoke-test each lib module**

```bash
cd /Users/rob/projects/arula-mc-labs-plugin
python3 workbench/scripts/lib/git_diff.py
python3 workbench/scripts/lib/test_runner.py
python3 workbench/scripts/lib/coverage.py
python3 workbench/scripts/lib/pr.py
python3 workbench/scripts/lib/spec_check.py
python3 workbench/scripts/lib/secret_scan.py
python3 workbench/scripts/lib/issue.py
```

Expected: each prints `smoke test: OK`.

- [ ] **Step 20: Validate plugin still passes**

```bash
claude plugin validate ./workbench
```

- [ ] **Step 21: Commit**

```bash
git add workbench/rules/ workbench/references/ workbench/scripts/
git commit -m "feat(M2): add rules, references, and shared Python lib"
git push origin main
```

---

## Task 3: `spec-craft` skill

**Files:**
- Create: `workbench/skills/spec-craft/SKILL.md`
- Create: `workbench/skills/spec-craft/scripts/validate_spec.py`

**Interfaces:**
- Consumes: `workbench/scripts/lib/spec_check.py:validate_spec()`, `workbench/scripts/lib/spec_check.py:write_status()`
- Produces: `SKILL.md` triggerable by `/spec`; `validate_spec.py` callable as `python3 validate_spec.py <spec_path>`

- [ ] **Step 1: Write `workbench/skills/spec-craft/SKILL.md`**

```markdown
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
```

- [ ] **Step 2: Write `workbench/skills/spec-craft/scripts/validate_spec.py`**

```python
#!/usr/bin/env python3
"""CLI entry point for spec validation. Usage: python3 validate_spec.py <spec.md>"""
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.spec_check import validate_spec, write_status


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_spec.py <spec.md>", file=sys.stderr)
        sys.exit(1)
    spec_path = sys.argv[1]
    result = validate_spec(spec_path)
    status_path = write_status(spec_path, result)
    print(json.dumps(result, indent=2))
    if not result["valid"]:
        print("\nSpec is NOT READY:", file=sys.stderr)
        for s in result["missing_sections"]:
            print(f"  Missing section: {s}", file=sys.stderr)
        for ac in result["non_testable_acs"]:
            print(f"  Non-testable AC: {ac}", file=sys.stderr)
        sys.exit(1)
    print(f"\nSpec is READY. Status written to {status_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Test validate_spec.py with a valid spec**

Create a temp spec file and verify it passes:

```bash
cat > /tmp/test_spec.md << 'EOF'
## Context
Test context.

## Scope
In scope: X. Out of scope: Y.

## Interfaces
| Name | Direction | Format | Owner |
|---|---|---|---|
| API | out | REST | Team |

## Data
Field A: string.

## Acceptance Criteria
AC-1: Given X when Y then Z.
AC-2: Given A when B then C must equal D.

## Non-Negotiables
No PAN in logs.

## Risks
Risk: none identified.
EOF

python3 workbench/skills/spec-craft/scripts/validate_spec.py /tmp/test_spec.md
```

Expected: `"valid": true`, exit 0.

- [ ] **Step 4: Test validate_spec.py with a missing section**

```bash
cat > /tmp/bad_spec.md << 'EOF'
## Context
Test context.

## Scope
In scope: X.
EOF

python3 workbench/skills/spec-craft/scripts/validate_spec.py /tmp/bad_spec.md
echo "Exit code: $?"
```

Expected: exit 1, lists missing sections.

- [ ] **Step 5: Test with non-testable AC**

```bash
cat > /tmp/untestable_spec.md << 'EOF'
## Context
C.
## Scope
S.
## Interfaces
I.
## Data
D.
## Acceptance Criteria
AC-1: The system should be good.
## Non-Negotiables
N.
## Risks
R.
EOF

python3 workbench/skills/spec-craft/scripts/validate_spec.py /tmp/untestable_spec.md
echo "Exit code: $?"
```

Expected: exit 1, `non_testable_acs: ["AC-1"]`.

- [ ] **Step 6: Validate plugin**

```bash
claude plugin validate ./workbench
```

- [ ] **Step 7: Commit**

```bash
git add workbench/skills/spec-craft/
git commit -m "feat(M3): add spec-craft skill and validate_spec.py"
git push origin main
```

---

## Task 4: `sdet-architect` skill

**Files:**
- Create: `workbench/skills/sdet-architect/SKILL.md`
- Create: `workbench/skills/sdet-architect/scripts/coverage_map.py`
- Create: `workbench/skills/sdet-architect/scripts/test_discovery.py`

**Interfaces:**
- Consumes: `workbench/scripts/lib/coverage.py:map_acs_to_tests()`, `workbench/scripts/lib/coverage.py:find_uncovered_acs()`
- Produces: `SKILL.md` triggerable by `/test-strategy` and `/build-tests`; scripts callable as `python3 coverage_map.py <spec.md> <test_dir>` and `python3 test_discovery.py <changed_files...>`

- [ ] **Step 1: Write `workbench/skills/sdet-architect/SKILL.md`**

```markdown
---
name: sdet-architect
description: "Use this skill when the user invokes /test-strategy or /build-tests, or asks to create a test plan, generate tests, define testing architecture, check coverage, or find tests broken by a change."
---

# sdet-architect

## Purpose
Define the testing strategy for a spec and build the tests.
Follows TDD: failing tests are written before implementation.

## Inputs
- A validated spec (`spec.md` + `spec.status.json` with `"valid": true`)
- The repo's stack and existing test setup (discovered automatically)

## Steps

### /test-strategy
1. Propose test architecture: unit / contract / integration / emulator boundaries.
   Name coverage targets (default: 80%) and what runs locally vs in CI.
2. Map every AC from the spec to a test description.
3. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/sdet-architect/scripts/coverage_map.py spec.md <test_dir>`
   to verify mapping. List any ACs with no test file.
4. Present the test plan and stop for human approval.

### /build-tests
1. Generate the failing tests for each AC (TDD-first).
   Tests must reference their AC-ID in a comment: `# AC-1`.
2. Run the tests to confirm they fail (red).
3. Commit the failing tests.

### test-maintainer mode (called by work-orchestrator)
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/sdet-architect/scripts/test_discovery.py <changed_files>`
   to find tests broken by a change.
2. Propose minimal fixes. Flag ACs with no coverage.

## Python load-bearing
- `coverage_map.py`: maps ACs to test files, reports uncovered ACs.
- `test_discovery.py`: finds tests that import or reference changed files.

## Outputs
- Test plan document (printed to stdout)
- Generated test files (written to `tests/`)
- Coverage baseline (printed by `coverage_map.py`)

## Acceptance criteria
- Every AC in the spec maps to at least one test.
- The test architecture names the emulator and contract boundaries.
- Generated tests fail before implementation (confirmed by running them).
```

- [ ] **Step 2: Write `workbench/skills/sdet-architect/scripts/coverage_map.py`**

```python
#!/usr/bin/env python3
"""Map ACs from a spec to test files. Usage: python3 coverage_map.py <spec.md> <test_dir>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.coverage import map_acs_to_tests, find_uncovered_acs


def main():
    if len(sys.argv) < 3:
        print("Usage: coverage_map.py <spec.md> <test_dir>", file=sys.stderr)
        sys.exit(1)
    spec_path, test_dir = sys.argv[1], sys.argv[2]
    mapping = map_acs_to_tests(spec_path, test_dir)
    uncovered = find_uncovered_acs(mapping)
    print(json.dumps({"mapping": mapping, "uncovered": uncovered}, indent=2))
    if uncovered:
        print(f"\nWARNING: {len(uncovered)} AC(s) have no test coverage: {uncovered}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write `workbench/skills/sdet-architect/scripts/test_discovery.py`**

```python
#!/usr/bin/env python3
"""Find tests that reference changed files. Usage: python3 test_discovery.py <file1> [file2...]"""
import re
import sys
from pathlib import Path


def find_tests_for_files(changed_files: list[str], test_root: str = "tests") -> dict[str, list[str]]:
    """Return mapping of changed_file -> list of test files that import or reference it."""
    result: dict[str, list[str]] = {f: [] for f in changed_files}
    for test_file in Path(test_root).rglob("test_*.py"):
        content = test_file.read_text(errors="replace")
        for cf in changed_files:
            module = Path(cf).stem
            if module in content or Path(cf).name in content:
                result[cf].append(str(test_file))
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: test_discovery.py <changed_file1> [changed_file2...]", file=sys.stderr)
        sys.exit(1)
    changed = sys.argv[1:]
    import json
    mapping = find_tests_for_files(changed)
    print(json.dumps(mapping, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Test coverage_map.py**

```bash
mkdir -p /tmp/test_sdet/tests
cat > /tmp/test_sdet/spec.md << 'EOF'
## Acceptance Criteria
AC-1: Given X when Y then Z.
AC-2: Given A when B then C.
EOF

cat > /tmp/test_sdet/tests/test_feature.py << 'EOF'
# AC-1
def test_something():
    pass
EOF

python3 workbench/skills/sdet-architect/scripts/coverage_map.py \
  /tmp/test_sdet/spec.md /tmp/test_sdet/tests
```

Expected: AC-1 mapped, AC-2 uncovered, exit 1 with warning.

- [ ] **Step 5: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/skills/sdet-architect/
git commit -m "feat(M4): add sdet-architect skill and coverage/discovery scripts"
git push origin main
```

---

## Task 5: Subagents

**Files:**
- Create: `workbench/agents/planner.md`
- Create: `workbench/agents/code-to-spec-validator.md`
- Create: `workbench/agents/pr-reviewer.md`
- Create: `workbench/agents/clean-room-judge.md`

**Interfaces:**
- Produces: four agent `.md` files with YAML frontmatter (`name`, `description`, `model`, `tools`)

- [ ] **Step 1: Write `workbench/agents/planner.md`**

```markdown
---
name: planner
description: "Use this agent when work-orchestrator needs to break a validated spec into an ordered list of implementation issues. Input: spec.md content. Output: structured JSON issue list."
model: sonnet
tools: ["Read", "Bash"]
---

You are a technical planner specialising in breaking payment system specs into
small, ordered, independently-implementable issues.

You will receive the full content of a validated spec. Your job is to output
a JSON array of issues — nothing else.

Rules:
- Each issue must be independently implementable and testable.
- Issues must be ordered: each issue can assume all previous issues are complete.
- Each issue must include its own acceptance criteria (subset of the spec ACs).
- Do not combine unrelated changes into one issue.
- Maximum 8 issues per spec. If more are needed, flag it.

Output format (JSON only, no prose):
```json
[
  {
    "number": 1,
    "title": "Short imperative title",
    "body": "What to implement and why. Reference spec ACs by ID.",
    "acs": ["AC-1", "AC-2"],
    "branch": "issue/1-short-slug"
  }
]
```
```

- [ ] **Step 2: Write `workbench/agents/code-to-spec-validator.md`**

```markdown
---
name: code-to-spec-validator
description: "Use this agent to validate a code diff against its spec and issue. Runs with clean context — never sees the building session. Input: spec content + issue + diff. Output: PASS or FAIL with reasons."
model: sonnet
tools: ["Read"]
---

You are a skeptical code-to-spec validator for a payments system.

You will receive:
1. The full spec content
2. The issue being implemented (title, body, ACs)
3. The unified diff of the change

You have NOT written this code. You are NOT the author. Your job is to find
problems, not to defend the implementation.

Score the diff against these five failure modes (defined in full in
`references/failure-modes.md` — read it before proceeding):

1. Spec Drift — implementation diverges from what the spec says
2. Missing Acceptance Criterion — an AC has no corresponding code path or test
3. Unsafe Data Handling — PAN or sensitive fields handled insecurely
4. Broken Contract — downstream API contract or ISO boundary violated
5. Missing Human Gate — a gate step ran without approval or override recording

Output format:
```
VERDICT: PASS | FAIL

FAILURE MODES FOUND:
- [FM-N] Description of finding (line reference if possible)

NOTES:
- Any warnings or observations that are not blockers
```

If all five failure modes are clear: VERDICT: PASS.
If any failure mode is triggered: VERDICT: FAIL. Do not soften findings.
```

- [ ] **Step 3: Write `workbench/agents/pr-reviewer.md`**

```markdown
---
name: pr-reviewer
description: "Use this agent to review a pull request diff against coding standards. Runs with clean context — never sees the building session. Input: diff + coding standards. Output: review comments."
model: sonnet
tools: ["Read"]
---

You are a skeptical pull request reviewer for a payments system.

You will receive:
1. The unified diff of the change
2. The content of `rules/coding-standards.md`

You have NOT written this code. You are NOT the author. You must not soften
your findings. Your job is to find problems that a human reviewer would catch.

Review for:
- Violations of coding-standards.md (naming, structure, length, docstrings)
- Missing or inadequate tests
- Logic errors visible in the diff
- Security issues (secrets, PAN handling, unsafe patterns)
- Dead code, unused imports, commented-out code

Output format:
```
REVIEW SUMMARY: APPROVE | REQUEST CHANGES | BLOCKER

FINDINGS:
- [BLOCKER|WARNING|NITPICK] file:line — description

If BLOCKER: do not approve. The developer must fix before PR creation.
If only WARNINGs/NITPICKs: flag them but do not block.
```

Do not write "looks good overall" or soften findings with qualifiers.
If you find a blocker, say BLOCKER clearly.
```

- [ ] **Step 4: Write `workbench/agents/clean-room-judge.md`**

```markdown
---
name: clean-room-judge
description: "Use this agent for any fresh-context scoring or judgment task that must be independent of the session that produced the artifact. Input: artifact + rubric or criteria. Output: structured judgment."
model: sonnet
tools: ["Read"]
---

You are a clean-room judge. You have no context from any prior session.

You will receive an artifact (journey file, spec, diff, or other output) and
a set of criteria or a rubric. Score the artifact objectively against the criteria.

Rules:
- You did not produce this artifact. Judge it as an independent reviewer.
- Do not infer intent — score only what is observable in the artifact.
- If a criterion is ambiguous, note the ambiguity and score conservatively.
- Return structured output only — no preamble, no prose outside the output format.

Output format (adapt field names to the rubric provided):
```json
{
  "score": 0-100,
  "criteria": [
    { "id": "criterion-id", "met": true|false, "evidence": "quote or observation" }
  ],
  "notes": "Any ambiguities or edge cases"
}
```
```

- [ ] **Step 5: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/agents/
git commit -m "feat(M5): add planner, code-to-spec-validator, pr-reviewer, clean-room-judge agents"
git push origin main
```

---

## Task 6: `work-orchestrator` skill + `quality_gates.py`

**Files:**
- Create: `workbench/skills/work-orchestrator/SKILL.md`
- Create: `workbench/skills/work-orchestrator/scripts/orchestrate.py`
- Create: `workbench/hooks/quality_gates.py`

**Interfaces:**
- Consumes: `lib/issue.py`, `lib/git_diff.py`, `lib/test_runner.py`, `lib/pr.py`, `lib/secret_scan.py`; agents `planner`, `code-to-spec-validator`, `pr-reviewer`
- Produces: `SKILL.md` triggerable by `/build`; `orchestrate.py` callable as `python3 orchestrate.py <spec.md>`; `quality_gates.py` callable as `python3 quality_gates.py pre-tool`

- [ ] **Step 1: Write `workbench/skills/work-orchestrator/SKILL.md`**

```markdown
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
```

- [ ] **Step 2: Write `workbench/skills/work-orchestrator/scripts/orchestrate.py`**

```python
#!/usr/bin/env python3
"""
Fallback orchestrator: runs the work-orchestrator pipeline using claude CLI
for judgment stages and Python for deterministic stages.

Usage: python3 orchestrate.py <spec.md>
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.issue import load_issues, save_issues, open_github_issue
from lib.git_diff import get_diff
from lib.test_runner import run_tests
from lib.pr import build_pr_body, create_pr
from lib.secret_scan import scan_diff


def run_claude(prompt: str) -> str:
    """Run a single claude --print invocation with the given prompt."""
    result = subprocess.run(
        ["claude", "--print", prompt],
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def run_quality_gates(hooks_dir: str) -> tuple[bool, str]:
    """Run quality_gates.py. Returns (passed, output)."""
    result = subprocess.run(
        ["python3", f"{hooks_dir}/quality_gates.py", "pre-tool"],
        capture_output=True, text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def process_issue(issue, spec_path: str, hooks_dir: str) -> dict:
    """Run the full pipeline for one issue. Returns a result dict."""
    diff = get_diff()

    # Secret scan before anything else
    scan = scan_diff(diff)
    if scan["pan"] or scan["secrets"]:
        return {"status": "BLOCKED", "reason": f"Secret/PAN found in diff: {scan}"}

    # Code-to-spec validation (fresh context via claude CLI)
    validator_prompt = (
        f"You are the code-to-spec-validator agent.\n"
        f"SPEC:\n{Path(spec_path).read_text()}\n\n"
        f"ISSUE:\n{issue.title}\n{issue.body}\nACs: {issue.acs}\n\n"
        f"DIFF:\n{diff}\n\n"
        f"Score against the five failure modes in references/failure-modes.md "
        f"and output VERDICT: PASS or FAIL."
    )
    validator_output = run_claude(validator_prompt)

    if "VERDICT: FAIL" in validator_output:
        return {"status": "VALIDATOR_FAIL", "validator": validator_output}

    # PR review (fresh context via claude CLI)
    standards = Path(hooks_dir).parent / "rules" / "coding-standards.md"
    reviewer_prompt = (
        f"You are the pr-reviewer agent.\n"
        f"CODING STANDARDS:\n{standards.read_text()}\n\n"
        f"DIFF:\n{diff}\n\n"
        f"Review and output REVIEW SUMMARY: APPROVE or REQUEST CHANGES or BLOCKER."
    )
    reviewer_output = run_claude(reviewer_prompt)

    if "BLOCKER" in reviewer_output:
        return {"status": "REVIEWER_BLOCKER", "reviewer": reviewer_output}

    # Quality gates
    gates_passed, gates_output = run_quality_gates(hooks_dir)
    if not gates_passed:
        return {"status": "GATES_FAIL", "gates": gates_output}

    return {
        "status": "READY_FOR_APPROVAL",
        "validator": validator_output,
        "reviewer": reviewer_output,
        "gates": gates_output,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: orchestrate.py <spec.md>", file=sys.stderr)
        sys.exit(1)
    spec_path = sys.argv[1]
    hooks_dir = str(Path(__file__).parent.parent.parent.parent / "hooks")

    if not Path("issues.json").exists():
        print("No issues.json found. Run the planner agent first.", file=sys.stderr)
        sys.exit(1)

    issues = load_issues("issues.json")
    for issue in issues:
        if issue.status != "open":
            continue
        print(f"\n=== Processing issue #{issue.number}: {issue.title} ===")
        result = process_issue(issue, spec_path, hooks_dir)
        print(json.dumps(result, indent=2))
        if result["status"] == "READY_FOR_APPROVAL":
            print("\n[GATE] Approve PR creation? (yes/no/override <reason>): ", end="")
            # In non-interactive mode, halt and let the developer respond
            break


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write `workbench/hooks/quality_gates.py`**

```python
#!/usr/bin/env python3
"""
Quality gates: lint, secret scan, and coverage threshold.
Returns exit code 0 on pass, nonzero on fail.
Usage: python3 quality_gates.py pre-tool
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from lib.secret_scan import scan_diff
from lib.git_diff import get_diff
from lib.test_runner import run_tests
from lib.coverage import check_threshold

COVERAGE_THRESHOLD = 80.0
RESULTS = []


def gate_secret_scan() -> bool:
    """Fail if the current diff contains PAN or secrets."""
    try:
        diff = get_diff()
    except subprocess.CalledProcessError:
        return True  # No diff available, skip
    scan = scan_diff(diff)
    if scan["pan"] or scan["secrets"]:
        RESULTS.append({"gate": "secret_scan", "passed": False,
                         "detail": f"PAN: {scan['pan']}, secrets: {scan['secrets']}"})
        return False
    RESULTS.append({"gate": "secret_scan", "passed": True})
    return True


def gate_lint() -> bool:
    """Run ruff lint if available, else skip."""
    result = subprocess.run(["which", "ruff"], capture_output=True)
    if result.returncode != 0:
        RESULTS.append({"gate": "lint", "passed": True, "detail": "ruff not found, skipped"})
        return True
    r = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
    passed = r.returncode == 0
    RESULTS.append({"gate": "lint", "passed": passed, "detail": r.stdout + r.stderr})
    return passed


def gate_coverage() -> bool:
    """Run pytest with coverage if pytest is available, else skip."""
    result = subprocess.run(["which", "pytest"], capture_output=True)
    if result.returncode != 0:
        RESULTS.append({"gate": "coverage", "passed": True, "detail": "pytest not found, skipped"})
        return True
    r = run_tests(["pytest", "--tb=no", "-q", "--cov=.", "--cov-report=term-missing"])
    passed = check_threshold(r.coverage_pct, COVERAGE_THRESHOLD)
    RESULTS.append({
        "gate": "coverage", "passed": passed,
        "detail": f"coverage={r.coverage_pct}% threshold={COVERAGE_THRESHOLD}%"
    })
    return passed


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "pre-tool"
    all_passed = True
    all_passed &= gate_secret_scan()
    all_passed &= gate_lint()
    if mode != "pre-tool":  # coverage only runs on full gate, not pre-tool
        all_passed &= gate_coverage()
    print(json.dumps({"mode": mode, "passed": all_passed, "gates": RESULTS}, indent=2))
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Test quality_gates.py**

```bash
python3 workbench/hooks/quality_gates.py pre-tool
echo "Exit code: $?"
```

Expected: exit 0 (no diff with PAN/secrets in clean repo), JSON output with gates.

- [ ] **Step 5: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/skills/work-orchestrator/ workbench/hooks/quality_gates.py
git commit -m "feat(M6): add work-orchestrator skill, orchestrate.py fallback, quality_gates.py"
git push origin main
```

---

## Task 7: Hooks wiring

**Files:**
- Create: `workbench/hooks/hooks.json`
- Create: `workbench/hooks/journey_record.py`

**Interfaces:**
- Produces: `hooks.json` loaded by Claude Code on session start; `journey_record.py` callable as `python3 journey_record.py <event>`

- [ ] **Step 1: Write `workbench/hooks/hooks.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py session-start",
        "timeout": 10
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py pre-tool",
        "timeout": 5
      },
      {
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/quality_gates.py pre-tool",
        "timeout": 30
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py post-tool",
        "timeout": 5
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py stop",
        "timeout": 10
      }
    ]
  }
}
```

- [ ] **Step 2: Write `workbench/hooks/journey_record.py`**

```python
#!/usr/bin/env python3
"""
Append-only journey event logger.
Usage: python3 journey_record.py <event>
Events: session-start, pre-tool, post-tool, stop
Reads CLAUDE_SESSION_ID and CLAUDE_TOOL_NAME from environment if available.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from lib.secret_scan import scan_for_pan, scan_for_secrets

JOURNEY_DIR = Path(os.environ.get("WORKBENCH_JOURNEY_DIR", "journey"))
SESSION_ID = os.environ.get("CLAUDE_SESSION_ID", f"session-{int(time.time())}")

SENSITIVE_KEYS = {"pan", "track1", "track2", "pin", "password", "secret", "token", "key"}


def redact(obj):
    """Recursively redact sensitive values from a dict/list/str."""
    if isinstance(obj, dict):
        return {k: "***REDACTED***" if k.lower() in SENSITIVE_KEYS else redact(v)
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(i) for i in obj]
    if isinstance(obj, str):
        if scan_for_pan(obj):
            return "***PAN-REDACTED***"
        if scan_for_secrets(obj):
            return "***SECRET-REDACTED***"
        return obj
    return obj


def append_event(event_type: str, data: dict) -> None:
    """Append a single event to the session journey file."""
    JOURNEY_DIR.mkdir(parents=True, exist_ok=True)
    journey_file = JOURNEY_DIR / f"{SESSION_ID}.jsonl"
    event = {
        "ts": int(time.time()),
        "event": event_type,
        "session": SESSION_ID,
        **redact(data),
    }
    with journey_file.open("a") as f:
        f.write(json.dumps(event) + "\n")


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")
    tool_input = os.environ.get("CLAUDE_TOOL_INPUT", "")

    if event == "session-start":
        append_event("session-start", {"cwd": os.getcwd()})
    elif event == "pre-tool":
        append_event("pre-tool", {"tool": tool_name, "input_preview": tool_input[:200]})
    elif event == "post-tool":
        append_event("post-tool", {"tool": tool_name})
    elif event == "stop":
        append_event("stop", {"reason": os.environ.get("CLAUDE_STOP_REASON", "")})
    else:
        append_event(event, {})


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Test journey_record.py**

```bash
mkdir -p /tmp/test_journey
WORKBENCH_JOURNEY_DIR=/tmp/test_journey \
CLAUDE_SESSION_ID=test-session-1 \
python3 workbench/hooks/journey_record.py session-start

WORKBENCH_JOURNEY_DIR=/tmp/test_journey \
CLAUDE_SESSION_ID=test-session-1 \
CLAUDE_TOOL_NAME=Read \
python3 workbench/hooks/journey_record.py pre-tool

cat /tmp/test_journey/test-session-1.jsonl
```

Expected: two JSON lines, each with `ts`, `event`, `session` fields.

- [ ] **Step 4: Test redaction**

```bash
WORKBENCH_JOURNEY_DIR=/tmp/test_journey \
CLAUDE_SESSION_ID=test-session-1 \
CLAUDE_TOOL_NAME=Read \
CLAUDE_TOOL_INPUT='{"pan": "4111111111111111"}' \
python3 workbench/hooks/journey_record.py pre-tool

grep -c "4111" /tmp/test_journey/test-session-1.jsonl
```

Expected: `0` (no PAN in the file).

- [ ] **Step 5: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/hooks/
git commit -m "feat(M7): wire hooks.json and journey_record.py"
git push origin main
```

---

## Task 8: `journey-recorder` skill

**Files:**
- Create: `workbench/skills/journey-recorder/SKILL.md`
- Create: `workbench/skills/journey-recorder/scripts/recorder.py`

**Interfaces:**
- Consumes: `journey/<session>.jsonl` written by `journey_record.py`
- Produces: `SKILL.md` triggerable by `/journey`; `recorder.py` callable as `python3 recorder.py export <session_id>`

- [ ] **Step 1: Write `workbench/skills/journey-recorder/SKILL.md`**

```markdown
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
```

- [ ] **Step 2: Write `workbench/skills/journey-recorder/scripts/recorder.py`**

```python
#!/usr/bin/env python3
"""
Export a JSONL journey file to readable markdown.
Usage: python3 recorder.py export <session_id> [journey_dir]
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def export_journey(session_id: str, journey_dir: str = "journey") -> str:
    """Convert session JSONL to markdown. Returns output file path."""
    jsonl_path = Path(journey_dir) / f"{session_id}.jsonl"
    if not jsonl_path.exists():
        print(f"Journey file not found: {jsonl_path}", file=sys.stderr)
        sys.exit(1)

    events = []
    for line in jsonl_path.read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))

    lines = [f"# Journey: {session_id}\n"]
    for event in events:
        ts = datetime.fromtimestamp(event.get("ts", 0)).strftime("%H:%M:%S")
        ev = event.get("event", "unknown")
        if ev == "session-start":
            lines.append(f"**{ts}** Session started in `{event.get('cwd', '')}`\n")
        elif ev == "pre-tool":
            lines.append(f"**{ts}** Tool: `{event.get('tool', '')}` — {event.get('input_preview', '')[:80]}\n")
        elif ev == "post-tool":
            lines.append(f"**{ts}** Tool complete: `{event.get('tool', '')}`\n")
        elif ev == "stop":
            lines.append(f"**{ts}** Session stopped — {event.get('reason', '')}\n")
        elif ev == "gate":
            lines.append(f"**{ts}** Gate: {event.get('decision', '')} — {event.get('reason', '')}\n")
        elif ev == "override":
            lines.append(f"**{ts}** OVERRIDE — reason: {event.get('reason', 'none recorded')}\n")
        else:
            lines.append(f"**{ts}** {ev}: {json.dumps({k: v for k, v in event.items() if k not in ('ts','event','session')})}\n")

    md_path = Path(journey_dir) / f"{session_id}.md"
    md_path.write_text("\n".join(lines))
    return str(md_path)


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "export":
        print("Usage: recorder.py export <session_id> [journey_dir]", file=sys.stderr)
        sys.exit(1)
    session_id = sys.argv[2]
    journey_dir = sys.argv[3] if len(sys.argv) > 3 else "journey"
    out = export_journey(session_id, journey_dir)
    print(f"Exported to: {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Test recorder.py**

```bash
mkdir -p /tmp/test_rec
cat > /tmp/test_rec/s1.jsonl << 'EOF'
{"ts": 1000000, "event": "session-start", "session": "s1", "cwd": "/projects/foo"}
{"ts": 1000010, "event": "pre-tool", "session": "s1", "tool": "Read", "input_preview": "reading spec.md"}
{"ts": 1000020, "event": "stop", "session": "s1", "reason": "completed"}
EOF

python3 workbench/skills/journey-recorder/scripts/recorder.py export s1 /tmp/test_rec
cat /tmp/test_rec/s1.md
```

Expected: readable markdown with three timestamped events.

- [ ] **Step 4: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/skills/journey-recorder/
git commit -m "feat(M8): add journey-recorder skill and recorder.py"
git push origin main
```

---

## Task 9: `lab-grader` skill

**Files:**
- Create: `workbench/skills/lab-grader/SKILL.md`
- Create: `workbench/skills/lab-grader/rubric.yaml` (starter template)
- Create: `workbench/skills/lab-grader/scripts/grader.py`

**Interfaces:**
- Consumes: `journey/<session>.jsonl`, `rubric.yaml` (per-lab, path from `lab.json`)
- Produces: `SKILL.md` triggerable by `/grade`; `grader.py` callable as `python3 grader.py <session.jsonl> <rubric.yaml>`

- [ ] **Step 1: Write `workbench/skills/lab-grader/SKILL.md`**

```markdown
---
name: lab-grader
description: "Use this skill when the user invokes /grade or asks to grade a lab, score a journey, or produce a cohort summary. Input: a journey file and a rubric. Output: per-learner grade card and cohort summary."
---

# lab-grader

## Purpose
Score a learner's lab run against a rubric and produce feedback plus a
cohort-level roll-up.

## Inputs
- Journey file path (e.g. `journey/<session>.jsonl`)
- Rubric file path (e.g. `.claude/rubrics/lab-1.yaml`) — resolved from `lab.json` if present

## Steps
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/lab-grader/scripts/grader.py <journey.jsonl> <rubric.yaml>`
   This scores all objective, measurable items from the journey log.
2. The model writes the qualitative feedback section based on the grader output.
3. Print the grade card to stdout.
4. Append the anonymized result to `cohort-summary.jsonl` if present.

## Python load-bearing
`grader.py` scores all objective items — the model only writes qualitative prose.
Grading is deterministic: same journey + same rubric → same score every run.

## Rubric convention
- The plugin ships a starter rubric at `skills/lab-grader/rubric.yaml`
- Each lab's authoritative rubric lives at `.claude/rubrics/lab-<n>.yaml`
  in the learner's project (not inside the plugin)
- `lab.json` at `.claude/lab.json` specifies which rubric to use

## Outputs
- Per-learner grade card (stdout + `journey/<session>-grade.json`)
- Anonymized entry appended to `cohort-summary.jsonl`

## Acceptance criteria
- Grading is deterministic: same journey + rubric → same score.
- Grade card lists each rubric criterion, whether it was met, and evidence from the journey.
```

- [ ] **Step 2: Write `workbench/skills/lab-grader/rubric.yaml`**

```yaml
# Starter rubric template — copy to .claude/rubrics/lab-N.yaml and customise
lab: 0
title: "Starter rubric (not a real lab)"
pass_threshold: 70  # percent of max_score needed to pass

criteria:
  - id: plugin-installed
    description: "Learner installed the workbench plugin"
    max_score: 10
    evidence: "session-start event present in journey"
    check: "event_exists:session-start"

  - id: spec-created
    description: "Learner ran /spec and produced a valid spec.status.json"
    max_score: 20
    evidence: "pre-tool event with tool=spec-craft or validate_spec.py output in journey"
    check: "event_contains:pre-tool:spec"

  - id: quality-gates-ran
    description: "Quality gates ran and passed"
    max_score: 20
    evidence: "gate event with passed=true in journey"
    check: "event_contains:gate:passed"

  - id: journey-captured
    description: "Journey file has at least 5 events"
    max_score: 10
    evidence: "journey file line count >= 5"
    check: "event_count_gte:5"

  - id: no-pan-in-journey
    description: "No PAN or secrets in the journey file"
    max_score: 40
    evidence: "secret_scan returns empty on journey file"
    check: "secret_scan_clean"
```

- [ ] **Step 3: Write `workbench/skills/lab-grader/scripts/grader.py`**

```python
#!/usr/bin/env python3
"""
Score a journey file against a rubric.
Usage: python3 grader.py <session.jsonl> <rubric.yaml>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.secret_scan import scan_for_pan, scan_for_secrets

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def load_rubric(path: str) -> dict:
    """Load rubric from YAML or JSON."""
    text = Path(path).read_text()
    if HAS_YAML:
        return yaml.safe_load(text)
    # Minimal YAML fallback: parse key: value lines only (no nesting)
    raise RuntimeError("PyYAML not installed. Install with: pip3 install pyyaml")


def load_events(jsonl_path: str) -> list[dict]:
    """Load all events from a journey JSONL file."""
    events = []
    for line in Path(jsonl_path).read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def score_criterion(criterion: dict, events: list[dict], journey_text: str) -> dict:
    """Score one rubric criterion. Returns {"id", "met", "score", "evidence"}."""
    check = criterion.get("check", "")
    max_score = criterion.get("max_score", 0)
    met = False
    evidence = "not found"

    if check.startswith("event_exists:"):
        event_type = check.split(":", 1)[1]
        matching = [e for e in events if e.get("event") == event_type]
        met = bool(matching)
        evidence = f"{len(matching)} event(s) of type '{event_type}'"

    elif check.startswith("event_contains:"):
        parts = check.split(":")
        event_type, keyword = parts[1], parts[2] if len(parts) > 2 else ""
        matching = [e for e in events
                    if e.get("event") == event_type and keyword in json.dumps(e)]
        met = bool(matching)
        evidence = f"{len(matching)} matching event(s)"

    elif check.startswith("event_count_gte:"):
        threshold = int(check.split(":", 1)[1])
        met = len(events) >= threshold
        evidence = f"{len(events)} events (threshold: {threshold})"

    elif check == "secret_scan_clean":
        pan = scan_for_pan(journey_text)
        secrets = scan_for_secrets(journey_text)
        met = not pan and not secrets
        evidence = "clean" if met else f"PAN: {pan}, secrets: {secrets}"

    return {
        "id": criterion["id"],
        "description": criterion.get("description", ""),
        "met": met,
        "score": max_score if met else 0,
        "max_score": max_score,
        "evidence": evidence,
    }


def grade(journey_path: str, rubric_path: str) -> dict:
    """Grade a journey against a rubric. Returns grade card dict."""
    events = load_events(journey_path)
    rubric = load_rubric(rubric_path)
    journey_text = Path(journey_path).read_text()

    results = []
    total_score = 0
    max_total = 0
    for criterion in rubric.get("criteria", []):
        result = score_criterion(criterion, events, journey_text)
        results.append(result)
        total_score += result["score"]
        max_total += result["max_score"]

    threshold = rubric.get("pass_threshold", 70)
    pct = (total_score / max_total * 100) if max_total else 0
    passed = pct >= threshold

    return {
        "session": Path(journey_path).stem,
        "lab": rubric.get("lab", 0),
        "score": total_score,
        "max_score": max_total,
        "percent": round(pct, 1),
        "passed": passed,
        "threshold": threshold,
        "criteria": results,
    }


def append_cohort_summary(result: dict, summary_path: str = "cohort-summary.jsonl") -> None:
    """Append an anonymized entry to the cohort summary if the file exists."""
    p = Path(summary_path)
    if not p.exists():
        return
    entry = {
        "lab": result["lab"],
        "score": result["score"],
        "max_score": result["max_score"],
        "percent": result["percent"],
        "passed": result["passed"],
        # omit session ID for anonymization
        "criteria_met": [c["id"] for c in result["criteria"] if c["met"]],
        "criteria_missed": [c["id"] for c in result["criteria"] if not c["met"]],
    }
    with p.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: grader.py <session.jsonl> <rubric.yaml>", file=sys.stderr)
        sys.exit(1)
    journey_path, rubric_path = sys.argv[1], sys.argv[2]
    result = grade(journey_path, rubric_path)

    # Write grade card
    grade_path = journey_path.replace(".jsonl", "-grade.json")
    Path(grade_path).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nGrade card written to: {grade_path}")

    # Append anonymized entry to cohort summary if present
    append_cohort_summary(result)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Test grader.py**

```bash
mkdir -p /tmp/test_grade
cat > /tmp/test_grade/s1.jsonl << 'EOF'
{"ts": 1000000, "event": "session-start", "session": "s1", "cwd": "/foo"}
{"ts": 1000010, "event": "pre-tool", "session": "s1", "tool": "Read", "input_preview": "spec"}
{"ts": 1000020, "event": "gate", "session": "s1", "passed": true}
{"ts": 1000030, "event": "pre-tool", "session": "s1", "tool": "Write", "input_preview": "x"}
{"ts": 1000040, "event": "stop", "session": "s1", "reason": "done"}
EOF

pip3 install pyyaml -q 2>/dev/null || true

python3 workbench/skills/lab-grader/scripts/grader.py \
  /tmp/test_grade/s1.jsonl \
  workbench/skills/lab-grader/rubric.yaml
```

Expected: JSON grade card with scores, `passed` field, deterministic output.

- [ ] **Step 5: Verify determinism (run twice, compare)**

```bash
python3 workbench/skills/lab-grader/scripts/grader.py \
  /tmp/test_grade/s1.jsonl workbench/skills/lab-grader/rubric.yaml > /tmp/grade1.json

python3 workbench/skills/lab-grader/scripts/grader.py \
  /tmp/test_grade/s1.jsonl workbench/skills/lab-grader/rubric.yaml > /tmp/grade2.json

diff /tmp/grade1.json /tmp/grade2.json && echo "DETERMINISTIC: OK"
```

Expected: no diff output, `DETERMINISTIC: OK`.

- [ ] **Step 6: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/skills/lab-grader/
git commit -m "feat(M9): add lab-grader skill, rubric.yaml, grader.py"
git push origin main
```

---

## Task 10: Commands (thin entry points)

**Files:**
- Create: `workbench/commands/spec.md`
- Create: `workbench/commands/test-strategy.md`
- Create: `workbench/commands/build-tests.md`
- Create: `workbench/commands/build.md`
- Create: `workbench/commands/review.md`
- Create: `workbench/commands/grade.md`
- Create: `workbench/commands/journey.md`
- Create: `workbench/commands/lab.md`

**Interfaces:**
- Produces: eight slash commands, each delegating immediately to its skill or agent

- [ ] **Step 1: Write all eight command files**

`workbench/commands/spec.md`:
```markdown
---
name: spec
description: "Create or validate a spec using the spec-craft skill. Usage: /spec <problem statement>"
---
Invoke the `spec-craft` skill to turn the user's problem statement into a validated spec.
Pass the full user input as the problem statement. Do not add steps of your own.
```

`workbench/commands/test-strategy.md`:
```markdown
---
name: test-strategy
description: "Design the test architecture for a validated spec. Usage: /test-strategy"
---
Invoke the `sdet-architect` skill in /test-strategy mode.
The spec.md and spec.status.json must exist and be valid before proceeding.
```

`workbench/commands/build-tests.md`:
```markdown
---
name: build-tests
description: "Generate failing tests (TDD) for a validated spec. Usage: /build-tests"
---
Invoke the `sdet-architect` skill in /build-tests mode.
Generate failing tests for every AC in the spec. Confirm they fail before committing.
```

`workbench/commands/build.md`:
```markdown
---
name: build
description: "Run the full development pipeline from spec to PR. Usage: /build"
---
Invoke the `work-orchestrator` skill.
The spec.md and spec.status.json must exist and be valid before proceeding.
```

`workbench/commands/review.md`:
```markdown
---
name: review
description: "Run a fresh-context PR review on the current diff. Usage: /review"
---
Spawn the `pr-reviewer` agent with the current diff and rules/coding-standards.md.
Present the review output to the developer without modification.
```

`workbench/commands/grade.md`:
```markdown
---
name: grade
description: "Grade a lab journey against a rubric. Usage: /grade <session_id>"
---
Invoke the `lab-grader` skill.
Resolve the rubric path from .claude/lab.json if present, otherwise prompt the user.
```

`workbench/commands/journey.md`:
```markdown
---
name: journey
description: "Control lab journey recording. Usage: /journey start|stop|export [session_id]"
---
Invoke the `journey-recorder` skill with the given subcommand.
For `start`: print the session ID. For `export`: run recorder.py and print the output path.
```

`workbench/commands/lab.md`:
```markdown
---
name: lab
description: "Start a lab session. Usage: /lab [lab_number]"
---
1. Read .claude/lab.json to determine the lab number, title, and rubric path.
2. If lab.json does not exist, prompt the user for the lab number and create a starter lab.json.
3. Start journey recording with /journey start.
4. Print the lab objectives from the rubric so the learner knows what to achieve.
```

- [ ] **Step 2: Create starter lab.json template**

Write `workbench/docs/lab.json.example` — this is the schema reference the `/lab` command and `lab.md` document for learners:

```json
{
  "lab": 1,
  "title": "Foundations and governance",
  "rubric": ".claude/rubrics/lab-1.yaml",
  "journey_session": "lab-1-learner-id",
  "objectives": ["plugin-installed", "spec-created", "quality-gates-ran", "journey-captured", "no-pan-in-journey"]
}
```

Fields:
- `lab`: integer 1–4
- `title`: human-readable lab name
- `rubric`: path to per-lab rubric (relative to project root)
- `journey_session`: session ID passed to `journey-recorder`; customise with learner's name/ID
- `objectives`: list of criterion IDs from the rubric that this lab targets

- [ ] **Step 3: Validate all commands load**

```bash
claude plugin validate ./workbench
```

Expected: no errors. All eight commands should appear in the component inventory.

- [ ] **Step 4: Test lab.json schema is parseable**

```bash
python3 -c "
import json
data = json.loads(open('workbench/docs/lab.json.example').read())
assert all(k in data for k in ['lab','title','rubric','journey_session','objectives']), 'Missing key'
print('lab.json schema: OK')
"
```

- [ ] **Step 5: Commit**

```bash
git add workbench/commands/ workbench/docs/lab.json.example
git commit -m "feat(M10): add all eight slash commands and lab.json schema example"
git push origin main
```

---

## Task 11: CI skill stubs (`red-team-review`, `test-maintainer`, `release-risk-scorer`)

**Files:**
- Create: `workbench/skills/red-team-review/SKILL.md`
- Create: `workbench/skills/test-maintainer/SKILL.md`
- Create: `workbench/skills/release-risk-scorer/SKILL.md`

**Interfaces:**
- Produces: three documented SKILL.md stubs; no scripts yet (Lab 4 cohort implements them)

- [ ] **Step 1: Write `workbench/skills/red-team-review/SKILL.md`**

```markdown
---
name: red-team-review
description: "Use this skill for scheduled or on-demand deep security and payments red-team review of a repo. Posts findings as GitHub issues. LAB 4 STUB — scripts/red_team.py not yet implemented."
---

# red-team-review (Lab 4 stub)

## Purpose
Scheduled and on-demand deep security and payments red-team review of a
repository. Posts findings as GitHub issues/comments. Runs agentically in
CI (GitHub Actions) without interactive input.

## Inputs
- Repository path (defaults to current directory)
- Scope: `full | changed-only` (default: `changed-only`)
- GitHub issue label to apply to findings (default: `red-team`)

## Steps
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/red-team-review/scripts/red_team.py <scope>`
   _(Lab 4: implement this script)_
2. The script uses `references/payments-checklist.md` and `references/pan-patterns.txt`
   to scan the repo for security and payments issues.
3. For each finding above the severity threshold, open a GitHub Issue via `issue.py`.
4. Post a summary comment on the triggering PR (if run in PR context).

## Python load-bearing (Lab 4)
`scripts/red_team.py` — implement using `lib/git_diff.py`, `lib/secret_scan.py`,
and the payments checklist. The model reviews findings and writes GitHub Issue bodies.

## Outputs
- GitHub Issues per finding (severity: HIGH or CRITICAL)
- Summary comment on triggering PR

## Acceptance criteria (Lab 4)
- Finds a deliberately seeded PAN in a changed file and opens a GitHub Issue.
- Finds a deliberately seeded secret (API key pattern) and opens a GitHub Issue.
- Runs to completion without interactive input in a GitHub Actions workflow.

## Extension point
Add `scripts/red_team.py` following the pattern in `docs/EXTENDING.md`.
Import from `scripts/lib/` — do not duplicate detection logic.
```

- [ ] **Step 2: Write `workbench/skills/test-maintainer/SKILL.md`**

```markdown
---
name: test-maintainer
description: "Use this skill on every PR to find tests broken by the change, propose minimal fixes, and flag missing coverage. LAB 4 STUB — scripts/maintainer.py not yet implemented."
---

# test-maintainer (Lab 4 stub)

## Purpose
On every pull request, find tests broken by the change, propose minimal fixes
in a follow-up PR, and flag ACs with no test coverage. Runs agentically in CI.

## Inputs
- Base branch (default: `main`)
- Test directory (default: `tests/`)
- Spec path (default: `spec.md`)

## Steps
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/test-maintainer/scripts/maintainer.py <base> <test_dir>`
   _(Lab 4: implement this script)_
2. The script uses `lib/git_diff.py` to get the diff and `lib/test_runner.py`
   to find broken tests.
3. It uses `sdet-architect/scripts/test_discovery.py` to map changed files
   to their test files.
4. For each broken test, the model proposes a minimal fix.
5. Proposed fixes are opened as a follow-up PR (draft).
6. Missing ACs (no test coverage) are posted as PR comments.

## Python load-bearing (Lab 4)
`scripts/maintainer.py` — implement using `lib/git_diff.py`, `lib/test_runner.py`,
`lib/coverage.py`, and `skills/sdet-architect/scripts/test_discovery.py`.

## Outputs
- Draft follow-up PR with proposed test fixes
- PR comment listing ACs with no test coverage

## Acceptance criteria (Lab 4)
- Given a changed file that breaks a test, identifies the broken test.
- Given a spec with an AC not covered by any test, flags it in a PR comment.
- Opens a draft follow-up PR with the proposed fix.

## Extension point
Add `scripts/maintainer.py` following the pattern in `docs/EXTENDING.md`.
```

- [ ] **Step 3: Write `workbench/skills/release-risk-scorer/SKILL.md`**

```markdown
---
name: release-risk-scorer
description: "Use this skill on PRs to a release branch to score payment-grade release risk and block high-risk PRs as a required check. LAB 4 STUB — scripts/risk_scorer.py not yet implemented."
---

# release-risk-scorer (Lab 4 stub)

## Purpose
On pull requests to a release branch, score payment-grade release risk
(authorization, holds, PAN paths, downstream contracts). Block PRs above
the configurable threshold as a required GitHub check.

## Inputs
- PR number (from CI environment: `GITHUB_PR_NUMBER`)
- Risk threshold (from `references/risk-weight-table.yaml`, default: 70)
- Release branch pattern (default: `release/*`)

## Steps
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/release-risk-scorer/scripts/risk_scorer.py <pr_number>`
   _(Lab 4: implement this script)_
2. The script reads the diff via `lib/git_diff.py` and scores each risk factor
   from `references/risk-weight-table.yaml`.
3. Posts the score as a PR check run via `lib/pr.py`.
4. If the total score >= threshold: set the check run to FAILURE (blocks merge).
5. If the total score < threshold: set the check run to SUCCESS.

## Python load-bearing (Lab 4)
`scripts/risk_scorer.py` — implement using `lib/git_diff.py`, `lib/pr.py`,
and `references/risk-weight-table.yaml`. The model writes the risk narrative;
Python computes the score.

## Risk factors
See `references/risk-weight-table.yaml` for the full list and weights.
Key factors: PAN path change (+30), auth flow change (+25), contract change (+20).

## Outputs
- GitHub check run with score and breakdown
- PR comment with risk narrative and factor breakdown

## Acceptance criteria (Lab 4)
- A PR that modifies PAN handling code scores >= 30 and triggers the check.
- A PR that scores >= 70 is blocked (check run FAILURE).
- A PR that scores < 70 passes (check run SUCCESS).
- Score is deterministic: same diff → same score.

## Extension point
Add `scripts/risk_scorer.py` following the pattern in `docs/EXTENDING.md`.
```

- [ ] **Step 4: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/skills/red-team-review/ workbench/skills/test-maintainer/ workbench/skills/release-risk-scorer/
git commit -m "feat(M11): add documented CI skill stubs for Lab 4"
git push origin main
```

---

## Task 12: `docs/ARCHITECTURE.md` and `docs/EXTENDING.md`

**Files:**
- Create: `workbench/docs/ARCHITECTURE.md`
- Create: `workbench/docs/EXTENDING.md`
- Modify: `workbench/README.md` (replace stub with full content)

**Interfaces:**
- Produces: documentation read by the cohort and by `pr-reviewer`

- [ ] **Step 1: Write `workbench/docs/ARCHITECTURE.md`**

```markdown
# Workbench Plugin — Architecture

## CLI Version
Built for Claude Code **2.1.177+**. Component auto-discovery is used —
no explicit paths in `plugin.json`. Validate with `claude plugin validate ./workbench`.

## Superpowers Integration
**Mode: Companion install.** The `superpowers` plugin must be installed alongside
`workbench`. Install: `claude plugin install superpowers@claude-plugins-official`.
`spec-craft` invokes `superpowers:brainstorming` and `superpowers:writing-plans` directly.

## Plugin Layout
```
workbench/
  .claude-plugin/plugin.json   # manifest (name, version, author, keywords)
  commands/                    # thin slash-command entry points (8 files)
  skills/                      # five primary skills + three CI stubs
  agents/                      # four fresh-context subagents
  hooks/                       # hooks.json + journey_record.py + quality_gates.py
  rules/                       # four governance files (auto-loaded)
  scripts/lib/                 # shared deterministic Python (7 modules)
  references/                  # static lookup content (6 files)
  docs/                        # this file + EXTENDING.md
```

## Design Principles
1. **Spec first.** No code without a validated spec.
2. **Fresh context for judgment.** `code-to-spec-validator` and `pr-reviewer`
   run as separate subagents and never see the building context.
3. **Python load-bearing.** Deterministic work (git, file I/O, diff parsing,
   coverage math, secret scanning, issue management) is done in `scripts/lib/`.
   The model does synthesis and judgment only.
4. **Developer stays the decision-maker.** Every pipeline stage has a human gate.
5. **Governed by default.** Four rules files auto-load on every session.

## Pipeline Flow
```
Validated spec
  → planner (subagent) → issues.json + GitHub Issues
  → per issue:
      sdet-architect → failing tests
      → code generation → tests pass
      → code-to-spec-validator (fresh context subagent)
      → pr-reviewer (fresh context subagent)
      → quality_gates.py
      → [HUMAN GATE]
      → PR created
```

## Fallback
If the CLI cannot spawn subagents from a workflow,
`skills/work-orchestrator/scripts/orchestrate.py` calls `claude --print`
for each judgment stage and Python for deterministic stages.
The pipeline stage sequence is identical either way.

## Five Failure Modes
Defined in `references/failure-modes.md`. Loaded verbatim by
`code-to-spec-validator`. The five modes are: spec drift, missing AC,
unsafe data handling, broken contract, missing human gate.

## Marketplace
`marketplace/.claude-plugin/marketplace.json` in the same repo as the plugin.
For local development `source` points to `../workbench`.
For distribution, swap `source` to the GitHub repo git URL.
```

- [ ] **Step 2: Write `workbench/docs/EXTENDING.md`**

```markdown
# Extending the Workbench

## Skill types

### Skill-first
The model does all the work; no scripts.
Example: `agents/pr-reviewer.md` — pure prompt, no Python.

### Hybrid
Model + Python. The model calls a script for deterministic work
and synthesises the result.
Example: `skills/spec-craft` — `validate_spec.py` does structural checks;
the model judges completeness and writes the spec.

### Python load-bearing
Python does the heavy deterministic lift; the model returns a tight
structured result.
Example: `skills/lab-grader` — `grader.py` scores all measurable criteria;
the model writes qualitative feedback prose only.

## Anatomy of a skill

```
skills/<name>/
  SKILL.md          # Required. YAML frontmatter: name, description.
                    # Body: purpose, inputs, steps, outputs, acceptance criteria.
  scripts/          # Optional. Skill-specific Python helpers.
```

Frontmatter required fields:
- `name`: kebab-case, matches directory name
- `description`: one sentence used for triggering — be specific about when to use this skill

## Adding a subagent

1. Create `agents/<name>.md` with YAML frontmatter: `name`, `description`, `model`, `tools`.
2. Write the agent body: persona, inputs, output format, anti-sycophancy rule if applicable.
3. No manifest update needed — auto-discovered.

## Adding a hook

1. Add the Python script to `hooks/`.
2. Add an entry to `hooks/hooks.json` under the relevant event key.
3. Use `${CLAUDE_PLUGIN_ROOT}` for the path to the hooks directory.

## Adding a command

1. Create `commands/<name>.md` with YAML frontmatter: `name`, `description`.
2. Body: one or two lines delegating to the skill or agent. Logic lives in skills.

## Adding a rule

1. Create `rules/<name>.md`.
2. No manifest update needed — auto-loaded by Claude Code.

## The contribution loop

```bash
git checkout -b feature/my-new-skill
# add skill, agent, hook, or command
claude plugin validate ./workbench   # must pass with no errors
git add . && git commit -m "feat: add my-new-skill"
git push origin feature/my-new-skill
# open PR to main
# after merge: bump version in plugin.json, tag with claude plugin tag ./workbench
# teammates run: claude plugin update workbench@mastercard-workbench
```

## Shared Python layer

All skills import from `scripts/lib/`. Never duplicate logic from lib — add a new
function to the appropriate module instead.

| Module | Use for |
|---|---|
| `git_diff.py` | Any git or diff operation |
| `test_runner.py` | Running tests, parsing results |
| `coverage.py` | Coverage math, AC-to-test mapping |
| `pr.py` | GitHub PR and check-run operations |
| `spec_check.py` | Spec template and AC validation |
| `secret_scan.py` | PAN and secret detection |
| `issue.py` | Issue file and GitHub Issue management |

Changes to `scripts/lib/` are reviewed like any other change — they affect every skill.

## Keep it small: one skill, one job

If a skill needs a fresh-context judgment, add a subagent rather than
folding the judgment into the skill. The anti-sycophancy rule requires
the judge to have no knowledge of the session that produced the artifact.
```

- [ ] **Step 3: Write full `workbench/README.md`**

```markdown
# workbench

Mastercard AU engineering workbench — a Claude Code plugin that standardises
how the cohort specs, tests, builds, reviews, and ships, and that powers the
Learning Labs (journey capture and grading).

## Prerequisites

- Claude Code 2.1.177+
- `superpowers` plugin: `claude plugin install superpowers@claude-plugins-official`
- Python 3.11+
- `gh` CLI authenticated: `gh auth login`
- `pyyaml`: `pip3 install pyyaml`

## Install

```bash
claude plugin marketplace add <marketplace-git-url>
claude plugin install workbench@mastercard-workbench
```

## Commands

| Command | Purpose |
|---|---|
| `/spec <problem>` | Create and validate a spec |
| `/test-strategy` | Design the test architecture for a spec |
| `/build-tests` | Generate failing tests (TDD) |
| `/build` | Run the full pipeline: spec → issues → tests → code → review → PR |
| `/review` | Fresh-context PR review of the current diff |
| `/grade <session>` | Grade a lab journey against a rubric |
| `/journey start\|stop\|export` | Control lab journey recording |
| `/lab [n]` | Start a lab session |

## Architecture

See `docs/ARCHITECTURE.md` for the full design, pipeline flow, and principles.

## Extending

See `docs/EXTENDING.md` for how to add skills, agents, hooks, commands, and rules.

## Verification

Run the acceptance checks from `docs/ARCHITECTURE.md` section "Acceptance criteria
for v0.1.0" before tagging a release.
```

- [ ] **Step 4: Validate and commit**

```bash
claude plugin validate ./workbench
git add workbench/docs/ workbench/README.md
git commit -m "docs(M12): add ARCHITECTURE.md, EXTENDING.md, full README"
git push origin main
```

---

## Task 13: Verification acceptance run

**Files:** none created — this task runs the five acceptance checks from the spec.

**Interfaces:**
- Consumes: all of Tasks 1–12
- Produces: a passing verification confirming the plugin is v0.1.0-ready

- [ ] **Step 1: Verify plugin validates cleanly**

```bash
claude plugin validate ./workbench
```

Expected: no errors. Component inventory shows: 8 commands, 4 agents, 8 skills, 1 hooks file.

- [ ] **Step 2: AC-1 — spec validation round-trip**

```bash
# Valid spec — use a purpose-built test spec with the exact required section headers
cat > /tmp/verify_valid_spec.md << 'EOF'
## Context
A toy partial-auth change for the AU acquiring gateway.

## Scope
In scope: partial auth flag in field 56. Out of scope: settlement.

## Interfaces
| Name | Direction | Format | Owner |
|---|---|---|---|
| Gateway | out | ISO 8583 | Platform |

## Data
Field 56 bit 0: partial auth supported flag.

## Acceptance Criteria
AC-1: Given field 56 bit 0 = 1 when issuer partially approves then response code equals 10.
AC-2: Given field 56 absent when any transaction then partial auth must not be assumed.

## Non-Negotiables
No PAN in logs.

## Risks
Risk: core banking may not support field 56 — mitigation: emulator test.
EOF

python3 workbench/skills/spec-craft/scripts/validate_spec.py /tmp/verify_valid_spec.md
echo "Exit: $? (expected: 0)"

# Spec missing a section should fail
cat > /tmp/incomplete_spec.md << 'EOF'
## Context
A toy payments change.

## Scope
In scope: X.
EOF
python3 workbench/skills/spec-craft/scripts/validate_spec.py /tmp/incomplete_spec.md
echo "Exit: $? (expected: 1)"
```

- [ ] **Step 3: AC-2 — quality gates catch a seeded secret**

```bash
cat > /tmp/secret_test.py << 'EOF'
API_KEY = "super_secret_api_key_abc123"
EOF
result=$(python3 -c "
import sys; sys.path.insert(0,'workbench/scripts')
from lib.secret_scan import scan_for_secrets
print(scan_for_secrets(open('/tmp/secret_test.py').read()))
")
echo "Secrets found: $result (expected: non-empty list)"
```

- [ ] **Step 4: AC-3 — journey file produces deterministic grade**

```bash
mkdir -p /tmp/verify_journey
cat > /tmp/verify_journey/verify-s1.jsonl << 'EOF'
{"ts": 1000000, "event": "session-start", "session": "verify-s1", "cwd": "/test"}
{"ts": 1000010, "event": "pre-tool", "session": "verify-s1", "tool": "Read", "input_preview": "spec.md"}
{"ts": 1000020, "event": "gate", "session": "verify-s1", "passed": true}
{"ts": 1000030, "event": "pre-tool", "session": "verify-s1", "tool": "Write", "input_preview": "code"}
{"ts": 1000040, "event": "stop", "session": "verify-s1", "reason": "done"}
EOF

pip3 install pyyaml -q 2>/dev/null || true

python3 workbench/skills/lab-grader/scripts/grader.py \
  /tmp/verify_journey/verify-s1.jsonl \
  workbench/skills/lab-grader/rubric.yaml > /tmp/grade_run1.json

python3 workbench/skills/lab-grader/scripts/grader.py \
  /tmp/verify_journey/verify-s1.jsonl \
  workbench/skills/lab-grader/rubric.yaml > /tmp/grade_run2.json

diff /tmp/grade_run1.json /tmp/grade_run2.json && echo "DETERMINISTIC: PASS" || echo "DETERMINISTIC: FAIL"
```

- [ ] **Step 5: AC-4 — coverage_map finds uncovered AC**

```bash
mkdir -p /tmp/verify_cov/tests
cat > /tmp/verify_cov/spec.md << 'EOF'
## Acceptance Criteria
AC-1: Given X when Y then Z.
AC-2: Given A when B then C.
EOF
cat > /tmp/verify_cov/tests/test_feat.py << 'EOF'
# AC-1
def test_x(): pass
EOF

python3 workbench/skills/sdet-architect/scripts/coverage_map.py \
  /tmp/verify_cov/spec.md /tmp/verify_cov/tests
echo "Exit: $? (expected: 1 — AC-2 uncovered)"
```

- [ ] **Step 6: AC-5 — journey redaction works**

```bash
mkdir -p /tmp/verify_redact
WORKBENCH_JOURNEY_DIR=/tmp/verify_redact \
CLAUDE_SESSION_ID=redact-test \
CLAUDE_TOOL_NAME=Write \
CLAUDE_TOOL_INPUT='pan: 4111111111111111' \
python3 workbench/hooks/journey_record.py pre-tool

grep -c "4111111111111111" /tmp/verify_redact/redact-test.jsonl
echo "(expected: 0)"
```

- [ ] **Step 7: Commit verification results note**

```bash
git commit --allow-empty -m "chore(M13): verification acceptance run passed — all 5 ACs confirmed"
git push origin main
```

---

## Task 14: Tag v0.1.0 and publish marketplace

**Files:**
- Modify: `workbench/.claude-plugin/plugin.json` (confirm version is `0.1.0`)
- Modify: `marketplace/.claude-plugin/marketplace.json` (add git URL for distribution)

**Interfaces:**
- Produces: a tagged release; marketplace installable from GitHub

- [ ] **Step 1: Confirm plugin.json version is 0.1.0**

Read `workbench/.claude-plugin/plugin.json` and verify `"version": "0.1.0"`. If not, update it.

- [ ] **Step 2: Update marketplace source to GitHub URL**

Edit `marketplace/.claude-plugin/marketplace.json` — change `"source": "../workbench"` to:

```json
"source": "https://github.com/ArulaAI/arula-mc-labs-plugin"
```

- [ ] **Step 3: Final plugin validate**

```bash
claude plugin validate ./workbench
claude plugin validate ./marketplace
```

Both must pass with no errors.

- [ ] **Step 4: Commit version and marketplace update**

```bash
git add workbench/.claude-plugin/plugin.json marketplace/.claude-plugin/marketplace.json
git commit -m "chore(M14): finalize v0.1.0 — update marketplace source to GitHub URL"
git push origin main
```

- [ ] **Step 5: Tag the release**

```bash
claude plugin tag ./workbench
```

Expected: creates tag `workbench--v0.1.0` on the current commit.

- [ ] **Step 6: Push the tag**

```bash
git push origin workbench--v0.1.0
```

- [ ] **Step 7: Verify install from marketplace (in a scratch directory)**

```bash
mkdir /tmp/scratch-install && cd /tmp/scratch-install
claude plugin marketplace add https://github.com/ArulaAI/arula-mc-labs-plugin
claude plugin install workbench@mastercard-workbench
claude plugin list
```

Expected: `workbench` appears in the installed plugins list.

- [ ] **Step 8: Final verification — validate the installed plugin**

```bash
claude plugin validate ~/.claude/plugins/cache/mastercard-workbench/workbench/0.1.0
```

Expected: no errors.
