from os.path import join
from math import ceil
from json import loads, dumps
from re import match
from datetime import datetime

from flask import current_app, make_response, request, session

# Auth
from flask_login import login_required
from sqlalchemy import create_engine, text  # Python objects for DB connections
from sqlalchemy import select, inspect  # Methods for sql expressions
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DBAPIError


import app.model.timeline_model as TLModel
from app import current_app
from app.api import api


AMOUNT_IN_PAGE = 100  # Max events per page, 100k crashed tabulator
PAGES_AROUND = 1  # Max pages before and after current
IS_ASCENDING_VALUES = {True: "ASC", False: "DESC"}
IS_ASCENDING_SIGN = {True: ">", False: "<"}
# TODO: Automate column retrieval
# MAKE SURE THE CLIENT SIDE MATCHES THESE VALUES
# Stores all columns objects for ease of understanding + used for search and sort column
# Comments aren't used since that meant modifying fts3 table as well
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
        "overview_label_column": "plugin",
        "overview_text_column": "evidence"
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
            "reasoning_description",
            "reasoning_reference",
            "test_event_type",
            "test_event_evidence",
            "low_level_event_id",
        ],
        "overview_label_column": "event_type",
        "overview_text_column": "description"
    },
}

MAX_KEYWORDS = 10
MAX_KEYWORD_LEN = 100

STRFTIME_FORMAT_STRING = {
    "month": "%Y-%m",
    "day": "%F",
    "hour": "%FT%H",
    "minute": "%FT%H-%M",
}
OVERVIEW_TEXT_LENGTH = 20 # Limit length for overview timeline text description


# Definition of db URL string using session value
def returnDBURL():
    # TEST: TEST DB PATH
    # return (
    #     "sqlite:///"
    #     + r"D:\Moving\Documents\Universitas - MatKul\PraTA_TA_LaporanKP\TA"
    #     + r"\Proj\dftpl_gui_proj\test\11062025.sqlite"
    # )

    return "sqlite:///" + join(
        current_app.config["UPLOAD_DIR"] + "\\" + f"{session['session_db']}"
    )


# Helper function to validate ISO 8601 string date range arrays
def validISODateRange(date_range):
    # Is it a valid string arr
    if len(date_range) == 2:
        if isinstance(date_range[0], str) and isinstance(date_range[1], str):
            # Are the dates valid ISO 8601 string
            re_str = (
                r"^(-?(?:[0-9][0-9]*)?[0-9]{4})-(1[0-2]|0[0-9])-(3[01]|0[0-9]|[12]"
                + r"[0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]{6})?(Z|"
                + r"[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
            )
            if match(re_str, date_range[0]) and match(re_str, date_range[1]):
                # Is the start date less than the end date?
                if date_range[0] < date_range[1]:
                    return True
    # If pass all, return true
    # Else return false
    return False


# Pagination function (use in API)
# 1. Low level tables
# 2. Low and high level timeline visualizations
# Arguments:


