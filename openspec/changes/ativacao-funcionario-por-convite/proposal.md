# Proposta: Ativação de funcionário por convite

## Por quê

O Xano envia convites com um link para uma página de demonstração que retorna 404, impedindo o funcionário de definir a própria senha. A ativação precisa ter uma página real no Reflex e validar o convite sem expor credenciais ou criar uma sessão de acesso geral.

## O que muda

- Adicionar uma página pública no Reflex para receber, validar e consumir convites de funcionários e permitir que a pessoa defina e confirme sua senha.
- Alterar o link gerado pelo convite no Xano para apontar à página publicada do Reflex, usando configuração explícita de URL e transportando o token de uso único de forma que não seja enviado em requisições HTTP de navegação.
- Criar uma operação Xano de aceitação de convite que valide e consuma o token, confirme que a conta é uma conta de funcionário ainda sem senha e salve a senha com as regras já impostas pelo domínio, sem emitir token de autenticação.
- Tratar convite inválido, expirado, já utilizado, dados incompletos, senha fraca e falha de rede com mensagens seguras e opção apropriada de nova tentativa.
- Testar página e contrato da API com chamadas simuladas; validar XanoScript e revisar publicação em dry-run. Não publicar mudanças no workspace remoto sem aprovação explícita.

Ficam fora do escopo: cadastro público, recuperação geral de senha, login automático após ativação, alteração de perfis/permissões e envio de convites sem uma URL de frontend configurada.

## Capabilities

### Novas capabilities

Nenhuma.

### Modified Capabilities

- `employee-management`: definir a aceitação segura de convite e a ativação inicial da conta pelo funcionário.

## Impacto

- Frontend Reflex: registro de rota, estado e formulário público de definição de senha.
- Cliente HTTP: chamadas públicas para validar/aceitar convite e tratamento explícito de erro.
- Xano: endpoint de aceitação, link do e-mail de convite e uso seguro da configuração de URL do frontend.
- Testes automatizados de estado, contrato e segurança; nenhuma dependência nova prevista.
