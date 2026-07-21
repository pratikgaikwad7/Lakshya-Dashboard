from exceptions import ValidationError


OJT_FIELDS = (
    'score_attendance', 'score_suggestions', 'score_projects', 'score_recognitions',
    'score_safety', 'score_discipline', 'score_bits_attendance', 'score_equipment',
    'score_shop_task', 'score_function_output',
)


def validate_evaluation_scores(data):
    values = {}
    for field in OJT_FIELDS:
        values[field] = _number_in_range(data.get(field, 0), 0, 10, field)
    values['training_marks'] = _number_in_range(data.get('training_marks', 0), 0, 100, 'training_marks')
    values['bits_cgpa'] = _number_in_range(data.get('bits_cgpa', 0), 0, 10, 'bits_cgpa')
    return values


def validate_semester(value):
    try:
        semester = int(value)
    except (TypeError, ValueError) as error:
        raise ValidationError('Semester must be a number from 1 to 7.') from error
    if semester < 1 or semester > 7:
        raise ValidationError('Semester must be from 1 to 7.')
    return semester


def _number_in_range(value, minimum, maximum, field):
    try:
        number = float(value or 0)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"{field} must be a number.") from error
    if number < minimum or number > maximum:
        raise ValidationError(f"{field} must be between {minimum} and {maximum}.")
    return number
