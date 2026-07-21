from exceptions import ValidationError
from schemas.common import require_mapping


ALLOWED_STUDENT_STATUSES = {"active", "dropped", "completed"}


def validate_student_payload(payload):
    data = dict(require_mapping(payload))
    for field in ("first_name", "ticket_no", "gender"):
        value = data.get(field)
        if value is None or not str(value).strip():
            raise ValidationError(f"{field.replace('_', ' ').title()} is required.")
        data[field] = str(value).strip()

    for field in ("middle_name", "surname", "mobile_no"):
        data[field] = str(data.get(field) or "").strip()

    status = str(data.get("status") or "active").strip().lower()
    if status not in ALLOWED_STUDENT_STATUSES:
        raise ValidationError("Status must be active, dropped, or completed.")
    data["status"] = status

    for field in ("batch_year", "batch_no"):
        value = data.get(field)
        if value in (None, ""):
            data[field] = None
            continue
        try:
            data[field] = int(value)
        except (TypeError, ValueError) as error:
            raise ValidationError(f"{field.replace('_', ' ').title()} must be a number.") from error

    return data
