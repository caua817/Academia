# Spec Delta

## MODIFIED Requirements

### Requirement: Páginas de gestão são restritas a administradores

O sistema SHALL permitir que usuários autenticados acessem somente as páginas e operações autorizadas ao seu perfil, conforme a matriz: `admin` acessa todas as áreas; `recepcionista` opera alunos, matrículas, consulta de planos ativos necessária à matrícula, mensalidades, registro de pagamentos e check-ins; `instrutor` consulta os dados mínimos de alunos e frequência e acessa exercícios, fichas e avaliações. A gestão de funcionários, configurações, relatórios, sessões de aula, reservas e correções financeiras SHALL permanecer restrita a `admin`. A interface SHALL refletir estas permissões, e o backend SHALL autorizar cada operação sem confiar na navegação ou no estado do frontend.

#### Scenario: Administrador acessa todas as áreas
- **WHEN** um usuário autenticado com perfil `admin` navega para qualquer área do aplicativo
- **THEN** o sistema apresenta a área e permite operações autorizadas pelo backend

#### Scenario: Administrador acessa páginas de gestão
- **WHEN** um usuário autenticado com perfil `admin` navega para uma página de gestão
- **THEN** o sistema apresenta a página e permite que ela consulte a API sob autorização do backend

#### Scenario: Recepcionista acessa operações de recepção
- **WHEN** um usuário autenticado com perfil `recepcionista` abre alunos, matrículas, financeiro ou check-ins
- **THEN** o sistema apresenta apenas as operações permitidas ao perfil e o backend valida a autorização correspondente

#### Scenario: Instrutor acessa acompanhamento e consultas permitidas
- **WHEN** um usuário autenticado com perfil `instrutor` abre alunos, check-ins ou acompanhamento
- **THEN** o sistema apresenta apenas dados e operações permitidos ao instrutor, sem dados financeiros ou administrativos

#### Scenario: Perfil tenta acessar área não autorizada
- **WHEN** um usuário autenticado tenta abrir uma página ou invocar diretamente uma operação fora da matriz do seu perfil
- **THEN** a interface nega a navegação e o backend rejeita a chamada sem revelar dados nem alterar registros

#### Scenario: Usuário sem sessão tenta abrir uma página protegida
- **WHEN** uma pessoa sem sessão tenta abrir diretamente qualquer página protegida
- **THEN** o sistema redireciona para o login e não apresenta dados da página

#### Scenario: Usuário sem sessão tenta abrir página de gestão
- **WHEN** uma pessoa sem sessão tenta abrir diretamente uma página de gestão
- **THEN** a interface redireciona para o login e não apresenta dados da página

#### Scenario: Usuário autenticado sem perfil de administrador tenta abrir página de gestão
- **WHEN** uma pessoa autenticada com perfil diferente de `admin` abre ou navega para uma página de gestão
- **THEN** a interface nega o acesso à página e não apresenta seus dados

#### Scenario: Falha ao verificar perfil
- **WHEN** a aplicação não consegue verificar a sessão ou o perfil do usuário
- **THEN** o sistema não concede acesso por padrão e apresenta o fluxo apropriado de erro ou autenticação
