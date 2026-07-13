# Comunicação de Status do Projeto — Stakeholders

**Projeto:** Micro-API de Contas a Pagar  
**Data:** 13 de julho de 2026  
**Destinatários:** Orientadores acadêmicos, equipe de laboratório e representantes da área de finanças (usuários internos simulados)

---

## Contexto

A equipe do ProjetoLaboratorio está desenvolvendo uma **micro-API REST** para apoiar o processo interno de **contas a pagar**. O MVP foi concebido para substituir controles manuais dispersos por uma base padronizada de dados financeiros, acessível via HTTP/JSON por sistemas internos ou interfaces futuras.

O projeto segue uma arquitetura em camadas (API, serviços, repositório e modelos) com **Python 3.12**, **FastAPI** e **Pydantic**, organizado em três releases: Core, Qualidade e Entrega Final. A Release 1 (Core) encontra-se **substancialmente concluída**, com o fluxo principal de cadastro, consulta, atualização, cancelamento e pagamento de contas operacional e coberto por testes automatizados.

---

## Situação Atual

### O que já foi entregue

- Fluxo completo de contas a pagar: criação, listagem, consulta por ID, atualização, registro de pagamento e cancelamento.
- Validações de negócio implementadas (valores positivos, campos obrigatórios, bloqueio de operações em contas canceladas ou pagas).
- Identificação de contas vencidas com endpoint dedicado (`/accounts-payable/overdue`).
- Bloqueio de remoção física para preservar rastreabilidade mínima.
- Documentação OpenAPI automática (Swagger UI) e coleção Postman para testes.
- Componente `PriorityAdvisor` com heurística local e fallback seguro para sugestão de prioridade por IA.
- Suíte de testes automatizados (serviço, rotas e componente de IA) com resultado estável.

### O que está em andamento

- Implementação de **autenticação interna simples** (requisito RNF03 do escopo).
- Evolução da listagem com **filtros, paginação e ordenação** (Release 2 — Qualidade).
- Integração do componente de **prioridade assistida por IA** ao fluxo principal da API.
- Ampliação da cobertura de testes para as novas funcionalidades.
- Revisão e alinhamento da documentação com o estado real da implementação.

---

## Riscos Monitorados

A equipe identificou e analisou 12 riscos associados ao projeto. Os mais relevantes para os stakeholders são:

| Risco | Situação | Ação em curso |
|-------|----------|---------------|
| **Perda de dados ao reiniciar a API** | O armazenamento atual é em memória; reinícios apagam registros. | Planejada migração para persistência em SQLite, mantendo a simplicidade do MVP. |
| **API sem autenticação** | Endpoints acessíveis sem credencial, em desacordo com o escopo. | Implementação de autenticação por API key prevista para a Release 2. |
| **Itens do escopo ainda pendentes** | Filtros, paginação e autenticação não implementados. | Priorização dos itens obrigatórios da Release 2 no cronograma das próximas semanas. |
| **Componente de IA isolado** | O `PriorityAdvisor` existe, mas ainda não aparece nas operações da API. | Integração planejada para expor prioridade sugerida nas respostas. |

Riscos de impacto médio — como falhas na API externa de IA (com fallback local já ativo), cobertura de testes e preparação para demonstração — estão sendo gerenciados com ações preventivas documentadas no plano de resposta da equipe.

---

## Ações em Andamento

1. **Autenticação (RT04):** Desenvolvimento de middleware de proteção para todos os endpoints, com documentação do mecanismo escolhido.
2. **Listagem avançada (RF07, RF08):** Implementação de filtros por status, fornecedor, categoria e intervalo de vencimento, com paginação e ordenação.
3. **Persistência de dados:** Avaliação e implementação de SQLite como evolução do repositório em memória.
4. **Testes e validação:** Ampliação da suíte de testes e preparação do checklist de validação final (RT08).
5. **Documentação:** Atualização contínua do README e documentos em `docs/` para refletir o que está implementado versus o que é planejado.

---

## Próximos Passos

| Prazo estimado | Entrega |
|----------------|---------|
| **Próximas 2 semanas** | Autenticação funcional, filtros e paginação na listagem. |
| **Semana 3** | Integração do `PriorityAdvisor` ao fluxo principal; persistência em SQLite. |
| **Semana 4** | Validação final do MVP contra critérios de aceite; preparação para demonstração. |
| **Entrega final** | MVP consolidado com documentação alinhada, testes estáveis e ambiente de demonstração validado. |

---

## Mensagem aos Stakeholders

O projeto avança de forma consistente: a **base funcional está sólida** e o fluxo principal de contas a pagar já pode ser demonstrado. Os riscos identificados são **conhecidos, analisados e possuem plano de resposta**, sem bloqueios que impeçam a conclusão do MVP dentro do cronograma acadêmico.

As prioridades imediatas são **segurança** (autenticação), **conformidade com o escopo** (filtros e paginação) e **confiabilidade** (persistência de dados). A equipe manterá comunicação periódica sobre o progresso e eventuais ajustes de prioridade, sempre com transparência sobre o que está entregue e o que permanece em desenvolvimento.

Para dúvidas ou alinhamento de expectativas, a equipe está disponível para reunião de status ou demonstração assistida da API via Swagger UI (`http://127.0.0.1:8000/docs`).

---

*Documento gerado como parte da gestão de riscos do ProjetoLaboratorio — Laboratório de Pós-Graduação.*
