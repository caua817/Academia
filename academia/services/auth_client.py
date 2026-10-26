import re

import httpx

from academia.services.xano_client import API_BASE_URL


class AuthenticationAPIError(Exception):
    """Indica falha ou resposta inválida nos endpoints públicos de autenticação."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 8


def password_requirements(password: str) -> dict[str, bool]:
    return {
        "minimum_length": len(password) >= PASSWORD_MIN_LENGTH,
        "uppercase": any("A" <= character <= "Z" for character in password),
        "lowercase": any("a" <= character <= "z" for character in password),
        "number": any("0" <= character <= "9" for character in password),
    }


def validate_login_fields(email: str, password: str) -> str | None:
    if not email.strip() or not password.strip():
        return "Preencha o e-mail e a senha."
    return None


def validate_signup_fields(name: str, email: str, password: str) -> str | None:
    if not name.strip() or not email.strip() or not password.strip():
        return "Preencha todos os campos do formulário."
    if not _EMAIL_PATTERN.fullmatch(email.strip()):
        return "Informe um e-mail válido."
    if not all(password_requirements(password).values()):
        return (
            "A senha deve ter pelo menos 8 caracteres, uma letra maiúscula, "
            "uma letra minúscula e um número."
        )
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

    @staticmethod
    def signup(name: str, email: str, password: str) -> dict:
        return AuthenticationClient._post(
            "/auth/signup",
            {
                "name": name.strip(),
                "email": email.strip().lower(),
                "password": password,
            },
        )
