# Design: Gestão de planos e matrículas

## Contexto

Ver [proposal.md](./proposal.md) para motivação e escopo, e as specs de [planos](./specs/plan-management/spec.md) e [matrículas](./specs/enrollment-management/spec.md) para os comportamentos exigidos. O app já tem gestão de alunos no Reflex, cliente HTTP Xano autenticado e autorização administrativa validada nos endpoints de alunos. Ainda não existem tabelas ou endpoints locais de planos e matrículas.

## Objetivos / Não objetivos

**Objetivos:**

- Implementar as regras de negócio e persistência no Xano e consumir a API pela interface Reflex.
- Permitir demonstrar o fluxo: cadastrar plano, matricular aluno ativo e consultar as condições contratadas.
- Preservar histórico sem apagar planos descontinuados nem matrículas.
- Garantir que autorização e validações sejam executadas no backend.

**Não objetivos:**

- Implementar mensalidades, pagamentos, inadimplência, multas, juros, check-in, trancamento ou cancelamento.
- Permitir início de matrícula futuro, múltiplas matrículas simultâneas ou acesso por perfis ainda não suportados pela API.
- Alterar a autenticação ou o fluxo de gestão de alunos.

## Decisões

### Tabelas de domínio separadas

Criar uma tabela `plano` com identificador, nome, descrição opcional, duração em meses, valor em reais, situação ativa/descontinuada e data de criação. Duração deve ser inteira e positiva; valor deve ser maior que zero. Descontinuar altera a situação, sem excluir fisicamente o plano.

Criar uma tabela `matricula` relacionada a um aluno e a um plano, com data de início, data de término, duração contratada, valor contratado e data de criação. A matrícula mantém os valores e a duração copiados do plano no instante da criação. A data final também fica persistida para que alterações posteriores no plano não modifiquem o período contratado.

Alternativa descartada: calcular as condições contratadas consultando o plano a cada leitura. Essa abordagem mudaria contratos anteriores quando o plano fosse editado.

### Término por mês de calendário

Calcular o término adicionando à data inicial o número de meses contratados, preservando o dia do mês quando ele existir. Se o mês final não tiver esse dia, usar seu último dia. Exemplo: 31 de janeiro mais um mês termina no último dia de fevereiro. A data final é inclusiva; a matrícula fica ativa até esse dia e aparece encerrada a partir do dia seguinte.

A data inicial pode ser hoje ou anterior. Datas futuras são rejeitadas. A regra utiliza datas civis da academia no fuso `America/Sao_Paulo` e não depende de horário de execução ou tarefa agendada.

Alternativa descartada: depender de um job diário para alterar a situação. A situação pode ser derivada da comparação entre a data atual e o intervalo persistido, evitando estado desatualizado quando uma tarefa não executa.

### Bloqueio de sobreposição de períodos

Antes de criar matrícula, o backend verifica se o aluno e o plano existem e estão ativos, e se o intervalo proposto não se sobrepõe a nenhum período já registrado para aquele aluno, inclusive matrículas encerradas. Como as datas inicial e final são inclusivas, períodos que compartilham um dia se sobrepõem. Uma nova matrícula só pode começar após o término anterior.

Alternativa descartada: verificar somente se existe matrícula ativa hoje. Isso permitiria criar retroativamente um segundo contrato concorrente com uma matrícula histórica.

As verificações e a inclusão serão executadas em uma transação Xano. Para serializar criações concorrentes do mesmo aluno sem depender da opção de isolamento `serializable` — rejeitada pelo validador Xano disponível — a transação atualiza um campo técnico interno do registro do aluno antes de consultar períodos existentes. A escrita adquire o bloqueio da linha do aluno até o fim da transação; depois de adquiri-lo, o backend relê e valida o estado do aluno, verifica sobreposição e inclui a matrícula. Todas as criações devem seguir essa mesma ordem. O campo técnico não será aceito em entradas nem exposto em respostas da API.

### Autorização e API Xano

Todos os endpoints de planos e matrículas exigem autenticação e perfil `admin` no backend, seguindo o padrão de autorização validado na gestão de alunos. A interface não é uma fronteira de segurança.

