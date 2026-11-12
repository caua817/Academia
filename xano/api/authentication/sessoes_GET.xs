// Lista sessões em um intervalo e calcula a ocupação atual.
query sessoes verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
    date data_inicio
    date data_fim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.data_inicio <= $input.data_fim) {
      error_type = "inputerror"
      error = "A data inicial deve ser anterior ou igual à data final."
    }

    var $inicio_ts {
      value = $input.data_inicio|to_timestamp:"America/Sao_Paulo"
    }

    var $fim_exclusivo {
      value = $input.data_fim|to_timestamp:"America/Sao_Paulo"|transform_timestamp:"1 day":"America/Sao_Paulo"
    }

    db.query sessao_aula {
      where = $db.sessao_aula.inicio >= $inicio_ts && $db.sessao_aula.inicio < $fim_exclusivo
      join = {
        modalidade: {
          table: "modalidade"
          where: $db.sessao_aula.modalidade_id == $db.modalidade.id
        }
        instrutor: {
          table: "user"
          where: $db.sessao_aula.instrutor_id == $db.instrutor.id
        }
      }
      eval = {
        modalidade_nome: $db.modalidade.nome
        instrutor_nome: $db.instrutor.name
      }
      sort = {inicio: "asc"}
      return = {type: "list"}
    } as $sessoes

    var $sessoes_visiveis {
      value = []
    }

    foreach ($sessoes) {
      each as $sessao {
        db.query reserva_aula {
          where = $db.reserva_aula.sessao_aula_id == $sessao.id && ($db.reserva_aula.situacao == "Confirmada" || $db.reserva_aula.situacao == "Presente" || $db.reserva_aula.situacao == "Falta")
          return = {type: "count"}
        } as $ocupacao

        var $percentual_ocupacao {
          value = 0
        }

        conditional {
          if ($sessao.capacidade > 0) {
            var.update $percentual_ocupacao {
              value = ($ocupacao / $sessao.capacidade) * 100
            }
          }
        }

        var.update $sessoes_visiveis {
          value = $sessoes_visiveis|append:```
            {
              id: $sessao.id,
              modalidade_id: $sessao.modalidade_id,
              modalidade_nome: $sessao.modalidade_nome,
              instrutor_id: $sessao.instrutor_id,
              instrutor_nome: $sessao.instrutor_nome,
              inicio: $sessao.inicio,
              termino: $sessao.termino,
              capacidade: $sessao.capacidade,
              ocupacao: $ocupacao,
              percentual_ocupacao: $percentual_ocupacao,
              local: $sessao.local,
              situacao: $sessao.situacao
            }
            ```
        }
      }
    }
  }

  response = $sessoes_visiveis
  guid = "yA8kP4cV2mN6rT1qB9dF5sH3wX7"
}
