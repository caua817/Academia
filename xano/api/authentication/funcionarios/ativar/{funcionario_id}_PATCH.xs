// Reativa uma conta de funcionário preservada.
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
        "activates employee": {
          id: 2147483641
          name: "Ana"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Inativo"
        }
        "rejects missing employee": null
        "rejects member account": {
          id: 2147483642
          name: "Aluno"
          email: "aluno@example.test"
          role: "member"
          situacao: "Ativo"
        }
      }
    } as $existente

    precondition ($existente != null && ($existente.role == "admin" || $existente.role == "recepcionista" || $existente.role == "instrutor")) {
      error_type = "notfound"
      error = "Funcionário não encontrado."
    }

    db.edit user {
      field_name = "id"
      field_value = $input.funcionario_id
      data = {situacao: "Ativo"}
      mock = {
        "activates employee": {
          id: 2147483641
          name: "Ana"
          email: "ana@example.test"
          role: "instrutor"
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

  test "activates employee" {
    input = {funcionario_id: 2147483641}
    expect.to_equal ($response.situacao) {value = "Ativo"}
  }

  test "rejects missing employee" {
    input = {funcionario_id: 2147483643}
    expect.to_throw
  }

  test "rejects member account" {
    input = {funcionario_id: 2147483642}
    expect.to_throw
  }
  guid = "CoeVYJ5lu0X2-xebrRRGL340Uxo"
}
