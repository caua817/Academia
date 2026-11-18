import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from academia.access_control import require_admin
from academia.login import LoginState
from academia.operacao import (
    OperacaoState,
    active_instructor_options,
    combine_session_datetime,
    to_api_timestamp,
    validate_date_range,
    validate_modalidade_fields,
    validate_sessao_fields,
    sessoes_content,
)
from academia.services.xano_client import XanoAPIError


class _LoginStateHarness(SimpleNamespace):
    _clear_verified_profile = LoginState._clear_verified_profile
    _cache_verified_profile = LoginState._cache_verified_profile
    _get_verified_profile_role = LoginState._get_verified_profile_role


class OperationValidationTests(unittest.TestCase):
    def test_date_range_validation(self):
        self.assertIsNone(validate_date_range("2026-11-01", "2026-11-30"))
        self.assertIsNotNone(validate_date_range("2026-11-30", "2026-11-01"))
        self.assertIsNotNone(validate_date_range("not-a-date", "2026-11-01"))

    def test_modality_requires_a_name(self):
        self.assertIsNotNone(validate_modalidade_fields("  "))
        self.assertIsNone(validate_modalidade_fields(" Yoga "))

    def test_instructor_options_only_include_active_named_instructors(self):
        options = active_instructor_options(
            [
                {"id": 7, "name": "Ana", "role": "instrutor", "situacao": "Ativo"},
                {"id": 8, "name": "Bia", "role": "instrutor", "situacao": "Inativo"},
                {"id": 9, "name": "Caio", "role": "admin", "situacao": "Ativo"},
                {"id": 0, "name": "Duda", "role": "instrutor", "situacao": "Ativo"},
                {"id": 10, "role": "instrutor", "situacao": "Ativo"},
            ]
        )
        self.assertEqual(options, [{"id": "7", "label": "Ana"}])

    def test_session_validation_checks_date_times_ids_and_capacity(self):
        now = datetime(2026, 11, 12, 12, tzinfo=timezone(timedelta(hours=-3)))
        valid = ("2", "7", "2026-11-13", "10:00", "11:00", "12")
        self.assertIsNone(validate_sessao_fields(*valid, now=now))
        self.assertIsNotNone(
            validate_sessao_fields(
                "0",
                "7",
                "2026-11-13",
                "10:00",
                "11:00",
                "12",
                now=now,
            )
        )
        self.assertIsNotNone(
            validate_sessao_fields(
                "2",
                "7",
                "2026-11-13",
                "10:00",
                "10:00",
                "12",
                now=now,
            )
        )
        self.assertIsNotNone(
            validate_sessao_fields(
                "2",
                "7",
                "2026-11-13",
                "10:00",
                "11:00",
                "0",
                now=now,
            )
        )

    def test_single_session_date_is_combined_with_each_time(self):
        self.assertEqual(
            combine_session_datetime("2026-11-13", "10:30"),
            "2026-11-13T10:30",
        )
        self.assertEqual(
            to_api_timestamp(
                combine_session_datetime("2026-11-13", "10:30")
            ),
            "2026-11-13T13:30:00Z",
        )

    def test_local_session_time_is_sent_as_utc(self):
        self.assertEqual(
            to_api_timestamp("2026-11-13T10:00"),
            "2026-11-13T13:00:00Z",
        )


