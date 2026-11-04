# authentication Specification

## Purpose

Esta capability permite que usuários entrem e criem contas com feedback claro, controles acessíveis para senha e uma política de senha validada também pelo backend.

## Requirements

### Requirement: Usuários podem revelar ou ocultar a senha no login

O sistema SHALL oferecer um controle acessível para alternar entre exibir e ocultar o conteúdo da senha no login, sem modificar o valor digitado.

#### Scenario: Alternar visibilidade da senha no login
- **WHEN** a pessoa aciona o controle de visibilidade no campo de senha do login
- **THEN** o campo alterna entre texto visível e mascarado sem perder o conteúdo digitado

### Requirement: Senhas existentes continuam válidas para login

O sistema SHALL aplicar os novos requisitos à criação de contas, sem bloquear o login de contas existentes por não atenderem à nova política.

#### Scenario: Login com senha existente que não atende à nova política
- **WHEN** uma conta existente envia credenciais válidas cuja senha não atende à política de cadastro
- **THEN** o login continua dependendo apenas da validação das credenciais pelo backend e pode iniciar a sessão normalmente

### Requirement: A tela de login apresenta layout espaçado e responsivo

O sistema SHALL organizar os campos, mensagens e ações do login com espaçamento consistente, hierarquia visual clara e adaptação a telas menores, mantendo legibilidade e acesso às ações sem sobreposição ou rolagem horizontal.

#### Scenario: Acesso em tela estreita
- **WHEN** a pessoa abre o login em uma tela estreita
- **THEN** os campos e ações permanecem legíveis, utilizáveis e sem sobreposição ou rolagem horizontal

#### Scenario: Exibição de mensagens do formulário
- **WHEN** uma mensagem de validação ou de resultado é apresentada no login
- **THEN** ela permanece visualmente associada ao formulário e não sobrepõe campos nem ações

### Requirement: O sistema não oferece cadastro público de contas

O sistema SHALL remover a opção de auto cadastro da interface e SHALL rejeitar chamadas, autenticadas ou não, ao endpoint legado de cadastro sem criar usuário ou emitir token. Contas já existentes SHALL continuar podendo autenticar normalmente.

#### Scenario: Login não apresenta ação de cadastro
- **WHEN** uma pessoa acessa a tela de login
- **THEN** a interface não oferece link, modal ou formulário de auto cadastro

#### Scenario: Chamada anônima direta ao endpoint legado
- **WHEN** uma pessoa não autenticada envia dados válidos ao endpoint legado de cadastro
- **THEN** a API rejeita a solicitação, não persiste uma conta e não emite token de autenticação

#### Scenario: Chamada autenticada ao endpoint legado
- **WHEN** uma pessoa autenticada envia dados ao endpoint legado de cadastro
- **THEN** a API também rejeita a solicitação, sem criar uma conta nem emitir token por esse fluxo

#### Scenario: Conta existente continua autenticando
- **WHEN** um funcionário com conta existente informa credenciais válidas
- **THEN** o login inicia a sessão normalmente, sem depender do cadastro público
