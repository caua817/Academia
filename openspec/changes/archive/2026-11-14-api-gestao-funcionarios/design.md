# Design

## Contexto

Veja [proposal.md](./proposal.md) para motivação e escopo. A capability consolidada `employee-management` já define os comportamentos esperados e o frontend usa os caminhos do contrato registrado no design da change arquivada de gestão de funcionários.

No workspace versionado, a tabela `user` já aceita os perfis `admin`, `member`, `recepcionista` e `instrutor`, e `GET /auth/me` já retorna a identidade autenticada. Os arquivos de endpoints de funcionários não existem. O cliente Reflex espera uma lista e detalhes de contas, convite por e-mail, edição e alteração de situação. Os endpoints atuais de operação reutilizam `Quick Start/enforce_role`, cuja hierarquia declara apenas `admin` e `member`.

## Objetivos / Não objetivos

**Objetivos:**

- Implementar o contrato já consumido pelo frontend, sem alterar seus caminhos ou payloads.
- Usar a tabela `user` existente e preservar contas inativas para manter histórico.
- Autorizar cada operação no backend e não retornar credenciais nem dados internos de autenticação.
- Reutilizar o fluxo seguro de link de uso único existente para que o convidado defina sua própria senha.

**Não objetivos:**

- Reintroduzir cadastro público ou permitir que o frontend seja a fronteira de autorização.
- Criar entidade de RH, redefinir regras de acesso dos módulos existentes ou modificar a interface Reflex.
- Publicar alterações no workspace remoto sem revisão e aprovação explícitas.

## Decisões

### Manter a tabela e os caminhos HTTP existentes

Os funcionários são contas da tabela `user`; não será criada uma tabela paralela. A API continuará no grupo `Authentication` e seguirá os caminhos já usados pelo cliente:

| Operação | Método e caminho | Retorno operacional |
|---|---|---|
| Listar funcionários | `GET /funcionarios` | Lista de contas com perfil de funcionário; excluir `member`. |
| Consultar funcionário | `GET /funcionarios/detalhes/{funcionario_id}` | Registro individual para edição. |
| Convidar funcionário | `POST /funcionarios/convites` | Entrada `name`, `email`, `role`; conta criada e convite solicitado. |
| Editar funcionário | `PUT /funcionarios/atualizar/{funcionario_id}` | Entrada `name`, `email`, `role`; dados operacionais atualizados. |
| Desativar funcionário | `PATCH /funcionarios/desativar/{funcionario_id}` | Conta preservada com situação inativa. |
| Reativar funcionário | `PATCH /funcionarios/ativar/{funcionario_id}` | Conta preservada com situação ativa. |

As respostas devem conter somente `id`, `name`, `email`, `role`, `situacao` e, quando houver fonte confiável, `status_convite`. Não retornar `password`, `password_reset`, tokens ou outros campos internos. O campo de convite é opcional no contrato atual; não criar um estado derivado que não possa ser sustentado pelos dados.

### Autorizar todas as rotas no backend

Cada endpoint exigirá autenticação e autorização explícita de `admin`, inclusive detalhes e alterações de status. Reutilizar `Quick Start/enforce_role` somente após validar, pela documentação do Xano e por testes, que perfis existentes `recepcionista`, `instrutor` e `member` são sempre negados. Se necessário, ajustar a hierarquia compartilhada para representar todos os perfis abaixo de `admin`, preservando o acesso administrativo atual dos demais endpoints.

Uma resposta 401 deve continuar sinalizando sessão inválida; uma resposta 403 deve negar a operação sem incluir dados de funcionários. A autorização não depende de menu, estado ou rota do Reflex.

### Convidar sem criar ou transmitir uma senha

O endpoint de convite valida nome, e-mail e o enum `admin`, `recepcionista` ou `instrutor`, rejeita e-mail já cadastrado e cria a conta sem senha definida pelo administrador. Deve usar o mecanismo existente de link de uso único/expiração e envio de e-mail para que o funcionário defina a própria senha. A construção exata do token e do link deve seguir a documentação atual do Xano; não armazenar credenciais em texto simples nem expor token na resposta.

Antes de habilitar o envio, validar que o link leva a uma experiência utilizável de definição de senha para um usuário sem senha. O fluxo atual de redefinição é uma referência técnica, não prova suficiente de que o destino visual do convite está correto. Se ele não atender ao caso, interromper a publicação e separar a experiência ausente em uma change própria, sem habilitar cadastro público.

### Preservar edição validada e desativação reversível

Atualizações aceitam apenas os campos do contrato e os perfis de funcionário permitidos. Ativação e desativação atualizam `situacao`; não removem a conta. IDs inexistentes, dados inválidos e conflitos de e-mail devem retornar erros HTTP explícitos compatíveis com o cliente.

### Não alterar os requisitos consolidados

A change não cria delta spec porque a capability `employee-management` já descreve os comportamentos. A configuração declara `skip_specs: true` para evitar duplicar ou divergir requisitos durante a implementação.

## Riscos / Trade-offs

- **[Risco]** O helper de autorização é compartilhado por vários endpoints e lista atualmente apenas `admin` e `member`. **→ Mitigação:** cobrir explicitamente todos os perfis existentes, confirmar que apenas `admin` é autorizado e executar validações para os endpoints já protegidos antes da publicação.
- **[Risco]** Os arquivos locais não provam que o workspace publicado está no mesmo estado; a sondagem sem autenticação por `HEAD` retornou 404, mas não valida sozinha os fluxos protegidos. **→ Mitigação:** fazer `xano workspace pull` conforme o procedimento do projeto antes de implementar e comparar com o workspace de destino.
- **[Risco]** O fluxo existente de redefinição pode não fornecer uma página válida de configuração inicial de senha. **→ Mitigação:** validar o destino e o fluxo ponta a ponta sem credenciais reais antes de ativar convites; não enviar links demonstrativos ou inutilizáveis.
- **[Risco]** Listas ou detalhes podem vazar campos internos da tabela `user`. **→ Mitigação:** construir respostas com allowlist explícita e testar ausência de senha, token e objeto de redefinição.

## Plano de migração

1. Sincronizar e inspecionar o workspace Xano de acordo com as instruções do projeto.
2. Consultar a documentação do Xano Developer MCP para os recursos XanoScript necessários; implementar as rotas e ajustes mínimos.
3. Validar autorização, payloads, respostas allowlist, duplicidade, convite, definição de senha e preservação de registros.
4. Revisar `git diff` e executar `xano workspace push --dry-run`. Não realizar push real sem aprovação explícita do grupo.
5. Se o rollback for necessário, desabilitar/remover somente os novos endpoints após verificar dependências; não excluir contas nem dados existentes.

## Questões em aberto

Nenhuma decisão de escopo é deixada para a implementação. A validade do fluxo e do destino de configuração de senha é um critério de liberação: se o mecanismo disponível no Xano não atender, a implementação deve parar antes de publicar convites.
