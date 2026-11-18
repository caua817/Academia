# Design

## Context

Veja [proposal.md](./proposal.md) e os contratos em [class-reservation-management](./specs/class-reservation-management/spec.md), [class-session-management](./specs/class-session-management/spec.md) e [management-reports](./specs/management-reports/spec.md).

Hoje a aplicação registra `/reservas` em `academia/academia.py`, expõe o link na navegação e inclui a rota no controle de acesso. A tela, seu estado e seus eventos ficam em `academia/operacao.py`, que também exibe ocupação na agenda e métricas de reserva nos relatórios. `academia/services/xano_client.py` contém wrappers locais para chamadas de reserva e recebe campos de ocupação nas respostas de sessões e relatórios. Os endpoints e dados persistidos pertencem ao Xano e ficam fora desta mudança.

## Goals / Non-Goals

**Goals:**

- Remover a superfície de reservas do aplicativo Reflex, inclusive o estado de reserva e dados derivados que seriam sincronizados com o cliente.
- Preservar a gestão de modalidades e sessões, e os demais indicadores dos relatórios.
- Preservar os endpoints Xano existentes, os dados históricos e suas regras de autorização.
- Manter o escopo do projeto documentado sem remover a entidade histórica do modelo de domínio.

**Non-Goals:**

- Excluir, cancelar em lote, migrar ou alterar qualquer reserva existente.
- Alterar endpoints, funções, tabelas ou permissões no workspace Xano, ou publicar mudanças nele.
- Remover a gestão de modalidades ou sessões de aula.

## Decisions

### Retirar somente a interface Reflex

Remover link, registro da página, mapeamentos da rota, permissão específica e componentes/eventos de reserva. A rota antiga deixa de ser registrada e não pode exibir dados ou controles da página. Os endpoints Xano continuam publicados e inalterados; a retirada da interface não é tratada como autorização ou bloqueio de API.

**Alternativa considerada:** desativar ou excluir os endpoints no Xano. Rejeitada porque a decisão confirmada preserva APIs e dados existentes, e mudanças no workspace exigiriam um ciclo de revisão e publicação separado.

### Impedir que ocupação continue no estado e nas telas

Remover ocupação da lista de sessões e os indicadores de reserva/ocupação da tela de relatórios. Os wrappers de consulta de sessões e relatórios podem validar o contrato atual do Xano, mas devem omitir campos derivados de reserva antes que as respostas sejam armazenadas no estado Reflex visível ao cliente. Remover também wrappers locais exclusivos de ações de reserva e ajustar o estado vazio do relatório para depender somente das métricas ainda exibidas.

**Alternativa considerada:** apenas ocultar os textos na renderização, mantendo os valores no estado Reflex. Rejeitada porque os dados ainda seriam sincronizados para o cliente e a interface continuaria dependendo de valores que a mudança pretende retirar.

### Manter sessões e registros sem migração

Manter criação, consulta, edição e cancelamento de sessões, modalidade, instrutor, capacidade configurada e local. Atualizar a documentação de visão geral para registrar que o frontend atual não oferece reservas; manter o modelo de domínio e os dados históricos, pois APIs e registros de reserva continuam existindo.

**Alternativa considerada:** apagar `Reserva` do modelo de domínio e da documentação do projeto. Rejeitada porque contrariaria a preservação explícita dos dados e contratos Xano.

## Risks / Trade-offs

- **[Risco]** Chamadas diretas aos endpoints Xano continuarão tecnicamente possíveis para clientes autorizados. **→ Mitigação:** manter a autorização existente no backend; esta mudança remove somente a interface Reflex.
- **[Risco]** A remoção de campos de resposta necessários ao frontend pode quebrar a validação do cliente local. **→ Mitigação:** preservar a validação do contrato recebido do Xano e filtrar os campos somente na saída destinada ao estado Reflex, com testes de contrato.
- **[Trade-off]** Usuários deixam de acompanhar ocupação e reservas pela interface. **→ Mitigação:** manter sessões, capacidade configurada e demais indicadores operacionais disponíveis.

## Migration Plan

1. Retirar a tela, navegação, rota e chamadas do aplicativo Reflex.
2. Sanitizar as respostas de sessões e relatórios no cliente local e atualizar testes/documentação.
3. Executar testes direcionados, suíte relevante, compilação Reflex e `git diff --check`.
4. Confirmar que `xano/` não mudou e validar em navegador que `/reservas` não apresenta a tela, enquanto páginas de sessões e relatórios continuam funcionando.

Rollback: restaurar os componentes e registro da rota do frontend a partir do histórico Git; como os endpoints e dados Xano permanecem inalterados, não é necessária migração de dados.
