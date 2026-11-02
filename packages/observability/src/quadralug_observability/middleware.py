import logging
from time import perf_counter

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("quadralug.http")


class RequestLogMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        started_at = perf_counter()
        status_code = 500

        async def capture_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self._app(scope, receive, capture_status)
        finally:
            logger.info(
                "http.request",
                extra={
                    "attributes": {
                        "http.request.method": scope["method"],
                        "http.route": getattr(scope.get("route"), "path", None),
                        "http.response.status_code": status_code,
                        "duration_ms": round((perf_counter() - started_at) * 1000, 3),
                    }
                },
            )
