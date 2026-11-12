# Spec Delta: Gestão de alunos

## Purpose

Permite que administradores gerenciem os cadastros de alunos da academia em uma interface centralizada, preservando os registros e protegendo os dados pessoais.

## ADDED Requirements

### Requirement: Administradores podem consultar e pesquisar alunos

O sistema SHALL permitir que usuários com perfil `admin` consultem os alunos cadastrados e filtrem a lista por nome ou contato.

#### Scenario: Administrador consulta alunos
- **WHEN** um usuário autenticado com perfil `admin` abre a área de alunos
- **THEN** o sistema apresenta os alunos cadastrados e seus estados de atividade

#### Scenario: Administrador pesquisa alunos
- **WHEN** um usuário `admin` informa um termo de pesquisa por nome ou contato
- **THEN** o sistema apresenta somente os alunos correspondentes ao termo

#### Scenario: Nenhum aluno corresponde à pesquisa
- **WHEN** a pesquisa não encontra correspondências
- **THEN** o sistema informa que nenhum aluno foi encontrado sem apresentar isso como falha da API

#### Scenario: Administrador consulta os detalhes para editar
- **WHEN** um usuário `admin` abre os detalhes de um aluno para edição
- **THEN** o sistema fornece os dados cadastrais necessários ao formulário, incluindo CPF, data de nascimento e endereço

### Requirement: Administradores podem cadastrar e editar alunos

O sistema SHALL permitir que usuários `admin` cadastrem e editem os dados de um aluno, incluindo nome, CPF, data de nascimento, contato e endereço conforme preenchidos.

#### Scenario: Cadastro válido
- **WHEN** um usuário `admin` envia um cadastro com nome preenchido e dados válidos
- **THEN** o sistema persiste o aluno com situação ativa e confirma o cadastro

#### Scenario: Cadastro sem nome
- **WHEN** um usuário `admin` tenta salvar um cadastro sem nome
- **THEN** o sistema rejeita a operação, informa que o nome é obrigatório e não cria o registro

#### Scenario: Edição válida
- **WHEN** um usuário `admin` salva alterações válidas em um aluno existente
- **THEN** o sistema persiste e apresenta os dados atualizados

### Requirement: A gestão de alunos exige autorização administrativa no backend

O sistema SHALL exigir autenticação e validar o perfil `admin` no backend para consultar, pesquisar, cadastrar, editar ou desativar alunos.

#### Scenario: Usuário não autenticado tenta acessar alunos
- **WHEN** uma requisição sem autenticação tenta executar uma operação de gestão de alunos
- **THEN** o backend rejeita a requisição sem revelar dados pessoais

#### Scenario: Usuário com perfil member tenta acessar alunos
- **WHEN** um usuário autenticado com perfil `member` tenta executar uma operação de gestão de alunos
- **THEN** o backend rejeita a requisição sem revelar dados pessoais

### Requirement: A lista de alunos minimiza a exposição de dados pessoais

O sistema SHALL exibir na lista somente os dados necessários à identificação operacional do aluno, mascarar o CPF e omitir o endereço.

#### Scenario: Administrador consulta a lista
- **WHEN** um usuário `admin` visualiza a lista de alunos
- **THEN** a interface mostra nome, contato e situação, apresenta CPF mascarado quando disponível e não mostra endereço

### Requirement: Alunos são desativados sem exclusão física

O sistema SHALL permitir que usuários `admin` desativem um aluno mantendo seu registro persistido e distinguindo-o de alunos ativos.

#### Scenario: Administrador desativa um aluno
- **WHEN** um usuário `admin` confirma a desativação de um aluno ativo
- **THEN** o sistema marca o aluno como inativo e mantém seu registro consultável

#### Scenario: Administrador cancela a desativação
- **WHEN** um usuário `admin` cancela a confirmação de desativação
- **THEN** o sistema mantém o aluno ativo sem alterar seus dados

### Requirement: A interface apresenta falhas da API sem mascará-las

O sistema SHALL diferenciar carregamento, lista vazia e falha de comunicação ou autorização ao consultar ou alterar alunos.

#### Scenario: Falha ao carregar alunos
- **WHEN** a API falha ao carregar a lista
- **THEN** a interface informa que não foi possível carregar os dados e oferece uma forma de tentar novamente

#### Scenario: Falha ao salvar aluno
- **WHEN** a API rejeita ou não conclui uma operação de cadastro, edição ou desativação
- **THEN** a interface informa que a operação falhou e não apresenta uma confirmação de sucesso

### Requirement: O painel oferece acesso à área de alunos

O sistema SHALL apresentar no painel uma navegação identificável para a área de gestão de alunos.

#### Scenario: Administrador navega até alunos
- **WHEN** um usuário `admin` seleciona a opção de alunos no painel
- **THEN** o sistema abre a área de gestão de alunos
