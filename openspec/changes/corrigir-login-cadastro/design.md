# Design: Corrigir login e cadastro

## Contexto

Ver [proposal.md](./proposal.md) para motivação e escopo, e [spec.md](./specs/authentication/spec.md) para o contrato comportamental. O estado Reflex `LoginState` faz as chamadas HTTP diretamente dentro de `login.py`. A API Xano local expõe `POST /auth/login` e `POST /auth/signup` sem exigir autenticação na requisição; login e cadastro retornam `authToken`. O cadastro público atribui o papel `member`.

## Objetivos / Não objetivos

**Objetivos:**

- Validar os campos antes de qualquer chamada HTTP.
- Garantir uma transição consistente de abrir/fechar o modal do cadastro.
- Tratar status HTTP, falha de conexão e resposta JSON inválida com mensagens seguras.
- Manter o token de login somente no estado de sessão server-side após autenticação válida.

**Não objetivos:**

- Alterar os endpoints ou executar operações no Xano.
- Conceder `admin` a contas cadastradas publicamente.
- Mudar permissões das páginas existentes ou tornar APIs protegidas públicas.

## Decisões

### Separar chamadas HTTP de eventos de interface

Criar um cliente de autenticação em `academia/services/auth_client.py`, reaproveitando `API_BASE_URL` e `httpx`. O cliente envia somente o payload ao login/cadastro, sem cabeçalho `Authorization`. Erros serão expostos por uma exceção de autenticação com status quando disponível; corpo de resposta e credenciais não serão incluídos nas mensagens.

**Alternativa descartada:** manter requisições em `LoginState`. Isso dificulta testar o contrato sem executar eventos da interface e mantém tratamento HTTP duplicado.

### Validar campos antes de alterar estado de carregamento

O login exige e-mail e senha não vazios; o cadastro exige nome, e-mail e senha não vazios, considerando espaços em branco como campo vazio. A senha original é enviada sem normalização; nome e e-mail são aparados, e e-mail é normalizado em minúsculas. A API permanece responsável pela validação final.

### Tratar o token do login de maneira explícita

O cliente aceita `authToken` ou `token` na resposta para compatibilidade com o frontend existente e exige que seja uma string não vazia. Em falha, não altera `auth_token`. Em sucesso, guarda o token na sessão e redireciona para `/`. O cadastro continua exibindo confirmação para o usuário fazer login; o token retornado pelo signup não será usado para elevar nem para contornar o perfil `member`.

### Usar valor de abertura explícito para o diálogo

O botão “Cadastre-se” define a abertura como verdadeira; o callback do diálogo recebe e aplica o booleano real do componente, em vez de alternar às cegas. Erros antigos são limpos quando o formulário é aberto ou fechado.

## Riscos / Trade-offs

- **[Risco]** Contas criadas via signup têm papel `member`, enquanto áreas operacionais existentes podem exigir `admin`. **→ Mitigação:** preservar o papel do backend, não forçar acesso administrativo e mostrar erros 403 existentes sem mascará-los.
- **[Risco]** Uma API retorna um formato diferente do esperado. **→ Mitigação:** validar objeto/token e mostrar erro de resposta inválida, sem sucesso falso.

## Plano de migração

1. Adicionar o cliente HTTP, ajustar `LoginState` e corrigir o modal.
2. Cobrir validação e contrato HTTP com transporte mockado local.
3. Executar testes focados, `reflex compile --dry` e conferir login/cadastro na interface sem credenciais reais.
4. Nenhuma migração de dados ou alteração Xano é necessária.
