#!/usr/bin/env python3
"""
Append-only journey event logger.
Usage: python3 journey_record.py <event>
Events: session-start, pre-tool, post-tool, stop
Reads CLAUDE_SESSION_ID and CLAUDE_TOOL_NAME from environment if available.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from lib.secret_scan import scan_for_pan, scan_for_secrets

JOURNEY_DIR = Path(os.environ.get("WORKBENCH_JOURNEY_DIR", "journey"))
SESSION_ID = os.environ.get("CLAUDE_SESSION_ID", f"session-{int(time.time())}")

SENSITIVE_KEYS = {"pan", "track1", "track2", "pin", "password", "secret", "token", "key"}


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


def append_event(event_type: str, data: dict) -> None:
    """Append a single event to the session journey file."""
    JOURNEY_DIR.mkdir(parents=True, exist_ok=True)
    journey_file = JOURNEY_DIR / f"{SESSION_ID}.jsonl"
    event = {
        "ts": int(time.time()),
        "event": event_type,
        "session": SESSION_ID,
        **redact(data),
    }
    with journey_file.open("a") as f:
        f.write(json.dumps(event) + "\n")


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")
    tool_input = os.environ.get("CLAUDE_TOOL_INPUT", "")

    if event == "session-start":
        append_event("session-start", {"cwd": os.getcwd()})
    elif event == "pre-tool":
        append_event("pre-tool", {"tool": tool_name, "input_preview": tool_input[:200]})
    elif event == "post-tool":
        append_event("post-tool", {"tool": tool_name})
    elif event == "stop":
        append_event("stop", {"reason": os.environ.get("CLAUDE_STOP_REASON", "")})
    else:
        append_event(event, {})


if __name__ == "__main__":
    main()
