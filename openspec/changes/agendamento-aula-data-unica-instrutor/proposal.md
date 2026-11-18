# Proposta: Agendamento de aula com data única e instrutor por nome

## Por quê

O formulário de agendamento repete a data nos campos de início e término e exige que a pessoa informe manualmente o ID do instrutor. Isso torna o preenchimento mais confuso e expõe um identificador técnico que não é útil para quem agenda a aula.

## O que muda

- Substituir a data repetida do início e do término por um único campo com o dia da aula, mantendo campos separados para os horários de início e término.
- Permitir selecionar um instrutor pelo nome, exibindo somente instrutores ativos e mantendo o ID apenas no estado interno e no contrato com a API.
- Aplicar o mesmo formulário ao agendamento e à edição de sessões.
- Preservar os filtros por período nas consultas da agenda e das reservas, e manter inalterados os contratos e as validações do backend.

## Capabilities

### Novas capabilities

Nenhuma.

### Modified Capabilities

- `class-session-management`: o formulário de sessões usa um único dia da aula, horários separados e seleção de instrutor por nome, sem pedir o ID à pessoa usuária.

## Impacto

- Frontend Reflex: estado, validação, componentes do formulário e apresentação dos dados de sessão.
- Testes Python de validação e da interface/reflex state.
- Cliente e endpoints Xano permanecem com os campos atuais (`instrutor_id`, `inicio` e `termino`); o frontend combina o dia e os horários antes de enviar a sessão.
- Nenhuma dependência nova prevista.
