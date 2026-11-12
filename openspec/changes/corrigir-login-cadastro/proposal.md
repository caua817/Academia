# Proposta: Corrigir login e cadastro

## Por quê

A tela já possui chamadas para login e cadastro, mas precisa oferecer um fluxo de autenticação previsível, mostrar erros de formulário no momento certo e tratar falhas da API sem deixar o usuário sem feedback. Corrigir a abertura/fechamento do cadastro e validar campos vazios melhora o acesso sem enfraquecer as permissões dos endpoints protegidos.

## O que muda

- Validar os campos de e-mail e senha antes de enviar o login e apresentar mensagens para campos vazios, credenciais inválidas, resposta inesperada e falha de conexão.
- Corrigir a abertura e o fechamento do modal de cadastro, exibindo erro ao clicar em “Cadastrar” com campos obrigatórios vazios.
- Validar nome, e-mail e senha antes de chamar a API de cadastro e apresentar erros sem falso sucesso.
- Centralizar as chamadas HTTP de login e cadastro, sem token na requisição pública e sem registrar ou exibir credenciais.
- Manter o token retornado pelo login no estado de sessão para uso posterior em APIs protegidas.
- Preservar o perfil `member` atribuído pelo endpoint de cadastro; não conceder privilégios administrativos automaticamente.

Fora do escopo: modificar Xano, alterar regras de autenticação/autorização do backend, criar contas administrativas, implementar recuperação de senha ou mudar permissões das áreas de alunos.

## Capabilities

### Novas capabilities

- `authentication`: autenticação de usuários por login e cadastro público.

### Modified Capabilities

Nenhuma. O projeto ainda não possui specs consolidadas.

## Impact

- Frontend Reflex: `academia/login.py` e telas de acesso.
- Cliente HTTP: serviço de autenticação em `academia/services/`, usando `/auth/login` e `/auth/signup` existentes.
- Testes: cobertura local mockada para payloads, token de resposta, falhas HTTP, conexão e validação vazia.
- Xano: nenhum arquivo ou workspace será alterado ou validado nesta change.
- Dependências: nenhuma nova dependência prevista.
