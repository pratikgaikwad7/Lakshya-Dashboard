from flask import Blueprint, render_template, request, redirect
from mysql.connector import IntegrityError

from exceptions import ConflictError, ValidationError
from models.user_model import get_all_users, add_user, delete_user
from security.access import roles_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/users')
@roles_required('Admin')
def users_page():
    users = get_all_users()
    return render_template('users.html', users=users)


@users_bp.route('/users/add', methods=['POST'])
@roles_required('Admin')
def users_add():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', '')
    plant_location = request.form.get('plant_location') or None

    allowed_roles = {'CHRO', 'PMO', 'Corporate Skill Head', 'HR Head', 'Skill Head', 'Admin', 'SDC Coordinator'}
    if not username or not password:
        raise ValidationError('Username and password are required.')
    if role not in allowed_roles:
        raise ValidationError('Invalid user role.')

    location_roles = ['HR Head', 'Skill Head', 'SDC Coordinator']

    if role not in location_roles:
        plant_location = None

    try:
        add_user(username, password, role, plant_location)
    except IntegrityError as error:
        raise ConflictError('That username already exists.') from error

    return redirect('/users')


@users_bp.route('/users/delete/<int:id>', methods=['POST'])
@roles_required('Admin')
def users_delete(id):
    delete_user(id)

    return redirect('/users')
