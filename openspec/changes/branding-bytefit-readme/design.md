# Design

## Contexto

A aplicação usa Reflex. A identidade aparece como “SISTEMA ACADEMIA” na tela de login e “ACADEMIA / GESTÃO FITNESS” no cabeçalho da navegação. O `README.md` atual já contém instalação e execução, mas ainda descreve reservas na interface e precisa ser alinhado à versão atual.

## Objetivos / Fora do escopo

**Objetivos:**

- Apresentar ByteFit na tela de login e no cabeçalho da navegação.
- Deixar o README suficiente para clonar ou baixar o projeto, preparar o ambiente Python e executar a aplicação no Windows.

**Fora do escopo:**

- Alterar autenticação, autorização, API Xano, dados ou infraestrutura de hospedagem.
- Criar uma nova identidade visual, logotipo ou dependência.
- Alterar a visibilidade do repositório, que já está público.

## Decisões

- Alterar somente os textos da identidade na tela de login e na navegação; manter ícones, estilos e layout atuais para reduzir risco de regressão.
- Atualizar o README existente em português e documentar os comandos compatíveis com o ambiente Windows e Reflex atual. Incluir a dependência de internet/API Xano e alertas para não versionar `.env` nem credenciais.
- Adicionar testes que confirmem a presença do nome ByteFit nas duas superfícies e revisar manualmente se o README não anunciar funcionalidades removidas.

## Riscos / Trade-offs

- **[Risco]** A documentação ficar desatualizada em relação à navegação real. **→ Mitigação:** validar os nomes de telas e perfis contra o código atual e os testes existentes.
- **[Risco]** Expor credenciais em instruções de configuração. **→ Mitigação:** usar somente nomes de variáveis e valores de exemplo claramente fictícios; não copiar `.env` local.

## Plano de migração

Não há migração de dados nem mudanças no backend. Reversão possível restaurando os textos e o README anteriores.
