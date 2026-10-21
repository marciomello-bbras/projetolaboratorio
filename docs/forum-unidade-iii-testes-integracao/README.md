# Unidade III — Prompts para testes de integração

Experimento com uma LLM no ciclo operacional da micro-API de contas a pagar. Os casos adotados estão executáveis em `tests/test_integracao_fluxo_contas.py`.

## Cenário de integração

O cliente HTTP conversa com a micro-API e o efeito de uma operação precisa aparecer na operação seguinte. O caminho atravessa quatro peças do mesmo processo:

1. `TestClient` (o papel do front-end ou de outro serviço consumidor);
2. rotas FastAPI em `/accounts-payable`;
3. `AccountsPayableService`, com a máquina de estados;
4. `AccountsPayableRepository`, em memória.

Não há banco externo nem autenticação (a autenticação foi adiada). O que se integra é o contrato HTTP com as regras de negócio e com o estado persistido.

Fluxo observado:

`POST` cria a conta em `pending` → `GET` e a listagem enxergam o mesmo registro → consulta de vencidas pode promover a conta a `overdue` → `PUT` altera dados cadastrais → `POST /payment` liquida só se o valor pago for igual ao previsto → `POST /cancel` torna o registro terminal → `DELETE` não apaga.

Envelope de sucesso: `{ sucesso, mensagem, dados }`. Envelope de erro: `{ sucesso: false, erro: { codigo, mensagem, detalhes? } }`.

Códigos internos usados pelo cliente:

| Situação | HTTP | `erro.codigo` |
| --- | --- | --- |
| Conta inexistente | 404 | `conta_nao_encontrada` |
| Estado ou valor incompatível | 409 | `estado_invalido` |
| Remoção física | 409 | `remocao_fisica_bloqueada` |
| Payload fora do schema | 422 | `erro_validacao` |

## Dois tipos de prompt

### 1. Prompt de cenários de integração

Pede jornadas com mais de uma chamada, para cobrir o caminho feliz e as transições de estado. O foco é a diversidade do fluxo: cadastro, consulta, atualização, vencimento, liquidação e cancelamento.

### 2. Prompt de casos de erro e de contrato

Pede falhas de schema, de regra e de política de retenção. O foco é a fronteira entre o que o contrato rejeita (`422`) e o que a regra de negócio rejeita (`409` ou `404`), e a garantia de que a falha não grava estado indevido.

Os textos usados, a primeira resposta e a versão ajustada estão em [prompts.md](prompts.md). A suíte resultante está em [casos-gerados.md](casos-gerados.md).

## Como cada tipo influenciou a suíte

O prompt de cenários puxou a cobertura para o tempo: cada caso só fecha quando a segunda requisição confirma a primeira. Sem esse pedido, a resposta colapsou em checagens isoladas de endpoint, parecidas com teste de unidade da rota. Com o pedido de “pelo menos duas chamadas”, surgiram cinco jornadas distintas (INT-01 a INT-05): visibilidade do cadastro, durabilidade da atualização, sincronização de vencidas na leitura, liquidação que sai da lista de overdue e cancelamento terminal.

O prompt de erro e contrato puxou a cobertura para o tipo de falha. A primeira versão misturava tudo em “erro 400”. A versão ajustada separou ausência de recurso, violação de schema e violação de regra, e exigiu um `GET` depois do erro. Isso produziu INT-06 a INT-10: `404` com código interno, `422` que não grava, `409` de liquidação que preserva `pending`, `DELETE` bloqueado com a conta ainda consultável, e a recusa de voltar uma vencida para `pending`.

A diversidade não veio de pedir “mais casos”. Veio de pedir dimensões diferentes: sequência de operações num prompt, classe de falha no outro. Os dois conjuntos quase não se sobrepõem. O primeiro responde “o ciclo fecha?”. O segundo responde “quando não fecha, o cliente sabe o motivo e o estado anterior continua íntegro?”.

## Ajustes que tornaram o resultado utilizável

A primeira rodada descrevia só o domínio (“API de contas a pagar”). A LLM inventou rotas (`/api/v1/bills`), autenticação JWT, pagamento parcial, paginação e `DELETE` com `204`. Parte disso contradiz o código: não há login, o valor pago tem de ser igual ao previsto, e a remoção física responde `409` com `remocao_fisica_bloqueada`.

Seis restrições corrigiram a geração:

1. Colar no prompt a lista real de rotas, os status (`pending`, `paid`, `overdue`, `cancelled`) e a tabela de códigos do envelope.
2. Proibir rota, header ou persistência que não esteja nessa lista. Autenticação ficou de fora de propósito.
3. Exigir, em todo cenário feliz, uma segunda chamada que observe o efeito da primeira.
4. Exigir, em todo caso de erro, um `GET` posterior provando que o estado não mudou.
5. Pedir `erro.codigo`, não só o status HTTP. O cliente desta API decide o ramo pelo código interno.
6. Separar explicitamente `422` (Pydantic, antes da regra) de `409` (regra já com a conta carregada). Data de pagamento futura é `422`; valor divergente e data anterior à emissão são `409`.

Com isso, os casos deixaram de ser uma suíte genérica de CRUD e passaram a ser afirmáveis no `TestClient`. A suíte foi executada com `py -3 -m pytest tests/test_integracao_fluxo_contas.py`: 16 testes passaram, contando as variações parametrizadas de INT-06 e INT-07.

## Limite do copiloto

A LLM acelerou o desenho da suíte e apontou fronteiras que um único teste de `POST 201` não cobre. Ela não substitui a leitura do contrato: sem as rotas e os códigos no prompt, os casos parecem completos e testam um sistema que não existe. O uso útil foi tratar a resposta como rascunho, confrontar com `app/api/accounts_payable_routes.py`, `app/services/accounts_payable_service.py` e o envelope em `app/main.py`, e só então versionar o que o teste realmente executa.
