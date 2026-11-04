from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("service", ["backend", "bff"])
def test_python_images_use_frozen_sync(service: str) -> None:
    dockerfile = (ROOT / "services" / service / "Dockerfile").read_text()

    assert "uv sync --frozen" in dockerfile
    assert "USER 10001" in dockerfile
