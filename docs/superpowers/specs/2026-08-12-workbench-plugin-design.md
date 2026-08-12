# Workbench Plugin — Design Spec
**Date:** 2026-08-12  
**Author:** Rob Buchanan / Arula.AI  
**Status:** Approved — ready for implementation planning

---

## 1. Goal

Build a Claude Code plugin named `workbench` that standardizes how the Mastercard Australia cohort specs, tests, builds, reviews, and ships — and that powers the Learning Labs (journey capture and grading). Distributed as a private plugin through a marketplace entry in the same repo.

---

## 2. Decisions locked

| Decision | Choice |
|---|---|
| Repo name | `ArulaAI/arula-mc-labs-plugin` (private) |
| Marketplace | Subdirectory `marketplace/` in same repo (not a second repo) |
| Superpowers integration | Companion install — `superpowers` plugin required alongside `workbench` |
| PRs per build | One PR per issue (not per spec) |
| Issue tracking | Local `issues.json` + real GitHub Issues via `gh` |
| CI skill stubs | Documented stubs — full SKILL.md, scripts left for Lab 4 cohort |
| Build approach | Sequential milestone (Option A) |

---

## 3. Repository layout

```
arula-mc-labs-plugin/           # GitHub repo: ArulaAI/arula-mc-labs-plugin (private)
  workbench/                    # The plugin itself
    .claude-plugin/
      plugin.json
    commands/
      spec.md
      test-strategy.md
      build-tests.md
      build.md
      review.md
      grade.md
      journey.md
      lab.md
    skills/
      spec-craft/
        SKILL.md
        scripts/
          validate_spec.py
      sdet-architect/
        SKILL.md
        scripts/
          coverage_map.py
          test_discovery.py
      work-orchestrator/
        SKILL.md
        scripts/
          orchestrate.py        # fallback if CLI can't spawn subagents from workflow
      journey-recorder/
        SKILL.md
        scripts/
          recorder.py
      lab-grader/
        SKILL.md
        rubric.yaml
        scripts/
          grader.py
      red-team-review/          # CI stub — Lab 4
        SKILL.md
      test-maintainer/          # CI stub — Lab 4
        SKILL.md
      release-risk-scorer/      # CI stub — Lab 4
        SKILL.md
    agents/
      planner.md
      code-to-spec-validator.md
      pr-reviewer.md
      clean-room-judge.md
    hooks/
      hooks.json
      journey_record.py
      quality_gates.py
    rules/
      coding-standards.md
      ai-use-policy.md
      spec-template.md
      payments-guardrails.md
    scripts/
      lib/
        git_diff.py
        test_runner.py
        coverage.py
        pr.py
        spec_check.py
        secret_scan.py
        issue.py
    references/
      payments-checklist.md
      pan-patterns.txt
      iso-field-map.yaml
      risk-weight-table.yaml
      spec-template-reference.md
      failure-modes.md
    docs/
      ARCHITECTURE.md
      EXTENDING.md
    README.md
  marketplace/                  # Private marketplace entry
    .claude-plugin/
      marketplace.json
  docs/                         # Repo-level docs (this spec, build instructions)
    Workbench_Plugin_Build_Instructions.md
    superpowers/
      specs/
        2026-08-12-workbench-plugin-design.md
```

---

## 4. Plugin manifest

`workbench/.claude-plugin/plugin.json`:

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

Auto-discovery handles `commands/`, `agents/`, `skills/`, `hooks/hooks.json` — no explicit paths needed. Validate with `claude plugin validate ./workbench`.

---

## 5. Marketplace entry

`marketplace/.claude-plugin/marketplace.json`:

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

For distribution: swap `source` to the GitHub repo git URL. Install: `claude plugin marketplace add <git-url>`, then `claude plugin install workbench@mastercard-workbench`.

---

## 6. Rules (auto-loaded governance)

Four files in `workbench/rules/` auto-loaded on every session:

