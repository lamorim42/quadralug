from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from quadralug_bff.application.readiness import BackendReadiness

router = APIRouter(prefix="/health")


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> JSONResponse:
    backend: BackendReadiness = request.app.state.backend_readiness
    if backend.is_ready():
        return JSONResponse({"status": "ok"})
    return JSONResponse(
        {
            "type": "https://quadralug.local/problems/not-ready",
            "title": "Serviço indisponível",
            "status": 503,
            "detail": "O backend não está acessível.",
            "code": "not_ready",
        },
        status_code=503,
        media_type="application/problem+json",
    )
