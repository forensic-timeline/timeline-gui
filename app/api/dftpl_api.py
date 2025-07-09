from os.path import join
from app.api import api
from app.dftpl_helper.run_dftpl import run_dftpl
from app import current_app
import json
from flask import session, make_response
from flask_login import login_required
# Read and returns list of analysers in dftpl.


# TODO: Add hyperlinks to each analyser's documentation when that's implemented
# TODO: Add "analysers.json" to main DFTPL build
# TODO: In dftpl/dftpl.py, modify default to start with every analysers, then remove depending on selected analysers
# Use this: https://www.geeksforgeeks.org/python-get-values-of-particular-key-in-list-of-dictionaries/
@api.route("/analysers", methods=["GET"])
def get_analysers():
    analyser_list_path = join(
        current_app.config["APP_DIR"], "dftpl_helper", "analysers.json"
    )

    try:
        with open(analyser_list_path, "r") as f:
            reader = json.load(f)["analysers-list"]
            return reader
    except IOError:
        print(f"Could not read file: {analyser_list_path}")

    pass


@api.route("/run-dftpl", methods=["GET"])
@login_required
def call_run_dftpl():
    if "session_db" in session:
        return make_response("", 200)
    # HACK: Creates a session var for the loading status of dftpl
    elif "session_csv" in session:
        if run_dftpl(
        join(
            current_app.config["UPLOAD_DIR"],
            session["session_csv"]
            ),
            session["selected_analysers"]
        ) >= 0:
            
            return make_response("", 200)
    return make_response("ERROR: Failed to generate or to save timeline file. Please sign out to try again.", 400)
    # FIXME: Catch return if no high level timeline, show message
    # TODO: Delete csv if database is created successfuly
