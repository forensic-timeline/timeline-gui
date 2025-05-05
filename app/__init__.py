from flask import Flask, current_app, render_template, session, redirect, url_for
from pathlib import PurePosixPath
# Database imports
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Auth imports
from flask_login import LoginManager, login_required, current_user, user_logged_out

# TODO: Implement HTTPS support
# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

# Vue's static folder
app = Flask("dftpl_gui_proj")

# Loads and logs current config
from .config import Config
app.logger.info('>>> {}'.format(Config.FLASK_ENV))
app.template_folder = Config.DIST_DIR
app.static_folder = Config.STATIC_DIR

# TODO: Wipe "temp" folder contents possibly filled with partial failed uploads

# Initializes other packages
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth'

# Imports later to avoid circular imports
from app.model import user_model

# API imports. Imports later to avoid circular imports
from app.api import api as api_blueprint
from app.api.auth import clean_up
user_logged_out.connect(clean_up, app)
# Registers blueprints (such as APIs)
app.register_blueprint(api_blueprint, url_prefix=Config.API_URL_PREFIX)
# TODO: Reroute '/' to either '/auth' or '/timeline_sandbox' if user session is valid
# TODO: Add redirect if user is logged in for login route
@app.route('/auth')
def auth():
    # Since web urls use forward slash, cannot use 'os' library
    # since 'os' library on windows uses back slash.
    entry = str(PurePosixPath('src', 'auth', 'index.html'))
    # Instead of using Flask's template folder, build path to Vue pages manually.
    return render_template(entry)

# TODO: Add redirect if user already uploaded a file + notify user to log out first
# TODO: Check if session results in different variables per user
@app.route('/start')
@login_required 
def start():
    # if session["session_csv"] or session["session_db"]:
    #     redirect(url_for('index_plot_sandbox'))
    entry = str(PurePosixPath('src', 'start_page', 'index.html'))
    return render_template(entry)

@app.route('/timeline_sandbox')
#TEST: Testing visualization
#@login_required 
def index_plot_sandbox():
    entry = str(PurePosixPath('src', 'timeline_sandbox', 'index.html'))
    # Instead of using Flask's template folder, build path to Vue pages manually.
    return render_template(entry)

#TODO: If server stops normally (python event 'atexit'):
# 1. Call SQLAlchemy's Engine.dispose() so db file isn't being used.
# 2. clean all user files from 'projects' dir
#If server exits unexpectedly, no cleaning is needed.
#User may need to recover notes in db.