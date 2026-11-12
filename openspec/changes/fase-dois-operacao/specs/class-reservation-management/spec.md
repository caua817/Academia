# Spec Delta

## Purpose

Permite que administradores reservem vagas em sessões para alunos elegíveis e acompanhem cancelamentos e comparecimento sem exceder a capacidade.

## ADDED Requirements

### Requirement: Administradores podem reservar vagas para alunos elegíveis

O sistema SHALL permitir que usuários `admin` reservem um aluno ativo com matrícula vigente em uma sessão futura agendada que tenha capacidade disponível.

#### Scenario: Criar reserva elegível
- **WHEN** um usuário `admin` reserva um aluno ativo com matrícula vigente em uma sessão futura com vaga
- **THEN** o sistema persiste a reserva como confirmada e incrementa a ocupação da sessão

#### Scenario: Rejeitar reserva sem elegibilidade ou vaga
- **WHEN** um usuário `admin` tenta reservar aluno inativo, aluno sem matrícula vigente, sessão não agendada, sessão iniciada ou sessão lotada
- **THEN** o sistema rejeita a solicitação sem criar uma reserva

#### Scenario: Impedir reserva ativa duplicada
- **WHEN** um usuário `admin` tenta criar outra reserva confirmada para o mesmo aluno na mesma sessão
- **THEN** o sistema rejeita a operação e mantém apenas a reserva existente

#### Scenario: Reservas simultâneas na última vaga
- **WHEN** duas solicitações simultâneas tentam reservar a última vaga de uma sessão
- **THEN** no máximo uma reserva é confirmada e a capacidade não é excedida

#### Scenario: Usuário sem perfil administrativo cria ou consulta reservas
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta criar ou consultar reservas
- **THEN** o backend rejeita a solicitação sem revelar dados nem alterar registros

### Requirement: Administradores podem cancelar reservas e registrar comparecimento

O sistema SHALL permitir que administradores cancelem reservas confirmadas antes do início da sessão e registrem comparecimento ou falta após o término, preservando o histórico.

#### Scenario: Cancelar reserva antes da sessão
- **WHEN** um usuário `admin` cancela uma reserva confirmada antes do início da sessão
- **THEN** o sistema mantém a reserva no histórico como cancelada e libera a vaga

#### Scenario: Registrar comparecimento ou falta após a sessão
- **WHEN** um usuário `admin` registra o resultado após o término de uma sessão com reserva confirmada
- **THEN** o sistema atualiza a situação da reserva para presente ou falta sem alterar o registro de check-in da academia

#### Scenario: Impedir alteração de reserva após situação final
- **WHEN** um usuário `admin` tenta cancelar uma reserva após o início da sessão ou alterar uma reserva já cancelada, presente ou falta
- **THEN** o sistema rejeita a operação e preserva o histórico

### Requirement: A consulta de reservas apresenta estado e ocupação corretos

O sistema SHALL permitir que administradores consultem reservas por sessão e apresentar o aluno, situação e ocupação atual, sem expor dados pessoais desnecessários.

#### Scenario: Consultar reservas da sessão
- **WHEN** um usuário `admin` consulta as reservas de uma sessão
- **THEN** o sistema apresenta as reservas e a quantidade de vagas confirmadas

#### Scenario: Falha ao consultar reservas
- **WHEN** a API rejeita ou não conclui a consulta de reservas
- **THEN** a interface informa a falha sem substituir os dados por uma lista vazia apresentada como sucesso
