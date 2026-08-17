# Extending the Workbench Plugin

## Adding a new skill

There are three skill types in this plugin. Pick the pattern that fits.

### Type 1: Agentic synthesis skill (model-heavy)

The model does all the work; Python is not required.

**Example:** `spec-craft`

```
workbench/skills/<name>/
  SKILL.md    # frontmatter: name, description. Steps in the body.
```

Add a thin command entry if users should invoke it via `/workbench:<name>`:

```
workbench/commands/<name>.md
```

### Type 2: Python-load-bearing skill (deterministic + synthesis)

Python handles deterministic work; model handles synthesis.

**Example:** `lab-grader`

```
workbench/skills/<name>/
  SKILL.md
  scripts/
    <name>.py    # entry point; may import from lib/
```

`<name>.py` must set `sys.path` four levels up to reach `scripts/lib/`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.git_diff import get_diff
```

Third-party packages are allowed in skill scripts (add to `requirements.txt`
if you create one). `scripts/lib/` must remain stdlib only.

### Type 3: Documented stub for future Labs

Use this when the design is complete but the implementation script is a Lab exercise.

```
workbench/skills/<name>/
  SKILL.md    # includes "LAB N STUB" in description and steps
```

Required content in the SKILL.md body:
- **Inputs** — each env var or argument the script expects
- **Steps** — numbered; mark the unimplemented step with `_(Lab N: implement this script)_`
- **Python load-bearing** — which `lib/` modules to use
- **Acceptance criteria** — testable, deterministic assertions
- **Extension point** — one line pointing back to this file

## Anatomy of a SKILL.md

```markdown
---
name: my-skill
description: "One sentence. Use this skill when..."
---

# my-skill

## Purpose
[What problem this solves]

## Inputs
- [env var or argument and what it means]

## Steps
1. [First step]
2. [Second step]

## Outputs
- [What this produces]

## Acceptance criteria
- [Testable assertion]
```

## Using a shared lib module

All seven modules in `scripts/lib/` are stdlib only and importable from any
skill or hook script with the `sys.path` pattern above. The modules are:

| Module | Exports |
|---|---|
| `git_diff` | `get_diff()`, `list_changed_files()`, `stage_files()`, `commit()` |
| `test_runner` | `run_tests()` → `TestResult` |
| `coverage` | `check_threshold()`, `coverage_delta()`, `map_acs_to_tests()`, `find_uncovered_acs()` |
| `pr` | `create_pr()`, `add_pr_comment()`, `get_pr_number()`, `build_pr_body()` |
| `spec_check` | `validate_spec()`, `write_status()` |
| `secret_scan` | `scan_for_pan()`, `scan_for_secrets()`, `scan_diff()` |
| `issue` | `Issue`, `load_issues()`, `save_issues()`, `open_github_issue()`, `close_github_issue()` |

## Using the agents outside their default input

- **`planner`** accepts a validated spec *or* another structured backlog (a risk register, a
  findings list). It returns JSON and does not save its own output — **the calling session
  writes the plan** (e.g. to `docs/plans/plan.md`) from that JSON. This is the norm; do not
  grant the agent `Write` to work around it.
- **`pr-reviewer`** is diff-shaped by default. When reviewing a plan or other prose artifact,
  it returns findings without `file:line` anchors.

## Stage boundaries: `/hand-off`

`/hand-off` appends a structured, model-authored checkpoint to `docs/workflow-tracker.md`.
It is deliberately **not** a deterministic script: the audit backbone is `journey_record.py`'s
hook capture, which runs independently of what the command writes. Grading reads hook-captured
journey events for pass/fail and treats `workflow-tracker.md` as the human-readable record — so
a thin or skipped hand-off never silently breaks grading integrity.

A lab may keep its own `.claude/commands/hand-off.md`; a project-level command overrides the
plugin's. The plugin command runs `.claude/scripts/journey_event.py` when the project provides one.

## Contribution loop

1. Write the SKILL.md (spec first).
2. Run `claude plugin validate ./workbench` — must pass before writing any code.
3. Write the script (if Type 2). Test with `python3 scripts/<name>.py`.
4. Re-validate: `claude plugin validate ./workbench`.
5. Open a PR — `pr-reviewer` agent checks it with fresh context.

## Security constraints (mandatory)

- Never log, print, or write PAN values.
- `scripts/lib/` modules must be stdlib only.
- If your script processes untrusted input, call `scan_for_pan()` before writing to any file.
