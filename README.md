#  Sistema de Gestão de Academia

Sistema web de alta performance para gestão operacional interna de academias, focado no controlo de matrículas, gestão de alunos, planos financeiro-operacionais e fichas de treino.

---

##  Objetivo do Projeto

O sistema foi desenhado exclusivamente para a equipe interna da academia (**Administradores, Recepcionistas e Instrutores**). Ele centraliza as rotinas administrativas e operacionais num único painel, garantindo segurança nos acessos e agilidade no atendimento.

---

## 🛠️ Tecnologias Utilizadas

- **Frontend:** [Reflex](https://reflex.dev/) (Framework web reativo construído integralmente em Python)
- **Backend & Database:** [Xano](https://www.xano.com/) (No-code Backend-as-a-Service com banco de dados PostgreSQL relacional)
- **Autenticação:** JWT (JSON Web Tokens) com controle de acesso baseado em cargos (*RBAC*)
- **Gestão de Metodologia:** OpenSpec (desenvolvimento guiado por especificações e mudanças incrementais)

---

##  Perfis de Acesso (*RBAC*)

- **Administrador:** Acesso total ao sistema, gestão de utilizadores/funcionários, relatórios e configurações gerais.
- **Recepcionista:** Gestão de cadastros de alunos, matrículas, verificação de pagamentos e atendimento.
- **Instrutor:** Prescrição, consulta e acompanhamento de fichas de treino e evolução dos alunos.

---

##  Estrutura da Solução

```text
academia/
├── academia/               # Código-fonte principal da aplicação Reflex
│   ├── services/           # Integração de APIs e cliente HTTP (xano_client.py)
│   ├── state.py            # Gerenciamento de estado global da aplicação
│   └── academia.py         # Interfaces e componentes visuais do Reflex
├── openspec/               # Histórico de especificações e mudanças do projeto
├── .env                    # Variáveis de ambiente (API Keys e Endpoints)
├── rxconfig.py             # Configurações do servidor Reflex
└── requirements.txt        # Dependências do projeto Python
