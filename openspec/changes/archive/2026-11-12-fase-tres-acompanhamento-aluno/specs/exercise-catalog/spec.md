# Spec Delta

## Purpose

Permite que a equipe mantenha um catálogo reutilizável de exercícios para compor fichas de treino, preservando as referências históricas quando um exercício deixa de ser oferecido.

## ADDED Requirements

### Requirement: Administradores e instrutores podem manter o catálogo de exercícios

O sistema SHALL permitir que usuários `admin` e `instrutor` consultem, cadastrem e editem exercícios com nome obrigatório e grupo muscular, descrição e equipamento opcionais.

#### Scenario: Cadastrar exercício válido
- **WHEN** um usuário autorizado cadastra um exercício com nome preenchido
- **THEN** o sistema o persiste como ativo e o disponibiliza para novas fichas

#### Scenario: Rejeitar exercício sem nome
- **WHEN** um usuário autorizado cadastra um exercício sem nome
- **THEN** o sistema rejeita a solicitação sem criar um registro

#### Scenario: Editar exercício
- **WHEN** um usuário autorizado altera os dados de um exercício
- **THEN** o sistema persiste os dados atualizados sem alterar os valores já registrados em fichas existentes

### Requirement: Exercícios são desativados sem apagar o histórico

O sistema SHALL permitir a desativação de exercícios sem exclusão física e SHALL impedir a seleção de exercícios desativados em novas fichas.

#### Scenario: Desativar exercício utilizado
- **WHEN** um exercício referenciado por uma ficha é desativado
- **THEN** o exercício e a ficha permanecem consultáveis e a ficha preserva os dados registrados

#### Scenario: Selecionar exercício desativado
- **WHEN** um usuário tenta adicionar um exercício desativado a uma nova ficha
- **THEN** o sistema rejeita a referência e mantém a ficha sem alterações

### Requirement: O catálogo exige autorização de administrador ou instrutor

O sistema SHALL validar no backend a autenticação e o perfil `admin` ou `instrutor` em todas as operações do catálogo.

#### Scenario: Perfil sem autorização consulta ou altera exercícios
- **WHEN** uma pessoa sem sessão ou com perfil `recepcionista` ou `member` consulta ou altera o catálogo
- **THEN** o backend rejeita a solicitação sem revelar dados nem alterar registros
