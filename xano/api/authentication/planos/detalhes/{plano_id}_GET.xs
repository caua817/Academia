query "planos/detalhes/{plano_id}" verb=GET {
  api_group = "Authentication"
  auth = "user"
  description = "Consulta os dados de um plano para administradores."

  input {
    int plano_id {
      table = "plano"
    }
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    db.get "plano" {
      field_name = "id"
      field_value = $input.plano_id
    } as $plano

    precondition ($plano != null) {
      error_type = "notfound"
      error = "Plano não encontrado."
    }
  }

  response = {
    id: $plano.id
    nome: $plano.nome
    descricao: $plano.descricao
    duracao_meses: $plano.duracao_meses
    valor: $plano.valor
    situacao: $plano.situacao
    created_at: $plano.created_at
  }
  guid = "VRAy-m7wnT3fbVcGK7DEn9i9m6A"
}
