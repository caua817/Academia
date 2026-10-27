# Tasks

## 1. Persistência e API de planos no Xano

- [x] 1.1 Criar a tabela de planos com campos, duração positiva em meses, valor positivo em reais e situação ativa/descontinuada; validar XanoScript e conferir que não há exclusão física prevista.
- [x] 1.2 Implementar listagem, detalhes, cadastro, edição, descontinuação e reativação de planos, exigindo `admin` no backend; validar os arquivos XanoScript.
- [ ] 1.3 Verificar no runtime Xano as operações de planos com dados sintéticos: acesso `admin`, negação sem autenticação e para `member`, validações de nome/duração/valor, edição e descontinuação/reativação sem exclusão.

## 2. Persistência e API de matrículas no Xano

- [x] 2.1 Criar a tabela de matrículas relacionada a aluno e plano, preservando valor e duração contratados e datas do período; adicionar o campo técnico interno usado para serializar criações por aluno, validar XanoScript e conferir as referências.
- [x] 2.2 Implementar criação, listagem e detalhes de matrículas, exigindo `admin`; validar aluno/plano ativos, rejeitar início futuro, calcular término de calendário e impedir sobreposição com bloqueio transacional por aluno.
- [ ] 2.3 Verificar no runtime Xano os casos válidos e inválidos de matrícula, limites de calendário, bloqueio de sobreposição inclusive em requisições simultâneas, preservação do contrato após edição/descontinuação do plano e negação sem autenticação ou com `member`; usar somente dados sintéticos e confirmar persistência.

## 3. Integração HTTP

- [x] 3.1 Estender `academia/services/xano_client.py` para operações de planos e matrículas, preservar erros HTTP/conexão e validar contratos com transporte mockado.

## 4. Interface Reflex

- [x] 4.1 Adicionar navegação, estado e página de planos para listar, cadastrar, editar, descontinuar e reativar; verificar estados de carregamento, vazio, sucesso, validação e erro.
- [x] 4.2 Adicionar estado e página de matrículas para selecionar aluno/plano ativos, informar início permitido e consultar matrículas; verificar feedback de sobreposição, campos contratados e situações ativa/encerrada.

## 5. Verificação integrada e publicação

- [x] 5.1 Adicionar testes focados para chamadas HTTP e validações de formulário; verificar cálculos de término e limites de calendário na tarefa runtime 2.3; executar testes e `reflex compile --dry`.
- [ ] 5.2 Conferir no navegador o fluxo de demonstração: cadastrar plano, matricular aluno, consultar matrícula e confirmar bloqueio de sobreposição; registrar se depende de publicar endpoints no Xano.
- [x] 5.3 Revisar o diff, validar todos os arquivos XanoScript e executar `xano workspace push --dry-run`; não fazer push real sem aprovação explícita do grupo.
