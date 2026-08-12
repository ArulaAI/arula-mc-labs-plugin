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
