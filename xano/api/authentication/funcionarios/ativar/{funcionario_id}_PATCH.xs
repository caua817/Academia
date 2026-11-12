// Reativa uma conta de funcionário.
query "funcionarios/ativar/{funcionario_id}" verb=PATCH {
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
        "reactivates legacy administrator": {
          id: 2147483647
          name: "Admin Exemplo"
          email: "admin@example.test"
          role: "admin"
          situacao: "Inativo"
        }
        "rejects legacy member account": {
          id: 2147483647
          name: "Membro Legado"
          email: "member@example.test"
          role: "member"
          situacao: "Inativo"
        }
      }
    } as $existente

    precondition ($existente != null && ($existente.role == "admin" || $existente.role == "recepcionista" || $existente.role == "instrutor")) {
      error_type = "notfound"
      error = "Funcionário não encontrado."
    }

    db.edit user {
      field_name = "id"
      field_value = $existente.id
      data = {situacao: "Ativo"}
      mock = {
        "reactivates legacy administrator": {
          id: 2147483647
          name: "Admin Exemplo"
          email: "admin@example.test"
          role: "admin"
          situacao: "Ativo"
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

  test "reactivates legacy administrator" {
    input = {funcionario_id: 2147483647}
    expect.to_equal ($response) {
      value = {
        id: 2147483647
        name: "Admin Exemplo"
        email: "admin@example.test"
        role: "admin"
        situacao: "Ativo"
      }
    }
  }

  test "rejects legacy member account" {
    input = {funcionario_id: 2147483647}
    expect.to_throw
  }
}
