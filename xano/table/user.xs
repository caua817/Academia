// Stores user information and allows the user to authenticate  against
table user {
  auth = true

  schema {
    int id
    timestamp created_at?=now
    text name filters=trim
    email? email filters=trim|lower
    password? password filters=min:8|minAlpha:1|minDigit:1
  
    // Perfil operacional do funcionário.
    enum role? {
      values = ["admin", "member", "recepcionista", "instrutor"]
    }

    enum situacao?=Ativo {
      values = ["Ativo", "Inativo"]
    }
    // Campo interno para serializar alterações da agenda do instrutor.
    timestamp? agenda_lock_at?
  
    object password_reset? {
      schema {
        password token?
        timestamp? expiration?
        bool used?
      }
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]

  tags = ["xano:quick-start"]
  guid = "RZqwDDzAeb4nFLmgkqQqSbIVYjM"
}