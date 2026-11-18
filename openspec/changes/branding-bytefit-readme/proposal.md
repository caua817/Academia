# Proposta: Identidade ByteFit e README do repositório

## Por quê

A aplicação ainda apresenta nomes genéricos de academia na tela de login e na navegação, enquanto o README contém instruções e funcionalidades que não refletem completamente a versão atual. Identificar o produto como ByteFit e documentar o uso corretamente prepara o repositório para apresentação e instalação em outro computador.

## O que muda

- Substituir os títulos genéricos da tela de login e da navegação pelo nome **ByteFit**.
- Atualizar o `README.md` em português com visão geral, requisitos, instalação, configuração da API, execução local, perfis, limitações e verificações, alinhado ao estado atual do projeto.
- Manter autenticação, autorização, APIs, dados e dependências inalterados.
- O repositório `caua817/Academia` já foi identificado como público no GitHub; nenhuma mudança de visibilidade será necessária nesta change.

## Capabilities

### Novas Capabilities

- `application-branding`: identifica a aplicação como ByteFit nas superfícies principais da interface.

### Capabilities Modificadas

Nenhuma.

## Impacto

- Interface Reflex: `academia/login.py` e `academia/academia.py`.
- Documentação do repositório: `README.md`.
- Testes de interface relacionados à identidade exibida.
- Nenhuma alteração no Xano, em dados, APIs, permissões, dependências ou configuração de visibilidade do GitHub.
