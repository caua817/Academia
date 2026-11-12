# Spec Delta

## Purpose

Permite registrar e consultar avaliações físicas ao longo do tempo, tratando medidas e observações como dados sensíveis e protegendo-as por autorização no backend.

## ADDED Requirements

### Requirement: Administradores e instrutores podem registrar avaliações físicas

O sistema SHALL permitir que usuários `admin` e `instrutor` registrem uma avaliação para um aluno com data, peso em quilogramas, altura em centímetros, medidas corporais identificadas e instrutor responsável; observações SHALL ser opcionais.

#### Scenario: Registrar avaliação válida
- **WHEN** um usuário autorizado registra uma avaliação com aluno, data, valores positivos de peso e altura e instrutor responsável
- **THEN** o sistema persiste a avaliação e a disponibiliza no histórico do aluno

#### Scenario: Rejeitar dados inválidos
- **WHEN** uma avaliação não informa campos obrigatórios, contém peso ou altura não positivos ou medidas com valor inválido
- **THEN** o sistema rejeita a solicitação sem criar um registro

#### Scenario: Registrar avaliação pelo instrutor responsável
- **WHEN** um instrutor registra uma avaliação
- **THEN** o sistema associa a avaliação ao instrutor autenticado e não aceita que o cliente substitua essa identidade

### Requirement: Avaliações físicas preservam histórico e confidencialidade

O sistema SHALL permitir que administradores e instrutores consultem o histórico de avaliações e SHALL impedir exclusão física de avaliações.

Ao corrigir uma avaliação, o sistema SHALL criar um novo registro vinculado ao original e exigir o motivo da correção; o registro original SHALL permanecer consultável.

#### Scenario: Consultar histórico de avaliações
- **WHEN** um usuário autorizado consulta as avaliações de um aluno
- **THEN** o sistema apresenta as avaliações em ordem cronológica com o instrutor responsável

#### Scenario: Corrigir uma avaliação
- **WHEN** um usuário autorizado identifica um erro em uma avaliação já registrada
- **THEN** o sistema exige o motivo, registra uma nova avaliação vinculada à original e mantém ambos os registros consultáveis sem sobrescrever o histórico

#### Scenario: Usuário sem perfil autorizado consulta avaliações
- **WHEN** uma pessoa sem sessão ou com perfil `recepcionista` ou `member` tenta consultar, registrar ou corrigir avaliações
- **THEN** o backend rejeita a solicitação sem revelar dados de saúde nem alterar registros

### Requirement: A interface limita a exposição de dados de saúde

O sistema SHALL apresentar os dados de avaliações somente nas telas de acompanhamento autorizadas e SHALL limpar esses dados após encerramento da sessão ou resposta HTTP 401/403.

#### Scenario: Acesso não autorizado ou sessão expirada
- **WHEN** a API rejeita a consulta de avaliações por falta de autorização ou sessão válida
- **THEN** a interface não apresenta dados de saúde, informa a falha e redireciona ao login quando a sessão expirou
