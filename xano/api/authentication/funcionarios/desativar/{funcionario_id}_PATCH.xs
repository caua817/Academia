// Desativa uma conta não administrativa sem remover seu histórico.
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
        "deactivates employee": {
          id: 2147483647
          name: "Ana Exemplo"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
        "rejects administrator deactivation": {
          id: 2147483647
          name: "Admin Exemplo"
          email: "admin@example.test"
          role: "admin"
          situacao: "Ativo"
        }
        "rejects legacy member deactivation": {
          id: 2147483647
          name: "Membro Legado"
          email: "member@example.test"
          role: "member"
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
      field_value = $existente.id
      data = {situacao: "Inativo"}
      mock = {
        "deactivates employee": {
          id: 2147483647
          name: "Ana Exemplo"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Inativo"
          password: "synthetic-hash"
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

  test "deactivates employee" {
    input = {funcionario_id: 2147483647}
    expect.to_equal ($response) {
      value = {
        id: 2147483647
        name: "Ana Exemplo"
        email: "ana@example.test"
        role: "instrutor"
        situacao: "Inativo"
      }
    }
  }

  test "rejects administrator deactivation" {
    input = {funcionario_id: 2147483647}
    expect.to_throw
  }

  test "rejects legacy member deactivation" {
    input = {funcionario_id: 2147483647}
    expect.to_throw
  }
}
