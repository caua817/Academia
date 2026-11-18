# Design

## Context

Veja [proposal.md](./proposal.md) para a motivação e [specs/employee-management/spec.md](./specs/employee-management/spec.md) e [specs/authentication/spec.md](./specs/authentication/spec.md) para os contratos observáveis. O formulário atual chama `funcionarios/convites`; esse endpoint exige `$env.frontend_base_url` e envia e-mail. O endpoint `auth/login` atualmente cria um token normal para qualquer conta com credenciais válidas, e a tela Reflex espera esse token para iniciar a sessão.

## Objetivos / Não objetivos

**Objetivos:**

- Oferecer um caminho de criação de funcionário que funcione quando a interface está em localhost.
- Aplicar validade de 24 horas e troca obrigatória da senha no backend, não apenas na navegação Reflex.
- Preservar login de funcionários com senha permanente e proteger dados de senha em respostas e logs.
- Dar ao administrador uma forma autorizada de reemitir uma credencial temporária expirada.

**Não objetivos:**

- Remover a ativação dos convites por e-mail já emitidos.
- Permitir cadastro público, entregar credenciais por e-mail ou configurar uma origem HTTPS fictícia.
- Fazer push ao workspace Xano sem revisão e aprovação explícitas.

## Decisões

### Separar provisionamento administrativo do convite por e-mail

Criar um caminho de API autenticado e restrito a `admin` para criar o funcionário com uma senha temporária; o frontend oferecerá esse caminho de cadastro presencial sem depender de hosting. Manter o endpoint de convite por e-mail como alternativa somente quando `frontend_base_url` HTTPS estiver válida e manter a aceitação de convites existentes. Não usar `frontend_base_url` no cadastro presencial.

**Alternativas consideradas:** continuar bloqueando cadastro até publicar o frontend; descartado porque o grupo aprovou a entrega presencial e a aplicação permanece local. Usar localhost ou omitir a validação do convite; descartado porque os links não seriam acessíveis ao funcionário.

### Impor a troca antes de criar uma sessão

Registrar no usuário que a senha é temporária e seu prazo de expiração. Quando credenciais temporárias válidas forem informadas no login, responder com o estado de troca obrigatória, sem emitir token de sessão normal. Uma operação própria valida e troca a senha temporária por uma senha permanente; somente uma nova chamada de login, após a troca, emite sessão normal. Uma senha expirada não pode concluir login nem troca.

O endpoint de troca sem sessão autenticada deverá validar e consumir a credencial temporária no backend, retornar apenas confirmação e não emitir token. Antes de escolher campos, filtros e operações XanoScript, consultar a documentação oficial Xano; não inferir sintaxe a partir dos arquivos existentes.

**Alternativas consideradas:** emitir um token normal e redirecionar a tela para trocar senha; descartado porque o funcionário poderia chamar diretamente outras APIs antes da troca. Reutilizar o fluxo autenticado de redefinição; descartado porque ele exige uma sessão que o funcionário ainda não deve possuir.

### Expirar e reemitir credenciais com proteção de dados

Aplicar uma validade fixa de 24 horas desde a criação ou reemissão. A reemissão só estará disponível ao administrador para uma conta cuja credencial temporária expirou; ela substitui a senha anterior e reinicia a validade. Persistir somente o hash tratado pelo campo de senha do Xano e os metadados de estado/expiração. Nunca retornar ou registrar a senha temporária ou permanente; o frontend deve usar campos mascarados transitórios e limpá-los após a operação.

**Alternativas consideradas:** manter a senha temporária válida indefinidamente; descartado por deixar uma credencial inicial reutilizável sem limite. Enviar nova credencial por e-mail; descartado porque exigiria novamente uma origem pública e contrariaria a entrega presencial aprovada.

### Limitar tentativas de credenciais temporárias

Usar `redis.ratelimit` com chave por identificador da conta, compartilhada entre `auth/login` e a troca obrigatória, permitindo cinco solicitações a cada 15 minutos. Contar todas as solicitações feitas para uma conta com senha temporária, independente do resultado; aplicar o limite somente a essas contas, preservando o login de contas com senha permanente. A integração Redis deve estar disponível no workspace Xano antes do push.

**Alternativas consideradas:** limitar somente a troca de senha; descartado porque permitiria contornar o limite tentando as mesmas credenciais no endpoint de login. Limitar todas as contas; descartado por ampliar desnecessariamente a mudança para o login de funcionários existentes.

### Implantar mudanças Xano com gate explícito

Antes de editar os arquivos Xano, puxar o estado atual do workspace. Validar o XanoScript com a documentação e ferramenta oficial disponível; executar o dry-run do push e revisar o diff. A implantação remota somente ocorre após aprovação explícita do grupo. Até essa aprovação, o cadastro não deve ser apresentado como funcional no workspace remoto.

## Riscos / Trade-offs

- **[Risco]** Uma conta com senha temporária expirada não consegue acessar o sistema. **→ Mitigação:** permitir ao administrador reemitir uma nova senha presencialmente com validade renovada de 24 horas.
- **[Risco]** A interface pode reter a senha temporária em estado de sessão ou logs. **→ Mitigação:** campo mascarado, valor transitório, limpeza após a tentativa e testes que confirmem que resposta, mensagens e logs não incluem a senha.
- **[Risco]** Um fluxo de troca sem sessão amplia a superfície de autenticação. **→ Mitigação:** exigir o e-mail e a senha temporária atual, validar validade e estado no backend, não emitir token na resposta e limitar a cinco solicitações por conta a cada 15 minutos, compartilhadas entre login temporário e troca; confirmar Redis habilitado no workspace antes do push.
- **[Risco]** O workspace Xano remoto pode divergir dos arquivos locais. **→ Mitigação:** realizar pull antes de editar, revisar dry-run e obter aprovação antes do push real.

## Plano de migração

1. Puxar e comparar o estado atual do workspace Xano.
2. Implementar localmente os metadados da credencial temporária, endpoints administrativos e troca obrigatória, após consultar a documentação oficial Xano.
3. Atualizar o formulário de funcionário e o login Reflex para o desafio de troca, sem salvar a senha temporária em sessão persistente.
4. Executar testes direcionados, validação Xano e dry-run do push; solicitar aprovação do grupo para implantação remota.
5. Após aprovação, publicar os endpoints e testar criação, bloqueio após expiração, reemissão, troca e login normal.
6. Para rollback, bloquear novos cadastros pelo fluxo temporário e restaurar os endpoints anteriores sem emitir sessão normal para contas ainda marcadas com troca obrigatória. Não remover registros de funcionários.
