from unittest import TestCase
from unittest.mock import Mock, patch

import pandas as pd

from services.excel.student_import import import_students


class StudentImportTests(TestCase):
    @patch("services.excel.student_import.update_student")
    @patch("services.excel.student_import.add_student", return_value=22)
    @patch("services.excel.student_import.get_db_connection")
    @patch("services.excel.student_import.pd.read_excel")
    def test_same_ticket_number_updates_existing_student(
        self, read_excel, get_db_connection, add_student, update_student
    ):
        read_excel.return_value = pd.DataFrame([
            {"Full Name": "Existing Student", "Ticket No": "T-100", "Gender": "Male"},
            {"Full Name": "New Student", "Ticket No": "T-200", "Gender": "Female"},
        ])
        cursor = Mock()
        cursor.fetchall.return_value = [(11, "T-100", "Pune")]
        connection = Mock()
        connection.cursor.return_value = cursor
        get_db_connection.return_value = connection

        result = import_students(Mock())

        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["skipped"], 0)
        update_student.assert_called_once()
        self.assertEqual(update_student.call_args.args[0], 11)
        self.assertEqual(update_student.call_args.args[1]["ticket_no"], "T-100")
        add_student.assert_called_once()
        self.assertEqual(add_student.call_args.args[0]["ticket_no"], "T-200")
