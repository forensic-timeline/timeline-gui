from os.path import join
from math import ceil

from flask import current_app, make_response, request, session

# Auth
from flask_login import login_required
from sqlalchemy import create_engine, engine, text  # Python objects for DB connections
from sqlalchemy import select, func, and_, or_  # Methods for sql expressions
from sqlalchemy.orm import scoped_session, sessionmaker

import app.model.timeline_model as TLModel
from app import current_app
from app.api import api

AMOUNT_IN_PAGE = 1000  # Max events per page, 100k crashed tabulator
PAGES_AROUND = 1  # Max pages before and after current
IS_ASCENDING_VALUES = ["true", "false"]
# TODO: Automate column retrieval
# MAKE SURE THE CLIENT SIDE MATCHES THESE VALUES
# Stores all columns objects for ease of understanding + used for search and sort column

TABLE_VALUES = {
    "low_level": {
        "model": TLModel.LowLevelEvents,
        "columns": {
            "id": TLModel.LowLevelEvents.id,
            "date_time_min": TLModel.LowLevelEvents.date_time_min,
            "event_type": TLModel.LowLevelEvents.event_type,
            "path": TLModel.LowLevelEvents.path,
            "evidence": TLModel.LowLevelEvents.evidence,
            "plugin": TLModel.LowLevelEvents.plugin,
        }
    },
    "high_level": {
        "model": TLModel.HighLevelEvents,
        "columns": {
            "id": TLModel.HighLevelEvents.id,
            "date_time_min": TLModel.HighLevelEvents.date_time_min,
            "event_type": TLModel.HighLevelEvents.event_type,
            "description": TLModel.HighLevelEvents.description,
            "category": TLModel.HighLevelEvents.category,
            "reasoning desc": TLModel.HighLevelEvents.reasoning_description,
            "reasoning ref": TLModel.HighLevelEvents.reasoning_reference,
        }
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
    sort_asc: bool = True,
    sort_column: str = "id",
    cur_page: int = 1,
):
    # TEST: https://mysql.rjweb.org/doc.php/pagination
    max_page = 1
    page_rows = []
    # FIXME: Check if code can handle modified db (missing ids, not ordered ids, missing values)
    # Get max pages
    # NOTE: Pylint throws a "not callable" error but false positive
    # https://github.com/sqlalchemy/sqlalchemy/discussions/9202
    queries = []
    # TEST: Try 2 columns search
    if len(filter_include) > 0:
        print("Added include") # TEST
        queries.append(
            or_(
                TABLE_VALUES[table_name]["columns"]["date_time_min"].in_(filter_include),
                TABLE_VALUES[table_name]["columns"]["event_type"].in_(filter_include),
            )
        )
    if len(filter_exclude) > 0:
        print("Added exclude") # TEST

        queries.append(
            or_(
                TABLE_VALUES[table_name]["columns"]["date_time_min"].not_in(filter_exclude),
                TABLE_VALUES[table_name]["columns"]["event_type"].not_in(filter_exclude),
            )
        )

    stmt = (
        select(func.count(TABLE_VALUES[table_name]["model"].id))
        .filter(*queries)
        .select_from(TABLE_VALUES[table_name]["model"])
    )

    

    max_page = ceil(
        float(db_session.scalars(stmt).first()) / float(AMOUNT_IN_PAGE)
    )  # Automatically closes result after getting value

    # Create select and where statement before adding limit and id lookup
    # TEST: Just grabbing page, no other operations
    stmt_2 = select(TABLE_VALUES[table_name]["model"])
    print(stmt_2.filter(*queries).limit(AMOUNT_IN_PAGE))
    queries.append(TABLE_VALUES[table_name]["model"].id > (cur_page - 1) * AMOUNT_IN_PAGE)

    for row in db_session.scalars(stmt_2.filter(*queries).limit(AMOUNT_IN_PAGE)).all():
        page_rows.append(
            {c.name: str(getattr(row, c.name)) for c in row.__table__.columns}
        )
    # If first, sort by first then limit

    # else if last, sort by last then limit

    # else calculate id to start retrieving with limit

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
        + r"\Proj\dftpl_gui_proj\test\timeline_2_example_short_12052025.sqlite"
    )
    db_engine = create_engine(database_uri)
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
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
    if arg_asc not in IS_ASCENDING_VALUES or arg_bycol not in list(
        TABLE_VALUES[event_type]["columns"].keys()
    ):
        return make_response("ERROR: Invalid Request", 400)
    # Include and exclude strings doesn't need to be sanitized
    # since not using raw sql commands so handled by SQLAlchemy
    print(f"Include: {arg_include}") # TEST
    print(f"Exclude: {arg_exclude}") # TEST

    # Update valid values if needed


    page_data = get_page_low_event(
        db_session=db_session,
        table_name=event_type,
        filter_include=arg_include,
        filter_exclude=arg_exclude,
        sort_asc=arg_asc,
        sort_column=arg_bycol,
        cur_page=arg_cur_page,
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
# Create new
# Edit
# Delete
# Retrieve
