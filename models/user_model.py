from models.db import get_db_connection
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from exceptions import NotFoundError


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.role = row["role"]
        self.plant_location = row.get("plant_location")


def init_user_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(100) NOT NULL,
            plant_location VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if plant_location column exists (migration safety)
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = DATABASE()
        AND table_name = 'users'
        AND column_name = 'plant_location'
    """)
    exists = cursor.fetchone()[0]

    if not exists:
        cursor.execute("ALTER TABLE users ADD COLUMN plant_location VARCHAR(100)")

    conn.commit()
    conn.close()


def check_user_login(username, password):
    """
    Checks user credentials.
    MODIFIED: Removed 'role' argument. Queries by username only.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query user by username only
    cursor.execute("""
        SELECT * FROM users
        WHERE username = %s
    """, (username,))

    user = cursor.fetchone()
    conn.close()

    # Check if user exists and password matches
    if user and check_password_hash(user['password'], password):
        return User(user)

    return None


def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, username, role, plant_location
            FROM users
            WHERE id = %s
        """, (user_id,))
        row = cursor.fetchone()
        return User(row) if row else None
    finally:
        conn.close()


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, username, role, plant_location, created_at
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()
    conn.close()
    return users


def add_user(username, password, role, plant_location=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    cursor.execute("""
        INSERT INTO users (username, password, role, plant_location)
        VALUES (%s, %s, %s, %s)
    """, (username, hashed_password, role, plant_location))

    conn.commit()
    conn.close()


def update_user_credentials(user_id, username, password=None):
    """Update a username and optionally replace its stored password hash."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise NotFoundError("User account was not found.")

        if password:
            cursor.execute(
                """
                UPDATE users
                SET username = %s, password = %s
                WHERE id = %s
                """,
                (username, generate_password_hash(password), user_id),
            )
        else:
            cursor.execute(
                "UPDATE users SET username = %s WHERE id = %s",
                (username, user_id),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_admin_user(username, password):
    """Create the configured Admin once without changing an existing account."""
    normalized_username = (username or "").strip()
    if not normalized_username or not password:
        raise RuntimeError(
            "LAKSHYA_BOOTSTRAP_ADMIN_USERNAME and "
            "LAKSHYA_BOOTSTRAP_ADMIN_PASSWORD are required when "
            "AUTO_CREATE_ADMIN is enabled."
        )

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, role FROM users WHERE username = %s",
            (normalized_username,),
        )
        if cursor.fetchone():
            return False

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password, role, plant_location)
            VALUES (%s, %s, 'Admin', NULL)
            ON DUPLICATE KEY UPDATE username = username
            """,
            (normalized_username, generate_password_hash(password)),
        )
        conn.commit()
        return cursor.rowcount == 1
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))

    conn.commit()
    conn.close()
