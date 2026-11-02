import json
import logging
import os
import re
import subprocess
import sys
import time
from collections.abc import Iterator
from typing import Any

import pytest
from opentelemetry.sdk.trace import TracerProvider
from quadralug_observability import JsonFormatter, build_resource

RESOURCE = {"service.name": "quadralug-bff", "deployment.environment": "test"}
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


def format_record(
    message: str = "evento",
    level: int = logging.INFO,
    attributes: dict[str, Any] | None = None,
    exc_info: Any = None,
) -> str:
    record = logging.LogRecord("t", level, __file__, 1, message, None, exc_info)
    if attributes is not None:
        record.attributes = attributes
    return JsonFormatter(RESOURCE).format(record)


def test_log_contract_has_the_eight_keys() -> None:
    line = format_record()

    assert set(json.loads(line)) == KEYS


def test_log_contract_timestamp_is_utc_with_z() -> None:
    entry = json.loads(format_record())

    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z", entry["timestamp"])


@pytest.fixture
def bahia_timezone(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("TZ", "America/Bahia")
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


def test_log_contract_timestamp_ignores_local_timezone(bahia_timezone: None) -> None:
    record = logging.LogRecord("t", logging.INFO, __file__, 1, "m", None, None)
    record.created = 0.0

    entry = json.loads(JsonFormatter(RESOURCE).format(record))

    assert entry["timestamp"] == "1970-01-01T00:00:00.000000Z"


@pytest.mark.parametrize(
    ("level", "text", "number"),
    [
        (logging.DEBUG, "DEBUG", 5),
        (logging.INFO, "INFO", 9),
        (logging.WARNING, "WARN", 13),
        (logging.ERROR, "ERROR", 17),
        (logging.CRITICAL, "FATAL", 21),
    ],
)
def test_log_contract_severity(level: int, text: str, number: int) -> None:
    entry = json.loads(format_record(level=level))

    assert (entry["severity_text"], entry["severity_number"]) == (text, number)


def test_log_contract_nulls_outside_span() -> None:
    entry = json.loads(format_record())

    assert entry["trace_id"] is None
    assert entry["span_id"] is None


def test_log_contract_ids_inside_span() -> None:
    tracer = TracerProvider().get_tracer("t")

    with tracer.start_as_current_span("s") as span:
        entry = json.loads(format_record())

    context = span.get_span_context()
    assert entry["trace_id"] == format(context.trace_id, "032x")
    assert entry["span_id"] == format(context.span_id, "016x")
    assert re.fullmatch(r"[0-9a-f]{32}", entry["trace_id"])
    assert re.fullmatch(r"[0-9a-f]{16}", entry["span_id"])


@pytest.mark.parametrize("separator", ["\n", "\r", "\v", "\f", "\x85", " ", " "])
def test_log_contract_newline_stays_on_one_line(separator: str) -> None:
    message = f"primeira{separator}segunda"

    line = format_record(message)

    assert line.splitlines() == [line]
    assert json.loads(line)["body"] == message


def test_log_contract_exception_stays_on_one_line() -> None:
    try:
        raise ValueError("falhou\naqui")
    except ValueError:
        line = format_record(level=logging.ERROR, exc_info=sys.exc_info())

    attributes = json.loads(line)["attributes"]
    assert "\n" not in line
    assert attributes["exception.type"] == "ValueError"
    assert "falhou" in attributes["exception.message"]
    assert "ValueError" in attributes["exception.stacktrace"]


def test_log_contract_keeps_attributes() -> None:
    entry = json.loads(format_record(attributes={"event.name": "x", "duration_ms": 87}))

    assert entry["attributes"] == {"event.name": "x", "duration_ms": 87}


def test_resource_attributes_in_every_log() -> None:
    entry = json.loads(format_record())

    assert entry["resource"] == RESOURCE


def test_resource_attributes_reach_configured_logger() -> None:
    script = (
        "import logging\n"
        "from fastapi import FastAPI\n"
        "from quadralug_observability import configure_observability\n"
        "configure_observability(FastAPI(), 'quadralug-bff')\n"
        "logging.getLogger('t').info('evento')\n"
    )
    env = {**os.environ, "DEPLOYMENT_ENVIRONMENT": "homologacao"}

    result = subprocess.run(
        [sys.executable, "-c", script], env=env, capture_output=True, text=True, check=True
    )

    entry = json.loads(result.stdout.splitlines()[-1])
    assert entry["resource"] == {
        "service.name": "quadralug-bff",
        "deployment.environment": "homologacao",
    }


@pytest.mark.parametrize("service", ["quadralug-bff", "quadralug-backend"])
def test_resource_attributes_from_environment(service: str) -> None:
    resource = build_resource(service, {"DEPLOYMENT_ENVIRONMENT": "staging"})

    assert resource == {"service.name": service, "deployment.environment": "staging"}
