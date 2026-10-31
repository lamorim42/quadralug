# Plano de execução: Quadralug — Conta e Home

## Contexto

O PRD está fechado e o TDD (Draft) define arquitetura, testes e 7 fases. O diretório só tem documentos e skills: não há código nem repositório git. O objetivo é construir a fase inteira com testes e review, terminando com os 12 estados da *Journey* do PRD provados por E2E.

Decisões do autor nesta sessão:

- **Claude implementa tudo**, e o autor aprova cada fase.
- **`tlc-spec-lean` em cada fase**. Cada fase do TDD vira uma feature com `plan.md`, `checks.md`, build e Verifier independente.
- **Fluxo `feature/*` → `develop` → `release/*` → `main`**, orquestrado pelo GitHub Actions em um repositório público. Cada fase gera uma release, e os merges são sempre do autor.

O PRD não é reaberto. O TDD é seguido, com os ajustes listados abaixo.

## Pré-requisitos

Precisam ser resolvidos antes da Fase 0. Os dois primeiros exigem `sudo`, e o login do `gh` usa o navegador, então o autor roda:

| Falta              | Comando                                             | Motivo                                                                     |
| ------------------ | --------------------------------------------------- | -------------------------------------------------------------------------- |
| `docker compose` | `sudo apt install docker-compose-v2`              | Só o Docker Engine 29.1.3 está instalado; o plugin compose não existe   |
| `gh`             | `sudo apt install gh && gh auth login`            | Cria o repositório, abre PRs e configura o GitHub; o `gh` não está instalado |
| `uv`             | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Gerencia dependências e lockfile, e baixa o Python 3.13 (o host tem 3.12) |

O Playwright roda em container, em `compose.e2e.yaml`, para não exigir `sudo` nem dependências de navegador no host.

## Fluxo de cada fase

Ao aprovar este plano, o autor autoriza `git init`, commits locais em `feature/*`, a criação do repositório público `quadralug` e o bootstrap descrito abaixo. O push de cada fase depende do OK da Parada 2.

1. **Branch** `feature/fase-N-nome`, a partir de `develop` atualizada.
2. **Plano**: `.specs/features/fN-nome/plan.md`, com critérios EARS, *path*, portas de mão única e os estados da Journey daquela fase. Roda `validate_plan.py`.
3. **Parada 1, aprovação do autor**: a aprovação entra no `plan.md` com as palavras do autor.
4. **Checks**: `checks.md`, com provas, coverage e as nove dimensões. Roda `validate_checks.py`.
5. **Build**: testes escritos a partir dos checks, depois o código. Commits em Conventional Commits, validados com `check_commit.py`.
6. **Testes**: `make check` e as suítes da fase ficam verdes.
7. **Review de código**: `/simplify`, depois `/code-review high` sobre o diff `develop...HEAD`. `/security-review` entra nas fases 2, 4, 5 e 6. Os achados viram commits nesta etapa, porque o Verifier precisa ler o `HEAD` final.
8. **Verificação independente**: `check_proofs.py`, depois um Verifier em sub-agente novo, que não lê o Handoff, com 3 mutações. A correção é feita de uma vez, seguida de `check_proofs.py --mutations`.
9. **Gate**: `validate_verification.py` sai com 0, e as lições são registradas com `lessons.py`.
10. **Parada 2, relatório ao autor**: resultado do gate, provas, desvios e os 3 arquivos que mais valem a leitura para o aprendizado. Com o OK, Claude faz o push da feature e abre o PR para `develop`.
11. **PR para `develop`**: a CI roda, e o autor faz o merge quando ela fica verde. Se a CI falhar, a correção é um commit na mesma feature, que repete as etapas 6, 8 e 9 antes do novo push, coberto pelo mesmo OK.
12. **Release**: o autor aciona o `open-release.yml`, que cria `release/x.y.z` a partir de `develop` e abre o PR para `main`.
13. **PR para `main`**: o gate de release roda, e o autor faz o merge. O `tag-release.yml` cria a tag `vX.Y.Z`. A fase só fecha aqui, e a próxima parte de `develop`.

As fases rodam em sequência, inclusive 2 e 3: `check_proofs.py` exige árvore limpa em um `HEAD` único, então paralelizar não compensa.

### Branches

