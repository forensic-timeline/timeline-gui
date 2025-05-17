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

AMOUNT_IN_PAGE = 1000  # Max events per page, 100k crashed tabulator
PAGES_AROUND = 1  # Max pages before and after current
IS_ASCENDING_VALUES = {"true": "ASC", "false": "DESC"}
# TODO: Automate column retrieval
# MAKE SURE THE CLIENT SIDE MATCHES THESE VALUES
# Stores all columns objects for ease of understanding + used for search and sort column

TABLE_VALUES = {
    "low_level": {
        "model": TLModel.LowLevelEvents,
        "columns": [
            "id",
            "date_time_min",
            "date_time_max",
            "event_type",
            "path",
            "evidence",
            "plugin",
            "provenance_raw_entry",
        ],
    },
    "high_level": {
        "model": TLModel.HighLevelEvents,
        "columns": [
            "id",
            "date_time_min",
            "date_time_max",
            "event_type",
            "description",
            "category",
            "reasoning desc",
            "reasoning ref",
        ],
    },
}

MAX_KEYWORDS = 10
# Pagination function (use in API)
# 1. Low level tables
# 2. Low and high level timeline visualizations
# Arguments:


# TEST: Measure execution time for each page retrieval
# FIXME: Error handling
# Support for search, filter, sort, range?
def get_page_low_event(
    db_session: scoped_session,
    table_name: str,
    filter_include: list[str] = [],
    filter_exclude: list[str] = [],
    sort_asc: str = "true",
    sort_column: str = "id",
    get_page: int = 1,
):
    # TEST: https://mysql.rjweb.org/doc.php/pagination
    cur_page = 1 if get_page < 1 else get_page  # Check min page requested
    max_page = 1
    page_rows = []
    # FIXME: Check if code can handle modified db (missing ids, not ordered ids, missing values)
    # Define MATCH statement (if any is required)
    # NOTE: Pylint throws a "not callable" error but false positive
    # https://github.com/sqlalchemy/sqlalchemy/discussions/9202
    include_exclude = ""
    column_filter = " ".join(TABLE_VALUES[table_name]["columns"])
    parameters = {} # For binding parameters
    # Generates MATCH statement with parameter tokens
    # HACK: Hardcoded table name
    # FIXME: Escape characters such as '%' in sqlite
    if len(filter_include) > 0:
        print("Added include")  # TEST
        param_id = []
        for index, word in enumerate(filter_include):
            param_id.append(f'||:inc{index}') # Concatenate so arg bindings will work
            parameters[f"inc{index}"] = f"\"{word}\"" # To escape characters like '$'
        include_exclude = include_exclude + (f" AND {table_name}_events_idx.id IN "
                                             f"(SELECT id FROM {table_name}_events_idx WHERE {table_name}_events_idx"
                                             f" MATCH \'{{{column_filter}}} : \'{" ".join(param_id)})"
                                             )

    if len(filter_exclude) > 0:
        print("Added exclude")  # TEST
        param_id = []
        for index, word in enumerate(filter_exclude):
            param_id.append(f'||:exc{index}') # Concatenate so arg bindings will work
            parameters[f"exc{index}"] = f"\"{word}\"" # To escape characters like '$'
        include_exclude = include_exclude + (f" AND {table_name}_events_idx.id NOT IN "
                                             f"(SELECT id FROM {table_name}_events_idx WHERE {table_name}_events_idx"
                                             f" MATCH \'{{{column_filter}}} : \'{" ".join(param_id)})"
                                            )
    
    # If an include or exclude term existed, add match statement
    # Get max pages
    # HACK: So MATCH and id where statements can be appended conditionally
    stmt = f"SELECT COUNT(id) FROM {table_name}_events_idx WHERE 1=1" 

    if include_exclude != "":
        stmt = f"{stmt} {include_exclude}"
    max_page = ceil(
        float(db_session.scalars(text(stmt), parameters).first()) / float(AMOUNT_IN_PAGE)
    )  # Automatically closes result after getting value

    cur_page = max_page if get_page > max_page else get_page  # Check max page requested

    # Create select and where statement before adding limit and id lookup
    # HACK: So MATCH and id where statements can be appended conditionally
    stmt_2 = f"SELECT * FROM {table_name}_events_idx WHERE 1=1"

    if include_exclude != "":
        stmt_2 = f"{stmt_2} {include_exclude}"

    # If first, sort by first then limit
    if cur_page <= 1:
        stmt_2 = f"{stmt_2} ORDER BY :sortcolumn ASC LIMIT {AMOUNT_IN_PAGE}"


    # else if last, sort by last then limit
    elif cur_page >= max_page:
        stmt_2 = f"{stmt_2} ORDER BY :sortcolumn DESC LIMIT {AMOUNT_IN_PAGE}"
    # else calculate id to start retrieving with limit
    else:
        stmt_2 = f"{stmt_2} AND id > :pagenum ORDER BY :sortcolumn {IS_ASCENDING_VALUES[sort_asc]} LIMIT {AMOUNT_IN_PAGE}"
        parameters["pagenum"] = (cur_page - 1) * AMOUNT_IN_PAGE
    parameters["sortcolumn"] = sort_column
    for row in db_session.execute(text(stmt_2), parameters).all():
        page_rows.append(
            dict(row._mapping)
        )
    # Return results
    return {"max_page": max_page, "page_rows": page_rows}


