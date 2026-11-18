# Spec Delta

## MODIFIED Requirements

### Requirement: Administradores podem consultar e pesquisar alunos

O sistema SHALL permitir que usuários com perfil `admin` ou `recepcionista` consultem os alunos cadastrados e filtrem a lista por nome ou contato. Usuários `instrutor` SHALL poder consultar somente os dados mínimos de identificação operacional necessários ao acompanhamento, sem CPF, endereço ou contato.

#### Scenario: Administrador ou recepcionista consulta alunos
- **WHEN** um usuário autenticado com perfil `admin` ou `recepcionista` abre a área de alunos
- **THEN** o sistema apresenta os alunos cadastrados e seus estados de atividade

#### Scenario: Administrador consulta alunos
- **WHEN** um usuário autenticado com perfil `admin` abre a área de alunos
- **THEN** o sistema apresenta os alunos cadastrados e seus estados de atividade

#### Scenario: Administrador ou recepcionista pesquisa alunos
- **WHEN** um usuário `admin` ou `recepcionista` informa um termo de pesquisa por nome ou contato
- **THEN** o sistema apresenta somente os alunos correspondentes ao termo

#### Scenario: Administrador pesquisa alunos
- **WHEN** um usuário `admin` informa um termo de pesquisa por nome ou contato
- **THEN** o sistema apresenta somente os alunos correspondentes ao termo

#### Scenario: Instrutor consulta alunos
- **WHEN** um usuário `instrutor` consulta alunos para prestar acompanhamento
- **THEN** o sistema apresenta somente dados mínimos de identificação e situação, sem CPF, endereço ou contato

#### Scenario: Nenhum aluno corresponde à pesquisa
- **WHEN** nenhum aluno corresponde ao termo de pesquisa
- **THEN** a interface informa que nenhum aluno foi encontrado sem apresentar isso como falha da API

#### Scenario: Usuário autorizado consulta detalhes para editar
- **WHEN** um usuário `admin` ou `recepcionista` abre os detalhes de um aluno para edição
- **THEN** o sistema fornece os dados cadastrais necessários ao formulário

#### Scenario: Administrador consulta os detalhes para editar
- **WHEN** um usuário `admin` abre os detalhes de um aluno para edição
- **THEN** o sistema fornece os dados cadastrais necessários ao formulário, incluindo CPF, data de nascimento e endereço

### Requirement: Administradores podem cadastrar e editar alunos

O sistema SHALL permitir que usuários `admin` e `recepcionista` cadastrem e editem os dados de um aluno, incluindo nome, CPF, data de nascimento, contato e endereço conforme preenchidos. Campos opcionais não preenchidos, enviados como nulos ou omitidos SHALL ser tratados como ausentes, sem impedir um cadastro válido com nome preenchido. Instrutores SHALL ter acesso somente de consulta.

#### Scenario: Recepcionista cadastra aluno válido
- **WHEN** um usuário `admin` ou `recepcionista` envia um cadastro com nome preenchido e dados válidos
- **THEN** o sistema persiste o aluno com situação ativa e confirma o cadastro

#### Scenario: Cadastro válido
- **WHEN** um usuário `admin` envia um cadastro com nome preenchido e dados válidos
- **THEN** o sistema persiste o aluno com situação ativa e confirma o cadastro

#### Scenario: Recepcionista cadastra campos opcionais vazios
- **WHEN** um usuário autorizado cadastra um aluno com nome preenchido e campos opcionais vazios, nulos ou omitidos
- **THEN** o sistema persiste o aluno com situação ativa e confirma o cadastro

#### Scenario: Cadastro com campos opcionais vazios
- **WHEN** um usuário `admin` cadastra um aluno com nome preenchido e os campos opcionais vazios enviados como nulos ou omitidos
- **THEN** o sistema persiste o aluno com situação ativa e confirma o cadastro

#### Scenario: Cadastro sem nome
- **WHEN** um usuário autorizado tenta salvar um cadastro sem nome
- **THEN** o sistema rejeita a operação, informa que o nome é obrigatório e não cria o registro

