from flask import Flask, current_app, render_template
from pathlib import PurePosixPath
# Database imports
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Auth imports
from flask_login import LoginManager, login_required, current_user

# TODO: Implement HTTPS support

# Vue's static folder
app = Flask("dftpl_gui_proj")

# Loads and logs current config
from .config import Config
app.logger.info('>>> {}'.format(Config.FLASK_ENV))
app.template_folder = Config.DIST_DIR
app.static_folder = Config.STATIC_DIR
print(app.template_folder)
# Initializes other packages
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth'
# Imports later to avoid circular imports
from app import models

# API imports. Imports later to avoid circular imports
from app.api import api as api_blueprint

# Registers blueprints (such as APIs)
app.register_blueprint(api_blueprint, url_prefix=Config.API_URL_PREFIX)

# TODO: Convert into method. Construct route based on input string array
@app.route('/auth')
def auth():
    # Since web urls use forward slash, cannot use 'os' library
    # since 'os' library on windows uses back slash.
    entry = str(PurePosixPath('src', 'auth', 'index.html'))
    # Instead of using Flask's template folder, build path to Vue pages manually.
    return render_template(entry)

# TODO: Add redirect if user is logged in for login route
#             if current_user.is_authenticated:

@app.route('/timeline_sandbox')
@login_required 
def index_plot_sandbox():
    entry = str(PurePosixPath('src', 'timeline_sandbox', 'index.html'))
    # Instead of using Flask's template folder, build path to Vue pages manually.
    return render_template(entry)

# @app.route('/page1')
# def multi_page_1():
#     dist_dir = current_app.config['DIST_DIR']
#     print(app.static_folder)
#     entry = os.path.join(dist_dir, "other_pages", 'index1.html')
#     # Instead of using Flask's template folder, build path to Vue pages manually.
#     return send_file(entry)

# @app.route('/page2')
# def multi_page_2():
#     dist_dir = current_app.config['DIST_DIR']
#     print(app.static_folder)
#     entry = os.path.join(dist_dir, "other_pages", 'index2.html')
#     # Instead of using Flask's template folder, build path to Vue pages manually.
#     return send_file(entry)

