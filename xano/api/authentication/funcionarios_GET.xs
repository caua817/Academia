// Lista somente contas com perfil de funcionário e campos operacionais.
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
        "excludes members and credentials": [
          {
            id: 2147483641
            name: "Ana Administradora"
            email: "ana@example.test"
            role: "admin"
            situacao: "Ativo"
            temporary_password: false
            password: "must-not-be-returned"
            password_reset: {token: "must-not-be-returned"}
          }
          {
            id: 2147483642
            name: "Aluno"
            email: "aluno@example.test"
            role: "member"
            situacao: "Ativo"
            temporary_password: false
            password: "must-not-be-returned"
          }
        ]
      }
    } as $contas

    var $funcionarios {
      value = []
    }

    foreach ($contas) {
      each as $conta {
        var $situacao {
          value = "Ativo"
        }

        conditional {
          if ($conta.situacao != null) {
            var.update $situacao {
              value = $conta.situacao
            }
          }
        }

        var $temporary_password_expired {
          value = false
        }

        conditional {
          if ($conta.temporary_password == true && $conta.situacao != "Inativo" && ($conta.temporary_password_expires_at == null || $conta.temporary_password_expires_at <= now)) {
            var.update $temporary_password_expired {
              value = true
            }
          }
        }

        var $status_convite {
          value = ""
        }

        conditional {
          if ($conta.temporary_password == true) {
            conditional {
              if ($temporary_password_expired) {
                var.update $status_convite {
                  value = "Senha temporária expirada"
                }
              }

              else {
                var.update $status_convite {
                  value = "Senha temporária ativa"
                }
              }
            }
          }
        }

        conditional {
          if ($conta.role == "admin" || $conta.role == "recepcionista" || $conta.role == "instrutor") {
            var.update $funcionarios {
              value = $funcionarios
                |append:```
                  {
                    id: $conta.id,
                    name: $conta.name,
                    email: $conta.email,
                    role: $conta.role,
                    situacao: $situacao,
                    status_convite: $status_convite,
                    temporary_password_expired: $temporary_password_expired
                  }
                  ```
            }
          }
        }
      }
    }
  }

  response = $funcionarios

  test "excludes members and credentials" {
    input = {}
    expect.to_equal ($response) {
      value = [
        {
          id: 2147483641,
          name: "Ana Administradora",
          email: "ana@example.test",
          role: "admin",
          situacao: "Ativo",
          status_convite: "",
          temporary_password_expired: false
        }
      ]
    }
  }
  guid = "aOBnLd5CTGNh2DHCQ7Sz3hCtqps"
}
