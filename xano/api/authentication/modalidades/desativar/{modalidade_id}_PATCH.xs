query "modalidades/desativar/{modalidade_id}" verb=PATCH {
  api_group = "Authentication"
  auth = "user"
  description = "Desativa uma modalidade sem excluir o registro."

  input {
    int modalidade_id
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.get modalidade {
      field_name = "id"
      field_value = $input.modalidade_id
    } as $modalidade_existente

    precondition ($modalidade_existente != null) {
      error_type = "notfound"
      error = "Modalidade não encontrada."
    }

    db.edit modalidade {
      field_name = "id"
      field_value = $input.modalidade_id
      data = {situacao: "Inativo"}
    } as $modalidade
  }

  response = {
    id: $modalidade.id
    nome: $modalidade.nome
    situacao: $modalidade.situacao
  }
  guid = "gR9k3v2b8aQ1nM6x7cP4tY0d5sE"
}
