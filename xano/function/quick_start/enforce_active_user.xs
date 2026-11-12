// Rejects missing or inactive accounts before protected operations.
function "Quick Start/enforce_active_user" {
  input {
    int user_id
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $input.user_id
      output = ["id", "situacao"]
      mock = {
        "rejects inactive account": {id: 2147483647, situacao: "Inativo"}
        "allows active account": {id: 2147483647, situacao: "Ativo"}
        "allows legacy account without status": {
          id: 2147483647
          situacao: null
        }
      }
    } as $user

    precondition ($user != null) {
      error_type = "accessdenied"
      error = "User is not active."
    }

    precondition ($user.situacao != "Inativo") {
      error_type = "accessdenied"
      error = "User is not active."
    }
  }

  response = null

  test "rejects inactive account" {
    input = {user_id: 2147483647}
    expect.to_throw
  }

  test "allows active account" {
    input = {user_id: 2147483647}
    expect.to_equal ($response) {value = null}
  }

  test "allows legacy account without status" {
    input = {user_id: 2147483647}
    expect.to_equal ($response) {value = null}
  }
  guid = "j97HKnQdplwskRdLP6Hth-KWOAc"
}
