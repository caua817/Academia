import json
import unittest
from unittest.mock import patch

import httpx

from academia.alunos import filter_alunos, validate_nome
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

    def test_create_uses_post_and_sends_the_new_fields(self):
        payload = {"nome": "Ana Lima", "cpf": None}
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


if __name__ == "__main__":
    unittest.main()
