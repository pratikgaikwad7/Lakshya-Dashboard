import click
from flask.cli import with_appcontext

from exceptions import NotFoundError
from models.student_model import check_and_update_completion_status
from models.user_model import ensure_admin_user, reset_admin_password


def _validate_admin_password(_context, _parameter, value):
    if len(value or "") < 8:
        raise click.BadParameter("must contain at least 8 characters")
    return value


def register_commands(app):
    @app.cli.command("update-student-statuses")
    @with_appcontext
    def update_student_statuses_command():
        """Mark students past their end date as completed."""
        updated = check_and_update_completion_status()
        click.echo(f"Updated {updated} student record(s).")

    @app.cli.command("create-admin")
    @click.option(
        "--username",
        envvar="LAKSHYA_BOOTSTRAP_ADMIN_USERNAME",
        prompt=True,
        help="Admin username. Defaults to LAKSHYA_BOOTSTRAP_ADMIN_USERNAME.",
    )
    @click.option(
        "--password",
        envvar="LAKSHYA_BOOTSTRAP_ADMIN_PASSWORD",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        callback=_validate_admin_password,
        help="Admin password. Defaults to LAKSHYA_BOOTSTRAP_ADMIN_PASSWORD.",
    )
    @with_appcontext
    def create_admin_command(username, password):
        """Create a database-backed administrator, optionally from .env."""
        normalized_username = username.strip()
        try:
            created = ensure_admin_user(normalized_username, password)
        except ValueError as error:
            raise click.ClickException(str(error)) from error
        if created:
            click.echo(f"Administrator '{normalized_username}' created.")
            return
        click.echo(
            f"Administrator '{normalized_username}' already exists; "
            "no password was changed."
        )

    @app.cli.command("reset-admin-password")
    @click.option(
        "--username",
        envvar="LAKSHYA_BOOTSTRAP_ADMIN_USERNAME",
        prompt=True,
        help="Existing Admin username.",
    )
    @click.option(
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        callback=_validate_admin_password,
        help="New Admin password.",
    )
    @with_appcontext
    def reset_admin_password_command(username, password):
        """Safely replace the password for an existing Admin account."""
        normalized_username = username.strip()
        try:
            reset_admin_password(normalized_username, password)
        except (NotFoundError, ValueError, RuntimeError) as error:
            raise click.ClickException(str(error)) from error
        click.echo(f"Password updated for Administrator '{normalized_username}'.")
