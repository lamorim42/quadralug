# F0 - Fundação - checks

Mutations: 3
Build: `uv run ruff check .`; `uv run ruff format --check .`; `uv run mypy`; `uv run lint-imports`; `cd web && npm run build`
Plan: `.specs/features/f0-fundacao/plan.md`

41 checks in 5 slices · 5 one-way doors · 0 open

C1 a C36 têm o mesmo número do critério do plano. C37 em diante cobrem as portas e os alvos de `make` que o plano promete fora dos critérios.

## Checks

### S1 - O ambiente sobe do zero

**C1** - Em uma cópia limpa, `make setup` seguido de `make up` sai com 0, com `db`, `backend`, `bff` e `web` em `healthy` e `migrate` em `exited (0)` (AC 1)
Proof: `uv run pytest tests/integration/test_stack.py -k test_make_up_brings_stack_healthy`

**C2** - Com senha errada só no `migrate`, `make up` sai com código diferente de 0 e `backend`, `bff` e `web` não têm container em execução; com a senha certa, a ordem declarada é `db` healthy → `migrate` completed → `backend` healthy → `bff` healthy → `web` (AC 2)
Proof: `uv run pytest tests/integration/test_stack.py -k test_migrate_failure_stops_stack`
Proof: `uv run pytest tests/repo/test_compose.py -k test_depends_on_chain`

**C3** - O `compose.yaml` só declara `ports` no serviço `web`, com o valor `8080`; `bff`, `backend`, `db` e `migrate` não têm `ports` (AC 3)
Proof: `uv run pytest tests/repo/test_compose.py -k test_only_web_publishes_8080`

**C4** - `web` está em `public`, `bff` em `public` e `internal`, `backend` em `internal` e `data`, `db` e `migrate` só em `data`; `data` tem `internal: true` e `internal` não tem essa opção (AC 4)
Proof: `uv run pytest tests/repo/test_compose.py -k test_networks_match_tdd`

**C5** - Nenhuma variável com `MYSQL` ou `DATABASE` no nome ou no valor aparece em `bff` e `web`; `db`, `backend` e `migrate` recebem as credenciais (AC 5)
Proof: `uv run pytest tests/repo/test_compose.py -k test_credentials_scope`

**C6** - `GET /health/live` responde `200` e `{"status":"ok"}` em `backend` e `bff` sem chamar as dependências, inclusive com o banco parado (AC 6)
Proof: `uv run pytest services/backend/tests/test_backend_health.py -k test_live_ignores_database`
Proof: `uv run pytest services/bff/tests/test_bff_health.py -k test_live_ignores_backend`
Proof: `uv run pytest tests/integration/test_stack.py -k test_live_answers_with_database_stopped`

**C7** - `GET /health/ready` do `backend` responde `200` e `{"status":"ok"}` com o banco acessível, e `503` com `application/problem+json` e `code` igual a `not_ready` com o banco inacessível (AC 7)
Proof: `uv run pytest services/backend/tests/test_backend_health.py -k test_ready`
Proof: `uv run pytest tests/integration/test_stack.py -k test_ready_reports_database_stopped`

**C8** - `GET /health/ready` do `bff` responde `200` com o backend em `200`, e `503` com `code` igual a `not_ready` com o backend em `503`, `500`, recusando conexão ou sem resposta; o cliente usa timeout de 5 s (AC 8)
Proof: `uv run pytest services/bff/tests/test_bff_health.py -k test_ready`

**C9** - `GET /` na porta 8080 responde `200` com o HTML da SPA, e o teste de componente encontra o título `Quadralug` (AC 9)
Proof: `cd web && npx vitest run src/App.test.tsx -t "mostra o título Quadralug"`
Proof: `uv run pytest tests/integration/test_stack.py -k test_web_serves_spa`

**C10** - `id -u` em `backend` e `bff` é diferente de 0, e os Dockerfiles instalam dependências com `uv sync --frozen` (AC 10)
Proof: `uv run pytest tests/integration/test_stack.py -k test_images_run_as_non_root`
Proof: `uv run pytest tests/repo/test_dockerfiles.py -k test_python_images_use_frozen_sync`

