import os

import uvicorn
from fastapi import FastAPI
from quadralug_observability import configure_observability
from quadralug_observability.database import instrument_engine

from quadralug_backend.shared.database import SqlDatabaseProbe, build_engine
from quadralug_backend.shared.health import DatabaseProbe
from quadralug_backend.shared.health import router as health_router

SERVICE_NAME = "quadralug-backend"


def create_app(database_probe: DatabaseProbe) -> FastAPI:
    app = FastAPI(title="Quadralug backend", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.database_probe = database_probe
    app.include_router(health_router)
    return app


def run() -> None:
    engine = build_engine(os.environ["DATABASE_URL"])
    app = create_app(SqlDatabaseProbe(engine))
    configure_observability(app, SERVICE_NAME)
    instrument_engine(engine)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None, access_log=False)
