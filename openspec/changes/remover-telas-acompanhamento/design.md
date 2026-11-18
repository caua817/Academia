# Design

## Contexto

Veja [proposal.md](./proposal.md) para a motivação e os limites do escopo. As funcionalidades estão concentradas em uma página/state Reflex de acompanhamento, rotas registradas em `academia/academia.py`, cliente Xano, endpoints e funções na pasta `xano/`, além de testes específicos. A árvore de trabalho já contém alterações não relacionadas e arquivos não rastreados dessas funcionalidades; a implementação deverá preservar tais alterações até confirmar quais arquivos pertencem exclusivamente à remoção.

## Objetivos / Não objetivos

**Objetivos:**

- Retirar páginas, links de navegação, eventos de carregamento, estado de acompanhamento e operações exclusivas de exercícios, fichas e avaliações.
- Remover endpoints Xano locais exclusivos somente após confirmar que nenhuma tela/capacidade mantida os utiliza.
- Manter os dados persistidos e todas as funcionalidades fora do escopo intactos.

**Não objetivos:**

- Excluir tabelas, registros, histórico ou arquivos remotos no Xano.
- Fazer push ao workspace Xano ou modificar recursos remotos.
- Alterar permissões ou remover telas de gestão de funcionários, alunos, operação ou finanças.
- Publicar o aplicativo ou configurar o hosting dos convites de funcionários, que permanece na change `publicar-frontend-para-convites`.

## Decisões

### Preservar o armazenamento e remover somente a superfície funcional

As tabelas de exercícios, fichas, itens e avaliações e seus registros serão mantidos. Essa escolha evita perda irrecuperável, principalmente de dados de saúde, enquanto remove as páginas e operações que o usuário não quer no aplicativo.

**Alternativas consideradas:** apagar tabelas/dados, rejeitado por ser destrutivo e desnecessário para remover telas; ocultar apenas links, rejeitado porque deixaria rotas e operações ainda acessíveis.

### Conferir referências antes de remover endpoints

Remover endpoints, funções e testes locais apenas quando forem exclusivos das funcionalidades retiradas. Manter compartilhados utilitários, controle de acesso e operações usadas pelas telas que permanecem. Não sincronizar nem publicar mudanças no Xano nesta change.

**Alternativas consideradas:** remover toda a pasta de acompanhamento por nome, rejeitado porque pode conter lógica compartilhada ou alterações preexistentes alheias.

### Separar a conclusão dos convites da remoção do acompanhamento

A correção de convites exige publicar o frontend e configurar `frontend_base_url` no Xano; ela permanece delimitada pela change ativa `publicar-frontend-para-convites` e não será considerada concluída por remover as outras telas.

## Riscos / Trade-offs

- **[Risco]** Remover um utilitário compartilhado pode quebrar outras páginas. **→ Mitigação:** rastrear referências antes de excluir módulos ou endpoints e executar testes de regressão.
- **[Risco]** Registros existentes deixam de ter uma interface de consulta. **→ Mitigação:** preservar os dados no Xano; nenhuma exclusão remota será feita.
- **[Risco]** Alterações preexistentes não rastreadas podem ser removidas por engano. **→ Mitigação:** revisar `git status` e diffs antes de cada exclusão, limitando-a a artefatos identificados como exclusivos.

## Plano de migração

1. Identificar referências e separar os componentes e endpoints exclusivos dos compartilhados.
2. Remover as rotas, links, componentes, estados, clientes, endpoints e testes exclusivos.
3. Executar testes direcionados e a compilação Reflex; verificar que as páginas e operações remanescentes continuam funcionais.
4. Preservar tabelas e registros no Xano. Nenhum push ou operação remota faz parte desta mudança.
5. Se houver rollback, restaurar os arquivos de interface e endpoints via controle de versão; os dados preservados continuam disponíveis.