# Label logic:
# Join event row with labels to retrieve attached label (many to many)
# Add "GROUP BY" clause for order of "GROUP_CONCAT" function
# It's so only the filtered & concatenated events are included in the JOIN operation
# FIXME: Error handling for all execution
# Support for search, filter, sort, range?
def get_page_event(
    db_session: scoped_session,
    table_name: str,
    filter_include: list[str] = [],
    filter_exclude: list[str] = [],
    sort_asc: str = "true",
    sort_column: str = "id",
    get_page: int = 1,
    filter_label: list[int] = [],
    filter_min_date_range: list[str] = [],
):
    is_filter_label = isinstance(filter_label, list) and len(filter_label) > 0
    # TEST: https://mysql.rjweb.org/doc.php/pagination
    cur_page = 1 if get_page < 1 else get_page  # Check min page requested
    max_page = 1
    page_rows = {}  # Converted into list of dicts before returning
    # FIXME: Check if code can handle modified db (missing ids, not ordered ids, missing values)
    # Define MATCH statement (if any is required)
    # NOTE: Pylint throws a "not callable" error but false positive
    # https://github.com/sqlalchemy/sqlalchemy/discussions/9202
    include_exclude = ""
    column_filter = " ".join(TABLE_VALUES[table_name]["columns"])
    parameters = {}  # For binding parameters
    # Generates MATCH statement with parameter tokens
    # HACK: Hardcoded table name
    # FIXME: Escape characters such as '%' in sqlite
    # TODO: Test if searching comments is possible
    if len(filter_include) > 0:
        param_id = []
        for index, word in enumerate(filter_include):
            param_id.append(f" :inc{index} ")  # Concatenate so arg bindings will work
            parameters[f"inc{index}"] = f'"{word}"'  # To escape characters like '$'
        include_exclude = include_exclude + (
            f" AND {table_name}_events_idx.id IN "
            f"(SELECT id FROM {table_name}_events_idx WHERE {table_name}_events_idx"
            f" MATCH '{{{column_filter}}} : '|| {'||" AND "||'.join(param_id)})"
        )

    if len(filter_exclude) > 0:
        param_id = []
        for index, word in enumerate(filter_exclude):
            param_id.append(f" :exc{index} ")  # Concatenate so arg bindings will work
            parameters[f"exc{index}"] = f'"{word}"'  # To escape characters like '$'
        include_exclude = include_exclude + (
            f" AND {table_name}_events_idx.id NOT IN "
            f"(SELECT id FROM {table_name}_events_idx WHERE {table_name}_events_idx"
            f" MATCH '{{{column_filter}}} : '|| {'||" AND "||'.join(param_id)})"
        )
    if validISODateRange(filter_min_date_range):
        include_exclude = include_exclude + (
            f" AND {table_name}_events_idx.date_time_min > :startmindate "
            + f"AND {table_name}_events_idx.date_time_min < :endmindate"
        )
        parameters["startmindate"] = filter_min_date_range[0]
        parameters["endmindate"] = filter_min_date_range[1]

    # If an include or exclude term existed, add match statement
    # Get max pages
    # HACK: So MATCH and id where statements can be appended conditionally
    if is_filter_label:
        stmt = f"SELECT * FROM {table_name}_events_idx WHERE 1=1"
        if include_exclude != "":
            stmt = f"{stmt} {include_exclude}"

        # If filter by label, add inner join to only include events with label
        # and to calculate page properly
        stmt = (
            f"SELECT COUNT(a.id) FROM ({stmt}) AS a "
            + f"INNER JOIN labels_{table_name}_events AS b ON b.{table_name}_events_id = a.id "
            + "INNER JOIN labels AS c ON b.labels_id = c.id "
            f"WHERE c.id IN ({', '.join(str(id) for id in filter_label)})"
        )
    else:
        stmt = (
            f"SELECT COUNT(id) FROM {table_name}_events_idx WHERE 1=1 {include_exclude}"
        )

    try:
        max_page = ceil(
            float(db_session.scalars(text(stmt), parameters).first())
            / float(AMOUNT_IN_PAGE)
        )  # Automatically closes result after getting value
    except DBAPIError as e:
        print(repr(e))  # FIXME
        return -1

    cur_page = (
        max_page if get_page >= max_page else get_page
    )  # Check max page requested

    # Create select and where statement before adding limit and id lookup
    # HACK: Using raw SQL so MATCH and id where statements on FTS5 table can be appended conditionally
    sub_stmt_2 = f"SELECT * FROM {table_name}_events_idx WHERE 1=1"

    if include_exclude != "":
        sub_stmt_2 = f"{sub_stmt_2} {include_exclude}"

    # If filter by label, add inner join to only include events with label
    # and to calculate page properly
    if is_filter_label:
        sub_stmt_2 = (
            f"SELECT a.*, c.id as cid, c.name as cname FROM ({sub_stmt_2}) AS a "
            + f"INNER JOIN labels_{table_name}_events AS b ON b.{table_name}_events_id = a.id "
            + "INNER JOIN labels AS c ON b.labels_id = c.id "
            f"WHERE c.id IN ({', '.join(str(id) for id in filter_label)})"
        )

    # NOTE: If ORDER BY is in nested SELECT, it won't trigger without LIMIT
    # THEORY: Due to SQLite's query optimizer
    # If first, sort by first then limit
    # NOTE: Column names cannot be paramaterized!
    if cur_page <= 1:
        sub_stmt_2 = f"{sub_stmt_2} ORDER BY {sort_column} {IS_ASCENDING_VALUES[sort_asc]} LIMIT {AMOUNT_IN_PAGE}"

    # else if last, sort by last then limit
    elif cur_page >= max_page:
        sub_stmt_2 = f"{sub_stmt_2} ORDER BY {sort_column} {IS_ASCENDING_VALUES[not sort_asc]} LIMIT {AMOUNT_IN_PAGE}"
    # else calculate id to start retrieving with limit
    else:
        sub_stmt_2 = f"{sub_stmt_2} AND id {IS_ASCENDING_SIGN[sort_asc]} :pagenum ORDER BY {sort_column} {IS_ASCENDING_VALUES[sort_asc]} LIMIT {AMOUNT_IN_PAGE}"
        parameters["pagenum"] = (
            (cur_page - 1) * AMOUNT_IN_PAGE
            if sort_asc
            else (max_page - cur_page + 1) * AMOUNT_IN_PAGE
        )

    # If not filtered by label, join labels using left join to include events without labels
    if is_filter_label:
        stmt_2 = sub_stmt_2

    else:
        stmt_2 = (
            f"SELECT a.*, c.id as cid, c.name as cname FROM ({sub_stmt_2}) AS a "
            + f"LEFT JOIN labels_{table_name}_events AS b ON b.{table_name}_events_id = a.id "
            + "LEFT JOIN labels AS c ON b.labels_id = c.id "
        )

    if table_name == "high_level":
        stmt_2 = (
            f"SELECT * FROM ({stmt_2}) "
            + "LEFT JOIN ("
            + "SELECT key_name, key_value, high_level_events_id FROM keys"
            + ") AS k ON k.high_level_events_id = id"
        )

    # Stores in temp dict of {id: rowdata}
    try:
        for row in db_session.execute(text(stmt_2), parameters).all():
            row_dict = row._asdict()
            # If given id already exists, append to list of label name and id
            # Since accessing value by key is O(1)
            # NOTE: JS Dict key values must be obj or string, so id is converted into string before returned

            if row_dict["id"] in page_rows:
                if (
                    row_dict["cid"]
                    and row_dict["cid"] not in page_rows[row_dict["id"]]["cid"]
                ):
                    page_rows[row_dict["id"]]["cid"].append(str(row_dict["cid"]))
                if (
                    row_dict["cname"]
                    and row_dict["cname"] not in page_rows[row_dict["id"]]["cname"]
                ):
                    page_rows[row_dict["id"]]["cname"].append(row_dict["cname"])
                if (
                    table_name == "high_level"
                    and row_dict["key_name"]
                    and row_dict["key_name"]
                    not in page_rows[row_dict["id"]]["key_name"]
                ):
                    page_rows[row_dict["id"]]["key_name"].append(row_dict["key_name"])

            else:
                page_rows[row_dict["id"]] = row_dict
                if row_dict["cid"]:
                    page_rows[row_dict["id"]]["cid"] = [str(row_dict["cid"])]
                if row_dict["cname"]:
                    page_rows[row_dict["id"]]["cname"] = [row_dict["cname"]]
                if table_name == "high_level" and row_dict["key_name"]:
                    page_rows[row_dict["id"]]["key_name"] = [row_dict["key_name"]]

        # Convert back to list of row dicts which is O(n)
        # Better than manually checking if there's duplicate id in a list of dicts
        # Which could be O(n^2)
        page_rows = list(page_rows.values())
    except DBAPIError as e:
        print(repr(e))  # FIXME
        return -1
    except Exception as e:  # HACK
        print(repr(e))  # FIXME
        return -2  # Incase unexpected error
    # Return results
    return {"max_page": max_page, "page_rows": page_rows}


