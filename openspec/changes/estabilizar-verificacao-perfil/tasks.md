# Tasks

## 1. Resiliência da verificação de perfil

- [x] 1.1 Implementar uma tentativa adicional limitada somente para falhas de transporte e HTTP 5xx em `GET /auth/me`; verificar com testes que 401, 403, 429, resposta inválida e escritas não são repetidas.
- [x] 1.2 Executar a validação de perfil em rotas protegidas fora do event loop e manter a sessão existente sem liberar a rota quando a verificação falhar; verificar com testes de autorização e responsividade.
- [x] 1.3 Tornar não bloqueantes as chamadas HTTP de login e verificação do perfil no fluxo de login, sem armazenar token antes da validação; verificar sucesso, indisponibilidade, respostas 401/403/429 e nova tentativa.

## 2. Verificação integrada

- [x] 2.1 Executar os testes direcionados e a suíte Python relevante, `reflex compile --dry` e `git diff --check`; confirmar que todos passam sem alterar os controles de autorização.
- [ ] 2.2 Validar no navegador autenticado a navegação entre páginas protegidas, a atualização após falha transitória e a mensagem para HTTP 429; manter a validação pendente se não houver sessão ou API disponível.
