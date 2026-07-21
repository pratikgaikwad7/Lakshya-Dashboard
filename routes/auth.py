from flask import Blueprint, render_template, request, redirect, session, flash
from flask_login import login_required, login_user, logout_user

from extensions import limiter
from models.user_model import check_user_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/login')
def login_page():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    user = check_user_login(username, password)

    if user:
        session.clear()
        login_user(user)
        session.permanent = True
        session['username'] = user.username
        session['role'] = user.role
        session['plant_location'] = user.plant_location
        session['is_admin'] = user.role == 'Admin'

        if user.role in ['Admin', 'PMO', 'SDC Coordinator']:
            return redirect('/admin-dashboard')
        return redirect('/user_dashboard')

    # If login fails
    flash('Invalid Username or Password', 'error')
    return redirect('/login')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/login')
