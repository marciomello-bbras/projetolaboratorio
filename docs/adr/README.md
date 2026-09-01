# Architecture Decision Records (ADR)

Registros das decisões de arquitetura já efetivas no código do MVP. Cada ADR descreve o contexto, a escolha, as alternativas e as consequências.

Convenção:

- identificador sequencial com quatro dígitos;
- status `Aceita` para decisão vigente;
- um arquivo por decisão;
- o README do projeto aponta este índice.

| ID | Título | Status |
|----|--------|--------|
| [ADR-0001](0001-micro-api-rest-fastapi.md) | Micro-API REST com FastAPI | Aceita |
| [ADR-0002](0002-arquitetura-em-camadas.md) | Separação em camadas api, models, services e repositories | Aceita |
| [ADR-0003](0003-persistencia-em-memoria.md) | Persistência em memória no MVP | Aceita |
| [ADR-0004](0004-bloqueio-remocao-fisica.md) | Bloqueio de remoção física para rastreabilidade | Aceita |
| [ADR-0005](0005-envelope-padrao-http.md) | Envelope padronizado de sucesso e erro HTTP | Aceita |
| [ADR-0006](0006-priority-advisor-desacoplado.md) | PriorityAdvisor com heurística local, fallback e fora do fluxo principal | Aceita |
| [ADR-0007](0007-sincronizacao-overdue-na-leitura.md) | Sincronização de contas vencidas na leitura | Aceita |
| [ADR-0008](0008-autenticacao-adiada.md) | Autenticação interna adiada para release posterior | Aceita |
