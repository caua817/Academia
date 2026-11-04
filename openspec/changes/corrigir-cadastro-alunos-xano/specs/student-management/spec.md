# Spec Delta

## MODIFIED Requirements

### Requirement: Administradores podem cadastrar e editar alunos

O sistema SHALL permitir que usuários `admin` cadastrem e editem os dados de um aluno, incluindo nome, CPF, data de nascimento, contato e endereço conforme preenchidos. Campos opcionais não preenchidos, enviados como nulos ou omitidos SHALL ser tratados como ausentes, sem impedir um cadastro válido com nome preenchido.

#### Scenario: Cadastro válido
- **WHEN** um usuário `admin` envia um cadastro com nome preenchido e dados válidos
- **THEN** o sistema persiste o aluno com situação ativa e confirma o cadastro

#### Scenario: Cadastro sem nome
- **WHEN** um usuário `admin` tenta salvar um cadastro sem nome
- **THEN** o sistema rejeita a operação, informa que o nome é obrigatório e não cria o registro

#### Scenario: Cadastro com campos opcionais vazios
- **WHEN** um usuário `admin` cadastra um aluno com nome preenchido e os campos opcionais vazios enviados como nulos ou omitidos
- **THEN** o sistema persiste o aluno com situação ativa e confirma o cadastro

#### Scenario: Edição válida
- **WHEN** um usuário `admin` salva alterações válidas em um aluno existente
- **THEN** o sistema persiste e apresenta os dados atualizados