**C11** - Depois de `make up`, as imagens de `backend`, `bff` e `web` têm como tag o commit curto do `HEAD` (AC 11)
Proof: `uv run pytest tests/integration/test_stack.py -k test_images_tagged_with_short_commit`

**C12** - `make down` remove os containers e mantém o volume do MySQL (AC 12)
Proof: `uv run pytest tests/integration/test_stack.py -k test_make_down_keeps_volume`

### S2 - Uma requisição pode ser seguida

**C13** - Uma requisição ao `/health/ready` do `bff` deixa nos logs de `bff` e `backend` o mesmo `trace_id` de 32 caracteres hexadecimais: o `trace_id` recebido em `traceparent`, ou um novo quando não há cabeçalho (AC 13)
Proof: `uv run pytest tests/integration/test_stack.py -k test_trace_id_crosses_services`

**C14** - Cada log é uma linha JSON com as 8 chaves `timestamp`, `severity_text`, `severity_number`, `body`, `trace_id`, `span_id`, `resource` e `attributes`, e `timestamp` em UTC terminado em `Z`; `WARNING` tem `severity_number` 13, log fora de span tem `trace_id` e `span_id` nulos, e mensagem com quebra de linha continua em uma linha (AC 14)
Proof: `uv run pytest packages/observability/tests/test_json_formatter.py -k test_log_contract`
Proof: `uv run pytest tests/integration/test_stack.py -k test_every_service_line_is_json`

**C15** - O `resource` de cada log tem `service.name` igual a `quadralug-bff` ou `quadralug-backend` e `deployment.environment` igual ao valor de `DEPLOYMENT_ENVIRONMENT` (AC 15)
Proof: `uv run pytest packages/observability/tests/test_json_formatter.py -k test_resource_attributes`
Proof: `uv run pytest tests/integration/test_stack.py -k test_logs_carry_resource`
Proof: `uv run pytest tests/repo/test_compose.py -k test_observability_env_reaches_service`

**C16** - Ao terminar uma requisição, o serviço registra um log INFO com `http.request.method`, `http.route` com o molde da rota, `http.response.status_code` e `duration_ms`; uma exceção não tratada registra status `500` (AC 16)
Proof: `uv run pytest packages/observability/tests/test_request_log.py -k test_request_log`

**C17** - Os 7 últimos segmentos `password`, `password_hash`, `token`, `cookie`, `set-cookie`, `authorization` e `email`, sem diferenciar maiúsculas, trazem `[REDACTED]` no valor, inclusive em dict aninhado; `Email` e `http.request.header.cookie` são redigidos e `enduser.id` é preservado (AC 17)
Proof: `uv run pytest packages/observability/tests/test_redaction.py -k test_redaction`

**C18** - Com `OTEL_EXPORTER_OTLP_ENDPOINT` definido, spans chegam em `POST /v1/traces` nesse endereço; sem a variável, ou com ela vazia, nenhum exportador OTLP é criado (AC 18)
Proof: `uv run pytest packages/observability/tests/test_otlp_export.py -k test_otlp`
Proof: `uv run pytest tests/repo/test_compose.py -k test_observability_env_reaches_service`

### S3 - O gate local recusa código fora do padrão

**C19** - `make check` executa ruff, mypy, import-linter, pytest e Vitest e sai com 0 só se os 5 passarem: cada um falhando sozinho leva a código diferente de 0, e uma violação real de ruff faz o ruff sair com código diferente de 0 (AC 19)
Proof: `uv run pytest tests/repo/test_makefile.py -k test_make_check`
Proof: `uv run pytest tests/repo/test_quality_gates.py -k test_ruff_rejects_planted_violation`

**C20** - Uma função sem anotação em módulo de `domain` ou `application` faz o mypy sair com código diferente de 0 (AC 20)
Proof: `uv run pytest tests/repo/test_quality_gates.py -k test_mypy_rejects_untyped_function`

