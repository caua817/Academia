// Lista os alunos com os campos permitidos para cada perfil.
query alunos verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    function.run "Quick Start/enforce_profile_access" {
      input = {
        user_id: $auth.id
        allow_receptionist: true
        allow_instructor: true
      }
    } as $role_check
  
    db.query aluno {
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $alunos
  
    var $alunos_visiveis {
      value = []
    }

    foreach ($alunos) {
      each as $aluno {
        var $cpf_mascarado {
          value = ""
        }

        conditional {
          if ($aluno.cpf != null && ($aluno.cpf|strlen) > 0) {
            var.update $cpf_mascarado {
              value = "***.***.***-" ~ ($aluno.cpf|substr:-2)
            }
          }
        }

        conditional {
          if ($role_check == "instrutor") {
            var.update $alunos_visiveis {
              value = $alunos_visiveis
                |append:```
                  {
                    id: $aluno.id,
                    nome: $aluno.nome,
                    situacao: $aluno.situacao
                  }
                  ```
            }
          }
          else {
            var.update $alunos_visiveis {
              value = $alunos_visiveis
                |append:```
                  {
                    id: $aluno.id,
                    nome: $aluno.nome,
                    cpf: $cpf_mascarado,
                    contato: $aluno.contato,
                    email: $aluno.email,
                    situacao: $aluno.situacao
                  }
                  ```
            }
          }
        }
      }
    }
  }

  response = $alunos_visiveis
  guid = "J8zfUdWmg0yEJQ4NbH_ustj6hBM"
}