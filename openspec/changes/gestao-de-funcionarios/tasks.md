# Tasks

## 1. Cliente HTTP de funcionários

- [ ] 1.1 Adicionar ao cliente HTTP a consulta de identidade, listagem, detalhes, convite, edição, ativação e desativação de funcionários conforme o contrato de `design.md`; verificar métodos, caminhos, payloads e formatos das respostas com transporte HTTP mockado.
- [ ] 1.2 Cobrir respostas inválidas, falhas de conexão, HTTP 401 e HTTP 403 sem chamadas ao Xano real; confirmar que nenhum payload ou resposta de funcionário contém campos de senha ou token.

## 2. Estado Reflex

- [ ] 2.1 Criar estado Reflex que consulte `/auth/me` antes de carregar funcionários, habilite a área somente para `admin`, pesquise localmente e limpe os dados e a sessão em HTTP 401; verificar cenários com testes locais.
- [ ] 2.2 Implementar convite por e-mail, edição de nome/e-mail/perfil e alteração confirmada de situação; verificar validação de campos obrigatórios e estados de carregamento, sucesso e erro com chamadas HTTP mockadas.

## 3. Interface e navegação

- [ ] 3.1 Integrar a rota e a navegação de funcionários ao shell existente, exibindo lista, busca, perfil, situação, formulário de convite/edição e confirmação de ativação/desativação; verificar montagem com `reflex compile --dry`.
- [ ] 3.2 Verificar os fluxos da tela com API mockada, incluindo usuário sem perfil administrativo, lista vazia, busca sem resultados, convite e edição rejeitados, falha de rede e sessão expirada; confirmar que credenciais não aparecem na interface.

## 4. Validação local e contrato

- [ ] 4.1 Executar a suíte focada, `reflex compile --dry` e `openspec validate gestao-de-funcionarios --strict`; corrigir falhas introduzidas pela change.
- [ ] 4.2 Revisar o diff para verificar que somente o frontend e seus testes foram alterados, sem arquivos ou chamadas de validação Xano; documentar que a integração real depende dos endpoints e perfis previstos em `design.md`.
