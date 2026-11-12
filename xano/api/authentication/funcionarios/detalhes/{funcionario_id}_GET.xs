// Retorna dados operacionais do funcionário selecionado.
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
      mock = {
        "returns operational employee fields": {
          id: 2147483647
          name: "Ana Exemplo"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Ativo"
          password: "synthetic-hash"
          password_reset: {token: "synthetic-token"}
        }
        "rejects non employee account": {
          id: 2147483647
          name: "Conta legada"
          email: "legacy@example.test"
          role: "member"
        }
      }
    } as $funcionario

    precondition ($funcionario != null && ($funcionario.role == "admin" || $funcionario.role == "recepcionista" || $funcionario.role == "instrutor")) {
      error_type = "notfound"
      error = "Funcionário não encontrado."
    }

    var $situacao {
      value = "Ativo"
    }

    conditional {
      if ($funcionario.situacao != null) {
        var.update $situacao {
          value = $funcionario.situacao
        }
      }
    }

  }

  response = {
    id: $funcionario.id
    name: $funcionario.name
    email: $funcionario.email
    role: $funcionario.role
    situacao: $situacao
  }

  test "returns operational employee fields" {
    input = {funcionario_id: 2147483647}
    expect.to_equal ($response) {
      value = {
        id: 2147483647
        name: "Ana Exemplo"
        email: "ana@example.test"
        role: "instrutor"
        situacao: "Ativo"
      }
    }
  }

  test "rejects non employee account" {
    input = {funcionario_id: 2147483647}
    expect.to_throw
  }
  guid = "UNCbQ5N9VKahjmLQGYOsfJkICIk"
}
