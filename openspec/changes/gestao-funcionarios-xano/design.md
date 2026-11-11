# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de `employee-management` e `authentication`. A tela Reflex e o `XanoClient` já definem as operações de funcionários, mas elas não aparecem no pull isolado do workspace. A tabela autenticada `user` atualmente aceita `admin` e `member`, tem senha opcional e não possui situação; login, autenticação por link e a função compartilhada de autorização não verificam uma conta inativa. O cliente HTTP também não encaminha o token recebido.

## Goals / Non-Goals

**Goals:**

- Fazer o backend cumprir o contrato já usado pela tela de funcionários.
- Disponibilizar contas de instrutor com perfil e situação consultáveis pelas sessões da Fase 2.
- Negar autenticação e operações protegidas quando a conta estiver inativa, inclusive para tokens emitidos anteriormente.
- Preservar dados legados e evitar exposição de senha, hash ou token de funcionário.

**Non-Goals:**

- Criar outra tela de gestão de funcionários; a tela existente só será ajustada para refletir a proteção de contas `admin`.
- Remover o papel legado `member` ou conceder a recepcionistas e instrutores as permissões administrativas existentes.
- Publicar alterações no workspace Xano ou modificar registros reais sem aprovação explícita.
- Implementar modalidades, sessões ou reservas, que permanecem na change `fase-dois-operacao`.

## Decisions

### Usar a tabela autenticada existente como fonte dos funcionários

Estender `user` com os papéis `recepcionista` e `instrutor` e uma situação ativa/inativa, mantendo os papéis já aceitos. Contas anteriores sem valor de situação permanecem ativas para compatibilidade; o valor retornado pela API será apresentado como `Ativo` ou `Inativo`. Contas com papel legado `member` continuam autenticáveis, mas não são listadas nem administradas como funcionários.

Alternativa descartada: criar uma tabela paralela de funcionários, que duplicaria identidade, e-mail e controle de sessão já mantidos pelo Xano Auth.

### Aplicar a situação ativa no backend em cada caminho de autenticação

Login por senha, troca de link individual, consulta de identidade e a função compartilhada de autorização verificam a situação da conta. Desativar uma conta não exige revogar fisicamente tokens já emitidos: as operações protegidas e a identidade recusam o token enquanto a conta estiver inativa. Os níveis `recepcionista` e `instrutor` não recebem acesso aos endpoints que exigem `admin`.

Alternativa descartada: bloquear somente o login, pois tokens emitidos antes da desativação continuariam funcionando.

### Convidar sem manipular senhas pelo administrador

O endpoint de convite cria a conta sem senha definida pelo administrador e envia um link individual de definição de senha usando o mecanismo existente de magic link. Uma conta ainda sem senha pode receber novo link ao repetir o convite após falha de envio; e-mails já associados a contas concluídas são rejeitados. A API calcula o estado do convite sem retornar dados de credencial.

Alternativa descartada: aceitar uma senha no formulário administrativo, o que aumentaria exposição e contrariaria o contrato Reflex existente.

### Impedir desativação ou rebaixamento de contas administrativas

Por decisão do grupo, a aplicação rejeitará a desativação ou o rebaixamento de qualquer conta com perfil `admin`, ainda que existam outros administradores. Essa restrição evita que operações concorrentes removam o acesso administrativo sem depender de garantias de isolamento que não puderam ser confirmadas no ambiente Xano disponível. A reativação de uma conta `admin` legada inativa continua permitida.

O endpoint continuará permitindo a edição de nome e e-mail de contas `admin`; a interface manterá o perfil fixo e não oferecerá a ação de desativação. O desligamento ou rebaixamento administrativo exigirá um processo fora da aplicação, aprovado e executado pelo grupo.

### Encaminhar o token de sessão no cliente HTTP

O `XanoClient` enviará o token recebido no cabeçalho `Authorization` no formato aceito pelo Xano e não o registrará em logs. Testes com transporte HTTP mockado verificam o cabeçalho e preservam a rejeição de tokens vazios.

Alternativa descartada: manter o placeholder atual, que impede qualquer chamada autenticada apesar de a tela ter uma sessão.

## Risks / Trade-offs

- **[Risco]** O provedor de e-mail pode falhar depois da criação da conta. → **Mitigação:** manter a conta pendente sem senha, reportar a falha e permitir que a mesma operação reenvie um link sem duplicar o usuário.
- **[Risco]** Contas existentes não têm a nova situação preenchida. → **Mitigação:** interpretar valor ausente como ativo e não alterar os papéis legados.
- **[Risco]** Tokens de usuários desativados continuam criptograficamente válidos até expirarem. → **Mitigação:** conferir a situação atual na identidade e na autorização compartilhada a cada solicitação protegida.
- **[Trade-off]** Nenhuma conta `admin` poderá ser desligada pela aplicação, mesmo quando houver outros administradores. → **Mitigação:** ocultar a ação na interface e exigir processo administrativo externo para esses casos.
- **[Risco]** O workspace publicado não contém os endpoints e não há uma sessão administrativa disponível para leitura autenticada. → **Mitigação:** validar os arquivos localmente e usar apenas `xano workspace push --dry-run`; publicação e teste no runtime aguardam aprovação explícita.

## Migration Plan

1. Manter o pull isolado como referência e revisar o diff local antes de editar arquivos Xano.
2. Estender a tabela `user`, a autorização compartilhada e os caminhos de login sem remover ou reclassificar contas existentes.
3. Implementar os endpoints administrativos nos caminhos já usados pelo `XanoClient`, protegendo todas as contas `admin` contra desativação e rebaixamento.
4. Ajustar a tela Reflex existente para refletir essa restrição, corrigir o cabeçalho autenticado do cliente e executar testes direcionados, validação XanoScript e OpenSpec.
5. Revisar o diff e executar dry-run seletivo. Não fazer push real sem aprovação explícita.

Rollback: interromper a publicação se a validação falhar. Reverter as alterações de código sem apagar contas ou outros registros; manter campos e valores legados compatíveis.
