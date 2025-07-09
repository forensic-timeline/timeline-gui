import csv

# TEST
import logging
from hashlib import sha256  # For getting file hash
from json import loads
from os import SEEK_SET, remove, rename
from os.path import getsize, join
from secrets import token_hex  # Generate random file name

from flask import (
    flash,
    make_response,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_login import login_required

# Following https://flask.palletsprojects.com/en/stable/patterns/sqlalchemy/#manual-object-relational-mapping
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import RequestEntityTooLarge  # Exceptions
from werkzeug.utils import secure_filename

from app import current_app
from app.api import api
from app.api.auth import clean_up
from app.model.timeline_model import SCHEMA_TABLE_SQL_VAL

DFTPL_CSV_COLUMNS = [
    "datetime",
    "timestamp_desc",
    "source",
    "source_long",
    "message",
    "parser",
    "display_name",
    "tag",
]  # Update if default plaso csv columns changes

SQLITE_MAGIC_HEADER_HEX = (
    "53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00"  # From official docs
)

BUF_SIZE = 10 * 1024 * 1024  # 10 MB chunks for calculating hashes


# SET OF ROUTES FOR FILES
# TODO: Associate ONLY 1 file upload and downloads with the respective user
# Store engine object in user/session data. If already exists, reject file upload.
# Check allowed files
def allowed_file(filename):
    if (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["UPLOAD_EXTENSIONS"]
    ):
        return filename.rsplit(".", 1)[1].lower()
    else:
        return False


# Upload new/old projects
# TODO: X Threading or multiprocessing for each user
# TODO: Add integrity hash check after file is saved, give user option to delete (EX: by logging out) if corrupted.
@api.route("/upload", methods=["POST"])
@login_required
def upload_file():
    # Checks if user already uploaded a valid file before
    if (
        not (
            ("session_csv" in session or "session_db" in session)
            and "dzuuid" not in session
        )
        and request.method == "POST"
    ):
        # Check if request is missing a Dropzone request value
        if (
            "dzuuid" not in request.form
            or "dzchunkindex" not in request.form
            or "dztotalfilesize" not in request.form
            or "dzchunksize" not in request.form
            or "dztotalchunkcount" not in request.form
            or "dzchunkbyteoffset" not in request.form
        ):
            return make_response(("ERROR: Invalid Upload Request!", 400))
        # Chunk type checking is done here for clarity
        is_first = False
        is_middle = False
        is_last = False
        is_one_chunk = False  # For files smaller than a chunk that only 1 chunk is sent
        # If invalid request: Return error
        if (
            int(request.form["dztotalchunkcount"]) < 1
            or int(request.form["dzchunkindex"]) < 0
        ):
            return make_response(("ERROR: Invalid Upload Request!", 400))
        # If chunk 0 and total > 1 : Store dzuuid for chunk id, start new upload
        elif (
            int(request.form["dztotalchunkcount"]) > 1
            and int(request.form["dzchunkindex"]) == 0
        ):
            is_first = True
            session["dzuuid"] = request.form["dzuuid"]
        # If chunk total-1: Check if dzuuid matches, if yes save file
        # For total>1, erase session["dzuuid"] when done
        # For total = 1, save file without saving "dzuuid"
        elif int(request.form["dzchunkindex"]) == (
            int(request.form["dztotalchunkcount"]) - 1
        ):
            if (
                int(request.form["dztotalchunkcount"]) > 1
                and "dzuuid" in session
                and session["dzuuid"] == request.form["dzuuid"]
            ):
                is_last = True
            elif int(request.form["dztotalchunkcount"]) == 1:
                is_one_chunk = True
            else:
                return make_response(("ERROR: Invalid Upload Request!", 400))
        # If chunk 1 to total-2: Check if dzuuid matches, if yes process chunk
        elif (
            "dzuuid" in session
            and session["dzuuid"] == request.form["dzuuid"]
            and int(request.form["dztotalchunkcount"]) > 1
            and int(request.form["dzchunkindex"]) > 0
        ):
            is_middle = True
        # Default to error
        else:
            return make_response(("ERROR: Invalid Upload Request!", 400))
        # FIXME: If upload interrupted and never finishes?
        # HACK: This assumes the file is uploaded entirely in one go without interruptions

        try:
            # check if the post request has the file part
            if "file" not in request.files:
                return make_response(("ERROR: Invalid Upload Request!", 400))
            file = request.files["file"]
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            # TODO: Show error to user for redundancy
            if file.filename == "":
                return make_response(("ERROR: No selected file!", 400))

            if file:
                file_type = allowed_file(file.filename)
                # csv
                # Create the dftpl timeline object while validating
                # Call dftpl program with the object + list of analyser
                # Just don't call dftpl if an error is caught
                if file_type == "csv":
                    # Checks for header structure
                    if is_first or is_one_chunk:
                        # Read csv file content
                        # Get the binary stream, decode into valid csv string iterable
                        # Since this assumes python default encoding 'utf-8', handle exceptions if it's not
                        try:
                            spamreader = csv.DictReader(
                                file.stream.read(150).decode().split("\n"),
                                delimiter=",",
                                quotechar="|",
                            )
                        except (UnicodeDecodeError, OSError):
                            return make_response(
                                ("ERROR: Error while reading file stream.", 500)
                            )
                        except:
                            return make_response(
                                ("ERROR: Unknown error reading csv.", 400)
                            )

                        if len(spamreader.fieldnames) == len(DFTPL_CSV_COLUMNS):
                            for index, column in enumerate(spamreader.fieldnames):
                                if column != DFTPL_CSV_COLUMNS[index]:
                                    return make_response(
                                        (
                                            "ERROR: Invalid csv header, use default plaso csv output.",
                                            400,
                                        )
                                    )
                            file.stream.seek(
                                SEEK_SET
                            )  # Return to beginning of stream after checking file content then save file.
                            filename = secure_filename(
                                file.filename
                            ) + token_hex(16) + ".csv" # Since new upload request = new file hash name
                            # Store path to session to process csv and deleting afterwards
                            session["session_csv"] = filename

                        else:
                            return make_response(("ERROR: Invalid csv file!", 400))

                    # Store to 'temp' folder with temporary extension
                    try:
                        with open(
                            join(
                                current_app.config["TEMP_DIR"],
                                session["session_csv"] + ".tmp",
                            ),
                            "ab",
                        ) as f:
                            f.seek(int(request.form["dzchunkbyteoffset"]))
                            f.write(file.stream.read())
                    except OSError as e:
                        # TODO: Logging
                        print(e)
                        return make_response(
                            ("ERROR: Error while writing to disk!", 500)
                        )

                    # If upload is interrupted, must redo from beginning

                    # TODO: If chunked upload not complete, return chunk confirmation
                    # Else Move when complete
                    if is_last or is_one_chunk:
                        try:
                            rename(
                                join(
                                    current_app.config["TEMP_DIR"],
                                    session["session_csv"] + ".tmp",
                                ),
                                join(
                                    current_app.config["UPLOAD_DIR"],
                                    session["session_csv"],
                                ),
                            )
                            session.pop("dzuuid", None)  # Clear upload id
                            # Store list of analysers
                            session["selected_analysers"] = loads(request.form["analysers"])
                            return make_response(("File upload successful", 200))
                        except OSError:
                            # FIXME: Log error
                            return make_response(
                                (
                                    "ERROR: Failed upload when saving, contact admin for help.",
                                    500,
                                )
                            )
                    # Returns if middle chunk success
                    return make_response(("Chunk upload successful", 200))

                # sqlite
                elif file_type == "sqlite":
                    # Check signature fir if it's even a valid sqlite db
                    # TODO: Prevent 2 files having same name by adding unix time to the name?
                    if is_first or is_one_chunk:
                        try:
                            file_signature = file.stream.read(16).hex()
                        except (UnicodeDecodeError, OSError):
                            return make_response(
                                ("ERROR: Error while reading file stream.", 500)
                            )
                        except:
                            return make_response(
                                ("ERROR: Unknown error reading sqlite.", 400)
                            )
                        # Check if .read() return 'None'
                        if file_signature != None and (
                            bytes.fromhex(file_signature)
                            == bytes.fromhex(SQLITE_MAGIC_HEADER_HEX)
                        ):
                            file.stream.seek(
                                SEEK_SET
                            )  # Return to beginning of stream after reading the first 16 bytes
                            # Save the file
                            # Assuming file is split into chunks, loop to get all the chunks
                            filename = secure_filename(file.filename) + token_hex(16) + ".sqlite"
                            session["session_db"] = filename  # To reuse later
                        else:
                            return make_response(("ERROR: Invalid sqlite file!", 400))

                    # If header is valid, upload DB
                    # Store to 'temp' folder with temporary extension
                    try:
                        with open(
                            join(
                                current_app.config["TEMP_DIR"],
                                session["session_db"] + ".tmp",
                            ),
                            "ab",
                        ) as f:
                            f.seek(int(request.form["dzchunkbyteoffset"]))
                            f.write(file.stream.read())
                    except OSError as e:
                        # TODO: Logging
                        print(e)
                        return make_response(
                            ("ERROR: Error while writing to disk!", 500)
                        )

                    # Once DB is fully uploaded
                    if is_last or is_one_chunk:
                        rename(
                            join(
                                current_app.config["TEMP_DIR"],
                                session["session_db"] + ".tmp",
                            ),
                            join(
                                current_app.config["UPLOAD_DIR"], session["session_db"]
                            ),
                        )
                        # Generate database uri.
                        # Try to create an engine, a session, and open a connection for query
                        database_uri = "sqlite:///" + join(
                            current_app.config["UPLOAD_DIR"]
                            + "\\"
                            + f"{session['session_db']}"
                        )
                        engine = create_engine(database_uri, echo=True)

                        # TODO: CATCH DB Corruptions

                        db_session = scoped_session(
                            sessionmaker(autocommit=False, autoflush=False, bind=engine)
                        )
                        # Run raw sql to get schema_table data
                        # schema_table isn't an actual table
                        # https://www.sqlite.org/schematab.html
                        query = """select sql\nfrom sqlite_master\nwhere type = "table"\norder by name"""
                        result = db_session.execute(text(query))

                        for index, row in enumerate(result):
                            if "".join(SCHEMA_TABLE_SQL_VAL[index].split()) != "".join(row[0].split()):
                                # Do these 3 to close DB connections
                                result.close()  # Close result proxy con
                                db_session.remove()
                                engine.dispose()
                                # Clean session values and false file
                                remove(
                                    join(
                                        current_app.config["UPLOAD_DIR"],
                                        session.pop("session_db", None),
                                    )
                                )
                                return make_response(
                                    ("ERROR: Invalid sqlite file!", 400)
                                )
                        session.pop("dzuuid", None)  # Clear upload id
                        # NOTE: File will still be in use.
                        # Do these 3 to close DB connections
                        result.close()  # Close result proxy con
                        db_session.remove()
                        engine.dispose()
                        # Clean session value
                        return make_response(("File upload successful", 200))
                    # Returns if middle chunk success
                    return make_response(("Chunk upload successful", 200))
                else:
                    return make_response(("ERROR: Invalid file!", 400))
            else:
                return make_response(("ERROR: Invalid file!", 400))
        except RequestEntityTooLarge:
            return make_response(("ERROR: File size too large!", 400))
    else:
        return make_response(("ERROR: Invalid Upload Request!", 400))


# Generates a SHA256 hash to help user confirm uploaded file's integrity
@api.route("/confirm-hash/<string:operation>", methods=["GET"])
@login_required
def confirm_hash(operation):
    if "session_csv" in session or "session_db" in session:
        if operation == "upload":
            file_name = (
                session["session_csv"]
                if "session_csv" in session
                else session["session_db"]
            )
        elif operation == "download":
            file_name = session["session_db"]
        else:
            return make_response("", 404)
        if request.method == "GET":
            try:
                h_sha256 = sha256()
                with open(join(current_app.config["UPLOAD_DIR"], file_name), "rb") as f:
                    while True:
                        data = f.read(BUF_SIZE)
                        if not data:
                            break
                        h_sha256.update(data)
                return make_response(
                    f"File '{file_name}' hash: {h_sha256.hexdigest()}", 200
                )
            except IOError:
                # TODO: Log and handle exception instead of returning raw text
                return make_response("Unknown error while reading file", 400)
        # elif request.method == "POST":
        else:
            return make_response("", 400)
    else:
        return make_response("", 400)


# Deletes uploaded file and session data about file
# Allows user to upload a file without refreshing the page or logging out
@api.route("/upload/undo-upload", methods=["GET"])
@login_required
def undo_upload():
    # HACK: App and user variable is for flask-login's event
    # Not used here.        
    if clean_up("","") < 0:
        return make_response(
            "Error while clean up, please check server for more information.", 500
        )
    else:
        return make_response("", 200)


@api.route("/download_db", methods=["GET"])
# TODO: Add integrity hash check after file is downloaded, give user option to redo if corrupted.
@login_required
def download_file():
    if request.method == "GET":
        return send_from_directory(current_app.config["UPLOAD_DIR"], session['session_db'], as_attachment=True)


#
