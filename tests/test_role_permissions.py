import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from academia.access_control import (
    AdminAccessState,
    ROLE_ROUTE_ACCESS,
    require_route_access,
)
from academia.login import LANDING_ROUTE_BY_ROLE, LoginState
from academia.services.auth_client import LoginResult
from academia.services.xano_client import XanoAPIError


class AccessHarness:
    def __init__(self, token: str = "session-token"):
        self.login_state = SimpleNamespace(auth_token=token)
        self.access_state = SimpleNamespace(
            is_admin=False,
            is_receptionist=False,
            is_instructor=False,
            user_role="",
            is_verifying=False,
            error_message="",
            authorized_route="",
        )

    async def get_state(self, state_type):
        if state_type is LoginState:
            return self.login_state
        if state_type is AdminAccessState:
            return self.access_state
        raise AssertionError(f"Unexpected state requested: {state_type}")


class RolePermissionTests(unittest.IsolatedAsyncioTestCase):
    async def authorize(self, role: str, route: str):
        state = AccessHarness()
        with patch(
            "academia.access_control.XanoClient.get_current_user",
            return_value={"role": role},
        ):
            token, redirect = await require_route_access(state, route)
        return state, token, redirect

    async def test_admin_can_access_every_protected_route(self):
        for route in ROLE_ROUTE_ACCESS["admin"]:
            with self.subTest(route=route):
                state, token, redirect = await self.authorize("admin", route)
                self.assertEqual(token, "session-token")
                self.assertFalse(redirect)
                self.assertEqual(state.access_state.authorized_route, route)
                self.assertTrue(state.access_state.is_admin)

    async def test_receptionist_has_only_operational_access(self):
        allowed = {"alunos", "matriculas", "financeiro", "checkins"}
        self.assertEqual(ROLE_ROUTE_ACCESS["recepcionista"], allowed)

        for route in allowed:
            with self.subTest(route=route):
                state, token, redirect = await self.authorize(
                    "recepcionista",
                    route,
                )
                self.assertEqual(token, "session-token")
                self.assertFalse(redirect)
                self.assertTrue(state.access_state.is_receptionist)

        state, token, redirect = await self.authorize(
            "recepcionista",
            "funcionarios",
        )
        self.assertEqual(token, "")
        self.assertFalse(redirect)
        self.assertTrue(state.access_state.error_message)
        self.assertFalse(state.access_state.authorized_route)

    async def test_instructor_can_only_access_students_and_attendance(self):
        allowed = {"alunos", "checkins"}
        self.assertEqual(ROLE_ROUTE_ACCESS["instrutor"], allowed)

        for route in allowed:
            with self.subTest(route=route):
                state, token, redirect = await self.authorize("instrutor", route)
                self.assertEqual(token, "session-token")
                self.assertFalse(redirect)
                self.assertTrue(state.access_state.is_instructor)

    async def test_retired_training_routes_are_denied_for_all_staff(self):
        for role in ("admin", "recepcionista", "instrutor"):
            for route in ("exercicios", "fichas", "avaliacoes"):
                with self.subTest(role=role, route=route):
                    state, token, redirect = await self.authorize(role, route)
                    self.assertEqual(token, "")
                    self.assertFalse(redirect)
                    self.assertFalse(state.access_state.authorized_route)

        for route in ("matriculas", "financeiro", "relatorios"):
            with self.subTest(route=route):
                state, token, redirect = await self.authorize("instrutor", route)
                self.assertEqual(token, "")
                self.assertFalse(redirect)
                self.assertFalse(state.access_state.authorized_route)

    async def test_unknown_route_and_role_are_denied_by_default(self):
        state, token, redirect = await self.authorize("admin", "unlisted")
        self.assertEqual(token, "")
        self.assertFalse(redirect)
        self.assertFalse(state.access_state.authorized_route)

        state, token, redirect = await self.authorize("member", "alunos")
        self.assertEqual(token, "")
        self.assertFalse(redirect)
        self.assertFalse(state.access_state.authorized_route)

    async def test_profile_verification_failure_never_grants_access(self):
        state = AccessHarness()
        with patch(
            "academia.access_control.XanoClient.get_current_user",
            side_effect=XanoAPIError("offline"),
        ):
            token, redirect = await require_route_access(state, "alunos")

        self.assertEqual(token, "")
        self.assertFalse(redirect)
        self.assertFalse(state.access_state.authorized_route)
        self.assertTrue(state.access_state.error_message)

    async def test_rate_limit_preserves_session_and_requests_wait(self):
        state = AccessHarness()
        with patch(
            "academia.access_control.XanoClient.get_current_user",
            side_effect=XanoAPIError("too many requests", 429),
        ):
            token, redirect = await require_route_access(state, "financeiro")

        self.assertEqual(token, "")
        self.assertFalse(redirect)
        self.assertEqual(state.login_state.auth_token, "session-token")
        self.assertIn("Aguarde", state.access_state.error_message)
        self.assertFalse(state.access_state.authorized_route)

    async def test_expired_session_is_cleared_without_retry(self):
        state = AccessHarness()
        with (
            patch(
                "academia.access_control.XanoClient.get_current_user",
                side_effect=XanoAPIError("expired", 401),
            ) as get_current_user,
            patch(
                "academia.session_state.clear_app_session",
                new_callable=AsyncMock,
            ) as clear_session,
        ):
            token, redirect = await require_route_access(state, "alunos")

        self.assertEqual(token, "")
        self.assertTrue(redirect)
        get_current_user.assert_called_once_with("session-token")
        clear_session.assert_awaited_once_with(state)

    async def test_missing_session_clears_session_and_requests_login(self):
        state = AccessHarness(token="")
        with patch(
            "academia.session_state.clear_app_session",
            new_callable=AsyncMock,
        ) as clear_session:
            token, redirect = await require_route_access(state, "alunos")

        self.assertEqual(token, "")
        self.assertTrue(redirect)
        clear_session.assert_awaited_once_with(state)


