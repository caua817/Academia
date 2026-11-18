# Tasks

## 1. Formulário e dados da sessão

- [x] 1.1 Separar no estado do formulário o dia da aula dos horários de início e término, recompondo os timestamps no fuso local; verificar criação, edição, sessão futura e rejeição de horários inválidos com testes unitários.
- [x] 1.2 Carregar funcionários e oferecer somente instrutores ativos pelo nome, mantendo o ID como valor interno; verificar filtragem, rótulos e falhas da API com testes.
- [x] 1.3 Atualizar os formulários de agendamento e edição para mostrar uma única data, dois horários e a seleção por nome; verificar que nenhum campo de ID seja apresentado e que os filtros existentes por período permaneçam.

## 2. Verificação integrada

- [x] 2.1 Executar os testes de operação e do cliente Xano, além de `reflex compile --dry`; confirmar que a API continua recebendo `instrutor_id`, `inicio` e `termino`.
