# Tasks

## 1. Contas e autorização

- [x] 1.1 Estender a tabela `user` com os papéis de funcionário e situação ativa, preservando `member` e contas existentes; validar a definição XanoScript e compatibilidade do schema.
- [ ] 1.2 Rejeitar contas inativas no login, autenticação por link, identidade e autorização de operações protegidas; validar os cenários ativo/inativo com testes Xano isolados e `xano_validate_xanoscript`.
- [ ] 1.3 Impedir desativação ou rebaixamento do último administrador ativo usando transação serializável; validar os estados finais em cenário isolado e a sintaxe XanoScript.

## 2. API de funcionários

- [ ] 2.1 Implementar listagem e detalhes de funcionários nos caminhos já usados pelo cliente, retornando somente campos operacionais e exigindo `admin`; validar respostas, rejeição de acesso e ausência de credenciais.
- [ ] 2.2 Implementar convite e edição de funcionários com validação de nome, e-mail e perfil; enviar link individual de definição de senha, permitir reenvio de convite pendente e rejeitar duplicidade concluída; validar erros e resposta sem segredos.
- [ ] 2.3 Implementar ativação e desativação sem exclusão física, incluindo proteção do último administrador; validar situações retornadas e histórico preservado.

## 3. Cliente autenticado

- [x] 3.1 Confirmar que o `XanoClient` encaminha o token real no cabeçalho de autenticação aceito pelo Xano, mantendo rejeição de sessão vazia; validar com transporte HTTP mockado que o token não é mascarado nem registrado.

## 4. Verificação e sincronização

- [x] 4.1 Executar testes direcionados do cliente, validação XanoScript dos arquivos alterados, `openspec validate --all` e `reflex compile --dry`; registrar os resultados sem criar dados reais.
- [x] 4.2 Revisar `git diff` e executar `xano workspace push --dry-run` limitado aos arquivos desta change; confirmar que nenhuma publicação real foi feita sem aprovação explícita.
