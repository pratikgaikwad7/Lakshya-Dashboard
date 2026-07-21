import logging

import pandas as pd

from models.db import get_db_connection
from models.student_model import add_student, normalize_plant_location
from services.excel.common import WorkbookValidationError, normalize_column_name


REQUIRED_COLUMNS = ["Full Name", "Ticket No", "Gender"]
logger = logging.getLogger(__name__)


def import_students(file, plant_location_restriction=None, enforce_plant_restriction=False):
    """Import a student workbook and return the existing API result payload."""
    dataframe = pd.read_excel(file)
    dataframe.columns = dataframe.columns.str.strip()
    column_map = {normalize_column_name(column): column for column in dataframe.columns}

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if normalize_column_name(column) not in column_map
    ]
    if missing_columns:
        raise WorkbookValidationError(f"Missing required columns: {', '.join(missing_columns)}")

    def get_value(row, standard_name):
        actual_name = column_map.get(normalize_column_name(standard_name))
        return row.get(actual_name) if actual_name else None

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ticket_no FROM students")
    existing_tickets = {row[0] for row in cursor.fetchall()}
    connection.close()

    inserted_count = 0
    skipped_count = 0
    failed_rows = []

    for index, row in dataframe.iterrows():
        row_number = index + 2
        missing_fields = [
            field for field in REQUIRED_COLUMNS
            if pd.isna(get_value(row, field)) or str(get_value(row, field)).strip() == ""
        ]
        if missing_fields:
            failed_rows.append(f"Row {row_number}: Missing fields - {', '.join(missing_fields)}")
            continue

        ticket_no = str(get_value(row, "Ticket No")).strip()
        if ticket_no in existing_tickets:
            skipped_count += 1
            continue

        name_parts = str(get_value(row, "Full Name")).strip().split()
        if not name_parts:
            failed_rows.append(f"Row {row_number}: Full Name is empty.")
            continue

        first_name = name_parts[0]
        surname = name_parts[-1] if len(name_parts) > 1 else ""
        middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""

        joining_date = get_value(row, "Date of Joining")
        formatted_joining_date = None
        if pd.notna(joining_date):
            try:
                formatted_joining_date = pd.to_datetime(joining_date).strftime("%Y-%m-%d")
            except Exception:
                pass

        raw_status = get_value(row, "Status")
        status = str(raw_status).strip().lower() if pd.notna(raw_status) else "active"
        raw_location = get_value(row, "Plant Location")
        location = normalize_plant_location(raw_location)

        payload = {
            "first_name": first_name,
            "middle_name": middle_name,
            "surname": surname,
            "ticket_no": ticket_no,
            "gender": str(get_value(row, "Gender")).strip(),
            "mobile_no": str(get_value(row, "Mobile No")).strip(),
            "email": _optional_text(get_value(row, "Email")),
            "diploma_branch": _optional_text(get_value(row, "Diploma Branch")),
            "department": _optional_text(get_value(row, "Department")),
            "bc_no": _optional_text(get_value(row, "BC No")),
            "reporting_manager": _optional_text(get_value(row, "Reporting Manager")),
            "function": _optional_text(get_value(row, "Function")),
            "date_of_joining": formatted_joining_date,
            "plant_location": location,
            "batch_year": _optional_int(get_value(row, "Batch Year")),
            "batch_no": _optional_int(get_value(row, "Batch No")),
            "status": status,
            "bits_stream": _optional_text(get_value(row, "Bits Stream")),
        }

        if enforce_plant_restriction:
            if payload["plant_location"] and payload["plant_location"] != plant_location_restriction:
                failed_rows.append(
                    f"Row {row_number}: Location mismatch. You cannot add students for "
                    f"{payload['plant_location']}."
                )
                continue
            payload["plant_location"] = plant_location_restriction

        try:
            add_student(payload)
            inserted_count += 1
            existing_tickets.add(ticket_no)
        except Exception as error:
            logger.exception("Student import failed at workbook row %s", row_number)
            failed_rows.append(f"Row {row_number}: Database operation failed.")

    return {
        "message": "Upload processed",
        "total_rows": len(dataframe),
        "inserted": inserted_count,
        "skipped": skipped_count,
        "failed": len(failed_rows),
        "errors": failed_rows,
    }


def _optional_text(value):
    return str(value).strip() if pd.notna(value) else None


def _optional_int(value):
    return int(value) if pd.notna(value) else None
