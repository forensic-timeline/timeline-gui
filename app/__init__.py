from flask import Flask, current_app, session
# from flask import redirect, url_for
# Database imports
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Auth imports
from flask_login import LoginManager, current_user, user_logged_out

# Global packages/plugins
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
# TODO: Implement HTTPS support
# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
def init_app():
    # Vue's static folder
    app = Flask("__main__", instance_relative_config=False)
    # Loads and logs current config
    from .config import Config
    app.config.from_object(Config)
    app.logger.info('>>> {}'.format(Config.FLASK_ENV))
    app.template_folder = Config.DIST_DIR
    app.static_folder = Config.STATIC_DIR

    # TODO: Wipe "temp" folder contents possibly filled with partial failed uploads

    # Initializes other packages
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Imports later to avoid circular imports
    # from app.model import user_model
    from app.dftpl_helper.run_dftpl import generate_analysers_list
    from app.api import api as api_blueprint
    from app.api.auth import clean_up

    with app.app_context():
        # Other files and functions
        from app.routes import main_routes
        generate_analysers_list()
        # Registers blueprints (such as APIs)
        app.register_blueprint(api_blueprint, url_prefix=Config.API_URL_PREFIX)
        app.register_blueprint(main_routes)
        login.login_view = 'main_routes.auth'

        # Connect event listeners
        user_logged_out.connect(clean_up, app)

        return app
    

