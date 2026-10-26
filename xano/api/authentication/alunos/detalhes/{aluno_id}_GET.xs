query "alunos/detalhes/{aluno_id}" verb=GET {
  api_group = "Authentication"
  auth = "user"
  description = "Consulta dados de um aluno para usuários administradores."

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
    } as $aluno

    precondition ($aluno != null) {
      error_type = "notfound"
      error = "Aluno não encontrado."
    }
  }

  response = {
    id: $aluno.id
    nome: $aluno.nome
    cpf: $aluno.cpf
    data_nascimento: $aluno.data_nascimento
    contato: $aluno.contato
    email: $aluno.email
    endereco: $aluno.endereco
    situacao: $aluno.situacao
  }
  guid = "QXOZWTwbYGkSUbAFm6XyzW6CuqI"
}
