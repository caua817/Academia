# Spec Delta

## MODIFIED Requirements

### Requirement: Administradores podem consultar relatórios operacionais agregados

O sistema SHALL apresentar a administradores indicadores agregados de matrículas ativas, pagamentos e mensalidades atrasadas, check-ins e sessões no período selecionado, sem exibir métricas de reservas ou ocupação.

#### Scenario: Consultar indicadores do período
- **WHEN** um usuário `admin` consulta os relatórios para um período válido
- **THEN** o sistema apresenta matrículas ativas na data final, valores pagos no intervalo, mensalidades vencidas e não pagas até a data final, check-ins, quantidade de sessões e capacidade total, sem métricas de reservas ou ocupação

#### Scenario: Exibir situação sem atividade
- **WHEN** não há registros para uma métrica exibida no período selecionado
- **THEN** o sistema apresenta zero para essa métrica sem tratá-la como falha

#### Scenario: Rejeitar período inválido
- **WHEN** um usuário `admin` envia datas inválidas ou uma data inicial posterior à final
- **THEN** o sistema rejeita a consulta e informa o erro sem apresentar dados de outro período

#### Scenario: Usuário sem perfil administrativo consulta relatórios
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta consultar relatórios
- **THEN** o backend rejeita a solicitação sem revelar dados agregados protegidos