**C21** - `lint-imports` sai com código diferente de 0 e cita o contrato violado nos 6 casos: `identity.domain` importa `fastapi`, `sqlalchemy` ou `pydantic`, `identity.application` importa `identity.infrastructure`, `identity` importa `weather`, e `quadralug_bff.application` importa `quadralug_bff.interface`; sem violação, sai com 0 (AC 21)
Proof: `uv run pytest tests/repo/test_quality_gates.py -k test_import_contract`

**C22** - `tools/mutation_gate.py` sai com 0 para 80 de 100 e com código diferente de 0 para 79 de 100, 0 mutantes e relatório ausente; `make mutation` executa esse script (AC 22)
Proof: `uv run pytest tests/repo/test_mutation_gate.py -k test_gate`
Proof: `uv run pytest tests/repo/test_makefile.py -k test_make_mutation_runs_gate`
Proof: `uv run pytest tests/integration/test_mutation_real.py -k test_make_mutation_real`

### S4 - As regras de branch valem antes do GitHub

**C23** - `.githooks/pre-commit` aceita `feature/x` e recusa `main`, `develop`, `release/0.1.0`, `featurex` e `HEAD` destacado, citando a branch atual (AC 23)
Proof: `uv run pytest tests/repo/test_hooks.py -k test_pre_commit`

**C24** - `.githooks/pre-push` aceita `feature/x` e recusa `feature/x:develop` e uma tag, com código diferente de 0, em um `git push` real para um repositório local (AC 24)
Proof: `uv run pytest tests/repo/test_hooks.py -k test_pre_push`

**C25** - `make setup` define `core.hooksPath` como `.githooks`, cria `.env` igual ao `.env.example` e, se o `.env` já existir, não muda o conteúdo dele (AC 25)
Proof: `uv run pytest tests/repo/test_makefile.py -k test_make_setup`

**C26** - Um `git push --no-verify` real para `develop` e para `main`, a partir de um clone temporário, é recusado pelo GitHub com mensagem que cita a regra do repositório (AC 26)
Proof: `uv run pytest tests/integration/test_github_rules.py -k test_github_refuses_direct_push`

### S5 - O GitHub Actions orquestra a promoção

**C27** - `tools/git_policy.py` sai com 0 só para `feature/*` → `develop`, `main` → `develop`, `feature/*` → `release/*` e `release/*` → `main`; recusa `develop` → `main`, `feature/x` → `main`, `release/0.1.0` → `develop` e qualquer PR de fork (AC 27)
Proof: `uv run pytest tests/repo/test_git_policy.py -k test_pr_route`

**C28** - O workflow `ci` dispara em `pull_request` para `develop` e `release/**`, e o job `ci` executa `tools/git_policy.py`, `make check` e `make integration` (AC 28)
Proof: `uv run pytest tests/repo/test_workflows.py -k test_ci_workflow`

**C29** - O workflow `release-gate` dispara em `pull_request` para `main`, e o job `release-gate` executa `tools/git_policy.py`, `make check` e `make integration` (AC 29)
Proof: `uv run pytest tests/repo/test_workflows.py -k test_release_gate_workflow`

**C30** - `0.1.0` é aceita; `v0.1.0`, `0.1` e `0.1.0-rc1` são recusadas; uma versão cuja branch ou tag já exista no remoto é recusada; e o workflow `open-release` valida antes de criar a branch (AC 30)
Proof: `uv run pytest tests/repo/test_git_policy.py -k test_release_version`
Proof: `uv run pytest tests/repo/test_workflows.py -k test_open_release_validates_first`

**C31** - O workflow `open-release` cria `refs/heads/release/$VERSION` a partir do SHA de `develop` e abre um PR com base `main` e head `release/$VERSION` (AC 31)
Proof: `uv run pytest tests/repo/test_workflows.py -k test_open_release_creates_branch_and_pr`

