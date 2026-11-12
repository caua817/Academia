table sessao_aula {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int modalidade_id {
      table = "modalidade"
    }
    int instrutor_id {
      table = "user"
    }
    timestamp inicio
    timestamp termino
    int capacidade
    text? local? filters=trim
    enum situacao?=Agendada {
      values = ["Agendada", "Cancelada"]
    }
    // Atualizado dentro da transação para serializar alterações da mesma sessão.
    timestamp? reserva_lock_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "inicio", op: "asc"}]}
    {type: "btree", field: [{name: "instrutor_id"}, {name: "inicio", op: "asc"}]}
    {type: "btree", field: [{name: "modalidade_id"}, {name: "inicio", op: "asc"}]}
    {type: "btree", field: [{name: "situacao"}, {name: "inicio", op: "asc"}]}
  ]
}
