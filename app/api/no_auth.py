from app.api import api
import json
# Read and returns list of analyzers in dftpl.

# TODO: Add hyperlinks to each analyzer's documentation when that's implemented
# TODO: In dftpl/dftpl.py, modify to start with every analyzers, then remove depending on selected analyzers
# Use this: https://www.geeksforgeeks.org/python-get-values-of-particular-key-in-list-of-dictionaries/
@api.route('/analyzers', methods=['GET'])
def get_analyzers():

    analyzer_list_path = r"dftpl\analyzers.json"

    try:
        with open(analyzer_list_path, 'r') as f:
            reader = json.load(f)["analyzers-list"]
            return reader
    except IOError:
        print (f"Could not read file: {analyzer_list_path}")

    pass