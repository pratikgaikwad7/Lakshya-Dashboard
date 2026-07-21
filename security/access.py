from functools import wraps

from flask_login import current_user, login_required

from exceptions import ForbiddenError


STUDENT_MANAGEMENT_ROLES = {"Admin", "SDC Coordinator", "PMO"}
EVALUATION_MANAGEMENT_ROLES = {"Admin", "SDC Coordinator"}
PLANT_RESTRICTED_ROLES = {"SDC Coordinator", "HR Head"}


def roles_required(*allowed_roles):
    allowed = set(allowed_roles)

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in allowed:
                raise ForbiddenError("You do not have permission to perform this action.")
            return view(*args, **kwargs)

        return wrapped

    return decorator


def assigned_plant_required(user=None):
    user = user or current_user
    if not user.plant_location:
        raise ForbiddenError("No plant location is assigned to this account.")
    return user.plant_location


def force_plant_scope(filters, user=None):
    user = user or current_user
    scoped = dict(filters or {})
    if user.role in PLANT_RESTRICTED_ROLES:
        scoped["plant_location"] = [assigned_plant_required(user)]
    return scoped


def authorize_student_plant(student, user=None):
    user = user or current_user
    if user.role == "SDC Coordinator":
        assigned_plant = assigned_plant_required(user)
        if not student or student.get("plant_location") != assigned_plant:
            raise ForbiddenError("This student does not belong to your assigned plant.")
