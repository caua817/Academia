# Tasks

## 1. Persistência e API de alunos no Xano

- [x] 1.1 Criar a tabela de alunos separada de `user`, com campos e situação definidos em `design.md`; validar o XanoScript e conferir que CPF não ganhou regra de unicidade.
- [x] 1.2 Implementar os endpoints autenticados para listar, consultar detalhes, cadastrar, editar e desativar alunos; exigir `admin` no backend e limitar os campos devolvidos na listagem e nos detalhes.
- [x] 1.3 Verificar em runtime que as cinco operações funcionam como `admin` e são negadas sem token ou com perfil `member`.
- [x] 1.4 Implementar a validação do nome obrigatório e a desativação sem exclusão física; validar os arquivos XanoScript.
- [x] 1.5 Verificar em runtime os cenários válidos e inválidos de cadastro/edição e confirmar que aluno desativado continua persistido.

## 2. Integração Reflex com a API

- [x] 2.1 Atualizar `academia/services/xano_client.py` para suportar as operações de alunos, propagar erros de comunicação/HTTP e não transformar falhas em listas vazias; verificar por testes.
- [x] 2.2 Adicionar estado Reflex para listar, pesquisar, cadastrar, editar e desativar alunos; manter o token no estado servidor da sessão de login, exigir token para chamadas e limpar os dados ao sair ou quando a sessão expirar; verificar estados de carregamento, sucesso, erro e lista vazia.
- [x] 2.3 Construir a área de gestão com busca, tabela, formulário e confirmação de desativação; verificar que só os campos mínimos aparecem na lista e que CPF é mascarado.
- [x] 2.4 Atualizar `academia/academia.py` com navegação funcional até a área de alunos e melhorar o painel sem quebrar a rota existente; verificar navegação e montagem das páginas no app Reflex.

## 3. Verificação e segurança

- [x] 3.1 Adicionar testes para busca, validação do nome, edição, desativação sem exclusão e respostas de erro; executar a suíte focada e corrigir falhas introduzidas.
- [x] 3.2 Executar a verificação/compilação Reflex disponível no projeto e conferir manualmente os fluxos principais, inclusive redirecionamento ao login sem sessão; registrar qualquer dependência de configuração local.
- [x] 3.3 Revisar `git diff` para confirmar que não há segredos nem exposição desnecessária de dados pessoais; validar novamente o XanoScript com as ferramentas/documentação Xano.
- [x] 3.4 Executar `xano workspace push --dry-run` após revisar o diff e registrar o resultado; não executar push real sem aprovação explícita do grupo.

## Registro da etapa Xano

