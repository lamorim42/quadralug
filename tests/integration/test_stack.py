import json
import re
import urllib.request
from collections.abc import Iterator

import pytest

from .conftest import Stack

pytestmark = pytest.mark.integration

TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"
TRACEPARENT = f"00-{TRACE_ID}-00f067aa0ba902b7-01"
KEYS = {
    "timestamp",
    "severity_text",
    "severity_number",
    "body",
    "trace_id",
    "span_id",
    "resource",
    "attributes",
}


@pytest.fixture
def database_stopped(stack: Stack) -> Iterator[None]:
    assert stack.compose("stop", "db").returncode == 0
    yield
    assert stack.compose("start", "db").returncode == 0
    stack.wait_healthy("db")
    stack.wait_healthy("backend")


def request_entries(stack: Stack, service: str) -> list[dict[str, object]]:
    return [
        entry
        for entry in stack.log_entries(service)
        if entry["body"] == "http.request" and entry["attributes"]["http.route"] == "/health/ready"
    ]


def test_make_up_brings_stack_healthy(stack: Stack) -> None:
    assert stack.up.returncode == 0, stack.up.stdout + stack.up.stderr
    for service in ("db", "backend", "bff", "web"):
        assert stack.state(service)["Health"] == "healthy"
    migrate = stack.state("migrate")
    assert migrate["State"] == "exited"
    assert migrate["ExitCode"] == 0


def test_migrate_failure_stops_stack(failed_migrate_stack: Stack) -> None:
    running = failed_migrate_stack.compose("ps", "--services", "--filter", "status=running")

    assert failed_migrate_stack.up.returncode != 0
    assert running.stdout.split() == ["db"]
    assert failed_migrate_stack.state("migrate")["ExitCode"] != 0


def test_web_serves_spa(stack: Stack) -> None:
    with urllib.request.urlopen("http://127.0.0.1:8080/", timeout=10) as response:
        status = response.status
        html = response.read().decode()

    assert status == 200
    assert '<div id="root"></div>' in html
    assert "<title>Quadralug</title>" in html
    script = re.search(r'src="(/assets/[^"]+\.js)"', html)
    assert script is not None
    with urllib.request.urlopen(f"http://127.0.0.1:8080{script[1]}", timeout=10) as asset:
        assert asset.status == 200
        assert "Quadralug" in asset.read().decode()


@pytest.mark.parametrize("service", ["backend", "bff"])
def test_images_run_as_non_root(stack: Stack, service: str) -> None:
    result = stack.compose("exec", "-T", service, "id", "-u")

    assert result.returncode == 0
    assert int(result.stdout) != 0


@pytest.mark.parametrize("service", ["backend", "bff", "web"])
def test_images_tagged_with_short_commit(stack: Stack, service: str) -> None:
    short_commit = stack.run("git", "rev-parse", "--short", "HEAD").stdout.strip()

    result = stack.run("docker", "image", "inspect", f"quadralug-{service}:{short_commit}")

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("service", ["backend", "bff"])
def test_live_answers_with_database_stopped(
    stack: Stack, database_stopped: None, service: str
) -> None:
    status, body = stack.fetch(service, "/health/live")

    assert status == 200
    assert json.loads(body) == {"status": "ok"}


def test_ready_reports_database_stopped(stack: Stack, database_stopped: None) -> None:
    status, body = stack.fetch("backend", "/health/ready")

    assert status == 503
    assert json.loads(body)["code"] == "not_ready"


def test_ready_reports_database_paused(stack: Stack) -> None:
    assert stack.compose("pause", "db").returncode == 0
    try:
        status, body = stack.fetch("backend", "/health/ready")
    finally:
        assert stack.compose("unpause", "db").returncode == 0
    stack.wait_healthy("backend")

    assert status == 503
    assert json.loads(body)["code"] == "not_ready"


def test_ready_reports_database_available(stack: Stack) -> None:
    status, body = stack.fetch("backend", "/health/ready")

    assert status == 200
    assert json.loads(body) == {"status": "ok"}


def test_trace_id_crosses_services_with_traceparent(stack: Stack) -> None:
    status, _ = stack.fetch("bff", "/health/ready", TRACEPARENT)

    assert status == 200
    assert TRACE_ID in {entry["trace_id"] for entry in request_entries(stack, "bff")}
    assert TRACE_ID in {entry["trace_id"] for entry in request_entries(stack, "backend")}


def test_trace_id_crosses_services_without_traceparent(stack: Stack) -> None:
    status, _ = stack.fetch("bff", "/health/ready")

    newest = request_entries(stack, "bff")[-1]["trace_id"]
    assert status == 200
    assert isinstance(newest, str)
    assert re.fullmatch(r"[0-9a-f]{32}", newest)
    assert newest != TRACE_ID
    assert newest in {entry["trace_id"] for entry in request_entries(stack, "backend")}


@pytest.mark.parametrize("service", ["backend", "bff"])
def test_every_service_line_is_json(stack: Stack, service: str) -> None:
    lines = stack.log_lines(service)

    assert lines
    for line in lines:
        assert set(json.loads(line)) == KEYS


@pytest.mark.parametrize(
    ("service", "name"), [("backend", "quadralug-backend"), ("bff", "quadralug-bff")]
)
def test_logs_carry_resource(stack: Stack, service: str, name: str) -> None:
    entries = stack.log_entries(service)

    assert entries
    for entry in entries:
        assert entry["resource"] == {"service.name": name, "deployment.environment": "dev"}


@pytest.mark.parametrize("service", ["backend", "bff"])
def test_boot_logs_no_errors(stack: Stack, service: str) -> None:
    entries = stack.log_entries(service)

    errors = [entry["body"] for entry in entries if entry["severity_number"] >= 17]

    assert entries
    assert errors == []


def test_make_down_keeps_volume(stack: Stack) -> None:
    result = stack.run("make", "down")

    remaining = stack.compose("ps", "--all", "--quiet")
    volumes = stack.run("docker", "volume", "ls", "--quiet")
    assert result.returncode == 0, result.stderr
    assert remaining.stdout.strip() == ""
    assert "quadralug-it_db-data" in volumes.stdout.split()
