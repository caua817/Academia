table ficha_treino {
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
    text objetivo filters=trim
    date data_inicio
    date data_fim
    enum situacao?=Vigente {
      values = ["Vigente", "Arquivada"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "aluno_id"}, {name: "data_inicio", op: "desc"}]}
    {type: "btree", field: [{name: "instrutor_id"}, {name: "situacao"}]}
  ]
}
