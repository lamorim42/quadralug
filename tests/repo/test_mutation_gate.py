import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "tools" / "mutation_gate.py"


def run_gate(report: Path) -> int:
    return subprocess.run([sys.executable, str(GATE), str(report)], capture_output=True).returncode


@pytest.mark.parametrize(
    ("killed", "total", "passes"),
    [
        (80, 100, True),
        (79, 100, False),
        (0, 0, False),
        (100, 100, True),
        (4, 5, True),
        (3, 5, False),
    ],
)
def test_gate_threshold(killed: int, total: int, passes: bool, tmp_path: Path) -> None:
    report = tmp_path / "stats.json"
    report.write_text(json.dumps({"killed": killed, "total": total}))

    code = run_gate(report)

    assert (code == 0) is passes


def test_gate_fails_without_report(tmp_path: Path) -> None:
    code = run_gate(tmp_path / "ausente.json")

    assert code != 0
