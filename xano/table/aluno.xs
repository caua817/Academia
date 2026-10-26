table "aluno" {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    timestamp? matricula_lock_at? {
      description = "Campo interno usado para serializar novas matrículas do aluno."
    }
    text nome filters=trim {
      sensitive = true
    }
    text cpf? filters=trim {
      sensitive = true
    }
    date data_nascimento? {
      sensitive = true
    }
    text contato? filters=trim {
      sensitive = true
    }
    email? email filters=trim|lower {
      sensitive = true
    }
    text endereco? filters=trim {
      sensitive = true
    }
    enum situacao?="Ativo" {
      values = ["Ativo", "Inativo"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "nome", op: "asc"}]}
    {type: "btree", field: [{name: "situacao", op: "asc"}]}
  ]
  guid = "W6gk5wQywhNKFWpaRfWHJmdPGuY"
}
