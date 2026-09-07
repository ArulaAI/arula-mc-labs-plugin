#!/usr/bin/env python3
"""
Regression tests for hooks/run-python (interpreter cache resolution).

Run: python3 -m pytest workbench/tests/ -q

The behaviour under test is the launcher's contract with the project-local cache at
`$CLAUDE_PROJECT_DIR/.claude/hooks/.python_path`: reuse it when it works, replace it when it
does not, and never exec a path that cannot run.

Why the stale case has a test of its own: the launcher previously accepted any non-empty cache.
A path whose interpreter had been removed, upgraded or renamed still looked valid, so `exec`
failed with 126/127 and the hook did not run. A consumer whose hook blocks on exit 2 reads that
as "no block" -- so the gate was disabled without anything saying so.
"""
import os
import shutil
import stat
import subprocess
from pathlib import Path

LAUNCHER = Path(__file__).parent.parent / "hooks" / "run-python"


def cache_path(project_dir: Path) -> Path:
    return project_dir / ".claude" / "hooks" / ".python_path"


def make_project(tmp_path: Path) -> Path:
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    probe = tmp_path / "probe.py"
    probe.write_text("print('ran')\n", encoding="utf-8")
    return tmp_path


def run(project_dir: Path, extra_path: str | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)}
    if extra_path:
        env["PATH"] = extra_path + os.pathsep + env.get("PATH", "")
    return subprocess.run(
        ["bash", str(LAUNCHER), str(project_dir / "probe.py")],
        capture_output=True, text=True, env=env,
    )


def shadow_dir_without_python(tmp_path: Path) -> str:
    """A PATH entry where every python launcher exists but fails, leaving coreutils intact."""
    d = tmp_path / "shadow"
    d.mkdir()
    for name in ("py", "python", "python3"):
        f = d / name
        f.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        f.chmod(f.stat().st_mode | stat.S_IEXEC)
    return str(d)


def test_absent_cache_is_resolved_and_written(tmp_path):
    project = make_project(tmp_path)
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert "ran" in result.stdout
    assert cache_path(project).read_text(encoding="utf-8").strip()


def test_empty_cache_is_replaced(tmp_path):
    project = make_project(tmp_path)
    cache_path(project).write_text("", encoding="utf-8")
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert cache_path(project).read_text(encoding="utf-8").strip()


def test_stale_cache_is_replaced_rather_than_executed(tmp_path):
    """The regression this change exists for."""
    project = make_project(tmp_path)
    cache_path(project).write_text("/nonexistent/python3", encoding="utf-8")

    result = run(project)

    assert result.returncode == 0, (
        "a cache pointing at a missing interpreter must be re-resolved, not exec'd; "
        f"got rc={result.returncode} stderr={result.stderr!r}"
    )
    assert "ran" in result.stdout
    assert cache_path(project).read_text(encoding="utf-8").strip() != "/nonexistent/python3"


def test_cache_pointing_at_a_non_python_executable_is_replaced(tmp_path):
    """A path that runs but is not Python 3.8+ is not a usable interpreter either."""
    project = make_project(tmp_path)
    cache_path(project).write_text(shutil.which("true") or "/bin/true", encoding="utf-8")

    result = run(project)

    assert result.returncode == 0, result.stderr
    assert "ran" in result.stdout


def test_working_cache_is_reused_unchanged(tmp_path):
    project = make_project(tmp_path)
    run(project)
    resolved = cache_path(project).read_text(encoding="utf-8")

    result = run(project)

    assert result.returncode == 0, result.stderr
    assert cache_path(project).read_text(encoding="utf-8") == resolved


def test_no_interpreter_reports_and_exits_nonzero(tmp_path):
    """Fail direction is unchanged: run-python's consumers are advisory, so it exits 1, not 2."""
    project = make_project(tmp_path)
    result = run(project, extra_path=shadow_dir_without_python(tmp_path))

    assert result.returncode == 1
    assert "Python 3.8+ not found" in result.stderr


def test_no_interpreter_does_not_write_a_bad_cache(tmp_path):
    project = make_project(tmp_path)
    run(project, extra_path=shadow_dir_without_python(tmp_path))

    cache = cache_path(project)
    assert not cache.exists() or not cache.read_text(encoding="utf-8").strip()


def test_arguments_are_forwarded_to_the_script(tmp_path):
    project = make_project(tmp_path)
    (project / "probe.py").write_text(
        "import sys; print('args:', ' '.join(sys.argv[1:]))\n", encoding="utf-8")
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    result = subprocess.run(
        ["bash", str(LAUNCHER), str(project / "probe.py"), "pre-tool", "--flag"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "args: pre-tool --flag" in result.stdout


def test_stdin_reaches_the_script(tmp_path):
    """Hooks receive their payload on stdin; the launcher must not consume it."""
    project = make_project(tmp_path)
    (project / "probe.py").write_text(
        "import sys; print('stdin:', sys.stdin.read().strip())\n", encoding="utf-8")
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    result = subprocess.run(
        ["bash", str(LAUNCHER), str(project / "probe.py")],
        input='{"tool_name":"Write"}', capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, result.stderr
    assert 'stdin: {"tool_name":"Write"}' in result.stdout
