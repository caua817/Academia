query "auth/signup" verb=POST {
  api_group = "Authentication"

  input {}

  stack {
    precondition (false) {
      error_type = "accessdenied"
      error = "O cadastro público está desativado."
    }
  }

  response = null
  tags = ["xano:quick-start"]
  guid = "2hnd_12aRH0pFOPUXwGdeXUakLE"
}