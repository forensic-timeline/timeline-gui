import os
from flask import Flask, current_app, send_file
from app.api import api as api_blueprint

# TODO: Implement HTTPS support

# Vue's static folder
app = Flask("dftpl_gui_proj", static_folder=r'dist\static')

# Registers blueprints (such as APIs)
app.register_blueprint(api_blueprint, url_prefix="/api/v1")

# Loads and logs current config
from .config import Config
app.logger.info('>>> {}'.format(Config.FLASK_ENV))

# TODO: Convert into method. Construct route based on input string array
@app.route('/')
def index_client():
    dist_dir = current_app.config['DIST_DIR']
    print(app.static_folder)
    entry = os.path.join(dist_dir, 'src', 'auth', 'index.html')
    # Instead of using Flask's template folder, build path to Vue pages manually.
    return send_file(entry)

@app.route('/timeline_sandbox')
def index_plot_sandbox():
    dist_dir = current_app.config['DIST_DIR']
    print(app.static_folder)
    entry = os.path.join(dist_dir, 'src', 'timeline_sandbox', 'index.html')
    # Instead of using Flask's template folder, build path to Vue pages manually.
    return send_file(entry)

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

