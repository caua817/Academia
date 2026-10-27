# Design: Gestão de funcionários

## Contexto

Ver [proposal.md](./proposal.md) para motivação e escopo, e [spec.md](./specs/employee-management/spec.md) para os comportamentos exigidos. O app já usa Reflex, mantém o token no `LoginState` e centraliza as chamadas Xano em `academia/services/xano_client.py`. Ainda não existe área nem API local de funcionários. A tabela `user.xs` declara atualmente `admin` e `member`; esta change assume que a API compatível aceitará `admin`, `recepcionista` e `instrutor`, conforme decisão do usuário.

## Objetivos / Não objetivos

**Objetivos:**

- Integrar a gestão de contas de funcionários ao shell e à navegação Reflex existentes.
- Usar convites de e-mail sem transportar senhas pela interface.
- Propagar falhas HTTP e de conexão pelo cliente atual e apresentar estados explícitos na interface.
- Tratar o papel administrativo como autorização obrigatória do backend; a visibilidade de rota no frontend é apenas uma conveniência de UX.

**Não objetivos:**

- Alterar Xano, criar tabelas ou endpoints, ou executar validações/runtime no workspace.
- Implementar fluxo de convite, envio de e-mail ou definição de senha no backend.
- Criar cadastro de dados trabalhistas, salário, folha de pagamento ou redefinição de senha.

## Decisões

### Usar uma conta de usuário como registro de funcionário

Funcionários são contas de acesso, não uma entidade de RH separada, conforme o modelo de domínio. A lista e os formulários trabalharão com nome, e-mail, perfil, situação e, se a API retornar, estado do convite. Senhas e tokens não serão campos da interface.

**Alternativa descartada:** criar um cadastro separado de funcionário. Isso duplicaria identidade e perfil de acesso sem suporte no modelo atual.

### Convite por e-mail para provisionar acesso

O formulário envia nome, e-mail e perfil. O backend é assumido como responsável por gerar e enviar o convite e permitir que o funcionário defina a senha. A interface não coleta uma senha temporária nem exibe tokens do convite.

**Alternativa descartada:** permitir que o administrador escolha a senha. Isso exige transmitir e expor uma credencial que deve permanecer privada do funcionário.

### Contrato HTTP pressuposto

Todas as operações usam o bearer token mantido na sessão existente. Os caminhos e formatos abaixo serão tratados como contrato esperado pela camada Reflex; não representam endpoints implementados ou validados nesta change.

| Operação | Método e caminho | Entrada / resposta esperada |
|---|---|---|
| Consultar identidade e perfil | `GET /auth/me` | Retorna a conta atual e `role`. O estado mostra a área administrativa somente para `admin`; a API ainda precisa aplicar a autorização. |
| Listar funcionários | `GET /funcionarios` | Lista com `id`, `name`, `email`, `role`, `situacao` e, opcionalmente, `status_convite`. |
| Enviar convite | `POST /funcionarios/convites` | Entrada: `name`, `email`, `role`. Resposta: registro criado e estado do convite, sem senha ou token. |
| Carregar detalhes | `GET /funcionarios/detalhes/{funcionario_id}` | Retorna os campos operacionais necessários para edição, sem credenciais. |
| Editar conta | `PUT /funcionarios/atualizar/{funcionario_id}` | Entrada: `name`, `email`, `role`; resposta com dados operacionais atualizados. |
| Desativar conta | `PATCH /funcionarios/desativar/{funcionario_id}` | Mantém o registro persistido e retorna a situação inativa. |
| Reativar conta | `PATCH /funcionarios/ativar/{funcionario_id}` | Mantém o registro persistido e retorna a situação ativa. |

Os valores de perfil enviados serão `admin`, `recepcionista` e `instrutor`; as situações serão `Ativo` e `Inativo`, alinhadas ao contrato visual já usado na gestão de alunos. A lista será filtrada localmente por nome, e-mail, perfil ou situação. Respostas HTTP inválidas ou incompatíveis com o formato esperado serão tratadas como erro, não como lista vazia.

### Autorização administrativa e sessão

Na entrada da área, o estado consultará `/auth/me` para identificar o perfil e só então carregará a lista. Os endpoints de convite, consulta, edição e alteração de situação devem ser autorizados para `admin` no backend. Um HTTP 403 não libera dados; um HTTP 401 limpa os estados de funcionários e a sessão e redireciona ao login.

**Alternativa descartada:** tratar a ocultação do menu ou da rota Reflex como controle de acesso. O frontend não é fronteira de segurança.

### Componentes e testes

Reutilizar a navegação, identidade visual e cliente HTTP atuais, sem adicionar dependências. Criar estado Reflex dedicado, tabela com campos operacionais, busca, formulário de convite/edição e confirmação para alterações de situação. Testar transformação de dados, métodos/caminhos HTTP e erros usando transporte mockado local; não chamar o Xano real.

## Riscos / Trade-offs

- **[Risco]** A tabela Xano atual não declara os perfis `recepcionista` e `instrutor`, e os endpoints definidos neste documento ainda não existem no código local. **→ Mitigação:** tratar esses caminhos e perfis como contrato futuro e bloquear a integração real até que a API os implemente; não afirmar compatibilidade runtime.
- **[Risco]** A interface pode ser acessada por um usuário não administrativo antes de a consulta de perfil terminar. **→ Mitigação:** manter a lista oculta durante o carregamento do perfil e depender sempre da autorização server-side.
- **[Risco]** O serviço de convite pode falhar depois de a interface enviar os dados. **→ Mitigação:** só confirmar sucesso após resposta HTTP bem-sucedida e permitir nova tentativa após erro.

## Plano de migração

1. Implementar o cliente HTTP, estado e componentes Reflex com os caminhos e formatos esperados.
2. Validar localmente com testes mockados e compilação Reflex, sem chamadas autenticadas ao Xano.
3. Integrar a interface somente quando o contrato correspondente estiver disponível no backend; antes disso, erros da API permanecem explícitos.
4. Para rollback, remover a rota e a navegação de funcionários; não excluir contas ou convites existentes no backend.

## Questões em aberto

Nenhuma para o escopo frontend definido. A implementação correspondente dos endpoints e dos novos perfis permanece fora desta change e precisa ocorrer no backend antes da integração real.