class LoginLandingRouteTests(unittest.IsolatedAsyncioTestCase):
    def test_staff_profiles_have_allowed_landing_pages(self):
        self.assertEqual(LANDING_ROUTE_BY_ROLE["admin"], "/")
        self.assertEqual(LANDING_ROUTE_BY_ROLE["recepcionista"], "/alunos")
        self.assertEqual(LANDING_ROUTE_BY_ROLE["instrutor"], "/alunos")
        self.assertNotIn("member", LANDING_ROUTE_BY_ROLE)
        self.assertFalse(hasattr(LoginState, "password"))

    async def test_login_verifies_profile_before_storing_session(self):
        state = SimpleNamespace(
            email=" staff@example.com ",
            password="secret",
            password_visible=True,
            auth_token="previous-token",
            error_message="",
            success_message="",
            requires_password_change=False,
            is_loading=False,
        )
        event = LoginState.__dict__["handle_login"].fn

        with (
            patch(
                "academia.login.AuthenticationClient.login",
                return_value=LoginResult(token="new-token"),
            ),
            patch(
                "academia.login.XanoClient.get_current_user",
                return_value={"role": "recepcionista"},
            ),
            patch(
                "academia.login.rx.redirect",
                side_effect=lambda route: f"redirect:{route}",
            ) as redirect,
        ):
            results = [
                result
                async for result in event(state, {"password": "secret"})
            ]

        self.assertIn("redirect:/alunos", results)
        redirect.assert_called_once_with("/alunos")
        self.assertEqual(state.auth_token, "new-token")
        self.assertEqual(state.email, "staff@example.com")
        self.assertFalse(state.password_visible)

    async def test_login_does_not_store_session_when_profile_check_fails(self):
        state = SimpleNamespace(
            email="staff@example.com",
            password="secret",
            password_visible=False,
            auth_token="previous-token",
            error_message="",
            success_message="",
            requires_password_change=False,
            is_loading=False,
        )
        event = LoginState.__dict__["handle_login"].fn

        with (
            patch(
                "academia.login.AuthenticationClient.login",
                return_value=LoginResult(token="new-token"),
            ),
            patch(
                "academia.login.XanoClient.get_current_user",
                side_effect=XanoAPIError("offline"),
            ),
            patch("academia.login.rx.redirect") as redirect,
        ):
            [
                result
                async for result in event(state, {"password": "secret"})
            ]

        self.assertEqual(state.auth_token, "")
        self.assertTrue(state.error_message)
        redirect.assert_not_called()

    async def test_login_profile_rate_limit_does_not_store_token(self):
        state = SimpleNamespace(
            email="staff@example.com",
            password="",
            password_visible=False,
            auth_token="previous-token",
            error_message="",
            success_message="",
            requires_password_change=False,
            is_loading=False,
        )
        event = LoginState.__dict__["handle_login"].fn

        with (
            patch(
                "academia.login.AuthenticationClient.login",
                return_value=LoginResult(token="new-token"),
            ),
            patch(
                "academia.login.XanoClient.get_current_user",
                side_effect=XanoAPIError("too many requests", 429),
            ),
            patch("academia.login.rx.redirect") as redirect,
        ):
            [
                result
                async for result in event(state, {"password": "secret"})
            ]

        self.assertEqual(state.auth_token, "")
        self.assertIn("Aguarde", state.error_message)
        redirect.assert_not_called()

    async def test_temporary_login_does_not_issue_or_verify_a_session(self):
        state = SimpleNamespace(
            email=" Staff@Example.com ",
            password="temporary-password",
            password_visible=True,
            auth_token="old-token",
            error_message="",
            success_message="",
            requires_password_change=False,
            is_loading=False,
        )
        event = LoginState.__dict__["handle_login"].fn

        with (
            patch(
                "academia.login.AuthenticationClient.login",
                return_value=LoginResult(
                    token=None,
                    requires_password_change=True,
                ),
            ),
            patch(
                "academia.login.XanoClient.get_current_user"
            ) as get_current_user,
            patch("academia.login.rx.redirect") as redirect,
        ):
            [
                result
                async for result in event(
                    state,
                    {"password": "temporary-password"},
                )
            ]

        get_current_user.assert_not_called()
        redirect.assert_not_called()
        self.assertEqual(state.auth_token, "")
        self.assertEqual(state.email, "staff@example.com")
        self.assertTrue(state.requires_password_change)

    async def test_expired_temporary_login_shows_reissue_message(self):
        state = SimpleNamespace(
            email="staff@example.com",
            password="temporary-password",
            password_visible=False,
            auth_token="",
            error_message="",
            success_message="",
            requires_password_change=False,
            is_loading=False,
        )
        event = LoginState.__dict__["handle_login"].fn

        with patch(
            "academia.login.AuthenticationClient.login",
            return_value=LoginResult(
                token=None,
                requires_password_change=True,
                temporary_password_expired=True,
            ),
        ), patch(
            "academia.login.XanoClient.get_current_user"
        ) as get_current_user:
            [
                result
                async for result in event(
                    state,
                    {"password": "temporary-password"},
                )
            ]

        get_current_user.assert_not_called()
        self.assertFalse(state.requires_password_change)
        self.assertIn("expirou", state.error_message)
        self.assertEqual(state.auth_token, "")


class TemporaryPasswordStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_temporary_password_change_requires_a_new_login(self):
        state = SimpleNamespace(
            requires_password_change=True,
            email="staff@example.com",
            auth_token="",
            password="",
            password_visible=False,
            error_message="",
            success_message="",
            is_loading=False,
        )
        event = LoginState.__dict__["change_temporary_password"].fn
        form_data = {
            "temporary_password": "Temporary1",
            "password": "NewPassword1",
            "password_confirmation": "NewPassword1",
        }

        with patch(
            "academia.login.AuthenticationClient.change_temporary_password"
        ) as change_password:
            results = [
                result async for result in event(state, form_data)
            ]

        change_password.assert_called_once_with(
            "staff@example.com",
            "Temporary1",
            "NewPassword1",
            "NewPassword1",
        )
        self.assertFalse(state.requires_password_change)
        self.assertEqual(state.auth_token, "")
        self.assertIn("Faça login novamente", state.success_message)
        self.assertEqual(len(results), 4)

    async def test_temporary_password_change_rejects_weak_password(self):
        state = SimpleNamespace(
            requires_password_change=True,
            email="staff@example.com",
            auth_token="",
            password="",
            password_visible=False,
            error_message="",
            success_message="",
            is_loading=False,
        )
        event = LoginState.__dict__["change_temporary_password"].fn

        with patch(
            "academia.login.AuthenticationClient.change_temporary_password"
        ) as change_password:
            results = [
                result
                async for result in event(
                    state,
                    {
                        "temporary_password": "Temporary1",
                        "password": "weak",
                        "password_confirmation": "weak",
                    },
                )
            ]

        change_password.assert_not_called()
        self.assertIn("8 caracteres", state.error_message)
        self.assertEqual(len(results), 4)


if __name__ == "__main__":
    unittest.main()
