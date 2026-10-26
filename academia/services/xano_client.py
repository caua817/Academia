import os
from collections.abc import Mapping

import httpx

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://x8ki-letl-twmt.n7.xano.io/api:sGd5fzIy",
)
JsonPayload = Mapping[str, str | int | float | None]


class XanoAPIError(Exception):
    """Indica falha de comunicação ou resposta inválida da API Xano."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class XanoClient:
    @staticmethod
    def _request(
        method: str,
        path: str,
        token: str,
        payload: JsonPayload | None = None,
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
    def get_alunos(token: str) -> list[dict]:
        """Busca os alunos e sinaliza explicitamente falhas da API."""
        data = XanoClient._request("GET", "/alunos", token)
        return XanoClient._expect_list(data, "alunos")

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
