from flask import Blueprint, render_template
from flask_login import current_user
# Import the stats function from evaluation_model
from models.evaluation_model import get_evaluation_dashboard_stats
from security.access import assigned_plant_required, roles_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin-dashboard')
@roles_required('Admin', 'PMO', 'SDC Coordinator')
def admin_dashboard():
    role = current_user.role

    # --- FETCH STATS ---
    filters = {} 
    
    # SDC Coordinator: Filter by their assigned plant location
    if role == 'SDC Coordinator':
        filters['plant_location'] = assigned_plant_required()
    
    # Get comprehensive stats
    stats_data = get_evaluation_dashboard_stats(filters)
    summary = stats_data['summary']

    return render_template(
        'admin_dashboard.html',
        user_name=current_user.username,
        stats=summary,
        role=role  # Pass role to template for UI logic
    )
