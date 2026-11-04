import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ("-c", "user.name=t", "-c", "user.email=t@example.invalid")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *IDENTITY, *args], capture_output=True, text=True
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "repo"
    path.mkdir()
    shutil.copytree(ROOT / ".githooks", path / ".githooks")
    git(path, "init", "-q", "-b", "feature/seed")
    git(path, "config", "core.hooksPath", ".githooks")
    git(path, "add", ".")
    git(path, "commit", "-q", "-m", "seed")
    return path


@pytest.mark.parametrize("branch", ["main", "develop", "release/0.1.0", "featurex"])
def test_pre_commit_refuses_branch(repo: Path, branch: str) -> None:
    git(repo, "update-ref", f"refs/heads/{branch}", "HEAD")
    git(repo, "symbolic-ref", "HEAD", f"refs/heads/{branch}")

    result = git(repo, "commit", "--allow-empty", "-m", "x")

    assert result.returncode != 0
    assert branch in result.stderr


def test_pre_commit_refuses_detached_head(repo: Path) -> None:
    git(repo, "checkout", "-q", "--detach")

    result = git(repo, "commit", "--allow-empty", "-m", "x")

    assert result.returncode != 0
    assert "HEAD destacado" in result.stderr


def test_pre_commit_accepts_feature_branch(repo: Path) -> None:
    git(repo, "checkout", "-q", "-b", "feature/x")

    result = git(repo, "commit", "--allow-empty", "-m", "x")

    assert result.returncode == 0


@pytest.fixture
def remote(repo: Path, tmp_path: Path) -> Path:
    path = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(path)], check=True)
    git(repo, "remote", "add", "origin", str(path))
    git(repo, "checkout", "-q", "-b", "feature/x")
    return path


def remote_refs(remote: Path) -> str:
    return subprocess.run(["git", "ls-remote", str(remote)], capture_output=True, text=True).stdout


def test_pre_push_accepts_feature_branch(repo: Path, remote: Path) -> None:
    result = git(repo, "push", "origin", "feature/x")

    assert result.returncode == 0
    assert "refs/heads/feature/x" in remote_refs(remote)


def test_pre_push_refuses_other_destination(repo: Path, remote: Path) -> None:
    result = git(repo, "push", "origin", "feature/x:develop")

    assert result.returncode != 0
    assert remote_refs(remote) == ""


def test_pre_push_refuses_tag(repo: Path, remote: Path) -> None:
    git(repo, "tag", "v0.1.0")

    result = git(repo, "push", "origin", "v0.1.0")

    assert result.returncode != 0
    assert remote_refs(remote) == ""


def test_pre_push_refuses_when_one_of_many_is_bad(repo: Path, remote: Path) -> None:
    result = git(repo, "push", "origin", "feature/x", "feature/x:main")

    assert result.returncode != 0
    assert remote_refs(remote) == ""
