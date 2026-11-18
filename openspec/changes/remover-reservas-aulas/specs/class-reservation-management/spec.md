# Spec Delta

## ADDED Requirements

### Requirement: O aplicativo Reflex não expõe a gestão de reservas de aulas

O aplicativo Reflex SHALL NOT oferecer navegação, rota, tela ou ação para consultar, criar, cancelar ou registrar o resultado de reservas de aulas. SHALL NOT enviar dados de reservas ou métricas de ocupação derivados de reservas ao estado visível da interface. A remoção da interface SHALL NOT excluir registros nem alterar os endpoints existentes no Xano.

#### Scenario: Navegação sem opção de reservas
- **WHEN** um funcionário navega pelo aplicativo
- **THEN** o menu não apresenta uma opção de reservas de aulas

#### Scenario: Acesso direto à rota antiga
- **WHEN** alguém abre diretamente a rota `/reservas`
- **THEN** o aplicativo não apresenta a tela de gestão nem dados ou ações de reserva

#### Scenario: Histórico e APIs Xano preservados
- **WHEN** a interface de reservas é removida
- **THEN** os registros de reserva existentes e os endpoints Xano permanecem intactos, sem exclusão ou migração de dados

## MODIFIED Requirements

### Requirement: A consulta de reservas apresenta estado e ocupação corretos

O Xano SHALL manter a API autenticada existente para que administradores autorizados consultem reservas por sessão e recebam os registros e a ocupação atual conforme o contrato já publicado. O aplicativo Reflex SHALL NOT chamar essa API nem apresentar suas respostas em páginas, relatórios ou estado visível ao cliente.

#### Scenario: Consultar reservas da sessão
- **WHEN** um administrador autorizado consulta reservas por meio do endpoint Xano existente
- **THEN** a API mantém o contrato e os dados de resposta atuais, incluindo reservas e quantidade de vagas confirmadas, sem alteração causada pela remoção da interface Reflex

#### Scenario: Falha ao consultar reservas
- **WHEN** o endpoint Xano rejeita ou não conclui uma consulta
- **THEN** o endpoint mantém sua resposta de erro atual e o aplicativo Reflex não apresenta uma tela de reservas ou converte a falha em dados vazios
