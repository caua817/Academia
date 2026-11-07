// Fornece apenas alunos ativos para o formulário de check-in.
query "checkins/alunos" verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.query aluno {
      where = $db.aluno.situacao == "Ativo"
      output = ["id", "nome"]
      sort = {nome: "asc"}
      return = {type: "list"}
    } as $alunos

    var $alunos_visiveis {
      value = $alunos
        |map:{id:$$.id,nome:$$.nome}
    }
  }

  response = $alunos_visiveis
}
