#!/usr/bin/env python3
"""Find tests that reference changed files. Usage: python3 test_discovery.py <file1> [file2...]"""
import sys
from pathlib import Path


def find_tests_for_files(changed_files: list[str], test_root: str = "tests") -> dict[str, list[str]]:
    """Return mapping of changed_file -> list of test files that import or reference it."""
    result: dict[str, list[str]] = {f: [] for f in changed_files}
    for test_file in Path(test_root).rglob("test_*.py"):
        content = test_file.read_text(errors="replace")
        for cf in changed_files:
            module = Path(cf).stem
            if module in content or Path(cf).name in content:
                result[cf].append(str(test_file))
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: test_discovery.py <changed_file1> [changed_file2...]", file=sys.stderr)
        sys.exit(1)
    changed = sys.argv[1:]
    import json
    mapping = find_tests_for_files(changed)
    print(json.dumps(mapping, indent=2))


if __name__ == "__main__":
    main()
