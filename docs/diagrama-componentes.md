# Diagramas de arquitetura

Fonte canônica no README: seção **Arquitetura**.

Os blocos usam `flowchart` e `sequenceDiagram` para renderizar no GitHub. A visão estrutural é inspirada no C4, mas não usa `C4Context`/`C4Container`: o renderer do GitHub não desenha esses tipos e o preview fica em carregamento.

O desenho reflete o código versionado: persistência em memória, `PriorityAdvisor` preparado e ainda fora das rotas, e liquidação como jornada crítica.

## Contexto do sistema (C4 Nível 1)

A equipe de finanças consome a micro-API por HTTP/JSON. A OpenAI é um sistema externo opcional, usado apenas pelo componente de prioridade quando houver chave configurada.

```mermaid
flowchart TB
    financeiro["Equipe de financas<br/>usuario interno"]
    cliente["Cliente HTTP / Postman / Swagger"]
    api["Micro-API de Contas a Pagar<br/>MVP REST em FastAPI"]
    openai["API OpenAI<br/>sistema externo opcional"]

    financeiro -->|"HTTP/JSON"| api
    cliente -->|"OpenAPI / REST"| api
    api -.->|"HTTPS se OPENAI_API_KEY"| openai
```

## Visao de containers (C4 Nível 2)

Um processo Python concentra API, dominio e persistencia volatil. O advisor e um container logico ainda desconectado do fluxo principal.

```mermaid
flowchart TB
    financeiro["Equipe de financas"]

    subgraph sistema["Micro-API de Contas a Pagar"]
        web["API HTTP<br/>Uvicorn + FastAPI"]
        app["Aplicacao de dominio<br/>AccountsPayableService + Pydantic"]
        advisor["PriorityAdvisor<br/>heuristica local + LLM opcional"]
        store[("Repositorio em memoria")]
    end

    openai["API OpenAI<br/>externo opcional"]

    financeiro -->|"HTTP/JSON"| web
    web -->|"chamada sincrona"| app
    app -->|"acesso em processo"| store
    app -.->|"ainda nao conectada"| advisor
    advisor -.->|"HTTPS opcional"| openai
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
    Service -. ainda nao integrado .-> Advisor
    Repository --> Service
    Service --> Routes
    Routes --> Client
```

## Jornada critica — registro de pagamento

`POST /accounts-payable/{id}/payment` fecha o ciclo operacional. Regras: conta existente, estado pagavel, `valor_pago` igual a `valor_previsto`, `data_pagamento` nao futura e nao anterior a emissao.

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Cliente HTTP
    participant API as FastAPI
    participant Schema as Pydantic
    participant Svc as Service
    participant Repo as Repository

    Cliente->>API: POST /accounts-payable/id/payment
    API->>Schema: valida contrato JSON

    alt payload invalido
        Schema-->>API: RequestValidationError
        API-->>Cliente: 422 erro_validacao
    else payload valido
        API->>Svc: register_payment
        Svc->>Repo: get_by_id

        alt conta inexistente
            Repo-->>Svc: None
            Svc-->>API: NotFoundError
            API-->>Cliente: 404 conta_nao_encontrada
        else conta encontrada
            Repo-->>Svc: AccountsPayableOut
            Svc->>Svc: sync overdue e ensure_payable

            alt estado ou valor invalido
                Svc-->>API: InvalidStateError
                API-->>Cliente: 409 estado_invalido
            else liquidacao permitida
                Svc->>Repo: register_payment
                Repo-->>Svc: status paid
                Svc-->>API: AccountsPayableOut
                API-->>Cliente: 200 sucesso
            end
        end
    end
```

## Atividades do ciclo operacional

Fluxo de trabalho da conta, do cadastro ate um estado terminal (`paid` ou `cancelled`). Consultas sincronizam vencidas. Atualizacao e pagamento exigem conta nao paga e nao cancelada. `DELETE` nao e caminho valido: a API bloqueia remocao fisica.

```mermaid
flowchart TD
    startNode([Inicio]) --> cadastrar[Cadastrar conta]
    cadastrar --> validaCadastro{Contrato valido?}

    validaCadastro -->|nao| erro422[Retornar 422]
    erro422 --> fimErro([Fim])

    validaCadastro -->|sim| persistir[Persistir status pending]
    persistir --> consultar{Consultar ou listar?}

    consultar -->|sim| syncVencida{Vencida e nao terminal?}
    consultar -->|nao| decidirAcao
    syncVencida -->|sim| marcarOverdue[Sincronizar status overdue]
    syncVencida -->|nao| decidirAcao
    marcarOverdue --> decidirAcao{Proxima acao}

    decidirAcao -->|atualizar| podeAtualizar{Paga ou cancelada?}
    podeAtualizar -->|sim| erro409upd[Retornar 409]
    podeAtualizar -->|nao| atualizar[Atualizar campos permitidos]
    atualizar --> decidirAcao
    erro409upd --> fimErro

    decidirAcao -->|cancelar| podeCancelar{Ja paga ou cancelada?}
    podeCancelar -->|sim| erro409can[Retornar 409]
    podeCancelar -->|nao| cancelar[Status cancelled]
    cancelar --> fimCancelada([Fim conta cancelada])
    erro409can --> fimErro

    decidirAcao -->|pagar| validaPagto{Payload de pagamento valido?}
    validaPagto -->|nao| erro422pag[Retornar 422]
    erro422pag --> fimErro
    validaPagto -->|sim| existeConta{Conta encontrada?}
    existeConta -->|nao| erro404[Retornar 404]
    erro404 --> fimErro
    existeConta -->|sim| podePagar{Pode liquidar?}
    podePagar -->|nao| erro409pag[Retornar 409]
    erro409pag --> fimErro
    podePagar -->|sim| liquidar[Persistir status paid]
    liquidar --> fimPaga([Fim conta liquidada])

    decidirAcao -->|encerrar| fimConsulta([Fim conta consultada])
```
