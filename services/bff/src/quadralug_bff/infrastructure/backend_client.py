import logging

import httpx

logger = logging.getLogger("quadralug.backend_client")

TIMEOUT_SECONDS = 5.0


class HttpBackendReadiness:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def is_ready(self) -> bool:
        try:
            response = self._client.get("/health/ready")
        except httpx.HTTPError as error:
            logger.warning(
                "backend.unreachable", extra={"attributes": {"error.type": type(error).__name__}}
            )
            return False
        return response.status_code == httpx.codes.OK


def build_backend_client(base_url: str) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=TIMEOUT_SECONDS)
