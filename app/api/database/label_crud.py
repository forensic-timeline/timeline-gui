from os.path import join
from math import ceil
from json import loads

from flask import current_app, make_response, request, session

# Auth
from flask_login import login_required
from sqlalchemy import create_engine, text  # Python objects for DB connections
from sqlalchemy import (
    select,
    delete,
    insert,
    update,
    func,
    and_,
    or_,
)  # Methods for sql expressions
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.dialects import sqlite  # TEST
from sqlalchemy.exc import DBAPIError


import app.model.timeline_model as TLModel
from app.api.db_crud import returnDBURL
from app import current_app
from app.api import api


# Retrieve labels as a dict of {id: name}
@api.route("/timeline/get_labels", methods=["GET"])
@login_required
def get_labels():
    database_uri = returnDBURL()
    db_engine = create_engine(database_uri, echo=True)
    db_session = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=db_engine,
        )
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
        print(repr(e))  # FIXME
        db_session.remove()
        db_engine.dispose()
        return make_response("ERROR: Database engine error", 500)
    db_session.remove()
    db_engine.dispose()
    return make_response({"labels": label_dict}, 200)

@api.route("/timeline/add_label", methods=["POST"])
@login_required
def add_label():
    if (
        "newLabel" in request.form and
        len("".join(request.form["newLabel"].split())) > 0 and # Check if string is not just whitespace
        len(request.form["newLabel"]) <= 50
    ):
        database_uri = returnDBURL()
        db_engine = create_engine(database_uri, echo=True)
        db_session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=db_engine,
            )
        )
        # Try to add, catch errors (like out of bounds error)
        # HACK: Hardcoded table name
        try:
            stmt = insert(TLModel.Labels).values(name=request.form["newLabel"])
            db_session.execute(stmt)
            db_session.commit()
        except DBAPIError as e:
            print(repr(e))  # FIXME
            db_session.remove()
            db_engine.dispose()
            return make_response("ERROR: Database engine error", 500)
        db_session.remove()
        db_engine.dispose()
        return make_response("", 200)
    else:
        return make_response("Invalid Label Name/Request", 400)
    

@api.route("/timeline/update_label", methods=["POST"])
@login_required
def update_label():
    if ("selectedLabel" in request.form and 
        "newLabel" in request.form and
        len("".join(request.form["newLabel"].split())) > 0 and # Check if string is not just whitespace
        len(request.form["newLabel"]) <= 50
    ):
        try:
            label_id = int(request.form["selectedLabel"])
        except ValueError as e:
            return make_response("Please select a label", 400)
        database_uri = returnDBURL()
        db_engine = create_engine(database_uri, echo=True)
        db_session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=db_engine,
            )
        )
        # Try to add, catch errors (like out of bounds error)
        # HACK: Hardcoded table name
        try:
            stmt = update(TLModel.Labels).where(TLModel.Labels.id == label_id).values(name=request.form["newLabel"])
            db_session.execute(stmt)
            db_session.commit()
        except DBAPIError as e:
            print(repr(e))  # FIXME
            db_session.remove()
            db_engine.dispose()
            return make_response("ERROR: Database engine error", 500)
        db_session.remove()
        db_engine.dispose()
        return make_response("", 200)
    else:
        return make_response("Invalid Label Name/Request", 400)

# Retrieve labels as a dict of {id: name}
@api.route("/timeline/delete_label", methods=["POST"])
@login_required
def delete_label():
    if ("selectedLabel" in request.form
    ):
        try:
            label_id = int(request.form["selectedLabel"])
        except ValueError as e:
            return make_response("", 400)
        database_uri = returnDBURL()
        db_engine = create_engine(database_uri, echo=True)
        db_session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=db_engine,
            )
        )
        # Try to add, catch errors (like out of bounds error)
        # HACK: Hardcoded table name
        try:
            stmt = delete(TLModel.Labels).where(TLModel.Labels.id == label_id)
            db_session.execute(stmt)
            db_session.commit()
        except DBAPIError as e:
            print(repr(e))  # FIXME
            db_session.remove()
            db_engine.dispose()
            return make_response("ERROR: Database engine error", 500)
        db_session.remove()
        db_engine.dispose()
        return make_response("", 200)
    else:
        return make_response("", 400)

# Update label timeline many to many relationships
@api.route("/timeline/<string:event_type>/u_labels", methods=["POST"])
@login_required
def update_event_labels(event_type):
    if (
        event_type in ["low_level", "high_level"]
        and "rowID" in request.form
        and "setToDelete" in request.form
        and "setToAdd" in request.form
    ):
        # FIXME: Catch json loading error
        set_to_delete = loads(request.form["setToDelete"])
        set_to_add = loads(request.form["setToAdd"])
        database_uri = returnDBURL()
        db_engine = create_engine(database_uri, echo=True)  # TEST
        db_session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=db_engine,
            )
        )
        print()
        # Try to insert and delete, catch errors (like out of bounds error)
        # HACK: Hardcoded table name
        try:
            table_object = (
                TLModel.labels_low_level_events_table
                if event_type == "low_level"
                else TLModel.labels_high_level_events_table
            )
            # Deleting labels
            if len(set_to_delete) > 0:
                for x in set_to_delete:
                    if event_type == "low_level":
                        db_session.execute(
                            delete(TLModel.labels_low_level_events_table)
                            .where(TLModel.labels_low_level_events_table.c.labels_id == x)
                            .where(
                                TLModel.labels_low_level_events_table.c.low_level_events_id
                                == request.form["rowID"]
                            )
                        )
                    else:
                        db_session.execute(
                            delete(TLModel.labels_high_level_events_table)
                            .where(TLModel.labels_high_level_events_table.c.labels_id == x)
                            .where(
                                TLModel.labels_high_level_events_table.c.high_level_events_id
                                == request.form["rowID"]
                            )
                        )
                db_session.commit()
            # Adding labels
            if len(set_to_add) > 0:
                model_dict = []
                for x in set_to_add:
                    model_dict.append(
                        {
                            "labels_id": x,
                            f"{event_type}_events_id": request.form["rowID"],
                        }
                    )
                db_session.execute(insert(table_object), model_dict)
                db_session.commit()
        except DBAPIError as e:
            print(repr(e))  # FIXME
            db_session.remove()
            db_engine.dispose()
            return make_response("ERROR: Can't update labels", 500)
        # Close DB Connections
        # result.close()  # Close result proxy con
        db_session.remove()
        db_engine.dispose()

        return make_response("", 200)
    else:
        return make_response("", 400)
