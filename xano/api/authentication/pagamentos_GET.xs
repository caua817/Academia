// Lista lançamentos de pagamento e suas correções para administradores.
query pagamentos verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.query pagamento {
      join = {
        mensalidade: {
          table: "mensalidade"
          where: $db.pagamento.mensalidade_id == $db.mensalidade.id
        }
        matricula: {
          table: "matricula"
          where: $db.mensalidade.matricula_id == $db.matricula.id
        }
        aluno: {
          table: "aluno"
          where: $db.matricula.aluno_id == $db.aluno.id
        }
      }

      eval = {
        aluno_nome: $db.aluno.nome
        competencia: $db.mensalidade.competencia
      }
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $pagamentos

    var $pagamentos_visiveis {
      value = $pagamentos
        |map:{
          id:$$.id,
          mensalidade_id:$$.mensalidade_id,
          aluno_nome:$$.aluno_nome,
          competencia:$$.competencia,
          valor:$$.valor,
          forma_pagamento:$$.forma_pagamento,
          data_pagamento:$$.data_pagamento,
          registrado_por:$$.registrado_por,
          situacao:$$.situacao,
          tipo_correcao:$$.tipo_correcao,
          motivo_correcao:$$.motivo_correcao,
          corrigido_em:$$.corrigido_em,
          corrigido_por:$$.corrigido_por
        }
    }
  }

  response = $pagamentos_visiveis
  guid = "wIz32wpOGfhZWYc3qZHcVF5Nzzc"
}
