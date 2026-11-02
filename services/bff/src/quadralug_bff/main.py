import os

import uvicorn
from fastapi import FastAPI
from quadralug_observability import configure_observability

from quadralug_bff.application.readiness import BackendReadiness
from quadralug_bff.infrastructure.backend_client import HttpBackendReadiness, build_backend_client
from quadralug_bff.interface.health import router as health_router

SERVICE_NAME = "quadralug-bff"


def create_app(backend_readiness: BackendReadiness) -> FastAPI:
    app = FastAPI(title="Quadralug BFF", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.backend_readiness = backend_readiness
    app.include_router(health_router)
    return app


def run() -> None:
    client = build_backend_client(os.environ["BACKEND_URL"])
    app = create_app(HttpBackendReadiness(client))
    configure_observability(app, SERVICE_NAME)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None, access_log=False)