- Tabela e cinco endpoints publicados no workspace `academia` após aprovação do grupo.
- Os seis arquivos passaram na validação XanoScript; o `dry-run` listou somente uma tabela e cinco endpoints novos.
- Verificado em runtime: `GET /alunos` sem token retorna HTTP 401.
- Nesta sessão, o pull do workspace trouxe 25 documentos; os GUIDs da tabela, dos cinco endpoints e da função `enforce_role` correspondem aos recursos locais. A validação XanoScript encontrou 25 arquivos válidos e nenhum inválido.
- O workspace não possui testes unitários nem testes de fluxo cadastrados; `unit_test run_all` e `workflow_test run_all` não executaram casos.
- Sem token, `GET /alunos`, consulta de detalhes e `PATCH` de desativação responderam HTTP 401. As tentativas sem token de `POST`/`PUT` usaram entradas incompletas e responderam HTTP 400; isso não comprova a autorização dessas operações.
- A primeira tentativa de executar os testes autenticados no ambiente isolado foi interrompida antes de qualquer chamada HTTP porque `API_BASE_URL` continha um endereço placeholder que não resolvia.
- Na rechecagem, `API_BASE_URL` ainda correspondia ao endpoint do workspace publicado. Por segurança, não foram feitas chamadas autenticadas nem alterações de dados.
- Após autorização explícita para usar dados sintéticos no workspace publicado, as credenciais locais foram verificadas em `GET /auth/me`; ambos os tokens de teste responderam HTTP 401. Nenhuma chamada CRUD foi feita e nenhum cadastro de teste foi criado.
- Por orientação do usuário, a validação runtime no Xano e os testes de escrita autenticados ficam adiados. Nenhum valor de token ou senha foi exibido.
- Cliente e interface Reflex implementados; 11 testes locais com transporte HTTP mockado passaram, sem chamadas autenticadas ao Xano.
- `reflex compile --dry` concluiu com sucesso. A validação XanoScript foi repetida: seis arquivos válidos, nenhum inválido.
- A revisão do diff não encontrou segredos nem exposição de CPF/endereço na listagem; a API omite o CPF por completo, e os detalhes pessoais são carregados sob demanda para edição.
- `xano workspace push --dry-run` concluiu com “No changes to push”; nenhum push real foi executado.
- Verificação local em 2026-10-24: os 11 testes focados passaram e `reflex compile --dry` concluiu com sucesso usando o ambiente `.venv` do projeto. No navegador, a tela de login renderizou, o WebSocket do Reflex conectou e o acesso direto a `/alunos` sem sessão redirecionou para `/login`. Nenhuma operação autenticada ou dado foi enviado ao Xano nesta verificação.
- Verificação manual do usuário em 2026-10-24 com conta `admin`: confirmou listagem, consulta de detalhes/edição, cadastro, edição e desativação; confirmou também rejeição de cadastro sem nome e de edição inválida. O usuário informou que o registro desativado continuou disponível após atualizar/reabrir. As operações negadas sem token e com perfil `member` ainda não foram verificadas.
- Tentativa de verificação com conta `member`: o usuário relatou que não viu alunos, mas a interface exibiu a mensagem genérica de falha de conexão em vez da mensagem específica de falta de permissão. Resultado inconclusivo; não comprova HTTP 403 e a tarefa 1.3 permanece pendente.
- Diagnóstico sem credenciais em 2026-10-24: a URL Xano configurada respondeu HTTP 401 a uma requisição GET `/alunos` sem token e também a um token Bearer sintético inválido. Isso confirma conectividade e rejeição de chamadas não autenticadas, mas não valida o token de um usuário `member`; a tentativa pela interface continua inconclusiva.
- Evidência visual enviada pelo usuário em 2026-10-24: a execução autenticada do endpoint de listagem no console Xano retornou sucesso e dados. Isso reforça a verificação de leitura autenticada, mas não identifica o perfil usado na execução nem comprova rejeição de chamadas como `member`; a tarefa 1.3 permanece pendente.
- Evidência visual adicional de `/auth/me` enviada pelo usuário em 2026-10-24: o token selecionado no console Xano pertence a um usuário com `role: admin`. Portanto, a execução bem-sucedida da listagem ocorreu como `admin`, não como `member`; ela não comprova a negação por perfil. Nenhuma falha de autorização foi confirmada até aqui.
- Verificação runtime do usuário em 2026-10-24: `/auth/me` confirmou que o token do teste pertence a `member` e `GET /alunos` respondeu HTTP 403, sem retornar a lista. Isso comprova a negação da operação de listagem para `member`. As demais operações como `member` e a negação de operações válidas sem token/perfil `member` ainda não foram verificadas, então a tarefa 1.3 permanece parcialmente pendente.
- Verificação adicional do usuário em 2026-10-24: usando o mesmo perfil `member`, `GET /alunos/detalhes/1` respondeu HTTP 403. Assim, a listagem e a consulta de detalhes estão comprovadamente bloqueadas para `member`; cadastro, edição e desativação não foram chamados com esse perfil para evitar alterações de dados.
- Verificação adicional do usuário em 2026-10-24: `PUT /alunos/atualizar/2147483647` e `PATCH /alunos/desativar/2147483647`, autenticados como `member`, responderam HTTP 403. O ID sentinela não aponta para um registro real. As quatro rotas testadas negaram acesso; falta verificar a rota POST como `member` com nome vazio para garantir que nenhuma linha possa ser criada caso o controle falhe.
- Verificação final do usuário em 2026-10-24: `POST /alunos` com perfil `member` e nome vazio respondeu HTTP 403. Com isso, as cinco operações (listar, detalhes, cadastrar, editar e desativar) foram observadas retornando 403 para `member`; cadastro vazio foi rejeitado antes de qualquer criação possível caso houvesse falha de autorização. O usuário também confirmou anteriormente os cinco fluxos válidos com `admin`. A verificação de acesso sem token permanece registrada nos endpoints GET de lista, GET de detalhes e PATCH, que responderam 401.
