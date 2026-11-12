import json
import unittest
from unittest.mock import patch

import httpx

from academia.services.xano_client import XanoAPIError, XanoClient

_HTTPX_CLIENT = httpx.Client


class PlanEnrollmentClientTests(unittest.TestCase):
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

    def test_plan_and_enrollment_routes_and_payloads(self):
        token = "session-token"
        plan = {
            "id": 4,
            "nome": "Mensal",
            "duracao_meses": 1,
            "valor": 99.9,
            "situacao": "Ativo",
        }
        enrollment = {
            "id": 9,
            "aluno_id": 2,
            "plano_id": 4,
            "data_inicio": "2026-10-24",
            "data_termino": "2026-11-24",
        }
        plan_payload = {
            "nome": "Mensal",
            "descricao": None,
            "duracao_meses": 1,
            "valor": "99.90",
        }
        enrollment_payload = {
            "aluno_id": 2,
            "plano_id": 4,
            "data_inicio": "2026-10-24",
        }
        scenarios = [
            (
                lambda: XanoClient.get_planos(token),
                [plan],
                "GET",
                "/planos",
                None,
            ),
            (
                lambda: XanoClient.get_plano(token, 4),
                plan,
                "GET",
                "/planos/detalhes/4",
                None,
            ),
            (
                lambda: XanoClient.create_plano(token, plan_payload),
                plan,
                "POST",
                "/planos",
                plan_payload,
            ),
            (
                lambda: XanoClient.update_plano(token, 4, plan_payload),
                plan,
                "PUT",
                "/planos/atualizar/4",
                plan_payload,
            ),
            (
                lambda: XanoClient.deactivate_plano(token, 4),
                plan,
                "PATCH",
                "/planos/descontinuar/4",
                None,
            ),
            (
                lambda: XanoClient.reactivate_plano(token, 4),
                plan,
                "PATCH",
                "/planos/reativar/4",
                None,
            ),
            (
                lambda: XanoClient.get_matriculas(token),
                [enrollment],
                "GET",
                "/matriculas",
                None,
            ),
            (
                lambda: XanoClient.get_matricula(token, 9),
                enrollment,
                "GET",
                "/matriculas/detalhes/9",
                None,
            ),
            (
                lambda: XanoClient.create_matricula(token, enrollment_payload),
                enrollment,
                "POST",
                "/matriculas",
                enrollment_payload,
            ),
        ]

        for operation, response_data, method, path, payload in scenarios:
            with self.subTest(method=method, path=path):
                result, requests = self.invoke(operation, response_data)
                self.assertEqual(result, response_data)
                self.assertEqual(len(requests), 1)
                request = requests[0]
                self.assertEqual(request.method, method)
                self.assertEqual(
                    request.url.path,
                    f"/api:sGd5fzIy{path}",
                )
                if payload is not None:
                    self.assertEqual(json.loads(request.content), payload)

    def test_invalid_plan_list_shape_is_reported(self):
        with self.assertRaises(XanoAPIError):
            self.invoke(
                lambda: XanoClient.get_planos("session-token"),
                {"planos": []},
            )

    def test_enrollment_http_error_preserves_status_code(self):
        def reject(request):
            return httpx.Response(409, json={"message": "overlap"}, request=request)

        client = _HTTPX_CLIENT(transport=httpx.MockTransport(reject))
        with patch(
            "academia.services.xano_client.httpx.Client",
            return_value=client,
        ):
            with self.assertRaises(XanoAPIError) as context:
                XanoClient.create_matricula(
                    "session-token",
                    {
                        "aluno_id": 2,
                        "plano_id": 4,
                        "data_inicio": "2026-10-24",
                    },
                )

        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("overlap", str(context.exception))


if __name__ == "__main__":
    unittest.main()
