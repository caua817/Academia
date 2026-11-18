# Spec Delta: Autenticação

## Purpose

Permite que pessoas validem suas credenciais e criem uma conta pública pela interface, com feedback claro e uma sessão autenticada somente após resposta válida da API.

## ADDED Requirements

### Requirement: Usuários podem entrar com credenciais válidas

O sistema SHALL enviar e-mail e senha ao endpoint público de login sem token de autorização e iniciar uma sessão somente quando a API retornar um token válido.

#### Scenario: Login com credenciais válidas
- **WHEN** o usuário envia e-mail e senha válidos e a API retorna um token
- **THEN** o sistema guarda o token no estado servidor da sessão e redireciona para a aplicação

#### Scenario: Login com credenciais inválidas
- **WHEN** a API rejeita as credenciais
- **THEN** o sistema informa que o e-mail ou a senha estão incorretos e não inicia uma sessão

#### Scenario: Login sem campos obrigatórios
- **WHEN** o usuário tenta entrar sem e-mail ou sem senha
- **THEN** o sistema mostra uma mensagem de validação e não envia a requisição

#### Scenario: API retorna sucesso sem token
- **WHEN** o endpoint de login retorna sucesso sem token de sessão
- **THEN** o sistema informa que não foi possível iniciar a sessão e permanece na tela de login

### Requirement: Usuários podem solicitar cadastro com dados obrigatórios

O sistema SHALL permitir o cadastro público de uma conta com nome, e-mail e senha, sem exigir token na requisição; a conta recém-criada mantém o perfil padrão `member`.

#### Scenario: Cadastro com dados preenchidos
- **WHEN** o usuário envia nome, e-mail e senha válidos
- **THEN** o sistema envia os dados ao endpoint de cadastro e confirma sucesso somente após resposta HTTP bem-sucedida

#### Scenario: Cadastro acionado sem dados
- **WHEN** o usuário clica em “Cadastrar” com nome, e-mail ou senha vazio
- **THEN** a interface mostra uma mensagem de erro junto ao formulário e não envia requisição

#### Scenario: Cadastro rejeitado
- **WHEN** a API rejeita o cadastro, inclusive por e-mail já utilizado
- **THEN** a interface informa a falha e não apresenta sucesso

### Requirement: A interface de autenticação apresenta falhas de rede explicitamente

O sistema SHALL diferenciar erros de credenciais, validação e indisponibilidade da API sem revelar detalhes internos ou dados sensíveis da resposta.

#### Scenario: API indisponível durante login ou cadastro
- **WHEN** a chamada HTTP falha por conexão ou tempo limite
- **THEN** a interface apresenta uma mensagem de conexão e permite nova tentativa

### Requirement: Modal de cadastro abre e fecha de forma consistente

O sistema SHALL abrir o formulário de cadastro quando o usuário seleciona “Cadastre-se” e fechá-lo quando o usuário cancela ou solicita o fechamento.

#### Scenario: Usuário abre ou fecha cadastro
- **WHEN** o usuário aciona abrir ou fechar o modal
- **THEN** o estado visual do modal corresponde à ação solicitada e as mensagens antigas são limpas ao iniciar um novo cadastro
