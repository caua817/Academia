# Spec Delta

## REMOVED Requirements

### Requirement: Administradores e instrutores podem manter fichas de treino
**Reason**: O aplicativo não oferecerá criação, edição ou consulta de fichas de treino.
**Migration**: Remover telas e operações de ficha do aplicativo e seus endpoints exclusivos após verificar referências cruzadas. Preservar fichas, itens e demais dados já armazenados no Xano.

### Requirement: O histórico de fichas é preservado
**Reason**: A consulta e o arquivamento de fichas deixam de fazer parte das funcionalidades do aplicativo.
**Migration**: Não apagar nem alterar fichas existentes; os registros permanecem preservados no armazenamento para eventual decisão futura.

### Requirement: Fichas e dados dos alunos exigem autorização de administrador ou instrutor
**Reason**: O aplicativo não exporá operações de ficha após esta mudança.
**Migration**: Remover somente endpoints exclusivos de fichas e preservar as regras de acesso das demais informações de alunos.
