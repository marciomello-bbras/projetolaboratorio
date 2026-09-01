# ADR-0006: PriorityAdvisor com heurística local, fallback e fora do fluxo principal

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

O projeto precisa de um componente de prioridade assistida por IA, sem tornar a API dependente de rede, custo ou chave externa. O fluxo principal de contas a pagar já opera sem essa sugestão.

## Decisão

Implementar `PriorityAdvisor` como componente isolado:

1. calcular prioridade local (`low`, `medium`, `high`, `critical`) por status, vencimento e palavras-chave;
2. se `OPENAI_API_KEY` existir, tentar a API OpenAI com timeout curto;
3. em qualquer falha ou ausência de chave, devolver a heurística local.

O advisor **não** é chamado por `AccountsPayableService` nem pelas rotas. A prioridade não entra no schema de resposta da conta. Testes cobrem o componente de forma independente.

## Alternativas consideradas

- **IA obrigatória em cada cadastro:** qualidade potencialmente maior, API indisponível sem rede ou crédito.
- **Somente heurística, sem cliente HTTP:** mais simples, perde o gancho de evolução pedido pelo laboratório.
- **Integrar já nas rotas de create/list:** antecipa valor, mistura um componente ainda experimental ao contrato estável.

## Consequências

Positivas:

- o fluxo principal não falha por timeout ou chave ausente (mitiga R05);
- a heurística local é testável sem mock de rede;
- a integração futura tem um ponto único (`suggest_priority`).

Negativas:

- a API atual não expõe prioridade (risco R11);
- existe código de produção que o usuário da API não exercita;
- quando integrado, o contrato JSON da conta deverá ganhar um campo novo.

## Referências

- `app/services/priority_advisor.py`
- `tests/test_priority_advisor.py`
- `riscos/identificacao.md` (R05, R11)
