// Lista mensalidades com situação calculada no momento da consulta.
query mensalidades verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
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
        aluno: {
          table: "aluno"
          where: $db.matricula.aluno_id == $db.aluno.id
        }
      }

      eval = {aluno_nome: $db.aluno.nome}
      sort = {data_vencimento: "asc"}
      return = {type: "list"}
    } as $mensalidades

    var $mensalidades_visiveis {
      value = []
    }

    foreach ($mensalidades) {
      each as $mensalidade {
        db.query pagamento {
          where = $db.pagamento.mensalidade_id == $mensalidade.id && $db.pagamento.situacao == "Registrado"
          return = {type: "single"}
        } as $pagamento_ativo

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
          if ($pagamento_ativo != null) {
            var.update $situacao {
              value = "Paga"
            }

            var.update $pagamento_id {
              value = $pagamento_ativo.id
            }

            var.update $forma_pagamento {
              value = $pagamento_ativo.forma_pagamento
            }

            var.update $data_pagamento {
              value = $pagamento_ativo.data_pagamento
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
}
