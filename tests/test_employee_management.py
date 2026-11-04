import json
import unittest
from unittest.mock import patch

import httpx

from academia.funcionarios import (
    FuncionariosState,
    employee_form_dialog,
    filter_funcionarios,
    validate_funcionario_fields,
)
from academia.services.xano_client import XanoAPIError, XanoClient

_HTTPX_CLIENT = httpx.Client


class EmployeeClientTests(unittest.TestCase):
    def invoke(self, operation, response_data):
        requests = []

        def handle(request):
            requests.append(request)
            return httpx.Response(200, json=response_data, request=request)

        client = _HTTPX_CLIENT(transport=httpx.MockTransport(handle))
        with patch(
            "academia.services.xano_client.httpx.Client",
            return_value=client,
        ):
            result = operation()
        return result, requests

    def test_employee_routes_and_payloads(self):
        token = "session-token"
        employee = {
            "id": 7,
            "name": "Ana Lima",
            "email": "ana@example.com",
            "role": "instrutor",
            "situacao": "Ativo",
            "status_convite": "Enviado",
        }
        payload = {
            "name": "Ana Lima",
            "email": "ana@example.com",
            "role": "instrutor",
        }
        scenarios = [
            (
                lambda: XanoClient.get_current_user(token),
                {"id": 1, "role": "admin"},
                "GET",
                "/auth/me",
                None,
            ),
            (
                lambda: XanoClient.get_funcionarios(token),
                [employee],
                "GET",
                "/funcionarios",
                None,
            ),
            (
                lambda: XanoClient.get_funcionario(token, 7),
                employee,
                "GET",
                "/funcionarios/detalhes/7",
                None,
            ),
            (
                lambda: XanoClient.invite_funcionario(token, payload),
                employee,
                "POST",
                "/funcionarios/convites",
                payload,
            ),
            (
                lambda: XanoClient.update_funcionario(token, 7, payload),
                employee,
                "PUT",
                "/funcionarios/atualizar/7",
                payload,
            ),
            (
                lambda: XanoClient.deactivate_funcionario(token, 7),
                {**employee, "situacao": "Inativo"},
                "PATCH",
                "/funcionarios/desativar/7",
                None,
            ),
            (
                lambda: XanoClient.activate_funcionario(token, 7),
                employee,
                "PATCH",
                "/funcionarios/ativar/7",
                None,
            ),
        ]

        for operation, response_data, method, path, payload_data in scenarios:
            with self.subTest(method=method, path=path):
                result, requests = self.invoke(operation, response_data)
                self.assertEqual(result, response_data)
                self.assertEqual(len(requests), 1)
                request = requests[0]
                self.assertEqual(request.method, method)
                self.assertEqual(
                    request.headers["Authorization"],
                    f"Bearer {token}",
                )
                self.assertEqual(
                    request.url.path,
                    f"/api:sGd5fzIy{path}",
                )
                if payload_data is not None:
                    self.assertEqual(
                        json.loads(request.content),
                        payload_data,
                    )

    def test_employee_payload_rejects_credentials_without_request(self):
        with self.assertRaises(XanoAPIError):
            XanoClient.invite_funcionario(
                "session-token",
                {
                    "name": "Ana Lima",
                    "email": "ana@example.com",
                    "role": "instrutor",
                    "password": "not-sent",
                },
            )

    def test_employee_responses_reject_passwords_and_tokens(self):
        responses = [
            lambda: self.invoke(
                lambda: XanoClient.get_current_user("session-token"),
                {"id": 1, "role": "admin", "access_token": "not-exposed"},
            ),
            lambda: self.invoke(
                lambda: XanoClient.get_funcionario("session-token", 7),
                {
                    "id": 7,
                    "name": "Ana Lima",
                    "credentials": {"access_token": "not-exposed"},
                },
            ),
            lambda: self.invoke(
                lambda: XanoClient.get_funcionarios("session-token"),
                [{"id": 7, "name": "Ana Lima", "password_hash": "not-exposed"}],
            ),
        ]

        for response in responses:
            with self.subTest(response=response):
                with self.assertRaises(XanoAPIError):
                    response()

    def test_invalid_employee_list_shape_is_reported(self):
        with self.assertRaises(XanoAPIError):
            self.invoke(
                lambda: XanoClient.get_funcionarios("session-token"),
                {"funcionarios": []},
            )

    def test_http_401_and_403_preserve_status_codes(self):
        for status_code in (401, 403):
            client = _HTTPX_CLIENT(
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(
                        status_code,
                        json={"message": "rejected"},
                        request=request,
                    )
                )
            )
            with self.subTest(status_code=status_code):
                with patch(
                    "academia.services.xano_client.httpx.Client",
                    return_value=client,
                ):
                    with self.assertRaises(XanoAPIError) as context:
                        XanoClient.get_funcionarios("session-token")
                self.assertEqual(context.exception.status_code, status_code)

    def test_connection_failure_is_reported(self):
        def fail_connection(request):
            raise httpx.ConnectError("offline", request=request)

        client = _HTTPX_CLIENT(
            transport=httpx.MockTransport(fail_connection)
        )
        with patch(
            "academia.services.xano_client.httpx.Client",
            return_value=client,
        ):
            with self.assertRaises(XanoAPIError) as context:
                XanoClient.get_funcionarios("session-token")

        self.assertIsNone(context.exception.status_code)


