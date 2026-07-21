from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from exceptions import ValidationError
from models.evaluation_model import (
    calculate_final_evaluation,
    get_attrition_by_location,
    get_batch_breakdown,
    get_branch_location_breakdown,
    get_distinct_locations,
    get_distinct_semesters,
    get_evaluation_dashboard_stats,
    get_filtered_students_for_eval,
    get_gender_options,
    get_location_breakdown,
    get_performance_distribution,
    get_students_by_score_range,
)
from models.student_model import get_filter_options
from schemas.dashboard import dashboard_filters_from_json, dashboard_filters_from_query
from security.access import PLANT_RESTRICTED_ROLES, assigned_plant_required, force_plant_scope


user_dashboard_bp = Blueprint('user_dashboard', __name__)


@user_dashboard_bp.route('/user_dashboard', methods=['GET'])
@login_required
def dashboard():
    filters = force_plant_scope(dashboard_filters_from_query(request.args))
    role = current_user.role

    all_locations = get_distinct_locations()
    if role in PLANT_RESTRICTED_ROLES:
        location = assigned_plant_required()
        locations = [location]
        filter_options = get_filter_options(plant_location_restriction=location)
    else:
        locations = all_locations
        filter_options = get_filter_options()

    students = get_filtered_students_for_eval(filters)
    for student in students:
        student['final_eval'] = calculate_final_evaluation(student)

    location_stats = []
    for location in get_location_breakdown(filters):
        total = location['total']
        location_stats.append({
            'location': location['location'],
            'total': total,
            'male_pct': round((location['male'] / total) * 100, 1) if total else 0,
            'female_pct': round((location['female'] / total) * 100, 1) if total else 0,
        })

    attrition_filters = dict(filters)
    attrition_filters.pop('student_status', None)
    attrition_data = []
    for row in get_attrition_by_location(attrition_filters):
        total = row['total_students']
        attrition_data.append({
            'location': row['location'],
            'attrition_pct': round((row['dropped_students'] / total) * 100, 1) if total else 0,
        })

    return render_template(
        'user_dashboard.html',
        stats=get_evaluation_dashboard_stats(filters)['summary'],
        students=students,
        filters=filters,
        filter_options=filter_options,
        sem_numbers=get_distinct_semesters(),
        genders=get_gender_options(),
        performance_data=get_performance_distribution(filters, score_type='bits'),
        location_stats=location_stats,
        attrition_data=attrition_data,
        batch_stats=get_batch_breakdown(filters),
        branch_stats=get_branch_location_breakdown(filters),
        branches=filter_options['branches'],
        functions=filter_options['functions'],
        locations=locations,
        batch_numbers=filter_options['batch_nos'],
        bits_streams=filter_options['bits_streams'],
        role=role,
        username=current_user.username,
    )


@user_dashboard_bp.route('/get-performance-data', methods=['POST'])
@login_required
def get_performance_data_api():
    data = request.get_json(silent=True)
    filters = force_plant_scope(dashboard_filters_from_json(data))
    score_type = _validated_score_type(data.get('score_type', 'all'))
    return jsonify(get_performance_distribution(filters, score_type))


@user_dashboard_bp.route('/get-students-in-range', methods=['POST'])
@login_required
def get_students_in_range_api():
    data = request.get_json(silent=True)
    filters = force_plant_scope(dashboard_filters_from_json(data))
    score_type = _validated_score_type(data.get('score_type', 'all'))
    try:
        minimum, maximum = (float(part) for part in str(data.get('range', '')).split('-', 1))
    except (TypeError, ValueError) as error:
        raise ValidationError('Invalid score range.') from error
    return jsonify(get_students_by_score_range(filters, minimum, maximum, score_type))


def _validated_score_type(value):
    if value not in {'all', 'bits', 'ojt', 'training'}:
        raise ValidationError('Invalid score type.')
    return value
