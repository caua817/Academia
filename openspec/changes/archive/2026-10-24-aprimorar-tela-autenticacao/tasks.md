# Tarefas

## 1. Política de senha no cadastro

- [x] 1.1 Implementar os critérios de senha no endpoint local de cadastro Xano antes da criação da conta; consultar a documentação XanoScript e validar a sintaxe com o Xano Developer MCP, confirmando que senha inválida é rejeitada e que cadastro público e papel `member` são preservados.
- [x] 1.2 Espelhar a política de senha no cliente Reflex, indicar cada critério atendido durante a digitação e impedir envio inválido; cobrir limites e combinações com testes focados de autenticação.

## 2. Visibilidade e apresentação dos formulários

- [x] 2.1 Adicionar controles independentes e acessíveis para mostrar/ocultar a senha no login e no cadastro; verificar alternância por teclado e preservação do conteúdo.
- [x] 2.2 Melhorar espaçamento, alinhamento, hierarquia e responsividade da página de login e do modal, sem regressão nos fluxos; conferir visualmente em larguras estreita e ampla, inclusive mensagens e ações.

## 3. Verificação integrada

- [x] 3.1 Executar os testes focados de autenticação, `reflex compile --dry` e `openspec validate aprimorar-tela-autenticacao --strict`; corrigir falhas introduzidas pela change.
- [x] 3.2 Revisar o diff do endpoint Xano e executar o dry-run de publicação conforme as regras do projeto; confirmar que não houve push real sem aprovação do grupo.
