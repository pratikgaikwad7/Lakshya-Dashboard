"""Apply resumable, versioned migrations to the configured MySQL database."""

import importlib.util
from pathlib import Path

from models.db import get_db_connection


MIGRATION_ROOT = Path(__file__).parents[1] / "migrations"


def _load_migration(path):
    spec = importlib.util.spec_from_file_location(f"lakshya_migration_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        cursor.execute("SELECT filename FROM schema_migrations")
        applied = {row[0] for row in cursor.fetchall()}

        for migration_path in sorted(MIGRATION_ROOT.glob("[0-9]*_*.py")):
            if migration_path.name in applied:
                continue
            migration = _load_migration(migration_path)
            migration.upgrade(cursor)
            cursor.execute(
                "INSERT INTO schema_migrations (filename) VALUES (%s)",
                (migration_path.name,),
            )
            connection.commit()
            print(f"Applied {migration_path.name}")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
