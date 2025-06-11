import re
from os import remove
from os.path import join, exists
import sqlalchemy as sa
from flask import request, session, current_app, make_response

# Auth
from flask_login import current_user, login_required, login_user, logout_user
# Input validation
# FIXME: Check for ERROR HANDLING FOR flask-login
from wtforms import Form, PasswordField, StringField, validators

from app import db
from app.api import api
from app.model.user_model import User

# Validation
# field.data is sanitized by WTFORMS


# Custom password validation
# Regex is by Matt Timmermans https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
def validate_password(form, field):
    valid = re.search(
        r"^(.{0,7}|.{64,}|[^0-9]*|[^A-Z]*|[^a-z]*|[a-zA-Z0-9]*)$", field.data
    )
    if bool(valid):
        raise validators.ValidationError(
            "Password must be:\n- Between 8 - 64 characters long\n- Have at least 1 capital letter, 1 number, and 1 special character"
        )


# Checks for duplicates
def validate_duplicate_username(form, field):
    user = db.session.scalar(sa.select(User).where(User.username == field.data))
    if user is not None:
        raise validators.StopValidation("Please use a different username.")


# Classes for server-side validation
class ValidateSignUp(Form):
    username = StringField(
        "username",
        [
            validators.DataRequired(),
            validators.Length(min=4, max=25),
            validate_duplicate_username,
            validators.Regexp(
                r"^([a-zA-Z0-9\-\_]*)$",
                message="Username must be:\n- Between 4 - 25 characters long\n- Only contain alphanumerical characters, '-', and '_'",
            ),
        ],
    )
    password = PasswordField(
        "password",
        [
            validators.DataRequired(),
            validators.EqualTo(
                "confirm", message="Password doesn't match confirmation"
            ),
            validate_password,
        ],
    )
    confirm = PasswordField("confirm", [validators.DataRequired(), validate_password])


class ValidateSignIn(Form):
    username = StringField(
        "username",
        [
            validators.DataRequired(),
            validators.Length(min=4, max=25),
            validators.Regexp(
                r"^([a-zA-Z0-9\-\_]*)$",
                message="Username must be:\n- Between 4 - 25 characters long\n- Only contain alphanumerical characters, '-', and '_'",
            ),
        ],
    )
    password = PasswordField("password", [validators.DataRequired(), validate_password])



@api.route("/sign-in", methods=["POST"])
def sign_in():
    try:
        # First, validate input
        validator = ValidateSignIn(data=request.json)
        if request.method == "POST":
            if not validator.validate():
                for key, value in validator.errors.items():
                    return make_response(value[0], 400)
            # If input is validated, authenticate user
            user = db.session.scalar(
                sa.select(User).where(User.username == request.json["username"])
            )
            if user is None or not user.check_password(request.json["password"]):
                return make_response("Wrong username or password!", 400)
            login_user(user)
            session.permanent = True # HACK: Make session permanent for (default) 31 days
            # NOTE: This means user must manually logout to erase their files
            # TODO: Redirect to project upload
            return make_response("Account created!", 200)

    except (validators.StopValidation, validators.ValidationError) as e:
        # FIXME: LOGGING
        return make_response(str(e), 400)
    except Exception as e:
        return make_response("Unknown error!", 500)

# TODO: 
# 1. Call SQLAlchemy's Engine.dispose() so db file isn't being used.
# 2. clean all user files from 'projects' dir
#If server exits unexpectedly, no cleaning is needed.
#User may need to recover notes in db.
@api.route("/sign-out", methods=["GET"])
@login_required
def logout():
    # TODO: Check if session and it's info is deleted entirely
    username = current_user.username
    logout_user()
    print(f"Logged out {username}") # HACK
    # TODO: Redirect back to login
    return make_response("Successfully logged out!", 200)

# On LOGOUT (event listener setup in __init__):
# Delete user's session variables and files
# 1. CSV Path (Should delete after sqlite db is created)
# 2. SQLite file
# FIXME: Check if valid path for removal
# Returns 0 for success, -1 for OSError or FileNotFoundError, -2 for unknowns
# NOTE: Doesn't get called when program terminates, only when user logs out
# TODO: Clean up when program terminates (clean folder instead on individual files)
# FIXME: Logging
def clean_up(app=None, user=None, csv=True, db=True):
    print(f"Cleaning files") # HACK
    try:
        if csv and "session_csv" in session:
            remove(join(current_app.config['UPLOAD_DIR'], session.pop('session_csv', None)))
        else:
            # HACK
            print("WARNING: Tried to clean up session var, but key is missing/no value")
        if db and "session_db" in session:
            remove(join(current_app.config['UPLOAD_DIR'], session.pop('session_db', None)))
        else:
            # HACK
            print("WARNING: Tried to clean up session var, but key is missing/no value")
    except (OSError, FileNotFoundError) as e:
        # HACK
        print(e.strerror)
        return -1
    except:
        # HACK
        print("Unknown error while clean_up")
        return -2
    return 0

# FIXME: Why there's an empty account at id 0? Subsequent submission doesn't generate that empty account.
@api.route("/sign-up", methods=["POST"])
def sign_up():
    try:
        # Validate with return value since validator error when raised is handled by validator, not returned to calling function
        validator = ValidateSignUp(data=request.json)
        if request.method == "POST":
            if not validator.validate():
                for key, value in validator.errors.items():
                    return make_response(value[0], 400)
            # First, validate input
            user = User(username=request.json["username"])
            user.set_password(request.json["password"])
            db.session.add(user)
            db.session.commit()
            sign_in()
            return make_response("Successfully signed in!", 200)
    except (validators.StopValidation, validators.ValidationError) as e:
        # FIXME: LOGGING
        return make_response(str(e), 400)
    except Exception as e:
        print(str(e))
        return make_response("Unknown error!", 500)

@api.route("/get-user", methods=["GET"])
@login_required
def get_user():
    return current_user.username
