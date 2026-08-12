#!/usr/bin/env python3
"""
Export a JSONL journey file to readable markdown.
Usage: python3 recorder.py export <session_id> [journey_dir]
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def export_journey(session_id: str, journey_dir: str = "journey") -> str:
    """Convert session JSONL to markdown. Returns output file path."""
    jsonl_path = Path(journey_dir) / f"{session_id}.jsonl"
    if not jsonl_path.exists():
        print(f"Journey file not found: {jsonl_path}", file=sys.stderr)
        sys.exit(1)

    events = []
    for line in jsonl_path.read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))

    lines = [f"# Journey: {session_id}\n"]
    for event in events:
        ts = datetime.fromtimestamp(event.get("ts", 0)).strftime("%H:%M:%S")
        ev = event.get("event", "unknown")
        if ev == "session-start":
            lines.append(f"**{ts}** Session started in `{event.get('cwd', '')}`\n")
        elif ev == "pre-tool":
            lines.append(f"**{ts}** Tool: `{event.get('tool', '')}` — {event.get('input_preview', '')[:80]}\n")
        elif ev == "post-tool":
            lines.append(f"**{ts}** Tool complete: `{event.get('tool', '')}`\n")
        elif ev == "stop":
            lines.append(f"**{ts}** Session stopped — {event.get('reason', '')}\n")
        elif ev == "gate":
            lines.append(f"**{ts}** Gate: {event.get('decision', '')} — {event.get('reason', '')}\n")
        elif ev == "override":
            lines.append(f"**{ts}** OVERRIDE — reason: {event.get('reason', 'none recorded')}\n")
        else:
            lines.append(f"**{ts}** {ev}: {json.dumps({k: v for k, v in event.items() if k not in ('ts','event','session')})}\n")

    md_path = Path(journey_dir) / f"{session_id}.md"
    md_path.write_text("\n".join(lines))
    return str(md_path)


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "export":
        print("Usage: recorder.py export <session_id> [journey_dir]", file=sys.stderr)
        sys.exit(1)
    session_id = sys.argv[2]
    journey_dir = sys.argv[3] if len(sys.argv) > 3 else "journey"
    out = export_journey(session_id, journey_dir)
    print(f"Exported to: {out}")


if __name__ == "__main__":
    main()
