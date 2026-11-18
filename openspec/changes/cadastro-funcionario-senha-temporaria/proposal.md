# Proposta: Cadastro de funcionários com senha temporária

## Por quê

O cadastro atual envia um convite por e-mail cujo link depende de uma origem HTTPS pública, indisponível enquanto o frontend roda somente em `localhost`. O grupo aprovou um fluxo administrativo presencial para permitir o cadastro sem hospedar publicamente a aplicação.

## O que muda

- Permitir que administradores criem funcionários definindo uma senha temporária, entregue presencialmente ao funcionário, sem depender de hospedagem pública.
- Manter o convite por e-mail como alternativa quando `frontend_base_url` HTTPS estiver configurada.
- Fazer a senha temporária expirar em 24 horas e exigir sua troca antes de conceder uma sessão normal ou acesso às funcionalidades do sistema.
- Permitir que um administrador reemita uma senha temporária para uma conta cujo prazo expirou.
- Não exigir `frontend_base_url`, envio de e-mail ou uma URL pública para o cadastro presencial por senha temporária.
- Preservar a autenticação de contas existentes e a proibição de cadastro público.
- Proteger a senha temporária: campo mascarado, nunca devolvida pela API, registrada em logs ou mantida na lista de funcionários.
- Manter o fluxo de ativação por convite existente; o administrador poderá escolher o cadastro presencial mesmo quando o frontend não tiver uma origem pública.

## Capabilities

### Novas capabilities

Nenhuma.

### Capabilities modificadas

- `employee-management`: adicionar o provisionamento administrativo e a reemissão de credenciais temporárias em pessoa.
- `authentication`: exigir troca da senha temporária antes de criar uma sessão normal, sem alterar o login de contas existentes.

## Impacto

- Frontend Reflex: formulário de cadastro administrativo, tratamento do primeiro login e reemissão após expiração.
- Xano: endpoint administrativo de provisionamento/reemissão, controle de validade e troca obrigatória da senha antes de emitir sessão.
- Modelo `user` e endpoints de login/autenticação; os detalhes de XanoScript devem ser confirmados com a documentação oficial durante a implementação.
- Testes de funcionário, autenticação e autorização.
- A change `publicar-frontend-para-convites` continua necessária somente para enviar convites por e-mail; não será necessário publicar o frontend para habilitar o cadastro presencial por senha temporária.
