<!-- reflex managed begin (do not edit inside this block; add custom content outside the markers) -->
# Agents

This project uses the **Reflex agent skills** � up-to-date knowledge for building full-stack Python web apps with [Reflex](https://reflex.dev). Install them first, then use them as described below.

## Installing the Skills

Before working on this project, make sure the Reflex skills are available to you.

### Claude Code

If the skills are not already available, install them yourself by running these shell commands:

```bash
claude plugin marketplace add reflex-dev/agent-skills
claude plugin install reflex@reflex-agent-skills
```

Newly installed plugins load on the next session. After installing, tell the user to restart the session so the skills auto-load; until then, read the skill files directly from `~/.claude/plugins/` when you need them.

### Other agents (Cursor, OpenCode, Codex, Pi)

```
npx skills add reflex-dev/agent-skills
```

Or clone https://github.com/reflex-dev/agent-skills and copy the `skills/` folders into your agent's skill directory (see the repo README for paths).

### Verifying

Before writing or editing any Reflex code, confirm these three skills are available: `reflex-docs`, `setup-python-env`, and `reflex-process-management`. If they are not, STOP and run the install step above � do not proceed without them.

## Using the Skills

### Reflex documentation

For anything about Reflex APIs � components, state management, events, styling, database, routing, authentication � use the **reflex-docs** skill rather than relying on memory. It carries current, version-accurate docs.

### Initializing a new Reflex project

When starting a new Reflex project or setting up a development environment, you **must** follow the **setup-python-env** skill before doing anything else.

Do not skip any steps. Do not assume a virtual environment or Reflex is already available � always verify first by following the skill's instructions in order.

After the environment is ready and Reflex is installed, run:

```bash
reflex init
```

Then proceed with the user's request.

### Managing a Reflex process

When you need to compile, run, reload, or debug a Reflex application, follow the **reflex-process-management** skill for the correct sequence and error investigation steps.
<!-- reflex managed end -->

> **Prioridade das instruções:** o bloco acima é gerenciado pelo Reflex e não deve ser editado. Em caso de conflito, valem as regras deste projeto, abaixo do bloco. Em especial:
> - O projeto Reflex **já foi inicializado**: não execute `reflex init` novamente.
> - Não instale plugins, skills ou pacotes de agentes sem aprovação do grupo. As skills do Reflex já estão em `.agents/skills/`.
> - O ambiente é `venv` + `pip`, não `uv`.

# AGENTS.md — Sistema de Gerenciamento de Academia

Instruções para agentes de IA que trabalham neste repositório. Este arquivo define **como atuar**. Para saber **o que é o projeto**, consulte os documentos de contexto.

## Documentos de contexto

Antes de qualquer alteração significativa, leia:

- `docs/project-overview.md` — o que é o projeto, escopo e restrições.
- `docs/domain-model.md` — conceitos do domínio e relacionamentos.
- `openspec/config.yaml` — contexto e regras dos workflows do OpenSpec.
- `openspec/specs/` — comportamento já consolidado do sistema.

Em caso de conflito entre um documento e uma suposição sua, prevalece o documento. Se o documento parecer errado ou incompleto, **pergunte** em vez de improvisar.

## Desenvolvimento com OpenSpec

- Mudanças funcionais ou técnicas relevantes devem passar pelo OpenSpec: Explore → Propose → Review → Apply → Archive.
- Não implemente código que não esteja coberto pelas tarefas (`tasks.md`) da change atual.
- Não crie arquivos em `openspec/specs/` manualmente; eles são atualizados pelo archive das changes.
- Não altere nem remova os arquivos de workflow instalados pelo `openspec init`.
- Implemente de forma incremental. O modelo de domínio é global, mas a implementação segue a ordem das changes; não crie entidades ou tabelas de fases futuras antes da hora.

## Arquitetura

- Respeite as tecnologias definidas no projeto. Não introduza tecnologias alternativas sem justificativa explícita.
- Regras de negócio e persistência ficam no backend (Xano). O frontend consome a API do backend e não implementa regras de negócio nem segurança.
- Backend: Xano, com código em XanoScript (`.xs`) na pasta `xano/`.
- Frontend: Reflex (Python), de forma exclusiva.

## Frontend

O frontend do projeto deve ser implementado exclusivamente com Reflex.

- Utilize os mecanismos próprios do Reflex para componentes, estado, eventos, páginas e interação.
- Não introduza outra tecnologia de frontend para substituir ou complementar o Reflex, salvo com alteração arquitetural explicitamente aprovada.
- Não execute `reflex init` novamente em um projeto já inicializado. Use `reflex run`.
- Dependências: o ambiente é `venv` + `pip`. Não use `uv` nem misture gerenciadores. Ao instalar uma nova biblioteca, verifique se é realmente necessária, teste e atualize o `requirements.txt` junto com a mudança.
- As Agent Skills do Reflex (`.agents/skills/`) são complementares. Não substituem este arquivo nem os documentos do OpenSpec. Se o Reflex gerar instruções próprias para agentes, examine-as e incorpore apenas o que for compatível com estas regras.

## Xano

- Não presuma a sintaxe do XanoScript. Consulte a documentação pelo Xano Developer MCP e valide o código antes de concluir.
- Faça `xano workspace pull` antes de começar a trabalhar, caso o workspace possa ter sido alterado diretamente no Xano.
- Antes de enviar alterações ao Xano, revise o `git diff` e execute `xano workspace push` com `--dry-run`. Só faça o push real depois da aprovação do grupo.
- Não utilize o Xano MCP Server (acesso direto ao workspace) nem execute operações destrutivas sem aprovação explícita do grupo.
- Nunca coloque tokens ou credenciais do Xano em arquivos versionados.

## Código

- Reutilize código existente quando apropriado e evite duplicação.
- Não modifique funcionalidades não relacionadas à change atual sem justificativa.
- Prefira mudanças pequenas e fáceis de revisar.
- Idioma: documentação e artefatos OpenSpec em português brasileiro; identificadores de código em `[A DEFINIR: inglês ou português]`, de forma consistente.

## Segurança e privacidade

- Regras de autorização devem ser aplicadas no backend; o frontend não é mecanismo de segurança.
- Nunca armazene senhas em texto puro nem registre credenciais, tokens ou dados pessoais em logs.
- Dados pessoais (CPF, contato, endereço) e dados de saúde (avaliações físicas) são sensíveis: exponha apenas o necessário e apenas aos perfis autorizados.
- Nunca inclua segredos ou credenciais no repositório.

## Integridade dos dados

- Registros financeiros (mensalidades e pagamentos) não devem ser apagados fisicamente; correções devem ser rastreáveis.
- Valide dados de entrada no backend.

## Testes

- Toda mudança funcional deve ter uma estratégia de verificação.
- Execute os testes relevantes antes de marcar tarefas como concluídas.
- Não desative nem remova testes para fazer uma mudança passar.

## Git e estabilidade

- A branch `main` deve estar sempre funcional.
- Trabalhe em uma branch por change do OpenSpec e faça commits pequenos, com mensagens claras.
- Não versione `.venv/`, `.env` nem credenciais. Versione `requirements.txt`, `rxconfig.py`, o código-fonte, `AGENTS.md`, `docs/`, `openspec/` e `xano/`.
- Não integre uma change na `main` sem que ela tenha sido verificada.

## Quando parar e perguntar

Interrompa e consulte o grupo quando algo:

- contradiga o modelo de domínio;
- altere significativamente a arquitetura;
- exija uma decisão de negócio não prevista (por exemplo, regras de inadimplência ou cancelamento);
- aumente muito o escopo da change.

O princípio é: **a IA propõe, o grupo analisa e aprova, e então a IA implementa.**
