# ADR-0005: Envelope padronizado de sucesso e erro HTTP

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

Clientes internos e a coleção Postman precisam distinguir sucesso, validação, recurso inexistente e violação de regra sem parsear formatos distintos por rota (RT03, RNF04).

## Decisão

Padronizar dois envelopes:

- sucesso: `{ sucesso: true, mensagem, dados }`;
- erro: `{ sucesso: false, erro: { codigo, mensagem, detalhes? } }`.

Mapeamento HTTP:

- `422` validação de contrato (Pydantic);
- `404` conta inexistente;
- `409` estado inválido ou remoção física bloqueada.

Handlers globais em `app/main.py` convertem exceções de domínio nesses códigos. Rotas de sucesso passam por `success_response`.

## Alternativas consideradas

- **Corpo cru do recurso sem envelope:** menos verboso, mensagens e metadados ficam em headers ou implícitos.
- **Problem Details (RFC 7807):** padrão amplo, exigiria adaptar Postman, testes e OpenAPI já existentes.
- **Códigos só na mensagem de texto:** frágil para o cliente tratar ramo a ramo.

## Consequências

Positivas:

- cliente único para todas as rotas;
- testes de rota afirmam `sucesso`, `mensagem` e `erro.codigo`;
- OpenAPI documenta os mesmos modelos de erro.

Negativas:

- payload de sucesso é um nível mais profundo (`dados`);
- códigos internos (`estado_invalido`, `conta_nao_encontrada`) são contrato: mudá-los quebra clientes.

## Referências

- `app/api/responses.py`
- `app/main.py`
- `docs/backlog.md` (RT03)
