# Proposta: Gestão de funcionários

## Por quê

O projeto define administrador, recepcionista e instrutor como funcionários com acesso ao sistema, mas ainda não oferece uma área para gerenciar essas contas. Uma gestão centralizada permite controlar os perfis e a situação de acesso sem expor ou compartilhar senhas.

## O que muda

- Adicionar no Reflex uma área para listar, pesquisar, convidar, editar, ativar e desativar funcionários.
- Representar os perfis `admin`, `recepcionista` e `instrutor`, conforme o modelo de domínio.
- Criar funcionários por convite de e-mail, permitindo que cada pessoa defina a própria senha.
- Integrar as operações por chamadas HTTP no cliente existente, tratando estados de carregamento, sucesso, erro e sessão expirada.
- Exibir somente dados operacionais necessários; nunca apresentar senhas, tokens ou credenciais na interface.
- Definir no design o contrato HTTP esperado. Esta change implementa somente o frontend e assume que a API correspondente estará disponível e aplicará a autorização no backend.

Ficam fora do escopo: implementação ou validação runtime no Xano, alterações na tabela `user` e nos perfis do backend, redefinição de senha, folha de pagamento, dados trabalhistas, permissões detalhadas por tela e as funcionalidades de manutenção de máquinas, gráficos e chatbot.

## Capabilities

### Novas capabilities

- `employee-management`: consulta e manutenção das contas de funcionários por administradores.

### Modified Capabilities

Nenhuma. O projeto ainda não possui specs consolidadas.

## Impact

- Frontend Reflex: navegação, estado, formulários e tabela de funcionários.
- Cliente HTTP: operações para consultar, convidar, editar e alterar a situação de funcionários, com token da sessão existente.
- API Xano: contrato esperado a ser documentado para esta interface, sem alterar nem validar arquivos ou workspace Xano nesta change.
- Testes: testes locais com respostas HTTP simuladas; sem chamadas autenticadas ao workspace.
- Dependências: nenhuma nova dependência prevista.
