query "alunos" verb=GET {
  api_group = "Authentication"
  auth = "user"
  description = "Lista os alunos para usuários administradores."

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    db.query "aluno" {
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $alunos

    var $alunos_visiveis {
      value = $alunos|map:{id:$$.id,nome:$$.nome,contato:$$.contato,email:$$.email,situacao:$$.situacao}
    }
  }

  response = $alunos_visiveis
  guid = "J8zfUdWmg0yEJQ4NbH_ustj6hBM"
}
