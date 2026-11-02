# Quadralug

Plataforma de aluguel de quadras em Salvador, BA. Projeto de estudo com qualidade de produção.

- Produto: `.prd/quadralug-conta-e-home.md`
- Arquitetura: `.tdd/quadralug-conta-e-home.md`
- Fases e fluxo: `plan.md`
- Decisões: `.specs/STATE.md`

## tlc-spec-lean

mutations: 3

## Comandos

| Comando | O que faz |
| --- | --- |
| `make setup` | Aponta `core.hooksPath` para `.githooks`, cria `.env` e instala as dependências |
| `make up` e `make down` | Sobem e removem o ambiente; `make down` mantém o volume do MySQL |
| `make check` | Gate local: ruff, mypy, import-linter, testes unitários e Vitest |
| `make integration` | Testes com o stack real em Docker |
| `make mutation` | mutmut, comparado com a meta por `tools/mutation_gate.py` |
| `make e2e` | Playwright, a partir da F5 |

## Nível de teste por camada

| Camada | Nível |
| --- | --- |
| `domain` e `application` | Unitário com AAA e FIRST, Hypothesis e mutmut |
| `infrastructure` | Integração |
| `interface` | Rota por HTTP, com portas falsas ou respx |
| Regra de dependência | import-linter |
| Compose, workflows e hooks | Testes em `tests/repo`; o que depende do stack, em `tests/integration` |
| SPA | Vitest e Testing Library; jornada completa em Playwright |

Código que só repassa argumentos não precisa de teste próprio.

## Branches

- O fluxo é `feature/*` → `develop` → `release/x.y.z` → `main`.
- Commit e push só acontecem em `feature/*`. As outras branches mudam apenas por PR.
- O merge é sempre *merge commit*, e quem faz é o autor.
- Cada fase gera uma release, e a tag `vX.Y.Z` nasce em `main` pelo Actions.

## Push

O Claude só faz push de uma feature depois do OK da Parada 2, o relatório ao autor. Esse OK também cobre os commits de correção de CI na mesma feature e o PR temporário de prova da etapa 11.

## Commits

- Mensagens em Conventional Commits, em português.
- Todo commit feito pelo Claude termina com o trailer `Co-Authored-By`.
- Nenhum e-mail pessoal em commits ou arquivos versionados (AD-005).
