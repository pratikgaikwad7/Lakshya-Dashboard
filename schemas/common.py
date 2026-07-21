from exceptions import ValidationError


def ensure_list(value):
    if isinstance(value, list):
        return [item for item in value if item not in (None, "")]
    if value not in (None, ""):
        return [value]
    return []


def require_mapping(value, message="A JSON object is required."):
    if not isinstance(value, dict):
        raise ValidationError(message)
    return value
