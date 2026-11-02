import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "services" / "backend" / "src" / "quadralug_backend"


@pytest.mark.parametrize(
    "directory", ["services/backend", "services/bff", "packages/observability", "web", "tools"]
)
def test_layout_directories(directory: str) -> None:
    assert (ROOT / directory).is_dir()


def test_layout_single_lockfile() -> None:
    files = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()

    locks = [name for name in files if Path(name).name == "uv.lock"]

    assert locks == ["uv.lock"]


@pytest.mark.parametrize("context", ["identity", "weather"])
@pytest.mark.parametrize("layer", ["domain", "application", "infrastructure", "interface"])
def test_layout_backend_layers(context: str, layer: str) -> None:
    assert (BACKEND / context / layer / "__init__.py").is_file()


@pytest.mark.parametrize("service", ["backend", "bff", "web"])
def test_layout_docker_context_is_root(service: str) -> None:
    compose = yaml.safe_load((ROOT / "compose.yaml").read_text())

    assert compose["services"][service]["build"]["context"] == "."


def test_observability_stack_dependencies() -> None:
    manifest = tomllib.loads((ROOT / "packages/observability/pyproject.toml").read_text())

    dependencies = set(manifest["project"]["dependencies"])

    assert dependencies >= {
        "opentelemetry-sdk",
        "opentelemetry-instrumentation-fastapi",
        "opentelemetry-instrumentation-httpx",
        "opentelemetry-instrumentation-sqlalchemy",
        "opentelemetry-exporter-otlp-proto-http",
    }
    assert "structlog" not in dependencies
