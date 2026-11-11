# Proposal

## Why

A interface Reflex já oferece gestão de funcionários e o `XanoClient` já chama os endpoints correspondentes, mas o pull isolado do workspace Xano publicado não contém essas APIs. Além disso, a tabela `user` não contempla os perfis `recepcionista` e `instrutor` nem uma situação ativa/inativa, impedindo a administração segura de instrutores necessária para a Fase 2.

## What Changes

- Implementar no Xano os endpoints de funcionários já consumidos pelo cliente: listagem, detalhes, convite, edição, ativação e desativação.
- Armazenar perfis e situação de funcionários na conta autenticada, preservando compatibilidade com contas e papéis existentes.
- Aplicar autorização administrativa no backend e impedir que contas inativas iniciem ou usem sessões autenticadas.
- Enviar convite para definição de senha sem solicitar, retornar ou registrar a senha do funcionário.
- Corrigir o cliente HTTP para enviar o token real de sessão no cabeçalho `Authorization` e cobrir esse contrato com testes.
- Manter a tela Reflex existente; não criar uma segunda interface de funcionários nem alterar dados reais ou publicar no Xano sem aprovação explícita.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `employee-management`: garantir que a gestão existente de funcionários tenha suporte efetivo no backend Xano, incluindo perfis, situação e proteção de credenciais.
- `authentication`: bloquear autenticação e operações protegidas para contas inativas.

## Impact

- Tabela `user`, autorização reutilizável e endpoints XanoScript de funcionários e autenticação.
- `XanoClient` e testes do contrato HTTP usado pela tela Reflex existente.
- A publicação no workspace Xano permanece fora desta change sem aprovação explícita; a validação de sincronização será somente por dry-run.
