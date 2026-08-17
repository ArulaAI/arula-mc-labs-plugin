#!/usr/bin/env python3
"""
Append-only journey event logger.
Usage: <hook payload JSON on stdin> | python3 journey_record.py <event>
Events: session-start, pre-tool, post-tool, stop

Claude Code delivers hook event data as JSON on stdin. Environment variables
are a secondary fallback and a timestamp is the last resort, so a manual call
with no stdin still records something usable.

The positional <event> argument stays the authoritative event label written to
the journey: `grader.py` matches these labels exactly against rubric checks
(event_exists:session-start, event_contains:pre-tool:...), so the payload's
`hook_event_name` is recorded as an extra field rather than replacing it.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from lib.secret_scan import scan_for_pan, scan_for_secrets

JOURNEY_DIR = Path(os.environ.get("WORKBENCH_JOURNEY_DIR", "journey"))

SENSITIVE_KEYS = {"pan", "track1", "track2", "pin", "password", "secret", "token", "key"}


def read_payload() -> dict:
    """Read the hook event payload from stdin JSON. Returns {} if absent or invalid."""
    if sys.stdin.isatty():
        return {}
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def redact(obj):
    """Recursively redact sensitive values from a dict/list/str."""
    if isinstance(obj, dict):
        return {k: "***REDACTED***" if k.lower() in SENSITIVE_KEYS else redact(v)
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(i) for i in obj]
    if isinstance(obj, str):
        if scan_for_pan(obj):
            return "***PAN-REDACTED***"
        if scan_for_secrets(obj):
            return "***SECRET-REDACTED***"
        return obj
    return obj


def append_event(event_type: str, data: dict, session_id: str) -> None:
    """Append a single event to the session journey file."""
    JOURNEY_DIR.mkdir(parents=True, exist_ok=True)
    journey_file = JOURNEY_DIR / f"{session_id}.jsonl"
    event = {
        "ts": int(time.time()),
        "event": event_type,
        "session": session_id,
        **redact(data),
    }
    with journey_file.open("a") as f:
        f.write(json.dumps(event) + "\n")


def main():
    payload = read_payload()
    event = sys.argv[1] if len(sys.argv) > 1 else payload.get("hook_event_name", "unknown")
    session_id = (payload.get("session_id")
                  or os.environ.get("CLAUDE_SESSION_ID")
                  or f"session-{int(time.time())}")

    tool_name = payload.get("tool_name") or os.environ.get("CLAUDE_TOOL_NAME", "")
    tool_input = payload.get("tool_input") or os.environ.get("CLAUDE_TOOL_INPUT", "")
    if not isinstance(tool_input, str):
        tool_input = json.dumps(tool_input)

    if event == "session-start":
        data = {"cwd": payload.get("cwd", os.getcwd())}
    elif event == "pre-tool":
        data = {"tool": tool_name, "input_preview": tool_input[:200]}
    elif event == "post-tool":
        data = {"tool": tool_name}
    elif event == "stop":
        data = {"reason": payload.get("stop_reason", os.environ.get("CLAUDE_STOP_REASON", ""))}
    else:
        data = {}

    if payload.get("hook_event_name"):
        data["hook_event"] = payload["hook_event_name"]
    append_event(event, data, session_id)


if __name__ == "__main__":
    main()
