#!/usr/bin/env python3
"""CLI entry point for spec validation. Usage: python3 validate_spec.py <spec.md>"""
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.spec_check import validate_spec, write_status


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_spec.py <spec.md>", file=sys.stderr)
        sys.exit(1)
    spec_path = sys.argv[1]
    result = validate_spec(spec_path)
    status_path = write_status(spec_path, result)
    print(json.dumps(result, indent=2))
    if not result["valid"]:
        print("\nSpec is NOT READY:", file=sys.stderr)
        for s in result["missing_sections"]:
            print(f"  Missing section: {s}", file=sys.stderr)
        for ac in result["non_testable_acs"]:
            print(f"  Non-testable AC: {ac}", file=sys.stderr)
        sys.exit(1)
    print(f"\nSpec is READY. Status written to {status_path}")


if __name__ == "__main__":
    main()
