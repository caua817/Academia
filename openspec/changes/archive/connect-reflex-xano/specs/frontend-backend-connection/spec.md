# Spec Delta: frontend-backend-connection

## ADDED Requirements

### Requirement: O frontend deve ler a URL da API do Xano de uma variável de ambiente

O app Reflex SHALL obter a URL base da API do Xano a partir da
variável de ambiente `API_BASE_URL`, nunca de um valor fixo no
código-fonte.

#### Scenario: Variável de ambiente configurada

- **GIVEN** um arquivo `.env` local com `API_BASE_URL` definida
- **WHEN** o app Reflex inicia
- **THEN** o cliente da API usa essa URL para todas as chamadas ao Xano

#### Scenario: Variável de ambiente ausente

- **GIVEN** que `API_BASE_URL` não está definida no ambiente
- **WHEN** o app Reflex tenta iniciar o cliente da API
- **THEN** o sistema apresenta um erro claro indicando que a variável
  está faltando, em vez de falhar silenciosamente ou usar uma URL
  fixa

### Requirement: O sistema deve prover uma forma de verificar a conexão com o Xano

O app SHALL oferecer uma tela ou seção de diagnóstico que chama um
endpoint do Xano e informa ao usuário se a conexão foi bem-sucedida.

#### Scenario: Backend acessível

- **GIVEN** que o workspace Xano está acessível pela URL configurada
- **WHEN** o usuário abre a tela de diagnóstico
- **THEN** o sistema mostra uma mensagem indicando que a conexão com o
  Xano foi bem-sucedida

#### Scenario: Backend inacessível

- **GIVEN** que o workspace Xano não está acessível (URL errada ou
  backend fora do ar)
- **WHEN** o usuário abre a tela de diagnóstico
- **THEN** o sistema mostra uma mensagem de erro compreensível, sem
  quebrar o restante do app e sem expor detalhes técnicos sensíveis
