function "Quick Start/enforce_profile_access" {
  input {
    int user_id
    bool allow_receptionist?=false
    bool allow_instructor?=false
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $input.user_id
      output = ["role", "situacao"]
      mock = {
        "allows active administrator": {id: 2147483641, role: "admin", situacao: "Ativo"}
        "allows receptionist when enabled": {id: 2147483642, role: "recepcionista", situacao: "Ativo"}
        "denies receptionist when disabled": {id: 2147483643, role: "recepcionista", situacao: "Ativo"}
        "allows instructor when enabled": {id: 2147483644, role: "instrutor", situacao: "Ativo"}
        "denies instructor when disabled": {id: 2147483645, role: "instrutor", situacao: "Ativo"}
        "denies member": {id: 2147483646, role: "member", situacao: "Ativo"}
        "denies inactive receptionist": {id: 2147483647, role: "recepcionista", situacao: "Inativo"}
      }
    } as $user

    precondition ($user != null && $user.situacao == "Ativo" && ($user.role == "admin" || ($input.allow_receptionist && $user.role == "recepcionista") || ($input.allow_instructor && $user.role == "instrutor"))) {
      error_type = "accessdenied"
      error = "Seu perfil não está autorizado a executar esta operação."
    }
  }

  response = $user.role

  test "allows active administrator" {
    input = {user_id: 2147483641}
    expect.to_equal ($response) {value = "admin"}
  }

  test "allows receptionist when enabled" {
    input = {user_id: 2147483642, allow_receptionist: true}
    expect.to_equal ($response) {value = "recepcionista"}
  }

  test "denies receptionist when disabled" {
    input = {user_id: 2147483643}
    expect.to_throw
  }

  test "allows instructor when enabled" {
    input = {user_id: 2147483644, allow_instructor: true}
    expect.to_equal ($response) {value = "instrutor"}
  }

  test "denies instructor when disabled" {
    input = {user_id: 2147483645}
    expect.to_throw
  }

  test "denies member" {
    input = {user_id: 2147483646, allow_receptionist: true, allow_instructor: true}
    expect.to_throw
  }

  test "denies inactive receptionist" {
    input = {user_id: 2147483647, allow_receptionist: true}
    expect.to_throw
  }
  guid = "VfzdbqUgWUnr3T1c-4BhHQ_Pgkc"
}
