# Design: Conectar o frontend (Reflex) ao backend (Xano)

## Contexto

- Frontend: Reflex (Python), app já inicializado em `academia/`.
- Backend: Xano, workspace `academia` (ID 151343), código local em
  `xano/`, com autenticação de fábrica já presente.
- Regra do `AGENTS.md`: o frontend não decide regras de negócio nem de
  segurança; ele só consome a API.

## Decisões

### 1. Onde fica a URL da API

Variável de ambiente `API_BASE_URL`, lida no Reflex a partir de um
arquivo `.env` na raiz do projeto (fora do Git). O projeto já tem um
`.gitignore` cobrindo `.env`.

Um arquivo `.env.example` é comitado, com o formato esperado:

```
API_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:XXXXXXXX
```

O valor real (com o endpoint verdadeiro do workspace `academia`) só
existe no `.env` local de cada pessoa do grupo, nunca no repositório.

### 2. Como o Reflex lê a variável

Um módulo central, por exemplo `academia/services/xano_client.py`,
responsável por:
- Ler `API_BASE_URL` do ambiente (usando `os.environ`, com uma
  mensagem de erro clara se a variável não estiver definida).
- Expor uma função simples para fazer requisições HTTP à API do Xano
  (por exemplo, `get(path)`), usada por todo o app daqui para frente.

Nenhuma outra parte do app deve montar a URL da API diretamente; tudo
passa por esse módulo.

### 3. Endpoint de teste

Duas opções, a decidir durante a implementação, dependendo do que já
existe no workspace:

- **Opção A (preferida):** usar um endpoint de leitura já existente em
  `xano/api/` que não exija autenticação, se houver algum adequado.
- **Opção B:** criar um endpoint novo e mínimo em `xano/api/` (por
  exemplo, um "health check" que devolve `{"status": "ok"}`), sem
  autenticação, só para esta change. Se for necessário, o agente deve
  validar o XanoScript pelo Xano Developer MCP antes de propor o push.

Nenhuma das duas opções envolve dados sensíveis ou tabelas de negócio.

### 4. Estrutura de páginas do Reflex

- Uma página inicial (`/`) com um layout simples e reutilizável
  (cabeçalho e área de conteúdo).
- Uma página ou seção de "Diagnóstico" que chama o endpoint de teste
  ao carregar (ou por um botão) e mostra o resultado: "Conectado ao
  Xano" ou uma mensagem de erro, sem vazar detalhes técnicos sensíveis
  na tela.

### 5. Estado (State)

Um `State` do Reflex dedicado ao diagnóstico (por exemplo,
`ConnectionState`), guardando se a chamada está em andamento, se teve
sucesso e a mensagem a mostrar. Segue o padrão de state do Reflex, sem
guardar segredos no estado.

## Fora do design desta change

- Autenticação de verdade (isso é a próxima change).
- Qualquer tabela ou tela de negócio (aluno, plano, matrícula...).
- Estilização definitiva do app (o visual pode ser simples nesta
  etapa).

## Riscos e mitigação

- **Risco:** esquecer o `.env` no `.gitignore` e vazar a URL da API.
  **Mitigação:** conferir o `.gitignore` antes de commitar, e revisar
  o `git status`/`git diff` antes de cada commit desta change.
- **Risco:** criar um endpoint de teste no Xano e esquecer de
  documentá-lo. **Mitigação:** se a Opção B for escolhida, documentar
  o endpoint no `tasks.md` e no `proposal.md` desta change.
