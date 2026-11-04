# Spec Delta

## ADDED Requirements

### Requirement: Usuários podem revelar ou ocultar a senha no login
O sistema SHALL oferecer um controle acessível para alternar entre exibir e ocultar o conteúdo da senha no login, sem modificar o valor digitado.

#### Scenario: Alternar visibilidade da senha no login
- **WHEN** a pessoa aciona o controle de visibilidade no campo de senha do login
- **THEN** o campo alterna entre texto visível e mascarado sem perder o conteúdo digitado

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

## REMOVED Requirements

### Requirement: Usuários podem revelar ou ocultar a senha nos formulários de autenticação
**Reason**: O requisito incluía um cenário de visibilidade no formulário de auto cadastro, que deixa de existir.
**Migration**: A visibilidade da senha no login continua coberta pelo requisito "Usuários podem revelar ou ocultar a senha no login".

### Requirement: O cadastro informa e valida os requisitos de senha
**Reason**: O cadastro público e seu formulário foram removidos; não há fluxo de criação de conta na interface nesta change.
**Migration**: Os critérios de senha aplicáveis ao futuro fluxo de convite e ativação de funcionários deverão ser especificados nesse fluxo. A API legado de cadastro não poderá criar contas, mesmo quando os dados atendam aos critérios.

### Requirement: A tela de autenticação apresenta layout espaçado e responsivo
**Reason**: O requisito abrangia as telas de login e cadastro, e a tela pública de cadastro deixa de existir.
**Migration**: O layout responsivo do login continua coberto pelo requisito "A tela de login apresenta layout espaçado e responsivo".
