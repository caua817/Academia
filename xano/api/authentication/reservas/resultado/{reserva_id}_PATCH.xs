query "reservas/resultado/{reserva_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"
  description = "Registra presença ou falta após o término da sessão."

  input {
    int reserva_id
    enum resultado {
      values = ["Presente", "Falta"]
    }
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.transaction {
      isolation = "serializable"

      stack {
        db.get reserva_aula {
          field_name = "id"
          field_value = $input.reserva_id
        } as $reserva_existente

        precondition ($reserva_existente != null) {
          error_type = "notfound"
          error = "Reserva não encontrada."
        }

        db.edit sessao_aula {
          field_name = "id"
          field_value = $reserva_existente.sessao_aula_id
          data = {reserva_lock_at: now}
        } as $sessao_bloqueada

        db.get sessao_aula {
          field_name = "id"
          field_value = $reserva_existente.sessao_aula_id
        } as $sessao

        precondition ($sessao != null && $sessao.situacao == "Agendada" && now >= $sessao.termino) {
          error_type = "inputerror"
          error = "A presença ou falta só pode ser registrada após a sessão."
        }

        db.get reserva_aula {
          field_name = "id"
          field_value = $input.reserva_id
        } as $reserva

        precondition ($reserva.situacao == "Confirmada") {
          error_type = "inputerror"
          error = "Somente reservas confirmadas podem receber um resultado."
        }

        db.edit reserva_aula {
          field_name = "id"
          field_value = $input.reserva_id
          data = {
            situacao: $input.resultado
            chave_ativa: null
          }
        } as $reserva_atualizada
      }
    }
  }

  response = {
    id: $reserva_atualizada.id
    sessao_aula_id: $reserva_atualizada.sessao_aula_id
    aluno_id: $reserva_atualizada.aluno_id
    situacao: $reserva_atualizada.situacao
  }
  guid = "dN2xS8vQ4mB1rK6pL9aF3cH7wY5"
}
