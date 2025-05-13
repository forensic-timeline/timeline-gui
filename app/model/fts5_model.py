from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy.engine import Connection
from sqlalchemy.schema import DDLElement
from sqlalchemy import Table, MetaData, Column, String, insert

from app.model.timeline_model import HighLevelEvents, LowLevelEvents

class CreateFtsTable(DDLElement):
    """Represents a CREATE VIRTUAL TABLE ... USING fts5 statement, for indexing
    a given table.
    """

    def __init__(self, table, version=5):
        self.table = table # Table to create an FTS virtual table for
        self.version = version # FTS Version


# Create FTS Table for a given table

@compiles(CreateFtsTable)
def compile_create_fts_table(element, compiler, **kw):
    tbl = element.table
    version = element.version
    preparer = compiler.preparer

    vtbl_name = preparer.quote(tbl.__table__.name + "_idx")

    # If column is nullable, add UNINDEXED option
    columns = [f"{x.name} UNINDEXED" if x.nullable else x.name for x in tbl.__mapper__.columns] # Defines FTS table's columns using main table's column 
    
    columns.append('tokenize="porter unicode61"') # Tokenizer for FTS, see documentation
    columns = ', '.join(columns)

    return f"CREATE VIRTUAL TABLE IF NOT EXISTS {vtbl_name} USING FTS{version} ({columns} , content={tbl.__table__.name}, content_rowid=id)"


    # Insert entries to the FTS table alongside the main table
# TEST
# def attach_fts_low_level(session: Session, instance: LowLevelEvents):
#     if type(instance) is LowLevelEvents:
#         meta = MetaData()
#         table = Table(
#                 'low_level_events_idx',
#                 meta,
#                 Column("date_time_min", String),
#                 Column("event_type", String),
#                 Column("keys", String),
#             )
#         session.execute(
#             insert(table).values(date_time_min=instance.date_time_min,
#                                 event_type=instance.event_type,
#                                 keys=instance.keys)
#         )

def attach_fts_low_level(mapper, conn: Connection, instance: LowLevelEvents):
    meta = MetaData()
    # TEST: Add the proper columns for searching
    table = Table(
            'low_level_events_idx',
            meta,
            Column("date_time_min", String),
            Column("date_time_max", String),
            Column("event_type", String),
            Column("path", String),
            Column("evidence", String),
            Column("plugin", String),
            Column("provenance_raw_entry", String),
            Column("keys", String),
        )
    conn.execute(
        insert(table).values(date_time_min=instance.date_time_min,
                             date_time_max=instance.date_time_max,
                             event_type=instance.event_type,
                             path=instance.path,
                             evidence=instance.evidence,
                             plugin=instance.plugin,
                             provenance_raw_entry=instance.provenance_raw_entry,
                             keys=instance.keys)
    )
# @event.listens_for(HighLevelEvents, 'after_attach')
# def attach_fts_high_level(session, instance):
