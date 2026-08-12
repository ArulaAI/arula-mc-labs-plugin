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
