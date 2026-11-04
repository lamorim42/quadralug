from fastapi.testclient import TestClient
from quadralug_backend.main import create_app
from quadralug_backend.shared.database import SqlDatabaseProbe, build_engine
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError


class FakeProbe:
    def __init__(self, reachable: bool) -> None:
        self.reachable = reachable
        self.calls = 0

    def is_reachable(self) -> bool:
        self.calls += 1
        return self.reachable


def test_live_ignores_database() -> None:
    probe = FakeProbe(reachable=False)
    client = TestClient(create_app(probe))

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert probe.calls == 0


def test_ready_ok_with_database_reachable() -> None:
    client = TestClient(create_app(FakeProbe(reachable=True)))

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_problem_with_database_unreachable() -> None:
    client = TestClient(create_app(FakeProbe(reachable=False)))

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "not_ready"
    assert response.json()["status"] == 503


def test_ready_probe_reports_real_query() -> None:
    engine: Engine = create_engine("sqlite://")

    reachable = SqlDatabaseProbe(engine).is_reachable()

    assert reachable is True


def test_engine_hides_sql_parameters_from_errors() -> None:
    engine = build_engine("mysql+pymysql://u:p@127.0.0.1:1/x")

    assert engine.hide_parameters is True


def test_ready_probe_reports_driver_failure() -> None:
    class BrokenEngine:
        def connect(self) -> None:
            raise OperationalError("SELECT 1", {}, Exception("fora do ar"))

    reachable = SqlDatabaseProbe(BrokenEngine()).is_reachable()  # type: ignore[arg-type]

    assert reachable is False
