#!/usr/bin/env python3
"""Tests for scripts/render_lab.py — exact stdout, deterministic output."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "render_lab.py"


def write_lab_json(root: Path, data: dict) -> None:
    d = root / ".claude"
    d.mkdir(parents=True, exist_ok=True)
    (d / "lab.json").write_text(json.dumps(data), encoding="utf-8")


def run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root)],
        capture_output=True, text=True,
    )


def test_valid_lab_exact_stdout(tmp_path):
    """Objectives are printed verbatim, in order, with exact formatting."""
    write_lab_json(tmp_path, {
        "lab": 99,
        "title": "Test Lab",
        "rubric": ".claude/rubrics/test.yaml",
        "objectives": ["obj-a", "obj-b", "obj-c"],
    })
    r = run(tmp_path)
    assert r.returncode == 0
    expected = "Lab 99 — Test Lab\n\nObjectives:\n1. obj-a\n2. obj-b\n3. obj-c\n"
    assert r.stdout == expected


def test_order_preserved(tmp_path):
    """Objectives appear in the same order as the JSON array."""
    write_lab_json(tmp_path, {
        "lab": 1, "title": "T",
        "objectives": ["zz-last", "aa-first", "mm-middle"],
    })
    r = run(tmp_path)
    assert r.returncode == 0
    lines = r.stdout.strip().splitlines()
    assert lines[-3:] == ["1. zz-last", "2. aa-first", "3. mm-middle"]


def test_repeated_runs_identical(tmp_path):
    """Two runs with the same fixture produce byte-identical stdout."""
    write_lab_json(tmp_path, {
        "lab": 2, "title": "Repeat",
        "objectives": ["alpha", "beta"],
    })
    r1 = run(tmp_path)
    r2 = run(tmp_path)
    assert r1.stdout == r2.stdout
    assert r1.returncode == 0


def test_text_preserved_verbatim(tmp_path):
    """Special characters and long text survive without alteration."""
    obj = "harness-confirmed — check (100%) of seam"
    write_lab_json(tmp_path, {
        "lab": 3, "title": "Verbatim",
        "objectives": [obj],
    })
    r = run(tmp_path)
    assert obj in r.stdout


def test_missing_lab_json(tmp_path):
    """Missing lab.json → exit 1."""
    r = run(tmp_path)
    assert r.returncode == 1


def test_missing_title(tmp_path):
    """lab.json without title → exit 2."""
    write_lab_json(tmp_path, {"lab": 1, "objectives": ["x"]})
    r = run(tmp_path)
    assert r.returncode == 2


def test_missing_objectives(tmp_path):
    """lab.json without objectives → exit 2."""
    write_lab_json(tmp_path, {"lab": 1, "title": "T"})
    r = run(tmp_path)
    assert r.returncode == 2


def test_empty_objectives(tmp_path):
    """lab.json with empty objectives array → exit 2."""
    write_lab_json(tmp_path, {"lab": 1, "title": "T", "objectives": []})
    r = run(tmp_path)
    assert r.returncode == 2


def test_rubric_path_not_in_output(tmp_path):
    """The rubric path must not appear in stdout."""
    write_lab_json(tmp_path, {
        "lab": 4, "title": "Clean Title",
        "rubric": ".claude/rubrics/secret.yaml",
        "objectives": ["a"],
    })
    r = run(tmp_path)
    assert r.returncode == 0
    assert "secret.yaml" not in r.stdout
    assert ".claude/rubrics" not in r.stdout
