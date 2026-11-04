# Proposta: Gestão de planos e matrículas

## Por quê

O projeto já permite manter os cadastros de alunos, mas ainda não representa os serviços oferecidos pela academia nem o vínculo de cada aluno com um plano. Sem esses dois elementos, não é possível demonstrar o fluxo operacional central de configurar um plano e matricular um aluno.

## O que muda

- Criar e manter planos com nome, descrição, duração em meses, valor em reais e situação ativa ou descontinuada.
- Permitir que administradores consultem os planos ativos e descontinuados e descontinuem planos sem apagar registros usados por matrículas.
- Criar matrículas de alunos ativos em planos ativos, registrando a data de início, o término calculado, o valor contratado e a duração contratada; serializar as criações por aluno no backend para impedir sobreposições também sob requisições simultâneas.
- Permitir consultar matrículas e identificar as que estão ativas ou encerradas.
- Impedir mais de uma matrícula ativa para o mesmo aluno.
- Congelar na matrícula o valor e a duração vigentes na contratação; alterações posteriores no plano não modificam matrículas existentes.
- Calcular o término por meses de calendário, usando o mesmo dia do mês de início e limitando ao último dia do mês quando esse dia não existir. A data de início deve ser hoje ou anterior; não haverá agendamento futuro nesta entrega.
- Aplicar autenticação e autorização `admin` no backend Xano para todas as operações; a interface Reflex não será tratada como controle de segurança.
- Integrar as telas ao painel Reflex existente e verificar persistência, validação, autorização e fluxo completo com dados de teste.

Ficam fora desta change: geração de mensalidades, registro de pagamentos, inadimplência, multas/juros, trancamento ou cancelamento de matrículas, check-in, planos familiares, múltiplas matrículas ativas e novos perfis de funcionário.

## Capabilities

### Novas capabilities

- `plan-management`: consulta, criação, edição e descontinuação de planos.
- `enrollment-management`: criação e consulta de matrículas, com duração e valor contratados preservados e limite de uma matrícula ativa por aluno.

### Capabilities modificadas

Nenhuma.

## Impacto

- Backend Xano: novas tabelas e endpoints para planos e matrículas, com validação, persistência e autorização administrativa; inclui um campo técnico interno no aluno para serializar criações de matrícula, sem expô-lo na interface ou nas respostas da API.
- Frontend Reflex: navegação, estados, formulários e listas para planos e matrículas, integrados à gestão de alunos existente.
- Cliente HTTP e testes: chamadas autenticadas, tratamento explícito de erros e testes locais mockados; verificação runtime no ambiente Xano com registros sintéticos.
- Dependências: nenhuma nova dependência prevista.
- Xano remoto: validar XanoScript, revisar o diff e executar dry-run antes de qualquer push; não publicar alterações sem aprovação explícita do grupo.