| Branch            | Papel                | Como recebe código                                              |
| ----------------- | -------------------- | ----------------------------------------------------------------- |
| `feature/*`     | Trabalho de uma fase | Commits locais e push. É a única branch em que isso acontece     |
| `develop`       | Integração           | PR de `feature/*`, ou de `main` quando uma release teve correção |
| `release/x.y.z` | Candidata à entrega  | Criada pelo Actions a partir de `develop`; correção só por PR de `feature/*` |
| `main`          | Código entregue      | PR de `release/*`                                                  |

- **Versão**: a Fase N gera `release/0.(N+1).0`, de `0.1.0` na Fase 0 a `0.6.0` na Fase 5. A Fase 6 gera `release/1.0.0`.
- **Merge**: sempre *merge commit*, nos três níveis. Squash e rebase ficam desligados para preservar os commits avaliados pelo Verifier.
- **Correção em release**: sai de `feature/fix-*`, criada a partir da `release/x.y.z`, passa pelas etapas 5 a 10 e abre o PR para a release. Depois do merge em `main`, o `tag-release.yml` abre o PR de `main` para `develop`, para a correção não se perder.
- **Regra local**: `.githooks/pre-commit` recusa commits fora de `feature/*`, e `.githooks/pre-push` recusa push de outras branches.
- **Regra no GitHub**: `develop`, `main` e `release/*` exigem PR e CI verde e recusam push direto e force push, inclusive de administradores. Nenhuma aprovação é exigida, porque o GitHub não deixa quem abriu o PR aprová-lo, e os PRs saem da conta do autor.
- **Limpeza**: as branches `feature/*` e `release/*` são apagadas depois do merge. A tag preserva cada release.

### GitHub Actions

| Workflow             | Gatilho                              | O que faz                                                                                                     |
| -------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `ci.yml`           | PR para `develop` e `release/*`  | Valida a branch de origem, roda `make check` e `make integration`                                          |
| `release-gate.yml` | PR para `main`                     | Valida que a origem é `release/*`, roda `make check`, `make integration`, `make mutation` e `make e2e` |
| `open-release.yml` | Manual (`workflow_dispatch`), com a versão | Cria `release/x.y.z` a partir de `develop` e abre o PR para `main`                                       |
| `tag-release.yml`  | Push em `main`                     | Cria a tag `vX.Y.Z`. Se `main` tiver diferenças em relação a `develop`, abre o PR de `main` para `develop` |

- **Token**: `open-release.yml` e `tag-release.yml` usam o secret `PROMOTION_TOKEN`, porque um PR aberto com o `GITHUB_TOKEN` não dispara a CI. É um *fine-grained token* limitado a este repositório, com escrita em Contents e Pull requests.
- **Suítes por fase**: `release-gate.yml` nasce na Fase 0 com `make check` e `make integration`. `make mutation` entra na Fase 1, e `make e2e` na Fase 5, junto com as suítes que eles executam.

### Bootstrap do repositório

Roda uma vez, antes da etapa 1 da Fase 0. Nenhum commit é feito fora de `feature/*`, e `main` e `develop` nascem no GitHub, sem push:

1. `git init -b feature/bootstrap`, com `.gitignore` e os documentos no primeiro commit.
2. Criar o repositório público `quadralug` e fazer o push de `feature/bootstrap`.
3. Criar `develop` e `main` a partir desse commit com `gh api`, definir `develop` como branch padrão e apagar `feature/bootstrap`.
4. Deixar só o *merge commit* habilitado, ligar a limpeza de branches e aplicar a proteção de `develop`, `main` e `release/*`.
5. O autor cria o token no navegador e o grava com `gh secret set PROMOTION_TOKEN`.

Os checks obrigatórios entram na proteção durante o PR da Fase 0, porque o GitHub só os oferece depois da primeira execução.

## Fases

