# Spec Delta

## MODIFIED Requirements

### Requirement: Administradores podem registrar check-ins elegíveis

O sistema SHALL permitir que usuários autenticados com perfil `admin` ou `recepcionista` registrem a entrada de um aluno ativo que possua matrícula vigente na data do check-in.

#### Scenario: Check-in de aluno e matrícula ativos
- **WHEN** um usuário `admin` ou `recepcionista` registra o check-in de um aluno ativo com matrícula vigente
- **THEN** o sistema persiste a presença com data e hora e identifica o usuário responsável pelo registro

#### Scenario: Mensalidade vencida não bloqueia check-in
- **WHEN** um usuário autorizado registra o check-in de um aluno ativo com matrícula vigente e mensalidade atrasada
- **THEN** o sistema permite o check-in sem alterar a situação financeira

#### Scenario: Check-ins repetidos no mesmo dia
- **WHEN** um usuário autorizado registra mais de um check-in para o mesmo aluno no mesmo dia
- **THEN** o sistema persiste cada ocorrência sem deduplicação automática

#### Scenario: Aluno inativo ou sem matrícula vigente
- **WHEN** um usuário autorizado tenta registrar o check-in de um aluno inativo ou sem matrícula vigente
- **THEN** o sistema rejeita a operação sem criar um registro de presença

#### Scenario: Perfil sem autorização registra check-in
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` ou `recepcionista` tenta registrar um check-in
- **THEN** o backend rejeita a solicitação sem criar um registro de presença

#### Scenario: Usuário sem perfil administrativo registra check-in
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta registrar um check-in
- **THEN** o backend rejeita a solicitação sem criar um registro de presença

### Requirement: Administradores podem consultar o histórico de check-ins

O sistema SHALL permitir que `admin` e `recepcionista` consultem o histórico operacional de check-ins e que `instrutor` consulte os dados mínimos de presença necessários ao acompanhamento, sem dados financeiros ou pessoais desnecessários.

#### Scenario: Administrador ou recepcionista consulta histórico
- **WHEN** um usuário `admin` ou `recepcionista` consulta os check-ins
- **THEN** o sistema apresenta os registros de presença disponíveis

#### Scenario: Consultar histórico de presença
- **WHEN** um usuário `admin` consulta os check-ins
- **THEN** o sistema apresenta os registros de presença disponíveis

#### Scenario: Instrutor consulta frequência
- **WHEN** um instrutor consulta a frequência dos alunos
- **THEN** o sistema apresenta aluno, data e hora da presença, sem expor dados financeiros ou cadastrais desnecessários

#### Scenario: Perfil não autorizado consulta check-ins
- **WHEN** uma pessoa sem sessão ou com perfil diferente de `admin`, `recepcionista` ou `instrutor` tenta consultar check-ins
- **THEN** o backend rejeita a solicitação sem revelar dados de alunos

#### Scenario: Usuário sem perfil administrativo consulta check-ins
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta consultar check-ins
- **THEN** o backend rejeita a solicitação sem revelar dados de alunos

### Requirement: A interface de check-in distingue sucesso, vazio e falha

O sistema SHALL diferenciar carregamento, histórico vazio, sucesso e falhas da API ao consultar check-ins ou registrar presença por `admin` ou `recepcionista`. Para instrutores, a interface SHALL apresentar apenas consulta de frequência e SHALL omitir ações de registro.

#### Scenario: Falha ao registrar check-in
- **WHEN** a API rejeita ou não conclui um registro de check-in
- **THEN** a interface informa a falha e não apresenta confirmação de presença

#### Scenario: Instrutor abre frequência
- **WHEN** um instrutor acessa a consulta de check-ins
- **THEN** a interface permite consultar o histórico e não apresenta a ação de registrar presença
