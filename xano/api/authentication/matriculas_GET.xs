query "matriculas" verb=GET {
  api_group = "Authentication"
  auth = "user"
  description = "Lista matrículas e condições contratadas para administradores."

  input {
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

    db.query "matricula" {
      join = {
        aluno: {
          table: "aluno"
          type: "inner"
          where: $db.matricula.aluno_id == $db.aluno.id
        }
        plano: {
          table: "plano"
          type: "inner"
          where: $db.matricula.plano_id == $db.plano.id
        }
      }
      eval = {
        aluno_nome: $db.aluno.nome
        plano_nome: $db.plano.nome
      }
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $matriculas

    var $matriculas_visiveis {
      value = []
    }

    foreach ($matriculas) {
      each as $matricula {
        var $matricula_situacao {
          value = "Encerrada"
        }

        conditional {
          if (($matricula.data_inicio|to_timestamp:"America/Sao_Paulo") <= $today_start && ($matricula.data_termino|to_timestamp:"America/Sao_Paulo") >= $today_start) {
            var.update $matricula_situacao {
              value = "Ativa"
            }
          }
        }

        var.update $matriculas_visiveis {
          value = $matriculas_visiveis|append:{
            id: $matricula.id,
            aluno_id: $matricula.aluno_id,
            aluno_nome: $matricula.aluno_nome,
            plano_id: $matricula.plano_id,
            plano_nome: $matricula.plano_nome,
            data_inicio: $matricula.data_inicio,
            data_termino: $matricula.data_termino,
            duracao_contratada_meses: $matricula.duracao_contratada_meses,
            valor_contratado: $matricula.valor_contratado,
            situacao: $matricula_situacao
          }
        }
      }
    }
  }

  response = $matriculas_visiveis
  guid = "LwAaNlx0dSvTwFSp1146aYwLfx8"
}
