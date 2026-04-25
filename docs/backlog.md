# Backlog Minimo do MVP

## Objetivo
Organizar a entrega do MVP da micro-API de contas a pagar em 3 releases sequenciais:

- `core`: capacidade funcional minima para operar o fluxo principal
- `qualidade`: aumento de robustez tecnica, confiabilidade e clareza de uso
- `entrega final`: fechamento do MVP para apresentacao e uso interno controlado

## Convencoes
- `RF`: requisito funcional implementado como item de backlog
- `RT`: requisito tecnico ou tarefa tecnica necessaria para suportar a entrega
- Status, prioridade e estimativa nao fazem parte deste documento

## Release 1 - Core
Objetivo da release: disponibilizar o fluxo minimo de cadastro, consulta e pagamento de contas a pagar.

### RF01 - Cadastrar conta a pagar
Descricao: Implementar endpoint para criar uma conta a pagar com os campos obrigatorios do MVP.

Criterios de aceite:
- deve ser possivel cadastrar conta com `descricao`, `fornecedor_ou_favorecido`, `categoria`, `valor_previsto` e `data_vencimento`
- o registro deve receber identificador unico
- o status inicial deve ser gravado como `PENDENTE`
- a API deve retornar sucesso com payload do registro criado

### RF02 - Consultar conta por identificador
Descricao: Implementar consulta detalhada de uma conta a pagar.

Criterios de aceite:
- deve ser possivel consultar uma conta existente pelo identificador
- a resposta deve retornar os campos principais cadastrados
- a API deve retornar erro coerente quando o identificador nao existir

### RF03 - Listar contas a pagar
Descricao: Implementar listagem basica de contas cadastradas.

Criterios de aceite:
- deve ser possivel listar contas a pagar existentes
- a resposta deve conter colecao de itens em formato JSON
- a listagem deve funcionar mesmo com zero registros, retornando colecao vazia

### RF04 - Atualizar dados da conta
Descricao: Permitir manutencao dos dados cadastrais da conta a pagar.

Criterios de aceite:
- deve ser possivel alterar campos permitidos de uma conta nao cancelada
- o identificador do registro nao pode ser alterado
- a API deve retornar os dados atualizados apos a operacao

### RF05 - Registrar pagamento
Descricao: Permitir registrar a liquidacao de uma conta.

Criterios de aceite:
- deve ser possivel informar `data_pagamento` e `valor_pago`
- ao registrar pagamento, o status deve ser alterado para `PAGA`
- uma conta cancelada nao pode ser marcada como paga

### RF06 - Atualizar status para cancelada
Descricao: Permitir cancelar uma conta dentro do fluxo minimo do MVP.

Criterios de aceite:
- deve ser possivel marcar uma conta como `CANCELADA`
- conta cancelada deve continuar consultavel
- conta cancelada nao pode receber registro de pagamento posterior

### RT01 - Estruturar projeto da micro-API
Descricao: Criar a base tecnica da aplicacao para suportar os endpoints do MVP.

Criterios de aceite:
- o projeto deve iniciar localmente sem ajustes manuais fora da configuracao prevista
- a estrutura deve separar pelo menos camadas de entrada, dominio e persistencia
- deve existir arquivo de configuracao de ambiente de exemplo

### RT02 - Modelar entidade de conta a pagar
Descricao: Criar o modelo de dados principal da aplicacao.

Criterios de aceite:
- a entidade deve refletir os campos obrigatorios do escopo
- deve existir persistencia dos dados em banco ou armazenamento definido
- o modelo deve suportar os status `PENDENTE`, `PAGA`, `VENCIDA` e `CANCELADA`

### RT03 - Implementar persistencia inicial
Descricao: Disponibilizar mecanismo de armazenamento para o fluxo core.

Criterios de aceite:
- registros criados devem permanecer disponiveis apos reinicio da aplicacao, quando aplicavel ao ambiente escolhido
- deve ser possivel buscar registros por identificador
- deve ser possivel atualizar e consultar registros sem perda de consistencia

### RT04 - Padronizar respostas e erros HTTP
Descricao: Definir contrato minimo de resposta da API.

Criterios de aceite:
- respostas de sucesso devem seguir formato consistente
- erros de validacao devem retornar codigo HTTP coerente
- erros por recurso inexistente devem retornar codigo HTTP coerente

## Release 2 - Qualidade
Objetivo da release: aumentar a confiabilidade operacional, cobertura do escopo e qualidade tecnica do servico.

### RF07 - Filtrar contas por status, fornecedor, categoria e vencimento
Descricao: Evoluir a listagem para suportar filtros operacionais.

