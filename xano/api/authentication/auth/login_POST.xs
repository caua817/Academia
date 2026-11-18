// Login and retrieve an authentication token or a password-change challenge.
query "auth/login" verb=POST {
  api_group = "Authentication"

  input {
    email email? filters=trim|lower
    text password?
  }

  stack {
    // Get the user record via email
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = [
        "id"
        "created_at"
        "name"
        "email"
        "password"
        "role"
        "situacao"
        "temporary_password"
        "temporary_password_expires_at"
      ]
      mock = {
        "blocks temporary-password login after five attempts": {
          id: 2147483641
          email: "employee@example.test"
          password: "synthetic-hash"
          role: "instrutor"
          situacao: "Ativo"
          temporary_password: true
          temporary_password_expires_at: "2099-01-01T00:00:00Z"
        }
      }
    } as $user
  
    // Check to make sure a user with that email exists
    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }

    conditional {
      if ($user.temporary_password == true) {
        var $temporary_password_rate_limit_status {
          value = "check"
          mock = {
            "blocks temporary-password login after five attempts": "blocked"
          }
        }

        conditional {
          if ($temporary_password_rate_limit_status == "check") {
            redis.ratelimit {
              key = "temporary_password_attempts:" ~ $user.id
              max = 5
              ttl = 900
              error = "Muitas tentativas. Aguarde 15 minutos antes de tentar novamente."
            }
          }
        }

        precondition ($temporary_password_rate_limit_status != "blocked") {
          error_type = "accessdenied"
          error = "Muitas tentativas. Aguarde 15 minutos antes de tentar novamente."
        }
      }
    }
  
    // Check that the password matches the hashed password
    security.check_password {
      text_password = $input.password
      hash_password = $user.password
    } as $pass_result

    // Verify that the password check passed
    precondition ($pass_result) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    function.run "Quick Start/enforce_active_user" {
      input = {user_id: $user.id}
    } as $active_user_check

    var $login_result {
      value = {}
    }

    conditional {
      if ($user.temporary_password == true) {
        conditional {
          if ($user.temporary_password_expires_at > now) {
            var.update $login_result {
              value = {
                authToken: null
                requires_password_change: true
                temporary_password_expired: false
              }
            }
          }

          else {
            var.update $login_result {
              value = {
                authToken: null
                requires_password_change: true
                temporary_password_expired: true
              }
            }
          }
        }

        function.run "Quick Start/log_event" {
          input = {
            user_id: $user.id
            action: "temporary_password_login"
            metadata: {}
          }
        } as $event_log
      }

      else {
        security.create_auth_token {
          table = "user"
          extras = {}
          expiration = 86400
          id = $user.id
        } as $authToken

        function.run "Quick Start/log_event" {
          input = {user_id: $user.id, action: "login", metadata: {}}
        } as $event_log

        var.update $login_result {
          value = {
            authToken: $authToken
            user_id: $user.id
            requires_password_change: false
            temporary_password_expired: false
          }
        }
      }
    }
  }

  response = $login_result
  tags = ["xano:quick-start"]

  test "blocks temporary-password login after five attempts" {
    input = {
      email: "employee@example.test"
      password: "Temporary1"
    }
    expect.to_throw
  }

  guid = "MAQGHIbNZKnJcj4-4SSbzwLGnOQ"
}