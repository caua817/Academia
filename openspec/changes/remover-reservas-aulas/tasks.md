# Tasks

## 1. Remover a interface de reservas

- [x] 1.1 Remover o link de reservas, o registro da rota `/reservas` e seus mapeamentos de carregamento/autorização; verificar que a navegação não exibe a opção e que a rota antiga não apresenta a tela.
- [x] 1.2 Remover do estado Reflex os campos, eventos e componentes exclusivos de reservas e retirar os wrappers locais de chamadas CRUD de reservas; verificar com testes que nenhuma página Reflex chama os endpoints de reserva.

## 2. Preservar as telas relacionadas e os dados

- [x] 2.1 Remover a ocupação da lista de sessões e os indicadores de reserva/ocupação dos relatórios, filtrando os campos derivados de reservas antes de sincronizar o estado Reflex; verificar que os demais campos e métricas continuam disponíveis e que o contrato Xano recebido continua validado.
- [x] 2.2 Atualizar `docs/project-overview.md` para registrar que o frontend não oferece gestão de reservas e que APIs e histórico Xano permanecem preservados; verificar que a documentação não contradiz o escopo.

## 3. Verificação integrada

- [x] 3.1 Executar testes direcionados e a suíte Python relevante, `reflex compile --dry` e `git diff --check`; confirmar que a pasta `xano/` não foi alterada.
- [ ] 3.2 Validar no navegador que `/reservas` não apresenta a tela, que as opções de menu e métricas foram removidas e que sessões/relatórios continuam acessíveis; manter a validação pendente se não houver sessão/API disponível.
