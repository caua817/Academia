import unittest
from types import SimpleNamespace

from academia.access_control import AdminAccessState
from academia.academia import DashboardState
from academia.alunos import AlunosState
from academia.financeiro import CheckinsState, FinanceiroState
from academia.funcionarios import FuncionariosState
from academia.login import LoginState
from academia.matriculas import MatriculasState
from academia.operacao import OperacaoState
from academia.planos import PlanosState
from academia.session_state import clear_app_session


class StrictState:
    def __init__(self, fields: set[str], **values):
        object.__setattr__(self, "_fields", fields)
        for field, value in values.items():
            setattr(self, field, value)

    def __setattr__(self, name: str, value: object) -> None:
        if name not in self._fields:
            raise AttributeError(f"Undeclared state field: {name}")
        object.__setattr__(self, name, value)


class SessionStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_clearing_session_only_updates_declared_login_fields(self):
        login_state = StrictState(
            set(LoginState.get_fields()),
            auth_token="session-token",
            email="staff@example.com",
            password_visible=True,
        )
        states = {
            DashboardState: SimpleNamespace(
                alunos=[{"id": 1}],
                search_query="Ana",
                error_message="error",
                is_loading=True,
            ),
            AlunosState: SimpleNamespace(
                _clear_sensitive_data=lambda: None,
                is_loading=True,
                is_loading_details=True,
                is_saving=True,
                is_deactivating=True,
            ),
            PlanosState: SimpleNamespace(
                _clear_sensitive_data=lambda: None,
                is_loading=True,
                is_loading_details=True,
                is_saving=True,
                is_changing_status=True,
            ),
            MatriculasState: SimpleNamespace(
                _clear_sensitive_data=lambda: None,
                is_loading=True,
                is_saving=True,
                is_loading_details=True,
            ),
            FinanceiroState: SimpleNamespace(_clear_sensitive_data=lambda: None),
            CheckinsState: SimpleNamespace(_clear_sensitive_data=lambda: None),
            FuncionariosState: SimpleNamespace(_clear_sensitive_data=lambda: None),
            OperacaoState: SimpleNamespace(_clear_sensitive_data=lambda: None),
            AdminAccessState: SimpleNamespace(clear=lambda: None),
            LoginState: login_state,
        }

        class StateHarness:
            async def get_state(self, state_type):
                return states[state_type]

        await clear_app_session(StateHarness())

        self.assertEqual(login_state.auth_token, "")
        self.assertEqual(login_state.email, "")
        self.assertFalse(login_state.password_visible)
