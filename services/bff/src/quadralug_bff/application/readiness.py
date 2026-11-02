from typing import Protocol


class BackendReadiness(Protocol):
    def is_ready(self) -> bool: ...
