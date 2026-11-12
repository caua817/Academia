import json
import unittest
from unittest.mock import patch

import httpx

from academia.alunos import AlunosState, filter_alunos, validate_nome
from academia.services.xano_client import XanoAPIError, XanoClient

_HTTPX_CLIENT = httpx.Client


class XanoClientTests(unittest.TestCase):
    def invoke(self, operation, response_handler):
        requests = []

        def handle(request):
            requests.append(request)
            return response_handler(request)

        client = _HTTPX_CLIENT(transport=httpx.MockTransport(handle))
        with patch(
            "academia.services.xano_client.httpx.Client",
            return_value=client,
        ):
            result = operation()
        return result, requests

    def test_list_requires_token_and_returns_list_without_sensitive_fields(self):
        aluno = {
            "id": 12,
            "nome": "Ana Lima",
            "contato": "11999990000",
            "email": "ana@example.com",
            "situacao": "Ativo",
        }
        result, requests = self.invoke(
            lambda: XanoClient.get_alunos("session-token"),
            lambda request: httpx.Response(200, json=[aluno], request=request),
        )

        self.assertEqual(result, [aluno])
        self.assertEqual(requests[0].method, "GET")
        self.assertEqual(requests[0].url.path, "/api:sGd5fzIy/alunos")
        self.assertEqual(
            requests[0].headers["Authorization"],
            "Bearer session-token",
        )
        self.assertNotIn("cpf", result[0])
        self.assertNotIn("endereco", result[0])

    def test_detail_uses_sensitive_data_endpoint_only_on_demand(self):
        aluno = {
            "id": 12,
            "nome": "Ana Lima",
            "cpf": "00000000000",
            "endereco": "Rua A",
        }
        result, requests = self.invoke(
            lambda: XanoClient.get_aluno("session-token", 12),
            lambda request: httpx.Response(200, json=aluno, request=request),
        )

        self.assertEqual(result, aluno)
        self.assertEqual(requests[0].url.path, "/api:sGd5fzIy/alunos/detalhes/12")

    def test_create_sends_empty_optional_fields_as_null(self):
        payload = {
            "nome": "Aluno Sintético",
            "cpf": None,
            "data_nascimento": None,
            "contato": None,
            "email": None,
            "endereco": None,
        }
        result, requests = self.invoke(
            lambda: XanoClient.create_aluno("session-token", payload),
            lambda request: httpx.Response(200, json={"id": 12}, request=request),
        )

        self.assertEqual(result, {"id": 12})
        self.assertEqual(requests[0].method, "POST")
        self.assertEqual(requests[0].url.path, "/api:sGd5fzIy/alunos")
        self.assertEqual(json.loads(requests[0].content), payload)

    def test_update_uses_put_and_sends_the_edited_fields(self):
        payload = {"nome": "Ana Lima", "contato": "11999990000"}
        result, requests = self.invoke(
            lambda: XanoClient.update_aluno("session-token", 12, payload),
            lambda request: httpx.Response(200, json={"id": 12}, request=request),
        )

        self.assertEqual(result, {"id": 12})
        self.assertEqual(requests[0].method, "PUT")
        self.assertEqual(requests[0].url.path, "/api:sGd5fzIy/alunos/atualizar/12")
        self.assertEqual(json.loads(requests[0].content), payload)

    def test_deactivation_uses_patch_and_never_delete(self):
        result, requests = self.invoke(
            lambda: XanoClient.deactivate_aluno("session-token", 12),
            lambda request: httpx.Response(
                200,
                json={"id": 12, "situacao": "Inativo"},
                request=request,
            ),
        )

        self.assertEqual(result["situacao"], "Inativo")
        self.assertEqual(requests[0].method, "PATCH")
        self.assertEqual(requests[0].url.path, "/api:sGd5fzIy/alunos/desativar/12")

    def test_http_error_preserves_status_code(self):
        with self.assertRaises(XanoAPIError) as context:
            self.invoke(
                lambda: XanoClient.get_alunos("session-token"),
                lambda request: httpx.Response(
                    403,
                    json={"message": "forbidden"},
                    request=request,
                ),
            )

        self.assertEqual(context.exception.status_code, 403)

    def test_connection_error_is_reported(self):
        def fail_connection(request):
            raise httpx.ConnectError("offline", request=request)

        with self.assertRaises(XanoAPIError) as context:
            self.invoke(
                lambda: XanoClient.get_alunos("session-token"),
                fail_connection,
            )

        self.assertIsNone(context.exception.status_code)

    def test_invalid_response_shape_is_reported(self):
        with self.assertRaises(XanoAPIError):
            self.invoke(
                lambda: XanoClient.get_alunos("session-token"),
                lambda request: httpx.Response(
                    200,
                    json={"alunos": []},
                    request=request,
                ),
            )

    def test_blank_token_is_rejected_without_http_request(self):
        with self.assertRaises(XanoAPIError) as context:
            XanoClient.get_alunos(" ")

        self.assertEqual(context.exception.status_code, 401)


