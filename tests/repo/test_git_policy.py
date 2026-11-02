import subprocess
from pathlib import Path

import git_policy
import pytest


def git(repo: Path, *args: str) -> str:
    identity = ("-c", "user.name=t", "-c", "user.email=t@example.invalid")
    result = subprocess.run(
        ["git", "-C", str(repo), *identity, *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def commit(repo: Path, name: str) -> None:
    (repo / name).write_text(name)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", name)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "repo"
    path.mkdir()
    git(path, "init", "-q", "-b", "develop")
    commit(path, "base")
    return path


@pytest.mark.parametrize(
    ("head", "base"),
    [
        ("feature/x", "develop"),
        ("main", "develop"),
        ("feature/fix-y", "release/0.1.0"),
        ("release/0.1.0", "main"),
    ],
)
def test_pr_route_accepts(head: str, base: str) -> None:
    code = git_policy.main(
        ["check-pr", "--head", head, "--base", base, "--head-repo", "o/r", "--base-repo", "o/r"]
    )

    assert code == 0


@pytest.mark.parametrize(
    ("head", "base"),
    [
        ("develop", "main"),
        ("feature/x", "main"),
        ("release/0.1.0", "develop"),
        ("feature/", "develop"),
        ("featurex", "develop"),
        ("release/", "main"),
        ("release/foo", "main"),
        ("release/0.1", "main"),
        ("main", "release/0.1.0"),
        ("feature/x", "feature/y"),
    ],
)
def test_pr_route_refuses(head: str, base: str) -> None:
    code = git_policy.main(
        ["check-pr", "--head", head, "--base", base, "--head-repo", "o/r", "--base-repo", "o/r"]
    )

    assert code == 1


@pytest.mark.parametrize(
    ("head", "base"),
    [("release/0.1.0", "main"), ("feature/x", "develop"), ("main", "develop")],
)
def test_pr_route_refuses_fork(head: str, base: str) -> None:
    code = git_policy.main(
        ["check-pr", "--head", head, "--base", base, "--head-repo", "f/r", "--base-repo", "o/r"]
    )

    assert code == 1


@pytest.mark.parametrize("version", ["0.1.0", "1.0.0", "10.20.30"])
def test_release_version_accepted(version: str, repo: Path) -> None:
    code = git_policy.main(["check-release", "--version", version, "--remote", str(repo)])

    assert code == 0


@pytest.mark.parametrize(
    "version", ["v0.1.0", "0.1", "0.1.0-rc1", "0.1.0\n", "", "a.b.c", "0.1.0.1"]
)
def test_release_version_refused(version: str, repo: Path) -> None:
    code = git_policy.main(["check-release", "--version", version, "--remote", str(repo)])

    assert code == 1


def test_release_version_refused_when_branch_exists(repo: Path) -> None:
    git(repo, "branch", "release/0.1.0")

    code = git_policy.main(["check-release", "--version", "0.1.0", "--remote", str(repo)])

    assert code == 1


def test_release_version_refused_when_tag_exists(repo: Path) -> None:
    git(repo, "tag", "v0.1.0")

    code = git_policy.main(["check-release", "--version", "0.1.0", "--remote", str(repo)])

    assert code == 1


def test_tag_for_merge_of_release() -> None:
    tag = git_policy.tag_for_merge("release/0.1.0", merged=True, same_repo=True)

    assert tag == "v0.1.0"


@pytest.mark.parametrize(
    ("head", "merged", "same_repo"),
    [
        ("release/0.1.0", False, True),
        ("feature/x", True, True),
        ("release/0.1.0", True, False),
        ("release/nao-e-versao", True, True),
    ],
)
def test_tag_for_merge_gives_nothing(head: str, merged: bool, same_repo: bool) -> None:
    tag = git_policy.tag_for_merge(head, merged=merged, same_repo=same_repo)

    assert tag is None


def test_tag_for_merge_cli_prints_output_line(capsys: pytest.CaptureFixture[str]) -> None:
    code = git_policy.main(
        [
            "tag-for-merge",
            "--head",
            "release/0.1.0",
            "--merged",
            "true",
            "--head-repo",
            "o/r",
            "--base-repo",
            "o/r",
        ]
    )

    assert code == 0
    assert capsys.readouterr().out == "tag=v0.1.0\n"


def test_tag_for_merge_cli_fails_without_tag() -> None:
    code = git_policy.main(
        [
            "tag-for-merge",
            "--head",
            "release/0.1.0",
            "--merged",
            "false",
            "--head-repo",
            "o/r",
            "--base-repo",
            "o/r",
        ]
    )

    assert code == 1


def test_release_needs_backmerge_with_fix_commit(repo: Path) -> None:
    git(repo, "checkout", "-q", "-b", "release/0.1.0")
    commit(repo, "fix")

    needed = git_policy.needs_backmerge(str(repo), "develop", "release/0.1.0")

    assert needed is True


def test_release_needs_backmerge_not_needed_without_fix(repo: Path) -> None:
    git(repo, "branch", "release/0.1.0")

    needed = git_policy.needs_backmerge(str(repo), "develop", "release/0.1.0")

    assert needed is False


def test_release_needs_backmerge_ignores_newer_develop(repo: Path) -> None:
    git(repo, "branch", "release/0.1.0")
    commit(repo, "ahead")

    needed = git_policy.needs_backmerge(str(repo), "develop", "release/0.1.0")

    assert needed is False


def test_release_needs_backmerge_cli_output(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    git(repo, "checkout", "-q", "-b", "release/0.1.0")
    commit(repo, "fix")

    git_policy.main(
        ["needs-backmerge", "--repo", str(repo), "--develop", "develop", "--release", "HEAD"]
    )

    assert capsys.readouterr().out == "needed=true\n"
