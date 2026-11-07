# Spec Delta

## Purpose

Permite que administradores acompanhem as mensalidades geradas pelas matrículas e registrem pagamentos integrais com histórico rastreável, preservando a integridade dos registros financeiros.

## ADDED Requirements

### Requirement: Administradores podem consultar mensalidades e sua situação

O sistema SHALL permitir que usuários autenticados com perfil `admin` consultem mensalidades com aluno, matrícula, competência, valor, vencimento e situação financeira.

#### Scenario: Consultar mensalidades
- **WHEN** um usuário `admin` abre a gestão financeira
- **THEN** o sistema apresenta as mensalidades e suas situações sem expor dados cadastrais sensíveis desnecessários

#### Scenario: Mensalidade vence sem pagamento
- **WHEN** a data atual passa da data de vencimento de uma mensalidade não paga
- **THEN** o sistema a apresenta como atrasada, sem aplicar juros ou multa

#### Scenario: Usuário sem perfil administrativo consulta mensalidades
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta consultar mensalidades
- **THEN** o backend rejeita a solicitação sem revelar dados financeiros ou pessoais

### Requirement: Administradores podem registrar o pagamento integral de uma mensalidade

O sistema SHALL permitir que usuários `admin` registrem o pagamento integral de uma mensalidade pendente ou atrasada, mantendo valor, data, forma de pagamento e usuário responsável pelo registro.

#### Scenario: Pagamento integral registrado
- **WHEN** um usuário `admin` registra o valor integral de uma mensalidade pendente ou atrasada
- **THEN** o sistema persiste o pagamento e apresenta a mensalidade como paga

#### Scenario: Pagamento parcial ou valor divergente
- **WHEN** um usuário `admin` tenta registrar valor menor ou diferente do total devido
- **THEN** o sistema rejeita a operação e mantém a mensalidade e o histórico sem alteração

#### Scenario: Pagamento duplicado
- **WHEN** um usuário `admin` tenta registrar outro pagamento para uma mensalidade já paga
- **THEN** o sistema rejeita a operação sem criar um segundo pagamento ativo

#### Scenario: Usuário sem perfil administrativo registra pagamento
- **WHEN** uma pessoa sem autenticação ou com perfil diferente de `admin` tenta registrar um pagamento
- **THEN** o backend rejeita a solicitação sem alterar registros

### Requirement: Correções financeiras preservam o histórico

O sistema SHALL preservar mensalidades e pagamentos registrados, permitindo corrigir um pagamento por cancelamento ou estorno rastreável, com motivo, responsável e data, sem apagar fisicamente o registro original.

#### Scenario: Pagamento corrigido
- **WHEN** um usuário `admin` corrige um pagamento registrado
- **THEN** o sistema mantém o lançamento original com sua situação de cancelado ou estornado e registra os dados da correção

#### Scenario: Correção sem motivo
- **WHEN** um usuário `admin` tenta cancelar ou estornar um pagamento sem informar o motivo
- **THEN** o sistema rejeita a correção e mantém os registros sem alteração

### Requirement: A interface financeira distingue sucesso, vazio e falha

O sistema SHALL diferenciar carregamento, ausência de mensalidades, sucesso e falhas da API ao consultar mensalidades, registrar pagamentos ou corrigir lançamentos.

#### Scenario: Falha ao registrar pagamento
- **WHEN** a API rejeita ou não conclui o registro ou a correção de um pagamento
- **THEN** a interface informa a falha e não apresenta confirmação de sucesso
