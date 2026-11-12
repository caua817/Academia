// Cadastra uma modalidade ativa para administradores.
query modalidades verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
    text nome? filters=trim
    text? descricao? filters=trim
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    precondition ($input.nome != null && ($input.nome|strlen) > 0) {
      error_type = "inputerror"
      error = "O nome da modalidade é obrigatório."
    }

    db.add modalidade {
      data = {
        nome: $input.nome
        descricao: $input.descricao
        situacao: "Ativo"
      }
      mock = {
        "creates valid modality": {id: 2147483647, nome: "Funcional", descricao: null, situacao: "Ativo"}
      }
    } as $modalidade
  }

  response = {
    id: $modalidade.id
    nome: $modalidade.nome
    descricao: $modalidade.descricao
    situacao: $modalidade.situacao
  }

  guid = "kB6s6Nfmv0mq8g1KJ1n2xZ4y9oA"

  test "rejects empty modality name" {
    input = {nome: ""}
    expect.to_throw
  }

  test "creates valid modality" {
    input = {nome: "Funcional", descricao: null}
    expect.to_equal ($response.situacao) {value = "Ativo"}
  }
}
