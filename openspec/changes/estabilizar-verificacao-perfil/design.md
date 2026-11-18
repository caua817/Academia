# Design

## Context

Veja [proposal.md](./proposal.md) para a motivação e [specs/authentication/spec.md](./specs/authentication/spec.md) para o contrato observável. `require_roles` é assíncrona, mas chama `XanoClient.get_current_user`, que realiza HTTP síncrono com timeout de 10 segundos. Tanto essa função quanto o fluxo de login convertem falhas da consulta em uma mensagem genérica; as páginas protegidas já oferecem uma ação explícita de atualização.

## Goals / Non-Goals

**Goals:**

- Impedir que a chamada síncrona de perfil bloqueie o event loop usado pelo Reflex.
- Recuperar uma única vez de falhas potencialmente transitórias sem amplificar 429 nem repetir respostas de autenticação.
- Manter a autorização fechada por padrão e distinguir sessão expirada, proibição, limitação temporária e indisponibilidade.
- Cobrir o fluxo de login e a revalidação nas rotas protegidas com testes.

**Non-Goals:**

- Alterar permissões por perfil, tokens ou autorização no backend.
- Retentar automaticamente gravações ou outras operações não idempotentes.
- Ocultar indisponibilidade persistente ou conceder acesso offline.
- Alterar ou reiniciar o workspace Xano como parte desta mudança.

## Decisions

### Isolar chamadas bloqueantes de perfil do event loop

Manter o cliente Xano síncrono compatível com os demais chamadores, mas executá-lo em uma thread de trabalho quando chamado pelo fluxo assíncrono de autorização. Tornar o evento de login assíncrono e executar também as chamadas HTTP de login/verificação fora do event loop. Isso resolve a causa de bloqueio sem introduzir uma segunda implementação HTTP.

**Alternativa considerada:** migrar todos os métodos do cliente Xano para HTTP assíncrono. Rejeitada por ampliar o escopo e exigir a conversão de numerosos fluxos que não estão relacionados à verificação de perfil.

### Retentativa limitada apenas para consulta segura

Centralizar a recuperação para a consulta GET do perfil: uma tentativa adicional após falha de transporte ou status 5xx, com pequeno atraso e limite fixo. Não repetir 401, 403, 429, respostas inválidas ou qualquer operação de escrita. Após falha persistente, deixar a atualização explícita da página como mecanismo de nova tentativa.

**Alternativa considerada:** repetir qualquer erro com backoff ou criar retentativas globais no cliente HTTP. Rejeitada porque pode agravar limites da API, repetir operações de resultado incerto ou esconder erros definitivos.

### Preservar a distinção entre sessão existente e novo login

Em rotas protegidas, uma falha temporária não limpa o token existente; a rota continua inacessível até nova verificação válida. Durante login, o novo token só é armazenado após verificação bem-sucedida, preservando o comportamento fail-closed. Erros 401 redirecionam para login, 403 negam acesso e 429 recebem orientação para aguardar.

## Risks / Trade-offs

- **[Risco]** Uma única repetição ainda pode aumentar a carga quando o serviço está degradado. **→ Mitigação:** limitar a uma tentativa, aplicá-la somente ao GET do perfil e excluir 429 e erros definitivos.
- **[Risco]** Uma indisponibilidade prolongada ainda impede acesso às páginas protegidas. **→ Mitigação:** manter mensagem explícita, interface responsiva e tentativa manual disponível; não autorizar usando dados de perfil antigos.
- **[Trade-off]** A retentativa pode adicionar um pequeno atraso no caso de falha transitória. O limite e o curto intervalo evitam espera indefinida.

## Plano de migração

1. Implementar a execução não bloqueante da verificação no login e nas rotas protegidas.
2. Adicionar retentativa restrita aos erros transitórios permitidos e tratamento explícito para 401/403/429.
3. Adicionar testes para recuperação, limite de tentativas, acesso negado, preservação de sessão e responsividade.
4. Executar os testes direcionados, a suíte relevante, `reflex compile --dry` e `git diff --check`.
5. Validar o fluxo autenticado no navegador compartilhado; se o backend estiver indisponível, manter essa validação reportada como pendente.

## Open Questions

Nenhuma.
