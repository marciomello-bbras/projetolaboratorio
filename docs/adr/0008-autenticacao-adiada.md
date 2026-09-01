# ADR-0008: Autenticação interna adiada para release posterior

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

O escopo exige autenticação interna simples (RNF03, RT04). A Release 1 priorizou o fluxo operacional. A API hoje escuta em `127.0.0.1` sem credencial.

## Decisão

Entregar o Core **sem** autenticação e registrar a ausência como decisão consciente, não como omissão.

Os endpoints de contas a pagar permanecem abertos. A proteção por API key (ou equivalente) fica na Release 2. Até lá, o uso previsto é local ou demonstração controlada, não exposição em rede compartilhada.

## Alternativas consideradas

- **API key estática já no Core:** atende RNF03 cedo, atrasa o fluxo de pagamento e os testes de rota.
- **JWT ou OAuth2:** desproporcional ao público interno do MVP.
- **Declarar RNF03 fora de escopo:** evitaria o risco documental, mas contradiz o escopo já acordado.

## Consequências

Positivas:

- o ciclo cadastro–pagamento pôde ser validado sem middleware;
- a dívida fica explícita no README, no backlog e no risco R02.

Negativas:

- qualquer cliente HTTP na máquina (ou na rede, se o bind mudar) opera a API;
- o critério de aceite do MVP ainda não está fechado;
- clientes e testes precisarão passar a enviar credencial quando RT04 for implementado.

Quando a autenticação for adotada, este ADR deve ser supersedido por um novo registro com o mecanismo escolhido.

## Referências

- `docs/escopo-mvp.md` (RNF03)
- `docs/backlog.md` (RT04)
- `riscos/identificacao.md` (R02)
