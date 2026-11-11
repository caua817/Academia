# Spec Delta

## ADDED Requirements

### Requirement: Contas inativas não iniciam nem usam sessões autenticadas

O sistema SHALL rejeitar a autenticação de contas inativas e SHALL impedir que sessões existentes dessas contas acessem identidade ou operações protegidas.

#### Scenario: Conta inativa tenta entrar com senha
- **WHEN** uma conta inativa envia credenciais válidas ao endpoint de login
- **THEN** a API rejeita a autenticação sem emitir token

#### Scenario: Conta inativa tenta entrar por link individual
- **WHEN** uma conta inativa utiliza um link individual de autenticação ou definição de senha
- **THEN** a API rejeita a troca do link por sessão autenticada

#### Scenario: Sessão existente pertence a conta desativada
- **WHEN** uma sessão previamente emitida para uma conta desativada consulta sua identidade ou uma operação protegida
- **THEN** a API rejeita a solicitação sem retornar dados protegidos nem efetuar alterações
