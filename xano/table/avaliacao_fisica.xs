table avaliacao_fisica {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int aluno_id {
      table = "aluno"
    }
    int instrutor_id {
      table = "user"
    }
    date data_avaliacao
    decimal peso_kg {
      sensitive = true
    }
    decimal altura_cm {
      sensitive = true
    }
    text? observacoes? filters=trim {
      sensitive = true
    }
    int? avaliacao_original_id? {
      table = "avaliacao_fisica"
    }
    text? motivo_correcao? filters=trim {
      sensitive = true
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "aluno_id"}, {name: "data_avaliacao", op: "asc"}]}
    {type: "btree", field: [{name: "instrutor_id"}]}
    {type: "btree", field: [{name: "avaliacao_original_id"}]}
  ]
}
