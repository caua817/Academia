import json
import unittest
from unittest.mock import patch

import httpx

from academia.services.auth_client import (
    AuthenticationAPIError,
    AuthenticationClient,
    validate_login_fields,
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

if __name__ == "__main__":
    unittest.main()
