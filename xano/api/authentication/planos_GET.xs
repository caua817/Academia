// Lista todos os planos para administradores e os ativos para a recepção.
query planos verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_profile_access" {
      input = {user_id: $auth.id, allow_receptionist: true}
    } as $role_check
  
    db.query plano {
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $planos
  
    var $planos_visiveis {
      value = []
    }

    foreach ($planos) {
      each as $plano {
        conditional {
          if ($role_check == "admin" || $plano.situacao == "Ativo") {
            var.update $planos_visiveis {
              value = $planos_visiveis
                |append:```
                  {
                    id: $plano.id,
                    nome: $plano.nome,
                    descricao: $plano.descricao,
                    duracao_meses: $plano.duracao_meses,
                    valor: $plano.valor,
                    situacao: $plano.situacao,
                    created_at: $plano.created_at
                  }
                  ```
            }
          }
        }
      }
    }
  }

  response = $planos_visiveis
  guid = "cKEUgDawJSDtfmz-oChI-8jaQhQ"
}