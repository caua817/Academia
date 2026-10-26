query "matriculas" verb=POST {
  api_group = "Authentication"
  auth = "user"
  description = "Cria uma matrícula com as condições vigentes do plano."

  input {
    int aluno_id {
      table = "aluno"
    }
    int plano_id {
      table = "plano"
    }
    date data_inicio
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    var $today_text {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }

    var $today_start {
      value = $today_text|to_timestamp:"America/Sao_Paulo"
    }

    var $start_timestamp {
      value = $input.data_inicio|to_timestamp:"America/Sao_Paulo"
    }

    precondition ($start_timestamp <= $today_start) {
      error_type = "inputerror"
      error = "A data de início não pode ser futura."
    }

    db.transaction {
      stack {
        db.get "aluno" {
          field_name = "id"
          field_value = $input.aluno_id
        } as $aluno_existente

        precondition ($aluno_existente != null) {
          error_type = "notfound"
          error = "Aluno não encontrado."
        }

        db.edit "aluno" {
          field_name = "id"
          field_value = $input.aluno_id
          data = {
            matricula_lock_at: now
          }
        } as $aluno_bloqueado

        db.get "aluno" {
          field_name = "id"
          field_value = $input.aluno_id
        } as $aluno_atual

        precondition ($aluno_atual.situacao == "Ativo") {
          error_type = "inputerror"
          error = "Não é possível matricular um aluno inativo."
        }

        db.get "plano" {
          field_name = "id"
          field_value = $input.plano_id
        } as $plano

        precondition ($plano != null) {
          error_type = "notfound"
          error = "Plano não encontrado."
        }

        precondition ($plano.situacao == "Ativo") {
          error_type = "inputerror"
          error = "Não é possível usar um plano descontinuado."
        }

        var $start_day {
          value = $start_timestamp|format_timestamp:"d":"America/Sao_Paulo"|to_int
        }

        var $start_month {
          value = $start_timestamp|transform_timestamp:"first day of this month":"America/Sao_Paulo"
        }

        var $month_shift {
          value = $plano.duracao_meses|to_text|concat:" months"
        }

        var $target_month_start {
          value = $start_month|transform_timestamp:$month_shift:"America/Sao_Paulo"
        }

        var $target_month_last_day {
          value = $target_month_start|transform_timestamp:"last day of this month":"America/Sao_Paulo"|format_timestamp:"d":"America/Sao_Paulo"|to_int
        }

        var $final_day {
          value = $start_day
        }

        conditional {
          if ($start_day > $target_month_last_day) {
            var.update $final_day {
              value = $target_month_last_day
            }
          }
        }

        var $day_offset {
          value = $final_day - 1
        }

        var $day_shift {
          value = $day_offset|to_text|concat:" days"
        }

        var $data_termino {
          value = $target_month_start|transform_timestamp:$day_shift:"America/Sao_Paulo"|format_timestamp:"Y-m-d":"America/Sao_Paulo"
        }

        db.query "matricula" {
          where = $db.matricula.aluno_id == $input.aluno_id && $db.matricula.data_inicio <= $data_termino && $db.matricula.data_termino >= $input.data_inicio
          return = {type: "exists"}
        } as $sobreposicao

        precondition (!$sobreposicao) {
          error_type = "inputerror"
          error = "O período da matrícula se sobrepõe a um período já cadastrado para este aluno."
        }

        db.add "matricula" {
          data = {
            aluno_id: $input.aluno_id
            plano_id: $input.plano_id
            data_inicio: $input.data_inicio
            data_termino: $data_termino
            duracao_contratada_meses: $plano.duracao_meses
            valor_contratado: $plano.valor
          }
        } as $matricula
      }
    }
  }

  response = {
    id: $matricula.id
    aluno_id: $matricula.aluno_id
    plano_id: $matricula.plano_id
    data_inicio: $matricula.data_inicio
    data_termino: $matricula.data_termino
    duracao_contratada_meses: $matricula.duracao_contratada_meses
    valor_contratado: $matricula.valor_contratado
  }
  guid = "VnYLn7eszHGKF6bXEbL_sPXj6S0"
}
