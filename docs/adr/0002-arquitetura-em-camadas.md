# ADR-0002: Separação em camadas api, models, services e repositories

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

O backlog pede estrutura que separe pelo menos entrada e domínio (RT01). As regras de contas a pagar — transições de status, liquidação e bloqueio de exclusão — não devem ficar nas rotas HTTP.

## Decisão

Organizar o código em quatro camadas no mesmo processo:

- `api`: rotas FastAPI e envelope HTTP;
- `models`: schemas e validações Pydantic;
- `services`: regras de negócio e orquestração;
- `repositories`: persistência, hoje em memória.

As rotas dependem do serviço; o serviço depende do repositório. O `PriorityAdvisor` vive em `services`, isolado das rotas até haver integração explícita.

## Alternativas consideradas

- **Tudo nas rotas:** entrega mais rápida, regras financeiras misturadas com HTTP e testes mais frágeis.
- **Hexagonal completa com portas e adaptadores:** melhor isolamento, custo de abstração alto para um MVP de um domínio.
- **Modularização por feature em pacotes separados:** prematura enquanto só existe contas a pagar.

## Consequências

Positivas:

- regras de domínio testáveis sem HTTP (`tests/test_accounts_payable_service.py`);
- troca futura do repositório (por exemplo SQLite) sem reescrever rotas;
- responsabilidade de cada arquivo permanece explícita.

Negativas:

- há passagem extra entre camadas para operações simples;
- o repositório ainda é instanciado no módulo de rotas, não em um composition root dedicado.

## Referências

- `app/api/accounts_payable_routes.py`
- `app/services/accounts_payable_service.py`
- `app/repositories/accounts_payable_repository.py`
- `docs/backlog.md` (RT01)
