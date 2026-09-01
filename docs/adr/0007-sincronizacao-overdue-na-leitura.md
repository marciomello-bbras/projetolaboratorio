# ADR-0007: Sincronização de contas vencidas na leitura

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

O MVP deve identificar contas vencidas (RF10 / RF09) sem job, fila ou cron. O status precisa permanecer coerente com a data corrente quando a conta ainda não foi paga nem cancelada.

## Decisão

Sincronizar `overdue` no caminho de leitura e de atualização cadastral, dentro de `AccountsPayableService`:

- se `data_vencimento` for anterior a hoje (UTC) e o status não for `paid` nem `cancelled`, persistir `overdue`;
- se a conta deixar de estar vencida e não for terminal, voltar para `pending`;
- `GET /accounts-payable/overdue` filtra o resultado já sincronizado.

Não há processo em background.

## Alternativas consideradas

- **Calcular vencida só na resposta, sem gravar:** mais simples, o status persistido ficaria mentiroso após o vencimento.
- **Job periódico:** correto em produção, depende de scheduler inexistente no MVP.
- **Campo derivado `vencida` além do status:** evita transições, duplica a informação já modelada em `AccountsPayableStatus`.

## Consequências

Positivas:

- listagem e consulta devolvem status alinhado à data atual;
- endpoint `/overdue` reutiliza a mesma regra;
- contas pagas ou canceladas não são reabertas como vencidas.

Negativas:

- a primeira leitura após o vencimento é o momento que grava a mudança;
- contas nunca consultadas permanecem `pending` no dicionário até alguém lê-las;
- testes de vencimento dependem de relógio (`datetime.now`).

## Referências

- `app/services/accounts_payable_service.py` (`_sync_overdue_status`, `list_overdue`)
- `docs/escopo-mvp.md` (RF10)
