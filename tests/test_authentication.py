import json
import unittest
from unittest.mock import patch

import httpx

from academia.services.auth_client import (
    AuthenticationAPIError,
    AuthenticationClient,
    LoginResult,
    validate_login_fields,
    validate_new_password,
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

        self.assertEqual(result, LoginResult(token="session-token"))
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

        self.assertEqual(result, LoginResult(token="session-token"))

    def test_login_returns_password_change_challenge_without_session(self):
        result, requests = self.invoke(
            lambda: AuthenticationClient.login("user@example.com", "temporary"),
            lambda request: httpx.Response(
                200,
                json={
                    "requires_password_change": True,
                    "temporary_password_expired": False,
                },
                request=request,
            ),
        )

        self.assertEqual(
            result,
            LoginResult(
                token=None,
                requires_password_change=True,
                temporary_password_expired=False,
            ),
        )
        self.assertNotIn("Authorization", requests[0].headers)

    def test_login_rejects_session_in_password_change_challenge(self):
        with self.assertRaises(AuthenticationAPIError):
            self.invoke(
                lambda: AuthenticationClient.login(
                    "user@example.com",
                    "temporary",
                ),
                lambda request: httpx.Response(
                    200,
                    json={
                        "authToken": "must-not-be-issued",
                        "requires_password_change": True,
                    },
                    request=request,
                ),
            )

    def test_accept_invitation_sends_public_activation_payload(self):
        result, requests = self.invoke(
            lambda: AuthenticationClient.accept_employee_invitation(
                " User@Example.com ",
                "invite-token",
                "Password1",
                "Password1",
            ),
            lambda request: httpx.Response(
                200,
                json={"success": True},
                request=request,
            ),
        )

        self.assertIsNone(result)
        self.assertEqual(requests[0].method, "POST")
        self.assertEqual(
            requests[0].url.path,
            "/api:sGd5fzIy/funcionarios/convites/aceitar",
        )
        self.assertEqual(
            json.loads(requests[0].content),
            {
                "email": "user@example.com",
                "token": "invite-token",
                "password": "Password1",
                "password_confirmation": "Password1",
            },
        )
        self.assertNotIn("Authorization", requests[0].headers)

    def test_accept_invitation_rejects_unexpected_success_response(self):
        with self.assertRaises(AuthenticationAPIError):
            self.invoke(
                lambda: AuthenticationClient.accept_employee_invitation(
                    "user@example.com",
                    "invite-token",
                    "Password1",
                    "Password1",
                ),
                lambda request: httpx.Response(
                    200,
                    json={"success": False},
                    request=request,
                ),
            )

    def test_temporary_password_change_sends_only_required_fields(self):
        result, requests = self.invoke(
            lambda: AuthenticationClient.change_temporary_password(
                " User@Example.com ",
                "Temporary1",
                "NewPassword1",
                "NewPassword1",
            ),
            lambda request: httpx.Response(
                200,
                json={"success": True},
                request=request,
            ),
        )

        self.assertIsNone(result)
        self.assertEqual(requests[0].method, "POST")
        self.assertEqual(
            requests[0].url.path,
            "/api:sGd5fzIy/auth/trocar-senha-temporaria",
        )
        self.assertEqual(
            json.loads(requests[0].content),
            {
                "email": "user@example.com",
                "temporary_password": "Temporary1",
                "password": "NewPassword1",
                "password_confirmation": "NewPassword1",
            },
        )
        self.assertNotIn("Authorization", requests[0].headers)

    def test_login_rejects_success_response_without_token(self):
        with self.assertRaises(AuthenticationAPIError):
            self.invoke(
                lambda: AuthenticationClient.login("user@example.com", "secret"),
                lambda request: httpx.Response(200, json={}, request=request),
            )

    def test_public_signup_client_is_not_available(self):
        self.assertFalse(hasattr(AuthenticationClient, "signup"))

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

class AuthenticationValidationTests(unittest.TestCase):
    def test_login_requires_both_fields(self):
        self.assertIsNotNone(validate_login_fields("", "secret"))
        self.assertIsNotNone(validate_login_fields("user@example.com", " "))
        self.assertIsNone(
            validate_login_fields(" user@example.com ", " secret ")
        )

    def test_new_password_requires_eight_chars_letter_digit_and_match(self):
        self.assertIsNotNone(validate_new_password("short1", "short1"))
        self.assertIsNotNone(validate_new_password("Password", "Password"))
        self.assertIsNotNone(validate_new_password("12345678", "12345678"))
        self.assertIsNotNone(
            validate_new_password("Password1", "Password2")
        )
        self.assertIsNone(
            validate_new_password("Password1", "Password1")
        )

if __name__ == "__main__":
    unittest.main()
