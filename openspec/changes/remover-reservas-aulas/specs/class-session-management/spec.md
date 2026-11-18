# Spec Delta

## MODIFIED Requirements

### Requirement: A agenda distingue sessões disponíveis e estados vazios

O sistema SHALL apresentar sessões com modalidade, instrutor, início, término, local, capacidade configurada e situação, distinguindo carregamento, lista vazia e falha da API. A interface SHALL NOT apresentar contagem de reservas nem ocupação derivada de reservas.

#### Scenario: Consultar agenda
- **WHEN** um usuário `admin` consulta a agenda em um período
- **THEN** a interface apresenta os dados das sessões e sua capacidade configurada sem exibir contagem ou ocupação de reservas

#### Scenario: Agenda sem sessões
- **WHEN** não há sessões no período consultado
- **THEN** a interface informa que não existem sessões sem apresentar a ausência como falha
