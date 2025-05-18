from os.path import join
from math import ceil

from flask import current_app, make_response, request, session

# Auth
from flask_login import login_required
from sqlalchemy import create_engine, text  # Python objects for DB connections
from sqlalchemy import select, func, and_, or_  # Methods for sql expressions
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.dialects import sqlite # TEST
from sqlalchemy.exc import DBAPIError


import app.model.timeline_model as TLModel
from app import current_app
from app.api import api

# Retrieve labels as a dict of {id: name}
@api.route("/timeline/get_labels", methods=["GET"])
# @login_required
# TEST: Add auth later
def get_labels():
    # TODO: Replace with user's database session info
    # TEST: Use test db to avoid processing with dftpl each test
    database_uri = (
        "sqlite:///"
        + r"D:\Moving\Documents\Universitas - MatKul\PraTA_TA_LaporanKP\TA"
        + r"\Proj\dftpl_gui_proj\test\timeline_2_fts5_short_12052025.sqlite"
    )
    db_engine = create_engine(database_uri, echo=True)
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=db_engine, )
    )
        # Try to update, catch errors (like out of bounds error)
        # HACK: Hardcoded table name
    label_dict = {}
    try:
        stmt = select(TLModel.Labels).order_by(TLModel.Labels.name.asc())
        
        for row in db_session.scalars(stmt).all():
            if isinstance(row, TLModel.Labels):
                label_dict[row.id] = row.name

    except DBAPIError as e:
        db_session.remove()
        db_engine.dispose()
        return make_response("ERROR: Database engine error", 500)
    db_session.remove()
    db_engine.dispose()
    return make_response({"labels": label_dict}, 200)