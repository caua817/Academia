# Tasks

## 1. Interface financeira

- [x] 1.1 Impedir carregamentos financeiros concorrentes e bloquear gravação/correção repetida durante operações em andamento; verificar com testes que cada ação concorrente dispara no máximo uma solicitação.
- [x] 1.2 Tratar HTTP 429 com orientação para aguardar, sem confirmação de sucesso e preservando os dados anteriores; verificar cenários de consulta, registro e correção com testes do estado financeiro.

## 2. Consulta de mensalidades no Xano

- [x] 2.1 Consultar documentação oficial Xano e consolidar a busca de pagamentos ativos no endpoint de mensalidades, preservando shape, ordenação e regras; validar o XanoScript e cobrir mensalidades pagas, pendentes e atrasadas.

## 3. Verificação e implantação

- [x] 3.1 Executar testes direcionados e a suíte Python relevante, `reflex compile --dry`, validação XanoScript e `git diff --check`; confirmar que a interface continua apresentando mensalidades e histórico de pagamentos corretamente.
- [x] 3.2 Revisar o diff e executar `xano workspace push --dry-run` apenas para os arquivos da mudança; apresentar os objetos e avisos ao grupo e obter aprovação explícita antes de qualquer push real.
- [ ] 3.3 Após aprovação, publicar somente os arquivos financeiros aprovados e verificar a consulta integrada sem excesso de operações; manter pendente se não houver ambiente autenticado seguro para o teste.
