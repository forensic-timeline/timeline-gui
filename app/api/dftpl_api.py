from os.path import join
from app.api import api
from app import current_app
import json

# Read and returns list of analysers in dftpl.

# TODO: Add hyperlinks to each analyser's documentation when that's implemented
# TODO: Add "analysers.json" to main DFTPL build
# TODO: In dftpl/dftpl.py, modify default to start with every analysers, then remove depending on selected analysers
# Use this: https://www.geeksforgeeks.org/python-get-values-of-particular-key-in-list-of-dictionaries/
@api.route('/analysers', methods=['GET'])
def get_analysers():

    analyser_list_path = join(current_app.config['APP_DIR'], 'dftpl_helper', 'analysers.json')

    try:
        with open(analyser_list_path, 'r') as f:
            reader = json.load(f)["analysers-list"]
            return reader
    except IOError:
        print (f"Could not read file: {analyser_list_path}")

    pass
