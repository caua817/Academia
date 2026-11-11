# Proposal

## Why

A Fase 1 já cobre o núcleo administrativo da academia, mas ainda não permite organizar atividades coletivas, controlar vagas ou acompanhar a operação em relatórios. A Fase 2 completa esse fluxo com gestão de modalidades e sessões de aula, reservas e indicadores gerenciais, mantendo o acesso restrito a administradores.

## What Changes

- Cadastrar, consultar, editar, ativar e desativar modalidades, preservando registros usados por sessões existentes.
- Criar e administrar aulas como sessões únicas, com modalidade, instrutor, início e fim, capacidade e local opcional.
- Permitir que administradores reservem e cancelem vagas para alunos com matrícula ativa, sem duplicar reservas ativas nem exceder a capacidade.
- Registrar a situação de comparecimento da reserva após a sessão e apresentar a ocupação de cada sessão.
- Disponibilizar relatórios agregados de matrículas ativas, pagamentos e inadimplência, frequência e ocupação de aulas/reservas.
- Restringir a navegação e o acesso direto às páginas de gestão existentes e novas a usuários `admin`, preservando a autorização correspondente no backend.
- Verificar se os endpoints publicados de gestão de funcionários estão disponíveis; sua implementação ou sincronização não faz parte desta change e eventual ausência será reportada como bloqueio separado.
- Manter as interfaces exclusivamente em Reflex e regras de negócio e persistência no Xano.

## Capabilities

### New Capabilities

- `modality-management`: administrar modalidades oferecidas pela academia.
- `class-session-management`: administrar sessões individuais de aulas com capacidade e instrutor.
- `class-reservation-management`: reservar e acompanhar vagas de alunos em sessões.
- `management-reports`: consultar indicadores agregados da operação da academia.

### Modified Capabilities

- `authentication`: acrescentar controle administrativo da navegação e do acesso direto a páginas de gestão.

## Impact

- Novas tabelas, endpoints autenticados e regras de capacidade, reserva e comparecimento em XanoScript; os arquivos locais e o workspace publicado devem ser comparados antes da implementação.
- Novos clientes e páginas Reflex para modalidades, agenda de sessões, reservas e relatórios, além de uma barreira de interface para páginas de gestão. A autorização do backend continua obrigatória.
- A verificação de funcionários depende de confirmar no workspace publicado os endpoints que não aparecem na pasta local `xano/api/`.
- Não há dependências novas previstas. Os relatórios serão agregados e não introduzirão dados pessoais além do necessário para as operações administrativas.
