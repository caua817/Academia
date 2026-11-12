table checkin {
  auth = false

  schema {
    int id
    timestamp data_hora?=now
    int aluno_id {
      table = "aluno"
    }
    int matricula_id {
      table = "matricula"
    }
    int registrado_por {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "aluno_id"}, {name: "data_hora", op: "desc"}]}
    {type: "btree", field: [{name: "matricula_id"}]}
    {type: "btree", field: [{name: "registrado_por"}]}
  ]
  guid = "oYEfUwdyCCz2dbLNS0AO19dPkMw"
}
