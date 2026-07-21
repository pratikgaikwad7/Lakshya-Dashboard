from flask_login import current_user
from mysql.connector import IntegrityError

from exceptions import ConflictError, NotFoundError
from models.student_model import (
    add_student,
    delete_student,
    get_all_students,
    get_filter_options,
    get_student_by_id,
    update_student,
)
from schemas.students import validate_student_payload
from security.access import assigned_plant_required, authorize_student_plant


def list_students(filters, user=None):
    user = user or current_user
    scoped_filters = dict(filters or {})
    if user.role == "SDC Coordinator":
        scoped_filters["plant_location"] = assigned_plant_required(user)
    return get_all_students(scoped_filters)


def student_filter_options(user=None):
    user = user or current_user
    restriction = assigned_plant_required(user) if user.role == "SDC Coordinator" else None
    return get_filter_options(plant_location_restriction=restriction)


def create_student(payload, user=None):
    user = user or current_user
    data = validate_student_payload(payload)
    if user.role == "SDC Coordinator":
        data["plant_location"] = assigned_plant_required(user)
    try:
        return add_student(data)
    except IntegrityError as error:
        raise ConflictError("A student with that ticket number already exists.") from error


def update_existing_student(student_id, payload, user=None):
    user = user or current_user
    student = _required_student(student_id)
    authorize_student_plant(student, user)
    data = validate_student_payload(payload)
    if user.role == "SDC Coordinator":
        data["plant_location"] = assigned_plant_required(user)
    try:
        update_student(student_id, data)
    except IntegrityError as error:
        raise ConflictError("A student with that ticket number already exists.") from error


def delete_existing_student(student_id, user=None):
    user = user or current_user
    student = _required_student(student_id)
    authorize_student_plant(student, user)
    delete_student(student_id)


def _required_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        raise NotFoundError("Student not found.")
    return student