| Fase | Feature                   | Entrega                                                                                           | Provas que fecham a fase                                                                                                                             | Atenção                                                                                                                        |
| ---- | ------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 0    | `f0-fundacao`           | Bootstrap do repositório, `AGENTS.md`, `CLAUDE.md`, workspace uv, tooling, Makefile, git hooks, 4 workflows, 5 serviços hello-world, OTel | `docker compose up --wait` com tudo saudável, mesmo `trace_id` nos logs de BFF e backend, import-linter falhando contra uma violação plantada, push direto em `develop` recusado, CI vermelha impedindo o merge, tag `v0.1.0` em `main` | Sem regra de negócio                                                                                                            |
| 1    | `f1-identidade-dominio` | VOs, agregados, portas, 4 casos de uso                                                            | Unitários AAA/FIRST, Hypothesis, cobertura ≥ 90%, mutmut ≥ 80%                                                                                    | Ao final, o autor decide se a meta de 80% fica (questão 4 do TDD)                                                               |
| 2    | `f2-identidade-api`     | Alembic, repositórios MySQL, Argon2id, tokens, `/v1` de contas e sessões                      | Testcontainers, `upgrade → downgrade → upgrade`, dois cadastros concorrentes, rotas com Problem Details                                          | `/security-review`                                                                                                             |
| 3    | `f3-clima`              | Domínio, cache, adapter Open-Meteo, `/v1/forecasts/weekly`                                     | Unitários, Hypothesis, respx, fuso `America/Bahia`, falha não cacheada, mutmut                                                                   | Começa gravando um payload real como fixture                                                                                    |
| 4    | `f4-bff`                | `/api`, cookie, `Origin`, `BuildHome`, cliente do backend                                   | Unitários, contrato, falha parcial, mutmut                                                                                                          | `/security-review`                                                                                                             |
| 5    | `f5-spa`                | Telas, guardas de rota, logout, nginx (proxy, CSP, rate limit, `no-store`), harness E2E         | Vitest, Playwright do caminho feliz, teste do `429` com o limite real, walk no app                                                                 | `/security-review`; sem captura, logo sem sub-agente de telas. Larguras assumidas: 360 a 1280 px, a confirmar no plano da fase |
| 6    | `f6-aceite`             | 12/12 estados em E2E, checklist da seção 5 do TDD, mutation final, TDD atualizado               | Suíte completa em ambiente limpo                                                                                                                    | `/security-review`                                                                                                             |

As fases 1 a 4 são camadas, não fatias verticais. Por isso, a pessoa só usa o produto de fato a partir da Fase 5, e a Fase 6 é a prova integrada.

### Onde cada estado da Journey é fechado

| Estados do PRD                                      | Regra | Exposição | Tela e E2E |
| --------------------------------------------------- | ----- | ----------- | ---------- |
| Criar conta: válido, e-mail duplicado, senha curta | F1    | F2, F4      | F5, F6     |
| Entrar: correto, errado                             | F1    | F2, F4      | F5, F6     |
| Home sem login, login já logado                    | F1    | F4          | F5, F6     |
| Previsão carregada, previsão indisponível        | F3    | F3, F4      | F5, F6     |
| Sair, fechar o navegador                            | F1    | F4          | F5, F6     |
| Esqueceu a senha (nenhuma opção na tela)          | —    | —          | F5, F6     |

## Ajustes ao TDD

O TDD tem contradições ou lacunas que travariam a implementação. A decisão de cada item está abaixo; ela entra no TDD e em `.specs/STATE.md` no commit da fase.