**C32** - Para um PR mesclado de `release/0.1.0` do próprio repositório, a tag calculada é `v0.1.0`, criada no `merge_commit_sha`; PR fechado sem merge, origem fora de `release/*` e PR de fork não geram tag (AC 32)
Proof: `uv run pytest tests/repo/test_git_policy.py -k test_tag_for_merge`
Proof: `uv run pytest tests/repo/test_workflows.py -k test_tag_release_workflow`

**C33** - Em um repositório git real, uma release com commit ausente de `develop` pede o PR de `main` para `develop`, e uma release sem commit novo não pede (AC 33)
Proof: `uv run pytest tests/repo/test_git_policy.py -k test_release_needs_backmerge`
Proof: `uv run pytest tests/repo/test_workflows.py -k test_tag_release_opens_backmerge_conditionally`

**C34** - Os 4 workflows declaram `permissions`, cada `uses` é fixado em SHA de 40 caracteres, nenhum `run` contém `${{ github.` ou `${{ inputs.`, e `actionlint` sai com 0 (AC 34)
Proof: `uv run pytest tests/repo/test_workflows.py -k test_workflow_hardening`

**C35** - `PROMOTION_TOKEN` aparece só em `open-release.yml` e `tag-release.yml` (AC 35)
Proof: `uv run pytest tests/repo/test_workflows.py -k test_promotion_token_scope`

**C36** - O `AGENTS.md` declara `mutations: 3`, o nível de teste por camada, as regras de branch, a autorização de push pelo OK da Parada 2 e o trailer `Co-Authored-By`, e o `CLAUDE.md` aponta para ele (AC 36)
Proof: `uv run pytest tests/repo/test_agents_md.py -k test_agents_md`

### Portas e alvos de make

**C37** - O repositório tem `services/backend`, `services/bff`, `packages/observability`, `web` e `tools`, um único `uv.lock` na raiz, Dockerfiles com contexto na raiz e os 8 pacotes `{identity,weather}/{domain,application,infrastructure,interface}` (door 1)
Proof: `uv run pytest tests/repo/test_layout.py -k test_layout`

**C38** - `packages/observability` depende de `opentelemetry-sdk`, das instrumentações de FastAPI, httpx e SQLAlchemy e de `opentelemetry-exporter-otlp-proto-http`, e não depende de `structlog` (door 4)
Proof: `uv run pytest tests/repo/test_layout.py -k test_observability_stack`

**C39** - `make e2e` sai com código diferente de 0 e diz que ainda não há suíte (Out of scope)
Proof: `uv run pytest tests/repo/test_makefile.py -k test_make_e2e_reports_no_suite`

**C40** - O nome dos jobs `ci` e `release-gate` não muda sem atualizar o ruleset: `ci.yml` tem exatamente o job `ci`, e `release-gate.yml` exatamente o job `release-gate` (door 3)
Proof: `uv run pytest tests/repo/test_workflows.py -k test_required_check_job_names`

**C41** - Os logs de `backend` e `bff` no stack real não têm nenhuma linha com `severity_number` 17 ou maior (achado no `/simplify`: o backend registrava um ERROR a cada boot ao instrumentar um `httpx` que ele não tem)
Proof: `uv run pytest tests/integration/test_stack.py -k test_boot_logs_no_errors`

## Coverage

