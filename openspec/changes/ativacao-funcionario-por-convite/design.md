# Design

## Contexto

Veja [proposal.md](./proposal.md) para motivação e escopo, e [spec.md](./specs/employee-management/spec.md) para os comportamentos exigidos.

O Xano atual gera o convite para `1_start_here_demo_page#/update-password/...`; a navegação conferida no navegador retorna 404. O fluxo Xano de redefinição existente troca um token de uso único por um token de autenticação com validade de 24 horas, marca o primeiro token como usado antes da definição da senha e, em seguida, chama um endpoint autenticado. Esse fluxo não atende ao comportamento de ativação: uma falha depois da troca consome o convite antes da senha ser salva, e os logs atuais recebem objetos de usuário como metadados.

O app Reflex registra as páginas explicitamente em `academia/academia.py`. A camada `AuthenticationClient` faz chamadas públicas sem bearer token; as operações autenticadas residem no cliente Xano separado. A tabela Xano `user` já guarda o hash e a expiração do token no objeto `password_reset`, com senha marcada como tipo `password` e política mínima de oito caracteres, uma letra e um dígito.

## Objetivos / Não objetivos

**Objetivos:**

- Fazer o convite abrir uma rota pública real do Reflex.
- Validar o convite e gravar a senha usando Xano como autoridade, sem criar token de autenticação.
- Consumir o convite somente quando a senha for gravada com sucesso.
- Manter token e senha fora de armazenamento persistente do navegador, logs e respostas da API.

**Não objetivos:**

- Mudar o login existente ou o fluxo geral de recuperação de senha.
- Criar cadastro público ou permitir que uma pessoa escolha o próprio perfil.
- Tornar a página de ativação um novo mecanismo de autorização para as APIs administrativas.

## Decisões

### Criar uma rota pública Reflex dedicada

Adicionar a rota `/ativar-funcionario` fora do shell administrativo. A página lê e valida a referência do convite no fragmento da URL através dos atributos do router do Reflex, apaga o fragmento com redirecionamento para a mesma rota e mantém os dados necessários apenas durante a interação. O fragmento não é enviado na requisição HTTP de navegação; a remoção reduz exposição na barra de endereço e no histórico. Não guardar token ou senha em `localStorage`, cookies, logs de aplicação ou estado persistente.

O formulário solicita senha e confirmação e espelha a política atual da tabela `user` para feedback rápido. A API Xano continua sendo a autoridade final. Após sucesso, limpar os campos e direcionar a pessoa para `/login`; erros de token ou conta não revelam se um e-mail está cadastrado.

**Alternativa descartada:** reutilizar a página inicial de demonstração Xano. Ela retorna 404 para a rota de definição de senha observada.

### Publicar o destino do convite por configuração explícita

O endpoint de convite construirá a URL com uma variável de ambiente Xano `frontend_base_url`, apontando para a origem publicada do Reflex e a rota `/ativar-funcionario`. A referência efêmera (e-mail e token) ficará no fragmento, codificada de forma compatível com URL. Se a variável estiver ausente ou não representar uma origem HTTPS válida, o endpoint falhará antes de criar a conta ou enviar e-mail; não usar o domínio da API como fallback.

**Alternativa descartada:** derivar a URL de `$env.$api_baseurl`. Esse valor aponta para a API Xano, não para o frontend, e levou ao destino inválido atual.

### Aceitar o convite em uma operação pública atômica

Adicionar um endpoint anônimo específico de aceitação de convite, por exemplo `POST /funcionarios/convites/aceitar`, com e-mail, token, senha e confirmação. O endpoint deve:

1. Validar campos, confirmação e política de senha.
2. Localizar a conta pelo e-mail e permitir somente perfis de funcionário previstos com senha ainda não definida.
3. Comparar o token em texto com o hash guardado, verificar expiração e rejeitar tokens já usados.
4. Serializar aceitações concorrentes com o campo interno `user.invitation_lock_at`: adquirir o bloqueio dentro da transação e revalidar a conta e o convite depois da aquisição.
5. Em uma única gravação do usuário, persistir a senha usando o tipo Xano `password`, marcar o token como usado e liberar o bloqueio.
6. Retornar apenas uma confirmação genérica, sem dados da conta, senha ou token; nunca emitir token de autenticação.

Assim, erros de validação não consomem o convite, e apenas uma de duas aceitações concorrentes pode efetivar a senha. Não reutilizar `reset/magic-link-login`, pois ele emite um bearer token de 24 horas e consome o convite antes da persistência da senha.

**Alternativa descartada:** trocar o token por um token de autenticação e chamar `reset/update_password`. Isso cria uma credencial de sessão que não é necessária e separa o consumo do convite da gravação da senha.

### Registrar eventos sem credenciais

Se a ativação registrar auditoria, guardar apenas identificador interno, ação e metadados não sensíveis. Não encaminhar o objeto `user`, objeto `password_reset`, token, senha ou confirmação ao helper de log. A resposta HTTP também não ecoará esses campos.

### Tratar o segredo somente durante a interação

Um estado Reflex dedicado fará a chamada HTTP com token e campos de senha a partir de handlers server-side. O token de ativação não será colocado no estado público serializado como variável de UI; os campos da senha serão limpos depois de cada tentativa concluída. A API não devolverá credencial de sessão e o login permanecerá uma ação separada.

## Riscos / Trade-offs

- **[Risco]** A origem pública do Reflex pode variar entre ambientes. **→ Mitigação:** exigir `frontend_base_url` HTTPS por ambiente e falhar de forma explícita se não estiver configurada.
- **[Risco]** A URL fragmentada precisa ser lida e removida sem perder os parâmetros necessários. **→ Mitigação:** cobrir parsing de token/e-mail, limpeza do endereço e requisição de ativação em testes e verificar a rota no navegador sem token real.
- **[Risco]** O fluxo existente de redefinição compartilha o campo `password_reset`. **→ Mitigação:** a nova operação aceita apenas conta de funcionário sem senha, consome o mesmo token validado numa única gravação e não altera o endpoint de recuperação geral.
- **[Risco]** O helper de auditoria pode persistir campos sensíveis se receber a conta completa. **→ Mitigação:** emitir apenas metadados allowlisted e incluir teste/revisão para ausência de token e senha.

## Plano de migração

1. Implementar e testar a página pública e o cliente HTTP com respostas simuladas.
2. Implementar o endpoint Xano de aceitação e ajustar o link gerado pelo endpoint existente de convite.
3. Validar XanoScript, fluxo de token expirado/usado, política de senha, ausência de credenciais em respostas/logs e o endereço real da rota Reflex em ambiente local.
4. Revisar `git diff` e executar `xano workspace push --dry-run`. Não publicar no workspace remoto até aprovação explícita do grupo e configuração validada de `frontend_base_url`.
5. Para rollback, suspender novos convites e remover a rota/endpoint novo após verificar dependências; não apagar contas ou senhas já ativadas.

## Questões em aberto

Nenhuma decisão de escopo é deixada para a implementação. O grupo deverá fornecer/configurar a origem HTTPS pública do Reflex em cada ambiente antes de habilitar o envio real de convites.
