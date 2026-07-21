import os
from datetime import timedelta


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv("SESSION_HOURS", "8")))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _as_bool(os.getenv("SESSION_COOKIE_SECURE"), False)
    WTF_CSRF_TIME_LIMIT = 3600
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    AUTO_CREATE_ADMIN = _as_bool(os.getenv("AUTO_CREATE_ADMIN"), False)
    ADMIN_USERNAME = os.getenv("LAKSHYA_BOOTSTRAP_ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("LAKSHYA_BOOTSTRAP_ADMIN_PASSWORD")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "testing-secret-key")
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    AUTO_CREATE_ADMIN = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    AUTO_CREATE_ADMIN = False


CONFIG_BY_ENV = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config():
    environment = os.getenv("APP_ENV", "development").strip().lower()
    return CONFIG_BY_ENV.get(environment, DevelopmentConfig)
