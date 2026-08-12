"""Run test commands, parse pass/fail/coverage output."""
import re
import subprocess
from dataclasses import dataclass


@dataclass
class TestResult:
    passed: int
    failed: int
    errors: int
    coverage_pct: float | None
    output: str
    returncode: int

    @property
    def success(self) -> bool:
        return self.returncode == 0 and self.failed == 0 and self.errors == 0


def run_tests(command: list[str], cwd: str | None = None) -> TestResult:
    """Run a test command and parse its output."""
    result = subprocess.run(
        command, capture_output=True, text=True, cwd=cwd
    )
    output = result.stdout + result.stderr
    passed = _parse_int(r"(\d+) passed", output)
    failed = _parse_int(r"(\d+) failed", output)
    errors = _parse_int(r"(\d+) error", output)
    coverage = _parse_float(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
    return TestResult(
        passed=passed, failed=failed, errors=errors,
        coverage_pct=coverage, output=output, returncode=result.returncode,
    )


def _parse_int(pattern: str, text: str) -> int:
    m = re.search(pattern, text)
    return int(m.group(1)) if m else 0


def _parse_float(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


if __name__ == "__main__":
    r = run_tests(["python3", "-m", "pytest", "--version"])
    print("smoke test returncode:", r.returncode, "OK")
