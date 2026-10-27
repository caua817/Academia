query "alunos/atualizar/{aluno_id}" verb=PUT {
  api_group = "Authentication"
  auth = "user"
  description = "Atualiza os dados de um aluno existente."

  input {
    int aluno_id {
      table = "aluno"
    }
    text nome filters=trim
    text cpf? filters=trim
    date data_nascimento?
    text contato? filters=trim
    email? email filters=trim|lower
    text endereco? filters=trim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    precondition (($input.nome|strlen) > 0) {
      error_type = "inputerror"
      error = "O nome do aluno é obrigatório."
    }

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
        nome: $input.nome
        cpf: $input.cpf
        data_nascimento: $input.data_nascimento
        contato: $input.contato
        email: $input.email
        endereco: $input.endereco
      }
    } as $aluno
  }

  response = {
    id: $aluno.id
    nome: $aluno.nome
    contato: $aluno.contato
    email: $aluno.email
    situacao: $aluno.situacao
  }
  guid = "OwqIhTRx_aiVP7cuBzT5rO0vaTU"
}
