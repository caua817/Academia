# Design

## Context

Consulte a matriz confirmada na [proposta](./proposal.md) e os requisitos completos em `specs/`. Atualmente o Reflex protege quase todas as páginas com `require_admin`; o estado compartilhado diferencia administrador e equipe de acompanhamento, que inclui instrutores. No Xano, a maioria dos endpoints operacionais exige `admin`; `enforce_training_access` já permite `admin` e `instrutor`. O helper hierárquico `enforce_role` não contém os perfis `recepcionista` e `instrutor`. O endpoint de planos hoje lista planos ativos e descontinuados, e a tela de matrícula busca alunos, planos e matrículas com o mesmo token.

## Goals / Non-Goals

**Goals:**
- Aplicar a matriz de acesso confirmada em páginas, ações do frontend e endpoints do Xano.
- Permitir à recepção as tarefas operacionais sem conceder administração de planos, funcionários, agenda, relatórios ou correções financeiras.
- Limitar a consulta do instrutor aos dados de aluno e frequência necessários ao acompanhamento, preservando o acesso existente às funções de treino.
- Negar acesso por padrão e limpar dados da sessão quando uma consulta for negada.

**Non-Goals:**
- Criar ou alterar o mecanismo de convite e ativação de funcionários.
- Permitir ao instrutor editar cadastro de aluno ou registrar check-in.
- Conceder correções de lançamentos financeiros à recepção.
- Criar permissões por funcionário ou um editor de papéis.

## Decisions

1. **Usar allowlists por perfil e por operação, não uma hierarquia numérica comum.** Administrador tem acesso a todas as áreas; permissões da recepção e do instrutor são distintas e não formam uma escala universal. O frontend deve validar a rota e ocultar ações proibidas, enquanto cada endpoint Xano valida o perfil autorizado para sua operação. Isso evita que autorizar uma leitura também autorize escrita ou correções financeiras. Alternativa descartada: apenas adicionar recepcionista à hierarquia de `enforce_role`, pois isso ampliaria acesso a endpoints sem diferenciar operações.

2. **Preservar o endpoint de planos e filtrar conforme o perfil.** `admin` continua recebendo a lista usada pela gestão de planos; `recepcionista` recebe somente planos ativos para a tela de matrícula. A página de configuração de planos permanece administrativa. Alternativa descartada: permitir à recepção consultar planos descontinuados ou duplicar a gestão de planos na área de matrícula.

3. **Separar consulta de escrita em alunos, check-ins e financeiro.** Recepcionistas operam alunos, matrículas, registro/consulta de pagamentos e check-ins, mas não correções de pagamentos. Instrutores recebem consultas mínimas de aluno/frequência e mantêm acesso às capacidades de acompanhamento já autorizadas. Dados pessoais e de saúde não necessários não devem ser incluídos nas respostas para cada perfil.

4. **Manter o cadastro de funcionários por convite existente.** A página continua sendo exclusiva de `admin`, com seleção de perfil e ativação pelo próprio funcionário. A API de funcionários permanece sob a change `api-gestao-funcionarios`; esta change não cria uma segunda rota nem configura senha.

## Risks / Trade-offs

- [Permissões divergentes entre Reflex e Xano] → Criar testes de matriz de perfil para chamadas diretas aos endpoints e para acesso às páginas; o backend é sempre a autoridade.
- [A tela de matrícula depende de dados de aluno e plano] → Permitir à recepção apenas as consultas operacionais necessárias e retornar apenas alunos/planos elegíveis; manter rotas de configuração administrativas.
- [Permissão de instrutor pode expor dados pessoais ou de saúde] → Aplicar respostas mínimas em consultas gerais e manter avaliações somente nas rotas de acompanhamento já autorizadas.
- [Endpoints existentes podem ter chamadas internas compartilhadas entre páginas] → Identificar cada endpoint por operação e preservar o comportamento administrativo, sem conceder autorização ampla a uma função compartilhada.

## Migration Plan

Não há migração de dados. Implementar e testar a matriz no frontend e no Xano, validar todos os perfis por endpoint, executar os testes e o dry-run do Xano, e revisar o diff. Não publicar no workspace Xano sem aprovação explícita. Em caso de rollback, restaurar as allowlists anteriores e manter os registros; nenhum dado será removido.
