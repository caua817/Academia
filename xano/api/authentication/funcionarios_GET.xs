// Lista funcionários sem expor campos de autenticação.
query funcionarios verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.query user {
      where = $db.user.role == "admin" || $db.user.role == "recepcionista" || $db.user.role == "instrutor"
      sort = {name: "asc"}
      return = {type: "list"}
      mock = {
        "returns operational employee fields": [
          {
            id: 2147483647
            name: "Ana Exemplo"
            email: "ana@example.test"
            role: "instrutor"
            situacao: "Ativo"
            password: "synthetic-hash"
            password_reset: {token: "synthetic-token"}
          }
        ]
      }
    } as $funcionarios

    var $funcionarios_visiveis {
      value = []
    }

    foreach ($funcionarios) {
      each as $funcionario {
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

        var.update $funcionarios_visiveis {
          value = $funcionarios_visiveis
            |append:```
              {
                id: $funcionario.id,
                name: $funcionario.name,
                email: $funcionario.email,
                role: $funcionario.role,
                situacao: $situacao
              }
              ```
        }
      }
    }
  }

  response = $funcionarios_visiveis

  test "returns operational employee fields" {
    input = {}
    expect.to_equal ($response) {
      value = [
        {
          id: 2147483647
          name: "Ana Exemplo"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
      ]
    }
  }
}
