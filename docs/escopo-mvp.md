# Escopo do MVP - Micro-API de Contas a Pagar

## Objetivo
Disponibilizar uma micro-API para suportar o processo interno de contas a pagar de uma equipe de finanças, com foco em registro, consulta, atualização de status e controle básico de vencimentos e pagamentos.

O MVP deve atender o fluxo operacional essencial, reduzindo controles manuais dispersos e permitindo que sistemas internos ou interfaces futuras consumam uma base padronizada de dados financeiros a pagar.

## Escopo do MVP
O produto cobre o ciclo minimo de uma conta a pagar, desde o cadastro ate a marcacao como paga ou cancelada, com persistencia dos dados e exposicao por API HTTP.

O foco do MVP e validar a operacao interna com baixo custo de implementacao, priorizando simplicidade, rastreabilidade basica e consistencia dos registros.

## Requisitos Funcionais
### RF01 - Cadastro de conta a pagar
A API deve permitir o cadastro de uma conta a pagar com, no minimo, os seguintes campos:

- identificador unico
- descricao
- fornecedor ou favorecido
- categoria
- centro de custo, quando informado
- valor previsto
- data de vencimento
- data de emissao, quando informada
- observacoes, quando informadas
- status inicial

### RF02 - Consulta de contas a pagar
A API deve permitir listar contas a pagar cadastradas.

A listagem deve suportar, no minimo, os seguintes filtros:

- status
- fornecedor ou favorecido
- intervalo de vencimento
- categoria

### RF03 - Consulta detalhada por identificador
A API deve permitir consultar uma conta a pagar especifica a partir do seu identificador unico.

### RF04 - Atualizacao de dados da conta
A API deve permitir atualizar dados cadastrais de uma conta a pagar enquanto ela nao estiver cancelada.

Os campos de identificacao tecnica do registro nao devem ser alterados manualmente.

### RF05 - Atualizacao de status
A API deve permitir alterar o status de uma conta a pagar conforme o fluxo operacional minimo abaixo:

- `PENDENTE`: conta criada e ainda nao paga
- `PAGA`: conta liquidada
- `VENCIDA`: conta com vencimento expirado e sem pagamento registrado
- `CANCELADA`: conta desconsiderada do fluxo

### RF06 - Registro de pagamento
Ao marcar uma conta como paga, a API deve permitir registrar, no minimo:

- data do pagamento
- valor pago
- observacao de pagamento, quando informada

### RF07 - Regras basicas de consistencia
A API deve validar, no minimo, as seguintes regras:

- valor previsto deve ser maior que zero
- data de vencimento e obrigatoria
- descricao e obrigatoria
- fornecedor ou favorecido e obrigatorio
- conta cancelada nao pode ser marcada como paga
- conta paga nao deve voltar para pendente no MVP

### RF08 - Exclusao logica ou bloqueio de remocao fisica
O MVP deve preservar rastreabilidade minima dos registros.

Para isso, a solucao deve adotar uma destas abordagens:

- exclusao logica, mantendo historico do registro
- bloqueio de exclusao fisica via API

### RF09 - Ordenacao e paginacao de listagem
As consultas de listagem devem suportar paginacao e ordenacao por, no minimo:

- data de vencimento
- data de criacao
- valor previsto

### RF10 - Indicacao de atraso
A API deve retornar informacao suficiente para identificar contas vencidas, considerando a data atual e a ausencia de pagamento registrado.

## Requisitos Nao Funcionais
### RNF01 - Arquitetura
A solucao deve ser implementada como micro-API REST, com responsabilidades restritas ao dominio de contas a pagar.

### RNF02 - Formato de dados
As entradas e saidas devem utilizar JSON.

### RNF03 - Persistencia
Os dados devem ser persistidos em base relacional ou nao relacional, desde que haja suporte a consultas por status, vencimento e fornecedor.

### RNF04 - Seguranca minima
O acesso a API deve exigir autenticacao para uso interno, mesmo que simplificada no MVP, como token estatico, API key ou mecanismo equivalente.

### RNF05 - Validacao e tratamento de erros
A API deve retornar codigos HTTP coerentes, mensagens objetivas de erro e validacoes de entrada consistentes.

### RNF06 - Observabilidade minima
O servico deve possuir logs basicos para:

- requisicoes recebidas
- falhas de validacao
- erros de processamento
- alteracoes de status

### RNF07 - Desempenho
O MVP deve responder adequadamente ao uso de uma equipe interna, priorizando estabilidade e previsibilidade sobre otimizacoes complexas.

Como referencia inicial, a API deve suportar volumes baixos a moderados sem degradacao perceptivel para o usuario interno.

### RNF08 - Manutenibilidade
O codigo deve ser organizado de forma simples e modular, permitindo evolucao futura para integracoes, aprovacoes e relatórios.

### RNF09 - Documentacao da API
O MVP deve possuir documentacao minima dos endpoints, payloads, respostas e codigos de erro, preferencialmente em formato OpenAPI ou equivalente.

### RNF10 - Ambiente
A solucao deve ser executavel em ambiente interno padronizado, com configuracao por variaveis de ambiente e sem dependencia de intervencoes manuais frequentes.

## Fora do Escopo
Os itens abaixo nao fazem parte deste MVP:

- fluxo de aprovacao multinivel
- integracao com ERP, banco, internet banking ou sistemas fiscais
- emissao de boletos, PIX, remessa bancaria ou conciliacao automatica
- anexacao e armazenamento de documentos fiscais
- motor de notificacoes por e-mail, SMS ou mensageria
- dashboard gerencial avancado e relatórios analiticos
- controle de orcamento corporativo
- gestao completa de fornecedores
- cadastro de impostos, rateios complexos ou contabilizacao automatica
- suporte a multiempresa, multimoeda ou operacao internacional
- trilha de auditoria completa com historico detalhado de cada alteracao
- controle de perfis e autorizacoes granulares por papel

## Criterio de Aceite do MVP
O MVP sera considerado aderente ao escopo quando permitir:

- cadastrar contas a pagar com validacoes basicas
- consultar registros por identificador e por filtros operacionais
- atualizar dados permitidos
- registrar pagamento e refletir o status correspondente
- identificar contas pendentes, pagas, canceladas e vencidas
- operar com autenticacao interna simples e persistencia confiavel
