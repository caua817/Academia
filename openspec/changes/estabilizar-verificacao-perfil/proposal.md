# Proposta: Estabilizar a verificação de perfil

## Por quê

Falhas transitórias ao consultar `/auth/me` impedem a entrada ou navegação e são exibidas como “Não foi possível verificar seu perfil”. Nas páginas protegidas, essa chamada HTTP síncrona ocorre dentro do fluxo assíncrono de autorização e pode bloquear o event loop do Reflex, interrompendo também a comunicação da interface. Além disso, cada navegação protegida consulta `/auth/me` novamente; como o endpoint também registra um evento no Xano, chamadas redundantes aumentam a carga e o risco de HTTP 429.

## O que muda

- Executar a verificação de perfil sem bloquear o fluxo assíncrono do Reflex.
- Permitir recuperação segura após falhas transitórias, com retentativa limitada somente para a consulta idempotente de perfil.
- Reutilizar, durante a sessão autenticada, o perfil já verificado para evitar chamadas redundantes a `/auth/me` em navegações protegidas.
- Manter a autorização fechada por padrão: falha ou resposta inválida nunca concede acesso; respostas 401, 403 e 429 não são repetidas automaticamente.
- Manter o cache de perfil somente no estado privado do servidor, vinculado ao token atual e sem substituir a autorização aplicada pelo backend em cada operação.
- Preservar a sessão em falhas temporárias de verificação nas páginas protegidas e permitir nova tentativa explícita.
- Adicionar testes para falha transitória, respostas não repetíveis, recuperação e isolamento do event loop.

## Capabilities

### Novas Capabilities

Nenhuma.

### Capabilities Modificadas

- `authentication`: definir recuperação de falhas transitórias durante a verificação de perfil sem bloquear a interface, sem conceder acesso indevido e sem repetir automaticamente respostas de autenticação ou limitação.

## Impacto

- Frontend Reflex: `academia/access_control.py`, fluxo de login em `academia/login.py` e limpeza de sessão em `academia/session_state.py`.
- Cliente Xano: chamada autenticada e idempotente de consulta de perfil em `academia/services/xano_client.py`.
- Testes: autorização por perfil, login e cliente Xano.
- Nenhuma alteração de contrato público, esquema de dados ou dependência prevista.
