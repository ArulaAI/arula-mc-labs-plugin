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
3. The primary path writes `risk-score.json` locally and exits non-zero at or above
   the threshold (blocking locally) via the shared lib's local-artifact mode
   (authored in Lab 4). The check-run path below is optional and CI-gated.
4. Optional (CI): post the score as a PR check run via `lib/pr.py` — FAILURE at or
   above the threshold (blocks merge), SUCCESS below it.

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
