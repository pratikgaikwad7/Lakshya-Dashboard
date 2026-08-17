from pathlib import Path

from flask import Blueprint, render_template, request, redirect, send_file
from flask_login import current_user, login_required

from exceptions import NotFoundError, ValidationError
from extensions import limiter
from models.evaluation_model import (
    calculate_final_evaluation,
    create_initial_evaluation,
    end_seventh_semester,
    get_distinct_semesters,
    get_filtered_students_for_eval,
    get_gender_options,
    get_student_active_evaluation,
    get_student_all_evaluations_list,
    get_student_evaluation_by_sem,
    get_student_evaluation_history,
    get_student_last_evaluation,
    promote_student_semester,
    upsert_evaluation_scores,
)
from models.student_model import get_filter_options, get_student_by_id
from schemas.evaluations import validate_evaluation_scores, validate_semester
from security.access import (
    EVALUATION_MANAGEMENT_ROLES,
    assigned_plant_required,
    authorize_student_plant,
    roles_required,
)
from services.excel.common import WorkbookValidationError
from services.excel.evaluation_import import import_evaluations


evaluations_bp = Blueprint('evaluations', __name__)


OJT_SCORE_FIELDS = (
    ('Attendance', 'score_attendance', 'fa-calendar-check'),
    ('Suggestions', 'score_suggestions', 'fa-lightbulb'),
    ('Projects', 'score_projects', 'fa-diagram-project'),
    ('Recognitions', 'score_recognitions', 'fa-award'),
    ('Safety', 'score_safety', 'fa-shield-halved'),
    ('Discipline', 'score_discipline', 'fa-user-check'),
    ('BITS Attendance', 'score_bits_attendance', 'fa-book-open-reader'),
    ('Equipment', 'score_equipment', 'fa-screwdriver-wrench'),
    ('Shop Tasks', 'score_shop_task', 'fa-list-check'),
    ('Function Output', 'score_function_output', 'fa-chart-line'),
)


@evaluations_bp.route('/evaluations')
@roles_required(*EVALUATION_MANAGEMENT_ROLES)
def list_evaluations():
    semester_status = request.args.get('semester_status')
    if semester_status is None:
        semester_status = request.args.get('status', 'ongoing')

    filters = {
        'semester': request.args.get('semester', ''),
        'semester_status': semester_status,
        'student_status': request.args.get('student_status', ''),
        'year': request.args.get('year', ''),
        'batch_no': request.args.get('batch_no', ''),
        'branch': request.args.get('branch', ''),
        'department': request.args.get('department', ''),
        'gender': request.args.get('gender', ''),
        'employee_name': request.args.get('employee_name', '').strip(),
        'ticket_no': request.args.get('ticket_no', ''),
        'function': request.args.get('function', ''),
        'bits_stream': request.args.get('bits_stream', ''),
        'plant_location': request.args.get('location', ''),
    }

    restriction = None
    if current_user.role == 'SDC Coordinator':
        restriction = assigned_plant_required()
        filters['plant_location'] = restriction

    students = get_filtered_students_for_eval(filters)
    for student in students:
        student['final_eval'] = calculate_final_evaluation(student)

    return render_template(
        'student_evaluation.html',
        students=students,
        filters=filters,
        filter_options=get_filter_options(plant_location_restriction=restriction),
        sem_numbers=get_distinct_semesters(),
        genders=get_gender_options(),
    )


@evaluations_bp.route('/evaluations/<int:student_id>', methods=['GET', 'POST'])
@roles_required(*EVALUATION_MANAGEMENT_ROLES)
def evaluation_sheet(student_id):
    _authorize_student(student_id)

    if request.method == 'POST':
        semester = validate_semester(request.form.get('semester', 1))
        scores = validate_evaluation_scores(request.form)
        success, message = upsert_evaluation_scores(student_id, semester, scores)
        if not success:
            raise ValidationError(message)
        return redirect(f'/evaluations/{student_id}?semester={semester}')

    active_evaluation = get_student_active_evaluation(student_id)
    if not active_evaluation:
        active_evaluation = get_student_last_evaluation(student_id)
        if not active_evaluation:
            create_initial_evaluation(student_id)
            active_evaluation = get_student_active_evaluation(student_id)
    if not active_evaluation:
        raise NotFoundError('Could not initialize the evaluation record.')

    active_semester = active_evaluation['semester']
    viewing_semester = validate_semester(request.args.get('semester', active_semester))
    student = get_student_evaluation_by_sem(student_id, viewing_semester)
    if not student:
        viewing_semester = active_semester
        student = get_student_evaluation_by_sem(student_id, viewing_semester)
    if not student:
        raise NotFoundError('Evaluation record not found.')

    authorize_student_plant(student)
    return render_template(
        'trainee_sheet.html',
        student=student,
        current_semester=viewing_semester,
        final_eval=calculate_final_evaluation(student),
        status=student['semester_status'],
        all_semesters=get_student_all_evaluations_list(student_id),
        is_latest_semester=viewing_semester >= active_semester,
        active_semester=active_semester,
        student_status=student.get('status', 'active'),
    )


