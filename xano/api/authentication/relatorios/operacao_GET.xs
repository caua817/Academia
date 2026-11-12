// Retorna somente métricas agregadas, sem identificadores ou dados pessoais.
query "relatorios/operacao" verb=GET {
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

    db.query matricula {
      where = $db.matricula.data_inicio <= $input.data_fim && $db.matricula.data_termino >= $input.data_fim
      return = {type: "count"}
      mock = {
        "returns aggregate totals without data identifiers": 0
      }
    } as $matriculas_ativas

    db.query pagamento {
      where = $db.pagamento.data_pagamento >= $inicio_ts && $db.pagamento.data_pagamento < $fim_exclusivo && $db.pagamento.situacao == "Registrado"
      return = {type: "list"}
      mock = {
        "returns aggregate totals without data identifiers": []
      }
    } as $pagamentos

    var $pagamentos_quantidade {
      value = 0
    }

    var $pagamentos_valor {
      value = 0
    }

    foreach ($pagamentos) {
      each as $pagamento {
        var.update $pagamentos_quantidade {
          value = $pagamentos_quantidade + 1
        }

        var.update $pagamentos_valor {
          value = $pagamentos_valor + $pagamento.valor
        }
      }
    }

    db.query mensalidade {
      where = $db.mensalidade.data_vencimento <= $input.data_fim
      return = {type: "list"}
      mock = {
        "returns aggregate totals without data identifiers": []
      }
    } as $mensalidades_vencidas

    var $mensalidades_atrasadas_quantidade {
      value = 0
    }

    var $mensalidades_atrasadas_valor {
      value = 0
    }

    foreach ($mensalidades_vencidas) {
      each as $mensalidade {
        db.query pagamento {
          where = $db.pagamento.mensalidade_id == $mensalidade.id && $db.pagamento.situacao == "Registrado" && $db.pagamento.data_pagamento < $fim_exclusivo
          return = {type: "exists"}
          mock = {
            "returns aggregate totals without data identifiers": false
          }
        } as $mensalidade_paga

        conditional {
          if (!$mensalidade_paga) {
            var.update $mensalidades_atrasadas_quantidade {
              value = $mensalidades_atrasadas_quantidade + 1
            }

            var.update $mensalidades_atrasadas_valor {
              value = $mensalidades_atrasadas_valor + $mensalidade.valor
            }
          }
        }
      }
    }

    db.query checkin {
      where = $db.checkin.data_hora >= $inicio_ts && $db.checkin.data_hora < $fim_exclusivo
      return = {type: "count"}
      mock = {
        "returns aggregate totals without data identifiers": 0
      }
    } as $checkins_quantidade

    db.query sessao_aula {
      where = $db.sessao_aula.inicio >= $inicio_ts && $db.sessao_aula.inicio < $fim_exclusivo && $db.sessao_aula.situacao == "Agendada"
      return = {type: "list"}
      mock = {
        "returns aggregate totals without data identifiers": []
      }
    } as $sessoes

    var $sessoes_quantidade {
      value = 0
    }

    var $capacidade_total {
      value = 0
    }

    var $reservas_nao_canceladas {
      value = 0
    }

    foreach ($sessoes) {
      each as $sessao {
        var.update $sessoes_quantidade {
          value = $sessoes_quantidade + 1
        }

        var.update $capacidade_total {
          value = $capacidade_total + $sessao.capacidade
        }

        db.query reserva_aula {
          where = $db.reserva_aula.sessao_aula_id == $sessao.id && ($db.reserva_aula.situacao == "Confirmada" || $db.reserva_aula.situacao == "Presente" || $db.reserva_aula.situacao == "Falta")
          return = {type: "count"}
          mock = {
            "returns aggregate totals without data identifiers": 0
          }
        } as $reservas_sessao

        var.update $reservas_nao_canceladas {
          value = $reservas_nao_canceladas + $reservas_sessao
        }
      }
    }

    var $ocupacao_percentual {
      value = 0
    }

    conditional {
      if ($capacidade_total > 0) {
        var.update $ocupacao_percentual {
          value = ($reservas_nao_canceladas / $capacidade_total) * 100
        }
      }
    }
  }

  response = {
    data_inicio: $input.data_inicio
    data_fim: $input.data_fim
    matriculas_ativas: $matriculas_ativas
    pagamentos_quantidade: $pagamentos_quantidade
    pagamentos_valor: $pagamentos_valor
    mensalidades_atrasadas_quantidade: $mensalidades_atrasadas_quantidade
    mensalidades_atrasadas_valor: $mensalidades_atrasadas_valor
    checkins_quantidade: $checkins_quantidade
    sessoes_quantidade: $sessoes_quantidade
    capacidade_total: $capacidade_total
    reservas_nao_canceladas: $reservas_nao_canceladas
    ocupacao_percentual: $ocupacao_percentual
  }
  guid = "eT4mN8vQ2xB6rK1pD9sA3cL7wY5"

  test "rejects reversed date range" {
    input = {data_inicio: "2026-11-30", data_fim: "2026-11-01"}
    expect.to_throw
  }

  test "returns aggregate totals without data identifiers" {
    input = {data_inicio: "2026-11-01", data_fim: "2026-11-30"}
    expect.to_equal ($response.matriculas_ativas) {value = 0}
    expect.to_equal ($response.pagamentos_quantidade) {value = 0}
    expect.to_equal ($response.mensalidades_atrasadas_quantidade) {value = 0}
    expect.to_equal ($response.checkins_quantidade) {value = 0}
    expect.to_equal ($response.ocupacao_percentual) {value = 0}
  }
}
