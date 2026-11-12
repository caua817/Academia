# Proposal

## Why

O sistema ainda não permite que a equipe acompanhe de forma estruturada os treinos prescritos e a evolução física dos alunos. A Fase 3 completa esse acompanhamento com histórico organizado, mantendo os dados de saúde protegidos no backend.

## What Changes

- Criar um catálogo de exercícios com nome, grupo muscular, descrição, equipamento e situação, preservando exercícios referenciados por fichas existentes.
- Permitir que administradores e instrutores criem e consultem fichas de treino por aluno, com instrutor responsável, objetivo, validade e exercícios ordenados com séries, repetições e carga sugerida.
- Permitir o registro e a consulta de avaliações físicas com data, peso, altura, medidas, observações e instrutor responsável, preservando o histórico.
- Autorizar administradores e todos os instrutores a consultar e manter fichas de treino e avaliações físicas; negar acesso a recepcionistas. Alunos continuam sem acesso ao sistema nesta versão.
- Implementar regras de autorização e persistência no Xano e as telas correspondentes exclusivamente em Reflex.

## Capabilities

### New Capabilities

- `exercise-catalog`: manter o catálogo de exercícios utilizado pelas fichas.
- `training-plan-management`: criar, consultar e preservar fichas de treino dos alunos.
- `physical-assessment-management`: registrar e consultar avaliações físicas como dados sensíveis.

### Modified Capabilities

Nenhuma. As funcionalidades da Fase 3 serão especificadas como novas capabilities; esta change não altera os contratos existentes de autenticação ou cadastro de alunos.

## Impact

- Backend Xano: tabelas, endpoints autenticados, validações e autorização por perfil para exercícios, fichas e avaliações.
- Frontend Reflex: chamadas tipadas no `XanoClient`, páginas de catálogo, fichas e avaliações, com estados de carregamento, vazio, sucesso e erro.
- Testes: regras de negócio, acesso por perfil, histórico, validação de dados e tratamento de falhas no cliente e nas telas.
- Não há dependências novas previstas. O frontend não oferecerá acesso de aluno, e nenhuma autorização dependerá somente da interface.
