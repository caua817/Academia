# Spec Delta

## MODIFIED Requirements

### Requirement: Administradores podem convidar funcionários por e-mail

O sistema SHALL permitir que administradores criem funcionários por cadastro presencial, informando nome, e-mail, perfil permitido (`admin`, `recepcionista` ou `instrutor`) e uma senha temporária definida para entrega presencial. A senha temporária SHALL expirar em 24 horas, e esse cadastro SHALL funcionar sem `frontend_base_url` e sem envio de e-mail. O sistema SHALL manter o convite por e-mail como alternativa somente quando uma origem HTTPS válida estiver configurada; convites existentes SHALL continuar válidos conforme sua expiração original.

#### Scenario: Administrador cadastra funcionário para entrega presencial
- **WHEN** um administrador informa dados válidos e uma senha temporária que atende à política de senha
- **THEN** a API cria a conta sem exigir origem HTTPS ou enviar e-mail e retorna somente dados operacionais, sem devolver a senha

#### Scenario: Convite enviado com sucesso
- **WHEN** um administrador escolhe o convite por e-mail, informa dados válidos e existe uma origem HTTPS válida configurada
- **THEN** o sistema envia o convite para a página pública de ativação e atualiza a lista sem revelar token ou senha

#### Scenario: Convite por e-mail sem origem HTTPS
- **WHEN** um administrador escolhe o convite por e-mail sem uma origem HTTPS válida configurada
- **THEN** a API rejeita o convite sem criar a conta nem enviar e-mail, enquanto o cadastro presencial por senha temporária permanece disponível

#### Scenario: Administrador reemite credencial temporária expirada
- **WHEN** um administrador define uma nova senha temporária para uma conta de funcionário cujo prazo expirou
- **THEN** a API substitui a credencial anterior, reinicia a validade por 24 horas e mantém obrigatória a troca no primeiro acesso

#### Scenario: Senha temporária expira antes do primeiro acesso
- **WHEN** o funcionário tenta autenticar com uma senha temporária após 24 horas
- **THEN** a API não concede sessão normal e informa que é necessário solicitar nova credencial ao administrador

#### Scenario: Convite com dados inválidos ou e-mail já utilizado
- **WHEN** a API rejeita os dados ou encontra um e-mail associado a outra conta
- **THEN** não cria nem altera uma conta e a interface apresenta a falha sem confirmar o cadastro

#### Scenario: Administrador sem autorização tenta cadastrar funcionário
- **WHEN** uma pessoa sem perfil `admin` tenta criar ou reemitir credencial temporária
- **THEN** a API retorna acesso negado e não cria nem altera a conta

#### Scenario: Convite existente é ativado
- **WHEN** um funcionário usa um convite por e-mail ainda válido que foi emitido antes da mudança
- **THEN** o fluxo de ativação existente continua aceitando o convite sem exigir a senha temporária presencial

### Requirement: A interface protege credenciais de funcionários

O sistema SHALL exibir somente os dados operacionais necessários e nunca apresentar senha temporária em tabelas, mensagens de resultado ou respostas da API. A interface de cadastro SHALL aceitar a senha temporária em campo mascarado apenas durante a operação administrativa e SHALL limpá-la após a tentativa, sem persistir a senha em estado durável ou logs.

#### Scenario: Administrador cadastra ou consulta funcionário
- **WHEN** o administrador cria ou consulta uma conta
- **THEN** a interface mostra os campos de senha apenas como entrada temporária mascarada e exibe em tabelas e mensagens somente nome, e-mail, perfil, situação e estado operacional

#### Scenario: Convite e consulta de funcionário
- **WHEN** um administrador convida ou consulta uma conta
- **THEN** a interface utiliza nome, e-mail, perfil, situação e estado do convite, sem exibir senha ou token de autenticação

#### Scenario: Operação de senha temporária termina
- **WHEN** a solicitação de cadastro ou reemissão termina com sucesso ou falha
- **THEN** a interface limpa os campos de senha e não os inclui em logs, mensagens ou dados de sessão persistidos
