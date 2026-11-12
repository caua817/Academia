// Lista modalidades sem excluir as desativadas do histórico administrativo.
query modalidades verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.query modalidade {
      sort = {nome: "asc"}
      return = {type: "list"}
    } as $modalidades

    var $modalidades_visiveis {
      value = $modalidades|map:{id:$$.id,nome:$$.nome,descricao:$$.descricao,situacao:$$.situacao,created_at:$$.created_at}
    }
  }

  response = $modalidades_visiveis
  guid = "7dvQ6jNjd-CF0z8qv7w4aV5gX1o"
}
