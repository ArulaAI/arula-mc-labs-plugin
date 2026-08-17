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
5. The primary path writes the draft-fix artifact locally (a patch plus
   `docs/DRAFT_FIX.md`) via the shared lib's local-artifact mode (authored in Lab 4).
   The draft-PR path below is optional and CI-gated.
6. Optional (CI): open the proposed fixes as a draft follow-up PR and post missing
   ACs (no test coverage) as PR comments.

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
