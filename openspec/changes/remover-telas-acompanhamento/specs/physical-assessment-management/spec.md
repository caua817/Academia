# Spec Delta

## REMOVED Requirements

### Requirement: Administradores e instrutores podem registrar avaliações físicas
**Reason**: O aplicativo não oferecerá registro de avaliações físicas.
**Migration**: Remover telas e operações de avaliação do aplicativo e seus endpoints exclusivos após verificar referências cruzadas. Preservar avaliações e medidas existentes no Xano; não excluir dados de saúde.

### Requirement: Avaliações físicas preservam histórico e confidencialidade
**Reason**: A consulta e a correção de avaliações deixam de fazer parte das funcionalidades do aplicativo.
**Migration**: Não apagar nem alterar avaliações existentes. Manter os dados armazenados e inacessíveis pela interface removida.

### Requirement: A interface limita a exposição de dados de saúde
**Reason**: Não haverá interface do aplicativo para expor avaliações físicas depois da mudança.
**Migration**: Remover rotas e componentes de avaliação, mantendo os controles de autenticação e proteção de dados em qualquer API remanescente.
