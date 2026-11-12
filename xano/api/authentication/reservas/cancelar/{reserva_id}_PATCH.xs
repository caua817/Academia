query "reservas/cancelar/{reserva_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"
  description = "Cancela reserva antes do início da sessão e libera a vaga."

  input {
    int reserva_id
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

        precondition ($sessao != null && $sessao.situacao == "Agendada" && now < $sessao.inicio) {
          error_type = "inputerror"
          error = "A reserva só pode ser cancelada antes do início de uma sessão agendada."
        }

        db.get reserva_aula {
          field_name = "id"
          field_value = $input.reserva_id
        } as $reserva

        precondition ($reserva.situacao == "Confirmada") {
          error_type = "inputerror"
          error = "Somente reservas confirmadas podem ser canceladas."
        }

        db.edit reserva_aula {
          field_name = "id"
          field_value = $input.reserva_id
          data = {
            situacao: "Cancelada"
            chave_ativa: null
          }
        } as $reserva_cancelada
      }
    }
  }

  response = {
    id: $reserva_cancelada.id
    sessao_aula_id: $reserva_cancelada.sessao_aula_id
    aluno_id: $reserva_cancelada.aluno_id
    situacao: $reserva_cancelada.situacao
  }
  guid = "cM1vR7xQ3nB9kD5fL2sA6pH8wY4"
}
