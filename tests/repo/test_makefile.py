import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FAKE_TOOL = """#!/bin/sh
echo "$(basename "$0") $*" >> "$CALLS_FILE"
case "$(basename "$0") $*" in
  *"$FAIL_ON"*) [ -n "$FAIL_ON" ] && exit 7 ;;
esac
exit 0
"""


@pytest.fixture
def project(tmp_path: Path) -> Path:
    path = tmp_path / "project"
    (path / "web").mkdir(parents=True)
    shutil.copy(ROOT / "Makefile", path)
    shutil.copy(ROOT / ".env.example", path)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path


def run_make(project: Path, target: str, fail_on: str = "") -> tuple[int, list[str], str]:
    bin_dir = project.parent / "bin"
    bin_dir.mkdir(exist_ok=True)
    for tool in ("uv", "npm"):
        script = bin_dir / tool
        script.write_text(FAKE_TOOL)
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
    calls = project.parent / "calls.txt"
    calls.unlink(missing_ok=True)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "CALLS_FILE": str(calls),
        "FAIL_ON": fail_on,
    }

    result = subprocess.run(
        ["make", "--no-print-directory", target],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
    )

    recorded = calls.read_text().splitlines() if calls.exists() else []
    return result.returncode, recorded, result.stderr


def test_make_check_runs_every_tool(project: Path) -> None:
    code, calls, _ = run_make(project, "check")

    assert code == 0
    assert any("ruff check" in call for call in calls)
    assert any("mypy" in call for call in calls)
    assert any("lint-imports" in call for call in calls)
    assert any("pytest" in call for call in calls)
    assert any(call.startswith("npm test") for call in calls)


@pytest.mark.parametrize(
    "tool", ["ruff check", "ruff format", "mypy", "lint-imports", "pytest", "npm test"]
)
def test_make_check_fails_when_tool_fails(project: Path, tool: str) -> None:
    code, _, _ = run_make(project, "check", fail_on=tool)

    assert code != 0


def test_make_check_excludes_integration_suites(project: Path) -> None:
    _, calls, _ = run_make(project, "check")

    pytest_call = next(call for call in calls if "pytest" in call)
    assert "not integration" in pytest_call
    assert "not github" in pytest_call


def test_make_mutation_runs_gate(project: Path) -> None:
    code, calls, _ = run_make(project, "mutation")

    assert code == 0
    assert any("tools/mutation_gate.py mutants/mutmut-cicd-stats.json" in call for call in calls)


def test_make_mutation_runs_gate_after_mutmut_fails(project: Path) -> None:
    _, calls, _ = run_make(project, "mutation", fail_on="mutmut run")

    assert any("tools/mutation_gate.py" in call for call in calls)


def test_make_mutation_runs_gate_failure_stops_target(project: Path) -> None:
    code, _, _ = run_make(project, "mutation", fail_on="mutation_gate")

    assert code != 0


def test_make_mutation_runs_gate_without_stale_report(project: Path) -> None:
    report = project / "mutants" / "mutmut-cicd-stats.json"
    report.parent.mkdir()
    report.write_text(json.dumps({"killed": 1, "total": 1}))
    previous_run = project / "mutants" / "planted.py.meta"
    previous_run.write_text("{}")

    run_make(project, "mutation")

    assert not report.exists()
    assert not previous_run.exists()


def test_make_setup_points_hooks_and_creates_env(project: Path) -> None:
    code, _, _ = run_make(project, "setup")

    hooks_path = subprocess.run(
        ["git", "-C", str(project), "config", "core.hooksPath"], capture_output=True, text=True
    ).stdout.strip()
    assert code == 0
    assert hooks_path == ".githooks"
    assert (project / ".env").read_text() == (project / ".env.example").read_text()


def test_make_setup_keeps_existing_env(project: Path) -> None:
    (project / ".env").write_text("MYSQL_PASSWORD=minha\n")

    code, _, _ = run_make(project, "setup")

    assert code == 0
    assert (project / ".env").read_text() == "MYSQL_PASSWORD=minha\n"


def test_make_e2e_reports_no_suite(project: Path) -> None:
    code, _, stderr = run_make(project, "e2e")

    assert code != 0
    assert "ainda não há suíte" in stderr
