import json
import os
import shutil
import subprocess
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ("-c", "user.name=t", "-c", "user.email=t@example.invalid")
TIMEOUT_SECONDS = 600


def base_env(project_name: str) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    env["COMPOSE_PROJECT_NAME"] = project_name
    env.pop("COMPOSE_FILE", None)
    return env


def make_clean_copy(destination: Path) -> None:
    files = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\0")
    for name in filter(None, files):
        source = ROOT / name
        if source.is_file():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    subprocess.run(["git", "init", "-q", str(destination)], check=True)
    subprocess.run(["git", "-C", str(destination), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(destination), *IDENTITY, "commit", "-q", "-m", "copia"], check=True
    )


@dataclass
class Stack:
    path: Path
    env: dict[str, str]
    up: subprocess.CompletedProcess[str]

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=self.path,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

    def compose(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self.run("docker", "compose", *args)

    def fetch(self, service: str, path: str, traceparent: str = "") -> tuple[int, str]:
        script = (
            "import sys, urllib.request as u, urllib.error as e\n"
            "headers = {'traceparent': sys.argv[2]} if sys.argv[2] else {}\n"
            "request = u.Request('http://127.0.0.1:8000' + sys.argv[1], headers=headers)\n"
            "try:\n"
            "    response = u.urlopen(request, timeout=10)\n"
            "except e.HTTPError as error:\n"
            "    response = error\n"
            "print(response.status)\n"
            "print(response.read().decode())\n"
        )
        result = self.compose("exec", "-T", service, "python", "-c", script, path, traceparent)
        assert result.returncode == 0, result.stderr
        status, _, body = result.stdout.partition("\n")
        return int(status), body.strip()

    def log_lines(self, *services: str) -> list[str]:
        result = self.compose("logs", "--no-log-prefix", "--no-color", *services)
        return [line for line in result.stdout.splitlines() if line.strip()]

    def log_entries(self, *services: str) -> list[dict[str, Any]]:
        return [json.loads(line) for line in self.log_lines(*services)]

    def state(self, service: str) -> dict[str, Any]:
        result = self.compose("ps", "--all", "--format", "json", service)
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        assert len(lines) == 1, result.stdout + result.stderr
        return json.loads(lines[0])

    def wait_healthy(self, service: str) -> None:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if self.state(service).get("Health") == "healthy":
                return
            time.sleep(1)
        raise AssertionError(f"{service} não ficou healthy")


def bring_up(path: Path, env: dict[str, str]) -> Stack:
    setup = subprocess.run(
        ["make", "setup"],
        cwd=path,
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )
    assert setup.returncode == 0, setup.stdout + setup.stderr
    up = subprocess.run(
        ["make", "up"], cwd=path, env=env, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
    )
    return Stack(path=path, env=env, up=up)


@pytest.fixture(scope="session")
def workspace(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("clone")
    make_clean_copy(path)
    return path


@pytest.fixture(scope="session")
def stack(workspace: Path) -> Iterator[Stack]:
    result = bring_up(workspace, base_env("quadralug-it"))
    yield result
    result.compose("down", "--volumes", "--remove-orphans")


@pytest.fixture
def failed_migrate_stack(workspace: Path) -> Iterator[Stack]:
    env = base_env("quadralug-it-bad")
    env["COMPOSE_FILE"] = "compose.yaml:tests/integration/compose.bad-migrate.yaml"
    result = bring_up(workspace, env)
    yield result
    result.compose("down", "--volumes", "--remove-orphans")
