query "planos/atualizar/{plano_id}" verb=PUT {
  api_group = "Authentication"
  auth = "user"
  description = "Atualiza os dados comerciais de um plano."

  input {
    int plano_id {
      table = "plano"
    }
    text nome filters=trim
    text? descricao filters=trim
    int duracao_meses
    decimal valor
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {
        user_id: $auth.id
        required_role: "admin"
      }
    } as $role_check

    precondition (($input.nome|strlen) > 0) {
      error_type = "inputerror"
      error = "O nome do plano é obrigatório."
    }

    precondition ($input.duracao_meses > 0) {
      error_type = "inputerror"
      error = "A duração do plano deve ser maior que zero."
    }

    precondition ($input.valor > 0) {
      error_type = "inputerror"
      error = "O valor do plano deve ser maior que zero."
    }

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
        nome: $input.nome
        descricao: $input.descricao
        duracao_meses: $input.duracao_meses
        valor: $input.valor
      }
    } as $plano
  }

  response = {
    id: $plano.id
    nome: $plano.nome
    descricao: $plano.descricao
    duracao_meses: $plano.duracao_meses
    valor: $plano.valor
    situacao: $plano.situacao
  }
  guid = "_7MnNQev9GKN-xBZMsJb8BLKUVo"
}
