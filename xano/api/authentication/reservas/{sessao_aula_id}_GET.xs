// Lista reservas por sessão sem expor documentos ou contatos dos alunos.
query "reservas/{sessao_aula_id}" verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
    int sessao_aula_id
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.get sessao_aula {
      field_name = "id"
      field_value = $input.sessao_aula_id
    } as $sessao

    precondition ($sessao != null) {
      error_type = "notfound"
      error = "Sessão não encontrada."
    }

    db.query reserva_aula {
      where = $db.reserva_aula.sessao_aula_id == $input.sessao_aula_id
      join = {
        aluno: {
          table: "aluno"
          where: $db.reserva_aula.aluno_id == $db.aluno.id
        }
      }
      eval = {aluno_nome: $db.aluno.nome}
      sort = {reservado_em: "asc"}
      return = {type: "list"}
    } as $reservas

    db.query reserva_aula {
      where = $db.reserva_aula.sessao_aula_id == $input.sessao_aula_id && ($db.reserva_aula.situacao == "Confirmada" || $db.reserva_aula.situacao == "Presente" || $db.reserva_aula.situacao == "Falta")
      return = {type: "count"}
    } as $ocupacao

    var $reservas_visiveis {
      value = $reservas|map:{id:$$.id,sessao_aula_id:$$.sessao_aula_id,aluno_id:$$.aluno_id,aluno_nome:$$.aluno_nome,situacao:$$.situacao,reservado_em:$$.reservado_em}
    }
  }

  response = {
    sessao_aula_id: $sessao.id
    capacidade: $sessao.capacidade
    ocupacao: $ocupacao
    vagas_disponiveis: $sessao.capacidade - $ocupacao
    reservas: $reservas_visiveis
  }
  guid = "bH4nK8mQ2vR6xF1pD9sA3cL7wY5"
}
