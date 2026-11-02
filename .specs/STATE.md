# Project state

## Decisions

| ID | Decision | Rationale | Status | Date |
| --- | --- | --- | --- | --- |
| AD-001 | Código evolui por `feature/*` → `develop` → `release/x.y.z` → `main`. Commit e push só em `feature/*`; o resto muda por PR | Pedido do autor na revisão do `plan.md`; a promoção fica visível e imposta pelo GitHub | active | 2026-10-31 |
| AD-002 | Merge sempre por *merge commit*, nos três níveis; squash e rebase ficam desligados | Preserva os commits avaliados pelo Verifier | active | 2026-10-31 |
| AD-003 | Cada fase gera uma release: Fase N → `0.(N+1).0`, Fase 6 → `1.0.0`. Tag `vX.Y.Z` em `main` | Autor escolheu "uma release por fase" | active | 2026-10-31 |
| AD-004 | Claude faz push e abre PR depois do OK da Parada 2; o autor faz todos os merges | Autor escolheu "Claude push e PR; você faz merge" | active | 2026-10-31 |
| AD-005 | Nenhum e-mail pessoal em arquivos versionados ou em commits. Commits usam o *noreply* do GitHub via `user.email` local | O autor removeu o e-mail do TDD antes de o repositório virar público; o PRD e a identidade dos commits foram alinhados a isso | active | 2026-10-31 |
| AD-006 | A rede `internal` tem saída para a internet, e só `data` é `internal: true` | O Compose não filtra saída por destino, e o backend precisa alcançar a Open-Meteo. O risco fica registrado | active | 2026-10-31 |
| AD-007 | Config OTel compartilhada fica em `packages/observability`, no workspace uv, com build Docker a partir da raiz | BFF e backend precisam do mesmo formato de log e da mesma propagação | active | 2026-10-31 |
| AD-008 | GitHub Actions entra na V1 para CI e promoção de branches; deploy em nuvem continua fora | Pedido do autor; substitui a exclusão de CI/CD remoto da §3 do TDD | active | 2026-10-31 |
| AD-009 | Os checks obrigatórios se chamam `ci` e `release-gate`. Renomear um job exige atualizar os rulesets no mesmo PR | Os rulesets referenciam o nome do job | active | 2026-10-31 |
