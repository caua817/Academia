# Spec Delta: Gestão de matrículas

## Purpose

Permite que administradores matriculem alunos ativos em planos ativos e consultem o período e as condições contratadas, sem perder o histórico quando planos mudam ou são descontinuados.

## ADDED Requirements

### Requirement: Administradores podem criar matrículas para alunos e planos ativos

O sistema SHALL permitir que usuários autenticados com perfil `admin` criem uma matrícula para um aluno ativo e um plano ativo, informando uma data de início igual ou anterior à data atual.

#### Scenario: Criar matrícula válida
- **WHEN** um usuário `admin` matricula um aluno ativo em um plano ativo com início hoje ou no passado
- **THEN** o sistema persiste a matrícula e confirma sua criação

#### Scenario: Aluno ou plano inativo
- **WHEN** um usuário `admin` tenta matricular um aluno inativo ou selecionar um plano descontinuado
- **THEN** o sistema rejeita a matrícula sem alterar registros

#### Scenario: Data de início futura
- **WHEN** um usuário `admin` tenta criar uma matrícula com início posterior à data atual
- **THEN** o sistema rejeita a matrícula e informa que o início futuro não é permitido

#### Scenario: Usuário sem perfil administrativo tenta criar matrícula
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta criar uma matrícula
- **THEN** o backend rejeita a solicitação sem criar registros

### Requirement: A matrícula preserva as condições contratadas e calcula o término

O sistema SHALL armazenar na matrícula o valor e a duração em meses vigentes no plano no momento da contratação, calcular a data de término por meses de calendário e manter essas condições independentemente de alterações posteriores no plano.

#### Scenario: Término no mesmo dia do mês final
- **WHEN** uma matrícula de um mês começa em um dia existente no mês seguinte
- **THEN** a data de término é o mesmo dia do mês seguinte, inclusive

#### Scenario: Término em mês sem o dia correspondente
- **WHEN** o dia de início não existe no mês de término calculado
- **THEN** a data de término usa o último dia daquele mês

#### Scenario: Alteração do plano após a contratação
- **WHEN** o valor ou a duração de um plano é alterado depois de uma matrícula ter sido criada
- **THEN** o valor contratado, a duração contratada e o término da matrícula existente permanecem inalterados

### Requirement: Um aluno não pode ter períodos de matrícula sobrepostos

O sistema SHALL impedir a criação de uma matrícula cujo período se sobreponha ao período de qualquer outra matrícula do mesmo aluno, inclusive matrículas encerradas.

O sistema SHALL serializar as criações de matrícula do mesmo aluno no backend para que requisições simultâneas não persistam períodos sobrepostos.

#### Scenario: Novo período se sobrepõe a uma matrícula existente
- **WHEN** um usuário `admin` tenta criar uma matrícula cujo período se sobrepõe ao de outra matrícula do aluno
- **THEN** o sistema rejeita a nova matrícula e mantém as matrículas existentes sem alterações

#### Scenario: Matrícula anterior terminou antes do novo início
- **WHEN** um usuário `admin` cria uma matrícula para um aluno cuja matrícula anterior terminou antes do novo início
- **THEN** o sistema permite a nova matrícula se o aluno e o plano estiverem ativos

#### Scenario: Requisições simultâneas tentam criar períodos sobrepostos
- **WHEN** duas requisições `admin` simultâneas tentam matricular o mesmo aluno em períodos que se sobrepõem
- **THEN** no máximo uma matrícula é persistida e a outra requisição é rejeitada sem alterar o registro persistido

### Requirement: Administradores podem consultar matrículas e sua situação

O sistema SHALL permitir que usuários `admin` consultem matrículas com aluno, plano, datas, valor contratado e situação, apresentando como ativa a matrícula cujo período inclui a data atual e como encerrada a matrícula cujo término já passou.

#### Scenario: Consultar matrícula ativa
- **WHEN** um usuário `admin` consulta uma matrícula cuja data de início já chegou e cujo término ainda não passou
- **THEN** o sistema apresenta a matrícula como ativa e exibe as condições contratadas

#### Scenario: Consultar matrícula encerrada
- **WHEN** um usuário `admin` consulta uma matrícula cuja data de término já passou
- **THEN** o sistema apresenta a matrícula como encerrada e preserva seus dados históricos

#### Scenario: Usuário sem perfil administrativo consulta matrículas
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` consulta matrículas
- **THEN** o backend rejeita a solicitação sem revelar dados de alunos ou condições comerciais
