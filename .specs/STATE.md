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
| AD-010 | O mutmut roda dentro de cada serviço, com `source_paths = ["src"]` e `do_not_mutate` para o que não é `domain` nem `application`. O BFF entra em `make mutation` na F4 | Na raiz, ou apontando só para `domain`, o pacote instalado vence o código mutado e o resultado é 0 mortos | active | 2026-11-02 |
| AD-011 | `sqlalchemy` fica em `>=2.0,<2.1` | A instrumentação OTel recusa 2.1 e se desliga, deixando só um ERROR no boot | active | 2026-11-02 |
| AD-012 | Cada serviço só instrumenta o cliente que tem: `quadralug_observability.database` no backend e `.http_client` no BFF. A F3 passa a chamar `instrument_http_clients` no backend | O instrumentador de httpx loga ERROR quando o pacote não está instalado | active | 2026-11-02 |
| AD-013 | Rotas do BFF que chamam o backend são `async`, com `httpx.AsyncClient` e `asyncio.timeout` para o prazo total. O backend segue síncrono | O timeout do httpx vale por operação, e uma resposta em partes passava de 5 s | active | 2026-11-02 |
