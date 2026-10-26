table "plano" {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text nome filters=trim
    text? descricao filters=trim
    int duracao_meses
    decimal valor
    enum situacao?="Ativo" {
      values = ["Ativo", "Descontinuado"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "nome", op: "asc"}]}
    {type: "btree", field: [{name: "situacao", op: "asc"}]}
  ]
  guid = "sHFmtC7Pbhw2aVQ9P4yDX-zR7_M"
}
