# Proposta: Acesso por perfil de funcionário

## Por quê

O aplicativo já permite ao administrador convidar funcionários escolhendo entre os perfis administrador, recepcionista e instrutor, mas as páginas de gestão permanecem em grande parte exclusivas ao administrador. É necessário conceder a cada perfil somente as telas e operações correspondentes à sua função, com autorização efetiva no backend.

## O que muda

- Manter o convite seguro de funcionários pela área existente, incluindo a escolha de perfil; não criar cadastro público nem permitir que o administrador defina a senha do funcionário.
- Garantir acesso total ao administrador.
- Conceder à recepção acesso operacional a alunos, matrículas, consulta de planos ativos durante a matrícula, consulta de mensalidades, registro de pagamentos e check-ins. Correções financeiras, gestão de funcionários, configurações e relatórios continuam restritos ao administrador.
- Conceder ao instrutor consulta mínima de alunos e frequência, além do acesso já previsto aos recursos de acompanhamento (exercícios, fichas e avaliações), sem acesso a dados financeiros, matrículas, gestão de funcionários ou configurações administrativas.
- Alinhar navegação e rotas Reflex às permissões e aplicar as mesmas decisões de autorização em cada endpoint Xano, sem confiar no menu como controle de segurança.

Fica fora do escopo alterar o fluxo de ativação por convite, criar permissões configuráveis por usuário ou disponibilizar acesso a alunos como usuários.

## Capabilities

### Novas capabilities

Nenhuma.

### Modified Capabilities

- `authentication`: substituir a restrição geral de páginas administrativas por uma matriz explícita de acesso por perfil, com negação por padrão e autorização no backend.
- `student-management`: permitir operações de alunos pela recepção e consulta mínima pelo instrutor, preservando autorização e minimização de dados.
- `attendance-management`: permitir registro pela recepção e consulta de frequência pelo instrutor, sem permitir que instrutores registrem check-ins.
- `enrollment-management`: permitir que a recepção consulte e crie matrículas.
- `plan-management`: permitir somente a consulta de planos ativos necessária para a recepção matricular alunos, mantendo configuração administrativa.
- `billing-management`: permitir consulta de mensalidades e registro de pagamentos pela recepção; manter correções restritas ao administrador.

## Impacto

- Frontend Reflex: controle de acesso compartilhado, menu, proteção de rotas e telas de alunos, matrículas, financeiro, check-ins e acompanhamento.
- Backend Xano: autorização por perfil nos endpoints correspondentes, inclusive os de leitura e escrita.
- Testes de autorização por rota e endpoint, cobrindo perfis autorizados e negados.
- O cadastro atual é por convite seguro; a change em andamento `api-gestao-funcionarios` continua responsável pela API de gestão de funcionários e não é substituída aqui.
