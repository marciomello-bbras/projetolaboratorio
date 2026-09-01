# Diagramas de arquitetura

Fonte canônica no README: seção **Arquitetura**. Os blocos Mermaid abaixo renderizam em visualizadores Markdown compatíveis (GitHub, GitLab, Cursor).

O desenho reflete o código versionado: persistência em memória, `PriorityAdvisor` preparado e ainda fora das rotas, e liquidação como jornada crítica.

## Contexto do sistema (C4 Nível 1)

A equipe de finanças consome a micro-API por HTTP/JSON. A OpenAI é um sistema externo opcional, usado apenas pelo componente de prioridade quando houver chave configurada.

```mermaid
C4Context
    title Contexto do sistema — Micro-API de Contas a Pagar

    Person(financeiro, "Equipe de finanças", "Usuário interno que cadastra, consulta, cancela e liquida contas.")
    Person_Ext(cliente_http, "Cliente HTTP / Postman / Swagger", "Consome o contrato OpenAPI para operação e demonstração.")

    System(api, "Micro-API de Contas a Pagar", "MVP REST em FastAPI: cadastro, consulta, atualização, cancelamento e pagamento.")

    System_Ext(openai, "API OpenAI", "Sugestão remota de prioridade. Uso opcional e ainda fora do fluxo principal.")

    Rel(financeiro, api, "Opera contas a pagar", "HTTP/JSON")
    Rel(cliente_http, api, "Explora e testa o contrato", "OpenAPI / REST")
    Rel_D(api, openai, "Chamada futura/opcional do PriorityAdvisor", "HTTPS, se OPENAI_API_KEY")
```

## Visão de containers (C4 Nível 2)

Um processo Python concentra API, domínio e persistência volátil. O advisor é um container lógico ainda desconectado do fluxo principal.

```mermaid
C4Container
    title Containers — Micro-API de Contas a Pagar

    Person(financeiro, "Equipe de finanças", "Operação interna de contas a pagar.")

    System_Boundary(sistema, "Micro-API de Contas a Pagar") {
        Container(web, "API HTTP", "Uvicorn + FastAPI", "Expõe /accounts-payable, health check, OpenAPI e handlers globais de erro.")
        Container(app, "Aplicação de domínio", "AccountsPayableService + schemas Pydantic", "Valida entrada, aplica regras de estado e orquestra persistência.")
        Container(advisor, "PriorityAdvisor", "Heurística local + LLM opcional", "Componente preparado e testado; ainda não integrado às rotas.")
        ContainerDb(store, "Repositório em memória", "dict[UUID, AccountsPayableOut]", "Persistência volátil do MVP. Reinício da API apaga os registros.")
    }

    System_Ext(openai, "API OpenAI", "Prioridade remota com timeout curto e fallback local.")

    Rel(financeiro, web, "CRUD operacional e liquidação", "HTTP/JSON")
    Rel(web, app, "Delega casos de uso", "chamada síncrona")
    Rel(app, store, "Cria, lê, atualiza e liquida", "acesso em processo")
    Rel_D(app, advisor, "Integração planejada", "ainda não conectada")
    Rel_D(advisor, openai, "Sugestão remota opcional", "HTTPS")
```

## Componentes internos

```mermaid
flowchart LR
    Client["Cliente API"]
    Routes["FastAPI Routes"]
    Schemas["Schemas Pydantic"]
    Service["AccountsPayableService"]
    Advisor["PriorityAdvisor"]
    Repository["AccountsPayableRepository"]

    Client --> Routes
    Routes --> Schemas
    Schemas --> Service
    Service --> Repository
    Service -. ainda não integrado .-> Advisor
    Repository --> Service
    Service --> Routes
    Routes --> Client
```

## Jornada crítica — registro de pagamento

