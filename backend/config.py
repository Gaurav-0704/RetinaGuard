# ============================================================
#  backend/config.py — Flask App Configuration
#
#  I keep all Flask settings here. DevelopmentConfig is the
#  default; ProductionConfig tightens cookies and requires
#  SECRET_KEY to be set in the environment.
# ============================================================

import os
import secrets
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


def _get_secret_key():
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    # Dev fallback: ephemeral key so the app starts without config.
    # Every restart invalidates existing sessions — fine for local dev,
    # unacceptable for production (set SECRET_KEY in your environment).
    logger.warning(
        "SECRET_KEY not set — generating a one-time ephemeral key. "
        "Sessions will not survive server restarts. "
        "Set SECRET_KEY in your environment before deploying."
    )
    return secrets.token_hex(32)


class Config:
    # Flask
    SECRET_KEY = _get_secret_key()
    DEBUG = False

    # Database (SQLite — easy to swap to PostgreSQL in production)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(ROOT_DIR, 'retinoguard.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.path.join(ROOT_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp"}

    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 hours


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
