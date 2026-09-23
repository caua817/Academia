# Tasks: Conectar o frontend (Reflex) ao backend (Xano)

## 1. Configuração de ambiente

- [ ] 1.1 Criar `.env.example` na raiz do projeto, com `API_BASE_URL`
      documentada (sem valor real).
- [ ] 1.2 Confirmar que `.env` está no `.gitignore` (já deve estar,
      conferir mesmo assim).
- [ ] 1.3 Cada pessoa do grupo cria seu próprio `.env` local com a URL
      real da API do workspace `academia`, sem commitar.

## 2. Cliente da API do Xano

- [ ] 2.1 Criar o módulo `academia/services/xano_client.py` (ou
      caminho equivalente definido durante a implementação), lendo
      `API_BASE_URL` do ambiente.
- [ ] 2.2 Implementar uma função de leitura simples (por exemplo,
      `get(path)`) usando uma biblioteca HTTP já disponível no
      ambiente Python (ex.: `httpx` ou `requests` — escolher uma só e
      registrar no `requirements.txt` com versão fixada).
- [ ] 2.3 Tratar erro de conexão (Xano fora do ar, URL errada) sem
      quebrar o app.

## 3. Endpoint de teste no Xano

- [ ] 3.1 Verificar se já existe, em `xano/api/`, algum endpoint de
      leitura sem autenticação adequado para o teste.
- [ ] 3.2 Se não existir, criar um endpoint mínimo de "health check"
      em XanoScript, validando a sintaxe pelo Xano Developer MCP antes
      de propor o `xano workspace push --dry-run`.
- [ ] 3.3 Documentar no `proposal.md` desta change qual opção (A ou B)
      foi usada e, se for a B, o caminho do novo endpoint.

## 4. Páginas e navegação no Reflex

- [ ] 4.1 Criar um layout simples reutilizável (cabeçalho + área de
      conteúdo).
- [ ] 4.2 Criar a página inicial (`/`) usando esse layout.
- [ ] 4.3 Criar a seção/página de diagnóstico, com um `ConnectionState`
      que chama o cliente da API (item 2) e mostra o resultado.

## 5. Verificação

- [ ] 5.1 Rodar `reflex run` e confirmar visualmente que a página de
      diagnóstico mostra "Conectado ao Xano" quando o backend está
      acessível.
- [ ] 5.2 Testar o caso de erro (por exemplo, com uma URL errada no
      `.env` local) e confirmar que o app mostra uma mensagem de erro
      sem quebrar.
- [ ] 5.3 Conferir `git status` e `git diff` antes de commitar: nenhum
      segredo, nenhum arquivo fora do escopo desta change.
- [ ] 5.4 Se um endpoint novo foi criado no Xano (item 3.2), confirmar
      que o `xano workspace pull` reflete esse endpoint em `xano/` antes
      do commit final.

## 6. Fechamento

- [ ] 6.1 Revisar esta change com o grupo antes de arquivar.
- [ ] 6.2 Rodar o passo de archive do OpenSpec para mover esta change
      para `openspec/specs/`, atualizando o comportamento consolidado
      do projeto.
