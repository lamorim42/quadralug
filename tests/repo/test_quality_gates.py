import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "services" / "backend" / "src"
BFF_SRC = ROOT / "services" / "bff" / "src"


@pytest.fixture
def sources(tmp_path: Path) -> Path:
    copy = tmp_path / "sources"
    for src in (BACKEND_SRC, BFF_SRC):
        shutil.copytree(
            src, copy / src.parents[0].name, ignore=shutil.ignore_patterns("__pycache__")
        )
    return copy


def run(*args: str, pythonpath: str = "") -> subprocess.CompletedProcess[str]:
    env = {**os.environ}
    if pythonpath:
        env["PYTHONPATH"] = pythonpath
    return subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)


def lint_imports(sources: Path) -> subprocess.CompletedProcess[str]:
    return run(
        "uv",
        "run",
        "lint-imports",
        "--no-cache",
        pythonpath=f"{sources / 'backend'}:{sources / 'bff'}",
    )


def test_ruff_rejects_planted_violation(tmp_path: Path) -> None:
    planted = tmp_path / "planted.py"
    planted.write_text("import os\n")

    result = run("uv", "run", "ruff", "check", "--config", "pyproject.toml", str(planted))

    assert result.returncode != 0
    assert "F401" in result.stdout


@pytest.mark.parametrize(
    "layer",
    ["identity/domain", "identity/application", "weather/domain", "weather/application"],
)
def test_mypy_rejects_untyped_function(tmp_path: Path, layer: str) -> None:
    package = tmp_path / "quadralug_backend" / layer
    package.mkdir(parents=True)
    planted = package / "planted.py"
    planted.write_text("def total(value):\n    return value\n")

    result = run("uv", "run", "mypy", "--config-file", "pyproject.toml", str(planted))

    assert result.returncode != 0
    assert "no-untyped-def" in result.stdout


def test_import_contract_clean_tree_passes(sources: Path) -> None:
    result = lint_imports(sources)

    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    ("planted_file", "import_line", "contract"),
    [
        (
            "backend/quadralug_backend/identity/domain/planted.py",
            "import fastapi\n",
            "backend: dominio sem dependencia externa",
        ),
        (
            "backend/quadralug_backend/identity/domain/planted.py",
            "import sqlalchemy\n",
            "backend: dominio sem dependencia externa",
        ),
        (
            "backend/quadralug_backend/identity/domain/planted.py",
            "import pydantic\n",
            "backend: dominio sem dependencia externa",
        ),
        (
            "backend/quadralug_backend/identity/application/planted.py",
            "import quadralug_backend.identity.infrastructure\n",
            "backend: camadas de cada contexto",
        ),
        (
            "backend/quadralug_backend/identity/application/planted.py",
            "import quadralug_backend.weather.domain\n",
            "backend: contextos independentes",
        ),
        (
            "bff/quadralug_bff/application/planted.py",
            "import quadralug_bff.interface\n",
            "bff: camadas",
        ),
    ],
)
def test_import_contract_violation_fails(
    sources: Path, planted_file: str, import_line: str, contract: str
) -> None:
    (sources / planted_file).write_text(import_line)

    result = lint_imports(sources)

    assert result.returncode != 0
    assert f"{contract} BROKEN" in result.stdout
