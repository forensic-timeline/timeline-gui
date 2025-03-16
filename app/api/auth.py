from flask import request
from app.api import api
# Input validation
from wtforms import Form, StringField, PasswordField, validators
import re, json

# Validation
# field.data is sanitized by WTFORMS

def validate_password(form, field):
    valid = re.search(r'^(.{0,7}|[^0-9]*|[^A-Z]*|[^a-z]*|[a-zA-Z0-9]*)$', field.data)
    if bool(valid):
        raise validators.ValidationError('Password must be at least ')

class ValidateForm(Form):
    username = StringField('username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm'),
        validate_password
    ])
    confirm = PasswordField('confirm', [
        validators.DataRequired(),
        validate_password
    ])

@api.route('/sign-in', methods=['POST'])
def sign_in():
    pass

@api.route('/sign-up', methods=['POST'])
def sign_up():
    print(request.json)
    validator = ValidateForm(data=request.json)
    if request.method == 'POST' and validator.validate():
        return request.json
    else:
        return {
            "message": "Error 1213"
        }