# Validates arguments and retrieves timeline data
@api.route("/timeline/<string:event_type>", methods=["GET"])
@login_required
def load_timeline(event_type):
    if event_type in ["low_level", "high_level"]:

        database_uri = returnDBURL()
        db_engine = create_engine(database_uri)  # TEST
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
        arg_filter_label = "".join(
            request.args.get("filterLabel", default="", type=str).split()
        )  # Remove whitespace for invalid
        arg_min_date_range_list = loads(
            request.args.get("minDateRangeArr", default="", type=str)
        )  # Remove whitespace for invalid

        # Translates bool string to value
        if arg_asc == "true":
            arg_asc = True
        elif arg_asc == "false":
            arg_asc = False

        # Checks if term string is too long
        for term in arg_include:
            if len(term) >= MAX_KEYWORD_LEN:
                return make_response(
                    f"ERROR: Keyword too long, MAX: {MAX_KEYWORD_LEN} characters", 400
                )
        for term in arg_exclude:
            if len(term) >= MAX_KEYWORD_LEN:
                return make_response(
                    f"ERROR: Keyword too long, MAX: {MAX_KEYWORD_LEN} characters", 400
                )
        # Limit number of include and exclude to MAX_KEYWORDS strings
        if len(arg_include) >= MAX_KEYWORDS or len(arg_exclude) >= MAX_KEYWORDS:
            db_session.remove()
            db_engine.dispose()
            return make_response(f"ERROR: Too many keywords, MAX: {MAX_KEYWORDS}", 400)
        # Checks for invalid values
        if (
            arg_asc not in list(IS_ASCENDING_VALUES.keys())
            or arg_bycol not in TABLE_VALUES[event_type]["columns"]
            or not isinstance(arg_cur_page, int)
        ):
            db_session.remove()
            db_engine.dispose()
            return make_response("ERROR: Invalid Request", 400)
        # Include and exclude strings doesn't need to be sanitized
        # since not using raw sql commands so handled by SQLAlchemy

        # Update valid values if needed

        page_data = get_page_event(
            db_session=db_session,
            table_name=event_type,
            filter_include=arg_include,
            filter_exclude=arg_exclude,
            sort_asc=arg_asc,
            sort_column=arg_bycol,
            get_page=arg_cur_page,
            filter_label=loads(arg_filter_label or "null"),
            filter_min_date_range=arg_min_date_range_list,
        )
        if isinstance(page_data, int) and page_data < 0:
            db_session.remove()
            db_engine.dispose()
            return make_response("ERROR: Can't retrieve data", 500)
        # Close DB Connections
        # result.close()  # Close result proxy con
        db_session.remove()
        db_engine.dispose()
        return make_response(page_data, 200)
    else:
        return make_response("", 404)


