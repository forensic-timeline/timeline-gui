"""
Global Flask Application Setting

See `.flaskenv` for default settings.
 """

import os
from app import app

class Config(object):
    # If not set fall back to production for safety
    FLASK_ENV =  os.getenv('FLASK_ENV', 'production')
    # Set FLASK_SECRET on your production Environment
    SECRET_KEY = os.getenv('FLASK_SECRET', 'Secret')

    # Getting Vue project's path
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    ROOT_DIR = os.path.abspath(os.path.dirname(APP_DIR))
    DIST_DIR = os.path.join(ROOT_DIR, 'dist')

    if not os.path.exists(DIST_DIR):
        raise Exception(
            'DIST_DIR not found: {}'.format(DIST_DIR))
    
    STATIC_DIR = os.path.join(DIST_DIR, 'static') # FIXME: Possible error if folder is missing?
    
    # Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(APP_DIR, 'app.db')

    # API Path
    API_URL_PREFIX = "/api/v1"
app.config.from_object('app.config.Config')