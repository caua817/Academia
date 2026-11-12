# Tasks

## 1. Diagnóstico e modelo de dados Xano

- [ ] 1.1 Fazer pull do workspace Xano em diretório isolado e comparar os arquivos locais com o publicado; verificar especificamente os endpoints de funcionários por leitura autenticada e registrar divergências sem publicar nem alterar dados.
- [ ] 1.2 Definir e implementar as tabelas e índices de modalidades, sessões e reservas, incluindo estados, chaves de unicidade e controle de capacidade; validar os arquivos XanoScript alterados.

## 2. APIs de modalidades e sessões

- [ ] 2.1 Implementar APIs `admin` para listar, cadastrar, editar e desativar modalidades preservando histórico; validar erros de entrada, autorização e respostas mínimas com testes Xano.
- [ ] 2.2 Implementar APIs `admin` para listar, criar, editar e cancelar sessões, validando modalidade/instrutor ativos, horário, capacidade e conflitos de agenda; validar XanoScript e cenários inválidos sem alterar registros existentes.
- [ ] 2.3 Garantir que o cancelamento de sessão preserve o histórico e cancele reservas confirmadas associadas; verificar estados finais e capacidade com testes direcionados.

## 3. APIs de reservas

- [ ] 3.1 Implementar criação e consulta de reservas para aluno ativo com matrícula vigente, rejeitando sessão indisponível, lotada ou reserva duplicada; validar autorização e respostas com testes Xano.
- [ ] 3.2 Implementar serialização/transação de capacidade para reservas concorrentes, cancelamento antes da sessão e registro de presença/falta após o término; verificar que nunca há excesso de vagas nem remoção do histórico.

## 4. Relatórios

- [ ] 4.1 Implementar endpoint `admin` agregado para matrículas ativas na data final, pagamentos no intervalo, mensalidades vencidas e não pagas até a data final, check-ins e ocupação de sessões; testar intervalo inválido, ausência de atividade, autorização e ausência de dados pessoais.

## 5. Clientes e interface Reflex

- [x] 5.1 Adicionar chamadas tipadas no `XanoClient` para modalidades, sessões, reservas e relatórios; cobrir caminhos, métodos, payloads, estados HTTP e respostas inválidas com transportes mockados.
- [x] 5.2 Criar telas administrativas de modalidades, agenda de sessões e reservas com carregamento, vazio, sucesso, erros, ocupação e ações compatíveis com o estado da sessão; verificar os fluxos sem dados pessoais desnecessários.
- [x] 5.3 Criar tela de relatórios com intervalo de datas e métricas agregadas; verificar estados de carregamento/vazio/erro e conferir que não aparecem identificadores ou dados pessoais.
- [x] 5.4 Proteger menu e acesso direto a todas as páginas de gestão existentes e novas por perfil `admin`, redirecionando sessão ausente ao login e negando perfil diferente; verificar URLs diretas e manter as APIs como autoridade.

## 6. Verificação integrada

- [ ] 6.1 Confirmar se a API publicada de funcionários atende aos contratos existentes por leitura autenticada; se ausente ou incompatível, documentar o bloqueio e não implementar nem publicar endpoints de funcionários nesta change.
- [ ] 6.2 Executar testes direcionados e a suíte existente, compilar com `reflex compile --dry`, validar OpenSpec e XanoScript, e fazer smoke test das páginas e APIs sem gravações repetidas nem alteração de dados reais.
- [ ] 6.3 Revisar o diff e executar `xano workspace push --dry-run` limitado aos arquivos da change; solicitar aprovação explícita antes de publicação real e confirmar o runtime após eventual publicação aprovada.
