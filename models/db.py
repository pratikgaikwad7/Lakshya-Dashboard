import mysql.connector
import os
from dotenv import load_dotenv
from flask import current_app, has_app_context

load_dotenv()

def get_db_connection():
    def setting(name):
        if has_app_context():
            return current_app.config.get(name)
        return os.getenv(name)

    connection = mysql.connector.connect(
        host=setting('DB_HOST'),
        user=setting('DB_USER'),
        password=setting('DB_PASSWORD'),
        database=setting('DB_NAME'),
        connection_timeout=int(setting('DB_CONNECT_TIMEOUT') or 5),
    )
    return connection
