import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.github

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ("-c", "user.name=probe", "-c", "user.email=probe@users.noreply.github.com")


@pytest.mark.parametrize("branch", ["develop", "main"])
def test_github_refuses_direct_push(tmp_path: Path, branch: str) -> None:
    origin = subprocess.run(
        ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", "--branch", branch, origin, str(clone)], check=True
    )
    subprocess.run(
        ["git", "-C", str(clone), *IDENTITY, "commit", "-q", "--allow-empty", "-m", "probe"],
        check=True,
    )

    result = subprocess.run(
        ["git", "-C", str(clone), "push", "--no-verify", "origin", f"HEAD:{branch}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "repository rule" in result.stderr.lower()
