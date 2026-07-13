# Etapa 3 — Definição de Estratégias de Resposta

**Projeto:** Micro-API de Contas a Pagar (ProjetoLaboratorio)  
**Data:** 13/07/2026  
**Base:** Riscos prioritários identificados nas Etapas 1 e 2

---

## Estratégias por Risco

As estratégias seguem as categorias clássicas de gestão de riscos: **evitar**, **mitigar**, **transferir** ou **aceitar**.

---

### R01 — Perda de dados por armazenamento em memória

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | Substituir completamente o armazenamento em memória por banco de dados neste estágio do MVP aumentaria escopo e complexidade de forma desproporcional. A mitigação com persistência em arquivo ou SQLite atende a necessidade mínima de continuidade sem abandonar a simplicidade arquitetural. |
| **Ações associadas** | Implementar persistência em SQLite como evolução do repositório, mantendo a interface atual. Documentar claramente que reinícios apagam dados até a migração. Criar script de seed com dados de demonstração para apresentações. Evitar demonstrações longas sem recarga prévia de dados. |

---

### R02 — Exposição da API sem autenticação

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | A autenticação é requisito obrigatório do escopo (RNF03) e o risco tem impacto alto. Implementar autenticação simples por API key ou token estático atende ao MVP sem exigir infraestrutura complexa. Evitar o risco (não expor a API) não é viável, pois a entrega depende da demonstração funcional. |
| **Ações associadas** | Implementar middleware de autenticação conforme RT04 do backlog. Proteger todos os endpoints de contas a pagar. Documentar o mecanismo no README e na coleção Postman. Retornar HTTP 401 para credenciais inválidas ou ausentes. Adicionar testes para cenários autenticado e não autenticado. |

---

### R03 — Não conformidade com o escopo do MVP

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | O escopo está bem definido e a base técnica já existe. Mitigar por meio de priorização e entregas incrementais é mais realista do que tentar evitar (reduzir escopo sem alinhamento) ou aceitar a não conformidade, que comprometeria a avaliação. |
| **Ações associadas** | Priorizar itens obrigatórios da Release 2: autenticação (RT04), filtros (RF07), paginação e ordenação (RF08). Formalizar em documento quais itens serão entregues na versão final e quais ficam como evolução futura. Executar checklist RT08 de validação final contra `escopo-mvp.md`. Atualizar README para refletir estado real após cada release. |

---

### R04 — Vazamento ou mau uso de credenciais sensíveis

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | Credenciais são necessárias para o funcionamento da API e da integração opcional com IA. A transferência total do risco (ex.: serviço gerenciado de secrets) foge ao escopo acadêmico. A mitigação por boas práticas é suficiente e de baixo custo. |
| **Ações associadas** | Garantir que `.env` esteja no `.gitignore` e nunca seja versionado. Usar apenas `.env.example` com placeholders. Rotacionar chaves após demonstrações públicas. Não exibir credenciais em slides ou logs. Configurar limites de uso na conta OpenAI, quando aplicável. |

---

### R05 — Falha ou indisponibilidade na integração com IA externa

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Aceitar** (com mitigação complementar) |
| **Justificativa** | O componente já possui fallback obrigatório para heurística local. A dependência externa é opcional e não bloqueia o fluxo principal. Transferir o risco (SLA de terceiro) ou evitá-lo (remover IA) reduziria o valor diferencial do projeto. |
| **Ações associadas** | Manter `OPENAI_API_KEY` como opcional. Preservar o fallback local em todas as chamadas. Documentar que a prioridade por IA é recurso complementar. Monitorar timeout e registrar falhas sem interromper a operação. Considerar desabilitar chamada remota em demonstrações ao vivo. |

---

### R06 — Inconsistência em dados e regras financeiras

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | Dados financeiros incorretos têm impacto alto no domínio. As regras já estão implementadas, mas a mitigação contínua via testes e validação é essencial. Aceitar o risco seria inadequado dado o contexto financeiro. |
| **Ações associadas** | Ampliar testes automatizados para transições de status e cenários de borda (pagamento parcial bloqueado, datas inválidas, contas vencidas). Executar validação manual do fluxo ponta a ponta antes da entrega (RF12). Revisar regras de sincronização de status `overdue`. Manter bloqueio de remoção física para rastreabilidade. |

---

