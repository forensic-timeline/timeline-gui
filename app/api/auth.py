from flask import request
from app.api import api
# Input validation
from wtforms import Form, StringField, PasswordField, validators
import re

# Validation
# field.data is sanitized by WTFORMS
# Regex is by Matt Timmermans https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
def validate_password(form, field):
    valid = re.search(r'^(.{0,7}|[^0-9]*|[^A-Z]*|[^a-z]*|[a-zA-Z0-9]*)$', field.data)
    if bool(valid):
        raise validators.ValidationError('Password must be:\n- At least 8 characters long\n- Have at least 1 capital letter and 1 number\n- Only contains alphanumerical characters')

class ValidateSignUp(Form):
    username = StringField('username', [validators.DataRequired(), validators.Length(min=4, max=25), validators.Regexp(r'^([a-zA-Z0-9\-\_]*)$', message="Username must:\n- Only contain alphanumerical characters, '-', and '_'")])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password doesn\'t match confirmation'),
        validate_password
    ])
    confirm = PasswordField('confirm', [
        validators.DataRequired(),
        validate_password
    ])

class ValidateSignIn(Form):
    username = StringField('username', [validators.DataRequired(), validators.Length(min=4, max=25), validators.Regexp(r'^([a-zA-Z0-9\-\_]*)$', message="Username must:\n- Only contain alphanumerical characters, '-', and '_'")])
    password = PasswordField('password', [
        validators.DataRequired(),
        validate_password
    ])

@api.route('/sign-in', methods=['POST'])
def sign_in():
    try:    
        validator = ValidateSignIn(data=request.json)
        if request.method == 'POST':
            validator.validate()
            return {
                "message": "Successfully signed in!"
            }

    except (validators.StopValidation, validators.ValidationError) as e:
            return {
                "message": str(e)
            }

@api.route('/sign-up', methods=['POST'])
def sign_up():
    try:    
        validator = ValidateSignUp(data=request.json)
        if request.method == 'POST':
            validator.validate()
            return {
                "message": "Successfully signed up!"
            }

    except (validators.StopValidation, validators.ValidationError) as e:
            return {
                "message": str(e)
            }