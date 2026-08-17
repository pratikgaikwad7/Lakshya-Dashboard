import datetime
import unittest
from unittest.mock import patch

from app import create_app
from config import TestingConfig
from models.user_model import User


class StudentProgressProfileTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.admin = User({
            "id": 1,
            "username": "admin",
            "role": "Admin",
            "plant_location": None,
        })
        self.student = {
            "id": 7,
            "email": "trainee@example.com",
            "employee_name": "Asha Patil",
            "ticket_no": "T-007",
            "diploma_branch": "Mechanical",
            "gender": "Female",
            "mobile_no": "9999999999",
            "department": "Manufacturing",
            "bc_no": "BC-7",
            "reporting_manager": "R. Manager",
            "function": "Production",
            "plant_location": "Pune_CV",
            "batch_year": 2025,
            "batch_no": 3,
            "status": "active",
            "bits_stream": "Manufacturing Systems",
            "date_of_joining": datetime.date(2025, 7, 1),
            "end_date": datetime.date(2029, 6, 30),
        }

    def authenticated_get(self, history, user=None):
        user = user or self.admin
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user.id)
            session["_fresh"] = True

        with (
            patch("models.user_model.get_user_by_id", return_value=user),
            patch("routes.evaluations.get_student_by_id", return_value=self.student),
            patch(
                "routes.evaluations.get_student_evaluation_history",
                return_value=history,
            ),
        ):
            return self.client.get("/evaluations/7/profile")

    def test_authenticated_non_evaluator_can_view_profile_but_not_evaluation_sheet(self):
        viewer = User({
            "id": 2,
            "username": "viewer",
            "role": "HR Head",
            "plant_location": "Pune_CV",
        })
        history = [{
            "id": 11,
            "student_id": 7,
            "semester": 1,
            "semester_status": "completed",
            "score_attendance": 8,
            "score_suggestions": 7,
            "score_projects": 9,
            "score_recognitions": 8,
            "score_safety": 9,
            "score_discipline": 8,
            "score_bits_attendance": 7,
            "score_equipment": 8,
            "score_shop_task": 9,
            "score_function_output": 7,
            "training_marks": 82,
            "bits_cgpa": 8.4,
            "updated_at": datetime.datetime(2026, 7, 1, 9, 30),
        }]

        profile_response = self.authenticated_get(history, viewer)
        profile_html = profile_response.get_data(as_text=True)
        self.assertEqual(profile_response.status_code, 200)
        self.assertIn("Asha Patil", profile_html)
        self.assertIn("Read-only semester record", profile_html)
        self.assertNotIn("Open evaluation", profile_html)
        self.assertNotIn("View evaluation sheet", profile_html)

        with patch("models.user_model.get_user_by_id", return_value=viewer):
            sheet_response = self.client.get("/evaluations/7?semester=1")
        self.assertEqual(sheet_response.status_code, 403)

    def test_profile_renders_semester_history_and_weighted_scores(self):
        response = self.authenticated_get([
            {
                "id": 11,
                "student_id": 7,
                "semester": 1,
                "semester_status": "completed",
                "score_attendance": 8,
                "score_suggestions": 7,
                "score_projects": 9,
                "score_recognitions": 8,
                "score_safety": 9,
                "score_discipline": 8,
                "score_bits_attendance": 7,
                "score_equipment": 8,
                "score_shop_task": 9,
                "score_function_output": 7,
                "training_marks": 82,
                "bits_cgpa": 8.4,
                "calc_training_total": 16.4,
                "calc_ojt_total": 40,
                "calc_bits_total": 25.2,
                "calc_grand_total": 81.6,
                "updated_at": datetime.datetime(2026, 7, 1, 9, 30),
            },
            {
                "id": 12,
                "student_id": 7,
                "semester": 2,
                "semester_status": "ongoing",
                "score_attendance": 0,
                "score_suggestions": 0,
                "score_projects": 0,
                "score_recognitions": 0,
                "score_safety": 0,
                "score_discipline": 0,
                "score_bits_attendance": 0,
                "score_equipment": 0,
                "score_shop_task": 0,
                "score_function_output": 0,
                "training_marks": 0,
                "bits_cgpa": 0,
                "calc_training_total": 0,
                "calc_ojt_total": 0,
                "calc_bits_total": 0,
                "calc_grand_total": 0,
                "updated_at": datetime.datetime(2026, 7, 20, 11, 0),
            },
        ])

        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Asha Patil", html)
        self.assertIn("Complete performance record", html)
        self.assertIn("Semester 1", html)
        self.assertIn("Semester 2", html)
        self.assertIn("81.6", html)
        self.assertIn("View evaluation sheet", html)
        self.assertIn('data-semester-target="semester-2"', html)
        self.assertIn("student-progress-profile.js", html)

    def test_profile_handles_student_without_semester_records(self):
        response = self.authenticated_get([])

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "No semester records have been created for this trainee.",
            response.get_data(as_text=True),
        )


if __name__ == "__main__":
    unittest.main()
