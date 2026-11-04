# Spec Delta: Gestão de funcionários

## Purpose

Permite que administradores gerenciem contas de funcionários da academia, definindo perfil e situação de acesso sem manipular senhas ou excluir registros.

## ADDED Requirements

### Requirement: Administradores podem consultar e pesquisar funcionários

O sistema SHALL permitir que usuários com perfil `admin` consultem funcionários e filtrem a lista por nome, e-mail, perfil ou situação.

#### Scenario: Administrador consulta funcionários
- **WHEN** um administrador abre a área de funcionários
- **THEN** o sistema apresenta nome, e-mail, perfil e situação de cada conta retornada pela API

#### Scenario: Administrador pesquisa funcionários
- **WHEN** um administrador informa um termo de pesquisa
- **THEN** o sistema apresenta somente funcionários cujos dados operacionais correspondam ao termo

#### Scenario: Pesquisa sem correspondências
- **WHEN** nenhum funcionário corresponde ao termo de pesquisa
- **THEN** a interface informa que nenhum funcionário foi encontrado sem apresentar o resultado como falha da API

### Requirement: Administradores podem convidar funcionários por e-mail

O sistema SHALL permitir que administradores enviem convites de acesso com nome, e-mail e um dos perfis `admin`, `recepcionista` ou `instrutor`, sem solicitar ou apresentar a senha do funcionário.

#### Scenario: Convite enviado com sucesso
- **WHEN** um administrador envia um convite com nome, e-mail e perfil válidos
- **THEN** o sistema confirma que o convite foi solicitado e atualiza a lista de funcionários

#### Scenario: Convite com dados inválidos ou e-mail já utilizado
- **WHEN** a API rejeita um convite
- **THEN** a interface apresenta uma mensagem de erro e não confirma o envio

### Requirement: Administradores podem editar os dados operacionais de funcionários

O sistema SHALL permitir que administradores atualizem nome, e-mail e perfil de uma conta de funcionário existente.

#### Scenario: Edição válida
- **WHEN** um administrador salva alterações aceitas pela API
- **THEN** a interface apresenta os dados atualizados e confirma a operação

#### Scenario: Edição rejeitada pela API
- **WHEN** a API rejeita as alterações
- **THEN** a interface mantém o formulário disponível, informa a falha e não apresenta sucesso

### Requirement: Funcionários podem ser ativados e desativados sem exclusão física

O sistema SHALL permitir que administradores alterem a situação de uma conta entre ativa e inativa, preservando seu registro.

#### Scenario: Administrador desativa funcionário
- **WHEN** um administrador confirma a desativação de uma conta ativa
- **THEN** o sistema solicita a alteração à API, atualiza a situação exibida e mantém o registro consultável

#### Scenario: Administrador reativa funcionário
- **WHEN** um administrador confirma a reativação de uma conta inativa
- **THEN** o sistema solicita a alteração à API e apresenta a conta como ativa

#### Scenario: Administrador cancela a alteração de situação
- **WHEN** um administrador cancela a confirmação
- **THEN** o sistema não altera a conta nem sua situação

### Requirement: A gestão de funcionários exige autorização administrativa no backend

O sistema SHALL disponibilizar a gestão somente a usuários `admin` e depender da autorização correspondente aplicada pela API em todas as operações.

#### Scenario: Usuário sem perfil administrativo tenta acessar a gestão
- **WHEN** a API retorna HTTP 403 para um usuário autenticado
- **THEN** a interface informa que o acesso não é permitido e não apresenta dados de funcionários

#### Scenario: Sessão expirada durante uma operação
- **WHEN** a API retorna HTTP 401
- **THEN** o sistema limpa os dados de funcionários da sessão e redireciona o usuário para o login

### Requirement: A interface diferencia carregamento, vazio, sucesso e falha

O sistema SHALL apresentar estados distintos para carregamento, lista vazia, sucesso e falhas de comunicação ou resposta da API.

#### Scenario: Falha ao carregar a lista
- **WHEN** a API não conclui a consulta de funcionários
- **THEN** a interface informa a falha e permite tentar novamente sem substituir o erro por uma lista vazia

#### Scenario: Operação concluída
- **WHEN** a API confirma um convite, edição ou alteração de situação
- **THEN** a interface apresenta confirmação de sucesso e atualiza os dados exibidos

### Requirement: A interface protege credenciais de funcionários

O sistema SHALL exibir somente os dados operacionais necessários e nunca apresentar ou armazenar senhas de funcionários em campos, tabelas ou mensagens.

#### Scenario: Convite e consulta de funcionário
- **WHEN** um administrador convida ou consulta uma conta
- **THEN** a interface utiliza nome, e-mail, perfil, situação e estado do convite quando disponível, sem exibir senha ou token de autenticação
