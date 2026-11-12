// Cria sessão e valida elegibilidade, capacidade e agenda do instrutor.
query sessoes verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
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

    precondition ($input.termino > $input.inicio) {
      error_type = "inputerror"
      error = "O término deve ser posterior ao início."
    }

    precondition ($input.inicio > now) {
      error_type = "inputerror"
      error = "A sessão deve começar no futuro."
    }

    precondition ($input.capacidade > 0) {
      error_type = "inputerror"
      error = "A capacidade deve ser maior que zero."
    }

    db.transaction {
      isolation = "serializable"

      stack {
        db.get user {
          field_name = "id"
          field_value = $input.instrutor_id
        } as $instrutor_existente

        precondition ($instrutor_existente != null) {
          error_type = "notfound"
          error = "Instrutor não encontrado."
        }

        db.edit user {
          field_name = "id"
          field_value = $input.instrutor_id
          data = {agenda_lock_at: now}
        } as $instrutor_bloqueado

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

        db.query sessao_aula {
          where = $db.sessao_aula.instrutor_id == $input.instrutor_id && $db.sessao_aula.situacao == "Agendada" && $db.sessao_aula.inicio < $input.termino && $db.sessao_aula.termino > $input.inicio
          return = {type: "exists"}
        } as $conflito

        precondition (!$conflito) {
          error_type = "inputerror"
          error = "O instrutor já possui sessão agendada nesse horário."
        }

        db.add sessao_aula {
          data = {
            modalidade_id: $input.modalidade_id
            instrutor_id: $input.instrutor_id
            inicio: $input.inicio
            termino: $input.termino
            capacidade: $input.capacidade
            local: $input.local
            situacao: "Agendada"
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
  guid = "fJ6mQ1xV8sD3nB5kR2pL7cA4wY9"

  test "rejects invalid duration and capacity" {
    input = {modalidade_id: 1, instrutor_id: 1, inicio: "2027-01-01T10:00:00Z", termino: "2027-01-01T09:00:00Z", capacidade: 0, local: null}
    expect.to_throw
  }
}
