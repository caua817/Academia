table modalidade {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text nome filters=trim
    text? descricao? filters=trim
    enum situacao?=Ativo {
      values = ["Ativo", "Inativo"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "nome", op: "asc"}]}
    {type: "btree", field: [{name: "situacao", op: "asc"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]
}
