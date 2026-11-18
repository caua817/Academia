# Tasks

## 1. Autorização no backend Xano

- [x] 1.1 Revisar os endpoints Xano de alunos, matrículas, planos, mensalidades, pagamentos e check-ins, mapear cada operação ao perfil permitido e consultar a documentação XanoScript; verificar o mapeamento com uma lista de endpoints e operações.
- [x] 1.2 Implementar autorização por operação nos endpoints de alunos para permitir leitura, cadastro, edição e desativação por `admin` e `recepcionista`, e consulta mínima por `instrutor`; validar a sintaxe XanoScript e cobrir chamadas permitidas e negadas.
- [x] 1.3 Implementar autorização de consulta de check-ins para `admin`, `recepcionista` e `instrutor`, limitando os campos retornados ao instrutor, e restringir o registro a `admin` e `recepcionista`; validar a sintaxe e os resultados por perfil.
- [x] 1.4 Permitir que `admin` e `recepcionista` consultem matrículas e criem matrículas, mantendo operações administrativas restritas; verificar que chamadas diretas sem perfil autorizado sejam rejeitadas.
- [x] 1.5 Permitir que `recepcionista` consulte apenas planos ativos sem conceder operações de gestão, preservando o acesso administrativo completo; validar respostas para ambos os perfis e rejeição dos demais.
- [x] 1.6 Permitir que `admin` e `recepcionista` consultem mensalidades e registrem pagamentos, mantendo correções financeiras exclusivas de `admin`; validar autorização em cada operação e preservação dos registros em tentativas negadas.

## 2. Controle de acesso no frontend Reflex

- [x] 2.1 Atualizar o controle compartilhado de acesso para representar permissões explícitas de `admin`, `recepcionista` e `instrutor`, negar acesso por padrão e direcionar falhas de sessão ou perfil ao fluxo apropriado; verificar com testes unitários do controle de acesso.
- [x] 2.2 Ajustar navegação e proteção de rotas para exibir somente áreas permitidas a cada perfil, preservando as áreas administrativas para `admin`; verificar acesso direto a rotas autorizadas e negadas por perfil.
- [x] 2.3 Ajustar páginas e ações de alunos, matrículas e planos para permitir as operações da recepção e limitar instrutores à consulta mínima, sem expor campos pessoais desnecessários; verificar formulários, ações e dados apresentados por perfil.
- [x] 2.4 Ajustar páginas e ações de check-ins e financeiro para permitir consulta e registro operacional à recepção, consulta de frequência sem escrita ao instrutor e correções financeiras somente ao administrador; verificar ações disponíveis e mensagens de falha.

## 3. Verificação integrada

- [x] 3.1 Adicionar ou atualizar testes da matriz de autorização para todos os perfis e operações, incluindo chamadas diretas ao backend, rotas protegidas, dados mínimos do instrutor e negação por padrão; verificar que os testes cubram acessos permitidos e proibidos.
- [x] 3.2 Executar os testes relevantes e `reflex compile --dry`, validar os arquivos XanoScript e executar `xano workspace push --dry-run`; revisar o diff e confirmar que nenhuma alteração foi publicada no workspace Xano.
