from flask import Blueprint, flash, redirect, render_template, request
from flask_login import current_user
from mysql.connector import IntegrityError

from exceptions import ConflictError, ValidationError
from models.user_model import add_user, delete_user, get_all_users, update_user_credentials
from security.access import roles_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/users')
@roles_required('Admin')
def users_page():
    users = get_all_users()
    return render_template('users.html', users=users, current_user_id=current_user.id)


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
    if len(username) > 255:
        raise ValidationError('Username must be 255 characters or fewer.')
    if len(password) < 8:
        raise ValidationError('Password must contain at least 8 characters.')
    if role not in allowed_roles:
        raise ValidationError('Invalid user role.')

    location_roles = ['HR Head', 'Skill Head', 'SDC Coordinator']

    if role not in location_roles:
        plant_location = None

    try:
        add_user(username, password, role, plant_location)
    except IntegrityError as error:
        raise ConflictError('That username already exists.') from error

    flash(f"User '{username}' was created successfully.", 'success')
    return redirect('/users')


@users_bp.route('/users/update/<int:id>', methods=['POST'])
@roles_required('Admin')
def users_update(id):
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    password_confirmation = request.form.get('password_confirmation', '')

    if not username:
        raise ValidationError('Username is required.')
    if len(username) > 255:
        raise ValidationError('Username must be 255 characters or fewer.')
    if password != password_confirmation:
        raise ValidationError('Password confirmation does not match.')
    if password and len(password) < 8:
        raise ValidationError('Password must contain at least 8 characters.')

    try:
        update_user_credentials(id, username, password or None)
    except IntegrityError as error:
        raise ConflictError('That username already exists.') from error

    flash(f"User '{username}' was updated successfully.", 'success')
    return redirect('/users')


@users_bp.route('/users/delete/<int:id>', methods=['POST'])
@roles_required('Admin')
def users_delete(id):
    if id == current_user.id:
        raise ValidationError('You cannot delete your active account.')
    delete_user(id)
    flash('User account was deleted.', 'success')
    return redirect('/users')
