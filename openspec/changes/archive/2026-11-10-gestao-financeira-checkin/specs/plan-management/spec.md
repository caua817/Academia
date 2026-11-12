# Spec Delta

## ADDED Requirements

### Requirement: O valor do plano representa uma parcela mensal

O sistema SHALL interpretar o valor cadastrado em um plano como o valor integral de cada mensalidade, independentemente da duração em meses do plano.

#### Scenario: Consultar o valor do plano
- **WHEN** um usuário `admin` consulta um plano
- **THEN** a interface identifica o valor apresentado como valor mensal

#### Scenario: Atualizar plano após matrícula existente
- **WHEN** o valor mensal de um plano é alterado após a criação de uma matrícula
- **THEN** as mensalidades da matrícula existente preservam o valor mensal contratado
