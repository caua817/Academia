// Registra check-in para aluno com matrícula vigente.
query checkins verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
    int aluno_id
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    var $today_text {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }

    db.get aluno {
      field_name = "id"
      field_value = $input.aluno_id
      output = ["id", "nome", "situacao"]
      mock = {
        "rejects missing student": null
        "rejects inactive student": {id: 2147483647, nome: "Aluno Inativo", situacao: "Inativo"}
        "rejects no active enrollment": {id: 2147483647, nome: "Aluno Ativo", situacao: "Ativo"}
        "registers checkin": {id: 2147483647, nome: "Aluno Ativo", situacao: "Ativo"}
      }
    } as $aluno

    precondition ($aluno != null) {
      error_type = "notfound"
      error = "Aluno não encontrado."
    }

    precondition ($aluno.situacao == "Ativo") {
      error_type = "inputerror"
      error = "Não é possível registrar check-in para aluno inativo."
    }

    db.query matricula {
      where = $db.matricula.aluno_id == $input.aluno_id && $db.matricula.data_inicio <= $today_text && $db.matricula.data_termino >= $today_text
      sort = {data_termino: "desc"}
      return = {type: "single"}
      mock = {
        "rejects inactive student": null
        "rejects no active enrollment": null
        "registers checkin": {id: 2147483647, aluno_id: 2147483647, data_inicio: "2026-11-01", data_termino: "2026-11-30"}
      }
    } as $matricula

    precondition ($matricula != null) {
      error_type = "inputerror"
      error = "O aluno não possui matrícula vigente."
    }

    db.add checkin {
      data = {
        aluno_id       : $aluno.id
        matricula_id   : $matricula.id
        data_hora      : now
        registrado_por : $auth.id
      }
      mock = {
        "registers checkin": {
          id: 2147483647
          aluno_id: 2147483647
          matricula_id: 2147483647
          data_hora: "2026-11-07T12:00:00Z"
          registrado_por: 1
        }
      }
    } as $checkin
  }

  response = {
    id             : $checkin.id
    aluno_id       : $checkin.aluno_id
    matricula_id   : $checkin.matricula_id
    data_hora      : $checkin.data_hora
    registrado_por : $checkin.registrado_por
  }
  guid = "cU4TgvHI8o2J8A0SwwXtousecD0"

  test "rejects missing student" {
    input = {aluno_id: 0}
    expect.to_throw
  }

  test "rejects inactive student" {
    input = {aluno_id: 2147483647}
    expect.to_throw
  }

  test "rejects no active enrollment" {
    input = {aluno_id: 2147483647}
    expect.to_throw
  }

  test "registers checkin" {
    input = {aluno_id: 2147483647}
    expect.to_equal ($response.aluno_id) {value = 2147483647}
    expect.to_equal ($response.matricula_id) {value = 2147483647}
  }
}
