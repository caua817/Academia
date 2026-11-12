# Design

## Context

Consulte [proposal.md](./proposal.md) para a motivação e [specs/student-management/spec.md](./specs/student-management/spec.md) para o comportamento esperado. O formulário Reflex envia o nome e os campos opcionais vazios como `null`. A comparação do pull publicado com os arquivos locais confirmou que ambos correspondem; porém, no endpoint publicado, CPF, nascimento, contato e endereço estão declarados como opcionais, mas não anuláveis. Na sintaxe Xano, isso permite omitir os campos, mas não enviar `null`, como o cliente faz. O e-mail é anulável, porém obrigatório no contrato atual. Essa incompatibilidade explica a falha no cadastro e será corrigida declarando todos os campos opcionais como opcionais e anuláveis; a autorização e a exigência de nome permanecem inalteradas.

## Goals / Non-Goals

**Goals:**

- Localizar a divergência entre payload, endpoint, tabela e versão publicada antes de escolher uma correção.
- Preservar o contrato existente de cadastro administrativo e a autorização executada no backend.
- Evitar duplicar um cadastro de teste caso uma requisição que retornou erro tenha sido persistida antes da falha de resposta.

**Non-Goals:**

- Alterar os campos de domínio do aluno, a regra de autorização ou outros fluxos de gestão de alunos.
- Corrigir ou contornar a falha escondendo o HTTP 500 ou apresentando uma confirmação sem persistência comprovada.
- Publicar alterações reais no Xano sem aprovação explícita do grupo.

## Decisions

### Reproduzir e comparar antes de corrigir

Reproduzir com um usuário `admin` e dados exclusivamente sintéticos, registrando apenas o método, caminho, código de resposta e campos não sensíveis necessários para identificar o contrato. Comparar a carga enviada pelo cliente, o endpoint e a tabela locais com a configuração efetiva do runtime. A correção será escolhida somente após a causa ser confirmada.

Alternativa descartada: alterar preventivamente o endpoint ou o payload local. O 500 pode decorrer de divergência do workspace, validação ou persistência; escolher uma causa sem evidência pode mascarar o problema ou afastar o contrato local do publicado.

### Manter compatibilidade de campos opcionais

Campos opcionais vazios enviados como `null` ou omitidos devem continuar sendo aceitos como ausentes. Se a causa estiver no cliente, ajustar a serialização sem retirar dados preenchidos; se estiver no Xano, corrigir o endpoint ou a tabela de forma compatível. Em qualquer caso, manter a autorização `admin` no backend e propagar falhas sem sucesso fictício.

Alternativa descartada: tornar campos pessoais obrigatórios para contornar o erro. Isso mudaria o contrato de domínio e exigiria dados que a spec mantém opcionais.

### Tornar o teste repetível sem duplicar registros

Usar um identificador/nome sintético exclusivo e verificar se o registro já existe antes de repetir um `POST` que falhou. Um HTTP 500 não prova, por si só, que a persistência não ocorreu. Não excluir fisicamente registros; manter qualquer dado de teste claramente identificável e utilizar somente informações fictícias.

Alternativa descartada: repetir automaticamente a criação após erro ou remover o registro para “limpar” o teste, pois ambas as ações podem criar duplicatas ou apagar histórico.

### Sincronização e publicação do Xano

Antes de editar arquivos Xano locais, verificar possíveis mudanças remotas e seguir a orientação do projeto para `xano workspace pull`; revisar o diff para preservar alterações locais. Validar o XanoScript e executar `xano workspace push --dry-run` após a implementação. Um push real depende de aprovação explícita do grupo.

## Risks / Trade-offs

- **[Risco]** O endpoint publicado diverge dos arquivos locais. → **Mitigação:** comparar o runtime e sincronizar/revisar antes de alterar código.
- **[Risco]** O servidor persistiu o aluno antes de retornar HTTP 500. → **Mitigação:** procurar o identificador sintético antes de qualquer nova tentativa e não repetir a criação cegamente.
- **[Risco]** Uma correção pode expor dados pessoais em logs ou respostas. → **Mitigação:** usar dados sintéticos e registrar somente metadados não sensíveis; manter os campos sensíveis restritos aos endpoints autorizados.
- **[Risco]** A validação local passa, mas o runtime continua sem o ajuste publicado. → **Mitigação:** manter a verificação runtime como critério obrigatório e não fazer push sem aprovação.

## Migration Plan

1. Confirmar se a primeira tentativa sintética foi persistida antes de repetir a criação.
2. Comparar cliente, endpoint, tabela e runtime; documentar a causa sem incluir credenciais ou dados pessoais.
3. Implementar a menor correção compatível com a spec e cobri-la com testes locais.
4. Validar XanoScript, executar verificações locais e revisar o dry-run do push.
5. Solicitar aprovação do grupo antes de publicar e, após aprovação, verificar a criação e leitura do registro sintético no runtime.

Rollback: reverter somente a correção de código se a validação falhar; não excluir fisicamente registros de teste já persistidos.
