# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas em `specs/`. A aplicação usa Reflex em `academia/`, com páginas e estado centralizados em módulos Python, e um `XanoClient` para consumir APIs. O backend é XanoScript; `user.role` já inclui `admin`, `instrutor`, `recepcionista` e `member`, enquanto alunos são registros sem autenticação. Não existem tabelas, endpoints ou telas locais para exercícios, fichas ou avaliações.

As avaliações contêm dados de saúde. A política aprovada para esta change permite que administradores e todos os instrutores consultem e mantenham fichas e avaliações; recepcionistas e alunos não têm acesso.

## Goals / Non-Goals

**Goals:**

- Fazer do Xano a autoridade para autorização, validação, persistência e histórico.
- Permitir que administradores e instrutores mantenham fichas e avaliações, identificando o responsável e minimizando dados pessoais exibidos.
- Preservar referências históricas ao desativar exercícios, arquivar fichas e registrar correções de avaliações.

**Non-Goals:**

- Criar login ou portal do aluno.
- Produzir diagnóstico, recomendação clínica, cálculo de IMC ou progressão automática de treino.
- Substituir ou alterar os fluxos existentes de matrícula, cobrança, frequência ou gestão de sessões.

## Decisions

### Separar catálogo, ficha e avaliação em registros relacionados

Manter exercícios em catálogo próprio; representar cada ficha por um registro principal e itens ordenados com exercício, séries, repetições e carga sugerida; e representar cada avaliação como registro independente associado ao aluno e ao responsável. Medidas corporais serão itens identificados com valor e unidade em vez de colunas fixas por região do corpo, permitindo registrar medidas sem alterar o esquema para cada novo tipo.

Alternativa descartada: armazenar os exercícios da ficha ou todo o histórico de avaliações em um único campo livre, pois dificulta validar itens, ordenar exercícios e consultar o histórico.

### Preservar histórico em vez de excluir registros

Exercícios serão desativados e fichas serão arquivadas, sem apagar referências já utilizadas. Avaliações serão append-only: uma correção cria novo registro e mantém o anterior consultável, sem sobrescrita ou exclusão física.

Alternativa descartada: exclusão física ou edição destrutiva de avaliações, que apagaria a evolução registrada. O vínculo explícito entre uma avaliação corrigida e sua versão anterior deve ser registrado para permitir rastreabilidade.

### Aplicar a autorização no backend e restringir dados por necessidade

Cada endpoint verificará autenticação e perfil `admin` ou `instrutor`; não dependerá da navegação Reflex como barreira. O instrutor autenticado será o responsável em operações feitas por instrutores. Quando um administrador registrar em nome de um instrutor, deverá selecionar um instrutor ativo. As APIs de seleção de alunos retornarão somente os campos necessários, sem CPF, contato ou endereço.

Alternativa descartada: reutilizar a barreira exclusivamente administrativa atual ou confiar no perfil e no identificador enviados pelo cliente, pois isso negaria o fluxo autorizado de instrutores ou permitiria falsificação de autoria.

### Isolar os dados sensíveis no estado e nas telas autorizadas

Usar chamadas tipadas no `XanoClient` e estado Reflex próprio para catálogo, fichas e avaliações. Limpar dados de avaliação ao sair da página, encerrar a sessão ou receber 401/403; diferenciar carregamento, vazio e erro. A consulta deve evitar manter em memória informações além das necessárias à tela.

Alternativa descartada: carregar avaliações no painel geral ou reaproveitar listas de alunos com CPF, contato ou endereço, pois amplia desnecessariamente a exposição.

### Construir a interface com os componentes Reflex existentes

Adicionar rotas e navegação Reflex para catálogo de exercícios, fichas e avaliações, reutilizando padrões de formulários, estados de API e confirmação já presentes no projeto. A autorização de rota deve aceitar `admin` e `instrutor` somente para as páginas desta change; as páginas atuais continuam com suas regras administrativas.

Alternativa descartada: introduzir outro framework de frontend ou alterar globalmente a política de acesso das páginas existentes.

## Risks / Trade-offs

- **[Risco]** Acesso de todos os instrutores amplia a exposição de dados físicos. → **Mitigação:** essa política foi escolhida pelo usuário; manter autorização explícita no Xano, não incluir dados pessoais desnecessários e não conceder acesso a recepcionistas ou alunos.
- **[Risco]** Medidas identificadas com valor e unidade podem ter formatos inconsistentes. → **Mitigação:** validar rótulo, valor numérico e unidade no backend, usando unidades consistentes (kg para peso, cm para altura e medidas corporais).
- **[Risco]** Um cliente pode tentar enviar outro responsável ou aluno. → **Mitigação:** derivar o instrutor da sessão autenticada e validar aluno e responsável no backend.
- **[Risco]** Falhas de autorização podem deixar avaliação em estado Reflex ou navegador. → **Mitigação:** limpar o estado sensível em 401/403, logout e saída da tela, além de não conceder acesso por padrão.

## Migration Plan

1. Implementar e validar localmente o modelo e as APIs Xano, sem tocar em dados reais.
2. Adicionar clientes tipados, estados, páginas e testes Reflex.
3. Executar testes direcionados, suíte existente, `reflex compile --dry`, validação OpenSpec e XanoScript, além de smoke tests controlados.
4. Revisar o diff e executar `xano workspace push --dry-run` limitado aos arquivos da change. Publicação real somente após revisão e aprovação explícita do grupo; confirmar o runtime depois.

Rollback: interromper a publicação se a validação falhar. Desativar exercícios e arquivar fichas de forma rastreável; não remover avaliações nem seus vínculos históricos.
