# Spec Delta

## ADDED Requirements

### Requirement: Convites usam uma origem HTTPS publicada para ativação
O sistema SHALL gerar links de convite para a origem HTTPS pública e configurada da aplicação, levando à página de ativação de funcionário. O endpoint SHALL rejeitar a solicitação antes de criar a conta ou enviar e-mail quando a origem estiver ausente ou inválida.

#### Scenario: Administrador envia convite com origem publicada
- **WHEN** um administrador envia dados válidos e a origem HTTPS publicada está configurada
- **THEN** o funcionário recebe um link para `/ativar-funcionario` na aplicação publicada, com o token no fragmento da URL

#### Scenario: Origem de ativação não está configurada
- **WHEN** um administrador envia convite sem uma origem HTTPS válida configurada
- **THEN** a API rejeita a solicitação sem criar a conta e sem enviar e-mail

#### Scenario: Convite é aberto pelo funcionário
- **WHEN** o funcionário abre o link recebido em um dispositivo com acesso à internet
- **THEN** a página pública de ativação carrega pela origem HTTPS publicada e permite definir a senha sem expor o token após a abertura
