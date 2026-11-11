# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [billing-management](./specs/billing-management/spec.md), [attendance-management](./specs/attendance-management/spec.md), [enrollment-management](./specs/enrollment-management/spec.md) e [plan-management](./specs/plan-management/spec.md). O backend existente é XanoScript; as matrículas já congelam `valor_contratado` e `duracao_contratada_meses`, e o frontend Reflex consome as APIs por `XanoClient`. Ainda não há tabelas ou endpoints de mensalidades, pagamentos ou check-ins.

## Goals / Non-Goals

**Goals:**

- Manter geração, validação, persistência e autorização de cobranças, pagamentos e presença no Xano.
- Preservar a atomicidade entre criação de matrícula e geração das parcelas.
- Permitir que a interface Reflex apresente listas e formulários usando respostas mínimas e estados explícitos de erro/sucesso.
- Preservar registros financeiros por meio de correções rastreáveis, sem exclusão física.

**Non-Goals:**

- Alterar permissões de `admin` escolhidas para esta entrega, ainda que o overview descreva a recepção como responsável por pagamentos e check-ins.
- Implementar juros, multas, pró-rata, pagamentos parciais, processamento de cartão, estorno financeiro externo ou conciliação bancária.
- Adicionar check-out, catraca, restrição de check-in por inadimplência, ou comportamento de aulas/reservas.

## Decisions

### Persistir parcelas junto com a matrícula

Estender a transação de criação de matrícula para gravar a matrícula e todas as parcelas em uma única transação. Cada parcela usa o `valor_contratado` e a duração congelados na matrícula; a competência e o vencimento seguem a regra da spec, sem depender de alterações posteriores no plano.

Alternativa descartada: gerar parcelas em uma tarefa assíncrona ou por execução manual, pois isso permite que uma matrícula válida fique sem cobranças ou parcialmente cobrada.

### Calcular a situação da mensalidade a partir dos lançamentos

Considerar a mensalidade paga quando houver pagamento integral ativo; caso contrário, considerá-la atrasada quando a data atual for posterior ao vencimento, e pendente até essa data. Após cancelar/estornar um pagamento, recalcular a situação da mensalidade sem apagar o registro original. Isso evita depender de tarefas agendadas para atualizar situações diariamente.

Alternativa descartada: manter um estado de atraso que precisa ser alterado por rotina periódica, o que pode deixar a situação desatualizada quando a rotina falhar.

### Registrar correções como eventos rastreáveis

Manter o pagamento original e seus metadados; uma correção contábil registra motivo, responsável, data e estado de cancelamento/estorno, sem iniciar reembolso externo. A API calcula a situação financeira com base nos lançamentos válidos, não em exclusão ou sobrescrita silenciosa. O meio de pagamento aceito é PIX ou cartão.

Alternativa descartada: editar ou apagar o pagamento original, pois isso elimina o histórico necessário para auditoria.

### Validar check-in no backend no momento do registro

O endpoint de check-in confirma no Xano que o aluno está ativo e que existe matrícula válida na data/hora do registro. A situação financeira não participa dessa validação. O usuário responsável e o instante devem ser obtidos/validados no backend, não confiados ao cliente. Vários registros no mesmo dia são ocorrências distintas e não serão deduplicados.

Alternativa descartada: aplicar a regra somente na interface Reflex, pois ela não é uma fronteira de segurança e pode operar com estado desatualizado.

### Separar contratos de API e superfícies de consulta

Criar endpoints Xano para consulta e registro de mensalidades/pagamentos e check-ins, todos autenticados e autorizados para `admin`. Respostas de lista devem trazer somente os dados operacionais necessários; dados sensíveis do cadastro do aluno não são necessários para estas telas. No Reflex, adicionar as chamadas correspondentes a `XanoClient` e páginas integradas à navegação administrativa.

Alternativa descartada: consultar dados financeiros diretamente de tabelas do frontend ou duplicar regras de negócio em Python.

## Risks / Trade-offs

- **[Risco]** Matrículas anteriores à implantação não terão parcelas associadas e poderão parecer sem cobrança na nova tela. → **Mitigação:** não criar cobranças retroativas automaticamente e deixar esse comportamento explícito na interface e na documentação operacional.
- **[Risco]** Repetição de requisição pode tentar duplicar parcelas. → **Mitigação:** manter a criação de parcelas na mesma transação e garantir uma chave única por matrícula e competência/parcela.
- **[Risco]** A restrição exclusiva a `admin` difere da operação descrita no overview. → **Mitigação:** documentar a decisão da change e manter o backend como autoridade; rever o perfil em change futura se o grupo desejar.
- **[Risco]** Cancelar um pagamento pode reabrir uma mensalidade já vencida. → **Mitigação:** recalcular o estado imediatamente e exibir a correção e o motivo no histórico.
- **[Risco]** Arquivos Xano locais podem divergir do workspace publicado. → **Mitigação:** fazer pull isolado e comparar antes da implementação; validar XanoScript e revisar o dry-run. Qualquer publicação real exige aprovação explícita do grupo.
- **[Risco]** Dados sintéticos de validação no workspace atual podem aparecer em relatórios. → **Mitigação:** criar somente após aprovação explícita, identificá-los com o prefixo `TESTE-VALIDACAO`, não usar dados pessoais reais, executar as criações uma única vez, registrar os IDs e não apagar registros financeiros nem alterar registros existentes.

## Migration Plan

1. Verificar a estrutura publicada do workspace e preservar os diffs locais antes de qualquer reconciliação.
2. Implementar tabelas/endpoints Xano, cobrindo atomicidade, autorização e preservação do histórico.
3. Implementar clientes e telas Reflex com testes focados e dados exclusivamente sintéticos.
4. Não gerar cobranças retroativas automaticamente para matrículas existentes antes da implantação.
5. Validar XanoScript, testes, compilação Reflex e `xano workspace push --dry-run`; pedir aprovação explícita antes de qualquer push real.
6. Após a publicação aprovada, validar cadastro de matrícula, parcelas, pagamento/correção e check-in no runtime. Se não houver staging, executar a validação no workspace atual somente após autorização explícita, usando registros identificados com `TESTE-VALIDACAO`, sem dados pessoais reais e sem alterar registros existentes. Registrar os IDs persistidos, não apagar registros financeiros e não repetir operações de criação após uma resposta incerta.

Rollback: interromper a publicação se a validação falhar. Não excluir fisicamente matrículas, mensalidades, pagamentos ou check-ins; corrigir por operações rastreáveis compatíveis com o domínio.