**`coding-standards.md`** — the review bar the `pr-reviewer` subagent uses: naming conventions, structure, test requirements, payments-specific guardrails (no PAN logging, ISO field handling, secrets hygiene).

**`ai-use-policy.md`** — what Claude can and cannot do autonomously; gate points requiring human approval; audit trail requirements; what constitutes a blocker vs. a warning.

**`spec-template.md`** — the canonical spec shape `spec-craft` enforces. Sections: context, scope, interfaces, data, acceptance criteria, non-negotiables, risks. Each section has field-level descriptions. This is the structural contract for `spec_check.py`.

**`payments-guardrails.md`** — payments-specific rules: PAN handling, ISO field constraints, authorization flow requirements, downstream contract obligations.

---

## 7. Shared Python layer (`scripts/lib/`)

Single-purpose modules imported by all skills. The model calls these for deterministic work; it only does synthesis and judgment.

| Module | Responsibility |
|---|---|
| `git_diff.py` | Extract diffs, list changed files, stage/commit |
| `test_runner.py` | Run test commands, parse pass/fail/coverage output |
| `coverage.py` | Delta math, threshold checks, AC-to-test-file mapping |
| `pr.py` | `gh pr create/view/comment`, check-run management |
| `spec_check.py` | Template conformance, required-section presence, AC testability linter |
| `secret_scan.py` | PAN pattern detection, secret pattern matching |
| `issue.py` | Write/read `issues.json`, open/close GitHub Issues via `gh` |

Static lookup content in `references/` — consumed by scripts and the model, never generated at runtime.

---

## 8. Skills

### 8.1 `spec-craft` — `/spec`
- Invokes superpowers brainstorming and planning skills (companion install required)
- Formats output into `rules/spec-template.md` structure
- `validate_spec.py` does structural checks: required sections present, ACs testable, IDs resolvable
- Model judges completeness and clarity
- Outputs: `spec.md` + `spec.status.json` (valid / gaps listed)
- Gate: human reviews "ready to work" summary before proceeding
- Acceptance: a spec missing a required section or with a non-testable AC is reported not-ready with specific gaps

### 8.2 `sdet-architect` — `/test-strategy`, `/build-tests`
- Proposes test architecture: unit/contract/integration/emulator boundaries, coverage targets, local vs CI split
- Generates failing tests from ACs (TDD-first)
- `coverage_map.py` maps ACs to test files; `test_discovery.py` finds tests broken by a change
- Outputs: test plan document + generated test files + coverage baseline
- Acceptance: every AC in the spec maps to at least one test; strategy names emulator and contract boundaries

### 8.3 `work-orchestrator` — `/build`
- Calls `issue.py` to break spec into ordered issues → `issues.json` + GitHub Issues
- Per issue pipeline:
  1. `sdet-architect` — write failing tests
  2. Code generation — implement until tests pass (Python runs tests via `test_runner.py`)
  3. `code-to-spec-validator` subagent — fresh context, scores change against spec and five failure modes
  4. `pr-reviewer` subagent — fresh context, skeptical reviewer, no sycophancy
  5. `quality_gates.py` — lint, security scan, secret scan, coverage threshold
  6. Human approval gate
  7. `pr.py` — opens PR with spec link, validator notes, reviewer notes, gate results
- Fallback: if CLI cannot spawn subagents from a workflow, `orchestrate.py` calls `claude` directly for each judgment stage
- One PR per issue; no PR created if validator fails, reviewer flags a blocker, or any gate fails
- Developer can override with a recorded reason

### 8.4 `journey-recorder` — `/journey start|stop|export`
- Hooks append events to `journey/<session>.jsonl` (see Section 10)
- `recorder.py`: append-only log, redaction of sensitive fields, export to `journey/<session>.md`
- Acceptance: completed lab produces a journey file showing each stage and decision

