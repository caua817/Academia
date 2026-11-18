# Tasks

## 1. Cliente e estado de ativação

- [x] 1.1 Adicionar ao cliente de autenticação a chamada pública de aceitação de convite, validando forma da resposta e erros HTTP sem registrar payloads; verificar método, caminho e payload com transporte mockado.
- [x] 1.2 Criar estado Reflex de ativação que leia token/e-mail do fragmento do router, remova o fragmento antes de prosseguir e mantenha segredos apenas no servidor; verificar parsing, limpeza de URL e ausência de token nas variáveis públicas.
- [x] 1.3 Validar senha e confirmação no estado, enviar a ativação uma única vez, limpar campos após a tentativa e direcionar para login somente após sucesso; cobrir senha fraca, divergente, link ausente, erro de API e sucesso com testes locais.

## 2. Página pública Reflex

- [x] 2.1 Criar a página pública `/ativar-funcionario`, fora do shell administrativo, com formulário acessível, estados de carregamento/erro/sucesso e nenhuma ação de cadastro público; verificar a rota e o fluxo por testes.
- [x] 2.2 Registrar a rota no app Reflex e validar com `reflex compile --dry` e navegação no navegador usando somente fragmentos fictícios, sem token real.

## 3. Contrato Xano

- [x] 3.1 Fazer pull do workspace em diretório isolado e sincronizar para `xano/` somente os arquivos relevantes após comparar diferenças; verificar que mudanças Xano não relacionadas permanecem intocadas.
- [x] 3.2 Implementar endpoint anônimo de aceitação que permita somente conta de funcionário pendente, serialize aceitações concorrentes, valide e-mail/token/expiração/uso e senha, grave hash e consumo do convite na mesma atualização e responda sem dados/credenciais; cobrir sucesso, expirado, usado, não funcionário e senha inválida com testes Xano.
- [x] 3.3 Atualizar o endpoint de convite para exigir `frontend_base_url` HTTPS, compor o link para `/ativar-funcionario` com dados no fragmento e falhar antes de criar conta/enviar e-mail quando a configuração for inválida; verificar link, ausência de fallback e payload de resposta sem token.
- [x] 3.4 Garantir que os registros de auditoria da aceitação não recebam senha, token, objeto `password_reset` nem registro completo do usuário; verificar allowlist de metadados e ausência de credenciais nos testes/revisão.

## 4. Verificação e publicação

- [x] 4.1 Validar todos os arquivos XanoScript alterados com Xano Developer MCP e executar os testes Xano relevantes; confirmar que a API não emite token de sessão e que convite inválido não altera a conta.
- [x] 4.2 Executar os testes Python focados e a compilação Reflex; verificar que os comportamentos existentes de login e recuperação de senha continuam funcionando.
- [x] 4.3 Revisar `git diff` e executar `xano workspace push --dry-run`; apresentar o resultado ao grupo e não fazer push real sem aprovação explícita.
