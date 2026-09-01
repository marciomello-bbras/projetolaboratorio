# ADR-0003: Persistência em memória no MVP

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

O MVP precisa persistir contas para demonstrar o fluxo operacional, com baixo custo de setup. Não há requisito de volume, multi-instância ou recuperação após reinício no critério de aceite atual.

## Decisão

Usar `AccountsPayableRepository` com `dict[UUID, AccountsPayableOut]` no processo da API. Cópias defensivas (`model_copy`) isolam o estado interno de mutações externas.

Não há banco, ORM nem arquivo de dados. Reinício do Uvicorn apaga os registros.

## Alternativas consideradas

- **SQLite:** persistência real com pouco setup; adiciona dependência, schema e ciclo de migração cedo demais.
- **PostgreSQL ou outro SGBD:** adequado a produção, incompatível com a simplicidade do laboratório.
- **Arquivo JSON/CSV:** sobrevive a reinício, mas exige concorrência e serialização sem ganho imediato.

## Consequências

Positivas:

- zero configuração de banco para subir a API;
- testes de serviço e rota sem fixture de infraestrutura;
- a interface do repositório já delimita o ponto de troca.

Negativas:

- perda total de dados ao reiniciar (risco R01);
- inadequado para demonstração longa ou uso contínuo interno;
- duas instâncias da API não compartilham estado.

Evolução prevista: substituir o dicionário por SQLite mantendo o contrato do repositório.

## Referências

- `app/repositories/accounts_payable_repository.py`
- `riscos/identificacao.md` (R01)
