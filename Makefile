IMAGE_TAG := $(shell git rev-parse --short HEAD)
export IMAGE_TAG

MUTATION_REPORT := mutants/mutmut-cicd-stats.json

.PHONY: setup up down check integration mutation e2e

setup:
	git config core.hooksPath .githooks
	test -f .env || cp .env.example .env
	uv sync
	cd web && npm ci

up:
	docker compose up --build --wait

down:
	docker compose down

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy
	uv run lint-imports
	uv run pytest -m "not integration and not github"
	cd web && npm test

integration:
	uv run pytest -m integration

mutation:
	rm -f $(MUTATION_REPORT)
	-uv run mutmut run
	-uv run mutmut export-cicd-stats
	uv run python tools/mutation_gate.py $(MUTATION_REPORT)

e2e:
	@echo "make e2e: ainda não há suíte; ela entra na F5" >&2
	@exit 1
