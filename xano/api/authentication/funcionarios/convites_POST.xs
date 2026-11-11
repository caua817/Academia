// Cria ou reenvia convite sem expor credenciais.
query "funcionarios/convites" verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
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
      field_name = "email"
      field_value = $input.email
      output = ["id", "password", "role", "situacao"]
    } as $existente

    conditional {
      if ($existente != null) {
        precondition (($existente.role == "admin" || $existente.role == "recepcionista" || $existente.role == "instrutor") && $existente.password == null && $existente.situacao != "Inativo") {
          error_type = "inputerror"
          error = "Este e-mail já pertence a uma conta."
        }

        precondition ($existente.role == $input.role) {
          error_type = "inputerror"
          error = "O perfil da conta pendente não pode ser alterado pelo reenvio do convite."
        }

        db.edit user {
          field_name = "id"
          field_value = $existente.id
          data = {name: $input.name}
        } as $funcionario
      }

      else {
        db.add user {
          data = {
            name: $input.name
            email: $input.email
            role: $input.role
            situacao: "Ativo"
          }
        } as $funcionario
      }
    }

    function.run "Quick Start/generate_magic_link" {
      input = {email: $input.email}
    } as $convite

    var $api_base_url {
      value = $env.$api_baseurl
    }

    var $magic_link {
      value = $api_base_url
        |concat:"1_start_here_demo_page#/update-password":"/"
        |concat:$convite.token:"?magic_token="
        |concat:$convite.email:""
    }

    util.template_engine {
      value = """
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Convite da academia</title></head>
        <body>
          <h2>Convite para acessar o sistema da academia</h2>
          <p>Use o link abaixo para definir sua senha e ativar seu acesso:</p>
          <p><a href="{{ $var.magic_link }}">Definir senha</a></p>
        </body>
        </html>
        """
    } as $message

    util.send_email {
      service_provider = "xano"
      subject = "Convite para acessar o sistema da academia"
      message = $message
    } as $send_email
  }

  response = {
    id: $funcionario.id
    name: $funcionario.name
    email: $funcionario.email
    role: $funcionario.role
    situacao: "Ativo"
    status_convite: "Enviado"
  }
}
