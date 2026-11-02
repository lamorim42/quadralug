from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def compose() -> dict[str, Any]:
    return yaml.safe_load((ROOT / "compose.yaml").read_text())


def test_only_web_publishes_8080(compose: dict[str, Any]) -> None:
    published = {
        name: service["ports"]
        for name, service in compose["services"].items()
        if "ports" in service
    }

    assert published == {"web": ["8080:8080"]}


@pytest.mark.parametrize(
    ("service", "networks"),
    [
        ("web", {"public"}),
        ("bff", {"public", "internal"}),
        ("backend", {"internal", "data"}),
        ("db", {"data"}),
        ("migrate", {"data"}),
    ],
)
def test_networks_match_tdd_by_service(
    compose: dict[str, Any], service: str, networks: set[str]
) -> None:
    assert set(compose["services"][service]["networks"]) == networks


def test_networks_match_tdd_isolation(compose: dict[str, Any]) -> None:
    networks = compose["networks"]

    assert networks["data"]["internal"] is True
    assert "internal" not in (networks["internal"] or {})
    assert "internal" not in (networks["public"] or {})


@pytest.mark.parametrize("service", ["bff", "web"])
def test_credentials_scope_excludes(compose: dict[str, Any], service: str) -> None:
    environment = compose["services"][service].get("environment", {})

    text = " ".join(f"{key}={value}" for key, value in environment.items()).upper()

    assert "MYSQL" not in text
    assert "DATABASE" not in text


@pytest.mark.parametrize(
    ("service", "variable"),
    [("db", "MYSQL_PASSWORD"), ("backend", "DATABASE_URL"), ("migrate", "DATABASE_URL")],
)
def test_credentials_scope_includes(compose: dict[str, Any], service: str, variable: str) -> None:
    assert variable in compose["services"][service]["environment"]


@pytest.mark.parametrize(
    ("service", "dependency", "condition"),
    [
        ("migrate", "db", "service_healthy"),
        ("backend", "migrate", "service_completed_successfully"),
        ("bff", "backend", "service_healthy"),
        ("web", "bff", "service_healthy"),
    ],
)
def test_depends_on_chain(
    compose: dict[str, Any], service: str, dependency: str, condition: str
) -> None:
    assert compose["services"][service]["depends_on"] == {dependency: {"condition": condition}}