class StudentManagementHelperTests(unittest.TestCase):
    def test_search_matches_name_or_contact_case_insensitively(self):
        alunos = [
            {"id": 1, "nome": "Ana Lima", "contato": "11999990000"},
            {"id": 2, "nome": "Bruno Reis", "email": "bruno@example.com"},
        ]

        self.assertEqual(filter_alunos(alunos, "ANA"), [alunos[0]])
        self.assertEqual(filter_alunos(alunos, "EXAMPLE.COM"), [alunos[1]])
        self.assertEqual(filter_alunos(alunos, "   "), alunos)
        self.assertEqual(filter_alunos(alunos, "sem resultado"), [])

    def test_name_is_required_after_trimming(self):
        self.assertEqual(validate_nome("   "), "O nome do aluno é obrigatório.")
        self.assertIsNone(validate_nome(" Ana Lima "))


class StudentStateHarness:
    def __init__(self):
        self.auth_token = "session-token"
        self.alunos = []
        self.is_saving = False
        self.is_editing = False
        self.aluno_id = 0
        self.is_form_open = True
        self.form_nome = "Aluno Sintético"
        self.form_cpf = ""
        self.form_data_nascimento = ""
        self.form_contato = ""
        self.form_email = ""
        self.form_endereco = ""
        self.form_error = ""
        self.success_message = ""

    async def _auth_token(self):
        return self.auth_token

    async def _clear_login(self):
        return None

    async def _reload_alunos(self, token, action):
        return False

    def _api_error_message(self, error, action):
        return AlunosState._api_error_message(self, error, action)

    def _reset_form(self):
        AlunosState._reset_form(self)


class StudentManagementStateTests(unittest.IsolatedAsyncioTestCase):
    async def run_save(self, state):
        event = AlunosState.__dict__["save_aluno"].fn
        return [result async for result in event(state)]

    async def test_save_sends_empty_optional_fields_as_null(self):
        state = StudentStateHarness()
        with patch(
            "academia.alunos.XanoClient.create_aluno",
            return_value={"id": 9},
        ) as create_aluno:
            await self.run_save(state)

        create_aluno.assert_called_once_with(
            "session-token",
            {
                "nome": "Aluno Sintético",
                "cpf": None,
                "data_nascimento": None,
                "contato": None,
                "email": None,
                "endereco": None,
            },
        )
        self.assertEqual(state.success_message, "Aluno cadastrado com sucesso.")

    async def test_blank_name_is_rejected_without_success_or_request(self):
        state = StudentStateHarness()
        state.form_nome = "  "
        state.success_message = "Aluno cadastrado com sucesso."
        with patch("academia.alunos.XanoClient.create_aluno") as create_aluno:
            await self.run_save(state)

        create_aluno.assert_not_called()
        self.assertEqual(state.form_error, "O nome do aluno é obrigatório.")
        self.assertEqual(state.success_message, "")

    async def test_http_failure_does_not_leave_success_message(self):
        state = StudentStateHarness()
        state.success_message = "Aluno cadastrado com sucesso."
        with patch(
            "academia.alunos.XanoClient.create_aluno",
            side_effect=XanoAPIError("falha sintética", 500),
        ):
            await self.run_save(state)

        self.assertIn("HTTP 500", state.form_error)
        self.assertEqual(state.success_message, "")
        self.assertTrue(state.is_form_open)
        self.assertFalse(state.is_saving)


if __name__ == "__main__":
    unittest.main()
