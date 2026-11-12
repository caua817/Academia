query "modalidades/atualizar/{modalidade_id}" verb=PUT {
  api_group = "Authentication"
  auth = "user"
  description = "Atualiza uma modalidade sem alterar sessões existentes."

  input {
    int modalidade_id
    text nome? filters=trim
    text? descricao? filters=trim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.nome != null && ($input.nome|strlen) > 0) {
      error_type = "inputerror"
      error = "O nome da modalidade é obrigatório."
    }

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
      data = {
        nome: $input.nome
        descricao: $input.descricao
      }
    } as $modalidade
  }

  response = {
    id: $modalidade.id
    nome: $modalidade.nome
    descricao: $modalidade.descricao
    situacao: $modalidade.situacao
  }
  guid = "mF1w37sA6d0f9v2n8p4q7r5t1cB"
}
