import json
import unittest
from unittest.mock import patch

import httpx

from academia.services.xano_client import XanoAPIError, XanoClient

_HTTPX_CLIENT = httpx.Client
API_PREFIX = "/api:sGd5fzIy"


class OperationClientTests(unittest.TestCase):
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

    def test_modality_routes_and_payloads(self):
        modality = {
            "id": 2,
            "nome": "Funcional",
            "descricao": None,
            "situacao": "Ativo",
        }
        payload = {"nome": "Funcional", "descricao": None}
        calls = [
            (lambda: XanoClient.get_modalidades("token"), [modality], "GET", "/modalidades", None),
            (
                lambda: XanoClient.create_modalidade("token", payload),
                modality,
                "POST",
                "/modalidades",
                payload,
            ),
            (
                lambda: XanoClient.update_modalidade("token", 2, payload),
                modality,
                "PUT",
                "/modalidades/atualizar/2",
                payload,
            ),
            (
                lambda: XanoClient.deactivate_modalidade("token", 2),
                {**modality, "situacao": "Inativo"},
                "PATCH",
                "/modalidades/desativar/2",
                None,
            ),
        ]
        self._assert_calls(calls)

    def test_session_routes_query_and_payloads(self):
        session = {
            "id": 4,
            "modalidade_id": 2,
            "modalidade_nome": "Funcional",
            "instrutor_id": 7,
            "instrutor_nome": "Instrutor",
            "inicio": "2026-12-01T12:00:00Z",
            "termino": "2026-12-01T13:00:00Z",
            "capacidade": 12,
            "ocupacao": 3,
            "situacao": "Agendada",
        }
        write_response = {
            key: session[key]
            for key in (
                "id",
                "modalidade_id",
                "instrutor_id",
                "inicio",
                "termino",
                "capacidade",
                "situacao",
            )
        }
        payload = {
            "modalidade_id": 2,
            "instrutor_id": 7,
            "inicio": "2026-12-01T12:00:00Z",
            "termino": "2026-12-01T13:00:00Z",
            "capacidade": 12,
            "local": "Sala 1",
        }
        calls = [
            (
                lambda: XanoClient.get_sessoes(
                    "token",
                    "2026-12-01",
                    "2026-12-31",
                ),
                [session],
                "GET",
                "/sessoes",
                None,
            ),
            (
                lambda: XanoClient.create_sessao("token", payload),
                write_response,
                "POST",
                "/sessoes",
                payload,
            ),
            (
                lambda: XanoClient.update_sessao("token", 4, payload),
                write_response,
                "PUT",
                "/sessoes/atualizar/4",
                payload,
            ),
            (
                lambda: XanoClient.cancel_sessao("token", 4),
                {"id": 4, "situacao": "Cancelada"},
                "PATCH",
                "/sessoes/cancelar/4",
                None,
            ),
        ]
        self._assert_calls(calls)

        _, requests = self.invoke(
            lambda: XanoClient.get_sessoes(
                "token",
                "2026-12-01",
                "2026-12-31",
            ),
            [session],
        )
        self.assertEqual(
            dict(requests[0].url.params),
            {"data_inicio": "2026-12-01", "data_fim": "2026-12-31"},
        )

    def test_reservation_routes_and_nested_response(self):
        summary = {
            "sessao_aula_id": 4,
            "capacidade": 12,
            "ocupacao": 2,
            "vagas_disponiveis": 10,
            "reservas": [
                {
                    "id": 10,
                    "sessao_aula_id": 4,
                    "aluno_id": 5,
                    "aluno_nome": "Aluno",
                    "situacao": "Confirmada",
                    "reservado_em": "2026-11-12T12:00:00Z",
                }
            ],
        }
        reservation = {
            "id": 10,
            "sessao_aula_id": 4,
            "aluno_id": 5,
            "situacao": "Confirmada",
            "reservado_em": "2026-11-12T12:00:00Z",
        }
        payload = {"sessao_aula_id": 4, "aluno_id": 5}
        calls = [
            (
                lambda: XanoClient.get_reservas("token", 4),
                summary,
                "GET",
                "/reservas/4",
                None,
            ),
            (
                lambda: XanoClient.create_reserva("token", payload),
                reservation,
                "POST",
                "/reservas",
                payload,
            ),
            (
                lambda: XanoClient.cancel_reserva("token", 10),
                {**reservation, "situacao": "Cancelada"},
                "PATCH",
                "/reservas/cancelar/10",
                None,
            ),
            (
                lambda: XanoClient.set_reserva_resultado("token", 10, "Presente"),
                {**reservation, "situacao": "Presente"},
                "PATCH",
                "/reservas/resultado/10",
                {"resultado": "Presente"},
            ),
        ]
        self._assert_calls(calls)

    def test_report_query_shape_and_aggregate_only_fields(self):
        report = {
            "data_inicio": "2026-11-01",
            "data_fim": "2026-11-30",
            "matriculas_ativas": 8,
            "pagamentos_quantidade": 3,
            "pagamentos_valor": 300.0,
            "mensalidades_atrasadas_quantidade": 2,
            "mensalidades_atrasadas_valor": 200.0,
            "checkins_quantidade": 9,
            "sessoes_quantidade": 4,
            "capacidade_total": 40,
            "reservas_nao_canceladas": 13,
            "ocupacao_percentual": 32.5,
        }
        result, requests = self.invoke(
            lambda: XanoClient.get_relatorio_operacao(
                "token",
                "2026-11-01",
                "2026-11-30",
            ),
            report,
        )
        self.assertEqual(result, report)
        self.assertEqual(requests[0].method, "GET")
        self.assertEqual(
            requests[0].url.path,
            f"{API_PREFIX}/relatorios/operacao",
        )
        self.assertEqual(
            dict(requests[0].url.params),
            {"data_inicio": "2026-11-01", "data_fim": "2026-11-30"},
        )

        with self.assertRaises(XanoAPIError):
            self.invoke(
                lambda: XanoClient.get_relatorio_operacao(
                    "token",
                    "2026-11-01",
                    "2026-11-30",
                ),
                {**report, "aluno_nome": "Não deve ser retornado"},
            )

    def test_invalid_payloads_and_incomplete_responses_are_rejected(self):
        with self.assertRaises(XanoAPIError):
            XanoClient.create_modalidade(
                "token",
                {"nome": "Funcional", "descricao": None, "situacao": "Ativo"},
            )
        with self.assertRaises(XanoAPIError):
            XanoClient.create_reserva(
                "token",
                {"sessao_aula_id": 4, "aluno_id": 5, "aluno_nome": "Aluno"},
            )
        with self.assertRaises(XanoAPIError):
            self.invoke(
                lambda: XanoClient.get_modalidades("token"),
                {"modalidades": []},
            )

    def test_http_errors_preserve_status_code(self):
        for status_code in (401, 403, 409):
            def reject(request):
                return httpx.Response(
                    status_code,
                    json={"message": "request rejected"},
                    request=request,
                )

            client = _HTTPX_CLIENT(transport=httpx.MockTransport(reject))
            with self.subTest(status=status_code):
                with patch(
                    "academia.services.xano_client.httpx.Client",
                    return_value=client,
                ):
                    with self.assertRaises(XanoAPIError) as context:
                        XanoClient.get_modalidades("token")
                self.assertEqual(context.exception.status_code, status_code)

    def _assert_calls(self, calls):
        for operation, response_data, method, path, payload in calls:
            with self.subTest(path=path):
                result, requests = self.invoke(operation, response_data)
                self.assertEqual(result, response_data)
                self.assertEqual(len(requests), 1)
                request = requests[0]
                self.assertEqual(request.method, method)
                self.assertEqual(request.url.path, f"{API_PREFIX}{path}")
                if payload is not None:
                    self.assertEqual(json.loads(request.content), payload)


if __name__ == "__main__":
    unittest.main()
