# Tasks

## 1. Preparação e contrato

- [x] 1.1 Fazer `xano workspace pull` conforme o procedimento do projeto e comparar o estado atual do workspace com `xano/`; registrar divergências antes de editar.
- [x] 1.2 Consultar a documentação do Xano Developer MCP para os recursos necessários e confirmar o fluxo de definição de senha por convite com link válido, uso único e expiração; o convite usa a rota da aplicação `/ativar-funcionario`, com token temporário e endpoint de aceite que valida expiração e uso único.
- [x] 1.3 Confirmar os caminhos, métodos, payloads e campos de resposta do contrato contra `academia/services/xano_client.py` e a capability `employee-management`.

## 2. Endpoints e autorização

- [x] 2.1 Implementar `GET /funcionarios` e `GET /funcionarios/detalhes/{funcionario_id}` usando `user`, excluindo `member` da lista e retornando somente campos operacionais; validar formato e ausência de credenciais.
- [x] 2.2 Implementar `POST /funcionarios/convites` com validação de nome, e-mail, perfil permitido e duplicidade, sem senha definida pelo administrador; verificar envio do link seguro e resposta sem token.
- [x] 2.3 Implementar `PUT /funcionarios/atualizar/{funcionario_id}` com allowlist de campos e validação de e-mail/perfil; verificar atualização e respostas de registro inexistente ou e-mail duplicado.
- [x] 2.4 Implementar `PATCH /funcionarios/desativar/{funcionario_id}` e `PATCH /funcionarios/ativar/{funcionario_id}` sem exclusão física; verificar situação retornada e preservação do registro.
- [x] 2.5 Proteger todas as rotas com autenticação e autorização `admin`; ajustar `Quick Start/enforce_role` somente se necessário e verificar que `member`, `recepcionista` e `instrutor` recebem negação sem afetar operações existentes.

## 3. Verificação e publicação

- [x] 3.1 Validar XanoScript com a documentação e ferramentas disponíveis; verificar respostas 401/403, validações 400/409, allowlist de campos, convite e operações de situação sem credenciais reais. Os três testes de `enforce_active_user` passaram; dos 11 testes de endpoints, 6 passaram e 5 foram bloqueados por `Unauthorized - Authentication Required` nos caminhos autenticados. Por solicitação explícita do usuário, a validação integrada adicional foi dispensada; esse resultado não representa aprovação dos cinco caminhos que o runner não conseguiu autenticar.
- [x] 3.2 Executar os testes locais relevantes do cliente/gestão de funcionários e confirmar que o contrato de `XanoClient` continua compatível.
- [x] 3.3 Revisar o `git diff` e executar `xano workspace push --dry-run`; apresentar o resultado ao grupo e não executar push real sem aprovação explícita.
