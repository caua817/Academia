query "matriculas/detalhes/{matricula_id}" verb=GET {
  api_group = "Authentication"
  auth = "user"
  description = "Consulta uma matrícula e suas condições contratadas."

  input {
    int matricula_id {
      table = "matricula"
    }
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    db.get "matricula" {
      field_name = "id"
      field_value = $input.matricula_id
    } as $matricula

    precondition ($matricula != null) {
      error_type = "notfound"
      error = "Matrícula não encontrada."
    }

    db.get "aluno" {
      field_name = "id"
      field_value = $matricula.aluno_id
    } as $aluno

    db.get "plano" {
      field_name = "id"
      field_value = $matricula.plano_id
    } as $plano

    var $today_text {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }

    var $today_start {
      value = $today_text|to_timestamp:"America/Sao_Paulo"
    }

    var $situacao {
      value = "Encerrada"
    }

    conditional {
      if (($matricula.data_inicio|to_timestamp:"America/Sao_Paulo") <= $today_start && ($matricula.data_termino|to_timestamp:"America/Sao_Paulo") >= $today_start) {
        var.update $situacao {
          value = "Ativa"
        }
      }
    }
  }

  response = {
    id: $matricula.id
    aluno_id: $matricula.aluno_id
    aluno_nome: $aluno.nome
    plano_id: $matricula.plano_id
    plano_nome: $plano.nome
    data_inicio: $matricula.data_inicio
    data_termino: $matricula.data_termino
    duracao_contratada_meses: $matricula.duracao_contratada_meses
    valor_contratado: $matricula.valor_contratado
    situacao: $situacao
    created_at: $matricula.created_at
  }
  guid = "GjV7OOsHAu2UrfERn4QOpvR2T-8"
}
