# Spec Delta

## ADDED Requirements

### Requirement: Senha temporária exige troca antes da sessão normal

O sistema SHALL exigir que funcionários autenticados com uma senha temporária válida definam uma senha pessoal antes de receber uma sessão normal. A senha temporária SHALL expirar após 24 horas, e a operação de troca SHALL validar a senha temporária atual e não SHALL criar sessão autenticada.

#### Scenario: Login com senha temporária válida
- **WHEN** o funcionário informa uma senha temporária válida e ainda dentro do prazo
- **THEN** a API solicita a troca obrigatória da senha e não retorna token de sessão normal

#### Scenario: Troca obrigatória concluída
- **WHEN** o funcionário informa sua senha temporária válida e uma nova senha que atende à política vigente
- **THEN** a API grava a nova senha, invalida a credencial temporária e sua validade, e solicita um novo login sem emitir sessão na troca

#### Scenario: Senha temporária expirada
- **WHEN** o funcionário tenta fazer login ou trocar a senha após o prazo de 24 horas
- **THEN** a API rejeita a operação sem emitir sessão e orienta a solicitar uma nova credencial ao administrador

#### Scenario: Senha atual ou nova senha inválida
- **WHEN** a senha temporária atual não corresponde ou a nova senha não atende à política vigente
- **THEN** a API não altera a conta, não emite sessão e informa uma falha sem revelar credenciais

#### Scenario: Login de funcionário com senha permanente
- **WHEN** um funcionário que já definiu sua senha pessoal informa credenciais válidas
- **THEN** a autenticação normal existente emite a sessão e encaminha o funcionário conforme seu perfil

#### Scenario: Limite de tentativas com senha temporária
- **WHEN** são feitas cinco solicitações de login e/ou troca para a mesma conta com senha temporária em 15 minutos
- **THEN** novas solicitações são rejeitadas até a janela expirar, sem alterar a conta ou emitir sessão
