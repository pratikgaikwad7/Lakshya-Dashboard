import click
from flask.cli import with_appcontext

from models.student_model import check_and_update_completion_status
from models.user_model import add_user


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
        help="Admin password. Defaults to LAKSHYA_BOOTSTRAP_ADMIN_PASSWORD.",
    )
    @with_appcontext
    def create_admin_command(username, password):
        """Create a database-backed administrator, optionally from .env."""
        add_user(username.strip(), password, "Admin")
        click.echo(f"Administrator '{username}' created.")
