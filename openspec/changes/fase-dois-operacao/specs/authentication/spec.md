# Spec Delta

## ADDED Requirements

### Requirement: Páginas de gestão são restritas a administradores

O sistema SHALL exibir e permitir a navegação nas páginas de gestão somente para usuários autenticados com perfil `admin`, mantendo a autorização do backend como controle efetivo de acesso aos dados e operações.

#### Scenario: Administrador acessa páginas de gestão
- **WHEN** um usuário autenticado com perfil `admin` navega para uma página de gestão
- **THEN** o sistema apresenta a página e permite que ela consulte a API sob autorização do backend

#### Scenario: Usuário sem sessão tenta abrir página de gestão
- **WHEN** uma pessoa sem sessão tenta abrir diretamente uma página de gestão
- **THEN** a interface redireciona para o login e não apresenta dados da página

#### Scenario: Usuário autenticado sem perfil de administrador tenta abrir página de gestão
- **WHEN** uma pessoa autenticada com perfil diferente de `admin` abre ou navega para uma página de gestão
- **THEN** a interface nega o acesso à página e não apresenta seus dados

#### Scenario: Falha ao verificar perfil
- **WHEN** a aplicação não consegue verificar a sessão ou o perfil do usuário
- **THEN** o sistema não concede acesso por padrão e apresenta o fluxo apropriado de erro ou autenticação
