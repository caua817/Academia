# Tarefas

## 1. Backend Xano

- [x] 1.1 Executar `xano workspace pull` em diretório isolado e revisar as diferenças do workspace remoto antes de editar; consultar a documentação oficial Xano para os recursos de senha, validade e validação de endpoints usados nesta change.
- [x] 1.2 Adicionar o estado de senha temporária e sua expiração de 24 horas ao usuário, além de um endpoint de criação/reemissão protegido para `admin`; validar os arquivos com o Xano Developer MCP e cobrir autorização, e-mail duplicado e reemissão após expiração.
- [x] 1.3 Alterar o login para não emitir sessão normal para senha temporária e criar a operação de troca sem sessão autenticada; validar senha atual e prazo no backend, limitar a cinco solicitações por conta/15 minutos usando Redis compartilhado entre os endpoints, não retornar credenciais e validar o XanoScript com a ferramenta oficial.

## 2. Interface Reflex

- [x] 2.1 Atualizar o formulário de funcionários para oferecer cadastro presencial por senha temporária e permitir reemiti-la quando expirada, mantendo convite por e-mail quando configurado; verificar mensagens de sucesso/erro, ausência de dependência HTTPS no cadastro presencial e limpeza dos campos.
- [x] 2.2 Atualizar o login para encaminhar credenciais temporárias válidas à troca obrigatória, limpar dados sensíveis e exigir novo login após a troca; verificar que contas existentes mantêm o fluxo normal.

## 3. Verificação e implantação

- [ ] 3.1 Adicionar e executar testes cobrindo cadastro autorizado, tentativas sem perfil admin, e-mail duplicado, validade/reemissão, login sem sessão para senha temporária, troca inválida/válida, bloqueio após cinco solicitações compartilhadas em 15 minutos e autenticação normal após novo login.
- [x] 3.2 Revisar `git diff`, executar validação Xano e `xano workspace push --dry-run`; apresentar o resultado ao grupo e obter aprovação explícita antes de qualquer push real.
- [ ] 3.3 Após a aprovação do push, implantar no workspace Xano sem referências auxiliares pendentes e validar o cadastro completo em ambiente integrado, sem envio de e-mail e sem publicar o frontend.