#### Scenario: Recepcionista edita aluno
- **WHEN** um usuário `admin` ou `recepcionista` salva alterações válidas em um aluno existente
- **THEN** o sistema persiste e apresenta os dados atualizados

#### Scenario: Edição válida
- **WHEN** um usuário `admin` salva alterações válidas em um aluno existente
- **THEN** o sistema persiste e apresenta os dados atualizados

#### Scenario: Instrutor tenta alterar aluno
- **WHEN** um usuário `instrutor` tenta cadastrar, editar ou desativar um aluno
- **THEN** o backend rejeita a operação sem alterar dados

### Requirement: A gestão de alunos exige autorização administrativa no backend

O sistema SHALL exigir autenticação e validar o perfil no backend: `admin` e `recepcionista` podem consultar, pesquisar, cadastrar, editar ou desativar alunos; `instrutor` pode somente consultar os dados mínimos de identificação operacional.

#### Scenario: Usuário não autenticado tenta acessar alunos
- **WHEN** uma requisição sem autenticação tenta executar uma operação de gestão de alunos
- **THEN** o backend rejeita a requisição sem revelar dados pessoais

#### Scenario: Instrutor consulta dados mínimos
- **WHEN** um usuário `instrutor` consulta a lista de alunos
- **THEN** o backend retorna apenas os campos mínimos permitidos e rejeita operações de escrita

#### Scenario: Perfil sem autorização tenta acessar alunos
- **WHEN** uma pessoa com perfil diferente de `admin`, `recepcionista` ou `instrutor` tenta acessar dados ou operações de alunos
- **THEN** o backend rejeita a requisição sem revelar dados pessoais nem alterar registros

#### Scenario: Usuário com perfil member tenta acessar alunos
- **WHEN** um usuário autenticado com perfil `member` tenta executar uma operação de gestão de alunos
- **THEN** o backend rejeita a requisição sem revelar dados pessoais

### Requirement: A lista de alunos minimiza a exposição de dados pessoais

O sistema SHALL exibir para `admin` e `recepcionista` somente os dados necessários à identificação operacional, mascarar o CPF e omitir o endereço. Para `instrutor`, o sistema SHALL limitar a resposta ao nome e situação do aluno, sem CPF, endereço, contato ou e-mail.

#### Scenario: Administrador ou recepcionista consulta a lista
- **WHEN** um usuário autorizado da recepção visualiza a lista de alunos
- **THEN** a interface mostra nome, contato e situação, apresenta CPF mascarado quando disponível e não mostra endereço

#### Scenario: Administrador consulta a lista
- **WHEN** um usuário `admin` visualiza a lista de alunos
- **THEN** a interface mostra nome, contato e situação, apresenta CPF mascarado quando disponível e não mostra endereço

#### Scenario: Instrutor consulta a lista
- **WHEN** um instrutor visualiza a lista para acompanhamento
- **THEN** a interface mostra somente nome e situação do aluno

### Requirement: Alunos são desativados sem exclusão física

O sistema SHALL permitir que usuários `admin` e `recepcionista` desativem um aluno mantendo seu registro persistido e distinguindo-o de alunos ativos.

#### Scenario: Usuário autorizado desativa um aluno
- **WHEN** um usuário `admin` ou `recepcionista` confirma a desativação de um aluno ativo
- **THEN** o sistema marca o aluno como inativo e mantém seu registro consultável

#### Scenario: Administrador desativa um aluno
- **WHEN** um usuário `admin` confirma a desativação de um aluno ativo
- **THEN** o sistema marca o aluno como inativo e mantém seu registro consultável

#### Scenario: Usuário cancela a desativação
- **WHEN** um usuário autorizado cancela a confirmação de desativação
- **THEN** o sistema mantém o aluno ativo sem alterar seus dados

#### Scenario: Administrador cancela a desativação
- **WHEN** um usuário `admin` cancela a confirmação de desativação
- **THEN** o sistema mantém o aluno ativo sem alterar seus dados

#### Scenario: Instrutor tenta desativar aluno
- **WHEN** um usuário `instrutor` tenta desativar um aluno
- **THEN** o backend rejeita a solicitação e mantém o aluno sem alterações
