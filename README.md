# Sistema de Gestão de Academia

Aplicação web para apoiar as rotinas de uma academia: cadastro de alunos,
planos e matrículas, pagamentos, frequência e operação de aulas. O frontend é
feito em Reflex/Python e consome uma API hospedada no Xano.

## Funcionalidades

- Cadastro e consulta de alunos.
- Gestão de planos e matrículas.
- Consulta de mensalidades, registro de pagamentos e correções financeiras
  rastreáveis.
- Registro e consulta de check-ins, conforme o perfil.
- Gestão de funcionários, modalidades, aulas, reservas e relatórios para
  administradores.
- Controle de acesso por perfil, validado também pelo backend.

## Requisitos

- Python compatível com a versão de Reflex declarada em `requirements.txt`.
- Acesso à API do Xano configurada para o projeto.
- Git, para clonar o repositório.

## Executar localmente

No PowerShell, na pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Opcionalmente, crie um arquivo `.env` na raiz para apontar o frontend para
outra API Xano:

```dotenv
API_BASE_URL=https://SEU-DOMINIO-XANO/api:SEU_GRUPO
```

O cliente usa uma URL padrão do projeto se `API_BASE_URL` não for informada.
Não adicione `.env`, tokens, senhas ou dados reais de alunos ao Git.

Inicie o app:

```powershell
reflex run --env prod --single-port
```

Abra <http://127.0.0.1:3000>. Para parar o servidor, use `Ctrl+C` no terminal
em que ele está rodando.

Em Linux/macOS, a criação e ativação do ambiente virtual podem ser feitas com:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
reflex run --env prod --single-port
```

## Acessar o sistema

1. Entre com a conta de funcionário criada ou fornecida pelo administrador.
   Não há cadastro público de usuários.
2. Se recebeu uma senha temporária, siga a tela para definir sua senha pessoal
   e depois entre novamente.
3. Use o menu lateral para abrir as áreas liberadas ao seu perfil.
4. Use **Atualizar** para buscar novamente os dados da tela e **Sair** para
   encerrar a sessão.

| Perfil | Áreas disponíveis |
|---|---|
| Administrador | Visão geral, alunos, planos, matrículas, financeiro, check-ins, funcionários, modalidades, agenda, reservas e relatórios. |
| Recepcionista | Alunos, matrículas, financeiro e check-ins. |
| Instrutor | Consulta de alunos e de check-ins. |

As permissões são verificadas no backend; ocultar uma tela no frontend não é
uma medida de autorização.

### Fluxos importantes

- **Alunos:** consulte a lista, cadastre ou atualize registros conforme o
  perfil e as opções da tela.
- **Matrículas:** escolha o aluno e o plano, preencha os dados solicitados e
  salve. Consulte os detalhes pela própria área de matrículas.
- **Financeiro:** consulte mensalidades e pagamentos. O registro de pagamento
  é integral; correções de lançamentos exigem motivo e ficam no histórico.
  Registros financeiros não devem ser apagados fisicamente.
- **Check-ins:** a recepção pode registrar entradas; instrutores podem
  consultar a frequência, mas não registrar check-ins.
- **Funcionários:** o administrador pode cadastrar funcionário com senha
  temporária ou enviar convite, além de gerenciar o acesso conforme as ações
  disponíveis na tela.
- **Aulas e reservas:** o administrador gerencia modalidades, agenda e
  reservas pelas áreas correspondentes.

## Convites de funcionários

O envio de convite precisa que o ambiente do Xano tenha a variável
`frontend_base_url` configurada com a URL pública HTTPS do frontend, sem
caminho de ativação. `localhost` e URLs HTTP não são aceitos pelo endpoint.
Depois de abrir o link, o funcionário define a senha e entra no sistema.

Essa configuração é feita no ambiente do Xano, não no `.env` local. Publicar
este repositório no GitHub não altera automaticamente o workspace ou a API do
Xano.

## Problemas comuns

- **Não foi possível verificar seu perfil / erro de conexão:** confirme sua
  conexão com a internet, se a API Xano está disponível e se a URL configurada
  está correta. Se sua sessão expirou, entre novamente.
- **HTTP 429 no financeiro:** aguarde um momento antes de tentar novamente.
  Não repita pagamentos às cegas; confirme o histórico antes de registrar
  outra vez.
- **Erro ao enviar convite com URL HTTPS:** peça ao administrador para
  configurar `frontend_base_url` no ambiente Xano com o domínio público HTTPS
  do app.
- **Alterações no Xano não aparecem após atualizar o GitHub:** GitHub armazena
  o código, mas não publica endpoints no Xano. A sincronização do backend deve
  ser revisada e executada separadamente por uma pessoa autorizada.

## Verificações de desenvolvimento

Ative o ambiente virtual e execute:

```powershell
python -m pytest -q
reflex compile --dry
```

Os endpoints e demais objetos XanoScript ficam em `xano/`. Consulte e valide
XanoScript antes de sincronizar mudanças com o workspace remoto. Não faça push
real ao Xano sem revisão e autorização explícita.

## Estrutura principal

```text
academia/                  Código Python da aplicação Reflex
academia/services/         Clientes HTTP para autenticação e API Xano
tests/                     Testes automatizados
xano/                      Endpoints, funções e tabelas XanoScript
docs/                      Contexto do projeto e modelo de domínio
openspec/                  Especificações e histórico de mudanças
requirements.txt           Dependências Python
rxconfig.py                Configuração Reflex
```
