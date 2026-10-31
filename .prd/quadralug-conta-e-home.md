# Quadralug — Conta e Home

> Read this PRD and take the bet as settled. Do not re-derive it.
> Status: confirmed by o autor do projeto, 2026-10-28

## Situation

- Effort: not shipped yet — produto novo, projeto de estudo, nada construído.
- Decision: committed by o autor do projeto, 2026-10-28, em Projeto.md (primeira fase do Quadralug).
- In flight: nada existente é tocado; a reserva de quadras é a fase seguinte e fica fora deste documento.
- At stake: cheap to undo — não há usuários, reservas nem pagamentos ainda.

## Problem

O Quadralug vai alugar 4 quadras em Salvador, BA: duas cobertas (ginásio) e duas a céu aberto. Esta é a primeira peça do produto. Ela deve permitir que uma pessoa tenha conta, entre e saia da plataforma, e veja ao entrar se vai chover nos próximos dias. A chuva é o que decide se vale reservar uma quadra descoberta.

Sem esta peça a reserva não pode começar, porque toda reserva precisa estar ligada a uma pessoa identificada. Por isso ela vem antes de qualquer outra. A previsão já aparece aqui porque é o motivo de o produto separar quadras cobertas de descobertas.

Não existe número medido: o produto ainda não existe, então não há uso nem demanda para medir.

## Success

- Worked if: a fase de reserva pode começar sobre contas reais, porque uma pessoa consegue criar conta, entrar, ver a previsão de Salvador para hoje e os próximos 6 dias, e sair, sem ajuda.

## Boundary

In: criar conta (nome, e-mail, senha), entrar, sair, e uma home que mostra a previsão do tempo de Salvador, BA.

Out: recuperação de senha — escolha de fazer o mais simples possível nesta fase; quem esquece a senha perde o acesso.
Out: confirmação de e-mail — sem reservas nem pagamento, uma conta falsa não causa dano.
Out: manter a pessoa conectada entre visitas — mais simples; cada nova visita pede login.
Out: previsão pela localização da pessoa — o que importa é o tempo onde ficam as quadras.
Out: reserva de quadras, disponibilidade e pagamento — próximas fases.

Unchanged: a lista de quadras (4: 2 cobertas, 2 a céu aberto) é só contexto; nada nesta fase mostra ou altera quadras.

## Journey

| State | What should happen | Person sees |
|---|---|---|
| Criar conta com dados válidos | A conta é criada já ativa e a pessoa entra direto | A home com a previsão |
| Criar conta com e-mail já cadastrado | A conta não é criada | Aviso de que o e-mail já tem conta, com link para entrar |
| Criar conta com senha de menos de 8 caracteres | A conta não é criada | Aviso de que a senha precisa ter pelo menos 8 caracteres |
| Entrar com e-mail e senha corretos | A pessoa entra | A home com a previsão |
| Entrar com e-mail ou senha errados | A pessoa não entra | "E-mail ou senha incorretos", sem dizer qual dos dois |
| Abrir a home sem estar logado | O acesso é negado | A tela de login |
| Abrir o login já estando logado | A pessoa segue para dentro | A home |
| Home, previsão carregada | Mostra o tempo de Salvador, BA, com hoje em destaque | Previsão de hoje, com opção de ver os próximos 6 dias (7 no total) |
| Home, previsão indisponível | A home abre normalmente; a falha da previsão não bloqueia nada | "Previsão indisponível no momento" e um botão para tentar de novo |
| Sair (logout) | A sessão termina | A tela de login; voltar no navegador não reabre a home |
| Fechar o navegador e voltar depois | A pessoa não continua conectada | A tela de login |
| Esqueceu a senha | Não há como recuperar nesta fase | Nenhuma opção de recuperação na tela de login |
