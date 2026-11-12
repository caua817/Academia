query "sessoes/cancelar/{sessao_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"
  description = "Cancela uma sessão e suas reservas confirmadas sem excluir histórico."

  input {
    int sessao_id
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.transaction {
      stack {
        db.get sessao_aula {
          field_name = "id"
          field_value = $input.sessao_id
        } as $sessao_existente

        precondition ($sessao_existente != null) {
          error_type = "notfound"
          error = "Sessão não encontrada."
        }

        db.edit sessao_aula {
          field_name = "id"
          field_value = $input.sessao_id
          data = {reserva_lock_at: now}
        } as $sessao_bloqueada

        db.get sessao_aula {
          field_name = "id"
          field_value = $input.sessao_id
        } as $sessao_atual

        precondition ($sessao_atual.situacao == "Agendada") {
          error_type = "inputerror"
          error = "A sessão já está cancelada."
        }

        db.edit sessao_aula {
          field_name = "id"
          field_value = $input.sessao_id
          data = {situacao: "Cancelada"}
        } as $sessao

        db.query reserva_aula {
          where = $db.reserva_aula.sessao_aula_id == $input.sessao_id && $db.reserva_aula.situacao == "Confirmada"
          return = {type: "list"}
        } as $reservas_confirmadas

        foreach ($reservas_confirmadas) {
          each as $reserva {
            db.edit reserva_aula {
              field_name = "id"
              field_value = $reserva.id
              data = {
                situacao: "Cancelada"
                chave_ativa: null
              }
            } as $reserva_cancelada
          }
        }
      }
    }
  }

  response = {
    id: $sessao.id
    situacao: $sessao.situacao
  }
  guid = "vC5nR1xB7mQ3pD9kL2sF6aH8wY4"
}
