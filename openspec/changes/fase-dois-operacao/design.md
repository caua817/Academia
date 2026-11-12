# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas desta change. O frontend Reflex já possui navegação administrativa, gestão de alunos, planos, matrículas, funcionários, mensalidades e check-ins, consumindo o Xano por `XanoClient`. O backend local usa XanoScript; as entidades de modalidades, sessões e reservas ainda não aparecem nas tabelas ou APIs versionadas. A interface atual exibe links de gestão sem verificar o perfil, embora as APIs existentes usem autorização administrativa.

## Goals / Non-Goals

**Goals:**

- Implementar modalidades, sessões únicas, reservas e relatórios agregados sem mover regras de negócio para o frontend.
- Evitar conflitos de horário de instrutor, reservas duplicadas e excesso de capacidade inclusive sob requisições simultâneas.
- Aplicar autorização `admin` no backend e restringir navegação e rotas de gestão no Reflex.
- Verificar os endpoints de funcionários publicados antes de depender deles; não criar endpoints nessa change.

**Non-Goals:**

- Aulas recorrentes, inscrições pelo aluno, cobrança de reservas, lista de espera, notificações, integração com catraca ou sincronização externa de calendário.
- Alterar as regras de matrículas, mensalidades, pagamentos ou check-ins já consolidadas.
- Reimplementar a gestão de funcionários ou publicar alterações no Xano sem revisão e aprovação explícitas.

## Decisions

### Representar cada aula como uma sessão independente

Uma sessão guarda modalidade, instrutor, início e fim, capacidade, local opcional e situação agendada/cancelada. O backend aceita apenas modalidade e instrutor ativos, impede horários sobrepostos do mesmo instrutor e preserva sessões canceladas no histórico. A interface pode editar uma sessão agendada, mas não permite reduzir a capacidade abaixo das reservas ainda válidas.

Alternativa descartada: regras recorrentes e geração automática de ocorrências, pois ampliam a mudança com calendários, exceções e edição em série sem serem necessárias para o fluxo de apresentação.

### Fazer do Xano a autoridade da ocupação

O Xano valida a elegibilidade do aluno e a capacidade no momento da reserva. Criação e cancelamento de reservas atualizam a ocupação de modo atômico, usando transação e serialização por sessão ou mecanismo equivalente suportado pelo workspace. Uma reserva ativa por aluno e sessão é garantida no backend, não somente pela interface.

Alternativa descartada: contar vagas apenas no Reflex antes de gravar, pois chamadas concorrentes podem exceder a capacidade.

### Separar reserva de presença na academia

Reserva confirmada, cancelada, presente ou falta descreve a participação numa sessão; check-in continua representando a entrada física na academia. Administradores podem cancelar uma reserva antes do início e registrar presença/falta depois do término; cancelar uma sessão preserva o histórico e cancela suas reservas ainda confirmadas.

Alternativa descartada: reutilizar o check-in da academia como presença em aula, pois são eventos e vínculos distintos.

### Consolidar relatórios em respostas agregadas

Os endpoints de relatório retornam apenas totais e percentuais, com intervalo de datas explícito. Matrículas ativas são avaliadas na data final do intervalo; valores pagos consideram pagamentos registrados dentro do intervalo; inadimplência considera mensalidades vencidas e ainda não pagas até a data final; frequência conta check-ins do intervalo; ocupação conta reservas não canceladas nas sessões do intervalo em relação à capacidade. Consultas e resultados são autorizados a `admin` e não retornam nomes, contatos ou documentos.

Alternativa descartada: compor os relatórios baixando listas pessoais no frontend, pois expõe mais dados do que o necessário e duplica lógica de agregação.

### Aplicar barreira de interface sem substituir autorização no servidor

O perfil é consultado pela sessão autenticada usando o endpoint de identidade existente. Navegação e rotas de gestão exigem perfil `admin`; falta de sessão redireciona ao login e falha ao determinar o perfil não concede acesso. Todas as APIs continuam autorizando cada operação no backend.

