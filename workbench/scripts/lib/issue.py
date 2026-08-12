"""Write/read issues.json, open/close GitHub Issues via gh CLI."""
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Issue:
    number: int
    title: str
    body: str
    acs: list[str]
    status: str = "open"
    github_number: int | None = None
    branch: str | None = None


def load_issues(path: str = "issues.json") -> list[Issue]:
    """Load issues from JSON file."""
    data = json.loads(Path(path).read_text())
    return [Issue(**i) for i in data]


def save_issues(issues: list[Issue], path: str = "issues.json") -> None:
    """Save issues to JSON file."""
    Path(path).write_text(json.dumps([asdict(i) for i in issues], indent=2))


def open_github_issue(title: str, body: str, labels: list[str] | None = None) -> int:
    """Create a GitHub Issue and return its number."""
    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    if labels:
        for label in labels:
            cmd += ["--label", label]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # gh returns the issue URL; extract the number
    url = result.stdout.strip()
    return int(url.rstrip("/").split("/")[-1])


def close_github_issue(issue_number: int, comment: str | None = None) -> None:
    """Close a GitHub Issue, optionally adding a closing comment."""
    if comment:
        subprocess.run(
            ["gh", "issue", "comment", str(issue_number), "--body", comment], check=True
        )
    subprocess.run(["gh", "issue", "close", str(issue_number)], check=True)


if __name__ == "__main__":
    issues = [Issue(number=1, title="Test", body="Body", acs=["AC-1"])]
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name
    save_issues(issues, tmp)
    loaded = load_issues(tmp)
    os.unlink(tmp)
    assert loaded[0].title == "Test"
    print("smoke test: OK")
