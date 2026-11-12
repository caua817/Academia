# Spec Delta

## Purpose

Esta capability permite que usuários entrem e criem contas com feedback claro, controles acessíveis para senha e uma política de senha validada também pelo backend.

## ADDED Requirements

### Requirement: Usuários podem revelar ou ocultar a senha nos formulários de autenticação

O sistema SHALL oferecer um controle acessível para alternar entre exibir e ocultar o conteúdo da senha, sem modificar o valor digitado.

#### Scenario: Alternar visibilidade da senha no login
- **WHEN** a pessoa aciona o controle de visibilidade no campo de senha do login
- **THEN** o campo alterna entre texto visível e mascarado sem perder o conteúdo digitado

#### Scenario: Alternar visibilidade da senha no cadastro
- **WHEN** a pessoa aciona o controle de visibilidade no campo de senha do cadastro
- **THEN** o campo alterna entre texto visível e mascarado sem perder o conteúdo digitado

### Requirement: O cadastro informa e valida os requisitos de senha

O sistema SHALL informar que a senha precisa conter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula e um número, e SHALL indicar quais critérios foram atendidos durante o preenchimento.

#### Scenario: Senha atende à política
- **WHEN** a senha possui pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula e um número
- **THEN** a interface indica que todos os critérios foram atendidos e permite enviar o cadastro

#### Scenario: Senha não atende à política
- **WHEN** a pessoa tenta cadastrar uma senha que não atende a um ou mais critérios
- **THEN** a interface indica os critérios pendentes e não envia a solicitação de cadastro

#### Scenario: API recebe senha fora da política
- **WHEN** uma solicitação de cadastro chega ao endpoint com uma senha que não atende à política
- **THEN** o backend rejeita a solicitação com erro de validação e não cria uma conta

### Requirement: Senhas existentes continuam válidas para login

O sistema SHALL aplicar os novos requisitos à criação de contas, sem bloquear o login de contas existentes por não atenderem à nova política.

#### Scenario: Login com senha existente que não atende à nova política
- **WHEN** uma conta existente envia credenciais válidas cuja senha não atende à política de cadastro
- **THEN** o login continua dependendo apenas da validação das credenciais pelo backend e pode iniciar a sessão normalmente

### Requirement: A tela de autenticação apresenta layout espaçado e responsivo

O sistema SHALL organizar os campos, mensagens, ações e conteúdos do login e do cadastro com espaçamento consistente, hierarquia visual clara e adaptação a telas menores, mantendo legibilidade e acesso às ações sem sobreposição ou rolagem horizontal.

#### Scenario: Acesso em tela estreita
- **WHEN** a pessoa abre o login ou o cadastro em uma tela estreita
- **THEN** os campos e ações permanecem legíveis, utilizáveis e sem sobreposição ou rolagem horizontal

#### Scenario: Exibição de mensagens do formulário
- **WHEN** uma mensagem de validação ou de resultado é apresentada no formulário
- **THEN** ela permanece visualmente associada ao formulário e não sobrepõe campos nem ações
