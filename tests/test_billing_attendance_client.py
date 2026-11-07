import json
import unittest
from unittest.mock import patch

import httpx

from academia.services.xano_client import XanoAPIError, XanoClient

_HTTPX_CLIENT = httpx.Client


class BillingAttendanceClientTests(unittest.TestCase):
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

    def test_list_routes_and_response_shapes(self):
        monthly = {
            "id": 3,
            "matricula_id": 8,
            "aluno_nome": "Aluno",
            "competencia": "2026-10-01",
            "data_vencimento": "2026-10-10",
            "valor": 120,
            "situacao": "Pendente",
        }
        payment = {
            "id": 4,
            "mensalidade_id": 3,
            "aluno_nome": "Aluno",
            "competencia": "2026-10-01",
            "valor": 120,
            "forma_pagamento": "PIX",
            "data_pagamento": "2026-10-10",
            "registrado_por": 1,
            "situacao": "Registrado",
        }
        checkin_student = {"id": 7, "nome": "Aluno"}
        checkin = {
            "id": 9,
            "aluno_id": 7,
            "aluno_nome": "Aluno",
            "matricula_id": 8,
            "data_hora": "2026-10-10T12:00:00Z",
            "registrado_por": 1,
            "usuario_nome": "Admin",
        }
        scenarios = [
            (
                lambda: XanoClient.get_mensalidades("session-token"),
                [monthly],
                "/mensalidades",
            ),
            (
                lambda: XanoClient.get_pagamentos("session-token"),
                [payment],
                "/pagamentos",
            ),
            (
                lambda: XanoClient.get_checkin_alunos("session-token"),
                [checkin_student],
                "/checkins/alunos",
            ),
            (
                lambda: XanoClient.get_checkins("session-token"),
                [checkin],
                "/checkins",
            ),
        ]

        for operation, response_data, path in scenarios:
            with self.subTest(path=path):
                result, requests = self.invoke(operation, response_data)
                self.assertEqual(result, response_data)
                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0].method, "GET")
                self.assertEqual(
                    requests[0].url.path,
                    f"/api:sGd5fzIy{path}",
                )

    def test_write_routes_and_payloads(self):
        payment_payload = {
            "mensalidade_id": 3,
            "valor": 120.0,
            "forma_pagamento": "PIX",
        }
        payment_response = {
            "id": 4,
            "mensalidade_id": 3,
            "valor": 120,
            "forma_pagamento": "PIX",
            "data_pagamento": "2026-10-10T12:00:00Z",
            "registrado_por": 1,
            "situacao": "Registrado",
        }
        correction_payload = {
            "tipo_correcao": "Cancelado",
            "motivo": "Lançamento duplicado",
        }
        correction_response = {
            "id": 4,
            "mensalidade_id": 3,
            "situacao": "Cancelado",
            "tipo_correcao": "Cancelado",
            "motivo_correcao": "Lançamento duplicado",
            "corrigido_em": "2026-10-10T12:00:00Z",
            "corrigido_por": 1,
        }
        checkin_payload = {"aluno_id": 7}
        checkin_response = {
            "id": 9,
            "aluno_id": 7,
            "matricula_id": 8,
            "data_hora": "2026-10-10T12:00:00Z",
            "registrado_por": 1,
        }
        scenarios = [
            (
                lambda: XanoClient.create_pagamento(
                    "session-token",
                    payment_payload,
                ),
                payment_response,
                "POST",
                "/pagamentos",
                payment_payload,
            ),
            (
                lambda: XanoClient.correct_pagamento(
                    "session-token",
                    4,
                    correction_payload,
                ),
                correction_response,
                "PATCH",
                "/pagamentos/corrigir/4",
                correction_payload,
            ),
            (
                lambda: XanoClient.create_checkin(
                    "session-token",
                    checkin_payload,
                ),
                checkin_response,
                "POST",
                "/checkins",
                checkin_payload,
            ),
        ]

        for operation, response_data, method, path, payload in scenarios:
            with self.subTest(path=path):
                result, requests = self.invoke(operation, response_data)
                self.assertEqual(result, response_data)
                self.assertEqual(len(requests), 1)
                request = requests[0]
                self.assertEqual(request.method, method)
                self.assertEqual(
                    request.url.path,
                    f"/api:sGd5fzIy{path}",
                )
                self.assertEqual(json.loads(request.content), payload)

    def test_incomplete_response_and_invalid_payload_are_reported(self):
        with self.assertRaises(XanoAPIError):
            self.invoke(
                lambda: XanoClient.get_mensalidades("session-token"),
                [{"id": 1}],
            )

        with self.assertRaises(XanoAPIError):
            XanoClient.create_checkin(
                "session-token",
                {"aluno_id": 7, "registrado_por": 1},
            )

    def test_http_error_preserves_status_and_api_message(self):
        def reject(request):
            return httpx.Response(
                409,
                json={"message": "mensalidade já paga"},
                request=request,
            )

        client = _HTTPX_CLIENT(transport=httpx.MockTransport(reject))
        with patch(
            "academia.services.xano_client.httpx.Client",
            return_value=client,
        ):
            with self.assertRaises(XanoAPIError) as context:
                XanoClient.create_pagamento(
                    "session-token",
                    {
                        "mensalidade_id": 3,
                        "valor": 120,
                        "forma_pagamento": "PIX",
                    },
                )

        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("mensalidade já paga", str(context.exception))


if __name__ == "__main__":
    unittest.main()
