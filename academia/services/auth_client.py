import httpx

from academia.services.xano_client import API_BASE_URL


class AuthenticationAPIError(Exception):
    """Indica falha ou resposta inválida nos endpoints de autenticação."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def validate_login_fields(email: str, password: str) -> str | None:
    if not email.strip() or not password.strip():
        return "Preencha o e-mail e a senha."
    return None


class AuthenticationClient:
    @staticmethod
    def _post(path: str, payload: dict[str, str]) -> dict:
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{API_BASE_URL.rstrip('/')}{path}",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as error:
            raise AuthenticationAPIError(
                "A API de autenticação rejeitou a solicitação.",
                error.response.status_code,
            ) from error
        except httpx.RequestError as error:
            raise AuthenticationAPIError(
                "Não foi possível conectar à API de autenticação."
            ) from error
        except ValueError as error:
            raise AuthenticationAPIError(
                "A API de autenticação retornou uma resposta inválida."
            ) from error

        if not isinstance(data, dict):
            raise AuthenticationAPIError(
                "A API de autenticação retornou uma resposta inválida."
            )
        return data

    @staticmethod
    def login(email: str, password: str) -> str:
        data = AuthenticationClient._post(
            "/auth/login",
            {"email": email.strip().lower(), "password": password},
        )
        token = data.get("authToken") or data.get("token")
        if not isinstance(token, str) or not token.strip():
            raise AuthenticationAPIError(
                "O servidor não retornou uma sessão válida."
            )
        return token
