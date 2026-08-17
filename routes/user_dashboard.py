from datetime import date

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
from models.student_model import get_all_students, get_filter_options
from schemas.dashboard import dashboard_filters_from_json, dashboard_filters_from_query
from security.access import PLANT_RESTRICTED_ROLES, assigned_plant_required, force_plant_scope


user_dashboard_bp = Blueprint('user_dashboard', __name__)


@user_dashboard_bp.route('/user_dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('user_dashboard.html', **_dashboard_context())


@user_dashboard_bp.route('/batches/<int:batch_year>/students', methods=['GET'])
@login_required
def batch_students(batch_year):
    return _student_records(batch_year=batch_year)


@user_dashboard_bp.route('/dashboard/student-records', methods=['GET'])
@login_required
def dashboard_student_records():
    return _student_records()


def _student_records(batch_year=None):
    role = current_user.role
    plant_restriction = assigned_plant_required() if role in PLANT_RESTRICTED_ROLES else None
    options = get_filter_options(plant_location_restriction=plant_restriction)
    selected_plant = plant_restriction or request.args.get('plant_location', '')
    selected_status = request.args.get('student_status') if 'student_status' in request.args else 'active'
    filters = {
        'year': batch_year or request.args.get('year') or None,
        'plant_location': selected_plant or None,
        'department': request.args.get('department') or None,
        'function': request.args.get('function') or None,
        'bits_stream': request.args.get('bits_stream') or None,
        'student_status': selected_status or None,
        'employee_name': request.args.get('employee_name') or None,
        'ticket_no': request.args.get('ticket_no') or None,
        'branch': request.args.get('branch') or None,
        'gender': request.args.get('gender') or None,
    }
    students = get_all_students({key: value for key, value in filters.items() if value is not None})
    summary = {
        'total': len(students),
        'male': sum(str(student.get('gender', '')).lower() == 'male' for student in students),
        'female': sum(str(student.get('gender', '')).lower() == 'female' for student in students),
        'active': sum(student.get('status') == 'active' for student in students),
        'completed': sum(student.get('status') == 'completed' for student in students),
        'dropped': sum(student.get('status') == 'dropped' for student in students),
    }
    return render_template(
        'batch_students.html',
        batch_year=batch_year,
        students=students,
        summary=summary,
        filters=filters,
        options=options,
        role=role,
    )


def _dashboard_context():
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
            'dropped_count': row['dropped_students'],
            'attrition_pct': round((row['dropped_students'] / total) * 100, 1) if total else 0,
        })

    historical_filters = dict(filters)
    historical_filters.pop('student_status', None)
    today = date.today()
    all_student_summary = get_evaluation_dashboard_stats(historical_filters)['summary']
    active_summary_filters = dict(historical_filters, student_status=['active'])
    dropped_summary_filters = dict(historical_filters, student_status=['dropped'])
    active_student_summary = get_evaluation_dashboard_stats(active_summary_filters)['summary']
    dropped_student_summary = get_evaluation_dashboard_stats(dropped_summary_filters)['summary']

    return dict(
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
        batch_history_stats=get_batch_breakdown(historical_filters),
        current_academic_year=today.year if today.month >= 4 else today.year - 1,
        overview_stats={
            'total': all_student_summary['total'],
            'active': active_student_summary['total'],
            'dropped': dropped_student_summary['total'],
            'male': active_student_summary['male'],
            'female': active_student_summary['female'],
        },
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
