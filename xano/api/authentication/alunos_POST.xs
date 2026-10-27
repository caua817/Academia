query "alunos" verb=POST {
  api_group = "Authentication"
  auth = "user"
  description = "Cadastra um aluno para usuários administradores."

  input {
    text nome filters=trim
    text cpf? filters=trim
    date data_nascimento?
    text contato? filters=trim
    email? email filters=trim|lower
    text endereco? filters=trim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    precondition (($input.nome|strlen) > 0) {
      error_type = "inputerror"
      error = "O nome do aluno é obrigatório."
    }

    db.add "aluno" {
      data = {
        nome: $input.nome
        cpf: $input.cpf
        data_nascimento: $input.data_nascimento
        contato: $input.contato
        email: $input.email
        endereco: $input.endereco
        situacao: "Ativo"
      }
    } as $aluno
  }

  response = {
    id: $aluno.id
    nome: $aluno.nome
    contato: $aluno.contato
    email: $aluno.email
    situacao: $aluno.situacao
  }
  guid = "UsKzGBnSvriMHQdYLByCbZXTImY"
}
