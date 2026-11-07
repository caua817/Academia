table mensalidade {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int matricula_id {
      table = "matricula"
    }
    date competencia
    date data_vencimento
    decimal valor
    timestamp? pagamento_lock_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type: "btree|unique"
      field: [{name: "matricula_id"}, {name: "competencia"}]
    }
    {type: "btree", field: [{name: "data_vencimento", op: "asc"}]}
  ]
  guid = "zCGX41CDf6iat4v_0pocdGd6xFo"
}
