# Proposta: Gestão de alunos

## Por quê

O painel atual tenta listar alunos por uma chamada que não tem tabela nem endpoint correspondente no workspace Xano local, e ainda não oferece busca, cadastro ou edição. A gestão de alunos é parte central da Fase 1 e uma base necessária para matrículas, frequência e demais funcionalidades previstas.

## O que muda

- Melhorar o painel Reflex com navegação consistente e uma área dedicada à gestão de alunos.
- Permitir listar e pesquisar alunos e apresentar estados de carregamento, lista vazia e erros de forma clara.
- Permitir cadastrar, editar e desativar alunos sem apagar fisicamente seus registros.
- Criar no Xano a persistência e os endpoints necessários, autorizando exclusivamente o perfil `admin` no backend.
- Tratar falhas da API explicitamente no frontend, sem transformar erros em listas vazias ou sucesso.
- Proteger dados pessoais e não expor CPF, endereço ou outros dados além do necessário nas telas.
- Usar os campos do modelo de domínio como base, sem impor unicidade de CPF até essa regra ser validada pelo grupo.

Fora do escopo desta change: planos, matrículas, mensalidades, pagamentos, check-in, gestão detalhada de permissões por perfil e alterações no cadastro/login de funcionários.

## Capabilities

### Novas capabilities

- `student-management`: consulta, pesquisa, cadastro, edição e desativação de alunos.

### Capabilities modificadas

Nenhuma. Ainda não há specs consolidadas no projeto.

## Impacto

- Frontend Reflex: painel e navegação em `academia/academia.py`, integração em `academia/services/xano_client.py` e estado/componentes necessários para gestão de alunos.
- Backend Xano: nova tabela e endpoints para alunos, autenticados e com autorização/validação no backend.
- Testes: cobrir operações da API e estados principais da interface conforme a estrutura de testes disponível.
- Xano remoto: qualquer envio ao workspace deve aguardar aprovação explícita do grupo; validar XanoScript e executar dry-run antes de solicitar essa aprovação.
