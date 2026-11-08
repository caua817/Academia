// Corrige contabilmente um pagamento sem apagar o lançamento original.
query "pagamentos/corrigir/{pagamento_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"

  input {
    int pagamento_id
    text tipo_correcao filters=trim
    text motivo filters=trim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.tipo_correcao != "Cancelado" && $input.tipo_correcao != "Estornado") {
      error_type = "inputerror"
      error = "Selecione uma correção válida."
    }

    precondition (($input.motivo|strlen) == 0) {
      error_type = "inputerror"
      error = "Informe o motivo da correção."
    }

    db.transaction {
      stack {
        db.edit pagamento {
          field_name = "id"
          field_value = $input.pagamento_id
          data = {correcao_lock_at: now}
        } as $pagamento_bloqueado

        db.get pagamento {
          field_name = "id"
          field_value = $input.pagamento_id
        } as $pagamento_atual

        precondition ($pagamento_atual == null) {
          error_type = "notfound"
          error = "Pagamento não encontrado."
        }

        precondition ($pagamento_atual.situacao != "Registrado") {
          error_type = "inputerror"
          error = "Somente pagamentos ativos podem ser corrigidos."
        }

        db.edit pagamento {
          field_name = "id"
          field_value = $pagamento_atual.id
          data = {
            situacao       : $input.tipo_correcao
            tipo_correcao  : $input.tipo_correcao
            motivo_correcao: $input.motivo
            corrigido_em   : now
            corrigido_por  : $auth.id
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
    tipo_correcao   : $pagamento.tipo_correcao
    motivo_correcao : $pagamento.motivo_correcao
    corrigido_em    : $pagamento.corrigido_em
    corrigido_por   : $pagamento.corrigido_por
  }
  guid = "P7J40XsdjrfdOl-r8GuuOIfhC94"
}
