from sqlalchemy import create_engine, text
from sqlalchemy.orm import session
from timeline_model import Base
import os.path

engine = create_engine(("sqlite:///" + os.path.abspath(os.path.dirname(__file__)) + "\\" + "test_db.sqlite"), echo=True)
# Base.metadata.create_all(engine)
# Run raw sql to get schema_table data
# schema_table isn't an actual table
# https://www.sqlite.org/schematab.html

query = """select sql\nfrom sqlite_master\nwhere type = "table"\norder by name"""
with engine.connect() as connection:
    result = connection.execute(text(query))
    for index, row in enumerate(result):
        print(row[0])
        print("---")
        print(SCHEMA_TABLE_SQL_VAL[index] == row[0])
        print("---")