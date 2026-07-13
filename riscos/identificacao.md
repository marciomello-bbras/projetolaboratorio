# Etapa 1 — Identificação de Riscos

**Projeto:** Micro-API de Contas a Pagar (ProjetoLaboratorio)  
**Data:** 13/07/2026  
**Objetivo:** Identificar riscos associados ao desenvolvimento e entrega do MVP da micro-API REST para o domínio de contas a pagar.

---

## Lista de Riscos Identificados

| ID | Risco | Categoria |
|----|-------|-----------|
| R01 | Perda de dados por armazenamento em memória | Técnico |
| R02 | Exposição da API sem autenticação | Segurança |
| R03 | Não conformidade com o escopo do MVP | Escopo / Entrega |
| R04 | Vazamento ou mau uso de credenciais sensíveis | Segurança |
| R05 | Falha ou indisponibilidade na integração com IA externa | Técnico / Operacional |
| R06 | Inconsistência em dados e regras financeiras | Negócio / Qualidade |
| R07 | Atraso na conclusão das releases pendentes | Cronograma |
| R08 | Cobertura de testes insuficiente para cenários críticos | Qualidade |
| R09 | Indisponibilidade do serviço em ambiente de demonstração | Operacional |
| R10 | Divergência entre documentação e implementação real | Comunicação / Qualidade |
| R11 | Componente de prioridade por IA não integrado ao fluxo principal | Escopo / Técnico |
| R12 | Concentração de conhecimento na equipe do laboratório | Recursos / Organizacional |

---

## Descrição e Contexto de Cada Risco

### R01 — Perda de dados por armazenamento em memória

**Descrição:** O repositório atual (`AccountsPayableRepository`) persiste contas a pagar apenas em estrutura em memória. Qualquer reinicialização do processo da API apaga todos os registros cadastrados.

**Contexto de ocorrência:** Durante desenvolvimento local, demonstrações acadêmicas, reinício do servidor (Uvicorn com `--reload`) ou falha inesperada do processo. Impacta diretamente a confiabilidade do MVP para uso contínuo, mesmo que interno.

---

### R02 — Exposição da API sem autenticação

**Descrição:** Os endpoints estão acessíveis sem mecanismo de autenticação, em desacordo com o requisito não funcional RNF03, que exige proteção mínima para uso interno.

**Contexto de ocorrência:** Quando a API for exposta em rede interna da instituição, ambiente de laboratório compartilhado ou demonstração com múltiplos participantes. Qualquer cliente HTTP pode criar, alterar ou consultar contas sem credencial.

---

### R03 — Não conformidade com o escopo do MVP

**Descrição:** Parte dos requisitos definidos em `docs/escopo-mvp.md` e `docs/backlog.md` ainda não foi implementada, como filtros, paginação, ordenação e autenticação (Release 2 — Qualidade).

**Contexto de ocorrência:** Na avaliação final do laboratório, na validação contra critérios de aceite do MVP ou na comparação entre o que foi prometido ao stakeholder (equipe de finanças simulada) e o que está disponível na API.

---

### R04 — Vazamento ou mau uso de credenciais sensíveis

**Descrição:** O projeto utiliza variáveis de ambiente para configuração (`OPENAI_API_KEY`, futuras chaves de API interna). Há risco de exposição acidental em repositório, logs ou compartilhamento de ambiente de demonstração.

**Contexto de ocorrência:** Ao versionar arquivos `.env`, compartilhar credenciais em coleções Postman, expor chaves em logs de erro ou durante apresentações ao vivo com tela compartilhada.

---

### R05 — Falha ou indisponibilidade na integração com IA externa

**Descrição:** O componente `PriorityAdvisor` pode realizar chamadas à API da OpenAI. Falhas de rede, timeout, indisponibilidade do serviço ou custo inesperado podem afetar a experiência quando a integração for ativada.

**Contexto de ocorrência:** Quando `OPENAI_API_KEY` estiver configurada e o componente for integrado ao fluxo principal. Embora exista fallback para heurística local, a dependência externa permanece como ponto de fragilidade.

---

### R06 — Inconsistência em dados e regras financeiras

**Descrição:** Erros nas regras de negócio (status, valores de pagamento, datas, transições de estado) podem gerar registros financeiros incorretos, como contas pagas com valor divergente ou status incoerente.

**Contexto de ocorrência:** Durante operações de cadastro, atualização, registro de pagamento e sincronização automática de contas vencidas. Especialmente relevante em cenários de borda não cobertos por testes.

---

### R07 — Atraso na conclusão das releases pendentes

**Descrição:** O backlog prevê três releases (Core, Qualidade e Entrega Final). Itens da Release 2 e 3 ainda estão pendentes, o que pode comprometer o cronograma acadêmico do laboratório.

**Contexto de ocorrência:** Nas semanas finais do projeto, quando múltiplos itens técnicos (autenticação, filtros, documentação final, validação de release) precisam ser concluídos em paralelo com outras disciplinas e atividades.

---

### R08 — Cobertura de testes insuficiente para cenários críticos

**Descrição:** Embora existam testes automatizados para serviço, rotas e `PriorityAdvisor`, a cobertura pode ser insuficiente para fluxos integrados, autenticação futura e cenários de concorrência ou volume.

**Contexto de ocorrência:** Ao introduzir novas funcionalidades (Release 2 e 3) sem ampliar a suíte de testes, aumentando a probabilidade de regressões não detectadas antes da entrega.

---

### R09 — Indisponibilidade do serviço em ambiente de demonstração

**Descrição:** A API roda como processo único sem mecanismos de alta disponibilidade, balanceamento ou recuperação automática. Falhas de ambiente (Python, dependências, porta ocupada) podem impedir a demonstração.

**Contexto de ocorrência:** Durante apresentações presenciais ou remotas do MVP, especialmente em máquinas de desenvolvimento não padronizadas ou sem ambiente virtual configurado corretamente.

---

### R10 — Divergência entre documentação e implementação real

**Descrição:** O README e documentos de apoio descrevem funcionalidades parcialmente implementadas ou planejadas (como integração da IA ao fluxo principal), o que pode gerar expectativas incorretas nos stakeholders.

**Contexto de ocorrência:** Quando orientadores, avaliadores ou usuários internos consultam a documentação assumindo que tudo descrito já está disponível na API em produção ou demonstração.

---

### R11 — Componente de prioridade por IA não integrado ao fluxo principal

**Descrição:** O `PriorityAdvisor` está implementado e testado, mas ainda não participa do fluxo de criação ou atualização de contas a pagar. Isso representa uma lacuna entre o diferencial técnico do projeto e o valor entregue ao usuário.

**Contexto de ocorrência:** Na avaliação do componente de IA do projeto ou quando stakeholders esperam priorização automática nas operações da API.

---

### R12 — Concentração de conhecimento na equipe do laboratório

**Descrição:** Em projetos acadêmicos de laboratório, o conhecimento sobre arquitetura, regras de negócio e configuração tende a ficar concentrado em poucos integrantes, criando dependência de pessoas-chave.

**Contexto de ocorrência:** Na ausência de um membro da equipe, durante revisões de código, manutenção pós-entrega ou continuidade do projeto para disciplinas subsequentes.
