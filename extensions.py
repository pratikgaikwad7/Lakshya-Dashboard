from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()
login_manager.login_view = "auth.login_page"


@login_manager.user_loader
def load_user(user_id):
    from models.user_model import get_user_by_id

    try:
        return get_user_by_id(int(user_id))
    except (TypeError, ValueError):
        return None
