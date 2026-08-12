"""Template conformance checks, required-section presence, AC testability linter."""
import json
import re
from pathlib import Path

REQUIRED_SECTIONS = [
    "## Context",
    "## Scope",
    "## Interfaces",
    "## Data",
    "## Acceptance Criteria",
    "## Non-Negotiables",
    "## Risks",
]


def check_sections(spec_text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in spec_text]


def extract_acs(spec_text: str) -> list[tuple[str, str]]:
    """Return list of (AC-ID, text) tuples from the spec."""
    return re.findall(r"(AC-\d+):\s*(.+)", spec_text)


def check_ac_testability(ac_text: str) -> bool:
    """
    Return True if the AC is testable (contains Given/When/Then or an assertion verb).
    A heuristic check — the model judges completeness; this catches obvious failures.
    """
    keywords = ["given", "when", "then", "must", "shall", "returns", "produces", "equals"]
    return any(k in ac_text.lower() for k in keywords)


def validate_spec(spec_path: str) -> dict:
    """
    Run all structural checks on a spec file.
    Returns: { "valid": bool, "missing_sections": [...], "non_testable_acs": [...] }
    """
    text = Path(spec_path).read_text()
    missing = check_sections(text)
    acs = extract_acs(text)
    non_testable = [ac_id for ac_id, ac_text in acs if not check_ac_testability(ac_text)]
    valid = not missing and not non_testable
    return {"valid": valid, "missing_sections": missing, "non_testable_acs": non_testable}


def write_status(spec_path: str, result: dict) -> str:
    """Write spec.status.json next to the spec file. Returns the status file path."""
    status_path = str(Path(spec_path).with_suffix(".status.json"))
    Path(status_path).write_text(json.dumps(result, indent=2))
    return status_path


if __name__ == "__main__":
    import tempfile
    import os
    sample = "\n".join(REQUIRED_SECTIONS) + "\nAC-1: Given X when Y then Z"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(sample)
        tmp = f.name
    result = validate_spec(tmp)
    os.unlink(tmp)
    assert result["valid"], result
    print("smoke test: OK", result)
