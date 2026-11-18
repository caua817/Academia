# ByteFit — Sistema de Gestão de Academia

Aplicação web acadêmica para apoiar a gestão de uma academia. O frontend é
desenvolvido em Python com Reflex e consome uma API hospedada no Xano.

## Funcionalidades

- Cadastro e consulta de alunos.
- Gestão de planos, matrículas, mensalidades e pagamentos.
- Registro e consulta de check-ins.
- Gestão de funcionários, modalidades e agenda de aulas.
- Relatórios operacionais para administradores.
- Controle de acesso por perfil, com autorização aplicada também no backend.

**Reservas de aulas não estão disponíveis na interface atual.** Os endpoints e
registros históricos existentes no Xano são preservados.

## Requisitos

- Windows 10 ou 11.
- Python 3.10 ou superior.
- Acesso à internet e à API Xano do projeto.
- Git para clonar o repositório (ou baixe o ZIP da branch no GitHub).

## Instalação e execução

Para obter a versão atualizada do projeto, clone a branch
`change/fase-tres-acompanhamento-aluno`:

```powershell
git clone --branch change/fase-tres-acompanhamento-aluno --single-branch https://github.com/caua817/Academia.git
cd Academia
```

Crie o ambiente Python e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Inicie o aplicativo:

```powershell
reflex run --env prod --single-port
```

Abra no navegador o endereço informado pelo Reflex no terminal (normalmente
`http://127.0.0.1:3000`). Se essa porta estiver ocupada, use a porta indicada
na mensagem de inicialização. Para encerrar, pressione `Ctrl+C` no terminal.

Se a política do PowerShell impedir a ativação do ambiente, execute os comandos
com o Python do ambiente diretamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\reflex.exe run --env prod --single-port
```

## Configuração da API

O cliente usa a URL padrão da API do projeto. Para apontar para outro ambiente,
crie um arquivo `.env` na raiz:

```dotenv
API_BASE_URL=https://SEU-DOMINIO-XANO/api:SEU_GRUPO
```

Não versione `.env`, tokens, senhas ou dados reais de alunos. O `.env` já está
incluído no `.gitignore`.

## Acesso ao sistema

Não há cadastro público de contas. Use uma conta de funcionário fornecida pelo
administrador. Caso receba uma senha temporária, siga o fluxo de troca de senha
na tela de login.

| Perfil | Áreas disponíveis |
|---|---|
| Administrador | Visão geral, alunos, planos, matrículas, financeiro, check-ins, funcionários, modalidades, agenda e relatórios. |
| Recepcionista | Alunos, matrículas, financeiro e check-ins. |
| Instrutor | Consulta de alunos e check-ins. |

As permissões são verificadas pelo backend; ocultar uma página no frontend não
substitui autorização.

### Convites de funcionários

Para enviar convites, o ambiente Xano precisa ter `frontend_base_url`
configurada com a URL pública HTTPS do frontend. Essa configuração é feita no
Xano e não no `.env` local. Publicar o código no GitHub não publica nem altera
a API Xano.

## Problemas comuns

- **Falha de conexão ou de verificação do perfil:** confirme a conexão com a
  internet e a disponibilidade da API Xano; depois tente entrar novamente.
- **HTTP 429:** a API está limitando solicitações. Aguarde antes de tentar
  novamente; no financeiro, confira o histórico antes de repetir um pagamento.
- **Convite de funcionário rejeitado:** confirme com o administrador que
  `frontend_base_url` está configurada no Xano com HTTPS público.

## Testes e compilação

Com o ambiente virtual ativado:

```powershell
python -m pytest -q
reflex compile --dry
```

## Estrutura do repositório

```text
academia/                  Aplicação Reflex
academia/services/         Clientes HTTP para autenticação e API Xano
tests/                     Testes automatizados
xano/                      Endpoints, funções e tabelas XanoScript
docs/                      Visão geral e modelo de domínio
openspec/                  Especificações e mudanças do projeto
requirements.txt           Dependências Python
rxconfig.py                Configuração Reflex
```
