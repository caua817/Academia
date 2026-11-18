# Spec Delta

## ADDED Requirements

### Requirement: Funcionários convidados podem definir a própria senha por convite

O sistema SHALL permitir que uma pessoa com convite pendente e válido defina a senha da própria conta de funcionário. O convite SHALL expirar, ser aceito uma única vez e não SHALL criar uma sessão autenticada após a ativação.

#### Scenario: Funcionário aceita convite válido
- **WHEN** a pessoa abre um convite válido de uma conta de funcionário pendente e informa uma senha válida e sua confirmação
- **THEN** o sistema define a senha, invalida o convite, confirma a ativação e direciona a pessoa ao login sem criar uma sessão autenticada

#### Scenario: Convite expirado ou já utilizado
- **WHEN** a pessoa tenta aceitar um convite expirado ou previamente utilizado
- **THEN** o sistema rejeita a ativação, não altera a conta e informa que é necessário solicitar um novo convite ao administrador

#### Scenario: Duas aceitações concorrentes do mesmo convite
- **WHEN** duas solicitações tentam aceitar simultaneamente o mesmo convite pendente
- **THEN** somente uma define a senha e consome o convite; a outra é rejeitada sem substituir a senha definida pela primeira

#### Scenario: Senha inválida ou confirmação divergente
- **WHEN** a pessoa informa uma senha fora da política vigente ou uma confirmação diferente
- **THEN** o sistema não define a senha, informa o erro sem expor dados internos e mantém o convite disponível até uma ativação bem-sucedida ou sua expiração

#### Scenario: Conta não corresponde a convite pendente de funcionário
- **WHEN** o token não corresponde ao e-mail, a conta não existe, já possui senha ou não tem perfil de funcionário permitido
- **THEN** o sistema rejeita a ativação sem modificar a conta nem criar uma sessão

#### Scenario: URL do frontend não está configurada para envio de convite
- **WHEN** o administrador solicita um convite sem que o destino público de ativação esteja configurado e validado
- **THEN** o sistema não envia o convite nem apresenta a operação como bem-sucedida

### Requirement: O fluxo de ativação protege token e senha

O sistema SHALL tratar o token de convite e a senha como credenciais temporárias, sem registrá-los em logs, armazená-los em persistência no navegador ou retorná-los em respostas da API. O token SHALL ser transportado sem inclusão em requisições HTTP de navegação ou cabeçalhos `Referer`.

#### Scenario: Pessoa abre a página do convite
- **WHEN** a página lê as informações necessárias para validar o convite
- **THEN** o token é removido do endereço visível antes de continuar o fluxo e não é enviado como parte da navegação HTTP ou do cabeçalho `Referer`

#### Scenario: Ativação é processada
- **WHEN** a pessoa envia a senha e a confirmação para ativar a conta
- **THEN** o sistema não registra senha ou token em logs, não os persiste no armazenamento do navegador e não retorna credenciais na resposta
