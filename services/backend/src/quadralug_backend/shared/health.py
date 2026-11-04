from typing import Protocol

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health")


class DatabaseProbe(Protocol):
    def is_reachable(self) -> bool: ...


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> JSONResponse:
    probe: DatabaseProbe = request.app.state.database_probe
    if probe.is_reachable():
        return JSONResponse({"status": "ok"})
    return JSONResponse(
        {
            "type": "https://quadralug.local/problems/not-ready",
            "title": "Serviço indisponível",
            "status": 503,
            "detail": "O banco de dados não está acessível.",
            "code": "not_ready",
        },
        status_code=503,
        media_type="application/problem+json",
    )
