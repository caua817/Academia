import threading
import unittest
from unittest.mock import patch

import httpx

from academia.services.xano_client import XanoAPIError, XanoClient

_HTTPX_CLIENT = httpx.Client


class ProfileVerificationRetryTests(unittest.TestCase):
    def invoke_with_responses(self, operation, responses):
        requests = []
        remaining = iter(responses)

        def handle(request):
            requests.append(request)
            response = next(remaining)
            if isinstance(response, Exception):
                raise response
            return httpx.Response(
                response[0],
                json=response[1],
                request=request,
            )

        with (
            patch(
                "academia.services.xano_client.httpx.Client",
                side_effect=lambda **kwargs: _HTTPX_CLIENT(
                    transport=httpx.MockTransport(handle),
                    **kwargs,
                ),
            ),
            patch("academia.services.xano_client.time.sleep"),
        ):
            result = operation()
        return result, requests

    def test_profile_retries_once_after_server_error(self):
        identity, requests = self.invoke_with_responses(
            lambda: XanoClient.get_current_user_with_retry("session-token"),
            [(503, {"message": "unavailable"}), (200, {"role": "admin"})],
        )

        self.assertEqual(identity, {"role": "admin"})
        self.assertEqual(len(requests), 2)
        self.assertTrue(all(request.method == "GET" for request in requests))
        self.assertTrue(all(request.url.path.endswith("/auth/me") for request in requests))

    def test_profile_retries_once_after_connection_error(self):
        request = httpx.Request("GET", "https://example.test/auth/me")
        identity, requests = self.invoke_with_responses(
            lambda: XanoClient.get_current_user_with_retry("session-token"),
            [
                httpx.ConnectError("offline", request=request),
                (200, {"role": "admin"}),
            ],
        )

        self.assertEqual(identity, {"role": "admin"})
        self.assertEqual(len(requests), 2)

    def test_profile_does_not_retry_auth_or_rate_limit_responses(self):
        for status_code in (401, 403, 429):
            with self.subTest(status_code=status_code):
                with self.assertRaises(XanoAPIError) as context:
                    self.invoke_with_responses(
                        lambda: XanoClient.get_current_user_with_retry(
                            "session-token"
                        ),
                        [(status_code, {"message": "rejected"})],
                    )

                self.assertEqual(context.exception.status_code, status_code)

    def test_profile_does_not_retry_invalid_response(self):
        requests = []

        def handle(request):
            requests.append(request)
            return httpx.Response(
                200,
                content=b"not-json",
                request=request,
            )

        client = _HTTPX_CLIENT(transport=httpx.MockTransport(handle))
        with patch(
            "academia.services.xano_client.httpx.Client",
            return_value=client,
        ):
            with self.assertRaises(XanoAPIError):
                XanoClient.get_current_user_with_retry("session-token")

        self.assertEqual(len(requests), 1)

    def test_profile_stops_after_second_transient_failure(self):
        with self.assertRaises(XanoAPIError) as context:
            self.invoke_with_responses(
                lambda: XanoClient.get_current_user_with_retry("session-token"),
                [(503, {}), (503, {})],
            )

        self.assertEqual(context.exception.status_code, 503)

    def test_ordinary_requests_are_not_retried(self):
        requests = []

        def handle(request):
            requests.append(request)
            return httpx.Response(503, json={}, request=request)

        with patch(
            "academia.services.xano_client.httpx.Client",
            side_effect=lambda **kwargs: _HTTPX_CLIENT(
                transport=httpx.MockTransport(handle),
                **kwargs,
            ),
        ):
            with self.assertRaises(XanoAPIError):
                XanoClient._request(
                    "POST",
                    "/alunos",
                    "session-token",
                    payload={"nome": "Aluno"},
                )
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, "POST")

    def test_server_errors_are_marked_retryable_but_invalid_json_is_not(self):
        with self.assertRaises(XanoAPIError) as server_error:
            self.invoke_with_responses(
                lambda: XanoClient.get_current_user("session-token"),
                [(503, {})],
            )
        self.assertTrue(server_error.exception.retryable)

        requests = []

        def invalid_json(request):
            requests.append(request)
            return httpx.Response(200, content=b"invalid", request=request)

        client = _HTTPX_CLIENT(transport=httpx.MockTransport(invalid_json))
        with patch(
            "academia.services.xano_client.httpx.Client",
            return_value=client,
        ):
            with self.assertRaises(XanoAPIError) as response_error:
                XanoClient.get_current_user("session-token")
        self.assertFalse(response_error.exception.retryable)


class ProfileVerificationResponsivenessTests(unittest.IsolatedAsyncioTestCase):
    async def test_profile_request_runs_outside_event_loop_thread(self):
        import asyncio

        from academia.access_control import (
            AdminAccessState,
            require_route_access,
        )
        from academia.login import LoginState

        class StateHarness:
            def __init__(self):
                self.login = type("Login", (), {"auth_token": "session-token"})()
                self.access = type(
                    "Access",
                    (),
                    {
                        "is_admin": False,
                        "is_receptionist": False,
                        "is_instructor": False,
                        "user_role": "",
                        "is_verifying": False,
                        "error_message": "",
                        "authorized_route": "",
                    },
                )()

            async def get_state(self, state_type):
                if state_type is LoginState:
                    return self.login
                if state_type is AdminAccessState:
                    return self.access
                raise AssertionError(f"Unexpected state: {state_type}")

        event_loop_thread = threading.get_ident()

        def get_identity(token):
            self.assertEqual(token, "session-token")
            self.assertNotEqual(threading.get_ident(), event_loop_thread)
            return {"role": "recepcionista"}

        with patch(
            "academia.access_control.XanoClient.get_current_user",
            side_effect=get_identity,
        ):
            token, redirect = await require_route_access(
                StateHarness(),
                "financeiro",
            )

        self.assertEqual(token, "session-token")
        self.assertFalse(redirect)

    async def test_login_http_requests_run_outside_event_loop_thread(self):
        from types import SimpleNamespace

        from academia.login import LoginState
        from academia.services.auth_client import LoginResult

        event_loop_thread = threading.get_ident()
        state = SimpleNamespace(
            email="staff@example.com",
            password_visible=False,
            auth_token="",
            error_message="",
            success_message="",
            requires_password_change=False,
            is_loading=False,
        )

        def login(email, password):
            self.assertNotEqual(threading.get_ident(), event_loop_thread)
            return LoginResult(token="session-token")

        def get_identity(token):
            self.assertEqual(token, "session-token")
            self.assertNotEqual(threading.get_ident(), event_loop_thread)
            return {"role": "recepcionista"}

        with (
            patch(
                "academia.login.AuthenticationClient.login",
                side_effect=login,
            ),
            patch(
                "academia.login.XanoClient.get_current_user",
                side_effect=get_identity,
            ),
            patch(
                "academia.login.rx.redirect",
                side_effect=lambda route: route,
            ),
        ):
            [
                result
                async for result in LoginState.__dict__["handle_login"].fn(
                    state,
                    {"password": "valid-password"},
                )
            ]

        self.assertEqual(state.auth_token, "session-token")
