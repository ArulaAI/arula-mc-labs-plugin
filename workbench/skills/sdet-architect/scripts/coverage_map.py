#!/usr/bin/env python3
"""Map ACs from a spec to test files. Usage: python3 coverage_map.py <spec.md> <test_dir>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.coverage import map_acs_to_tests, find_uncovered_acs


def main():
    if len(sys.argv) < 3:
        print("Usage: coverage_map.py <spec.md> <test_dir>", file=sys.stderr)
        sys.exit(1)
    spec_path, test_dir = sys.argv[1], sys.argv[2]
    mapping = map_acs_to_tests(spec_path, test_dir)
    uncovered = find_uncovered_acs(mapping)
    print(json.dumps({"mapping": mapping, "uncovered": uncovered}, indent=2))
    if uncovered:
        print(f"\nWARNING: {len(uncovered)} AC(s) have no test coverage: {uncovered}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
