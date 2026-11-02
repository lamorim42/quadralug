# f0-fundacao proofs

**HEAD**: 0bfe5fe
**Tree**: clean
**Result**: 62 pass, 0 fail; mutations 3 killed, 0 not

| Check | Proof | Ran | Passed | Result |
| --- | --- | --- | --- | --- |
| C1 | `uv run pytest tests/integration/test_stack.py -k test_make_up_brings_stack_healthy` | 1 | 1 | pass |
| C2 | `uv run pytest tests/integration/test_stack.py -k test_migrate_failure_stops_stack` | 1 | 1 | pass |
| C2 | `uv run pytest tests/repo/test_compose.py -k test_depends_on_chain` | 4 | 4 | pass |
| C3 | `uv run pytest tests/repo/test_compose.py -k test_only_web_publishes_8080` | 1 | 1 | pass |
| C4 | `uv run pytest tests/repo/test_compose.py -k test_networks_match_tdd` | 6 | 6 | pass |
| C5 | `uv run pytest tests/repo/test_compose.py -k test_credentials_scope` | 5 | 5 | pass |
| C6 | `uv run pytest services/backend/tests/test_backend_health.py -k test_live_ignores_database` | 1 | 1 | pass |
| C6 | `uv run pytest services/bff/tests/test_bff_health.py -k test_live_ignores_backend` | 1 | 1 | pass |
| C6 | `uv run pytest tests/integration/test_stack.py -k test_live_answers_with_database_stopped` | 2 | 2 | pass |
| C7 | `uv run pytest services/backend/tests/test_backend_health.py -k test_ready` | 4 | 4 | pass |
| C7 | `uv run pytest tests/integration/test_stack.py -k test_ready_reports_database_stopped` | 1 | 1 | pass |
| C8 | `uv run pytest services/bff/tests/test_bff_health.py -k test_ready` | 9 | 9 | pass |
| C9 | `cd web && npx vitest run src/App.test.tsx -t "mostra o título Quadralug"` | 1 | 1 | pass |
| C9 | `uv run pytest tests/integration/test_stack.py -k test_web_serves_spa` | 1 | 1 | pass |
| C10 | `uv run pytest tests/integration/test_stack.py -k test_images_run_as_non_root` | 2 | 2 | pass |
| C10 | `uv run pytest tests/repo/test_dockerfiles.py -k test_python_images_use_frozen_sync` | 2 | 2 | pass |
| C11 | `uv run pytest tests/integration/test_stack.py -k test_images_tagged_with_short_commit` | 3 | 3 | pass |
| C12 | `uv run pytest tests/integration/test_stack.py -k test_make_down_keeps_volume` | 1 | 1 | pass |
| C13 | `uv run pytest tests/integration/test_stack.py -k test_trace_id_crosses_services` | 2 | 2 | pass |
| C14 | `uv run pytest packages/observability/tests/test_json_formatter.py -k test_log_contract` | 19 | 19 | pass |
| C14 | `uv run pytest tests/integration/test_stack.py -k test_every_service_line_is_json` | 2 | 2 | pass |
| C15 | `uv run pytest packages/observability/tests/test_json_formatter.py -k test_resource_attributes` | 4 | 4 | pass |
| C15 | `uv run pytest tests/integration/test_stack.py -k test_logs_carry_resource` | 2 | 2 | pass |
| C15 | `uv run pytest tests/repo/test_compose.py -k test_observability_env_reaches_service` | 4 | 4 | pass |
| C16 | `uv run pytest packages/observability/tests/test_request_log.py -k test_request_log` | 3 | 3 | pass |
| C17 | `uv run pytest packages/observability/tests/test_redaction.py -k test_redaction` | 28 | 28 | pass |
| C18 | `uv run pytest packages/observability/tests/test_otlp_export.py -k test_otlp` | 7 | 7 | pass |
| C18 | `uv run pytest tests/repo/test_compose.py -k test_observability_env_reaches_service` | 4 | 4 | pass |
| C19 | `uv run pytest tests/repo/test_makefile.py -k test_make_check` | 9 | 9 | pass |
| C19 | `uv run pytest tests/repo/test_quality_gates.py -k test_ruff_rejects_planted_violation` | 1 | 1 | pass |
| C20 | `uv run pytest tests/repo/test_quality_gates.py -k test_mypy_rejects_untyped_function` | 5 | 5 | pass |
| C21 | `uv run pytest tests/repo/test_quality_gates.py -k test_import_contract` | 17 | 17 | pass |
| C22 | `uv run pytest tests/repo/test_mutation_gate.py -k test_gate` | 7 | 7 | pass |
| C22 | `uv run pytest tests/repo/test_makefile.py -k test_make_mutation_runs_gate` | 4 | 4 | pass |
| C22 | `uv run pytest tests/integration/test_mutation_real.py -k test_make_mutation_real` | 2 | 2 | pass |
| C23 | `uv run pytest tests/repo/test_hooks.py -k test_pre_commit` | 6 | 6 | pass |
| C24 | `uv run pytest tests/repo/test_hooks.py -k test_pre_push` | 4 | 4 | pass |
| C25 | `uv run pytest tests/repo/test_makefile.py -k test_make_setup` | 2 | 2 | pass |
| C26 | `uv run pytest tests/integration/test_github_rules.py -k test_github_refuses_direct_push` | 2 | 2 | pass |
| C27 | `uv run pytest tests/repo/test_git_policy.py -k test_pr_route` | 17 | 17 | pass |
| C28 | `uv run pytest tests/repo/test_workflows.py -k test_ci_workflow` | 5 | 5 | pass |
| C29 | `uv run pytest tests/repo/test_workflows.py -k test_release_gate_workflow` | 5 | 5 | pass |
| C30 | `uv run pytest tests/repo/test_git_policy.py -k test_release_version` | 12 | 12 | pass |
| C30 | `uv run pytest tests/repo/test_workflows.py -k test_open_release_validates_first` | 1 | 1 | pass |
| C31 | `uv run pytest tests/repo/test_workflows.py -k test_open_release_creates_branch_and_pr` | 1 | 1 | pass |
| C32 | `uv run pytest tests/repo/test_git_policy.py -k test_tag_for_merge` | 7 | 7 | pass |
| C32 | `uv run pytest tests/repo/test_workflows.py -k test_tag_release_workflow` | 3 | 3 | pass |
| C33 | `uv run pytest tests/repo/test_git_policy.py -k test_release_needs_backmerge` | 4 | 4 | pass |
| C33 | `uv run pytest tests/repo/test_workflows.py -k test_tag_release_opens_backmerge_conditionally` | 1 | 1 | pass |
| C34 | `uv run pytest tests/repo/test_workflows.py -k test_workflow_hardening` | 13 | 13 | pass |
| C35 | `uv run pytest tests/repo/test_workflows.py -k test_promotion_token_scope` | 1 | 1 | pass |
| C36 | `uv run pytest tests/repo/test_agents_md.py -k test_agents_md` | 7 | 7 | pass |
| C37 | `uv run pytest tests/repo/test_layout.py -k test_layout` | 18 | 18 | pass |
| C38 | `uv run pytest tests/repo/test_layout.py -k test_observability_stack` | 1 | 1 | pass |
| C39 | `uv run pytest tests/repo/test_makefile.py -k test_make_e2e_reports_no_suite` | 1 | 1 | pass |
| C40 | `uv run pytest tests/repo/test_workflows.py -k test_required_check_job_names` | 2 | 2 | pass |
| C41 | `uv run pytest tests/integration/test_stack.py -k test_boot_logs_no_errors` | 2 | 2 | pass |
| Build | `uv run ruff check .` | - | - | pass |
| Build | `uv run ruff format --check .` | - | - | pass |
| Build | `uv run mypy` | - | - | pass |
| Build | `uv run lint-imports` | - | - | pass |
| Build | `cd web && npm run build` | - | - | pass |

## Mutations

| Mutation | Location | Killed |
| --- | --- | --- |
| C17 redact para de descer em tuple: list \ | `tuple -> list` | yes |
| C18 serviço ignora o endpoint OTLP: os.environ -> {} em configure_observability | `packages/observability/src/quadralug_observability/setup.py:45` | yes |
| C27/C29 release-gate deixa de ver fork: head.repo.full_name -> github.repository | `.github/workflows/release-gate.yml:24` | yes |
