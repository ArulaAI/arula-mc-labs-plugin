#!/usr/bin/env python3
"""Deterministic lab objective renderer.

Reads .claude/lab.json and prints the title and objectives verbatim, in array
order.  No summarising, no rephrasing, no reordering.  Objectives come from
lab.json, never from the rubric.

    python3 render_lab.py [project_root]

Exit codes: 0 = success, 1 = lab.json missing, 2 = required field missing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def render(root: Path) -> tuple[int, str]:
    lab_file = root / ".claude" / "lab.json"
    if not lab_file.is_file():
        return 1, f"lab.json not found at {lab_file}"

    try:
        data = json.loads(lab_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        return 1, f"lab.json is not valid JSON: {exc}"

    title = data.get("title")
    if not title or not isinstance(title, str):
        return 2, "lab.json is missing a 'title' string"

    objectives = data.get("objectives")
    if not objectives or not isinstance(objectives, list) or len(objectives) == 0:
        return 2, "lab.json is missing a non-empty 'objectives' array"

    lab_number = data.get("lab", "")
    lines = [f"Lab {lab_number} — {title}", "", "Objectives:"]
    for i, obj in enumerate(objectives, 1):
        lines.append(f"{i}. {obj}")

    return 0, "\n".join(lines)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    code, output = render(root)
    if code == 0:
        print(output)
    else:
        print(output, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
