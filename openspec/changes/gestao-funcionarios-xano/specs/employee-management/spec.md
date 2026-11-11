# Spec Delta

## ADDED Requirements

### Requirement: A API Xano oferece operações administrativas de funcionários

O sistema SHALL disponibilizar operações autenticadas para listar e consultar funcionários, convidar por e-mail, editar dados operacionais, ativar e desativar contas, permitindo essas operações somente a usuários `admin`.

#### Scenario: Administrador consulta funcionários
- **WHEN** um usuário `admin` lista ou consulta um funcionário
- **THEN** a API retorna somente identificador, nome, e-mail, perfil, situação e estado do convite quando disponível, sem senha, hash de senha ou token

#### Scenario: Administrador convida funcionário
- **WHEN** um usuário `admin` envia nome, e-mail e perfil válido (`admin`, `recepcionista` ou `instrutor`)
- **THEN** a API cria a conta sem senha definida pelo administrador e envia um link individual para definição de senha

#### Scenario: Rejeitar convite inválido ou duplicado
- **WHEN** um usuário `admin` envia campos inválidos ou um e-mail já associado a uma conta
- **THEN** a API rejeita a solicitação, não cria outra conta e não confirma o envio do convite

#### Scenario: Administrador edita dados operacionais
- **WHEN** um usuário `admin` altera nome, e-mail ou perfil de um funcionário existente
- **THEN** a API persiste os campos aceitos sem alterar a situação da conta nem expor credenciais

#### Scenario: Administrador altera situação da conta
- **WHEN** um usuário `admin` ativa ou desativa uma conta
- **THEN** a API atualiza sua situação sem apagar a conta e retorna os dados operacionais atualizados

#### Scenario: Impedir remoção do último administrador ativo
- **WHEN** uma operação desativa ou altera o perfil do último usuário `admin` ativo
- **THEN** a API rejeita a operação e mantém ao menos um administrador ativo

#### Scenario: Usuário sem autorização administra funcionários
- **WHEN** uma pessoa sem sessão ou sem perfil `admin` consulta ou altera funcionários
- **THEN** a API rejeita a solicitação sem revelar dados nem alterar registros
