import csv
from os import SEEK_SET
from os import remove
from os.path import join
from secrets import token_hex  # Generate random file name

from flask import flash, redirect, request, send_from_directory, session, url_for
from flask_login import login_required

# TEST: Following https://flask.palletsprojects.com/en/stable/patterns/sqlalchemy/#manual-object-relational-mapping
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import RequestEntityTooLarge  # Exceptions
from werkzeug.utils import secure_filename

from app import current_app
from app.api import api
from app.model.timeline_model import SCHEMA_TABLE_SQL_VAL

DFTPL_CSV_COLUMNS = ["datetime","timestamp_desc","source","source_long","message","parser","display_name","tag"]
SQLITE_MAGIC_HEADER_HEX = "53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00"

# SET OF ROUTES FOR FILES
# TODO: Associate ONLY 1 file upload and downloads with the respective user
# Store engine object in user/session data. If already exists, reject file upload.
# Check allowed files
def allowed_file(filename):
    if ('.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['UPLOAD_EXTENSIONS']):
        return filename.rsplit('.', 1)[1].lower()
    else:
        return False
    
# Upload new/old projects
# TODO: X Threading or multiprocessing for each user
# TODO: Add integrity hash check after file is saved, give user option to delete (EX: by logging out) if corrupted.
@api.route('/upload', methods=['POST'])
@login_required 
def upload_file():
    # Checks if user already uploaded a valid file before
    if not('session_csv' in session or 'session_db' in session) and request.method == 'POST':
        
        try:
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('Invalid Upload Request')
                return {"message": "ERROR: Invalid Upload Request!"}
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            # TODO: Show error to user for redundancy
            if file.filename == '':
                flash('No selected file')
                return {"message": "ERROR: No selected file"}
            if file:
                # TODO: VALIDATE FILE CONTENTS (Name/extentions can be falsified)
                # TODO: Handle empty files
                file_type = allowed_file(file.filename)
                # csv
                # TODO: Integrate csv validation with dftpl csv reading+timeline object creation
                # Create the dftpl timeline object while validating
                # Call dftpl program with the object + list of analyzer
                # Just don't call dftpl if an error is caught
                if file_type == "csv":
                    # FIXME: Check if file already exists
                    # Read csv file content
                    # Get the binary stream, decode into valid csv string iterable
                    # TEST: Simple test structure   
                    # Since this assumes python default encoding 'utf-8', handle exceptions if it's not
                    try:
                        spamreader = csv.DictReader(file.stream.read(150).decode().split("\n"), delimiter=',', quotechar='|')
                    except UnicodeDecodeError:
                        return{"message": "ERROR: Invalid csv character encoding, please use utf-8."}
                    except:
                        return{"message": "ERROR: Unknown error reading csv."}
                    # Checks for header structure
                    if len(spamreader.fieldnames) > 0:
                        for (index, column) in enumerate(spamreader.fieldnames):
                            if column != DFTPL_CSV_COLUMNS[index]:
                                # TODO: Handle invalid csv header
                                return {"message": "ERROR: Invalid csv header, use default plaso csv output."}
                        file.stream.seek(SEEK_SET) # Return to beginning of stream after checking file content then save file.

                        # If header is correct, save the file
                        filename = token_hex(8) + secure_filename(file.filename) 
                        file.save(join(current_app.config['UPLOAD_DIR'], filename))
                        # Store path to session to process csv and deleting afterwards
                        session['session_csv'] = filename

                        # TODO: Move to it's own python file
                        # Call function for database storage and DFTPL processing.
                        #TODO: Handle passing analyzer list to dftpl
                        # Loop to read and sanitize rows into dftpl timeline object
                        # If no row, return error.
                        # If a row with missing column is detected, notify user (which row) and cancel process (delete db, csv)
                        # Else, notify that process succeeds and pass timeline object to dftpl

                        # TEST
                        print("Hellow" + filename)
                        return redirect(url_for('api.download_file', name=filename))
                    else:
                        # TODO: Handle invalid csv file
                        return {"message": "ERROR: Invalid csv file!"}
                    
                # sqlite
                    # TEST: Simple test schema
                elif file_type == "sqlite":
                    # FIXME: Check if file already exists
                    # Check signature fir if it's even a valid sqlite db
                    # TODO: Prevent 2 files having same name by adding unix time to the name?
                    file_signature = file.stream.read(16).hex()
                    # Check if .read() return 'None'
                    if (file_signature and (bytes.fromhex(file_signature) == bytes.fromhex(SQLITE_MAGIC_HEADER_HEX))):
                        file.stream.seek(SEEK_SET) # Return to beginning of stream after reading the first 16 bytes
                        # Save the file
                        filename = token_hex(8) + secure_filename(file.filename) 
                        file.save(join(current_app.config['UPLOAD_DIR'], filename))
                        # Generate database uri.
                        # Try to create an engine, a session, and open a connection for query
                        database_uri = "sqlite:///" + join(current_app.config["UPLOAD_DIR"]  + '\\' + f"{filename}")
                        engine = create_engine(database_uri)
                        session['session_db'] = filename # To reuse later
                        
                        # TODO: CATCH DB Corruptions

                        db_session = scoped_session(sessionmaker(autocommit=False,
                                                                autoflush=False,
                                                                bind=engine))
                        # Run raw sql to get schema_table data
                        # schema_table isn't an actual table
                        # https://www.sqlite.org/schematab.html
                        query = """select sql\nfrom sqlite_master\nwhere type = "table"\norder by name"""
                        result = db_session.execute(text(query))
                        
                        for index, row in enumerate(result):
                            # TEST
                            if SCHEMA_TABLE_SQL_VAL[index] != row[0]:
                                # Do these 3 to close DB connections
                                result.close() # Close result proxy con
                                db_session.remove()
                                engine.dispose()
                                # Clean session values and false file
                                remove(join(current_app.config['UPLOAD_DIR'], session.pop('session_db', None)))
                                return {"message": "ERROR: Invalid sqlite file!"}



                        # Close session connection.
                        # NOTE: File will still be in use.
                        db_session.remove()
                        return {"message": "Success upload"}
                        
                    else:
                        # TODO: Handle invalid sqlite file
                        return {"message": "ERROR: Invalid sqlite file!"}

                else:
                    return {"message": "ERROR: Invalid file upload!"}
            else:
                return {"message": "ERROR: Invalid file upload!"}
        except (RequestEntityTooLarge):
            return {"message": "ERROR: File size too large!"}


@api.route('/uploads/<name>', methods=['GET'])
# TODO: Add integrity hash check after file is downloaded, give user option to redo if corrupted.
#TEST: Testing 
#@login_required 
def download_file(name):
    if request.method == 'GET':
        return send_from_directory(current_app.config["UPLOAD_DIR"], name)
    
#