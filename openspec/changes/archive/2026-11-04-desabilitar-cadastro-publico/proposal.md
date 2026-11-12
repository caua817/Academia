# Proposta: Desabilitar cadastro público

## Por quê

O endpoint público de cadastro cria contas com perfil `member`, embora o modelo do projeto determine que somente funcionários tenham acesso ao sistema e que alunos sejam apenas registros gerenciados pela equipe. Remover a criação anônima reduz a exposição do sistema e evita conceder contas a pessoas sem vínculo autorizado com a academia.

## O que muda

- **BREAKING**: remover da tela de login o acesso e o formulário de cadastro público.
- Desativar o endpoint legado de cadastro para que nenhuma chamada, autenticada ou não, crie usuários ou emita token por esse fluxo.
- Preservar login e contas existentes sem promover, excluir ou alterar automaticamente seus perfis.
- Até existir um fluxo administrativo de convite provisionado no backend, o app não oferecerá criação de novas contas; não serão definidas nem compartilhadas senhas em nome dos funcionários.
- Manter a implementação de convites pela interface e respectivos endpoints sob a change de gestão de funcionários, sem antecipar esse escopo nesta mudança.

## Capabilities

### Novas capabilities

Nenhuma.

### Modified capabilities

- `authentication`: cadastro de contas deixa de ser público, e contas existentes continuam podendo entrar.

## Impacto

- Frontend Reflex: `academia/login.py`, `academia/services/auth_client.py` e testes de autenticação para remover o cadastro público.
- Backend Xano: endpoint `xano/api/authentication/auth/signup_POST.xs` para impedir criação anônima de contas; validação e publicação dependem do Xano.
- Documentação/specs: explicitar que somente funcionários acessam o sistema e que alunos não possuem login nesta versão.
- Sem alterações planejadas em dependências, contas existentes ou registros persistidos.
- Nenhuma publicação real ao workspace Xano será feita sem aprovação explícita do grupo.
