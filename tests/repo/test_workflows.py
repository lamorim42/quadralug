import re
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
NAMES = ["ci", "release-gate", "open-release", "tag-release"]


def load(name: str) -> dict[str, Any]:
    return yaml.safe_load((WORKFLOWS / f"{name}.yml").read_text())


def triggers(workflow: dict[str, Any]) -> dict[str, Any]:
    # O YAML 1.1 lê a chave `on` como booleano.
    return workflow[True]


def steps(name: str) -> list[dict[str, Any]]:
    jobs = load(name)["jobs"]
    return jobs[name]["steps"]


def step_index(name: str, fragment: str) -> int:
    for index, step in enumerate(steps(name)):
        if fragment in step.get("run", ""):
            return index
    raise AssertionError(f"nenhum passo de {name} contém {fragment!r}")


def assert_passes_pr_identity(name: str) -> None:
    step = steps(name)[step_index(name, "check-pr")]

    assert step["env"] == {
        "HEAD_REF": "${{ github.head_ref }}",
        "BASE_REF": "${{ github.base_ref }}",
        "HEAD_REPO": "${{ github.event.pull_request.head.repo.full_name }}",
        "BASE_REPO": "${{ github.repository }}",
    }
    for argument in (
        '--head "$HEAD_REF"',
        '--base "$BASE_REF"',
        '--head-repo "$HEAD_REPO"',
        '--base-repo "$BASE_REPO"',
    ):
        assert argument in step["run"]


def test_ci_workflow_passes_pr_identity() -> None:
    assert_passes_pr_identity("ci")


def test_release_gate_workflow_passes_pr_identity() -> None:
    assert_passes_pr_identity("release-gate")


def test_ci_workflow_trigger() -> None:
    branches = triggers(load("ci"))["pull_request"]["branches"]

    assert branches == ["develop", "release/**"]


@pytest.mark.parametrize(
    "fragment", ["tools/git_policy.py check-pr", "make check", "make integration"]
)
def test_ci_workflow_runs(fragment: str) -> None:
    assert step_index("ci", fragment) >= 0


def test_release_gate_workflow_trigger() -> None:
    branches = triggers(load("release-gate"))["pull_request"]["branches"]

    assert branches == ["main"]


@pytest.mark.parametrize(
    "fragment", ["tools/git_policy.py check-pr", "make check", "make integration"]
)
def test_release_gate_workflow_runs(fragment: str) -> None:
    assert step_index("release-gate", fragment) >= 0


def test_open_release_validates_first() -> None:
    validate = step_index("open-release", "tools/git_policy.py check-release")
    create = step_index("open-release", "git/refs")
    open_pr = step_index("open-release", "gh pr create")

    assert validate < create < open_pr


def test_open_release_creates_branch_and_pr() -> None:
    create = steps("open-release")[step_index("open-release", "git/refs")]["run"]
    open_pr = steps("open-release")[step_index("open-release", "gh pr create")]["run"]

    assert "git/ref/heads/develop" in create
    assert "ref=refs/heads/release/$VERSION" in create
    assert "--base main" in open_pr
    assert '--head "release/$VERSION"' in open_pr


def test_open_release_is_manual_with_required_version() -> None:
    dispatch = triggers(load("open-release"))["workflow_dispatch"]

    assert dispatch["inputs"]["version"]["required"] is True


def test_tag_release_workflow_trigger() -> None:
    pull_request = triggers(load("tag-release"))["pull_request"]

    assert pull_request == {"types": ["closed"], "branches": ["main"]}


def test_tag_release_workflow_guards_merged_release_from_this_repo() -> None:
    condition = load("tag-release")["jobs"]["tag-release"]["if"]

    assert "github.event.pull_request.merged == true" in condition
    assert "head.repo.full_name == github.repository" in condition
    assert "startsWith(github.event.pull_request.head.ref, 'release/')" in condition


def test_tag_release_workflow_tags_the_merge_commit() -> None:
    step = steps("tag-release")[step_index("tag-release", "git/refs")]

    assert step["env"]["MERGE_SHA"] == "${{ github.event.pull_request.merge_commit_sha }}"
    assert '-f "sha=$MERGE_SHA"' in step["run"]
    assert '-f "ref=refs/tags/$TAG"' in step["run"]


def test_tag_release_opens_backmerge_conditionally() -> None:
    check = steps("tag-release")[step_index("tag-release", "needs-backmerge")]
    open_pr = steps("tag-release")[step_index("tag-release", "gh pr create")]

    assert check["env"]["RELEASE_SHA"] == "${{ github.event.pull_request.head.sha }}"
    assert open_pr["if"] == "steps.backmerge.outputs.needed == 'true'"
    assert "--base develop --head main" in open_pr["run"]


def test_tag_release_fetches_develop_history() -> None:
    checkout = steps("tag-release")[0]

    assert checkout["with"]["fetch-depth"] == 0


@pytest.mark.parametrize("name", NAMES)
def test_workflow_hardening_declares_permissions(name: str) -> None:
    assert load(name)["permissions"] == {"contents": "read"}


@pytest.mark.parametrize("name", NAMES)
def test_workflow_hardening_pins_actions(name: str) -> None:
    uses = [step["uses"] for step in steps(name) if "uses" in step]

    assert uses
    assert all(re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", action) for action in uses)


@pytest.mark.parametrize("name", NAMES)
def test_workflow_hardening_no_interpolation_in_run(name: str) -> None:
    commands = [step.get("run", "") for step in steps(name)]

    assert not [command for command in commands if "${{" in command]


def test_workflow_hardening_actionlint() -> None:
    result = subprocess.run(["uv", "run", "actionlint"], cwd=ROOT, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout


def test_promotion_token_scope() -> None:
    users = {
        path.name
        for path in (ROOT / ".github").rglob("*")
        if path.is_file() and "PROMOTION_TOKEN" in path.read_text()
    }

    assert users == {"open-release.yml", "tag-release.yml"}


@pytest.mark.parametrize("name", ["ci", "release-gate"])
def test_required_check_job_names(name: str) -> None:
    assert list(load(name)["jobs"]) == [name]
