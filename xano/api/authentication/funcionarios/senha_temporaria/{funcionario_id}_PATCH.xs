// Reemite senha temporária somente para conta ativa cuja credencial expirou.
query "funcionarios/senha-temporaria/{funcionario_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"

  input {
    int funcionario_id {
      table = "user"
    }
    text temporary_password filters=min:8
    text temporary_password_confirmation
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.temporary_password == $input.temporary_password_confirmation) {
      error_type = "inputerror"
      error = "A confirmação da senha não corresponde."
    }

    precondition (("/[A-Za-z]/"|regex_matches:$input.temporary_password) && ("/[0-9]/"|regex_matches:$input.temporary_password)) {
      error_type = "inputerror"
      error = "A senha deve conter pelo menos uma letra e um número."
    }

    db.transaction {
      stack {
        db.get user {
          field_name = "id"
          field_value = $input.funcionario_id
          output = [
            "id"
            "name"
            "email"
            "role"
            "situacao"
            "temporary_password"
            "temporary_password_expires_at"
          ]
          mock = {
            "reissues expired password": {
              id: 2147483641
              name: "Ana"
              email: "ana@example.test"
              role: "instrutor"
              situacao: "Ativo"
              temporary_password: true
              temporary_password_expires_at: "2020-01-01T00:00:00Z"
            }
            "rejects active temporary password": {
              id: 2147483641
              name: "Ana"
              email: "ana@example.test"
              role: "instrutor"
              situacao: "Ativo"
              temporary_password: true
              temporary_password_expires_at: "2099-01-01T00:00:00Z"
            }
            "rejects inactive employee": {
              id: 2147483641
              name: "Ana"
              email: "ana@example.test"
              role: "instrutor"
              situacao: "Inativo"
              temporary_password: true
              temporary_password_expires_at: "2020-01-01T00:00:00Z"
            }
            "rejects missing employee": null
          }
        } as $employee

        precondition ($employee != null && ($employee.role == "admin" || $employee.role == "recepcionista" || $employee.role == "instrutor")) {
          error_type = "notfound"
          error = "Funcionário não encontrado."
        }

        precondition ($employee.situacao != "Inativo" && $employee.temporary_password == true && ($employee.temporary_password_expires_at == null || $employee.temporary_password_expires_at <= now)) {
          error_type = "inputerror"
          error = "A senha temporária ainda não expirou ou não se aplica a esta conta."
        }

        db.edit user {
          field_name = "id"
          field_value = $employee.id
          data = {temporary_password_lock_at: now}
          mock = {
            "reissues expired password": {
              id: 2147483641
              name: "Ana"
              email: "ana@example.test"
              role: "instrutor"
              situacao: "Ativo"
              temporary_password: true
              temporary_password_expires_at: "2020-01-01T00:00:00Z"
            }
          }
        } as $locked_employee

        precondition ($locked_employee.temporary_password == true && ($locked_employee.temporary_password_expires_at == null || $locked_employee.temporary_password_expires_at <= now)) {
          error_type = "inputerror"
          error = "A senha temporária ainda não expirou ou não se aplica a esta conta."
        }

        db.edit user {
          field_name = "id"
          field_value = $locked_employee.id
          data = {
            password: $input.temporary_password
            temporary_password: true
            temporary_password_expires_at: now|transform_timestamp:"+24 hours"
            temporary_password_lock_at: null
          }
          mock = {
            "reissues expired password": {
              id: 2147483641
              name: "Ana"
              email: "ana@example.test"
              role: "instrutor"
              situacao: "Ativo"
              temporary_password: true
              temporary_password_expires_at: "2099-01-01T00:00:00Z"
            }
          }
        } as $updated_employee
      }
    }
  }

  response = {success: true}

  test "rejects missing employee" {
    input = {
      funcionario_id: 2147483647
      temporary_password: "Password1"
      temporary_password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects active temporary password" {
    input = {
      funcionario_id: 2147483641
      temporary_password: "Password1"
      temporary_password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects inactive employee" {
    input = {
      funcionario_id: 2147483641
      temporary_password: "Password1"
      temporary_password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects mismatched password confirmation" {
    input = {
      funcionario_id: 2147483647
      temporary_password: "Password1"
      temporary_password_confirmation: "Password2"
    }
    expect.to_throw
  }

  test "reissues expired password" {
    input = {
      funcionario_id: 2147483641
      temporary_password: "Password1"
      temporary_password_confirmation: "Password1"
    }
    expect.to_equal ($response.success) {value = true}
  }

  guid = "7K6m1q4s9Z2p5V8c3N0b7A6d4Qe"
}
