// Lista o histórico de check-ins com campos mínimos por perfil.
query checkins verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_profile_access" {
      input = {
        user_id: $auth.id
        allow_receptionist: true
        allow_instructor: true
      }
    } as $role_check

    db.query checkin {
      join = {
        aluno: {
          table: "aluno"
          where: $db.checkin.aluno_id == $db.aluno.id
        }
        usuario: {
          table: "user"
          where: $db.checkin.registrado_por == $db.usuario.id
        }
      }

      eval = {
        aluno_nome: $db.aluno.nome
        usuario_nome: $db.usuario.name
      }
      sort = {data_hora: "desc"}
      return = {type: "list"}
    } as $checkins

    var $checkins_visiveis {
      value = []
    }

    foreach ($checkins) {
      each as $checkin {
        conditional {
          if ($role_check == "instrutor") {
            var.update $checkins_visiveis {
              value = $checkins_visiveis
                |append:```
                  {
                    id: $checkin.id,
                    aluno_id: $checkin.aluno_id,
                    aluno_nome: $checkin.aluno_nome,
                    data_hora: $checkin.data_hora
                  }
                  ```
            }
          }
          else {
            var.update $checkins_visiveis {
              value = $checkins_visiveis
                |append:```
                  {
                    id: $checkin.id,
                    aluno_id: $checkin.aluno_id,
                    aluno_nome: $checkin.aluno_nome,
                    matricula_id: $checkin.matricula_id,
                    data_hora: $checkin.data_hora,
                    registrado_por: $checkin.registrado_por,
                    usuario_nome: $checkin.usuario_nome
                  }
                  ```
            }
          }
        }
      }
    }
  }

  response = $checkins_visiveis
  guid = "b-p6EsZNVehcMObQ8Q3IdCxwB8E"
}
