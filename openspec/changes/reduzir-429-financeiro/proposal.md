# Proposta: Reduzir respostas HTTP 429 no financeiro

## Por quê

A tela financeira pode emitir consultas repetidas ao carregar, atualizar após operações ou receber ações concorrentes. Além disso, a consulta de mensalidades executa uma consulta de pagamento para cada parcela, aumentando o trabalho do backend. Isso torna o fluxo suscetível a limitação de requisições e falhas HTTP 429.

## O que muda

- Evitar carregamentos e gravações financeiras duplicados enquanto uma operação equivalente estiver em andamento.
- Reduzir o número de consultas internas usadas para montar a lista de mensalidades.
- Apresentar uma orientação específica quando a API responder HTTP 429, sem indicar sucesso nem apagar dados financeiros já carregados.
- Cobrir concorrência, limitação de requisições e recuperação com testes.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `billing-management`: definir o comportamento da interface quando a API limita requisições financeiras, incluindo orientação para aguardar e tentar novamente sem duplicar operações.

## Impacto

- Frontend Reflex: estado, eventos de carregamento/registro/correção e mensagens de erro da tela financeira.
- Backend Xano: consulta de mensalidades e pagamentos, reduzindo consultas repetidas sem alterar o contrato de resposta nem as regras financeiras.
- Testes Python e validação XanoScript; nenhuma dependência nova prevista.
