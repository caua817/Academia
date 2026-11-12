# Tasks

## 1. Modelo de dados e APIs Xano

- [ ] 1.1 Criar tabelas e índices para catálogo de exercícios, fichas, itens ordenados de ficha, avaliações, medidas e vínculo de correção; validar todos os XanoScripts alterados.
- [ ] 1.2 Implementar APIs autenticadas de consulta, cadastro, edição e desativação de exercícios para `admin` e `instrutor`; testar validação, perfis negados e preservação de exercícios referenciados.
- [ ] 1.3 Implementar APIs de consulta e manutenção de fichas, itens e opções mínimas de aluno/instrutor; testar autorização, validação de períodos e parâmetros, exercício ativo e atomicidade sem persistência parcial.
- [ ] 1.4 Implementar APIs de registro e consulta de avaliações e medidas, incluindo responsável derivado da sessão, correção vinculada com motivo e proibição de exclusão; testar autorização, unidades, valores inválidos e preservação do histórico.

## 2. Cliente e interface Reflex

- [ ] 2.1 Adicionar chamadas tipadas no `XanoClient` para exercícios, fichas e avaliações; cobrir caminhos, métodos, payloads, respostas inválidas e estados HTTP com transporte mockado.
- [ ] 2.2 Implementar acesso a páginas por `admin` e `instrutor` sem ampliar o acesso às páginas administrativas existentes; testar URL direta, perfil negado, sessão ausente e falha ao verificar perfil.
- [ ] 2.3 Criar a página Reflex de catálogo de exercícios com estados de carregamento, vazio, sucesso, erro e desativação; cobrir validação e falhas em testes de UI.
- [ ] 2.4 Criar páginas Reflex de fichas e histórico por aluno, incluindo exercícios ordenados, validação e arquivamento; testar fluxo de sucesso, estados vazios e erros sem expor dados cadastrais desnecessários.
- [ ] 2.5 Criar páginas Reflex de registro e histórico de avaliações, com unidades explícitas e fluxo de correção; testar limpeza de dados sensíveis em logout e respostas 401/403.

## 3. Verificação integrada e publicação

- [ ] 3.1 Executar testes direcionados e a suíte existente, `reflex compile --dry`, validação OpenSpec e XanoScript; fazer smoke test com identidade e dados de teste não produtivos para sucesso, rejeição de perfil e histórico.
- [ ] 3.2 Revisar o diff e executar `xano workspace push --dry-run` limitado aos arquivos da change; não publicar no workspace real sem aprovação explícita e confirmar o runtime após eventual publicação aprovada.
