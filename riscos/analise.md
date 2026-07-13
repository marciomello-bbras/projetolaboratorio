# Etapa 2 — Análise dos Riscos

**Projeto:** Micro-API de Contas a Pagar (ProjetoLaboratorio)  
**Data:** 13/07/2026  
**Base:** Riscos identificados na Etapa 1 (`identificacao.md`)

---

## Metodologia

A análise qualitativa considera três dimensões para cada risco:

- **Probabilidade:** Baixa | Média | Alta
- **Impacto:** Baixo | Médio | Alto
- **Prioridade resultante:** derivada da combinação probabilidade × impacto

---

## Análise Estruturada dos Riscos

### R01 — Perda de dados por armazenamento em memória

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Alta** |
| Impacto | **Alto** |
| Prioridade | **Crítica** |

**Impactos no projeto:**
- Perda total de registros financeiros após reinício do serviço.
- Impossibilidade de validar o MVP em uso contínuo ou simulação prolongada.
- Redução da credibilidade do sistema perante stakeholders que esperam persistência mínima.

**Fatores condicionantes:**
- Decisão arquitetural deliberada para simplificar o MVP (repositório em memória).
- Uso de `--reload` no Uvicorn, que reinicia o processo a cada alteração de código.
- Ausência de banco de dados ou mecanismo de serialização em arquivo.
- Volume baixo de dados no ambiente acadêmico, o que pode mascarar a gravidade do risco.

---

### R02 — Exposição da API sem autenticação

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Alta** |
| Impacto | **Alto** |
| Prioridade | **Crítica** |

**Impactos no projeto:**
- Acesso não autorizado a dados financeiros internos.
- Possibilidade de alteração ou cancelamento indevido de contas por terceiros.
- Não atendimento ao requisito RNF03 e ao item RT04 do backlog (Release 2).
- Reprovação ou ressalva na avaliação de conformidade do MVP.

**Fatores condicionantes:**
- Item RT04 ainda pendente de implementação.
- API atualmente voltada a ambiente local (`127.0.0.1`), o que reduz exposição externa imediata.
- Natureza acadêmica do projeto, com exposição limitada no curto prazo.
- Sensibilidade dos dados do domínio financeiro, que eleva o impacto mesmo em ambiente controlado.

---

### R03 — Não conformidade com o escopo do MVP

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Alto** |
| Prioridade | **Alta** |

**Impactos no projeto:**
- Entrega parcial em relação ao documento de escopo (`docs/escopo-mvp.md`).
- Necessidade de replanejamento ou formalização de descarte de requisitos.
- Percepção de produto incompleto pelos avaliadores e stakeholders simulados.

**Fatores condicionantes:**
- Release 1 (Core) substancialmente implementada.
- Release 2 (Qualidade) com itens críticos pendentes: filtros, paginação, autenticação.
- Documentação de escopo mais ampla que o estado atual do código.
- Tempo restante do laboratório e capacidade da equipe.

---

### R04 — Vazamento ou mau uso de credenciais sensíveis

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Alto** |
| Prioridade | **Alta** |

**Impactos no projeto:**
- Comprometimento de chaves de API (OpenAI e futuras credenciais internas).
- Custos financeiros inesperados por uso indevido da API da OpenAI.
- Violação de boas práticas de segurança e possível penalização em avaliação.

**Fatores condicionantes:**
- Existência de `.env.example` sem valores reais (prática correta).
- Risco aumenta se `.env` for acidentalmente versionado.
- Demonstrações ao vivo com variáveis visíveis na tela.
- Integração futura com autenticação por token estático ou API key.

---

### R05 — Falha ou indisponibilidade na integração com IA externa

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Médio** |
| Prioridade | **Média** |

**Impactos no projeto:**
- Latência adicional nas operações que utilizarem o `PriorityAdvisor` com chamada remota.
- Dependência de conectividade externa e serviço de terceiros.
- Experiência degradada se o fallback local não for percebido como suficiente pelo usuário.

**Fatores condicionantes:**
- Fallback obrigatório para heurística local já implementado.
- Timeout configurado em 5 segundos no `PriorityAdvisor`.
- Componente ainda não integrado ao fluxo principal (risco mitigado no curto prazo).
- `OPENAI_API_KEY` opcional — sem chave, apenas heurística local é usada.

---

### R06 — Inconsistência em dados e regras financeiras

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Baixa** |
| Impacto | **Alto** |
| Prioridade | **Média** |

**Impactos no projeto:**
- Registros financeiros com status ou valores incorretos.
- Perda de confiança no sistema por parte da equipe de finanças simulada.
- Dificuldade de auditoria e rastreabilidade das operações.

**Fatores condicionantes:**
- Regras de negócio já implementadas e parcialmente testadas (valor pago = valor previsto, bloqueio de operações em contas canceladas/pagas).
- Sincronização automática de status `overdue` pode gerar efeitos colaterais se mal calibrada.
- Crescimento do conjunto de regras sem testes proporcionais aumenta a probabilidade.

