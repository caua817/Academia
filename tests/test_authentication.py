import json
import unittest
from unittest.mock import patch

import httpx

from academia.services.auth_client import (
    AuthenticationAPIError,
    AuthenticationClient,
    password_requirements,
    validate_login_fields,
    validate_signup_fields,
)

_HTTPX_CLIENT = httpx.Client


class AuthenticationClientTests(unittest.TestCase):
    def invoke(self, operation, response_handler):
        requests = []

        def handle(request):
            requests.append(request)
            return response_handler(request)

        client = _HTTPX_CLIENT(transport=httpx.MockTransport(handle))
        with patch(
            "academia.services.auth_client.httpx.Client",
            return_value=client,
        ):
            result = operation()
        return result, requests

    def test_login_sends_credentials_without_authorization_header(self):
        result, requests = self.invoke(
            lambda: AuthenticationClient.login(" User@Example.com ", "secret"),
            lambda request: httpx.Response(
                200,
                json={"authToken": "session-token", "user_id": 7},
                request=request,
            ),
        )

        self.assertEqual(result, "session-token")
        self.assertEqual(requests[0].method, "POST")
        self.assertEqual(requests[0].url.path, "/api:sGd5fzIy/auth/login")
        self.assertEqual(
            json.loads(requests[0].content),
            {"email": "user@example.com", "password": "secret"},
        )
        self.assertNotIn("Authorization", requests[0].headers)

    def test_login_accepts_legacy_token_field(self):
        result, _ = self.invoke(
            lambda: AuthenticationClient.login("user@example.com", "secret"),
            lambda request: httpx.Response(
                200,
                json={"token": "session-token"},
                request=request,
            ),
        )

        self.assertEqual(result, "session-token")

    def test_login_rejects_success_response_without_token(self):
        with self.assertRaises(AuthenticationAPIError):
            self.invoke(
                lambda: AuthenticationClient.login("user@example.com", "secret"),
                lambda request: httpx.Response(200, json={}, request=request),
            )

    def test_signup_sends_normalized_fields_without_authorization_header(self):
        result, requests = self.invoke(
            lambda: AuthenticationClient.signup(
                " Ana Lima ",
                " Ana@Example.com ",
                " secret ",
            ),
            lambda request: httpx.Response(
                200,
                json={"authToken": "ignored-by-signup", "user_id": 8},
                request=request,
            ),
        )

        self.assertEqual(result["user_id"], 8)
        self.assertEqual(requests[0].method, "POST")
        self.assertEqual(requests[0].url.path, "/api:sGd5fzIy/auth/signup")
        self.assertEqual(
            json.loads(requests[0].content),
            {
                "name": "Ana Lima",
                "email": "ana@example.com",
                "password": " secret ",
            },
        )
        self.assertNotIn("Authorization", requests[0].headers)

    def test_http_error_preserves_status_without_response_body(self):
        with self.assertRaises(AuthenticationAPIError) as context:
            self.invoke(
                lambda: AuthenticationClient.login("user@example.com", "secret"),
                lambda request: httpx.Response(
                    401,
                    json={"message": "private backend detail"},
                    request=request,
                ),
            )

        self.assertEqual(context.exception.status_code, 401)
        self.assertNotIn("private backend detail", str(context.exception))

    def test_connection_failure_is_reported(self):
        def fail_connection(request):
            raise httpx.ConnectError("offline", request=request)

        with self.assertRaises(AuthenticationAPIError) as context:
            self.invoke(
                lambda: AuthenticationClient.login("user@example.com", "secret"),
                fail_connection,
            )

        self.assertIsNone(context.exception.status_code)

    def test_invalid_json_shape_is_reported(self):
        with self.assertRaises(AuthenticationAPIError):
            self.invoke(
                lambda: AuthenticationClient.signup(
                    "Ana Lima",
                    "ana@example.com",
                    "secret",
                ),
                lambda request: httpx.Response(200, json=[], request=request),
            )


class AuthenticationValidationTests(unittest.TestCase):
    def test_login_requires_both_fields(self):
        self.assertIsNotNone(validate_login_fields("", "secret"))
        self.assertIsNotNone(validate_login_fields("user@example.com", " "))
        self.assertIsNone(
            validate_login_fields(" user@example.com ", " secret ")
        )

    def test_signup_requires_fields_and_valid_email(self):
        self.assertEqual(
            validate_signup_fields("", "user@example.com", "secret"),
            "Preencha todos os campos do formulário.",
        )
        self.assertEqual(
            validate_signup_fields("Ana", "not-an-email", "secret"),
            "Informe um e-mail válido.",
        )
        self.assertIsNone(
            validate_signup_fields(" Ana ", "ana@example.com ", "Senha123")
        )

    def test_password_requirements_accept_exact_minimum(self):
        self.assertEqual(
            password_requirements("Aaa12345"),
            {
                "minimum_length": True,
                "uppercase": True,
                "lowercase": True,
                "number": True,
            },
        )

    def test_password_requirements_report_each_missing_criterion(self):
        self.assertEqual(
            password_requirements("Aaa1234"),
            {
                "minimum_length": False,
                "uppercase": True,
                "lowercase": True,
                "number": True,
            },
        )
        self.assertFalse(password_requirements("aaaaaaa1")["uppercase"])
        self.assertFalse(password_requirements("AAAAAAA1")["lowercase"])
        self.assertFalse(password_requirements("Aaaaaaaa")["number"])

    def test_signup_rejects_password_outside_policy(self):
        self.assertEqual(
            validate_signup_fields("Ana", "ana@example.com", "Aaaaaaaa"),
            (
                "A senha deve ter pelo menos 8 caracteres, uma letra maiúscula, "
                "uma letra minúscula e um número."
            ),
        )


if __name__ == "__main__":
    unittest.main()
