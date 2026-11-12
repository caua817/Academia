# Design

## Context

O login Reflex atualmente também expõe um modal de cadastro e chama `POST /auth/signup`. O endpoint Xano correspondente é público, cria um usuário com papel `member` e retorna um token. A change `gestao-de-funcionarios` planeja convites pela interface, mas ainda não implementa o provisionamento administrativo no backend.

## Goals / Non-Goals

**Goals:**

- Remover a auto inscrição da interface.
- Tornar impossível criar contas ou emitir tokens pelo endpoint legado de cadastro.
- Preservar login, perfis e registros de contas já existentes.

**Non-Goals:**

- Implementar convite, ativação ou criação administrativa de contas.
- Remover o papel `member`, migrar usuários existentes ou conceder papel `admin` a qualquer conta.
- Alterar permissões de outras APIs ou resolver a autorização runtime de planos e matrículas.

## Decisions

- Desativar completamente o endpoint legado, em vez de simplesmente escondê-lo na interface ou convertê-lo em um endpoint de cadastro administrativo. O frontend não é uma fronteira de segurança, e o endpoint atual não tem fluxo de convite nem regras para provisionar funcionários.
- Remover do estado e da tela de login o modal, os campos e a chamada HTTP de cadastro. Manter as validações e o fluxo de login sem alterações funcionais.
- Não remover a enumeração `member` nem alterar registros existentes: isso exigiria uma migração separada e poderia afetar contas já criadas. A API legado deve negar chamadas com ou sem token e não deve criar conta nem emitir token.
- Deixar a criação de novas contas indisponível no app até uma change separada entregar convite e ativação autorizados no backend. Não solicitar, gerar ou compartilhar senhas de funcionários por um fluxo manual improvisado.

## Risks / Trade-offs

- [Indisponibilidade temporária de novas contas] → Preservar as contas existentes; entregar o provisionamento administrativo por convite em change própria antes de cadastrar novos funcionários.
- [O endpoint pode continuar ativo no workspace enquanto a alteração local não for publicada] → Não considerar o risco resolvido pela remoção do botão; revisar o dry-run e obter aprovação do grupo antes do push real, depois validar o runtime.
- [Chamadas de versões antigas do app ainda podem atingir a rota] → Desativar a API no backend, independentemente da versão do frontend.

## Migration Plan

1. Consultar a documentação e validar a alteração Xano; revisar o diff e executar `xano workspace push --dry-run`.
2. Após aprovação explícita do grupo, publicar a desativação da rota no Xano antes de publicar o frontend.
3. Confirmar no runtime que chamadas diretas ao endpoint não criam conta nem retornam token, e verificar que contas existentes continuam autenticando.
4. Publicar o frontend sem a opção de cadastro e verificar o login no navegador.

Rollback não deve reativar o cadastro público. Se a alteração do Xano falhar, manter o cadastro indisponível e corrigir a rota antes de liberar a interface.
