# workbench

Mastercard AU engineering workbench — a Claude Code plugin for spec-driven
development, SDET-grade testing, PAN-safe governance, and lab grading.

## Prerequisites

- Claude Code **2.1.177+**
- Python **3.11+**
- `pyyaml` (`pip install pyyaml`) — required by `lab-grader`
- The `superpowers` companion plugin:
  ```
  claude plugin install superpowers@claude-plugins-official
  ```

## Install

```bash
claude plugin install ./workbench
```

Validate after install:

```bash
claude plugin validate ./workbench
```

## Commands

| Command | What it does |
|---|---|
| `/workbench:spec` | Craft or refine a spec via `spec-craft` |
| `/workbench:test-strategy` | Design an SDET-grade test strategy |
| `/workbench:build-tests` | Generate failing tests from a spec |
| `/workbench:build` | Run the full spec → tests → code pipeline |
| `/workbench:review` | Fresh-context spec vs. code validation |
| `/workbench:grade` | Grade a lab submission against its rubric |
| `/workbench:journey` | Export the session journey to markdown |
| `/workbench:lab` | Set up a new lab from `lab.json` |

## Skills (invoked automatically by commands)

| Skill | Purpose |
|---|---|
| `spec-craft` | Spec authoring via superpowers brainstorming + plans |
| `sdet-architect` | Test strategy and coverage mapping |
| `lab-grader` | Rubric-driven lab grading with cohort summary |
| `journey-recorder` | JSONL journey → markdown export |
| `work-orchestrator` | Fallback pipeline if subagents unavailable |

### Lab 4 stubs (documented, not yet implemented)

| Skill | Implements |
|---|---|
| `red-team-review` | Security + PAN red-team, posts findings as GitHub Issues |
| `test-maintainer` | Finds broken tests, proposes fixes as draft PRs |
| `release-risk-scorer` | Scores payment-grade release risk, blocks high-risk PRs |

See each skill's `SKILL.md` for the implementation spec.

## Hooks

| Hook | What it does |
|---|---|
| `SessionStart` | Begins a journey log (JSONL) |
| `PreToolUse` | Logs the tool call; runs secret scan + lint gate |
| `PostToolUse` | Logs the tool result |
| `Stop` | Closes the journey log |

Journey logs are written to `$WORKBENCH_JOURNEY_DIR` (default: `~/.workbench/journeys/`).
**PAN values are redacted** from all log entries before writing.

## Governance

Four rules files auto-load on every session:

- `rules/spec-first.md` — no code without a validated spec
- `rules/payments-safety.md` — PAN handling and secrets governance
- `rules/tdd-contract.md` — test-first TDD contract
- `rules/pr-governance.md` — one PR per issue, required checks

## Security constraints

- PAN values are never logged, printed, or written anywhere.
- `scripts/lib/` uses Python stdlib only.
- Secret scan runs on every `PreToolUse` event via `quality_gates.py`.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Extending

See [docs/EXTENDING.md](docs/EXTENDING.md).

## Lab configuration

Copy `docs/lab.json.example` to `lab.json` in the project root and fill in the fields:

```json
{
  "lab": 1,
  "title": "Foundations and governance",
  "rubric": ".claude/rubrics/lab-1.yaml",
  "journey_session": "lab-1-learner-id",
  "objectives": ["plugin-installed", "spec-created", "quality-gates-ran", "journey-captured", "no-pan-in-journey"]
}
```

Then run `/workbench:lab` to begin.

## Author

Arula.AI / InRhythm — rbuchanan@inrhythm.com
