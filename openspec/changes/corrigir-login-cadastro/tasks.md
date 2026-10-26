# Tasks

## 1. Cliente HTTP de autenticação

- [x] 1.1 Criar cliente para `POST /auth/login` e `POST /auth/signup` sem cabeçalho de autorização; verificar caminhos, payloads, normalização e formato de token com transporte mockado.
- [x] 1.2 Tratar respostas HTTP, conexão e JSON inválido sem expor credenciais ou detalhes internos; verificar erros com testes locais.

## 2. Estado e formulários Reflex

- [x] 2.1 Atualizar `LoginState` para validar campos obrigatórios antes das requisições, iniciar sessão somente com token e apresentar mensagens seguras; verificar validações e contrato de token com testes locais mockados.
- [x] 2.2 Corrigir abertura/fechamento do modal e validar campos do cadastro; verificar visualmente que “Cadastrar” vazio mostra erro e não envia HTTP.

## 3. Verificação

- [x] 3.1 Executar os testes focados e `reflex compile --dry`; corrigir falhas introduzidas pela mudança.
- [x] 3.2 Conferir login/cadastro no navegador sem credenciais reais, confirmar que login envia e-mail/senha sem token e revisar o diff para não incluir segredos nem alterações Xano.
