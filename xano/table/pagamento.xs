table pagamento {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int mensalidade_id {
      table = "mensalidade"
    }
    decimal valor
    enum forma_pagamento {
      values = ["PIX", "Cartão"]
    }
    timestamp data_pagamento?=now
    int registrado_por {
      table = "user"
    }
    enum situacao?=Registrado {
      values = ["Registrado", "Cancelado", "Estornado"]
    }
    enum tipo_correcao? {
      values = ["Cancelado", "Estornado"]
    }
    text? motivo_correcao filters=trim
    timestamp? corrigido_em?
    int? corrigido_por {
      table = "user"
    }
    timestamp? correcao_lock_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "mensalidade_id"}, {name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "registrado_por"}]}
    {type: "btree", field: [{name: "situacao"}]}
  ]
  guid = "EVadIVgNRkx2msa9Sw9YRXJe1AE"
}
