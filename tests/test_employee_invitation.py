import unittest
from unittest.mock import patch

import reflex as rx

from academia.ativacao_funcionario import (
    EmployeeInvitationActivationState,
    parse_invitation_fragment,
    validate_invitation_password,
)
from academia.services.auth_client import AuthenticationAPIError


class InvitationFragmentTests(unittest.TestCase):
    def test_parses_email_and_token_and_normalizes_email(self):
        self.assertEqual(
            parse_invitation_fragment(
                "email=User%40Example.com&token=one-time-token"
            ),
            ("user@example.com", "one-time-token"),
        )

    def test_rejects_missing_duplicate_or_malformed_fields(self):
        for fragment in (
            "",
            "email=user%40example.com",
            "email=user%40example.com&token=",
            "email=user%40example.com&email=other%40example.com&token=x",
            "email=user%40example.com&token=x&extra=y",
            "email=user%40example.com&token=%",
            "email=user%FFexample.com&token=x",
        ):
            with self.subTest(fragment=fragment):
                self.assertIsNone(parse_invitation_fragment(fragment))


class InvitationPasswordValidationTests(unittest.TestCase):
    def test_requires_existing_password_policy_and_matching_confirmation(self):
        self.assertIsNotNone(validate_invitation_password("short1", "short1"))
        self.assertIsNotNone(validate_invitation_password("password", "password"))
        self.assertIsNotNone(validate_invitation_password("ççççççç1", "ççççççç1"))
        self.assertIsNotNone(validate_invitation_password("aaaaaaaa١", "aaaaaaaa١"))
        self.assertIsNotNone(validate_invitation_password("Password1", "Password2"))
        self.assertIsNone(
            validate_invitation_password("Password1", "Password1")
        )


class InvitationActivationStateTests(unittest.TestCase):
    def setUp(self):
        self.state = EmployeeInvitationActivationState()
        self.state._email = "user@example.com"
        self.state._token = "one-time-token"
        self.state.has_valid_invitation = True

    def test_token_is_only_stored_in_backend_only_state(self):
        all_fields = set(EmployeeInvitationActivationState.get_fields())
        public_vars = {field for field in all_fields if not field.startswith("_")}
        self.assertIn("_token", all_fields)
        self.assertIn("_email", all_fields)
        self.assertNotIn("_token", public_vars)
        self.assertNotIn("_email", public_vars)
        self.assertNotIn("password", public_vars)
        self.assertNotIn("password_confirmation", public_vars)

    def test_invalid_password_does_not_call_api(self):
        with patch(
            "academia.ativacao_funcionario.AuthenticationClient.accept_employee_invitation"
        ) as accept:
            events = list(
                self.state.activate(
                    {"password": "short", "password_confirmation": "short"}
                )
            )

        accept.assert_not_called()
        self.assertIn("8 caracteres", self.state.error_message)
        self.assertEqual(self.state._token, "one-time-token")
        self.assertEqual(len(events), 3)

    def test_invalid_invitation_clears_token_and_password_attempt_data(self):
        with patch(
            "academia.ativacao_funcionario.AuthenticationClient.accept_employee_invitation",
            side_effect=AuthenticationAPIError("rejected", 404),
        ) as accept:
            list(
                self.state.activate(
                    {
                        "password": "Password1",
                        "password_confirmation": "Password1",
                    }
                )
            )

        accept.assert_called_once_with(
            "user@example.com",
            "one-time-token",
            "Password1",
            "Password1",
        )
        self.assertEqual(self.state._token, "")
        self.assertEqual(self.state._email, "")
        self.assertIn("convite", self.state.error_message.lower())
        self.assertFalse(self.state.is_loading)

    def test_transient_api_error_preserves_invitation_and_allows_retry(self):
        with patch(
            "academia.ativacao_funcionario.AuthenticationClient.accept_employee_invitation",
            side_effect=AuthenticationAPIError("unavailable"),
        ) as accept:
            list(
                self.state.activate(
                    {
                        "password": "Password1",
                        "password_confirmation": "Password1",
                    }
                )
            )

        accept.assert_called_once()
        self.assertEqual(self.state._token, "one-time-token")
        self.assertEqual(self.state._email, "user@example.com")
        self.assertTrue(self.state.has_valid_invitation)
        self.assertIn("Tente novamente", self.state.error_message)
        self.assertFalse(self.state.is_loading)

    def test_api_validation_error_preserves_invitation_for_retry(self):
        with patch(
            "academia.ativacao_funcionario.AuthenticationClient.accept_employee_invitation",
            side_effect=AuthenticationAPIError("invalid input", 400),
        ):
            list(
                self.state.activate(
                    {
                        "password": "Password1",
                        "password_confirmation": "Password1",
                    }
                )
            )

        self.assertEqual(self.state._token, "one-time-token")
        self.assertTrue(self.state.has_valid_invitation)
        self.assertIn("Tente novamente", self.state.error_message)

    def test_success_consumes_private_invitation_and_redirects(self):
        with patch(
            "academia.ativacao_funcionario.AuthenticationClient.accept_employee_invitation"
        ) as accept:
            events = list(
                self.state.activate(
                    {
                        "password": "Password1",
                        "password_confirmation": "Password1",
                    }
                )
            )

        accept.assert_called_once()
        self.assertTrue(self.state._activation_succeeded)
        self.assertEqual(self.state._token, "")
        self.assertEqual(self.state._email, "")
        self.assertFalse(self.state.has_valid_invitation)
        self.assertIsInstance(events[-1], type(rx.redirect("/login")))
        self.assertIn('"/login"', repr(events[-1].args))


if __name__ == "__main__":
    unittest.main()
