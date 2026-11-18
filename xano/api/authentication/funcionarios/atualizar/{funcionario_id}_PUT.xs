// Atualiza os campos operacionais permitidos de um funcionário.
query "funcionarios/atualizar/{funcionario_id}" verb=PUT {
  api_group = "Authentication"
  auth = "user"

  input {
    int funcionario_id {
      table = "user"
    }
    text name? filters=trim
    email email filters=trim|lower
    text role filters=trim|lower
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.name != null && ($input.name|strlen) > 0) {
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
      output = ["id", "name", "email", "role", "situacao"]
      mock = {
        "updates employee": {
          id: 2147483641
          name: "Ana"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
        "rejects administrator role change": {
          id: 2147483641
          name: "Admin"
          email: "admin@example.test"
          role: "admin"
          situacao: "Ativo"
        }
        "rejects missing employee": null
        "rejects duplicate email": {
          id: 2147483641
          name: "Ana"
          email: "ana@example.test"
          role: "admin"
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

    db.query user {
      where = $db.user.email == $input.email && $db.user.id != $input.funcionario_id
      return = {type: "exists"}
      mock = {
        "updates employee": false
        "rejects duplicate email": true
      }
    } as $email_em_uso

    precondition (!$email_em_uso) {
      error_type = "inputerror"
      error = "Este e-mail já pertence a outra conta."
    }

    db.edit user {
      field_name = "id"
      field_value = $input.funcionario_id
      data = {
        name: $input.name
        email: $input.email
        role: $input.role
      }
      mock = {
        "updates employee": {
          id: 2147483641
          name: "Ana"
          email: "ana@example.test"
          role: "instrutor"
          situacao: "Ativo"
        }
      }
    } as $funcionario

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

  test "updates employee" {
    input = {
      funcionario_id: 2147483641
      name: "Ana"
      email: "ana@example.test"
      role: "instrutor"
    }
    expect.to_equal ($response.role) {value = "instrutor"}
    expect.to_equal ($response.situacao) {value = "Ativo"}
  }

  test "rejects invalid role" {
    input = {
      funcionario_id: 2147483641
      name: "Ana"
      email: "ana@example.test"
      role: "member"
    }
    expect.to_throw
  }

  test "rejects administrator role change" {
    input = {
      funcionario_id: 2147483641
      name: "Admin"
      email: "admin@example.test"
      role: "instrutor"
    }
    expect.to_throw
  }

  test "rejects missing employee" {
    input = {
      funcionario_id: 2147483643
      name: "Ana"
      email: "ana@example.test"
      role: "instrutor"
    }
    expect.to_throw
  }

  test "rejects duplicate email" {
    input = {
      funcionario_id: 2147483641
      name: "Ana"
      email: "used@example.test"
      role: "instrutor"
    }
    expect.to_throw
  }
  guid = "FxZ6Q2AYqq3RN0Tl22RLFfWR5q4"
}
