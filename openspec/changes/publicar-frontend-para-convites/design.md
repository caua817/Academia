# Design

## Contexto

Veja [proposal.md](./proposal.md) para a motivação e [spec.md](./specs/employee-management/spec.md) para o contrato observável. Hoje o Reflex roda somente em `localhost:3000`; o endpoint Xano de convites valida `frontend_base_url` antes de criar a conta e enviar e-mail. O `reflex-hosting-cli` instalado está na versão 0.2.0 e encerra comandos Cloud ao detectar a 0.2.2; o comando legado `reflex login` também está desativado nesta versão do Reflex. O CLI Xano não oferece comando de configuração de variáveis do workspace.

## Objetivos / Não objetivos

**Objetivos:**

- Obter uma origem HTTPS estável do hosting Reflex e apontar o Xano para ela.
- Atualizar o CLI de hosting para a versão mínima compatível com os comandos Cloud.
- Manter credenciais e variáveis locais fora do pacote de deploy.
- Confirmar que a página de ativação está acessível antes de liberar convites.

**Não objetivos:**

- Publicar o workspace Xano ou alterar os endpoints XanoScript.
- Criar domínio próprio, enviar convites para funcionários reais ou alterar regras de autenticação.
- Usar túnel temporário, URL localhost, variável de teste ou fallback HTTP.

## Decisões

### Usar Reflex Cloud com token no escopo organizacional autorizado

Atualizar `reflex-hosting-cli` para `>=0.2.2` no `requirements.txt` e no ambiente virtual, pois a versão atual bloqueia os comandos Cloud. O portal oficial informa que tokens têm escopo da organização selecionada, não de um projeto específico; não há token limitado ao projeto disponível. O grupo autorizou o escopo da organização selecionada para esta publicação. Criar o token apenas nessa organização e salvá-lo pelo mecanismo seguro do CLI (`reflex cloud token --set`), sem exibir ou copiar o segredo no chat. Confirmar a identidade, o plano e os custos antes de qualquer deploy. Não selecionar um plano pago nem autorizar cobranças sem aprovação explícita. Antes de publicar, executar uma auditoria local de dependências e revisar a lista de arquivos incluídos, sem enviar o código a serviços externos.

**Alternativas consideradas:** túnel HTTPS temporário, descartado porque o link é enviado por e-mail e precisa continuar funcionando fora da sessão local; domínio próprio, não disponível no momento.

### Excluir configuração local e segredos do deploy

Não usar `.env` como `--envfile` nem como fonte de configuração do deploy. Excluir explicitamente `.env` do pacote backend e verificar que `XANO_TEST_ADMIN_TOKEN` e `XANO_TEST_MEMBER_TOKEN` não sejam publicados. O app usa um endpoint Xano configurado pelo código ou por uma variável de ambiente de produção não secreta; tokens de teste nunca são necessários em runtime.

### Configurar a origem no Xano somente depois de obter a URL

Após o deploy fornecer a URL HTTPS definitiva, configurar apenas essa origem, sem caminho de página, na variável `frontend_base_url` do workspace Xano. A variável deve ser alterada pelo mecanismo oficial disponível para o workspace; não enviar o `.xs` do endpoint nem fazer push geral para resolver uma configuração de ambiente.

### Validar antes de considerar o cadastro disponível

Verificar a página pública `/ativar-funcionario` na origem publicada e executar o fluxo com uma conta/endereço de teste autorizado. Confirmar que o link enviado aponta para a origem publicada, que o endpoint não cria conta quando a origem está ausente/inválida e que token e senha não aparecem em logs ou respostas. Se não houver ambiente/conta de teste autorizados, parar antes de enviar convite real.

## Riscos / Trade-offs

- **[Risco]** O Reflex Cloud pode exigir autenticação, cota ou plano pago. **→ Mitigação:** consultar os limites da conta antes de publicar; parar e reportar qualquer custo ou confirmação não prevista.
- **[Risco]** O token disponível concede acesso de CLI à organização inteira, não somente a este projeto. **→ Mitigação:** usar somente a organização autorizada, manter o token no armazenamento local seguro e não incluí-lo em código, arquivos versionados, logs ou mensagens.
- **[Risco]** Arquivos de ambiente locais podem conter tokens de teste. **→ Mitigação:** excluir `.env`, não usar `--envfile`, executar uma auditoria local e revisar o pacote antes do deploy.
- **[Risco]** Uma URL de deploy pode mudar ou não estar acessível publicamente. **→ Mitigação:** testar a URL final e só então atualizar `frontend_base_url`.
- **[Risco]** O runner de testes Xano pode não fornecer contexto autenticado. **→ Mitigação:** não tratar 401 do runner como sucesso do convite; validar com conta de teste autorizada ou deixar o fluxo explicitamente bloqueado.

## Plano de migração

1. Atualizar o requisito do CLI de hosting e instalar a versão compatível no venv.
2. Salvar um token de deploy no escopo da organização autorizada pelo mecanismo seguro do CLI e confirmar identidade/plano e custos, sem selecionar um plano pago ou autorizar cobranças.
3. Executar auditoria local de dependências, excluir segredos e revisar o conjunto de arquivos a publicar, sem enviar o código a serviços externos.
4. Publicar o app e validar a página `/ativar-funcionario` em HTTPS.
5. Configurar `frontend_base_url` no Xano com a origem publicada e verificar a configuração.
6. Testar convite e ativação em conta de teste; não enviar convite real antes da validação.
7. Para rollback, suspender convites e restaurar a configuração anterior do Xano; não remover contas nem links já enviados.