| Set (size) | Member -> proof | Unproven |
| --- | --- | --- |
| `GET /health/live` statuses, backend e bff (2) | backend 200 C6 · bff 200 C6 | - |
| `GET /health/ready` statuses, backend (2) | 200 C7 · 503 C7 | - |
| `GET /health/ready` statuses, bff (2) | 200 C8 · 503 C8 | - |
| `GET /` statuses, web (1) | 200 C9 | - |
| falhas do backend vistas pelo bff (4) | `503` C8 · `500` C8 · conexão recusada C8 · timeout de 5 s C8 | - |
| serviços do Compose (5) | `db` C1 · `migrate` C1 · `backend` C1 · `bff` C1 · `web` C1 | - |
| redes, por serviço (5) | `web` C4 · `bff` C4 · `backend` C4 · `db` C4 · `migrate` C4 | - |
| chaves do log (8) | `timestamp` C14 · `severity_text` C14 · `severity_number` C14 · `body` C14 · `trace_id` C14 · `span_id` C14 · `resource` C14 · `attributes` C14 | - |
| segmentos redigidos (7) | `password` C17 · `password_hash` C17 · `token` C17 · `cookie` C17 · `set-cookie` C17 · `authorization` C17 · `email` C17 | - |
| ferramentas de `make check` (5) | ruff C19 · mypy C19 · import-linter C19 · pytest C19 · Vitest C19 | - |
| violações de import (6) | `fastapi` C21 · `sqlalchemy` C21 · `pydantic` C21 · application → infrastructure C21 · identity → weather C21 · bff application → interface C21 | - |
| meta de mutação, AC 22 (4 exemplos) | 80 de 100 C22 · 79 de 100 C22 · 0 mutantes C22 · relatório ausente C22 | - |
| refs do pre-commit (6) | `feature/x` C23 · `main` C23 · `develop` C23 · `release/0.1.0` C23 · `featurex` C23 · `HEAD` destacado C23 | - |
| refs do pre-push (3) | `feature/x` C24 · `feature/x:develop` C24 · tag C24 | - |
| rotas de PR aceitas (4) | `feature/*` → `develop` C27 · `main` → `develop` C27 · `feature/*` → `release/*` C27 · `release/*` → `main` C27 | - |
| rotas de PR recusadas (4) | `develop` → `main` C27 · `feature/x` → `main` C27 · `release/0.1.0` → `develop` C27 · fork C27 | - |
| versões, AC 30 (4) | `0.1.0` C30 · `v0.1.0` C30 · `0.1` C30 · `0.1.0-rc1` C30 | - |
| workflows (4) | `ci` C28 · `release-gate` C29 · `open-release` C31 · `tag-release` C32 | - |
| alvos de `make` (7) | `setup` C25 · `up` C1 · `down` C12 · `check` C19 · `integration` C28 · `mutation` C22 · `e2e` C39 | - |
| portas do plano (5) | layout C37 · contrato de log C14 · nomes dos checks C40 · stack de observabilidade C38 · fluxo de release C27 | - |
| startup config: JSON e OTel (2 assemblies) | `backend` C13 · `bff` C13 | - |

- Claims que citam status, rota ou forma de resposta: C6, C7, C8 e C9 têm prova que cruza HTTP, e C6, C7 e C9 também passam pelo stack real
- C27 a C35 têm prova estática e por script no `HEAD`; a execução real dos workflows fica nas etapas 11 a 13 do `plan.md` da raiz, como confirmado nas Assumptions

## Swept

- validation: C27, C30
- failure modes: C2, C8
- idempotency: C25, C30
- authorization: C3, C5, C26, C34, C35
- concurrency: n/a - nenhum serviço tem estado compartilhado nesta fase, e duas execuções de `open-release` da mesma versão disputam a criação da mesma ref, que o GitHub só aceita uma vez (C30)
- data lifecycle: C12
- dependency failure: C7, C8
- state transitions: C2, C33
- observability: C13, C14, C15, C16, C17, C18, C41

## Handoff

- **Settled mid-build:** none
- **Dispatched:** Verifier, no `HEAD` 4948023
- **Boundary:** C1-C41 fechados no commit que adiciona esta linha
- **Abandoned:** do `/code-review high`, 2 achados ficam de fora: (a) `check-pr` roda a política do próprio PR, e carregar a política da base quebraria o PR da F0, porque `develop` ainda não tem `tools/`, então a correção entra na F1; (b) `open-release` e `tag-release` não são idempotentes em reexecução, e a recuperação é manual. O `make mutation` cobre só `services/backend`, e o BFF entra na F4, com o `BuildHome`
- **Walked:** n/a - a F0 não tem tela além do título; C9 cobre o `GET /` no stack real
