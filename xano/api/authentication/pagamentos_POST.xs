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
          mock = {
            "rejects unsupported payment method": {id: 2147483647}
            "rejects partial payment": {id: 2147483647}
            "rejects overpayment": {id: 2147483647}
            "rejects duplicate payment": {id: 2147483647}
            "registers full payment": {id: 2147483647}
          }
        } as $mensalidade_bloqueada

        db.get mensalidade {
          field_name = "id"
          field_value = $input.mensalidade_id
          mock = {
            "rejects partial payment": {id: 2147483647, valor: 12.50}
            "rejects overpayment": {id: 2147483647, valor: 12.50}
            "rejects duplicate payment": {id: 2147483647, valor: 12.50}
            "registers full payment": {id: 2147483647, valor: 12.50}
          }
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
          mock = {
            "rejects duplicate payment": true
            "registers full payment": false
          }
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
          mock = {
            "registers full payment": {
              id: 2147483647
              mensalidade_id: 2147483647
              valor: 12.50
              forma_pagamento: "PIX"
              data_pagamento: "2026-11-07"
              registrado_por: 1
              situacao: "Registrado"
            }
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
  guid = "70mRAmiHAs_dygW1t59iPDjU2S4"

  test "rejects unsupported payment method" {
    input = {mensalidade_id: 2147483647, valor: 12.50, forma_pagamento: "Dinheiro"}
    expect.to_throw
  }

  test "rejects partial payment" {
    input = {mensalidade_id: 2147483647, valor: 12.00, forma_pagamento: "PIX"}
    expect.to_throw
  }

  test "rejects overpayment" {
    input = {mensalidade_id: 2147483647, valor: 13.00, forma_pagamento: "PIX"}
    expect.to_throw
  }

  test "rejects duplicate payment" {
    input = {mensalidade_id: 2147483647, valor: 12.50, forma_pagamento: "PIX"}
    expect.to_throw
  }

  test "registers full payment" {
    input = {mensalidade_id: 2147483647, valor: 12.50, forma_pagamento: "PIX"}
    expect.to_equal ($response.situacao) {value = "Registrado"}
    expect.to_equal ($response.valor) {value = 12.50}
  }
}
