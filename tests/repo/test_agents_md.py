from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "fragment",
    [
        "mutations: 3",
        "## Nível de teste por camada",
        "| `domain` e `application` | Unitário",
        "`feature/*` → `develop` → `release/x.y.z` → `main`",
        "depois do OK da Parada 2",
        "`Co-Authored-By`",
    ],
)
def test_agents_md_declares(fragment: str) -> None:
    assert fragment in (ROOT / "AGENTS.md").read_text()


def test_agents_md_is_referenced_by_claude_md() -> None:
    assert "AGENTS.md" in (ROOT / "CLAUDE.md").read_text()
