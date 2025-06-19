from flask import render_template, Blueprint, url_for, redirect, session
from pathlib import PurePosixPath

from flask_login import login_required, current_user, AnonymousUserMixin

from app.config import Config

main_routes = Blueprint('main_routes', __name__)
main_routes.template_folder = Config.DIST_DIR
main_routes.static_folder = Config.STATIC_DIR


@main_routes.route('/')
def domain_redirect():
    return redirect("/auth", code=302)
    # Else go to auth
# TODO: Add redirect if user is logged in for login route
@main_routes.route('/auth')
def auth():
    # Checks if user has a file uploaded, if yes redirect to timeline
    if not isinstance(current_user, AnonymousUserMixin) :
        if "session_db" in session:
            return redirect("/timeline", code=302)
        else:
            return redirect("/start", code=302)
    else:

        # Since web urls use forward slash, cannot use 'os' library
        # since 'os' library on windows uses back slash.
        entry = str(PurePosixPath('src', 'auth', 'index.html'))
        # Instead of using Flask's template folder, build path to Vue pages manually.
        return render_template(entry)

# TODO: Add redirect if user already uploaded a file + notify user to log out first
# TODO: Check if session results in different variables per user
@main_routes.route('/start')
@login_required 
def start():
    # if session["session_csv"] or session["session_db"]:
    #     redirect(url_for('index_plot_sandbox'))
    if "session_db" in session:
        return redirect("/timeline", code=302)
    else:
        entry = str(PurePosixPath('src', 'start_page', 'index.html'))
        return render_template(entry)

@main_routes.route('/timeline')
@login_required
def index_plot_sandbox():
    entry = str(PurePosixPath('src', 'timeline_sandbox', 'index.html'))
    # Instead of using Flask's template folder, build path to Vue pages manually.
    return render_template(entry)

#TODO: If server stops normally (python event 'atexit'):
# 1. Call SQLAlchemy's Engine.dispose() so db file isn't being used.
# 2. clean all user files from 'projects' dir
#If server exits unexpectedly, no cleaning is needed.
#User may need to recover notes in db.