class _AccessHarness:
    def __init__(self, token):
        self.login_state = _LoginStateHarness(
            auth_token=token,
            _verified_profile_role="",
            _verified_profile_token_digest="",
        )
        self.access_state = SimpleNamespace(
            is_admin=False,
            is_verifying=False,
            error_message="",
            authorized_route="",
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
        self.relatorio = {}
        self.report_metrics = []
        self.selected_sessao = {}
        self.selected_sessao_id = ""
        self.instrutor_options = []
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
        self.sessao_data = ""
        self.sessao_hora_inicio = ""
        self.sessao_hora_termino = ""
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

    def _prepare_sessions(self):
        OperacaoState._prepare_sessions(self)

    def _date_filters(self):
        return OperacaoState._date_filters(self)

    def _reset_sessao_form(self):
        OperacaoState._reset_sessao_form(self)

    def _api_error_message(self, error, action):
        return OperacaoState._api_error_message(self, error, action)

    def _clear_sensitive_data(self):
        self.modalidades = []


class OperationScreenStateTests(unittest.IsolatedAsyncioTestCase):
    async def run_event(self, name, state):
        event = OperacaoState.__dict__[name].fn
        return [result async for result in event(state)]

    async def run_load_sessoes(self, state):
        event = OperacaoState.__dict__["load_sessoes"].fn
        return [result async for result in event(state)]

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

    async def test_edit_session_splits_local_date_and_times(self):
        state = _OperationStateHarness()
        state.sessoes = [
            {
                "id": 4,
                "modalidade_id": 2,
                "instrutor_id": 7,
                "inicio": "2026-11-13T13:00:00Z",
                "termino": "2026-11-13T14:30:00Z",
                "capacidade": 12,
                "local": "Sala 1",
            }
        ]
        OperacaoState.__dict__["edit_sessao"].fn(state, 4)
        self.assertEqual(state.sessao_data, "2026-11-13")
        self.assertEqual(state.sessao_hora_inicio, "10:00")
        self.assertEqual(state.sessao_hora_termino, "11:30")
        self.assertEqual(state.sessao_instrutor_id, "7")
        self.assertTrue(state.sessao_editing)

    async def test_create_session_combines_one_date_and_preserves_api_payload(self):
        state = _OperationStateHarness()
        state.sessao_modalidade_id = "2"
        state.sessao_instrutor_id = "7"
        state.sessao_data = "2027-01-02"
        state.sessao_hora_inicio = "10:00"
        state.sessao_hora_termino = "11:00"
        state.sessao_capacidade = "12"
        state.sessao_local = "Sala 1"
        state.data_inicio = "2027-01-02"
        state.data_fim = "2027-01-16"
        with (
            patch(
                "academia.access_control.XanoClient.get_current_user",
                return_value={"role": "admin"},
            ),
            patch(
                "academia.operacao.XanoClient.create_sessao",
            ) as create_session,
            patch(
                "academia.operacao.XanoClient.get_modalidades",
                return_value=[],
            ),
            patch(
                "academia.operacao.XanoClient.get_sessoes",
                return_value=[],
            ),
        ):
            await self.run_event("save_sessao", state)
        create_session.assert_called_once_with(
            "session-token",
            {
                "modalidade_id": 2,
                "instrutor_id": 7,
                "inicio": "2027-01-02T13:00:00Z",
                "termino": "2027-01-02T14:00:00Z",
                "capacidade": 12,
                "local": "Sala 1",
            },
        )
        self.assertEqual(state.success_message, "Sessão criada com sucesso.")

    async def test_invalid_session_times_do_not_call_api(self):
        state = _OperationStateHarness()
        state.sessao_modalidade_id = "2"
        state.sessao_instrutor_id = "7"
        state.sessao_data = "2027-01-02"
        state.sessao_hora_inicio = "11:00"
        state.sessao_hora_termino = "10:00"
        state.sessao_capacidade = "12"
        with patch(
            "academia.operacao.XanoClient.create_sessao",
        ) as create_session:
            await self.run_event("save_sessao", state)
        create_session.assert_not_called()
        self.assertIn("posterior", state.form_error)

    async def test_load_sessions_exposes_only_active_instructors_by_name(self):
        state = _OperationStateHarness()
        state.data_inicio = "2026-11-13"
        state.data_fim = "2026-11-14"
        employees = [
            {"id": 7, "name": "Ana", "role": "instrutor", "situacao": "Ativo"},
            {"id": 8, "name": "Bia", "role": "instrutor", "situacao": "Inativo"},
            {"id": 9, "name": "Caio", "role": "admin", "situacao": "Ativo"},
        ]
        with (
            patch(
                "academia.access_control.XanoClient.get_current_user",
                return_value={"role": "admin"},
            ),
            patch(
                "academia.operacao.XanoClient.get_modalidades",
                return_value=[],
            ),
            patch(
                "academia.operacao.XanoClient.get_funcionarios",
                return_value=employees,
            ),
            patch(
                "academia.operacao.XanoClient.get_sessoes",
                return_value=[],
            ) as get_sessions,
        ):
            await self.run_load_sessoes(state)
        get_sessions.assert_called_once_with(
            "session-token",
            "2026-11-13",
            "2026-11-14",
        )
        self.assertEqual(
            state.instrutor_options,
            [{"id": "7", "label": "Ana"}],
        )
        self.assertEqual(state.sessoes, [])
        self.assertEqual(state.error_message, "")

    async def test_load_sessions_reports_employee_api_failure(self):
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
            patch(
                "academia.operacao.XanoClient.get_funcionarios",
                side_effect=XanoAPIError("offline"),
            ),
        ):
            await self.run_load_sessoes(state)
        self.assertEqual(state.instrutor_options, [])
        self.assertTrue(state.error_message)
        self.assertFalse(state.is_loading)

    async def test_session_form_renders_one_date_and_named_instructor(self):
        rendered = str(sessoes_content())
        self.assertIn("Data da aula", rendered)
        self.assertIn("Hor\\u00e1rio de in\\u00edcio", rendered)
        self.assertIn("Hor\\u00e1rio de t\\u00e9rmino", rendered)
        self.assertIn("Selecione um instrutor", rendered)
        self.assertNotIn("ID do instrutor", rendered)
        self.assertNotIn('type:"datetime-local"', rendered)
        self.assertNotIn("Ocupação:", rendered)
        self.assertNotIn("Reservas", rendered)

    def test_removed_reservation_route_is_not_registered_or_linked(self):
        from academia.academia import app, sidebar

        self.assertNotIn("/reservas", app._pages)
        self.assertNotIn("/reservas", str(sidebar("dashboard")))

    def test_bytefit_brand_is_visible_on_login_and_navigation(self):
        from academia.academia import sidebar
        from academia.login import login_page

        self.assertIn("ByteFit", str(login_page()))
        self.assertIn("ByteFit", str(sidebar("dashboard")))

    def test_report_metrics_exclude_reservations_and_occupancy(self):
        state = _OperationStateHarness()
        state.relatorio = {
            "matriculas_ativas": 2,
            "pagamentos_quantidade": 1,
            "pagamentos_valor": 50,
            "mensalidades_atrasadas_quantidade": 0,
            "mensalidades_atrasadas_valor": 0,
            "checkins_quantidade": 4,
            "sessoes_quantidade": 2,
            "capacidade_total": 20,
        }
        OperacaoState._prepare_report_metrics(state)
        labels = {metric["label"] for metric in state.report_metrics}
        self.assertIn("Sessões", labels)
        self.assertIn("Capacidade total", labels)
        self.assertNotIn("Ocupação", labels)
        self.assertNotIn("Reservas não canceladas", labels)


if __name__ == "__main__":
    unittest.main()
