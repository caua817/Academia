# Proposal: Conectar o frontend (Reflex) ao backend (Xano)

## Por que

O projeto tem hoje dois pedaços que ainda não se falam: um app Reflex em
branco (`academia/academia.py`) e um workspace Xano (`xano/`) já com
autenticação de fábrica (tabelas `user`, endpoints de login, signup,
`me`, redefinição de senha e link mágico, mais logs de evento).

Antes de implementar qualquer funcionalidade de negócio (login, alunos,
planos, matrículas...), o projeto precisa de uma fundação técnica que
prove que o Reflex consegue chamar a API do Xano de forma configurável
e sem segredos no código. Sem isso, cada change futura reinventaria essa
conexão e correria o risco de fazer de um jeito diferente.

## O que muda

- Estrutura inicial de páginas e navegação do app Reflex (uma página
  inicial e um layout simples reutilizável).
- Um serviço central no Reflex responsável por chamar a API do Xano,
  lendo a URL base da API de uma variável de ambiente (não fixa no
  código-fonte).
- Um arquivo `.env.example` (comitado) mostrando quais variáveis são
  necessárias, e um `.env` real (fora do Git, listado no `.gitignore`)
  com o valor de verdade.
- Uma tela de diagnóstico simples que chama um endpoint de leitura do
  Xano (por exemplo, um endpoint que não exija autenticação ainda) e
  mostra na tela se a conexão funcionou ou falhou.

## O que NÃO muda nesta change

- Nenhuma tela de login, cadastro de aluno, plano, matrícula,
  mensalidade, pagamento ou check-in.
- Nenhuma alteração nas tabelas ou endpoints existentes em `xano/`
  (autenticação, `event_log`, funções de exemplo). Esta change só lê
  dados do Xano para provar a conexão; não altera o schema.
- Nenhuma remoção dos endpoints de exemplo do Xano (isso fica para a
  change de autenticação, que vai revisar `signup_POST` à luz da
  decisão "só funcionários têm login").

## Impacto

- **Frontend:** cria a estrutura de pastas do app Reflex
  (`state/`, `services/` ou equivalente, conforme o design), sem
  quebrar a página em branco que já existe.
- **Backend:** nenhuma alteração no Xano nesta change. Pode ser
  necessário criar, no Xano, um endpoint bem simples de "health check"
  se não houver nenhum endpoint público existente adequado para o
  teste — isso será decidido no `design.md`.
- **Segurança:** a URL da API do Xano passa a vir de variável de
  ambiente. Nenhuma credencial do Xano é usada nesta change, porque o
  endpoint de teste não deve exigir autenticação.
- **Risco:** baixo. É a change mais simples possível que ainda entrega
  algo verificável (a tela mostrando "conectado" ou "erro").
