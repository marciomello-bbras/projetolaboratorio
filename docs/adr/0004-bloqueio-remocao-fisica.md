# ADR-0004: Bloqueio de remoção física para rastreabilidade

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

O escopo exige rastreabilidade mínima (RF08 / RF11): exclusão lógica ou bloqueio de exclusão física. Contas a pagar são registros financeiros; apagá-las impede auditoria mesmo no MVP.

## Decisão

Manter o endpoint `DELETE /accounts-payable/{id}`, mas fazê-lo falhar de propósito.

O serviço verifica se a conta existe e lança `AccountsPayableDeletionBlockedError`. A API responde `409` com código `remocao_fisica_bloqueada`. O caminho válido para desconsiderar uma conta é o cancelamento (`POST /accounts-payable/{id}/cancel`), que preserva o registro com status `cancelled`.

Há teste `xfail` documentando que a remoção física permanece bloqueada.

## Alternativas consideradas

- **Exclusão lógica com flag `ativo`:** atende rastreabilidade, mas cria um segundo eixo além do status.
- **Remover o verbo DELETE:** mais simples, porém esconde a regra; clientes descobririam só pela ausência da rota.
- **Hard delete:** viola RF08 e perde histórico.

## Consequências

Positivas:

- nenhum registro some do repositório por operação de API;
- a regra fica explícita no contrato HTTP;
- cancelamento continua consultável.

Negativas:

- o vocabulário REST fica não idiomático (`DELETE` que nunca apaga);
- o armazenamento em memória ainda perde tudo no reinício, então a rastreabilidade vale só enquanto o processo vive.

## Referências

- `app/services/accounts_payable_service.py` (`delete`, `cancel`)
- `app/api/accounts_payable_routes.py`
- `docs/escopo-mvp.md` (RF08)
- `docs/backlog.md` (RF11)
