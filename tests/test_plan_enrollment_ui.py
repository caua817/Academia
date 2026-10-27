import unittest
from datetime import date

from academia.matriculas import validate_matricula_fields
from academia.planos import format_currency, validate_plano_fields


class PlanFormValidationTests(unittest.TestCase):
    def test_plan_requires_name_duration_and_positive_value(self):
        self.assertEqual(
            validate_plano_fields("", "1", "50"),
            "O nome do plano é obrigatório.",
        )
        self.assertEqual(
            validate_plano_fields("Plano", "0", "50"),
            "A duração do plano deve ser maior que zero.",
        )
        self.assertEqual(
            validate_plano_fields("Plano", "1.5", "50"),
            "Informe a duração do plano em meses inteiros.",
        )
        self.assertEqual(
            validate_plano_fields("Plano", "1", "0"),
            "O valor do plano deve ser maior que zero.",
        )
        self.assertIsNone(validate_plano_fields(" Plano ", "3", "129,90"))

    def test_currency_uses_brazilian_decimal_separator(self):
        self.assertEqual(format_currency(129.9), "R$ 129,90")


class EnrollmentFormValidationTests(unittest.TestCase):
    def test_enrollment_requires_selected_active_records(self):
        self.assertEqual(
            validate_matricula_fields("", "2", "2026-10-24"),
            "Selecione um aluno e um plano.",
        )
        self.assertEqual(
            validate_matricula_fields("1", "0", "2026-10-24"),
            "Selecione um aluno e um plano.",
        )

    def test_enrollment_date_must_be_valid_and_not_future(self):
        today = date(2026, 10, 24)
        self.assertEqual(
            validate_matricula_fields("1", "2", "invalid", today),
            "Informe uma data de início válida.",
        )
        self.assertEqual(
            validate_matricula_fields("1", "2", "2026-10-25", today),
            "A data de início não pode ser futura.",
        )
        self.assertIsNone(
            validate_matricula_fields("1", "2", "2026-10-24", today)
        )
        self.assertIsNone(
            validate_matricula_fields("1", "2", "2026-09-30", today)
        )


if __name__ == "__main__":
    unittest.main()
