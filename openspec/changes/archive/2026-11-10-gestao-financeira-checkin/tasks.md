# Tasks

## 1. Diagnóstico e modelo de dados Xano

- [x] 1.1 Fazer pull do workspace Xano para uma pasta isolada, comparar as matrículas e preservar os diffs locais; registrar a estrutura publicada sem incluir registros, tokens ou dados pessoais.
- [x] 1.2 Criar tabelas e índices de mensalidades, pagamentos e check-ins, incluindo vínculos, competência, vencimento, responsável e estados de correção; validar cada arquivo XanoScript.

## 2. Geração de mensalidades na matrícula

- [x] 2.1 Alterar a criação da matrícula para gerar na mesma transação uma parcela integral por mês contratado, com valor congelado, vencimentos no dia 10 e sem cobranças retroativas; validar XanoScript e cobrir calendário, atomicidade e prevenção de duplicatas com testes.
- [x] 2.2 Preservar matrículas anteriores sem parcelas automáticas; verificar com teste que a implantação não cria cobranças retroativas.

## 3. APIs de gestão financeira

- [x] 3.1 Implementar consulta de mensalidades e cálculo de situações pendente, paga e atrasada sem rotina agendada; validar filtros, autorização `admin` e respostas sem dados pessoais desnecessários com testes.
- [x] 3.2 Implementar registro de pagamento integral, rejeitando valores parciais, divergentes ou duplicados; verificar autorização e transições de estado com testes.
- [x] 3.3 Implementar cancelamento/estorno com motivo, responsável e data sem apagar o lançamento original; verificar que o histórico permanece e que a situação da mensalidade é recalculada.

## 4. APIs de check-in

- [x] 4.1 Implementar registro de check-in autorizado a `admin`, validando no backend aluno ativo e matrícula vigente, sem bloquear por inadimplência; validar XanoScript e cobrir os cenários aceitos e rejeitados.
- [x] 4.2 Implementar consulta de histórico de check-ins com dados mínimos; verificar autorização e formato da resposta com testes.

## 5. Interfaces Reflex e integração

- [x] 5.1 Adicionar chamadas tipadas no `XanoClient` para mensalidades, pagamentos, correções e check-ins; cobrir métodos, caminhos, payloads, erros HTTP e respostas inválidas com testes.
- [x] 5.2 Criar telas Reflex de mensalidades/pagamentos e check-ins, acessíveis pelo painel administrativo; verificar carregamento, vazio, sucesso, erros e ausência de dados pessoais desnecessários.
- [x] 5.3 Executar testes focados e a suíte completa, compilar o app com `reflex compile --dry` e validar todos os XanoScript alterados.
- [x] 5.4 Corrigir o `XanoClient` para enviar o token de sessão como `Authorization: Bearer <token>` em toda chamada protegida; adicionar regressão com transporte mockado que verifica o token sintético enviado e rejeita token vazio sem requisição.

## 6. Verificação integrada e publicação

- [x] 6.1 Fazer uma verificação integrada enxuta com os dados sintéticos já existentes: confirmar que a sessão administrativa consulta matrículas e mensalidades, que pagamentos integrais e correções aparecem no histórico e que o histórico de check-ins é consultável. O runtime apresentou matrículas com parcelas, mensalidades pagas/atrasadas/pendentes, pagamento cancelado com motivo e check-in registrado; os endpoints sem autenticação já haviam retornado HTTP 401. Os cenários de check-in com e sem inadimplência permanecem cobertos pelos testes locais de regra. Não foram criados novos registros nem repetidas operações no workspace atual.
- [x] 6.2 Revisar o diff e executar `xano workspace push --dry-run` limitado aos arquivos da change; realizar publicação real somente após aprovação explícita e, então, repetir as verificações de runtime.
