# Spec Delta

## ADDED Requirements

### Requirement: O formulário de sessão usa uma única data e identifica instrutores pelo nome

O sistema SHALL permitir que administradores agendem e editem sessões informando um único dia para a aula, horários de início e término separados e selecionando um instrutor ativo pelo nome, sem exigir que a pessoa informe ou consulte seu identificador.

#### Scenario: Agendar uma sessão em um dia
- **WHEN** um administrador informa o dia da aula, horários válidos, modalidade, instrutor ativo, capacidade e local opcional
- **THEN** a interface associa o início e o término ao dia informado e salva a sessão para o instrutor selecionado

#### Scenario: Selecionar instrutor pelo nome
- **WHEN** um administrador escolhe uma opção de instrutor no formulário
- **THEN** a opção é apresentada pelo nome e a sessão fica associada ao instrutor correspondente

#### Scenario: Editar uma sessão existente
- **WHEN** um administrador abre uma sessão para edição
- **THEN** a interface apresenta o dia da aula uma única vez, os horários atuais e o nome do instrutor selecionado
