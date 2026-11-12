# Proposta: Aprimorar a tela de autenticação

## Por quê

A tela de login e o modal de cadastro deixam os campos de senha sempre ocultos e têm pouco espaçamento visual, o que dificulta a leitura e o preenchimento. O cadastro também não apresenta nem aplica uma política explícita de senha, deixando incerto para a pessoa usuária quais credenciais serão aceitas.

## O que muda

- Adicionar controles acessíveis para mostrar ou ocultar a senha nos campos de login e cadastro.
- Apresentar no cadastro os requisitos da senha e validá-los antes do envio: mínimo de 8 caracteres, ao menos uma letra maiúscula, uma minúscula e um número.
- Aplicar os mesmos requisitos no endpoint público de cadastro do Xano, para que a política não dependa apenas da interface.
- Melhorar espaçamento, alinhamento, hierarquia visual e adaptação a telas menores na página de login e no modal de cadastro, preservando os fluxos existentes.
- Exibir de forma clara quais requisitos da senha ainda não foram atendidos, sem apagar a senha enquanto a pessoa a corrige.

Fora do escopo: mudar o fluxo de login, os papéis de usuário, recuperação de senha, armazenamento de credenciais ou outras telas do sistema.

## Capabilities

### Novas capabilities

- `authentication`: experiência de autenticação com visibilidade de senha, política verificável no cadastro e apresentação responsiva.

### Capabilities modificadas

Nenhuma. Ainda não há specs consolidadas em `openspec/specs/`; esta change introduz os requisitos da capability `authentication`.

## Impacto

- Frontend Reflex: `academia/login.py` e os testes do fluxo de autenticação.
- Backend Xano: validação da senha no endpoint `POST /auth/signup`, mantendo o cadastro público sem token e o papel padrão `member`.
- Documentação: nova spec delta para `authentication`.
- Nenhuma dependência nova prevista. A alteração do código local Xano deverá ser revisada e validada antes de qualquer publicação no workspace.