Criterios de aceite:
- deve ser possivel filtrar por `status`
- deve ser possivel filtrar por `fornecedor_ou_favorecido`
- deve ser possivel filtrar por `categoria`
- deve ser possivel filtrar por intervalo de vencimento

### RF08 - Paginar e ordenar listagem
Descricao: Adicionar recursos de navegacao para listagens maiores.

Criterios de aceite:
- a listagem deve suportar paginacao
- a listagem deve suportar ordenacao por `data_vencimento`
- a listagem deve suportar ordenacao por `data_criacao` e `valor_previsto`

### RF09 - Identificar contas vencidas
Descricao: Sinalizar contas em atraso sem pagamento registrado.

Criterios de aceite:
- conta com vencimento expirado e sem pagamento deve ser identificada como vencida
- a resposta da API deve expor essa condicao de forma clara
- contas ja pagas nao devem ser marcadas como vencidas

### RF10 - Aplicar validacoes de negocio do MVP
Descricao: Garantir consistencia minima das operacoes do dominio.

Criterios de aceite:
- nao deve ser permitido cadastrar conta com `valor_previsto` menor ou igual a zero
- campos obrigatorios devem ser validados antes da persistencia
- conta paga nao deve retornar para `PENDENTE`
- a API deve responder com mensagem objetiva quando uma regra for violada

### RT05 - Implementar autenticacao interna simples
Descricao: Proteger os endpoints para uso interno.

Criterios de aceite:
- chamadas sem credencial valida nao devem acessar a API
- o mecanismo escolhido deve ser simples e documentado
- endpoints protegidos devem responder com erro coerente em caso de acesso nao autorizado

### RT06 - Adicionar logs basicos
Descricao: Registrar eventos essenciais para operacao e diagnostico.

Criterios de aceite:
- deve haver log de requisicoes recebidas
- deve haver log de falhas de validacao
- deve haver log de erros de processamento
- deve haver log de alteracao de status

### RT07 - Criar testes automatizados minimos
Descricao: Garantir cobertura das regras mais criticas do fluxo.

Criterios de aceite:
- deve haver testes para cadastro com sucesso
- deve haver testes para validacoes obrigatorias
- deve haver testes para registro de pagamento
- deve haver testes para bloqueio de operacoes invalidas relevantes

### RT08 - Documentar endpoints da API
Descricao: Publicar documentacao tecnica minima para consumo interno.

Criterios de aceite:
- deve existir documentacao dos endpoints disponiveis
- cada endpoint deve informar payload de entrada e resposta esperada
- erros principais devem estar documentados

## Release 3 - Entrega Final
Objetivo da release: consolidar o MVP, fechar pendencias de entrega e preparar demonstracao ou uso assistido.

### RF11 - Preservar rastreabilidade minima dos registros
Descricao: Impedir remocao irreversivel inadequada de contas no MVP.

Criterios de aceite:
- a solucao deve adotar exclusao logica ou bloqueio de exclusao fisica
- registros cancelados ou inativos devem continuar rastreaveis conforme abordagem adotada
- a regra implementada deve estar documentada

### RF12 - Finalizar fluxo operacional completo do MVP
Descricao: Validar o encadeamento do fluxo principal de ponta a ponta.

Criterios de aceite:
- deve ser possivel cadastrar, consultar, atualizar, pagar e cancelar contas conforme regras do MVP
- o fluxo completo deve funcionar com autenticacao habilitada
- os estados finais apresentados pela API devem ser coerentes com as operacoes executadas

### RT09 - Configurar ambiente de execucao final
Descricao: Consolidar parametros e instrucoes necessarias para subir o servico.

Criterios de aceite:
- a aplicacao deve poder ser executada com configuracao por variaveis de ambiente
- dependencias e parametros obrigatorios devem estar documentados
- o ambiente definido deve ser suficiente para demonstracao interna controlada

### RT10 - Executar validacao final da release
Descricao: Realizar checklist final de conformidade com o escopo do MVP.

Criterios de aceite:
- todos os itens obrigatorios das releases anteriores devem estar implementados ou formalmente descartados
- deve existir evidência de teste ou validacao manual dos fluxos principais
- a documentacao minima deve estar disponivel junto da entrega

## Resumo por Release
### Core
- RF01 a RF06
- RT01 a RT04

### Qualidade
- RF07 a RF10
- RT05 a RT08

### Entrega final
- RF11 a RF12
- RT09 a RT10

## Definicao Minima de Pronto
Um item do backlog sera considerado pronto quando:

- atender a descricao funcional ou tecnica proposta
- cumprir todos os criterios de aceite do item
- nao introduzir inconsistencias nas regras basicas do dominio
- estiver documentado quando isso fizer parte do proprio item
