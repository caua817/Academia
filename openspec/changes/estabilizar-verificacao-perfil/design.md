# Design

## Context

Veja [proposal.md](./proposal.md) para a motivação e [specs/authentication/spec.md](./specs/authentication/spec.md) para o contrato observável. `require_roles` é assíncrona, mas chama `XanoClient.get_current_user`, que realiza HTTP síncrono com timeout de 10 segundos. Tanto essa função quanto o fluxo de login convertem falhas da consulta em uma mensagem genérica; as páginas protegidas já oferecem uma ação explícita de atualização.

## Goals / Non-Goals

**Goals:**

- Impedir que a chamada síncrona de perfil bloqueie o event loop usado pelo Reflex.
- Recuperar uma única vez de falhas potencialmente transitórias sem amplificar 429 nem repetir respostas de autenticação.
- Reduzir chamadas redundantes a `/auth/me` reutilizando o perfil verificado durante a sessão autenticada.
- Manter a autorização fechada por padrão e distinguir sessão expirada, proibição, limitação temporária e indisponibilidade.
- Cobrir o fluxo de login e a revalidação nas rotas protegidas com testes.

**Non-Goals:**

- Alterar permissões por perfil, tokens ou autorização no backend.
- Usar o cache do frontend como mecanismo de autorização ou ignorar validações de perfil feitas pelo backend.
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

### Reutilizar o perfil verificado dentro da sessão

Guardar o perfil verificado em uma variável privada do estado Reflex de login, associada a um resumo do token atual. Após o login, preencher o cache somente depois que `/auth/me` retornar um perfil válido. Para sessões existentes sem cache, a primeira navegação protegida realiza a verificação normal e preenche o cache após sucesso; as navegações seguintes reutilizam o perfil sem nova chamada. Uma falha de verificação não cria nem atualiza o cache, e um cache que não corresponda ao token atual nunca libera a rota.

Limpar o perfil verificado ao iniciar um novo login, trocar o token ou encerrar/limpar a sessão. O cache é apenas uma otimização de navegação: os endpoints protegidos do Xano, incluindo mensalidades e pagamentos, continuam validando o usuário ativo e seu perfil em cada operação. Se o perfil mudar durante a sessão, o backend rejeita a operação conforme a permissão atual; a interface atualiza o perfil de navegação em um novo login.

**Alternativa considerada:** chamar `/auth/me` em toda navegação para refletir imediatamente as mudanças de perfil na interface. Rejeitada porque gera chamadas redundantes, e a autorização efetiva já é verificada no backend em cada operação protegida.

## Risks / Trade-offs

- **[Risco]** Uma única repetição ainda pode aumentar a carga quando o serviço está degradado. **→ Mitigação:** limitar a uma tentativa, aplicá-la somente ao GET do perfil e excluir 429 e erros definitivos.
- **[Risco]** Uma indisponibilidade prolongada ainda impede acesso às páginas protegidas. **→ Mitigação:** manter mensagem explícita, interface responsiva e tentativa manual disponível; não autorizar usando dados de perfil antigos.
- **[Trade-off]** A interface pode manter o perfil de navegação até o fim da sessão após uma alteração de perfil. **→ Mitigação:** cada endpoint protegido revalida a permissão atual no Xano; um novo login atualiza o perfil exibido pela interface.
- **[Trade-off]** A retentativa pode adicionar um pequeno atraso no caso de falha transitória. O limite e o curto intervalo evitam espera indefinida.

## Plano de migração

1. Implementar a execução não bloqueante da verificação no login e nas rotas protegidas.
2. Adicionar retentativa restrita aos erros transitórios permitidos e tratamento explícito para 401/403/429.
3. Reutilizar o perfil verificado no estado privado da sessão e invalidá-lo quando o token ou a sessão mudar.
4. Adicionar testes para recuperação, cache por token, invalidação, acesso negado, preservação de sessão e responsividade.
5. Executar os testes direcionados, a suíte relevante, `reflex compile --dry` e `git diff --check`.
6. Validar o fluxo autenticado no navegador compartilhado; se o backend estiver indisponível, manter essa validação reportada como pendente.

## Open Questions

Nenhuma.
