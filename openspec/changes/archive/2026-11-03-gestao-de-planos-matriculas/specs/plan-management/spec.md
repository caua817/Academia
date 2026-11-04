# Spec Delta: Gestão de planos

## Purpose

Permite que administradores configurem os planos comerciais oferecidos pela academia, preservando seu histórico e disponibilizando somente planos ativos para novas matrículas.

## ADDED Requirements

### Requirement: Administradores podem consultar e manter planos

O sistema SHALL permitir que usuários autenticados com perfil `admin` consultem, cadastrem e editem planos com nome, descrição opcional, duração em meses inteiros e valor em reais maior que zero.

#### Scenario: Cadastro de plano válido
- **WHEN** um usuário `admin` cadastra um plano com nome, duração positiva em meses e valor maior que zero
- **THEN** o sistema persiste o plano como ativo e confirma o cadastro

#### Scenario: Cadastro de plano inválido
- **WHEN** um usuário `admin` envia um plano sem nome, com duração não positiva ou com valor não positivo
- **THEN** o sistema rejeita o cadastro, informa os campos inválidos e não cria o plano

#### Scenario: Edição de plano existente
- **WHEN** um usuário `admin` altera os dados de um plano existente
- **THEN** o sistema persiste as alterações para novas matrículas sem alterar matrículas já contratadas

#### Scenario: Usuário sem perfil administrativo tenta manter planos
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` consulta ou altera planos
- **THEN** o backend rejeita a solicitação sem revelar dados protegidos nem alterar registros

### Requirement: Planos podem ser descontinuados sem exclusão física

O sistema SHALL permitir que administradores descontinuem planos sem excluir fisicamente seu registro e SHALL impedir que planos descontinuados sejam usados em novas matrículas.

#### Scenario: Descontinuar plano disponível
- **WHEN** um usuário `admin` descontinua um plano
- **THEN** o sistema mantém o plano consultável como descontinuado e não o oferece para novas matrículas

#### Scenario: Matrícula existente usa plano descontinuado
- **WHEN** um plano é descontinuado após já ter sido contratado por uma matrícula
- **THEN** a matrícula existente permanece consultável e preserva seus dados contratados

#### Scenario: Usuário sem perfil administrativo tenta descontinuar plano
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta descontinuar um plano
- **THEN** o backend rejeita a solicitação e mantém o plano sem alterações
