"""Backward-compatible student model API."""

from models.students.helpers import calculate_end_date, normalize_plant_location
from models.students.repository import (
    add_student,
    delete_student,
    get_all_students,
    get_dashboard_stats,
    get_filter_options,
    get_student_by_id,
    get_student_ticket_id_map,
    update_student,
)
from models.students.schema import check_and_update_completion_status, init_db

__all__ = [
    "add_student", "calculate_end_date", "check_and_update_completion_status",
    "delete_student", "get_all_students", "get_dashboard_stats",
    "get_filter_options", "get_student_by_id", "get_student_ticket_id_map", "init_db",
    "normalize_plant_location", "update_student",
]
