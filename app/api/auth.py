from flask import request, redirect, url_for
from app.api import api

# Input validation
# TODO: Import parts of validators to reduce size
# FIXME: Check for ERROR HANDLING FOR flask-login
from wtforms import Form, StringField, PasswordField, validators
import re

# Auth
from flask_login import login_user, logout_user, login_required, current_user
import sqlalchemy as sa
from app import db
from app.models import User
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
        raise validators.ValidationError("Please use a different username.")


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
            validator.validate()
            # If input is validated, authenticate user
            user = db.session.scalar(
                sa.select(User).where(User.username == request.json["username"])
            )
            if user is None or not user.check_password(request.json["password"]):
                # TODO: Refresh page
                return {"message": "ERROR: Wrong username or password!"}
            if current_user.is_authenticated:
                return {"message": "ERROR: Please log out from your first browser first!"}
            # TODO: Redirect to project upload
            return {
            "message": "redirect"
            }

    except (validators.StopValidation, validators.ValidationError) as e:
        return {"message": str(e)}


@api.route("/sign-out", methods=["GET"])
@login_required
def logout():
    print(f"Logged out {current_user.username}")
    logout_user()
    # TODO: Redirect back to login
    return {"message": "Logged out!"}


# FIXME: Why there's an empty account at id 0? Subsequent submission doesn't generate that empty account.
@api.route("/sign-up", methods=["POST"])
def sign_up():
    try:
        validator = ValidateSignUp(data=request.json)
        if request.method == "POST":
            validator.validate()
            # First, validate input
            print(request.json)
            user = User(username=request.json["username"])
            user.set_password(request.json["password"])
            db.session.add(user)
            db.session.commit()
            return {"message": "Successfully signed up!"}

    except (validators.StopValidation, validators.ValidationError) as e:
        return {"message": str(e)}


@api.route("/get-user", methods=["GET"])
@login_required
def get_user():
    #TEST
    print(f"CURR USER: {current_user.username}")
    return [current_user.username]
