from flask import Blueprint

# TODO: Replace __name__?
api = Blueprint('api', __name__)
# TODO: Change error status code returns to json for non-web browser requests

# Import all api files
from app.api import auth, file_crud, tokens, errors, fake_data, dftpl_api