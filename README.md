# Quadralug

Plataforma de aluguel de quadras em Salvador, BA. É um projeto de estudo construído com qualidade de produção.

> **Estado atual: Fase 0 (fundação).** O ambiente completo sobe e está observável, mas ainda não existe funcionalidade de produto: não há cadastro, login nem previsão do tempo. Veja [o que já funciona](#o-que-já-funciona).

## Como rodar

### Pré-requisitos

| Ferramenta | Para quê |
| --- | --- |
| [Docker](https://docs.docker.com/engine/install/) 25 ou mais recente, com o plugin Compose | Subir os serviços |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Instalar as dependências Python e baixar o Python 3.13 |
| Node.js 22 ou mais recente, com npm | Instalar as dependências da SPA |
| `make` e `git` | Rodar os comandos do projeto |

### Subir a aplicação

```bash
git clone git@github.com:lamorim42/quadralug.git
cd quadralug
make setup
make up
```

- `make setup` instala as dependências, ativa os git hooks e cria o `.env` a partir do `.env.example`. Ele não sobrescreve um `.env` existente.
- `make up` constrói as imagens e só termina quando os serviços estão saudáveis. A primeira execução leva alguns minutos.

Depois, abra <http://localhost:8080>. A página mostra o título **Quadralug**.

### Parar a aplicação

```bash
make down               # remove os containers e mantém o banco
docker compose down -v  # remove também o volume do MySQL
```

## O que já funciona

| Funcionalidade | Como ver |
| --- | --- |
| Página web em React com o título do produto | <http://localhost:8080> |
| Cinco serviços que sobem em ordem: `db`, `migrate`, `backend`, `bff` e `web` | `docker compose ps --all` |
| Migrações com Alembic, ainda sem tabelas de negócio | O `migrate` termina com código 0 |
| Health checks no `backend` e no `bff` | [Conferir os health checks](#conferir-os-health-checks) |
| Logs JSON com o mesmo `trace_id` entre BFF e backend, e dados sensíveis redigidos | [Seguir uma requisição](#seguir-uma-requisição) |
| Exportação de traces por OTLP, desligada por padrão | Defina `OTEL_EXPORTER_OTLP_ENDPOINT` no `.env` |
| Gates de qualidade e regras de branch | [Comandos](#comandos) |

### Conferir os health checks

Só o `web` publica uma porta no host, na 8080. Por isso, os outros serviços são consultados de dentro do container:

```bash
docker compose exec bff python -c "import urllib.request as u; print(u.urlopen('http://127.0.0.1:8000/health/ready').read().decode())"
```

Troque `bff` por `backend` para consultar o outro serviço. A resposta esperada é `{"status":"ok"}`.

| Rota | O que verifica | Resposta |
| --- | --- | --- |
| `GET /health/live` | Se o processo está de pé | `200` |
| `GET /health/ready` no `backend` | Se o banco está acessível | `200`, ou `503` com `code: not_ready` |
| `GET /health/ready` no `bff` | Se o backend está pronto | `200`, ou `503` com `code: not_ready` |

### Seguir uma requisição

```bash
docker compose logs -f bff backend
```

Cada linha é um JSON. Rode um health check do `bff` em outro terminal e procure o mesmo `trace_id` nos logs dos dois serviços.

## O que ainda não existe

| Fase | Entrega |
| --- | --- |
| F1 e F2 | Contas e sessões: regras de domínio, banco e API |
| F3 | Previsão do tempo com a Open-Meteo |
| F4 | BFF: rotas públicas `/api`, cookie de sessão e dados da home |
| F5 | Telas de cadastro, login, home e logout |
| F6 | Aceite completo da jornada do produto |

Por enquanto, o `web` só serve a SPA. Um caminho como `/api/home` devolve a mesma página HTML, porque o proxy para o BFF entra na F5.

## Comandos

| Comando | O que faz |
| --- | --- |
| `make setup` | Prepara o ambiente local |
| `make up` | Constrói e sobe os serviços |
| `make down` | Remove os containers e mantém o banco |
| `make check` | Roda ruff, mypy, import-linter, testes unitários e Vitest |
| `make integration` | Testa o stack real em uma cópia limpa do repositório. Leva alguns minutos |
| `make mutation` | Roda o mutmut e compara com a meta de 80% |
| `make e2e` | Reservado para os testes de ponta a ponta |

Dois alvos **falham de propósito** nesta fase:

- `make mutation` sai com erro porque ainda não há regra de negócio para mutar.
- `make e2e` sai com erro porque a suíte só nasce na F5.

## Problemas comuns

| Sintoma | Causa e solução |
| --- | --- |
| A porta 8080 já está em uso | Pare o processo que a ocupa. O `make integration` também usa essa porta, então rode `make down` antes dele |
| O `migrate` falha depois de mudar a senha no `.env` | O MySQL guarda a senha no volume. Rode `docker compose down -v` e `make up`, sabendo que isso apaga o banco |
| O `migrate` falha com uma senha nova | `MYSQL_PASSWORD` entra em uma URL. Use só letras, números, hífen ou sublinhado |
| O commit é recusado | Os hooks só aceitam commit e push em `feature/*`. Crie uma branch com esse prefixo |

## Estrutura do repositório

```text
services/backend/        API de domínio em FastAPI, com os contextos identity e weather
services/bff/            Fronteira do navegador em FastAPI
packages/observability/  Logs JSON e traces usados pelos dois serviços
web/                     SPA em React, Vite e TypeScript, servida pelo nginx
tools/                   Política de branches e meta de mutação
tests/                   Testes do repositório e de integração
compose.yaml             Definição do ambiente local
```

## Documentação

- [Requisitos do produto](.prd/quadralug-conta-e-home.md)
- [Arquitetura](.tdd/quadralug-conta-e-home.md)
- [Plano de fases e fluxo de entrega](plan.md)
- [Regras para contribuir](AGENTS.md)
- [Decisões](DECISIONS.md)
