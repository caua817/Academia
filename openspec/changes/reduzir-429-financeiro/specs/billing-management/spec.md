# Spec Delta

## MODIFIED Requirements

### Requirement: A interface financeira distingue sucesso, vazio e falha

O sistema SHALL diferenciar carregamento, ausência de mensalidades, sucesso e falhas da API ao consultar mensalidades, registrar pagamentos ou corrigir lançamentos. Quando a API responder HTTP 429, a interface SHALL informar que o limite temporário de solicitações foi atingido, orientar o usuário a aguardar antes de tentar novamente, preservar os dados financeiros já carregados e não apresentar confirmação de sucesso para a operação rejeitada.

#### Scenario: Falha ao registrar pagamento
- **WHEN** a API rejeita ou não conclui o registro ou a correção de um pagamento
- **THEN** a interface informa a falha e não apresenta confirmação de sucesso

#### Scenario: Limite temporário de requisições financeiras
- **WHEN** a API responde HTTP 429 ao consultar dados financeiros ou executar uma operação financeira
- **THEN** a interface explica que o limite temporário foi atingido, orienta a aguardar e tentar novamente, mantém os dados previamente carregados e não mostra sucesso para a operação rejeitada

#### Scenario: Operação financeira repetida durante carregamento ou gravação
- **WHEN** o usuário aciona novamente um carregamento, registro ou correção enquanto a mesma operação está em andamento
- **THEN** o sistema não inicia uma segunda solicitação concorrente e mantém o estado da primeira operação
