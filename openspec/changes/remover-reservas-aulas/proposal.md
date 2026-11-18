# Proposta: Remover a interface de reservas de aulas

## Por quê

A tela de reservas de aulas tem apresentado falhas recorrentes e gera chamadas e operações que não são necessárias para a entrega atual do aplicativo. A remoção da superfície de reservas no Reflex reduz esses pontos de falha sem apagar o histórico existente nem alterar os serviços já publicados no Xano.

## O que muda

- **BREAKING:** remover o link “Reservas”, a página e a rota `/reservas` do aplicativo Reflex, incluindo os controles para criar, consultar, cancelar e registrar comparecimento ou falta.
- Remover do fluxo Reflex o estado e os eventos exclusivos de gerenciamento de reservas, bem como seus wrappers locais não utilizados para chamar a API.
- Remover a ocupação de reservas da agenda de sessões e os indicadores de reservas/ocupação da tela de relatórios; manter o cadastro e a organização de sessões, modalidades e capacidade.
- Preservar os endpoints Xano existentes, os registros de reservas e seu histórico. Não alterar, excluir ou publicar mudanças no workspace Xano como parte desta mudança.
- Atualizar a documentação e os testes do frontend para refletir que reservas não estão disponíveis na interface.

## Capabilities

### Novas Capabilities

Nenhuma.

### Modified Capabilities

- `class-reservation-management`: a interface Reflex deixa de expor a gestão de reservas; os endpoints Xano e os registros existentes são preservados.
- `class-session-management`: a agenda continua exibindo e gerenciando sessões, mas deixa de apresentar ocupação derivada de reservas.
- `management-reports`: os relatórios da interface deixam de apresentar contagens e percentuais de reservas/ocupação, mantendo os demais indicadores.

## Impact

- Frontend Reflex: `academia/academia.py`, `academia/access_control.py` e `academia/operacao.py`.
- Cliente HTTP local: remoção dos wrappers de reserva não utilizados em `academia/services/xano_client.py`; os endpoints Xano continuam inalterados.
- Testes: atualização de `tests/test_operation_ui.py` e `tests/test_operation_client.py`, incluindo a ausência da rota/link e das métricas removidas.
- Documentação do escopo atual em `docs/project-overview.md`.
- Nenhuma alteração de banco, dados, endpoints ou workspace Xano; nenhuma dependência nova.
