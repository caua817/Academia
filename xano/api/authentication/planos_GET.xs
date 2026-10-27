query "planos" verb=GET {
  api_group = "Authentication"
  auth = "user"
  description = "Lista planos ativos e descontinuados para administradores."

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    db.query "plano" {
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $planos

    var $planos_visiveis {
      value = $planos|map:{id:$$.id,nome:$$.nome,descricao:$$.descricao,duracao_meses:$$.duracao_meses,valor:$$.valor,situacao:$$.situacao,created_at:$$.created_at}
    }
  }

  response = $planos_visiveis
  guid = "cKEUgDawJSDtfmz-oChI-8jaQhQ"
}
