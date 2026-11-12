// Lista histórico de check-ins para administradores.
query checkins verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
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
      value = $checkins
        |map:{
          id:$$.id,
          aluno_id:$$.aluno_id,
          aluno_nome:$$.aluno_nome,
          matricula_id:$$.matricula_id,
          data_hora:$$.data_hora,
          registrado_por:$$.registrado_por,
          usuario_nome:$$.usuario_nome
        }
    }
  }

  response = $checkins_visiveis
  guid = "b-p6EsZNVehcMObQ8Q3IdCxwB8E"
}
