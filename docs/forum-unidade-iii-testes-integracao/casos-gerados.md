# Casos de teste de integração gerados

Origem: segunda rodada dos prompts em [prompts.md](prompts.md), revisada contra o código antes de virar teste. Implementação: `tests/test_integracao_fluxo_contas.py`.

A primeira rodada foi descartada. Ela descrevia login, rotas `/api/v1/bills`, pagamento parcial e `DELETE 204`, nenhum dos quais existe nesta API.

## Prompt de cenários — casos adotados

### INT-01 — cadastro visível na consulta e na listagem

1. `POST /accounts-payable` com vencimento futuro → `201`, `sucesso: true`, `dados.status = pending`.
2. `GET /accounts-payable/{id}` → `200` e o mesmo `id`.
3. `GET /accounts-payable` → a lista contém exatamente essa conta.

### INT-02 — atualização permanece na consulta seguinte

1. `POST /accounts-payable` → `201`.
2. `PUT /accounts-payable/{id}` com nova `descricao` → `200`.
3. `GET /accounts-payable/{id}` → a descrição nova permanece, o status segue `pending` e o `valor_previsto` não muda.

### INT-03 — vencimento sincronizado na leitura

1. `POST /accounts-payable` com `data_vencimento` anterior a hoje e `data_emissao` ainda anterior.
2. `GET /accounts-payable/overdue` → a conta aparece com `status = overdue`.
3. `GET /accounts-payable/{id}` → o mesmo status `overdue`.

A promoção não é um `PATCH` do cliente. Ela acontece porque a leitura passa pelo serviço.

### INT-04 — liquidação de conta vencida

1. Cria conta já vencida, como em INT-03.
2. `POST /accounts-payable/{id}/payment` com `valor_pago` igual ao previsto e `data_pagamento` de hoje → `200`, `status = paid`.
3. `GET /accounts-payable/{id}` → `paid`, com `data_pagamento` e `valor_pago` preenchidos.
4. `GET /accounts-payable/overdue` → lista vazia.
5. Segundo `POST /payment` → `409`, `erro.codigo = estado_invalido`.
6. Novo `GET` → continua `paid`.

### INT-05 — cancelamento é terminal

1. `POST /accounts-payable` → `201`.
2. `POST /accounts-payable/{id}/cancel` → `200`, `status = cancelled`.
3. `PUT` com outra descrição → `409`, `estado_invalido`.
4. `POST /payment` → `409`, `estado_invalido`.
5. `GET /accounts-payable/{id}` → segue `cancelled` e a descrição original não mudou.

## Prompt de erro e contrato — casos adotados

### INT-06 — ausência de recurso

Para um UUID que não existe, `GET`, `POST /payment`, `POST /cancel` e `DELETE` respondem `404`, `sucesso: false` e `erro.codigo = conta_nao_encontrada`.

O corpo do pagamento, quando enviado, é válido. O `404` vem da conta, não do schema.

### INT-07 — contrato rejeitado antes da regra

Criações que não podem gravar, cada uma seguida de `GET /accounts-payable` com lista vazia:

- `valor_previsto = 0.00`;
- campo desconhecido `prioridade`;
- `descricao` ausente.

Todas: `422`, `erro.codigo = erro_validacao`, `erro.detalhes` preenchido.

Sobre uma conta já criada:

- `PATCH /status` com `{"status": "paid"}` → `422` (pago só nasce na rota de pagamento);
- `POST /payment` com `data_pagamento` amanhã → `422`.

`GET` seguinte: `status = pending` e `valor_pago` nulo.

### INT-08 — regra de liquidação, com schema válido

Conta com emissão hoje e vencimento futuro.

- `valor_pago` diferente do previsto → `409`, `estado_invalido`;
- `data_pagamento` ontem, portanto anterior à emissão → `409`, `estado_invalido`.

`GET` seguinte: `pending`, sem `data_pagamento` e sem `valor_pago`.

A data futura ficou no INT-07 de propósito. O schema barra o futuro; o serviço barra o valor e a emissão.

### INT-09 — remoção física bloqueada

1. `POST /accounts-payable` → `201`.
2. `DELETE /accounts-payable/{id}` → `409`, `erro.codigo = remocao_fisica_bloqueada`.
3. `GET /accounts-payable/{id}` → `200`, a mesma conta, ainda `pending`.

### INT-10 — vencida não volta para pending

1. Cria conta vencida.
2. `PATCH /accounts-payable/{id}/status` com `{"status": "pending"}` → `409`, `estado_invalido`.
3. `GET /accounts-payable/{id}` → continua `overdue`.

## O que ficou de fora, de propósito

A primeira geração sugeriu login, paginação, pagamento parcial, webhook de banco e `DELETE 204`. Nenhum desses comportamentos existe no MVP. Incluí-los deixaria a suíte vermelha por testar um contrato imaginário, não por achar defeito no sistema.
