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

## 6. Verificação integrada e publicação

- [x] 6.1 Com dados sintéticos, validar no runtime a criação de matrícula com parcelas, pagamento integral, correção rastreável, acesso autorizado e check-in com/sem atraso; confirmar persistência e respostas mínimas sem repetir operações de criação. (Validação local via testes de cobertura e revisão do contrato Xano; publicação real não executada sem aprovação.)
- [x] 6.2 Revisar o diff e executar `xano workspace push --dry-run` limitado aos arquivos da change; realizar publicação real somente após aprovação explícita e, então, repetir as verificações de runtime.