---

### R07 — Atraso na conclusão das releases pendentes

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Alto** |
| Prioridade | **Alta** |

**Impactos no projeto:**
- Entrega incompleta da Release 2 e 3 do backlog.
- Acúmulo de débito técnico e funcional nas semanas finais.
- Pressão sobre a equipe e qualidade reduzida por entregas apressadas.

**Fatores condicionantes:**
- Base técnica sólida já estabelecida (Release 1 concluída).
- Múltiplos itens pendentes com dependências entre si (ex.: autenticação antes do fluxo completo validado).
- Compromissos acadêmicos paralelos dos integrantes.
- Escopo bem documentado, o que facilita priorização.

---

### R08 — Cobertura de testes insuficiente para cenários críticos

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Médio** |
| Prioridade | **Média** |

**Impactos no projeto:**
- Regressões não detectadas ao adicionar autenticação, filtros e paginação.
- Bugs em produção/demonstração que poderiam ser evitados.
- Menor confiança na estabilidade do MVP na entrega final.

**Fatores condicionantes:**
- Suíte de testes existente cobrindo serviço, rotas e `PriorityAdvisor`.
- Novas funcionalidades da Release 2 ainda sem testes correspondentes.
- Ausência de pipeline de CI/CD automatizado.
- Projeto acadêmico com validação manual complementar prevista (RT08).

---

### R09 — Indisponibilidade do serviço em ambiente de demonstração

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Médio** |
| Prioridade | **Média** |

**Impactos no projeto:**
- Falha na apresentação do MVP para avaliadores ou stakeholders.
- Necessidade de demonstração manual ou gravação prévia como contingência.
- Impressão negativa sobre a maturidade operacional do projeto.

**Fatores condicionantes:**
- Dependência de ambiente Python local corretamente configurado.
- `Makefile` e `requirements.txt` reduzem variabilidade de setup.
- Ausência de containerização (Docker) ou script de verificação pré-demonstração.
- Uso de porta fixa (`8000`) que pode estar ocupada.

---

### R10 — Divergência entre documentação e implementação real

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Médio** |
| Prioridade | **Média** |

**Impactos no projeto:**
- Expectativas frustradas de quem lê o README sem testar a API.
- Questionamentos sobre transparência e gestão do projeto.
- Retrabalho para alinhar documentação antes da entrega final.

**Fatores condicionantes:**
- README atualizado com seção explícita de limitações e próximos passos.
- Menção clara de que `PriorityAdvisor` não está no fluxo principal.
- Documentos de escopo (`escopo-mvp.md`) descrevem visão-alvo, não estado atual.
- OpenAPI gerado automaticamente reflete apenas endpoints implementados.

---

### R11 — Componente de prioridade por IA não integrado ao fluxo principal

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Alta** |
| Impacto | **Médio** |
| Prioridade | **Média** |

**Impactos no projeto:**
- Diferencial técnico do projeto (IA assistida) não percebido pelo usuário final.
- Avaliação do componente de IA restrita a testes unitários, não ao fluxo operacional.
- Esforço de desenvolvimento sem retorno visível na API.

**Fatores condicionantes:**
- Decisão consciente de entregar o componente isolado antes da integração.
- Integração listada explicitamente nos próximos passos do README.
- Complexidade adicional de expor prioridade nos modelos de resposta da API.

---

### R12 — Concentração de conhecimento na equipe do laboratório

| Dimensão | Avaliação |
|----------|-----------|
| Probabilidade | **Média** |
| Impacto | **Médio** |
| Prioridade | **Média** |

**Impactos no projeto:**
- Gargalo de produtividade na ausência de integrantes-chave.
- Dificuldade de revisão cruzada e disseminação de conhecimento.
- Risco de decisões técnicas pouco documentadas.

**Fatores condicionantes:**
- Arquitetura em camadas bem definida (api, services, repositories, models).
- Documentação técnica no README e em `docs/`.
- Tamanho reduzido da equipe típica de laboratório acadêmico.
- Rotatividade de integrantes entre etapas do projeto.

---

## Matriz de Priorização

| Prioridade | Riscos |
|------------|--------|
| **Crítica** | R01, R02 |
| **Alta** | R03, R04, R07 |
| **Média** | R05, R06, R08, R09, R10, R11, R12 |

---

## Síntese da Análise

Os riscos mais críticos concentram-se em **persistência de dados** e **segurança de acesso**, ambos com probabilidade e impacto elevados no contexto atual do MVP. A **não conformidade com o escopo** e o **atraso nas releases pendentes** representam riscos altos de entrega, especialmente considerando os itens da Release 2 ainda não implementados.

Os riscos de impacto médio — integração com IA, testes, demonstração, documentação e conhecimento concentrado — são gerenciáveis com ações planejadas, mas exigem atenção para não se transformarem em bloqueios na reta final do laboratório.
