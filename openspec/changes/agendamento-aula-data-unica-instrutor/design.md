# Design

## Context

Consulte a motivação e o escopo em [proposal.md](./proposal.md) e o contrato visível em [spec.md](./specs/class-session-management/spec.md). Hoje o estado do formulário guarda início e término como valores `datetime-local`; a gravação converte ambos para timestamps UTC. A lista de funcionários já usa `GET /funcionarios`, cujos registros contêm `id`, `name`, `role` e `situacao`. A API de sessões já devolve `instrutor_nome`, mas os endpoints de escrita continuam recebendo `instrutor_id`.

## Goals / Non-Goals

**Goals:**
- Manter uma única data de aula no formulário e derivar dela os timestamps de início e término.
- Selecionar instrutores ativos por nome sem alterar a associação por ID enviada à API.
- Preservar a interpretação de horários no fuso `America/Sao_Paulo`, as validações atuais e o filtro por período nas demais telas.

**Non-Goals:**
- Alterar endpoints, tabelas ou contratos Xano.
- Mudar os filtros de período da agenda, reservas ou relatórios.
- Permitir sessão que atravesse a meia-noite.

## Decisions

1. **Separar data e horários no estado do formulário.** Guardar um campo de data e dois campos de hora; ao salvar, compor os valores locais de início e término antes da validação e de `to_api_timestamp`. Ao editar, converter os timestamps existentes para `America/Sao_Paulo` e preencher a data e os horários correspondentes. Isso evita diferenças acidentais de dia entre início e término. Alternativa descartada: manter dois campos `datetime-local`, que continua solicitando a mesma data duas vezes.

2. **Carregar opções a partir da lista de funcionários existente.** Filtrar os registros para `role == "instrutor"` e situação ativa, apresentar `name` como rótulo e usar `id` como valor interno da opção. Reutiliza a API existente e mantém a validação de instrutor ativo no backend. Alternativa descartada: pedir um ID numérico ou criar uma nova rota de instrutores, pois ambas adicionariam atrito ou duplicariam o contrato.

3. **Preservar o payload do backend.** Continuar enviando `instrutor_id`, `inicio` e `termino`; a seleção por nome não muda a relação persistida nem exige migração. Os filtros de consulta permanecem como períodos, conforme escopo confirmado.

## Risks / Trade-offs

- [A lista de funcionários pode falhar ou não conter instrutores ativos] → Exibir o erro da API explicitamente e impedir o salvamento sem instrutor selecionável; não tratar a falha como uma lista carregada vazia.
- [A edição pode receber timestamps com offset ou formato inesperado] → Reutilizar o parser de horário da sessão e manter o fuso local da aplicação; testar a conversão com timestamps UTC.
- [Campos separados de data e hora não representam sessões noturnas que cruzam a meia-noite] → Fora do escopo atual; a validação exige término posterior ao início no mesmo dia.

## Migration Plan

Não há migração: o formato persistido e os payloads Xano não mudam. O formulário novo substitui os campos atuais no frontend.
