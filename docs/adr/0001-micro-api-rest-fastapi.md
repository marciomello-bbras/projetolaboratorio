# ADR-0001: Micro-API REST com FastAPI

- Status: Aceita
- Data: 2026-09-01
- Decisores: equipe do laboratório

## Contexto

O MVP precisa expor o ciclo mínimo de contas a pagar para consumo interno, com contrato HTTP/JSON, validação de entrada e documentação explorável. O escopo restringe a solução a uma micro-API de um único domínio (RNF01), sem ERP, filas ou interface gráfica própria.

## Decisão

Implementar uma micro-API REST em Python 3.12+ com FastAPI, Pydantic e Uvicorn.

A API é o único ponto de entrada. O contrato OpenAPI é gerado pela própria framework (`/docs` e `/openapi.json`).

## Alternativas consideradas

- **Flask + marshaling manual:** mais código de roteamento e documentação, sem ganho para o MVP.
- **Django REST Framework:** adequado a sistemas maiores, excessivo para um domínio único sem ORM.
- **Serviço gRPC ou mensageria:** fora do requisito de HTTP/JSON e do público interno do laboratório.

## Consequências

Positivas:

- contrato JSON e códigos HTTP padronizados com pouco boilerplate;
- validação de entrada acoplada aos schemas;
- documentação interativa disponível sem ferramenta extra.

Negativas:

- o desenho assume um único processo síncrono;
- evolução para múltiplos bounded contexts exigiria novo recorte, não apenas novas rotas.

## Referências

- `app/main.py`
- `docs/escopo-mvp.md` (RNF01, RNF02, RNF07)
