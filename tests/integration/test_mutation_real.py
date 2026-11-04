from collections.abc import Iterator
from pathlib import Path

import pytest

from .conftest import base_env, run_in

pytestmark = pytest.mark.integration

RULE = "services/backend/src/quadralug_backend/identity/domain/planted_rule.py"
RULE_TEST = "services/backend/tests/test_planted_rule.py"
TEST_BODY = """from quadralug_backend.identity.domain.planted_rule import is_adult


def test_rule() -> None:
{assertions}
"""


@pytest.fixture
def planted_rule(workspace: Path) -> Iterator[Path]:
    rule = workspace / RULE
    rule.write_text("def is_adult(age: int) -> bool:\n    return age >= 18\n")
    yield workspace
    rule.unlink()
    (workspace / RULE_TEST).unlink()


def run_mutation(workspace: Path, assertions: str) -> tuple[int, str]:
    (workspace / RULE_TEST).write_text(TEST_BODY.format(assertions=assertions))

    result = run_in(workspace, base_env("quadralug-it"), "make", "mutation")

    return result.returncode, result.stdout + result.stderr


def test_make_mutation_real_kills_planted_rule(planted_rule: Path) -> None:
    code, output = run_mutation(
        planted_rule, "    assert is_adult(18) is True\n    assert is_adult(17) is False"
    )

    assert code == 0, output
    assert "mutação: 2 de 2 mortos" in output


def test_make_mutation_real_fails_on_weak_test(planted_rule: Path) -> None:
    code, output = run_mutation(planted_rule, "    assert is_adult(99) is True")

    assert code != 0
    assert "mutação abaixo da meta: 0 de 2" in output
