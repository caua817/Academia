# Spec Delta

## Purpose

Permite que administradores organizem as modalidades oferecidas pela academia e as disponibilizem para sessões de aula sem perder o histórico operacional.

## ADDED Requirements

### Requirement: Administradores podem manter modalidades

O sistema SHALL permitir que usuários `admin` cadastrem, consultem e editem modalidades com nome e descrição opcional.

#### Scenario: Cadastrar modalidade válida
- **WHEN** um usuário `admin` cadastra uma modalidade com nome válido
- **THEN** o sistema persiste a modalidade como ativa e a disponibiliza para novas sessões

#### Scenario: Rejeitar modalidade sem nome
- **WHEN** um usuário `admin` envia uma modalidade sem nome
- **THEN** o sistema rejeita o cadastro sem criar um registro

#### Scenario: Editar modalidade
- **WHEN** um usuário `admin` altera o nome ou a descrição de uma modalidade
- **THEN** o sistema persiste os dados atualizados sem alterar as sessões e reservas já registradas

#### Scenario: Usuário sem perfil administrativo consulta ou altera modalidades
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta consultar ou alterar modalidades
- **THEN** o backend rejeita a solicitação sem revelar dados nem alterar registros

### Requirement: Modalidades são desativadas sem apagar histórico

O sistema SHALL permitir que administradores desativem modalidades sem exclusão física e SHALL impedir seu uso em novas sessões.

#### Scenario: Desativar modalidade disponível
- **WHEN** um usuário `admin` desativa uma modalidade
- **THEN** a modalidade permanece consultável no histórico e deixa de estar disponível para novas sessões

#### Scenario: Sessão existente usa modalidade desativada
- **WHEN** uma modalidade é desativada depois de associada a uma sessão
- **THEN** os dados e reservas da sessão permanecem consultáveis
