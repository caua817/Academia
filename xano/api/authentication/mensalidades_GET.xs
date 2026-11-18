// Lista mensalidades com situação calculada no momento da consulta.
query mensalidades verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_profile_access" {
      input = {user_id: $auth.id, allow_receptionist: true}
      mock = {
        "returns a paid monthly status": "admin"
        "returns a pending monthly status": "admin"
        "returns an overdue monthly status": "admin"
      }
    } as $role_check

    var $today_text {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }

    var $today_start {
      value = $today_text|to_timestamp:"America/Sao_Paulo"
    }

    db.query mensalidade {
      join = {
        matricula: {
          table: "matricula"
          where: $db.mensalidade.matricula_id == $db.matricula.id
        }
        pagamento_ativo: {
          table: "pagamento"
          type: "left"
          where: $db.mensalidade.id == $db.pagamento_ativo.mensalidade_id && $db.pagamento_ativo.situacao == "Registrado"
        }
        aluno: {
          table: "aluno"
          where: $db.matricula.aluno_id == $db.aluno.id
        }
      }

      eval = {
        aluno_nome: $db.aluno.nome
        pagamento_ativo_id: $db.pagamento_ativo.id
        pagamento_ativo_forma: $db.pagamento_ativo.forma_pagamento
        pagamento_ativo_data: $db.pagamento_ativo.data_pagamento
      }
      sort = {data_vencimento: "asc"}
      return = {type: "list"}
      mock = {
        "returns a paid monthly status": [
          {
            id: 1
            matricula_id: 2
            aluno_nome: "Aluno"
            competencia: "2026-01"
            data_vencimento: "2000-01-01"
            valor: 100
            pagamento_ativo_id: 3
            pagamento_ativo_forma: "PIX"
            pagamento_ativo_data: "2026-01-10T12:00:00-03:00"
          }
        ]
        "returns a pending monthly status": [
          {
            id: 4
            matricula_id: 2
            aluno_nome: "Aluno"
            competencia: "2999-01"
            data_vencimento: "2999-01-01"
            valor: 100
            pagamento_ativo_id: null
            pagamento_ativo_forma: null
            pagamento_ativo_data: null
          }
        ]
        "returns an overdue monthly status": [
          {
            id: 5
            matricula_id: 2
            aluno_nome: "Aluno"
            competencia: "2000-01"
            data_vencimento: "2000-01-01"
            valor: 100
            pagamento_ativo_id: null
            pagamento_ativo_forma: null
            pagamento_ativo_data: null
          }
        ]
      }
    } as $mensalidades

    var $mensalidades_visiveis {
      value = []
    }

    foreach ($mensalidades) {
      each as $mensalidade {
        var $situacao {
          value = "Pendente"
        }

        var $pagamento_id {
          value = 0
        }

        var $forma_pagamento {
          value = ""
        }

        var $data_pagamento {
          value = ""
        }

        conditional {
          if ($mensalidade.pagamento_ativo_id != null) {
            var.update $situacao {
              value = "Paga"
            }

            var.update $pagamento_id {
              value = $mensalidade.pagamento_ativo_id
            }

            var.update $forma_pagamento {
              value = $mensalidade.pagamento_ativo_forma
            }

            var.update $data_pagamento {
              value = $mensalidade.pagamento_ativo_data
                |format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo"
            }
          }

          elseif (($today_start) > ($mensalidade.data_vencimento|to_timestamp:"America/Sao_Paulo")) {
            var.update $situacao {
              value = "Atrasada"
            }
          }
        }

        var.update $mensalidades_visiveis {
          value = $mensalidades_visiveis
            |append:```
              {
                id: $mensalidade.id,
                matricula_id: $mensalidade.matricula_id,
                aluno_nome: $mensalidade.aluno_nome,
                competencia: $mensalidade.competencia,
                data_vencimento: $mensalidade.data_vencimento,
                valor: $mensalidade.valor,
                situacao: $situacao,
                pagamento_id: $pagamento_id,
                forma_pagamento: $forma_pagamento,
                data_pagamento: $data_pagamento
              }
              ```
        }
      }
    }
  }

  response = $mensalidades_visiveis
  guid = "_gUzf4FuYv6nXxi0blxS_ZwYo3k"

  test "returns a paid monthly status" {
    input = {}
    expect.to_equal ($response) {
      value = [
        {
          id: 1
          matricula_id: 2
          aluno_nome: "Aluno"
          competencia: "2026-01"
          data_vencimento: "2000-01-01"
          valor: 100
          situacao: "Paga"
          pagamento_id: 3
          forma_pagamento: "PIX"
          data_pagamento: "2026-01-10 12:00:00"
        }
      ]
    }
  }

  test "returns a pending monthly status" {
    input = {}
    expect.to_equal ($response) {
      value = [
        {
          id: 4
          matricula_id: 2
          aluno_nome: "Aluno"
          competencia: "2999-01"
          data_vencimento: "2999-01-01"
          valor: 100
          situacao: "Pendente"
          pagamento_id: 0
          forma_pagamento: ""
          data_pagamento: ""
        }
      ]
    }
  }

  test "returns an overdue monthly status" {
    input = {}
    expect.to_equal ($response) {
      value = [
        {
          id: 5
          matricula_id: 2
          aluno_nome: "Aluno"
          competencia: "2000-01"
          data_vencimento: "2000-01-01"
          valor: 100
          situacao: "Atrasada"
          pagamento_id: 0
          forma_pagamento: ""
          data_pagamento: ""
        }
      ]
    }
  }
}
