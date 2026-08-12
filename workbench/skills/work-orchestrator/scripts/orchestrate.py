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
from lib.issue import load_issues, save_issues, open_github_issue  # noqa: F401
from lib.git_diff import get_diff
from lib.test_runner import run_tests  # noqa: F401
from lib.pr import build_pr_body, create_pr  # noqa: F401
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