# Keys API
# INPROGRESS
# Currently only used to retrieve keys from keys table for high level events
# since low level events doesn't have separate key objects
@api.route("/timeline/high_level/get_keys", methods=["GET"])
@login_required
def get_high_level_keys():
    # Get row id from GET Args
    row_id = request.args.get("rowID", default=0, type=int)

    keys_data = {}
    database_uri = returnDBURL()
    db_engine = create_engine(database_uri)  # TEST
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    )
    stmt = select(TLModel.Keys).where(TLModel.Keys.high_level_events_id == row_id)

    try:
        for row in db_session.scalars(stmt).all():
            if isinstance(row, TLModel.Keys):
                keys_data[row.key_name] = row.key_value
        db_session.remove()
        db_engine.dispose()
    except DBAPIError as e:
        print(repr(e))  # FIXME
        return make_response("ERROR: Invalid Request", 400)
    except Exception as e:  # HACK
        print(repr(e))  # FIXME
        return make_response("ERROR: Invalid Request", 400)

    return make_response(keys_data, 200)


# Comment APIs
# Edit
@api.route("/timeline/<string:event_type>/u_comments", methods=["POST"])
@login_required
def update_comments(event_type):
    if (
        event_type in ["low_level", "high_level"]
        and "rowID" in request.form
        and "comment" in request.form
    ):
        if len(request.form["comment"]) > 200:
            return make_response("", 400)

        database_uri = returnDBURL()
        db_engine = create_engine(database_uri)
        db_session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=db_engine,
            )
        )

        # Try to update, catch errors (like out of bounds error)
        # HACK: Hardcoded table name
        try:
            stmt = (
                f"UPDATE {event_type}_events "
                + f"SET user_comments = :c "
                + f"WHERE {event_type}_events.id = :s"
            )  # Updates main table
            stmt2 = (
                f"UPDATE {event_type}_events_idx "
                + f"SET user_comments = :c "
                + f"WHERE {event_type}_events_idx.id = :s"
            )  # Updates fts5 table

            db_session.execute(
                text(stmt), {"c": request.form["comment"], "s": request.form["rowID"]}
            )
            db_session.execute(
                text(stmt2), {"c": request.form["comment"], "s": request.form["rowID"]}
            )
            db_session.commit()
        except DBAPIError as e:
            db_session.remove()
            db_engine.dispose()
            return make_response("ERROR: Can't update comments", 500)
        # Close DB Connections
        # result.close()  # Close result proxy con
        db_session.remove()
        db_engine.dispose()
        return make_response("", 200)
    else:
        return make_response("", 404)