### 8.5 `lab-grader` — `/grade`
- Input: journey file + `rubric.yaml`
- Python scores objective measurable items from the journey log
- Model writes qualitative feedback
- Outputs: per-learner grade card + anonymized cohort summary
- Acceptance: deterministic — same journey + rubric → same score every run

### 8.6 CI stubs (documented, scripts TBD in Lab 4)

**`red-team-review`** — scheduled and on-demand deep security and payments red-team review; posts findings as GitHub issues/comments. Cohort implements `scripts/red_team.py` in Lab 4.

**`test-maintainer`** — on every PR, finds tests broken by the change, proposes minimal fixes in a follow-up PR, flags missing coverage. Cohort implements `scripts/maintainer.py` in Lab 4.

**`release-risk-scorer`** — on PRs to a release branch, scores payment-grade release risk (authorization, holds, PAN paths, downstream contracts); blocks above a configurable threshold as a required check. Cohort implements `scripts/risk_scorer.py` in Lab 4.

---

## 9. Subagents (`agents/`)

Each subagent is a focused reviewer running with clean context — it never sees the building context that produced the artifact it's judging.

**`planner.md`** — input: spec. Output: ordered issue list with per-issue ACs. Small, deterministic prompts. Writes to `issues.json` via `issue.py`.

**`code-to-spec-validator.md`** — input: spec + issue + diff only. Output: pass/fail with reasons, checked against spec and the five failure modes (defined in `references/failure-modes.md`). Explicitly instructed it is not the author.

**`pr-reviewer.md`** — input: diff + `rules/coding-standards.md` only. Output: review comments as a skeptical reviewer. Explicitly instructed it must not soften findings.

**`clean-room-judge.md`** — fresh-context scoring for lab grading and any ad-hoc judgment task that must be independent of the session that produced the artifact.

---

## 10. Hooks (`hooks/hooks.json`)

```json
{
  "hooks": {
    "SessionStart": [{ "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py session-start" }],
    "PreToolUse": [
      { "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py pre-tool" },
      { "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/quality_gates.py pre-tool" }
    ],
    "PostToolUse": [{ "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py post-tool" }],
    "Stop": [{ "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/journey_record.py stop" }]
  }
}
```

**`journey_record.py`** — appends structured events to `journey/<session>.jsonl` on SessionStart, PreToolUse, PostToolUse, and Stop. Redacts sensitive fields before writing.

**`quality_gates.py`** — runs lint, security scan, secret scan, and coverage threshold check. Returns nonzero on failure to halt the orchestrator. Reusable in CI.

---

## 11. Commands (`commands/`)

Thin entry points — logic lives in the skills, not the commands.

| File | Trigger | Delegates to |
|---|---|---|
| `spec.md` | `/spec` | `spec-craft` skill |
| `test-strategy.md` | `/test-strategy` | `sdet-architect` skill |
| `build-tests.md` | `/build-tests` | `sdet-architect` skill |
| `build.md` | `/build` | `work-orchestrator` skill |
| `review.md` | `/review` | `pr-reviewer` agent |
| `grade.md` | `/grade` | `lab-grader` skill |
| `journey.md` | `/journey` | `journey-recorder` skill |
| `lab.md` | `/lab` | per-lab `.claude/lab.json` + rubric |

---

## 11a. Five failure modes (`references/failure-modes.md`)

The five failure modes are the canonical taxonomy used by `code-to-spec-validator` to score a diff. They are defined in `references/failure-modes.md` and loaded by the validator subagent as part of its input context.

1. **Spec drift** — the implementation diverges from what the spec says (different field names, wrong logic, missing requirement).
2. **Missing acceptance criterion** — at least one AC from the spec has no corresponding code path or test.
3. **Unsafe data handling** — PAN, credentials, or sensitive ISO fields logged, persisted, or transmitted insecurely.
4. **Broken contract** — a downstream API contract, ISO message boundary, or emulator interface is violated.
5. **Missing human gate** — a step that requires developer approval ran without it, or the override was not recorded.

---

## 11b. Lab infrastructure conventions

