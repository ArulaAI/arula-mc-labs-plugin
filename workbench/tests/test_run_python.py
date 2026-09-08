#!/usr/bin/env python3
"""Tests for hooks/run-python — cache validation and stale-cache recovery.

These tests invoke run-python as a bash script with a controlled CACHE_FILE
pointing at a tmp directory.  They verify the sentinel-based validation and
re-resolution behavior.
"""
import os
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

RUN_PYTHON = Path(__file__).parent.parent / "hooks" / "run-python"
# A tiny Python script that prints its own interpreter path
PROBE = "import sys; print(sys.executable)"


def make_cache_dir(tmp_path: Path) -> Path:
    """Create a .claude/hooks/ directory and return it."""
    d = tmp_path / ".claude" / "hooks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_python_with_cache(tmp_path: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Invoke run-python with CLAUDE_PROJECT_DIR pointed at tmp_path."""
    cmd = ["bash", str(RUN_PYTHON)]
    if extra_args:
        cmd.extend(extra_args)
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
    return subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)


def test_missing_cache_resolves(tmp_path):
    """No .python_path file → discovers interpreter, creates cache, succeeds."""
    make_cache_dir(tmp_path)
    r = run_python_with_cache(tmp_path, ["-c", PROBE])
    assert r.returncode == 0
    assert r.stdout.strip()  # printed the interpreter path
    # Cache was created
    cache = tmp_path / ".claude" / "hooks" / ".python_path"
    assert cache.is_file()
    assert len(cache.read_text().strip()) > 0


def test_empty_cache_resolves(tmp_path):
    """Empty .python_path → re-resolves."""
    d = make_cache_dir(tmp_path)
    (d / ".python_path").write_text("")
    r = run_python_with_cache(tmp_path, ["-c", PROBE])
    assert r.returncode == 0
    assert r.stdout.strip()


def test_stale_cache_resolves(tmp_path):
    """Cache pointing to nonexistent path → re-resolves."""
    d = make_cache_dir(tmp_path)
    (d / ".python_path").write_text("/no/such/python/interpreter")
    r = run_python_with_cache(tmp_path, ["-c", PROBE])
    assert r.returncode == 0
    assert r.stdout.strip()


def test_non_python_executable_rejected(tmp_path):
    """Cache pointing to a non-Python executable → sentinel fails, re-resolves.

    Uses a portable temp script that exits 0 but does not print the sentinel.
    """
    d = make_cache_dir(tmp_path)
    # Create a fake executable that exits 0 but is not Python
    fake = tmp_path / "not-python"
    fake.write_text("#!/bin/sh\nexit 0\n")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    (d / ".python_path").write_text(str(fake))
    r = run_python_with_cache(tmp_path, ["-c", PROBE])
    assert r.returncode == 0
    # Should have re-resolved to a real Python, not used the fake
    assert r.stdout.strip() != str(fake)


def test_valid_cache_used(tmp_path):
    """Cache pointing to a working Python 3.11+ → used directly."""
    d = make_cache_dir(tmp_path)
    (d / ".python_path").write_text(sys.executable)
    r = run_python_with_cache(tmp_path, ["-c", PROBE])
    assert r.returncode == 0
    # The probe prints sys.executable; it should match what we cached
    assert r.stdout.strip() == sys.executable


def test_path_with_spaces(tmp_path):
    """A cache directory with spaces in the path works correctly."""
    spaced = tmp_path / "path with spaces"
    d = spaced / ".claude" / "hooks"
    d.mkdir(parents=True, exist_ok=True)
    r = run_python_with_cache(spaced, ["-c", PROBE])
    assert r.returncode == 0
    assert r.stdout.strip()


def test_discovery_order_in_source():
    """The fallback chain must try py -3, then python3, then python — in that order.

    A behavioral test would require PATH manipulation with fake interpreters,
    which is fragile across CI environments.  This structural test verifies the
    order is coded correctly in both run-python (re-resolution) and
    resolve-python (initial resolution).
    """
    for script_name in ("run-python", "resolve-python"):
        script = Path(__file__).parent.parent / "hooks" / script_name
        text = script.read_text()
        py3_pos = text.index("py -3")
        python3_pos = text.index("python3", py3_pos)
        # The bare `python` fallback: find the line that checks version_info
        # after the python3 line (the `python -c` with version guard)
        python_bare_pos = text.index('python -c "import sys;sys.version_info', python3_pos)
        assert py3_pos < python3_pos < python_bare_pos, (
            f"{script_name}: discovery order is wrong — "
            f"py -3 @{py3_pos}, python3 @{python3_pos}, python @{python_bare_pos}"
        )
