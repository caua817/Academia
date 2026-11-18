// Desativa uma conta de funcionário sem excluir o registro.
query "funcionarios/desativar/{funcionario_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"

  input {
    int funcionario_id {
      table = "user"
    }
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.get user {
      field_name = "id"
      field_value = $input.funcionario_id
      output = ["id", "name", "email", "role", "situacao"]
      mock = {
        "deactivates employee without deleting it": {
          id: 2147483641
          name: "Ana"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
        "rejects missing employee": null
        "rejects member account": {
          id: 2147483642
          name: "Aluno"
          email: "aluno@example.test"
          role: "member"
          situacao: "Ativo"
        }
        "rejects administrator deactivation": {
          id: 2147483644
          name: "Admin"
          email: "admin@example.test"
          role: "admin"
          situacao: "Ativo"
        }
      }
    } as $existente

    precondition ($existente != null && ($existente.role == "admin" || $existente.role == "recepcionista" || $existente.role == "instrutor")) {
      error_type = "notfound"
      error = "Funcionário não encontrado."
    }

    precondition ($existente.role != "admin") {
      error_type = "accessdenied"
      error = "Contas administrativas não podem ser desativadas por esta operação."
    }

    db.edit user {
      field_name = "id"
      field_value = $input.funcionario_id
      data = {situacao: "Inativo"}
      mock = {
        "deactivates employee without deleting it": {
          id: 2147483641
          name: "Ana"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Inativo"
        }
      }
    } as $funcionario
  }

  response = {
    id: $funcionario.id
    name: $funcionario.name
    email: $funcionario.email
    role: $funcionario.role
    situacao: $funcionario.situacao
  }

  test "deactivates employee without deleting it" {
    input = {funcionario_id: 2147483641}
    expect.to_equal ($response.situacao) {value = "Inativo"}
  }

  test "rejects missing employee" {
    input = {funcionario_id: 2147483643}
    expect.to_throw
  }

  test "rejects member account" {
    input = {funcionario_id: 2147483642}
    expect.to_throw
  }

  test "rejects administrator deactivation" {
    input = {funcionario_id: 2147483644}
    expect.to_throw
  }
  guid = "4d6LQSAq0ie08jkTw3AmpJDY3-k"
}
