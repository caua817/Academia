# Tasks

## 1. Diagnóstico do runtime

- [x] 1.1 Com conta `admin`, verificar se a tentativa de cadastro `TESTE OpenSpec 20261027 Aluno` foi persistida antes de qualquer novo POST; confirmar pelo resultado filtrado, sem expor outros registros nem dados pessoais.
- [x] 1.2 Conferir alterações locais e sincronizar/reconciliar o workspace Xano conforme as instruções do projeto; comparar o endpoint e a tabela publicados com o payload atual e identificar a causa do HTTP 500 sem registrar credenciais ou dados pessoais.

## 2. Correção e regressão

- [x] 2.1 Aplicar a menor correção no cliente Reflex ou no contrato Xano, conforme a causa confirmada; adicionar teste de regressão para campos opcionais vazios enviados como `null` e verificar que o teste reproduz o comportamento esperado.
- [x] 2.2 Validar os arquivos XanoScript alterados e executar os testes focados do cliente/estado Reflex; verificar também que o cadastro sem nome continua sendo rejeitado e que nenhuma falha HTTP é apresentada como sucesso.

## 3. Verificação integrada

- [x] 3.1 No runtime, validar com dados sintéticos o cadastro de aluno com apenas nome, confirmar persistência e leitura como `admin`, e verificar que a lista não expõe CPF nem endereço; antes de criar, confirmar que o registro de teste não existe para evitar duplicação.
- [ ] 3.2 Verificar no runtime a rejeição sem autenticação e com perfil `member`, além da rejeição de cadastro sem nome; confirmar que não há novo registro após as rejeições. Se não houver conta de teste para algum perfil, registrar o bloqueio sem compartilhar credenciais.
- [x] 3.3 Revisar o diff e executar `xano workspace push --dry-run`; não publicar alterações reais no Xano sem aprovação explícita do grupo.
