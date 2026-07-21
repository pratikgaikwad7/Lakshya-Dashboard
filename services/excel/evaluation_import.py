import pandas as pd

from models.evaluation_model import bulk_upsert_evaluations
from models.student_model import get_student_ticket_id_map
from services.excel.common import WorkbookValidationError, normalize_column_name, validate_score


COLUMN_MAPPING = {
    "ticketno": "ticket_no", "employeename": "employee_name",
    "semester": "semester", "semesterstatus": "semester_status",
    "scoreattendance": "score_attendance", "scoresuggestions": "score_suggestions",
    "scoreprojects": "score_projects", "scorerecognitions": "score_recognitions",
    "scoresafety": "score_safety", "scorediscipline": "score_discipline",
    "scorebitsattendance": "score_bits_attendance", "scoreequipment": "score_equipment",
    "scoreshoptask": "score_shop_task", "scorefunctionoutput": "score_function_output",
    "trainingmarks": "training_marks", "bitscgpa": "bits_cgpa",
}
OJT_FIELDS = [
    "score_attendance", "score_suggestions", "score_projects", "score_recognitions",
    "score_safety", "score_discipline", "score_bits_attendance", "score_equipment",
    "score_shop_task", "score_function_output",
]


def import_evaluations(file, plant_location_restriction=None):
    """Validate and persist an evaluation workbook."""
    dataframe = pd.read_excel(file)
    dataframe.columns = [normalize_column_name(column) for column in dataframe.columns]
    dataframe.rename(
        columns={column: COLUMN_MAPPING[column] for column in dataframe.columns if column in COLUMN_MAPPING},
        inplace=True,
    )

    missing_columns = [column for column in ("ticket_no", "semester") if column not in dataframe.columns]
    if missing_columns:
        raise WorkbookValidationError(f"Missing required columns: {', '.join(missing_columns)}")

    ticket_map = get_student_ticket_id_map(
        plant_location=plant_location_restriction,
        active_only=True,
    )
    valid_records = []
    error_rows = []

    for index, row in dataframe.iterrows():
        row_number = index + 2
        ticket_no = str(row["ticket_no"]).strip()
        if ticket_no not in ticket_map:
            error_rows.append(_error(row_number, ticket_no, "Ticket No not found in system"))
            continue

        semester = int(row["semester"]) if pd.notna(row["semester"]) else None
        if semester is None or semester < 1 or semester > 7:
            error_rows.append(_error(row_number, ticket_no, "Semester must be 1-7"))
            continue

        raw_status = row.get("semester_status", "ongoing")
        status = str(raw_status).strip().lower() if pd.notna(raw_status) else "ongoing"
        if status not in ("ongoing", "completed"):
            error_rows.append(_error(row_number, ticket_no, "Status must be 'ongoing' or 'completed'"))
            continue

        record = {"student_id": ticket_map[ticket_no], "semester": semester, "semester_status": status}
        has_error = False
        for field in OJT_FIELDS:
            score, error = validate_score(row.get(field), 0, 10, field) if field in row else (0, None)
            if error:
                error_rows.append(_error(row_number, ticket_no, error))
                has_error = True
                break
            record[field] = score
        if has_error:
            continue

        for field, maximum in (("training_marks", 100), ("bits_cgpa", 10)):
            score, error = validate_score(row.get(field), 0, maximum, field) if field in row else (0, None)
            if error:
                error_rows.append(_error(row_number, ticket_no, error))
                has_error = True
                break
            record[field] = score
        if not has_error:
            valid_records.append(record)

    success_count = bulk_upsert_evaluations(valid_records) if valid_records else 0
    return {"success_count": success_count, "error_rows": error_rows, "total_rows": len(dataframe)}


def _error(row, ticket_no, reason):
    return {"row": row, "ticket_no": ticket_no, "reason": reason}