**`lab.json` schema** — per-lab configuration file at `.claude/lab.json` in the learner's project directory (not inside the plugin). Loaded by the `/lab` command at runtime.

```json
{
  "lab": 1,
  "title": "Foundations and governance",
  "rubric": ".claude/rubrics/lab-1.yaml",
  "journey_session": "lab-1-<learner-id>",
  "objectives": ["install-plugin", "run-quality-gates", "capture-journey"]
}
```

Fields: `lab` (integer, 1–4), `title`, `rubric` (path to per-lab rubric file), `journey_session` (session ID for `journey-recorder`), `objectives` (list matching rubric item keys).

**Rubric convention** — each lab ships its own rubric at `.claude/rubrics/lab-<n>.yaml` in the learner's project. The `lab-grader/rubric.yaml` inside the plugin is a starter template only — not the authoritative rubric for any specific lab. `grader.py` accepts a rubric path as its first argument; the `/grade` command resolves the path from `lab.json`.

---

## 12. Build sequence (milestone order)

Each milestone ends with a passing `claude plugin validate ./workbench`.

| Milestone | Deliverables |
|---|---|
| M1 | Git init, GitHub repo, `plugin.json`, `marketplace.json`, validate |
| M2 | `rules/` (all four files), `references/` (incl. `failure-modes.md`), `scripts/lib/` (all modules) |
| M3 | `spec-craft` skill + `validate_spec.py` |
| M4 | `sdet-architect` skill + coverage/discovery scripts |
| M5 | Subagents: `planner`, `code-to-spec-validator`, `pr-reviewer`, `clean-room-judge` |
| M6 | `work-orchestrator` skill + `orchestrate.py` fallback + `quality_gates.py` |
| M7 | Hooks wired: `hooks.json`, `journey_record.py` |
| M8 | `journey-recorder` skill + `recorder.py` |
| M9 | `lab-grader` skill + `rubric.yaml` + `grader.py` |
| M10 | All seven commands (thin entry points) |
| M11 | CI stubs: `red-team-review`, `test-maintainer`, `release-risk-scorer` (documented) |
| M12 | `docs/ARCHITECTURE.md`, `docs/EXTENDING.md`, `README.md` |
| M13 | Verification acceptance run (section 9 of build instructions) |
| M14 | Tag `workbench--v0.1.0`, publish marketplace |

---

## 13. GitHub issue decomposition

One GitHub Issue per milestone. Each issue carries:
- What to build
- Acceptance criteria (what `claude plugin validate` and manual checks must pass)
- The feature branch name: `issue/<n>-<slug>`

Issues opened in the `ArulaAI/arula-mc-labs-plugin` repo at project kickoff.

---

## 14. Lab mapping

| Lab | Skills / components exercised |
|---|---|
| Lab 1 (Foundations, governance, five failure modes) | Install plugin; governance rules, audit trail, `quality_gates`, `journey-recorder` |
| Lab 2 (Spec to trusted build) | `spec-craft`, `work-orchestrator` planner + TDD + `code-to-spec-validator` |
| Lab 3 (Confidence past TDD) | `sdet-architect`, fresh-context validator and reviewer, quality gates |
| Lab 4 (Extend the workbench) | Author CI skill stubs → implement scripts; publish; sync |

---

## 15. Acceptance criteria for v0.1.0

1. `/spec` on a toy payments change produces a spec that fails validation when a section or AC is missing, and passes when complete.
2. `/build` breaks the spec into issues, writes failing tests, generates code, and blocks PR creation when a deliberate spec mismatch is seeded (validator catches it) and when a standards violation is seeded (reviewer catches it). Validator and reviewer ran as separate contexts.
3. Quality gates fail the run on an intentional lint or secret violation.
4. A lab run yields a journey file; `/grade` produces the same score twice on the same journey.
5. Adding a trivial new skill following `EXTENDING.md`, running `claude plugin validate`, and confirming it loads.

Ship v0.1.0 only when all five pass.
