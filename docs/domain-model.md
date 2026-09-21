# Domain Model — Sistema de Gerenciamento de Academia

> **Rascunho inicial.** Este documento descreve conceitos e relacionamentos, não tabelas. Regras marcadas com `[VALIDAR]` precisam de confirmação do grupo. Entidades das Fases 2 e 3 fazem parte da visão global, mas **não serão implementadas de imediato**.

## Visão geral dos relacionamentos

```text
Usuário do sistema ──── Perfil (Administrador | Recepcionista | Instrutor)

Aluno
  │
  ├── Matrícula ──── Plano
  │       │
  │       └── Mensalidade ──── Pagamento
  │
  ├── Check-in                                   (Fase 1)
  │
  ├── Reserva ──── Aula ──── Modalidade          (Fase 2)
  │                  │
  │                  └── Instrutor
  │
  ├── Ficha de Treino ──── Exercício             (Fase 3)
  │
  └── Avaliação Física                           (Fase 3)
```

---

## Fase 1 — Núcleo

### Usuário do sistema

Pessoa que acessa o sistema com login (administrador, recepcionista ou instrutor).

**Decisão:** apenas funcionários (administrador, recepcionista e instrutor) possuem login. O aluno é um cadastro, não um usuário do sistema.

**Principais informações:** nome, e-mail, credencial de acesso, perfil, situação (ativo/inativo).

**Relacionamentos:** possui exatamente um perfil. Um instrutor é também um funcionário da academia.

**Regras estruturais:** as permissões dependem do perfil. `[VALIDAR: quais telas/ações cada perfil pode acessar]`

### Aluno

Pessoa cadastrada na academia que treina ou já treinou nela.

**Principais informações:** nome, CPF, data de nascimento, contato, endereço, situação (ativo, inativo, bloqueado) `[VALIDAR]`.

**Relacionamentos:** possui matrículas, check-ins e, nas fases futuras, reservas, fichas de treino e avaliações físicas.

**Regras estruturais:**
- Um aluno é identificado de forma única (por exemplo, pelo CPF). `[VALIDAR]`
- Um aluno não deve ser excluído fisicamente se possuir histórico financeiro ou de frequência.

### Plano

Modelo comercial oferecido pela academia (por exemplo, mensal, trimestral, anual).

**Principais informações:** nome, descrição, duração, valor, situação (ativo/descontinuado). Na Fase 2, pode indicar as modalidades incluídas.

**Relacionamentos:** um plano pode ser usado em várias matrículas.

**Regras estruturais:** alterar o valor de um plano não deve alterar mensalidades já geradas. `[VALIDAR]`

### Matrícula

Vínculo de um aluno com um plano durante um período.

**Principais informações:** data de início, data de término, situação (ativa, trancada, cancelada, encerrada), valor contratado.

**Relacionamentos:** pertence a um aluno e a um plano; gera mensalidades.

**Regras estruturais:**
- Um aluno pode ter várias matrículas ao longo do tempo, mas no máximo uma ativa por vez. `[VALIDAR]`
- O valor contratado é guardado na matrícula, independentemente de mudanças futuras no plano.

### Mensalidade

Cobrança devida por uma matrícula em determinado período.

**Principais informações:** competência (mês/ano), valor, data de vencimento, situação (pendente, paga, atrasada, cancelada).

**Relacionamentos:** pertence a uma matrícula; pode ter pagamentos associados.

**Regras estruturais:** a situação "atrasada" decorre do vencimento sem pagamento. `[VALIDAR: regras de multa, juros e carência]`

### Pagamento

Registro de um valor recebido.

**Principais informações:** valor, data, forma de pagamento (dinheiro, PIX, cartão etc.), usuário que registrou.

**Relacionamentos:** pertence a uma mensalidade.

**Regras estruturais:**
- Pagamentos não são apagados; erros são corrigidos por estorno ou cancelamento rastreável. `[VALIDAR]`
- `[VALIDAR: pagamento parcial é permitido?]`

### Check-in

Registro da presença de um aluno na academia.

**Principais informações:** aluno, data e hora de entrada, usuário que registrou (quando manual).

**Relacionamentos:** pertence a um aluno.

**Regras estruturais:** o check-in depende da situação do aluno e da matrícula. `[VALIDAR: aluno inadimplente pode entrar?]`

---

## Fase 2 — Operação

### Modalidade

Tipo de atividade oferecida (musculação, spinning, funcional, yoga etc.).

**Relacionamentos:** uma modalidade possui várias aulas e pode fazer parte de planos.

### Aula

Sessão de uma modalidade em dia e horário definidos, conduzida por um instrutor.

**Principais informações:** modalidade, instrutor, dia/horário, capacidade máxima, sala.

**Relacionamentos:** possui reservas; pertence a uma modalidade e a um instrutor.

**Regras estruturais:** o número de reservas confirmadas não pode ultrapassar a capacidade.

### Reserva

Vaga de um aluno em uma aula.

**Principais informações:** situação (confirmada, cancelada, presente, falta), data da reserva.

**Relacionamentos:** liga um aluno a uma aula.

**Regras estruturais:** um aluno não pode ter duas reservas ativas para a mesma aula; só alunos com matrícula ativa podem reservar. `[VALIDAR]`

---

## Fase 3 — Acompanhamento do aluno

### Exercício

Movimento de treino cadastrado no catálogo da academia.

**Principais informações:** nome, grupo muscular, descrição, equipamento.

### Ficha de Treino

Conjunto organizado de exercícios prescrito a um aluno por um instrutor.

**Principais informações:** objetivo, período de validade, exercícios com séries, repetições e carga sugerida.

**Relacionamentos:** pertence a um aluno; criada por um instrutor; referencia exercícios.

### Avaliação Física

Registro de medidas e condição física de um aluno em determinada data.

**Principais informações:** data, peso, altura, medidas corporais, observações, instrutor responsável.

**Relacionamentos:** pertence a um aluno.

**Regras estruturais:** é **dado sensível** (saúde). O acesso deve ser restrito ao aluno e aos perfis autorizados. `[VALIDAR]`

---

## Questões em aberto

- Um aluno pode ter mais de uma matrícula ativa (por exemplo, planos de modalidades diferentes)?
- Existem dependentes ou planos familiares?
- Como tratar trancamento e cancelamento (impacto em mensalidades futuras)?
