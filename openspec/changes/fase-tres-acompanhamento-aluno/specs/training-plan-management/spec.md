# Spec Delta

## Purpose

Permite que administradores e instrutores organizem prescrições de exercícios por aluno, com período de validade e parâmetros de execução, mantendo fichas anteriores consultáveis.

## ADDED Requirements

### Requirement: Administradores e instrutores podem manter fichas de treino

O sistema SHALL permitir que usuários `admin` e `instrutor` criem, consultem e editem fichas que identifiquem o aluno, o instrutor responsável, o objetivo, o período de validade e a lista ordenada de exercícios.

#### Scenario: Criar ficha válida
- **WHEN** um usuário autorizado cria uma ficha com aluno, instrutor responsável, objetivo, período válido e ao menos um exercício ativo
- **THEN** o sistema persiste a ficha e apresenta seus dados e exercícios na ordem definida

#### Scenario: Rejeitar ficha incompleta
- **WHEN** uma solicitação não informa os dados obrigatórios, informa fim anterior ao início ou não contém exercício
- **THEN** o sistema rejeita a solicitação sem criar ou alterar uma ficha

#### Scenario: Editar ficha
- **WHEN** um usuário autorizado altera uma ficha não arquivada com dados válidos
- **THEN** o sistema persiste as alterações e mantém fichas arquivadas e avaliações físicas inalteradas

#### Scenario: Exercício com parâmetros inválidos
- **WHEN** uma ficha contém séries ou repetições não positivas, carga negativa ou exercício desativado
- **THEN** o sistema rejeita a solicitação sem persistir alterações parciais

### Requirement: O histórico de fichas é preservado

O sistema SHALL permitir arquivar fichas sem exclusão física e SHALL manter fichas arquivadas consultáveis como histórico.

#### Scenario: Arquivar ficha
- **WHEN** um usuário autorizado arquiva uma ficha
- **THEN** a ficha deixa de ser apresentada como vigente e permanece consultável no histórico

#### Scenario: Consultar fichas de um aluno
- **WHEN** um usuário autorizado consulta as fichas de um aluno
- **THEN** o sistema apresenta fichas vigentes e arquivadas, distinguindo sua situação e período

### Requirement: Fichas e dados dos alunos exigem autorização de administrador ou instrutor

O sistema SHALL validar no backend a autenticação e o perfil `admin` ou `instrutor` para consultar ou alterar fichas, sem conceder acesso a `recepcionista` ou `member`.

#### Scenario: Usuário sem perfil autorizado acessa fichas
- **WHEN** uma pessoa sem sessão ou com perfil `recepcionista` ou `member` consulta ou altera uma ficha
- **THEN** o backend rejeita a solicitação sem revelar informações do aluno nem alterar registros

#### Scenario: Instrutor ou administrador consulta fichas
- **WHEN** um usuário autenticado com perfil `instrutor` ou `admin` consulta fichas
- **THEN** o backend permite a operação de acordo com sua autorização e a interface não expõe dados pessoais além dos necessários para identificar o aluno
