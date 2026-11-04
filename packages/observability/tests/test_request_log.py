import logging
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from quadralug_observability import RequestLogMiddleware


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestLogMiddleware)

    @app.get("/itens/{item_id}")
    def item(item_id: str) -> dict[str, str]:
        return {"id": item_id}

    @app.get("/quebra")
    def quebra() -> None:
        raise RuntimeError("falhou")

    return app


def request_attributes(caplog: pytest.LogCaptureFixture) -> dict[str, Any]:
    records = [record for record in caplog.records if record.name == "quadralug.http"]
    assert len(records) == 1
    assert records[0].levelno == logging.INFO
    assert records[0].getMessage() == "http.request"
    attributes: dict[str, Any] = records[0].attributes  # type: ignore[attr-defined]
    return attributes


def test_request_log_has_the_four_attributes(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="quadralug.http")
    client = TestClient(build_app())

    client.get("/itens/42")

    attributes = request_attributes(caplog)
    assert attributes["http.request.method"] == "GET"
    assert attributes["http.route"] == "/itens/{item_id}"
    assert attributes["http.response.status_code"] == 200
    assert isinstance(attributes["duration_ms"], float)
    assert attributes["duration_ms"] >= 0


def test_request_log_records_error_status(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="quadralug.http")
    client = TestClient(build_app())

    client.get("/nao-existe")

    attributes = request_attributes(caplog)
    assert attributes["http.response.status_code"] == 404
    assert attributes["http.route"] is None


def test_request_log_records_500_for_unhandled_exception(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="quadralug.http")
    client = TestClient(build_app(), raise_server_exceptions=False)

    response = client.get("/quebra")

    attributes = request_attributes(caplog)
    assert response.status_code == 500
    assert attributes["http.response.status_code"] == 500
    assert attributes["http.route"] == "/quebra"
