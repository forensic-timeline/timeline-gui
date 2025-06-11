from flask import Blueprint

api = Blueprint('api', __name__)

# Import all api files
from app.api import auth, file_crud, dftpl_api, db_crud
from app.api.database import label_crud