from typing import Protocol


class BackendReadiness(Protocol):
    async def is_ready(self) -> bool: ...
