import pandas as pd

from exceptions import ValidationError


class WorkbookValidationError(ValidationError):
    """Raised when an uploaded workbook does not match the required format."""


def normalize_column_name(name):
    """Return the case/spacing-insensitive key used by existing imports."""
    return str(name).strip().lower().replace(" ", "").replace("_", "")


def safe_float(value, default=0.0):
    try:
        return float(value) if pd.notna(value) else default
    except Exception:
        return default


def validate_score(value, minimum, maximum, field_name):
    score = safe_float(value, 0)
    if score < minimum or score > maximum:
        return None, f"{field_name} must be {minimum}-{maximum}"
    return score, None
