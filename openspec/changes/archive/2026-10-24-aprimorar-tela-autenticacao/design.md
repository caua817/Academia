# Design: Aprimorar a tela de autenticação

## Contexto

Consulte [proposal.md](./proposal.md) para a motivação e [spec.md](./specs/authentication/spec.md) para os requisitos observáveis. A página e o diálogo são implementados em Reflex em `academia/login.py`; a validação de campos do cliente fica em `academia/services/auth_client.py`. O endpoint público `xano/api/authentication/auth/signup_POST.xs` atualmente recebe a senha e cria a conta sem verificar sua composição. O login usa outro endpoint e não deve herdar a nova política.

## Objetivos / Não objetivos

**Objetivos:**

- Manter os requisitos da senha explícitos no cadastro e rejeitar entradas inválidas tanto na interface quanto no Xano.
- Tornar a alternância de visibilidade independente para cada campo, preservando seu valor.
- Reorganizar a página e o modal com hierarquia, espaçamento e comportamento responsivo consistentes.
- Preservar o login de contas existentes e o cadastro público com papel `member`.

**Não objetivos:**

- Alterar o formato de autenticação, o token, os papéis ou o fluxo de sessão.
- Fazer a validação da interface substituir a validação autoritativa do backend.
- Publicar alterações no workspace Xano sem aprovação do grupo.

## Decisões

### Validar a política no backend e espelhá-la na interface

O endpoint de cadastro no Xano será a autoridade para a política de senha. A interface exibirá critérios individuais e impedirá o envio enquanto algum deles estiver pendente; o endpoint também recusará a solicitação antes de criar a conta. As duas camadas usarão a mesma regra acordada: mínimo de 8 caracteres, uma letra maiúscula, uma minúscula e um número.

**Alternativa descartada:** aplicar a regra somente no cliente. Isso permitiria criar contas fora da política chamando a API diretamente. A alteração local em Xano deverá usar sintaxe documentada e validada; nenhum push real está autorizado por esta change.

### Não aplicar os critérios de criação ao login

A nova validação ocorre apenas no cadastro. Senhas de contas existentes que não satisfaçam os critérios continuam podendo autenticar se o endpoint de login confirmar as credenciais.

**Alternativa descartada:** bloquear senhas antigas no login, pois isso poderia impedir o acesso de usuários existentes sem fluxo de atualização ou recuperação de senha no escopo.

### Controlar visibilidade sem alterar credenciais

Cada formulário terá um controle explícito para alternar o tipo do campo entre oculto e visível. O valor permanece no estado existente, e os controles de login e cadastro são independentes. O rótulo acessível identifica a ação atual de mostrar ou ocultar.

**Alternativa descartada:** usar um único estado compartilhado, que poderia revelar simultaneamente uma senha em outro formulário.

### Reduzir densidade visual e manter a interface Reflex

Reorganizar os elementos da página e do diálogo em grupos visuais com espaçamento consistente entre rótulos, campos, mensagens e ações. Ajustar largura e padding para telas estreitas, mantendo mensagens junto ao formulário e sem introduzir outra biblioteca ou tecnologia de frontend.

**Alternativa descartada:** adicionar uma biblioteca de componentes ou uma página separada de cadastro, pois o Reflex existente permite evoluir os mesmos fluxos sem dependências ou navegação adicional.

## Riscos / Trade-offs

- **[Risco]** A validação do Xano pode rejeitar cadastros que a interface consideraria válidos se as regras divergirem. **→ Mitigação:** validar casos equivalentes nas duas camadas e testar critérios limítrofes.
- **[Risco]** A política nova é menos rigorosa que uma senha longa sem regras de composição, mas foi escolhida explicitamente para esta experiência. **→ Mitigação:** mostrar os critérios antes do envio e manter a validação no backend.
- **[Risco]** A integração de alterações locais Xano pode divergir do workspace remoto. **→ Mitigação:** conferir o estado atual do workspace conforme o procedimento do projeto, revisar o diff e executar apenas validação/dry-run; não publicar sem aprovação do grupo.
- **[Risco]** Controles de visibilidade podem reduzir acessibilidade se forem apenas ícones sem nome acessível. **→ Mitigação:** expor a ação no nome acessível e validar navegação por teclado e o estado visível/oculto.

## Plano de migração

1. Atualizar e testar o cliente/interface Reflex, incluindo os critérios de cadastro e a apresentação visual.
2. Validar e testar a regra equivalente no endpoint Xano local, sem alterar o contrato público nem o papel padrão.
3. Executar testes focados, `reflex compile --dry`, validação OpenSpec e conferência visual em larguras estreita e ampla.
4. Não há migração de dados: a política vale para novas contas. Validar o diff e o dry-run de publicação conforme as regras do projeto; qualquer push real permanece condicionado à aprovação do grupo.
