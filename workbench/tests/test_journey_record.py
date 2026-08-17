#!/usr/bin/env python3
"""
Smoke tests for hooks/journey_record.py (C-1: stdin payload contract).

Run: python3 -m pytest workbench/tests/ -q
"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "journey_record.py"


def run_hook(payload, event, journey_dir):
    """Invoke the hook with a JSON payload on stdin, as Claude Code does."""
    return subprocess.run(
        [sys.executable, str(HOOK), event],
        input=json.dumps(payload) if payload is not None else "",
        capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "WORKBENCH_JOURNEY_DIR": str(journey_dir)},
    )


def read_events(journey_dir, session):
    lines = (journey_dir / f"{session}.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def test_session_id_from_stdin_payload(tmp_path):
    """The payload's session_id names the journey file — not a fresh timestamp."""
    run_hook({"session_id": "s1", "hook_event_name": "PreToolUse",
              "tool_name": "Edit"}, "pre-tool", tmp_path)
    events = read_events(tmp_path, "s1")
    assert events[0]["session"] == "s1"
    assert events[0]["tool"] == "Edit"


def test_one_session_produces_one_file(tmp_path):
    """The C-1 regression: several events in one session must not scatter."""
    for _ in range(3):
        run_hook({"session_id": "s2", "tool_name": "Read"}, "pre-tool", tmp_path)
    assert [p.name for p in tmp_path.glob("*.jsonl")] == ["s2.jsonl"]
    assert len(read_events(tmp_path, "s2")) == 3


def test_event_label_stays_grader_vocabulary(tmp_path):
    """grader.py matches labels exactly; hook_event_name must not replace them."""
    run_hook({"session_id": "s3", "hook_event_name": "PreToolUse"}, "pre-tool", tmp_path)
    event = read_events(tmp_path, "s3")[0]
    assert event["event"] == "pre-tool"
    assert event["hook_event"] == "PreToolUse"


def test_dict_tool_input_is_serialised(tmp_path):
    """tool_input arrives as a dict; the 200-char preview must not crash on it."""
    run_hook({"session_id": "s4", "tool_name": "Edit",
              "tool_input": {"file_path": "/tmp/x.py"}}, "pre-tool", tmp_path)
    assert "/tmp/x.py" in read_events(tmp_path, "s4")[0]["input_preview"]


def test_pan_in_payload_is_redacted(tmp_path):
    """Existing redaction still applies to stdin-sourced data."""
    run_hook({"session_id": "s5", "tool_name": "Edit",
              "tool_input": "card 4111111111111111"}, "pre-tool", tmp_path)
    assert "4111111111111111" not in json.dumps(read_events(tmp_path, "s5")[0])


def test_no_stdin_still_records(tmp_path):
    """A manual call with no payload falls back instead of crashing."""
    result = run_hook(None, "session-start", tmp_path)
    assert result.returncode == 0
    assert len(list(tmp_path.glob("*.jsonl"))) == 1


def test_malformed_stdin_does_not_crash(tmp_path):
    """A hook that raises would break the tool call it is attached to."""
    result = subprocess.run(
        [sys.executable, str(HOOK), "pre-tool"],
        input="not json", capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "WORKBENCH_JOURNEY_DIR": str(tmp_path)},
    )
    assert result.returncode == 0