# When user first loads timeline, retrieve:
# First and last event id
# def get_edge_id(table_name):


@api.route("/timeline/<string:event_type>", methods=["GET"])
# @login_required
# TEST: Add auth later
def load_timeline(event_type):
    # TODO: Replace with user's database session info
    # TEST: Use test db to avoid processing with dftpl each test
    database_uri = (
        "sqlite:///"
        + r"D:\Moving\Documents\Universitas - MatKul\PraTA_TA_LaporanKP\TA"
        + r"\Proj\dftpl_gui_proj\test\timeline_2_fts5_short_12052025.sqlite"
    )
    db_engine = create_engine(database_uri)
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=db_engine, )
    )
    # FIXME: Do input validation against acceptable values, return invalid request if failed
    # FIXME: Catch ValueError
    # FIXME: SANITIZE FILTER VALUES
    # Get named URL parameters, sync with vue front end

    arg_include = request.args.get("include", default="", type=str).split()
    arg_exclude = request.args.get("exclude", default="", type=str).split()
    arg_asc = request.args.get("asc", default="true", type=str)
    arg_bycol = request.args.get("byCol", default="id", type=str)
    arg_cur_page = request.args.get("curPage", default=1, type=int)
    # Limit number of include and exclude to MAX_KEYWORDS strings
    if len(arg_include) >= MAX_KEYWORDS or len(arg_exclude) >= MAX_KEYWORDS:
        return make_response(f"ERROR: Too many keywords, MAX: {MAX_KEYWORDS}", 400)
    # Sanitize values by replacing invalid values with defaults
    if (
        arg_asc not in list(IS_ASCENDING_VALUES.keys())
        or arg_bycol not in TABLE_VALUES[event_type]["columns"]
        or not isinstance(arg_cur_page, int)
    ):
        return make_response("ERROR: Invalid Request", 400)
    # Include and exclude strings doesn't need to be sanitized
    # since not using raw sql commands so handled by SQLAlchemy
    print(f"Include: {arg_include}")  # TEST
    print(f"Exclude: {arg_exclude}")  # TEST

    # Update valid values if needed

    page_data = get_page_low_event(
        db_session=db_session,
        table_name=event_type,
        filter_include=arg_include,
        filter_exclude=arg_exclude,
        sort_asc=arg_asc,
        sort_column=arg_bycol,
        get_page=arg_cur_page,
    )
    # Close DB Connections
    # result.close()  # Close result proxy con
    db_session.remove()
    db_engine.dispose()
    return make_response(page_data, 200)


# Statistics API
# For summary of timeline and other aggregate functions

# Label APIs
# Create new Label
# Delete old label
# List new labels (pagination?)
# Rename old label

# Comment APIs
# Edit
@api.route("/timeline/<string:event_type>/u_comments", methods=["POST"])
# @login_required
# TEST: Add auth later
def update_comments(event_type):
    if event_type in ["low_level", "high_level"] and "row_id" in request.form and "comment" in request.form:
        if len(request.form["comment"]) > 200:
            return make_response("", 400)
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
        try:
            stmt = (f"UPDATE {event_type}_events " +
                    f"SET user_comments = :c " +
                    f"WHERE {event_type}_events.id = :s") # Updates main table
            stmt2 = (f"UPDATE {event_type}_events_idx " +
                    f"SET user_comments = :c " +
                    f"WHERE {event_type}_events_idx.id = :s")# Updates fts5 table
            
            db_session.execute(text(stmt), {"c": request.form["comment"], "s": request.form["row_id"]})
            db_session.execute(text(stmt2), {"c": request.form["comment"], "s": request.form["row_id"]})
            db_session.commit()
        except DBAPIError as e:
            return make_response("ERROR: Database engine error", 500)
        # Close DB Connections
        # result.close()  # Close result proxy con
        db_session.remove()
        db_engine.dispose()
        return make_response("", 200)
    else:
        return make_response("", 400)