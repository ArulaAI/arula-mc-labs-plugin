"""Coverage delta math, threshold checks, AC-to-test-file mapping."""
import re
from pathlib import Path


def check_threshold(coverage_pct: float | None, threshold: float = 80.0) -> bool:
    """Return True if coverage meets or exceeds threshold."""
    if coverage_pct is None:
        return False
    return coverage_pct >= threshold


def coverage_delta(before: float | None, after: float | None) -> float:
    """Return coverage change (after - before). None treated as 0."""
    return (after or 0.0) - (before or 0.0)


def map_acs_to_tests(spec_path: str, test_dir: str) -> dict[str, list[str]]:
    """
    Return a mapping of AC-N identifiers to test files that reference them.
    Looks for 'AC-N' string literals in test files.
    """
    spec = Path(spec_path).read_text()
    ac_ids = re.findall(r"(AC-\d+)", spec)
    mapping: dict[str, list[str]] = {ac: [] for ac in ac_ids}
    for test_file in Path(test_dir).rglob("test_*.py"):
        content = test_file.read_text()
        for ac in ac_ids:
            if ac in content:
                mapping[ac].append(str(test_file))
    return mapping


def find_uncovered_acs(mapping: dict[str, list[str]]) -> list[str]:
    """Return AC IDs with no test files."""
    return [ac for ac, files in mapping.items() if not files]


if __name__ == "__main__":
    print("threshold 80%:", check_threshold(85.0))
    print("threshold 80%:", check_threshold(79.9))
    print("smoke test: OK")
