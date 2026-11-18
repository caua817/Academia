# Spec Delta

## ADDED Requirements

### Requirement: A verificação de perfil resiste a falhas transitórias sem bloquear a interface

Ao verificar o perfil de uma sessão, o sistema SHALL manter a interface responsiva e SHALL conceder acesso somente após receber e validar um perfil autorizado. O sistema SHALL fazer no máximo uma nova tentativa automática para falhas transitórias de transporte ou respostas HTTP 5xx na consulta idempotente de perfil. SHALL NOT repetir automaticamente respostas HTTP 401, 403 ou 429. Se a verificação continuar indisponível, o sistema SHALL informar que a verificação falhou e permitir uma nova tentativa explícita, sem descartar uma sessão já autenticada nem armazenar uma nova sessão cujo perfil não foi verificado.

#### Scenario: Consulta de perfil se recupera após falha transitória
- **WHEN** a primeira consulta de perfil falha por transporte ou erro HTTP 5xx e a tentativa seguinte retorna um perfil válido e autorizado
- **THEN** a interface permanece responsiva durante as consultas e permite o acesso correspondente ao perfil

#### Scenario: Verificação continua indisponível
- **WHEN** a consulta de perfil continua falhando após a tentativa automática limitada
- **THEN** o sistema não autoriza a rota, mantém uma sessão existente para nova tentativa explícita e informa que não foi possível verificar o perfil

#### Scenario: Perfil não é verificado durante novo login
- **WHEN** as credenciais iniciam uma sessão mas a verificação de perfil falha
- **THEN** o sistema não armazena o novo token, não redireciona para uma área protegida e permite que a pessoa tente novamente

#### Scenario: Sessão expirada
- **WHEN** a consulta de perfil responde HTTP 401
- **THEN** o sistema não repete a consulta, limpa a sessão e encaminha a pessoa para o login

#### Scenario: Acesso negado pelo perfil
- **WHEN** a consulta de perfil responde HTTP 403 ou retorna um perfil sem permissão para a rota
- **THEN** o sistema não repete a consulta nem apresenta os dados protegidos

#### Scenario: Limite temporário da API
- **WHEN** a consulta de perfil responde HTTP 429
- **THEN** o sistema não repete automaticamente a consulta, não concede acesso e orienta a aguardar antes de tentar novamente

#### Scenario: Resposta de perfil inválida
- **WHEN** a API retorna uma resposta de perfil ausente, malformada ou não autorizada
- **THEN** o sistema não concede acesso e apresenta o fluxo apropriado de erro ou autenticação
