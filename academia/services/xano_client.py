import os
from collections.abc import Mapping

import httpx

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://x8ki-letl-twmt.n7.xano.io/api:sGd5fzIy",
)
JsonPayload = Mapping[str, str | int | float | None]
QueryParams = Mapping[str, str]


class XanoAPIError(Exception):
    """Indica falha de comunicação ou resposta inválida da API Xano."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class XanoClient:
    @staticmethod
    def _contains_employee_credential(data: object) -> bool:
        if isinstance(data, dict):
            for key, value in data.items():
                normalized_key = "".join(
                    character
                    for character in str(key).casefold()
                    if character.isalnum()
                )
                if (
                    "password" in normalized_key
                    or "senha" in normalized_key
                    or "token" in normalized_key
                    or "credential" in normalized_key
                ):
                    return True
                if XanoClient._contains_employee_credential(value):
                    return True
        elif isinstance(data, list):
            return any(
                XanoClient._contains_employee_credential(item)
                for item in data
            )
        return False

    @staticmethod
    def _validate_employee_payload(payload: JsonPayload) -> None:
        allowed_fields = {"name", "email", "role"}
        if (
            set(payload) != allowed_fields
            or XanoClient._contains_employee_credential(payload)
        ):
            raise XanoAPIError(
                "A solicitação de funcionário contém campos inválidos."
            )

    @staticmethod
    def _expect_employee_object(data: object) -> dict:
        employee = XanoClient._expect_object(data)
        if XanoClient._contains_employee_credential(employee):
            raise XanoAPIError(
                "A API retornou campos de credencial inesperados."
            )
        return employee

    @staticmethod
    def _request(
        method: str,
        path: str,
        token: str,
        payload: JsonPayload | None = None,
        params: QueryParams | None = None,
    ) -> object:
        if not token.strip():
            raise XanoAPIError("Sua sessão expirou. Faça login novamente.", 401)

        headers = {"Authorization": f"Bearer {token}"}
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.request(
                    method,
                    f"{API_BASE_URL.rstrip('/')}{path}",
                    headers=headers,
                    json=payload,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as error:
            detail = ""
            try:
                error_data = error.response.json()
            except ValueError:
                error_data = None
            if isinstance(error_data, dict):
                for field in ("message", "error"):
                    value = error_data.get(field)
                    if isinstance(value, str) and value.strip():
                        detail = value.strip()
                        break
            message = (
                f"A API respondeu com o status HTTP {error.response.status_code}."
            )
            if detail:
                message = f"{message} {detail}"
            raise XanoAPIError(
                message,
                error.response.status_code,
            ) from error
        except httpx.RequestError as error:
            raise XanoAPIError("Não foi possível conectar à API.") from error
        except ValueError as error:
            raise XanoAPIError("A API retornou uma resposta inválida.") from error

        return data

    @staticmethod
    def _expect_object(data: object) -> dict:
        if not isinstance(data, dict):
            raise XanoAPIError("A API retornou um registro inválido.")
        return data

    @staticmethod
    def _expect_list(data: object, resource_name: str) -> list[dict]:
        if not isinstance(data, list) or any(
            not isinstance(item, dict) for item in data
        ):
            raise XanoAPIError(
                f"A API retornou uma lista de {resource_name} inválida."
            )
        return data

    @staticmethod
    def _expect_records(
        data: object,
        resource_name: str,
        required_fields: tuple[str, ...],
    ) -> list[dict]:
        records = XanoClient._expect_list(data, resource_name)
        if any(
            any(field not in record for field in required_fields)
            for record in records
        ):
            raise XanoAPIError(
                f"A API retornou registros de {resource_name} incompletos."
            )
        return records

    @staticmethod
    def _expect_record(
        data: object,
        resource_name: str,
        required_fields: tuple[str, ...],
    ) -> dict:
        record = XanoClient._expect_object(data)
        if any(field not in record for field in required_fields):
            raise XanoAPIError(
                f"A API retornou um registro de {resource_name} incompleto."
            )
        return record

    @staticmethod
    def _validate_payload_fields(
        payload: JsonPayload,
        expected_fields: set[str],
        resource_name: str,
    ) -> None:
        if set(payload) != expected_fields:
            raise XanoAPIError(
                f"A solicitação de {resource_name} contém campos inválidos."
            )

    @staticmethod
    def get_alunos(token: str) -> list[dict]:
        """Busca os alunos e sinaliza explicitamente falhas da API."""
        data = XanoClient._request("GET", "/alunos", token)
        return XanoClient._expect_list(data, "alunos")

    @staticmethod
    def get_current_user(token: str) -> dict:
        data = XanoClient._request("GET", "/auth/me", token)
        return XanoClient._expect_employee_object(data)

    @staticmethod
    def get_funcionarios(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/funcionarios", token)
        employees = XanoClient._expect_list(data, "funcionários")
        if XanoClient._contains_employee_credential(employees):
            raise XanoAPIError(
                "A API retornou campos de credencial inesperados."
            )
        return employees

    @staticmethod
    def get_funcionario(token: str, funcionario_id: int) -> dict:
        data = XanoClient._request(
            "GET",
            f"/funcionarios/detalhes/{funcionario_id}",
            token,
        )
        return XanoClient._expect_employee_object(data)

    @staticmethod
    def invite_funcionario(token: str, payload: JsonPayload) -> dict:
        XanoClient._validate_employee_payload(payload)
        data = XanoClient._request(
            "POST",
            "/funcionarios/convites",
            token,
            payload,
        )
        return XanoClient._expect_employee_object(data)

    @staticmethod
    def update_funcionario(
        token: str,
        funcionario_id: int,
        payload: JsonPayload,
    ) -> dict:
        XanoClient._validate_employee_payload(payload)
        data = XanoClient._request(
            "PUT",
            f"/funcionarios/atualizar/{funcionario_id}",
            token,
            payload,
        )
        return XanoClient._expect_employee_object(data)

    @staticmethod
    def deactivate_funcionario(token: str, funcionario_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/funcionarios/desativar/{funcionario_id}",
            token,
        )
        return XanoClient._expect_employee_object(data)

    @staticmethod
    def activate_funcionario(token: str, funcionario_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/funcionarios/ativar/{funcionario_id}",
            token,
        )
        return XanoClient._expect_employee_object(data)

    @staticmethod
    def get_aluno(token: str, aluno_id: int) -> dict:
        data = XanoClient._request(
            "GET",
            f"/alunos/detalhes/{aluno_id}",
            token,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def create_aluno(token: str, payload: dict[str, str | None]) -> dict:
        data = XanoClient._request("POST", "/alunos", token, payload)
        return XanoClient._expect_object(data)

    @staticmethod
    def update_aluno(
        token: str,
        aluno_id: int,
        payload: dict[str, str | None],
    ) -> dict:
        data = XanoClient._request(
            "PUT",
            f"/alunos/atualizar/{aluno_id}",
            token,
            payload,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def deactivate_aluno(token: str, aluno_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/alunos/desativar/{aluno_id}",
            token,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def get_planos(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/planos", token)
        return XanoClient._expect_list(data, "planos")

    @staticmethod
    def get_plano(token: str, plano_id: int) -> dict:
        data = XanoClient._request(
            "GET",
            f"/planos/detalhes/{plano_id}",
            token,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def create_plano(token: str, payload: JsonPayload) -> dict:
        data = XanoClient._request("POST", "/planos", token, payload)
        return XanoClient._expect_object(data)

    @staticmethod
    def update_plano(
        token: str,
        plano_id: int,
        payload: JsonPayload,
    ) -> dict:
        data = XanoClient._request(
            "PUT",
            f"/planos/atualizar/{plano_id}",
            token,
            payload,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def deactivate_plano(token: str, plano_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/planos/descontinuar/{plano_id}",
            token,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def reactivate_plano(token: str, plano_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/planos/reativar/{plano_id}",
            token,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def get_matriculas(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/matriculas", token)
        return XanoClient._expect_list(data, "matrículas")

    @staticmethod
    def get_matricula(token: str, matricula_id: int) -> dict:
        data = XanoClient._request(
            "GET",
            f"/matriculas/detalhes/{matricula_id}",
            token,
        )
        return XanoClient._expect_object(data)

    @staticmethod
    def create_matricula(token: str, payload: JsonPayload) -> dict:
        data = XanoClient._request("POST", "/matriculas", token, payload)
        return XanoClient._expect_object(data)

    @staticmethod
    def get_mensalidades(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/mensalidades", token)
        return XanoClient._expect_records(
            data,
            "mensalidades",
            (
                "id",
                "matricula_id",
                "aluno_nome",
                "competencia",
                "data_vencimento",
                "valor",
                "situacao",
            ),
        )

    @staticmethod
    def get_pagamentos(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/pagamentos", token)
        return XanoClient._expect_records(
            data,
            "pagamentos",
            (
                "id",
                "mensalidade_id",
                "aluno_nome",
                "competencia",
                "valor",
                "forma_pagamento",
                "data_pagamento",
                "registrado_por",
                "situacao",
            ),
        )

    @staticmethod
    def create_pagamento(token: str, payload: JsonPayload) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {"mensalidade_id", "valor", "forma_pagamento"},
            "pagamento",
        )
        data = XanoClient._request("POST", "/pagamentos", token, payload)
        return XanoClient._expect_record(
            data,
            "pagamentos",
            (
                "id",
                "mensalidade_id",
                "valor",
                "forma_pagamento",
                "data_pagamento",
                "registrado_por",
                "situacao",
            ),
        )

    @staticmethod
    def correct_pagamento(
        token: str,
        pagamento_id: int,
        payload: JsonPayload,
    ) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {"tipo_correcao", "motivo"},
            "correção de pagamento",
        )
        data = XanoClient._request(
            "PATCH",
            f"/pagamentos/corrigir/{pagamento_id}",
            token,
            payload,
        )
        return XanoClient._expect_record(
            data,
            "pagamentos",
            (
                "id",
                "mensalidade_id",
                "situacao",
                "tipo_correcao",
                "motivo_correcao",
                "corrigido_em",
                "corrigido_por",
            ),
        )

    @staticmethod
    def get_checkin_alunos(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/checkins/alunos", token)
        return XanoClient._expect_records(
            data,
            "alunos disponíveis para check-in",
            ("id", "nome"),
        )

    @staticmethod
    def get_checkins(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/checkins", token)
        return XanoClient._expect_records(
            data,
            "check-ins",
            (
                "id",
                "aluno_id",
                "aluno_nome",
                "matricula_id",
                "data_hora",
                "registrado_por",
                "usuario_nome",
            ),
        )

    @staticmethod
    def create_checkin(token: str, payload: JsonPayload) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {"aluno_id"},
            "check-in",
        )
        data = XanoClient._request("POST", "/checkins", token, payload)
        return XanoClient._expect_record(
            data,
            "check-ins",
            (
                "id",
                "aluno_id",
                "matricula_id",
                "data_hora",
                "registrado_por",
            ),
        )

    @staticmethod
    def get_modalidades(token: str) -> list[dict]:
        data = XanoClient._request("GET", "/modalidades", token)
        return XanoClient._expect_records(
            data,
            "modalidades",
            ("id", "nome", "situacao"),
        )

    @staticmethod
    def create_modalidade(token: str, payload: JsonPayload) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {"nome", "descricao"},
            "modalidade",
        )
        data = XanoClient._request("POST", "/modalidades", token, payload)
        return XanoClient._expect_record(
            data,
            "modalidades",
            ("id", "nome", "situacao"),
        )

    @staticmethod
    def update_modalidade(
        token: str,
        modalidade_id: int,
        payload: JsonPayload,
    ) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {"nome", "descricao"},
            "modalidade",
        )
        data = XanoClient._request(
            "PUT",
            f"/modalidades/atualizar/{modalidade_id}",
            token,
            payload,
        )
        return XanoClient._expect_record(
            data,
            "modalidades",
            ("id", "nome", "situacao"),
        )

    @staticmethod
    def deactivate_modalidade(token: str, modalidade_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/modalidades/desativar/{modalidade_id}",
            token,
        )
        return XanoClient._expect_record(
            data,
            "modalidades",
            ("id", "nome", "situacao"),
        )

    @staticmethod
    def get_sessoes(
        token: str,
        data_inicio: str,
        data_fim: str,
    ) -> list[dict]:
        data = XanoClient._request(
            "GET",
            "/sessoes",
            token,
            params={"data_inicio": data_inicio, "data_fim": data_fim},
        )
        return XanoClient._expect_records(
            data,
            "sessões",
            (
                "id",
                "modalidade_id",
                "modalidade_nome",
                "instrutor_id",
                "instrutor_nome",
                "inicio",
                "termino",
                "capacidade",
                "ocupacao",
                "situacao",
            ),
        )

    @staticmethod
    def create_sessao(token: str, payload: JsonPayload) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {
                "modalidade_id",
                "instrutor_id",
                "inicio",
                "termino",
                "capacidade",
                "local",
            },
            "sessão",
        )
        data = XanoClient._request("POST", "/sessoes", token, payload)
        return XanoClient._expect_record(
            data,
            "sessões",
            (
                "id",
                "modalidade_id",
                "instrutor_id",
                "inicio",
                "termino",
                "capacidade",
                "situacao",
            ),
        )

    @staticmethod
    def update_sessao(
        token: str,
        sessao_id: int,
        payload: JsonPayload,
    ) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {
                "modalidade_id",
                "instrutor_id",
                "inicio",
                "termino",
                "capacidade",
                "local",
            },
            "sessão",
        )
        data = XanoClient._request(
            "PUT",
            f"/sessoes/atualizar/{sessao_id}",
            token,
            payload,
        )
        return XanoClient._expect_record(
            data,
            "sessões",
            (
                "id",
                "modalidade_id",
                "instrutor_id",
                "inicio",
                "termino",
                "capacidade",
                "situacao",
            ),
        )

    @staticmethod
    def cancel_sessao(token: str, sessao_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/sessoes/cancelar/{sessao_id}",
            token,
        )
        return XanoClient._expect_record(
            data,
            "sessões",
            ("id", "situacao"),
        )

    @staticmethod
    def get_reservas(token: str, sessao_id: int) -> dict:
        data = XanoClient._request(
            "GET",
            f"/reservas/{sessao_id}",
            token,
        )
        result = XanoClient._expect_record(
            data,
            "reservas",
            (
                "sessao_aula_id",
                "capacidade",
                "ocupacao",
                "vagas_disponiveis",
                "reservas",
            ),
        )
        expected_summary_fields = {
            "sessao_aula_id",
            "capacidade",
            "ocupacao",
            "vagas_disponiveis",
            "reservas",
        }
        if set(result) != expected_summary_fields:
            raise XanoAPIError(
                "A API retornou campos inesperados na consulta de reservas."
            )
        reservations = XanoClient._expect_records(
            result["reservas"],
            "reservas",
            (
                "id",
                "sessao_aula_id",
                "aluno_id",
                "aluno_nome",
                "situacao",
                "reservado_em",
            ),
        )
        expected_reservation_fields = {
            "id",
            "sessao_aula_id",
            "aluno_id",
            "aluno_nome",
            "situacao",
            "reservado_em",
        }
        if any(
            set(reservation) != expected_reservation_fields
            for reservation in reservations
        ):
            raise XanoAPIError(
                "A API retornou campos inesperados na lista de reservas."
            )
        result["reservas"] = reservations
        return result

    @staticmethod
    def create_reserva(token: str, payload: JsonPayload) -> dict:
        XanoClient._validate_payload_fields(
            payload,
            {"sessao_aula_id", "aluno_id"},
            "reserva",
        )
        data = XanoClient._request("POST", "/reservas", token, payload)
        return XanoClient._expect_record(
            data,
            "reservas",
            (
                "id",
                "sessao_aula_id",
                "aluno_id",
                "situacao",
                "reservado_em",
            ),
        )

    @staticmethod
    def cancel_reserva(token: str, reserva_id: int) -> dict:
        data = XanoClient._request(
            "PATCH",
            f"/reservas/cancelar/{reserva_id}",
            token,
        )
        return XanoClient._expect_record(
            data,
            "reservas",
            ("id", "sessao_aula_id", "aluno_id", "situacao"),
        )

    @staticmethod
    def set_reserva_resultado(
        token: str,
        reserva_id: int,
        resultado: str,
    ) -> dict:
        XanoClient._validate_payload_fields(
            {"resultado": resultado},
            {"resultado"},
            "resultado de reserva",
        )
        if resultado not in {"Presente", "Falta"}:
            raise XanoAPIError("O resultado da reserva é inválido.")
        data = XanoClient._request(
            "PATCH",
            f"/reservas/resultado/{reserva_id}",
            token,
            {"resultado": resultado},
        )
        return XanoClient._expect_record(
            data,
            "reservas",
            ("id", "sessao_aula_id", "aluno_id", "situacao"),
        )

    @staticmethod
    def get_relatorio_operacao(
        token: str,
        data_inicio: str,
        data_fim: str,
    ) -> dict:
        data = XanoClient._request(
            "GET",
            "/relatorios/operacao",
            token,
            params={"data_inicio": data_inicio, "data_fim": data_fim},
        )
        report = XanoClient._expect_record(
            data,
            "relatórios",
            (
                "data_inicio",
                "data_fim",
                "matriculas_ativas",
                "pagamentos_quantidade",
                "pagamentos_valor",
                "mensalidades_atrasadas_quantidade",
                "mensalidades_atrasadas_valor",
                "checkins_quantidade",
                "sessoes_quantidade",
                "capacidade_total",
                "reservas_nao_canceladas",
                "ocupacao_percentual",
            ),
        )
        expected_fields = {
            "data_inicio",
            "data_fim",
            "matriculas_ativas",
            "pagamentos_quantidade",
            "pagamentos_valor",
            "mensalidades_atrasadas_quantidade",
            "mensalidades_atrasadas_valor",
            "checkins_quantidade",
            "sessoes_quantidade",
            "capacidade_total",
            "reservas_nao_canceladas",
            "ocupacao_percentual",
        }
        if set(report) != expected_fields:
            raise XanoAPIError(
                "A API retornou campos inesperados no relatório."
            )
        if any(
            isinstance(report[field], bool)
            or not isinstance(report[field], (int, float))
            for field in expected_fields - {"data_inicio", "data_fim"}
        ):
            raise XanoAPIError(
                "A API retornou métricas inválidas no relatório."
            )
        return report
