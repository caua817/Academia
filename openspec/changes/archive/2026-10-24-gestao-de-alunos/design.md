# Design: Gestão de alunos

## Context

Ver [proposal.md](./proposal.md) para a motivação e o escopo. O app já usa Reflex e `httpx`; o painel faz uma chamada a `/alunos`, mas o workspace versionado não contém tabela nem endpoints de alunos. O cliente atual também converte qualquer falha em uma lista vazia. No Xano, `user.role` contém `admin` e `member`, o cadastro atual cria usuários como `member`, e existe a função de exemplo `Quick Start/enforce_role`.

## Goals / Non-Goals

**Goals:**
- Adicionar uma gestão de alunos ponta a ponta usando Reflex e Xano.
- Preservar o limite de acesso `admin` definido na spec, validado no backend.
- Manter falhas de API visíveis e registros de alunos recuperáveis após desativação.

**Non-Goals:**
- Alterar autenticação, cadastro de funcionários ou a hierarquia atual de perfis.
- Dar acesso a `member`, recepcionistas ou instrutores até que o grupo defina como esses perfis serão representados no Xano.
- Impor unicidade de CPF, criar regras de matrículas ou antecipar outras entidades da Fase 1.

## Decisions

### Entidade de aluno separada da conta de usuário

Criar uma tabela própria de alunos, distinta da tabela `user`, com campos de domínio para nome, CPF, data de nascimento, contato, endereço e situação ativa/inativa. A operação de desativação altera a situação e nunca apaga fisicamente o registro.

CPF permanece opcional e sem regra de unicidade nesta change, pois essa decisão está marcada para validação no modelo de domínio. O nome é obrigatório; os demais campos são opcionais até decisão do grupo.

### Autorização no Xano

Os endpoints de alunos exigem autenticação e validam `admin` em cada operação, incluindo leitura. O frontend pode ocultar ou bloquear a navegação para outros perfis, mas essa apresentação não substitui a autorização no backend. Reutilizar a função de validação de perfil existente se sua semântica servir; validar qualquer ajuste de XanoScript com a documentação/ferramentas do Xano antes de considerar o código pronto.

Alternativa descartada: permitir acesso a `member` por ser o perfil criado pelo cadastro atual. Isso exporia dados pessoais a contas que não foram definidas como funcionários autorizados.

### API e tratamento de erros

Adicionar operações Xano para listar, consultar detalhes, criar, atualizar e desativar alunos. A listagem retorna apenas identificador, nome, contato, e-mail e situação; CPF, data de nascimento e endereço só são devolvidos pela consulta autenticada de detalhes, necessária para preencher o formulário de edição. Centralizar chamadas HTTP no cliente existente; preservar códigos/mensagens de erro úteis para o estado Reflex e não converter falhas em respostas vazias. Exibir na tabela apenas o mínimo necessário; mascarar CPF se vier a ser incluído na listagem e não exibir endereço nela.

### Sessão autenticada no Reflex

Manter o token recebido no estado servidor por usuário (`LoginState`), em vez de gravá-lo em armazenamento genérico do navegador. A tela de alunos obtém o estado de login associado à mesma sessão do Reflex e redireciona para o login quando não há token. Ao sair, limpar o token e as credenciais do estado antes de redirecionar. Se uma consulta autenticada falhar, limpar a lista em memória para não continuar mostrando dados potencialmente desatualizados.

### Interface Reflex

Adicionar uma área de alunos integrada à navegação atual, com tabela, pesquisa, formulário de cadastro/edição e confirmação antes de desativar. Manter estados visíveis de carregamento, vazio, sucesso e erro, preservando a identidade visual existente sem adicionar dependências enquanto os componentes Reflex atuais forem suficientes.

### Workspace Xano remoto

Versionar e validar mudanças localmente primeiro. Executar `xano workspace push --dry-run` após revisar o diff. Não executar push real sem aprovação explícita do grupo.

## Risks / Trade-offs

- `[Risco]` O perfil `admin` pode não representar o acesso esperado para recepcionistas e instrutores. → `[Mitigação]` Restringir esta entrega a `admin` e tratar o alinhamento dos perfis em change posterior.
- `[Risco]` A regra de unicidade do CPF segue indefinida. → `[Mitigação]` Não rejeitar cadastros por duplicidade nesta change; registrar a decisão pendente para uma evolução posterior.
- `[Risco]` A API remota pode não refletir os arquivos locais antes do envio aprovado. → `[Mitigação]` Não anunciar integração remota concluída até a aprovação e execução do push.

## Migration Plan

1. Criar tabela e endpoints de alunos no código Xano local e validar XanoScript.
2. Implementar e testar o cliente e a interface Reflex contra respostas esperadas, incluindo erros de autenticação.
3. Revisar o diff e executar dry-run do push; solicitar aprovação do grupo antes de qualquer sincronização real.
4. Para rollback, retirar a navegação e os componentes do frontend e reverter os endpoints/tabela em uma alteração rastreável, sem apagar registros de alunos já criados.

## Open Questions

- A unicidade do CPF e os perfis de funcionário além de `admin` continuam pendentes de decisão do grupo, sem bloquear esta entrega restrita a administradores.
