// Cria um funcionário com senha temporária para entrega presencial.
query "funcionarios/provisionar" verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
    text name filters=trim
    email email filters=trim|lower
    text role filters=trim|lower
    text temporary_password filters=min:8
    text temporary_password_confirmation
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition (($input.name|strlen) > 0) {
      error_type = "inputerror"
      error = "O nome do funcionário é obrigatório."
    }

    precondition ($input.role == "admin" || $input.role == "recepcionista" || $input.role == "instrutor") {
      error_type = "inputerror"
      error = "Perfil de funcionário inválido."
    }

    precondition ($input.temporary_password == $input.temporary_password_confirmation) {
      error_type = "inputerror"
      error = "A confirmação da senha não corresponde."
    }

    precondition (("/[A-Za-z]/"|regex_matches:$input.temporary_password) && ("/[0-9]/"|regex_matches:$input.temporary_password)) {
      error_type = "inputerror"
      error = "A senha deve conter pelo menos uma letra e um número."
    }

    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
      mock = {
        "creates temporary employee without returning a password": null
        "rejects duplicate email": {id: 2147483641}
      }
    } as $existing_user

    precondition ($existing_user == null) {
      error_type = "inputerror"
      error = "Este e-mail já pertence a uma conta."
    }

    db.add user {
      data = {
        name: $input.name
        email: $input.email
        role: $input.role
        password: $input.temporary_password
        situacao: "Ativo"
        temporary_password: true
        temporary_password_expires_at: now|transform_timestamp:"+24 hours"
      }
      mock = {
        "creates temporary employee without returning a password": {
          id: 2147483641
          name: "Funcionário de teste"
          email: "employee@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
      }
    } as $employee
  }

  response = {
    id: $employee.id
    name: $employee.name
    email: $employee.email
    role: $employee.role
    situacao: "Ativo"
    status_convite: "Senha temporária"
  }

  test "rejects invalid role" {
    input = {
      name: "Funcionário de teste"
      email: "employee@example.test"
      role: "member"
      temporary_password: "Password1"
      temporary_password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "rejects mismatched password confirmation" {
    input = {
      name: "Funcionário de teste"
      email: "employee@example.test"
      role: "instrutor"
      temporary_password: "Password1"
      temporary_password_confirmation: "Password2"
    }
    expect.to_throw
  }

  test "rejects duplicate email" {
    input = {
      name: "Funcionário de teste"
      email: "employee@example.test"
      role: "instrutor"
      temporary_password: "Password1"
      temporary_password_confirmation: "Password1"
    }
    expect.to_throw
  }

  test "creates temporary employee without returning a password" {
    input = {
      name: "Funcionário de teste"
      email: "employee@example.test"
      role: "instrutor"
      temporary_password: "Password1"
      temporary_password_confirmation: "Password1"
    }
    expect.to_equal ($response.status_convite) {
      value = "Senha temporária"
    }
  }

  guid = "dxbqFfXjM9gR4P6K2v7wqB0aN3s"
}
