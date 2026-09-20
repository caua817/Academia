# Project Overview — Sistema de Gerenciamento de Academia

> **Rascunho inicial.** Itens marcados com `[A DEFINIR]` ou `[VALIDAR]` precisam de decisão do grupo. Remova esta nota quando o documento for revisado.

## 1. Visão geral

Sistema para gerenciar o funcionamento de uma academia: cadastro de alunos, planos e matrículas, cobrança de mensalidades, controle de frequência (check-in) e, em fases posteriores, aulas, treinos e avaliações físicas.

## 2. Problema

Academias pequenas e médias costumam controlar alunos, pagamentos e acessos em planilhas, cadernos ou ferramentas desconectadas. Isso gera:

- dificuldade para saber quem está com a mensalidade em dia ou em atraso;
- retrabalho na recepção (cadastros, renovações, consultas);
- falta de visibilidade sobre frequência e retenção dos alunos;
- risco de perda ou exposição de dados pessoais.

## 3. Objetivos

- Centralizar o cadastro de alunos, planos e matrículas.
- Controlar mensalidades e pagamentos, com visão clara de inadimplência.
- Registrar a frequência dos alunos.
- Dar a cada perfil de usuário apenas o acesso de que precisa.
- Servir de base para evoluir para aulas, treinos e avaliações físicas.

## 4. Público-alvo / usuários

| Perfil | O que faz no sistema |
|---|---|
| Administrador / Gerente | Configura planos e modalidades, gerencia funcionários, acompanha indicadores financeiros. |
| Recepcionista | Cadastra alunos, realiza matrículas, registra pagamentos e check-ins. |
| Instrutor | Consulta alunos, acompanha frequência; nas fases futuras, gerencia treinos e avaliações. |
| Aluno | Consulta seus dados, plano, pagamentos e frequência `[VALIDAR: haverá acesso do aluno na fase inicial?]`. |

## 5. Escopo

### Dentro do escopo

O objetivo do grupo é entregar a gestão completa da academia, com todas as fases abaixo. O desenvolvimento é incremental (uma change do OpenSpec por vez), para que o sistema permaneça estável e funcional a cada entrega. As fases indicam a **ordem de implementação**, não cortes de escopo.

**Fase 1 — Núcleo**
- Autenticação e perfis de acesso.
- Cadastro de alunos.
- Cadastro de planos.
- Matrículas.
- Mensalidades e registro de pagamentos.
- Check-in / controle de frequência.

**Fase 2 — Operação**
- Modalidades, aulas e reservas.
- Cadastro de instrutores e funcionários.
- Relatórios gerenciais.

**Fase 3 — Acompanhamento do aluno**
- Fichas de treino e exercícios.
- Avaliações físicas.

### Fora do escopo (por enquanto) `[VALIDAR]`

- Integração com catracas ou equipamentos físicos.
- Aplicativo móvel nativo.
- Emissão de nota fiscal.
- Processamento de pagamento com cartão dentro do sistema (apenas registro/conciliação).

## 6. Principais funcionalidades

- Gestão de alunos, planos e matrículas.
- Geração e acompanhamento de mensalidades, com identificação de atrasos.
- Registro de pagamentos e situação financeira do aluno.
- Registro de frequência.
- Controle de acesso por perfil.
- (Fases posteriores) agenda de aulas, reservas, treinos e avaliações físicas.

## 7. Requisitos e restrições importantes

- O sistema lida com **dados pessoais** e, na Fase 3, **dados de saúde** (avaliações físicas), sujeitos à LGPD.
- O projeto é acadêmico e será desenvolvido em grupo, de forma incremental. `[VALIDAR: prazo e equipe]`
- Regras de negócio sobre inadimplência, trancamento e cancelamento ainda não foram definidas. `[A DEFINIR]`

## 8. Arquitetura tecnológica

- **Backend:** Xano (API, lógica de negócio e banco de dados), com código em XanoScript (`.xs`).
- **Sincronização:** Xano CLI (pull/push entre a pasta `xano/` local e o workspace Xano).
- **Frontend:** Reflex (Python). Será utilizado como tecnologia exclusiva para implementação do frontend da aplicação. Dependências gerenciadas com `venv` + `pip` (`requirements.txt`).
- **Controle de versão:** Git, com repositório remoto no GitHub.
- **Especificação e desenvolvimento assistido por IA:** OpenSpec, com o Xano Developer MCP para consulta e validação de XanoScript. Agente de IA: `[A DEFINIR]`.
- Autenticação e ambiente de execução do frontend: `[A DEFINIR]`.

> Ao decidir os itens pendentes, registrar aqui e replicar no `context` do `openspec/config.yaml`.

## 9. Princípios de desenvolvimento

- Desenvolvimento incremental, uma change do OpenSpec por vez.
- Backend é responsável por regras de negócio e persistência.
- Reutilizar código existente e evitar duplicação.
- Toda mudança funcional deve ter uma forma de verificação.
- Estabilidade: a branch `main` deve estar sempre funcional; cada change é validada antes de ser integrada.

## 10. Segurança e integridade

- Autorização aplicada sempre no backend; o frontend não é mecanismo de segurança.
- Senhas nunca armazenadas em texto puro.
- Dados pessoais e de saúde acessíveis apenas aos perfis que precisam deles.
- Registros financeiros não devem ser apagados fisicamente; correções devem ser rastreáveis. `[VALIDAR]`

## 11. Estratégia de desenvolvimento

1. Concluir a documentação de contexto e o `openspec init`.
2. Executar um Explore do projeto inteiro.
3. Definir a primeira change (provavelmente autenticação/perfis ou cadastro de alunos e planos).
4. Seguir o ciclo Propose → Review → Apply → Archive para cada change.

## 12. Fonte de verdade e documentação

| Assunto | Onde está |
|---|---|
| O que é o projeto | `docs/project-overview.md` |
| Conceitos do domínio | `docs/domain-model.md` |
| Como o agente trabalha | `AGENTS.md` |
| Contexto e regras do OpenSpec | `openspec/config.yaml` |
| Comportamento consolidado | `openspec/specs/` |
| Mudanças em andamento | `openspec/changes/` |
