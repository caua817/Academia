// Atualiza os dados operacionais de uma conta de funcionário.
query "funcionarios/atualizar/{funcionario_id}" verb=PUT {
  api_group = "Authentication"
  auth = "user"

  input {
    int funcionario_id {
      table = "user"
    }
    text name filters=trim
    email email filters=trim|lower
    text role filters=trim|lower
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

    db.get user {
      field_name = "id"
      field_value = $input.funcionario_id
      output = ["id", "email", "role", "situacao"]
      mock = {
        "updates operational employee fields": {
          id: 2147483647
          email: "ana-old@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
        "updates administrator operational fields": {
          id: 2147483647
          email: "admin-old@example.test"
          role: "admin"
          situacao: "Ativo"
        }
        "rejects administrator role change": {
          id: 2147483647
          email: "admin@example.test"
          role: "admin"
          situacao: "Ativo"
        }
        "rejects duplicate email": {
          id: 2147483647
          email: "ana-old@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
        "rejects legacy member account": {
          id: 2147483647
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

    precondition ($existente.role != "admin" || $input.role == "admin") {
      error_type = "inputerror"
      error = "O perfil de administrador não pode ser rebaixado por esta operação."
    }

    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
      mock = {
        "updates operational employee fields": null
        "updates administrator operational fields": null
        "rejects administrator role change": null
        "rejects duplicate email": {id: 2147483648}
      }
    } as $email_existente

    precondition ($email_existente == null || $email_existente.id == $existente.id) {
      error_type = "inputerror"
      error = "Este e-mail já pertence a outra conta."
    }

    db.edit user {
      field_name = "id"
      field_value = $existente.id
      data = {
        name: $input.name
        email: $input.email
        role: $input.role
      }
      mock = {
        "updates operational employee fields": {
          id: 2147483647
          name: "Ana Exemplo"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Ativo"
          password: "synthetic-hash"
        }
        "updates administrator operational fields": {
          id: 2147483647
          name: "Admin Exemplo"
          email: "admin@example.test"
          role: "admin"
          situacao: "Ativo"
          password: "synthetic-hash"
        }
      }
    } as $funcionario

    var $situacao {
      value = "Ativo"
    }

    conditional {
      if ($funcionario.situacao == "Inativo") {
        var.update $situacao {
          value = "Inativo"
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

  test "updates operational employee fields" {
    input = {
      funcionario_id: 2147483647
      name: "Ana Exemplo"
      email: "ana@example.test"
      role: "instrutor"
    }
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

  test "rejects administrator role change" {
    input = {
      funcionario_id: 2147483647
      name: "Admin Exemplo"
      email: "admin@example.test"
      role: "instrutor"
    }
    expect.to_throw
  }

  test "updates administrator operational fields without changing role" {
    input = {
      funcionario_id: 2147483647
      name: "Admin Exemplo"
      email: "admin@example.test"
      role: "admin"
    }
    expect.to_equal ($response) {
      value = {
        id: 2147483647
        name: "Admin Exemplo"
        email: "admin@example.test"
        role: "admin"
        situacao: "Ativo"
      }
    }
  }

  test "rejects duplicate email" {
    input = {
      funcionario_id: 2147483647
      name: "Ana Exemplo"
      email: "other@example.test"
      role: "instrutor"
    }
    expect.to_throw
  }

  test "rejects legacy member account" {
    input = {
      funcionario_id: 2147483647
      name: "Member Legado"
      email: "member@example.test"
      role: "instrutor"
    }
    expect.to_throw
  }
  guid = "FxZ6Q2AYqq3RN0Tl22RLFfWR5q4"
}
