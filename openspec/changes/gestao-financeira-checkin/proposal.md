# Proposal

## Why

A Fase 1 já permite manter alunos, planos e matrículas, mas ainda não registra as cobranças mensais, pagamentos ou presença dos alunos. Sem esses recursos, a academia não consegue acompanhar o ciclo financeiro básico nem registrar check-ins dentro do fluxo administrativo.

## What Changes

- Criar mensalidades para cada matrícula a partir do valor mensal e da duração contratada, preservando as condições vigentes no momento da matrícula.
- Não gerar cobranças retroativas automaticamente para matrículas existentes antes da implantação.
- Permitir consultar mensalidades e registrar pagamentos integrais, mantendo histórico rastreável para correções e sem exclusão física de registros financeiros.
- Registrar e consultar check-ins de alunos com matrícula ativa; mensalidades vencidas não impedem a entrada.
- Disponibilizar as operações desta entrega somente para `admin`, com autorização aplicada no Xano. Esta decisão é específica desta change e diverge do overview, que descreve a recepção como responsável por pagamentos e check-ins.
- Implementar as interfaces correspondentes exclusivamente em Reflex, consumindo APIs Xano.

## Capabilities

### New Capabilities

- `billing-management`: consultar mensalidades e registrar pagamentos integrais e suas correções rastreáveis.
- `attendance-management`: registrar e consultar check-ins de alunos elegíveis.

### Modified Capabilities

- `plan-management`: estabelecer que o valor cadastrado no plano representa o valor de cada parcela mensal.
- `enrollment-management`: gerar a quantidade de mensalidades correspondente à duração contratada usando o valor mensal congelado na matrícula.

## Impact

- XanoScript e tabelas de mensalidades, pagamentos e check-ins; endpoints autenticados com autorização administrativa no backend.
- Fluxo de criação de matrícula para gerar as parcelas sem alterar o valor e a duração já contratados.
- Telas Reflex para consulta de mensalidades, registro/correção de pagamentos e registro/consulta de check-ins.
- Testes de contrato, regras de estado e integração com dados sintéticos; nenhuma dependência nova é prevista.

As regras confirmadas para esta change são: vencimento no dia 10; parcelas mensais integrais, sem pró-rata, em quantidade igual à duração da matrícula; primeira parcela no próximo dia 10 em ou após o início, e parcelas seguintes a cada mês; mensalidade em atraso após o vencimento, sem juros ou multa; pagamento integral somente por PIX ou cartão; correção contábil por estorno/cancelamento rastreável, sem reembolso externo; check-in permitido mesmo com mensalidade vencida, desde que aluno e matrícula estejam ativos; múltiplos check-ins no mesmo dia são permitidos; e não há geração automática de cobranças retroativas para matrículas existentes antes da implantação.