Contrato HTTP esperado:

| Operação | Método e caminho |
|---|---|
| Listar planos (ativos e descontinuados) | `GET /planos` |
| Cadastrar plano | `POST /planos` |
| Consultar plano | `GET /planos/detalhes/{plano_id}` |
| Editar plano | `PUT /planos/atualizar/{plano_id}` |
| Descontinuar plano | `PATCH /planos/descontinuar/{plano_id}` |
| Reativar plano | `PATCH /planos/reativar/{plano_id}` |
| Listar matrículas | `GET /matriculas` |
| Consultar matrícula | `GET /matriculas/detalhes/{matricula_id}` |
| Criar matrícula | `POST /matriculas` |

Os contratos devem retornar somente campos necessários às telas. A listagem de matrículas pode incluir o nome do aluno e do plano, datas, valor contratado e situação; detalhes pessoais do aluno não são necessários.

### Interface e integração Reflex

Adicionar páginas de planos e matrículas ao shell atual, reutilizando `LoginState`, o cliente HTTP Xano, padrões de formulários, carregamento e tratamento de erro da área de alunos. A página de planos permite cadastrar, editar, listar e descontinuar/reativar. A página de matrículas permite selecionar aluno e plano ativos, escolher a data de início e consultar histórico.

O formulário não calcula nem valida sozinho regras de autorização ou sobreposição; ele pode oferecer feedback imediato, mas o Xano é a fonte de verdade. Respostas `401`, `403`, validações de negócio e falhas de conexão permanecem estados distintos e não podem ser apresentadas como sucesso ou lista vazia.

Alternativa descartada: implementar regras apenas em estado Reflex, pois estados de cliente não protegem os dados e não garantem consistência entre usuários simultâneos.

### Validação e publicação Xano

Consultar a documentação atual do Xano Developer MCP e validar os arquivos XanoScript antes de considerar a implementação pronta. Testes unitários locais usam transporte HTTP mockado. Testes runtime devem usar dados sintéticos e comprovar autorização, persistência e casos inválidos. Revisar o diff e executar `xano workspace push --dry-run`; não fazer push real sem aprovação explícita do grupo.

## Riscos / Trade-offs

- **[Risco]** Matrículas retroativas podem conflitar com períodos antigos. → **Mitigação:** o backend rejeita qualquer sobreposição de intervalos inclusivos.
- **[Risco]** Requisições simultâneas podem ultrapassar uma verificação comum de sobreposição. → **Mitigação:** serializar as criações por aluno com uma escrita técnica na linha do aluno dentro da transação e comprovar o comportamento no runtime Xano.
- **[Risco]** Um usuário pode consultar alunos ou valores comerciais sem autorização se somente a interface ocultar a página. → **Mitigação:** todos os endpoints validam autenticação e `admin` no Xano.
- **[Risco]** A API remota pode divergir dos arquivos locais até a sincronização aprovada. → **Mitigação:** não anunciar integração remota concluída antes da verificação no workspace e da aprovação de publicação.
- **[Risco]** A regra de fim do mês pode gerar interpretações diferentes em datas como 31 de janeiro. → **Mitigação:** explicitar o ajuste para o último dia do mês e testar limites de fevereiro e meses de 30 dias.

## Plano de migração

1. Implementar e validar localmente tabelas e endpoints Xano para planos e matrículas.
2. Implementar cliente e páginas Reflex; executar testes mockados e compilação.
3. Testar no Xano com dados sintéticos as operações autorizadas, recusas por perfil, validações, persistência, sobreposição e preservação dos valores contratados.
4. Revisar o diff e executar dry-run do push; solicitar aprovação antes de publicar.
5. Para rollback, retirar navegação e páginas sem apagar registros de planos ou matrículas; mudanças de backend devem permanecer rastreáveis e não remover histórico.

## Questões em aberto

Nenhuma para o escopo desta change. Cobranças, pagamentos, cancelamento e trancamento permanecem deliberadamente para decisões e changes posteriores.
