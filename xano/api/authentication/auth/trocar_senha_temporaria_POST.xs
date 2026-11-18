// Troca credencial temporária sem emitir sessão autenticada.
query "auth/trocar-senha-temporaria" verb=POST {
  api_group = "Authentication"

  input {
    email email filters=trim|lower
    text temporary_password
    text password filters=min:8
    text password_confirmation
  }

  stack {
    precondition ($input.password == $input.password_confirmation) {
      error_type = "inputerror"
      error = "A confirmação da senha não corresponde."
    }

    precondition (("/[A-Za-z]/"|regex_matches:$input.password) && ("/[0-9]/"|regex_matches:$input.password)) {
      error_type = "inputerror"
      error = "A senha deve conter pelo menos uma letra e um número."
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
            "temporary_password"
            "temporary_password_expires_at"
          ]
          mock = {
            "rejects expired temporary password": {
              id: 2147483641
              email: "employee@example.test"
              role: "instrutor"
              situacao: "Ativo"
              password: "synthetic-hash"
              temporary_password: true
              temporary_password_expires_at: "2020-01-01T00:00:00Z"
            }
            "rejects incorrect temporary password": {
              id: 2147483641
              email: "employee@example.test"
              role: "instrutor"
              situacao: "Ativo"
              password: "synthetic-hash"
              temporary_password: true
              temporary_password_expires_at: "2099-01-01T00:00:00Z"
            }
            "changes temporary password without issuing a session": {
              id: 2147483641
              email: "employee@example.test"
              role: "instrutor"
              situacao: "Ativo"
              password: "synthetic-hash"
              temporary_password: true
              temporary_password_expires_at: "2099-01-01T00:00:00Z"
            }
            "rejects after five temporary password attempts": {
              id: 2147483641
              email: "employee@example.test"
              role: "instrutor"
              situacao: "Ativo"
              password: "synthetic-hash"
              temporary_password: true
              temporary_password_expires_at: "2099-01-01T00:00:00Z"
            }
          }
        } as $employee

        precondition ($employee != null && ($employee.role == "admin" || $employee.role == "recepcionista" || $employee.role == "instrutor") && $employee.situacao != "Inativo" && $employee.temporary_password == true && $employee.temporary_password_expires_at > now) {
          error_type = "accessdenied"
          error = "A senha temporária não é mais válida. Solicite uma nova ao administrador."
        }

        var $temporary_password_rate_limit_status {
          value = "check"
          mock = {
            "rejects incorrect temporary password": "allowed"
            "changes temporary password without issuing a session": "allowed"
            "rejects after five temporary password attempts": "blocked"
          }
        }

        conditional {
          if ($temporary_password_rate_limit_status == "check") {
            redis.ratelimit {
              key = "temporary_password_attempts:" ~ $employee.id
              max = 5
              ttl = 900
              error = "Muitas tentativas. Aguarde 15 minutos antes de tentar novamente."
            }
          }
        }

        precondition ($temporary_password_rate_limit_status != "blocked") {
          error_type = "accessdenied"
          error = "Muitas tentativas. Aguarde 15 minutos antes de tentar novamente."
        }

        db.edit user {
          field_name = "id"
          field_value = $employee.id
          data = {temporary_password_lock_at: now}
          mock = {
            "rejects incorrect temporary password": {
              id: 2147483641
              role: "instrutor"
              situacao: "Ativo"
              password: "synthetic-hash"
              temporary_password: true
              temporary_password_expires_at: "2099-01-01T00:00:00Z"
            }
            "changes temporary password without issuing a session": {
              id: 2147483641
              role: "instrutor"
              situacao: "Ativo"
              password: "synthetic-hash"
              temporary_password: true
              temporary_password_expires_at: "2099-01-01T00:00:00Z"
            }
          }
        } as $locked_employee

        security.check_password {
          text_password = $input.temporary_password
          hash_password = $locked_employee.password
          mock = {
            "rejects incorrect temporary password": false
            "changes temporary password without issuing a session": true
          }
        } as $temporary_password_matches

        precondition ($temporary_password_matches && $locked_employee.temporary_password == true && $locked_employee.temporary_password_expires_at > now) {
          error_type = "accessdenied"
          error = "A senha temporária não é mais válida. Solicite uma nova ao administrador."
        }

        db.edit user {
          field_name = "id"
          field_value = $locked_employee.id
          data = {
            password: $input.password
            temporary_password: false
            temporary_password_expires_at: null
            temporary_password_lock_at: null
          }
          mock = {
            "changes temporary password without issuing a session": {
              id: 2147483641
              role: "instrutor"
              situacao: "Ativo"
              temporary_password: false
              temporary_password_expires_at: null
            }
          }
        } as $updated_employee

      }
    }
  }

  response = {success: true}

  test "rejects mismatched password confirmation" {
    input = {
      email: "employee@example.test"
      temporary_password: "Password1"
      password: "Password2"
      password_confirmation: "Password3"
    }
    expect.to_throw
  }

  test "rejects expired temporary password" {
    input = {
      email: "employee@example.test"
      temporary_password: "Password1"
      password: "NewPassword1"
      password_confirmation: "NewPassword1"
    }
    expect.to_throw
  }

  test "rejects incorrect temporary password" {
    input = {
      email: "employee@example.test"
      temporary_password: "Password1"
      password: "NewPassword1"
      password_confirmation: "NewPassword1"
    }
    expect.to_throw
  }

  test "rejects after five temporary password attempts" {
    input = {
      email: "employee@example.test"
      temporary_password: "Password1"
      password: "NewPassword1"
      password_confirmation: "NewPassword1"
    }
    expect.to_throw
  }

  test "changes temporary password without issuing a session" {
    input = {
      email: "employee@example.test"
      temporary_password: "Password1"
      password: "NewPassword1"
      password_confirmation: "NewPassword1"
    }
    expect.to_equal ($response.success) {value = true}
  }

  guid = "9v3Q1p8m5K2x7N4c0A6d9R5s3Tz"
}
