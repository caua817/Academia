# attendance-management Specification

## Purpose

Permite registrar e consultar a presença de alunos na academia, vinculando cada check-in à elegibilidade atual do aluno sem usar o frontend como mecanismo de autorização.

## Requirements

### Requirement: Administradores podem registrar check-ins elegíveis

O sistema SHALL permitir que usuários autenticados com perfil `admin` registrem a entrada de um aluno ativo que possua matrícula vigente na data do check-in.

#### Scenario: Check-in de aluno e matrícula ativos
- **WHEN** um usuário `admin` registra o check-in de um aluno ativo com matrícula vigente
- **THEN** o sistema persiste a presença com data e hora e identifica o usuário responsável pelo registro

#### Scenario: Mensalidade vencida não bloqueia check-in
- **WHEN** um usuário `admin` registra o check-in de um aluno ativo com matrícula vigente e mensalidade atrasada
- **THEN** o sistema permite o check-in sem alterar a situação financeira

#### Scenario: Check-ins repetidos no mesmo dia
- **WHEN** um usuário `admin` registra mais de um check-in para o mesmo aluno no mesmo dia
- **THEN** o sistema persiste cada ocorrência sem deduplicação automática

#### Scenario: Aluno inativo ou sem matrícula vigente
- **WHEN** um usuário `admin` tenta registrar o check-in de um aluno inativo ou sem matrícula vigente
- **THEN** o sistema rejeita a operação sem criar um registro de presença

#### Scenario: Usuário sem perfil administrativo registra check-in
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta registrar um check-in
- **THEN** o backend rejeita a solicitação sem criar um registro de presença

### Requirement: Administradores podem consultar o histórico de check-ins

O sistema SHALL permitir que usuários `admin` consultem os registros de presença com aluno, data, hora e usuário responsável, sem expor dados cadastrais sensíveis desnecessários.

#### Scenario: Consultar histórico de presença
- **WHEN** um usuário `admin` consulta os check-ins
- **THEN** o sistema apresenta os registros de presença disponíveis

#### Scenario: Usuário sem perfil administrativo consulta check-ins
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta consultar check-ins
- **THEN** o backend rejeita a solicitação sem revelar dados de alunos

### Requirement: A interface de check-in distingue sucesso, vazio e falha

O sistema SHALL diferenciar carregamento, histórico vazio, sucesso e falhas da API ao registrar ou consultar check-ins.

#### Scenario: Falha ao registrar check-in
- **WHEN** a API rejeita ou não conclui um registro de check-in
- **THEN** a interface informa a falha e não apresenta confirmação de presença
