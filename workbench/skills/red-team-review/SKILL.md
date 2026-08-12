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
