# Prompts usados no experimento

Modelo: LLM no Cursor, sobre o repositório da micro-API de contas a pagar. Duas rodadas para cada tipo. A primeira rodada só descrevia o domínio. A segunda recebeu o contrato real.

## Tipo 1 — cenários de integração

### Versão inicial

```text
Você é um analista de testes. Gere casos de teste de integração para uma API REST
de contas a pagar. Cubra o fluxo completo, do cadastro ao pagamento. Responda em
português, no formato Dado / Quando / Então.
```

### O que essa versão devolveu

A resposta tinha volume, mas testava outro sistema:

- rotas inventadas (`POST /api/v1/bills`, `POST /api/v1/auth/login`);
- header `Authorization: Bearer ...`, embora esta API não autentique;
- pagamento parcial e parcelamento, que a regra local não aceita;
- `DELETE` com status `204` e corpo vazio;
- cada caso olhava só a resposta imediata, sem uma segunda chamada conferindo o estado.

Serviu para ver o formato Dado/Quando/Então. Não serviu para implementar.

### Ajustes aplicados ao prompt

- lista fechada de rotas e de status;
- envelope e códigos internos;
- proibição de inventar rota, autenticação ou banco;
- obrigação de uma segunda chamada observando o efeito da primeira;
- regra de liquidação explícita (`valor_pago` igual a `valor_previsto`).

### Versão ajustada

```text
Você é um analista de testes de integração. Gere cenários para a micro-API de
contas a pagar abaixo. Não invente rota, header, autenticação, banco nem campo
que não esteja neste contrato.

Rotas:
- POST /accounts-payable
- GET /accounts-payable
- GET /accounts-payable/overdue
- GET /accounts-payable/{id}
- PUT /accounts-payable/{id}
- POST /accounts-payable/{id}/payment
- PATCH /accounts-payable/{id}/status
- POST /accounts-payable/{id}/cancel
- DELETE /accounts-payable/{id}

Status: pending, paid, overdue, cancelled.
Cadastro nasce pending. Conta com data_vencimento anterior a hoje passa a
overdue na leitura (GET, listagem ou overdue), desde que não esteja paid nem
cancelled. Pagamento só liquida se valor_pago for igual a valor_previsto e a
data_pagamento não for futura nem anterior à data_emissao. Cancelada ou paga
não volta atrás. DELETE de conta existente responde 409 com
erro.codigo = remocao_fisica_bloqueada.

Sucesso: { sucesso: true, mensagem, dados } com HTTP 201 no POST de criação e
200 nas demais. Erro: { sucesso: false, erro: { codigo, mensagem, detalhes? } }.

Gere de 4 a 6 cenários de integração do ciclo operacional. Cada cenário precisa
de pelo menos duas chamadas HTTP, e a última deve observar o efeito persistido
da anterior (consulta, listagem ou overdue). Inclua um caminho de liquidação de
conta já vencida e um caminho de cancelamento. Não cubra erro de payload nesta
resposta.

Formato de cada caso:
- id (INT-01...)
- objetivo
- chamadas, em ordem: método, caminho, corpo relevante, status esperado,
  campos do envelope a afirmar
```

### Efeito na qualidade

Os cenários passaram a encadear operações que existem e a afirmar o estado na chamada seguinte. A diversidade saiu do “CRUD genérico” e foi para cinco jornadas do domínio: visibilidade, atualização, vencimento na leitura, liquidação de vencida e cancelamento terminal. Esses casos viraram INT-01 a INT-05.

## Tipo 2 — casos de erro e contrato de API

### Versão inicial

```text
Gere casos de teste negativos e de contrato para a API de contas a pagar:
dados inválidos, recursos inexistentes e conflitos de estado. Inclua o status
HTTP esperado.
```

### O que essa versão devolveu

A resposta variou os títulos (“campo obrigatório”, “não encontrado”, “conflito”), mas o critério de aceite ficou pobre e, em vários pontos, errado:

- quase todo erro virou HTTP `400`;
- apareceu `401` para requisição sem token;
- `DELETE` de novo como `204`;
- nenhuma menção a `erro.codigo`;
- nenhum caso conferia se a conta continuava no estado anterior depois da falha;
- data de pagamento futura e valor divergente caíram no mesmo balde de “pagamento inválido”.

### Ajustes aplicados ao prompt

- tabela fechada de HTTP e `erro.codigo`;
- distinção entre validação do schema (`422`) e regra de domínio (`409`);
- exemplos concretos de cada classe, tirados do serviço;
- obrigação de consultar a conta depois do erro;
- proibição de autenticação e de pagamento parcial.

### Versão ajustada

```text
Você é um analista de testes de contrato. Gere casos de erro para a mesma
micro-API do prompt anterior. Use somente as rotas e os status já listados.
Não invente autenticação.

Mapa de erro, que deve ser afirmado no envelope (sucesso = false e erro.codigo):
- conta inexistente: HTTP 404, codigo conta_nao_encontrada
- regra de estado ou de valor: HTTP 409, codigo estado_invalido
- DELETE de conta que existe: HTTP 409, codigo remocao_fisica_bloqueada
- payload rejeitado pelo schema (campo ausente, valor <= 0, campo desconhecido,
  status "paid" em PATCH /status, data_pagamento no futuro): HTTP 422,
  codigo erro_validacao, com erro.detalhes preenchido

Regras que NÃO são 422, e sim 409, porque a conta existe e o schema do
pagamento é válido:
- valor_pago diferente de valor_previsto
- data_pagamento anterior a data_emissao
- pagar ou atualizar conta cancelled
- PATCH /status tentando voltar uma conta overdue para pending
  (paid só pode nascer em POST /payment)

Gere de 4 a 6 casos. Cada caso de conta já existente deve terminar com
GET /accounts-payable/{id} provando que status, valor_pago e data_pagamento
não mudaram. Casos de POST inválido devem terminar com GET /accounts-payable
provando que a lista continua vazia.

Formato:
- id (INT-06...)
- classe (ausência, contrato ou regra)
- chamadas em ordem, com status e erro.codigo
- estado que precisa permanecer
```

### Efeito na qualidade

A suíte deixou de repetir “deve falhar” e passou a distinguir a classe do erro e o efeito colateral. O mesmo verbo `POST /payment` ficou com dois destinos diferentes: data futura em `422`, valor divergente em `409`. O `DELETE`, que na primeira rodada apagava o recurso, passou a preservar a conta. Esses casos viraram INT-06 a INT-10.