| Fase | Problema no TDD                                                                                             | Decisão                                                                                                                                              |
| ---- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0    | "Backend só sai para a Open-Meteo": o Compose não filtra saída por destino                               | O backend tem saída geral pela rede `internal`, que não pode ser `internal: true`. O risco fica registrado                                      |
| 0    | §3 deixa CI/CD remoto fora do escopo, mas o autor decidiu usar GitHub Actions                               | O GitHub Actions entra na V1 para CI e promoção de branches. Deploy em nuvem continua fora                                                          |
| 0    | `mutmut` deveria falhar o build, e o limite precisa ser conferido por script                               | `make mutation` compara o resultado com a meta e sai com erro. `make check` é o gate local, e o `release-gate.yml` roda a mutação nos PRs para `main` |
| 0    | Config OTel "compartilhada" sem local definido                                                              | Pacote `packages/observability` no workspace uv, com build Docker a partir da raiz                                                                  |
| 1    | `RegisterAccount` grava conta e sessão sem atomicidade                                                   | Nova porta `UnitOfWork`; o hash da senha é calculado antes de abrir a transação                                                                  |
| 1    | §5 pede rehash no login, mas as portas da §4.2 não permitem                                              | `PasswordHasher.needs_rehash` e `AccountRepository.update_password_hash`                                                                          |
| 1    | `reason` de `auth.login.failed` só existe no caso de uso, e `application` não pode depender de OTel | Nova porta `EventRecorder`, com *fake* que permite testar os eventos                                                                              |
| 2    | O caso de uso traduziria `IntegrityError`, o que viola a regra de dependência                            | O repositório traduz para `EmailAlreadyRegistered`                                                                                                 |
| 2    | Collation `ai_ci` faz `jose@` e `josé@` colidirem no `UNIQUE`                                      | Coluna `email` com `utf8mb4_0900_bin`. É porta de mão única                                                                                    |
| 2    | "Schemas validados dos dois lados" sem mecanismo                                                            | Snapshot `contracts/backend-v1.openapi.json`: o backend falha se divergir, e os fakes do BFF são validados contra ele                              |
| 3    | "Condição padrão" para WMO desconhecido não definida                                                    | `CLOUDY`                                                                                                                                            |
| 3    | `precipitation_probability_max` nulo derrubaria a semana inteira                                          | Tratado como payload inválido, salvo se o payload real mostrar que nulos são comuns; aí a decisão volta ao autor                                  |
| 4    | BFF sem timeout, e `/api/home` sem erro para backend fora do ar                                           | Timeout de 5 s, acima dos 3 s do clima. Falha na checagem de sessão retorna `503 service_unavailable`, sem mandar para o login                     |
| 5    | `limit_req` responde `503` por padrão e, sem `nodelay`, enfileira requisições                      | `limit_req_status 429`, `nodelay` e `error_page` em `problem+json`. Texto: "Muitas tentativas. Aguarde um minuto e tente de novo."            |
| 5    | O rate limit de 5/min por IP derrubaria os próprios E2E                                                    | Limite configurável por env, alto em `compose.e2e.yaml`; um teste à parte prova o limite real                                                     |
| 5    | Sem forma determinística de forçar "previsão indisponível"                                              | Serviço de teste `weather-stub`, só em `compose.e2e.yaml`, com `OPEN_METEO_BASE_URL` e TTL do cache 0. A produção continua com 5 containers |
| 6    | Trocar de `context` não prova "fechar o navegador"                                                       | Playwright com `launchPersistentContext`: fecha e reabre o mesmo perfil, e confirma que o cookie não tem expiração                               |

A questão 1 do TDD (LGPD) segue aberta e bloqueia uso por pessoas reais, mas não bloqueia esta fase.

## Estrutura do repositório

```
compose.yaml  compose.e2e.yaml  Makefile  pyproject.toml  uv.lock  .env.example
AGENTS.md  CLAUDE.md
.github/workflows/  .githooks/
services/backend/   src/quadralug_backend/{identity,weather}/{domain,application,infrastructure,interface}, shared/, alembic/, tests/
services/bff/       src/quadralug_bff/{interface,application,infrastructure}, tests/
packages/observability/
web/                SPA React + Vite + TS, nginx, Dockerfile
e2e/                Playwright, weather-stub
contracts/backend-v1.openapi.json
.specs/             STATE.md, LESSONS.md, features/
```

- **Makefile**: `setup` (aponta `core.hooksPath` para `.githooks`), `up`, `down`, `check` (ruff, mypy, import-linter, unitários, Vitest), `integration`, `mutation`, `e2e`.
- **Dependência adicional**: `pytest-cov`, necessária para a meta de cobertura.
- **`AGENTS.md`**: declara `mutations: 3`, o nível de teste por camada, as regras de branch, a autorização de push dada pelo OK da Parada 2 e a exigência do trailer `Co-Authored-By` nos commits, porque a skill o proíbe se o repositório não pedir. `CLAUDE.md` aponta para ele.
- **Git**: versiona `.github`, `.githooks`, `.prd`, `.tdd`, `.specs`, `Projeto.md`, `plan.md` e `.claude/skills`. Ignora `.env`, `.agents`, `.cursor` e `.windsurf`.

## Verificação final

Em ambiente limpo, ao fim da Fase 6:

1. `docker compose down -v`, `docker compose up --wait`: o `migrate` termina com sucesso e todos os serviços ficam saudáveis.
2. `make check`, `make integration`, `make mutation` e `make e2e`, todos verdes, com **12/12 estados** do PRD.
3. Cobertura ≥ 90% em `domain` e `application`, mutmut na meta e zero violações no import-linter.
4. `validate_verification.py` sai com 0 para as 7 features.
5. Fluxo manual com a Open-Meteo real: criar conta, ver hoje e os 6 dias, sair, e confirmar que voltar no navegador não reabre a home.
6. Logs conferidos: mesmo `trace_id` entre BFF e backend, sem senha, token, cookie ou e-mail em claro.
7. `release-gate.yml` verde no PR de `release/1.0.0`, merge feito pelo autor e tag `v1.0.0` criada em `main`.
