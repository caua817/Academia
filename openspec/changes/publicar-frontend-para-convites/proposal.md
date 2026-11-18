# Proposta: Publicar o frontend para convites de funcionários

## Por quê

O endpoint de convite exige `frontend_base_url` com HTTPS para gerar o link de ativação, mas o aplicativo está disponível apenas em `localhost`, que não pode ser acessado pelo funcionário convidado. Por isso, o Xano rejeita o cadastro com HTTP 400 antes de criar a conta.

## O que muda

- Publicar o app Reflex no hosting do Reflex, autorizado pelo grupo, para obter uma origem HTTPS acessível aos funcionários.
- Criar uma credencial de deploy no escopo da organização Reflex selecionada; o portal não oferece escopo por projeto, e o grupo autorizou esse escopo organizacional para esta publicação.
- Configurar essa origem no Xano como `frontend_base_url`, preservando a rota `/ativar-funcionario` e o token no fragmento do link.
- Atualizar o requisito do `reflex-hosting-cli` para uma versão compatível com os comandos de hosting usados no deploy.
- Excluir arquivos locais de ambiente e credenciais do pacote de deploy; validar a página publicada e o fluxo de convite antes de considerar o cadastro disponível.
- Não usar `localhost`, origem HTTP ou fallback que crie contas sem um link de ativação utilizável.
- Não selecionar um plano pago nem autorizar cobranças sem aprovação explícita.

## Capabilities

### Novas capabilities

Nenhuma.

### Capabilities modificadas

- `employee-management`: garantir que convites enviados apontem para a página pública HTTPS de ativação do aplicativo publicado.

## Impacto

- Hosting externo Reflex Cloud e configuração de deploy da aplicação Reflex.
- Credencial de CLI com acesso no escopo da organização Reflex selecionada.
- Dependência de ferramenta `reflex-hosting-cli` com versão mínima compatível com o deploy.
- Variável de ambiente `frontend_base_url` no workspace Xano.
- Fluxo de convite e ativação em `academia/funcionarios.py`, `academia/ativacao_funcionario.py` e `xano/api/authentication/funcionarios/convites_POST.xs`.
- Custos, limites e disponibilidade do hosting dependem da conta/plano Reflex utilizado.