class EmployeeStateHarness:
    def __init__(self, token="session-token"):
        self.auth_token = token
        self.funcionarios = []
        self.user_role = ""
        self.search_query = ""
        self.is_admin = False
        self.is_loading = False
        self.is_loading_details = False
        self.is_saving = False
        self.is_changing_status = False
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""
        self.is_form_open = False
        self.is_editing = False
        self.funcionario_id = 0
        self.form_name = ""
        self.form_email = ""
        self.form_role = "recepcionista"
        self.is_status_dialog_open = False
        self.funcionario_id_to_change = 0
        self.is_reactivating = False
        self.session_cleared = False

    async def _auth_token(self):
        return self.auth_token

    async def _clear_login(self):
        self.session_cleared = True
        self.funcionarios = []
        self.user_role = ""
        self.is_admin = False

    def _api_error_message(self, error, action):
        return FuncionariosState._api_error_message(self, error, action)

    async def _reload_funcionarios(self, token, action):
        return await FuncionariosState._reload_funcionarios(self, token, action)

    def _require_admin(self):
        return FuncionariosState._require_admin(self)

    def _reset_form(self):
        FuncionariosState._reset_form(self)

    def _clear_sensitive_data(self):
        FuncionariosState._clear_sensitive_data(self)


class EmployeeStateTests(unittest.IsolatedAsyncioTestCase):
    async def run_load(self, state):
        event = FuncionariosState.__dict__["load_funcionarios"].fn
        return [result async for result in event(state)]

    async def run_event(self, name, state):
        event = FuncionariosState.__dict__[name].fn
        return [result async for result in event(state)]

    async def test_admin_identity_is_checked_before_loading_employees(self):
        employees = [{"id": 3, "name": "Ana", "role": "instrutor"}]
        call_order = []
        with (
            patch(
                "academia.funcionarios.XanoClient.get_current_user",
                side_effect=lambda token: (
                    call_order.append("identity") or {"role": "admin"}
                ),
            ) as get_identity,
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios",
                side_effect=lambda token: (
                    call_order.append("employees") or employees
                ),
            ) as get_employees,
        ):
            state = EmployeeStateHarness()
            await self.run_load(state)

        self.assertEqual(call_order, ["identity", "employees"])
        get_identity.assert_called_once_with("session-token")
        get_employees.assert_called_once_with("session-token")
        self.assertTrue(state.is_admin)
        self.assertEqual(state.funcionarios, employees)
        self.assertFalse(state.is_loading)

    async def test_non_admin_identity_never_loads_employee_data(self):
        with (
            patch(
                "academia.funcionarios.XanoClient.get_current_user",
                return_value={"role": "member"},
            ),
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios"
            ) as get_employees,
        ):
            state = EmployeeStateHarness()
            await self.run_load(state)

        get_employees.assert_not_called()
        self.assertFalse(state.is_admin)
        self.assertEqual(state.funcionarios, [])
        self.assertIn("permissão", state.error_message)

    async def test_http_403_identity_denies_area_without_loading_employees(self):
        with (
            patch(
                "academia.funcionarios.XanoClient.get_current_user",
                side_effect=XanoAPIError("forbidden", 403),
            ),
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios"
            ) as get_employees,
        ):
            state = EmployeeStateHarness()
            await self.run_load(state)

        get_employees.assert_not_called()
        self.assertFalse(state.is_admin)
        self.assertEqual(state.funcionarios, [])
        self.assertIn("permissão", state.error_message)

    async def test_http_401_clears_employee_data_and_session(self):
        with (
            patch(
                "academia.funcionarios.XanoClient.get_current_user",
                side_effect=XanoAPIError("expired", 401),
            ),
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios"
            ) as get_employees,
        ):
            state = EmployeeStateHarness()
            state.funcionarios = [{"id": 3, "name": "Ana"}]
            state.user_role = "admin"
            state.is_admin = True
            await self.run_load(state)

        get_employees.assert_not_called()
        self.assertTrue(state.session_cleared)
        self.assertFalse(state.is_admin)
        self.assertEqual(state.funcionarios, [])
        self.assertFalse(state.is_loading)

    async def test_invite_sends_only_operational_fields_and_confirms_success(self):
        state = EmployeeStateHarness()
        state.is_admin = True
        state.form_name = "Ana Lima"
        state.form_email = " ANA@example.com "
        state.form_role = "instrutor"
        state.is_form_open = True
        with (
            patch(
                "academia.funcionarios.XanoClient.invite_funcionario",
                return_value={"id": 7},
            ) as invite,
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios",
                return_value=[],
            ),
        ):
            await self.run_event("save_funcionario", state)

        invite.assert_called_once_with(
            "session-token",
            {
                "name": "Ana Lima",
                "email": "ana@example.com",
                "role": "instrutor",
            },
        )
        self.assertFalse(state.is_form_open)
        self.assertEqual(state.success_message, "Convite enviado com sucesso.")
        self.assertFalse(state.is_saving)

    async def test_rejected_invite_keeps_form_open_without_success(self):
        state = EmployeeStateHarness()
        state.is_admin = True
        state.form_name = "Ana Lima"
        state.form_email = "ana@example.com"
        state.form_role = "instrutor"
        state.is_form_open = True
        with patch(
            "academia.funcionarios.XanoClient.invite_funcionario",
            side_effect=XanoAPIError("E-mail já utilizado.", 409),
        ):
            await self.run_event("save_funcionario", state)

        self.assertTrue(state.is_form_open)
        self.assertIn("E-mail já utilizado", state.form_error)
        self.assertEqual(state.success_message, "")

    async def test_rejected_edit_keeps_form_open_without_success(self):
        state = EmployeeStateHarness()
        state.is_admin = True
        state.is_editing = True
        state.funcionario_id = 7
        state.form_name = "Ana Lima"
        state.form_email = "ana@example.com"
        state.form_role = "instrutor"
        state.is_form_open = True
        with patch(
            "academia.funcionarios.XanoClient.update_funcionario",
            side_effect=XanoAPIError("Alteração rejeitada.", 400),
        ):
            await self.run_event("save_funcionario", state)

        self.assertTrue(state.is_form_open)
        self.assertIn("Alteração rejeitada", state.form_error)
        self.assertEqual(state.success_message, "")

    async def test_confirmed_reactivation_uses_activate_endpoint(self):
        state = EmployeeStateHarness()
        state.is_admin = True
        state.funcionario_id_to_change = 7
        state.is_reactivating = True
        state.is_status_dialog_open = True
        with (
            patch(
                "academia.funcionarios.XanoClient.activate_funcionario",
                return_value={"id": 7, "situacao": "Ativo"},
            ) as activate,
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios",
                return_value=[],
            ),
        ):
            await self.run_event("confirm_status_change", state)

        activate.assert_called_once_with("session-token", 7)
        self.assertFalse(state.is_status_dialog_open)
        self.assertEqual(state.success_message, "Funcionário ativado com sucesso.")
        self.assertFalse(state.is_changing_status)

    async def test_confirmed_deactivation_uses_deactivate_endpoint(self):
        state = EmployeeStateHarness()
        state.is_admin = True
        state.funcionario_id_to_change = 7
        state.is_status_dialog_open = True
        with (
            patch(
                "academia.funcionarios.XanoClient.deactivate_funcionario",
                return_value={"id": 7, "situacao": "Inativo"},
            ) as deactivate,
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios",
                return_value=[],
            ),
        ):
            await self.run_event("confirm_status_change", state)

        deactivate.assert_called_once_with("session-token", 7)
        self.assertFalse(state.is_status_dialog_open)
        self.assertEqual(
            state.success_message,
            "Funcionário desativado com sucesso.",
        )

    def test_cancel_status_change_does_not_call_api(self):
        state = EmployeeStateHarness()
        state.is_status_dialog_open = True
        state.funcionario_id_to_change = 7

        FuncionariosState.__dict__["cancel_status_change"].fn(state)

        self.assertFalse(state.is_status_dialog_open)
        self.assertEqual(state.funcionario_id_to_change, 0)

    def test_search_includes_name_email_role_and_status(self):
        employees = [
            {
                "id": 1,
                "name": "Ana Lima",
                "email": "ana@example.com",
                "role": "instrutor",
                "situacao": "Ativo",
            },
            {
                "id": 2,
                "name": "Bruno Reis",
                "email": "bruno@example.com",
                "role": "recepcionista",
                "situacao": "Inativo",
            },
        ]

        self.assertEqual(filter_funcionarios(employees, "ANA"), [employees[0]])
        self.assertEqual(
            filter_funcionarios(employees, "EXAMPLE.COM"),
            employees,
        )
        self.assertEqual(
            filter_funcionarios(employees, "recepcionista"),
            [employees[1]],
        )
        self.assertEqual(filter_funcionarios(employees, "inativo"), [employees[1]])
        self.assertEqual(filter_funcionarios(employees, " "), employees)
        self.assertEqual(filter_funcionarios(employees, "no match"), [])

    async def test_empty_employee_list_is_not_reported_as_an_api_error(self):
        with (
            patch(
                "academia.funcionarios.XanoClient.get_current_user",
                return_value={"role": "admin"},
            ),
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios",
                return_value=[],
            ),
        ):
            state = EmployeeStateHarness()
            await self.run_load(state)

        self.assertTrue(state.is_admin)
        self.assertEqual(state.funcionarios, [])
        self.assertEqual(state.error_message, "")

    async def test_network_failure_is_not_shown_as_an_empty_success(self):
        with (
            patch(
                "academia.funcionarios.XanoClient.get_current_user",
                return_value={"role": "admin"},
            ),
            patch(
                "academia.funcionarios.XanoClient.get_funcionarios",
                side_effect=XanoAPIError("offline"),
            ),
        ):
            state = EmployeeStateHarness()
            await self.run_load(state)

        self.assertTrue(state.is_admin)
        self.assertEqual(state.funcionarios, [])
        self.assertIn("conexão", state.error_message)
        self.assertFalse(state.session_cleared)

    def test_employee_form_requires_name_email_and_supported_role(self):
        self.assertEqual(
            validate_funcionario_fields("", "ana@example.com", "instrutor"),
            "O nome do funcionário é obrigatório.",
        )
        self.assertEqual(
            validate_funcionario_fields("Ana", "", "instrutor"),
            "O e-mail do funcionário é obrigatório.",
        )
        self.assertEqual(
            validate_funcionario_fields("Ana", "invalid", "instrutor"),
            "Informe um e-mail válido.",
        )
        self.assertEqual(
            validate_funcionario_fields("Ana", "ana@example.com", "member"),
            "Selecione um perfil válido.",
        )
        self.assertIsNone(
            validate_funcionario_fields(
                " Ana ",
                " ana@example.com ",
                "instrutor",
            )
        )

    def test_employee_form_has_no_password_or_token_inputs(self):
        rendered = employee_form_dialog().render()
        input_props = []

        def collect_inputs(node):
            if isinstance(node, dict):
                if node.get("name") == "DebounceInput":
                    props = node.get("props")
                    if isinstance(props, list):
                        input_props.extend(props)
                for value in node.values():
                    collect_inputs(value)
            elif isinstance(node, list):
                for value in node:
                    collect_inputs(value)

        collect_inputs(rendered)
        serialized_props = " ".join(input_props).casefold()
        self.assertIn('type:"email"', serialized_props)
        self.assertNotIn('type:"password"', serialized_props)
        self.assertNotIn("token", serialized_props)


if __name__ == "__main__":
    unittest.main()
