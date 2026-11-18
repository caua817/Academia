# Proposta: Remover telas de acompanhamento do aluno

## Por quê

O grupo decidiu que o aplicativo de gestão não precisa oferecer as telas de exercícios, fichas de treino e avaliações físicas. Essas funcionalidades ampliam o escopo do sistema e envolvem dados de saúde que não são necessários para a gestão operacional pretendida.

## O que muda

- **BREAKING**: Remover do aplicativo as páginas, navegação e operações de interface para catálogo de exercícios, fichas de treino e avaliações físicas.
- Remover as rotas e endpoints Xano dedicados exclusivamente a essas telas, após verificar que não são dependências de outras funcionalidades.
- Preservar tabelas e registros existentes durante esta mudança; nenhuma exclusão física de dados será feita.
- Manter inalteradas as telas e APIs de alunos, funcionários, autenticação, operação e gestão financeira.

## Capabilities

### Novas capabilities

Nenhuma.

### Capabilities modificadas

- `exercise-catalog`: remover do produto a manutenção e consulta do catálogo de exercícios.
- `training-plan-management`: remover do produto a criação, consulta e manutenção de fichas de treino.
- `physical-assessment-management`: remover do produto o registro e a consulta de avaliações físicas.

## Impacto

- Interface Reflex em `academia/acompanhamento.py` e `academia/academia.py`, navegação e estados de autorização.
- Endpoints e funções Xano de `acompanhamento`, `exercicios`, `fichas` e `avaliacoes`, após verificar referências cruzadas.
- Testes de UI, cliente Xano, permissões e integração relacionados às três funcionalidades.
- Tabelas e registros do Xano são preservados; nenhuma operação destrutiva de dados faz parte desta mudança.
- A publicação do frontend e a correção do fluxo de convite de funcionários permanecem na change `publicar-frontend-para-convites`.
