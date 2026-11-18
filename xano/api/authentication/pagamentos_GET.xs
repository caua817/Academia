// Lista lançamentos de pagamento e suas correções para a equipe autorizada.
query pagamentos verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_profile_access" {
      input = {user_id: $auth.id, allow_receptionist: true}
    } as $role_check

    db.query pagamento {
      join = {
        mensalidade: {
          table: "mensalidade"
          where: $db.pagamento.mensalidade_id == $db.mensalidade.id
        }
        matricula: {
          table: "matricula"
          where: $db.mensalidade.matricula_id == $db.matricula.id
        }
        aluno: {
          table: "aluno"
          where: $db.matricula.aluno_id == $db.aluno.id
        }
      }

      eval = {
        aluno_nome: $db.aluno.nome
        competencia: $db.mensalidade.competencia
      }
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $pagamentos

    var $pagamentos_visiveis {
      value = []
    }

    foreach ($pagamentos) {
      each as $pagamento {
        conditional {
          if ($role_check == "admin") {
            var.update $pagamentos_visiveis {
              value = $pagamentos_visiveis
                |append:```
                  {
                    id: $pagamento.id,
                    mensalidade_id: $pagamento.mensalidade_id,
                    aluno_nome: $pagamento.aluno_nome,
                    competencia: $pagamento.competencia,
                    valor: $pagamento.valor,
                    forma_pagamento: $pagamento.forma_pagamento,
                    data_pagamento: $pagamento.data_pagamento,
                    registrado_por: $pagamento.registrado_por,
                    situacao: $pagamento.situacao,
                    tipo_correcao: $pagamento.tipo_correcao,
                    motivo_correcao: $pagamento.motivo_correcao,
                    corrigido_em: $pagamento.corrigido_em,
                    corrigido_por: $pagamento.corrigido_por
                  }
                  ```
            }
          }
          else {
            var.update $pagamentos_visiveis {
              value = $pagamentos_visiveis
                |append:```
                  {
                    id: $pagamento.id,
                    mensalidade_id: $pagamento.mensalidade_id,
                    aluno_nome: $pagamento.aluno_nome,
                    competencia: $pagamento.competencia,
                    valor: $pagamento.valor,
                    forma_pagamento: $pagamento.forma_pagamento,
                    data_pagamento: $pagamento.data_pagamento,
                    situacao: $pagamento.situacao
                  }
                  ```
            }
          }
        }
      }
    }
  }

  response = $pagamentos_visiveis
  guid = "wIz32wpOGfhZWYc3qZHcVF5Nzzc"
}