### R07 — Atraso na conclusão das releases pendentes

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | O atraso é provável dado o volume de itens pendentes, mas pode ser controlado com planejamento. Evitar o risco (cortar releases) só é viável com acordo formal com o orientador. A mitigação por cronograma e priorização é a abordagem mais equilibrada. |
| **Ações associadas** | Definir cronograma semanal com marcos para Release 2 e 3. Atribuir responsáveis por item do backlog. Realizar revisões curtas de progresso a cada entrega parcial. Identificar itens que podem ser simplificados sem violar critérios de aceite. Preparar plano de contingência com demonstração do Core caso a Release 2 atrase. |

---

### R08 — Cobertura de testes insuficiente para cenários críticos

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | Testes são investimento direto em qualidade e já fazem parte do backlog (RT05). A cobertura total de todos os cenários possíveis não é exigida no MVP, mas os fluxos críticos devem ser protegidos. |
| **Ações associadas** | Adicionar testes para autenticação assim que RT04 for implementado. Criar testes de integração para fluxo completo (cadastro → pagamento → consulta). Executar `pytest` antes de cada entrega. Documentar casos de teste manuais complementares para RT08. |

---

### R09 — Indisponibilidade do serviço em ambiente de demonstração

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | Falhas em demonstração têm impacto reputacional, mas são previsíveis em ambiente local. Mitigar com preparação prévia é mais eficaz do que transferir (hospedagem externa) neste estágio. |
| **Ações associadas** | Criar checklist pré-demonstração: ambiente virtual ativo, dependências instaladas, porta livre, dados de seed carregados. Testar a API na máquina de apresentação com antecedência. Preparar gravação ou screenshots como contingência. Documentar comandos de execução no `Makefile` (`make run`, `make test`). |

---

### R10 — Divergência entre documentação e implementação real

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | Documentação desalinhada gera expectativas incorretas. A mitigação por atualização contínua é de baixo esforço e alto retorno. O README já adota boa prática ao separar "implementado" de "pendente". |
| **Ações associadas** | Revisar README e `docs/` a cada release concluída. Manter seção "Limitações atuais" e "Próximos passos" sempre atualizadas. Indicar claramente no escopo o que é visão-alvo versus entregue. Usar OpenAPI como fonte de verdade para endpoints disponíveis. |

---

### R11 — Componente de prioridade por IA não integrado ao fluxo principal

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | A integração agrega valor ao projeto e está planejada. Evitar (remover o componente) desperdiçaria trabalho já realizado. Aceitar a situação atual é temporariamente aceitável, mas a mitigação deve ser executada antes da entrega final. |
| **Ações associadas** | Integrar `PriorityAdvisor` ao fluxo de criação ou consulta de contas. Expor campo de prioridade sugerida na resposta da API. Manter fallback local documentado. Incluir testes de integração do advisor no fluxo principal. Comunicar aos stakeholders que a priorização é sugestiva, não vinculante. |

---

### R12 — Concentração de conhecimento na equipe do laboratório

| Item | Detalhe |
|------|---------|
| **Estratégia** | **Mitigar** |
| **Justificativa** | Em equipes acadêmicas pequenas, a concentração de conhecimento é comum. Mitigar por documentação e revisão cruzada reduz o impacto sem exigir reestruturação da equipe. |
| **Ações associadas** | Manter README e diagrama de componentes atualizados. Realizar revisões de código entre pares antes de merges. Registrar decisões técnicas relevantes em `docs/`. Distribuir ownership de módulos (api, services, repositories) entre integrantes. |

---

## Resumo das Estratégias

| Risco | Estratégia | Prioridade |
|-------|------------|------------|
| R01 — Perda de dados em memória | Mitigar | Crítica |
| R02 — API sem autenticação | Mitigar | Crítica |
| R03 — Não conformidade com escopo | Mitigar | Alta |
| R04 — Vazamento de credenciais | Mitigar | Alta |
| R05 — Falha na IA externa | Aceitar (com mitigação) | Média |
| R06 — Inconsistência financeira | Mitigar | Média |
| R07 — Atraso nas releases | Mitigar | Alta |
| R08 — Cobertura de testes | Mitigar | Média |
| R09 — Indisponibilidade na demo | Mitigar | Média |
| R10 — Divergência documental | Mitigar | Média |
| R11 — IA não integrada | Mitigar | Média |
| R12 — Conhecimento concentrado | Mitigar | Média |

---

## Plano de Ação Consolidado (Próximas 4 Semanas)

1. **Semana 1:** Implementar autenticação (R02) e iniciar persistência SQLite (R01).
2. **Semana 2:** Entregar filtros, paginação e ordenação (R03); ampliar testes (R08).
3. **Semana 3:** Integrar `PriorityAdvisor` ao fluxo principal (R11); revisar documentação (R10).
4. **Semana 4:** Validação final RT08, checklist de demonstração (R09) e comunicação aos stakeholders.
