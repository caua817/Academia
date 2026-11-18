from dataclasses import dataclass

import httpx

from academia.services.xano_client import API_BASE_URL


class AuthenticationAPIError(Exception):
    """Indica falha ou resposta inválida nos endpoints de autenticação."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class LoginResult:
    token: str | None
    requires_password_change: bool = False
    temporary_password_expired: bool = False


def validate_login_fields(email: str, password: str) -> str | None:
    if not email.strip() or not password.strip():
        return "Preencha o e-mail e a senha."
    return None


def validate_new_password(
    password: str,
    password_confirmation: str,
) -> str | None:
    has_ascii_letter = any(
        "A" <= char <= "Z" or "a" <= char <= "z" for char in password
    )
    has_ascii_digit = any("0" <= char <= "9" for char in password)
    if len(password) < 8 or not has_ascii_letter or not has_ascii_digit:
        return "A senha deve ter pelo menos 8 caracteres, uma letra e um número."
    if password != password_confirmation:
        return "A confirmação da senha não corresponde."
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
    def login(email: str, password: str) -> LoginResult:
        data = AuthenticationClient._post(
            "/auth/login",
            {"email": email.strip().lower(), "password": password},
        )

        requires_password_change = data.get("requires_password_change", False)
        temporary_password_expired = data.get(
            "temporary_password_expired",
            False,
        )
        if not isinstance(requires_password_change, bool) or not isinstance(
            temporary_password_expired,
            bool,
        ):
            raise AuthenticationAPIError(
                "O servidor retornou um desafio de autenticação inválido."
            )

        if requires_password_change:
            if data.get("authToken") or data.get("token"):
                raise AuthenticationAPIError(
                    "O servidor emitiu uma sessão durante a troca obrigatória."
                )
            return LoginResult(
                token=None,
                requires_password_change=True,
                temporary_password_expired=temporary_password_expired,
            )

        if temporary_password_expired:
            raise AuthenticationAPIError(
                "O servidor retornou um estado de senha temporária inválido."
            )

        token = data.get("authToken") or data.get("token")
        if not isinstance(token, str) or not token.strip():
            raise AuthenticationAPIError(
                "O servidor não retornou uma sessão válida."
            )
        return LoginResult(token=token)

    @staticmethod
    def change_temporary_password(
        email: str,
        temporary_password: str,
        password: str,
        password_confirmation: str,
    ) -> None:
        data = AuthenticationClient._post(
            "/auth/trocar-senha-temporaria",
            {
                "email": email.strip().lower(),
                "temporary_password": temporary_password,
                "password": password,
                "password_confirmation": password_confirmation,
            },
        )
        if data.get("success") is not True:
            raise AuthenticationAPIError(
                "A API não confirmou a troca da senha temporária."
            )

    @staticmethod
    def accept_employee_invitation(
        email: str,
        token: str,
        password: str,
        password_confirmation: str,
    ) -> None:
        if not email.strip() or not token.strip():
            raise AuthenticationAPIError(
                "O convite não contém as informações necessárias."
            )

        data = AuthenticationClient._post(
            "/funcionarios/convites/aceitar",
            {
                "email": email.strip().lower(),
                "token": token,
                "password": password,
                "password_confirmation": password_confirmation,
            },
        )
        if data.get("success") is not True:
            raise AuthenticationAPIError(
                "A API não confirmou a ativação do convite."
            )
