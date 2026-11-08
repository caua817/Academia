# Proposal

## Why

Ao tentar cadastrar um aluno sintético pelo painel Reflex, a API Xano respondeu HTTP 500 mesmo com o nome preenchido e os demais campos opcionais vazios. Isso impede criar um aluno de teste para concluir a demonstração de matrícula e indica uma divergência que precisa ser diagnosticada entre o payload, o endpoint e a tabela em runtime.

## What Changes

- Investigar a causa do HTTP 500 comparando a requisição de cadastro, o endpoint e a tabela locais com o contrato efetivamente publicado no Xano, sem presumir a origem da falha.
- Corrigir somente a divergência confirmada para que campos opcionais vazios ou nulos não impeçam um cadastro válido com nome preenchido.
- Verificar o cadastro e as respostas de erro com dados sintéticos, preservando a autorização administrativa e sem expor dados pessoais ou detalhes internos.
- Não publicar alterações reais no workspace Xano sem aprovação explícita do grupo.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `student-management`: esclarecer e garantir o cadastro administrativo quando os campos opcionais não são preenchidos e chegam como nulos.

## Impact

- Frontend Reflex: payload enviado pelo formulário e apresentação dos resultados.
- Xano: endpoint de criação de aluno e, se a causa confirmada exigir, compatibilidade com a tabela.
- Testes: cobertura local do contrato e verificação runtime com registro sintético.
- Nenhuma dependência nova prevista.
