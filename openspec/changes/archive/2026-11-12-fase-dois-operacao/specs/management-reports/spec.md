# Spec Delta

## Purpose

Permite que administradores acompanhem indicadores agregados da academia para um período, reunindo matrículas, situação financeira, frequência e ocupação de aulas.

## ADDED Requirements

### Requirement: Administradores podem consultar relatórios operacionais agregados

O sistema SHALL apresentar a administradores indicadores agregados de matrículas ativas, pagamentos e mensalidades atrasadas, check-ins e ocupação de sessões no período selecionado.

#### Scenario: Consultar indicadores do período
- **WHEN** um usuário `admin` consulta os relatórios para um período válido
- **THEN** o sistema apresenta matrículas ativas na data final, valores pagos no intervalo, mensalidades vencidas e não pagas até a data final, check-ins e ocupação de sessões no período

#### Scenario: Exibir situação sem atividade
- **WHEN** não há registros para uma métrica no período selecionado
- **THEN** o sistema apresenta zero para essa métrica sem tratá-la como falha

#### Scenario: Rejeitar período inválido
- **WHEN** um usuário `admin` envia datas inválidas ou uma data inicial posterior à final
- **THEN** o sistema rejeita a consulta e informa o erro sem apresentar dados de outro período

#### Scenario: Usuário sem perfil administrativo consulta relatórios
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta consultar relatórios
- **THEN** o backend rejeita a solicitação sem revelar dados agregados protegidos

### Requirement: Relatórios não expõem dados pessoais de alunos

O sistema SHALL retornar e apresentar somente métricas agregadas necessárias, sem nomes, contatos, documentos ou endereços de alunos.

#### Scenario: Consultar relatório agregado
- **WHEN** um usuário `admin` abre ou atualiza um relatório
- **THEN** a resposta contém somente totais e percentuais operacionais, sem identificadores ou dados pessoais de alunos

### Requirement: A interface de relatórios distingue carregamento, vazio e falha

O sistema SHALL diferenciar carregamento, resultados sem atividade, sucesso e falhas da API ao consultar relatórios.

#### Scenario: Falha ao carregar relatórios
- **WHEN** a API rejeita ou não conclui uma consulta
- **THEN** a interface informa a falha e não apresenta os indicadores como se fossem resultados válidos
