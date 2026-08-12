"""Git and diff helpers — extract diffs, list changed files, stage and commit."""
import subprocess


def get_diff(base: str = "HEAD", paths: list[str] | None = None) -> str:
    """Return unified diff between base and working tree."""
    cmd = ["git", "diff", base, "--"]
    if paths:
        cmd.extend(paths)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def list_changed_files(base: str = "HEAD") -> list[str]:
    """Return list of files changed since base."""
    result = subprocess.run(
        ["git", "diff", "--name-only", base, "--"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in result.stdout.splitlines() if f]


def stage_files(paths: list[str]) -> None:
    """Stage specific files for commit."""
    subprocess.run(["git", "add", "--"] + paths, check=True)


def commit(message: str) -> str:
    """Commit staged changes. Returns the new commit SHA."""
    subprocess.run(["git", "commit", "-m", message], check=True)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


if __name__ == "__main__":
    print("changed files:", list_changed_files())
    print("smoke test: OK")
