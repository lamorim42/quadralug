import asyncio
import logging

import httpx

logger = logging.getLogger("quadralug.backend_client")

TIMEOUT_SECONDS = 5.0


class HttpBackendReadiness:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def is_ready(self) -> bool:
        try:
            # O timeout do httpx vale por operação; uma resposta em partes o ultrapassaria.
            async with asyncio.timeout(TIMEOUT_SECONDS):
                response = await self._client.get("/health/ready")
        except (httpx.HTTPError, TimeoutError) as error:
            logger.warning(
                "backend.unreachable", extra={"attributes": {"error.type": type(error).__name__}}
            )
            return False
        return response.status_code == httpx.codes.OK


def build_backend_client(base_url: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=base_url, timeout=TIMEOUT_SECONDS)
