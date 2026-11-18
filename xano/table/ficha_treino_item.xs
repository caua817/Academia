table ficha_treino_item {
  auth = false

  schema {
    int id
    int ficha_treino_id {
      table = "ficha_treino"
    }
    int exercicio_id {
      table = "exercicio"
    }
    int ordem
    int series
    int repeticoes
    decimal? carga_kg?
    text exercicio_nome filters=trim
    text? grupo_muscular? filters=trim
    text? equipamento? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "ficha_treino_id"}, {name: "ordem"}]}
    {type: "btree", field: [{name: "exercicio_id"}]}
  ]
}
