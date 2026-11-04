table matricula {
  auth = false

  schema {
    int id
    timestamp created_at?=now
  
    // Aluno vinculado à matrícula.
    int aluno_id {
      table = "aluno"
    }
  
    // Plano contratado na matrícula.
    int plano_id {
      table = "plano"
    }
  
    date data_inicio
    date data_termino
    int duracao_contratada_meses
    decimal valor_contratado
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree"
      field: [{name: "aluno_id"}, {name: "data_inicio"}]
    }
    {type: "btree", field: [{name: "plano_id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "qspfS7yhclgc7dnSQYQCZ11cJ9k"
}