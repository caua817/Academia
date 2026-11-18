# Tarefas

## 1. Preparação segura do deploy

- [x] 1.1 Adicionar `reflex-hosting-cli>=0.2.2` ao `requirements.txt`, atualizar o venv e verificar que `reflex cloud whoami` e os comandos Cloud não são mais interrompidos pelo aviso de versão.
- [x] 1.2 Criar token Deploy no escopo da organização Reflex autorizada (o portal não oferece escopo por projeto), salvá-lo pelo mecanismo seguro do CLI e confirmar identidade, plano e custos; não expor o token e não selecionar plano pago nem autorizar cobranças sem aprovação explícita.
- [x] 1.3 Executar uma auditoria local de dependências e revisar os arquivos do pacote, confirmando que `.env`, `XANO_TEST_ADMIN_TOKEN` e `XANO_TEST_MEMBER_TOKEN` não serão enviados, sem fazer upload do código para serviços externos.

## 2. Publicação do frontend

- [ ] 2.1 Publicar a aplicação Reflex no hosting autorizado, excluindo explicitamente `.env`; registrar a origem HTTPS estável retornada pelo provedor.
- [ ] 2.2 Abrir a origem publicada e `/ativar-funcionario` em HTTPS e confirmar que ambas respondem sem erro antes de configurar convites.

## 3. Configuração e validação Xano

- [ ] 3.1 Configurar somente a origem HTTPS publicada em `frontend_base_url` no workspace Xano, sem fazer push geral de XanoScript; conferir o valor configurado.
- [ ] 3.2 Executar um convite usando conta e endereço de teste autorizados e confirmar que o link recebido aponta à página publicada, abre em HTTPS e não expõe o token fora do fragmento nem nas respostas/logs.
- [ ] 3.3 Completar a ativação com a conta de teste e confirmar o login; se o teste autenticado não puder ser executado, não enviar convites reais e registrar a limitação.
