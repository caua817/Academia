# Spec Delta

## REMOVED Requirements

### Requirement: Administradores e instrutores podem manter o catálogo de exercícios
**Reason**: O aplicativo de gestão deixará de oferecer cadastro ou consulta de exercícios.
**Migration**: Remover a interface e as operações públicas do aplicativo. Preservar tabelas e registros existentes no Xano; não executar exclusão física.

### Requirement: Exercícios são desativados sem apagar o histórico
**Reason**: O fluxo de desativação pertence à funcionalidade de catálogo que será retirada do aplicativo.
**Migration**: Manter exercícios e referências históricas existentes armazenados, sem permitir novas operações pela aplicação.

### Requirement: O catálogo exige autorização de administrador ou instrutor
**Reason**: Não haverá operações de catálogo de exercícios expostas pelo aplicativo após a mudança.
**Migration**: Retirar os endpoints exclusivos dessa funcionalidade depois de verificar que não são usados por outras capacidades; preservar autenticação e autorização das demais APIs.