# Helper function to create ISO8601 strings for db searching.
# Pads empty arguments with 0 values.
# WARNING: Can result in invalid ISO 8601 dates
# FIXME: Allow for timezones other than UTC
def constructISO8601(
    year: "0000", month: "00", day: "00", hour: "00", minute: "00", second: "00"
):
    # Are the dates valid ISO 8601 string
    date_string = f"{year}-{month}-{day}T{hour}:{minute}:{second}.000000+00:00"
    re_str = (
        r"^(-?(?:[0-9][0-9]*)?[0-9]{4})-(1[0-2]|0[0-9])-(3[01]|0[0-9]|[12]"
        + r"[0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]{6})?(Z|"
        + r"[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    )
    if match(re_str, date_string):
        return date_string
    else:
        return False

#  Retrieves all timeline data.
#  @param openNodes Dicts of dicts {analyser: {entry_id: [[start_id, amount]]}} to expand. Empty array if none is selected.
#  @param aggregateBy Time interval for period ("month","day", "hour", or "minute"), unused if reqType = "event"
# @param loadInvalid Flag, enable to load events before epoch time and current time which doesn't have valid timestamps
# @param doMergeTimelines Flag, enable to merge all categories into one timeline

# FIXME: Allow for timezones other than UTC
# TODO: Default range is epoch time to current time. Anything else is assumed to be invalid timestamps
# only loaded when loadInvalid flag is true
@api.route("/timeline/<string:event_type>/overview", methods=["POST"])
@login_required
def timeline_overview(event_type):
    start_range = "1970-01-01T00:00:00.000000+00:00" # Unix epoch
    end_range = datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%f%:z")
    if (
        event_type in ["low_level", "high_level"]
        and "openNodes" in request.form
        and "aggregateBy" in request.form
        and "loadInvalid" in request.form
        and "doMergeTimelines" in request.form
        and "minDateRangeArr" in request.form
    ):
        # Translates bool string to value
        is_load_invalid = False
        if request.form["loadInvalid"] == "true":
            is_load_invalid = True
        is_merge_timelines = False
        if request.form["doMergeTimelines"] == "true":
            is_merge_timelines = True
        minDateRangeArrList = loads(request.form["minDateRangeArr"])
        # Override loadInvalid flag, min and max date, and load events within range in minDateRangeArr
        if validISODateRange(minDateRangeArrList):
            start_range = minDateRangeArrList[0]
            end_range = minDateRangeArrList[1]
            is_load_invalid = False

        # TODO: Validate values
        if request.form["aggregateBy"] in list(STRFTIME_FORMAT_STRING.keys()):
            database_uri = returnDBURL()
            db_engine = create_engine(database_uri) # TEST ECHO
            db_session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db_engine,
                )
            )
            result_json = []
            is_load_invalid_str = f"AND date_time_min >= '{start_range}' AND date_time_min <= '{end_range}' " if not is_load_invalid else ""
            # Get dict of periods, first
            stmt = text(
                f"SELECT id, {TABLE_VALUES[event_type]['overview_label_column']}, date_time_min, COUNT(id) as event_num "
                + f"FROM {event_type}_events WHERE 1=1 "
                + is_load_invalid_str
                + f"GROUP BY {TABLE_VALUES[event_type]['overview_label_column']}, strftime('{STRFTIME_FORMAT_STRING[request.form["aggregateBy"]]}', date_time_min)"
            )
            inserted_category = []
            COLOR_DEF = {False: "#001EFF", True: "#87004F"} # Coloring period nodes
            try:
                # If merged into one timeline, prepare structure
                if is_merge_timelines:
                    result_json.append({
                        "category": "Merged timeline",
                        "nodes": []
                    })
                # Get all the period nodes
                # For all result row
                for index, row in enumerate(db_session.execute(stmt).all()):
                    # Changes color if period node is expanded
                    toggleColor = False
                    # If this category is included in the expanded nodes list
                    if row[1] in list(loads(request.form['openNodes']).keys()):
                        # If this period node is expanded
                        if str(index) in loads(loads(request.form['openNodes'])[row[1]]).keys():
                            toggleColor = True
                    
                    # If timelines is merged
                    if is_merge_timelines:
                        # So add new period node to category's dictionary
                        result_json[0]["nodes"].append(
                            {
                                "entry_id": index,
                                "category": row[1],
                                "evt_count": row[3],
                                "type": "period",
                                "timestamp": row[2],
                                "start_id": row[0],
                                "text": f"{row[1]}-Event count: {row[3]}",
                                "textStyle": {
                                    "color": f"{COLOR_DEF[toggleColor]}"
                                },
                            }
                        )
                    # If timelines are separated
                    else: 
                        # If this category already inserted into structure
                        if row[1] in inserted_category:
                            # Index for category in inserted_category should be the same
                            # So add new period node to category's dictionary
                            result_json[inserted_category.index(row[1])]["nodes"].append(
                                {
                                    "entry_id": index,
                                    "category": row[1],
                                    "evt_count": row[3],
                                    "type": "period",
                                    "timestamp": row[2],
                                    "start_id": row[0],
                                    "text": f"Event count: {row[3]}",
                                    "textStyle": {
                                        "color": f"{COLOR_DEF[toggleColor]}"
                                    },
                                }
                            )
                        else:
                            # Create new category dict
                            result_json.append(
                                {
                                    "category": row[1],
                                    "nodes": [
                                        {
                                            "entry_id": index,
                                            "category": row[1],
                                            "evt_count": row[3],
                                            "type": "period",
                                            "timestamp": row[2],
                                            "start_id": row[0],
                                            "text": f"Event count: {row[3]}",
                                            "textStyle": {
                                                "color": f"{COLOR_DEF[toggleColor]}"
                                            },
                                        }
                                    ],
                                }
                            )
                            inserted_category.append(row[1])

            # If some period nodes is expanded, retrieve said events
                if len(loads(request.form["openNodes"])) > 0:
                    stmt2_arr = []
                    
                    for category, id_dicts in loads(request.form['openNodes']).items():
                        for [start_id, amount] in loads(id_dicts).values():
                            stmt2_arr.append(
                                [category,
                                text(
                                    f"SELECT id, {TABLE_VALUES[event_type]['overview_text_column']}, date_time_min "+
                                    f"FROM {event_type}_events WHERE 1=1 "+
                                    f"AND id >= {start_id} AND {TABLE_VALUES[event_type]['overview_label_column']} == '{category}'  "+
                                    is_load_invalid_str+
                                    f"LIMIT {amount}" # Skip past "Event count: " string
                                )
                                ]
                            )
                    # Get all the event nodes
                    # HACK: Text is wrapped in brackets since text ending in an image extension (.jpg) and maybe others
                    # are treated as an image element
                    for [category, statement] in stmt2_arr:
                        for index, row in enumerate(db_session.execute(statement).all()):
                                if is_merge_timelines:
                                    result_json[0]["nodes"].append(
                                        {
                                            "category": category,
                                            "type": "event",
                                            "timestamp": row[2],
                                            "event_id": row[0],
                                            "text": f"({category} ID {0}: {row[1][:OVERVIEW_TEXT_LENGTH]})",
                                            "textStyle": {
                                                "color": "#698600"
                                            },
                                        }
                                    )
                                else:
                                    result_json[inserted_category.index(category)]["nodes"].append(
                                        {
                                            "category": category,
                                            "type": "event",
                                            "timestamp": row[2],
                                            "event_id": row[0],
                                            "text": f"(ID {0}: {row[1][:OVERVIEW_TEXT_LENGTH]})",
                                            "textStyle": {
                                                "color": "#698600"
                                            },
                                        }
                                    )
            except DBAPIError as e:
                print(repr(e))  # FIXME
                db_session.remove()
                db_engine.dispose()
                return make_response("ERROR: Database engine error", 500)

            db_session.remove()
            db_engine.dispose()
            if len(result_json) < 1:
                return make_response(
                    "ERROR: Is there no events? If there is, please report this db error!",
                    500,
                )
            
            return make_response(dumps(result_json), 200)
        else:
            return make_response("ERROR: Invalid Request", 400)
    else:
        return make_response("ERROR: Invalid Request", 400)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

