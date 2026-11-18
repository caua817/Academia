// Aceita convite pendente de funcionário sem criar sessão autenticada.
query "funcionarios/convites/aceitar" verb=POST {
  api_group = "Authentication"

  input {
    email email filters=trim|lower
    text token filters=trim
    text password
    text password_confirmation
  }

  stack {
    precondition (($input.password|strlen) >= 8 && ("/[A-Za-z]/"|regex_matches:$input.password) && ("/[0-9]/"|regex_matches:$input.password)) {
      error_type = "inputerror"
      error = "A senha deve ter pelo menos 8 caracteres, uma letra e um número."
    }

    precondition ($input.password == $input.password_confirmation) {
      error_type = "inputerror"
      error = "A confirmação da senha não corresponde."
    }

    db.transaction {
      stack {
        db.get user {
          field_name = "email"
          field_value = $input.email
          output = [
            "id"
            "role"
            "situacao"
            "password"
            "password_reset.token"
            "password_reset.expiration"
            "password_reset.used"
          ]
          mock = {
            "rejects missing account": null
            "rejects expired invitation": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2020-01-01T00:00:00Z"
                used: false
              }
            }
            "rejects used invitation": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: true
              }
            }
            "rejects non-employee account": {
              id: 2147483647
              role: "member"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: false
              }
            }
            "rejects invalid token": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: false
              }
            }
            "accepts valid invitation": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: false
              }
            }
          }
        } as $funcionario

        precondition ($funcionario != null) {
          error_type = "notfound"
          error = "O convite não é válido. Solicite um novo convite ao administrador."
        }

        db.edit user {
          field_name = "id"
          field_value = $funcionario.id
          data = {invitation_lock_at: now}
          mock = {
            "rejects expired invitation": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2020-01-01T00:00:00Z"
                used: false
              }
            }
            "rejects used invitation": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: true
              }
            }
            "rejects non-employee account": {
              id: 2147483647
              role: "member"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: false
              }
            }
            "rejects invalid token": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: false
              }
            }
            "accepts valid invitation": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: null
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: false
              }
            }
          }
        } as $funcionario_bloqueado

        precondition (($funcionario_bloqueado.role == "admin" || $funcionario_bloqueado.role == "recepcionista" || $funcionario_bloqueado.role == "instrutor") && $funcionario_bloqueado.password == null && $funcionario_bloqueado.situacao == "Ativo" && $funcionario_bloqueado.password_reset.token != null && $funcionario_bloqueado.password_reset.expiration > now && $funcionario_bloqueado.password_reset.used == false) {
          error_type = "unauthorized"
          error = "O convite não é válido. Solicite um novo convite ao administrador."
        }

        security.check_password {
          text_password = $input.token
          hash_password = $funcionario_bloqueado.password_reset.token
          mock = {
            "rejects invalid token": false
            "accepts valid invitation": true
          }
        } as $token_valido

        precondition ($token_valido) {
          error_type = "unauthorized"
          error = "O convite não é válido. Solicite um novo convite ao administrador."
        }

        db.edit user {
          field_name = "id"
          field_value = $funcionario_bloqueado.id
          data = {
            password: $input.password
            password_reset: {
              token: $funcionario_bloqueado.password_reset.token
              expiration: $funcionario_bloqueado.password_reset.expiration
              used: true
            }
            invitation_lock_at: null
          }
          mock = {
            "accepts valid invitation": {
              id: 2147483647
              role: "instrutor"
              situacao: "Ativo"
              password: "synthetic-password-hash"
              password_reset: {
                token: "synthetic-hash"
                expiration: "2099-01-01T00:00:00Z"
                used: true
              }
            }
          }
        } as $ativacao
      }
    }
  }

  response = {success: true}

  test "rejects weak password" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "short"
      password_confirmation: "short"
    }
    expect.to_throw
  }

  test "rejects mismatched confirmation" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "Password1"
      password_confirmation: "Password2"
    }
    expect.to_throw
  }

  test "rejects missing account" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "Password1"
      password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects expired invitation" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "Password1"
      password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects used invitation" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "Password1"
      password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects non-employee account" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "Password1"
      password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects invalid token" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "Password1"
      password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "accepts valid invitation" {
    input = {
      email: "employee@example.test"
      token: "synthetic-token"
      password: "Password1"
      password_confirmation: "Password1"
    }
    expect.to_equal ($response) {
      value = {success: true}
    }
  }
  guid = "hFl7KYiD9WgfJ_a_nKPgRbMF9YU"
}
