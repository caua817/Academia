# Tasks

## 1. Remover a interface de acompanhamento

- [x] 1.1 Remover links de navegação, rotas e conteúdo Reflex de exercícios, fichas e avaliações; verificar que essas URLs não exibem mais as páginas e que as rotas mantidas ainda compilam.
- [x] 1.2 Remover estados, carregadores, eventos, imports e cliente Xano exclusivos dessas páginas, preservando auxiliares compartilhados; verificar testes de autenticação, navegação e páginas ainda suportadas.
- [x] 1.3 Remover ou atualizar testes exclusivos das funcionalidades retiradas sem enfraquecer os testes das funcionalidades mantidas; executar a suíte direcionada e confirmar que os testes restantes passam.

## 2. Remover operações locais exclusivas e validar

- [x] 2.1 Rastrear referências de endpoints, funções e tabelas de exercícios, fichas e avaliações; remover somente endpoints e funções locais sem consumidores remanescentes e verificar XanoScript com a documentação/validador oficial.
- [x] 2.2 Preservar tabelas e registros existentes e confirmar que nenhum comando ou diff inclui exclusão física de dados ou push remoto ao Xano.
- [x] 2.3 Executar compilação Reflex e testes de regressão das páginas mantidas, confirmando que gestão de funcionários, alunos, operação e finanças continuam disponíveis.
