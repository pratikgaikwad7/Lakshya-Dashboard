from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user

from extensions import limiter
from security.access import STUDENT_MANAGEMENT_ROLES, assigned_plant_required, roles_required
from services.excel.student_import import import_students
from services.student_service import (
    create_student,
    delete_existing_student,
    list_students,
    student_filter_options,
    update_existing_student,
)


students_bp = Blueprint('students', __name__)


@students_bp.route('/students')
@roles_required(*STUDENT_MANAGEMENT_ROLES)
def index():
    if current_user.role == 'SDC Coordinator':
        assigned_plant_required()
    return render_template('students.html')


@students_bp.route('/api/students/filters', methods=['GET'])
@roles_required(*STUDENT_MANAGEMENT_ROLES)
def api_get_filters():
    return jsonify(student_filter_options())


@students_bp.route('/api/students', methods=['GET'])
@roles_required(*STUDENT_MANAGEMENT_ROLES)
def api_get_students():
    filters = {
        'plant_location': request.args.get('location'),
        'year': request.args.get('year'),
        'department': request.args.get('department'),
        'batch_no': request.args.get('batch_no'),
        'function': request.args.get('function'),
        'bits_stream': request.args.get('bits_stream'),
        'student_status': request.args.get('student_status'),
    }
    return jsonify(list_students({key: value for key, value in filters.items() if value}))


@students_bp.route('/api/students', methods=['POST'])
@roles_required(*STUDENT_MANAGEMENT_ROLES)
def api_add_student():
    student_id = create_student(request.get_json(silent=True))
    return jsonify({'success': True, 'id': student_id}), 201


@students_bp.route('/api/students/<int:student_id>', methods=['PUT'])
@roles_required(*STUDENT_MANAGEMENT_ROLES)
def api_update_student(student_id):
    update_existing_student(student_id, request.get_json(silent=True))
    return jsonify({'success': True}), 200


@students_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
@roles_required(*STUDENT_MANAGEMENT_ROLES)
def api_delete_student(student_id):
    delete_existing_student(student_id)
    return jsonify({'success': True}), 200


@students_bp.route('/api/students/upload-excel', methods=['POST'])
@roles_required(*STUDENT_MANAGEMENT_ROLES)
@limiter.limit("10 per hour")
def upload_excel():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'No file selected.', 'code': 'validation_error'}), 400

    file = request.files['file']
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Invalid file type. Only .xlsx or .xls allowed.', 'code': 'validation_error'}), 400

    is_coordinator = current_user.role == 'SDC Coordinator'
    restriction = assigned_plant_required() if is_coordinator else None
    return jsonify(import_students(
        file,
        plant_location_restriction=restriction,
        enforce_plant_restriction=is_coordinator,
    )), 200
