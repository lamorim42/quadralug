import asyncio
from collections.abc import Iterator

import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from quadralug_bff.infrastructure import backend_client
from quadralug_bff.infrastructure.backend_client import HttpBackendReadiness, build_backend_client
from quadralug_bff.main import create_app

BACKEND = "http://backend.test"
READY = f"{BACKEND}/health/ready"


@pytest.fixture
def backend() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture
def client() -> TestClient:
    readiness = HttpBackendReadiness(build_backend_client(BACKEND))
    return TestClient(create_app(readiness))


def test_live_ignores_backend(backend: respx.MockRouter, client: TestClient) -> None:
    route = backend.get(READY).mock(side_effect=httpx.ConnectError("fora do ar"))

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert route.call_count == 0


def test_ready_ok_with_backend_ready(backend: respx.MockRouter, client: TestClient) -> None:
    backend.get(READY).mock(return_value=httpx.Response(200, json={"status": "ok"}))

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "outcome",
    [
        httpx.Response(503),
        httpx.Response(500),
        httpx.Response(204),
        httpx.ConnectError("conexão recusada"),
        httpx.ReadTimeout("sem resposta"),
        httpx.ConnectTimeout("sem conexão"),
    ],
    ids=["503", "500", "204", "conexao-recusada", "read-timeout", "connect-timeout"],
)
def test_ready_problem_when_backend_fails(
    backend: respx.MockRouter, client: TestClient, outcome: httpx.Response | Exception
) -> None:
    backend.get(READY).mock(side_effect=[outcome])

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "not_ready"


def test_ready_problem_when_backend_exceeds_total_deadline(
    backend: respx.MockRouter, client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def slow_response(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(5)
        return httpx.Response(200)

    monkeypatch.setattr(backend_client, "TIMEOUT_SECONDS", 0.05)
    backend.get(READY).mock(side_effect=slow_response)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["code"] == "not_ready"


def test_ready_uses_five_second_timeout(backend: respx.MockRouter, client: TestClient) -> None:
    route = backend.get(READY).mock(return_value=httpx.Response(200))

    client.get("/health/ready")

    timeout = route.calls.last.request.extensions["timeout"]
    assert timeout == {"connect": 5.0, "read": 5.0, "write": 5.0, "pool": 5.0}
