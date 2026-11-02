# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Plan/Checks)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Prove uma ferramenta de gate com a ferramenta real em um caso plantado: um stub de CLI prova só o Makefile e deixou o mutmut medindo 0 sem ninguém ver.
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `tooling` · harmful: 0
- features: f0-fundacao
- evidence: AC22 (tooling)
- last seen: 2026-11-02T15:02:09Z

### L-002 - Contratos forbidden do import-linter listam nomes, então parta da regra do TDD e enumere tudo o que ela proíbe, não só os exemplos do critério.
- signal: `spec_deviation` · recurrence: 1 feature(s) · scope: `architecture` · harmful: 0
- features: f0-fundacao
- evidence: AC21 (architecture)
- last seen: 2026-11-02T15:02:09Z

### L-003 - Teste o ponto de montagem com o ambiente real em subprocesso: testar a função pura com environ injetado não prova que o serviço lê a variável.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `observability` · harmful: 0
- features: f0-fundacao
- evidence: C18 (observability)
- last seen: 2026-11-02T15:02:09Z

### L-004 - Em workflows, afirme o mapeamento de env e argumentos, não só o texto do comando: procurar o comando deixa passar a origem errada do dado.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `ci` · harmful: 0
- features: f0-fundacao
- evidence: C29 (ci)
- last seen: 2026-11-02T15:02:09Z

### L-005 - Afirme ausência de ERROR no boot: instrumentação OTel fora da faixa de versão só loga e se desliga, com todas as suítes verdes.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `dependencies` · harmful: 0
- features: f0-fundacao
- evidence: C41 (dependencies)
- last seen: 2026-11-02T15:02:09Z

### L-006 - Timeout do httpx vale por operação: um limite total de resposta exige asyncio.timeout e precisa de teste com resposta lenta.
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `http` · harmful: 0
- features: f0-fundacao
- evidence: AC8 (http)
- last seen: 2026-11-02T15:02:09Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
