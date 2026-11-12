query "alunos/desativar/{aluno_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"
  description = "Desativa um aluno sem excluir seu registro."

  input {
    int aluno_id {
      table = "aluno"
    }
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    db.get "aluno" {
      field_name = "id"
      field_value = $input.aluno_id
    } as $aluno_existente

    precondition ($aluno_existente != null) {
      error_type = "notfound"
      error = "Aluno não encontrado."
    }

    db.edit "aluno" {
      field_name = "id"
      field_value = $input.aluno_id
      data = {
        situacao: "Inativo"
      }
    } as $aluno
  }

  response = {
    id: $aluno.id
    nome: $aluno.nome
    situacao: $aluno.situacao
  }
  guid = "4EOGJrMvPsdLWSE03OMvBcoqytg"
}
