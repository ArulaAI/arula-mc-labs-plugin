"""GitHub PR and check-run management via gh CLI."""
import json
import subprocess


def create_pr(title: str, body: str, base: str = "main", draft: bool = False) -> str:
    """Create a PR and return its URL."""
    cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
    if draft:
        cmd.append("--draft")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def add_pr_comment(pr_number: int, body: str) -> None:
    """Add a comment to an existing PR."""
    subprocess.run(
        ["gh", "pr", "comment", str(pr_number), "--body", body], check=True
    )


def get_pr_number(branch: str) -> int | None:
    """Return PR number for the given branch, or None if not found."""
    result = subprocess.run(
        ["gh", "pr", "view", branch, "--json", "number"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout).get("number")


def build_pr_body(spec_path: str, issue_number: int, validator_notes: str,
                  reviewer_notes: str, gate_results: str) -> str:
    """Assemble the standard PR body used by work-orchestrator."""
    return f"""## Spec
See issue #{issue_number} — spec: `{spec_path}`

## Code-to-Spec Validation
{validator_notes}

## PR Review
{reviewer_notes}

## Quality Gates
{gate_results}
"""


if __name__ == "__main__":
    print("pr.py loaded — smoke test: OK")