Alternativa descartada: ocultar somente links, pois URL direta ainda abriria páginas e poderia iniciar consultas.

### Verificar funcionários sem ampliar a implementação

Antes de concluir a integração da Fase 2, comparar a API de funcionários publicada com os arquivos locais e validar uma leitura autenticada sem operações de escrita. Se os endpoints não estiverem disponíveis no workspace, registrar o bloqueio e não criar nem publicar endpoints de funcionários como parte desta mudança.

Alternativa descartada: presumir que os arquivos ausentes localmente existem no workspace ou acrescentar a gestão de funcionários ao escopo sem planejamento próprio.

## Risks / Trade-offs

- **[Risco]** Os endpoints publicados de funcionários podem não estar disponíveis ou divergir dos contratos usados pelo frontend. → **Mitigação:** validar leitura autenticada antes de declarar cobertura; registrar ausência como bloqueio fora do escopo.
- **[Bloqueio de validação]** O pull isolado do workspace confirma que os endpoints de funcionários publicados estão presentes, e o esquema remoto inclui os perfis `admin`, `member`, `recepcionista` e `instrutor`. A leitura autenticada desses endpoints não foi executada porque o executor CLI não fornece uma sessão autenticada de usuário da aplicação; não usar credenciais ou dados reais para contornar essa limitação.
- **[Validação parcial]** A instância Xano `v1` rejeitou `isolation = "serializable"` no primeiro import e o reverteu. As transações foram ajustadas para usar atualizações de linha como locks explícitos; a edição de sessão adquire os locks dos instrutores em ordem crescente. A nova versão foi publicada e um pull isolado confirmou os endpoints, tabelas e referências. Os testes Xano de caminhos de rejeição executados passaram; os testes de sucesso em endpoints protegidos retornaram `Unauthorized - Authentication Required` porque o executor não fornece sessão autenticada de usuário. A leitura autenticada e a concorrência permanecem sem validação.
- **[Risco]** O workspace Xano pode conter alterações remotas que não existem no checkout. → **Mitigação:** fazer pull isolado e revisar diferenças antes de editar ou publicar; qualquer push real requer aprovação explícita.
- **[Risco]** Edições de sessões e reservas simultâneas podem causar conflitos de capacidade. → **Mitigação:** validar e serializar as transições no backend e testar concorrência de forma direcionada.
- **[Risco]** O resumo de inadimplência em período pode ser interpretado de modos diferentes. → **Mitigação:** usar a data final do intervalo como referência para vencimentos e incluir essa definição na interface.
- **[Risco]** Uma conta sem permissão pode conservar uma página aberta após a sessão ou perfil mudar. → **Mitigação:** validar a sessão nas entradas de rota e depender também das respostas de autorização do backend, limpando dados ao receber HTTP 401/403.

## Migration Plan

1. Fazer pull do workspace Xano para uma pasta isolada e comparar os endpoints existentes de funcionários e as alterações remotas antes de modificar arquivos.
2. Validar o modelo e os contratos de modalidades, sessões, reservas e relatórios; implementar persistência e autorização Xano, validando XanoScript e concorrência de capacidade.
3. Implementar os clientes Reflex, telas e restrição de navegação/rota por perfil, mantendo mensagens explícitas para carregamento, vazio, sucesso e falha.
4. Executar testes direcionados, suíte existente, compilação Reflex e validação OpenSpec; fazer smoke test sem criar dados reais nem repetir operações de escrita.
5. Revisar `git diff` e executar `xano workspace push --dry-run` apenas para os arquivos da change. Solicitar aprovação explícita antes de qualquer publicação real e, após aprovação, validar leitura e fluxos no runtime.

Rollback: interromper a publicação se a validação falhar. Desativar modalidades ou cancelar sessões e reservas de forma rastreável; não apagar registros de sessões, reservas, matrículas ou finanças.
