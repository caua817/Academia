# Proposta: API de gestão de funcionários

## Por quê

A interface e o cliente HTTP de funcionários já estão implementados, mas os endpoints correspondentes não existem no workspace Xano local. A ausência da API impede validar a integração real e concluir o fluxo de gestão previsto na capability `employee-management`.

## O que muda

- Implementar no Xano o contrato já consumido pelo frontend para listar e consultar funcionários, convidar por e-mail, editar dados operacionais e ativar/desativar contas.
- Aplicar autorização administrativa no backend a todas as operações e retornar somente os campos operacionais necessários.
- Provisionar convites sem transportar ou expor senhas; reutilizar um fluxo de criação de senha seguro, com link de uso único e expiração, validado contra os recursos existentes do Xano.
- Validar o XanoScript e o plano de publicação em dry-run. Não publicar no workspace remoto sem aprovação explícita.

Ficam fora do escopo: cadastro público de contas, alterações no frontend, redefinição geral de senha, dados de RH e publicação não aprovada no Xano.

## Capabilities

### Novas capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A capability `employee-management` já define os comportamentos; esta change implementa o contrato existente sem alterar seus requisitos.

## Impacto

- Endpoints, funções e, se necessário, campos da tabela `user` na pasta `xano/`.
- Contrato consumido por `academia/services/xano_client.py`.
- Testes locais de contrato/segurança e validação XanoScript.
- Nenhuma dependência nova prevista.
