# Workbench Plugin — Architecture

## CLI Version
Built for Claude Code **2.1.177+**; the 0.2.0 acceptance run additionally verified on 2.1.233.
Component auto-discovery is used — no explicit paths in `plugin.json`. Validate with
`claude plugin validate ./workbench`.

The `journey_record.py` hook parses its event payload as JSON on stdin per Anthropic's
documented hook contract (0.2.0). Previously it read `CLAUDE_SESSION_ID`/`CLAUDE_TOOL_NAME`
from environment variables, which the hook contract never populates — every invocation fell
back to a fresh timestamp-based session id, scattering one continuous session across many
`journey/*.jsonl` files.

## Superpowers Integration
**Mode: Companion install.** The `superpowers` plugin must be installed alongside
`workbench`. Install: `claude plugin install superpowers@claude-plugins-official`.
`spec-craft` invokes `superpowers:brainstorming` and `superpowers:writing-plans` directly.

## Plugin Layout
```
workbench/
  .claude-plugin/plugin.json   # manifest (name, version, author, keywords)
  commands/                    # thin slash-command entry points (9 files, incl. /hand-off)
  skills/                      # five primary skills + three CI stubs
  agents/                      # four fresh-context subagents
  hooks/                       # hooks.json + journey_record.py + quality_gates.py
  rules/                       # four governance files (auto-loaded)
  scripts/lib/                 # shared deterministic Python (7 modules)
  references/                  # static lookup content (6 files)
  tests/                       # pytest for hooks (0.2.0)
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

## Hooks Schema
Plugin hooks use the matcher/hooks nested format required by Claude Code 2.1.177+:
```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "..." }]
      }
    ]
  }
}
```

## Marketplace
`marketplace/.claude-plugin/marketplace.json` in the same repo as the plugin.
For local development `source` points to `../workbench`.
For distribution, swap `source` to the GitHub repo git URL.
