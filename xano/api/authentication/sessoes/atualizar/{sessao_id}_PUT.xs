query "sessoes/atualizar/{sessao_id}" verb=PUT {
  api_group = "Authentication"
  auth = "user"
  description = "Atualiza uma sessão agendada sem reduzir vagas ocupadas."

  input {
    int sessao_id
    int modalidade_id
    int instrutor_id
    timestamp inicio
    timestamp termino
    int capacidade
    text? local? filters=trim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.termino > $input.inicio && $input.inicio > now) {
      error_type = "inputerror"
      error = "A sessão deve ter início futuro e término posterior ao início."
    }

    precondition ($input.capacidade > 0) {
      error_type = "inputerror"
      error = "A capacidade deve ser maior que zero."
    }

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

        precondition ($sessao_atual.situacao == "Agendada" && $sessao_atual.inicio > now) {
          error_type = "inputerror"
          error = "Somente sessões futuras agendadas podem ser editadas."
        }

        db.get user {
          field_name = "id"
          field_value = $input.instrutor_id
        } as $instrutor_existente

        precondition ($instrutor_existente != null) {
          error_type = "notfound"
          error = "Instrutor não encontrado."
        }

        conditional {
          if ($sessao_atual.instrutor_id <= $input.instrutor_id) {
            db.edit user {
              field_name = "id"
              field_value = $sessao_atual.instrutor_id
              data = {agenda_lock_at: now}
            } as $instrutor_anterior_bloqueado

            conditional {
              if ($sessao_atual.instrutor_id != $input.instrutor_id) {
                db.edit user {
                  field_name = "id"
                  field_value = $input.instrutor_id
                  data = {agenda_lock_at: now}
                } as $instrutor_novo_bloqueado
              }
            }
          }
          else {
            db.edit user {
              field_name = "id"
              field_value = $input.instrutor_id
              data = {agenda_lock_at: now}
            } as $instrutor_novo_bloqueado

            db.edit user {
              field_name = "id"
              field_value = $sessao_atual.instrutor_id
              data = {agenda_lock_at: now}
            } as $instrutor_anterior_bloqueado
          }
        }

        db.get user {
          field_name = "id"
          field_value = $input.instrutor_id
        } as $instrutor

        precondition ($instrutor.role == "instrutor" && $instrutor.situacao == "Ativo") {
          error_type = "inputerror"
          error = "A sessão exige um instrutor ativo."
        }

        db.get modalidade {
          field_name = "id"
          field_value = $input.modalidade_id
        } as $modalidade

        precondition ($modalidade != null && $modalidade.situacao == "Ativo") {
          error_type = "inputerror"
          error = "A sessão exige uma modalidade ativa."
        }

        db.query reserva_aula {
          where = $db.reserva_aula.sessao_aula_id == $input.sessao_id && $db.reserva_aula.situacao == "Confirmada"
          return = {type: "count"}
        } as $reservas_confirmadas

        precondition ($input.capacidade >= $reservas_confirmadas) {
          error_type = "inputerror"
          error = "A capacidade não pode ser menor que as reservas confirmadas."
        }

        db.query sessao_aula {
          where = $db.sessao_aula.instrutor_id == $input.instrutor_id && $db.sessao_aula.id != $input.sessao_id && $db.sessao_aula.situacao == "Agendada" && $db.sessao_aula.inicio < $input.termino && $db.sessao_aula.termino > $input.inicio
          return = {type: "exists"}
        } as $conflito

        precondition (!$conflito) {
          error_type = "inputerror"
          error = "O instrutor já possui sessão agendada nesse horário."
        }

        db.edit sessao_aula {
          field_name = "id"
          field_value = $input.sessao_id
          data = {
            modalidade_id: $input.modalidade_id
            instrutor_id: $input.instrutor_id
            inicio: $input.inicio
            termino: $input.termino
            capacidade: $input.capacidade
            local: $input.local
          }
        } as $sessao
      }
    }
  }

  response = {
    id: $sessao.id
    modalidade_id: $sessao.modalidade_id
    instrutor_id: $sessao.instrutor_id
    inicio: $sessao.inicio
    termino: $sessao.termino
    capacidade: $sessao.capacidade
    local: $sessao.local
    situacao: $sessao.situacao
  }
  guid = "hR3mX7qV1nF9kB4pD2sL6cA8wY5"
}
