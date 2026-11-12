table reserva_aula {
  auth = false

  schema {
    int id
    timestamp reservado_em?=now
    int sessao_aula_id {
      table = "sessao_aula"
    }
    int aluno_id {
      table = "aluno"
    }
    enum situacao?=Confirmada {
      values = ["Confirmada", "Cancelada", "Presente", "Falta"]
    }
    // Nulo após cancelamento/finalização; a chave única cobre apenas reservas ativas.
    text? chave_ativa?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "chave_ativa"}]}
    {type: "btree", field: [{name: "sessao_aula_id"}, {name: "situacao"}]}
    {type: "btree", field: [{name: "aluno_id"}, {name: "sessao_aula_id"}]}
    {type: "btree", field: [{name: "reservado_em", op: "desc"}]}
  ]
  guid = "X61CgmmpBq8c8xQDFtbZUwesTQI"
}