# Get a single event's data, for overview
@api.route("/timeline/<string:event_type>/overview_detail", methods=["GET"])
@login_required
def overview_detail_event(event_type):
    if (
        event_type in ["low_level", "high_level"]
    ):
        # Get row id from GET Args
        row_id = request.args.get("rowID", default=1, type=int)

        event_data = {}
        database_uri = returnDBURL()
        db_engine = create_engine(database_uri)  # TEST
        db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        )
        stmt = select(TABLE_VALUES[event_type]["model"]).where(TABLE_VALUES[event_type]["model"].id == row_id)
        if event_type == "high_level":
            stmt2 = select(TLModel.Labels.name).join(TLModel.labels_high_level_events_table).where(TLModel.labels_high_level_events_table.c.high_level_events_id == row_id)
        else:
            stmt2 = select(TLModel.Labels.name).join(TLModel.labels_low_level_events_table).where(TLModel.labels_low_level_events_table.c.low_level_events_id == row_id)
        try:
            event_data = object_as_dict(db_session.scalars(stmt).first())
            event_data["labels"] = "|".join(db_session.scalars(stmt2).all())
            db_session.remove()
            db_engine.dispose()
        except DBAPIError as e:
            print(repr(e))  # FIXME
            return make_response("ERROR: Invalid Request", 400)
        except Exception as e:  # HACK
            print(repr(e))  # FIXME
            return make_response("ERROR: Invalid Request", 400)
        return make_response(event_data, 200)
    return make_response("ERROR: Invalid Request", 400)