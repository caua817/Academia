# Spec Delta

## ADDED Requirements

### Requirement: A verificação de perfil resiste a falhas transitórias sem bloquear a interface

Ao verificar o perfil de uma sessão, o sistema SHALL manter a interface responsiva e SHALL conceder acesso somente após receber e validar um perfil autorizado. O sistema SHALL fazer no máximo uma nova tentativa automática para falhas transitórias de transporte ou respostas HTTP 5xx na consulta idempotente de perfil. SHALL NOT repetir automaticamente respostas HTTP 401, 403 ou 429. Se a verificação continuar indisponível, o sistema SHALL informar que a verificação falhou e permitir uma nova tentativa explícita, sem descartar uma sessão já autenticada nem armazenar uma nova sessão cujo perfil não foi verificado.

Após validar o perfil para o token atual, o sistema SHALL reutilizar esse perfil nas navegações protegidas subsequentes da mesma sessão, sem chamar `/auth/me` novamente a cada navegação. O cache SHALL permanecer somente no estado privado do servidor e SHALL ser invalidado ao iniciar outro login, encerrar ou limpar a sessão, ou trocar o token. Sem um perfil verificado para o token atual, o sistema SHALL consultar a API e SHALL manter o acesso fechado se essa verificação falhar. O cache SHALL servir somente à navegação da interface; o backend SHALL continuar validando autenticação, situação e perfil em cada operação protegida.

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

#### Scenario: Navegação protegida com perfil já verificado
- **WHEN** a pessoa navega para outra rota protegida com o mesmo token cuja verificação já foi concluída
- **THEN** a interface reutiliza o perfil privado da sessão sem nova chamada a `/auth/me`, e as operações da página continuam sujeitas à autorização do backend

#### Scenario: Token alterado ou sessão encerrada
- **WHEN** um novo login começa, o token muda ou a sessão é encerrada ou limpa
- **THEN** o perfil armazenado para a sessão anterior é descartado e nenhuma rota é liberada até que o perfil do token atual seja verificado

#### Scenario: Perfil ou situação alterados no backend durante a sessão
- **WHEN** o perfil ou a situação da conta muda após o cache de navegação ser criado e a pessoa solicita uma operação protegida
- **THEN** o backend revalida o perfil e a situação atuais e rejeita a operação sem retornar dados ou persistir alterações não autorizadas
