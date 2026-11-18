table medida_avaliacao {
  auth = false

  schema {
    int id
    int avaliacao_fisica_id {
      table = "avaliacao_fisica"
    }
    text nome filters=trim {
      sensitive = true
    }
    decimal valor {
      sensitive = true
    }
    enum unidade?=cm {
      values = ["cm"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "avaliacao_fisica_id"}]}
  ]
}
