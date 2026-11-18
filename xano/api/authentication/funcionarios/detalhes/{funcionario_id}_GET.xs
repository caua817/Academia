// Consulta os dados operacionais de um funcionário.
query "funcionarios/detalhes/{funcionario_id}" verb=GET {
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
        "returns employee fields only": {
          id: 2147483641
          name: "Ana Administradora"
          email: "ana@example.test"
          role: "admin"
          situacao: "Ativo"
          password: "must-not-be-returned"
          password_reset: {token: "must-not-be-returned"}
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
    } as $conta

    precondition ($conta != null && ($conta.role == "admin" || $conta.role == "recepcionista" || $conta.role == "instrutor")) {
      error_type = "notfound"
      error = "Funcionário não encontrado."
    }
  }

  response = {
    id: $conta.id
    name: $conta.name
    email: $conta.email
    role: $conta.role
    situacao: $conta.situacao
  }

  test "returns employee fields only" {
    input = {funcionario_id: 2147483641}
    expect.to_equal ($response.role) {value = "admin"}
    expect.to_equal ($response.email) {value = "ana@example.test"}
  }

  test "rejects missing employee" {
    input = {funcionario_id: 2147483643}
    expect.to_throw
  }

  test "rejects member account" {
    input = {funcionario_id: 2147483642}
    expect.to_throw
  }
  guid = "UNCbQ5N9VKahjmLQGYOsfJkICIk"
}
