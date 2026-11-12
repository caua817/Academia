import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from academia.access_control import require_admin
from academia.login import LoginState
from academia.operacao import (
    OperacaoState,
    active_student_options,
    to_api_timestamp,
    validate_date_range,
    validate_modalidade_fields,
    validate_sessao_fields,
)
from academia.services.xano_client import XanoAPIError


class OperationValidationTests(unittest.TestCase):
    def test_date_range_validation(self):
        self.assertIsNone(validate_date_range("2026-11-01", "2026-11-30"))
        self.assertIsNotNone(validate_date_range("2026-11-30", "2026-11-01"))
        self.assertIsNotNone(validate_date_range("not-a-date", "2026-11-01"))

    def test_modality_requires_a_name(self):
        self.assertIsNotNone(validate_modalidade_fields("  "))
        self.assertIsNone(validate_modalidade_fields(" Yoga "))

    def test_reservation_student_options_are_active_and_minimal(self):
        options = active_student_options(
            [
                {
                    "id": 3,
                    "nome": "Ana",
                    "situacao": "Ativo",
                    "cpf": "sensitive",
                    "contato": "sensitive",
                },
                {"id": 4, "nome": "Bia", "situacao": "Inativo"},
            ]
        )
        self.assertEqual(options, [{"id": "3", "label": "Ana"}])
        self.assertNotIn("cpf", options[0])

    def test_session_validation_checks_ids_time_and_capacity(self):
        now = datetime(2026, 11, 12, 12, tzinfo=timezone(timedelta(hours=-3)))
        valid = ("2", "7", "2026-11-13T10:00", "2026-11-13T11:00", "12")
        self.assertIsNone(validate_sessao_fields(*valid, now=now))
        self.assertIsNotNone(
            validate_sessao_fields(
                "0",
                "7",
                "2026-11-13T10:00",
                "2026-11-13T11:00",
                "12",
                now=now,
            )
        )
        self.assertIsNotNone(
            validate_sessao_fields(
                "2",
                "7",
                "2026-11-13T10:00",
                "2026-11-13T10:00",
                "12",
                now=now,
            )
        )
        self.assertIsNotNone(
            validate_sessao_fields(
                "2",
                "7",
                "2026-11-13T10:00",
                "2026-11-13T11:00",
                "0",
                now=now,
            )
        )

    def test_local_session_time_is_sent_as_utc(self):
        self.assertEqual(
            to_api_timestamp("2026-11-13T10:00"),
            "2026-11-13T13:00:00Z",
        )


class _AccessHarness:
    def __init__(self, token):
        self.login_state = SimpleNamespace(auth_token=token)
        self.access_state = SimpleNamespace(
            is_admin=False,
            is_verifying=False,
            error_message="",
        )

    async def get_state(self, state_type):
        if state_type is LoginState:
            return self.login_state
        return self.access_state


class AdminRouteAccessTests(unittest.IsolatedAsyncioTestCase):
    async def test_admin_identity_is_allowed(self):
        state = _AccessHarness("session-token")
        with patch(
            "academia.access_control.XanoClient.get_current_user",
            return_value={"id": 7, "role": "admin"},
        ):
            token, redirect = await require_admin(state, "relatorios")
        self.assertEqual(token, "session-token")
        self.assertFalse(redirect)
        self.assertTrue(state.access_state.is_admin)
        self.assertEqual(state.access_state.authorized_route, "relatorios")

    async def test_non_admin_identity_is_denied(self):
        state = _AccessHarness("session-token")
        with patch(
            "academia.access_control.XanoClient.get_current_user",
            return_value={"id": 7, "role": "instrutor"},
        ):
            token, redirect = await require_admin(state)
        self.assertEqual(token, "")
        self.assertFalse(redirect)
        self.assertFalse(state.access_state.is_admin)
        self.assertTrue(state.access_state.error_message)

    async def test_missing_session_requests_login_redirect(self):
        state = _AccessHarness("")
        with patch(
            "academia.session_state.clear_app_session",
            new_callable=AsyncMock,
        ) as clear_session:
            token, redirect = await require_admin(state)
        self.assertEqual(token, "")
        self.assertTrue(redirect)
        clear_session.assert_awaited_once_with(state)


class _OperationStateHarness(_AccessHarness):
    def __init__(self):
        super().__init__("session-token")
        self.modalidades = []
        self.modalidade_options = []
        self.sessoes = []
        self.sessao_options = []
        self.reservas = []
        self.aluno_options = []
        self.resumo_reservas = {}
        self.relatorio = {}
        self.report_metrics = []
        self.selected_sessao = {}
        self.selected_sessao_id = ""
        self.data_inicio = ""
        self.data_fim = ""
        self.is_loading = False
        self.is_saving = False
        self.is_changing_status = False
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""
        self.modalidade_id = 0
        self.modalidade_nome = ""
        self.modalidade_descricao = ""
        self.modalidade_editing = False
        self.sessao_id = 0
        self.sessao_modalidade_id = ""
        self.sessao_instrutor_id = ""
        self.sessao_inicio = ""
        self.sessao_termino = ""
        self.sessao_capacidade = ""
        self.sessao_local = ""
        self.sessao_editing = False
        self.reserva_aluno_id = ""

    async def _admin_token(self, route):
        return await require_admin(self, route)

    async def _redirect_if_expired(self, error):
        return error.status_code == 401

    def _prepare_modality_options(self):
        OperacaoState._prepare_modality_options(self)

    def _api_error_message(self, error, action):
        return OperacaoState._api_error_message(self, error, action)

    def _clear_sensitive_data(self):
        self.modalidades = []


class OperationScreenStateTests(unittest.IsolatedAsyncioTestCase):
    async def run_load_modalidades(self, state):
        event = OperacaoState.__dict__["load_modalidades"].fn
        return [result async for result in event(state)]

    async def test_empty_modalities_are_a_successful_empty_state(self):
        state = _OperationStateHarness()
        with (
            patch(
                "academia.access_control.XanoClient.get_current_user",
                return_value={"role": "admin"},
            ),
            patch(
                "academia.operacao.XanoClient.get_modalidades",
                return_value=[],
            ),
        ):
            await self.run_load_modalidades(state)
        self.assertEqual(state.modalidades, [])
        self.assertEqual(state.error_message, "")
        self.assertFalse(state.is_loading)
        self.assertEqual(state.access_state.authorized_route, "modalidades")

    async def test_modality_load_failure_is_not_presented_as_empty_success(self):
        state = _OperationStateHarness()
        with (
            patch(
                "academia.access_control.XanoClient.get_current_user",
                return_value={"role": "admin"},
            ),
            patch(
                "academia.operacao.XanoClient.get_modalidades",
                side_effect=XanoAPIError("offline"),
            ),
        ):
            await self.run_load_modalidades(state)
        self.assertEqual(state.modalidades, [])
        self.assertTrue(state.error_message)
        self.assertFalse(state.is_loading)


if __name__ == "__main__":
    unittest.main()
