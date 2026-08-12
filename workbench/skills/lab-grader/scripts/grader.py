#!/usr/bin/env python3
"""
Score a journey file against a rubric.
Usage: python3 grader.py <session.jsonl> <rubric.yaml>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from lib.secret_scan import scan_for_pan, scan_for_secrets

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def load_rubric(path: str) -> dict:
    """Load rubric from YAML or JSON."""
    text = Path(path).read_text()
    if HAS_YAML:
        return yaml.safe_load(text)
    # Minimal YAML fallback: parse key: value lines only (no nesting)
    raise RuntimeError("PyYAML not installed. Install with: pip3 install pyyaml")


def load_events(jsonl_path: str) -> list[dict]:
    """Load all events from a journey JSONL file."""
    events = []
    for line in Path(jsonl_path).read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def score_criterion(criterion: dict, events: list[dict], journey_text: str) -> dict:
    """Score one rubric criterion. Returns {"id", "met", "score", "evidence"}."""
    check = criterion.get("check", "")
    max_score = criterion.get("max_score", 0)
    met = False
    evidence = "not found"

    if check.startswith("event_exists:"):
        event_type = check.split(":", 1)[1]
        matching = [e for e in events if e.get("event") == event_type]
        met = bool(matching)
        evidence = f"{len(matching)} event(s) of type '{event_type}'"

    elif check.startswith("event_contains:"):
        parts = check.split(":")
        event_type, keyword = parts[1], parts[2] if len(parts) > 2 else ""
        matching = [e for e in events
                    if e.get("event") == event_type and keyword in json.dumps(e)]
        met = bool(matching)
        evidence = f"{len(matching)} matching event(s)"

    elif check.startswith("event_count_gte:"):
        threshold = int(check.split(":", 1)[1])
        met = len(events) >= threshold
        evidence = f"{len(events)} events (threshold: {threshold})"

    elif check == "secret_scan_clean":
        pan = scan_for_pan(journey_text)
        secrets = scan_for_secrets(journey_text)
        met = not pan and not secrets
        evidence = "clean" if met else f"PAN: {pan}, secrets: {secrets}"

    return {
        "id": criterion["id"],
        "description": criterion.get("description", ""),
        "met": met,
        "score": max_score if met else 0,
        "max_score": max_score,
        "evidence": evidence,
    }


def grade(journey_path: str, rubric_path: str) -> dict:
    """Grade a journey against a rubric. Returns grade card dict."""
    events = load_events(journey_path)
    rubric = load_rubric(rubric_path)
    journey_text = Path(journey_path).read_text()

    results = []
    total_score = 0
    max_total = 0
    for criterion in rubric.get("criteria", []):
        result = score_criterion(criterion, events, journey_text)
        results.append(result)
        total_score += result["score"]
        max_total += result["max_score"]

    threshold = rubric.get("pass_threshold", 70)
    pct = (total_score / max_total * 100) if max_total else 0
    passed = pct >= threshold

    return {
        "session": Path(journey_path).stem,
        "lab": rubric.get("lab", 0),
        "score": total_score,
        "max_score": max_total,
        "percent": round(pct, 1),
        "passed": passed,
        "threshold": threshold,
        "criteria": results,
    }


def append_cohort_summary(result: dict, summary_path: str = "cohort-summary.jsonl") -> None:
    """Append an anonymized entry to the cohort summary if the file exists."""
    p = Path(summary_path)
    if not p.exists():
        return
    entry = {
        "lab": result["lab"],
        "score": result["score"],
        "max_score": result["max_score"],
        "percent": result["percent"],
        "passed": result["passed"],
        # omit session ID for anonymization
        "criteria_met": [c["id"] for c in result["criteria"] if c["met"]],
        "criteria_missed": [c["id"] for c in result["criteria"] if not c["met"]],
    }
    with p.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: grader.py <session.jsonl> <rubric.yaml>", file=sys.stderr)
        sys.exit(1)
    journey_path, rubric_path = sys.argv[1], sys.argv[2]
    result = grade(journey_path, rubric_path)

    # Write grade card
    grade_path = journey_path.replace(".jsonl", "-grade.json")
    Path(grade_path).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nGrade card written to: {grade_path}")

    # Append anonymized entry to cohort summary if present
    append_cohort_summary(result)


if __name__ == "__main__":
    main()
