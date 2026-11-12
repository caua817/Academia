# Continuidade do projeto

Este arquivo registra o estado conhecido do projeto e orienta outro Copilot a continuar o trabalho sem perder o contexto. Atualize-o conforme as entregas forem concluídas.

## Objetivo

Concluir o sistema de gerenciamento de academia conforme o escopo em [project-overview.md](./project-overview.md), respeitando o modelo de domínio em [domain-model.md](./domain-model.md) e o fluxo OpenSpec definido em [AGENTS.md](../AGENTS.md).

## Estado verificado em 27/10/2026

- Branch local: `apresentacao/2026-10-26`.
- Pull request #1 aberta para `main`: <https://github.com/caua817/Academia/pull/1>.
- A PR contém 2 commits e 58 arquivos alterados; ainda não foi integrada à `main`.
- Há um `reflex.log` não rastreado localmente; ele não faz parte da PR.
- Não compartilhar nem versionar `.env`, tokens ou credenciais.
- O projeto usa Reflex no frontend e Xano no backend. Regras de negócio e autorização devem permanecer no backend.

## OpenSpec: changes existentes

| Change | Estado observado | Próximo trabalho |
|---|---:|---|
| `corrigir-login-cadastro` | Concluída, 6/6 tarefas | Conferir e arquivar pelo fluxo OpenSpec quando apropriado. |
| `gestao-de-planos-matriculas` | Em andamento, 9/12 tarefas | Concluir as verificações de runtime Xano (planos e matrículas) e o fluxo demonstrativo no navegador; ver tarefas 1.3, 2.3 e 5.2 em `openspec/changes/gestao-de-planos-matriculas/tasks.md`. |
| `gestao-de-funcionarios` | Em andamento, 0/8 tarefas | Implementar e verificar conforme `proposal.md`, `design.md`, `specs/employee-management/spec.md` e `tasks.md`. Confirmar previamente os contratos/endpoints necessários no Xano; a change delimita o trabalho ao frontend e testes locais. |

Existem também três changes arquivadas: `connect-reflex-xano`, `2026-10-24-aprimorar-tela-autenticacao` e `2026-10-24-gestao-de-alunos`.

As specs consolidadas atualmente listadas são `authentication` e `student-management`. Não presumir que uma change esteja implementada apenas por estar publicada ou especificada: verificar código, tarefas e testes.

## Escopo do projeto ainda previsto

O overview divide o projeto em três fases:

1. **Núcleo:** autenticação/perfis, alunos, planos, matrículas, mensalidades/pagamentos e check-in.
2. **Operação:** modalidades, aulas, reservas, funcionários/instrutores e relatórios.
3. **Acompanhamento do aluno:** fichas de treino, exercícios e avaliações físicas.

As changes existentes cobrem parte desse escopo, mas ainda não há changes ativas identificadas para mensalidades/pagamentos, check-in, modalidades/aulas/reservas, relatórios, treinos e avaliações físicas. Antes de implementar essas áreas, explorar requisitos, decisões de negócio pendentes e dependências, e criar propostas OpenSpec revisáveis. Não inventar regras para inadimplência, trancamento/cancelamento, permissões ou acesso a dados sensíveis.

## Próximos passos sugeridos

1. Confirmar a integração da PR #1 com o grupo; não fazer merge sem aprovação.
2. Retomar `gestao-de-planos-matriculas`: verificar se os endpoints já estão publicados no Xano e concluir as tarefas pendentes usando dados sintéticos. Não fazer push real ao Xano sem aprovação explícita.
3. Implementar `gestao-de-funcionarios` conforme a change aprovada, validando contratos e dependências do backend sem ampliar o escopo sem aprovação.
4. Propor changes OpenSpec para as funcionalidades restantes do escopo, em entregas pequenas e ordenadas por dependência.
5. Para cada change: revisar a proposta e as decisões de negócio, implementar somente o que está nas tarefas, executar testes e validações relevantes, atualizar tarefas e arquivar quando concluída.
6. Ao final, conferir os critérios de conclusão com o grupo e atualizar este arquivo.

## Instruções para o próximo Copilot

- Leia primeiro `AGENTS.md`, `docs/project-overview.md`, `docs/domain-model.md`, `openspec/config.yaml`, as specs existentes e os artefatos da change que será trabalhada.
- Consulte o estado real do GitHub, da branch e das changes antes de agir; este resumo pode ficar desatualizado.
- Siga o OpenSpec: Explore → Propose → Review → Apply → Archive. Não implemente algo sem cobertura por tarefas de uma change atual aprovada.
- Preserve alterações locais e não inclua arquivos não relacionados na PR.
- Use Reflex exclusivamente no frontend; consulte e valide a sintaxe XanoScript conforme as instruções do projeto.
- Nunca exponha ou versione `.env`, tokens, credenciais ou dados reais de alunos. Use dados sintéticos nos testes.
- Execute verificações relevantes antes de marcar tarefas como concluídas.
