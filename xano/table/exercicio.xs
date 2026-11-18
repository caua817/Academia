table exercicio {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text nome filters=trim
    text? grupo_muscular? filters=trim
    text? descricao? filters=trim
    text? equipamento? filters=trim
    enum situacao?=Ativo {
      values = ["Ativo", "Inativo"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "nome", op: "asc"}]}
    {type: "btree", field: [{name: "situacao", op: "asc"}]}
  ]
}
