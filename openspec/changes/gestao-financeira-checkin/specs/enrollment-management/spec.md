# Spec Delta

## ADDED Requirements

### Requirement: A criação da matrícula gera suas mensalidades

O sistema SHALL gerar, ao criar uma matrícula, uma mensalidade por mês da duração contratada, cada uma pelo valor mensal congelado na matrícula, sem pró-rata, multa ou juros. A primeira mensalidade SHALL vencer no dia 10 da competência inicial se essa data ainda não passou; caso contrário, SHALL vencer no próximo dia 10. As seguintes SHALL vencer no dia 10 de cada mês subsequente.

#### Scenario: Gerar mensalidades da matrícula
- **WHEN** um usuário `admin` cria uma matrícula válida
- **THEN** o sistema cria exatamente a quantidade de mensalidades correspondente à duração contratada, com o valor mensal contratado e seus vencimentos

#### Scenario: Início da matrícula após o dia 10
- **WHEN** a data de início da matrícula ocorre depois do dia 10
- **THEN** a primeira mensalidade vence no dia 10 do mês seguinte

#### Scenario: Falha durante a criação da matrícula ou mensalidades
- **WHEN** o sistema não consegue persistir a matrícula ou todas as mensalidades previstas
- **THEN** o sistema não confirma a operação deixando matrícula ou parcelas parcialmente criadas

#### Scenario: Plano alterado após a matrícula
- **WHEN** o plano é alterado depois da criação da matrícula
- **THEN** as mensalidades da matrícula mantêm o valor mensal e a quantidade definidos pelas condições contratadas

#### Scenario: Matrícula existente antes da implantação financeira
- **WHEN** o sistema habilita a gestão financeira para matrículas criadas antes desta funcionalidade
- **THEN** o sistema não gera mensalidades retroativas automaticamente para essas matrículas
