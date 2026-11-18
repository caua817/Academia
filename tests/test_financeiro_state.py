import unittest
from types import SimpleNamespace
from unittest.mock import patch

from academia.financeiro import FinanceiroState
from academia.login import LoginState
from academia.services.xano_client import XanoAPIError


class FinanceiroStateHarness:
    def __init__(self):
        self.mensalidades = [
            {"id": 5, "valor": 80, "situacao": "Pendente"},
        ]
        self.pagamentos = [{"id": 12, "situacao": "Registrado"}]
        self.is_loading = False
        self.is_saving = False
        self.is_correcting = False
        self.is_correction_open = True
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""
        self.forma_pagamento = "PIX"
        self.pagamento_id = 12
        self.tipo_correcao = "Cancelado"
        self.motivo_correcao = "Lançamento incorreto"
        self.login_state = SimpleNamespace(auth_token="session-token")

    async def get_state(self, state_type):
        if state_type is LoginState:
            return self.login_state
        raise AssertionError(f"Unexpected state requested: {state_type}")

    def _api_error_message(self, error, action):
        return FinanceiroState._api_error_message(self, error, action)

    def _reload(self, token, action):
        return FinanceiroState._reload(self, token, action)


class FinanceiroStateTests(unittest.IsolatedAsyncioTestCase):
    async def run_event(self, name, state, *args):
        event = FinanceiroState.__dict__[name].fn
        return [result async for result in event(state, *args)]

    async def test_duplicate_load_is_ignored_while_a_load_is_in_progress(self):
        state = FinanceiroStateHarness()
        event = FinanceiroState.__dict__["load_financeiro"].fn
        with (
            patch("academia.financeiro.begin_admin_check", new=_begin_admin_check),
            patch(
                "academia.financeiro.require_route_access",
                new=_require_route_access,
            ),
            patch(
                "academia.financeiro.XanoClient.get_mensalidades",
                return_value=[],
            ) as get_mensalidades,
            patch(
                "academia.financeiro.XanoClient.get_pagamentos",
                return_value=[],
            ) as get_pagamentos,
        ):
            first_load = event(state)
            await first_load.__anext__()
            await self.run_event("load_financeiro", state)
            await _finish_event(first_load)

        get_mensalidades.assert_called_once_with("session-token")
        get_pagamentos.assert_called_once_with("session-token")
        self.assertFalse(state.is_loading)

    async def test_duplicate_payment_registration_is_ignored_while_saving(self):
        state = FinanceiroStateHarness()
        event = FinanceiroState.__dict__["registrar_pagamento"].fn
        with (
            patch(
                "academia.financeiro.XanoClient.create_pagamento",
                return_value={},
            ) as create_pagamento,
            patch(
                "academia.financeiro.XanoClient.get_mensalidades",
                return_value=[],
            ),
            patch(
                "academia.financeiro.XanoClient.get_pagamentos",
                return_value=[],
            ),
        ):
            first_save = event(state, 5)
            await first_save.__anext__()
            await self.run_event("registrar_pagamento", state, 5)
            await _finish_event(first_save)

        create_pagamento.assert_called_once()
        self.assertFalse(state.is_saving)

    async def test_duplicate_correction_is_ignored_while_correcting(self):
        state = FinanceiroStateHarness()
        event = FinanceiroState.__dict__["corrigir_pagamento"].fn
        with (
            patch(
                "academia.financeiro.XanoClient.correct_pagamento",
                return_value={},
            ) as correct_pagamento,
            patch(
                "academia.financeiro.XanoClient.get_mensalidades",
                return_value=[],
            ),
            patch(
                "academia.financeiro.XanoClient.get_pagamentos",
                return_value=[],
            ),
        ):
            first_correction = event(state)
            await first_correction.__anext__()
            await self.run_event("corrigir_pagamento", state)
            await _finish_event(first_correction)

        correct_pagamento.assert_called_once()
        self.assertFalse(state.is_correcting)

    async def test_rate_limit_during_reload_preserves_loaded_data(self):
        state = FinanceiroStateHarness()
        previous_mensalidades = state.mensalidades
        previous_pagamentos = state.pagamentos
        with patch(
            "academia.financeiro.XanoClient.get_mensalidades",
            side_effect=XanoAPIError("too many requests", 429),
        ):
            expired = state._reload("session-token", "carregar os dados")

        self.assertFalse(expired)
        self.assertEqual(state.mensalidades, previous_mensalidades)
        self.assertEqual(state.pagamentos, previous_pagamentos)
        self.assertIn("limite temporário", state.error_message)
        self.assertIn("Aguarde", state.error_message)

    async def test_rate_limited_payment_registration_keeps_data_without_success(self):
        state = FinanceiroStateHarness()
        previous_mensalidades = state.mensalidades
        previous_pagamentos = state.pagamentos
        with patch(
            "academia.financeiro.XanoClient.create_pagamento",
            side_effect=XanoAPIError("too many requests", 429),
        ):
            await self.run_event("registrar_pagamento", state, 5)

        self.assertEqual(state.mensalidades, previous_mensalidades)
        self.assertEqual(state.pagamentos, previous_pagamentos)
        self.assertEqual(state.success_message, "")
        self.assertIn("limite temporário", state.error_message)
        self.assertFalse(state.is_saving)

    async def test_rate_limited_correction_keeps_data_without_success(self):
        state = FinanceiroStateHarness()
        previous_mensalidades = state.mensalidades
        previous_pagamentos = state.pagamentos
        with patch(
            "academia.financeiro.XanoClient.correct_pagamento",
            side_effect=XanoAPIError("too many requests", 429),
        ):
            await self.run_event("corrigir_pagamento", state)

        self.assertEqual(state.mensalidades, previous_mensalidades)
        self.assertEqual(state.pagamentos, previous_pagamentos)
        self.assertEqual(state.success_message, "")
        self.assertIn("limite temporário", state.error_message)
        self.assertFalse(state.is_correcting)


async def _finish_event(event):
    try:
        while True:
            await event.__anext__()
    except StopAsyncIteration:
        return


async def _begin_admin_check(state):
    return None


async def _require_route_access(state, route):
    return "session-token", False


if __name__ == "__main__":
    unittest.main()
