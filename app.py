import logging
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

load_dotenv()

from config import get_config
from exceptions import AppError
from extensions import csrf, limiter, login_manager


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or get_config())
    _validate_configuration(app)
    _configure_logging(app)

    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)

    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.evaluations import evaluations_bp
    from routes.students import students_bp
    from routes.user_dashboard import user_dashboard_bp
    from routes.users import users_bp

    for blueprint in (
        students_bp, auth_bp, users_bp, admin_bp, evaluations_bp, user_dashboard_bp
    ):
        app.register_blueprint(blueprint)

    from commands import register_commands
    register_commands(app)
    _register_admin_bootstrap(app)
    _register_error_handlers(app)
    _register_security_headers(app)
    return app


def _validate_configuration(app):
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be configured before the application can start.")
    if not app.config.get("TESTING"):
        missing = [name for name in ("DB_HOST", "DB_USER", "DB_NAME") if not app.config.get(name)]
        if missing:
            raise RuntimeError(f"Missing required database configuration: {', '.join(missing)}")
    if app.config.get("AUTO_CREATE_ADMIN"):
        missing = [
            name for name in ("ADMIN_USERNAME", "ADMIN_PASSWORD")
            if not app.config.get(name)
        ]
        if missing:
            raise RuntimeError(
                "Missing automatic Admin configuration: " + ", ".join(missing)
            )


def _configure_logging(app):
    logging.basicConfig(
        level=getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _wants_json():
    return request.path.startswith("/api/") or request.is_json


def _register_error_handlers(app):
    @login_manager.unauthorized_handler
    def unauthorized():
        if _wants_json():
            return jsonify({"error": "Authentication is required.", "code": "unauthorized"}), 401
        return redirect("/login")

    @app.errorhandler(AppError)
    def handle_app_error(error):
        if _wants_json():
            return jsonify({"error": error.message, "code": error.code}), error.status_code
        return error.message, error.status_code

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        if _wants_json():
            return jsonify({"error": "Invalid or missing CSRF token.", "code": "csrf_error"}), 400
        return "Invalid or missing CSRF token.", 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return error
        app.logger.exception("Unhandled application error", exc_info=error)
        if _wants_json():
            return jsonify({"error": "An unexpected error occurred.", "code": "internal_error"}), 500
        return "An unexpected error occurred.", 500


def _register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response


def _register_admin_bootstrap(app):
    """Create the configured development Admin once on the first request."""
    if not app.config.get("AUTO_CREATE_ADMIN"):
        return

    if len(app.config["ADMIN_PASSWORD"]) < 8:
        app.logger.warning(
            "LAKSHYA_BOOTSTRAP_ADMIN_PASSWORD contains fewer than 8 characters. "
            "Change it and run 'flask --app app reset-admin-password'."
        )

    bootstrap_lock = Lock()
    bootstrap_state = {"checked": False}

    @app.before_request
    def ensure_configured_admin():
        if bootstrap_state["checked"]:
            return None

        with bootstrap_lock:
            if bootstrap_state["checked"]:
                return None

            from models.user_model import ensure_admin_user

            created = ensure_admin_user(
                app.config["ADMIN_USERNAME"],
                app.config["ADMIN_PASSWORD"],
            )
            if created:
                app.logger.info(
                    "Created configured development Admin account '%s'.",
                    app.config["ADMIN_USERNAME"],
                )
            else:
                app.logger.info(
                    "Configured Admin account '%s' already exists; its password "
                    "was not changed. Use 'flask --app app reset-admin-password' "
                    "to set a new password.",
                    app.config["ADMIN_USERNAME"],
                )
            bootstrap_state["checked"] = True
        return None


app = create_app()


if __name__ == "__main__":
    app.run(port=5001)
