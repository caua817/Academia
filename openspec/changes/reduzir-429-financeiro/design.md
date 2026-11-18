# Design

## Context

Veja [proposal.md](./proposal.md) para a motivação e [specs/billing-management/spec.md](./specs/billing-management/spec.md) para o comportamento esperado. Atualmente, `FinanceiroState` permite iniciar `load_financeiro` sem verificar se já existe uma carga em andamento. Após registrar ou corrigir um pagamento, `_reload` consulta mensalidades e pagamentos novamente. O endpoint Xano de mensalidades percorre cada mensalidade e executa uma consulta individual para localizar o pagamento ativo correspondente.

## Goals / Non-Goals

**Goals:**

- Impedir solicitações concorrentes redundantes na tela financeira.
- Diminuir a quantidade de consultas internas do endpoint de mensalidades, mantendo o mesmo formato de resposta e as regras de situação.
- Dar orientação clara ao receber HTTP 429 sem repetir automaticamente operações financeiras.
- Preservar dados já carregados quando uma atualização falhar por limite temporário.

**Non-Goals:**

- Alterar autorização, regras de pagamento, dados persistidos ou contrato público dos endpoints.
- Retentar automaticamente gravações financeiras, pois uma falha de transporte ou limite pode deixar incerto se a operação foi processada.
- Alterar limites ou configurações do workspace Xano sem aprovação explícita.

## Decisions

### Evitar chamadas concorrentes no estado Reflex

Usar os estados de carregamento, registro e correção como trava para rejeitar eventos duplicados antes de iniciar uma nova chamada. Depois de uma gravação bem-sucedida, atualizar a lista sem permitir que outra operação de escrita seja iniciada durante a atualização. Cobrir o comportamento com testes do estado financeiro.

**Alternativa considerada:** adicionar retentativas ou debounce genérico no cliente HTTP. Rejeitada por afetar outras áreas e, no caso de retentativas de escrita, poder duplicar efeitos financeiros.

### Consolidar a busca de pagamentos do endpoint de mensalidades

Substituir a consulta de pagamento feita dentro do loop por uma leitura consolidada dos pagamentos ativos e associá-los às mensalidades em memória, ou por uma junção equivalente suportada pelo Xano. A implementação deve preservar a ordenação, o cálculo de vencimento e os campos retornados; a sintaxe e o plano devem ser conferidos com a documentação oficial Xano e o validador antes de qualquer publicação.

**Alternativa considerada:** manter a consulta por mensalidade e apenas elevar limites ou cachear no frontend. Rejeitada porque não reduz o trabalho no backend e não trata a causa estrutural do volume de consultas.

### Tratar HTTP 429 sem ocultar a falha

Exibir uma mensagem específica para o limite temporário e manter os dados financeiros existentes quando a atualização falhar. Não executar repetição automática; a tentativa seguinte será uma ação explícita do usuário após aguardar.

**Alternativa considerada:** repetir a requisição automaticamente com backoff. Rejeitada para não amplificar a carga nem repetir gravações de resultado incerto.

## Risks / Trade-offs

- **[Risco]** A consolidação altera a forma de associar pagamentos e mensalidades. **→ Mitigação:** cobrir mensalidades pagas, pendentes, atrasadas e pagamentos corrigidos com testes; preservar o shape existente e validar o XanoScript.
- **[Risco]** O limite 429 pode ser imposto pela plataforma ou por configuração do workspace, não somente pela carga do endpoint. **→ Mitigação:** reduzir chamadas concorrentes e trabalho interno, manter mensagem clara e não alterar limites sem revisão autorizada.
- **[Trade-off]** Sem retry automático, o usuário precisa acionar novamente a atualização após aguardar. Isso evita repetição de operações financeiras e é preferível a uma falha silenciosa.

## Plano de migração

1. Implementar os guards e as mensagens específicas no frontend; adicionar testes.
2. Otimizar o endpoint Xano de mensalidades, validar XanoScript e revisar o diff.
3. Executar `xano workspace push --dry-run` e solicitar aprovação explícita antes de qualquer push real.
4. Após aprovação, publicar somente os arquivos financeiros incluídos e validar o carregamento com mensalidades pendentes e pagas.
5. Se a mudança Xano precisar ser revertida, restaurar a consulta anterior sem alterar registros financeiros; manter no frontend os guards e o tratamento de HTTP 429.
