# Tasks

## 1. Interface Reflex

- [x] 1.1 Remover o acesso ao cadastro, o modal e o estado/handlers de auto cadastro da tela de login; verificar que nenhum link, formulário ou evento de cadastro permanece.
- [x] 1.2 Remover a chamada pública de cadastro do cliente de autenticação e atualizar os testes focados para confirmar que o login mantém o contrato e que não há chamada HTTP de cadastro.

## 2. Endpoint Xano

- [x] 2.1 Atualizar o workspace local com `xano workspace pull` quando necessário, consultar a documentação Xano e desativar o endpoint legado de forma que nenhuma chamada autenticada ou anônima crie usuário ou token; validar XanoScript.
- [x] 2.2 Revisar o diff e executar `xano workspace push --dry-run`; após aprovação explícita do grupo, publicar a desativação e verificar no runtime que chamadas diretas ao endpoint não criam conta nem emitem token.

## 3. Validação integrada

- [x] 3.1 Executar os testes de autenticação, `reflex compile --dry` e `openspec validate desabilitar-cadastro-publico --strict`; corrigir falhas introduzidas pela change.
- [x] 3.2 Verificar no navegador que o login não oferece cadastro público, que o controle de senha e as mensagens continuam funcionais e que uma conta existente consegue entrar; não usar nem registrar credenciais reais nos testes.
