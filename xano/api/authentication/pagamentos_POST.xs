// Registra o pagamento integral de uma mensalidade.
query pagamentos verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
    int mensalidade_id
    decimal valor filters=min:0.01
    text forma_pagamento filters=trim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.forma_pagamento == "PIX" || $input.forma_pagamento == "Cartão") {
      error_type = "inputerror"
      error = "A forma de pagamento deve ser PIX ou Cartão."
    }

    db.transaction {
      stack {
        db.edit mensalidade {
          field_name = "id"
          field_value = $input.mensalidade_id
          data = {pagamento_lock_at: now}
        } as $mensalidade_bloqueada

        db.get mensalidade {
          field_name = "id"
          field_value = $input.mensalidade_id
        } as $mensalidade

        precondition ($mensalidade != null) {
          error_type = "notfound"
          error = "Mensalidade não encontrada."
        }

        precondition ($input.valor == $mensalidade.valor) {
          error_type = "inputerror"
          error = "O pagamento deve corresponder ao valor integral da mensalidade."
        }

        db.query pagamento {
          where = $db.pagamento.mensalidade_id == $mensalidade.id && $db.pagamento.situacao == "Registrado"
          return = {type: "exists"}
        } as $pagamento_ativo

        precondition (!$pagamento_ativo) {
          error_type = "inputerror"
          error = "Esta mensalidade já possui um pagamento ativo."
        }

        db.add pagamento {
          data = {
            mensalidade_id  : $mensalidade.id
            valor           : $mensalidade.valor
            forma_pagamento : $input.forma_pagamento
            data_pagamento  : now
            registrado_por  : $auth.id
            situacao        : "Registrado"
          }
        } as $pagamento
      }
    }
  }

  response = {
    id              : $pagamento.id
    mensalidade_id  : $pagamento.mensalidade_id
    valor           : $pagamento.valor
    forma_pagamento : $pagamento.forma_pagamento
    data_pagamento  : $pagamento.data_pagamento
    registrado_por  : $pagamento.registrado_por
    situacao        : $pagamento.situacao
  }
}
