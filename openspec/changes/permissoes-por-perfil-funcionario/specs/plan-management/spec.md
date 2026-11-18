# Spec Delta

## MODIFIED Requirements

### Requirement: Administradores podem consultar e manter planos

O sistema SHALL permitir que usuários `admin` consultem, cadastrem e editem planos com nome, descrição opcional, duração em meses inteiros e valor em reais maior que zero. O sistema SHALL permitir que usuários `recepcionista` consultem somente planos ativos necessários à criação de matrículas, sem acesso à tela ou às operações de configuração dos planos.

#### Scenario: Cadastro de plano válido
- **WHEN** um usuário `admin` cadastra um plano com nome, duração positiva em meses e valor maior que zero
- **THEN** o sistema persiste o plano como ativo e confirma o cadastro

#### Scenario: Cadastro de plano inválido
- **WHEN** um usuário `admin` envia um plano sem nome, com duração não positiva ou com valor não positivo
- **THEN** o sistema rejeita o cadastro, informa os campos inválidos e não cria o plano

#### Scenario: Edição de plano existente
- **WHEN** um usuário `admin` altera os dados de um plano existente
- **THEN** o sistema persiste as alterações para novas matrículas sem alterar matrículas já contratadas

#### Scenario: Recepcionista consulta opções de matrícula
- **WHEN** um usuário `recepcionista` consulta planos para criar uma matrícula
- **THEN** o sistema retorna somente planos ativos e não permite criar, editar, descontinuar ou reativar planos

#### Scenario: Usuário sem perfil autorizado consulta ou mantém planos
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` e do acesso de leitura operacional `recepcionista` consulta ou altera planos
- **THEN** o backend rejeita a solicitação sem revelar dados protegidos nem alterar registros

#### Scenario: Usuário sem perfil administrativo tenta manter planos
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` consulta ou altera planos
- **THEN** o backend rejeita a solicitação sem revelar dados protegidos nem alterar registros

### Requirement: Planos podem ser descontinuados sem exclusão física

O sistema SHALL permitir que apenas usuários `admin` descontinuem ou reativem planos sem exclusão física e SHALL impedir que planos descontinuados sejam usados em novas matrículas.

#### Scenario: Descontinuar plano disponível
- **WHEN** um usuário `admin` descontinua um plano
- **THEN** o sistema mantém o plano consultável como descontinuado e não o oferece para novas matrículas

#### Scenario: Matrícula existente usa plano descontinuado
- **WHEN** um plano é descontinuado após já ter sido contratado por uma matrícula
- **THEN** a matrícula existente permanece consultável e preserva seus dados contratados

#### Scenario: Usuário sem perfil administrativo tenta alterar situação de plano
- **WHEN** uma pessoa sem perfil `admin` tenta descontinuar ou reativar um plano
- **THEN** o backend rejeita a solicitação e mantém o plano sem alterações

#### Scenario: Usuário sem perfil administrativo tenta descontinuar plano
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta descontinuar um plano
- **THEN** o backend rejeita a solicitação e mantém o plano sem alterações

### Requirement: O valor do plano representa uma parcela mensal

O sistema SHALL interpretar o valor cadastrado em um plano como o valor integral de cada mensalidade, independentemente da duração em meses do plano.

#### Scenario: Consultar o valor do plano
- **WHEN** um usuário autorizado consulta um plano
- **THEN** a interface identifica o valor apresentado como valor mensal

#### Scenario: Atualizar plano após matrícula existente
- **WHEN** o valor mensal de um plano é alterado após a criação de uma matrícula
- **THEN** as mensalidades da matrícula existente preservam o valor mensal contratado
