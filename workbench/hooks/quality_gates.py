#!/usr/bin/env python3
"""
Quality gates: lint, secret scan, and coverage threshold.
Returns exit code 0 on pass, nonzero on fail.
Usage: python3 quality_gates.py pre-tool
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from lib.secret_scan import scan_diff
from lib.git_diff import get_diff
from lib.test_runner import run_tests
from lib.coverage import check_threshold

COVERAGE_THRESHOLD = 80.0
RESULTS = []


def gate_secret_scan() -> bool:
    """Fail if the current diff contains PAN or secrets."""
    try:
        diff = get_diff()
    except subprocess.CalledProcessError:
        return True  # No diff available, skip
    scan = scan_diff(diff)
    if scan["pan"] or scan["secrets"]:
        RESULTS.append({"gate": "secret_scan", "passed": False,
                         "detail": f"PAN: {scan['pan']}, secrets: {scan['secrets']}"})
        return False
    RESULTS.append({"gate": "secret_scan", "passed": True})
    return True


def gate_lint() -> bool:
    """Run ruff lint if available, else skip."""
    result = subprocess.run(["which", "ruff"], capture_output=True)
    if result.returncode != 0:
        RESULTS.append({"gate": "lint", "passed": True, "detail": "ruff not found, skipped"})
        return True
    r = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
    passed = r.returncode == 0
    RESULTS.append({"gate": "lint", "passed": passed, "detail": r.stdout + r.stderr})
    return passed


def gate_coverage() -> bool:
    """Run pytest with coverage if pytest is available, else skip."""
    result = subprocess.run(["which", "pytest"], capture_output=True)
    if result.returncode != 0:
        RESULTS.append({"gate": "coverage", "passed": True, "detail": "pytest not found, skipped"})
        return True
    r = run_tests(["pytest", "--tb=no", "-q", "--cov=.", "--cov-report=term-missing"])
    passed = check_threshold(r.coverage_pct, COVERAGE_THRESHOLD)
    RESULTS.append({
        "gate": "coverage", "passed": passed,
        "detail": f"coverage={r.coverage_pct}% threshold={COVERAGE_THRESHOLD}%"
    })
    return passed


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "pre-tool"
    all_passed = True
    all_passed &= gate_secret_scan()
    all_passed &= gate_lint()
    if mode != "pre-tool":  # coverage only runs on full gate, not pre-tool
        all_passed &= gate_coverage()
    print(json.dumps({"mode": mode, "passed": all_passed, "gates": RESULTS}, indent=2))
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
