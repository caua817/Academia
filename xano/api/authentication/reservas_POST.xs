// Reserva vaga elegível sob transação e lock da sessão para serializar capacidade.
query reservas verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
    int sessao_aula_id
    int aluno_id
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    var $today_text {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }

    db.transaction {
      stack {
        db.get sessao_aula {
          field_name = "id"
          field_value = $input.sessao_aula_id
          mock = {
            "rejects unavailable session": {id: 2147483647, inicio: "2027-01-01T10:00:00Z", capacidade: 1, situacao: "Cancelada"}
            "rejects ineligible student": {id: 2147483647, inicio: "2027-01-01T10:00:00Z", capacidade: 1, situacao: "Agendada"}
            "rejects full session": {id: 2147483647, inicio: "2099-01-01T10:00:00Z", capacidade: 1, situacao: "Agendada"}
            "confirms reservation": {id: 2147483647, inicio: "2099-01-01T10:00:00Z", capacidade: 1, situacao: "Agendada"}
          }
        } as $sessao_existente

        precondition ($sessao_existente != null) {
          error_type = "notfound"
          error = "Sessão não encontrada."
        }

        db.edit sessao_aula {
          field_name = "id"
          field_value = $input.sessao_aula_id
          data = {reserva_lock_at: now}
          mock = {
            "rejects unavailable session": {id: 2147483647}
            "rejects ineligible student": {id: 2147483647}
            "confirms reservation": {id: 2147483647}
          }
        } as $sessao_bloqueada

        db.get sessao_aula {
          field_name = "id"
          field_value = $input.sessao_aula_id
          mock = {
            "rejects unavailable session": {id: 2147483647, inicio: "2027-01-01T10:00:00Z", capacidade: 1, situacao: "Cancelada"}
            "rejects ineligible student": {id: 2147483647, inicio: "2027-01-01T10:00:00Z", capacidade: 1, situacao: "Agendada"}
            "rejects full session": {id: 2147483647, inicio: "2099-01-01T10:00:00Z", capacidade: 1, situacao: "Agendada"}
            "confirms reservation": {id: 2147483647, inicio: "2099-01-01T10:00:00Z", capacidade: 1, situacao: "Agendada"}
          }
        } as $sessao

        precondition ($sessao.situacao == "Agendada" && $sessao.inicio > now) {
          error_type = "inputerror"
          error = "A sessão não está disponível para reservas."
        }

        db.get aluno {
          field_name = "id"
          field_value = $input.aluno_id
          mock = {
            "rejects ineligible student": {id: 2147483647, situacao: "Ativo"}
            "rejects full session": {id: 2147483647, situacao: "Ativo"}
            "confirms reservation": {id: 2147483647, situacao: "Ativo"}
          }
        } as $aluno

        precondition ($aluno != null && $aluno.situacao == "Ativo") {
          error_type = "inputerror"
          error = "A reserva exige um aluno ativo."
        }

        db.query matricula {
          where = $db.matricula.aluno_id == $input.aluno_id && $db.matricula.data_inicio <= $today_text && $db.matricula.data_termino >= $today_text
          return = {type: "exists"}
          mock = {
            "rejects ineligible student": false
            "rejects full session": true
            "confirms reservation": true
          }
        } as $matricula_vigente

        precondition ($matricula_vigente) {
          error_type = "inputerror"
          error = "O aluno não possui matrícula vigente."
        }

        db.query reserva_aula {
          where = $db.reserva_aula.sessao_aula_id == $input.sessao_aula_id && $db.reserva_aula.aluno_id == $input.aluno_id && $db.reserva_aula.situacao == "Confirmada"
          return = {type: "exists"}
          mock = {
            "rejects full session": false
            "confirms reservation": false
          }
        } as $reserva_duplicada

        precondition (!$reserva_duplicada) {
          error_type = "inputerror"
          error = "O aluno já possui uma reserva confirmada para esta sessão."
        }

        db.query reserva_aula {
          where = $db.reserva_aula.sessao_aula_id == $input.sessao_aula_id && $db.reserva_aula.situacao == "Confirmada"
          return = {type: "count"}
          mock = {
            "rejects full session": 1
            "rejects unavailable session": 1
            "confirms reservation": 0
          }
        } as $ocupacao

        precondition ($ocupacao < $sessao.capacidade) {
          error_type = "inputerror"
          error = "A sessão não possui vagas disponíveis."
        }

        var $chave_ativa {
          value = ($input.sessao_aula_id|to_text) ~ ":" ~ ($input.aluno_id|to_text)
        }

        db.add reserva_aula {
          data = {
            sessao_aula_id: $input.sessao_aula_id
            aluno_id: $input.aluno_id
            situacao: "Confirmada"
            chave_ativa: $chave_ativa
          }
          mock = {
            "confirms reservation": {
              id: 2147483647
              sessao_aula_id: 2147483647
              aluno_id: 2147483647
              situacao: "Confirmada"
              reservado_em: "2026-11-07T12:00:00Z"
              chave_ativa: "2147483647:2147483647"
            }
          }
        } as $reserva
      }
    }
  }

  response = {
    id: $reserva.id
    sessao_aula_id: $reserva.sessao_aula_id
    aluno_id: $reserva.aluno_id
    situacao: $reserva.situacao
    reservado_em: $reserva.reservado_em
  }
  guid = "pK7mV3xQ9nB2rD5fL1sA6cH8wY4"

  test "rejects unavailable session" {
    input = {sessao_aula_id: 2147483647, aluno_id: 1}
    expect.to_throw
  }

  test "confirms eligible reservation" {
    input = {sessao_aula_id: 2147483647, aluno_id: 2147483647}
    expect.to_equal ($response.situacao) {value = "Confirmada"}
  }

  test "rejects full session" {
    input = {sessao_aula_id: 2147483647, aluno_id: 2147483647}
    expect.to_throw
  }
}
