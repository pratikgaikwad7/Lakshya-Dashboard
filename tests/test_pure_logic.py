import datetime
import unittest

from models.evaluation_model import calculate_final_evaluation
from models.evaluations.filters import _build_filter_conditions
from models.student_model import calculate_end_date, normalize_plant_location
from services.excel.common import normalize_column_name, validate_score


class PureLogicTests(unittest.TestCase):
    def test_location_normalization_preserves_database_format(self):
        self.assertEqual(normalize_plant_location("Pune CV"), "Pune_CV")
        self.assertEqual(normalize_plant_location("Sanand PV 1"), "Sanand_PV1")
        self.assertEqual(normalize_plant_location("pune_cv"), "Pune_CV")
        self.assertIsNone(normalize_plant_location(None))

    def test_end_date_is_five_years_after_joining_date(self):
        self.assertEqual(calculate_end_date("2024-01-15"), datetime.date(2029, 1, 15))
        self.assertEqual(calculate_end_date("2024-02-29"), datetime.date(2029, 2, 28))
        self.assertIsNone(calculate_end_date(""))

    def test_final_evaluation_uses_existing_totals_and_ojt_sum(self):
        student = {
            "score_attendance": 8,
            "score_suggestions": 7,
            "score_projects": 6,
            "score_recognitions": 5,
            "score_safety": 4,
            "score_discipline": 3,
            "score_bits_attendance": 2,
            "score_equipment": 1,
            "score_shop_task": None,
            "score_function_output": 10,
            "training_marks": 80,
            "bits_cgpa": 8.5,
            "calc_training_total": 16,
            "calc_ojt_total": 23,
            "calc_bits_total": 25.5,
            "calc_grand_total": 64.5,
        }

        self.assertEqual(calculate_final_evaluation(student), {
            "training_marks": 80.0,
            "ojt_marks": 46.0,
            "bits_cgpa": 8.5,
            "training_total": 16.0,
            "ojt_total": 23.0,
            "bits_total": 25.5,
            "grand_total": 64.5,
        })

    def test_filter_builder_keeps_list_and_search_semantics(self):
        conditions, params = _build_filter_conditions({
            "semester": [1, 2],
            "plant_location": ["Pune_CV", "Sanand_PV1"],
            "ticket_no": "123",
            "grand_total_min": 60,
        })

        self.assertIn("e.semester IN (%s,%s)", conditions)
        self.assertIn("s.plant_location IN (%s,%s)", conditions)
        self.assertIn("s.ticket_no LIKE %s", conditions)
        self.assertIn("e.calc_grand_total >= %s", conditions)
        self.assertEqual(params, [1, 2, "%123%", "Pune_CV", "Sanand_PV1", 60])

    def test_excel_helpers_keep_flexible_columns_and_score_limits(self):
        self.assertEqual(normalize_column_name(" Score_Bits Attendance "), "scorebitsattendance")
        self.assertEqual(validate_score(10, 0, 10, "score")[0], 10.0)
        self.assertEqual(validate_score(11, 0, 10, "score"), (None, "score must be 0-10"))


if __name__ == "__main__":
    unittest.main()
