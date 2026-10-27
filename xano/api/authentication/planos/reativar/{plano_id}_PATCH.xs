query "planos/reativar/{plano_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"
  description = "Reativa um plano descontinuado."

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
    } as $plano_existente

    precondition ($plano_existente != null) {
      error_type = "notfound"
      error = "Plano não encontrado."
    }

    db.edit "plano" {
      field_name = "id"
      field_value = $input.plano_id
      data = {
        situacao: "Ativo"
      }
    } as $plano
  }

  response = {
    id: $plano.id
    nome: $plano.nome
    situacao: $plano.situacao
  }
  guid = "zf5nCoV2fubBNbYecHTTC1pl0so"
}
