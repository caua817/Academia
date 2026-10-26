query "planos/descontinuar/{plano_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"
  description = "Descontinua um plano sem excluir o registro."

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
        situacao: "Descontinuado"
      }
    } as $plano
  }

  response = {
    id: $plano.id
    nome: $plano.nome
    situacao: $plano.situacao
  }
  guid = "1zIrLvqd7rQZWqBJ9OeFa6d924Y"
}