@evaluations_bp.route('/evaluations/<int:student_id>/profile')
@login_required
def student_progress_profile(student_id):
    student = _authorize_student(student_id)
    evaluations = get_student_evaluation_history(student_id)

    for evaluation in evaluations:
        evaluation['final_eval'] = calculate_final_evaluation(evaluation)
        evaluation['ojt_metrics'] = [
            {
                'label': label,
                'value': float(evaluation.get(field) or 0),
                'icon': icon,
            }
            for label, field, icon in OJT_SCORE_FIELDS
        ]

    completed_semesters = sum(
        evaluation.get('semester_status') == 'completed'
        for evaluation in evaluations
    )
    active_evaluation = next(
        (
            evaluation
            for evaluation in reversed(evaluations)
            if evaluation.get('semester_status') == 'ongoing'
        ),
        evaluations[-1] if evaluations else None,
    )
    summary = {
        'completed_semesters': completed_semesters,
        'current_semester': active_evaluation.get('semester') if active_evaluation else 0,
    }

    return render_template(
        'student_progress_profile.html',
        student=student,
        evaluations=evaluations,
        summary=summary,
        can_manage_evaluations=current_user.role in EVALUATION_MANAGEMENT_ROLES,
    )


@evaluations_bp.route('/evaluations/<int:student_id>/promote', methods=['POST'])
@roles_required(*EVALUATION_MANAGEMENT_ROLES)
def move_next_semester(student_id):
    _authorize_student(student_id)
    success, message = promote_student_semester(student_id)
    if not success:
        raise ValidationError(message)
    return redirect(f'/evaluations/{student_id}')


@evaluations_bp.route('/evaluations/<int:student_id>/end-semester-seven', methods=['POST'])
@roles_required(*EVALUATION_MANAGEMENT_ROLES)
def end_semester_seven_route(student_id):
    _authorize_student(student_id)
    success, message = end_seventh_semester(student_id)
    if not success:
        raise ValidationError(message)
    return redirect(f'/evaluations/{student_id}')


@evaluations_bp.route('/evaluations/upload-excel', methods=['GET', 'POST'])
@roles_required(*EVALUATION_MANAGEMENT_ROLES)
@limiter.limit("10 per hour")
def upload_evaluations_excel():
    if request.method == 'GET':
        return render_template('upload_evaluations.html', success_count=None, error_rows=None)

    if 'excel_file' not in request.files or request.files['excel_file'].filename == '':
        return _upload_error('No file selected.')

    file = request.files['excel_file']
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return _upload_error('Invalid file format. Please upload .xlsx or .xls')

    restriction = assigned_plant_required() if current_user.role == 'SDC Coordinator' else None
    try:
        return render_template('upload_evaluations.html', **import_evaluations(file, restriction))
    except WorkbookValidationError as error:
        return _upload_error(str(error))


@evaluations_bp.route('/evaluations/upload-excel/template')
@roles_required(*EVALUATION_MANAGEMENT_ROLES)
def download_evaluation_template():
    template_path = Path(__file__).resolve().parents[1] / 'outputs' / 'evaluation-upload-template' / 'evaluation-upload-template.xlsx'
    return send_file(template_path, as_attachment=True, download_name='LAKSHYA-evaluation-upload-template.xlsx')


def _authorize_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        raise NotFoundError('Student not found.')
    authorize_student_plant(student)
    return student


def _upload_error(message):
    return render_template(
        'upload_evaluations.html',
        error=message,
        success_count=None,
        error_rows=None,
    ), 400
