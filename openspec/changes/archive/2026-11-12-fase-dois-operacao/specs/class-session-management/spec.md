# Spec Delta

## Purpose

Permite que administradores organizem sessões individuais de aula, associando modalidade e instrutor e controlando horário, capacidade e local.

## ADDED Requirements

### Requirement: Administradores podem manter sessões de aula

O sistema SHALL permitir que usuários `admin` criem, consultem, editem e cancelem sessões individuais com modalidade ativa, instrutor ativo, horário de início e término, capacidade positiva e local opcional.

#### Scenario: Criar sessão válida
- **WHEN** um usuário `admin` cria uma sessão futura com modalidade e instrutor ativos, término posterior ao início e capacidade positiva
- **THEN** o sistema persiste a sessão como agendada e a apresenta na agenda

#### Scenario: Rejeitar dados de sessão inválidos
- **WHEN** um usuário `admin` envia uma sessão com modalidade ou instrutor inativo, término anterior ou igual ao início, ou capacidade não positiva
- **THEN** o sistema rejeita a operação sem criar ou alterar uma sessão

#### Scenario: Evitar conflito de agenda do instrutor
- **WHEN** um usuário `admin` cria ou edita uma sessão em horário sobreposto a outra sessão agendada do mesmo instrutor
- **THEN** o sistema rejeita a operação sem alterar as sessões existentes

#### Scenario: Editar sessão sem reduzir capacidade abaixo das reservas
- **WHEN** um usuário `admin` edita uma sessão que possui reservas confirmadas
- **THEN** o sistema rejeita capacidade inferior ao número de reservas confirmadas e preserva os dados atuais

#### Scenario: Cancelar sessão com reservas
- **WHEN** um usuário `admin` cancela uma sessão com reservas
- **THEN** a sessão permanece no histórico como cancelada, deixa de aceitar reservas e suas reservas confirmadas são canceladas

#### Scenario: Usuário sem perfil administrativo mantém sessões
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta consultar ou alterar sessões
- **THEN** o backend rejeita a solicitação sem revelar dados nem alterar registros

### Requirement: A agenda distingue sessões disponíveis e estados vazios

O sistema SHALL apresentar sessões com modalidade, instrutor, início, término, local, capacidade ocupada e situação, distinguindo carregamento, lista vazia e falha da API.

#### Scenario: Consultar agenda
- **WHEN** um usuário `admin` consulta a agenda em um período
- **THEN** o sistema apresenta as sessões do período e a ocupação atual sem expor dados sensíveis desnecessários

#### Scenario: Agenda sem sessões
- **WHEN** não há sessões no período consultado
- **THEN** a interface informa que não existem sessões sem apresentar a ausência como falha