`POST /accounts-payable/{id}/payment` fecha o ciclo operacional. Regras: conta existente, estado pagável, `valor_pago` igual a `valor_previsto`, `data_pagamento` não futura e não anterior à emissão.

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Cliente HTTP
    participant API as FastAPI / rotas
    participant Schema as Pydantic<br/>AccountsPayablePaymentCreate
    participant Svc as AccountsPayableService
    participant Repo as AccountsPayableRepository

    Cliente->>API: POST /accounts-payable/{id}/payment<br/>data_pagamento, valor_pago, observacao_pagamento
    API->>Schema: valida contrato JSON

    alt data_pagamento no futuro ou valor_pago <= 0
        Schema-->>API: RequestValidationError
        API-->>Cliente: 422 erro_validacao
    else payload válido
        API->>Svc: register_payment(id, payload)
        Svc->>Repo: get_by_id(id)

        alt conta inexistente
            Repo-->>Svc: None
            Svc-->>API: AccountsPayableNotFoundError
            API-->>Cliente: 404 conta_nao_encontrada
        else conta encontrada
            Repo-->>Svc: AccountsPayableOut
            Svc->>Svc: sincroniza overdue e aplica _ensure_payable

            alt cancelada, já paga, valor diferente ou data anterior à emissão
                Svc-->>API: AccountsPayableInvalidStateError
                API-->>Cliente: 409 estado_invalido
            else liquidação permitida
                Svc->>Repo: register_payment(id, payload)
                Repo-->>Svc: conta com status paid
                Svc-->>API: AccountsPayableOut
                API-->>Cliente: 200 Pagamento registrado com sucesso.
            end
        end
    end
```

## Atividades do ciclo operacional

Fluxo de trabalho da conta, do cadastro até um estado terminal (`paid` ou `cancelled`). Consultas sincronizam vencidas. Atualização e pagamento exigem conta não paga e não cancelada. `DELETE` não é caminho válido: a API bloqueia remoção física.

```mermaid
flowchart TD
    startNode([Início]) --> cadastrar["Cadastrar conta<br/>POST /accounts-payable"]
    cadastrar --> validaCadastro{"Contrato válido?<br/>campos obrigatórios, valor &gt; 0,<br/>emissão ≤ vencimento"}

    validaCadastro -->|não| erro422["Retornar 422 erro_validacao"]
    erro422 --> fimErro([Fim])

    validaCadastro -->|sim| persistir["Persistir conta com status pending"]
    persistir --> consultar{"Consultar ou listar?"}

    consultar -->|sim| syncVencida{"data_vencimento &lt; hoje<br/>e status não terminal?"}
    consultar -->|não| decidirAcao
    syncVencida -->|sim| marcarOverdue["Sincronizar status overdue"]
    syncVencida -->|não| decidirAcao
    marcarOverdue --> decidirAcao{"Próxima ação operacional"}

    decidirAcao -->|atualizar dados| podeAtualizar{"Status pago ou cancelado?"}
    podeAtualizar -->|sim| erro409upd["Retornar 409 estado_invalido"]
    podeAtualizar -->|não| atualizar["Atualizar campos permitidos"]
    atualizar --> decidirAcao
    erro409upd --> fimErro

    decidirAcao -->|cancelar| podeCancelar{"Status já pago ou cancelado?"}
    podeCancelar -->|sim| erro409can["Retornar 409 estado_invalido"]
    podeCancelar -->|não| cancelar["Transicionar para cancelled"]
    cancelar --> fimCancelada([Fim — conta cancelada])
    erro409can --> fimErro

    decidirAcao -->|registrar pagamento| validaPagto{"Payload válido?<br/>valor_pago &gt; 0 e<br/>data_pagamento não futura"}
    validaPagto -->|não| erro422pag["Retornar 422 erro_validacao"]
    erro422pag --> fimErro
    validaPagto -->|sim| existeConta{"Conta encontrada?"}
    existeConta -->|não| erro404["Retornar 404 conta_nao_encontrada"]
    erro404 --> fimErro
    existeConta -->|sim| podePagar{"Pagável?<br/>não paga, não cancelada,<br/>valor_pago = valor_previsto,<br/>data ≥ emissão"}
    podePagar -->|não| erro409pag["Retornar 409 estado_invalido"]
    erro409pag --> fimErro
    podePagar -->|sim| liquidar["Persistir pagamento<br/>e status paid"]
    liquidar --> fimPaga([Fim — conta liquidada])

    decidirAcao -->|encerrar consulta| fimConsulta([Fim — conta consultada])
```

