"""
Global Flask Application Setting

See `.flaskenv` for default settings.
"""

import os, secrets
from datetime import timedelta

class Config(object):
    # If not set fall back to production for safety
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    # Set FLASK_SECRET on your production Environment
    SECRET_KEY = os.getenv("FLASK_SECRET", secrets.token_hex())

    # Getting Vue project's path
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    ROOT_DIR = os.path.abspath(os.path.dirname(APP_DIR))
    DIST_DIR = os.path.join(ROOT_DIR, "dist")

    if not os.path.exists(DIST_DIR):
        raise Exception("Client dir not found: {}".format(DIST_DIR))

    STATIC_DIR = os.path.join(DIST_DIR, "static")
    if not os.path.exists(STATIC_DIR):
        raise Exception("Static folder not found: {}".format(STATIC_DIR))

    # Flask Login & Flask-SQLAlchemy Config
    # TEST: User data temp setup
    # User Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(APP_DIR, "app.db")
    USE_SESSION_FOR_NEXT = True # TEST: URL "Next" var causing error

    # TODO: Use this for all api calls
    # API Path
    API_URL_PREFIX = "/api/v1"

    # File upload and download configs
    # TODO: Generate unique subfolder for each user
    TEMP_DIR = os.path.join(APP_DIR, "temp")
    if not os.path.exists(TEMP_DIR):
        raise Exception("Temp folder not found: {}".format(TEMP_DIR))
    UPLOAD_DIR = os.path.join(APP_DIR, "projects")
    if not os.path.exists(UPLOAD_DIR):
        raise Exception("Upload folder not found: {}".format(UPLOAD_DIR))
    UPLOAD_EXTENSIONS = [
        "csv",
        "sqlite",
    ]  # Use .sqlite for database files for clarity on what type of db
    MAX_FILE_SIZE = (
        5 * 1073741824
    )  # HACK: 5 GB Flask upload limit. Practical size 1 KB = 1024 B
    # Technically unused since dropzonejs has it's own chunked upload but
    # set just in case
    # TEST 
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)