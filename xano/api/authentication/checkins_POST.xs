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
    } as $checkin
  }

  response = {
    id             : $checkin.id
    aluno_id       : $checkin.aluno_id
    matricula_id   : $checkin.matricula_id
    data_hora      : $checkin.data_hora
    registrado_por : $checkin.registrado_por
  }
}
